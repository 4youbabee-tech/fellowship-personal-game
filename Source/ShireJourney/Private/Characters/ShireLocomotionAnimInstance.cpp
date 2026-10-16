#include "ShireLocomotionAnimInstance.h"

#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "GameFramework/Pawn.h"

void UShireLocomotionAnimInstance::NativeInitializeAnimation()
{
    Super::NativeInitializeAnimation();
    bHasPreviousOwnerLocation = false;
    GroundSpeed = 0.0f;
    UE_LOG(LogTemp, Display, TEXT("SHIRE_AUTHORED_LOCOMOTION_INITIALIZED owner=%s class=%s"),
        *GetNameSafe(TryGetPawnOwner()), *GetClass()->GetPathName());
}

void UShireLocomotionAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
    Super::NativeUpdateAnimation(DeltaSeconds);
    APawn* Owner = TryGetPawnOwner();
    if (!Owner || !FMath::IsFinite(DeltaSeconds) || DeltaSeconds <= KINDA_SMALL_NUMBER)
    {
        GroundSpeed = 0.0f;
        bHasPreviousOwnerLocation = false;
        return;
    }
    const FVector Location = Owner->GetActorLocation();
    float Speed = Owner->GetVelocity().Size2D();
    // Existing resident routines sometimes move the actor directly rather than
    // through CharacterMovement. Their actual displacement still drives gait.
    if (bHasPreviousOwnerLocation)
    {
        const float DisplacementSpeed = (Location - PreviousOwnerLocation).Size2D() / DeltaSeconds;
        if (FMath::IsFinite(DisplacementSpeed) && DisplacementSpeed <= 1200.0f)
        {
            Speed = FMath::Max(Speed, DisplacementSpeed);
        }
    }
    PreviousOwnerLocation = Location;
    bHasPreviousOwnerLocation = true;
    GroundSpeed = FMath::IsFinite(Speed) ? FMath::Clamp(Speed, 0.0f, 600.0f) : 0.0f;
}

bool UShireLocomotionAnimInstance::AlignMeshToCapsule(
    USkeletalMeshComponent* Mesh, float CapsuleHalfHeight)
{
    if (!Mesh || !Mesh->SkeletalMesh || CapsuleHalfHeight <= 0.0f)
    {
        return false;
    }
    const FBoxSphereBounds Bounds = Mesh->SkeletalMesh->GetBounds();
    const float Height = Bounds.BoxExtent.Z * 2.0f;
    if (!FMath::IsFinite(Height) || Height < 1.0f)
    {
        return false;
    }
    const float Scale = (CapsuleHalfHeight * 2.0f) / Height;
    Mesh->SetRelativeScale3D(FVector(Scale));
    Mesh->SetRelativeLocation(FVector(0.0f, 0.0f,
        -CapsuleHalfHeight - (Bounds.Origin.Z - Bounds.BoxExtent.Z) * Scale));
    return true;
}
