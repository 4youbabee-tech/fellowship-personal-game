#include "ChapterWorldRouter.h"

#include "BlackRiderPrototype.h"
#include "BreePrototypeWorldBuilder.h"
#include "FellowshipChapterWorldBuilder.h"
#include "ShireAmbientNPC.h"
#include "ShireNPC.h"
#include "ShirePrototypeWorldBuilder.h"
#include "ShireQuestSubsystem.h"
#include "ShireQuestTrigger.h"

#include "Engine/GameInstance.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/TextRenderActor.h"
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

    auto DestroyAllOfClass = [this](UClass* ActorClass)
    {
        if (!ActorClass)
        {
            return;
        }

        TArray<AActor*> Actors;
        UGameplayStatics::GetAllActorsOfClass(this, ActorClass, Actors);
        for (AActor* Actor : Actors)
        {
            if (Actor && Actor != this)
            {
                Actor->Destroy();
            }
        }
    };

    // Runtime chapter worlds are generated entirely from these prototype actor classes.
    // Clear them before constructing the next chapter so geometry, NPCs and quest triggers
    // cannot accumulate across chapter transitions on the low-memory target laptop.
    DestroyAllOfClass(AShireQuestTrigger::StaticClass());
    DestroyAllOfClass(AShireNPC::StaticClass());
    DestroyAllOfClass(AShireAmbientNPC::StaticClass());
    DestroyAllOfClass(ABlackRiderPrototype::StaticClass());
    DestroyAllOfClass(AStaticMeshActor::StaticClass());
    DestroyAllOfClass(ATextRenderActor::StaticClass());
    DestroyAllOfClass(AShirePrototypeWorldBuilder::StaticClass());
    DestroyAllOfClass(ABreePrototypeWorldBuilder::StaticClass());
    DestroyAllOfClass(AFellowshipChapterWorldBuilder::StaticClass());
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
