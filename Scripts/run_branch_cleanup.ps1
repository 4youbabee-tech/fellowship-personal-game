param(
    [string]$PlanPath = "Data/BranchCleanupPlan.json",
    [string]$Repository = $env:GITHUB_REPOSITORY,
    [string]$MergedHeadRef = $env:MERGED_HEAD_REF,
    [string]$MergedHeadSha = $env:MERGED_HEAD_SHA
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

function Remove-RemoteBranch {
    param(
        [Parameter(Mandatory = $true)][string]$Branch,
        [Parameter(Mandatory = $true)][string]$Reason
    )

    if ($planProtectedBranches.Contains($Branch)) {
        throw "Refusing plan-protected branch: $Branch"
    }
    if ($activeHeads -contains $Branch) {
        throw "Refusing to delete active PR head: $Branch"
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

# DEC-042/DEC-088: close the lifecycle of the exact merged PR head first.
# This is independent of the repository-level delete_branch_on_merge setting.
$deletedMergedHead = 0
if (-not [string]::IsNullOrWhiteSpace($MergedHeadRef)) {
    $mergedBranch = $MergedHeadRef.Trim()
    $mergedSha = ([string]$MergedHeadSha).Trim()

    if ($mergedBranch -in @("develop", "main")) {
        Write-Host "BRANCH_CLEANUP_MERGED_HEAD_SKIP_CANONICAL branch=$mergedBranch"
    }
    elseif ($activeHeads -contains $mergedBranch) {
        Write-Host "BRANCH_CLEANUP_MERGED_HEAD_KEEP_ACTIVE branch=$mergedBranch"
    }
    else {
        $remoteRef = "refs/heads/$mergedBranch"
        $existing = @(& git ls-remote --heads origin $remoteRef)
        if ($LASTEXITCODE -ne 0) {
            throw "Unable to query merged PR head branch: $mergedBranch"
        }

        if ($existing.Count -eq 0) {
            Write-Host "BRANCH_CLEANUP_MERGED_HEAD_ALREADY_ABSENT branch=$mergedBranch"
        }
        else {
            $remoteSha = (($existing[0] -split "\s+")[0]).Trim()
            if ([string]::IsNullOrWhiteSpace($mergedSha)) {
                throw "MERGED_HEAD_SHA is required when MERGED_HEAD_REF is present."
            }
            if (-not $remoteSha.Equals($mergedSha, [System.StringComparison]::OrdinalIgnoreCase)) {
                Write-Host "BRANCH_CLEANUP_MERGED_HEAD_MOVED branch=$mergedBranch remoteSha=$remoteSha mergedSha=$mergedSha"
            }
            else {
                Write-Host "BRANCH_CLEANUP_MERGED_HEAD_DELETE branch=$mergedBranch sha=$remoteSha"
                & git push origin --delete $mergedBranch
                if ($LASTEXITCODE -ne 0) {
                    throw "Failed to delete exact merged PR head branch: $mergedBranch"
                }
                $deletedMergedHead = 1
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
Write-Host ("BRANCH_CLEANUP_PASS mergedHeadDeleted=" + $deletedMergedHead + " deletedPlanCount=" + $deleteBranches.Count + " deletedExplicit=" + $deletedExplicit + " deletedAutoZeroAhead=" + $deletedAuto + " keptUnique=" + $keptUnique + " activePrHeads=" + $activeHeads.Count + " planProtected=" + $planProtectedBranches.Count + " canonical=develop stable=main")
