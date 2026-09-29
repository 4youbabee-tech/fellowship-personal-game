param(
    [switch]$Json
)

$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
$GovernorPath = Join-Path $RepoRoot 'Data\ProjectGovernor.json'
$StatePath = Join-Path $RepoRoot 'Docs\CURRENT_PROJECT_STATE.md'
$GatesPath = Join-Path $RepoRoot 'Docs\DEVELOPMENT_GATES.md'
$GuardianPath = Join-Path $RepoRoot 'Docs\PROJECT_GUARDIAN.md'

if (-not (Test-Path $GovernorPath)) {
    throw "ProjectGovernor not found at $GovernorPath"
}

$Governor = Get-Content $GovernorPath -Raw | ConvertFrom-Json

function Invoke-GitText {
    param([Parameter(Mandatory=$true)][string[]]$Args)
    try {
        $out = & git -C $RepoRoot @Args 2>$null
        if ($LASTEXITCODE -ne 0) { return $null }
        return (($out | Out-String).Trim())
    }
    catch {
        return $null
    }
}

$CurrentBranch = Invoke-GitText @('rev-parse','--abbrev-ref','HEAD')
$CurrentHead = Invoke-GitText @('rev-parse','HEAD')
$DevelopHead = Invoke-GitText @('rev-parse','develop')

$NextActions = @()
if ($Governor.execution_control -and $Governor.execution_control.next_actions) {
    $NextActions = @($Governor.execution_control.next_actions)
}
elseif ($Governor.immediate_next_large_actions) {
    $NextActions = @($Governor.immediate_next_large_actions)
}

$Target = $Governor.target_hardware
if (-not $Target) { $Target = $Governor.target_profile }

$CurrentFocus = $null
if ($Governor.current_focus -and $Governor.current_focus.rule) {
    $CurrentFocus = [string]$Governor.current_focus.rule
}

$ResumeStatus = $null
if ($Governor.production_resume_checkpoint_2026_09_27 -and $Governor.production_resume_checkpoint_2026_09_27.status) {
    $ResumeStatus = [string]$Governor.production_resume_checkpoint_2026_09_27.status
}

$Summary = [ordered]@{
    project = 'Shire Journey / Fellowship Personal Game'
    engine = [string]$Governor.engine
    authority = 'Data/ProjectGovernor.json'
    authority_guide = 'Docs/PROJECT_GOVERNOR.md'
    story_source_index = 'Data/OwnerSourceReferenceIndex.json'
    story_rule = if ($Governor.story_source_execution_contract) { [string]$Governor.story_source_execution_contract.no_story_shortcut_rule } else { $null }
    localization_rule = if ($Governor.localization_contract) { "English VO; Arabic subtitles/UI/objectives; canonical map location labels remain English." } else { $null }
    canonical_development_branch = [string]$Governor.branch_workflow.integration_branch
    stable_release_branch = [string]$Governor.branch_workflow.stable_release_branch
    current_git_branch = $CurrentBranch
    branch_warning = if ($CurrentBranch -and $Governor.branch_workflow.integration_branch -and ($CurrentBranch -ne [string]$Governor.branch_workflow.integration_branch)) { "You are not on the canonical development branch. Switch to $($Governor.branch_workflow.integration_branch) before inferring current state or editing." } else { $null }
    current_git_head = $CurrentHead
    develop_head = $DevelopHead
    active_lane = [string]$Governor.execution_control.active_lane
    active_gate = [string]$Governor.active_gate.id
    active_gate_status = [string]$Governor.active_gate.status
    visible_benchmark = [string]$Governor.current_focus.visible_benchmark
    current_status = $ResumeStatus
    current_focus = $CurrentFocus
    next_actions = $NextActions
    target_hardware = $Target
    evidence_boundary = [string]$Governor.active_gate.evidence_scope
    runner_ownership_rule = if ($Governor.runner_execution_contract) { "UE4 runner = interactive-user watchdog only; actions.runner.* should be absent or Stopped+Disabled pending deletion; NETWORK SERVICE/LOCAL SERVICE/SYSTEM forbidden; watchdog continuously removes recreated service mode; do not change topology without owner authorization." } else { $null }
    required_reading = @(
        'Docs/PROJECT_GOVERNOR.md',
        'Data/ProjectGovernor.json',
        'Data/OwnerSourceReferenceIndex.json',
        'Docs/CURRENT_PROJECT_STATE.md',
        'Docs/DEVELOPMENT_GATES.md',
        'Docs/PROJECT_GUARDIAN.md',
        'Docs/WORLD_DETAIL_LEDGER.md'
    )
}

if ($Json) {
    $Summary | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host ''
Write-Host '============================================================'
Write-Host ' SHIRE JOURNEY - NEW DEVELOPER / AI SESSION ENTRY'
Write-Host '============================================================'
Write-Host ''
Write-Host "Authority:            $($Summary.authority)"
Write-Host "Authority guide:      $($Summary.authority_guide)"
Write-Host "Story source index:   $($Summary.story_source_index)"
Write-Host "Engine:               $($Summary.engine)"
Write-Host "Development branch:   $($Summary.canonical_development_branch)"
Write-Host "Stable branch:        $($Summary.stable_release_branch)"
Write-Host "Current Git branch:   $($Summary.current_git_branch)"
Write-Host "Current HEAD:         $($Summary.current_git_head)"
Write-Host "Develop HEAD:         $($Summary.develop_head)"
if (-not [string]::IsNullOrWhiteSpace($Summary.branch_warning)) {
    Write-Host "BRANCH WARNING:       $($Summary.branch_warning)"
}
Write-Host ''
Write-Host "Active lane:          $($Summary.active_lane)"
Write-Host "Active gate:          $($Summary.active_gate) [$($Summary.active_gate_status)]"
Write-Host "Visible benchmark:    $($Summary.visible_benchmark)"
Write-Host "Current status:       $($Summary.current_status)"
Write-Host ''
Write-Host 'STORY / SOURCE RULE'
if ([string]::IsNullOrWhiteSpace($Summary.story_rule)) {
    Write-Host '  - Read the Governor and source index before story/world work.'
}
else {
    Write-Host "  $($Summary.story_rule)"
}
if (-not [string]::IsNullOrWhiteSpace($Summary.localization_rule)) {
    Write-Host "  Localization: $($Summary.localization_rule)"
}
Write-Host ''
Write-Host 'CURRENT FOCUS'
if ([string]::IsNullOrWhiteSpace($Summary.current_focus)) {
    Write-Host '  - No current_focus rule registered. Read the Governor before editing.'
}
else {
    Write-Host "  $($Summary.current_focus)"
}
Write-Host ''
Write-Host 'NEXT ALLOWED ACTIONS'
if ($NextActions.Count -eq 0) {
    Write-Host '  - No next_actions registered. Read the Governor before editing.'
}
else {
    foreach ($Action in $NextActions) {
        Write-Host "  - $Action"
    }
}
Write-Host ''
Write-Host 'READ IN THIS ORDER'
foreach ($Doc in $Summary.required_reading) {
    $Exists = Test-Path (Join-Path $RepoRoot $Doc)
    $Mark = if ($Exists) { '[OK]' } else { '[MISSING]' }
    Write-Host "  $Mark $Doc"
}
Write-Host ''
Write-Host 'RUNNER OWNERSHIP'
if (-not [string]::IsNullOrWhiteSpace($Summary.runner_ownership_rule)) {
    Write-Host "  $($Summary.runner_ownership_rule)"
}
Write-Host ''
Write-Host 'PROOF BOUNDARY'
Write-Host "  $($Summary.evidence_boundary)"
Write-Host ''
Write-Host 'RULES'
Write-Host '  - Do not work directly on main.'
Write-Host '  - Never enable/start actions.runner.*; use the interactive-user watchdog runner only.'
Write-Host '  - Do not reconstruct direction from old PRs or chat history.'
Write-Host '  - GitHub owns live PR/branch/workflow transport state.'
Write-Host '  - ProjectGovernor owns durable requirements, priorities, gates and evidence.'
Write-Host '  - STATIC/COMPILE evidence never implies PIE/DEVICE/VISUAL/PERFORMANCE acceptance.'
Write-Host '============================================================'
