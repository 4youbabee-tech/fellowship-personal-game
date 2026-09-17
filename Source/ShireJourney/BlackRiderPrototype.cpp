#include "BlackRiderPrototype.h"
#include "ShireHUD.h"
#include "ShireQuestSubsystem.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/GameInstance.h"
#include "GameFramework/Character.h"
#include "GameFramework/PlayerController.h"
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

void ABlackRiderPrototype::BeginPlay()
{
    Super::BeginPlay();
    if (PatrolA.IsNearlyZero() && PatrolB.Equals(FVector(900.0f, 0.0f, 0.0f)))
    {
        PatrolA = GetActorLocation();
        PatrolB = GetActorLocation() + FVector(900.0f, 0.0f, 0.0f);
    }
}

void ABlackRiderPrototype::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    UpdatePatrol(DeltaSeconds);
    CheckPlayerDetection();
}

void ABlackRiderPrototype::UpdatePatrol(float DeltaSeconds)
{
    const FVector Target = bHeadingToB ? PatrolB : PatrolA;
    const FVector ToTarget = Target - GetActorLocation();
    if (ToTarget.Size2D() < 45.0f)
    {
        bHeadingToB = !bHeadingToB;
        return;
    }

    const FVector Direction = ToTarget.GetSafeNormal2D();
    AddActorWorldOffset(Direction * PatrolSpeed * DeltaSeconds, true);
    SetActorRotation(Direction.Rotation());
}

void ABlackRiderPrototype::CheckPlayerDetection()
{
    if (!GetWorld())
    {
        return;
    }

    APlayerController* PC = GetWorld()->GetFirstPlayerController();
    ACharacter* Player = PC ? Cast<ACharacter>(PC->GetPawn()) : nullptr;
    if (!Player)
    {
        return;
    }

    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!Quests || Quests->GetActiveQuestId() != TEXT("KeepOffRoad"))
    {
        return;
    }

    const float Radius = Player->bIsCrouched ? CrouchedDetectionRadius : DetectionRadius;
    const FVector ToPlayer = Player->GetActorLocation() - GetActorLocation();
    if (ToPlayer.Size2D() > Radius)
    {
        return;
    }

    const float Facing = FVector::DotProduct(GetActorForwardVector().GetSafeNormal2D(), ToPlayer.GetSafeNormal2D());
    if (Facing < -0.1f)
    {
        return;
    }

    if (GetWorld()->GetTimeSeconds() >= NextAlertTime)
    {
        if (Quests->GetQuestStage(TEXT("KeepOffRoad")) == 0)
        {
            Quests->SetQuestStage(TEXT("KeepOffRoad"), 1);
        }

        if (PC)
        {
            if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
            {
                HUD->ShowAlert(FText::FromString(TEXT("The Rider has noticed movement. Stay low and break line of sight.")), 3.0f);
            }
        }
        NextAlertTime = GetWorld()->GetTimeSeconds() + 5.0f;
    }
}
