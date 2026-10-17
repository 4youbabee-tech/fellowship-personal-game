"""Prepare a hash-verified CC0 rigged GLB as Skeletal FBX for Unreal 4.27.

Run with Blender's bundled Python, not the system interpreter:
blender -b --python convert_licensed_glb_rig_to_ue427_fbx.py -- --glb INPUT --manifest LICENSE.json --output Saved/FBX
No user GLB is bundled, downloaded or imported by this source-only tool.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import bpy


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--glb", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--require-clips", action="store_true")
    args = parser.parse_args(argv)
    glb = Path(args.glb).resolve()
    manifest = Path(args.manifest).resolve()
    out = Path(args.output).resolve()
    if glb.suffix.lower() != ".glb" or not glb.is_file():
        raise ValueError("GLB_SOURCE_REQUIRED")
    licence = json.loads(manifest.read_text(encoding="utf-8"))
    for field in ("source_url", "creator", "license", "source_sha256", "source_filename"):
        if not str(licence.get(field, "")).strip():
            raise ValueError("GLB_PROVENANCE_MISSING_" + field)
    if licence["license"].upper() not in ("CC0", "CC0-1.0", "PUBLIC-DOMAIN"):
        raise ValueError("GLB_LICENSE_QUARANTINE_ONLY")
    if glb.name != licence["source_filename"] or sha256(glb) != licence["source_sha256"].lower():
        raise ValueError("GLB_SOURCE_HASH_MISMATCH")

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(glb))
    rigs = [obj for obj in bpy.data.objects if obj.type == "ARMATURE"]
    skinned = [obj for obj in bpy.data.objects if obj.type == "MESH" and any(
        mod.type == "ARMATURE" and mod.object in rigs for mod in obj.modifiers)]
    if len(rigs) != 1 or not skinned:
        raise ValueError("GLB_SKINNED_ARMATURE_REQUIRED")
    rig = rigs[0]
    bones = [bone for bone in rig.data.bones if bone.use_deform]
    if not (18 <= len(bones) <= 180):
        raise ValueError("GLB_RIG_BONE_BUDGET")
    triangles = 0
    weighted = 0
    vertex_count = 0
    max_influences = 0
    for mesh in skinned:
        if not mesh.data.uv_layers:
            raise ValueError("GLB_SKINNED_UVS_REQUIRED:" + mesh.name)
        triangles += sum(max(0, len(face.vertices) - 2) for face in mesh.data.polygons)
        for v in mesh.data.vertices:
            weights = [g.weight for g in v.groups if g.weight > 0.0001]
            vertex_count += 1
            max_influences = max(max_influences, len(weights))
            if weights:
                weighted += 1
            if not weights or len(weights) > 4 or abs(sum(weights) - 1.0) > 0.02:
                raise ValueError("GLB_VERTEX_SKIN_INVALID:" + mesh.name)
    if vertex_count < 1000 or vertex_count != weighted or triangles > 65000:
        raise ValueError("GLB_TOPOLOGY_BUDGET")
    for image in bpy.data.images:
        if image.size[0] > 2048 or image.size[1] > 2048:
            raise ValueError("GLB_TEXTURE_2K_BUDGET")
    actions = sorted(a.name for a in bpy.data.actions)
    if args.require_clips and not all(any(name in act.lower() for act in actions)
                                      for name in ("idle", "walk", "turn")):
        raise ValueError("GLB_IDLE_WALK_TURN_MISSING")

    out.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    for mesh in skinned:
        mesh.select_set(True)
    bpy.context.view_layer.objects.active = rig
    target = out / (glb.stem + "_UE427_SK.fbx")
    bpy.ops.export_scene.fbx(
        filepath=str(target), use_selection=True, object_types={"MESH", "ARMATURE"},
        use_mesh_modifiers=True, bake_anim=True, bake_anim_use_all_actions=True,
        add_leaf_bones=False, use_armature_deform_only=True, mesh_smooth_type="FACE",
        axis_forward="-Y", axis_up="Z", apply_unit_scale=True,
        path_mode="COPY", embed_textures=False)
    if not target.is_file() or target.stat().st_size < 20480:
        raise ValueError("GLB_FBX_EXPORT_INVALID")
    receipt = {
        "source_url": licence["source_url"], "creator": licence["creator"],
        "license": licence["license"], "source_sha256": licence["source_sha256"],
        "fbx_sha256": sha256(target), "fbx": target.name,
        "deform_bones": len(bones), "triangles": triangles,
        "vertices": vertex_count, "weighted_vertices": weighted,
        "max_skin_influences": max_influences, "animation_actions": actions,
        "ue_imported": False, "pie_deformation_tested": False,
        "visually_accepted": False,
    }
    (out / (glb.stem + "_source_receipt.json")).write_text(
        json.dumps(receipt, indent=2), encoding="utf-8")
    print("GLB_SKINNED_FBX_SOURCE_QC_PASS " + json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    index = sys.argv.index("--") if "--" in sys.argv else -1
    main(sys.argv[index + 1:] if index >= 0 else [])
