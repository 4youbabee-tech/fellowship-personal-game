#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "ShireStoryFlowSubsystem.generated.h"

class UShireQuestSubsystem;

// Defensive story-flow guardrails for chapter hand-offs that must never leave the
// player stranded at the end of a playable region. This does not replace normal
// world triggers; it verifies critical terminal quest states at runtime and also
// repairs compatible older save states when they are restored.
UCLASS()
class SHIREJOURNEY_API UShireStoryFlowSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

private:
    UPROPERTY()
    UShireQuestSubsystem* QuestSubsystem = nullptr;

    UFUNCTION()
    void HandleQuestStageChanged(FName QuestId, int32 NewStage);

    void EvaluateCriticalHandoff(FName QuestId, int32 NewStage);
};
