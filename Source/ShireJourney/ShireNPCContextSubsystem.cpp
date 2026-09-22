#include "ShireNPCContextSubsystem.h"

#include "ShireQuestSubsystem.h"

#include "Dom/JsonObject.h"
#include "Engine/GameInstance.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"


namespace
{
    // Story/knowledge/memory eligibility is checked before ranking. Never select
    // another region's line merely because it is fresh in the repetition cache.
    int32 ShireDialogueContextRank(FName RequiredMood, FName CurrentMood, bool bSpecificMemory)
    {
        if (RequiredMood != NAME_None && RequiredMood != CurrentMood)
        {
            return -1;
        }
        return (RequiredMood != NAME_None ? 2 : 0) + (bSpecificMemory ? 1 : 0);
    }
}

FString UShireNPCContextSubsystem::NormalizeLookupKey(const FString& Value)
{
    FString Key = Value;
    Key.TrimStartAndEndInline();
    Key.ToLowerInline();
    return Key;
}

FName UShireNPCContextSubsystem::MakeDialogueKey(FName SpeakerProfileId, FName IntentId)
{
    return FName(*FString::Printf(TEXT("%s|%s"), *SpeakerProfileId.ToString(), *IntentId.ToString()));
}

FName UShireNPCContextSubsystem::MakeFilmContextKey(FName RouteId, FName ChapterId)
{
    return FName(*FString::Printf(TEXT("%s|%s"), *RouteId.ToString(), *ChapterId.ToString()));
}

void UShireNPCContextSubsystem::ParseNameArray(
    const TSharedPtr<FJsonObject>& Object,
    const TCHAR* Field,
    TArray<FName>& OutNames)
{
    OutNames.Empty();
    if (!Object.IsValid())
    {
        return;
    }

    const TArray<TSharedPtr<FJsonValue>>* Values = nullptr;
    if (!Object->TryGetArrayField(Field, Values) || !Values)
    {
        return;
    }

    for (const TSharedPtr<FJsonValue>& Value : *Values)
    {
        if (Value.IsValid())
        {
            const FString StringValue = Value->AsString();
            if (!StringValue.IsEmpty())
            {
                OutNames.Add(FName(*StringValue));
            }
        }
    }
}

void UShireNPCContextSubsystem::ParseStringArray(
    const TSharedPtr<FJsonObject>& Object,
    const TCHAR* Field,
    TArray<FString>& OutStrings)
{
    OutStrings.Empty();
    if (!Object.IsValid())
    {
        return;
    }

    const TArray<TSharedPtr<FJsonValue>>* Values = nullptr;
    if (!Object->TryGetArrayField(Field, Values) || !Values)
    {
        return;
    }

    for (const TSharedPtr<FJsonValue>& Value : *Values)
    {
        if (Value.IsValid())
        {
            FString StringValue = Value->AsString();
            StringValue.TrimStartAndEndInline();
            if (!StringValue.IsEmpty())
            {
                OutStrings.Add(StringValue);
            }
        }
    }
}

bool UShireNPCContextSubsystem::LoadJsonObject(
    const FString& RelativePath,
    TSharedPtr<FJsonObject>& OutRoot) const
{
    const FString FullPath = FPaths::Combine(FPaths::ProjectDir(), RelativePath);
    FString JsonText;
    if (!FFileHelper::LoadFileToString(JsonText, *FullPath))
    {
        UE_LOG(LogTemp, Error, TEXT("NPCContext: failed to read %s"), *FullPath);
        return false;
    }

    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonText);
    if (!FJsonSerializer::Deserialize(Reader, OutRoot) || !OutRoot.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("NPCContext: invalid JSON in %s"), *FullPath);
        return false;
    }
    return true;
}

void UShireNPCContextSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    Profiles.Empty();
    CanonicalLookup.Empty();
    ProfileSchedules.Empty();
    IntentRequiredKnowledge.Empty();
    DialogueVariants.Empty();
    ChapterMoodById.Empty();
    ChapterPressureById.Empty();
    FilmContextsByRouteChapter.Empty();
    bHasCommittedWorldContext = false;
    CommittedChapterId = NAME_None;
    CommittedRouteId = NAME_None;
    CommittedEpisodeId = NAME_None;
    CommittedActiveQuestId = NAME_None;
    CommittedActiveQuestStage = 0;
    CommittedWorldRevision = 0;

    const bool bSocialLoaded = LoadSocialModel();
    const bool bConversationLoaded = LoadConversationPlan();
    const bool bBoundedLoaded = LoadBoundedDialoguePlan();
    const bool bRegionalMoodLoaded = LoadRegionalMoodPlan();
    BuildDialogueVariantLibrary();
    const bool bFilmSourceLoaded = LoadFilmDialogueSourceContext();

    bDataReady = bSocialLoaded && bConversationLoaded && bBoundedLoaded &&
        bRegionalMoodLoaded && bFilmSourceLoaded && Profiles.Num() > 0;

    if (bDataReady)
    {
        UE_LOG(
            LogTemp,
            Display,
            TEXT("NPCContext: ready=yes profiles=%d scheduleBindings=%d intentContracts=%d dialogueKeys=%d filmContextKeys=%d"),
            Profiles.Num(),
            ProfileSchedules.Num(),
            IntentRequiredKnowledge.Num(),
            DialogueVariants.Num(),
            FilmContextsByRouteChapter.Num());
    }
    else
    {
        UE_LOG(
            LogTemp,
            Error,
            TEXT("NPCContext: ready=no profiles=%d scheduleBindings=%d intentContracts=%d dialogueKeys=%d filmContextKeys=%d"),
            Profiles.Num(),
            ProfileSchedules.Num(),
            IntentRequiredKnowledge.Num(),
            DialogueVariants.Num(),
            FilmContextsByRouteChapter.Num());
    }
}

void UShireNPCContextSubsystem::Deinitialize()
{
    Profiles.Empty();
    CanonicalLookup.Empty();
    ProfileSchedules.Empty();
    IntentRequiredKnowledge.Empty();
    DialogueVariants.Empty();
    ChapterMoodById.Empty();
    ChapterPressureById.Empty();
    FilmContextsByRouteChapter.Empty();
    bDataReady = false;
    Super::Deinitialize();
}

bool UShireNPCContextSubsystem::LoadSocialModel()
{
    TSharedPtr<FJsonObject> Root;
    if (!LoadJsonObject(TEXT("Data/NPCSocialModel.json"), Root))
    {
        return false;
    }

    const TArray<TSharedPtr<FJsonValue>>* ProfileValues = nullptr;
    if (!Root->TryGetArrayField(TEXT("profiles"), ProfileValues) || !ProfileValues)
    {
        return false;
    }

    for (const TSharedPtr<FJsonValue>& Value : *ProfileValues)
    {
        const TSharedPtr<FJsonObject> Object = Value.IsValid() ? Value->AsObject() : nullptr;
        if (!Object.IsValid())
        {
            continue;
        }

        FString IdString;
        FString DisplayName;
        FString TypeString;
        FString PersistenceTier;
        FString Community;
        FString Origin;
        FString Occupation;
        Object->TryGetStringField(TEXT("id"), IdString);
        Object->TryGetStringField(TEXT("display_name"), DisplayName);
        Object->TryGetStringField(TEXT("type"), TypeString);
        Object->TryGetStringField(TEXT("persistence_tier"), PersistenceTier);
        Object->TryGetStringField(TEXT("community"), Community);
        Object->TryGetStringField(TEXT("origin"), Origin);
        Object->TryGetStringField(TEXT("occupation"), Occupation);

        if (IdString.IsEmpty())
        {
            continue;
        }

        FShireNPCProfileRuntime Profile;
        Profile.ProfileId = FName(*IdString);
        Profile.DisplayName = DisplayName;
        Profile.ProfileType = FName(*TypeString);
        Profile.PersistenceTier = FName(*PersistenceTier);
        Profile.Community = FName(*Community);
        Profile.Origin = Origin;
        Profile.Occupation = Occupation;
        ParseNameArray(Object, TEXT("aliases"), Profile.Aliases);
        ParseNameArray(Object, TEXT("regions"), Profile.Regions);
        ParseNameArray(Object, TEXT("roles"), Profile.Roles);
        ParseNameArray(Object, TEXT("knowledge_tags"), Profile.KnowledgeTags);
        ParseNameArray(Object, TEXT("anchors"), Profile.Anchors);
        ParseNameArray(Object, TEXT("attitude_tags"), Profile.AttitudeTags);
        ParseStringArray(Object, TEXT("biography_facts"), Profile.BiographyFacts);
        ParseStringArray(Object, TEXT("knowledge_limits"), Profile.KnowledgeLimits);

        Profiles.Add(Profile.ProfileId, Profile);
        CanonicalLookup.Add(NormalizeLookupKey(IdString), Profile.ProfileId);
        if (!DisplayName.IsEmpty())
        {
            CanonicalLookup.Add(NormalizeLookupKey(DisplayName), Profile.ProfileId);
        }
        for (const FName Alias : Profile.Aliases)
        {
            CanonicalLookup.Add(NormalizeLookupKey(Alias.ToString()), Profile.ProfileId);
        }
    }

    const TArray<TSharedPtr<FJsonValue>>* ScheduleValues = nullptr;
    if (Root->TryGetArrayField(TEXT("schedule_templates"), ScheduleValues) && ScheduleValues)
    {
        for (const TSharedPtr<FJsonValue>& ScheduleValue : *ScheduleValues)
        {
            const TSharedPtr<FJsonObject> ScheduleObject =
                ScheduleValue.IsValid() ? ScheduleValue->AsObject() : nullptr;
            if (!ScheduleObject.IsValid())
            {
                continue;
            }

            TArray<FName> AppliesTo;
            ParseNameArray(ScheduleObject, TEXT("applies_to"), AppliesTo);

            TArray<FScheduleEntry> Entries;
            const TArray<TSharedPtr<FJsonValue>>* PhaseValues = nullptr;
            if (ScheduleObject->TryGetArrayField(TEXT("phases"), PhaseValues) && PhaseValues)
            {
                for (const TSharedPtr<FJsonValue>& PhaseValue : *PhaseValues)
                {
                    const TSharedPtr<FJsonObject> PhaseObject =
                        PhaseValue.IsValid() ? PhaseValue->AsObject() : nullptr;
                    if (!PhaseObject.IsValid())
                    {
                        continue;
                    }

                    FString PhaseString;
                    FString AnchorPolicy;
                    double Weight = 0.0;
                    PhaseObject->TryGetStringField(TEXT("phase"), PhaseString);
                    PhaseObject->TryGetStringField(TEXT("anchor_policy"), AnchorPolicy);
                    PhaseObject->TryGetNumberField(TEXT("weight"), Weight);

                    if (!PhaseString.IsEmpty() && Weight > 0.0)
                    {
                        FScheduleEntry Entry;
                        Entry.Phase = FName(*PhaseString);
                        Entry.Weight = static_cast<float>(Weight);
                        Entry.AnchorPolicy = FName(*AnchorPolicy);
                        Entries.Add(Entry);
                    }
                }
            }

            for (const FName ProfileId : AppliesTo)
            {
                ProfileSchedules.Add(ProfileId, Entries);
            }
        }
    }

    return Profiles.Num() > 0;
}

bool UShireNPCContextSubsystem::LoadConversationPlan()
{
    TSharedPtr<FJsonObject> Root;
    if (!LoadJsonObject(TEXT("Data/NPCConversationPlan.json"), Root))
    {
        return false;
    }

    const TArray<TSharedPtr<FJsonValue>>* IntentValues = nullptr;
    if (!Root->TryGetArrayField(TEXT("intent_contracts"), IntentValues) || !IntentValues)
    {
        return false;
    }

    for (const TSharedPtr<FJsonValue>& Value : *IntentValues)
    {
        const TSharedPtr<FJsonObject> Object = Value.IsValid() ? Value->AsObject() : nullptr;
        if (!Object.IsValid())
        {
            continue;
        }

        FString IdString;
        Object->TryGetStringField(TEXT("id"), IdString);
        if (IdString.IsEmpty())
        {
            continue;
        }

        TArray<FName> RequiredTags;
        ParseNameArray(Object, TEXT("required_knowledge_tags"), RequiredTags);
        IntentRequiredKnowledge.Add(FName(*IdString), RequiredTags);
    }

    return IntentRequiredKnowledge.Num() > 0;
}

bool UShireNPCContextSubsystem::LoadBoundedDialoguePlan()
{
    TSharedPtr<FJsonObject> Root;
    if (!LoadJsonObject(TEXT("Data/BoundedDialoguePlan.json"), Root))
    {
        return false;
    }

    const TSharedPtr<FJsonObject>* LimitsObject = nullptr;
    if (Root->TryGetObjectField(TEXT("limits"), LimitsObject) && LimitsObject && LimitsObject->IsValid())
    {
        double Value = 0.0;
        if ((*LimitsObject)->TryGetNumberField(TEXT("max_words_ambient_line"), Value))
        {
            MaxWordsAmbient = FMath::Max(8, static_cast<int32>(Value));
        }
        if ((*LimitsObject)->TryGetNumberField(TEXT("max_words_story_reactive_line"), Value))
        {
            MaxWordsStoryReactive = FMath::Max(MaxWordsAmbient, static_cast<int32>(Value));
        }
        if ((*LimitsObject)->TryGetNumberField(TEXT("max_recent_line_ids_for_repetition_guard"), Value))
        {
            MaxRecentLineIds = FMath::Clamp(static_cast<int32>(Value), 4, 24);
        }
    }

    return true;
}

bool UShireNPCContextSubsystem::LoadRegionalMoodPlan()
{
    TSharedPtr<FJsonObject> Root;
    if (!LoadJsonObject(TEXT("Data/NPCRegionalMoodPlan.json"), Root))
    {
        return false;
    }

    const TArray<TSharedPtr<FJsonValue>>* MoodValues = nullptr;
    if (!Root->TryGetArrayField(TEXT("chapter_moods"), MoodValues) || !MoodValues)
    {
        return false;
    }

    for (const TSharedPtr<FJsonValue>& Value : *MoodValues)
    {
        const TSharedPtr<FJsonObject> Object = Value.IsValid() ? Value->AsObject() : nullptr;
        if (!Object.IsValid())
        {
            continue;
        }

        FString ChapterString;
        FString MoodString;
        double Pressure = 0.0;
        Object->TryGetStringField(TEXT("chapter"), ChapterString);
        Object->TryGetStringField(TEXT("mood"), MoodString);
        Object->TryGetNumberField(TEXT("pressure"), Pressure);

        if (ChapterString.IsEmpty() || MoodString.IsEmpty())
        {
            continue;
        }

        const FName ChapterId(*ChapterString);
        ChapterMoodById.Add(ChapterId, FName(*MoodString));
        ChapterPressureById.Add(ChapterId, FMath::Clamp(static_cast<float>(Pressure), 0.0f, 1.0f));
    }

    return ChapterMoodById.Num() > 0;
}

bool UShireNPCContextSubsystem::LoadFilmDialogueSourceContext()
{
    TSharedPtr<FJsonObject> Root;
    if (!LoadJsonObject(TEXT("Data/FilmDialogueSourceContext.json"), Root)) return false;

    const TArray<TSharedPtr<FJsonValue>>* Values = nullptr;
    if (!Root->TryGetArrayField(TEXT("part1_contexts"), Values) || !Values) return false;

    for (const TSharedPtr<FJsonValue>& Value : *Values)
    {
        const TSharedPtr<FJsonObject> Object = Value.IsValid() ? Value->AsObject() : nullptr;
        if (!Object.IsValid()) continue;

        FString ContextId, SourceId, RouteId, ChapterId, BeatId, Window;
        double Sequence = 0.0;
        Object->TryGetStringField(TEXT("context_id"), ContextId);
        Object->TryGetStringField(TEXT("source_id"), SourceId);
        Object->TryGetStringField(TEXT("route"), RouteId);
        Object->TryGetStringField(TEXT("chapter"), ChapterId);
        Object->TryGetStringField(TEXT("required_story_beat"), BeatId);
        Object->TryGetStringField(TEXT("source_window"), Window);
        Object->TryGetNumberField(TEXT("sequence"), Sequence);
        if (ContextId.IsEmpty() || SourceId.IsEmpty() || RouteId.IsEmpty() || ChapterId.IsEmpty()) continue;

        FFilmDialogueContextRuntime Context;
        Context.ContextId = FName(*ContextId);
        Context.SourceId = FName(*SourceId);
        Context.RouteId = FName(*RouteId);
        Context.ChapterId = FName(*ChapterId);
        Context.RequiredStoryBeat = BeatId.IsEmpty() ? NAME_None : FName(*BeatId);
        Context.Sequence = static_cast<int32>(Sequence);
        Context.SourceWindow = Window;
        ParseNameArray(Object, TEXT("tone_tags"), Context.ToneTags);
        ParseStringArray(Object, TEXT("safe_topics"), Context.SafeTopics);
        ParseStringArray(Object, TEXT("future_knowledge_blocks"), Context.FutureKnowledgeBlocks);
        FilmContextsByRouteChapter.FindOrAdd(MakeFilmContextKey(Context.RouteId, Context.ChapterId)).Add(MoveTemp(Context));
    }

    for (TPair<FName, TArray<FFilmDialogueContextRuntime>>& Pair : FilmContextsByRouteChapter)
    {
        Pair.Value.Sort([](const FFilmDialogueContextRuntime& A, const FFilmDialogueContextRuntime& B)
        {
            return A.Sequence < B.Sequence;
        });
    }

    const TArray<TSharedPtr<FJsonValue>>* DialogueValues = nullptr;
    if (Root->TryGetArrayField(TEXT("original_dialogue_variants"), DialogueValues) && DialogueValues)
    {
        for (const TSharedPtr<FJsonValue>& Value : *DialogueValues)
        {
            const TSharedPtr<FJsonObject> Object = Value.IsValid() ? Value->AsObject() : nullptr;
            if (!Object.IsValid()) continue;

            FString VariantId, Speaker, Intent, Text, RequiredBeat, RequiredMood;
            Object->TryGetStringField(TEXT("variant_id"), VariantId);
            Object->TryGetStringField(TEXT("speaker"), Speaker);
            Object->TryGetStringField(TEXT("intent"), Intent);
            Object->TryGetStringField(TEXT("text"), Text);
            Object->TryGetStringField(TEXT("required_story_beat"), RequiredBeat);
            Object->TryGetStringField(TEXT("required_mood"), RequiredMood);

            if (VariantId.IsEmpty() || Speaker.IsEmpty() || Intent.IsEmpty() || Text.IsEmpty())
            {
                continue;
            }

            AddDialogueVariant(
                FName(*Speaker),
                FName(*Intent),
                FName(*VariantId),
                *Text,
                NAME_None,
                RequiredBeat.IsEmpty() ? NAME_None : FName(*RequiredBeat),
                NAME_None,
                RequiredMood.IsEmpty() ? NAME_None : FName(*RequiredMood));
        }
    }

    return FilmContextsByRouteChapter.Num() > 0;
}

void UShireNPCContextSubsystem::AddDialogueVariant(
    FName SpeakerProfileId,
    FName IntentId,
    FName VariantId,
    const TCHAR* Text,
    FName VoiceCue,
    FName RequiredStoryBeat,
    FName RequiredMemory,
    FName RequiredMood)
{
    FDialogueVariantRuntime Variant;
    Variant.SpeakerProfileId = SpeakerProfileId;
    Variant.IntentId = IntentId;
    Variant.VariantId = VariantId;
    Variant.Text = Text;
    Variant.VoiceCue = VoiceCue;
    Variant.RequiredStoryBeat = RequiredStoryBeat;
    Variant.RequiredMemory = RequiredMemory;
    Variant.RequiredMood = RequiredMood;
    Variant.MaxWords =
        IntentId == TEXT("STORY_REACTION") || IntentId == TEXT("DANGER_WARNING")
            ? MaxWordsStoryReactive
            : MaxWordsAmbient;
    DialogueVariants.FindOrAdd(MakeDialogueKey(SpeakerProfileId, IntentId)).Add(MoveTemp(Variant));
}

void UShireNPCContextSubsystem::BuildDialogueVariantLibrary()
{
    DialogueVariants.Empty();

    AddDialogueVariant(TEXT("NPC_SAM"), TEXT("COMPANION_BANTER"), TEXT("SAM_BANTER_01"),
        TEXT("I would rather have a quiet road, but I am glad none of us is walking it alone."),
        TEXT("VO_Banter_Sam_01"));
    AddDialogueVariant(TEXT("NPC_SAM"), TEXT("TRAVEL_COMMENT"), TEXT("SAM_TRAVEL_01"),
        TEXT("If we keep a steady pace, we can rest before the light goes."),
        TEXT("VO_Travel_Sam_01"));
    AddDialogueVariant(TEXT("NPC_SAM"), TEXT("STORY_REACTION"), TEXT("SAM_MEMORY_01"),
        TEXT("I remember what happened before. We should be more careful this time."),
        TEXT("VO_Memory_Sam_01"), NAME_None, TEXT("PLAYER_INTERACTED"));
    AddDialogueVariant(TEXT("NPC_SAM"), TEXT("DANGER_WARNING"), TEXT("SAM_DANGER_01"),
        TEXT("Stay close. Whatever is ahead, we face it together."),
        TEXT("VO_Danger_Sam_01"));

    AddDialogueVariant(TEXT("NPC_MERRY"), TEXT("COMPANION_BANTER"), TEXT("MERRY_BANTER_01"),
        TEXT("We have survived worse plans than this, though usually Pippin helped invent them."),
        TEXT("VO_Banter_Merry_01"));
    AddDialogueVariant(TEXT("NPC_MERRY"), TEXT("TRAVEL_COMMENT"), TEXT("MERRY_TRAVEL_01"),
        TEXT("The road is easier when someone remembers to look behind us."),
        TEXT("VO_Travel_Merry_01"));
    AddDialogueVariant(TEXT("NPC_MERRY"), TEXT("DANGER_WARNING"), TEXT("MERRY_DANGER_01"),
        TEXT("Something is wrong. Keep moving and do not spread out."),
        TEXT("VO_Danger_Merry_01"));

    AddDialogueVariant(TEXT("NPC_PIPPIN"), TEXT("COMPANION_BANTER"), TEXT("PIPPIN_BANTER_01"),
        TEXT("I was going to suggest a rest, but I can already hear the objections."),
        TEXT("VO_Banter_Pippin_01"));
    AddDialogueVariant(TEXT("NPC_PIPPIN"), TEXT("TRAVEL_COMMENT"), TEXT("PIPPIN_TRAVEL_01"),
        TEXT("I keep discovering new ways for a road to be uncomfortable."),
        TEXT("VO_Travel_Pippin_01"));
    AddDialogueVariant(TEXT("NPC_PIPPIN"), TEXT("DANGER_WARNING"), TEXT("PIPPIN_DANGER_01"),
        TEXT("I heard that too. Please tell me someone else heard it."),
        TEXT("VO_Danger_Pippin_01"));

    AddDialogueVariant(TEXT("NPC_ARAGORN"), TEXT("COMPANION_BANTER"), TEXT("ARAGORN_BANTER_01"),
        TEXT("Talk if it keeps your spirits up, but keep listening to the country around us."),
        TEXT("VO_Banter_Aragorn_01"));
    AddDialogueVariant(TEXT("NPC_ARAGORN"), TEXT("TRAVEL_COMMENT"), TEXT("ARAGORN_TRAVEL_01"),
        TEXT("The safest path is rarely the straightest one."),
        TEXT("VO_Travel_Aragorn_01"));
    AddDialogueVariant(TEXT("NPC_ARAGORN"), TEXT("DANGER_WARNING"), TEXT("ARAGORN_DANGER_01"),
        TEXT("Close ranks. We have been watched for too long."),
        TEXT("VO_Danger_Aragorn_01"));
    AddDialogueVariant(TEXT("NPC_ARAGORN"), TEXT("STORY_REACTION"), TEXT("ARAGORN_MORIA_01"),
        TEXT("We carry the loss with us, but the others still need a road forward."),
        TEXT("VO_Memory_Aragorn_01"), TEXT("MoriaEscape"));

    AddDialogueVariant(TEXT("NPC_BOROMIR"), TEXT("COMPANION_BANTER"), TEXT("BOROMIR_BANTER_01"),
        TEXT("A company travels better when everyone knows who is guarding which side."),
        TEXT("VO_Banter_Boromir_01"));
    AddDialogueVariant(TEXT("NPC_BOROMIR"), TEXT("TRAVEL_COMMENT"), TEXT("BOROMIR_TRAVEL_01"),
        TEXT("Open ground favors speed, but it also leaves us visible."),
        TEXT("VO_Travel_Boromir_01"));
    AddDialogueVariant(TEXT("NPC_BOROMIR"), TEXT("DANGER_WARNING"), TEXT("BOROMIR_DANGER_01"),
        TEXT("Weapons ready. Keep the hobbits behind the stronger line."),
        TEXT("VO_Danger_Boromir_01"));

    AddDialogueVariant(TEXT("NPC_LEGOLAS"), TEXT("COMPANION_BANTER"), TEXT("LEGOLAS_BANTER_01"),
        TEXT("Even loud companions can be useful if they make the forest less lonely."),
        TEXT("VO_Banter_Legolas_01"));
    AddDialogueVariant(TEXT("NPC_LEGOLAS"), TEXT("TRAVEL_COMMENT"), TEXT("LEGOLAS_TRAVEL_01"),
        TEXT("The wind is carrying sounds from farther away than usual."),
        TEXT("VO_Travel_Legolas_01"));
    AddDialogueVariant(TEXT("NPC_LEGOLAS"), TEXT("DANGER_WARNING"), TEXT("LEGOLAS_DANGER_01"),
        TEXT("Movement ahead. Not all of it belongs to animals."),
        TEXT("VO_Danger_Legolas_01"));

    AddDialogueVariant(TEXT("NPC_GIMLI"), TEXT("COMPANION_BANTER"), TEXT("GIMLI_BANTER_01"),
        TEXT("If the road insists on climbing, it could at least have the courtesy to become stone."),
        TEXT("VO_Banter_Gimli_01"));
    AddDialogueVariant(TEXT("NPC_GIMLI"), TEXT("TRAVEL_COMMENT"), TEXT("GIMLI_TRAVEL_01"),
        TEXT("There is good ground beneath this mud somewhere. I intend to find it."),
        TEXT("VO_Travel_Gimli_01"));
    AddDialogueVariant(TEXT("NPC_GIMLI"), TEXT("DANGER_WARNING"), TEXT("GIMLI_DANGER_01"),
        TEXT("Good. Let whatever follows us come close enough to regret it."),
        TEXT("VO_Danger_Gimli_01"));

    AddDialogueVariant(TEXT("NPC_GANDALF"), TEXT("COMPANION_BANTER"), TEXT("GANDALF_BANTER_01"),
        TEXT("A little conversation is harmless. Forgetting why we travel is not."),
        TEXT("VO_Banter_Gandalf_01"));
    AddDialogueVariant(TEXT("NPC_GANDALF"), TEXT("TRAVEL_COMMENT"), TEXT("GANDALF_TRAVEL_01"),
        TEXT("Keep moving. The road will offer answers only after it has asked for patience."),
        TEXT("VO_Travel_Gandalf_01"));
    AddDialogueVariant(TEXT("NPC_GANDALF"), TEXT("DANGER_WARNING"), TEXT("GANDALF_DANGER_01"),
        TEXT("Do not wait to understand every shadow before you move away from it."),
        TEXT("VO_Danger_Gandalf_01"));

    AddDialogueVariant(TEXT("NPC_BARLIMAN_BUTTERBUR"), TEXT("GREETING"), TEXT("BUTTERBUR_GREETING_01"),
        TEXT("Rooms are scarce tonight, but a quiet guest can still find a corner."),
        TEXT("VO_Greeting_Butterbur_01"));
    AddDialogueVariant(TEXT("NPC_BREE_GATEKEEPER"), TEXT("GREETING"), TEXT("GATEKEEPER_GREETING_01"),
        TEXT("State your business, keep the road clear, and there will be no trouble."),
        TEXT("VO_Greeting_Gatekeeper_01"));
    AddDialogueVariant(TEXT("NPC_HALDIR"), TEXT("GREETING"), TEXT("HALDIR_GREETING_01"),
        TEXT("Walk carefully beneath these trees. Every sound carries farther than you think."),
        TEXT("VO_Greeting_Haldir_01"));
    AddDialogueVariant(TEXT("NPC_GALADRIEL"), TEXT("STORY_REACTION"), TEXT("GALADRIEL_MEMORY_01"),
        TEXT("Memory can guide a choice, but it cannot make the choice for you."),
        TEXT("VO_Memory_Galadriel_01"), NAME_None, TEXT("PLAYER_INTERACTED"));

    AddDialogueVariant(TEXT("NPC_BILBO"), TEXT("GREETING"), TEXT("BILBO_GREETING_01"),
        TEXT("You have arrived at just the right moment, which usually means something unexpected is about to happen."),
        TEXT("VO_Greeting_Bilbo_01"));
    AddDialogueVariant(TEXT("NPC_BILBO"), TEXT("STORY_REACTION"), TEXT("BILBO_MEMORY_01"),
        TEXT("Some journeys begin long before anyone is willing to admit they have started."),
        TEXT("VO_Memory_Bilbo_01"), NAME_None, TEXT("PLAYER_INTERACTED"));

    AddDialogueVariant(TEXT("NPC_ARWEN"), TEXT("GREETING"), TEXT("ARWEN_GREETING_01"),
        TEXT("Rest while you can. The road ahead will ask more of you than the last one did."),
        TEXT("VO_Greeting_Arwen_01"));
    AddDialogueVariant(TEXT("NPC_ARWEN"), TEXT("STORY_REACTION"), TEXT("ARWEN_MEMORY_01"),
        TEXT("What you remember can steady you, if you do not let fear choose what it means."),
        TEXT("VO_Memory_Arwen_01"), NAME_None, TEXT("PLAYER_INTERACTED"));

    AddDialogueVariant(TEXT("NPC_ELROND"), TEXT("GREETING"), TEXT("ELROND_GREETING_01"),
        TEXT("There is safety here for a time, and work to be done before that time ends."),
        TEXT("VO_Greeting_Elrond_01"));
    AddDialogueVariant(TEXT("NPC_ELROND"), TEXT("STORY_REACTION"), TEXT("ELROND_MEMORY_01"),
        TEXT("A decision gains weight when its consequences are understood and accepted."),
        TEXT("VO_Memory_Elrond_01"), NAME_None, TEXT("PLAYER_INTERACTED"));

    AddDialogueVariant(TEXT("NPC_SARUMAN"), TEXT("GREETING"), TEXT("SARUMAN_GREETING_01"),
        TEXT("You mistake resistance for strength. It is often only delay wearing a proud face."),
        TEXT("VO_Greeting_Saruman_01"));
    AddDialogueVariant(TEXT("NPC_SARUMAN"), TEXT("STORY_REACTION"), TEXT("SARUMAN_MEMORY_01"),
        TEXT("Past choices are useful only to those willing to turn them into leverage."),
        TEXT("VO_Memory_Saruman_01"), NAME_None, TEXT("PLAYER_INTERACTED"));

    AddDialogueVariant(TEXT("NPC_HAMFAST_GAMGEE"), TEXT("GREETING"), TEXT("HAMFAST_GREETING_01"),
        TEXT("A garden tells you plenty, if you learn to notice what changed since yesterday."),
        TEXT("VO_Greeting_Hamfast_01"));
    AddDialogueVariant(TEXT("NPC_HAMFAST_GAMGEE"), TEXT("LOCAL_NEWS"), TEXT("HAMFAST_NEWS_01"),
        TEXT("More folk are taking the lane today. I would keep an eye on who comes back."),
        TEXT("VO_News_Hamfast_01"));

    AddDialogueVariant(TEXT("NPC_ROSIE_COTTON"), TEXT("GREETING"), TEXT("ROSIE_GREETING_01"),
        TEXT("If you are staying, make yourself useful. If you are leaving, at least eat first."),
        TEXT("VO_Greeting_Rosie_01"));
    AddDialogueVariant(TEXT("NPC_ROSIE_COTTON"), TEXT("LOCAL_NEWS"), TEXT("ROSIE_NEWS_01"),
        TEXT("Everyone hears something different, but they all agree the roads feel busier."),
        TEXT("VO_News_Rosie_01"));

    AddDialogueVariant(TEXT("NPC_FARMER_MAGGOT"), TEXT("GREETING"), TEXT("MAGGOT_GREETING_01"),
        TEXT("Keep to the path and leave the fields as you found them, and we will get along."),
        TEXT("VO_Greeting_Maggot_01"));
    AddDialogueVariant(TEXT("NPC_FARMER_MAGGOT"), TEXT("LOCAL_NEWS"), TEXT("MAGGOT_NEWS_01"),
        TEXT("Strangers have passed nearby. Quiet ones. That usually worries me more than loud ones."),
        TEXT("VO_News_Maggot_01"));

    AddDialogueVariant(TEXT("NPC_BARLIMAN_BUTTERBUR"), TEXT("LOCAL_NEWS"), TEXT("BUTTERBUR_NEWS_01"),
        TEXT("Half the room has a rumor and the other half has already improved it."),
        TEXT("VO_News_Butterbur_01"));
    AddDialogueVariant(TEXT("NPC_BREE_GATEKEEPER"), TEXT("DANGER_WARNING"), TEXT("GATEKEEPER_DANGER_01"),
        TEXT("Inside the gate, now. Questions can wait until the road is quiet again."),
        TEXT("VO_Danger_Gatekeeper_01"));

    AddDialogueVariant(TEXT("NPC_HALDIR"), TEXT("DANGER_WARNING"), TEXT("HALDIR_DANGER_01"),
        TEXT("Do not leave the marked way. The forest is already listening."),
        TEXT("VO_Danger_Haldir_01"));
    AddDialogueVariant(TEXT("NPC_GALADRIEL"), TEXT("GREETING"), TEXT("GALADRIEL_GREETING_01"),
        TEXT("You have carried much farther than distance alone can measure."),
        TEXT("VO_Greeting_Galadriel_01"));
    // Contextual companion lines remain offline and reuse existing knowledge,
    // chapter, memory and repetition gates. No unrecorded voice assets are referenced.
    struct FRegionalLinePair
    {
        const TCHAR* Speaker;
        const TCHAR* Mood;
        const TCHAR* First;
        const TCHAR* Second;
    };
    const FRegionalLinePair RegionalLines[] = {
        { TEXT("NPC_SAM"), TEXT("DEAD_CITY_DREAD"), TEXT("Stay near me. I cannot see far enough to like this place."), TEXT("I will keep watch while you catch your breath.") },
        { TEXT("NPC_MERRY"), TEXT("DEAD_CITY_DREAD"), TEXT("Keep your steps quiet. Every sound seems to come back twice."), TEXT("Let us count heads before we take another turning.") },
        { TEXT("NPC_PIPPIN"), TEXT("DEAD_CITY_DREAD"), TEXT("I will be quiet. I would rather not find out what heard us."), TEXT("Could we stay where we can still see each other?") },
        { TEXT("NPC_ARAGORN"), TEXT("DEAD_CITY_DREAD"), TEXT("Watch the passage behind us. Darkness can conceal more than distance."), TEXT("Stay together and leave room for the others to move.") },
        { TEXT("NPC_BOROMIR"), TEXT("DEAD_CITY_DREAD"), TEXT("Keep the smaller ones inside our line. I will watch the rear."), TEXT("If something moves, warn the company before you draw it closer.") },
        { TEXT("NPC_LEGOLAS"), TEXT("DEAD_CITY_DREAD"), TEXT("Listen before you step. The stone carries sounds we cannot yet place."), TEXT("There is too little light ahead. Move carefully.") },
        { TEXT("NPC_GIMLI"), TEXT("DEAD_CITY_DREAD"), TEXT("These halls deserved voices and lamplight. Tread with respect."), TEXT("Good stone endures, but I do not trust every shadow beneath it.") },
        { TEXT("NPC_GANDALF"), TEXT("DEAD_CITY_DREAD"), TEXT("Patience. A wrong turning here could cost us dearly."), TEXT("Keep close, and let me study the way ahead.") },
        { TEXT("NPC_SAM"), TEXT("GRIEF_AND_REFUGE"), TEXT("You need not find words. I can sit here with you."), TEXT("Rest a little. I will be close when you are ready.") },
        { TEXT("NPC_MERRY"), TEXT("GRIEF_AND_REFUGE"), TEXT("It is quiet here. For once, I am grateful for that."), TEXT("We can take a little time together before we move on.") },
        { TEXT("NPC_PIPPIN"), TEXT("GRIEF_AND_REFUGE"), TEXT("I do not feel much like talking. May I stay beside you?"), TEXT("I thought finding shelter would make everything feel easier.") },
        { TEXT("NPC_ARAGORN"), TEXT("GRIEF_AND_REFUGE"), TEXT("Take the rest this place offers. We need not speak yet."), TEXT("Let the company gather itself before the next road.") },
        { TEXT("NPC_BOROMIR"), TEXT("GRIEF_AND_REFUGE"), TEXT("There is no shame in needing rest. Even a guard must breathe."), TEXT("I will keep my voice down. The others need their peace.") },
        { TEXT("NPC_LEGOLAS"), TEXT("GRIEF_AND_REFUGE"), TEXT("Let the leaves speak for a while. We have carried enough noise."), TEXT("There is room for silence beneath these trees.") },
        { TEXT("NPC_GIMLI"), TEXT("GRIEF_AND_REFUGE"), TEXT("I have no fine words for this. You still have my company."), TEXT("Let us rest our feet. Our thoughts may take longer.") },

        { TEXT("NPC_SAM"), TEXT("PEACEFUL_HOME"), TEXT("The lane feels easy today. I hope it stays that way."), TEXT("There is still time for a quiet walk before supper.") },
        { TEXT("NPC_MERRY"), TEXT("PEACEFUL_HOME"), TEXT("If nothing goes wrong, we may have to invent our own excitement."), TEXT("The Shire is best when nobody is in a hurry.") },
        { TEXT("NPC_PIPPIN"), TEXT("PEACEFUL_HOME"), TEXT("I was promised food somewhere nearby, and I intend to find it."), TEXT("It is hard to worry when the whole place smells like supper.") },
        { TEXT("NPC_BILBO"), TEXT("PEACEFUL_HOME"), TEXT("A peaceful road can still hide a good story if you look closely."), TEXT("Home is comfortable, but curiosity never stays quiet for long.") },

        { TEXT("NPC_SAM"), TEXT("SUSPICIOUS_TOWN"), TEXT("Too many eyes in this town. I would rather keep you close."), TEXT("This place feels crowded even when the street is empty.") },
        { TEXT("NPC_MERRY"), TEXT("SUSPICIOUS_TOWN"), TEXT("Let us hear the room before we decide who sounds friendly."), TEXT("A closed door can be sensible when strangers keep asking questions.") },
        { TEXT("NPC_PIPPIN"), TEXT("SUSPICIOUS_TOWN"), TEXT("I liked the Shire better when every face had a name."), TEXT("I will try not to attract attention. Try is the important word.") },
        { TEXT("NPC_ARAGORN"), TEXT("SUSPICIOUS_TOWN"), TEXT("Keep your voices low until we leave these streets."), TEXT("Bree is safer than the wild, not safer than carelessness.") },

        { TEXT("NPC_SAM"), TEXT("PURSUED_WILDERNESS"), TEXT("Do not fall behind. If you stop, I stop with you."), TEXT("Every ridge looks harmless until something moves behind it.") },
        { TEXT("NPC_MERRY"), TEXT("PURSUED_WILDERNESS"), TEXT("Cross open ground quickly and rest where the land hides us."), TEXT("I keep counting footsteps that are not ours.") },
        { TEXT("NPC_PIPPIN"), TEXT("PURSUED_WILDERNESS"), TEXT("I am trying not to look behind us every ten steps."), TEXT("If we find cover, I vote we breathe there for a minute.") },
        { TEXT("NPC_ARAGORN"), TEXT("PURSUED_WILDERNESS"), TEXT("Read the ground before the horizon. Tracks tell you what distance hides."), TEXT("Stay off the obvious line. We are not the only ones here.") },

        { TEXT("NPC_GANDALF"), TEXT("SAFE_REFUGE"), TEXT("Rest is part of the journey. Use it before the road asks more."), TEXT("Safety gives us time to think, not permission to forget danger.") },
        { TEXT("NPC_BILBO"), TEXT("SAFE_REFUGE"), TEXT("A quiet room after a long road can feel like its own adventure."), TEXT("Sit a while. Stories sound different when nobody is chasing you.") },
        { TEXT("NPC_ARWEN"), TEXT("SAFE_REFUGE"), TEXT("You are safe enough to breathe here. Let that be enough for now."), TEXT("Healing is not idleness. The road can wait while strength returns.") },
        { TEXT("NPC_ELROND"), TEXT("SAFE_REFUGE"), TEXT("Use this refuge to see the choice clearly before movement begins again."), TEXT("Peace here is temporary, but clarity need not be.") },

        { TEXT("NPC_GANDALF"), TEXT("FELLOWSHIP_UNDER_PRESSURE"), TEXT("Keep your purpose in sight when the road becomes louder than thought."), TEXT("Pressure reveals weak choices quickly. We will choose carefully.") },
        { TEXT("NPC_SAM"), TEXT("FELLOWSHIP_UNDER_PRESSURE"), TEXT("Whatever the mountain does, you are not facing it alone."), TEXT("Cold is easier to bear when we keep moving together.") },
        { TEXT("NPC_ARAGORN"), TEXT("FELLOWSHIP_UNDER_PRESSURE"), TEXT("Close the gaps. Weather can separate us as easily as an enemy."), TEXT("Watch the footing and the company at the same time.") },
        { TEXT("NPC_GIMLI"), TEXT("FELLOWSHIP_UNDER_PRESSURE"), TEXT("Stone I understand. Snow pretending to be stone is another matter."), TEXT("There are roads beneath mountains as well as over them.") },

        { TEXT("NPC_SAM"), TEXT("FELLOWSHIP_FRACTURE"), TEXT("Something is wrong among us. I am staying where I can see you."), TEXT("The river is quiet, but the company is not.") },
        { TEXT("NPC_ARAGORN"), TEXT("FELLOWSHIP_FRACTURE"), TEXT("Keep the company in sight. Tension can scatter us before danger arrives."), TEXT("We need clear heads now more than quick feet.") },
        { TEXT("NPC_BOROMIR"), TEXT("FELLOWSHIP_FRACTURE"), TEXT("Every choice feels heavier here. I need a moment to think clearly."), TEXT("Do not mistake silence for peace. There is too much at stake.") },
        { TEXT("NPC_LEGOLAS"), TEXT("FELLOWSHIP_FRACTURE"), TEXT("The woods warn of movement, and the company is already unsettled."), TEXT("We should not remain divided while danger closes around us.") },

        { TEXT("NPC_GANDALF"), TEXT("WAR_CORRUPTION"), TEXT("This place no longer feels like counsel. It feels like a trap."), TEXT("Power without restraint has changed the air here.") },
        { TEXT("NPC_SARUMAN"), TEXT("WAR_CORRUPTION"), TEXT("The old balance is finished. Only those who adapt will shape what follows."), TEXT("Warning cannot reverse what is already in motion.") },
    };
    const FName RegionalIntents[] = {
        TEXT("GREETING"), TEXT("STORY_REACTION"),
        TEXT("COMPANION_BANTER"), TEXT("TRAVEL_COMMENT")
    };
    for (const FRegionalLinePair& Pair : RegionalLines)
    {
        for (FName Intent : RegionalIntents)
        {
            const FName FirstId(*FString::Printf(TEXT("%s_%s_%s_01"), Pair.Speaker, Pair.Mood, *Intent.ToString()));
            const FName SecondId(*FString::Printf(TEXT("%s_%s_%s_02"), Pair.Speaker, Pair.Mood, *Intent.ToString()));
            AddDialogueVariant(Pair.Speaker, Intent, FirstId, Pair.First, NAME_None, NAME_None, NAME_None, Pair.Mood);
            AddDialogueVariant(Pair.Speaker, Intent, SecondId, Pair.Second, NAME_None, NAME_None, NAME_None, Pair.Mood);
        }
    }

}

FName UShireNPCContextSubsystem::ResolveCanonicalProfileId(FName IdAliasOrDisplayName) const
{
    if (IdAliasOrDisplayName == NAME_None)
    {
        return NAME_None;
    }

    if (Profiles.Contains(IdAliasOrDisplayName))
    {
        return IdAliasOrDisplayName;
    }

    const FString Key = NormalizeLookupKey(IdAliasOrDisplayName.ToString());
    if (const FName* Found = CanonicalLookup.Find(Key))
    {
        return *Found;
    }
    return NAME_None;
}

FName UShireNPCContextSubsystem::GetPersistenceTier(FName ProfileHint) const
{
    const FName ProfileId = ResolveCanonicalProfileId(ProfileHint);
    if (const FShireNPCProfileRuntime* Profile = Profiles.Find(ProfileId))
    {
        return Profile->PersistenceTier;
    }
    return NAME_None;
}

int32 UShireNPCContextSubsystem::GetPersistentMemoryBudget(FName ProfileHint) const
{
    const FName Tier = GetPersistenceTier(ProfileHint);
    if (Tier == TEXT("NAMED_STORY"))
    {
        return 12;
    }
    if (Tier == TEXT("NAMED_LIGHT"))
    {
        return 4;
    }
    return 0;
}

int32 UShireNPCContextSubsystem::GetRelationshipBudget(FName ProfileHint) const
{
    const FName Tier = GetPersistenceTier(ProfileHint);
    if (Tier == TEXT("NAMED_STORY"))
    {
        return 8;
    }
    if (Tier == TEXT("NAMED_LIGHT"))
    {
        return 3;
    }
    return 0;
}

bool UShireNPCContextSubsystem::HasKnowledgeTag(FName ProfileHint, FName KnowledgeTag) const
{
    const FName ProfileId = ResolveCanonicalProfileId(ProfileHint);
    const FShireNPCProfileRuntime* Profile = Profiles.Find(ProfileId);
    return Profile && KnowledgeTag != NAME_None && Profile->KnowledgeTags.Contains(KnowledgeTag);
}

bool UShireNPCContextSubsystem::CanUseIntent(FName ProfileHint, FName IntentId) const
{
    const FName ProfileId = ResolveCanonicalProfileId(ProfileHint);
    const FShireNPCProfileRuntime* Profile = Profiles.Find(ProfileId);
    if (!Profile || IntentId == NAME_None)
    {
        return false;
    }

    const TArray<FName>* RequiredTags = IntentRequiredKnowledge.Find(IntentId);
    if (!RequiredTags)
    {
        return false;
    }

    for (const FName RequiredTag : *RequiredTags)
    {
        if (!Profile->KnowledgeTags.Contains(RequiredTag))
        {
            return false;
        }
    }
    return true;
}

void UShireNPCContextSubsystem::SetCommittedWorldContext(
    FName ChapterId,
    FName RouteId,
    FName EpisodeId,
    uint32 WorldRevision,
    FName ActiveQuestId,
    int32 ActiveQuestStage)
{
    if (ChapterId.IsNone() || RouteId.IsNone() || EpisodeId.IsNone() || WorldRevision == 0)
    {
        return;
    }

    CommittedChapterId = ChapterId;
    CommittedRouteId = RouteId;
    CommittedEpisodeId = EpisodeId;
    CommittedActiveQuestId = ActiveQuestId;
    CommittedActiveQuestStage = FMath::Max(0, ActiveQuestStage);
    CommittedWorldRevision = WorldRevision;
    bHasCommittedWorldContext = true;

    UE_LOG(
        LogTemp,
        Display,
        TEXT("NPCContextCommit: chapter=%s route=%s episode=%s quest=%s stage=%d revision=%u"),
        *CommittedChapterId.ToString(),
        *CommittedRouteId.ToString(),
        *CommittedEpisodeId.ToString(),
        *CommittedActiveQuestId.ToString(),
        CommittedActiveQuestStage,
        CommittedWorldRevision);
}

FName UShireNPCContextSubsystem::GetContextChapterId() const
{
    if (bHasCommittedWorldContext)
    {
        return CommittedChapterId;
    }
    const UGameInstance* GI = GetGameInstance();
    const UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    return Quests ? Quests->GetCurrentChapterId() : NAME_None;
}

FName UShireNPCContextSubsystem::GetContextRouteId() const
{
    if (bHasCommittedWorldContext)
    {
        return CommittedRouteId;
    }
    const UGameInstance* GI = GetGameInstance();
    const UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    return Quests ? Quests->GetCurrentRouteId() : NAME_None;
}

FName UShireNPCContextSubsystem::GetContextActiveQuestId() const
{
    if (bHasCommittedWorldContext)
    {
        return CommittedActiveQuestId;
    }
    const UGameInstance* GI = GetGameInstance();
    const UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    return Quests ? Quests->GetActiveQuestId() : NAME_None;
}

int32 UShireNPCContextSubsystem::GetContextActiveQuestStage() const
{
    if (bHasCommittedWorldContext)
    {
        return CommittedActiveQuestStage;
    }
    const UGameInstance* GI = GetGameInstance();
    const UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    return Quests ? Quests->GetActiveQuestStage() : 0;
}

bool UShireNPCContextSubsystem::IsFellowshipProfile(const FShireNPCProfileRuntime& Profile) const
{
    return Profile.Roles.Contains(TEXT("FELLOWSHIP_MEMBER"));
}

bool UShireNPCContextSubsystem::ProfileAvailableInCurrentChapter(
    const FShireNPCProfileRuntime& Profile) const
{
    const UGameInstance* GI = GetGameInstance();
    const UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!Quests)
    {
        return true;
    }

    FName Region = GetContextChapterId();
    if (GetContextRouteId() == TEXT("GandalfParallel"))
    {
        Region = TEXT("P1G01");
    }

    return Profile.Regions.Num() == 0 || Profile.Regions.Contains(Region);
}

FString UShireNPCContextSubsystem::GetProfileContextSummary(FName ProfileHint) const
{
    const FName ProfileId = ResolveCanonicalProfileId(ProfileHint);
    const FShireNPCProfileRuntime* Profile = Profiles.Find(ProfileId);
    if (!Profile)
    {
        return FString();
    }

    TArray<FString> Parts;
    Parts.Add(FString::Printf(TEXT("id=%s"), *Profile->ProfileId.ToString()));
    if (!Profile->DisplayName.IsEmpty()) Parts.Add(FString::Printf(TEXT("name=%s"), *Profile->DisplayName));
    if (!Profile->Origin.IsEmpty()) Parts.Add(FString::Printf(TEXT("origin=%s"), *Profile->Origin));
    if (!Profile->Occupation.IsEmpty()) Parts.Add(FString::Printf(TEXT("occupation=%s"), *Profile->Occupation));

    if (Profile->BiographyFacts.Num() > 0)
    {
        Parts.Add(FString::Printf(TEXT("history=%s"), *FString::Join(Profile->BiographyFacts, TEXT(" | "))));
    }
    if (Profile->KnowledgeLimits.Num() > 0)
    {
        Parts.Add(FString::Printf(TEXT("limits=%s"), *FString::Join(Profile->KnowledgeLimits, TEXT(" | "))));
    }

    TArray<FString> Attitudes;
    for (const FName Tag : Profile->AttitudeTags)
    {
        Attitudes.Add(Tag.ToString());
    }
    if (Attitudes.Num() > 0)
    {
        Parts.Add(FString::Printf(TEXT("attitudes=%s"), *FString::Join(Attitudes, TEXT(","))));
    }

    Parts.Add(FString::Printf(TEXT("world_mood=%s"), *GetRegionalWorldMood().ToString()));
    Parts.Add(FString::Printf(TEXT("world_pressure=%.2f"), GetRegionalPressure()));
    Parts.Add(FString::Printf(TEXT("emotion=%s"), *GetProfileEmotionalState(ProfileId).ToString()));
    const FString FilmContext = GetFilmDialogueContextSummary();
    if (!FilmContext.IsEmpty()) Parts.Add(FString::Printf(TEXT("film_context=%s"), *FilmContext));
    if (IsDangerStateActive())
    {
        Parts.Add(TEXT("danger=ACTIVE"));
    }
    if (IsInclementWeather())
    {
        Parts.Add(FString::Printf(TEXT("weather=%s"), *WeatherState.ToString()));
    }

    return FString::Join(Parts, TEXT("; "));
}

FName UShireNPCContextSubsystem::GetRegionalWorldMood() const
{
    const UGameInstance* GI = GetGameInstance();
    const UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!Quests)
    {
        return TEXT("CALM_TRAVEL");
    }

    FName ChapterId = GetContextChapterId();
    if (GetContextRouteId() == TEXT("GandalfParallel"))
    {
        ChapterId = TEXT("P1G01");
    }

    if (const FName* Mood = ChapterMoodById.Find(ChapterId))
    {
        return *Mood;
    }
    return TEXT("CALM_TRAVEL");
}

float UShireNPCContextSubsystem::GetRegionalPressure() const
{
    const UGameInstance* GI = GetGameInstance();
    const UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!Quests)
    {
        return 0.25f;
    }

    FName ChapterId = GetContextChapterId();
    if (GetContextRouteId() == TEXT("GandalfParallel"))
    {
        ChapterId = TEXT("P1G01");
    }

    float Pressure = 0.25f;
    if (const float* Found = ChapterPressureById.Find(ChapterId))
    {
        Pressure = *Found;
    }
    if (IsDangerStateActive())
    {
        Pressure = FMath::Max(Pressure, 0.90f);
    }
    return FMath::Clamp(Pressure, 0.0f, 1.0f);
}

FName UShireNPCContextSubsystem::GetProfileEmotionalState(FName ProfileHint) const
{
    const FName ProfileId = ResolveCanonicalProfileId(ProfileHint);
    const FShireNPCProfileRuntime* Profile = Profiles.Find(ProfileId);
    if (!Profile)
    {
        return TEXT("CALM");
    }

    const FName Mood = GetRegionalWorldMood();
    if (Mood == TEXT("PEACEFUL_HOME")) return TEXT("RELAXED");
    if (Mood == TEXT("SUSPICIOUS_TOWN")) return TEXT("WATCHFUL");
    if (Mood == TEXT("SAFE_REFUGE")) return TEXT("RELIEVED");
    if (Mood == TEXT("GRIEF_AND_REFUGE")) return TEXT("GRIEVING");
    if (Mood == TEXT("PURSUED_WILDERNESS")) return TEXT("TENSE");
    if (Mood == TEXT("FELLOWSHIP_UNDER_PRESSURE")) return TEXT("DETERMINED");
    if (Mood == TEXT("FELLOWSHIP_FRACTURE"))
    {
        return ProfileId == TEXT("NPC_BOROMIR") ? FName(TEXT("CONFLICTED")) : FName(TEXT("ALARMED"));
    }
    if (Mood == TEXT("WAR_CORRUPTION"))
    {
        return ProfileId == TEXT("NPC_SARUMAN") ? FName(TEXT("HOSTILE")) : FName(TEXT("RESOLUTE"));
    }
    if (Mood == TEXT("DEAD_CITY_DREAD"))
    {
        if (ProfileId == TEXT("NPC_GIMLI")) return TEXT("GRIEVING");
        return Profile->AttitudeTags.Contains(FName(TEXT("PROTECTIVE")))
            ? FName(TEXT("GRAVE"))
            : FName(TEXT("AFRAID"));
    }

    return GetRegionalPressure() >= 0.75f ? FName(TEXT("ALERT")) : FName(TEXT("CALM"));
}

const UShireNPCContextSubsystem::FFilmDialogueContextRuntime*
UShireNPCContextSubsystem::GetActiveFilmDialogueContext() const
{
    const UGameInstance* GI = GetGameInstance();
    const UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!Quests) return nullptr;

    const FName ContextRouteId = GetContextRouteId();
    const FName ContextChapterId = GetContextChapterId();
    const TArray<FFilmDialogueContextRuntime>* Contexts =
        FilmContextsByRouteChapter.Find(MakeFilmContextKey(ContextRouteId, ContextChapterId));
    if (!Contexts) return nullptr;

    const FFilmDialogueContextRuntime* Best = nullptr;
    for (const FFilmDialogueContextRuntime& Context : *Contexts)
    {
        if (Context.RequiredStoryBeat != NAME_None && !Quests->HasStoryBeatTriggered(Context.RequiredStoryBeat)) continue;
        if (!Best || Context.Sequence >= Best->Sequence) Best = &Context;
    }
    return Best;
}

FName UShireNPCContextSubsystem::GetFilmDialogueContextId() const
{
    const FFilmDialogueContextRuntime* Context = GetActiveFilmDialogueContext();
    return Context ? Context->ContextId : NAME_None;
}

FString UShireNPCContextSubsystem::GetFilmDialogueContextSummary() const
{
    const FFilmDialogueContextRuntime* Context = GetActiveFilmDialogueContext();
    if (!Context) return FString();

    TArray<FString> Tone;
    for (const FName Tag : Context->ToneTags) Tone.Add(Tag.ToString());

    TArray<FString> Parts;
    Parts.Add(FString::Printf(TEXT("id=%s"), *Context->ContextId.ToString()));
    Parts.Add(FString::Printf(TEXT("source=%s"), *Context->SourceId.ToString()));
    if (Tone.Num() > 0) Parts.Add(FString::Printf(TEXT("tone=%s"), *FString::Join(Tone, TEXT(","))));
    if (Context->SafeTopics.Num() > 0) Parts.Add(FString::Printf(TEXT("topics=%s"), *FString::Join(Context->SafeTopics, TEXT(" | "))));
    if (Context->FutureKnowledgeBlocks.Num() > 0) Parts.Add(FString::Printf(TEXT("future_blocks=%s"), *FString::Join(Context->FutureKnowledgeBlocks, TEXT(" | "))));
    return FString::Join(Parts, TEXT("; "));
}

FName UShireNPCContextSubsystem::ResolveSchedulePhase(
    FName ProfileHint,
    float NormalizedDay,
    bool bDangerOverride,
    bool bStoryOverride) const
{
    const FName ProfileId = ResolveCanonicalProfileId(ProfileHint);
    if (ProfileId == NAME_None)
    {
        return NAME_None;
    }

    if (bDangerOverride)
    {
        return TEXT("DANGER_OVERRIDE");
    }
    if (bStoryOverride)
    {
        return TEXT("STORY_OVERRIDE");
    }

    const TArray<FScheduleEntry>* Entries = ProfileSchedules.Find(ProfileId);
    if (!Entries || Entries->Num() == 0)
    {
        return TEXT("STORY_OVERRIDE");
    }

    const float T = FMath::Frac(FMath::Max(0.0f, NormalizedDay));
    float TotalWeight = 0.0f;
    for (const FScheduleEntry& Entry : *Entries)
    {
        TotalWeight += FMath::Max(0.0f, Entry.Weight);
    }
    if (TotalWeight <= KINDA_SMALL_NUMBER)
    {
        return Entries->Last().Phase;
    }

    const float Target = T * TotalWeight;
    float Cursor = 0.0f;
    for (const FScheduleEntry& Entry : *Entries)
    {
        Cursor += FMath::Max(0.0f, Entry.Weight);
        if (Target <= Cursor)
        {
            return Entry.Phase;
        }
    }
    return Entries->Last().Phase;
}

FName UShireNPCContextSubsystem::GetPreferredAnchor(FName ProfileHint, FName SchedulePhase) const
{
    const FName ProfileId = ResolveCanonicalProfileId(ProfileHint);
    const FShireNPCProfileRuntime* Profile = Profiles.Find(ProfileId);
    if (!Profile)
    {
        return NAME_None;
    }

    if (const TArray<FScheduleEntry>* Entries = ProfileSchedules.Find(ProfileId))
    {
        for (const FScheduleEntry& Entry : *Entries)
        {
            if (Entry.Phase == SchedulePhase && Entry.AnchorPolicy != NAME_None)
            {
                if (Entry.AnchorPolicy == TEXT("PROFILE_ANCHOR") && Profile->Anchors.Num() > 0)
                {
                    return Profile->Anchors[0];
                }
                return Entry.AnchorPolicy;
            }
        }
    }

    return Profile->Anchors.Num() > 0 ? Profile->Anchors[0] : NAME_None;
}

TArray<FName> UShireNPCContextSubsystem::GetNamedProfilesForCurrentChapter() const
{
    TArray<FName> Result;
    for (const TPair<FName, FShireNPCProfileRuntime>& Pair : Profiles)
    {
        if (Pair.Value.ProfileType == TEXT("NAMED") && ProfileAvailableInCurrentChapter(Pair.Value))
        {
            Result.Add(Pair.Key);
        }
    }
    Result.Sort([](const FName& A, const FName& B)
    {
        return A.LexicalLess(B);
    });
    return Result;
}

int32 UShireNPCContextSubsystem::CountWords(const FString& Text) const
{
    TArray<FString> Words;
    Text.ParseIntoArrayWS(Words);
    return Words.Num();
}

bool UShireNPCContextSubsystem::IsDangerStateActive() const
{
    const UGameInstance* GI = GetGameInstance();
    const UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!Quests)
    {
        return false;
    }

    const FName Quest = GetContextActiveQuestId();
    const int32 Stage = GetContextActiveQuestStage();

    if (Quest == TEXT("KeepOffRoad") || Quest == TEXT("NightAttack") ||
        Quest == TEXT("WeathertopAttack") || Quest == TEXT("BridgeOfKhazadDum") ||
        Quest == TEXT("BreakingFellowship"))
    {
        return true;
    }
    return Quest == TEXT("BalinsTomb") && Stage >= 3;
}

bool UShireNPCContextSubsystem::IsInclementWeather() const
{
    return WeatherState == TEXT("RAIN") || WeatherState == TEXT("STORM") ||
        WeatherState == TEXT("SNOW") || WeatherState == TEXT("HEAVY_RAIN");
}

void UShireNPCContextSubsystem::SetWeatherState(FName InWeatherState)
{
    WeatherState = InWeatherState == NAME_None ? FName(TEXT("CLEAR")) : InWeatherState;
}

FShireBoundedDialogueResult UShireNPCContextSubsystem::SelectBoundedDialogue(
    FName SpeakerHint,
    FName ListenerHint,
    FName IntentId,
    FName LocationTag)
{
    FShireBoundedDialogueResult Result;
    const FName SpeakerId = ResolveCanonicalProfileId(SpeakerHint);
    FName ListenerId = ResolveCanonicalProfileId(ListenerHint);
    if (ListenerId == NAME_None && ListenerHint == TEXT("PLAYER_FRODO"))
    {
        ListenerId = TEXT("PLAYER_FRODO");
    }

    const FShireNPCProfileRuntime* Speaker = Profiles.Find(SpeakerId);
    if (!Speaker || !ProfileAvailableInCurrentChapter(*Speaker))
    {
        return Result;
    }

    if (IntentId == NAME_None)
    {
        const FShireNPCProfileRuntime* Listener = Profiles.Find(ListenerId);
        IntentId = Listener && IsFellowshipProfile(*Speaker) && IsFellowshipProfile(*Listener)
            ? FName(TEXT("COMPANION_BANTER"))
            : FName(TEXT("GREETING"));
    }

    if (!CanUseIntent(SpeakerId, IntentId))
    {
        return Result;
    }

    const FName Key = MakeDialogueKey(SpeakerId, IntentId);
    const TArray<FDialogueVariantRuntime>* Variants = DialogueVariants.Find(Key);
    if (!Variants || Variants->Num() == 0)
    {
        return Result;
    }

    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;

    const FName CurrentMood = GetRegionalWorldMood();
    int32 BestContextRank = -1;
    TArray<const FDialogueVariantRuntime*> Eligible;
    TArray<const FDialogueVariantRuntime*> Fresh;
    for (const FDialogueVariantRuntime& Variant : *Variants)
    {
        if (CountWords(Variant.Text) > Variant.MaxWords)
        {
            continue;
        }
        if (Variant.RequiredStoryBeat != NAME_None &&
            (!Quests || !Quests->HasStoryBeatTriggered(Variant.RequiredStoryBeat)))
        {
            continue;
        }
        if (Variant.RequiredMemory != NAME_None &&
            (!Quests || !Quests->HasNamedNPCMemory(SpeakerId, Variant.RequiredMemory)))
        {
            continue;
        }

        const int32 ContextRank = ShireDialogueContextRank(
            Variant.RequiredMood, CurrentMood,
            Variant.RequiredStoryBeat != NAME_None || Variant.RequiredMemory != NAME_None);
        if (ContextRank < 0 || ContextRank < BestContextRank)
        {
            continue;
        }
        if (ContextRank > BestContextRank)
        {
            Eligible.Reset();
            Fresh.Reset();
            BestContextRank = ContextRank;
        }
        Eligible.Add(&Variant);
        if (!Quests || !Quests->HasRecentNPCDialogueVariant(SpeakerId, Variant.VariantId))
        {
            Fresh.Add(&Variant);
        }
    }

    const TArray<const FDialogueVariantRuntime*>& Pool = Fresh.Num() > 0 ? Fresh : Eligible;
    if (Pool.Num() == 0)
    {
        return Result;
    }

    uint32 Seed = GetTypeHash(SpeakerId);
    Seed = HashCombine(Seed, GetTypeHash(ListenerId));
    Seed = HashCombine(Seed, GetTypeHash(IntentId));
    Seed = HashCombine(Seed, GetTypeHash(LocationTag));
    int32 RelationshipContext = 0;
    if (Quests)
    {
        Seed = HashCombine(Seed, GetTypeHash(GetContextChapterId()));
        Seed = HashCombine(Seed, GetTypeHash(GetContextActiveQuestId()));
        Seed = HashCombine(Seed, static_cast<uint32>(GetContextActiveQuestStage()));
        RelationshipContext = Quests->GetNamedNPCRelationship(
            SpeakerId,
            ListenerId == NAME_None ? FName(TEXT("PLAYER_FRODO")) : ListenerId);
        Seed = HashCombine(Seed, static_cast<uint32>(RelationshipContext + 100));
        Seed = HashCombine(Seed, GetTypeHash(Quests->GetRingStateTag()));
        Seed = HashCombine(Seed, static_cast<uint32>(Quests->GetRingPressureTier()));
    }
    Seed = HashCombine(Seed, GetTypeHash(GetRegionalWorldMood()));
    Seed = HashCombine(Seed, static_cast<uint32>(FMath::RoundToInt(GetRegionalPressure() * 100.0f)));
    const FFilmDialogueContextRuntime* FilmContext = GetActiveFilmDialogueContext();
    if (FilmContext) Seed = HashCombine(Seed, GetTypeHash(FilmContext->ContextId));

    const FDialogueVariantRuntime* Selected = Pool[Seed % static_cast<uint32>(Pool.Num())];
    Result.bValid = true;
    Result.SpeakerProfileId = SpeakerId;
    Result.ListenerProfileId = ListenerId;
    Result.IntentId = IntentId;
    Result.VariantId = Selected->VariantId;
    Result.Text = FText::FromString(Selected->Text);
    Result.VoiceCue = Selected->VoiceCue;
    Result.ProvenanceMode = TEXT("AUTHORED_VARIANT");
    Result.bMemoryInfluenced =
        Selected->RequiredMemory != NAME_None ||
        Selected->RequiredStoryBeat != NAME_None ||
        RelationshipContext != 0;
    Result.WorldMood = CurrentMood;
    Result.EmotionalState = GetProfileEmotionalState(SpeakerId);
    if (FilmContext)
    {
        Result.SourceContextId = FilmContext->ContextId;
        Result.SourceContextSummary = GetFilmDialogueContextSummary();
    }

    if (Quests)
    {
        Quests->RecordNamedNPCDialogueUse(SpeakerId, Selected->VariantId, ListenerId, MaxRecentLineIds);
    }

    return Result;
}

#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FShireRegionalDialogueTest,
    "Shire.NPC.RegionalDialogue", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FShireRegionalDialogueTest::RunTest(const FString& Parameters)
{
    const FName Dread(TEXT("DEAD_CITY_DREAD"));
    const FName Grief(TEXT("GRIEF_AND_REFUGE"));
    TestEqual(TEXT("Wrong-region lines stay ineligible even with memory"), ShireDialogueContextRank(Dread, Grief, true), -1);
    TestEqual(TEXT("Unknown mood does not unlock regional text"), ShireDialogueContextRank(Dread, NAME_None, false), -1);
    TestEqual(TEXT("Generic fallback remains available"), ShireDialogueContextRank(NAME_None, Grief, false), 0);
    TestTrue(TEXT("Current mood outranks generic remembered text"),
        ShireDialogueContextRank(Grief, Grief, false) > ShireDialogueContextRank(NAME_None, Grief, true));
    TestTrue(TEXT("Remembered contextual text wins within a mood"),
        ShireDialogueContextRank(Grief, Grief, true) > ShireDialogueContextRank(Grief, Grief, false));
    return true;
}
#endif
