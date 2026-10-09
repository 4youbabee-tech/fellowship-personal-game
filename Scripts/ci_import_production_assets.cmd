@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "PROJECT=%GITHUB_WORKSPACE%\ShireJourney.uproject"
set "EDITORCMD=C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Cmd.exe"
set "LOGDIR=%GITHUB_WORKSPACE%\Saved\Logs"
set "IMPORTLOG=%LOGDIR%\CI-ProductionAssetImport.log"
set "PREFLIGHT=%GITHUB_WORKSPACE%\Scripts\preflight_production_asset_import.ps1"
if not exist "%EDITORCMD%" exit /b 50
if not exist "%PREFLIGHT%" exit /b 52
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PREFLIGHT%" -Workspace "%GITHUB_WORKSPACE%"
if errorlevel 1 exit /b 53

set ATTEMPT=1
:run_import
if exist "%IMPORTLOG%" del /F /Q "%IMPORTLOG%" >nul 2>nul
echo PRODUCTION_IMPORT_ATTEMPT attempt=!ATTEMPT!/2
"%EDITORCMD%" "%PROJECT%" -run=ShireProductionImport %* -unattended -nop4 -nosplash -NoSound -abslog="%IMPORTLOG%"
set "IMPORT_EXIT=!ERRORLEVEL!"
if exist "%IMPORTLOG%" findstr /I /C:"ShireProductionImport:" /C:"ShireProductionImport FAILED" /C:"Error:" /C:"Warning:" "%IMPORTLOG%"

if "!IMPORT_EXIT!"=="0" goto verify_success
if !ATTEMPT! GEQ 2 exit /b !IMPORT_EXIT!

set "SAVE_RETRYABLE=0"
if exist "%IMPORTLOG%" (
  findstr /I /C:"Error deleting file" /C:"Error saving" "%IMPORTLOG%" >nul
  if not errorlevel 1 set "SAVE_RETRYABLE=1"
)
if not "!SAVE_RETRYABLE!"=="1" exit /b !IMPORT_EXIT!

echo PRODUCTION_IMPORT_RECOVERY_BEGIN reason=save-delete-failure
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PREFLIGHT%" -Workspace "%GITHUB_WORKSPACE%"
if errorlevel 1 exit /b 54
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Start-Sleep -Seconds 2"
set ATTEMPT=2
goto run_import

:verify_success
findstr /C:"ShireProductionImport:" "%IMPORTLOG%" | findstr /C:"0 failures" >nul
if errorlevel 1 exit /b 51
echo UE4.27.2 production asset import succeeded.

rem Only the isolated FBX candidate probe may skip Frodo's expensive LFS/
rem animation lane. Shipping and regular production imports still require it.
if /I "%~1"=="-EnableCharacterRigImport" if /I "%SHIRE_TECHNICAL_RIG_BRIDGE_ONLY%"=="1" (
  echo KAYKIT_RIG_ISOLATED_IMPORT_PASS frodoPersistentImport=skipped notShippingProof=yes
  exit /b 0
)

call :import_frodo_runtime
if errorlevel 1 exit /b !ERRORLEVEL!
echo UE4.27.2 production asset import + persistent Frodo runtime import succeeded.
exit /b 0

:import_frodo_runtime
set "FRODO_ROOT=%GITHUB_WORKSPACE%\SourceAssets\ValidatedRuntime\FRODO"
set "FRODO_RIG=%FRODO_ROOT%\SK_FRODO_Validated.fbx"
set "FRODO_IDLE=%FRODO_ROOT%\Frodo_Idle_Retarget.fbx"
set "FRODO_WALK=%FRODO_ROOT%\Frodo_Walk_Retarget.fbx"
set "FRODO_RUN=%FRODO_ROOT%\Frodo_Run_Retarget.fbx"
set "FRODOLOG=%LOGDIR%\CI-FrodoPersistentRuntimeImport.log"

for %%F in ("%FRODO_RIG%" "%FRODO_IDLE%" "%FRODO_WALK%" "%FRODO_RUN%") do (
  if not exist "%%~F" (
    echo P1C01_FRODO_PERSISTENT_RUNTIME_IMPORT_FAIL reason=tracked_fbx_missing path="%%~F"
    exit /b 55
  )
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "$checks=@(@('%FRODO_RIG%','75d715f6ce4673a650a4382bc4f86b7ae0baf0fe548cc63f9b6ded1800f669be'),@('%FRODO_IDLE%','ee81650714587d2a1a638f3ff0c1a8239ea555bf84959e96ce5d037af3f33cd3'),@('%FRODO_WALK%','c4091b7881a4e9e810e70bb7f3abed58683dff5bacf54e26ccb2e926e4c9e688'),@('%FRODO_RUN%','4a4d10d91343dbd701c535d30ea9d9384ca74596cd7720cf6bfdd1c6328e1fc1')); $bad=@(); foreach($row in $checks){$actual=(Get-FileHash -LiteralPath $row[0] -Algorithm SHA256).Hash.ToLowerInvariant(); if($actual -ne $row[1]){$bad += $row[0]}}; if($bad.Count -gt 0){exit 9}; exit 0"
if errorlevel 1 (
  echo P1C01_FRODO_LFS_HYDRATE_BEGIN
  git -C "%GITHUB_WORKSPACE%" lfs pull --include="SourceAssets/ValidatedRuntime/FRODO/*.fbx" --exclude=""
  if errorlevel 1 exit /b 56

  powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
    "$checks=@(@('%FRODO_RIG%','75d715f6ce4673a650a4382bc4f86b7ae0baf0fe548cc63f9b6ded1800f669be'),@('%FRODO_IDLE%','ee81650714587d2a1a638f3ff0c1a8239ea555bf84959e96ce5d037af3f33cd3'),@('%FRODO_WALK%','c4091b7881a4e9e810e70bb7f3abed58683dff5bacf54e26ccb2e926e4c9e688'),@('%FRODO_RUN%','4a4d10d91343dbd701c535d30ea9d9384ca74596cd7720cf6bfdd1c6328e1fc1')); foreach($row in $checks){$actual=(Get-FileHash -LiteralPath $row[0] -Algorithm SHA256).Hash.ToLowerInvariant(); if($actual -ne $row[1]){Write-Host ('P1C01_FRODO_PERSISTENT_RUNTIME_HASH_FAIL path='+$row[0]+' expected='+$row[1]+' actual='+$actual); exit 10}}; Write-Host 'P1C01_FRODO_PERSISTENT_RUNTIME_HASH_PASS assets=4'"
  if errorlevel 1 exit /b 57
) else (
  echo P1C01_FRODO_PERSISTENT_RUNTIME_HASH_PASS assets=4
)

if exist "%FRODOLOG%" del /F /Q "%FRODOLOG%" >nul 2>nul
"%EDITORCMD%" "%PROJECT%" -run=ShireFrodoAnimationImport -TargetFbx="%FRODO_RIG%" -AnimationDir="%FRODO_ROOT%" -unattended -nop4 -nosplash -NoSound -abslog="%FRODOLOG%"
set "FRODO_EXIT=!ERRORLEVEL!"
if exist "%FRODOLOG%" findstr /I /C:"ShireFrodoAnimationImport:" /C:"Error:" /C:"Warning:" "%FRODOLOG%"
if not "!FRODO_EXIT!"=="0" exit /b !FRODO_EXIT!

findstr /C:"UE4_ANIMATION_PACKAGE_PERSISTENCE_PASS assets=5" "%FRODOLOG%" >nul
if errorlevel 1 exit /b 58
findstr /C:"UE4_ANIMATION_IMPORT_TECHNICAL_PASS clips=3 bones=48" "%FRODOLOG%" >nul
if errorlevel 1 exit /b 59

set "FRODO_PACKAGE_ROOT=%GITHUB_WORKSPACE%\Content\Production\Characters"
for %%P in (
  "%FRODO_PACKAGE_ROOT%\Rigs\FRODO\SK_FRODO.uasset"
  "%FRODO_PACKAGE_ROOT%\Rigs\FRODO\SK_FRODO_Skeleton.uasset"
  "%FRODO_PACKAGE_ROOT%\Animations\FRODO\A_Frodo_Idle.uasset"
  "%FRODO_PACKAGE_ROOT%\Animations\FRODO\A_Frodo_Walk.uasset"
  "%FRODO_PACKAGE_ROOT%\Animations\FRODO\A_Frodo_Run.uasset"
) do (
  if not exist "%%~P" (
    echo P1C01_FRODO_PERSISTENT_PACKAGE_FILE_FAIL path="%%~P"
    exit /b 60
  )
)
echo P1C01_FRODO_PERSISTENT_PACKAGE_FILE_PASS packages=5
echo P1C01_FRODO_PERSISTENT_RUNTIME_IMPORT_PASS packages=5 bones=48 clips=3
exit /b 0
