#!/usr/bin/env python3
"""28 distinct P1C01 modular detail families x LOD0+LOD1, SOURCE ONLY.

Collision authoring is approximate static support; interactable door hinges and
ferry walkability still require UE4 PIE, nav and save/restore evidence.
"""
import hashlib
import json
import sys
from pathlib import Path
import bpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import blender_shire as sh

KITS = [
    ("DoorIronHinge", "bracket", "oak_timber"),
    ("DoorLatchPlate", "bracket", "mossy_stone"),
    ("DoorThreshold", "slab", "mossy_stone"),
    ("RoundFrameMolding", "arch", "oak_timber"),
    ("WindowShutter", "panel", "oak_timber"),
    ("EntryBootRack", "shelf", "oak_timber"),
    ("EntryCoatHooks", "bracket", "oak_timber"),
    ("PantryStackedShelves", "shelf", "oak_timber"),
    ("KitchenUtensilRail", "bracket", "oak_timber"),
    ("HearthToolHolder", "stand", "charred_basalt"),
    ("OpenBookStand", "stand", "oak_timber"),
    ("CandleBracket", "bracket", "charred_basalt"),
    ("GardenWaterTray", "slab", "mossy_stone"),
    ("GardenPotCluster", "cluster", "shire_earth"),
    ("OrchardLadderFrame", "ladder", "oak_timber"),
    ("FenceCornerBrace", "panel", "oak_timber"),
    ("CountryRoadDrain", "slab", "mossy_stone"),
    ("FootpathMarkerStone", "stand", "mossy_stone"),
    ("RoadsideReedCluster", "cluster", "shire_meadow"),
    ("MillGrainSpout", "tube", "oak_timber"),
    ("MillWaterGateHandle", "stand", "oak_timber"),
    ("MillDrainGrating", "panel", "oak_timber"),
    ("BridgeCrossBrace", "panel", "oak_timber"),
    ("FerryRampSegment", "slab", "oak_timber"),
    ("FerryMooringCleat", "bracket", "oak_timber"),
    ("FerryRopeSpool", "tube", "oak_timber"),
    ("FerryBoardingBarrier", "panel", "oak_timber"),
    ("FerryDeckLightPost", "stand", "oak_timber"),
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def geometry(name, grammar, material, i, lod, out):
    fine = lod == 0
    k = 0.88 + (i % 7) * 0.08
    secondary = "mossy_stone" if material == "oak_timber" else "oak_timber"
    blocks = []
    if grammar == "bracket":
        sh.box("BracketPlate", (0, 0, 0.48*k), (0.54*k, 0.14, 0.96*k), material, out, 0.025 if fine else 0)
        sh.box("Arm", (0, -0.28*k, 0.52*k), (0.18, 0.64*k, 0.17), secondary, out)
        if fine:
            for z in (0.20*k, 0.76*k):
                sh.cylinder("Fastener", (0, -0.085, z), 0.045, 0.055, secondary, out, 8)
        blocks.append(((0, 0, 0.48*k), (0.54*k, 0.32, 0.96*k)))
    elif grammar == "slab":
        sh.box("WalkableSurface", (0, 0, 0.105*k), (2.2*k, 1.05*k, 0.21*k), material, out, 0.03 if fine else 0)
        if fine:
            for j in (-1, 0, 1):
                sh.box("SurfaceEdge", (j*0.68*k, 0, 0.23*k), (0.075, 1.06*k, 0.045), secondary, out)
        blocks.append(((0, 0, 0.105*k), (2.2*k, 1.05*k, 0.21*k)))
    elif grammar == "arch":
        for x in (-0.88*k, 0.88*k):
            sh.box("DoorFrameLeg", (x, 0, 1.05*k), (0.18, 0.26, 2.10*k), material, out)
            blocks.append(((x, 0, 1.05*k), (0.18, 0.26, 2.10*k)))
        sh.box("FrameLintel", (0, 0, 2.09*k), (1.92*k, 0.26, 0.18), material, out)
        blocks.append(((0, 0, 2.09*k), (1.92*k, 0.26, 0.18)))
        if fine:
            sh.box("DecorativeTop", (0, -0.15, 2.19*k), (2.04*k, 0.11, 0.075), secondary, out)
    elif grammar == "panel":
        sh.box("PanelBase", (0, 0, 0.68*k), (1.54*k, 0.16, 1.36*k), material, out)
        if fine:
            for x in (-0.53*k, 0.53*k):
                sh.box("PanelRib", (x, -0.12, 0.68*k), (0.095, 0.11, 1.30*k), secondary, out)
            sh.box("PanelTrim", (0, -0.12, 1.25*k), (1.48*k, 0.1, 0.075), secondary, out)
        blocks.append(((0, 0, 0.68*k), (1.54*k, 0.18, 1.36*k)))
    elif grammar == "shelf":
        for z in (0.24*k, 0.72*k, 1.18*k) if fine else (0.24*k, 1.18*k):
            sh.box("ShelfBoard", (0, 0, z), (1.55*k, 0.49*k, 0.12), material, out)
        for x in (-0.7*k, 0.7*k):
            sh.box("ShelfLeg", (x, 0, 0.64*k), (0.11, 0.44*k, 1.28*k), material, out)
        blocks.append(((0, 0, 0.64*k), (1.55*k, 0.5*k, 1.28*k)))
    elif grammar == "stand":
        sh.cylinder("StandMast", (0, 0, 0.64*k), 0.12*k, 1.28*k, material, out, 9 if fine else 6)
        sh.box("BaseFoot", (0, 0, 0.09*k), (0.71*k, 0.62*k, 0.18*k), secondary, out)
        if fine:
            sh.box("UpperFixture", (0, -0.19*k, 1.19*k), (0.58*k, 0.2, 0.16), secondary, out)
        blocks.append(((0, 0, 0.64*k), (0.71*k, 0.62*k, 1.28*k)))
    elif grammar == "cluster":
        sh.box("PlanterBase", (0, 0, 0.12*k), (1.43*k, 0.91*k, 0.24*k), secondary, out)
        for n in range(3 if fine else 2):
            x = (n - 1)*0.42*k
            sh.ico("OrganicCluster", (x, 0, (0.31 + n*0.13)*k),
                   (0.48*k, 0.53*k, 0.52*k), material, out, lod == 1)
        blocks.append(((0, 0, 0.17*k), (1.43*k, 0.91*k, 0.34*k)))
    elif grammar == "ladder":
        for x in (-0.42*k, 0.42*k):
            sh.box("LadderSide", (x, 0, 1.18*k), (0.13, 0.17, 2.36*k), material, out)
        for z in ((0.42, 0.89, 1.36, 1.83) if fine else (0.55, 1.45)):
            sh.box("LadderRung", (0, -0.03, z*k), (0.84*k, 0.13, 0.11), secondary, out)
        blocks.append(((0, 0, 1.18*k), (0.99*k, 0.21, 2.36*k)))
    elif grammar == "tube":
        sh.cylinder("TubeCore", (0, 0, 0.61*k), 0.39*k, 1.22*k, material, out, 12 if fine else 6)
        for z in (0.13*k, 1.09*k) if fine else (0.13*k,):
            sh.cylinder("Rim", (0, 0, z), 0.48*k, 0.13*k, secondary, out, 12 if fine else 6)
        blocks.append(((0, 0, 0.61*k), (0.99*k, 0.99*k, 1.22*k)))
    else:
        raise RuntimeError("UNSUPPORTED_SHIRE_GRAMMAR")
    return blocks


def one(entry, ordinal, lod, out):
    name, grammar, material = entry
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sh.PARTS = []
    collision_groups = geometry(name, grammar, material, ordinal, lod, out)
    visual_name = "SM_ShDetail_" + name + "_LOD" + str(lod)
    visual = sh.join_visual(visual_name)
    polygons = len(visual.data.polygons)
    if not 0 < polygons <= 15000:
        raise RuntimeError("DETAIL_FBX_TRIANGLE_BUDGET")
    for i, (center, dimensions) in enumerate(collision_groups):
        sh.collider(visual_name, center, dimensions, i)
    mesh_dir = out / "shire_detail_meshes"
    mesh_dir.mkdir(parents=True, exist_ok=True)
    path = mesh_dir / (visual_name + ".fbx")
    bpy.ops.object.select_all(action="DESELECT")
    visual.select_set(True)
    for obj in bpy.data.objects:
        if obj.name.startswith("UCX_" + visual_name + "_"):
            obj.select_set(True)
    bpy.context.view_layer.objects.active = visual
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True,
        object_types={"MESH"}, mesh_smooth_type="FACE", use_mesh_modifiers=True,
        apply_unit_scale=True, global_scale=1.0, axis_forward="-Y",
        axis_up="Z", path_mode="RELATIVE", bake_anim=False, embed_textures=False)
    data = path.read_bytes()
    if not data.startswith(b"Kaydara FBX Binary") or int.from_bytes(data[23:27], "little") != 7400:
        raise RuntimeError("DETAIL_BINARY_FBX_7400_REQUIRED")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(path), use_anim=False)
    imported = [o for o in bpy.data.objects if o.type == "MESH"]
    visible = [o for o in imported if not o.name.startswith("UCX_")]
    collision = [o for o in imported if o.name.startswith("UCX_")]
    if len(visible) != 1 or len(collision) != len(collision_groups):
        raise RuntimeError("DETAIL_FBX_REIMPORT_MESH_UCX_MISMATCH")
    mesh = visible[0].data
    if not mesh.uv_layers or not 0 < len(mesh.polygons) <= 15000:
        raise RuntimeError("DETAIL_FBX_UV_POLYGON_MISSING")
    if any(p.area <= 1e-8 for p in mesh.polygons):
        raise RuntimeError("DETAIL_FBX_DEGENERATE_POLYGON")
    return {"asset": name, "role": grammar, "lod": lod,
            "path": "shire_detail_meshes/" + path.name,
            "sha256": sha(path), "bytes": len(data),
            "reimport_polygons": len(mesh.polygons), "uv_layers": len(mesh.uv_layers),
            "collider_count": len(collision), "format": "FBX_BINARY_7400",
            "static_source_only": True, "unreal_imported": False}


def main(destination):
    destination.mkdir(parents=True, exist_ok=True)
    if len(KITS) != 28 or len({r[0] for r in KITS}) != 28:
        raise RuntimeError("DETAIL_KIT_IDENTITIES_MUST_BE_DISTINCT")
    results = [one(entry, i, lod, destination)
               for i, entry in enumerate(KITS) for lod in (0, 1)]
    if len(results) != 56 or len({r["sha256"] for r in results}) != 56:
        raise RuntimeError("DETAIL_56_FILES_MUST_HAVE_UNIQUE_BYTES")
    receipt = {"schema_version": 1, "stage": "BLENDER_REIMPORTED_SOURCE_ONLY",
               "provenance": "ORIGINAL_PROJECT_PROCEDURAL",
               "source_generator_sha256": sha(__file__), "families": 28,
               "fbx_count": 56, "objects": results,
               "warehouse_persisted": False, "unreal_imported": False,
               "world_placed": False, "pie_tested": False,
               "device_tested": False, "visual_accepted": False,
               "gate67_closed": False}
    (destination / "shire_detail_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("SHIRE_DETAIL_56_FBX_GENERATED families=28 files=56 lods=2")


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) != 2 or args[0] != "--out":
        raise SystemExit("usage: blender -b --python blender_shire_detail56.py -- --out OUTPUT")
    main(Path(args[1]).resolve())
