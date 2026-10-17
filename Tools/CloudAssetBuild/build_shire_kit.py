#!/usr/bin/env python3
"""Build reviewed source meshes into UE4.27 FBX + LOD sidecars.

This script never invents geometry. External source files must be staged in
ExternalLicensed/Approved and match an approved ExternalAssetManifest row.
Rows lacking that receipt remain pending and do not stop other rows.
Run in Blender: blender -b --python build_shire_kit.py -- --manifest ... --external-manifest ...
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import traceback
from pathlib import Path

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{1,79}$")
ALLOWED_EXT = {".fbx", ".obj", ".glb", ".gltf", ".blend"}
DEFAULT_LODS = (1.0, 0.5, 0.25)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def validate_manifest(manifest: dict) -> list[str]:
    errors = []
    if manifest.get("schema_version") != 1:
        errors.append("SCHEMA_VERSION_UNSUPPORTED")
    rows = manifest.get("assets")
    if not isinstance(rows, list):
        return errors + ["ASSETS_MUST_BE_LIST"]
    seen = set()
    for index, row in enumerate(rows):
        prefix = f"ROW_{index}"
        if not isinstance(row, dict):
            errors.append(prefix + "_NOT_OBJECT")
            continue
        asset_id = row.get("id")
        if not isinstance(asset_id, str) or not ID_RE.fullmatch(asset_id):
            errors.append(prefix + "_INVALID_ID")
            continue
        if asset_id in seen:
            errors.append(prefix + "_DUPLICATE_ID_" + asset_id)
        seen.add(asset_id)
        for field in ("source", "source_url", "license", "license_evidence",
                      "external_asset_id", "material_group"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                errors.append(prefix + "_MISSING_" + field.upper())
        if not isinstance(row.get("provider"), str) or not row["provider"].strip():
            errors.append(prefix + "_MISSING_PROVIDER")
        tris = row.get("target_tris")
        if type(tris) is not int or tris < 4:
            errors.append(prefix + "_INVALID_TARGET_TRIS")
        lods = row.get("lods")
        if not isinstance(lods, list) or len(lods) != 3:
            errors.append(prefix + "_REQUIRES_THREE_LODS")
        elif any(type(value) not in (int, float) or not 0 < value <= 1 for value in lods):
            errors.append(prefix + "_INVALID_LOD_RATIO")
        elif lods != sorted(lods, reverse=True) or lods[0] != 1:
            errors.append(prefix + "_LOD_RATIOS_MUST_DESCEND_FROM_ONE")
        collision = row.get("collision")
        if not isinstance(collision, dict) or collision.get("mode") not in ("convex", "none"):
            errors.append(prefix + "_INVALID_COLLISION_POLICY")
        if row.get("status") not in ("PENDING_SOURCE", "APPROVED"):
            errors.append(prefix + "_INVALID_STATUS")
    return errors


def approved_record(row: dict, external_manifest: dict) -> dict | None:
    for record in external_manifest.get("assets", []):
        if record.get("id") == row.get("external_asset_id") and record.get("status") == "APPROVED":
            return record
    return None


def validate_input(row: dict, source_root: Path, external_manifest: dict) -> tuple[Path | None, str | None]:
    if row.get("status") != "APPROVED":
        return None, "PENDING_SOURCE"
    record = approved_record(row, external_manifest)
    if record is None:
        return None, "EXTERNAL_LICENSE_RECEIPT_MISSING"
    source = (source_root / row["source"]).resolve()
    root = source_root.resolve()
    if root not in source.parents:
        return None, "SOURCE_PATH_ESCAPES_ROOT"
    if "Approved" not in source.relative_to(root).parts:
        return None, "SOURCE_NOT_IN_APPROVED_ROOT"
    if source.suffix.lower() not in ALLOWED_EXT:
        return None, "SOURCE_FORMAT_UNSUPPORTED"
    if not source.is_file():
        return None, "SOURCE_FILE_MISSING"
    expected = record.get("sha256")
    actual = sha256_file(source)
    if record.get("source_url") != row.get("source_url"):
        return None, "SOURCE_URL_RECEIPT_MISMATCH"
    if record.get("license_class") != row.get("license"):
        return None, "LICENSE_RECEIPT_MISMATCH"
    if record.get("provider") != row.get("provider"):
        return None, "PROVIDER_RECEIPT_MISMATCH"
    expected = record.get("sha256")
    actual = sha256_file(source)
    if not isinstance(expected, str) or actual.lower() != expected.lower():
        return None, "SOURCE_SHA256_MISMATCH"
    return source, None


def emit_status(row: dict, status: str, detail: str = "") -> None:
    suffix = (" detail=" + detail.replace("\n", " ")[:240]) if detail else ""
    print(f"SHIRE_KIT asset={row.get('id','?')} status={status}{suffix}", flush=True)


def import_source(bpy, source: Path) -> list:
    bpy.ops.object.select_all(action="DESELECT")
    ext = source.suffix.lower()
    if ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(source), use_anim=False)
    elif ext == ".obj":
        bpy.ops.wm.obj_import(filepath=str(source))
    elif ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=str(source))
    elif ext == ".blend":
        with bpy.data.libraries.load(str(source), link=False) as (data_from, data_to):
            data_to.objects = list(data_from.objects)
        for obj in data_to.objects:
            if obj:
                bpy.context.scene.collection.objects.link(obj)
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not meshes:
        raise ValueError("SOURCE_CONTAINS_NO_MESH")
    return meshes


def join_meshes(bpy, meshes, name: str):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = name
    obj.data.name = name + "_Mesh"
    return obj


def normalize_mesh(bpy, obj, row: dict) -> None:
    if len(obj.data.polygons) == 0:
        raise ValueError("EMPTY_MESH")
    if len(obj.data.uv_layers) == 0:
        raise ValueError("UV0_MISSING")
    # Apply source transforms first, then fit the declared real-world height.
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bounds = [obj.matrix_world @ __import__("mathutils").Vector(corner)
              for corner in obj.bound_box]
    height = max(v.z for v in bounds) - min(v.z for v in bounds)
    target_height = row.get("target_height_m")
    if target_height is not None:
        if not isinstance(target_height, (int, float)) or target_height <= 0:
            raise ValueError("INVALID_TARGET_HEIGHT")
        if height <= 1e-6:
            raise ValueError("ZERO_HEIGHT_MESH")
        factor = float(target_height) / height
        obj.scale = (factor, factor, factor)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # Center X/Y and place lowest point on ground origin.
    bounds = [obj.matrix_world @ __import__("mathutils").Vector(corner)
              for corner in obj.bound_box]
    min_x, max_x = min(v.x for v in bounds), max(v.x for v in bounds)
    min_y, max_y = min(v.y for v in bounds), max(v.y for v in bounds)
    min_z = min(v.z for v in bounds)
    obj.location.x -= (min_x + max_x) * 0.5
    obj.location.y -= (min_y + max_y) * 0.5
    obj.location.z -= min_z
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.0001)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    if not obj.data.uv_layers or not obj.data.materials:
        raise ValueError("UV_OR_MATERIALS_LOST_DURING_NORMALIZATION")
    obj.data.calc_loop_triangles()
    triangles = len(obj.data.loop_triangles)
    if triangles > int(row["target_tris"]):
        raise ValueError(f"LOD0_OVER_TARGET:{triangles}>{row['target_tris']}")


def make_lod(bpy, source, name: str, ratio: float):
    lod = source.copy()
    lod.data = source.data.copy()
    lod.name = name
    bpy.context.collection.objects.link(lod)
    if ratio < 1:
        mod = lod.modifiers.new("ShireDecimate", "DECIMATE")
        mod.ratio = ratio
        bpy.context.view_layer.objects.active = lod
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return lod


def make_convex_collision(bpy, source, name: str):
    import bmesh
    obj = source.copy()
    obj.data = source.data.copy()
    obj.name = name
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    result = bmesh.ops.convex_hull(bm, input=bm.verts)
    for face in result.get("geom_interior", []):
        if isinstance(face, bmesh.types.BMFace) and face.is_valid:
            bm.faces.remove(face)
    bm.to_mesh(obj.data)
    bm.free()
    if len(obj.data.vertices) > 255:
        mod = obj.modifiers.new("CollisionVertexBudget", "DECIMATE")
        mod.ratio = max(0.05, 255.0 / len(obj.data.vertices))
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
    if len(obj.data.vertices) > 255 or len(obj.data.polygons) < 4:
        raise ValueError("CONVEX_COLLISION_LIMIT")
    return obj


def export_objects(bpy, objects: list, output: Path) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.fbx(
        filepath=str(output), use_selection=True, object_types={"MESH"},
        apply_unit_scale=True, global_scale=1.0, axis_forward="-Z",
        axis_up="Y", bake_space_transform=False, add_leaf_bones=False,
        path_mode="COPY", embed_textures=False,
    )
    if not output.is_file() or output.stat().st_size < 128:
        raise ValueError("FBX_EXPORT_EMPTY")


def normalize_images(bpy, row: dict, out_root: Path) -> list[dict]:
    max_px = int(row.get("texture_max_px", 2048))
    if max_px not in (1024, 2048):
        raise ValueError("TEXTURE_BUDGET_MUST_BE_1K_OR_2K")
    receipt = []
    folder = out_root / "Textures" / row["id"]
    for image in list(bpy.data.images):
        if image.source not in ("FILE", "GENERATED") or not image.size[0] or not image.size[1]:
            continue
        width, height = int(image.size[0]), int(image.size[1])
        if max(width, height) > max_px:
            factor = max_px / max(width, height)
            image.scale(max(1, round(width * factor)), max(1, round(height * factor)))
        folder.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", Path(image.name).stem) or "Texture"
        dest = folder / (safe_name + ".png")
        image.filepath_raw = str(dest)
        image.file_format = "PNG"
        image.save()
        if not dest.is_file():
            raise ValueError("TEXTURE_OUTPUT_NOT_PERSISTED")
        receipt.append({"path": dest.as_posix(), "width": int(image.size[0]),
                        "height": int(image.size[1]), "bytes": dest.stat().st_size,
                        "sha256": sha256_file(dest)})
    return receipt


def build_row(bpy, row: dict, source: Path, out_root: Path) -> dict:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    out_root.mkdir(parents=True, exist_ok=True)
    imported = import_source(bpy, source)
    base = join_meshes(bpy, imported, "SM_" + row["id"])
    normalize_mesh(bpy, base, row)
    source_triangles = len(base.data.loop_triangles)
    texture_receipt = normalize_images(bpy, row, out_root)
    outputs = []
    lod_records = []
    max_tris = int(row["target_tris"])
    l0_ratio = min(1.0, max_tris / max(1, source_triangles))
    lod0 = make_lod(bpy, base, "SM_" + row["id"] + "_LOD0", l0_ratio)
    lod0.data.calc_loop_triangles()
    if len(lod0.data.loop_triangles) > max_tris:
        raise ValueError(f"LOD0_OVER_TARGET:{len(lod0.data.loop_triangles)}>{max_tris}")
    l0 = out_root / f"SM_{row['id']}.fbx"
    objects = [lod0]
    collision = row["collision"]
    if collision["mode"] == "convex":
        objects.append(make_convex_collision(bpy, lod0, f"UCX_SM_{row['id']}_00"))
    export_objects(bpy, objects, l0)
    outputs.append(l0)
    lod_records.append({"index": 0, "triangles": len(lod0.data.loop_triangles)})
    for lod_index, ratio in enumerate(row["lods"][1:], start=1):
        lod = make_lod(bpy, lod0, f"SM_{row['id']}_LOD{lod_index}", float(ratio))
        lod.data.calc_loop_triangles()
        path = out_root / f"SM_{row['id']}_LOD{lod_index}.fbx"
        export_objects(bpy, [lod], path)
        outputs.append(path)
        lod_records.append({"index": lod_index, "triangles": len(lod.data.loop_triangles)})
    for path in outputs:
        if path.stat().st_size > 250 * 1024 * 1024:
            raise ValueError("OUTPUT_EXCEEDS_250MB")
    return {
        "id": row["id"], "source_sha256": sha256_file(source),
        "source": source.as_posix(), "license": row["license"],
        "source_triangles": source_triangles,
        "lod_triangle_counts": lod_records,
        "material_group": row["material_group"],
        "material_slots": [m.name if m else "" for m in base.data.materials],
        "textures": texture_receipt,
        "lods": [{"path": p.name, "bytes": p.stat().st_size,
                  "sha256": sha256_file(p)} for p in outputs],
        "collision": collision["mode"], "unreal_imported": False,
    }


def run(args) -> int:
    manifest_path = Path(args.manifest).resolve()
    ext_path = Path(args.external_manifest).resolve()
    manifest = load_json(manifest_path)
    external = load_json(ext_path)
    errors = validate_manifest(manifest)
    if errors:
        print("SHIRE_KIT_MANIFEST_INVALID " + ",".join(errors), flush=True)
        return 2
    print(f"SHIRE_KIT_MANIFEST rows={len(manifest['assets'])}", flush=True)
    source_root = Path(args.source_root).resolve()
    out_root = Path(args.out).resolve()
    quarantine = Path(args.quarantine).resolve()
    receipts = []
    pending = 0
    failed = 0
    if args.validate_only:
        for row in manifest["assets"]:
            source, reason = validate_input(row, source_root, external)
            if reason:
                pending += 1
                emit_status(row, reason)
            else:
                emit_status(row, "READY", source.relative_to(source_root).as_posix())
        print(f"SHIRE_KIT_SUMMARY ready={len(manifest['assets'])-pending} pending={pending} failed=0")
        return 0 if not pending else 3

    try:
        import bpy
    except ImportError:
        print("SHIRE_KIT_REQUIRES_BLENDER", file=sys.stderr)
        return 4
    quarantine.mkdir(parents=True, exist_ok=True)
    for row in manifest["assets"]:
        source, reason = validate_input(row, source_root, external)
        if reason:
            pending += 1
            emit_status(row, reason)
            continue
        stage = out_root / ".staging" / row["id"]
        final = out_root / row["id"]
        try:
            if final.exists():
                raise FileExistsError("OUTPUT_ALREADY_EXISTS:" + str(final))
            if stage.exists():
                shutil.rmtree(stage)
            result = build_row(bpy, row, source, stage)
            final.parent.mkdir(parents=True, exist_ok=True)
            stage.replace(final)
            result["output_dir"] = final.relative_to(out_root).as_posix()
            for item in result["lods"]:
                item["path"] = f"{result['output_dir']}/{item['path']}"
            for item in result["textures"]:
                item["path"] = Path(item["path"]).relative_to(out_root).as_posix()
            receipts.append(result)
            emit_status(row, "BUILT", f"lods={len(result['lods'])}")
        except Exception as exc:  # Asset-level fault containment is intentional.
            failed += 1
            reason = str(exc)
            detail = traceback.format_exc()
            if stage.exists():
                failed_output = quarantine / (row["id"] + ".failed")
                if not failed_output.exists():
                    failed_output.parent.mkdir(parents=True, exist_ok=True)
                    stage.replace(failed_output)
            (quarantine / f"{row['id']}.json").write_text(json.dumps({
                "id": row["id"], "status": "QUARANTINED",
                "source": row["source"], "reason": reason, "traceback": detail,
            }, indent=2) + "\n", encoding="utf-8")
            emit_status(row, "QUARANTINED", reason)
        finally:
            bpy.ops.wm.read_factory_settings(use_empty=True)
    receipt = {
        "schema_version": 1, "manifest": manifest_path.name,
        "built_assets": receipts, "pending_rows": pending,
        "quarantined_rows": failed, "unreal_imported": False,
    }
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "shire_kit_receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"SHIRE_KIT_SUMMARY built={len(receipts)} pending={pending} quarantined={failed}")
    return 0 if failed == 0 else 5


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--external-manifest", required=True)
    parser.add_argument("--source-root", default="SourceAssets/ExternalLicensed")
    parser.add_argument("--out", default="SourceAssets/Production/World/Shire/Kit")
    parser.add_argument("--quarantine", default="SourceAssets/ExternalLicensed/Quarantine/ShireKit")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
