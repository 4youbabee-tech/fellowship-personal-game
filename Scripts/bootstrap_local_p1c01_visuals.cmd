@echo off
setlocal EnableExtensions EnableDelayedExpansion

for %%I in ("%~dp0..") do set "WORKSPACE=%%~fI"
set "GITHUB_WORKSPACE=%WORKSPACE%"
set "PROJECT=%WORKSPACE%\ShireJourney.uproject"
set "UE_ROOT=C:\Program Files\Epic Games\UE_4.27"
set "EDITOR=%UE_ROOT%\Engine\Binaries\Win64\UE4Editor.exe"
set "EDITORCMD=%UE_ROOT%\Engine\Binaries\Win64\UE4Editor-Cmd.exe"

if not exist "%PROJECT%" (
  echo P1C01_LOCAL_VISUAL_BOOTSTRAP_FAIL reason=project_missing path="%PROJECT%"
  exit /b 61
)
if not exist "%EDITORCMD%" (
  echo P1C01_LOCAL_VISUAL_BOOTSTRAP_FAIL reason=ue4_editor_cmd_missing path="%EDITORCMD%"
  exit /b 62
)
if not exist "%EDITOR%" (
  echo P1C01_LOCAL_VISUAL_BOOTSTRAP_FAIL reason=ue4_editor_missing path="%EDITOR%"
  exit /b 63
)

echo.
echo ============================================================
echo SHIRE JOURNEY - P1C01 LOCAL VISUAL BOOTSTRAP
echo ============================================================
echo This reuses the existing production importer.
echo Close UE4Editor before continuing; the preflight fails closed if it is running.
echo.

for /f %%C in ('powershell.exe -NoProfile -Command "(Get-ChildItem -LiteralPath '%WORKSPACE%\SourceAssets\Production' -Recurse -File -ErrorAction Stop ^| Measure-Object).Count"') do set "SOURCE_FILES=%%C"
echo P1C01_LOCAL_VISUAL_SOURCE_FILES count=!SOURCE_FILES!

call "%WORKSPACE%\Scripts\ci_import_production_assets.cmd"
set "IMPORT_EXIT=!ERRORLEVEL!"
if not "!IMPORT_EXIT!"=="0" (
  echo P1C01_LOCAL_VISUAL_BOOTSTRAP_FAIL reason=production_import exit=!IMPORT_EXIT!
  exit /b !IMPORT_EXIT!
)

for /f %%C in ('powershell.exe -NoProfile -Command "if(Test-Path -LiteralPath '%WORKSPACE%\Content\Production'){(Get-ChildItem -LiteralPath '%WORKSPACE%\Content\Production' -Recurse -File -Filter '*.uasset' -ErrorAction Stop ^| Measure-Object).Count}else{0}"') do set "UASSET_COUNT=%%C"
if "!UASSET_COUNT!"=="0" (
  echo P1C01_LOCAL_VISUAL_BOOTSTRAP_FAIL reason=no_generated_uassets root="%WORKSPACE%\Content\Production"
  exit /b 64
)

echo P1C01_LOCAL_VISUAL_IMPORT_PASS generatedUassets=!UASSET_COUNT!
echo P1C01_LOCAL_VISUAL_LAUNCH map=/Engine/Maps/Entry renderer=DX11 resolution=1280x720
echo NOTE: this is a local preview launcher, not PIE/device/visual/performance acceptance.

start "" "%EDITOR%" "%PROJECT%" /Engine/Maps/Entry -game -log -d3d11 -ResX=1280 -ResY=720 -Windowed -NoSplash
if errorlevel 1 (
  echo P1C01_LOCAL_VISUAL_BOOTSTRAP_FAIL reason=launch_failed
  exit /b 65
)

echo P1C01_LOCAL_VISUAL_BOOTSTRAP_PASS sourceFiles=!SOURCE_FILES! generatedUassets=!UASSET_COUNT!
exit /b 0
