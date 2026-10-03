@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Shire Journey - Update Build Launch

rem Run from a temporary immutable copy so git pull cannot rewrite the batch file
rem that CMD is currently parsing. The project root is passed explicitly to the copy.
if not defined SHIRE_UPDATE_BOOTSTRAPPED (
  set "SHIRE_UPDATE_BOOTSTRAPPED=1"
  set "SHIRE_BOOTSTRAP_ROOT=%~dp0"
  set "SHIRE_BOOTSTRAP_FILE=%TEMP%\ShireJourney_UpdateBuildLaunch_!RANDOM!_!RANDOM!.bat"
  copy /Y "%~f0" "!SHIRE_BOOTSTRAP_FILE!" >NUL
  if errorlevel 1 (
    echo ERROR: LOCAL_BOOTSTRAP_COPY_FAILED
    pause
    exit /b 9
  )
  call "!SHIRE_BOOTSTRAP_FILE!" "!SHIRE_BOOTSTRAP_ROOT!"
  set "SHIRE_BOOTSTRAP_RC=!ERRORLEVEL!"
  del /Q "!SHIRE_BOOTSTRAP_FILE!" >NUL 2>NUL
  exit /b !SHIRE_BOOTSTRAP_RC!
)

set "ROOT=%~1"
if not defined ROOT set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"
cd /d "%ROOT%"

set "PROJECT=%ROOT%\ShireJourney.uproject"
set "UE_ROOT=C:\Program Files\Epic Games\UE_4.27"
set "BUILD_BAT=%UE_ROOT%\Engine\Build\BatchFiles\Build.bat"
set "EDITOR_EXE=%UE_ROOT%\Engine\Binaries\Win64\UE4Editor.exe"
set "EDITOR_CMD_EXE=%UE_ROOT%\Engine\Binaries\Win64\UE4Editor-Cmd.exe"
set "BUILD_LOG=%ROOT%\Saved\Logs\LastOneClickBuildFailure.txt"
set "IMPORT_LOG=%ROOT%\Saved\Logs\LastProductionAssetImport.log"

echo ============================================================
echo SHIRE JOURNEY - DEVELOP UPDATE ^> BUILD ^> IMPORT ^> LAUNCH
echo ============================================================
echo.

echo(%ROOT%| findstr /I /C:"\actions-runner\" >NUL
if not errorlevel 1 (
  echo ERROR: RUNNER_ROOT_BLOCKED
  echo Interactive Unreal work must use the developer clone under Documents.
  echo The GitHub Actions runner root is reserved for CI only.
  pause
  exit /b 13
)

if not exist "%PROJECT%" (
  echo ERROR: ShireJourney.uproject was not found next to this script.
  pause
  exit /b 10
)

if not exist "%BUILD_BAT%" (
  echo ERROR: Unreal Engine 4.27 was not found at:
  echo %UE_ROOT%
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
for /f "delims=" %%G in ('where git 2^>nul') do if not defined GIT_EXE set "GIT_EXE=%%G"
if not defined GIT_EXE (
  for /f "delims=" %%D in ('dir /b /ad /o-d "%LOCALAPPDATA%\GitHubDesktop\app-*" 2^>nul') do (
    if not defined GIT_EXE if exist "%LOCALAPPDATA%\GitHubDesktop\%%D\resources\app\git\cmd\git.exe" (
      set "GIT_EXE=%LOCALAPPDATA%\GitHubDesktop\%%D\resources\app\git\cmd\git.exe"
    )
  )
)
if not defined GIT_EXE (
  echo ERROR: git.exe was not found.
  pause
  exit /b 14
)

set "ACTIVE_BRANCH="
for /f "delims=" %%B in ('"%GIT_EXE%" rev-parse --abbrev-ref HEAD 2^>nul') do if not defined ACTIVE_BRANCH set "ACTIVE_BRANCH=%%B"
if not defined ACTIVE_BRANCH goto :branch_failed
if /I not "!ACTIVE_BRANCH!"=="develop" goto :branch_failed

set "DIRTY_TRACKED="
for /f "delims=" %%S in ('"%GIT_EXE%" status --porcelain --untracked-files=no') do set "DIRTY_TRACKED=1"
if defined DIRTY_TRACKED goto :dirty_failed

echo [1/4] Updating canonical develop from GitHub...
"%GIT_EXE%" fetch --no-tags origin develop
if errorlevel 1 goto :git_failed
"%GIT_EXE%" pull --ff-only origin develop
if errorlevel 1 goto :git_failed
for /f "delims=" %%S in ('"%GIT_EXE%" rev-parse HEAD') do if not defined ACTIVE_SHA set "ACTIVE_SHA=%%S"
echo       develop HEAD: !ACTIVE_SHA!

echo.
echo [2/4] Building ShireJourneyEditor with UE4.27.2...
call "%BUILD_BAT%" ShireJourneyEditor Win64 Development "%PROJECT%" -WaitMutex -NoHotReloadFromIDE
if errorlevel 1 goto :build_failed

echo.
echo [3/4] Importing production assets...
if not exist "%ROOT%\Saved\Logs" mkdir "%ROOT%\Saved\Logs"
if exist "%IMPORT_LOG%" del /Q "%IMPORT_LOG%" >NUL 2>NUL
"%EDITOR_CMD_EXE%" "%PROJECT%" -run=ShireProductionImport -unattended -nop4 -nosplash -NoSound -abslog="%IMPORT_LOG%"
if errorlevel 1 goto :asset_import_failed

echo.
echo [4/4] Update, build and import succeeded. Launching Unreal Engine...
start "" "%EDITOR_EXE%" "%PROJECT%"
exit /b 0

:branch_failed
echo.
echo ERROR: CANONICAL_BRANCH_REQUIRED
echo This project now has one interactive development branch: develop.
echo Current branch: !ACTIVE_BRANCH!
echo Switch this Documents clone to develop with GitHub Desktop, then run again.
echo The helper will never switch branches silently.
pause
exit /b 21

:dirty_failed
echo.
echo ERROR: TRACKED_LOCAL_CHANGES_PRESENT
echo Commit, stash or revert tracked local changes before updating develop.
pause
exit /b 22

:git_failed
echo.
echo ERROR: Git update failed. No build was attempted.
echo The helper never changes branches and never falls back to another ref.
pause
exit /b 20

:build_failed
echo.
echo ERROR: Build failed.
if not exist "%ROOT%\Saved\Logs" mkdir "%ROOT%\Saved\Logs"
if exist "%LOCALAPPDATA%\UnrealBuildTool\Log.txt" (
  copy /Y "%LOCALAPPDATA%\UnrealBuildTool\Log.txt" "%BUILD_LOG%" >NUL
  echo Build log copied to:
  echo %BUILD_LOG%
)
pause
exit /b 30

:asset_import_failed
echo.
echo ERROR: Production asset import failed.
if exist "%IMPORT_LOG%" (
  echo Import log:
  echo %IMPORT_LOG%
  findstr /I /C:"ShireProductionImport FAILED" /C:"Error:" /C:"Warning:" "%IMPORT_LOG%"
)
pause
exit /b 31
