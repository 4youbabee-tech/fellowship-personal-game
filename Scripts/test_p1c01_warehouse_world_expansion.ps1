$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest
$root=Split-Path -Parent $PSScriptRoot
$p=Join-Path $root "Data\P1C01WarehouseWorldExpansionV1.json"
if(-not(Test-Path $p -PathType Leaf)){throw "P1C01_WORLD_EXPANSION_MISSING"}
$j=Get-Content $p -Raw|ConvertFrom-Json
if(@($j.acquisition_lanes).Count -lt 9){throw "P1C01_WORLD_EXPANSION_LANES_FAIL"}
if(@($j.world_build_cells).Count -lt 4){throw "P1C01_WORLD_EXPANSION_CELLS_FAIL"}
if($j.acquisition_lanes[2].production -notcontains "FBX only"){throw "P1C01_WORLD_EXPANSION_FBX_FAIL"}
if($j.acquisition_lanes[0].production -notcontains "1K/2K default"){throw "P1C01_WORLD_EXPANSION_TEXTURE_BUDGET_FAIL"}
if($j.blockers[0].state -ne "BLOCKED_MANUAL"){throw "P1C01_WORLD_EXPANSION_MANUAL_BLOCK_FAIL"}
if($j.warehouse_first.rule -notmatch "before new acquisition"){throw "P1C01_WORLD_EXPANSION_WAREHOUSE_FIRST_FAIL"}
Write-Host "P1C01_WAREHOUSE_WORLD_EXPANSION_PASS lanes=$(@($j.acquisition_lanes).Count) cells=$(@($j.world_build_cells).Count)"
