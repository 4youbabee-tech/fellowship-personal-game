#include "ChapterWorldRouter.h"

#include "BlackRiderPrototype.h"
#include "BreePrototypeWorldBuilder.h"
#include "FellowshipChapterWorldBuilder.h"
#include "IsengardPrototypeWorldBuilder.h"
#include "ShireAmbientNPC.h"
#include "ShireNPC.h"
#include "ShirePrototypeWorldBuilder.h"
#include "ShireQuestSubsystem.h"
#include "ShireQuestTrigger.h"

#include "Engine/GameInstance.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/TextRenderActor.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
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
    Quests->OnExperienceChanged.AddDynamic(this, &AChapterWorldRouter::HandleExperienceChanged);
    LoadChapterWorld(Quests->GetCurrentChapterId());
}

void AChapterWorldRouter::HandleChapterChanged(FName PreviousChapterId, FName NewChapterId)
{
    LoadChapterWorld(NewChapterId);
}

void AChapterWorldRouter::HandleExperienceChanged(FName RouteId, FName EpisodeId, FName PlayableCharacterId)
{
    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (Quests)
    {
        LoadChapterWorld(Quests->GetCurrentChapterId(), true);
    }
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

    auto DestroyTaggedOfClass = [this](UClass* ActorClass, FName RequiredTag)
    {
        if (!ActorClass)
        {
            return;
        }

        TArray<AActor*> Actors;
        UGameplayStatics::GetAllActorsOfClass(this, ActorClass, Actors);
        for (AActor* Actor : Actors)
        {
            if (Actor && Actor != this && Actor->ActorHasTag(RequiredTag))
            {
                Actor->Destroy();
            }
        }
    };

    // Runtime-only gameplay actors use dedicated prototype classes, so they are always safe
    // to clear. Generic StaticMesh/Text actors are different: the template level may contain
    // its own floor/lights/helpers, so only destroy geometry explicitly tagged by our builders.
    DestroyAllOfClass(AShireQuestTrigger::StaticClass());
    DestroyAllOfClass(AShireNPC::StaticClass());
    DestroyAllOfClass(AShireAmbientNPC::StaticClass());
    DestroyAllOfClass(ABlackRiderPrototype::StaticClass());
    DestroyTaggedOfClass(AStaticMeshActor::StaticClass(), TEXT("RuntimePrototypeGenerated"));
    DestroyTaggedOfClass(ATextRenderActor::StaticClass(), TEXT("RuntimePrototypeGenerated"));
    DestroyAllOfClass(AShirePrototypeWorldBuilder::StaticClass());
    DestroyAllOfClass(ABreePrototypeWorldBuilder::StaticClass());
    DestroyAllOfClass(AFellowshipChapterWorldBuilder::StaticClass());
    DestroyAllOfClass(AIsengardPrototypeWorldBuilder::StaticClass());
}

FVector AChapterWorldRouter::GetChapterSpawnLocation(FName ChapterId) const
{
    if (ChapterId == TEXT("P1C01"))
    {
        return FVector(-2410.0f, -120.0f, 130.0f);
    }
    if (ChapterId == TEXT("P1C02"))
    {
        return FVector(-2380.0f, 0.0f, 130.0f);
    }
    if (ChapterId == TEXT("P1C03"))
    {
        return FVector(-2350.0f, 0.0f, 130.0f);
    }
    if (ChapterId == TEXT("P1C04"))
    {
        return FVector(-1900.0f, 0.0f, 130.0f);
    }
    if (ChapterId == TEXT("P1C05"))
    {
        return FVector(-2400.0f, 0.0f, 130.0f);
    }
    if (ChapterId == TEXT("P1C06"))
    {
        return FVector(-2350.0f, 0.0f, 130.0f);
    }
    if (ChapterId == TEXT("P1C07"))
    {
        return FVector(-2050.0f, 0.0f, 130.0f);
    }
    if (ChapterId == TEXT("P1C08"))
    {
        return FVector(-1950.0f, 0.0f, 130.0f);
    }

    return FVector(-2410.0f, -120.0f, 130.0f);
}

void AChapterWorldRouter::MovePlayerToChapterStart(FName ChapterId, bool bRestoreRouteTransform)
{
    APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
    if (!PlayerPawn)
    {
        return;
    }

    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;

    if (bRestoreRouteTransform && Quests)
    {
        FVector SavedLocation;
        FRotator SavedRotation;
        if (Quests->GetCurrentRouteSavedTransform(SavedLocation, SavedRotation))
        {
            PlayerPawn->SetActorLocationAndRotation(
                SavedLocation, SavedRotation, false, nullptr, ETeleportType::TeleportPhysics);
            return;
        }
    }

    FVector Spawn = GetChapterSpawnLocation(ChapterId);
    if (Quests && Quests->GetCurrentRouteId() == TEXT("GandalfParallel"))
    {
        Spawn = FVector(-2400.0f, 0.0f, 130.0f);
    }

    PlayerPawn->SetActorLocationAndRotation(
        Spawn,
        FRotator::ZeroRotator,
        false,
        nullptr,
        ETeleportType::TeleportPhysics);
}

void AChapterWorldRouter::LoadChapterWorld(FName ChapterId, bool bRestoreRouteTransform)
{
    if (!GetWorld())
    {
        return;
    }

    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    const FName RouteId = Quests ? Quests->GetCurrentRouteId() : FName(TEXT("FrodoMain"));
    const FName EpisodeId = Quests ? Quests->GetCurrentEpisodeId() : FName(*FString::Printf(TEXT("%s_Main"), *ChapterId.ToString()));

    if (LastLoadedRouteId == RouteId && LastLoadedEpisodeId == EpisodeId && LastLoadedChapterId == ChapterId)
    {
        return;
    }

    LastLoadedRouteId = RouteId;
    LastLoadedEpisodeId = EpisodeId;
    LastLoadedChapterId = ChapterId;

    ClearPrototypeBuilders();

    if (RouteId == TEXT("GandalfParallel"))
    {
        GetWorld()->SpawnActor<AIsengardPrototypeWorldBuilder>(FVector::ZeroVector, FRotator::ZeroRotator);
        MovePlayerToChapterStart(ChapterId, bRestoreRouteTransform);
        return;
    }

    if (ChapterId == TEXT("P1C01"))
    {
        GetWorld()->SpawnActor<AShirePrototypeWorldBuilder>(FVector::ZeroVector, FRotator::ZeroRotator);
        MovePlayerToChapterStart(ChapterId, bRestoreRouteTransform);
        return;
    }

    if (ChapterId == TEXT("P1C02"))
    {
        GetWorld()->SpawnActor<ABreePrototypeWorldBuilder>(FVector::ZeroVector, FRotator::ZeroRotator);
        MovePlayerToChapterStart(ChapterId, bRestoreRouteTransform);
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
        MovePlayerToChapterStart(ChapterId, bRestoreRouteTransform);
        return;
    }

    // Unknown chapter IDs fall back to the first chapter rather than leaving the player in an empty world.
    GetWorld()->SpawnActor<AShirePrototypeWorldBuilder>(FVector::ZeroVector, FRotator::ZeroRotator);
    MovePlayerToChapterStart(TEXT("P1C01"));
}
