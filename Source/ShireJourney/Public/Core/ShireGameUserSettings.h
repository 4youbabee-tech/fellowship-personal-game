#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameUserSettings.h"
#include "ShireGameUserSettings.generated.h"

UENUM(BlueprintType)
enum class EShireGraphicsPreset : uint8
{
    Performance UMETA(DisplayName="Performance"),
    Recommended UMETA(DisplayName="Recommended"),
    High UMETA(DisplayName="High"),
    Ultra UMETA(DisplayName="Ultra"),
    Custom UMETA(DisplayName="Custom")
};

UCLASS(Config=GameUserSettings)
class SHIREJOURNEY_API UShireGameUserSettings : public UGameUserSettings
{
    GENERATED_BODY()

public:
    virtual void SetToDefaults() override;
    virtual void LoadSettings(bool bForceReload = false) override;

    UFUNCTION(BlueprintPure, Category="Settings|Graphics")
    static UShireGameUserSettings* GetShireGameUserSettings();

    UFUNCTION(BlueprintCallable, Category="Settings|Graphics")
    void ApplyGraphicsPreset(EShireGraphicsPreset Preset, bool bApplyImmediately = true);

    UFUNCTION(BlueprintCallable, Category="Settings|Graphics")
    void ApplyCustomGraphicsQuality(
        int32 ViewDistance,
        int32 AntiAliasing,
        int32 Shadows,
        int32 PostProcessing,
        int32 Textures,
        int32 Effects,
        int32 Foliage,
        float ResolutionScalePercent,
        bool bApplyImmediately = true);

    UFUNCTION(BlueprintCallable, Category="Settings|Graphics")
    void ApplyDisplayPreferences(bool bEnableVSync, float FrameRateLimit, bool bApplyImmediately = true);

    UFUNCTION(BlueprintCallable, Category="Settings|Graphics")
    void ApplyDisplayModeAndResolution(
        EWindowMode::Type WindowMode,
        FIntPoint Resolution,
        bool bApplyImmediately = true);

    UFUNCTION(BlueprintPure, Category="Settings|Graphics")
    EShireGraphicsPreset GetShireGraphicsPreset() const { return ShireGraphicsPreset; }

    UFUNCTION(BlueprintPure, Category="Settings|Graphics")
    FText GetShireGraphicsPresetLabel() const;

    UFUNCTION(BlueprintPure, Category="Settings|Graphics")
    static FText GetGraphicsPresetLabel(EShireGraphicsPreset Preset);

private:
    void ApplyPresetScalability(EShireGraphicsPreset Preset);
    void PersistAndOptionallyApply(bool bApplyImmediately);

    UPROPERTY(Config)
    EShireGraphicsPreset ShireGraphicsPreset = EShireGraphicsPreset::Recommended;

    UPROPERTY(Config)
    bool bShirePresetInitialized = false;
};
