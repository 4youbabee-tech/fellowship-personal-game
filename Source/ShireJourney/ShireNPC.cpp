#include "ShireNPC.h"
#include "ShireQuestSubsystem.h"
#include "ShireHUD.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/GameInstance.h"
#include "GameFramework/PlayerController.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

AShireNPC::AShireNPC()
{
    PrimaryActorTick.bCanEverTick = true;
    GetCapsuleComponent()->SetCapsuleRadius(28.0f);
    GetCapsuleComponent()->SetCapsuleHalfHeight(60.0f);
    DisplayName = FText::FromString(TEXT("Hobbit"));

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

    PrototypeLeftEye = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeLeftEye"));
    PrototypeLeftEye->SetupAttachment(PrototypeHead);
    PrototypeLeftEye->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeLeftEye->SetRelativeLocation(FVector(43.0f, -16.0f, 8.0f));
    PrototypeLeftEye->SetRelativeScale3D(FVector(0.12f, 0.09f, 0.13f));

    PrototypeRightEye = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeRightEye"));
    PrototypeRightEye->SetupAttachment(PrototypeHead);
    PrototypeRightEye->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeRightEye->SetRelativeLocation(FVector(43.0f, 16.0f, 8.0f));
    PrototypeRightEye->SetRelativeScale3D(FVector(0.12f, 0.09f, 0.13f));

    PrototypeMouth = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeMouth"));
    PrototypeMouth->SetupAttachment(PrototypeHead);
    PrototypeMouth->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeMouth->SetRelativeLocation(FVector(44.0f, 0.0f, -16.0f));
    PrototypeMouth->SetRelativeScale3D(FVector(0.11f, 0.16f, 0.045f));

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

    static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(TEXT("/Engine/BasicShapes/Sphere.Sphere"));

    if (CubeMesh.Succeeded())
    {
        PrototypeTorso->SetStaticMesh(CubeMesh.Object);
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
        PrototypeLeftEye->SetStaticMesh(SphereMesh.Object);
        PrototypeRightEye->SetStaticMesh(SphereMesh.Object);
        PrototypeMouth->SetStaticMesh(SphereMesh.Object);
    }
}

void AShireNPC::ApplyPrototypeStyle()
{
    UMaterialInterface* BasicMaterial = LoadObject<UMaterialInterface>(
        nullptr, TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
    if (!BasicMaterial)
    {
        bVisualStyleApplied = true;
        return;
    }

    const FString Name = DisplayName.ToString();

    FLinearColor Coat(0.24f, 0.34f, 0.17f);
    FLinearColor Trousers(0.27f, 0.18f, 0.10f);
    FLinearColor Hair(0.12f, 0.055f, 0.025f);
    FLinearColor Skin(0.74f, 0.52f, 0.34f);

    PrototypeTorsoBaseZ = -4.0f;
    PrototypeHeadBaseZ = 39.0f;
    PrototypeHairBaseZ = 47.0f;

    auto ConfigureTallFigure = [this](float WidthScale)
    {
        PrototypeTorsoBaseZ = 6.0f;
        PrototypeHeadBaseZ = 61.0f;
        PrototypeHairBaseZ = 69.0f;

        PrototypeTorso->SetRelativeLocation(FVector(0.0f, 0.0f, PrototypeTorsoBaseZ));
        PrototypeTorso->SetRelativeScale3D(FVector(0.31f * WidthScale, 0.23f * WidthScale, 0.50f));
        PrototypeHead->SetRelativeLocation(FVector(0.0f, 0.0f, PrototypeHeadBaseZ));
        PrototypeHead->SetRelativeScale3D(FVector(0.225f));
        PrototypeHair->SetRelativeLocation(FVector(-1.0f, 0.0f, PrototypeHairBaseZ));
        PrototypeHair->SetRelativeScale3D(FVector(0.23f, 0.23f, 0.11f));
        PrototypeLeftArm->SetRelativeLocation(FVector(0.0f, -25.0f * WidthScale, 8.0f));
        PrototypeRightArm->SetRelativeLocation(FVector(0.0f, 25.0f * WidthScale, 8.0f));
        PrototypeLeftArm->SetRelativeScale3D(FVector(0.08f, 0.08f, 0.44f));
        PrototypeRightArm->SetRelativeScale3D(FVector(0.08f, 0.08f, 0.44f));
        PrototypeLeftLeg->SetRelativeLocation(FVector(0.0f, -10.0f, -43.0f));
        PrototypeRightLeg->SetRelativeLocation(FVector(0.0f, 10.0f, -43.0f));
        PrototypeLeftLeg->SetRelativeScale3D(FVector(0.10f, 0.10f, 0.41f));
        PrototypeRightLeg->SetRelativeScale3D(FVector(0.10f, 0.10f, 0.41f));
    };

    auto ConfigureDwarfFigure = [this]()
    {
        PrototypeTorsoBaseZ = -1.0f;
        PrototypeHeadBaseZ = 45.0f;
        PrototypeHairBaseZ = 53.0f;

        PrototypeTorso->SetRelativeLocation(FVector(0.0f, 0.0f, PrototypeTorsoBaseZ));
        PrototypeTorso->SetRelativeScale3D(FVector(0.39f, 0.30f, 0.40f));
        PrototypeHead->SetRelativeLocation(FVector(0.0f, 0.0f, PrototypeHeadBaseZ));
        PrototypeHead->SetRelativeScale3D(FVector(0.25f));
        PrototypeHair->SetRelativeLocation(FVector(-1.0f, 0.0f, PrototypeHairBaseZ));
        PrototypeHair->SetRelativeScale3D(FVector(0.255f, 0.255f, 0.14f));
        PrototypeLeftArm->SetRelativeLocation(FVector(0.0f, -29.0f, -1.0f));
        PrototypeRightArm->SetRelativeLocation(FVector(0.0f, 29.0f, -1.0f));
        PrototypeLeftArm->SetRelativeScale3D(FVector(0.095f, 0.095f, 0.34f));
        PrototypeRightArm->SetRelativeScale3D(FVector(0.095f, 0.095f, 0.34f));
        PrototypeLeftLeg->SetRelativeLocation(FVector(0.0f, -11.0f, -42.0f));
        PrototypeRightLeg->SetRelativeLocation(FVector(0.0f, 11.0f, -42.0f));
        PrototypeLeftLeg->SetRelativeScale3D(FVector(0.12f, 0.12f, 0.29f));
        PrototypeRightLeg->SetRelativeScale3D(FVector(0.12f, 0.12f, 0.29f));
    };

    const bool bRanger =
        Name.Equals(TEXT("Aragorn"), ESearchCase::IgnoreCase) ||
        Name.Equals(TEXT("Strider"), ESearchCase::IgnoreCase);
    const bool bWizard =
        Name.Equals(TEXT("Gandalf"), ESearchCase::IgnoreCase) ||
        Name.Equals(TEXT("Saruman"), ESearchCase::IgnoreCase);
    const bool bHuman =
        bRanger ||
        Name.Equals(TEXT("Boromir"), ESearchCase::IgnoreCase) ||
        Name.Equals(TEXT("Gate Keeper"), ESearchCase::IgnoreCase) ||
        Name.Equals(TEXT("Barliman Butterbur"), ESearchCase::IgnoreCase);
    const bool bElf =
        Name.Equals(TEXT("Arwen"), ESearchCase::IgnoreCase) ||
        Name.Equals(TEXT("Elrond"), ESearchCase::IgnoreCase) ||
        Name.Equals(TEXT("Haldir"), ESearchCase::IgnoreCase) ||
        Name.Equals(TEXT("Galadriel"), ESearchCase::IgnoreCase) ||
        Name.Equals(TEXT("Legolas"), ESearchCase::IgnoreCase);

    if (bWizard)
    {
        ConfigureTallFigure(1.02f);
        PrototypeTorsoBaseZ = 8.0f;
        PrototypeHeadBaseZ = 64.0f;
        PrototypeHairBaseZ = 72.0f;
        PrototypeTorso->SetRelativeLocation(FVector(0.0f, 0.0f, PrototypeTorsoBaseZ));
        PrototypeHead->SetRelativeLocation(FVector(0.0f, 0.0f, PrototypeHeadBaseZ));
        PrototypeHair->SetRelativeLocation(FVector(-1.0f, 0.0f, PrototypeHairBaseZ));
        const bool bSaruman = Name.Equals(TEXT("Saruman"), ESearchCase::IgnoreCase);
        Coat = bSaruman ? FLinearColor(0.70f, 0.69f, 0.64f) : FLinearColor(0.30f, 0.31f, 0.29f);
        Trousers = bSaruman ? FLinearColor(0.50f, 0.49f, 0.45f) : FLinearColor(0.20f, 0.21f, 0.20f);
        Hair = bSaruman ? FLinearColor(0.82f, 0.80f, 0.74f) : FLinearColor(0.72f, 0.70f, 0.64f);
    }
    else if (Name.Equals(TEXT("Gimli"), ESearchCase::IgnoreCase))
    {
        ConfigureDwarfFigure();
        Coat = FLinearColor(0.30f, 0.20f, 0.12f);
        Trousers = FLinearColor(0.20f, 0.15f, 0.10f);
        Hair = FLinearColor(0.44f, 0.20f, 0.07f);
    }
    else if (bElf)
    {
        ConfigureTallFigure(0.90f);
        Coat = Name.Equals(TEXT("Galadriel"), ESearchCase::IgnoreCase)
            ? FLinearColor(0.62f, 0.66f, 0.60f)
            : FLinearColor(0.25f, 0.36f, 0.28f);
        Trousers = FLinearColor(0.20f, 0.26f, 0.20f);
        Hair = (Name.Equals(TEXT("Galadriel"), ESearchCase::IgnoreCase) ||
                Name.Equals(TEXT("Haldir"), ESearchCase::IgnoreCase) ||
                Name.Equals(TEXT("Legolas"), ESearchCase::IgnoreCase))
            ? FLinearColor(0.78f, 0.68f, 0.42f)
            : FLinearColor(0.10f, 0.065f, 0.04f);
        Skin = FLinearColor(0.78f, 0.61f, 0.46f);
    }
    else if (bHuman)
    {
        const float Width = Name.Equals(TEXT("Barliman Butterbur"), ESearchCase::IgnoreCase) ? 1.18f : 1.0f;
        ConfigureTallFigure(Width);
        if (bRanger)
        {
            Coat = FLinearColor(0.16f, 0.22f, 0.14f);
            Trousers = FLinearColor(0.16f, 0.13f, 0.09f);
            Hair = FLinearColor(0.10f, 0.055f, 0.025f);
        }
        else if (Name.Equals(TEXT("Boromir"), ESearchCase::IgnoreCase))
        {
            Coat = FLinearColor(0.36f, 0.16f, 0.12f);
            Trousers = FLinearColor(0.22f, 0.16f, 0.11f);
            Hair = FLinearColor(0.30f, 0.19f, 0.08f);
        }
        else
        {
            Coat = FLinearColor(0.31f, 0.25f, 0.18f);
            Trousers = FLinearColor(0.22f, 0.18f, 0.13f);
            Hair = FLinearColor(0.18f, 0.10f, 0.045f);
        }
    }
    else if (Name.Equals(TEXT("Bilbo"), ESearchCase::IgnoreCase))
    {
        Coat = FLinearColor(0.42f, 0.22f, 0.12f);
        Trousers = FLinearColor(0.34f, 0.27f, 0.14f);
        Hair = FLinearColor(0.48f, 0.39f, 0.28f);
    }
    else if (Name.Equals(TEXT("Sam"), ESearchCase::IgnoreCase))
    {
        Coat = FLinearColor(0.34f, 0.43f, 0.18f);
        Trousers = FLinearColor(0.31f, 0.22f, 0.12f);
        Hair = FLinearColor(0.35f, 0.20f, 0.08f);
    }
    else if (Name.Equals(TEXT("Merry"), ESearchCase::IgnoreCase))
    {
        Coat = FLinearColor(0.42f, 0.30f, 0.12f);
        Trousers = FLinearColor(0.24f, 0.17f, 0.09f);
        Hair = FLinearColor(0.20f, 0.10f, 0.04f);
    }
    else if (Name.Equals(TEXT("Pippin"), ESearchCase::IgnoreCase))
    {
        Coat = FLinearColor(0.24f, 0.36f, 0.22f);
        Trousers = FLinearColor(0.30f, 0.20f, 0.11f);
        Hair = FLinearColor(0.30f, 0.18f, 0.08f);
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

    const bool bGandalfVisual = Name.Equals(TEXT("Gandalf"), ESearchCase::IgnoreCase);
    const bool bHobbitVisual =
        !bWizard && !bHuman && !bElf && !Name.Equals(TEXT("Gimli"), ESearchCase::IgnoreCase);

    bool bProductionVisual = false;
    if (bGandalfVisual)
    {
        bProductionVisual =
            TryMesh(PrototypeTorso, TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Torso.SM_Gandalf_Torso")) &&
            TryMesh(PrototypeHead, TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Head.SM_Gandalf_Head")) &&
            TryMesh(PrototypeHair, TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Hair.SM_Gandalf_Hair")) &&
            TryMesh(PrototypeLeftArm, TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Arm.SM_Gandalf_Arm")) &&
            TryMesh(PrototypeLeftLeg, TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Leg.SM_Gandalf_Leg"));
        TryMesh(PrototypeRightArm, TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Arm.SM_Gandalf_Arm"));
        TryMesh(PrototypeRightLeg, TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Leg.SM_Gandalf_Leg"));
    }
    else if (bHobbitVisual)
    {
        bProductionVisual =
            TryMesh(PrototypeTorso, TEXT("/Game/Production/Characters/Hobbit/SM_Hobbit_Torso.SM_Hobbit_Torso")) &&
            TryMesh(PrototypeHead, TEXT("/Game/Production/Characters/Hobbit/SM_Hobbit_Head.SM_Hobbit_Head")) &&
            TryMesh(PrototypeHair, TEXT("/Game/Production/Characters/Hobbit/SM_Hobbit_Hair.SM_Hobbit_Hair")) &&
            TryMesh(PrototypeLeftArm, TEXT("/Game/Production/Characters/Hobbit/SM_Hobbit_Arm.SM_Hobbit_Arm")) &&
            TryMesh(PrototypeLeftLeg, TEXT("/Game/Production/Characters/Hobbit/SM_Hobbit_Leg.SM_Hobbit_Leg"));
        TryMesh(PrototypeRightArm, TEXT("/Game/Production/Characters/Hobbit/SM_Hobbit_Arm.SM_Hobbit_Arm"));
        TryMesh(PrototypeRightLeg, TEXT("/Game/Production/Characters/Hobbit/SM_Hobbit_Leg.SM_Hobbit_Leg"));
    }

    if (bProductionVisual)
    {
        PrototypeTorso->SetRelativeScale3D(FVector(1));
        PrototypeHead->SetRelativeScale3D(FVector(1));
        PrototypeHair->SetRelativeScale3D(FVector(1));
        PrototypeLeftArm->SetRelativeScale3D(FVector(1));
        PrototypeRightArm->SetRelativeScale3D(FVector(1));
        PrototypeLeftLeg->SetRelativeScale3D(FVector(1));
        PrototypeRightLeg->SetRelativeScale3D(FVector(1));
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

    ApplyColor(PrototypeTorso, Coat);
    ApplyColor(PrototypeHead, Skin);
    ApplyColor(PrototypeHair, Hair);
    ApplyColor(PrototypeLeftArm, Coat * 0.95f);
    ApplyColor(PrototypeRightArm, Coat * 0.95f);
    ApplyColor(PrototypeLeftLeg, Trousers);
    ApplyColor(PrototypeRightLeg, Trousers);
    ApplyColor(PrototypeLeftEye, FLinearColor(0.045f, 0.035f, 0.025f));
    ApplyColor(PrototypeRightEye, FLinearColor(0.045f, 0.035f, 0.025f));
    ApplyColor(PrototypeMouth, FLinearColor(0.20f, 0.055f, 0.045f));

    bVisualStyleApplied = true;
}

void AShireNPC::UpdatePrototypeAnimation(float DeltaSeconds)
{
    float Swing = 0.0f;
    float Bob = 0.0f;
    if (bPrototypeMoving)
    {
        PrototypeWalkPhase += DeltaSeconds * 8.0f;
        Swing = FMath::Sin(PrototypeWalkPhase) * 25.0f;
        Bob = FMath::Abs(FMath::Sin(PrototypeWalkPhase * 2.0f)) * 1.2f;
    }

    const float BlendSpeed = 10.0f;
    if (PrototypeLeftArm)
    {
        PrototypeLeftArm->SetRelativeRotation(FMath::RInterpTo(
            PrototypeLeftArm->GetRelativeRotation(), FRotator(Swing, 0.0f, 0.0f), DeltaSeconds, BlendSpeed));
    }
    if (PrototypeRightArm)
    {
        PrototypeRightArm->SetRelativeRotation(FMath::RInterpTo(
            PrototypeRightArm->GetRelativeRotation(), FRotator(-Swing, 0.0f, 0.0f), DeltaSeconds, BlendSpeed));
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
            PrototypeTorso->GetRelativeLocation(),
            FVector(0.0f, 0.0f, PrototypeTorsoBaseZ + Bob), DeltaSeconds, 12.0f));
    }
    if (PrototypeHead)
    {
        PrototypeHead->SetRelativeLocation(FMath::VInterpTo(
            PrototypeHead->GetRelativeLocation(),
            FVector(0.0f, 0.0f, PrototypeHeadBaseZ + Bob), DeltaSeconds, 12.0f));
    }
    if (PrototypeHair)
    {
        PrototypeHair->SetRelativeLocation(FMath::VInterpTo(
            PrototypeHair->GetRelativeLocation(),
            FVector(-1.0f, 0.0f, PrototypeHairBaseZ + Bob), DeltaSeconds, 12.0f));
    }
}


void AShireNPC::UpdatePrototypeActing(float DeltaSeconds)
{
    if (!PrototypeHead || !PrototypeLeftEye || !PrototypeRightEye || !PrototypeMouth)
    {
        return;
    }

    if (BlinkCooldownRemaining <= 0.0f && BlinkRemaining <= 0.0f)
    {
        BlinkCooldownRemaining = 2.2f + FMath::Fmod(static_cast<float>(GetUniqueID()) * 0.173f, 2.1f);
    }

    BlinkCooldownRemaining = FMath::Max(0.0f, BlinkCooldownRemaining - DeltaSeconds);
    if (BlinkCooldownRemaining <= 0.0f && BlinkRemaining <= 0.0f)
    {
        BlinkRemaining = 0.10f;
    }
    if (BlinkRemaining > 0.0f)
    {
        BlinkRemaining = FMath::Max(0.0f, BlinkRemaining - DeltaSeconds);
    }

    const float EyeZ = BlinkRemaining > 0.0f ? 0.025f : 0.13f;
    PrototypeLeftEye->SetRelativeScale3D(FVector(0.12f, 0.09f, EyeZ));
    PrototypeRightEye->SetRelativeScale3D(FVector(0.12f, 0.09f, EyeZ));

    DialogueActingRemaining = FMath::Max(0.0f, DialogueActingRemaining - DeltaSeconds);
    if (DialogueActingRemaining > 0.0f)
    {
        ActingPhase += DeltaSeconds * 13.0f;
        const float MouthOpen = 0.045f + FMath::Abs(FMath::Sin(ActingPhase)) * 0.085f;
        PrototypeMouth->SetRelativeScale3D(FVector(0.11f, 0.16f, MouthOpen));
    }
    else
    {
        PrototypeMouth->SetRelativeScale3D(FVector(0.11f, 0.16f, 0.045f));
    }

    if (!bPrototypeMoving && GetWorld())
    {
        APlayerController* PC = GetWorld()->GetFirstPlayerController();
        APawn* PlayerPawn = PC ? PC->GetPawn() : nullptr;
        if (PlayerPawn)
        {
            FVector ToPlayer = PlayerPawn->GetActorLocation() - GetActorLocation();
            ToPlayer.Z = 0.0f;
            if (ToPlayer.SizeSquared2D() <= FMath::Square(520.0f) && !ToPlayer.IsNearlyZero())
            {
                const float RelativeYaw = FMath::FindDeltaAngleDegrees(
                    GetActorRotation().Yaw, ToPlayer.Rotation().Yaw);
                const float ClampedYaw = FMath::Clamp(RelativeYaw, -38.0f, 38.0f);
                PrototypeHead->SetRelativeRotation(FMath::RInterpTo(
                    PrototypeHead->GetRelativeRotation(),
                    FRotator(0.0f, ClampedYaw, 0.0f),
                    DeltaSeconds,
                    DialogueActingRemaining > 0.0f ? 7.0f : 3.0f));
                return;
            }
        }
    }

    PrototypeHead->SetRelativeRotation(FMath::RInterpTo(
        PrototypeHead->GetRelativeRotation(), FRotator::ZeroRotator, DeltaSeconds, 3.0f));
}

int32 AShireNPC::ResolveCompanionSlot() const
{
    if (CompanionSlotIndex >= 0)
    {
        return CompanionSlotIndex;
    }

    const FString Name = DisplayName.ToString();
    if (Name.Equals(TEXT("Sam"), ESearchCase::IgnoreCase)) return 0;
    if (Name.Equals(TEXT("Merry"), ESearchCase::IgnoreCase)) return 1;
    if (Name.Equals(TEXT("Pippin"), ESearchCase::IgnoreCase)) return 2;
    if (Name.Equals(TEXT("Aragorn"), ESearchCase::IgnoreCase) || Name.Equals(TEXT("Strider"), ESearchCase::IgnoreCase)) return 3;
    if (Name.Equals(TEXT("Boromir"), ESearchCase::IgnoreCase)) return 4;
    if (Name.Equals(TEXT("Legolas"), ESearchCase::IgnoreCase)) return 5;
    if (Name.Equals(TEXT("Gimli"), ESearchCase::IgnoreCase)) return 6;
    if (Name.Equals(TEXT("Gandalf"), ESearchCase::IgnoreCase)) return 7;
    return 8;
}

FVector AShireNPC::GetFormationTarget(const APawn* PlayerPawn) const
{
    if (!PlayerPawn)
    {
        return GetActorLocation();
    }

    const int32 Slot = ResolveCompanionSlot();
    const int32 Row = Slot / 2;
    const float Side = (Slot % 2 == 0) ? -1.0f : 1.0f;
    const float BackDistance = FollowDistance + Row * (FormationSpacing * 0.85f);
    const float SideDistance = FormationSpacing * (1.0f + 0.15f * Row) * Side;

    const FVector Forward = PlayerPawn->GetActorForwardVector().GetSafeNormal2D();
    const FVector Right = PlayerPawn->GetActorRightVector().GetSafeNormal2D();
    FVector Target = PlayerPawn->GetActorLocation() - Forward * BackDistance + Right * SideDistance;
    Target.Z = PlayerPawn->GetActorLocation().Z;
    return Target;
}

void AShireNPC::RestoreCompanionFollowState()
{
    bCompanionFollowStateResolved = true;

    if (!bFollowPlayerAfterInteraction)
    {
        return;
    }

    // Runtime builders assign quest/follow properties immediately after SpawnActor. Resolve on
    // the first Tick instead of BeginPlay so those assigned values are already available.
    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* QuestSubsystem = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!QuestSubsystem)
    {
        return;
    }

    if (QuestId == NAME_None)
    {
        bFollowingPlayer = true;
        return;
    }

    // Quest stages are persisted. If the interaction's resulting stage has already been reached,
    // this companion was recruited before a save/load or chapter-world rebuild and should resume
    // the cheap formation-follow behavior without requiring the player to repeat dialogue.
    if (QuestStageAfterInteraction >= 0 && QuestSubsystem->GetQuestStage(QuestId) >= QuestStageAfterInteraction)
    {
        bFollowingPlayer = true;
    }
}

void AShireNPC::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (!bVisualStyleApplied)
    {
        ApplyPrototypeStyle();
    }

    if (!bCompanionFollowStateResolved)
    {
        RestoreCompanionFollowState();
    }

    bPrototypeMoving = false;

    if (bFollowingPlayer && StopFollowingStoryBeat != NAME_None)
    {
        UGameInstance* GI = GetGameInstance();
        UShireQuestSubsystem* QuestSubsystem = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
        if (QuestSubsystem && QuestSubsystem->HasStoryBeatTriggered(StopFollowingStoryBeat))
        {
            bFollowingPlayer = false;
        }
    }

    if (bFollowingPlayer && GetWorld())
    {
        APlayerController* PC = GetWorld()->GetFirstPlayerController();
        APawn* PlayerPawn = PC ? PC->GetPawn() : nullptr;
        if (PlayerPawn)
        {
            const FVector Target = GetFormationTarget(PlayerPawn);
            FVector ToTarget = Target - GetActorLocation();
            ToTarget.Z = 0.0f;
            const float Distance = ToTarget.Size();

            if (Distance > TeleportCatchUpDistance)
            {
                FVector SafeTarget = Target;
                SafeTarget.Z = PlayerPawn->GetActorLocation().Z;
                SetActorLocation(SafeTarget, false, nullptr, ETeleportType::TeleportPhysics);
            }
            else if (Distance > FollowAcceptanceRadius)
            {
                const float EffectiveSpeed = Distance > CatchUpDistance ? FollowSpeed * 2.0f : FollowSpeed;
                const float MaxStep = EffectiveSpeed * DeltaSeconds;
                const FVector Step = ToTarget.GetSafeNormal() * FMath::Min(MaxStep, Distance - FollowAcceptanceRadius);
                AddActorWorldOffset(Step, true);
                bPrototypeMoving = !Step.IsNearlyZero();

                if (bPrototypeMoving)
                {
                    const FRotator DesiredRotation = Step.Rotation();
                    SetActorRotation(FMath::RInterpTo(GetActorRotation(), DesiredRotation, DeltaSeconds, 7.0f));
                }
            }
        }
    }

    UpdatePrototypeAnimation(DeltaSeconds);
    UpdatePrototypeActing(DeltaSeconds);
}


const TArray<FText>* AShireNPC::ResolveDialogueLines(const UShireQuestSubsystem* QuestSubsystem) const
{
    const TArray<FText>* Selected = &DialogueLines;
    if (!QuestSubsystem)
    {
        return Selected;
    }

    for (const FShireDialogueVariant& Variant : DialogueVariants)
    {
        bool bMatches = true;

        if (Variant.RequiredStoryBeat != NAME_None &&
            !QuestSubsystem->HasStoryBeatTriggered(Variant.RequiredStoryBeat))
        {
            bMatches = false;
        }

        if (Variant.ExcludedStoryBeat != NAME_None &&
            QuestSubsystem->HasStoryBeatTriggered(Variant.ExcludedStoryBeat))
        {
            bMatches = false;
        }

        if (Variant.RequiredQuestId != NAME_None)
        {
            if (QuestSubsystem->GetActiveQuestId() != Variant.RequiredQuestId)
            {
                bMatches = false;
            }
            else if (Variant.MinQuestStage >= 0 &&
                QuestSubsystem->GetQuestStage(Variant.RequiredQuestId) < Variant.MinQuestStage)
            {
                bMatches = false;
            }
        }

        if (bMatches && Variant.Lines.Num() > 0)
        {
            Selected = &Variant.Lines;
        }
    }

    return Selected;
}

void AShireNPC::Interact_Implementation(AActor* Interactor)
{
    DialogueActingRemaining = 2.5f;

    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* QuestSubsystem = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;

    if (QuestSubsystem && RequiredSideStoryBeat != NAME_None &&
        !QuestSubsystem->HasStoryBeatTriggered(RequiredSideStoryBeat))
    {
        if (APlayerController* PC = GetWorld() ? GetWorld()->GetFirstPlayerController() : nullptr)
        {
            if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
            {
                HUD->ShowDialogue(DisplayName,
                    FText::FromString(TEXT("There is something else to see before this part of the story continues.")), 4.0f);
            }
        }
        return;
    }

    if (QuestSubsystem && QuestId != NAME_None)
    {
        if (QuestSubsystem->GetActiveQuestId() != QuestId || QuestSubsystem->GetQuestStage(QuestId) < RequiredQuestStage)
        {
            if (APlayerController* PC = GetWorld() ? GetWorld()->GetFirstPlayerController() : nullptr)
            {
                if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
                {
                    HUD->ShowDialogue(DisplayName, FText::FromString(TEXT("Not now. There is something you must do first.")), 3.5f);
                }
            }
            return;
        }
    }

    const TArray<FText>* ActiveDialogue = ResolveDialogueLines(QuestSubsystem);
    if (ActiveDialogue && ActiveDialogue->Num() > 0)
    {
        const FText& Line = (*ActiveDialogue)[CurrentDialogueIndex % ActiveDialogue->Num()];
        if (APlayerController* PC = GetWorld() ? GetWorld()->GetFirstPlayerController() : nullptr)
        {
            if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
            {
                HUD->ShowDialogue(DisplayName, Line, 6.0f);
                DialogueActingRemaining = 5.5f;
            }
        }
        CurrentDialogueIndex = (CurrentDialogueIndex + 1) % ActiveDialogue->Num();
    }

    if (QuestSubsystem && SideStoryBeatAfterInteraction != NAME_None)
    {
        const bool bAlreadyTriggered = QuestSubsystem->HasStoryBeatTriggered(SideStoryBeatAfterInteraction);
        QuestSubsystem->TriggerStoryBeat(SideStoryBeatAfterInteraction);

        if (!bAlreadyTriggered && !SideStoryStartMessage.IsEmpty())
        {
            if (APlayerController* PC = GetWorld() ? GetWorld()->GetFirstPlayerController() : nullptr)
            {
                if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
                {
                    HUD->ShowAlert(SideStoryStartMessage, 4.0f);
                }
            }
        }
    }

    if (QuestSubsystem && QuestId != NAME_None && QuestStageAfterInteraction >= 0)
    {
        if (QuestSubsystem->GetQuestStage(QuestId) < QuestStageAfterInteraction)
        {
            QuestSubsystem->SetQuestStage(QuestId, QuestStageAfterInteraction);
        }
    }

    if (QuestSubsystem && NextQuestId != NAME_None)
    {
        QuestSubsystem->StartQuest(NextQuestId, NextQuestStage);
    }

    if (bFollowPlayerAfterInteraction)
    {
        bFollowingPlayer = true;
        bCompanionFollowStateResolved = true;
    }
}
