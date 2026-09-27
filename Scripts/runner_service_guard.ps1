param(
    [string]$RunnerRoot = "C:\actions-runner"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$diagRoot = Join-Path $RunnerRoot "_diag"
if (-not (Test-Path -LiteralPath $diagRoot -PathType Container)) {
    New-Item -ItemType Directory -Path $diagRoot -Force | Out-Null
}
$guardLog = Join-Path $diagRoot "ShireRunnerServiceGuard.log"

function Write-GuardLog {
    param([string]$Message)
    $line = ("{0:o} {1}" -f [DateTime]::UtcNow, $Message)
    Write-Host $line
    try { Add-Content -LiteralPath $guardLog -Value $line -Encoding UTF8 } catch {}
}

function Get-ProcessOwnerName {
    param([object]$Process)
    try {
        $ownerResult = Invoke-CimMethod -InputObject $Process -MethodName GetOwner -ErrorAction Stop
        if ($ownerResult.ReturnValue -ne 0) { return "" }
        return (($ownerResult.Domain + "\" + $ownerResult.User).Trim("\"))
    }
    catch {
        return ""
    }
}

function Test-ForbiddenRunnerIdentity {
    param([string]$Owner)
    if ([string]::IsNullOrWhiteSpace($Owner)) { return $false }
    return $Owner -match '(?i)(^|\\)(NETWORK SERVICE|LOCAL SERVICE|SYSTEM)$'
}

$services = @(Get-Service -Name "actions.runner.*" -ErrorAction SilentlyContinue)
foreach ($service in $services) {
    try {
        Set-Service -Name $service.Name -StartupType Disabled -ErrorAction SilentlyContinue
    }
    catch {}

    if ($service.Status -ne "Stopped") {
        Write-GuardLog ("RUNNER_SERVICE_GUARD_STOP service=" + $service.Name + " status=" + $service.Status)
        try { Stop-Service -Name $service.Name -Force -ErrorAction SilentlyContinue } catch {}
        Start-Sleep -Seconds 2
    }

    $deleteOutput = & sc.exe delete $service.Name 2>&1
    $deleteExit = $LASTEXITCODE
    Write-GuardLog ("RUNNER_SERVICE_GUARD_DELETE service=" + $service.Name + " exit=" + $deleteExit + " output=" + (($deleteOutput | Out-String).Trim()))
}

foreach ($processName in @("Runner.Worker.exe","Runner.Listener.exe")) {
    foreach ($proc in @(Get-CimInstance Win32_Process -Filter ("Name='" + $processName + "'") -ErrorAction SilentlyContinue)) {
        $owner = Get-ProcessOwnerName -Process $proc
        if (Test-ForbiddenRunnerIdentity -Owner $owner) {
            Write-GuardLog ("RUNNER_SERVICE_GUARD_KILL process=" + $processName + " pid=" + $proc.ProcessId + " owner=" + $owner)
            Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
        }
    }
}

$remainingBad = @()
foreach ($processName in @("Runner.Worker.exe","Runner.Listener.exe")) {
    foreach ($proc in @(Get-CimInstance Win32_Process -Filter ("Name='" + $processName + "'") -ErrorAction SilentlyContinue)) {
        $owner = Get-ProcessOwnerName -Process $proc
        if (Test-ForbiddenRunnerIdentity -Owner $owner) {
            $remainingBad += ($processName + ":" + $proc.ProcessId + ":" + $owner)
        }
    }
}
if ($remainingBad.Count -gt 0) {
    throw ("Forbidden service-owned runner process survived guard: " + ($remainingBad -join ","))
}

$activeServices = @()
foreach ($service in @(Get-Service -Name "actions.runner.*" -ErrorAction SilentlyContinue)) {
    $escaped = $service.Name.Replace("'","''")
    $cim = Get-CimInstance Win32_Service -Filter ("Name='" + $escaped + "'") -ErrorAction SilentlyContinue
    if ($service.Status -ne "Stopped" -or ($null -ne $cim -and $cim.StartMode -ne "Disabled")) {
        $activeServices += ($service.Name + ":status=" + $service.Status + ":startMode=" + $cim.StartMode)
    }
}
if ($activeServices.Count -gt 0) {
    throw ("Legacy runner service is not inert: " + ($activeServices -join ","))
}

Write-GuardLog "RUNNER_SERVICE_GUARD_PASS legacyService=absent-or-stopped-disabled forbiddenProcesses=0"
