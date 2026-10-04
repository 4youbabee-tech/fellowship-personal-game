param(
  [string]$HostedReceiptPath,
  [string]$ArtifactRoot = "",
  [string]$OutputRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
if([string]::IsNullOrWhiteSpace($HostedReceiptPath)){ throw "HUMAN_WAVE2_UE4_RECEIPT_REQUIRED" }
if(-not (Test-Path -LiteralPath $HostedReceiptPath -PathType Leaf)){ throw "HUMAN_WAVE2_UE4_RECEIPT_MISSING path=$HostedReceiptPath" }
if([string]::IsNullOrWhiteSpace($ArtifactRoot)){ $ArtifactRoot=Split-Path $HostedReceiptPath -Parent }
if([string]::IsNullOrWhiteSpace($OutputRoot)){ $OutputRoot=Join-Path $env:RUNNER_TEMP "shire-human-wave2-ue4" }
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null

$hosted=Get-Content -LiteralPath $HostedReceiptPath -Raw | ConvertFrom-Json
$selected=@($hosted.normalized_candidates)
if($selected.Count -lt 1){ throw "HUMAN_WAVE2_UE4_NO_CANDIDATES" }

$sourceDestination=Join-Path $root "SourceAssets\Production\Characters\Rigs\FRODO\SK_FRODO.fbx"
$contentDir=Join-Path $root "Content\Production\Characters\Rigs\FRODO"
$generated=@(
  (Join-Path $contentDir "SK_FRODO.uasset"),
  (Join-Path $contentDir "SK_FRODO_Skeleton.uasset"),
  (Join-Path $contentDir "SK_FRODO_PhysicsAsset.uasset")
)
$importScript=Join-Path $root "Scripts\ci_import_production_assets.cmd"
$importLog=Join-Path $root "Saved\Logs\CI-ProductionAssetImport.log"

function Remove-Transient {
  foreach($path in $generated){ Remove-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue }
  Remove-Item -LiteralPath $sourceDestination -Force -ErrorAction SilentlyContinue
}

$results=@()
$winner=$null
foreach($candidate in $selected){
  Remove-Transient
  $candidatePath=Join-Path $ArtifactRoot ([string]$candidate.normalized_relative_path)
  if(-not (Test-Path -LiteralPath $candidatePath -PathType Leaf)){ throw "HUMAN_WAVE2_UE4_PAYLOAD_MISSING path=$candidatePath" }
  $expected=([string]$candidate.normalized_sha256).ToLowerInvariant()
  $actual=(Get-FileHash -LiteralPath $candidatePath -Algorithm SHA256).Hash.ToLowerInvariant()
  if($actual -ne $expected){ throw "HUMAN_WAVE2_UE4_HASH_FAIL expected=$expected actual=$actual" }

  New-Item -ItemType Directory -Path (Split-Path $sourceDestination -Parent) -Force | Out-Null
  Copy-Item -LiteralPath $candidatePath -Destination $sourceDestination -Force
  if(Test-Path -LiteralPath $importLog){ Remove-Item -LiteralPath $importLog -Force }

  Write-Host ("HUMAN_WAVE2_UE4_PROBE_BEGIN source="+$candidate.source_entry+" normalizedSha="+$expected)
  & $importScript "-EnableCharacterRigImport"
  $importExit=[int]$LASTEXITCODE
  if($importExit -ne 0){ throw "HUMAN_WAVE2_UE4_IMPORT_INFRA_FAIL exit=$importExit" }
  if(-not (Test-Path -LiteralPath $importLog -PathType Leaf)){ throw "HUMAN_WAVE2_UE4_LOG_MISSING" }

  $lines=@(Get-Content -LiteralPath $importLog)
  $begin=-1
  $result=-1
  for($i=0;$i -lt $lines.Count;$i++){
    if($lines[$i].Contains("ShireProductionImport: skeletal FBX import") -and $lines[$i].Contains("/Characters/Rigs/FRODO/SK_FRODO.fbx")){ $begin=$i }
    if($begin -ge 0 -and $lines[$i].Contains("ShireProductionImport result:") -and $lines[$i].Contains("/Characters/Rigs/FRODO/SK_FRODO.fbx |")){ $result=$i; break }
  }
  if($begin -lt 0 -or $result -lt 0){ throw "HUMAN_WAVE2_UE4_IMPORT_MARKERS_MISSING" }

  $resultLine=[string]$lines[$result]
  $registered=$resultLine.Contains("skeletal-registered=yes")
  $m=[regex]::Match($resultLine,'skeletal-bones=(\d+)')
  $bones=if($m.Success){[int]$m.Groups[1].Value}else{0}
  $linkedSkeleton=$resultLine.Contains("skeletal-skeleton=yes")
  $skeletonPathMatch=[regex]::Match($resultLine,'skeletal-skeleton-path=([^\s]+)')
  $linkedSkeletonPath=if($skeletonPathMatch.Success){[string]$skeletonPathMatch.Groups[1].Value}else{"NONE"}
  $segment=($lines[$begin..$result] -join [Environment]::NewLine)
  $reasons=@()
  if(-not $registered){ $reasons+="SKELETAL_REGISTRATION_FAILED" }
  if($bones -le 0){ $reasons+="ZERO_REFERENCE_BONES" }
  if(-not $linkedSkeleton){ $reasons+="LINKED_USKELETON_MISSING" }
  if($segment -match "No smoothing group information was found"){ $reasons+="MISSING_SMOOTHING_GROUPS" }
  if($segment -match "missing from the bind pose"){ $reasons+="MISSING_BIND_POSE_BONES" }
  if($segment -match "Not valid bind pose"){ $reasons+="INVALID_BIND_POSE" }
  if($segment -match "has no UV set"){ $reasons+="MISSING_UV_SET" }
  $reasons=@($reasons | Sort-Object -Unique)

  $meshAsset=Join-Path $contentDir "SK_FRODO.uasset"
  $physicsAsset=Join-Path $contentDir "SK_FRODO_PhysicsAsset.uasset"
  $meshPackageExists=(Test-Path -LiteralPath $meshAsset -PathType Leaf)
  $physicsAssetExists=(Test-Path -LiteralPath $physicsAsset -PathType Leaf)
  if(-not $meshPackageExists -and $reasons.Count -eq 0){ $reasons+="GENERATED_SKELETAL_MESH_PACKAGE_MISSING" }

  $row=[pscustomobject][ordered]@{
    source_entry=[string]$candidate.source_entry
    source_sha256=[string]$candidate.source_sha256
    normalized_sha256=$expected
    normalized_fbx_version=[int]$candidate.normalized_fbx_version
    hosted_bone_count=[int]$candidate.bone_count
    hosted_weighted_vertex_count=[int]$candidate.weighted_vertex_count
    hosted_zero_weight_vertex_count=[int]$candidate.zero_weight_vertex_count
    hosted_uv_layer_count=[int]$candidate.uv_layer_count
    ue4_skeletal_registered=[bool]$registered
    ue4_reference_bones=$bones
    ue4_linked_skeleton=[bool]$linkedSkeleton
    ue4_linked_skeleton_path=$linkedSkeletonPath
    generated_mesh_package_exists=[bool]$meshPackageExists
    physics_asset_exists=[bool]$physicsAssetExists
    physics_sanity=if($physicsAssetExists){"AUTO_GENERATED_PRESENT"}else{"SEPARATE_SANITY_GATE_PENDING_CAPSULE_RUNTIME_OWNED"}
    technical_pass=($reasons.Count -eq 0)
    reasons=$reasons
  }
  $results+=$row

  if($reasons.Count -eq 0){
    $winner=$row
    Write-Host ("HUMAN_WAVE2_UE4_TECHNICAL_PASS normalizedSha="+$expected+" bones="+$bones+" next=deformation-readiness")
    break
  }
  Write-Host ("HUMAN_WAVE2_UE4_TECHNICAL_REJECT normalizedSha="+$expected+" bones="+$bones+" reasons="+($reasons -join ","))
}

$out=[ordered]@{
  schema_version=1
  status=if($null -ne $winner){"TECHNICAL_WINNER_DEFORMATION_GATE_NEXT"}else{"SOURCE_FAMILY_EXHAUSTED_TECHNICAL_REJECTION"}
  source_page=[string]$hosted.source_page
  archive_sha256=[string]$hosted.archive_sha256
  blender_version=[string]$hosted.blender_version
  probed_count=$results.Count
  results=$results
  technical_winner=$winner
  runtime_integration_allowed=$false
  deformation_accepted=$false
  next_if_pass="Reference-pose/root-scale/hierarchy + shoulder/elbow/knee + hands/feet deformation review, then Idle/Walk/Run retarget and AnimBP. Runtime remains modular fallback until all pass."
  evidence_boundary="Real UE4.27 skeletal technical gate only. No visual deformation/runtime/PIE/device/FPS acceptance."
}
$outPath=Join-Path $OutputRoot "p1c01_human_wave2_ue4.json"
$out | ConvertTo-Json -Depth 14 | Set-Content -LiteralPath $outPath -Encoding UTF8

Remove-Transient
if($null -eq $winner){ throw "HUMAN_WAVE2_UE4_FAMILY_EXHAUSTED receipt=$outPath" }
Write-Host ("HUMAN_WAVE2_UE4_PASS winner="+$winner.normalized_sha256+" receipt="+$outPath)
