@echo off
"%PYTHON_EXE%" "%GITHUB_WORKSPACE%\Scripts\warning_debt_guard.py" --log-dir "%GITHUB_WORKSPACE%\Saved\Logs" --summary "%GITHUB_STEP_SUMMARY%"
if errorlevel 1 exit /b 65
exit /b 0
