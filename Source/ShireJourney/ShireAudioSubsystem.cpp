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
#include "Sound/SoundBase.h"

namespace ShireAudioAssetPaths
{
    static const TCHAR* Ambience = TEXT("/Game/Audio/Ambience/");
    static const TCHAR* Music = TEXT("/Game/Audio/Music/");
    static const TCHAR* SFX = TEXT("/Game/Audio/SFX/");
}


void UShireAudioSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    Collection.InitializeDependency<UShireDialogueSubsystem>();
    Collection.InitializeDependency<UShireStoryPresentationSubsystem>();

    ActiveAmbienceCue = NAME_None;
    ActiveMusicCue = NAME_None;

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
    TMap<FName, USoundBase*>& Cache)
{
    if (CueId == NAME_None)
    {
        return nullptr;
    }

    if (USoundBase** Cached = Cache.Find(CueId))
    {
        return *Cached;
    }

    const FString Cue = CueId.ToString();
    const FString PackagePath = FString::Printf(TEXT("%s%s"), FolderPrefix, *Cue);
    if (!FPackageName::DoesPackageExist(PackagePath))
    {
        // Audio cues are intentionally allowed to be un-authored during the current
        // verification pass. Keep subtitle/story behavior without warning spam.
        Cache.Add(CueId, nullptr);
        return nullptr;
    }

    const FString AssetPath = FString::Printf(
        TEXT("%s.%s"),
        *PackagePath,
        *Cue);

    USoundBase* Sound = LoadObject<USoundBase>(nullptr, *AssetPath);
    Cache.Add(CueId, Sound);
    return Sound;
}

void UShireAudioSubsystem::ApplyMusicDuck(bool bDuck)
{
    bVoiceActive = bDuck;
    if (ActiveMusicComponent)
    {
        ActiveMusicComponent->SetVolumeMultiplier(bDuck ? 0.36f : 1.0f);
    }
}

void UShireAudioSubsystem::SetAmbienceCue(FName CueId)
{
    if (CueId == ActiveAmbienceCue)
    {
        return;
    }

    if (ActiveAmbienceComponent)
    {
        ActiveAmbienceComponent->Stop();
        ActiveAmbienceComponent = nullptr;
    }

    const FName Previous = ActiveAmbienceCue;
    ActiveAmbienceCue = CueId;
    OnAmbienceChanged.Broadcast(Previous, ActiveAmbienceCue);

    if (CueId != NAME_None)
    {
        if (USoundBase* Sound = ResolveCategorizedAsset(CueId, ShireAudioAssetPaths::Ambience, AmbienceCache))
        {
            ActiveAmbienceComponent = UGameplayStatics::SpawnSound2D(
                this, Sound, 1.0f, 1.0f, 0.0f, nullptr, false, false);
        }
    }
}

void UShireAudioSubsystem::SetMusicCue(FName CueId)
{
    if (CueId == ActiveMusicCue)
    {
        return;
    }

    if (ActiveMusicComponent)
    {
        ActiveMusicComponent->Stop();
        ActiveMusicComponent = nullptr;
    }

    const FName Previous = ActiveMusicCue;
    ActiveMusicCue = CueId;
    OnMusicChanged.Broadcast(Previous, ActiveMusicCue);

    if (CueId != NAME_None)
    {
        if (USoundBase* Sound = ResolveCategorizedAsset(CueId, ShireAudioAssetPaths::Music, MusicCache))
        {
            ActiveMusicComponent = UGameplayStatics::SpawnSound2D(
                this, Sound, bVoiceActive ? 0.36f : 1.0f, 1.0f, 0.0f, nullptr, false, false);
        }
    }
}

void UShireAudioSubsystem::PlaySfxCue(FName CueId)
{
    if (CueId == NAME_None)
    {
        return;
    }

    OnSfxRequested.Broadcast(CueId);

    if (USoundBase* Sound = ResolveCategorizedAsset(CueId, ShireAudioAssetPaths::SFX, SfxCache))
    {
        UGameplayStatics::SpawnSound2D(this, Sound, 1.0f, 1.0f, 0.0f, nullptr, false, true);
    }
}

USoundBase* UShireAudioSubsystem::ResolveVoiceAsset(FName CueId)
{
    if (CueId == NAME_None)
    {
        return nullptr;
    }

    if (USoundBase** Cached = VoiceCache.Find(CueId))
    {
        return *Cached;
    }

    const FString Cue = CueId.ToString();
    TArray<FString> Parts;
    Cue.ParseIntoArray(Parts, TEXT("_"), true);
    if (Parts.Num() < 2)
    {
        VoiceCache.Add(CueId, nullptr);
        return nullptr;
    }

    const FString& Speaker = Parts[1];
    const FString PackagePath = FString::Printf(
        TEXT("/Game/Audio/Voice/%s/%s"),
        *Speaker,
        *Cue);
    if (!FPackageName::DoesPackageExist(PackagePath))
    {
        VoiceCache.Add(CueId, nullptr);
        return nullptr;
    }

    const FString AssetPath = FString::Printf(
        TEXT("%s.%s"),
        *PackagePath,
        *Cue);

    USoundBase* Sound = LoadObject<USoundBase>(nullptr, *AssetPath);
    VoiceCache.Add(CueId, Sound);
    return Sound;
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

    ApplyMusicDuck(false);
    OnVoicePlaybackStateChanged.Broadcast(false);
}

void UShireAudioSubsystem::PlayVoiceCue(FName CueId)
{
    if (CueId == NAME_None)
    {
        return;
    }

    // Keep the logical event even when the actual SoundWave/SoundCue has not been authored yet.
    // Dialogue subtitles therefore remain functional while production voice assets are filled in.
    OnVoiceRequested.Broadcast(CueId);

    USoundBase* Sound = ResolveVoiceAsset(CueId);
    if (!Sound || !GetWorld())
    {
        return;
    }

    if (ActiveVoiceComponent)
    {
        ActiveVoiceComponent->OnAudioFinished.RemoveDynamic(this, &UShireAudioSubsystem::HandleVoiceFinished);
        ActiveVoiceComponent->Stop();
        ActiveVoiceComponent = nullptr;
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
            this,
            Sound,
            1.0f,
            1.0f,
            0.0f,
            nullptr,
            false,
            true);
    }

    if (ActiveVoiceComponent)
    {
        ActiveVoiceComponent->OnAudioFinished.AddDynamic(this, &UShireAudioSubsystem::HandleVoiceFinished);
        ApplyMusicDuck(true);
        OnVoicePlaybackStateChanged.Broadcast(true);
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
