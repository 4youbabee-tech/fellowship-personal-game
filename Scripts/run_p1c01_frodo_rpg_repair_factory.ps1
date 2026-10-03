param(
  [ValidateSet("NormalizeHosted","ProbeUE4")]
  [string]$Mode,
  [string]$ManifestPath = "Data/P1C01OpenGameArtRpgHeroCandidateBatchV1.json",
  [string]$RejectionHistoryPath = "Data/P1C01FrodoTechnicalRejectionHistoryV1.json",
  [string]$OutputRoot = "",
  [string]$RepairReceiptPath = "",
  [string]$BlenderExecutable = "blender"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path $PSScriptRoot -Parent
if([string]::IsNullOrWhiteSpace($OutputRoot)) { $OutputRoot = Join-Path $env:RUNNER_TEMP "shire-frodo-rpg-repair-factory" }
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null

function Get-FbxBinaryVersion([string]$Path) {
  $bytes = [System.IO.File]::ReadAllBytes($Path)
  if($bytes.Length -lt 27) { return 0 }
  $magic = [System.Text.Encoding]::ASCII.GetString($bytes, 0, [Math]::Min(23, $bytes.Length))
  if(-not $magic.StartsWith("Kaydara FBX Binary")) { return 0 }
  return [BitConverter]::ToInt32($bytes, 23)
}

if($Mode -eq "NormalizeHosted") {
  $stageRoot = Join-Path $OutputRoot "source"
  & (Join-Path $root "Scripts/stage_p1c01_frodo_rpg_gauntlet.ps1") -ManifestPath $ManifestPath -RejectionHistoryPath $RejectionHistoryPath -OutputRoot $stageRoot
  $staticReceiptPath = Join-Path $stageRoot "p1c01_frodo_rpg_static_gauntlet.json"
  if(-not (Test-Path -LiteralPath $staticReceiptPath -PathType Leaf)) { throw "FRODO_REPAIR_STATIC_RECEIPT_MISSING" }
  $staticReceipt = Get-Content -LiteralPath $staticReceiptPath -Raw | ConvertFrom-Json
  $selected = @($staticReceipt.selected_candidates)
  if($selected.Count -lt 1) { throw "FRODO_REPAIR_NO_SELECTED_CANDIDATES" }

  $blenderCommand = Get-Command $BlenderExecutable -ErrorAction Stop
  $blenderVersionLines = @(& $blenderCommand.Source --version)
  $blenderExit = [int]$LASTEXITCODE
  if($blenderExit -ne 0 -or $blenderVersionLines.Count -lt 1) {
    throw "FRODO_REPAIR_BLENDER_UNAVAILABLE executable=$BlenderExecutable exit=$blenderExit"
  }
  $blenderVersion = [string]$blenderVersionLines[0]

  $normalizedDir = Join-Path $OutputRoot "normalized"
  New-Item -ItemType Directory -Path $normalizedDir -Force | Out-Null
  $pythonPath = Join-Path $OutputRoot "normalize_fbx_for_ue427.py"
  @'
import argparse
import os
import sys
import bpy

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args(argv)

bpy.ops.wm.read_factory_settings(use_empty=True)
result = bpy.ops.import_scene.fbx(filepath=args.input, use_custom_normals=True)
if "FINISHED" not in result:
    raise RuntimeError("FBX import failed")

armatures = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
if not armatures:
    raise RuntimeError("No armature after FBX import")
if not meshes:
    raise RuntimeError("No mesh after FBX import")

skinned = any(
    mod.type == "ARMATURE" and mod.object is not None
    for mesh in meshes for mod in mesh.modifiers
)
if not skinned:
    raise RuntimeError("No skinned mesh/armature modifier after FBX import")

os.makedirs(os.path.dirname(args.output), exist_ok=True)
bpy.ops.export_scene.fbx(
    filepath=args.output,
    check_existing=False,
    use_selection=False,
    object_types={"ARMATURE", "MESH", "EMPTY"},
    use_mesh_modifiers=True,
    use_custom_props=True,
    add_leaf_bones=False,
    primary_bone_axis="Y",
    secondary_bone_axis="X",
    use_armature_deform_only=False,
    mesh_smooth_type="FACE",
    use_tspace=True,
    bake_anim=True,
    bake_anim_use_all_bones=True,
    bake_anim_use_nla_strips=True,
    bake_anim_use_all_actions=True,
    bake_anim_force_startend_keying=True,
    path_mode="AUTO",
    embed_textures=False,
)
if not os.path.isfile(args.output) or os.path.getsize(args.output) <= 0:
    raise RuntimeError("FBX export did not create output")
print("SHIRE_FRODO_NORMALIZE_PASS armatures=%d meshes=%d output=%s" % (len(armatures), len(meshes), args.output))
'@ | Set-Content -LiteralPath $pythonPath -Encoding UTF8

  $rows = @()
  $index = 0
  foreach($candidate in $selected) {
    $index++
    $sourceSha = ([string]$candidate.sha256).ToLowerInvariant()
    $sourcePath = [string]$candidate.extracted_path
    if(-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) { throw "FRODO_REPAIR_SOURCE_MISSING entry=$($candidate.entry)" }
    $actualSourceSha = (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash.ToLowerInvariant()
    if($actualSourceSha -ne $sourceSha) { throw "FRODO_REPAIR_SOURCE_HASH_FAIL entry=$($candidate.entry) expected=$sourceSha actual=$actualSourceSha" }

    $outName = ("candidate_{0:D2}.fbx" -f $index)
    $outPath = Join-Path $normalizedDir $outName
    & $BlenderExecutable --background --factory-startup --python $pythonPath -- --input $sourcePath --output $outPath
    if($LASTEXITCODE -ne 0) { throw "FRODO_REPAIR_BLENDER_EXPORT_FAIL entry=$($candidate.entry) exit=$LASTEXITCODE" }
    if(-not (Test-Path -LiteralPath $outPath -PathType Leaf)) { throw "FRODO_REPAIR_OUTPUT_MISSING entry=$($candidate.entry)" }

    $normalizedSha = (Get-FileHash -LiteralPath $outPath -Algorithm SHA256).Hash.ToLowerInvariant()
    $normalizedBytes = (Get-Item -LiteralPath $outPath).Length
    $fbxVersion = Get-FbxBinaryVersion $outPath
    if($fbxVersion -le 0 -or $fbxVersion -gt 7500) { throw "FRODO_REPAIR_FBX_VERSION_REJECT entry=$($candidate.entry) version=$fbxVersion" }

    $rows += [pscustomobject][ordered]@{
      entry = [string]$candidate.entry
      source_sha256 = $sourceSha
      source_bytes = [int64]$candidate.bytes
      source_fbx_version = [int]$candidate.fbx_version
      score = [int]$candidate.score
      normalized_relative_path = ("normalized/" + $outName)
      normalized_sha256 = $normalizedSha
      normalized_bytes = [int64]$normalizedBytes
      normalized_fbx_version = [int]$fbxVersion
      repair_kind = "BLENDER_REEXPORT_EXPORT_METADATA_NORMALIZATION"
    }
    Write-Host ("FRODO_RPG_REPAIR_NORMALIZED entry="+$candidate.entry+" sourceSha="+$sourceSha+" normalizedSha="+$normalizedSha+" version="+$fbxVersion+" bytes="+$normalizedBytes)
  }

  $receipt = [ordered]@{
    schema_version = 1
    status = "NORMALIZED_CANDIDATES_READY_FOR_UE4_REVALIDATION"
    source_archive_sha256 = [string]$staticReceipt.archive_sha256
    source_archive_bytes = [int64]$staticReceipt.archive_bytes
    blender_version = [string]$blenderVersion
    normalized_candidates = $rows
    original_payloads_remain_rejected = $true
    runtime_integration_allowed = $false
    evidence_boundary = "Hosted normalization only. Re-export does not prove UE4 technical acceptance, deformation, retarget, likeness, AnimBP, runtime, PIE/device/visual/performance acceptance."
  }
  $receiptPath = Join-Path $OutputRoot "p1c01_frodo_rpg_repair_receipt.json"
  $receipt | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $receiptPath -Encoding UTF8
  Write-Host ("FRODO_RPG_REPAIR_FACTORY_PASS candidates="+$rows.Count+" receipt="+$receiptPath)
  exit 0
}

if([string]::IsNullOrWhiteSpace($RepairReceiptPath)) { throw "FRODO_REPAIR_UE4_RECEIPT_REQUIRED" }
if(-not (Test-Path -LiteralPath $RepairReceiptPath -PathType Leaf)) { throw "FRODO_REPAIR_UE4_RECEIPT_MISSING path=$RepairReceiptPath" }
$repairReceipt = Get-Content -LiteralPath $RepairReceiptPath -Raw | ConvertFrom-Json
$selected = @($repairReceipt.normalized_candidates)
if($selected.Count -lt 1) { throw "FRODO_REPAIR_UE4_NO_NORMALIZED_CANDIDATES" }
$repairRoot = Split-Path $RepairReceiptPath -Parent

$sourceDestination = Join-Path $root "SourceAssets/Production/Characters/Rigs/FRODO/SK_FRODO.fbx"
$contentDir = Join-Path $root "Content/Production/Characters/Rigs/FRODO"
$generated = @(
  (Join-Path $contentDir "SK_FRODO.uasset"),
  (Join-Path $contentDir "SK_FRODO_Skeleton.uasset"),
  (Join-Path $contentDir "SK_FRODO_PhysicsAsset.uasset")
)
$importScript = Join-Path $root "Scripts/ci_import_production_assets.cmd"
$importLog = Join-Path $root "Saved/Logs/CI-ProductionAssetImport.log"
$results = @()
$technicalPass = $null

function Remove-TransientFrodoAssets {
  foreach($path in $generated) { Remove-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue }
}

foreach($candidate in $selected) {
  Remove-TransientFrodoAssets
  $candidatePath = Join-Path $repairRoot ([string]$candidate.normalized_relative_path)
  if(-not (Test-Path -LiteralPath $candidatePath -PathType Leaf)) { throw "FRODO_REPAIR_UE4_NORMALIZED_FILE_MISSING entry=$($candidate.entry) path=$candidatePath" }
  $expectedSha = ([string]$candidate.normalized_sha256).ToLowerInvariant()
  $actualSha = (Get-FileHash -LiteralPath $candidatePath -Algorithm SHA256).Hash.ToLowerInvariant()
  if($actualSha -ne $expectedSha) { throw "FRODO_REPAIR_UE4_NORMALIZED_HASH_FAIL entry=$($candidate.entry) expected=$expectedSha actual=$actualSha" }

  New-Item -ItemType Directory -Path (Split-Path $sourceDestination -Parent) -Force | Out-Null
  Copy-Item -LiteralPath $candidatePath -Destination $sourceDestination -Force
  if(Test-Path -LiteralPath $importLog) { Remove-Item -LiteralPath $importLog -Force }

  Write-Host ("FRODO_RPG_REPAIR_UE4_PROBE_BEGIN entry="+$candidate.entry+" sourceSha="+$candidate.source_sha256+" normalizedSha="+$expectedSha)
  & $importScript "-EnableCharacterRigImport"
  $importExit = [int]$LASTEXITCODE
  if($importExit -ne 0) { throw "FRODO_REPAIR_UE4_IMPORT_INFRA_FAIL entry=$($candidate.entry) exit=$importExit" }
  if(-not (Test-Path -LiteralPath $importLog -PathType Leaf)) { throw "FRODO_REPAIR_UE4_LOG_MISSING entry=$($candidate.entry)" }

  $lines = @(Get-Content -LiteralPath $importLog)
  $begin = -1
  $result = -1
  for($i=0; $i -lt $lines.Count; $i++) {
    if($lines[$i].Contains("ShireProductionImport: skeletal FBX import") -and $lines[$i].Contains("/Characters/Rigs/FRODO/SK_FRODO.fbx")) { $begin = $i }
    if($begin -ge 0 -and $lines[$i].Contains("ShireProductionImport result:") -and $lines[$i].Contains("/Characters/Rigs/FRODO/SK_FRODO.fbx |")) { $result = $i; break }
  }
  if($begin -lt 0 -or $result -lt 0) { throw "FRODO_REPAIR_UE4_IMPORT_MARKERS_MISSING entry=$($candidate.entry)" }

  $resultLine = [string]$lines[$result]
  $registered = $resultLine.Contains("skeletal-registered=yes")
  $match = [regex]::Match($resultLine, 'skeletal-bones=(\d+)')
  $bones = if($match.Success){[int]$match.Groups[1].Value}else{0}
  $segment = ($lines[$begin..$result] -join [Environment]::NewLine)
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

  $row = [pscustomobject][ordered]@{
    entry = [string]$candidate.entry
    source_sha256 = ([string]$candidate.source_sha256).ToLowerInvariant()
    normalized_sha256 = $expectedSha
    normalized_bytes = [int64]$candidate.normalized_bytes
    normalized_fbx_version = [int]$candidate.normalized_fbx_version
    skeletal_registered = [bool]$registered
    reference_bones = $bones
    generated_assets_exist = [bool]$assetsExist
    technical_pass = ($reasons.Count -eq 0)
    reasons = $reasons
  }
  $results += $row

  if($reasons.Count -eq 0) {
    $technicalPass = $row
    Write-Host ("FRODO_RPG_REPAIR_UE4_TECHNICAL_PASS entry="+$candidate.entry+" normalizedSha="+$expectedSha+" bones="+$bones+" deformationGate=next runtimeIntegration=false")
    break
  }
  Write-Host ("FRODO_RPG_REPAIR_UE4_TECHNICAL_REJECT entry="+$candidate.entry+" normalizedSha="+$expectedSha+" bones="+$bones+" reasons="+($reasons -join ","))
}

$receipt = [ordered]@{
  schema_version = 1
  status = if($null -ne $technicalPass){"NORMALIZED_TECHNICAL_PASS_DEFORMATION_GATE_NEXT"}else{"NORMALIZED_GAUNTLET_EXHAUSTED_TECHNICAL_REJECTION"}
  source_archive_sha256 = [string]$repairReceipt.source_archive_sha256
  blender_version = [string]$repairReceipt.blender_version
  probed_count = $results.Count
  results = $results
  technical_pass_candidate = $technicalPass
  runtime_integration_allowed = $false
  next_if_pass = "Deformation/reference-pose/limb/hand-foot/root/scale hierarchy gate, then locomotion retarget and AnimBP; async runtime promotion remains blocked until those pass."
  evidence_boundary = "Real UE4.27 skeletal revalidation of normalized payloads only. No deformation, retarget, likeness, AnimBP, runtime, PIE/device/visual/FPS acceptance is claimed."
}
$receiptPath = Join-Path $OutputRoot "p1c01_frodo_rpg_repair_ue4_receipt.json"
$receipt | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $receiptPath -Encoding UTF8

Remove-TransientFrodoAssets
Remove-Item -LiteralPath $sourceDestination -Force -ErrorAction SilentlyContinue

if($null -eq $technicalPass) { throw "FRODO_RPG_REPAIR_UE4_GAUNTLET_EXHAUSTED probed=$($results.Count) receipt=$receiptPath" }
Write-Host ("FRODO_RPG_REPAIR_UE4_GAUNTLET_PASS winner="+$technicalPass.entry+" normalizedSha="+$technicalPass.normalized_sha256+" bones="+$technicalPass.reference_bones+" receipt="+$receiptPath)
