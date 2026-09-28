#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "ShirePlayerCharacter.generated.h"

class USpringArmComponent;
class UCameraComponent;
class UStaticMeshComponent;
class UShireFootstepComponent;
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

    // Internal transaction restore used by ChapterWorldRouter rollback. This does not write a save slot.
    void RestoreTransactionalPlayerState(float Health, float Stamina, float Resolve, int32 InSupplies);

    UFUNCTION(BlueprintPure, Category="Chronicle")
    bool IsChronicleOpen() const { return bChronicleOpen; }

    UFUNCTION(BlueprintPure, Category="Chronicle")
    int32 GetChronicleBrowseIndex() const { return ChronicleBrowseIndex; }

    UFUNCTION(BlueprintPure, Category="MapKnowledge")
    bool IsWorldMapOpen() const { return bWorldMapOpen; }

    UFUNCTION(BlueprintPure, Category="Settings|Graphics")
    bool IsGraphicsSettingsOpen() const { return bGraphicsSettingsOpen; }

    UFUNCTION(BlueprintPure, Category="Settings|Graphics")
    int32 GetGraphicsSettingsSelectionIndex() const { return GraphicsSettingsSelectionIndex; }

    UFUNCTION(BlueprintPure, Category="Movement")
    bool IsCrouchingForStealth() const { return bIsCrouched; }

    UFUNCTION(BlueprintCallable, Category="Save")
    bool SaveAutomaticCheckpoint(FName CheckpointId, bool bShowHUD = true);

    UFUNCTION(BlueprintCallable, Category="Save")
    bool RestoreAutomaticCheckpoint(bool bShowHUD = true);

    // Explicit CI-only disk roundtrip through the production snapshot/restore path.
    bool RunSaveRoundtripAudit();

#if !UE_BUILD_SHIPPING
    // W00 regression probes: exercise the production restore path and stale
    // checkpoint completion guard without exposing debug controls in shipping.
    bool RunLegacyTerminalRestoreAuditSetup();
    bool RunStaleCheckpointCompletionAudit();
    bool RunMalformedExperienceRestoreAuditSetup();
    bool RunQueuedCheckpointRevisionRaceAuditSetup();
    bool IsQueuedCheckpointRevisionRaceAuditComplete() const { return bCIAuditQueuedCheckpointRaceComplete; }
    bool DidQueuedCheckpointRevisionRaceAuditPass() const { return bCIAuditQueuedCheckpointRacePassed; }
#endif

    // Raised by ChapterWorldRouter before destination construction and released only
    // after committed-world publication. Gameplay mutation must stay inert meanwhile.
    void SetWorldTransitionHeld(bool bHeld) { bWorldTransitionHeld = bHeld; }
    bool IsWorldTransitionHeld() const { return bWorldTransitionHeld; }
    bool IsGameplayWorldCommitted() const;

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
    void ToggleWorldMap();
    void ToggleGraphicsSettings();
    void GraphicsSettingsPrevious();
    void GraphicsSettingsNext();
    void GraphicsSettingsDecrease();
    void GraphicsSettingsIncrease();
    void AdjustGraphicsSetting(int32 Delta);
    void QuickSave();
    void QuickLoad();
    void DebugPreviousChapter();
    void DebugNextChapter();
    void DebugToggleParallelRoute();
    void DebugStartChapterByIndex(int32 ChapterIndex);

    UFUNCTION()
    void HandleCinematicStateChanged(bool bLocked);

    UFUNCTION()
    void HandleStoryCameraCue(FName CameraCue);

    UFUNCTION()
    void HandleExperienceChanged(FName RouteId, FName EpisodeId, FName PlayableCharacterId);

    UFUNCTION()
    void HandleChapterChanged(FName PreviousChapterId, FName NewChapterId);

    void HandleProductionRigReady(FName CharacterId);
    void HandleChapterAssetsCommitted(FName ChapterId, FName RouteId);

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Camera")
    USpringArmComponent* CameraBoom;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Camera")
    UCameraComponent* FollowCamera;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Audio")
    UShireFootstepComponent* FootstepComponent;

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

    // Raw MouseX/MouseY input is already frame-relative; do not multiply it by DeltaSeconds.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Camera")
    float MouseLookSensitivity = 1.0f;

private:
    bool bCinematicInputLocked = false;
    bool bWorldTransitionHeld = true;
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
    bool bUsingSkeletalProductionRig = false;
    bool bSprintRequested = false;
    float CurrentStamina = 100.0f;
    float CurrentResolve = 100.0f;
    int32 Supplies = 3;
    float StaminaRegenDelayRemaining = 0.0f;
    bool bStaminaExhausted = false;
    bool bChronicleOpen = false;
    int32 ChronicleBrowseIndex = 0;
    bool bWorldMapOpen = false;
    bool bGraphicsSettingsOpen = false;
    int32 GraphicsSettingsSelectionIndex = 0;
    float PrototypeIdlePhase = 0.0f;
    FName PendingChapterCheckpointId = NAME_None;
    bool bPendingSaveRestoreTransform = false;
    FVector PendingSaveRestoreLocation = FVector::ZeroVector;
    FRotator PendingSaveRestoreRotation = FRotator::ZeroRotator;
    FName PendingSaveRestoreChapterId = NAME_None;
    FName PendingSaveRestoreRouteId = NAME_None;
    FName PendingSaveRestoreEpisodeId = NAME_None;
    FText PendingSaveRestoreSuccessMessage;
    bool bCheckpointSaveInFlight = false;
    bool bCheckpointSaveShowHUD = false;
    UPROPERTY()
    UShireSaveGame* CheckpointSaveInFlightSnapshot = nullptr;
    FName CheckpointSaveInFlightId = NAME_None;
    FName CheckpointSaveInFlightChapterId = NAME_None;
    FName CheckpointSaveInFlightRouteId = NAME_None;
    FName CheckpointSaveInFlightEpisodeId = NAME_None;
    uint32 CheckpointSaveInFlightWorldRevision = 0;

    // Coalesce to the latest queued checkpoint, but preserve the snapshot and
    // originating committed-world identity captured when that checkpoint was reached.
    UPROPERTY()
    UShireSaveGame* QueuedCheckpointSnapshot = nullptr;
    FName QueuedCheckpointSaveId = NAME_None;
    FName QueuedCheckpointChapterId = NAME_None;
    FName QueuedCheckpointRouteId = NAME_None;
    FName QueuedCheckpointEpisodeId = NAME_None;
    uint32 QueuedCheckpointWorldRevision = 0;
    bool bQueuedCheckpointShowHUD = false;
#if !UE_BUILD_SHIPPING
    int32 CIAuditCheckpointCallbacksToDefer = 0;
    bool bCIAuditQueuedCheckpointRaceActive = false;
    bool bCIAuditQueuedCheckpointRaceComplete = false;
    bool bCIAuditQueuedCheckpointRacePassed = false;
    bool bCIAuditQueuedCheckpointAnyEffects = false;
    bool bCIAuditQueuedCheckpointAllWritesSucceeded = true;
    int32 CIAuditQueuedCheckpointCompletions = 0;
    uint32 CIAuditQueuedCheckpointOriginRevision = 0;
    uint32 CIAuditQueuedCheckpointLastCompletionRevision = 0;
    float CIAuditQueuedCheckpointOriginalHealth = 100.0f;
    float CIAuditQueuedCheckpointOriginalStamina = 100.0f;
    float CIAuditQueuedCheckpointOriginalResolve = 100.0f;
    int32 CIAuditQueuedCheckpointOriginalSupplies = 0;
#endif
    bool bStoryCameraCueActive = false;
    float StoryCameraCueRemaining = 0.0f;
    float StoryCameraTargetArmLength = 260.0f;
    float StoryCameraTargetFOV = 78.0f;
    FVector StoryCameraTargetSocketOffset = FVector(0.0f, 28.0f, 10.0f);

    UShireSaveGame* CreateSaveSnapshot(FName CheckpointId, bool bCheckpointSnapshot) const;
    bool StartCheckpointSnapshotSave(
        UShireSaveGame* Snapshot,
        FName CheckpointId,
        bool bShowHUD,
        FName ChapterId,
        FName RouteId,
        FName EpisodeId,
        uint32 WorldRevision);
    void HandleCheckpointSaveComplete(const FString& SlotName, const int32 UserIndex, bool bSuccess);
    void FinalizeCheckpointSaveComplete(const FString& SlotName, const int32 UserIndex, bool bSuccess);
    bool RestoreSaveSnapshot(UShireSaveGame* Save, const FText& SuccessMessage);
    bool TryApplyPendingSaveRestoreTransform();
    bool IsCurrentWorldCommitted() const;
    bool TryApplyProductionRig(const FString& RigFolder);
    void ApplyPrototypeStyle();
    void UpdatePrototypeAnimation(float DeltaSeconds);
    void UpdatePlayerLife(float DeltaSeconds);
    void UpdateStoryCameraCue(float DeltaSeconds);
    float GetResolveTarget() const;
};