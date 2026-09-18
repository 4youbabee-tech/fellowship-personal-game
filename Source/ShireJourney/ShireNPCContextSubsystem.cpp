#include "ShireNPCContextSubsystem.h"

#include "ShireQuestSubsystem.h"

#include "Dom/JsonObject.h"
#include "Engine/GameInstance.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

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

    const bool bSocialLoaded = LoadSocialModel();
    const bool bConversationLoaded = LoadConversationPlan();
    const bool bBoundedLoaded = LoadBoundedDialoguePlan();
    BuildDialogueVariantLibrary();

    bDataReady = bSocialLoaded && bConversationLoaded && bBoundedLoaded && Profiles.Num() > 0;

    if (bDataReady)
    {
        UE_LOG(
            LogTemp,
            Display,
            TEXT("NPCContext: ready=yes profiles=%d scheduleBindings=%d intentContracts=%d dialogueKeys=%d"),
            Profiles.Num(),
            ProfileSchedules.Num(),
            IntentRequiredKnowledge.Num(),
            DialogueVariants.Num());
    }
    else
    {
        UE_LOG(
            LogTemp,
            Error,
            TEXT("NPCContext: ready=no profiles=%d scheduleBindings=%d intentContracts=%d dialogueKeys=%d"),
            Profiles.Num(),
            ProfileSchedules.Num(),
            IntentRequiredKnowledge.Num(),
            DialogueVariants.Num());
    }
}

void UShireNPCContextSubsystem::Deinitialize()
{
    Profiles.Empty();
    CanonicalLookup.Empty();
    ProfileSchedules.Empty();
    IntentRequiredKnowledge.Empty();
    DialogueVariants.Empty();
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
        Object->TryGetStringField(TEXT("id"), IdString);
        Object->TryGetStringField(TEXT("display_name"), DisplayName);
        Object->TryGetStringField(TEXT("type"), TypeString);
        Object->TryGetStringField(TEXT("persistence_tier"), PersistenceTier);
        Object->TryGetStringField(TEXT("community"), Community);

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
        ParseNameArray(Object, TEXT("aliases"), Profile.Aliases);
        ParseNameArray(Object, TEXT("regions"), Profile.Regions);
        ParseNameArray(Object, TEXT("roles"), Profile.Roles);
        ParseNameArray(Object, TEXT("knowledge_tags"), Profile.KnowledgeTags);
        ParseNameArray(Object, TEXT("anchors"), Profile.Anchors);

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

void UShireNPCContextSubsystem::AddDialogueVariant(
    FName SpeakerProfileId,
    FName IntentId,
    FName VariantId,
    const TCHAR* Text,
    FName VoiceCue,
    FName RequiredStoryBeat,
    FName RequiredMemory)
{
    FDialogueVariantRuntime Variant;
    Variant.SpeakerProfileId = SpeakerProfileId;
    Variant.IntentId = IntentId;
    Variant.VariantId = VariantId;
    Variant.Text = Text;
    Variant.VoiceCue = VoiceCue;
    Variant.RequiredStoryBeat = RequiredStoryBeat;
    Variant.RequiredMemory = RequiredMemory;
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

    FName Region = Quests->GetCurrentChapterId();
    if (Quests->GetCurrentRouteId() == TEXT("GandalfParallel"))
    {
        Region = TEXT("P1G01");
    }

    return Profile.Regions.Num() == 0 || Profile.Regions.Contains(Region);
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

    const FName Quest = Quests->GetActiveQuestId();
    const int32 Stage = Quests->GetActiveQuestStage();

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
        Seed = HashCombine(Seed, GetTypeHash(Quests->GetCurrentChapterId()));
        Seed = HashCombine(Seed, GetTypeHash(Quests->GetActiveQuestId()));
        Seed = HashCombine(Seed, static_cast<uint32>(Quests->GetActiveQuestStage()));
        RelationshipContext = Quests->GetNamedNPCRelationship(
            SpeakerId,
            ListenerId == NAME_None ? FName(TEXT("PLAYER_FRODO")) : ListenerId);
        Seed = HashCombine(Seed, static_cast<uint32>(RelationshipContext + 100));
    }

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

    if (Quests)
    {
        Quests->RecordNamedNPCDialogueUse(SpeakerId, Selected->VariantId, ListenerId, MaxRecentLineIds);
    }

    return Result;
}
