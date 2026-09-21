#pragma once

#include "CoreMinimal.h"
#include "Engine/StreamableManager.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "UObject/SoftObjectPath.h"
#include "ShireChapterAssetStreamingSubsystem.generated.h"

DECLARE_MULTICAST_DELEGATE_TwoParams(
    FOnShireChapterAssetsReady,
    FName /* ChapterId */,
    FName /* RouteId */);

UCLASS()
class SHIREJOURNEY_API UShireChapterAssetStreamingSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    void RequestChapterAssets(FName ChapterId, FName RouteId);
    bool IsChapterBankReady(FName ChapterId, FName RouteId) const;
    int32 GetChapterBankSize(FName ChapterId, FName RouteId) const;

    FOnShireChapterAssetsReady OnChapterAssetsReady;

private:
    struct FChapterBankRuntime
    {
        FName RouteId = NAME_None;
        TArray<FSoftObjectPath> Assets;
    };

    bool LoadStreamingPlan();
    FName ResolveBankId(FName ChapterId, FName RouteId) const;
    void HandleAsyncLoadComplete(uint64 CompletedSerial);

    TMap<FName, FChapterBankRuntime> Banks;
    FStreamableManager StreamableManager;
    TSharedPtr<FStreamableHandle> ResidentHandle;
    TSharedPtr<FStreamableHandle> PendingHandle;

    FName ResidentChapterId = NAME_None;
    FName ResidentRouteId = NAME_None;
    FName PendingChapterId = NAME_None;
    FName PendingRouteId = NAME_None;
    uint64 RequestSerial = 0;
    bool bPlanReady = false;
};
