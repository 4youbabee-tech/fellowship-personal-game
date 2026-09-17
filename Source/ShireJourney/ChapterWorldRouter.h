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

    void LoadChapterWorld(FName ChapterId);
    void ClearPrototypeBuilders();
    FVector GetChapterSpawnLocation(FName ChapterId) const;
    void MovePlayerToChapterStart(FName ChapterId);
};
