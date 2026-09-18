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

namespace ShireLayout
{
    // UE units are centimeters. These anchors intentionally keep the village compact
    // while making the eastward journey feel like travel rather than a single arena.
    constexpr float HobbitonExitX = 1500.0f;
    constexpr float FieldsX = 7600.0f;
    constexpr float WoodedRoadX = 14500.0f;
    constexpr float FerryX = 23500.0f;
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
        for (int32 Ring = 0; Ring < 12; ++Ring)
        {
            const float Angle = FMath::DegreesToRadians(static_cast<float>((Ring * 137 + GrassIndex * 29) % 360));
            const float Radius = 120.0f + 48.0f * static_cast<float>(Ring % 5);
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
    // The expanded terrain covers roughly 340m x 130m. One cheap slab keeps collision
    // predictable on the low-spec target while hills and vegetation break the horizon.
    SpawnShape(CubeMesh, FVector(10800.0f, 0.0f, -70.0f), FVector(340.0f, 130.0f, 0.7f),
        FLinearColor(0.16f, 0.34f, 0.10f), FRotator::ZeroRotator, true);

    // Horizon / occlusion hills. These deliberately hide later regions so the player
    // discovers them by travelling instead of seeing the ferry from Bag End.
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
        SpawnShape(SphereMesh, HillCenters[Index], FVector(XY, XY * 0.72f, 6.8f + 0.6f * (Index % 2)),
            Index % 2 == 0 ? FLinearColor(0.13f,0.33f,0.09f) : FLinearColor(0.15f,0.37f,0.10f),
            FRotator::ZeroRotator, false);
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
        SpawnShape(CubeMesh, Mid, FVector(Delta.Size2D()/100.0f, 1.15f, 0.10f),
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
        SpawnShape(CubeMesh,(CoreFootpath[Index]+CoreFootpath[Index+1])*0.5f,
            FVector(D.Size2D()/100.0f,0.52f,0.065f),FLinearColor(0.36f,0.25f,0.14f),D.Rotation(),true);
    }

    const FVector FieldLoop[] = {
        FVector(5600,-200,15), FVector(6100,-1200,15), FVector(7350,-1500,15),
        FVector(8600,-1220,15), FVector(9300,-300,15)
    };
    for (int32 Index=0; Index<UE_ARRAY_COUNT(FieldLoop)-1; ++Index)
    {
        const FVector D=FieldLoop[Index+1]-FieldLoop[Index];
        SpawnShape(CubeMesh,(FieldLoop[Index]+FieldLoop[Index+1])*0.5f,
            FVector(D.Size2D()/100.0f,0.46f,0.06f),FLinearColor(0.34f,0.24f,0.13f),D.Rotation(),true);
    }

    // Stone bridge, The Water and mill anchor the village center.
    SpawnShape(CubeMesh, FVector(-1050,90,25), FVector(2.0f,1.05f,0.16f), FLinearColor(0.34f,0.34f,0.31f));
    SpawnShape(CubeMesh, FVector(-1050,185,62), FVector(2.0f,0.09f,0.34f), FLinearColor(0.30f,0.30f,0.28f), FRotator::ZeroRotator,false);
    SpawnShape(CubeMesh, FVector(-1050,-5,62), FVector(2.0f,0.09f,0.34f), FLinearColor(0.30f,0.30f,0.28f), FRotator::ZeroRotator,false);
    SpawnShape(CubeMesh, FVector(-1060,310,-4), FVector(8.0f,1.0f,0.06f), FLinearColor(0.055f,0.26f,0.38f), FRotator(0,88,0),false);
    SpawnShape(CubeMesh, FVector(-1250,330,88), FVector(1.45f,1.05f,0.88f), FLinearColor(0.52f,0.39f,0.23f));
    SpawnShape(ConeMesh, FVector(-1250,330,215), FVector(1.65f,1.25f,0.52f), FLinearColor(0.30f,0.17f,0.075f), FRotator::ZeroRotator,false);
    SpawnShape(CylinderMesh, FVector(-1135,330,95), FVector(0.74f,0.74f,0.09f), FLinearColor(0.24f,0.16f,0.08f), FRotator(0,90,0),false);
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

    // Green Dragon and market.
    SpawnShape(CubeMesh,FVector(-520,360,115),FVector(2.1f,1.5f,1.15f),FLinearColor(0.45f,0.30f,0.17f));
    SpawnShape(ConeMesh,FVector(-520,360,270),FVector(2.4f,1.8f,0.7f),FLinearColor(0.28f,0.12f,0.05f),FRotator::ZeroRotator,false);
    SpawnLabel(TEXT("The Green Dragon"),FVector(-520,360,370),FLinearColor(0.85f,0.80f,0.55f));
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

    // Party Field is a distinct destination north of the village center.
    const FVector PartyCenter(280.0f,1320.0f,0.0f);
    SpawnTree(PartyCenter,1.45f);
    SpawnShape(CubeMesh,PartyCenter+FVector(300,20,50),FVector(1.6f,0.9f,0.5f),FLinearColor(0.70f,0.62f,0.38f));
    SpawnLabel(TEXT("Party Field"),PartyCenter+FVector(0,0,390),FLinearColor::White);
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
    const FVector LanternPosts[] = {
        PartyCenter+FVector(-520,-300,0),PartyCenter+FVector(520,-300,0),
        PartyCenter+FVector(-520,320,0),PartyCenter+FVector(520,320,0),
        PartyCenter+FVector(0,-350,0),PartyCenter+FVector(0,360,0)
    };
    for(const FVector& Post:LanternPosts)
    {
        SpawnShape(CylinderMesh,Post+FVector(0,0,105),FVector(0.045f,0.045f,1.05f),FLinearColor(0.24f,0.13f,0.06f),FRotator::ZeroRotator,false);
        SpawnShape(SphereMesh,Post+FVector(0,0,208),FVector(0.11f),FLinearColor(0.92f,0.62f,0.18f),FRotator::ZeroRotator,false);
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
    for(int32 Row=0; Row<12; ++Row)
    {
        const float Y=-1320.0f+Row*135.0f;
        SpawnShape(CubeMesh,FVector(ShireLayout::FieldsX,Y,8),FVector(12.0f,0.10f,0.06f),
            FLinearColor(0.30f,0.22f,0.075f),FRotator::ZeroRotator,false);
    }
    SpawnShape(CylinderMesh,FVector(8900,-1180,36),FVector(0.48f,0.48f,0.40f),FLinearColor(0.64f,0.48f,0.16f));
    SpawnShape(CylinderMesh,FVector(9020,-1110,36),FVector(0.44f,0.44f,0.38f),FLinearColor(0.64f,0.48f,0.16f));

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
    SpawnShape(CylinderMesh,FVector(14550,1180,42),FVector(0.24f,0.24f,1.55f),
        FLinearColor(0.20f,0.10f,0.045f),FRotator(0,82,90),true);
    SpawnShape(SphereMesh,FVector(14470,1160,50),FVector(1.15f,0.52f,0.36f),
        FLinearColor(0.12f,0.29f,0.075f),FRotator::ZeroRotator,true);
    SpawnLabel(TEXT("Wooded Road"),FVector(ShireLayout::WoodedRoadX,1750,310),FLinearColor(0.72f,0.78f,0.62f));

    // The run to the Brandywine is intentionally long enough to feel like escape.
    for(int32 Index=0; Index<10; ++Index)
    {
        SpawnTree(FVector(18400.0f+Index*380.0f,(Index%2==0 ? 900.0f : -1400.0f),0),0.76f);
    }

    // Brandywine and Bucklebury Ferry. River runs north/south; the story crosses east.
    SpawnShape(CubeMesh,FVector(ShireLayout::FerryX,-500,-10),FVector(14.0f,60.0f,0.18f),
        FLinearColor(0.06f,0.24f,0.42f),FRotator::ZeroRotator,false);
    const float NearX=ShireLayout::FerryX-700.0f;
    const float FarX=ShireLayout::FerryX+700.0f;
    SpawnShape(CubeMesh,FVector(NearX,-500,12),FVector(2.0f,2.0f,0.12f),FLinearColor(0.34f,0.20f,0.09f));
    SpawnShape(CubeMesh,FVector(FarX,-500,12),FVector(2.0f,2.0f,0.12f),FLinearColor(0.34f,0.20f,0.09f));
    SpawnShape(CubeMesh,FVector(ShireLayout::FerryX,-500,24),FVector(1.30f,0.86f,0.10f),FLinearColor(0.30f,0.18f,0.085f));
    const FVector FerryPosts[] = {
        FVector(NearX,-700,70),FVector(NearX,-300,70),FVector(FarX,-700,70),FVector(FarX,-300,70)
    };
    for(const FVector& Post:FerryPosts)
    {
        SpawnShape(CylinderMesh,Post,FVector(0.09f,0.09f,0.72f),FLinearColor(0.26f,0.15f,0.07f));
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

    // Population is clustered where people logically live/work, leaving wilderness quieter.
    const FVector HobbitStarts[] = {
        FVector(-2050,-330,20),FVector(-1840,80,20),FVector(-1660,-420,20),FVector(-1510,160,20),
        FVector(-1320,430,20),FVector(-1180,20,20),FVector(-900,330,20),FVector(-760,-360,20),
        FVector(-610,-120,20),FVector(-310,190,20),FVector(-80,420,20),FVector(220,180,20),
        FVector(-120,1120,20),FVector(180,1460,20),FVector(520,1160,20),FVector(680,1480,20),
        FVector(1150,-320,20),FVector(2500,400,20),
        FVector(6100,-1460,20),FVector(6700,-1180,20),FVector(7350,-900,20),FVector(8200,-450,20),
        FVector(9000,150,20),FVector(10200,-1250,20),
        FVector(11800,1050,20),FVector(12800,780,20),FVector(17200,-650,20),
        FVector(ShireLayout::FerryX-1300,-720,20),FVector(ShireLayout::FerryX-900,-250,20)
    };
    for(int32 Index=0; Index<UE_ARRAY_COUNT(HobbitStarts); ++Index)
    {
        AShireAmbientNPC* Hobbit=GetWorld()->SpawnActor<AShireAmbientNPC>(HobbitStarts[Index],FRotator::ZeroRotator);
        if(!Hobbit) continue;

        Hobbit->RoutinePointA=HobbitStarts[Index];
        const float Side=(Index%2==0)?1.0f:-1.0f;
        Hobbit->RoutinePointB=HobbitStarts[Index]+FVector(300.0f+35.0f*(Index%3),Side*150.0f,0);
        Hobbit->WalkSpeed=44.0f+6.0f*(Index%4);

        if(Index<12)
        {
            Hobbit->RoutineRole=TEXT("Villager");
            Hobbit->MinWait=2.0f;
            Hobbit->MaxWait=5.0f;
        }
        else if(Index<16)
        {
            Hobbit->RoutineRole=TEXT("PartyGuest");
            Hobbit->PlayerNoticeRadius=340.0f;
            Hobbit->MinWait=1.0f;
            Hobbit->MaxWait=3.0f;
        }
        else if(Index<18)
        {
            Hobbit->RoutineRole=TEXT("Courier");
            Hobbit->WalkSpeed=70.0f;
        }
        else if(Index<24)
        {
            Hobbit->RoutineRole=TEXT("FieldWorker");
            Hobbit->WalkSpeed=42.0f;
            Hobbit->MinWait=2.5f;
            Hobbit->MaxWait=6.0f;
        }
        else if(Index<27)
        {
            Hobbit->RoutineRole=TEXT("RoadWalker");
            Hobbit->PlayerNoticeRadius=260.0f;
        }
        else
        {
            Hobbit->RoutineRole=TEXT("FerryWorker");
            Hobbit->WalkSpeed=38.0f;
        }
    }
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
            FText::FromString(TEXT("They have carried half the Green Dragon into that field. If you pass the party tables, make sure the far row has not been forgotten.")),
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

    for(const FTalker& Talker:Talkers)
    {
        AShireNPC* NPC=GetWorld()->SpawnActor<AShireNPC>(Talker.Location,Talker.Rotation);
        if(NPC)
        {
            NPC->DisplayName=FText::FromString(Talker.Name);
            NPC->DialogueLines={FText::FromString(Talker.LineA),FText::FromString(Talker.LineB)};
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
        Bilbo->DialogueLines={
            FText::FromString(TEXT("Enjoy the evening, Frodo. I have been preparing for this one for quite some time.")),
            FText::FromString(TEXT("There are some things an old hobbit must finally leave behind."))
        };
        Bilbo->QuestId=TEXT("ShireArrival");
        Bilbo->RequiredQuestStage=3;
        Bilbo->QuestStageAfterInteraction=3;
        Bilbo->NextQuestId=TEXT("LongExpectedParty");
        Bilbo->NextQuestStage=1;
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
        Merry->QuestStageAfterInteraction=2;
        Merry->bFollowPlayerAfterInteraction=true;
    }

    AShireNPC* Pippin=GetWorld()->SpawnActor<AShireNPC>(FVector(8260,-760,65),FRotator(0,170,0));
    if(Pippin)
    {
        Pippin->DisplayName=FText::FromString(TEXT("Pippin"));
        Pippin->DialogueLines={FText::FromString(TEXT("If we are running, I would very much like to know what we are running from."))};
        Pippin->QuestId=TEXT("Shortcut");
        Pippin->RequiredQuestStage=1;
        Pippin->QuestStageAfterInteraction=2;
        Pippin->bFollowPlayerAfterInteraction=true;
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
