#include "ChapterWorldRouter.h"

#include "BlackRiderPrototype.h"
#include "BreePrototypeWorldBuilder.h"
#include "FellowshipChapterWorldBuilder.h"
#include "FellowshipEnemyPrototype.h"
#include "IsengardPrototypeWorldBuilder.h"
#include "ShireAmbientNPC.h"
#include "ShireChapterAssetStreamingSubsystem.h"
#include "ShireNPC.h"
#include "ShireNPCContextSubsystem.h"
#include "ShirePlayerCharacter.h"
#include "ShirePrototypeWorldBuilder.h"
#include "WorldDetailCluster.h"
#include "ShireQuestSubsystem.h"
#include "ShireQuestTrigger.h"
#include "ShireSaveGame.h"

#include "Engine/GameInstance.h"
#include "Engine/EngineTypes.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/TextRenderActor.h"
#include "Engine/World.h"
#include "Components/CapsuleComponent.h"
#include "CollisionShape.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/DefaultValueHelper.h"
#include "Misc/Parse.h"
#include "TimerManager.h"
#include "UnrealClient.h"

namespace ShireGrounding
{
    static constexpr float GroundingStabilitySeconds = 2.0f;
}

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

    Quests->OnWorldTransitionRequested.AddUObject(
        this,
        &AChapterWorldRouter::HandleWorldTransitionRequested);
    Quests->OnChapterChanged.AddDynamic(this, &AChapterWorldRouter::HandleChapterChanged);
    Quests->OnExperienceChanged.AddDynamic(this, &AChapterWorldRouter::HandleExperienceChanged);

    AssetStreamingSubsystem = GI->GetSubsystem<UShireChapterAssetStreamingSubsystem>();
    if (AssetStreamingSubsystem)
    {
        AssetStreamingSubsystem->OnChapterAssetsReady.AddUObject(
            this,
            &AChapterWorldRouter::HandleChapterAssetsReady);
        AssetStreamingSubsystem->OnChapterAssetsFailed.AddUObject(
            this,
            &AChapterWorldRouter::HandleChapterAssetsFailed);
    }

    SetPlayerWorldHold(true);
    LoadChapterWorld(Quests->GetCurrentChapterId());
}

void AChapterWorldRouter::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (UGameInstance* GI = GetGameInstance())
    {
        if (UShireQuestSubsystem* Quests = GI->GetSubsystem<UShireQuestSubsystem>())
        {
            Quests->OnWorldTransitionRequested.RemoveAll(this);
        }
    }

    if (AssetStreamingSubsystem)
    {
        AssetStreamingSubsystem->OnChapterAssetsReady.RemoveAll(this);
        AssetStreamingSubsystem->OnChapterAssetsFailed.RemoveAll(this);
        AssetStreamingSubsystem = nullptr;
    }

    GetWorldTimerManager().ClearTimer(P1C01VisualPoseTimer);
    GetWorldTimerManager().ClearTimer(P1C01VisualScreenshotTimer);
    P1C01VisualCaptureRevision = 0;
    LastCommittedRollbackSnapshot = nullptr;
    Super::EndPlay(EndPlayReason);
}

void AChapterWorldRouter::HandleWorldTransitionRequested(
    FName TargetChapterId,
    FName TargetRouteId,
    FName TargetEpisodeId)
{
    if (bRollbackInProgress)
    {
        return;
    }

    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!Quests)
    {
        SetPlayerWorldHold(true);
        return;
    }

    // Capture the exact live origin only while it is still fully committed.
    // Rapid A -> pending B -> A requests must not overwrite the A snapshot with
    // B's uncommitted logical state.
    if (IsWorldCommitted(
            Quests->GetCurrentChapterId(),
            Quests->GetCurrentRouteId(),
            Quests->GetCurrentEpisodeId()))
    {
        CaptureCommittedRollbackSnapshot();
    }

    SetPlayerWorldHold(true);
    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireWorldTransaction: BEGIN origin=%s/%s/%s target=%s/%s/%s revision=%u"),
        *Quests->GetCurrentChapterId().ToString(),
        *Quests->GetCurrentRouteId().ToString(),
        *Quests->GetCurrentEpisodeId().ToString(),
        *TargetChapterId.ToString(),
        *TargetRouteId.ToString(),
        *TargetEpisodeId.ToString(),
        WorldRevision);
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
    // Decorative HISM clusters are independent actors, not children destroyed with
    // their Shire builder. Clear them on every chapter unload to prevent stale
    // instanced meshes and memory from accumulating after save/load transitions.
    DestroyTaggedOfClass(AWorldDetailCluster::StaticClass(), TEXT("RuntimePrototypeGenerated"));
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
    if (AShirePlayerCharacter* ShirePlayer = Cast<AShirePlayerCharacter>(Character))
    {
        ShirePlayer->SetWorldTransitionHeld(bHold);
    }

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

    // Grounding is a world-level invariant, not a chapter-specific patch. Authored
    // starts and restored transforms can land close to a seam between collision
    // surfaces as production geometry changes. Probe the requested point first, then
    // a small deterministic ring around it and choose the closest blocking surface.
    // The 240 cm maximum correction is intentionally bounded so a bad world build
    // still fails rather than silently teleporting the player across the scene.
    static const FVector2D GroundProbeOffsets[] =
    {
        FVector2D(0.0f, 0.0f),
        FVector2D(90.0f, 0.0f),
        FVector2D(-90.0f, 0.0f),
        FVector2D(0.0f, 90.0f),
        FVector2D(0.0f, -90.0f),
        FVector2D(130.0f, 130.0f),
        FVector2D(130.0f, -130.0f),
        FVector2D(-130.0f, 130.0f),
        FVector2D(-130.0f, -130.0f),
        FVector2D(180.0f, 0.0f),
        FVector2D(-180.0f, 0.0f),
        FVector2D(0.0f, 180.0f),
        FVector2D(0.0f, -180.0f),
        FVector2D(240.0f, 0.0f),
        FVector2D(-240.0f, 0.0f),
        FVector2D(0.0f, 240.0f),
        FVector2D(0.0f, -240.0f)
    };

    float CapsuleHalfHeight = 60.0f;
    float CapsuleRadius = 34.0f;
    if (const ACharacter* Character = Cast<ACharacter>(PlayerPawn))
    {
        if (const UCapsuleComponent* Capsule = Character->GetCapsuleComponent())
        {
            CapsuleHalfHeight = Capsule->GetScaledCapsuleHalfHeight();
            CapsuleRadius = Capsule->GetScaledCapsuleRadius();
        }
    }

    FCollisionQueryParams QueryParams(FName(TEXT("ShireChapterSpawnGround")), false, PlayerPawn);
    bool bFoundGround = false;
    float BestDistanceSq = TNumericLimits<float>::Max();
    FVector BestLocation = FVector::ZeroVector;
    FVector2D BestOffset = FVector2D::ZeroVector;

    for (const FVector2D& Offset : GroundProbeOffsets)
    {
        const FVector ProbeLocation(
            RequestedLocation.X + Offset.X,
            RequestedLocation.Y + Offset.Y,
            RequestedLocation.Z);
        const FVector TraceStart = ProbeLocation + FVector(0.0f, 0.0f, 650.0f);
        const FVector TraceEnd = ProbeLocation - FVector(0.0f, 0.0f, 2200.0f);

        FHitResult GroundHit;
        if (!GetWorld()->LineTraceSingleByChannel(
                GroundHit,
                TraceStart,
                TraceEnd,
                ECC_Visibility,
                QueryParams) ||
            !GroundHit.bBlockingHit ||
            GroundHit.ImpactNormal.Z < 0.55f)
        {
            continue;
        }

        FVector CandidateLocation = ProbeLocation;
        CandidateLocation.Z = GroundHit.ImpactPoint.Z + CapsuleHalfHeight + 4.0f;
        const bool bCapsuleBlocked = GetWorld()->OverlapBlockingTestByChannel(
            CandidateLocation,
            FQuat::Identity,
            ECC_Pawn,
            FCollisionShape::MakeCapsule(CapsuleRadius, CapsuleHalfHeight),
            QueryParams);
        if (bCapsuleBlocked)
        {
            continue;
        }

        const float DistanceSq = Offset.SizeSquared();
        if (DistanceSq >= BestDistanceSq)
        {
            continue;
        }

        BestDistanceSq = DistanceSq;
        BestOffset = Offset;
        BestLocation = CandidateLocation;
        bFoundGround = true;
    }

    if (!bFoundGround)
    {
        return false;
    }

    OutGroundedLocation = BestLocation;
    if (!BestOffset.IsNearlyZero())
    {
        UE_LOG(
            LogTemp,
            Warning,
            TEXT("ShireStartupGrounding: adjusted-to-nearby-ground offset=(%.1f,%.1f) requested=(%.1f,%.1f,%.1f) grounded=(%.1f,%.1f,%.1f)"),
            BestOffset.X,
            BestOffset.Y,
            RequestedLocation.X,
            RequestedLocation.Y,
            RequestedLocation.Z,
            OutGroundedLocation.X,
            OutGroundedLocation.Y,
            OutGroundedLocation.Z);
    }
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

    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireStartupGrounding: PLACED chapter=%s source=%s requestedZ=%.1f groundedZ=%.1f"),
        *ChapterId.ToString(),
        bUsingSavedTransform ? TEXT("saved-route") : TEXT("chapter-start"),
        RequestedLocation.Z,
        GroundedLocation.Z);

    return true;
}

void AChapterWorldRouter::VerifyPlayerGroundingStability(FName ChapterId, FVector PlacedLocation)
{
    if (PendingGroundingCommitChapterId != ChapterId ||
        PendingGroundingCommitRouteId == NAME_None ||
        PendingGroundingCommitEpisodeId == NAME_None)
    {
        return;
    }

    APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
    ACharacter* Character = Cast<ACharacter>(PlayerPawn);
    UCharacterMovementComponent* Movement = Character ? Character->GetCharacterMovement() : nullptr;
    if (!PlayerPawn || !Movement)
    {
        UE_LOG(
            LogTemp,
            Error,
            TEXT("ShireStartupGrounding: FAIL chapter=%s reason=stability-player-missing"),
            *ChapterId.ToString());
        RollbackFailedWorldSwap(LastLoadedChapterId, LastLoadedRouteId);
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
        if (GroundingRecoveryAttempts < 1)
        {
            FVector RecoveryLocation;
            if (ResolveGroundedSpawnLocation(
                    PlayerPawn,
                    PendingGroundingPlacedLocation,
                    RecoveryLocation))
            {
                ++GroundingRecoveryAttempts;
                PlayerPawn->SetActorLocation(
                    RecoveryLocation,
                    false,
                    nullptr,
                    ETeleportType::TeleportPhysics);
                Movement->StopMovementImmediately();
                Movement->SetMovementMode(MOVE_Walking);
                PendingGroundingPlacedLocation = RecoveryLocation;

                FTimerDelegate RetryDelegate = FTimerDelegate::CreateUObject(
                    this,
                    &AChapterWorldRouter::VerifyPlayerGroundingStability,
                    ChapterId,
                    RecoveryLocation);
                GetWorldTimerManager().SetTimer(
                    GroundingStabilityTimer,
                    RetryDelegate,
                    ShireGrounding::GroundingStabilitySeconds,
                    false);

                UE_LOG(
                    LogTemp,
                    Warning,
                    TEXT("ShireStartupGrounding: RECOVERY chapter=%s attempt=%d ground=%s falling=%s drop=%.1f drift=%.1f"),
                    *ChapterId.ToString(),
                    GroundingRecoveryAttempts,
                    bHasBlockingGround ? TEXT("yes") : TEXT("no"),
                    Movement->IsFalling() ? TEXT("yes") : TEXT("no"),
                    VerticalDrop,
                    HorizontalDrift);
                return;
            }
        }

        UE_LOG(
            LogTemp,
            Error,
            TEXT("ShireStartupGrounding: FAIL chapter=%s reason=unstable-commit-barrier ground=%s falling=%s drop=%.1f drift=%.1f current=(%.1f,%.1f,%.1f)"),
            *ChapterId.ToString(),
            bHasBlockingGround ? TEXT("yes") : TEXT("no"),
            Movement->IsFalling() ? TEXT("yes") : TEXT("no"),
            VerticalDrop,
            HorizontalDrift,
            CurrentLocation.X,
            CurrentLocation.Y,
            CurrentLocation.Z);

        PendingGroundingCommitChapterId = NAME_None;
        PendingGroundingCommitRouteId = NAME_None;
        PendingGroundingCommitEpisodeId = NAME_None;
        PendingGroundingBuilderName = NAME_None;
        GroundingRecoveryAttempts = 0;
        RollbackFailedWorldSwap(LastLoadedChapterId, LastLoadedRouteId);
        return;
    }

    const FName CommittedChapterId = PendingGroundingCommitChapterId;
    const FName CommittedRouteId = PendingGroundingCommitRouteId;
    const FName CommittedEpisodeId = PendingGroundingCommitEpisodeId;
    const FName CommittedBuilderName = PendingGroundingBuilderName;

    LastLoadedRouteId = CommittedRouteId;
    LastLoadedEpisodeId = CommittedEpisodeId;
    LastLoadedChapterId = CommittedChapterId;
    PendingRouteId = NAME_None;
    PendingEpisodeId = NAME_None;
    PendingChapterId = NAME_None;
    bPendingRestoreRouteTransform = false;
    ++WorldRevision;

    if (UGameInstance* ContextGI = GetGameInstance())
    {
        if (UShireNPCContextSubsystem* NPCContext =
                ContextGI->GetSubsystem<UShireNPCContextSubsystem>())
        {
            UShireQuestSubsystem* ContextQuests =
                ContextGI->GetSubsystem<UShireQuestSubsystem>();
            NPCContext->SetCommittedWorldContext(
                CommittedChapterId,
                CommittedRouteId,
                CommittedEpisodeId,
                WorldRevision,
                ContextQuests ? ContextQuests->GetActiveQuestId() : NAME_None,
                ContextQuests ? ContextQuests->GetActiveQuestStage() : 0);
        }
    }

    if (UGameInstance* QuestGI = GetGameInstance())
    {
        if (UShireQuestSubsystem* CommitQuests =
                QuestGI->GetSubsystem<UShireQuestSubsystem>())
        {
            CommitQuests->CommitWorldBoundState();
        }
    }

    PendingGroundingCommitChapterId = NAME_None;
    PendingGroundingCommitRouteId = NAME_None;
    PendingGroundingCommitEpisodeId = NAME_None;
    PendingGroundingBuilderName = NAME_None;
    GroundingRecoveryAttempts = 0;

    CaptureCommittedRollbackSnapshot();

    if (CommittedRouteId == TEXT("FrodoMain") && CommittedChapterId == TEXT("P1C01"))
    {
        UE_LOG(
            LogTemp,
            Display,
            TEXT("ShirePlayableStartup: chapter=P1C01 route=%s"),
            *CommittedRouteId.ToString());
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireStartupGrounding: PASS chapter=%s commitBarrier=yes stableSeconds=2.0 ground=yes drop=%.1f drift=%.1f"),
        *CommittedChapterId.ToString(),
        VerticalDrop,
        HorizontalDrift);
    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireChapterAudit: loaded=%s builder=%s route=%s streamed=committed revision=%u"),
        *CommittedChapterId.ToString(),
        *CommittedBuilderName.ToString(),
        *CommittedRouteId.ToString(),
        WorldRevision);
    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireWorldCommit: PASS chapter=%s route=%s episode=%s revision=%u"),
        *CommittedChapterId.ToString(),
        *CommittedRouteId.ToString(),
        *CommittedEpisodeId.ToString(),
        WorldRevision);

    OnWorldCommitted.Broadcast(WorldRevision);
    SetPlayerWorldHold(false);
    if (CommittedChapterId == TEXT("P1C01") && CommittedRouteId == TEXT("FrodoMain"))
    {
        QueueP1C01VisualCapture();
    }
}

void AChapterWorldRouter::QueueP1C01VisualCapture()
{
    // Never interfere with an ordinary game, PIE session or other chapters.
    if (!GetWorld() || !FParse::Param(FCommandLine::Get(), TEXT("ShireVisualCapture")))
    {
        return;
    }

    P1C01VisualCaptureRevision = WorldRevision;
    GetWorldTimerManager().SetTimer(
        P1C01VisualPoseTimer,
        this,
        &AChapterWorldRouter::PositionP1C01VisualCamera,
        0.75f,
        false);
}

void AChapterWorldRouter::PositionP1C01VisualCamera()
{
    if (P1C01VisualCaptureRevision == 0 ||
        P1C01VisualCaptureRevision != WorldRevision ||
        LastLoadedChapterId != TEXT("P1C01") ||
        LastLoadedRouteId != TEXT("FrodoMain") ||
        bPlayerWorldHoldActive)
    {
        UE_LOG(LogTemp, Error, TEXT("P1C01_RENDER_CAPTURE_FAIL reason=world_revision_not_committed"));
        return;
    }

    // UE4 command-line Value parsing does not preserve comma-delimited tokens
    // reliably. Pass one numeric scalar per switch instead.
    static const TCHAR* PoseKeys[6] =
    {
        TEXT("ShireCaptureX="),
        TEXT("ShireCaptureY="),
        TEXT("ShireCaptureZ="),
        TEXT("ShireCapturePitch="),
        TEXT("ShireCaptureYaw="),
        TEXT("ShireCaptureRoll=")
    };

    float Values[6] = {};
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(PoseKeys); ++Index)
    {
        FString Scalar;
        if (!FParse::Value(FCommandLine::Get(), PoseKeys[Index], Scalar))
        {
            UE_LOG(LogTemp, Error,
                TEXT("P1C01_RENDER_CAPTURE_FAIL reason=camera_pose_argument_missing key=%s"),
                PoseKeys[Index]);
            return;
        }
        if (!FDefaultValueHelper::ParseFloat(Scalar, Values[Index]) ||
            !FMath::IsFinite(Values[Index]))
        {
            UE_LOG(LogTemp, Error,
                TEXT("P1C01_RENDER_CAPTURE_FAIL reason=camera_pose_invalid_numeric key=%s value=%s"),
                PoseKeys[Index], *Scalar);
            return;
        }
    }

    const FString PoseString = FString::Printf(
        TEXT("%.3f,%.3f,%.3f,%.3f,%.3f,%.3f"),
        Values[0], Values[1], Values[2], Values[3], Values[4], Values[5]);

    APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
    if (!PC)
    {
        UE_LOG(LogTemp, Error, TEXT("P1C01_RENDER_CAPTURE_FAIL reason=controller_unavailable"));
        return;
    }

    // BugItGo is only issued AFTER the chapter grounding barrier. Previously
    // ExecCmds teleported during world hold, causing recovery and pre-commit shots.
    PC->ConsoleCommand(FString::Printf(
        TEXT("BugItGo %.3f %.3f %.3f %.3f %.3f %.3f"),
        Values[0], Values[1], Values[2], Values[3], Values[4], Values[5]), true);

    UE_LOG(LogTemp, Display,
        TEXT("P1C01_RENDER_CAMERA_READY chapter=P1C01 worldCommitted=yes revision=%u pose=%s"),
        WorldRevision, *PoseString);

    // Give the viewport multiple frames to settle after camera reposition.
    GetWorldTimerManager().SetTimer(
        P1C01VisualScreenshotTimer,
        this,
        &AChapterWorldRouter::RequestP1C01VisualScreenshot,
        1.25f,
        false);
}

void AChapterWorldRouter::RequestP1C01VisualScreenshot()
{
    if (P1C01VisualCaptureRevision == 0 ||
        P1C01VisualCaptureRevision != WorldRevision ||
        LastLoadedChapterId != TEXT("P1C01") ||
        LastLoadedRouteId != TEXT("FrodoMain") ||
        bPlayerWorldHoldActive)
    {
        UE_LOG(LogTemp, Error, TEXT("P1C01_RENDER_CAPTURE_FAIL reason=screenshot_world_not_committed"));
        return;
    }

    // Requested through the game viewport on the next frame. The CMD caller
    // observes a fresh screenshot file and refuses to accept pre-commit shots.
    UE_LOG(LogTemp, Display,
        TEXT("P1C01_RENDER_CAPTURE_REQUESTED chapter=P1C01 worldCommitted=yes revision=%u"),
        WorldRevision);
    FScreenshotRequest::RequestScreenshot(false);
    P1C01VisualCaptureRevision = 0;
}

void AChapterWorldRouter::LoadChapterWorld(FName ChapterId, bool bRestoreRouteTransform)
{
    if (!GetWorld())
    {
        return;
    }

    GetWorldTimerManager().ClearTimer(P1C01VisualPoseTimer);
    GetWorldTimerManager().ClearTimer(P1C01VisualScreenshotTimer);
    P1C01VisualCaptureRevision = 0;

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

        // A -> pending B -> A is complete only after stale pending work is gone.
        // During rollback this function is suppressed by bRollbackInProgress.
        if (IsWorldCommitted(ChapterId, RouteId, EpisodeId))
        {
            SetPlayerWorldHold(false);
        }
        return;
    }

    if (PendingRouteId == RouteId &&
        PendingEpisodeId == EpisodeId &&
        PendingChapterId == ChapterId)
    {
        return;
    }

    // Quest identity is destination-facing before asynchronous preload completes.
    // Hold all gameplay mutation from request time until destination publication.
    SetPlayerWorldHold(true);

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

void AChapterWorldRouter::HandleChapterAssetsFailed(
    FName ChapterId,
    FName RouteId)
{
    if (PendingChapterId != ChapterId || PendingRouteId != RouteId)
    {
        return;
    }

    const FName PreviousChapterId = LastLoadedChapterId;
    const FName PreviousRouteId = LastLoadedRouteId;
    UE_LOG(
        LogTemp,
        Error,
        TEXT("ShireWorldCommit: asset-preload-failed chapter=%s route=%s rollback=yes"),
        *ChapterId.ToString(),
        *RouteId.ToString());
    RollbackFailedWorldSwap(PreviousChapterId, PreviousRouteId);
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
    if (const AShirePlayerCharacter* PlayerCharacter = Cast<AShirePlayerCharacter>(PlayerPawn))
    {
        Snapshot->PlayerHealth = PlayerCharacter->GetCurrentHealth();
        Snapshot->PlayerStamina = PlayerCharacter->GetCurrentStamina();
        Snapshot->PlayerResolve = PlayerCharacter->GetCurrentResolve();
        Snapshot->PlayerSupplies = PlayerCharacter->GetSupplies();
    }
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

    if (!Quests->BeginPersistenceRestore())
    {
        bRollbackInProgress = false;
        UE_LOG(LogTemp, Error, TEXT("ShireWorldCommit: rollback-failed reason=persistence-transaction-busy"));
        return false;
    }

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

    if (bPlaced)
    {
        if (AShirePlayerCharacter* PlayerCharacter = Cast<AShirePlayerCharacter>(PlayerPawn))
        {
            PlayerCharacter->RestoreTransactionalPlayerState(
                Snapshot->PlayerHealth,
                Snapshot->PlayerStamina,
                Snapshot->PlayerResolve,
                Snapshot->PlayerSupplies);
            UE_LOG(
                LogTemp,
                Display,
                TEXT("ShireRollbackSnapshotApplied: health=%.1f stamina=%.1f resolve=%.1f supplies=%d"),
                Snapshot->PlayerHealth,
                Snapshot->PlayerStamina,
                Snapshot->PlayerResolve,
                Snapshot->PlayerSupplies);
        }
    }

    if (!RestoredWorld || !bPlaced)
    {
        Quests->AbortPersistenceRestore();
        LastLoadedChapterId = NAME_None;
        LastLoadedRouteId = NAME_None;
        LastLoadedEpisodeId = NAME_None;
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
    if (UGameInstance* ContextGI = GetGameInstance())
    {
        if (UShireNPCContextSubsystem* NPCContext =
                ContextGI->GetSubsystem<UShireNPCContextSubsystem>())
        {
            NPCContext->SetCommittedWorldContext(
                RestoreChapterId,
                RestoreRouteId,
                RestoreEpisodeId,
                WorldRevision,
                Quests->GetActiveQuestId(),
                Quests->GetActiveQuestStage());
        }
    }
    CaptureCommittedRollbackSnapshot();

    // Keep rollback re-entrancy suppression active while restored logical state is
    // published. Router chapter/experience handlers must not start a second load
    // before the restored world revision itself is broadcast.
    Quests->CommitPersistenceRestore(false);

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
    SetPlayerWorldHold(false);
    bRollbackInProgress = false;
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

    const FName PreviousChapterId = LastLoadedChapterId;
    const FName PreviousRouteId = LastLoadedRouteId;

    const bool bFrodoMainChapter =
        RouteId == TEXT("FrodoMain") &&
        (ChapterId == TEXT("P1C01") ||
         ChapterId == TEXT("P1C02") ||
         ChapterId == TEXT("P1C03") ||
         ChapterId == TEXT("P1C04") ||
         ChapterId == TEXT("P1C05") ||
         ChapterId == TEXT("P1C06") ||
         ChapterId == TEXT("P1C07") ||
         ChapterId == TEXT("P1C08"));
    const bool bGandalfParallel =
        RouteId == TEXT("GandalfParallel") &&
        ChapterId == TEXT("P1C01");
    const bool bSupported = bFrodoMainChapter || bGandalfParallel;
    if (!bSupported)
    {
        UE_LOG(
            LogTemp,
            Error,
            TEXT("ShireWorldCommit: rejected unsupported chapter=%s route=%s rollback=yes"),
            *ChapterId.ToString(),
            *RouteId.ToString());
        RollbackFailedWorldSwap(PreviousChapterId, PreviousRouteId);
        return;
    }

    GetWorldTimerManager().ClearTimer(GroundingStabilityTimer);
    PendingGroundingCommitChapterId = NAME_None;
    PendingGroundingCommitRouteId = NAME_None;
    PendingGroundingCommitEpisodeId = NAME_None;
    PendingGroundingBuilderName = NAME_None;
    PendingGroundingPlacedLocation = FVector::ZeroVector;
    GroundingRecoveryAttempts = 0;

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

    APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
    if (!PlayerPawn)
    {
        UE_LOG(
            LogTemp,
            Error,
            TEXT("ShireWorldCommit: grounding-barrier-failed chapter=%s route=%s reason=no-player"),
            *ChapterId.ToString(),
            *RouteId.ToString());
        RollbackFailedWorldSwap(PreviousChapterId, PreviousRouteId);
        return;
    }

    PendingGroundingCommitChapterId = ChapterId;
    PendingGroundingCommitRouteId = RouteId;
    PendingGroundingCommitEpisodeId = EpisodeId;
    PendingGroundingBuilderName = BuilderName;
    PendingGroundingPlacedLocation = PlayerPawn->GetActorLocation();
    GroundingRecoveryAttempts = 0;

    // Keep gameplay input held, but allow CharacterMovement physics to settle on the
    // blocking surface before the world is published as committed.
    if (ACharacter* Character = Cast<ACharacter>(PlayerPawn))
    {
        if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
        {
            Movement->StopMovementImmediately();
            Movement->SetMovementMode(MOVE_Walking);
        }
    }

    FTimerDelegate StabilityDelegate = FTimerDelegate::CreateUObject(
        this,
        &AChapterWorldRouter::VerifyPlayerGroundingStability,
        ChapterId,
        PendingGroundingPlacedLocation);
    GetWorldTimerManager().SetTimer(
        GroundingStabilityTimer,
        StabilityDelegate,
        ShireGrounding::GroundingStabilitySeconds,
        false);

    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireWorldCommit: grounding-barrier-pending chapter=%s route=%s episode=%s builder=%s stableSeconds=2.0"),
        *ChapterId.ToString(),
        *RouteId.ToString(),
        *EpisodeId.ToString(),
        *BuilderName.ToString());
}

