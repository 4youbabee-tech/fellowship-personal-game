param(
  [string]$ManifestPath = "Data/P1C01HumanCharacterProductionWave2V1.json",
  [string]$OutputRoot = "",
  [string]$BlenderExecutable = "blender"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression.FileSystem

$root = Split-Path $PSScriptRoot -Parent
if(-not [IO.Path]::IsPathRooted($ManifestPath)){ $ManifestPath = Join-Path $root $ManifestPath }
if(-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)){ throw "HUMAN_WAVE2_MANIFEST_MISSING path=$ManifestPath" }
$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json

if(([string]$manifest.source_family.observed_license).ToUpperInvariant() -ne "CC0"){ throw "HUMAN_WAVE2_LICENSE_POLICY_FAIL" }
if(([string]$manifest.source_family.final_animated_format).ToUpperInvariant() -ne "FBX"){ throw "HUMAN_WAVE2_FORMAT_POLICY_FAIL" }

if([string]::IsNullOrWhiteSpace($OutputRoot)){ $OutputRoot = Join-Path $env:RUNNER_TEMP "shire-human-wave2" }
if(Test-Path -LiteralPath $OutputRoot){ Remove-Item -LiteralPath $OutputRoot -Recurse -Force }
$downloadRoot = Join-Path $OutputRoot "download"
$extractRoot = Join-Path $OutputRoot "source"
$normalizedRoot = Join-Path $OutputRoot "normalized"
New-Item -ItemType Directory -Path $downloadRoot,$extractRoot,$normalizedRoot -Force | Out-Null

$headers = @{ "User-Agent" = "ShireJourney-HumanWave2/1.0" }
$pagePath = Join-Path $downloadRoot "source_page.html"
$archivePath = Join-Path $downloadRoot "character_source.zip"
Invoke-WebRequest -UseBasicParsing -Uri ([string]$manifest.source_family.source_page) -Headers $headers -OutFile $pagePath
Invoke-WebRequest -UseBasicParsing -Uri ([string]$manifest.source_family.archive_url) -Headers $headers -OutFile $archivePath

$pageText = Get-Content -LiteralPath $pagePath -Raw
if($pageText -notmatch "CC0"){ throw "HUMAN_WAVE2_SOURCE_PAGE_CC0_MARKER_MISSING" }
$pageMarker=if($null -ne $manifest.source_family.PSObject.Properties["required_page_regex"]){[string]$manifest.source_family.required_page_regex}else{"Rigged Low Poly Character Base Model|Rigged.*Character"}
if($pageText -notmatch $pageMarker){ throw "HUMAN_WAVE2_SOURCE_PAGE_RIGGED_MARKER_MISSING" }

$archiveItem = Get-Item -LiteralPath $archivePath
if($archiveItem.Length -le 0 -or $archiveItem.Length -gt [int64]$manifest.source_policy.max_archive_bytes){ throw "HUMAN_WAVE2_ARCHIVE_SIZE_FAIL bytes=$($archiveItem.Length)" }
$archiveSha = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
$pageSha = (Get-FileHash -LiteralPath $pagePath -Algorithm SHA256).Hash.ToLowerInvariant()

$zip = [IO.Compression.ZipFile]::OpenRead($archivePath)
$sourceRows=@()
try {
  foreach($entry in $zip.Entries){
    $name=([string]$entry.FullName).Replace([char]92,'/')
    $parts=@($name.Split('/') | Where-Object { $_ -ne '' })
    if($name.StartsWith('/') -or $name -match '^[A-Za-z]:' -or @($parts | Where-Object { $_ -eq '..' }).Count -gt 0){ throw "HUMAN_WAVE2_ARCHIVE_PATH_UNSAFE entry=$name" }
    if([int64]$entry.Length -gt [int64]$manifest.source_policy.max_source_entry_bytes){ throw "HUMAN_WAVE2_ARCHIVE_ENTRY_OVERSIZE entry=$name bytes=$($entry.Length)" }
    $ext=[IO.Path]::GetExtension($name).ToLowerInvariant()
    if($ext -notin @(".fbx",".blend",".png",".tga") -or [string]::IsNullOrWhiteSpace($entry.Name)){ continue }
    $safeName=("src_{0:D2}_{1}" -f ($sourceRows.Count+1), [IO.Path]::GetFileName($name))
    $dest=Join-Path $extractRoot $safeName
    [IO.Compression.ZipFileExtensions]::ExtractToFile($entry,$dest,$true)
    $sourceRows += [pscustomobject]@{
      entry=$name; extracted_path=$dest; filename=$safeName; extension=$ext;
      bytes=[int64]$entry.Length; sha256=(Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash.ToLowerInvariant()
    }
  }
}
finally { $zip.Dispose() }

$characterSources=@($sourceRows | Where-Object { $_.extension -in @(".blend",".fbx") })
if($characterSources.Count -lt 1){ throw "HUMAN_WAVE2_NO_CHARACTER_SOURCE" }

$blenderCommand=Get-Command $BlenderExecutable -ErrorAction Stop
$blenderVersionLines=@(& $blenderCommand.Source --version)
if([int]$LASTEXITCODE -ne 0 -or $blenderVersionLines.Count -lt 1){ throw "HUMAN_WAVE2_BLENDER_UNAVAILABLE" }
$blenderVersion=[string]$blenderVersionLines[0]

$pythonPath=Join-Path $OutputRoot "normalize_human_wave2.py"
@'
import argparse, json, math, os, sys
import bpy
from mathutils import Vector

argv=sys.argv
argv=argv[argv.index("--")+1:] if "--" in argv else []
p=argparse.ArgumentParser()
p.add_argument("--source", required=True)
p.add_argument("--source-kind", required=True)
p.add_argument("--output", required=True)
p.add_argument("--receipt", required=True)
args=p.parse_args(argv)

if args.source_kind == ".fbx":
    bpy.ops.wm.read_factory_settings(use_empty=True)
    result=bpy.ops.import_scene.fbx(filepath=args.source, use_custom_normals=True)
    if "FINISHED" not in result:
        raise RuntimeError("FBX import failed")
elif args.source_kind == ".blend":
    bpy.ops.wm.open_mainfile(filepath=args.source)
else:
    raise RuntimeError("unsupported source kind")

armatures=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"]
meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
if not armatures: raise RuntimeError("no armature")
if not meshes: raise RuntimeError("no mesh")

for o in bpy.context.scene.objects: o.select_set(False)
for o in armatures + meshes:
    o.hide_set(False)
    o.select_set(True)
bpy.context.view_layer.objects.active=armatures[0]

bone_names=[b.name.lower() for a in armatures for b in a.data.bones]
bone_count=sum(len(a.data.bones) for a in armatures)
deform_bone_count=sum(1 for a in armatures for b in a.data.bones if b.use_deform)
vertex_count=weighted=zero_weight=uv_layers=0
finite_bounds=True
for m in meshes:
    vertex_count += len(m.data.vertices)
    uv_layers += len(m.data.uv_layers)
    for v in m.data.vertices:
        if any(g.weight > 0.00001 for g in v.groups): weighted += 1
        else: zero_weight += 1
    for c in m.bound_box:
        w=m.matrix_world @ Vector(c)
        finite_bounds = finite_bounds and all(math.isfinite(float(v)) for v in w)

def has_any(tokens):
    return any(any(t in n for t in tokens) for n in bone_names)

coverage={
    "root":has_any(["root","master","hips","pelvis"]),
    "pelvis":has_any(["pelvis","hips"]),
    "spine":has_any(["spine","chest"]),
    "head":has_any(["head"]),
    "shoulder":has_any(["shoulder","clavicle","upperarm","upper_arm"]),
    "elbow":has_any(["forearm","lowerarm","lower_arm","elbow"]),
    "knee":has_any(["calf","shin","lowerleg","lower_leg","knee"]),
}
if weighted <= 0: raise RuntimeError("no weighted vertices")
if uv_layers <= 0: raise RuntimeError("no UV layers")
if not finite_bounds: raise RuntimeError("non-finite bounds")

os.makedirs(os.path.dirname(args.output), exist_ok=True)
bpy.ops.export_scene.fbx(
    filepath=args.output, check_existing=False, use_selection=True,
    object_types={"ARMATURE","MESH"}, use_mesh_modifiers=True,
    add_leaf_bones=False, primary_bone_axis="Y", secondary_bone_axis="X",
    use_armature_deform_only=True, mesh_smooth_type="FACE", use_tspace=True,
    bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True,
    bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True,
    path_mode="AUTO", embed_textures=False)
if not os.path.isfile(args.output) or os.path.getsize(args.output) <= 0:
    raise RuntimeError("FBX export missing")

receipt={
    "armature_count":len(armatures),"mesh_count":len(meshes),"bone_count":bone_count,
    "deform_bone_count":deform_bone_count,
    "vertex_count":vertex_count,"weighted_vertex_count":weighted,
    "zero_weight_vertex_count":zero_weight,"uv_layer_count":uv_layers,
    "finite_bounds":finite_bounds,"joint_name_coverage":coverage,
    "source_kind":args.source_kind}
with open(args.receipt,"w",encoding="utf-8") as f: json.dump(receipt,f,indent=2,sort_keys=True)
print("HUMAN_WAVE2_BLENDER_PASS",json.dumps(receipt,sort_keys=True))
'@ | Set-Content -LiteralPath $pythonPath -Encoding UTF8

function Get-FbxBinaryVersion([string]$Path){
  $bytes=[IO.File]::ReadAllBytes($Path)
  if($bytes.Length -lt 27){ return 0 }
  $prefix=[Text.Encoding]::ASCII.GetString($bytes,0,[Math]::Min(32,$bytes.Length))
  if(-not $prefix.StartsWith("Kaydara FBX Binary")){ return 0 }
  return [BitConverter]::ToInt32($bytes,23)
}

function Get-HumanWave2FilenameTokens([string]$Entry){$s=[regex]::Replace([IO.Path]::GetFileNameWithoutExtension($Entry),'([a-z0-9])([A-Z])','$1 $2');return @($s.ToLowerInvariant() -split '[^a-z0-9]+' | Where-Object {$_})}
$preferred=@($manifest.source_policy.preferred_filename_tokens | ForEach-Object {([string]$_).ToLowerInvariant()})
$excluded=@($manifest.source_policy.excluded_filename_tokens | ForEach-Object {([string]$_).ToLowerInvariant()})
$scored=@()
foreach($src in $characterSources){$tokens=@(Get-HumanWave2FilenameTokens ([string]$src.entry));if(@($excluded|Where-Object{$tokens -contains $_}).Count -gt 0){continue};$score=@($preferred|Where-Object{$tokens -contains $_}).Count;if($preferred.Count -gt 0 -and $score -eq 0){continue};$scored += [pscustomobject]@{source=$src;score=$score}}
$maxHostedCandidates=if($null -ne $manifest.source_policy.PSObject.Properties["max_hosted_candidates"]){[int]$manifest.source_policy.max_hosted_candidates}else{[Math]::Max([int]$manifest.source_policy.max_ue4_candidates,8)}
$selectedSources=@($scored | Sort-Object @{Expression="score";Descending=$true}, @{Expression={if($_.source.extension -eq ".fbx"){0}else{1}}}, @{Expression={$_.source.bytes}} | Select-Object -First $maxHostedCandidates | ForEach-Object {$_.source})
Write-Host ("HUMAN_WAVE2_HOSTED_SWEEP candidates="+$selectedSources.Count+" ue4Max="+[int]$manifest.source_policy.max_ue4_candidates)
$normalized=@(); $index=0
foreach($src in $selectedSources){
  $index++
  $outName=("candidate_{0:D2}.fbx" -f $index)
  $outPath=Join-Path $normalizedRoot $outName
  $readinessPath=Join-Path $normalizedRoot ("candidate_{0:D2}_readiness.json" -f $index)
  $deformationPath=Join-Path $normalizedRoot ("candidate_{0:D2}_deformation_preflight.json" -f $index)
  $rejectReasons=@()

  if($src.extension -eq ".blend"){
    & $blenderCommand.Source --background ([string]$src.extracted_path) --python-exit-code 18 --python $pythonPath -- --source ([string]$src.extracted_path) --source-kind ".blend" --output $outPath --receipt $readinessPath
  }else{
    & $blenderCommand.Source --background --factory-startup --python-exit-code 18 --python $pythonPath -- --source ([string]$src.extracted_path) --source-kind ".fbx" --output $outPath --receipt $readinessPath
  }
  $normalizeExit=[int]$LASTEXITCODE
  if($normalizeExit -ne 0 -or -not (Test-Path -LiteralPath $outPath -PathType Leaf) -or -not (Test-Path -LiteralPath $readinessPath -PathType Leaf)){
    $rejectReasons += ("NORMALIZATION_REJECT_EXIT_"+$normalizeExit)
    $normalized += [pscustomobject]@{
      source_entry=[string]$src.entry; source_kind=[string]$src.extension; source_sha256=[string]$src.sha256; source_bytes=[int64]$src.bytes;
      normalized_relative_path=$null; normalized_sha256=$null; normalized_bytes=0; normalized_fbx_version=0; static_rig_markers=$false;
      readiness_relative_path=$null; armature_count=0; mesh_count=0; bone_count=0; deform_bone_count=0; vertex_count=0; weighted_vertex_count=0;
      zero_weight_vertex_count=0; zero_weight_ratio=1.0; uv_layer_count=0; finite_bounds=$false; joint_name_coverage=$null;
      deformation_preflight_status="NOT_RUN"; deformation_preflight_reasons=@(); deformation_preflight_relative_path=$null;
      quality_pass=$false; quality_reasons=$rejectReasons
    }
    Write-Host ("HUMAN_WAVE2_CANDIDATE_FAST_REJECT stage=normalize entry="+[string]$src.entry+" exit="+$normalizeExit)
    Remove-Item -LiteralPath $outPath,$readinessPath -Force -ErrorAction SilentlyContinue
    continue
  }

  $version=Get-FbxBinaryVersion $outPath
  if($version -le 0 -or $version -gt [int]$manifest.source_policy.fbx_version_ceiling){
    $rejectReasons += ("NORMALIZED_FBX_VERSION_FAIL_"+$version)
  }

  $normSha=(Get-FileHash -LiteralPath $outPath -Algorithm SHA256).Hash.ToLowerInvariant()
  $readiness=Get-Content -LiteralPath $readinessPath -Raw | ConvertFrom-Json

  if($rejectReasons.Count -eq 0){
    $probeScript=Join-Path $root "Scripts\probe_p1c01_human_fbx_deformation.py"
    & $blenderCommand.Source --background --factory-startup --python-exit-code 19 --python $probeScript -- --fbx $outPath --output $deformationPath
    $probeExit=[int]$LASTEXITCODE
    if($probeExit -ne 0){ throw "HUMAN_WAVE2_DEFORMATION_PREFLIGHT_INFRA_FAIL entry=$($src.entry) exit=$probeExit" }
    if(-not (Test-Path -LiteralPath $deformationPath -PathType Leaf)){ throw "HUMAN_WAVE2_DEFORMATION_PREFLIGHT_RECEIPT_MISSING entry=$($src.entry)" }
    $deformation=Get-Content -LiteralPath $deformationPath -Raw | ConvertFrom-Json
  }else{
    $deformation=[pscustomobject]@{status="NOT_RUN";reasons=@($rejectReasons)}
  }

  $ascii=[Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes($outPath))
  $staticPass=$ascii.Contains("Geometry") -and $ascii.Contains("Model") -and $ascii.Contains("LimbNode") -and $ascii.Contains("Skin") -and $ascii.Contains("Cluster")
  $zeroWeightRatio=if([int]$readiness.vertex_count -gt 0){ [double]$readiness.zero_weight_vertex_count / [double]$readiness.vertex_count }else{ 1.0 }
  $qualityReasons=@($rejectReasons)
  if(-not $staticPass){ $qualityReasons+="MISSING_STATIC_RIG_MARKERS" }
  if([int]$readiness.deform_bone_count -le 0){ $qualityReasons+="ZERO_DEFORM_BONES" }
  if([int]$readiness.weighted_vertex_count -le 0){ $qualityReasons+="ZERO_WEIGHTED_VERTICES" }
  if([int]$readiness.uv_layer_count -le 0){ $qualityReasons+="MISSING_UV_LAYER" }
  if(-not [bool]$readiness.finite_bounds){ $qualityReasons+="NONFINITE_BOUNDS" }
  if($zeroWeightRatio -gt [double]$manifest.source_policy.max_zero_weight_ratio){ $qualityReasons+="EXCESS_ZERO_WEIGHT_RATIO" }
  if(([string]$deformation.status) -ne "HOSTED_DEFORMATION_PREFLIGHT_PASS"){ $qualityReasons+="HOSTED_DEFORMATION_PREFLIGHT_REJECT" }
  $qualityPass=$qualityReasons.Count -eq 0

  $normalized += [pscustomobject]@{
    source_entry=[string]$src.entry; source_kind=[string]$src.extension; source_sha256=[string]$src.sha256; source_bytes=[int64]$src.bytes;
    normalized_relative_path=("normalized/"+$outName); normalized_sha256=$normSha; normalized_bytes=[int64](Get-Item $outPath).Length;
    normalized_fbx_version=[int]$version; static_rig_markers=[bool]$staticPass;
    readiness_relative_path=("normalized/"+[IO.Path]::GetFileName($readinessPath));
    armature_count=[int]$readiness.armature_count; mesh_count=[int]$readiness.mesh_count; bone_count=[int]$readiness.bone_count;
    deform_bone_count=[int]$readiness.deform_bone_count; vertex_count=[int]$readiness.vertex_count; weighted_vertex_count=[int]$readiness.weighted_vertex_count;
    zero_weight_vertex_count=[int]$readiness.zero_weight_vertex_count; zero_weight_ratio=$zeroWeightRatio; uv_layer_count=[int]$readiness.uv_layer_count;
    finite_bounds=[bool]$readiness.finite_bounds; joint_name_coverage=$readiness.joint_name_coverage;
    deformation_preflight_status=[string]$deformation.status; deformation_preflight_reasons=@($deformation.reasons);
    deformation_preflight_relative_path=if(Test-Path -LiteralPath $deformationPath -PathType Leaf){"normalized/"+[IO.Path]::GetFileName($deformationPath)}else{$null};
    quality_pass=[bool]$qualityPass; quality_reasons=$qualityReasons
  }
  Write-Host ("HUMAN_WAVE2_CANDIDATE_HOSTED_RESULT entry="+[string]$src.entry+" qualityPass="+$qualityPass+" reasons="+($qualityReasons -join ","))
}

$eligible=@($normalized | Where-Object { $_.quality_pass } | Select-Object -First ([int]$manifest.source_policy.max_ue4_candidates))
$receipt=[ordered]@{
  schema_version=1; status=if($eligible.Count -gt 0){"HOSTED_NORMALIZED_CANDIDATES_READY_FOR_UE4"}else{"HOSTED_SOURCE_FAMILY_EXHAUSTED_BEFORE_UE4"};
  source_page=[string]$manifest.source_family.source_page; source_creator=[string]$manifest.source_family.creator; license="CC0";
  source_page_sha256=$pageSha; archive_sha256=$archiveSha; archive_bytes=[int64]$archiveItem.Length; blender_version=$blenderVersion;
  source_inventory=@($sourceRows | Select-Object entry,extension,bytes,sha256); normalized_results=$normalized; normalized_candidates=$eligible; selected_count=$eligible.Count;
  runtime_integration_allowed=$false; deformation_accepted=$false;
  evidence_boundary="Hosted source/provenance/Blender normalization + static deformation-readiness only. UE4 technical gate next; no rendered deformation acceptance."
}
$receiptPath=Join-Path $OutputRoot "p1c01_human_wave2_hosted.json"
$receipt | ConvertTo-Json -Depth 16 | Set-Content -LiteralPath $receiptPath -Encoding UTF8
if($eligible.Count -lt 1){ Write-Host ("HUMAN_WAVE2_HOSTED_FAST_REJECT selected=0 receipt="+$receiptPath); exit 0 }
Write-Host ("HUMAN_WAVE2_HOSTED_PASS selected="+$eligible.Count+" deformOnly=true maxZeroWeightRatio="+$manifest.source_policy.max_zero_weight_ratio+" archiveSha="+$archiveSha+" receipt="+$receiptPath)
