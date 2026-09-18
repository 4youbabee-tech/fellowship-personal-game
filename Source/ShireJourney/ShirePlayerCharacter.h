#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "ShirePlayerCharacter.generated.h"

class USpringArmComponent;
class UCameraComponent;
class UStaticMeshComponent;

UCLASS()
class SHIREJOURNEY_API AShirePlayerCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AShirePlayerCharacter();
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
    virtual void Tick(float DeltaSeconds) override;

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    void MoveForward(float Value);
    void MoveRight(float Value);
    void TurnAtRate(float Value);
    void LookUpAtRate(float Value);
    void StartJump();
    void StopJump();
    void StartSprint();
    void StopSprint();
    void StartCrouch();
    void StopCrouch();
    void Interact();
    void QuickSave();
    void QuickLoad();
    void DebugPreviousChapter();
    void DebugNextChapter();
    void DebugToggleParallelRoute();
    void DebugStartChapterByIndex(int32 ChapterIndex);

    UFUNCTION()
    void HandleCinematicStateChanged(bool bLocked);

    UFUNCTION()
    void HandleExperienceChanged(FName RouteId, FName EpisodeId, FName PlayableCharacterId);

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Camera")
    USpringArmComponent* CameraBoom;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Camera")
    UCameraComponent* FollowCamera;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Prototype")
    UStaticMeshComponent* PrototypeTorso;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Prototype")
    UStaticMeshComponent* PrototypeHead;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Prototype")
    UStaticMeshComponent* PrototypeHair;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Prototype")
    UStaticMeshComponent* PrototypeLeftArm;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Prototype")
    UStaticMeshComponent* PrototypeRightArm;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Prototype")
    UStaticMeshComponent* PrototypeLeftLeg;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Prototype")
    UStaticMeshComponent* PrototypeRightLeg;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Prototype")
    UStaticMeshComponent* PrototypeLeftFoot;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Prototype")
    UStaticMeshComponent* PrototypeRightFoot;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Movement")
    float WalkSpeed = 310.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Movement")
    float SprintSpeed = 475.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Interaction")
    float InteractionDistance = 370.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Camera")
    float BaseTurnRate = 45.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Camera")
    float BaseLookUpRate = 45.0f;

private:
    bool bCinematicInputLocked = false;
    float PrototypeWalkPhase = 0.0f;

    void ApplyPrototypeStyle();
    void UpdatePrototypeAnimation(float DeltaSeconds);
};
