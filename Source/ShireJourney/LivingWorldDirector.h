#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LivingWorldDirector.generated.h"

class AShireAmbientNPC;
class UShireQuestSubsystem;

UCLASS()
class SHIREJOURNEY_API ALivingWorldDirector : public AActor
{
    GENERATED_BODY()

public:
    ALivingWorldDirector();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    virtual void Tick(float DeltaSeconds) override;

private:
    struct FActiveMicroEvent
    {
        FName EventId = NAME_None;
        FName EventType = NAME_None;
        TArray<TWeakObjectPtr<AActor>> Actors;
        float ExpiresAt = 0.0f;
    };

    UPROPERTY()
    UShireQuestSubsystem* QuestSubsystem = nullptr;

    TMap<FName, TArray<FName>> AllowedEventTypesByChapter;
    TArray<FActiveMicroEvent> ActiveEvents;
    TArray<TWeakObjectPtr<AShireAmbientNPC>> BaselinePopulation;
    TMap<FName, int32> BaselineTargetByChapter;
    TMap<FName, TArray<FName>> BaselineRolesByChapter;
    FRandomStream Random;
    FName ActiveChapterId = NAME_None;
    FName LastEventType = NAME_None;
    float NextEventTime = 0.0f;
    float NextPopulationSpawnTime = 0.0f;
    float MinSecondsBetweenEventStarts = 12.0f;
    float EventCullDistance = 5000.0f;
    float PopulationInnerRadius = 850.0f;
    float PopulationOuterRadius = 2600.0f;
    float PopulationCullRadius = 6200.0f;
    float PopulationSpawnInterval = 0.35f;
    int32 MaxActiveMicroEvents = 3;

    UFUNCTION()
    void HandleChapterChanged(FName PreviousChapterId, FName NewChapterId);

    UFUNCTION()
    void HandleExperienceChanged(FName RouteId, FName EpisodeId, FName PlayableCharacterId);

    bool LoadEventContract();
    bool LoadLifeSaturationContract();
    void ResetForCurrentChapter();
    void CleanupExpiredEvents();
    void CleanupBaselinePopulation();
    void MaintainBaselinePopulation();
    void TryStartMicroEvent();
    bool SpawnEvent(FName EventType, FActiveMicroEvent& OutEvent);
    AShireAmbientNPC* SpawnAmbientActor(
        const FVector& Location,
        FName RoutineRole,
        FName ActivityProp,
        const FVector& TravelOffset,
        float Speed,
        float MinWait,
        float MaxWait);
    FName ChooseEventType() const;
    FName ResolveResidentRole(FName ChapterId) const;
    FName ChooseBaselineRole() const;
    FName ChooseBaselineProp(FName RoleName) const;
    FVector ChooseEventOrigin(float MinRadius = 700.0f, float MaxRadius = 1500.0f);
    FVector ChoosePopulationOrigin();
    void ApplyChapterWeatherContext();
    bool IsStoryDangerActive() const;
};
