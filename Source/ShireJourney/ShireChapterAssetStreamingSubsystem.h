#pragma once

#include "CoreMinimal.h"
#include "Engine/StreamableManager.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "UObject/SoftObjectPath.h"
#include "ShireChapterAssetStreamingSubsystem.generated.h"

class USkeletalMesh;

DECLARE_MULTICAST_DELEGATE_TwoParams(
    FOnShireChapterAssetsReady,
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

    FOnShireChapterAssetsReady OnChapterAssetsReady;
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
        TSharedPtr<FStreamableHandle> Handle;
        bool bAvailabilityChecked = false;
        bool bPackagesPresent = false;
    };

    bool LoadStreamingPlan();
    FName ResolveBankId(FName ChapterId, FName RouteId) const;
    void HandleAsyncLoadComplete(uint64 CompletedSerial);
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
