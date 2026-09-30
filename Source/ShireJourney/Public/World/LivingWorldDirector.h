#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LivingWorldDirector.generated.h"

class APawn;
class AShireAmbientNPC;
class AChapterWorldRouter;
class AShireWorldEventInteraction;
class AWorldAmbientMotionActor;
class UStaticMesh;
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
    uint32 GetAppliedWorldRevision() const { return AppliedWorldRevision; }
    void GatherActiveAmbientNPCsNear(
        const FVector& Origin,
        float Radius,
        TArray<AShireAmbientNPC*>& OutNPCs) const;

private:
    struct FActiveMicroEvent
    {
        FName EventId = NAME_None;
        FName EventType = NAME_None;
        TArray<TWeakObjectPtr<AActor>> Actors;
        float ExpiresAt = 0.0f;
    };

    struct FChapterPopulationProfile
    {
        float SpawnInterval = 0.35f;
        float InnerRadius = 850.0f;
        float OuterRadius = 2600.0f;
        float CullRadius = 6200.0f;
        float DangerPopulationFraction = 0.50f;
    };

    UPROPERTY()
    UShireQuestSubsystem* QuestSubsystem = nullptr;

    TWeakObjectPtr<AChapterWorldRouter> WorldRouter;
    uint32 AppliedWorldRevision = 0;
    bool SynchronizeCommittedWorld();
    void HandleWorldCommitted(uint32 Revision);

    TMap<FName, TArray<FName>> AllowedEventTypesByChapter;
    TArray<FActiveMicroEvent> ActiveEvents;
    TArray<TWeakObjectPtr<AShireAmbientNPC>> BaselinePopulation;
    // Builder-authored ambient residents are persistent world content, not pooled
    // LivingWorld-owned population. Keep weak registration only so bounded social
    // queries can see them without transferring lifecycle ownership.
    TArray<TWeakObjectPtr<AShireAmbientNPC>> PersistentAmbientNPCs;
    TArray<TWeakObjectPtr<AShireAmbientNPC>> AmbientNPCPool;
    TArray<TWeakObjectPtr<AShireWorldEventInteraction>> InteractionPool;
    TArray<TWeakObjectPtr<AWorldAmbientMotionActor>> AmbientMotionPool;
    mutable TWeakObjectPtr<APawn> CachedPlayerPawn;
    TMap<FName, int32> BaselineTargetByChapter;
    TMap<FName, TArray<FName>> BaselineRolesByChapter;
    TMap<FName, FChapterPopulationProfile> PopulationProfilesByChapter;
    FRandomStream Random;
    FName ActiveChapterId = NAME_None;
    FName LastEventType = NAME_None;
    float NextEventTime = 0.0f;
    float NextMaintenanceTime = 0.0f;
    float NextPopulationSpawnTime = 0.0f;
    float MinSecondsBetweenEventStarts = 12.0f;
    float EventCullDistance = 5000.0f;
    float PopulationInnerRadius = 850.0f;
    float PopulationOuterRadius = 2600.0f;
    float PopulationCullRadius = 6200.0f;
    float PopulationSpawnInterval = 0.35f;
    float DangerPopulationFraction = 0.50f;
    int32 MaxActiveMicroEvents = 3;
    int32 MaxActiveFaunaGroups = 2;
    int32 MaxAmbientNPCPoolSize = 24;
    int32 MaxInteractionPoolSize = 12;
    int32 MaxAmbientMotionPoolSize = 16;

    UFUNCTION()
    void HandleChapterChanged(FName PreviousChapterId, FName NewChapterId);

    UFUNCTION()
    void HandleExperienceChanged(FName RouteId, FName EpisodeId, FName PlayableCharacterId);

    bool LoadEventContract();
    bool LoadLifeSaturationContract();
    void ResetForCurrentChapter();
    void ApplyPopulationProfile();
    void CleanupExpiredEvents();
    void CleanupBaselinePopulation();
    void ReconcilePersistentAmbientNPCRegistry();
    void ReleaseAmbientNPCToPool(AShireAmbientNPC* NPC);
    AShireAmbientNPC* AcquireAmbientNPC(const FVector& Location);
    void ReleaseInteractionToPool(AShireWorldEventInteraction* Interaction);
    AShireWorldEventInteraction* AcquireInteraction(const FVector& Location);
    void ReleaseAmbientMotionToPool(AWorldAmbientMotionActor* Actor);
    AWorldAmbientMotionActor* AcquireAmbientMotionActor(
        const FVector& Location,
        const FRotator& Rotation);
    APawn* ResolvePlayerPawn() const;
    void MaintainBaselinePopulation();
    void TryStartMicroEvent();
    bool SpawnEvent(FName EventType, FActiveMicroEvent& OutEvent);
    AShireWorldEventInteraction* SpawnPlayerInteraction(
        FName EventId,
        FName EventType,
        const FVector& Origin);
    AShireAmbientNPC* SpawnAmbientActor(
        const FVector& Location,
        FName RoutineRole,
        FName ActivityProp,
        const FVector& TravelOffset,
        float Speed,
        float MinWait,
        float MaxWait);
    AWorldAmbientMotionActor* SpawnAmbientMotionActor(
        UStaticMesh* Mesh,
        const FVector& Location,
        const FRotator& Rotation,
        const FVector& Scale,
        FName MotionMode,
        float Amplitude,
        float Speed);
    FName ChooseEventType() const;
    FName ResolveResidentRole(FName ChapterId) const;
    FName ChooseBaselineRole() const;
    FName ChooseBaselineProp(FName RoleName) const;
    FVector ChooseEventOrigin(float MinRadius = 700.0f, float MaxRadius = 1500.0f);
    FVector ChoosePopulationOrigin();
    bool ResolveGroundedAmbientPoint(const FVector& Candidate, FVector& OutGroundedPoint) const;
    void ApplyChapterWeatherContext();
    bool IsStoryDangerActive() const;
};
