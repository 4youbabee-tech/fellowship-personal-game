#include "ShireDialogueSubsystem.h"

#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "TimerManager.h"

void UShireDialogueSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    BuildDialogueLibrary();
}

void UShireDialogueSubsystem::Deinitialize()
{
    StopDialogue();
    DialogueLibrary.Empty();
    Super::Deinitialize();
}

void UShireDialogueSubsystem::AddSequence(FName DialogueCue, std::initializer_list<FShireDialogueLine> Lines)
{
    if (DialogueCue == NAME_None)
    {
        return;
    }

    FShireDialogueSequence Sequence;
    for (const FShireDialogueLine& Line : Lines)
    {
        Sequence.Lines.Add(Line);
    }
    DialogueLibrary.Add(DialogueCue, Sequence);
}

void UShireDialogueSubsystem::BuildDialogueLibrary()
{
    DialogueLibrary.Empty();

    // All lines are newly written for the game and intentionally avoid copying screenplay dialogue.
    AddSequence(TEXT("Dlg_BreeRingIncident"), {
        { FText::FromString(TEXT("Sam")), FText::FromString(TEXT("Frodo! Everyone is looking this way.")), TEXT("VO_Sam_BreeRing_01"), 3.2f },
        { FText::FromString(TEXT("Strider")), FText::FromString(TEXT("You have drawn the wrong kind of attention. Come with me, quietly.")), TEXT("VO_Strider_BreeRing_01"), 5.0f }
    });

    AddSequence(TEXT("Dlg_StriderWarning"), {
        { FText::FromString(TEXT("Strider")), FText::FromString(TEXT("Those riders will not stop at the gate. If they believe you are in one room, we will sleep in another.")), TEXT("VO_Strider_Warn_01"), 6.0f },
        { FText::FromString(TEXT("Frodo")), FText::FromString(TEXT("And Gandalf? We were told to meet him here.")), TEXT("VO_Frodo_Warn_01"), 4.0f },
        { FText::FromString(TEXT("Strider")), FText::FromString(TEXT("Then we leave at first light. Until then, trust no easy answer.")), TEXT("VO_Strider_Warn_02"), 5.2f }
    });

    AddSequence(TEXT("Dlg_WeathertopCamp"), {
        { FText::FromString(TEXT("Aragorn")), FText::FromString(TEXT("Keep the fire small and your voices lower. This hill remembers danger.")), TEXT("VO_Aragorn_Weathertop_01"), 5.0f },
        { FText::FromString(TEXT("Merry")), FText::FromString(TEXT("That is not the sort of thing one hopes to hear before supper.")), TEXT("VO_Merry_Weathertop_01"), 4.5f }
    });

    AddSequence(TEXT("Dlg_AfterWound"), {
        { FText::FromString(TEXT("Sam")), FText::FromString(TEXT("Stay with us, Mr. Frodo. We are not leaving you here.")), TEXT("VO_Sam_Wound_01"), 4.3f },
        { FText::FromString(TEXT("Aragorn")), FText::FromString(TEXT("We move now. The wound is worse than it looks.")), TEXT("VO_Aragorn_Wound_01"), 4.4f }
    });

    AddSequence(TEXT("Dlg_ArwenFlight"), {
        { FText::FromString(TEXT("Arwen")), FText::FromString(TEXT("Hold on. We are nearly there.")), TEXT("VO_Arwen_Ford_01"), 3.0f },
        { FText::FromString(TEXT("Frodo")), FText::FromString(TEXT("Do not let them take me.")), TEXT("VO_Frodo_Ford_01"), 3.2f }
    });

    AddSequence(TEXT("Dlg_RivendellAwakening"), {
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("You are safe for the moment. Rest has done what the road could not.")), TEXT("VO_Gandalf_Rivendell_01"), 5.2f },
        { FText::FromString(TEXT("Frodo")), FText::FromString(TEXT("I thought I had lost all of you.")), TEXT("VO_Frodo_Rivendell_01"), 4.0f }
    });

    AddSequence(TEXT("Dlg_CouncilOriginal"), {
        { FText::FromString(TEXT("Elrond")), FText::FromString(TEXT("The Ring cannot remain hidden forever. Its fate must be decided here.")), TEXT("VO_Elrond_Council_01"), 5.8f },
        { FText::FromString(TEXT("Boromir")), FText::FromString(TEXT("My people have fought beneath its shadow for years. Do not ask us to pretend its power means nothing.")), TEXT("VO_Boromir_Council_01"), 6.5f },
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("Power borrowed from that Ring would not remain ours for long.")), TEXT("VO_Gandalf_Council_01"), 5.0f }
    });

    AddSequence(TEXT("Dlg_FellowshipFormationOriginal"), {
        { FText::FromString(TEXT("Frodo")), FText::FromString(TEXT("I will carry it. I only wish I knew the road better.")), TEXT("VO_Frodo_Fellowship_01"), 4.6f },
        { FText::FromString(TEXT("Sam")), FText::FromString(TEXT("Then you will not learn it alone.")), TEXT("VO_Sam_Fellowship_01"), 3.6f }
    });

    AddSequence(TEXT("Dlg_RivendellFarewell"), {
        { FText::FromString(TEXT("Elrond")), FText::FromString(TEXT("Travel lightly. The strength of your company will matter more than speed.")), TEXT("VO_Elrond_Departure_01"), 5.2f }
    });

    AddSequence(TEXT("Dlg_CaradhrasOriginal"), {
        { FText::FromString(TEXT("Gimli")), FText::FromString(TEXT("The mountain has made its answer plain enough.")), TEXT("VO_Gimli_Caradhras_01"), 4.0f },
        { FText::FromString(TEXT("Aragorn")), FText::FromString(TEXT("Then we find another road before the snow buries this one.")), TEXT("VO_Aragorn_Caradhras_01"), 4.8f }
    });

    AddSequence(TEXT("Dlg_MoriaGateSearch"), {
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("The door is here. The mountain is simply refusing to show it to us.")), TEXT("VO_Gandalf_MoriaGate_01"), 5.5f },
        { FText::FromString(TEXT("Pippin")), FText::FromString(TEXT("It seems very good at that.")), TEXT("VO_Pippin_MoriaGate_01"), 3.0f }
    });

    AddSequence(TEXT("Dlg_MoriaDoorOriginal"), {
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("A simple answer, hiding in plain sight. Stay close once we are inside.")), TEXT("VO_Gandalf_MoriaDoor_01"), 5.4f }
    });

    AddSequence(TEXT("Dlg_MoriaWhispers"), {
        { FText::FromString(TEXT("Frodo")), FText::FromString(TEXT("Something is following us.")), TEXT("VO_Frodo_Moria_01"), 3.4f },
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("I know. Keep moving.")), TEXT("VO_Gandalf_Moria_01"), 2.8f }
    });

    AddSequence(TEXT("Dlg_BalinTombOriginal"), {
        { FText::FromString(TEXT("Gimli")), FText::FromString(TEXT("This was a hall of our people. It should not have ended like this.")), TEXT("VO_Gimli_Balin_01"), 5.6f },
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("Grieve quickly. We are not alone in here.")), TEXT("VO_Gandalf_Balin_01"), 4.5f }
    });

    AddSequence(TEXT("Dlg_MoriaAttack"), {
        { FText::FromString(TEXT("Aragorn")), FText::FromString(TEXT("Door! Hold them there and give Frodo room to move!")), TEXT("VO_Aragorn_MoriaAttack_01"), 4.0f }
    });

    AddSequence(TEXT("Dlg_BalrogApproach"), {
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("Run. This enemy is beyond the rest of you.")), TEXT("VO_Gandalf_Balrog_01"), 4.2f }
    });

    AddSequence(TEXT("Dlg_BridgeOriginalIntent"), {
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("Go! I will hold the bridge long enough for you to reach the stairs.")), TEXT("VO_Gandalf_Bridge_01"), 5.1f }
    });

    AddSequence(TEXT("Dlg_MoriaAftermath"), {
        { FText::FromString(TEXT("Aragorn")), FText::FromString(TEXT("We cannot stay exposed. We carry the grief with us, but we keep moving.")), TEXT("VO_Aragorn_MoriaAfter_01"), 6.0f }
    });

    AddSequence(TEXT("Dlg_LorienFirstContact"), {
        { FText::FromString(TEXT("Haldir")), FText::FromString(TEXT("You bring sorrow and danger beneath these trees. You will come with us.")), TEXT("VO_Haldir_Lorien_01"), 5.8f }
    });

    AddSequence(TEXT("Dlg_LorienGiftsOriginal"), {
        { FText::FromString(TEXT("Galadriel")), FText::FromString(TEXT("Take what will help you remember who you were before fear chose your road.")), TEXT("VO_Galadriel_Gifts_01"), 6.3f }
    });

    AddSequence(TEXT("Dlg_AnduinTravel"), {
        { FText::FromString(TEXT("Sam")), FText::FromString(TEXT("The river is easier on the feet, but I cannot say it feels safer.")), TEXT("VO_Sam_Anduin_01"), 4.8f }
    });

    AddSequence(TEXT("Dlg_ArgonathReaction"), {
        { FText::FromString(TEXT("Aragorn")), FText::FromString(TEXT("The old kings watched this river long before any of us were born.")), TEXT("VO_Aragorn_Argonath_01"), 5.2f }
    });

    AddSequence(TEXT("Dlg_ParthGalenCamp"), {
        { FText::FromString(TEXT("Boromir")), FText::FromString(TEXT("We should choose our road before doubt chooses it for us.")), TEXT("VO_Boromir_ParthGalen_01"), 5.0f }
    });

    AddSequence(TEXT("Dlg_UrukAttack"), {
        { FText::FromString(TEXT("Legolas")), FText::FromString(TEXT("They are in the trees! Keep the hobbits behind us!")), TEXT("VO_Legolas_Uruk_01"), 4.0f }
    });

    AddSequence(TEXT("Dlg_BoromirFinalOriginal"), {
        { FText::FromString(TEXT("Boromir")), FText::FromString(TEXT("I tried to master what I should have feared. Do not let that failure follow the others.")), TEXT("VO_Boromir_Final_01"), 6.8f },
        { FText::FromString(TEXT("Aragorn")), FText::FromString(TEXT("Your courage is what I will remember.")), TEXT("VO_Aragorn_FinalBoromir_01"), 4.2f }
    });

    AddSequence(TEXT("Dlg_FrodoSamDepartureOriginal"), {
        { FText::FromString(TEXT("Frodo")), FText::FromString(TEXT("I have to go on, Sam. The others have already paid too much for my choice.")), TEXT("VO_Frodo_Departure_01"), 6.0f },
        { FText::FromString(TEXT("Sam")), FText::FromString(TEXT("Then I am going with you. That part is not yours to decide alone.")), TEXT("VO_Sam_Departure_01"), 5.6f }
    });
}

bool UShireDialogueSubsystem::PlayDialogueCue(FName DialogueCue)
{
    const FShireDialogueSequence* Sequence = DialogueLibrary.Find(DialogueCue);
    if (!Sequence || Sequence->Lines.Num() == 0)
    {
        return false;
    }

    StopDialogue();
    ActiveDialogueCue = DialogueCue;
    PendingLines = Sequence->Lines;
    bPlaying = true;
    OnDialogueStateChanged.Broadcast(true);
    AdvanceQueue();
    return true;
}

void UShireDialogueSubsystem::StopDialogue()
{
    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().ClearTimer(AdvanceTimerHandle);
    }

    const bool bWasPlaying = bPlaying;
    bPlaying = false;
    PendingLines.Empty();
    CurrentLine = FShireDialogueLine();
    ActiveDialogueCue = NAME_None;

    if (bWasPlaying)
    {
        OnDialogueStateChanged.Broadcast(false);
    }
}

void UShireDialogueSubsystem::AdvanceQueue()
{
    if (PendingLines.Num() == 0)
    {
        StopDialogue();
        return;
    }

    CurrentLine = PendingLines[0];
    PendingLines.RemoveAt(0);

    OnSubtitleChanged.Broadcast(CurrentLine);
    if (CurrentLine.VoiceCue != NAME_None)
    {
        OnVoiceCueRequested.Broadcast(CurrentLine.VoiceCue);
    }

    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().SetTimer(
            AdvanceTimerHandle,
            this,
            &UShireDialogueSubsystem::AdvanceQueue,
            FMath::Max(0.75f, CurrentLine.Duration),
            false);
    }
}
