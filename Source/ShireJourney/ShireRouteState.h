#pragma once

#include "CoreMinimal.h"
#include "ShireRouteState.generated.h"

USTRUCT(BlueprintType)
struct FShireRouteProgress
{
    GENERATED_BODY()

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Route")
    TMap<FName, int32> QuestStages;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Route")
    FName ActiveQuestId = NAME_None;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Route")
    FName CurrentChapterId = TEXT("P1C01");

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Route")
    FName EpisodeId = NAME_None;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Route")
    FName PlayableCharacterId = TEXT("Frodo");

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Route")
    TArray<FName> CompletedStoryBeats;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Route")
    bool bHasPlayerTransform = false;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Route")
    FVector PlayerLocation = FVector::ZeroVector;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Route")
    FRotator PlayerRotation = FRotator::ZeroRotator;
};
