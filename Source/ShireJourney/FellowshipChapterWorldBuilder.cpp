#include "FellowshipChapterWorldBuilder.h"

#include "BlackRiderPrototype.h"
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

    UStaticMeshComponent* MeshComponent = Actor->GetStaticMeshComponent();
    MeshComponent->SetStaticMesh(Mesh);
    MeshComponent->SetMobility(EComponentMobility::Static);
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

void AFellowshipChapterWorldBuilder::SpawnNPC(
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
        return;
    }

    AShireNPC* NPC = GetWorld()->SpawnActor<AShireNPC>(Location, Rotation);
    if (!NPC)
    {
        return;
    }

    NPC->DisplayName = FText::FromString(Name);
    NPC->DialogueLines = { FText::FromString(Line) };
    NPC->QuestId = QuestId;
    NPC->RequiredQuestStage = RequiredStage;
    NPC->QuestStageAfterInteraction = StageAfter;
    NPC->NextQuestId = NextQuestId;
    NPC->NextQuestStage = NextQuestStage;
    NPC->bFollowPlayerAfterInteraction = bFollow;
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
    SpawnQuestTrigger(FVector(2750, 0, 90), TEXT("FlightToFord"), 1, 2,
        TEXT("The river crossing is ahead. Reach the far bank before the Riders."), TEXT("FordChase"));
    SpawnQuestTrigger(FVector(3200, 0, 90), TEXT("FlightToFord"), 2, 2,
        TEXT("The pursuit breaks at the river. Rivendell lies beyond."), TEXT("FordEscape"), NAME_None, 0,
        TEXT("P1C04"), TEXT("RivendellRecovery"), 0);
}

void AFellowshipChapterWorldBuilder::BuildRivendell()
{
    SpawnShape(CubeMesh, FVector(0, 0, -80), FVector(34, 26, 0.8f), FLinearColor(0.12f, 0.22f, 0.14f));

    // Valley terraces and water.
    SpawnShape(CubeMesh, FVector(0, 720, -20), FVector(30, 2.0f, 0.2f), FLinearColor(0.06f, 0.28f, 0.42f), FRotator::ZeroRotator, false);
    for (int32 I = 0; I < 10; ++I)
    {
        SpawnTree(FVector(-1900.0f + I * 420.0f, (I % 2 == 0 ? 620.0f : -620.0f), 0.0f), 0.9f);
    }

    // Elven house terraces / bridges.
    SpawnShape(CubeMesh, FVector(-650, 0, 95), FVector(3.8f, 2.8f, 0.95f), FLinearColor(0.62f, 0.55f, 0.42f));
    SpawnShape(ConeMesh, FVector(-650, 0, 240), FVector(4.2f, 3.2f, 0.65f), FLinearColor(0.32f, 0.24f, 0.16f), FRotator::ZeroRotator, false);
    SpawnShape(CubeMesh, FVector(450, 0, 25), FVector(4.0f, 0.45f, 0.18f), FLinearColor(0.48f, 0.42f, 0.32f));
    SpawnShape(CylinderMesh, FVector(1250, 0, 35), FVector(3.0f, 3.0f, 0.35f), FLinearColor(0.56f, 0.52f, 0.44f));
    SpawnLabel(TEXT("Rivendell"), FVector(-650, 0, 420), FLinearColor(0.92f, 0.88f, 0.72f));
    SpawnLabel(TEXT("Council Terrace"), FVector(1250, 0, 220), FLinearColor::White);

    SpawnQuestTrigger(FVector(-1850, 0, 90), TEXT("RivendellRecovery"), 0, 1,
        TEXT("Frodo wakes in safety. Explore the valley and find Gandalf."), TEXT("RivendellAwakening"));
    SpawnNPC(TEXT("Gandalf"), FVector(-820, -180, 70), FRotator(0, 120, 0), TEXT("RivendellRecovery"), 1, 2,
        TEXT("You are safe for the moment, but the Ring cannot remain here forever."), TEXT("CouncilOfElrond"), 0);

    SpawnQuestTrigger(FVector(1050, 0, 90), TEXT("CouncilOfElrond"), 0, 1,
        TEXT("Representatives gather. The fate of the Ring will be decided here."), TEXT("CouncilBegins"));
    SpawnNPC(TEXT("Elrond"), FVector(1250, 180, 70), FRotator(0, 210, 0), TEXT("CouncilOfElrond"), 1, 2,
        TEXT("The Ring must be carried beyond the reach of those who would claim it."), TEXT("FellowshipForms"), 0);

    SpawnQuestTrigger(FVector(1490, -120, 90), TEXT("FellowshipForms"), 0, 1,
        TEXT("Nine companions stand together. Prepare to leave the valley."), TEXT("FellowshipAssembled"));
    SpawnNPC(TEXT("Aragorn"), FVector(1720, 80, 70), FRotator(0, 200, 0), TEXT("FellowshipForms"), 1, 2,
        TEXT("We leave with the first clear light. Keep only what you can carry."));
    SpawnQuestTrigger(FVector(2300, 0, 90), TEXT("FellowshipForms"), 2, 2,
        TEXT("The Fellowship leaves Rivendell and turns south."), TEXT("RivendellDeparture"), NAME_None, 0,
        TEXT("P1C05"), TEXT("SouthwardJourney"), 0);
}

void AFellowshipChapterWorldBuilder::BuildFellowshipRoad()
{
    SpawnShape(CubeMesh, FVector(0, 0, -75), FVector(42, 25, 0.75f), FLinearColor(0.19f, 0.20f, 0.17f));

    for (int32 I = 0; I < 12; ++I)
    {
        const float X = -2400.0f + I * 420.0f;
        SpawnShape(CubeMesh, FVector(X, 0, 20 + FMath::Max(0, I - 4) * 25), FVector(2.5f, 0.9f, 0.12f),
            I < 6 ? FLinearColor(0.28f, 0.25f, 0.18f) : FLinearColor(0.72f, 0.74f, 0.76f));
    }

    // Caradhras wall.
    SpawnShape(CubeMesh, FVector(500, 580, 470), FVector(12, 2.4f, 4.8f), FLinearColor(0.50f, 0.52f, 0.54f));
    SpawnLabel(TEXT("Caradhras"), FVector(500, 0, 620), FLinearColor::White);

    // West-gate lake and door wall.
    SpawnShape(CubeMesh, FVector(2300, 0, -15), FVector(5.5f, 10.0f, 0.2f), FLinearColor(0.05f, 0.17f, 0.22f), FRotator::ZeroRotator, false);
    SpawnShape(CubeMesh, FVector(2920, 0, 320), FVector(1.1f, 7.0f, 3.2f), FLinearColor(0.20f, 0.22f, 0.22f));
    SpawnShape(CylinderMesh, FVector(2810, 0, 170), FVector(1.0f, 1.0f, 1.7f), FLinearColor(0.35f, 0.38f, 0.37f), FRotator(0, 90, 0));
    SpawnLabel(TEXT("West Gate of Moria"), FVector(2700, 0, 540), FLinearColor(0.78f, 0.82f, 0.80f));

    SpawnQuestTrigger(FVector(-1850, 0, 90), TEXT("SouthwardJourney"), 0, 1,
        TEXT("Travel south with the Fellowship. Keep pace and watch the ridges."), TEXT("FellowshipMarch"));
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
        TEXT("The company passes beneath the mountain."), TEXT("MoriaDoorOpens"), NAME_None, 0,
        TEXT("P1C06"), TEXT("MoriaDark"), 0);
}

void AFellowshipChapterWorldBuilder::BuildMoria()
{
    SpawnShape(CubeMesh, FVector(0, 0, -80), FVector(44, 22, 0.8f), FLinearColor(0.08f, 0.085f, 0.09f));

    // Main halls.
    for (int32 I = 0; I < 12; ++I)
    {
        SpawnShape(CubeMesh, FVector(-2400.0f + I * 430.0f, 0, 15), FVector(2.6f, 1.2f, 0.12f),
            FLinearColor(0.17f, 0.17f, 0.18f));
    }
    for (int32 I = 0; I < 10; ++I)
    {
        const float X = -1300.0f + I * 290.0f;
        SpawnShape(CylinderMesh, FVector(X, -520, 250), FVector(0.45f, 0.45f, 2.5f), FLinearColor(0.24f, 0.24f, 0.25f));
        SpawnShape(CylinderMesh, FVector(X, 520, 250), FVector(0.45f, 0.45f, 2.5f), FLinearColor(0.24f, 0.24f, 0.25f));
    }

    // Balin's tomb chamber.
    SpawnShape(CubeMesh, FVector(450, 0, 20), FVector(4.0f, 3.5f, 0.15f), FLinearColor(0.19f, 0.19f, 0.20f));
    SpawnShape(CubeMesh, FVector(450, 0, 75), FVector(1.2f, 0.7f, 0.45f), FLinearColor(0.30f, 0.30f, 0.31f));
    SpawnLabel(TEXT("Balin's Tomb"), FVector(450, 0, 270), FLinearColor(0.75f, 0.76f, 0.78f));

    // Bridge and chasm.
    SpawnShape(CubeMesh, FVector(2350, 0, -35), FVector(7.0f, 9.0f, 0.15f), FLinearColor(0.02f, 0.02f, 0.025f), FRotator::ZeroRotator, false);
    SpawnShape(CubeMesh, FVector(2350, 0, 40), FVector(5.6f, 0.38f, 0.12f), FLinearColor(0.27f, 0.26f, 0.24f));
    SpawnLabel(TEXT("Bridge of Khazad-dum"), FVector(2350, 0, 300), FLinearColor(0.82f, 0.72f, 0.52f));

    SpawnQuestTrigger(FVector(-1900, 0, 90), TEXT("MoriaDark"), 0, 1,
        TEXT("The doors close behind you. Follow Gandalf through the dark halls."), TEXT("MoriaEntry"));
    SpawnQuestTrigger(FVector(-650, 0, 90), TEXT("MoriaDark"), 1, 2,
        TEXT("The air changes. Evidence of battle lies ahead."), TEXT("MoriaUnease"), TEXT("BalinsTomb"), 0);
    SpawnQuestTrigger(FVector(250, 0, 90), TEXT("BalinsTomb"), 0, 1,
        TEXT("Enter the chamber and search for what happened here."), TEXT("BalinsTombReveal"));
    SpawnNPC(TEXT("Gimli"), FVector(520, -140, 70), FRotator(0, 170, 0), TEXT("BalinsTomb"), 1, 2,
        TEXT("This hall was meant to be a home. We cannot remain here now."));
    SpawnQuestTrigger(FVector(900, 0, 90), TEXT("BalinsTomb"), 2, 2,
        TEXT("Drums answer from the deep. Fight your way out of the chamber."), TEXT("MoriaAttack"), TEXT("BridgeOfKhazadDum"), 0);
    SpawnQuestTrigger(FVector(1950, 0, 90), TEXT("BridgeOfKhazadDum"), 0, 1,
        TEXT("Run for the bridge. Something greater than the orcs is coming."), TEXT("BalrogApproach"));
    SpawnQuestTrigger(FVector(2420, 0, 90), TEXT("BridgeOfKhazadDum"), 1, 2,
        TEXT("Cross the bridge while Gandalf holds the passage."), TEXT("BridgeConfrontation"));
    SpawnQuestTrigger(FVector(2900, 0, 90), TEXT("BridgeOfKhazadDum"), 2, 3,
        TEXT("The Fellowship escapes the mountain, but Gandalf is gone."), TEXT("MoriaEscape"), NAME_None, 0,
        TEXT("P1C07"), TEXT("LothlorienRest"), 0);
}

void AFellowshipChapterWorldBuilder::BuildLothlorien()
{
    SpawnShape(CubeMesh, FVector(0, 0, -75), FVector(36, 26, 0.75f), FLinearColor(0.08f, 0.20f, 0.09f));

    for (int32 I = 0; I < 16; ++I)
    {
        const float X = -2100.0f + (I % 8) * 600.0f;
        const float Y = (I < 8 ? -700.0f : 700.0f);
        SpawnTree(FVector(X, Y, 0), 1.25f);
    }

    // Elevated flets / central glade.
    SpawnShape(CylinderMesh, FVector(250, 0, 260), FVector(4.2f, 4.2f, 0.22f), FLinearColor(0.38f, 0.33f, 0.18f));
    SpawnShape(CylinderMesh, FVector(250, 0, 135), FVector(0.8f, 0.8f, 2.6f), FLinearColor(0.20f, 0.12f, 0.05f));
    SpawnLabel(TEXT("Caras Galadhon Prototype"), FVector(250, 0, 520), FLinearColor(0.88f, 0.82f, 0.52f));

    // River departure area.
    SpawnShape(CubeMesh, FVector(2400, 0, -10), FVector(7.0f, 18.0f, 0.2f), FLinearColor(0.05f, 0.24f, 0.34f), FRotator::ZeroRotator, false);

    SpawnQuestTrigger(FVector(-1850, 0, 90), TEXT("LothlorienRest"), 0, 1,
        TEXT("The woods close around the grieving Fellowship. Follow the hidden path."), TEXT("LorienEntry"));
    SpawnNPC(TEXT("Haldir"), FVector(-900, -120, 70), FRotator(0, 170, 0), TEXT("LothlorienRest"), 1, 2,
        TEXT("You may pass, but tread carefully. These woods do not welcome careless feet."));
    SpawnNPC(TEXT("Galadriel"), FVector(250, 120, 320), FRotator(0, 200, 0), TEXT("LothlorienRest"), 2, 3,
        TEXT("Rest while you can. Each of you will carry a different burden from this place."), TEXT("GaladrielFarewell"), 0);
    SpawnQuestTrigger(FVector(1450, 0, 90), TEXT("GaladrielFarewell"), 0, 1,
        TEXT("Gather the boats and supplies prepared for the journey south."), TEXT("LorienFarewell"));
    SpawnQuestTrigger(FVector(2250, 0, 90), TEXT("GaladrielFarewell"), 1, 2,
        TEXT("The Fellowship takes to the river."), TEXT("LorienDeparture"), NAME_None, 0,
        TEXT("P1C08"), TEXT("AnduinJourney"), 0);
}

void AFellowshipChapterWorldBuilder::BuildAnduinAmonHen()
{
    SpawnShape(CubeMesh, FVector(0, 0, -75), FVector(44, 28, 0.75f), FLinearColor(0.12f, 0.23f, 0.11f));
    SpawnShape(CubeMesh, FVector(-650, 0, -15), FVector(24.0f, 3.4f, 0.25f), FLinearColor(0.05f, 0.25f, 0.40f), FRotator::ZeroRotator, false);

    // Argonath proxy statues.
    SpawnShape(CylinderMesh, FVector(-250, -520, 470), FVector(1.1f, 1.1f, 4.7f), FLinearColor(0.36f, 0.37f, 0.35f));
    SpawnShape(CylinderMesh, FVector(-250, 520, 470), FVector(1.1f, 1.1f, 4.7f), FLinearColor(0.36f, 0.37f, 0.35f));
    SpawnLabel(TEXT("Argonath Passage"), FVector(-250, 0, 720), FLinearColor(0.82f, 0.82f, 0.76f));

    // Amon Hen hill / ruins.
    SpawnShape(CylinderMesh, FVector(1750, 0, 170), FVector(5.0f, 5.0f, 1.7f), FLinearColor(0.18f, 0.22f, 0.16f));
    for (int32 I = 0; I < 6; ++I)
    {
        const float Angle = I * 60.0f;
        const FVector Offset(FMath::Cos(FMath::DegreesToRadians(Angle)) * 260.0f,
            FMath::Sin(FMath::DegreesToRadians(Angle)) * 260.0f, 0.0f);
        SpawnShape(CubeMesh, FVector(1750, 0, 390) + Offset, FVector(0.38f, 0.38f, 1.2f), FLinearColor(0.33f, 0.34f, 0.31f));
    }
    SpawnLabel(TEXT("Amon Hen"), FVector(1750, 0, 650), FLinearColor::White);

    SpawnQuestTrigger(FVector(-1900, 0, 90), TEXT("AnduinJourney"), 0, 1,
        TEXT("Travel down the Anduin and keep the boats together."), TEXT("AnduinDeparture"));
    SpawnQuestTrigger(FVector(-300, 0, 90), TEXT("AnduinJourney"), 1, 2,
        TEXT("Ancient stone guardians rise above the river."), TEXT("ArgonathReveal"));
    SpawnQuestTrigger(FVector(900, 0, 90), TEXT("AnduinJourney"), 2, 2,
        TEXT("Land beneath Amon Hen and make a brief camp."), TEXT("AmonHenArrival"), TEXT("AmonHen"), 0);

    SpawnNPC(TEXT("Boromir"), FVector(1450, -180, 180), FRotator(0, 120, 0), TEXT("AmonHen"), 0, 1,
        TEXT("We are running out of roads that do not end in danger. I need a moment to think."));
    SpawnQuestTrigger(FVector(1800, 0, 310), TEXT("AmonHen"), 1, 2,
        TEXT("The Fellowship scatters as enemies enter the woods."), TEXT("UrukAttack"), TEXT("BreakingFellowship"), 0);
    SpawnNPC(TEXT("Boromir"), FVector(2220, 260, 70), FRotator(0, 200, 0), TEXT("BreakingFellowship"), 0, 1,
        TEXT("Find the others. Do not let the enemy take the hobbits."));
    SpawnQuestTrigger(FVector(2500, -220, 90), TEXT("BreakingFellowship"), 1, 2,
        TEXT("Merry and Pippin are taken while Aragorn turns to Boromir."), TEXT("BoromirFall"));
    SpawnQuestTrigger(FVector(2750, 520, 90), TEXT("BreakingFellowship"), 2, 3,
        TEXT("Frodo chooses the eastern shore. Sam refuses to let him go alone."), TEXT("FrodoSamDeparture"), TEXT("Part1Complete"), 0);
    SpawnQuestTrigger(FVector(3150, 520, 90), TEXT("Part1Complete"), 0, 1,
        TEXT("Part I complete: the Fellowship has broken, but the journey continues."), TEXT("Part1End"));
}
