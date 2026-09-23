#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ShireInteractable.h"
#include "ShireWorldEventInteraction.generated.h"

class USceneComponent;
class UStaticMeshComponent;

UCLASS()
class SHIREJOURNEY_API AShireWorldEventInteraction : public AActor, public IShireInteractable
{
    GENERATED_BODY()

public:
    AShireWorldEventInteraction();

    void ConfigureInteraction(
        FName InEventId,
        FName InEventType,
        FName InChapterId,
        const FText& InPromptText,
        const FText& InResponseText,
        bool bInSuppressDuringDanger = true);

    virtual void Interact_Implementation(AActor* Interactor) override;

private:
    UPROPERTY()
    USceneComponent* Root;

    UPROPERTY()
    UStaticMeshComponent* InteractionMarker;

    FName EventId = NAME_None;
    FName EventType = NAME_None;
    FName ChapterId = NAME_None;
    FText PromptText;
    FText ResponseText;
    bool bSuppressDuringDanger = true;
    bool bConsumed = false;

    bool IsInteractionAllowed() const;
    void DisableInteraction();
    void ShowAlert(const FText& Message, float Duration = 1.6f) const;
};
