@echo off
"%PYTHON_EXE%" "%GITHUB_WORKSPACE%\Scripts\runtime_smoke.py" --editor "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Cmd.exe" --project "%GITHUB_WORKSPACE%\ShireJourney.uproject" --mode state
if errorlevel 1 exit /b 64
exit /b 0
