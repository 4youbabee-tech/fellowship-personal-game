#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ShireTraversalChallenge.generated.h"

class USceneComponent;
class USphereComponent;
class UPrimitiveComponent;

UCLASS()
class SHIREJOURNEY_API AShireTraversalChallenge : public AActor
{
    GENERATED_BODY()

public:
    AShireTraversalChallenge();

    void ConfigureChallenge(
        FName InDiscoveryId,
        const FText& InDisplayName,
        FName InRequiredStoryBeat,
        FName InBlockedAfterStoryBeat,
        FName InCompletionStoryBeat,
        const FVector& GateAOffset,
        const FVector& GateBOffset,
        const FVector& GateCOffset);

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    USceneComponent* Root;

    UPROPERTY()
    USphereComponent* GateA;

    UPROPERTY()
    USphereComponent* GateB;

    UPROPERTY()
    USphereComponent* GateC;

    FName DiscoveryId = NAME_None;
    FText DisplayName;
    FName RequiredStoryBeat = NAME_None;
    FName BlockedAfterStoryBeat = NAME_None;
    FName CompletionStoryBeat = NAME_None;
    int32 CurrentGateIndex = 0;
    bool bCompleted = false;

    UFUNCTION()
    void HandleGateOverlap(
        UPrimitiveComponent* OverlappedComponent,
        AActor* OtherActor,
        UPrimitiveComponent* OtherComp,
        int32 OtherBodyIndex,
        bool bFromSweep,
        const FHitResult& SweepResult);

    bool IsEligible() const;
    void DisableChallenge();
};
