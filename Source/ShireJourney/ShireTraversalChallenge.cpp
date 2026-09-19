#include "ShireTraversalChallenge.h"

#include "ShireHUD.h"
#include "ShirePlayerCharacter.h"
#include "ShireQuestSubsystem.h"

#include "Components/SceneComponent.h"
#include "Components/SphereComponent.h"
#include "Engine/GameInstance.h"
#include "GameFramework/PlayerController.h"

AShireTraversalChallenge::AShireTraversalChallenge()
{
    PrimaryActorTick.bCanEverTick = false;

    Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    SetRootComponent(Root);

    GateA = CreateDefaultSubobject<USphereComponent>(TEXT("GateA"));
    GateB = CreateDefaultSubobject<USphereComponent>(TEXT("GateB"));
    GateC = CreateDefaultSubobject<USphereComponent>(TEXT("GateC"));

    USphereComponent* Gates[] = { GateA, GateB, GateC };
    for (USphereComponent* Gate : Gates)
    {
        Gate->SetupAttachment(Root);
        Gate->SetSphereRadius(150.0f);
        Gate->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
        Gate->SetCollisionResponseToAllChannels(ECR_Ignore);
        Gate->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
    }
}

void AShireTraversalChallenge::ConfigureChallenge(
    FName InDiscoveryId,
    const FText& InDisplayName,
    FName InRequiredStoryBeat,
    FName InBlockedAfterStoryBeat,
    FName InCompletionStoryBeat,
    const FVector& GateAOffset,
    const FVector& GateBOffset,
    const FVector& GateCOffset)
{
    DiscoveryId = InDiscoveryId;
    DisplayName = InDisplayName;
    RequiredStoryBeat = InRequiredStoryBeat;
    BlockedAfterStoryBeat = InBlockedAfterStoryBeat;
    CompletionStoryBeat = InCompletionStoryBeat;

    GateA->SetRelativeLocation(GateAOffset);
    GateB->SetRelativeLocation(GateBOffset);
    GateC->SetRelativeLocation(GateCOffset);
}

void AShireTraversalChallenge::BeginPlay()
{
    Super::BeginPlay();

    GateA->OnComponentBeginOverlap.AddDynamic(this, &AShireTraversalChallenge::HandleGateOverlap);
    GateB->OnComponentBeginOverlap.AddDynamic(this, &AShireTraversalChallenge::HandleGateOverlap);
    GateC->OnComponentBeginOverlap.AddDynamic(this, &AShireTraversalChallenge::HandleGateOverlap);
}

bool AShireTraversalChallenge::IsEligible() const
{
    const UGameInstance* GI = GetGameInstance();
    const UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!Quests)
    {
        return false;
    }
    if (RequiredStoryBeat != NAME_None && !Quests->HasStoryBeatTriggered(RequiredStoryBeat))
    {
        return false;
    }
    if (BlockedAfterStoryBeat != NAME_None && Quests->HasStoryBeatTriggered(BlockedAfterStoryBeat))
    {
        return false;
    }
    return true;
}

void AShireTraversalChallenge::DisableChallenge()
{
    GateA->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    GateB->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    GateC->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}

void AShireTraversalChallenge::HandleGateOverlap(
    UPrimitiveComponent* OverlappedComponent,
    AActor* OtherActor,
    UPrimitiveComponent* OtherComp,
    int32 OtherBodyIndex,
    bool bFromSweep,
    const FHitResult& SweepResult)
{
    if (bCompleted || !Cast<AShirePlayerCharacter>(OtherActor) || !IsEligible())
    {
        return;
    }

    int32 GateIndex = INDEX_NONE;
    if (OverlappedComponent == GateA) GateIndex = 0;
    else if (OverlappedComponent == GateB) GateIndex = 1;
    else if (OverlappedComponent == GateC) GateIndex = 2;

    if (GateIndex == 0 && CurrentGateIndex != 0)
    {
        CurrentGateIndex = 1;
        return;
    }
    if (GateIndex != CurrentGateIndex)
    {
        return;
    }

    ++CurrentGateIndex;
    if (CurrentGateIndex < 3)
    {
        return;
    }

    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!Quests)
    {
        return;
    }

    const int32 InsightBefore = Quests->GetJourneyInsight();
    const bool bNewDiscovery = Quests->RegisterJourneyDiscovery(DiscoveryId);
    if (!bNewDiscovery)
    {
        bCompleted = true;
        DisableChallenge();
        return;
    }

    if (CompletionStoryBeat != NAME_None)
    {
        Quests->TriggerStoryBeat(CompletionStoryBeat);
    }

    bCompleted = true;
    DisableChallenge();

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
        TEXT("TraversalChallenge: PASS id=%s gates=3"),
        *DiscoveryId.ToString());
}
