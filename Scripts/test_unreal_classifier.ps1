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
    @{Name='bag-end-hero-trim-source'; Paths=@('Data/P1C01BagEndHeroTrimSourceProbeV1.json','Docs/CURRENT_PROJECT_STATE.md','Docs/PRODUCTION_COMPLETENESS_MATRIX.md','Docs/WORLD_DETAIL_LEDGER.md'); Proof=$true; Mode='inherit'; TreeProof=$false},
    @{Name='bag-end-official-receipt-hosted'; Paths=@('Data/P1C01BagEndHeroTrimSourceProbeV1.json','Scripts/stage_p1c01_bag_end_trim_official_receipt.ps1','.github/workflows/p1c01-bag-end-trim-official-receipt.yml','Docs/CURRENT_PROJECT_STATE.md'); Proof=$true; Mode='inherit'; TreeProof=$false},
    @{Name='bag-end-static-fbx-qc-hosted'; Paths=@('Data/P1C01BagEndHeroTrimSourceProbeV1.json','Scripts/test_p1c01_bag_end_trim_static_fbx_qc.ps1','.github/workflows/p1c01-bag-end-trim-static-fbx-qc.yml','Docs/CURRENT_PROJECT_STATE.md'); Proof=$true; Mode='inherit'; TreeProof=$false},
    @{Name='frodo-dedicated-probe-source'; Paths=@('Data/P1C01FrodoKnightV2TechnicalProbe.json','Data/P1C01FrodoTechnicalRejectionHistoryV1.json','.github/workflows/p1c01-frodo-knight-v2-technical-probe.yml','Docs/CURRENT_PROJECT_STATE.md'); Proof=$true; Mode='inherit'; TreeProof=$false},
    @{Name='frodo-lowpoly-dummy-source-inventory'; Paths=@('Data/P1C01OpenGameArtLowpolyDummyCandidateV1.json','Scripts/inspect_p1c01_frodo_lowpoly_dummy_candidate.ps1','.github/workflows/p1c01-frodo-lowpoly-dummy-source-inventory.yml','Docs/CURRENT_PROJECT_STATE.md'); Proof=$true; Mode='inherit'; TreeProof=$false},
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

# Hosted full-history regression: tree-equivalent proof must probe the local parent object
# before attempting credential-dependent network fetch.
if (-not $source.Contains('rev-parse --verify --quiet "$ParentSha^{object}"')) {
    throw 'Classifier must probe local merge-parent object before tree-equivalent fetch'
}
if (-not $source.Contains('TREE_EQUIVALENT_PARENT_FETCH_REQUIRED')) {
    throw 'Classifier shallow-history fallback marker missing'
}
if (-not $source.Contains('"Data/P1C01BagEndHeroTrimSourceProbeV1.json"')) {
    throw 'Bag End hero trim source packet exact allowlist missing'
}
Write-Host 'UNREAL_CLASSIFIER_LOCAL_TREE_AND_BAG_END_SOURCE_PASS'

# Governance ancestry may cross merge commits with no direct run only when the entire
# intervening delta is safe and that ancestor has exact tree-equivalent core proof.
if (-not $source.Contains('Test-TreeEquivalentCoreProof $GitExe $candidate')) {
    throw 'Classifier transitive governance ancestor must support tree-equivalent proof'
}
if (-not $source.Contains('source=$proofSource')) {
    throw 'Classifier transitive governance proof source marker missing'
}
Write-Host 'UNREAL_CLASSIFIER_TRANSITIVE_GOVERNANCE_TREE_PROOF_PASS'
