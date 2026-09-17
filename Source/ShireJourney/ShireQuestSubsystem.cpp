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

    // Chapter 2 data is available before its world is loaded so the transition at
    // Bucklebury Ferry can be tested without spawning Bree assets into the Shire.
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
        TEXT("Decide whether to follow his warning upstairs."),
        TEXT("Prepare to leave Bree before the Riders return.")
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

void UShireQuestSubsystem::RestoreQuestState(const TMap<FName, int32>& InStages, FName InActiveQuestId, FName InCurrentChapterId)
{
    QuestStages = InStages;
    ActiveQuestId = InActiveQuestId;
    CurrentChapterId = InCurrentChapterId == NAME_None ? FName(TEXT("P1C01")) : InCurrentChapterId;

    if (QuestDefinitions.Num() == 0)
    {
        BuildQuestDefinitions();
    }

    OnChapterChanged.Broadcast(NAME_None, CurrentChapterId);
    OnActiveQuestChanged.Broadcast(ActiveQuestId);
    for (const TPair<FName, int32>& Pair : QuestStages)
    {
        OnQuestStageChanged.Broadcast(Pair.Key, Pair.Value);
    }
}
