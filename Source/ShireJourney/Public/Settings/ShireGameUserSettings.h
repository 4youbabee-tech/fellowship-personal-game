#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameUserSettings.h"
#include "ShireGameUserSettings.generated.h"

UENUM(BlueprintType)
enum class EShireVideoPreset : uint8
{
    Performance UMETA(DisplayName="Performance"),
    CinematicBalanced UMETA(DisplayName="Cinematic Balanced"),
    High UMETA(DisplayName="High"),
    Ultra UMETA(DisplayName="Ultra"),
    Custom UMETA(DisplayName="Custom")
};

UENUM(BlueprintType)
enum class EShireWindowMode : uint8
{
    Fullscreen UMETA(DisplayName="Fullscreen"),
    Borderless UMETA(DisplayName="Borderless"),
    Windowed UMETA(DisplayName="Windowed")
};

USTRUCT(BlueprintType)
struct FShireScalabilitySettings
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Video")
    int32 ViewDistanceQuality = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Video")
    int32 AntiAliasingQuality = 2;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Video")
    int32 ShadowQuality = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Video")
    int32 PostProcessQuality = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Video")
    int32 TextureQuality = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Video")
    int32 EffectsQuality = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Video")
    int32 FoliageQuality = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Video")
    float ResolutionScalePercent = 100.0f;
};

USTRUCT(BlueprintType)
struct FShireDisplaySettings
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Video")
    int32 ResolutionX = 1280;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Video")
    int32 ResolutionY = 720;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Video")
    EShireWindowMode WindowMode = EShireWindowMode::Borderless;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Video")
    bool bVSync = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Video")
    float FrameRateLimit = 60.0f;
};

UCLASS(Config=GameUserSettings, ConfigDoNotCheckDefaults)
class SHIREJOURNEY_API UShireGameUserSettings : public UGameUserSettings
{
    GENERATED_BODY()

public:
    virtual void SetToDefaults() override;

    UFUNCTION(BlueprintPure, Category="Shire|Video")
    static UShireGameUserSettings* GetShireGameUserSettings();

    UFUNCTION(BlueprintPure, Category="Shire|Video")
    EShireVideoPreset GetActivePreset() const { return ActivePreset; }

    UFUNCTION(BlueprintPure, Category="Shire|Video")
    FShireScalabilitySettings GetCurrentScalabilitySettings() const;

    UFUNCTION(BlueprintPure, Category="Shire|Video")
    FShireDisplaySettings GetCurrentDisplaySettings() const;

    UFUNCTION(BlueprintCallable, Category="Shire|Video")
    void ApplyPreset(EShireVideoPreset Preset, bool bSave);

    UFUNCTION(BlueprintCallable, Category="Shire|Video")
    void ApplyCustomScalability(const FShireScalabilitySettings& Settings, bool bSave);

    UFUNCTION(BlueprintCallable, Category="Shire|Video")
    void ApplyDisplaySettings(const FShireDisplaySettings& Settings, bool bSave);

    UFUNCTION(BlueprintCallable, Category="Shire|Video")
    void ApplyAndSave();

private:
    UPROPERTY(Config)
    EShireVideoPreset ActivePreset = EShireVideoPreset::CinematicBalanced;

    static FShireScalabilitySettings MakePresetProfile(EShireVideoPreset Preset);
    void ApplyScalabilityProfile(const FShireScalabilitySettings& Settings);
    static EWindowMode::Type ToEngineWindowMode(EShireWindowMode Mode);
    static EShireWindowMode FromEngineWindowMode(EWindowMode::Type Mode);
};
