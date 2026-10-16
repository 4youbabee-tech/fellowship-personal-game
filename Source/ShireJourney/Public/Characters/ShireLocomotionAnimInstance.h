#pragma once

#include "Animation/AnimInstance.h"
#include "ShireLocomotionAnimInstance.generated.h"

class USkeletalMeshComponent;

// Gameplay values consumed by the imported, shared-skeleton locomotion graph.
UCLASS(Transient, Blueprintable)
class SHIREJOURNEY_API UShireLocomotionAnimInstance : public UAnimInstance
{
    GENERATED_BODY()
public:
    UPROPERTY(Transient, BlueprintReadOnly, Category="Locomotion")
    float GroundSpeed = 0.0f;

    virtual void NativeInitializeAnimation() override;
    virtual void NativeUpdateAnimation(float DeltaSeconds) override;

    static bool AlignMeshToCapsule(USkeletalMeshComponent* Mesh, float CapsuleHalfHeight);
private:
    FVector PreviousOwnerLocation = FVector::ZeroVector;
    bool bHasPreviousOwnerLocation = false;
};
