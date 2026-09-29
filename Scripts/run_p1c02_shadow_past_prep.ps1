param(
  [string]$ManifestPath = "Data/P1C02ShadowPastChapterPackV1.json",
  [string]$WarehouseRoot = "D:\actions-runner\_warehouse\ShireJourney"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
if(-not [IO.Path]::IsPathRooted($ManifestPath)){ $ManifestPath = Join-Path $ProjectRoot $ManifestPath }
if(-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)){ throw "P1C02 prep manifest missing: $ManifestPath" }
if(-not (Test-Path -LiteralPath $WarehouseRoot -PathType Container)){ throw "P1C02 warehouse missing: $WarehouseRoot" }

$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
Write-Host ("P1C02_SHADOW_PAST_PREP_BEGIN pack=" + [string]$manifest.pack_id)

$cars = @(
  @{ id="SATURATION"; script="run_warehouse_saturation_train.ps1"; manifest="Data/WarehouseSaturationTrainV1.json" },
  @{ id="CRITICAL_GAP"; script="run_warehouse_critical_gap_preparation.ps1"; manifest="Data/WarehouseCriticalGapPreparationTrainV2.json" },
  @{ id="PROVIDER_RESOLUTION"; script="run_warehouse_provider_resolution.ps1"; manifest="Data/WarehouseProviderResolutionTrainV3.json" }
)

$passed = 0
$quarantined = 0
foreach($car in $cars){
  $child = Join-Path $ProjectRoot $car.manifest
  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot $car.script) -ManifestPath $child
  if($LASTEXITCODE -eq 0){
    $passed++
    Write-Host ("P1C02_PREP_CAR_PASS id=" + $car.id)
  } else {
    $quarantined++
    Write-Host ("P1C02_PREP_CAR_QUARANTINED id=" + $car.id + " exit=" + $LASTEXITCODE)
  }
}

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "audit_warehouse_inventory.ps1")
if($LASTEXITCODE -ne 0){ throw "P1C02 final warehouse audit failed" }

Write-Host ("P1C02_SHADOW_PAST_PREP_PASS passed=" + $passed + " quarantined=" + $quarantined + " runtimeIntegration=not-started")
exit 0
