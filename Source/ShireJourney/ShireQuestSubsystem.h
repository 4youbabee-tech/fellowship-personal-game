#pragma once

#include "CoreMinimal.h"
#include <initializer_list>
#include "Subsystems/GameInstanceSubsystem.h"
#include "ShireRouteState.h"
#include "ShireQuestSubsystem.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnQuestStageChanged, FName, QuestId, int32, NewStage);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnActiveQuestChanged, FName, QuestId);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnChapterChanged, FName, PreviousChapterId, FName, NewChapterId);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnStoryBeatTriggered, FName, StoryBeatId);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnExperienceChanged, FName, RouteId, FName, EpisodeId, FName, PlayableCharacterId);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnQuestStateRestored);

USTRUCT(BlueprintType)
struct FShireQuestDefinition
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    FText Title;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    TArray<FText> Objectives;
};

UCLASS()
class SHIREJOURNEY_API UShireQuestSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    UPROPERTY(BlueprintAssignable, Category="Quest")
    FOnQuestStageChanged OnQuestStageChanged;

    UPROPERTY(BlueprintAssignable, Category="Quest")
    FOnActiveQuestChanged OnActiveQuestChanged;

    UPROPERTY(BlueprintAssignable, Category="Chapter")
    FOnChapterChanged OnChapterChanged;

    UPROPERTY(BlueprintAssignable, Category="Story")
    FOnStoryBeatTriggered OnStoryBeatTriggered;

    UPROPERTY(BlueprintAssignable, Category="Route")
    FOnExperienceChanged OnExperienceChanged;

    // Emitted only after a save-state restore has rebuilt quest/chapter state. Runtime
    // story guards use this event so they can repair legacy/incomplete terminal states
    // without interfering with normal trigger-driven cinematics or chapter hand-offs.
    UPROPERTY(BlueprintAssignable, Category="Save")
    FOnQuestStateRestored OnQuestStateRestored;

    UFUNCTION(BlueprintCallable, Category="Quest")
    int32 GetQuestStage(FName QuestId) const;

    UFUNCTION(BlueprintCallable, Category="Quest")
    void SetQuestStage(FName QuestId, int32 NewStage);

    UFUNCTION(BlueprintCallable, Category="Quest")
    void AdvanceQuest(FName QuestId, int32 Amount = 1);

    UFUNCTION(BlueprintCallable, Category="Quest")
    void StartQuest(FName QuestId, int32 InitialStage = 0);

    UFUNCTION(BlueprintCallable, Category="Chapter")
    void StartChapter(FName ChapterId, FName StartingQuestId = NAME_None, int32 StartingQuestStage = 0);

    UFUNCTION(BlueprintCallable, Category="Route")
    void StartExperience(FName RouteId, FName EpisodeId, FName InPlayableCharacterId,
        FName ChapterId, FName StartingQuestId = NAME_None, int32 StartingQuestStage = 0);

    UFUNCTION(BlueprintCallable, Category="Story")
    void TriggerStoryBeat(FName StoryBeatId);

    UFUNCTION(BlueprintPure, Category="Story")
    bool HasStoryBeatTriggered(FName StoryBeatId) const;

    UFUNCTION(BlueprintPure, Category="Quest")
    FName GetActiveQuestId() const { return ActiveQuestId; }

    UFUNCTION(BlueprintPure, Category="Quest")
    int32 GetActiveQuestStage() const;

    UFUNCTION(BlueprintPure, Category="Quest")
    FText GetActiveQuestTitle() const;

    UFUNCTION(BlueprintPure, Category="Quest")
    FText GetActiveObjective() const;

    UFUNCTION(BlueprintPure, Category="Chapter")
    FName GetCurrentChapterId() const { return CurrentChapterId; }

    UFUNCTION(BlueprintPure, Category="Route")
    FName GetCurrentRouteId() const { return CurrentRouteId; }

    UFUNCTION(BlueprintPure, Category="Route")
    FName GetCurrentEpisodeId() const { return CurrentEpisodeId; }

    UFUNCTION(BlueprintPure, Category="Route")
    FName GetPlayableCharacterId() const { return PlayableCharacterId; }

    const TMap<FName, int32>& GetAllQuestStages() const { return QuestStages; }
    const TArray<FName>& GetCompletedStoryBeats() const { return CompletedStoryBeats; }
    TMap<FName, FShireRouteProgress> GetRouteProgressSnapshot() const;
    bool GetCurrentRouteSavedTransform(FVector& OutLocation, FRotator& OutRotation) const;
    bool RememberNamedNPCEvent(FName CanonicalProfileId, FName EventId, int32 Priority = 50);
    bool HasNamedNPCMemory(FName CanonicalProfileId, FName EventId) const;
    int32 AdjustNamedNPCRelationship(FName CanonicalProfileId, FName OtherProfileId, int32 Delta);
    TMap<FName, FShireNPCMemoryBucket> GetNPCMemorySnapshot() const { return NPCMemoryState; }
    void RestoreNPCMemoryState(const TMap<FName, FShireNPCMemoryBucket>& InState);
    void RestoreQuestState(const TMap<FName, int32>& InStages, FName InActiveQuestId,
        FName InCurrentChapterId, const TArray<FName>& InCompletedStoryBeats,
        FName InCurrentRouteId, FName InCurrentEpisodeId, FName InPlayableCharacterId,
        const TMap<FName, FShireRouteProgress>& InRouteProgress);

private:
    UPROPERTY()
    TMap<FName, int32> QuestStages;

    UPROPERTY()
    FName ActiveQuestId = NAME_None;

    UPROPERTY()
    FName CurrentChapterId = TEXT("P1C01");

    UPROPERTY()
    FName CurrentRouteId = TEXT("FrodoMain");

    UPROPERTY()
    FName CurrentEpisodeId = TEXT("P1C01_Main");

    UPROPERTY()
    FName PlayableCharacterId = TEXT("Frodo");

    UPROPERTY()
    TArray<FName> CompletedStoryBeats;

    UPROPERTY()
    TMap<FName, FShireRouteProgress> RouteProgress;

    UPROPERTY()
    TMap<FName, FShireQuestDefinition> QuestDefinitions;

    UPROPERTY()
    TMap<FName, FShireNPCMemoryBucket> NPCMemoryState;

    void BuildQuestDefinitions();
    void AddQuestDefinition(FName QuestId, const FString& Title, std::initializer_list<const TCHAR*> Objectives);
    FShireRouteProgress CaptureCurrentRouteProgress(bool bCapturePlayerTransform) const;
    void ApplyRouteProgress(const FShireRouteProgress& Progress);
    FName MakeNPCMemoryKey(FName CanonicalProfileId) const;
};
