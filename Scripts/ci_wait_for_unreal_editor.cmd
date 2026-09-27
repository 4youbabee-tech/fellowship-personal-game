@echo off
setlocal EnableExtensions
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$deadline=(Get-Date).AddMinutes(20); $getEditors={ Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -like 'UE4Editor*' } }; $editors=@(& $getEditors); while($editors.Length -gt 0){$names=($editors | ForEach-Object { '{0}(PID {1})' -f $_.ProcessName,$_.Id }) -join ', '; if((Get-Date)-ge $deadline){Write-Error ('Unreal editor processes stayed open for 20 minutes: ' + $names + '. Close them so automated validation can rebuild safely.');exit 40}; Write-Host ('Unreal editor process(es) still hold the project session: ' + $names + '; waiting 10 seconds without terminating them.');Start-Sleep -Seconds 10;$editors=@(& $getEditors)};Write-Host 'All UE4Editor* processes are closed. Validation may continue.'"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" exit /b %RC%
exit /b 0
