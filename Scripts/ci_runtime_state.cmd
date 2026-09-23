@echo off
"%PYTHON_EXE%" "%GITHUB_WORKSPACE%\Scripts\runtime_smoke.py" --editor "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Cmd.exe" --project "%GITHUB_WORKSPACE%\ShireJourney.uproject" --mode state
if errorlevel 1 exit /b 64
"%PYTHON_EXE%" "%GITHUB_WORKSPACE%\Scripts\runtime_smoke.py" --editor "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Cmd.exe" --project "%GITHUB_WORKSPACE%\ShireJourney.uproject" --mode transitions --timeout 120
if errorlevel 1 exit /b 65
"%PYTHON_EXE%" "%GITHUB_WORKSPACE%\Scripts\runtime_smoke.py" --editor "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Cmd.exe" --project "%GITHUB_WORKSPACE%\ShireJourney.uproject" --mode faults --timeout 90
if errorlevel 1 exit /b 66
"%PYTHON_EXE%" "%GITHUB_WORKSPACE%\Scripts\runtime_smoke.py" --editor "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Cmd.exe" --project "%GITHUB_WORKSPACE%\ShireJourney.uproject" --mode pending --timeout 90
if errorlevel 1 exit /b 67
exit /b 0
