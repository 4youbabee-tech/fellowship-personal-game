param(
  [string]$ManifestPath = "Data/P1C01ChapterClosureMegaPackV2.json",
  [string]$WarehouseRoot = "C:\actions-runner\_warehouse\ShireJourney"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
if(-not [IO.Path]::IsPathRooted($ManifestPath)){ $ManifestPath = Join-Path $ProjectRoot $ManifestPath }
if(-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)){ throw "CLOSURE_PREFLIGHT_MANIFEST_MISSING path=$ManifestPath" }
if(-not (Test-Path -LiteralPath $WarehouseRoot -PathType Container)){ throw "CLOSURE_PREFLIGHT_WAREHOUSE_MISSING root=$WarehouseRoot" }

$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
if([string]$manifest.status -ne "RUNNER_EXECUTION_READY"){ throw "CLOSURE_PREFLIGHT_STATUS_INVALID status=$($manifest.status)" }

$requiredFiles=@(
  "Scripts\run_p1c01_chapter_closure_pack_v2.ps1",
  "Scripts\stage_polyhaven_warehouse.ps1",
  "Scripts\stage_ambientcg_warehouse.ps1",
  "Scripts\stage_quaternius_warehouse.ps1",
  "Scripts\stage_kenney_warehouse.ps1",
  "Scripts\stage_kaykit_github_warehouse.ps1",
  "Scripts\stage_opengameart_audio.ps1",
  "Scripts\audit_warehouse_inventory.ps1",
  "Scripts\run_warehouse_saturation_train.ps1",
  "Scripts\run_warehouse_critical_gap_preparation.ps1",
  "Scripts\run_warehouse_provider_resolution.ps1",
  "Scripts\run_warehouse_p1c01_mega_promotion.ps1",
  "Scripts\export_p1c01_material_source_branch.ps1",
  "Scripts\prepare_p1c01_character_rig_intake.ps1",
  "Data\WarehouseP1C01ClosurePromotionTrainV2.json",
  "Data\P1C01MaterialImportWaveV2.json",
  "Data\P1C01CharacterRigAnimationPrepV1.json"
)
foreach($relative in $requiredFiles){
  $absolute=Join-Path $ProjectRoot $relative
  if(-not (Test-Path -LiteralPath $absolute -PathType Leaf)){ throw "CLOSURE_PREFLIGHT_REQUIRED_FILE_MISSING path=$relative" }
}

$parseTargets=@($requiredFiles | Where-Object { $_.EndsWith(".ps1",[StringComparison]::OrdinalIgnoreCase) })
foreach($relative in $parseTargets){
  $absolute=Join-Path $ProjectRoot $relative
  $tokens=$null
  $errors=$null
  [void][System.Management.Automation.Language.Parser]::ParseFile($absolute,[ref]$tokens,[ref]$errors)
  if(@($errors).Count -gt 0){
    $first=@($errors)[0]
    throw "CLOSURE_PREFLIGHT_POWERSHELL_PARSE_FAIL path=$relative line=$($first.Extent.StartLineNumber) message=$($first.Message)"
  }
}

foreach($car in @($manifest.cars)){
  if($null -ne $car.PSObject.Properties["manifest"]){
    $child=[string]$car.manifest
    if(-not [IO.Path]::IsPathRooted($child)){ $child=Join-Path $ProjectRoot $child }
    if(-not (Test-Path -LiteralPath $child -PathType Leaf)){ throw "CLOSURE_PREFLIGHT_CHILD_MANIFEST_MISSING car=$($car.id) path=$child" }
    try { [void](Get-Content -LiteralPath $child -Raw | ConvertFrom-Json) }
    catch { throw "CLOSURE_PREFLIGHT_CHILD_MANIFEST_INVALID car=$($car.id) path=$child detail=$($_.Exception.Message)" }
  }
}

$warehouseItem=Get-Item -LiteralPath $WarehouseRoot
$drive=[IO.DriveInfo]::new($warehouseItem.PSDrive.Root)
$reserve=[int64]$manifest.storage_policy.minimum_free_disk_reserve_bytes
$free=[int64]$drive.AvailableFreeSpace
if($free -lt $reserve){ throw "CLOSURE_PREFLIGHT_DISK_RESERVE_FAIL freeBytes=$free reserveBytes=$reserve" }

Write-Host ("P1C01_CLOSURE_PREFLIGHT_PASS cars="+@($manifest.cars).Count+" parsedScripts="+$parseTargets.Count+" freeBytes="+$free+" reserveBytes="+$reserve)
exit 0
