$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

$root=Split-Path -Parent $PSScriptRoot
$planPath=Join-Path $root "Data\P1C01VisibleWorldProxyReplacementV1.json"
$packPath=Join-Path $root "Data\P1C01MegaChapterPackV1.json"
$eastFieldsPath=Join-Path $root "Data\P1C01EastFieldsRowReplacementV1.json"
$builderPath=Join-Path $root "Source\ShireJourney\Private\World\ShirePrototypeWorldBuilder.cpp"

foreach($path in @($planPath,$packPath,$eastFieldsPath,$builderPath)){
  if(-not (Test-Path -LiteralPath $path -PathType Leaf)){
    throw "P1C01_VISIBLE_WORLD_CONTRACT_FILE_MISSING path=$path"
  }
}

$plan=Get-Content -LiteralPath $planPath -Raw | ConvertFrom-Json
$pack=Get-Content -LiteralPath $packPath -Raw | ConvertFrom-Json
$eastFields=Get-Content -LiteralPath $eastFieldsPath -Raw | ConvertFrom-Json
$builder=Get-Content -LiteralPath $builderPath -Raw

if([string]$plan.plan_id -ne "P1C01_VISIBLE_WORLD_PROXY_REPLACEMENT_V1"){
  throw "P1C01_VISIBLE_WORLD_PLAN_ID_FAIL"
}
if([bool]$plan.runtime_integration_allowed){
  throw "P1C01_VISIBLE_WORLD_RUNTIME_MUST_REMAIN_FALSE"
}
if([int]$pack.schema_version -lt 2){
  throw "P1C01_VISIBLE_WORLD_PACK_SCHEMA_FAIL"
}

$requiredCells=@("BAG_END_HERO_RING","HOBBITON_VILLAGE","SHIRE_ROAD_CORRIDOR","BUCKLEBURY_FERRY")
$cells=@($plan.replacement_cells | ForEach-Object { [string]$_.cell })
foreach($cell in $requiredCells){
  if($cells -notcontains $cell){
    throw "P1C01_VISIBLE_WORLD_CELL_MISSING cell=$cell"
  }
}

foreach($marker in @(
  "/Engine/BasicShapes/Cube.Cube",
  "/Engine/BasicShapes/Sphere.Sphere",
  "/Engine/BasicShapes/Cylinder.Cylinder",
  "/Engine/BasicShapes/Cone.Cone",
  "SM_ShHobbitFacade",
  "SM_ShCottageHouse",
  "SM_ShRoadBlock",
  "SM_CommonRiverBank",
  "M_ProductionWater"
)){
  if(-not $builder.Contains($marker)){
    throw "P1C01_VISIBLE_WORLD_BUILDER_MARKER_MISSING marker=$marker"
  }
}

if([string]$plan.target_profile.animated_asset_format -ne "FBX"){
  throw "P1C01_VISIBLE_WORLD_ANIMATED_FORMAT_FAIL"
}
$formats=@($plan.target_profile.texture_formats | ForEach-Object { [string]$_ })
if($formats -contains "BMP" -or $formats -notcontains "PNG" -or $formats -notcontains "TGA"){
  throw "P1C01_VISIBLE_WORLD_TEXTURE_POLICY_FAIL"
}
if([string]$plan.target_profile.loading -notmatch "FStreamableManager"){
  throw "P1C01_VISIBLE_WORLD_ASYNC_LOADING_POLICY_FAIL"
}
if([string]$plan.target_profile.repeated_detail -notmatch "HISM"){
  throw "P1C01_VISIBLE_WORLD_INSTANCING_POLICY_FAIL"
}

if([string]$eastFields.plan_id -ne "P1C01_EAST_FIELDS_ROW_REPLACEMENT_V1"){
  throw "P1C01_EAST_FIELDS_PLAN_ID_FAIL"
}
if(-not [bool]$eastFields.runtime_integration_allowed){
  throw "P1C01_EAST_FIELDS_RUNTIME_AUTHORIZATION_MISSING"
}
if([int]$eastFields.proposed_runtime_contract.max_instances -ne 96){
  throw "P1C01_EAST_FIELDS_INSTANCE_BUDGET_FAIL"
}
if([int]$eastFields.proposed_runtime_contract.cull_start_cm -ne 900 -or [int]$eastFields.proposed_runtime_contract.cull_end_cm -ne 6500){
  throw "P1C01_EAST_FIELDS_CULL_BUDGET_FAIL"
}
foreach($marker in @(
  "EastFieldRowInstances",
  "SetCullDistances(900, 6500)",
  "EastFieldRowCount * InstancesPerRow == 96",
  "AddInstanceWorldSpace",
  "if (EastFieldRowInstances && ProductionGrassClumpMesh)",
  "UStaticMesh* EntryShrubMesh = ProductionShrubMesh ? ProductionShrubMesh : SphereMesh",
  "Keep the primitive spheres only as a deterministic no-asset fallback"
)){
  if(-not $builder.Contains($marker)){
    throw "P1C01_EAST_FIELDS_BUILDER_MARKER_MISSING marker=$marker"
  }
}

Write-Host ("P1C01_VISIBLE_WORLD_CONTRACT_PASS cells="+$cells.Count+" eastFieldsHism=true eastFieldsMax=96 runtime=true")


$bagEndTrimPacketPath = Join-Path $RepoRoot "Data\P1C01BagEndHeroTrimSourceProbeV1.json"
if(-not (Test-Path $bagEndTrimPacketPath)){
  throw "P1C01_BAG_END_HERO_TRIM_PACKET_MISSING"
}
$bagEndTrim = Get-Content $bagEndTrimPacketPath -Raw | ConvertFrom-Json
if($bagEndTrim.runtime_integration_allowed -ne $false){
  throw "P1C01_BAG_END_HERO_TRIM_RUNTIME_MUST_REMAIN_DISABLED"
}
if($bagEndTrim.status -ne "SOURCE_PREPRODUCTION_ACTIVE"){
  throw "P1C01_BAG_END_HERO_TRIM_STATUS_INVALID"
}
if(@($bagEndTrim.candidate_families).Count -lt 2){
  throw "P1C01_BAG_END_HERO_TRIM_CANDIDATE_FAMILY_COUNT_LOW"
}
if(-not (@($bagEndTrim.required_static_gates) -contains "FBX only for selected 3D hero-support asset")){
  throw "P1C01_BAG_END_HERO_TRIM_FBX_GATE_MISSING"
}
if(-not (@($bagEndTrim.required_static_gates) -contains "no BMP texture payload; PNG/TGA only, channel-packed where applicable")){
  throw "P1C01_BAG_END_HERO_TRIM_TEXTURE_GATE_MISSING"
}
Write-Host "P1C01_BAG_END_HERO_TRIM_SOURCE_PROBE_PASS candidates=$(@($bagEndTrim.candidate_families).Count) runtime=false"
