#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "ShireNPCContextSubsystem.generated.h"

USTRUCT(BlueprintType)
struct FShireNPCProfileRuntime
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category="NPCContext")
    FName ProfileId = NAME_None;

    UPROPERTY(BlueprintReadOnly, Category="NPCContext")
    FString DisplayName;

    UPROPERTY(BlueprintReadOnly, Category="NPCContext")
    FName ProfileType = NAME_None;

    UPROPERTY(BlueprintReadOnly, Category="NPCContext")
    FName PersistenceTier = NAME_None;

    UPROPERTY(BlueprintReadOnly, Category="NPCContext")
    FName Community = NAME_None;

    UPROPERTY(BlueprintReadOnly, Category="NPCContext")
    TArray<FName> Aliases;

    UPROPERTY(BlueprintReadOnly, Category="NPCContext")
    TArray<FName> Regions;

    UPROPERTY(BlueprintReadOnly, Category="NPCContext")
    TArray<FName> Roles;

    UPROPERTY(BlueprintReadOnly, Category="NPCContext")
    TArray<FName> KnowledgeTags;

    UPROPERTY(BlueprintReadOnly, Category="NPCContext")
    TArray<FName> Anchors;

    UPROPERTY(BlueprintReadOnly, Category="NPCContext")
    FString Origin;

    UPROPERTY(BlueprintReadOnly, Category="NPCContext")
    FString Occupation;

    UPROPERTY(BlueprintReadOnly, Category="NPCContext")
    TArray<FString> BiographyFacts;

    UPROPERTY(BlueprintReadOnly, Category="NPCContext")
    TArray<FString> KnowledgeLimits;

    UPROPERTY(BlueprintReadOnly, Category="NPCContext")
    TArray<FName> AttitudeTags;
};

USTRUCT(BlueprintType)
struct FShireBoundedDialogueResult
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category="NPCDialogue")
    bool bValid = false;

    UPROPERTY(BlueprintReadOnly, Category="NPCDialogue")
    FName SpeakerProfileId = NAME_None;

    UPROPERTY(BlueprintReadOnly, Category="NPCDialogue")
    FName ListenerProfileId = NAME_None;

    UPROPERTY(BlueprintReadOnly, Category="NPCDialogue")
    FName IntentId = NAME_None;

    UPROPERTY(BlueprintReadOnly, Category="NPCDialogue")
    FName VariantId = NAME_None;

    UPROPERTY(BlueprintReadOnly, Category="NPCDialogue")
    FText Text;

    UPROPERTY(BlueprintReadOnly, Category="NPCDialogue")
    FName VoiceCue = NAME_None;

    UPROPERTY(BlueprintReadOnly, Category="NPCDialogue")
    FName ProvenanceMode = TEXT("SILENT_FALLBACK");

    UPROPERTY(BlueprintReadOnly, Category="NPCDialogue")
    bool bMemoryInfluenced = false;

    UPROPERTY(BlueprintReadOnly, Category="NPCDialogue")
    FName WorldMood = NAME_None;

    UPROPERTY(BlueprintReadOnly, Category="NPCDialogue")
    FName EmotionalState = NAME_None;

    UPROPERTY(BlueprintReadOnly, Category="NPCDialogue")
    FName SourceContextId = NAME_None;

    UPROPERTY(BlueprintReadOnly, Category="NPCDialogue")
    FString SourceContextSummary;
};

UCLASS()
class SHIREJOURNEY_API UShireNPCContextSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    UFUNCTION(BlueprintPure, Category="NPCContext")
    bool IsDataReady() const { return bDataReady; }

    UFUNCTION(BlueprintPure, Category="NPCContext")
    FName ResolveCanonicalProfileId(FName IdAliasOrDisplayName) const;

    UFUNCTION(BlueprintPure, Category="NPCContext")
    FName GetPersistenceTier(FName ProfileHint) const;

    UFUNCTION(BlueprintPure, Category="NPCContext")
    int32 GetPersistentMemoryBudget(FName ProfileHint) const;

    UFUNCTION(BlueprintPure, Category="NPCContext")
    int32 GetRelationshipBudget(FName ProfileHint) const;

    UFUNCTION(BlueprintPure, Category="NPCContext")
    bool HasKnowledgeTag(FName ProfileHint, FName KnowledgeTag) const;

    UFUNCTION(BlueprintPure, Category="NPCContext")
    bool CanUseIntent(FName ProfileHint, FName IntentId) const;

    UFUNCTION(BlueprintPure, Category="NPCContext")
    FString GetProfileContextSummary(FName ProfileHint) const;

    UFUNCTION(BlueprintPure, Category="NPCContext")
    FName GetRegionalWorldMood() const;

    UFUNCTION(BlueprintPure, Category="NPCContext")
    float GetRegionalPressure() const;

    UFUNCTION(BlueprintPure, Category="NPCContext")
    FName GetProfileEmotionalState(FName ProfileHint) const;

    UFUNCTION(BlueprintPure, Category="NPCContext")
    FName GetFilmDialogueContextId() const;

    UFUNCTION(BlueprintPure, Category="NPCContext")
    FString GetFilmDialogueContextSummary() const;

    UFUNCTION(BlueprintPure, Category="NPCContext")
    FName ResolveSchedulePhase(FName ProfileHint, float NormalizedDay, bool bDangerOverride, bool bStoryOverride) const;

    UFUNCTION(BlueprintPure, Category="NPCContext")
    FName GetPreferredAnchor(FName ProfileHint, FName SchedulePhase) const;

    UFUNCTION(BlueprintPure, Category="NPCContext")
    TArray<FName> GetNamedProfilesForCurrentChapter() const;

    UFUNCTION(BlueprintCallable, Category="NPCDialogue")
    FShireBoundedDialogueResult SelectBoundedDialogue(
        FName SpeakerHint,
        FName ListenerHint,
        FName IntentId = NAME_None,
        FName LocationTag = NAME_None);

    UFUNCTION(BlueprintCallable, Category="NPCContext")
    void SetWeatherState(FName InWeatherState);

    UFUNCTION(BlueprintPure, Category="NPCContext")
    FName GetWeatherState() const { return WeatherState; }

    UFUNCTION(BlueprintPure, Category="NPCContext")
    bool IsDangerStateActive() const;

    UFUNCTION(BlueprintPure, Category="NPCContext")
    bool IsInclementWeather() const;

    // World-facing NPC context must follow the visible committed world, not logical
    // quest state that may already be pointing at an asynchronously loading destination.
    void SetCommittedWorldContext(
        FName ChapterId,
        FName RouteId,
        FName EpisodeId,
        uint32 WorldRevision,
        FName ActiveQuestId,
        int32 ActiveQuestStage);

    // Public read-only transaction query used by world-facing NPC consumers.
    UFUNCTION(BlueprintPure, Category="NPCContext")
    bool IsLogicalWorldContextCommitted() const;

private:
    struct FScheduleEntry
    {
        FName Phase = NAME_None;
        float Weight = 0.0f;
        FName AnchorPolicy = NAME_None;
    };

    struct FDialogueVariantRuntime
    {
        FName VariantId = NAME_None;
        FName SpeakerProfileId = NAME_None;
        FName IntentId = NAME_None;
        FString Text;
        FName VoiceCue = NAME_None;
        FName RequiredStoryBeat = NAME_None;
        FName RequiredMemory = NAME_None;
        FName RequiredMood = NAME_None;
        int32 MaxWords = 24;
    };

    struct FFilmDialogueContextRuntime
    {
        FName ContextId = NAME_None;
        FName SourceId = NAME_None;
        FName RouteId = NAME_None;
        FName ChapterId = NAME_None;
        FName RequiredStoryBeat = NAME_None;
        int32 Sequence = 0;
        FString SourceWindow;
        TArray<FName> ToneTags;
        TArray<FString> SafeTopics;
        TArray<FString> FutureKnowledgeBlocks;
    };

    UPROPERTY()
    TMap<FName, FShireNPCProfileRuntime> Profiles;

    TMap<FString, FName> CanonicalLookup;
    TMap<FName, TArray<FScheduleEntry>> ProfileSchedules;
    TMap<FName, TArray<FName>> IntentRequiredKnowledge;
    TMap<FName, TArray<FDialogueVariantRuntime>> DialogueVariants;
    TMap<FName, FName> ChapterMoodById;
    TMap<FName, float> ChapterPressureById;
    TMap<FName, TArray<FFilmDialogueContextRuntime>> FilmContextsByRouteChapter;

    bool bDataReady = false;
    bool bHasCommittedWorldContext = false;
    FName CommittedChapterId = NAME_None;
    FName CommittedRouteId = NAME_None;
    FName CommittedEpisodeId = NAME_None;
    FName CommittedActiveQuestId = NAME_None;
    int32 CommittedActiveQuestStage = 0;
    uint32 CommittedWorldRevision = 0;
    int32 MaxWordsAmbient = 24;
    int32 MaxWordsStoryReactive = 38;
    int32 MaxRecentLineIds = 12;
    FName WeatherState = TEXT("CLEAR");

    static FString NormalizeLookupKey(const FString& Value);
    static FName MakeDialogueKey(FName SpeakerProfileId, FName IntentId);
    static FName MakeFilmContextKey(FName RouteId, FName ChapterId);
    static void ParseNameArray(const TSharedPtr<class FJsonObject>& Object, const TCHAR* Field, TArray<FName>& OutNames);
    static void ParseStringArray(const TSharedPtr<class FJsonObject>& Object, const TCHAR* Field, TArray<FString>& OutStrings);
    bool LoadJsonObject(const FString& RelativePath, TSharedPtr<class FJsonObject>& OutRoot) const;
    bool LoadSocialModel();
    bool LoadConversationPlan();
    bool LoadBoundedDialoguePlan();
    bool LoadRegionalMoodPlan();
    bool LoadFilmDialogueSourceContext();
    void BuildDialogueVariantLibrary();
    void AddDialogueVariant(
        FName SpeakerProfileId,
        FName IntentId,
        FName VariantId,
        const TCHAR* Text,
        FName VoiceCue = NAME_None,
        FName RequiredStoryBeat = NAME_None,
        FName RequiredMemory = NAME_None,
        FName RequiredMood = NAME_None);
    FName GetContextChapterId() const;
    FName GetContextRouteId() const;
    FName GetContextActiveQuestId() const;
    int32 GetContextActiveQuestStage() const;
    bool ProfileAvailableInCurrentChapter(const FShireNPCProfileRuntime& Profile) const;
    bool IsFellowshipProfile(const FShireNPCProfileRuntime& Profile) const;
    const FFilmDialogueContextRuntime* GetActiveFilmDialogueContext() const;
    int32 CountWords(const FString& Text) const;
};
