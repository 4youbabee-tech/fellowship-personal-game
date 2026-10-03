$ErrorActionPreference = 'Stop'
$source = Get-Content (Join-Path $PSScriptRoot 'classify_unreal_validation.ps1') -Raw
$tokens = $null
$parseErrors = $null
[void][System.Management.Automation.Language.Parser]::ParseInput($source, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count) { throw ($parseErrors | Out-String) }
# Exercise the real classifier; mock only Git/GitHub and replace process exit with return.
$mocks = @'
function Get-GitExe { return 'Test-Git' }
function Test-Git {
    $global:LASTEXITCODE = 0
    switch ($args[0]) {
        'fetch' { return }
        'diff' { return $script:Case.Paths }
        'rev-parse' { return 'candidate-parent' }
        'rev-list' { return @('candidate-parent') }
        default { throw "Unexpected Git call: $args" }
    }
}
function Test-ParentWholeWorkflowGreen([string]$ParentSha) {
    return $script:Case.Proof -and $ParentSha -eq 'candidate-parent'
}
function Test-ParentCoreUnrealGreen([string]$ParentSha) { return $true }
function Test-TreeEquivalentCoreProof([string]$GitExe, [string]$ParentSha) { return [bool]$script:Case.TreeProof }
function Set-Mode([string]$Mode, [string]$Reason, [string]$ParentSha, [string]$ResumeStage = 'none', [bool]$ResetIntermediates = $false) {
    $script:ActualMode = $Mode
    $script:ActualReset = $ResetIntermediates
}
'@
$marker = 'Set-Location $env:GITHUB_WORKSPACE'
if (-not $source.Contains($marker)) { throw 'Classifier entry point missing' }
$program = [scriptblock]::Create($source.Replace($marker, $mocks + [Environment]::NewLine + $marker).Replace('exit 0', 'return'))
$cases = @(
    @{Name='onboarding'; Paths=@('README.md','Scripts/new_developer_onboarding.ps1','Scripts/pre_unreal_validate.py'); Proof=$true; Mode='inherit'; TreeProof=$false},
    @{Name='handoff'; Paths=@('Scripts/governor_handoff.py','Scripts/test_governor_handoff.py'); Proof=$true; Mode='inherit'; TreeProof=$false},
    @{Name='p1c01-material-tooling'; Paths=@('Scripts/prepare_p1c01_material_intake.ps1','Scripts/promote_p1c01_material_intake.ps1','Scripts/run_p1c01_material_pipeline.ps1','Scripts/export_p1c01_material_source_branch.ps1','Scripts/pre_unreal_validate.py','Docs/CURRENT_PROJECT_STATE.md'); Proof=$true; Mode='inherit'; TreeProof=$false},
    @{Name='east-fields-source-plan'; Paths=@('Data/P1C01EastFieldsRowReplacementV1.json','Docs/CURRENT_PROJECT_STATE.md','Docs/PRODUCTION_COMPLETENESS_MATRIX.md','Docs/WORLD_DETAIL_LEDGER.md'); Proof=$true; Mode='inherit'; TreeProof=$false},
    @{Name='kaykit-source-registration'; Paths=@('Data/P1C01KayKitAdventurersHeroCandidateBatchV1.json','Scripts/test_p1c01_hero_candidate_provider_contract.ps1','Docs/CURRENT_PROJECT_STATE.md'); Proof=$true; Mode='inherit'; TreeProof=$false},
    @{Name='whole-game-source-packets'; Paths=@('Data/WholeGameChapterAssetDemandMatrixV1.json','Data/WholeGameChapterProductionPacketsV1.json','Scripts/test_whole_game_chapter_production_packets.ps1','Docs/CURRENT_PROJECT_STATE.md'); Proof=$true; Mode='inherit'; TreeProof=$false},
    @{Name='no-proof'; Paths=@('README.md','Scripts/pre_unreal_validate.py'); Proof=$false; Mode='full'; TreeProof=$false},
    @{Name='mixed-story'; Paths=@('README.md','Scripts/pre_unreal_validate.py','Source/ShireJourney/ShireQuestSubsystem.cpp'); Proof=$true; Mode='core'; TreeProof=$false},
    @{Name='config'; Paths=@('README.md','Config/DefaultGame.ini'); Proof=$true; Mode='full'; Reset=$false; TreeProof=$false},
    @{Name='build-rules'; Paths=@('Source/ShireJourney.Target.cs'); Proof=$true; Mode='full'; Reset=$true; TreeProof=$false},
    @{Name='streaming'; Paths=@('Data/ChapterAssetStreamingPlan.json'); Proof=$true; Mode='full'; TreeProof=$false},
    @{Name='unknown-script'; Paths=@('Scripts/new_unknown_tool.ps1'); Proof=$true; Mode='full'; TreeProof=$false},
    @{Name='runtime-data'; Paths=@('Data/QuestDefinitions.json'); Proof=$true; Mode='core'; TreeProof=$false},
    @{Name='editor-assets'; Paths=@('Source/ShireJourneyEditorTools/Import.cpp'); Proof=$true; Mode='asset'; TreeProof=$false},
    @{Name='workflow-policy-tree-proof'; Paths=@('.github/workflows/unreal-build-validation.yml'); Proof=$false; Mode='inherit'; TreeProof=$true},
    @{Name='workflow-policy-no-proof'; Paths=@('.github/workflows/unreal-build-validation.yml'); Proof=$false; Mode='full'; TreeProof=$false}
)
$oldWorkspace = $env:GITHUB_WORKSPACE
$oldBase = $env:BASE_SHA
$oldTarget = $env:TARGET_SHA
$oldToken = $env:GH_TOKEN
$oldLocation = Get-Location
try {
    $env:GITHUB_WORKSPACE = Split-Path -Parent $PSScriptRoot
    $env:BASE_SHA = 'integration-base'
    $env:TARGET_SHA = 'candidate'
    $env:GH_TOKEN = 'mock-no-network'
    foreach ($caseItem in $cases) {
        $script:Case = $caseItem
        $script:ActualMode = ''
        $script:ActualReset = $false
        & $program
        if ($script:ActualMode -ne $caseItem.Mode) {
            throw "$($caseItem.Name): expected $($caseItem.Mode), got $script:ActualMode"
        }
        $expectedReset = if ($caseItem.ContainsKey('Reset')) { [bool]$caseItem.Reset } else { $false }
        if ($script:ActualReset -ne $expectedReset) {
            throw "$($caseItem.Name): expected reset=$expectedReset, got reset=$script:ActualReset"
        }
        Write-Host "CLASSIFIER_TEST_PASS $($caseItem.Name) mode=$script:ActualMode reset=$script:ActualReset"
    }
} finally {
    $env:GITHUB_WORKSPACE = $oldWorkspace
    $env:BASE_SHA = $oldBase
    $env:TARGET_SHA = $oldTarget
    $env:GH_TOKEN = $oldToken
    Set-Location $oldLocation
}


# Exact source-only allowlist for Bag End hero trim probe; never broaden Data/ safety.
if(-not $source.Contains('"Data/P1C01BagEndHeroTrimSourceProbeV1.json"')){
    throw "UNREAL_CLASSIFIER_BAG_END_HERO_TRIM_SOURCE_ALLOWLIST_MISSING"
}
if($source.Contains('$n.StartsWith("Data/") -and $safe')){
    throw "UNREAL_CLASSIFIER_BROAD_DATA_SAFE_BYPASS_FORBIDDEN"
}
Write-Host "UNREAL_CLASSIFIER_BAG_END_HERO_TRIM_EXACT_ALLOWLIST_PASS"
