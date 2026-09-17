#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "ShireDialogueSubsystem.generated.h"

USTRUCT(BlueprintType)
struct FShireDialogueLine
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category="Dialogue")
    FText Speaker;

    UPROPERTY(BlueprintReadOnly, Category="Dialogue")
    FText Subtitle;

    // Logical ID only. Final voice assets are intentionally not hard referenced yet.
    UPROPERTY(BlueprintReadOnly, Category="Dialogue")
    FName VoiceCue = NAME_None;

    UPROPERTY(BlueprintReadOnly, Category="Dialogue")
    float Duration = 4.0f;
};

USTRUCT()
struct FShireDialogueSequence
{
    GENERATED_BODY()

    UPROPERTY()
    TArray<FShireDialogueLine> Lines;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnShireSubtitleChanged, FShireDialogueLine, Line);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnShireDialogueStateChanged, bool, bPlaying);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnShireVoiceCueRequested, FName, VoiceCue);

UCLASS()
class SHIREJOURNEY_API UShireDialogueSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    UPROPERTY(BlueprintAssignable, Category="Dialogue")
    FOnShireSubtitleChanged OnSubtitleChanged;

    UPROPERTY(BlueprintAssignable, Category="Dialogue")
    FOnShireDialogueStateChanged OnDialogueStateChanged;

    // An audio implementation can bind to this later and resolve VoiceCue IDs to SoundWave/SoundCue assets.
    UPROPERTY(BlueprintAssignable, Category="Dialogue")
    FOnShireVoiceCueRequested OnVoiceCueRequested;

    UFUNCTION(BlueprintCallable, Category="Dialogue")
    bool PlayDialogueCue(FName DialogueCue);

    UFUNCTION(BlueprintCallable, Category="Dialogue")
    void StopDialogue();

    UFUNCTION(BlueprintPure, Category="Dialogue")
    bool IsDialoguePlaying() const { return bPlaying; }

    UFUNCTION(BlueprintPure, Category="Dialogue")
    FName GetActiveDialogueCue() const { return ActiveDialogueCue; }

    UFUNCTION(BlueprintPure, Category="Dialogue")
    FShireDialogueLine GetCurrentLine() const { return CurrentLine; }

private:
    UPROPERTY()
    TMap<FName, FShireDialogueSequence> DialogueLibrary;

    UPROPERTY()
    TArray<FShireDialogueLine> PendingLines;

    UPROPERTY()
    FShireDialogueLine CurrentLine;

    UPROPERTY()
    FName ActiveDialogueCue = NAME_None;

    bool bPlaying = false;
    FTimerHandle AdvanceTimerHandle;

    void BuildDialogueLibrary();
    void AddSequence(FName DialogueCue, std::initializer_list<FShireDialogueLine> Lines);

    UFUNCTION()
    void AdvanceQueue();
};
