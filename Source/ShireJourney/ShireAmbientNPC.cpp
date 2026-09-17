#include "ShireAmbientNPC.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"

AShireAmbientNPC::AShireAmbientNPC()
{
    PrimaryActorTick.bCanEverTick = true;

    Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    RootComponent = Root;

    Torso = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Torso"));
    Torso->SetupAttachment(Root);
    Torso->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Torso->SetRelativeLocation(FVector(0.0f, 0.0f, 52.0f));
    Torso->SetRelativeScale3D(FVector(0.26f, 0.26f, 0.48f));

    Head = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Head"));
    Head->SetupAttachment(Root);
    Head->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Head->SetRelativeLocation(FVector(0.0f, 0.0f, 102.0f));
    Head->SetRelativeScale3D(FVector(0.20f));

    static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    if (CylinderMesh.Succeeded()) Torso->SetStaticMesh(CylinderMesh.Object);
    if (SphereMesh.Succeeded()) Head->SetStaticMesh(SphereMesh.Object);
}

void AShireAmbientNPC::BeginPlay()
{
    Super::BeginPlay();
    Random.Initialize(GetUniqueID() * 9176 + 427);
    if (RoutinePointA.IsNearlyZero())
    {
        RoutinePointA = GetActorLocation();
        RoutinePointB = GetActorLocation() + FVector(350.0f, 0.0f, 0.0f);
    }
}

void AShireAmbientNPC::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (WaitRemaining > 0.0f)
    {
        WaitRemaining -= DeltaSeconds;
        return;
    }

    const FVector Target = bHeadingToB ? RoutinePointB : RoutinePointA;
    const FVector ToTarget = Target - GetActorLocation();
    if (ToTarget.Size2D() < 25.0f)
    {
        bHeadingToB = !bHeadingToB;
        WaitRemaining = Random.FRandRange(MinWait, MaxWait);
        return;
    }

    const FVector Direction = ToTarget.GetSafeNormal2D();
    AddActorWorldOffset(Direction * WalkSpeed * DeltaSeconds, true);
    SetActorRotation(Direction.Rotation());
}
