#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ShireInteractable.h"
#include "ShireEnvironmentalPuzzle.generated.h"

class USceneComponent;
class UStaticMeshComponent;

UCLASS()
class SHIREJOURNEY_API AShireEnvironmentalPuzzle : public AActor, public IShireInteractable
{
    GENERATED_BODY()

public:
    AShireEnvironmentalPuzzle();

    void ConfigurePuzzle(
        FName InDiscoveryId,
        const FText& InDisplayName,
        const FVector& NodeAOffset,
        const FVector& NodeBOffset,
        const FVector& NodeCOffset,
        int32 FirstNode,
        int32 SecondNode,
        int32 ThirdNode);

    virtual void Interact_Implementation(AActor* Interactor) override;

private:
    UPROPERTY()
    USceneComponent* Root;

    UPROPERTY()
    UStaticMeshComponent* NodeA;

    UPROPERTY()
    UStaticMeshComponent* NodeB;

    UPROPERTY()
    UStaticMeshComponent* NodeC;

    FName DiscoveryId = NAME_None;
    FText DisplayName;
    int32 ExpectedOrder[3];
    int32 CurrentStep = 0;
    bool bCompleted = false;
    float MaxNodeInteractionDistance = 330.0f;

    int32 ResolveNearestNode(const AActor* Interactor) const;
    bool IsEligible() const;
    void UpdateVisualState();
    void DisablePuzzle();
    void ShowPlayerAlert(const FText& Message, float Duration = 1.5f) const;
};
