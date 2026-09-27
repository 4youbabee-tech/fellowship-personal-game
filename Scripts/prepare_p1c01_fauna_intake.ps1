param(
  [string]$ManifestPath="Data/P1C01LivingWorldFaunaPrepV1.json",
  [string]$WarehouseRoot="C:\actions-runner\_warehouse\ShireJourney",
  [string]$OutputRoot=""
)
Set-StrictMode -Version Latest
$ErrorActionPreference="Stop"
$ProjectRoot=Split-Path $PSScriptRoot -Parent
if([string]::IsNullOrWhiteSpace($OutputRoot)){$OutputRoot=Join-Path $ProjectRoot "Saved\FaunaIntake\P1C01"}
if(-not(Test-Path -LiteralPath $ManifestPath)){$c=Join-Path $ProjectRoot $ManifestPath;if(Test-Path -LiteralPath $c){$ManifestPath=$c}}
if(-not(Test-Path -LiteralPath $ManifestPath)){throw "Fauna intake manifest missing: $ManifestPath"}
$manifest=Get-Content -LiteralPath $ManifestPath -Raw|ConvertFrom-Json
New-Item -ItemType Directory -Path $OutputRoot -Force|Out-Null
$fallback=@()
foreach($item in @($manifest.project_owned_fallback)){
  $p=Join-Path $ProjectRoot ([string]$item.path)
  $fallback += [ordered]@{id=[string]$item.id;exists=(Test-Path -LiteralPath $p -PathType Leaf);path=[string]$item.path;state=[string]$item.state}
}
$pending=@()
foreach($item in @($manifest.external_candidates)){
  if([string]$item.state -ne "AUTHORIZED_FOR_STAGING"){
    $pending += [ordered]@{provider=[string]$item.provider;id=[string]$item.id;reason="license_capture_required_before_staging"}
  }
}
$report=[ordered]@{
  schema_version=1;batch_id=[string]$manifest.batch_id;project_owned_fallback=$fallback;external_pending=$pending;
  caps=$manifest.living_world_caps;
  rule="Do not increase fauna group caps. Animated external fauna remain blocked until explicit license capture and FBX rig/deformation QC."
}
$receipt=Join-Path $OutputRoot "p1c01_fauna_intake_receipt.json"
$report|ConvertTo-Json -Depth 10|Set-Content -LiteralPath $receipt -Encoding UTF8
if(@($fallback|Where-Object{-not $_.exists}).Count -gt 0){Write-Host "P1C01_FAUNA_PREP_BLOCKED missing_project_owned_fallback=true";exit 2}
Write-Host ("P1C01_FAUNA_PREP_PASS fallback="+$fallback.Count+" pending_external="+$pending.Count+" receipt="+$receipt)
