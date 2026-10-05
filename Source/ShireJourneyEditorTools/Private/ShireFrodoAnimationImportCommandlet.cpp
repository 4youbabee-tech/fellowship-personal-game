#include "ShireFrodoAnimationImportCommandlet.h"

#include "Animation/AnimSequence.h"
#include "Animation/Skeleton.h"
#include "AssetImportTask.h"
#include "AssetRegistryModule.h"
#include "AssetToolsModule.h"
#include "Engine/SkeletalMesh.h"
#include "Factories/FbxAnimSequenceImportData.h"
#include "Factories/FbxImportUI.h"
#include "Factories/FbxSkeletalMeshImportData.h"
#include "HAL/FileManager.h"
#include "Misc/PackageName.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "UObject/Package.h"
#include "Modules/ModuleManager.h"

namespace ShireFrodoAnimationImport
{
    struct FClipSpec
    {
        const TCHAR* SourceFile;
        const TCHAR* AssetName;
        const TCHAR* Role;
    };

    static const FClipSpec RequiredClips[] =
    {
        { TEXT("Frodo_Idle_Retarget.fbx"), TEXT("A_Frodo_Idle"), TEXT("Idle") },
        { TEXT("Frodo_Walk_Retarget.fbx"), TEXT("A_Frodo_Walk"), TEXT("Walk") },
        { TEXT("Frodo_Run_Retarget.fbx"), TEXT("A_Frodo_Run"), TEXT("Run") }
    };
}

UShireFrodoAnimationImportCommandlet::UShireFrodoAnimationImportCommandlet()
{
    IsClient = false;
    IsServer = false;
    IsEditor = true;
    LogToConsole = true;
    ShowErrorCount = true;
}

int32 UShireFrodoAnimationImportCommandlet::Main(const FString& Params)
{
    FString TargetFbx;
    FString AnimationDir;
    FString RigDestination = TEXT("/Game/Production/Characters/Rigs/FRODO");
    FString AnimationDestination = TEXT("/Game/Production/Characters/Animations/FRODO");

    if (!FParse::Value(*Params, TEXT("TargetFbx="), TargetFbx) ||
        !FParse::Value(*Params, TEXT("AnimationDir="), AnimationDir))
    {
        UE_LOG(
            LogTemp,
            Error,
            TEXT("ShireFrodoAnimationImport: required args missing; expected -TargetFbx=... -AnimationDir=..."));
        return 41;
    }

    FParse::Value(*Params, TEXT("RigDestination="), RigDestination);
    FParse::Value(*Params, TEXT("AnimationDestination="), AnimationDestination);

    TargetFbx = FPaths::ConvertRelativePathToFull(TargetFbx);
    AnimationDir = FPaths::ConvertRelativePathToFull(AnimationDir);

    if (!FPaths::GetExtension(TargetFbx).Equals(TEXT("fbx"), ESearchCase::IgnoreCase) ||
        !IFileManager::Get().FileExists(*TargetFbx))
    {
        UE_LOG(LogTemp, Error, TEXT("ShireFrodoAnimationImport: exact target FBX missing or invalid: %s"), *TargetFbx);
        return 42;
    }

    if (!RigDestination.StartsWith(TEXT("/Game/")) ||
        !AnimationDestination.StartsWith(TEXT("/Game/")))
    {
        UE_LOG(
            LogTemp,
            Error,
            TEXT("ShireFrodoAnimationImport: destinations must be project /Game paths rig=%s animation=%s"),
            *RigDestination,
            *AnimationDestination);
        return 43;
    }

    for (const ShireFrodoAnimationImport::FClipSpec& Clip : ShireFrodoAnimationImport::RequiredClips)
    {
        const FString ClipPath = FPaths::Combine(AnimationDir, Clip.SourceFile);
        if (!IFileManager::Get().FileExists(*ClipPath) ||
            !FPaths::GetExtension(ClipPath).Equals(TEXT("fbx"), ESearchCase::IgnoreCase))
        {
            UE_LOG(
                LogTemp,
                Error,
                TEXT("ShireFrodoAnimationImport: required FBX animation missing role=%s file=%s"),
                Clip.Role,
                *ClipPath);
            return 44;
        }
    }

    FAssetToolsModule& AssetTools =
        FModuleManager::LoadModuleChecked<FAssetToolsModule>(TEXT("AssetTools"));

    UAssetImportTask* RigTask = NewObject<UAssetImportTask>();
    RigTask->Filename = TargetFbx;
    RigTask->DestinationPath = RigDestination;
    RigTask->DestinationName = TEXT("SK_FRODO");
    RigTask->bAutomated = true;
    RigTask->bSave = true;
    RigTask->bReplaceExisting = true;
    RigTask->bReplaceExistingSettings = true;

    UFbxImportUI* RigOptions = NewObject<UFbxImportUI>();
    RigOptions->OriginalImportType = EFBXImportType::FBXIT_SkeletalMesh;
    RigOptions->MeshTypeToImport = EFBXImportType::FBXIT_SkeletalMesh;
    RigOptions->bAutomatedImportShouldDetectType = false;
    RigOptions->bImportAsSkeletal = true;
    RigOptions->bImportMesh = true;
    RigOptions->bImportAnimations = false;
    RigOptions->bImportMaterials = false;
    RigOptions->bImportTextures = false;
    if (RigOptions->SkeletalMeshImportData)
    {
        RigOptions->SkeletalMeshImportData->bUseT0AsRefPose = true;
    }
    RigTask->Options = RigOptions;

    TArray<UAssetImportTask*> RigTasks;
    RigTasks.Add(RigTask);
    AssetTools.Get().ImportAssetTasks(RigTasks);

    const FString ExpectedRigObjectPath = FString::Printf(
        TEXT("%s/SK_FRODO.SK_FRODO"),
        *RigDestination);
    FAssetRegistryModule& AssetRegistryModule =
        FModuleManager::LoadModuleChecked<FAssetRegistryModule>(TEXT("AssetRegistry"));
    const FAssetData RigAssetData =
        AssetRegistryModule.Get().GetAssetByObjectPath(FName(*ExpectedRigObjectPath));

    USkeletalMesh* SkeletalMesh =
        FindObject<USkeletalMesh>(nullptr, *ExpectedRigObjectPath);
    if (!SkeletalMesh && RigAssetData.IsValid())
    {
        SkeletalMesh = Cast<USkeletalMesh>(RigAssetData.GetAsset());
    }

    if (!SkeletalMesh ||
        !RigAssetData.IsValid() ||
        RigAssetData.AssetClass != USkeletalMesh::StaticClass()->GetFName())
    {
        UE_LOG(
            LogTemp,
            Error,
            TEXT("ShireFrodoAnimationImport: exact Rogue skeletal registration failed path=%s assetRegistry=%s resultObjects=%d"),
            *ExpectedRigObjectPath,
            RigAssetData.IsValid() ? TEXT("valid") : TEXT("missing"),
            RigTask->Result.Num());
        return 46;
    }

    const int32 ReferenceBoneCount = SkeletalMesh->GetRefSkeleton().GetNum();
    USkeleton* Skeleton = SkeletalMesh->GetSkeleton();
    if (!Skeleton || ReferenceBoneCount != 48)
    {
        UE_LOG(
            LogTemp,
            Error,
            TEXT("ShireFrodoAnimationImport: exact Rogue skeleton sanity failed bones=%d skeleton=%s"),
            ReferenceBoneCount,
            Skeleton ? *Skeleton->GetPathName() : TEXT("NONE"));
        return 47;
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireFrodoAnimationImport: exact-rig-pass mesh=%s bones=%d skeleton=%s use-t0-ref-pose=yes"),
        *SkeletalMesh->GetPathName(),
        ReferenceBoneCount,
        *Skeleton->GetPathName());

    auto SaveExactAssetPackage = [](UObject* Asset, const TCHAR* Label) -> bool
    {
        if (!Asset)
        {
            UE_LOG(LogTemp, Error, TEXT("ShireFrodoAnimationImport: package-save missing asset label=%s"), Label);
            return false;
        }

        UPackage* Package = Asset->GetOutermost();
        if (!Package || Package == GetTransientPackage())
        {
            UE_LOG(LogTemp, Error, TEXT("ShireFrodoAnimationImport: package-save invalid package label=%s asset=%s"),
                Label, *Asset->GetPathName());
            return false;
        }

        const FString Filename = FPackageName::LongPackageNameToFilename(
            Package->GetName(),
            FPackageName::GetAssetPackageExtension());
        IFileManager::Get().MakeDirectory(*FPaths::GetPath(Filename), true);
        Package->MarkPackageDirty();

        const bool bSaved = UPackage::SavePackage(
            Package,
            Asset,
            RF_Public | RF_Standalone,
            *Filename,
            GError,
            nullptr,
            false,
            true,
            SAVE_NoError);
        const bool bExists = IFileManager::Get().FileExists(*Filename);
        if (bSaved && bExists)
        {
            UE_LOG(
                LogTemp,
                Display,
                TEXT("ShireFrodoAnimationImport: package-save label=%s asset=%s saved=yes exists=yes file=%s"),
                Label,
                *Asset->GetPathName(),
                *Filename);
        }
        else
        {
            UE_LOG(
                LogTemp,
                Error,
                TEXT("ShireFrodoAnimationImport: package-save label=%s asset=%s saved=%s exists=%s file=%s"),
                Label,
                *Asset->GetPathName(),
                bSaved ? TEXT("yes") : TEXT("no"),
                bExists ? TEXT("yes") : TEXT("no"),
                *Filename);
        }
        return bSaved && bExists;
    };

    int32 ImportedSequenceCount = 0;
    TArray<UAnimSequence*> ImportedSequences;
    for (const ShireFrodoAnimationImport::FClipSpec& Clip : ShireFrodoAnimationImport::RequiredClips)
    {
        const FString ClipPath = FPaths::Combine(AnimationDir, Clip.SourceFile);

        UAssetImportTask* Task = NewObject<UAssetImportTask>();
        Task->Filename = ClipPath;
        Task->DestinationPath = AnimationDestination;
        Task->DestinationName = Clip.AssetName;
        Task->bAutomated = true;
        Task->bSave = true;
        Task->bReplaceExisting = true;
        Task->bReplaceExistingSettings = true;

        UFbxImportUI* Options = NewObject<UFbxImportUI>();
        Options->OriginalImportType = EFBXImportType::FBXIT_Animation;
        Options->MeshTypeToImport = EFBXImportType::FBXIT_Animation;
        Options->bAutomatedImportShouldDetectType = false;
        Options->bImportAsSkeletal = false;
        Options->bImportMesh = false;
        Options->bImportAnimations = true;
        Options->bImportMaterials = false;
        Options->bImportTextures = false;
        Options->Skeleton = Skeleton;

        if (Options->AnimSequenceImportData)
        {
            Options->AnimSequenceImportData->AnimationLength = EFBXAnimationLengthImportType::FBXALIT_ExportedTime;
            Options->AnimSequenceImportData->bUseDefaultSampleRate = false;
            Options->AnimSequenceImportData->CustomSampleRate = 0;
            Options->AnimSequenceImportData->bImportCustomAttribute = false;
            Options->AnimSequenceImportData->bImportBoneTracks = true;
            Options->AnimSequenceImportData->bPreserveLocalTransform = false;
        }
        Task->Options = Options;

        TArray<UAssetImportTask*> Tasks;
        Tasks.Add(Task);
        AssetTools.Get().ImportAssetTasks(Tasks);

        const FString ExpectedSequenceObjectPath = FString::Printf(
            TEXT("%s/%s.%s"),
            *AnimationDestination,
            Clip.AssetName,
            Clip.AssetName);
        const FAssetData SequenceAssetData =
            AssetRegistryModule.Get().GetAssetByObjectPath(FName(*ExpectedSequenceObjectPath));

        UAnimSequence* Sequence =
            FindObject<UAnimSequence>(nullptr, *ExpectedSequenceObjectPath);
        if (!Sequence && SequenceAssetData.IsValid())
        {
            Sequence = Cast<UAnimSequence>(SequenceAssetData.GetAsset());
        }

        if (!Sequence ||
            !SequenceAssetData.IsValid() ||
            SequenceAssetData.AssetClass != UAnimSequence::StaticClass()->GetFName())
        {
            UE_LOG(
                LogTemp,
                Error,
                TEXT("ShireFrodoAnimationImport: animation registration failed role=%s path=%s assetRegistry=%s resultObjects=%d"),
                Clip.Role,
                *ExpectedSequenceObjectPath,
                SequenceAssetData.IsValid() ? TEXT("valid") : TEXT("missing"),
                Task->Result.Num());
            return 48;
        }

        const int32 FrameCount = Sequence->GetNumberOfFrames();
        const float PlayLength = Sequence->GetPlayLength();
        const bool bSameSkeleton = Sequence->GetSkeleton() == Skeleton;

        if (!bSameSkeleton || FrameCount <= 1 || !FMath::IsFinite(PlayLength) || PlayLength <= 0.0f)
        {
            UE_LOG(
                LogTemp,
                Error,
                TEXT("ShireFrodoAnimationImport: animation technical gate failed role=%s asset=%s same-skeleton=%s frames=%d play-length=%.6f"),
                Clip.Role,
                *Sequence->GetPathName(),
                bSameSkeleton ? TEXT("yes") : TEXT("no"),
                FrameCount,
                PlayLength);
            return 49;
        }

        ImportedSequences.Add(Sequence);
        ++ImportedSequenceCount;
        UE_LOG(
            LogTemp,
            Display,
            TEXT("ShireFrodoAnimationImport: animation-pass role=%s asset=%s skeleton=%s frames=%d play-length=%.6f"),
            Clip.Role,
            *Sequence->GetPathName(),
            *Skeleton->GetPathName(),
            FrameCount,
            PlayLength);
    }

    if (ImportedSequenceCount != 3)
    {
        UE_LOG(
            LogTemp,
            Error,
            TEXT("ShireFrodoAnimationImport: clip count mismatch imported=%d expected=3"),
            ImportedSequenceCount);
        return 50;
    }

    bool bPersistencePass =
        SaveExactAssetPackage(SkeletalMesh, TEXT("skeletal-mesh")) &&
        SaveExactAssetPackage(Skeleton, TEXT("skeleton"));
    for (UAnimSequence* Sequence : ImportedSequences)
    {
        bPersistencePass =
            SaveExactAssetPackage(Sequence, TEXT("animation-sequence")) &&
            bPersistencePass;
    }
    if (!bPersistencePass)
    {
        UE_LOG(LogTemp, Error, TEXT("ShireFrodoAnimationImport: deterministic package persistence failed"));
        return 51;
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireFrodoAnimationImport: UE4_ANIMATION_PACKAGE_PERSISTENCE_PASS assets=5"));

    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireFrodoAnimationImport: UE4_ANIMATION_IMPORT_TECHNICAL_PASS clips=3 bones=48 skeleton=%s"),
        *Skeleton->GetPathName());
    return 0;
}
