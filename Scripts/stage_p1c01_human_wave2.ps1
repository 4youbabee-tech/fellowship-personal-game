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
if($pageText -notmatch "Rigged Low Poly Character Base Model|Rigged.*Character"){ throw "HUMAN_WAVE2_SOURCE_PAGE_RIGGED_MARKER_MISSING" }

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

# Recover skinning only when the public source is missing real DEF limb weights.
# Never treat a Rigify control or a mesh-parent relationship as deformation proof.
import re
if len(armatures) != 1:
    raise RuntimeError("HUMAN_WAVE2_SKIN_REPAIR_MULTIPLE_ARMATURES")
source_armature = armatures[0]
bound_meshes = [m for m in meshes if any(
    mod.type == "ARMATURE" and mod.object == source_armature for mod in m.modifiers
)]
if not bound_meshes:
    raise RuntimeError("HUMAN_WAVE2_SKIN_REPAIR_NO_BOUND_MESH")
# This CC0 base model is deliberately split into several small, already-bound
# body components. A per-component size gate misclassified that valid family
# before the actual skin/deformation checks ever ran. Treat it as one
# armature-bound character only when the aggregate geometry is substantial;
# the later exported-FBX bilateral influence gate remains mandatory.
bound_vertex_count = sum(len(m.data.vertices) for m in bound_meshes)
if bound_vertex_count < 1000:
    raise RuntimeError("HUMAN_WAVE2_SKIN_REPAIR_BOUND_CHARACTER_TOO_SMALL")

def original_def_influence(mesh_group):
    deform = {bone.name for bone in source_armature.data.bones if bone.use_deform}
    weighted = set()
    for mesh in mesh_group:
        names = {group.index: group.name for group in mesh.vertex_groups}
        for vertex in mesh.data.vertices:
            for membership in vertex.groups:
                name = names.get(membership.group)
                if membership.weight > 0.00001 and name in deform:
                    weighted.add(name)
    return weighted

source_def_weights = original_def_influence(bound_meshes)
skin_rebuilt = False
# The baseline CC0 hero FBX reimport had only four weighted bones. Rebuild
# the principal humanoid skin from the *existing licensed geometry/skeleton*,
# not a substitute dummy rig. Blender bone-heat failures remain hard failures.
if len(source_def_weights) < 13:
    original_worlds = {mesh: mesh.matrix_world.copy() for mesh in bound_meshes}
    for mesh in bound_meshes:
        for modifier in list(mesh.modifiers):
            if modifier.type == "ARMATURE":
                mesh.modifiers.remove(modifier)
        mesh.vertex_groups.clear()
        mesh.parent = None
        mesh.matrix_world = original_worlds[mesh]
    bpy.ops.object.select_all(action="DESELECT")
    source_armature.hide_set(False)
    source_armature.select_set(True)
    for mesh in bound_meshes:
        mesh.hide_set(False)
        mesh.select_set(True)
    bpy.context.view_layer.objects.active = source_armature
    try:
        result = bpy.ops.object.parent_set(type="ARMATURE_AUTO", keep_transform=True)
    except RuntimeError as exc:
        raise RuntimeError("HUMAN_WAVE2_SKIN_REPAIR_BONE_HEAT_FAILED") from exc
    if "FINISHED" not in result:
        raise RuntimeError("HUMAN_WAVE2_SKIN_REPAIR_PARENT_FAILED")
    if not all(any(mod.type == "ARMATURE" and mod.object == source_armature
                   for mod in mesh.modifiers) for mesh in bound_meshes):
        raise RuntimeError("HUMAN_WAVE2_SKIN_REPAIR_BINDING_MISSING")
    if len(original_def_influence(bound_meshes)) < 13:
        raise RuntimeError("HUMAN_WAVE2_SKIN_REPAIR_INSUFFICIENT_DEFORM_WEIGHTS")
    skin_rebuilt = True
    print("HUMAN_WAVE2_AUTO_REBIND_BOUND_CHARACTER meshes=" +
          str(len(bound_meshes)) + " vertices=" + str(bound_vertex_count), flush=True)

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

# Audit the EXPORTED FBX, not just the original .blend: Rigify control
# weights may disappear during deform-only export while total weighted
# vertices still looks healthy. A technical winner must move real limbs.
import re
bpy.ops.wm.read_factory_settings(use_empty=True)
if "FINISHED" not in bpy.ops.import_scene.fbx(filepath=args.output):
    raise RuntimeError("normalized FBX reimport failed")
post_armatures=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"]
post_meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
if len(post_armatures)!=1:
    raise RuntimeError("normalized FBX armature cardinality invalid")
reimport_arm=post_armatures[0]
influence={}
for m in post_meshes:
    if not any(mod.type=="ARMATURE" and mod.object==reimport_arm for mod in m.modifiers):
        continue
    by_index={g.index:g.name for g in m.vertex_groups}
    for v in m.data.vertices:
        for g in v.groups:
            if g.weight>0.00001 and g.group in by_index:
                name=by_index[g.group]
                influence[name]=influence.get(name,0.0)+float(g.weight)
required_roles=("upperarm","forearm","thigh","shin","foot","hand","head")
def role_of(name):
    stem=re.sub(r"[^a-z0-9]","",name.lower())
    if "forearm" in stem or "lowerarm" in stem:return "forearm"
    if "upperarm" in stem or "uparm" in stem:return "upperarm"
    if "thigh" in stem or "upleg" in stem:return "thigh"
    if "shin" in stem or "calf" in stem or "lowerleg" in stem:return "shin"
    if "foot" in stem:return "foot"
    if "hand" in stem:return "hand"
    if "head" in stem:return "head"
    return None
weighted_bone_roles=set()
for bone in reimport_arm.data.bones:
    if influence.get(bone.name,0.0)<=1e-6:continue
    role=role_of(bone.name)
    if not role:continue
    name=bone.name.lower()
    side=("L" if re.search(r"(?:^|[.:_ -])(?:l|left)(?:$|[.:_ -])",name) or "left" in name
          else "R" if re.search(r"(?:^|[.:_ -])(?:r|right)(?:$|[.:_ -])",name) or "right" in name
          else None)
    if role=="head":weighted_bone_roles.add("head")
    elif side:weighted_bone_roles.add(side+"_"+role)
needed={"head"}|{side+"_"+role for side in ("L","R") for role in required_roles if role!="head"}
missing_influence=sorted(needed-weighted_bone_roles)
print("HUMAN_WAVE2_EXPORTED_SKIN_QC missing="+",".join(missing_influence)+" weighted_bones="+str(len(influence)),flush=True)

receipt={
    "armature_count":len(armatures),"mesh_count":len(meshes),"bone_count":bone_count,
    "deform_bone_count":deform_bone_count,
    "vertex_count":vertex_count,"weighted_vertex_count":weighted,
    "zero_weight_vertex_count":zero_weight,"uv_layer_count":uv_layers,
    "finite_bounds":finite_bounds,"joint_name_coverage":coverage,
    "source_kind":args.source_kind,
    "bound_character_mesh_count":len(bound_meshes),
    "bound_character_vertex_count":bound_vertex_count,
    "auto_skin_rebuilt":skin_rebuilt,
    "source_def_weighted_bones_before_repair":len(source_def_weights),
    "exported_weighted_bone_count":len(influence),
    "exported_missing_limb_influence":missing_influence}
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

$ranked=@($characterSources | Sort-Object @{Expression={if($_.extension -eq ".blend"){0}else{1}}}, @{Expression={$_.bytes}})
$selectedSources=@($ranked | Select-Object -First ([int]$manifest.source_policy.max_ue4_candidates))
$normalized=@(); $index=0
foreach($src in $selectedSources){
  $index++
  $outName=("candidate_{0:D2}.fbx" -f $index)
  $outPath=Join-Path $normalizedRoot $outName
  $readinessPath=Join-Path $normalizedRoot ("candidate_{0:D2}_readiness.json" -f $index)
  if($src.extension -eq ".blend"){
    & $blenderCommand.Source --background ([string]$src.extracted_path) --python $pythonPath -- --source ([string]$src.extracted_path) --source-kind ".blend" --output $outPath --receipt $readinessPath
  }else{
    & $blenderCommand.Source --background --factory-startup --python $pythonPath -- --source ([string]$src.extracted_path) --source-kind ".fbx" --output $outPath --receipt $readinessPath
  }
  if([int]$LASTEXITCODE -ne 0){ throw "HUMAN_WAVE2_NORMALIZE_FAIL entry=$($src.entry)" }

  $version=Get-FbxBinaryVersion $outPath
  if($version -le 0 -or $version -gt [int]$manifest.source_policy.fbx_version_ceiling){ throw "HUMAN_WAVE2_NORMALIZED_FBX_VERSION_FAIL entry=$($src.entry) version=$version" }
  $normSha=(Get-FileHash -LiteralPath $outPath -Algorithm SHA256).Hash.ToLowerInvariant()
  $readiness=Get-Content -LiteralPath $readinessPath -Raw | ConvertFrom-Json
  $ascii=[Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes($outPath))
  $staticPass=$ascii.Contains("Geometry") -and $ascii.Contains("Model") -and $ascii.Contains("LimbNode") -and $ascii.Contains("Skin") -and $ascii.Contains("Cluster")
  $zeroWeightRatio=if([int]$readiness.vertex_count -gt 0){ [double]$readiness.zero_weight_vertex_count / [double]$readiness.vertex_count }else{ 1.0 }
  $qualityReasons=@()
  if(-not $staticPass){ $qualityReasons+="MISSING_STATIC_RIG_MARKERS" }
  if([int]$readiness.deform_bone_count -le 0){ $qualityReasons+="ZERO_DEFORM_BONES" }
  if([int]$readiness.weighted_vertex_count -le 0){ $qualityReasons+="ZERO_WEIGHTED_VERTICES" }
  if([int]$readiness.uv_layer_count -le 0){ $qualityReasons+="MISSING_UV_LAYER" }
  if(-not [bool]$readiness.finite_bounds){ $qualityReasons+="NONFINITE_BOUNDS" }
  if($zeroWeightRatio -gt [double]$manifest.source_policy.max_zero_weight_ratio){ $qualityReasons+="EXCESS_ZERO_WEIGHT_RATIO" }
  if(@($readiness.exported_missing_limb_influence).Count -gt 0){ $qualityReasons+="EXPORTED_LIMB_SKIN_INFLUENCE_MISSING" }
  $qualityPass=$qualityReasons.Count -eq 0
  $normalized += [pscustomobject]@{
    source_entry=[string]$src.entry; source_kind=[string]$src.extension; source_sha256=[string]$src.sha256; source_bytes=[int64]$src.bytes;
    normalized_relative_path=("normalized/"+$outName); normalized_sha256=$normSha; normalized_bytes=[int64](Get-Item $outPath).Length;
    normalized_fbx_version=[int]$version; static_rig_markers=[bool]$staticPass;
    readiness_relative_path=("normalized/"+[IO.Path]::GetFileName($readinessPath));
    armature_count=[int]$readiness.armature_count; mesh_count=[int]$readiness.mesh_count; bone_count=[int]$readiness.bone_count;
    deform_bone_count=[int]$readiness.deform_bone_count;
    vertex_count=[int]$readiness.vertex_count; weighted_vertex_count=[int]$readiness.weighted_vertex_count;
    zero_weight_vertex_count=[int]$readiness.zero_weight_vertex_count; zero_weight_ratio=$zeroWeightRatio; uv_layer_count=[int]$readiness.uv_layer_count;
    finite_bounds=[bool]$readiness.finite_bounds; joint_name_coverage=$readiness.joint_name_coverage;
    quality_pass=[bool]$qualityPass; quality_reasons=$qualityReasons
  }
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
if($eligible.Count -lt 1){ throw "HUMAN_WAVE2_HOSTED_EXHAUSTED receipt=$receiptPath" }
Write-Host ("HUMAN_WAVE2_HOSTED_PASS selected="+$eligible.Count+" deformOnly=true maxZeroWeightRatio="+$manifest.source_policy.max_zero_weight_ratio+" archiveSha="+$archiveSha+" receipt="+$receiptPath)
