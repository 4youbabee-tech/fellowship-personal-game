#!/usr/bin/env python3
"""Manifest-driven, per-row Shire static-mesh intake for Blender/UE4.27.

This tool never creates replacement geometry. It imports a licensed source,
normalizes/validates it, writes three binary FBX LODs, and quarantines a row
when source, license, UV, geometry, or export checks fail.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import traceback
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_row(row: object, root: Path) -> tuple[Path, list[str]]:
    root = root.resolve()
    if not isinstance(row, dict):
        return root, ["ROW_NOT_OBJECT"]
    errors: list[str] = []
    for key in ("id", "source", "license", "target_tris", "lods", "collision", "material_groups"):
        if key not in row:
            errors.append(f"MISSING_{key.upper()}")
    if errors:
        return root, errors
    ident = row["id"]
    if not isinstance(ident, str) or not ident.replace("_", "").isalnum():
        errors.append("INVALID_ID")
    license_info = row["license"]
    if not isinstance(license_info, dict) or license_info.get("status") != "VERIFIED" or not license_info.get("evidence_url"):
        errors.append("LICENSE_NOT_VERIFIED")
    source_info = row["source"]
    if not isinstance(source_info, dict) or not isinstance(source_info.get("path"), str) or not source_info["path"].strip():
        return root, errors + ["SOURCE_PATH_MISSING"]
    source_rel = Path(source_info["path"])
    source = (root / source_rel).resolve()
    if source_rel.is_absolute() or (source != root and root not in source.parents):
        errors.append("SOURCE_PATH_ESCAPES_ROOT")
    if not source.is_file():
        errors.append("SOURCE_FILE_MISSING")
    expected_hash = source_info.get("source_sha256")
    if expected_hash is not None:
        if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected_hash):
            errors.append("INVALID_SOURCE_SHA256")
        elif source.is_file() and sha256(source).lower() != expected_hash.lower():
            errors.append("SOURCE_SHA256_MISMATCH")
    if not isinstance(row["target_tris"], int) or isinstance(row["target_tris"], bool) or row["target_tris"] < 12:
        errors.append("INVALID_TRIANGLE_BUDGET")
    lods = row["lods"]
    if not isinstance(lods, list) or lods != [1.0, 0.5, 0.25]:
        errors.append("EXPECTED_THREE_LOD_RATIOS")
    if row["collision"] not in ("convex_hull", "none"):
        errors.append("INVALID_COLLISION_POLICY")
    dims = row.get("dimensions_m")
    if (not isinstance(dims, list) or len(dims) != 3 or
            any(not isinstance(value, (int, float)) or isinstance(value, bool) or
                not math.isfinite(value) or value <= 0 for value in dims)):
        errors.append("INVALID_DIMENSIONS_M")
    groups = row["material_groups"]
    if not isinstance(groups, list) or any(not isinstance(value, str) or not value.strip() for value in groups):
        errors.append("INVALID_MATERIAL_GROUPS")
    return source, errors


def preflight(manifest: dict, root: Path) -> tuple[list[dict], list[dict]]:
    good, rejected = [], []
    rows = manifest.get("assets")
    if not isinstance(rows, list):
        raise ValueError("manifest.assets must be an array")
    seen: set[str] = set()
    for row_number, row in enumerate(rows, start=1):
        raw_ident = row.get("id") if isinstance(row, dict) else None
        ident = raw_ident if isinstance(raw_ident, str) else f"<row-{row_number}>"
        errors = []
        if isinstance(raw_ident, str) and raw_ident in seen:
            errors.append("DUPLICATE_ID")
        if isinstance(raw_ident, str):
            seen.add(raw_ident)
        source, row_errors = validate_row(row, root)
        errors.extend(row_errors)
        entry = {"id": ident, "row_number": row_number, "source": source,
                 "row": row if isinstance(row, dict) else {}}
        (rejected if errors else good).append({**entry, "errors": errors} if errors else entry)
    return good, rejected


def blender_build(entry: dict, root: Path, out: Path) -> dict:
    import bpy  # Imported only inside Blender; preflight stays cheap on CI.
    import bmesh
    from mathutils import Vector

    row, ident, source = entry["row"], entry["id"], entry["source"]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ext = source.suffix.lower()
    if ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(source), use_anim=False)
    elif ext == ".obj":
        if hasattr(bpy.ops.wm, "obj_import"):
            bpy.ops.wm.obj_import(filepath=str(source))
        else:
            bpy.ops.import_scene.obj(filepath=str(source))
    elif ext in (".gltf", ".glb"):
        bpy.ops.import_scene.gltf(filepath=str(source))
    else:
        raise ValueError(f"UNSUPPORTED_SOURCE_FORMAT:{ext}")

    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not meshes:
        raise ValueError("NO_MESHES_IMPORTED")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.join()
    visual = bpy.context.object
    visual.name = f"SM_{ident}"
    cleanup = bmesh.new()
    cleanup.from_mesh(visual.data)
    bmesh.ops.remove_doubles(cleanup, verts=list(cleanup.verts), dist=0.0001)
    bmesh.ops.recalc_face_normals(cleanup, faces=list(cleanup.faces))
    cleanup.to_mesh(visual.data)
    cleanup.free()
    visual.data.update()
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    # Use the declared game-unit dimensions (metres); retain proportions.
    dims = row.get("dimensions_m")
    if not isinstance(dims, list) or len(dims) != 3 or min(dims) <= 0:
        raise ValueError("INVALID_DIMENSIONS_M")
    size = max(visual.dimensions)
    target = max(dims)
    if size <= 0:
        raise ValueError("ZERO_BOUNDS")
    visual.scale *= target / size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    actual_dims = list(visual.dimensions)
    tolerance = float(row.get("dimension_tolerance", 0.25))
    if any(abs(actual - expected) / expected > tolerance for actual, expected in zip(actual_dims, dims)):
        raise ValueError(f"DIMENSION_RATIO_MISMATCH:actual={actual_dims}:expected={dims}")
    min_z = min((visual.matrix_world @ Vector(corner)).z for corner in visual.bound_box)
    visual.location.z -= min_z
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

    if not visual.data.uv_layers:
        bpy.context.view_layer.objects.active = visual
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(island_margin=0.015)
        bpy.ops.object.mode_set(mode="OBJECT")
    if not visual.data.uv_layers or len(visual.data.uv_layers[0].data) != len(visual.data.loops):
        raise ValueError("UV0_INVALID")
    material_names = {slot.material.name for slot in visual.material_slots if slot.material}
    if not material_names:
        raise ValueError("NO_SOURCE_MATERIALS")
    expected_groups = set(row["material_groups"])
    if expected_groups and not (material_names & expected_groups):
        raise ValueError("MATERIAL_GROUP_MISMATCH:" + ",".join(sorted(material_names)))

    output_rows = []
    ratios = row["lods"]
    for lod, ratio in enumerate(ratios):
        bpy.ops.object.select_all(action="DESELECT")
        duplicate = visual.copy()
        duplicate.data = visual.data.copy()
        bpy.context.collection.objects.link(duplicate)
        duplicate.name = f"SM_{ident}_LOD{lod}"
        if lod:
            mod = duplicate.modifiers.new("ShireLODDecimate", "DECIMATE")
            mod.ratio = ratio
            bpy.context.view_layer.objects.active = duplicate
            bpy.ops.object.modifier_apply(modifier=mod.name)
        tris = sum(len(poly.vertices) - 2 for poly in duplicate.data.polygons)
        if tris > row["target_tris"]:
            raise ValueError(f"TRIANGLE_BUDGET_EXCEEDED:LOD{lod}:{tris}>{row['target_tris']}")
        chosen = [duplicate]
        collider = None
        if row["collision"] == "convex_hull":
            bm = bmesh.new()
            bm.from_mesh(duplicate.data)
            bmesh.ops.convex_hull(bm, input=list(bm.verts))
            mesh = bpy.data.meshes.new(f"UCX_SM_{ident}_LOD{lod}_00")
            bm.to_mesh(mesh)
            bm.free()
            collider = bpy.data.objects.new(mesh.name, mesh)
            bpy.context.collection.objects.link(collider)
            chosen.append(collider)
        bpy.ops.object.select_all(action="DESELECT")
        for obj in chosen:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = duplicate
        target_dir = out / "meshes"
        target_dir.mkdir(parents=True, exist_ok=True)
        dest = target_dir / f"SM_{ident}_LOD{lod}.fbx"
        bpy.ops.export_scene.fbx(filepath=str(dest), use_selection=True, object_types={"MESH"},
            mesh_smooth_type="FACE", add_leaf_bones=False, axis_forward="-Y", axis_up="Z",
            bake_anim=False, embed_textures=False, path_mode="COPY")
        if not dest.is_file() or dest.stat().st_size < 1024:
            raise ValueError(f"FBX_EXPORT_EMPTY:LOD{lod}")
        pre_import = set(bpy.context.scene.objects)
        bpy.ops.import_scene.fbx(filepath=str(dest), use_anim=False)
        imported = [obj for obj in bpy.context.scene.objects if obj not in pre_import]
        imported_visuals = [obj for obj in imported if obj.type == "MESH" and not obj.name.startswith("UCX_")]
        imported_colliders = [obj for obj in imported if obj.type == "MESH" and obj.name.startswith("UCX_")]
        if len(imported_visuals) != 1 or not imported_visuals[0].data.uv_layers:
            raise ValueError(f"FBX_REIMPORT_VISUAL_OR_UV_FAIL:LOD{lod}")
        if row["collision"] == "convex_hull" and not imported_colliders:
            raise ValueError(f"FBX_REIMPORT_COLLISION_FAIL:LOD{lod}")
        reimport_tris = sum(len(poly.vertices) - 2 for poly in imported_visuals[0].data.polygons)
        if reimport_tris <= 0 or reimport_tris > row["target_tris"]:
            raise ValueError(f"FBX_REIMPORT_TRIANGLE_FAIL:LOD{lod}:{reimport_tris}")
        output_rows.append({"lod": lod, "path": str(dest.relative_to(out)), "sha256": sha256(dest),
            "bytes": dest.stat().st_size, "triangles": tris, "reimport_triangles": reimport_tris, "uv0": True,
            "collision": collider.name if collider else "none"})
        for obj in imported:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.objects.remove(duplicate, do_unlink=True)
        if collider:
            bpy.data.objects.remove(collider, do_unlink=True)
    return {"id": ident, "source_sha256": sha256(source), "license": row["license"], "outputs": output_rows}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else None)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    good, rejected = preflight(manifest, args.root.resolve())
    args.out.mkdir(parents=True, exist_ok=True)
    receipt = {"schema_version": 1, "loaded": len(manifest["assets"]), "placed": 0,
        "rejected": len(rejected), "assets": [], "quarantine": []}
    for item in rejected:
        row = {"id": item["id"], "row_number": item["row_number"], "errors": item["errors"]}
        receipt["quarantine"].append(row)
        qdir = args.out / "quarantine"
        qdir.mkdir(exist_ok=True)
        safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", item["id"]).strip("_") or "invalid"
        (qdir / f"{safe_id[:80]}__row_{item['row_number']:04d}.json").write_text(
            json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if not args.preflight_only:
        for item in good:
            try:
                result = blender_build(item, args.root.resolve(), args.out)
                receipt["assets"].append(result)
                receipt["placed"] += 1
            except Exception as exc:
                row = {"id": item["id"], "errors": [str(exc)], "traceback": traceback.format_exc()}
                receipt["quarantine"].append(row)
                receipt["rejected"] += 1
                safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", item["id"]).strip("_") or "invalid"
                (args.out / "quarantine" / f"{safe_id[:80]}__row_{item['row_number']:04d}.json").write_text(
                    json.dumps(row, indent=2) + "\n", encoding="utf-8")
    (args.out / "shire_kit_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"SHIRE_KIT_PREFLIGHT loaded={receipt['loaded']} placed={receipt['placed']} rejected={receipt['rejected']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
