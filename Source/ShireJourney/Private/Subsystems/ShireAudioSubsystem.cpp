#include "ShireAudioSubsystem.h"

#include "ShireDialogueSubsystem.h"
#include "ShireNPC.h"
#include "ShireQuestSubsystem.h"
#include "ShireStoryPresentationSubsystem.h"

#include "Components/AudioComponent.h"
#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/PackageName.h"
#include "Sound/SoundAttenuation.h"
#include "Sound/SoundBase.h"
#include "UObject/SoftObjectPath.h"

namespace ShireAudioAssetPaths
{
    static const TCHAR* Ambience = TEXT("/Game/Audio/Ambience/");
    static const TCHAR* Music = TEXT("/Game/Audio/Music/");
    static const TCHAR* SFX = TEXT("/Game/Audio/SFX/");

    static const FName AmbienceCategory(TEXT("Ambience"));
    static const FName MusicCategory(TEXT("Music"));
    static const FName SfxCategory(TEXT("SFX"));
    static const FName VoiceCategory(TEXT("Voice"));
}


void UShireAudioSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    Collection.InitializeDependency<UShireDialogueSubsystem>();
    Collection.InitializeDependency<UShireStoryPresentationSubsystem>();

    ActiveAmbienceCue = NAME_None;
    ActiveMusicCue = NAME_None;
    PendingVoiceCue = NAME_None;
    PendingAudioLoads.Empty();
    PendingSpatialSfx.Empty();
    LastSfxPlaybackTimeSeconds.Empty();
    RecentDecorativeSfxStartTimes.Empty();

    SpatialSfxAttenuation = NewObject<USoundAttenuation>(this);
    if (SpatialSfxAttenuation)
    {
        FSoundAttenuationSettings& Settings = SpatialSfxAttenuation->Attenuation;
        Settings.bAttenuate = true;
        Settings.bSpatialize = true;
        Settings.DistanceAlgorithm = EAttenuationDistanceModel::NaturalSound;
        Settings.AttenuationShape = EAttenuationShape::Sphere;
        Settings.AttenuationShapeExtents = FVector(110.0f, 0.0f, 0.0f);
        Settings.FalloffDistance = 850.0f;
    }

    if (UGameInstance* GI = GetGameInstance())
    {
        if (UShireDialogueSubsystem* Dialogue = GI->GetSubsystem<UShireDialogueSubsystem>())
        {
            Dialogue->OnVoiceCueRequested.AddDynamic(this, &UShireAudioSubsystem::HandleVoiceRequest);
        }

        if (UShireStoryPresentationSubsystem* Presentation = GI->GetSubsystem<UShireStoryPresentationSubsystem>())
        {
            Presentation->OnAmbienceCueRequested.AddDynamic(this, &UShireAudioSubsystem::HandleAmbienceRequest);
            Presentation->OnMusicCueRequested.AddDynamic(this, &UShireAudioSubsystem::HandleMusicRequest);
            Presentation->OnSfxCueRequested.AddDynamic(this, &UShireAudioSubsystem::HandleSfxRequest);
        }
    }
}

void UShireAudioSubsystem::Deinitialize()
{
    if (UGameInstance* GI = GetGameInstance())
    {
        if (UShireDialogueSubsystem* Dialogue = GI->GetSubsystem<UShireDialogueSubsystem>())
        {
            Dialogue->OnVoiceCueRequested.RemoveDynamic(this, &UShireAudioSubsystem::HandleVoiceRequest);
        }

        if (UShireStoryPresentationSubsystem* Presentation = GI->GetSubsystem<UShireStoryPresentationSubsystem>())
        {
            Presentation->OnAmbienceCueRequested.RemoveDynamic(this, &UShireAudioSubsystem::HandleAmbienceRequest);
            Presentation->OnMusicCueRequested.RemoveDynamic(this, &UShireAudioSubsystem::HandleMusicRequest);
            Presentation->OnSfxCueRequested.RemoveDynamic(this, &UShireAudioSubsystem::HandleSfxRequest);
        }
    }

    for (TPair<FName, TSharedPtr<FStreamableHandle>>& Pair : PendingAudioLoads)
    {
        if (Pair.Value.IsValid())
        {
            Pair.Value->CancelHandle();
        }
    }
    PendingAudioLoads.Empty();
    PendingSpatialSfx.Empty();
    LastSfxPlaybackTimeSeconds.Empty();
    RecentDecorativeSfxStartTimes.Empty();
    PendingVoiceCue = NAME_None;
    SpatialSfxAttenuation = nullptr;

    if (ActiveVoiceComponent)
    {
        ActiveVoiceComponent->OnAudioFinished.RemoveDynamic(this, &UShireAudioSubsystem::HandleVoiceFinished);
        ActiveVoiceComponent->Stop();
        ActiveVoiceComponent = nullptr;
    }
    VoiceCache.Empty();
    AmbienceCache.Empty();
    MusicCache.Empty();
    SfxCache.Empty();

    ClearPersistentAudio();
    Super::Deinitialize();
}

USoundBase* UShireAudioSubsystem::ResolveCategorizedAsset(
    FName CueId,
    const TCHAR* FolderPrefix,
    TMap<FName, TWeakObjectPtr<USoundBase>>& Cache,
    FName Category)
{
    if (CueId == NAME_None)
    {
        return nullptr;
    }

    if (TWeakObjectPtr<USoundBase>* Cached = Cache.Find(CueId))
    {
        if (Cached->IsValid())
        {
            return Cached->Get();
        }
        Cache.Remove(CueId);
    }

    const FString Cue = CueId.ToString();
    const FString PackagePath = FString::Printf(TEXT("%s%s"), FolderPrefix, *Cue);
    if (!FPackageName::DoesPackageExist(PackagePath))
    {
        return nullptr;
    }

    const FSoftObjectPath AssetPath(FString::Printf(TEXT("%s.%s"), *PackagePath, *Cue));
    if (USoundBase* Sound = Cast<USoundBase>(AssetPath.ResolveObject()))
    {
        Cache.Add(CueId, Sound);
        return Sound;
    }

    RequestAudioAssetAsync(Category, CueId, AssetPath);
    return nullptr;
}

void UShireAudioSubsystem::RequestAudioAssetAsync(
    FName Category,
    FName CueId,
    const FSoftObjectPath& AssetPath)
{
    if (Category == NAME_None || CueId == NAME_None || !AssetPath.IsValid())
    {
        return;
    }

    const FName LoadKey(*FString::Printf(
        TEXT("%s|%s"), *Category.ToString(), *CueId.ToString()));
    if (TSharedPtr<FStreamableHandle>* Existing = PendingAudioLoads.Find(LoadKey))
    {
        if (Existing->IsValid() && !(*Existing)->HasLoadCompleted())
        {
            return;
        }
        PendingAudioLoads.Remove(LoadKey);
    }

    TArray<FSoftObjectPath> Assets;
    Assets.Add(AssetPath);
    TSharedPtr<FStreamableHandle> Handle = StreamableManager.RequestAsyncLoad(
        Assets,
        FStreamableDelegate::CreateUObject(
            this,
            &UShireAudioSubsystem::HandleAsyncAudioReady,
            Category,
            CueId,
            AssetPath,
            LoadKey));

    if (Handle.IsValid())
    {
        PendingAudioLoads.Add(LoadKey, Handle);
        UE_LOG(
            LogTemp,
            Verbose,
            TEXT("AudioStreaming: request category=%s cue=%s"),
            *Category.ToString(),
            *CueId.ToString());
    }
}

void UShireAudioSubsystem::CancelPendingAudioCategory(FName Category)
{
    const FString Prefix = Category.ToString() + TEXT("|");
    for (auto It = PendingAudioLoads.CreateIterator(); It; ++It)
    {
        if (!It.Key().ToString().StartsWith(Prefix))
        {
            continue;
        }

        if (It.Value().IsValid())
        {
            It.Value()->CancelHandle();
        }
        It.RemoveCurrent();
    }
}

void UShireAudioSubsystem::HandleAsyncAudioReady(
    FName Category,
    FName CueId,
    FSoftObjectPath AssetPath,
    FName LoadKey)
{
    // CancelPendingAudioCategory removes the ownership record before cancelling.
    // A late delegate from a cancelled request must never resurrect stale audio.
    if (!PendingAudioLoads.Contains(LoadKey))
    {
        return;
    }

    USoundBase* Sound = Cast<USoundBase>(AssetPath.ResolveObject());
    if (!Sound)
    {
        if (Category == ShireAudioAssetPaths::SfxCategory)
        {
            PendingSpatialSfx.Remove(CueId);
        }
        PendingAudioLoads.Remove(LoadKey);
        UE_LOG(
            LogTemp,
            Warning,
            TEXT("AudioStreaming: load-complete-unresolved category=%s cue=%s"),
            *Category.ToString(),
            *CueId.ToString());
        return;
    }

    if (Category == ShireAudioAssetPaths::AmbienceCategory)
    {
        AmbienceCache.Add(CueId, Sound);
        if (ActiveAmbienceCue == CueId && !ActiveAmbienceComponent)
        {
            ActiveAmbienceComponent = UGameplayStatics::SpawnSound2D(
                this, Sound, 0.0f, 1.0f, 0.0f, nullptr, false, true);
            if (ActiveAmbienceComponent)
            {
                ActiveAmbienceComponent->FadeIn(0.55f, 1.0f);
            }
        }
    }
    else if (Category == ShireAudioAssetPaths::MusicCategory)
    {
        MusicCache.Add(CueId, Sound);
        if (ActiveMusicCue == CueId && !ActiveMusicComponent)
        {
            const float TargetVolume = bVoiceActive ? 0.36f : 1.0f;
            ActiveMusicComponent = UGameplayStatics::SpawnSound2D(
                this, Sound, 0.0f, 1.0f, 0.0f, nullptr, false, true);
            if (ActiveMusicComponent)
            {
                ActiveMusicComponent->FadeIn(0.95f, TargetVolume);
            }
        }
    }
    else if (Category == ShireAudioAssetPaths::SfxCategory)
    {
        SfxCache.Add(CueId, Sound);
        if (FPendingSpatialSfx* Pending = PendingSpatialSfx.Find(CueId))
        {
            UGameplayStatics::SpawnSoundAtLocation(
                this,
                Sound,
                Pending->Location,
                FRotator::ZeroRotator,
                Pending->VolumeMultiplier,
                Pending->PitchMultiplier,
                0.0f,
                SpatialSfxAttenuation,
                nullptr,
                true);
            PendingSpatialSfx.Remove(CueId);
        }
        else
        {
            UGameplayStatics::SpawnSound2D(
                this, Sound, 1.0f, 1.0f, 0.0f, nullptr, false, true);
        }
    }
    else if (Category == ShireAudioAssetPaths::VoiceCategory)
    {
        VoiceCache.Add(CueId, Sound);
        if (PendingVoiceCue == CueId)
        {
            StartVoicePlayback(CueId, Sound);
        }
    }

    PendingAudioLoads.Remove(LoadKey);
}

void UShireAudioSubsystem::ApplyMusicDuck(bool bDuck)
{
    bVoiceActive = bDuck;
    if (ActiveMusicComponent)
    {
        ActiveMusicComponent->SetVolumeMultiplier(bDuck ? 0.36f : 1.0f);
    }
}

bool UShireAudioSubsystem::CanPlaySfxNow(FName CueId, bool bStoryCritical)
{
    if (CueId == NAME_None)
    {
        return false;
    }

    const UWorld* World = GetWorld();
    if (!World)
    {
        return false;
    }

    const double Now = static_cast<double>(World->GetTimeSeconds());
    if (const double* LastTime = LastSfxPlaybackTimeSeconds.Find(CueId))
    {
        if ((Now - *LastTime) < static_cast<double>(MinSfxRepeatIntervalSeconds))
        {
            return false;
        }
    }

    if (!bStoryCritical)
    {
        const double WindowStart = Now - static_cast<double>(DecorativeSfxWindowSeconds);
        RecentDecorativeSfxStartTimes.RemoveAll(
            [WindowStart](double TimeSeconds)
            {
                return TimeSeconds < WindowStart;
            });

        if (RecentDecorativeSfxStartTimes.Num() >= MaxDecorativeSfxStartsPerWindow)
        {
            return false;
        }

        RecentDecorativeSfxStartTimes.Add(Now);
    }

    LastSfxPlaybackTimeSeconds.Add(CueId, Now);
    return true;
}

void UShireAudioSubsystem::SetAmbienceCue(FName CueId)
{
    if (CueId == ActiveAmbienceCue)
    {
        return;
    }

    CancelPendingAudioCategory(ShireAudioAssetPaths::AmbienceCategory);

    if (ActiveAmbienceComponent)
    {
        // Source 11 audio doctrine: ambience should transition as a physical world
        // layer rather than hard-cut whenever a story beat changes.
        UAudioComponent* FadingComponent = ActiveAmbienceComponent;
        ActiveAmbienceComponent = nullptr;
        FadingComponent->FadeOut(0.45f, 0.0f);
    }

    const FName Previous = ActiveAmbienceCue;
    ActiveAmbienceCue = CueId;
    OnAmbienceChanged.Broadcast(Previous, ActiveAmbienceCue);

    if (CueId != NAME_None)
    {
        if (USoundBase* Sound = ResolveCategorizedAsset(
                CueId,
                ShireAudioAssetPaths::Ambience,
                AmbienceCache,
                ShireAudioAssetPaths::AmbienceCategory))
        {
            ActiveAmbienceComponent = UGameplayStatics::SpawnSound2D(
                this, Sound, 0.0f, 1.0f, 0.0f, nullptr, false, true);
            if (ActiveAmbienceComponent)
            {
                ActiveAmbienceComponent->FadeIn(0.55f, 1.0f);
            }
        }
    }
}

void UShireAudioSubsystem::SetMusicCue(FName CueId)
{
    if (CueId == ActiveMusicCue)
    {
        return;
    }

    CancelPendingAudioCategory(ShireAudioAssetPaths::MusicCategory);

    if (ActiveMusicComponent)
    {
        UAudioComponent* FadingComponent = ActiveMusicComponent;
        ActiveMusicComponent = nullptr;
        FadingComponent->FadeOut(0.85f, 0.0f);
    }

    const FName Previous = ActiveMusicCue;
    ActiveMusicCue = CueId;
    OnMusicChanged.Broadcast(Previous, ActiveMusicCue);

    if (CueId != NAME_None)
    {
        if (USoundBase* Sound = ResolveCategorizedAsset(
                CueId,
                ShireAudioAssetPaths::Music,
                MusicCache,
                ShireAudioAssetPaths::MusicCategory))
        {
            const float TargetVolume = bVoiceActive ? 0.36f : 1.0f;
            ActiveMusicComponent = UGameplayStatics::SpawnSound2D(
                this, Sound, 0.0f, 1.0f, 0.0f, nullptr, false, true);
            if (ActiveMusicComponent)
            {
                ActiveMusicComponent->FadeIn(0.95f, TargetVolume);
            }
        }
    }
}

void UShireAudioSubsystem::PlaySfxCue(FName CueId)
{
    if (!CanPlaySfxNow(CueId, true))
    {
        return;
    }

    OnSfxRequested.Broadcast(CueId);

    if (USoundBase* Sound = ResolveCategorizedAsset(
            CueId,
            ShireAudioAssetPaths::SFX,
            SfxCache,
            ShireAudioAssetPaths::SfxCategory))
    {
        UGameplayStatics::SpawnSound2D(this, Sound, 1.0f, 1.0f, 0.0f, nullptr, false, true);
    }
}

void UShireAudioSubsystem::PlaySfxCueAtLocation(
    FName CueId,
    FVector WorldLocation,
    float VolumeMultiplier,
    float PitchMultiplier)
{
    if (!GetWorld() || !CanPlaySfxNow(CueId, false))
    {
        return;
    }

    OnSfxRequested.Broadcast(CueId);

    const FString Cue = CueId.ToString();
    const FString PackagePath = FString::Printf(TEXT("%s%s"), ShireAudioAssetPaths::SFX, *Cue);
    if (!FPackageName::DoesPackageExist(PackagePath))
    {
        // The runtime route is allowed to precede the approved audio bank. Missing
        // authored cues remain silent and never trigger synchronous loads or warnings.
        PendingSpatialSfx.Remove(CueId);
        return;
    }

    FPendingSpatialSfx& Pending = PendingSpatialSfx.FindOrAdd(CueId);
    Pending.Location = WorldLocation;
    Pending.VolumeMultiplier = FMath::Clamp(VolumeMultiplier, 0.0f, 2.0f);
    Pending.PitchMultiplier = FMath::Clamp(PitchMultiplier, 0.5f, 2.0f);

    if (USoundBase* Sound = ResolveCategorizedAsset(
            CueId,
            ShireAudioAssetPaths::SFX,
            SfxCache,
            ShireAudioAssetPaths::SfxCategory))
    {
        UGameplayStatics::SpawnSoundAtLocation(
            this,
            Sound,
            Pending.Location,
            FRotator::ZeroRotator,
            Pending.VolumeMultiplier,
            Pending.PitchMultiplier,
            0.0f,
            SpatialSfxAttenuation,
            nullptr,
            true);
        PendingSpatialSfx.Remove(CueId);
    }
}

USoundBase* UShireAudioSubsystem::ResolveVoiceAsset(FName CueId)
{
    if (CueId == NAME_None)
    {
        return nullptr;
    }

    if (TWeakObjectPtr<USoundBase>* Cached = VoiceCache.Find(CueId))
    {
        if (Cached->IsValid())
        {
            return Cached->Get();
        }
        VoiceCache.Remove(CueId);
    }

    const FString Cue = CueId.ToString();
    TArray<FString> Parts;
    Cue.ParseIntoArray(Parts, TEXT("_"), true);
    if (Parts.Num() < 2)
    {
        return nullptr;
    }

    const FString& Speaker = Parts[1];
    const FString PackagePath = FString::Printf(
        TEXT("/Game/Audio/Voice/%s/%s"), *Speaker, *Cue);
    if (!FPackageName::DoesPackageExist(PackagePath))
    {
        return nullptr;
    }

    const FSoftObjectPath AssetPath(FString::Printf(TEXT("%s.%s"), *PackagePath, *Cue));
    if (USoundBase* Sound = Cast<USoundBase>(AssetPath.ResolveObject()))
    {
        VoiceCache.Add(CueId, Sound);
        return Sound;
    }

    RequestAudioAssetAsync(ShireAudioAssetPaths::VoiceCategory, CueId, AssetPath);
    return nullptr;
}

AActor* UShireAudioSubsystem::ResolveVoiceSpeakerActor(FName CueId) const
{
    if (!GetWorld() || CueId == NAME_None)
    {
        return nullptr;
    }

    const FString Cue = CueId.ToString();
    TArray<FString> Parts;
    Cue.ParseIntoArray(Parts, TEXT("_"), true);
    if (Parts.Num() < 2)
    {
        return nullptr;
    }

    const FString Speaker = Parts[1];

    APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
    APawn* PlayerPawn = PC ? PC->GetPawn() : nullptr;

    if (UGameInstance* GI = GetGameInstance())
    {
        if (const UShireQuestSubsystem* Quests = GI->GetSubsystem<UShireQuestSubsystem>())
        {
            if (PlayerPawn && Quests->GetPlayableCharacterId().ToString().Equals(Speaker, ESearchCase::IgnoreCase))
            {
                return PlayerPawn;
            }
        }
    }

    TArray<AActor*> NPCs;
    UGameplayStatics::GetAllActorsOfClass(this, AShireNPC::StaticClass(), NPCs);

    AActor* Best = nullptr;
    float BestDistanceSq = TNumericLimits<float>::Max();
    for (AActor* Actor : NPCs)
    {
        AShireNPC* NPC = Cast<AShireNPC>(Actor);
        if (!NPC || !NPC->DisplayName.ToString().Equals(Speaker, ESearchCase::IgnoreCase))
        {
            continue;
        }

        const float DistanceSq = PlayerPawn
            ? FVector::DistSquared(PlayerPawn->GetActorLocation(), NPC->GetActorLocation())
            : 0.0f;

        if (DistanceSq < BestDistanceSq)
        {
            BestDistanceSq = DistanceSq;
            Best = NPC;
        }
    }

    return Best;
}

void UShireAudioSubsystem::HandleVoiceFinished()
{
    if (ActiveVoiceComponent)
    {
        ActiveVoiceComponent->OnAudioFinished.RemoveDynamic(this, &UShireAudioSubsystem::HandleVoiceFinished);
        ActiveVoiceComponent = nullptr;
    }

    PendingVoiceCue = NAME_None;
    ApplyMusicDuck(false);
    OnVoicePlaybackStateChanged.Broadcast(false);
}

void UShireAudioSubsystem::StartVoicePlayback(FName CueId, USoundBase* Sound)
{
    if (!Sound || !GetWorld() || PendingVoiceCue != CueId)
    {
        return;
    }

    if (AActor* SpeakerActor = ResolveVoiceSpeakerActor(CueId))
    {
        ActiveVoiceComponent = UGameplayStatics::SpawnSoundAttached(
            Sound,
            SpeakerActor->GetRootComponent(),
            NAME_None,
            FVector::ZeroVector,
            EAttachLocation::KeepRelativeOffset,
            false,
            1.0f,
            1.0f,
            0.0f,
            nullptr,
            nullptr,
            true);
    }
    else
    {
        ActiveVoiceComponent = UGameplayStatics::SpawnSound2D(
            this, Sound, 1.0f, 1.0f, 0.0f, nullptr, false, true);
    }

    if (ActiveVoiceComponent)
    {
        ActiveVoiceComponent->OnAudioFinished.AddDynamic(
            this, &UShireAudioSubsystem::HandleVoiceFinished);
        ApplyMusicDuck(true);
        OnVoicePlaybackStateChanged.Broadcast(true);
    }
}

void UShireAudioSubsystem::PlayVoiceCue(FName CueId)
{
    if (CueId == NAME_None)
    {
        return;
    }

    OnVoiceRequested.Broadcast(CueId);
    CancelPendingAudioCategory(ShireAudioAssetPaths::VoiceCategory);
    PendingVoiceCue = CueId;

    if (ActiveVoiceComponent)
    {
        ActiveVoiceComponent->OnAudioFinished.RemoveDynamic(
            this, &UShireAudioSubsystem::HandleVoiceFinished);
        ActiveVoiceComponent->Stop();
        ActiveVoiceComponent = nullptr;
        ApplyMusicDuck(false);
        OnVoicePlaybackStateChanged.Broadcast(false);
    }

    if (USoundBase* Sound = ResolveVoiceAsset(CueId))
    {
        StartVoicePlayback(CueId, Sound);
    }
}

void UShireAudioSubsystem::ClearPersistentAudio()
{
    SetAmbienceCue(NAME_None);
    SetMusicCue(NAME_None);
}

void UShireAudioSubsystem::HandleAmbienceRequest(FName CueId)
{
    SetAmbienceCue(CueId);
}

void UShireAudioSubsystem::HandleMusicRequest(FName CueId)
{
    SetMusicCue(CueId);
}

void UShireAudioSubsystem::HandleSfxRequest(FName CueId)
{
    PlaySfxCue(CueId);
}

void UShireAudioSubsystem::HandleVoiceRequest(FName CueId)
{
    PlayVoiceCue(CueId);
}