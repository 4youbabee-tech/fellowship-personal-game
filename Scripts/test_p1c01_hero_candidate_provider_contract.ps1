$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$manifestPath = Join-Path $projectRoot "Data\WarehouseQuaterniusHeroCandidateBatchV1.json"
$wavePath = Join-Path $projectRoot "Data\P1C01HeroSkeletalCandidateWaveV1.json"
$workflowPath = Join-Path $projectRoot ".github\workflows\warehouse-stage.yml"

foreach($path in @($manifestPath,$wavePath,$workflowPath)){
    if(-not (Test-Path -LiteralPath $path -PathType Leaf)){ throw "P1C01_HERO_PROVIDER_CONTRACT_MISSING path=$path" }
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$wave = Get-Content -LiteralPath $wavePath -Raw | ConvertFrom-Json
$workflow = Get-Content -LiteralPath $workflowPath -Raw

$required = @($wave.authorized_source_packs | ForEach-Object { [string]$_ } | Sort-Object -Unique)
$staged = @($manifest.source_pages | ForEach-Object { [string]$_.id } | Sort-Object -Unique)

if($required.Count -ne $staged.Count){
    throw "P1C01_HERO_PROVIDER_CONTRACT_COUNT_FAIL required=$($required.Count) staged=$($staged.Count)"
}
foreach($id in $required){
    if($staged -notcontains $id){ throw "P1C01_HERO_PROVIDER_CONTRACT_PACK_MISSING id=$id" }
}
foreach($row in @($manifest.source_pages)){
    if(([string]$row.required_final_format).ToUpperInvariant() -ne "FBX"){
        throw "P1C01_HERO_PROVIDER_CONTRACT_FORMAT_FAIL id=$([string]$row.id) format=$([string]$row.required_final_format)"
    }
    if(([string]$row.observed_page_license).ToUpperInvariant() -ne "CC0"){
        throw "P1C01_HERO_PROVIDER_CONTRACT_LICENSE_FAIL id=$([string]$row.id)"
    }
}

$triggerMarker = "'Data/WarehouseQuaterniusHeroCandidateBatchV1.json'"
if(-not $workflow.Contains($triggerMarker)){
    throw "P1C01_HERO_PROVIDER_CONTRACT_TRIGGER_MISSING"
}

$stageMarker = 'WarehouseQuaterniusHeroCandidateBatchV1.json'
$reportMarker = 'run_p1c01_hero_skeletal_candidate_wave.ps1'
$stageIndex = $workflow.IndexOf($stageMarker,[StringComparison]::Ordinal)
$reportIndex = $workflow.IndexOf($reportMarker,[StringComparison]::Ordinal)
if($stageIndex -lt 0 -or $reportIndex -lt 0 -or $stageIndex -ge $reportIndex){
    throw "P1C01_HERO_PROVIDER_CONTRACT_ORDER_FAIL stage=$stageIndex report=$reportIndex"
}

$stageBlockStart = $workflow.LastIndexOf("- name: Stage P1C01 hero candidate provider batch",$stageIndex,[StringComparison]::Ordinal)
if($stageBlockStart -lt 0){ throw "P1C01_HERO_PROVIDER_CONTRACT_STEP_MISSING" }
$stageBlockLength = [Math]::Min(900,$workflow.Length-$stageBlockStart)
$stageBlock = $workflow.Substring($stageBlockStart,$stageBlockLength)
if(-not $stageBlock.Contains("if: github.event_name == 'push'")){
    throw "P1C01_HERO_PROVIDER_CONTRACT_PUSH_GATE_MISSING"
}

Write-Host "P1C01_HERO_PROVIDER_CONTRACT_TEST_PASS packs=$($required.Count) targeted=true precedes_candidate_report=true"
