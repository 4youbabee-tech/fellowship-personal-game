#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BlackRiderPrototype.generated.h"

class USceneComponent;
class UStaticMeshComponent;

UCLASS()
class SHIREJOURNEY_API ABlackRiderPrototype : public AActor
{
    GENERATED_BODY()

public:
    ABlackRiderPrototype();
    virtual void BeginPlay() override;
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

private:
    UPROPERTY()
    USceneComponent* Root;

    UPROPERTY()
    UStaticMeshComponent* HorseBody;

    UPROPERTY()
    UStaticMeshComponent* RiderBody;

    UPROPERTY()
    UStaticMeshComponent* RiderHead;

    bool bHeadingToB = true;
    float NextAlertTime = 0.0f;

    void UpdatePatrol(float DeltaSeconds);
    void CheckPlayerDetection();
};
