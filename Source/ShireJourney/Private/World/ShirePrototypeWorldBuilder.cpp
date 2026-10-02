#include "ShirePrototypeWorldBuilder.h"

#include "BlackRiderPrototype.h"
#include "ShireNPC.h"
#include "ShireQuestSubsystem.h"
#include "ShireQuestTrigger.h"
#include "ShireTraversalChallenge.h"
#include "WorldDetailCluster.h"

#include "Components/BoxComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Components/HierarchicalInstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Components/SkyAtmosphereComponent.h"
#include "Components/SkyLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/ExponentialHeightFog.h"
#include "Engine/PostProcessVolume.h"
#include "Engine/SkyLight.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/TextRenderActor.h"
#include "EngineUtils.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"
#include "UObject/SoftObjectPath.h"

namespace ShireLayout
{
    // CP28 starts the visual-production transition. World-space labels remain available
    // in code for debugging, but are hidden by default so the playable view reads as a world.
    constexpr bool ShowPrototypeWorldLabels = false;
    // UE units are centimeters. These anchors intentionally keep the village compact
    // while making the eastward journey feel like travel rather than a single arena.
    constexpr float HobbitonExitX = 1500.0f;
    constexpr float FieldsX = 7600.0f;
    constexpr float WoodedRoadX = 14500.0f;
    constexpr float FerryX = 23500.0f;
}

namespace
{
    UStaticMesh* ResolveResidentStaticMesh(const TCHAR* AssetPath)
    {
        return AssetPath
            ? Cast<UStaticMesh>(FSoftObjectPath(AssetPath).ResolveObject())
            : nullptr;
    }

    UMaterialInterface* ResolveResidentMaterial(const TCHAR* AssetPath)
    {
        return AssetPath
            ? Cast<UMaterialInterface>(FSoftObjectPath(AssetPath).ResolveObject())
            : nullptr;
    }
}

AShirePrototypeWorldBuilder::AShirePrototypeWorldBuilder()
{
    PrimaryActorTick.bCanEverTick = false;

    RuntimeRoot = CreateDefaultSubobject<USceneComponent>(TEXT("RuntimeRoot"));
    RootComponent = RuntimeRoot;

    GrassInstances = CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("GrassInstances"));
    GrassInstances->SetupAttachment(RuntimeRoot);
    GrassInstances->SetMobility(EComponentMobility::Movable);
    GrassInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    GrassInstances->SetCastShadow(false);

    EastFieldRowInstances = CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("EastFieldRowInstances"));
    EastFieldRowInstances->SetupAttachment(RuntimeRoot);
    EastFieldRowInstances->SetMobility(EComponentMobility::Movable);
    EastFieldRowInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    EastFieldRowInstances->SetGenerateOverlapEvents(false);
    EastFieldRowInstances->SetCastShadow(false);

    FlowerInstances = CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("FlowerInstances"));
    FlowerInstances->SetupAttachment(RuntimeRoot);
    FlowerInstances->SetMobility(EComponentMobility::Movable);
    FlowerInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    FlowerInstances->SetCastShadow(false);

    ShrubInstances = CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("ShrubInstances"));
    ShrubInstances->SetupAttachment(RuntimeRoot);
    ShrubInstances->SetMobility(EComponentMobility::Movable);
    ShrubInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    ShrubInstances->SetCastShadow(false);

    DistantTreeTrunkInstances = CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("DistantTreeTrunkInstances"));
    DistantTreeTrunkInstances->SetupAttachment(RuntimeRoot);
    DistantTreeTrunkInstances->SetMobility(EComponentMobility::Movable);
    DistantTreeTrunkInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    DistantTreeTrunkInstances->SetCastShadow(false);

    DistantTreeCanopyInstances = CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("DistantTreeCanopyInstances"));
    DistantTreeCanopyInstances->SetupAttachment(RuntimeRoot);
    DistantTreeCanopyInstances->SetMobility(EComponentMobility::Movable);
    DistantTreeCanopyInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    DistantTreeCanopyInstances->SetCastShadow(false);

    RockInstances = CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("RockInstances"));
    RockInstances->SetupAttachment(RuntimeRoot);
    RockInstances->SetMobility(EComponentMobility::Movable);
    RockInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    RockInstances->SetCastShadow(false);

    PathStoneInstances = CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("PathStoneInstances"));
    PathStoneInstances->SetupAttachment(RuntimeRoot);
    PathStoneInstances->SetMobility(EComponentMobility::Movable);
    PathStoneInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    PathStoneInstances->SetCastShadow(false);

    GeographyHillInstances = CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("GeographyHillInstances"));
    GeographyHillInstances->SetupAttachment(RuntimeRoot);
    GeographyHillInstances->SetMobility(EComponentMobility::Movable);
    GeographyHillInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    GeographyHillInstances->SetCastShadow(false);

    GeographySlopeInstances = CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("GeographySlopeInstances"));
    GeographySlopeInstances->SetupAttachment(RuntimeRoot);
    GeographySlopeInstances->SetMobility(EComponentMobility::Movable);
    GeographySlopeInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    GeographySlopeInstances->SetCastShadow(false);

    GeographyRiverBankInstances = CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(TEXT("GeographyRiverBankInstances"));
    GeographyRiverBankInstances->SetupAttachment(RuntimeRoot);
    GeographyRiverBankInstances->SetMobility(EComponentMobility::Movable);
    GeographyRiverBankInstances->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    GeographyRiverBankInstances->SetCastShadow(false);

    // Explicit cull bands keep the first production world pass bounded on the
    // i7/8 GB/~2 GB VRAM target. These are starting budgets, not acceptance proof.
    GrassInstances->SetCullDistances(1200, 5200);
    EastFieldRowInstances->SetCullDistances(900, 6500);
    FlowerInstances->SetCullDistances(800, 3200);
    ShrubInstances->SetCullDistances(1500, 6500);
    DistantTreeTrunkInstances->SetCullDistances(5000, 19000);
    DistantTreeCanopyInstances->SetCullDistances(5000, 19000);
    RockInstances->SetCullDistances(2200, 9000);
    PathStoneInstances->SetCullDistances(900, 5000);
    GeographyHillInstances->SetCullDistances(16000, 32000);
    GeographySlopeInstances->SetCullDistances(12000, 28000);
    GeographyRiverBankInstances->SetCullDistances(9000, 26000);

    static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeAsset(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereAsset(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderAsset(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> ConeAsset(TEXT("/Engine/BasicShapes/Cone.Cone"));
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> BasicMaterialAsset(TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));

    CubeMesh = CubeAsset.Succeeded() ? CubeAsset.Object : nullptr;
    SphereMesh = SphereAsset.Succeeded() ? SphereAsset.Object : nullptr;
    CylinderMesh = CylinderAsset.Succeeded() ? CylinderAsset.Object : nullptr;
    ConeMesh = ConeAsset.Succeeded() ? ConeAsset.Object : nullptr;
    BasicMaterial = BasicMaterialAsset.Succeeded() ? BasicMaterialAsset.Object : nullptr;

    if (ConeMesh)
    {
        GrassInstances->SetStaticMesh(ConeMesh);
    }
    if (SphereMesh)
    {
        FlowerInstances->SetStaticMesh(SphereMesh);
        ShrubInstances->SetStaticMesh(SphereMesh);
        DistantTreeCanopyInstances->SetStaticMesh(SphereMesh);
        RockInstances->SetStaticMesh(SphereMesh);
    }
    if (CylinderMesh)
    {
        DistantTreeTrunkInstances->SetStaticMesh(CylinderMesh);
    }
    if (CubeMesh)
    {
        PathStoneInstances->SetStaticMesh(CubeMesh);
    }
}

void AShirePrototypeWorldBuilder::BeginPlay()
{
    Super::BeginPlay();

    ProductionTreeTrunkMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShTreeTrunk.SM_ShTreeTrunk"));
    ProductionTreeCanopyMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShTreeCanopy.SM_ShTreeCanopy"));
    ProductionRockMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShRock.SM_ShRock"));
    ProductionCrateMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShCrate.SM_ShCrate"));
    ProductionSignpostMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShSignpost.SM_ShSignpost"));
    ProductionBarrelMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShBarrel.SM_ShBarrel"));
    ProductionGroundBlockMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShGroundBlock.SM_ShGroundBlock"));
    ProductionRoadBlockMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShRoadBlock.SM_ShRoadBlock"));
    ProductionTurfMoundMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShTurfMound.SM_ShTurfMound"));
    ProductionHedgeMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShHedge.SM_ShHedge"));
    ProductionShrubMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShShrub.SM_ShShrub"));
    ProductionPathStoneMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShPathStone.SM_ShPathStone"));
    ProductionGrassClumpMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShGrassClump.SM_ShGrassClump"));
    ProductionFenceSegmentMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShFenceSegment.SM_ShFenceSegment"));
    ProductionHobbitFacadeMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShHobbitFacade.SM_ShHobbitFacade"));
    ProductionCartMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShCart.SM_ShCart"));
    ProductionBenchMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShBench.SM_ShBench"));
    ProductionMillWheelMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShMillWheel.SM_ShMillWheel"));
    ProductionLanternMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShLantern.SM_ShLantern"));
    ProductionCottageHouseMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShCottageHouse.SM_ShCottageHouse"));
    ProductionMillHouseMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShMillHouse.SM_ShMillHouse"));
    ProductionStoneBridgeMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShStoneBridge.SM_ShStoneBridge"));
    ProductionWellMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShWell.SM_ShWell"));
    ProductionMarketStallMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShMarketStall.SM_ShMarketStall"));
    ProductionStoneWallMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShStoneWall.SM_ShStoneWall"));
    ProductionFarmGateMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShFarmGate.SM_ShFarmGate"));
    ProductionHaystackMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShHaystack.SM_ShHaystack"));
    ProductionFlowerBoxMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShFlowerBox.SM_ShFlowerBox"));
    ProductionLampPostMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShLampPost.SM_ShLampPost"));
    ProductionPicnicTableMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShPicnicTable.SM_ShPicnicTable"));
    ProductionLoadedCartMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Shire/SM_ShCartLoaded.SM_ShCartLoaded"));
    ProductionCommonTerracedHillMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonTerracedHill.SM_CommonTerracedHill"));
    ProductionCommonVillageSlopeMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonVillageSlope.SM_CommonVillageSlope"));
    ProductionCommonRiverBankMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonRiverBank.SM_CommonRiverBank"));
    ProductionCommonBoulderClusterMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonBoulderCluster.SM_CommonBoulderCluster"));
    ProductionCommonBroadleafTreeMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonBroadleafTree.SM_CommonBroadleafTree"));
    ProductionCommonFallenLogMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonFallenLog.SM_CommonFallenLog"));
    ProductionCommonDryStoneWallMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonDryStoneWall.SM_CommonDryStoneWall"));
    ProductionCommonPathMarkerMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonPathMarker.SM_CommonPathMarker"));
    ProductionCommonVillageFenceMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonVillageFence.SM_CommonVillageFence"));
    ProductionCommonWoodPileMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonWoodPile.SM_CommonWoodPile"));
    ProductionCommonFernClumpMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonFernClump.SM_CommonFernClump"));
    ProductionCommonReedClusterMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonReedCluster.SM_CommonReedCluster"));
    ProductionCommonFootbridgeMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonFootbridge.SM_CommonFootbridge"));
    ProductionCommonRiverBoatMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonRiverBoat.SM_CommonRiverBoat"));
    ProductionCommonRopePostMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonRopePost.SM_CommonRopePost"));
    ProductionCommonRopeCoilMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonRopeCoil.SM_CommonRopeCoil"));
    ProductionCommonMarketCanopyMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonMarketCanopy.SM_CommonMarketCanopy"));
    ProductionWaterMaterial = ResolveResidentMaterial(
        TEXT("/Game/Production/Materials/M_ProductionWater.M_ProductionWater"));

    if (GeographyHillInstances && ProductionCommonTerracedHillMesh)
    {
        GeographyHillInstances->SetStaticMesh(ProductionCommonTerracedHillMesh);
    }
    if (GeographySlopeInstances && ProductionCommonVillageSlopeMesh)
    {
        GeographySlopeInstances->SetStaticMesh(ProductionCommonVillageSlopeMesh);
    }
    if (GeographyRiverBankInstances && ProductionCommonRiverBankMesh)
    {
        GeographyRiverBankInstances->SetStaticMesh(ProductionCommonRiverBankMesh);
    }

    if (ProductionTreeTrunkMesh) DistantTreeTrunkInstances->SetStaticMesh(ProductionTreeTrunkMesh);
    if (ProductionTreeCanopyMesh) DistantTreeCanopyInstances->SetStaticMesh(ProductionTreeCanopyMesh);
    if (ProductionRockMesh) RockInstances->SetStaticMesh(ProductionRockMesh);
    if (ProductionGrassClumpMesh) GrassInstances->SetStaticMesh(ProductionGrassClumpMesh);
    if (ProductionGrassClumpMesh) EastFieldRowInstances->SetStaticMesh(ProductionGrassClumpMesh);
    if (ProductionShrubMesh) ShrubInstances->SetStaticMesh(ProductionShrubMesh);
    if (ProductionPathStoneMesh) PathStoneInstances->SetStaticMesh(ProductionPathStoneMesh);

    BuildPrototypeWorld();

    if (UGameInstance* GI = GetGameInstance())
    {
        QuestSubsystem = GI->GetSubsystem<UShireQuestSubsystem>();
        if (QuestSubsystem)
        {
            QuestSubsystem->OnActiveQuestChanged.AddDynamic(this, &AShirePrototypeWorldBuilder::HandleActiveQuestChanged);
            QuestSubsystem->OnQuestStageChanged.AddDynamic(this, &AShirePrototypeWorldBuilder::HandleQuestStageChanged);
            QuestSubsystem->OnStoryBeatTriggered.AddDynamic(this, &AShirePrototypeWorldBuilder::HandleStoryBeatTriggered);
        }
    }

    ApplyStoryAtmosphere();
    ApplyBagEndStoryVariant();
    ApplyPartyStoryVariant();
}

void AShirePrototypeWorldBuilder::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (QuestSubsystem)
    {
        QuestSubsystem->OnActiveQuestChanged.RemoveDynamic(this, &AShirePrototypeWorldBuilder::HandleActiveQuestChanged);
        QuestSubsystem->OnQuestStageChanged.RemoveDynamic(this, &AShirePrototypeWorldBuilder::HandleQuestStageChanged);
        QuestSubsystem->OnStoryBeatTriggered.RemoveDynamic(this, &AShirePrototypeWorldBuilder::HandleStoryBeatTriggered);
        QuestSubsystem = nullptr;
    }

    Super::EndPlay(EndPlayReason);
}

AStaticMeshActor* AShirePrototypeWorldBuilder::SpawnShape(
    UStaticMesh* Mesh,
    const FVector& Location,
    const FVector& Scale,
    const FLinearColor& Color,
    const FRotator& Rotation,
    bool bCollision)
{
    if (!GetWorld() || !Mesh)
    {
        return nullptr;
    }

    FActorSpawnParameters Params;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

    AStaticMeshActor* Actor = GetWorld()->SpawnActor<AStaticMeshActor>(Location, Rotation, Params);
    if (!Actor)
    {
        return nullptr;
    }

    Actor->Tags.AddUnique(TEXT("RuntimePrototypeGenerated"));

    UStaticMeshComponent* MeshComponent = Actor->GetStaticMeshComponent();
    MeshComponent->SetMobility(EComponentMobility::Movable);
    MeshComponent->SetStaticMesh(Mesh);
    MeshComponent->SetCollisionEnabled(bCollision ? ECollisionEnabled::QueryAndPhysics : ECollisionEnabled::NoCollision);
    Actor->SetActorScale3D(Scale);

    // Preserve authored/imported materials on production meshes. Engine primitives are
    // still colorized as deterministic fallbacks when an imported asset is unavailable.
    const bool bFallbackPrimitive =
        Mesh == CubeMesh || Mesh == SphereMesh || Mesh == CylinderMesh || Mesh == ConeMesh;
    if (BasicMaterial && bFallbackPrimitive)
    {
        UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(BasicMaterial, Actor);
        if (MID)
        {
            MID->SetVectorParameterValue(TEXT("Color"), Color);
            MeshComponent->SetMaterial(0, MID);
        }
    }

    return Actor;
}

void AShirePrototypeWorldBuilder::SpawnWaterSurface(
    const FVector& Location,
    const FVector& Scale,
    const FRotator& Rotation)
{
    // D keeps water deliberately cheap on the 2 GB-class VRAM target: one opaque
    // production material, no planar/scene-capture reflection, no CPU simulation,
    // no collision ownership change. The chapter streaming subsystem owns residency.
    AStaticMeshActor* WaterActor = SpawnShape(
        CubeMesh,
        Location,
        Scale,
        FLinearColor(0.045f, 0.20f, 0.30f),
        Rotation,
        false);

    if (!WaterActor)
    {
        return;
    }

    if (UStaticMeshComponent* WaterMesh = WaterActor->GetStaticMeshComponent())
    {
        WaterMesh->SetCastShadow(false);
        if (ProductionWaterMaterial)
        {
            WaterMesh->SetMaterial(0, ProductionWaterMaterial);
        }
    }

    WaterActor->Tags.AddUnique(TEXT("P1C01LowCostWaterSurface"));
    UE_LOG(
        LogTemp,
        Display,
        TEXT("D_WATER_EVIDENCE materialResident=%s collision=none planarReflection=no sceneCapture=no cpuSimulation=no"),
        ProductionWaterMaterial ? TEXT("yes") : TEXT("no"));
}

void AShirePrototypeWorldBuilder::SpawnLabel(const FString& Text, const FVector& Location, const FLinearColor& Color)
{
    if (!ShireLayout::ShowPrototypeWorldLabels)
    {
        return;
    }

    if (!GetWorld())
    {
        return;
    }

    ATextRenderActor* Label = GetWorld()->SpawnActor<ATextRenderActor>(Location, FRotator(0.0f, 180.0f, 0.0f));
    if (!Label)
    {
        return;
    }

    Label->Tags.AddUnique(TEXT("RuntimePrototypeGenerated"));

    UTextRenderComponent* TextComponent = Label->GetTextRender();
    TextComponent->SetText(FText::FromString(Text));
    TextComponent->SetHorizontalAlignment(EHorizTextAligment::EHTA_Center);
    TextComponent->SetWorldSize(42.0f);
    TextComponent->SetTextRenderColor(Color.ToFColor(true));
}

void AShirePrototypeWorldBuilder::SpawnTree(const FVector& Location, float Scale)
{
    const FLinearColor Bark(0.18f, 0.085f, 0.035f);
    const FLinearColor LeafDark(0.075f, 0.28f, 0.065f);
    const FLinearColor LeafMid(0.105f, 0.37f, 0.085f);
    const FLinearColor LeafLight(0.16f, 0.43f, 0.11f);

    if (ProductionTreeTrunkMesh && ProductionTreeCanopyMesh)
    {
        SpawnShape(ProductionTreeTrunkMesh, Location, FVector(Scale), Bark, FRotator::ZeroRotator, true);
        SpawnShape(ProductionTreeCanopyMesh, Location + FVector(0.0f, 0.0f, 205.0f * Scale),
            FVector(Scale), LeafMid,
            FRotator(0.0f, FMath::Fmod(Location.X * 0.011f - Location.Y * 0.019f, 360.0f), 0.0f), false);
        return;
    }

    SpawnShape(CylinderMesh, Location + FVector(0.0f, 0.0f, 92.0f * Scale),
        FVector(0.15f, 0.15f, 0.92f) * Scale, Bark, FRotator::ZeroRotator, true);
    SpawnShape(SphereMesh, Location + FVector(-20.0f, -12.0f, 205.0f) * Scale,
        FVector(0.78f, 0.72f, 0.62f) * Scale, LeafDark, FRotator::ZeroRotator, false);
    SpawnShape(SphereMesh, Location + FVector(28.0f, 8.0f, 222.0f) * Scale,
        FVector(0.72f, 0.68f, 0.60f) * Scale, LeafMid, FRotator::ZeroRotator, false);
    SpawnShape(SphereMesh, Location + FVector(0.0f, 18.0f, 250.0f) * Scale,
        FVector(0.58f, 0.54f, 0.48f) * Scale, LeafLight, FRotator::ZeroRotator, false);
}

void AShirePrototypeWorldBuilder::SpawnHobbitHole(const FVector& Location, float Scale)
{
    const FLinearColor Turf(0.18f, 0.40f, 0.105f);
    const FLinearColor Earth(0.36f, 0.24f, 0.13f);
    const FLinearColor Timber(0.32f, 0.18f, 0.075f);
    const FLinearColor DoorGreen(0.08f, 0.34f, 0.15f);
    const FLinearColor WarmGlass(0.92f, 0.67f, 0.28f);
    const FLinearColor Stone(0.42f, 0.40f, 0.34f);

    // Imported production mound/facade replace the toy-like primitive silhouette when
    // available. Runtime accents below remain cheap and readable on the target laptop.
    if (ProductionTurfMoundMesh && ProductionHobbitFacadeMesh)
    {
        SpawnShape(ProductionTurfMoundMesh, Location + FVector(0.0f, 0.0f, 30.0f * Scale),
            FVector(2.45f, 2.10f, 2.10f) * Scale, Turf, FRotator::ZeroRotator, true);
        SpawnShape(ProductionHobbitFacadeMesh, Location + FVector(-88.0f * Scale, 0.0f, 0.0f),
            FVector(1.0f) * Scale, Earth, FRotator::ZeroRotator, true);
    }
    else
    {
        SpawnShape(SphereMesh, Location + FVector(0.0f, 0.0f, 82.0f * Scale),
            FVector(1.72f, 1.12f, 0.78f) * Scale, Turf, FRotator::ZeroRotator, true);
        SpawnShape(CubeMesh, Location + FVector(-72.0f * Scale, 0.0f, 54.0f * Scale),
            FVector(0.10f, 0.82f, 0.58f) * Scale, Earth, FRotator::ZeroRotator, true);
    }

    const bool bProductionHobbitHoleResident =
        ProductionTurfMoundMesh && ProductionHobbitFacadeMesh;

    if (bProductionHobbitHoleResident)
    {
        return;
    }

    // Primitive accent geometry belongs only to the deterministic fallback path.
    // Production mound/facade assets own the final visible silhouette when resident.
    // Round frame + inset painted door.
    SpawnShape(CylinderMesh, Location + FVector(-83.0f * Scale, 0.0f, 55.0f * Scale),
        FVector(0.51f, 0.51f, 0.075f) * Scale, Timber, FRotator(0.0f, 90.0f, 0.0f), false);
    SpawnShape(CylinderMesh, Location + FVector(-88.0f * Scale, 0.0f, 55.0f * Scale),
        FVector(0.43f, 0.43f, 0.050f) * Scale, DoorGreen, FRotator(0.0f, 90.0f, 0.0f), false);
    SpawnShape(SphereMesh, Location + FVector(-94.0f * Scale, 21.0f * Scale, 56.0f * Scale),
        FVector(0.045f) * Scale, FLinearColor(0.74f, 0.55f, 0.18f), FRotator::ZeroRotator, false);

    // Two warm circular windows and shallow stone sills.
    for (float Side : { -1.0f, 1.0f })
    {
        const FVector Window = Location + FVector(-88.0f * Scale, Side * 58.0f * Scale, 68.0f * Scale);
        SpawnShape(CylinderMesh, Window, FVector(0.22f, 0.22f, 0.035f) * Scale,
            Timber, FRotator(0.0f, 90.0f, 0.0f), false);
        SpawnShape(CylinderMesh, Window + FVector(-4.0f * Scale, 0.0f, 0.0f),
            FVector(0.17f, 0.17f, 0.025f) * Scale, WarmGlass, FRotator(0.0f, 90.0f, 0.0f), false);
        SpawnShape(CubeMesh, Window + FVector(-2.0f * Scale, 0.0f, -27.0f * Scale),
            FVector(0.10f, 0.30f, 0.045f) * Scale, Stone, FRotator::ZeroRotator, false);
    }

    // Chimney, doorstep and planted entry soften the generated silhouette.
    SpawnShape(CubeMesh, Location + FVector(35.0f, -45.0f, 170.0f) * Scale,
        FVector(0.18f, 0.18f, 0.48f) * Scale, Stone, FRotator::ZeroRotator, false);
    SpawnShape(CubeMesh, Location + FVector(-122.0f, 0.0f, 8.0f) * Scale,
        FVector(0.42f, 0.70f, 0.10f) * Scale, Stone, FRotator::ZeroRotator, true);
    SpawnShape(SphereMesh, Location + FVector(-105.0f, -92.0f, 24.0f) * Scale,
        FVector(0.32f, 0.26f, 0.22f) * Scale, FLinearColor(0.10f, 0.32f, 0.08f), FRotator::ZeroRotator, false);
    SpawnShape(SphereMesh, Location + FVector(-105.0f, 92.0f, 24.0f) * Scale,
        FVector(0.32f, 0.26f, 0.22f) * Scale, FLinearColor(0.12f, 0.36f, 0.09f), FRotator::ZeroRotator, false);
}


void AShirePrototypeWorldBuilder::SpawnFenceLine(const FVector& Start, const FVector& End, int32 Sections)
{
    if (Sections <= 0)
    {
        return;
    }

    const FVector FullDelta = End - Start;
    const FVector SectionDelta = FullDelta / static_cast<float>(Sections);
    const float SectionLength = SectionDelta.Size2D();
    const FRotator RailRotation = SectionDelta.GetSafeNormal2D().Rotation();
    const FLinearColor Wood(0.31f, 0.18f, 0.08f);

    if (ProductionFenceSegmentMesh)
    {
        for (int32 Index = 0; Index < Sections; ++Index)
        {
            const FVector Mid = Start + SectionDelta * (static_cast<float>(Index) + 0.5f);
            SpawnShape(ProductionFenceSegmentMesh, Mid,
                FVector(FMath::Max(0.25f, SectionLength / 100.0f), 1.0f, 1.0f),
                Wood, RailRotation, true);
        }
        return;
    }

    for (int32 Index = 0; Index <= Sections; ++Index)
    {
        const FVector PostBase = Start + SectionDelta * static_cast<float>(Index);
        SpawnShape(CubeMesh, PostBase + FVector(0.0f, 0.0f, 34.0f),
            FVector(0.075f, 0.075f, 0.68f), Wood, FRotator::ZeroRotator, true);
    }

    for (int32 Index = 0; Index < Sections; ++Index)
    {
        const FVector Mid = Start + SectionDelta * (static_cast<float>(Index) + 0.5f);
        const FVector RailScale(FMath::Max(0.25f, SectionLength / 100.0f), 0.055f, 0.055f);
        SpawnShape(CubeMesh, Mid + FVector(0.0f, 0.0f, 28.0f), RailScale, Wood, RailRotation, false);
        SpawnShape(CubeMesh, Mid + FVector(0.0f, 0.0f, 58.0f), RailScale, Wood, RailRotation, false);
    }
}

void AShirePrototypeWorldBuilder::SpawnGardenPatch(const FVector& Center, float Scale)
{
    const FLinearColor Soil(0.23f, 0.13f, 0.065f);
    const FLinearColor Leaf(0.18f, 0.42f, 0.12f);

    for (int32 Row = -2; Row <= 2; ++Row)
    {
        const FVector RowCenter = Center + FVector(0.0f, Row * 42.0f * Scale, 4.0f);
        SpawnShape(CubeMesh, RowCenter, FVector(1.25f, 0.12f, 0.05f) * Scale, Soil, FRotator::ZeroRotator, false);

        for (int32 Plant = -2; Plant <= 2; ++Plant)
        {
            const FVector PlantLocation = RowCenter + FVector(Plant * 48.0f * Scale, 0.0f, 12.0f * Scale);
            SpawnShape(SphereMesh, PlantLocation, FVector(0.10f, 0.10f, 0.075f) * Scale,
                Leaf, FRotator::ZeroRotator, false);
        }
    }
}

void AShirePrototypeWorldBuilder::ConfigureFoliageInstances()
{
    if (!BasicMaterial)
    {
        return;
    }

    auto ApplyInstanceColor = [this](
        UHierarchicalInstancedStaticMeshComponent* Component,
        UStaticMesh* ProductionMesh,
        const FLinearColor& Color)
    {
        if (!Component)
        {
            return;
        }

        // Imported production meshes already carry authored materials/textures.
        // Do not flatten them back to BasicShapeMaterial.
        if (ProductionMesh && Component->GetStaticMesh() == ProductionMesh)
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

    ApplyInstanceColor(GrassInstances, ProductionGrassClumpMesh, FLinearColor(0.105f, 0.34f, 0.065f));
    ApplyInstanceColor(FlowerInstances, nullptr, FLinearColor(0.92f, 0.69f, 0.24f));
    ApplyInstanceColor(ShrubInstances, ProductionShrubMesh, FLinearColor(0.085f, 0.285f, 0.055f));
    ApplyInstanceColor(DistantTreeTrunkInstances, ProductionTreeTrunkMesh, FLinearColor(0.15f, 0.075f, 0.03f));
    ApplyInstanceColor(DistantTreeCanopyInstances, ProductionTreeCanopyMesh, FLinearColor(0.07f, 0.25f, 0.045f));
    ApplyInstanceColor(RockInstances, ProductionRockMesh, FLinearColor(0.34f, 0.35f, 0.31f));
    ApplyInstanceColor(PathStoneInstances, ProductionPathStoneMesh, FLinearColor(0.43f, 0.40f, 0.32f));
}

void AShirePrototypeWorldBuilder::SpawnFoliagePass()
{
    if (!GrassInstances || !FlowerInstances || !ShrubInstances)
    {
        return;
    }

    GrassInstances->ClearInstances();
    FlowerInstances->ClearInstances();
    ShrubInstances->ClearInstances();

    // Clustered instancing keeps the expanded world green without turning every blade
    // into a ticking/rendering actor.
    const FVector GrassCenters[] = {
        FVector(-2200,-650,20), FVector(-1500,650,20), FVector(-650,-520,20), FVector(100,720,20),
        FVector(900,-520,20), FVector(2500,520,20), FVector(4300,-300,20),
        FVector(ShireLayout::FieldsX,-650,20), FVector(ShireLayout::FieldsX+1300,250,20),
        FVector(ShireLayout::WoodedRoadX-1800,1000,20), FVector(ShireLayout::WoodedRoadX,650,20),
        FVector(ShireLayout::WoodedRoadX+1900,-600,20), FVector(19500,-1100,20),
        FVector(ShireLayout::FerryX-1800,-650,20), FVector(ShireLayout::FerryX+1000,500,20)
    };

    int32 GrassIndex = 0;
    for (const FVector& Center : GrassCenters)
    {
        for (int32 Ring = 0; Ring < 48; ++Ring)
        {
            const float Angle = FMath::DegreesToRadians(static_cast<float>((Ring * 137 + GrassIndex * 29) % 360));
            const float Radius = 95.0f + 58.0f * static_cast<float>(Ring % 8);
            const FVector Base = Center + FVector(FMath::Cos(Angle) * Radius, FMath::Sin(Angle) * Radius, 0.0f);
            const float Size = 0.09f + 0.012f * static_cast<float>((Ring + GrassIndex) % 4);
            const float Height = 0.18f + 0.020f * static_cast<float>((Ring + GrassIndex) % 5);

            GrassInstances->AddInstance(FTransform(
                FRotator(0.0f, static_cast<float>((Ring * 43 + GrassIndex * 17) % 360), 0.0f),
                Base,
                FVector(Size, Size, Height)));
        }
        ++GrassIndex;
    }

    const FVector FlowerBeds[] = {
        FVector(-2140,-690,38), FVector(-1990,-680,38), FVector(-1270,-560,38),
        FVector(-300,1180,38), FVector(20,1260,38), FVector(350,1180,38),
        FVector(6200,-1480,38), FVector(6480,-1390,38), FVector(6900,-1540,38),
        FVector(ShireLayout::FerryX-650,-920,38)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(FlowerBeds); ++Index)
    {
        const float Scale = 0.055f + 0.008f * static_cast<float>(Index % 3);
        FlowerInstances->AddInstance(FTransform(
            FRotator::ZeroRotator,
            FlowerBeds[Index],
            FVector(Scale, Scale, Scale * 0.75f)));
    }

    const FVector ShrubCenters[] = {
        FVector(-2250,-610,42), FVector(-1600,-450,42), FVector(-820,-500,42),
        FVector(-250,1180,42), FVector(520,1050,42), FVector(2900,520,42),
        FVector(5600,-900,42), FVector(9300,350,42),
        FVector(ShireLayout::WoodedRoadX-2100,950,42), FVector(ShireLayout::WoodedRoadX-900,-850,42),
        FVector(ShireLayout::WoodedRoadX+350,900,42), FVector(ShireLayout::WoodedRoadX+1600,-750,42),
        FVector(19700,-1180,42), FVector(ShireLayout::FerryX-1300,-800,42)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(ShrubCenters); ++Index)
    {
        const float Scale = 0.24f + 0.035f * static_cast<float>(Index % 4);
        ShrubInstances->AddInstance(FTransform(
            FRotator(0.0f, static_cast<float>((Index * 31) % 360), 0.0f),
            ShrubCenters[Index],
            FVector(Scale * 1.35f, Scale, Scale * 0.72f)));
    }
}


void AShirePrototypeWorldBuilder::ConfigureMorningAtmosphere()
{
    if (!GetWorld())
    {
        return;
    }

    ADirectionalLight* Sun = nullptr;
    for (TActorIterator<ADirectionalLight> It(GetWorld()); It; ++It)
    {
        Sun = *It;
        break;
    }

    if (!Sun)
    {
        Sun = GetWorld()->SpawnActor<ADirectionalLight>(
            FVector::ZeroVector, FRotator(-38.0f, -28.0f, 0.0f));
        if (Sun)
        {
            Sun->Tags.AddUnique(TEXT("RuntimePrototypeGenerated"));
        }
    }

    RuntimeSun = Sun;

    if (Sun)
    {
        if (UDirectionalLightComponent* SunComponent = Cast<UDirectionalLightComponent>(Sun->GetLightComponent()))
        {
            // UE4.27 requires the light to be movable before changing the actor rotation in PIE.
            SunComponent->SetMobility(EComponentMobility::Movable);
            Sun->SetActorRotation(FRotator(-38.0f, -28.0f, 0.0f));
            SunComponent->SetIntensity(2.55f);
            SunComponent->SetLightColor(FLinearColor(1.0f, 0.86f, 0.70f));
            SunComponent->SetCastShadows(true);
            SunComponent->SetAtmosphereSunLight(true);
            SunComponent->SetAtmosphereSunLightIndex(0);
        }
    }

    // The template map may still contain legacy AtmosphericFog. Running it together
    // with SkyAtmosphere produces a visible UE4.27 warning and conflicting sky models.
    for (TActorIterator<AActor> It(GetWorld()); It; ++It)
    {
        AActor* Candidate = *It;
        if (Candidate && Candidate != this &&
            Candidate->GetClass() && Candidate->GetClass()->GetName().Contains(TEXT("AtmosphericFog")))
        {
            Candidate->Destroy();
        }
    }

    ASkyAtmosphere* Atmosphere = nullptr;
    for (TActorIterator<ASkyAtmosphere> It(GetWorld()); It; ++It)
    {
        Atmosphere = *It;
        break;
    }
    if (!Atmosphere)
    {
        Atmosphere = GetWorld()->SpawnActor<ASkyAtmosphere>(FVector::ZeroVector, FRotator::ZeroRotator);
        if (Atmosphere)
        {
            Atmosphere->Tags.AddUnique(TEXT("RuntimePrototypeGenerated"));
        }
    }

    AExponentialHeightFog* HeightFog = nullptr;
    for (TActorIterator<AExponentialHeightFog> It(GetWorld()); It; ++It)
    {
        HeightFog = *It;
        break;
    }
    if (!HeightFog)
    {
        HeightFog = GetWorld()->SpawnActor<AExponentialHeightFog>(
            FVector(0.0f, 0.0f, -80.0f), FRotator::ZeroRotator);
        if (HeightFog)
        {
            HeightFog->Tags.AddUnique(TEXT("RuntimePrototypeGenerated"));
        }
    }
    if (HeightFog)
    {
        if (UExponentialHeightFogComponent* FogComponent = HeightFog->GetComponent())
        {
            FogComponent->SetFogDensity(0.0085f);
            FogComponent->SetFogHeightFalloff(0.17f);
            FogComponent->SetFogInscatteringColor(FLinearColor(0.62f, 0.70f, 0.61f));
            FogComponent->SetDirectionalInscatteringColor(FLinearColor(1.0f, 0.82f, 0.60f));
            FogComponent->SetStartDistance(850.0f);
            FogComponent->SetFogMaxOpacity(0.72f);
            FogComponent->SetVolumetricFog(false);
        }
    }

    ASkyLight* Sky = nullptr;
    for (TActorIterator<ASkyLight> It(GetWorld()); It; ++It)
    {
        Sky = *It;
        break;
    }

    if (!Sky)
    {
        Sky = GetWorld()->SpawnActor<ASkyLight>(FVector::ZeroVector, FRotator::ZeroRotator);
        if (Sky)
        {
            Sky->Tags.AddUnique(TEXT("RuntimePrototypeGenerated"));
        }
    }

    RuntimeSky = Sky;

    if (Sky)
    {
        if (USkyLightComponent* SkyComponent = Cast<USkyLightComponent>(Sky->GetLightComponent()))
        {
            SkyComponent->SetMobility(EComponentMobility::Movable);
            SkyComponent->SetIntensity(0.60f);
            SkyComponent->bLowerHemisphereIsBlack = false;
            SkyComponent->RecaptureSky();
        }
    }

    APostProcessVolume* PostProcess = nullptr;
    for (TActorIterator<APostProcessVolume> It(GetWorld()); It; ++It)
    {
        PostProcess = *It;
        if (PostProcess->bUnbound)
        {
            break;
        }
    }

    if (!PostProcess)
    {
        PostProcess = GetWorld()->SpawnActor<APostProcessVolume>(
            FVector::ZeroVector, FRotator::ZeroRotator);
        if (PostProcess)
        {
            PostProcess->Tags.AddUnique(TEXT("RuntimePrototypeGenerated"));
        }
    }

    RuntimePostProcess = PostProcess;

    if (PostProcess)
    {
        PostProcess->bUnbound = true;
        PostProcess->BlendWeight = 1.0f;

        PostProcess->Settings.bOverride_AutoExposureMinBrightness = true;
        PostProcess->Settings.AutoExposureMinBrightness = 0.68f;
        PostProcess->Settings.bOverride_AutoExposureMaxBrightness = true;
        PostProcess->Settings.AutoExposureMaxBrightness = 0.98f;
        PostProcess->Settings.bOverride_AutoExposureBias = true;
        PostProcess->Settings.AutoExposureBias = -0.12f;

        PostProcess->Settings.bOverride_BloomIntensity = true;
        PostProcess->Settings.BloomIntensity = 0.16f;
        PostProcess->Settings.bOverride_VignetteIntensity = true;
        PostProcess->Settings.VignetteIntensity = 0.17f;
    }
}


void AShirePrototypeWorldBuilder::HandleActiveQuestChanged(FName QuestId)
{
    ApplyStoryAtmosphere();
    ApplyBagEndStoryVariant();
    ApplyPartyStoryVariant();
}

void AShirePrototypeWorldBuilder::HandleQuestStageChanged(FName QuestId, int32 NewStage)
{
    ApplyStoryAtmosphere();
    ApplyBagEndStoryVariant();
    ApplyPartyStoryVariant();
}

void AShirePrototypeWorldBuilder::HandleStoryBeatTriggered(FName StoryBeatId)
{
    ApplyStoryAtmosphere();
    ApplyBagEndStoryVariant();
    ApplyPartyStoryVariant();
}

void AShirePrototypeWorldBuilder::ApplyPartyStoryVariant()
{
    if (!QuestSubsystem)
    {
        return;
    }

    const bool bPartyArrived = QuestSubsystem->HasStoryBeatTriggered(TEXT("PartyArrival"));
    const bool bPartyEnded = QuestSubsystem->HasStoryBeatTriggered(TEXT("BilboDisappearance"));
    const bool bSetupVisible = !bPartyArrived && !bPartyEnded &&
        QuestSubsystem->GetActiveQuestId() == TEXT("ShireArrival");
    const bool bCelebrationVisible = bPartyArrived && !bPartyEnded;

    for (AStaticMeshActor* Actor : PartySetupVariantActors)
    {
        if (IsValid(Actor))
        {
            Actor->SetActorHiddenInGame(!bSetupVisible);
        }
    }
    for (AStaticMeshActor* Actor : PartyCelebrationVariantActors)
    {
        if (IsValid(Actor))
        {
            Actor->SetActorHiddenInGame(!bCelebrationVisible);
        }
    }

    UE_LOG(
        LogTemp, Verbose,
        TEXT("PARTY_SOCIAL_STORY_VARIANT setup=%s celebration=%s ended=%s setupProps=%d celebrationProps=%d"),
        bSetupVisible ? TEXT("visible") : TEXT("hidden"),
        bCelebrationVisible ? TEXT("visible") : TEXT("hidden"),
        bPartyEnded ? TEXT("yes") : TEXT("no"),
        PartySetupVariantActors.Num(),
        PartyCelebrationVariantActors.Num());
}


void AShirePrototypeWorldBuilder::ApplyBagEndStoryVariant()
{
    const FName QuestId = QuestSubsystem ? QuestSubsystem->GetActiveQuestId() : NAME_None;
    const bool bBirthdayState =
        QuestId == TEXT("ShireArrival") ||
        QuestId == TEXT("LongExpectedParty");
    const bool bDepartureState =
        QuestId == TEXT("RingSecret") ||
        QuestId == TEXT("LeavingHome");

    for (AStaticMeshActor* Actor : BagEndBirthdayVariantActors)
    {
        if (IsValid(Actor))
        {
            Actor->SetActorHiddenInGame(!bBirthdayState);
        }
    }

    for (AStaticMeshActor* Actor : BagEndDepartureVariantActors)
    {
        if (IsValid(Actor))
        {
            Actor->SetActorHiddenInGame(!bDepartureState);
        }
    }

    const TCHAR* StateName =
        bBirthdayState ? TEXT("birthday") :
        (bDepartureState ? TEXT("departure") : TEXT("neutral"));

    UE_LOG(
        LogTemp,
        Verbose,
        TEXT("BAG_END_STORY_VARIANT quest=%s state=%s birthdayVisible=%d departureVisible=%d"),
        *QuestId.ToString(),
        StateName,
        bBirthdayState ? BagEndBirthdayVariantActors.Num() : 0,
        bDepartureState ? BagEndDepartureVariantActors.Num() : 0);
}


void AShirePrototypeWorldBuilder::ApplyStoryAtmosphere()
{
    if (!QuestSubsystem || !RuntimeSun || !RuntimeSky || !RuntimePostProcess)
    {
        return;
    }

    UDirectionalLightComponent* SunComponent =
        Cast<UDirectionalLightComponent>(RuntimeSun->GetLightComponent());
    USkyLightComponent* SkyComponent =
        Cast<USkyLightComponent>(RuntimeSky->GetLightComponent());
    if (!SunComponent || !SkyComponent)
    {
        return;
    }

    const FName QuestId = QuestSubsystem->GetActiveQuestId();

    FRotator SunRotation(-38.0f, -28.0f, 0.0f);
    float SunIntensity = 2.55f;
    FLinearColor SunColor(1.0f, 0.86f, 0.70f);
    float SkyIntensity = 0.60f;
    float ExposureBias = -0.12f;
    float Bloom = 0.16f;
    float Vignette = 0.17f;

    if (QuestId == TEXT("LongExpectedParty"))
    {
        SunRotation = FRotator(-22.0f, -42.0f, 0.0f);
        SunIntensity = 2.05f;
        SunColor = FLinearColor(1.0f, 0.67f, 0.42f);
        SkyIntensity = 0.56f;
        ExposureBias = -0.10f;
        Bloom = 0.34f;
        Vignette = 0.14f;
    }
    else if (QuestId == TEXT("RingSecret"))
    {
        SunRotation = FRotator(-10.0f, -58.0f, 0.0f);
        SunIntensity = 1.15f;
        SunColor = FLinearColor(0.64f, 0.70f, 0.88f);
        SkyIntensity = 0.44f;
        ExposureBias = -0.18f;
        Bloom = 0.18f;
        Vignette = 0.22f;
    }
    else if (QuestId == TEXT("LeavingHome") || QuestId == TEXT("Shortcut"))
    {
        SunRotation = FRotator(-16.0f, -66.0f, 0.0f);
        SunIntensity = 1.55f;
        SunColor = FLinearColor(0.78f, 0.76f, 0.72f);
        SkyIntensity = 0.52f;
        ExposureBias = -0.08f;
        Bloom = 0.18f;
        Vignette = 0.18f;
    }
    else if (QuestId == TEXT("KeepOffRoad"))
    {
        SunRotation = FRotator(-13.0f, -75.0f, 0.0f);
        SunIntensity = 1.05f;
        SunColor = FLinearColor(0.52f, 0.58f, 0.68f);
        SkyIntensity = 0.34f;
        ExposureBias = -0.28f;
        Bloom = 0.12f;
        Vignette = 0.30f;
    }
    else if (QuestId == TEXT("FerryEscape"))
    {
        SunRotation = FRotator(-18.0f, -84.0f, 0.0f);
        SunIntensity = 1.45f;
        SunColor = FLinearColor(0.62f, 0.68f, 0.78f);
        SkyIntensity = 0.42f;
        ExposureBias = -0.16f;
        Bloom = 0.14f;
        Vignette = 0.24f;
    }

    SunComponent->SetMobility(EComponentMobility::Movable);
    RuntimeSun->SetActorRotation(SunRotation);
    SunComponent->SetIntensity(SunIntensity);
    SunComponent->SetLightColor(SunColor);

    SkyComponent->SetMobility(EComponentMobility::Movable);
    SkyComponent->SetIntensity(SkyIntensity);
    SkyComponent->RecaptureSky();

    RuntimePostProcess->Settings.bOverride_AutoExposureBias = true;
    RuntimePostProcess->Settings.AutoExposureBias = ExposureBias;
    RuntimePostProcess->Settings.bOverride_BloomIntensity = true;
    RuntimePostProcess->Settings.BloomIntensity = Bloom;
    RuntimePostProcess->Settings.bOverride_VignetteIntensity = true;
    RuntimePostProcess->Settings.VignetteIntensity = Vignette;
}

void AShirePrototypeWorldBuilder::SpawnVillage()
{
    // Foundational collision must not depend on an imported OBJ having generated
    // simple collision. Keep one deterministic Engine/BasicShapes cube under the Shire.
    const FLinearColor GroundColor(0.16f, 0.34f, 0.10f);
    AStaticMeshActor* CollisionFoundation = SpawnShape(
        CubeMesh,
        FVector(10800.0f, 0.0f, -105.0f),
        FVector(340.0f, 130.0f, 0.7f),
        GroundColor,
        FRotator::ZeroRotator,
        true);
    if (CollisionFoundation)
    {
        CollisionFoundation->Tags.AddUnique(TEXT("RuntimeCollisionFoundation"));
        if (ProductionGroundBlockMesh)
        {
            if (UStaticMeshComponent* FoundationComponent = CollisionFoundation->GetStaticMeshComponent())
            {
                FoundationComponent->SetVisibility(false, true);
                FoundationComponent->SetCastShadow(false);
            }
        }
    }

    if (ProductionGroundBlockMesh)
    {
        SpawnShape(
            ProductionGroundBlockMesh,
            FVector(10800.0f, 0.0f, -70.0f),
            FVector(340.0f, 130.0f, 1.0f),
            GroundColor,
            FRotator::ZeroRotator,
            false);
    }

    // Fallback-only horizon silhouettes. When the authored common terrain mesh is
    // resident, SpawnGeographyFoundationPass owns this repeated geography through HISM.
    if (!ProductionCommonTerracedHillMesh)
    {
        const FVector HillCenters[] = {
            FVector(-2300,-1500,-145), FVector(-1200,1650,-150), FVector(700,1850,-160),
            FVector(3200,-1500,-150), FVector(4300,1650,-150),
            FVector(9800,-1750,-150), FVector(10800,1850,-155),
            FVector(13900,-1850,-145), FVector(15100,1900,-150),
            FVector(19000,-1750,-150), FVector(20500,1750,-155),
            FVector(24700,-1600,-150)
        };
        for (int32 Index = 0; Index < UE_ARRAY_COUNT(HillCenters); ++Index)
        {
            const float XY = 12.0f + 2.0f * static_cast<float>(Index % 3);
            SpawnShape(
                ProductionTurfMoundMesh ? ProductionTurfMoundMesh : SphereMesh,
                HillCenters[Index],
                FVector(XY, XY * 0.72f, 6.8f + 0.6f * (Index % 2)),
                Index % 2 == 0 ? FLinearColor(0.13f,0.33f,0.09f) : FLinearColor(0.15f,0.37f,0.10f),
                FRotator::ZeroRotator,
                false);
        }
    }

    // Continuous curved main road from Bag End to the Brandywine.
    const FVector RoadPoints[] = {
        FVector(-2450,-140,12), FVector(-2050,-90,12), FVector(-1550,30,12), FVector(-1050,100,12),
        FVector(-500,40,12), FVector(100,-80,12), FVector(700,-120,12),
        FVector(ShireLayout::HobbitonExitX,0,12), FVector(2500,320,12), FVector(3800,680,12),
        FVector(5200,420,12), FVector(6400,-260,12), FVector(ShireLayout::FieldsX,-620,12),
        FVector(9000,-180,12), FVector(10500,620,12), FVector(12100,980,12),
        FVector(ShireLayout::WoodedRoadX,520,12), FVector(16000,-180,12), FVector(17600,-720,12),
        FVector(19500,-980,12), FVector(21400,-820,12), FVector(ShireLayout::FerryX-700,-520,12)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(RoadPoints)-1; ++Index)
    {
        const FVector A = RoadPoints[Index];
        const FVector B = RoadPoints[Index+1];
        const FVector Delta = B-A;
        const FVector Mid = (A+B)*0.5f;
        SpawnShape(ProductionRoadBlockMesh ? ProductionRoadBlockMesh : CubeMesh, Mid, FVector(Delta.Size2D()/100.0f, 1.15f, ProductionRoadBlockMesh ? 0.25f : 0.10f),
            FLinearColor(0.40f,0.27f,0.14f), Delta.Rotation(), true);
    }

    // Hobbiton exploration paths remain denser than the wilderness paths.
    const FVector CoreFootpath[] = {
        FVector(-2250,-420,15), FVector(-1960,-560,15), FVector(-1650,-520,15),
        FVector(-1360,360,15), FVector(-1080,500,15), FVector(-760,520,15),
        FVector(-420,420,15), FVector(-80,760,15), FVector(360,1050,15), FVector(740,760,15)
    };
    for (int32 Index=0; Index<UE_ARRAY_COUNT(CoreFootpath)-1; ++Index)
    {
        const FVector D=CoreFootpath[Index+1]-CoreFootpath[Index];
        SpawnShape(ProductionRoadBlockMesh ? ProductionRoadBlockMesh : CubeMesh,(CoreFootpath[Index]+CoreFootpath[Index+1])*0.5f,
            FVector(D.Size2D()/100.0f,0.52f,ProductionRoadBlockMesh ? 0.18f : 0.065f),FLinearColor(0.36f,0.25f,0.14f),D.Rotation(),true);
    }

    const FVector FieldLoop[] = {
        FVector(5600,-200,15), FVector(6100,-1200,15), FVector(7350,-1500,15),
        FVector(8600,-1220,15), FVector(9300,-300,15)
    };
    for (int32 Index=0; Index<UE_ARRAY_COUNT(FieldLoop)-1; ++Index)
    {
        const FVector D=FieldLoop[Index+1]-FieldLoop[Index];
        SpawnShape(ProductionRoadBlockMesh ? ProductionRoadBlockMesh : CubeMesh,(FieldLoop[Index]+FieldLoop[Index+1])*0.5f,
            FVector(D.Size2D()/100.0f,0.46f,ProductionRoadBlockMesh ? 0.17f : 0.06f),FLinearColor(0.34f,0.24f,0.13f),D.Rotation(),true);
    }

    // Stone bridge, The Water and mill anchor the village center.
    // In production mode, do not leave the old cube/cone landmark shells underneath
    // the imported bridge and mill. They made the scene read like a greybox even when
    // the production assets had imported successfully.
    if (!ProductionStoneBridgeMesh)
    {
        SpawnShape(CubeMesh, FVector(-1050,90,25), FVector(2.0f,1.05f,0.16f), FLinearColor(0.34f,0.34f,0.31f));
        SpawnShape(CubeMesh, FVector(-1050,185,62), FVector(2.0f,0.09f,0.34f), FLinearColor(0.30f,0.30f,0.28f), FRotator::ZeroRotator,false);
        SpawnShape(CubeMesh, FVector(-1050,-5,62), FVector(2.0f,0.09f,0.34f), FLinearColor(0.30f,0.30f,0.28f), FRotator::ZeroRotator,false);
    }
    SpawnWaterSurface(FVector(-1060,310,-4), FVector(8.0f,1.0f,0.06f), FRotator(0,88,0));
    if (!ProductionMillHouseMesh)
    {
        SpawnShape(CubeMesh, FVector(-1250,330,88), FVector(1.45f,1.05f,0.88f), FLinearColor(0.52f,0.39f,0.23f));
        SpawnShape(ConeMesh, FVector(-1250,330,215), FVector(1.65f,1.25f,0.52f), FLinearColor(0.30f,0.17f,0.075f), FRotator::ZeroRotator,false);
    }
    if (!ProductionMillWheelMesh)
    {
        SpawnShape(CylinderMesh, FVector(-1135,330,95), FVector(0.74f,0.74f,0.09f), FLinearColor(0.24f,0.16f,0.08f), FRotator(0,90,0),false);
    }
    SpawnLabel(TEXT("The Mill"),FVector(-1250,330,320),FLinearColor(0.86f,0.82f,0.66f));

    // Hobbiton homes spread across the Hill instead of sitting in one row.
    const FVector Homes[] = {
        FVector(-2210,-520,0), FVector(-1780,-720,0), FVector(-1680,620,0), FVector(-1320,820,0),
        FVector(-1180,-760,0), FVector(-760,-620,0), FVector(-520,760,0), FVector(-120,-680,0),
        FVector(260,780,0), FVector(560,-720,0), FVector(920,700,0), FVector(1180,-620,0),
        FVector(1380,820,0), FVector(-2050,1120,0), FVector(-1450,1320,0), FVector(-820,1280,0)
    };
    for (int32 Index=0; Index<UE_ARRAY_COUNT(Homes); ++Index)
    {
        SpawnHobbitHole(Homes[Index], Index==0 ? 1.25f : 0.76f + 0.07f*(Index%4));
    }
    SpawnLabel(TEXT("Bag End"),FVector(-2210,-520,270),FLinearColor::Yellow);

    SpawnGardenPatch(FVector(-1910,-700,0),0.80f);
    SpawnGardenPatch(FVector(-1220,-600,0),0.68f);
    SpawnGardenPatch(FVector(430,610,0),0.70f);
    SpawnGardenPatch(FVector(1030,820,0),0.66f);
    SpawnFenceLine(FVector(-2290,-810,0),FVector(-1600,-810,0),7);
    SpawnFenceLine(FVector(-1540,-820,0),FVector(-930,-820,0),6);
    SpawnFenceLine(FVector(260,520,0),FVector(900,520,0),6);

    // Village common and market. The Green Dragon belongs at Bywater and is not
    // promoted as a canonical Hobbiton landmark in this compact P1C01 production slice.
    // The production layer provides the dominant building and stall silhouettes.
    // Retain these primitives only as a fallback when imports are unavailable.
    if (!ProductionCottageHouseMesh)
    {
        SpawnShape(CubeMesh,FVector(-520,360,115),FVector(2.1f,1.5f,1.15f),FLinearColor(0.45f,0.30f,0.17f));
        SpawnShape(ConeMesh,FVector(-520,360,270),FVector(2.4f,1.8f,0.7f),FLinearColor(0.28f,0.12f,0.05f),FRotator::ZeroRotator,false);
    }
    SpawnLabel(TEXT("Village Common"),FVector(-520,360,370),FLinearColor(0.85f,0.80f,0.55f));
    if (!ProductionMarketStallMesh)
    {
        const FVector MarketStalls[] = {
            FVector(-820,220,38),FVector(-660,180,38),FVector(-480,170,38),FVector(-300,250,38),FVector(-150,190,38)
        };
        for(int32 Index=0; Index<UE_ARRAY_COUNT(MarketStalls); ++Index)
        {
            const FVector Stall=MarketStalls[Index];
            SpawnShape(CubeMesh,Stall,FVector(0.72f,0.38f,0.08f),FLinearColor(0.43f,0.28f,0.13f));
            SpawnShape(CubeMesh,Stall+FVector(0,0,75),FVector(0.78f,0.44f,0.05f),
                Index%2==0 ? FLinearColor(0.48f,0.20f,0.12f) : FLinearColor(0.22f,0.39f,0.16f),FRotator::ZeroRotator,false);
        }
    }

    // Party Field is a distinct destination north of the village center.
    const FVector PartyCenter(280.0f,1320.0f,0.0f);
    SpawnTree(PartyCenter,1.45f);
    // The later architecture pass places the resident production picnic canopy at
    // this same story destination. Do not leave a large cube shell underneath it.
    if (!ProductionCommonMarketCanopyMesh)
    {
        SpawnShape(
            CubeMesh,
            PartyCenter+FVector(300,20,50),
            FVector(1.6f,0.9f,0.5f),
            FLinearColor(0.70f,0.62f,0.38f));
    }
    SpawnLabel(TEXT("Party Field"),PartyCenter+FVector(0,0,390),FLinearColor::White);
    if (!ProductionPicnicTableMesh)
    {
        const FVector PartyTables[] = {
            PartyCenter+FVector(-420,-150,40), PartyCenter+FVector(-100,-190,40), PartyCenter+FVector(240,-160,40),
            PartyCenter+FVector(-310,170,40), PartyCenter+FVector(40,210,40), PartyCenter+FVector(380,150,40)
        };
        for(const FVector& Table:PartyTables)
        {
            SpawnShape(CubeMesh,Table,FVector(0.90f,0.36f,0.08f),FLinearColor(0.43f,0.27f,0.12f));
            SpawnShape(CubeMesh,Table+FVector(0,62,-20),FVector(0.82f,0.10f,0.11f),FLinearColor(0.34f,0.20f,0.09f));
            SpawnShape(CubeMesh,Table+FVector(0,-62,-20),FVector(0.82f,0.10f,0.11f),FLinearColor(0.34f,0.20f,0.09f));
        }
    }
    const FVector LanternPosts[] = {
        PartyCenter+FVector(-520,-300,0),PartyCenter+FVector(520,-300,0),
        PartyCenter+FVector(-520,320,0),PartyCenter+FVector(520,320,0),
        PartyCenter+FVector(0,-350,0),PartyCenter+FVector(0,360,0)
    };
    for(const FVector& Post:LanternPosts)
    {
        if (ProductionLanternMesh)
        {
            SpawnShape(ProductionLanternMesh, Post, FVector(0.88f), FLinearColor::White, FRotator::ZeroRotator, false);
        }
        else
        {
            SpawnShape(CylinderMesh,Post+FVector(0,0,105),FVector(0.045f,0.045f,1.05f),FLinearColor(0.24f,0.13f,0.06f),FRotator::ZeroRotator,false);
            SpawnShape(SphereMesh,Post+FVector(0,0,208),FVector(0.11f),FLinearColor(0.92f,0.62f,0.18f),FRotator::ZeroRotator,false);
        }
    }

    // A long pastoral approach separates Hobbiton from the eastern farms.
    SpawnHobbitHole(FVector(4200,1450,0),0.72f);
    SpawnHobbitHole(FVector(5350,-1350,0),0.78f);
    SpawnTree(FVector(3300,1350,0),0.92f);
    SpawnTree(FVector(4550,-1250,0),0.88f);
    SpawnTree(FVector(5450,1150,0),0.90f);
    SpawnLabel(TEXT("East Fields"),FVector(ShireLayout::FieldsX,-1650,300),FLinearColor(0.86f,0.84f,0.68f));

    // Maggot-style farm proxy and crop rows.
    SpawnHobbitHole(FVector(6200,-1600,0),0.92f);
    SpawnFenceLine(FVector(5750,-1850,0),FVector(6900,-1850,0),9);
    SpawnGardenPatch(FVector(6500,-1420,0),0.95f);
    if (EastFieldRowInstances && ProductionGrassClumpMesh)
    {
        constexpr int32 EastFieldRowCount = 12;
        constexpr int32 InstancesPerRow = 8;
        static_assert(EastFieldRowCount * InstancesPerRow == 96, "East Fields row budget must remain capped at 96 instances.");

        for (int32 Row = 0; Row < EastFieldRowCount; ++Row)
        {
            const float Y = -1320.0f + Row * 135.0f;
            for (int32 Segment = 0; Segment < InstancesPerRow; ++Segment)
            {
                const float X = ShireLayout::FieldsX - 525.0f + Segment * 150.0f;
                const float ScaleBias = 0.76f + 0.05f * static_cast<float>((Row + Segment) % 3);
                const float Yaw = static_cast<float>((Row * 13 + Segment * 17) % 360);
                EastFieldRowInstances->AddInstanceWorldSpace(
                    FTransform(
                        FRotator(0.0f, Yaw, 0.0f),
                        FVector(X, Y, 6.0f),
                        FVector(ScaleBias, 0.62f, ScaleBias)));
            }
        }
    }
    else
    {
        // Deterministic greybox fallback only when the resident production row mesh
        // is unavailable. Production mode must not overlay cubes beneath the HISM rows.
        for (int32 Row = 0; Row < 12; ++Row)
        {
            const float Y = -1320.0f + Row * 135.0f;
            SpawnShape(
                CubeMesh,
                FVector(ShireLayout::FieldsX, Y, 8),
                FVector(12.0f, 0.10f, 0.06f),
                FLinearColor(0.30f,0.22f,0.075f),
                FRotator::ZeroRotator,
                false);
        }
    }
    if (ProductionBarrelMesh)
    {
        SpawnShape(ProductionBarrelMesh,FVector(8900,-1180,28),FVector(0.82f),FLinearColor(0.42f,0.24f,0.08f));
        SpawnShape(ProductionBarrelMesh,FVector(9020,-1110,28),FVector(0.76f),FLinearColor(0.42f,0.24f,0.08f));
    }
    else
    {
        SpawnShape(CylinderMesh,FVector(8900,-1180,36),FVector(0.48f,0.48f,0.40f),FLinearColor(0.64f,0.48f,0.16f));
        SpawnShape(CylinderMesh,FVector(9020,-1110,36),FVector(0.44f,0.44f,0.38f),FLinearColor(0.64f,0.48f,0.16f));
    }

    // Orchard / overlook gives exploration space before the road becomes threatening.
    for(int32 Index=0; Index<9; ++Index)
    {
        const float X=9700.0f+(Index%3)*260.0f;
        const float Y=-1550.0f+(Index/3)*260.0f;
        SpawnTree(FVector(X,Y,0),0.70f);
    }
    SpawnLabel(TEXT("Old Boundary"),FVector(10150,-1850,260),FLinearColor(0.74f,0.72f,0.60f));

    // Wooded Road: dense cover and hedges form a stealth space, not an open arena.
    const FVector WoodTrees[] = {
        FVector(12100,350,0),FVector(12400,1450,0),FVector(12800,-250,0),FVector(13200,1500,0),
        FVector(13600,-650,0),FVector(14000,1550,0),FVector(14500,-850,0),FVector(14900,1450,0),
        FVector(15300,-750,0),FVector(15700,1300,0),FVector(16100,-900,0),FVector(16600,1050,0),
        FVector(17000,-1150,0),FVector(17400,850,0)
    };
    for(const FVector& P:WoodTrees) SpawnTree(P,0.94f);
    SpawnFenceLine(FVector(11900,-450,0),FVector(17100,-1150,0),16);
    SpawnFenceLine(FVector(12000,1450,0),FVector(17100,800,0),16);
    if (ProductionCommonFallenLogMesh)
    {
        SpawnShape(
            ProductionCommonFallenLogMesh,
            FVector(14510,1180,18),
            FVector(0.82f),
            FLinearColor::White,
            FRotator(0,82,0),
            true);
    }
    else
    {
        SpawnShape(CylinderMesh,FVector(14550,1180,42),FVector(0.24f,0.24f,1.55f),
            FLinearColor(0.20f,0.10f,0.045f),FRotator(0,82,90),true);
        SpawnShape(SphereMesh,FVector(14470,1160,50),FVector(1.15f,0.52f,0.36f),
            FLinearColor(0.12f,0.29f,0.075f),FRotator::ZeroRotator,true);
    }
    if (ProductionCommonBoulderClusterMesh)
    {
        SpawnShape(
            ProductionCommonBoulderClusterMesh,
            FVector(14920,980,8),
            FVector(0.62f),
            FLinearColor::White,
            FRotator(0,-18,0),
            true);
    }
    SpawnLabel(TEXT("Wooded Road"),FVector(ShireLayout::WoodedRoadX,1750,310),FLinearColor(0.72f,0.78f,0.62f));

    // The run to the Brandywine is intentionally long enough to feel like escape.
    for(int32 Index=0; Index<10; ++Index)
    {
        SpawnTree(FVector(18400.0f+Index*380.0f,(Index%2==0 ? 900.0f : -1400.0f),0),0.76f);
    }

    // Brandywine and Bucklebury Ferry. River runs north/south; the story crosses east.
    SpawnWaterSurface(
        FVector(ShireLayout::FerryX,-500,-10),
        FVector(14.0f,60.0f,0.18f),
        FRotator::ZeroRotator);
    const float NearX=ShireLayout::FerryX-700.0f;
    const float FarX=ShireLayout::FerryX+700.0f;
    if (ProductionCommonFootbridgeMesh)
    {
        SpawnShape(ProductionCommonFootbridgeMesh,FVector(NearX,-500,4),FVector(0.78f),FLinearColor::White,FRotator(0,90,0),true);
        SpawnShape(ProductionCommonFootbridgeMesh,FVector(FarX,-500,4),FVector(0.78f),FLinearColor::White,FRotator(0,90,0),true);
    }
    else
    {
        SpawnShape(CubeMesh,FVector(NearX,-500,12),FVector(2.0f,2.0f,0.12f),FLinearColor(0.34f,0.20f,0.09f));
        SpawnShape(CubeMesh,FVector(FarX,-500,12),FVector(2.0f,2.0f,0.12f),FLinearColor(0.34f,0.20f,0.09f));
    }

    if (ProductionCommonRiverBoatMesh)
    {
        SpawnShape(ProductionCommonRiverBoatMesh,FVector(ShireLayout::FerryX,-500,12),FVector(0.86f),FLinearColor::White,FRotator(0,90,0),true);
    }
    else
    {
        SpawnShape(CubeMesh,FVector(ShireLayout::FerryX,-500,24),FVector(1.30f,0.86f,0.10f),FLinearColor(0.30f,0.18f,0.085f));
    }

    const FVector FerryPosts[] = {
        FVector(NearX,-700,18),FVector(NearX,-300,18),FVector(FarX,-700,18),FVector(FarX,-300,18)
    };
    for(const FVector& Post:FerryPosts)
    {
        if (ProductionCommonRopePostMesh)
        {
            SpawnShape(ProductionCommonRopePostMesh,Post,FVector(0.72f),FLinearColor::White,FRotator::ZeroRotator,true);
        }
        else
        {
            SpawnShape(CylinderMesh,Post+FVector(0,0,52),FVector(0.09f,0.09f,0.72f),FLinearColor(0.26f,0.15f,0.07f));
        }
    }

    if (ProductionCommonRopeCoilMesh)
    {
        SpawnShape(ProductionCommonRopeCoilMesh,FVector(NearX+90,-620,12),FVector(0.62f),FLinearColor::White,FRotator(0,25,0),false);
    }
    if (ProductionCommonReedClusterMesh)
    {
        SpawnShape(ProductionCommonReedClusterMesh,FVector(NearX-180,-880,0),FVector(0.82f),FLinearColor::White,FRotator(0,15,0),false);
        SpawnShape(ProductionCommonReedClusterMesh,FVector(FarX+170,-120,0),FVector(0.74f),FLinearColor::White,FRotator(0,-20,0),false);
    }
    if (ProductionCommonBoulderClusterMesh)
    {
        SpawnShape(ProductionCommonBoulderClusterMesh,FVector(NearX-250,-220,0),FVector(0.58f),FLinearColor::White,FRotator(0,35,0),true);
    }
    SpawnLabel(TEXT("Bucklebury Ferry"),FVector(NearX,-500,280),FLinearColor::White);

    // Distributed vegetation actors: visually important trees stay actors; ground cover is instanced.
    const FVector TreeLocations[] = {
        FVector(-2050,420,0),FVector(-1820,900,0),FVector(-1500,-980,0),FVector(-820,980,0),
        FVector(360,980,0),FVector(980,-820,0),FVector(2100,900,0),FVector(3000,-850,0),
        FVector(4800,900,0),FVector(5900,-900,0),FVector(7200,1250,0),FVector(8600,1050,0),
        FVector(10300,900,0),FVector(11200,-900,0),FVector(18100,800,0),FVector(20700,700,0),
        FVector(22200,-1300,0),FVector(24700,900,0)
    };
    for(const FVector& P:TreeLocations) SpawnTree(P,0.80f);

    // Ambient population ownership belongs exclusively to ALivingWorldDirector.
    // The director applies the chapter population target, pooling, culling, danger
    // thinning and micro-event/fauna budgets. Story/named actors remain builder-owned.

}


void AShirePrototypeWorldBuilder::SpawnPartySocialLoopPass()
{
    if (!GetWorld())
    {
        return;
    }

    const FVector PartyCenter(280.0f, 1320.0f, 0.0f);
    UStaticMesh* CommonSackBale = ResolveResidentStaticMesh(
        TEXT("/Game/Production/World/Common/SM_CommonSackBale.SM_CommonSackBale"));
    UStaticMesh* CommonCargoCrate = ResolveResidentStaticMesh(
        TEXT("/Game/Production/World/Common/SM_CommonCargoCrate.SM_CommonCargoCrate"));
    UStaticMesh* CommonFlowerPlanter = ResolveResidentStaticMesh(
        TEXT("/Game/Production/World/Common/SM_CommonFlowerPlanter.SM_CommonFlowerPlanter"));
    UStaticMesh* CommonLongBench = ResolveResidentStaticMesh(
        TEXT("/Game/Production/World/Common/SM_CommonLongBench.SM_CommonLongBench"));
    UStaticMesh* CommonMarketTable = ResolveResidentStaticMesh(
        TEXT("/Game/Production/World/Common/SM_CommonMarketTable.SM_CommonMarketTable"));
    UStaticMesh* CommonMarketCanopy = ProductionCommonMarketCanopyMesh;
    UStaticMesh* CommonWheelbarrow = ResolveResidentStaticMesh(
        TEXT("/Game/Production/World/Common/SM_CommonWheelbarrow.SM_CommonWheelbarrow"));
    UStaticMesh* CommonBarrel = ResolveResidentStaticMesh(
        TEXT("/Game/Production/World/Common/SM_CommonBarrel.SM_CommonBarrel"));

    int32 ClusterCount = 0;
    int32 InstanceCount = 0;
    auto SpawnPartyCluster = [this, &ClusterCount, &InstanceCount](
        UStaticMesh* Mesh, const TCHAR* Tag, int32 StartCull, int32 EndCull,
        const TArray<FTransform>& Placements)
    {
        if (!Mesh || Placements.Num() == 0)
        {
            return;
        }
        AWorldDetailCluster* Cluster = GetWorld()->SpawnActor<AWorldDetailCluster>();
        if (!Cluster)
        {
            return;
        }
        Cluster->Tags.AddUnique(TEXT("RuntimePrototypeGenerated"));
        Cluster->Tags.AddUnique(TEXT("P1C01PartySocialDetail"));
        Cluster->Tags.AddUnique(FName(Tag));
        Cluster->Configure(Mesh, false, StartCull, EndCull);
        for (const FTransform& T : Placements)
        {
            Cluster->AddDetailInstance(T.GetLocation(), T.Rotator(), T.GetScale3D());
        }
        ++ClusterCount;
        InstanceCount += Cluster->GetDetailCount();
    };

    auto RingPlacements = [&PartyCenter](float Radius, int32 Count, float Z, float Scale, float YawOffset)
    {
        TArray<FTransform> Out;
        Out.Reserve(Count);
        for (int32 Index = 0; Index < Count; ++Index)
        {
            const float Angle = (360.0f / static_cast<float>(Count)) * static_cast<float>(Index) + YawOffset;
            const float Radians = FMath::DegreesToRadians(Angle);
            const FVector P = PartyCenter + FVector(FMath::Cos(Radians) * Radius, FMath::Sin(Radians) * Radius, Z);
            Out.Emplace(FRotator(0.0f, Angle + 90.0f, 0.0f), P, FVector(Scale + 0.03f * static_cast<float>(Index % 3)));
        }
        return Out;
    };

    SpawnPartyCluster(CommonSackBale, TEXT("P1C01PartyFoodStores"), 800, 3800,
        RingPlacements(610.0f, 12, 0.0f, 0.55f, 5.0f));
    SpawnPartyCluster(CommonCargoCrate, TEXT("P1C01PartySupplyCrates"), 900, 4200,
        RingPlacements(760.0f, 12, 0.0f, 0.52f, 18.0f));
    SpawnPartyCluster(CommonFlowerPlanter, TEXT("P1C01PartyDecorPlanters"), 700, 3400,
        RingPlacements(500.0f, 12, 0.0f, 0.50f, 2.0f));
    SpawnPartyCluster(ProductionLanternMesh, TEXT("P1C01PartyLanternRing"), 1000, 4600,
        RingPlacements(880.0f, 12, 16.0f, 0.52f, 0.0f));

    int32 StaticPropCount = 0;
    auto SpawnPartyProp = [this, &StaticPropCount](
        UStaticMesh* Mesh, const FVector& Location, const FVector& Scale, const FRotator& Rotation)
    {
        AStaticMeshActor* Actor = SpawnShape(Mesh, Location, Scale, FLinearColor::White, Rotation, false);
        if (Actor)
        {
            Actor->Tags.AddUnique(TEXT("P1C01PartySocialDetail"));
            ++StaticPropCount;
        }
        return Actor;
    };

    const FVector TableOffsets[] = {
        FVector(-420,-150,0), FVector(-100,-190,0), FVector(240,-160,0),
        FVector(-310,170,0), FVector(40,210,0), FVector(380,150,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(TableOffsets); ++Index)
    {
        SpawnPartyProp(ProductionPicnicTableMesh, PartyCenter + TableOffsets[Index],
            FVector(0.72f), FRotator(0.0f, static_cast<float>((Index % 3) * 4 - 4), 0.0f));
    }
    SpawnPartyProp(CommonLongBench, PartyCenter + FVector(-560,40,0), FVector(0.68f), FRotator(0,8,0));
    SpawnPartyProp(CommonLongBench, PartyCenter + FVector(560,20,0), FVector(0.68f), FRotator(0,-8,0));
    SpawnPartyProp(CommonMarketCanopy, PartyCenter + FVector(-260,-400,0), FVector(0.68f), FRotator(0,6,0));
    SpawnPartyProp(CommonMarketCanopy, PartyCenter + FVector(300,-405,0), FVector(0.68f), FRotator(0,-6,0));
    SpawnPartyProp(ProductionLoadedCartMesh, PartyCenter + FVector(780,-360,0), FVector(0.58f), FRotator(0,95,0));
    SpawnPartyProp(CommonBarrel, PartyCenter + FVector(690,-250,0), FVector(0.60f), FRotator::ZeroRotator);
    SpawnPartyProp(CommonBarrel, PartyCenter + FVector(735,-205,0), FVector(0.56f), FRotator(0,15,0));
    SpawnPartyProp(ProductionHaystackMesh, PartyCenter + FVector(-760,-330,0), FVector(0.62f), FRotator(0,-12,0));

    auto SpawnStateProp = [this, &PartyCenter](
        TArray<AStaticMeshActor*>& Target, UStaticMesh* Mesh,
        const FVector& Offset, const FVector& Scale, const FRotator& Rotation, const TCHAR* Tag)
    {
        AStaticMeshActor* Actor = SpawnShape(Mesh, PartyCenter + Offset, Scale, FLinearColor::White, Rotation, false);
        if (!Actor)
        {
            return;
        }
        Actor->Tags.AddUnique(TEXT("P1C01PartyStateVariant"));
        Actor->Tags.AddUnique(FName(Tag));
        Actor->SetActorHiddenInGame(true);
        Actor->SetActorEnableCollision(false);
        Target.Add(Actor);
    };

    SpawnStateProp(PartySetupVariantActors, CommonWheelbarrow, FVector(-690,310,0), FVector(0.62f), FRotator(0,25,0), TEXT("P1C01PartySetupState"));
    SpawnStateProp(PartySetupVariantActors, CommonCargoCrate, FVector(-610,350,0), FVector(0.62f), FRotator(0,-8,0), TEXT("P1C01PartySetupState"));
    SpawnStateProp(PartySetupVariantActors, CommonMarketTable, FVector(610,345,0), FVector(0.68f), FRotator(0,5,0), TEXT("P1C01PartySetupState"));
    SpawnStateProp(PartySetupVariantActors, CommonSackBale, FVector(690,310,0), FVector(0.60f), FRotator(0,-12,0), TEXT("P1C01PartySetupState"));

    SpawnStateProp(PartyCelebrationVariantActors, ProductionLanternMesh, FVector(-480,410,20), FVector(0.68f), FRotator::ZeroRotator, TEXT("P1C01PartyCelebrationState"));
    SpawnStateProp(PartyCelebrationVariantActors, ProductionLanternMesh, FVector(500,410,20), FVector(0.68f), FRotator::ZeroRotator, TEXT("P1C01PartyCelebrationState"));
    SpawnStateProp(PartyCelebrationVariantActors, CommonMarketCanopy, FVector(-20,430,0), FVector(0.72f), FRotator(0,2,0), TEXT("P1C01PartyCelebrationState"));
    SpawnStateProp(PartyCelebrationVariantActors, ProductionMarketStallMesh, FVector(760,80,0), FVector(0.58f), FRotator(0,92,0), TEXT("P1C01PartyCelebrationState"));

    UE_LOG(
        LogTemp, Display,
        TEXT("PARTY_SOCIAL_LOOP_PASS clusters=%d instances=%d staticProps=%d setupProps=%d celebrationProps=%d populationTarget=18 collision=none tick=none"),
        ClusterCount, InstanceCount, StaticPropCount,
        PartySetupVariantActors.Num(), PartyCelebrationVariantActors.Num());
}


void AShirePrototypeWorldBuilder::SpawnSideStories()
{
    if (!GetWorld())
    {
        return;
    }

    AShireNPC* Hamfast=GetWorld()->SpawnActor<AShireNPC>(FVector(-2050,-690,65),FRotator(0,25,0));
    if(Hamfast)
    {
        Hamfast->DisplayName=FText::FromString(TEXT("Hamfast Gamgee"));
        Hamfast->DialogueLines={
            FText::FromString(TEXT("Frodo, if you have a moment, take a look along the lower garden fence. The party traffic has everyone cutting across the beds.")),
            FText::FromString(TEXT("Good soil asks for patience. Folk are much the same, if you ask me."))
        };
        Hamfast->SideStoryBeatAfterInteraction=TEXT("Side_GardenHelpStarted");
        Hamfast->SideStoryStartMessage=FText::FromString(TEXT("Optional: Walk the lower Bag End garden and check the fence."));
    }
    AShireQuestTrigger* GardenCheck=GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(-1740,-820,70),FRotator::ZeroRotator);
    if(GardenCheck)
    {
        GardenCheck->RequiredSideStoryBeat=TEXT("Side_GardenHelpStarted");
        GardenCheck->SideStoryBeatAfterTrigger=TEXT("Side_GardenHelpComplete");
        GardenCheck->ObjectiveMessage=FText::FromString(TEXT("Side story complete: the garden path and fence are clear before the party."));
    }

    AShireNPC* Rosie=GetWorld()->SpawnActor<AShireNPC>(FVector(-420,520,65),FRotator(0,205,0));
    if(Rosie)
    {
        Rosie->DisplayName=FText::FromString(TEXT("Rosie Cotton"));
        Rosie->DialogueLines={
            FText::FromString(TEXT("Half of Hobbiton seems to be carrying supper into that field. If you pass the party tables, make sure the far row has not been forgotten.")),
            FText::FromString(TEXT("Everyone says Bilbo planned too much. I think they will change their minds once the food arrives."))
        };
        Rosie->SideStoryBeatAfterInteraction=TEXT("Side_PartyTablesStarted");
        Rosie->SideStoryStartMessage=FText::FromString(TEXT("Optional: Check the far party tables before meeting Bilbo."));
    }
    AShireQuestTrigger* PartyTableCheck=GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(650,1480,75),FRotator::ZeroRotator);
    if(PartyTableCheck)
    {
        PartyTableCheck->RequiredSideStoryBeat=TEXT("Side_PartyTablesStarted");
        PartyTableCheck->SideStoryBeatAfterTrigger=TEXT("Side_PartyTablesComplete");
        PartyTableCheck->ObjectiveMessage=FText::FromString(TEXT("Side story complete: the last tables are ready for the celebration."));
    }

    // CP56 optional friendship/life beats: they enrich the film-spine opening
    // without blocking or reordering the main quest.
    AShireQuestTrigger* GreenDragonLife = GetWorld()->SpawnActor<AShireQuestTrigger>(
        FVector(-470, 520, 80), FRotator::ZeroRotator);
    if (GreenDragonLife)
    {
        GreenDragonLife->SideStoryBeatAfterTrigger = TEXT("Side_GreenDragonRevelry");
        GreenDragonLife->RequiredSideStoryBeat = TEXT("ShireOpening");
        GreenDragonLife->BlockedAfterStoryBeat = TEXT("PartyArrival");
        GreenDragonLife->DiscoveryId = TEXT("SHIRE_GREEN_DRAGON_MEMORY");
        // Keep the legacy discovery ID for save compatibility; only player-visible text is corrected.
        GreenDragonLife->DiscoveryDisplayName = FText::FromString(TEXT("Hobbiton Village Common"));
        GreenDragonLife->ObjectiveMessage = FText::FromString(
            TEXT("The village common is loud with friends, dancing and local gossip. Stay awhile or continue to the party."));
    }

    AShireTraversalChallenge* PartyPreparations = GetWorld()->SpawnActor<AShireTraversalChallenge>(
        FVector(-820, -420, 75), FRotator::ZeroRotator);
    if (PartyPreparations)
    {
        PartyPreparations->ConfigureActivityChallenge(
            TEXT("SHIRE_MARKET_GARDEN_LOOP"),
            FText::FromString(TEXT("Party Preparations")),
            TEXT("TIMING_CHALLENGE"),
            FVector(0, 0, 0),
            FVector(250, 120, 0),
            FVector(520, -40, 0),
            false,
            26.0f);
    }

    AShireQuestTrigger* PartyMischief = GetWorld()->SpawnActor<AShireQuestTrigger>(
        FVector(520, 1420, 80), FRotator::ZeroRotator);
    if (PartyMischief)
    {
        PartyMischief->RequiredSideStoryBeat = TEXT("Side_GreenDragonRevelry");
        PartyMischief->SideStoryBeatAfterTrigger = TEXT("Side_PartyMischief");
        PartyMischief->ObjectiveMessage = FText::FromString(
            TEXT("Laughter erupts near the fireworks wagon. Someone has clearly been where they were told not to be."));
    }

    // F1-01 birthday setup chain: three optional local beats, all invalid once
    // PartyArrival closes the preparation window.
    AShireQuestTrigger* PartyDecorations = GetWorld()->SpawnActor<AShireQuestTrigger>(
        FVector(-120, 1060, 75), FRotator::ZeroRotator);
    if (PartyDecorations)
    {
        PartyDecorations->RequiredSideStoryBeat = TEXT("ShireOpening");
        PartyDecorations->BlockedAfterStoryBeat = TEXT("PartyArrival");
        PartyDecorations->SideStoryBeatAfterTrigger = TEXT("Side_BirthdayDecorReady");
        PartyDecorations->ObjectiveMessage = FText::FromString(
            TEXT("Optional party setup: decorations and lantern positions are ready."));
    }

    AShireQuestTrigger* PartyFood = GetWorld()->SpawnActor<AShireQuestTrigger>(
        FVector(300, 1010, 75), FRotator::ZeroRotator);
    if (PartyFood)
    {
        PartyFood->RequiredSideStoryBeat = TEXT("Side_BirthdayDecorReady");
        PartyFood->BlockedAfterStoryBeat = TEXT("PartyArrival");
        PartyFood->SideStoryBeatAfterTrigger = TEXT("Side_BirthdayFoodReady");
        PartyFood->ObjectiveMessage = FText::FromString(
            TEXT("Optional party setup: food stores and serving tables are in place."));
    }

    AShireQuestTrigger* PartyGuests = GetWorld()->SpawnActor<AShireQuestTrigger>(
        FVector(610, 1220, 75), FRotator::ZeroRotator);
    if (PartyGuests)
    {
        PartyGuests->RequiredSideStoryBeat = TEXT("Side_BirthdayFoodReady");
        PartyGuests->BlockedAfterStoryBeat = TEXT("PartyArrival");
        PartyGuests->SideStoryBeatAfterTrigger = TEXT("Side_BirthdaySetupComplete");
        PartyGuests->ObjectiveMessage = FText::FromString(
            TEXT("Optional party setup complete: the field is ready for Bilbo's guests."));
    }

    AShireTraversalChallenge* FireworksSafety = GetWorld()->SpawnActor<AShireTraversalChallenge>(
        FVector(760, 1180, 75), FRotator::ZeroRotator);
    if (FireworksSafety)
    {
        FireworksSafety->ConfigureActivityChallenge(
            TEXT("SHIRE_FIREWORKS_SAFETY"),
            FText::FromString(TEXT("Gandalf's Fireworks")),
            TEXT("TIMING_CHALLENGE"),
            FVector(0, 0, 0),
            FVector(170, 120, 0),
            FVector(330, -20, 0),
            false,
            28.0f,
            TEXT("Side_FireworksSafetyComplete"));
    }

    AShireTraversalChallenge* DragonFireworkMishap = GetWorld()->SpawnActor<AShireTraversalChallenge>(
        FVector(430, 1510, 75), FRotator::ZeroRotator);
    if (DragonFireworkMishap)
    {
        DragonFireworkMishap->ConfigureActivityChallenge(
            TEXT("SHIRE_DRAGON_FIREWORK_MISHAP"),
            FText::FromString(TEXT("A Firework Best Left Alone")),
            TEXT("STEALTH_LITE"),
            FVector(0, 0, 0),
            FVector(150, 80, 0),
            FVector(290, -40, 0),
            true,
            0.0f,
            TEXT("Side_DragonFireworkMishapComplete"));
    }

    AShireTraversalChallenge* FieldRace = GetWorld()->SpawnActor<AShireTraversalChallenge>(
        FVector(600, 1100, 75), FRotator::ZeroRotator);
    if (FieldRace)
    {
        FieldRace->ConfigureChallenge(
            TEXT("SHIRE_FIELD_RACE"),
            FText::FromString(TEXT("A Last Race in the Shire")),
            TEXT("GandalfArrival"),
            TEXT("PartyArrival"),
            TEXT("Side_SharedShireMemory"),
            FVector(0, 0, 0),
            FVector(360, 120, 0),
            FVector(720, 140, 0));
    }

    AShireTraversalChallenge* QuietFeet = GetWorld()->SpawnActor<AShireTraversalChallenge>(
        FVector(980, -980, 75), FRotator::ZeroRotator);
    if (QuietFeet)
    {
        QuietFeet->ConfigureActivityChallenge(
            TEXT("SHIRE_QUIET_FEET"),
            FText::FromString(TEXT("Quiet Feet Through the Hedges")),
            TEXT("STEALTH_LITE"),
            FVector(0, 0, 0),
            FVector(260, 90, 0),
            FVector(520, -30, 0),
            true,
            0.0f);
    }

    AShireNPC* Maggot=GetWorld()->SpawnActor<AShireNPC>(FVector(6200,-1500,65),FRotator(0,155,0));
    if(Maggot)
    {
        Maggot->DisplayName=FText::FromString(TEXT("Farmer Maggot"));
        Maggot->DialogueLines={
            FText::FromString(TEXT("There have been strangers asking questions beyond the fields. If you are walking east, keep an eye on the old boundary fence.")),
            FText::FromString(TEXT("The crops are ordinary. The questions were not."))
        };
        Maggot->SideStoryBeatAfterInteraction=TEXT("Side_FieldWatchStarted");
        Maggot->SideStoryStartMessage=FText::FromString(TEXT("Optional: Follow the field edge and inspect the old boundary fence."));
    }
    AShireQuestTrigger* FieldWatch=GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(10100,-1180,75),FRotator::ZeroRotator);
    if(FieldWatch)
    {
        FieldWatch->RequiredSideStoryBeat=TEXT("Side_FieldWatchStarted");
        FieldWatch->SideStoryBeatAfterTrigger=TEXT("Side_FieldWatchComplete");
        FieldWatch->ObjectiveMessage=FText::FromString(TEXT("Side story complete: hoof marks and a disturbed fence lead toward the wooded road."));
    }

    struct FTalker
    {
        const TCHAR* Name;
        FVector Location;
        FRotator Rotation;
        const TCHAR* LineA;
        const TCHAR* LineB;
    };
    const FTalker Talkers[] = {
        { TEXT("Old Noakes"), FVector(-930,580,65), FRotator(0,210,0),
          TEXT("Too many carts on the lane today. Mark my words, a proper party begins with everyone arriving late."),
          TEXT("Still, it is good to see the Hill busy again.") },
        { TEXT("Party Cook"), FVector(40,1120,65), FRotator(0,90,0),
          TEXT("If one more cousin asks when supper begins, I shall put them to work peeling potatoes."),
          TEXT("Bilbo asked for enough food to feed the whole Shire. I suspect he meant it.") },
        { TEXT("Hobbiton Miller"), FVector(-1210,240,65), FRotator(0,140,0),
          TEXT("The wheel has been turning since sunrise. Party day or not, flour does not grind itself."),
          TEXT("Take the bridge slowly. Everyone is in too much of a hurry today.") },
        { TEXT("Market Gardener"), FVector(-620,250,65), FRotator(0,35,0),
          TEXT("Fresh onions, early carrots, and not one quiet customer since breakfast."),
          TEXT("Bilbo's party has emptied half the gardens in Hobbiton.") },
        { TEXT("Excited Party Guest"), FVector(420,1450,65), FRotator(0,210,0),
          TEXT("They say the fireworks came all the way from outside the Shire."),
          TEXT("I only hope Bilbo remembered enough benches for the relatives who arrive early.") },
        { TEXT("Hobbiton Field Hand"), FVector(6900,-1050,65), FRotator(0,250,0),
          TEXT("The road is quieter past the last hedges. Nice walking, if you do not mind being far from a warm kitchen."),
          TEXT("I would stay for the fireworks before going anywhere east.") },
        { TEXT("East Road Walker"), FVector(11600,1150,65), FRotator(0,270,0),
          TEXT("Past those hedges the road feels different. Less laughter, more wind."),
          TEXT("If you hear horses after dark, I would step well aside.") },
        { TEXT("Boundary Farmer"), FVector(9800,-1420,65), FRotator(0,30,0),
          TEXT("Something heavy crossed the fence last night. Not a cart, and not one of our ponies."),
          TEXT("I patched the rail. I did not follow the tracks.") },
        { TEXT("Ferry Keeper"), FVector(ShireLayout::FerryX-950,-260,65), FRotator(0,190,0),
          TEXT("The current is gentle now. It changes quickly when the wind turns."),
          TEXT("Keep the landing clear and the rope where you can reach it.") }
    };

    FActorSpawnParameters TalkerSpawnParams;
    TalkerSpawnParams.SpawnCollisionHandlingOverride =
        ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;
    for(const FTalker& Talker:Talkers)
    {
        AShireNPC* NPC=GetWorld()->SpawnActor<AShireNPC>(
            Talker.Location,Talker.Rotation,TalkerSpawnParams);
        if(NPC)
        {
            NPC->DisplayName=FText::FromString(Talker.Name);
            NPC->DialogueLines={FText::FromString(Talker.LineA),FText::FromString(Talker.LineB)};

            const FString TalkerName(Talker.Name);
            if (TalkerName == TEXT("Old Noakes"))
            {
                FShireDialogueVariant AfterParty;
                AfterParty.RequiredStoryBeat = TEXT("BilboDisappearance");
                AfterParty.Lines = {
                    FText::FromString(TEXT("I have seen strange departures before, but vanishing in front of half the Shire is showing off.")),
                    FText::FromString(TEXT("Everyone will have a version of the story by breakfast. None of them will agree."))
                };
                NPC->DialogueVariants.Add(AfterParty);
            }
            else if (TalkerName == TEXT("Hobbiton Miller"))
            {
                FShireDialogueVariant Leaving;
                Leaving.RequiredStoryBeat = TEXT("LeavingHomeRoad");
                Leaving.Lines = {
                    FText::FromString(TEXT("You are a long way from the party road now. Keep your provisions dry and your feet on the path.")),
                    FText::FromString(TEXT("The mill sounds farther away out here. That is how you know home is behind you."))
                };
                NPC->DialogueVariants.Add(Leaving);
            }
            else if (TalkerName == TEXT("Boundary Farmer"))
            {
                FShireDialogueVariant RiderSeen;
                RiderSeen.RequiredStoryBeat = TEXT("BlackRiderApproach");
                RiderSeen.Lines = {
                    FText::FromString(TEXT("That rider came through again. Never gave a name, only asked which road the Baggins folk had taken.")),
                    FText::FromString(TEXT("I would not stand in the open if you hear hoofbeats."))
                };
                NPC->DialogueVariants.Add(RiderSeen);
            }
            else if (TalkerName == TEXT("Ferry Keeper"))
            {
                FShireDialogueVariant DangerNear;
                DangerNear.RequiredQuestId = TEXT("FerryEscape");
                DangerNear.MinQuestStage = 0;
                DangerNear.Lines = {
                    FText::FromString(TEXT("No questions. Get the rope loose and keep the boat straight.")),
                    FText::FromString(TEXT("Whatever is behind you can argue with the river."))
                };
                NPC->DialogueVariants.Add(DangerNear);
            }
        }
    }
    struct FDiscovery
    {
        FVector Location;
        FName Beat;
        const TCHAR* Message;
    };

    const FDiscovery Discoveries[] = {
        { FVector(-1250,330,75), TEXT("Discover_ShireMill"), TEXT("Discovered: The Mill beside the Water.") },
        // Legacy discovery ID retained for existing saves; visible copy no longer misplaces Bywater's inn in Hobbiton.
        { FVector(-520,360,75), TEXT("Discover_GreenDragon"), TEXT("Discovered: Hobbiton village common.") },
        { FVector(280,1320,75), TEXT("Discover_PartyField"), TEXT("Discovered: Bilbo's Party Field.") },
        { FVector(10150,-1500,75), TEXT("Discover_OldBoundary"), TEXT("Discovered: the old eastern boundary and orchard.") },
        { FVector(14500,1180,75), TEXT("Discover_RootHide"), TEXT("Discovered: a hollow root beneath the wooded road.") },
        { FVector(ShireLayout::FerryX-700,-500,75), TEXT("Discover_BuckleburyFerry"), TEXT("Discovered: Bucklebury Ferry on the Brandywine.") }
    };

    for (const FDiscovery& Discovery : Discoveries)
    {
        AShireQuestTrigger* Trigger = GetWorld()->SpawnActor<AShireQuestTrigger>(Discovery.Location, FRotator::ZeroRotator);
        if (Trigger)
        {
            Trigger->SideStoryBeatAfterTrigger = Discovery.Beat;
            Trigger->ObjectiveMessage = FText::FromString(Discovery.Message);
        }
    }

}


void AShirePrototypeWorldBuilder::SpawnStoryActors()
{
    if (!GetWorld())
    {
        return;
    }

    AShireQuestTrigger* OpeningBeat=GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(-2320,-120,90),FRotator::ZeroRotator);
    if(OpeningBeat)
    {
        OpeningBeat->QuestId=TEXT("ShireArrival");
        OpeningBeat->RequiredStage=0;
        OpeningBeat->StageAfterTrigger=-1;
        OpeningBeat->StoryBeatId=TEXT("ShireOpening");
    }

    AShireNPC* GandalfRoad=GetWorld()->SpawnActor<AShireNPC>(FVector(-1950,-40,70),FRotator(0,180,0));
    if(GandalfRoad)
    {
        GandalfRoad->DisplayName=FText::FromString(TEXT("Gandalf"));
        GandalfRoad->ProductionCharacterId=TEXT("Gandalf");
        GandalfRoad->DialogueLines={
            FText::FromString(TEXT("The Shire has not changed much. That is part of its charm.")),
            FText::FromString(TEXT("Come. There is a party ahead, and an old friend waiting."))
        };
        GandalfRoad->QuestId=TEXT("ShireArrival");
        GandalfRoad->RequiredQuestStage=0;
        GandalfRoad->QuestStageAfterInteraction=1;
    }

    AShireQuestTrigger* BridgeTrigger=GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(-1050,90,90),FRotator::ZeroRotator);
    if(BridgeTrigger)
    {
        BridgeTrigger->QuestId=TEXT("ShireArrival");
        BridgeTrigger->RequiredStage=1;
        BridgeTrigger->StageAfterTrigger=2;
        BridgeTrigger->StoryBeatId=TEXT("GandalfArrival");
        BridgeTrigger->ObjectiveMessage=FText::FromString(TEXT("The road bends toward Hobbiton and the party field."));
    }

    AShireQuestTrigger* PartyApproach=GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(-60,980,90),FRotator::ZeroRotator);
    if(PartyApproach)
    {
        PartyApproach->QuestId=TEXT("ShireArrival");
        PartyApproach->RequiredStage=2;
        PartyApproach->StageAfterTrigger=3;
        PartyApproach->StoryBeatId=TEXT("PartyArrival");
        PartyApproach->ObjectiveMessage=FText::FromString(TEXT("Music and lanterns carry across the field."));
    }

    AShireNPC* Bilbo=GetWorld()->SpawnActor<AShireNPC>(FVector(420,1300,70),FRotator(0,220,0));
    if(Bilbo)
    {
        Bilbo->DisplayName=FText::FromString(TEXT("Bilbo"));
        Bilbo->ProductionCharacterId=TEXT("Bilbo");
        Bilbo->DialogueLines={
            FText::FromString(TEXT("Enjoy the evening, Frodo. I have been preparing for this one for quite some time.")),
            FText::FromString(TEXT("There are some things an old hobbit must finally leave behind."))
        };
        Bilbo->QuestId=TEXT("ShireArrival");
        Bilbo->RequiredQuestStage=3;
        Bilbo->QuestStageAfterInteraction=3;
        Bilbo->NextQuestId=TEXT("LongExpectedParty");
        Bilbo->NextQuestStage=1;
        Bilbo->bCompleteDialogueBeforeNextQuest=true;
    }

    AShireQuestTrigger* BagEndReturn=GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(-2140,-430,90),FRotator::ZeroRotator);
    if(BagEndReturn)
    {
        BagEndReturn->QuestId=TEXT("LongExpectedParty");
        BagEndReturn->RequiredStage=1;
        BagEndReturn->StageAfterTrigger=2;
        BagEndReturn->NextQuestId=TEXT("RingSecret");
        BagEndReturn->NextQuestStage=0;
        BagEndReturn->StoryBeatId=TEXT("BilboDisappearance");
        BagEndReturn->ObjectiveMessage=FText::FromString(TEXT("Bag End is quiet now. Gandalf is waiting inside."));
    }

    AShireQuestTrigger* RingWarningBeat=GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(-2160,-555,80),FRotator::ZeroRotator);
    if(RingWarningBeat)
    {
        RingWarningBeat->QuestId=TEXT("RingSecret");
        RingWarningBeat->RequiredStage=0;
        RingWarningBeat->StageAfterTrigger=-1;
        RingWarningBeat->StoryBeatId=TEXT("RingWarning");
    }

    AShireNPC* GandalfBagEnd=GetWorld()->SpawnActor<AShireNPC>(FVector(-2160,-610,70),FRotator(0,30,0));
    if(GandalfBagEnd)
    {
        GandalfBagEnd->DisplayName=FText::FromString(TEXT("Gandalf"));
        GandalfBagEnd->ProductionCharacterId=TEXT("Gandalf");
        GandalfBagEnd->DialogueLines={
            FText::FromString(TEXT("Keep the Ring hidden. Do not use it, and do not speak of it lightly.")),
            FText::FromString(TEXT("You must leave quietly. Sam can be trusted to go with you."))
        };
        GandalfBagEnd->QuestId=TEXT("RingSecret");
        GandalfBagEnd->RequiredQuestStage=0;
        GandalfBagEnd->QuestStageAfterInteraction=1;
    }

    AShireNPC* Sam=GetWorld()->SpawnActor<AShireNPC>(FVector(-1870,-560,65),FRotator(0,20,0));
    if(Sam)
    {
        Sam->DisplayName=FText::FromString(TEXT("Sam"));
        Sam->ProductionCharacterId=TEXT("Sam");
        Sam->DialogueLines={FText::FromString(TEXT("Wherever the road goes, Mr. Frodo, you will not be taking it alone."))};
        Sam->QuestId=TEXT("RingSecret");
        Sam->RequiredQuestStage=1;
        Sam->QuestStageAfterInteraction=2;
        Sam->NextQuestId=TEXT("LeavingHome");
        Sam->NextQuestStage=1;
        Sam->bFollowPlayerAfterInteraction=true;
    }

    AShireQuestTrigger* LeaveHobbiton=GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(ShireLayout::HobbitonExitX,0,90),FRotator::ZeroRotator);
    if(LeaveHobbiton)
    {
        LeaveHobbiton->QuestId=TEXT("LeavingHome");
        LeaveHobbiton->RequiredStage=1;
        LeaveHobbiton->StageAfterTrigger=2;
        LeaveHobbiton->NextQuestId=TEXT("Shortcut");
        LeaveHobbiton->NextQuestStage=0;
        LeaveHobbiton->StoryBeatId=TEXT("LeavingHomeRoad");
        LeaveHobbiton->ObjectiveMessage=FText::FromString(TEXT("The lanes of Hobbiton fall behind you. The eastern road stretches on."));
    }

    AShireQuestTrigger* CropFields=GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(6500,-420,90),FRotator::ZeroRotator);
    if(CropFields)
    {
        CropFields->QuestId=TEXT("Shortcut");
        CropFields->RequiredStage=0;
        CropFields->StageAfterTrigger=1;
        CropFields->ObjectiveMessage=FText::FromString(TEXT("Voices and crashing footsteps come from the crops ahead."));
    }

    AShireNPC* Merry=GetWorld()->SpawnActor<AShireNPC>(FVector(8100,-620,65),FRotator(0,200,0));
    if(Merry)
    {
        Merry->DisplayName=FText::FromString(TEXT("Merry"));
        Merry->DialogueLines={FText::FromString(TEXT("This is a fine mess. Whatever you are doing, we had better move before someone finds us."))};
        Merry->QuestId=TEXT("Shortcut");
        Merry->RequiredQuestStage=1;
        Merry->QuestStageAfterInteraction=1;
        Merry->SideStoryBeatAfterInteraction=TEXT("P1C01_MerryJoined");
        Merry->bFollowPlayerAfterInteraction=true;
        Merry->FollowActivationStoryBeat=TEXT("P1C01_MerryJoined");
    }

    AShireNPC* Pippin=GetWorld()->SpawnActor<AShireNPC>(FVector(8260,-760,65),FRotator(0,170,0));
    if(Pippin)
    {
        Pippin->DisplayName=FText::FromString(TEXT("Pippin"));
        Pippin->DialogueLines={FText::FromString(TEXT("If we are running, I would very much like to know what we are running from."))};
        Pippin->QuestId=TEXT("Shortcut");
        Pippin->RequiredQuestStage=1;
        Pippin->QuestStageAfterInteraction=1;
        Pippin->SideStoryBeatAfterInteraction=TEXT("P1C01_PippinJoined");
        Pippin->bFollowPlayerAfterInteraction=true;
        Pippin->FollowActivationStoryBeat=TEXT("P1C01_PippinJoined");
    }

    AShireQuestTrigger* CropCompanionsReady=GetWorld()->SpawnActor<AShireQuestTrigger>(
        FVector(8180,-690,90),FRotator::ZeroRotator);
    if(CropCompanionsReady)
    {
        CropCompanionsReady->TriggerBox->SetBoxExtent(FVector(520,520,180));
        CropCompanionsReady->QuestId=TEXT("Shortcut");
        CropCompanionsReady->RequiredStage=1;
        CropCompanionsReady->StageAfterTrigger=2;
        CropCompanionsReady->RequiredSideStoryBeat=TEXT("P1C01_MerryJoined");
        CropCompanionsReady->AdditionalRequiredSideStoryBeat=TEXT("P1C01_PippinJoined");
        CropCompanionsReady->ObjectiveMessage=
            FText::FromString(TEXT("Merry and Pippin fall in beside you. Move together toward the wooded road."));
    }

    AShireQuestTrigger* WoodedRoad=GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(12000,920,90),FRotator::ZeroRotator);
    if(WoodedRoad)
    {
        WoodedRoad->QuestId=TEXT("Shortcut");
        WoodedRoad->RequiredStage=2;
        WoodedRoad->StageAfterTrigger=2;
        WoodedRoad->NextQuestId=TEXT("KeepOffRoad");
        WoodedRoad->NextQuestStage=0;
        WoodedRoad->StoryBeatId=TEXT("BlackRiderApproach");
        WoodedRoad->ObjectiveMessage=FText::FromString(TEXT("Hoofbeats. Something is coming along the road."));
    }

    ABlackRiderPrototype* Rider=GetWorld()->SpawnActor<ABlackRiderPrototype>(FVector(ShireLayout::WoodedRoadX,-120,35),FRotator::ZeroRotator);
    if(Rider)
    {
        Rider->PatrolA=FVector(13600,-520,35);
        Rider->PatrolB=FVector(16100,720,35);
        Rider->DetectionRadius=760.0f;
        Rider->CrouchedDetectionRadius=330.0f;
        Rider->InvestigationDuration=5.5f;
    }

    AShireQuestTrigger* HideUnderRoad=GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(14500,1160,70),FRotator::ZeroRotator);
    if(HideUnderRoad)
    {
        HideUnderRoad->QuestId=TEXT("KeepOffRoad");
        HideUnderRoad->RequiredStage=0;
        HideUnderRoad->StageAfterTrigger=1;
        HideUnderRoad->StoryBeatId=TEXT("RootHide");
        HideUnderRoad->ObjectiveMessage=FText::FromString(TEXT("Stay low and keep out of the Rider's sight."));
    }

    AShireQuestTrigger* EscapeForest=GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(17600,-700,90),FRotator::ZeroRotator);
    if(EscapeForest)
    {
        EscapeForest->QuestId=TEXT("KeepOffRoad");
        EscapeForest->RequiredStage=1;
        EscapeForest->StageAfterTrigger=2;
        EscapeForest->NextQuestId=TEXT("FerryEscape");
        EscapeForest->NextQuestStage=0;
        EscapeForest->ObjectiveMessage=FText::FromString(TEXT("The trees thin ahead. Keep moving for the Brandywine."));
    }

    const float NearX=ShireLayout::FerryX-700.0f;
    const float FarX=ShireLayout::FerryX+700.0f;

    AShireQuestTrigger* FerryNearSide=GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(NearX,-500,90),FRotator::ZeroRotator);
    if(FerryNearSide)
    {
        FerryNearSide->QuestId=TEXT("FerryEscape");
        FerryNearSide->RequiredStage=0;
        FerryNearSide->StageAfterTrigger=1;
        FerryNearSide->StoryBeatId=TEXT("FerryEscape");
        FerryNearSide->ObjectiveMessage=FText::FromString(TEXT("Push off and get across the Brandywine."));
    }

    AShireQuestTrigger* FerryFarSide=GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(FarX,-500,90),FRotator::ZeroRotator);
    if(FerryFarSide)
    {
        FerryFarSide->QuestId=TEXT("FerryEscape");
        FerryFarSide->RequiredStage=1;
        FerryFarSide->StageAfterTrigger=2;
        FerryFarSide->NextChapterId=TEXT("P1C02");
        FerryFarSide->NextChapterQuestId=TEXT("RoadToBree");
        FerryFarSide->NextChapterQuestStage=0;
        FerryFarSide->ObjectiveMessage=FText::FromString(TEXT("Across the river. The road to Bree begins here."));
    }
}



void AShirePrototypeWorldBuilder::SpawnGeographyFoundationPass()
{
    if (!GeographyHillInstances || !GeographySlopeInstances || !GeographyRiverBankInstances)
    {
        return;
    }

    GeographyHillInstances->ClearInstances();
    GeographySlopeInstances->ClearInstances();
    GeographyRiverBankInstances->ClearInstances();

    int32 HillCount = 0;
    int32 SlopeCount = 0;
    int32 BankCount = 0;

    if (ProductionCommonTerracedHillMesh)
    {
        struct FGeoPlacement
        {
            FVector Location;
            FVector Scale;
            float Yaw;
        };

        // Pastoral sightline breaks frame the playable route without moving any
        // story/quest anchor. Later areas should reveal through travel, not from Bag End.
        const FGeoPlacement Hills[] = {
            { FVector(-2850,2050,-175), FVector(3.15f,2.40f,1.55f), -18.0f },
            { FVector(-2250,1650,-145), FVector(3.05f,2.25f,1.45f), 12.0f },
            { FVector(-1200,1900,-165), FVector(2.85f,2.30f,1.45f), 31.0f },
            { FVector(150,1880,-160), FVector(3.20f,2.35f,1.48f), 62.0f },
            { FVector(1350,1650,-150), FVector(2.95f,2.20f,1.42f), 95.0f },
            { FVector(3600,2020,-170), FVector(3.10f,2.30f,1.48f), 18.0f },
            { FVector(6100,2050,-175), FVector(3.30f,2.35f,1.52f), 42.0f },
            { FVector(7900,2150,-180), FVector(3.10f,2.45f,1.50f), 78.0f },
            { FVector(10200,2250,-185), FVector(3.45f,2.50f,1.55f), 104.0f },
            { FVector(13200,2300,-190), FVector(3.35f,2.45f,1.58f), 132.0f },
            { FVector(15100,2180,-185), FVector(3.15f,2.35f,1.52f), 166.0f },
            { FVector(17600,2280,-190), FVector(3.45f,2.55f,1.58f), 205.0f },
            { FVector(20500,2350,-195), FVector(3.55f,2.60f,1.62f), 244.0f },
            { FVector(22800,2100,-180), FVector(3.20f,2.40f,1.50f), 282.0f },
            { FVector(24900,1880,-170), FVector(3.10f,2.35f,1.48f), 318.0f }
        };

        for (const FGeoPlacement& P : Hills)
        {
            GeographyHillInstances->AddInstance(
                FTransform(FRotator(0.0f, P.Yaw, 0.0f), P.Location, P.Scale));
            ++HillCount;
        }
    }

    if (ProductionCommonVillageSlopeMesh)
    {
        struct FSlopePlacement
        {
            FVector Location;
            FVector Scale;
            float Yaw;
        };

        const FSlopePlacement Slopes[] = {
            { FVector(-2550,-1700,-90), FVector(2.45f,1.90f,1.28f), 8.0f },
            { FVector(-650,-1750,-95), FVector(2.35f,1.85f,1.25f), -10.0f },
            { FVector(2450,-1850,-92), FVector(2.55f,1.95f,1.26f), 7.0f },
            { FVector(4550,-2050,-98), FVector(2.65f,2.00f,1.30f), -12.0f },
            { FVector(6200,-2350,-100), FVector(2.50f,1.90f,1.28f), 8.0f },
            { FVector(8850,-2200,-95), FVector(2.55f,1.95f,1.28f), -10.0f },
            { FVector(11200,-2150,-100), FVector(2.70f,2.00f,1.32f), 6.0f },
            { FVector(13700,-2250,-105), FVector(2.60f,1.95f,1.30f), -9.0f },
            { FVector(16000,-2100,-95), FVector(2.55f,1.90f,1.28f), 8.0f },
            { FVector(18600,-2150,-100), FVector(2.75f,2.00f,1.32f), -7.0f },
            { FVector(21100,-2050,-95), FVector(2.60f,1.95f,1.30f), 10.0f },
            { FVector(24600,-1850,-90), FVector(2.45f,1.85f,1.25f), -8.0f }
        };

        for (const FSlopePlacement& P : Slopes)
        {
            GeographySlopeInstances->AddInstance(
                FTransform(FRotator(0.0f, P.Yaw, 0.0f), P.Location, P.Scale));
            ++SlopeCount;
        }
    }

    if (ProductionCommonRiverBankMesh)
    {
        struct FBankPlacement
        {
            FVector Location;
            FVector Scale;
            float Yaw;
        };

        const FBankPlacement Banks[] = {
            { FVector(-1380,260,-32), FVector(1.35f,0.92f,0.72f), 86.0f },
            { FVector(-760,350,-32), FVector(1.35f,0.92f,0.72f), 266.0f },
            { FVector(22650,-1220,-35), FVector(2.80f,1.50f,1.00f), 2.0f },
            { FVector(22950,420,-35), FVector(2.80f,1.50f,1.00f), 178.0f },
            { FVector(23950,-1220,-35), FVector(2.80f,1.50f,1.00f), 2.0f },
            { FVector(24250,420,-35), FVector(2.80f,1.50f,1.00f), 178.0f }
        };

        for (const FBankPlacement& P : Banks)
        {
            GeographyRiverBankInstances->AddInstance(
                FTransform(FRotator(0.0f, P.Yaw, 0.0f), P.Location, P.Scale));
            ++BankCount;
        }
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireWorldFoundation: geography-pass hills=%d slopes=%d banks=%d route=BagEnd-Hobbiton-Fields-WoodedRoad-Ferry"),
        HillCount,
        SlopeCount,
        BankCount);
}


void AShirePrototypeWorldBuilder::SpawnHobbitonArchitecturePass()
{
    // Drop B uses already-resident production meshes only. Missing optional meshes
    // simply remove dressing; they never trigger synchronous runtime loads.
    auto ResolveShire = [](const TCHAR* Path) -> UStaticMesh*
    {
        return ResolveResidentStaticMesh(Path);
    };

    auto SpawnProd = [this](UStaticMesh* Mesh, const FVector& Location, const FVector& Scale,
        const FRotator& Rotation = FRotator::ZeroRotator, bool bCollision = true)
    {
        if (Mesh)
        {
            SpawnShape(Mesh, Location, Scale, FLinearColor::White, Rotation, bCollision);
        }
    };

    UStaticMesh* GardenArch = ResolveShire(TEXT("/Game/Production/World/Shire/SM_ShGardenArch.SM_ShGardenArch"));
    UStaticMesh* Mailbox = ResolveShire(TEXT("/Game/Production/World/Shire/SM_ShMailbox.SM_ShMailbox"));
    UStaticMesh* PicnicCanopy = ResolveShire(TEXT("/Game/Production/World/Shire/SM_ShPicnicCanopy.SM_ShPicnicCanopy"));
    UStaticMesh* ProduceStand = ResolveShire(TEXT("/Game/Production/World/Shire/SM_ShProduceStand.SM_ShProduceStand"));
    UStaticMesh* PumpWell = ResolveShire(TEXT("/Game/Production/World/Shire/SM_ShPumpWell.SM_ShPumpWell"));
    UStaticMesh* WashLine = ResolveShire(TEXT("/Game/Production/World/Shire/SM_ShWashLine.SM_ShWashLine"));
    UStaticMesh* FarmPlough = ResolveShire(TEXT("/Game/Production/World/Shire/SM_ShFarmPlough.SM_ShFarmPlough"));
    UStaticMesh* OrchardLadder = ResolveShire(TEXT("/Game/Production/World/Shire/SM_ShOrchardLadder.SM_ShOrchardLadder"));
    UStaticMesh* FlowerPlanter = ResolveShire(TEXT("/Game/Production/World/Common/SM_CommonFlowerPlanter.SM_CommonFlowerPlanter"));
    UStaticMesh* LongBench = ResolveShire(TEXT("/Game/Production/World/Common/SM_CommonLongBench.SM_CommonLongBench"));

    // Bag End is the dominant Hobbiton landmark and narrative return point.
    // Keep the existing story/quest anchor fixed; enrich only its architectural read.
    const FVector BagEnd(-2210.0f, -520.0f, 0.0f);
    SpawnProd(GardenArch, BagEnd + FVector(260.0f, -10.0f, 0.0f), FVector(0.90f),
        FRotator(0.0f, 90.0f, 0.0f), true);
    SpawnProd(Mailbox, BagEnd + FVector(245.0f, -150.0f, 0.0f), FVector(0.72f),
        FRotator(0.0f, 82.0f, 0.0f), false);
    SpawnProd(ProductionBenchMesh, BagEnd + FVector(170.0f, 185.0f, 0.0f), FVector(0.72f),
        FRotator(0.0f, -8.0f, 0.0f), true);
    SpawnProd(FlowerPlanter, BagEnd + FVector(45.0f, -155.0f, 0.0f), FVector(0.78f),
        FRotator(0.0f, 6.0f, 0.0f), false);
    SpawnProd(FlowerPlanter, BagEnd + FVector(45.0f, 155.0f, 0.0f), FVector(0.78f),
        FRotator(0.0f, -6.0f, 0.0f), false);
    SpawnProd(ProductionLampPostMesh, BagEnd + FVector(320.0f, 120.0f, 0.0f), FVector(0.72f),
        FRotator::ZeroRotator, false);

    const FVector BagEndWalls[] = {
        BagEnd + FVector(40.0f,-330.0f,0.0f),
        BagEnd + FVector(420.0f,-330.0f,0.0f),
        BagEnd + FVector(40.0f,330.0f,0.0f),
        BagEnd + FVector(420.0f,330.0f,0.0f)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(BagEndWalls); ++Index)
    {
        SpawnProd(ProductionStoneWallMesh, BagEndWalls[Index], FVector(0.72f),
            FRotator(0.0f, 90.0f, 0.0f), true);
    }
    SpawnProd(ProductionFarmGateMesh, BagEnd + FVector(470.0f,-40.0f,0.0f), FVector(0.72f),
        FRotator(0.0f,90.0f,0.0f), true);

    // Domestic clusters reinforce warm scale and garden/property rhythm without
    // challenging Bag End's silhouette dominance.
    struct FDomesticCluster
    {
        FVector Center;
        float Yaw;
    };
    const FDomesticCluster Clusters[] = {
        { FVector(-1660.0f, 610.0f, 0.0f), 20.0f },
        { FVector(-760.0f, -610.0f, 0.0f), -15.0f },
        { FVector(320.0f, 760.0f, 0.0f), 16.0f },
        { FVector(1120.0f, -620.0f, 0.0f), -18.0f }
    };

    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Clusters); ++Index)
    {
        const FDomesticCluster& C = Clusters[Index];
        SpawnProd(GardenArch, C.Center + FVector(165.0f, 0.0f, 0.0f), FVector(0.62f),
            FRotator(0.0f, C.Yaw + 90.0f, 0.0f), true);
        SpawnProd(ProductionFlowerBoxMesh, C.Center + FVector(55.0f,-135.0f,0.0f), FVector(0.58f),
            FRotator(0.0f, C.Yaw, 0.0f), false);
        SpawnProd(ProductionFlowerBoxMesh, C.Center + FVector(55.0f,135.0f,0.0f), FVector(0.58f),
            FRotator(0.0f, C.Yaw, 0.0f), false);
        if ((Index % 2) == 0)
        {
            SpawnProd(Mailbox, C.Center + FVector(220.0f,-115.0f,0.0f), FVector(0.54f),
                FRotator(0.0f, C.Yaw + 75.0f, 0.0f), false);
        }
        else
        {
            SpawnProd(LongBench, C.Center + FVector(205.0f,120.0f,0.0f), FVector(0.60f),
                FRotator(0.0f, C.Yaw, 0.0f), true);
        }
    }

    // Village common: social/readable space, deliberately not identified as the
    // Green Dragon because that canonical inn belongs at Bywater.
    const FVector CommonCenter(-520.0f, 360.0f, 0.0f);
    SpawnProd(PumpWell, CommonCenter + FVector(360.0f,-40.0f,0.0f), FVector(0.70f),
        FRotator::ZeroRotator, true);
    SpawnProd(ProduceStand, CommonCenter + FVector(-360.0f,-150.0f,0.0f), FVector(0.70f),
        FRotator(0.0f, 8.0f, 0.0f), true);
    SpawnProd(ProduceStand, CommonCenter + FVector(-160.0f,-210.0f,0.0f), FVector(0.66f),
        FRotator(0.0f,-6.0f,0.0f), true);

    // F1-01 birthday/social space. Keep this readable as a destination separate
    // from Bag End while reusing the existing party field story location.
    const FVector PartyCenter(280.0f,1320.0f,0.0f);
    SpawnProd(PicnicCanopy, PartyCenter + FVector(0.0f,30.0f,0.0f), FVector(0.92f),
        FRotator(0.0f,-4.0f,0.0f), true);
    SpawnProd(ProduceStand, PartyCenter + FVector(-540.0f,80.0f,0.0f), FVector(0.66f),
        FRotator(0.0f,12.0f,0.0f), true);
    SpawnProd(ProduceStand, PartyCenter + FVector(520.0f,70.0f,0.0f), FVector(0.66f),
        FRotator(0.0f,-12.0f,0.0f), true);

    // Working Shire details around the eastward domestic edge.
    SpawnProd(WashLine, FVector(1700.0f,640.0f,0.0f), FVector(0.68f),
        FRotator(0.0f,8.0f,0.0f), false);
    SpawnProd(FarmPlough, FVector(5650.0f,-1570.0f,0.0f), FVector(0.70f),
        FRotator(0.0f,-12.0f,0.0f), true);
    SpawnProd(OrchardLadder, FVector(9950.0f,-1350.0f,0.0f), FVector(0.66f),
        FRotator(0.0f,16.0f,0.0f), true);

    UE_LOG(
        LogTemp,
        Display,
        TEXT("ShireArchitecture: DropB BagEnd=hero Hobbiton=domestic PartyField=prepared canonGreenDragon=Bywater interior=deferred"));
}


void AShirePrototypeWorldBuilder::SpawnProductionVillageDetailLayer()
{
    // CP40 visual-production layer. This pass deliberately prefers imported original
    // project meshes and skips a detail when its production asset is unavailable.
    // It overlays the earlier traversal-safe blockout without changing quest anchors.

    auto SpawnProd = [this](UStaticMesh* Mesh, const FVector& Location, const FVector& Scale,
        const FRotator& Rotation = FRotator::ZeroRotator, bool bCollision = true)
    {
        if (Mesh)
        {
            SpawnShape(Mesh, Location, Scale, FLinearColor::White, Rotation, bCollision);
        }
    };

    // W01 geography foundation owns repeated hills/slopes/river banks through HISM.
    // Keep this detail layer focused on authored architecture and local props.

    const FVector BoulderGroups[] = {
        FVector(10800,-1280,0), FVector(12850,1480,0), FVector(15300,-1380,0),
        FVector(18200,1350,0), FVector(21700,-1280,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(BoulderGroups); ++Index)
    {
        SpawnProd(ProductionCommonBoulderClusterMesh, BoulderGroups[Index],
            FVector(0.95f + 0.12f * (Index % 3)),
            FRotator(0.0f, static_cast<float>((Index * 47) % 360), 0.0f), false);
    }

    // Above-ground cottages make Hobbiton read as a lived-in settlement rather than
    // only a line of turf mounds.
    const struct FCottagePlacement
    {
        FVector Location;
        float Scale;
        float Yaw;
    } Cottages[] = {
        { FVector(-1840, 420, 0), 0.72f, 12.0f },
        { FVector(-1320, -330, 0), 0.78f, -18.0f },
        { FVector(-760, 760, 0), 0.66f, 25.0f },
        { FVector(120, 540, 0), 0.72f, -12.0f },
        { FVector(840, -420, 0), 0.76f, 18.0f },
        { FVector(1540, 520, 0), 0.70f, -28.0f }
    };
    for (const FCottagePlacement& P : Cottages)
    {
        SpawnProd(ProductionCottageHouseMesh, P.Location, FVector(P.Scale),
            FRotator(0.0f, P.Yaw, 0.0f), true);
        SpawnProd(ProductionFlowerBoxMesh, P.Location + FVector(-55.0f, -155.0f, 0.0f),
            FVector(P.Scale * 0.65f), FRotator(0.0f, P.Yaw, 0.0f), false);
    }

    // Hobbiton village-common visual shell and social yard.
    SpawnProd(ProductionCottageHouseMesh, FVector(-520, 360, 0), FVector(1.28f, 1.15f, 1.18f),
        FRotator(0.0f, -8.0f, 0.0f), true);
    SpawnProd(ProductionWellMesh, FVector(-120, 300, 0), FVector(0.82f), FRotator::ZeroRotator, true);

    const FVector Market[] = {
        FVector(-830,205,0), FVector(-650,170,0), FVector(-470,165,0),
        FVector(-285,230,0), FVector(-95,180,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Market); ++Index)
    {
        SpawnProd(ProductionMarketStallMesh, Market[Index], FVector(0.62f),
            FRotator(0.0f, -8.0f + 4.0f * Index, 0.0f), true);
    }

    // Replace the visual read of the primitive mill/bridge with authored production shells.
    SpawnProd(ProductionMillHouseMesh, FVector(-1250, 330, 0), FVector(0.90f),
        FRotator(0.0f, 0.0f, 0.0f), true);
    SpawnProd(ProductionStoneBridgeMesh, FVector(-1050, 90, 0), FVector(0.82f),
        FRotator(0.0f, 0.0f, 0.0f), true);

    // Dry-stone boundaries and timber gates establish fields and property edges.
    const FVector WallCenters[] = {
        FVector(-2070,-930,0), FVector(-1600,-930,0), FVector(-1110,-930,0),
        FVector(320,430,0), FVector(790,430,0), FVector(6080,-1900,0),
        FVector(6510,-1900,0), FVector(6940,-1900,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(WallCenters); ++Index)
    {
        SpawnProd(ProductionStoneWallMesh, WallCenters[Index], FVector(0.78f),
            FRotator(0.0f, Index < 5 ? 0.0f : 4.0f, 0.0f), true);
    }
    SpawnProd(ProductionFarmGateMesh, FVector(-1350,-930,0), FVector(0.78f), FRotator::ZeroRotator, true);
    SpawnProd(ProductionFarmGateMesh, FVector(6750,-1885,0), FVector(0.92f), FRotator::ZeroRotator, true);

    // Farming clutter gives the East Fields visible work history.
    const FVector Hay[] = {
        FVector(5980,-1480,0), FVector(6280,-1320,0), FVector(7050,-1180,0),
        FVector(8050,-780,0), FVector(8450,-560,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Hay); ++Index)
    {
        SpawnProd(ProductionHaystackMesh, Hay[Index], FVector(0.70f + 0.06f * (Index % 3)),
            FRotator(0.0f, static_cast<float>((Index * 37) % 180), 0.0f), true);
    }
    SpawnProd(ProductionLoadedCartMesh, FVector(6200,-1570,0), FVector(0.72f),
        FRotator(0.0f, 16.0f, 0.0f), true);
    SpawnProd(ProductionLoadedCartMesh, FVector(8750,-1080,0), FVector(0.78f),
        FRotator(0.0f, -12.0f, 0.0f), true);

    // Party Field gets real tables and warm lamp-post silhouettes.
    const FVector PartyCenter(280.0f,1320.0f,0.0f);
    const FVector PartyTables[] = {
        PartyCenter + FVector(-420,-150,0), PartyCenter + FVector(-100,-190,0),
        PartyCenter + FVector(240,-160,0), PartyCenter + FVector(-310,170,0),
        PartyCenter + FVector(40,210,0), PartyCenter + FVector(380,150,0)
    };
    for (const FVector& Table : PartyTables)
    {
        SpawnProd(ProductionPicnicTableMesh, Table, FVector(0.72f), FRotator::ZeroRotator, true);
    }

    const FVector Lamps[] = {
        PartyCenter + FVector(-520,-300,0), PartyCenter + FVector(520,-300,0),
        PartyCenter + FVector(-520,320,0), PartyCenter + FVector(520,320,0),
        FVector(-920, 120, 0), FVector(-620, 110, 0), FVector(-300, 125, 0),
        FVector(20, 140, 0), FVector(340, 110, 0)
    };
    for (const FVector& Lamp : Lamps)
    {
        SpawnProd(ProductionLampPostMesh, Lamp, FVector(0.76f), FRotator::ZeroRotator, false);
    }
    // CP54 mega inventory pass: dense farm, market, river and household activity props.
    auto LoadCP54 = [](const TCHAR* Path) -> UStaticMesh* { return ResolveResidentStaticMesh(Path); };
    UStaticMesh* CP54Bucket = LoadCP54(TEXT("/Game/Production/World/Common/SM_CommonBucket.SM_CommonBucket"));
    UStaticMesh* CP54Wheelbarrow = LoadCP54(TEXT("/Game/Production/World/Common/SM_CommonWheelbarrow.SM_CommonWheelbarrow"));
    UStaticMesh* CP54Table = LoadCP54(TEXT("/Game/Production/World/Common/SM_CommonMarketTable.SM_CommonMarketTable"));
    UStaticMesh* CP54Chest = LoadCP54(TEXT("/Game/Production/World/Common/SM_CommonStorageChest.SM_CommonStorageChest"));
    UStaticMesh* CP54Beehive = LoadCP54(TEXT("/Game/Production/World/Common/SM_CommonBeehive.SM_CommonBeehive"));
    UStaticMesh* CP54Coop = LoadCP54(TEXT("/Game/Production/World/Common/SM_CommonChickenCoop.SM_CommonChickenCoop"));
    UStaticMesh* CP54Scarecrow = LoadCP54(TEXT("/Game/Production/World/Common/SM_CommonScarecrow.SM_CommonScarecrow"));
    UStaticMesh* CP54Wagon = LoadCP54(TEXT("/Game/Production/World/Common/SM_CommonWagon.SM_CommonWagon"));
    UStaticMesh* CP54Planter = LoadCP54(TEXT("/Game/Production/World/Common/SM_CommonFlowerPlanter.SM_CommonFlowerPlanter"));
    UStaticMesh* CP54Plough = LoadCP54(TEXT("/Game/Production/World/Shire/SM_ShFarmPlough.SM_ShFarmPlough"));
    UStaticMesh* CP54GardenArch = LoadCP54(TEXT("/Game/Production/World/Shire/SM_ShGardenArch.SM_ShGardenArch"));
    UStaticMesh* CP54Mailbox = LoadCP54(TEXT("/Game/Production/World/Shire/SM_ShMailbox.SM_ShMailbox"));
    UStaticMesh* CP54WashLine = LoadCP54(TEXT("/Game/Production/World/Shire/SM_ShWashLine.SM_ShWashLine"));
    UStaticMesh* CP54Produce = LoadCP54(TEXT("/Game/Production/World/Shire/SM_ShProduceStand.SM_ShProduceStand"));
    UStaticMesh* CP54Well = LoadCP54(TEXT("/Game/Production/World/Shire/SM_ShPumpWell.SM_ShPumpWell"));
    UStaticMesh* CP54Ladder = LoadCP54(TEXT("/Game/Production/World/Shire/SM_ShOrchardLadder.SM_ShOrchardLadder"));
    UStaticMesh* CP54Canopy = LoadCP54(TEXT("/Game/Production/World/Shire/SM_ShPicnicCanopy.SM_ShPicnicCanopy"));
    const FVector CP54FarmNodes[] = {
        FVector(3600,-1320,0), FVector(4100,-1370,0), FVector(4700,-1300,0),
        FVector(7900,1290,0), FVector(8500,1340,0), FVector(9100,1270,0),
        FVector(16200,-1220,0), FVector(16800,-1280,0), FVector(17450,-1180,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(CP54FarmNodes); ++Index)
    {
        UStaticMesh* Choice = Index % 3 == 0 ? CP54Plough : (Index % 3 == 1 ? CP54Wheelbarrow : CP54Scarecrow);
        SpawnProd(Choice, CP54FarmNodes[Index], FVector(0.64f + 0.04f * (Index % 2)), FRotator(0.0f, static_cast<float>((Index * 37) % 360), 0.0f), false);
    }
    const FVector CP54VillageNodes[] = {
        FVector(-880,-420,0), FVector(-620,420,0), FVector(-320,-460,0), FVector(-40,440,0),
        FVector(260,-430,0), FVector(520,450,0), FVector(810,-390,0), FVector(1030,410,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(CP54VillageNodes); ++Index)
    {
        UStaticMesh* Choice = Index % 4 == 0 ? CP54Mailbox : (Index % 4 == 1 ? CP54Planter : (Index % 4 == 2 ? CP54Bucket : CP54Chest));
        SpawnProd(Choice, CP54VillageNodes[Index], FVector(0.62f), FRotator(0.0f, static_cast<float>((Index * 51) % 360), 0.0f), false);
    }
    SpawnProd(CP54Produce, FVector(-260,120,0), FVector(0.72f), FRotator(0,4,0), false);
    SpawnProd(CP54Produce, FVector(340,-90,0), FVector(0.70f), FRotator(0,-5,0), false);
    SpawnProd(CP54Table, FVector(40,250,0), FVector(0.70f), FRotator(0,8,0), false);
    SpawnProd(CP54Canopy, FVector(40,250,0), FVector(0.78f), FRotator(0,8,0), false);
    SpawnProd(CP54GardenArch, FVector(11900,180,0), FVector(0.74f), FRotator(0,90,0), false);
    SpawnProd(CP54WashLine, FVector(12600,-650,0), FVector(0.68f), FRotator(0,8,0), false);
    SpawnProd(CP54Well, FVector(13200,540,0), FVector(0.70f), FRotator::ZeroRotator, false);
    SpawnProd(CP54Ladder, FVector(14200,-760,0), FVector(0.66f), FRotator(0,15,0), false);
    SpawnProd(CP54Beehive, FVector(14900,780,0), FVector(0.66f), FRotator(0,-10,0), false);
    SpawnProd(CP54Beehive, FVector(15100,820,0), FVector(0.62f), FRotator(0,12,0), false);
    SpawnProd(CP54Coop, FVector(15650,-760,0), FVector(0.66f), FRotator(0,8,0), false);
    SpawnProd(CP54Wagon, FVector(18400,-520,0), FVector(0.66f), FRotator(0,3,0), false);

}

void AShirePrototypeWorldBuilder::SpawnBagEndHeroPass()
{
    if (!GetWorld())
    {
        return;
    }

    const FVector BagEnd(-2210.0f, -520.0f, 0.0f);

    UStaticMesh* CommonFlowerPlanter = ResolveResidentStaticMesh(
        TEXT("/Game/Production/World/Common/SM_CommonFlowerPlanter.SM_CommonFlowerPlanter"));
    UStaticMesh* CommonBucket = ResolveResidentStaticMesh(
        TEXT("/Game/Production/World/Common/SM_CommonBucket.SM_CommonBucket"));
    UStaticMesh* CommonStorageChest = ResolveResidentStaticMesh(
        TEXT("/Game/Production/World/Common/SM_CommonStorageChest.SM_CommonStorageChest"));
    UStaticMesh* CommonSackBale = ResolveResidentStaticMesh(
        TEXT("/Game/Production/World/Common/SM_CommonSackBale.SM_CommonSackBale"));
    UStaticMesh* CommonWheelbarrow = ResolveResidentStaticMesh(
        TEXT("/Game/Production/World/Common/SM_CommonWheelbarrow.SM_CommonWheelbarrow"));

    int32 ClusterCount = 0;
    int32 InstanceCount = 0;
    auto SpawnDetailCluster = [this, &ClusterCount, &InstanceCount](
        UStaticMesh* Mesh,
        const TCHAR* Tag,
        int32 StartCull,
        int32 EndCull,
        const TArray<FTransform>& Placements)
    {
        if (!Mesh || Placements.Num() == 0)
        {
            return;
        }

        AWorldDetailCluster* Cluster = GetWorld()->SpawnActor<AWorldDetailCluster>();
        if (!Cluster)
        {
            return;
        }

        Cluster->Tags.AddUnique(TEXT("RuntimePrototypeGenerated"));
        Cluster->Tags.AddUnique(TEXT("P1C01BagEndHeroDetail"));
        Cluster->Tags.AddUnique(FName(Tag));
        Cluster->Configure(Mesh, false, StartCull, EndCull);
        for (const FTransform& Transform : Placements)
        {
            Cluster->AddDetailInstance(
                Transform.GetLocation(),
                Transform.Rotator(),
                Transform.GetScale3D());
        }

        ++ClusterCount;
        InstanceCount += Cluster->GetDetailCount();
    };

    TArray<FTransform> ApproachStones;
    ApproachStones.Reserve(14);
    for (int32 Index = 0; Index < 14; ++Index)
    {
        const float Alpha = static_cast<float>(Index) / 13.0f;
        const FVector Location = FMath::Lerp(
            FVector(-1710.0f, -355.0f, 5.0f),
            FVector(-2180.0f, -500.0f, 5.0f),
            Alpha);
        const float Side = (Index % 2 == 0) ? -22.0f : 22.0f;
        ApproachStones.Emplace(
            FRotator(0.0f, -15.0f + static_cast<float>((Index * 17) % 31), 0.0f),
            Location + FVector(0.0f, Side, 0.0f),
            FVector(0.48f + 0.03f * static_cast<float>(Index % 3)));
    }
    SpawnDetailCluster(ProductionPathStoneMesh, TEXT("P1C01BagEndApproachStones"), 700, 3600, ApproachStones);

    TArray<FTransform> GardenPlanters;
    GardenPlanters.Reserve(12);
    const FVector PlanterOffsets[] = {
        FVector(-20,-245,0), FVector(45,-250,0), FVector(115,-238,0),
        FVector(190,-222,0), FVector(-5,245,0), FVector(65,250,0),
        FVector(140,238,0), FVector(215,218,0), FVector(300,-205,0),
        FVector(345,-160,0), FVector(305,205,0), FVector(350,155,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(PlanterOffsets); ++Index)
    {
        GardenPlanters.Emplace(
            FRotator(0.0f, static_cast<float>((Index * 29) % 50) - 25.0f, 0.0f),
            BagEnd + PlanterOffsets[Index],
            FVector(0.52f + 0.03f * static_cast<float>(Index % 3)));
    }
    SpawnDetailCluster(CommonFlowerPlanter, TEXT("P1C01BagEndGardenPlanters"), 600, 3000, GardenPlanters);

    TArray<FTransform> WoodPiles;
    WoodPiles.Reserve(8);
    const FVector WoodOffsets[] = {
        FVector(-90,-300,0), FVector(5,-315,0), FVector(105,-302,0), FVector(205,-292,0),
        FVector(-70,300,0), FVector(30,315,0), FVector(135,302,0), FVector(238,286,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(WoodOffsets); ++Index)
    {
        WoodPiles.Emplace(
            FRotator(0.0f, static_cast<float>((Index * 37) % 35) - 17.0f, 0.0f),
            BagEnd + WoodOffsets[Index],
            FVector(0.54f + 0.04f * static_cast<float>(Index % 2)));
    }
    SpawnDetailCluster(ProductionCommonWoodPileMesh, TEXT("P1C01BagEndWoodPiles"), 900, 4200, WoodPiles);

    int32 StaticPropCount = 0;
    auto SpawnHeroProp = [this, &StaticPropCount](
        UStaticMesh* Mesh, const FVector& Location, const FVector& Scale, const FRotator& Rotation)
    {
        AStaticMeshActor* Actor = SpawnShape(Mesh, Location, Scale, FLinearColor::White, Rotation, false);
        if (Actor)
        {
            Actor->Tags.AddUnique(TEXT("P1C01BagEndHeroDetail"));
            ++StaticPropCount;
        }
        return Actor;
    };

    SpawnHeroProp(CommonWheelbarrow, BagEnd + FVector(355,-255,0), FVector(0.62f), FRotator(0,72,0));
    SpawnHeroProp(CommonBucket, BagEnd + FVector(295,-105,0), FVector(0.60f), FRotator(0,-8,0));
    SpawnHeroProp(CommonStorageChest, BagEnd + FVector(125,255,0), FVector(0.62f), FRotator(0,12,0));
    SpawnHeroProp(CommonSackBale, BagEnd + FVector(210,275,0), FVector(0.58f), FRotator(0,-16,0));
    SpawnHeroProp(ProductionBarrelMesh, BagEnd + FVector(305,265,0), FVector(0.58f), FRotator(0,9,0));
    SpawnHeroProp(ProductionCrateMesh, BagEnd + FVector(365,230,0), FVector(0.56f), FRotator(0,-11,0));
    SpawnHeroProp(ProductionLanternMesh, BagEnd + FVector(220,-170,18), FVector(0.56f), FRotator::ZeroRotator);
    SpawnHeroProp(ProductionFlowerBoxMesh, BagEnd + FVector(-25,185,0), FVector(0.62f), FRotator(0,-5,0));

    auto SpawnVariantProp = [this, &BagEnd](
        TArray<AStaticMeshActor*>& Target,
        UStaticMesh* Mesh,
        const FVector& Offset,
        const FVector& Scale,
        const FRotator& Rotation,
        const TCHAR* StateTag)
    {
        AStaticMeshActor* Actor = SpawnShape(Mesh, BagEnd + Offset, Scale, FLinearColor::White, Rotation, false);
        if (!Actor)
        {
            return;
        }

        Actor->Tags.AddUnique(TEXT("P1C01BagEndStateVariant"));
        Actor->Tags.AddUnique(FName(StateTag));
        Actor->SetActorHiddenInGame(true);
        Actor->SetActorEnableCollision(false);
        Target.Add(Actor);
    };

    SpawnVariantProp(BagEndBirthdayVariantActors, ProductionPicnicTableMesh, FVector(520,180,0), FVector(0.58f), FRotator(0,-8,0), TEXT("P1C01BagEndBirthdayState"));
    SpawnVariantProp(BagEndBirthdayVariantActors, ProductionPicnicTableMesh, FVector(555,-155,0), FVector(0.56f), FRotator(0,10,0), TEXT("P1C01BagEndBirthdayState"));
    SpawnVariantProp(BagEndBirthdayVariantActors, ProductionLanternMesh, FVector(455,245,12), FVector(0.58f), FRotator::ZeroRotator, TEXT("P1C01BagEndBirthdayState"));
    SpawnVariantProp(BagEndBirthdayVariantActors, ProductionLanternMesh, FVector(475,-245,12), FVector(0.58f), FRotator::ZeroRotator, TEXT("P1C01BagEndBirthdayState"));
    SpawnVariantProp(BagEndBirthdayVariantActors, ProductionMarketStallMesh, FVector(650,20,0), FVector(0.50f), FRotator(0,90,0), TEXT("P1C01BagEndBirthdayState"));

    SpawnVariantProp(BagEndDepartureVariantActors, CommonStorageChest, FVector(430,205,0), FVector(0.64f), FRotator(0,-7,0), TEXT("P1C01BagEndDepartureState"));
    SpawnVariantProp(BagEndDepartureVariantActors, CommonSackBale, FVector(500,230,0), FVector(0.62f), FRotator(0,12,0), TEXT("P1C01BagEndDepartureState"));
    SpawnVariantProp(BagEndDepartureVariantActors, ProductionCrateMesh, FVector(455,-210,0), FVector(0.62f), FRotator(0,-10,0), TEXT("P1C01BagEndDepartureState"));
    SpawnVariantProp(BagEndDepartureVariantActors, ProductionLoadedCartMesh, FVector(625,-70,0), FVector(0.54f), FRotator(0,82,0), TEXT("P1C01BagEndDepartureState"));
    SpawnVariantProp(BagEndDepartureVariantActors, CommonBucket, FVector(380,-170,0), FVector(0.60f), FRotator::ZeroRotator, TEXT("P1C01BagEndDepartureState"));

    UE_LOG(
        LogTemp,
        Display,
        TEXT("BAG_END_HERO_PASS clusters=%d instances=%d staticProps=%d birthdayProps=%d departureProps=%d populationTarget=18 collision=none tick=none interior=content-pending"),
        ClusterCount,
        InstanceCount,
        StaticPropCount,
        BagEndBirthdayVariantActors.Num(),
        BagEndDepartureVariantActors.Num());
}


void AShirePrototypeWorldBuilder::SpawnWorldDensityDetailPass()
{
    if (!GetWorld())
    {
        return;
    }

    struct FDetailPlacement
    {
        FVector Location;
        FRotator Rotation;
        FVector Scale;
    };

    int32 ClusterCount = 0;
    int32 InstanceCount = 0;

    auto SpawnDetailCluster = [this, &ClusterCount, &InstanceCount](
        UStaticMesh* Mesh,
        int32 StartCullDistance,
        int32 EndCullDistance,
        const FDetailPlacement* Placements,
        int32 PlacementCount)
    {
        if (!Mesh || !Placements || PlacementCount <= 0)
        {
            return;
        }

        FActorSpawnParameters Params;
        Params.Owner = this;
        Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

        AWorldDetailCluster* Cluster = GetWorld()->SpawnActor<AWorldDetailCluster>(
            FVector::ZeroVector, FRotator::ZeroRotator, Params);
        if (!Cluster)
        {
            return;
        }

        Cluster->Tags.AddUnique(TEXT("RuntimePrototypeGenerated"));
        Cluster->Tags.AddUnique(TEXT("P1C01WorldDensityDetail"));
        Cluster->Configure(Mesh, false, StartCullDistance, EndCullDistance);

        for (int32 Index = 0; Index < PlacementCount; ++Index)
        {
            const FDetailPlacement& P = Placements[Index];
            Cluster->AddDetailInstance(P.Location, P.Rotation, P.Scale);
        }

        ++ClusterCount;
        InstanceCount += Cluster->GetDetailCount();
    };

    // Domestic/farm work history. Visual-only HISM instances: no collision, no Tick,
    // and no population ownership.
    const FDetailPlacement WoodPiles[] = {
        { FVector(-2050,-1020,0), FRotator(0,18,0), FVector(0.72f) },
        { FVector(-1520,-1060,0), FRotator(0,-12,0), FVector(0.66f) },
        { FVector(-860,-920,0), FRotator(0,24,0), FVector(0.70f) },
        { FVector(520,760,0), FRotator(0,-20,0), FVector(0.62f) },
        { FVector(1120,980,0), FRotator(0,14,0), FVector(0.68f) },
        { FVector(6040,-1660,0), FRotator(0,8,0), FVector(0.76f) },
        { FVector(6480,-1220,0), FRotator(0,-22,0), FVector(0.72f) },
        { FVector(7240,-1080,0), FRotator(0,31,0), FVector(0.74f) },
        { FVector(8360,-720,0), FRotator(0,-16,0), FVector(0.70f) },
        { FVector(9020,-1280,0), FRotator(0,27,0), FVector(0.78f) }
    };
    SpawnDetailCluster(
        ProductionCommonWoodPileMesh, 1200, 6500,
        WoodPiles, UE_ARRAY_COUNT(WoodPiles));

    // Ferns thicken hedge/wood edges without adding actors per plant.
    const FDetailPlacement Ferns[] = {
        { FVector(-2380,-1120,0), FRotator(0,5,0), FVector(0.58f) },
        { FVector(-1900,-1280,0), FRotator(0,42,0), FVector(0.64f) },
        { FVector(-1280,-1180,0), FRotator(0,81,0), FVector(0.56f) },
        { FVector(-620,-1120,0), FRotator(0,123,0), FVector(0.62f) },
        { FVector(480,980,0), FRotator(0,167,0), FVector(0.54f) },
        { FVector(1180,1040,0), FRotator(0,208,0), FVector(0.60f) },
        { FVector(11650,-980,0), FRotator(0,12,0), FVector(0.68f) },
        { FVector(12150,1120,0), FRotator(0,47,0), FVector(0.61f) },
        { FVector(12700,-1100,0), FRotator(0,83,0), FVector(0.66f) },
        { FVector(13250,1250,0), FRotator(0,118,0), FVector(0.59f) },
        { FVector(13800,-1220,0), FRotator(0,154,0), FVector(0.70f) },
        { FVector(14350,1180,0), FRotator(0,191,0), FVector(0.62f) },
        { FVector(14900,-1150,0), FRotator(0,226,0), FVector(0.67f) },
        { FVector(15450,1260,0), FRotator(0,263,0), FVector(0.60f) },
        { FVector(16000,-1230,0), FRotator(0,298,0), FVector(0.69f) },
        { FVector(16550,1130,0), FRotator(0,333,0), FVector(0.63f) },
        { FVector(17100,-1100,0), FRotator(0,9,0), FVector(0.66f) },
        { FVector(17600,980,0), FRotator(0,44,0), FVector(0.58f) },
        { FVector(18400,-1050,0), FRotator(0,79,0), FVector(0.64f) },
        { FVector(18850,920,0), FRotator(0,116,0), FVector(0.57f) },
        { FVector(19400,-980,0), FRotator(0,151,0), FVector(0.65f) },
        { FVector(19950,860,0), FRotator(0,187,0), FVector(0.59f) },
        { FVector(20600,-900,0), FRotator(0,223,0), FVector(0.62f) },
        { FVector(21200,780,0), FRotator(0,259,0), FVector(0.56f) }
    };
    SpawnDetailCluster(
        ProductionCommonFernClumpMesh, 900, 4800,
        Ferns, UE_ARRAY_COUNT(Ferns));

    // The Water/ferry corridor gets low-cost edge vegetation, kept off the authored
    // travel line so this pass cannot become a traversal collider.
    const FDetailPlacement Reeds[] = {
        { FVector(ShireLayout::FerryX-1800,-1760,0), FRotator(0,8,0), FVector(0.70f) },
        { FVector(ShireLayout::FerryX-1500,-1690,0), FRotator(0,37,0), FVector(0.66f) },
        { FVector(ShireLayout::FerryX-1200,-1810,0), FRotator(0,71,0), FVector(0.74f) },
        { FVector(ShireLayout::FerryX-900,-1720,0), FRotator(0,104,0), FVector(0.68f) },
        { FVector(ShireLayout::FerryX-600,-1780,0), FRotator(0,139,0), FVector(0.72f) },
        { FVector(ShireLayout::FerryX-300,-1700,0), FRotator(0,173,0), FVector(0.65f) },
        { FVector(ShireLayout::FerryX,-1800,0), FRotator(0,207,0), FVector(0.76f) },
        { FVector(ShireLayout::FerryX+300,-1710,0), FRotator(0,241,0), FVector(0.69f) },
        { FVector(ShireLayout::FerryX+600,-1760,0), FRotator(0,276,0), FVector(0.71f) },
        { FVector(ShireLayout::FerryX-1800,760,0), FRotator(0,19,0), FVector(0.68f) },
        { FVector(ShireLayout::FerryX-1500,700,0), FRotator(0,54,0), FVector(0.72f) },
        { FVector(ShireLayout::FerryX-1200,790,0), FRotator(0,88,0), FVector(0.65f) },
        { FVector(ShireLayout::FerryX-900,720,0), FRotator(0,122,0), FVector(0.74f) },
        { FVector(ShireLayout::FerryX-600,780,0), FRotator(0,157,0), FVector(0.67f) },
        { FVector(ShireLayout::FerryX-300,710,0), FRotator(0,191,0), FVector(0.70f) },
        { FVector(ShireLayout::FerryX,800,0), FRotator(0,225,0), FVector(0.73f) },
        { FVector(ShireLayout::FerryX+300,730,0), FRotator(0,260,0), FVector(0.66f) },
        { FVector(ShireLayout::FerryX+600,780,0), FRotator(0,294,0), FVector(0.71f) }
    };
    SpawnDetailCluster(
        ProductionCommonReedClusterMesh, 1200, 6000,
        Reeds, UE_ARRAY_COUNT(Reeds));

    // Sparse route-side markers improve travel rhythm/readability without replacing
    // canonical landmarks or quest coordinates.
    const FDetailPlacement PathMarkers[] = {
        { FVector(2650,1120,0), FRotator(0,12,0), FVector(0.68f) },
        { FVector(4300,-1180,0), FRotator(0,-18,0), FVector(0.72f) },
        { FVector(6100,1060,0), FRotator(0,24,0), FVector(0.70f) },
        { FVector(7900,-1160,0), FRotator(0,-12,0), FVector(0.74f) },
        { FVector(9800,1100,0), FRotator(0,18,0), FVector(0.69f) },
        { FVector(11600,-1040,0), FRotator(0,-20,0), FVector(0.71f) },
        { FVector(13600,1080,0), FRotator(0,16,0), FVector(0.70f) },
        { FVector(15600,-1060,0), FRotator(0,-14,0), FVector(0.73f) },
        { FVector(17800,1040,0), FRotator(0,20,0), FVector(0.68f) },
        { FVector(19800,-1020,0), FRotator(0,-17,0), FVector(0.72f) },
        { FVector(21800,980,0), FRotator(0,15,0), FVector(0.70f) },
        { FVector(ShireLayout::FerryX-850,-980,0), FRotator(0,-10,0), FVector(0.74f) }
    };
    SpawnDetailCluster(
        ProductionCommonPathMarkerMesh, 1600, 8000,
        PathMarkers, UE_ARRAY_COUNT(PathMarkers));

    const FDetailPlacement FallenLogs[] = {
        { FVector(12600,1380,0), FRotator(0,18,0), FVector(0.78f) },
        { FVector(13750,-1380,0), FRotator(0,-22,0), FVector(0.82f) },
        { FVector(14950,1420,0), FRotator(0,31,0), FVector(0.76f) },
        { FVector(16150,-1360,0), FRotator(0,-16,0), FVector(0.80f) },
        { FVector(17350,1320,0), FRotator(0,27,0), FVector(0.74f) },
        { FVector(18800,-1280,0), FRotator(0,-19,0), FVector(0.79f) }
    };
    SpawnDetailCluster(
        ProductionCommonFallenLogMesh, 1800, 8500,
        FallenLogs, UE_ARRAY_COUNT(FallenLogs));

    UE_LOG(
        LogTemp,
        Display,
        TEXT("SHIRE_WORLD_DENSITY_DETAIL_PASS clusters=%d instances=%d populationTarget=18 collision=none tick=none"),
        ClusterCount,
        InstanceCount);
}



void AShirePrototypeWorldBuilder::SpawnScenicDetailPass()
{
    if (!DistantTreeTrunkInstances || !DistantTreeCanopyInstances || !RockInstances || !PathStoneInstances)
    {
        return;
    }

    auto SpawnProd = [this](UStaticMesh* Mesh, const FVector& Location, const FVector& Scale,
        const FRotator& Rotation = FRotator::ZeroRotator, bool bCollision = true)
    {
        if (Mesh)
        {
            SpawnShape(Mesh, Location, Scale, FLinearColor::White, Rotation, bCollision);
        }
    };

    DistantTreeTrunkInstances->ClearInstances();
    DistantTreeCanopyInstances->ClearInstances();
    RockInstances->ClearInstances();
    PathStoneInstances->ClearInstances();

    // Long tree lines close the horizon without hundreds of AStaticMeshActors.
    // The positions are deterministic so screenshots/perf comparisons remain repeatable.
    for (int32 Index = 0; Index < 52; ++Index)
    {
        const float X = -2600.0f + static_cast<float>(Index) * 560.0f;
        const float Wave = FMath::Sin(static_cast<float>(Index) * 0.73f) * 430.0f;
        for (int32 Side = -1; Side <= 1; Side += 2)
        {
            const float Y = static_cast<float>(Side) * (2450.0f + Wave * 0.35f);
            const float S = 0.65f + 0.09f * static_cast<float>((Index + (Side > 0 ? 1 : 0)) % 4);
            if (ProductionTreeTrunkMesh && ProductionTreeCanopyMesh)
            {
                DistantTreeTrunkInstances->AddInstance(FTransform(
                    FRotator(0.0f, static_cast<float>((Index * 29) % 360), 0.0f),
                    FVector(X, Y, 0.0f), FVector(S * 0.72f)));
                DistantTreeCanopyInstances->AddInstance(FTransform(
                    FRotator(0.0f, static_cast<float>((Index * 37) % 360), 0.0f),
                    FVector(X, Y, 150.0f * S), FVector(S * 0.72f)));
            }
            else
            {
                DistantTreeTrunkInstances->AddInstance(FTransform(
                    FRotator::ZeroRotator, FVector(X, Y, 78.0f * S),
                    FVector(0.12f, 0.12f, 0.78f) * S));
                DistantTreeCanopyInstances->AddInstance(FTransform(
                    FRotator(0.0f, static_cast<float>((Index * 37) % 360), 0.0f),
                    FVector(X + 18.0f, Y, 190.0f * S),
                    FVector(0.70f, 0.62f, 0.58f) * S));
                DistantTreeCanopyInstances->AddInstance(FTransform(
                    FRotator(0.0f, static_cast<float>((Index * 19 + 70) % 360), 0.0f),
                    FVector(X - 28.0f, Y + 22.0f, 212.0f * S),
                    FVector(0.52f, 0.48f, 0.45f) * S));
            }
        }
    }

    // Irregular stepping stones around Bag End, the Water and village paths.
    const FVector StoneCenters[] = {
        FVector(-2210,-400,8), FVector(-1950,-330,8), FVector(-1680,-210,8),
        FVector(-1400,-40,8), FVector(-1180,95,8), FVector(-900,150,8),
        FVector(-620,220,8), FVector(-350,310,8), FVector(-80,520,8),
        FVector(160,800,8), FVector(300,1080,8)
    };
    for (int32 Segment = 0; Segment < UE_ARRAY_COUNT(StoneCenters) - 1; ++Segment)
    {
        const FVector A = StoneCenters[Segment];
        const FVector B = StoneCenters[Segment + 1];
        for (int32 Step = 0; Step < 4; ++Step)
        {
            const float Alpha = static_cast<float>(Step) / 4.0f;
            FVector P = FMath::Lerp(A, B, Alpha);
            P.Y += FMath::Sin(static_cast<float>(Segment * 4 + Step) * 1.7f) * 22.0f;
            const float S = 0.20f + 0.035f * static_cast<float>((Segment + Step) % 3);
            PathStoneInstances->AddInstance(FTransform(
                FRotator(0.0f, static_cast<float>((Segment * 41 + Step * 17) % 360), 0.0f),
                P,
                FVector(S * 1.45f, S, 0.055f)));
        }
    }

    // River-bank and field rocks break the perfectly clean generated edges.
    for (int32 Index = 0; Index < 64; ++Index)
    {
        const bool bRiver = Index >= 34;
        const float X = bRiver
            ? ShireLayout::FerryX - 1100.0f + static_cast<float>((Index - 34) % 15) * 150.0f
            : 2500.0f + static_cast<float>(Index) * 265.0f;
        const float Y = bRiver
            ? ((Index % 2 == 0) ? -1760.0f : 720.0f) + FMath::Sin(Index * 0.9f) * 180.0f
            : ((Index % 2 == 0) ? -1550.0f : 1450.0f) + FMath::Sin(Index * 0.61f) * 160.0f;
        const float S = 0.12f + 0.04f * static_cast<float>(Index % 4);
        RockInstances->AddInstance(FTransform(
            FRotator(0.0f, static_cast<float>((Index * 53) % 360), 0.0f),
            FVector(X, Y, 14.0f),
            FVector(S * 1.5f, S, S * 0.7f)));
    }

    // Foreground composition around Hobbiton: gentle turf banks, carts/crates and signposts.
    const FVector Mounds[] = {
        FVector(-2450,900,-75), FVector(-2050,1500,-90), FVector(-1150,1650,-95),
        FVector(-250,1750,-90), FVector(900,1580,-85), FVector(1850,1250,-95),
        FVector(-2550,-1250,-80), FVector(-1500,-1500,-95), FVector(-350,-1450,-90),
        FVector(850,-1320,-90), FVector(2100,-1150,-85)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Mounds); ++Index)
    {
        const FVector MoundScale = ProductionTurfMoundMesh
            ? FVector(4.0f + 0.45f * (Index % 3), 3.6f + 0.35f * (Index % 2), 1.7f)
            : FVector(5.5f + (Index % 3), 3.0f + 0.5f * (Index % 2), 1.15f);
        SpawnShape(ProductionTurfMoundMesh ? ProductionTurfMoundMesh : SphereMesh, Mounds[Index],
            MoundScale,
            Index % 2 == 0 ? FLinearColor(0.14f,0.34f,0.075f) : FLinearColor(0.16f,0.37f,0.085f),
            FRotator::ZeroRotator, false);
    }

    const FVector Crates[] = {
        FVector(-1370,220,34), FVector(-1320,250,34), FVector(-760,250,28),
        FVector(-700,270,28), FVector(120,1180,28), FVector(205,1160,28)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Crates); ++Index)
    {
        SpawnShape(ProductionCrateMesh ? ProductionCrateMesh : CubeMesh, Crates[Index],
            ProductionCrateMesh ? FVector(0.58f) : FVector(0.28f,0.28f,0.28f),
            Index % 2 == 0 ? FLinearColor(0.34f,0.19f,0.075f) : FLinearColor(0.42f,0.27f,0.11f),
            FRotator(0.0f, static_cast<float>((Index * 23) % 45), 0.0f), false);
    }

    // Dense production hedgerows give Hobbiton and the wooded road the layered,
    // enclosed lane composition missing from the earlier open prototype.
    if (ProductionHedgeMesh)
    {
        struct FHedgePlacement
        {
            FVector Location;
            FVector Scale;
            float Yaw;
        };

        const FHedgePlacement Hedges[] = {
            { FVector(-2140,-900,35), FVector(1.9f,0.95f,1.15f), 8.0f },
            { FVector(-1650,-930,35), FVector(2.1f,0.95f,1.20f), -6.0f },
            { FVector(-1080,-900,35), FVector(2.0f,0.90f,1.10f), 5.0f },
            { FVector(-420,560,35), FVector(1.8f,0.90f,1.05f), 2.0f },
            { FVector(280,560,35), FVector(1.8f,0.90f,1.05f), -3.0f },
            { FVector(850,560,35), FVector(1.7f,0.90f,1.05f), 4.0f },

            { FVector(5850,-1910,35), FVector(2.3f,1.00f,1.20f), 0.0f },
            { FVector(6450,-1910,35), FVector(2.3f,1.00f,1.20f), 0.0f },
            { FVector(7050,-1910,35), FVector(2.3f,1.00f,1.20f), 0.0f },

            { FVector(12400,-520,42), FVector(2.5f,1.05f,1.35f), -7.0f },
            { FVector(13250,-630,42), FVector(2.5f,1.05f,1.35f), -7.0f },
            { FVector(14100,-745,42), FVector(2.5f,1.05f,1.35f), -7.0f },
            { FVector(14950,-860,42), FVector(2.5f,1.05f,1.35f), -7.0f },
            { FVector(15800,-975,42), FVector(2.5f,1.05f,1.35f), -7.0f },

            { FVector(12450,1420,42), FVector(2.5f,1.05f,1.35f), 7.0f },
            { FVector(13300,1315,42), FVector(2.5f,1.05f,1.35f), 7.0f },
            { FVector(14150,1210,42), FVector(2.5f,1.05f,1.35f), 7.0f },
            { FVector(15000,1105,42), FVector(2.5f,1.05f,1.35f), 7.0f },
            { FVector(15850,1000,42), FVector(2.5f,1.05f,1.35f), 7.0f }
        };

        for (const FHedgePlacement& Hedge : Hedges)
        {
            SpawnShape(
                ProductionHedgeMesh,
                Hedge.Location,
                Hedge.Scale,
                FLinearColor::White,
                FRotator(0.0f, Hedge.Yaw, 0.0f),
                false);
        }
    }

    // Production props create readable lived-in spaces instead of bare primitive staging.
    if (ProductionCartMesh)
    {
        SpawnShape(ProductionCartMesh, FVector(-760, 420, 0), FVector(0.82f),
            FLinearColor::White, FRotator(0, 24, 0), false);
        SpawnShape(ProductionCartMesh, FVector(5050, -1110, 0), FVector(0.78f),
            FLinearColor::White, FRotator(0, -18, 0), false);
    }
    if (ProductionBenchMesh)
    {
        SpawnShape(ProductionBenchMesh, FVector(-360, 1180, 0), FVector(0.86f),
            FLinearColor::White, FRotator(0, 12, 0), false);
        SpawnShape(ProductionBenchMesh, FVector(420, 1120, 0), FVector(0.86f),
            FLinearColor::White, FRotator(0, -8, 0), false);
    }
    if (ProductionMillWheelMesh)
    {
        SpawnShape(ProductionMillWheelMesh, FVector(-1135, 330, 92), FVector(0.95f),
            FLinearColor::White, FRotator(0, 0, 90), false);
    }
    if (ProductionLanternMesh)
    {
        const FVector Lanterns[] = {
            FVector(-520, 260, 0), FVector(-250, 1040, 0),
            FVector(260, 1080, 0), FVector(720, 980, 0)
        };
        for (int32 Index = 0; Index < UE_ARRAY_COUNT(Lanterns); ++Index)
        {
            SpawnShape(ProductionLanternMesh, Lanterns[Index], FVector(0.82f),
                FLinearColor::White, FRotator::ZeroRotator, false);
        }
    }

    // Road sign silhouettes help the player read the space without floating text labels.
    const FVector Signs[] = {
        FVector(1450,120,0), FVector(5850,-500,0), FVector(11200,770,0), FVector(21800,-760,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Signs); ++Index)
    {
        const FVector P = Signs[Index];
        if (ProductionSignpostMesh)
        {
            SpawnShape(ProductionSignpostMesh, P, FVector(1.0f), FLinearColor(0.34f,0.20f,0.075f),
                FRotator(0, Index % 2 == 0 ? 18.0f : -16.0f, 0), false);
        }
        else
        {
            SpawnShape(CylinderMesh, P + FVector(0,0,78), FVector(0.055f,0.055f,0.78f),
                FLinearColor(0.25f,0.13f,0.045f), FRotator::ZeroRotator, false);
            SpawnShape(CubeMesh, P + FVector(0,0,130), FVector(0.58f,0.08f,0.14f),
                FLinearColor(0.38f,0.22f,0.075f), FRotator(0, Index % 2 == 0 ? 18.0f : -16.0f, 0), false);
        }
    }

    // CP52: saturate the playable Shire with the reusable common kit. These are
    // deliberately non-blocking details around existing safe traversal corridors.
    const FVector SharedTrees[] = {
        FVector(-2380,1180,0), FVector(-1760,1480,0), FVector(-820,1520,0),
        FVector(1180,1380,0), FVector(5720,-1360,0), FVector(7350,-1180,0),
        FVector(12650,1120,0), FVector(15150,-1180,0), FVector(20600,1280,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(SharedTrees); ++Index)
    {
        SpawnProd(ProductionCommonBroadleafTreeMesh, SharedTrees[Index],
            FVector(0.72f + 0.05f * (Index % 3)),
            FRotator(0.0f, static_cast<float>((Index * 41) % 360), 0.0f), false);
    }

    const FVector FieldFences[] = {
        FVector(4300,-1250,0), FVector(4780,-1260,0), FVector(5260,-1270,0),
        FVector(9300,1180,0), FVector(9780,1190,0), FVector(10260,1200,0),
        FVector(17000,-1080,0), FVector(17480,-1090,0), FVector(17960,-1100,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(FieldFences); ++Index)
    {
        SpawnProd(ProductionCommonVillageFenceMesh, FieldFences[Index], FVector(0.78f),
            FRotator(0.0f, Index < 6 ? 0.0f : 3.0f, 0.0f), false);
    }

    const FVector RuralClutter[] = {
        FVector(-1460,570,0), FVector(-180,620,0), FVector(680,590,0),
        FVector(6250,-1410,0), FVector(8450,-970,0), FVector(13650,980,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(RuralClutter); ++Index)
    {
        SpawnProd(Index % 2 == 0 ? ProductionCommonWoodPileMesh : ProductionCommonFallenLogMesh,
            RuralClutter[Index], FVector(0.72f + 0.04f * (Index % 3)),
            FRotator(0.0f, static_cast<float>((Index * 53) % 360), 0.0f), false);
    }

    const FVector Ferns[] = {
        FVector(-2020,720,0), FVector(-1540,930,0), FVector(-980,980,0), FVector(-420,880,0),
        FVector(5050,-720,0), FVector(5580,-860,0), FVector(11200,960,0), FVector(11800,880,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Ferns); ++Index)
    {
        SpawnProd(ProductionCommonFernClumpMesh, Ferns[Index],
            FVector(0.62f + 0.05f * (Index % 3)),
            FRotator(0.0f, static_cast<float>((Index * 67) % 360), 0.0f), false);
    }

    const FVector Reeds[] = {
        FVector(21950,-1420,-5), FVector(22300,-1380,-5), FVector(22650,-1330,-5),
        FVector(23250,520,-5), FVector(23600,560,-5), FVector(23950,520,-5)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Reeds); ++Index)
    {
        SpawnProd(ProductionCommonReedClusterMesh, Reeds[Index], FVector(0.72f),
            FRotator(0.0f, static_cast<float>(Index * 31), 0.0f), false);
    }

    SpawnProd(ProductionCommonFootbridgeMesh, FVector(22680,-420,8), FVector(0.70f),
        FRotator(0.0f, 5.0f, 0.0f), true);
    SpawnProd(ProductionCommonPathMarkerMesh, FVector(10950,650,0), FVector(0.76f),
        FRotator(0.0f, -14.0f, 0.0f), false);
    SpawnProd(ProductionCommonDryStoneWallMesh, FVector(18400,980,0), FVector(0.86f),
        FRotator(0.0f, 5.0f, 0.0f), false);

    // CP53 resource flood: imported project-owned clutter makes every Shire zone read as worked,
    // travelled and inhabited without touching quest anchors.
    UStaticMesh* CommonBarrel = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonBarrel.SM_CommonBarrel"));
    UStaticMesh* CommonCargoCrate = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonCargoCrate.SM_CommonCargoCrate"));
    UStaticMesh* CommonSackBale = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonSackBale.SM_CommonSackBale"));
    UStaticMesh* CommonLongBench = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonLongBench.SM_CommonLongBench"));
    UStaticMesh* CommonHayBale = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonHayBale.SM_CommonHayBale"));
    UStaticMesh* CommonRopePost = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonRopePost.SM_CommonRopePost"));
    UStaticMesh* CommonMarketCanopy = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonMarketCanopy.SM_CommonMarketCanopy"));
    UStaticMesh* CommonRiverBoat = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonRiverBoat.SM_CommonRiverBoat"));
    UStaticMesh* CommonTreeStump = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonTreeStump.SM_CommonTreeStump"));
    UStaticMesh* CommonMushrooms = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonMushroomCluster.SM_CommonMushroomCluster"));

    const FVector FarmGoods[] = {
        FVector(3880,-1120,0), FVector(4200,-1060,0), FVector(4550,-1140,0),
        FVector(8200,1060,0), FVector(8600,1110,0), FVector(8950,1030,0),
        FVector(16600,-960,0), FVector(17000,-900,0), FVector(17400,-980,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(FarmGoods); ++Index)
    {
        SpawnProd(Index % 3 == 0 ? CommonHayBale : (Index % 3 == 1 ? CommonCargoCrate : CommonSackBale),
            FarmGoods[Index], FVector(0.68f + 0.04f * (Index % 2)),
            FRotator(0.0f, static_cast<float>((Index * 37) % 360), 0.0f), false);
    }

    const FVector SocialProps[] = {
        FVector(-720,410,0), FVector(-420,520,0), FVector(-120,430,0),
        FVector(220,520,0), FVector(540,430,0), FVector(860,500,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(SocialProps); ++Index)
    {
        SpawnProd(Index % 2 == 0 ? CommonLongBench : CommonBarrel,
            SocialProps[Index], FVector(0.68f),
            FRotator(0.0f, Index % 2 == 0 ? 8.0f : -12.0f, 0.0f), false);
    }

    SpawnProd(CommonMarketCanopy, FVector(-470,80,10), FVector(0.78f), FRotator(0.0f,-6.0f,0.0f), false);
    SpawnProd(CommonMarketCanopy, FVector(30,40,10), FVector(0.74f), FRotator(0.0f,5.0f,0.0f), false);

    const FVector RiverPosts[] = {
        FVector(22200,-760,0), FVector(22420,-740,0), FVector(23180,290,0), FVector(23400,310,0)
    };
    for (const FVector& P : RiverPosts)
    {
        SpawnProd(CommonRopePost, P, FVector(0.74f), FRotator::ZeroRotator, false);
    }
    SpawnProd(CommonRiverBoat, FVector(23080,-300,-10), FVector(0.62f), FRotator(0.0f,7.0f,0.0f), false);

    const FVector WoodlandFloor[] = {
        FVector(11850,-930,0), FVector(12400,-1020,0), FVector(12950,-880,0),
        FVector(14500,940,0), FVector(15100,1010,0), FVector(15700,920,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(WoodlandFloor); ++Index)
    {
        SpawnProd(Index % 2 == 0 ? CommonTreeStump : CommonMushrooms,
            WoodlandFloor[Index], FVector(0.72f + 0.05f * (Index % 3)),
            FRotator(0.0f, static_cast<float>(Index * 43), 0.0f), false);
    }
}

void AShirePrototypeWorldBuilder::BuildPrototypeWorld()
{
    if (bBuilt || !GetWorld())
    {
        return;
    }

    bBuilt = true;
    ConfigureMorningAtmosphere();
    ConfigureFoliageInstances();
    SpawnVillage();
    SpawnGeographyFoundationPass();
    SpawnHobbitonArchitecturePass();
    SpawnProductionVillageDetailLayer();
    SpawnFoliagePass();
    SpawnScenicDetailPass();
    SpawnWorldDensityDetailPass();
    SpawnBagEndHeroPass();
    SpawnPartySocialLoopPass();
    SpawnSideStories();
    SpawnStoryActors();
}