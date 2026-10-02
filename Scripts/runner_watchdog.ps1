param(
    [string]$RunnerRoot = "D:\actions-runner",
    [int]$PollSeconds = 15,
    [int]$AcquireHangSeconds = 150,
    [int]$WorkerIdleHangSeconds = 300,
    [int]$BrokerTransportHangSeconds = 180,
    [int]$RestartCooldownSeconds = 20,
    [int]$ServiceGuardIntervalSeconds = 300,
    [string]$ServiceGuardPath = "",
    [switch]$Once
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ($PollSeconds -lt 5) { throw "PollSeconds must be >= 5." }
if ($AcquireHangSeconds -lt 110) { throw "AcquireHangSeconds must be >= 110." }
if ($WorkerIdleHangSeconds -lt 180) { throw "WorkerIdleHangSeconds must be >= 180." }
if ($BrokerTransportHangSeconds -lt 120) { throw "BrokerTransportHangSeconds must be >= 120." }
if ($RestartCooldownSeconds -lt 5) { throw "RestartCooldownSeconds must be >= 5." }

$runCmd = Join-Path $RunnerRoot "run.cmd"
$diagRoot = Join-Path $RunnerRoot "_diag"
if (-not (Test-Path -LiteralPath $runCmd -PathType Leaf)) { throw "GitHub runner run.cmd not found: $runCmd" }
if (-not (Test-Path -LiteralPath $diagRoot -PathType Container)) { New-Item -ItemType Directory -Path $diagRoot -Force | Out-Null }

$watchLog = Join-Path $diagRoot "ShireRunnerWatchdog.log"
if ([string]::IsNullOrWhiteSpace($ServiceGuardPath)) {
    $ServiceGuardPath = Join-Path $PSScriptRoot "runner_service_guard.ps1"
}
if (-not (Test-Path -LiteralPath $ServiceGuardPath -PathType Leaf)) {
    throw "runner_service_guard.ps1 missing: $ServiceGuardPath"
}
$timestampParserPath = Join-Path $PSScriptRoot "runner_log_timestamp.ps1"
if (-not (Test-Path -LiteralPath $timestampParserPath -PathType Leaf)) {
    throw "runner_log_timestamp.ps1 missing: $timestampParserPath"
}
. $timestampParserPath
$lastServiceGuardUtc = [DateTime]::MinValue
$mutex = New-Object System.Threading.Mutex($false, "ShireJourneyRunnerWatchdog")

function Write-WatchLog {
    param([string]$Message)
    $line = ("{0:o} {1}" -f [DateTime]::UtcNow, $Message)
    Write-Host $line
    try {
        if (Test-Path -LiteralPath $watchLog -PathType Leaf) {
            $item = Get-Item -LiteralPath $watchLog
            if ($item.Length -gt 5242880) { Move-Item -LiteralPath $watchLog -Destination ($watchLog + ".1") -Force }
        }
        Add-Content -LiteralPath $watchLog -Value $line -Encoding UTF8
    }
    catch { Write-Host ("WATCHDOG_LOG_WRITE_FAILED " + $_.Exception.Message) }
}

function Invoke-ServiceOwnershipGuard {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ServiceGuardPath -RunnerRoot $RunnerRoot
    if ($LASTEXITCODE -ne 0) {
        throw "runner_service_guard.ps1 failed with exit code $LASTEXITCODE"
    }
}

function Invoke-RunnerServiceGuard {
    $now = [DateTime]::UtcNow
    if (($now - $script:lastServiceGuardUtc).TotalSeconds -lt $ServiceGuardIntervalSeconds) { return }
    Write-WatchLog "SHIRE_RUNNER_WATCHDOG_SERVICE_GUARD_TRIGGER"
    Invoke-ServiceOwnershipGuard
    $script:lastServiceGuardUtc = $now
}

function Get-RunnerTimestampUtc {
    param([string]$Line)
    return ConvertFrom-RunnerLogTimestampUtc -Line $Line
}

function Get-RunnerBrokerState {
    $latest = Get-ChildItem -LiteralPath $diagRoot -Filter "Runner_*.log" -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    if ($null -eq $latest) {
        return [pscustomobject]@{
            LogPath = ""
            AckUtc = $null
            RunningUtc = $null
            ErrorUtc = $null
            HealthyUtc = $null
        }
    }

    $tail = @(Get-Content -LiteralPath $latest.FullName -Tail 1200 -ErrorAction SilentlyContinue)
    $evidence = Get-RunnerBrokerEvidenceFromLines -Lines $tail
    return [pscustomobject]@{
        LogPath = $latest.FullName
        AckUtc = $evidence.AckUtc
        RunningUtc = $evidence.RunningUtc
        ErrorUtc = $evidence.ErrorUtc
        HealthyUtc = $evidence.HealthyUtc
    }
}

function Get-LatestRunnerLog {
    return Get-ChildItem -LiteralPath $diagRoot -Filter "Runner_*.log" -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTimeUtc -Descending |
        Select-Object -First 1
}

function Get-LatestWorkerLog {
    return Get-ChildItem -LiteralPath $diagRoot -Filter "Worker_*.log" -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTimeUtc -Descending |
        Select-Object -First 1
}

function Test-RunnerBrokerListening {
    param([DateTime]$StartedUtc)
    $latest = Get-LatestRunnerLog
    if ($null -eq $latest) { return $false }
    if ($latest.LastWriteTimeUtc -lt $StartedUtc.AddSeconds(-5)) { return $false }
    $tail = @(Get-Content -LiteralPath $latest.FullName -Tail 250 -ErrorAction SilentlyContinue)
    return @($tail | Where-Object { $_ -match 'Listening for Jobs' }).Count -gt 0
}

function Get-DescendantProcessCount {
    param([int]$RootPid)
    $all = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue)
    if ($all.Count -eq 0) { return 0 }

    $parents = New-Object 'System.Collections.Generic.HashSet[int]'
    [void]$parents.Add($RootPid)
    $changed = $true
    while ($changed) {
        $changed = $false
        foreach ($proc in $all) {
            if ($parents.Contains([int]$proc.ParentProcessId) -and -not $parents.Contains([int]$proc.ProcessId)) {
                [void]$parents.Add([int]$proc.ProcessId)
                $changed = $true
            }
        }
    }
    return [Math]::Max(0, $parents.Count - 1)
}

function Test-StaleWorker {
    param([System.Diagnostics.Process]$Worker)

    $workerAgeSeconds = ([DateTime]::UtcNow - $Worker.StartTime.ToUniversalTime()).TotalSeconds
    if ($workerAgeSeconds -lt $WorkerIdleHangSeconds) { return $false }

    $descendants = Get-DescendantProcessCount -RootPid $Worker.Id
    if ($descendants -gt 0) { return $false }

    $latestWorkerLog = Get-LatestWorkerLog
    if ($null -eq $latestWorkerLog) { return $false }

    $logIdleSeconds = ([DateTime]::UtcNow - $latestWorkerLog.LastWriteTimeUtc).TotalSeconds
    if ($logIdleSeconds -lt $WorkerIdleHangSeconds) { return $false }

    Write-WatchLog ("SHIRE_RUNNER_WATCHDOG_STALE_WORKER pid=" + $Worker.Id + " workerAgeSeconds=" + [Math]::Round($workerAgeSeconds) + " logIdleSeconds=" + [Math]::Round($logIdleSeconds) + " descendants=0 log=" + $latestWorkerLog.FullName)
    return $true
}

function Recover-StaleWorker {
    param([System.Diagnostics.Process]$Worker)

    Write-WatchLog ("SHIRE_RUNNER_WATCHDOG_RECOVERY reason=stale-worker pid=" + $Worker.Id)
    Stop-Process -Id $Worker.Id -Force -ErrorAction SilentlyContinue
    foreach ($listener in @(Get-Process -Name "Runner.Listener" -ErrorAction SilentlyContinue)) {
        Stop-Process -Id $listener.Id -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds $RestartCooldownSeconds
    Start-RunnerListener
}

function Start-RunnerListener {
    $existing = @(Get-Process -Name "Runner.Listener" -ErrorAction SilentlyContinue)
    if ($existing.Count -gt 0) { return }
    $startedUtc = [DateTime]::UtcNow
    Write-WatchLog ("SHIRE_RUNNER_WATCHDOG_START root=" + $RunnerRoot)
    Start-Process -FilePath $runCmd -WorkingDirectory $RunnerRoot -WindowStyle Hidden

    $deadline = [DateTime]::UtcNow.AddSeconds(45)
    $started = @()
    $brokerListening = $false
    while ([DateTime]::UtcNow -lt $deadline) {
        Start-Sleep -Seconds 2
        $started = @(Get-Process -Name "Runner.Listener" -ErrorAction SilentlyContinue)
        if ($started.Count -gt 0 -and (Test-RunnerBrokerListening -StartedUtc $startedUtc)) {
            $brokerListening = $true
            break
        }
    }

    if ($started.Count -eq 0) { throw "Runner.Listener did not start after run.cmd." }
    if (-not $brokerListening) {
        foreach ($listener in $started) { Stop-Process -Id $listener.Id -Force -ErrorAction SilentlyContinue }
        throw "Runner.Listener process started but did not reach 'Listening for Jobs' within 45 seconds."
    }
    Write-WatchLog ("SHIRE_RUNNER_WATCHDOG_ONLINE pid=" + $started[0].Id + " brokerListening=true")
}

function Recover-OrphanedListenerOnSupervisorBoot {
    $workers = @(Get-Process -Name "Runner.Worker" -ErrorAction SilentlyContinue)
    if ($workers.Count -gt 0) {
        Write-WatchLog ("SHIRE_RUNNER_WATCHDOG_BOOT_RECOVERY_SKIP reason=worker-active")
        return
    }

    $listeners = @(Get-Process -Name "Runner.Listener" -ErrorAction SilentlyContinue)
    if ($listeners.Count -eq 0) { return }

    Write-WatchLog ("SHIRE_RUNNER_WATCHDOG_BOOT_RECOVERY reason=orphaned-listener count=" + $listeners.Count)
    foreach ($listener in $listeners) {
        Stop-Process -Id $listener.Id -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds $RestartCooldownSeconds
    Start-RunnerListener
}

function Recover-StalledAcquire {
    param([DateTime]$AckUtc, [string]$RunnerLog)
    $workers = @(Get-Process -Name "Runner.Worker" -ErrorAction SilentlyContinue)
    if ($workers.Count -gt 0) {
        Write-WatchLog ("SHIRE_RUNNER_WATCHDOG_RECOVERY_SKIP reason=worker-active ack=" + $AckUtc.ToString("o"))
        return
    }
    $listeners = @(Get-Process -Name "Runner.Listener" -ErrorAction SilentlyContinue)
    if ($listeners.Count -eq 0) { Start-RunnerListener; return }
    Write-WatchLog ("SHIRE_RUNNER_WATCHDOG_RECOVERY reason=ack-without-worker ack=" + $AckUtc.ToString("o") + " log=" + $RunnerLog)
    foreach ($listener in $listeners) { Stop-Process -Id $listener.Id -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds $RestartCooldownSeconds
    Start-RunnerListener
}

function Test-GitHubControlPlaneReachable {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $task = $client.ConnectAsync("github.com", 443)
        if (-not $task.Wait(5000)) { return $false }
        return $client.Connected
    }
    catch {
        return $false
    }
    finally {
        $client.Close()
        $client.Dispose()
    }
}

function Recover-BrokerTransportStall {
    param([DateTime]$ErrorUtc, [string]$RunnerLog)

    $workers = @(Get-Process -Name "Runner.Worker" -ErrorAction SilentlyContinue)
    if ($workers.Count -gt 0) {
        Write-WatchLog ("SHIRE_RUNNER_WATCHDOG_RECOVERY_SKIP reason=worker-active brokerError=" + $ErrorUtc.ToString("o"))
        return
    }

    if (-not (Test-GitHubControlPlaneReachable)) {
        Write-WatchLog ("SHIRE_RUNNER_WATCHDOG_NETWORK_BLOCKED brokerError=" + $ErrorUtc.ToString("o") + " endpoint=github.com:443")
        return
    }

    $listeners = @(Get-Process -Name "Runner.Listener" -ErrorAction SilentlyContinue)
    if ($listeners.Count -eq 0) { Start-RunnerListener; return }

    Write-WatchLog ("SHIRE_RUNNER_WATCHDOG_RECOVERY reason=broker-transport-stall brokerError=" + $ErrorUtc.ToString("o") + " log=" + $RunnerLog)
    foreach ($listener in $listeners) {
        Stop-Process -Id $listener.Id -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds $RestartCooldownSeconds
    Start-RunnerListener
}

$hasMutex = $false
try {
    $hasMutex = $mutex.WaitOne(0, $false)
    if (-not $hasMutex) { throw "Another ShireJourney runner watchdog instance is already active." }
    $identity = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    Write-WatchLog ("SHIRE_RUNNER_WATCHDOG_BOOT identity=" + $identity + " root=" + $RunnerRoot + " acquireHangSeconds=" + $AcquireHangSeconds + " workerIdleHangSeconds=" + $WorkerIdleHangSeconds + " brokerTransportHangSeconds=" + $BrokerTransportHangSeconds)
    Invoke-ServiceOwnershipGuard
    $script:lastServiceGuardUtc = [DateTime]::UtcNow
    Recover-OrphanedListenerOnSupervisorBoot

    while ($true) {
        try {
            Invoke-RunnerServiceGuard
            $listener = @(Get-Process -Name "Runner.Listener" -ErrorAction SilentlyContinue)
            if ($listener.Count -eq 0) {
                Start-RunnerListener
            }
            else {
                $workersNow = @(Get-Process -Name "Runner.Worker" -ErrorAction SilentlyContinue)
                $recoveredStaleWorker = $false
                foreach ($workerNow in $workersNow) {
                    if (Test-StaleWorker -Worker $workerNow) {
                        Recover-StaleWorker -Worker $workerNow
                        $recoveredStaleWorker = $true
                        break
                    }
                }
                if ($recoveredStaleWorker) {
                    if ($Once) { break }
                    Start-Sleep -Seconds $PollSeconds
                    continue
                }

                $state = Get-RunnerBrokerState
                $workers = @(Get-Process -Name "Runner.Worker" -ErrorAction SilentlyContinue)

                if ($null -ne $state.AckUtc) {
                    $ackStillPending = ($null -eq $state.RunningUtc) -or ($state.RunningUtc -lt $state.AckUtc)
                    if ($ackStillPending) {
                        $ageSeconds = ([DateTime]::UtcNow - $state.AckUtc).TotalSeconds
                        if ($ageSeconds -ge $AcquireHangSeconds -and $workers.Count -eq 0) {
                            Recover-StalledAcquire -AckUtc $state.AckUtc -RunnerLog $state.LogPath
                            if ($Once) { break }
                            Start-Sleep -Seconds $PollSeconds
                            continue
                        }
                    }
                }

                if ($null -ne $state.ErrorUtc) {
                    $transportStillBad = ($null -eq $state.HealthyUtc) -or ($state.HealthyUtc -lt $state.ErrorUtc)
                    if ($transportStillBad) {
                        $errorAgeSeconds = ([DateTime]::UtcNow - $state.ErrorUtc).TotalSeconds
                        if ($errorAgeSeconds -ge $BrokerTransportHangSeconds -and $workers.Count -eq 0) {
                            Recover-BrokerTransportStall -ErrorUtc $state.ErrorUtc -RunnerLog $state.LogPath
                        }
                    }
                }
            }
        }
        catch { Write-WatchLog ("SHIRE_RUNNER_WATCHDOG_LOOP_ERROR " + $_.Exception.Message) }
        if ($Once) { break }
        Start-Sleep -Seconds $PollSeconds
    }
}
finally {
    if ($hasMutex) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
}
