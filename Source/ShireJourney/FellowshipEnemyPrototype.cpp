#include "FellowshipEnemyPrototype.h"

#include "ShirePlayerCharacter.h"
#include "ShireQuestSubsystem.h"

#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"
#include "UObject/SoftObjectPath.h"

AFellowshipEnemyPrototype::AFellowshipEnemyPrototype()
{
    PrimaryActorTick.bCanEverTick = true;
    PrimaryActorTick.TickInterval = 0.05f;

    GetCapsuleComponent()->SetCapsuleRadius(32.0f);
    GetCapsuleComponent()->SetCapsuleHalfHeight(72.0f);
    GetCharacterMovement()->DisableMovement();

    Torso = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Torso"));
    Torso->SetupAttachment(GetCapsuleComponent());
    Torso->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    Head = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Head"));
    Head->SetupAttachment(GetCapsuleComponent());
    Head->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    LeftArm = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("LeftArm"));
    LeftArm->SetupAttachment(GetCapsuleComponent());
    LeftArm->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    RightArm = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RightArm"));
    RightArm->SetupAttachment(GetCapsuleComponent());
    RightArm->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    LeftLeg = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("LeftLeg"));
    LeftLeg->SetupAttachment(GetCapsuleComponent());
    LeftLeg->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    RightLeg = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RightLeg"));
    RightLeg->SetupAttachment(GetCapsuleComponent());
    RightLeg->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    Weapon = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Weapon"));
    Weapon->SetupAttachment(GetCapsuleComponent());
    Weapon->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(TEXT("/Engine/BasicShapes/Sphere.Sphere"));

    if (CubeMesh.Succeeded())
    {
        Torso->SetStaticMesh(CubeMesh.Object);
        Weapon->SetStaticMesh(CubeMesh.Object);
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
    }
}

void AFellowshipEnemyPrototype::BeginPlay()
{
    Super::BeginPlay();
    HomeLocation = GetActorLocation();
    ApplyTypeProfile();
}

void AFellowshipEnemyPrototype::ConfigureEnemy(EFellowshipEnemyType InType, FName InRequiredQuestId, int32 InRequiredMinStage)
{
    EnemyType = InType;
    RequiredQuestId = InRequiredQuestId;
    RequiredMinStage = FMath::Max(0, InRequiredMinStage);
    bProfileApplied = false;
}

void AFellowshipEnemyPrototype::ApplyTypeProfile()
{
    UMaterialInterface* BasicMaterial = LoadObject<UMaterialInterface>(
        nullptr, TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
    if (!BasicMaterial)
    {
        return;
    }

    FLinearColor Skin(0.24f, 0.30f, 0.18f);
    FLinearColor Armor(0.12f, 0.11f, 0.09f);
    FLinearColor WeaponColor(0.34f, 0.34f, 0.32f);

    float HeightScale = 1.0f;
    float WidthScale = 1.0f;

    auto TryMesh = [](UStaticMeshComponent* Component, const FString& AssetPath) -> bool
    {
        if (!Component) return false;
        if (UStaticMesh* Mesh = Cast<UStaticMesh>(FSoftObjectPath(AssetPath).ResolveObject()))
        {
            Component->SetStaticMesh(Mesh);
            return true;
        }
        return false;
    };

    if (EnemyType == EFellowshipEnemyType::Orc)
    {
        MaxHealth = 55.0f;
        DetectionRadius = 900.0f;
        AttackRange = 135.0f;
        AttackDamage = 8.0f;
        AttackInterval = 1.25f;
        MoveSpeed = 185.0f;
    }
    else if (EnemyType == EFellowshipEnemyType::UrukHai)
    {
        MaxHealth = 85.0f;
        DetectionRadius = 1050.0f;
        AttackRange = 150.0f;
        AttackDamage = 12.0f;
        AttackInterval = 1.05f;
        MoveSpeed = 225.0f;
        HeightScale = 1.10f;
        WidthScale = 1.08f;
        Skin = FLinearColor(0.22f, 0.16f, 0.11f);
    }
    else if (EnemyType == EFellowshipEnemyType::Lurtz)
    {
        // Film-locked hero antagonist: this actor may pressure the encounter, but
        // player damage cannot resolve Lurtz's canonical outcome.
        MaxHealth = 320.0f;
        DetectionRadius = 1250.0f;
        AttackRange = 165.0f;
        AttackDamage = 18.0f;
        AttackInterval = 0.95f;
        MoveSpeed = 235.0f;
        HeightScale = 1.18f;
        WidthScale = 1.14f;
        Skin = FLinearColor(0.20f, 0.13f, 0.085f);
        Armor = FLinearColor(0.075f, 0.065f, 0.055f);
        WeaponColor = FLinearColor(0.26f, 0.25f, 0.23f);
        Tags.AddUnique(TEXT("FilmLockedOutcome"));
    }
    else if (EnemyType == EFellowshipEnemyType::CaveTroll)
    {
        MaxHealth = 240.0f;
        DetectionRadius = 1200.0f;
        AttackRange = 205.0f;
        AttackDamage = 22.0f;
        AttackInterval = 1.70f;
        MoveSpeed = 125.0f;
        HeightScale = 1.75f;
        WidthScale = 1.65f;
        Skin = FLinearColor(0.28f, 0.31f, 0.24f);
        Armor = FLinearColor(0.16f, 0.15f, 0.12f);
        WeaponColor = FLinearColor(0.24f, 0.17f, 0.09f);
    }

    FString ProductionFolder;
    if (EnemyType == EFellowshipEnemyType::Orc) ProductionFolder = TEXT("Orc");
    else if (EnemyType == EFellowshipEnemyType::UrukHai) ProductionFolder = TEXT("UrukHai");
    else if (EnemyType == EFellowshipEnemyType::Lurtz) ProductionFolder = TEXT("Lurtz");
    else if (EnemyType == EFellowshipEnemyType::CaveTroll) ProductionFolder = TEXT("CaveTroll");

    bool bProductionVisual = false;
    if (!ProductionFolder.IsEmpty())
    {
        const FString Prefix = FString::Printf(
            TEXT("/Game/Production/Enemies/%s/SM_%s_"),
            *ProductionFolder,
            *ProductionFolder);
        const FString WeaponSuffix =
            EnemyType == EFellowshipEnemyType::Lurtz ? TEXT("Blade") : TEXT("Weapon");
        bProductionVisual =
            TryMesh(Torso, Prefix + TEXT("Torso.SM_") + ProductionFolder + TEXT("_Torso")) &&
            TryMesh(Head, Prefix + TEXT("Head.SM_") + ProductionFolder + TEXT("_Head")) &&
            TryMesh(LeftArm, Prefix + TEXT("Arm.SM_") + ProductionFolder + TEXT("_Arm")) &&
            TryMesh(LeftLeg, Prefix + TEXT("Leg.SM_") + ProductionFolder + TEXT("_Leg")) &&
            TryMesh(Weapon, Prefix + WeaponSuffix + TEXT(".SM_") + ProductionFolder + TEXT("_") + WeaponSuffix);
        TryMesh(RightArm, Prefix + TEXT("Arm.SM_") + ProductionFolder + TEXT("_Arm"));
        TryMesh(RightLeg, Prefix + TEXT("Leg.SM_") + ProductionFolder + TEXT("_Leg"));
    }

    GetCapsuleComponent()->SetCapsuleRadius(32.0f * WidthScale);
    GetCapsuleComponent()->SetCapsuleHalfHeight(72.0f * HeightScale);

    Torso->SetRelativeLocation(FVector(0.0f, 0.0f, 0.0f));
    Torso->SetRelativeScale3D(FVector(0.34f * WidthScale, 0.26f * WidthScale, 0.48f * HeightScale));
    Head->SetRelativeLocation(FVector(0.0f, 0.0f, 52.0f * HeightScale));
    Head->SetRelativeScale3D(FVector(0.24f * WidthScale));
    LeftArm->SetRelativeLocation(FVector(0.0f, -30.0f * WidthScale, 3.0f * HeightScale));
    RightArm->SetRelativeLocation(FVector(0.0f, 30.0f * WidthScale, 3.0f * HeightScale));
    LeftArm->SetRelativeScale3D(FVector(0.09f * WidthScale, 0.09f * WidthScale, 0.42f * HeightScale));
    RightArm->SetRelativeScale3D(FVector(0.09f * WidthScale, 0.09f * WidthScale, 0.42f * HeightScale));
    LeftLeg->SetRelativeLocation(FVector(0.0f, -13.0f * WidthScale, -49.0f * HeightScale));
    RightLeg->SetRelativeLocation(FVector(0.0f, 13.0f * WidthScale, -49.0f * HeightScale));
    LeftLeg->SetRelativeScale3D(FVector(0.12f * WidthScale, 0.12f * WidthScale, 0.38f * HeightScale));
    RightLeg->SetRelativeScale3D(FVector(0.12f * WidthScale, 0.12f * WidthScale, 0.38f * HeightScale));
    Weapon->SetRelativeLocation(FVector(8.0f, 40.0f * WidthScale, -4.0f));
    Weapon->SetRelativeRotation(FRotator(-18.0f, 0.0f, 8.0f));
    Weapon->SetRelativeScale3D(
        EnemyType == EFellowshipEnemyType::CaveTroll
            ? FVector(0.62f, 0.10f, 0.10f)
            : (EnemyType == EFellowshipEnemyType::Lurtz
                ? FVector(0.54f, 0.055f, 0.070f)
                : FVector(0.46f, 0.045f, 0.055f)));

    if (bProductionVisual)
    {
        Torso->SetRelativeScale3D(FVector(1.0f));
        Head->SetRelativeScale3D(FVector(1.0f));
        LeftArm->SetRelativeScale3D(FVector(1.0f));
        RightArm->SetRelativeScale3D(FVector(1.0f));
        LeftLeg->SetRelativeScale3D(FVector(1.0f));
        RightLeg->SetRelativeScale3D(FVector(1.0f));
        Weapon->SetRelativeScale3D(FVector(1.0f));
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

    // Bare fallback primitives need runtime tinting. Imported production hero/
    // enemy parts now keep their authored OBJ/MTL materials instead of being flattened
    // back to the engine BasicShape material.
    if (!bProductionVisual)
    {
        ApplyColor(Torso, Armor);
        ApplyColor(Head, Skin);
        ApplyColor(LeftArm, Skin);
        ApplyColor(RightArm, Skin);
        ApplyColor(LeftLeg, Armor);
        ApplyColor(RightLeg, Armor);
        ApplyColor(Weapon, WeaponColor);
    }

    CurrentHealth = MaxHealth;
    bProfileApplied = true;
}

bool AFellowshipEnemyPrototype::IsEncounterAllowed() const
{
    if (RequiredQuestId == NAME_None)
    {
        return true;
    }

    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    return Quests &&
        Quests->GetActiveQuestId() == RequiredQuestId &&
        Quests->GetQuestStage(RequiredQuestId) >= RequiredMinStage;
}

void AFellowshipEnemyPrototype::SetEncounterActive(bool bActive)
{
    if (bEncounterStateInitialized && bEncounterActive == bActive)
    {
        return;
    }

    bEncounterStateInitialized = true;
    bEncounterActive = bActive;
    SetActorHiddenInGame(!bActive);
    SetActorEnableCollision(bActive && !bDefeated);
    PrimaryActorTick.TickInterval = bActive ? 0.05f : 0.50f;
}

void AFellowshipEnemyPrototype::UpdateVisualMotion(float DeltaSeconds, bool bMoving)
{
    if (bMoving)
    {
        WalkPhase += DeltaSeconds * (EnemyType == EFellowshipEnemyType::CaveTroll ? 4.0f : 7.0f);
    }

    const float Swing = bMoving ? FMath::Sin(WalkPhase) * 25.0f : 0.0f;
    LeftArm->SetRelativeRotation(FMath::RInterpTo(
        LeftArm->GetRelativeRotation(), FRotator(Swing, 0.0f, 0.0f), DeltaSeconds, 8.0f));
    RightArm->SetRelativeRotation(FMath::RInterpTo(
        RightArm->GetRelativeRotation(), FRotator(-Swing, 0.0f, 0.0f), DeltaSeconds, 8.0f));
    LeftLeg->SetRelativeRotation(FMath::RInterpTo(
        LeftLeg->GetRelativeRotation(), FRotator(-Swing * 0.60f, 0.0f, 0.0f), DeltaSeconds, 8.0f));
    RightLeg->SetRelativeRotation(FMath::RInterpTo(
        RightLeg->GetRelativeRotation(), FRotator(Swing * 0.60f, 0.0f, 0.0f), DeltaSeconds, 8.0f));
}

void AFellowshipEnemyPrototype::AttackPlayer(AShirePlayerCharacter* Player)
{
    if (!Player || AttackCooldownRemaining > 0.0f)
    {
        return;
    }

    AttackCooldownRemaining = AttackInterval;
    UGameplayStatics::ApplyDamage(Player, AttackDamage, nullptr, this, nullptr);
}

void AFellowshipEnemyPrototype::UpdateBehavior(float DeltaSeconds)
{
    AShirePlayerCharacter* Player = Cast<AShirePlayerCharacter>(
        UGameplayStatics::GetPlayerCharacter(this, 0));
    if (!Player)
    {
        return;
    }

    const float Distance = FVector::Dist2D(GetActorLocation(), Player->GetActorLocation());
    PrimaryActorTick.TickInterval = Distance > 4200.0f ? 0.30f : (Distance > 2200.0f ? 0.12f : 0.05f);

    FVector ToPlayer = Player->GetActorLocation() - GetActorLocation();
    ToPlayer.Z = 0.0f;

    bool bCanSeePlayer = false;
    if (Distance <= DetectionRadius)
    {
        FHitResult Hit;
        FCollisionQueryParams Params(SCENE_QUERY_STAT(FellowshipEnemySight), false, this);
        Params.AddIgnoredActor(this);
        const FVector Eye = GetActorLocation() + FVector(
            0.0f, 0.0f, GetCapsuleComponent()->GetScaledCapsuleHalfHeight() * 0.72f);
        const FVector Target = Player->GetActorLocation() + FVector(0.0f, 0.0f, 35.0f);

        if (GetWorld()->LineTraceSingleByChannel(Hit, Eye, Target, ECC_Visibility, Params))
        {
            bCanSeePlayer = Hit.GetActor() == Player;
        }
        else
        {
            bCanSeePlayer = true;
        }
    }

    bool bMoving = false;
    if (Distance <= AttackRange && (bCanSeePlayer || Distance < AttackRange * 0.80f))
    {
        if (!ToPlayer.IsNearlyZero())
        {
            SetActorRotation(FMath::RInterpTo(
                GetActorRotation(), ToPlayer.Rotation(), DeltaSeconds, 8.0f));
        }
        AttackPlayer(Player);
    }
    else if (bCanSeePlayer)
    {
        const FVector Direction = ToPlayer.GetSafeNormal2D();
        AddActorWorldOffset(Direction * MoveSpeed * DeltaSeconds, true);
        SetActorRotation(FMath::RInterpTo(
            GetActorRotation(), Direction.Rotation(), DeltaSeconds, 5.0f));
        bMoving = true;
    }
    else
    {
        FVector ToHome = HomeLocation - GetActorLocation();
        ToHome.Z = 0.0f;
        if (ToHome.Size2D() > 120.0f)
        {
            const FVector Direction = ToHome.GetSafeNormal2D();
            AddActorWorldOffset(Direction * MoveSpeed * 0.55f * DeltaSeconds, true);
            SetActorRotation(FMath::RInterpTo(
                GetActorRotation(), Direction.Rotation(), DeltaSeconds, 3.5f));
            bMoving = true;
        }
    }

    UpdateVisualMotion(DeltaSeconds, bMoving);
}

void AFellowshipEnemyPrototype::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (!bProfileApplied)
    {
        ApplyTypeProfile();
    }

    AttackCooldownRemaining = FMath::Max(0.0f, AttackCooldownRemaining - DeltaSeconds);

    if (bDefeated)
    {
        return;
    }

    const bool bAllowed = IsEncounterAllowed();
    SetEncounterActive(bAllowed);
    if (!bAllowed)
    {
        return;
    }

    UpdateBehavior(DeltaSeconds);
}

float AFellowshipEnemyPrototype::TakeDamage(
    float DamageAmount,
    FDamageEvent const& DamageEvent,
    AController* EventInstigator,
    AActor* DamageCauser)
{
    const float Applied = Super::TakeDamage(DamageAmount, DamageEvent, EventInstigator, DamageCauser);
    if (EnemyType == EFellowshipEnemyType::Lurtz)
    {
        // Lurtz's film outcome is not a player-controlled branch. Runtime damage can
        // create pressure but cannot kill or reward-rewrite this story actor.
        return 0.0f;
    }
    if (bDefeated || DamageAmount <= 0.0f)
    {
        return Applied;
    }

    CurrentHealth = FMath::Max(0.0f, CurrentHealth - DamageAmount);
    if (CurrentHealth <= 0.0f)
    {
        bDefeated = true;
        SetActorHiddenInGame(true);
        SetActorEnableCollision(false);
        PrimaryActorTick.SetTickFunctionEnable(false);
        SetLifeSpan(1.0f);
    }

    return DamageAmount;
}
