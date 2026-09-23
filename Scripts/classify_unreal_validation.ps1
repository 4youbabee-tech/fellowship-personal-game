$ErrorActionPreference = "Stop"

function Set-Decision([bool]$Full, [string]$Reason, [string]$ParentSha) {
    $v = if ($Full) { "true" } else { "false" }
    Add-Content -LiteralPath $env:GITHUB_ENV -Value "SHIRE_FULL_UNREAL_REQUIRED=$v"
    Add-Content -LiteralPath $env:GITHUB_ENV -Value "SHIRE_UNREAL_DECISION_REASON=$Reason"
    Add-Content -LiteralPath $env:GITHUB_ENV -Value "SHIRE_UNREAL_PARENT_SHA=$ParentSha"
    Write-Host "UNREAL_VALIDATION_DECISION full=$v parent=$ParentSha reason=$Reason"
}

Set-Location $env:GITHUB_WORKSPACE
$git = (Get-Command git.exe -ErrorAction SilentlyContinue).Source
if (-not $git) {
    foreach ($candidate in @(
        "C:\Program Files\Git\cmd\git.exe",
        "C:\Program Files (x86)\Git\cmd\git.exe",
        (Join-Path $env:RUNNER_TEMP "mingit-2.55.0.5\cmd\git.exe")
    )) {
        if (Test-Path -LiteralPath $candidate) { $git = $candidate; break }
    }
}
if (-not $git) { Set-Decision $true "git-unavailable-fail-safe" ""; exit 0 }

$parentSha = (& $git rev-parse "HEAD^").Trim()
if (-not $parentSha) { Set-Decision $true "parent-unavailable-fail-safe" ""; exit 0 }

$changed = @(& $git diff --name-only $parentSha $env:TARGET_SHA)
if ($LASTEXITCODE -ne 0 -or $changed.Count -eq 0) {
    Set-Decision $true "delta-unavailable-fail-safe" $parentSha
    exit 0
}

$safeExact = @(
    "Data/ProjectGovernor.json",
    "Data/DeepProjectAudit.json",
    "Data/MasterExecutionRoadmap.json",
    "Data/PIEVerificationEvidence.json",
    "Data/ProjectGovernor.schema.json",
    "Data/Production100ReadinessGate.json"
)
$unsafe=@()
foreach($p in $changed){
    $n=$p -replace "\\","/"
    if(-not $n.StartsWith("Docs/") -and -not ($safeExact -contains $n)){ $unsafe += $n }
}
if($unsafe.Count -gt 0){
    $unsafe | ForEach-Object { Write-Host "FULL_UNREAL_FILE $_" }
    Set-Decision $true "engine-or-ci-impact-delta" $parentSha
    exit 0
}
if(-not $env:GH_TOKEN){ Set-Decision $true "missing-token-fail-safe" $parentSha; exit 0 }

try {
    $headers=@{
        Authorization="Bearer $($env:GH_TOKEN)"
        Accept="application/vnd.github+json"
        "X-GitHub-Api-Version"="2022-11-28"
        "User-Agent"="ShireJourney-UnrealValidationClassifier"
    }
    $uri="https://api.github.com/repos/$($env:GITHUB_REPOSITORY)/actions/runs?head_sha=$parentSha&per_page=100"
    $r=Invoke-RestMethod -Uri $uri -Headers $headers -Method Get -TimeoutSec 20
    $green=@($r.workflow_runs | Where-Object {
        $_.name -eq "Unreal Build Validation" -and $_.status -eq "completed" -and $_.conclusion -eq "success"
    })
    if($green.Count -lt 1){
        Set-Decision $true "governance-only-but-parent-unreal-not-green" $parentSha
        exit 0
    }
} catch {
    Write-Host "Parent proof lookup failed: $($_.Exception.Message)"
    Set-Decision $true "parent-proof-lookup-failed-safe" $parentSha
    exit 0
}

Set-Decision $false "governance-docs-only-inherits-green-parent" $parentSha
