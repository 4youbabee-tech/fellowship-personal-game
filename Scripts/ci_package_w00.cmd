@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "PROJECT=%GITHUB_WORKSPACE%\ShireJourney.uproject"
set "UAT=C:\Program Files\Epic Games\UE_4.27\Engine\Build\BatchFiles\RunUAT.bat"
set "ARCHIVE=%GITHUB_WORKSPACE%\Saved\W00Package"
set "LOGDIR=%GITHUB_WORKSPACE%\Saved\Logs"
set "LOG=%LOGDIR%\CI-W00-Package.log"

if not exist "%PROJECT%" exit /b 90
if not exist "%UAT%" exit /b 91
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
if exist "%ARCHIVE%" rmdir /S /Q "%ARCHIVE%"
mkdir "%ARCHIVE%"

echo W00_PACKAGE_BEGIN sha=%TARGET_SHA%
call "%UAT%" BuildCookRun -project="%PROJECT%" -noP4 -platform=Win64 -clientconfig=Development -build -cook -map=/Engine/Maps/Templates/Template_Default -stage -pak -archive -archivedirectory="%ARCHIVE%" -utf8output -unattended > "%LOG%" 2>&1
set "EXITCODE=!ERRORLEVEL!"
type "%LOG%"
if not "!EXITCODE!"=="0" exit /b !EXITCODE!

if not exist "%ARCHIVE%\WindowsNoEditor\ShireJourney.exe" (
  echo ERROR: Packaged executable missing: %ARCHIVE%\WindowsNoEditor\ShireJourney.exe
  exit /b 92
)

echo W00_PACKAGE_PASS exe=%ARCHIVE%\WindowsNoEditor\ShireJourney.exe
exit /b 0
