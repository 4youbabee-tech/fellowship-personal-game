#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "ShireAudioSubsystem.generated.h"

class UAudioComponent;
class USoundBase;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnShireAudioCueChanged, FName, PreviousCue, FName, NewCue);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnShireOneShotAudioRequested, FName, CueId);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnShireVoicePlaybackStateChanged, bool, bSpeaking);

UCLASS()
class SHIREJOURNEY_API UShireAudioSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    UPROPERTY(BlueprintAssignable, Category="Audio")
    FOnShireAudioCueChanged OnAmbienceChanged;

    UPROPERTY(BlueprintAssignable, Category="Audio")
    FOnShireAudioCueChanged OnMusicChanged;

    UPROPERTY(BlueprintAssignable, Category="Audio")
    FOnShireOneShotAudioRequested OnSfxRequested;

    UPROPERTY(BlueprintAssignable, Category="Audio")
    FOnShireOneShotAudioRequested OnVoiceRequested;

    UPROPERTY(BlueprintAssignable, Category="Audio")
    FOnShireVoicePlaybackStateChanged OnVoicePlaybackStateChanged;

    UFUNCTION(BlueprintCallable, Category="Audio")
    void SetAmbienceCue(FName CueId);

    UFUNCTION(BlueprintCallable, Category="Audio")
    void SetMusicCue(FName CueId);

    UFUNCTION(BlueprintCallable, Category="Audio")
    void PlaySfxCue(FName CueId);

    UFUNCTION(BlueprintCallable, Category="Audio")
    void PlayVoiceCue(FName CueId);

    UFUNCTION(BlueprintCallable, Category="Audio")
    void ClearPersistentAudio();

    UFUNCTION(BlueprintPure, Category="Audio")
    FName GetActiveAmbienceCue() const { return ActiveAmbienceCue; }

    UFUNCTION(BlueprintPure, Category="Audio")
    FName GetActiveMusicCue() const { return ActiveMusicCue; }

private:
    UPROPERTY()
    FName ActiveAmbienceCue = NAME_None;

    UPROPERTY()
    FName ActiveMusicCue = NAME_None;

    UPROPERTY(Transient)
    UAudioComponent* ActiveVoiceComponent = nullptr;

    UPROPERTY(Transient)
    UAudioComponent* ActiveAmbienceComponent = nullptr;

    UPROPERTY(Transient)
    UAudioComponent* ActiveMusicComponent = nullptr;

    UPROPERTY(Transient)
    TMap<FName, USoundBase*> VoiceCache;

    UPROPERTY(Transient)
    TMap<FName, USoundBase*> AmbienceCache;

    UPROPERTY(Transient)
    TMap<FName, USoundBase*> MusicCache;

    UPROPERTY(Transient)
    TMap<FName, USoundBase*> SfxCache;

    bool bVoiceActive = false;

    USoundBase* ResolveVoiceAsset(FName CueId);
    USoundBase* ResolveCategorizedAsset(FName CueId, const TCHAR* FolderPrefix, TMap<FName, USoundBase*>& Cache);
    void ApplyMusicDuck(bool bDuck);
    AActor* ResolveVoiceSpeakerActor(FName CueId) const;

    UFUNCTION()
    void HandleVoiceFinished();

    UFUNCTION()
    void HandleAmbienceRequest(FName CueId);

    UFUNCTION()
    void HandleMusicRequest(FName CueId);

    UFUNCTION()
    void HandleSfxRequest(FName CueId);

    UFUNCTION()
    void HandleVoiceRequest(FName CueId);
};
