param(
  [string]$ManifestPath = "Data/P1C01OpenGameArtRpgHeroCandidateBatchV1.json",
  [string]$RejectionHistoryPath = "Data/P1C01FrodoTechnicalRejectionHistoryV1.json",
  [string]$OutputRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path $PSScriptRoot -Parent
if([string]::IsNullOrWhiteSpace($OutputRoot)) { $OutputRoot = Join-Path $env:RUNNER_TEMP "shire-frodo-rpg-ue4-gauntlet" }
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null

$stageScript = Join-Path $root "Scripts\stage_p1c01_frodo_rpg_gauntlet.ps1"
& $stageScript -ManifestPath $ManifestPath -RejectionHistoryPath $RejectionHistoryPath -OutputRoot $OutputRoot
$staticReceiptPath = Join-Path $OutputRoot "p1c01_frodo_rpg_static_gauntlet.json"
if(-not (Test-Path -LiteralPath $staticReceiptPath -PathType Leaf)) { throw "FRODO_RPG_UE4_STATIC_RECEIPT_MISSING" }
$staticReceipt = Get-Content -LiteralPath $staticReceiptPath -Raw | ConvertFrom-Json
$selected = @($staticReceipt.selected_candidates)
if($selected.Count -lt 1) { throw "FRODO_RPG_UE4_NO_SELECTED_CANDIDATES" }

$sourceDestination = Join-Path $root "SourceAssets\Production\Characters\Rigs\FRODO\SK_FRODO.fbx"
$contentDir = Join-Path $root "Content\Production\Characters\Rigs\FRODO"
$generated = @(
  (Join-Path $contentDir "SK_FRODO.uasset"),
  (Join-Path $contentDir "SK_FRODO_Skeleton.uasset"),
  (Join-Path $contentDir "SK_FRODO_PhysicsAsset.uasset")
)
$importScript = Join-Path $root "Scripts\ci_import_production_assets.cmd"
$importLog = Join-Path $root "Saved\Logs\CI-ProductionAssetImport.log"
$results = @()
$technicalPass = $null

function Remove-TransientFrodoAssets {
  foreach($path in $generated) { Remove-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue }
}

foreach($candidate in $selected) {
  Remove-TransientFrodoAssets
  New-Item -ItemType Directory -Path (Split-Path $sourceDestination -Parent) -Force | Out-Null
  Copy-Item -LiteralPath ([string]$candidate.extracted_path) -Destination $sourceDestination -Force
  $copiedSha = (Get-FileHash -LiteralPath $sourceDestination -Algorithm SHA256).Hash.ToLowerInvariant()
  $expectedSha = ([string]$candidate.sha256).ToLowerInvariant()
  if($copiedSha -ne $expectedSha) { throw "FRODO_RPG_UE4_COPY_HASH_FAIL entry=$($candidate.entry) expected=$expectedSha actual=$copiedSha" }

  if(Test-Path -LiteralPath $importLog) { Remove-Item -LiteralPath $importLog -Force }
  Write-Host ("FRODO_RPG_UE4_PROBE_BEGIN entry="+$candidate.entry+" sha256="+$expectedSha+" score="+$candidate.score)
  & $importScript "-EnableCharacterRigImport"
  $importExit = [int]$LASTEXITCODE
  if($importExit -ne 0) { throw "FRODO_RPG_UE4_IMPORT_INFRA_FAIL entry=$($candidate.entry) exit=$importExit" }
  if(-not (Test-Path -LiteralPath $importLog -PathType Leaf)) { throw "FRODO_RPG_UE4_LOG_MISSING entry=$($candidate.entry)" }

  $lines = @(Get-Content -LiteralPath $importLog)
  $begin = -1
  $result = -1
  for($i=0; $i -lt $lines.Count; $i++) {
    if($lines[$i].Contains("ShireProductionImport: skeletal FBX import") -and $lines[$i].Contains("/Characters/Rigs/FRODO/SK_FRODO.fbx")) { $begin = $i }
    if($begin -ge 0 -and $lines[$i].Contains("ShireProductionImport result:") -and $lines[$i].Contains("/Characters/Rigs/FRODO/SK_FRODO.fbx |")) { $result = $i; break }
  }
  if($begin -lt 0 -or $result -lt 0) { throw "FRODO_RPG_UE4_IMPORT_MARKERS_MISSING entry=$($candidate.entry)" }

  $resultLine = [string]$lines[$result]
  $registered = $resultLine.Contains("skeletal-registered=yes")
  $match = [regex]::Match($resultLine, 'skeletal-bones=(\d+)')
  $bones = if($match.Success){[int]$match.Groups[1].Value}else{0}
  $segment = ($lines[$begin..$result] -join "`n")
  $reasons = @()
  if(-not $registered) { $reasons += "SKELETAL_REGISTRATION_FAILED" }
  if($bones -le 0) { $reasons += "ZERO_REFERENCE_BONES" }
  if($segment -match "No smoothing group information was found") { $reasons += "MISSING_SMOOTHING_GROUPS" }
  if($segment -match "missing from the bind pose") { $reasons += "MISSING_BIND_POSE_BONES" }
  if($segment -match "Not valid bind pose") { $reasons += "INVALID_BIND_POSE" }
  if($segment -match "has no UV set") { $reasons += "MISSING_UV_SET" }
  $reasons = @($reasons | Sort-Object -Unique)

  $meshAsset = Join-Path $contentDir "SK_FRODO.uasset"
  $skeletonAsset = Join-Path $contentDir "SK_FRODO_Skeleton.uasset"
  $assetsExist = (Test-Path -LiteralPath $meshAsset -PathType Leaf) -and (Test-Path -LiteralPath $skeletonAsset -PathType Leaf)
  if(-not $assetsExist -and $reasons.Count -eq 0) { $reasons += "GENERATED_SKELETAL_ASSETS_MISSING" }

  $row = [ordered]@{
    entry = [string]$candidate.entry
    sha256 = $expectedSha
    bytes = [int64]$candidate.bytes
    fbx_version = [int]$candidate.fbx_version
    score = [int]$candidate.score
    skeletal_registered = [bool]$registered
    reference_bones = $bones
    generated_assets_exist = [bool]$assetsExist
    technical_pass = ($reasons.Count -eq 0)
    reasons = $reasons
  }
  $results += [pscustomobject]$row

  if($reasons.Count -eq 0) {
    $technicalPass = [pscustomobject]$row
    Write-Host ("FRODO_RPG_UE4_TECHNICAL_PASS entry="+$candidate.entry+" sha256="+$expectedSha+" bones="+$bones+" deformationGate=next runtimeIntegration=false")
    break
  }

  Write-Host ("FRODO_RPG_UE4_TECHNICAL_REJECT entry="+$candidate.entry+" sha256="+$expectedSha+" bones="+$bones+" reasons="+($reasons -join ","))
}

$receipt = [ordered]@{
  schema_version = 1
  status = if($null -ne $technicalPass){"TECHNICAL_PASS_DEFORMATION_GATE_NEXT"}else{"GAUNTLET_EXHAUSTED_TECHNICAL_REJECTION"}
  archive_sha256 = [string]$staticReceipt.archive_sha256
  archive_bytes = [int64]$staticReceipt.archive_bytes
  selected_count = $selected.Count
  probed_count = $results.Count
  results = $results
  technical_pass_candidate = $technicalPass
  runtime_integration_allowed = $false
  next_if_pass = "Deformation, pose, locomotion-skeleton and retarget suitability mega gate; then AnimBP and async runtime promotion only after those pass.",
  evidence_boundary = "Real UE4.27 skeletal technical evidence only. A pass does not prove deformation, retarget, final likeness, AnimBP, runtime, PIE/device/visual/performance acceptance."
}
$receiptPath = Join-Path $OutputRoot "p1c01_frodo_rpg_ue4_gauntlet.json"
$receipt | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $receiptPath -Encoding UTF8

Remove-TransientFrodoAssets
Remove-Item -LiteralPath $sourceDestination -Force -ErrorAction SilentlyContinue

if($null -eq $technicalPass) {
  throw "FRODO_RPG_UE4_GAUNTLET_EXHAUSTED probed=$($results.Count) receipt=$receiptPath"
}
Write-Host ("FRODO_RPG_UE4_GAUNTLET_PASS probed="+$results.Count+" winner="+$technicalPass.entry+" sha256="+$technicalPass.sha256+" bones="+$technicalPass.reference_bones+" receipt="+$receiptPath)
