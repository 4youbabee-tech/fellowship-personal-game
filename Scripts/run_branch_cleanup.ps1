param(
    [string]$PlanPath = "Data/BranchCleanupPlan.json",
    [string]$Repository = $env:GITHUB_REPOSITORY,
    [string]$ClosedHeadRef = $env:CLOSED_HEAD_REF,
    [string]$ClosedHeadSha = $env:CLOSED_HEAD_SHA
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

function Test-BranchHasOpenPull {
    param([Parameter(Mandatory = $true)][string]$Branch)

    $owner = ($Repository -split '/', 2)[0]
    if ([string]::IsNullOrWhiteSpace($owner)) {
        throw "Unable to derive repository owner for active-PR branch recheck."
    }
    $headValue = "${owner}:$Branch"
    $headFilter = [System.Uri]::EscapeDataString($headValue)
    $activeBranchUri = "https://api.github.com/repos/$Repository/pulls?state=open&head=$headFilter&per_page=1"
    try {
        $activeForBranch = @(Invoke-RestMethod -Method Get -Uri $activeBranchUri -Headers $headers)
    }
    catch {
        throw "Unable to recheck active PR ownership for branch: $Branch :: $($_.Exception.Message)"
    }

    $isActive = $activeForBranch.Count -gt 0
    Write-Host "BRANCH_CLEANUP_ACTIVE_HEAD_RECHECK branch=$Branch active=$($isActive.ToString().ToLowerInvariant())"
    return $isActive
}
function Remove-RemoteBranch {
    param(
        [Parameter(Mandatory = $true)][string]$Branch,
        [Parameter(Mandatory = $true)][string]$Reason
    )

    if ($planProtectedBranches.Contains($Branch)) {
        throw "Refusing plan-protected branch: $Branch"
    }
    if (($activeHeads -contains $Branch) -or (Test-BranchHasOpenPull -Branch $Branch)) {
        Write-Host "BRANCH_CLEANUP_KEEP_ACTIVE_PR branch=$Branch reason=$Reason"
        return $false
    }

    $remoteRef = "refs/heads/$Branch"
    $existing = @(& git ls-remote --heads origin $remoteRef)
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to query remote branch: $Branch"
    }
    if ($existing.Count -eq 0) {
        Write-Host "BRANCH_CLEANUP_ALREADY_ABSENT branch=$Branch reason=$Reason"
        return $false
    }

    Write-Host "BRANCH_CLEANUP_DELETE branch=$Branch reason=$Reason"
    & git push origin --delete $Branch
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to delete approved stale branch: $Branch"
    }
    return $true
}

# DEC-042/DEC-088: closing a PR ends the lifecycle of that exact head ref, whether the
# PR merged or was explicitly closed as superseded/abandoned. The exact-SHA check prevents
# deleting later work if the branch moved after the close event.
$deletedClosedHead = 0
if (-not [string]::IsNullOrWhiteSpace($ClosedHeadRef)) {
    $closedBranch = $ClosedHeadRef.Trim()
    $closedSha = ([string]$ClosedHeadSha).Trim()

    if ($closedBranch -in @("develop", "main")) {
        Write-Host "BRANCH_CLEANUP_CLOSED_HEAD_SKIP_CANONICAL branch=$closedBranch"
    }
    elseif (($activeHeads -contains $closedBranch) -or (Test-BranchHasOpenPull -Branch $closedBranch)) {
        Write-Host "BRANCH_CLEANUP_CLOSED_HEAD_KEEP_ACTIVE branch=$closedBranch"
    }
    else {
        $remoteRef = "refs/heads/$closedBranch"
        $existing = @(& git ls-remote --heads origin $remoteRef)
        if ($LASTEXITCODE -ne 0) {
            throw "Unable to query closed PR head branch: $closedBranch"
        }

        if ($existing.Count -eq 0) {
            Write-Host "BRANCH_CLEANUP_CLOSED_HEAD_ALREADY_ABSENT branch=$closedBranch"
        }
        else {
            $remoteSha = (($existing[0] -split "\s+")[0]).Trim()
            if ([string]::IsNullOrWhiteSpace($closedSha)) {
                throw "CLOSED_HEAD_SHA is required when CLOSED_HEAD_REF is present."
            }
            if (-not $remoteSha.Equals($closedSha, [System.StringComparison]::OrdinalIgnoreCase)) {
                Write-Host "BRANCH_CLEANUP_CLOSED_HEAD_MOVED branch=$closedBranch remoteSha=$remoteSha closedSha=$closedSha"
            }
            else {
                Write-Host "BRANCH_CLEANUP_CLOSED_HEAD_DELETE branch=$closedBranch sha=$remoteSha"
                & git push origin --delete $closedBranch
                if ($LASTEXITCODE -ne 0) {
                    throw "Failed to delete exact closed PR head branch: $closedBranch"
                }
                $deletedClosedHead = 1
            }
        }
    }
}

$deletedExplicit = 0
foreach ($branch in $deleteBranches) {
    if (Remove-RemoteBranch -Branch $branch -Reason "explicit-plan") {
        ++$deletedExplicit
    }
}

# DEC-042 root fix: delete_after_merge is a supplement, not the only discovery source.
$allRemoteLines = @(& git ls-remote --heads origin)
if ($LASTEXITCODE -ne 0) {
    throw "Unable to enumerate remote branches for automatic zero-ahead cleanup."
}
$remoteBranches = @(
    foreach ($line in $allRemoteLines) {
        if ($line -match 'refs/heads/(.+)$') {
            [string]$Matches[1]
        }
    }
) | Sort-Object -Unique

$deletedAuto = 0
$keptUnique = 0
foreach ($branch in $remoteBranches) {
    if ($planProtectedBranches.Contains($branch)) {
        continue
    }
    if ($activeHeads -contains $branch) {
        Write-Host "BRANCH_CLEANUP_KEEP_ACTIVE_PR branch=$branch"
        continue
    }
    if ($deleteBranches -contains $branch) {
        continue
    }

    $encodedBranch = [System.Uri]::EscapeDataString($branch)
    $compareUri = "https://api.github.com/repos/$Repository/compare/develop...$encodedBranch"
    try {
        $comparison = Invoke-RestMethod -Method Get -Uri $compareUri -Headers $headers
    }
    catch {
        throw "Unable to compare branch against develop: $branch :: $($_.Exception.Message)"
    }

    $ahead = [int]$comparison.ahead_by
    $behind = [int]$comparison.behind_by
    if ($ahead -eq 0) {
        Write-Host "BRANCH_CLEANUP_AUTO_ZERO_AHEAD branch=$branch ahead=$ahead behind=$behind"
        if (Remove-RemoteBranch -Branch $branch -Reason "auto-zero-ahead") {
            ++$deletedAuto
        }
    }
    else {
        ++$keptUnique
        Write-Host "BRANCH_CLEANUP_KEEP_UNIQUE branch=$branch ahead=$ahead behind=$behind"
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
Write-Host ("BRANCH_CLEANUP_PASS closedHeadDeleted=" + $deletedClosedHead + " deletedPlanCount=" + $deleteBranches.Count + " deletedExplicit=" + $deletedExplicit + " deletedAutoZeroAhead=" + $deletedAuto + " keptUnique=" + $keptUnique + " activePrHeads=" + $activeHeads.Count + " planProtected=" + $planProtectedBranches.Count + " canonical=develop stable=main")
