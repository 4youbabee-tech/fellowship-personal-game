#pragma once

#include "CoreMinimal.h"
#include "Engine/StreamableManager.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "UObject/SoftObjectPath.h"
#include "ShireChapterAssetStreamingSubsystem.generated.h"

class USkeletalMesh;
class UAnimSequence;

DECLARE_MULTICAST_DELEGATE_TwoParams(
    FOnShireChapterAssetsReady,
    FName /* ChapterId */,
    FName /* RouteId */);

DECLARE_MULTICAST_DELEGATE_TwoParams(
    FOnShireChapterAssetsCommitted,
    FName /* ChapterId */,
    FName /* RouteId */);

DECLARE_MULTICAST_DELEGATE_TwoParams(
    FOnShireChapterAssetsFailed,
    FName /* ChapterId */,
    FName /* RouteId */);

DECLARE_MULTICAST_DELEGATE_OneParam(
    FOnShireCharacterRigReady,
    FName /* CharacterId */);

UCLASS()
class SHIREJOURNEY_API UShireChapterAssetStreamingSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    void RequestChapterAssets(FName ChapterId, FName RouteId);
    void CancelPendingRequest();
    bool CommitPendingRequest(FName ChapterId, FName RouteId);
    bool IsChapterBankReady(FName ChapterId, FName RouteId) const;
    int32 GetChapterBankSize(FName ChapterId, FName RouteId) const;

    void RequestCharacterRig(FName CharacterId);
    bool ResolveCharacterRig(
        FName CharacterId,
        USkeletalMesh*& OutSkeletalMesh,
        UClass*& OutAnimClass) const;
    bool ResolveCharacterLocomotionAssets(
        FName CharacterId,
        USkeletalMesh*& OutSkeletalMesh,
        UClass*& OutAnimClass,
        UAnimSequence*& OutIdle,
        UAnimSequence*& OutWalk,
        UAnimSequence*& OutRun) const;

    FOnShireChapterAssetsReady OnChapterAssetsReady;
    FOnShireChapterAssetsCommitted OnChapterAssetsCommitted;
    FOnShireChapterAssetsFailed OnChapterAssetsFailed;
    FOnShireCharacterRigReady OnCharacterRigReady;

private:
    struct FChapterBankRuntime
    {
        FName RouteId = NAME_None;
        TArray<FSoftObjectPath> Assets;
    };

    struct FCharacterRigRuntime
    {
        FSoftObjectPath SkeletalMeshPath;
        FSoftObjectPath AnimClassPath;
        FSoftObjectPath IdleAnimationPath;
        FSoftObjectPath WalkAnimationPath;
        FSoftObjectPath RunAnimationPath;
        TSharedPtr<FStreamableHandle> Handle;
        bool bSequenceLocomotionRequired = false;
        bool bAnimBlueprintPackagePresent = false;
        bool bAvailabilityChecked = false;
        bool bPackagesPresent = false;
        double LastAvailabilityCheckSeconds = -1.0;
    };

    bool LoadStreamingPlan();
    FName ResolveBankId(FName ChapterId, FName RouteId) const;
    void HandleAsyncLoadComplete(uint64 CompletedSerial);
    void PublishPendingReady(
        uint64 CompletedSerial,
        FName CompletedChapter,
        FName CompletedRoute);
    bool AreBankAssetsResolved(FName ChapterId, FName RouteId, int32& OutMissingCount) const;
    void FailPendingRequest(FName ChapterId, FName RouteId, const TCHAR* Reason);
    void HandleCharacterRigLoadComplete(FName CharacterId);

    TMap<FName, FChapterBankRuntime> Banks;
    TMap<FName, FCharacterRigRuntime> CharacterRigRequests;
    FStreamableManager StreamableManager;
    TSharedPtr<FStreamableHandle> ResidentHandle;
    TSharedPtr<FStreamableHandle> PendingHandle;

    FName ResidentChapterId = NAME_None;
    FName ResidentRouteId = NAME_None;
    FName PendingChapterId = NAME_None;
    FName PendingRouteId = NAME_None;
    uint64 RequestSerial = 0;
    bool bPlanReady = false;
    bool bPendingCompatibilityReady = false;
};
