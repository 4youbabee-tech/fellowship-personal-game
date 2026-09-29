@echo off
setlocal EnableExtensions
set "WAITER=%GITHUB_WORKSPACE%\Scripts\wait_for_unreal_processes.ps1"
if not exist "%WAITER%" exit /b 41
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%WAITER%" -Workspace "%GITHUB_WORKSPACE%" -TimeoutMinutes 20 -StaleCommandletMinutes 20
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" exit /b %RC%
exit /b 0
