@echo off
setlocal EnableExtensions
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$deadline=(Get-Date).AddMinutes(20); while(Get-Process -Name UE4Editor -ErrorAction SilentlyContinue){if((Get-Date)-ge $deadline){Write-Error 'UE4Editor.exe stayed open for 20 minutes. Close the editor so automated validation can rebuild safely.';exit 40};Write-Host 'UE4Editor.exe is open; waiting 10 seconds instead of terminating it.';Start-Sleep -Seconds 10};Write-Host 'Unreal Editor is closed. Validation may continue.'"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" exit /b %RC%
exit /b 0
