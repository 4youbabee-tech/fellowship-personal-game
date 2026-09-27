#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "ShireFootstepComponent.generated.h"

struct FHitResult;

UCLASS(ClassGroup=(Shire), meta=(BlueprintSpawnableComponent))
class SHIREJOURNEY_API UShireFootstepComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UShireFootstepComponent();

protected:
    virtual void BeginPlay() override;
    virtual void TickComponent(
        float DeltaTime,
        ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction) override;

    UPROPERTY(EditDefaultsOnly, Category="Footsteps", meta=(ClampMin="0.02", ClampMax="0.20"))
    float SampleIntervalSeconds = 0.05f;

    UPROPERTY(EditDefaultsOnly, Category="Footsteps", meta=(ClampMin="80.0", ClampMax="260.0"))
    float WalkStrideDistance = 145.0f;

    UPROPERTY(EditDefaultsOnly, Category="Footsteps", meta=(ClampMin="100.0", ClampMax="320.0"))
    float SprintStrideDistance = 185.0f;

    UPROPERTY(EditDefaultsOnly, Category="Footsteps", meta=(ClampMin="10.0", ClampMax="150.0"))
    float MinimumMovementSpeed = 45.0f;

private:
    FVector LastSampleLocation = FVector::ZeroVector;
    float DistanceSinceLastStep = 0.0f;
    bool bHasLocationSample = false;

    void ResetCadence(const FVector& CurrentLocation);
    FName ResolveSurfaceCue(const FHitResult& Hit) const;
};
