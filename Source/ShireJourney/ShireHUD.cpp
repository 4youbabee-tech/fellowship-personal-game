#include "ShireHUD.h"
#include "ShireDialogueSubsystem.h"
#include "ShireQuestSubsystem.h"
#include "ShirePlayerCharacter.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"

void AShireHUD::DrawHUD()
{
    Super::DrawHUD();
    if (!Canvas || !GetWorld())
    {
        return;
    }

    const float W = Canvas->ClipX;
    const float H = Canvas->ClipY;
    UFont* SmallFont = GEngine ? GEngine->GetSmallFont() : nullptr;
    UFont* MediumFont = GEngine ? GEngine->GetMediumFont() : SmallFont;

    const float QuestCardW = FMath::Min(520.0f, W - 44.0f);
    DrawRect(FLinearColor(0.015f, 0.020f, 0.015f, 0.76f), 22.0f, 20.0f, QuestCardW, 106.0f);
    DrawRect(FLinearColor(0.76f, 0.57f, 0.22f, 0.92f), 22.0f, 20.0f, 4.0f, 106.0f);
    DrawText(TEXT("MIDDLE-EARTH JOURNEY"), FLinearColor(0.94f, 0.86f, 0.62f), 38.0f, 30.0f, MediumFont, 0.92f, false);

    UShireQuestSubsystem* Quests = nullptr;
    UShireDialogueSubsystem* Dialogue = nullptr;
    if (UGameInstance* GI = GetWorld()->GetGameInstance())
    {
        Quests = GI->GetSubsystem<UShireQuestSubsystem>();
        Dialogue = GI->GetSubsystem<UShireDialogueSubsystem>();
    }

    if (Quests)
    {
        const FString Context = FString::Printf(TEXT("%s  |  %s"),
            *Quests->GetPlayableCharacterId().ToString(),
            *Quests->GetCurrentEpisodeId().ToString());
        DrawText(Context, FLinearColor(0.70f, 0.76f, 0.63f), 38.0f, 54.0f, SmallFont, 0.82f, false);
        DrawText(Quests->GetActiveQuestTitle().ToString(), FLinearColor::White, 38.0f, 73.0f, SmallFont, 0.96f, false);
        DrawText(Quests->GetActiveObjective().ToString(), FLinearColor(0.82f, 0.86f, 0.76f), 38.0f, 95.0f, SmallFont, 0.86f, false);
    }

    AShirePlayerCharacter* Player =
        PlayerOwner ? Cast<AShirePlayerCharacter>(PlayerOwner->GetPawn()) : nullptr;
    const bool bCombat = Player && Player->IsCombatAvailable();

    if (bCombat)
    {
        const float HealthRatio = FMath::Clamp(
            Player->GetCurrentHealth() / FMath::Max(1.0f, Player->GetMaxHealth()), 0.0f, 1.0f);
        DrawRect(FLinearColor(0.03f, 0.03f, 0.03f, 0.78f), 24.0f, H - 72.0f, 220.0f, 18.0f);
        DrawRect(FLinearColor(0.52f, 0.08f, 0.055f, 0.94f), 26.0f, H - 70.0f, 216.0f * HealthRatio, 14.0f);
        DrawText(FString::Printf(TEXT("Health %d / %d"),
            FMath::RoundToInt(Player->GetCurrentHealth()),
            FMath::RoundToInt(Player->GetMaxHealth())),
            FLinearColor::White, 254.0f, H - 75.0f, SmallFont, 0.82f, false);
    }

    DrawText(
        bCombat
            ? TEXT("WASD Move  |  LMB Attack  |  Shift Sprint  |  Ctrl Crouch  |  E Interact  |  F5 Save  |  F9 Load")
            : TEXT("WASD Move  |  Shift Sprint  |  Ctrl Crouch  |  E Interact  |  F5 Save  |  F9 Load  |  F6/F7 Chapter  |  F8 Route"),
        FLinearColor(0.78f, 0.80f, 0.76f, 0.46f), 24.0f, H - 28.0f, SmallFont, 0.72f, false);

    const float Now = GetWorld()->GetTimeSeconds();

    bool bDrewQueuedSubtitle = false;
    if (Dialogue && Dialogue->IsDialoguePlaying())
    {
        const FShireDialogueLine Current = Dialogue->GetCurrentLine();
        if (!Current.Subtitle.IsEmpty())
        {
            const float BoxW = FMath::Min(760.0f, W - 60.0f);
            const float BoxX = (W - BoxW) * 0.5f;
            const float BoxY = H - 155.0f;
            DrawRect(FLinearColor(0.01f, 0.01f, 0.01f, 0.86f), BoxX, BoxY, BoxW, 95.0f);
            DrawText(Current.Speaker.ToString(), FLinearColor(0.96f, 0.82f, 0.45f), BoxX + 18.0f, BoxY + 14.0f, MediumFont, 1.0f, false);
            DrawText(Current.Subtitle.ToString(), FLinearColor::White, BoxX + 18.0f, BoxY + 46.0f, SmallFont, 1.0f, false);
            bDrewQueuedSubtitle = true;
        }
    }

    if (!bDrewQueuedSubtitle && Now < DialogueUntilTime && !DialogueLine.IsEmpty())
    {
        const float BoxW = FMath::Min(760.0f, W - 60.0f);
        const float BoxX = (W - BoxW) * 0.5f;
        const float BoxY = H - 155.0f;
        DrawRect(FLinearColor(0.01f, 0.01f, 0.01f, 0.82f), BoxX, BoxY, BoxW, 95.0f);
        DrawText(DialogueSpeaker.ToString(), FLinearColor(0.96f, 0.82f, 0.45f), BoxX + 18.0f, BoxY + 14.0f, MediumFont, 1.0f, false);
        DrawText(DialogueLine.ToString(), FLinearColor::White, BoxX + 18.0f, BoxY + 46.0f, SmallFont, 1.0f, false);
    }

    if (Now < AlertUntilTime && !AlertMessage.IsEmpty())
    {
        const float BoxW = FMath::Min(540.0f, W - 80.0f);
        const float BoxX = (W - BoxW) * 0.5f;
        DrawRect(FLinearColor(0.16f, 0.01f, 0.01f, 0.82f), BoxX, 132.0f, BoxW, 48.0f);
        DrawText(AlertMessage.ToString(), FLinearColor(1.0f, 0.76f, 0.72f), BoxX + 18.0f, 146.0f, MediumFont, 0.95f, false);
    }
}

void AShireHUD::ShowDialogue(const FText& Speaker, const FText& Line, float Duration)
{
    DialogueSpeaker = Speaker;
    DialogueLine = Line;
    DialogueUntilTime = GetWorld() ? GetWorld()->GetTimeSeconds() + FMath::Max(0.5f, Duration) : Duration;
}

void AShireHUD::ShowAlert(const FText& Message, float Duration)
{
    AlertMessage = Message;
    AlertUntilTime = GetWorld() ? GetWorld()->GetTimeSeconds() + FMath::Max(0.5f, Duration) : Duration;
}
