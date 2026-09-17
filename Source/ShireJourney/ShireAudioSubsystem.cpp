#include "ShireAudioSubsystem.h"

#include "ShireDialogueSubsystem.h"
#include "ShireStoryPresentationSubsystem.h"
#include "Engine/GameInstance.h"

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

void UShireAudioSubsystem::PlayVoiceCue(FName CueId)
{
    if (CueId != NAME_None)
    {
        OnVoiceRequested.Broadcast(CueId);
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
