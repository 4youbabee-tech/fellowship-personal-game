#pragma once

#include "CoreMinimal.h"
#include "Commandlets/Commandlet.h"
#include "ShireProductionImportCommandlet.generated.h"

UCLASS()
class SHIREJOURNEYEDITORTOOLS_API UShireProductionImportCommandlet : public UCommandlet
{
    GENERATED_BODY()
public:
    UShireProductionImportCommandlet();
    virtual int32 Main(const FString& Params) override;
};
