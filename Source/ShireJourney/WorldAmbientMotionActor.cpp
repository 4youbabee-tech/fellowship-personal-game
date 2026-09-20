#include "WorldAmbientMotionActor.h"

#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"

AWorldAmbientMotionActor::AWorldAmbientMotionActor()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickInterval = 0.05f;

    Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    SetRootComponent(Root);

    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    Mesh->SetupAttachment(Root);
    Mesh->SetMobility(EComponentMobility::Movable);
    Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Mesh->SetGenerateOverlapEvents(false);
}

void AWorldAmbientMotionActor::BeginPlay()
{
    Super::BeginPlay();
    BaseLocation = GetActorLocation();
    BaseRotation = GetActorRotation();
    Phase = FMath::Fmod(
        FMath::Abs(GetActorLocation().X * 0.013f + GetActorLocation().Y * 0.017f),
        2.0f * PI);
}

void AWorldAmbientMotionActor::Configure(
    UStaticMesh* InMesh,
    EWorldAmbientMotionMode InMode,
    float InAmplitude,
    float InSpeed,
    const FVector& InScale,
    bool bInCollision)
{
    MotionMode = InMode;
    MotionAmplitude = FMath::Clamp(InAmplitude, 0.0f, 120.0f);
    MotionSpeed = FMath::Clamp(InSpeed, 0.05f, 6.0f);
    SetActorScale3D(InScale);

    if (Mesh)
    {
        Mesh->SetStaticMesh(InMesh);
        Mesh->SetCollisionEnabled(
            bInCollision ? ECollisionEnabled::QueryAndPhysics : ECollisionEnabled::NoCollision);
    }

    BaseLocation = GetActorLocation();
    BaseRotation = GetActorRotation();
}

void AWorldAmbientMotionActor::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    Phase += DeltaSeconds * MotionSpeed;
    const float Sine = FMath::Sin(Phase);
    const float Cosine = FMath::Cos(Phase * 0.73f);

    switch (MotionMode)
    {
    case EWorldAmbientMotionMode::Bob:
        SetActorLocation(BaseLocation + FVector(0.0f, 0.0f, Sine * MotionAmplitude));
        break;
    case EWorldAmbientMotionMode::Rotate:
        SetActorRotation(BaseRotation + FRotator(0.0f, DeltaSeconds * MotionSpeed * 55.0f, 0.0f));
        BaseRotation = GetActorRotation();
        break;
    case EWorldAmbientMotionMode::Shiver:
        SetActorLocation(BaseLocation + FVector(Cosine * MotionAmplitude * 0.22f, Sine * MotionAmplitude * 0.18f, 0.0f));
        SetActorRotation(BaseRotation + FRotator(Sine * 1.4f, Cosine * 2.5f, Sine * 1.0f));
        break;
    case EWorldAmbientMotionMode::Sway:
    default:
        SetActorRotation(BaseRotation + FRotator(Sine * MotionAmplitude * 0.22f, 0.0f, Cosine * MotionAmplitude));
        break;
    }
}
