@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Shire Journey - Update Build Launch

cd /d "%~dp0"
set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

set "PROJECT=%ROOT%\ShireJourney.uproject"
set "UE_ROOT=C:\Program Files\Epic Games\UE_4.27"
set "BUILD_BAT=%UE_ROOT%\Engine\Build\BatchFiles\Build.bat"
set "EDITOR_EXE=%UE_ROOT%\Engine\Binaries\Win64\UE4Editor.exe"
set "EDITOR_CMD_EXE=%UE_ROOT%\Engine\Binaries\Win64\UE4Editor-Cmd.exe"
set "BUILD_LOG=%ROOT%\Saved\Logs\LastOneClickBuildFailure.txt"
set "IMPORT_LOG=%ROOT%\Saved\Logs\LastProductionAssetImport.log"

echo ============================================================
echo SHIRE JOURNEY - UPDATE ^> BUILD ^> LAUNCH
echo ============================================================
echo.

if not exist "%PROJECT%" (
  echo ERROR: ShireJourney.uproject was not found next to this script.
  pause
  exit /b 10
)

if not exist "%BUILD_BAT%" (
  echo ERROR: Unreal Engine 4.27 was not found at:
  echo %UE_ROOT%
  echo.
  echo Install UE 4.27.2 in the default Epic Games location, then run again.
  pause
  exit /b 11
)

tasklist /FI "IMAGENAME eq UE4Editor.exe" 2>NUL | find /I "UE4Editor.exe" >NUL
if not errorlevel 1 (
  echo ERROR: Unreal Editor is already open.
  echo Close Unreal first so the game DLL can be rebuilt safely.
  pause
  exit /b 12
)

set "GIT_EXE="
for /f "delims=" %%G in ('where git 2^>nul') do (
  if not defined GIT_EXE set "GIT_EXE=%%G"
)

if not defined GIT_EXE (
  for /f "delims=" %%D in ('dir /b /ad /o-d "%LOCALAPPDATA%\GitHubDesktop\app-*" 2^>nul') do (
    if not defined GIT_EXE if exist "%LOCALAPPDATA%\GitHubDesktop\%%D\resources\app\git\cmd\git.exe" (
      set "GIT_EXE=%LOCALAPPDATA%\GitHubDesktop\%%D\resources\app\git\cmd\git.exe"
    )
  )
)

if defined GIT_EXE (
  echo [1/5] Updating develop from GitHub...
  "%GIT_EXE%" fetch origin
  if errorlevel 1 goto :git_failed
  "%GIT_EXE%" checkout develop
  if errorlevel 1 goto :git_failed
  "%GIT_EXE%" pull --ff-only origin develop
  if errorlevel 1 goto :git_failed
) else (
  echo [1/5] Git executable not found. Skipping automatic pull.
  echo       Update with GitHub Desktop before the next run.
)

echo.
echo [2/5] Running local Pre-Unreal/static preflight...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ROOT%\Scripts\run_local_preflight.ps1"
if errorlevel 1 goto :preflight_failed

echo.
echo [3/5] Building ShireJourneyEditor with UE4.27...
call "%BUILD_BAT%" ShireJourneyEditor Win64 Development "%PROJECT%" -WaitMutex -NoHotReloadFromIDE
if errorlevel 1 goto :preflight_failed
echo.
echo ERROR: Local Pre-Unreal/static preflight failed. No Unreal build was attempted.
echo Fix the reported static/governance/test failure, then run this file again.
pause
exit /b 25

:build_failed

echo.
echo [4/5] Importing production 3D assets into Unreal...
if not exist "%ROOT%\Saved\Logs" mkdir "%ROOT%\Saved\Logs"
if exist "%IMPORT_LOG%" del /Q "%IMPORT_LOG%" >NUL 2>NUL
"%EDITOR_CMD_EXE%" "%PROJECT%" -run=ShireProductionImport -unattended -nop4 -nosplash -NoSound -abslog="%IMPORT_LOG%"
if errorlevel 1 goto :asset_import_failed

echo.
echo [5/5] Build and asset import succeeded. Launching Unreal Engine...
start "" "%EDITOR_EXE%" "%PROJECT%"
exit /b 0

:git_failed
echo.
echo ERROR: Git update failed. No build was attempted.
echo Open GitHub Desktop, resolve any local changes, then run this file again.
pause
exit /b 20

:build_failed
echo.
echo ERROR: Build failed.
if not exist "%ROOT%\Saved\Logs" mkdir "%ROOT%\Saved\Logs"
if exist "%LOCALAPPDATA%\UnrealBuildTool\Log.txt" (
  copy /Y "%LOCALAPPDATA%\UnrealBuildTool\Log.txt" "%BUILD_LOG%" >NUL
  echo A copy of the build log was saved here:
  echo %BUILD_LOG%
)
echo.
echo Send LastOneClickBuildFailure.txt to ChatGPT and the source can be fixed.
pause
exit /b 30

:asset_import_failed
echo.
echo ERROR: Production asset import failed.
if exist "%IMPORT_LOG%" (
  echo Detailed import log was saved here:
  echo %IMPORT_LOG%
  echo.
  echo Last import errors:
  findstr /I /C:"ShireProductionImport FAILED" /C:"Error:" /C:"Warning:" "%IMPORT_LOG%"
)
echo.
echo Send LastProductionAssetImport.log to ChatGPT so the exact failing asset can be fixed.
pause
exit /b 31
