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
DECLARE_MULTICAST_DELEGATE_ThreeParams(
    FOnWorldTransitionRequested,
    FName /* TargetChapterId */,
    FName /* TargetRouteId */,
    FName /* TargetEpisodeId */);

USTRUCT(BlueprintType)
struct FShireQuestDefinition
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    FText Title;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    TArray<FText> Objectives;
};

struct FShireJourneyDiscoveryDefinition
{
    FName DiscoveryId = NAME_None;
    FName RouteId = NAME_None;
    FName ChapterId = NAME_None;
    FName RegionId = NAME_None;
    FName CategoryId = NAME_None;
    FString DisplayLabel;
    int32 Insight = 0;
};

struct FShireJourneyInsightMilestoneDefinition
{
    FName MilestoneId = NAME_None;
    int32 Threshold = 0;
};

struct FShireJourneyRegionBonusDefinition
{
    FName RouteId = NAME_None;
    FName ChapterId = NAME_None;
    int32 RequiredDiscoveries = 0;
    int32 BonusInsight = 0;
};

struct FShireSideActivityProgressionDefinition
{
    FName DiscoveryId = NAME_None;
    FName ActivityId = NAME_None;
    FName ActivityType = NAME_None;
    FName RouteId = NAME_None;
    FName ChapterId = NAME_None;
    FName AvailableAfterStoryBeat = NAME_None;
    FName EndsBeforeStoryBeat = NAME_None;
};

struct FShireChapterProductionDefinition
{
    FName RouteId = NAME_None;
    FName ChapterId = NAME_None;
    FString DisplayName;
    FString MacroRegion;
    FString PrimaryRegion;
    TArray<FString> LandmarkSequence;
};

struct FShireWorldMapNodeDefinition
{
    FName NodeId = NAME_None;
    FName RouteId = NAME_None;
    FName ChapterId = NAME_None;
    FString DisplayName;
    FString MacroRegion;
    float X = 0.0f;
    float Y = 0.0f;
    bool bChapterAnchor = false;
};

struct FShireWorldMapEdgeDefinition
{
    FName FromNodeId = NAME_None;
    FName ToNodeId = NAME_None;
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

    // Native pre-mutation transaction boundary. ChapterWorldRouter subscribes here
    // so it can snapshot the exact committed origin before logical route/chapter
    // state advances toward an asynchronous destination.
    FOnWorldTransitionRequested OnWorldTransitionRequested;

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

    UFUNCTION(BlueprintPure, Category="Ring")
    bool IsRingQuestActive() const;

    UFUNCTION(BlueprintPure, Category="Ring")
    FName GetRingBearerId() const;

    UFUNCTION(BlueprintPure, Category="Ring")
    FName GetRingStateTag() const;

    UFUNCTION(BlueprintPure, Category="Ring")
    int32 GetRingPressureTier() const;

    UFUNCTION(BlueprintCallable, Category="Exploration")
    bool RegisterJourneyDiscovery(FName DiscoveryId);

    UFUNCTION(BlueprintPure, Category="Exploration")
    bool HasJourneyDiscovery(FName DiscoveryId) const;

    UFUNCTION(BlueprintPure, Category="SideActivity")
    bool HasSideActivityForDiscovery(FName DiscoveryId) const;

    UFUNCTION(BlueprintPure, Category="SideActivity")
    bool IsSideActivityAvailable(FName ActivityId) const;

    UFUNCTION(BlueprintPure, Category="SideActivity")
    bool IsSideActivityDiscoveryAvailable(FName DiscoveryId) const;

    UFUNCTION(BlueprintPure, Category="SideActivity")
    FName GetSideActivityIdForDiscovery(FName DiscoveryId) const;

    UFUNCTION(BlueprintCallable, Category="SideActivity")
    bool CompleteSideActivityDiscovery(FName DiscoveryId);

    UFUNCTION(BlueprintPure, Category="Exploration")
    int32 GetJourneyInsight() const;

    UFUNCTION(BlueprintPure, Category="Exploration")
    bool HasJourneyInsightMilestone(FName MilestoneId) const;

    const TArray<FName>& GetJourneyDiscoveryIds() const { return JourneyDiscoveryIds; }
    const TArray<FName>& GetJourneyInsightMilestones() const { return JourneyInsightMilestones; }
    void RestoreJourneyDiscoveryState(
        const TArray<FName>& InDiscoveryIds,
        int32 SavedJourneyInsight,
        const TArray<FName>& InMilestones);

    UFUNCTION(BlueprintCallable, Category="Progression")
    void AwardProgressionXP(FName TrackId, int32 Amount);

    UFUNCTION(BlueprintPure, Category="Progression")
    int32 GetProgressionXP(FName TrackId) const;

    UFUNCTION(BlueprintPure, Category="Progression")
    int32 GetProgressionRank(FName TrackId) const;

    UFUNCTION(BlueprintPure, Category="Progression")
    int32 GetFellowshipBond() const;

    TMap<FName, int32> GetProgressionSnapshot() const { return ProgressionXP; }
    void RestoreProgressionState(const TMap<FName, int32>& InProgressionXP);

    UFUNCTION(BlueprintPure, Category="Chronicle")
    int32 GetChronicleCount() const { return ChronicleEntryIds.Num(); }

    UFUNCTION(BlueprintPure, Category="Chronicle")
    bool HasChronicleEntry(FName EntryId) const { return ChronicleEntryIds.Contains(EntryId); }

    UFUNCTION(BlueprintPure, Category="MapKnowledge")
    int32 GetKnownRegionCount() const { return KnownMapRegionIds.Num(); }

    UFUNCTION(BlueprintPure, Category="MapKnowledge")
    bool HasKnownMapRegion(FName RegionId) const { return KnownMapRegionIds.Contains(RegionId); }

    const TArray<FName>& GetChronicleEntryIds() const { return ChronicleEntryIds; }
    const TArray<FName>& GetKnownMapRegionIds() const { return KnownMapRegionIds; }
    FString GetChronicleEntryDisplayLabel(FName EntryId) const;
    FString GetChronicleEntryContextLabel(FName EntryId) const;
    FString GetKnownMapRegionDisplayLabel(FName RegionId) const;
    void RestoreKnowledgeState(const TArray<FName>& InChronicleEntryIds, const TArray<FName>& InKnownMapRegionIds);

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

    UFUNCTION(BlueprintPure, Category="World")
    FString GetCurrentChapterDisplayName() const;

    UFUNCTION(BlueprintPure, Category="World")
    FString GetCurrentPrimaryRegionName() const;

    UFUNCTION(BlueprintPure, Category="World")
    FString GetCurrentMacroRegionName() const;

    UFUNCTION(BlueprintPure, Category="World")
    FString GetCurrentLandmarkSummary() const;

    UFUNCTION(BlueprintPure, Category="MapKnowledge")
    bool IsWorldMapNodeVisible(FName NodeId) const;

    UFUNCTION(BlueprintPure, Category="MapKnowledge")
    FName GetCurrentWorldMapNodeId() const;

    const TArray<FShireWorldMapNodeDefinition>& GetWorldMapNodes() const { return WorldMapNodes; }
    const TArray<FShireWorldMapEdgeDefinition>& GetWorldMapEdges() const { return WorldMapEdges; }

    const TMap<FName, int32>& GetAllQuestStages() const { return QuestStages; }
    const TArray<FName>& GetCompletedStoryBeats() const { return CompletedStoryBeats; }
    TMap<FName, FShireRouteProgress> GetRouteProgressSnapshot() const;
    bool GetCurrentRouteSavedTransform(FVector& OutLocation, FRotator& OutRotation) const;
    bool RememberNamedNPCEvent(FName CanonicalProfileId, FName EventId, int32 Priority = 50);
    bool HasNamedNPCMemory(FName CanonicalProfileId, FName EventId) const;
    int32 AdjustNamedNPCRelationship(FName CanonicalProfileId, FName OtherProfileId, int32 Delta);
    int32 GetNamedNPCRelationship(FName CanonicalProfileId, FName OtherProfileId) const;
    bool HasRecentNPCDialogueVariant(FName CanonicalProfileId, FName VariantId) const;
    void RecordNamedNPCDialogueUse(FName CanonicalProfileId, FName VariantId, FName PartnerProfileId, int32 MaxRecentVariants = 12);
    TMap<FName, FShireNPCMemoryBucket> GetNPCMemorySnapshot() const { return NPCMemoryState; }
    void RestoreNPCMemoryState(const TMap<FName, FShireNPCMemoryBucket>& InState);

    // Save/rollback restore is a logical transaction. State fields are rebuilt while
    // broadcasts are suppressed, then published once after the full snapshot exists.
    bool BeginPersistenceRestore();
    void CommitPersistenceRestore(bool bBroadcastQuestStateRestored = true);
    void AbortPersistenceRestore();
    bool IsPersistenceRestoreInProgress() const { return bPersistenceRestoreInProgress; }
    uint32 GetPersistenceRestorePublicationSerial() const { return PersistenceRestorePublicationSerial; }

    // A save restore can change world identity without calling StartChapter first.
    // Publish the destination intent after BeginPersistenceRestore succeeds but before
    // any restored logical fields are applied, so rollback captures the live origin.
    void PreparePersistenceWorldTransition(
        FName TargetChapterId,
        FName TargetRouteId,
        FName TargetEpisodeId);

    // Destructive chapter-age housekeeping belongs to the committed world boundary,
    // not the logical request boundary.
    void CommitWorldBoundState();

    void RestoreQuestState(const TMap<FName, int32>& InStages, FName InActiveQuestId,
        FName InCurrentChapterId, const TArray<FName>& InCompletedStoryBeats,
        FName InCurrentRouteId, FName InCurrentEpisodeId, FName InPlayableCharacterId,
        const TMap<FName, FShireRouteProgress>& InRouteProgress);

    // Save/rollback input is normalized before publication. Unknown routes or
    // unsupported chapters fail closed; known legacy aliases are repaired.
    bool CanonicalizeRestoredExperienceIdentity(
        FName& InOutRouteId,
        FName& InOutChapterId,
        FName& InOutEpisodeId,
        FName& InOutPlayableCharacterId,
        TMap<FName, FShireRouteProgress>& InOutRouteProgress) const;

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

    UPROPERTY()
    TArray<FName> JourneyDiscoveryIds;

    UPROPERTY()
    TArray<FName> JourneyInsightMilestones;

    UPROPERTY()
    int32 JourneyInsight = 0;

    UPROPERTY()
    TMap<FName, int32> ProgressionXP;

    UPROPERTY()
    TArray<FName> ChronicleEntryIds;

    UPROPERTY()
    TArray<FName> KnownMapRegionIds;

    bool bPersistenceRestoreInProgress = false;
    uint32 PersistenceRestorePublicationSerial = 0;
    FName PersistenceRestorePreviousChapterId = NAME_None;
    FName PersistenceRestorePreviousRouteId = NAME_None;
    FName PersistenceRestorePreviousEpisodeId = NAME_None;
    FName PersistenceRestorePreviousPlayableCharacterId = NAME_None;
    FName PersistenceRestorePreviousActiveQuestId = NAME_None;

    TMap<FName, FShireJourneyDiscoveryDefinition> JourneyDiscoveryDefinitions;
    TArray<FShireJourneyInsightMilestoneDefinition> JourneyInsightDefinitions;
    TArray<FShireJourneyRegionBonusDefinition> JourneyRegionBonusDefinitions;
    TMap<FName, FShireSideActivityProgressionDefinition> SideActivityProgressionDefinitions;
    TMap<FName, FShireSideActivityProgressionDefinition> SideActivityDefinitionsById;
    TMap<FName, FShireChapterProductionDefinition> ChapterProductionDefinitions;
    TArray<FShireWorldMapNodeDefinition> WorldMapNodes;
    TArray<FShireWorldMapEdgeDefinition> WorldMapEdges;
    bool bSideActivityRewardInProgress = false;

    void BuildQuestDefinitions();
    void AddQuestDefinition(FName QuestId, const FString& Title, std::initializer_list<const TCHAR*> Objectives);
    FShireRouteProgress CaptureCurrentRouteProgress(bool bCapturePlayerTransform) const;
    void ApplyRouteProgress(const FShireRouteProgress& Progress);
    bool NormalizeExperienceIdentity(
        FName RouteId,
        FName& InOutChapterId,
        FName& InOutEpisodeId,
        FName& InOutPlayableCharacterId,
        bool bRepairMalformed) const;
    void SanitizeRouteProgressMap(TMap<FName, FShireRouteProgress>& InOutRouteProgress) const;
    FName MakeNPCMemoryKey(FName CanonicalProfileId) const;
    FName ResolveCanonicalNPCProfile(FName ProfileHint) const;
    int32 ResolvePersistentMemoryBudget(FName ProfileHint) const;
    int32 ResolveRelationshipBudget(FName ProfileHint) const;
    static int32 ChapterOrdinal(FName ChapterId);
    void PruneNPCMemoryForCurrentChapter();
    void RecordStoryBeatForEligibleNPCs(FName StoryBeatId);
    bool LoadJourneyDiscoveryPlan();
    bool LoadSideActivityPlan();
    bool LoadPart1ProductionAtlas();
    bool LoadPart1WorldMap();
    const FShireWorldMapNodeDefinition* FindWorldMapNode(FName NodeId) const;
    const FShireChapterProductionDefinition* FindChapterProductionDefinition(FName RouteId, FName ChapterId) const;
    static FName MakeChapterProductionKey(FName RouteId, FName ChapterId);
    bool IsSideActivityDefinitionAvailable(const FShireSideActivityProgressionDefinition& Definition) const;
    void RebuildJourneyInsightState();
    FName MakeJourneyRegionCompletionId(FName RouteId, FName ChapterId) const;
    void AwardDiscoveryProgression(const FShireJourneyDiscoveryDefinition& Definition);
    static bool IsValidProgressionTrack(FName TrackId);
    void AwardSideActivityProgression(FName DiscoveryId);
    void UnlockDiscoveryKnowledge(const FShireJourneyDiscoveryDefinition& Definition);
    static FName MakeChronicleEntryId(FName DiscoveryId);
    static FName MakeKnownMapRegionId(FName RouteId, FName ChapterId);
};
