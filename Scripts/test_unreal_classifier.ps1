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
function Set-Mode([string]$Mode, [string]$Reason, [string]$ParentSha, [string]$ResumeStage = 'none') {
    $script:ActualMode = $Mode
}
'@
$marker = 'Set-Location $env:GITHUB_WORKSPACE'
if (-not $source.Contains($marker)) { throw 'Classifier entry point missing' }
$program = [scriptblock]::Create($source.Replace($marker, $mocks + [Environment]::NewLine + $marker).Replace('exit 0', 'return'))
$cases = @(
    @{Name='onboarding'; Paths=@('README.md','Scripts/new_developer_onboarding.ps1','Scripts/pre_unreal_validate.py'); Proof=$true; Mode='inherit'},
    @{Name='handoff'; Paths=@('Scripts/governor_handoff.py','Scripts/test_governor_handoff.py'); Proof=$true; Mode='inherit'},
    @{Name='no-proof'; Paths=@('README.md','Scripts/pre_unreal_validate.py'); Proof=$false; Mode='full'},
    @{Name='mixed-story'; Paths=@('README.md','Scripts/pre_unreal_validate.py','Source/ShireJourney/ShireQuestSubsystem.cpp'); Proof=$true; Mode='core'},
    @{Name='config'; Paths=@('README.md','Config/DefaultGame.ini'); Proof=$true; Mode='full'},
    @{Name='streaming'; Paths=@('Data/ChapterAssetStreamingPlan.json'); Proof=$true; Mode='full'},
    @{Name='unknown-script'; Paths=@('Scripts/new_unknown_tool.ps1'); Proof=$true; Mode='full'},
    @{Name='runtime-data'; Paths=@('Data/QuestDefinitions.json'); Proof=$true; Mode='core'},
    @{Name='editor-assets'; Paths=@('Source/ShireJourneyEditorTools/Import.cpp'); Proof=$true; Mode='asset'}
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
        & $program
        if ($script:ActualMode -ne $caseItem.Mode) {
            throw "$($caseItem.Name): expected $($caseItem.Mode), got $script:ActualMode"
        }
        Write-Host "CLASSIFIER_TEST_PASS $($caseItem.Name) mode=$script:ActualMode"
    }
} finally {
    $env:GITHUB_WORKSPACE = $oldWorkspace
    $env:BASE_SHA = $oldBase
    $env:TARGET_SHA = $oldTarget
    $env:GH_TOKEN = $oldToken
    Set-Location $oldLocation
}
