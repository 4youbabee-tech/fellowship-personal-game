#include "ShireAmbientNPC.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

AShireAmbientNPC::AShireAmbientNPC()
{
    PrimaryActorTick.bCanEverTick = true;

    Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    RootComponent = Root;

    Torso = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Torso"));
    Torso->SetupAttachment(Root);
    Torso->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Torso->SetRelativeLocation(FVector(0.0f, 0.0f, 58.0f));
    Torso->SetRelativeScale3D(FVector(0.28f, 0.21f, 0.36f));

    Head = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Head"));
    Head->SetupAttachment(Root);
    Head->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Head->SetRelativeLocation(FVector(0.0f, 0.0f, 101.0f));
    Head->SetRelativeScale3D(FVector(0.22f));

    Hair = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Hair"));
    Hair->SetupAttachment(Root);
    Hair->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Hair->SetRelativeLocation(FVector(-1.0f, 0.0f, 109.0f));
    Hair->SetRelativeScale3D(FVector(0.225f, 0.225f, 0.11f));

    LeftArm = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("LeftArm"));
    LeftArm->SetupAttachment(Root);
    LeftArm->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    LeftArm->SetRelativeLocation(FVector(0.0f, -23.0f, 58.0f));
    LeftArm->SetRelativeScale3D(FVector(0.075f, 0.075f, 0.30f));

    RightArm = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RightArm"));
    RightArm->SetupAttachment(Root);
    RightArm->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    RightArm->SetRelativeLocation(FVector(0.0f, 23.0f, 58.0f));
    RightArm->SetRelativeScale3D(FVector(0.075f, 0.075f, 0.30f));

    LeftLeg = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("LeftLeg"));
    LeftLeg->SetupAttachment(Root);
    LeftLeg->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    LeftLeg->SetRelativeLocation(FVector(0.0f, -9.0f, 20.0f));
    LeftLeg->SetRelativeScale3D(FVector(0.09f, 0.09f, 0.28f));

    RightLeg = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RightLeg"));
    RightLeg->SetupAttachment(Root);
    RightLeg->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    RightLeg->SetRelativeLocation(FVector(0.0f, 9.0f, 20.0f));
    RightLeg->SetRelativeScale3D(FVector(0.09f, 0.09f, 0.28f));

    static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(TEXT("/Engine/BasicShapes/Sphere.Sphere"));

    if (CubeMesh.Succeeded())
    {
        Torso->SetStaticMesh(CubeMesh.Object);
    }
    if (CylinderMesh.Succeeded())
    {
        LeftArm->SetStaticMesh(CylinderMesh.Object);
        RightArm->SetStaticMesh(CylinderMesh.Object);
        LeftLeg->SetStaticMesh(CylinderMesh.Object);
        RightLeg->SetStaticMesh(CylinderMesh.Object);
    }
    if (SphereMesh.Succeeded())
    {
        Head->SetStaticMesh(SphereMesh.Object);
        Hair->SetStaticMesh(SphereMesh.Object);
    }
}

void AShireAmbientNPC::ApplyVisualStyle()
{
    UMaterialInterface* BasicMaterial = LoadObject<UMaterialInterface>(
        nullptr, TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
    if (!BasicMaterial)
    {
        return;
    }

    const FLinearColor Coat(
        Random.FRandRange(0.18f, 0.42f),
        Random.FRandRange(0.22f, 0.46f),
        Random.FRandRange(0.10f, 0.24f));
    const FLinearColor Trousers(
        Random.FRandRange(0.18f, 0.34f),
        Random.FRandRange(0.12f, 0.25f),
        Random.FRandRange(0.06f, 0.14f));
    const FLinearColor HairColor(
        Random.FRandRange(0.08f, 0.34f),
        Random.FRandRange(0.04f, 0.20f),
        Random.FRandRange(0.02f, 0.10f));
    const FLinearColor Skin(
        Random.FRandRange(0.64f, 0.80f),
        Random.FRandRange(0.43f, 0.58f),
        Random.FRandRange(0.28f, 0.38f));

    auto ApplyColor = [this, BasicMaterial](UStaticMeshComponent* Component, const FLinearColor& Color)
    {
        if (!Component)
        {
            return;
        }

        UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(BasicMaterial, this);
        if (MID)
        {
            MID->SetVectorParameterValue(TEXT("Color"), Color);
            Component->SetMaterial(0, MID);
        }
    };

    ApplyColor(Torso, Coat);
    ApplyColor(Head, Skin);
    ApplyColor(Hair, HairColor);
    ApplyColor(LeftArm, Coat * 0.95f);
    ApplyColor(RightArm, Coat * 0.95f);
    ApplyColor(LeftLeg, Trousers);
    ApplyColor(RightLeg, Trousers);
}

void AShireAmbientNPC::UpdateWalkAnimation(float DeltaSeconds, bool bMoving)
{
    float Swing = 0.0f;
    float Bob = 0.0f;
    if (bMoving)
    {
        WalkPhase += DeltaSeconds * 6.5f;
        Swing = FMath::Sin(WalkPhase) * 22.0f;
        Bob = FMath::Abs(FMath::Sin(WalkPhase * 2.0f)) * 1.0f;
    }

    LeftArm->SetRelativeRotation(FMath::RInterpTo(
        LeftArm->GetRelativeRotation(), FRotator(Swing, 0.0f, 0.0f), DeltaSeconds, 9.0f));
    RightArm->SetRelativeRotation(FMath::RInterpTo(
        RightArm->GetRelativeRotation(), FRotator(-Swing, 0.0f, 0.0f), DeltaSeconds, 9.0f));
    LeftLeg->SetRelativeRotation(FMath::RInterpTo(
        LeftLeg->GetRelativeRotation(), FRotator(-Swing * 0.65f, 0.0f, 0.0f), DeltaSeconds, 9.0f));
    RightLeg->SetRelativeRotation(FMath::RInterpTo(
        RightLeg->GetRelativeRotation(), FRotator(Swing * 0.65f, 0.0f, 0.0f), DeltaSeconds, 9.0f));

    Torso->SetRelativeLocation(FMath::VInterpTo(
        Torso->GetRelativeLocation(), FVector(0.0f, 0.0f, 58.0f + Bob), DeltaSeconds, 10.0f));
    Head->SetRelativeLocation(FMath::VInterpTo(
        Head->GetRelativeLocation(), FVector(0.0f, 0.0f, 101.0f + Bob), DeltaSeconds, 10.0f));
    Hair->SetRelativeLocation(FMath::VInterpTo(
        Hair->GetRelativeLocation(), FVector(-1.0f, 0.0f, 109.0f + Bob), DeltaSeconds, 10.0f));
}

void AShireAmbientNPC::BeginPlay()
{
    Super::BeginPlay();
    Random.Initialize(GetUniqueID() * 9176 + 427);
    ApplyVisualStyle();

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
        UpdateWalkAnimation(DeltaSeconds, false);
        return;
    }

    const FVector Target = bHeadingToB ? RoutinePointB : RoutinePointA;
    const FVector ToTarget = Target - GetActorLocation();
    if (ToTarget.Size2D() < 25.0f)
    {
        bHeadingToB = !bHeadingToB;
        WaitRemaining = Random.FRandRange(MinWait, MaxWait);
        UpdateWalkAnimation(DeltaSeconds, false);
        return;
    }

    const FVector Direction = ToTarget.GetSafeNormal2D();
    AddActorWorldOffset(Direction * WalkSpeed * DeltaSeconds, true);
    SetActorRotation(FMath::RInterpTo(GetActorRotation(), Direction.Rotation(), DeltaSeconds, 5.0f));
    UpdateWalkAnimation(DeltaSeconds, true);
}
