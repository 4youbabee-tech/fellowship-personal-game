#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "ShireStoryFlowSubsystem.generated.h"

class UShireQuestSubsystem;

// Defensive story-flow guardrails for chapter hand-offs that must never leave the
// player stranded at the end of a playable region. Normal gameplay still uses the
// authored world triggers; this subsystem only repairs compatible restored saves
// that ended at a terminal quest stage before the next chapter was activated.
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
    void HandleQuestStateRestored();

    void RepairRestoredTerminalState();
};
