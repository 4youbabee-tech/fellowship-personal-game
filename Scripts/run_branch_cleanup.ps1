param(
    [string]$PlanPath = "Data/BranchCleanupPlan.json",
    [string]$Repository = $env:GITHUB_REPOSITORY
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($Repository)) {
    throw "GITHUB_REPOSITORY is required."
}
if ([string]::IsNullOrWhiteSpace($env:GH_TOKEN)) {
    throw "GH_TOKEN is required for active-PR safety checks."
}
if (-not (Test-Path -LiteralPath $PlanPath -PathType Leaf)) {
    throw "Branch cleanup plan missing: $PlanPath"
}

$plan = Get-Content -LiteralPath $PlanPath -Raw | ConvertFrom-Json
$deleteBranches = @($plan.delete_after_merge | ForEach-Object { [string]$_ } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

$planProtectedBranches = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::OrdinalIgnoreCase)
foreach ($protected in @("develop", "main")) {
    [void]$planProtectedBranches.Add($protected)
}
foreach ($branch in @($plan.active_work_branches)) {
    $name = [string]$branch
    if (-not [string]::IsNullOrWhiteSpace($name)) { [void]$planProtectedBranches.Add($name.Trim()) }
}
foreach ($entry in @($plan.preserve_pending_salvage)) {
    $name = [string]$entry.branch
    if (-not [string]::IsNullOrWhiteSpace($name)) { [void]$planProtectedBranches.Add($name.Trim()) }
}
foreach ($entry in @($plan.active_infrastructure_branches)) {
    $raw = [string]$entry
    if (-not [string]::IsNullOrWhiteSpace($raw)) {
        $name = ($raw -split '\s+/\s+', 2)[0].Trim()
        if ($name) { [void]$planProtectedBranches.Add($name) }
    }
}
foreach ($protected in $planProtectedBranches) {
    if ($deleteBranches -contains $protected) {
        throw "Refusing plan-protected branch in delete_after_merge: $protected"
    }
}

$headers = @{
    Authorization = "Bearer $($env:GH_TOKEN)"
    Accept = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}
$pullUri = "https://api.github.com/repos/$Repository/pulls?state=open&per_page=100"
$openPulls = @(Invoke-RestMethod -Method Get -Uri $pullUri -Headers $headers)
$activeHeads = @(
    $openPulls |
        ForEach-Object {
            if ($null -ne $_ -and $_.PSObject.Properties['head'] -and $null -ne $_.head -and $_.head.PSObject.Properties['ref']) {
                [string]$_.head.ref
            }
        } |
        Where-Object { $_ }
)

foreach ($branch in $deleteBranches) {
    if ($planProtectedBranches.Contains($branch)) {
        throw "Refusing plan-protected branch: $branch"
    }
    if ($activeHeads -contains $branch) {
        throw "Refusing to delete active PR head: $branch"
    }

    $remoteRef = "refs/heads/$branch"
    $existing = @(& git ls-remote --heads origin $remoteRef)
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to query remote branch: $branch"
    }
    if ($existing.Count -eq 0) {
        Write-Host "BRANCH_CLEANUP_ALREADY_ABSENT branch=$branch"
        continue
    }

    Write-Host "BRANCH_CLEANUP_DELETE branch=$branch"
    & git push origin --delete $branch
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to delete approved stale branch: $branch"
    }
}

$canonicalRefs = @(& git ls-remote --heads origin refs/heads/develop refs/heads/main)
if ($LASTEXITCODE -ne 0) {
    throw "Unable to query canonical refs."
}
if (@($canonicalRefs | Select-String "refs/heads/develop").Count -lt 1) {
    throw "develop missing after cleanup"
}
if (@($canonicalRefs | Select-String "refs/heads/main").Count -lt 1) {
    throw "main missing after cleanup"
}

foreach ($protected in @($planProtectedBranches | Where-Object { $_ -notin @("develop", "main") })) {
    $protectedRef = "refs/heads/$protected"
    $present = @(& git ls-remote --heads origin $protectedRef)
    if ($LASTEXITCODE -ne 0 -or $present.Count -eq 0) {
        throw "Plan-protected branch missing after cleanup: $protected"
    }
}
Write-Host ("BRANCH_CLEANUP_PASS deletedPlanCount=" + $deleteBranches.Count + " activePrHeads=" + $activeHeads.Count + " planProtected=" + $planProtectedBranches.Count + " canonical=develop stable=main")
