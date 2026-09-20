#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ShireStoryPresentationSubsystem.h"
#include "StoryPresentationDirector.generated.h"

class ACameraActor;
class APlayerController;

UCLASS()
class SHIREJOURNEY_API AStoryPresentationDirector : public AActor
{
    GENERATED_BODY()

public:
    AStoryPresentationDirector();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    struct FShotProfile
    {
        float BackDistance = 420.0f;
        float SideDistance = 120.0f;
        float Height = 170.0f;
        float FocusDistance = 620.0f;
        float FocusHeight = 70.0f;
        float Fov = 72.0f;
        float HoldSeconds = 1.35f;
        float BlendIn = 0.28f;
        float BlendOut = 0.32f;
        bool bPreferNamedSubject = false;
        FName SubjectName = NAME_None;
    };

    UPROPERTY(Transient)
    ACameraActor* RuntimeCamera = nullptr;

    TWeakObjectPtr<AActor> PreviousViewTarget;
    FTimerHandle ReleaseTimer;

    UFUNCTION()
    void HandlePresentationCue(FShireStoryPresentationCue Cue);

    UFUNCTION()
    void HandleChapterChanged(FName PreviousChapterId, FName NewChapterId);

    void ReleaseCamera();
    FShotProfile ResolveShotProfile(const FShireStoryPresentationCue& Cue) const;
    AActor* ResolveNamedSubject(FName SubjectName) const;
    FVector ResolveSafeCameraLocation(
        const FVector& DesiredLocation,
        const FVector& FocusLocation,
        AActor* FocusActor,
        APawn* PlayerPawn) const;
};
