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
#include "Sound/SoundBase.h"

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

    ClearPersistentAudio();
    Super::Deinitialize();
}

void UShireAudioSubsystem::SetAmbienceCue(FName CueId)
{
    if (CueId == ActiveAmbienceCue)
    {
        return;
    }

    const FName Previous = ActiveAmbienceCue;
    ActiveAmbienceCue = CueId;
    OnAmbienceChanged.Broadcast(Previous, ActiveAmbienceCue);
}

void UShireAudioSubsystem::SetMusicCue(FName CueId)
{
    if (CueId == ActiveMusicCue)
    {
        return;
    }

    const FName Previous = ActiveMusicCue;
    ActiveMusicCue = CueId;
    OnMusicChanged.Broadcast(Previous, ActiveMusicCue);
}

void UShireAudioSubsystem::PlaySfxCue(FName CueId)
{
    if (CueId != NAME_None)
    {
        OnSfxRequested.Broadcast(CueId);
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
    const FString AssetPath = FString::Printf(
        TEXT("/Game/Audio/Voice/%s/%s.%s"),
        *Speaker,
        *Cue,
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
        ActiveVoiceComponent = UGameplayStatics::SpawnSoundAtLocation(
            this,
            Sound,
            SpeakerActor->GetActorLocation(),
            SpeakerActor->GetActorRotation(),
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
