$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$root = Split-Path -Parent $PSScriptRoot
$prepPath = Join-Path $root "Scripts\prepare_p1c01_character_rig_intake.ps1"
$wavePath = Join-Path $root "Scripts\run_p1c01_hero_skeletal_candidate_wave.ps1"
$manifestPath = Join-Path $root "Data\P1C01HeroSkeletalCandidateWaveV1.json"

foreach($path in @($prepPath,$wavePath,$manifestPath)){
  if(-not (Test-Path -LiteralPath $path -PathType Leaf)){ throw "P1C01_HERO_PROVENANCE_FILE_MISSING path=$path" }
}

$prep = Get-Content -LiteralPath $prepPath -Raw
$wave = Get-Content -LiteralPath $wavePath -Raw
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json

if(-not [bool]$manifest.candidate_policy.require_provenance){ throw "P1C01_HERO_PROVENANCE_POLICY_DISABLED" }
foreach($marker in @("candidate_source_provenance","candidate_file","source_sha256",'receipt=[string]$row.receipt')){
  if(-not $prep.Contains($marker)){ throw "P1C01_HERO_PROVENANCE_INTAKE_MARKER_MISSING marker=$marker" }
}
foreach($marker in @("P1C01_HERO_RIG_PROVENANCE_FAIL","source_asset_id","source_receipt","source_payload","unprovenanced_fbx")){
  if(-not $wave.Contains($marker)){ throw "P1C01_HERO_PROVENANCE_WAVE_MARKER_MISSING marker=$marker" }
}
if(-not $wave.Contains('-ieq [string]$file.FullName')){ throw "P1C01_HERO_PROVENANCE_EXACT_FILE_MATCH_MISSING" }

Write-Host "P1C01_HERO_PROVENANCE_CONTRACT_PASS failClosed=true exactFile=true receiptBound=true"
