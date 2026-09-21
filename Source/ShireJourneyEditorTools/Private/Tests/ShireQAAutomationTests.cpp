#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "ShireSaveGame.h"

#include "Dom/JsonObject.h"
#include "Misc/FileHelper.h"
#include "Misc/PackageName.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/UObjectGlobals.h"

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

#endif
