#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ChapterWorldRouter.generated.h"

UCLASS()
class SHIREJOURNEY_API AChapterWorldRouter : public AActor
{
    GENERATED_BODY()

public:
    AChapterWorldRouter();

protected:
    virtual void BeginPlay() override;

private:
    UFUNCTION()
    void HandleChapterChanged(FName PreviousChapterId, FName NewChapterId);

    UFUNCTION()
    void HandleExperienceChanged(FName RouteId, FName EpisodeId, FName PlayableCharacterId);

    void LoadChapterWorld(FName ChapterId, bool bRestoreRouteTransform = false);
    void ClearPrototypeBuilders();
    FVector GetChapterSpawnLocation(FName ChapterId) const;
    void MovePlayerToChapterStart(FName ChapterId, bool bRestoreRouteTransform);
    FName LastLoadedRouteId = NAME_None;
    FName LastLoadedEpisodeId = NAME_None;
    FName LastLoadedChapterId = NAME_None;
};
