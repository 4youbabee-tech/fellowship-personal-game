$ErrorActionPreference = "Stop"

function Set-Mode([string]$Mode, [string]$Reason, [string]$ParentSha, [string]$ResumeStage = "none") {
    $full = if ($Mode -eq "full") { "true" } else { "false" }
    $acceptance = if ($Mode -eq "acceptance") { "true" } else { "false" }

    Add-Content -LiteralPath $env:GITHUB_ENV -Value "SHIRE_UNREAL_MODE=$Mode"
    Add-Content -LiteralPath $env:GITHUB_ENV -Value "SHIRE_FULL_UNREAL_REQUIRED=$full"
    Add-Content -LiteralPath $env:GITHUB_ENV -Value "SHIRE_ACCEPTANCE_ONLY=$acceptance"
    Add-Content -LiteralPath $env:GITHUB_ENV -Value "SHIRE_ACCEPTANCE_RESUME_STAGE=$ResumeStage"
    Add-Content -LiteralPath $env:GITHUB_ENV -Value "SHIRE_UNREAL_DECISION_REASON=$Reason"
    Add-Content -LiteralPath $env:GITHUB_ENV -Value "SHIRE_UNREAL_PARENT_SHA=$ParentSha"

    Write-Host "UNREAL_VALIDATION_DECISION mode=$Mode full=$full acceptance=$acceptance resume=$ResumeStage parent=$ParentSha reason=$Reason"
}

function Get-GitExe {
    $git = (Get-Command git.exe -ErrorAction SilentlyContinue).Source
    if ($git) { return $git }

    foreach ($candidate in @(
        "C:\Program Files\Git\cmd\git.exe",
        "C:\Program Files (x86)\Git\cmd\git.exe",
        (Join-Path $env:RUNNER_TEMP "mingit-2.55.0.5\cmd\git.exe")
    )) {
        if (Test-Path -LiteralPath $candidate) { return $candidate }
    }
    return $null
}

function Get-GitHubHeaders {
    return @{
        Authorization="Bearer $($env:GH_TOKEN)"
        Accept="application/vnd.github+json"
        "X-GitHub-Api-Version"="2022-11-28"
        "User-Agent"="ShireJourney-UnrealValidationClassifier"
    }
}

function Test-ParentWholeWorkflowGreen([string]$ParentSha) {
    if (-not $env:GH_TOKEN) { return $false }
    try {
        $headers = Get-GitHubHeaders
        $uri="https://api.github.com/repos/$($env:GITHUB_REPOSITORY)/actions/runs?head_sha=$ParentSha&per_page=100"
        $r=Invoke-RestMethod -Uri $uri -Headers $headers -Method Get -TimeoutSec 20
        $green=@($r.workflow_runs | Where-Object {
            $_.name -eq "Unreal Build Validation" -and
            $_.status -eq "completed" -and
            $_.conclusion -eq "success"
        })
        return $green.Count -ge 1
    } catch {
        Write-Host "Parent whole-workflow proof lookup failed: $($_.Exception.Message)"
        return $false
    }
}

function Test-PackagingCookConfigOnlyDelta([string]$GitExe, [string]$ParentSha, [string]$HeadSha) {
    $path = "Config/DefaultGame.ini"
    $diff = @(& $GitExe diff --unified=0 $ParentSha $HeadSha -- $path)
    if ($LASTEXITCODE -ne 0) { return $false }

    $requiredAdds = @(
        '+DirectoriesToAlwaysCook=(Path="/Game/Production/World")',
        '+DirectoriesToAlwaysCook=(Path="/Game/Production/Characters/Common")',
        '+DirectoriesToAlwaysCook=(Path="/Game/Production/Characters/Hobbit")',
        '+DirectoriesToAlwaysCook=(Path="/Game/Production/Enemies")'
    )
    $changedLines = @($diff | Where-Object {
        $_ -match '^[+-]' -and $_ -notmatch '^(---|\+\+\+)'
    })
    $trimmedChangedLines = @($changedLines | ForEach-Object { $_.Trim() })

    if ($trimmedChangedLines.Count -ne $requiredAdds.Count) { return $false }
    foreach ($line in $trimmedChangedLines) {
        if ($requiredAdds -notcontains $line) { return $false }
    }
    foreach ($required in $requiredAdds) {
        if ($trimmedChangedLines -notcontains $required) { return $false }
    }
    return $true
}

function Test-CiPackagingTargetOnlyDelta([string]$GitExe, [string]$ParentSha, [string]$HeadSha) {
    $path = "Source/ShireJourney.Target.cs"
    $diff = @(& $GitExe diff --unified=0 $ParentSha $HeadSha -- $path)
    if ($LASTEXITCODE -ne 0) { return $false }

    $changedLines = @($diff | Where-Object {
        $_ -match '^[+-]' -and $_ -notmatch '^(---|\+\+\+)'
    })
    if ($changedLines.Count -eq 0) { return $false }

    $hasCiGuard = $false
    $hasDbgHelpPolicy = $false
    foreach ($line in $changedLines) {
        $body = $line.Substring(1).Trim()
        if ($body -eq 'if (Environment.GetEnvironmentVariable("SHIRE_CI_NO_DEBUGINFO") == "1")') {
            $hasCiGuard = $true
            continue
        }
        if ($body -eq "WindowsPlatform.bUseBundledDbgHelp = false;") {
            $hasDbgHelpPolicy = $true
            continue
        }
        if ($body -in @("", "using System;", "{", "}")) {
            continue
        }
        return $false
    }

    return $hasCiGuard -and $hasDbgHelpPolicy
}

function Test-ParentCoreUnrealGreen([string]$ParentSha) {
    if (-not $env:GH_TOKEN) { return $false }

    $requiredSteps = @(
        "Build ShireJourneyEditor",
        "Import production assets in UE4.27.2",
        "Run ShireJourney Automation Framework QA",
        "Headless playable startup smoke",
        "Headless chapter-by-chapter runtime audit",
        "Headless route/story state roundtrip audit",
        "Summarize and guard runtime warning debt"
    )

    try {
        $headers = Get-GitHubHeaders
        $runsUri="https://api.github.com/repos/$($env:GITHUB_REPOSITORY)/actions/runs?head_sha=$ParentSha&per_page=100"
        $runs=Invoke-RestMethod -Uri $runsUri -Headers $headers -Method Get -TimeoutSec 20
        $candidates=@($runs.workflow_runs | Where-Object {
            $_.name -eq "Unreal Build Validation" -and $_.status -eq "completed"
        })

        foreach($run in $candidates) {
            $jobsUri="https://api.github.com/repos/$($env:GITHUB_REPOSITORY)/actions/runs/$($run.id)/jobs?per_page=100"
            $jobs=Invoke-RestMethod -Uri $jobsUri -Headers $headers -Method Get -TimeoutSec 20
            foreach($job in @($jobs.jobs)) {
                $stepMap=@{}
                foreach($step in @($job.steps)) {
                    $stepMap[$step.name] = $step.conclusion
                }

                $allGreen=$true
                foreach($required in $requiredSteps) {
                    if(-not $stepMap.ContainsKey($required) -or $stepMap[$required] -ne "success") {
                        $allGreen=$false
                        break
                    }
                }

                if($allGreen) {
                    Write-Host "PARENT_CORE_UNREAL_PROOF_PASS parent=$ParentSha run=$($run.id) job=$($job.id)"
                    return $true
                }

                if(
                    $stepMap.ContainsKey("Acceptance-only Unreal fast path") -and
                    $stepMap["Acceptance-only Unreal fast path"] -eq "success"
                ) {
                    Write-Host "PARENT_CORE_UNREAL_PROOF_PASS parent=$ParentSha run=$($run.id) job=$($job.id) source=transitive-acceptance"
                    return $true
                }
            }
        }
    } catch {
        Write-Host "Parent core Unreal proof lookup failed: $($_.Exception.Message)"
        return $false
    }

    return $false
}

function Test-ParentAcceptanceDataGreen([string]$ParentSha) {
    if (-not $env:GH_TOKEN) { return $false }

    $requiredSteps = @(
        "Build cook stage and archive real Windows package",
        "Verify packaged Runtime Data JSON payload"
    )

    try {
        $headers = Get-GitHubHeaders
        $runsUri="https://api.github.com/repos/$($env:GITHUB_REPOSITORY)/actions/runs?head_sha=$ParentSha&per_page=100"
        $runs=Invoke-RestMethod -Uri $runsUri -Headers $headers -Method Get -TimeoutSec 20
        $candidates=@($runs.workflow_runs | Where-Object {
            $_.name -eq "Unreal Build Validation" -and $_.status -eq "completed"
        })

        foreach($run in $candidates) {
            $jobsUri="https://api.github.com/repos/$($env:GITHUB_REPOSITORY)/actions/runs/$($run.id)/jobs?per_page=100"
            $jobs=Invoke-RestMethod -Uri $jobsUri -Headers $headers -Method Get -TimeoutSec 20
            foreach($job in @($jobs.jobs)) {
                $stepMap=@{}
                foreach($step in @($job.steps)) {
                    $stepMap[$step.name] = $step.conclusion
                }

                $allGreen=$true
                foreach($required in $requiredSteps) {
                    if(-not $stepMap.ContainsKey($required) -or $stepMap[$required] -ne "success") {
                        $allGreen=$false
                        break
                    }
                }

                if($allGreen) {
                    Write-Host "PARENT_ACCEPTANCE_DATA_PROOF_PASS parent=$ParentSha run=$($run.id) job=$($job.id)"
                    return $true
                }
            }
        }
    } catch {
        Write-Host "Parent package/data proof lookup failed: $($_.Exception.Message)"
        return $false
    }

    return $false
}

Set-Location $env:GITHUB_WORKSPACE
$git = Get-GitExe
if (-not $git) { Set-Mode "full" "git-unavailable-fail-safe" ""; exit 0 }

$parentSha = (& $git rev-parse "HEAD^").Trim()
if (-not $parentSha) { Set-Mode "full" "parent-unavailable-fail-safe" ""; exit 0 }

$changed = @(& $git diff --name-only $parentSha $env:TARGET_SHA)
if ($LASTEXITCODE -ne 0 -or $changed.Count -eq 0) {
    Set-Mode "full" "delta-unavailable-fail-safe" $parentSha
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

$acceptanceExact = @(
    ".github/workflows/unreal-build-validation.yml",
    "Scripts/classify_unreal_validation.ps1",
    "Scripts/pre_unreal_validate.py",
    "Scripts/ci_package_w00.ps1",
    "Scripts/ci_package_w00.cmd",
    "Scripts/verify_packaged_runtime_data.ps1",
    "Scripts/verify_packaged_startup.ps1",
    "Scripts/capture_runner_hardware.ps1",
    "Data/W00FinalClosurePlanV1.json"
)

$fullImpact = @()
$acceptanceTouched = @()
foreach($p in $changed){
    $n=$p -replace "\\","/"

    if($n.StartsWith("Docs/") -or ($safeExact -contains $n)){
        continue
    }
    if($acceptanceExact -contains $n){
        $acceptanceTouched += $n
        continue
    }
    if(
        $n -eq "Source/ShireJourney.Target.cs" -and
        (Test-CiPackagingTargetOnlyDelta $git $parentSha $env:TARGET_SHA)
    ){
        $acceptanceTouched += $n
        continue
    }
    if(
        $n -eq "Config/DefaultGame.ini" -and
        (Test-PackagingCookConfigOnlyDelta $git $parentSha $env:TARGET_SHA)
    ){
        $acceptanceTouched += $n
        continue
    }
    $fullImpact += $n
}

if($fullImpact.Count -gt 0){
    $fullImpact | ForEach-Object { Write-Host "FULL_UNREAL_FILE $_" }
    Set-Mode "full" "engine-runtime-config-or-unclassified-delta" $parentSha
    exit 0
}

if($acceptanceTouched.Count -gt 0){
    if(Test-ParentCoreUnrealGreen $parentSha){
        $acceptanceTouched | ForEach-Object { Write-Host "ACCEPTANCE_ONLY_FILE $_" }

        $startupResumeExact = @(
            ".github/workflows/unreal-build-validation.yml",
            "Scripts/classify_unreal_validation.ps1",
            "Scripts/pre_unreal_validate.py",
            "Scripts/verify_packaged_startup.ps1"
        )
        $startupResumeCandidate = (
            ($acceptanceTouched -contains "Scripts/verify_packaged_startup.ps1") -and
            (@($acceptanceTouched | Where-Object { $startupResumeExact -notcontains $_ }).Count -eq 0)
        )

        if($startupResumeCandidate -and (Test-ParentAcceptanceDataGreen $parentSha)){
            Set-Mode "acceptance" "startup-verifier-only-inherits-parent-package-data-proof" $parentSha "startup"
            exit 0
        }

        Set-Mode "acceptance" "acceptance-only-delta-inherits-parent-core-unreal-proof" $parentSha
        exit 0
    }
    Set-Mode "full" "acceptance-delta-parent-core-proof-missing-fail-safe" $parentSha
    exit 0
}

if(Test-ParentWholeWorkflowGreen $parentSha){
    Set-Mode "inherit" "governance-docs-only-inherits-green-parent" $parentSha
    exit 0
}

Set-Mode "full" "governance-only-but-parent-unreal-not-green" $parentSha
