@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Shire Journey - Develop PIE Verification

cd /d "%~dp0"
set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

set "PROJECT=%ROOT%\ShireJourney.uproject"
set "UE_ROOT=C:\Program Files\Epic Games\UE_4.27"
set "EDITOR_EXE=%UE_ROOT%\Engine\Binaries\Win64\UE4Editor.exe"
set "SESSION_DIR=%ROOT%\Saved\PIEVerification"
set "SESSION_FILE=%SESSION_DIR%\CurrentHeadSession.txt"

echo ============================================================
echo SHIRE JOURNEY - DEVELOP PIE VERIFICATION
echo ============================================================
echo.
echo Canonical interactive branch: develop
echo This helper never changes branches silently.
echo.

echo(%ROOT%| findstr /I /C:"\actions-runner\_work\" >NUL
if not errorlevel 1 (
  echo ERROR: RUNNER_WORKSPACE_BLOCKED
  echo PIE must run from the separate developer clone under Documents.
  pause
  exit /b 13
)

if not exist "%PROJECT%" (
  echo ERROR: ShireJourney.uproject was not found next to this script.
  pause
  exit /b 10
)

if not exist "%EDITOR_EXE%" (
  echo ERROR: UE4Editor.exe was not found at:
  echo %EDITOR_EXE%
  pause
  exit /b 11
)

tasklist /FI "IMAGENAME eq UE4Editor.exe" 2>NUL | find /I "UE4Editor.exe" >NUL
if not errorlevel 1 (
  echo ERROR: Unreal Editor is already open.
  echo Close Unreal first so the exact commit can be built and recorded.
  pause
  exit /b 12
)

set "GIT_EXE="
for /f "delims=" %%G in ('where git 2^>nul') do if not defined GIT_EXE set "GIT_EXE=%%G"
if not defined GIT_EXE (
  echo ERROR: git.exe is required.
  pause
  exit /b 14
)

set "TESTED_BRANCH="
for /f "delims=" %%B in ('"%GIT_EXE%" rev-parse --abbrev-ref HEAD 2^>nul') do if not defined TESTED_BRANCH set "TESTED_BRANCH=%%B"
if /I not "!TESTED_BRANCH!"=="develop" (
  echo ERROR: CANONICAL_BRANCH_REQUIRED
  echo Current branch: !TESTED_BRANCH!
  echo Switch the Documents clone to develop first.
  pause
  exit /b 15
)

echo [1/4] Canonical branch confirmed: develop
echo [2/4] Running update/build/import/launch...
call "%ROOT%\SHIRE_UPDATE_BUILD_LAUNCH.bat"
if errorlevel 1 (
  echo ERROR: Update/build/import/launch failed. No PIE proof may be recorded.
  pause
  exit /b 20
)

set "TESTED_SHA="
for /f %%S in ('"%GIT_EXE%" rev-parse HEAD') do set "TESTED_SHA=%%S"
if not defined TESTED_SHA (
  echo ERROR: Could not resolve current develop commit.
  pause
  exit /b 16
)

if not exist "%SESSION_DIR%" mkdir "%SESSION_DIR%"
(
  echo SHIRE JOURNEY DEVELOP PIE VERIFICATION SESSION
  echo Tested commit: !TESTED_SHA!
  echo Branch: develop
  echo Target: UE4.27.2 / Windows / DX11 / 1280x720 / Low-Medium
  echo.
  echo This file anchors the exact session only. It is not proof by itself.
  echo Human observations must be recorded separately.
  echo.
  echo P1C01:
  echo [ ] PIE boots without crash
  echo [ ] ShireStartupGrounding PASS / player does not fall
  echo [ ] Movement / camera / sprint / crouch
  echo [ ] Interact / HUD / quest progression
  echo [ ] NPC routines / awareness
  echo [ ] F5 quick save / F9 quick load
  echo [ ] F8 route round-trip
  echo [ ] FPS / hitch observation at 720p Low-Medium
) > "%SESSION_FILE%"

echo [3/4] Verification session anchor written:
echo   %SESSION_FILE%
echo [4/4] Unreal is launching on develop commit:
echo   !TESTED_SHA!
exit /b 0
