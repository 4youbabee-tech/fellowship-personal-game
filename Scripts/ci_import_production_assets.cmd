@echo off
setlocal EnableExtensions
set "PROJECT=%GITHUB_WORKSPACE%\ShireJourney.uproject"
set "EDITORCMD=C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Cmd.exe"
set "LOGDIR=%GITHUB_WORKSPACE%\Saved\Logs"
set "IMPORTLOG=%LOGDIR%\CI-ProductionAssetImport.log"
set "PRODUCTION_DIR=%GITHUB_WORKSPACE%\Content\Production"
set "BACKUP_DIR=%GITHUB_WORKSPACE%\Saved\CI-Production-Backup-%GITHUB_RUN_ID%-%GITHUB_RUN_ATTEMPT%-%RANDOM%"
set "FAILED_DIR=%GITHUB_WORKSPACE%\Saved\CI-Production-Failed-%GITHUB_RUN_ID%-%GITHUB_RUN_ATTEMPT%-%RANDOM%"
set "HAD_OUTPUT=0"
if not exist "%EDITORCMD%" exit /b 50
if not exist "%PROJECT%" exit /b 50
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
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
  rem Move the old tree aside so UE4 never has to delete/overwrite stale .uasset packages.
  move "%PRODUCTION_DIR%" "%BACKUP_DIR%" >nul
  if errorlevel 1 (
    echo ERROR: could not quarantine generated Content/Production before import. Failing fast; check open handles or runner permissions. Previous files remain in place.
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
