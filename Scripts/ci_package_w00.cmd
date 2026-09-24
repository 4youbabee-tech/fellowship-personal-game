@echo off
setlocal EnableExtensions
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%GITHUB_WORKSPACE%\Scripts\ci_package_w00.ps1" -TimeoutMinutes 45 -HeartbeatSeconds 30
exit /b %ERRORLEVEL%
