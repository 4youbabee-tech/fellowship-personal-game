#include "ShireGameMode.h"
#include "ChapterWorldRouter.h"
#include "LivingWorldDirector.h"
#include "ShireHUD.h"
#include "ShirePlayerCharacter.h"
#include "ShireQuestSubsystem.h"

#include "Engine/GameInstance.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/PlayerController.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

AShireGameMode::AShireGameMode()
{
    DefaultPawnClass = AShirePlayerCharacter::StaticClass();
    HUDClass = AShireHUD::StaticClass();
}

void AShireGameMode::BeginPlay()
{
    Super::BeginPlay();

    // Verification-only command-line override. It does not change normal player startup:
    // CI can boot every Part I runtime chapter independently and prove that its world
    // builder survives a real UE4.27 game startup before manual PIE acceptance.
    bool bAuditChapterApplied = false;
    FString AuditChapterValue;
    if (FParse::Value(FCommandLine::Get(), TEXT("AuditChapter="), AuditChapterValue))
    {
        const FName AuditChapterId(*AuditChapterValue);
        FName StartingQuestId = NAME_None;

        if (AuditChapterId == TEXT("P1C01")) StartingQuestId = TEXT("ShireArrival");
        else if (AuditChapterId == TEXT("P1C02")) StartingQuestId = TEXT("RoadToBree");
        else if (AuditChapterId == TEXT("P1C03")) StartingQuestId = TEXT("RoadToWeathertop");
        else if (AuditChapterId == TEXT("P1C04")) StartingQuestId = TEXT("RivendellRecovery");
        else if (AuditChapterId == TEXT("P1C05")) StartingQuestId = TEXT("SouthwardJourney");
        else if (AuditChapterId == TEXT("P1C06")) StartingQuestId = TEXT("MoriaDark");
        else if (AuditChapterId == TEXT("P1C07")) StartingQuestId = TEXT("LothlorienRest");
        else if (AuditChapterId == TEXT("P1C08")) StartingQuestId = TEXT("AnduinJourney");

        UGameInstance* GI = GetGameInstance();
        UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
        if (Quests && StartingQuestId != NAME_None)
        {
            Quests->StartChapter(AuditChapterId, StartingQuestId, 0);
            bAuditChapterApplied = true;
            UE_LOG(
                LogTemp,
                Display,
                TEXT("ShireChapterAudit: requested=%s quest=%s"),
                *AuditChapterId.ToString(),
                *StartingQuestId.ToString());
        }
        else
        {
            UE_LOG(
                LogTemp,
                Error,
                TEXT("ShireChapterAudit: invalid or unavailable AuditChapter=%s"),
                *AuditChapterValue);
        }
    }

    if (FParse::Param(FCommandLine::Get(), TEXT("AuditState")))
    {
        UGameInstance* GI = GetGameInstance();
        UShireQuestSubsystem* Quests = GI ? GI->GetSubsystem<UShireQuestSubsystem>() : nullptr;
        if (!Quests)
        {
            UE_LOG(LogTemp, Error, TEXT("ShireStateAudit: subsystem=missing"));
        }
        else
        {
            Quests->StartExperience(
                TEXT("FrodoMain"), TEXT("P1C03_Main"), TEXT("Frodo"),
                TEXT("P1C03"), TEXT("RoadToWeathertop"), 2);
            Quests->TriggerStoryBeat(TEXT("CI_STATE_AUDIT_BEAT"));

            Quests->StartExperience(
                TEXT("GandalfParallel"), TEXT("P1G01_Isengard"), TEXT("Gandalf"),
                TEXT("P1G01"), TEXT("IsengardCounsel"), 1);

            Quests->StartExperience(
                TEXT("FrodoMain"), TEXT("P1C03_Main"), TEXT("Frodo"),
                TEXT("P1C03"), TEXT("RoadToWeathertop"), 0);

            const bool bRouteRestored =
                Quests->GetCurrentRouteId() == TEXT("FrodoMain") &&
                Quests->GetCurrentChapterId() == TEXT("P1C03") &&
                Quests->GetQuestStage(TEXT("RoadToWeathertop")) == 2 &&
                Quests->HasStoryBeatTriggered(TEXT("CI_STATE_AUDIT_BEAT"));

            UE_LOG(
                LogTemp,
                bRouteRestored ? Display : Error,
                TEXT("ShireStateAudit: route-roundtrip=%s chapter=%s questStage=%d beat=%s"),
                bRouteRestored ? TEXT("PASS") : TEXT("FAIL"),
                *Quests->GetCurrentChapterId().ToString(),
                Quests->GetQuestStage(TEXT("RoadToWeathertop")),
                Quests->HasStoryBeatTriggered(TEXT("CI_STATE_AUDIT_BEAT")) ? TEXT("yes") : TEXT("no"));
        }
    }

    // Prototype chapter worlds are spawned through a router so Chapter 1 can hand off
    // to Bree without loading both regions at the same time.
    GetWorld()->SpawnActor<AChapterWorldRouter>(FVector::ZeroVector, FRotator::ZeroRotator);
    GetWorld()->SpawnActor<ALivingWorldDirector>(FVector::ZeroVector, FRotator::ZeroRotator);
    UE_LOG(LogTemp, Display, TEXT("ShirePlayableStartup: GameMode ready; router and living-world director spawned"));

    // Normal launches preserve the authored P1C01 placement. Audit launches let the
    // chapter router own placement so P1C02-P1C08 are not teleported back into Shire.
    if (!bAuditChapterApplied)
    {
        APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
        if (PC)
        {
            if (!PC->GetPawn())
            {
                RestartPlayerAtTransform(PC, FTransform(FRotator(0.0f, 0.0f, 0.0f), FVector(-2410.0f, -120.0f, 130.0f)));
            }
            else
            {
                PC->GetPawn()->SetActorLocationAndRotation(FVector(-2410.0f, -120.0f, 130.0f), FRotator(0.0f, 0.0f, 0.0f));
            }
        }
    }
}
