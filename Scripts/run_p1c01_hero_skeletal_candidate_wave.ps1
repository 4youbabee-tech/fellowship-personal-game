param(
  [string]$ManifestPath = "Data/P1C01HeroSkeletalCandidateWaveV1.json",
  [string]$BaseIntakeManifest = "Data/P1C01CharacterRigAnimationPrepV1.json",
  [string]$WarehouseRoot = "D:\actions-runner\_warehouse\ShireJourney",
  [string]$OutputRoot = "",
  [switch]$ScoreSelfTest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-OptionalPropertyValue {
  param([object]$Object,[string]$Name,[object]$Default=$null)
  if($null -eq $Object){ return $Default }
  $property=$Object.PSObject.Properties[$Name]
  if($null -eq $property){ return $Default }
  return $property.Value
}

function Get-CandidateNameTokens {
  param([string]$Name)
  $stem=[IO.Path]::GetFileNameWithoutExtension($Name)
  $expanded=[regex]::Replace($stem,'([a-z0-9])([A-Z])','$1 $2')
  $expanded=[regex]::Replace($expanded,'([A-Za-z])([0-9])','$1 $2')
  $expanded=[regex]::Replace($expanded,'([0-9])([A-Za-z])','$1 $2')
  return @($expanded.ToLowerInvariant() -split '[^a-z0-9]+' | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
}

function Test-TokenSetContains {
  param([hashtable]$TokenSet,[string]$Token)
  return $TokenSet.ContainsKey($Token.ToLowerInvariant())
}

if($ScoreSelfTest){
  $female=@(Get-CandidateNameTokens "Worker_Female.fbx")
  $soldier=@(Get-CandidateNameTokens "BlueSoldier_Male.fbx")
  $base=@(Get-CandidateNameTokens "BaseCharacter.fbx")
  $old=@(Get-CandidateNameTokens "Doctor_Male_Old.fbx")
  if($female -contains "male"){ throw "P1C01_HERO_TOKEN_SELF_TEST_FEMALE_MATCHED_MALE" }
  if($soldier -contains "old"){ throw "P1C01_HERO_TOKEN_SELF_TEST_SOLDIER_MATCHED_OLD" }
  if($base -notcontains "base" -or $base -notcontains "character"){ throw "P1C01_HERO_TOKEN_SELF_TEST_CAMEL_SPLIT_FAIL" }
  if($old -notcontains "male" -or $old -notcontains "old"){ throw "P1C01_HERO_TOKEN_SELF_TEST_EXACT_MATCH_FAIL" }
  Write-Host "P1C01_HERO_TOKEN_SELF_TEST_PASS femaleNotMale=true soldierNotOld=true camelSplit=true"
  exit 0
}

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
$provenanceRows=@($intakeReceipt.candidate_source_provenance)

$fbxFiles=@(Get-ChildItem -LiteralPath $intakeRoot -Recurse -File -Filter "*.fbx" -ErrorAction SilentlyContinue)
$textureFiles=@(Get-ChildItem -LiteralPath $intakeRoot -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.Extension.ToLowerInvariant() -in @(".png",".tga") })
$bmpFiles=@(Get-ChildItem -LiteralPath $intakeRoot -Recurse -File -Filter "*.bmp" -ErrorAction SilentlyContinue)
if($bmpFiles.Count -gt 0){ throw "P1C01_HERO_RIG_FORBIDDEN_BMP count=$($bmpFiles.Count)" }

$globalMax=[int]$manifest.candidate_policy.max_ranked_candidates_per_character
$characterReports=@()
$poolReady=0
$unprovenancedFbx=@()
foreach($file in $fbxFiles){
  $match=@($provenanceRows | Where-Object { [string]$_.candidate_file -ieq [string]$file.FullName })
  if($match.Count -ne 1){ $unprovenancedFbx += $file.FullName }
}
if($unprovenancedFbx.Count -gt 0){ throw "P1C01_HERO_RIG_PROVENANCE_FAIL count=$($unprovenancedFbx.Count) first=$($unprovenancedFbx[0])" }

foreach($character in @($manifest.priority_characters)){
  $id=[string]$character.id
  $keywords=@($manifest.character_scoring.$id | ForEach-Object { ([string]$_).ToLowerInvariant() })
  $requiredAny=@(Get-OptionalPropertyValue $character "required_any_tokens" @() | ForEach-Object { ([string]$_).ToLowerInvariant() })
  $requiredAll=@(Get-OptionalPropertyValue $character "required_all_tokens" @() | ForEach-Object { ([string]$_).ToLowerInvariant() })
  $excluded=@(Get-OptionalPropertyValue $character "excluded_tokens" @() | ForEach-Object { ([string]$_).ToLowerInvariant() })
  $maxPer=[int](Get-OptionalPropertyValue $character "max_ranked_candidates" $globalMax)
  $scored=@()
  foreach($file in $fbxFiles){
    $tokens=@(Get-CandidateNameTokens $file.Name)
    $tokenSet=@{}
    foreach($token in $tokens){ $tokenSet[$token]=$true }
    $excludedMatches=@($excluded | Where-Object { Test-TokenSetContains $tokenSet $_ })
    if($excludedMatches.Count -gt 0){ continue }
    $identityMatches=@($requiredAny | Where-Object { Test-TokenSetContains $tokenSet $_ })
    if($requiredAny.Count -gt 0 -and $identityMatches.Count -eq 0){ continue }
    $missingRequired=@($requiredAll | Where-Object { -not (Test-TokenSetContains $tokenSet $_) })
    if($missingRequired.Count -gt 0){ continue }
    $matches=@($keywords | Where-Object { Test-TokenSetContains $tokenSet $_ })
    $score=$matches.Count
    if(Test-TokenSetContains $tokenSet "rig"){ $score+=2 }
    if(Test-TokenSetContains $tokenSet "anim"){ $score+=1 }
    if(Test-TokenSetContains $tokenSet "character"){ $score+=1 }
    if($score -le 0){ continue }
    $dir=$file.DirectoryName
    $nearTextures=@($textureFiles | Where-Object { $_.DirectoryName -eq $dir }).Count
    $prov=@($provenanceRows | Where-Object { [string]$_.candidate_file -ieq [string]$file.FullName })[0]
    $scored += [pscustomobject]@{
      source_fbx=$file.FullName
      filename=$file.Name
      bytes=[int64]$file.Length
      score=[int]$score
      filename_tokens=$tokens
      matched_terms=$matches
      identity_terms=$identityMatches
      nearby_png_tga=$nearTextures
      provider=[string]$prov.provider
      source_asset_id=[string]$prov.asset_id
      source_receipt=[string]$prov.receipt
      source_payload=[string]$prov.source_file
      source_sha256=[string]$prov.source_sha256
      state="RIG_BASE_CANDIDATE_STATIC_QC_REQUIRED"
      final_character_likeness=$false
      ready_for_import=$false
      qc_pending=@("fbx_static_structure","ue4_import","skeleton_quality","skin_weights","retarget","deformation","animation_coverage","material_slots","equipment_sockets","lod_cull","visual_readability")
    }
  }
  $ranked=@($scored | Sort-Object -Property @{Expression="score";Descending=$true}, @{Expression="bytes";Descending=$false} | Select-Object -First $maxPer)
  if($ranked.Count -gt 0){ $poolReady++ }
  $characterReports += [ordered]@{
    character=$id
    rig_family=[string]$character.rig_family
    selection_mode="EXACT_FILENAME_TOKEN_MATCH"
    required_any_tokens=$requiredAny
    required_all_tokens=$requiredAll
    excluded_tokens=$excluded
    candidate_count=$ranked.Count
    candidates=$ranked
  }
  Write-Host ("P1C01_HERO_RIG_POOL character="+$id+" candidates="+$ranked.Count+" selection=exact-filename-tokens")
}

$totalRanked=0
foreach($row in $characterReports){ $totalRanked += [int]$row.candidate_count }
$minimumTotal=[int]$manifest.success_boundary.minimum_fbx_candidates_total
$minimumPools=[int]$manifest.success_boundary.minimum_character_pools_with_candidates

$report=[ordered]@{
  schema_version=2
  wave_id=[string]$manifest.wave_id
  generated_utc=[DateTime]::UtcNow.ToString("o")
  ranking_semantics="EXACT_FILENAME_TOKENS_V2"
  intake_exit=$intakeExit
  intake_prepared_count=[int]$intakeReceipt.prepared_count
  intake_pending_count=[int]$intakeReceipt.pending_count
  intake_blocked_count=[int]$intakeReceipt.blocked_count
  discovered_fbx=$fbxFiles.Count
  provenance_rows=$provenanceRows.Count
  unprovenanced_fbx=$unprovenancedFbx.Count
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

Write-Host ("P1C01_HERO_RIG_DIAGNOSTIC intakeExit="+$intakeExit+" intakePrepared="+[int]$intakeReceipt.prepared_count+" intakePending="+[int]$intakeReceipt.pending_count+" intakeBlocked="+[int]$intakeReceipt.blocked_count+" discoveredFbx="+$fbxFiles.Count+" discoveredPngTga="+$textureFiles.Count+" ranked="+$totalRanked+" pools="+$poolReady+" ranking=exact-filename-tokens-v2")
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

Write-Host ("P1C01_HERO_RIG_CANDIDATE_PASS fbx="+$fbxFiles.Count+" ranked="+$totalRanked+" pools="+$poolReady+" ranking=exact-filename-tokens-v2 summary="+$summary)
exit 0

