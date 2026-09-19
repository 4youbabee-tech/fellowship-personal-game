#include "ShireProductionImportCommandlet.h"

#include "AssetImportTask.h"
#include "AssetToolsModule.h"
#include "FileHelpers.h"
#include "Factories/FbxImportUI.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Modules/ModuleManager.h"

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
        if (FPaths::GetExtension(Filename).Equals(TEXT("obj"), ESearchCase::IgnoreCase))
        {
            FString ObjSource;
            if (FFileHelper::LoadFileToString(ObjSource, *Filename) &&
                !ObjSource.Contains(TEXT("mtllib "), ESearchCase::IgnoreCase))
            {
                UFbxImportUI* ImportOptions = NewObject<UFbxImportUI>();
                ImportOptions->bImportMaterials = false;
                ImportOptions->bImportTextures = false;
                Task->Options = ImportOptions;
                bBareObjMaterialImportDisabled = true;
            }
        }

        TArray<UAssetImportTask*> Tasks;
        Tasks.Add(Task);
        AssetTools.Get().ImportAssetTasks(Tasks);

        const FString AssetName = FPaths::GetBaseFilename(Filename);
        const FString ExpectedObjectPath = FString::Printf(
            TEXT("%s/%s.%s"), *DestinationPath, *AssetName, *AssetName);
        UObject* ImportedAsset = LoadObject<UObject>(nullptr, *ExpectedObjectPath);

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
            TEXT("ShireProductionImport result: %s | paths=%d result=%d resolved=%s bare-obj-materials=%s"),
            *Filename,
            Task->ImportedObjectPaths.Num(),
            Task->Result.Num(),
            ImportedAsset ? TEXT("yes") : TEXT("no"),
            bBareObjMaterialImportDisabled ? TEXT("disabled") : TEXT("authored"));

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
    // consistently include in UAssetImportTask::ImportedObjectPaths. Save every dirty
    // content package once after the batch so meshes never point at transient materials.
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
