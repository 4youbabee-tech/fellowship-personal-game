@echo off
setlocal EnableExtensions
set "PROJECT=%GITHUB_WORKSPACE%\ShireJourney.uproject"
set "EDITORCMD=C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Cmd.exe"
set "LOGDIR=%GITHUB_WORKSPACE%\Saved\Logs"
set "IMPORTLOG=%LOGDIR%\CI-ProductionAssetImport.log"
if not exist "%EDITORCMD%" exit /b 50
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
"%EDITORCMD%" "%PROJECT%" -run=ShireProductionImport -unattended -nop4 -nosplash -NoSound -abslog="%IMPORTLOG%"
set "IMPORT_EXIT=%ERRORLEVEL%"
if exist "%IMPORTLOG%" findstr /I /C:"ShireProductionImport:" /C:"ShireProductionImport FAILED" /C:"Error:" /C:"Warning:" "%IMPORTLOG%"
if not "%IMPORT_EXIT%"=="0" exit /b %IMPORT_EXIT%
findstr /C:"ShireProductionImport:" "%IMPORTLOG%" | findstr /C:"0 failures" >nul
if errorlevel 1 exit /b 51
echo UE4.27.2 production asset import succeeded.
exit /b 0
