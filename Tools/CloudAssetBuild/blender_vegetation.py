#!/usr/bin/env python3
"""Original, source-only, budgeted Shire vegetation. Seven families / 14 FBX LODs.

Ubuntu hosted Blender 4.x only; no Unreal import, runtime placement or device proof.
Reuses the established Shire binary FBX/UV/UCX exporters rather than duplicating
existing OakTree, GardenHedge, GrassClump, Shrub or CommonPine assets.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blender_shire as shire

MODELS = (
    "WeepingWillow", "OrchardApple", "SilverBirch", "RiverAlder",
    "HazelCoppice", "MeadowWildflowers", "RiverReeds",
)
TREES = ("WeepingWillow", "OrchardApple", "SilverBirch", "RiverAlder", "HazelCoppice")
# Height (m), crown radius (m), trunk radius (m), leaves, trunk material.
TREE_DATA = {
    "WeepingWillow": (7.6, 2.65, 0.36, "willow_leaf", "oak_timber"),
    "OrchardApple": (4.8, 2.25, 0.30, "spring_leaf", "oak_timber"),
    "SilverBirch": (7.2, 1.75, 0.22, "birch_leaf", "silver_bark"),
    "RiverAlder": (6.2, 2.25, 0.30, "alder_leaf", "oak_timber"),
    "HazelCoppice": (3.8, 1.85, 0.20, "hazel_leaf", "oak_timber"),
}
shire.PALETTE.update({
    "willow_leaf": (0.22, 0.40, 0.15, 1.0),
    "spring_leaf": (0.25, 0.45, 0.16, 1.0),
    "birch_leaf": (0.38, 0.53, 0.20, 1.0),
    "alder_leaf": (0.16, 0.31, 0.12, 1.0),
    "hazel_leaf": (0.28, 0.41, 0.12, 1.0),
    "silver_bark": (0.73, 0.70, 0.60, 1.0),
    "fruit_red": (0.58, 0.18, 0.10, 1.0),
    "flower_cream": (0.88, 0.79, 0.57, 1.0),
    "flower_lilac": (0.55, 0.38, 0.61, 1.0),
    "reed_green": (0.29, 0.41, 0.13, 1.0),
    "reed_seed": (0.35, 0.27, 0.14, 1.0),
})


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def branch(name, start, end, thick, material, out, lod, tip_ratio=0.53):
    direction = Vector(end) - Vector(start)
    if direction.length <= 0.04:
        raise ValueError("ZERO_BRANCH")
    midpoint = (Vector(start) + Vector(end)) * 0.5
    bpy.ops.mesh.primitive_cone_add(
        vertices=6 if lod else 9,
        radius1=thick,
        radius2=thick * tip_ratio,
        depth=direction.length,
        location=midpoint,
        rotation=direction.to_track_quat("Z", "Y").to_euler(),
    )
    obj = bpy.context.object
    obj.name = name
    return shire.finish(obj, material, out)


def leaf(name, pos, scale, material, out, lod):
    return shire.ico(name, tuple(pos), tuple(scale), material, out, lod == 1)


def make_tree(name, lod, out, rng):
    h, crown, radius, leaf_material, bark = TREE_DATA[name]
    central_top = h * (0.77 if name != "SilverBirch" else 0.88)
    branch("Trunk", (0, 0, 0.05), (0, 0, central_top),
           radius, bark, out, lod, tip_ratio=0.56)
    if name == "HazelCoppice":
        for angle in (0.1, 2.3, 4.4):
            x, y = math.cos(angle), math.sin(angle)
            branch("CoppiceShoot", (0.04*x, 0.04*y, 0.08),
                   (0.72*x, 0.72*y, h*0.77),
                   0.10, bark, out, lod, tip_ratio=0.38)
    n = 10 if lod else 21
    if name == "SilverBirch":
        n = 8 if lod else 17
    if name == "HazelCoppice":
        n = 8 if lod else 17
    for i in range(n):
        angle = (i * 2.3999632297 + rng.uniform(-0.15, 0.15))
        spread = crown * (0.34 + 0.62 * rng.random())
        x = math.cos(angle) * spread
        y = math.sin(angle) * spread
        z = h * (0.69 + 0.22 * rng.random())
        if name == "SilverBirch":
            z += h * 0.04
        stem_start = (0.0, 0.0, h * (0.48 if name != "HazelCoppice" else 0.38))
        stem_end = (x, y, z)
        branch("Branch", stem_start, stem_end, 0.055 if lod else 0.080,
               bark, out, lod, tip_ratio=0.22)
        if name == "WeepingWillow":
            leaf("WillowCurtain", (x, y, z-0.52),
                 (0.35, 0.30, 0.88 if lod else 1.12),
                 leaf_material, out, lod)
            if not lod:
                branch("WillowHangingTwig", stem_end,
                       (x+0.10, y-0.07, z-0.94), 0.025,
                       bark, out, lod, tip_ratio=0.19)
        else:
            radial = 0.51 if name != "SilverBirch" else 0.37
            leaf("CrownCluster", (x, y, z),
                 (radial + (0.12 if not lod else 0),
                  radial * 0.85, radial * (0.87 if name == "SilverBirch" else 1.12)),
                 leaf_material, out, lod)
        if name == "OrchardApple" and (i % 3 == 0):
            leaf("AppleFruit", (x*0.96, y*0.94, z-0.37),
                 (0.095, 0.095, 0.11), "fruit_red", out, lod)
    if name == "SilverBirch" and not lod:
        for z in (0.65, 1.30, 2.45, 3.30):
            shire.box("BarkDarkLenticel", (0, -radius*0.97, z),
                      (radius*1.15, 0.028, 0.045),
                      "charred_basalt", out)
    # Tree collision is intentionally trunk-only; canopy has NO collision.


def make_flower_meadow(lod, out, rng):
    count = 9 if lod else 21
    for i in range(count):
        angle = i * 2.3999632297 + rng.uniform(-0.16, 0.16)
        r = 0.19 + rng.random() * 0.85
        x, y = math.cos(angle) * r, math.sin(angle) * r
        h = 0.24 + rng.random() * 0.21
        branch("FlowerStem", (x, y, 0.015), (x+0.04, y, h),
               0.015, "reed_green", out, lod, tip_ratio=0.46)
        material = "flower_cream" if i % 2 else "flower_lilac"
        petals = 3 if lod else 5
        for k in range(petals):
            a = k * 2 * math.pi / petals
            leaf("FlowerPetal", (x+0.048*math.cos(a), y+0.048*math.sin(a), h),
                 (0.045, 0.035, 0.024), material, out, lod)
        leaf("FlowerCentre", (x, y, h+0.018), (0.032, 0.032, 0.030),
             "reed_seed", out, lod)


def make_river_reeds(lod, out, rng):
    count = 10 if lod else 22
    for i in range(count):
        angle = i * 2.3999632297 + rng.uniform(-0.1, 0.1)
        r = 0.15 + 0.68 * rng.random()
        x, y = r*math.cos(angle), r*math.sin(angle)
        h = 0.72 + 0.75*rng.random()
        top = (x+0.10, y+0.04, h)
        branch("ReedStalk", (x, y, 0.02), top,
               0.023, "reed_green", out, lod, tip_ratio=0.25)
        branch("ReedSeedhead", top, (top[0], top[1], h+0.18),
               0.063, "reed_seed", out, lod, tip_ratio=0.50)
        if not lod:
            leaf("ReedLongLeaf", (x+0.08, y, h*0.43),
                 (0.105, 0.038, h*0.25), "reed_green", out, lod)


def build_one(name, lod, out):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.scale_length = 1.0
    shire.PARTS = []
    rng = random.Random(int.from_bytes(hashlib.sha256(name.encode("ascii")).digest()[:8], "little"))
    if name in TREES:
        make_tree(name, lod, out, rng)
    elif name == "MeadowWildflowers":
        make_flower_meadow(lod, out, rng)
    elif name == "RiverReeds":
        make_river_reeds(lod, out, rng)
    else:
        raise ValueError("UNKNOWN_FAMILY")
    visual_name = "SM_Sh" + name + "_LOD" + str(lod)
    visual = shire.join_visual(visual_name)
    poly_count = len(visual.data.polygons)
    if poly_count <= 0 or poly_count > 15000:
        raise ValueError("SOURCE_POLY_BUDGET_" + name)
    colliders = []
    if name in TREES:
        h, _, radius, _, _ = TREE_DATA[name]
        c = shire.collider(visual_name, (0, 0, h*0.25),
                           (max(0.26, radius*1.8), max(0.26, radius*1.8), h*0.50))
        colliders.append(c)
    bpy.ops.object.select_all(action="DESELECT")
    visual.select_set(True)
    for c in colliders:
        c.select_set(True)
    bpy.context.view_layer.objects.active = visual
    folder = out / "vegetation_fbx"
    folder.mkdir(parents=True, exist_ok=True)
    fbx = folder / (visual_name + ".fbx")
    bpy.ops.export_scene.fbx(
        filepath=str(fbx), use_selection=True, object_types={"MESH"},
        mesh_smooth_type="FACE", add_leaf_bones=False, use_mesh_modifiers=True,
        apply_unit_scale=True, global_scale=1.0, axis_forward="-Y",
        axis_up="Z", path_mode="RELATIVE", embed_textures=False, bake_anim=False,
    )
    with fbx.open("rb") as stream:
        header = stream.read(27)
    if not header.startswith(b"Kaydara FBX Binary") or int.from_bytes(header[23:27], "little") != 7400:
        raise ValueError("UE4_UNSUPPORTED_FBX_VERSION_" + name)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(fbx), use_anim=False)
    imported = [ob for ob in bpy.data.objects if ob.type == "MESH"]
    drawable = [ob for ob in imported if not ob.name.startswith("UCX_")]
    blockers = [ob for ob in imported if ob.name.startswith("UCX_")]
    if len(drawable) != 1 or len(blockers) != len(colliders):
        raise ValueError("BAD_FBX_REIMPORT_OBJECTS_" + name)
    mesh = drawable[0].data
    if len(mesh.polygons) < 1 or len(mesh.polygons) > 15000 or not mesh.uv_layers:
        raise ValueError("BAD_FBX_REIMPORT_UV_OR_POLYS_" + name)
    if any(poly.area <= 1e-8 for poly in mesh.polygons):
        raise ValueError("BAD_FBX_REIMPORT_DEGENERATE_FACE_" + name)
    return {
        "family": name, "lod": lod, "path": "vegetation_fbx/" + fbx.name,
        "bytes": fbx.stat().st_size, "sha256": digest(fbx),
        "source_polygons": poly_count, "reimport_polygons": len(mesh.polygons),
        "reimport_uv_layers": len(mesh.uv_layers),
        "material_slots": len(drawable[0].material_slots),
        "trunk_collision_ucx": len(blockers),
        "collision_intent": "TRUNK_ONLY" if name in TREES else "NO_COLLISION",
        "source_only": True,
    }


def main(out: Path):
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    assets = [build_one(name, lod, out) for name in MODELS for lod in (0, 1)]
    receipt = {
        "id": "P1C01_SHIRE_ORIGINAL_VEGETATION_7_FAMILIES_V1",
        "producer_sha256": digest(Path(__file__)),
        "blender_version": bpy.app.version_string,
        "license": "ORIGINAL_PROJECT_PROCEDURAL_GEOMETRY",
        "families": list(MODELS), "family_count": len(MODELS),
        "binary_fbx_count": len(assets), "objects": assets,
        "runtime_imported": False, "ue4_import_proof": None, "pie_proof": None,
        "visual_acceptance": None, "target_device_proof": None,
        "quality_boundary": "BLENDER_PHYSICAL_FBX_REIMPORT_QC_ONLY",
    }
    (out/"vegetation_receipt.json").write_text(
        json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
    print("SHIRE_VEGETATION_SOURCE_PHYSICAL_PASS families={} binary_fbx={}".format(
        len(MODELS), len(assets)))


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    if len(args) != 2 or args[0] != "--out":
        raise SystemExit("usage: blender -b --python blender_vegetation.py -- --out PATH")
    main(Path(args[1]))
