@echo off
setlocal EnableExtensions EnableDelayedExpansion

for %%I in ("%~dp0..") do set "WORKSPACE=%%~fI"
set "GITHUB_WORKSPACE=%WORKSPACE%"
set "PROJECT=%WORKSPACE%\ShireJourney.uproject"
set "UE_ROOT=C:\Program Files\Epic Games\UE_4.27"
set "EDITOR=%UE_ROOT%\Engine\Binaries\Win64\UE4Editor.exe"
set "CAPTURE_ROOT=%WORKSPACE%\Saved\Automation\P1C01VisualCapture"
set "SCREENSHOT_ROOT=%WORKSPACE%\Saved\Screenshots\Windows"

if not exist "%PROJECT%" (
  echo P1C01_RENDER_CAPTURE_FAIL reason=project_missing path="%PROJECT%"
  exit /b 71
)
if not exist "%EDITOR%" (
  echo P1C01_RENDER_CAPTURE_FAIL reason=ue4_editor_missing path="%EDITOR%"
  exit /b 72
)

for /f "delims=" %%S in ('git -C "%WORKSPACE%" rev-parse --short^=12 HEAD 2^>nul') do set "SHORT_SHA=%%S"
if not defined SHORT_SHA set "SHORT_SHA=unknown"
set "RUN_DIR=%CAPTURE_ROOT%\%SHORT_SHA%"

if exist "%RUN_DIR%" rmdir /S /Q "%RUN_DIR%"
mkdir "%RUN_DIR%" >nul 2>nul
if not exist "%SCREENSHOT_ROOT%" mkdir "%SCREENSHOT_ROOT%" >nul 2>nul

echo P1C01_RENDER_CAPTURE_BEGIN sha=%SHORT_SHA% map=/Engine/Maps/Entry renderer=DX11 resolution=1280x720

call "%WORKSPACE%\Scripts\ci_import_production_assets.cmd"
set "IMPORT_EXIT=!ERRORLEVEL!"
if not "!IMPORT_EXIT!"=="0" (
  echo P1C01_RENDER_CAPTURE_FAIL reason=production_import exit=!IMPORT_EXIT!
  exit /b !IMPORT_EXIT!
)

call :Capture "01_BagEnd_Hill" -3160 -1760 440 -8 37 0
if errorlevel 1 exit /b !ERRORLEVEL!
call :Capture "02_Hobbiton_Common" -1540 -650 430 -7 32 0
if errorlevel 1 exit /b !ERRORLEVEL!
call :Capture "03_Party_Field" -880 520 430 -8 32 0
if errorlevel 1 exit /b !ERRORLEVEL!
call :Capture "04_Water_Mill_Bridge" -1830 260 390 -8 2 0
if errorlevel 1 exit /b !ERRORLEVEL!
call :Capture "05_Bywater_Facing_Edge" 720 -540 430 -7 14 0
if errorlevel 1 exit /b !ERRORLEVEL!
call :Capture "06_Bucklebury_Ferry" 21900 -1550 520 -9 18 0
if errorlevel 1 exit /b !ERRORLEVEL!

for /f %%C in ('powershell.exe -NoProfile -Command "(Get-ChildItem -LiteralPath '%RUN_DIR%' -File -Filter '*.png' -ErrorAction SilentlyContinue ^| Measure-Object).Count"') do set "PNG_COUNT=%%C"
if not "!PNG_COUNT!"=="6" (
  echo P1C01_RENDER_CAPTURE_FAIL reason=unexpected_capture_count expected=6 actual=!PNG_COUNT! dir="%RUN_DIR%"
  exit /b 79
)

echo P1C01_RENDER_CAPTURE_PASS sha=%SHORT_SHA% captures=!PNG_COUNT! artifact="%RUN_DIR%"
echo NOTE: automated rendered captures are evidence for review only; they are not PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED, PACING-ACCEPTED or PERFORMANCE-ACCEPTED.
exit /b 0

:Capture
set "SHOT_NAME=%~1"
set "X=%~2"
set "Y=%~3"
set "Z=%~4"
set "PITCH=%~5"
set "YAW=%~6"
set "ROLL=%~7"
set "BEFORE_FILE=%TEMP%\p1c01_before_%RANDOM%.txt"
set "LOG_FILE=%RUN_DIR%\%SHOT_NAME%.log"

powershell.exe -NoProfile -Command "Get-ChildItem -LiteralPath '%SCREENSHOT_ROOT%' -File -Filter '*.png' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName | Set-Content -LiteralPath '%BEFORE_FILE%'"

echo P1C01_RENDER_CAPTURE_SHOT_BEGIN name=%SHOT_NAME% x=%X% y=%Y% z=%Z% pitch=%PITCH% yaw=%YAW% roll=%ROLL%

start "" /B "%EDITOR%" "%PROJECT%" /Engine/Maps/Entry -game -log -abslog="%LOG_FILE%" -d3d11 -ResX=1280 -ResY=720 -Windowed -NoSplash -NoSound -ExecCmds="BugItGo %X% %Y% %Z% %PITCH% %YAW% %ROLL%,HighResShot 1"

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "$deadline=(Get-Date).AddSeconds(75); $before=@(); if(Test-Path -LiteralPath '%BEFORE_FILE%'){$before=Get-Content -LiteralPath '%BEFORE_FILE%'}; $shot=$null; do { Start-Sleep -Milliseconds 750; $shot=Get-ChildItem -LiteralPath '%SCREENSHOT_ROOT%' -File -Filter '*.png' -ErrorAction SilentlyContinue | Where-Object { $before -notcontains $_.FullName } | Sort-Object LastWriteTime -Descending | Select-Object -First 1 } while(-not $shot -and (Get-Date) -lt $deadline); if(-not $shot){exit 3}; Copy-Item -LiteralPath $shot.FullName -Destination '%RUN_DIR%\%SHOT_NAME%.png' -Force; exit 0"
set "WAIT_EXIT=!ERRORLEVEL!"

powershell.exe -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='UE4Editor.exe'\" | Where-Object { $_.CommandLine -like '*ShireJourney.uproject*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
if exist "%BEFORE_FILE%" del /F /Q "%BEFORE_FILE%" >nul 2>nul

if not "!WAIT_EXIT!"=="0" (
  echo P1C01_RENDER_CAPTURE_FAIL reason=screenshot_timeout name=%SHOT_NAME% log="%LOG_FILE%"
  if exist "%LOG_FILE%" powershell.exe -NoProfile -Command "Get-Content -LiteralPath '%LOG_FILE%' -Tail 120"
  exit /b 78
)

if not exist "%RUN_DIR%\%SHOT_NAME%.png" (
  echo P1C01_RENDER_CAPTURE_FAIL reason=missing_named_capture name=%SHOT_NAME%
  exit /b 77
)

echo P1C01_RENDER_CAPTURE_SHOT_PASS name=%SHOT_NAME% file="%RUN_DIR%\%SHOT_NAME%.png"
exit /b 0
