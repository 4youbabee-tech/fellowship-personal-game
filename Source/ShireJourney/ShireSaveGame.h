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
    static constexpr int32 CurrentSchemaVersion = 5;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Save")
    int32 SaveSchemaVersion = CurrentSchemaVersion;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Save")
    int64 SnapshotCreatedUnixSeconds = 0;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Save")
    FVector PlayerLocation = FVector::ZeroVector;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Save")
    FRotator PlayerRotation = FRotator::ZeroRotator;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Save")
    float PlayerHealth = 100.0f;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="PlayerLife")
    float PlayerStamina = 100.0f;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="PlayerLife")
    float PlayerResolve = 100.0f;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="PlayerLife")
    int32 PlayerSupplies = 3;

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

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Save")
    TMap<FName, FShireNPCMemoryBucket> NPCMemoryState;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Exploration")
    TArray<FName> JourneyDiscoveryIds;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Exploration")
    int32 JourneyInsight = 0;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Exploration")
    TArray<FName> JourneyInsightMilestones;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Progression")
    TMap<FName, int32> ProgressionXP;
};
