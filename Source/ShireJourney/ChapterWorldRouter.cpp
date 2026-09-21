#include "ChapterWorldRouter.h"

#include "BlackRiderPrototype.h"
#include "BreePrototypeWorldBuilder.h"
#include "FellowshipChapterWorldBuilder.h"
#include "FellowshipEnemyPrototype.h"
#include "IsengardPrototypeWorldBuilder.h"
#include "ShireAmbientNPC.h"
#include "ShireChapterAssetStreamingSubsystem.h"
#include "ShireNPC.h"
#include "ShirePrototypeWorldBuilder.h"
#include "ShireQuestSubsystem.h"
#include "ShireQuestTrigger.h"

#include "Engine/GameInstance.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/TextRenderActor.h"
#include "Engine/World.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
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

    AssetStreamingSubsystem = GI->GetSubsystem<UShireChapterAssetStreamingSubsystem>();
    if (AssetStreamingSubsystem)
    {
        AssetStreamingSubsystem->OnChapterAssetsReady.AddUObject(
            this,
            &AChapterWorldRouter::HandleChapterAssetsReady);
    }

    SetPlayerWorldHold(true);
    LoadChapterWorld(Quests->GetCurrentChapterId());
}

void AChapterWorldRouter::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (AssetStreamingSubsystem)
    {
        AssetStreamingSubsystem->OnChapterAssetsReady.RemoveAll(this);
        AssetStreamingSubsystem = nullptr;
    }

    Super::EndPlay(EndPlayReason);
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
    DestroyAllOfClass(AFellowshipEnemyPrototype::StaticClass());
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

void AChapterWorldRouter::SetPlayerWorldHold(bool bHold)
{
    ACharacter* Character = Cast<ACharacter>(UGameplayStatics::GetPlayerPawn(this, 0));
    if (!Character || !Character->GetCharacterMovement())
    {
        bPlayerWorldHoldActive = bHold;
        return;
    }

    UCharacterMovementComponent* Movement = Character->GetCharacterMovement();
    if (bHold)
    {
        Movement->StopMovementImmediately();
        Movement->DisableMovement();
        bPlayerWorldHoldActive = true;
        UE_LOG(LogTemp, Display, TEXT("ShireStartupGrounding: HOLD reason=awaiting-world"));
    }
    else if (bPlayerWorldHoldActive)
    {
        Movement->StopMovementImmediately();
        Movement->SetMovementMode(MOVE_Walking);
        bPlayerWorldHoldActive = false;
    }
}

bool AChapterWorldRouter::ResolveGroundedSpawnLocation(
    APawn* PlayerPawn,
    const FVector& RequestedLocation,
    FVector& OutGroundedLocation) const
{
    if (!GetWorld() || !PlayerPawn)
    {
        return false;
    }

    const FVector TraceStart = RequestedLocation + FVector(0.0f, 0.0f, 650.0f);
    const FVector TraceEnd = RequestedLocation - FVector(0.0f, 0.0f, 2200.0f);
    FCollisionQueryParams QueryParams(FName(TEXT("ShireChapterSpawnGround")), false, PlayerPawn);

    FHitResult GroundHit;
    if (!GetWorld()->LineTraceSingleByChannel(
            GroundHit,
            TraceStart,
            TraceEnd,
            ECC_Visibility,
            QueryParams) ||
        !GroundHit.bBlockingHit)
    {
        return false;
    }

    float CapsuleHalfHeight = 60.0f;
    if (const ACharacter* Character = Cast<ACharacter>(PlayerPawn))
    {
        if (const UCapsuleComponent* Capsule = Character->GetCapsuleComponent())
        {
            CapsuleHalfHeight = Capsule->GetScaledCapsuleHalfHeight();
        }
    }

    OutGroundedLocation = RequestedLocation;
    OutGroundedLocation.Z = GroundHit.ImpactPoint.Z + CapsuleHalfHeight + 4.0f;
    return true;
}

bool AChapterWorldRouter::MovePlayerToChapterStart(FName ChapterId, bool bRestoreRouteTransform)
{
    APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
    if (!PlayerPawn)
    {
        UE_LOG(LogTemp, Error, TEXT("ShireStartupGrounding: FAIL chapter=%s reason=no-player-pawn"), *ChapterId.ToString());
        return false;
    }

    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;

    FVector RequestedLocation = GetChapterSpawnLocation(ChapterId);
    FRotator RequestedRotation = FRotator::ZeroRotator;
    bool bUsingSavedTransform = false;

    if (bRestoreRouteTransform && Quests)
    {
        FVector SavedLocation;
        FRotator SavedRotation;
        if (Quests->GetCurrentRouteSavedTransform(SavedLocation, SavedRotation))
        {
            RequestedLocation = SavedLocation;
            RequestedRotation = SavedRotation;
            bUsingSavedTransform = true;
        }
    }

    if (!bUsingSavedTransform && Quests && Quests->GetCurrentRouteId() == TEXT("GandalfParallel"))
    {
        RequestedLocation = FVector(-2400.0f, 0.0f, 130.0f);
    }

    FVector GroundedLocation;
    if (!ResolveGroundedSpawnLocation(PlayerPawn, RequestedLocation, GroundedLocation))
    {
        PlayerPawn->SetActorLocationAndRotation(
            RequestedLocation,
            RequestedRotation,
            false,
            nullptr,
            ETeleportType::TeleportPhysics);
        SetPlayerWorldHold(true);
        UE_LOG(
            LogTemp,
            Error,
            TEXT("ShireStartupGrounding: FAIL chapter=%s reason=no-blocking-ground requested=(%.1f,%.1f,%.1f)"),
            *ChapterId.ToString(),
            RequestedLocation.X,
            RequestedLocation.Y,
            RequestedLocation.Z);
        return false;
    }

    PlayerPawn->SetActorLocationAndRotation(
        GroundedLocation,
        RequestedRotation,
        false,
        nullptr,
        ETeleportType::TeleportPhysics);

    if (ACharacter* Character = Cast<ACharacter>(PlayerPawn))
    {
        if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
        {
            Movement->StopMovementImmediately();
        }
    }

    SetPlayerWorldHold(false);
    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireStartupGrounding: PASS chapter=%s source=%s requestedZ=%.1f groundedZ=%.1f"),
        *ChapterId.ToString(),
        bUsingSavedTransform ? TEXT("saved-route") : TEXT("chapter-start"),
        RequestedLocation.Z,
        GroundedLocation.Z);
    return true;
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
    const FName EpisodeId = Quests
        ? Quests->GetCurrentEpisodeId()
        : FName(*FString::Printf(TEXT("%s_Main"), *ChapterId.ToString()));

    if (LastLoadedRouteId == RouteId &&
        LastLoadedEpisodeId == EpisodeId &&
        LastLoadedChapterId == ChapterId)
    {
        // A -> pending B -> A: abandon B before returning to the visible world.
        // Otherwise its delayed completion would still swap the player into B.
        PendingRouteId = NAME_None;
        PendingEpisodeId = NAME_None;
        PendingChapterId = NAME_None;
        bPendingRestoreRouteTransform = false;
        if (AssetStreamingSubsystem)
        {
            AssetStreamingSubsystem->CancelPendingRequest();
        }
        return;
    }

    if (PendingRouteId == RouteId &&
        PendingEpisodeId == EpisodeId &&
        PendingChapterId == ChapterId)
    {
        return;
    }

    PendingRouteId = RouteId;
    PendingEpisodeId = EpisodeId;
    PendingChapterId = ChapterId;
    bPendingRestoreRouteTransform = bRestoreRouteTransform;

    if (AssetStreamingSubsystem)
    {
        UE_LOG(
            LogTemp,
            Display,
            TEXT("ChapterAssetStreaming: router-wait chapter=%s route=%s bank-assets=%d"),
            *ChapterId.ToString(),
            *RouteId.ToString(),
            AssetStreamingSubsystem->GetChapterBankSize(ChapterId, RouteId));

        AssetStreamingSubsystem->RequestChapterAssets(ChapterId, RouteId);
        return;
    }

    // Compatibility path if the subsystem cannot initialize. The existing builders
    // remain authoritative and may synchronously resolve their assets.
    CommitChapterWorld(ChapterId, RouteId, EpisodeId, bRestoreRouteTransform);
}

void AChapterWorldRouter::HandleChapterAssetsReady(FName ChapterId, FName RouteId)
{
    if (PendingChapterId != ChapterId || PendingRouteId != RouteId)
    {
        return;
    }

    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!Quests || Quests->GetCurrentChapterId() != ChapterId ||
        Quests->GetCurrentRouteId() != RouteId ||
        Quests->GetCurrentEpisodeId() != PendingEpisodeId)
    {
        // Quest/save state may have changed again while assets were loading.
        return;
    }

    CommitChapterWorld(
        PendingChapterId,
        PendingRouteId,
        PendingEpisodeId,
        bPendingRestoreRouteTransform);
}

void AChapterWorldRouter::CommitChapterWorld(
    FName ChapterId,
    FName RouteId,
    FName EpisodeId,
    bool bRestoreRouteTransform)
{
    if (!GetWorld())
    {
        return;
    }

    LastLoadedRouteId = RouteId;
    LastLoadedEpisodeId = EpisodeId;
    LastLoadedChapterId = ChapterId;

    PendingRouteId = NAME_None;
    PendingEpisodeId = NAME_None;
    PendingChapterId = NAME_None;
    bPendingRestoreRouteTransform = false;

    // The previous visible chapter remains intact while the next bank streams.
    // Only swap runtime worlds after the requested bank reports ready.
    ClearPrototypeBuilders();

    if (RouteId == TEXT("GandalfParallel"))
    {
        AIsengardPrototypeWorldBuilder* Builder = GetWorld()->SpawnActor<AIsengardPrototypeWorldBuilder>(
            FVector::ZeroVector,
            FRotator::ZeroRotator);
        if (!Builder || !MovePlayerToChapterStart(ChapterId, bRestoreRouteTransform))
        {
            UE_LOG(LogTemp, Error, TEXT("ShireChapterAudit: grounding-or-builder-failed chapter=%s route=%s"), *ChapterId.ToString(), *RouteId.ToString());
            return;
        }
        UE_LOG(
            LogTemp,
            Display,
            TEXT("ShireChapterAudit: loaded=%s builder=Isengard route=%s streamed=ready"),
            *ChapterId.ToString(),
            *RouteId.ToString());
        return;
    }

    if (ChapterId == TEXT("P1C01"))
    {
        AShirePrototypeWorldBuilder* Builder = GetWorld()->SpawnActor<AShirePrototypeWorldBuilder>(
            FVector::ZeroVector,
            FRotator::ZeroRotator);
        if (!Builder)
        {
            UE_LOG(LogTemp, Error, TEXT("ShireChapterAudit: failed-to-spawn builder for P1C01"));
            return;
        }
        Builder->BuildPrototypeWorld();
        if (!MovePlayerToChapterStart(ChapterId, bRestoreRouteTransform))
        {
            return;
        }
        UE_LOG(LogTemp, Display, TEXT("ShirePlayableStartup: chapter=P1C01 route=%s"), *RouteId.ToString());
        UE_LOG(
            LogTemp,
            Display,
            TEXT("ShireChapterAudit: loaded=P1C01 builder=Shire route=%s streamed=ready"),
            *RouteId.ToString());
        return;
    }

    if (ChapterId == TEXT("P1C02"))
    {
        ABreePrototypeWorldBuilder* Builder = GetWorld()->SpawnActor<ABreePrototypeWorldBuilder>(
            FVector::ZeroVector,
            FRotator::ZeroRotator);
        if (!Builder)
        {
            UE_LOG(LogTemp, Error, TEXT("ShireChapterAudit: failed-to-spawn builder for P1C02"));
            return;
        }
        Builder->BuildPrototypeWorld();
        if (!MovePlayerToChapterStart(ChapterId, bRestoreRouteTransform))
        {
            return;
        }
        UE_LOG(
            LogTemp,
            Display,
            TEXT("ShireChapterAudit: loaded=P1C02 builder=Bree route=%s streamed=ready"),
            *RouteId.ToString());
        return;
    }

    if (ChapterId == TEXT("P1C03") ||
        ChapterId == TEXT("P1C04") ||
        ChapterId == TEXT("P1C05") ||
        ChapterId == TEXT("P1C06") ||
        ChapterId == TEXT("P1C07") ||
        ChapterId == TEXT("P1C08"))
    {
        AFellowshipChapterWorldBuilder* Builder =
            GetWorld()->SpawnActor<AFellowshipChapterWorldBuilder>(
                FVector::ZeroVector,
                FRotator::ZeroRotator);
        if (Builder)
        {
            Builder->BuildChapter(ChapterId);
            UE_LOG(
                LogTemp,
                Display,
                TEXT("ShireChapterAudit: loaded=%s builder=Fellowship route=%s streamed=ready"),
                *ChapterId.ToString(),
                *RouteId.ToString());
        }
        else
        {
            UE_LOG(
                LogTemp,
                Error,
                TEXT("ShireChapterAudit: failed-to-spawn builder for %s"),
                *ChapterId.ToString());
        }
        if (!Builder || !MovePlayerToChapterStart(ChapterId, bRestoreRouteTransform))
        {
            return;
        }
        return;
    }

    // Unknown chapter IDs fall back to the first chapter rather than leaving the
    // player in an empty world.
    AShirePrototypeWorldBuilder* FallbackBuilder = GetWorld()->SpawnActor<AShirePrototypeWorldBuilder>(
        FVector::ZeroVector,
        FRotator::ZeroRotator);
    if (FallbackBuilder)
    {
        FallbackBuilder->BuildPrototypeWorld();
        MovePlayerToChapterStart(TEXT("P1C01"), false);
    }
}
