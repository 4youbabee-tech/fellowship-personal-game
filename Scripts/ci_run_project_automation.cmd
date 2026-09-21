@echo off
setlocal EnableExtensions
set "PROJECT=%GITHUB_WORKSPACE%\ShireJourney.uproject"
set "EDITORCMD=C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Cmd.exe"
set "REPORTDIR=%GITHUB_WORKSPACE%\Saved\Automation\ShireJourneyQA"
set "LOGDIR=%GITHUB_WORKSPACE%\Saved\Logs"
set "AUTOMATIONLOG=%LOGDIR%\CI-ProjectAutomation.log"

if not exist "%EDITORCMD%" exit /b 80
if not defined PYTHON_EXE exit /b 81
if exist "%REPORTDIR%" rmdir /S /Q "%REPORTDIR%"
if not exist "%REPORTDIR%" mkdir "%REPORTDIR%"
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

"%EDITORCMD%" "%PROJECT%" -unattended -nop4 -nosplash -NoSound -NullRHI -ExecCmds="Automation RunTests ShireJourney.QA;Quit" -TestExit="Automation Test Queue Empty" -ReportOutputPath="%REPORTDIR%" -abslog="%AUTOMATIONLOG%"
set "EDITOR_EXIT=%ERRORLEVEL%"
if exist "%AUTOMATIONLOG%" findstr /I /C:"ShireJourney.QA" /C:"Automation Test Failed" /C:"Automation Test Succeeded" "%AUTOMATIONLOG%"
if not "%EDITOR_EXIT%"=="0" exit /b %EDITOR_EXIT%

"%PYTHON_EXE%" "%GITHUB_WORKSPACE%\Scripts\parse_automation_report.py" --report "%REPORTDIR%" --required-prefix "ShireJourney.QA"
if errorlevel 1 exit /b 82

echo ShireJourney Automation Framework suite passed.
exit /b 0
