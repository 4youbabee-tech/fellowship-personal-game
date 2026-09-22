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
    ChallengeType = TEXT("TRAVERSAL_CHALLENGE");
    bRequireCrouch = false;
    MaxCompletionSeconds = 0.0f;
    ChallengeStartedAtSeconds = -1.0f;

    GateA->SetRelativeLocation(GateAOffset);
    GateB->SetRelativeLocation(GateBOffset);
    GateC->SetRelativeLocation(GateCOffset);
}

void AShireTraversalChallenge::ConfigureActivityChallenge(
    FName InDiscoveryId,
    const FText& InDisplayName,
    FName InChallengeType,
    const FVector& GateAOffset,
    const FVector& GateBOffset,
    const FVector& GateCOffset,
    bool bInRequireCrouch,
    float InMaxCompletionSeconds)
{
    DiscoveryId = InDiscoveryId;
    DisplayName = InDisplayName;
    RequiredStoryBeat = NAME_None;
    BlockedAfterStoryBeat = NAME_None;
    CompletionStoryBeat = NAME_None;
    ChallengeType = InChallengeType == NAME_None ? TEXT("TRAVERSAL_CHALLENGE") : InChallengeType;
    bRequireCrouch = bInRequireCrouch || ChallengeType == TEXT("STEALTH_LITE");
    MaxCompletionSeconds = InMaxCompletionSeconds > 0.0f
        ? FMath::Clamp(InMaxCompletionSeconds, 5.0f, 120.0f)
        : (ChallengeType == TEXT("TIMING_CHALLENGE") ? 24.0f : 0.0f);
    ChallengeStartedAtSeconds = -1.0f;
    CurrentGateIndex = 0;
    bCompleted = false;

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
    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!Quests) return false;
    if (RequiredStoryBeat != NAME_None && !Quests->HasStoryBeatTriggered(RequiredStoryBeat)) return false;
    if (BlockedAfterStoryBeat != NAME_None && Quests->HasStoryBeatTriggered(BlockedAfterStoryBeat)) return false;
    if (Quests->HasSideActivityForDiscovery(DiscoveryId) &&
        !Quests->IsSideActivityDiscoveryAvailable(DiscoveryId)) return false;
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
    AShirePlayerCharacter* Player = Cast<AShirePlayerCharacter>(OtherActor);
    if (bCompleted || !Player || !Player->IsGameplayWorldCommitted() || !IsEligible())
    {
        return;
    }

    UGameInstance* GI = GetGameInstance();
    UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!Quests)
    {
        return;
    }

    AShireHUD* HUD = nullptr;
    if (APlayerController* PC = GetWorld() ? GetWorld()->GetFirstPlayerController() : nullptr)
    {
        HUD = Cast<AShireHUD>(PC->GetHUD());
    }

    if (bRequireCrouch && !Player->IsCrouchingForStealth())
    {
        CurrentGateIndex = 0;
        ChallengeStartedAtSeconds = -1.0f;
        if (HUD)
        {
            HUD->ShowAlert(FText::FromString(TEXT("Keep low and move quietly through this route.")), 1.4f);
        }
        return;
    }

    int32 GateIndex = INDEX_NONE;
    if (OverlappedComponent == GateA) GateIndex = 0;
    else if (OverlappedComponent == GateB) GateIndex = 1;
    else if (OverlappedComponent == GateC) GateIndex = 2;
    if (GateIndex == INDEX_NONE)
    {
        return;
    }

    const float Now = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0f;
    if (CurrentGateIndex > 0 && MaxCompletionSeconds > 0.0f &&
        ChallengeStartedAtSeconds >= 0.0f &&
        Now - ChallengeStartedAtSeconds > MaxCompletionSeconds)
    {
        CurrentGateIndex = 0;
        ChallengeStartedAtSeconds = -1.0f;
        if (HUD)
        {
            HUD->ShowAlert(FText::FromString(TEXT("The sequence slipped away. Start again.")), 1.3f);
        }
    }

    if (GateIndex == 0 && CurrentGateIndex != 0)
    {
        CurrentGateIndex = 1;
        ChallengeStartedAtSeconds = Now;
        return;
    }
    if (GateIndex != CurrentGateIndex)
    {
        return;
    }

    if (CurrentGateIndex == 0)
    {
        ChallengeStartedAtSeconds = Now;
    }

    ++CurrentGateIndex;
    if (CurrentGateIndex < 3)
    {
        if (HUD)
        {
            HUD->ShowAlert(
                FText::FromString(FString::Printf(
                    TEXT("%s: %d / 3"),
                    DisplayName.IsEmpty() ? *ChallengeType.ToString() : *DisplayName.ToString(),
                    CurrentGateIndex)),
                1.15f);
        }
        return;
    }

    const int32 InsightBefore = Quests->GetJourneyInsight();
    const bool bNewDiscovery = Quests->HasSideActivityForDiscovery(DiscoveryId)
        ? Quests->CompleteSideActivityDiscovery(DiscoveryId)
        : Quests->RegisterJourneyDiscovery(DiscoveryId);

    if (!bNewDiscovery)
    {
        if (Quests->HasJourneyDiscovery(DiscoveryId))
        {
            bCompleted = true;
            DisableChallenge();
        }
        else
        {
            CurrentGateIndex = 0;
            ChallengeStartedAtSeconds = -1.0f;
        }
        return;
    }

    if (CompletionStoryBeat != NAME_None)
    {
        Quests->TriggerStoryBeat(CompletionStoryBeat);
    }

    bCompleted = true;
    DisableChallenge();

    if (HUD)
    {
        HUD->ShowDiscovery(
            DisplayName.IsEmpty() ? FText::FromString(DiscoveryId.ToString()) : DisplayName,
            FMath::Max(0, Quests->GetJourneyInsight() - InsightBefore),
            Quests->GetJourneyInsight(),
            3.2f);
    }

    UE_LOG(LogTemp, Display,
        TEXT("TraversalChallenge: PASS id=%s type=%s gates=3"),
        *DiscoveryId.ToString(),
        *ChallengeType.ToString());
}
