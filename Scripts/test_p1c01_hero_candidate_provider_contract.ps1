$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$qtnPath = Join-Path $projectRoot "Data\WarehouseQuaterniusHeroCandidateBatchV1.json"
$ogaPath = Join-Path $projectRoot "Data\P1C01OpenGameArtHeroCandidateBatchV1.json"
$ogaRpgPath = Join-Path $projectRoot "Data\P1C01OpenGameArtRpgHeroCandidateBatchV1.json"
$wavePath = Join-Path $projectRoot "Data\P1C01HeroSkeletalCandidateWaveV1.json"
$workflowPath = Join-Path $projectRoot ".github\workflows\warehouse-stage.yml"

foreach($path in @($qtnPath,$ogaPath,$ogaRpgPath,$wavePath,$workflowPath)){
  if(-not (Test-Path -LiteralPath $path -PathType Leaf)){ throw "P1C01_HERO_PROVIDER_CONTRACT_MISSING path=$path" }
}
$qtn=Get-Content -LiteralPath $qtnPath -Raw | ConvertFrom-Json
$oga=Get-Content -LiteralPath $ogaPath -Raw | ConvertFrom-Json
$ogaRpg=Get-Content -LiteralPath $ogaRpgPath -Raw | ConvertFrom-Json
$wave=Get-Content -LiteralPath $wavePath -Raw | ConvertFrom-Json
$workflow=Get-Content -LiteralPath $workflowPath -Raw

$required=@($wave.authorized_source_packs | ForEach-Object {[string]$_} | Sort-Object -Unique)
$staged=@(
  @($qtn.source_pages | ForEach-Object {[string]$_.id})
  @($oga.assets | ForEach-Object {[string]$_.id})
  @($ogaRpg.assets | ForEach-Object {[string]$_.id})
) | Sort-Object -Unique
if($required.Count -ne $staged.Count){ throw "P1C01_HERO_PROVIDER_CONTRACT_COUNT_FAIL required=$($required.Count) staged=$($staged.Count)" }
foreach($id in $required){ if($staged -notcontains $id){ throw "P1C01_HERO_PROVIDER_CONTRACT_PACK_MISSING id=$id" } }
foreach($row in @($qtn.source_pages)+@($oga.assets)+@($ogaRpg.assets)){
  if(([string]$row.required_final_format).ToUpperInvariant() -ne "FBX"){ throw "P1C01_HERO_PROVIDER_CONTRACT_FORMAT_FAIL id=$([string]$row.id)" }
  if(([string]$row.observed_page_license).ToUpperInvariant() -ne "CC0"){ throw "P1C01_HERO_PROVIDER_CONTRACT_LICENSE_FAIL id=$([string]$row.id)" }
}
foreach($marker in @(
  "'Data/WarehouseQuaterniusHeroCandidateBatchV1.json'",
  "'Data/P1C01OpenGameArtHeroCandidateBatchV1.json'",
  "'Data/P1C01OpenGameArtRpgHeroCandidateBatchV1.json'",
  "- name: Stage P1C01 hero candidate provider batch",
  "- name: Stage OpenGameArt Quaternius character candidate",
  "- name: Stage alternate OpenGameArt Quaternius RPG character candidate",
  "- name: Build exact-head P1C01 Frodo Gandalf candidate report"
)){
  if(-not $workflow.Contains($marker)){ throw "P1C01_HERO_PROVIDER_CONTRACT_WORKFLOW_MARKER_MISSING marker=$marker" }
}
$qtnIndex=$workflow.IndexOf("- name: Stage P1C01 hero candidate provider batch",[StringComparison]::Ordinal)
$ogaIndex=$workflow.IndexOf("- name: Stage OpenGameArt Quaternius character candidate",[StringComparison]::Ordinal)
$ogaRpgIndex=$workflow.IndexOf("- name: Stage alternate OpenGameArt Quaternius RPG character candidate",[StringComparison]::Ordinal)
$reportIndex=$workflow.IndexOf("- name: Build exact-head P1C01 Frodo Gandalf candidate report",[StringComparison]::Ordinal)
if($qtnIndex -lt 0 -or $ogaIndex -le $qtnIndex -or $ogaRpgIndex -le $ogaIndex -or $reportIndex -le $ogaRpgIndex){ throw "P1C01_HERO_PROVIDER_CONTRACT_ORDER_FAIL qtn=$qtnIndex oga=$ogaIndex ogaRpg=$ogaRpgIndex report=$reportIndex" }

Write-Host "P1C01_HERO_PROVIDER_CONTRACT_TEST_PASS packs=$($required.Count) directFallback=true precedes_candidate_report=true"
