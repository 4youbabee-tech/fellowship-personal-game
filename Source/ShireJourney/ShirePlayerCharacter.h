#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "ShirePlayerCharacter.generated.h"

class USpringArmComponent;
class UCameraComponent;
class UStaticMeshComponent;
class UShireSaveGame;

UCLASS()
class SHIREJOURNEY_API AShirePlayerCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AShirePlayerCharacter();
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
    virtual void Tick(float DeltaSeconds) override;
    virtual float TakeDamage(float DamageAmount, struct FDamageEvent const& DamageEvent,
        class AController* EventInstigator, AActor* DamageCauser) override;

    UFUNCTION(BlueprintPure, Category="Combat")
    float GetCurrentHealth() const { return CurrentHealth; }

    UFUNCTION(BlueprintPure, Category="Combat")
    float GetMaxHealth() const { return MaxHealth; }

    UFUNCTION(BlueprintPure, Category="Combat")
    bool IsCombatAvailable() const;

    UFUNCTION(BlueprintPure, Category="PlayerLife")
    float GetCurrentStamina() const { return CurrentStamina; }

    UFUNCTION(BlueprintPure, Category="PlayerLife")
    float GetMaxStamina() const { return MaxStamina; }

    UFUNCTION(BlueprintPure, Category="PlayerLife")
    float GetCurrentResolve() const { return CurrentResolve; }

    UFUNCTION(BlueprintPure, Category="PlayerLife")
    float GetMaxResolve() const { return MaxResolve; }

    UFUNCTION(BlueprintPure, Category="PlayerLife")
    int32 GetSupplies() const { return Supplies; }

    UFUNCTION(BlueprintCallable, Category="PlayerLife")
    void GrantSupplies(int32 Amount);

    UFUNCTION(BlueprintPure, Category="Chronicle")
    bool IsChronicleOpen() const { return bChronicleOpen; }

    UFUNCTION(BlueprintPure, Category="Chronicle")
    int32 GetChronicleBrowseIndex() const { return ChronicleBrowseIndex; }

    UFUNCTION(BlueprintPure, Category="Movement")
    bool IsCrouchingForStealth() const { return bIsCrouched; }

    UFUNCTION(BlueprintCallable, Category="Save")
    bool SaveAutomaticCheckpoint(FName CheckpointId, bool bShowHUD = true);

    UFUNCTION(BlueprintCallable, Category="Save")
    bool RestoreAutomaticCheckpoint(bool bShowHUD = true);

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
    void PrimaryAttack();
    void UseSupply();
    void ToggleChronicle();
    void ChroniclePrevious();
    void ChronicleNext();
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

    UFUNCTION()
    void HandleChapterChanged(FName PreviousChapterId, FName NewChapterId);

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

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Prototype")
    UStaticMeshComponent* PrototypeWeapon;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Prototype")
    UStaticMeshComponent* PrototypeCloak;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Prototype")
    UStaticMeshComponent* PrototypeHat;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Prototype")
    UStaticMeshComponent* PrototypeBeard;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Prototype")
    UStaticMeshComponent* PrototypeLeftEye;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Prototype")
    UStaticMeshComponent* PrototypeRightEye;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Prototype")
    UStaticMeshComponent* PrototypeMouth;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Prototype")
    UStaticMeshComponent* PrototypeSatchel;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat")
    float MaxHealth = 100.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat")
    float AttackDamage = 26.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat")
    float AttackRange = 175.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Combat")
    float AttackCooldown = 0.55f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Movement")
    float WalkSpeed = 310.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Movement")
    float SprintSpeed = 475.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="PlayerLife")
    float MaxStamina = 100.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="PlayerLife")
    float SprintStaminaDrainPerSecond = 18.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="PlayerLife")
    float StaminaRegenPerSecond = 16.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="PlayerLife")
    float MaxResolve = 100.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="PlayerLife")
    float ResolveRecoveryPerSecond = 7.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="PlayerLife")
    int32 MaxSupplies = 5;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Interaction")
    float InteractionDistance = 370.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Camera")
    float BaseTurnRate = 45.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Camera")
    float BaseLookUpRate = 45.0f;

private:
    bool bCinematicInputLocked = false;
    float PrototypeWalkPhase = 0.0f;
    float CurrentHealth = 100.0f;
    float AttackCooldownRemaining = 0.0f;
    float AttackVisualRemaining = 0.0f;
    float PrototypeTorsoBaseZ = -4.0f;
    float PrototypeHeadBaseZ = 39.0f;
    float PrototypeHairBaseZ = 47.0f;
    bool bPrototypeIsGandalf = false;
    FName PrototypeMotionProfile = TEXT("HOBBIT");
    bool bUsingProductionCharacter = false;
    bool bSprintRequested = false;
    float CurrentStamina = 100.0f;
    float CurrentResolve = 100.0f;
    int32 Supplies = 3;
    float StaminaRegenDelayRemaining = 0.0f;
    bool bStaminaExhausted = false;
    bool bChronicleOpen = false;
    int32 ChronicleBrowseIndex = 0;
    float PrototypeIdlePhase = 0.0f;
    FName PendingChapterCheckpointId = NAME_None;

    UShireSaveGame* CreateSaveSnapshot(FName CheckpointId, bool bCheckpointSnapshot) const;
    bool RestoreSaveSnapshot(UShireSaveGame* Save, const FText& SuccessMessage);
    void ApplyPrototypeStyle();
    void UpdatePrototypeAnimation(float DeltaSeconds);
    void UpdatePlayerLife(float DeltaSeconds);
    float GetResolveTarget() const;
};
