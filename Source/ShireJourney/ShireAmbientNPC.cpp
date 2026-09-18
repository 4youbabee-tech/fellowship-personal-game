#include "ShireAmbientNPC.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "GameFramework/Pawn.h"
#include "Kismet/GameplayStatics.h"
#include "EngineUtils.h"
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

    ActivityProp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ActivityProp"));
    ActivityProp->SetupAttachment(Root);
    ActivityProp->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    ActivityProp->SetVisibility(false);

    SocialCaption = CreateDefaultSubobject<UTextRenderComponent>(TEXT("SocialCaption"));
    SocialCaption->SetupAttachment(Root);
    SocialCaption->SetRelativeLocation(FVector(0.0f, 0.0f, 145.0f));
    SocialCaption->SetHorizontalAlignment(EHorizTextAligment::EHTA_Center);
    SocialCaption->SetWorldSize(18.0f);
    SocialCaption->SetTextRenderColor(FColor(235, 228, 205));
    SocialCaption->SetVisibility(false);

    static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(TEXT("/Engine/BasicShapes/Sphere.Sphere"));

    if (CubeMesh.Succeeded())
    {
        Torso->SetStaticMesh(CubeMesh.Object);
        ActivityProp->SetStaticMesh(CubeMesh.Object);
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

    auto TryMesh = [](UStaticMeshComponent* Component, const TCHAR* AssetPath) -> bool
    {
        if (!Component) return false;
        if (UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr, AssetPath))
        {
            Component->SetStaticMesh(Mesh);
            return true;
        }
        return false;
    };

    const bool bBreeTownsperson = RoutineRole == TEXT("BreeTownsperson");
    const bool bElf = RoutineRole == TEXT("Elf");
    const bool bBird = RoutineRole == TEXT("Bird");
    const bool bHobbitResident = !bBreeTownsperson && !bElf && !bBird;

    Torso->SetVisibility(true);
    Head->SetVisibility(true);
    Hair->SetVisibility(true);
    LeftArm->SetVisibility(true);
    RightArm->SetVisibility(true);
    LeftLeg->SetVisibility(true);
    RightLeg->SetVisibility(true);

    if (!bHobbitResident)
    {
        TryMesh(Torso, TEXT("/Engine/BasicShapes/Cube.Cube"));
        TryMesh(Head, TEXT("/Engine/BasicShapes/Sphere.Sphere"));
        TryMesh(Hair, TEXT("/Engine/BasicShapes/Sphere.Sphere"));
        TryMesh(LeftArm, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
        TryMesh(RightArm, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
        TryMesh(LeftLeg, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
        TryMesh(RightLeg, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    }

    bool bProductionHobbit = false;
    if (bHobbitResident)
    {
        bProductionHobbit = true;
        bProductionHobbit = TryMesh(Torso, TEXT("/Game/Production/Characters/Hobbit/SM_Hobbit_Torso.SM_Hobbit_Torso")) && bProductionHobbit;
        bProductionHobbit = TryMesh(Head, TEXT("/Game/Production/Characters/Hobbit/SM_Hobbit_Head.SM_Hobbit_Head")) && bProductionHobbit;
        bProductionHobbit = TryMesh(Hair, TEXT("/Game/Production/Characters/Hobbit/SM_Hobbit_Hair.SM_Hobbit_Hair")) && bProductionHobbit;
        bProductionHobbit = TryMesh(LeftArm, TEXT("/Game/Production/Characters/Hobbit/SM_Hobbit_Arm.SM_Hobbit_Arm")) && bProductionHobbit;
        TryMesh(RightArm, TEXT("/Game/Production/Characters/Hobbit/SM_Hobbit_Arm.SM_Hobbit_Arm"));
        bProductionHobbit = TryMesh(LeftLeg, TEXT("/Game/Production/Characters/Hobbit/SM_Hobbit_Leg.SM_Hobbit_Leg")) && bProductionHobbit;
        TryMesh(RightLeg, TEXT("/Game/Production/Characters/Hobbit/SM_Hobbit_Leg.SM_Hobbit_Leg"));
    }

    if (bBird)
    {
        VisualTorsoBaseZ = 10.0f;
        VisualHeadBaseZ = 15.0f;
        VisualHairBaseZ = 15.0f;
        Torso->SetRelativeLocation(FVector(0.0f, 0.0f, VisualTorsoBaseZ));
        Torso->SetRelativeScale3D(FVector(0.16f, 0.08f, 0.07f));
        Head->SetRelativeLocation(FVector(13.0f, 0.0f, VisualHeadBaseZ));
        Head->SetRelativeScale3D(FVector(0.07f));
        Hair->SetVisibility(false);
        LeftArm->SetRelativeLocation(FVector(0.0f, -13.0f, 12.0f));
        RightArm->SetRelativeLocation(FVector(0.0f, 13.0f, 12.0f));
        LeftArm->SetRelativeScale3D(FVector(0.025f, 0.025f, 0.22f));
        RightArm->SetRelativeScale3D(FVector(0.025f, 0.025f, 0.22f));
        LeftArm->SetRelativeRotation(FRotator(0.0f, 0.0f, 65.0f));
        RightArm->SetRelativeRotation(FRotator(0.0f, 0.0f, -65.0f));
        LeftLeg->SetVisibility(false);
        RightLeg->SetVisibility(false);
    }
    else if (bProductionHobbit)
    {
        Torso->SetRelativeScale3D(FVector(1));
        Head->SetRelativeScale3D(FVector(1));
        Hair->SetRelativeScale3D(FVector(1));
        LeftArm->SetRelativeScale3D(FVector(1));
        RightArm->SetRelativeScale3D(FVector(1));
        LeftLeg->SetRelativeScale3D(FVector(1));
        RightLeg->SetRelativeScale3D(FVector(1));
        VisualTorsoBaseZ = 58.0f;
        VisualHeadBaseZ = 101.0f;
        VisualHairBaseZ = 111.0f;
        Torso->SetRelativeLocation(FVector(0.0f, 0.0f, VisualTorsoBaseZ));
        Head->SetRelativeLocation(FVector(0.0f, 0.0f, VisualHeadBaseZ));
        Hair->SetRelativeLocation(FVector(-2.0f, 0.0f, VisualHairBaseZ));
    }
    else if (bElf)
    {
        VisualTorsoBaseZ = 78.0f;
        VisualHeadBaseZ = 139.0f;
        VisualHairBaseZ = 149.0f;
        Torso->SetRelativeLocation(FVector(0.0f, 0.0f, VisualTorsoBaseZ));
        Torso->SetRelativeScale3D(FVector(0.27f, 0.19f, 0.52f));
        Head->SetRelativeLocation(FVector(0.0f, 0.0f, VisualHeadBaseZ));
        Head->SetRelativeScale3D(FVector(0.205f));
        Hair->SetRelativeLocation(FVector(-1.0f, 0.0f, VisualHairBaseZ));
        Hair->SetRelativeScale3D(FVector(0.21f, 0.20f, 0.13f));
        LeftArm->SetRelativeLocation(FVector(0.0f, -22.0f, 78.0f));
        RightArm->SetRelativeLocation(FVector(0.0f, 22.0f, 78.0f));
        LeftArm->SetRelativeScale3D(FVector(0.065f, 0.065f, 0.43f));
        RightArm->SetRelativeScale3D(FVector(0.065f, 0.065f, 0.43f));
        LeftLeg->SetRelativeLocation(FVector(0.0f, -8.5f, 27.0f));
        RightLeg->SetRelativeLocation(FVector(0.0f, 8.5f, 27.0f));
        LeftLeg->SetRelativeScale3D(FVector(0.075f, 0.075f, 0.40f));
        RightLeg->SetRelativeScale3D(FVector(0.075f, 0.075f, 0.40f));
    }
    else if (bBreeTownsperson)
    {
        VisualTorsoBaseZ = 72.0f;
        VisualHeadBaseZ = 128.0f;
        VisualHairBaseZ = 138.0f;
        Torso->SetRelativeLocation(FVector(0.0f, 0.0f, VisualTorsoBaseZ));
        Torso->SetRelativeScale3D(FVector(0.31f, 0.23f, 0.48f));
        Head->SetRelativeLocation(FVector(0.0f, 0.0f, VisualHeadBaseZ));
        Head->SetRelativeScale3D(FVector(0.22f));
        Hair->SetRelativeLocation(FVector(-1.0f, 0.0f, VisualHairBaseZ));
        Hair->SetRelativeScale3D(FVector(0.225f, 0.225f, 0.11f));
        LeftArm->SetRelativeLocation(FVector(0.0f, -25.0f, 72.0f));
        RightArm->SetRelativeLocation(FVector(0.0f, 25.0f, 72.0f));
        LeftArm->SetRelativeScale3D(FVector(0.075f, 0.075f, 0.40f));
        RightArm->SetRelativeScale3D(FVector(0.075f, 0.075f, 0.40f));
        LeftLeg->SetRelativeLocation(FVector(0.0f, -9.0f, 25.0f));
        RightLeg->SetRelativeLocation(FVector(0.0f, 9.0f, 25.0f));
        LeftLeg->SetRelativeScale3D(FVector(0.085f, 0.085f, 0.36f));
        RightLeg->SetRelativeScale3D(FVector(0.085f, 0.085f, 0.36f));
    }

    FLinearColor Coat;
    FLinearColor Trousers;
    FLinearColor HairColor;
    FLinearColor Skin;

    if (bBird)
    {
        Coat = FLinearColor(0.16f, 0.17f, 0.16f);
        Trousers = FLinearColor(0.10f, 0.10f, 0.10f);
        HairColor = FLinearColor(0.08f, 0.08f, 0.08f);
        Skin = FLinearColor(0.34f, 0.30f, 0.22f);
    }
    else if (bElf)
    {
        Coat = FLinearColor(
            Random.FRandRange(0.20f, 0.34f),
            Random.FRandRange(0.30f, 0.46f),
            Random.FRandRange(0.20f, 0.32f));
        Trousers = FLinearColor(0.18f, 0.24f, 0.18f);
        HairColor = Random.FRand() > 0.45f
            ? FLinearColor(0.72f, 0.62f, 0.38f)
            : FLinearColor(0.12f, 0.075f, 0.045f);
        Skin = FLinearColor(0.78f, 0.61f, 0.47f);
    }
    else if (bBreeTownsperson)
    {
        Coat = FLinearColor(
            Random.FRandRange(0.18f, 0.34f),
            Random.FRandRange(0.15f, 0.28f),
            Random.FRandRange(0.10f, 0.20f));
        Trousers = FLinearColor(0.18f, 0.15f, 0.12f);
        HairColor = FLinearColor(
            Random.FRandRange(0.08f, 0.28f),
            Random.FRandRange(0.04f, 0.16f),
            Random.FRandRange(0.02f, 0.08f));
        Skin = FLinearColor(0.70f, 0.50f, 0.36f);
    }
    else
    {
        Coat = FLinearColor(
            Random.FRandRange(0.18f, 0.42f),
            Random.FRandRange(0.22f, 0.46f),
            Random.FRandRange(0.10f, 0.24f));
        Trousers = FLinearColor(
            Random.FRandRange(0.18f, 0.34f),
            Random.FRandRange(0.12f, 0.25f),
            Random.FRandRange(0.06f, 0.14f));
        HairColor = FLinearColor(
            Random.FRandRange(0.08f, 0.34f),
            Random.FRandRange(0.04f, 0.20f),
            Random.FRandRange(0.02f, 0.10f));
        Skin = FLinearColor(
            Random.FRandRange(0.64f, 0.80f),
            Random.FRandRange(0.43f, 0.58f),
            Random.FRandRange(0.28f, 0.38f));
    }

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

    ActivityProp->SetVisibility(false);
    if (!bBird && ActivityPropType != NAME_None)
    {
        FLinearColor PropColor(0.28f, 0.17f, 0.08f);
        FVector PropScale(0.18f, 0.18f, 0.18f);
        ActivityPropBase = FVector(5.0f, bElf || bBreeTownsperson ? 28.0f : 22.0f, VisualTorsoBaseZ - 3.0f);
        ActivityPropBaseRotation = FRotator::ZeroRotator;

        if (ActivityPropType == TEXT("Mug"))
        {
            TryMesh(ActivityProp, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
            PropScale = FVector(0.07f, 0.07f, 0.11f);
            PropColor = FLinearColor(0.38f, 0.24f, 0.10f);
            ActivityPropBase = FVector(12.0f, bElf || bBreeTownsperson ? 28.0f : 21.0f, VisualTorsoBaseZ + 5.0f);
        }
        else if (ActivityPropType == TEXT("Satchel"))
        {
            TryMesh(ActivityProp, TEXT("/Engine/BasicShapes/Cube.Cube"));
            PropScale = FVector(0.13f, 0.20f, 0.18f);
            PropColor = FLinearColor(0.17f, 0.09f, 0.045f);
            ActivityPropBase = FVector(-5.0f, bElf || bBreeTownsperson ? 27.0f : 21.0f, VisualTorsoBaseZ - 8.0f);
            ActivityPropBaseRotation = FRotator(0.0f, 10.0f, 8.0f);
        }
        else if (ActivityPropType == TEXT("Basket"))
        {
            TryMesh(ActivityProp, TEXT("/Engine/BasicShapes/Cube.Cube"));
            PropScale = FVector(0.20f, 0.16f, 0.13f);
            PropColor = FLinearColor(0.34f, 0.20f, 0.08f);
            ActivityPropBase = FVector(12.0f, bElf || bBreeTownsperson ? 27.0f : 22.0f, VisualTorsoBaseZ - 7.0f);
        }
        else if (ActivityPropType == TEXT("Crate"))
        {
            TryMesh(ActivityProp, TEXT("/Engine/BasicShapes/Cube.Cube"));
            PropScale = FVector(0.24f, 0.20f, 0.18f);
            PropColor = FLinearColor(0.28f, 0.16f, 0.07f);
            ActivityPropBase = FVector(16.0f, 0.0f, VisualTorsoBaseZ - 10.0f);
        }
        else if (ActivityPropType == TEXT("Book"))
        {
            TryMesh(ActivityProp, TEXT("/Engine/BasicShapes/Cube.Cube"));
            PropScale = FVector(0.19f, 0.14f, 0.035f);
            PropColor = FLinearColor(0.20f, 0.10f, 0.05f);
            ActivityPropBase = FVector(16.0f, bElf || bBreeTownsperson ? 24.0f : 19.0f, VisualTorsoBaseZ + 3.0f);
            ActivityPropBaseRotation = FRotator(0.0f, 0.0f, -18.0f);
        }
        else if (ActivityPropType == TEXT("Lantern"))
        {
            TryMesh(ActivityProp, TEXT("/Engine/BasicShapes/Sphere.Sphere"));
            PropScale = FVector(0.10f);
            PropColor = FLinearColor(0.72f, 0.50f, 0.15f);
            ActivityPropBase = FVector(6.0f, bElf || bBreeTownsperson ? 29.0f : 23.0f, VisualTorsoBaseZ - 10.0f);
        }

        ActivityProp->SetRelativeLocation(ActivityPropBase);
        ActivityProp->SetRelativeRotation(ActivityPropBaseRotation);
        ActivityProp->SetRelativeScale3D(PropScale);
        ActivityProp->SetVisibility(true);
        ApplyColor(ActivityProp, PropColor);
    }

    AppliedVisualRole = RoutineRole;
}

void AShireAmbientNPC::UpdateWalkAnimation(float DeltaSeconds, bool bMoving)
{
    float Swing = 0.0f;
    float Bob = 0.0f;
    ActivityPhase += DeltaSeconds * (bSocializing ? 4.2f : 2.8f);
    if (bMoving)
    {
        WalkPhase += DeltaSeconds * 6.5f;
        Swing = FMath::Sin(WalkPhase) * 22.0f;
        Bob = FMath::Abs(FMath::Sin(WalkPhase * 2.0f)) * 1.0f;
    }

    float LeftArmTarget = Swing;
    float RightArmTarget = -Swing;
    if (!bMoving && bSocializing)
    {
        LeftArmTarget = -12.0f + FMath::Sin(ActivityPhase) * 9.0f;
        RightArmTarget = -24.0f + FMath::Sin(ActivityPhase + 1.1f) * 12.0f;
    }
    else if (!bMoving && ActivityProp && ActivityProp->IsVisible())
    {
        const float WorkGesture = FMath::Sin(ActivityPhase) * 7.0f;
        LeftArmTarget = -20.0f + WorkGesture;
        RightArmTarget = -28.0f - WorkGesture;
    }

    LeftArm->SetRelativeRotation(FMath::RInterpTo(
        LeftArm->GetRelativeRotation(), FRotator(LeftArmTarget, 0.0f, 0.0f), DeltaSeconds, 9.0f));
    RightArm->SetRelativeRotation(FMath::RInterpTo(
        RightArm->GetRelativeRotation(), FRotator(RightArmTarget, 0.0f, 0.0f), DeltaSeconds, 9.0f));
    LeftLeg->SetRelativeRotation(FMath::RInterpTo(
        LeftLeg->GetRelativeRotation(), FRotator(-Swing * 0.65f, 0.0f, 0.0f), DeltaSeconds, 9.0f));
    RightLeg->SetRelativeRotation(FMath::RInterpTo(
        RightLeg->GetRelativeRotation(), FRotator(Swing * 0.65f, 0.0f, 0.0f), DeltaSeconds, 9.0f));

    Torso->SetRelativeLocation(FMath::VInterpTo(
        Torso->GetRelativeLocation(), FVector(0.0f, 0.0f, VisualTorsoBaseZ + Bob), DeltaSeconds, 10.0f));
    Head->SetRelativeLocation(FMath::VInterpTo(
        Head->GetRelativeLocation(), FVector(0.0f, 0.0f, VisualHeadBaseZ + Bob), DeltaSeconds, 10.0f));
    Hair->SetRelativeLocation(FMath::VInterpTo(
        Hair->GetRelativeLocation(), FVector(-1.0f, 0.0f, VisualHairBaseZ + Bob), DeltaSeconds, 10.0f));

    if (ActivityProp && ActivityProp->IsVisible())
    {
        const float CarryBob = Bob * 0.55f;
        const float Gesture = !bMoving ? FMath::Sin(ActivityPhase) * 2.5f : 0.0f;
        ActivityProp->SetRelativeLocation(FMath::VInterpTo(
            ActivityProp->GetRelativeLocation(),
            ActivityPropBase + FVector(0.0f, 0.0f, CarryBob + Gesture),
            DeltaSeconds,
            9.0f));
        ActivityProp->SetRelativeRotation(FMath::RInterpTo(
            ActivityProp->GetRelativeRotation(),
            ActivityPropBaseRotation + FRotator(0.0f, 0.0f, bMoving ? Swing * 0.05f : Gesture),
            DeltaSeconds,
            7.0f));
    }
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

    WaitRemaining = Random.FRandRange(0.0f, 1.5f);
    SenseAccumulator = Random.FRandRange(0.0f, 0.35f);
    SocialCheckRemaining = Random.FRandRange(1.0f, 3.0f);
}

void AShireAmbientNPC::UpdateAwareness(float DeltaSeconds)
{
    if (!bCanNoticePlayer)
    {
        bObservingPlayer = false;
        ObservedPlayer.Reset();
        return;
    }

    NoticeCooldownRemaining = FMath::Max(0.0f, NoticeCooldownRemaining - DeltaSeconds);

    if (bObservingPlayer)
    {
        ObserveRemaining -= DeltaSeconds;

        APawn* PlayerPawn = ObservedPlayer.Get();
        if (PlayerPawn)
        {
            FVector ToPlayer = PlayerPawn->GetActorLocation() - GetActorLocation();
            ToPlayer.Z = 0.0f;
            if (ToPlayer.SizeSquared2D() > FMath::Square(PlayerNoticeRadius * 1.65f))
            {
                ObserveRemaining = 0.0f;
            }
            else if (!ToPlayer.IsNearlyZero())
            {
                SetActorRotation(FMath::RInterpTo(
                    GetActorRotation(), ToPlayer.Rotation(), DeltaSeconds, 4.5f));
            }
        }

        if (ObserveRemaining <= 0.0f)
        {
            bObservingPlayer = false;
            ObservedPlayer.Reset();
            NoticeCooldownRemaining = NoticeCooldown;
            WaitRemaining = FMath::Max(WaitRemaining, Random.FRandRange(0.4f, 1.2f));
        }
        return;
    }

    SenseAccumulator -= DeltaSeconds;
    if (SenseAccumulator > 0.0f || NoticeCooldownRemaining > 0.0f)
    {
        return;
    }

    SenseAccumulator = 0.45f + Random.FRandRange(0.0f, 0.20f);

    APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
    if (!PlayerPawn)
    {
        return;
    }

    float EffectiveRadius = PlayerNoticeRadius;
    if (PlayerPawn->GetVelocity().Size2D() > 220.0f)
    {
        EffectiveRadius *= RunningNoticeMultiplier;
    }

    const float DistanceSq = FVector::DistSquared2D(PlayerPawn->GetActorLocation(), GetActorLocation());
    if (DistanceSq <= FMath::Square(EffectiveRadius))
    {
        bObservingPlayer = true;
        ObservedPlayer = PlayerPawn;
        ObserveRemaining = Random.FRandRange(MinObserveDuration, MaxObserveDuration);
    }
}


FText AShireAmbientNPC::ResolveAmbientConversationLine(bool bResponse) const
{
    if (RoutineRole == TEXT("PartyGuest"))
    {
        return FText::FromString(bResponse
            ? TEXT("Nearly ready for the dancing.")
            : TEXT("Have you seen the lanterns?"));
    }
    if (RoutineRole == TEXT("FieldWorker"))
    {
        return FText::FromString(bResponse
            ? TEXT("Best finish before the weather turns.")
            : TEXT("The field will not tend itself."));
    }
    if (RoutineRole == TEXT("FerryWorker"))
    {
        return FText::FromString(bResponse
            ? TEXT("Then keep the rope tight.")
            : TEXT("The water is running fast today."));
    }
    if (RoutineRole == TEXT("BreeTownsperson"))
    {
        return FText::FromString(bResponse
            ? TEXT("Aye. Keep your purse close after dark.")
            : TEXT("The road is busy tonight."));
    }
    if (RoutineRole == TEXT("Elf"))
    {
        return FText::FromString(bResponse
            ? TEXT("The valley has heard it too.")
            : TEXT("The wind changed beyond the trees."));
    }
    if (RoutineRole == TEXT("Villager"))
    {
        return FText::FromString(bResponse
            ? TEXT("Aye. Plenty still to do.")
            : TEXT("Fine weather for the lane."));
    }

    return FText::FromString(bResponse ? TEXT("And to you.") : TEXT("Good day."));
}

void AShireAmbientNPC::BeginSocialCaption(const FText& Text, float Delay, float Duration)
{
    PendingSocialCaption = Text;
    SocialCaptionDelay = FMath::Max(0.0f, Delay);
    SocialCaptionRemaining = FMath::Max(0.0f, Duration);
    if (SocialCaption)
    {
        SocialCaption->SetVisibility(false);
    }
}

void AShireAmbientNPC::UpdateSocialCaption(float DeltaSeconds)
{
    if (!SocialCaption)
    {
        return;
    }

    if (SocialCaptionDelay > 0.0f)
    {
        SocialCaptionDelay -= DeltaSeconds;
        if (SocialCaptionDelay > 0.0f)
        {
            SocialCaption->SetVisibility(false);
            return;
        }

        SocialCaption->SetText(PendingSocialCaption);
    }

    if (SocialCaptionRemaining <= 0.0f || PendingSocialCaption.IsEmpty())
    {
        SocialCaption->SetVisibility(false);
        return;
    }

    APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
    if (!PlayerPawn)
    {
        SocialCaption->SetVisibility(false);
        return;
    }

    const float DistanceSq = FVector::DistSquared(
        PlayerPawn->GetActorLocation(), GetActorLocation());
    if (DistanceSq > FMath::Square(1200.0f))
    {
        SocialCaption->SetVisibility(false);
        return;
    }

    SocialCaptionRemaining -= DeltaSeconds;
    if (SocialCaptionRemaining <= 0.0f)
    {
        SocialCaption->SetVisibility(false);
        PendingSocialCaption = FText::GetEmpty();
        return;
    }

    SocialCaption->SetRelativeLocation(FVector(0.0f, 0.0f, VisualHeadBaseZ + 38.0f));
    const FVector ToPlayer = PlayerPawn->GetActorLocation() - SocialCaption->GetComponentLocation();
    if (!ToPlayer.IsNearlyZero())
    {
        SocialCaption->SetWorldRotation(FRotator(0.0f, ToPlayer.Rotation().Yaw + 180.0f, 0.0f));
    }
    SocialCaption->SetVisibility(true);
}

void AShireAmbientNPC::UpdateSocialLife(float DeltaSeconds)
{
    if (RoutineRole == TEXT("Courier") || RoutineRole == TEXT("RoadWalker") ||
        RoutineRole == TEXT("Bird"))
    {
        bSocializing = false;
        SocialPartner.Reset();
        return;
    }

    if (bSocializing)
    {
        SocialRemaining -= DeltaSeconds;
        AShireAmbientNPC* Partner = SocialPartner.Get();

        if (!Partner ||
            FVector::DistSquared2D(GetActorLocation(), Partner->GetActorLocation()) > FMath::Square(280.0f))
        {
            SocialRemaining = 0.0f;
        }
        else
        {
            FVector ToPartner = Partner->GetActorLocation() - GetActorLocation();
            ToPartner.Z = 0.0f;
            if (!ToPartner.IsNearlyZero())
            {
                SetActorRotation(FMath::RInterpTo(
                    GetActorRotation(), ToPartner.Rotation(), DeltaSeconds, 3.5f));
            }
        }

        if (SocialRemaining <= 0.0f)
        {
            bSocializing = false;
            SocialPartner.Reset();
            SocialCheckRemaining = Random.FRandRange(6.0f, 11.0f);
            WaitRemaining = FMath::Max(WaitRemaining, Random.FRandRange(0.3f, 0.9f));
        }
        return;
    }

    SocialCheckRemaining -= DeltaSeconds;
    if (SocialCheckRemaining > 0.0f)
    {
        return;
    }

    SocialCheckRemaining = Random.FRandRange(4.0f, 8.0f);

    APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
    if (!PlayerPawn ||
        FVector::DistSquared2D(PlayerPawn->GetActorLocation(), GetActorLocation()) > FMath::Square(1800.0f))
    {
        return;
    }

    AShireAmbientNPC* BestPartner = nullptr;
    float BestDistanceSq = FMath::Square(240.0f);

    for (TActorIterator<AShireAmbientNPC> It(GetWorld()); It; ++It)
    {
        AShireAmbientNPC* Candidate = *It;
        if (!Candidate || Candidate == this || Candidate->bSocializing || Candidate->bObservingPlayer)
        {
            continue;
        }

        if (Candidate->RoutineRole == TEXT("Courier") ||
            Candidate->RoutineRole == TEXT("RoadWalker") ||
            Candidate->RoutineRole == TEXT("Bird"))
        {
            continue;
        }

        const float DistanceSq =
            FVector::DistSquared2D(GetActorLocation(), Candidate->GetActorLocation());
        if (DistanceSq < BestDistanceSq)
        {
            BestDistanceSq = DistanceSq;
            BestPartner = Candidate;
        }
    }

    if (BestPartner)
    {
        bSocializing = true;
        SocialPartner = BestPartner;
        SocialRemaining = Random.FRandRange(3.0f, 4.2f);

        BestPartner->bSocializing = true;
        BestPartner->SocialPartner = this;
        BestPartner->SocialRemaining = SocialRemaining;
        BestPartner->SocialCheckRemaining = Random.FRandRange(7.0f, 12.0f);

        BeginSocialCaption(ResolveAmbientConversationLine(false), 0.0f, 1.25f);
        BestPartner->BeginSocialCaption(
            BestPartner->ResolveAmbientConversationLine(true),
            1.15f,
            1.35f);
    }
}

void AShireAmbientNPC::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    UpdateSocialCaption(DeltaSeconds);

    if (AppliedVisualRole != RoutineRole)
    {
        ApplyVisualStyle();
    }

    if (APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0))
    {
        const float Distance = FVector::Dist2D(PlayerPawn->GetActorLocation(), GetActorLocation());
        PrimaryActorTick.TickInterval = Distance > DormantTickDistance ? 0.75f :
            (Distance > ReducedTickDistance ? 0.22f : 0.0f);
    }

    if (RoutineRole == TEXT("Bird"))
    {
        const FVector Target = bHeadingToB ? RoutinePointB : RoutinePointA;
        const FVector ToTarget = Target - GetActorLocation();
        if (ToTarget.Size() < 45.0f)
        {
            bHeadingToB = !bHeadingToB;
        }

        const FVector Direction = ToTarget.GetSafeNormal();
        AddActorWorldOffset(Direction * WalkSpeed * DeltaSeconds, false);
        if (!Direction.IsNearlyZero())
        {
            SetActorRotation(FMath::RInterpTo(GetActorRotation(), Direction.Rotation(), DeltaSeconds, 4.0f));
        }

        PrototypeWalkPhase += DeltaSeconds * 9.0f;
        const float Wing = FMath::Sin(PrototypeWalkPhase) * 42.0f;
        LeftArm->SetRelativeRotation(FMath::RInterpTo(
            LeftArm->GetRelativeRotation(), FRotator(0.0f, 0.0f, 58.0f + Wing), DeltaSeconds, 10.0f));
        RightArm->SetRelativeRotation(FMath::RInterpTo(
            RightArm->GetRelativeRotation(), FRotator(0.0f, 0.0f, -58.0f - Wing), DeltaSeconds, 10.0f));
        Torso->SetRelativeLocation(FVector(0.0f, 0.0f, VisualTorsoBaseZ + FMath::Sin(PrototypeWalkPhase * 0.5f) * 1.5f));
        return;
    }

    UpdateAwareness(DeltaSeconds);

    if (bObservingPlayer)
    {
        UpdateWalkAnimation(DeltaSeconds, false);
        return;
    }

    UpdateSocialLife(DeltaSeconds);
    if (bSocializing)
    {
        UpdateWalkAnimation(DeltaSeconds, false);
        return;
    }

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
