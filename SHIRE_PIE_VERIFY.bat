@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Shire Journey - Current Head PIE Verification

cd /d "%~dp0"
set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

set "PROJECT=%ROOT%\ShireJourney.uproject"
set "UE_ROOT=C:\Program Files\Epic Games\UE_4.27"
set "EDITOR_EXE=%UE_ROOT%\Engine\Binaries\Win64\UE4Editor.exe"
set "SESSION_DIR=%ROOT%\Saved\PIEVerification"
set "SESSION_FILE=%SESSION_DIR%\CurrentHeadSession.txt"

echo ============================================================
echo SHIRE JOURNEY - CURRENT HEAD PIE VERIFICATION
echo ============================================================
echo.
echo This helper does NOT mark PIE as passed.
echo It only locks the session to the exact develop commit and
echo records the human verification checklist for that commit.
echo.

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
  echo Close Unreal first so this session can be tied to one exact commit.
  pause
  exit /b 12
)

set "GIT_EXE="
for /f "delims=" %%G in ('where git 2^>nul') do (
  if not defined GIT_EXE set "GIT_EXE=%%G"
)

if not defined GIT_EXE (
  echo ERROR: git.exe is required for exact-commit PIE verification.
  echo Use GitHub Desktop or install Git, then run this helper again.
  pause
  exit /b 13
)

echo [1/4] Synchronizing exact develop head...
"%GIT_EXE%" fetch origin
if errorlevel 1 goto :git_failed
"%GIT_EXE%" checkout develop
if errorlevel 1 goto :git_failed
"%GIT_EXE%" pull --ff-only origin develop
if errorlevel 1 goto :git_failed

for /f %%S in ('"%GIT_EXE%" rev-parse HEAD') do set "TESTED_SHA=%%S"
if not defined TESTED_SHA (
  echo ERROR: Could not resolve current develop commit.
  pause
  exit /b 14
)

echo.
echo Exact commit under human PIE test:
echo   %TESTED_SHA%
echo.

echo [2/4] Running the normal update/build/import/launch path...
call "%ROOT%\SHIRE_UPDATE_BUILD_LAUNCH.bat"
if errorlevel 1 (
  echo.
  echo ERROR: Update/build/import/launch failed. PIE evidence must remain NOT_RUN/BLOCKED.
  pause
  exit /b 20
)

if not exist "%SESSION_DIR%" mkdir "%SESSION_DIR%"

(
  echo SHIRE JOURNEY CURRENT-HEAD PIE VERIFICATION SESSION
  echo Tested commit: %TESTED_SHA%
  echo Branch: develop
  echo Target: UE4.27.2 / Windows / DX11 / 1280x720 / Low-Medium
  echo.
  echo IMPORTANT:
  echo - This file is a session anchor, not proof by itself.
  echo - Only direct human observations may update Data/PIEVerificationEvidence.json.
  echo - Test chapters in order. Repair blocking failures before advancing.
  echo.
  echo P1C01 SHIRE FIRST:
  echo [ ] PIE boots without crash
  echo [ ] Movement / camera / sprint / crouch
  echo [ ] Interact / HUD / quest progression
  echo [ ] NPC routines / awareness
  echo [ ] Ambient NPC-to-NPC conversation
  echo [ ] Named-NPC memory/context where applicable
  echo [ ] F5 quick save
  echo [ ] F9 quick load round-trip
  echo [ ] F8 Frodo - Gandalf/Isengard - Frodo round-trip
  echo [ ] Weather / atmosphere observed
  echo [ ] FPS / hitch / memory observations at 720p Low-Medium
  echo [ ] Screenshot or log artifact retained
  echo.
  echo Then repeat chapter smoke in order:
  echo P1C02 Bree
  echo P1C03 Weathertop/Ford
  echo P1C04 Rivendell
  echo P1C05 Road/Caradhras/West Gate
  echo P1C06 Moria
  echo P1C07 Lothlorien
  echo P1C08 Anduin/Amon Hen
) > "%SESSION_FILE%"

echo [3/4] Verification session anchor written:
echo   %SESSION_FILE%
echo.
echo [4/4] Unreal Editor is launching.
echo Start with P1C01. Do not mark anything PIE_TESTED unless you directly observed it.
echo.
exit /b 0

:git_failed
echo.
echo ERROR: Could not synchronize develop. No PIE evidence should be recorded.
pause
exit /b 30
