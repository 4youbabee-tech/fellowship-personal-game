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
    static const FString CheckpointSlotName(TEXT("ShireJourney_Checkpoint"));
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
    CameraBoom->TargetArmLength = 260.0f;
    CameraBoom->bUsePawnControlRotation = true;
    CameraBoom->bEnableCameraLag = true;
    CameraBoom->CameraLagSpeed = 8.5f;
    CameraBoom->CameraLagMaxDistance = 65.0f;
    CameraBoom->SetRelativeLocation(FVector(0.0f, 0.0f, 52.0f));
    CameraBoom->SocketOffset = FVector(0.0f, 28.0f, 10.0f);

    FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
    FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
    FollowCamera->bUsePawnControlRotation = false;
    FollowCamera->SetFieldOfView(78.0f);

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
    if (!BasicMaterial) return;

    auto ApplyColor = [this, BasicMaterial](UStaticMeshComponent* Component, const FLinearColor& Color)
    {
        if (!Component) return;
        if (UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(BasicMaterial, this))
        {
            MID->SetVectorParameterValue(TEXT("Color"), Color);
            Component->SetMaterial(0, MID);
        }
    };

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
    bool bProductionCharacter = true;

    if (bGandalf)
    {
        bProductionCharacter = TryMesh(PrototypeTorso, TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Torso.SM_Gandalf_Torso")) && bProductionCharacter;
        bProductionCharacter = TryMesh(PrototypeHead, TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Head.SM_Gandalf_Head")) && bProductionCharacter;
        bProductionCharacter = TryMesh(PrototypeHair, TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Hair.SM_Gandalf_Hair")) && bProductionCharacter;
        bProductionCharacter = TryMesh(PrototypeLeftArm, TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Arm.SM_Gandalf_Arm")) && bProductionCharacter;
        TryMesh(PrototypeRightArm, TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Arm.SM_Gandalf_Arm"));
        bProductionCharacter = TryMesh(PrototypeLeftLeg, TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Leg.SM_Gandalf_Leg")) && bProductionCharacter;
        TryMesh(PrototypeRightLeg, TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Leg.SM_Gandalf_Leg"));
        TryMesh(PrototypeLeftFoot, TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Boot.SM_Gandalf_Boot"));
        TryMesh(PrototypeRightFoot, TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Boot.SM_Gandalf_Boot"));
        TryMesh(PrototypeCloak, TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Cloak.SM_Gandalf_Cloak"));
        TryMesh(PrototypeHat, TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Hat.SM_Gandalf_Hat"));
        TryMesh(PrototypeBeard, TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Beard.SM_Gandalf_Beard"));
        TryMesh(PrototypeWeapon, TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Staff.SM_Gandalf_Staff"));
    }
    else
    {
        bProductionCharacter = TryMesh(PrototypeTorso, TEXT("/Game/Production/Characters/Frodo/SM_Frodo_Torso.SM_Frodo_Torso")) && bProductionCharacter;
        bProductionCharacter = TryMesh(PrototypeHead, TEXT("/Game/Production/Characters/Frodo/SM_Frodo_Head.SM_Frodo_Head")) && bProductionCharacter;
        bProductionCharacter = TryMesh(PrototypeHair, TEXT("/Game/Production/Characters/Frodo/SM_Frodo_Hair.SM_Frodo_Hair")) && bProductionCharacter;
        bProductionCharacter = TryMesh(PrototypeLeftArm, TEXT("/Game/Production/Characters/Frodo/SM_Hobbit_Arm.SM_Hobbit_Arm")) && bProductionCharacter;
        TryMesh(PrototypeRightArm, TEXT("/Game/Production/Characters/Frodo/SM_Hobbit_Arm.SM_Hobbit_Arm"));
        bProductionCharacter = TryMesh(PrototypeLeftLeg, TEXT("/Game/Production/Characters/Frodo/SM_Hobbit_Leg.SM_Hobbit_Leg")) && bProductionCharacter;
        TryMesh(PrototypeRightLeg, TEXT("/Game/Production/Characters/Frodo/SM_Hobbit_Leg.SM_Hobbit_Leg"));
        TryMesh(PrototypeLeftFoot, TEXT("/Game/Production/Characters/Frodo/SM_Hobbit_Foot.SM_Hobbit_Foot"));
        TryMesh(PrototypeRightFoot, TEXT("/Game/Production/Characters/Frodo/SM_Hobbit_Foot.SM_Hobbit_Foot"));
        TryMesh(PrototypeCloak, TEXT("/Game/Production/Characters/Frodo/SM_Frodo_Cloak.SM_Frodo_Cloak"));
        TryMesh(PrototypeSatchel, TEXT("/Game/Production/Characters/Frodo/SM_Frodo_Satchel.SM_Frodo_Satchel"));
        TryMesh(PrototypeWeapon, TEXT("/Game/Production/Characters/Frodo/SM_Frodo_Sword.SM_Frodo_Sword"));
    }

    bUsingProductionCharacter = bProductionCharacter;
    UE_LOG(
        LogTemp,
        Display,
        TEXT("CharacterVisual: %s production=%s"),
        *CharacterId.ToString(),
        bUsingProductionCharacter ? TEXT("yes") : TEXT("fallback"));

    GetCapsuleComponent()->SetCapsuleHalfHeight(bGandalf ? 86.0f : 60.0f);
    if (CameraBoom)
    {
        CameraBoom->TargetArmLength = bGandalf ? 300.0f : 260.0f;
        CameraBoom->SetRelativeLocation(FVector(0.0f, 0.0f, bGandalf ? 77.0f : 52.0f));
        CameraBoom->SocketOffset = FVector(0.0f, bGandalf ? 32.0f : 28.0f, 10.0f);
    }

    PrototypeTorsoBaseZ = bGandalf ? 9.0f : -4.0f;
    PrototypeHeadBaseZ = bGandalf ? 69.0f : 39.0f;
    PrototypeHairBaseZ = bGandalf ? 82.0f : 49.0f;

    PrototypeTorso->SetRelativeLocation(FVector(0,0,PrototypeTorsoBaseZ));
    PrototypeHead->SetRelativeLocation(FVector(0,0,PrototypeHeadBaseZ));
    PrototypeHair->SetRelativeLocation(FVector(-2,0,PrototypeHairBaseZ));
    PrototypeLeftArm->SetRelativeLocation(FVector(0,bGandalf ? -26.0f : -23.0f,bGandalf ? 8.0f : -3.0f));
    PrototypeRightArm->SetRelativeLocation(FVector(0,bGandalf ? 26.0f : 23.0f,bGandalf ? 8.0f : -3.0f));
    PrototypeLeftLeg->SetRelativeLocation(FVector(0,-9.5f,bGandalf ? -50.0f : -43.0f));
    PrototypeRightLeg->SetRelativeLocation(FVector(0,9.5f,bGandalf ? -50.0f : -43.0f));
    PrototypeLeftFoot->SetRelativeLocation(FVector(9,-10,bGandalf ? -80.0f : -58.0f));
    PrototypeRightFoot->SetRelativeLocation(FVector(9,10,bGandalf ? -80.0f : -58.0f));

    if (bProductionCharacter)
    {
        PrototypeTorso->SetRelativeScale3D(FVector(1));
        PrototypeHead->SetRelativeScale3D(FVector(1));
        PrototypeHair->SetRelativeScale3D(FVector(1));
        PrototypeLeftArm->SetRelativeScale3D(FVector(1)); PrototypeRightArm->SetRelativeScale3D(FVector(1));
        PrototypeLeftLeg->SetRelativeScale3D(FVector(1)); PrototypeRightLeg->SetRelativeScale3D(FVector(1));
        PrototypeLeftFoot->SetRelativeScale3D(FVector(1)); PrototypeRightFoot->SetRelativeScale3D(FVector(1));
    }
    else
    {
        PrototypeTorso->SetRelativeScale3D(bGandalf ? FVector(0.29f,0.22f,0.52f) : FVector(0.27f,0.20f,0.35f));
        PrototypeHead->SetRelativeScale3D(bGandalf ? FVector(0.205f,0.19f,0.235f) : FVector(0.225f,0.215f,0.235f));
        PrototypeHair->SetRelativeScale3D(bGandalf ? FVector(0.22f,0.21f,0.14f) : FVector(0.235f,0.235f,0.12f));
        PrototypeLeftArm->SetRelativeScale3D(bGandalf ? FVector(0.075f,0.075f,0.46f) : FVector(0.075f,0.075f,0.33f));
        PrototypeRightArm->SetRelativeScale3D(bGandalf ? FVector(0.075f,0.075f,0.46f) : FVector(0.075f,0.075f,0.33f));
        PrototypeLeftLeg->SetRelativeScale3D(bGandalf ? FVector(0.085f,0.085f,0.36f) : FVector(0.095f,0.095f,0.29f));
        PrototypeRightLeg->SetRelativeScale3D(bGandalf ? FVector(0.085f,0.085f,0.36f) : FVector(0.095f,0.095f,0.29f));
        PrototypeLeftFoot->SetRelativeScale3D(bGandalf ? FVector(0.18f,0.105f,0.07f) : FVector(0.23f,0.135f,0.075f));
        PrototypeRightFoot->SetRelativeScale3D(bGandalf ? FVector(0.18f,0.105f,0.07f) : FVector(0.23f,0.135f,0.075f));
    }

    PrototypeCloak->SetRelativeLocation(FVector(-8,0,bGandalf ? -4.0f : -8.0f));
    PrototypeCloak->SetRelativeScale3D(bProductionCharacter ? FVector(1) :
        (bGandalf ? FVector(0.38f,0.33f,0.72f) : FVector(0.30f,0.27f,0.42f)));
    PrototypeHat->SetVisibility(bGandalf,true);
    PrototypeHat->SetRelativeLocation(FVector(-1,0,bProductionCharacter ? 91.0f : 101.0f));
    PrototypeHat->SetRelativeScale3D(bProductionCharacter ? FVector(1) : FVector(0.34f,0.34f,0.48f));
    PrototypeBeard->SetVisibility(bGandalf,true);
    PrototypeBeard->SetRelativeLocation(FVector(bProductionCharacter ? 14.0f : 10.0f,0,bProductionCharacter ? 62.0f : 48.0f));
    PrototypeBeard->SetRelativeRotation(bProductionCharacter ? FRotator::ZeroRotator : FRotator(180,0,0));
    PrototypeBeard->SetRelativeScale3D(bProductionCharacter ? FVector(1) : FVector(0.14f,0.13f,0.28f));

    const float FaceX=bProductionCharacter ? 17.0f : 10.5f;
    const float FaceY=bProductionCharacter ? 6.5f : 5.2f;
    const float FaceZ=PrototypeHeadBaseZ+(bProductionCharacter ? 3.0f : 1.5f);
    PrototypeLeftEye->SetRelativeLocation(FVector(FaceX,-FaceY,FaceZ+2));
    PrototypeRightEye->SetRelativeLocation(FVector(FaceX,FaceY,FaceZ+2));
    PrototypeLeftEye->SetRelativeScale3D(bProductionCharacter ? FVector(0.026f,0.020f,0.035f) : FVector(0.035f,0.025f,0.045f));
    PrototypeRightEye->SetRelativeScale3D(bProductionCharacter ? FVector(0.026f,0.020f,0.035f) : FVector(0.035f,0.025f,0.045f));
    PrototypeMouth->SetRelativeLocation(FVector(FaceX+0.5f,0,FaceZ-6));
    PrototypeMouth->SetRelativeScale3D(bProductionCharacter ? FVector(0.012f,0.050f,0.010f) : FVector(0.018f,0.065f,0.012f));

    PrototypeSatchel->SetVisibility(!bGandalf,true);
    PrototypeSatchel->SetRelativeLocation(FVector(-2,bProductionCharacter ? 19.0f : 22.0f,-5));
    PrototypeSatchel->SetRelativeRotation(FRotator(0,12,8));
    PrototypeSatchel->SetRelativeScale3D(bProductionCharacter ? FVector(1) : FVector(0.13f,0.06f,0.15f));

    const FLinearColor Skin=bGandalf ? FLinearColor(0.72f,0.54f,0.40f) : FLinearColor(0.78f,0.57f,0.39f);
    ApplyColor(PrototypeTorso,bGandalf ? FLinearColor(0.28f,0.29f,0.27f) : FLinearColor(0.18f,0.31f,0.135f));
    ApplyColor(PrototypeHead,Skin);
    ApplyColor(PrototypeHair,bGandalf ? FLinearColor(0.69f,0.68f,0.63f) : FLinearColor(0.105f,0.045f,0.020f));
    ApplyColor(PrototypeLeftArm,bGandalf ? FLinearColor(0.25f,0.26f,0.24f) : FLinearColor(0.20f,0.35f,0.15f));
    ApplyColor(PrototypeRightArm,bGandalf ? FLinearColor(0.25f,0.26f,0.24f) : FLinearColor(0.20f,0.35f,0.15f));
    ApplyColor(PrototypeLeftLeg,bGandalf ? FLinearColor(0.17f,0.18f,0.17f) : FLinearColor(0.27f,0.17f,0.075f));
    ApplyColor(PrototypeRightLeg,bGandalf ? FLinearColor(0.17f,0.18f,0.17f) : FLinearColor(0.27f,0.17f,0.075f));
    ApplyColor(PrototypeLeftFoot,bGandalf ? FLinearColor(0.095f,0.09f,0.085f) : FLinearColor(0.22f,0.105f,0.04f));
    ApplyColor(PrototypeRightFoot,bGandalf ? FLinearColor(0.095f,0.09f,0.085f) : FLinearColor(0.22f,0.105f,0.04f));
    ApplyColor(PrototypeCloak,bGandalf ? FLinearColor(0.24f,0.25f,0.235f) : FLinearColor(0.16f,0.24f,0.105f));
    ApplyColor(PrototypeHat,FLinearColor(0.245f,0.25f,0.235f));
    ApplyColor(PrototypeBeard,FLinearColor(0.68f,0.67f,0.62f));
    ApplyColor(PrototypeLeftEye,FLinearColor(0.035f,0.028f,0.020f));
    ApplyColor(PrototypeRightEye,FLinearColor(0.035f,0.028f,0.020f));
    ApplyColor(PrototypeMouth,FLinearColor(0.23f,0.055f,0.045f));
    ApplyColor(PrototypeSatchel,FLinearColor(0.26f,0.13f,0.045f));

    const bool bCombatAvailable=IsCombatAvailable();
    PrototypeWeapon->SetVisibility(bGandalf||bCombatAvailable,true);
    PrototypeWeapon->SetRelativeLocation(bGandalf ? FVector(4,34,0) : FVector(8,29,-4));
    PrototypeWeapon->SetRelativeScale3D(bProductionCharacter ? FVector(1) :
        (bGandalf ? FVector(0.055f,0.055f,0.92f) : FVector(0.045f,0.045f,0.48f)));
    PrototypeWeapon->SetRelativeRotation(bGandalf ? FRotator::ZeroRotator : FRotator(-12,0,8));
    ApplyColor(PrototypeWeapon,bGandalf ? FLinearColor(0.22f,0.13f,0.055f) : FLinearColor(0.48f,0.50f,0.52f));
}

void AShirePlayerCharacter::UpdatePrototypeAnimation(float DeltaSeconds)
{
    UCharacterMovementComponent* Movement = GetCharacterMovement();
    if (!Movement)
    {
        return;
    }

    const FVector Velocity = GetVelocity();
    const float Speed = Velocity.Size2D();
    const bool bMoving = Speed > 5.0f && !bCinematicInputLocked;
    const bool bCrouching = bIsCrouched;
    const bool bFalling = Movement->IsFalling();
    const bool bSprinting = bMoving && bSprintRequested && !bCrouching &&
        Speed > WalkSpeed * 1.05f;

    PrototypeIdlePhase += DeltaSeconds * (bPrototypeIsGandalf ? 1.05f : 1.35f);

    const FVector LocalVelocity = GetActorTransform().InverseTransformVectorNoScale(Velocity);
    const float SideRatio = FMath::Clamp(
        LocalVelocity.Y / FMath::Max(1.0f, SprintSpeed), -1.0f, 1.0f);

    float Swing = 0.0f;
    float Bob = 0.0f;
    float StepLift = 0.0f;

    if (bMoving && !bFalling)
    {
        const float SpeedRatio = FMath::Clamp(
            Speed / FMath::Max(1.0f, WalkSpeed), 0.45f, 1.85f);
        const float GaitRate = bSprinting ? 10.5f : 7.8f;
        const float GaitAmplitude = bPrototypeIsGandalf
            ? (bSprinting ? 30.0f : 22.0f)
            : (bSprinting ? 38.0f : 29.0f);

        PrototypeWalkPhase += DeltaSeconds * GaitRate * SpeedRatio;
        const float StepSin = FMath::Sin(PrototypeWalkPhase);
        Swing = StepSin * GaitAmplitude;
        Bob = FMath::Abs(FMath::Sin(PrototypeWalkPhase * 2.0f)) *
            (bSprinting ? 2.4f : 1.4f);
        StepLift = FMath::Max(0.0f, StepSin) * (bSprinting ? 3.0f : 1.6f);
    }

    const float IdleBreath = (!bMoving && !bFalling)
        ? FMath::Sin(PrototypeIdlePhase) * (bPrototypeIsGandalf ? 0.55f : 0.75f)
        : 0.0f;
    const float CrouchDrop = bCrouching ? (bPrototypeIsGandalf ? 11.0f : 8.0f) : 0.0f;
    const float SprintLean = bSprinting ? (bPrototypeIsGandalf ? -4.0f : -7.0f) : 0.0f;
    const float SideLean = -SideRatio * 5.0f;
    const float BlendSpeed = bSprinting ? 14.0f : 10.0f;

    float LeftArmPitch = Swing;
    float RightArmPitch = -Swing;
    float LeftLegPitch = -Swing * 0.66f;
    float RightLegPitch = Swing * 0.66f;

    if (bCrouching)
    {
        LeftArmPitch *= 0.35f;
        RightArmPitch *= 0.35f;
        LeftLegPitch = 18.0f + LeftLegPitch * 0.22f;
        RightLegPitch = 18.0f + RightLegPitch * 0.22f;
    }
    else if (bFalling)
    {
        LeftArmPitch = bPrototypeIsGandalf ? -10.0f : -18.0f;
        RightArmPitch = bPrototypeIsGandalf ? -18.0f : -28.0f;
        LeftLegPitch = 12.0f;
        RightLegPitch = -10.0f;
    }

    if (AttackVisualRemaining > 0.0f)
    {
        RightArmPitch = bPrototypeIsGandalf ? -68.0f : -88.0f;
    }

    if (PrototypeLeftArm)
    {
        PrototypeLeftArm->SetRelativeRotation(FMath::RInterpTo(
            PrototypeLeftArm->GetRelativeRotation(),
            FRotator(LeftArmPitch, 0.0f, SideLean * 0.35f),
            DeltaSeconds,
            BlendSpeed));
    }
    if (PrototypeRightArm)
    {
        PrototypeRightArm->SetRelativeRotation(FMath::RInterpTo(
            PrototypeRightArm->GetRelativeRotation(),
            FRotator(RightArmPitch, 0.0f, SideLean * 0.35f),
            DeltaSeconds,
            BlendSpeed));
    }
    if (PrototypeLeftLeg)
    {
        PrototypeLeftLeg->SetRelativeRotation(FMath::RInterpTo(
            PrototypeLeftLeg->GetRelativeRotation(),
            FRotator(LeftLegPitch, 0.0f, 0.0f),
            DeltaSeconds,
            BlendSpeed));
    }
    if (PrototypeRightLeg)
    {
        PrototypeRightLeg->SetRelativeRotation(FMath::RInterpTo(
            PrototypeRightLeg->GetRelativeRotation(),
            FRotator(RightLegPitch, 0.0f, 0.0f),
            DeltaSeconds,
            BlendSpeed));
    }

    const float MotionZ = Bob + IdleBreath - CrouchDrop;
    if (PrototypeTorso)
    {
        PrototypeTorso->SetRelativeLocation(FMath::VInterpTo(
            PrototypeTorso->GetRelativeLocation(),
            FVector(0.0f, 0.0f, PrototypeTorsoBaseZ + MotionZ),
            DeltaSeconds,
            12.0f));
        PrototypeTorso->SetRelativeRotation(FMath::RInterpTo(
            PrototypeTorso->GetRelativeRotation(),
            FRotator(SprintLean, 0.0f, SideLean),
            DeltaSeconds,
            8.0f));
    }
    if (PrototypeHead)
    {
        PrototypeHead->SetRelativeLocation(FMath::VInterpTo(
            PrototypeHead->GetRelativeLocation(),
            FVector(0.0f, 0.0f, PrototypeHeadBaseZ + MotionZ),
            DeltaSeconds,
            12.0f));
        PrototypeHead->SetRelativeRotation(FMath::RInterpTo(
            PrototypeHead->GetRelativeRotation(),
            FRotator(
                bSprinting ? 3.0f : 0.0f,
                SideRatio * 3.0f + FMath::Sin(PrototypeIdlePhase * 0.55f) * 1.2f,
                -SideLean * 0.3f),
            DeltaSeconds,
            5.0f));
    }
    if (PrototypeHair)
    {
        PrototypeHair->SetRelativeLocation(FMath::VInterpTo(
            PrototypeHair->GetRelativeLocation(),
            FVector(-2.0f, 0.0f, PrototypeHairBaseZ + MotionZ),
            DeltaSeconds,
            12.0f));
    }

    const float FootBaseZ = bPrototypeIsGandalf ? -80.0f : -58.0f;
    const float LeftLift = bMoving && !bFalling
        ? FMath::Max(0.0f, FMath::Sin(PrototypeWalkPhase)) * (bSprinting ? 3.0f : 1.7f)
        : 0.0f;
    const float RightLift = bMoving && !bFalling
        ? FMath::Max(0.0f, -FMath::Sin(PrototypeWalkPhase)) * (bSprinting ? 3.0f : 1.7f)
        : 0.0f;
    const float FootCrouchDrop = bCrouching ? 3.0f : 0.0f;

    if (PrototypeLeftFoot)
    {
        PrototypeLeftFoot->SetRelativeLocation(FMath::VInterpTo(
            PrototypeLeftFoot->GetRelativeLocation(),
            FVector(9.0f, -10.0f, FootBaseZ + LeftLift - FootCrouchDrop),
            DeltaSeconds,
            14.0f));
        PrototypeLeftFoot->SetRelativeRotation(FMath::RInterpTo(
            PrototypeLeftFoot->GetRelativeRotation(),
            FRotator(-LeftLegPitch * 0.22f, 0.0f, 0.0f),
            DeltaSeconds,
            12.0f));
    }
    if (PrototypeRightFoot)
    {
        PrototypeRightFoot->SetRelativeLocation(FMath::VInterpTo(
            PrototypeRightFoot->GetRelativeLocation(),
            FVector(9.0f, 10.0f, FootBaseZ + RightLift - FootCrouchDrop),
            DeltaSeconds,
            14.0f));
        PrototypeRightFoot->SetRelativeRotation(FMath::RInterpTo(
            PrototypeRightFoot->GetRelativeRotation(),
            FRotator(-RightLegPitch * 0.22f, 0.0f, 0.0f),
            DeltaSeconds,
            12.0f));
    }

    if (PrototypeCloak)
    {
        const float CloakPitch = bFalling
            ? -12.0f
            : (bMoving ? -4.0f - FMath::Abs(Swing) * 0.09f - (bSprinting ? 4.0f : 0.0f) : -2.0f);
        const float CloakYaw = bMoving ? SideRatio * 5.0f : FMath::Sin(PrototypeIdlePhase * 0.45f) * 1.0f;
        PrototypeCloak->SetRelativeRotation(FMath::RInterpTo(
            PrototypeCloak->GetRelativeRotation(),
            FRotator(CloakPitch, CloakYaw, -SideLean * 0.45f),
            DeltaSeconds,
            5.5f));
    }

    if (PrototypeWeapon)
    {
        const FVector WeaponBaseLocation = bPrototypeIsGandalf
            ? FVector(4.0f, 34.0f, 0.0f)
            : FVector(8.0f, 29.0f, -4.0f);
        FRotator WeaponTarget = bPrototypeIsGandalf
            ? FRotator::ZeroRotator
            : FRotator(-12.0f, 0.0f, 8.0f);

        if (AttackVisualRemaining > 0.0f)
        {
            WeaponTarget = bPrototypeIsGandalf
                ? FRotator(-42.0f, 0.0f, 18.0f)
                : FRotator(-78.0f, 0.0f, 32.0f);
        }
        else if (bSprinting)
        {
            WeaponTarget += bPrototypeIsGandalf
                ? FRotator(-5.0f, 0.0f, 4.0f)
                : FRotator(7.0f, 0.0f, -5.0f);
        }

        PrototypeWeapon->SetRelativeLocation(FMath::VInterpTo(
            PrototypeWeapon->GetRelativeLocation(),
            WeaponBaseLocation + FVector(0.0f, 0.0f, MotionZ * 0.35f),
            DeltaSeconds,
            12.0f));
        PrototypeWeapon->SetRelativeRotation(FMath::RInterpTo(
            PrototypeWeapon->GetRelativeRotation(),
            WeaponTarget,
            DeltaSeconds,
            AttackVisualRemaining > 0.0f ? 18.0f : 9.0f));
    }

    if (PrototypeSatchel && !bPrototypeIsGandalf)
    {
        const float SatchelY = bUsingProductionCharacter ? 19.0f : 22.0f;
        PrototypeSatchel->SetRelativeLocation(FMath::VInterpTo(
            PrototypeSatchel->GetRelativeLocation(),
            FVector(-2.0f, SatchelY, -5.0f + MotionZ * 0.45f),
            DeltaSeconds,
            10.0f));
        PrototypeSatchel->SetRelativeRotation(FMath::RInterpTo(
            PrototypeSatchel->GetRelativeRotation(),
            FRotator(0.0f, 12.0f + SideRatio * 3.0f, 8.0f + Swing * 0.08f),
            DeltaSeconds,
            7.0f));
    }

    const float FaceX = bUsingProductionCharacter ? 17.0f : 10.5f;
    const float FaceY = bUsingProductionCharacter ? 6.5f : 5.2f;
    const float FaceZ = PrototypeHeadBaseZ + (bUsingProductionCharacter ? 3.0f : 1.5f) + MotionZ;

    if (PrototypeLeftEye)
    {
        PrototypeLeftEye->SetRelativeLocation(FVector(FaceX, -FaceY, FaceZ + 2.0f));
    }
    if (PrototypeRightEye)
    {
        PrototypeRightEye->SetRelativeLocation(FVector(FaceX, FaceY, FaceZ + 2.0f));
    }
    if (PrototypeMouth)
    {
        PrototypeMouth->SetRelativeLocation(FVector(FaceX + 0.5f, 0.0f, FaceZ - 6.0f));
    }

    if (bPrototypeIsGandalf)
    {
        if (PrototypeHat)
        {
            const float HatBaseZ = bUsingProductionCharacter ? 91.0f : 101.0f;
            PrototypeHat->SetRelativeLocation(FVector(-1.0f, 0.0f, HatBaseZ + MotionZ));
            PrototypeHat->SetRelativeRotation(FMath::RInterpTo(
                PrototypeHat->GetRelativeRotation(),
                FRotator(0.0f, SideRatio * 2.0f, -SideLean * 0.25f),
                DeltaSeconds,
                5.0f));
        }
        if (PrototypeBeard)
        {
            const float BeardX = bUsingProductionCharacter ? 14.0f : 10.0f;
            const float BeardZ = bUsingProductionCharacter ? 62.0f : 48.0f;
            const FRotator BeardBaseRotation = bUsingProductionCharacter
                ? FRotator::ZeroRotator
                : FRotator(180.0f, 0.0f, 0.0f);
            PrototypeBeard->SetRelativeLocation(FVector(BeardX, 0.0f, BeardZ + MotionZ));
            PrototypeBeard->SetRelativeRotation(FMath::RInterpTo(
                PrototypeBeard->GetRelativeRotation(),
                BeardBaseRotation + FRotator(bMoving ? Swing * 0.04f : 0.0f, 0.0f, SideRatio * 2.0f),
                DeltaSeconds,
                5.0f));
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

            if (Quests->GetCurrentRouteId() == TEXT("FrodoMain") &&
                Quests->GetCurrentChapterId() == TEXT("P1C01") &&
                !UGameplayStatics::DoesSaveGameExist(
                    ShireSaveConstants::CheckpointSlotName,
                    ShireSaveConstants::UserIndex))
            {
                SaveAutomaticCheckpoint(TEXT("WC_P1C01_START"), false);
            }
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
        bSprintRequested = false;
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
        bSprintRequested = true;
        GetCharacterMovement()->MaxWalkSpeed = SprintSpeed;
    }
}

void AShirePlayerCharacter::StopSprint()
{
    bSprintRequested = false;
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

    CurrentHealth = FMath::Max(0.0f, CurrentHealth - DamageAmount);

    if (CurrentHealth <= 0.0f)
    {
        if (RestoreAutomaticCheckpoint(false))
        {
            if (APlayerController* PC = Cast<APlayerController>(Controller))
            {
                if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
                {
                    HUD->ShowAlert(
                        FText::FromString(TEXT("You fell. Restoring the last safe checkpoint.")),
                        2.4f);
                }
            }
            return DamageAmount;
        }

        CurrentHealth = 1.0f;
    }

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

UShireSaveGame* AShirePlayerCharacter::CreateSaveSnapshot(
    FName CheckpointId,
    bool bCheckpointSnapshot) const
{
    UShireSaveGame* Save = Cast<UShireSaveGame>(
        UGameplayStatics::CreateSaveGameObject(UShireSaveGame::StaticClass()));
    if (!Save)
    {
        return nullptr;
    }

    Save->PlayerLocation = GetActorLocation();
    Save->PlayerRotation = GetActorRotation();
    Save->CheckpointId = CheckpointId;
    Save->PlayerHealth = bCheckpointSnapshot ? MaxHealth : CurrentHealth;

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
        }
    }

    return Save;
}

bool AShirePlayerCharacter::RestoreSaveSnapshot(
    UShireSaveGame* Save,
    const FText& SuccessMessage)
{
    if (!Save)
    {
        return false;
    }

    bool bApplyExactSavedTransform = true;
    if (UGameInstance* GI = GetGameInstance())
    {
        if (UShireQuestSubsystem* QuestSubsystem = GI->GetSubsystem<UShireQuestSubsystem>())
        {
            const FName SavedChapterId =
                Save->CurrentChapterId == NAME_None ? FName(TEXT("P1C01")) : Save->CurrentChapterId;

            QuestSubsystem->RestoreQuestState(
                Save->QuestStages,
                Save->ActiveQuestId,
                Save->CurrentChapterId,
                Save->CompletedStoryBeats,
                Save->CurrentRouteId,
                Save->CurrentEpisodeId,
                Save->PlayableCharacterId,
                Save->RouteProgress);

            bApplyExactSavedTransform =
                QuestSubsystem->GetCurrentChapterId() == SavedChapterId;
        }
    }

    CurrentHealth = FMath::Clamp(Save->PlayerHealth, 1.0f, MaxHealth);

    if (bApplyExactSavedTransform)
    {
        SetActorLocationAndRotation(
            Save->PlayerLocation,
            Save->PlayerRotation,
            false,
            nullptr,
            ETeleportType::TeleportPhysics);
    }

    GetCharacterMovement()->StopMovementImmediately();
    ApplyPrototypeStyle();

    if (!SuccessMessage.IsEmpty())
    {
        if (APlayerController* PC = Cast<APlayerController>(Controller))
        {
            if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
            {
                HUD->ShowAlert(SuccessMessage, 1.8f);
            }
        }
    }

    return true;
}

bool AShirePlayerCharacter::SaveAutomaticCheckpoint(FName CheckpointId, bool bShowHUD)
{
    if (CheckpointId == NAME_None)
    {
        return false;
    }

    UShireSaveGame* Save = CreateSaveSnapshot(CheckpointId, true);
    if (!Save)
    {
        return false;
    }

    const bool bSaved = UGameplayStatics::SaveGameToSlot(
        Save,
        ShireSaveConstants::CheckpointSlotName,
        ShireSaveConstants::UserIndex);

    if (bSaved)
    {
        CurrentHealth = MaxHealth;
    }

    if (bShowHUD)
    {
        if (APlayerController* PC = Cast<APlayerController>(Controller))
        {
            if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
            {
                HUD->ShowAlert(
                    FText::FromString(bSaved ? TEXT("Checkpoint reached.") : TEXT("Checkpoint failed.")),
                    1.4f);
            }
        }
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("SafeCheckpoint: id=%s saved=%s"),
        *CheckpointId.ToString(),
        bSaved ? TEXT("yes") : TEXT("no"));

    return bSaved;
}

bool AShirePlayerCharacter::RestoreAutomaticCheckpoint(bool bShowHUD)
{
    if (!UGameplayStatics::DoesSaveGameExist(
        ShireSaveConstants::CheckpointSlotName,
        ShireSaveConstants::UserIndex))
    {
        return false;
    }

    UShireSaveGame* Save = Cast<UShireSaveGame>(
        UGameplayStatics::LoadGameFromSlot(
            ShireSaveConstants::CheckpointSlotName,
            ShireSaveConstants::UserIndex));
    if (!Save)
    {
        return false;
    }

    const FText Message = bShowHUD
        ? FText::FromString(TEXT("Safe checkpoint restored."))
        : FText::GetEmpty();

    const bool bRestored = RestoreSaveSnapshot(Save, Message);
    if (bRestored)
    {
        CurrentHealth = MaxHealth;
        UE_LOG(
            LogTemp,
            Display,
            TEXT("SafeCheckpoint: restored id=%s"),
            *Save->CheckpointId.ToString());
    }
    return bRestored;
}

void AShirePlayerCharacter::QuickSave()
{
    UShireSaveGame* Save = CreateSaveSnapshot(NAME_None, false);
    const bool bSaved = Save && UGameplayStatics::SaveGameToSlot(
        Save,
        ShireSaveConstants::SlotName,
        ShireSaveConstants::UserIndex);

    if (APlayerController* PC = Cast<APlayerController>(Controller))
    {
        if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
        {
            HUD->ShowAlert(
                FText::FromString(bSaved ? TEXT("Journey saved.") : TEXT("Save failed.")),
                1.8f);
        }
    }
}

void AShirePlayerCharacter::QuickLoad()
{
    if (!UGameplayStatics::DoesSaveGameExist(
        ShireSaveConstants::SlotName,
        ShireSaveConstants::UserIndex))
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

    UShireSaveGame* Save = Cast<UShireSaveGame>(
        UGameplayStatics::LoadGameFromSlot(
            ShireSaveConstants::SlotName,
            ShireSaveConstants::UserIndex));

    RestoreSaveSnapshot(
        Save,
        FText::FromString(TEXT("Journey restored.")));
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
