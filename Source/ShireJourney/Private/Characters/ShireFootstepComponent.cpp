#include "ShireFootstepComponent.h"

#include "ShireAudioSubsystem.h"
#include "ShirePlayerCharacter.h"

#include "Components/PrimitiveComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Materials/MaterialInterface.h"
#include "PhysicalMaterials/PhysicalMaterial.h"

namespace ShireFootstep
{
    static const FName GrassCue(TEXT("SFX_Footstep_Grass"));
    static const FName DirtCue(TEXT("SFX_Footstep_Dirt"));
    static const FName StoneCue(TEXT("SFX_Footstep_Stone"));
    static const FName WoodCue(TEXT("SFX_Footstep_Wood"));

    constexpr float SprintSpeedThreshold = 390.0f;
    constexpr float TeleportDistance = 500.0f;
    constexpr float TraceAboveOwner = 20.0f;
    constexpr float TraceBelowOwner = 145.0f;

    bool ContainsAny(const FString& Haystack, std::initializer_list<const TCHAR*> Needles)
    {
        for (const TCHAR* Needle : Needles)
        {
            if (Haystack.Contains(Needle))
            {
                return true;
            }
        }
        return false;
    }
}

UShireFootstepComponent::UShireFootstepComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.bStartWithTickEnabled = true;
    PrimaryComponentTick.TickInterval = SampleIntervalSeconds;
}

void UShireFootstepComponent::BeginPlay()
{
    Super::BeginPlay();

    PrimaryComponentTick.TickInterval = SampleIntervalSeconds;
    ResetCadence(GetOwner() ? GetOwner()->GetActorLocation() : FVector::ZeroVector);
}

void UShireFootstepComponent::ResetCadence(const FVector& CurrentLocation)
{
    LastSampleLocation = CurrentLocation;
    DistanceSinceLastStep = 0.0f;
    bHasLocationSample = true;
}

void UShireFootstepComponent::TickComponent(
    float DeltaTime,
    ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    AShirePlayerCharacter* Player = Cast<AShirePlayerCharacter>(GetOwner());
    UWorld* World = GetWorld();
    if (!Player || !World)
    {
        return;
    }

    const FVector CurrentLocation = Player->GetActorLocation();
    if (!bHasLocationSample)
    {
        ResetCadence(CurrentLocation);
        return;
    }

    const float TravelDistance = FVector::Dist2D(CurrentLocation, LastSampleLocation);
    LastSampleLocation = CurrentLocation;

    UCharacterMovementComponent* Movement = Player->GetCharacterMovement();
    const float Speed = Movement ? Movement->Velocity.Size2D() : 0.0f;
    if (!Player->IsGameplayWorldCommitted()
        || !Movement
        || !Movement->IsMovingOnGround()
        || Speed < MinimumMovementSpeed
        || TravelDistance > ShireFootstep::TeleportDistance)
    {
        DistanceSinceLastStep = 0.0f;
        return;
    }

    DistanceSinceLastStep += TravelDistance;
    const float StrideDistance = Speed >= ShireFootstep::SprintSpeedThreshold
        ? SprintStrideDistance
        : WalkStrideDistance;
    if (DistanceSinceLastStep < StrideDistance)
    {
        return;
    }

    // At most one trace and one cue are emitted per 20 Hz sample. Excess travel is
    // retained without producing an audio burst after a hitch.
    DistanceSinceLastStep = FMath::Fmod(DistanceSinceLastStep, StrideDistance);

    FHitResult Hit;
    FCollisionQueryParams QueryParams(SCENE_QUERY_STAT(ShireFootstepSurface), false, Player);
    QueryParams.bReturnPhysicalMaterial = true;

    const FVector TraceStart = CurrentLocation + FVector(0.0f, 0.0f, ShireFootstep::TraceAboveOwner);
    const FVector TraceEnd = CurrentLocation - FVector(0.0f, 0.0f, ShireFootstep::TraceBelowOwner);
    if (!World->LineTraceSingleByChannel(Hit, TraceStart, TraceEnd, ECC_Visibility, QueryParams))
    {
        return;
    }

    UGameInstance* GameInstance = World->GetGameInstance();
    UShireAudioSubsystem* Audio = GameInstance
        ? GameInstance->GetSubsystem<UShireAudioSubsystem>()
        : nullptr;
    if (Audio)
    {
        Audio->PlaySfxCueAtLocation(
            ResolveSurfaceCue(Hit),
            Hit.ImpactPoint + Hit.ImpactNormal * 2.0f,
            0.82f,
            1.0f);
    }
}

FName UShireFootstepComponent::ResolveSurfaceCue(const FHitResult& Hit) const
{
    if (Hit.PhysMaterial.IsValid())
    {
        switch (UPhysicalMaterial::DetermineSurfaceType(Hit.PhysMaterial.Get()))
        {
        case SurfaceType1:
            return ShireFootstep::GrassCue;
        case SurfaceType2:
            return ShireFootstep::DirtCue;
        case SurfaceType3:
            return ShireFootstep::StoneCue;
        case SurfaceType4:
            return ShireFootstep::WoodCue;
        default:
            break;
        }
    }

    // Keep the existing identity fallback for legacy/proxy materials that have not
    // yet been assigned an authored Physical Material. Production surfaces should
    // converge on the explicit SurfaceType contract above.
    FString SurfaceIdentity;
    if (Hit.PhysMaterial.IsValid())
    {
        SurfaceIdentity += Hit.PhysMaterial->GetName();
    }

    if (const UPrimitiveComponent* Component = Hit.GetComponent())
    {
        SurfaceIdentity += TEXT("|") + Component->GetName();

        if (const UStaticMeshComponent* StaticMeshComponent = Cast<UStaticMeshComponent>(Component))
        {
            if (const UStaticMesh* StaticMesh = StaticMeshComponent->GetStaticMesh())
            {
                SurfaceIdentity += TEXT("|") + StaticMesh->GetName();
            }
        }

        if (const UMaterialInterface* Material = Component->GetMaterial(0))
        {
            SurfaceIdentity += TEXT("|") + Material->GetName();
        }
    }

    if (const AActor* HitActor = Hit.GetActor())
    {
        SurfaceIdentity += TEXT("|") + HitActor->GetName();
        for (const FName& Tag : HitActor->Tags)
        {
            SurfaceIdentity += TEXT("|") + Tag.ToString();
        }
    }

    SurfaceIdentity = SurfaceIdentity.ToLower();
    if (ShireFootstep::ContainsAny(SurfaceIdentity, { TEXT("stone"), TEXT("rock"), TEXT("cobble"), TEXT("bridge") }))
    {
        return ShireFootstep::StoneCue;
    }
    if (ShireFootstep::ContainsAny(SurfaceIdentity, { TEXT("wood"), TEXT("timber"), TEXT("plank"), TEXT("floor"), TEXT("fence"), TEXT("cart") }))
    {
        return ShireFootstep::WoodCue;
    }
    if (ShireFootstep::ContainsAny(SurfaceIdentity, { TEXT("grass"), TEXT("turf"), TEXT("meadow"), TEXT("field"), TEXT("groundblock") }))
    {
        return ShireFootstep::GrassCue;
    }

    // P1C01 traversal is predominantly compacted earth/road when no authored
    // physical-material identity exists, so dirt is the safe chapter fallback.
    return ShireFootstep::DirtCue;
}
