param(
    [string]$RunnerRoot = "C:\actions-runner",
    [string]$TaskName = "ShireJourney-GitHubRunner-Watchdog"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$identityObject = [System.Security.Principal.WindowsIdentity]::GetCurrent()
$identity = $identityObject.Name
$principalCheck = New-Object System.Security.Principal.WindowsPrincipal($identityObject)
$isAdmin = $principalCheck.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) { throw "Run this installer once from an elevated PowerShell window (Run as Administrator)." }
if ($identity -match 'NETWORK SERVICE') { throw "Do not install the watchdog under NETWORK SERVICE. Run it under the interactive Windows user that already proved UE4 access." }

$sourceWatchdog = Join-Path $PSScriptRoot "runner_watchdog.ps1"
$runCmd = Join-Path $RunnerRoot "run.cmd"
$supervisorRoot = Join-Path $RunnerRoot "supervisor"
$installedWatchdog = Join-Path $supervisorRoot "runner_watchdog.ps1"

if (-not (Test-Path -LiteralPath $sourceWatchdog -PathType Leaf)) { throw "Watchdog source missing: $sourceWatchdog" }
if (-not (Test-Path -LiteralPath $runCmd -PathType Leaf)) { throw "GitHub runner run.cmd missing: $runCmd" }

$workers = @(Get-Process -Name "Runner.Worker" -ErrorAction SilentlyContinue)
if ($workers.Count -gt 0) { throw "Runner.Worker is active. Wait for the live job to finish and run this installer again." }

New-Item -ItemType Directory -Path $supervisorRoot -Force | Out-Null
Copy-Item -LiteralPath $sourceWatchdog -Destination $installedWatchdog -Force

$runnerServices = @(Get-Service -Name "actions.runner.*" -ErrorAction SilentlyContinue)
foreach ($service in $runnerServices) {
    if ($service.Status -ne "Stopped") {
        Write-Host ("Stopping legacy runner service before supervised interactive-user mode: " + $service.Name)
        Stop-Service -Name $service.Name -Force
    }
    Set-Service -Name $service.Name -StartupType Manual
}

$listeners = @(Get-Process -Name "Runner.Listener" -ErrorAction SilentlyContinue)
foreach ($listener in $listeners) { Stop-Process -Id $listener.Id -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 2

$taskAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument ('-NoProfile -ExecutionPolicy Bypass -File "' + $installedWatchdog + '" -RunnerRoot "' + $RunnerRoot + '"')
$logonTrigger = New-ScheduledTaskTrigger -AtLogOn -User $identity
$recoveryTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 3650)
$taskTriggers = @($logonTrigger, $recoveryTrigger)
$taskPrincipal = New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Highest
$taskSettings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Days 3650)

Register-ScheduledTask -TaskName $TaskName -Action $taskAction -Trigger $taskTriggers -Principal $taskPrincipal -Settings $taskSettings -Description "Keeps the Shire Journey GitHub Actions runner alive; retries supervisor launch every five minutes and recycles only orphaned/stalled listeners when no Runner.Worker is active." -Force | Out-Null

Start-ScheduledTask -TaskName $TaskName
Start-Sleep -Seconds 5

$listenerNow = @(Get-Process -Name "Runner.Listener" -ErrorAction SilentlyContinue)
if ($listenerNow.Count -eq 0) { throw "Watchdog task installed, but Runner.Listener is not online. Check $RunnerRoot\_diag\ShireRunnerWatchdog.log." }

Write-Host ("SHIRE_RUNNER_WATCHDOG_INSTALLED task=" + $TaskName + " identity=" + $identity + " listenerPid=" + $listenerNow[0].Id)
Write-Host ("Watchdog copy: " + $installedWatchdog)
Write-Host ("Watchdog log: " + (Join-Path $RunnerRoot "_diag\ShireRunnerWatchdog.log"))
