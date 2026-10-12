#!/usr/bin/env python3
"""70 distinct original region-specific modular families x 2 LOD (SOURCE ONLY)."""
import hashlib
import json
import sys
from pathlib import Path
import bpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import blender_shire as sh
import blender_regions as regions

PLAN = ROOT / "Data/WholeGameRegionProductionPacketsV1.json"
PART_NAMES = ("RouteStone", "BoundaryMarker", "WorkStation", "EnvironmentalCluster",
              "WayfindingStructure")
FAMILIES = {
    "pastoral": ("oak_timber", "shire_earth"),
    "woodland": ("oak_timber", "shire_meadow"),
    "highland": ("mossy_stone", "shire_earth"),
    "wetland": ("mossy_stone", "oak_timber"),
    "masonry": ("mossy_stone", "charred_basalt"),
    "darkstone": ("charred_basalt", "mossy_stone"),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_geometry(region, role, lod, ordinal, out):
    category = regions.GROUP_FOR[region]
    base, trim = FAMILIES[category]
    fine = lod == 0
    # Five FUNCTIONALLY different silhouettes, not copies under other filenames.
    height = 0.88 + ordinal * 0.024
    width = 1.10 + (ordinal % 7) * 0.09
    if role == "RouteStone":
        sh.box("RouteDeck", (0, 0, 0.16), (2.4, width, 0.32), base, out)
        if fine:
            for x in (-0.72, 0, 0.72):
                sh.box("JointStone", (x, 0, 0.34), (0.09, width, 0.05), trim, out)
        collider = ((0, 0, 0.16), (2.4, width, 0.32))
    elif role == "BoundaryMarker":
        for x in (-width, width):
            sh.box("BoundaryPier", (x, 0, height / 2), (0.23, 0.35, height), base, out)
        sh.box("BoundaryTop", (0, 0, height - 0.09), (width * 2.25, 0.35, 0.18), trim, out)
        if fine:
            sh.box("BoundaryLowRail", (0, 0, 0.38), (width * 2, 0.18, 0.13), trim, out)
        collider = ((0, 0, height / 2), (width * 2.3, 0.38, height))
    elif role == "WorkStation":
        sh.box("WorkSurface", (0, 0, height), (width * 1.5, 0.83, 0.13), base, out)
        for x in (-width * 0.63, width * 0.63):
            sh.box("WorkLeg", (x, 0, height / 2), (0.17, 0.52, height), trim, out)
        if fine:
            sh.box("SideSupplyShelf", (0, -0.38, 0.55), (width * 1.15, 0.2, 0.11), base, out)
        collider = ((0, 0, height / 2), (width * 1.5, 0.83, height))
    elif role == "EnvironmentalCluster":
        sh.box("ClusterGround", (0, 0, 0.12), (width * 2.1, 1.3, 0.24), base, out)
        for n in range(3 if fine else 2):
            x = (n - 1) * width * 0.53
            z = 0.43 + n * 0.11 + ordinal * 0.01
            sh.box("ClusterForm", (x, 0, z), (0.43, 0.5, z * 1.42), trim, out,
                   0.03 if fine else 0)
        collider = ((0, 0, 0.27), (width * 2.1, 1.3, 0.54))
    else:
        sh.box("WaymarkBase", (0, 0, 0.14), (0.58, 0.58, 0.28), base, out)
        sh.box("WaymarkMast", (0, 0, height), (0.19, 0.19, height * 2), trim, out)
        sh.box("DirectionPlate", (0.25, 0, height * 1.58),
               (1.05 + (ordinal % 4) * 0.13, 0.18, 0.26), base, out)
        if fine:
            sh.box("SecondaryDirection", (-0.23, 0, height * 1.25), (0.86, 0.15, 0.19), trim, out)
        collider = ((0, 0, height), (0.58, 0.58, height * 2))
    return collider


def export_one(region, role, lod, ordinal, out):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sh.PARTS = []
    collider = source_geometry(region, role, lod, ordinal, out)
    name = "SM_WG_" + region + "_" + role + "_LOD" + str(lod)
    mesh = sh.join_visual(name)
    source_polygons = len(mesh.data.polygons)
    if not 0 < source_polygons <= 12000:
        raise RuntimeError("WAVE140_SOURCE_POLYGON_BUDGET")
    sh.collider(name, *collider, 0)
    folder = out / "wave140_meshes"
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / (name + ".fbx")
    bpy.ops.object.select_all(action="DESELECT")
    mesh.select_set(True)
    for obj in bpy.data.objects:
        if obj.name.startswith("UCX_" + name + "_"):
            obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.export_scene.fbx(filepath=str(dest), use_selection=True,
         object_types={"MESH"}, mesh_smooth_type="FACE", use_mesh_modifiers=True,
         apply_unit_scale=True, global_scale=1.0, axis_forward="-Y",
         axis_up="Z", path_mode="RELATIVE", bake_anim=False, embed_textures=False)
    header = dest.read_bytes()[:27]
    if not header.startswith(b"Kaydara FBX Binary") or int.from_bytes(header[23:27], "little") != 7400:
        raise RuntimeError("WAVE140_FBX_BINARY_VERSION")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(dest), use_anim=False)
    objects = [x for x in bpy.data.objects if x.type == "MESH"]
    visible = [x for x in objects if not x.name.startswith("UCX_")]
    blockers = [x for x in objects if x.name.startswith("UCX_")]
    if len(visible) != 1 or len(blockers) != 1:
        raise RuntimeError("WAVE140_REIMPORT_UCX")
    geometry = visible[0].data
    if not geometry.uv_layers or not 0 < len(geometry.polygons) <= 12000 or any(p.area <= 1e-8 for p in geometry.polygons):
        raise RuntimeError("WAVE140_REIMPORT_GEOMETRY")
    return {"region_id": region, "role": role, "lod": lod,
            "path": "wave140_meshes/" + dest.name, "sha256": sha(dest),
            "bytes": dest.stat().st_size, "reimport_polygons": len(geometry.polygons),
            "uv_layers": len(geometry.uv_layers), "collider_count": 1,
            "format": "FBX_BINARY_7400", "unreal_imported": False}


def main(out):
    packets = json.loads(PLAN.read_text(encoding="utf-8"))["packets"]
    names = [x["region_id"] for x in packets]
    if len(names) != 28 or len(set(names)) != 28 or set(names) != set(regions.GROUP_FOR):
        raise RuntimeError("WAVE140_REGION_AUTHORITY_DRIFT")
    # 28x2 = 56 foundational families plus 14 deliberately selected work/route families.
    pairs = [(region, PART_NAMES[ordinal % 5]) for ordinal, region in enumerate(names)]
    pairs += [(region, PART_NAMES[(ordinal + 1) % 5]) for ordinal, region in enumerate(names)]
    pairs += [(region, PART_NAMES[(ordinal + 2) % 5]) for ordinal, region in enumerate(names[:14])]
    if len(pairs) != 70 or len(set(pairs)) != 70:
        raise RuntimeError("WAVE140_FAMILY_DUPLICATE")
    outputs = [export_one(region, role, lod, idx, out)
               for idx, (region, role) in enumerate(pairs) for lod in (0, 1)]
    hashes = [row["sha256"] for row in outputs]
    if len(outputs) != 140 or len(set(hashes)) != 140:
        raise RuntimeError("WAVE140_NONUNIQUE_BINARY_PAYLOADS")
    receipt = {"schema_version": 1, "stage": "SOURCE_GENERATED_BLENDER_REIMPORT_ONLY",
               "provenance": "ORIGINAL_PROJECT_PROCEDURAL",
               "generator_sha256": sha(__file__), "region_plan_sha256": sha(PLAN),
               "families": len(pairs), "fbx_count": 140, "regions": len(names),
               "objects": outputs, "warehouse_persisted": False,
               "unreal_imported": False, "world_placed": False,
               "pie_tested": False, "device_tested": False, "visual_accepted": False}
    (out / "wave140_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("WHOLEGAME_140_DISTINCT_FBX_GENERATED families=70 files=140 regions=28")


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) != 2 or args[0] != "--out":
        raise SystemExit("usage: blender -b --python blender_wave140.py -- --out DEST")
    main(Path(args[1]).resolve())
