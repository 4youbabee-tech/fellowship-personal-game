param(
    [string]$RunnerRoot = "D:\actions-runner",
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
$sourceServiceGuard = Join-Path $PSScriptRoot "runner_service_guard.ps1"
$runCmd = Join-Path $RunnerRoot "run.cmd"
$supervisorRoot = Join-Path $RunnerRoot "supervisor"
$installedWatchdog = Join-Path $supervisorRoot "runner_watchdog.ps1"
$installedServiceGuard = Join-Path $supervisorRoot "runner_service_guard.ps1"

if (-not (Test-Path -LiteralPath $sourceWatchdog -PathType Leaf)) { throw "Watchdog source missing: $sourceWatchdog" }
if (-not (Test-Path -LiteralPath $sourceServiceGuard -PathType Leaf)) { throw "Runner service guard missing: $sourceServiceGuard" }
if (-not (Test-Path -LiteralPath $runCmd -PathType Leaf)) { throw "GitHub runner run.cmd missing: $runCmd" }

$workers = @(Get-Process -Name "Runner.Worker" -ErrorAction SilentlyContinue)
if ($workers.Count -gt 0) { throw "Runner.Worker is active. Wait for the live job to finish and run this installer again." }

New-Item -ItemType Directory -Path $supervisorRoot -Force | Out-Null
Copy-Item -LiteralPath $sourceWatchdog -Destination $installedWatchdog -Force
Copy-Item -LiteralPath $sourceServiceGuard -Destination $installedServiceGuard -Force

# Permanently eliminate service-mode ownership before starting the interactive watchdog.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $installedServiceGuard -RunnerRoot $RunnerRoot
if ($LASTEXITCODE -ne 0) { throw "Runner service guard failed with exit code $LASTEXITCODE." }

$listeners = @(Get-Process -Name "Runner.Listener" -ErrorAction SilentlyContinue)
foreach ($listener in $listeners) { Stop-Process -Id $listener.Id -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 2

$taskAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument ('-NoProfile -ExecutionPolicy Bypass -File "' + $installedWatchdog + '" -RunnerRoot "' + $RunnerRoot + '" -ServiceGuardPath "' + $installedServiceGuard + '"')
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

$serviceViolations = @()
foreach ($service in @(Get-Service -Name "actions.runner.*" -ErrorAction SilentlyContinue)) {
    $serviceNow = Get-CimInstance Win32_Service -Filter ("Name='" + $service.Name.Replace("'","''") + "'")
    if ($service.Status -ne "Stopped" -or $serviceNow.StartMode -ne "Disabled") {
        $serviceViolations += ($service.Name + ":status=" + $service.Status + ":startMode=" + $serviceNow.StartMode)
    }
}
if ($serviceViolations.Count -gt 0) { throw ("Legacy runner service survived permanent guard: " + ($serviceViolations -join ",")) }

$taskNow = Get-ScheduledTask -TaskName $TaskName
if ($taskNow.State -notin @("Running","Ready")) { throw ("Watchdog scheduled task is not healthy: " + $taskNow.State) }

Write-Host ("SHIRE_RUNNER_WATCHDOG_INSTALLED task=" + $TaskName + " identity=" + $identity + " listenerPid=" + $listenerNow[0].Id + " taskState=" + $taskNow.State + " serviceOwnership=absent-or-disabled-stopped")
Write-Host ("Watchdog copy: " + $installedWatchdog)
Write-Host ("Watchdog log: " + (Join-Path $RunnerRoot "_diag\ShireRunnerWatchdog.log"))
