$ErrorActionPreference = "Stop"

function Set-Mode([string]$Mode, [string]$Reason, [string]$ParentSha, [string]$ResumeStage = "none") {
    $full = if ($Mode -eq "full") { "true" } else { "false" }
    $core = if ($Mode -eq "core" -or $Mode -eq "asset") { "true" } else { "false" }
    $asset = if ($Mode -eq "asset") { "true" } else { "false" }
    $acceptance = if ($Mode -eq "acceptance") { "true" } else { "false" }

    Add-Content -LiteralPath $env:GITHUB_ENV -Value "SHIRE_UNREAL_MODE=$Mode"
    Add-Content -LiteralPath $env:GITHUB_ENV -Value "SHIRE_FULL_UNREAL_REQUIRED=$full"
    Add-Content -LiteralPath $env:GITHUB_ENV -Value "SHIRE_CORE_UNREAL_REQUIRED=$core"
    Add-Content -LiteralPath $env:GITHUB_ENV -Value "SHIRE_ASSET_IMPORT_ONLY=$asset"
    Add-Content -LiteralPath $env:GITHUB_ENV -Value "SHIRE_ACCEPTANCE_ONLY=$acceptance"
    Add-Content -LiteralPath $env:GITHUB_ENV -Value "SHIRE_ACCEPTANCE_RESUME_STAGE=$ResumeStage"
    Add-Content -LiteralPath $env:GITHUB_ENV -Value "SHIRE_UNREAL_DECISION_REASON=$Reason"
    Add-Content -LiteralPath $env:GITHUB_ENV -Value "SHIRE_UNREAL_PARENT_SHA=$ParentSha"

    Write-Host "UNREAL_VALIDATION_DECISION mode=$Mode full=$full core=$core asset=$asset acceptance=$acceptance resume=$ResumeStage parent=$ParentSha reason=$Reason"
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

function Test-SafeGovernanceDelta([string]$GitExe, [string]$BaseSha, [string]$HeadSha, [string[]]$SafeExact) {
    $delta = @(& $GitExe diff --name-only $BaseSha $HeadSha)
    if ($LASTEXITCODE -ne 0 -or $delta.Count -eq 0) { return $false }

    foreach ($path in $delta) {
        $n = $path -replace "\\","/"
        $safe = (
            $n.StartsWith("Docs/") -or
            ($SafeExact -contains $n) -or
            $n -eq "Scripts/project_governor.py" -or
            $n -eq "Scripts/asset_quality_audit.py" -or
            $n -eq ".github/workflows/pre-unreal-validation.yml" -or
            $n -eq "SHIRE_UPDATE_BUILD_LAUNCH.bat" -or
            $n -eq "SHIRE_PIE_VERIFY.bat"
        )
        if (-not $safe) { return $false }
    }
    return $true
}

function Test-NearestSafeGovernanceAncestorGreen([string]$GitExe, [string]$ParentSha, [string]$HeadSha, [string[]]$SafeExact) {
    if (-not $env:GH_TOKEN) { return $false }

    $ancestors = @(& $GitExe rev-list --first-parent --max-count=20 $ParentSha)
    if ($LASTEXITCODE -ne 0 -or $ancestors.Count -eq 0) { return $false }

    foreach ($candidate in $ancestors) {
        if (-not (Test-ParentWholeWorkflowGreen $candidate)) { continue }
        if (-not (Test-SafeGovernanceDelta $GitExe $candidate $HeadSha $SafeExact)) { continue }

        Write-Host "TRANSITIVE_GOVERNANCE_PROOF_PASS ancestor=$candidate parent=$ParentSha head=$HeadSha"
        return $true
    }

    return $false
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

                if(
                    $stepMap.ContainsKey("Governance/docs-only Unreal fast path") -and
                    $stepMap["Governance/docs-only Unreal fast path"] -eq "success"
                ) {
                    Write-Host "PARENT_CORE_UNREAL_PROOF_PASS parent=$ParentSha run=$($run.id) job=$($job.id) source=transitive-governance"
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

function Test-CoreProofSafeInterveningDelta([string]$GitExe, [string]$BaseSha, [string]$ParentSha) {
    $delta = @(& $GitExe diff --name-only $BaseSha $ParentSha)
    if ($LASTEXITCODE -ne 0) { return $false }
    if ($delta.Count -eq 0) { return $true }

    $safeExact = @(
        "Data/ProjectGovernor.json",
        "Data/DeepProjectAudit.json",
        "Data/BranchCleanupPlan.json",
        "Data/ProjectSourcePdfRegistryV1.json",
        "Data/P1C01SourceExtractionV1.json",
        "Data/P1C01SourceToProductionBridgeV1.json",
        "Data/P1C01MaterialImportWaveV1.json",
        "Data/P1C01WorldBuildIntakePacketV1.json",
        "Data/P1C01C3FoliageMaterialIdentityPlanV1.json",
        "Data/P1C01C4FoliageLodCullOverdrawPlanV1.json",
        "Data/P1C01DLightingSkyFogWaterPlanV1.json",
        "Data/P1C01ECharacterPresentationPlanV1.json",
        "Data/P1C01FLivingShirePlanV1.json",
        "Data/P1C01GQuestCinematicAudioPolishPlanV1.json",
        "Data/P1C01HTargetDeviceProfilingPlanV1.json",
        "Data/P1C01Gate67AcceptanceChecklistV1.json",
        ".github/workflows/pre-unreal-validation.yml",
        ".github/workflows/branch-cleanup.yml",
        ".github/workflows/warehouse-stage.yml",
        "Scripts/run_local_static_validation.ps1",
        "Scripts/prepare_p1c01_material_intake.ps1",
        "Scripts/promote_p1c01_material_intake.ps1",
        "Scripts/run_p1c01_material_pipeline.ps1"
    )

    foreach ($path in $delta) {
        $n = $path -replace "\\","/"
        $safe = (
            $n.StartsWith("Docs/") -or
            ($safeExact -contains $n) -or
            $n -like "Data/WholeGame*.json" -or
            $n -like "Data/*Warehouse*.json" -or
            $n -like "Scripts/stage_*warehouse*.ps1"
        )
        if (-not $safe) {
            Write-Host "TRANSITIVE_CORE_PROOF_BLOCKED file=$n base=$BaseSha parent=$ParentSha"
            return $false
        }
    }

    return $true
}

function Test-NearestSafeCoreAncestorGreen([string]$GitExe, [string]$ParentSha) {
    if (-not $env:GH_TOKEN) { return $false }

    $ancestors = @(& $GitExe rev-list --first-parent --max-count=40 $ParentSha)
    if ($LASTEXITCODE -ne 0 -or $ancestors.Count -eq 0) { return $false }

    foreach ($candidate in $ancestors) {
        if (-not (Test-ParentCoreUnrealGreen $candidate)) { continue }
        if (-not (Test-CoreProofSafeInterveningDelta $GitExe $candidate $ParentSha)) { continue }

        Write-Host "TRANSITIVE_CORE_PROOF_PASS ancestor=$candidate parent=$ParentSha"
        return $true
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

$parentSha = ""
if ($env:BASE_SHA) {
    $parentSha = $env:BASE_SHA.Trim()
}
if (-not $parentSha) {
    $parentSha = (& $git rev-parse "HEAD^").Trim()
}
if (-not $parentSha) { Set-Mode "full" "parent-unavailable-fail-safe" ""; exit 0 }

$changed = @(& $git diff --name-only $parentSha $env:TARGET_SHA)
if ($LASTEXITCODE -ne 0) {
    Write-Host "DELTA_BASE_FETCH_REQUIRED parent=$parentSha head=$($env:TARGET_SHA)"
    & $git fetch --no-tags --depth=1 origin $parentSha
    if ($LASTEXITCODE -eq 0) {
        $changed = @(& $git diff --name-only $parentSha $env:TARGET_SHA)
    }
}
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
    "Data/Production100ReadinessGate.json",
    "Data/W00FinalClosurePlanV1.json",
    "Data/BranchCleanupPlan.json",
    "Data/LivingWorldSensoryCompletenessPlanV1.json",
    "Data/VoiceProductionMasterPlanV1.json",
    "Data/GeneratedAudioWarehouseV1.json",
    "Data/P1C01AmbientSpeechAndBarksV1.json",
    "Data/P1C01CompleteAudioBankV1.json",
    "Data/P1C01NamedCharacterEffortsV1.json",
    "Data/WarehouseGapAuditSource09V1.json",
    "Scripts/operation_recovery.py",
    "Scripts/test_operation_recovery.py",
    ".github/workflows/branch-cleanup.yml"
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
    "Scripts/verify_runtime_source_workspace.ps1"
)

$fullImpact = @()
$coreImpact = @()
$policyOnlyTouched = @()
$acceptanceTouched = @()
foreach($p in $changed){
    $n=$p -replace "\\","/"

    if(
        $n.StartsWith("Docs/") -or
        ($safeExact -contains $n) -or
        $n -eq "Scripts/project_governor.py" -or
        $n -eq "Scripts/asset_quality_audit.py" -or
        $n -eq ".github/workflows/pre-unreal-validation.yml" -or
        $n -eq "SHIRE_UPDATE_BUILD_LAUNCH.bat" -or
        $n -eq "SHIRE_PIE_VERIFY.bat"
    ){
        continue
    }
    if($n -eq "Scripts/classify_unreal_validation.ps1" -or $n -eq "Scripts/pre_unreal_validate.py"){
        $policyOnlyTouched += $n
        continue
    }
    if($acceptanceExact -contains $n){
        $acceptanceTouched += $n
        continue
    }

    $isPackagingCritical = (
        $n.StartsWith("Config/") -or
        $n.EndsWith(".Build.cs") -or
        $n.EndsWith(".Target.cs") -or
        $n -match "ChapterAssetStreaming" -or
        $n -eq "Data/ChapterAssetStreamingPlan.json" -or
        $n -match "Package|Packaging|Cook|Release"
    )
    if($isPackagingCritical){
        $fullImpact += $n
        continue
    }

    $isCoreRuntime = (
        $n.StartsWith("Source/ShireJourney/") -or
        $n.StartsWith("Source/ShireJourneyEditorTools/") -or
        $n.StartsWith("SourceAssets/") -or
        $n.StartsWith("Data/")
    )
    if($isCoreRuntime){
        $coreImpact += $n
        continue
    }

    $fullImpact += $n
}

if($fullImpact.Count -gt 0){
    $fullImpact | ForEach-Object { Write-Host "FULL_UNREAL_FILE $_" }
    Set-Mode "full" "engine-runtime-config-or-unclassified-delta" $parentSha
    exit 0
}

if($policyOnlyTouched.Count -gt 0 -and $acceptanceTouched.Count -eq 0 -and $coreImpact.Count -eq 0 -and $fullImpact.Count -eq 0){
    if(Test-ParentWholeWorkflowGreen $parentSha){
        $policyOnlyTouched | ForEach-Object { Write-Host "VALIDATION_POLICY_ONLY_FILE $_" }
        Set-Mode "inherit" "validation-policy-only-inherits-green-parent-no-engine-repeat" $parentSha
        exit 0
    }
    Set-Mode "full" "validation-policy-only-parent-not-green-fail-safe" $parentSha
    exit 0
}

if($coreImpact.Count -gt 0){
    $assetOnlyAllowed = @(
        "Data/P1C01MaterialsVegetationPlanV1.json"
    )
    $assetOnlyDelta = @($coreImpact | Where-Object {
        (-not $_.StartsWith("Source/ShireJourneyEditorTools/")) -and
        ($assetOnlyAllowed -notcontains $_)
    }).Count -eq 0

    if($assetOnlyDelta){
        $coreImpact | ForEach-Object { Write-Host "ASSET_IMPORT_ONLY_FILE $_" }
        Set-Mode "asset" "editor-tool-or-p1c01-material-delta-build-import-startup-only" $parentSha
        exit 0
    }

    if(Test-ParentCoreUnrealGreen $parentSha){
        $coreImpact | ForEach-Object { Write-Host "CORE_UNREAL_FILE $_" }
        Set-Mode "core" "runtime-or-asset-delta-inherits-parent-core-proof-no-package" $parentSha
        exit 0
    }
    if(Test-NearestSafeCoreAncestorGreen $git $parentSha){
        $coreImpact | ForEach-Object { Write-Host "CORE_UNREAL_FILE $_" }
        Set-Mode "core" "runtime-or-asset-delta-inherits-nearest-safe-core-ancestor-no-package" $parentSha
        exit 0
    }
    Set-Mode "full" "core-delta-no-safe-core-proof-fail-safe" $parentSha
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

if(Test-NearestSafeGovernanceAncestorGreen $git $parentSha $env:TARGET_SHA $safeExact){
    Set-Mode "inherit" "governance-docs-only-inherits-nearest-safe-green-ancestor" $parentSha
    exit 0
}

Set-Mode "full" "governance-only-no-safe-green-ancestor-fail-safe" $parentSha
