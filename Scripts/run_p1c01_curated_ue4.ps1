param(
  [Parameter(Mandatory=$true)][string]$ExpectedSha,
  [string]$Workspace = '',
  [string]$WarehouseRoot = 'D:\actions-runner\_warehouse\ShireJourney'
)
# Owner-authorized exact-head automatic UE4 curated import. Single existing Windows writer.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if([string]::IsNullOrWhiteSpace($Workspace)) { $Workspace = Split-Path $PSScriptRoot -Parent }
$Workspace = (Resolve-Path -LiteralPath $Workspace).Path
$head = (& git -C $Workspace rev-parse HEAD).Trim()
if($LASTEXITCODE -ne 0 -or $head -ne $ExpectedSha) { throw "P1C01_CURATED_EXACT_HEAD_REQUIRED expected=$ExpectedSha actual=$head" }
if(-not (Test-Path -LiteralPath $WarehouseRoot -PathType Container)) { throw 'P1C01_CURATED_WAREHOUSE_MISSING' }
$drive = [IO.DriveInfo]::new(([IO.Path]::GetPathRoot($WarehouseRoot)))
if($drive.AvailableFreeSpace -lt 6GB) { throw 'P1C01_CURATED_DISK_RESERVE_BELOW_6GIB' }
$archive = Join-Path $WarehouseRoot '_drive_temp_staging\curated_p1c01\SHIRE_P1C01_CURATED_SOURCE_20261012.zip'
if(-not (Test-Path -LiteralPath $archive -PathType Leaf)) { throw 'P1C01_CURATED_WAREHOUSE_ARCHIVE_MISSING' }
if(Get-Process -Name 'UE4Editor','UE4Editor-Cmd' -ErrorAction SilentlyContinue) { throw 'P1C01_CURATED_EDITOR_ALREADY_RUNNING' }
$python = (Get-Command python.exe -ErrorAction SilentlyContinue)
$py = (Get-Command py.exe -ErrorAction SilentlyContinue)
if($python -and $python.Source -notlike '*WindowsApps*') { $exe=$python.Source; $pyArgs=@() }
elseif($py) { $exe=$py.Source; $pyArgs=@('-3.12') }
else { throw 'P1C01_CURATED_PYTHON_MISSING' }
$qc = Join-Path $Workspace 'Saved\P1C01CuratedStage\warehouse_qc.json'
New-Item -Force -ItemType Directory -Path (Split-Path $qc -Parent) | Out-Null
& $exe @pyArgs (Join-Path $Workspace 'Scripts\verify_drive_warehouse_receipts.py') --warehouse-root $WarehouseRoot --out $qc
if($LASTEXITCODE -ne 0) { throw 'P1C01_CURATED_TEN_ZIP_PHYSICAL_QC_FAILED' }
$qcReport = Get-Content -LiteralPath $qc -Raw | ConvertFrom-Json
if($qcReport.state -ne 'SOURCE_QC_PASS_IMPORT_BLOCKED' -or $qcReport.verified_archive_count -ne 10) { throw 'P1C01_CURATED_TEN_ZIP_QC_NOT_GREEN' }
& $exe @pyArgs (Join-Path $Workspace 'Scripts\stage_p1c01_curated_original.py') --archive $archive --workspace $Workspace
if($LASTEXITCODE -ne 0) { throw 'P1C01_CURATED_SOURCE_STAGING_FAILED' }
& $exe @pyArgs (Join-Path $Workspace 'Scripts\p1c01_curated_ue_plan.py') --workspace $Workspace
if($LASTEXITCODE -ne 0) { throw 'P1C01_CURATED_STAGE_PLAN_REJECTED' }
$oldWorkspace = $env:GITHUB_WORKSPACE
$oldTarget = $env:SHIRE_TARGET_SHA
try {
  $env:GITHUB_WORKSPACE = $Workspace
  $env:SHIRE_TARGET_SHA = $ExpectedSha
  & (Join-Path $Workspace 'Scripts\ci_import_production_assets.cmd')
  if($LASTEXITCODE -ne 0) { throw 'P1C01_CURATED_EXISTING_COMMANDLET_IMPORT_FAILED' }
  $editor = 'C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Cmd.exe'
  if(-not (Test-Path -LiteralPath $editor -PathType Leaf)) { throw 'P1C01_CURATED_EDITOR_427_NOT_FOUND' }
  $script = Join-Path $Workspace 'Scripts\ue4_p1c01_curated_postimport.py'
  $project = Join-Path $Workspace 'ShireJourney.uproject'
  $postreport = Join-Path $Workspace 'Saved\P1C01CuratedEditorPostImport\receipt.json'
  $postlog = Join-Path $Workspace 'Saved\Logs\P1C01-Curated-EditorPython.log'
  New-Item -Force -ItemType Directory -Path (Split-Path $postlog -Parent) | Out-Null
  if(Test-Path -LiteralPath $postreport) { Remove-Item -LiteralPath $postreport -Force }
  if(Test-Path -LiteralPath $postlog) { Remove-Item -LiteralPath $postlog -Force }
  # Epic UE4.27 headless commandlet contract. ExecutePythonScript full-editor
  # option exited without running our script on the owner Windows runner.
  $env:SHIRE_CURATED_EDITOR_RUN = '1'
  try {
    & $editor $project '-run=pythonscript' ("-script=" + $script) '-unattended' '-nop4' '-nosplash' '-NoSound' '-nullrhi' '-stdout' '-FullStdOutLogOutput' ("-abslog=" + $postlog)
    $pythonExit = $LASTEXITCODE
  } finally {
    Remove-Item Env:\SHIRE_CURATED_EDITOR_RUN -ErrorAction SilentlyContinue
  }
  if($pythonExit -ne 0 -or -not (Test-Path -LiteralPath $postreport -PathType Leaf)) {
    if(Test-Path -LiteralPath $postlog) {
      Get-Content -LiteralPath $postlog -Tail 150 |
        Where-Object { $_ -match 'LogPython|P1C01|Error:|Warning:' } |
        Select-Object -Last 75 | ForEach-Object { Write-Host $_ }
    }
    if($pythonExit -ne 0) { throw "P1C01_CURATED_PYTHON_COMMANDLET_FAILED exit=$pythonExit" }
    throw 'P1C01_CURATED_EDITOR_POSTIMPORT_RECEIPT_MISSING'
  }
  $obs = Get-Content -LiteralPath $postreport -Raw | ConvertFrom-Json
  if($obs.target_sha -ne $ExpectedSha -or $obs.static_meshes_with_verified_lods -ne 34 -or
     $obs.imported_authored_sidecar_lods -ne 46 -or $obs.configured_packed_textures -ne 63 -or
     $obs.created_or_updated_material_instances -ne 21 -or
     $obs.material_triplet_bindings -ne 63 -or
     ($obs.exact_nature_single_slot_bindings + $obs.unresolved_nature_material_slots) -ne 8 -or
     $obs.tree_material_family_count -ne 4 -or
     ($obs.tree_material_verified_families + $obs.tree_material_unresolved_families) -ne 4 -or
     $obs.physically_persisted_uasset_checks -ne 118 -or
     $obs.gate6_7_closed -ne $false) { throw 'P1C01_CURATED_EDITOR_POSTIMPORT_EVIDENCE_INVALID' }
  Write-Host "P1C01_CURATED_AUTOMATIC_UE4_PASS sha=$ExpectedSha meshes=34 lods=46 textures=63 instances=21 nature_bound=$($obs.exact_nature_single_slot_bindings) nature_held=$($obs.unresolved_nature_material_slots) tree_bound=$($obs.tree_material_verified_families) tree_held=$($obs.tree_material_unresolved_families) report=$postreport"
  Write-Host 'P1C01_GATE67_OPEN needs=unresolved-multislot-architecture-collision-world-placement-PIE-package-device-human-review'
} finally {
  $env:GITHUB_WORKSPACE = $oldWorkspace
  $env:SHIRE_TARGET_SHA = $oldTarget
}
