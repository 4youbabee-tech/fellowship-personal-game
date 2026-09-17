#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "ShireHUD.generated.h"

UCLASS()
class SHIREJOURNEY_API AShireHUD : public AHUD
{
    GENERATED_BODY()

public:
    virtual void DrawHUD() override;

    UFUNCTION(BlueprintCallable, Category="HUD")
    void ShowDialogue(const FText& Speaker, const FText& Line, float Duration = 6.0f);

    UFUNCTION(BlueprintCallable, Category="HUD")
    void ShowAlert(const FText& Message, float Duration = 3.0f);

private:
    FText DialogueSpeaker;
    FText DialogueLine;
    FText AlertMessage;
    float DialogueUntilTime = 0.0f;
    float AlertUntilTime = 0.0f;
};
