param(
  [string]$StaticReceiptPath,
  [string]$ArtifactRoot = "",
  [string]$OutputRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path $PSScriptRoot -Parent
if([string]::IsNullOrWhiteSpace($StaticReceiptPath)){ throw "KAYKIT_RIG_UE4_RECEIPT_PATH_REQUIRED" }
if(-not (Test-Path -LiteralPath $StaticReceiptPath -PathType Leaf)){ throw "KAYKIT_RIG_UE4_STATIC_RECEIPT_MISSING path=$StaticReceiptPath" }
if([string]::IsNullOrWhiteSpace($ArtifactRoot)){ $ArtifactRoot = Split-Path $StaticReceiptPath -Parent }
if([string]::IsNullOrWhiteSpace($OutputRoot)){ $OutputRoot = Join-Path $env:RUNNER_TEMP "shire-kaykit-rig-ue4" }
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null

$receipt = Get-Content -LiteralPath $StaticReceiptPath -Raw | ConvertFrom-Json
$selected = @($receipt.selected_candidates)
if($selected.Count -lt 1){ throw "KAYKIT_RIG_UE4_NO_SELECTED_CANDIDATES" }

$target = $receipt.technical_import_target
$sourceRelative = "Characters/Rigs/P1C01_TECHNICAL_BRIDGE/SK_P1C01_KAYKIT_TECHNICAL.fbx"
$contentRelative = "Content/Production/Characters/Rigs/P1C01_TECHNICAL_BRIDGE"
$assetName = "SK_P1C01_KAYKIT_TECHNICAL"
if($target -ne $null){
  if(-not [string]::IsNullOrWhiteSpace([string]$target.source_relative)){ $sourceRelative = [string]$target.source_relative }
  if(-not [string]::IsNullOrWhiteSpace([string]$target.content_dir)){ $contentRelative = [string]$target.content_dir }
  if(-not [string]::IsNullOrWhiteSpace([string]$target.asset_name)){ $assetName = [string]$target.asset_name }
}
$sourceRelativePlatform = $sourceRelative.Replace("/", "\\")
$contentRelativePlatform = $contentRelative.Replace("/", "\\")
$productionRoot = Join-Path $root "SourceAssets\Production"
$sourceDestination = Join-Path $productionRoot $sourceRelativePlatform
$contentDir = Join-Path $root $contentRelativePlatform
$sourceIsolationBackup = Join-Path $OutputRoot "SourceAssets_Production_Backup"
$generated = @(
  (Join-Path $contentDir ($assetName + ".uasset")),
  (Join-Path $contentDir ($assetName + "_Skeleton.uasset")),
  (Join-Path $contentDir ($assetName + "_PhysicsAsset.uasset"))
)
$importMarkerPath = "/" + $sourceRelative.Replace("\\", "/")
$importScript = Join-Path $root "Scripts\ci_import_production_assets.cmd"
$importLog = Join-Path $root "Saved\Logs\CI-ProductionAssetImport.log"

function Remove-TransientRigAssets {
  foreach($path in $generated){ Remove-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue }
  Remove-Item -LiteralPath $sourceDestination -Force -ErrorAction SilentlyContinue
}

function Enter-IsolatedRigSource {
  if(Test-Path -LiteralPath $sourceIsolationBackup){ Remove-Item -LiteralPath $sourceIsolationBackup -Recurse -Force }
  if(Test-Path -LiteralPath $productionRoot){
    Move-Item -LiteralPath $productionRoot -Destination $sourceIsolationBackup -Force
  }
  New-Item -ItemType Directory -Path $productionRoot -Force | Out-Null
}

function Restore-ProductionSource {
  Remove-Item -LiteralPath $productionRoot -Recurse -Force -ErrorAction SilentlyContinue
  if(Test-Path -LiteralPath $sourceIsolationBackup){
    Move-Item -LiteralPath $sourceIsolationBackup -Destination $productionRoot -Force
  }
}

$results = @()
$technicalPass = $null
foreach($candidate in $selected){
  Remove-TransientRigAssets
  $candidatePath = Join-Path (Join-Path $ArtifactRoot "extracted") ([string]$candidate.filename)
  if(-not (Test-Path -LiteralPath $candidatePath -PathType Leaf)){ throw "KAYKIT_RIG_UE4_PAYLOAD_MISSING file=$candidatePath" }

  $expectedSha = ([string]$candidate.sha256).ToLowerInvariant()
  $actualSha = (Get-FileHash -LiteralPath $candidatePath -Algorithm SHA256).Hash.ToLowerInvariant()
  if($actualSha -ne $expectedSha){ throw "KAYKIT_RIG_UE4_ARTIFACT_HASH_FAIL file=$($candidate.filename) expected=$expectedSha actual=$actualSha" }

  Enter-IsolatedRigSource
  try {
    New-Item -ItemType Directory -Path (Split-Path $sourceDestination -Parent) -Force | Out-Null
    Copy-Item -LiteralPath $candidatePath -Destination $sourceDestination -Force
    $copiedSha = (Get-FileHash -LiteralPath $sourceDestination -Algorithm SHA256).Hash.ToLowerInvariant()
    if($copiedSha -ne $expectedSha){ throw "KAYKIT_RIG_UE4_COPY_HASH_FAIL file=$($candidate.filename)" }

    if(Test-Path -LiteralPath $importLog){ Remove-Item -LiteralPath $importLog -Force }
    Write-Host ("KAYKIT_RIG_UE4_PROBE_BEGIN file="+$candidate.filename+" sha256="+$expectedSha+" isolated-source=yes")
    # Set this one-call opt-in only while the real source tree is isolated.
    $savedIsolatedFlag=[Environment]::GetEnvironmentVariable("SHIRE_KAYKIT_RIG_ISOLATED_PROBE","Process")
    try{
      $env:SHIRE_KAYKIT_RIG_ISOLATED_PROBE="1"
      & $importScript "-EnableCharacterRigImport"
      $importExit = [int]$LASTEXITCODE
    }finally{
      if($null -eq $savedIsolatedFlag){
        Remove-Item -LiteralPath Env:SHIRE_KAYKIT_RIG_ISOLATED_PROBE -ErrorAction SilentlyContinue
      }else{
        $env:SHIRE_KAYKIT_RIG_ISOLATED_PROBE=$savedIsolatedFlag
      }
    }
  }
  finally {
    Restore-ProductionSource
  }
  if($importExit -ne 0){ throw "KAYKIT_RIG_UE4_IMPORT_INFRA_FAIL file=$($candidate.filename) exit=$importExit" }
  if(-not (Test-Path -LiteralPath $importLog -PathType Leaf)){ throw "KAYKIT_RIG_UE4_LOG_MISSING file=$($candidate.filename)" }

  $lines = @(Get-Content -LiteralPath $importLog)
  $begin = -1
  $result = -1
  for($i=0; $i -lt $lines.Count; $i++){
    if($lines[$i].Contains("ShireProductionImport: skeletal FBX import") -and $lines[$i].Contains($importMarkerPath)){ $begin=$i }
    if($begin -ge 0 -and $lines[$i].Contains("ShireProductionImport result:") -and $lines[$i].Contains($importMarkerPath + " |")){ $result=$i; break }
  }
  if($begin -lt 0 -or $result -lt 0){ throw "KAYKIT_RIG_UE4_IMPORT_MARKERS_MISSING file=$($candidate.filename)" }

  $resultLine = [string]$lines[$result]
  $registered = $resultLine.Contains("skeletal-registered=yes")
  $match = [regex]::Match($resultLine,'skeletal-bones=(\d+)')
  $bones = if($match.Success){[int]$match.Groups[1].Value}else{0}
  $segment = ($lines[$begin..$result] -join "`n")
  $reasons = @()
  if(-not $registered){ $reasons += "SKELETAL_REGISTRATION_FAILED" }
  if($bones -le 0){ $reasons += "ZERO_REFERENCE_BONES" }
  if($segment -match "No smoothing group information was found"){ $reasons += "MISSING_SMOOTHING_GROUPS" }
  if($segment -match "missing from the bind pose"){ $reasons += "MISSING_BIND_POSE_BONES" }
  if($segment -match "Not valid bind pose"){ $reasons += "INVALID_BIND_POSE" }
  if($segment -match "has no UV set"){ $reasons += "MISSING_UV_SET" }
  $reasons = @($reasons | Sort-Object -Unique)

  $meshAsset = Join-Path $contentDir ($assetName + ".uasset")
  $skeletonAsset = Join-Path $contentDir ($assetName + "_Skeleton.uasset")
  $assetsExist = (Test-Path -LiteralPath $meshAsset -PathType Leaf) -and (Test-Path -LiteralPath $skeletonAsset -PathType Leaf)
  if(-not $assetsExist -and $reasons.Count -eq 0){ $reasons += "GENERATED_SKELETAL_ASSETS_MISSING" }

  $row = [ordered]@{
    filename=[string]$candidate.filename
    sha256=$expectedSha
    bytes=[int64]$candidate.bytes
    fbx_version=[int]$candidate.fbx_version
    embedded_animation_marker=[bool]$candidate.animation
    skeletal_registered=[bool]$registered
    reference_bones=$bones
    generated_assets_exist=[bool]$assetsExist
    technical_pass=($reasons.Count -eq 0)
    reasons=$reasons
  }
  $results += [pscustomobject]$row

  if($reasons.Count -eq 0){
    $technicalPass = [pscustomobject]$row
    Write-Host ("KAYKIT_RIG_UE4_TECHNICAL_PASS file="+$candidate.filename+" sha256="+$expectedSha+" bones="+$bones+" deformationGate=next runtimeIntegration=false")
    break
  }
  Write-Host ("KAYKIT_RIG_UE4_TECHNICAL_REJECT file="+$candidate.filename+" sha256="+$expectedSha+" bones="+$bones+" reasons="+($reasons -join ","))
}

$out = [ordered]@{
  schema_version=1
  status=if($null -ne $technicalPass){"TECHNICAL_PASS_DEFORMATION_GATE_NEXT"}else{"BRIDGE_EXHAUSTED_TECHNICAL_REJECTION"}
  delivery_mode=[string]$receipt.delivery_mode
  license_sha256=[string]$receipt.license_sha256
  source_payload_sha256=@($selected | ForEach-Object { ([string]$_.sha256).ToLowerInvariant() })
  probed_count=$results.Count
  results=$results
  technical_pass_candidate=$technicalPass
  runtime_integration_allowed=$false
  final_likeness=$false
  next_if_pass="Deformation/reference-pose/root-scale/limb/hands-feet review plus embedded Idle/Walk/Run animation coverage. AnimBP and async runtime promotion remain blocked until those pass."
  evidence_boundary="Real UE4.27 skeletal technical import only. No final likeness, deformation, runtime, PIE/device/rendered visual/FPS acceptance."
}
$outPath = Join-Path $OutputRoot "p1c01_kaykit_rig_bridge_ue4.json"
$out | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $outPath -Encoding UTF8

Remove-TransientRigAssets
if($null -eq $technicalPass){ throw "KAYKIT_RIG_UE4_BRIDGE_EXHAUSTED probed=$($results.Count) receipt=$outPath" }
Write-Host ("KAYKIT_RIG_UE4_BRIDGE_PASS winner="+$technicalPass.filename+" sha256="+$technicalPass.sha256+" bones="+$technicalPass.reference_bones+" receipt="+$outPath)
