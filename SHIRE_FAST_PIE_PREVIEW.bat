@echo off
setlocal EnableExtensions
title Shire Journey - Fast Local PIE Preview (no package/no sync)
set "ROOT=%~dp0"
set "PROJECT=%ROOT%ShireJourney.uproject"
set "UE_EDITOR=C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor.exe"
set "EDITOR_DLL=%ROOT%Binaries\Win64\UE4Editor-ShireJourney.dll"
set "LOGDIR=%ROOT%Saved\PIEFastPreview"
echo SHIRE_PIE_FAST_PREVIEW_START: local files only, NO git pull, NO cook/package, NO build
if not exist "%PROJECT%" (
  echo ERROR: Local ShireJourney.uproject missing in "%ROOT%"
  exit /b 10
)
if not exist "%UE_EDITOR%" (
  echo ERROR: UE4.27.2 editor not found at "%UE_EDITOR%"
  echo If installed elsewhere, edit UE_EDITOR in this helper.
  exit /b 11
)
if not exist "%EDITOR_DLL%" (
  echo ERROR: Compiled ShireJourney editor module missing: "%EDITOR_DLL%"
  echo Run the normal update/build once, then use this fast PIE preview for unchanged C++ builds.
  exit /b 12
)
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
set "GIT_SHA=UNKNOWN_LOCAL_NOT_VERIFIED"
where git >nul 2>nul
if not errorlevel 1 (
  for /f %%H in ('git -C "%ROOT%" rev-parse HEAD 2^>nul') do set "GIT_SHA=%%H"
)
(
  echo P1C01 LOCAL FAST PIE PREVIEW
  echo Source HEAD: %GIT_SHA%
  echo Source folder: %ROOT%
  echo Engine: UE4.27.2 / DX11 / 1280x720
  echo NOTICE: session metadata only, not PIE-TESTED or 30 FPS evidence.
  echo Click Play in the Unreal Editor to begin the chapter-specific PIE test.
  echo Required observations: screenshot/log, player traversal, materials, save/load, FPS/frame-times.
) > "%LOGDIR%\LAST_SESSION.txt"
echo.
echo Fast Editor preview: click Play after project opens.
echo WARNING: This does NOT update GitHub branch or compile changed C++/UHT code.
echo WARNING: This does NOT prove that current local assets match a GitHub PR.
start "" "%UE_EDITOR%" "%PROJECT%" -d3d11 -ResX=1280 -ResY=720 -log
if errorlevel 1 exit /b 13
echo SHIRE_PIE_FAST_PREVIEW_LAUNCH_REQUESTED head=%GIT_SHA%
exit /b 0
