#include "ShireHUD.h"
#include "ShireDialogueSubsystem.h"
#include "ShireQuestSubsystem.h"
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

    DrawRect(FLinearColor(0.02f, 0.03f, 0.02f, 0.65f), 22.0f, 20.0f, FMath::Min(510.0f, W - 44.0f), 92.0f);
    DrawText(TEXT("SHIRE JOURNEY  |  VISUAL PROXY R1"), FLinearColor(0.95f, 0.90f, 0.68f), 38.0f, 32.0f, MediumFont, 1.0f, false);

    UShireQuestSubsystem* Quests = nullptr;
    UShireDialogueSubsystem* Dialogue = nullptr;
    if (UGameInstance* GI = GetWorld()->GetGameInstance())
    {
        Quests = GI->GetSubsystem<UShireQuestSubsystem>();
        Dialogue = GI->GetSubsystem<UShireDialogueSubsystem>();
    }

    if (Quests)
    {
        DrawText(Quests->GetActiveQuestTitle().ToString(), FLinearColor::White, 38.0f, 60.0f, SmallFont, 1.0f, false);
        DrawText(Quests->GetActiveObjective().ToString(), FLinearColor(0.84f, 0.88f, 0.77f), 38.0f, 82.0f, SmallFont, 0.95f, false);
    }

    DrawText(TEXT("WASD Move  |  Shift Sprint  |  Ctrl Crouch  |  E Interact  |  F5 Save  |  F9 Load  |  F6/F7 Chapter Test"),
        FLinearColor(0.85f, 0.85f, 0.85f, 0.85f), 24.0f, H - 34.0f, SmallFont, 0.85f, false);

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
