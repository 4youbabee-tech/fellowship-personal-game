#include "ShireHUD.h"
#include "ShireDialogueSubsystem.h"
#include "ShireQuestSubsystem.h"
#include "ShirePlayerCharacter.h"
#include "ShireGameUserSettings.h"
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

    const auto DrawWrappedText = [this](
        const FString& Text,
        const FLinearColor& Color,
        float X,
        float Y,
        float MaxWidth,
        UFont* Font,
        float Scale,
        int32 MaxLines)
    {
        TArray<FString> Words;
        Text.ParseIntoArrayWS(Words);
        FString Line;
        int32 LinesDrawn = 0;
        const float LineHeight = 18.0f * Scale;

        for (const FString& Word : Words)
        {
            const FString Candidate = Line.IsEmpty() ? Word : Line + TEXT(" ") + Word;
            float TextW = 0.0f;
            float TextH = 0.0f;
            GetTextSize(Candidate, TextW, TextH, Font, Scale);

            if (!Line.IsEmpty() && TextW > MaxWidth)
            {
                DrawText(Line, Color, X, Y + LinesDrawn * LineHeight, Font, Scale, false);
                ++LinesDrawn;
                if (LinesDrawn >= MaxLines)
                {
                    return;
                }
                Line = Word;
            }
            else
            {
                Line = Candidate;
            }
        }

        if (!Line.IsEmpty() && LinesDrawn < MaxLines)
        {
            DrawText(Line, Color, X, Y + LinesDrawn * LineHeight, Font, Scale, false);
        }
    };

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
            *Quests->GetCurrentPrimaryRegionName());
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

    if (Player)
    {
        const float StaminaRatio = FMath::Clamp(
            Player->GetCurrentStamina() / FMath::Max(1.0f, Player->GetMaxStamina()), 0.0f, 1.0f);
        const float ResolveRatio = FMath::Clamp(
            Player->GetCurrentResolve() / FMath::Max(1.0f, Player->GetMaxResolve()), 0.0f, 1.0f);
        const float LifeY = bCombat ? H - 118.0f : H - 92.0f;

        DrawRect(FLinearColor(0.03f, 0.03f, 0.03f, 0.72f), 24.0f, LifeY, 180.0f, 12.0f);
        DrawRect(FLinearColor(0.18f, 0.46f, 0.22f, 0.90f), 26.0f, LifeY + 2.0f, 176.0f * StaminaRatio, 8.0f);
        DrawText(FString::Printf(TEXT("Stamina %d / %d"),
            FMath::RoundToInt(Player->GetCurrentStamina()),
            FMath::RoundToInt(Player->GetMaxStamina())),
            FLinearColor(0.82f, 0.90f, 0.78f), 214.0f, LifeY - 4.0f, SmallFont, 0.72f, false);

        DrawRect(FLinearColor(0.03f, 0.03f, 0.03f, 0.72f), 24.0f, LifeY + 18.0f, 180.0f, 12.0f);
        DrawRect(FLinearColor(0.40f, 0.34f, 0.62f, 0.90f), 26.0f, LifeY + 20.0f, 176.0f * ResolveRatio, 8.0f);
        DrawText(FString::Printf(TEXT("Resolve %d / %d  |  Supplies %d"),
            FMath::RoundToInt(Player->GetCurrentResolve()),
            FMath::RoundToInt(Player->GetMaxResolve()),
            Player->GetSupplies()),
            FLinearColor(0.84f, 0.82f, 0.94f), 214.0f, LifeY + 14.0f, SmallFont, 0.72f, false);

        if (Quests)
        {
            DrawText(FString::Printf(TEXT("Journey %d  |  Fellowship %d"),
                Quests->GetJourneyInsight(), Quests->GetFellowshipBond()),
                FLinearColor(0.76f, 0.80f, 0.70f, 0.72f),
                24.0f, LifeY - 21.0f, SmallFont, 0.70f, false);
            DrawText(FString::Printf(TEXT("Chronicle %d  |  Regions %d"),
                Quests->GetChronicleCount(), Quests->GetKnownRegionCount()),
                FLinearColor(0.70f, 0.76f, 0.68f, 0.68f),
                24.0f, LifeY - 39.0f, SmallFont, 0.68f, false);
        }
    }

    if (Player && Player->IsChronicleOpen() && Quests)
    {
        const float PanelW = FMath::Min(500.0f, W - 80.0f);
        const float PanelH = FMath::Min(560.0f, H - 120.0f);
        const float PanelX = W - PanelW - 24.0f;
        const float PanelY = 118.0f;
        DrawRect(FLinearColor(0.012f, 0.018f, 0.013f, 0.95f), PanelX, PanelY, PanelW, PanelH);
        DrawRect(FLinearColor(0.76f, 0.57f, 0.22f, 0.94f), PanelX, PanelY, 4.0f, PanelH);

        DrawText(TEXT("CHRONICLE & JOURNEY"),
            FLinearColor(0.95f, 0.86f, 0.62f),
            PanelX + 18.0f, PanelY + 14.0f, MediumFont, 0.92f, false);
        DrawText(FString::Printf(TEXT("Entries %d  |  Known regions %d  |  Journey %d"),
            Quests->GetChronicleCount(), Quests->GetKnownRegionCount(), Quests->GetJourneyInsight()),
            FLinearColor(0.76f, 0.82f, 0.72f),
            PanelX + 18.0f, PanelY + 42.0f, SmallFont, 0.78f, false);

        float Y = PanelY + 72.0f;
        const TArray<FName>& Entries = Quests->GetChronicleEntryIds();
        if (Entries.Num() > 0)
        {
            const int32 SelectedIndex =
                FMath::Clamp(Player->GetChronicleBrowseIndex(), 0, Entries.Num() - 1);
            const FName SelectedEntry = Entries[SelectedIndex];
            DrawText(
                FString::Printf(TEXT("ENTRY %d / %d    [  ] Browse"), SelectedIndex + 1, Entries.Num()),
                FLinearColor(0.93f, 0.78f, 0.43f),
                PanelX + 18.0f, Y, SmallFont, 0.78f, false);
            Y += 23.0f;
            DrawText(
                Quests->GetChronicleEntryDisplayLabel(SelectedEntry),
                FLinearColor(0.94f, 0.91f, 0.80f),
                PanelX + 18.0f, Y, MediumFont, 0.88f, false);
            Y += 25.0f;
            DrawText(
                Quests->GetChronicleEntryContextLabel(SelectedEntry),
                FLinearColor(0.70f, 0.80f, 0.70f),
                PanelX + 18.0f, Y, SmallFont, 0.72f, false);
            Y += 30.0f;
        }
        else
        {
            DrawText(TEXT("No Chronicle entries discovered yet."),
                FLinearColor(0.76f, 0.82f, 0.72f),
                PanelX + 18.0f, Y, SmallFont, 0.78f, false);
            Y += 34.0f;
        }

        DrawText(TEXT("PROGRESSION"),
            FLinearColor(0.93f, 0.78f, 0.43f),
            PanelX + 18.0f, Y, SmallFont, 0.82f, false);
        Y += 22.0f;

        const FName Tracks[] = {
            TEXT("WAYFINDING"), TEXT("PERCEPTION"), TEXT("QUIET_STEP"), TEXT("CAMPCRAFT"),
            TEXT("FELLOWSHIP"), TEXT("LORE"), TEXT("RESOLVE")
        };
        for (const FName Track : Tracks)
        {
            DrawText(
                FString::Printf(TEXT("%s  Rank %d  XP %d"),
                    *Track.ToString(),
                    Quests->GetProgressionRank(Track),
                    Quests->GetProgressionXP(Track)),
                FLinearColor(0.82f, 0.84f, 0.78f),
                PanelX + 26.0f, Y, SmallFont, 0.70f, false);
            Y += 18.0f;
        }

        Y += 6.0f;
        DrawText(TEXT("KNOWN MAP REGIONS"),
            FLinearColor(0.93f, 0.78f, 0.43f),
            PanelX + 18.0f, Y, SmallFont, 0.82f, false);
        Y += 22.0f;

        const TArray<FName>& Regions = Quests->GetKnownMapRegionIds();
        const int32 FirstRegion = FMath::Max(0, Regions.Num() - 6);
        for (int32 RegionIndex = FirstRegion; RegionIndex < Regions.Num(); ++RegionIndex)
        {
            DrawText(
                Quests->GetKnownMapRegionDisplayLabel(Regions[RegionIndex]),
                FLinearColor(0.72f, 0.80f, 0.72f),
                PanelX + 26.0f, Y, SmallFont, 0.68f, false);
            Y += 17.0f;
        }

        DrawText(TEXT("C Close   [ Previous   ] Next"),
            FLinearColor(0.62f, 0.68f, 0.61f),
            PanelX + 18.0f, PanelY + PanelH - 24.0f, SmallFont, 0.66f, false);
    }

    if (Player && Player->IsWorldMapOpen() && Quests)
    {
        const float MapW = FMath::Min(760.0f, W - 70.0f);
        const float MapH = FMath::Min(560.0f, H - 105.0f);
        const float MapX = (W - MapW) * 0.5f;
        const float MapY = 72.0f;

        DrawRect(FLinearColor(0.028f, 0.026f, 0.019f, 0.97f), MapX, MapY, MapW, MapH);
        DrawRect(FLinearColor(0.71f, 0.55f, 0.28f, 0.94f), MapX, MapY, 4.0f, MapH);
        DrawText(TEXT("JOURNEY MAP"),
            FLinearColor(0.95f, 0.87f, 0.67f),
            MapX + 18.0f, MapY + 13.0f, MediumFont, 0.96f, false);
        DrawText(
            FString::Printf(TEXT("%s  |  %s"),
                *Quests->GetCurrentPrimaryRegionName(),
                *Quests->GetCurrentMacroRegionName()),
            FLinearColor(0.78f, 0.80f, 0.67f),
            MapX + 18.0f, MapY + 40.0f, SmallFont, 0.78f, false);

        const FString Landmarks = Quests->GetCurrentLandmarkSummary();
        if (!Landmarks.IsEmpty())
        {
            DrawText(
                FString::Printf(TEXT("Route landmarks: %s"), *Landmarks),
                FLinearColor(0.66f, 0.72f, 0.60f),
                MapX + 18.0f, MapY + 59.0f, SmallFont, 0.66f, false);
        }

        const float PlotX = MapX + 44.0f;
        const float PlotY = MapY + 92.0f;
        const float PlotW = MapW - 88.0f;
        const float PlotH = MapH - 136.0f;
        DrawRect(FLinearColor(0.055f, 0.052f, 0.038f, 0.82f), PlotX, PlotY, PlotW, PlotH);

        const TArray<FShireWorldMapNodeDefinition>& Nodes = Quests->GetWorldMapNodes();
        const TArray<FShireWorldMapEdgeDefinition>& Edges = Quests->GetWorldMapEdges();

        auto NodePosition = [PlotX, PlotY, PlotW, PlotH](const FShireWorldMapNodeDefinition& Node)
        {
            return FVector2D(
                PlotX + FMath::Clamp(Node.X, 0.0f, 1.0f) * PlotW,
                PlotY + FMath::Clamp(Node.Y, 0.0f, 1.0f) * PlotH);
        };

        auto FindNode = [&Nodes](FName NodeId) -> const FShireWorldMapNodeDefinition*
        {
            for (const FShireWorldMapNodeDefinition& Node : Nodes)
            {
                if (Node.NodeId == NodeId)
                {
                    return &Node;
                }
            }
            return nullptr;
        };

        for (const FShireWorldMapEdgeDefinition& Edge : Edges)
        {
            const FShireWorldMapNodeDefinition* From = FindNode(Edge.FromNodeId);
            const FShireWorldMapNodeDefinition* To = FindNode(Edge.ToNodeId);
            if (!From || !To ||
                !Quests->IsWorldMapNodeVisible(From->NodeId) ||
                !Quests->IsWorldMapNodeVisible(To->NodeId))
            {
                continue;
            }

            const FVector2D A = NodePosition(*From);
            const FVector2D B = NodePosition(*To);
            DrawLine(A.X, A.Y, B.X, B.Y, FLinearColor(0.52f, 0.44f, 0.27f, 0.72f), 2.0f);
        }

        const FName CurrentNode = Quests->GetCurrentWorldMapNodeId();
        for (const FShireWorldMapNodeDefinition& Node : Nodes)
        {
            if (!Quests->IsWorldMapNodeVisible(Node.NodeId))
            {
                continue;
            }

            const FVector2D P = NodePosition(Node);
            const bool bCurrent = Node.NodeId == CurrentNode;
            const float MarkerSize = bCurrent ? 10.0f : 7.0f;
            DrawRect(
                bCurrent
                    ? FLinearColor(0.92f, 0.70f, 0.28f, 1.0f)
                    : FLinearColor(0.70f, 0.74f, 0.58f, 0.90f),
                P.X - MarkerSize * 0.5f,
                P.Y - MarkerSize * 0.5f,
                MarkerSize,
                MarkerSize);

            DrawText(
                Node.DisplayName,
                bCurrent
                    ? FLinearColor(0.98f, 0.88f, 0.62f)
                    : FLinearColor(0.76f, 0.79f, 0.68f),
                P.X + 7.0f,
                P.Y - 7.0f,
                SmallFont,
                bCurrent ? 0.64f : 0.56f,
                false);
        }

        DrawText(TEXT("M Close  |  Undiscovered future chapters stay hidden"),
            FLinearColor(0.61f, 0.63f, 0.55f),
            MapX + 18.0f, MapY + MapH - 23.0f, SmallFont, 0.65f, false);
    }

    if (Player && Player->IsGraphicsSettingsOpen())
    {
        UShireGameUserSettings* Settings =
            UShireGameUserSettings::GetShireGameUserSettings();
        if (Settings)
        {
            const auto QualityLabel = [](int32 Quality) -> FString
            {
                switch (FMath::Clamp(Quality, 0, 3))
                {
                case 0: return TEXT("Low");
                case 1: return TEXT("Medium");
                case 2: return TEXT("High");
                case 3: return TEXT("Epic");
                default: return TEXT("Custom");
                }
            };

            float ScaleNormalized = 1.0f;
            float ScaleValue = 100.0f;
            float MinScale = 70.0f;
            float MaxScale = 100.0f;
            Settings->GetResolutionScaleInformationEx(
                ScaleNormalized, ScaleValue, MinScale, MaxScale);
            (void)ScaleNormalized;

            const FIntPoint Resolution = Settings->GetScreenResolution();
            FString WindowMode = TEXT("Windowed");
            if (Settings->GetFullscreenMode() == EWindowMode::Fullscreen)
            {
                WindowMode = TEXT("Fullscreen");
            }
            else if (Settings->GetFullscreenMode() == EWindowMode::WindowedFullscreen)
            {
                WindowMode = TEXT("Borderless");
            }

            const float PanelW = FMath::Min(650.0f, W - 70.0f);
            const float PanelH = FMath::Min(610.0f, H - 80.0f);
            const float PanelX = (W - PanelW) * 0.5f;
            const float PanelY = (H - PanelH) * 0.5f;

            DrawRect(FLinearColor(0.005f, 0.009f, 0.006f, 0.96f), PanelX, PanelY, PanelW, PanelH);
            DrawRect(FLinearColor(0.76f, 0.57f, 0.22f, 0.98f), PanelX, PanelY, 5.0f, PanelH);
            DrawText(TEXT("GRAPHICS / VIDEO"),
                FLinearColor(0.96f, 0.87f, 0.64f),
                PanelX + 24.0f, PanelY + 20.0f, MediumFont, 1.05f, false);
            DrawText(
                FString::Printf(TEXT("%dx%d  |  %s  |  DX11"),
                    Resolution.X, Resolution.Y, *WindowMode),
                FLinearColor(0.68f, 0.74f, 0.66f),
                PanelX + 24.0f, PanelY + 51.0f, SmallFont, 0.76f, false);

            const FString FrameLimit =
                Settings->GetFrameRateLimit() <= 0.5f
                    ? TEXT("Unlimited")
                    : FString::Printf(TEXT("%.0f FPS"), Settings->GetFrameRateLimit());

            const FString Labels[] = {
                TEXT("Overall Quality"),
                TEXT("Render Scale"),
                TEXT("View Distance"),
                TEXT("Anti-Aliasing"),
                TEXT("Shadows"),
                TEXT("Post Processing"),
                TEXT("Textures"),
                TEXT("Effects"),
                TEXT("Foliage"),
                TEXT("VSync"),
                TEXT("Frame Limit")
            };
            const FString Values[] = {
                Settings->GetShireGraphicsPresetLabel().ToString(),
                FString::Printf(TEXT("%.0f%% (%.0f-%.0f)"), ScaleValue, MinScale, MaxScale),
                QualityLabel(Settings->GetViewDistanceQuality()),
                QualityLabel(Settings->GetAntiAliasingQuality()),
                QualityLabel(Settings->GetShadowQuality()),
                QualityLabel(Settings->GetPostProcessingQuality()),
                QualityLabel(Settings->GetTextureQuality()),
                QualityLabel(Settings->GetVisualEffectQuality()),
                QualityLabel(Settings->GetFoliageQuality()),
                Settings->IsVSyncEnabled() ? TEXT("On") : TEXT("Off"),
                FrameLimit
            };

            float RowY = PanelY + 92.0f;
            for (int32 Index = 0; Index < UE_ARRAY_COUNT(Labels); ++Index)
            {
                const bool bSelected =
                    Index == Player->GetGraphicsSettingsSelectionIndex();
                if (bSelected)
                {
                    DrawRect(
                        FLinearColor(0.20f, 0.18f, 0.10f, 0.88f),
                        PanelX + 18.0f, RowY - 5.0f, PanelW - 36.0f, 34.0f);
                }

                DrawText(
                    Labels[Index],
                    bSelected
                        ? FLinearColor(0.98f, 0.90f, 0.66f)
                        : FLinearColor(0.78f, 0.82f, 0.74f),
                    PanelX + 32.0f, RowY, SmallFont, 0.84f, false);
                DrawText(
                    Values[Index],
                    bSelected
                        ? FLinearColor::White
                        : FLinearColor(0.78f, 0.80f, 0.76f),
                    PanelX + PanelW - 190.0f, RowY, SmallFont, 0.84f, false);
                RowY += 37.0f;
            }

            DrawText(
                TEXT("Recommended = image-first default  |  High/Ultra = stronger-hardware headroom"),
                FLinearColor(0.66f, 0.70f, 0.63f),
                PanelX + 24.0f, PanelY + PanelH - 58.0f, SmallFont, 0.66f, false);
            DrawText(
                TEXT("F10 Close   Up/Down Select   Left/Right Change"),
                FLinearColor(0.86f, 0.78f, 0.56f),
                PanelX + 24.0f, PanelY + PanelH - 31.0f, SmallFont, 0.72f, false);
        }
    }

    DrawText(
        Player && Player->IsGraphicsSettingsOpen()
            ? TEXT("GRAPHICS / VIDEO  |  F10 Close  |  Arrow keys adjust")
            : (bCombat
                ? TEXT("WASD Move  |  LMB Attack  |  Shift Sprint  |  E Interact  |  R Supply  |  C Chronicle  |  M Map  |  F10 Graphics  |  F5/F9 Save/Load")
                : TEXT("WASD Move  |  Shift Sprint  |  E Interact  |  R Supply  |  C Chronicle  |  M Map  |  F10 Graphics  |  F5/F9 Save/Load  |  F6-F8 Debug")),
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
            const float BoxY = H - 188.0f;
            DrawRect(FLinearColor(0.01f, 0.01f, 0.01f, 0.86f), BoxX, BoxY, BoxW, 126.0f);
            DrawText(Current.Speaker.ToString(), FLinearColor(0.96f, 0.82f, 0.45f), BoxX + 18.0f, BoxY + 14.0f, MediumFont, 1.0f, false);
            DrawWrappedText(Current.Subtitle.ToString(), FLinearColor::White,
                BoxX + 18.0f, BoxY + 46.0f, BoxW - 36.0f, SmallFont, 1.0f, 4);
            bDrewQueuedSubtitle = true;
        }
    }

    if (!bDrewQueuedSubtitle && Now < DialogueUntilTime && !DialogueLine.IsEmpty())
    {
        const float BoxW = FMath::Min(760.0f, W - 60.0f);
        const float BoxX = (W - BoxW) * 0.5f;
        const float BoxY = H - 188.0f;
        DrawRect(FLinearColor(0.01f, 0.01f, 0.01f, 0.82f), BoxX, BoxY, BoxW, 126.0f);
        DrawText(DialogueSpeaker.ToString(), FLinearColor(0.96f, 0.82f, 0.45f), BoxX + 18.0f, BoxY + 14.0f, MediumFont, 1.0f, false);
        DrawWrappedText(DialogueLine.ToString(), FLinearColor::White,
            BoxX + 18.0f, BoxY + 46.0f, BoxW - 36.0f, SmallFont, 1.0f, 4);
    }

    if (Now < AlertUntilTime && !AlertMessage.IsEmpty())
    {
        const float BoxW = FMath::Min(540.0f, W - 80.0f);
        const float BoxX = (W - BoxW) * 0.5f;
        DrawRect(FLinearColor(0.16f, 0.01f, 0.01f, 0.82f), BoxX, 132.0f, BoxW, 48.0f);
        DrawText(AlertMessage.ToString(), FLinearColor(1.0f, 0.76f, 0.72f), BoxX + 18.0f, 146.0f, MediumFont, 0.95f, false);
    }

    if (Now < DiscoveryUntilTime && !DiscoveryTitle.IsEmpty())
    {
        const float BoxW = FMath::Min(340.0f, W - 60.0f);
        const float BoxX = W - BoxW - 24.0f;
        const float BoxY = 24.0f;
        DrawRect(FLinearColor(0.025f, 0.035f, 0.025f, 0.88f), BoxX, BoxY, BoxW, 72.0f);
        DrawRect(FLinearColor(0.76f, 0.57f, 0.22f, 0.94f), BoxX, BoxY, 4.0f, 72.0f);
        DrawText(
            FString::Printf(TEXT("Discovered: %s"), *DiscoveryTitle.ToString()),
            FLinearColor(0.96f, 0.88f, 0.66f),
            BoxX + 16.0f, BoxY + 12.0f, SmallFont, 0.90f, false);
        DrawText(
            FString::Printf(TEXT("Journey Insight +%d   Total %d"), DiscoveryAwardedInsight, DiscoveryTotalInsight),
            FLinearColor(0.76f, 0.82f, 0.72f),
            BoxX + 16.0f, BoxY + 40.0f, SmallFont, 0.80f, false);
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

void AShireHUD::ShowDiscovery(const FText& Title, int32 AwardedInsight, int32 TotalInsight, float Duration)
{
    DiscoveryTitle = Title;
    DiscoveryAwardedInsight = FMath::Max(0, AwardedInsight);
    DiscoveryTotalInsight = FMath::Max(0, TotalInsight);
    DiscoveryUntilTime = GetWorld()
        ? GetWorld()->GetTimeSeconds() + FMath::Max(0.5f, Duration)
        : Duration;
}
