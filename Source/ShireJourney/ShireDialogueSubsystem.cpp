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

    // Chapter 1 - The Shire. These lines are original game dialogue written to preserve
    // the story beats without reproducing screenplay text.
    AddSequence(TEXT("Dlg_ShireGandalfRoad"), {
        { FText::FromString(TEXT("Frodo")), FText::FromString(TEXT("Bilbo has been restless for weeks. I thought the party might settle him.")), TEXT("VO_Frodo_ShireRoad_01"), 4.4f },
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("A celebration can hide many things, but it cannot make a restless heart stay put.")), TEXT("VO_Gandalf_ShireRoad_01"), 5.2f },
        { FText::FromString(TEXT("Frodo")), FText::FromString(TEXT("Then I suppose I should enjoy Hobbiton while it is still quiet.")), TEXT("VO_Frodo_ShireRoad_02"), 4.3f }
    });

    AddSequence(TEXT("Dlg_ShirePartyArrival"), {
        { FText::FromString(TEXT("Sam")), FText::FromString(TEXT("They have lanterns all the way to the far hedge. Half the Shire must be coming.")), TEXT("VO_Sam_Party_01"), 4.8f },
        { FText::FromString(TEXT("Frodo")), FText::FromString(TEXT("Bilbo never does anything by halves when he has an audience.")), TEXT("VO_Frodo_Party_01"), 4.4f },
        { FText::FromString(TEXT("Bilbo")), FText::FromString(TEXT("Then do not stand at the edge, my boy. A party is wasted on spectators.")), TEXT("VO_Bilbo_Party_01"), 4.8f }
    });

    AddSequence(TEXT("Dlg_ShireBilboAftermath"), {
        { FText::FromString(TEXT("Frodo")), FText::FromString(TEXT("He was there a moment ago. Everyone saw him, and then nothing.")), TEXT("VO_Frodo_AfterParty_01"), 4.8f },
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("Bilbo has chosen his own manner of leaving. What matters now is what he left behind.")), TEXT("VO_Gandalf_AfterParty_01"), 5.5f },
        { FText::FromString(TEXT("Frodo")), FText::FromString(TEXT("I will go back to Bag End.")), TEXT("VO_Frodo_AfterParty_02"), 3.2f }
    });

    AddSequence(TEXT("Dlg_ShireRingWarning"), {
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("The thing Bilbo left you is not an ordinary heirloom. I have feared that for longer than I wished to admit.")), TEXT("VO_Gandalf_RingWarn_01"), 6.4f },
        { FText::FromString(TEXT("Frodo")), FText::FromString(TEXT("He carried it for years. Why should it become dangerous now?")), TEXT("VO_Frodo_RingWarn_01"), 4.5f },
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("Because dangerous things are patient. Keep it hidden while I learn whose shadow is following it.")), TEXT("VO_Gandalf_RingWarn_02"), 6.2f },
        { FText::FromString(TEXT("Frodo")), FText::FromString(TEXT("And if that shadow reaches the Shire first?")), TEXT("VO_Frodo_RingWarn_02"), 4.2f },
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("Then leave quietly. Trust Sam, and do not give strangers a reason to remember your name.")), TEXT("VO_Gandalf_RingWarn_03"), 5.8f }
    });

    AddSequence(TEXT("Dlg_ShireLeavingHome"), {
        { FText::FromString(TEXT("Sam")), FText::FromString(TEXT("It feels strange to walk past the last gardens and not know when we will see them again.")), TEXT("VO_Sam_Leaving_01"), 5.1f },
        { FText::FromString(TEXT("Frodo")), FText::FromString(TEXT("We are only going as far as we must. I would rather keep the Shire out of whatever this becomes.")), TEXT("VO_Frodo_Leaving_01"), 5.7f },
        { FText::FromString(TEXT("Sam")), FText::FromString(TEXT("Then I will make sure you do not have to do that alone.")), TEXT("VO_Sam_Leaving_02"), 4.3f }
    });

    AddSequence(TEXT("Dlg_ShireBlackRider"), {
        { FText::FromString(TEXT("Pippin")), FText::FromString(TEXT("That rider has passed the same stretch twice. No traveler does that by accident.")), TEXT("VO_Pippin_Rider_01"), 4.9f },
        { FText::FromString(TEXT("Merry")), FText::FromString(TEXT("Then we stop being where he expects us to be.")), TEXT("VO_Merry_Rider_01"), 4.0f },
        { FText::FromString(TEXT("Sam")), FText::FromString(TEXT("Off the road. Now.")), TEXT("VO_Sam_Rider_01"), 2.6f }
    });

    AddSequence(TEXT("Dlg_ShireRootHide"), {
        { FText::FromString(TEXT("Sam")), FText::FromString(TEXT("Do not move. Let it pass.")), TEXT("VO_Sam_RootHide_01"), 3.0f },
        { FText::FromString(TEXT("Frodo")), FText::FromString(TEXT("I can feel it searching.")), TEXT("VO_Frodo_RootHide_01"), 3.3f }
    });

    AddSequence(TEXT("Dlg_ShireFerry"), {
        { FText::FromString(TEXT("Merry")), FText::FromString(TEXT("Get the rope loose. We can argue about directions on the other bank.")), TEXT("VO_Merry_Ferry_01"), 4.5f },
        { FText::FromString(TEXT("Sam")), FText::FromString(TEXT("Frodo, get aboard. I am right behind you.")), TEXT("VO_Sam_Ferry_01"), 3.8f },
        { FText::FromString(TEXT("Pippin")), FText::FromString(TEXT("I was hoping the dangerous part ended before the river.")), TEXT("VO_Pippin_Ferry_01"), 4.0f }
    });

    AddSequence(TEXT("Dlg_IsengardArrival"), {
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("Saruman asked for counsel to be shared. The silence here feels more like a warning.")), TEXT("VO_Gandalf_Isengard_01"), 5.4f },
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("Orthanc has always been severe. Today it feels watchful.")), TEXT("VO_Gandalf_Isengard_02"), 4.5f }
    });

    AddSequence(TEXT("Dlg_OrthancBetrayal"), {
        { FText::FromString(TEXT("Saruman")), FText::FromString(TEXT("The old order is ending. You can either understand that change or be crushed beneath it.")), TEXT("VO_Saruman_Betrayal_01"), 6.1f },
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("Wisdom that kneels to fear is only another kind of surrender.")), TEXT("VO_Gandalf_Betrayal_01"), 5.5f },
        { FText::FromString(TEXT("Saruman")), FText::FromString(TEXT("Then you have chosen isolation over influence.")), TEXT("VO_Saruman_Betrayal_02"), 4.6f }
    });

    AddSequence(TEXT("Dlg_OrthancPrison"), {
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("The trees are falling. He is not preparing for war someday; he has already begun it.")), TEXT("VO_Gandalf_Prison_01"), 6.0f },
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("If I cannot stop this from here, I must survive long enough to warn those who still can.")), TEXT("VO_Gandalf_Prison_02"), 6.0f }
    });

    AddSequence(TEXT("Dlg_IsengardIndustry"), {
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("Pits, furnaces, chains. Isengard is being remade into a weapon.")), TEXT("VO_Gandalf_Industry_01"), 5.1f },
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("Saruman has traded patience for production. That makes him dangerous, but not invincible.")), TEXT("VO_Gandalf_Industry_02"), 5.8f }
    });

    AddSequence(TEXT("Dlg_OrthancEscape"), {
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("At last. One chance is enough.")), TEXT("VO_Gandalf_Escape_01"), 3.2f },
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("The warning must reach Rivendell before Saruman's armies do.")), TEXT("VO_Gandalf_Escape_02"), 4.8f }
    });

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

    AddSequence(TEXT("Dlg_StriderDeparture"), {
        { FText::FromString(TEXT("Strider")), FText::FromString(TEXT("We leave before Bree wakes. Stay off the main road and keep close to me.")), TEXT("VO_Strider_Depart_01"), 5.3f },
        { FText::FromString(TEXT("Sam")), FText::FromString(TEXT("I liked the Shire roads better, but I suppose that is the point.")), TEXT("VO_Sam_Depart_01"), 4.2f }
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

    AddSequence(TEXT("Dlg_BilboReunion"), {
        { FText::FromString(TEXT("Bilbo")), FText::FromString(TEXT("You look taller than when I left, though perhaps that is only what worry does to an old hobbit's eyes.")), TEXT("VO_Bilbo_Rivendell_01"), 5.4f },
        { FText::FromString(TEXT("Frodo")), FText::FromString(TEXT("I thought finding you would make the road feel smaller.")), TEXT("VO_Frodo_RivendellBilbo_01"), 4.4f },
        { FText::FromString(TEXT("Bilbo")), FText::FromString(TEXT("Roads rarely shrink after we understand where they lead.")), TEXT("VO_Bilbo_Rivendell_02"), 4.8f }
    });

    AddSequence(TEXT("Dlg_FellowshipCamp"), {
        { FText::FromString(TEXT("Boromir")), FText::FromString(TEXT("Again. Keep your balance before you worry about striking hard.")), TEXT("VO_Boromir_Training_01"), 4.5f },
        { FText::FromString(TEXT("Merry")), FText::FromString(TEXT("I was balanced perfectly until the sword arrived.")), TEXT("VO_Merry_Training_01"), 4.0f },
        { FText::FromString(TEXT("Pippin")), FText::FromString(TEXT("Does surviving lunch count as training?")), TEXT("VO_Pippin_Training_01"), 3.6f }
    });

    AddSequence(TEXT("Dlg_CrebainWarning"), {
        { FText::FromString(TEXT("Aragorn")), FText::FromString(TEXT("Down. Those birds are not moving like a wild flock.")), TEXT("VO_Aragorn_Crebain_01"), 4.2f },
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("Keep still until they pass. We have been noticed.")), TEXT("VO_Gandalf_Crebain_01"), 4.5f }
    });

    AddSequence(TEXT("Dlg_WatcherAttack"), {
        { FText::FromString(TEXT("Gandalf")), FText::FromString(TEXT("Inside! Leave the lake behind us.")), TEXT("VO_Gandalf_Watcher_01"), 3.4f },
        { FText::FromString(TEXT("Aragorn")), FText::FromString(TEXT("Stay together. Do not let it pull anyone back to the water.")), TEXT("VO_Aragorn_Watcher_01"), 4.6f }
    });

    AddSequence(TEXT("Dlg_CaveTrollAttack"), {
        { FText::FromString(TEXT("Boromir")), FText::FromString(TEXT("Keep it away from the hobbits. Make it turn.")), TEXT("VO_Boromir_Troll_01"), 4.2f },
        { FText::FromString(TEXT("Gimli")), FText::FromString(TEXT("At last, something in here large enough to hit without searching for it.")), TEXT("VO_Gimli_Troll_01"), 4.9f }
    });

    AddSequence(TEXT("Dlg_LorienGrief"), {
        { FText::FromString(TEXT("Aragorn")), FText::FromString(TEXT("We cannot pretend the mountain did not take something from us.")), TEXT("VO_Aragorn_LorienGrief_01"), 4.9f },
        { FText::FromString(TEXT("Sam")), FText::FromString(TEXT("Then let us remember him before the road asks us to move again.")), TEXT("VO_Sam_LorienGrief_01"), 4.8f }
    });

    AddSequence(TEXT("Dlg_MirrorOriginal"), {
        { FText::FromString(TEXT("Galadriel")), FText::FromString(TEXT("Water can show what is feared, what is possible, and what may never come to pass.")), TEXT("VO_Galadriel_Mirror_01"), 6.1f },
        { FText::FromString(TEXT("Frodo")), FText::FromString(TEXT("Then I do not know which part frightens me most.")), TEXT("VO_Frodo_Mirror_01"), 4.2f }
    });

    AddSequence(TEXT("Dlg_BoromirPressure"), {
        { FText::FromString(TEXT("Boromir")), FText::FromString(TEXT("Every mile south brings the danger closer to my people, and still we carry power we refuse to use.")), TEXT("VO_Boromir_Pressure_01"), 6.1f },
        { FText::FromString(TEXT("Frodo")), FText::FromString(TEXT("The Ring does not offer help without taking something back.")), TEXT("VO_Frodo_Pressure_01"), 5.0f }
    });

    AddSequence(TEXT("Dlg_BoromirDefense"), {
        { FText::FromString(TEXT("Boromir")), FText::FromString(TEXT("Merry! Pippin! Stay behind me and keep moving toward the river.")), TEXT("VO_Boromir_Defense_01"), 4.7f },
        { FText::FromString(TEXT("Merry")), FText::FromString(TEXT("We are not leaving you to hold them alone.")), TEXT("VO_Merry_Defense_01"), 4.1f }
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

    AddSequence(TEXT("Dlg_FellowshipTravel"), {
        { FText::FromString(TEXT("Boromir")), FText::FromString(TEXT("We have open country ahead. Better to cross it while the weather still favors us.")), TEXT("VO_Boromir_Travel_01"), 5.0f },
        { FText::FromString(TEXT("Gimli")), FText::FromString(TEXT("Open country is only pleasant until the wind discovers you.")), TEXT("VO_Gimli_Travel_01"), 4.5f },
        { FText::FromString(TEXT("Legolas")), FText::FromString(TEXT("The birds are moving strangely. We should keep our eyes above as well as ahead.")), TEXT("VO_Legolas_Travel_01"), 5.2f }
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

bool UShireDialogueSubsystem::PlayDynamicLine(
    const FShireDialogueLine& Line,
    FName DynamicCueId)
{
    TArray<FShireDialogueLine> Lines;
    Lines.Add(Line);
    return PlayDynamicSequence(Lines, DynamicCueId);
}

bool UShireDialogueSubsystem::PlayDynamicSequence(
    const TArray<FShireDialogueLine>& Lines,
    FName DynamicCueId)
{
    PendingLines.Empty();
    for (const FShireDialogueLine& Line : Lines)
    {
        if (!Line.Subtitle.IsEmpty())
        {
            PendingLines.Add(Line);
        }
    }
    if (PendingLines.Num() == 0)
    {
        return false;
    }

    StopDialogue();
    ActiveDialogueCue = DynamicCueId == NAME_None ? FName(TEXT("DynamicNPCSequence")) : DynamicCueId;
    PendingLines = Lines;
    for (int32 Index = PendingLines.Num() - 1; Index >= 0; --Index)
    {
        if (PendingLines[Index].Subtitle.IsEmpty())
        {
            PendingLines.RemoveAt(Index);
        }
    }
    bPlaying = PendingLines.Num() > 0;
    if (!bPlaying)
    {
        return false;
    }
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
