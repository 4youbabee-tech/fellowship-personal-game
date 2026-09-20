#include "IsengardPrototypeWorldBuilder.h"

#include "ShireNPC.h"
#include "ShireAmbientNPC.h"
#include "ShireQuestTrigger.h"
#include "ShireTraversalChallenge.h"

#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/TextRenderActor.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

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

    if (BasicMaterial)
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

    UStaticMesh* OrthancCore = LoadObject<UStaticMesh>(
        nullptr, TEXT("/Game/Production/World/Isengard/SM_Isengard_OrthancCore.SM_Isengard_OrthancCore"));
    UStaticMesh* OrthancSpire = LoadObject<UStaticMesh>(
        nullptr, TEXT("/Game/Production/World/Isengard/SM_Isengard_OrthancSpire.SM_Isengard_OrthancSpire"));
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

    UStaticMesh* PitRim = LoadObject<UStaticMesh>(
        nullptr, TEXT("/Game/Production/World/Isengard/SM_Isengard_IndustrialPitRim.SM_Isengard_IndustrialPitRim"));
    UStaticMesh* FurnaceStack = LoadObject<UStaticMesh>(
        nullptr, TEXT("/Game/Production/World/Isengard/SM_Isengard_FurnaceStack.SM_Isengard_FurnaceStack"));
    UStaticMesh* FelledTrunk = LoadObject<UStaticMesh>(
        nullptr, TEXT("/Game/Production/World/Isengard/SM_Isengard_FelledTrunk.SM_Isengard_FelledTrunk"));
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
    for (int32 I = 0; I < 12; ++I)
    {
        const FVector Stump(-900.0f + I * 210.0f, -820.0f - 90.0f * (I % 3), 25.0f);
        SpawnShape(FelledTrunk ? FelledTrunk : CylinderMesh, Stump,
            FelledTrunk ? FVector(0.55f) : FVector(0.16f, 0.16f, 0.25f),
            FLinearColor(0.22f, 0.12f, 0.055f),
            FelledTrunk ? FRotator(0.0f, I * 27.0f, 88.0f) : FRotator::ZeroRotator,
            true);
    }

    // Raised path acts as the prototype rooftop/prison overlook.
    for (int32 I = 0; I < 8; ++I)
    {
        SpawnShape(CubeMesh, FVector(760.0f + I * 95.0f, -520.0f, 55.0f + I * 85.0f),
            FVector(0.90f, 0.55f, 0.12f), FLinearColor(0.11f, 0.11f, 0.12f),
            FRotator(0, 0, -7.0f), true);
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
