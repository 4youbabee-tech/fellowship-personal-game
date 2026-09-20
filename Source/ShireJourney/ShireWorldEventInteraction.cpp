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
    InteractionMarker->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
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
    if (bConsumed || !Cast<AShirePlayerCharacter>(Interactor))
    {
        return;
    }

    if (!IsInteractionAllowed())
    {
        DisableInteraction();
        return;
    }

    if (!PromptText.IsEmpty())
    {
        ShowAlert(PromptText, 1.2f);
    }

    if (!ResponseText.IsEmpty())
    {
        ShowAlert(ResponseText, 2.4f);
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
