param(
    [string]$RunnerRoot = "C:\actions-runner",
    [int]$PollSeconds = 15,
    [int]$AcquireHangSeconds = 150,
    [int]$RestartCooldownSeconds = 20,
    [switch]$Once
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ($PollSeconds -lt 5) { throw "PollSeconds must be >= 5." }
if ($AcquireHangSeconds -lt 110) { throw "AcquireHangSeconds must be >= 110." }
if ($RestartCooldownSeconds -lt 5) { throw "RestartCooldownSeconds must be >= 5." }

$runCmd = Join-Path $RunnerRoot "run.cmd"
$diagRoot = Join-Path $RunnerRoot "_diag"
if (-not (Test-Path -LiteralPath $runCmd -PathType Leaf)) { throw "GitHub runner run.cmd not found: $runCmd" }
if (-not (Test-Path -LiteralPath $diagRoot -PathType Container)) { New-Item -ItemType Directory -Path $diagRoot -Force | Out-Null }

$watchLog = Join-Path $diagRoot "ShireRunnerWatchdog.log"
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

function Start-RunnerListener {
    $existing = @(Get-Process -Name "Runner.Listener" -ErrorAction SilentlyContinue)
    if ($existing.Count -gt 0) { return }
    Write-WatchLog ("SHIRE_RUNNER_WATCHDOG_START root=" + $RunnerRoot)
    Start-Process -FilePath $runCmd -WorkingDirectory $RunnerRoot -WindowStyle Hidden
    Start-Sleep -Seconds 3
    $started = @(Get-Process -Name "Runner.Listener" -ErrorAction SilentlyContinue)
    if ($started.Count -eq 0) { throw "Runner.Listener did not start after run.cmd." }
    Write-WatchLog ("SHIRE_RUNNER_WATCHDOG_ONLINE pid=" + $started[0].Id)
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
    Write-WatchLog ("SHIRE_RUNNER_WATCHDOG_BOOT identity=" + $identity + " root=" + $RunnerRoot + " acquireHangSeconds=" + $AcquireHangSeconds)

    while ($true) {
        try {
            $listener = @(Get-Process -Name "Runner.Listener" -ErrorAction SilentlyContinue)
            if ($listener.Count -eq 0) {
                Start-RunnerListener
            }
            else {
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
