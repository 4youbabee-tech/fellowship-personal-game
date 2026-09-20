#include "ShireEnvironmentalPuzzle.h"

#include "ShireHUD.h"
#include "ShirePlayerCharacter.h"
#include "ShireQuestSubsystem.h"

#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/StaticMesh.h"
#include "GameFramework/PlayerController.h"
#include "UObject/ConstructorHelpers.h"

AShireEnvironmentalPuzzle::AShireEnvironmentalPuzzle()
{
    PrimaryActorTick.bCanEverTick = false;

    Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    SetRootComponent(Root);

    NodeA = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("NodeA"));
    NodeB = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("NodeB"));
    NodeC = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("NodeC"));

    static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube.Cube"));

    UStaticMeshComponent* Nodes[] = { NodeA, NodeB, NodeC };
    for (int32 Index = 0; Index < 3; ++Index)
    {
        UStaticMeshComponent* Node = Nodes[Index];
        Node->SetupAttachment(Root);
        Node->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
        Node->SetCollisionResponseToAllChannels(ECR_Ignore);
        Node->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
        Node->SetRelativeScale3D(FVector(0.30f, 0.30f, 0.12f));
        if (CubeMesh.Succeeded())
        {
            Node->SetStaticMesh(CubeMesh.Object);
        }
    }

    ExpectedOrder[0] = 0;
    ExpectedOrder[1] = 1;
    ExpectedOrder[2] = 2;
}

void AShireEnvironmentalPuzzle::ConfigurePuzzle(
    FName InDiscoveryId,
    const FText& InDisplayName,
    const FVector& NodeAOffset,
    const FVector& NodeBOffset,
    const FVector& NodeCOffset,
    int32 FirstNode,
    int32 SecondNode,
    int32 ThirdNode)
{
    DiscoveryId = InDiscoveryId;
    DisplayName = InDisplayName;
    NodeA->SetRelativeLocation(NodeAOffset);
    NodeB->SetRelativeLocation(NodeBOffset);
    NodeC->SetRelativeLocation(NodeCOffset);

    ExpectedOrder[0] = FMath::Clamp(FirstNode, 0, 2);
    ExpectedOrder[1] = FMath::Clamp(SecondNode, 0, 2);
    ExpectedOrder[2] = FMath::Clamp(ThirdNode, 0, 2);
    CurrentStep = 0;
    bCompleted = false;
    UpdateVisualState();
}

bool AShireEnvironmentalPuzzle::IsEligible() const
{
    const UGameInstance* GI = GetGameInstance();
    const UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!Quests || DiscoveryId == NAME_None)
    {
        return false;
    }

    return Quests->HasSideActivityForDiscovery(DiscoveryId) &&
        Quests->IsSideActivityDiscoveryAvailable(DiscoveryId);
}

int32 AShireEnvironmentalPuzzle::ResolveNearestNode(const AActor* Interactor) const
{
    if (!Interactor)
    {
        return INDEX_NONE;
    }

    UStaticMeshComponent* Nodes[] = { NodeA, NodeB, NodeC };
    int32 BestIndex = INDEX_NONE;
    float BestDistanceSq = FMath::Square(MaxNodeInteractionDistance);

    for (int32 Index = 0; Index < 3; ++Index)
    {
        const float DistanceSq = FVector::DistSquared(
            Interactor->GetActorLocation(),
            Nodes[Index]->GetComponentLocation());
        if (DistanceSq <= BestDistanceSq)
        {
            BestDistanceSq = DistanceSq;
            BestIndex = Index;
        }
    }

    return BestIndex;
}

void AShireEnvironmentalPuzzle::ShowPlayerAlert(const FText& Message, float Duration) const
{
    if (APlayerController* PC = GetWorld() ? GetWorld()->GetFirstPlayerController() : nullptr)
    {
        if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
        {
            HUD->ShowAlert(Message, Duration);
        }
    }
}

void AShireEnvironmentalPuzzle::UpdateVisualState()
{
    UStaticMeshComponent* Nodes[] = { NodeA, NodeB, NodeC };
    for (int32 Index = 0; Index < 3; ++Index)
    {
        const bool bExpected =
            !bCompleted &&
            CurrentStep >= 0 &&
            CurrentStep < 3 &&
            ExpectedOrder[CurrentStep] == Index;
        Nodes[Index]->SetRelativeScale3D(
            bExpected ? FVector(0.36f, 0.36f, 0.14f) : FVector(0.30f, 0.30f, 0.12f));
    }
}

void AShireEnvironmentalPuzzle::DisablePuzzle()
{
    UStaticMeshComponent* Nodes[] = { NodeA, NodeB, NodeC };
    for (UStaticMeshComponent* Node : Nodes)
    {
        Node->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    }
}

void AShireEnvironmentalPuzzle::Interact_Implementation(AActor* Interactor)
{
    AShirePlayerCharacter* Player = Cast<AShirePlayerCharacter>(Interactor);
    if (!Player || bCompleted)
    {
        return;
    }

    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!Quests)
    {
        return;
    }

    if (!IsEligible())
    {
        if (Quests->HasJourneyDiscovery(DiscoveryId))
        {
            bCompleted = true;
            DisablePuzzle();
        }
        else
        {
            ShowPlayerAlert(FText::FromString(TEXT("This study is not available at this point in the journey.")));
        }
        return;
    }

    const int32 NodeIndex = ResolveNearestNode(Player);
    if (NodeIndex == INDEX_NONE)
    {
        ShowPlayerAlert(FText::FromString(TEXT("Move closer to one of the marked details.")), 1.2f);
        return;
    }

    if (NodeIndex != ExpectedOrder[CurrentStep])
    {
        CurrentStep = 0;
        UpdateVisualState();
        ShowPlayerAlert(FText::FromString(TEXT("That detail does not fit the sequence. Start again.")), 1.4f);
        return;
    }

    ++CurrentStep;
    if (CurrentStep < 3)
    {
        UpdateVisualState();
        const FString Label = DisplayName.IsEmpty() ? DiscoveryId.ToString() : DisplayName.ToString();
        ShowPlayerAlert(
            FText::FromString(FString::Printf(TEXT("%s: pattern %d / 3"), *Label, CurrentStep)),
            1.25f);
        return;
    }

    const int32 InsightBefore = Quests->GetJourneyInsight();
    const bool bNewDiscovery = Quests->CompleteSideActivityDiscovery(DiscoveryId);
    if (!bNewDiscovery)
    {
        CurrentStep = 0;
        UpdateVisualState();
        return;
    }

    bCompleted = true;
    UpdateVisualState();
    DisablePuzzle();

    if (APlayerController* PC = GetWorld() ? GetWorld()->GetFirstPlayerController() : nullptr)
    {
        if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
        {
            HUD->ShowDiscovery(
                DisplayName.IsEmpty() ? FText::FromString(DiscoveryId.ToString()) : DisplayName,
                FMath::Max(0, Quests->GetJourneyInsight() - InsightBefore),
                Quests->GetJourneyInsight(),
                3.2f);
        }
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("EnvironmentalPuzzle: PASS id=%s steps=3"),
        *DiscoveryId.ToString());
}
