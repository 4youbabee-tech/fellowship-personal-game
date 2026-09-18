#include "BreePrototypeWorldBuilder.h"

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

void ABreePrototypeWorldBuilder::SpawnLabel(const FString& Text, const FVector& Location, const FLinearColor& Color)
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

    // Western gate and hedge/dike silhouette.
    SpawnShape(CubeMesh, FVector(-980.0f, -230.0f, 130.0f), FVector(0.35f, 0.35f, 1.3f),
        FLinearColor(0.20f, 0.12f, 0.07f), FRotator::ZeroRotator, true);
    SpawnShape(CubeMesh, FVector(-980.0f, 230.0f, 130.0f), FVector(0.35f, 0.35f, 1.3f),
        FLinearColor(0.20f, 0.12f, 0.07f), FRotator::ZeroRotator, true);
    SpawnShape(CubeMesh, FVector(-980.0f, 0.0f, 265.0f), FVector(0.35f, 2.65f, 0.25f),
        FLinearColor(0.18f, 0.10f, 0.06f), FRotator::ZeroRotator, true);
    SpawnLabel(TEXT("West Gate of Bree"), FVector(-980.0f, 0.0f, 380.0f), FLinearColor(0.75f, 0.75f, 0.65f));

    // Dense, narrow street walls and simple roof masses.
    const FVector HouseCenters[] = {
        FVector(-520, -430, 110), FVector(-120, -500, 110), FVector(300, -470, 110), FVector(690, -400, 110),
        FVector(-520, 430, 110), FVector(-120, 510, 110), FVector(330, 470, 110), FVector(760, 420, 110)
    };
    for (int32 Index = 0; Index < UE_ARRAY_COUNT(HouseCenters); ++Index)
    {
        const FVector P = HouseCenters[Index];
        SpawnShape(CubeMesh, P, FVector(1.45f, 1.15f, 1.10f),
            FLinearColor(0.30f, 0.24f, 0.19f), FRotator::ZeroRotator, true);
        SpawnShape(ConeMesh, P + FVector(0, 0, 165), FVector(1.7f, 1.4f, 0.65f),
            FLinearColor(0.16f, 0.10f, 0.08f), FRotator::ZeroRotator, false);
    }

    // Prancing Pony silhouette and a simple open common-room gameplay area beside it.
    SpawnShape(CubeMesh, FVector(1120.0f, 130.0f, 150.0f), FVector(2.7f, 2.2f, 1.5f),
        FLinearColor(0.34f, 0.25f, 0.17f), FRotator::ZeroRotator, true);
    SpawnShape(ConeMesh, FVector(1120.0f, 130.0f, 345.0f), FVector(3.0f, 2.5f, 0.8f),
        FLinearColor(0.14f, 0.08f, 0.05f), FRotator::ZeroRotator, false);
    SpawnLabel(TEXT("The Prancing Pony"), FVector(1120.0f, 130.0f, 470.0f), FLinearColor(0.92f, 0.75f, 0.35f));

    // Open common room proxy so Chapter 2 can be tested before an interior .umap exists.
    SpawnShape(CubeMesh, FVector(1450.0f, 780.0f, 10.0f), FVector(4.4f, 3.6f, 0.10f),
        FLinearColor(0.22f, 0.16f, 0.10f), FRotator::ZeroRotator, true);
    SpawnShape(CubeMesh, FVector(1450.0f, 1110.0f, 135.0f), FVector(4.4f, 0.15f, 1.35f),
        FLinearColor(0.26f, 0.20f, 0.15f), FRotator::ZeroRotator, true);
    SpawnShape(CubeMesh, FVector(1850.0f, 780.0f, 135.0f), FVector(0.15f, 3.6f, 1.35f),
        FLinearColor(0.26f, 0.20f, 0.15f), FRotator::ZeroRotator, true);
    SpawnLabel(TEXT("Common Room Prototype"), FVector(1450.0f, 780.0f, 300.0f), FLinearColor::White);

    // Tables / bar proxies.
    for (int32 Row = 0; Row < 2; ++Row)
    {
        for (int32 Col = 0; Col < 3; ++Col)
        {
            SpawnShape(CubeMesh, FVector(1220.0f + Col * 180.0f, 650.0f + Row * 190.0f, 48.0f),
                FVector(0.65f, 0.45f, 0.10f), FLinearColor(0.28f, 0.17f, 0.08f), FRotator::ZeroRotator, true);
        }
    }
    SpawnShape(CubeMesh, FVector(1710.0f, 920.0f, 65.0f), FVector(1.35f, 0.35f, 0.65f),
        FLinearColor(0.30f, 0.18f, 0.09f), FRotator::ZeroRotator, true);

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
            Townsperson->WalkSpeed = 42.0f + 4.0f * (Index % 3);
        }
    }
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
    SpawnStoryFlow();
}
