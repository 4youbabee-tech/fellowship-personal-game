#include "ShireProductionImportCommandlet.h"

#include "AssetImportTask.h"
#include "AssetToolsModule.h"
#include "FileHelpers.h"
#include "Factories/FbxImportUI.h"
#include "Factories/FbxStaticMeshImportData.h"
#include "Engine/StaticMesh.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Materials/MaterialInterface.h"
#include "Modules/ModuleManager.h"
#include "UObject/Package.h"

UShireProductionImportCommandlet::UShireProductionImportCommandlet()
{
    IsClient = false;
    IsServer = false;
    IsEditor = true;
    LogToConsole = true;
    ShowErrorCount = true;
}

int32 UShireProductionImportCommandlet::Main(const FString& Params)
{
    const FString SourceRoot = FPaths::ConvertRelativePathToFull(
        FPaths::Combine(FPaths::ProjectDir(), TEXT("SourceAssets/Production")));

    TArray<FString> SourceFiles;
    TArray<FString> TextureFiles;
    TArray<FString> MeshFiles;
    IFileManager::Get().FindFilesRecursive(TextureFiles, *SourceRoot, TEXT("*.bmp"), true, false, false);
    IFileManager::Get().FindFilesRecursive(MeshFiles, *SourceRoot, TEXT("*.obj"), true, false, false);
    TextureFiles.Sort();
    MeshFiles.Sort();
    SourceFiles.Append(TextureFiles);
    SourceFiles.Append(MeshFiles);

    if (SourceFiles.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("ShireProductionImport: no production assets found at %s"), *SourceRoot);
        return 0;
    }

    FAssetToolsModule& AssetTools = FModuleManager::LoadModuleChecked<FAssetToolsModule>(TEXT("AssetTools"));
    int32 Failed = 0;
    TArray<UPackage*> ImportedMaterialPackages;

    for (const FString& Filename : SourceFiles)
    {
        FString Relative = Filename;
        FPaths::MakePathRelativeTo(Relative, *(SourceRoot / TEXT("")));
        Relative.ReplaceInline(TEXT("\\"), TEXT("/"));

        const FString RelativeDir = FPaths::GetPath(Relative);
        const FString DestinationPath = RelativeDir.IsEmpty()
            ? TEXT("/Game/Production")
            : FString::Printf(TEXT("/Game/Production/%s"), *RelativeDir);

        UAssetImportTask* Task = NewObject<UAssetImportTask>();
        Task->Filename = Filename;
        Task->DestinationPath = DestinationPath;
        Task->DestinationName = FPaths::GetBaseFilename(Filename);
        Task->bAutomated = true;
        Task->bSave = true;
        Task->bReplaceExisting = true;

        bool bBareObjMaterialImportDisabled = false;
        bool bInjectedSmoothingGroup = false;
        bool bAuthoredMaterialImportForced = false;
        if (FPaths::GetExtension(Filename).Equals(TEXT("obj"), ESearchCase::IgnoreCase))
        {
            FString ObjSource;
            if (FFileHelper::LoadFileToString(ObjSource, *Filename))
            {
                // The production bank is intentionally lightweight, but UE4.27 emits
                // hundreds of warnings when OBJ files omit an explicit smoothing group.
                // Normalize only the ephemeral CI/import working copy.
                const bool bHasSmoothing =
                    ObjSource.StartsWith(TEXT("s ")) ||
                    ObjSource.Contains(TEXT("\ns "), ESearchCase::CaseSensitive);
                if (!bHasSmoothing)
                {
                    int32 FaceLine = ObjSource.Find(TEXT("\nf "), ESearchCase::CaseSensitive);
                    if (FaceLine != INDEX_NONE)
                    {
                        ObjSource.InsertAt(FaceLine + 1, TEXT("s 1\n"));
                        if (FFileHelper::SaveStringToFile(ObjSource, *Filename))
                        {
                            bInjectedSmoothingGroup = true;
                        }
                    }
                }

                const bool bHasMaterialLibrary =
                    ObjSource.Contains(TEXT("mtllib "), ESearchCase::IgnoreCase);

                // Do not depend on factory defaults in unattended UE4.27 imports.
                // Authored OBJ/MTL pairs must explicitly create material assets;
                // bare character/proxy OBJ files must explicitly avoid placeholder
                // material references.
                UFbxImportUI* ImportOptions = NewObject<UFbxImportUI>();
                ImportOptions->bImportMaterials = bHasMaterialLibrary;
                ImportOptions->bImportTextures = bHasMaterialLibrary;
                if (ImportOptions->StaticMeshImportData)
                {
                    ImportOptions->StaticMeshImportData->bRemoveDegenerates = true;
                }
                Task->Options = ImportOptions;

                bBareObjMaterialImportDisabled = !bHasMaterialLibrary;
                bAuthoredMaterialImportForced = bHasMaterialLibrary;
            }
        }

        TArray<UAssetImportTask*> Tasks;
        Tasks.Add(Task);
        AssetTools.Get().ImportAssetTasks(Tasks);

        const FString AssetName = FPaths::GetBaseFilename(Filename);
        const FString ExpectedObjectPath = FString::Printf(
            TEXT("%s/%s.%s"), *DestinationPath, *AssetName, *AssetName);
        UObject* ImportedAsset = LoadObject<UObject>(nullptr, *ExpectedObjectPath);

        int32 MarkedMaterialPackages = 0;
        if (UStaticMesh* ImportedMesh = Cast<UStaticMesh>(ImportedAsset))
        {
            // OBJ/MTL import can leave material packages referenced by the mesh without
            // flagging those secondary packages for persistence. Mark every real
            // imported material package dirty so the final SaveDirtyPackages pass writes
            // the mesh and its material dependencies together.
            for (const FStaticMaterial& StaticMaterial : ImportedMesh->StaticMaterials)
            {
                UMaterialInterface* Material = StaticMaterial.MaterialInterface;
                UPackage* Package = Material ? Material->GetOutermost() : nullptr;
                if (Package && Package != GetTransientPackage())
                {
                    Package->MarkPackageDirty();
                    if (Package->GetName().StartsWith(TEXT("/Game/Production/")))
                    {
                        ImportedMaterialPackages.AddUnique(Package);
                    }
                    ++MarkedMaterialPackages;
                }
            }
            ImportedMesh->MarkPackageDirty();
        }

        // UE4.27 import factories are not perfectly consistent about which result
        // collection they populate in unattended mode. Treat the import as successful
        // when any task result is reported or the expected asset can be resolved.
        const bool bImported =
            Task->ImportedObjectPaths.Num() > 0 ||
            Task->Result.Num() > 0 ||
            ImportedAsset != nullptr;

        UE_LOG(
            LogTemp,
            Display,
            TEXT("ShireProductionImport result: %s | paths=%d result=%d resolved=%s bare-obj-materials=%s authored-material-import=%s smoothing-injected=%s material-packages-marked=%d"),
            *Filename,
            Task->ImportedObjectPaths.Num(),
            Task->Result.Num(),
            ImportedAsset ? TEXT("yes") : TEXT("no"),
            bBareObjMaterialImportDisabled ? TEXT("disabled") : TEXT("n/a"),
            bAuthoredMaterialImportForced ? TEXT("forced") : TEXT("n/a"),
            bInjectedSmoothingGroup ? TEXT("yes") : TEXT("no"),
            MarkedMaterialPackages);

        if (!bImported)
        {
            ++Failed;
            UE_LOG(LogTemp, Error, TEXT("ShireProductionImport FAILED: %s"), *Filename);
        }
        else
        {
            UE_LOG(LogTemp, Display, TEXT("ShireProductionImport imported: %s"), *Filename);
        }
    }

    // OBJ import may create secondary material packages that UE4.27 does not
    // consistently include in UAssetImportTask::ImportedObjectPaths. Save those exact
    // packages explicitly before the broader dirty-package pass; on unattended UE4.27
    // the generic dirty save can report success while secondary OBJ materials remain
    // memory-only, leaving the saved meshes with broken /Game/Production references.
    if (ImportedMaterialPackages.Num() > 0)
    {
        for (UPackage* Package : ImportedMaterialPackages)
        {
            if (Package)
            {
                Package->MarkPackageDirty();
            }
        }

        (void)FEditorFileUtils::PromptForCheckoutAndSave(
            ImportedMaterialPackages,
            false, // bCheckDirty
            false  // bPromptToSave
        );

        UE_LOG(
            LogTemp,
            Display,
            TEXT("ShireProductionImport explicit material package save: %d packages"),
            ImportedMaterialPackages.Num());
    }

    // Keep the broad pass for imported meshes/textures and any other secondary assets.
    const bool bSavedDirtyPackages = FEditorFileUtils::SaveDirtyPackages(
        false,  // bPromptUserToSave
        false,  // bSaveMapPackages
        true,   // bSaveContentPackages
        true,   // bFastSave
        false,  // bNotifyNoPackagesSaved
        false); // bCanBeDeclined
    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireProductionImport secondary package save: %s"),
        bSavedDirtyPackages ? TEXT("ok") : TEXT("no-dirty-or-failed"));

    UE_LOG(LogTemp, Display, TEXT("ShireProductionImport: %d files, %d failures"), SourceFiles.Num(), Failed);
    return Failed == 0 ? 0 : 3;
}
