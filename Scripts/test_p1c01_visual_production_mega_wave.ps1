$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest
$root=Split-Path -Parent $PSScriptRoot
$m=Join-Path $root "Data\P1C01VisualProductionMegaWaveV2.json"
$s=Join-Path $root "Scripts\run_p1c01_visual_production_mega_wave.ps1"
if(-not(Test-Path $m -PathType Leaf)){throw "P1C01_MEGA_WAVE_MANIFEST_MISSING"}
if(-not(Test-Path $s -PathType Leaf)){throw "P1C01_MEGA_WAVE_SCRIPT_MISSING"}
$j=Get-Content $m -Raw|ConvertFrom-Json
if([int]$j.total_slots -ne @($j.slots).Count){throw "P1C01_MEGA_WAVE_COUNT_MISMATCH"}
if([int]$j.total_slots -lt 180){throw "P1C01_MEGA_WAVE_MINIMUM_FAIL"}
$families=@($j.slots|ForEach-Object{$_.family}|Sort-Object -Unique)
foreach($required in @("architecture","props","vegetation","materials","audio","vfx","animation","creature_support")){
  if($families -notcontains $required){throw "P1C01_MEGA_WAVE_FAMILY_MISSING family=$required"}
}
foreach($slot in @($j.slots)){
  if(-not [bool]$slot.provenance_required){throw "P1C01_MEGA_WAVE_PROVENANCE_DISABLED id=$($slot.id)"}
}
if($j.promotion_rules -notcontains "Animated production assets: FBX only."){throw "P1C01_MEGA_WAVE_FBX_RULE_FAIL"}
Write-Host "P1C01_VISUAL_MEGA_WAVE_CONTRACT_PASS slots=$($j.total_slots) families=$($families.Count)"
