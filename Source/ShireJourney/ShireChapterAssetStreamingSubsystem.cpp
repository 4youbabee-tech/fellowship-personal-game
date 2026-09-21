#include "ShireChapterAssetStreamingSubsystem.h"

#include "Dom/JsonObject.h"
#include "Engine/GameInstance.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

void UShireChapterAssetStreamingSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    Banks.Empty();
    ResidentHandle.Reset();
    PendingHandle.Reset();
    ResidentChapterId = NAME_None;
    ResidentRouteId = NAME_None;
    PendingChapterId = NAME_None;
    PendingRouteId = NAME_None;
    RequestSerial = 0;

    bPlanReady = LoadStreamingPlan();
    if (bPlanReady)
    {
        UE_LOG(
            LogTemp,
            Display,
            TEXT("ChapterAssetStreaming: plan-ready=yes banks=%d"),
            Banks.Num());
    }
    else
    {
        UE_LOG(
            LogTemp,
            Warning,
            TEXT("ChapterAssetStreaming: plan-ready=no banks=%d"),
            Banks.Num());
    }
}

void UShireChapterAssetStreamingSubsystem::CancelPendingRequest()
{
    // Invalidate callbacks before cancelling; retain the visible resident bank.
    ++RequestSerial;

    if (PendingHandle.IsValid())
    {
        PendingHandle->CancelHandle();
        PendingHandle.Reset();
    }

    PendingChapterId = NAME_None;
    PendingRouteId = NAME_None;
}

void UShireChapterAssetStreamingSubsystem::Deinitialize()
{
    CancelPendingRequest();

    ResidentHandle.Reset();
    Banks.Empty();
    bPlanReady = false;
    OnChapterAssetsReady.Clear();

    Super::Deinitialize();
}

bool UShireChapterAssetStreamingSubsystem::LoadStreamingPlan()
{
    const FString Path = FPaths::Combine(
        FPaths::ProjectDir(),
        TEXT("Data/ChapterAssetStreamingPlan.json"));

    FString JsonText;
    if (!FFileHelper::LoadFileToString(JsonText, *Path))
    {
        UE_LOG(
            LogTemp,
            Warning,
            TEXT("ChapterAssetStreaming: could not read %s; router will use compatibility loading."),
            *Path);
        return false;
    }

    TSharedPtr<FJsonObject> Root;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonText);
    if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("ChapterAssetStreaming: invalid JSON plan."));
        return false;
    }

    const TSharedPtr<FJsonObject>* BanksObject = nullptr;
    if (!Root->TryGetObjectField(TEXT("banks"), BanksObject) ||
        !BanksObject || !BanksObject->IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("ChapterAssetStreaming: banks object missing."));
        return false;
    }

    for (const auto& Pair : (*BanksObject)->Values)
    {
        const TSharedPtr<FJsonObject> BankObject =
            Pair.Value.IsValid() ? Pair.Value->AsObject() : nullptr;
        if (!BankObject.IsValid())
        {
            continue;
        }

        FChapterBankRuntime Bank;
        FString RouteString;
        BankObject->TryGetStringField(TEXT("route"), RouteString);
        Bank.RouteId = RouteString.IsEmpty() ? NAME_None : FName(*RouteString);

        const TArray<TSharedPtr<FJsonValue>>* AssetValues = nullptr;
        if (BankObject->TryGetArrayField(TEXT("assets"), AssetValues) && AssetValues)
        {
            for (const TSharedPtr<FJsonValue>& AssetValue : *AssetValues)
            {
                const FString AssetPath =
                    AssetValue.IsValid() ? AssetValue->AsString() : FString();
                if (!AssetPath.IsEmpty())
                {
                    Bank.Assets.AddUnique(FSoftObjectPath(AssetPath));
                }
            }
        }

        if (Bank.Assets.Num() > 0)
        {
            Banks.Add(FName(*Pair.Key), MoveTemp(Bank));
        }
    }

    return Banks.Num() > 0;
}

FName UShireChapterAssetStreamingSubsystem::ResolveBankId(
    FName ChapterId,
    FName RouteId) const
{
    if (RouteId == TEXT("GandalfParallel"))
    {
        return TEXT("GANDALF_ISENGARD");
    }
    return ChapterId;
}

bool UShireChapterAssetStreamingSubsystem::IsChapterBankReady(
    FName ChapterId,
    FName RouteId) const
{
    return ResidentChapterId == ChapterId &&
        ResidentRouteId == RouteId &&
        (!ResidentHandle.IsValid() || ResidentHandle->HasLoadCompleted());
}

int32 UShireChapterAssetStreamingSubsystem::GetChapterBankSize(
    FName ChapterId,
    FName RouteId) const
{
    const FChapterBankRuntime* Bank = Banks.Find(ResolveBankId(ChapterId, RouteId));
    return Bank ? Bank->Assets.Num() : 0;
}

void UShireChapterAssetStreamingSubsystem::RequestChapterAssets(
    FName ChapterId,
    FName RouteId)
{
    if (IsChapterBankReady(ChapterId, RouteId))
    {
        CancelPendingRequest();
        OnChapterAssetsReady.Broadcast(ChapterId, RouteId);
        return;
    }

    if (PendingChapterId == ChapterId &&
        PendingRouteId == RouteId &&
        PendingHandle.IsValid() &&
        !PendingHandle->HasLoadCompleted())
    {
        return;
    }

    ++RequestSerial;
    const uint64 ThisSerial = RequestSerial;

    if (PendingHandle.IsValid())
    {
        PendingHandle->CancelHandle();
        PendingHandle.Reset();
    }

    PendingChapterId = ChapterId;
    PendingRouteId = RouteId;

    const FChapterBankRuntime* Bank =
        bPlanReady ? Banks.Find(ResolveBankId(ChapterId, RouteId)) : nullptr;

    if (!Bank || Bank->Assets.Num() == 0)
    {
        UE_LOG(
            LogTemp,
            Warning,
            TEXT("ChapterAssetStreaming: no bank for chapter=%s route=%s; compatibility path continues."),
            *ChapterId.ToString(),
            *RouteId.ToString());
        ResidentChapterId = ChapterId;
        ResidentRouteId = RouteId;
        PendingChapterId = NAME_None;
        PendingRouteId = NAME_None;
        OnChapterAssetsReady.Broadcast(ChapterId, RouteId);
        return;
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("ChapterAssetStreaming: request chapter=%s route=%s assets=%d"),
        *ChapterId.ToString(),
        *RouteId.ToString(),
        Bank->Assets.Num());

    PendingHandle = StreamableManager.RequestAsyncLoad(
        Bank->Assets,
        FStreamableDelegate::CreateUObject(
            this,
            &UShireChapterAssetStreamingSubsystem::HandleAsyncLoadComplete,
            ThisSerial));

    if (!PendingHandle.IsValid())
    {
        UE_LOG(
            LogTemp,
            Warning,
            TEXT("ChapterAssetStreaming: async handle unavailable for chapter=%s; compatibility path continues."),
            *ChapterId.ToString());
        ResidentChapterId = ChapterId;
        ResidentRouteId = RouteId;
        PendingChapterId = NAME_None;
        PendingRouteId = NAME_None;
        OnChapterAssetsReady.Broadcast(ChapterId, RouteId);
    }
}

void UShireChapterAssetStreamingSubsystem::HandleAsyncLoadComplete(uint64 CompletedSerial)
{
    if (CompletedSerial != RequestSerial)
    {
        return;
    }

    const FName CompletedChapter = PendingChapterId;
    const FName CompletedRoute = PendingRouteId;

    // Promote the new bank only after it is loaded. Until this point the old resident
    // handle stays alive, matching Source 11's requirement to avoid exposing a broken
    // narrative seam while critical content is still asynchronous.
    ResidentHandle = PendingHandle;
    PendingHandle.Reset();

    ResidentChapterId = CompletedChapter;
    ResidentRouteId = CompletedRoute;
    PendingChapterId = NAME_None;
    PendingRouteId = NAME_None;

    UE_LOG(
        LogTemp,
        Display,
        TEXT("ChapterAssetStreaming: ready chapter=%s route=%s"),
        *CompletedChapter.ToString(),
        *CompletedRoute.ToString());

    OnChapterAssetsReady.Broadcast(CompletedChapter, CompletedRoute);
}
