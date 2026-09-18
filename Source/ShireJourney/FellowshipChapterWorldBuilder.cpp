#include "FellowshipChapterWorldBuilder.h"

#include "BlackRiderPrototype.h"
#include "FellowshipEnemyPrototype.h"
#include "ShireNPC.h"
#include "ShireQuestTrigger.h"

#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/TextRenderActor.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

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

void AFellowshipChapterWorldBuilder::SpawnLabel(const FString& Text, const FVector& Location, const FLinearColor& Color)
{
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

void AFellowshipChapterWorldBuilder::BuildChapter(FName ChapterId)
{
    if (bBuilt || !GetWorld())
    {
        return;
    }

    bBuilt = true;

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

    // Fellowship camp / training clearing.
    SpawnShape(CubeMesh, FVector(-1050, 420, 18), FVector(4.0f, 3.0f, 0.08f), FLinearColor(0.24f, 0.25f, 0.18f));
    SpawnShape(CylinderMesh, FVector(-1050, 420, 42), FVector(0.24f, 0.24f, 0.08f), FLinearColor(0.45f, 0.20f, 0.06f), FRotator::ZeroRotator, false);
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

    SpawnShape(CylinderMesh, FVector(250, 0, 260), FVector(4.2f, 4.2f, 0.22f), FLinearColor(0.38f, 0.33f, 0.18f));
    SpawnShape(CylinderMesh, FVector(250, 0, 135), FVector(0.8f, 0.8f, 2.6f), FLinearColor(0.20f, 0.12f, 0.05f));
    SpawnLabel(TEXT("Caras Galadhon"), FVector(250, 0, 520), FLinearColor(0.88f, 0.82f, 0.52f));

    // Mirror glade.
    SpawnShape(CylinderMesh, FVector(1000, 420, 55), FVector(0.70f, 0.70f, 0.14f), FLinearColor(0.36f, 0.38f, 0.31f));
    SpawnShape(CylinderMesh, FVector(1000, 420, 95), FVector(0.52f, 0.52f, 0.05f), FLinearColor(0.08f, 0.24f, 0.32f), FRotator::ZeroRotator, false);
    SpawnLabel(TEXT("Mirror Glade"), FVector(1000, 420, 260), FLinearColor(0.84f, 0.86f, 0.68f));

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

    SpawnShape(CylinderMesh, FVector(-250, -520, 470), FVector(1.1f, 1.1f, 4.7f), FLinearColor(0.36f, 0.37f, 0.35f));
    SpawnShape(CylinderMesh, FVector(-250, 520, 470), FVector(1.1f, 1.1f, 4.7f), FLinearColor(0.36f, 0.37f, 0.35f));
    SpawnLabel(TEXT("Argonath Passage"), FVector(-250, 0, 720), FLinearColor(0.82f, 0.82f, 0.76f));

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
