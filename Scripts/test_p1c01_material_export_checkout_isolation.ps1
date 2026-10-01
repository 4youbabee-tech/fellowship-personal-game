$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$exportPath = Join-Path $projectRoot "Scripts\export_p1c01_material_source_branch.ps1"
$workflowPath = Join-Path $projectRoot ".github\workflows\warehouse-stage.yml"
$prePath = Join-Path $projectRoot ".github\workflows\pre-unreal-validation.yml"

foreach($path in @($exportPath,$workflowPath,$prePath)){
  if(-not (Test-Path -LiteralPath $path -PathType Leaf)){ throw "P1C01_MATERIAL_EXPORT_ISOLATION_FILE_MISSING path=$path" }
}

$export = Get-Content -LiteralPath $exportPath -Raw
$workflow = Get-Content -LiteralPath $workflowPath -Raw
$pre = Get-Content -LiteralPath $prePath -Raw

if($export -match '(?i)worktree\s+remove\s+--force'){
  throw "P1C01_MATERIAL_EXPORT_UNBOUNDED_GIT_WORKTREE_REMOVE_FORBIDDEN"
}
foreach($marker in @(
  "Generated material worktree overlaps caller checkout",
  "P1C01_MATERIAL_SOURCE_CALLER_CHECKOUT_LOST",
  "P1C01_MATERIAL_SOURCE_CALLER_SCRIPT_LOST",
  "P1C01_MATERIAL_SOURCE_CALLER_CHECKOUT_PASS",
  "worktree prune --expire now"
)){
  if(-not $export.Contains($marker)){ throw "P1C01_MATERIAL_EXPORT_ISOLATION_MARKER_MISSING marker=$marker" }
}
if(-not $workflow.Contains("WAREHOUSE_SOURCE_CHECKOUT_SURVIVAL_PASS")){
  throw "P1C01_MATERIAL_EXPORT_WORKFLOW_SURVIVAL_GUARD_MISSING"
}
if(-not $workflow.Contains('if not exist "%SHIRE_WAREHOUSE_SOURCE%\Scripts\stage_quaternius_warehouse.ps1" exit /b 84')){
  throw "P1C01_MATERIAL_EXPORT_WORKFLOW_DOWNSTREAM_SCRIPT_GUARD_MISSING"
}
$wiring=@([regex]::Matches($pre,'test_p1c01_material_export_checkout_isolation\.ps1'))
if($wiring.Count -ne 1){ throw "P1C01_MATERIAL_EXPORT_ISOLATION_TEST_WIRING_COUNT count=$($wiring.Count)" }

Write-Host "P1C01_MATERIAL_EXPORT_CHECKOUT_ISOLATION_PASS boundedCleanup=true callerGuard=true workflowGuard=true"
