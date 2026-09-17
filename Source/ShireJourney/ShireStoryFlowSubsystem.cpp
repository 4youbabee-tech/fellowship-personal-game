#include "ShireStoryFlowSubsystem.h"

#include "ShireQuestSubsystem.h"
#include "Engine/GameInstance.h"

void UShireStoryFlowSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    Collection.InitializeDependency<UShireQuestSubsystem>();

    if (UGameInstance* GI = GetGameInstance())
    {
        QuestSubsystem = GI->GetSubsystem<UShireQuestSubsystem>();
        if (QuestSubsystem)
        {
            QuestSubsystem->OnQuestStageChanged.AddDynamic(this, &UShireStoryFlowSubsystem::HandleQuestStageChanged);

            // Repair critical end-of-region states from a restored save as soon as
            // the subsystem becomes active. Normal fresh games remain unchanged.
            EvaluateCriticalHandoff(QuestSubsystem->GetActiveQuestId(), QuestSubsystem->GetActiveQuestStage());
        }
    }
}

void UShireStoryFlowSubsystem::Deinitialize()
{
    if (QuestSubsystem)
    {
        QuestSubsystem->OnQuestStageChanged.RemoveDynamic(this, &UShireStoryFlowSubsystem::HandleQuestStageChanged);
        QuestSubsystem = nullptr;
    }

    Super::Deinitialize();
}

void UShireStoryFlowSubsystem::HandleQuestStageChanged(FName QuestId, int32 NewStage)
{
    EvaluateCriticalHandoff(QuestId, NewStage);
}

void UShireStoryFlowSubsystem::EvaluateCriticalHandoff(FName QuestId, int32 NewStage)
{
    if (!QuestSubsystem)
    {
        return;
    }

    // Chapter 1 terminal state: crossing to the far bank of Bucklebury Ferry.
    // The physical trigger sets FerryEscape to stage 2; the guard then performs
    // the chapter hand-off even if an older save or an incomplete trigger config
    // reaches this exact state.
    if (QuestId == TEXT("FerryEscape") && NewStage >= 2 && QuestSubsystem->GetCurrentChapterId() == TEXT("P1C01"))
    {
        QuestSubsystem->StartChapter(TEXT("P1C02"), TEXT("RoadToBree"), 0);
    }
}
