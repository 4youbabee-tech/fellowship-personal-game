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

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FShireQARuntimeCompletionTrainContractTest,
    "ShireJourney.QA.Runtime.CompletionTrainContract",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FShireQARuntimeCompletionTrainContractTest::RunTest(const FString& Parameters)
{
    const FString Path = FPaths::Combine(
        FPaths::ProjectDir(),
        TEXT("Data/P1C01RuntimeCompletionTrainV1.json"));

    FString JsonText;
    if (!TestTrue(TEXT("Runtime completion train must be readable"),
            FFileHelper::LoadFileToString(JsonText, *Path)))
    {
        return false;
    }

    TSharedPtr<FJsonObject> Root;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonText);
    if (!TestTrue(TEXT("Runtime completion train must be valid JSON"),
            FJsonSerializer::Deserialize(Reader, Root) && Root.IsValid()))
    {
        return false;
    }

    const TArray<TSharedPtr<FJsonValue>>* Cars = nullptr;
    if (!TestTrue(TEXT("Runtime completion train must define cars"),
            Root->TryGetArrayField(TEXT("cars"), Cars) && Cars))
    {
        return false;
    }

    TestEqual(TEXT("Runtime completion train must contain 20 cars"), Cars->Num(), 20);

    for (int32 Index = 0; Index < Cars->Num(); ++Index)
    {
        const TSharedPtr<FJsonObject> Car =
            (*Cars)[Index].IsValid() ? (*Cars)[Index]->AsObject() : nullptr;
        if (!TestTrue(
                *FString::Printf(TEXT("Runtime car %d must be an object"), Index + 1),
                Car.IsValid()))
        {
            continue;
        }

        double Order = 0.0;
        FString Id;
        FString Status;
        Car->TryGetNumberField(TEXT("order"), Order);
        Car->TryGetStringField(TEXT("id"), Id);
        Car->TryGetStringField(TEXT("status"), Status);

        TestEqual(
            *FString::Printf(TEXT("Runtime car %d order must remain serialized"), Index + 1),
            static_cast<int32>(Order),
            Index + 1);
        TestTrue(
            *FString::Printf(TEXT("Runtime car %d id must be non-empty"), Index + 1),
            !Id.IsEmpty());

        if (Index < 5)
        {
            TestEqual(
                *FString::Printf(TEXT("Runtime car %d must be source-implemented"), Index + 1),
                Status,
                FString(TEXT("SOURCE_IMPLEMENTED")));
        }
        else
        {
            TestTrue(
                *FString::Printf(TEXT("Runtime car %d must remain gate-queued"), Index + 1),
                Status.StartsWith(TEXT("QUEUED_BEHIND")));
        }
    }

    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FShireQALivingWorldBudgetContractTest,
    "ShireJourney.QA.Runtime.LivingWorldBudgetContract",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FShireQALivingWorldBudgetContractTest::RunTest(const FString& Parameters)
{
    const FString Path = FPaths::Combine(
        FPaths::ProjectDir(),
        TEXT("Data/LivingWorldEventPlan.json"));

    FString JsonText;
    if (!TestTrue(TEXT("LivingWorld event plan must be readable"),
            FFileHelper::LoadFileToString(JsonText, *Path)))
    {
        return false;
    }

    TSharedPtr<FJsonObject> Root;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonText);
    if (!TestTrue(TEXT("LivingWorld event plan must be valid JSON"),
            FJsonSerializer::Deserialize(Reader, Root) && Root.IsValid()))
    {
        return false;
    }

    const TSharedPtr<FJsonObject>* Budgets = nullptr;
    if (!TestTrue(TEXT("LivingWorld event plan must define region budgets"),
            Root->TryGetObjectField(TEXT("region_budgets"), Budgets) &&
            Budgets && Budgets->IsValid()))
    {
        return false;
    }

    double MaxMicroEvents = 0.0;
    double MaxFaunaGroups = 0.0;
    double EventCullDistance = 0.0;
    double FaunaCullDistance = 0.0;
    FString OffscreenSimulation;

    (*Budgets)->TryGetNumberField(TEXT("max_active_micro_events_near_player"), MaxMicroEvents);
    (*Budgets)->TryGetNumberField(TEXT("max_active_fauna_groups_near_player"), MaxFaunaGroups);
    (*Budgets)->TryGetNumberField(TEXT("event_cull_distance_cm"), EventCullDistance);
    (*Budgets)->TryGetNumberField(TEXT("fauna_cull_distance_cm"), FaunaCullDistance);
    (*Budgets)->TryGetStringField(TEXT("offscreen_simulation"), OffscreenSimulation);

    TestEqual(TEXT("LivingWorld max micro-events must remain 3"),
        static_cast<int32>(MaxMicroEvents), 3);
    TestEqual(TEXT("LivingWorld max fauna groups must remain 2"),
        static_cast<int32>(MaxFaunaGroups), 2);
    TestEqual(TEXT("LivingWorld event cull distance must remain 5000 cm"),
        static_cast<int32>(EventCullDistance), 5000);
    TestEqual(TEXT("LivingWorld fauna cull distance must remain 4200 cm"),
        static_cast<int32>(FaunaCullDistance), 4200);
    TestEqual(TEXT("LivingWorld offscreen simulation must remain STATE_ONLY"),
        OffscreenSimulation, FString(TEXT("STATE_ONLY")));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FShireQACharacterRigIntakeContractTest,
    "ShireJourney.QA.Assets.CharacterRigIntakeContract",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FShireQACharacterRigIntakeContractTest::RunTest(const FString& Parameters)
{
    const FString Path = FPaths::Combine(
        FPaths::ProjectDir(),
        TEXT("Data/P1C01CharacterRigAnimationPrepV1.json"));

    FString JsonText;
    if (!TestTrue(TEXT("Character rig intake contract must be readable"),
            FFileHelper::LoadFileToString(JsonText, *Path)))
    {
        return false;
    }

    TSharedPtr<FJsonObject> Root;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonText);
    if (!TestTrue(TEXT("Character rig intake contract must be valid JSON"),
            FJsonSerializer::Deserialize(Reader, Root) && Root.IsValid()))
    {
        return false;
    }

    const TSharedPtr<FJsonObject>* RequiredBundle = nullptr;
    if (!TestTrue(TEXT("Character rig contract must define required_bundle"),
            Root->TryGetObjectField(TEXT("required_bundle"), RequiredBundle) &&
            RequiredBundle && RequiredBundle->IsValid()))
    {
        return false;
    }

    FString SkeletalMeshFormat;
    (*RequiredBundle)->TryGetStringField(TEXT("skeletal_mesh"), SkeletalMeshFormat);
    TestEqual(TEXT("Final skeletal mesh format must remain FBX"),
        SkeletalMeshFormat, FString(TEXT("FBX")));

    const TArray<TSharedPtr<FJsonValue>>* Textures = nullptr;
    if (TestTrue(TEXT("Character rig contract must define texture formats"),
            (*RequiredBundle)->TryGetArrayField(TEXT("textures"), Textures) && Textures))
    {
        TArray<FString> TextureFormats;
        for (const TSharedPtr<FJsonValue>& Value : *Textures)
        {
            if (Value.IsValid())
            {
                TextureFormats.Add(Value->AsString());
            }
        }
        TestTrue(TEXT("Character texture contract must allow PNG"),
            TextureFormats.Contains(TEXT("PNG")));
        TestTrue(TEXT("Character texture contract must allow TGA"),
            TextureFormats.Contains(TEXT("TGA")));
        TestFalse(TEXT("Character texture contract must not allow BMP"),
            TextureFormats.Contains(TEXT("BMP")));
    }

    const TArray<TSharedPtr<FJsonValue>>* Forbidden = nullptr;
    if (TestTrue(TEXT("Character rig contract must define forbidden states"),
            Root->TryGetArrayField(TEXT("forbidden"), Forbidden) && Forbidden))
    {
        TArray<FString> ForbiddenValues;
        for (const TSharedPtr<FJsonValue>& Value : *Forbidden)
        {
            if (Value.IsValid())
            {
                ForbiddenValues.Add(Value->AsString());
            }
        }
        TestTrue(TEXT("Animated OBJ must remain forbidden"),
            ForbiddenValues.Contains(TEXT("OBJ_AS_FINAL_ANIMATED_CHARACTER")));
        TestTrue(TEXT("BMP textures must remain forbidden"),
            ForbiddenValues.Contains(TEXT("BMP_TEXTURE")));
    }

    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FShireQAAudioMasterContractTest,
    "ShireJourney.QA.Audio.P1C01MasterContract",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FShireQAAudioMasterContractTest::RunTest(const FString& Parameters)
{
    const FString Path = FPaths::Combine(
        FPaths::ProjectDir(),
        TEXT("Data/P1C01AudioFoleyAmbiencePrepV1.json"));

    FString JsonText;
    if (!TestTrue(TEXT("P1C01 audio contract must be readable"),
            FFileHelper::LoadFileToString(JsonText, *Path)))
    {
        return false;
    }

    TSharedPtr<FJsonObject> Root;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonText);
    if (!TestTrue(TEXT("P1C01 audio contract must be valid JSON"),
            FJsonSerializer::Deserialize(Reader, Root) && Root.IsValid()))
    {
        return false;
    }

    const TArray<TSharedPtr<FJsonValue>>* Items = nullptr;
    if (!TestTrue(TEXT("P1C01 audio contract must define items"),
            Root->TryGetArrayField(TEXT("items"), Items) && Items))
    {
        return false;
    }

    TestEqual(TEXT("P1C01 audio contract must contain five authorized candidates"),
        Items->Num(), 5);

    for (const TSharedPtr<FJsonValue>& Value : *Items)
    {
        const TSharedPtr<FJsonObject> Item =
            Value.IsValid() ? Value->AsObject() : nullptr;
        if (!TestTrue(TEXT("Each P1C01 audio item must be an object"), Item.IsValid()))
        {
            continue;
        }

        FString Id;
        FString License;
        FString State;
        FString MasterRequirement;
        Item->TryGetStringField(TEXT("id"), Id);
        Item->TryGetStringField(TEXT("license"), License);
        Item->TryGetStringField(TEXT("state"), State);
        Item->TryGetStringField(TEXT("master_requirement"), MasterRequirement);

        TestTrue(TEXT("Audio item id must be non-empty"), !Id.IsEmpty());
        TestEqual(*FString::Printf(TEXT("%s license must remain CC0"), *Id),
            License, FString(TEXT("CC0")));
        TestEqual(*FString::Printf(TEXT("%s must remain authorized for staging"), *Id),
            State, FString(TEXT("AUTHORIZED_FOR_STAGING")));
        TestEqual(*FString::Printf(TEXT("%s production master must remain WAV"), *Id),
            MasterRequirement, FString(TEXT("WAV")));
    }

    return true;
}

#endif
