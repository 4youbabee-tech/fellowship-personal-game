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

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    FName QuestId = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    int32 RequiredQuestStage = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    int32 QuestStageAfterInteraction = -1;

    // Optional transition used by story NPCs when an interaction completes one beat
    // and immediately activates the next film-continuity mission.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    FName NextQuestId = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    int32 NextQuestStage = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    bool bFollowPlayerAfterInteraction = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    float FollowDistance = 190.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Companion")
    float FollowSpeed = 240.0f;

    virtual void Interact_Implementation(AActor* Interactor) override;

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Prototype")
    UStaticMeshComponent* PrototypeTorso;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Prototype")
    UStaticMeshComponent* PrototypeHead;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Dialogue")
    int32 CurrentDialogueIndex = 0;

private:
    bool bFollowingPlayer = false;
};
