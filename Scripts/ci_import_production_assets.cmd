@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "PROJECT=%GITHUB_WORKSPACE%\ShireJourney.uproject"
set "EDITORCMD=C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Cmd.exe"
set "LOGDIR=%GITHUB_WORKSPACE%\Saved\Logs"
set "IMPORTLOG=%LOGDIR%\CI-ProductionAssetImport.log"
set "PREFLIGHT=%GITHUB_WORKSPACE%\Scripts\preflight_production_asset_import.ps1"
if not exist "%EDITORCMD%" exit /b 50
if not exist "%PREFLIGHT%" exit /b 52
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PREFLIGHT%" -Workspace "%GITHUB_WORKSPACE%"
if errorlevel 1 exit /b 53

set ATTEMPT=1
:run_import
if exist "%IMPORTLOG%" del /F /Q "%IMPORTLOG%" >nul 2>nul
echo PRODUCTION_IMPORT_ATTEMPT attempt=!ATTEMPT!/2
"%EDITORCMD%" "%PROJECT%" -run=ShireProductionImport -unattended -nop4 -nosplash -NoSound -abslog="%IMPORTLOG%"
set "IMPORT_EXIT=!ERRORLEVEL!"
if exist "%IMPORTLOG%" findstr /I /C:"ShireProductionImport:" /C:"ShireProductionImport FAILED" /C:"Error:" /C:"Warning:" "%IMPORTLOG%"

if "!IMPORT_EXIT!"=="0" goto verify_success
if !ATTEMPT! GEQ 2 exit /b !IMPORT_EXIT!

set "SAVE_RETRYABLE=0"
if exist "%IMPORTLOG%" (
  findstr /I /C:"Error deleting file" /C:"Error saving" "%IMPORTLOG%" >nul
  if not errorlevel 1 set "SAVE_RETRYABLE=1"
)
if not "!SAVE_RETRYABLE!"=="1" exit /b !IMPORT_EXIT!

echo PRODUCTION_IMPORT_RECOVERY_BEGIN reason=save-delete-failure
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PREFLIGHT%" -Workspace "%GITHUB_WORKSPACE%"
if errorlevel 1 exit /b 54
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Start-Sleep -Seconds 2"
set ATTEMPT=2
goto run_import

:verify_success
findstr /C:"ShireProductionImport:" "%IMPORTLOG%" | findstr /C:"0 failures" >nul
if errorlevel 1 exit /b 51
echo UE4.27.2 production asset import succeeded.
exit /b 0
