#include "BreePrototypeWorldBuilder.h"

#include "ShireAmbientNPC.h"
#include "ShireNPC.h"
#include "ShireQuestTrigger.h"
#include "ShireTraversalChallenge.h"

#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/TextRenderActor.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"
#include "UObject/SoftObjectPath.h"

namespace BreeVisual
{
    constexpr bool ShowPrototypeWorldLabels = false;
}

namespace
{
    UStaticMesh* ResolveResidentStaticMesh(const TCHAR* AssetPath)
    {
        return AssetPath
            ? Cast<UStaticMesh>(FSoftObjectPath(AssetPath).ResolveObject())
            : nullptr;
    }
}

ABreePrototypeWorldBuilder::ABreePrototypeWorldBuilder()
{
    PrimaryActorTick.bCanEverTick = false;

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
}

void ABreePrototypeWorldBuilder::BeginPlay()
{
    Super::BeginPlay();

    ProductionHouseMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Bree/SM_BreeHouse.SM_BreeHouse"));
    ProductionInnMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Bree/SM_BreeInn.SM_BreeInn"));
    ProductionGateMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Bree/SM_BreeGate.SM_BreeGate"));
    ProductionStallMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Bree/SM_BreeStall.SM_BreeStall"));
    ProductionLanternMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Bree/SM_BreeLantern.SM_BreeLantern"));
    ProductionHitchingPostMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Bree/SM_BreeHitchingPost.SM_BreeHitchingPost"));
    ProductionTableMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Bree/SM_BreeTable.SM_BreeTable"));
    ProductionCrateStackMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Bree/SM_BreeCrateStack.SM_BreeCrateStack"));
    CommonBroadleafTreeMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonBroadleafTree.SM_CommonBroadleafTree"));
    CommonFallenLogMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonFallenLog.SM_CommonFallenLog"));
    CommonDryStoneWallMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonDryStoneWall.SM_CommonDryStoneWall"));
    CommonPathMarkerMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonPathMarker.SM_CommonPathMarker"));
    CommonVillageFenceMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonVillageFence.SM_CommonVillageFence"));
    CommonWoodPileMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonWoodPile.SM_CommonWoodPile"));
    CommonFernClumpMesh = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonFernClump.SM_CommonFernClump"));

    BuildPrototypeWorld();
}

AStaticMeshActor* ABreePrototypeWorldBuilder::SpawnShape(
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

void ABreePrototypeWorldBuilder::SpawnLabel(const FString& Text, const FVector& Location, const FLinearColor& Color)
{
    if (!BreeVisual::ShowPrototypeWorldLabels)
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
    TextComponent->SetWorldSize(40.0f);
    TextComponent->SetTextRenderColor(Color.ToFColor(true));
}

void ABreePrototypeWorldBuilder::SpawnBreeTown()
{
    // Compact Chapter 2 greybox: rainy-night Bree is intentionally denser than the Shire.
    SpawnShape(CubeMesh, FVector(0.0f, 0.0f, -70.0f), FVector(34.0f, 24.0f, 0.7f),
        FLinearColor(0.10f, 0.12f, 0.09f), FRotator::ZeroRotator, true);

    // East Road leading into the western gate.
    const FVector RoadPoints[] = {
        FVector(-2450.0f, 0.0f, 12.0f), FVector(-2050.0f, 0.0f, 12.0f), FVector(-1650.0f, 0.0f, 12.0f),
        FVector(-1250.0f, 0.0f, 12.0f), FVector(-850.0f, 0.0f, 12.0f), FVector(-450.0f, 0.0f, 12.0f),
        FVector(0.0f, 0.0f, 12.0f), FVector(450.0f, 40.0f, 12.0f), FVector(900.0f, 90.0f, 12.0f)
    };
    for (const FVector& P : RoadPoints)
    {
        SpawnShape(CubeMesh, P, FVector(2.4f, 0.9f, 0.10f),
            FLinearColor(0.24f, 0.20f, 0.16f), FRotator::ZeroRotator, true);
    }

    // Western gate and hedge/dike silhouette. Production gate replaces the old blockout.
    if (!ProductionGateMesh)
    {
        SpawnShape(CubeMesh, FVector(-980.0f, -230.0f, 130.0f), FVector(0.35f, 0.35f, 1.3f),
            FLinearColor(0.20f, 0.12f, 0.07f), FRotator::ZeroRotator, true);
        SpawnShape(CubeMesh, FVector(-980.0f, 230.0f, 130.0f), FVector(0.35f, 0.35f, 1.3f),
            FLinearColor(0.20f, 0.12f, 0.07f), FRotator::ZeroRotator, true);
        SpawnShape(CubeMesh, FVector(-980.0f, 0.0f, 265.0f), FVector(0.35f, 2.65f, 0.25f),
            FLinearColor(0.18f, 0.10f, 0.06f), FRotator::ZeroRotator, true);
    }
    SpawnLabel(TEXT("West Gate of Bree"), FVector(-980.0f, 0.0f, 380.0f), FLinearColor(0.75f, 0.75f, 0.65f));

    // Dense, narrow street walls and simple roof masses.
    const FVector HouseCenters[] = {
        FVector(-520, -430, 110), FVector(-120, -500, 110), FVector(300, -470, 110), FVector(690, -400, 110),
        FVector(-520, 430, 110), FVector(-120, 510, 110), FVector(330, 470, 110), FVector(760, 420, 110)
    };
    if (!ProductionHouseMesh)
    {
        for (int32 Index = 0; Index < UE_ARRAY_COUNT(HouseCenters); ++Index)
        {
            const FVector P = HouseCenters[Index];
            SpawnShape(CubeMesh, P, FVector(1.45f, 1.15f, 1.10f),
                FLinearColor(0.30f, 0.24f, 0.19f), FRotator::ZeroRotator, true);
            SpawnShape(ConeMesh, P + FVector(0, 0, 165), FVector(1.7f, 1.4f, 0.65f),
                FLinearColor(0.16f, 0.10f, 0.08f), FRotator::ZeroRotator, false);
        }
    }

    // Prancing Pony production shell replaces the original cube/cone exterior.
    if (!ProductionInnMesh)
    {
        SpawnShape(CubeMesh, FVector(1120.0f, 130.0f, 150.0f), FVector(2.7f, 2.2f, 1.5f),
            FLinearColor(0.34f, 0.25f, 0.17f), FRotator::ZeroRotator, true);
        SpawnShape(ConeMesh, FVector(1120.0f, 130.0f, 345.0f), FVector(3.0f, 2.5f, 0.8f),
            FLinearColor(0.14f, 0.08f, 0.05f), FRotator::ZeroRotator, false);
    }
    SpawnLabel(TEXT("The Prancing Pony"), FVector(1120.0f, 130.0f, 470.0f), FLinearColor(0.92f, 0.75f, 0.35f));

    // Open common room proxy so Chapter 2 can be tested before an interior .umap exists.
    SpawnShape(CubeMesh, FVector(1450.0f, 780.0f, 10.0f), FVector(4.4f, 3.6f, 0.10f),
        FLinearColor(0.22f, 0.16f, 0.10f), FRotator::ZeroRotator, true);
    SpawnShape(CubeMesh, FVector(1450.0f, 1110.0f, 135.0f), FVector(4.4f, 0.15f, 1.35f),
        FLinearColor(0.26f, 0.20f, 0.15f), FRotator::ZeroRotator, true);
    SpawnShape(CubeMesh, FVector(1850.0f, 780.0f, 135.0f), FVector(0.15f, 3.6f, 1.35f),
        FLinearColor(0.26f, 0.20f, 0.15f), FRotator::ZeroRotator, true);
    SpawnLabel(TEXT("Common Room Prototype"), FVector(1450.0f, 780.0f, 300.0f), FLinearColor::White);

    // Tables remain as primitive fallbacks only when the production table is unavailable.
    if (!ProductionTableMesh)
    {
        for (int32 Row = 0; Row < 2; ++Row)
        {
            for (int32 Col = 0; Col < 3; ++Col)
            {
                SpawnShape(CubeMesh, FVector(1220.0f + Col * 180.0f, 650.0f + Row * 190.0f, 48.0f),
                    FVector(0.65f, 0.45f, 0.10f), FLinearColor(0.28f, 0.17f, 0.08f), FRotator::ZeroRotator, true);
            }
        }
    }
    SpawnShape(CubeMesh, FVector(1710.0f, 920.0f, 65.0f), FVector(1.35f, 0.35f, 0.65f),
        FLinearColor(0.30f, 0.18f, 0.09f), FRotator::ZeroRotator, true);

    // Street-life pass: stalls, rain puddles, lantern posts, crates and hitching details.
    if (!ProductionStallMesh)
    {
        const FVector StallCenters[] = {
            FVector(-260, 250, 55), FVector(140, -270, 55), FVector(520, 260, 55)
        };
        for (int32 Index = 0; Index < UE_ARRAY_COUNT(StallCenters); ++Index)
        {
            const FVector P = StallCenters[Index];
            SpawnShape(CubeMesh, P, FVector(0.95f, 0.55f, 0.55f),
                FLinearColor(0.31f, 0.20f, 0.10f), FRotator::ZeroRotator, true);
            SpawnShape(CubeMesh, P + FVector(0, 0, 85), FVector(1.10f, 0.70f, 0.05f),
                Index % 2 == 0 ? FLinearColor(0.34f, 0.14f, 0.10f) : FLinearColor(0.16f, 0.23f, 0.12f),
                FRotator(0, 0, Index % 2 == 0 ? 5.0f : -5.0f), false);
        }
    }

    for (int32 Index = 0; Index < 7; ++Index)
    {
        const float X = -720.0f + Index * 250.0f;
        const float Y = Index % 2 == 0 ? -140.0f : 155.0f;
        SpawnShape(CubeMesh, FVector(X, Y, 3.0f), FVector(0.55f, 0.26f, 0.015f),
            FLinearColor(0.055f, 0.11f, 0.13f), FRotator(0.0f, Index * 13.0f, 0.0f), false);
    }

    const FVector LanternPosts[] = {
        FVector(-760, -260, 80), FVector(-360, 270, 80), FVector(80, -260, 80),
        FVector(520, 280, 80), FVector(940, -180, 80), FVector(1280, 420, 80)
    };
    for (const FVector& P : LanternPosts)
    {
        SpawnShape(CylinderMesh, P, FVector(0.055f, 0.055f, 0.78f),
            FLinearColor(0.16f, 0.10f, 0.055f), FRotator::ZeroRotator, false);
        SpawnShape(SphereMesh, P + FVector(0, 0, 95), FVector(0.10f),
            FLinearColor(0.78f, 0.52f, 0.14f), FRotator::ZeroRotator, false);
    }

    for (int32 Index = 0; Index < 10; ++Index)
    {
        const FVector P(
            900.0f + (Index % 5) * 150.0f,
            480.0f + (Index / 5) * 250.0f,
            34.0f);
        SpawnShape(CubeMesh, P, FVector(0.25f + 0.05f * (Index % 2), 0.25f, 0.30f),
            FLinearColor(0.24f, 0.15f, 0.07f), FRotator(0.0f, Index * 17.0f, 0.0f), true);
    }

    // A few dark birds circle rooflines and the western gate; cheap motion helps rainy Bree feel occupied.
    const FVector BreeBirds[] = {
        FVector(-780, -340, 430), FVector(120, 520, 470), FVector(980, -420, 500)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(BreeBirds); ++Index)
    {
        AShireAmbientNPC* Bird = GetWorld()->SpawnActor<AShireAmbientNPC>(BreeBirds[Index], FRotator::ZeroRotator);
        if (!Bird) continue;
        Bird->RoutineRole = TEXT("Bird");
        Bird->RoutinePointA = BreeBirds[Index];
        Bird->RoutinePointB = BreeBirds[Index] + FVector(520.0f, Index % 2 == 0 ? 360.0f : -360.0f, 70.0f);
        Bird->WalkSpeed = 145.0f + 10.0f * Index;
        Bird->MinWait = 0.0f;
        Bird->MaxWait = 0.0f;
    }

    // Lightweight Bree crowd. Fewer agents than final art; enough for navigation and crowd-flow tests.
    const FVector BreeCrowd[] = {
        FVector(-420, 120, 20), FVector(-160, -120, 20), FVector(180, 160, 20), FVector(420, -80, 20),
        FVector(720, 150, 20), FVector(1120, 620, 20), FVector(1320, 760, 20), FVector(1580, 690, 20)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(BreeCrowd); ++Index)
    {
        AShireAmbientNPC* Townsperson = GetWorld()->SpawnActor<AShireAmbientNPC>(BreeCrowd[Index], FRotator::ZeroRotator);
        if (Townsperson)
        {
            Townsperson->RoutinePointA = BreeCrowd[Index];
            Townsperson->RoutinePointB = BreeCrowd[Index] + FVector(170.0f + 15.0f * (Index % 3), (Index % 2 ? 95.0f : -95.0f), 0.0f);
            Townsperson->RoutineRole = TEXT("BreeTownsperson");
            Townsperson->ActivityPropType =
                Index % 3 == 0 ? TEXT("Basket") :
                (Index % 3 == 1 ? TEXT("Crate") : TEXT("Mug"));
            Townsperson->WalkSpeed = 42.0f + 4.0f * (Index % 3);
        }
    }

    // CP56: denser inn/street social life around the Prancing Pony. This reuses
    // existing bounded BreeTownsperson logic rather than introducing a new crowd system.
    const FVector InnCrowd[] = {
        FVector(980, 720, 20), FVector(1120, 850, 20), FVector(1260, 680, 20),
        FVector(1420, 820, 20), FVector(1540, 610, 20), FVector(1660, 760, 20)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(InnCrowd); ++Index)
    {
        AShireAmbientNPC* Guest = GetWorld()->SpawnActor<AShireAmbientNPC>(InnCrowd[Index], FRotator::ZeroRotator);
        if (!Guest) continue;
        Guest->RoutineRole = TEXT("BreeTownsperson");
        Guest->ActivityPropType = Index % 2 == 0 ? FName(TEXT("Mug")) : NAME_None;
        Guest->RoutinePointA = InnCrowd[Index];
        Guest->RoutinePointB = InnCrowd[Index] + FVector(
            90.0f + 20.0f * (Index % 3), Index % 2 == 0 ? 80.0f : -80.0f, 0.0f);
        Guest->WalkSpeed = 30.0f + 3.0f * (Index % 3);
        Guest->MinWait = 2.0f;
        Guest->MaxWait = 5.5f;
        Guest->PlayerNoticeRadius = 420.0f;
    }
}


void ABreePrototypeWorldBuilder::SpawnProductionBreeDetailLayer()
{
    auto SpawnProd = [this](UStaticMesh* Mesh, const FVector& Location, const FVector& Scale,
        const FRotator& Rotation = FRotator::ZeroRotator, bool bCollision = true)
    {
        if (Mesh)
        {
            SpawnShape(Mesh, Location, Scale, FLinearColor::White, Rotation, bCollision);
        }
    };

    // Replace the dominant street silhouette with production architecture while keeping
    // all quest trigger positions and traversal coordinates untouched.
    SpawnProd(ProductionGateMesh, FVector(-980.0f, 0.0f, 0.0f), FVector(0.92f), FRotator::ZeroRotator, true);

    const struct FHousePlacement
    {
        FVector Location;
        float Scale;
        float Yaw;
    } Houses[] = {
        { FVector(-560,-450,0), 0.72f, 5.0f },
        { FVector(-150,-510,0), 0.76f, -4.0f },
        { FVector(290,-475,0), 0.74f, 4.0f },
        { FVector(700,-405,0), 0.80f, -7.0f },
        { FVector(-555,445,0), 0.70f, -6.0f },
        { FVector(-130,520,0), 0.78f, 5.0f },
        { FVector(335,480,0), 0.74f, -5.0f },
        { FVector(770,430,0), 0.82f, 8.0f }
    };
    for (const FHousePlacement& P : Houses)
    {
        SpawnProd(ProductionHouseMesh, P.Location, FVector(P.Scale), FRotator(0.0f, P.Yaw, 0.0f), true);
    }

    SpawnProd(ProductionInnMesh, FVector(1120.0f,130.0f,0.0f), FVector(0.94f),
        FRotator(0.0f,-4.0f,0.0f), true);

    const FVector Stalls[] = {
        FVector(-260,250,0), FVector(140,-270,0), FVector(520,260,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Stalls); ++Index)
    {
        SpawnProd(ProductionStallMesh, Stalls[Index], FVector(0.72f),
            FRotator(0.0f, Index == 1 ? 180.0f : 0.0f, 0.0f), true);
    }

    const FVector Lamps[] = {
        FVector(-760,-260,0), FVector(-360,270,0), FVector(80,-260,0),
        FVector(520,280,0), FVector(940,-180,0), FVector(1280,420,0)
    };
    for (const FVector& P : Lamps)
    {
        SpawnProd(ProductionLanternMesh, P, FVector(0.72f), FRotator::ZeroRotator, false);
    }

    const FVector Hitching[] = {
        FVector(-820,340,0), FVector(900,-330,0), FVector(1320,430,0)
    };
    for (const FVector& P : Hitching)
    {
        SpawnProd(ProductionHitchingPostMesh, P, FVector(0.78f), FRotator::ZeroRotator, true);
    }

    const FVector CommonTables[] = {
        FVector(1220,650,0), FVector(1400,650,0), FVector(1580,650,0),
        FVector(1220,840,0), FVector(1400,840,0), FVector(1580,840,0)
    };
    for (const FVector& P : CommonTables)
    {
        SpawnProd(ProductionTableMesh, P, FVector(0.72f), FRotator::ZeroRotator, true);
    }

    const FVector Goods[] = {
        FVector(930,490,0), FVector(1080,500,0), FVector(1240,500,0),
        FVector(1460,560,0), FVector(1600,590,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Goods); ++Index)
    {
        SpawnProd(ProductionCrateStackMesh, Goods[Index], FVector(0.58f + 0.05f * (Index % 2)),
            FRotator(0.0f, 17.0f * Index, 0.0f), true);
    }

    // CP52: pull the shared production kit into Bree so the town reads as a complete
    // region rather than a single architecture set. Keep this dressing non-blocking.
    const FVector BoundaryWalls[] = {
        FVector(-920,-620,0), FVector(-420,-650,0), FVector(120,-650,0), FVector(650,-610,0),
        FVector(-900,640,0), FVector(-370,660,0), FVector(180,650,0), FVector(720,610,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(BoundaryWalls); ++Index)
    {
        SpawnProd(CommonDryStoneWallMesh, BoundaryWalls[Index], FVector(0.82f),
            FRotator(0.0f, Index < 4 ? 0.0f : 180.0f, 0.0f), false);
    }

    const FVector FenceRuns[] = {
        FVector(-720,-760,0), FVector(-240,-780,0), FVector(260,-770,0),
        FVector(760,-710,0), FVector(-720,760,0), FVector(-200,790,0),
        FVector(320,770,0), FVector(820,720,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(FenceRuns); ++Index)
    {
        SpawnProd(CommonVillageFenceMesh, FenceRuns[Index], FVector(0.78f),
            FRotator(0.0f, Index < 4 ? 0.0f : 180.0f, 0.0f), false);
    }

    const FVector Trees[] = {
        FVector(-1180,-720,0), FVector(-1040,760,0), FVector(-450,-940,0),
        FVector(360,-920,0), FVector(920,-720,0), FVector(980,760,0),
        FVector(1540,-520,0), FVector(1650,650,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Trees); ++Index)
    {
        SpawnProd(CommonBroadleafTreeMesh, Trees[Index], FVector(0.72f + 0.05f * (Index % 3)),
            FRotator(0.0f, static_cast<float>((Index * 47) % 360), 0.0f), false);
    }

    const FVector WorkClutter[] = {
        FVector(-640,310,0), FVector(-120,-310,0), FVector(430,300,0),
        FVector(900,-300,0), FVector(1200,520,0), FVector(1520,500,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(WorkClutter); ++Index)
    {
        SpawnProd(Index % 2 == 0 ? CommonWoodPileMesh : CommonFallenLogMesh,
            WorkClutter[Index], FVector(0.68f + 0.04f * (Index % 3)),
            FRotator(0.0f, static_cast<float>((Index * 59) % 360), 0.0f), false);
    }

    const FVector Ferns[] = {
        FVector(-980,-510,0), FVector(-820,520,0), FVector(-360,-560,0),
        FVector(260,560,0), FVector(790,-510,0), FVector(1080,500,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Ferns); ++Index)
    {
        SpawnProd(CommonFernClumpMesh, Ferns[Index], FVector(0.58f + 0.04f * (Index % 2)),
            FRotator(0.0f, static_cast<float>(Index * 61), 0.0f), false);
    }

    SpawnProd(CommonPathMarkerMesh, FVector(-1200,80,0), FVector(0.78f),
        FRotator(0.0f, 12.0f, 0.0f), false);

    // CP53 dense town-life dressing: more imported clutter, seating and trade goods
    // around streets and the inn, with collision disabled on decorative pieces.
    UStaticMesh* CommonBarrel = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonBarrel.SM_CommonBarrel"));
    UStaticMesh* CommonCargoCrate = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonCargoCrate.SM_CommonCargoCrate"));
    UStaticMesh* CommonSackBale = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonSackBale.SM_CommonSackBale"));
    UStaticMesh* CommonLongBench = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonLongBench.SM_CommonLongBench"));
    UStaticMesh* CommonRopePost = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonRopePost.SM_CommonRopePost"));
    UStaticMesh* CommonMarketCanopy = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Common/SM_CommonMarketCanopy.SM_CommonMarketCanopy"));

    const FVector StreetGoods[] = {
        FVector(-700,-250,0), FVector(-510,280,0), FVector(-240,-310,0), FVector(-40,300,0),
        FVector(220,-300,0), FVector(430,300,0), FVector(700,-250,0), FVector(920,280,0),
        FVector(1120,500,0), FVector(1330,520,0), FVector(1530,500,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(StreetGoods); ++Index)
    {
        UStaticMesh* Chosen = Index % 3 == 0 ? CommonBarrel :
            (Index % 3 == 1 ? CommonCargoCrate : CommonSackBale);
        SpawnProd(Chosen, StreetGoods[Index], FVector(0.62f + 0.04f * (Index % 2)),
            FRotator(0.0f, static_cast<float>((Index * 33) % 360), 0.0f), false);
    }

    const FVector Benches[] = {
        FVector(-620,120,0), FVector(-120,-140,0), FVector(420,120,0),
        FVector(980,40,0), FVector(1240,720,0), FVector(1540,760,0)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Benches); ++Index)
    {
        SpawnProd(CommonLongBench, Benches[Index], FVector(0.66f),
            FRotator(0.0f, Index < 4 ? 0.0f : 90.0f, 0.0f), false);
    }

    SpawnProd(CommonMarketCanopy, FVector(-240,220,22), FVector(0.72f), FRotator(0.0f,4.0f,0.0f), false);
    SpawnProd(CommonMarketCanopy, FVector(330,-230,22), FVector(0.70f), FRotator(0.0f,-5.0f,0.0f), false);

    const FVector StablePosts[] = {
        FVector(1020,-430,0), FVector(1130,-430,0), FVector(1240,-430,0), FVector(1350,-430,0)
    };
    for (const FVector& P : StablePosts)
    {
        SpawnProd(CommonRopePost, P, FVector(0.72f), FRotator::ZeroRotator, false);
    }
    // CP54 mega inventory pass: tavern, stable, market and alley clutter.
    auto LoadCP54 = [](const TCHAR* Path) -> UStaticMesh* { return ResolveResidentStaticMesh(Path); };
    UStaticMesh* CP54Table = LoadCP54(TEXT("/Game/Production/World/Common/SM_CommonMarketTable.SM_CommonMarketTable"));
    UStaticMesh* CP54Stool = LoadCP54(TEXT("/Game/Production/World/Common/SM_CommonStool.SM_CommonStool"));
    UStaticMesh* CP54Rack = LoadCP54(TEXT("/Game/Production/World/Common/SM_CommonToolRack.SM_CommonToolRack"));
    UStaticMesh* CP54Lamp = LoadCP54(TEXT("/Game/Production/World/Common/SM_CommonLanternPost.SM_CommonLanternPost"));
    UStaticMesh* CP54Wagon = LoadCP54(TEXT("/Game/Production/World/Common/SM_CommonWagon.SM_CommonWagon"));
    UStaticMesh* CP54Awning = LoadCP54(TEXT("/Game/Production/World/Bree/SM_BreeStreetAwning.SM_BreeStreetAwning"));
    UStaticMesh* CP54Bench = LoadCP54(TEXT("/Game/Production/World/Bree/SM_BreeTavernBench.SM_BreeTavernBench"));
    UStaticMesh* CP54Casks = LoadCP54(TEXT("/Game/Production/World/Bree/SM_BreeAleCaskRack.SM_BreeAleCaskRack"));
    UStaticMesh* CP54Stable = LoadCP54(TEXT("/Game/Production/World/Bree/SM_BreeStableRail.SM_BreeStableRail"));
    UStaticMesh* CP54Board = LoadCP54(TEXT("/Game/Production/World/Bree/SM_BreeMarketBoard.SM_BreeMarketBoard"));
    UStaticMesh* CP54Arch = LoadCP54(TEXT("/Game/Production/World/Bree/SM_BreeAlleyArch.SM_BreeAlleyArch"));
    UStaticMesh* CP54TradeWagon = LoadCP54(TEXT("/Game/Production/World/Bree/SM_BreeTradeWagon.SM_BreeTradeWagon"));
    UStaticMesh* CP54InnSign = LoadCP54(TEXT("/Game/Production/World/Bree/SM_BreeInnSign.SM_BreeInnSign"));
    const FVector CP54Market[] = { FVector(-560,180,0), FVector(-300,-210,0), FVector(-30,190,0), FVector(260,-180,0), FVector(540,200,0), FVector(800,-170,0) };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(CP54Market); ++Index)
        SpawnProd(Index % 2 == 0 ? CP54Table : CP54Awning, CP54Market[Index], FVector(0.66f), FRotator(0.0f, Index % 2 == 0 ? 4.0f : -5.0f, 0.0f), false);
    const FVector CP54InnYard[] = { FVector(1040,500,0), FVector(1200,520,0), FVector(1380,520,0), FVector(1060,700,0), FVector(1240,720,0), FVector(1430,710,0) };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(CP54InnYard); ++Index)
    {
        UStaticMesh* Choice = Index % 3 == 0 ? CP54Bench : (Index % 3 == 1 ? CP54Casks : CP54Stool);
        SpawnProd(Choice, CP54InnYard[Index], FVector(0.64f), FRotator(0.0f, static_cast<float>((Index * 47) % 180), 0.0f), false);
    }
    SpawnProd(CP54Stable, FVector(1180,-520,0), FVector(0.74f), FRotator(0,0,0), false);
    SpawnProd(CP54Stable, FVector(1400,-520,0), FVector(0.74f), FRotator(0,0,0), false);
    SpawnProd(CP54TradeWagon, FVector(1580,-360,0), FVector(0.66f), FRotator(0,-8,0), false);
    SpawnProd(CP54Wagon, FVector(-1180,420,0), FVector(0.62f), FRotator(0,8,0), false);
    SpawnProd(CP54Arch, FVector(-820,0,0), FVector(0.70f), FRotator(0,90,0), false);
    SpawnProd(CP54Arch, FVector(760,0,0), FVector(0.70f), FRotator(0,90,0), false);
    SpawnProd(CP54InnSign, FVector(1030,250,0), FVector(0.74f), FRotator(0,90,0), false);
    SpawnProd(CP54Board, FVector(-400,350,0), FVector(0.68f), FRotator(0,6,0), false);
    SpawnProd(CP54Rack, FVector(1510,480,0), FVector(0.62f), FRotator(0,-10,0), false);
    SpawnProd(CP54Lamp, FVector(-1050,-180,0), FVector(0.62f), FRotator::ZeroRotator, false);
    SpawnProd(CP54Lamp, FVector(1520,180,0), FVector(0.62f), FRotator::ZeroRotator, false);

}

void ABreePrototypeWorldBuilder::SpawnStoryFlow()
{
    if (!GetWorld())
    {
        return;
    }

    AShireQuestTrigger* EveningRoad = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(-2050.0f, 0.0f, 90.0f), FRotator::ZeroRotator);
    if (EveningRoad)
    {
        EveningRoad->QuestId = TEXT("RoadToBree");
        EveningRoad->RequiredStage = 0;
        EveningRoad->StageAfterTrigger = 1;
        EveningRoad->ObjectiveMessage = FText::FromString(TEXT("Evening closes in. Keep together and stay on the road."));
        EveningRoad->StoryBeatId = TEXT("BreeRoadNightfall");
    }

    AShireQuestTrigger* GateApproach = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(-1250.0f, 0.0f, 90.0f), FRotator::ZeroRotator);
    if (GateApproach)
    {
        GateApproach->QuestId = TEXT("RoadToBree");
        GateApproach->RequiredStage = 1;
        GateApproach->StageAfterTrigger = 2;
        GateApproach->ObjectiveMessage = FText::FromString(TEXT("The western gate of Bree rises ahead in the rain."));
    }

    auto SpawnHobbitCompanion = [this](const TCHAR* Name, const FVector& Location, const TCHAR* Line)
    {
        AShireNPC* Companion = GetWorld()->SpawnActor<AShireNPC>(Location, FRotator(0.0f, 0.0f, 0.0f));
        if (!Companion)
        {
            return;
        }

        Companion->DisplayName = FText::FromString(Name);
        Companion->DialogueLines = { FText::FromString(Line) };
        Companion->bFollowPlayerAfterInteraction = true;
    };

    SpawnHobbitCompanion(TEXT("Sam"), FVector(-1190.0f, -180.0f, 70.0f),
        TEXT("Bree is bigger than I expected. I am not letting you out of sight in here."));
    SpawnHobbitCompanion(TEXT("Merry"), FVector(-1280.0f, 240.0f, 70.0f),
        TEXT("We should find the inn, find Gandalf, and avoid attracting attention. In that order."));
    SpawnHobbitCompanion(TEXT("Pippin"), FVector(-1370.0f, -40.0f, 70.0f),
        TEXT("I can manage not attracting attention. Probably."));

    AShireNPC* GateKeeper = GetWorld()->SpawnActor<AShireNPC>(FVector(-1030.0f, 120.0f, 70.0f), FRotator(0.0f, 180.0f, 0.0f));
    if (GateKeeper)
    {
        GateKeeper->DisplayName = FText::FromString(TEXT("Gate Keeper"));
        GateKeeper->DialogueLines = {
            FText::FromString(TEXT("Late travelers from the west? Keep your business quiet and do not linger in the street."))
        };
        GateKeeper->QuestId = TEXT("RoadToBree");
        GateKeeper->RequiredQuestStage = 2;
        GateKeeper->QuestStageAfterInteraction = 2;
        GateKeeper->NextQuestId = TEXT("BreeArrival");
        GateKeeper->NextQuestStage = 0;
    }

    AShireQuestTrigger* InnApproach = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(850.0f, 90.0f, 90.0f), FRotator::ZeroRotator);
    if (InnApproach)
    {
        InnApproach->QuestId = TEXT("BreeArrival");
        InnApproach->RequiredStage = 0;
        InnApproach->StageAfterTrigger = 1;
        InnApproach->ObjectiveMessage = FText::FromString(TEXT("Warm light spills from the Prancing Pony."));
        InnApproach->StoryBeatId = TEXT("PrancingPonyExterior");
    }

    AShireNPC* Butterbur = GetWorld()->SpawnActor<AShireNPC>(FVector(1710.0f, 930.0f, 70.0f), FRotator(0.0f, 200.0f, 0.0f));
    if (Butterbur)
    {
        Butterbur->DisplayName = FText::FromString(TEXT("Barliman Butterbur"));
        Butterbur->DialogueLines = {
            FText::FromString(TEXT("You are welcome to a room, but I have not seen the grey wizard you describe in a long while.")),
            FText::FromString(TEXT("Keep your voices down. Folk notice strangers quickly in Bree."))
        };
        Butterbur->QuestId = TEXT("BreeArrival");
        Butterbur->RequiredQuestStage = 1;
        Butterbur->QuestStageAfterInteraction = 2;
    }

    AShireQuestTrigger* BreeCommonRoomLife = GetWorld()->SpawnActor<AShireQuestTrigger>(
        FVector(1180.0f, 720.0f, 90.0f), FRotator::ZeroRotator);
    if (BreeCommonRoomLife)
    {
        BreeCommonRoomLife->SideStoryBeatAfterTrigger = TEXT("Side_BreeCommonRoomLife");
        BreeCommonRoomLife->ObjectiveMessage = FText::FromString(
            TEXT("The common room is noisy with travelers, locals and too many curious glances. You can listen, mingle, or keep moving."));
    }

    auto SpawnBreeDiscovery = [this](
        const FVector& Location,
        FName DiscoveryId,
        const TCHAR* DisplayName,
        FName OpensAfter,
        FName ClosesBefore)
    {
        AShireQuestTrigger* Trigger =
            GetWorld()->SpawnActor<AShireQuestTrigger>(Location, FRotator::ZeroRotator);
        if (Trigger)
        {
            Trigger->DiscoveryId = DiscoveryId;
            Trigger->DiscoveryDisplayName = FText::FromString(DisplayName);
            Trigger->RequiredSideStoryBeat = OpensAfter;
            Trigger->BlockedAfterStoryBeat = ClosesBefore;
        }
    };

    AShireTraversalChallenge* WatchTheRoom = GetWorld()->SpawnActor<AShireTraversalChallenge>(
        FVector(1180.0f, 650.0f, 90.0f), FRotator::ZeroRotator);
    if (WatchTheRoom)
    {
        WatchTheRoom->ConfigureActivityChallenge(
            TEXT("BREE_GATE_GOSSIP"),
            FText::FromString(TEXT("Watch the Room")),
            TEXT("OBSERVATION_CHALLENGE"),
            FVector(0, 0, 0),
            FVector(220, 80, 0),
            FVector(420, -100, 0));
    }

    AShireTraversalChallenge* StableSigns = GetWorld()->SpawnActor<AShireTraversalChallenge>(
        FVector(520.0f, -520.0f, 90.0f), FRotator::ZeroRotator);
    if (StableSigns)
    {
        StableSigns->ConfigureActivityChallenge(
            TEXT("BREE_STABLE_YARD"),
            FText::FromString(TEXT("Stable Yard Signs")),
            TEXT("TRACKING_CHALLENGE"),
            FVector(0, 0, 0),
            FVector(240, 100, 0),
            FVector(470, -60, 0));
    }

    SpawnBreeDiscovery(
        FVector(1520.0f, 570.0f, 90.0f),
        TEXT("BREE_INN_KITCHEN_LIFE"), TEXT("Life Behind the Prancing Pony"),
        TEXT("PrancingPonyExterior"), TEXT("RingIncident"));

    AShireQuestTrigger* CommonRoomAttention = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(1390.0f, 760.0f, 90.0f), FRotator::ZeroRotator);
    if (CommonRoomAttention)
    {
        CommonRoomAttention->QuestId = TEXT("BreeArrival");
        CommonRoomAttention->RequiredStage = 2;
        CommonRoomAttention->StageAfterTrigger = 2;
        CommonRoomAttention->NextQuestId = TEXT("MeetStrider");
        CommonRoomAttention->NextQuestStage = 0;
        CommonRoomAttention->ObjectiveMessage = FText::FromString(TEXT("A Ranger in the shadows has been watching the table."));
        CommonRoomAttention->StoryBeatId = TEXT("RingIncident");
    }

    AShireNPC* Strider = GetWorld()->SpawnActor<AShireNPC>(FVector(1160.0f, 950.0f, 70.0f), FRotator(0.0f, 315.0f, 0.0f));
    if (Strider)
    {
        Strider->DisplayName = FText::FromString(TEXT("Strider"));
        Strider->DialogueLines = {
            FText::FromString(TEXT("You have drawn more attention than you realize. If you want to survive the night, come with me.")),
            FText::FromString(TEXT("There are riders hunting you. Waiting here for the wizard is no longer safe."))
        };
        Strider->QuestId = TEXT("MeetStrider");
        Strider->RequiredQuestStage = 0;
        Strider->QuestStageAfterInteraction = 1;
    }

    AShireQuestTrigger* PrivateRoom = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(1780.0f, 1080.0f, 90.0f), FRotator::ZeroRotator);
    if (PrivateRoom)
    {
        PrivateRoom->QuestId = TEXT("MeetStrider");
        PrivateRoom->RequiredStage = 1;
        PrivateRoom->StageAfterTrigger = 2;
        PrivateRoom->NextQuestId = TEXT("NightAttack");
        PrivateRoom->NextQuestStage = 0;
        PrivateRoom->ObjectiveMessage = FText::FromString(TEXT("Strider moves the hobbits away from the public room."));
        PrivateRoom->StoryBeatId = TEXT("StriderPrivateRoom");
    }

    AShireQuestTrigger* NazgulAttack = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(1640.0f, 1030.0f, 90.0f), FRotator::ZeroRotator);
    if (NazgulAttack)
    {
        NazgulAttack->QuestId = TEXT("NightAttack");
        NazgulAttack->RequiredStage = 0;
        NazgulAttack->StageAfterTrigger = 1;
        NazgulAttack->ObjectiveMessage = FText::FromString(TEXT("Steel strikes the decoy beds elsewhere in the inn. Stay hidden."));
        NazgulAttack->StoryBeatId = TEXT("NazgulAttackPrancingPony");
    }

    AShireQuestTrigger* DawnDeparture = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(650.0f, 40.0f, 90.0f), FRotator::ZeroRotator);
    if (DawnDeparture)
    {
        DawnDeparture->QuestId = TEXT("NightAttack");
        DawnDeparture->RequiredStage = 1;
        DawnDeparture->StageAfterTrigger = 2;
        DawnDeparture->NextChapterId = TEXT("P1C03");
        DawnDeparture->NextChapterQuestId = TEXT("RoadToWeathertop");
        DawnDeparture->NextChapterQuestStage = 0;
        DawnDeparture->ObjectiveMessage = FText::FromString(TEXT("Leave Bree with Strider before the town fully wakes."));
        DawnDeparture->StoryBeatId = TEXT("DepartBree");
    }
}

void ABreePrototypeWorldBuilder::BuildPrototypeWorld()
{
    if (bBuilt || !GetWorld())
    {
        return;
    }

    bBuilt = true;
    SpawnBreeTown();
    SpawnProductionBreeDetailLayer();
    SpawnStoryFlow();
}
