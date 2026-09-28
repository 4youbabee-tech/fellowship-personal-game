#include "ShireGameUserSettings.h"

#include "Engine/Engine.h"

namespace
{
    int32 ClampQuality(int32 Value)
    {
        return FMath::Clamp(Value, 0, 3);
    }
}

void UShireGameUserSettings::SetToDefaults()
{
    Super::SetToDefaults();

    ShireGraphicsPreset = EShireGraphicsPreset::Recommended;
    bShirePresetInitialized = true;

    // Recommended is deliberately image-first: native render scale, strong textures,
    // AA and post processing, while shadows/effects/foliage carry the first savings.
    ApplyPresetScalability(ShireGraphicsPreset);
    SetVSyncEnabled(false);
    SetFrameRateLimit(60.0f);
}

void UShireGameUserSettings::LoadSettings(bool bForceReload)
{
    Super::LoadSettings(bForceReload);

    if (!bShirePresetInitialized)
    {
        ShireGraphicsPreset = EShireGraphicsPreset::Recommended;
        bShirePresetInitialized = true;
        ApplyPresetScalability(ShireGraphicsPreset);
        SaveSettings();
    }
}

UShireGameUserSettings* UShireGameUserSettings::GetShireGameUserSettings()
{
    return GEngine
        ? Cast<UShireGameUserSettings>(GEngine->GetGameUserSettings())
        : nullptr;
}

void UShireGameUserSettings::ApplyGraphicsPreset(
    EShireGraphicsPreset Preset,
    bool bApplyImmediately)
{
    ShireGraphicsPreset = Preset;
    bShirePresetInitialized = true;

    if (Preset != EShireGraphicsPreset::Custom)
    {
        ApplyPresetScalability(Preset);
    }

    PersistAndOptionallyApply(bApplyImmediately);
}

void UShireGameUserSettings::ApplyCustomGraphicsQuality(
    int32 ViewDistance,
    int32 AntiAliasing,
    int32 Shadows,
    int32 PostProcessing,
    int32 Textures,
    int32 Effects,
    int32 Foliage,
    float ResolutionScalePercent,
    bool bApplyImmediately)
{
    ShireGraphicsPreset = EShireGraphicsPreset::Custom;
    bShirePresetInitialized = true;

    SetViewDistanceQuality(ClampQuality(ViewDistance));
    SetAntiAliasingQuality(ClampQuality(AntiAliasing));
    SetShadowQuality(ClampQuality(Shadows));
    SetPostProcessingQuality(ClampQuality(PostProcessing));
    SetTextureQuality(ClampQuality(Textures));
    SetVisualEffectQuality(ClampQuality(Effects));
    SetFoliageQuality(ClampQuality(Foliage));
    SetResolutionScaleValueEx(FMath::Clamp(ResolutionScalePercent, 70.0f, 100.0f));

    PersistAndOptionallyApply(bApplyImmediately);
}

void UShireGameUserSettings::ApplyDisplayPreferences(
    bool bEnableVSync,
    float FrameRateLimit,
    bool bApplyImmediately)
{
    SetVSyncEnabled(bEnableVSync);
    SetFrameRateLimit(FMath::Clamp(FrameRateLimit, 0.0f, 240.0f));
    PersistAndOptionallyApply(bApplyImmediately);
}

void UShireGameUserSettings::ApplyDisplayModeAndResolution(
    EWindowMode::Type WindowMode,
    FIntPoint Resolution,
    bool bApplyImmediately)
{
    const int32 Width = FMath::Clamp(Resolution.X, 960, 3840);
    const int32 Height = FMath::Clamp(Resolution.Y, 540, 2160);

    SetFullscreenMode(WindowMode);
    SetScreenResolution(FIntPoint(Width, Height));
    PersistAndOptionallyApply(bApplyImmediately);
}

FText UShireGameUserSettings::GetShireGraphicsPresetLabel() const
{
    return GetGraphicsPresetLabel(ShireGraphicsPreset);
}

FText UShireGameUserSettings::GetGraphicsPresetLabel(EShireGraphicsPreset Preset)
{
    switch (Preset)
    {
    case EShireGraphicsPreset::Performance:
        return FText::FromString(TEXT("Performance"));
    case EShireGraphicsPreset::Recommended:
        return FText::FromString(TEXT("Recommended"));
    case EShireGraphicsPreset::High:
        return FText::FromString(TEXT("High"));
    case EShireGraphicsPreset::Ultra:
        return FText::FromString(TEXT("Ultra"));
    case EShireGraphicsPreset::Custom:
    default:
        return FText::FromString(TEXT("Custom"));
    }
}

void UShireGameUserSettings::ApplyPresetScalability(EShireGraphicsPreset Preset)
{
    switch (Preset)
    {
    case EShireGraphicsPreset::Performance:
        SetViewDistanceQuality(1);
        SetAntiAliasingQuality(1);
        SetShadowQuality(0);
        SetPostProcessingQuality(1);
        SetTextureQuality(1);
        SetVisualEffectQuality(1);
        SetFoliageQuality(0);
        SetResolutionScaleValueEx(85.0f);
        break;

    case EShireGraphicsPreset::Recommended:
        SetViewDistanceQuality(2);
        SetAntiAliasingQuality(2);
        SetShadowQuality(1);
        SetPostProcessingQuality(2);
        SetTextureQuality(2);
        SetVisualEffectQuality(1);
        SetFoliageQuality(1);
        SetResolutionScaleValueEx(100.0f);
        break;

    case EShireGraphicsPreset::High:
        SetViewDistanceQuality(2);
        SetAntiAliasingQuality(3);
        SetShadowQuality(2);
        SetPostProcessingQuality(2);
        SetTextureQuality(3);
        SetVisualEffectQuality(2);
        SetFoliageQuality(2);
        SetResolutionScaleValueEx(100.0f);
        break;

    case EShireGraphicsPreset::Ultra:
        SetViewDistanceQuality(3);
        SetAntiAliasingQuality(3);
        SetShadowQuality(3);
        SetPostProcessingQuality(3);
        SetTextureQuality(3);
        SetVisualEffectQuality(3);
        SetFoliageQuality(3);
        SetResolutionScaleValueEx(100.0f);
        break;

    case EShireGraphicsPreset::Custom:
    default:
        break;
    }
}

void UShireGameUserSettings::PersistAndOptionallyApply(bool bApplyImmediately)
{
    if (bApplyImmediately)
    {
        ApplySettings(false);
    }
    else
    {
        SaveSettings();
    }
}
