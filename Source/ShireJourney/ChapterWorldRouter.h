#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ChapterWorldRouter.generated.h"

class UShireChapterAssetStreamingSubsystem;
class APawn;

UCLASS()
class SHIREJOURNEY_API AChapterWorldRouter : public AActor
{
    GENERATED_BODY()

public:
    AChapterWorldRouter();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UFUNCTION()
    void HandleChapterChanged(FName PreviousChapterId, FName NewChapterId);

    UFUNCTION()
    void HandleExperienceChanged(FName RouteId, FName EpisodeId, FName PlayableCharacterId);

    void LoadChapterWorld(FName ChapterId, bool bRestoreRouteTransform = false);
    void CommitChapterWorld(
        FName ChapterId,
        FName RouteId,
        FName EpisodeId,
        bool bRestoreRouteTransform);

    void HandleChapterAssetsReady(FName ChapterId, FName RouteId);
    void ClearPrototypeBuilders();
    FVector GetChapterSpawnLocation(FName ChapterId) const;
    bool ResolveGroundedSpawnLocation(APawn* PlayerPawn, const FVector& RequestedLocation, FVector& OutGroundedLocation) const;
    bool MovePlayerToChapterStart(FName ChapterId, bool bRestoreRouteTransform);
    void SetPlayerWorldHold(bool bHold);
    UShireChapterAssetStreamingSubsystem* AssetStreamingSubsystem = nullptr;

    FName LastLoadedRouteId = NAME_None;
    FName LastLoadedEpisodeId = NAME_None;
    FName LastLoadedChapterId = NAME_None;

    FName PendingRouteId = NAME_None;
    FName PendingEpisodeId = NAME_None;
    FName PendingChapterId = NAME_None;
    bool bPendingRestoreRouteTransform = false;
    bool bPlayerWorldHoldActive = false;
};
