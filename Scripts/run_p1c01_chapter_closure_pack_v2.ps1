param(
  [string]$ManifestPath = "Data/P1C01ChapterClosureMegaPackV2.json",
  [string]$WarehouseRoot = "D:\actions-runner\_warehouse\ShireJourney",
  [string]$ReportRoot = "",
  [switch]$AssetFirst
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot=Split-Path $PSScriptRoot -Parent
if(-not [IO.Path]::IsPathRooted($ManifestPath)){ $ManifestPath=Join-Path $ProjectRoot $ManifestPath }
if(-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)){ throw "P1C01 closure pack manifest missing: $ManifestPath" }
if(-not (Test-Path -LiteralPath $WarehouseRoot -PathType Container)){ throw "Warehouse root missing: $WarehouseRoot" }
$manifest=Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
if([string]::IsNullOrWhiteSpace($ReportRoot)){ $ReportRoot=Join-Path $WarehouseRoot "_p1c01_chapter_closure_pack_v2" }
New-Item -ItemType Directory -Path $ReportRoot -Force | Out-Null
$results=@()
$hardFailure=$false

function Resolve-ChildManifest([string]$Path){
  if([IO.Path]::IsPathRooted($Path)){ return $Path }
  return Join-Path $ProjectRoot $Path
}
function Add-CarResult {
  param([string]$Id,[string]$State,[int]$ExitCode,[string]$Detail)
  $script:results += [ordered]@{id=$Id;state=$State;exit_code=$ExitCode;detail=$Detail;completed_at_utc=[DateTime]::UtcNow.ToString("o")}
}
function Invoke-ChildPowerShell {
  param([string]$ScriptPath,[object[]]$ChildArgs=@())
  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptPath @ChildArgs
  $code=[int]$LASTEXITCODE
  if($code -ne 0){
    $ex=New-Object System.Exception -ArgumentList ("child PowerShell failed exit="+$code+" script="+$ScriptPath)
    $ex.Data["ExitCode"]=$code
    throw $ex
  }
}
function Invoke-Car {
  param([object]$Car,[scriptblock]$Body)
  $id=[string]$Car.id
  if(-not [bool]$Car.enabled){ Add-CarResult $id "SKIPPED_DISABLED" 0 "disabled by manifest"; return }
  Write-Host ("P1C01_CLOSURE_PACK_CAR_BEGIN id="+$id)
  try{
    & $Body
    Add-CarResult $id "PASS" 0 "completed"
    Write-Host ("P1C01_CLOSURE_PACK_CAR_PASS id="+$id)
    return
  }catch{
    $failureCode=1
    if($null -ne $_.Exception.Data -and $_.Exception.Data.Contains("ExitCode")){
      $failureCode=[int]$_.Exception.Data["ExitCode"]
    }
    if(([string]$Car.criticality) -eq "INFRASTRUCTURE"){
      Add-CarResult $id "HARD_FAILURE" $failureCode $_.Exception.Message
      $script:hardFailure=$true
      Write-Host ("P1C01_CLOSURE_PACK_CAR_HARD_FAIL id="+$id+" exit="+$failureCode+" detail="+$_.Exception.Message)
    }else{
      Add-CarResult $id "QUARANTINED_CONTINUE" $failureCode $_.Exception.Message
      Write-Host ("P1C01_CLOSURE_PACK_CAR_QUARANTINED id="+$id+" exit="+$failureCode+" detail="+$_.Exception.Message)
    }
  }
}
function Invoke-ManifestScript {
  param([string]$ScriptName,[string]$ChildManifest)
  $resolved=Resolve-ChildManifest $ChildManifest
  Invoke-ChildPowerShell -ScriptPath (Join-Path $PSScriptRoot $ScriptName) -ChildArgs @("-ManifestPath",$resolved)
}

foreach($car in @($manifest.cars | Sort-Object order)){
  # DEC-109: New asset acquisition/promotions stay active; global admin scans
  # and old coverage reports wait for the definitive full closeout.
  if($AssetFirst -and ([string]$car.id) -in @("INVENTORY_AUDIT","SATURATION_REPORT","CRITICAL_GAP_PREP","PROVIDER_RESOLUTION","FINAL_INVENTORY_AUDIT")){
    Add-CarResult ([string]$car.id) "DEFERRED_TO_CLOSEOUT" 0 "asset-first only; retain per-source SHA256 and storage QC"
    Write-Host ("P1C01_ASSET_FIRST_ADMIN_DEFER id="+[string]$car.id)
    continue
  }
  switch([string]$car.id){
    "PREFLIGHT_STORAGE" {
      Invoke-Car $car {
        $warehouseItem=Get-Item -LiteralPath $WarehouseRoot
        $drive=[IO.DriveInfo]::new($warehouseItem.PSDrive.Root)
        $reserve=[int64]$manifest.storage_policy.minimum_free_disk_reserve_bytes
        $free=[int64]$drive.AvailableFreeSpace
        $existing=@()
        $existingBytes=[int64]0
        if(-not $AssetFirst){
          $existing=@(Get-ChildItem -LiteralPath $WarehouseRoot -Recurse -File -ErrorAction SilentlyContinue)
          $sum=($existing | Measure-Object -Property Length -Sum).Sum
          $existingBytes=if($null -eq $sum){[int64]0}else{[int64]$sum}
        }
        if($free -lt $reserve){ throw "warehouse free-space reserve not met: free=$free reserve=$reserve" }
        if($AssetFirst){
          Write-Host ("P1C01_CLOSURE_PACK_STORAGE_PASS existingFiles=deferred existingBytes=deferred freeBytes="+$free+" reserveBytes="+$reserve)
        }else{
          Write-Host ("P1C01_CLOSURE_PACK_STORAGE_PASS existingFiles="+$existing.Count+" existingBytes="+$existingBytes+" freeBytes="+$free+" reserveBytes="+$reserve)
        }
      }
      if($hardFailure){ break }
    }
    "STAGE_POLYHAVEN" { Invoke-Car $car { Invoke-ManifestScript "stage_polyhaven_warehouse.ps1" ([string]$car.manifest) } }
    "STAGE_AMBIENTCG" { Invoke-Car $car { Invoke-ManifestScript "stage_ambientcg_warehouse.ps1" ([string]$car.manifest) } }
    "STAGE_QUATERNIUS" { Invoke-Car $car { Invoke-ManifestScript "stage_quaternius_warehouse.ps1" ([string]$car.manifest) } }
    "STAGE_KENNEY" { Invoke-Car $car { Invoke-ManifestScript "stage_kenney_warehouse.ps1" ([string]$car.manifest) } }
    "STAGE_KAYKIT" { Invoke-Car $car { Invoke-ManifestScript "stage_kaykit_github_warehouse.ps1" ([string]$car.manifest) } }
    "STAGE_AUDIO" { Invoke-Car $car { Invoke-ManifestScript "stage_opengameart_audio.ps1" ([string]$car.manifest) } }
    "INVENTORY_AUDIT" {
      Invoke-Car $car { Invoke-ChildPowerShell -ScriptPath (Join-Path $PSScriptRoot "audit_warehouse_inventory.ps1") }
      if($hardFailure){ break }
    }
    "SATURATION_REPORT" { Invoke-Car $car { Invoke-ManifestScript "run_warehouse_saturation_train.ps1" ([string]$car.manifest) } }
    "CRITICAL_GAP_PREP" { Invoke-Car $car { Invoke-ManifestScript "run_warehouse_critical_gap_preparation.ps1" ([string]$car.manifest) } }
    "PROVIDER_RESOLUTION" { Invoke-Car $car { Invoke-ManifestScript "run_warehouse_provider_resolution.ps1" ([string]$car.manifest) } }
    "MEGA_PROMOTION" {
      Invoke-Car $car {
        $resolved=Resolve-ChildManifest ([string]$car.manifest)
        Invoke-ChildPowerShell -ScriptPath (Join-Path $PSScriptRoot "run_warehouse_p1c01_mega_promotion.ps1") -ChildArgs @("-ManifestPath",$resolved,"-WarehouseRoot",$WarehouseRoot)
      }
    }
    "MATERIAL_SOURCE_EXPORT" {
      Invoke-Car $car {
        $resolved=Resolve-ChildManifest ([string]$car.manifest)
        $budget=$car.export_budget
        Invoke-ChildPowerShell -ScriptPath (Join-Path $PSScriptRoot "export_p1c01_material_source_branch.ps1") -ChildArgs @("-ManifestPath",$resolved,"-WarehouseRoot",$WarehouseRoot,"-GeneratedBranch",([string]$car.generated_branch),"-MaxSingleSourceBytes",([int64]$budget.max_single_source_bytes),"-MaxBatchSourceBytes",([int64]$budget.max_batch_source_bytes),"-MinimumExportedMaterials",([int]$budget.minimum_exported_materials))
      }
    }
    "CHARACTER_INTAKE" {
      Invoke-Car $car {
        $resolved=Resolve-ChildManifest ([string]$car.manifest)
        $out=Join-Path $WarehouseRoot "_p1c01_character_intake"
        Invoke-ChildPowerShell -ScriptPath (Join-Path $PSScriptRoot "prepare_p1c01_character_rig_intake.ps1") -ChildArgs @("-ManifestPath",$resolved,"-WarehouseRoot",$WarehouseRoot,"-OutputRoot",$out)
      }
    }
    "FINAL_INVENTORY_AUDIT" {
      Invoke-Car $car { & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "audit_warehouse_inventory.ps1") }
      if($hardFailure){ break }
    }
    default { Add-CarResult ([string]$car.id) "SKIPPED_UNKNOWN_CAR" 0 "unknown car id" }
  }
  if($hardFailure){ Write-Host ("P1C01_CLOSURE_PACK_ABORT_AFTER_INFRA_FAILURE car="+[string]$car.id); break }
}

$passCount=@($results | Where-Object {$_.state -eq "PASS"}).Count
$quarantineCount=@($results | Where-Object {$_.state -eq "QUARANTINED_CONTINUE"}).Count
$hardCount=@($results | Where-Object {$_.state -eq "HARD_FAILURE"}).Count
$files=@()
$bytes=[int64]0
if(-not $AssetFirst){
  $files=@(Get-ChildItem -LiteralPath $WarehouseRoot -Recurse -File -ErrorAction SilentlyContinue)
  $sum=($files | Measure-Object -Property Length -Sum).Sum
  $bytes=if($null -eq $sum){[int64]0}else{[int64]$sum}
}else{
  Write-Host "P1C01_ASSET_FIRST_NO_REDUNDANT_GLOBAL_WAREHOUSE_SCAN"
}
$report=[ordered]@{
  schema_version=2
  pack_id=[string]$manifest.pack_id
  generated_at_utc=[DateTime]::UtcNow.ToString("o")
  warehouse_root=$WarehouseRoot
  warehouse_files=$(if($AssetFirst){$null}else{$files.Count})
  warehouse_bytes=$(if($AssetFirst){$null}else{$bytes})
  car_count=$results.Count
  passed=$passCount
  quarantined=$quarantineCount
  hard_failures=$hardCount
  cars=$results
  execution_mode=$(if($AssetFirst){"ASSET_FIRST_NEW_ONLY"}else{"FULL_CLOSEOUT"})
  deferred_admin_count=@($results | Where-Object {$_.state -eq "DEFERRED_TO_CLOSEOUT"}).Count
  warehouse_global_inventory_scanned=(-not $AssetFirst)
  execution_rule="Large chapter source cars continue independently; only infrastructure failure stops the pack."
  acceptance_boundary="Source/acquisition/preparation only; no UE import/integration/PIE/device/visual/performance acceptance."
}
$reportedFiles=if($AssetFirst){"deferred"}else{[string]$files.Count}
$reportedBytes=if($AssetFirst){"deferred"}else{[string]$bytes}
$reportPath=Join-Path $ReportRoot "p1c01_chapter_closure_pack_v2_latest.json"
$report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $reportPath -Encoding UTF8
if($hardFailure){
  Write-Host ("P1C01_CHAPTER_CLOSURE_PACK_V2_FAIL passed="+$passCount+" quarantined="+$quarantineCount+" hard="+$hardCount+" files="+$reportedFiles+" bytes="+$reportedBytes+" report="+$reportPath)
  exit 41
}
Write-Host ("P1C01_CHAPTER_CLOSURE_PACK_V2_PASS passed="+$passCount+" quarantined="+$quarantineCount+" hard=0 files="+$reportedFiles+" bytes="+$reportedBytes+" report="+$reportPath)
exit 0
