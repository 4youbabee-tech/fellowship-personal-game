#pragma once

#include "CoreMinimal.h"
#include "Engine/StreamableManager.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "UObject/SoftObjectPath.h"
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

    // Weak caches do not pin every sound for the GameInstance lifetime. The active
    // audio component owns a playing sound; streamable handles own only in-flight loads.
    TMap<FName, TWeakObjectPtr<USoundBase>> VoiceCache;
    TMap<FName, TWeakObjectPtr<USoundBase>> AmbienceCache;
    TMap<FName, TWeakObjectPtr<USoundBase>> MusicCache;
    TMap<FName, TWeakObjectPtr<USoundBase>> SfxCache;

    FStreamableManager StreamableManager;
    TMap<FName, TSharedPtr<FStreamableHandle>> PendingAudioLoads;
    FName PendingVoiceCue = NAME_None;
    bool bVoiceActive = false;

    USoundBase* ResolveVoiceAsset(FName CueId);
    USoundBase* ResolveCategorizedAsset(
        FName CueId,
        const TCHAR* FolderPrefix,
        TMap<FName, TWeakObjectPtr<USoundBase>>& Cache,
        FName Category);
    void RequestAudioAssetAsync(FName Category, FName CueId, const FSoftObjectPath& AssetPath);
    void HandleAsyncAudioReady(
        FName Category,
        FName CueId,
        FSoftObjectPath AssetPath,
        FName LoadKey);
    void CancelPendingAudioCategory(FName Category);
    void StartVoicePlayback(FName CueId, USoundBase* Sound);
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
