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

protected:
    virtual void BeginPlay() override;

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
    void DebugStartChapterByIndex(int32 ChapterIndex);

    UFUNCTION()
    void HandleCinematicStateChanged(bool bLocked);

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Camera")
    USpringArmComponent* CameraBoom;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Camera")
    UCameraComponent* FollowCamera;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Prototype")
    UStaticMeshComponent* PrototypeTorso;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Prototype")
    UStaticMeshComponent* PrototypeHead;

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
};
