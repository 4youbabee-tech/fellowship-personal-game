#include "BlackRiderPrototype.h"
#include "ShireHUD.h"
#include "ShireQuestSubsystem.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/PlayerController.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

ABlackRiderPrototype::ABlackRiderPrototype()
{
    PrimaryActorTick.bCanEverTick = true;

    Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    RootComponent = Root;

    HorseBody = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("HorseBody"));
    HorseBody->SetupAttachment(Root);
    HorseBody->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    HorseBody->SetRelativeLocation(FVector(0.0f, 0.0f, 55.0f));
    HorseBody->SetRelativeScale3D(FVector(1.05f, 0.42f, 0.55f));

    RiderBody = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RiderBody"));
    RiderBody->SetupAttachment(Root);
    RiderBody->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    RiderBody->SetRelativeLocation(FVector(0.0f, 0.0f, 135.0f));
    RiderBody->SetRelativeScale3D(FVector(0.35f, 0.35f, 0.75f));

    RiderHead = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RiderHead"));
    RiderHead->SetupAttachment(Root);
    RiderHead->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    RiderHead->SetRelativeLocation(FVector(0.0f, 0.0f, 205.0f));
    RiderHead->SetRelativeScale3D(FVector(0.26f));

    static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    if (CubeMesh.Succeeded()) HorseBody->SetStaticMesh(CubeMesh.Object);
    if (CylinderMesh.Succeeded()) RiderBody->SetStaticMesh(CylinderMesh.Object);
    if (SphereMesh.Succeeded()) RiderHead->SetStaticMesh(SphereMesh.Object);
}

void ABlackRiderPrototype::ApplyPrototypeStyle()
{
    UMaterialInterface* BasicMaterial = LoadObject<UMaterialInterface>(
        nullptr, TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
    if (!BasicMaterial)
    {
        return;
    }

    auto ApplyColor = [this, BasicMaterial](UStaticMeshComponent* Component, const FLinearColor& Color)
    {
        if (!Component)
        {
            return;
        }

        if (UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(BasicMaterial, this))
        {
            MID->SetVectorParameterValue(TEXT("Color"), Color);
            Component->SetMaterial(0, MID);
        }
    };

    ApplyColor(HorseBody, FLinearColor(0.055f, 0.045f, 0.040f));
    ApplyColor(RiderBody, FLinearColor(0.025f, 0.025f, 0.030f));
    ApplyColor(RiderHead, FLinearColor(0.015f, 0.015f, 0.018f));
}

void ABlackRiderPrototype::UpdateRideMotion(float DeltaSeconds)
{
    RidePhase += DeltaSeconds * 6.0f;
    const float HorseBob = FMath::Sin(RidePhase * 2.0f) * 1.8f;
    const float RiderBob = FMath::Sin(RidePhase * 2.0f + 0.35f) * 1.4f;

    HorseBody->SetRelativeLocation(FVector(0.0f, 0.0f, 55.0f + HorseBob));
    RiderBody->SetRelativeLocation(FVector(0.0f, 0.0f, 135.0f + RiderBob));
    RiderHead->SetRelativeLocation(FVector(0.0f, 0.0f, 205.0f + RiderBob));
}

void ABlackRiderPrototype::BeginPlay()
{
    Super::BeginPlay();
    ApplyPrototypeStyle();
    if (PatrolA.IsNearlyZero() && PatrolB.Equals(FVector(900.0f, 0.0f, 0.0f)))
    {
        PatrolA = GetActorLocation();
        PatrolB = GetActorLocation() + FVector(900.0f, 0.0f, 0.0f);
    }

    UGameInstance* GI = GetGameInstance();
    QuestSubsystem = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (QuestSubsystem)
    {
        QuestSubsystem->OnActiveQuestChanged.AddDynamic(this, &ABlackRiderPrototype::HandleActiveQuestChanged);
        HandleActiveQuestChanged(QuestSubsystem->GetActiveQuestId());
    }
    else
    {
        bDetectionQuestActive = false;
        NextDetectionCheckTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0f;
    }
}

void ABlackRiderPrototype::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (QuestSubsystem)
    {
        QuestSubsystem->OnActiveQuestChanged.RemoveDynamic(this, &ABlackRiderPrototype::HandleActiveQuestChanged);
        QuestSubsystem = nullptr;
    }

    Super::EndPlay(EndPlayReason);
}

void ABlackRiderPrototype::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (bInvestigating)
    {
        InvestigationRemaining = FMath::Max(0.0f, InvestigationRemaining - DeltaSeconds);
        if (InvestigationRemaining <= 0.0f)
        {
            bInvestigating = false;
        }
    }

    UpdatePatrol(DeltaSeconds);
    UpdateRideMotion(DeltaSeconds);

    if (!bDetectionQuestActive || !GetWorld())
    {
        return;
    }

    const float Now = GetWorld()->GetTimeSeconds();
    if (Now >= NextDetectionCheckTime)
    {
        NextDetectionCheckTime = Now + FMath::Max(0.05f, DetectionCheckInterval);
        CheckPlayerDetection();
    }
}

void ABlackRiderPrototype::HandleActiveQuestChanged(FName QuestId)
{
    bDetectionQuestActive = QuestId == TEXT("KeepOffRoad");
    bInvestigating = false;
    InvestigationRemaining = 0.0f;
    ResetDetectionConfidence();

    if (GetWorld())
    {
        NextDetectionCheckTime = GetWorld()->GetTimeSeconds();
    }
}

void ABlackRiderPrototype::UpdatePatrol(float DeltaSeconds)
{
    const FVector Target = bInvestigating ? LastKnownPlayerLocation : (bHeadingToB ? PatrolB : PatrolA);
    const FVector ToTarget = Target - GetActorLocation();

    const float AcceptanceRadius = bInvestigating ? 70.0f : 45.0f;
    if (ToTarget.Size2D() < AcceptanceRadius)
    {
        if (bInvestigating)
        {
            bInvestigating = false;
            InvestigationRemaining = 0.0f;
        }
        else
        {
            bHeadingToB = !bHeadingToB;
        }
        return;
    }

    const FVector Direction = ToTarget.GetSafeNormal2D();
    const float Speed = bInvestigating ? PatrolSpeed * InvestigationSpeedMultiplier : PatrolSpeed;
    AddActorWorldOffset(Direction * Speed * DeltaSeconds, true);
    SetActorRotation(FMath::RInterpTo(GetActorRotation(), Direction.Rotation(), DeltaSeconds, bInvestigating ? 4.5f : 3.0f));
}

bool ABlackRiderPrototype::HasLineOfSightToPlayer(ACharacter* Player) const
{
    if (!Player || !GetWorld())
    {
        return false;
    }

    const FVector Start = GetActorLocation() + FVector(0.0f, 0.0f, 165.0f);
    const FVector End = Player->GetActorLocation() + FVector(0.0f, 0.0f, 45.0f);

    // Greybox cover uses simple collision, so a simple visibility trace is both sufficient and cheaper
    // than a complex triangle trace on the low-spec target.
    FCollisionQueryParams Params(SCENE_QUERY_STAT(BlackRiderSight), false, this);
    Params.AddIgnoredActor(this);

    FHitResult Hit;
    const bool bHit = GetWorld()->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Params);
    if (!bHit)
    {
        // Nothing blocks the trace before the target point.
        return true;
    }

    return Hit.GetActor() == Player;
}

void ABlackRiderPrototype::ResetDetectionConfidence()
{
    ConsecutiveVisibleChecks = 0;
}

void ABlackRiderPrototype::CheckPlayerDetection()
{
    if (!GetWorld() || !QuestSubsystem || !bDetectionQuestActive)
    {
        ResetDetectionConfidence();
        return;
    }

    APlayerController* PC = GetWorld()->GetFirstPlayerController();
    ACharacter* Player = PC ? Cast<ACharacter>(PC->GetPawn()) : nullptr;
    if (!Player)
    {
        ResetDetectionConfidence();
        return;
    }

    const float Radius = Player->bIsCrouched ? CrouchedDetectionRadius : DetectionRadius;
    FVector ToPlayer = Player->GetActorLocation() - GetActorLocation();
    ToPlayer.Z = 0.0f;
    if (ToPlayer.SizeSquared() > FMath::Square(Radius))
    {
        ResetDetectionConfidence();
        return;
    }

    const FVector DirectionToPlayer = ToPlayer.GetSafeNormal();
    const float Facing = FVector::DotProduct(GetActorForwardVector().GetSafeNormal2D(), DirectionToPlayer);
    if (Facing < MinimumFacingDot)
    {
        ResetDetectionConfidence();
        return;
    }

    if (!HasLineOfSightToPlayer(Player))
    {
        ResetDetectionConfidence();
        return;
    }

    LastKnownPlayerLocation = Player->GetActorLocation();
    bInvestigating = true;
    InvestigationRemaining = InvestigationDuration;

    const int32 RequiredChecks = FMath::Max(1, RequiredVisibleChecks);
    ConsecutiveVisibleChecks = FMath::Min(ConsecutiveVisibleChecks + 1, RequiredChecks);
    if (ConsecutiveVisibleChecks < RequiredChecks)
    {
        return;
    }

    const float Now = GetWorld()->GetTimeSeconds();
    if (Now >= NextAlertTime)
    {
        if (QuestSubsystem->GetQuestStage(TEXT("KeepOffRoad")) == 0)
        {
            QuestSubsystem->SetQuestStage(TEXT("KeepOffRoad"), 1);
        }

        if (AShireHUD* HUD = PC ? Cast<AShireHUD>(PC->GetHUD()) : nullptr)
        {
            HUD->ShowAlert(FText::FromString(TEXT("The Rider has noticed movement. Stay low and break line of sight.")), 3.0f);
        }

        NextAlertTime = Now + 5.0f;
    }
}
