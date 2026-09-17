#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
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
    TMap<FName, int32> QuestStages;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Save")
    FName ActiveQuestId = NAME_None;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Save")
    FName CurrentChapterId = TEXT("P1C01");
};
