#include "ShireQuestTrigger.h"
#include "ShireQuestSubsystem.h"
#include "ShirePlayerCharacter.h"
#include "ShireHUD.h"
#include "Components/BoxComponent.h"
#include "Engine/GameInstance.h"
#include "GameFramework/PlayerController.h"

namespace ShireCheckpointBindings
{
    struct FStoryCheckpointBinding
    {
        FName StoryBeatId;
        FName CheckpointId;
    };

    static const FStoryCheckpointBinding StoryBindings[] = {
        { TEXT("PartyArrival"), TEXT("WC_P1C01_PARTY") },
        { TEXT("LeavingHomeRoad"), TEXT("WC_P1C01_DEPART") },
        { TEXT("BlackRiderApproach"), TEXT("WC_P1C01_RIDER_PRE") },
        { TEXT("BreeRoadNightfall"), TEXT("WC_P1C02_GATE") },
        { TEXT("StriderPrivateRoom"), TEXT("WC_P1C02_PONY") },
        { TEXT("WeathertopReveal"), TEXT("WC_P1C03_WEATHERTOP") },
        { TEXT("MorgulWound"), TEXT("WC_P1C03_WOUND") },
        { TEXT("RivendellAwakening"), TEXT("WC_P1C04_WAKE") },
        { TEXT("FellowshipAssembled"), TEXT("WC_P1C04_COUNCIL") },
        { TEXT("FellowshipCamp"), TEXT("WC_P1C05_CAMP") },
        { TEXT("CaradhrasApproach"), TEXT("WC_P1C05_CARADHRAS") },
        { TEXT("MoriaLake"), TEXT("WC_P1C05_MORIA_GATE") },
        { TEXT("MoriaEntry"), TEXT("WC_P1C06_ENTRY") },
        { TEXT("BalinsTombReveal"), TEXT("WC_P1C06_BALIN") },
        { TEXT("BalrogApproach"), TEXT("WC_P1C06_BRIDGE") },
        { TEXT("LorienEntry"), TEXT("WC_P1C07_ENTRY") },
        { TEXT("Mirror"), TEXT("WC_P1C07_MIRROR") },
        { TEXT("AnduinDeparture"), TEXT("WC_P1C08_ANDUIN") },
        { TEXT("AmonHenArrival"), TEXT("WC_P1C08_AMONHEN") },
        { TEXT("BoromirFall"), TEXT("WC_P1C08_FALL") },
        { TEXT("Part1End"), TEXT("WC_P1C08_END") },
    };

    static FName Resolve(FName StoryBeatId)
    {
        if (StoryBeatId == NAME_None)
        {
            return NAME_None;
        }

        for (const FStoryCheckpointBinding& Binding : StoryBindings)
        {
            if (Binding.StoryBeatId == StoryBeatId)
            {
                return Binding.CheckpointId;
            }
        }
        return NAME_None;
    }
}

AShireQuestTrigger::AShireQuestTrigger()
{
    PrimaryActorTick.bCanEverTick = false;

    TriggerBox = CreateDefaultSubobject<UBoxComponent>(TEXT("TriggerBox"));
    RootComponent = TriggerBox;
    TriggerBox->SetBoxExtent(FVector(180.0f, 180.0f, 140.0f));
    TriggerBox->SetCollisionProfileName(TEXT("Trigger"));
}

void AShireQuestTrigger::BeginPlay()
{
    Super::BeginPlay();
    TriggerBox->OnComponentBeginOverlap.AddDynamic(this, &AShireQuestTrigger::OnTriggerBeginOverlap);
}

void AShireQuestTrigger::OnTriggerBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
    UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep,
    const FHitResult& SweepResult)
{
    AShirePlayerCharacter* Player = Cast<AShirePlayerCharacter>(OtherActor);
    if (!Player || (bTriggerOnce && bHasTriggered))
    {
        return;
    }

    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!Quests)
    {
        return;
    }

    if (QuestId != NAME_None)
    {
        if (Quests->GetActiveQuestId() != QuestId || Quests->GetQuestStage(QuestId) != RequiredStage)
        {
            return;
        }
    }

    if (RequiredSideStoryBeat != NAME_None && !Quests->HasStoryBeatTriggered(RequiredSideStoryBeat))
    {
        return;
    }

    // Optional side-story completion must stay one-time even after a save/load rebuild.
    if (QuestId == NAME_None && SideStoryBeatAfterTrigger != NAME_None &&
        Quests->HasStoryBeatTriggered(SideStoryBeatAfterTrigger))
    {
        return;
    }

    // Lock this trigger before broadcasting any quest/chapter delegates. A chapter
    // transition can destroy the generated trigger immediately through the world router,
    // so no trigger-owned state is intentionally mutated after the hand-off begins.
    if (bTriggerOnce)
    {
        bHasTriggered = true;
    }

    if (QuestId != NAME_None && StageAfterTrigger >= 0)
    {
        Quests->SetQuestStage(QuestId, StageAfterTrigger);
    }

    if (StoryBeatId != NAME_None)
    {
        Quests->TriggerStoryBeat(StoryBeatId);
    }

    if (SideStoryBeatAfterTrigger != NAME_None)
    {
        Quests->TriggerStoryBeat(SideStoryBeatAfterTrigger);
    }

    // Checkpoints tied to story beats are written only after the authoritative quest/story
    // mutations above. Chapter-transition checkpoints are queued by the player after the
    // next chapter is rebuilt, so those transition beats are intentionally not duplicated here.
    const FName CheckpointId = ShireCheckpointBindings::Resolve(StoryBeatId);
    if (CheckpointId != NAME_None)
    {
        Player->SaveAutomaticCheckpoint(CheckpointId, true);
    }

    // Show the authored objective before a chapter hand-off can destroy this actor.
    if (!ObjectiveMessage.IsEmpty())
    {
        if (APlayerController* PC = GetWorld() ? GetWorld()->GetFirstPlayerController() : nullptr)
        {
            if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
            {
                HUD->ShowAlert(ObjectiveMessage, 3.5f);
            }
        }
    }

    // Transitions are deliberately last: StartChapter synchronously notifies the router,
    // which may destroy this generated trigger as part of rebuilding the next region.
    if (NextChapterId != NAME_None)
    {
        const FName ChapterId = NextChapterId;
        const FName ChapterQuestId = NextChapterQuestId;
        const int32 ChapterQuestStage = NextChapterQuestStage;
        Quests->StartChapter(ChapterId, ChapterQuestId, ChapterQuestStage);
        return;
    }

    if (NextQuestId != NAME_None)
    {
        Quests->StartQuest(NextQuestId, NextQuestStage);
    }
}
