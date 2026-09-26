param(
    [string]$ExpectedRunnerName = "UE4-27-Windows",
    [string]$TaskName = "ShireJourney-GitHubRunner-Watchdog"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Fail([string]$Message) {
    Write-Host ("RUNNER_HEALTH_FAIL " + $Message)
    exit 91
}

$identityObject = [System.Security.Principal.WindowsIdentity]::GetCurrent()
$identity = $identityObject.Name
$current = [System.Diagnostics.Process]::GetCurrentProcess()
$currentSession = $current.SessionId

if ($identity -match 'NETWORK SERVICE|LOCAL SERVICE|SYSTEM') {
    Fail ("service-identity identity=" + $identity)
}
if ($env:RUNNER_NAME -and $env:RUNNER_NAME -ne $ExpectedRunnerName) {
    Fail ("unexpected-runner-name actual=" + $env:RUNNER_NAME + " expected=" + $ExpectedRunnerName)
}
if ($currentSession -eq 0) {
    Fail ("non-interactive-session sessionId=0 identity=" + $identity)
}

$explorers = @(Get-Process explorer -ErrorAction SilentlyContinue | Where-Object { $_.SessionId -eq $currentSession })
if ($explorers.Count -eq 0) {
    Fail ("no-interactive-explorer sessionId=" + $currentSession)
}
Write-Host ("RUNNER_HEALTH_IDENTITY_PASS identity=" + $identity + " sessionId=" + $currentSession + " runnerName=" + $env:RUNNER_NAME)

$serviceProblems = @()
foreach ($service in @(Get-Service "actions.runner.*" -ErrorAction SilentlyContinue)) {
    $escaped = $service.Name.Replace("'","''")
    $cim = Get-CimInstance Win32_Service -Filter ("Name='" + $escaped + "'")
    if ($service.Status -ne "Stopped" -or $cim.StartMode -ne "Manual") {
        $serviceProblems += ($service.Name + ":status=" + $service.Status + ":startMode=" + $cim.StartMode)
    }
}
if ($serviceProblems.Count -gt 0) {
    Fail ("legacy-service-ownership " + ($serviceProblems -join ","))
}
Write-Host "RUNNER_HEALTH_SERVICE_PASS legacyService=stopped-manual"

$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($null -eq $task) {
    Fail ("watchdog-task-missing task=" + $TaskName)
}
if ($task.Principal.UserId -ne $identity) {
    Fail ("watchdog-owner actual=" + $task.Principal.UserId + " expected=" + $identity)
}
if ($task.State -ne "Running") {
    Fail ("watchdog-state state=" + $task.State)
}
Write-Host ("RUNNER_HEALTH_WATCHDOG_PASS task=" + $TaskName + " state=" + $task.State + " owner=" + $task.Principal.UserId)

$listeners = @(Get-CimInstance Win32_Process -Filter "Name='Runner.Listener.exe'")
if ($listeners.Count -ne 1) {
    Fail ("listener-count count=" + $listeners.Count)
}
$listener = $listeners[0]
$listenerOwnerResult = Invoke-CimMethod -InputObject $listener -MethodName GetOwner
$listenerOwner = $listenerOwnerResult.Domain + "\" + $listenerOwnerResult.User
$listenerProcess = Get-Process -Id $listener.ProcessId -ErrorAction Stop
if ($listenerOwner -ne $identity) {
    Fail ("listener-owner actual=" + $listenerOwner + " expected=" + $identity)
}
if ($listenerProcess.SessionId -ne $currentSession) {
    Fail ("listener-session actual=" + $listenerProcess.SessionId + " expected=" + $currentSession)
}

$workers = @(Get-CimInstance Win32_Process -Filter "Name='Runner.Worker.exe'")
if ($workers.Count -lt 1) {
    Fail "worker-missing"
}
foreach ($worker in $workers) {
    $workerOwnerResult = Invoke-CimMethod -InputObject $worker -MethodName GetOwner
    $workerOwner = $workerOwnerResult.Domain + "\" + $workerOwnerResult.User
    $workerProcess = Get-Process -Id $worker.ProcessId -ErrorAction Stop
    if ($workerOwner -ne $identity) {
        Fail ("worker-owner pid=" + $worker.ProcessId + " actual=" + $workerOwner + " expected=" + $identity)
    }
    if ($workerProcess.SessionId -ne $currentSession) {
        Fail ("worker-session pid=" + $worker.ProcessId + " actual=" + $workerProcess.SessionId + " expected=" + $currentSession)
    }
}
Write-Host ("RUNNER_HEALTH_PROCESS_PASS listenerPid=" + $listener.ProcessId + " workers=" + $workers.Count + " sessionId=" + $currentSession)

if (-not (Test-NetConnection github.com -Port 443 -InformationLevel Quiet -WarningAction SilentlyContinue)) {
    Fail "github-443-unreachable"
}
Write-Host "RUNNER_HEALTH_NETWORK_PASS github443=true"

$probeRoot = if ($env:RUNNER_TEMP) { $env:RUNNER_TEMP } else { $env:TEMP }
$probe = Join-Path $probeRoot ("shire-runner-health-" + [Guid]::NewGuid().ToString("N") + ".tmp")
try {
    [System.IO.File]::WriteAllText($probe, "runner-health")
    if (-not (Test-Path -LiteralPath $probe -PathType Leaf)) {
        Fail ("temp-write-failed path=" + $probeRoot)
    }
} finally {
    Remove-Item -LiteralPath $probe -Force -ErrorAction SilentlyContinue
}
Write-Host ("RUNNER_HEALTH_WORKSPACE_PASS temp=" + $probeRoot)

$systemDrive = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
$os = Get-CimInstance Win32_OperatingSystem
$diskFreeGb = [Math]::Round($systemDrive.FreeSpace / 1GB, 1)
$memFreeMb = [Math]::Round($os.FreePhysicalMemory / 1KB, 0)
Write-Host ("RUNNER_HEALTH_RESOURCES diskFreeGB=" + $diskFreeGb + " memFreeMB=" + $memFreeMb)

$gpus = @(Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name)
$monitors = @(Get-CimInstance Win32_DesktopMonitor -ErrorAction SilentlyContinue | Where-Object { $_.Status -eq "OK" })
if ($gpus.Count -eq 0) {
    Fail "gpu-missing"
}
Write-Host ("RUNNER_HEALTH_DISPLAY_REPORT gpuCount=" + $gpus.Count + " monitorCount=" + $monitors.Count + " gpus=" + ($gpus -join " | "))

Write-Host ("RUNNER_HEALTH_PASS identity=" + $identity + " sessionId=" + $currentSession + " listenerPid=" + $listener.ProcessId + " workerCount=" + $workers.Count)
