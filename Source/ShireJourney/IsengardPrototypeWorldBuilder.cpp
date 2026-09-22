#include "IsengardPrototypeWorldBuilder.h"

#include "ShireNPC.h"
#include "ShireAmbientNPC.h"
#include "ShireQuestTrigger.h"
#include "ShireTraversalChallenge.h"
#include "WorldAmbientMotionActor.h"

#include "Components/DirectionalLightComponent.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/SkyLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/ExponentialHeightFog.h"
#include "Engine/PointLight.h"
#include "Engine/SkyLight.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/TextRenderActor.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"
#include "UObject/SoftObjectPath.h"

namespace IsengardVisual
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

AIsengardPrototypeWorldBuilder::AIsengardPrototypeWorldBuilder()
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

void AIsengardPrototypeWorldBuilder::BeginPlay()
{
    Super::BeginPlay();
    BuildIsengard();
}

AStaticMeshActor* AIsengardPrototypeWorldBuilder::SpawnShape(
    UStaticMesh* Mesh, const FVector& Location, const FVector& Scale,
    const FLinearColor& Color, const FRotator& Rotation, bool bCollision)
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
    UStaticMeshComponent* Component = Actor->GetStaticMeshComponent();
    Component->SetStaticMesh(Mesh);
    Component->SetMobility(EComponentMobility::Movable);
    Component->SetCollisionEnabled(bCollision ? ECollisionEnabled::QueryAndPhysics : ECollisionEnabled::NoCollision);
    Actor->SetActorScale3D(Scale);

    const bool bFallbackPrimitive =
        Mesh == CubeMesh || Mesh == SphereMesh || Mesh == CylinderMesh || Mesh == ConeMesh;
    if (BasicMaterial && bFallbackPrimitive)
    {
        if (UMaterialInstanceDynamic* MID = UMaterialInstanceDynamic::Create(BasicMaterial, Actor))
        {
            MID->SetVectorParameterValue(TEXT("Color"), Color);
            Component->SetMaterial(0, MID);
        }
    }

    return Actor;
}

void AIsengardPrototypeWorldBuilder::SpawnLabel(const FString& Text, const FVector& Location, const FLinearColor& Color)
{
    if (!IsengardVisual::ShowPrototypeWorldLabels)
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
    TextComponent->SetWorldSize(44.0f);
    TextComponent->SetTextRenderColor(Color.ToFColor(true));
}

void AIsengardPrototypeWorldBuilder::BuildIsengard()
{
    if (bBuilt || !GetWorld())
    {
        return;
    }
    bBuilt = true;

    // Isengard gets a distinct, low-cost production atmosphere: cold directional
    // light and industrial haze, countered by a bounded set of warm furnace glows.
    ADirectionalLight* IsengardSun = GetWorld()->SpawnActor<ADirectionalLight>(
        FVector::ZeroVector, FRotator(-32.0f, -58.0f, 0.0f));
    if (IsengardSun && IsengardSun->GetLightComponent())
    {
        IsengardSun->Tags.AddUnique(TEXT("RuntimePrototypeGenerated"));
        IsengardSun->GetLightComponent()->SetMobility(EComponentMobility::Movable);
        IsengardSun->GetLightComponent()->SetIntensity(2.15f);
        IsengardSun->GetLightComponent()->SetLightColor(FLinearColor(0.62f, 0.68f, 0.72f));
    }

    ASkyLight* IsengardSky = GetWorld()->SpawnActor<ASkyLight>(
        FVector::ZeroVector, FRotator::ZeroRotator);
    if (IsengardSky && IsengardSky->GetLightComponent())
    {
        IsengardSky->Tags.AddUnique(TEXT("RuntimePrototypeGenerated"));
        IsengardSky->GetLightComponent()->SetMobility(EComponentMobility::Movable);
        IsengardSky->GetLightComponent()->SetIntensity(0.42f);
        IsengardSky->GetLightComponent()->SetLightColor(FLinearColor(0.34f, 0.39f, 0.37f));
        IsengardSky->GetLightComponent()->RecaptureSky();
    }

    AExponentialHeightFog* IsengardFog = GetWorld()->SpawnActor<AExponentialHeightFog>(
        FVector::ZeroVector, FRotator::ZeroRotator);
    if (IsengardFog && IsengardFog->GetComponent())
    {
        IsengardFog->Tags.AddUnique(TEXT("RuntimePrototypeGenerated"));
        IsengardFog->GetComponent()->SetMobility(EComponentMobility::Movable);
        IsengardFog->GetComponent()->SetFogDensity(0.018f);
        IsengardFog->GetComponent()->SetFogHeightFalloff(0.18f);
        IsengardFog->GetComponent()->SetFogInscatteringColor(FLinearColor(0.16f, 0.19f, 0.17f));
    }

    SpawnShape(CubeMesh, FVector(0, 0, -75), FVector(42, 32, 0.75f),
        FLinearColor(0.09f, 0.12f, 0.08f), FRotator::ZeroRotator, true);

    // Ring wall and road into Orthanc.
    for (int32 I = 0; I < 16; ++I)
    {
        const float Angle = (360.0f / 16.0f) * I;
        const float Radians = FMath::DegreesToRadians(Angle);
        const FVector P(FMath::Cos(Radians) * 2500.0f, FMath::Sin(Radians) * 2500.0f, 120.0f);
        SpawnShape(CubeMesh, P, FVector(3.1f, 0.42f, 1.2f),
            FLinearColor(0.16f, 0.17f, 0.15f), FRotator(0, Angle + 90.0f, 0), true);
    }

    for (int32 I = 0; I < 11; ++I)
    {
        SpawnShape(CubeMesh, FVector(-2350.0f + I * 340.0f, 0.0f, 10.0f),
            FVector(2.0f, 0.82f, 0.08f), FLinearColor(0.20f, 0.18f, 0.14f), FRotator::ZeroRotator, true);
    }

    UStaticMesh* OrthancCore = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Isengard/SM_Isengard_OrthancCore.SM_Isengard_OrthancCore"));
    UStaticMesh* OrthancSpire = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Isengard/SM_Isengard_OrthancSpire.SM_Isengard_OrthancSpire"));
    if (OrthancCore && OrthancSpire)
    {
        SpawnShape(OrthancCore, FVector(900, 0, -75), FVector(1.0f),
            FLinearColor(0.055f, 0.06f, 0.065f), FRotator::ZeroRotator, true);
        for (int32 I = 0; I < 4; ++I)
        {
            const float Angle = I * 90.0f;
            const float R = FMath::DegreesToRadians(Angle);
            const FVector Offset(FMath::Cos(R) * 245.0f, FMath::Sin(R) * 245.0f, 0.0f);
            SpawnShape(OrthancSpire, FVector(900, 0, 720) + Offset, FVector(1.0f),
                FLinearColor(0.035f, 0.04f, 0.045f), FRotator(0, Angle, 0), true);
        }
    }
    else
    {
        SpawnShape(CubeMesh, FVector(900, 0, 520), FVector(3.0f, 3.0f, 5.2f),
            FLinearColor(0.055f, 0.06f, 0.065f), FRotator::ZeroRotator, true);
        for (int32 I = 0; I < 4; ++I)
        {
            const float Angle = I * 90.0f;
            const float R = FMath::DegreesToRadians(Angle);
            const FVector Offset(FMath::Cos(R) * 260.0f, FMath::Sin(R) * 260.0f, 0.0f);
            SpawnShape(CubeMesh, FVector(900, 0, 700) + Offset, FVector(0.72f, 1.15f, 7.0f),
                FLinearColor(0.035f, 0.04f, 0.045f), FRotator(0, Angle, 0), true);
        }
        SpawnShape(CubeMesh, FVector(900, 0, 1125), FVector(3.0f, 3.0f, 0.18f),
            FLinearColor(0.07f, 0.07f, 0.075f), FRotator::ZeroRotator, true);
    }
    SpawnLabel(TEXT("Orthanc"), FVector(900, 0, 1450), FLinearColor(0.72f, 0.74f, 0.76f));

    UStaticMesh* PitRim = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Isengard/SM_Isengard_IndustrialPitRim.SM_Isengard_IndustrialPitRim"));
    UStaticMesh* FurnaceStack = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Isengard/SM_Isengard_FurnaceStack.SM_Isengard_FurnaceStack"));
    UStaticMesh* FelledTrunk = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Isengard/SM_Isengard_FelledTrunk.SM_Isengard_FelledTrunk"));
    UStaticMesh* ParapetSlab = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Isengard/SM_Isengard_ParapetSlab.SM_Isengard_ParapetSlab"));
    UStaticMesh* HoistFrame = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Isengard/SM_IsengardHoistFrame.SM_IsengardHoistFrame"));
    UStaticMesh* SlagCart = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Isengard/SM_IsengardSlagCart.SM_IsengardSlagCart"));
    UStaticMesh* TrenchGrate = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Isengard/SM_IsengardTrenchGrate.SM_IsengardTrenchGrate"));
    UStaticMesh* WaterGate = ResolveResidentStaticMesh(TEXT("/Game/Production/World/Isengard/SM_IsengardWaterGate.SM_IsengardWaterGate"));
    for (int32 I = 0; I < 8; ++I)
    {
        const FVector Pit(-200.0f + I * 260.0f, 720.0f + (I % 2) * 180.0f, 10.0f);
        SpawnShape(PitRim ? PitRim : CylinderMesh, Pit,
            PitRim ? FVector(1.0f) : FVector(0.72f, 0.72f, 0.12f),
            FLinearColor(0.10f, 0.085f, 0.07f), FRotator::ZeroRotator, false);
        SpawnShape(FurnaceStack ? FurnaceStack : CylinderMesh, Pit + FVector(0, 0, 45),
            FurnaceStack ? FVector(0.55f) : FVector(0.10f, 0.10f, 0.85f),
            FLinearColor(0.16f, 0.11f, 0.07f), FRotator::ZeroRotator, false);
    }

    // Bible-driven secondary industrial ring: pits, service cuts and stacks repeat on
    // the opposite side of Orthanc so the valley reads as a war-production system,
    // not a single decorative furnace row. All pieces are visual-only to protect traversal.
    for (int32 I = 0; I < 6; ++I)
    {
        const FVector InnerPit(-350.0f + I * 310.0f, -760.0f - (I % 2) * 150.0f, 8.0f);
        SpawnShape(PitRim ? PitRim : CylinderMesh, InnerPit,
            PitRim ? FVector(0.82f) : FVector(0.62f, 0.62f, 0.10f),
            FLinearColor(0.085f, 0.072f, 0.062f), FRotator(0.0f, I * 13.0f, 0.0f), false);
        SpawnShape(FurnaceStack ? FurnaceStack : CylinderMesh, InnerPit + FVector(0, 0, 42),
            FurnaceStack ? FVector(0.46f) : FVector(0.085f, 0.085f, 0.72f),
            FLinearColor(0.14f, 0.09f, 0.06f), FRotator(0.0f, I * -11.0f, 0.0f), false);
        SpawnShape(CubeMesh, InnerPit + FVector(0.0f, 210.0f, -2.0f),
            FVector(1.25f, 0.24f, 0.035f), FLinearColor(0.075f, 0.068f, 0.060f),
            FRotator(0.0f, I * 5.0f, 0.0f), false);
    }

    // Realm Detail Saturation V2: harsh iron, crude mass-production logistics and
    // future flood-control readability. These are bounded visual actors and do not
    // pre-apply the Ent assault outcome.
    const FVector HoistsV2[] = {
        FVector(-520,520,15), FVector(240,610,15), FVector(1180,560,15), FVector(1580,-590,15)
    };
    for (int32 I=0; I<UE_ARRAY_COUNT(HoistsV2); ++I)
        SpawnShape(HoistFrame, HoistsV2[I], FVector(0.62f),
            FLinearColor(0.11f,0.09f,0.07f), FRotator(0,I*17.0f-12.0f,0), false);

    const FVector SlagCartsV2[] = {
        FVector(-760,930,12), FVector(-120,-940,12), FVector(720,970,12), FVector(1420,-920,12)
    };
    for (int32 I=0; I<UE_ARRAY_COUNT(SlagCartsV2); ++I)
        SpawnShape(SlagCart, SlagCartsV2[I], FVector(0.66f),
            FLinearColor(0.13f,0.09f,0.06f), FRotator(0,I*29.0f,0), false);

    for (int32 I=0; I<7; ++I)
    {
        SpawnShape(TrenchGrate, FVector(-650.0f + I*420.0f, -360.0f, 4.0f), FVector(0.72f),
            FLinearColor(0.10f,0.09f,0.08f), FRotator::ZeroRotator, false);
    }
    SpawnShape(WaterGate, FVector(-1180,-1180,20), FVector(0.82f),
        FLinearColor(0.07f,0.075f,0.08f), FRotator(0,90,0), false);
    SpawnShape(WaterGate, FVector(1960,1120,20), FVector(0.72f),
        FLinearColor(0.07f,0.075f,0.08f), FRotator(0,-90,0), false);

    if (ParapetSlab)
    {
        for (int32 I = 0; I < 8; ++I)
        {
            const float Angle = I * 45.0f;
            const float R = FMath::DegreesToRadians(Angle);
            const FVector BaseRing(
                900.0f + FMath::Cos(R) * 430.0f,
                FMath::Sin(R) * 430.0f,
                25.0f);
            SpawnShape(ParapetSlab, BaseRing, FVector(0.58f),
                FLinearColor(0.055f, 0.060f, 0.065f), FRotator(0.0f, Angle + 90.0f, 0.0f), false);
        }
    }

    // Source 03/11: Isengard should read as a living war-production machine.
    // A few bounded, shadowless industrial motion accents sell machinery without
    // introducing a heavy simulation layer or changing the authored route.
    if (FurnaceStack)
    {
        const FVector FurnaceMotionLocations[] = {
            FVector(-180.0f, 770.0f, 75.0f),
            FVector(360.0f, 900.0f, 75.0f),
            FVector(900.0f, 785.0f, 75.0f),
            FVector(1420.0f, 930.0f, 75.0f),
            FVector(220.0f, -825.0f, 70.0f),
            FVector(1120.0f, -860.0f, 70.0f)
        };
        for (int32 Index = 0; Index < UE_ARRAY_COUNT(FurnaceMotionLocations); ++Index)
        {
            FActorSpawnParameters MotionParams;
            MotionParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
            AWorldAmbientMotionActor* FurnaceMotion = GetWorld()->SpawnActor<AWorldAmbientMotionActor>(
                FurnaceMotionLocations[Index],
                FRotator(0.0f, Index * 17.0f, 0.0f),
                MotionParams);
            if (!FurnaceMotion)
            {
                continue;
            }

            FurnaceMotion->Tags.AddUnique(TEXT("RuntimePrototypeGenerated"));
            FurnaceMotion->Configure(
                FurnaceStack,
                EWorldAmbientMotionMode::Shiver,
                1.5f + 0.25f * (Index % 3),
                1.15f + 0.12f * (Index % 2),
                FVector(0.42f),
                false);
            FurnaceMotion->ConfigureGlow(
                FLinearColor(1.0f, 0.16f, 0.035f),
                260.0f,
                230.0f);
        }
    }

    const FVector ForgeGlowLocations[] = {
        FVector(50.0f, 810.0f, 120.0f),
        FVector(830.0f, 900.0f, 130.0f),
        FVector(1610.0f, 810.0f, 120.0f)
    };
    for (const FVector& GlowLocation : ForgeGlowLocations)
    {
        APointLight* ForgeGlow = GetWorld()->SpawnActor<APointLight>(
            GlowLocation, FRotator::ZeroRotator);
        if (ForgeGlow && ForgeGlow->GetLightComponent())
        {
            ForgeGlow->Tags.AddUnique(TEXT("RuntimePrototypeGenerated"));
            ForgeGlow->GetLightComponent()->SetMobility(EComponentMobility::Movable);
            ForgeGlow->GetLightComponent()->SetIntensity(1900.0f);
            if (UPointLightComponent* PointComponent =
                Cast<UPointLightComponent>(ForgeGlow->GetLightComponent()))
            {
                PointComponent->SetAttenuationRadius(620.0f);
            }
            ForgeGlow->GetLightComponent()->SetLightColor(FLinearColor(1.0f, 0.19f, 0.045f));
        }
    }

    for (int32 I = 0; I < 12; ++I)
    {
        const FVector Stump(-900.0f + I * 210.0f, -820.0f - 90.0f * (I % 3), 25.0f);
        SpawnShape(FelledTrunk ? FelledTrunk : CylinderMesh, Stump,
            FelledTrunk ? FVector(0.55f) : FVector(0.16f, 0.16f, 0.25f),
            FLinearColor(0.22f, 0.12f, 0.055f),
            FelledTrunk ? FRotator(0.0f, I * 27.0f, 88.0f) : FRotator::ZeroRotator,
            true);
    }

    // Raised path acts as the prison overlook. Production parapet slabs replace
    // the visible outer edge where available while the original collision path stays.
    for (int32 I = 0; I < 8; ++I)
    {
        const FVector StepLocation(760.0f + I * 95.0f, -520.0f, 55.0f + I * 85.0f);
        SpawnShape(CubeMesh, StepLocation,
            FVector(0.90f, 0.55f, 0.12f), FLinearColor(0.11f, 0.11f, 0.12f),
            FRotator(0, 0, -7.0f), true);
        if (ParapetSlab && (I % 2 == 0))
        {
            SpawnShape(ParapetSlab, StepLocation + FVector(0.0f, -72.0f, 38.0f),
                FVector(0.62f), FLinearColor(0.07f, 0.075f, 0.08f),
                FRotator(0.0f, 0.0f, -7.0f), false);
        }
    }
    SpawnShape(CubeMesh, FVector(1450, -520, 720), FVector(2.3f, 1.8f, 0.12f),
        FLinearColor(0.09f, 0.09f, 0.10f), FRotator::ZeroRotator, true);
    SpawnLabel(TEXT("Orthanc Prison Overlook"), FVector(1450, -520, 940), FLinearColor::White);

    // Sparse dark birds over the stripped valley add motion without softening Isengard's hostile mood.
    const FVector IsengardBirds[] = {
        FVector(-950, -1050, 640), FVector(150, 1080, 720), FVector(1120, -980, 780)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(IsengardBirds); ++Index)
    {
        AShireAmbientNPC* Bird = GetWorld()->SpawnActor<AShireAmbientNPC>(IsengardBirds[Index], FRotator::ZeroRotator);
        if (!Bird) continue;
        Bird->RoutineRole = TEXT("Bird");
        Bird->RoutinePointA = IsengardBirds[Index];
        Bird->RoutinePointB = IsengardBirds[Index] + FVector(
            720.0f, Index % 2 == 0 ? 460.0f : -460.0f, 100.0f);
        Bird->WalkSpeed = 170.0f + 15.0f * Index;
        Bird->MinWait = 0.0f;
        Bird->MaxWait = 0.0f;
    }

    AShireQuestTrigger* Arrival = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(-1700, 0, 90), FRotator::ZeroRotator);
    if (Arrival)
    {
        Arrival->QuestId = TEXT("IsengardCounsel");
        Arrival->RequiredStage = 0;
        Arrival->StageAfterTrigger = 1;
        Arrival->StoryBeatId = TEXT("IsengardArrival");
        Arrival->ObjectiveMessage = FText::FromString(TEXT("Orthanc rises ahead. Seek Saruman's counsel."));
    }

    AShireNPC* Saruman = GetWorld()->SpawnActor<AShireNPC>(FVector(500, 0, 70), FRotator(0, 180, 0));
    if (Saruman)
    {
        Saruman->DisplayName = FText::FromString(TEXT("Saruman"));
        Saruman->DialogueLines = {
            FText::FromString(TEXT("You came seeking counsel, but the world has moved beyond old assurances.")),
            FText::FromString(TEXT("Power is gathering. Refusing to recognize it will not make it disappear."))
        };
        Saruman->QuestId = TEXT("IsengardCounsel");
        Saruman->RequiredQuestStage = 1;
        Saruman->QuestStageAfterInteraction = 2;
        Saruman->SideStoryBeatAfterInteraction = TEXT("OrthancBetrayal");
        Saruman->NextQuestId = TEXT("OrthancCaptive");
        Saruman->NextQuestStage = 0;
    }

    AShireQuestTrigger* Prison = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(1050, -520, 360), FRotator::ZeroRotator);
    if (Prison)
    {
        Prison->QuestId = TEXT("OrthancCaptive");
        Prison->RequiredStage = 0;
        Prison->StageAfterTrigger = 1;
        Prison->StoryBeatId = TEXT("OrthancPrison");
        Prison->ObjectiveMessage = FText::FromString(TEXT("From the tower, Isengard's transformation becomes impossible to ignore."));
    }

    AShireQuestTrigger* Industry = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(1450, -520, 790), FRotator::ZeroRotator);
    if (Industry)
    {
        Industry->QuestId = TEXT("OrthancCaptive");
        Industry->RequiredStage = 1;
        Industry->StageAfterTrigger = 2;
        Industry->NextQuestId = TEXT("OrthancEscape");
        Industry->NextQuestStage = 0;
        Industry->StoryBeatId = TEXT("IsengardIndustry");
        Industry->ObjectiveMessage = FText::FromString(TEXT("The valley below is being stripped and armed for war."));
    }

    AShireTraversalChallenge* OldCounselMemory = GetWorld()->SpawnActor<AShireTraversalChallenge>(
        FVector(220, -300, 100), FRotator::ZeroRotator);
    if (OldCounselMemory)
    {
        OldCounselMemory->ConfigureActivityChallenge(
            TEXT("ORTHANC_OLD_ALLIANCE_MEMORY"),
            FText::FromString(TEXT("Old Counsel, Broken Trust")),
            TEXT("SOCIAL_MEMORY"),
            FVector(0, 0, 0), FVector(160, 110, 0), FVector(340, -30, 0));
    }

    AShireTraversalChallenge* ParapetSurvey = GetWorld()->SpawnActor<AShireTraversalChallenge>(
        FVector(1320, -760, 790), FRotator::ZeroRotator);
    if (ParapetSurvey)
    {
        ParapetSurvey->ConfigureActivityChallenge(
            TEXT("ORTHANC_PARAPET_VIEW"),
            FText::FromString(TEXT("What Has Changed Below")),
            TEXT("OBSERVATION_CHALLENGE"),
            FVector(0, 0, 0), FVector(180, 120, 0), FVector(360, -50, 0));
    }

    AShireQuestTrigger* Escape = GetWorld()->SpawnActor<AShireQuestTrigger>(FVector(1680, -520, 790), FRotator::ZeroRotator);
    if (Escape)
    {
        Escape->QuestId = TEXT("OrthancEscape");
        Escape->RequiredStage = 0;
        Escape->StageAfterTrigger = 1;
        Escape->StoryBeatId = TEXT("OrthancEscape");
        Escape->ObjectiveMessage = FText::FromString(TEXT("An escape is possible. The warning must reach the free peoples."));
    }
}
