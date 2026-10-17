"""MPFB2 -> original Hobbit-source FBX pilot, fail-closed and source-only.

Run INSIDE Blender with the official MPFB2 extension and core system asset pack
installed. Never overwrite an existing output. Not an Unreal import or an
acceptance test: export geometry, texture sidecars, metadata and skin metrics.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import re
import shutil
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mpfb_pose_qc import inspect_deform_and_pose


def mpfb_api(suffix: str, symbol: str):
    for name in list(sys.modules):
        if name.endswith(suffix):
            module = importlib.import_module(name)
            if hasattr(module, symbol):
                return getattr(module, symbol)
    raise RuntimeError("MPFB2_EXTENSION_NOT_LOADED: " + suffix)


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    if "--" not in sys.argv:
        raise RuntimeError("SPEC_AND_OUTPUT_ARGUMENTS_REQUIRED")
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    spec_path = args.spec.resolve(strict=True)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out = args.out.resolve()
    if out.exists():
        raise RuntimeError("OUTPUT_MUST_NOT_EXIST_TO_PREVENT_OVERWRITE: " + str(out))
    if spec.get("pack_license") != "CC0" or spec.get("required_asset_pack") != "makehuman_system_assets":
        raise RuntimeError("LICENSE_OR_CORE_ASSET_PACK_NOT_APPROVED")
    if not re.fullmatch(r"[A-Z][A-Z0-9_]{4,95}", spec.get("pilot_id", "")):
        raise RuntimeError("INVALID_CHARACTER_ID")
    if spec.get("rig") not in ("game_engine", "mixamo"):
        raise RuntimeError("UNSUPPORTED_MPFB_RIG")
    if not spec.get("skin") or not spec.get("parts"):
        raise RuntimeError("SKIN_AND_EQUIPPED_BODY_PARTS_REQUIRED")

    if bpy.app.version < (4, 2, 0):
        raise RuntimeError("MPFB2_REQUIRES_BLENDER_4_2_OR_NEWER")
    # MPFB2 is a Blender extension; headless sessions may have it installed but disabled.
    if not any(name.endswith("mpfb.services.humanservice") for name in sys.modules):
        import addon_utils
        candidates = [module.__name__ for module in addon_utils.modules(refresh=True)
                      if module.__name__.split(".")[-1] == "mpfb"]
        if len(candidates) != 1:
            raise RuntimeError("MPFB2_EXTENSION_NOT_INSTALLED_OR_AMBIGUOUS")
        addon_utils.enable(candidates[0], default_set=False, persistent=False)

    HumanService = mpfb_api("mpfb.services.humanservice", "HumanService")
    AssetService = mpfb_api("mpfb.services.assetservice", "AssetService")
    ExportService = mpfb_api("mpfb.services.exportservice", "ExportService")
    ObjectService = mpfb_api("mpfb.services.objectservice", "ObjectService")
    HumanObjectProperties = mpfb_api("mpfb.entities.objectproperties", "HumanObjectProperties")
    TargetService = mpfb_api("mpfb.services.targetservice", "TargetService")

    # Resolve every referenced asset BEFORE creating any generated output.
    skin = AssetService.find_asset_absolute_path(spec["skin"], asset_subdir="skins")
    if not skin or not Path(skin).is_file():
        raise RuntimeError("MPFB_CORE_SKIN_MISSING: " + str(spec["skin"]))
    resolved_parts = []
    allowed_parts = {"Eyes", "Eyebrows", "Eyelashes", "Tongue", "Teeth", "Hair", "Clothes"}
    for part in spec["parts"]:
        if part["asset_type"] not in allowed_parts or part["subdir"] != part["asset_type"].lower():
            raise RuntimeError("UNSUPPORTED_MPFB_BODY_PART: " + str(part))
        path = AssetService.find_asset_absolute_path(part["name"], asset_subdir=part["subdir"])
        if not path or not Path(path).is_file():
            raise RuntimeError("MPFB_CORE_ASSET_MISSING: " + part["name"])
        resolved_parts.append((part, path))
    types = {part["asset_type"] for part, _ in resolved_parts}
    if not {"Eyes", "Hair", "Clothes"}.issubset(types):
        raise RuntimeError("REAL_CHARACTER_REQUIRES_EYES_HAIR_CLOTHES")

    human = HumanService.create_human()
    for key, value in spec.get("phenotype", {}).items():
        if key not in {"gender", "age", "weight", "muscle", "height"}:
            raise RuntimeError("UNSUPPORTED_PHENOTYPE_KEY: " + key)
        if not isinstance(value, (float, int)) or not (0.0 <= value <= 1.0):
            raise RuntimeError("INVALID_PHENOTYPE_VALUE")
        HumanObjectProperties.set_value(key, float(value), entity_reference=human)
    if spec.get("phenotype"):
        TargetService.reapply_macro_details(human)
    HumanService.set_character_skin(skin, human, skin_type="GAMEENGINE")
    rig = HumanService.add_builtin_rig(human, spec["rig"])
    if rig is None or rig.type != "ARMATURE" or len(rig.data.bones) < 8:
        raise RuntimeError("MPFB_BONE_HIERARCHY_MISSING")
    for part, path in resolved_parts:
        HumanService.add_mhclo_asset(path, human, asset_type=part["asset_type"], material_type="GAMEENGINE")

    root = ExportService.create_character_copy(human, name_suffix="_shire_export")
    body = ObjectService.find_object_of_type_amongst_nearest_relatives(root, "Basemesh")
    if body is None or body.type != "MESH":
        raise RuntimeError("MPFB_EXPORTED_BASEMESH_MISSING")
    ExportService.bake_modifiers_remove_helpers(
        body, bake_masks=True, bake_subdiv=True, remove_helpers=True, also_proxy=True)

    relatives = [root] + list(ObjectService.get_list_of_children(root))
    meshes = [o for o in relatives if o.type == "MESH"]
    bones = [o for o in relatives if o.type == "ARMATURE"]
    if not bones or len(meshes) < 4:
        raise RuntimeError("MPFB_EXPORT_RIG_OR_EQUIPMENT_MISSING")
    if not all(len(m.data.uv_layers) for m in meshes):
        raise RuntimeError("MPFB_EXPORTED_UV_MISSING")
    # Inspect the actual exported deform-bone vertex groups, not helper weights;
    # bend both a lower arm and lower leg and measure real evaluated mesh motion.
    weighted, pose_deformation = inspect_deform_and_pose(body, bones[0])
    vertices = sum(len(m.data.vertices) for m in meshes)
    faces = sum(len(m.data.polygons) for m in meshes)

    out.mkdir(parents=True, exist_ok=False)
    texture_dir = out / "Textures"
    texture_dir.mkdir()
    textures = []
    known = {}
    for mesh in meshes:
        for material in mesh.data.materials:
            if not material or not material.use_nodes:
                continue
            for node in material.node_tree.nodes:
                if node.type != "TEX_IMAGE" or not node.image or node.image.source != "FILE":
                    continue
                image = node.image
                original = Path(bpy.path.abspath(image.filepath)).resolve()
                if not original.is_file():
                    raise RuntimeError("MPFB_PBR_TEXTURE_FILE_MISSING: " + str(original))
                digest = file_sha256(original)
                if image.name in known:
                    if known[image.name] != digest:
                        raise RuntimeError("DUPLICATE_TEXTURE_NAME_DIFFERENT_BYTES: " + image.name)
                    continue
                known[image.name] = digest
                dest = texture_dir / (digest[:12] + "_" + original.name)
                shutil.copyfile(original, dest)
                image.filepath = str(dest)
                textures.append({"name": dest.name, "sha256": digest})

    if not textures:
        raise RuntimeError("MPFB_NO_PORTABLE_AUTHOR_SKIN_OR_COSTUME_TEXTURE_SIDECARS")

    bpy.ops.object.select_all(action="DESELECT")
    for obj in relatives:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    fbx = out / (spec["pilot_id"] + ".fbx")
    bpy.ops.export_scene.fbx(
        filepath=str(fbx), use_selection=True, add_leaf_bones=False,
        bake_anim=False, path_mode="RELATIVE", embed_textures=False)
    if not fbx.is_file() or fbx.stat().st_size < 1024:
        raise RuntimeError("MPFB_FBX_EMPTY")

    receipt = {
        "status": "SOURCE_FBX_PREPARED_NOT_UE_IMPORTED",
        "character_id": spec["pilot_id"],
        "spec_sha256": file_sha256(spec_path),
        "fbx_name": fbx.name,
        "fbx_sha256": file_sha256(fbx),
        "license": spec["pack_license"],
        "license_url": spec["pack_license_evidence"],
        "mpfb_rig": spec["rig"],
        "source_pack": spec["required_asset_pack"],
        "mesh_count": len(meshes),
        "bone_count": max(len(a.data.bones) for a in bones),
        "vertices": vertices,
        "faces_not_triangulated": faces,
        "weighted_body_vertices": weighted,
        "blender_joint_deformation": pose_deformation,
        "blender_joint_deformation_evidence": "POSED_EVALUATED_MESH_LOCAL_ONLY_NOT_UE4",
        "texture_sidecars": textures,
        "ue_import": "NOT_RUN",
        "pie_deformation": "NOT_RUN",
        "visual_acceptance": "NOT_RUN",
    }
    (out / "source_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("PES002_MPFB_SOURCE_CANDIDATE_PREPARED " + json.dumps(receipt, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
