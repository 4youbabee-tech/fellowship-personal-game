#pragma once

#include "CoreMinimal.h"
#include <initializer_list>
#include "Subsystems/GameInstanceSubsystem.h"
#include "ShireQuestSubsystem.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnQuestStageChanged, FName, QuestId, int32, NewStage);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnActiveQuestChanged, FName, QuestId);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnChapterChanged, FName, PreviousChapterId, FName, NewChapterId);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnStoryBeatTriggered, FName, StoryBeatId);

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

    UFUNCTION(BlueprintCallable, Category="Story")
    void TriggerStoryBeat(FName StoryBeatId);

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

    const TMap<FName, int32>& GetAllQuestStages() const { return QuestStages; }
    void RestoreQuestState(const TMap<FName, int32>& InStages, FName InActiveQuestId, FName InCurrentChapterId);

private:
    UPROPERTY()
    TMap<FName, int32> QuestStages;

    UPROPERTY()
    FName ActiveQuestId = NAME_None;

    UPROPERTY()
    FName CurrentChapterId = TEXT("P1C01");

    UPROPERTY()
    TMap<FName, FShireQuestDefinition> QuestDefinitions;

    void BuildQuestDefinitions();
    void AddQuestDefinition(FName QuestId, const FString& Title, std::initializer_list<const TCHAR*> Objectives);
};
