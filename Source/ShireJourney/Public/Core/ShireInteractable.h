#pragma once

#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "ShireInteractable.generated.h"

class AActor;

UINTERFACE(BlueprintType)
class UShireInteractable : public UInterface
{
    GENERATED_BODY()
};

class SHIREJOURNEY_API IShireInteractable
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category="Interaction")
    void Interact(AActor* Interactor);
};
