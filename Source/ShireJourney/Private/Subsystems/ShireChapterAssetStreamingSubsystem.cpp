#include "ShireChapterAssetStreamingSubsystem.h"

#include "Dom/JsonObject.h"
#include "Engine/GameInstance.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformTime.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/PackageName.h"
#include "Misc/Parse.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "TimerManager.h"

void UShireChapterAssetStreamingSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    Banks.Empty();
    CharacterRigRequests.Empty();
    ResidentHandle.Reset();
    PendingHandle.Reset();
    ResidentChapterId = NAME_None;
    ResidentRouteId = NAME_None;
    PendingChapterId = NAME_None;
    PendingRouteId = NAME_None;
    RequestSerial = 0;
    bPendingCompatibilityReady = false;

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
    bPendingCompatibilityReady = false;
}

bool UShireChapterAssetStreamingSubsystem::CommitPendingRequest(
    FName ChapterId,
    FName RouteId)
{
    // Same chapter-bank, new episode/save-state: RequestChapterAssets intentionally
    // cancels any stale pending request and reports the already resident bank ready.
    // Treat that as a successful residency commit rather than forcing rollback.
    if (IsChapterBankReady(ChapterId, RouteId) &&
        PendingChapterId.IsNone() &&
        PendingRouteId.IsNone())
    {
        OnChapterAssetsCommitted.Broadcast(ChapterId, RouteId);
        UE_LOG(
            LogTemp,
            Display,
            TEXT("ChapterAssetStreaming: committed already-resident chapter=%s route=%s"),
            *ChapterId.ToString(),
            *RouteId.ToString());
        return true;
    }

    if (PendingChapterId != ChapterId || PendingRouteId != RouteId)
    {
        return false;
    }

    const bool bReady =
        bPendingCompatibilityReady ||
        (PendingHandle.IsValid() && PendingHandle->HasLoadCompleted());
    if (!bReady)
    {
        return false;
    }

    ResidentHandle = PendingHandle;
    PendingHandle.Reset();
    ResidentChapterId = ChapterId;
    ResidentRouteId = RouteId;
    PendingChapterId = NAME_None;
    PendingRouteId = NAME_None;
    bPendingCompatibilityReady = false;

    // Publish only after the new FStreamableHandle has become the resident owner.
    // Consumers can now ResolveObject without racing the preload/commit boundary.
    OnChapterAssetsCommitted.Broadcast(ChapterId, RouteId);

    UE_LOG(
        LogTemp,
        Display,
        TEXT("ChapterAssetStreaming: committed chapter=%s route=%s"),
        *ChapterId.ToString(),
        *RouteId.ToString());
    return true;
}

void UShireChapterAssetStreamingSubsystem::Deinitialize()
{
    CancelPendingRequest();

    ResidentHandle.Reset();
    for (TPair<FName, FCharacterRigRuntime>& Pair : CharacterRigRequests)
    {
        if (Pair.Value.Handle.IsValid())
        {
            Pair.Value.Handle->CancelHandle();
        }
    }
    CharacterRigRequests.Empty();
    Banks.Empty();
    bPlanReady = false;
    OnChapterAssetsReady.Clear();
    OnChapterAssetsCommitted.Clear();
    OnCharacterRigReady.Clear();

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

    if (PendingChapterId == ChapterId && PendingRouteId == RouteId)
    {
        if (bPendingCompatibilityReady ||
            (PendingHandle.IsValid() && PendingHandle->HasLoadCompleted()))
        {
            OnChapterAssetsReady.Broadcast(ChapterId, RouteId);
        }
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
    bPendingCompatibilityReady = false;

    const FChapterBankRuntime* Bank =
        bPlanReady ? Banks.Find(ResolveBankId(ChapterId, RouteId)) : nullptr;

    if (!Bank || Bank->Assets.Num() == 0)
    {
        FailPendingRequest(ChapterId, RouteId, TEXT("missing-or-empty-bank"));
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
        FailPendingRequest(ChapterId, RouteId, TEXT("async-handle-unavailable"));
    }
}

bool UShireChapterAssetStreamingSubsystem::ResolveCharacterRig(
    FName CharacterId,
    USkeletalMesh*& OutSkeletalMesh,
    UClass*& OutAnimClass) const
{
    OutSkeletalMesh = nullptr;
    OutAnimClass = nullptr;

    const FCharacterRigRuntime* Rig = CharacterRigRequests.Find(CharacterId);
    if (!Rig)
    {
        return false;
    }

    OutSkeletalMesh = Cast<USkeletalMesh>(Rig->SkeletalMeshPath.ResolveObject());
    OutAnimClass = Cast<UClass>(Rig->AnimClassPath.ResolveObject());
    return OutSkeletalMesh != nullptr && OutAnimClass != nullptr;
}

void UShireChapterAssetStreamingSubsystem::RequestCharacterRig(FName CharacterId)
{
    if (CharacterId.IsNone())
    {
        return;
    }

    FCharacterRigRuntime& Rig = CharacterRigRequests.FindOrAdd(CharacterId);
    if (!Rig.SkeletalMeshPath.IsValid())
    {
        const FString Character = CharacterId.ToString();
        Rig.SkeletalMeshPath = FSoftObjectPath(FString::Printf(
            TEXT("/Game/Production/Characters/Rigs/%s/SK_%s.SK_%s"),
            *Character, *Character, *Character));
        Rig.AnimClassPath = FSoftObjectPath(FString::Printf(
            TEXT("/Game/Production/Characters/Rigs/%s/ABP_%s_Locomotion.ABP_%s_Locomotion_C"),
            *Character, *Character, *Character));
    }

    USkeletalMesh* ExistingMesh = nullptr;
    UClass* ExistingAnimClass = nullptr;
    if (ResolveCharacterRig(CharacterId, ExistingMesh, ExistingAnimClass))
    {
        OnCharacterRigReady.Broadcast(CharacterId);
        return;
    }

    // Missing production rigs are an expected maturity state, not an async-loading
    // error. Package existence checks are bounded: missing rigs retry at most once
    // every two seconds, so an editor/import session can recover without restart
    // while large NPC groups cannot hammer the filesystem every request.
    const double NowSeconds = FPlatformTime::Seconds();
    const bool bShouldCheckAvailability =
        !Rig.bAvailabilityChecked ||
        (!Rig.bPackagesPresent &&
         (Rig.LastAvailabilityCheckSeconds < 0.0 ||
          (NowSeconds - Rig.LastAvailabilityCheckSeconds) >= 2.0));

    if (bShouldCheckAvailability)
    {
        const bool bWasPresent = Rig.bPackagesPresent;
        const FString MeshPackage =
            FPackageName::ObjectPathToPackageName(Rig.SkeletalMeshPath.ToString());
        const FString AnimPackage =
            FPackageName::ObjectPathToPackageName(Rig.AnimClassPath.ToString());
        Rig.bPackagesPresent =
            FPackageName::DoesPackageExist(MeshPackage) &&
            FPackageName::DoesPackageExist(AnimPackage);
        Rig.bAvailabilityChecked = true;
        Rig.LastAvailabilityCheckSeconds = NowSeconds;

        if (!Rig.bPackagesPresent)
        {
            UE_LOG(
                LogTemp,
                Display,
                TEXT("CharacterRigStreaming: unavailable id=%s reason=packages-missing fallback=modular retry=bounded"),
                *CharacterId.ToString());
        }
        else if (!bWasPresent)
        {
            UE_LOG(
                LogTemp,
                Display,
                TEXT("CharacterRigStreaming: availability-recovered id=%s async-request=ready"),
                *CharacterId.ToString());
        }
    }

    if (!Rig.bPackagesPresent)
    {
        return;
    }

    if (Rig.Handle.IsValid() && !Rig.Handle->HasLoadCompleted())
    {
        return;
    }

    TArray<FSoftObjectPath> Assets;
    Assets.Add(Rig.SkeletalMeshPath);
    Assets.Add(Rig.AnimClassPath);

    Rig.Handle = StreamableManager.RequestAsyncLoad(
        Assets,
        FStreamableDelegate::CreateUObject(
            this,
            &UShireChapterAssetStreamingSubsystem::HandleCharacterRigLoadComplete,
            CharacterId));

    UE_LOG(
        LogTemp,
        Display,
        TEXT("CharacterRigStreaming: request id=%s assets=%d"),
        *CharacterId.ToString(),
        Assets.Num());
}

void UShireChapterAssetStreamingSubsystem::HandleCharacterRigLoadComplete(FName CharacterId)
{
    FCharacterRigRuntime* Rig = CharacterRigRequests.Find(CharacterId);

    USkeletalMesh* SkeletalMesh = nullptr;
    UClass* AnimClass = nullptr;
    if (!ResolveCharacterRig(CharacterId, SkeletalMesh, AnimClass))
    {
        if (Rig)
        {
            // A completed failed handle must not pin a useless request forever.
            Rig->Handle.Reset();
        }
        UE_LOG(
            LogTemp,
            Warning,
            TEXT("CharacterRigStreaming: unavailable id=%s; modular fallback retained"),
            *CharacterId.ToString());
        return;
    }

    UE_LOG(
        LogTemp,
        Display,
        TEXT("CharacterRigStreaming: ready id=%s residency=actor-owned"),
        *CharacterId.ToString());

    // Broadcast while the handle still pins the assets. Player/NPC components take
    // their own UObject references during the callback. Releasing afterward lets
    // inactive rigs become GC-eligible instead of accumulating for GameInstance life.
    const TSharedPtr<FStreamableHandle> CompletedHandle = Rig ? Rig->Handle : nullptr;
    OnCharacterRigReady.Broadcast(CharacterId);
    // Listeners may add requests (reallocating the TMap), clear it during teardown,
    // or replace this entry. Never dereference a pre-broadcast map pointer here.
    Rig = CharacterRigRequests.Find(CharacterId);
    if (Rig && Rig->Handle == CompletedHandle)
    {
        Rig->Handle.Reset();
    }
}

bool UShireChapterAssetStreamingSubsystem::AreBankAssetsResolved(
    FName ChapterId,
    FName RouteId,
    int32& OutMissingCount) const
{
    OutMissingCount = 0;
    const FChapterBankRuntime* Bank = Banks.Find(ResolveBankId(ChapterId, RouteId));
    if (!Bank || Bank->Assets.Num() == 0)
    {
        OutMissingCount = 1;
        return false;
    }

    for (const FSoftObjectPath& AssetPath : Bank->Assets)
    {
        if (!AssetPath.ResolveObject())
        {
            ++OutMissingCount;
        }
    }
    return OutMissingCount == 0;
}

void UShireChapterAssetStreamingSubsystem::FailPendingRequest(
    FName ChapterId,
    FName RouteId,
    const TCHAR* Reason)
{
    // Failed pending ownership is never promoted to residency. Drop its handle
    // before notifying the router; the old resident handle remains untouched.
    PendingHandle.Reset();
    bPendingCompatibilityReady = false;

    UE_LOG(
        LogTemp,
        Error,
        TEXT("ChapterAssetStreaming: FAILED chapter=%s route=%s reason=%s residentChapter=%s residentRoute=%s"),
        *ChapterId.ToString(),
        *RouteId.ToString(),
        Reason ? Reason : TEXT("unknown"),
        *ResidentChapterId.ToString(),
        *ResidentRouteId.ToString());

    // Publish failure while request identity is still intact. Router owns rollback;
    // its cancellation then invalidates the serial and releases only pending ownership.
    OnChapterAssetsFailed.Broadcast(ChapterId, RouteId);
}

void UShireChapterAssetStreamingSubsystem::HandleAsyncLoadComplete(uint64 CompletedSerial)
{
    if (CompletedSerial != RequestSerial)
    {
        return;
    }

    const FName CompletedChapter = PendingChapterId;
    const FName CompletedRoute = PendingRouteId;
    if (CompletedChapter.IsNone() || CompletedRoute.IsNone())
    {
        return;
    }

#if !UE_BUILD_SHIPPING
    FString CIForcedFailureChapter;
    const bool bForceCIFailure =
        FParse::Param(FCommandLine::Get(), TEXT("ShireCIRuntimeAudit")) &&
        FParse::Value(
            FCommandLine::Get(),
            TEXT("ShireCIForceChapterAssetFailure="),
            CIForcedFailureChapter) &&
        CIForcedFailureChapter.Equals(
            CompletedChapter.ToString(),
            ESearchCase::IgnoreCase);
    if (bForceCIFailure)
    {
        FailPendingRequest(
            CompletedChapter,
            CompletedRoute,
            TEXT("ci-forced-async-failure"));
        return;
    }
#endif

    int32 MissingCount = 0;
    if (!AreBankAssetsResolved(CompletedChapter, CompletedRoute, MissingCount))
    {
        UE_LOG(
            LogTemp,
            Error,
            TEXT("ChapterAssetStreaming: unresolved-bank-assets chapter=%s route=%s missing=%d"),
            *CompletedChapter.ToString(),
            *CompletedRoute.ToString(),
            MissingCount);
        FailPendingRequest(
            CompletedChapter,
            CompletedRoute,
            TEXT("async-complete-with-unresolved-assets"));
        return;
    }

    // CI may hold ready publication after the actual async load completes. This
    // exercises the real two-phase transaction window without blocking the game thread.
    float CIDelaySeconds = 0.0f;
    const bool bForceCIDelay =
        FParse::Param(FCommandLine::Get(), TEXT("ShireCIRuntimeAudit")) &&
        FParse::Value(
            FCommandLine::Get(),
            TEXT("ShireCIAssetReadyDelay="),
            CIDelaySeconds) &&
        CIDelaySeconds > 0.0f &&
        GetWorld();

    if (bForceCIDelay)
    {
        CIDelaySeconds = FMath::Clamp(CIDelaySeconds, 0.1f, 5.0f);
        FTimerHandle DelayTimer;
        FTimerDelegate DelayDelegate = FTimerDelegate::CreateUObject(
            this,
            &UShireChapterAssetStreamingSubsystem::PublishPendingReady,
            CompletedSerial,
            CompletedChapter,
            CompletedRoute);
        GetWorld()->GetTimerManager().SetTimer(
            DelayTimer,
            DelayDelegate,
            CIDelaySeconds,
            false);
        UE_LOG(
            LogTemp,
            Display,
            TEXT("ChapterAssetStreaming: ci-ready-delay chapter=%s route=%s seconds=%.2f"),
            *CompletedChapter.ToString(),
            *CompletedRoute.ToString(),
            CIDelaySeconds);
        return;
    }

    PublishPendingReady(CompletedSerial, CompletedChapter, CompletedRoute);
}

void UShireChapterAssetStreamingSubsystem::PublishPendingReady(
    uint64 CompletedSerial,
    FName CompletedChapter,
    FName CompletedRoute)
{
    if (CompletedSerial != RequestSerial ||
        PendingChapterId != CompletedChapter ||
        PendingRouteId != CompletedRoute)
    {
        return;
    }

    int32 MissingCount = 0;
    if (!AreBankAssetsResolved(CompletedChapter, CompletedRoute, MissingCount))
    {
        FailPendingRequest(
            CompletedChapter,
            CompletedRoute,
            TEXT("assets-lost-before-ready-publication"));
        return;
    }

    // Two-phase transition: preload is not residency. Keep the old resident handle
    // alive until ChapterWorldRouter proves destination construction and grounding.
    UE_LOG(
        LogTemp,
        Display,
        TEXT("ChapterAssetStreaming: preloaded chapter=%s route=%s awaiting-world-commit"),
        *CompletedChapter.ToString(),
        *CompletedRoute.ToString());

    OnChapterAssetsReady.Broadcast(CompletedChapter, CompletedRoute);
}
