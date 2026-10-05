#pragma once

#include "CoreMinimal.h"
#include "Commandlets/Commandlet.h"
#include "ShireFrodoAnimationImportCommandlet.generated.h"

UCLASS()
class SHIREJOURNEYEDITORTOOLS_API UShireFrodoAnimationImportCommandlet : public UCommandlet
{
    GENERATED_BODY()

public:
    UShireFrodoAnimationImportCommandlet();
    virtual int32 Main(const FString& Params) override;
};
