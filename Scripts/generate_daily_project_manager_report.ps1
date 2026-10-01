param(
    [string]$ProjectRoot = "",
    [string]$OutputPath = "daily_manager_report.md",
    [datetime]$NowUtc = [DateTime]::UtcNow
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-ObjectProperty {
    param(
        [object]$Object,
        [string]$Name
    )

    if ($null -eq $Object) {
        return $false
    }

    return $null -ne $Object.PSObject.Properties[$Name]
}

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent $PSScriptRoot
}

$ProjectRoot = [IO.Path]::GetFullPath($ProjectRoot)
if (-not [IO.Path]::IsPathRooted($OutputPath)) {
    $OutputPath = Join-Path $ProjectRoot $OutputPath
}

$governorPath = Join-Path $ProjectRoot "Data\ProjectGovernor.json"
$waveMapPath = Join-Path $ProjectRoot "Data\CompletionWaveMapV1.json"

foreach ($path in @($governorPath, $waveMapPath)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "DAILY_MANAGER_REPORT_INPUT_MISSING path=$path"
    }
}

$gov = Get-Content -LiteralPath $governorPath -Raw | ConvertFrom-Json
$waves = Get-Content -LiteralPath $waveMapPath -Raw | ConvertFrom-Json

$current = $null
if ((Test-ObjectProperty -Object $gov -Name "daily_progress_reporting") -and
    (Test-ObjectProperty -Object $gov.daily_progress_reporting -Name "current_planning_percent")) {
    $current = [int]$gov.daily_progress_reporting.current_planning_percent
}

if ($null -eq $current) {
    $current = [int]$waves.baseline.planning_completion_percent
    if ((Test-ObjectProperty -Object $gov -Name "w00_final_closure") -and
        (Test-ObjectProperty -Object $gov.w00_final_closure -Name "status") -and
        ([string]$gov.w00_final_closure.status -like "CLOSED*")) {
        $current = 42
    }
}

$previous = $current
if ((Test-ObjectProperty -Object $gov -Name "daily_progress_reporting") -and
    (Test-ObjectProperty -Object $gov.daily_progress_reporting -Name "previous_planning_percent")) {
    $previous = [int]$gov.daily_progress_reporting.previous_planning_percent
}

Push-Location $ProjectRoot
try {
    $head = (& git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($head)) {
        throw "DAILY_MANAGER_REPORT_GIT_HEAD_FAIL"
    }

    $since = $NowUtc.AddHours(-24).ToString("o")
    $merges = @(& git log "--since=$since" --merges "--pretty=format:%h %s" | Select-Object -First 8)
    if ($LASTEXITCODE -ne 0) {
        throw "DAILY_MANAGER_REPORT_GIT_MERGE_LOG_FAIL"
    }

    $changes = @(& git log "--since=$since" --no-merges "--pretty=format:%h %s" | Select-Object -First 12)
    if ($LASTEXITCODE -ne 0) {
        throw "DAILY_MANAGER_REPORT_GIT_CHANGE_LOG_FAIL"
    }
}
finally {
    Pop-Location
}

$wave = $null
foreach ($item in @($waves.waves)) {
    if ($current -ge [int]$item.from_percent -and $current -lt [int]$item.to_percent) {
        $wave = $item
        break
    }
}

$activeLane = "UNKNOWN"
if ((Test-ObjectProperty -Object $gov -Name "current_focus") -and
    (Test-ObjectProperty -Object $gov.current_focus -Name "production_lane")) {
    $activeLane = [string]$gov.current_focus.production_lane
}

$activeGateId = "UNKNOWN"
$activeGateStatus = "UNKNOWN"
if (Test-ObjectProperty -Object $gov -Name "active_gate") {
    if (Test-ObjectProperty -Object $gov.active_gate -Name "id") {
        $activeGateId = [string]$gov.active_gate.id
    }
    if (Test-ObjectProperty -Object $gov.active_gate -Name "status") {
        $activeGateStatus = [string]$gov.active_gate.status
    }
}

$delta = $current - $previous
$deltaText = [string]::Format("{0:+0;-0;0}", $delta)

$report = New-Object "System.Collections.Generic.List[string]"
$report.Add("# Shire Journey - Daily Project Manager Report")
$report.Add("")
$report.Add(("- Generated UTC: {0}" -f $NowUtc.ToString("yyyy-MM-dd HH:mm")))
$report.Add(("- Develop head observed: {0}" -f $head))
$report.Add(("- Planning / production completion: **{0}%**" -f $current))
$report.Add(("- 24h planning delta: **{0} percentage points**" -f $deltaText))
$report.Add(("- Active lane: **{0}**" -f $activeLane))
$report.Add(("- Active gate: **{0}** - {1}" -f $activeGateId, $activeGateStatus))

if ($null -ne $wave) {
    $report.Add(("- Current wave: **{0} - {1}**" -f [string]$wave.id, [string]$wave.name))
    $report.Add(("- Wave range: {0}% -> {1}%" -f [int]$wave.from_percent, [int]$wave.to_percent))
}

$report.Add("")
$report.Add("## Meaningful movement in the last 24 hours")
foreach ($line in $merges) {
    if (-not [string]::IsNullOrWhiteSpace([string]$line)) {
        $report.Add(("- Merge: {0}" -f [string]$line))
    }
}
foreach ($line in $changes) {
    if (-not [string]::IsNullOrWhiteSpace([string]$line)) {
        $report.Add(("- Change: {0}" -f [string]$line))
    }
}
if ($merges.Count -eq 0 -and $changes.Count -eq 0) {
    $report.Add("- No repository commits recorded in the last 24 hours.")
}

if ($null -ne $wave) {
    $report.Add("")
    $report.Add("## Next percentage unlock")
    $exitPreview = @($wave.exit | Select-Object -First 4) -join "; "
    $report.Add(("- {0}% after: {1}" -f [int]$wave.to_percent, $exitPreview))
}

$report.Add("")
$report.Add("## Evidence boundary")
$report.Add("- This is a planning/production estimate, not a test-acceptance label.")
$report.Add("- Commit count alone never raises the percentage.")
$report.Add("- STATIC/COMPILE evidence does not imply PIE, DEVICE, VISUAL, PACING, or PERFORMANCE acceptance.")

if ((Test-ObjectProperty -Object $gov -Name "session_handoff") -and
    (Test-ObjectProperty -Object $gov.session_handoff -Name "unverified_acceptance")) {
    $items = @($gov.session_handoff.unverified_acceptance | Select-Object -First 8)
    if ($items.Count -gt 0) {
        $report.Add("")
        $report.Add("## Still awaiting human/device evidence")
        foreach ($item in $items) {
            $report.Add(("- {0}" -f [string]$item))
        }
    }
}

$parent = Split-Path -Parent $OutputPath
if (-not [string]::IsNullOrWhiteSpace($parent)) {
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
}

$report | Set-Content -LiteralPath $OutputPath -Encoding UTF8
Write-Host ("DAILY_MANAGER_REPORT_GENERATED path={0} current={1} previous={2} head={3}" -f $OutputPath, $current, $previous, $head)
