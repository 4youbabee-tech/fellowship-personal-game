#include "ShireProductionImportCommandlet.h"

#include "AssetImportTask.h"
#include "AssetToolsModule.h"
#include "HAL/FileManager.h"
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
    IFileManager::Get().FindFilesRecursive(SourceFiles, *SourceRoot, TEXT("*.obj"), true, false, false);
    SourceFiles.Sort();

    if (SourceFiles.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("ShireProductionImport: no OBJ assets found at %s"), *SourceRoot);
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
        Task->bAsync = false;

        TArray<UAssetImportTask*> Tasks;
        Tasks.Add(Task);
        AssetTools.Get().ImportAssetTasks(Tasks);

        if (Task->ImportedObjectPaths.Num() == 0)
        {
            ++Failed;
            UE_LOG(LogTemp, Error, TEXT("ShireProductionImport FAILED: %s"), *Filename);
        }
        else
        {
            UE_LOG(LogTemp, Display, TEXT("ShireProductionImport imported: %s"), *Filename);
        }
    }

    UE_LOG(LogTemp, Display, TEXT("ShireProductionImport: %d files, %d failures"), SourceFiles.Num(), Failed);
    return Failed == 0 ? 0 : 3;
}
