#include "ShireQuestTrigger.h"
#include "ShireQuestSubsystem.h"
#include "ShirePlayerCharacter.h"
#include "ShireHUD.h"
#include "Components/BoxComponent.h"
#include "Engine/GameInstance.h"
#include "GameFramework/PlayerController.h"

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
    if (!OtherActor || !OtherActor->IsA<AShirePlayerCharacter>() || (bTriggerOnce && bHasTriggered))
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
