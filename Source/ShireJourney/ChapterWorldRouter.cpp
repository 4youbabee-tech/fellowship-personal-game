#include "ChapterWorldRouter.h"

#include "BreePrototypeWorldBuilder.h"
#include "ShirePrototypeWorldBuilder.h"
#include "ShireQuestSubsystem.h"

#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"

AChapterWorldRouter::AChapterWorldRouter()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AChapterWorldRouter::BeginPlay()
{
    Super::BeginPlay();

    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!Quests)
    {
        return;
    }

    Quests->OnChapterChanged.AddDynamic(this, &AChapterWorldRouter::HandleChapterChanged);
    LoadChapterWorld(Quests->GetCurrentChapterId());
}

void AChapterWorldRouter::HandleChapterChanged(FName PreviousChapterId, FName NewChapterId)
{
    LoadChapterWorld(NewChapterId);
}

void AChapterWorldRouter::ClearPrototypeBuilders()
{
    if (!GetWorld())
    {
        return;
    }

    TArray<AActor*> ExistingBuilders;
    UGameplayStatics::GetAllActorsOfClass(this, AShirePrototypeWorldBuilder::StaticClass(), ExistingBuilders);
    for (AActor* Actor : ExistingBuilders)
    {
        if (Actor)
        {
            Actor->Destroy();
        }
    }

    ExistingBuilders.Reset();
    UGameplayStatics::GetAllActorsOfClass(this, ABreePrototypeWorldBuilder::StaticClass(), ExistingBuilders);
    for (AActor* Actor : ExistingBuilders)
    {
        if (Actor)
        {
            Actor->Destroy();
        }
    }
}

void AChapterWorldRouter::LoadChapterWorld(FName ChapterId)
{
    if (!GetWorld())
    {
        return;
    }

    ClearPrototypeBuilders();

    if (ChapterId == TEXT("P1C02"))
    {
        GetWorld()->SpawnActor<ABreePrototypeWorldBuilder>(FVector::ZeroVector, FRotator::ZeroRotator);
    }
    else
    {
        // Until later chapter builders are implemented, default to the Shire rather than
        // leaving an empty level. This branch will be expanded chapter by chapter.
        GetWorld()->SpawnActor<AShirePrototypeWorldBuilder>(FVector::ZeroVector, FRotator::ZeroRotator);
    }
}
