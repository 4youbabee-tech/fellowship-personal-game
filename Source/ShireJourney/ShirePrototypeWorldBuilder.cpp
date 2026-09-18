#include "ShirePrototypeWorldBuilder.h"

#include "BlackRiderPrototype.h"
#include "ShireAmbientNPC.h"
#include "ShireNPC.h"
#include "ShireQuestTrigger.h"

#include "Components/DirectionalLightComponent.h"
#include "Components/HierarchicalInstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Components/SkyLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/PostProcessVolume.h"
#include "Engine/SkyLight.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/TextRenderActor.h"
#include "EngineUtils.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

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
    }
}

void AShirePrototypeWorldBuilder::BeginPlay()
{
    Super::BeginPlay();
    BuildPrototypeWorld();
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
    MeshComponent->SetStaticMesh(Mesh);
    MeshComponent->SetMobility(EComponentMobility::Movable);
    MeshComponent->SetCollisionEnabled(bCollision ? ECollisionEnabled::QueryAndPhysics : ECollisionEnabled::NoCollision);
    Actor->SetActorScale3D(Scale);

    if (BasicMaterial)
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

void AShirePrototypeWorldBuilder::SpawnLabel(const FString& Text, const FVector& Location, const FLinearColor& Color)
{
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
    SpawnShape(CylinderMesh, Location + FVector(0.0f, 0.0f, 90.0f * Scale), FVector(0.14f, 0.14f, 0.9f) * Scale,
        FLinearColor(0.20f, 0.10f, 0.04f), FRotator::ZeroRotator, true);
    SpawnShape(SphereMesh, Location + FVector(0.0f, 0.0f, 210.0f * Scale), FVector(1.0f, 1.0f, 0.75f) * Scale,
        FLinearColor(0.12f, 0.38f, 0.10f), FRotator::ZeroRotator, false);
}

void AShirePrototypeWorldBuilder::SpawnHobbitHole(const FVector& Location, float Scale)
{
    SpawnShape(SphereMesh, Location + FVector(0.0f, 0.0f, 85.0f * Scale), FVector(1.55f, 1.0f, 0.72f) * Scale,
        FLinearColor(0.25f, 0.42f, 0.12f), FRotator::ZeroRotator, true);

    SpawnShape(CubeMesh, Location + FVector(-70.0f * Scale, 0.0f, 55.0f * Scale), FVector(0.10f, 0.72f, 0.55f) * Scale,
        FLinearColor(0.48f, 0.32f, 0.17f), FRotator::ZeroRotator, true);

    SpawnShape(CylinderMesh, Location + FVector(-82.0f * Scale, 0.0f, 55.0f * Scale), FVector(0.44f, 0.44f, 0.06f) * Scale,
        FLinearColor(0.14f, 0.48f, 0.20f), FRotator(0.0f, 90.0f, 0.0f), false);
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

    auto ApplyInstanceColor = [this](UHierarchicalInstancedStaticMeshComponent* Component, const FLinearColor& Color)
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

    ApplyInstanceColor(GrassInstances, FLinearColor(0.12f, 0.38f, 0.08f));
    ApplyInstanceColor(FlowerInstances, FLinearColor(0.90f, 0.70f, 0.28f));
    ApplyInstanceColor(ShrubInstances, FLinearColor(0.10f, 0.31f, 0.075f));
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

    const FVector GrassPatches[] = {
        FVector(-2320,-760,20), FVector(-2210,-690,20), FVector(-2110,-820,20), FVector(-2010,-720,20),
        FVector(-1910,-620,20), FVector(-1810,-850,20), FVector(-1710,-760,20), FVector(-1600,-600,20),
        FVector(-1510,520,20), FVector(-1410,620,20), FVector(-1320,760,20), FVector(-1210,680,20),
        FVector(-1110,560,20), FVector(-1010,720,20), FVector(-900,610,20), FVector(-810,710,20),
        FVector(-690,-540,20), FVector(-580,-650,20), FVector(-470,-590,20), FVector(-350,-720,20),
        FVector(-240,-600,20), FVector(-120,-690,20), FVector(10,-610,20), FVector(140,-680,20),
        FVector(-360,420,20), FVector(-250,520,20), FVector(-120,580,20), FVector(20,520,20),
        FVector(160,540,20), FVector(300,470,20), FVector(430,560,20), FVector(560,440,20),
        FVector(690,-510,20), FVector(820,-590,20), FVector(950,-530,20), FVector(1080,-610,20),
        FVector(1180,480,20), FVector(1320,520,20), FVector(1460,470,20), FVector(1580,560,20),
        FVector(1760,-420,20), FVector(1880,-520,20), FVector(2010,-430,20), FVector(2150,-520,20),
        FVector(2250,480,20), FVector(2380,540,20), FVector(2490,430,20), FVector(2600,520,20)
    };

    for (int32 Index = 0; Index < UE_ARRAY_COUNT(GrassPatches); ++Index)
    {
        const FVector Base = GrassPatches[Index];
        const float Size = 0.10f + 0.015f * static_cast<float>(Index % 4);
        const float Height = 0.18f + 0.025f * static_cast<float>(Index % 5);
        GrassInstances->AddInstance(FTransform(
            FRotator(0.0f, static_cast<float>((Index * 37) % 360), 0.0f),
            Base,
            FVector(Size, Size, Height)));

        GrassInstances->AddInstance(FTransform(
            FRotator(0.0f, static_cast<float>((Index * 53 + 19) % 360), 0.0f),
            Base + FVector(34.0f + 7.0f * (Index % 3), 22.0f - 5.0f * (Index % 2), 0.0f),
            FVector(Size * 0.86f, Size * 0.86f, Height * 0.92f)));
    }

    const FVector FlowerBeds[] = {
        FVector(-2140,-690,38), FVector(-2070,-720,38), FVector(-1990,-680,38),
        FVector(-1270,-560,38), FVector(-1200,-590,38), FVector(-1130,-550,38),
        FVector(-300,610,38), FVector(-180,650,38), FVector(-60,610,38),
        FVector(80,650,38), FVector(220,610,38), FVector(350,650,38),
        FVector(390,390,38), FVector(460,420,38), FVector(530,390,38)
    };

    for (int32 Index = 0; Index < UE_ARRAY_COUNT(FlowerBeds); ++Index)
    {
        const float Scale = 0.055f + 0.008f * static_cast<float>(Index % 3);
        FlowerInstances->AddInstance(FTransform(
            FRotator::ZeroRotator,
            FlowerBeds[Index],
            FVector(Scale, Scale, Scale * 0.75f)));
    }

    const FVector Shrubs[] = {
        FVector(-2280,-610,42), FVector(-2200,-590,42), FVector(-2110,-600,42),
        FVector(-1710,-470,42), FVector(-1620,-450,42), FVector(-1380,470,42),
        FVector(-1280,450,42), FVector(-820,-500,42), FVector(-720,-480,42),
        FVector(-440,420,42), FVector(-340,400,42), FVector(80,-470,42),
        FVector(190,-450,42), FVector(430,500,42), FVector(540,490,42),
        FVector(730,-560,42), FVector(830,-540,42)
    };

    for (int32 Index = 0; Index < UE_ARRAY_COUNT(Shrubs); ++Index)
    {
        const float Scale = 0.24f + 0.035f * static_cast<float>(Index % 4);
        ShrubInstances->AddInstance(FTransform(
            FRotator(0.0f, static_cast<float>((Index * 29) % 360), 0.0f),
            Shrubs[Index],
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

    if (Sun)
    {
        if (UDirectionalLightComponent* SunComponent = Cast<UDirectionalLightComponent>(Sun->GetLightComponent()))
        {
            // UE4.27 requires the light to be movable before changing the actor rotation in PIE.
            SunComponent->SetMobility(EComponentMobility::Movable);
            Sun->SetActorRotation(FRotator(-38.0f, -28.0f, 0.0f));
            SunComponent->SetIntensity(3.4f);
            SunComponent->SetLightColor(FLinearColor(1.0f, 0.82f, 0.63f));
            SunComponent->SetCastShadows(true);
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

    if (Sky)
    {
        if (USkyLightComponent* SkyComponent = Cast<USkyLightComponent>(Sky->GetLightComponent()))
        {
            SkyComponent->SetMobility(EComponentMobility::Movable);
            SkyComponent->SetIntensity(0.78f);
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

    if (PostProcess)
    {
        PostProcess->bUnbound = true;
        PostProcess->BlendWeight = 1.0f;

        PostProcess->Settings.bOverride_AutoExposureMinBrightness = true;
        PostProcess->Settings.AutoExposureMinBrightness = 0.80f;
        PostProcess->Settings.bOverride_AutoExposureMaxBrightness = true;
        PostProcess->Settings.AutoExposureMaxBrightness = 1.20f;
        PostProcess->Settings.bOverride_AutoExposureBias = true;
        PostProcess->Settings.AutoExposureBias = 0.10f;

        PostProcess->Settings.bOverride_BloomIntensity = true;
        PostProcess->Settings.BloomIntensity = 0.25f;
        PostProcess->Settings.bOverride_VignetteIntensity = true;
        PostProcess->Settings.VignetteIntensity = 0.12f;
    }
}

void AShirePrototypeWorldBuilder::SpawnVillage()
{
    // Broad terrain slabs: cheap greybox geometry sized for the target 2 GB VRAM laptop.
    SpawnShape(CubeMesh, FVector(0.0f, 0.0f, -70.0f), FVector(65.0f, 42.0f, 0.7f),
        FLinearColor(0.16f, 0.34f, 0.10f), FRotator::ZeroRotator, true);

    // Rolling hill silhouettes break the flat slab horizon while keeping the low-spec
    // runtime proxy cheap. A later asset pass can replace these with authored Landscape.
    SpawnShape(SphereMesh, FVector(-2250.0f, -760.0f, -135.0f), FVector(7.0f, 5.2f, 3.4f),
        FLinearColor(0.13f, 0.33f, 0.09f), FRotator::ZeroRotator, false);
    SpawnShape(SphereMesh, FVector(-1450.0f, 720.0f, -150.0f), FVector(7.5f, 4.8f, 3.5f),
        FLinearColor(0.15f, 0.37f, 0.10f), FRotator::ZeroRotator, false);
    SpawnShape(SphereMesh, FVector(160.0f, 930.0f, -165.0f), FVector(9.0f, 5.5f, 3.8f),
        FLinearColor(0.14f, 0.35f, 0.09f), FRotator::ZeroRotator, false);
    SpawnShape(SphereMesh, FVector(1620.0f, -720.0f, -160.0f), FVector(8.0f, 4.7f, 3.6f),
        FLinearColor(0.12f, 0.32f, 0.08f), FRotator::ZeroRotator, false);
    SpawnShape(SphereMesh, FVector(2250.0f, 760.0f, -170.0f), FVector(8.5f, 5.0f, 3.9f),
        FLinearColor(0.13f, 0.34f, 0.09f), FRotator::ZeroRotator, false);

    // Main lane from Bag End through Hobbiton toward the eastern fields.
    const FVector RoadPoints[] = {
        FVector(-2380.0f, -120.0f, 12.0f), FVector(-1950.0f, -80.0f, 12.0f), FVector(-1500.0f, 40.0f, 12.0f),
        FVector(-1000.0f, 90.0f, 12.0f), FVector(-500.0f, 40.0f, 12.0f), FVector(0.0f, -40.0f, 12.0f),
        FVector(500.0f, -120.0f, 12.0f), FVector(1000.0f, -160.0f, 12.0f), FVector(1500.0f, -80.0f, 12.0f),
        FVector(2050.0f, 70.0f, 12.0f), FVector(2550.0f, 120.0f, 12.0f)
    };

    for (const FVector& P : RoadPoints)
    {
        SpawnShape(CubeMesh, P, FVector(2.8f, 1.1f, 0.10f), FLinearColor(0.40f, 0.27f, 0.14f), FRotator::ZeroRotator, true);
    }

    // Narrow footpaths invite exploration between homes instead of keeping the player
    // on one obvious corridor.
    const FVector FootpathPoints[] = {
        FVector(-2240, -360, 15), FVector(-1990, -470, 15), FVector(-1740, -500, 15),
        FVector(-1360, 330, 15), FVector(-1120, 420, 15), FVector(-850, 420, 15),
        FVector(-560, 300, 15), FVector(-320, 500, 15), FVector(-40, 610, 15),
        FVector(320, 480, 15), FVector(620, 290, 15)
    };
    for (const FVector& P : FootpathPoints)
    {
        SpawnShape(CubeMesh, P, FVector(1.55f, 0.52f, 0.065f),
            FLinearColor(0.36f, 0.25f, 0.14f), FRotator::ZeroRotator, true);
    }

    // Simple stone bridge landmark so the story objective has a readable place.
    SpawnShape(CubeMesh, FVector(-1050.0f, 90.0f, 25.0f), FVector(2.0f, 1.05f, 0.16f),
        FLinearColor(0.34f, 0.34f, 0.31f), FRotator::ZeroRotator, true);
    SpawnShape(CubeMesh, FVector(-1050.0f, 185.0f, 62.0f), FVector(2.0f, 0.09f, 0.34f),
        FLinearColor(0.30f, 0.30f, 0.28f), FRotator::ZeroRotator, false);
    SpawnShape(CubeMesh, FVector(-1050.0f, -5.0f, 62.0f), FVector(2.0f, 0.09f, 0.34f),
        FLinearColor(0.30f, 0.30f, 0.28f), FRotator::ZeroRotator, false);

    // The Water: a narrow stream and mill landmark turn the bridge into a place rather
    // than a quest coordinate.
    SpawnShape(CubeMesh, FVector(-1060.0f, 310.0f, -4.0f), FVector(8.0f, 1.0f, 0.06f),
        FLinearColor(0.055f, 0.26f, 0.38f), FRotator(0.0f, 88.0f, 0.0f), false);
    SpawnShape(CubeMesh, FVector(-1250.0f, 330.0f, 88.0f), FVector(1.45f, 1.05f, 0.88f),
        FLinearColor(0.52f, 0.39f, 0.23f), FRotator::ZeroRotator, true);
    SpawnShape(ConeMesh, FVector(-1250.0f, 330.0f, 215.0f), FVector(1.65f, 1.25f, 0.52f),
        FLinearColor(0.30f, 0.17f, 0.075f), FRotator::ZeroRotator, false);
    SpawnShape(CylinderMesh, FVector(-1135.0f, 330.0f, 95.0f), FVector(0.74f, 0.74f, 0.09f),
        FLinearColor(0.24f, 0.16f, 0.08f), FRotator(0.0f, 90.0f, 0.0f), false);
    SpawnLabel(TEXT("The Mill"), FVector(-1250.0f, 330.0f, 320.0f), FLinearColor(0.86f, 0.82f, 0.66f));

    // Bag End and nearby Hobbiton homes.
    SpawnHobbitHole(FVector(-2210.0f, -520.0f, 0.0f), 1.25f);
    SpawnLabel(TEXT("Bag End"), FVector(-2210.0f, -520.0f, 270.0f), FLinearColor::Yellow);

    SpawnHobbitHole(FVector(-1680.0f, -520.0f, 0.0f), 0.95f);
    SpawnHobbitHole(FVector(-1320.0f, 520.0f, 0.0f), 1.05f);
    SpawnHobbitHole(FVector(-760.0f, -540.0f, 0.0f), 0.90f);
    SpawnHobbitHole(FVector(-380.0f, 470.0f, 0.0f), 0.92f);
    SpawnHobbitHole(FVector(120.0f, -520.0f, 0.0f), 0.88f);
    SpawnHobbitHole(FVector(-1960.0f, 560.0f, 0.0f), 0.82f);
    SpawnHobbitHole(FVector(-1160.0f, -690.0f, 0.0f), 0.78f);
    SpawnHobbitHole(FVector(430.0f, 520.0f, 0.0f), 0.82f);
    SpawnHobbitHole(FVector(760.0f, -610.0f, 0.0f), 0.80f);
    SpawnHobbitHole(FVector(980.0f, 520.0f, 0.0f), 0.76f);
    SpawnHobbitHole(FVector(1280.0f, 610.0f, 0.0f), 0.72f);
    SpawnHobbitHole(FVector(1580.0f, 520.0f, 0.0f), 0.70f);
    SpawnHobbitHole(FVector(-1780.0f, 920.0f, 0.0f), 0.72f);

    // Home gardens and fences make the lane read as lived-in Hobbiton rather than a
    // collection of isolated primitive shapes.
    SpawnGardenPatch(FVector(-1910.0f, -700.0f, 0.0f), 0.80f);
    SpawnGardenPatch(FVector(-1220.0f, -560.0f, 0.0f), 0.68f);
    SpawnGardenPatch(FVector(430.0f, 390.0f, 0.0f), 0.70f);
    SpawnFenceLine(FVector(-2290.0f, -810.0f, 0.0f), FVector(-1600.0f, -810.0f, 0.0f), 7);
    SpawnFenceLine(FVector(-1540.0f, -680.0f, 0.0f), FVector(-930.0f, -680.0f, 0.0f), 6);
    SpawnFenceLine(FVector(250.0f, 340.0f, 0.0f), FVector(720.0f, 340.0f, 0.0f), 5);

    // The Green Dragon / market silhouette.
    SpawnShape(CubeMesh, FVector(-670.0f, 250.0f, 115.0f), FVector(2.1f, 1.5f, 1.15f),
        FLinearColor(0.45f, 0.30f, 0.17f), FRotator::ZeroRotator, true);
    SpawnShape(ConeMesh, FVector(-670.0f, 250.0f, 270.0f), FVector(2.4f, 1.8f, 0.7f),
        FLinearColor(0.28f, 0.12f, 0.05f), FRotator::ZeroRotator, false);
    SpawnLabel(TEXT("The Green Dragon"), FVector(-670.0f, 250.0f, 370.0f), FLinearColor(0.85f, 0.80f, 0.55f));

    // Small market square: stalls, produce tables, benches and a cart make the village
    // center feel used even when the player is not on a quest.
    const FVector MarketStalls[] = {
        FVector(-910, 130, 38), FVector(-770, 80, 38), FVector(-590, 70, 38), FVector(-450, 145, 38)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(MarketStalls); ++Index)
    {
        const FVector Stall = MarketStalls[Index];
        SpawnShape(CubeMesh, Stall, FVector(0.72f, 0.38f, 0.08f),
            FLinearColor(0.43f, 0.28f, 0.13f), FRotator::ZeroRotator, true);
        SpawnShape(CubeMesh, Stall + FVector(0, 0, 75), FVector(0.78f, 0.44f, 0.05f),
            Index % 2 == 0 ? FLinearColor(0.48f, 0.20f, 0.12f) : FLinearColor(0.22f, 0.39f, 0.16f),
            FRotator::ZeroRotator, false);
        SpawnShape(CubeMesh, Stall + FVector(-55, -28, 30), FVector(0.08f, 0.08f, 0.55f),
            FLinearColor(0.30f, 0.18f, 0.08f), FRotator::ZeroRotator, false);
        SpawnShape(CubeMesh, Stall + FVector(55, 28, 30), FVector(0.08f, 0.08f, 0.55f),
            FLinearColor(0.30f, 0.18f, 0.08f), FRotator::ZeroRotator, false);
    }

    SpawnShape(CubeMesh, FVector(-350, 270, 35), FVector(1.15f, 0.42f, 0.13f),
        FLinearColor(0.34f, 0.20f, 0.09f), FRotator(0, -18, 0), true);
    SpawnShape(CylinderMesh, FVector(-420, 220, 38), FVector(0.22f, 0.22f, 0.10f),
        FLinearColor(0.18f, 0.12f, 0.07f), FRotator(90, 0, 0), false);
    SpawnShape(CylinderMesh, FVector(-280, 320, 38), FVector(0.22f, 0.22f, 0.10f),
        FLinearColor(0.18f, 0.12f, 0.07f), FRotator(90, 0, 0), false);

    // Party field with central tree and simple pavilion blocks.
    SpawnTree(FVector(-50.0f, 720.0f, 0.0f), 1.35f);
    SpawnShape(CubeMesh, FVector(220.0f, 710.0f, 50.0f), FVector(1.4f, 0.8f, 0.5f),
        FLinearColor(0.70f, 0.62f, 0.38f), FRotator::ZeroRotator, true);
    SpawnLabel(TEXT("Party Field"), FVector(-50.0f, 720.0f, 360.0f), FLinearColor::White);

    // Tables, benches and lantern posts create a readable celebration space.
    const FVector PartyTables[] = {
        FVector(-230, 620, 40), FVector(20, 610, 40), FVector(270, 610, 40),
        FVector(-150, 820, 40), FVector(130, 835, 40)
    };
    for (const FVector& Table : PartyTables)
    {
        SpawnShape(CubeMesh, Table, FVector(0.80f, 0.34f, 0.08f),
            FLinearColor(0.43f, 0.27f, 0.12f), FRotator::ZeroRotator, true);
        SpawnShape(CubeMesh, Table + FVector(0.0f, 58.0f, -20.0f), FVector(0.75f, 0.10f, 0.11f),
            FLinearColor(0.34f, 0.20f, 0.09f), FRotator::ZeroRotator, true);
        SpawnShape(CubeMesh, Table + FVector(0.0f, -58.0f, -20.0f), FVector(0.75f, 0.10f, 0.11f),
            FLinearColor(0.34f, 0.20f, 0.09f), FRotator::ZeroRotator, true);
    }
    // Hay, barrels and a small speech platform add readable party preparation.
    const FVector PartyProps[] = {
        FVector(-320, 735, 28), FVector(335, 735, 28), FVector(-270, 900, 28), FVector(250, 930, 28)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(PartyProps); ++Index)
    {
        SpawnShape(CylinderMesh, PartyProps[Index], FVector(0.28f, 0.28f, 0.30f),
            Index % 2 == 0 ? FLinearColor(0.58f, 0.44f, 0.16f) : FLinearColor(0.28f, 0.17f, 0.08f),
            FRotator::ZeroRotator, true);
    }
    SpawnShape(CubeMesh, FVector(240, 890, 25), FVector(1.15f, 0.72f, 0.12f),
        FLinearColor(0.40f, 0.24f, 0.10f), FRotator::ZeroRotator, true);

    const FVector LanternPosts[] = {
        FVector(-390, 520, 0), FVector(390, 520, 0), FVector(-390, 920, 0), FVector(390, 920, 0),
        FVector(0, 500, 0), FVector(0, 950, 0)
    };
    for (const FVector& Post : LanternPosts)
    {
        SpawnShape(CylinderMesh, Post + FVector(0, 0, 105), FVector(0.045f, 0.045f, 1.05f),
            FLinearColor(0.24f, 0.13f, 0.06f), FRotator::ZeroRotator, false);
        SpawnShape(SphereMesh, Post + FVector(0, 0, 208), FVector(0.11f),
            FLinearColor(0.92f, 0.62f, 0.18f), FRotator::ZeroRotator, false);
    }

    // Crop rows and field props visually prepare the later shortcut encounter.
    for (int32 Row = 0; Row < 8; ++Row)
    {
        const float Y = -520.0f + Row * 115.0f;
        SpawnShape(CubeMesh, FVector(1260.0f, Y, 8.0f), FVector(3.9f, 0.11f, 0.06f),
            FLinearColor(0.30f, 0.22f, 0.075f), FRotator::ZeroRotator, false);
        for (int32 Plant = 0; Plant < 6; ++Plant)
        {
            SpawnShape(SphereMesh, FVector(980.0f + Plant * 110.0f, Y, 26.0f), FVector(0.10f, 0.10f, 0.16f),
                FLinearColor(0.32f, 0.46f, 0.12f), FRotator::ZeroRotator, false);
        }
    }
    SpawnShape(CylinderMesh, FVector(1510, -580, 36), FVector(0.42f, 0.42f, 0.36f),
        FLinearColor(0.64f, 0.48f, 0.16f), FRotator::ZeroRotator, true);
    SpawnShape(CylinderMesh, FVector(1590, -540, 36), FVector(0.38f, 0.38f, 0.34f),
        FLinearColor(0.64f, 0.48f, 0.16f), FRotator::ZeroRotator, true);

    // Wooded-road cover: dense silhouettes, hedges and a fallen root/log create actual
    // line-of-sight choices for the Black Rider encounter.
    const FVector WoodedRoadTrees[] = {
        FVector(1620,-520,0), FVector(1740,-650,0), FVector(1890,-540,0), FVector(2060,-620,0),
        FVector(1700,430,0), FVector(1860,520,0), FVector(2020,430,0), FVector(2190,520,0)
    };
    for (const FVector& P : WoodedRoadTrees)
    {
        SpawnTree(P, 0.92f);
    }
    SpawnFenceLine(FVector(1580,-360,0), FVector(2210,-360,0), 7);
    SpawnFenceLine(FVector(1580,340,0), FVector(2210,340,0), 7);
    SpawnShape(CylinderMesh, FVector(1780,235,42), FVector(0.22f, 0.22f, 1.35f),
        FLinearColor(0.20f, 0.10f, 0.045f), FRotator(0, 82, 90), true);
    SpawnShape(SphereMesh, FVector(1745,220,48), FVector(0.95f, 0.42f, 0.30f),
        FLinearColor(0.12f, 0.29f, 0.075f), FRotator::ZeroRotator, true);

    // Brandywine river and Bucklebury Ferry destination.
    SpawnShape(CubeMesh, FVector(2780.0f, 120.0f, -10.0f), FVector(2.7f, 42.0f, 0.18f),
        FLinearColor(0.06f, 0.24f, 0.42f), FRotator::ZeroRotator, false);
    SpawnShape(CubeMesh, FVector(2690.0f, 120.0f, 12.0f), FVector(1.4f, 1.8f, 0.12f),
        FLinearColor(0.34f, 0.20f, 0.09f), FRotator::ZeroRotator, true);
    SpawnShape(CubeMesh, FVector(2940.0f, 120.0f, 12.0f), FVector(1.4f, 1.8f, 0.12f),
        FLinearColor(0.34f, 0.20f, 0.09f), FRotator::ZeroRotator, true);
    const FVector FerryPosts[] = {
        FVector(2580,-20,0), FVector(2580,260,0), FVector(3060,-20,0), FVector(3060,260,0)
    };
    for (const FVector& Post : FerryPosts)
    {
        SpawnShape(CylinderMesh, Post + FVector(0,0,70), FVector(0.08f,0.08f,0.70f),
            FLinearColor(0.26f,0.15f,0.07f), FRotator::ZeroRotator, true);
    }
    SpawnShape(CubeMesh, FVector(2820,120,24), FVector(1.05f,0.78f,0.10f),
        FLinearColor(0.30f,0.18f,0.085f), FRotator::ZeroRotator, true);
    SpawnLabel(TEXT("Bucklebury Ferry"), FVector(2500.0f, 120.0f, 250.0f), FLinearColor::White);

    // Trees deliberately sparse in greybox; final foliage will use instancing/LODs.
    const FVector TreeLocations[] = {
        FVector(-2050, 420, 0), FVector(-1820, 760, 0), FVector(-1500, -840, 0), FVector(-1080, -720, 0),
        FVector(-820, 820, 0), FVector(-300, -820, 0), FVector(360, 760, 0), FVector(720, -680, 0),
        FVector(1050, 620, 0), FVector(1320, -610, 0), FVector(1600, 590, 0), FVector(1900, -500, 0),
        FVector(2200, 550, 0), FVector(2460, -440, 0)
    };
    for (const FVector& P : TreeLocations)
    {
        SpawnTree(P, 0.82f);
    }

    const FVector OrchardTrees[] = {
        FVector(-2100, -980, 0), FVector(-1850, -1050, 0), FVector(-1570, -940, 0),
        FVector(-1210, 900, 0), FVector(-970, 1030, 0), FVector(-690, 940, 0),
        FVector(530, 980, 0), FVector(810, 860, 0), FVector(1210, 780, 0),
        FVector(1510, 910, 0), FVector(2030, 880, 0), FVector(2380, 720, 0)
    };
    for (const FVector& P : OrchardTrees)
    {
        SpawnTree(P, 0.62f);
    }

    // Lightweight ambient population. The final art pass will replace these with optimized skeletal NPCs.
    const FVector HobbitStarts[] = {
        FVector(-2050, -330, 20), FVector(-1840, 80, 20), FVector(-1660, -420, 20),
        FVector(-1510, 160, 20), FVector(-1320, 430, 20), FVector(-1180, 20, 20),
        FVector(-900, 330, 20), FVector(-760, -360, 20), FVector(-610, -120, 20),
        FVector(-310, 190, 20), FVector(-80, 420, 20), FVector(220, 180, 20),
        FVector(380, 610, 20), FVector(480, -40, 20), FVector(760, 150, 20),
        FVector(980, -220, 20), FVector(1180, 220, 20), FVector(1390, -330, 20),
        FVector(-1180, 300, 20), FVector(-480, 250, 20), FVector(-250, 820, 20),
        FVector(100, 900, 20), FVector(620, 620, 20), FVector(1060, -440, 20),
        FVector(1500, 400, 20), FVector(2080, 250, 20), FVector(2440, 40, 20),
        FVector(2520, 310, 20)
    };

    for (int32 Index = 0; Index < UE_ARRAY_COUNT(HobbitStarts); ++Index)
    {
        AShireAmbientNPC* Hobbit = GetWorld()->SpawnActor<AShireAmbientNPC>(HobbitStarts[Index], FRotator::ZeroRotator);
        if (Hobbit)
        {
            Hobbit->RoutinePointA = HobbitStarts[Index];
            const float Side = (Index % 2 == 0) ? 1.0f : -1.0f;
            Hobbit->RoutinePointB = HobbitStarts[Index] + FVector(240.0f + 20.0f * (Index % 3), Side * 110.0f, 0.0f);
            Hobbit->WalkSpeed = 45.0f + 5.0f * (Index % 4);

            if (Index < 5)
            {
                Hobbit->RoutineRole = TEXT("Gardener");
                Hobbit->MinWait = 2.5f;
                Hobbit->MaxWait = 6.0f;
            }
            else if (Index < 11)
            {
                Hobbit->RoutineRole = TEXT("Villager");
            }
            else if (Index < 18)
            {
                Hobbit->RoutineRole = TEXT("PartyGuest");
                Hobbit->PlayerNoticeRadius = 330.0f;
                Hobbit->MinWait = 1.0f;
                Hobbit->MaxWait = 3.0f;
            }
            else if (Index < 24)
            {
                Hobbit->RoutineRole = TEXT("FieldWorker");
                Hobbit->WalkSpeed = 42.0f;
                Hobbit->MinWait = 2.0f;
                Hobbit->MaxWait = 5.5f;
            }
            else
            {
                Hobbit->RoutineRole = TEXT("Courier");
                Hobbit->WalkSpeed = 68.0f;
                Hobbit->PlayerNoticeRadius = 240.0f;
            }
        }
    }
}


void AShirePrototypeWorldBuilder::SpawnSideStories()
{
    if (!GetWorld())
    {
        return;
    }

    // Optional: help Hamfast check the Bag End garden before the party. This does not
    // replace the active Shire quest and remains completed after save/load.
    AShireNPC* Hamfast = GetWorld()->SpawnActor<AShireNPC>(
        FVector(-2050.0f, -690.0f, 65.0f), FRotator(0.0f, 25.0f, 0.0f));
    if (Hamfast)
    {
        Hamfast->DisplayName = FText::FromString(TEXT("Hamfast Gamgee"));
        Hamfast->DialogueLines = {
            FText::FromString(TEXT("Frodo, if you have a moment, take a look along the lower garden fence. The party traffic has everyone cutting across the beds.")),
            FText::FromString(TEXT("Good soil asks for patience. Folk are much the same, if you ask me."))
        };
        Hamfast->SideStoryBeatAfterInteraction = TEXT("Side_GardenHelpStarted");
        Hamfast->SideStoryStartMessage = FText::FromString(TEXT("Optional: Walk the lower Bag End garden and check the fence."));
    }

    AShireQuestTrigger* GardenCheck = GetWorld()->SpawnActor<AShireQuestTrigger>(
        FVector(-1740.0f, -790.0f, 70.0f), FRotator::ZeroRotator);
    if (GardenCheck)
    {
        GardenCheck->RequiredSideStoryBeat = TEXT("Side_GardenHelpStarted");
        GardenCheck->SideStoryBeatAfterTrigger = TEXT("Side_GardenHelpComplete");
        GardenCheck->ObjectiveMessage = FText::FromString(TEXT("Side story complete: the garden path and fence are clear before the party."));
    }

    // Optional: Rosie needs the last party tables checked before the field fills up.
    AShireNPC* Rosie = GetWorld()->SpawnActor<AShireNPC>(
        FVector(-650.0f, 390.0f, 65.0f), FRotator(0.0f, 205.0f, 0.0f));
    if (Rosie)
    {
        Rosie->DisplayName = FText::FromString(TEXT("Rosie Cotton"));
        Rosie->DialogueLines = {
            FText::FromString(TEXT("They have carried half the Green Dragon into that field. If you pass the party tables, make sure the far row has not been forgotten.")),
            FText::FromString(TEXT("Everyone says Bilbo planned too much. I think they will change their minds once the food arrives."))
        };
        Rosie->SideStoryBeatAfterInteraction = TEXT("Side_PartyTablesStarted");
        Rosie->SideStoryStartMessage = FText::FromString(TEXT("Optional: Check the far party tables before meeting Bilbo."));
    }

    AShireQuestTrigger* PartyTableCheck = GetWorld()->SpawnActor<AShireQuestTrigger>(
        FVector(310.0f, 830.0f, 75.0f), FRotator::ZeroRotator);
    if (PartyTableCheck)
    {
        PartyTableCheck->RequiredSideStoryBeat = TEXT("Side_PartyTablesStarted");
        PartyTableCheck->SideStoryBeatAfterTrigger = TEXT("Side_PartyTablesComplete");
        PartyTableCheck->ObjectiveMessage = FText::FromString(TEXT("Side story complete: the last tables are ready for the celebration."));
    }

    // Optional: Farmer Maggot's warning gives the eastern fields context before the
    // later shortcut and Rider sequence.
    AShireNPC* Maggot = GetWorld()->SpawnActor<AShireNPC>(
        FVector(1010.0f, -430.0f, 65.0f), FRotator(0.0f, 155.0f, 0.0f));
    if (Maggot)
    {
        Maggot->DisplayName = FText::FromString(TEXT("Farmer Maggot"));
        Maggot->DialogueLines = {
            FText::FromString(TEXT("There have been strangers asking questions beyond the fields. If you are walking east, keep an eye on the old boundary fence.")),
            FText::FromString(TEXT("The crops are ordinary. The questions were not."))
        };
        Maggot->SideStoryBeatAfterInteraction = TEXT("Side_FieldWatchStarted");
        Maggot->SideStoryStartMessage = FText::FromString(TEXT("Optional: Follow the field edge and inspect the old boundary fence."));
    }

    AShireQuestTrigger* FieldWatch = GetWorld()->SpawnActor<AShireQuestTrigger>(
        FVector(1450.0f, -500.0f, 75.0f), FRotator::ZeroRotator);
    if (FieldWatch)
    {
        FieldWatch->RequiredSideStoryBeat = TEXT("Side_FieldWatchStarted");
        FieldWatch->SideStoryBeatAfterTrigger = TEXT("Side_FieldWatchComplete");
        FieldWatch->ObjectiveMessage = FText::FromString(TEXT("Side story complete: hoof marks and a disturbed fence lead toward the wooded road."));
    }

    // Free ambient conversations add character without forcing a task.
    AShireNPC* OldNoakes = GetWorld()->SpawnActor<AShireNPC>(
        FVector(-930.0f, 470.0f, 65.0f), FRotator(0.0f, 210.0f, 0.0f));
    if (OldNoakes)
    {
        OldNoakes->DisplayName = FText::FromString(TEXT("Old Noakes"));
        OldNoakes->DialogueLines = {
            FText::FromString(TEXT("Too many carts on the lane today. Mark my words, a proper party begins with everyone arriving late.")),
            FText::FromString(TEXT("Still, it is good to see the Hill busy again."))
        };
    }

    AShireNPC* PartyCook = GetWorld()->SpawnActor<AShireNPC>(
        FVector(-30.0f, 570.0f, 65.0f), FRotator(0.0f, 90.0f, 0.0f));
    if (PartyCook)
    {
        PartyCook->DisplayName = FText::FromString(TEXT("Party Cook"));
        PartyCook->DialogueLines = {
            FText::FromString(TEXT("If one more cousin asks when supper begins, I shall put them to work peeling potatoes.")),
            FText::FromString(TEXT("Bilbo asked for enough food to feed the whole Shire. I suspect he meant it."))
        };
    }

    AShireNPC* FieldHand = GetWorld()->SpawnActor<AShireNPC>(
        FVector(1220.0f, 360.0f, 65.0f), FRotator(0.0f, 250.0f, 0.0f));
    if (FieldHand)
    {
        FieldHand->DisplayName = FText::FromString(TEXT("Hobbiton Field Hand"));
        FieldHand->DialogueLines = {
            FText::FromString(TEXT("The road is quieter past the last hedges. Nice walking, if you do not mind being far from a warm kitchen.")),
            FText::FromString(TEXT("I would stay for the fireworks before going anywhere east."))
        };
    }

    AShireNPC* Miller = GetWorld()->SpawnActor<AShireNPC>(
        FVector(-1210.0f, 240.0f, 65.0f), FRotator(0.0f, 140.0f, 0.0f));
    if (Miller)
    {
        Miller->DisplayName = FText::FromString(TEXT("Hobbiton Miller"));
        Miller->DialogueLines = {
            FText::FromString(TEXT("The wheel has been turning since sunrise. Party day or not, flour does not grind itself.")),
            FText::FromString(TEXT("Take the bridge slowly. Everyone is in too much of a hurry today."))
        };
    }

    AShireNPC* MarketGardener = GetWorld()->SpawnActor<AShireNPC>(
        FVector(-790.0f, 110.0f, 65.0f), FRotator(0.0f, 35.0f, 0.0f));
    if (MarketGardener)
    {
        MarketGardener->DisplayName = FText::FromString(TEXT("Market Gardener"));
        MarketGardener->DialogueLines = {
            FText::FromString(TEXT("Fresh onions, early carrots, and not one quiet customer since breakfast.")),
            FText::FromString(TEXT("Bilbo's party has emptied half the gardens in Hobbiton."))
        };
    }

    AShireNPC* PartyGuest = GetWorld()->SpawnActor<AShireNPC>(
        FVector(250.0f, 800.0f, 65.0f), FRotator(0.0f, 210.0f, 0.0f));
    if (PartyGuest)
    {
        PartyGuest->DisplayName = FText::FromString(TEXT("Excited Party Guest"));
        PartyGuest->DialogueLines = {
            FText::FromString(TEXT("They say the fireworks came all the way from outside the Shire.")),
            FText::FromString(TEXT("I only hope Bilbo remembered enough benches for the relatives who arrive early."))
        };
    }

    AShireNPC* EastRoadWalker = GetWorld()->SpawnActor<AShireNPC>(
        FVector(1710.0f, 420.0f, 65.0f), FRotator(0.0f, 270.0f, 0.0f));
    if (EastRoadWalker)
    {
        EastRoadWalker->DisplayName = FText::FromString(TEXT("East Road Walker"));
        EastRoadWalker->DialogueLines = {
            FText::FromString(TEXT("Past those hedges the road feels different. Less laughter, more wind.")),
            FText::FromString(TEXT("If you hear horses after dark, I would step well aside."))
        };
    }

    AShireNPC* FerryKeeper = GetWorld()->SpawnActor<AShireNPC>(
        FVector(2480.0f, 270.0f, 65.0f), FRotator(0.0f, 190.0f, 0.0f));
    if (FerryKeeper)
    {
        FerryKeeper->DisplayName = FText::FromString(TEXT("Ferry Keeper"));
        FerryKeeper->DialogueLines = {
            FText::FromString(TEXT("The current is gentle now. It changes quickly when the wind turns.")),
            FText::FromString(TEXT("Keep the landing clear and the rope where you can reach it."))
        };
    }
}

void AShirePrototypeWorldBuilder::SpawnStoryActors()
{
    if (!GetWorld())
    {
        return;
    }

    // Opening beat is separated from quest progression so presentation can establish
    // the Shire before the player reaches Gandalf.
    AShireQuestTrigger* OpeningBeat = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(-2320.0f, -120.0f, 90.0f), FRotator::ZeroRotator);
    if (OpeningBeat)
    {
        OpeningBeat->QuestId = TEXT("ShireArrival");
        OpeningBeat->RequiredStage = 0;
        OpeningBeat->StageAfterTrigger = -1;
        OpeningBeat->StoryBeatId = TEXT("ShireOpening");
    }

    // Gandalf on the Shire road: first story interaction.
    AShireNPC* GandalfRoad = GetWorld()->SpawnActor<AShireNPC>(FVector(-1950.0f, -40.0f, 70.0f), FRotator(0.0f, 180.0f, 0.0f));
    if (GandalfRoad)
    {
        GandalfRoad->DisplayName = FText::FromString(TEXT("Gandalf"));
        GandalfRoad->DialogueLines = {
            FText::FromString(TEXT("The Shire has not changed much. That is part of its charm.")),
            FText::FromString(TEXT("Come. There is a party ahead, and an old friend waiting."))
        };
        GandalfRoad->QuestId = TEXT("ShireArrival");
        GandalfRoad->RequiredQuestStage = 0;
        GandalfRoad->QuestStageAfterInteraction = 1;
    }

    // Bridge progression.
    AShireQuestTrigger* BridgeTrigger = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(-1050.0f, 90.0f, 90.0f), FRotator::ZeroRotator);
    if (BridgeTrigger)
    {
        BridgeTrigger->QuestId = TEXT("ShireArrival");
        BridgeTrigger->RequiredStage = 1;
        BridgeTrigger->StageAfterTrigger = 2;
        BridgeTrigger->StoryBeatId = TEXT("GandalfArrival");
        BridgeTrigger->ObjectiveMessage = FText::FromString(TEXT("The road bends toward Hobbiton and the party field."));
    }

    AShireQuestTrigger* PartyApproach = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(-120.0f, 470.0f, 90.0f), FRotator::ZeroRotator);
    if (PartyApproach)
    {
        PartyApproach->QuestId = TEXT("ShireArrival");
        PartyApproach->RequiredStage = 2;
        PartyApproach->StageAfterTrigger = 3;
        PartyApproach->StoryBeatId = TEXT("PartyArrival");
        PartyApproach->ObjectiveMessage = FText::FromString(TEXT("Music and lanterns carry across the field."));
    }

    AShireNPC* Bilbo = GetWorld()->SpawnActor<AShireNPC>(FVector(120.0f, 680.0f, 70.0f), FRotator(0.0f, 220.0f, 0.0f));
    if (Bilbo)
    {
        Bilbo->DisplayName = FText::FromString(TEXT("Bilbo"));
        Bilbo->DialogueLines = {
            FText::FromString(TEXT("Enjoy the evening, Frodo. I have been preparing for this one for quite some time.")),
            FText::FromString(TEXT("There are some things an old hobbit must finally leave behind."))
        };
        Bilbo->QuestId = TEXT("ShireArrival");
        Bilbo->RequiredQuestStage = 3;
        Bilbo->QuestStageAfterInteraction = 3;
        Bilbo->NextQuestId = TEXT("LongExpectedParty");
        Bilbo->NextQuestStage = 1;
    }

    // Returning to Bag End transitions into the Ring-secret sequence.
    AShireQuestTrigger* BagEndReturn = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(-2140.0f, -430.0f, 90.0f), FRotator::ZeroRotator);
    if (BagEndReturn)
    {
        BagEndReturn->QuestId = TEXT("LongExpectedParty");
        BagEndReturn->RequiredStage = 1;
        BagEndReturn->StageAfterTrigger = 2;
        BagEndReturn->NextQuestId = TEXT("RingSecret");
        BagEndReturn->NextQuestStage = 0;
        BagEndReturn->StoryBeatId = TEXT("BilboDisappearance");
        BagEndReturn->ObjectiveMessage = FText::FromString(TEXT("Bag End is quiet now. Gandalf is waiting inside."));
    }

    // Dedicated presentation beat before Gandalf's Ring warning. It does not progress the quest.
    AShireQuestTrigger* RingWarningBeat = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(-2160.0f, -555.0f, 80.0f), FRotator::ZeroRotator);
    if (RingWarningBeat)
    {
        RingWarningBeat->QuestId = TEXT("RingSecret");
        RingWarningBeat->RequiredStage = 0;
        RingWarningBeat->StageAfterTrigger = -1;
        RingWarningBeat->StoryBeatId = TEXT("RingWarning");
    }

    AShireNPC* GandalfBagEnd = GetWorld()->SpawnActor<AShireNPC>(FVector(-2160.0f, -610.0f, 70.0f), FRotator(0.0f, 30.0f, 0.0f));
    if (GandalfBagEnd)
    {
        GandalfBagEnd->DisplayName = FText::FromString(TEXT("Gandalf"));
        GandalfBagEnd->DialogueLines = {
            FText::FromString(TEXT("Keep the Ring hidden. Do not use it, and do not speak of it lightly.")),
            FText::FromString(TEXT("You must leave quietly. Sam can be trusted to go with you."))
        };
        GandalfBagEnd->QuestId = TEXT("RingSecret");
        GandalfBagEnd->RequiredQuestStage = 0;
        GandalfBagEnd->QuestStageAfterInteraction = 1;
    }

    AShireNPC* Sam = GetWorld()->SpawnActor<AShireNPC>(FVector(-1870.0f, -560.0f, 65.0f), FRotator(0.0f, 20.0f, 0.0f));
    if (Sam)
    {
        Sam->DisplayName = FText::FromString(TEXT("Sam"));
        Sam->DialogueLines = {
            FText::FromString(TEXT("Wherever the road goes, Mr. Frodo, you will not be taking it alone."))
        };
        Sam->QuestId = TEXT("RingSecret");
        Sam->RequiredQuestStage = 1;
        Sam->QuestStageAfterInteraction = 2;
        Sam->NextQuestId = TEXT("LeavingHome");
        Sam->NextQuestStage = 1;
        Sam->bFollowPlayerAfterInteraction = true;
    }

    AShireQuestTrigger* LeaveHobbiton = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(520.0f, -120.0f, 90.0f), FRotator::ZeroRotator);
    if (LeaveHobbiton)
    {
        LeaveHobbiton->QuestId = TEXT("LeavingHome");
        LeaveHobbiton->RequiredStage = 1;
        LeaveHobbiton->StageAfterTrigger = 2;
        LeaveHobbiton->NextQuestId = TEXT("Shortcut");
        LeaveHobbiton->NextQuestStage = 0;
        LeaveHobbiton->StoryBeatId = TEXT("LeavingHomeRoad");
        LeaveHobbiton->ObjectiveMessage = FText::FromString(TEXT("The lanes of Hobbiton fall behind you."));
    }

    AShireQuestTrigger* CropFields = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(1120.0f, -150.0f, 90.0f), FRotator::ZeroRotator);
    if (CropFields)
    {
        CropFields->QuestId = TEXT("Shortcut");
        CropFields->RequiredStage = 0;
        CropFields->StageAfterTrigger = 1;
        CropFields->ObjectiveMessage = FText::FromString(TEXT("Voices and crashing footsteps come from the crops ahead."));
    }

    AShireNPC* Merry = GetWorld()->SpawnActor<AShireNPC>(FVector(1350.0f, 20.0f, 65.0f), FRotator(0.0f, 200.0f, 0.0f));
    if (Merry)
    {
        Merry->DisplayName = FText::FromString(TEXT("Merry"));
        Merry->DialogueLines = {
            FText::FromString(TEXT("This is a fine mess. Whatever you are doing, we had better move before someone finds us."))
        };
        Merry->QuestId = TEXT("Shortcut");
        Merry->RequiredQuestStage = 1;
        Merry->QuestStageAfterInteraction = 2;
        Merry->bFollowPlayerAfterInteraction = true;
    }

    AShireNPC* Pippin = GetWorld()->SpawnActor<AShireNPC>(FVector(1420.0f, -65.0f, 65.0f), FRotator(0.0f, 170.0f, 0.0f));
    if (Pippin)
    {
        Pippin->DisplayName = FText::FromString(TEXT("Pippin"));
        Pippin->DialogueLines = {
            FText::FromString(TEXT("If we are running, I would very much like to know what we are running from."))
        };
        Pippin->QuestId = TEXT("Shortcut");
        Pippin->RequiredQuestStage = 1;
        Pippin->QuestStageAfterInteraction = 2;
        Pippin->bFollowPlayerAfterInteraction = true;
    }

    AShireQuestTrigger* WoodedRoad = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(1650.0f, -20.0f, 90.0f), FRotator::ZeroRotator);
    if (WoodedRoad)
    {
        WoodedRoad->QuestId = TEXT("Shortcut");
        WoodedRoad->RequiredStage = 2;
        WoodedRoad->StageAfterTrigger = 2;
        WoodedRoad->NextQuestId = TEXT("KeepOffRoad");
        WoodedRoad->NextQuestStage = 0;
        WoodedRoad->StoryBeatId = TEXT("BlackRiderApproach");
        WoodedRoad->ObjectiveMessage = FText::FromString(TEXT("Hoofbeats. Something is coming along the road."));
    }

    ABlackRiderPrototype* Rider = GetWorld()->SpawnActor<ABlackRiderPrototype>(FVector(1850.0f, -260.0f, 35.0f), FRotator::ZeroRotator);
    if (Rider)
    {
        Rider->PatrolA = FVector(1760.0f, -320.0f, 35.0f);
        Rider->PatrolB = FVector(2190.0f, 180.0f, 35.0f);
        Rider->DetectionRadius = 620.0f;
        Rider->CrouchedDetectionRadius = 300.0f;
    }

    AShireQuestTrigger* HideUnderRoad = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(1760.0f, 220.0f, 70.0f), FRotator::ZeroRotator);
    if (HideUnderRoad)
    {
        HideUnderRoad->QuestId = TEXT("KeepOffRoad");
        HideUnderRoad->RequiredStage = 0;
        HideUnderRoad->StageAfterTrigger = 1;
        HideUnderRoad->StoryBeatId = TEXT("RootHide");
        HideUnderRoad->ObjectiveMessage = FText::FromString(TEXT("Stay low and keep out of the Rider's sight."));
    }

    AShireQuestTrigger* EscapeForest = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(2240.0f, 120.0f, 90.0f), FRotator::ZeroRotator);
    if (EscapeForest)
    {
        EscapeForest->QuestId = TEXT("KeepOffRoad");
        EscapeForest->RequiredStage = 1;
        EscapeForest->StageAfterTrigger = 2;
        EscapeForest->NextQuestId = TEXT("FerryEscape");
        EscapeForest->NextQuestStage = 0;
        EscapeForest->ObjectiveMessage = FText::FromString(TEXT("The ferry is close. Run."));
    }

    AShireQuestTrigger* FerryNearSide = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(2510.0f, 120.0f, 90.0f), FRotator::ZeroRotator);
    if (FerryNearSide)
    {
        FerryNearSide->QuestId = TEXT("FerryEscape");
        FerryNearSide->RequiredStage = 0;
        FerryNearSide->StageAfterTrigger = 1;
        FerryNearSide->StoryBeatId = TEXT("FerryEscape");
        FerryNearSide->ObjectiveMessage = FText::FromString(TEXT("Push off and get across the Brandywine."));
    }

    AShireQuestTrigger* FerryFarSide = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(3050.0f, 120.0f, 90.0f), FRotator::ZeroRotator);
    if (FerryFarSide)
    {
        FerryFarSide->QuestId = TEXT("FerryEscape");
        FerryFarSide->RequiredStage = 1;
        FerryFarSide->StageAfterTrigger = 2;
        FerryFarSide->NextChapterId = TEXT("P1C02");
        FerryFarSide->NextChapterQuestId = TEXT("RoadToBree");
        FerryFarSide->NextChapterQuestStage = 0;
        FerryFarSide->ObjectiveMessage = FText::FromString(TEXT("Across the river. The road to Bree begins here."));
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
    SpawnFoliagePass();
    SpawnSideStories();
    SpawnStoryActors();
}
