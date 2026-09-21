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
#include "ShireSaveGame.h"

#include "Engine/GameInstance.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/TextRenderActor.h"
#include "Engine/World.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Pawn.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "TimerManager.h"

AChapterWorldRouter::AChapterWorldRouter()
{
    PrimaryActorTick.bCanEverTick = false;
}

bool AChapterWorldRouter::IsWorldCommitted(
    FName ChapterId,
    FName RouteId,
    FName EpisodeId) const
{
    return WorldRevision > 0 &&
        PendingChapterId.IsNone() &&
        PendingRouteId.IsNone() &&
        PendingEpisodeId.IsNone() &&
        LastLoadedChapterId == ChapterId &&
        LastLoadedRouteId == RouteId &&
        LastLoadedEpisodeId == EpisodeId;
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

    LastCommittedRollbackSnapshot = nullptr;
    Super::EndPlay(EndPlayReason);
}

void AChapterWorldRouter::HandleChapterChanged(FName PreviousChapterId, FName NewChapterId)
{
    if (bRollbackInProgress)
    {
        return;
    }
    LoadChapterWorld(NewChapterId);
}

void AChapterWorldRouter::HandleExperienceChanged(FName RouteId, FName EpisodeId, FName PlayableCharacterId)
{
    if (bRollbackInProgress)
    {
        return;
    }

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

    TArray<AActor*> AmbientActors;
    UGameplayStatics::GetAllActorsOfClass(this, AShireAmbientNPC::StaticClass(), AmbientActors);
    for (AActor* Actor : AmbientActors)
    {
        if (Actor && Actor != this && !Actor->ActorHasTag(TEXT("LivingWorldManaged")))
        {
            Actor->Destroy();
        }
    }
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

bool AChapterWorldRouter::PlacePlayerAtCommittedTransform(
    APawn* PlayerPawn,
    FName ChapterId,
    FName RouteId,
    FName EpisodeId,
    const FVector& RequestedLocation,
    const FRotator& RequestedRotation)
{
    if (!PlayerPawn || !IsWorldCommitted(ChapterId, RouteId, EpisodeId))
    {
        return false;
    }

    FVector GroundedLocation = FVector::ZeroVector;
    if (!ResolveGroundedSpawnLocation(PlayerPawn, RequestedLocation, GroundedLocation))
    {
        UE_LOG(
            LogTemp,
            Error,
            TEXT("ShireSaveRestore: FAIL chapter=%s route=%s episode=%s reason=no-ground"),
            *ChapterId.ToString(),
            *RouteId.ToString(),
            *EpisodeId.ToString());
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

    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireSaveRestore: PLACED chapter=%s route=%s episode=%s revision=%u"),
        *ChapterId.ToString(),
        *RouteId.ToString(),
        *EpisodeId.ToString(),
        WorldRevision);
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
        TEXT("ShireStartupGrounding: PLACED chapter=%s source=%s requestedZ=%.1f groundedZ=%.1f"),
        *ChapterId.ToString(),
        bUsingSavedTransform ? TEXT("saved-route") : TEXT("chapter-start"),
        RequestedLocation.Z,
        GroundedLocation.Z);

    if (FParse::Param(FCommandLine::Get(), TEXT("ShireCIRuntimeAudit")))
    {
        FTimerHandle StabilityTimer;
        FTimerDelegate StabilityDelegate = FTimerDelegate::CreateUObject(
            this,
            &AChapterWorldRouter::VerifyPlayerGroundingStability,
            ChapterId,
            GroundedLocation);
        GetWorldTimerManager().SetTimer(StabilityTimer, StabilityDelegate, 2.0f, false);
    }
    return true;
}

void AChapterWorldRouter::VerifyPlayerGroundingStability(FName ChapterId, FVector PlacedLocation)
{
    APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
    ACharacter* Character = Cast<ACharacter>(PlayerPawn);
    UCharacterMovementComponent* Movement = Character ? Character->GetCharacterMovement() : nullptr;
    if (!PlayerPawn || !Movement)
    {
        UE_LOG(LogTemp, Error, TEXT("ShireStartupGrounding: FAIL chapter=%s reason=stability-player-missing"), *ChapterId.ToString());
        return;
    }

    const FVector CurrentLocation = PlayerPawn->GetActorLocation();
    FVector ResolvedGroundLocation;
    const bool bHasBlockingGround = ResolveGroundedSpawnLocation(
        PlayerPawn,
        CurrentLocation,
        ResolvedGroundLocation);
    const float VerticalDrop = PlacedLocation.Z - CurrentLocation.Z;
    const float HorizontalDrift = FVector::Dist2D(PlacedLocation, CurrentLocation);
    const bool bStable =
        bHasBlockingGround &&
        !Movement->IsFalling() &&
        VerticalDrop <= 35.0f &&
        HorizontalDrift <= 80.0f;

    if (!bStable)
    {
        UE_LOG(
            LogTemp,
            Error,
            TEXT("ShireStartupGrounding: FAIL chapter=%s reason=unstable-after-2s ground=%s falling=%s drop=%.1f drift=%.1f current=(%.1f,%.1f,%.1f)"),
            *ChapterId.ToString(),
            bHasBlockingGround ? TEXT("yes") : TEXT("no"),
            Movement->IsFalling() ? TEXT("yes") : TEXT("no"),
            VerticalDrop,
            HorizontalDrift,
            CurrentLocation.X,
            CurrentLocation.Y,
            CurrentLocation.Z);
        return;
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireStartupGrounding: PASS chapter=%s stableSeconds=2.0 ground=yes drop=%.1f drift=%.1f"),
        *ChapterId.ToString(),
        VerticalDrop,
        HorizontalDrift);
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

AActor* AChapterWorldRouter::SpawnWorldForRequest(
    FName ChapterId,
    FName RouteId,
    FName& OutBuilderName)
{
    if (!GetWorld())
    {
        return nullptr;
    }

    if (RouteId == TEXT("GandalfParallel"))
    {
        OutBuilderName = TEXT("Isengard");
        return GetWorld()->SpawnActor<AIsengardPrototypeWorldBuilder>(
            FVector::ZeroVector, FRotator::ZeroRotator);
    }

    if (ChapterId == TEXT("P1C01"))
    {
        OutBuilderName = TEXT("Shire");
        AShirePrototypeWorldBuilder* Builder =
            GetWorld()->SpawnActor<AShirePrototypeWorldBuilder>(
                FVector::ZeroVector, FRotator::ZeroRotator);
        if (Builder)
        {
            Builder->BuildPrototypeWorld();
        }
        return Builder;
    }

    if (ChapterId == TEXT("P1C02"))
    {
        OutBuilderName = TEXT("Bree");
        ABreePrototypeWorldBuilder* Builder =
            GetWorld()->SpawnActor<ABreePrototypeWorldBuilder>(
                FVector::ZeroVector, FRotator::ZeroRotator);
        if (Builder)
        {
            Builder->BuildPrototypeWorld();
        }
        return Builder;
    }

    if (ChapterId == TEXT("P1C03") || ChapterId == TEXT("P1C04") ||
        ChapterId == TEXT("P1C05") || ChapterId == TEXT("P1C06") ||
        ChapterId == TEXT("P1C07") || ChapterId == TEXT("P1C08"))
    {
        OutBuilderName = TEXT("Fellowship");
        AFellowshipChapterWorldBuilder* Builder =
            GetWorld()->SpawnActor<AFellowshipChapterWorldBuilder>(
                FVector::ZeroVector, FRotator::ZeroRotator);
        if (Builder)
        {
            Builder->BuildChapter(ChapterId);
        }
        return Builder;
    }

    OutBuilderName = NAME_None;
    return nullptr;
}

void AChapterWorldRouter::CaptureCommittedRollbackSnapshot()
{
    APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!PlayerPawn || !Quests || !IsWorldCommitted(
            Quests->GetCurrentChapterId(),
            Quests->GetCurrentRouteId(),
            Quests->GetCurrentEpisodeId()))
    {
        return;
    }

    UShireSaveGame* Snapshot = NewObject<UShireSaveGame>(this);
    if (!Snapshot)
    {
        return;
    }

    Snapshot->SaveSchemaVersion = UShireSaveGame::CurrentSchemaVersion;
    Snapshot->SnapshotCreatedUnixSeconds = FDateTime::UtcNow().ToUnixTimestamp();
    Snapshot->PlayerLocation = PlayerPawn->GetActorLocation();
    Snapshot->PlayerRotation = PlayerPawn->GetActorRotation();
    Snapshot->QuestStages = Quests->GetAllQuestStages();
    Snapshot->ActiveQuestId = Quests->GetActiveQuestId();
    Snapshot->CurrentChapterId = Quests->GetCurrentChapterId();
    Snapshot->CompletedStoryBeats = Quests->GetCompletedStoryBeats();
    Snapshot->CurrentRouteId = Quests->GetCurrentRouteId();
    Snapshot->CurrentEpisodeId = Quests->GetCurrentEpisodeId();
    Snapshot->PlayableCharacterId = Quests->GetPlayableCharacterId();
    Snapshot->RouteProgress = Quests->GetRouteProgressSnapshot();
    Snapshot->NPCMemoryState = Quests->GetNPCMemorySnapshot();
    Snapshot->JourneyDiscoveryIds = Quests->GetJourneyDiscoveryIds();
    Snapshot->JourneyInsight = Quests->GetJourneyInsight();
    Snapshot->JourneyInsightMilestones = Quests->GetJourneyInsightMilestones();
    Snapshot->ProgressionXP = Quests->GetProgressionSnapshot();
    Snapshot->ChronicleEntryIds = Quests->GetChronicleEntryIds();
    Snapshot->KnownMapRegionIds = Quests->GetKnownMapRegionIds();

    LastCommittedRollbackSnapshot = Snapshot;
    LastCommittedSnapshotRevision = WorldRevision;

    UE_LOG(
        LogTemp,
        Verbose,
        TEXT("ShireWorldCommit: rollback-snapshot chapter=%s route=%s episode=%s revision=%u"),
        *Snapshot->CurrentChapterId.ToString(),
        *Snapshot->CurrentRouteId.ToString(),
        *Snapshot->CurrentEpisodeId.ToString(),
        LastCommittedSnapshotRevision);
}

bool AChapterWorldRouter::RestoreCommittedWorldFromSnapshot(
    FName FallbackChapterId,
    FName FallbackRouteId)
{
    if (!GetWorld() || !LastCommittedRollbackSnapshot)
    {
        return false;
    }

    UShireSaveGame* Snapshot = LastCommittedRollbackSnapshot;
    const FName RestoreChapterId = Snapshot->CurrentChapterId != NAME_None
        ? Snapshot->CurrentChapterId
        : FallbackChapterId;
    const FName RestoreRouteId = Snapshot->CurrentRouteId != NAME_None
        ? Snapshot->CurrentRouteId
        : FallbackRouteId;
    const FName RestoreEpisodeId = Snapshot->CurrentEpisodeId != NAME_None
        ? Snapshot->CurrentEpisodeId
        : LastLoadedEpisodeId;

    if (RestoreChapterId == NAME_None || RestoreRouteId == NAME_None || RestoreEpisodeId == NAME_None)
    {
        return false;
    }

    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!Quests)
    {
        return false;
    }

    bRollbackInProgress = true;

    Quests->RestoreNPCMemoryState(Snapshot->NPCMemoryState);
    Quests->RestoreJourneyDiscoveryState(
        Snapshot->JourneyDiscoveryIds,
        Snapshot->JourneyInsight,
        Snapshot->JourneyInsightMilestones);
    Quests->RestoreProgressionState(Snapshot->ProgressionXP);
    Quests->RestoreKnowledgeState(
        Snapshot->ChronicleEntryIds,
        Snapshot->KnownMapRegionIds);
    Quests->RestoreQuestState(
        Snapshot->QuestStages,
        Snapshot->ActiveQuestId,
        RestoreChapterId,
        Snapshot->CompletedStoryBeats,
        RestoreRouteId,
        RestoreEpisodeId,
        Snapshot->PlayableCharacterId,
        Snapshot->RouteProgress);

    ClearPrototypeBuilders();

    FName RestoredBuilderName = NAME_None;
    AActor* RestoredWorld = SpawnWorldForRequest(
        RestoreChapterId,
        RestoreRouteId,
        RestoredBuilderName);

    APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
    const bool bPlaced = RestoredWorld && PlayerPawn && PlacePlayerAtCommittedTransform(
        PlayerPawn,
        RestoreChapterId,
        RestoreRouteId,
        RestoreEpisodeId,
        Snapshot->PlayerLocation,
        Snapshot->PlayerRotation);

    if (!RestoredWorld || !bPlaced)
    {
        bRollbackInProgress = false;
        UE_LOG(
            LogTemp,
            Error,
            TEXT("ShireWorldCommit: rollback-failed chapter=%s route=%s builder=%s world=%s placed=%s priorRevision=%u"),
            *RestoreChapterId.ToString(),
            *RestoreRouteId.ToString(),
            *RestoredBuilderName.ToString(),
            RestoredWorld ? TEXT("yes") : TEXT("no"),
            bPlaced ? TEXT("yes") : TEXT("no"),
            LastCommittedSnapshotRevision);
        return false;
    }

    ++WorldRevision;
    CaptureCommittedRollbackSnapshot();
    SetPlayerWorldHold(false);
    bRollbackInProgress = false;

    UE_LOG(
        LogTemp,
        Warning,
        TEXT("ShireWorldCommit: rollback-pass chapter=%s route=%s episode=%s builder=%s revision=%u"),
        *RestoreChapterId.ToString(),
        *RestoreRouteId.ToString(),
        *RestoreEpisodeId.ToString(),
        *RestoredBuilderName.ToString(),
        WorldRevision);

    OnWorldCommitted.Broadcast(WorldRevision);
    return true;
}

void AChapterWorldRouter::RollbackFailedWorldSwap(
    FName PreviousChapterId,
    FName PreviousRouteId)
{
    if (AssetStreamingSubsystem)
    {
        AssetStreamingSubsystem->CancelPendingRequest();
    }

    PendingRouteId = NAME_None;
    PendingEpisodeId = NAME_None;
    PendingChapterId = NAME_None;
    bPendingRestoreRouteTransform = false;
    SetPlayerWorldHold(true);

    if (!RestoreCommittedWorldFromSnapshot(PreviousChapterId, PreviousRouteId))
    {
        UE_LOG(
            LogTemp,
            Error,
            TEXT("ShireWorldCommit: rollback unavailable or incomplete previousChapter=%s previousRoute=%s movementHeld=yes"),
            *PreviousChapterId.ToString(),
            *PreviousRouteId.ToString());
    }
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

    const bool bSupported =
        RouteId == TEXT("GandalfParallel") ||
        ChapterId == TEXT("P1C01") ||
        ChapterId == TEXT("P1C02") ||
        ChapterId == TEXT("P1C03") ||
        ChapterId == TEXT("P1C04") ||
        ChapterId == TEXT("P1C05") ||
        ChapterId == TEXT("P1C06") ||
        ChapterId == TEXT("P1C07") ||
        ChapterId == TEXT("P1C08");
    if (!bSupported)
    {
        UE_LOG(
            LogTemp,
            Error,
            TEXT("ShireWorldCommit: rejected unsupported chapter=%s route=%s"),
            *ChapterId.ToString(),
            *RouteId.ToString());
        if (AssetStreamingSubsystem)
        {
            AssetStreamingSubsystem->CancelPendingRequest();
        }
        PendingRouteId = NAME_None;
        PendingEpisodeId = NAME_None;
        PendingChapterId = NAME_None;
        bPendingRestoreRouteTransform = false;
        return;
    }

    const FName PreviousChapterId = LastLoadedChapterId;
    const FName PreviousRouteId = LastLoadedRouteId;

    SetPlayerWorldHold(true);
    ClearPrototypeBuilders();

    FName BuilderName = NAME_None;
    AActor* BuiltWorld = SpawnWorldForRequest(ChapterId, RouteId, BuilderName);
    if (!BuiltWorld)
    {
        UE_LOG(
            LogTemp,
            Error,
            TEXT("ShireWorldCommit: builder-failed chapter=%s route=%s"),
            *ChapterId.ToString(),
            *RouteId.ToString());
        RollbackFailedWorldSwap(PreviousChapterId, PreviousRouteId);
        return;
    }

    if (!MovePlayerToChapterStart(ChapterId, bRestoreRouteTransform))
    {
        UE_LOG(
            LogTemp,
            Error,
            TEXT("ShireWorldCommit: grounding-failed chapter=%s route=%s"),
            *ChapterId.ToString(),
            *RouteId.ToString());
        RollbackFailedWorldSwap(PreviousChapterId, PreviousRouteId);
        return;
    }

    if (AssetStreamingSubsystem &&
        !AssetStreamingSubsystem->CommitPendingRequest(ChapterId, RouteId))
    {
        UE_LOG(
            LogTemp,
            Error,
            TEXT("ShireWorldCommit: asset-commit-failed chapter=%s route=%s"),
            *ChapterId.ToString(),
            *RouteId.ToString());
        RollbackFailedWorldSwap(PreviousChapterId, PreviousRouteId);
        return;
    }

    LastLoadedRouteId = RouteId;
    LastLoadedEpisodeId = EpisodeId;
    LastLoadedChapterId = ChapterId;
    PendingRouteId = NAME_None;
    PendingEpisodeId = NAME_None;
    PendingChapterId = NAME_None;
    bPendingRestoreRouteTransform = false;
    ++WorldRevision;
    CaptureCommittedRollbackSnapshot();

    if (RouteId == TEXT("FrodoMain") && ChapterId == TEXT("P1C01"))
    {
        UE_LOG(
            LogTemp,
            Display,
            TEXT("ShirePlayableStartup: chapter=P1C01 route=%s"),
            *RouteId.ToString());
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireChapterAudit: loaded=%s builder=%s route=%s streamed=committed revision=%u"),
        *ChapterId.ToString(),
        *BuilderName.ToString(),
        *RouteId.ToString(),
        WorldRevision);
    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireWorldCommit: PASS chapter=%s route=%s episode=%s revision=%u"),
        *ChapterId.ToString(),
        *RouteId.ToString(),
        *EpisodeId.ToString(),
        WorldRevision);

    OnWorldCommitted.Broadcast(WorldRevision);
}

