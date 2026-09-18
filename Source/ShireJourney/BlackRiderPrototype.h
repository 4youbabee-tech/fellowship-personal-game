#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BlackRiderPrototype.generated.h"

class USceneComponent;
class UStaticMeshComponent;
class UShireQuestSubsystem;

UCLASS()
class SHIREJOURNEY_API ABlackRiderPrototype : public AActor
{
    GENERATED_BODY()

public:
    ABlackRiderPrototype();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    virtual void Tick(float DeltaSeconds) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Patrol")
    FVector PatrolA = FVector::ZeroVector;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Patrol")
    FVector PatrolB = FVector(900.0f, 0.0f, 0.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Patrol")
    float PatrolSpeed = 105.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Detection")
    float DetectionRadius = 650.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Detection")
    float CrouchedDetectionRadius = 340.0f;

    // Detection is intentionally throttled for the low-spec target; patrol movement still ticks smoothly.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Detection", meta=(ClampMin="0.05", ClampMax="1.0"))
    float DetectionCheckInterval = 0.15f;

    // Dot-product threshold for the Rider's forward vision cone. Lower values widen the cone.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Detection", meta=(ClampMin="-1.0", ClampMax="1.0"))
    float MinimumFacingDot = -0.05f;

    // Requiring more than one visible sample prevents one-frame edge cases from feeling like instant detection.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Detection", meta=(ClampMin="1", ClampMax="4"))
    int32 RequiredVisibleChecks = 2;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Investigation", meta=(ClampMin="1.0", ClampMax="12.0"))
    float InvestigationDuration = 4.5f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Investigation", meta=(ClampMin="1.0", ClampMax="2.0"))
    float InvestigationSpeedMultiplier = 1.20f;

private:
    UPROPERTY()
    USceneComponent* Root;

    UPROPERTY()
    UStaticMeshComponent* HorseBody;

    UPROPERTY()
    UStaticMeshComponent* RiderBody;

    UPROPERTY()
    UStaticMeshComponent* RiderHead;

    UPROPERTY()
    UShireQuestSubsystem* QuestSubsystem = nullptr;

    bool bHeadingToB = true;
    bool bDetectionQuestActive = false;
    bool bInvestigating = false;
    int32 ConsecutiveVisibleChecks = 0;
    float NextAlertTime = 0.0f;
    float NextDetectionCheckTime = 0.0f;
    float InvestigationRemaining = 0.0f;
    float RidePhase = 0.0f;
    FVector LastKnownPlayerLocation = FVector::ZeroVector;

    UFUNCTION()
    void HandleActiveQuestChanged(FName QuestId);

    void UpdatePatrol(float DeltaSeconds);
    void UpdateRideMotion(float DeltaSeconds);
    void ApplyPrototypeStyle();
    void CheckPlayerDetection();
    void ResetDetectionConfidence();
    bool HasLineOfSightToPlayer(class ACharacter* Player) const;
};
