#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ShireQuestTrigger.generated.h"

class UBoxComponent;

UCLASS()
class SHIREJOURNEY_API AShireQuestTrigger : public AActor
{
    GENERATED_BODY()

public:
    AShireQuestTrigger();

protected:
    virtual void BeginPlay() override;

    UFUNCTION()
    void OnTriggerBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
        UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep,
        const FHitResult& SweepResult);

public:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Quest")
    UBoxComponent* TriggerBox;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    FName QuestId = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    int32 RequiredStage = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    int32 StageAfterTrigger = -1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    FName NextQuestId = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    int32 NextQuestStage = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Chapter")
    FName NextChapterId = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Chapter")
    FName NextChapterQuestId = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Chapter")
    int32 NextChapterQuestStage = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Story")
    FName StoryBeatId = NAME_None;

    // Lightweight optional exploration progression. These flags are persisted through
    // the existing story-beat save data but do not replace the active main quest.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="SideStory")
    FName RequiredSideStoryBeat = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="SideStory")
    FName SideStoryBeatAfterTrigger = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    FText ObjectiveMessage;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    bool bTriggerOnce = true;

private:
    bool bHasTriggered = false;
};
