#include "ShireGameUserSettings.h"

#include "Engine/Engine.h"

namespace
{
int32 ClampQuality(int32 Value)
{
    return FMath::Clamp(Value, 0, 3);
}

float ClampResolutionScale(float Value)
{
    return FMath::Clamp(Value, 50.0f, 100.0f);
}

float ClampFrameRate(float Value)
{
    if (Value <= 0.0f)
    {
        return 0.0f;
    }
    return FMath::Clamp(Value, 30.0f, 240.0f);
}
}

void UShireGameUserSettings::SetToDefaults()
{
    Super::SetToDefaults();

    ActivePreset = EShireVideoPreset::CinematicBalanced;
    ApplyScalabilityProfile(MakePresetProfile(ActivePreset));

    SetScreenResolution(FIntPoint(1280, 720));
    SetFullscreenMode(EWindowMode::WindowedFullscreen);
    SetVSyncEnabled(false);
    SetFrameRateLimit(60.0f);
}

UShireGameUserSettings* UShireGameUserSettings::GetShireGameUserSettings()
{
    return GEngine ? Cast<UShireGameUserSettings>(GEngine->GetGameUserSettings()) : nullptr;
}

FShireScalabilitySettings UShireGameUserSettings::GetCurrentScalabilitySettings() const
{
    FShireScalabilitySettings Result;
    Result.ViewDistanceQuality = GetViewDistanceQuality();
    Result.AntiAliasingQuality = GetAntiAliasingQuality();
    Result.ShadowQuality = GetShadowQuality();
    Result.PostProcessQuality = GetPostProcessingQuality();
    Result.TextureQuality = GetTextureQuality();
    Result.EffectsQuality = GetVisualEffectQuality();
    Result.FoliageQuality = GetFoliageQuality();
    Result.ResolutionScalePercent = FMath::Clamp(ScalabilityQuality.ResolutionQuality, 50.0f, 100.0f);
    return Result;
}

FShireDisplaySettings UShireGameUserSettings::GetCurrentDisplaySettings() const
{
    const FIntPoint Resolution = GetScreenResolution();

    FShireDisplaySettings Result;
    Result.ResolutionX = Resolution.X;
    Result.ResolutionY = Resolution.Y;
    Result.WindowMode = FromEngineWindowMode(GetFullscreenMode());
    Result.bVSync = IsVSyncEnabled();
    Result.FrameRateLimit = GetFrameRateLimit();
    return Result;
}

void UShireGameUserSettings::ApplyPreset(EShireVideoPreset Preset, bool bSave)
{
    ActivePreset = Preset;

    if (Preset != EShireVideoPreset::Custom)
    {
        ApplyScalabilityProfile(MakePresetProfile(Preset));
    }

    ApplyNonResolutionSettings();

    if (bSave)
    {
        SaveSettings();
    }
}

void UShireGameUserSettings::ApplyCustomScalability(const FShireScalabilitySettings& Settings, bool bSave)
{
    ActivePreset = EShireVideoPreset::Custom;
    ApplyScalabilityProfile(Settings);
    ApplyNonResolutionSettings();

    if (bSave)
    {
        SaveSettings();
    }
}

void UShireGameUserSettings::ApplyDisplaySettings(const FShireDisplaySettings& Settings, bool bSave)
{
    const int32 Width = FMath::Clamp(Settings.ResolutionX, 960, 7680);
    const int32 Height = FMath::Clamp(Settings.ResolutionY, 540, 4320);

    SetScreenResolution(FIntPoint(Width, Height));
    SetFullscreenMode(ToEngineWindowMode(Settings.WindowMode));
    SetVSyncEnabled(Settings.bVSync);
    SetFrameRateLimit(ClampFrameRate(Settings.FrameRateLimit));

    ApplyResolutionSettings(false);
    ApplyNonResolutionSettings();
    ConfirmVideoMode();

    if (bSave)
    {
        SaveSettings();
    }
}

void UShireGameUserSettings::ApplyAndSave()
{
    ApplyResolutionSettings(false);
    ApplyNonResolutionSettings();
    ConfirmVideoMode();
    SaveSettings();
}

FShireScalabilitySettings UShireGameUserSettings::MakePresetProfile(EShireVideoPreset Preset)
{
    FShireScalabilitySettings Profile;

    switch (Preset)
    {
    case EShireVideoPreset::Performance:
        Profile.ViewDistanceQuality = 0;
        Profile.AntiAliasingQuality = 1;
        Profile.ShadowQuality = 0;
        Profile.PostProcessQuality = 0;
        Profile.TextureQuality = 0;
        Profile.EffectsQuality = 0;
        Profile.FoliageQuality = 0;
        Profile.ResolutionScalePercent = 85.0f;
        break;

    case EShireVideoPreset::High:
        Profile.ViewDistanceQuality = 2;
        Profile.AntiAliasingQuality = 2;
        Profile.ShadowQuality = 2;
        Profile.PostProcessQuality = 2;
        Profile.TextureQuality = 2;
        Profile.EffectsQuality = 2;
        Profile.FoliageQuality = 2;
        Profile.ResolutionScalePercent = 100.0f;
        break;

    case EShireVideoPreset::Ultra:
        Profile.ViewDistanceQuality = 3;
        Profile.AntiAliasingQuality = 3;
        Profile.ShadowQuality = 3;
        Profile.PostProcessQuality = 3;
        Profile.TextureQuality = 3;
        Profile.EffectsQuality = 3;
        Profile.FoliageQuality = 3;
        Profile.ResolutionScalePercent = 100.0f;
        break;

    case EShireVideoPreset::Custom:
    case EShireVideoPreset::CinematicBalanced:
    default:
        Profile.ViewDistanceQuality = 1;
        Profile.AntiAliasingQuality = 2;
        Profile.ShadowQuality = 1;
        Profile.PostProcessQuality = 1;
        Profile.TextureQuality = 1;
        Profile.EffectsQuality = 1;
        Profile.FoliageQuality = 1;
        Profile.ResolutionScalePercent = 100.0f;
        break;
    }

    return Profile;
}

void UShireGameUserSettings::ApplyScalabilityProfile(const FShireScalabilitySettings& Settings)
{
    SetViewDistanceQuality(ClampQuality(Settings.ViewDistanceQuality));
    SetAntiAliasingQuality(ClampQuality(Settings.AntiAliasingQuality));
    SetShadowQuality(ClampQuality(Settings.ShadowQuality));
    SetPostProcessingQuality(ClampQuality(Settings.PostProcessQuality));
    SetTextureQuality(ClampQuality(Settings.TextureQuality));
    SetVisualEffectQuality(ClampQuality(Settings.EffectsQuality));
    SetFoliageQuality(ClampQuality(Settings.FoliageQuality));
    SetResolutionScaleValueEx(ClampResolutionScale(Settings.ResolutionScalePercent));
}

EWindowMode::Type UShireGameUserSettings::ToEngineWindowMode(EShireWindowMode Mode)
{
    switch (Mode)
    {
    case EShireWindowMode::Fullscreen:
        return EWindowMode::Fullscreen;
    case EShireWindowMode::Windowed:
        return EWindowMode::Windowed;
    case EShireWindowMode::Borderless:
    default:
        return EWindowMode::WindowedFullscreen;
    }
}

EShireWindowMode UShireGameUserSettings::FromEngineWindowMode(EWindowMode::Type Mode)
{
    switch (Mode)
    {
    case EWindowMode::Fullscreen:
        return EShireWindowMode::Fullscreen;
    case EWindowMode::Windowed:
        return EShireWindowMode::Windowed;
    case EWindowMode::WindowedFullscreen:
    default:
        return EShireWindowMode::Borderless;
    }
}
