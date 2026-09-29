param(
  [string]$ManifestPath = "Data/P1C01HeroSkeletalCandidateWaveV1.json",
  [string]$BaseIntakeManifest = "Data/P1C01CharacterRigAnimationPrepV1.json",
  [string]$WarehouseRoot = "D:\actions-runner\_warehouse\ShireJourney",
  [string]$OutputRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
foreach($name in @("ManifestPath","BaseIntakeManifest")){
  $value = Get-Variable -Name $name -ValueOnly
  if(-not [IO.Path]::IsPathRooted($value)){ Set-Variable -Name $name -Value (Join-Path $ProjectRoot $value) }
}
if(-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)){ throw "P1C01_HERO_RIG_MANIFEST_MISSING path=$ManifestPath" }
if(-not (Test-Path -LiteralPath $BaseIntakeManifest -PathType Leaf)){ throw "P1C01_HERO_RIG_BASE_INTAKE_MISSING path=$BaseIntakeManifest" }
if(-not (Test-Path -LiteralPath $WarehouseRoot -PathType Container)){ throw "P1C01_HERO_RIG_WAREHOUSE_MISSING root=$WarehouseRoot" }

$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
if([string]::IsNullOrWhiteSpace($OutputRoot)){ $OutputRoot = Join-Path $WarehouseRoot "_p1c01_hero_skeletal_candidate_v1" }
$intakeRoot = Join-Path $OutputRoot "intake"
New-Item -ItemType Directory -Path $intakeRoot -Force | Out-Null

Write-Host "P1C01_HERO_RIG_INVENTORY_GATE_BEGIN"
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "audit_warehouse_inventory.ps1") -Root $WarehouseRoot
if([int]$LASTEXITCODE -ne 0){ throw "P1C01_HERO_RIG_INVENTORY_GATE_FAIL exit=$LASTEXITCODE" }
Write-Host "P1C01_HERO_RIG_INVENTORY_GATE_PASS"

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "prepare_p1c01_character_rig_intake.ps1") -ManifestPath $BaseIntakeManifest -WarehouseRoot $WarehouseRoot -OutputRoot $intakeRoot
$intakeExit=[int]$LASTEXITCODE
$receiptPath=Join-Path $intakeRoot "p1c01_character_rig_intake_receipt.json"
if(-not (Test-Path -LiteralPath $receiptPath -PathType Leaf)){ throw "P1C01_HERO_RIG_INTAKE_RECEIPT_MISSING exit=$intakeExit" }
$intakeReceipt=Get-Content -LiteralPath $receiptPath -Raw | ConvertFrom-Json

$fbxFiles=@(Get-ChildItem -LiteralPath $intakeRoot -Recurse -File -Filter "*.fbx" -ErrorAction SilentlyContinue)
$textureFiles=@(Get-ChildItem -LiteralPath $intakeRoot -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.Extension.ToLowerInvariant() -in @(".png",".tga") })
$bmpFiles=@(Get-ChildItem -LiteralPath $intakeRoot -Recurse -File -Filter "*.bmp" -ErrorAction SilentlyContinue)
if($bmpFiles.Count -gt 0){ throw "P1C01_HERO_RIG_FORBIDDEN_BMP count=$($bmpFiles.Count)" }

$maxPer=[int]$manifest.candidate_policy.max_ranked_candidates_per_character
$characterReports=@()
$poolReady=0
foreach($character in @($manifest.priority_characters)){
  $id=[string]$character.id
  $keywords=@($manifest.character_scoring.$id | ForEach-Object { ([string]$_).ToLowerInvariant() })
  $scored=@()
  foreach($file in $fbxFiles){
    $hay=$file.FullName.ToLowerInvariant()
    $matches=@($keywords | Where-Object { $hay.Contains($_) })
    $score=$matches.Count
    if($hay.Contains("rig")){ $score+=2 }
    if($hay.Contains("anim")){ $score+=1 }
    if($hay.Contains("character")){ $score+=1 }
    if($score -le 0){ continue }
    $dir=$file.DirectoryName
    $nearTextures=@($textureFiles | Where-Object { $_.DirectoryName -eq $dir }).Count
    $scored += [pscustomobject]@{
      source_fbx=$file.FullName
      bytes=[int64]$file.Length
      score=[int]$score
      matched_terms=$matches
      nearby_png_tga=$nearTextures
      state="RIG_FAMILY_CANDIDATE_QC_REQUIRED"
      ready_for_import=$false
      qc_pending=@("skeleton","skin_weights","retarget","deformation","animation_coverage","material_slots","equipment_sockets","lod_cull","visual_readability")
    }
  }
  $ranked=@($scored | Sort-Object -Property @{Expression="score";Descending=$true}, @{Expression="bytes";Descending=$false} | Select-Object -First $maxPer)
  if($ranked.Count -gt 0){ $poolReady++ }
  $characterReports += [ordered]@{
    character=$id
    rig_family=[string]$character.rig_family
    candidate_count=$ranked.Count
    candidates=$ranked
  }
  Write-Host ("P1C01_HERO_RIG_POOL character="+$id+" candidates="+$ranked.Count)
}

$totalRanked=0
foreach($row in $characterReports){ $totalRanked += [int]$row.candidate_count }
$minimumTotal=[int]$manifest.success_boundary.minimum_fbx_candidates_total
$minimumPools=[int]$manifest.success_boundary.minimum_character_pools_with_candidates

$report=[ordered]@{
  schema_version=1
  wave_id=[string]$manifest.wave_id
  generated_utc=[DateTime]::UtcNow.ToString("o")
  intake_exit=$intakeExit
  intake_prepared_count=[int]$intakeReceipt.prepared_count
  intake_pending_count=[int]$intakeReceipt.pending_count
  intake_blocked_count=[int]$intakeReceipt.blocked_count
  discovered_fbx=$fbxFiles.Count
  discovered_png_tga=$textureFiles.Count
  ranked_candidates_total=$totalRanked
  pools_with_candidates=$poolReady
  minimum_fbx_candidates_total=$minimumTotal
  minimum_character_pools_with_candidates=$minimumPools
  characters=$characterReports
  runtime_integration="NOT_STARTED"
  visual_acceptance="NOT_CLAIMED"
  evidence_boundary=[string]$manifest.evidence_boundary
}
$summary=Join-Path $OutputRoot "p1c01_hero_skeletal_candidate_summary.json"
$report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $summary -Encoding UTF8

Write-Host ("P1C01_HERO_RIG_DIAGNOSTIC intakeExit="+$intakeExit+" intakePrepared="+[int]$intakeReceipt.prepared_count+" intakePending="+[int]$intakeReceipt.pending_count+" intakeBlocked="+[int]$intakeReceipt.blocked_count+" discoveredFbx="+$fbxFiles.Count+" discoveredPngTga="+$textureFiles.Count+" ranked="+$totalRanked+" pools="+$poolReady)
foreach($pendingRow in @($intakeReceipt.pending)){
  Write-Host ("P1C01_HERO_RIG_PENDING provider="+[string]$pendingRow.provider+" id="+[string]$pendingRow.id+" reason="+[string]$pendingRow.reason)
}
foreach($blockedRow in @($intakeReceipt.blocked)){
  Write-Host ("P1C01_HERO_RIG_BLOCKED id="+[string]$blockedRow.id+" reason="+[string]$blockedRow.reason+" file="+[string]$blockedRow.file)
}
foreach($charRow in $characterReports){
  Write-Host ("P1C01_HERO_RIG_CHARACTER character="+[string]$charRow.character+" candidates="+[int]$charRow.candidate_count)
}
Write-Host ("P1C01_HERO_RIG_SUMMARY path="+$summary)

if($totalRanked -lt $minimumTotal){ throw "P1C01_HERO_RIG_CANDIDATE_COVERAGE_FAIL total=$totalRanked required=$minimumTotal" }
if($poolReady -lt $minimumPools){ throw "P1C01_HERO_RIG_POOL_COVERAGE_FAIL ready=$poolReady required=$minimumPools" }

Write-Host ("P1C01_HERO_RIG_CANDIDATE_PASS fbx="+$fbxFiles.Count+" ranked="+$totalRanked+" pools="+$poolReady+" summary="+$summary)
exit 0
