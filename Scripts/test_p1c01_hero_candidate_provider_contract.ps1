$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$qtnPath = Join-Path $projectRoot "Data\WarehouseQuaterniusHeroCandidateBatchV1.json"
$ogaPath = Join-Path $projectRoot "Data\P1C01OpenGameArtHeroCandidateBatchV1.json"
$ogaRpgPath = Join-Path $projectRoot "Data\P1C01OpenGameArtRpgHeroCandidateBatchV1.json"
$kayPath = Join-Path $projectRoot "Data\P1C01KayKitAdventurersHeroCandidateBatchV1.json"
$kayHoodedPath = Join-Path $projectRoot "Data\P1C01KayKitAdventurersRogueHoodedHeroCandidateBatchV1.json"
$kenneyPath = Join-Path $projectRoot "Data\P1C01KenneyBlockyHeroCandidateBatchV1.json"
$wavePath = Join-Path $projectRoot "Data\P1C01HeroSkeletalCandidateWaveV1.json"
$workflowPath = Join-Path $projectRoot ".github\workflows\warehouse-stage.yml"

foreach($path in @($qtnPath,$ogaPath,$ogaRpgPath,$kayPath,$kayHoodedPath,$kenneyPath,$wavePath,$workflowPath)){
  if(-not (Test-Path -LiteralPath $path -PathType Leaf)){ throw "P1C01_HERO_PROVIDER_CONTRACT_MISSING path=$path" }
}
$qtn=Get-Content -LiteralPath $qtnPath -Raw | ConvertFrom-Json
$oga=Get-Content -LiteralPath $ogaPath -Raw | ConvertFrom-Json
$ogaRpg=Get-Content -LiteralPath $ogaRpgPath -Raw | ConvertFrom-Json
$kay=Get-Content -LiteralPath $kayPath -Raw | ConvertFrom-Json
$kayHooded=Get-Content -LiteralPath $kayHoodedPath -Raw | ConvertFrom-Json
$kenney=Get-Content -LiteralPath $kenneyPath -Raw | ConvertFrom-Json
$wave=Get-Content -LiteralPath $wavePath -Raw | ConvertFrom-Json
$workflow=Get-Content -LiteralPath $workflowPath -Raw

$required=@($wave.authorized_source_packs | ForEach-Object {[string]$_} | Sort-Object -Unique)
$stagedAll=@(
  @($qtn.source_pages | ForEach-Object {[string]$_.id})
  @($oga.assets | ForEach-Object {[string]$_.id})
  @($ogaRpg.assets | ForEach-Object {[string]$_.id})
  @($kay.assets | ForEach-Object {[string]$_.id})
  @($kayHooded.assets | ForEach-Object {[string]$_.id})
  @($kenney.assets | ForEach-Object {[string]$_.id})
) | Sort-Object -Unique
$staged=@($stagedAll | Where-Object { $required -contains $_ })
if($required.Count -ne $staged.Count){ throw "P1C01_HERO_PROVIDER_CONTRACT_COUNT_FAIL required=$($required.Count) staged=$($staged.Count)" }
foreach($id in $required){ if($staged -notcontains $id){ throw "P1C01_HERO_PROVIDER_CONTRACT_PACK_MISSING id=$id" } }
foreach($row in @($qtn.source_pages)+@($oga.assets)+@($ogaRpg.assets)+@($kay.assets)+@($kayHooded.assets)+@($kenney.assets)){
  if(([string]$row.required_final_format).ToUpperInvariant() -ne "FBX"){ throw "P1C01_HERO_PROVIDER_CONTRACT_FORMAT_FAIL id=$([string]$row.id)" }
  if(([string]$row.observed_page_license).ToUpperInvariant() -ne "CC0"){ throw "P1C01_HERO_PROVIDER_CONTRACT_LICENSE_FAIL id=$([string]$row.id)" }
}
foreach($marker in @(
  "'Data/WarehouseQuaterniusHeroCandidateBatchV1.json'",
  "'Data/P1C01OpenGameArtHeroCandidateBatchV1.json'",
  "'Data/P1C01OpenGameArtRpgHeroCandidateBatchV1.json'",
  "'Data/P1C01KayKitAdventurersHeroCandidateBatchV1.json'",
  "'Data/P1C01KayKitAdventurersRogueHoodedHeroCandidateBatchV1.json'",
  "'Data/P1C01KenneyBlockyHeroCandidateBatchV1.json'",
  "- name: Stage P1C01 hero candidate provider batch",
  "- name: Stage OpenGameArt Quaternius character candidate",
  "- name: Stage alternate OpenGameArt RPG hero candidate",
  "- name: Stage KayKit Adventurers alternate hero candidate",
  "- name: Stage KayKit RogueHooded alternate hero candidate",
  "- name: Stage Kenney Blocky alternate hero candidate",
  "- name: Build exact-head P1C01 Frodo Gandalf candidate report"
)){
  if(-not $workflow.Contains($marker)){ throw "P1C01_HERO_PROVIDER_CONTRACT_WORKFLOW_MARKER_MISSING marker=$marker" }
}
$qtnIndex=$workflow.IndexOf("- name: Stage P1C01 hero candidate provider batch",[StringComparison]::Ordinal)
$ogaIndex=$workflow.IndexOf("- name: Stage OpenGameArt Quaternius character candidate",[StringComparison]::Ordinal)
$ogaRpgIndex=$workflow.IndexOf("- name: Stage alternate OpenGameArt RPG hero candidate",[StringComparison]::Ordinal)
$kayIndex=$workflow.IndexOf("- name: Stage KayKit Adventurers alternate hero candidate",[StringComparison]::Ordinal)
$kayHoodedIndex=$workflow.IndexOf("- name: Stage KayKit RogueHooded alternate hero candidate",[StringComparison]::Ordinal)
$kenneyIndex=$workflow.IndexOf("- name: Stage Kenney Blocky alternate hero candidate",[StringComparison]::Ordinal)
$reportIndex=$workflow.IndexOf("- name: Build exact-head P1C01 Frodo Gandalf candidate report",[StringComparison]::Ordinal)
if($qtnIndex -lt 0 -or $ogaIndex -le $qtnIndex -or $ogaRpgIndex -le $ogaIndex -or $kayIndex -le $ogaRpgIndex -or $kayHoodedIndex -le $kayIndex -or $kenneyIndex -le $kayHoodedIndex -or $reportIndex -le $kenneyIndex){ throw "P1C01_HERO_PROVIDER_CONTRACT_ORDER_FAIL qtn=$qtnIndex oga=$ogaIndex ogaRpg=$ogaRpgIndex kay=$kayIndex kayHooded=$kayHoodedIndex kenney=$kenneyIndex report=$reportIndex" }

Write-Host "P1C01_HERO_PROVIDER_CONTRACT_TEST_PASS packs=$($required.Count) directFallback=true precedes_candidate_report=true"
