@echo off
setlocal EnableExtensions
set "PROJECT=%GITHUB_WORKSPACE%\ShireJourney.uproject"
set "EDITORCMD=C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Cmd.exe"
set "LOGDIR=%GITHUB_WORKSPACE%\Saved\Logs"
set "IMPORTLOG=%LOGDIR%\CI-ProductionAssetImport.log"
set "PRODUCTION_DIR=%GITHUB_WORKSPACE%\Content\Production"
set "BACKUP_DIR=%RUNNER_TEMP%\CI-Production-Backup-%GITHUB_RUN_ID%-%GITHUB_RUN_ATTEMPT%-%RANDOM%"
set "FAILED_DIR=%RUNNER_TEMP%\CI-Production-Failed-%GITHUB_RUN_ID%-%GITHUB_RUN_ATTEMPT%-%RANDOM%"
set "HAD_OUTPUT=0"
for /f "delims=" %%I in ('whoami') do set "RUNNER_IDENTITY=%%I"
if not exist "%EDITORCMD%" exit /b 50
if not exist "%PROJECT%" exit /b 50
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
if not defined RUNNER_TEMP (
  echo ERROR: RUNNER_TEMP is unavailable; cannot place generated-content rollback on the runner volume.
  exit /b 50
)
if not exist "%RUNNER_TEMP%" (
  echo ERROR: runner temp directory does not exist: "%RUNNER_TEMP%"
  exit /b 50
)
if exist "%BACKUP_DIR%" (
  echo ERROR: unique generated-content backup path already exists: "%BACKUP_DIR%"
  exit /b 52
)
if exist "%FAILED_DIR%" (
  echo ERROR: unique failed-import quarantine path already exists: "%FAILED_DIR%"
  exit /b 53
)
if exist "%PRODUCTION_DIR%" (
  rem Content/Production is ignored generated output rebuilt from SourceAssets/Production.
  rem Repair Modify only on that generated tree so the runner can quarantine it for UE4 import.
  if not defined RUNNER_IDENTITY (
    echo ERROR: could not resolve runner identity before generated-content quarantine.
    exit /b 55
  )
  echo Generated-content quarantine identity: %RUNNER_IDENTITY%
  icacls "%PRODUCTION_DIR%" /grant "%RUNNER_IDENTITY%:(OI)(CI)M" /T /C
  if errorlevel 1 (
    echo ERROR: could not grant Modify to the runner on generated Content/Production. ACL follows.
    icacls "%PRODUCTION_DIR%"
    exit /b 56
  )
  for %%I in ("%PRODUCTION_DIR%") do set "PRODUCTION_DRIVE=%%~dI"
  for %%I in ("%BACKUP_DIR%") do set "BACKUP_DRIVE=%%~dI"
  if /I not "%PRODUCTION_DRIVE%"=="%BACKUP_DRIVE%" (
    echo ERROR: generated-content quarantine must remain on one volume. source=%PRODUCTION_DRIVE% destination=%BACKUP_DRIVE%
    exit /b 57
  )
  move "%PRODUCTION_DIR%" "%BACKUP_DIR%"
  if errorlevel 1 (
    echo ERROR: could not quarantine generated Content/Production before import. Runner identity: %RUNNER_IDENTITY%. Source and destination ACLs follow; previous files remain in place.
    icacls "%PRODUCTION_DIR%"
    icacls "%GITHUB_WORKSPACE%\Content"
    icacls "%RUNNER_TEMP%"
    exit /b 54
  )
  set "HAD_OUTPUT=1"
)
"%EDITORCMD%" "%PROJECT%" -run=ShireProductionImport -unattended -nop4 -nosplash -NoSound -abslog="%IMPORTLOG%"
set "IMPORT_EXIT=%ERRORLEVEL%"
if exist "%IMPORTLOG%" findstr /I /C:"ShireProductionImport:" /C:"ShireProductionImport FAILED" /C:"Error:" /C:"Warning:" "%IMPORTLOG%"
if not "%IMPORT_EXIT%"=="0" goto :restore_previous
findstr /C:"ShireProductionImport:" "%IMPORTLOG%" | findstr /C:"0 failures" >nul
if errorlevel 1 (
  set "IMPORT_EXIT=51"
  goto :restore_previous
)
if "%HAD_OUTPUT%"=="1" (
  rmdir /S /Q "%BACKUP_DIR%"
  if exist "%BACKUP_DIR%" echo WARNING: validated import succeeded; prior generated backup remains at "%BACKUP_DIR%".
)
echo UE4.27.2 production asset import succeeded.
exit /b 0

:restore_previous
if "%HAD_OUTPUT%"=="1" (
  if exist "%PRODUCTION_DIR%" (
    move "%PRODUCTION_DIR%" "%FAILED_DIR%" >nul
    if errorlevel 1 echo WARNING: failed partial import could not be moved; preserved source backup remains at "%BACKUP_DIR%".
  )
  if not exist "%PRODUCTION_DIR%" (
    move "%BACKUP_DIR%" "%PRODUCTION_DIR%" >nul
    if errorlevel 1 echo ERROR: failed import and automatic restoration; previous generated assets remain at "%BACKUP_DIR%".
  )
)
exit /b %IMPORT_EXIT%
