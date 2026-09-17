#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "TimerManager.h"
#include "ShireStoryPresentationSubsystem.generated.h"

UENUM(BlueprintType)
enum class EShireStoryPresentationMode : uint8
{
    Gameplay UMETA(DisplayName="Gameplay"),
    GameplayBlend UMETA(DisplayName="Gameplay Blend"),
    Cinematic UMETA(DisplayName="Cinematic")
};

USTRUCT(BlueprintType)
struct FShireStoryPresentationCue
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category="Story")
    FName StoryBeatId = NAME_None;

    UPROPERTY(BlueprintReadOnly, Category="Story")
    EShireStoryPresentationMode Mode = EShireStoryPresentationMode::Gameplay;

    UPROPERTY(BlueprintReadOnly, Category="Story")
    FName CameraCue = NAME_None;

    UPROPERTY(BlueprintReadOnly, Category="Story")
    FName DialogueCue = NAME_None;

    UPROPERTY(BlueprintReadOnly, Category="Story")
    FName AmbienceCue = NAME_None;

    UPROPERTY(BlueprintReadOnly, Category="Story")
    FName MusicCue = NAME_None;

    UPROPERTY(BlueprintReadOnly, Category="Story")
    FName SfxCue = NAME_None;

    UPROPERTY(BlueprintReadOnly, Category="Story")
    float SuggestedDuration = 0.0f;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnStoryPresentationRequested, FShireStoryPresentationCue, Cue);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnStoryCameraCueRequested, FName, CameraCue);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnStoryAmbienceCueRequested, FName, AmbienceCue);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnStoryMusicCueRequested, FName, MusicCue);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnStorySfxCueRequested, FName, SfxCue);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnStoryCinematicStateChanged, bool, bLocked);

UCLASS()
class SHIREJOURNEY_API UShireStoryPresentationSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    UPROPERTY(BlueprintAssignable, Category="Story Presentation")
    FOnStoryPresentationRequested OnStoryPresentationRequested;

    UPROPERTY(BlueprintAssignable, Category="Story Presentation")
    FOnStoryCameraCueRequested OnCameraCueRequested;

    UPROPERTY(BlueprintAssignable, Category="Story Presentation")
    FOnStoryAmbienceCueRequested OnAmbienceCueRequested;

    UPROPERTY(BlueprintAssignable, Category="Story Presentation")
    FOnStoryMusicCueRequested OnMusicCueRequested;

    UPROPERTY(BlueprintAssignable, Category="Story Presentation")
    FOnStorySfxCueRequested OnSfxCueRequested;

    UPROPERTY(BlueprintAssignable, Category="Story Presentation")
    FOnStoryCinematicStateChanged OnCinematicStateChanged;

    UFUNCTION(BlueprintPure, Category="Story Presentation")
    bool FindCue(FName StoryBeatId, FShireStoryPresentationCue& OutCue) const;

    UFUNCTION(BlueprintPure, Category="Story Presentation")
    FShireStoryPresentationCue GetActiveCue() const { return ActiveCue; }

    UFUNCTION(BlueprintCallable, Category="Story Presentation")
    void ReleaseCinematicLock();

private:
    UPROPERTY()
    TMap<FName, FShireStoryPresentationCue> CueLibrary;

    UPROPERTY()
    FShireStoryPresentationCue ActiveCue;

    bool bCinematicLocked = false;
    FTimerHandle CinematicReleaseTimer;

    UFUNCTION()
    void HandleStoryBeat(FName StoryBeatId);

    void BuildCueLibrary();
    void AddCue(FName StoryBeatId, EShireStoryPresentationMode Mode, FName CameraCue,
        FName DialogueCue, FName AmbienceCue, FName MusicCue, FName SfxCue,
        float SuggestedDuration = 0.0f);
};
