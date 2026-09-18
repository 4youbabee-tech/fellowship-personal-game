#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ShireAmbientNPC.generated.h"

class USceneComponent;
class UStaticMeshComponent;

UCLASS()
class SHIREJOURNEY_API AShireAmbientNPC : public AActor
{
    GENERATED_BODY()

public:
    AShireAmbientNPC();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Routine")
    FVector RoutinePointA = FVector::ZeroVector;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Routine")
    FVector RoutinePointB = FVector(350.0f, 0.0f, 0.0f);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Routine")
    float WalkSpeed = 55.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Routine")
    float MinWait = 1.5f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Routine")
    float MaxWait = 5.0f;

private:
    UPROPERTY()
    USceneComponent* Root;

    UPROPERTY()
    UStaticMeshComponent* Torso;

    UPROPERTY()
    UStaticMeshComponent* Head;

    UPROPERTY()
    UStaticMeshComponent* Hair;

    UPROPERTY()
    UStaticMeshComponent* LeftArm;

    UPROPERTY()
    UStaticMeshComponent* RightArm;

    UPROPERTY()
    UStaticMeshComponent* LeftLeg;

    UPROPERTY()
    UStaticMeshComponent* RightLeg;

    bool bHeadingToB = true;
    float WaitRemaining = 0.0f;
    float WalkPhase = 0.0f;
    FRandomStream Random;

    void ApplyVisualStyle();
    void UpdateWalkAnimation(float DeltaSeconds, bool bMoving);
};
