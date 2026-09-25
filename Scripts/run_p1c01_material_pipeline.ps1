param(
  [switch]$RefreshWarehouse,
  [switch]$RunUnrealImport
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path $PSScriptRoot -Parent
Push-Location $ProjectRoot
try {
  Write-Host "P1C01_MASSIVE_PREP_BEGIN"

  $polyArgs = @("-NoProfile","-ExecutionPolicy","Bypass","-File",(Join-Path $PSScriptRoot "stage_polyhaven_warehouse.ps1"))
  if($RefreshWarehouse){ $polyArgs += "-Refresh" }
  & powershell.exe @polyArgs
  if($LASTEXITCODE -ne 0){ throw "Poly Haven warehouse stage failed: $LASTEXITCODE" }

  $ambientArgs = @("-NoProfile","-ExecutionPolicy","Bypass","-File",(Join-Path $PSScriptRoot "stage_ambientcg_warehouse.ps1"))
  if($RefreshWarehouse){ $ambientArgs += "-Refresh" }
  & powershell.exe @ambientArgs
  if($LASTEXITCODE -ne 0){ throw "ambientCG warehouse stage failed: $LASTEXITCODE" }

  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "audit_warehouse_inventory.ps1")
  if($LASTEXITCODE -ne 0){ throw "Warehouse inventory audit failed: $LASTEXITCODE" }

  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "prepare_p1c01_material_intake.ps1")
  if($LASTEXITCODE -ne 0){ throw "P1C01 material intake preparation failed: $LASTEXITCODE" }

  if($RunUnrealImport){
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "promote_p1c01_material_intake.ps1") -RunUnrealImport
    if($LASTEXITCODE -ne 0){ throw "P1C01 material UE import failed: $LASTEXITCODE" }
  } else {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "promote_p1c01_material_intake.ps1")
    if($LASTEXITCODE -ne 0){ throw "P1C01 material overlay preparation failed: $LASTEXITCODE" }
  }

  Write-Host ("P1C01_MASSIVE_PREP_PASS unrealImport=" + [bool]$RunUnrealImport)
}
finally {
  Pop-Location
}
