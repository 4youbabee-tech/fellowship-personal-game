param(
  [string]$ManifestPath = "Data/P1C01MegaChapterPackV1.json",
  [string]$WarehouseRoot = "C:\\actions-runner\\_warehouse\\ShireJourney",
  [string]$ReportRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
if(-not [IO.Path]::IsPathRooted($ManifestPath)){
  $ManifestPath = Join-Path $ProjectRoot $ManifestPath
}
if(-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)){
  throw "P1C01 chapter pack manifest missing: $ManifestPath"
}
if(-not (Test-Path -LiteralPath $WarehouseRoot -PathType Container)){
  throw "Warehouse root missing: $WarehouseRoot"
}

$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
if([string]::IsNullOrWhiteSpace($ReportRoot)){
  $ReportRoot = Join-Path $WarehouseRoot "_p1c01_chapter_pack_v1"
}
New-Item -ItemType Directory -Path $ReportRoot -Force | Out-Null

$results = @()
$hardFailure = $false

function Add-CarResult {
  param(
    [string]$Id,
    [string]$State,
    [int]$ExitCode,
    [string]$Detail
  )
  $script:results += [ordered]@{
    id = $Id
    state = $State
    exit_code = $ExitCode
    detail = $Detail
    completed_at_utc = [DateTime]::UtcNow.ToString("o")
  }
}

function Invoke-Car {
  param(
    [object]$Car,
    [scriptblock]$Body
  )

  $id = [string]$Car.id
  if(-not [bool]$Car.enabled){
    Add-CarResult $id "SKIPPED_DISABLED" 0 "disabled by manifest"
    return
  }

  Write-Host ("P1C01_CHAPTER_PACK_CAR_BEGIN id=" + $id)
  try {
    & $Body
    $code = $LASTEXITCODE
    if($null -eq $code){ $code = 0 }

    if($code -eq 0){
      Add-CarResult $id "PASS" 0 "completed"
      Write-Host ("P1C01_CHAPTER_PACK_CAR_PASS id=" + $id)
      return
    }

    $criticality = [string]$Car.criticality
    if($criticality -eq "INFRASTRUCTURE"){
      Add-CarResult $id "HARD_FAILURE" $code ("critical infrastructure car exit=" + $code)
      $script:hardFailure = $true
      Write-Host ("P1C01_CHAPTER_PACK_CAR_HARD_FAIL id=" + $id + " exit=" + $code)
    } else {
      Add-CarResult $id "QUARANTINED_CONTINUE" $code ("asset/source blocker isolated; exit=" + $code)
      Write-Host ("P1C01_CHAPTER_PACK_CAR_QUARANTINED id=" + $id + " exit=" + $code)
    }
  } catch {
    $criticality = [string]$Car.criticality
    if($criticality -eq "INFRASTRUCTURE"){
      Add-CarResult $id "HARD_FAILURE" 1 $_.Exception.Message
      $script:hardFailure = $true
      Write-Host ("P1C01_CHAPTER_PACK_CAR_HARD_FAIL id=" + $id + " detail=" + $_.Exception.Message)
    } else {
      Add-CarResult $id "QUARANTINED_CONTINUE" 1 $_.Exception.Message
      Write-Host ("P1C01_CHAPTER_PACK_CAR_QUARANTINED id=" + $id + " detail=" + $_.Exception.Message)
    }
  }
}

foreach($car in @($manifest.cars | Sort-Object order)){
  switch([string]$car.id){
    "INVENTORY_AUDIT" {
      Invoke-Car $car {
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "audit_warehouse_inventory.ps1")
      }
      if($hardFailure){ break }
    }
    "MEGA_PROMOTION" {
      Invoke-Car $car {
        $childManifest = [string]$car.manifest
        if(-not [IO.Path]::IsPathRooted($childManifest)){ $childManifest = Join-Path $ProjectRoot $childManifest }
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "run_warehouse_p1c01_mega_promotion.ps1") -ManifestPath $childManifest -WarehouseRoot $WarehouseRoot
      }
    }
    "MATERIAL_SOURCE_EXPORT" {
      Invoke-Car $car {
        $childManifest = [string]$car.manifest
        if(-not [IO.Path]::IsPathRooted($childManifest)){ $childManifest = Join-Path $ProjectRoot $childManifest }
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "export_p1c01_material_source_branch.ps1") -ManifestPath $childManifest -WarehouseRoot $WarehouseRoot -GeneratedBranch ([string]$car.generated_branch)
      }
    }
    "CHARACTER_INTAKE" {
      Invoke-Car $car {
        $childManifest = [string]$car.manifest
        if(-not [IO.Path]::IsPathRooted($childManifest)){ $childManifest = Join-Path $ProjectRoot $childManifest }
        $outputRoot = Join-Path $WarehouseRoot "_p1c01_character_intake"
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "prepare_p1c01_character_rig_intake.ps1") -ManifestPath $childManifest -OutputRoot $outputRoot
      }
    }
    default {
      Add-CarResult ([string]$car.id) "SKIPPED_UNKNOWN_CAR" 0 "unknown car id"
    }
  }
}

$passCount = @($results | Where-Object { $_.state -eq "PASS" }).Count
$quarantineCount = @($results | Where-Object { $_.state -eq "QUARANTINED_CONTINUE" }).Count
$hardCount = @($results | Where-Object { $_.state -eq "HARD_FAILURE" }).Count

$report = [ordered]@{
  schema_version = 1
  pack_id = [string]$manifest.pack_id
  generated_at_utc = [DateTime]::UtcNow.ToString("o")
  warehouse_root = $WarehouseRoot
  car_count = $results.Count
  passed = $passCount
  quarantined = $quarantineCount
  hard_failures = $hardCount
  cars = $results
  execution_rule = "Asset/source blockers quarantine the affected car and later cars continue. Infrastructure failure stops the pack."
  acceptance_boundary = "Car outputs only; no UE import/integration/PIE/device/visual/performance acceptance."
}
$reportPath = Join-Path $ReportRoot "p1c01_mega_chapter_pack_latest.json"
$report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $reportPath -Encoding UTF8

if($hardFailure){
  Write-Host ("P1C01_MEGA_CHAPTER_PACK_FAIL passed=" + $passCount + " quarantined=" + $quarantineCount + " hard=" + $hardCount + " report=" + $reportPath)
  exit 31
}

Write-Host ("P1C01_MEGA_CHAPTER_PACK_PASS passed=" + $passCount + " quarantined=" + $quarantineCount + " hard=0 report=" + $reportPath)
exit 0
