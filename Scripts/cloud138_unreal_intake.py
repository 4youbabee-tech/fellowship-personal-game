#!/usr/bin/env python3
"""One-writer, source-hash-gated Cloud138 -> UE4.27 P1C01 intake.

Only 41 Shire LOD0 + 41 sidecars and 36 original PNG are eligible.
56 regional FBX remain solely in the persistent source warehouse. This module
never edits a runtime world, activates P1C02, or claims PIE/device/visual proof.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stage_cloud_wholegame_source import inspect_saved, require

SOURCE_COMMIT = "1e1e5c9df5aeee75e130eed7891fdfb7b129c9fc"
STAGE_REL = Path("Saved/Cloud138Unreal/stage.json")
EDITOR_REL = Path("Saved/Cloud138Unreal/editor.json")
REOPEN_REL = Path("Saved/Cloud138Unreal/reopen.json")
SOURCE_PREFIX = Path("SourceAssets/Production")
MESH_REL = Path("World/Shire/Cloud138")
MATERIAL_REL = Path("Materials/Cloud138")
LOD_REL = Path("Saved/Cloud138Unreal/LODs")
GAME_MESH = "/Game/Production/World/Shire/Cloud138"
GAME_MATERIAL = "/Game/Production/Materials/Cloud138"
MASTER = "/Game/Production/Materials/M_P1C01VerifiedPBR"
MAPS = ("BaseColor", "NormalDX", "ORM")
PARAMS = {"BaseColor": "AlbedoTexture", "NormalDX": "NormalTexture", "ORM": "ORMTexture"}
IMPORTANT_COLLISION = {"RoundDoor", "WoodenFootbridge", "FerryLanding", "StonePath"}
COLLISION_BOX_FALLBACK_FAMILIES = frozenset(("FerryLanding", "RoundDoor"))


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def saved_asset_path(workspace, game_path):
    require(game_path.startswith("/Game/Production/"), "UNSAFE_GAME_ASSET_PATH")
    return Path(workspace) / "Content" / (game_path[len("/Game/"):] + ".uasset")


def copy_exact(source, target, expected):
    source, target = Path(source), Path(target)
    require(source.is_file() and not source.is_symlink() and digest(source) == expected,
            "SOURCE_HASH_CHANGED:" + str(source))
    require(not target.is_symlink(), "TARGET_SYMLINK_REJECTED:" + str(target))
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        require(target.is_file() and digest(target) == expected,
                "STAGE_CONFLICT_CHANGED_CONTENT:" + str(target))
    else:
        shutil.copyfile(source, target)
        require(digest(target) == expected, "POST_COPY_HASH_MISMATCH:" + str(target))


def stage(warehouse_root, workspace, pin):
    warehouse_root, workspace = Path(warehouse_root).resolve(), Path(workspace).resolve()
    require(warehouse_root.is_dir() and workspace.is_dir(), "WAREHOUSE_OR_WORKSPACE_MISSING")
    require(pin["source_commit"] == SOURCE_COMMIT and pin["artifact_id"] == 11767251532,
            "UNTRUSTED_CLOUD138_PIN")
    physical = warehouse_root / "_original_cloud_wholegame" / SOURCE_COMMIT
    receipt = inspect_saved(physical, pin["source_zip_sha256"])
    require(receipt.get("artifact_id") == pin["artifact_id"] and
            receipt.get("source_commit") == SOURCE_COMMIT and
            receipt.get("physical_fbx") == 138 and receipt.get("shire_fbx") == 82 and
            receipt.get("regional_fbx") == 56 and receipt.get("textures_png") == 36 and
            receipt.get("region_count") == 28 and receipt.get("unreal_imported") is False,
            "CLOUD138_WAREHOUSE_COUNT_OR_STATE_DRIFT")
    recorded = {x["path"]: x for x in receipt["files"]}
    require(len(recorded) == 177, "CLOUD138_WAREHOUSE_RECEIPT_DUPLICATES")
    shire = read_json(physical / "fbx_receipt.json")
    materials = read_json(physical / "materials_receipt.json")
    regional = read_json(physical / "regional_fbx_receipt.json")
    require(shire.get("asset_count") == 41 and len(shire.get("objects", [])) == 82 and
            len(regional.get("objects", [])) == 56 and
            len(materials.get("textures", [])) == 36,
            "CLOUD138_INNER_SOURCE_RECEIPTS_DRIFT")
    meshes = {}
    for row in shire["objects"]:
        family = row.get("asset")
        lod = row.get("lod")
        require(isinstance(family, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9]{1,63}", family),
                "CLOUD138_UNSAFE_MESH_IDENTITY")
        require(lod in (0, 1) and type(lod) is int, "CLOUD138_UNSAFE_LOD")
        source = "meshes/SM_Sh%s_LOD%d.fbx" % (family, lod)
        require(row.get("path") == source and source in recorded and
                row["sha256"] == recorded[source]["sha256"] and
                row["bytes"] == recorded[source]["bytes"] and
                row.get("collider_count", 0) >= 1 and row.get("reimport_polygons", 0) > 0,
                "CLOUD138_SHIRE_SOURCE_MISMATCH:" + source)
        family_lods = meshes.setdefault(family, {})
        require(lod not in family_lods, "CLOUD138_DUPLICATE_MESH_LOD:" + family)
        family_lods[lod] = row
    require(len(meshes) == 41 and all(set(x) == {0, 1} for x in meshes.values()),
            "CLOUD138_EXPECTED_41_COMPLETE_MESH_FAMILIES")
    groups = {}
    for row in materials["textures"]:
        family = row.get("family")
        kind = row.get("type")
        require(isinstance(family, str) and re.fullmatch(r"[a-z][a-z0-9_]{2,63}", family) and
                kind in MAPS, "CLOUD138_UNTRUSTED_MATERIAL_IDENTITY")
        source = row.get("path")
        require(isinstance(source, str) and
                source.startswith("materials/" + family + "/") and
                source.endswith("_" + kind + ".png") and
                source in recorded and recorded[source]["sha256"] == row["sha256"] and
                recorded[source]["bytes"] == row["bytes"],
                "CLOUD138_MATERIAL_MISMATCH:" + str(source))
        grp = groups.setdefault(family, {})
        require(kind not in grp, "CLOUD138_DUPLICATE_PBR_MAP")
        grp[kind] = row
    require(len(groups) == 12 and all(set(x) == set(MAPS) for x in groups.values()),
            "CLOUD138_EXPECTED_12_COMPLETE_PBR_TRIPLETS")
    rows = []
    for family in sorted(meshes):
        for lod in (0, 1):
            source = meshes[family][lod]
            asset = "SM_Sh" + family
            target = (workspace / SOURCE_PREFIX / MESH_REL / (asset + ".fbx")
                      if lod == 0 else workspace / LOD_REL / (asset + "_LOD1.fbx"))
            copy_exact(physical / source["path"], target, source["sha256"])
            rows.append({"kind": "mesh", "family": family, "lod": lod,
                         "source": source["path"], "sha256": source["sha256"],
                         "target": str(target.relative_to(workspace)).replace("\\", "/"),
                         "asset": GAME_MESH + "/" + asset})
    for family in sorted(groups):
        for kind in MAPS:
            row = groups[family][kind]
            name = "TX_" + family + "_" + kind
            target = workspace / SOURCE_PREFIX / MATERIAL_REL / family / (name + ".png")
            copy_exact(physical / row["path"], target, row["sha256"])
            rows.append({"kind": "texture", "family": family, "map": kind,
                         "source": row["path"], "sha256": row["sha256"],
                         "target": str(target.relative_to(workspace)).replace("\\", "/"),
                         "asset": GAME_MATERIAL + "/" + family + "/" + name})
    require(len(rows) == 118, "CLOUD138_STAGE_COUNT_WRONG")
    output = {"schema_version": 1, "mode": "P1C01_SOURCE_STAGED_NO_UNREAL_CLAIMS",
              "source_commit": SOURCE_COMMIT, "source_zip_sha256": pin["source_zip_sha256"],
              "warehouse_receipt_sha256": digest(physical / "warehouse_receipt.json"),
              "shires_lod0": 41, "shire_sidecar_lod1": 41, "packed_png": 36,
              "regional_fbx_held_in_warehouse": 56, "source_rows": rows,
              "ue_imported": False, "world_placed": False, "pie_tested": False,
              "device_tested": False, "visual_accepted": False, "gate67_closed": False}
    write_json(workspace / STAGE_REL, output)
    print("CLOUD138_SHIRE_UNREAL_SOURCE_STAGE_PASS meshes=41 lod1=41 png=36 regional_held=56")
    return output


def load_plan(root):
    root = Path(root).resolve()
    obj = read_json(root / STAGE_REL)
    require(obj.get("source_commit") == SOURCE_COMMIT and
            obj.get("mode") == "P1C01_SOURCE_STAGED_NO_UNREAL_CLAIMS" and
            len(obj.get("source_rows", [])) == 118 and
            obj.get("regional_fbx_held_in_warehouse") == 56 and
            obj.get("ue_imported") is False,
            "CLOUD138_STAGE_PLAN_UNTRUSTED")
    for row in obj["source_rows"]:
        path = root / row["target"]
        require(root in path.resolve().parents and path.is_file() and
                not path.is_symlink() and digest(path) == row["sha256"],
                "CLOUD138_WORKSPACE_STAGED_FILE_DRIFT:" + str(path))
    return obj


def saved_or_raise(unreal, game_path):
    require(unreal.EditorAssetLibrary.does_asset_exist(game_path),
            "CLOUD138_REGISTRY_MISSING:" + game_path)
    disk = saved_asset_path(unreal.Paths.project_dir(), game_path)
    require(disk.is_file() and disk.stat().st_size > 2048,
            "CLOUD138_UASSET_NOT_SAVED:" + str(disk))


def editor_mode(reopen=False):
    import unreal
    root = Path(unreal.Paths.project_dir()).resolve()
    # Reject stale receipts from prior Windows runner checkouts.
    output = root / (REOPEN_REL if reopen else EDITOR_REL)
    if output.exists():
        output.unlink()
    plan = load_plan(root)
    rows = plan["source_rows"]
    meshes = {r["family"]: r for r in rows if r["kind"] == "mesh" and r["lod"] == 0}
    lods = {r["family"]: r for r in rows if r["kind"] == "mesh" and r["lod"] == 1}
    textures = [r for r in rows if r["kind"] == "texture"]
    mapping = {"BaseColor": unreal.TextureCompressionSettings.TC_DEFAULT,
               "NormalDX": unreal.TextureCompressionSettings.TC_NORMALMAP,
               "ORM": unreal.TextureCompressionSettings.TC_MASKS}
    observations = []
    for family, row in sorted(meshes.items()):
        path = row["asset"]
        mesh = unreal.EditorAssetLibrary.load_asset(path)
        require(mesh and isinstance(mesh, unreal.StaticMesh),
                "CLOUD138_UNREAL_MESH_MISSING:" + path)
        if not reopen:
            imported = unreal.EditorStaticMeshLibrary.import_lod(mesh, 1, str(root / lods[family]["target"]))
            require(imported == 1, "CLOUD138_LOD_IMPORT_FAILED:" + path)
        count = unreal.EditorStaticMeshLibrary.get_lod_count(mesh)
        require(count == 2 and all(unreal.EditorStaticMeshLibrary.get_number_verts(mesh, k) > 0
                                   for k in (0, 1)), "CLOUD138_LOD_DATA_MISSING:" + path)
        slots = unreal.EditorStaticMeshLibrary.get_number_materials(mesh)
        require(slots > 0, "CLOUD138_MESH_MATERIAL_SLOTS_MISSING:" + path)
        collision = unreal.EditorStaticMeshLibrary.get_simple_collision_count(mesh)
        # Some UE4 FBX imports lose authored UCX. Restrict editor fallback to
        # the two known closed SOLID shapes only: a landing platform and a closed
        # round door. Never box open bridges, foliage or decorative meshes.
        # A RoundDoor box is only a closed-state proxy: opening/hinge traversal
        # requires separate PIE evidence, not this import check.
        if family in COLLISION_BOX_FALLBACK_FAMILIES and collision == 0 and not reopen:
            source = next((r for r in plan["source_rows"] if r["kind"] == "mesh"
                           and r["family"] == family and r["lod"] == 0), None)
            require(source is not None and (root / source["target"]).is_file(),
                    "CLOUD138_COLLISION_FALLBACK_SOURCE_MISSING:" + path)
            collision_index = unreal.EditorStaticMeshLibrary.add_simple_collisions(
                mesh, unreal.ScriptingCollisionShapeType.BOX)
            require(collision_index >= 0,
                    "CLOUD138_BOX_COLLISION_API_FAILED:" + path)
            collision = unreal.EditorStaticMeshLibrary.get_simple_collision_count(mesh)
            require(collision > 0, "CLOUD138_BOX_COLLISION_REPAIR_FAILED:" + path)
            print("CLOUD138_COLLISION_FALLBACK family=" + family +
                  " editor_box_created=1 source_ucx_not_imported;"
                  " CLOSED_STATE_ONLY_NAV_PIE_REVIEW_REQUIRED")
        if family in IMPORTANT_COLLISION:
            require(collision > 0, "CLOUD138_WALKABLE_UCX_NOT_IMPORTED:" + path)
        if not reopen:
            require(unreal.EditorAssetLibrary.save_loaded_asset(mesh, only_if_is_dirty=False),
                    "CLOUD138_MESH_SAVE_FAILED:" + path)
        saved_or_raise(unreal, path)
        observations.append({"asset": path, "lods": count, "slots": slots,
                             "simple_collisions": collision})
    for row in textures:
        path = row["asset"]
        tex = unreal.EditorAssetLibrary.load_asset(path)
        require(tex and isinstance(tex, unreal.Texture2D), "CLOUD138_TEXTURE_NOT_IMPORTED:" + path)
        if not reopen:
            tex.set_editor_property("srgb", row["map"] == "BaseColor")
            tex.set_editor_property("compression_settings", mapping[row["map"]])
            tex.set_editor_property("never_stream", False)
            require(unreal.EditorAssetLibrary.save_loaded_asset(tex, only_if_is_dirty=False),
                    "CLOUD138_TEXTURE_SAVE_FAILED:" + path)
        require(tex.get_editor_property("srgb") == (row["map"] == "BaseColor") and
                tex.get_editor_property("compression_settings") == mapping[row["map"]] and
                tex.get_editor_property("never_stream") is False,
                "CLOUD138_TEXTURE_PROPERTIES_NOT_PERSISTED:" + path)
        saved_or_raise(unreal, path)
    parent = unreal.EditorAssetLibrary.load_asset(MASTER)
    require(parent and isinstance(parent, unreal.MaterialInterface),
            "CLOUD138_EXISTING_PBR_PARENT_REQUIRED")
    param_names = {str(x) for x in unreal.MaterialEditingLibrary.get_texture_parameter_names(parent)}
    require(set(PARAMS.values()).issubset(param_names), "CLOUD138_PARENT_PARAM_SCHEMA_INVALID")
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    all_materials = []
    for family in sorted({r["family"] for r in textures}):
        path = GAME_MATERIAL + "/MI_Cloud138_" + family
        material = (unreal.EditorAssetLibrary.load_asset(path)
                    if unreal.EditorAssetLibrary.does_asset_exist(path) else None)
        if not material and not reopen:
            material = tools.create_asset("MI_Cloud138_" + family, GAME_MATERIAL,
                                          unreal.MaterialInstanceConstant,
                                          unreal.MaterialInstanceConstantFactoryNew())
        require(material and isinstance(material, unreal.MaterialInstanceConstant),
                "CLOUD138_MI_CREATE_OR_RELOAD_FAILED:" + path)
        if not reopen:
            unreal.MaterialEditingLibrary.set_material_instance_parent(material, parent)
            unreal.MaterialEditingLibrary.update_material_instance(material)
        require(material.get_editor_property("parent") and
                material.get_editor_property("parent").get_path_name() == parent.get_path_name(),
                "CLOUD138_MI_PARENT_INVALID:" + path)
        for row in [r for r in textures if r["family"] == family]:
            texture = unreal.EditorAssetLibrary.load_asset(row["asset"])
            if not reopen:
                unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
                    material, PARAMS[row["map"]], texture)
        if not reopen:
            unreal.MaterialEditingLibrary.update_material_instance(material)
            require(unreal.EditorAssetLibrary.save_loaded_asset(material, only_if_is_dirty=False),
                    "CLOUD138_MI_SAVE_FAILED:" + path)
        saved_or_raise(unreal, path)
        for row in [r for r in textures if r["family"] == family]:
            bound = unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(
                material, PARAMS[row["map"]])
            expected = row["asset"] + "." + row["asset"].rsplit("/", 1)[1]
            require(bound and bound.get_path_name() == expected,
                    "CLOUD138_MI_TEXTURE_READBACK_WRONG:" + path)
        all_materials.append(path)
    saved_or_raise(unreal, MASTER)
    report = {"schema_version": 1, "source_commit": SOURCE_COMMIT,
              "stage_receipt_sha256": digest(root / STAGE_REL),
              "mode": "UE4_REOPEN_READBACK" if reopen else "UE4_EDITOR_IMPORT",
              "mesh_uassets": len(observations), "authored_lod1_imported": len(observations),
              "texture_uassets": len(textures), "linked_pbr_material_instances": len(all_materials),
              "verified_original_pbr_maps": len(textures), "mesh_material_bindings": 0,
              "total_new_uassets": len(observations) + len(textures) + len(all_materials),
              "parent_dependency": MASTER, "observations": observations,
              "regional_fbx_unreal_imported": 0, "world_placed": False,
              "collision_nav_tested": False, "pie_tested": False, "device_tested": False,
              "visual_accepted": False, "gate67_closed": False}
    require(report["total_new_uassets"] == 89, "CLOUD138_EDITOR_COUNTS_WRONG")
    path = root / (REOPEN_REL if reopen else EDITOR_REL)
    write_json(path, report)
    print("CLOUD138_UE_REOPEN_PASS" if reopen else "CLOUD138_UE_IMPORT_PASS",
          "meshes=41 lod1=41 textures=36 mi=12 new_uassets=89 world_placed=0")
    return report


def persist(warehouse_root, workspace, pin):
    warehouse_root, workspace = Path(warehouse_root).resolve(), Path(workspace).resolve()
    stage_plan = load_plan(workspace)
    editor, reopened = read_json(workspace / EDITOR_REL), read_json(workspace / REOPEN_REL)
    require(editor.get("mode") == "UE4_EDITOR_IMPORT" and
            reopened.get("mode") == "UE4_REOPEN_READBACK" and
            editor.get("source_commit") == reopened.get("source_commit") == SOURCE_COMMIT and
            editor.get("total_new_uassets") == reopened.get("total_new_uassets") == 89 and
            editor.get("stage_receipt_sha256") == reopened.get("stage_receipt_sha256") == digest(workspace / STAGE_REL),
            "CLOUD138_UNREAL_REOPEN_EVIDENCE_MISSING")
    require(pin["source_zip_sha256"] == stage_plan["source_zip_sha256"], "CLOUD138_PIN_CHANGED")
    assets = sorted({r["asset"] for r in stage_plan["source_rows"]} |
                    {GAME_MATERIAL + "/MI_Cloud138_" + r["family"]
                     for r in stage_plan["source_rows"] if r["kind"] == "texture"} | {MASTER})
    require(len(assets) == 90, "CLOUD138_NEW_UASSET_PLUS_PARENT_NOT_90")
    destination = warehouse_root / "_unreal_cloud138" / SOURCE_COMMIT
    if destination.exists():
        old = read_json(destination / "unreal_receipt.json")
        require(old.get("source_zip_sha256") == pin["source_zip_sha256"] and
                len(old.get("files", [])) == 90, "CLOUD138_PERSISTENT_UASSET_RECEIPT_INVALID")
        for row in old["files"]:
            disk = destination / row["relative"]
            require(disk.is_file() and disk.stat().st_size == row["bytes"] and
                    digest(disk) == row["sha256"], "CLOUD138_PERSISTENT_PACKAGE_CORRUPT")
        print("CLOUD138_UE_PERSIST_REUSED uassets=90")
        return old
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix=".cloud138_ue_", dir=destination.parent))
    try:
        rows = []
        for asset in assets:
            src = saved_asset_path(workspace, asset)
            require(src.is_file() and not src.is_symlink() and src.stat().st_size > 2048,
                    "CLOUD138_ENGINE_PACKAGE_MISSING:" + asset)
            rel = "Content/" + asset[len("/Game/"):] + ".uasset"
            target = temp / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, target)
            checksum = digest(src)
            require(digest(target) == checksum, "CLOUD138_ENGINE_PACKAGE_COPY_HASH_CHANGED")
            rows.append({"relative": rel, "bytes": target.stat().st_size,
                         "sha256": checksum, "game_asset": asset})
        proof = {"schema_version": 1, "stage": "UE4_IMPORTED_REOPENED_PERSISTED_NOT_WORLD_PLACED",
                 "source_commit": SOURCE_COMMIT, "source_zip_sha256": pin["source_zip_sha256"],
                 "new_uassets": 89, "dependent_parent_uassets": 1,
                 "shires_meshes": 41, "authored_lod1": 41, "pbr_textures": 36,
                 "pbr_instances": 12, "material_maps_bound": 36,
                 "mesh_material_slots_bound": 0, "regions_fbx_held": 56,
                 "payload_bytes": sum(x["bytes"] for x in rows), "files": rows,
                 "world_placed": False, "collision_nav_tested": False,
                 "pie_tested": False, "device_tested": False, "visual_accepted": False,
                 "gate67_closed": False}
        write_json(temp / "unreal_receipt.json", proof)
        temp.rename(destination)
        print("CLOUD138_UE_PERSIST_PASS new_uassets=89 shared_parent=1 saved=90 bytes=%d" %
              proof["payload_bytes"])
        return proof
    finally:
        if temp.exists():
            shutil.rmtree(temp)


def main():
    if os.environ.get("SHIRE_CLOUD138_EDITOR_MODE"):
        mode = os.environ["SHIRE_CLOUD138_EDITOR_MODE"]
        require(mode in ("editor", "reopen"), "CLOUD138_EDITOR_MODE_INVALID")
        editor_mode(mode == "reopen")
        return 0
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("stage", "preflight", "persist"))
    parser.add_argument("--warehouse-root", type=Path)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--pin", type=Path)
    opts = parser.parse_args()
    try:
        if opts.mode == "preflight":
            load_plan(opts.workspace)
            print("CLOUD138_STAGED_HASH_PREFLIGHT_PASS")
        else:
            require(opts.pin and opts.warehouse_root, "CLOUD138_PIN_AND_ROOT_REQUIRED")
            pin = read_json(opts.pin)
            if opts.mode == "stage":
                stage(opts.warehouse_root, opts.workspace, pin)
            else:
                persist(opts.warehouse_root, opts.workspace, pin)
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print("CLOUD138_UNREAL_INTAKE_FAIL " + str(exc), file=sys.stderr)
        return 86


if __name__ == "__main__":
    raise SystemExit(main())
