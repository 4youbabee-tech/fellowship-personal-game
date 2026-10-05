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

    // Route identity is repairable because the currently implemented routes each have
    // one canonical playable character. This prevents a malformed/legacy save from
    // loading Frodo into Isengard or Gandalf into the Frodo main route.
    if (QuestSubsystem->GetCurrentRouteId() == TEXT("GandalfParallel"))
    {
        if (QuestSubsystem->GetPlayableCharacterId() != TEXT("Gandalf"))
        {
            QuestSubsystem->StartExperience(
                TEXT("GandalfParallel"),
                TEXT("P1G01_Isengard"),
                TEXT("Gandalf"),
                TEXT("P1C01"),
                QuestId,
                Stage);
            return;
        }
    }
    else if (QuestSubsystem->GetCurrentRouteId() == TEXT("FrodoMain") &&
        QuestSubsystem->GetPlayableCharacterId() != TEXT("Frodo"))
    {
        QuestSubsystem->StartExperience(
            TEXT("FrodoMain"),
            QuestSubsystem->GetCurrentEpisodeId(),
            TEXT("Frodo"),
            ChapterId,
            QuestId,
            Stage);
        return;
    }

    // Terminal-state repair applies only after a chapter has been explicitly opened.
    // P1C01 FerryEscape stage 2 is intentionally a valid committed terminal state:
    // Bree/P1C02 remains owner-explicit and must not be opened by save restoration.
    if (ChapterId == TEXT("P1C02") && QuestId == TEXT("NightAttack") && Stage >= 2)
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
