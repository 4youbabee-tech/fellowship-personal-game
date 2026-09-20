#include "ShireProductionImportCommandlet.h"

#include "AssetImportTask.h"
#include "AssetRegistryModule.h"
#include "AssetToolsModule.h"
#include "FileHelpers.h"
#include "Factories/FbxImportUI.h"
#include "Factories/FbxStaticMeshImportData.h"
#include "Factories/MaterialInstanceConstantFactoryNew.h"
#include "Engine/StaticMesh.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformFilemanager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceConstant.h"
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
    const FString WorkingRoot = FPaths::ConvertRelativePathToFull(
        FPaths::Combine(FPaths::ProjectSavedDir(), TEXT("ShireProductionImportWorking")));

    // Never normalize/import directly from tracked SourceAssets. The older path
    // injected smoothing-group text into real .obj source files, which made
    // GitHub Desktop show hundreds/thousands of local changes after one-click
    // import. Work on an ignored Saved/ copy so source assets stay byte-stable.
    IFileManager::Get().DeleteDirectory(*WorkingRoot, false, true);
    IPlatformFile& PlatformFile = FPlatformFileManager::Get().GetPlatformFile();
    if (!PlatformFile.CopyDirectoryTree(*WorkingRoot, *SourceRoot, true))
    {
        UE_LOG(LogTemp, Error, TEXT("ShireProductionImport: failed to create working copy %s from %s"), *WorkingRoot, *SourceRoot);
        return 4;
    }

    TArray<FString> SourceFiles;
    TArray<FString> TextureFiles;
    TArray<FString> MeshFiles;
    TArray<FString> MaterialLibraryFiles;
    IFileManager::Get().FindFilesRecursive(TextureFiles, *WorkingRoot, TEXT("*.bmp"), true, false, false);
    IFileManager::Get().FindFilesRecursive(MeshFiles, *WorkingRoot, TEXT("*.obj"), true, false, false);
    IFileManager::Get().FindFilesRecursive(MaterialLibraryFiles, *WorkingRoot, TEXT("*.mtl"), true, false, false);
    TextureFiles.Sort();
    MeshFiles.Sort();
    MaterialLibraryFiles.Sort();
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

    // UE4.27 unattended OBJ import does not reliably persist simple MTL-created
    // material packages. Create deterministic project material instances first,
    // then bind OBJ slots to those assets after mesh import.
    UMaterialInterface* ProductionMaterialParent = LoadObject<UMaterialInterface>(
        nullptr, TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
    int32 SynthesizedMaterialAssets = 0;

    if (ProductionMaterialParent)
    {
        for (const FString& MtlFilename : MaterialLibraryFiles)
        {
            FString RelativeMtl = MtlFilename;
            FPaths::MakePathRelativeTo(RelativeMtl, *(WorkingRoot / TEXT("")));
            RelativeMtl.ReplaceInline(TEXT("\\"), TEXT("/"));
            const FString RelativeDir = FPaths::GetPath(RelativeMtl);
            const FString DestinationPath = RelativeDir.IsEmpty()
                ? TEXT("/Game/Production")
                : FString::Printf(TEXT("/Game/Production/%s"), *RelativeDir);

            FString MtlText;
            if (!FFileHelper::LoadFileToString(MtlText, *MtlFilename))
            {
                UE_LOG(LogTemp, Warning, TEXT("ShireProductionImport: could not read MTL %s"), *MtlFilename);
                continue;
            }

            TArray<FString> Lines;
            MtlText.ParseIntoArrayLines(Lines, true);
            FString CurrentMaterialName;
            FLinearColor CurrentBaseColor(0.35f, 0.35f, 0.35f, 1.0f);

            auto FlushMaterial = [&]()
            {
                if (CurrentMaterialName.IsEmpty())
                {
                    return;
                }

                const FString ObjectPath = FString::Printf(
                    TEXT("%s/%s.%s"),
                    *DestinationPath,
                    *CurrentMaterialName,
                    *CurrentMaterialName);

                UMaterialInstanceConstant* Instance =
                    LoadObject<UMaterialInstanceConstant>(nullptr, *ObjectPath);

                if (!Instance)
                {
                    UMaterialInstanceConstantFactoryNew* Factory =
                        NewObject<UMaterialInstanceConstantFactoryNew>();
                    Factory->InitialParent = ProductionMaterialParent;
                    Instance = Cast<UMaterialInstanceConstant>(
                        AssetTools.Get().CreateAsset(
                            CurrentMaterialName,
                            DestinationPath,
                            UMaterialInstanceConstant::StaticClass(),
                            Factory));
                }

                if (Instance)
                {
                    Instance->SetVectorParameterValueEditorOnly(
                        FMaterialParameterInfo(TEXT("Color")),
                        CurrentBaseColor);
                    Instance->PostEditChange();
                    Instance->MarkPackageDirty();
                    ImportedMaterialPackages.AddUnique(Instance->GetOutermost());
                    ++SynthesizedMaterialAssets;
                }
                else
                {
                    ++Failed;
                    UE_LOG(
                        LogTemp,
                        Error,
                        TEXT("ShireProductionImport: failed to synthesize material %s/%s"),
                        *DestinationPath,
                        *CurrentMaterialName);
                }
            };

            for (const FString& RawLine : Lines)
            {
                const FString Line = RawLine.TrimStartAndEnd();
                if (Line.StartsWith(TEXT("newmtl "), ESearchCase::IgnoreCase))
                {
                    FlushMaterial();
                    CurrentMaterialName = Line.Mid(7).TrimStartAndEnd();
                    CurrentBaseColor = FLinearColor(0.35f, 0.35f, 0.35f, 1.0f);
                }
                else if (Line.StartsWith(TEXT("Kd "), ESearchCase::IgnoreCase) &&
                    !CurrentMaterialName.IsEmpty())
                {
                    TArray<FString> Parts;
                    Line.ParseIntoArrayWS(Parts);
                    if (Parts.Num() >= 4)
                    {
                        CurrentBaseColor = FLinearColor(
                            FCString::Atof(*Parts[1]),
                            FCString::Atof(*Parts[2]),
                            FCString::Atof(*Parts[3]),
                            1.0f);
                    }
                }
            }
            FlushMaterial();
        }

        if (ImportedMaterialPackages.Num() > 0)
        {
            (void)FEditorFileUtils::PromptForCheckoutAndSave(
                ImportedMaterialPackages,
                false,
                false);
        }

        UE_LOG(
            LogTemp,
            Display,
            TEXT("ShireProductionImport synthesized authored materials: libraries=%d assets=%d packages=%d"),
            MaterialLibraryFiles.Num(),
            SynthesizedMaterialAssets,
            ImportedMaterialPackages.Num());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("ShireProductionImport: production material parent missing"));
        ++Failed;
    }
    TSet<FString> AuthoredMaterialDestinationPaths;
    int32 RecoveredMaterialBindings = 0;

    for (const FString& Filename : SourceFiles)
    {
        FString Relative = Filename;
        FPaths::MakePathRelativeTo(Relative, *(WorkingRoot / TEXT("")));
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
                // Filename points into the ignored Saved/ working copy, so this
                // normalization can never dirty tracked SourceAssets.
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
                // MTL definitions are synthesized above into deterministic material
                // instances. Disable FBX/OBJ material creation here to prevent UE4.27
                // from emitting transient/broken duplicate package references.
                ImportOptions->bImportMaterials = false;
                ImportOptions->bImportTextures = false;
                if (ImportOptions->StaticMeshImportData)
                {
                    ImportOptions->StaticMeshImportData->bRemoveDegenerates = true;
                }
                Task->Options = ImportOptions;

                bBareObjMaterialImportDisabled = !bHasMaterialLibrary;
                bAuthoredMaterialImportForced = bHasMaterialLibrary;
                if (bHasMaterialLibrary)
                {
                    AuthoredMaterialDestinationPaths.Add(DestinationPath);
                }
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
            for (FStaticMaterial& StaticMaterial : ImportedMesh->StaticMaterials)
            {
                UMaterialInterface* Material = StaticMaterial.MaterialInterface;

                // UE4.27 OBJ import can serialize the material package path into the
                // mesh while leaving MaterialInterface unresolved in unattended mode.
                // Recover the material object by the imported slot name immediately,
                // then save both sides of the reference in the same commandlet run.
                if (bAuthoredMaterialImportForced && !StaticMaterial.MaterialSlotName.IsNone())
                {
                    const FString SlotName = StaticMaterial.MaterialSlotName.ToString();
                    const FString CandidateObjectPath = FString::Printf(
                        TEXT("%s/%s.%s"),
                        *DestinationPath,
                        *SlotName,
                        *SlotName);
                    if (UMaterialInterface* AuthoredMaterial =
                        LoadObject<UMaterialInterface>(nullptr, *CandidateObjectPath))
                    {
                        Material = AuthoredMaterial;
                        StaticMaterial.MaterialInterface = AuthoredMaterial;
                        ++RecoveredMaterialBindings;
                    }
                }

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

    // Sweep authored-material destination folders through AssetRegistry as a second
    // recovery path. Some UE4.27 OBJ factories register the material asset but do not
    // return it through the import task or static-mesh material pointer during the same
    // unattended import. Including in-memory assets here lets us mark and persist those
    // packages before any startup/chapter audit reloads the mesh from disk.
    if (AuthoredMaterialDestinationPaths.Num() > 0)
    {
        FAssetRegistryModule& AssetRegistryModule =
            FModuleManager::LoadModuleChecked<FAssetRegistryModule>(TEXT("AssetRegistry"));
        int32 RegistryMaterialAssets = 0;

        for (const FString& DestinationPath : AuthoredMaterialDestinationPaths)
        {
            TArray<FAssetData> Assets;
            AssetRegistryModule.Get().GetAssetsByPath(
                FName(*DestinationPath),
                Assets,
                false, // bRecursive
                false  // bIncludeOnlyOnDiskAssets
            );

            for (const FAssetData& AssetData : Assets)
            {
                if (UMaterialInterface* Material = Cast<UMaterialInterface>(AssetData.GetAsset()))
                {
                    UPackage* Package = Material->GetOutermost();
                    if (Package && Package != GetTransientPackage())
                    {
                        Package->MarkPackageDirty();
                        ImportedMaterialPackages.AddUnique(Package);
                        ++RegistryMaterialAssets;
                    }
                }
            }
        }

        UE_LOG(
            LogTemp,
            Display,
            TEXT("ShireProductionImport material registry recovery: folders=%d assets=%d bindings=%d packages=%d"),
            AuthoredMaterialDestinationPaths.Num(),
            RegistryMaterialAssets,
            RecoveredMaterialBindings,
            ImportedMaterialPackages.Num());
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

    // The copy is only needed during import. Best-effort cleanup keeps Saved/
    // smaller; if interrupted, .gitignore still prevents it becoming source debt.
    IFileManager::Get().DeleteDirectory(*WorkingRoot, false, true);

    return Failed == 0 ? 0 : 3;
}
