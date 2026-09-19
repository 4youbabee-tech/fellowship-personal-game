#include "FellowshipChapterWorldBuilder.h"

#include "BlackRiderPrototype.h"
#include "FellowshipEnemyPrototype.h"
#include "ShireNPC.h"
#include "ShireAmbientNPC.h"
#include "ShireQuestTrigger.h"

#include "Components/DirectionalLightComponent.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Components/SkyLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/ExponentialHeightFog.h"
#include "Engine/SkyLight.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/TextRenderActor.h"
#include "EngineUtils.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

namespace FellowshipVisual
{
    constexpr bool ShowPrototypeWorldLabels = false;
}

AFellowshipChapterWorldBuilder::AFellowshipChapterWorldBuilder()
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

void AFellowshipChapterWorldBuilder::ConfigureChapterAtmosphere(FName ChapterId)
{
    if (!GetWorld())
    {
        return;
    }

    float SunIntensity = 3.0f;
    FLinearColor SunColor(0.95f, 0.82f, 0.64f);
    FRotator SunRotation(-26.0f, -20.0f, 0.0f);
    float SkyIntensity = 0.76f;
    FLinearColor SkyColor(0.54f, 0.64f, 0.72f);
    float FogDensity = 0.010f;
    float FogHeightFalloff = 0.18f;
    FLinearColor FogColor(0.42f, 0.49f, 0.52f);

    if (ChapterId == TEXT("P1C03"))
    {
        SunIntensity = 2.4f; SunColor = FLinearColor(1.0f, 0.78f, 0.60f); SunRotation = FRotator(-18.0f, -35.0f, 0.0f);
        SkyIntensity = 0.60f; SkyColor = FLinearColor(0.48f, 0.56f, 0.62f);
        FogDensity = 0.018f; FogHeightFalloff = 0.19f; FogColor = FLinearColor(0.28f, 0.32f, 0.34f);
    }
    else if (ChapterId == TEXT("P1C04"))
    {
        SunIntensity = 3.6f; SunColor = FLinearColor(1.0f, 0.88f, 0.68f); SunRotation = FRotator(-32.0f, 55.0f, 0.0f);
        SkyIntensity = 1.00f; SkyColor = FLinearColor(0.65f, 0.75f, 0.82f);
        FogDensity = 0.008f; FogHeightFalloff = 0.22f; FogColor = FLinearColor(0.58f, 0.66f, 0.70f);
    }
    else if (ChapterId == TEXT("P1C05"))
    {
        SunIntensity = 2.8f; SunColor = FLinearColor(0.82f, 0.88f, 1.0f); SunRotation = FRotator(-24.0f, -70.0f, 0.0f);
        SkyIntensity = 0.72f; SkyColor = FLinearColor(0.48f, 0.56f, 0.68f);
        FogDensity = 0.015f; FogHeightFalloff = 0.14f; FogColor = FLinearColor(0.36f, 0.42f, 0.48f);
    }
    else if (ChapterId == TEXT("P1C06"))
    {
        SunIntensity = 0.18f; SunColor = FLinearColor(0.48f, 0.50f, 0.55f); SunRotation = FRotator(-70.0f, 0.0f, 0.0f);
        SkyIntensity = 0.28f; SkyColor = FLinearColor(0.16f, 0.18f, 0.22f);
        FogDensity = 0.028f; FogHeightFalloff = 0.35f; FogColor = FLinearColor(0.08f, 0.09f, 0.11f);
    }
    else if (ChapterId == TEXT("P1C07"))
    {
        SunIntensity = 2.2f; SunColor = FLinearColor(1.0f, 0.80f, 0.42f); SunRotation = FRotator(-38.0f, 30.0f, 0.0f);
        SkyIntensity = 0.90f; SkyColor = FLinearColor(0.72f, 0.58f, 0.30f);
        FogDensity = 0.011f; FogHeightFalloff = 0.24f; FogColor = FLinearColor(0.50f, 0.43f, 0.23f);
    }
    else if (ChapterId != TEXT("P1C08"))
    {
        return;
    }

    ADirectionalLight* Sun = nullptr;
    for (TActorIterator<ADirectionalLight> It(GetWorld()); It; ++It)
    {
        if (It->ActorHasTag(TEXT("RuntimeAtmosphereManaged")))
        {
            Sun = *It;
            break;
        }
    }
    if (!Sun)
    {
        Sun = GetWorld()->SpawnActor<ADirectionalLight>(FVector::ZeroVector, SunRotation);
        if (Sun) Sun->Tags.AddUnique(TEXT("RuntimeAtmosphereManaged"));
    }
    if (Sun && Sun->GetLightComponent())
    {
        Sun->SetActorRotation(SunRotation);
        Sun->GetLightComponent()->SetMobility(EComponentMobility::Movable);
        Sun->GetLightComponent()->SetIntensity(SunIntensity);
        Sun->GetLightComponent()->SetLightColor(SunColor);
    }

    ASkyLight* Sky = nullptr;
    for (TActorIterator<ASkyLight> It(GetWorld()); It; ++It)
    {
        if (It->ActorHasTag(TEXT("RuntimeAtmosphereManaged")))
        {
            Sky = *It;
            break;
        }
    }
    if (!Sky)
    {
        Sky = GetWorld()->SpawnActor<ASkyLight>(FVector::ZeroVector, FRotator::ZeroRotator);
        if (Sky) Sky->Tags.AddUnique(TEXT("RuntimeAtmosphereManaged"));
    }
    if (Sky && Sky->GetLightComponent())
    {
        Sky->GetLightComponent()->SetMobility(EComponentMobility::Movable);
        Sky->GetLightComponent()->SetIntensity(SkyIntensity);
        Sky->GetLightComponent()->SetLightColor(SkyColor);
        Sky->GetLightComponent()->RecaptureSky();
    }

    AExponentialHeightFog* Fog = nullptr;
    for (TActorIterator<AExponentialHeightFog> It(GetWorld()); It; ++It)
    {
        if (It->ActorHasTag(TEXT("RuntimeAtmosphereManaged")))
        {
            Fog = *It;
            break;
        }
    }
    if (!Fog)
    {
        Fog = GetWorld()->SpawnActor<AExponentialHeightFog>(FVector::ZeroVector, FRotator::ZeroRotator);
        if (Fog) Fog->Tags.AddUnique(TEXT("RuntimeAtmosphereManaged"));
    }
    if (Fog && Fog->GetComponent())
    {
        Fog->GetComponent()->SetMobility(EComponentMobility::Movable);
        Fog->GetComponent()->SetFogDensity(FogDensity);
        Fog->GetComponent()->SetFogHeightFalloff(FogHeightFalloff);
        Fog->GetComponent()->SetFogInscatteringColor(FogColor);
    }
}

AStaticMeshActor* AFellowshipChapterWorldBuilder::SpawnShape(
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

void AFellowshipChapterWorldBuilder::SpawnLabel(const FString& Text, const FVector& Location, const FLinearColor& Color)
{
    if (!FellowshipVisual::ShowPrototypeWorldLabels)
    {
        return;
    }

    if (!GetWorld())
    {
        return;
    }

    ATextRenderActor* Label = GetWorld()->SpawnActor<ATextRenderActor>(Location, FRotator(0.0f, 180.0f, 0.0f));
    if (Label && Label->GetTextRender())
    {
        Label->Tags.AddUnique(TEXT("RuntimePrototypeGenerated"));
        Label->GetTextRender()->SetText(FText::FromString(Text));
        Label->GetTextRender()->SetHorizontalAlignment(EHorizTextAligment::EHTA_Center);
        Label->GetTextRender()->SetWorldSize(40.0f);
        Label->GetTextRender()->SetTextRenderColor(Color.ToFColor(true));
    }
}

void AFellowshipChapterWorldBuilder::SpawnTree(const FVector& Location, float Scale)
{
    SpawnShape(CylinderMesh, Location + FVector(0.0f, 0.0f, 95.0f * Scale), FVector(0.14f, 0.14f, 0.95f) * Scale,
        FLinearColor(0.18f, 0.09f, 0.04f), FRotator::ZeroRotator, true);
    SpawnShape(SphereMesh, Location + FVector(0.0f, 0.0f, 220.0f * Scale), FVector(0.95f, 0.95f, 0.78f) * Scale,
        FLinearColor(0.09f, 0.26f, 0.08f), FRotator::ZeroRotator, false);
}

AShireNPC* AFellowshipChapterWorldBuilder::SpawnNPC(
    const FString& Name,
    const FVector& Location,
    const FRotator& Rotation,
    FName QuestId,
    int32 RequiredStage,
    int32 StageAfter,
    const FString& Line,
    FName NextQuestId,
    int32 NextQuestStage,
    bool bFollow)
{
    if (!GetWorld())
    {
        return nullptr;
    }

    AShireNPC* NPC = GetWorld()->SpawnActor<AShireNPC>(Location, Rotation);
    if (!NPC)
    {
        return nullptr;
    }

    NPC->DisplayName = FText::FromString(Name);
    NPC->DialogueLines = { FText::FromString(Line) };
    NPC->QuestId = QuestId;
    NPC->RequiredQuestStage = RequiredStage;
    NPC->QuestStageAfterInteraction = StageAfter;
    NPC->NextQuestId = NextQuestId;
    NPC->NextQuestStage = NextQuestStage;
    NPC->bFollowPlayerAfterInteraction = bFollow;
    return NPC;
}

AShireNPC* AFellowshipChapterWorldBuilder::SpawnTravelCompanion(
    const FString& Name,
    const FVector& Location,
    const FString& Line,
    FName StopFollowingStoryBeat)
{
    AShireNPC* Companion = SpawnNPC(
        Name,
        Location,
        FRotator(0.0f, 0.0f, 0.0f),
        NAME_None,
        0,
        -1,
        Line,
        NAME_None,
        0,
        true);

    if (Companion)
    {
        Companion->StopFollowingStoryBeat = StopFollowingStoryBeat;
    }
    return Companion;
}


AFellowshipEnemyPrototype* AFellowshipChapterWorldBuilder::SpawnEnemy(
    EFellowshipEnemyType Type,
    const FVector& Location,
    const FRotator& Rotation,
    FName RequiredQuestId,
    int32 RequiredMinStage)
{
    if (!GetWorld())
    {
        return nullptr;
    }

    AFellowshipEnemyPrototype* Enemy =
        GetWorld()->SpawnActor<AFellowshipEnemyPrototype>(Location, Rotation);
    if (Enemy)
    {
        Enemy->ConfigureEnemy(Type, RequiredQuestId, RequiredMinStage);
    }
    return Enemy;
}

void AFellowshipChapterWorldBuilder::SpawnQuestTrigger(
    const FVector& Location,
    FName QuestId,
    int32 RequiredStage,
    int32 StageAfter,
    const FString& Message,
    FName StoryBeatId,
    FName NextQuestId,
    int32 NextQuestStage,
    FName NextChapterId,
    FName NextChapterQuestId,
    int32 NextChapterQuestStage)
{
    if (!GetWorld())
    {
        return;
    }

    AShireQuestTrigger* Trigger = GetWorld()->SpawnActor<AShireQuestTrigger>(Location, FRotator::ZeroRotator);
    if (!Trigger)
    {
        return;
    }

    Trigger->QuestId = QuestId;
    Trigger->RequiredStage = RequiredStage;
    Trigger->StageAfterTrigger = StageAfter;
    Trigger->ObjectiveMessage = FText::FromString(Message);
    Trigger->StoryBeatId = StoryBeatId;
    Trigger->NextQuestId = NextQuestId;
    Trigger->NextQuestStage = NextQuestStage;
    Trigger->NextChapterId = NextChapterId;
    Trigger->NextChapterQuestId = NextChapterQuestId;
    Trigger->NextChapterQuestStage = NextChapterQuestStage;
}


void AFellowshipChapterWorldBuilder::EnsureProductionMeshes()
{
    if (bProductionMeshesLoaded)
    {
        return;
    }
    bProductionMeshesLoaded = true;

    WeathertopArchMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Weathertop/SM_WeathertopRuinedArch.SM_WeathertopRuinedArch"));
    WeathertopPillarMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Weathertop/SM_WeathertopBrokenPillar.SM_WeathertopBrokenPillar"));
    WeathertopCampRingMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Weathertop/SM_WeathertopCampRing.SM_WeathertopCampRing"));

    RivendellPavilionMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Rivendell/SM_RivendellPavilion.SM_RivendellPavilion"));
    RivendellArchMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Rivendell/SM_RivendellArch.SM_RivendellArch"));
    RivendellBridgeMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Rivendell/SM_RivendellBridge.SM_RivendellBridge"));
    RivendellLanternMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Rivendell/SM_RivendellLantern.SM_RivendellLantern"));

    RoadCampTentMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Road/SM_RoadCampTent.SM_RoadCampTent"));
    RoadSupplyRackMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Road/SM_RoadSupplyRack.SM_RoadSupplyRack"));
    CaradhrasRockMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Road/SM_CaradhrasRock.SM_CaradhrasRock"));

    MoriaPillarMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Moria/SM_MoriaPillar.SM_MoriaPillar"));
    MoriaDoorMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Moria/SM_MoriaDoor.SM_MoriaDoor"));
    MoriaBrazierMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Moria/SM_MoriaBrazier.SM_MoriaBrazier"));
    MoriaBridgeMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Moria/SM_MoriaBridgeSegment.SM_MoriaBridgeSegment"));

    LorienTalanMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Lothlorien/SM_LorienTalan.SM_LorienTalan"));
    LorienLanternMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Lothlorien/SM_LorienLantern.SM_LorienLantern"));
    LorienMirrorMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Lothlorien/SM_LorienMirror.SM_LorienMirror"));

    AnduinBoatMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Anduin/SM_AnduinBoat.SM_AnduinBoat"));
    AmonHenStairMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Anduin/SM_AmonHenStair.SM_AmonHenStair"));
    AmonHenRuinMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Anduin/SM_AmonHenRuin.SM_AmonHenRuin"));
    ArgonathSentinelMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Anduin/SM_ArgonathSentinel.SM_ArgonathSentinel"));

    CommonMountainRidgeMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Common/SM_CommonMountainRidge.SM_CommonMountainRidge"));
    CommonCliffWallMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Common/SM_CommonCliffWall.SM_CommonCliffWall"));
    CommonTerracedHillMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Common/SM_CommonTerracedHill.SM_CommonTerracedHill"));
    CommonRiverBankMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Common/SM_CommonRiverBank.SM_CommonRiverBank"));
    CommonBoulderClusterMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Common/SM_CommonBoulderCluster.SM_CommonBoulderCluster"));
    CommonPineTreeMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Common/SM_CommonPineTree.SM_CommonPineTree"));
    CommonBroadleafTreeMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Common/SM_CommonBroadleafTree.SM_CommonBroadleafTree"));
    CommonGoldenTreeMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Common/SM_CommonGoldenTree.SM_CommonGoldenTree"));
    CommonFallenLogMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Common/SM_CommonFallenLog.SM_CommonFallenLog"));
    CommonDryStoneWallMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Common/SM_CommonDryStoneWall.SM_CommonDryStoneWall"));
    CommonPathMarkerMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Common/SM_CommonPathMarker.SM_CommonPathMarker"));
    CommonVillageFenceMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Common/SM_CommonVillageFence.SM_CommonVillageFence"));
    CommonWoodPileMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Common/SM_CommonWoodPile.SM_CommonWoodPile"));
    CommonFernClumpMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Common/SM_CommonFernClump.SM_CommonFernClump"));
    CommonReedClusterMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Common/SM_CommonReedCluster.SM_CommonReedCluster"));
    CommonRuinSlabMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Common/SM_CommonRuinSlab.SM_CommonRuinSlab"));
    CommonFootbridgeMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/Production/World/Common/SM_CommonFootbridge.SM_CommonFootbridge"));
}

void AFellowshipChapterWorldBuilder::SpawnProductionChapterLayer(FName ChapterId)
{
    auto SpawnProd = [this](UStaticMesh* Mesh, const FVector& Location, const FVector& Scale,
        const FRotator& Rotation = FRotator::ZeroRotator, bool bCollision = true)
    {
        if (Mesh)
        {
            SpawnShape(Mesh, Location, Scale, FLinearColor::White, Rotation, bCollision);
        }
    };

    // CP49 common production terrain gives each chapter a readable silhouette without
    // replacing the established story/quest topology. These are mostly non-colliding
    // boundary/vista forms so the current traversal remains stable.
    auto SpawnTerrainBand = [&SpawnProd](
        UStaticMesh* Mesh,
        const FVector& Start,
        const FVector& Step,
        int32 Count,
        const FVector& Scale,
        float YawStep)
    {
        for (int32 Index = 0; Index < Count; ++Index)
        {
            SpawnProd(Mesh, Start + Step * static_cast<float>(Index), Scale,
                FRotator(0.0f, YawStep * Index, 0.0f), false);
        }
    };

    auto SpawnScatter = [&SpawnProd](
        UStaticMesh* Mesh,
        const FVector& Center,
        int32 Count,
        const FVector& Radius,
        const FVector& BaseScale,
        float YawStep,
        float HeightJitter = 0.0f)
    {
        if (!Mesh || Count <= 0)
        {
            return;
        }

        for (int32 Index = 0; Index < Count; ++Index)
        {
            const float Angle = FMath::DegreesToRadians(
                FMath::Fmod(Index * 137.507764f + YawStep * 0.37f, 360.0f));
            const float Ring = 0.35f + 0.65f * (static_cast<float>((Index * 7) % Count) / FMath::Max(1, Count - 1));
            const FVector Offset(
                FMath::Cos(Angle) * Radius.X * Ring,
                FMath::Sin(Angle) * Radius.Y * Ring,
                HeightJitter * FMath::Sin(Angle * 1.7f));
            const float ScaleJitter = 0.82f + 0.08f * (Index % 5);
            SpawnProd(
                Mesh,
                Center + Offset,
                BaseScale * ScaleJitter,
                FRotator(0.0f, FMath::Fmod(Index * YawStep, 360.0f), 0.0f),
                false);
        }
    };

    if (ChapterId == TEXT("P1C03"))
    {
        SpawnTerrainBand(CommonTerracedHillMesh, FVector(-2200,-1450,-150), FVector(650,0,15), 8,
            FVector(1.85f,1.45f,1.15f), 9.0f);
        SpawnTerrainBand(CommonMountainRidgeMesh, FVector(-1800,1700,-120), FVector(850,0,25), 6,
            FVector(2.2f,1.5f,1.55f), -7.0f);
        SpawnProd(CommonBoulderClusterMesh, FVector(650,-850,10), FVector(1.15f), FRotator(0,31,0), false);
        SpawnProd(WeathertopArchMesh, FVector(1350, 0, 405), FVector(0.92f), FRotator(0, 8, 0), true);
        for (int32 I = 0; I < 6; ++I)
        {
            const float A = FMath::DegreesToRadians(I * 60.0f);
            SpawnProd(WeathertopPillarMesh,
                FVector(1350 + FMath::Cos(A) * 245.0f, FMath::Sin(A) * 245.0f, 390.0f),
                FVector(0.72f + 0.05f * (I % 2)), FRotator(0, I * 27.0f, I % 2 ? 7.0f : -4.0f), true);
        }
        SpawnProd(WeathertopCampRingMesh, FVector(1250, -260, 420), FVector(0.72f), FRotator::ZeroRotator, false);
        SpawnScatter(CommonPineTreeMesh, FVector(-600,-100,0), 18, FVector(2200,1300,0), FVector(0.75f), 31.0f, 18.0f);
        SpawnScatter(CommonFallenLogMesh, FVector(-300,-120,0), 6, FVector(1700,900,0), FVector(0.72f), 53.0f, 6.0f);
        SpawnScatter(CommonFernClumpMesh, FVector(0,0,0), 26, FVector(2100,1200,0), FVector(0.62f), 29.0f, 4.0f);
        SpawnProd(CommonPathMarkerMesh, FVector(-950,220,0), FVector(0.78f), FRotator(0,24,0), false);
        SpawnScatter(CommonBoulderClusterMesh, FVector(450,-120,0), 8, FVector(1750,950,0), FVector(0.70f), 41.0f, 7.0f);
        SpawnScatter(CommonDryStoneWallMesh, FVector(-900,-820,0), 6, FVector(1300,360,0), FVector(0.62f), 67.0f, 2.0f);
        SpawnScatter(CommonWoodPileMesh, FVector(1100,-260,390), 4, FVector(520,340,0), FVector(0.58f), 83.0f, 2.0f);
    }
    else if (ChapterId == TEXT("P1C04"))
    {
        SpawnTerrainBand(CommonCliffWallMesh, FVector(-2200,-1700,-80), FVector(800,0,40), 7,
            FVector(2.5f,1.4f,2.0f), 4.0f);
        SpawnTerrainBand(CommonCliffWallMesh, FVector(-2100,1750,-70), FVector(820,0,35), 7,
            FVector(2.4f,1.4f,1.9f), -4.0f);
        SpawnProd(CommonRiverBankMesh, FVector(250,760,-30), FVector(2.6f,1.25f,1.0f), FRotator::ZeroRotator, false);
        const FVector Pavilions[] = { FVector(-850,-420,0), FVector(150,-520,0), FVector(1080,-360,0) };
        for (int32 I = 0; I < UE_ARRAY_COUNT(Pavilions); ++I)
        {
            SpawnProd(RivendellPavilionMesh, Pavilions[I], FVector(0.78f + 0.05f * I),
                FRotator(0, I * 12.0f - 8.0f, 0), true);
        }
        SpawnProd(RivendellBridgeMesh, FVector(200,720,15), FVector(0.82f), FRotator::ZeroRotator, true);
        const FVector Arches[] = { FVector(-1350,120,0), FVector(-450,160,0), FVector(650,160,0), FVector(1450,120,0) };
        for (int32 I = 0; I < UE_ARRAY_COUNT(Arches); ++I)
            SpawnProd(RivendellArchMesh, Arches[I], FVector(0.82f), FRotator(0,0,0), true);
        const FVector Lamps[] = { FVector(-1000,-200,0), FVector(-250,-250,0), FVector(500,-220,0), FVector(1200,-180,0) };
        for (const FVector& P : Lamps) SpawnProd(RivendellLanternMesh, P, FVector(0.78f), FRotator::ZeroRotator, false);
        SpawnScatter(CommonBroadleafTreeMesh, FVector(100,0,0), 30, FVector(2500,1450,0), FVector(0.82f), 23.0f, 8.0f);
        SpawnScatter(CommonFernClumpMesh, FVector(250,100,0), 42, FVector(2400,1300,0), FVector(0.70f), 17.0f, 4.0f);
        SpawnScatter(CommonReedClusterMesh, FVector(200,720,-10), 20, FVector(1350,260,0), FVector(0.72f), 19.0f, 2.0f);
        SpawnProd(CommonFootbridgeMesh, FVector(-650,690,20), FVector(0.72f), FRotator(0,4,0), true);
        SpawnScatter(CommonFallenLogMesh, FVector(200,-250,0), 7, FVector(1900,900,0), FVector(0.62f), 59.0f, 4.0f);
        SpawnScatter(CommonPathMarkerMesh, FVector(-100,120,0), 8, FVector(2100,650,0), FVector(0.58f), 47.0f, 2.0f);
        SpawnScatter(CommonBoulderClusterMesh, FVector(300,500,0), 6, FVector(2100,900,0), FVector(0.62f), 71.0f, 6.0f);
    }
    else if (ChapterId == TEXT("P1C05"))
    {
        SpawnTerrainBand(CommonMountainRidgeMesh, FVector(-1900,-1900,-140), FVector(900,0,75), 7,
            FVector(2.7f,1.65f,2.2f), 6.0f);
        SpawnTerrainBand(CommonMountainRidgeMesh, FVector(-1700,1900,-130), FVector(900,0,65), 7,
            FVector(2.6f,1.6f,2.1f), -5.0f);
        SpawnProd(CommonBoulderClusterMesh, FVector(400,-720,20), FVector(1.45f), FRotator(0,22,0), false);
        SpawnProd(CommonBoulderClusterMesh, FVector(1400,760,30), FVector(1.65f), FRotator(0,-18,0), false);
        const FVector Tents[] = { FVector(-1550,-360,0), FVector(-1200,360,0), FVector(-820,-300,0) };
        for (int32 I = 0; I < UE_ARRAY_COUNT(Tents); ++I)
            SpawnProd(RoadCampTentMesh, Tents[I], FVector(0.78f), FRotator(0, I * 18.0f - 12.0f,0), true);
        SpawnProd(RoadSupplyRackMesh, FVector(-1080,120,0), FVector(0.82f), FRotator::ZeroRotator, true);
        for (int32 I = 0; I < 9; ++I)
            SpawnProd(CaradhrasRockMesh, FVector(180 + I * 270.0f, (I % 2 ? 610.0f : -590.0f), 40.0f),
                FVector(0.65f + 0.08f * (I % 3)), FRotator(I * 5.0f, I * 31.0f, 0), true);
        SpawnScatter(CommonPineTreeMesh, FVector(-700,0,0), 18, FVector(2200,1200,0), FVector(0.68f), 23.0f, 10.0f);
        SpawnScatter(CommonFallenLogMesh, FVector(-900,0,0), 6, FVector(1500,780,0), FVector(0.62f), 61.0f, 5.0f);
        SpawnScatter(CommonDryStoneWallMesh, FVector(-1200,0,0), 8, FVector(1000,520,0), FVector(0.60f), 43.0f, 2.0f);
        SpawnScatter(CommonPathMarkerMesh, FVector(-300,0,0), 8, FVector(2200,450,0), FVector(0.62f), 37.0f, 2.0f);
        SpawnScatter(CommonWoodPileMesh, FVector(-1200,80,0), 5, FVector(720,420,0), FVector(0.56f), 73.0f, 2.0f);
    }
    else if (ChapterId == TEXT("P1C06"))
    {
        SpawnTerrainBand(CommonCliffWallMesh, FVector(-2300,-1350,-120), FVector(780,0,0), 8,
            FVector(2.2f,1.25f,2.7f), 0.0f);
        SpawnTerrainBand(CommonCliffWallMesh, FVector(-2300,1350,-120), FVector(780,0,0), 8,
            FVector(2.2f,1.25f,2.7f), 180.0f);
        for (int32 I = 0; I < 14; ++I)
        {
            const float X = -1900.0f + (I % 7) * 600.0f;
            const float Y = I < 7 ? -760.0f : 760.0f;
            SpawnProd(MoriaPillarMesh, FVector(X,Y,0), FVector(0.88f), FRotator::ZeroRotator, true);
        }
        SpawnProd(MoriaDoorMesh, FVector(-2200,0,0), FVector(0.92f), FRotator(0,90,0), true);
        const FVector Braziers[] = { FVector(-1200,-400,0), FVector(-450,420,0), FVector(350,-420,0), FVector(1150,420,0) };
        for (const FVector& P : Braziers) SpawnProd(MoriaBrazierMesh, P, FVector(0.82f), FRotator::ZeroRotator, false);
        SpawnProd(MoriaBridgeMesh, FVector(2450,0,40), FVector(0.92f), FRotator::ZeroRotator, true);
        SpawnScatter(CommonRuinSlabMesh, FVector(-200,0,0), 18, FVector(2300,1050,0), FVector(0.78f), 37.0f, 2.0f);
        SpawnScatter(CommonBoulderClusterMesh, FVector(300,0,0), 14, FVector(2500,1150,0), FVector(0.85f), 31.0f, 6.0f);
        SpawnScatter(CommonRuinSlabMesh, FVector(900,0,0), 12, FVector(2100,900,0), FVector(0.62f), 53.0f, 2.0f);
    }
    else if (ChapterId == TEXT("P1C07"))
    {
        SpawnTerrainBand(CommonTerracedHillMesh, FVector(-2100,-1550,-145), FVector(800,0,20), 7,
            FVector(1.9f,1.5f,1.25f), 11.0f);
        SpawnTerrainBand(CommonTerracedHillMesh, FVector(-1900,1600,-140), FVector(800,0,15), 7,
            FVector(1.8f,1.45f,1.2f), -9.0f);
        const FVector Talans[] = { FVector(-1450,-720,0), FVector(-750,720,0), FVector(-50,-720,0), FVector(650,720,0), FVector(1350,-720,0) };
        for (int32 I = 0; I < UE_ARRAY_COUNT(Talans); ++I)
            SpawnProd(LorienTalanMesh, Talans[I], FVector(0.78f + 0.04f * (I % 2)), FRotator(0,I*19.0f,0), true);
        const FVector Lamps[] = { FVector(-1100,-250,0), FVector(-500,280,0), FVector(100,-260,0), FVector(700,270,0), FVector(1300,-220,0) };
        for (const FVector& P : Lamps) SpawnProd(LorienLanternMesh, P, FVector(0.82f), FRotator::ZeroRotator, false);
        SpawnProd(LorienMirrorMesh, FVector(1000,420,0), FVector(0.90f), FRotator::ZeroRotator, true);
        SpawnScatter(CommonGoldenTreeMesh, FVector(0,0,0), 34, FVector(2600,1550,0), FVector(0.92f), 19.0f, 12.0f);
        SpawnScatter(CommonFernClumpMesh, FVector(100,0,0), 48, FVector(2500,1450,0), FVector(0.72f), 13.0f, 4.0f);
        SpawnScatter(CommonFallenLogMesh, FVector(-100,150,0), 8, FVector(2100,1200,0), FVector(0.68f), 47.0f, 4.0f);
        SpawnScatter(CommonBroadleafTreeMesh, FVector(150,0,0), 14, FVector(2200,1300,0), FVector(0.72f), 31.0f, 8.0f);
        SpawnScatter(CommonFootbridgeMesh, FVector(-200,250,0), 3, FVector(1450,500,0), FVector(0.60f), 97.0f, 2.0f);
        SpawnScatter(CommonPathMarkerMesh, FVector(0,0,0), 7, FVector(1800,620,0), FVector(0.56f), 43.0f, 2.0f);
    }
    else if (ChapterId == TEXT("P1C08"))
    {
        SpawnTerrainBand(CommonCliffWallMesh, FVector(-2600,-1650,-110), FVector(760,0,30), 8,
            FVector(2.35f,1.3f,2.0f), 3.0f);
        SpawnTerrainBand(CommonCliffWallMesh, FVector(-2500,1650,-100), FVector(760,0,25), 8,
            FVector(2.3f,1.3f,1.95f), -3.0f);
        SpawnProd(CommonRiverBankMesh, FVector(-1250,-620,-25), FVector(3.1f,1.2f,1.0f), FRotator(0,0,0), false);
        SpawnProd(CommonRiverBankMesh, FVector(-1250,620,-25), FVector(3.1f,1.2f,1.0f), FRotator(0,180,0), false);
        const FVector Boats[] = { FVector(-1900,-120,0), FVector(-1500,130,0), FVector(-1080,-80,0) };
        for (int32 I = 0; I < UE_ARRAY_COUNT(Boats); ++I)
            SpawnProd(AnduinBoatMesh, Boats[I], FVector(0.82f), FRotator(0,I*3.0f,0), false);
        SpawnProd(ArgonathSentinelMesh, FVector(-450,-1150,0), FVector(1.65f), FRotator(0,8,0), true);
        SpawnProd(ArgonathSentinelMesh, FVector(-450,1150,0), FVector(1.65f), FRotator(0,172,0), true);
        SpawnProd(AmonHenStairMesh, FVector(1320,0,0), FVector(0.86f), FRotator(0,0,0), true);
        SpawnProd(AmonHenRuinMesh, FVector(1900,0,175), FVector(0.90f), FRotator(0,-6,0), true);
        SpawnScatter(CommonBroadleafTreeMesh, FVector(700,0,0), 24, FVector(2600,1450,0), FVector(0.88f), 21.0f, 10.0f);
        SpawnScatter(CommonPineTreeMesh, FVector(1000,0,0), 14, FVector(2200,1300,0), FVector(0.82f), 29.0f, 10.0f);
        SpawnScatter(CommonReedClusterMesh, FVector(-1500,0,-10), 28, FVector(1250,520,0), FVector(0.76f), 17.0f, 2.0f);
        SpawnScatter(CommonRuinSlabMesh, FVector(1600,0,0), 10, FVector(1100,800,0), FVector(0.74f), 43.0f, 3.0f);
        SpawnScatter(CommonFallenLogMesh, FVector(800,0,0), 7, FVector(2100,1100,0), FVector(0.66f), 47.0f, 4.0f);
        SpawnScatter(CommonFootbridgeMesh, FVector(-1050,0,0), 2, FVector(900,380,0), FVector(0.68f), 101.0f, 2.0f);
        SpawnScatter(CommonPathMarkerMesh, FVector(650,0,0), 8, FVector(2200,700,0), FVector(0.60f), 39.0f, 2.0f);
        SpawnScatter(CommonBoulderClusterMesh, FVector(1350,0,0), 8, FVector(1300,900,0), FVector(0.70f), 57.0f, 5.0f);
    }
}

void AFellowshipChapterWorldBuilder::BuildChapter(FName ChapterId)
{
    if (bBuilt || !GetWorld())
    {
        return;
    }

    bBuilt = true;
    EnsureProductionMeshes();
    ConfigureChapterAtmosphere(ChapterId);

    if (ChapterId == TEXT("P1C03"))
    {
        BuildWeathertop();
    }
    else if (ChapterId == TEXT("P1C04"))
    {
        BuildRivendell();
    }
    else if (ChapterId == TEXT("P1C05"))
    {
        BuildFellowshipRoad();
    }
    else if (ChapterId == TEXT("P1C06"))
    {
        BuildMoria();
    }
    else if (ChapterId == TEXT("P1C07"))
    {
        BuildLothlorien();
    }
    else if (ChapterId == TEXT("P1C08"))
    {
        BuildAnduinAmonHen();
    }

    SpawnProductionChapterLayer(ChapterId);
}

void AFellowshipChapterWorldBuilder::BuildWeathertop()
{
    SpawnShape(CubeMesh, FVector(0, 0, -70), FVector(38, 24, 0.7f), FLinearColor(0.12f, 0.14f, 0.09f));

    // Distant broken ridges hide the map edge and make the lone hill feel exposed.
    for (int32 I = 0; I < 9; ++I)
    {
        const float X = -2800.0f + I * 760.0f;
        const float Y = (I % 2 == 0 ? 1750.0f : -1750.0f);
        SpawnShape(SphereMesh, FVector(X, Y, -170.0f), FVector(4.8f, 3.2f, 2.2f + 0.25f * (I % 3)),
            FLinearColor(0.11f, 0.13f, 0.10f), FRotator::ZeroRotator, false);
    }

    // Midgewater-style wet ground and stepping islands keep the approach visually distinct.
    for (int32 I = 0; I < 6; ++I)
    {
        const float X = -1950.0f + I * 430.0f;
        const float Y = (I % 2 == 0 ? 280.0f : -340.0f);
        SpawnShape(CubeMesh, FVector(X, Y, -18.0f), FVector(1.9f, 1.25f, 0.045f),
            FLinearColor(0.055f, 0.16f, 0.17f), FRotator(0.0f, I * 11.0f, 0.0f), false);
        SpawnShape(SphereMesh, FVector(X + 120.0f, Y + 90.0f, 8.0f), FVector(0.52f, 0.38f, 0.14f),
            FLinearColor(0.18f, 0.19f, 0.14f), FRotator::ZeroRotator, true);
    }

    for (int32 I = 0; I < 10; ++I)
    {
        SpawnShape(CubeMesh, FVector(-2350.0f + I * 360.0f, 0.0f, 10.0f), FVector(2.2f, 0.75f, 0.1f),
            FLinearColor(0.24f, 0.20f, 0.14f));
    }

    // Wet lowlands / wilderness silhouettes.
    for (int32 I = 0; I < 8; ++I)
    {
        SpawnTree(FVector(-1850.0f + I * 330.0f, (I % 2 == 0 ? 560.0f : -520.0f), 0.0f), 0.75f);
    }

    // Reeds, low rocks and abandoned camp remains keep the marsh approach from feeling empty.
    for (int32 I = 0; I < 16; ++I)
    {
        const float X = -2050.0f + I * 210.0f;
        const float Y = (I % 3 - 1) * 420.0f;
        SpawnShape(CylinderMesh, FVector(X, Y, 24.0f), FVector(0.025f, 0.025f, 0.24f + 0.03f * (I % 4)),
            FLinearColor(0.28f, 0.31f, 0.12f), FRotator(0.0f, I * 19.0f, 0.0f), false);
    }
    for (int32 I = 0; I < 9; ++I)
    {
        SpawnShape(SphereMesh, FVector(-1450.0f + I * 320.0f, (I % 2 == 0 ? 680.0f : -650.0f), 24.0f),
            FVector(0.38f + 0.06f * (I % 3), 0.30f, 0.22f),
            FLinearColor(0.22f, 0.22f, 0.18f), FRotator(0.0f, I * 27.0f, 0.0f), true);
    }
    // Small fire ring / bedroll proxies near the summit camp.
    for (int32 I = 0; I < 7; ++I)
    {
        const float Angle = I * (360.0f / 7.0f);
        const FVector Offset(
            FMath::Cos(FMath::DegreesToRadians(Angle)) * 82.0f,
            FMath::Sin(FMath::DegreesToRadians(Angle)) * 82.0f,
            0.0f);
        SpawnShape(SphereMesh, FVector(1250, -260, 425) + Offset,
            FVector(0.15f, 0.12f, 0.10f), FLinearColor(0.25f, 0.22f, 0.18f), FRotator::ZeroRotator, false);
    }
    SpawnShape(CylinderMesh, FVector(1250, -260, 438), FVector(0.18f, 0.18f, 0.035f),
        FLinearColor(0.56f, 0.20f, 0.05f), FRotator::ZeroRotator, false);

    const FVector WeathertopBirds[] = {
        FVector(-1400, -520, 520), FVector(-200, 620, 580), FVector(1350, -740, 650)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(WeathertopBirds); ++Index)
    {
        AShireAmbientNPC* Bird = GetWorld()->SpawnActor<AShireAmbientNPC>(WeathertopBirds[Index], FRotator::ZeroRotator);
        if (!Bird) continue;
        Bird->RoutineRole = TEXT("Bird");
        Bird->RoutinePointA = WeathertopBirds[Index];
        Bird->RoutinePointB = WeathertopBirds[Index] + FVector(620.0f, Index % 2 == 0 ? 420.0f : -420.0f, 90.0f);
        Bird->WalkSpeed = 150.0f + 12.0f * Index;
        Bird->MinWait = 0.0f;
        Bird->MaxWait = 0.0f;
    }

    // Weathertop hill and broken crown.
    SpawnShape(CylinderMesh, FVector(1350, 0, 130), FVector(5.2f, 5.2f, 1.3f),
        FLinearColor(0.19f, 0.18f, 0.14f), FRotator::ZeroRotator, true);
    SpawnShape(CylinderMesh, FVector(1350, 0, 330), FVector(3.4f, 3.4f, 0.7f),
        FLinearColor(0.22f, 0.21f, 0.18f), FRotator::ZeroRotator, true);
    for (int32 I = 0; I < 7; ++I)
    {
        const float Angle = (360.0f / 7.0f) * I;
        const FVector Offset(FMath::Cos(FMath::DegreesToRadians(Angle)) * 220.0f,
            FMath::Sin(FMath::DegreesToRadians(Angle)) * 220.0f, 0.0f);
        SpawnShape(CubeMesh, FVector(1350, 0, 470) + Offset, FVector(0.35f, 0.35f, 1.1f),
            FLinearColor(0.26f, 0.25f, 0.23f), FRotator(0, Angle, 0), true);
    }
    SpawnLabel(TEXT("Weathertop"), FVector(1350, 0, 690), FLinearColor(0.85f, 0.82f, 0.70f));

    SpawnTravelCompanion(TEXT("Sam"), FVector(-2020, -180, 70),
        TEXT("I do not like this country, Mr. Frodo, but I am staying close."));
    SpawnTravelCompanion(TEXT("Merry"), FVector(-2110, 120, 70),
        TEXT("We have come too far to lose each other in a marsh."));
    SpawnTravelCompanion(TEXT("Pippin"), FVector(-2180, -20, 70),
        TEXT("I would prefer a dry road, but I suppose we have run out of those."));

    SpawnQuestTrigger(FVector(-1850, 0, 90), TEXT("RoadToWeathertop"), 0, 1,
        TEXT("The road gives way to wet country. Strider leads you off the obvious path."), TEXT("MidgewaterRoad"));
    SpawnQuestTrigger(FVector(-250, 0, 90), TEXT("RoadToWeathertop"), 1, 2,
        TEXT("The ruined hill is ahead. Keep close to the Ranger."), TEXT("WeathertopReveal"));

    SpawnNPC(TEXT("Strider"), FVector(760, -160, 70), FRotator(0, 180, 0), TEXT("RoadToWeathertop"), 2, 2,
        TEXT("We will rest only briefly. This place can be seen from far away."), TEXT("WeathertopAttack"), 0, true);

    SpawnQuestTrigger(FVector(1280, 0, 400), TEXT("WeathertopAttack"), 0, 1,
        TEXT("Night settles over the ruins. Keep the fire small and watch the dark."), TEXT("WeathertopCamp"));

    const FVector RiderLocations[] = {
        FVector(1580, -420, 70), FVector(1730, -220, 70), FVector(1780, 0, 70), FVector(1730, 220, 70), FVector(1580, 420, 70)
    };
    for (const FVector& P : RiderLocations)
    {
        ABlackRiderPrototype* Rider = GetWorld()->SpawnActor<ABlackRiderPrototype>(P, FRotator::ZeroRotator);
        if (Rider)
        {
            Rider->PatrolA = P;
            Rider->PatrolB = P + FVector(-260.0f, 0.0f, 0.0f);
            Rider->DetectionRadius = 520.0f;
            Rider->CrouchedDetectionRadius = 260.0f;
        }
    }

    SpawnQuestTrigger(FVector(1470, 0, 430), TEXT("WeathertopAttack"), 1, 2,
        TEXT("The Riders close in. Stay near your companions and survive the assault."), TEXT("NazgulCloseIn"));
    SpawnQuestTrigger(FVector(1190, -140, 430), TEXT("WeathertopAttack"), 2, 3,
        TEXT("Frodo is wounded. The company must move east without delay."), TEXT("MorgulWound"), TEXT("FlightToFord"), 0);

    SpawnNPC(TEXT("Arwen"), FVector(2200, -160, 70), FRotator(0, 180, 0), TEXT("FlightToFord"), 0, 1,
        TEXT("There is no time to lose. I can carry him faster than the road will allow."));
    // Ford approach: visible water, banks and scattered stones make the chase destination readable.
    SpawnShape(CubeMesh, FVector(3000, 0, -18), FVector(5.6f, 13.0f, 0.12f),
        FLinearColor(0.055f, 0.23f, 0.38f), FRotator::ZeroRotator, false);
    for (int32 I = 0; I < 7; ++I)
    {
        SpawnShape(SphereMesh, FVector(2760.0f + I * 85.0f, (I % 2 == 0 ? 110.0f : -90.0f), 8.0f),
            FVector(0.34f, 0.28f, 0.12f), FLinearColor(0.34f, 0.35f, 0.31f), FRotator::ZeroRotator, true);
    }

    SpawnQuestTrigger(FVector(2750, 0, 90), TEXT("FlightToFord"), 1, 2,
        TEXT("The river crossing is ahead. Reach the far bank before the Riders."), TEXT("FordChase"));
    SpawnQuestTrigger(FVector(3200, 0, 90), TEXT("FlightToFord"), 2, 2,
        TEXT("The pursuit breaks at the river. Rivendell lies beyond."), TEXT("FordEscape"), NAME_None, 0,
        TEXT("P1C04"), TEXT("RivendellRecovery"), 0);
}

void AFellowshipChapterWorldBuilder::BuildRivendell()
{
    SpawnShape(CubeMesh, FVector(0, 0, -80), FVector(38, 30, 0.8f), FLinearColor(0.12f, 0.22f, 0.14f));

    // High valley walls and layered green terraces create enclosure without expensive landscape assets.
    for (int32 I = 0; I < 8; ++I)
    {
        const float X = -2400.0f + I * 720.0f;
        SpawnShape(SphereMesh, FVector(X, -2100.0f, -140.0f), FVector(5.2f, 3.0f, 3.0f + 0.25f * (I % 3)),
            FLinearColor(0.16f, 0.25f, 0.17f), FRotator::ZeroRotator, false);
        SpawnShape(SphereMesh, FVector(X + 220.0f, 2150.0f, -160.0f), FVector(5.0f, 3.2f, 2.8f + 0.20f * (I % 2)),
            FLinearColor(0.14f, 0.23f, 0.16f), FRotator::ZeroRotator, false);
    }

    // Waterfall ribbons from the valley walls into the river.
    const FVector Waterfalls[] = {
        FVector(-1800, 1720, 310), FVector(-200, -1760, 360), FVector(1520, 1760, 330)
    };
    for (const FVector& P : Waterfalls)
    {
        SpawnShape(CubeMesh, P, FVector(0.22f, 0.10f, 3.2f),
            FLinearColor(0.62f, 0.78f, 0.86f), FRotator::ZeroRotator, false);
        SpawnShape(CubeMesh, P - FVector(0, 0, 300), FVector(1.5f, 0.75f, 0.04f),
            FLinearColor(0.08f, 0.30f, 0.42f), FRotator::ZeroRotator, false);
    }

    // Valley terraces, water and layered gardens.
    SpawnShape(CubeMesh, FVector(0, 720, -20), FVector(34, 2.0f, 0.2f), FLinearColor(0.06f, 0.28f, 0.42f), FRotator::ZeroRotator, false);
    for (int32 I = 0; I < 14; ++I)
    {
        SpawnTree(FVector(-2200.0f + (I % 7) * 700.0f, (I < 7 ? -760.0f : 760.0f), 0.0f), 0.88f + 0.06f * (I % 3));
    }

    // Garden paths, arcades and resting places make the valley read as an inhabited refuge.
    for (int32 I = 0; I < 8; ++I)
    {
        const float X = -1500.0f + I * 390.0f;
        SpawnShape(CylinderMesh, FVector(X, -360.0f, 115.0f), FVector(0.16f, 0.16f, 1.15f),
            FLinearColor(0.58f, 0.54f, 0.44f), FRotator::ZeroRotator, true);
        SpawnShape(CylinderMesh, FVector(X, 360.0f, 115.0f), FVector(0.16f, 0.16f, 1.15f),
            FLinearColor(0.58f, 0.54f, 0.44f), FRotator::ZeroRotator, true);
    }
    for (int32 I = 0; I < 6; ++I)
    {
        SpawnShape(CubeMesh, FVector(-1280.0f + I * 500.0f, (I % 2 == 0 ? -560.0f : 560.0f), 30.0f),
            FVector(0.70f, 0.20f, 0.12f), FLinearColor(0.32f, 0.24f, 0.14f),
            FRotator(0.0f, I % 2 == 0 ? 8.0f : -8.0f, 0.0f), true);
    }
    for (int32 I = 0; I < 7; ++I)
    {
        const float X = -1350.0f + I * 450.0f;
        SpawnShape(SphereMesh, FVector(X, 520.0f, 34.0f), FVector(0.28f, 0.22f, 0.18f),
            I % 2 == 0 ? FLinearColor(0.48f, 0.18f, 0.22f) : FLinearColor(0.72f, 0.62f, 0.28f),
            FRotator::ZeroRotator, false);
    }

    const FVector RivendellBirds[] = {
        FVector(-1600, -880, 620), FVector(-700, 900, 680), FVector(420, -860, 640), FVector(1450, 880, 700)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(RivendellBirds); ++Index)
    {
        AShireAmbientNPC* Bird = GetWorld()->SpawnActor<AShireAmbientNPC>(RivendellBirds[Index], FRotator::ZeroRotator);
        if (!Bird) continue;
        Bird->RoutineRole = TEXT("Bird");
        Bird->RoutinePointA = RivendellBirds[Index];
        Bird->RoutinePointB = RivendellBirds[Index] + FVector(540.0f, Index % 2 == 0 ? 390.0f : -390.0f, 75.0f);
        Bird->WalkSpeed = 132.0f + 8.0f * Index;
        Bird->MinWait = 0.0f;
        Bird->MaxWait = 0.0f;
    }

    // House of Elrond, bridges and council terrace.
    SpawnShape(CubeMesh, FVector(-650, 0, 95), FVector(4.2f, 3.2f, 0.95f), FLinearColor(0.62f, 0.55f, 0.42f));
    SpawnShape(ConeMesh, FVector(-650, 0, 240), FVector(4.6f, 3.6f, 0.65f), FLinearColor(0.32f, 0.24f, 0.16f), FRotator::ZeroRotator, false);
    SpawnShape(CubeMesh, FVector(450, 0, 25), FVector(4.5f, 0.45f, 0.18f), FLinearColor(0.48f, 0.42f, 0.32f));
    SpawnShape(CylinderMesh, FVector(1250, 0, 35), FVector(3.2f, 3.2f, 0.35f), FLinearColor(0.56f, 0.52f, 0.44f));
    SpawnShape(CubeMesh, FVector(-1450, 380, 35), FVector(2.3f, 1.6f, 0.35f), FLinearColor(0.48f, 0.40f, 0.30f));
    SpawnShape(CylinderMesh, FVector(-1550, 470, 170), FVector(0.35f, 0.35f, 1.7f), FLinearColor(0.26f, 0.17f, 0.10f));
    SpawnLabel(TEXT("Rivendell"), FVector(-650, 0, 420), FLinearColor(0.92f, 0.88f, 0.72f));
    SpawnLabel(TEXT("Council Terrace"), FVector(1250, 0, 220), FLinearColor::White);
    SpawnLabel(TEXT("Bilbo's Garden"), FVector(-1450, 380, 240), FLinearColor(0.86f, 0.83f, 0.68f));

    const FVector RivendellResidents[] = {
        FVector(-1180, -520, 70), FVector(-980, 520, 70), FVector(-320, 620, 70),
        FVector(280, -620, 70), FVector(760, 520, 70), FVector(1520, -430, 70)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(RivendellResidents); ++Index)
    {
        AShireAmbientNPC* Resident = GetWorld()->SpawnActor<AShireAmbientNPC>(
            RivendellResidents[Index], FRotator::ZeroRotator);
        if (Resident)
        {
            Resident->RoutineRole = TEXT("Elf");
            Resident->ActivityPropType = Index % 2 == 0 ? TEXT("Book") : TEXT("Lantern");
            Resident->RoutinePointA = RivendellResidents[Index];
            Resident->RoutinePointB = RivendellResidents[Index] +
                FVector(180.0f + 20.0f * (Index % 3), (Index % 2 == 0 ? 120.0f : -120.0f), 0.0f);
            Resident->WalkSpeed = 48.0f + 3.0f * (Index % 3);
            Resident->MinWait = 2.5f;
            Resident->MaxWait = 7.0f;
        }
    }

    SpawnQuestTrigger(FVector(-1850, 0, 90), TEXT("RivendellRecovery"), 0, 1,
        TEXT("Frodo wakes in safety. Explore the valley and find Gandalf."), TEXT("RivendellAwakening"));
    SpawnNPC(TEXT("Gandalf"), FVector(-820, -180, 70), FRotator(0, 120, 0), TEXT("RivendellRecovery"), 1, 2,
        TEXT("You are safe for the moment, but the Ring cannot remain here forever."), TEXT("CouncilOfElrond"), 0);

    // Optional social space before the Council.
    SpawnNPC(TEXT("Bilbo"), FVector(-1450, 320, 70), FRotator(0, 40, 0), NAME_None, 0, -1,
        TEXT("Rivendell is kind to old bones, but memory travels farther than any road."));
    SpawnQuestTrigger(FVector(-1360, 360, 90), NAME_None, 0, -1,
        TEXT("Bilbo has found a quiet corner of Rivendell, but the journey still weighs on him."), TEXT("BilboReunion"));

    SpawnNPC(TEXT("Boromir"), FVector(700, -330, 70), FRotator(0, 80, 0), NAME_None, 0, -1,
        TEXT("Gondor has stood beneath the shadow for years. I did not come here for riddles."));
    SpawnNPC(TEXT("Legolas"), FVector(820, 300, 70), FRotator(0, 220, 0), NAME_None, 0, -1,
        TEXT("The valley is peaceful, but news from the wider world does not stop at its borders."));
    SpawnNPC(TEXT("Gimli"), FVector(520, 420, 70), FRotator(0, 210, 0), NAME_None, 0, -1,
        TEXT("Fair place. Too many stairs. I will decide which matters more after supper."));
    SpawnNPC(TEXT("Aragorn"), FVector(-260, -420, 70), FRotator(0, 30, 0), NAME_None, 0, -1,
        TEXT("There are roads here I have known since youth. None of them make the next choice easier."));

    SpawnNPC(TEXT("Arwen"), FVector(-520, 420, 70), FRotator(0, 320, 0), NAME_None, 0, -1,
        TEXT("You have time to breathe here. Do not mistake that for the end of the danger."));

    SpawnNPC(TEXT("Sam"), FVector(-120, 360, 65), FRotator(0, 210, 0), NAME_None, 0, -1,
        TEXT("It is a fair place, but I will feel better when I know what road we are taking."));
    SpawnNPC(TEXT("Merry"), FVector(80, 420, 65), FRotator(0, 205, 0), NAME_None, 0, -1,
        TEXT("There are more paths in this valley than I can count. Pippin has already tried."));
    SpawnNPC(TEXT("Pippin"), FVector(260, 460, 65), FRotator(0, 200, 0), NAME_None, 0, -1,
        TEXT("I only wanted to see where the stairs went. There were more stairs."));

    SpawnQuestTrigger(FVector(1050, 0, 90), TEXT("CouncilOfElrond"), 0, 1,
        TEXT("Representatives gather. The fate of the Ring will be decided here."), TEXT("CouncilBegins"));
    SpawnNPC(TEXT("Elrond"), FVector(1250, 180, 70), FRotator(0, 210, 0), TEXT("CouncilOfElrond"), 1, 2,
        TEXT("The Ring must be carried beyond the reach of those who would claim it."), TEXT("FellowshipForms"), 0);

    SpawnQuestTrigger(FVector(1490, -120, 90), TEXT("FellowshipForms"), 0, 1,
        TEXT("Nine companions stand together. Meet them before the road south."), TEXT("FellowshipAssembled"));
    SpawnNPC(TEXT("Aragorn"), FVector(1720, 80, 70), FRotator(0, 200, 0), TEXT("FellowshipForms"), 1, 2,
        TEXT("We leave with the first clear light. Keep only what you can carry."));
    SpawnQuestTrigger(FVector(2300, 0, 90), TEXT("FellowshipForms"), 2, 2,
        TEXT("The Fellowship leaves Rivendell and turns south."), TEXT("RivendellDeparture"), NAME_None, 0,
        TEXT("P1C05"), TEXT("SouthwardJourney"), 0);
}

void AFellowshipChapterWorldBuilder::BuildFellowshipRoad()
{
    SpawnShape(CubeMesh, FVector(0, 0, -75), FVector(46, 28, 0.75f), FLinearColor(0.19f, 0.20f, 0.17f));

    // Mountain walls build toward Caradhras, while lower foothills remain visible behind the company.
    for (int32 I = 0; I < 10; ++I)
    {
        const float X = -1200.0f + I * 560.0f;
        const float Z = 120.0f + FMath::Max(0, I - 2) * 55.0f;
        SpawnShape(ConeMesh, FVector(X, 1700.0f, Z), FVector(4.0f, 4.0f, 5.2f + 0.35f * I),
            FLinearColor(0.42f, 0.44f, 0.45f), FRotator::ZeroRotator, false);
        SpawnShape(ConeMesh, FVector(X + 260.0f, -1750.0f, Z - 25.0f), FVector(3.7f, 3.7f, 4.8f + 0.30f * I),
            FLinearColor(0.39f, 0.41f, 0.42f), FRotator::ZeroRotator, false);
    }

    // Snow sheets thicken along the pass rather than appearing as one white block.
    for (int32 I = 0; I < 9; ++I)
    {
        const float X = -100.0f + I * 270.0f;
        const float Z = 60.0f + I * 23.0f;
        SpawnShape(CubeMesh, FVector(X, (I % 2 == 0 ? 160.0f : -180.0f), Z), FVector(1.9f, 2.1f, 0.035f),
            FLinearColor(0.82f, 0.86f, 0.88f), FRotator(0.0f, I * 7.0f, 0.0f), false);
    }

    for (int32 I = 0; I < 14; ++I)
    {
        const float X = -2600.0f + I * 390.0f;
        SpawnShape(CubeMesh, FVector(X, 0, 20 + FMath::Max(0, I - 6) * 22), FVector(2.4f, 0.9f, 0.12f),
            I < 7 ? FLinearColor(0.28f, 0.25f, 0.18f) : FLinearColor(0.72f, 0.74f, 0.76f));
    }

    // Loose scree, cairns and route markers increase mountain scale without expensive simulation.
    for (int32 I = 0; I < 18; ++I)
    {
        const float X = -2200.0f + I * 290.0f;
        const float Y = (I % 2 == 0 ? 720.0f : -760.0f);
        SpawnShape(SphereMesh, FVector(X, Y, 24.0f + (I % 3) * 7.0f),
            FVector(0.42f + 0.05f * (I % 4), 0.33f, 0.22f),
            I < 9 ? FLinearColor(0.31f, 0.30f, 0.27f) : FLinearColor(0.68f, 0.70f, 0.72f),
            FRotator(0.0f, I * 23.0f, 0.0f), true);
    }
    for (int32 I = 0; I < 4; ++I)
    {
        const FVector Cairn(-1750.0f + I * 780.0f, I % 2 == 0 ? 520.0f : -520.0f, 0.0f);
        for (int32 Layer = 0; Layer < 3; ++Layer)
        {
            SpawnShape(SphereMesh, Cairn + FVector(0, 0, 18.0f + Layer * 24.0f),
                FVector(0.28f - Layer * 0.04f), FLinearColor(0.32f, 0.31f, 0.29f),
                FRotator::ZeroRotator, false);
        }
    }

    const FVector MountainBirds[] = {
        FVector(-1450, -900, 720), FVector(250, 980, 860), FVector(1650, -920, 980)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(MountainBirds); ++Index)
    {
        AShireAmbientNPC* Bird = GetWorld()->SpawnActor<AShireAmbientNPC>(MountainBirds[Index], FRotator::ZeroRotator);
        if (!Bird) continue;
        Bird->RoutineRole = TEXT("Bird");
        Bird->RoutinePointA = MountainBirds[Index];
        Bird->RoutinePointB = MountainBirds[Index] + FVector(720.0f, Index % 2 == 0 ? 520.0f : -520.0f, 120.0f);
        Bird->WalkSpeed = 175.0f + 15.0f * Index;
        Bird->MinWait = 0.0f;
        Bird->MaxWait = 0.0f;
    }

    // Fellowship camp / training clearing.
    SpawnShape(CubeMesh, FVector(-1050, 420, 18), FVector(4.0f, 3.0f, 0.08f), FLinearColor(0.24f, 0.25f, 0.18f));
    SpawnShape(CylinderMesh, FVector(-1050, 420, 42), FVector(0.24f, 0.24f, 0.08f), FLinearColor(0.45f, 0.20f, 0.06f), FRotator::ZeroRotator, false);
    for (int32 I = 0; I < 7; ++I)
    {
        const float Angle = I * (360.0f / 7.0f);
        const FVector Offset(FMath::Cos(FMath::DegreesToRadians(Angle)) * 190.0f,
            FMath::Sin(FMath::DegreesToRadians(Angle)) * 190.0f, 0.0f);
        SpawnShape(CubeMesh, FVector(-1050, 420, 28) + Offset, FVector(0.58f, 0.18f, 0.08f),
            I % 2 == 0 ? FLinearColor(0.28f, 0.20f, 0.10f) : FLinearColor(0.20f, 0.24f, 0.14f),
            FRotator(0.0f, Angle, 0.0f), false);
    }
    SpawnShape(CubeMesh, FVector(-1290, 560, 42), FVector(0.38f, 0.32f, 0.34f),
        FLinearColor(0.25f, 0.16f, 0.08f), FRotator(0, 18, 0), true);
    SpawnShape(CubeMesh, FVector(-810, 560, 42), FVector(0.34f, 0.28f, 0.30f),
        FLinearColor(0.25f, 0.16f, 0.08f), FRotator(0, -16, 0), true);
    SpawnLabel(TEXT("Fellowship Camp"), FVector(-1050, 420, 220), FLinearColor(0.86f, 0.82f, 0.68f));

    SpawnShape(CubeMesh, FVector(500, 580, 470), FVector(12, 2.4f, 4.8f), FLinearColor(0.50f, 0.52f, 0.54f));
    SpawnLabel(TEXT("Caradhras"), FVector(500, 0, 620), FLinearColor::White);

    SpawnShape(CubeMesh, FVector(2300, 0, -15), FVector(5.5f, 10.0f, 0.2f), FLinearColor(0.05f, 0.17f, 0.22f), FRotator::ZeroRotator, false);
    SpawnShape(CubeMesh, FVector(2920, 0, 320), FVector(1.1f, 7.0f, 3.2f), FLinearColor(0.20f, 0.22f, 0.22f));
    SpawnShape(CylinderMesh, FVector(2810, 0, 170), FVector(1.0f, 1.0f, 1.7f), FLinearColor(0.35f, 0.38f, 0.37f), FRotator(0, 90, 0));
    SpawnLabel(TEXT("West Gate of Moria"), FVector(2700, 0, 540), FLinearColor(0.78f, 0.82f, 0.80f));

    SpawnTravelCompanion(TEXT("Sam"), FVector(-2200, -190, 70),
        TEXT("I will keep an eye on the packs. You keep an eye on the road."));
    SpawnTravelCompanion(TEXT("Aragorn"), FVector(-2270, 150, 70),
        TEXT("The mountains make their own weather. We should not waste the clear hours."));
    SpawnTravelCompanion(TEXT("Legolas"), FVector(-2360, -330, 70),
        TEXT("There is movement far above us, but it is too distant to name."));
    SpawnTravelCompanion(TEXT("Gimli"), FVector(-2450, 300, 70),
        TEXT("A road under the mountain would be better than a road over it."));

    SpawnQuestTrigger(FVector(-2050, 0, 90), TEXT("SouthwardJourney"), 0, 1,
        TEXT("Travel south with the Fellowship. Keep pace and watch the ridges."), TEXT("FellowshipMarch"));

    SpawnQuestTrigger(FVector(-1150, 260, 90), TEXT("SouthwardJourney"), 1, 1,
        TEXT("The company pauses. Boromir turns the stop into training for Merry and Pippin."), TEXT("FellowshipCamp"));
    SpawnNPC(TEXT("Boromir"), FVector(-980, 500, 70), FRotator(0, 200, 0), TEXT("SouthwardJourney"), 1, -1,
        TEXT("A sword is no help if your feet are in the wrong place. Again."), NAME_None, 0, true);
    SpawnNPC(TEXT("Merry"), FVector(-860, 390, 65), FRotator(0, 20, 0), TEXT("SouthwardJourney"), 1, -1,
        TEXT("I am beginning to suspect he enjoys correcting us."), NAME_None, 0, true);
    SpawnNPC(TEXT("Pippin"), FVector(-830, 500, 65), FRotator(0, 20, 0), TEXT("SouthwardJourney"), 1, -1,
        TEXT("I would learn faster if training came with second breakfast."), NAME_None, 0, true);

    SpawnQuestTrigger(FVector(-620, 0, 110), TEXT("SouthwardJourney"), 1, 1,
        TEXT("Black birds cross the sky in an unnatural mass. Get the company under cover."), TEXT("CrebainWarning"));

    SpawnQuestTrigger(FVector(-250, 0, 120), TEXT("SouthwardJourney"), 1, 2,
        TEXT("The mountain pass rises ahead. Snow thickens underfoot."), TEXT("CaradhrasApproach"), TEXT("CaradhrasPass"), 0);
    SpawnQuestTrigger(FVector(700, 0, 250), TEXT("CaradhrasPass"), 0, 1,
        TEXT("The storm worsens. Stay together and keep moving."), TEXT("CaradhrasStorm"));
    SpawnNPC(TEXT("Gandalf"), FVector(930, -120, 220), FRotator(0, 180, 0), TEXT("CaradhrasPass"), 1, 2,
        TEXT("We cannot force the mountain. We will seek another road."), TEXT("WestGate"), 0);
    SpawnQuestTrigger(FVector(2250, 0, 90), TEXT("WestGate"), 0, 1,
        TEXT("Dark water lies before the western door. Search the stone carefully."), TEXT("MoriaLake"));
    SpawnNPC(TEXT("Gandalf"), FVector(2730, -160, 70), FRotator(0, 90, 0), TEXT("WestGate"), 1, 2,
        TEXT("The door will open, but the answer is simpler than our fear makes it."));
    SpawnQuestTrigger(FVector(3050, 0, 90), TEXT("WestGate"), 2, 2,
        TEXT("The company passes beneath the mountain as the lake erupts behind them."), TEXT("MoriaDoorOpens"), NAME_None, 0,
        TEXT("P1C06"), TEXT("MoriaDark"), 0);
}

void AFellowshipChapterWorldBuilder::BuildMoria()
{
    SpawnShape(CubeMesh, FVector(0, 0, -80), FVector(48, 24, 0.8f), FLinearColor(0.08f, 0.085f, 0.09f));

    // Massive side walls and ceiling ribs give the mine a readable scale beyond the playable corridor.
    for (int32 I = 0; I < 10; ++I)
    {
        const float X = -2300.0f + I * 560.0f;
        SpawnShape(CubeMesh, FVector(X, -1250.0f, 360.0f), FVector(2.8f, 0.65f, 4.4f),
            FLinearColor(0.12f, 0.12f, 0.13f), FRotator::ZeroRotator, true);
        SpawnShape(CubeMesh, FVector(X, 1250.0f, 360.0f), FVector(2.8f, 0.65f, 4.4f),
            FLinearColor(0.12f, 0.12f, 0.13f), FRotator::ZeroRotator, true);
        SpawnShape(CubeMesh, FVector(X, 0.0f, 760.0f), FVector(2.6f, 12.0f, 0.28f),
            FLinearColor(0.10f, 0.10f, 0.11f), FRotator::ZeroRotator, true);
    }

    // Pillar forest and cold braziers make the halls feel architectural rather than a single tunnel.
    for (int32 I = 0; I < 16; ++I)
    {
        const float X = -2100.0f + (I % 8) * 600.0f;
        const float Y = I < 8 ? -760.0f : 760.0f;
        SpawnShape(CylinderMesh, FVector(X, Y, 250.0f), FVector(0.32f, 0.32f, 2.5f),
            FLinearColor(0.18f, 0.18f, 0.19f), FRotator::ZeroRotator, true);
        SpawnShape(CubeMesh, FVector(X, Y, 510.0f), FVector(0.52f, 0.52f, 0.16f),
            FLinearColor(0.20f, 0.20f, 0.21f), FRotator::ZeroRotator, true);
    }
    for (int32 I = 0; I < 6; ++I)
    {
        const float X = -1450.0f + I * 720.0f;
        SpawnShape(CylinderMesh, FVector(X, (I % 2 == 0 ? -420.0f : 420.0f), 46.0f),
            FVector(0.18f, 0.18f, 0.14f), FLinearColor(0.28f, 0.22f, 0.15f), FRotator::ZeroRotator, false);
        SpawnShape(SphereMesh, FVector(X, (I % 2 == 0 ? -420.0f : 420.0f), 72.0f),
            FVector(0.16f), FLinearColor(0.42f, 0.17f, 0.045f), FRotator::ZeroRotator, false);
    }

    // Rubble and side-door silhouettes make the route feel like one path through a much larger city.
    for (int32 I = 0; I < 14; ++I)
    {
        const float X = -1850.0f + I * 320.0f;
        const float Y = (I % 2 == 0 ? 690.0f : -720.0f);
        SpawnShape(CubeMesh, FVector(X, Y, 24.0f), FVector(0.42f + 0.08f * (I % 3), 0.50f, 0.32f),
            FLinearColor(0.20f, 0.20f, 0.21f), FRotator(I * 7.0f, I * 13.0f, 0.0f), true);
    }

    // Collapsed entrance / lake-side threshold carried over from the West Gate.
    SpawnShape(CubeMesh, FVector(-2350, 0, 40), FVector(3.0f, 3.0f, 0.20f), FLinearColor(0.18f, 0.19f, 0.19f));
    SpawnShape(SphereMesh, FVector(-2250, 480, 90), FVector(1.6f, 0.30f, 0.26f), FLinearColor(0.10f, 0.18f, 0.16f), FRotator(0, 30, 0), false);
    SpawnShape(SphereMesh, FVector(-2180, -470, 95), FVector(1.5f, 0.28f, 0.25f), FLinearColor(0.10f, 0.18f, 0.16f), FRotator(0, -25, 0), false);

    for (int32 I = 0; I < 12; ++I)
    {
        SpawnShape(CubeMesh, FVector(-1900.0f + I * 430.0f, 0, 15), FVector(2.6f, 1.2f, 0.12f),
            FLinearColor(0.17f, 0.17f, 0.18f));
    }
    for (int32 I = 0; I < 10; ++I)
    {
        const float X = -1100.0f + I * 290.0f;
        SpawnShape(CylinderMesh, FVector(X, -520, 250), FVector(0.45f, 0.45f, 2.5f), FLinearColor(0.24f, 0.24f, 0.25f));
        SpawnShape(CylinderMesh, FVector(X, 520, 250), FVector(0.45f, 0.45f, 2.5f), FLinearColor(0.24f, 0.24f, 0.25f));
    }

    SpawnShape(CubeMesh, FVector(450, 0, 20), FVector(4.0f, 3.5f, 0.15f), FLinearColor(0.19f, 0.19f, 0.20f));
    SpawnShape(CubeMesh, FVector(450, 0, 75), FVector(1.2f, 0.7f, 0.45f), FLinearColor(0.30f, 0.30f, 0.31f));
    SpawnLabel(TEXT("Balin's Tomb"), FVector(450, 0, 270), FLinearColor(0.75f, 0.76f, 0.78f));

    // Cave troll proxy silhouette in the chamber.
    SpawnShape(CubeMesh, FVector(1050, 180, 150), FVector(0.75f, 0.65f, 1.5f), FLinearColor(0.20f, 0.22f, 0.18f), FRotator::ZeroRotator, false);
    SpawnShape(SphereMesh, FVector(1050, 180, 315), FVector(0.52f), FLinearColor(0.18f, 0.20f, 0.16f), FRotator::ZeroRotator, false);
    SpawnLabel(TEXT("Cave Troll Threat"), FVector(1050, 180, 440), FLinearColor(0.72f, 0.68f, 0.58f));

    // Black abyss under the bridge and broken approaches on either side.
    SpawnShape(CubeMesh, FVector(2450, 0, -35), FVector(7.0f, 9.0f, 0.15f), FLinearColor(0.02f, 0.02f, 0.025f), FRotator::ZeroRotator, false);
    SpawnShape(CubeMesh, FVector(2450, -930, 80), FVector(8.0f, 0.45f, 2.2f), FLinearColor(0.11f, 0.10f, 0.10f));
    SpawnShape(CubeMesh, FVector(2450, 930, 80), FVector(8.0f, 0.45f, 2.2f), FLinearColor(0.11f, 0.10f, 0.10f));
    SpawnShape(CubeMesh, FVector(2450, 0, 40), FVector(5.6f, 0.38f, 0.12f), FLinearColor(0.27f, 0.26f, 0.24f));
    SpawnLabel(TEXT("Bridge of Khazad-dum"), FVector(2450, 0, 300), FLinearColor(0.82f, 0.72f, 0.52f));

    SpawnTravelCompanion(TEXT("Sam"), FVector(-2440, -210, 70),
        TEXT("Stay where I can see you, Mr. Frodo. This place swallows the light."));
    SpawnTravelCompanion(TEXT("Merry"), FVector(-2520, 120, 70),
        TEXT("Every passage looks older than the last one."));
    SpawnTravelCompanion(TEXT("Pippin"), FVector(-2600, -40, 70),
        TEXT("I am trying very hard not to touch anything."));
    SpawnTravelCompanion(TEXT("Aragorn"), FVector(-2680, 250, 70),
        TEXT("Keep the company close. Sound travels farther than sight down here."));
    SpawnTravelCompanion(TEXT("Boromir"), FVector(-2760, -310, 70),
        TEXT("If something comes through these halls, we meet it together."));
    SpawnTravelCompanion(TEXT("Legolas"), FVector(-2840, 90, 70),
        TEXT("The air is still, but the stone carries echoes."));
    SpawnTravelCompanion(TEXT("Gandalf"), FVector(-2920, -150, 70),
        TEXT("Do not wander. The road is difficult enough when we remain together."),
        TEXT("MoriaEscape"));

    SpawnQuestTrigger(FVector(-2250, 0, 90), TEXT("MoriaDark"), 0, 1,
        TEXT("Something from the lake strikes at the entrance. Get inside before the doors are lost."), TEXT("WatcherAttack"));
    SpawnQuestTrigger(FVector(-1750, 0, 90), TEXT("MoriaDark"), 1, 2,
        TEXT("The doors close behind you. Follow Gandalf through the dark halls."), TEXT("MoriaEntry"));
    SpawnQuestTrigger(FVector(-650, 0, 90), TEXT("MoriaDark"), 2, 3,
        TEXT("The air changes. Evidence of battle lies ahead."), TEXT("MoriaUnease"), TEXT("BalinsTomb"), 0);

    SpawnQuestTrigger(FVector(250, 0, 90), TEXT("BalinsTomb"), 0, 1,
        TEXT("Enter the chamber and search for what happened here."), TEXT("BalinsTombReveal"));
    SpawnNPC(TEXT("Gimli"), FVector(520, -140, 70), FRotator(0, 170, 0), TEXT("BalinsTomb"), 1, 2,
        TEXT("This hall was meant to be a home. We cannot remain here now."));
    SpawnQuestTrigger(FVector(820, 0, 90), TEXT("BalinsTomb"), 2, 3,
        TEXT("Drums answer from the deep. Orcs flood toward the chamber."), TEXT("MoriaAttack"));

    SpawnEnemy(EFellowshipEnemyType::Orc, FVector(980, -260, 75), FRotator(0, 170, 0), TEXT("BalinsTomb"), 3);
    SpawnEnemy(EFellowshipEnemyType::Orc, FVector(1080, 260, 75), FRotator(0, 195, 0), TEXT("BalinsTomb"), 3);
    SpawnEnemy(EFellowshipEnemyType::Orc, FVector(1260, -80, 75), FRotator(0, 180, 0), TEXT("BalinsTomb"), 3);
    SpawnQuestTrigger(FVector(1120, 0, 90), TEXT("BalinsTomb"), 3, 4,
        TEXT("A cave troll smashes into the fight. Keep moving and protect the hobbits."), TEXT("CaveTrollAttack"), TEXT("BridgeOfKhazadDum"), 0);

    SpawnEnemy(EFellowshipEnemyType::CaveTroll, FVector(1450, 260, 95), FRotator(0, 190, 0), TEXT("BridgeOfKhazadDum"), 0);

    SpawnQuestTrigger(FVector(2000, 0, 90), TEXT("BridgeOfKhazadDum"), 0, 1,
        TEXT("Run for the bridge. Something greater than the orcs is coming."), TEXT("BalrogApproach"));
    SpawnQuestTrigger(FVector(2520, 0, 90), TEXT("BridgeOfKhazadDum"), 1, 2,
        TEXT("Cross the bridge while Gandalf holds the passage."), TEXT("BridgeConfrontation"));
    SpawnQuestTrigger(FVector(3000, 0, 90), TEXT("BridgeOfKhazadDum"), 2, 3,
        TEXT("The Fellowship escapes the mountain, but Gandalf is gone."), TEXT("MoriaEscape"), NAME_None, 0,
        TEXT("P1C07"), TEXT("LothlorienRest"), 0);
}

void AFellowshipChapterWorldBuilder::BuildLothlorien()
{
    SpawnShape(CubeMesh, FVector(0, 0, -75), FVector(40, 30, 0.75f), FLinearColor(0.08f, 0.20f, 0.09f));

    // Golden canopy layers distinguish Lothlorien from the Shire/Rivendell forests.
    for (int32 I = 0; I < 18; ++I)
    {
        const float X = -2450.0f + (I % 9) * 620.0f;
        const float Y = (I < 9 ? -1180.0f : 1180.0f);
        SpawnShape(CylinderMesh, FVector(X, Y, 210.0f), FVector(0.22f, 0.22f, 2.1f),
            FLinearColor(0.25f, 0.16f, 0.07f), FRotator::ZeroRotator, true);
        SpawnShape(SphereMesh, FVector(X, Y, 430.0f), FVector(1.20f, 1.20f, 0.78f),
            FLinearColor(0.60f, 0.54f, 0.19f), FRotator::ZeroRotator, false);
    }

    // Silver-gold leaf beds in quiet clearings.
    for (int32 I = 0; I < 10; ++I)
    {
        SpawnShape(SphereMesh, FVector(-1600.0f + I * 360.0f, (I % 2 == 0 ? 380.0f : -420.0f), 18.0f),
            FVector(0.34f, 0.28f, 0.10f), FLinearColor(0.67f, 0.61f, 0.27f), FRotator::ZeroRotator, false);
    }

    for (int32 I = 0; I < 20; ++I)
    {
        const float X = -2300.0f + (I % 10) * 520.0f;
        const float Y = (I < 10 ? -760.0f : 760.0f);
        SpawnTree(FVector(X, Y, 0), 1.15f + 0.08f * (I % 3));
    }

    const FVector LorienBirds[] = {
        FVector(-1700, -500, 620), FVector(-900, 650, 700), FVector(-100, -620, 670),
        FVector(750, 620, 740), FVector(1550, -520, 690)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(LorienBirds); ++Index)
    {
        AShireAmbientNPC* Bird = GetWorld()->SpawnActor<AShireAmbientNPC>(LorienBirds[Index], FRotator::ZeroRotator);
        if (!Bird) continue;
        Bird->RoutineRole = TEXT("Bird");
        Bird->RoutinePointA = LorienBirds[Index];
        Bird->RoutinePointB = LorienBirds[Index] + FVector(480.0f, Index % 2 == 0 ? 330.0f : -330.0f, 65.0f);
        Bird->WalkSpeed = 125.0f + 7.0f * Index;
        Bird->MinWait = 0.0f;
        Bird->MaxWait = 0.0f;
    }

    // Talan platforms, rope-bridge proxies and warm lights make the canopy feel inhabited vertically.
    for (int32 I = 0; I < 5; ++I)
    {
        const float X = -1450.0f + I * 700.0f;
        const float Y = I % 2 == 0 ? -720.0f : 720.0f;
        const float Z = 280.0f + (I % 3) * 45.0f;
        SpawnShape(CylinderMesh, FVector(X, Y, Z), FVector(1.05f, 1.05f, 0.10f),
            FLinearColor(0.36f, 0.27f, 0.12f), FRotator::ZeroRotator, true);
        SpawnShape(CylinderMesh, FVector(X, Y, Z - 120.0f), FVector(0.18f, 0.18f, 1.20f),
            FLinearColor(0.24f, 0.14f, 0.06f), FRotator::ZeroRotator, true);
        SpawnShape(SphereMesh, FVector(X + 85.0f, Y, Z + 45.0f), FVector(0.11f),
            FLinearColor(0.72f, 0.62f, 0.20f), FRotator::ZeroRotator, false);
    }
    for (int32 I = 0; I < 4; ++I)
    {
        SpawnShape(CubeMesh, FVector(-1100.0f + I * 720.0f, 0.0f, 190.0f + I * 18.0f),
            FVector(2.2f, 0.11f, 0.055f), FLinearColor(0.30f, 0.22f, 0.10f),
            FRotator(0.0f, I % 2 == 0 ? 4.0f : -4.0f, 0.0f), true);
    }

    SpawnShape(CylinderMesh, FVector(250, 0, 260), FVector(4.2f, 4.2f, 0.22f), FLinearColor(0.38f, 0.33f, 0.18f));
    SpawnShape(CylinderMesh, FVector(250, 0, 135), FVector(0.8f, 0.8f, 2.6f), FLinearColor(0.20f, 0.12f, 0.05f));
    SpawnLabel(TEXT("Caras Galadhon"), FVector(250, 0, 520), FLinearColor(0.88f, 0.82f, 0.52f));

    // Mirror glade.
    SpawnShape(CylinderMesh, FVector(1000, 420, 55), FVector(0.70f, 0.70f, 0.14f), FLinearColor(0.36f, 0.38f, 0.31f));
    SpawnShape(CylinderMesh, FVector(1000, 420, 95), FVector(0.52f, 0.52f, 0.05f), FLinearColor(0.08f, 0.24f, 0.32f), FRotator::ZeroRotator, false);
    SpawnLabel(TEXT("Mirror Glade"), FVector(1000, 420, 260), FLinearColor(0.84f, 0.86f, 0.68f));

    const FVector LorienResidents[] = {
        FVector(-1500, -420, 70), FVector(-1180, 500, 70), FVector(-520, -560, 70),
        FVector(120, 520, 70), FVector(720, -480, 70), FVector(1320, 220, 70)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(LorienResidents); ++Index)
    {
        AShireAmbientNPC* Resident = GetWorld()->SpawnActor<AShireAmbientNPC>(
            LorienResidents[Index], FRotator::ZeroRotator);
        if (Resident)
        {
            Resident->RoutineRole = TEXT("Elf");
            Resident->ActivityPropType = Index % 3 == 0 ? TEXT("Lantern") : TEXT("Book");
            Resident->RoutinePointA = LorienResidents[Index];
            Resident->RoutinePointB = LorienResidents[Index] +
                FVector(150.0f + 20.0f * (Index % 2), (Index % 2 == 0 ? 100.0f : -100.0f), 0.0f);
            Resident->WalkSpeed = 44.0f + 2.0f * (Index % 3);
            Resident->MinWait = 3.0f;
            Resident->MaxWait = 8.0f;
        }
    }

    SpawnShape(CubeMesh, FVector(2400, 0, -10), FVector(7.0f, 18.0f, 0.2f), FLinearColor(0.05f, 0.24f, 0.34f), FRotator::ZeroRotator, false);

    SpawnTravelCompanion(TEXT("Sam"), FVector(-2380, -200, 70),
        TEXT("It is quiet here. I cannot decide whether that helps."));
    SpawnTravelCompanion(TEXT("Merry"), FVector(-2460, 120, 70),
        TEXT("We should stay close. None of us is ready to lose anyone else."));
    SpawnTravelCompanion(TEXT("Pippin"), FVector(-2540, -40, 70),
        TEXT("I keep expecting to hear his voice behind us."));
    SpawnTravelCompanion(TEXT("Aragorn"), FVector(-2620, 250, 70),
        TEXT("We carry grief with us, but we still have a road to finish."));
    SpawnTravelCompanion(TEXT("Boromir"), FVector(-2700, -310, 70),
        TEXT("Rest while there is shelter. The south will ask much of us."));
    SpawnTravelCompanion(TEXT("Legolas"), FVector(-2780, 90, 70),
        TEXT("These trees are ancient even by the measure of my people."));
    SpawnTravelCompanion(TEXT("Gimli"), FVector(-2860, -150, 70),
        TEXT("I have had enough of dark stone. I will not complain about trees today."));

    SpawnQuestTrigger(FVector(-2200, 0, 90), TEXT("LothlorienRest"), 0, 0,
        TEXT("No one speaks much after Moria. The forest receives the Fellowship in silence."), TEXT("LorienGrief"));
    SpawnQuestTrigger(FVector(-1850, 0, 90), TEXT("LothlorienRest"), 0, 1,
        TEXT("The woods close around the grieving Fellowship. Follow the hidden path."), TEXT("LorienEntry"));
    SpawnNPC(TEXT("Haldir"), FVector(-900, -120, 70), FRotator(0, 170, 0), TEXT("LothlorienRest"), 1, 2,
        TEXT("You may pass, but tread carefully. These woods do not welcome careless feet."));
    SpawnNPC(TEXT("Galadriel"), FVector(250, 120, 320), FRotator(0, 200, 0), TEXT("LothlorienRest"), 2, 3,
        TEXT("Rest while you can. Each of you will carry a different burden from this place."), TEXT("GaladrielFarewell"), 0);

    SpawnQuestTrigger(FVector(950, 420, 90), TEXT("GaladrielFarewell"), 0, 0,
        TEXT("Still water becomes a window into fear, possibility and choice."), TEXT("Mirror"));
    SpawnQuestTrigger(FVector(1450, 0, 90), TEXT("GaladrielFarewell"), 0, 1,
        TEXT("Gather the boats and supplies prepared for the journey south."), TEXT("LorienFarewell"));
    SpawnQuestTrigger(FVector(2250, 0, 90), TEXT("GaladrielFarewell"), 1, 2,
        TEXT("The Fellowship takes to the river."), TEXT("LorienDeparture"), NAME_None, 0,
        TEXT("P1C08"), TEXT("AnduinJourney"), 0);
}

void AFellowshipChapterWorldBuilder::BuildAnduinAmonHen()
{
    SpawnShape(CubeMesh, FVector(0, 0, -75), FVector(48, 32, 0.75f), FLinearColor(0.12f, 0.23f, 0.11f));
    SpawnShape(CubeMesh, FVector(-650, 0, -15), FVector(24.0f, 3.4f, 0.25f), FLinearColor(0.05f, 0.25f, 0.40f), FRotator::ZeroRotator, false);

    // River canyon walls frame the Argonath approach and hide the map boundary.
    for (int32 I = 0; I < 9; ++I)
    {
        const float X = -2650.0f + I * 520.0f;
        SpawnShape(SphereMesh, FVector(X, -1500.0f, 180.0f), FVector(3.8f, 2.4f, 3.4f),
            FLinearColor(0.24f, 0.27f, 0.23f), FRotator::ZeroRotator, true);
        SpawnShape(SphereMesh, FVector(X + 140.0f, 1500.0f, 160.0f), FVector(3.6f, 2.5f, 3.2f),
            FLinearColor(0.22f, 0.25f, 0.22f), FRotator::ZeroRotator, true);
    }

    // Small river islands and reeds create scale between the boats and the banks.
    for (int32 I = 0; I < 7; ++I)
    {
        SpawnShape(SphereMesh, FVector(-1900.0f + I * 420.0f, (I % 2 == 0 ? 120.0f : -150.0f), -2.0f),
            FVector(0.70f, 0.42f, 0.12f), FLinearColor(0.24f, 0.28f, 0.15f), FRotator::ZeroRotator, false);
    }

    const FVector AnduinBirds[] = {
        FVector(-2200, -680, 520), FVector(-1350, 720, 560), FVector(-480, -650, 500),
        FVector(500, 700, 590), FVector(1450, -620, 540)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(AnduinBirds); ++Index)
    {
        AShireAmbientNPC* Bird = GetWorld()->SpawnActor<AShireAmbientNPC>(AnduinBirds[Index], FRotator::ZeroRotator);
        if (!Bird) continue;
        Bird->RoutineRole = TEXT("Bird");
        Bird->RoutinePointA = AnduinBirds[Index];
        Bird->RoutinePointB = AnduinBirds[Index] + FVector(650.0f, Index % 2 == 0 ? 440.0f : -440.0f, 80.0f);
        Bird->WalkSpeed = 155.0f + 8.0f * Index;
        Bird->MinWait = 0.0f;
        Bird->MaxWait = 0.0f;
    }

    // Boat silhouettes, reeds and shoreline camps make the river journey feel travelled rather than empty.
    const FVector BoatCenters[] = {
        FVector(-1900, -120, 10), FVector(-1500, 130, 10), FVector(-1080, -80, 10)
    };
    for (int32 I = 0; I < UE_ARRAY_COUNT(BoatCenters); ++I)
    {
        SpawnShape(CubeMesh, BoatCenters[I], FVector(1.15f, 0.28f, 0.10f),
            FLinearColor(0.30f, 0.18f, 0.08f), FRotator(0.0f, 3.0f * I, 0.0f), false);
        SpawnShape(CubeMesh, BoatCenters[I] + FVector(0, 0, 22), FVector(0.82f, 0.05f, 0.035f),
            FLinearColor(0.42f, 0.29f, 0.14f), FRotator(0.0f, 3.0f * I, 0.0f), false);
    }
    for (int32 I = 0; I < 18; ++I)
    {
        const float X = -2300.0f + I * 260.0f;
        const float Y = I % 2 == 0 ? -510.0f : 520.0f;
        SpawnShape(CylinderMesh, FVector(X, Y, 28.0f), FVector(0.022f, 0.022f, 0.28f),
            FLinearColor(0.24f, 0.32f, 0.12f), FRotator(0.0f, I * 11.0f, 0.0f), false);
    }
    SpawnShape(CylinderMesh, FVector(-520, 720, 42), FVector(0.22f, 0.22f, 0.08f),
        FLinearColor(0.42f, 0.17f, 0.045f), FRotator::ZeroRotator, false);
    for (int32 I = 0; I < 4; ++I)
    {
        SpawnShape(CubeMesh, FVector(-700.0f + I * 120.0f, 820.0f, 26.0f),
            FVector(0.42f, 0.14f, 0.08f), FLinearColor(0.26f, 0.17f, 0.08f),
            FRotator(0.0f, I * 18.0f, 0.0f), false);
    }

    SpawnShape(CylinderMesh, FVector(-250, -520, 470), FVector(1.1f, 1.1f, 4.7f), FLinearColor(0.36f, 0.37f, 0.35f));
    SpawnShape(CylinderMesh, FVector(-250, 520, 470), FVector(1.1f, 1.1f, 4.7f), FLinearColor(0.36f, 0.37f, 0.35f));
    SpawnLabel(TEXT("Argonath Passage"), FVector(-250, 0, 720), FLinearColor(0.82f, 0.82f, 0.76f));

    // Amon Hen stair fragments and broken lookout stones make the final arena readable from the river.
    for (int32 I = 0; I < 8; ++I)
    {
        SpawnShape(CubeMesh, FVector(1120.0f + I * 95.0f, 0.0f, 32.0f + I * 28.0f),
            FVector(0.62f, 1.05f, 0.11f), FLinearColor(0.33f, 0.34f, 0.31f),
            FRotator::ZeroRotator, true);
    }
    for (int32 I = 0; I < 6; ++I)
    {
        const float Angle = I * 60.0f;
        const FVector Offset(FMath::Cos(FMath::DegreesToRadians(Angle)) * 360.0f,
            FMath::Sin(FMath::DegreesToRadians(Angle)) * 360.0f, 0.0f);
        SpawnShape(CubeMesh, FVector(1750, 0, 250) + Offset, FVector(0.28f, 0.42f, 1.15f),
            FLinearColor(0.31f, 0.32f, 0.30f), FRotator(0.0f, Angle, 7.0f), true);
    }

    SpawnShape(CylinderMesh, FVector(1750, 0, 170), FVector(5.0f, 5.0f, 1.7f), FLinearColor(0.18f, 0.22f, 0.16f));
    for (int32 I = 0; I < 6; ++I)
    {
        const float Angle = I * 60.0f;
        const FVector Offset(FMath::Cos(FMath::DegreesToRadians(Angle)) * 260.0f,
            FMath::Sin(FMath::DegreesToRadians(Angle)) * 260.0f, 0.0f);
        SpawnShape(CubeMesh, FVector(1750, 0, 390) + Offset, FVector(0.38f, 0.38f, 1.2f), FLinearColor(0.33f, 0.34f, 0.31f));
    }
    SpawnLabel(TEXT("Amon Hen"), FVector(1750, 0, 650), FLinearColor::White);

    // Battle lanes for Boromir / Merry / Pippin defense.
    for (int32 I = 0; I < 7; ++I)
    {
        SpawnTree(FVector(2050.0f + I * 190.0f, (I % 2 == 0 ? 520.0f : -520.0f), 0), 0.80f);
    }

    SpawnTravelCompanion(TEXT("Sam"), FVector(-2080, -190, 70),
        TEXT("I will stay with you, whatever shore we end up on."));
    SpawnTravelCompanion(TEXT("Merry"), FVector(-2160, 130, 70),
        TEXT("The river is easier on the feet, but it gives a fellow too much time to think."),
        TEXT("BoromirFall"));
    SpawnTravelCompanion(TEXT("Pippin"), FVector(-2240, -20, 70),
        TEXT("I thought boats would feel faster than walking."),
        TEXT("BoromirFall"));
    SpawnTravelCompanion(TEXT("Aragorn"), FVector(-2320, 260, 70),
        TEXT("We cannot remain on the river forever. A choice is coming."),
        TEXT("FrodoSamDeparture"));
    SpawnTravelCompanion(TEXT("Legolas"), FVector(-2400, -300, 70),
        TEXT("There are signs of pursuit along the banks."),
        TEXT("FrodoSamDeparture"));
    SpawnTravelCompanion(TEXT("Gimli"), FVector(-2480, 80, 70),
        TEXT("Give me firm ground and an enemy I can see."),
        TEXT("FrodoSamDeparture"));

    SpawnQuestTrigger(FVector(-1900, 0, 90), TEXT("AnduinJourney"), 0, 1,
        TEXT("Travel down the Anduin and keep the boats together."), TEXT("AnduinDeparture"));
    SpawnQuestTrigger(FVector(-300, 0, 90), TEXT("AnduinJourney"), 1, 2,
        TEXT("Ancient stone guardians rise above the river."), TEXT("ArgonathReveal"));
    SpawnQuestTrigger(FVector(900, 0, 90), TEXT("AnduinJourney"), 2, 2,
        TEXT("Land beneath Amon Hen and make a brief camp."), TEXT("AmonHenArrival"), TEXT("AmonHen"), 0);

    SpawnNPC(TEXT("Boromir"), FVector(1450, -180, 180), FRotator(0, 120, 0), TEXT("AmonHen"), 0, 1,
        TEXT("We are running out of roads that do not end in danger. I need a moment to think."));
    SpawnQuestTrigger(FVector(1580, -80, 240), TEXT("AmonHen"), 1, 1,
        TEXT("The Ring presses on Boromir's fear for Gondor. Frodo realizes he must choose alone."), TEXT("BoromirPressure"));
    SpawnQuestTrigger(FVector(1800, 0, 310), TEXT("AmonHen"), 1, 2,
        TEXT("The Fellowship scatters as enemies enter the woods."), TEXT("UrukAttack"), TEXT("BreakingFellowship"), 0);

    SpawnEnemy(EFellowshipEnemyType::UrukHai, FVector(2050, -420, 75), FRotator(0, 160, 0), TEXT("BreakingFellowship"), 0);
    SpawnEnemy(EFellowshipEnemyType::UrukHai, FVector(2200, 480, 75), FRotator(0, 205, 0), TEXT("BreakingFellowship"), 0);
    SpawnEnemy(EFellowshipEnemyType::UrukHai, FVector(2380, -180, 75), FRotator(0, 180, 0), TEXT("BreakingFellowship"), 0);
    SpawnEnemy(EFellowshipEnemyType::UrukHai, FVector(2500, 360, 75), FRotator(0, 195, 0), TEXT("BreakingFellowship"), 1);

    SpawnNPC(TEXT("Boromir"), FVector(2220, 260, 70), FRotator(0, 200, 0), TEXT("BreakingFellowship"), 0, 1,
        TEXT("Find the others. Do not let the enemy take the hobbits."));
    SpawnQuestTrigger(FVector(2350, 120, 90), TEXT("BreakingFellowship"), 1, 1,
        TEXT("Boromir turns back toward Merry and Pippin and fights to protect them."), TEXT("BoromirDefense"));
    SpawnQuestTrigger(FVector(2550, -220, 90), TEXT("BreakingFellowship"), 1, 2,
        TEXT("Merry and Pippin are taken while Aragorn turns to Boromir."), TEXT("BoromirFall"));
    SpawnQuestTrigger(FVector(2800, 520, 90), TEXT("BreakingFellowship"), 2, 3,
        TEXT("Frodo chooses the eastern shore. Sam refuses to let him go alone."), TEXT("FrodoSamDeparture"), TEXT("Part1Complete"), 0);
    SpawnQuestTrigger(FVector(3200, 520, 90), TEXT("Part1Complete"), 0, 1,
        TEXT("Part I complete: the Fellowship has broken, but the journey continues."), TEXT("Part1End"));
}
