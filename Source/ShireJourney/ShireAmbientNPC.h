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

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Routine")
    FName RoutineRole = TEXT("Villager");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Awareness")
    bool bCanNoticePlayer = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Awareness")
    float PlayerNoticeRadius = 280.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Awareness")
    float MinObserveDuration = 1.2f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Awareness")
    float MaxObserveDuration = 2.8f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Awareness")
    float NoticeCooldown = 7.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Awareness", meta=(ClampMin="1.0", ClampMax="2.0"))
    float RunningNoticeMultiplier = 1.35f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Performance")
    float ReducedTickDistance = 3500.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Performance")
    float DormantTickDistance = 9000.0f;

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
    bool bObservingPlayer = false;
    float WaitRemaining = 0.0f;
    float WalkPhase = 0.0f;
    float SenseAccumulator = 0.0f;
    float ObserveRemaining = 0.0f;
    float NoticeCooldownRemaining = 0.0f;
    float SocialCheckRemaining = 0.0f;
    float SocialRemaining = 0.0f;
    bool bSocializing = false;
    float VisualTorsoBaseZ = 58.0f;
    float VisualHeadBaseZ = 101.0f;
    float VisualHairBaseZ = 109.0f;
    TWeakObjectPtr<APawn> ObservedPlayer;
    TWeakObjectPtr<AShireAmbientNPC> SocialPartner;
    FRandomStream Random;

    void ApplyVisualStyle();
    void UpdateWalkAnimation(float DeltaSeconds, bool bMoving);
    void UpdateAwareness(float DeltaSeconds);
    void UpdateSocialLife(float DeltaSeconds);
};
