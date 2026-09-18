#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "ShireRouteState.h"
#include "ShireSaveGame.generated.h"

UCLASS()
class SHIREJOURNEY_API UShireSaveGame : public USaveGame
{
    GENERATED_BODY()

public:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Save")
    FVector PlayerLocation = FVector::ZeroVector;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Save")
    FRotator PlayerRotation = FRotator::ZeroRotator;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Save")
    float PlayerHealth = 100.0f;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Save")
    TMap<FName, int32> QuestStages;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Save")
    FName ActiveQuestId = NAME_None;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Save")
    FName CurrentChapterId = TEXT("P1C01");

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Save")
    TArray<FName> CompletedStoryBeats;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Save")
    FName CurrentRouteId = TEXT("FrodoMain");

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Save")
    FName CurrentEpisodeId = TEXT("P1C01_Main");

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Save")
    FName PlayableCharacterId = TEXT("Frodo");

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Save")
    FName CheckpointId = NAME_None;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Save")
    TMap<FName, FShireRouteProgress> RouteProgress;
};
