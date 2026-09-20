@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "PROJECT=%GITHUB_WORKSPACE%\ShireJourney.uproject"
set "BUILDBAT=C:\Program Files\Epic Games\UE_4.27\Engine\Build\BatchFiles\Build.bat"
set "LOGDIR=%GITHUB_WORKSPACE%\Saved\Logs"
set "BUILDLOG=%LOGDIR%\CI-UnrealBuild.log"
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
rem Re-establish the job-local compiler scratch directory at its point of use.
rem A missing inherited TEMP prevents UnrealBuildTool's C# compiler from starting.
if not defined TEMP (
  echo ERROR: Compiler TEMP is not configured.
  exit /b 77
)
if not exist "%TEMP%\." mkdir "%TEMP%"
if not exist "%TEMP%\." (
  echo ERROR: Compiler TEMP could not be created.
  exit /b 77
)
echo Building exact commit: %TARGET_SHA%
call "%BUILDBAT%" ShireJourneyEditor Win64 Development "%PROJECT%" -WaitMutex -NoHotReloadFromIDE -MaxParallelActions=1 > "%BUILDLOG%" 2>&1
set "BUILD_EXIT=!ERRORLEVEL!"
if not "!BUILD_EXIT!"=="0" (
  findstr /I /C:"error C3859" /C:"fatal error C1076" /C:"error D8050" /C:"Command line error D8050" "%BUILDLOG%" >nul
  if not errorlevel 1 (
    echo.>>"%BUILDLOG%"
    echo CI_BUILD_RETRY: MSVC compiler resource/process pressure detected; clearing project intermediates and retrying once.>>"%BUILDLOG%"
    powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$paths=@((Join-Path $env:GITHUB_WORKSPACE 'Intermediate\Build\Win64'),(Join-Path $env:GITHUB_WORKSPACE 'Binaries\Win64'));foreach($p in $paths){if(Test-Path -LiteralPath $p){Remove-Item -LiteralPath $p -Recurse -Force}};Start-Sleep -Seconds 5"
    call "%BUILDBAT%" ShireJourneyEditor Win64 Development "%PROJECT%" -WaitMutex -NoHotReloadFromIDE -MaxParallelActions=1 >> "%BUILDLOG%" 2>&1
    set "BUILD_EXIT=!ERRORLEVEL!"
  )
)
type "%BUILDLOG%"
if not "!BUILD_EXIT!"=="0" exit /b !BUILD_EXIT!
echo UE4.27.2 build succeeded.
exit /b 0
