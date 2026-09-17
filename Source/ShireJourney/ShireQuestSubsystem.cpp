#include "ShireQuestSubsystem.h"

void UShireQuestSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    BuildQuestDefinitions();
    CurrentChapterId = TEXT("P1C01");
    StartQuest(TEXT("ShireArrival"), 0);
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
    OnActiveQuestChanged.Broadcast(QuestId);
    OnQuestStageChanged.Broadcast(QuestId, GetQuestStage(QuestId));
}

void UShireQuestSubsystem::StartChapter(FName ChapterId, FName StartingQuestId, int32 StartingQuestStage)
{
    if (ChapterId == NAME_None)
    {
        return;
    }

    const FName PreviousChapterId = CurrentChapterId;
    CurrentChapterId = ChapterId;

    if (PreviousChapterId != CurrentChapterId)
    {
        OnChapterChanged.Broadcast(PreviousChapterId, CurrentChapterId);
    }

    if (StartingQuestId != NAME_None)
    {
        StartQuest(StartingQuestId, StartingQuestStage);
    }
}

void UShireQuestSubsystem::TriggerStoryBeat(FName StoryBeatId)
{
    if (StoryBeatId == NAME_None || CompletedStoryBeats.Contains(StoryBeatId))
    {
        return;
    }

    CompletedStoryBeats.Add(StoryBeatId);
    OnStoryBeatTriggered.Broadcast(StoryBeatId);
}

bool UShireQuestSubsystem::HasStoryBeatTriggered(FName StoryBeatId) const
{
    return StoryBeatId != NAME_None && CompletedStoryBeats.Contains(StoryBeatId);
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
    FName InCurrentChapterId, const TArray<FName>& InCompletedStoryBeats)
{
    QuestStages = InStages;
    ActiveQuestId = InActiveQuestId;
    CurrentChapterId = InCurrentChapterId == NAME_None ? FName(TEXT("P1C01")) : InCurrentChapterId;
    CompletedStoryBeats = InCompletedStoryBeats;

    if (QuestDefinitions.Num() == 0)
    {
        BuildQuestDefinitions();
    }

    // Rebuild world/UI state, but do not rebroadcast completed story beats: cinematics should
    // remain one-time events after loading a save.
    OnChapterChanged.Broadcast(NAME_None, CurrentChapterId);
    OnActiveQuestChanged.Broadcast(ActiveQuestId);
    for (const TPair<FName, int32>& Pair : QuestStages)
    {
        OnQuestStageChanged.Broadcast(Pair.Key, Pair.Value);
    }
}
