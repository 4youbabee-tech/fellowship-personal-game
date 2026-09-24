param(
    [string]$Workspace = $env:GITHUB_WORKSPACE
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Workspace) -or -not (Test-Path -LiteralPath $Workspace -PathType Container)) {
    throw "RUNTIME_SOURCE_WORKSPACE_INVALID root=$Workspace"
}

Set-Location $Workspace
$git = (Get-Command git.exe -ErrorAction SilentlyContinue).Source
if (-not $git) {
    foreach ($candidate in @(
        "C:\Program Files\Git\cmd\git.exe",
        "C:\Program Files (x86)\Git\cmd\git.exe"
    )) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { $git = $candidate; break }
    }
}
if (-not $git) { throw "RUNTIME_SOURCE_WORKSPACE_GIT_MISSING" }

$tracked = @(& $git ls-files -- "Source")
if ($LASTEXITCODE -ne 0) { throw "RUNTIME_SOURCE_WORKSPACE_INDEX_READ_FAIL" }

$required = @($tracked | Where-Object { $_ -match '\.(?:h|cpp|cs)$' })
if ($required.Count -eq 0) { throw "RUNTIME_SOURCE_WORKSPACE_EMPTY_INDEX" }

function Get-Missing([string[]]$Paths) {
    return @($Paths | Where-Object {
        -not (Test-Path -LiteralPath (Join-Path $Workspace ($_.Replace("/", "\"))) -PathType Leaf)
    })
}

$missing = @(Get-Missing $required)
if ($missing.Count -gt 0) {
    Write-Host ("RUNTIME_SOURCE_WORKSPACE_REPAIR_BEGIN missing=" + $missing.Count)
    foreach ($relative in $missing) {
        Write-Host ("RUNTIME_SOURCE_WORKSPACE_RESTORE " + $relative)
        & $git checkout HEAD -- $relative
        if ($LASTEXITCODE -ne 0) {
            throw "RUNTIME_SOURCE_WORKSPACE_RESTORE_FAIL path=$relative"
        }
    }
}

$remaining = @(Get-Missing $required)
if ($remaining.Count -gt 0) {
    foreach ($relative in $remaining) {
        Write-Host ("RUNTIME_SOURCE_WORKSPACE_MISSING " + $relative)
    }
    throw "RUNTIME_SOURCE_WORKSPACE_INTEGRITY_FAIL missing=$($remaining.Count)"
}

$planPath = Join-Path $Workspace "Data\SourceArchitecturePlan.json"
if (-not (Test-Path -LiteralPath $planPath -PathType Leaf)) {
    throw "RUNTIME_SOURCE_ARCHITECTURE_PLAN_MISSING"
}
$plan = Get-Content -LiteralPath $planPath -Raw | ConvertFrom-Json
foreach ($entry in @($plan.files)) {
    $relative = if ([string]$entry.migration_status -eq "MIGRATED") {
        [string]$entry.target_path
    } else {
        [string]$entry.current_path
    }
    if ([string]::IsNullOrWhiteSpace($relative)) { continue }
    $absolute = Join-Path $Workspace ($relative.Replace("/", "\"))
    if (-not (Test-Path -LiteralPath $absolute -PathType Leaf)) {
        throw "RUNTIME_SOURCE_ARCHITECTURE_TARGET_MISSING path=$relative"
    }
}

Write-Host ("RUNTIME_SOURCE_WORKSPACE_INTEGRITY_PASS trackedSourceFiles=" + $required.Count)
exit 0
