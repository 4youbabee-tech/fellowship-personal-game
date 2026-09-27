$ErrorActionPreference = 'Stop'
$production = Join-Path $env:GITHUB_WORKSPACE 'Content\Production'
$sourceParent = Join-Path $env:GITHUB_WORKSPACE 'Content'
$destinationParent = $env:RUNNER_TEMP
if (-not $destinationParent -or -not (Test-Path -LiteralPath $destinationParent -PathType Container)) {
    Write-Output 'PRODUCTION_PREFLIGHT_FAIL reason=runner-temp-unavailable'
    exit 70
}
if ([IO.Path]::GetPathRoot($sourceParent) -ne [IO.Path]::GetPathRoot($destinationParent)) {
    Write-Output 'PRODUCTION_PREFLIGHT_FAIL reason=volume-mismatch'
    exit 71
}
$probeName = "CI-Production-MoveProbe-$env:GITHUB_RUN_ID-$env:GITHUB_RUN_ATTEMPT-$PID"
$sourceProbe = Join-Path $sourceParent $probeName
$destinationProbe = Join-Path $destinationParent $probeName
if ((Test-Path -LiteralPath $sourceProbe) -or (Test-Path -LiteralPath $destinationProbe)) {
    Write-Output 'PRODUCTION_PREFLIGHT_FAIL reason=probe-path-collision'
    exit 72
}
try {
    New-Item -ItemType Directory -Path $sourceProbe -ErrorAction Stop | Out-Null
    Set-Content -LiteralPath (Join-Path $sourceProbe 'probe.txt') -Value 'move-probe' -ErrorAction Stop
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'ci_report_production_locks.ps1') -Root $sourceProbe
    if ($LASTEXITCODE -ne 0) {
        Write-Output "PRODUCTION_PREFLIGHT_FAIL reason=lock-scanner exit=$LASTEXITCODE"
        exit 73
    }
    [IO.Directory]::Move($sourceProbe, $destinationProbe)
    [IO.Directory]::Move($destinationProbe, $sourceProbe)
    Write-Output 'PRODUCTION_PREFLIGHT_MOVE_PASS source-parent-and-runner-temp'
} catch {
    Write-Output "PRODUCTION_PREFLIGHT_FAIL reason=fresh-directory-move hresult=$($_.Exception.HResult) detail=$($_.Exception.Message)"
    exit 74
} finally {
    if (Test-Path -LiteralPath $sourceProbe) { Remove-Item -LiteralPath $sourceProbe -Recurse -Force -ErrorAction SilentlyContinue }
    if (Test-Path -LiteralPath $destinationProbe) { Remove-Item -LiteralPath $destinationProbe -Recurse -Force -ErrorAction SilentlyContinue }
}
if (-not (Test-Path -LiteralPath $production -PathType Container)) {
    Write-Output 'PRODUCTION_PREFLIGHT_SKIP reason=no-generated-tree'
    exit 0
}
$renamed = "$production.CI-RenameProbe-$env:GITHUB_RUN_ID-$env:GITHUB_RUN_ATTEMPT-$PID"
if (Test-Path -LiteralPath $renamed) {
    Write-Output 'PRODUCTION_PREFLIGHT_FAIL reason=production-probe-path-collision'
    exit 75
}
try {
    [IO.Directory]::Move($production, $renamed)
    [IO.Directory]::Move($renamed, $production)
    Write-Output 'PRODUCTION_PREFLIGHT_RENAME_PASS generated-tree'
} catch {
    Write-Output "PRODUCTION_PREFLIGHT_RENAME_FAIL hresult=$($_.Exception.HResult) detail=$($_.Exception.Message)"
    if ((Test-Path -LiteralPath $renamed) -and -not (Test-Path -LiteralPath $production)) {
        try {
            [IO.Directory]::Move($renamed, $production)
            Write-Output 'PRODUCTION_PREFLIGHT_RESTORE_PASS'
        } catch {
            Write-Output "PRODUCTION_PREFLIGHT_RESTORE_FAIL path=$renamed detail=$($_.Exception.Message)"
        }
    }
    if (Test-Path -LiteralPath $production) {
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'ci_report_production_locks.ps1') -Root $production
        Write-Output "PRODUCTION_PREFLIGHT_LOCK_SCAN_EXIT code=$LASTEXITCODE"
    }
    exit 76
}
