#include "ShirePrototypeWorldBuilder.h"

#include "BlackRiderPrototype.h"
#include "ShireAmbientNPC.h"
#include "ShireNPC.h"
#include "ShireQuestTrigger.h"

#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/TextRenderActor.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

AShirePrototypeWorldBuilder::AShirePrototypeWorldBuilder()
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

void AShirePrototypeWorldBuilder::SpawnVillage()
{
    // Broad terrain slabs: cheap greybox geometry sized for the target 2 GB VRAM laptop.
    SpawnShape(CubeMesh, FVector(0.0f, 0.0f, -70.0f), FVector(65.0f, 42.0f, 0.7f),
        FLinearColor(0.16f, 0.34f, 0.10f), FRotator::ZeroRotator, true);

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

    // Bag End and nearby Hobbiton homes.
    SpawnHobbitHole(FVector(-2210.0f, -520.0f, 0.0f), 1.25f);
    SpawnLabel(TEXT("Bag End"), FVector(-2210.0f, -520.0f, 270.0f), FLinearColor::Yellow);

    SpawnHobbitHole(FVector(-1680.0f, -520.0f, 0.0f), 0.95f);
    SpawnHobbitHole(FVector(-1320.0f, 520.0f, 0.0f), 1.05f);
    SpawnHobbitHole(FVector(-760.0f, -540.0f, 0.0f), 0.90f);
    SpawnHobbitHole(FVector(-380.0f, 470.0f, 0.0f), 0.92f);
    SpawnHobbitHole(FVector(120.0f, -520.0f, 0.0f), 0.88f);

    // The Green Dragon / market silhouette.
    SpawnShape(CubeMesh, FVector(-670.0f, 250.0f, 115.0f), FVector(2.1f, 1.5f, 1.15f),
        FLinearColor(0.45f, 0.30f, 0.17f), FRotator::ZeroRotator, true);
    SpawnShape(ConeMesh, FVector(-670.0f, 250.0f, 270.0f), FVector(2.4f, 1.8f, 0.7f),
        FLinearColor(0.28f, 0.12f, 0.05f), FRotator::ZeroRotator, false);
    SpawnLabel(TEXT("The Green Dragon"), FVector(-670.0f, 250.0f, 370.0f), FLinearColor(0.85f, 0.80f, 0.55f));

    // Party field with central tree and simple pavilion blocks.
    SpawnTree(FVector(-50.0f, 720.0f, 0.0f), 1.35f);
    SpawnShape(CubeMesh, FVector(220.0f, 710.0f, 50.0f), FVector(1.4f, 0.8f, 0.5f),
        FLinearColor(0.70f, 0.62f, 0.38f), FRotator::ZeroRotator, true);
    SpawnLabel(TEXT("Party Field"), FVector(-50.0f, 720.0f, 360.0f), FLinearColor::White);

    // Brandywine river and Bucklebury Ferry destination.
    SpawnShape(CubeMesh, FVector(2780.0f, 120.0f, -10.0f), FVector(2.7f, 42.0f, 0.18f),
        FLinearColor(0.06f, 0.24f, 0.42f), FRotator::ZeroRotator, false);
    SpawnShape(CubeMesh, FVector(2690.0f, 120.0f, 12.0f), FVector(1.4f, 1.8f, 0.12f),
        FLinearColor(0.34f, 0.20f, 0.09f), FRotator::ZeroRotator, true);
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

    // Lightweight ambient population. The final art pass will replace these with optimized skeletal NPCs.
    const FVector HobbitStarts[] = {
        FVector(-1840, 80, 20), FVector(-1510, 160, 20), FVector(-1180, 20, 20), FVector(-900, 330, 20),
        FVector(-610, -120, 20), FVector(-310, 190, 20), FVector(-80, 420, 20), FVector(220, 180, 20),
        FVector(480, -40, 20), FVector(760, 150, 20), FVector(980, -220, 20), FVector(1180, 220, 20)
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
        }
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
    SpawnVillage();
    SpawnStoryActors();
}
