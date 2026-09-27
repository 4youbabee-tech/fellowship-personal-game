param(
    [string]$RunnerRoot = "C:\actions-runner",
    [int]$PollSeconds = 15,
    [int]$AcquireHangSeconds = 150,
    [int]$WorkerIdleHangSeconds = 300,
    [int]$RestartCooldownSeconds = 20,
    [string]$ServiceGuardPath = "",
    [switch]$Once
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ($PollSeconds -lt 5) { throw "PollSeconds must be >= 5." }
if ($AcquireHangSeconds -lt 110) { throw "AcquireHangSeconds must be >= 110." }
if ($WorkerIdleHangSeconds -lt 180) { throw "WorkerIdleHangSeconds must be >= 180." }
if ($RestartCooldownSeconds -lt 5) { throw "RestartCooldownSeconds must be >= 5." }

$runCmd = Join-Path $RunnerRoot "run.cmd"
$diagRoot = Join-Path $RunnerRoot "_diag"
if (-not (Test-Path -LiteralPath $runCmd -PathType Leaf)) { throw "GitHub runner run.cmd not found: $runCmd" }
if (-not (Test-Path -LiteralPath $diagRoot -PathType Container)) { New-Item -ItemType Directory -Path $diagRoot -Force | Out-Null }

$watchLog = Join-Path $diagRoot "ShireRunnerWatchdog.log"
$serviceGuard = Join-Path $PSScriptRoot "runner_service_guard.ps1"
if (-not (Test-Path -LiteralPath $serviceGuard -PathType Leaf)) { throw "Runner service guard missing beside watchdog: $serviceGuard" }
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
    if (-not (Test-Path -LiteralPath $ServiceGuardPath -PathType Leaf)) {
        throw "Runner service guard missing: $ServiceGuardPath"
    }
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ServiceGuardPath -RunnerRoot $RunnerRoot
    if ($LASTEXITCODE -ne 0) {
        throw "Runner service guard failed with exit code $LASTEXITCODE."
    }
}


function Invoke-RunnerServiceGuard {
    $needsGuard = @(Get-Service -Name "actions.runner.*" -ErrorAction SilentlyContinue).Count -gt 0
    if (-not $needsGuard) {
        foreach ($processName in @("Runner.Worker.exe","Runner.Listener.exe")) {
            foreach ($proc in @(Get-CimInstance Win32_Process -Filter ("Name='" + $processName + "'") -ErrorAction SilentlyContinue)) {
                try {
                    $owner = Invoke-CimMethod -InputObject $proc -MethodName GetOwner -ErrorAction Stop
                    $ownerName = (($owner.Domain + "\" + $owner.User).Trim("\"))
                    if ($ownerName -match '(?i)(^|\\)(NETWORK SERVICE|LOCAL SERVICE|SYSTEM)
    param([string]$Line)
    if ($Line -match '^\[RUNNER (?<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}Z) ') {
        return [DateTime]::ParseExact($Matches["ts"], "yyyy-MM-dd HH:mm:ssZ", [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal).ToUniversalTime()
    }
    return $null
}

function Get-RunnerBrokerState {
    $latest = Get-ChildItem -LiteralPath $diagRoot -Filter "Runner_*.log" -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    if ($null -eq $latest) { return [pscustomobject]@{ LogPath = ""; AckUtc = $null; RunningUtc = $null } }

    $tail = @(Get-Content -LiteralPath $latest.FullName -Tail 800 -ErrorAction SilentlyContinue)
    $ackUtc = $null
    $runningUtc = $null
    foreach ($line in $tail) {
        if ($line -match 'Acknowledging runner request') {
            $parsed = Get-RunnerTimestampUtc $line
            if ($null -ne $parsed) { $ackUtc = $parsed }
        }
        if ($line -match 'Running job:') {
            $parsed = Get-RunnerTimestampUtc $line
            if ($null -ne $parsed) { $runningUtc = $parsed }
        }
    }
    return [pscustomobject]@{ LogPath = $latest.FullName; AckUtc = $ackUtc; RunningUtc = $runningUtc }
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

$hasMutex = $false
try {
    $hasMutex = $mutex.WaitOne(0, $false)
    if (-not $hasMutex) { throw "Another ShireJourney runner watchdog instance is already active." }
    $identity = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    Write-WatchLog ("SHIRE_RUNNER_WATCHDOG_BOOT identity=" + $identity + " root=" + $RunnerRoot + " acquireHangSeconds=" + $AcquireHangSeconds + " workerIdleHangSeconds=" + $WorkerIdleHangSeconds)
    Invoke-RunnerServiceGuard
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
                if ($null -ne $state.AckUtc) {
                    $ackStillPending = ($null -eq $state.RunningUtc) -or ($state.RunningUtc -lt $state.AckUtc)
                    if ($ackStillPending) {
                        $ageSeconds = ([DateTime]::UtcNow - $state.AckUtc).TotalSeconds
                        $workers = @(Get-Process -Name "Runner.Worker" -ErrorAction SilentlyContinue)
                        if ($ageSeconds -ge $AcquireHangSeconds -and $workers.Count -eq 0) { Recover-StalledAcquire -AckUtc $state.AckUtc -RunnerLog $state.LogPath }
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
) { $needsGuard = $true; break }
                } catch {}
            }
            if ($needsGuard) { break }
        }
    }
    if (-not $needsGuard) { return }

    Write-WatchLog "SHIRE_RUNNER_WATCHDOG_SERVICE_GUARD_TRIGGER"
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $serviceGuard -RunnerRoot $RunnerRoot
    if ($LASTEXITCODE -ne 0) { throw "runner_service_guard.ps1 failed with exit code $LASTEXITCODE" }
}

function Get-RunnerTimestampUtc {
    param([string]$Line)
    if ($Line -match '^\[RUNNER (?<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}Z) ') {
        return [DateTime]::ParseExact($Matches["ts"], "yyyy-MM-dd HH:mm:ssZ", [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::AssumeUniversal).ToUniversalTime()
    }
    return $null
}

function Get-RunnerBrokerState {
    $latest = Get-ChildItem -LiteralPath $diagRoot -Filter "Runner_*.log" -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
    if ($null -eq $latest) { return [pscustomobject]@{ LogPath = ""; AckUtc = $null; RunningUtc = $null } }

    $tail = @(Get-Content -LiteralPath $latest.FullName -Tail 800 -ErrorAction SilentlyContinue)
    $ackUtc = $null
    $runningUtc = $null
    foreach ($line in $tail) {
        if ($line -match 'Acknowledging runner request') {
            $parsed = Get-RunnerTimestampUtc $line
            if ($null -ne $parsed) { $ackUtc = $parsed }
        }
        if ($line -match 'Running job:') {
            $parsed = Get-RunnerTimestampUtc $line
            if ($null -ne $parsed) { $runningUtc = $parsed }
        }
    }
    return [pscustomobject]@{ LogPath = $latest.FullName; AckUtc = $ackUtc; RunningUtc = $runningUtc }
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

$hasMutex = $false
try {
    $hasMutex = $mutex.WaitOne(0, $false)
    if (-not $hasMutex) { throw "Another ShireJourney runner watchdog instance is already active." }
    $identity = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    Write-WatchLog ("SHIRE_RUNNER_WATCHDOG_BOOT identity=" + $identity + " root=" + $RunnerRoot + " acquireHangSeconds=" + $AcquireHangSeconds + " workerIdleHangSeconds=" + $WorkerIdleHangSeconds)
    Invoke-ServiceOwnershipGuard
    Recover-OrphanedListenerOnSupervisorBoot

    while ($true) {
        try {
            Invoke-ServiceOwnershipGuard
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
                if ($null -ne $state.AckUtc) {
                    $ackStillPending = ($null -eq $state.RunningUtc) -or ($state.RunningUtc -lt $state.AckUtc)
                    if ($ackStillPending) {
                        $ageSeconds = ([DateTime]::UtcNow - $state.AckUtc).TotalSeconds
                        $workers = @(Get-Process -Name "Runner.Worker" -ErrorAction SilentlyContinue)
                        if ($ageSeconds -ge $AcquireHangSeconds -and $workers.Count -eq 0) { Recover-StalledAcquire -AckUtc $state.AckUtc -RunnerLog $state.LogPath }
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
