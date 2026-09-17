#include "ShireAudioSubsystem.h"

void UShireAudioSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    ActiveAmbienceCue = NAME_None;
    ActiveMusicCue = NAME_None;
}

void UShireAudioSubsystem::Deinitialize()
{
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
