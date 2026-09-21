@echo off
setlocal EnableExtensions
set "PROJECT=%GITHUB_WORKSPACE%\ShireJourney.uproject"
set "BUILDBAT=C:\Program Files\Epic Games\UE_4.27\Engine\Build\BatchFiles\Build.bat"
set "BUILDVERSION=C:\Program Files\Epic Games\UE_4.27\Engine\Build\Build.version"
set "ENGINEPREFLIGHT=%GITHUB_WORKSPACE%\Scripts\verify_ue_engine_content.ps1"
if not exist "%PROJECT%" exit /b 30
if not exist "%BUILDBAT%" exit /b 31
if not exist "%BUILDVERSION%" exit /b 32
if not exist "%ENGINEPREFLIGHT%" exit /b 34
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$v=Get-Content '%BUILDVERSION%' -Raw|ConvertFrom-Json; Write-Host ('Detected Unreal Engine {0}.{1}.{2}' -f $v.MajorVersion,$v.MinorVersion,$v.PatchVersion); if($v.MajorVersion-ne 4-or $v.MinorVersion-ne 27-or $v.PatchVersion-ne 2){exit 33}"
if errorlevel 1 exit /b 33
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ENGINEPREFLIGHT%"
if errorlevel 1 exit /b %ERRORLEVEL%
exit /b 0
