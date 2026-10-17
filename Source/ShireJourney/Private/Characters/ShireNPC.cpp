#include "ShireNPC.h"
#include "ShireQuestSubsystem.h"
#include "ShireChapterAssetStreamingSubsystem.h"
#include "ShireNPCContextSubsystem.h"
#include "ShireDialogueSubsystem.h"
#include "ShireHUD.h"
#include "ShirePlayerCharacter.h"
#include "Animation/AnimInstance.h"
#include "ShireLocomotionAnimInstance.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"
#include "UObject/SoftObjectPath.h"

AShireNPC::AShireNPC()
{
    PrimaryActorTick.bCanEverTick = true;
    GetCapsuleComponent()->SetCapsuleRadius(28.0f);
    GetCapsuleComponent()->SetCapsuleHalfHeight(60.0f);
    // Player interaction traces ECC_Visibility; UE4's Pawn preset commonly ignores
    // that channel. Opt in this interactable NPC only, keeping walking/pawn
    // collision and the non-interactable ambient crowd profiles unchanged.
    GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
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

    PrototypeCloak = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeCloak"));
    PrototypeCloak->SetupAttachment(GetCapsuleComponent());
    PrototypeCloak->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeCloak->SetVisibility(false);

    PrototypePrimaryProp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypePrimaryProp"));
    PrototypePrimaryProp->SetupAttachment(GetCapsuleComponent());
    PrototypePrimaryProp->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypePrimaryProp->SetVisibility(false);

    PrototypeSecondaryProp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeSecondaryProp"));
    PrototypeSecondaryProp->SetupAttachment(GetCapsuleComponent());
    PrototypeSecondaryProp->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeSecondaryProp->SetVisibility(false);

    PrototypeBeard = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeBeard"));
    PrototypeBeard->SetupAttachment(GetCapsuleComponent());
    PrototypeBeard->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeBeard->SetVisibility(false);

    PrototypeHeadpiece = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeHeadpiece"));
    PrototypeHeadpiece->SetupAttachment(GetCapsuleComponent());
    PrototypeHeadpiece->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PrototypeHeadpiece->SetVisibility(false);

    static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMesh(TEXT("/Engine/BasicShapes/Sphere.Sphere"));

    if (CubeMesh.Succeeded())
    {
        PrototypeTorso->SetStaticMesh(CubeMesh.Object);
        PrototypeCloak->SetStaticMesh(CubeMesh.Object);
        PrototypeSecondaryProp->SetStaticMesh(CubeMesh.Object);
        PrototypeHeadpiece->SetStaticMesh(CubeMesh.Object);
    }
    if (CylinderMesh.Succeeded())
    {
        PrototypeLeftArm->SetStaticMesh(CylinderMesh.Object);
        PrototypeRightArm->SetStaticMesh(CylinderMesh.Object);
        PrototypeLeftLeg->SetStaticMesh(CylinderMesh.Object);
        PrototypeRightLeg->SetStaticMesh(CylinderMesh.Object);
        PrototypePrimaryProp->SetStaticMesh(CylinderMesh.Object);
        PrototypeBeard->SetStaticMesh(CylinderMesh.Object);
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


namespace ShireStoryGrounding
{
    // ACharacter's actor Z is the CAPSULE CENTER, not the hobbit's foot.
    // Reject overhead roofs and use WorldStatic multi hits to resolve the
    // expected floor without touching the AI, dialogue or quest systems.
    static bool FindFloor(UWorld* World, const FVector& ExpectedFoot,
                          const AActor* IgnoreActor, float& OutFloorZ)
    {
        if (!World) return false;
        FCollisionQueryParams Query(TEXT("PES002StoryNPCFloor"), false, IgnoreActor);
        FCollisionObjectQueryParams ObjectTypes;
        ObjectTypes.AddObjectTypesToQuery(ECC_WorldStatic);
        TArray<FHitResult> Hits;
        if (!World->LineTraceMultiByObjectType(
                Hits, ExpectedFoot + FVector(0.0f, 0.0f, 900.0f),
                ExpectedFoot - FVector(0.0f, 0.0f, 2200.0f),
                ObjectTypes, Query)) return false;
        bool bFound = false;
        float LowestZ = 0.0f;
        for (const FHitResult& Hit : Hits)
        {
            const float Delta = Hit.ImpactPoint.Z - ExpectedFoot.Z;
            if (Hit.bStartPenetrating || !FMath::IsFinite(Delta) ||
                Hit.ImpactNormal.Z < 0.72f ||
                Delta < -350.0f || Delta > 160.0f)
            {
                continue;
            }
            if (!bFound || Hit.ImpactPoint.Z < LowestZ)
            {
                bFound = true;
                LowestZ = Hit.ImpactPoint.Z;
            }
        }
        if (bFound) OutFloorZ = LowestZ;
        return bFound;
    }
}

bool AShireNPC::TryApplyProductionRig(const FString& RigFolder)
{
    if (!GetMesh()) return false;
    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    const bool bShire = Quests && Quests->GetCurrentChapterId() == TEXT("P1C01");
    if (RigFolder.IsEmpty() && !bShire) return false;
    RequestedProductionRigId = RigFolder.IsEmpty() ? FName(TEXT("Frodo")) : FName(*RigFolder);
    UShireChapterAssetStreamingSubsystem* Streaming =
        GI ? GI->GetSubsystem<UShireChapterAssetStreamingSubsystem>() : nullptr;
    if (!Streaming)
    {
        GetMesh()->SetVisibility(false, true);
        return false;
    }

    USkeletalMesh* SkeletalMesh = nullptr;
    UClass* AnimClass = nullptr;
    bUsingSharedTechnicalRig = false;
    if (!Streaming->ResolveCharacterRig(RequestedProductionRigId, SkeletalMesh, AnimClass))
    {
        Streaming->RequestCharacterRig(RequestedProductionRigId);
        // In P1C01 only, a physical already-resident technical Frodo rig is
        // better than disconnected box limbs; it is NOT unique named art.
        if (!bShire || RequestedProductionRigId == TEXT("Frodo") ||
            !Streaming->ResolveCharacterRig(TEXT("Frodo"), SkeletalMesh, AnimClass))
        {
            if (bShire && RequestedProductionRigId != TEXT("Frodo"))
                Streaming->RequestCharacterRig(TEXT("Frodo"));
            GetMesh()->SetVisibility(false, true);
            return false;
        }
        bUsingSharedTechnicalRig = true;
    }
    else if (RigFolder.IsEmpty()) bUsingSharedTechnicalRig = true;

    const bool bStoryRig = SkeletalMesh && AnimClass &&
        AnimClass->IsChildOf(UShireLocomotionAnimInstance::StaticClass());
    if (!bStoryRig)
    {
        UE_LOG(LogTemp, Warning, TEXT("PES002_NAMED_RIG_NOT_READY id=%s mesh=%d anim=%d"),
            *RigFolder, SkeletalMesh ? 1 : 0, AnimClass ? 1 : 0);
        return false;
    }
    GetMesh()->SetSkeletalMesh(SkeletalMesh);
    if (!UShireLocomotionAnimInstance::AlignMeshToCapsule(
            GetMesh(), GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight()))
    {
        UE_LOG(LogTemp, Error, TEXT("SHIRE_SKELETAL_PRESENTATION_REJECT npc=%s reason=invalid-bounds"), *GetName());
        return false;
    }
    GetMesh()->SetAnimationMode(EAnimationMode::AnimationBlueprint);
    GetMesh()->SetAnimInstanceClass(AnimClass);
    GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    GetMesh()->bEnableUpdateRateOptimizations = true;
    GetMesh()->VisibilityBasedAnimTickOption =
        EVisibilityBasedAnimTickOption::OnlyTickPoseWhenRendered;
    GetMesh()->SetVisibility(true, true);
    int32 EmptyMaterialSlots = 0;
    for (int32 Slot = 0; Slot < GetMesh()->GetNumMaterials(); ++Slot)
    {
        if (!GetMesh()->GetMaterial(Slot)) ++EmptyMaterialSlots;
    }
    int32 TintCount = 0;
    if (bUsingSharedTechnicalRig)
    {
        const FString Identity = ResolveProductionCharacterId().ToString();
        FLinearColor Dye(0.30f, 0.34f, 0.16f);
        if (Identity.Equals(TEXT("Gandalf"), ESearchCase::IgnoreCase))
            Dye = FLinearColor(0.27f, 0.31f, 0.41f);
        else if (Identity.Equals(TEXT("Rosie Cotton"), ESearchCase::IgnoreCase))
            Dye = FLinearColor(0.48f, 0.24f, 0.22f);
        else if (Identity.Equals(TEXT("Bilbo"), ESearchCase::IgnoreCase))
            Dye = FLinearColor(0.48f, 0.23f, 0.13f);
        else if (Identity.Equals(TEXT("Hamfast Gamgee"), ESearchCase::IgnoreCase))
            Dye = FLinearColor(0.35f, 0.26f, 0.16f);
        else if (Identity.Equals(TEXT("Sam"), ESearchCase::IgnoreCase))
            Dye = FLinearColor(0.25f, 0.32f, 0.13f);
        else
        {
            const FLinearColor Palette[] = {
                FLinearColor(0.36f, 0.25f, 0.14f),
                FLinearColor(0.30f, 0.37f, 0.21f),
                FLinearColor(0.46f, 0.36f, 0.20f),
                FLinearColor(0.38f, 0.21f, 0.19f)};
            Dye = Palette[GetTypeHash(ResolveProductionCharacterId()) % UE_ARRAY_COUNT(Palette)];
        }
        UMaterialInterface* ShireDyeMaster = Cast<UMaterialInterface>(
            FSoftObjectPath(TEXT("/Game/Production/Materials/M_ProductionSurface.M_ProductionSurface")).ResolveObject());
        for (int32 Slot = 0; Slot < GetMesh()->GetNumMaterials(); ++Slot)
        {
            if (!ShireDyeMaster) break;
            if (UMaterialInstanceDynamic* MID = GetMesh()->CreateDynamicMaterialInstance(Slot, ShireDyeMaster))
            {
                MID->SetVectorParameterValue(TEXT("Color"), Dye);
                MID->SetScalarParameterValue(TEXT("Roughness"), 0.85f);
                MID->SetScalarParameterValue(TEXT("Metallic"), 0.0f);
                ++TintCount;
            }
        }
    }
    UE_LOG(LogTemp, Display,
        TEXT("PES002_NAMED_NPC_SKELETAL_MATERIALS id=%s slots=%d empty=%d tint=%d sharedTechnical=%d"),
        *RequestedProductionRigId.ToString(), GetMesh()->GetNumMaterials(),
        EmptyMaterialSlots, TintCount, bUsingSharedTechnicalRig ? 1 : 0);

    UE_LOG(LogTemp, Display,
        TEXT("ProductionRig: npc=%s characterId=%s rig=%s async=yes URO=on visibilityTick=rendered"),
        *DisplayName.ToString(), *ResolveProductionCharacterId().ToString(), *RigFolder);

    UStaticMeshComponent* ModularPieces[] = {
        PrototypeTorso, PrototypeHead, PrototypeHair,
        PrototypeLeftEye, PrototypeRightEye, PrototypeMouth,
        PrototypeLeftArm, PrototypeRightArm, PrototypeLeftLeg, PrototypeRightLeg,
        PrototypeCloak, PrototypePrimaryProp, PrototypeSecondaryProp,
        PrototypeBeard, PrototypeHeadpiece
    };
    for (UStaticMeshComponent* Piece : ModularPieces)
    {
        if (Piece)
        {
            Piece->SetVisibility(false, true);
            Piece->SetHiddenInGame(true, true);
            Piece->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        }
    }
    UE_LOG(LogTemp, Display,
        TEXT("PES002_STORY_SKELETAL_VISIBLE actor=%s rig=%s sharedTechnical=%d prototypeVisible=0"),
        *DisplayName.ToString(), *SkeletalMesh->GetPathName(),
        bUsingSharedTechnicalRig ? 1 : 0);
    return true;
}

void AShireNPC::ApplyPrototypeStyle()
{
    // Already imported and streamed: the verified master exposes Color and
    // Roughness parameters. BasicShapeMaterial does not guarantee either.
    UMaterialInterface* ProductionSurfaceMaterial = Cast<UMaterialInterface>(
        FSoftObjectPath(TEXT("/Game/Production/Materials/M_ProductionSurface.M_ProductionSurface")).ResolveObject());
    UMaterialInterface* BasicMaterial = ProductionSurfaceMaterial ? nullptr :
        Cast<UMaterialInterface>(
            FSoftObjectPath(TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial")).ResolveObject());
    UE_LOG(LogTemp, Display,
        TEXT("PES002_NAMED_NPC_MATERIAL_PARENT owner=AShireNPC authoredColor=%d basicFallback=%d synchronousLoad=0"),
        ProductionSurfaceMaterial ? 1 : 0, BasicMaterial ? 1 : 0);
    if (!BasicMaterial && !ProductionSurfaceMaterial)
    {
        bVisualStyleApplied = true;
        return;
    }

    const FName PresentationId = ResolveProductionCharacterId();
    const FString Name = PresentationId.IsNone() ? DisplayName.ToString() : PresentationId.ToString();

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

    // CP51: visible motion profiles keep the modular cast alive now while the same
    // actor remains ready to hand off to an imported skeletal mesh + locomotion AnimBP.
    MotionCadenceScale = 1.0f;
    MotionStrideScale = 1.0f;
    MotionIdleScale = 0.82f;
    PerformanceGestureScale = 1.0f;
    PerformanceGazeScale = 1.0f;
    PerformanceWeightScale = 1.0f;
    PerformanceComposure = 0.55f;
    if (bWizard)
    {
        MotionCadenceScale = 0.82f; MotionStrideScale = 0.86f; MotionIdleScale = 0.74f;
    }
    else if (bElf)
    {
        MotionCadenceScale = 0.90f; MotionStrideScale = 0.80f; MotionIdleScale = 0.62f;
    }
    else if (Name.Equals(TEXT("Gimli"), ESearchCase::IgnoreCase))
    {
        MotionCadenceScale = 0.96f; MotionStrideScale = 1.12f; MotionIdleScale = 0.72f;
    }
    else if (!bHuman)
    {
        MotionCadenceScale = 1.08f; MotionStrideScale = 0.92f; MotionIdleScale = 0.95f;
    }

    // Source 02 + Source 11: share animation technology, not personality.
    // These low-cost fallback acting multipliers keep named cast silhouettes readable
    // until the final skeletal/facial rigs replace the modular presentation path.
    if (Name.Equals(TEXT("Gandalf"), ESearchCase::IgnoreCase))
    {
        PerformanceGestureScale = 0.68f; PerformanceGazeScale = 0.82f;
        PerformanceWeightScale = 0.58f; PerformanceComposure = 0.90f;
    }
    else if (Name.Equals(TEXT("Saruman"), ESearchCase::IgnoreCase))
    {
        PerformanceGestureScale = 0.74f; PerformanceGazeScale = 0.72f;
        PerformanceWeightScale = 0.52f; PerformanceComposure = 0.94f;
    }
    else if (Name.Equals(TEXT("Aragorn"), ESearchCase::IgnoreCase) ||
             Name.Equals(TEXT("Strider"), ESearchCase::IgnoreCase))
    {
        PerformanceGestureScale = 0.78f; PerformanceGazeScale = 0.92f;
        PerformanceWeightScale = 0.72f; PerformanceComposure = 0.86f;
    }
    else if (Name.Equals(TEXT("Boromir"), ESearchCase::IgnoreCase))
    {
        PerformanceGestureScale = 1.16f; PerformanceGazeScale = 1.05f;
        PerformanceWeightScale = 1.08f; PerformanceComposure = 0.48f;
    }
    else if (Name.Equals(TEXT("Legolas"), ESearchCase::IgnoreCase))
    {
        PerformanceGestureScale = 0.52f; PerformanceGazeScale = 1.08f;
        PerformanceWeightScale = 0.46f; PerformanceComposure = 0.93f;
    }
    else if (Name.Equals(TEXT("Gimli"), ESearchCase::IgnoreCase))
    {
        PerformanceGestureScale = 1.10f; PerformanceGazeScale = 0.82f;
        PerformanceWeightScale = 1.18f; PerformanceComposure = 0.72f;
    }
    else if (Name.Equals(TEXT("Sam"), ESearchCase::IgnoreCase))
    {
        PerformanceGestureScale = 0.88f; PerformanceGazeScale = 1.02f;
        PerformanceWeightScale = 0.92f; PerformanceComposure = 0.66f;
    }
    else if (Name.Equals(TEXT("Merry"), ESearchCase::IgnoreCase))
    {
        PerformanceGestureScale = 0.98f; PerformanceGazeScale = 1.02f;
        PerformanceWeightScale = 0.92f; PerformanceComposure = 0.64f;
    }
    else if (Name.Equals(TEXT("Pippin"), ESearchCase::IgnoreCase))
    {
        PerformanceGestureScale = 1.08f; PerformanceGazeScale = 1.10f;
        PerformanceWeightScale = 0.96f; PerformanceComposure = 0.52f;
    }
    else if (bElf)
    {
        PerformanceGestureScale = 0.58f; PerformanceGazeScale = 0.92f;
        PerformanceWeightScale = 0.50f; PerformanceComposure = 0.91f;
    }

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
        if (UStaticMesh* Mesh = Cast<UStaticMesh>(FSoftObjectPath(AssetPath).ResolveObject()))
        {
            Component->SetStaticMesh(Mesh);
            return true;
        }
        return false;
    };

    auto TryDedicatedThenFallback = [&TryMesh](
        UStaticMeshComponent* Component,
        const TCHAR* DedicatedPath,
        const TCHAR* FallbackPath) -> bool
    {
        if (DedicatedPath && TryMesh(Component, DedicatedPath))
        {
            return true;
        }
        return FallbackPath ? TryMesh(Component, FallbackPath) : false;
    };

    const bool bGandalfVisual = Name.Equals(TEXT("Gandalf"), ESearchCase::IgnoreCase);
    const bool bHobbitVisual =
        !bWizard && !bHuman && !bElf && !Name.Equals(TEXT("Gimli"), ESearchCase::IgnoreCase);

    FString DedicatedFolder;
    if (Name.Equals(TEXT("Sam"), ESearchCase::IgnoreCase)) DedicatedFolder = TEXT("Sam");
    else if (Name.Equals(TEXT("Merry"), ESearchCase::IgnoreCase)) DedicatedFolder = TEXT("Merry");
    else if (Name.Equals(TEXT("Pippin"), ESearchCase::IgnoreCase)) DedicatedFolder = TEXT("Pippin");
    else if (Name.Equals(TEXT("Aragorn"), ESearchCase::IgnoreCase) || Name.Equals(TEXT("Strider"), ESearchCase::IgnoreCase)) DedicatedFolder = TEXT("Aragorn");
    else if (Name.Equals(TEXT("Bilbo"), ESearchCase::IgnoreCase)) DedicatedFolder = TEXT("Bilbo");
    else if (Name.Equals(TEXT("Boromir"), ESearchCase::IgnoreCase)) DedicatedFolder = TEXT("Boromir");
    else if (Name.Equals(TEXT("Legolas"), ESearchCase::IgnoreCase)) DedicatedFolder = TEXT("Legolas");
    else if (Name.Equals(TEXT("Gimli"), ESearchCase::IgnoreCase)) DedicatedFolder = TEXT("Gimli");
    else if (Name.Equals(TEXT("Arwen"), ESearchCase::IgnoreCase)) DedicatedFolder = TEXT("Arwen");
    else if (Name.Equals(TEXT("Elrond"), ESearchCase::IgnoreCase)) DedicatedFolder = TEXT("Elrond");
    else if (Name.Equals(TEXT("Haldir"), ESearchCase::IgnoreCase)) DedicatedFolder = TEXT("Haldir");
    else if (Name.Equals(TEXT("Galadriel"), ESearchCase::IgnoreCase)) DedicatedFolder = TEXT("Galadriel");
    else if (Name.Equals(TEXT("Saruman"), ESearchCase::IgnoreCase)) DedicatedFolder = TEXT("Saruman");
    else if (Name.Equals(TEXT("Barliman Butterbur"), ESearchCase::IgnoreCase)) DedicatedFolder = TEXT("Butterbur");
    else if (Name.Equals(TEXT("Gate Keeper"), ESearchCase::IgnoreCase)) DedicatedFolder = TEXT("GateKeeper");
    else if (Name.Equals(TEXT("Hamfast Gamgee"), ESearchCase::IgnoreCase)) DedicatedFolder = TEXT("Hamfast");
    else if (Name.Equals(TEXT("Rosie Cotton"), ESearchCase::IgnoreCase)) DedicatedFolder = TEXT("Rosie");
    else if (Name.Equals(TEXT("Farmer Maggot"), ESearchCase::IgnoreCase)) DedicatedFolder = TEXT("FarmerMaggot");

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
    else if (!DedicatedFolder.IsEmpty())
    {
        const FString TorsoPath = FString::Printf(
            TEXT("/Game/Production/Characters/%s/SM_%s_Torso.SM_%s_Torso"),
            *DedicatedFolder, *DedicatedFolder, *DedicatedFolder);
        const FString HeadPath = FString::Printf(
            TEXT("/Game/Production/Characters/%s/SM_%s_Head.SM_%s_Head"),
            *DedicatedFolder, *DedicatedFolder, *DedicatedFolder);
        const FString HairPath = FString::Printf(
            TEXT("/Game/Production/Characters/%s/SM_%s_Hair.SM_%s_Hair"),
            *DedicatedFolder, *DedicatedFolder, *DedicatedFolder);

        const bool bDedicatedHobbit =
            DedicatedFolder == TEXT("Sam") ||
            DedicatedFolder == TEXT("Merry") ||
            DedicatedFolder == TEXT("Pippin") ||
            DedicatedFolder == TEXT("Bilbo") ||
            DedicatedFolder == TEXT("Hamfast") ||
            DedicatedFolder == TEXT("Rosie") ||
            DedicatedFolder == TEXT("FarmerMaggot");
        const bool bDedicatedDwarf = DedicatedFolder == TEXT("Gimli");

        const TCHAR* ArmPath = bDedicatedHobbit
            ? TEXT("/Game/Production/Characters/Hobbit/SM_Hobbit_Arm.SM_Hobbit_Arm")
            : (bDedicatedDwarf
                ? TEXT("/Game/Production/Characters/Common/SM_Dwarf_Arm.SM_Dwarf_Arm")
                : TEXT("/Game/Production/Characters/Common/SM_Human_Arm.SM_Human_Arm"));
        const TCHAR* LegPath = bDedicatedHobbit
            ? TEXT("/Game/Production/Characters/Hobbit/SM_Hobbit_Leg.SM_Hobbit_Leg")
            : (bDedicatedDwarf
                ? TEXT("/Game/Production/Characters/Common/SM_Dwarf_Leg.SM_Dwarf_Leg")
                : TEXT("/Game/Production/Characters/Common/SM_Human_Leg.SM_Human_Leg"));

        bProductionVisual =
            TryMesh(PrototypeTorso, *TorsoPath) &&
            TryMesh(PrototypeHead, *HeadPath) &&
            TryMesh(PrototypeHair, *HairPath) &&
            TryMesh(PrototypeLeftArm, ArmPath) &&
            TryMesh(PrototypeLeftLeg, LegPath);
        TryMesh(PrototypeRightArm, ArmPath);
        TryMesh(PrototypeRightLeg, LegPath);
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
    else if (bElf)
    {
        bProductionVisual =
            TryMesh(PrototypeTorso, TEXT("/Game/Production/Characters/Common/SM_Elf_Torso.SM_Elf_Torso")) &&
            TryMesh(PrototypeHead, TEXT("/Game/Production/Characters/Common/SM_Elf_Head.SM_Elf_Head")) &&
            TryMesh(PrototypeHair, TEXT("/Game/Production/Characters/Common/SM_Elf_Hair.SM_Elf_Hair")) &&
            TryMesh(PrototypeLeftArm, TEXT("/Game/Production/Characters/Common/SM_Human_Arm.SM_Human_Arm")) &&
            TryMesh(PrototypeLeftLeg, TEXT("/Game/Production/Characters/Common/SM_Human_Leg.SM_Human_Leg"));
        TryMesh(PrototypeRightArm, TEXT("/Game/Production/Characters/Common/SM_Human_Arm.SM_Human_Arm"));
        TryMesh(PrototypeRightLeg, TEXT("/Game/Production/Characters/Common/SM_Human_Leg.SM_Human_Leg"));
    }
    else if (Name.Equals(TEXT("Gimli"), ESearchCase::IgnoreCase))
    {
        bProductionVisual =
            TryMesh(PrototypeTorso, TEXT("/Game/Production/Characters/Common/SM_Dwarf_Torso.SM_Dwarf_Torso")) &&
            TryMesh(PrototypeHead, TEXT("/Game/Production/Characters/Common/SM_Dwarf_Head.SM_Dwarf_Head")) &&
            TryMesh(PrototypeLeftArm, TEXT("/Game/Production/Characters/Common/SM_Dwarf_Arm.SM_Dwarf_Arm")) &&
            TryMesh(PrototypeLeftLeg, TEXT("/Game/Production/Characters/Common/SM_Dwarf_Leg.SM_Dwarf_Leg"));
        TryMesh(PrototypeRightArm, TEXT("/Game/Production/Characters/Common/SM_Dwarf_Arm.SM_Dwarf_Arm"));
        TryMesh(PrototypeRightLeg, TEXT("/Game/Production/Characters/Common/SM_Dwarf_Leg.SM_Dwarf_Leg"));
        TryMesh(PrototypeHair, TEXT("/Game/Production/Characters/Common/SM_Human_Hair.SM_Human_Hair"));
    }
    else if (bHuman || bWizard)
    {
        bProductionVisual =
            TryMesh(PrototypeTorso, TEXT("/Game/Production/Characters/Common/SM_Human_Torso.SM_Human_Torso")) &&
            TryMesh(PrototypeHead, TEXT("/Game/Production/Characters/Common/SM_Human_Head.SM_Human_Head")) &&
            TryMesh(PrototypeHair, TEXT("/Game/Production/Characters/Common/SM_Human_Hair.SM_Human_Hair")) &&
            TryMesh(PrototypeLeftArm, TEXT("/Game/Production/Characters/Common/SM_Human_Arm.SM_Human_Arm")) &&
            TryMesh(PrototypeLeftLeg, TEXT("/Game/Production/Characters/Common/SM_Human_Leg.SM_Human_Leg"));
        TryMesh(PrototypeRightArm, TEXT("/Game/Production/Characters/Common/SM_Human_Arm.SM_Human_Arm"));
        TryMesh(PrototypeRightLeg, TEXT("/Game/Production/Characters/Common/SM_Human_Leg.SM_Human_Leg"));
    }

    bUsingProductionVisual = bProductionVisual;
    if (bProductionVisual)
    {
        PrototypeTorso->SetRelativeScale3D(FVector(1));
        PrototypeHead->SetRelativeScale3D(FVector(1));
        PrototypeHair->SetRelativeScale3D(FVector(1));
        PrototypeLeftArm->SetRelativeScale3D(FVector(1));
        PrototypeRightArm->SetRelativeScale3D(FVector(1));
        PrototypeLeftLeg->SetRelativeScale3D(FVector(1));
        PrototypeRightLeg->SetRelativeScale3D(FVector(1));

        // Production heads are authored in centimeter scale. Keep the facial
        // markers on the actual face rather than using BasicShape-sphere offsets.
        const float FaceX = 16.5f;
        const float FaceY = 6.2f;
        PrototypeLeftEye->SetRelativeLocation(FVector(FaceX, -FaceY, 4.5f));
        PrototypeRightEye->SetRelativeLocation(FVector(FaceX, FaceY, 4.5f));
        PrototypeLeftEye->SetRelativeScale3D(FVector(0.026f, 0.020f, 0.035f));
        PrototypeRightEye->SetRelativeScale3D(FVector(0.026f, 0.020f, 0.035f));
        PrototypeMouth->SetRelativeLocation(FVector(FaceX + 0.5f, 0.0f, -4.0f));
        PrototypeMouth->SetRelativeScale3D(FVector(0.012f, 0.050f, 0.010f));
    }

    auto ApplySurface = [this, BasicMaterial, ProductionSurfaceMaterial](
        UStaticMeshComponent* Component,
        const FLinearColor& Color,
        float Roughness,
        float Metallic)
    {
        if (!Component)
        {
            return;
        }

        UMaterialInterface* Parent = ProductionSurfaceMaterial ?
            ProductionSurfaceMaterial : BasicMaterial;
        if (!Parent)
        {
            return;
        }

        UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(Parent, this);
        if (MID)
        {
            MID->SetVectorParameterValue(TEXT("Color"), Color);
            MID->SetScalarParameterValue(TEXT("Roughness"), FMath::Clamp(Roughness, 0.0f, 1.0f));
            MID->SetScalarParameterValue(TEXT("Metallic"), FMath::Clamp(Metallic, 0.0f, 1.0f));
            Component->SetMaterial(0, MID);
        }
    };

    auto ApplyColor = [&ApplySurface](UStaticMeshComponent* Component, const FLinearColor& Color)
    {
        ApplySurface(Component, Color, 0.84f, 0.0f);
    };

    ApplySurface(PrototypeTorso, Coat, 0.82f, 0.0f);
    ApplySurface(PrototypeHead, Skin, 0.54f, 0.0f);
    ApplySurface(PrototypeHair, Hair, 0.72f, 0.0f);
    ApplySurface(PrototypeLeftArm, Coat * 0.95f, 0.80f, 0.0f);
    ApplySurface(PrototypeRightArm, Coat * 0.95f, 0.80f, 0.0f);
    ApplySurface(PrototypeLeftLeg, Trousers, 0.84f, 0.0f);
    ApplySurface(PrototypeRightLeg, Trousers, 0.84f, 0.0f);
    ApplySurface(PrototypeLeftEye, FLinearColor(0.045f, 0.035f, 0.025f), 0.24f, 0.0f);
    ApplySurface(PrototypeRightEye, FLinearColor(0.045f, 0.035f, 0.025f), 0.24f, 0.0f);
    ApplySurface(PrototypeMouth, FLinearColor(0.20f, 0.055f, 0.045f), 0.56f, 0.0f);

    auto HideIdentityPiece = [](UStaticMeshComponent* Component)
    {
        if (Component)
        {
            Component->SetVisibility(false);
            Component->SetRelativeRotation(FRotator::ZeroRotator);
        }
    };

    HideIdentityPiece(PrototypeCloak);
    HideIdentityPiece(PrototypePrimaryProp);
    HideIdentityPiece(PrototypeSecondaryProp);
    HideIdentityPiece(PrototypeBeard);
    HideIdentityPiece(PrototypeHeadpiece);

    const bool bProductionCloakMesh = TryMesh(
        PrototypeCloak,
        TEXT("/Game/Production/Characters/Common/SM_ProductionCloak.SM_ProductionCloak"));
    const bool bProductionSwordMesh = TryMesh(
        PrototypePrimaryProp,
        TEXT("/Game/Production/Characters/Common/SM_ProductionSword.SM_ProductionSword"));
    const TCHAR* ProductionShieldPath =
        TEXT("/Game/Production/Characters/Common/SM_ProductionShield.SM_ProductionShield");
    const TCHAR* ProductionBowPath =
        TEXT("/Game/Production/Characters/Common/SM_ProductionBow.SM_ProductionBow");
    const TCHAR* ProductionAxePath =
        TEXT("/Game/Production/Characters/Common/SM_ProductionAxe.SM_ProductionAxe");

    const bool bSam = Name.Equals(TEXT("Sam"), ESearchCase::IgnoreCase);
    const bool bMerry = Name.Equals(TEXT("Merry"), ESearchCase::IgnoreCase);
    const bool bPippin = Name.Equals(TEXT("Pippin"), ESearchCase::IgnoreCase);
    const bool bBoromir = Name.Equals(TEXT("Boromir"), ESearchCase::IgnoreCase);
    const bool bLegolas = Name.Equals(TEXT("Legolas"), ESearchCase::IgnoreCase);
    const bool bGimli = Name.Equals(TEXT("Gimli"), ESearchCase::IgnoreCase);
    const bool bSaruman = Name.Equals(TEXT("Saruman"), ESearchCase::IgnoreCase);
    const bool bGaladriel = Name.Equals(TEXT("Galadriel"), ESearchCase::IgnoreCase);
    const bool bElrond = Name.Equals(TEXT("Elrond"), ESearchCase::IgnoreCase);
    const bool bArwen = Name.Equals(TEXT("Arwen"), ESearchCase::IgnoreCase);

    FLinearColor Leather(0.16f, 0.09f, 0.045f);
    FLinearColor Steel(0.34f, 0.36f, 0.37f);
    FLinearColor Wood(0.23f, 0.12f, 0.055f);
    FLinearColor DarkGreen(0.10f, 0.20f, 0.10f);
    FLinearColor ElfGreen(0.18f, 0.31f, 0.20f);
    FLinearColor WhiteCloth(0.68f, 0.69f, 0.65f);

    if (bSam)
    {
        const bool bSamSwordMesh = TryDedicatedThenFallback(
            PrototypePrimaryProp,
            TEXT("/Game/Production/Characters/Sam/SM_Sam_Sword.SM_Sam_Sword"),
            TEXT("/Game/Production/Characters/Common/SM_ProductionSword.SM_ProductionSword"));
        PrototypePrimaryProp->SetVisibility(true);
        PrototypePrimaryPropBase = FVector(3.0f, 27.0f, -5.0f);
        PrototypePrimaryPropRotation = FRotator(-8.0f, 0.0f, 10.0f);
        PrototypePrimaryProp->SetRelativeLocation(PrototypePrimaryPropBase);
        PrototypePrimaryProp->SetRelativeRotation(PrototypePrimaryPropRotation);
        PrototypePrimaryProp->SetRelativeScale3D(bSamSwordMesh ? FVector(0.92f) : FVector(0.62f));
        ApplySurface(PrototypePrimaryProp, Steel, 0.34f, 0.78f);

        const bool bPackMesh = TryDedicatedThenFallback(
            PrototypeSecondaryProp,
            TEXT("/Game/Production/Characters/Sam/SM_Sam_Pack.SM_Sam_Pack"),
            TEXT("/Game/Production/Characters/Frodo/SM_Frodo_Satchel.SM_Frodo_Satchel"));
        PrototypeSecondaryProp->SetVisibility(true);
        PrototypeSecondaryProp->SetRelativeLocation(FVector(-7.0f, 20.0f, -4.0f));
        PrototypeSecondaryProp->SetRelativeScale3D(
            bPackMesh ? FVector(0.88f) : FVector(0.12f, 0.18f, 0.18f));
        PrototypeSecondaryProp->SetRelativeRotation(FRotator(0.0f, 12.0f, 8.0f));
        ApplySurface(PrototypeSecondaryProp, Leather, 0.66f, 0.0f);
    }
    else if (bMerry || bPippin)
    {
        const TCHAR* HobbitCloakPath = bMerry
            ? TEXT("/Game/Production/Characters/Merry/SM_Merry_Cloak.SM_Merry_Cloak")
            : TEXT("/Game/Production/Characters/Pippin/SM_Pippin_Cloak.SM_Pippin_Cloak");
        const bool bDedicatedHobbitCloak = TryMesh(PrototypeCloak, HobbitCloakPath);
        PrototypeCloak->SetVisibility(true);
        PrototypeCloakBase = FVector(-10.0f, 0.0f, -5.0f);
        PrototypeCloak->SetRelativeLocation(PrototypeCloakBase);
        PrototypeCloak->SetRelativeScale3D(
            bDedicatedHobbitCloak
                ? FVector(0.86f)
                : (bProductionCloakMesh
                    ? FVector(0.72f)
                    : (bMerry ? FVector(0.12f, 0.34f, 0.42f) : FVector(0.11f, 0.32f, 0.38f))));
        ApplyColor(PrototypeCloak, bMerry
            ? FLinearColor(0.26f, 0.20f, 0.08f)
            : FLinearColor(0.12f, 0.26f, 0.16f));

        const TCHAR* HobbitSwordPath = bMerry
            ? TEXT("/Game/Production/Characters/Merry/SM_Merry_Sword.SM_Merry_Sword")
            : TEXT("/Game/Production/Characters/Pippin/SM_Pippin_Sword.SM_Pippin_Sword");
        const bool bDedicatedHobbitSword = TryDedicatedThenFallback(
            PrototypePrimaryProp,
            HobbitSwordPath,
            TEXT("/Game/Production/Characters/Common/SM_ProductionSword.SM_ProductionSword"));
        PrototypePrimaryProp->SetVisibility(true);
        PrototypePrimaryPropBase = FVector(3.0f, 27.0f, -6.0f);
        PrototypePrimaryPropRotation = FRotator(-9.0f, 0.0f, bMerry ? 7.0f : 12.0f);
        PrototypePrimaryProp->SetRelativeLocation(PrototypePrimaryPropBase);
        PrototypePrimaryProp->SetRelativeRotation(PrototypePrimaryPropRotation);
        PrototypePrimaryProp->SetRelativeScale3D(bDedicatedHobbitSword ? FVector(0.94f) : FVector(0.58f));
        ApplySurface(PrototypePrimaryProp, Steel, 0.34f, 0.78f);
    }
    else if (bRanger)
    {
        const bool bAragornCloak = TryDedicatedThenFallback(
            PrototypeCloak,
            TEXT("/Game/Production/Characters/Aragorn/SM_Aragorn_Cloak.SM_Aragorn_Cloak"),
            TEXT("/Game/Production/Characters/Common/SM_ProductionCloak.SM_ProductionCloak"));
        PrototypeCloak->SetVisibility(true);
        PrototypeCloakBase = FVector(-11.0f, 0.0f, 7.0f);
        PrototypeCloak->SetRelativeLocation(PrototypeCloakBase);
        PrototypeCloak->SetRelativeScale3D(
            bAragornCloak ? FVector(0.94f) :
            (bProductionCloakMesh ? FVector(1.0f) : FVector(0.14f, 0.45f, 0.68f)));
        ApplySurface(PrototypeCloak, DarkGreen, 0.86f, 0.0f);

        const bool bAragornSword = TryDedicatedThenFallback(
            PrototypePrimaryProp,
            TEXT("/Game/Production/Characters/Aragorn/SM_Aragorn_Sword.SM_Aragorn_Sword"),
            TEXT("/Game/Production/Characters/Common/SM_ProductionSword.SM_ProductionSword"));
        PrototypePrimaryProp->SetVisibility(true);
        PrototypePrimaryPropBase = FVector(2.0f, 31.0f, 5.0f);
        PrototypePrimaryPropRotation = FRotator(0.0f, 0.0f, 7.0f);
        PrototypePrimaryProp->SetRelativeLocation(PrototypePrimaryPropBase);
        PrototypePrimaryProp->SetRelativeRotation(PrototypePrimaryPropRotation);
        PrototypePrimaryProp->SetRelativeScale3D(
            bAragornSword ? FVector(0.92f) :
            (bProductionSwordMesh ? FVector(1.0f) : FVector(0.045f, 0.045f, 0.78f)));
        ApplySurface(PrototypePrimaryProp, Steel, 0.34f, 0.78f);

        const bool bBackBow = TryDedicatedThenFallback(
            PrototypeSecondaryProp,
            TEXT("/Game/Production/Characters/Aragorn/SM_Aragorn_Bow.SM_Aragorn_Bow"),
            ProductionBowPath);
        PrototypeSecondaryProp->SetVisibility(true);
        PrototypeSecondaryProp->SetRelativeLocation(FVector(-11.0f, -18.0f, 21.0f));
        PrototypeSecondaryProp->SetRelativeRotation(FRotator(0.0f, 0.0f, -18.0f));
        PrototypeSecondaryProp->SetRelativeScale3D(
            bBackBow ? FVector(0.92f) : FVector(0.04f, 0.04f, 0.72f));
        ApplySurface(PrototypeSecondaryProp, Wood, 0.78f, 0.0f);
    }
    else if (bBoromir)
    {
        const bool bBoromirCloak = TryDedicatedThenFallback(
            PrototypeCloak,
            TEXT("/Game/Production/Characters/Boromir/SM_Boromir_Cloak.SM_Boromir_Cloak"),
            TEXT("/Game/Production/Characters/Common/SM_ProductionCloak.SM_ProductionCloak"));
        PrototypeCloak->SetVisibility(true);
        PrototypeCloakBase = FVector(-12.0f, 0.0f, 8.0f);
        PrototypeCloak->SetRelativeLocation(PrototypeCloakBase);
        PrototypeCloak->SetRelativeScale3D(
            bBoromirCloak ? FVector(0.94f) :
            (bProductionCloakMesh ? FVector(1.0f) : FVector(0.15f, 0.47f, 0.66f)));
        ApplyColor(PrototypeCloak, FLinearColor(0.28f, 0.10f, 0.08f));

        const bool bBoromirSword = TryDedicatedThenFallback(
            PrototypePrimaryProp,
            TEXT("/Game/Production/Characters/Boromir/SM_Boromir_Sword.SM_Boromir_Sword"),
            TEXT("/Game/Production/Characters/Common/SM_ProductionSword.SM_ProductionSword"));
        PrototypePrimaryProp->SetVisibility(true);
        PrototypePrimaryPropBase = FVector(2.0f, 31.0f, 6.0f);
        PrototypePrimaryPropRotation = FRotator(0.0f, 0.0f, 5.0f);
        PrototypePrimaryProp->SetRelativeLocation(PrototypePrimaryPropBase);
        PrototypePrimaryProp->SetRelativeRotation(PrototypePrimaryPropRotation);
        PrototypePrimaryProp->SetRelativeScale3D(
            bBoromirSword ? FVector(0.92f) :
            (bProductionSwordMesh ? FVector(1.0f) : FVector(0.05f, 0.05f, 0.82f)));
        ApplySurface(PrototypePrimaryProp, Steel, 0.34f, 0.78f);

        const bool bShieldMesh = TryDedicatedThenFallback(
            PrototypeSecondaryProp,
            TEXT("/Game/Production/Characters/Boromir/SM_Boromir_Shield.SM_Boromir_Shield"),
            ProductionShieldPath);
        PrototypeSecondaryProp->SetVisibility(true);
        PrototypeSecondaryProp->SetRelativeLocation(FVector(-7.0f, -24.0f, 16.0f));
        PrototypeSecondaryProp->SetRelativeRotation(FRotator(0.0f, 14.0f, -8.0f));
        PrototypeSecondaryProp->SetRelativeScale3D(
            bShieldMesh ? FVector(0.92f) : FVector(0.08f, 0.34f, 0.34f));
        ApplySurface(PrototypeSecondaryProp, FLinearColor(0.30f, 0.22f, 0.14f), 0.62f, 0.10f);
    }
    else if (bLegolas)
    {
        const bool bLegolasCloak = TryDedicatedThenFallback(
            PrototypeCloak,
            TEXT("/Game/Production/Characters/Legolas/SM_Legolas_Cloak.SM_Legolas_Cloak"),
            TEXT("/Game/Production/Characters/Common/SM_ProductionCloak.SM_ProductionCloak"));
        PrototypeCloak->SetVisibility(true);
        PrototypeCloakBase = FVector(-10.0f, 0.0f, 8.0f);
        PrototypeCloak->SetRelativeLocation(PrototypeCloakBase);
        PrototypeCloak->SetRelativeScale3D(
            bLegolasCloak ? FVector(0.92f) :
            (bProductionCloakMesh ? FVector(0.94f) : FVector(0.11f, 0.40f, 0.61f)));
        ApplyColor(PrototypeCloak, ElfGreen);

        const bool bProductionBow = TryDedicatedThenFallback(
            PrototypePrimaryProp,
            TEXT("/Game/Production/Characters/Legolas/SM_Legolas_Bow.SM_Legolas_Bow"),
            ProductionBowPath);
        PrototypePrimaryProp->SetVisibility(true);
        PrototypePrimaryPropBase = FVector(-6.0f, 26.0f, 22.0f);
        PrototypePrimaryPropRotation = FRotator(0.0f, 0.0f, 20.0f);
        PrototypePrimaryProp->SetRelativeLocation(PrototypePrimaryPropBase);
        PrototypePrimaryProp->SetRelativeRotation(PrototypePrimaryPropRotation);
        PrototypePrimaryProp->SetRelativeScale3D(
            bProductionBow ? FVector(1.0f) : FVector(0.035f, 0.035f, 0.72f));
        ApplySurface(PrototypePrimaryProp, Wood, 0.78f, 0.0f);

        const bool bKnifeMesh = TryDedicatedThenFallback(
            PrototypeSecondaryProp,
            TEXT("/Game/Production/Characters/Legolas/SM_Legolas_WhiteKnife.SM_Legolas_WhiteKnife"),
            TEXT("/Game/Production/Characters/Common/SM_ProductionSword.SM_ProductionSword"));
        PrototypeSecondaryProp->SetVisibility(true);
        PrototypeSecondaryProp->SetRelativeLocation(FVector(-9.0f, -21.0f, 22.0f));
        PrototypeSecondaryProp->SetRelativeRotation(FRotator(0.0f, 0.0f, -28.0f));
        PrototypeSecondaryProp->SetRelativeScale3D(
            bKnifeMesh ? FVector(0.55f) : FVector(0.09f, 0.20f, 0.52f));
        ApplySurface(PrototypeSecondaryProp, Steel, 0.34f, 0.78f);
    }
    else if (bGimli)
    {
        const bool bProductionDwarfBeard = TryDedicatedThenFallback(
            PrototypeBeard,
            TEXT("/Game/Production/Characters/Gimli/SM_Gimli_Beard.SM_Gimli_Beard"),
            TEXT("/Game/Production/Characters/Common/SM_Dwarf_Beard.SM_Dwarf_Beard"));
        PrototypeBeard->SetVisibility(true);
        PrototypeBeard->SetRelativeLocation(FVector(13.0f, 0.0f, 33.0f));
        PrototypeBeard->SetRelativeScale3D(
            bProductionDwarfBeard ? FVector(1.0f) : FVector(0.13f, 0.13f, 0.30f));
        PrototypeBeard->SetRelativeRotation(
            bProductionDwarfBeard ? FRotator::ZeroRotator : FRotator(90.0f, 0.0f, 0.0f));
        ApplySurface(PrototypeBeard, FLinearColor(0.44f, 0.20f, 0.07f), 0.74f, 0.0f);

        const bool bProductionAxe = TryDedicatedThenFallback(
            PrototypePrimaryProp,
            TEXT("/Game/Production/Characters/Gimli/SM_Gimli_Axe.SM_Gimli_Axe"),
            ProductionAxePath);
        PrototypePrimaryProp->SetVisibility(true);
        PrototypePrimaryPropBase = FVector(4.0f, 34.0f, -1.0f);
        PrototypePrimaryPropRotation = FRotator(-10.0f, 0.0f, 12.0f);
        PrototypePrimaryProp->SetRelativeLocation(PrototypePrimaryPropBase);
        PrototypePrimaryProp->SetRelativeRotation(PrototypePrimaryPropRotation);
        PrototypePrimaryProp->SetRelativeScale3D(
            bProductionAxe ? FVector(1.0f) : FVector(0.065f, 0.065f, 0.62f));
        ApplySurface(PrototypePrimaryProp, FLinearColor(0.26f, 0.22f, 0.18f), 0.38f, 0.72f);

        const bool bSecondAxe = TryDedicatedThenFallback(
            PrototypeSecondaryProp,
            TEXT("/Game/Production/Characters/Gimli/SM_Gimli_Axe.SM_Gimli_Axe"),
            ProductionAxePath);
        PrototypeSecondaryProp->SetVisibility(true);
        PrototypeSecondaryProp->SetRelativeLocation(FVector(-8.0f, -27.0f, 25.0f));
        PrototypeSecondaryProp->SetRelativeRotation(FRotator(0.0f, 0.0f, -24.0f));
        PrototypeSecondaryProp->SetRelativeScale3D(
            bSecondAxe ? FVector(0.72f) : FVector(0.28f, 0.06f, 0.16f));
        ApplySurface(PrototypeSecondaryProp, Steel, 0.34f, 0.78f);

        const bool bGimliHelmet = TryMesh(
            PrototypeHeadpiece,
            TEXT("/Game/Production/Characters/Gimli/SM_Gimli_Helmet.SM_Gimli_Helmet"));
        if (bGimliHelmet)
        {
            PrototypeHeadpiece->SetVisibility(true);
            PrototypeHeadpiece->SetRelativeLocation(FVector(-2.0f, 0.0f, PrototypeHairBaseZ + 7.0f));
            PrototypeHeadpiece->SetRelativeRotation(FRotator::ZeroRotator);
            PrototypeHeadpiece->SetRelativeScale3D(FVector(0.92f));
            ApplySurface(PrototypeHeadpiece, FLinearColor(0.24f, 0.20f, 0.16f), 0.42f, 0.66f);
        }
    }
    else if (bWizard)
    {
        const bool bGandalfStaff = bGandalfVisual && TryMesh(
            PrototypePrimaryProp,
            TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Staff.SM_Gandalf_Staff"));
        PrototypePrimaryProp->SetVisibility(true);
        PrototypePrimaryPropBase = FVector(3.0f, 34.0f, 3.0f);
        PrototypePrimaryPropRotation = FRotator::ZeroRotator;
        PrototypePrimaryProp->SetRelativeLocation(PrototypePrimaryPropBase);
        PrototypePrimaryProp->SetRelativeRotation(PrototypePrimaryPropRotation);
        PrototypePrimaryProp->SetRelativeScale3D(
            bGandalfStaff ? FVector(1.0f) : FVector(0.045f, 0.045f, 0.92f));
        ApplySurface(PrototypePrimaryProp, bSaruman ? FLinearColor(0.60f, 0.58f, 0.52f) : Wood, bSaruman ? 0.58f : 0.78f, bSaruman ? 0.12f : 0.0f);

        const bool bGandalfBeard = bGandalfVisual && TryMesh(
            PrototypeBeard,
            TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Beard.SM_Gandalf_Beard"));
        PrototypeBeard->SetVisibility(true);
        PrototypeBeard->SetRelativeLocation(FVector(13.0f, 0.0f, 49.0f));
        PrototypeBeard->SetRelativeScale3D(
            bGandalfBeard ? FVector(1.0f) : FVector(0.10f, 0.10f, 0.30f));
        PrototypeBeard->SetRelativeRotation(
            bGandalfBeard ? FRotator::ZeroRotator : FRotator(90.0f, 0.0f, 0.0f));
        ApplySurface(PrototypeBeard, bSaruman
            ? FLinearColor(0.84f, 0.82f, 0.76f)
            : FLinearColor(0.68f, 0.66f, 0.60f), 0.74f, 0.0f);

        if (bGandalfVisual)
        {
            const bool bGandalfHat = TryMesh(
                PrototypeHeadpiece,
                TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Hat.SM_Gandalf_Hat"));
            PrototypeHeadpiece->SetVisibility(true);
            PrototypeHeadpiece->SetRelativeLocation(FVector(-1.0f, 0.0f, PrototypeHairBaseZ + 10.0f));
            PrototypeHeadpiece->SetRelativeScale3D(
                bGandalfHat ? FVector(1.0f) : FVector(0.18f, 0.42f, 0.22f));
            ApplySurface(PrototypeHeadpiece, FLinearColor(0.28f, 0.29f, 0.27f), 0.84f, 0.0f);

            const bool bGandalfCloak = TryMesh(
                PrototypeCloak,
                TEXT("/Game/Production/Characters/Gandalf/SM_Gandalf_Cloak.SM_Gandalf_Cloak"));
            PrototypeCloak->SetVisibility(true);
            PrototypeCloakBase = FVector(-12.0f, 0.0f, 8.0f);
            PrototypeCloak->SetRelativeLocation(PrototypeCloakBase);
            PrototypeCloak->SetRelativeScale3D(
                bGandalfCloak ? FVector(1.0f) : FVector(0.14f, 0.46f, 0.72f));
            ApplySurface(PrototypeCloak, FLinearColor(0.30f, 0.31f, 0.29f), 0.86f, 0.0f);
        }
    }
    else if (bGaladriel || bElrond || bArwen)
    {
        PrototypeCloak->SetVisibility(true);
        PrototypeCloakBase = FVector(-10.0f, 0.0f, 9.0f);
        PrototypeCloak->SetRelativeLocation(PrototypeCloakBase);
        PrototypeCloak->SetRelativeScale3D(
            bProductionCloakMesh ? FVector(0.96f) : FVector(0.10f, 0.40f, 0.70f));
        ApplyColor(PrototypeCloak, bGaladriel ? WhiteCloth : ElfGreen);

        PrototypeHeadpiece->SetVisibility(true);
        PrototypeHeadpiece->SetRelativeLocation(FVector(-1.0f, 0.0f, PrototypeHairBaseZ + 7.0f));
        PrototypeHeadpiece->SetRelativeScale3D(bGaladriel
            ? FVector(0.12f, 0.34f, 0.055f)
            : FVector(0.10f, 0.28f, 0.045f));
        ApplySurface(PrototypeHeadpiece, bGaladriel
            ? FLinearColor(0.62f, 0.66f, 0.60f)
            : FLinearColor(0.34f, 0.42f, 0.26f), 0.36f, 0.78f);
    }

    FString RigFolder = DedicatedFolder;
    if (RigFolder.IsEmpty() && bGandalfVisual)
    {
        RigFolder = TEXT("Gandalf");
    }
    bUsingSkeletalProductionRig = TryApplyProductionRig(RigFolder);

    bVisualStyleApplied = true;
}

void AShireNPC::UpdatePrototypeAnimation(float DeltaSeconds)
{
    if (bUsingSkeletalProductionRig)
    {
        return;
    }

    float Swing = 0.0f;
    float Bob = 0.0f;
    float IdleBreath = 0.0f;
    float IdleSway = 0.0f;
    float WeightShift = 0.0f;
    if (bPrototypeMoving)
    {
        PrototypeWalkPhase += DeltaSeconds * 8.0f * MotionCadenceScale *
            PrototypeMovementCadenceScale;
        Swing = FMath::Sin(PrototypeWalkPhase) * 25.0f * MotionStrideScale;
        Bob = FMath::Abs(FMath::Sin(PrototypeWalkPhase * 2.0f)) * 1.2f * MotionStrideScale;
    }
    else
    {
        PrototypeIdlePhase += DeltaSeconds * (1.15f + 0.04f * static_cast<float>(GetUniqueID() % 7));
        IdleBreath = FMath::Sin(PrototypeIdlePhase) * 0.70f * MotionIdleScale;
        IdleSway = FMath::Sin(PrototypeIdlePhase * 0.55f) * 1.6f * MotionIdleScale;
        WeightShift = FMath::Sin(PrototypeIdlePhase * 0.43f + ResolveCompanionSlot() * 0.71f) *
            0.85f * PerformanceWeightScale;
    }

    const float DialogueGesture = DialogueActingRemaining > 0.0f
        ? FMath::Sin(ActingPhase * 0.72f) * 7.0f * PerformanceGestureScale
        : 0.0f;
    const float BlendSpeed = 10.0f;
    if (PrototypeLeftArm)
    {
        PrototypeLeftArm->SetRelativeRotation(FMath::RInterpTo(
            PrototypeLeftArm->GetRelativeRotation(), FRotator(Swing + IdleSway, 0.0f, 0.0f), DeltaSeconds, BlendSpeed));
    }
    if (PrototypeRightArm)
    {
        PrototypeRightArm->SetRelativeRotation(FMath::RInterpTo(
            PrototypeRightArm->GetRelativeRotation(), FRotator(-Swing - IdleSway + DialogueGesture, 0.0f, 0.0f), DeltaSeconds, BlendSpeed));
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
            FVector(0.0f, WeightShift, PrototypeTorsoBaseZ + Bob + IdleBreath), DeltaSeconds, 12.0f));
    }
    if (PrototypeHead)
    {
        PrototypeHead->SetRelativeLocation(FMath::VInterpTo(
            PrototypeHead->GetRelativeLocation(),
            FVector(0.0f, 0.0f, PrototypeHeadBaseZ + Bob + IdleBreath * 0.65f), DeltaSeconds, 12.0f));
    }
    if (PrototypeHair)
    {
        PrototypeHair->SetRelativeLocation(FMath::VInterpTo(
            PrototypeHair->GetRelativeLocation(),
            FVector(-1.0f, 0.0f, PrototypeHairBaseZ + Bob + IdleBreath * 0.65f), DeltaSeconds, 12.0f));
    }

    if (PrototypeCloak && PrototypeCloak->IsVisible())
    {
        const float CloakPitch = bPrototypeMoving ? -4.0f - FMath::Abs(Swing) * 0.08f : -1.5f;
        PrototypeCloak->SetRelativeLocation(FMath::VInterpTo(
            PrototypeCloak->GetRelativeLocation(),
            PrototypeCloakBase + FVector(0.0f, 0.0f, Bob * 0.45f),
            DeltaSeconds,
            8.0f));
        PrototypeCloak->SetRelativeRotation(FMath::RInterpTo(
            PrototypeCloak->GetRelativeRotation(),
            FRotator(CloakPitch, 0.0f, bPrototypeMoving ? Swing * 0.05f : 0.0f),
            DeltaSeconds,
            5.0f));
    }

    if (PrototypePrimaryProp && PrototypePrimaryProp->IsVisible())
    {
        PrototypePrimaryProp->SetRelativeLocation(FMath::VInterpTo(
            PrototypePrimaryProp->GetRelativeLocation(),
            PrototypePrimaryPropBase + FVector(0.0f, 0.0f, Bob * 0.30f),
            DeltaSeconds,
            10.0f));
        PrototypePrimaryProp->SetRelativeRotation(FMath::RInterpTo(
            PrototypePrimaryProp->GetRelativeRotation(),
            PrototypePrimaryPropRotation + FRotator(
                bPrototypeMoving ? -Swing * 0.12f : 0.0f,
                0.0f,
                bPrototypeMoving ? Swing * 0.04f : 0.0f),
            DeltaSeconds,
            7.0f));
    }

    if (PrototypeBeard && PrototypeBeard->IsVisible())
    {
        PrototypeBeard->SetRelativeRotation(FMath::RInterpTo(
            PrototypeBeard->GetRelativeRotation(),
            FRotator(90.0f + (bPrototypeMoving ? Swing * 0.04f : 0.0f), 0.0f, 0.0f),
            DeltaSeconds,
            5.0f));
    }
}


void AShireNPC::UpdatePrototypeActing(float DeltaSeconds)
{
    if (bUsingSkeletalProductionRig)
    {
        return;
    }

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

    const float EyeOpenZ = bUsingProductionVisual ? 0.035f : 0.13f;
    const float EyeClosedZ = bUsingProductionVisual ? 0.007f : 0.025f;
    const float EyeZ = BlinkRemaining > 0.0f ? EyeClosedZ : EyeOpenZ;
    const FVector EyeScale = bUsingProductionVisual
        ? FVector(0.026f, 0.020f, EyeZ)
        : FVector(0.12f, 0.09f, EyeZ);
    PrototypeLeftEye->SetRelativeScale3D(EyeScale);
    PrototypeRightEye->SetRelativeScale3D(EyeScale);

    DialogueActingRemaining = FMath::Max(0.0f, DialogueActingRemaining - DeltaSeconds);
    if (DialogueActingRemaining > 0.0f)
    {
        ActingPhase += DeltaSeconds * 13.0f;
        const float MouthOpen = bUsingProductionVisual
            ? (0.010f + FMath::Abs(FMath::Sin(ActingPhase)) * 0.020f)
            : (0.045f + FMath::Abs(FMath::Sin(ActingPhase)) * 0.085f);
        PrototypeMouth->SetRelativeScale3D(
            bUsingProductionVisual
                ? FVector(0.012f, 0.050f, MouthOpen)
                : FVector(0.11f, 0.16f, MouthOpen));
    }
    else
    {
        PrototypeMouth->SetRelativeScale3D(
            bUsingProductionVisual
                ? FVector(0.012f, 0.050f, 0.010f)
                : FVector(0.11f, 0.16f, 0.045f));
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
                const float MaxGaze = FMath::Lerp(22.0f, 38.0f, PerformanceGazeScale);
                const float ClampedYaw = FMath::Clamp(
                    RelativeYaw, -MaxGaze, MaxGaze) * PerformanceGazeScale;

                float EmotionalPitch = 0.0f;
                if (CachedEmotionalState == TEXT("GRIEF") ||
                    CachedEmotionalState == TEXT("AFRAID") ||
                    CachedEmotionalState == TEXT("WEARY"))
                {
                    EmotionalPitch = -3.8f * (1.0f - 0.35f * PerformanceComposure);
                }
                else if (CachedEmotionalState == TEXT("ALERT") ||
                         CachedEmotionalState == TEXT("ANGRY"))
                {
                    EmotionalPitch = 2.6f * (1.0f - 0.25f * PerformanceComposure);
                }

                PrototypeHead->SetRelativeRotation(FMath::RInterpTo(
                    PrototypeHead->GetRelativeRotation(),
                    FRotator(EmotionalPitch, ClampedYaw, 0.0f),
                    DeltaSeconds,
                    DialogueActingRemaining > 0.0f ? 7.0f : 3.0f));
                return;
            }
        }
    }

    const float AmbientLookYaw =
        (!bPrototypeMoving && DialogueActingRemaining <= 0.0f)
            ? FMath::Sin(PrototypeIdlePhase * 0.31f + static_cast<float>(GetUniqueID() % 13)) *
                5.0f * PerformanceGazeScale
            : 0.0f;
    const float PressurePitch =
        !bPrototypeMoving
            ? FMath::Lerp(0.0f, 2.2f, FMath::Clamp(CachedWorldPressure, 0.0f, 1.0f)) *
                (1.0f - 0.35f * PerformanceComposure)
            : 0.0f;
    PrototypeHead->SetRelativeRotation(FMath::RInterpTo(
        PrototypeHead->GetRelativeRotation(),
        FRotator(PressurePitch, AmbientLookYaw, 0.0f),
        DeltaSeconds,
        2.4f));
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
    const float CohesionScale = FMath::Lerp(
        1.12f, 0.72f, FMath::Clamp(CachedWorldPressure, 0.0f, 1.0f));
    const float BackDistance =
        FollowDistance * CohesionScale + Row * (FormationSpacing * 0.85f * CohesionScale);
    const float SideDistance =
        FormationSpacing * CohesionScale * (1.0f + 0.15f * Row) * Side;

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

    if (FollowActivationStoryBeat != NAME_None)
    {
        const bool bHasIndividualRecruitment =
            QuestSubsystem->HasStoryBeatTriggered(FollowActivationStoryBeat);
        const bool bLegacySharedStageReached =
            QuestId != NAME_None
            && QuestStageAfterInteraction >= 0
            && QuestSubsystem->GetQuestStage(QuestId) > QuestStageAfterInteraction;
        bFollowingPlayer = bHasIndividualRecruitment || bLegacySharedStageReached;
        return;
    }

    if (QuestId == NAME_None || QuestStageAfterInteraction < 0)
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

FName AShireNPC::ResolveProductionCharacterId() const
{
    if (!ProductionCharacterId.IsNone())
    {
        return ProductionCharacterId;
    }

    const FString Name = DisplayName.ToString();
    if (Name.Equals(TEXT("Gandalf"), ESearchCase::IgnoreCase)) return TEXT("Gandalf");
    if (Name.Equals(TEXT("Bilbo"), ESearchCase::IgnoreCase)) return TEXT("Bilbo");
    if (Name.Equals(TEXT("Sam"), ESearchCase::IgnoreCase)) return TEXT("Sam");
    if (Name.Equals(TEXT("Merry"), ESearchCase::IgnoreCase)) return TEXT("Merry");
    if (Name.Equals(TEXT("Pippin"), ESearchCase::IgnoreCase)) return TEXT("Pippin");
    if (Name.Equals(TEXT("Aragorn"), ESearchCase::IgnoreCase) || Name.Equals(TEXT("Strider"), ESearchCase::IgnoreCase)) return TEXT("Aragorn");
    if (Name.Equals(TEXT("Boromir"), ESearchCase::IgnoreCase)) return TEXT("Boromir");
    if (Name.Equals(TEXT("Legolas"), ESearchCase::IgnoreCase)) return TEXT("Legolas");
    if (Name.Equals(TEXT("Gimli"), ESearchCase::IgnoreCase)) return TEXT("Gimli");
    if (Name.Equals(TEXT("Arwen"), ESearchCase::IgnoreCase)) return TEXT("Arwen");
    return NAME_None;
}

FName AShireNPC::ResolveCanonicalProfileId() const
{
    const UGameInstance* GI = GetGameInstance();
    const UShireNPCContextSubsystem* Context =
        GI ? GI->GetSubsystem<UShireNPCContextSubsystem>() : nullptr;
    if (!Context)
    {
        return NAME_None;
    }

    return Context->ResolveCanonicalProfileId(FName(*DisplayName.ToString()));
}

void AShireNPC::RefreshLivingContext(float DeltaSeconds)
{
    LivingContextRefreshRemaining = FMath::Max(0.0f, LivingContextRefreshRemaining - DeltaSeconds);
    if (LivingContextRefreshRemaining > 0.0f)
    {
        return;
    }

    LivingContextRefreshRemaining =
        0.75f + 0.11f * static_cast<float>(ResolveCompanionSlot() % 5);

    const UGameInstance* GI = GetGameInstance();
    const UShireNPCContextSubsystem* Context =
        GI ? GI->GetSubsystem<UShireNPCContextSubsystem>() : nullptr;
    if (!Context || !Context->IsDataReady())
    {
        return;
    }

    const FName ProfileId = ResolveCanonicalProfileId();
    const FName NewMood = Context->GetRegionalWorldMood();
    CachedWorldPressure = Context->GetRegionalPressure();
    CachedEmotionalState = ProfileId != NAME_None
        ? Context->GetProfileEmotionalState(ProfileId)
        : FName(TEXT("CALM"));

    if (CachedWorldMood != NAME_None && NewMood != CachedWorldMood && bFollowingPlayer)
    {
        const float Stagger = 4.0f + 1.6f * static_cast<float>(ResolveCompanionSlot());
        BanterCooldownRemaining = BanterCooldownRemaining < 0.0f
            ? Stagger
            : FMath::Min(BanterCooldownRemaining, Stagger);
    }

    CachedWorldMood = NewMood;
}

void AShireNPC::UpdateCompanionBanter(float DeltaSeconds)
{
    if (!bFollowingPlayer || !GetWorld())
    {
        return;
    }

    if (BanterCooldownRemaining < 0.0f)
    {
        BanterCooldownRemaining =
            38.0f + ResolveCompanionSlot() * 10.0f + CachedWorldPressure * 24.0f;
    }
    else
    {
        BanterCooldownRemaining = FMath::Max(0.0f, BanterCooldownRemaining - DeltaSeconds);
    }

    if (BanterCooldownRemaining > 0.0f)
    {
        return;
    }

    UGameInstance* GI = GetGameInstance();
    UShireNPCContextSubsystem* Context =
        GI ? GI->GetSubsystem<UShireNPCContextSubsystem>() : nullptr;
    UShireDialogueSubsystem* Dialogue =
        GI ? GI->GetSubsystem<UShireDialogueSubsystem>() : nullptr;
    UShireQuestSubsystem* Quests =
        GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;

    if (!Context || !Dialogue || !Quests || Dialogue->IsDialoguePlaying() ||
        !Context->IsLogicalWorldContextCommitted() ||
        Context->IsDangerStateActive())
    {
        BanterCooldownRemaining = 8.0f;
        return;
    }

    APawn* PlayerPawn = GetWorld()->GetFirstPlayerController()
        ? GetWorld()->GetFirstPlayerController()->GetPawn()
        : nullptr;
    if (!PlayerPawn || FVector::DistSquared2D(GetActorLocation(), PlayerPawn->GetActorLocation()) >
        FMath::Square(950.0f))
    {
        BanterCooldownRemaining = 10.0f;
        return;
    }

    const FName ProfileId = ResolveCanonicalProfileId();
    if (ProfileId == NAME_None || !Context->HasKnowledgeTag(ProfileId, TEXT("FELLOWSHIP_MEMBER")))
    {
        BanterCooldownRemaining = 90.0f;
        return;
    }

    AShireNPC* BestPartner = nullptr;
    float BestDistanceSq = FMath::Square(700.0f);
    for (TActorIterator<AShireNPC> It(GetWorld()); It; ++It)
    {
        AShireNPC* Candidate = *It;
        if (!Candidate || Candidate == this || !Candidate->bFollowingPlayer)
        {
            continue;
        }
        const FName CandidateProfile = Candidate->ResolveCanonicalProfileId();
        if (CandidateProfile == NAME_None ||
            !Context->HasKnowledgeTag(CandidateProfile, TEXT("FELLOWSHIP_MEMBER")))
        {
            continue;
        }

        const float DistanceSq = FVector::DistSquared2D(GetActorLocation(), Candidate->GetActorLocation());
        if (DistanceSq < BestDistanceSq)
        {
            BestDistanceSq = DistanceSq;
            BestPartner = Candidate;
        }
    }

    const FName ListenerProfileId =
        BestPartner ? BestPartner->ResolveCanonicalProfileId() : FName(TEXT("PLAYER_FRODO"));
    const FShireBoundedDialogueResult First = Context->SelectBoundedDialogue(
        ProfileId,
        ListenerProfileId,
        TEXT("COMPANION_BANTER"),
        Quests->GetCurrentChapterId());

    TArray<FShireDialogueLine> Lines;
    if (First.bValid)
    {
        FShireDialogueLine Line;
        Line.Speaker = DisplayName;
        Line.Subtitle = First.Text;
        Line.VoiceCue = First.VoiceCue;
        Line.Duration = 4.0f;
        Lines.Add(Line);
    }

    if (BestPartner && First.bValid)
    {
        const FShireBoundedDialogueResult Response = Context->SelectBoundedDialogue(
            ListenerProfileId,
            ProfileId,
            TEXT("COMPANION_BANTER"),
            Quests->GetCurrentChapterId());
        if (Response.bValid)
        {
            FShireDialogueLine Line;
            Line.Speaker = BestPartner->DisplayName;
            Line.Subtitle = Response.Text;
            Line.VoiceCue = Response.VoiceCue;
            Line.Duration = 4.0f;
            Lines.Add(Line);
            BestPartner->DialogueActingRemaining = 7.5f;
        }
    }

    if (Lines.Num() > 0)
    {
        Dialogue->PlayDynamicSequence(Lines, First.VariantId);
        DialogueActingRemaining = Lines.Num() > 1 ? 7.5f : 4.0f;
    }

    BanterCooldownRemaining =
        58.0f + ResolveCompanionSlot() * 12.0f + CachedWorldPressure * 30.0f;
}

void AShireNPC::BeginPlay()
{
    Super::BeginPlay();

    // Foot-safe authored spawn snap: one original probe, then bounded
    // 150/300/450cm rings. No quest trigger, route or authoring transform moves.
    if (GetWorld() && GetCapsuleComponent())
    {
        const FVector Initial = GetActorLocation();
        const float HalfHeight = GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
        const FCollisionShape Capsule = FCollisionShape::MakeCapsule(
            GetCapsuleComponent()->GetScaledCapsuleRadius(), HalfHeight);
        FCollisionQueryParams ClearQuery(TEXT("PES002StoryNPCBodyClear"), false, this);
        int32 Probes = 0;
        float ChosenDistance = -1.0f;
        float ChosenFloor = 0.0f;
        for (int32 Ring = 0; Ring <= 3 && !bStoryGroundSupportProven; ++Ring)
        {
            const int32 Directions = Ring == 0 ? 1 : 8;
            const float Radius = 150.0f * Ring;
            for (int32 AngleIndex = 0; AngleIndex < Directions; ++AngleIndex)
            {
                const float Angle = 2.0f * PI * AngleIndex / Directions;
                const FVector Offset = Ring == 0 ? FVector::ZeroVector :
                    FVector(FMath::Cos(Angle) * Radius, FMath::Sin(Angle) * Radius, 0.0f);
                const FVector Probe = Initial + Offset - FVector(0.0f, 0.0f, HalfHeight);
                float FloorZ = 0.0f;
                ++Probes;
                if (!ShireStoryGrounding::FindFloor(GetWorld(), Probe, this, FloorZ)) continue;
                const FVector Target(Initial.X + Offset.X, Initial.Y + Offset.Y,
                                     FloorZ + HalfHeight + 2.0f);
                if (GetWorld()->OverlapBlockingTestByChannel(
                        Target, FQuat::Identity, ECC_Pawn, Capsule, ClearQuery)) continue;
                if (!Initial.Equals(Target, 0.5f))
                    SetActorLocation(Target, false, nullptr, ETeleportType::TeleportPhysics);
                const FVector Actual = GetActorLocation();
                bStoryGroundSupportProven = FVector::DistSquared2D(Actual, Target) < 1.0f &&
                    FMath::Abs(Actual.Z - HalfHeight - (FloorZ + 2.0f)) < 3.0f;
                if (bStoryGroundSupportProven)
                {
                    ChosenDistance = Radius;
                    ChosenFloor = FloorZ;
                    break;
                }
            }
        }
        if (bStoryGroundSupportProven)
            UE_LOG(LogTemp, Display,
                TEXT("PES002_STORY_NPC_GROUND npc=%s floorZ=%.1f beforeFootZ=%.1f afterFootZ=%.1f radialCm=%.1f probes=%d grounded=1"),
                *GetName(), ChosenFloor, Initial.Z - HalfHeight,
                GetActorLocation().Z - HalfHeight, ChosenDistance, Probes);
        else
            UE_LOG(LogTemp, Warning,
                TEXT("PES002_STORY_NPC_GROUND_REJECT npc=%s expectedFootZ=%.1f probes=%d reason=no-clear-support-within-450"),
                *GetName(), Initial.Z - HalfHeight, Probes);
    }

    if (UGameInstance* GI = GetGameInstance())
    {
        if (UShireChapterAssetStreamingSubsystem* Streaming =
                GI->GetSubsystem<UShireChapterAssetStreamingSubsystem>())
        {
            Streaming->OnCharacterRigReady.AddUObject(
                this,
                &AShireNPC::HandleProductionRigReady);
        }
    }
}

void AShireNPC::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (UGameInstance* GI = GetGameInstance())
    {
        if (UShireChapterAssetStreamingSubsystem* Streaming =
                GI->GetSubsystem<UShireChapterAssetStreamingSubsystem>())
        {
            Streaming->OnCharacterRigReady.RemoveAll(this);
        }
    }

    Super::EndPlay(EndPlayReason);
}

void AShireNPC::HandleProductionRigReady(FName CharacterId)
{
    if (RequestedProductionRigId.IsNone() ||
        (CharacterId != RequestedProductionRigId &&
         !(CharacterId == TEXT("Frodo") && !bUsingSkeletalProductionRig)))
        return;
    // Avoid recursion when already-resident bundles broadcast synchronously.
    // The next Tick performs the one final binding after the async callback.
    bVisualStyleApplied = false;
}

void AShireNPC::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (!bVisualStyleApplied)
    {
        ApplyPrototypeStyle();
    }

    if (const AShirePlayerCharacter* Player =
            Cast<AShirePlayerCharacter>(UGameplayStatics::GetPlayerPawn(this, 0)))
    {
        if (!Player->IsGameplayWorldCommitted())
        {
            return;
        }
    }

    if (!bCompanionFollowStateResolved)
    {
        RestoreCompanionFollowState();
    }

    RefreshLivingContext(DeltaSeconds);
    bPrototypeMoving = false;
    PrototypeMovementCadenceScale = FMath::FInterpTo(
        PrototypeMovementCadenceScale, 1.0f, DeltaSeconds, 6.0f);

    // Preserve full-rate follow/dialogue responsiveness while throttling only
    // stationary named NPCs that are far from the player.
    if (GetWorld())
    {
        APlayerController* DistancePC = GetWorld()->GetFirstPlayerController();
        APawn* DistancePawn = DistancePC ? DistancePC->GetPawn() : nullptr;
        if (DistancePawn && !bFollowingPlayer && DialogueActingRemaining <= 0.0f)
        {
            const float PlayerDistance =
                FVector::Dist2D(GetActorLocation(), DistancePawn->GetActorLocation());
            PrimaryActorTick.TickInterval =
                PlayerDistance > 4200.0f ? 0.22f :
                (PlayerDistance > 2200.0f ? 0.10f : 0.0f);
        }
        else
        {
            PrimaryActorTick.TickInterval = 0.0f;
        }
    }

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

            const float Pressure = FMath::Clamp(CachedWorldPressure, 0.0f, 1.0f);
            const float EffectiveAcceptance = FMath::Lerp(
                FollowAcceptanceRadius * 1.15f, FollowAcceptanceRadius * 0.72f, Pressure);

            if (Distance > TeleportCatchUpDistance)
            {
                FVector SafeTarget = Target;
                SafeTarget.Z = PlayerPawn->GetActorLocation().Z;

                // Use AActor's encroachment-aware teleport instead of forcing the
                // capsule into scenery when a companion has fallen far behind.
                TeleportTo(SafeTarget, GetActorRotation(), false, false);
            }
            else if (Distance > EffectiveAcceptance)
            {
                const float PressureSpeed = FMath::Lerp(1.0f, 1.28f, Pressure);
                const float EffectiveSpeed =
                    FollowSpeed * PressureSpeed * (Distance > CatchUpDistance ? 2.0f : 1.0f);
                const float MaxStep = EffectiveSpeed * DeltaSeconds;
                const FVector Step = ToTarget.GetSafeNormal() * FMath::Min(MaxStep, Distance - EffectiveAcceptance);
                const FVector MoveStart = GetActorLocation();

                FHitResult ForwardHit;
                AddActorWorldOffset(Step, true, &ForwardHit);
                if (ForwardHit.IsValidBlockingHit() && ForwardHit.Time < 1.0f)
                {
                    FVector SlideStep = FVector::VectorPlaneProject(
                        Step * (1.0f - ForwardHit.Time), ForwardHit.Normal);
                    SlideStep.Z = 0.0f;
                    if (!SlideStep.IsNearlyZero())
                    {
                        AddActorWorldOffset(SlideStep, true);
                    }
                }

                FVector ActualStep = GetActorLocation() - MoveStart;
                ActualStep.Z = 0.0f;
                bPrototypeMoving = !ActualStep.IsNearlyZero(0.5f);

                if (bPrototypeMoving)
                {
                    const float ActualSpeed = ActualStep.Size() /
                        FMath::Max(DeltaSeconds, KINDA_SMALL_NUMBER);
                    const float TargetCadenceScale = FMath::Clamp(
                        ActualSpeed / FMath::Max(FollowSpeed, 1.0f), 0.55f, 1.65f);
                    PrototypeMovementCadenceScale = FMath::FInterpTo(
                        PrototypeMovementCadenceScale, TargetCadenceScale, DeltaSeconds, 8.0f);

                    const FRotator DesiredRotation = ActualStep.Rotation();
                    SetActorRotation(FMath::RInterpTo(GetActorRotation(), DesiredRotation, DeltaSeconds, 7.0f));
                }
            }
        }
    }

    UpdateCompanionBanter(DeltaSeconds);
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
    AShirePlayerCharacter* Player = Cast<AShirePlayerCharacter>(Interactor);
    if (!Player || !Player->IsGameplayWorldCommitted())
    {
        return;
    }

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

    bool bUsedBoundedDialogue = false;
    bool bAuthoredDialogueSequenceCompleted = false;
    const FName CanonicalProfileId = ResolveCanonicalProfileId();
    UShireNPCContextSubsystem* Context =
        GI ? GI->GetSubsystem<UShireNPCContextSubsystem>() : nullptr;
    UShireDialogueSubsystem* Dialogue =
        GI ? GI->GetSubsystem<UShireDialogueSubsystem>() : nullptr;

    // Story/quest-authored lines remain authoritative. Free-standing and companion
    // interactions may consume bounded memory-aware variants.
    if (QuestSubsystem && Context && Dialogue && CanonicalProfileId != NAME_None &&
        (QuestId == NAME_None || QuestStageAfterInteraction < 0))
    {
        FName Intent = TEXT("GREETING");
        const FName Mood = Context->GetRegionalWorldMood();
        const bool bFellowship =
            Context->HasKnowledgeTag(CanonicalProfileId, TEXT("FELLOWSHIP_MEMBER"));

        if (Context->IsDangerStateActive())
        {
            Intent = TEXT("DANGER_WARNING");
        }
        else if (Mood == TEXT("SUSPICIOUS_TOWN") ||
                 Mood == TEXT("PURSUED_WILDERNESS") ||
                 Mood == TEXT("DEAD_CITY_DREAD") ||
                 Mood == TEXT("GRIEF_AND_REFUGE") ||
                 Mood == TEXT("FELLOWSHIP_FRACTURE") ||
                 Mood == TEXT("WAR_CORRUPTION"))
        {
            Intent = TEXT("STORY_REACTION");
        }
        else if (bFellowship)
        {
            Intent = TEXT("TRAVEL_COMMENT");
        }
        else if (QuestSubsystem->HasNamedNPCMemory(CanonicalProfileId, TEXT("PLAYER_INTERACTED")) &&
                 Context->HasKnowledgeTag(CanonicalProfileId, TEXT("MAIN_STORY_CONTEXT")))
        {
            Intent = TEXT("STORY_REACTION");
        }

        FShireBoundedDialogueResult Result = Context->SelectBoundedDialogue(
            CanonicalProfileId,
            TEXT("PLAYER_FRODO"),
            Intent,
            QuestSubsystem->GetCurrentChapterId());

        if (!Result.bValid && Intent != TEXT("GREETING"))
        {
            Result = Context->SelectBoundedDialogue(
                CanonicalProfileId,
                TEXT("PLAYER_FRODO"),
                TEXT("GREETING"),
                QuestSubsystem->GetCurrentChapterId());
        }
        if (Result.bValid)
        {
            FShireDialogueLine DynamicLine;
            DynamicLine.Speaker = DisplayName;
            DynamicLine.Subtitle = Result.Text;
            DynamicLine.VoiceCue = Result.VoiceCue;
            DynamicLine.Duration = 5.0f;
            bUsedBoundedDialogue = Dialogue->PlayDynamicLine(DynamicLine, Result.VariantId);
            DialogueActingRemaining = bUsedBoundedDialogue ? 4.8f : DialogueActingRemaining;
        }
    }

    if (!bUsedBoundedDialogue)
    {
        const TArray<FText>* ActiveDialogue = ResolveDialogueLines(QuestSubsystem);
        if (ActiveDialogue && ActiveDialogue->Num() > 0)
        {
            const int32 DialogueIndex = CurrentDialogueIndex % ActiveDialogue->Num();
            const FText& Line = (*ActiveDialogue)[DialogueIndex];
            bAuthoredDialogueSequenceCompleted = DialogueIndex == ActiveDialogue->Num() - 1;
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
    }

    if (QuestSubsystem && CanonicalProfileId != NAME_None)
    {
        QuestSubsystem->RememberNamedNPCEvent(CanonicalProfileId, TEXT("PLAYER_INTERACTED"), 55);
        QuestSubsystem->AdjustNamedNPCRelationship(CanonicalProfileId, TEXT("PLAYER_FRODO"), 1);
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

    if (QuestSubsystem && NextQuestId != NAME_None &&
        (!bCompleteDialogueBeforeNextQuest || bAuthoredDialogueSequenceCompleted))
    {
        QuestSubsystem->StartQuest(NextQuestId, NextQuestStage);
    }

    if (bFollowPlayerAfterInteraction)
    {
        bFollowingPlayer = true;
        bCompanionFollowStateResolved = true;
    }
}
