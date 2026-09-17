#include "ChapterWorldRouter.h"

#include "BreePrototypeWorldBuilder.h"
#include "FellowshipChapterWorldBuilder.h"
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

    ExistingBuilders.Reset();
    UGameplayStatics::GetAllActorsOfClass(this, AFellowshipChapterWorldBuilder::StaticClass(), ExistingBuilders);
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

    if (ChapterId == TEXT("P1C01"))
    {
        GetWorld()->SpawnActor<AShirePrototypeWorldBuilder>(FVector::ZeroVector, FRotator::ZeroRotator);
        return;
    }

    if (ChapterId == TEXT("P1C02"))
    {
        GetWorld()->SpawnActor<ABreePrototypeWorldBuilder>(FVector::ZeroVector, FRotator::ZeroRotator);
        return;
    }

    if (ChapterId == TEXT("P1C03") || ChapterId == TEXT("P1C04") || ChapterId == TEXT("P1C05") ||
        ChapterId == TEXT("P1C06") || ChapterId == TEXT("P1C07") || ChapterId == TEXT("P1C08"))
    {
        AFellowshipChapterWorldBuilder* Builder = GetWorld()->SpawnActor<AFellowshipChapterWorldBuilder>(
            FVector::ZeroVector, FRotator::ZeroRotator);
        if (Builder)
        {
            Builder->BuildChapter(ChapterId);
        }
        return;
    }

    // Unknown chapter IDs fall back to the first chapter rather than leaving the player in an empty world.
    GetWorld()->SpawnActor<AShirePrototypeWorldBuilder>(FVector::ZeroVector, FRotator::ZeroRotator);
}
