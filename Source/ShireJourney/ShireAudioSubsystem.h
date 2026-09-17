#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "ShireAudioSubsystem.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnShireAudioCueChanged, FName, PreviousCue, FName, NewCue);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnShireOneShotAudioRequested, FName, CueId);

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
};
