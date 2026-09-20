#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FellowshipMythicThreat.generated.h"

class UPointLightComponent;
class USceneComponent;
class UStaticMeshComponent;

UENUM(BlueprintType)
enum class EFellowshipMythicThreatType : uint8
{
    Watcher,
    Balrog
};

UCLASS()
class SHIREJOURNEY_API AFellowshipMythicThreat : public AActor
{
    GENERATED_BODY()

public:
    AFellowshipMythicThreat();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

    void ConfigureThreat(
        EFellowshipMythicThreatType InType,
        FName InActivationStoryBeat,
        FName InDeactivationStoryBeat);

private:
    UPROPERTY() USceneComponent* Root;
    UPROPERTY() UStaticMeshComponent* Core;
    UPROPERTY() UStaticMeshComponent* Head;
    UPROPERTY() UStaticMeshComponent* AppendageA;
    UPROPERTY() UStaticMeshComponent* AppendageB;
    UPROPERTY() UStaticMeshComponent* AppendageC;
    UPROPERTY() UStaticMeshComponent* AppendageD;
    UPROPERTY() UPointLightComponent* ThreatLight;

    EFellowshipMythicThreatType ThreatType = EFellowshipMythicThreatType::Watcher;
    FName ActivationStoryBeat = NAME_None;
    FName DeactivationStoryBeat = NAME_None;
    bool bThreatActive = false;
    float MotionTime = 0.0f;

    void ApplyVisualProfile();
    void UpdateActivation();
    void SetThreatActive(bool bActive);
    void UpdateWatcherMotion(float DeltaSeconds);
    void UpdateBalrogMotion(float DeltaSeconds);
};
