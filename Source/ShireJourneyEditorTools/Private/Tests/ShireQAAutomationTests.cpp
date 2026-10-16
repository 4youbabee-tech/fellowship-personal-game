#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "ShireSaveGame.h"
#include "ShireNPC.h"
#include "Components/CapsuleComponent.h"

#include "Dom/JsonObject.h"
#include "Misc/FileHelper.h"
#include "Misc/PackageName.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/UObjectGlobals.h"
#include "Editor.h"
#include "PlayInEditorDataTypes.h"
#include "Engine/World.h"
#include "Engine/GameViewportClient.h"
#include "UnrealClient.h"
#include "Slate/SceneViewport.h"
#include "EngineUtils.h"
#include "ShirePrototypeWorldBuilder.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/Pawn.h"
#include "HAL/PlatformTime.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Settings/LevelEditorPlaySettings.h"
#include "Tests/AutomationEditorCommon.h"

// Opt-in editor integration evidence. This deliberately runs a real PIE world;
// ordinary QA runs neither enter PIE nor produce visual acceptance claims.
class FShirePES002StartFloatingPIE : public IAutomationLatentCommand
{
public:
    virtual bool Update() override
    {
        // UE4.27: an explicitly empty destination selects a separate PIE
        // viewport; FStartPIECommand instead forces the active editor viewport.
        FRequestPlaySessionParams Params;
        Params.DestinationSlateViewport = nullptr;
        GEditor->RequestPlaySession(Params);
        return true;
    }
};

class FShirePES002WaitForVisualPIE : public IAutomationLatentCommand
{
public:
    explicit FShirePES002WaitForVisualPIE(FAutomationTestBase* InTest)
        : Test(InTest), StartedAt(FPlatformTime::Seconds()) {}

    virtual bool Update() override
    {
        UWorld* World = GEditor ? GEditor->PlayWorld : nullptr;
        APlayerController* PC = World ? World->GetFirstPlayerController() : nullptr;
        if (World && World->WorldType == EWorldType::PIE && PC && PC->GetPawn())
        {
            if (!bObservedPIE)
            {
                bObservedPIE = true;
                // Windows work-area fitting can shrink a requested PIE window.
                // Resize the actual rendering viewport, not the outer Editor.
                UGameViewportClient* ViewportClient = World->GetGameViewport();
                if (ViewportClient && ViewportClient->GetGameViewport())
                    ViewportClient->GetGameViewport()->ResizeFrame(1280, 720, EWindowMode::Windowed);
                UE_LOG(LogTemp, Display,
                    TEXT("PES002_PIE_SESSION_ACTUAL world=%s worldType=PIE pawn=%s"),
                    *World->GetName(), *PC->GetPawn()->GetName());
            }
            // Chapter streaming can finish long after PIE starts. Capture and
            // CSV timers begin when the actual Shire builder is created.
            bool bCaptureWindowComplete = false;
            for (TActorIterator<AShirePrototypeWorldBuilder> It(World); It; ++It)
                bCaptureWindowComplete |= It->GetGameTimeSinceCreation() >= 50.0f;
            if (bCaptureWindowComplete)
            {
                UE_LOG(LogTemp, Display,
                    TEXT("PES002_PIE_CAPTURE_WINDOW_COMPLETE worldType=PIE worldSeconds=%.2f visualAcceptance=pending"),
                    World->GetTimeSeconds());
                return true;
            }
        }
        else if (bObservedPIE)
        {
            Test->AddError(TEXT("Actual PIE world/player pawn disappeared before the capture window completed"));
            return true;
        }
        if (FPlatformTime::Seconds() - StartedAt > 180.0)
        {
            Test->AddError(TEXT("Timed out waiting for actual PIE world, player pawn and 50 seconds of world ticks"));
            return true;
        }
        return false;
    }
private:
    FAutomationTestBase* Test;
    double StartedAt;
    bool bObservedPIE = false;
};

class FShirePES002RestorePIESettings : public IAutomationLatentCommand
{
public:
    FShirePES002RestorePIESettings(FAutomationTestBase* InTest, int32 InWidth, int32 InHeight)
        : Test(InTest), Width(InWidth), Height(InHeight) {}
    virtual bool Update() override
    {
        if (GEditor && GEditor->PlayWorld)
        {
            if (EndedAt == 0.0) EndedAt = FPlatformTime::Seconds();
            if (FPlatformTime::Seconds() - EndedAt < 30.0) return false;
            Test->AddError(TEXT("PIE teardown did not complete within 30 seconds"));
        }
        ULevelEditorPlaySettings* Settings = GetMutableDefault<ULevelEditorPlaySettings>();
        Settings->NewWindowWidth = Width;
        Settings->NewWindowHeight = Height;
        UE_LOG(LogTemp, Display, TEXT("PES002_PIE_SESSION_ENDED active=%d"),
            GEditor && GEditor->PlayWorld ? 1 : 0);
        return true;
    }
private:
    FAutomationTestBase* Test;
    double EndedAt = 0.0;
    int32 Width;
    int32 Height;
};

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FShirePES002VisualPIETest,
    "ShireJourney.PES002.VisualPIE",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FShirePES002VisualPIETest::RunTest(const FString& Parameters)
{
    if (!FParse::Param(FCommandLine::Get(), TEXT("PES002VisualProof")))
    {
        AddWarning(TEXT("VisualPIE requires explicit -PES002VisualProof; no PIE evidence produced"));
        return true;
    }
    if (!GEditor || GEditor->PlayWorld)
    {
        AddError(TEXT("VisualPIE requires an idle Unreal Editor; will not replace an active PIE session"));
        return false;
    }
    ULevelEditorPlaySettings* Settings = GetMutableDefault<ULevelEditorPlaySettings>();
    const int32 PreviousWidth = Settings->NewWindowWidth;
    const int32 PreviousHeight = Settings->NewWindowHeight;
    Settings->NewWindowWidth = 1280;
    Settings->NewWindowHeight = 720;
    ADD_LATENT_AUTOMATION_COMMAND(FEditorLoadMap(TEXT("/Engine/Maps/Entry")));
    ADD_LATENT_AUTOMATION_COMMAND(FShirePES002StartFloatingPIE());
    ADD_LATENT_AUTOMATION_COMMAND(FShirePES002WaitForVisualPIE(this));
    ADD_LATENT_AUTOMATION_COMMAND(FEndPlayMapCommand());
    ADD_LATENT_AUTOMATION_COMMAND(FShirePES002RestorePIESettings(this, PreviousWidth, PreviousHeight));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FShireQASaveDefaultStateTest,
    "ShireJourney.QA.Save.DefaultState",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FShireQASaveDefaultStateTest::RunTest(const FString& Parameters)
{
    UShireSaveGame* Save = NewObject<UShireSaveGame>();
    if (!TestNotNull(TEXT("Save object must construct"), Save))
    {
        return false;
    }

    TestTrue(TEXT("Save schema must equal current schema"),
        Save->SaveSchemaVersion == UShireSaveGame::CurrentSchemaVersion);
    TestTrue(TEXT("Default chapter must be P1C01"), Save->CurrentChapterId == TEXT("P1C01"));
    TestTrue(TEXT("Default route must be FrodoMain"), Save->CurrentRouteId == TEXT("FrodoMain"));
    TestTrue(TEXT("Default playable character must be Frodo"), Save->PlayableCharacterId == TEXT("Frodo"));
    TestTrue(TEXT("Health must begin positive"), Save->PlayerHealth > 0.0f);
    TestTrue(TEXT("Stamina must begin positive"), Save->PlayerStamina > 0.0f);
    TestTrue(TEXT("Resolve must begin positive"), Save->PlayerResolve > 0.0f);
    TestTrue(TEXT("Supplies may not begin negative"), Save->PlayerSupplies >= 0);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FShireQAStreamingBankPackagesTest,
    "ShireJourney.QA.Assets.StreamingBankPackages",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FShireQAStreamingBankPackagesTest::RunTest(const FString& Parameters)
{
    const FString PlanPath = FPaths::Combine(
        FPaths::ProjectDir(),
        TEXT("Data/ChapterAssetStreamingPlan.json"));

    FString JsonText;
    if (!TestTrue(TEXT("Streaming plan must be readable"),
            FFileHelper::LoadFileToString(JsonText, *PlanPath)))
    {
        return false;
    }

    TSharedPtr<FJsonObject> Root;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonText);
    if (!TestTrue(TEXT("Streaming plan must be valid JSON"),
            FJsonSerializer::Deserialize(Reader, Root) && Root.IsValid()))
    {
        return false;
    }

    const TSharedPtr<FJsonObject>* BanksObject = nullptr;
    if (!TestTrue(TEXT("Streaming plan must define banks"),
            Root->TryGetObjectField(TEXT("banks"), BanksObject) &&
            BanksObject && BanksObject->IsValid()))
    {
        return false;
    }

    int32 AssetCount = 0;
    for (const auto& BankPair : (*BanksObject)->Values)
    {
        const TSharedPtr<FJsonObject> Bank =
            BankPair.Value.IsValid() ? BankPair.Value->AsObject() : nullptr;
        if (!Bank.IsValid())
        {
            AddError(FString::Printf(TEXT("Invalid streaming bank: %s"), *BankPair.Key));
            continue;
        }

        const TArray<TSharedPtr<FJsonValue>>* Assets = nullptr;
        if (!Bank->TryGetArrayField(TEXT("assets"), Assets) || !Assets)
        {
            AddError(FString::Printf(TEXT("Streaming bank has no assets array: %s"), *BankPair.Key));
            continue;
        }

        for (const TSharedPtr<FJsonValue>& AssetValue : *Assets)
        {
            const FString ObjectPath = AssetValue.IsValid() ? AssetValue->AsString() : FString();
            if (ObjectPath.IsEmpty())
            {
                AddError(FString::Printf(TEXT("Empty asset path in bank: %s"), *BankPair.Key));
                continue;
            }

            ++AssetCount;
            const FString PackageName = FPackageName::ObjectPathToPackageName(ObjectPath);
            TestTrue(
                *FString::Printf(TEXT("Imported package must exist: %s"), *ObjectPath),
                FPackageName::DoesPackageExist(PackageName));
        }
    }

    TestTrue(TEXT("At least one streamed package must be audited"), AssetCount > 0);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FShireQANPCVisibilityInteractionTest,
    "ShireJourney.QA.NPC.VisibilityInteraction",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FShireQANPCVisibilityInteractionTest::RunTest(const FString& Parameters)
{
    const AShireNPC* NPCDefaults = GetDefault<AShireNPC>();
    if (!TestNotNull(TEXT("Interactable NPC class default must exist"), NPCDefaults))
    {
        return false;
    }

    const UCapsuleComponent* Capsule = NPCDefaults->GetCapsuleComponent();
    if (!TestNotNull(TEXT("Interactable NPC capsule must exist"), Capsule))
    {
        return false;
    }

    // The camera's visibility trace must be able to reach a named NPC, while
    // pawn movement collision remains governed by the existing capsule profile.
    TestEqual(TEXT("Named NPC capsule must block interaction visibility traces"),
        Capsule->GetCollisionResponseToChannel(ECC_Visibility), ECR_Block);
    TestTrue(TEXT("Named NPC capsule must remain query-enabled"),
        Capsule->GetCollisionEnabled() != ECollisionEnabled::NoCollision);
    return true;
}

#endif
