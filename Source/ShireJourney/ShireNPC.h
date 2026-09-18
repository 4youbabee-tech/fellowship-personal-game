#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "ShireInteractable.h"
#include "ShireNPC.generated.h"

class UStaticMeshComponent;

UCLASS()
class SHIREJOURNEY_API AShireNPC : public ACharacter, public IShireInteractable
{
    GENERATED_BODY()

public:
    AShireNPC();
    virtual void Tick(float DeltaSeconds) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NPC")
    FText DisplayName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Dialogue", meta=(MultiLine="true"))
    TArray<FText> DialogueLines;

    // Optional side-story flags reuse the persisted story-beat store without replacing
    // the currently active main quest. This keeps exploration optional and save-safe.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="SideStory")
    FName RequiredSideStoryBeat = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="SideStory")
    FName SideStoryBeatAfterInteraction = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="SideStory")
    FText SideStoryStartMessage;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    FName QuestId = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    int32 RequiredQuestStage = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    int32 QuestStageAfterInteraction = -1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    FName NextQuestId = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    int32 NextQuestStage = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    bool bFollowPlayerAfterInteraction = false;

    // -1 means choose a stable slot automatically from the companion name.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    int32 CompanionSlotIndex = -1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    float FollowDistance = 190.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    float FormationSpacing = 120.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    float FollowAcceptanceRadius = 70.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    float FollowSpeed = 240.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    float CatchUpDistance = 760.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    float TeleportCatchUpDistance = 2400.0f;

    virtual void Interact_Implementation(AActor* Interactor) override;

protected:
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

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Dialogue")
    int32 CurrentDialogueIndex = 0;

private:
    bool bFollowingPlayer = false;
    bool bCompanionFollowStateResolved = false;
    bool bVisualStyleApplied = false;
    bool bPrototypeMoving = false;
    float PrototypeWalkPhase = 0.0f;

    void ApplyPrototypeStyle();
    void UpdatePrototypeAnimation(float DeltaSeconds);
    int32 ResolveCompanionSlot() const;
    FVector GetFormationTarget(const APawn* PlayerPawn) const;
    void RestoreCompanionFollowState();
};
