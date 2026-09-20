#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WorldAmbientMotionActor.generated.h"

class USceneComponent;
class UStaticMesh;
class UStaticMeshComponent;

UENUM()
enum class EWorldAmbientMotionMode : uint8
{
    Sway,
    Bob,
    Rotate,
    Shiver
};

UCLASS()
class SHIREJOURNEY_API AWorldAmbientMotionActor : public AActor
{
    GENERATED_BODY()

public:
    AWorldAmbientMotionActor();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

    void Configure(
        UStaticMesh* InMesh,
        EWorldAmbientMotionMode InMode,
        float InAmplitude,
        float InSpeed,
        const FVector& InScale,
        bool bInCollision = false);

private:
    UPROPERTY()
    USceneComponent* Root = nullptr;

    UPROPERTY()
    UStaticMeshComponent* Mesh = nullptr;

    EWorldAmbientMotionMode MotionMode = EWorldAmbientMotionMode::Sway;
    FVector BaseLocation = FVector::ZeroVector;
    FRotator BaseRotation = FRotator::ZeroRotator;
    float MotionAmplitude = 6.0f;
    float MotionSpeed = 1.0f;
    float Phase = 0.0f;
};
