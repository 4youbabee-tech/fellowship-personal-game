#include "ShirePlayerCharacter.h"
#include "ShireInteractable.h"
#include "ShireQuestSubsystem.h"
#include "ShireSaveGame.h"
#include "ShireHUD.h"
#include "ShireStoryPresentationSubsystem.h"
#include "FellowshipEnemyPrototype.h"
#include "Animation/AnimInstance.h"
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
#include "Engine/SkeletalMesh.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "Misc/PackageName.h"
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

bool AShirePlayerCharacter::TryApplyProductionRig(const FString& RigFolder)
{
    if (RigFolder.IsEmpty() || !GetMesh())
    {
        return false;
    }

    const FString SkeletalPackagePath = FString::Printf(
        TEXT("/Game/Production/Characters/Rigs/%s/SK_%s"),
        *RigFolder,
        *RigFolder);
    const FString AnimPackagePath = FString::Printf(
        TEXT("/Game/Production/Characters/Rigs/%s/ABP_%s_Locomotion"),
        *RigFolder,
        *RigFolder);

    if (!FPackageName::DoesPackageExist(SkeletalPackagePath) ||
        !FPackageName::DoesPackageExist(AnimPackagePath))
    {
        GetMesh()->SetVisibility(false, true);
        return false;
    }

    const FString SkeletalPath = FString::Printf(TEXT("%s.SK_%s"), *SkeletalPackagePath, *RigFolder);
    const FString AnimClassPath = FString::Printf(
        TEXT("%s.ABP_%s_Locomotion_C"),
        *AnimPackagePath,
        *RigFolder);

    USkeletalMesh* SkeletalMesh = LoadObject<USkeletalMesh>(nullptr, *SkeletalPath);
    UClass* AnimClass = LoadClass<UAnimInstance>(nullptr, *AnimClassPath);
    if (!SkeletalMesh || !AnimClass)
    {
        GetMesh()->SetVisibility(false, true);
        return false;
    }

    GetMesh()->SetSkeletalMesh(SkeletalMesh);
    GetMesh()->SetAnimInstanceClass(AnimClass);
    GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    GetMesh()->SetVisibility(true, true);

    UStaticMeshComponent* ModularPieces[] = {
        PrototypeTorso, PrototypeHead, PrototypeHair,
        PrototypeLeftArm, PrototypeRightArm, PrototypeLeftLeg, PrototypeRightLeg,
        PrototypeLeftFoot, PrototypeRightFoot, PrototypeWeapon, PrototypeCloak,
        PrototypeHat, PrototypeBeard, PrototypeLeftEye, PrototypeRightEye,
        PrototypeMouth, PrototypeSatchel
    };
    for (UStaticMeshComponent* Piece : ModularPieces)
    {
        if (Piece)
        {
            Piece->SetVisibility(false, true);
        }
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("CharacterVisual: skeletal production rig active id=%s"),
        *RigFolder);
    return true;
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
        if (UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(BasicMaterial, this))
        {
            MID->SetVectorParameterValue(TEXT("Color"), Color);
            Component->SetMaterial(0, MID);
        }
    };

    auto TryMesh = [](UStaticMeshComponent* Component, const TCHAR* AssetPath) -> bool
    {
        if (!Component)
        {
            return false;
        }
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

    const TArray<FName> SupportedPlayableIds = {
        TEXT("Frodo"), TEXT("Gandalf"), TEXT("Sam"), TEXT("Merry"), TEXT("Pippin"),
        TEXT("Aragorn"), TEXT("Boromir"), TEXT("Legolas"), TEXT("Gimli"), TEXT("Arwen")
    };
    FName VisualId = CharacterId;
    if (!SupportedPlayableIds.Contains(VisualId))
    {
        UE_LOG(
            LogTemp,
            Warning,
            TEXT("CharacterVisual: unsupported playable id=%s; using Frodo fallback"),
            *CharacterId.ToString());
        VisualId = TEXT("Frodo");
    }

    const bool bFrodo = VisualId == TEXT("Frodo");
    const bool bGandalf = VisualId == TEXT("Gandalf");
    const bool bSam = VisualId == TEXT("Sam");
    const bool bMerry = VisualId == TEXT("Merry");
    const bool bPippin = VisualId == TEXT("Pippin");
    const bool bAragorn = VisualId == TEXT("Aragorn");
    const bool bBoromir = VisualId == TEXT("Boromir");
    const bool bLegolas = VisualId == TEXT("Legolas");
    const bool bGimli = VisualId == TEXT("Gimli");
    const bool bArwen = VisualId == TEXT("Arwen");

    const bool bHobbit = bFrodo || bSam || bMerry || bPippin;
    const bool bDwarf = bGimli;
    const bool bElf = bLegolas || bArwen;
    const bool bWizard = bGandalf;
    const bool bTall = bWizard || bElf || bAragorn || bBoromir;

    bPrototypeIsGandalf = bGandalf;
    PrototypeMotionProfile = bHobbit ? FName(TEXT("HOBBIT"))
        : (bDwarf ? FName(TEXT("DWARF"))
        : (bElf ? FName(TEXT("ELF")) : FName(TEXT("TALL"))));

    PrototypeHat->SetVisibility(false, true);
    PrototypeBeard->SetVisibility(false, true);
    PrototypeCloak->SetVisibility(false, true);
    PrototypeSatchel->SetVisibility(false, true);
    PrototypeWeapon->SetVisibility(false, true);

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
    else if (bFrodo)
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
    else
    {
        const FString Folder = VisualId.ToString();
        const FString TorsoPath = FString::Printf(
            TEXT("/Game/Production/Characters/%s/SM_%s_Torso.SM_%s_Torso"),
            *Folder, *Folder, *Folder);
        const FString HeadPath = FString::Printf(
            TEXT("/Game/Production/Characters/%s/SM_%s_Head.SM_%s_Head"),
            *Folder, *Folder, *Folder);
        const FString HairPath = FString::Printf(
            TEXT("/Game/Production/Characters/%s/SM_%s_Hair.SM_%s_Hair"),
            *Folder, *Folder, *Folder);

        const TCHAR* ArmPath = bHobbit
            ? TEXT("/Game/Production/Characters/Hobbit/SM_Hobbit_Arm.SM_Hobbit_Arm")
            : (bDwarf
                ? TEXT("/Game/Production/Characters/Common/SM_Dwarf_Arm.SM_Dwarf_Arm")
                : TEXT("/Game/Production/Characters/Common/SM_Human_Arm.SM_Human_Arm"));
        const TCHAR* LegPath = bHobbit
            ? TEXT("/Game/Production/Characters/Hobbit/SM_Hobbit_Leg.SM_Hobbit_Leg")
            : (bDwarf
                ? TEXT("/Game/Production/Characters/Common/SM_Dwarf_Leg.SM_Dwarf_Leg")
                : TEXT("/Game/Production/Characters/Common/SM_Human_Leg.SM_Human_Leg"));
        const TCHAR* FootPath = bHobbit
            ? TEXT("/Game/Production/Characters/Hobbit/SM_Hobbit_Foot.SM_Hobbit_Foot")
            : TEXT("/Game/Production/Characters/Common/SM_Human_Boot.SM_Human_Boot");

        bProductionCharacter = TryMesh(PrototypeTorso, *TorsoPath) && bProductionCharacter;
        bProductionCharacter = TryMesh(PrototypeHead, *HeadPath) && bProductionCharacter;
        bProductionCharacter = TryMesh(PrototypeHair, *HairPath) && bProductionCharacter;
        bProductionCharacter = TryMesh(PrototypeLeftArm, ArmPath) && bProductionCharacter;
        TryMesh(PrototypeRightArm, ArmPath);
        bProductionCharacter = TryMesh(PrototypeLeftLeg, LegPath) && bProductionCharacter;
        TryMesh(PrototypeRightLeg, LegPath);
        TryMesh(PrototypeLeftFoot, FootPath);
        TryMesh(PrototypeRightFoot, FootPath);
    }

    const bool bNeedsCloak = bFrodo || bGandalf || bAragorn || bMerry || bPippin;
    if (bNeedsCloak && !bFrodo && !bGandalf)
    {
        TryMesh(PrototypeCloak, TEXT("/Game/Production/Characters/Common/SM_ProductionCloak.SM_ProductionCloak"));
    }

    if (bAragorn || bBoromir)
    {
        TryMesh(PrototypeWeapon, TEXT("/Game/Production/Characters/Common/SM_ProductionSword.SM_ProductionSword"));
    }
    else if (bLegolas)
    {
        TryMesh(PrototypeWeapon, TEXT("/Game/Production/Characters/Common/SM_ProductionBow.SM_ProductionBow"));
    }
    else if (bGimli)
    {
        TryMesh(PrototypeWeapon, TEXT("/Game/Production/Characters/Common/SM_ProductionAxe.SM_ProductionAxe"));
        TryMesh(PrototypeBeard, TEXT("/Game/Production/Characters/Common/SM_Dwarf_Beard.SM_Dwarf_Beard"));
    }
    if (bBoromir)
    {
        TryMesh(PrototypeSatchel, TEXT("/Game/Production/Characters/Common/SM_ProductionShield.SM_ProductionShield"));
    }

    bUsingProductionCharacter = bProductionCharacter;
    UE_LOG(
        LogTemp,
        Display,
        TEXT("CharacterVisual: requested=%s visual=%s profile=%s productionFoundation=%s"),
        *CharacterId.ToString(),
        *VisualId.ToString(),
        *PrototypeMotionProfile.ToString(),
        bUsingProductionCharacter ? TEXT("yes") : TEXT("fallback"));

    const float CapsuleHalfHeight = bHobbit ? 60.0f : (bDwarf ? 70.0f : (bWizard ? 86.0f : 88.0f));
    const float CameraLength = bHobbit ? 260.0f : (bDwarf ? 280.0f : 300.0f);
    const float CameraZ = bHobbit ? 52.0f : (bDwarf ? 62.0f : 77.0f);
    GetCapsuleComponent()->SetCapsuleHalfHeight(CapsuleHalfHeight);
    if (CameraBoom)
    {
        CameraBoom->TargetArmLength = CameraLength;
        CameraBoom->SetRelativeLocation(FVector(0.0f, 0.0f, CameraZ));
        CameraBoom->SocketOffset = FVector(0.0f, bHobbit ? 28.0f : 32.0f, 10.0f);
    }

    PrototypeTorsoBaseZ = bHobbit ? -4.0f : (bDwarf ? 1.0f : 9.0f);
    PrototypeHeadBaseZ = bHobbit ? 39.0f : (bDwarf ? 51.0f : 69.0f);
    PrototypeHairBaseZ = bHobbit ? 49.0f : (bDwarf ? 61.0f : 82.0f);
    const float ArmSide = bHobbit ? 23.0f : (bDwarf ? 25.0f : 26.0f);
    const float ArmZ = bHobbit ? -3.0f : (bDwarf ? 2.0f : 8.0f);
    const float LegZ = bHobbit ? -43.0f : (bDwarf ? -48.0f : -50.0f);
    const float FootZ = bHobbit ? -58.0f : (bDwarf ? -68.0f : -80.0f);

    PrototypeTorso->SetRelativeLocation(FVector(0, 0, PrototypeTorsoBaseZ));
    PrototypeHead->SetRelativeLocation(FVector(0, 0, PrototypeHeadBaseZ));
    PrototypeHair->SetRelativeLocation(FVector(-2, 0, PrototypeHairBaseZ));
    PrototypeLeftArm->SetRelativeLocation(FVector(0, -ArmSide, ArmZ));
    PrototypeRightArm->SetRelativeLocation(FVector(0, ArmSide, ArmZ));
    PrototypeLeftLeg->SetRelativeLocation(FVector(0, -9.5f, LegZ));
    PrototypeRightLeg->SetRelativeLocation(FVector(0, 9.5f, LegZ));
    PrototypeLeftFoot->SetRelativeLocation(FVector(9, -10, FootZ));
    PrototypeRightFoot->SetRelativeLocation(FVector(9, 10, FootZ));

    if (bProductionCharacter)
    {
        PrototypeTorso->SetRelativeScale3D(FVector(1));
        PrototypeHead->SetRelativeScale3D(FVector(1));
        PrototypeHair->SetRelativeScale3D(FVector(1));
        PrototypeLeftArm->SetRelativeScale3D(FVector(1));
        PrototypeRightArm->SetRelativeScale3D(FVector(1));
        PrototypeLeftLeg->SetRelativeScale3D(FVector(1));
        PrototypeRightLeg->SetRelativeScale3D(FVector(1));
        PrototypeLeftFoot->SetRelativeScale3D(FVector(1));
        PrototypeRightFoot->SetRelativeScale3D(FVector(1));
    }
    else
    {
        const FVector TorsoScale = bHobbit ? FVector(0.27f, 0.20f, 0.35f)
            : (bDwarf ? FVector(0.31f, 0.27f, 0.42f) : FVector(0.29f, 0.22f, 0.52f));
        const FVector HeadScale = bHobbit ? FVector(0.225f, 0.215f, 0.235f)
            : (bDwarf ? FVector(0.23f, 0.22f, 0.24f) : FVector(0.205f, 0.19f, 0.235f));
        const FVector HairScale = bHobbit ? FVector(0.235f, 0.235f, 0.12f)
            : (bDwarf ? FVector(0.24f, 0.23f, 0.13f) : FVector(0.22f, 0.21f, 0.14f));
        PrototypeTorso->SetRelativeScale3D(TorsoScale);
        PrototypeHead->SetRelativeScale3D(HeadScale);
        PrototypeHair->SetRelativeScale3D(HairScale);
        const FVector ArmScale = bHobbit ? FVector(0.075f, 0.075f, 0.33f)
            : (bDwarf ? FVector(0.085f, 0.085f, 0.36f) : FVector(0.075f, 0.075f, 0.46f));
        const FVector LegScale = bHobbit ? FVector(0.095f, 0.095f, 0.29f)
            : (bDwarf ? FVector(0.105f, 0.105f, 0.31f) : FVector(0.085f, 0.085f, 0.36f));
        PrototypeLeftArm->SetRelativeScale3D(ArmScale);
        PrototypeRightArm->SetRelativeScale3D(ArmScale);
        PrototypeLeftLeg->SetRelativeScale3D(LegScale);
        PrototypeRightLeg->SetRelativeScale3D(LegScale);
        PrototypeLeftFoot->SetRelativeScale3D(bHobbit ? FVector(0.23f, 0.135f, 0.075f) : FVector(0.18f, 0.105f, 0.07f));
        PrototypeRightFoot->SetRelativeScale3D(PrototypeLeftFoot->GetRelativeScale3D());
    }

    PrototypeCloak->SetVisibility(bNeedsCloak, true);
    PrototypeCloak->SetRelativeLocation(FVector(-8, 0, bHobbit ? -8.0f : -4.0f));
    PrototypeCloak->SetRelativeScale3D(bProductionCharacter ? FVector(1) :
        (bHobbit ? FVector(0.30f, 0.27f, 0.42f) : FVector(0.38f, 0.33f, 0.72f)));

    PrototypeHat->SetVisibility(bGandalf, true);
    PrototypeHat->SetRelativeLocation(FVector(-1, 0, bProductionCharacter ? 91.0f : 101.0f));
    PrototypeHat->SetRelativeScale3D(bProductionCharacter ? FVector(1) : FVector(0.34f, 0.34f, 0.48f));

    PrototypeBeard->SetVisibility(bGandalf || bGimli, true);
    PrototypeBeard->SetRelativeLocation(FVector(bProductionCharacter ? 14.0f : 10.0f, 0, bGimli ? 35.0f : 62.0f));
    PrototypeBeard->SetRelativeRotation(bProductionCharacter ? FRotator::ZeroRotator : FRotator(180, 0, 0));
    PrototypeBeard->SetRelativeScale3D(bProductionCharacter ? FVector(1) : (bGimli ? FVector(0.13f, 0.13f, 0.30f) : FVector(0.14f, 0.13f, 0.28f)));

    const bool bUsesSatchel = bFrodo || bSam;
    PrototypeSatchel->SetVisibility(bUsesSatchel || bBoromir, true);
    PrototypeSatchel->SetRelativeLocation(bBoromir ? FVector(-9, 24, 15) : FVector(-2, bProductionCharacter ? 19.0f : 22.0f, -5));
    PrototypeSatchel->SetRelativeRotation(bBoromir ? FRotator(0, 90, 8) : FRotator(0, 12, 8));
    PrototypeSatchel->SetRelativeScale3D(bProductionCharacter ? FVector(1) : (bBoromir ? FVector(0.08f, 0.34f, 0.42f) : FVector(0.13f, 0.06f, 0.15f)));

    FLinearColor TorsoColor(0.18f, 0.31f, 0.135f);
    FLinearColor HairColor(0.105f, 0.045f, 0.020f);
    FLinearColor LimbColor(0.20f, 0.35f, 0.15f);
    FLinearColor LegColor(0.27f, 0.17f, 0.075f);
    if (bGandalf) { TorsoColor=FLinearColor(0.28f,0.29f,0.27f); HairColor=FLinearColor(0.69f,0.68f,0.63f); LimbColor=FLinearColor(0.25f,0.26f,0.24f); LegColor=FLinearColor(0.17f,0.18f,0.17f); }
    else if (bSam) { TorsoColor=FLinearColor(0.24f,0.31f,0.14f); HairColor=FLinearColor(0.25f,0.12f,0.045f); LimbColor=FLinearColor(0.30f,0.34f,0.17f); }
    else if (bMerry) { TorsoColor=FLinearColor(0.30f,0.24f,0.10f); LimbColor=FLinearColor(0.28f,0.30f,0.14f); }
    else if (bPippin) { TorsoColor=FLinearColor(0.13f,0.28f,0.16f); LimbColor=FLinearColor(0.17f,0.31f,0.18f); }
    else if (bAragorn) { TorsoColor=FLinearColor(0.10f,0.18f,0.10f); HairColor=FLinearColor(0.08f,0.045f,0.025f); LimbColor=FLinearColor(0.13f,0.16f,0.10f); LegColor=FLinearColor(0.12f,0.10f,0.07f); }
    else if (bBoromir) { TorsoColor=FLinearColor(0.32f,0.12f,0.09f); HairColor=FLinearColor(0.26f,0.14f,0.06f); LimbColor=FLinearColor(0.30f,0.24f,0.18f); LegColor=FLinearColor(0.18f,0.16f,0.14f); }
    else if (bLegolas) { TorsoColor=FLinearColor(0.23f,0.31f,0.19f); HairColor=FLinearColor(0.52f,0.43f,0.23f); LimbColor=FLinearColor(0.27f,0.33f,0.23f); LegColor=FLinearColor(0.21f,0.23f,0.16f); }
    else if (bGimli) { TorsoColor=FLinearColor(0.28f,0.18f,0.10f); HairColor=FLinearColor(0.42f,0.18f,0.055f); LimbColor=FLinearColor(0.25f,0.19f,0.13f); LegColor=FLinearColor(0.20f,0.15f,0.10f); }
    else if (bArwen) { TorsoColor=FLinearColor(0.12f,0.16f,0.24f); HairColor=FLinearColor(0.055f,0.035f,0.025f); LimbColor=FLinearColor(0.16f,0.19f,0.27f); LegColor=FLinearColor(0.11f,0.13f,0.18f); }

    const FLinearColor Skin = bGandalf ? FLinearColor(0.72f,0.54f,0.40f) : FLinearColor(0.78f,0.57f,0.39f);
    ApplyColor(PrototypeTorso,TorsoColor);
    ApplyColor(PrototypeHead,Skin);
    ApplyColor(PrototypeHair,HairColor);
    ApplyColor(PrototypeLeftArm,LimbColor);
    ApplyColor(PrototypeRightArm,LimbColor);
    ApplyColor(PrototypeLeftLeg,LegColor);
    ApplyColor(PrototypeRightLeg,LegColor);
    ApplyColor(PrototypeLeftFoot,FLinearColor(0.12f,0.08f,0.055f));
    ApplyColor(PrototypeRightFoot,FLinearColor(0.12f,0.08f,0.055f));
    ApplyColor(PrototypeCloak,bAragorn ? FLinearColor(0.10f,0.20f,0.10f) : TorsoColor * 0.75f);
    ApplyColor(PrototypeHat,FLinearColor(0.245f,0.25f,0.235f));
    ApplyColor(PrototypeBeard,bGimli ? FLinearColor(0.44f,0.20f,0.07f) : FLinearColor(0.68f,0.67f,0.62f));
    ApplyColor(PrototypeLeftEye,FLinearColor(0.035f,0.028f,0.020f));
    ApplyColor(PrototypeRightEye,FLinearColor(0.035f,0.028f,0.020f));
    ApplyColor(PrototypeMouth,FLinearColor(0.23f,0.055f,0.045f));
    ApplyColor(PrototypeSatchel,bBoromir ? FLinearColor(0.34f,0.36f,0.37f) : FLinearColor(0.26f,0.13f,0.045f));

    const bool bWeaponVisible = bFrodo || bGandalf || bAragorn || bBoromir || bLegolas || bGimli;
    PrototypeWeapon->SetVisibility(bWeaponVisible, true);
    PrototypeWeapon->SetRelativeLocation(bGandalf ? FVector(4,34,0) : FVector(8,29,-4));
    PrototypeWeapon->SetRelativeScale3D(bProductionCharacter ? FVector(1) :
        (bGandalf ? FVector(0.055f,0.055f,0.92f) : (bLegolas ? FVector(0.035f,0.035f,0.72f) : FVector(0.045f,0.045f,0.52f))));
    PrototypeWeapon->SetRelativeRotation(bGandalf ? FRotator::ZeroRotator : FRotator(-12,0,8));
    ApplyColor(PrototypeWeapon,bGandalf ? FLinearColor(0.22f,0.13f,0.055f) : FLinearColor(0.48f,0.50f,0.52f));

    const float FaceX=bProductionCharacter ? 17.0f : 10.5f;
    const float FaceY=bProductionCharacter ? 6.5f : 5.2f;
    const float FaceZ=PrototypeHeadBaseZ+(bProductionCharacter ? 3.0f : 1.5f);
    PrototypeLeftEye->SetRelativeLocation(FVector(FaceX,-FaceY,FaceZ+2));
    PrototypeRightEye->SetRelativeLocation(FVector(FaceX,FaceY,FaceZ+2));
    PrototypeLeftEye->SetRelativeScale3D(bProductionCharacter ? FVector(0.026f,0.020f,0.035f) : FVector(0.035f,0.025f,0.045f));
    PrototypeRightEye->SetRelativeScale3D(bProductionCharacter ? FVector(0.026f,0.020f,0.035f) : FVector(0.035f,0.025f,0.045f));
    PrototypeMouth->SetRelativeLocation(FVector(FaceX+0.5f,0,FaceZ-6));
    PrototypeMouth->SetRelativeScale3D(bProductionCharacter ? FVector(0.012f,0.050f,0.010f) : FVector(0.018f,0.065f,0.012f));

    bUsingSkeletalProductionRig = TryApplyProductionRig(VisualId.ToString());
}

void AShirePlayerCharacter::UpdatePrototypeAnimation(float DeltaSeconds)
{
    if (bUsingSkeletalProductionRig)
    {
        return;
    }

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

    const bool bTallMotion = PrototypeMotionProfile == TEXT("TALL") || PrototypeMotionProfile == TEXT("ELF");
    const bool bDwarfMotion = PrototypeMotionProfile == TEXT("DWARF");
    PrototypeIdlePhase += DeltaSeconds * (bTallMotion ? 1.05f : (bDwarfMotion ? 1.15f : 1.35f));

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
        const float GaitAmplitude = bTallMotion
            ? (bSprinting ? 31.0f : 23.0f)
            : (bDwarfMotion ? (bSprinting ? 34.0f : 25.0f) : (bSprinting ? 38.0f : 29.0f));

        PrototypeWalkPhase += DeltaSeconds * GaitRate * SpeedRatio;
        const float StepSin = FMath::Sin(PrototypeWalkPhase);
        Swing = StepSin * GaitAmplitude;
        Bob = FMath::Abs(FMath::Sin(PrototypeWalkPhase * 2.0f)) *
            (bSprinting ? 2.4f : 1.4f);
        StepLift = FMath::Max(0.0f, StepSin) * (bSprinting ? 3.0f : 1.6f);
    }

    const float IdleBreath = (!bMoving && !bFalling)
        ? FMath::Sin(PrototypeIdlePhase) * (bTallMotion ? 0.55f : (bDwarfMotion ? 0.62f : 0.75f))
        : 0.0f;
    const float CrouchDrop = bCrouching ? (bTallMotion ? 11.0f : (bDwarfMotion ? 9.0f : 8.0f)) : 0.0f;
    const float SprintLean = bSprinting ? (bTallMotion ? -4.0f : (bDwarfMotion ? -5.0f : -7.0f)) : 0.0f;
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

    if (PendingChapterCheckpointId != NAME_None)
    {
        const FName CheckpointId = PendingChapterCheckpointId;
        PendingChapterCheckpointId = NAME_None;
        SaveAutomaticCheckpoint(CheckpointId, true);
    }

    AttackCooldownRemaining = FMath::Max(0.0f, AttackCooldownRemaining - DeltaSeconds);
    AttackVisualRemaining = FMath::Max(0.0f, AttackVisualRemaining - DeltaSeconds);
    UpdatePlayerLife(DeltaSeconds);
    UpdatePrototypeAnimation(DeltaSeconds);
}

void AShirePlayerCharacter::BeginPlay()
{
    Super::BeginPlay();
    GetCharacterMovement()->MaxWalkSpeed = WalkSpeed;
    CurrentStamina = FMath::Clamp(CurrentStamina, 0.0f, MaxStamina);
    CurrentResolve = FMath::Clamp(CurrentResolve, 0.0f, MaxResolve);
    Supplies = FMath::Clamp(Supplies, 0, MaxSupplies);
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
    PlayerInputComponent->BindAction(TEXT("UseSupply"), IE_Pressed, this, &AShirePlayerCharacter::UseSupply);
    PlayerInputComponent->BindAction(TEXT("ToggleChronicle"), IE_Pressed, this, &AShirePlayerCharacter::ToggleChronicle);
    PlayerInputComponent->BindAction(TEXT("ChroniclePrevious"), IE_Pressed, this, &AShirePlayerCharacter::ChroniclePrevious);
    PlayerInputComponent->BindAction(TEXT("ChronicleNext"), IE_Pressed, this, &AShirePlayerCharacter::ChronicleNext);
    PlayerInputComponent->BindAction(TEXT("ToggleWorldMap"), IE_Pressed, this, &AShirePlayerCharacter::ToggleWorldMap);
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

    // Queue transition checkpoints until the next player Tick. StartChapter broadcasts
    // synchronously while the world router rebuilds the generated region, so waiting one
    // Tick ensures the checkpoint transform belongs to the new authoritative chapter.
    if (PreviousChapterId == TEXT("P1C01") && NewChapterId == TEXT("P1C02"))
    {
        PendingChapterCheckpointId = TEXT("WC_P1C01_FERRY");
    }
    else if (PreviousChapterId == TEXT("P1C02") && NewChapterId == TEXT("P1C03"))
    {
        PendingChapterCheckpointId = TEXT("WC_P1C02_DEPART");
    }
    else if (PreviousChapterId == TEXT("P1C03") && NewChapterId == TEXT("P1C04"))
    {
        PendingChapterCheckpointId = TEXT("WC_P1C03_FORD");
    }
    else if (PreviousChapterId == TEXT("P1C04") && NewChapterId == TEXT("P1C05"))
    {
        PendingChapterCheckpointId = TEXT("WC_P1C04_DEPART");
    }
    else if (PreviousChapterId == TEXT("P1C05") && NewChapterId == TEXT("P1C06"))
    {
        PendingChapterCheckpointId = TEXT("WC_P1C05_MORIA_GATE");
    }
    else if (PreviousChapterId == TEXT("P1C06") && NewChapterId == TEXT("P1C07"))
    {
        PendingChapterCheckpointId = TEXT("WC_P1C06_EXIT");
    }
    else if (PreviousChapterId == TEXT("P1C07") && NewChapterId == TEXT("P1C08"))
    {
        PendingChapterCheckpointId = TEXT("WC_P1C07_DEPART");
    }
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
        if (!bStaminaExhausted && CurrentStamina > 5.0f)
        {
            GetCharacterMovement()->MaxWalkSpeed = SprintSpeed;
        }
    }
}

void AShirePlayerCharacter::StopSprint()
{
    bSprintRequested = false;
    GetCharacterMovement()->MaxWalkSpeed = WalkSpeed;
}

float AShirePlayerCharacter::GetResolveTarget() const
{
    int32 RingPressure = 0;
    if (const UGameInstance* GI = GetGameInstance())
    {
        if (const UShireQuestSubsystem* Quests = GI->GetSubsystem<UShireQuestSubsystem>())
        {
            RingPressure = Quests->GetRingPressureTier();
        }
    }
    return FMath::Clamp(MaxResolve - static_cast<float>(RingPressure) * 10.0f, MaxResolve * 0.45f, MaxResolve);
}

void AShirePlayerCharacter::UpdatePlayerLife(float DeltaSeconds)
{
    if (DeltaSeconds <= 0.0f || !GetCharacterMovement())
    {
        return;
    }

    const bool bMoving = GetVelocity().SizeSquared2D() > 100.0f;
    const bool bCanSprint = bSprintRequested && !bCinematicInputLocked && !bStaminaExhausted && CurrentStamina > 0.0f;
    const bool bActivelySprinting = bCanSprint && bMoving;

    if (bActivelySprinting)
    {
        CurrentStamina = FMath::Max(0.0f, CurrentStamina - SprintStaminaDrainPerSecond * DeltaSeconds);
        StaminaRegenDelayRemaining = 0.75f;
        GetCharacterMovement()->MaxWalkSpeed = SprintSpeed;
        if (CurrentStamina <= 0.0f)
        {
            bStaminaExhausted = true;
            GetCharacterMovement()->MaxWalkSpeed = WalkSpeed;
        }
    }
    else
    {
        StaminaRegenDelayRemaining = FMath::Max(0.0f, StaminaRegenDelayRemaining - DeltaSeconds);
        if (StaminaRegenDelayRemaining <= 0.0f)
        {
            CurrentStamina = FMath::Min(MaxStamina, CurrentStamina + StaminaRegenPerSecond * DeltaSeconds);
        }
        if (bStaminaExhausted && CurrentStamina >= MaxStamina * 0.25f)
        {
            bStaminaExhausted = false;
        }
        GetCharacterMovement()->MaxWalkSpeed =
            bSprintRequested && !bStaminaExhausted && CurrentStamina > 5.0f ? SprintSpeed : WalkSpeed;
    }

    const float ResolveTarget = GetResolveTarget();
    if (CurrentResolve < ResolveTarget)
    {
        CurrentResolve = FMath::Min(ResolveTarget, CurrentResolve + ResolveRecoveryPerSecond * DeltaSeconds);
    }
    else if (CurrentResolve > ResolveTarget)
    {
        const float PressureRate = FMath::Max(1.5f, ResolveRecoveryPerSecond * 0.35f);
        CurrentResolve = FMath::Max(ResolveTarget, CurrentResolve - PressureRate * DeltaSeconds);
    }
}

void AShirePlayerCharacter::GrantSupplies(int32 Amount)
{
    if (Amount > 0)
    {
        Supplies = FMath::Clamp(Supplies + Amount, 0, MaxSupplies);
    }
}

void AShirePlayerCharacter::UseSupply()
{
    if (bCinematicInputLocked)
    {
        return;
    }
    if (Supplies <= 0)
    {
        if (APlayerController* PC = Cast<APlayerController>(Controller))
            if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
                HUD->ShowAlert(FText::FromString(TEXT("No travel supplies left.")), 1.4f);
        return;
    }

    const bool bNeedsRecovery =
        CurrentHealth < MaxHealth - 0.5f ||
        CurrentResolve < GetResolveTarget() - 0.5f ||
        CurrentStamina < MaxStamina - 0.5f;
    if (!bNeedsRecovery)
    {
        if (APlayerController* PC = Cast<APlayerController>(Controller))
            if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
                HUD->ShowAlert(FText::FromString(TEXT("You are already well prepared.")), 1.2f);
        return;
    }

    --Supplies;
    CurrentHealth = FMath::Min(MaxHealth, CurrentHealth + 28.0f);
    CurrentStamina = FMath::Min(MaxStamina, CurrentStamina + 55.0f);
    CurrentResolve = FMath::Min(GetResolveTarget(), CurrentResolve + 24.0f);
    bStaminaExhausted = false;

    if (APlayerController* PC = Cast<APlayerController>(Controller))
        if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
            HUD->ShowAlert(
                FText::FromString(FString::Printf(TEXT("Travel supplies used. %d remaining."), Supplies)),
                1.5f);
}

void AShirePlayerCharacter::ToggleChronicle()
{
    if (bCinematicInputLocked)
    {
        return;
    }

    bChronicleOpen = !bChronicleOpen;
    if (bChronicleOpen)
    {
        bWorldMapOpen = false;
        const UGameInstance* GI = GetGameInstance();
        const UShireQuestSubsystem* Quests =
            GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
        ChronicleBrowseIndex = Quests ? FMath::Max(0, Quests->GetChronicleCount() - 1) : 0;
    }
}

void AShirePlayerCharacter::ChroniclePrevious()
{
    if (!bChronicleOpen || bCinematicInputLocked)
    {
        return;
    }
    ChronicleBrowseIndex = FMath::Max(0, ChronicleBrowseIndex - 1);
}

void AShirePlayerCharacter::ChronicleNext()
{
    if (!bChronicleOpen || bCinematicInputLocked)
    {
        return;
    }

    const UGameInstance* GI = GetGameInstance();
    const UShireQuestSubsystem* Quests =
        GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    const int32 MaxIndex = Quests ? FMath::Max(0, Quests->GetChronicleCount() - 1) : 0;
    ChronicleBrowseIndex = FMath::Min(MaxIndex, ChronicleBrowseIndex + 1);
}


void AShirePlayerCharacter::ToggleWorldMap()
{
    if (bCinematicInputLocked)
    {
        return;
    }

    bWorldMapOpen = !bWorldMapOpen;
    if (bWorldMapOpen)
    {
        bChronicleOpen = false;
    }
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
    CurrentResolve = FMath::Max(0.0f, CurrentResolve - 8.0f);

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

    Save->SaveSchemaVersion = UShireSaveGame::CurrentSchemaVersion;
    Save->SnapshotCreatedUnixSeconds = FDateTime::UtcNow().ToUnixTimestamp();
    Save->PlayerLocation = GetActorLocation();
    Save->PlayerRotation = GetActorRotation();
    Save->CheckpointId = CheckpointId;
    Save->PlayerHealth = bCheckpointSnapshot ? MaxHealth : CurrentHealth;
    Save->PlayerStamina = bCheckpointSnapshot ? MaxStamina : CurrentStamina;
    Save->PlayerResolve = bCheckpointSnapshot ? GetResolveTarget() : CurrentResolve;
    Save->PlayerSupplies = Supplies;

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
            Save->NPCMemoryState = QuestSubsystem->GetNPCMemorySnapshot();
            Save->JourneyDiscoveryIds = QuestSubsystem->GetJourneyDiscoveryIds();
            Save->JourneyInsight = QuestSubsystem->GetJourneyInsight();
            Save->JourneyInsightMilestones = QuestSubsystem->GetJourneyInsightMilestones();
            Save->ProgressionXP = QuestSubsystem->GetProgressionSnapshot();
            Save->ChronicleEntryIds = QuestSubsystem->GetChronicleEntryIds();
            Save->KnownMapRegionIds = QuestSubsystem->GetKnownMapRegionIds();
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

    if (Save->SaveSchemaVersion > UShireSaveGame::CurrentSchemaVersion)
    {
        UE_LOG(
            LogTemp,
            Error,
            TEXT("Save snapshot schema is newer than this build: save=%d supported=%d"),
            Save->SaveSchemaVersion,
            UShireSaveGame::CurrentSchemaVersion);
        return false;
    }

    if (!FMath::IsFinite(Save->PlayerLocation.X) ||
        !FMath::IsFinite(Save->PlayerLocation.Y) ||
        !FMath::IsFinite(Save->PlayerLocation.Z) ||
        !FMath::IsFinite(Save->PlayerHealth) ||
        !FMath::IsFinite(Save->PlayerStamina) ||
        !FMath::IsFinite(Save->PlayerResolve))
    {
        UE_LOG(LogTemp, Error, TEXT("Save snapshot rejected: invalid numeric state."));
        return false;
    }

    if (Save->CurrentRouteId == NAME_None)
    {
        Save->CurrentRouteId = TEXT("FrodoMain");
    }
    if (Save->CurrentChapterId == NAME_None)
    {
        Save->CurrentChapterId = TEXT("P1C01");
    }
    if (Save->PlayableCharacterId == NAME_None)
    {
        Save->PlayableCharacterId =
            Save->CurrentRouteId == TEXT("GandalfParallel") ? FName(TEXT("Gandalf")) : FName(TEXT("Frodo"));
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

            QuestSubsystem->RestoreNPCMemoryState(Save->NPCMemoryState);
            QuestSubsystem->RestoreJourneyDiscoveryState(
                Save->JourneyDiscoveryIds,
                Save->JourneyInsight,
                Save->JourneyInsightMilestones);
            QuestSubsystem->RestoreProgressionState(Save->ProgressionXP);
            QuestSubsystem->RestoreKnowledgeState(
                Save->ChronicleEntryIds,
                Save->KnownMapRegionIds);

            bApplyExactSavedTransform =
                QuestSubsystem->GetCurrentChapterId() == SavedChapterId;
        }
    }

    CurrentHealth = FMath::Clamp(Save->PlayerHealth, 1.0f, MaxHealth);
    CurrentStamina = FMath::Clamp(Save->PlayerStamina, 0.0f, MaxStamina);
    CurrentResolve = FMath::Clamp(Save->PlayerResolve, 0.0f, MaxResolve);
    Supplies = FMath::Clamp(Save->PlayerSupplies, 0, MaxSupplies);
    bStaminaExhausted = CurrentStamina <= 0.0f;

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
        CurrentStamina = MaxStamina;
        CurrentResolve = GetResolveTarget();
        bStaminaExhausted = false;
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
