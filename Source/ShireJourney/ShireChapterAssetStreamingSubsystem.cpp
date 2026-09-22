#include "ShireChapterAssetStreamingSubsystem.h"

#include "Dom/JsonObject.h"
#include "Engine/GameInstance.h"
#include "Engine/SkeletalMesh.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

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
        UE_LOG(
            LogTemp,
            Warning,
            TEXT("ChapterAssetStreaming: no bank for chapter=%s route=%s; compatibility path continues."),
            *ChapterId.ToString(),
            *RouteId.ToString());
        bPendingCompatibilityReady = true;
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
        bPendingCompatibilityReady = true;
        OnChapterAssetsReady.Broadcast(ChapterId, RouteId);
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
    OnCharacterRigReady.Broadcast(CharacterId);
    if (Rig)
    {
        Rig->Handle.Reset();
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
    if (CompletedChapter.IsNone() || CompletedRoute.IsNone())
    {
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
