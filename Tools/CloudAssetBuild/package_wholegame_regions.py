#!/usr/bin/env python3
"""Make ten bounded chapter source packs from the existing SHA-pinned physical 28-region FBX/PBR bank. NOT a UE importer."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile

CHAPTERS = {
    "F104_BREE_WEATHERTOP": ["BREE", "WEATHERTOP"],
    "F105_RIVENDELL": ["RIVENDELL"],
    "F106_CARADHRAS_MORIA": ["CARADHRAS", "MORIA"],
    "F107_LOTHLORIEN_ANDUIN": ["LOTHLORIEN", "ANDUIN_AMON_HEN"],
    "F108_AMON_HEN": ["ANDUIN_AMON_HEN"],
    "F201_THREE_HUNTERS": ["EMYN_MUIL", "FANGORN"],
    "F202_FANGORN_ISENGARD": ["FANGORN", "ISENGARD_ORTHANC"],
    "F203_EDORAS_MEDUSELD": ["EDORAS_MEDUSELD"],
    "F204_HELMS_DEEP_ISENGARD": ["HELMS_DEEP", "ISENGARD_ORTHANC"],
    "F3_MINAS_TIRITH_OSGILIATH": ["MINAS_TIRITH", "OSGILIATH", "PELENNOR_FIELDS"],
}

def sha(b):
    return hashlib.sha256(b).hexdigest()

def verified(root, row):
    name = row["path"]
    item = PurePosixPath(name)
    if item.is_absolute() or len(item.parts) > 5 or any(p in (".", "..") for p in item.parts):
        raise ValueError("UNSAFE_FILE:" + name)
    path = root / name
    if path.is_symlink() or not path.is_file():
        raise ValueError("MISSING_FILE:" + name)
    data = path.read_bytes()
    if len(data) != row["bytes"] or sha(data) != row["sha256"]:
        raise ValueError("SOURCE_HASH_FAILED:" + name)
    return data

def store(z, name, data):
    info = zipfile.ZipInfo(name, (2026, 10, 17, 0, 0, 0))
    info.external_attr = 0o644 << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    z.writestr(info, data)

def package(root, output, pin):
    bank = root / "_original_cloud_wholegame" / pin["source_commit"]
    source_receipt = json.loads((bank / "warehouse_receipt.json").read_text())
    if not (source_receipt["artifact_id"] == pin["artifact_id"] and
            source_receipt["source_zip_sha256"] == pin["source_zip_sha256"] and
            source_receipt["source_commit"] == pin["source_commit"] and
            len(source_receipt["files"]) == 177 and
            source_receipt["physical_fbx"] == 138 and
            source_receipt["textures_png"] == 36):
        raise ValueError("SOURCE_ARTIFACT_DRIFT")
    for row in source_receipt["files"]:
        verified(bank, row)
    regional = json.loads((bank / "regional_fbx_receipt.json").read_text())
    mats = json.loads((bank / "materials_receipt.json").read_text())
    if not (regional["region_count"] == 28 and regional["fbx_count"] == 56 and
            regional["provenance"] == "ORIGINAL_PROJECT_PROCEDURAL" and
            regional["unreal_imported"] is False and mats["runtime_imported"] is False and
            mats["physical_textures"] == 36):
        raise ValueError("SOURCE_NOT_ELIGIBLE")
    regions = {}
    for mesh in regional["objects"]:
        regions.setdefault(mesh["region_id"], []).append(mesh)
    bindings = {i["id"]: i for i in mats["region_bindings"]}
    textures = {}
    for tex in mats["textures"]:
        textures.setdefault(PurePosixPath(tex["path"]).parts[1], []).append(tex)
    if len(regions) != 28 or set(regions) != set(bindings) or len(textures) != 12:
        raise ValueError("28_REGION_PBR_REGISTRY_INCOMPLETE")
    if any({m["lod"] for m in meshes} != {0, 1} for meshes in regions.values()):
        raise ValueError("REGION_LOD0_LOD1_INCOMPLETE")
    output.mkdir(parents=True, exist_ok=True)
    index = []
    for ident, ids in [("WHOLEGAME_28_SUPPORT", sorted(regions))] + list(CHAPTERS.items()):
        files = {}
        meshes = []
        selected_textures = {}
        for rid in ids:
            meshes.extend(regions[rid])
            for surface in bindings[rid]["support_surfaces"]:
                for tex in textures[surface]:
                    selected_textures[tex["path"]] = tex
        for row in meshes:
            data = verified(bank, row)
            if not data.startswith(b"Kaydara FBX Binary"):
                raise ValueError("NOT_A_BINARY_FBX")
            files[row["path"]] = data
        for row in selected_textures.values():
            data = verified(bank, row)
            if not data.startswith(bytes.fromhex("89504e470d0a1a0a")):
                raise ValueError("NOT_A_PNG")
            files[row["path"]] = data
        receipt = {
            "pack": ident, "regions": ids, "source_artifact_id": pin["artifact_id"],
            "source_commit": pin["source_commit"], "source_zip_sha256": pin["source_zip_sha256"],
            "license": "ORIGINAL_PROJECT_ASSET", "provenance": "ORIGINAL_PROJECT_PROCEDURAL",
            "stage": "SOURCE_QC_ONLY_NOT_UE_IMPORTED", "runtime_open": False,
            "ue_imported": False, "world_placed": False, "visual_accepted": False,
            "asset_role": "LOW_POLYGON_SUPPORT_NOT_HERO_CASTLES_RIGS_OR_MONSTERS",
            "fbx": len(meshes), "png": len(selected_textures),
            "lod0_polygons": sum(x["reimport_polygons"] for x in meshes if x["lod"] == 0),
            "files": [{"path": name, "sha256": sha(data), "bytes": len(data)}
                      for name, data in sorted(files.items())],
        }
        dest = output / (ident + ".zip")
        with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for name, data in sorted(files.items()):
                store(z, name, data)
            store(z, "preproduction_receipt.json", json.dumps(receipt, indent=2).encode())
        with zipfile.ZipFile(dest) as z:
            if z.testzip() is not None or len(z.namelist()) != len(files) + 1:
                raise ValueError("PACKAGE_ZIP_INVALID")
            for name, data in files.items():
                if z.read(name) != data:
                    raise ValueError("PACKAGE_SOURCE_BYTES_DRIFT")
        index.append({"pack": ident, "regions": ids, "fbx": len(meshes),
                      "png": len(selected_textures), "lod0_polygons": receipt["lod0_polygons"],
                      "zip": dest.name, "sha256": sha(dest.read_bytes()),
                      "stage": "SOURCE_QC_ONLY_NOT_UE_IMPORTED"})
        print("WHOLEGAME_SOURCE_PACK %s regions=%d fbx=%d png=%d" %
              (ident, len(ids), len(meshes), len(selected_textures)), flush=True)
    (output / "index.json").write_text(json.dumps({
        "source_artifact_id": pin["artifact_id"], "regions": 28, "physical_support_fbx": 56,
        "physical_pbr_png": 36, "chapter_source_packs": 10,
        "stage": "SOURCE_QC_ONLY_NO_UE_OR_VISUAL_ACCEPTANCE", "packs": index
    }, indent=2) + "\n")
    print("WHOLEGAME_PARALLEL_SOURCE_PREP_PASS regions=28 supportFbx=56 png=36 packs=10", flush=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--warehouse-root", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    ap.add_argument("--pin", type=Path, required=True)
    args = ap.parse_args()
    try:
        package(args.warehouse_root, args.output_root, json.loads(args.pin.read_text()))
    except (ValueError, KeyError, IndexError, OSError, AssertionError, zipfile.BadZipFile) as exc:
        print("WHOLEGAME_PARALLEL_SOURCE_PREP_FAIL " + repr(exc), flush=True)
        return 86
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
