$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$planPath = Join-Path $root "Data\SourceArchitecturePlan.json"
if (-not (Test-Path -LiteralPath $planPath -PathType Leaf)) {
    throw "Source architecture plan missing: $planPath"
}

$plan = Get-Content -LiteralPath $planPath -Raw | ConvertFrom-Json
if ([string]$plan.current_layout -ne "PUBLIC_PRIVATE_BY_DOMAIN") {
    Write-Host "Runtime source layout is not migrated; no persistent-workspace cleanup required."
    exit 0
}

$removed = 0
foreach ($entry in @($plan.files)) {
    if ([string]$entry.migration_status -ne "MIGRATED") { continue }

    $currentRelative = ([string]$entry.current_path).Replace("/", "\")
    $targetRelative = ([string]$entry.target_path).Replace("/", "\")
    if ([string]::IsNullOrWhiteSpace($currentRelative) -or
        [string]::IsNullOrWhiteSpace($targetRelative) -or
        $currentRelative -eq $targetRelative) {
        continue
    }

    $current = Join-Path $root $currentRelative
    $target = Join-Path $root $targetRelative

    if (-not (Test-Path -LiteralPath $target -PathType Leaf)) {
        throw "Mapped migrated target is missing; refusing to remove legacy path: $targetRelative"
    }

    if (Test-Path -LiteralPath $current -PathType Leaf) {
        Remove-Item -LiteralPath $current -Force
        if (Test-Path -LiteralPath $current) {
            throw "Failed to remove stale pre-migration runtime source: $currentRelative"
        }
        Write-Host "Removed stale pre-migration runtime source: $currentRelative"
        $removed++
    }
}

Write-Host "RUNTIME_SOURCE_LAYOUT_PREP_PASS removed=$removed layout=$($plan.current_layout)"
exit 0
