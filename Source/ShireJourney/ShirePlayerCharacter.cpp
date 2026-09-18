#include "ShirePlayerCharacter.h"
#include "ShireInteractable.h"
#include "ShireQuestSubsystem.h"
#include "ShireSaveGame.h"
#include "ShireHUD.h"
#include "ShireStoryPresentationSubsystem.h"
#include "FellowshipEnemyPrototype.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/InputComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SpringArmComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/GameInstance.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

namespace ShireSaveConstants
{
    static const FString SlotName(TEXT("ShireJourney_Auto"));
    static const int32 UserIndex = 0;
}

namespace ShireDebugChapters
{
    static const FName ChapterIds[] = {
        TEXT("P1C01"), TEXT("P1C02"), TEXT("P1C03"), TEXT("P1C04"),
        TEXT("P1C05"), TEXT("P1C06"), TEXT("P1C07"), TEXT("P1C08")
    };

    static const FName StartQuests[] = {
        TEXT("ShireArrival"), TEXT("RoadToBree"), TEXT("RoadToWeathertop"), TEXT("RivendellRecovery"),
        TEXT("SouthwardJourney"), TEXT("MoriaDark"), TEXT("LothlorienRest"), TEXT("AnduinJourney")
    };

    static const int32 Count = UE_ARRAY_COUNT(ChapterIds);
}

AShirePlayerCharacter::AShirePlayerCharacter()
{
    PrimaryActorTick.bCanEverTick = true;
    GetCapsuleComponent()->SetCapsuleRadius(28.0f);
    GetCapsuleComponent()->SetCapsuleHalfHeight(60.0f);

    bUseControllerRotationPitch = false;
    bUseControllerRotationYaw = false;
    bUseControllerRotationRoll = false;

    GetCharacterMovement()->bOrientRotationToMovement = true;
    GetCharacterMovement()->RotationRate = FRotator(0.0f, 480.0f, 0.0f);
    GetCharacterMovement()->MaxWalkSpeed = WalkSpeed;
    GetCharacterMovement()->GetNavAgentPropertiesRef().bCanCrouch = true;

    CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
    CameraBoom->SetupAttachment(RootComponent);
    CameraBoom->TargetArmLength = 315.0f;
    CameraBoom->bUsePawnControlRotation = true;
    CameraBoom->bEnableCameraLag = true;
    CameraBoom->CameraLagSpeed = 11.0f;
    CameraBoom->SetRelativeLocation(FVector(0.0f, 0.0f, 58.0f));

    FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
    FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
    FollowCamera->bUsePawnControlRotation = false;

    PrototypeTorso = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeTorso"));
    PrototypeTorso->SetupAttachment(GetCapsuleComponent());
    PrototypeTorso->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeTorso->SetRelativeLocation(FVector(0.0f, 0.0f, -4.0f));
    PrototypeTorso->SetRelativeScale3D(FVector(0.30f, 0.22f, 0.36f));

    PrototypeHead = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeHead"));
    PrototypeHead->SetupAttachment(GetCapsuleComponent());
    PrototypeHead->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeHead->SetRelativeLocation(FVector(0.0f, 0.0f, 39.0f));
    PrototypeHead->SetRelativeScale3D(FVector(0.23f));

    PrototypeHair = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeHair"));
    PrototypeHair->SetupAttachment(GetCapsuleComponent());
    PrototypeHair->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeHair->SetRelativeLocation(FVector(-1.0f, 0.0f, 47.0f));
    PrototypeHair->SetRelativeScale3D(FVector(0.235f, 0.235f, 0.11f));

    PrototypeLeftArm = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeLeftArm"));
    PrototypeLeftArm->SetupAttachment(GetCapsuleComponent());
    PrototypeLeftArm->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeLeftArm->SetRelativeLocation(FVector(0.0f, -24.0f, -3.0f));
    PrototypeLeftArm->SetRelativeScale3D(FVector(0.08f, 0.08f, 0.34f));

    PrototypeRightArm = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeRightArm"));
    PrototypeRightArm->SetupAttachment(GetCapsuleComponent());
    PrototypeRightArm->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeRightArm->SetRelativeLocation(FVector(0.0f, 24.0f, -3.0f));
    PrototypeRightArm->SetRelativeScale3D(FVector(0.08f, 0.08f, 0.34f));

    PrototypeLeftLeg = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeLeftLeg"));
    PrototypeLeftLeg->SetupAttachment(GetCapsuleComponent());
    PrototypeLeftLeg->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeLeftLeg->SetRelativeLocation(FVector(0.0f, -10.0f, -43.0f));
    PrototypeLeftLeg->SetRelativeScale3D(FVector(0.10f, 0.10f, 0.30f));

    PrototypeRightLeg = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeRightLeg"));
    PrototypeRightLeg->SetupAttachment(GetCapsuleComponent());
    PrototypeRightLeg->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeRightLeg->SetRelativeLocation(FVector(0.0f, 10.0f, -43.0f));
    PrototypeRightLeg->SetRelativeScale3D(FVector(0.10f, 0.10f, 0.30f));

    PrototypeLeftFoot = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeLeftFoot"));
    PrototypeLeftFoot->SetupAttachment(GetCapsuleComponent());
    PrototypeLeftFoot->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeLeftFoot->SetRelativeLocation(FVector(8.0f, -10.0f, -57.0f));
    PrototypeLeftFoot->SetRelativeScale3D(FVector(0.22f, 0.12f, 0.08f));

    PrototypeRightFoot = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeRightFoot"));
    PrototypeRightFoot->SetupAttachment(GetCapsuleComponent());
    PrototypeRightFoot->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeRightFoot->SetRelativeLocation(FVector(8.0f, 10.0f, -57.0f));
    PrototypeRightFoot->SetRelativeScale3D(FVector(0.22f, 0.12f, 0.08f));

    PrototypeWeapon = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeWeapon"));
    PrototypeWeapon->SetupAttachment(GetCapsuleComponent());
    PrototypeWeapon->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeWeapon->SetRelativeLocation(FVector(8.0f, 29.0f, -4.0f));
    PrototypeWeapon->SetRelativeRotation(FRotator(-10.0f, 0.0f, 8.0f));
    PrototypeWeapon->SetRelativeScale3D(FVector(0.05f, 0.05f, 0.48f));

    PrototypeCloak = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeCloak"));
    PrototypeCloak->SetupAttachment(GetCapsuleComponent());
    PrototypeCloak->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    PrototypeHat = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeHat"));
    PrototypeHat->SetupAttachment(GetCapsuleComponent());
    PrototypeHat->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    PrototypeBeard = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeBeard"));
    PrototypeBeard->SetupAttachment(GetCapsuleComponent());
    PrototypeBeard->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    PrototypeLeftEye = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeLeftEye"));
    PrototypeLeftEye->SetupAttachment(GetCapsuleComponent());
    PrototypeLeftEye->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    PrototypeRightEye = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeRightEye"));
    PrototypeRightEye->SetupAttachment(GetCapsuleComponent());
    PrototypeRightEye->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    PrototypeMouth = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeMouth"));
    PrototypeMouth->SetupAttachment(GetCapsuleComponent());
    PrototypeMouth->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    PrototypeSatchel = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeSatchel"));
    PrototypeSatchel->SetupAttachment(GetCapsuleComponent());
    PrototypeSatchel->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> ConeMesh(TEXT("/Engine/BasicShapes/Cone.Cone"));

    if (CubeMesh.Succeeded())
    {
        PrototypeTorso->SetStaticMesh(CubeMesh.Object);
        PrototypeWeapon->SetStaticMesh(CubeMesh.Object);
        PrototypeMouth->SetStaticMesh(CubeMesh.Object);
        PrototypeSatchel->SetStaticMesh(CubeMesh.Object);
    }
    if (CylinderMesh.Succeeded())
    {
        PrototypeLeftArm->SetStaticMesh(CylinderMesh.Object);
        PrototypeRightArm->SetStaticMesh(CylinderMesh.Object);
        PrototypeLeftLeg->SetStaticMesh(CylinderMesh.Object);
        PrototypeRightLeg->SetStaticMesh(CylinderMesh.Object);
    }
    if (SphereMesh.Succeeded())
    {
        PrototypeHead->SetStaticMesh(SphereMesh.Object);
        PrototypeHair->SetStaticMesh(SphereMesh.Object);
        PrototypeLeftFoot->SetStaticMesh(SphereMesh.Object);
        PrototypeRightFoot->SetStaticMesh(SphereMesh.Object);
        PrototypeLeftEye->SetStaticMesh(SphereMesh.Object);
        PrototypeRightEye->SetStaticMesh(SphereMesh.Object);
    }
    if (ConeMesh.Succeeded())
    {
        PrototypeCloak->SetStaticMesh(ConeMesh.Object);
        PrototypeHat->SetStaticMesh(ConeMesh.Object);
        PrototypeBeard->SetStaticMesh(ConeMesh.Object);
    }
}

void AShirePlayerCharacter::ApplyPrototypeStyle()
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

        UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(BasicMaterial, this);
        if (MID)
        {
            MID->SetVectorParameterValue(TEXT("Color"), Color);
            Component->SetMaterial(0, MID);
        }
    };

    FName CharacterId = TEXT("Frodo");
    if (UGameInstance* GI = GetGameInstance())
    {
        if (UShireQuestSubsystem* Quests = GI->GetSubsystem<UShireQuestSubsystem>())
        {
            CharacterId = Quests->GetPlayableCharacterId();
        }
    }

    bPrototypeIsGandalf = CharacterId == TEXT("Gandalf");
    const bool bGandalf = bPrototypeIsGandalf;

    GetCapsuleComponent()->SetCapsuleHalfHeight(bGandalf ? 86.0f : 60.0f);

    PrototypeTorsoBaseZ = bGandalf ? 10.0f : -4.0f;
    PrototypeHeadBaseZ = bGandalf ? 66.0f : 39.0f;
    PrototypeHairBaseZ = bGandalf ? 73.0f : 47.0f;

    PrototypeTorso->SetRelativeLocation(FVector(0.0f, 0.0f, PrototypeTorsoBaseZ));
    PrototypeTorso->SetRelativeScale3D(bGandalf ? FVector(0.29f, 0.22f, 0.52f) : FVector(0.27f, 0.20f, 0.35f));
    PrototypeHead->SetRelativeLocation(FVector(0.0f, 0.0f, PrototypeHeadBaseZ));
    PrototypeHead->SetRelativeScale3D(bGandalf ? FVector(0.205f,0.19f,0.235f) : FVector(0.225f,0.215f,0.235f));
    PrototypeHair->SetRelativeLocation(FVector(-2.0f, 0.0f, PrototypeHairBaseZ));
    PrototypeHair->SetRelativeScale3D(bGandalf ? FVector(0.22f,0.21f,0.14f) : FVector(0.235f,0.235f,0.12f));

    PrototypeLeftArm->SetRelativeLocation(FVector(0.0f, -23.0f, bGandalf ? 10.0f : -3.0f));
    PrototypeRightArm->SetRelativeLocation(FVector(0.0f, 23.0f, bGandalf ? 10.0f : -3.0f));
    PrototypeLeftArm->SetRelativeScale3D(bGandalf ? FVector(0.075f,0.075f,0.46f) : FVector(0.075f,0.075f,0.33f));
    PrototypeRightArm->SetRelativeScale3D(bGandalf ? FVector(0.075f,0.075f,0.46f) : FVector(0.075f,0.075f,0.33f));

    PrototypeLeftLeg->SetRelativeLocation(FVector(0.0f, -9.5f, bGandalf ? -50.0f : -43.0f));
    PrototypeRightLeg->SetRelativeLocation(FVector(0.0f, 9.5f, bGandalf ? -50.0f : -43.0f));
    PrototypeLeftLeg->SetRelativeScale3D(bGandalf ? FVector(0.085f,0.085f,0.36f) : FVector(0.095f,0.095f,0.29f));
    PrototypeRightLeg->SetRelativeScale3D(bGandalf ? FVector(0.085f,0.085f,0.36f) : FVector(0.095f,0.095f,0.29f));

    PrototypeLeftFoot->SetRelativeLocation(FVector(8.0f, -10.0f, bGandalf ? -78.0f : -57.0f));
    PrototypeRightFoot->SetRelativeLocation(FVector(8.0f, 10.0f, bGandalf ? -78.0f : -57.0f));
    PrototypeLeftFoot->SetRelativeScale3D(bGandalf ? FVector(0.18f,0.105f,0.07f) : FVector(0.23f,0.135f,0.075f));
    PrototypeRightFoot->SetRelativeScale3D(bGandalf ? FVector(0.18f,0.105f,0.07f) : FVector(0.23f,0.135f,0.075f));

    // Silhouette pieces: a separate cloak, face, and wizard hat/beard make the two
    // playable routes readable before final skeletal meshes arrive.
    PrototypeCloak->SetRelativeLocation(FVector(-9.0f, 0.0f, bGandalf ? -1.0f : -9.0f));
    PrototypeCloak->SetRelativeScale3D(bGandalf ? FVector(0.38f,0.33f,0.72f) : FVector(0.30f,0.27f,0.42f));
    PrototypeCloak->SetRelativeRotation(FRotator(0.0f, 0.0f, 0.0f));

    PrototypeHat->SetVisibility(bGandalf, true);
    PrototypeHat->SetRelativeLocation(FVector(-1.0f,0.0f,101.0f));
    PrototypeHat->SetRelativeScale3D(FVector(0.34f,0.34f,0.48f));

    PrototypeBeard->SetVisibility(bGandalf, true);
    PrototypeBeard->SetRelativeLocation(FVector(10.0f,0.0f,48.0f));
    PrototypeBeard->SetRelativeRotation(FRotator(180.0f,0.0f,0.0f));
    PrototypeBeard->SetRelativeScale3D(FVector(0.14f,0.13f,0.28f));

    const float FaceZ = PrototypeHeadBaseZ + 1.5f;
    PrototypeLeftEye->SetRelativeLocation(FVector(10.5f,-5.2f,FaceZ+2.0f));
    PrototypeRightEye->SetRelativeLocation(FVector(10.5f,5.2f,FaceZ+2.0f));
    PrototypeLeftEye->SetRelativeScale3D(FVector(0.035f,0.025f,0.045f));
    PrototypeRightEye->SetRelativeScale3D(FVector(0.035f,0.025f,0.045f));
    PrototypeMouth->SetRelativeLocation(FVector(10.7f,0.0f,FaceZ-5.0f));
    PrototypeMouth->SetRelativeScale3D(FVector(0.018f,0.065f,0.012f));

    PrototypeSatchel->SetVisibility(!bGandalf, true);
    PrototypeSatchel->SetRelativeLocation(FVector(-3.0f,22.0f,-5.0f));
    PrototypeSatchel->SetRelativeRotation(FRotator(0.0f,12.0f,8.0f));
    PrototypeSatchel->SetRelativeScale3D(FVector(0.13f,0.06f,0.15f));

    const FLinearColor Skin = bGandalf ? FLinearColor(0.72f,0.54f,0.40f) : FLinearColor(0.78f,0.57f,0.39f);
    const FLinearColor DarkEye(0.035f,0.028f,0.020f);
    const FLinearColor Mouth(0.23f,0.055f,0.045f);

    ApplyColor(PrototypeTorso, bGandalf ? FLinearColor(0.28f,0.29f,0.27f) : FLinearColor(0.18f,0.31f,0.135f));
    ApplyColor(PrototypeHead, Skin);
    ApplyColor(PrototypeHair, bGandalf ? FLinearColor(0.69f,0.68f,0.63f) : FLinearColor(0.105f,0.045f,0.020f));
    ApplyColor(PrototypeLeftArm, bGandalf ? FLinearColor(0.25f,0.26f,0.24f) : FLinearColor(0.20f,0.35f,0.15f));
    ApplyColor(PrototypeRightArm, bGandalf ? FLinearColor(0.25f,0.26f,0.24f) : FLinearColor(0.20f,0.35f,0.15f));
    ApplyColor(PrototypeLeftLeg, bGandalf ? FLinearColor(0.17f,0.18f,0.17f) : FLinearColor(0.27f,0.17f,0.075f));
    ApplyColor(PrototypeRightLeg, bGandalf ? FLinearColor(0.17f,0.18f,0.17f) : FLinearColor(0.27f,0.17f,0.075f));
    ApplyColor(PrototypeLeftFoot, bGandalf ? FLinearColor(0.095f,0.09f,0.085f) : FLinearColor(0.22f,0.105f,0.04f));
    ApplyColor(PrototypeRightFoot, bGandalf ? FLinearColor(0.095f,0.09f,0.085f) : FLinearColor(0.22f,0.105f,0.04f));
    ApplyColor(PrototypeCloak, bGandalf ? FLinearColor(0.24f,0.25f,0.235f) : FLinearColor(0.16f,0.24f,0.105f));
    ApplyColor(PrototypeHat, FLinearColor(0.245f,0.25f,0.235f));
    ApplyColor(PrototypeBeard, FLinearColor(0.68f,0.67f,0.62f));
    ApplyColor(PrototypeLeftEye, DarkEye);
    ApplyColor(PrototypeRightEye, DarkEye);
    ApplyColor(PrototypeMouth, Mouth);
    ApplyColor(PrototypeSatchel, FLinearColor(0.26f,0.13f,0.045f));

    const bool bCombatAvailable = IsCombatAvailable();
    PrototypeWeapon->SetVisibility(bGandalf || bCombatAvailable, true);
    PrototypeWeapon->SetRelativeLocation(bGandalf ? FVector(4.0f,34.0f,-1.0f) : FVector(8.0f,29.0f,-4.0f));
    PrototypeWeapon->SetRelativeScale3D(bGandalf ? FVector(0.055f,0.055f,0.92f) : FVector(0.045f,0.045f,0.48f));
    PrototypeWeapon->SetRelativeRotation(bGandalf ? FRotator::ZeroRotator : FRotator(-10.0f,0.0f,8.0f));
    ApplyColor(PrototypeWeapon, bGandalf ? FLinearColor(0.22f,0.13f,0.055f) : FLinearColor(0.48f,0.50f,0.52f));
}

void AShirePlayerCharacter::UpdatePrototypeAnimation(float DeltaSeconds)
{
    const float Speed = GetVelocity().Size2D();
    const bool bMoving = Speed > 5.0f && !bCinematicInputLocked;

    float Swing = 0.0f;
    float Bob = 0.0f;
    if (bMoving)
    {
        const float SpeedRatio = FMath::Clamp(Speed / FMath::Max(1.0f, WalkSpeed), 0.55f, 1.8f);
        PrototypeWalkPhase += DeltaSeconds * 8.0f * SpeedRatio;
        Swing = FMath::Sin(PrototypeWalkPhase) * 28.0f;
        Bob = FMath::Abs(FMath::Sin(PrototypeWalkPhase * 2.0f)) * 1.5f;
    }

    const float BlendSpeed = 10.0f;
    if (PrototypeLeftArm)
    {
        PrototypeLeftArm->SetRelativeRotation(FMath::RInterpTo(
            PrototypeLeftArm->GetRelativeRotation(), FRotator(Swing, 0.0f, 0.0f), DeltaSeconds, BlendSpeed));
    }
    if (PrototypeRightArm)
    {
        const float RightArmPitch = AttackVisualRemaining > 0.0f ? -82.0f : -Swing;
        PrototypeRightArm->SetRelativeRotation(FMath::RInterpTo(
            PrototypeRightArm->GetRelativeRotation(), FRotator(RightArmPitch, 0.0f, 0.0f), DeltaSeconds, BlendSpeed));
    }
    if (PrototypeLeftLeg)
    {
        PrototypeLeftLeg->SetRelativeRotation(FMath::RInterpTo(
            PrototypeLeftLeg->GetRelativeRotation(), FRotator(-Swing * 0.65f, 0.0f, 0.0f), DeltaSeconds, BlendSpeed));
    }
    if (PrototypeRightLeg)
    {
        PrototypeRightLeg->SetRelativeRotation(FMath::RInterpTo(
            PrototypeRightLeg->GetRelativeRotation(), FRotator(Swing * 0.65f, 0.0f, 0.0f), DeltaSeconds, BlendSpeed));
    }

    if (PrototypeTorso)
    {
        PrototypeTorso->SetRelativeLocation(FMath::VInterpTo(
            PrototypeTorso->GetRelativeLocation(), FVector(0.0f, 0.0f, PrototypeTorsoBaseZ + Bob), DeltaSeconds, 12.0f));
    }
    if (PrototypeHead)
    {
        PrototypeHead->SetRelativeLocation(FMath::VInterpTo(
            PrototypeHead->GetRelativeLocation(), FVector(0.0f, 0.0f, PrototypeHeadBaseZ + Bob), DeltaSeconds, 12.0f));
    }
    if (PrototypeHair)
    {
        PrototypeHair->SetRelativeLocation(FMath::VInterpTo(
            PrototypeHair->GetRelativeLocation(), FVector(-2.0f, 0.0f, PrototypeHairBaseZ + Bob), DeltaSeconds, 12.0f));
    }

    if (PrototypeCloak)
    {
        const float CloakPitch = bMoving ? -4.0f - Swing * 0.07f : -2.0f;
        PrototypeCloak->SetRelativeRotation(FMath::RInterpTo(
            PrototypeCloak->GetRelativeRotation(), FRotator(CloakPitch,0.0f,0.0f), DeltaSeconds, 5.0f));
    }

    const float FaceZ = PrototypeHeadBaseZ + 1.5f + Bob;
    if (PrototypeLeftEye)
    {
        PrototypeLeftEye->SetRelativeLocation(FVector(10.5f,-5.2f,FaceZ+2.0f));
    }
    if (PrototypeRightEye)
    {
        PrototypeRightEye->SetRelativeLocation(FVector(10.5f,5.2f,FaceZ+2.0f));
    }
    if (PrototypeMouth)
    {
        PrototypeMouth->SetRelativeLocation(FVector(10.7f,0.0f,FaceZ-5.0f));
    }
    if (bPrototypeIsGandalf)
    {
        if (PrototypeHat)
        {
            PrototypeHat->SetRelativeLocation(FVector(-1.0f,0.0f,101.0f + Bob));
        }
        if (PrototypeBeard)
        {
            PrototypeBeard->SetRelativeLocation(FVector(10.0f,0.0f,48.0f + Bob));
        }
    }
}

void AShirePlayerCharacter::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    AttackCooldownRemaining = FMath::Max(0.0f, AttackCooldownRemaining - DeltaSeconds);
    AttackVisualRemaining = FMath::Max(0.0f, AttackVisualRemaining - DeltaSeconds);
    UpdatePrototypeAnimation(DeltaSeconds);
}

void AShirePlayerCharacter::BeginPlay()
{
    Super::BeginPlay();
    GetCharacterMovement()->MaxWalkSpeed = WalkSpeed;
    ApplyPrototypeStyle();

    if (UGameInstance* GI = GetGameInstance())
    {
        if (UShireStoryPresentationSubsystem* Presentation = GI->GetSubsystem<UShireStoryPresentationSubsystem>())
        {
            Presentation->OnCinematicStateChanged.AddDynamic(this, &AShirePlayerCharacter::HandleCinematicStateChanged);
        }
        if (UShireQuestSubsystem* Quests = GI->GetSubsystem<UShireQuestSubsystem>())
        {
            Quests->OnExperienceChanged.AddDynamic(this, &AShirePlayerCharacter::HandleExperienceChanged);
            Quests->OnChapterChanged.AddDynamic(this, &AShirePlayerCharacter::HandleChapterChanged);
        }
    }
}

void AShirePlayerCharacter::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (UGameInstance* GI = GetGameInstance())
    {
        if (UShireStoryPresentationSubsystem* Presentation = GI->GetSubsystem<UShireStoryPresentationSubsystem>())
        {
            Presentation->OnCinematicStateChanged.RemoveDynamic(this, &AShirePlayerCharacter::HandleCinematicStateChanged);
        }
        if (UShireQuestSubsystem* Quests = GI->GetSubsystem<UShireQuestSubsystem>())
        {
            Quests->OnExperienceChanged.RemoveDynamic(this, &AShirePlayerCharacter::HandleExperienceChanged);
            Quests->OnChapterChanged.RemoveDynamic(this, &AShirePlayerCharacter::HandleChapterChanged);
        }
    }

    Super::EndPlay(EndPlayReason);
}

void AShirePlayerCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    PlayerInputComponent->BindAxis(TEXT("MoveForward"), this, &AShirePlayerCharacter::MoveForward);
    PlayerInputComponent->BindAxis(TEXT("MoveRight"), this, &AShirePlayerCharacter::MoveRight);
    PlayerInputComponent->BindAxis(TEXT("Turn"), this, &AShirePlayerCharacter::TurnAtRate);
    PlayerInputComponent->BindAxis(TEXT("LookUp"), this, &AShirePlayerCharacter::LookUpAtRate);

    PlayerInputComponent->BindAction(TEXT("Jump"), IE_Pressed, this, &AShirePlayerCharacter::StartJump);
    PlayerInputComponent->BindAction(TEXT("Jump"), IE_Released, this, &AShirePlayerCharacter::StopJump);
    PlayerInputComponent->BindAction(TEXT("Crouch"), IE_Pressed, this, &AShirePlayerCharacter::StartCrouch);
    PlayerInputComponent->BindAction(TEXT("Crouch"), IE_Released, this, &AShirePlayerCharacter::StopCrouch);
    PlayerInputComponent->BindAction(TEXT("Sprint"), IE_Pressed, this, &AShirePlayerCharacter::StartSprint);
    PlayerInputComponent->BindAction(TEXT("Sprint"), IE_Released, this, &AShirePlayerCharacter::StopSprint);
    PlayerInputComponent->BindAction(TEXT("Interact"), IE_Pressed, this, &AShirePlayerCharacter::Interact);
    PlayerInputComponent->BindAction(TEXT("PrimaryAttack"), IE_Pressed, this, &AShirePlayerCharacter::PrimaryAttack);
    PlayerInputComponent->BindAction(TEXT("QuickSave"), IE_Pressed, this, &AShirePlayerCharacter::QuickSave);
    PlayerInputComponent->BindAction(TEXT("QuickLoad"), IE_Pressed, this, &AShirePlayerCharacter::QuickLoad);
    PlayerInputComponent->BindAction(TEXT("DebugPreviousChapter"), IE_Pressed, this, &AShirePlayerCharacter::DebugPreviousChapter);
    PlayerInputComponent->BindAction(TEXT("DebugNextChapter"), IE_Pressed, this, &AShirePlayerCharacter::DebugNextChapter);
    PlayerInputComponent->BindAction(TEXT("DebugAlternateRoute"), IE_Pressed, this, &AShirePlayerCharacter::DebugToggleParallelRoute);
}

void AShirePlayerCharacter::HandleExperienceChanged(FName RouteId, FName EpisodeId, FName InPlayableCharacterId)
{
    ApplyPrototypeStyle();

    if (APlayerController* PC = Cast<APlayerController>(Controller))
    {
        if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
        {
            HUD->ShowAlert(FText::FromString(FString::Printf(
                TEXT("Now playing: %s  |  %s"),
                *InPlayableCharacterId.ToString(),
                *EpisodeId.ToString())), 3.0f);
        }
    }
}

void AShirePlayerCharacter::HandleChapterChanged(FName PreviousChapterId, FName NewChapterId)
{
    CurrentHealth = FMath::Clamp(CurrentHealth, 1.0f, MaxHealth);
    ApplyPrototypeStyle();
}

void AShirePlayerCharacter::HandleCinematicStateChanged(bool bLocked)
{
    bCinematicInputLocked = bLocked;

    if (APlayerController* PC = Cast<APlayerController>(Controller))
    {
        PC->SetIgnoreMoveInput(bLocked);
        PC->SetIgnoreLookInput(bLocked);
    }

    if (bLocked)
    {
        StopJumping();
        UnCrouch();
        GetCharacterMovement()->StopMovementImmediately();
        GetCharacterMovement()->MaxWalkSpeed = WalkSpeed;
    }
}

void AShirePlayerCharacter::MoveForward(float Value)
{
    if (!bCinematicInputLocked && Controller && !FMath::IsNearlyZero(Value))
    {
        const FRotator Rotation = Controller->GetControlRotation();
        const FRotator YawRotation(0.0f, Rotation.Yaw, 0.0f);
        AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X), Value);
    }
}

void AShirePlayerCharacter::MoveRight(float Value)
{
    if (!bCinematicInputLocked && Controller && !FMath::IsNearlyZero(Value))
    {
        const FRotator Rotation = Controller->GetControlRotation();
        const FRotator YawRotation(0.0f, Rotation.Yaw, 0.0f);
        AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y), Value);
    }
}

void AShirePlayerCharacter::TurnAtRate(float Value)
{
    if (!bCinematicInputLocked && GetWorld())
    {
        AddControllerYawInput(Value * BaseTurnRate * GetWorld()->GetDeltaSeconds());
    }
}

void AShirePlayerCharacter::LookUpAtRate(float Value)
{
    if (!bCinematicInputLocked && GetWorld())
    {
        AddControllerPitchInput(Value * BaseLookUpRate * GetWorld()->GetDeltaSeconds());
    }
}

void AShirePlayerCharacter::StartJump()
{
    if (!bCinematicInputLocked)
    {
        Jump();
    }
}

void AShirePlayerCharacter::StopJump()
{
    StopJumping();
}

void AShirePlayerCharacter::StartSprint()
{
    if (!bCinematicInputLocked)
    {
        GetCharacterMovement()->MaxWalkSpeed = SprintSpeed;
    }
}

void AShirePlayerCharacter::StopSprint()
{
    GetCharacterMovement()->MaxWalkSpeed = WalkSpeed;
}

void AShirePlayerCharacter::StartCrouch()
{
    if (!bCinematicInputLocked)
    {
        Crouch();
    }
}

void AShirePlayerCharacter::StopCrouch()
{
    UnCrouch();
}


bool AShirePlayerCharacter::IsCombatAvailable() const
{
    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!Quests)
    {
        return false;
    }

    if (Quests->GetPlayableCharacterId() == TEXT("Gandalf"))
    {
        return true;
    }

    const FName Chapter = Quests->GetCurrentChapterId();
    return Chapter == TEXT("P1C03") || Chapter == TEXT("P1C05") ||
        Chapter == TEXT("P1C06") || Chapter == TEXT("P1C08");
}

float AShirePlayerCharacter::TakeDamage(
    float DamageAmount,
    FDamageEvent const& DamageEvent,
    AController* EventInstigator,
    AActor* DamageCauser)
{
    const float Applied = Super::TakeDamage(DamageAmount, DamageEvent, EventInstigator, DamageCauser);
    if (DamageAmount <= 0.0f || !IsCombatAvailable())
    {
        return Applied;
    }

    CurrentHealth = FMath::Max(1.0f, CurrentHealth - DamageAmount);

    if (APlayerController* PC = Cast<APlayerController>(Controller))
    {
        if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
        {
            HUD->ShowAlert(
                CurrentHealth <= MaxHealth * 0.25f
                    ? FText::FromString(TEXT("Health critical. Break contact and recover."))
                    : FText::FromString(TEXT("Hit!")),
                0.9f);
        }
    }

    return DamageAmount;
}

void AShirePlayerCharacter::PrimaryAttack()
{
    if (bCinematicInputLocked || AttackCooldownRemaining > 0.0f || !IsCombatAvailable() || !GetWorld())
    {
        return;
    }

    AttackCooldownRemaining = AttackCooldown;
    AttackVisualRemaining = 0.22f;

    const FVector Start = GetActorLocation() + FVector(0.0f, 0.0f, 32.0f);
    const FVector End = Start + GetActorForwardVector() * AttackRange;

    TArray<FHitResult> Hits;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(PlayerMeleeAttack), false, this);
    Params.AddIgnoredActor(this);

    const FCollisionShape Shape = FCollisionShape::MakeSphere(52.0f);
    if (GetWorld()->SweepMultiByChannel(Hits, Start, End, FQuat::Identity, ECC_Pawn, Shape, Params))
    {
        for (const FHitResult& Hit : Hits)
        {
            AFellowshipEnemyPrototype* Enemy = Cast<AFellowshipEnemyPrototype>(Hit.GetActor());
            if (Enemy && !Enemy->IsDefeated())
            {
                UGameplayStatics::ApplyDamage(Enemy, AttackDamage, Controller, this, nullptr);
                break;
            }
        }
    }
}

void AShirePlayerCharacter::Interact()
{
    if (bCinematicInputLocked || !FollowCamera || !GetWorld())
    {
        return;
    }

    const FVector Start = FollowCamera->GetComponentLocation();
    const FVector End = Start + FollowCamera->GetForwardVector() * InteractionDistance;

    FHitResult Hit;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(ShireInteract), false, this);
    if (GetWorld()->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Params))
    {
        AActor* HitActor = Hit.GetActor();
        if (HitActor && HitActor->GetClass()->ImplementsInterface(UShireInteractable::StaticClass()))
        {
            IShireInteractable::Execute_Interact(HitActor, this);
            return;
        }
    }

    if (APlayerController* PC = Cast<APlayerController>(Controller))
    {
        if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
        {
            HUD->ShowAlert(FText::FromString(TEXT("Nothing nearby to interact with.")), 1.5f);
        }
    }
}

void AShirePlayerCharacter::QuickSave()
{
    UShireSaveGame* Save = Cast<UShireSaveGame>(UGameplayStatics::CreateSaveGameObject(UShireSaveGame::StaticClass()));
    if (!Save)
    {
        return;
    }

    Save->PlayerLocation = GetActorLocation();
    Save->PlayerRotation = GetActorRotation();

    if (UGameInstance* GI = GetGameInstance())
    {
        if (UShireQuestSubsystem* QuestSubsystem = GI->GetSubsystem<UShireQuestSubsystem>())
        {
            Save->QuestStages = QuestSubsystem->GetAllQuestStages();
            Save->ActiveQuestId = QuestSubsystem->GetActiveQuestId();
            Save->CurrentChapterId = QuestSubsystem->GetCurrentChapterId();
            Save->CompletedStoryBeats = QuestSubsystem->GetCompletedStoryBeats();
            Save->CurrentRouteId = QuestSubsystem->GetCurrentRouteId();
            Save->CurrentEpisodeId = QuestSubsystem->GetCurrentEpisodeId();
            Save->PlayableCharacterId = QuestSubsystem->GetPlayableCharacterId();
            Save->RouteProgress = QuestSubsystem->GetRouteProgressSnapshot();
            Save->PlayerHealth = CurrentHealth;
        }
    }

    const bool bSaved = UGameplayStatics::SaveGameToSlot(Save, ShireSaveConstants::SlotName, ShireSaveConstants::UserIndex);
    if (APlayerController* PC = Cast<APlayerController>(Controller))
    {
        if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
        {
            HUD->ShowAlert(FText::FromString(bSaved ? TEXT("Journey saved.") : TEXT("Save failed.")), 1.8f);
        }
    }
}

void AShirePlayerCharacter::QuickLoad()
{
    if (!UGameplayStatics::DoesSaveGameExist(ShireSaveConstants::SlotName, ShireSaveConstants::UserIndex))
    {
        if (APlayerController* PC = Cast<APlayerController>(Controller))
        {
            if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
            {
                HUD->ShowAlert(FText::FromString(TEXT("No save found yet.")), 1.8f);
            }
        }
        return;
    }

    UShireSaveGame* Save = Cast<UShireSaveGame>(UGameplayStatics::LoadGameFromSlot(
        ShireSaveConstants::SlotName, ShireSaveConstants::UserIndex));
    if (!Save)
    {
        return;
    }

    bool bApplyExactSavedTransform = true;
    if (UGameInstance* GI = GetGameInstance())
    {
        if (UShireQuestSubsystem* QuestSubsystem = GI->GetSubsystem<UShireQuestSubsystem>())
        {
            const FName SavedChapterId = Save->CurrentChapterId == NAME_None ? FName(TEXT("P1C01")) : Save->CurrentChapterId;

            QuestSubsystem->RestoreQuestState(
                Save->QuestStages,
                Save->ActiveQuestId,
                Save->CurrentChapterId,
                Save->CompletedStoryBeats,
                Save->CurrentRouteId,
                Save->CurrentEpisodeId,
                Save->PlayableCharacterId,
                Save->RouteProgress);

            // A compatibility repair may advance a legacy terminal save into the next
            // runtime chapter. In that case the router has already placed the pawn at the
            // safe chapter spawn, so restoring coordinates from the previous region would
            // put the player outside the newly generated world.
            bApplyExactSavedTransform = QuestSubsystem->GetCurrentChapterId() == SavedChapterId;
        }
    }

    CurrentHealth = FMath::Clamp(Save->PlayerHealth, 1.0f, MaxHealth);

    if (bApplyExactSavedTransform)
    {
        SetActorLocationAndRotation(Save->PlayerLocation, Save->PlayerRotation, false, nullptr, ETeleportType::TeleportPhysics);
    }

    ApplyPrototypeStyle();

    if (APlayerController* PC = Cast<APlayerController>(Controller))
    {
        if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
        {
            HUD->ShowAlert(FText::FromString(TEXT("Journey restored.")), 1.8f);
        }
    }
}


void AShirePlayerCharacter::DebugToggleParallelRoute()
{
    if (bCinematicInputLocked)
    {
        return;
    }

    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!Quests)
    {
        return;
    }

    if (Quests->GetCurrentRouteId() == TEXT("GandalfParallel"))
    {
        Quests->StartExperience(TEXT("FrodoMain"), NAME_None, TEXT("Frodo"), NAME_None);
    }
    else
    {
        Quests->StartExperience(TEXT("GandalfParallel"), TEXT("P1G01_Isengard"), TEXT("Gandalf"),
            TEXT("P1C01"), TEXT("IsengardCounsel"), 0);
    }
}

void AShirePlayerCharacter::DebugStartChapterByIndex(int32 ChapterIndex)
{
    if (bCinematicInputLocked || ChapterIndex < 0 || ChapterIndex >= ShireDebugChapters::Count)
    {
        return;
    }

    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* QuestSubsystem = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!QuestSubsystem)
    {
        return;
    }

    QuestSubsystem->StartChapter(
        ShireDebugChapters::ChapterIds[ChapterIndex],
        ShireDebugChapters::StartQuests[ChapterIndex],
        0);

    if (APlayerController* PC = Cast<APlayerController>(Controller))
    {
        if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
        {
            HUD->ShowAlert(FText::FromString(FString::Printf(TEXT("Developer jump: %s"), *ShireDebugChapters::ChapterIds[ChapterIndex].ToString())), 2.0f);
        }
    }
}

void AShirePlayerCharacter::DebugPreviousChapter()
{
    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* QuestSubsystem = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!QuestSubsystem)
    {
        return;
    }

    const FName Current = QuestSubsystem->GetCurrentChapterId();
    int32 CurrentIndex = 0;
    for (int32 Index = 0; Index < ShireDebugChapters::Count; ++Index)
    {
        if (ShireDebugChapters::ChapterIds[Index] == Current)
        {
            CurrentIndex = Index;
            break;
        }
    }

    DebugStartChapterByIndex(FMath::Max(0, CurrentIndex - 1));
}

void AShirePlayerCharacter::DebugNextChapter()
{
    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* QuestSubsystem = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!QuestSubsystem)
    {
        return;
    }

    const FName Current = QuestSubsystem->GetCurrentChapterId();
    int32 CurrentIndex = 0;
    for (int32 Index = 0; Index < ShireDebugChapters::Count; ++Index)
    {
        if (ShireDebugChapters::ChapterIds[Index] == Current)
        {
            CurrentIndex = Index;
            break;
        }
    }

    DebugStartChapterByIndex(FMath::Min(ShireDebugChapters::Count - 1, CurrentIndex + 1));
}
