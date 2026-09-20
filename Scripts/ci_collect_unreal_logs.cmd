@echo off
setlocal EnableExtensions
set "LOGDIR=%GITHUB_WORKSPACE%\Saved\Logs"
if not exist "%LOGDIR%" mkdir "%LOGDIR%"
if exist "%LOCALAPPDATA%\UnrealBuildTool\Log.txt" copy /Y "%LOCALAPPDATA%\UnrealBuildTool\Log.txt" "%LOGDIR%\CI-UnrealBuildTool.log" >nul
echo UE4.27.2 build job status: %~1>>"%GITHUB_STEP_SUMMARY%"
echo Commit: %TARGET_SHA%>>"%GITHUB_STEP_SUMMARY%"
exit /b 0
