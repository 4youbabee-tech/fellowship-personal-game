#include "ShireWorldEventInteraction.h"

#include "ShireHUD.h"
#include "ShireNPCContextSubsystem.h"
#include "ShirePlayerCharacter.h"
#include "ShireQuestSubsystem.h"

#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/StaticMesh.h"
#include "GameFramework/PlayerController.h"
#include "UObject/ConstructorHelpers.h"

AShireWorldEventInteraction::AShireWorldEventInteraction()
{
    PrimaryActorTick.bCanEverTick = false;

    Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
    SetRootComponent(Root);

    InteractionMarker = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("InteractionMarker"));
    InteractionMarker->SetupAttachment(Root);
    InteractionMarker->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    InteractionMarker->SetCollisionResponseToAllChannels(ECR_Ignore);
    InteractionMarker->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
    InteractionMarker->SetRelativeLocation(FVector(0.0f, 0.0f, 42.0f));
    InteractionMarker->SetRelativeScale3D(FVector(0.16f, 0.16f, 0.08f));

    static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    if (CylinderMesh.Succeeded())
    {
        InteractionMarker->SetStaticMesh(CylinderMesh.Object);
    }
}

void AShireWorldEventInteraction::ConfigureInteraction(
    FName InEventId,
    FName InEventType,
    FName InChapterId,
    const FText& InPromptText,
    const FText& InResponseText,
    bool bInSuppressDuringDanger)
{
    EventId = InEventId;
    EventType = InEventType;
    ChapterId = InChapterId;
    PromptText = InPromptText;
    ResponseText = InResponseText;
    bSuppressDuringDanger = bInSuppressDuringDanger;
    bConsumed = false;
    SetActorHiddenInGame(false);
    InteractionMarker->SetVisibility(true, true);
    InteractionMarker->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
}


void AShireWorldEventInteraction::ActivateFromLivingWorldPool(const FVector& InLocation)
{
    SetActorLocation(InLocation, false, nullptr, ETeleportType::TeleportPhysics);
    SetActorHiddenInGame(false);
    bConsumed = false;
    if (InteractionMarker)
    {
        InteractionMarker->SetVisibility(true, true);
        InteractionMarker->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    }
}

void AShireWorldEventInteraction::DeactivateForLivingWorldPool()
{
    bConsumed = true;
    SetActorHiddenInGame(true);
    if (InteractionMarker)
    {
        InteractionMarker->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        InteractionMarker->SetVisibility(false, true);
    }
}

bool AShireWorldEventInteraction::IsInteractionAllowed() const
{
    const UGameInstance* GI = GetGameInstance();
    const UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
    if (!Quests || Quests->GetCurrentRouteId() != TEXT("FrodoMain") ||
        Quests->GetCurrentChapterId() != ChapterId)
    {
        return false;
    }

    if (bSuppressDuringDanger)
    {
        const UShireNPCContextSubsystem* Context =
            GI ? GI->GetSubsystem<UShireNPCContextSubsystem>() : nullptr;
        if (Context && Context->IsDangerStateActive())
        {
            return false;
        }
    }

    return true;
}

void AShireWorldEventInteraction::DisableInteraction()
{
    bConsumed = true;
    InteractionMarker->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    InteractionMarker->SetVisibility(false, true);
}

void AShireWorldEventInteraction::ShowAlert(const FText& Message, float Duration) const
{
    if (APlayerController* PC = GetWorld() ? GetWorld()->GetFirstPlayerController() : nullptr)
    {
        if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
        {
            HUD->ShowAlert(Message, Duration);
        }
    }
}

void AShireWorldEventInteraction::Interact_Implementation(AActor* Interactor)
{
    AShirePlayerCharacter* Player = Cast<AShirePlayerCharacter>(Interactor);
    if (bConsumed || !Player || !Player->IsGameplayWorldCommitted())
    {
        return;
    }

    if (!IsInteractionAllowed())
    {
        // Story danger and committed-world context can change while this micro-event
        // is alive. Refusing an attempt must not mark the event consumed: the player
        // may safely retry if the same event is still active after danger clears.
        return;
    }

    if (!PromptText.IsEmpty())
    {
        ShowAlert(PromptText, 1.2f);
    }

    if (!ResponseText.IsEmpty())
    {
        if (APlayerController* PC = GetWorld() ? GetWorld()->GetFirstPlayerController() : nullptr)
        {
            if (AShireHUD* HUD = Cast<AShireHUD>(PC->GetHUD()))
            {
                // ShowAlert shares one slot: a second alert immediately erased the
                // player's prompt. The wrapped dialogue channel renders separately.
                HUD->ShowDialogue(
                    FText::FromString(TEXT("A passing moment")),
                    ResponseText,
                    3.6f);
            }
        }
    }

    DisableInteraction();

    UE_LOG(
        LogTemp,
        Display,
        TEXT("WorldEventInteraction: PASS id=%s type=%s chapter=%s storyEffect=NONE"),
        *EventId.ToString(),
        *EventType.ToString(),
        *ChapterId.ToString());
}
