#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ShireQuestTrigger.generated.h"

class UBoxComponent;
class UShireQuestSubsystem;
class AShirePlayerCharacter;

UCLASS()
class SHIREJOURNEY_API AShireQuestTrigger : public AActor
{
    GENERATED_BODY()

public:
    AShireQuestTrigger();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION()
    void OnTriggerBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
        UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep,
        const FHitResult& SweepResult);

    UFUNCTION()
    void OnTriggerEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
        UPrimitiveComponent* OtherComp, int32 OtherBodyIndex);

    UFUNCTION()
    void HandleQuestStageChanged(FName ChangedQuestId, int32 NewStage);

    UFUNCTION()
    void HandleActiveQuestChanged(FName NewQuestId);

    UFUNCTION()
    void HandleStoryBeatTriggered(FName TriggeredStoryBeatId);

    UFUNCTION()
    void HandleQuestStateRestored();

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

    // A second persisted condition supports small group gates without inventing
    // another quest-state authority or polling every frame.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="SideStory")
    FName AdditionalRequiredSideStoryBeat = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="SideStory")
    FName SideStoryBeatAfterTrigger = NAME_None;

    // Optional Journey Discovery reward. This never advances the main story.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Exploration")
    FName DiscoveryId = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Exploration")
    FText DiscoveryDisplayName;

    // If this closing beat already happened, the optional trigger is no longer valid.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Exploration")
    FName BlockedAfterStoryBeat = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    FText ObjectiveMessage;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    bool bTriggerOnce = true;

private:
    bool bHasTriggered = false;
    bool bActivationInProgress = false;
    TWeakObjectPtr<AShirePlayerCharacter> OverlappingPlayer;

    void TryActivateForPlayer(AShirePlayerCharacter* Player);
    void ReevaluateOverlappingPlayer();
};