#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "ShireGameMode.generated.h"

UCLASS()
class SHIREJOURNEY_API AShireGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    AShireGameMode();

protected:
    virtual void BeginPlay() override;
};
