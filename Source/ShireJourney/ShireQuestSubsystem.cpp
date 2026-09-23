#include "ShireQuestSubsystem.h"
#include "ShireNPCContextSubsystem.h"

#include "GameFramework/Pawn.h"
#include "Kismet/GameplayStatics.h"

#include "Dom/JsonObject.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

void UShireQuestSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    BuildQuestDefinitions();
    LoadJourneyDiscoveryPlan();
    LoadSideActivityPlan();
    LoadPart1ProductionAtlas();
    LoadPart1WorldMap();
    CurrentChapterId = TEXT("P1C01");
    CurrentRouteId = TEXT("FrodoMain");
    CurrentEpisodeId = TEXT("P1C01_Main");
    PlayableCharacterId = TEXT("Frodo");
    bPersistenceRestoreInProgress = false;
    StartQuest(TEXT("ShireArrival"), 0);
}

bool UShireQuestSubsystem::BeginPersistenceRestore()
{
    if (bPersistenceRestoreInProgress)
    {
        UE_LOG(LogTemp, Error, TEXT("ShirePersistenceRestore: BEGIN rejected reason=already-in-progress"));
        return false;
    }

    PersistenceRestorePreviousChapterId = CurrentChapterId;
    PersistenceRestorePreviousRouteId = CurrentRouteId;
    PersistenceRestorePreviousEpisodeId = CurrentEpisodeId;
    PersistenceRestorePreviousPlayableCharacterId = PlayableCharacterId;
    PersistenceRestorePreviousActiveQuestId = ActiveQuestId;
    bPersistenceRestoreInProgress = true;

    UE_LOG(
        LogTemp,
        Verbose,
        TEXT("ShirePersistenceRestore: BEGIN chapter=%s route=%s episode=%s"),
        *CurrentChapterId.ToString(),
        *CurrentRouteId.ToString(),
        *CurrentEpisodeId.ToString());
    return true;
}

void UShireQuestSubsystem::CommitPersistenceRestore(bool bBroadcastQuestStateRestored)
{
    if (!bPersistenceRestoreInProgress)
    {
        UE_LOG(LogTemp, Warning, TEXT("ShirePersistenceRestore: COMMIT ignored reason=not-in-progress"));
        return;
    }

    // The restore-repair hook runs while mutation broadcasts are still suppressed.
    // StoryFlow may canonicalize legacy terminal states here, but StartChapter /
    // StartExperience / StartQuest remain silent until the final repaired identity
    // is known. This prevents the router and world consumers from committing an
    // intermediate legacy state and then committing again.
    if (bBroadcastQuestStateRestored)
    {
        OnQuestStateRestored.Broadcast();
    }

    bPersistenceRestoreInProgress = false;

    // Publish exactly one complete, repaired logical snapshot after every
    // persistence domain and any canonical legacy repair have settled.
    OnExperienceChanged.Broadcast(CurrentRouteId, CurrentEpisodeId, PlayableCharacterId);
    if (PersistenceRestorePreviousChapterId != CurrentChapterId)
    {
        OnChapterChanged.Broadcast(PersistenceRestorePreviousChapterId, CurrentChapterId);
    }
    OnActiveQuestChanged.Broadcast(ActiveQuestId);
    for (const TPair<FName, int32>& Pair : QuestStages)
    {
        OnQuestStageChanged.Broadcast(Pair.Key, Pair.Value);
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShirePersistenceRestore: COMMIT chapter=%s route=%s episode=%s repairBroadcast=%s"),
        *CurrentChapterId.ToString(),
        *CurrentRouteId.ToString(),
        *CurrentEpisodeId.ToString(),
        bBroadcastQuestStateRestored ? TEXT("yes") : TEXT("no"));

    PersistenceRestorePreviousChapterId = NAME_None;
    PersistenceRestorePreviousRouteId = NAME_None;
    PersistenceRestorePreviousEpisodeId = NAME_None;
    PersistenceRestorePreviousPlayableCharacterId = NAME_None;
    PersistenceRestorePreviousActiveQuestId = NAME_None;
}

void UShireQuestSubsystem::AbortPersistenceRestore()
{
    if (!bPersistenceRestoreInProgress)
    {
        return;
    }

    bPersistenceRestoreInProgress = false;
    PersistenceRestorePreviousChapterId = NAME_None;
    PersistenceRestorePreviousRouteId = NAME_None;
    PersistenceRestorePreviousEpisodeId = NAME_None;
    PersistenceRestorePreviousPlayableCharacterId = NAME_None;
    PersistenceRestorePreviousActiveQuestId = NAME_None;
    UE_LOG(LogTemp, Error, TEXT("ShirePersistenceRestore: ABORTED broadcasts-suppressed=yes"));
}

void UShireQuestSubsystem::AddQuestDefinition(FName QuestId, const FString& Title,
    std::initializer_list<const TCHAR*> Objectives)
{
    FShireQuestDefinition Definition;
    Definition.Title = FText::FromString(Title);
    for (const TCHAR* Objective : Objectives)
    {
        Definition.Objectives.Add(FText::FromString(Objective));
    }
    QuestDefinitions.Add(QuestId, Definition);
}

void UShireQuestSubsystem::BuildQuestDefinitions()
{
    QuestDefinitions.Empty();

    // Chapter 1 — The Shire
    AddQuestDefinition(TEXT("ShireArrival"), TEXT("An Unexpected Arrival"), {
        TEXT("Reach the Shire lane and meet Gandalf."),
        TEXT("Follow the road through the fields toward Hobbiton."),
        TEXT("Cross the stone bridge and continue toward the party field."),
        TEXT("The preparations are underway. Find Bilbo at the party field.")
    });
    AddQuestDefinition(TEXT("LongExpectedParty"), TEXT("A Long-Expected Party"), {
        TEXT("Explore the celebration and speak with Bilbo."),
        TEXT("Bilbo has vanished. Return toward Bag End."),
        TEXT("The party is over. Something has changed.")
    });
    AddQuestDefinition(TEXT("RingSecret"), TEXT("Keep It Secret"), {
        TEXT("Find Gandalf at Bag End and speak with him privately."),
        TEXT("The Ring is dangerous. Find Sam and prepare to leave."),
        TEXT("Do not draw attention to the Ring.")
    });
    AddQuestDefinition(TEXT("LeavingHome"), TEXT("Leaving Home"), {
        TEXT("Meet Sam beside Bag End."),
        TEXT("Leave Hobbiton quietly with Sam."),
        TEXT("The familiar lanes are behind you.")
    });
    AddQuestDefinition(TEXT("Shortcut"), TEXT("A Short Cut"), {
        TEXT("Cross the fields with Sam."),
        TEXT("Find Merry and Pippin after the collision in the crops."),
        TEXT("Move toward the wooded road together.")
    });
    AddQuestDefinition(TEXT("KeepOffRoad"), TEXT("Keep Off the Road"), {
        TEXT("Something is approaching. Get below the road and stay hidden."),
        TEXT("The Black Rider is searching. Crouch, stay quiet, and slip away."),
        TEXT("Run for the forest path before the Rider circles back.")
    });
    AddQuestDefinition(TEXT("FerryEscape"), TEXT("Bucklebury Ferry"), {
        TEXT("Stay together and run for the ferry."),
        TEXT("Reach the far side of the Brandywine."),
        TEXT("The Shire is behind you. Bree lies ahead.")
    });

    // Parallel Part I route — Gandalf / Isengard
    AddQuestDefinition(TEXT("IsengardCounsel"), TEXT("The Road to Isengard"), {
        TEXT("Approach Orthanc and seek Saruman's counsel."),
        TEXT("Enter the tower and confront what Saruman has become."),
        TEXT("The alliance is broken. Survive the betrayal.")
    });
    AddQuestDefinition(TEXT("OrthancCaptive"), TEXT("The Tower of Orthanc"), {
        TEXT("Imprisoned above Isengard, study what is happening below."),
        TEXT("The valley is being remade for war. Look for a chance to escape."),
        TEXT("Hold out until an escape becomes possible.")
    });
    AddQuestDefinition(TEXT("OrthancEscape"), TEXT("Escape from Isengard"), {
        TEXT("Reach the open edge of the tower."),
        TEXT("Escape Orthanc and carry warning back to the free peoples."),
        TEXT("The road now turns back toward the Ring-bearer.")
    });

    // Chapter 2 — Bree
    AddQuestDefinition(TEXT("RoadToBree"), TEXT("The East Road"), {
        TEXT("Follow the road east with Sam, Merry and Pippin."),
        TEXT("Travel carefully as evening closes in."),
        TEXT("Reach the gates of Bree.")
    });
    AddQuestDefinition(TEXT("BreeArrival"), TEXT("At the Sign of the Prancing Pony"), {
        TEXT("Enter Bree and find the Prancing Pony."),
        TEXT("Ask after Gandalf without drawing attention."),
        TEXT("Remain alert. Someone is watching the room.")
    });
    AddQuestDefinition(TEXT("MeetStrider"), TEXT("Strider"), {
        TEXT("Speak with the Ranger who calls himself Strider."),
        TEXT("Follow his warning away from the common room."),
        TEXT("Prepare for the danger moving through Bree tonight.")
    });
    AddQuestDefinition(TEXT("NightAttack"), TEXT("The Nazgul"), {
        TEXT("Stay out of sight while Strider prepares a safer room."),
        TEXT("The Riders have struck the decoy beds. Remain hidden until dawn."),
        TEXT("Leave Bree with Strider before the Riders can return.")
    });

    // Chapter 3 — Weathertop / Ford
    AddQuestDefinition(TEXT("RoadToWeathertop"), TEXT("Into the Wild"), {
        TEXT("Follow Strider away from the roads most travelers use."),
        TEXT("Cross the wet lowlands and keep the company together."),
        TEXT("Reach the high ground below Weathertop.")
    });
    AddQuestDefinition(TEXT("WeathertopAttack"), TEXT("A Knife in the Dark"), {
        TEXT("Climb the ruined watchtower and make a cautious camp."),
        TEXT("The Riders are near. Stay close to the fire and your companions."),
        TEXT("Survive the attack long enough for Strider to drive them back."),
        TEXT("Frodo is wounded. The journey must turn toward Rivendell.")
    });
    AddQuestDefinition(TEXT("FlightToFord"), TEXT("Flight to the Ford"), {
        TEXT("Keep moving east with the wounded Ring-bearer."),
        TEXT("Follow Arwen toward the river crossing."),
        TEXT("Reach the far bank before the Riders close in.")
    });

    // Chapter 4 — Rivendell
    AddQuestDefinition(TEXT("RivendellRecovery"), TEXT("Rivendell"), {
        TEXT("Wake in the hidden valley and regain your bearings."),
        TEXT("Find Gandalf and learn what happened after the Ford."),
        TEXT("The Ring cannot remain here. Prepare for the Council.")
    });
    AddQuestDefinition(TEXT("CouncilOfElrond"), TEXT("The Council of Elrond"), {
        TEXT("Join the gathering on the council terrace."),
        TEXT("Listen as the danger of the Ring is laid before the company."),
        TEXT("A decision has been made. The Ring must go south.")
    });
    AddQuestDefinition(TEXT("FellowshipForms"), TEXT("The Fellowship"), {
        TEXT("Meet the companions who will travel with Frodo."),
        TEXT("Prepare supplies for the road south."),
        TEXT("Leave Rivendell with the Fellowship.")
    });

    // Chapter 5 — Southward / Caradhras / West-gate
    AddQuestDefinition(TEXT("SouthwardJourney"), TEXT("The Ring Goes South"), {
        TEXT("Travel south with the Fellowship."),
        TEXT("Keep watch as the land rises toward the mountains."),
        TEXT("Approach the pass of Caradhras.")
    });
    AddQuestDefinition(TEXT("CaradhrasPass"), TEXT("The Pass of Caradhras"), {
        TEXT("Push into the snow while the storm worsens."),
        TEXT("Keep the company together in the deepening drifts."),
        TEXT("The pass is lost. Turn back and seek another road.")
    });
    AddQuestDefinition(TEXT("WestGate"), TEXT("The West-gate of Moria"), {
        TEXT("Reach the dark lake before the western door."),
        TEXT("Search the stone and help Gandalf open the hidden entrance."),
        TEXT("Enter Moria before the shore becomes more dangerous.")
    });

    // Chapter 6 — Moria
    AddQuestDefinition(TEXT("MoriaDark"), TEXT("A Journey in the Dark"), {
        TEXT("Follow Gandalf beneath the mountain."),
        TEXT("Cross the great halls and watch for signs of danger."),
        TEXT("Evidence of battle leads toward a sealed chamber.")
    });
    AddQuestDefinition(TEXT("BalinsTomb"), TEXT("Balin's Tomb"), {
        TEXT("Enter the chamber and learn what happened to the colony."),
        TEXT("Stay close as the Fellowship realizes it is trapped."),
        TEXT("Break out before the drums in the deep draw nearer.")
    });
    AddQuestDefinition(TEXT("BridgeOfKhazadDum"), TEXT("The Bridge of Khazad-dum"), {
        TEXT("Run through the lower halls toward the bridge."),
        TEXT("Cross while Gandalf holds the enemy back."),
        TEXT("Escape the mountain after Gandalf falls."),
        TEXT("Keep moving. The Fellowship cannot remain outside Moria.")
    });

    // Chapter 7 — Lothlorien
    AddQuestDefinition(TEXT("LothlorienRest"), TEXT("Lothlorien"), {
        TEXT("Enter the guarded woods while the Fellowship grieves."),
        TEXT("Follow the hidden path under Haldir's watch."),
        TEXT("Reach the safety of the Galadhrim."),
        TEXT("Rest and prepare for the river journey.")
    });
    AddQuestDefinition(TEXT("GaladrielFarewell"), TEXT("Farewell to Lorien"), {
        TEXT("Gather the boats and supplies prepared for the Fellowship."),
        TEXT("Say farewell and make ready to depart."),
        TEXT("Take to the Anduin and continue south.")
    });

    // Chapter 8 — Anduin / Amon Hen / Breaking of the Fellowship
    AddQuestDefinition(TEXT("AnduinJourney"), TEXT("The Great River"), {
        TEXT("Travel down the Anduin and keep the boats together."),
        TEXT("Pass beneath the ancient stone guardians."),
        TEXT("Land beneath Amon Hen for a brief rest.")
    });
    AddQuestDefinition(TEXT("AmonHen"), TEXT("Amon Hen"), {
        TEXT("Explore the wooded ruins while the Fellowship debates its road."),
        TEXT("Find Boromir and learn why he has left the others."),
        TEXT("Enemies are entering the woods. Regroup quickly.")
    });
    AddQuestDefinition(TEXT("BreakingFellowship"), TEXT("The Breaking of the Fellowship"), {
        TEXT("Find the scattered companions during the attack."),
        TEXT("Merry and Pippin are in danger. Reach the lower woods."),
        TEXT("Frodo must choose his road while the Fellowship breaks apart."),
        TEXT("Reach the eastern shore with Sam.")
    });
    AddQuestDefinition(TEXT("Part1Complete"), TEXT("Part I Complete"), {
        TEXT("The Fellowship has broken, but the journey continues."),
        TEXT("Part I is complete.")
    });
}

int32 UShireQuestSubsystem::GetQuestStage(FName QuestId) const
{
    if (const int32* Stage = QuestStages.Find(QuestId))
    {
        return *Stage;
    }
    return 0;
}

void UShireQuestSubsystem::SetQuestStage(FName QuestId, int32 NewStage)
{
    if (QuestId == NAME_None)
    {
        return;
    }

    const int32 ClampedStage = FMath::Max(0, NewStage);
    QuestStages.Add(QuestId, ClampedStage);
    OnQuestStageChanged.Broadcast(QuestId, ClampedStage);
}

void UShireQuestSubsystem::AdvanceQuest(FName QuestId, int32 Amount)
{
    SetQuestStage(QuestId, GetQuestStage(QuestId) + Amount);
}

void UShireQuestSubsystem::StartQuest(FName QuestId, int32 InitialStage)
{
    if (QuestId == NAME_None)
    {
        return;
    }

    ActiveQuestId = QuestId;
    QuestStages.Add(QuestId, FMath::Max(0, InitialStage));
    if (!bPersistenceRestoreInProgress)
    {
        OnActiveQuestChanged.Broadcast(QuestId);
        OnQuestStageChanged.Broadcast(QuestId, GetQuestStage(QuestId));
    }
}

void UShireQuestSubsystem::StartChapter(FName ChapterId, FName StartingQuestId, int32 StartingQuestStage)
{
    if (ChapterId == NAME_None)
    {
        return;
    }

    const FName TargetEpisodeId = CurrentRouteId == TEXT("FrodoMain")
        ? FName(*FString::Printf(TEXT("%s_Main"), *ChapterId.ToString()))
        : CurrentEpisodeId;
    if (!bPersistenceRestoreInProgress)
    {
        OnWorldTransitionRequested.Broadcast(
            ChapterId,
            CurrentRouteId,
            TargetEpisodeId);
    }

    const FName PreviousChapterId = CurrentChapterId;
    CurrentChapterId = ChapterId;

    if (CurrentRouteId == TEXT("FrodoMain"))
    {
        CurrentEpisodeId = TargetEpisodeId;
        PlayableCharacterId = TEXT("Frodo");
    }

    if (PreviousChapterId != CurrentChapterId)
    {
        // Memory pruning is destructive. The destination may still fail to build,
        // so defer aging until ChapterWorldRouter commits destination geometry.
        if (!bPersistenceRestoreInProgress)
        {
            OnChapterChanged.Broadcast(PreviousChapterId, CurrentChapterId);
        }
    }

    if (StartingQuestId != NAME_None)
    {
        StartQuest(StartingQuestId, StartingQuestStage);
    }
}

FShireRouteProgress UShireQuestSubsystem::CaptureCurrentRouteProgress(bool bCapturePlayerTransform) const
{
    FShireRouteProgress Progress;
    Progress.QuestStages = QuestStages;
    Progress.ActiveQuestId = ActiveQuestId;
    Progress.CurrentChapterId = CurrentChapterId;
    Progress.EpisodeId = CurrentEpisodeId;
    Progress.PlayableCharacterId = PlayableCharacterId;
    Progress.CompletedStoryBeats = CompletedStoryBeats;

    if (bCapturePlayerTransform)
    {
        if (APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0))
        {
            Progress.bHasPlayerTransform = true;
            Progress.PlayerLocation = PlayerPawn->GetActorLocation();
            Progress.PlayerRotation = PlayerPawn->GetActorRotation();
        }
    }

    return Progress;
}

void UShireQuestSubsystem::ApplyRouteProgress(const FShireRouteProgress& Progress)
{
    QuestStages = Progress.QuestStages;
    ActiveQuestId = Progress.ActiveQuestId;
    CurrentChapterId = Progress.CurrentChapterId == NAME_None ? FName(TEXT("P1C01")) : Progress.CurrentChapterId;
    CurrentEpisodeId = Progress.EpisodeId;
    PlayableCharacterId = Progress.PlayableCharacterId == NAME_None ? FName(TEXT("Frodo")) : Progress.PlayableCharacterId;
    CompletedStoryBeats = Progress.CompletedStoryBeats;
}

void UShireQuestSubsystem::StartExperience(FName RouteId, FName EpisodeId, FName InPlayableCharacterId,
    FName ChapterId, FName StartingQuestId, int32 StartingQuestStage)
{
    if (RouteId == NAME_None)
    {
        return;
    }

    FName TargetChapterId = ChapterId == NAME_None ? FName(TEXT("P1C01")) : ChapterId;
    FName TargetEpisodeId = EpisodeId;
    if (const FShireRouteProgress* TargetExisting = RouteProgress.Find(RouteId))
    {
        if (TargetExisting->CurrentChapterId != NAME_None)
        {
            TargetChapterId = TargetExisting->CurrentChapterId;
        }
        if (TargetEpisodeId == NAME_None)
        {
            TargetEpisodeId = TargetExisting->EpisodeId;
        }
    }
    if (!bPersistenceRestoreInProgress)
    {
        OnWorldTransitionRequested.Broadcast(
            TargetChapterId,
            RouteId,
            TargetEpisodeId);
    }

    if (CurrentRouteId != NAME_None && !bPersistenceRestoreInProgress)
    {
        RouteProgress.Add(CurrentRouteId, CaptureCurrentRouteProgress(true));
    }

    CurrentRouteId = RouteId;

    if (const FShireRouteProgress* Existing = RouteProgress.Find(RouteId))
    {
        ApplyRouteProgress(*Existing);
    }
    else
    {
        QuestStages.Empty();
        CompletedStoryBeats.Empty();
        ActiveQuestId = NAME_None;
        CurrentChapterId = ChapterId == NAME_None ? FName(TEXT("P1C01")) : ChapterId;
        CurrentEpisodeId = EpisodeId;
        PlayableCharacterId = InPlayableCharacterId == NAME_None ? FName(TEXT("Frodo")) : InPlayableCharacterId;

        if (StartingQuestId != NAME_None)
        {
            ActiveQuestId = StartingQuestId;
            QuestStages.Add(StartingQuestId, FMath::Max(0, StartingQuestStage));
        }
    }

    if (EpisodeId != NAME_None)
    {
        CurrentEpisodeId = EpisodeId;
    }
    if (InPlayableCharacterId != NAME_None)
    {
        PlayableCharacterId = InPlayableCharacterId;
    }

    if (!bPersistenceRestoreInProgress)
    {
        OnExperienceChanged.Broadcast(CurrentRouteId, CurrentEpisodeId, PlayableCharacterId);
        OnActiveQuestChanged.Broadcast(ActiveQuestId);
        for (const TPair<FName, int32>& Pair : QuestStages)
        {
            OnQuestStageChanged.Broadcast(Pair.Key, Pair.Value);
        }
    }
}

TMap<FName, FShireRouteProgress> UShireQuestSubsystem::GetRouteProgressSnapshot() const
{
    TMap<FName, FShireRouteProgress> Snapshot = RouteProgress;
    if (CurrentRouteId != NAME_None)
    {
        Snapshot.Add(CurrentRouteId, CaptureCurrentRouteProgress(true));
    }
    return Snapshot;
}

bool UShireQuestSubsystem::GetCurrentRouteSavedTransform(FVector& OutLocation, FRotator& OutRotation) const
{
    if (const FShireRouteProgress* Progress = RouteProgress.Find(CurrentRouteId))
    {
        if (Progress->bHasPlayerTransform)
        {
            OutLocation = Progress->PlayerLocation;
            OutRotation = Progress->PlayerRotation;
            return true;
        }
    }

    return false;
}

void UShireQuestSubsystem::TriggerStoryBeat(FName StoryBeatId)
{
    if (StoryBeatId == NAME_None || CompletedStoryBeats.Contains(StoryBeatId))
    {
        return;
    }

    CompletedStoryBeats.Add(StoryBeatId);
    RecordStoryBeatForEligibleNPCs(StoryBeatId);
    OnStoryBeatTriggered.Broadcast(StoryBeatId);
}

bool UShireQuestSubsystem::HasStoryBeatTriggered(FName StoryBeatId) const
{
    return StoryBeatId != NAME_None && CompletedStoryBeats.Contains(StoryBeatId);
}

bool UShireQuestSubsystem::IsRingQuestActive() const
{
    if (CurrentRouteId == TEXT("GandalfParallel"))
    {
        return true;
    }

    const int32 Chapter = ChapterOrdinal(CurrentChapterId);
    if (Chapter > 1)
    {
        return true;
    }

    return HasStoryBeatTriggered(TEXT("BilboDisappearance")) ||
        HasStoryBeatTriggered(TEXT("RingWarning")) ||
        ActiveQuestId == TEXT("RingSecret") ||
        ActiveQuestId == TEXT("LeavingHome") ||
        ActiveQuestId == TEXT("FerryEscape");
}

FName UShireQuestSubsystem::GetRingBearerId() const
{
    if (CurrentRouteId == TEXT("GandalfParallel"))
    {
        return TEXT("Frodo");
    }

    const int32 Chapter = ChapterOrdinal(CurrentChapterId);
    return (Chapter > 1 || IsRingQuestActive()) ? FName(TEXT("Frodo")) : FName(TEXT("Bilbo"));
}

FName UShireQuestSubsystem::GetRingStateTag() const
{
    if (CurrentRouteId == TEXT("GandalfParallel")) return TEXT("OFF_ROUTE_WITH_FRODO");
    if (!IsRingQuestActive()) return TEXT("PRE_TRANSFER");

    const int32 Chapter = ChapterOrdinal(CurrentChapterId);
    if (Chapter <= 1) return TEXT("HIDDEN_SECRET");
    if (Chapter == 2) return TEXT("EXPOSED_AT_BREE");
    if (Chapter == 3) return TEXT("WOUNDED_HUNTED_BURDEN");
    if (Chapter == 4) return TEXT("COUNCIL_MISSION");
    if (Chapter == 5) return TEXT("FELLOWSHIP_GUARDING_RING");
    if (Chapter == 6) return TEXT("MORIA_BURDEN");
    if (Chapter == 7) return TEXT("TEMPTATION_TEST");
    return TEXT("FELLOWSHIP_FRACTURE");
}

int32 UShireQuestSubsystem::GetRingPressureTier() const
{
    if (!IsRingQuestActive()) return 0;
    if (CurrentRouteId == TEXT("GandalfParallel")) return 2;

    const int32 Chapter = ChapterOrdinal(CurrentChapterId);
    if (Chapter <= 1) return 1;
    if (Chapter == 2) return 2;
    if (Chapter == 3) return HasStoryBeatTriggered(TEXT("MorgulWound")) ? 3 : 2;
    if (Chapter == 4 || Chapter == 5) return 2;
    if (Chapter == 6) return 3;
    if (Chapter == 7) return HasStoryBeatTriggered(TEXT("Mirror")) ? 4 : 3;
    if (Chapter >= 8)
    {
        return HasStoryBeatTriggered(TEXT("BoromirPressure")) ||
            HasStoryBeatTriggered(TEXT("UrukAttack")) ||
            HasStoryBeatTriggered(TEXT("BoromirFall")) ? 4 : 3;
    }
    return 1;
}


bool UShireQuestSubsystem::LoadJourneyDiscoveryPlan()
{
    JourneyDiscoveryDefinitions.Empty();
    JourneyInsightDefinitions.Empty();
    JourneyRegionBonusDefinitions.Empty();

    const FString Path = FPaths::Combine(FPaths::ProjectDir(), TEXT("Data/JourneyDiscoveryRewardPlan.json"));
    FString JsonText;
    if (!FFileHelper::LoadFileToString(JsonText, *Path))
    {
        UE_LOG(LogTemp, Error, TEXT("JourneyDiscovery: failed to read %s"), *Path);
        return false;
    }

    TSharedPtr<FJsonObject> Root;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonText);
    if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("JourneyDiscovery: invalid JSON %s"), *Path);
        return false;
    }

    const TArray<TSharedPtr<FJsonValue>>* Rewards = nullptr;
    if (Root->TryGetArrayField(TEXT("discovery_rewards"), Rewards) && Rewards)
    {
        for (const TSharedPtr<FJsonValue>& Value : *Rewards)
        {
            const TSharedPtr<FJsonObject> Object = Value.IsValid() ? Value->AsObject() : nullptr;
            if (!Object.IsValid())
            {
                continue;
            }

            FString Id, Route, Chapter, Region, Category, DisplayLabel;
            double InsightNumber = 0.0;
            Object->TryGetStringField(TEXT("discovery_id"), Id);
            Object->TryGetStringField(TEXT("route"), Route);
            Object->TryGetStringField(TEXT("chapter"), Chapter);
            Object->TryGetStringField(TEXT("region"), Region);
            Object->TryGetStringField(TEXT("category"), Category);
            Object->TryGetStringField(TEXT("display_label"), DisplayLabel);
            Object->TryGetNumberField(TEXT("journey_insight"), InsightNumber);
            if (Id.IsEmpty() || Route.IsEmpty() || Chapter.IsEmpty() || Region.IsEmpty() ||
                DisplayLabel.IsEmpty() || InsightNumber <= 0.0)
            {
                continue;
            }

            FShireJourneyDiscoveryDefinition Definition;
            Definition.DiscoveryId = FName(*Id);
            Definition.RouteId = FName(*Route);
            Definition.ChapterId = FName(*Chapter);
            Definition.RegionId = FName(*Region);
            Definition.CategoryId = FName(*Category);
            Definition.DisplayLabel = DisplayLabel;
            Definition.Insight = FMath::Max(1, FMath::RoundToInt(InsightNumber));
            JourneyDiscoveryDefinitions.Add(Definition.DiscoveryId, Definition);
        }
    }

    const TArray<TSharedPtr<FJsonValue>>* Milestones = nullptr;
    if (Root->TryGetArrayField(TEXT("journey_insight_milestones"), Milestones) && Milestones)
    {
        for (const TSharedPtr<FJsonValue>& Value : *Milestones)
        {
            const TSharedPtr<FJsonObject> Object = Value.IsValid() ? Value->AsObject() : nullptr;
            if (!Object.IsValid())
            {
                continue;
            }

            FString Id;
            double ThresholdNumber = 0.0;
            Object->TryGetStringField(TEXT("id"), Id);
            Object->TryGetNumberField(TEXT("threshold"), ThresholdNumber);
            if (!Id.IsEmpty() && ThresholdNumber > 0.0)
            {
                FShireJourneyInsightMilestoneDefinition Definition;
                Definition.MilestoneId = FName(*Id);
                Definition.Threshold = FMath::RoundToInt(ThresholdNumber);
                JourneyInsightDefinitions.Add(Definition);
            }
        }
    }

    const TArray<TSharedPtr<FJsonValue>>* RegionBonuses = nullptr;
    if (Root->TryGetArrayField(TEXT("region_completion_bonuses"), RegionBonuses) && RegionBonuses)
    {
        for (const TSharedPtr<FJsonValue>& Value : *RegionBonuses)
        {
            const TSharedPtr<FJsonObject> Object = Value.IsValid() ? Value->AsObject() : nullptr;
            if (!Object.IsValid())
            {
                continue;
            }

            FString Route, Chapter;
            double RequiredNumber = 0.0;
            double BonusNumber = 0.0;
            Object->TryGetStringField(TEXT("route"), Route);
            Object->TryGetStringField(TEXT("chapter"), Chapter);
            Object->TryGetNumberField(TEXT("required_discoveries"), RequiredNumber);
            Object->TryGetNumberField(TEXT("bonus_journey_insight"), BonusNumber);
            if (!Route.IsEmpty() && !Chapter.IsEmpty() && RequiredNumber > 0.0 && BonusNumber >= 0.0)
            {
                FShireJourneyRegionBonusDefinition Definition;
                Definition.RouteId = FName(*Route);
                Definition.ChapterId = FName(*Chapter);
                Definition.RequiredDiscoveries = FMath::RoundToInt(RequiredNumber);
                Definition.BonusInsight = FMath::RoundToInt(BonusNumber);
                JourneyRegionBonusDefinitions.Add(Definition);
            }
        }
    }

    const bool bReady =
        JourneyDiscoveryDefinitions.Num() > 0 &&
        JourneyInsightDefinitions.Num() > 0 &&
        JourneyRegionBonusDefinitions.Num() > 0;
    if (bReady)
    {
        UE_LOG(LogTemp, Display,
            TEXT("JourneyDiscovery: ready=yes discoveries=%d milestones=%d regionBonuses=%d"),
            JourneyDiscoveryDefinitions.Num(),
            JourneyInsightDefinitions.Num(),
            JourneyRegionBonusDefinitions.Num());
    }
    else
    {
        UE_LOG(LogTemp, Error,
            TEXT("JourneyDiscovery: ready=no discoveries=%d milestones=%d regionBonuses=%d"),
            JourneyDiscoveryDefinitions.Num(),
            JourneyInsightDefinitions.Num(),
            JourneyRegionBonusDefinitions.Num());
    }
    return bReady;
}


FName UShireQuestSubsystem::MakeChapterProductionKey(FName RouteId, FName ChapterId)
{
    return FName(*FString::Printf(TEXT("%s::%s"), *RouteId.ToString(), *ChapterId.ToString()));
}

const FShireChapterProductionDefinition* UShireQuestSubsystem::FindChapterProductionDefinition(
    FName RouteId,
    FName ChapterId) const
{
    return ChapterProductionDefinitions.Find(MakeChapterProductionKey(RouteId, ChapterId));
}

bool UShireQuestSubsystem::LoadPart1ProductionAtlas()
{
    ChapterProductionDefinitions.Empty();

    const FString Path = FPaths::Combine(FPaths::ProjectDir(), TEXT("Data/Part1ProductionAtlas.json"));
    FString JsonText;
    if (!FFileHelper::LoadFileToString(JsonText, *Path))
    {
        UE_LOG(LogTemp, Error, TEXT("ProductionAtlas: failed to read %s"), *Path);
        return false;
    }

    TSharedPtr<FJsonObject> Root;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonText);
    if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("ProductionAtlas: invalid JSON %s"), *Path);
        return false;
    }

    const TArray<TSharedPtr<FJsonValue>>* Chapters = nullptr;
    if (!Root->TryGetArrayField(TEXT("chapters"), Chapters) || !Chapters)
    {
        UE_LOG(LogTemp, Error, TEXT("ProductionAtlas: chapters array missing"));
        return false;
    }

    for (const TSharedPtr<FJsonValue>& Value : *Chapters)
    {
        const TSharedPtr<FJsonObject> Object = Value.IsValid() ? Value->AsObject() : nullptr;
        if (!Object.IsValid())
        {
            continue;
        }

        FString Route;
        FString Chapter;
        FString DisplayName;
        FString MacroRegion;
        FString PrimaryRegion;
        Object->TryGetStringField(TEXT("route"), Route);
        Object->TryGetStringField(TEXT("chapter"), Chapter);
        Object->TryGetStringField(TEXT("display_name"), DisplayName);
        Object->TryGetStringField(TEXT("macro_region"), MacroRegion);
        Object->TryGetStringField(TEXT("primary_region"), PrimaryRegion);

        if (Route.IsEmpty() || Chapter.IsEmpty() || DisplayName.IsEmpty() ||
            MacroRegion.IsEmpty() || PrimaryRegion.IsEmpty())
        {
            UE_LOG(LogTemp, Error, TEXT("ProductionAtlas: incomplete chapter identity"));
            continue;
        }

        FShireChapterProductionDefinition Definition;
        Definition.RouteId = FName(*Route);
        Definition.ChapterId = FName(*Chapter);
        Definition.DisplayName = DisplayName;
        Definition.MacroRegion = MacroRegion;
        Definition.PrimaryRegion = PrimaryRegion;

        const TArray<TSharedPtr<FJsonValue>>* Landmarks = nullptr;
        if (Object->TryGetArrayField(TEXT("landmark_sequence"), Landmarks) && Landmarks)
        {
            for (const TSharedPtr<FJsonValue>& LandmarkValue : *Landmarks)
            {
                const FString Landmark = LandmarkValue.IsValid() ? LandmarkValue->AsString() : FString();
                if (!Landmark.IsEmpty())
                {
                    Definition.LandmarkSequence.Add(Landmark);
                }
            }
        }

        ChapterProductionDefinitions.Add(
            MakeChapterProductionKey(Definition.RouteId, Definition.ChapterId),
            Definition);
    }

    const bool bReady = ChapterProductionDefinitions.Num() == 9;
    if (bReady)
    {
        UE_LOG(LogTemp, Display, TEXT("ProductionAtlas: ready=yes chapters=%d"),
            ChapterProductionDefinitions.Num());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("ProductionAtlas: ready=no chapters=%d"),
            ChapterProductionDefinitions.Num());
    }
    return bReady;
}

FString UShireQuestSubsystem::GetCurrentChapterDisplayName() const
{
    const FShireChapterProductionDefinition* Definition =
        FindChapterProductionDefinition(CurrentRouteId, CurrentChapterId);
    return Definition ? Definition->DisplayName : CurrentChapterId.ToString();
}

FString UShireQuestSubsystem::GetCurrentPrimaryRegionName() const
{
    const FShireChapterProductionDefinition* Definition =
        FindChapterProductionDefinition(CurrentRouteId, CurrentChapterId);
    return Definition ? Definition->PrimaryRegion : CurrentChapterId.ToString();
}

FString UShireQuestSubsystem::GetCurrentMacroRegionName() const
{
    const FShireChapterProductionDefinition* Definition =
        FindChapterProductionDefinition(CurrentRouteId, CurrentChapterId);
    return Definition ? Definition->MacroRegion : FString();
}

FString UShireQuestSubsystem::GetCurrentLandmarkSummary() const
{
    const FShireChapterProductionDefinition* Definition =
        FindChapterProductionDefinition(CurrentRouteId, CurrentChapterId);
    if (!Definition || Definition->LandmarkSequence.Num() == 0)
    {
        return FString();
    }

    const int32 MaxShown = FMath::Min(3, Definition->LandmarkSequence.Num());
    FString Result;
    for (int32 Index = 0; Index < MaxShown; ++Index)
    {
        if (!Result.IsEmpty())
        {
            Result += TEXT("  >  ");
        }
        Result += Definition->LandmarkSequence[Index];
    }
    return Result;
}


const FShireWorldMapNodeDefinition* UShireQuestSubsystem::FindWorldMapNode(FName NodeId) const
{
    for (const FShireWorldMapNodeDefinition& Node : WorldMapNodes)
    {
        if (Node.NodeId == NodeId)
        {
            return &Node;
        }
    }
    return nullptr;
}

bool UShireQuestSubsystem::LoadPart1WorldMap()
{
    WorldMapNodes.Empty();
    WorldMapEdges.Empty();

    const FString Path = FPaths::Combine(FPaths::ProjectDir(), TEXT("Data/Part1WorldMap.json"));
    FString JsonText;
    if (!FFileHelper::LoadFileToString(JsonText, *Path))
    {
        UE_LOG(LogTemp, Error, TEXT("WorldMap: failed to read %s"), *Path);
        return false;
    }

    TSharedPtr<FJsonObject> Root;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonText);
    if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("WorldMap: invalid JSON %s"), *Path);
        return false;
    }

    const TArray<TSharedPtr<FJsonValue>>* Nodes = nullptr;
    if (Root->TryGetArrayField(TEXT("nodes"), Nodes) && Nodes)
    {
        for (const TSharedPtr<FJsonValue>& Value : *Nodes)
        {
            const TSharedPtr<FJsonObject> Object = Value.IsValid() ? Value->AsObject() : nullptr;
            if (!Object.IsValid())
            {
                continue;
            }

            FString Id, Route, Chapter, DisplayName, MacroRegion;
            double X = 0.0;
            double Y = 0.0;
            bool bAnchor = false;
            Object->TryGetStringField(TEXT("id"), Id);
            Object->TryGetStringField(TEXT("route"), Route);
            Object->TryGetStringField(TEXT("chapter"), Chapter);
            Object->TryGetStringField(TEXT("display_name"), DisplayName);
            Object->TryGetStringField(TEXT("macro_region"), MacroRegion);
            Object->TryGetNumberField(TEXT("x"), X);
            Object->TryGetNumberField(TEXT("y"), Y);
            Object->TryGetBoolField(TEXT("chapter_anchor"), bAnchor);

            if (Id.IsEmpty() || Route.IsEmpty() || Chapter.IsEmpty() || DisplayName.IsEmpty() ||
                MacroRegion.IsEmpty() || X < 0.0 || X > 1.0 || Y < 0.0 || Y > 1.0)
            {
                UE_LOG(LogTemp, Error, TEXT("WorldMap: invalid node contract id=%s"), *Id);
                continue;
            }

            FShireWorldMapNodeDefinition Definition;
            Definition.NodeId = FName(*Id);
            Definition.RouteId = FName(*Route);
            Definition.ChapterId = FName(*Chapter);
            Definition.DisplayName = DisplayName;
            Definition.MacroRegion = MacroRegion;
            Definition.X = static_cast<float>(X);
            Definition.Y = static_cast<float>(Y);
            Definition.bChapterAnchor = bAnchor;
            WorldMapNodes.Add(Definition);
        }
    }

    const TArray<TSharedPtr<FJsonValue>>* Edges = nullptr;
    if (Root->TryGetArrayField(TEXT("edges"), Edges) && Edges)
    {
        for (const TSharedPtr<FJsonValue>& Value : *Edges)
        {
            const TArray<TSharedPtr<FJsonValue>>& Pair = Value->AsArray();
            if (Pair.Num() != 2)
            {
                continue;
            }

            FShireWorldMapEdgeDefinition Edge;
            Edge.FromNodeId = FName(*Pair[0]->AsString());
            Edge.ToNodeId = FName(*Pair[1]->AsString());
            if (FindWorldMapNode(Edge.FromNodeId) && FindWorldMapNode(Edge.ToNodeId))
            {
                WorldMapEdges.Add(Edge);
            }
        }
    }

    const bool bReady = WorldMapNodes.Num() >= 16 && WorldMapEdges.Num() >= 14;
    if (bReady)
    {
        UE_LOG(LogTemp, Display, TEXT("WorldMap: ready=yes nodes=%d edges=%d"),
            WorldMapNodes.Num(), WorldMapEdges.Num());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("WorldMap: ready=no nodes=%d edges=%d"),
            WorldMapNodes.Num(), WorldMapEdges.Num());
    }
    return bReady;
}

bool UShireQuestSubsystem::IsWorldMapNodeVisible(FName NodeId) const
{
    const FShireWorldMapNodeDefinition* Node = FindWorldMapNode(NodeId);
    if (!Node)
    {
        return false;
    }

    if (Node->RouteId == CurrentRouteId && Node->ChapterId == CurrentChapterId)
    {
        return true;
    }

    return HasKnownMapRegion(MakeKnownMapRegionId(Node->RouteId, Node->ChapterId));
}

FName UShireQuestSubsystem::GetCurrentWorldMapNodeId() const
{
    for (const FShireWorldMapNodeDefinition& Node : WorldMapNodes)
    {
        if (Node.RouteId == CurrentRouteId &&
            Node.ChapterId == CurrentChapterId &&
            Node.bChapterAnchor)
        {
            return Node.NodeId;
        }
    }

    for (const FShireWorldMapNodeDefinition& Node : WorldMapNodes)
    {
        if (Node.RouteId == CurrentRouteId && Node.ChapterId == CurrentChapterId)
        {
            return Node.NodeId;
        }
    }
    return NAME_None;
}


bool UShireQuestSubsystem::LoadSideActivityPlan()
{
    SideActivityProgressionDefinitions.Empty();
    SideActivityDefinitionsById.Empty();

    const FString Path = FPaths::Combine(FPaths::ProjectDir(), TEXT("Data/ContextualSideActivityPlan.json"));
    FString JsonText;
    if (!FFileHelper::LoadFileToString(JsonText, *Path))
    {
        UE_LOG(LogTemp, Error, TEXT("SideActivityRuntime: failed to read %s"), *Path);
        return false;
    }

    TSharedPtr<FJsonObject> Root;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonText);
    if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("SideActivityRuntime: invalid JSON %s"), *Path);
        return false;
    }

    const TArray<TSharedPtr<FJsonValue>>* Chapters = nullptr;
    if (Root->TryGetArrayField(TEXT("chapters"), Chapters) && Chapters)
    {
        for (const TSharedPtr<FJsonValue>& ChapterValue : *Chapters)
        {
            const TSharedPtr<FJsonObject> Chapter = ChapterValue.IsValid() ? ChapterValue->AsObject() : nullptr;
            if (!Chapter.IsValid()) continue;

            FString RouteId;
            FString ChapterId;
            Chapter->TryGetStringField(TEXT("route"), RouteId);
            Chapter->TryGetStringField(TEXT("chapter"), ChapterId);
            if (RouteId.IsEmpty() || ChapterId.IsEmpty())
            {
                UE_LOG(LogTemp, Error, TEXT("SideActivityRuntime: chapter entry missing route/chapter"));
                continue;
            }

            const TArray<TSharedPtr<FJsonValue>>* Activities = nullptr;
            if (!Chapter->TryGetArrayField(TEXT("activities"), Activities) || !Activities) continue;

            for (const TSharedPtr<FJsonValue>& ActivityValue : *Activities)
            {
                const TSharedPtr<FJsonObject> Activity = ActivityValue.IsValid() ? ActivityValue->AsObject() : nullptr;
                if (!Activity.IsValid()) continue;

                FString DiscoveryId;
                FString ActivityId;
                FString ActivityType;
                FString AvailableAfter;
                FString EndsBefore;
                Activity->TryGetStringField(TEXT("discovery_reward_id"), DiscoveryId);
                Activity->TryGetStringField(TEXT("id"), ActivityId);
                Activity->TryGetStringField(TEXT("type"), ActivityType);
                Activity->TryGetStringField(TEXT("available_after"), AvailableAfter);
                Activity->TryGetStringField(TEXT("ends_before"), EndsBefore);

                bool bMayAdvanceRequiredAnchor = false;
                bool bMayChangeCanonOutcome = false;
                bool bFutureKnowledgeAllowed = false;
                Activity->TryGetBoolField(TEXT("may_advance_required_anchor"), bMayAdvanceRequiredAnchor);
                Activity->TryGetBoolField(TEXT("may_change_canon_outcome"), bMayChangeCanonOutcome);
                Activity->TryGetBoolField(TEXT("future_knowledge_allowed"), bFutureKnowledgeAllowed);

                if (DiscoveryId.IsEmpty() || ActivityId.IsEmpty() || ActivityType.IsEmpty() ||
                    AvailableAfter.IsEmpty() || EndsBefore.IsEmpty())
                {
                    UE_LOG(LogTemp, Error, TEXT("SideActivityRuntime: incomplete activity contract route=%s chapter=%s"),
                        *RouteId, *ChapterId);
                    continue;
                }

                if (bMayAdvanceRequiredAnchor || bMayChangeCanonOutcome || bFutureKnowledgeAllowed)
                {
                    UE_LOG(LogTemp, Error, TEXT("SideActivityRuntime: rejected canon-unsafe activity id=%s"), *ActivityId);
                    continue;
                }

                const FName DiscoveryName(*DiscoveryId);
                const FName ActivityName(*ActivityId);
                const FName RouteName(*RouteId);
                const FName ChapterName(*ChapterId);
                const FShireJourneyDiscoveryDefinition* Discovery = JourneyDiscoveryDefinitions.Find(DiscoveryName);
                if (!Discovery || Discovery->RouteId != RouteName || Discovery->ChapterId != ChapterName)
                {
                    UE_LOG(LogTemp, Error,
                        TEXT("SideActivityRuntime: reward mismatch activity=%s discovery=%s route=%s chapter=%s"),
                        *ActivityId, *DiscoveryId, *RouteId, *ChapterId);
                    continue;
                }

                if (SideActivityProgressionDefinitions.Contains(DiscoveryName) ||
                    SideActivityDefinitionsById.Contains(ActivityName))
                {
                    UE_LOG(LogTemp, Error, TEXT("SideActivityRuntime: duplicate activity/reward id=%s discovery=%s"),
                        *ActivityId, *DiscoveryId);
                    continue;
                }

                FShireSideActivityProgressionDefinition Definition;
                Definition.DiscoveryId = DiscoveryName;
                Definition.ActivityId = ActivityName;
                Definition.ActivityType = FName(*ActivityType);
                Definition.RouteId = RouteName;
                Definition.ChapterId = ChapterName;
                Definition.AvailableAfterStoryBeat = FName(*AvailableAfter);
                Definition.EndsBeforeStoryBeat = FName(*EndsBefore);
                SideActivityProgressionDefinitions.Add(Definition.DiscoveryId, Definition);
                SideActivityDefinitionsById.Add(Definition.ActivityId, Definition);
            }
        }
    }

    const bool bReady = SideActivityProgressionDefinitions.Num() > 0 &&
        SideActivityProgressionDefinitions.Num() == SideActivityDefinitionsById.Num();
    if (bReady)
    {
        UE_LOG(LogTemp, Display,
            TEXT("SideActivityRuntime: ready=yes activities=%d mappedDiscoveries=%d"),
            SideActivityDefinitionsById.Num(),
            SideActivityProgressionDefinitions.Num());
    }
    else
    {
        UE_LOG(LogTemp, Error,
            TEXT("SideActivityRuntime: ready=no activities=%d mappedDiscoveries=%d"),
            SideActivityDefinitionsById.Num(),
            SideActivityProgressionDefinitions.Num());
    }
    return bReady;
}

bool UShireQuestSubsystem::IsSideActivityDefinitionAvailable(
    const FShireSideActivityProgressionDefinition& Definition) const
{
    if (Definition.RouteId != CurrentRouteId || Definition.ChapterId != CurrentChapterId) return false;
    if (Definition.AvailableAfterStoryBeat != NAME_None &&
        !HasStoryBeatTriggered(Definition.AvailableAfterStoryBeat)) return false;
    if (Definition.EndsBeforeStoryBeat != NAME_None &&
        HasStoryBeatTriggered(Definition.EndsBeforeStoryBeat)) return false;
    return !JourneyDiscoveryIds.Contains(Definition.DiscoveryId);
}

bool UShireQuestSubsystem::HasSideActivityForDiscovery(FName DiscoveryId) const
{
    return DiscoveryId != NAME_None && SideActivityProgressionDefinitions.Contains(DiscoveryId);
}

bool UShireQuestSubsystem::IsSideActivityAvailable(FName ActivityId) const
{
    const FShireSideActivityProgressionDefinition* Definition = SideActivityDefinitionsById.Find(ActivityId);
    return Definition && IsSideActivityDefinitionAvailable(*Definition);
}

bool UShireQuestSubsystem::IsSideActivityDiscoveryAvailable(FName DiscoveryId) const
{
    const FShireSideActivityProgressionDefinition* Definition = SideActivityProgressionDefinitions.Find(DiscoveryId);
    return Definition && IsSideActivityDefinitionAvailable(*Definition);
}

FName UShireQuestSubsystem::GetSideActivityIdForDiscovery(FName DiscoveryId) const
{
    const FShireSideActivityProgressionDefinition* Definition = SideActivityProgressionDefinitions.Find(DiscoveryId);
    return Definition ? Definition->ActivityId : NAME_None;
}

bool UShireQuestSubsystem::CompleteSideActivityDiscovery(FName DiscoveryId)
{
    if (!HasSideActivityForDiscovery(DiscoveryId) || !IsSideActivityDiscoveryAvailable(DiscoveryId))
    {
        return false;
    }

    bSideActivityRewardInProgress = true;
    const bool bCompleted = RegisterJourneyDiscovery(DiscoveryId);
    bSideActivityRewardInProgress = false;
    return bCompleted;
}

FName UShireQuestSubsystem::MakeChronicleEntryId(FName DiscoveryId)
{
    return FName(*FString::Printf(TEXT("CHRONICLE_%s"), *DiscoveryId.ToString()));
}

FName UShireQuestSubsystem::MakeKnownMapRegionId(FName RouteId, FName ChapterId)
{
    return FName(*FString::Printf(TEXT("MAP_REGION_%s_%s"), *RouteId.ToString(), *ChapterId.ToString()));
}

void UShireQuestSubsystem::UnlockDiscoveryKnowledge(const FShireJourneyDiscoveryDefinition& Definition)
{
    ChronicleEntryIds.AddUnique(MakeChronicleEntryId(Definition.DiscoveryId));
    KnownMapRegionIds.AddUnique(MakeKnownMapRegionId(Definition.RouteId, Definition.ChapterId));
}

void UShireQuestSubsystem::AwardSideActivityProgression(FName DiscoveryId)
{
    const FShireSideActivityProgressionDefinition* Activity = SideActivityProgressionDefinitions.Find(DiscoveryId);
    if (!Activity)
    {
        return;
    }

    if (Activity->ActivityType == TEXT("CAMP_PREPARATION"))
    {
        AwardProgressionXP(TEXT("CAMPCRAFT"), 12);
    }
    else if (Activity->ActivityType == TEXT("STEALTH_LITE"))
    {
        AwardProgressionXP(TEXT("QUIET_STEP"), 12);
    }
    else if (Activity->ActivityType == TEXT("TRAVERSAL_CHALLENGE") ||
             Activity->ActivityType == TEXT("ROUTE_READING"))
    {
        AwardProgressionXP(TEXT("WAYFINDING"), 6);
    }
    else if (Activity->ActivityType == TEXT("TRACKING_CHALLENGE") ||
             Activity->ActivityType == TEXT("OBSERVATION_CHALLENGE"))
    {
        AwardProgressionXP(TEXT("PERCEPTION"), 6);
    }
    else if (Activity->ActivityType == TEXT("PATTERN_MATCH"))
    {
        AwardProgressionXP(TEXT("LORE"), 6);
    }
    else if (Activity->ActivityType == TEXT("SOCIAL_MEMORY"))
    {
        AwardProgressionXP(TEXT("FELLOWSHIP"), 6);
    }
    else if (Activity->ActivityType == TEXT("TIMING_CHALLENGE"))
    {
        AwardProgressionXP(TEXT("RESOLVE"), 4);
    }
}

FString UShireQuestSubsystem::GetChronicleEntryDisplayLabel(FName EntryId) const
{
    FString DiscoveryString = EntryId.ToString();
    if (!DiscoveryString.RemoveFromStart(TEXT("CHRONICLE_")))
    {
        return EntryId.ToString();
    }
    const FShireJourneyDiscoveryDefinition* Definition =
        JourneyDiscoveryDefinitions.Find(FName(*DiscoveryString));
    if (Definition && !Definition->DisplayLabel.IsEmpty())
    {
        return Definition->DisplayLabel;
    }
    DiscoveryString.ReplaceInline(TEXT("_"), TEXT(" "));
    return DiscoveryString;
}

FString UShireQuestSubsystem::GetChronicleEntryContextLabel(FName EntryId) const
{
    FString DiscoveryString = EntryId.ToString();
    if (!DiscoveryString.RemoveFromStart(TEXT("CHRONICLE_")))
    {
        return FString();
    }

    const FShireJourneyDiscoveryDefinition* Definition =
        JourneyDiscoveryDefinitions.Find(FName(*DiscoveryString));
    if (!Definition)
    {
        return FString();
    }

    FString Category = Definition->CategoryId.ToString();
    Category.ReplaceInline(TEXT("_"), TEXT(" "));
    const FShireChapterProductionDefinition* Chapter =
        FindChapterProductionDefinition(Definition->RouteId, Definition->ChapterId);
    const FString Region = Chapter ? Chapter->PrimaryRegion : Definition->RegionId.ToString();
    return FString::Printf(TEXT("%s  |  %s"), *Region, *Category);
}

FString UShireQuestSubsystem::GetKnownMapRegionDisplayLabel(FName RegionId) const
{
    for (const TPair<FName, FShireJourneyDiscoveryDefinition>& Pair : JourneyDiscoveryDefinitions)
    {
        const FShireJourneyDiscoveryDefinition& Definition = Pair.Value;
        if (MakeKnownMapRegionId(Definition.RouteId, Definition.ChapterId) == RegionId)
        {
            const FShireChapterProductionDefinition* Chapter =
                FindChapterProductionDefinition(Definition.RouteId, Definition.ChapterId);
            if (Chapter)
            {
                return FString::Printf(
                    TEXT("%s  |  %s"),
                    *Chapter->PrimaryRegion,
                    *Chapter->DisplayName);
            }

            return FString::Printf(
                TEXT("%s  |  %s"),
                *Definition.RegionId.ToString(),
                *Definition.ChapterId.ToString());
        }
    }

    FString Label = RegionId.ToString();
    Label.RemoveFromStart(TEXT("MAP_REGION_"));
    Label.ReplaceInline(TEXT("_"), TEXT(" / "));
    return Label;
}

void UShireQuestSubsystem::RestoreKnowledgeState(
    const TArray<FName>& InChronicleEntryIds,
    const TArray<FName>& InKnownMapRegionIds)
{
    ChronicleEntryIds.Empty();
    KnownMapRegionIds.Empty();

    for (const FName EntryId : InChronicleEntryIds)
    {
        if (EntryId != NAME_None && EntryId.ToString().StartsWith(TEXT("CHRONICLE_")))
        {
            ChronicleEntryIds.AddUnique(EntryId);
        }
    }
    for (const FName RegionId : InKnownMapRegionIds)
    {
        if (RegionId != NAME_None && RegionId.ToString().StartsWith(TEXT("MAP_REGION_")))
        {
            KnownMapRegionIds.AddUnique(RegionId);
        }
    }
}

FName UShireQuestSubsystem::MakeJourneyRegionCompletionId(FName RouteId, FName ChapterId) const
{
    return FName(*FString::Printf(
        TEXT("REGION_COMPLETE_%s_%s"),
        *RouteId.ToString(),
        *ChapterId.ToString()));
}

void UShireQuestSubsystem::RebuildJourneyInsightState()
{
    TArray<FName> SanitizedDiscoveries;
    SanitizedDiscoveries.Reserve(JourneyDiscoveryIds.Num());
    JourneyInsight = 0;

    for (const FName DiscoveryId : JourneyDiscoveryIds)
    {
        const FShireJourneyDiscoveryDefinition* Definition = JourneyDiscoveryDefinitions.Find(DiscoveryId);
        if (Definition && !SanitizedDiscoveries.Contains(DiscoveryId))
        {
            SanitizedDiscoveries.Add(DiscoveryId);
            JourneyInsight += Definition->Insight;
        }
    }
    JourneyDiscoveryIds = MoveTemp(SanitizedDiscoveries);
    JourneyInsightMilestones.Empty();

    for (const FShireJourneyRegionBonusDefinition& Region : JourneyRegionBonusDefinitions)
    {
        int32 Found = 0;
        for (const FName DiscoveryId : JourneyDiscoveryIds)
        {
            const FShireJourneyDiscoveryDefinition* Definition = JourneyDiscoveryDefinitions.Find(DiscoveryId);
            if (Definition && Definition->RouteId == Region.RouteId && Definition->ChapterId == Region.ChapterId)
            {
                ++Found;
            }
        }

        if (Found >= Region.RequiredDiscoveries)
        {
            JourneyInsight += Region.BonusInsight;
            JourneyInsightMilestones.AddUnique(MakeJourneyRegionCompletionId(Region.RouteId, Region.ChapterId));
        }
    }

    for (const FShireJourneyInsightMilestoneDefinition& Milestone : JourneyInsightDefinitions)
    {
        if (JourneyInsight >= Milestone.Threshold)
        {
            JourneyInsightMilestones.AddUnique(Milestone.MilestoneId);
        }
    }
}

bool UShireQuestSubsystem::RegisterJourneyDiscovery(FName DiscoveryId)
{
    if (DiscoveryId == NAME_None || JourneyDiscoveryIds.Contains(DiscoveryId))
    {
        return false;
    }

    const FShireJourneyDiscoveryDefinition* Definition = JourneyDiscoveryDefinitions.Find(DiscoveryId);
    if (!Definition)
    {
        UE_LOG(LogTemp, Warning, TEXT("JourneyDiscovery: unknown id=%s"), *DiscoveryId.ToString());
        return false;
    }

    if (Definition->RouteId != CurrentRouteId || Definition->ChapterId != CurrentChapterId)
    {
        UE_LOG(
            LogTemp,
            Warning,
            TEXT("JourneyDiscovery: rejected id=%s expected=%s/%s current=%s/%s"),
            *DiscoveryId.ToString(),
            *Definition->RouteId.ToString(),
            *Definition->ChapterId.ToString(),
            *CurrentRouteId.ToString(),
            *CurrentChapterId.ToString());
        return false;
    }

    if (HasSideActivityForDiscovery(DiscoveryId))
    {
        if (!bSideActivityRewardInProgress)
        {
            UE_LOG(LogTemp, Warning,
                TEXT("SideActivityRuntime: rejected direct reward bypass activity=%s discovery=%s"),
                *GetSideActivityIdForDiscovery(DiscoveryId).ToString(),
                *DiscoveryId.ToString());
            return false;
        }

        if (!IsSideActivityDiscoveryAvailable(DiscoveryId))
        {
            UE_LOG(LogTemp, Warning,
                TEXT("SideActivityRuntime: rejected reward outside window activity=%s discovery=%s route=%s chapter=%s"),
                *GetSideActivityIdForDiscovery(DiscoveryId).ToString(),
                *DiscoveryId.ToString(),
                *CurrentRouteId.ToString(),
                *CurrentChapterId.ToString());
            return false;
        }
    }

    const int32 Before = JourneyInsight;
    JourneyDiscoveryIds.Add(DiscoveryId);
    RebuildJourneyInsightState();
    AwardDiscoveryProgression(*Definition);
    AwardSideActivityProgression(DiscoveryId);
    UnlockDiscoveryKnowledge(*Definition);

    UE_LOG(
        LogTemp,
        Display,
        TEXT("JourneyDiscovery: id=%s awarded=%d total=%d route=%s chapter=%s"),
        *DiscoveryId.ToString(),
        JourneyInsight - Before,
        JourneyInsight,
        *CurrentRouteId.ToString(),
        *CurrentChapterId.ToString());
    return true;
}

bool UShireQuestSubsystem::HasJourneyDiscovery(FName DiscoveryId) const
{
    return DiscoveryId != NAME_None && JourneyDiscoveryIds.Contains(DiscoveryId);
}

int32 UShireQuestSubsystem::GetJourneyInsight() const
{
    return JourneyInsight;
}

bool UShireQuestSubsystem::IsValidProgressionTrack(FName TrackId)
{
    return TrackId == TEXT("WAYFINDING") || TrackId == TEXT("PERCEPTION") ||
        TrackId == TEXT("QUIET_STEP") || TrackId == TEXT("CAMPCRAFT") ||
        TrackId == TEXT("FELLOWSHIP") || TrackId == TEXT("LORE") ||
        TrackId == TEXT("RESOLVE");
}

void UShireQuestSubsystem::AwardProgressionXP(FName TrackId, int32 Amount)
{
    if (!IsValidProgressionTrack(TrackId) || Amount <= 0) return;
    int32& XP = ProgressionXP.FindOrAdd(TrackId);
    XP = FMath::Clamp(XP + Amount, 0, 999);
}

int32 UShireQuestSubsystem::GetProgressionXP(FName TrackId) const
{
    const int32* XP = ProgressionXP.Find(TrackId);
    return XP ? FMath::Max(0, *XP) : 0;
}

int32 UShireQuestSubsystem::GetProgressionRank(FName TrackId) const
{
    const int32 XP = GetProgressionXP(TrackId);
    if (XP >= 200) return 4;
    if (XP >= 120) return 3;
    if (XP >= 60) return 2;
    if (XP >= 25) return 1;
    return 0;
}

int32 UShireQuestSubsystem::GetFellowshipBond() const
{
    return FMath::Clamp(GetProgressionXP(TEXT("FELLOWSHIP")), 0, 100);
}

void UShireQuestSubsystem::AwardDiscoveryProgression(const FShireJourneyDiscoveryDefinition& Definition)
{
    if (Definition.CategoryId == TEXT("ROAD_WISDOM"))
    {
        AwardProgressionXP(TEXT("WAYFINDING"), 10);
        AwardProgressionXP(TEXT("PERCEPTION"), 4);
    }
    else if (Definition.CategoryId == TEXT("PEOPLES_AND_PLACES"))
    {
        AwardProgressionXP(TEXT("LORE"), 10);
    }
    else if (Definition.CategoryId == TEXT("FELLOWSHIP_BONDS"))
    {
        AwardProgressionXP(TEXT("FELLOWSHIP"), 10);
    }
    else if (Definition.CategoryId == TEXT("PERIL_SENSE"))
    {
        AwardProgressionXP(TEXT("PERCEPTION"), 8);
        AwardProgressionXP(TEXT("RESOLVE"), 6);
    }
}

void UShireQuestSubsystem::RestoreProgressionState(const TMap<FName, int32>& InProgressionXP)
{
    ProgressionXP.Empty();
    for (const TPair<FName, int32>& Pair : InProgressionXP)
    {
        if (IsValidProgressionTrack(Pair.Key) && Pair.Value > 0)
        {
            ProgressionXP.Add(Pair.Key, FMath::Clamp(Pair.Value, 0, 999));
        }
    }
}

bool UShireQuestSubsystem::HasJourneyInsightMilestone(FName MilestoneId) const
{
    return MilestoneId != NAME_None && JourneyInsightMilestones.Contains(MilestoneId);
}

void UShireQuestSubsystem::RestoreJourneyDiscoveryState(
    const TArray<FName>& InDiscoveryIds,
    int32 SavedJourneyInsight,
    const TArray<FName>& InMilestones)
{
    JourneyDiscoveryIds = InDiscoveryIds;
    RebuildJourneyInsightState();

    if (SavedJourneyInsight != JourneyInsight)
    {
        UE_LOG(
            LogTemp,
            Warning,
            TEXT("JourneyDiscovery: sanitized saved insight from %d to derived %d"),
            SavedJourneyInsight,
            JourneyInsight);
    }

    for (const FName SavedMilestone : InMilestones)
    {
        if (SavedMilestone != NAME_None && !JourneyInsightMilestones.Contains(SavedMilestone))
        {
            UE_LOG(
                LogTemp,
                Verbose,
                TEXT("JourneyDiscovery: ignored stale milestone %s during restore"),
                *SavedMilestone.ToString());
        }
    }
}

int32 UShireQuestSubsystem::GetActiveQuestStage() const
{
    return GetQuestStage(ActiveQuestId);
}

FText UShireQuestSubsystem::GetActiveQuestTitle() const
{
    if (const FShireQuestDefinition* Definition = QuestDefinitions.Find(ActiveQuestId))
    {
        return Definition->Title;
    }
    return FText::FromString(TEXT("The Journey"));
}

FText UShireQuestSubsystem::GetActiveObjective() const
{
    if (const FShireQuestDefinition* Definition = QuestDefinitions.Find(ActiveQuestId))
    {
        if (Definition->Objectives.Num() > 0)
        {
            const int32 Index = FMath::Clamp(GetActiveQuestStage(), 0, Definition->Objectives.Num() - 1);
            return Definition->Objectives[Index];
        }
    }
    return FText::FromString(TEXT("Explore the road ahead."));
}

void UShireQuestSubsystem::RestoreQuestState(const TMap<FName, int32>& InStages, FName InActiveQuestId,
    FName InCurrentChapterId, const TArray<FName>& InCompletedStoryBeats,
    FName InCurrentRouteId, FName InCurrentEpisodeId, FName InPlayableCharacterId,
    const TMap<FName, FShireRouteProgress>& InRouteProgress)
{
    QuestStages = InStages;
    ActiveQuestId = InActiveQuestId;
    CurrentChapterId = InCurrentChapterId == NAME_None ? FName(TEXT("P1C01")) : InCurrentChapterId;
    CompletedStoryBeats = InCompletedStoryBeats;
    CurrentRouteId = InCurrentRouteId == NAME_None ? FName(TEXT("FrodoMain")) : InCurrentRouteId;
    CurrentEpisodeId = InCurrentEpisodeId == NAME_None
        ? FName(*FString::Printf(TEXT("%s_Main"), *CurrentChapterId.ToString()))
        : InCurrentEpisodeId;
    PlayableCharacterId = InPlayableCharacterId == NAME_None ? FName(TEXT("Frodo")) : InPlayableCharacterId;
    RouteProgress = InRouteProgress;

    if (QuestDefinitions.Num() == 0)
    {
        BuildQuestDefinitions();
    }

    if (!bPersistenceRestoreInProgress)
    {
        OnExperienceChanged.Broadcast(CurrentRouteId, CurrentEpisodeId, PlayableCharacterId);
        OnChapterChanged.Broadcast(NAME_None, CurrentChapterId);
        OnActiveQuestChanged.Broadcast(ActiveQuestId);
        for (const TPair<FName, int32>& Pair : QuestStages)
        {
            OnQuestStageChanged.Broadcast(Pair.Key, Pair.Value);
        }

        OnQuestStateRestored.Broadcast();
    }
}

FName UShireQuestSubsystem::ResolveCanonicalNPCProfile(FName ProfileHint) const
{
    if (ProfileHint == NAME_None)
    {
        return NAME_None;
    }

    const UGameInstance* GI = GetGameInstance();
    const UShireNPCContextSubsystem* Context =
        GI ? GI->GetSubsystem<UShireNPCContextSubsystem>() : nullptr;
    if (Context)
    {
        const FName Canonical = Context->ResolveCanonicalProfileId(ProfileHint);
        if (Canonical != NAME_None)
        {
            return Canonical;
        }
    }
    return ProfileHint;
}

int32 UShireQuestSubsystem::ResolvePersistentMemoryBudget(FName ProfileHint) const
{
    const UGameInstance* GI = GetGameInstance();
    const UShireNPCContextSubsystem* Context =
        GI ? GI->GetSubsystem<UShireNPCContextSubsystem>() : nullptr;
    if (Context)
    {
        return Context->GetPersistentMemoryBudget(ProfileHint);
    }
    return 12;
}

int32 UShireQuestSubsystem::ResolveRelationshipBudget(FName ProfileHint) const
{
    const UGameInstance* GI = GetGameInstance();
    const UShireNPCContextSubsystem* Context =
        GI ? GI->GetSubsystem<UShireNPCContextSubsystem>() : nullptr;
    if (Context)
    {
        return Context->GetRelationshipBudget(ProfileHint);
    }
    return 8;
}

int32 UShireQuestSubsystem::ChapterOrdinal(FName ChapterId)
{
    const FString Value = ChapterId.ToString();
    if (Value.StartsWith(TEXT("P1C")) && Value.Len() >= 5)
    {
        return FCString::Atoi(*Value.Mid(3));
    }
    return -1;
}

FName UShireQuestSubsystem::MakeNPCMemoryKey(FName CanonicalProfileId) const
{
    const FName ResolvedProfileId = ResolveCanonicalNPCProfile(CanonicalProfileId);
    if (ResolvedProfileId == NAME_None || CurrentRouteId == NAME_None)
    {
        return NAME_None;
    }

    return FName(*FString::Printf(
        TEXT("%s|%s"),
        *CurrentRouteId.ToString(),
        *ResolvedProfileId.ToString()));
}

bool UShireQuestSubsystem::RememberNamedNPCEvent(
    FName CanonicalProfileId,
    FName EventId,
    int32 Priority)
{
    const FName ResolvedProfileId = ResolveCanonicalNPCProfile(CanonicalProfileId);
    const int32 Budget = ResolvePersistentMemoryBudget(ResolvedProfileId);
    const FName Key = MakeNPCMemoryKey(ResolvedProfileId);
    if (Key == NAME_None || EventId == NAME_None || Budget <= 0)
    {
        return false;
    }

    FShireNPCMemoryBucket& Bucket = NPCMemoryState.FindOrAdd(Key);
    Bucket.CanonicalProfileId = ResolvedProfileId;
    Bucket.RouteId = CurrentRouteId;

    for (FShireNPCMemoryEvent& Existing : Bucket.Events)
    {
        if (Existing.EventId == EventId)
        {
            Existing.ChapterId = CurrentChapterId;
            Existing.Priority = FMath::Max(Existing.Priority, FMath::Clamp(Priority, 0, 100));
            return true;
        }
    }

    FShireNPCMemoryEvent Memory;
    Memory.EventId = EventId;
    Memory.ChapterId = CurrentChapterId;
    Memory.Priority = FMath::Clamp(Priority, 0, 100);
    Bucket.Events.Add(Memory);

    while (Bucket.Events.Num() > Budget)
    {
        int32 LowestIndex = 0;
        for (int32 Index = 1; Index < Bucket.Events.Num(); ++Index)
        {
            if (Bucket.Events[Index].Priority < Bucket.Events[LowestIndex].Priority)
            {
                LowestIndex = Index;
            }
        }
        Bucket.Events.RemoveAt(LowestIndex);
    }

    return true;
}

bool UShireQuestSubsystem::HasNamedNPCMemory(
    FName CanonicalProfileId,
    FName EventId) const
{
    const FName Key = MakeNPCMemoryKey(CanonicalProfileId);
    const FShireNPCMemoryBucket* Bucket = NPCMemoryState.Find(Key);
    if (!Bucket || EventId == NAME_None)
    {
        return false;
    }

    for (const FShireNPCMemoryEvent& Memory : Bucket->Events)
    {
        if (Memory.EventId == EventId)
        {
            return true;
        }
    }
    return false;
}

int32 UShireQuestSubsystem::AdjustNamedNPCRelationship(
    FName CanonicalProfileId,
    FName OtherProfileId,
    int32 Delta)
{
    const FName ResolvedProfileId = ResolveCanonicalNPCProfile(CanonicalProfileId);
    const FName ResolvedOtherId = ResolveCanonicalNPCProfile(OtherProfileId);
    const int32 Budget = ResolveRelationshipBudget(ResolvedProfileId);
    const FName Key = MakeNPCMemoryKey(ResolvedProfileId);
    if (Key == NAME_None || ResolvedOtherId == NAME_None || Delta == 0 || Budget <= 0)
    {
        return 0;
    }

    FShireNPCMemoryBucket& Bucket = NPCMemoryState.FindOrAdd(Key);
    Bucket.CanonicalProfileId = ResolvedProfileId;
    Bucket.RouteId = CurrentRouteId;

    if (!Bucket.RelationshipDeltas.Contains(ResolvedOtherId) &&
        Bucket.RelationshipDeltas.Num() >= Budget)
    {
        return 0;
    }

    int32& Value = Bucket.RelationshipDeltas.FindOrAdd(ResolvedOtherId);
    Value = FMath::Clamp(Value + Delta, -100, 100);
    return Value;
}

int32 UShireQuestSubsystem::GetNamedNPCRelationship(
    FName CanonicalProfileId,
    FName OtherProfileId) const
{
    const FName ResolvedOtherId = ResolveCanonicalNPCProfile(OtherProfileId);
    const FName Key = MakeNPCMemoryKey(CanonicalProfileId);
    const FShireNPCMemoryBucket* Bucket = NPCMemoryState.Find(Key);
    if (!Bucket || ResolvedOtherId == NAME_None)
    {
        return 0;
    }

    if (const int32* Value = Bucket->RelationshipDeltas.Find(ResolvedOtherId))
    {
        return *Value;
    }
    return 0;
}

bool UShireQuestSubsystem::HasRecentNPCDialogueVariant(
    FName CanonicalProfileId,
    FName VariantId) const
{
    const FName Key = MakeNPCMemoryKey(CanonicalProfileId);
    const FShireNPCMemoryBucket* Bucket = NPCMemoryState.Find(Key);
    return Bucket && VariantId != NAME_None && Bucket->RecentDialogueVariantIds.Contains(VariantId);
}

void UShireQuestSubsystem::RecordNamedNPCDialogueUse(
    FName CanonicalProfileId,
    FName VariantId,
    FName PartnerProfileId,
    int32 MaxRecentVariants)
{
    const FName ResolvedProfileId = ResolveCanonicalNPCProfile(CanonicalProfileId);
    const FName Key = MakeNPCMemoryKey(ResolvedProfileId);
    if (Key == NAME_None || ResolvePersistentMemoryBudget(ResolvedProfileId) <= 0)
    {
        return;
    }

    FShireNPCMemoryBucket& Bucket = NPCMemoryState.FindOrAdd(Key);
    Bucket.CanonicalProfileId = ResolvedProfileId;
    Bucket.RouteId = CurrentRouteId;

    if (VariantId != NAME_None)
    {
        Bucket.RecentDialogueVariantIds.Remove(VariantId);
        Bucket.RecentDialogueVariantIds.Add(VariantId);
        while (Bucket.RecentDialogueVariantIds.Num() > FMath::Clamp(MaxRecentVariants, 4, 24))
        {
            Bucket.RecentDialogueVariantIds.RemoveAt(0);
        }
    }

    const FName ResolvedPartner = ResolveCanonicalNPCProfile(PartnerProfileId);
    if (ResolvedPartner != NAME_None)
    {
        Bucket.RecentPartnerIds.Remove(ResolvedPartner);
        Bucket.RecentPartnerIds.Add(ResolvedPartner);
        while (Bucket.RecentPartnerIds.Num() > 4)
        {
            Bucket.RecentPartnerIds.RemoveAt(0);
        }
    }
}

void UShireQuestSubsystem::CommitWorldBoundState()
{
    PruneNPCMemoryForCurrentChapter();
    UE_LOG(
        LogTemp,
        Verbose,
        TEXT("ShireQuestCommit: world-bound-state chapter=%s route=%s"),
        *CurrentChapterId.ToString(),
        *CurrentRouteId.ToString());
}

void UShireQuestSubsystem::PruneNPCMemoryForCurrentChapter()
{
    const int32 CurrentOrdinal = ChapterOrdinal(CurrentChapterId);
    if (CurrentOrdinal < 0)
    {
        return;
    }

    for (TPair<FName, FShireNPCMemoryBucket>& Pair : NPCMemoryState)
    {
        FShireNPCMemoryBucket& Bucket = Pair.Value;
        for (int32 Index = Bucket.Events.Num() - 1; Index >= 0; --Index)
        {
            const FShireNPCMemoryEvent& Event = Bucket.Events[Index];
            const int32 EventOrdinal = ChapterOrdinal(Event.ChapterId);
            const bool bProtected = Event.Priority >= 80;
            if (!bProtected && EventOrdinal >= 0 && CurrentOrdinal - EventOrdinal > 2)
            {
                Bucket.Events.RemoveAt(Index);
            }
        }
    }
}

void UShireQuestSubsystem::RecordStoryBeatForEligibleNPCs(FName StoryBeatId)
{
    UGameInstance* GI = GetGameInstance();
    UShireNPCContextSubsystem* Context =
        GI ? GI->GetSubsystem<UShireNPCContextSubsystem>() : nullptr;
    if (!Context || StoryBeatId == NAME_None)
    {
        return;
    }

    const TArray<FName> ProfilesInChapter = Context->GetNamedProfilesForCurrentChapter();
    for (const FName ProfileId : ProfilesInChapter)
    {
        if (Context->HasKnowledgeTag(ProfileId, TEXT("MAIN_STORY_CONTEXT")))
        {
            RememberNamedNPCEvent(ProfileId, StoryBeatId, 90);
        }
    }
}

void UShireQuestSubsystem::RestoreNPCMemoryState(
    const TMap<FName, FShireNPCMemoryBucket>& InState)
{
    NPCMemoryState.Empty();

    for (const TPair<FName, FShireNPCMemoryBucket>& Pair : InState)
    {
        FShireNPCMemoryBucket Bucket = Pair.Value;
        const FName CanonicalProfileId = ResolveCanonicalNPCProfile(Bucket.CanonicalProfileId);
        if (CanonicalProfileId == NAME_None || Bucket.RouteId == NAME_None)
        {
            continue;
        }

        Bucket.CanonicalProfileId = CanonicalProfileId;
        const int32 EventBudget = ResolvePersistentMemoryBudget(CanonicalProfileId);
        const int32 RelationshipBudget = ResolveRelationshipBudget(CanonicalProfileId);
        if (EventBudget <= 0)
        {
            continue;
        }

        while (Bucket.Events.Num() > EventBudget)
        {
            int32 LowestIndex = 0;
            for (int32 Index = 1; Index < Bucket.Events.Num(); ++Index)
            {
                if (Bucket.Events[Index].Priority < Bucket.Events[LowestIndex].Priority)
                {
                    LowestIndex = Index;
                }
            }
            Bucket.Events.RemoveAt(LowestIndex);
        }

        TMap<FName, int32> CanonicalRelationships;
        for (const TPair<FName, int32>& Relationship : Bucket.RelationshipDeltas)
        {
            if (CanonicalRelationships.Num() >= RelationshipBudget)
            {
                break;
            }
            const FName CanonicalOther = ResolveCanonicalNPCProfile(Relationship.Key);
            if (CanonicalOther != NAME_None)
            {
                CanonicalRelationships.Add(
                    CanonicalOther,
                    FMath::Clamp(Relationship.Value, -100, 100));
            }
        }
        Bucket.RelationshipDeltas = MoveTemp(CanonicalRelationships);

        while (Bucket.RecentDialogueVariantIds.Num() > 12)
        {
            Bucket.RecentDialogueVariantIds.RemoveAt(0);
        }
        while (Bucket.RecentPartnerIds.Num() > 4)
        {
            Bucket.RecentPartnerIds.RemoveAt(0);
        }

        const FName SanitizedKey(*FString::Printf(
            TEXT("%s|%s"),
            *Bucket.RouteId.ToString(),
            *Bucket.CanonicalProfileId.ToString()));
        NPCMemoryState.Add(SanitizedKey, MoveTemp(Bucket));
    }

    // During a restore transaction the final chapter may still be canonicalized by
    // StoryFlow. Prune once, at the final committed world boundary.
    if (!bPersistenceRestoreInProgress)
    {
        PruneNPCMemoryForCurrentChapter();
    }
}
