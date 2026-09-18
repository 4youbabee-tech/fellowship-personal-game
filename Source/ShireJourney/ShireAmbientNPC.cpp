#include "ShireAmbientNPC.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
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
    const bool bHobbitResident = !bBreeTownsperson && !bElf;

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

    if (bProductionHobbit)
    {
        Torso->SetRelativeScale3D(FVector(1));
        Head->SetRelativeScale3D(FVector(1));
        Hair->SetRelativeScale3D(FVector(1));
        LeftArm->SetRelativeScale3D(FVector(1));
        RightArm->SetRelativeScale3D(FVector(1));
        LeftLeg->SetRelativeScale3D(FVector(1));
        RightLeg->SetRelativeScale3D(FVector(1));
        Torso->SetRelativeLocation(FVector(0.0f, 0.0f, 58.0f));
        Head->SetRelativeLocation(FVector(0.0f, 0.0f, 101.0f));
        Hair->SetRelativeLocation(FVector(-2.0f, 0.0f, 111.0f));
    }
    else if (bElf)
    {
        Torso->SetRelativeLocation(FVector(0.0f, 0.0f, 78.0f));
        Torso->SetRelativeScale3D(FVector(0.27f, 0.19f, 0.52f));
        Head->SetRelativeLocation(FVector(0.0f, 0.0f, 139.0f));
        Head->SetRelativeScale3D(FVector(0.205f));
        Hair->SetRelativeLocation(FVector(-1.0f, 0.0f, 149.0f));
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
        Torso->SetRelativeLocation(FVector(0.0f, 0.0f, 72.0f));
        Torso->SetRelativeScale3D(FVector(0.31f, 0.23f, 0.48f));
        Head->SetRelativeLocation(FVector(0.0f, 0.0f, 128.0f));
        Head->SetRelativeScale3D(FVector(0.22f));
        Hair->SetRelativeLocation(FVector(-1.0f, 0.0f, 138.0f));
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

    if (bElf)
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


void AShireAmbientNPC::UpdateSocialLife(float DeltaSeconds)
{
    if (RoutineRole == TEXT("Courier") || RoutineRole == TEXT("RoadWalker"))
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

        if (Candidate->RoutineRole == TEXT("Courier") || Candidate->RoutineRole == TEXT("RoadWalker"))
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
        SocialRemaining = Random.FRandRange(1.6f, 3.4f);
    }
}

void AShireAmbientNPC::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0))
    {
        const float Distance = FVector::Dist2D(PlayerPawn->GetActorLocation(), GetActorLocation());
        PrimaryActorTick.TickInterval = Distance > DormantTickDistance ? 0.75f :
            (Distance > ReducedTickDistance ? 0.22f : 0.0f);
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
