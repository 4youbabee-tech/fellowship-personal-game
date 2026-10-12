#!/usr/bin/env python3
"""Whole-game source-only support kit: 28 canonical regions x 2 LOD = 56 FBX.

Uses existing original modular primitives, binary FBX7400 exporter and Blender
reimport. These are supporting modular region props, NOT hero landmarks, player
routes, skeletal characters, licensed external content or UE imported assets.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import blender_shire as sh  # Reuse established UV/UCX/export shape helpers.

PLAN = ROOT / "Data" / "WholeGameRegionProductionPacketsV1.json"
GROUPS = {
    "pastoral": ("SHIRE_HOBBITON", "BAG_END", "BREE", "EDORAS_MEDUSELD",
                 "PELENNOR_FIELDS", "GREY_HAVENS"),
    "woodland": ("RIVENDELL", "LOTHLORIEN", "FANGORN", "ITHILIEN"),
    "highland": ("WEATHERTOP", "CARADHRAS", "EMYN_MUIL", "HENNETH_ANNUN"),
    "wetland": ("ANDUIN_AMON_HEN", "DEAD_MARSHES"),
    "masonry": ("MORIA", "HELMS_DEEP", "MINAS_TIRITH", "OSGILIATH",
                "PATHS_OF_THE_DEAD"),
    "darkstone": ("ISENGARD_ORTHANC", "MINAS_MORGUL", "CIRITH_UNGOL",
                  "SHELOBS_LAIR", "BLACK_GATE_MORANNON",
                  "MORDOR_GORGOROTH", "MOUNT_DOOM"),
}
GROUP_FOR = {key: group for group, keys in GROUPS.items() for key in keys}
MATERIAL_FOR = {
    "pastoral": "oak_timber", "woodland": "shire_meadow",
    "highland": "mossy_stone", "wetland": "shire_earth",
    "masonry": "mossy_stone", "darkstone": "charred_basalt",
}


def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authored_geometry(region: str, lod: int, ordinal: int, output: Path) -> list:
    """Distinct bounded supporting silhouettes, no new lore/hero-asset claim."""
    category = GROUP_FOR[region]
    basic = MATERIAL_FOR[category]
    detail = lod == 0
    shift = ((ordinal % 5) - 2) * 0.08
    blocks = []
    if category == "pastoral":
        # Fence/garden or dock-side timber support module.
        for x in (-1.05, 1.05):
            sh.box("TimberUpright", (x, 0, 0.83), (0.16, 0.18, 1.66),
                   "oak_timber", output)
            blocks.append(((x, 0, 0.83), (0.16, 0.18, 1.66)))
        sh.box("TimberCrossRail", (0, 0, 1.31), (2.28, 0.13, 0.14),
               "oak_timber", output)
        if detail:
            sh.box("LowSupportRail", (0, 0, 0.40), (2.25, 0.11, 0.11),
                   "oak_timber", output)
    elif category == "woodland":
        sh.cylinder("WoodlandBase", (0, 0, 0.69), 0.19, 1.38,
                    "oak_timber", output, 10 if detail else 6)
        blocks.append(((0, 0, 0.69), (0.50, 0.50, 1.38)))
        sh.ico("BoundedShrub", (shift, 0, 1.48),
               (0.90, 0.72, 0.69), "shire_meadow", output, not detail)
        if detail:
            sh.ico("SideFoliage", (0.54, 0.16, 1.20),
                   (0.44, 0.42, 0.52), "shire_meadow", output, False)
    elif category == "wetland":
        sh.box("RaisedStonePath", (0, 0, 0.19), (2.35, 1.24, 0.38),
               "mossy_stone", output)
        blocks.append(((0, 0, 0.19), (2.35, 1.24, 0.38)))
        for x in ((-0.92, 0.92) if detail else (-0.92,)):
            sh.cylinder("WaterEdgeStake", (x, -0.56, 0.60),
                        0.08, 1.20, "oak_timber", output, 6)
    elif category == "highland":
        for n, x in enumerate((-0.65, 0.38)):
            h = 0.95 + 0.19 * n + abs(shift)
            sh.box("SlopedRockCourse", (x, 0, h / 2),
                   (1.28, 1.00, h), basic, output,
                   0.02 if detail else 0)
            blocks.append(((x, 0, h / 2), (1.28, 1.00, h)))
        if detail:
            sh.box("Capstone", (0.30, 0.05, 1.19),
                   (0.78, 0.92, 0.19), basic, output)
    elif category == "masonry":
        for x in (-1.02, 1.02):
            sh.box("BrokenStonePier", (x, 0, 1.05 + shift),
                   (0.60, 0.68, 2.10), basic, output)
            blocks.append(((x, 0, 1.05 + shift), (0.60, 0.68, 2.10)))
        sh.box("WallLintel", (0, 0, 2.13),
               (2.70, 0.69, 0.28), basic, output)
        blocks.append(((0, 0, 2.13), (2.70, 0.69, 0.28)))
        if detail:
            sh.box("CarvedMasonryEdge", (0, -0.37, 2.20),
                   (2.58, 0.09, 0.08), basic, output)
    else:
        for n in range(2 if lod else 3):
            x = (n - 1) * 0.70
            height = 0.75 + (n % 2) * 0.34 + abs(shift)
            sh.box("DarkRockSupport", (x, 0, height / 2),
                   (0.85, 1.00, height), "charred_basalt", output,
                   0.01 if detail else 0)
            blocks.append(((x, 0, height / 2), (0.85, 1.00, height)))
    return blocks


def export_one(region: str, lod: int, ordinal: int, output: Path) -> dict:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sh.PARTS = []
    blockers = authored_geometry(region, lod, ordinal, output)
    name = "SM_Region_" + region + "_Support_LOD" + str(lod)
    mesh = sh.join_visual(name)
    polygons = len(mesh.data.polygons)
    if polygons < 1 or polygons > 12000:
        raise ValueError("REGION_SOURCE_POLYGON_BUDGET")
    # No permanent gameplay collision decision is made from author-space UCX.
    for i, (center, dimensions) in enumerate(blockers):
        sh.collider(name, center, dimensions, i)
    mesh_dir = output / "regional_meshes"
    mesh_dir.mkdir(parents=True, exist_ok=True)
    path = mesh_dir / (name + ".fbx")
    bpy.ops.object.select_all(action="DESELECT")
    mesh.select_set(True)
    for ob in bpy.data.objects:
        if ob.name.startswith("UCX_" + name + "_"):
            ob.select_set(True)
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.export_scene.fbx(
        filepath=str(path), use_selection=True, object_types={"MESH"},
        mesh_smooth_type="FACE", use_mesh_modifiers=True,
        apply_unit_scale=True, global_scale=1.0,
        axis_forward="-Y", axis_up="Z", path_mode="RELATIVE",
        bake_anim=False, embed_textures=False)
    header = path.read_bytes()[:27]
    if not header.startswith(b"Kaydara FBX Binary") or int.from_bytes(header[23:27], "little") != 7400:
        raise ValueError("REGION_FBX_NOT_BINARY_7400")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path), use_anim=False)
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    original = [o for o in meshes if not o.name.startswith("UCX_")]
    colliders = [o for o in meshes if o.name.startswith("UCX_")]
    if len(original) != 1 or len(colliders) != len(blockers):
        raise ValueError("REGION_FBX_REIMPORT_OBJECT_MISMATCH")
    actual = original[0].data
    if not actual.uv_layers or not 0 < len(actual.polygons) <= 12000:
        raise ValueError("REGION_FBX_UV_OR_TOPOLOGY_INVALID")
    if any(p.area <= 0.00000001 for p in actual.polygons):
        raise ValueError("REGION_FBX_DEGENERATE_FACE")
    return {"region_id": region, "category": GROUP_FOR[region], "lod": lod,
            "path": "regional_meshes/" + path.name, "bytes": path.stat().st_size,
            "sha256": checksum(path), "reimport_polygons": len(actual.polygons),
            "uv_layers": len(actual.uv_layers), "collider_count": len(colliders),
            "target": "UE4.27.2", "format": "FBX_BINARY_7400",
            "unreal_imported": False, "visual_accepted": False}


def main(destination: Path) -> None:
    packets = json.loads(PLAN.read_text(encoding="utf-8"))["packets"]
    regions = [p["region_id"] for p in packets]
    if len(regions) != 28 or len(set(regions)) != 28 or set(regions) != set(GROUP_FOR):
        raise ValueError("CANONICAL_28_REGION_MAP_DRIFT")
    destination.mkdir(parents=True, exist_ok=True)
    objects = [export_one(r, lod, i, destination)
               for i, r in enumerate(regions) for lod in (0, 1)]
    receipt = {
        "id": "WHOLE_GAME_ORIGINAL_28_REGION_SUPPORT_WAVE_V1",
        "status": "BLENDER_REIMPORTED_BINARY_SOURCE_ONLY",
        "provenance": "ORIGINAL_PROJECT_PROCEDURAL",
        "generator_sha256": checksum(Path(__file__)),
        "region_packet_sha256": checksum(PLAN),
        "blender_version": bpy.app.version_string,
        "region_count": 28, "fbx_count": len(objects),
        "objects": objects, "warehouse_persisted": False,
        "unreal_imported": False, "hero_assets": False,
        "pie_proof": None, "device_fps": None,
    }
    (destination / "regional_fbx_receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("WHOLEGAME_ORIGINAL_REGION_FBX_GENERATED regions=28 files=56 blender=" + bpy.app.version_string)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) != 2 or args[0] != "--out":
        raise SystemExit("usage: blender -b --python blender_regions.py -- --out OUTPUT")
    main(Path(args[1]).resolve())
