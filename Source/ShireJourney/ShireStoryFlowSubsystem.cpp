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
            QuestSubsystem->OnQuestStateRestored.AddDynamic(this, &UShireStoryFlowSubsystem::HandleQuestStateRestored);
        }
    }
}

void UShireStoryFlowSubsystem::Deinitialize()
{
    if (QuestSubsystem)
    {
        QuestSubsystem->OnQuestStateRestored.RemoveDynamic(this, &UShireStoryFlowSubsystem::HandleQuestStateRestored);
        QuestSubsystem = nullptr;
    }

    Super::Deinitialize();
}

void UShireStoryFlowSubsystem::HandleQuestStateRestored()
{
    RepairRestoredTerminalState();
}

void UShireStoryFlowSubsystem::RepairRestoredTerminalState()
{
    if (!QuestSubsystem)
    {
        return;
    }

    const FName ChapterId = QuestSubsystem->GetCurrentChapterId();
    const FName QuestId = QuestSubsystem->GetActiveQuestId();
    const int32 Stage = QuestSubsystem->GetActiveQuestStage();

    // These states are the terminal authored stages immediately before a chapter
    // hand-off. A normal playthrough transitions through the world trigger itself.
    // If an older/incomplete save captured the terminal state first, resume safely
    // at the opening quest of the next chapter instead of leaving the player stranded.
    if (ChapterId == TEXT("P1C01") && QuestId == TEXT("FerryEscape") && Stage >= 2)
    {
        QuestSubsystem->StartChapter(TEXT("P1C02"), TEXT("RoadToBree"), 0);
    }
    else if (ChapterId == TEXT("P1C02") && QuestId == TEXT("NightAttack") && Stage >= 2)
    {
        QuestSubsystem->StartChapter(TEXT("P1C03"), TEXT("RoadToWeathertop"), 0);
    }
    else if (ChapterId == TEXT("P1C03") && QuestId == TEXT("FlightToFord") && Stage >= 2)
    {
        QuestSubsystem->StartChapter(TEXT("P1C04"), TEXT("RivendellRecovery"), 0);
    }
    else if (ChapterId == TEXT("P1C04") && QuestId == TEXT("FellowshipForms") && Stage >= 2)
    {
        QuestSubsystem->StartChapter(TEXT("P1C05"), TEXT("SouthwardJourney"), 0);
    }
    else if (ChapterId == TEXT("P1C05") && QuestId == TEXT("WestGate") && Stage >= 2)
    {
        QuestSubsystem->StartChapter(TEXT("P1C06"), TEXT("MoriaDark"), 0);
    }
    else if (ChapterId == TEXT("P1C06") && QuestId == TEXT("BridgeOfKhazadDum") && Stage >= 3)
    {
        QuestSubsystem->StartChapter(TEXT("P1C07"), TEXT("LothlorienRest"), 0);
    }
    else if (ChapterId == TEXT("P1C07") && QuestId == TEXT("GaladrielFarewell") && Stage >= 2)
    {
        QuestSubsystem->StartChapter(TEXT("P1C08"), TEXT("AnduinJourney"), 0);
    }
}
