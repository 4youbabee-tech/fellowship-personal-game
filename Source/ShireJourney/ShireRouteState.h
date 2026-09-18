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

USTRUCT(BlueprintType)
struct FShireNPCMemoryEvent
{
    GENERATED_BODY()

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NPCMemory")
    FName EventId = NAME_None;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NPCMemory")
    FName ChapterId = NAME_None;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NPCMemory")
    int32 Priority = 0;
};

USTRUCT(BlueprintType)
struct FShireNPCMemoryBucket
{
    GENERATED_BODY()

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NPCMemory")
    FName CanonicalProfileId = NAME_None;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NPCMemory")
    FName RouteId = NAME_None;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NPCMemory")
    TArray<FShireNPCMemoryEvent> Events;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="NPCMemory")
    TMap<FName, int32> RelationshipDeltas;
};
