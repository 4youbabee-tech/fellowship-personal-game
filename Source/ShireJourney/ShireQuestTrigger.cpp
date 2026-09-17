#include "ShireQuestTrigger.h"
#include "ShireQuestSubsystem.h"
#include "ShireHUD.h"
#include "Components/BoxComponent.h"
#include "Engine/GameInstance.h"
#include "GameFramework/Character.h"
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
    if (!OtherActor || !OtherActor->IsA<ACharacter>() || (bTriggerOnce && bHasTriggered))
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

        if (StageAfterTrigger >= 0)
        {
            Quests->SetQuestStage(QuestId, StageAfterTrigger);
        }
    }

    if (NextChapterId != NAME_None)
    {
        Quests->StartChapter(NextChapterId, NextChapterQuestId, NextChapterQuestStage);
    }
    else if (NextQuestId != NAME_None)
    {
        Quests->StartQuest(NextQuestId, NextQuestStage);
    }

    bHasTriggered = true;

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
}
