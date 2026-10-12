#!/usr/bin/env python3
"""Stage pinned physical Shire + 28-region source into the single persistent warehouse.

The stage is SOURCE-ONLY. It does not execute Unreal, claim imported .uasset
packages, change content in the git checkout or promote chapter Gate 6/7.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import struct
import sys
import tempfile
import urllib.request
import zipfile

FBX_MAGIC = b"Kaydara FBX Binary"
PNG_MAGIC = bytes.fromhex("89504e470d0a1a0a")
MAX_OUTER_BYTES = 32 * 1024 * 1024
MAX_UNPACKED_BYTES = 256 * 1024 * 1024
MIN_RESERVE = 1024 * 1024 * 1024


class IntakeError(ValueError):
    pass


def require(value, message):
    if not value:
        raise IntakeError(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_name(name: str) -> str:
    require(isinstance(name, str) and name and
            "\\" not in name and ":" not in name and "\x00" not in name,
            "UNSAFE_ZIP_PATH")
    path = PurePosixPath(name)
    require(not path.is_absolute() and all(p not in (".", "..") for p in path.parts)
            and len(path.parts) <= 5, "UNSAFE_ZIP_PATH")
    return name


def members(archive: zipfile.ZipFile) -> dict:
    result = {}
    uncompressed = 0
    for item in archive.infolist():
        name = safe_name(item.filename)
        require(not item.is_dir() and name not in result, "DUPLICATE_OR_DIR_MEMBER")
        require((item.external_attr >> 16) & 0o170000 != 0o120000,
                "ZIP_SYMLINK_REJECTED")
        uncompressed += item.file_size
        require(item.file_size <= 16 * 1024 * 1024 and
                uncompressed <= MAX_UNPACKED_BYTES, "ZIP_SIZE_BUDGET")
        result[name] = item
    return result


def read_receipt(z: zipfile.ZipFile, key: str):
    value = json.loads(z.read(key).decode("utf-8"))
    require(isinstance(value, dict), "BAD_RECEIPT:" + key)
    return value


def validate_payload(archive: bytes, manifest: dict):
    require(len(archive) <= MAX_OUTER_BYTES and
            sha(archive) == manifest["source_zip_sha256"], "SOURCE_ZIP_HASH_MISMATCH")
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        present = members(z)
        region = read_receipt(z, "regional_fbx_receipt.json")
        shire = read_receipt(z, "fbx_receipt.json")
        surfaces = read_receipt(z, "materials_receipt.json")
        require(region.get("region_count") == 28 and
                region.get("fbx_count") == 56 and
                len(region.get("objects", [])) == 56 and
                region.get("warehouse_persisted") is False and
                region.get("unreal_imported") is False, "REGION_RECEIPT_DRIFT")
        require(shire.get("asset_count") == 41 and
                shire.get("fbx_count") == 82 and
                len(shire.get("objects", [])) == 82 and
                shire.get("runtime_imported") is False, "SHIRE_RECEIPT_DRIFT")
        require(surfaces.get("material_families") == 12 and
                surfaces.get("physical_textures") == 36 and
                len(surfaces.get("textures", [])) == 36 and
                len(surfaces.get("region_bindings", [])) == 28 and
                surfaces.get("runtime_imported") is False, "MATERIAL_RECEIPT_DRIFT")
        require(shire.get("provenance") == "ORIGINAL_PROJECT_PROCEDURAL_GEOMETRY"
                and region.get("provenance") == "ORIGINAL_PROJECT_PROCEDURAL"
                and surfaces.get("license") == "ORIGINAL_PROJECT_ASSET",
                "PROVENANCE_DRIFT")
        regions = {x["id"] for x in surfaces["region_bindings"]}
        all_regions = {x["region_id"] for x in region["objects"]}
        require(len(regions) == 28 and regions == all_regions, "REGION_IDENTITY_DRIFT")
        mesh_items = [(x, "meshes/", "export_format") for x in shire["objects"]]
        mesh_items += [(x, "regional_meshes/", "format") for x in region["objects"]]
        paths = set()
        digests = set()
        shire_families = set()
        region_lods = set()
        for row, prefix, format_key in mesh_items:
            name = safe_name(row["path"])
            require(name.startswith(prefix) and name.endswith(".fbx") and
                    name in present and name not in paths, "FBX_IDENTITY_DRIFT")
            paths.add(name)
            data = z.read(name)
            require(len(data) >= 1024 and len(data) == row["bytes"] and
                    sha(data) == row["sha256"], "FBX_DIGEST_OR_SIZE_MISMATCH:" + name)
            require(data.startswith(FBX_MAGIC) and
                    struct.unpack("<I", data[23:27])[0] == 7400 and
                    row[format_key] == "FBX_BINARY_7400", "FBX_FORMAT_INVALID:" + name)
            require(row.get("lod") in (0, 1) and
                    row.get("collider_count", 0) >= 1, "FBX_LOD_UCX_INVALID:" + name)
            if prefix == "meshes/":
                require(row.get("reimport_uv_layers", 0) >= 1 and
                        row.get("reimport_polygons", 0) > 0, "SHIRE_REIMPORT_MISSING")
                shire_families.add((row["asset"], row["lod"]))
            else:
                require(row.get("uv_layers", 0) >= 1 and
                        row.get("reimport_polygons", 0) > 0,
                        "REGION_REIMPORT_MISSING")
                region_lods.add((row["region_id"], row["lod"]))
            require(row["sha256"] not in digests, "DUPLICATE_PHYSICAL_FBX_HASH")
            digests.add(row["sha256"])
        require(len(shire_families) == 82 and len(region_lods) == 56 and
                region_lods == {(x, lod) for x in regions for lod in (0, 1)},
                "LOD_IDENTITY_COVERAGE_FAIL")
        for row in surfaces["textures"]:
            name = safe_name(row["path"])
            require(name.startswith("materials/") and name.endswith(".png") and
                    name not in paths and name in present, "PNG_IDENTITY_INVALID")
            paths.add(name)
            data = z.read(name)
            require(len(data) == row["bytes"] and sha(data) == row["sha256"] and
                    data[:8] == PNG_MAGIC and data[12:16] == b"IHDR" and
                    list(struct.unpack(">II", data[16:24])) == [1024, 1024] and
                    row["dimensions"] == [1024, 1024],
                    "PNG_HASH_OR_DIMENSIONS_INVALID:" + name)
        require(len(paths) == 174 and
                set(present) == paths | {"fbx_receipt.json",
                                        "regional_fbx_receipt.json",
                                        "materials_receipt.json"},
                "UNDECLARED_OR_MISSING_SOURCE_FILE")
        require(z.testzip() is None, "SOURCE_ZIP_CRC_FAILURE")
        return {"physical_fbx": 138, "shire_fbx": 82, "regional_fbx": 56,
                "textures_png": 36, "region_count": 28,
                "file_count": len(present), "bytes_zip": len(archive),
                "source_zip_sha256": sha(archive)}


def inspect_saved(folder: Path, source_hash: str):
    receipt_file = folder / "warehouse_receipt.json"
    require(receipt_file.is_file() and not receipt_file.is_symlink(),
            "WAREHOUSE_RECEIPT_MISSING")
    receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
    require(receipt["source_zip_sha256"] == source_hash and
            receipt["stage"] == "PERSISTENT_SOURCE_WAREHOUSE_QC_ONLY",
            "WAREHOUSE_RECEIPT_DRIFT")
    for row in receipt["files"]:
        target = folder / safe_name(row["path"])
        require(target.is_file() and not target.is_symlink() and
                target.stat().st_size == row["bytes"] and
                sha(target.read_bytes()) == row["sha256"],
                "WAREHOUSE_FILE_CHANGED:" + str(target))
    require(len(receipt["files"]) == 177, "WAREHOUSE_FILE_COUNT_DRIFT")
    return receipt


def stage_archive(archive: bytes, config: dict, root: Path, artifact_id: int):
    result = validate_payload(archive, config)
    dest = root / "_original_cloud_wholegame" / config["source_commit"]
    require(root.is_dir() and not root.is_symlink(), "WAREHOUSE_ROOT_NOT_PRESENT")
    base = dest.parent
    base.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        receipt = inspect_saved(dest, result["source_zip_sha256"])
        print("CLOUD_WHOLEGAME_WAREHOUSE_REUSED fbx=138 png=36 regions=28", flush=True)
        return receipt
    require(shutil.disk_usage(root).free >=
            MAX_UNPACKED_BYTES + MIN_RESERVE, "WAREHOUSE_DISK_RESERVE_LOW")
    temp = Path(tempfile.mkdtemp(prefix=".cloud138_", dir=base))
    try:
        files = []
        with zipfile.ZipFile(io.BytesIO(archive)) as source:
            for name in sorted(members(source)):
                data = source.read(name)
                path = temp / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                require(sha(path.read_bytes()) == sha(data), "POST_COPY_HASH_MISMATCH")
                files.append({"path": name, "sha256": sha(data), "bytes": len(data)})
        receipt = {**result, "schema_version": 1,
                   "stage": "PERSISTENT_SOURCE_WAREHOUSE_QC_ONLY",
                   "artifact_id": artifact_id,
                   "source_commit": config["source_commit"],
                   "run_id": config["workflow_run_id"],
                   "files": files,
                   "unreal_imported": False, "pie_tested": False,
                   "device_tested": False, "visual_accepted": False,
                   "gate67_accepted": False}
        (temp / "warehouse_receipt.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        temp.rename(dest)
        inspect_saved(dest, result["source_zip_sha256"])
        print("CLOUD_WHOLEGAME_PERSISTENT_WAREHOUSE_PASS fbx=138 shire=82 regional=56 png=36 regions=28",
              flush=True)
        return receipt
    finally:
        if temp.exists():
            shutil.rmtree(temp)


class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        result = super().redirect_request(req, fp, code, msg, headers, newurl)
        if result and not newurl.startswith("https://api.github.com/"):
            result.remove_header("Authorization")
            result.remove_header("authorization")
        return result


def fetch_artifact(config: dict, token: str):
    require(bool(token), "GITHUB_ACTIONS_READ_TOKEN_MISSING")
    base = "https://api.github.com/repos/" + config["repository"]
    url = base + "/actions/artifacts/" + str(config["artifact_id"])
    opener = urllib.request.build_opener(SafeRedirect())
    headers = {"Authorization": "Bearer " + token, "User-Agent": "ShireJourney-warehouse",
               "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    with opener.open(urllib.request.Request(url, headers=headers), timeout=60) as response:
        metadata = json.loads(response.read(65536))
    require(metadata.get("id") == config["artifact_id"] and
            metadata.get("name") == config["artifact_name"] and
            not metadata.get("expired") and
            metadata.get("size_in_bytes") == config["artifact_wrapper_bytes"] and
            metadata.get("digest") == "sha256:" + config["artifact_wrapper_sha256"],
            "REMOTE_ARTIFACT_IDENTITY_CHANGED")
    with opener.open(urllib.request.Request(url + "/zip", headers=headers),
                     timeout=180) as response:
        payload = response.read(MAX_OUTER_BYTES + 1)
    require(len(payload) <= MAX_OUTER_BYTES and
            sha(payload) == config["artifact_wrapper_sha256"],
            "ARTIFACT_WRAPPER_HASH_MISMATCH")
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        listing = members(z)
        require(set(listing) == {config["inner_zip_name"]},
                "ARTIFACT_WRAPPER_CONTENT_MISMATCH")
        content = z.read(config["inner_zip_name"])
    return content


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--warehouse-root", type=Path, required=True)
    ap.add_argument("--artifact-file", type=Path, help="Offline test only; bypass download")
    args = ap.parse_args()
    try:
        config = json.loads(args.manifest.read_text(encoding="utf-8"))
        require(config["repository"] == "4youbabee-tech/fellowship-personal-game" and
                config["artifact_id"] == 11767251532 and
                config["workflow_run_id"] == 38292163970 and
                config["source_commit"] == "1e1e5c9df5aeee75e130eed7891fdfb7b129c9fc",
                "PINNED_ARTIFACT_MANIFEST_DRIFT")
        payload = (args.artifact_file.read_bytes() if args.artifact_file else
                   fetch_artifact(config, os.environ.get("GH_TOKEN", "")))
        stage_archive(payload, config, args.warehouse_root, config["artifact_id"])
        return 0
    except (KeyError, OSError, ValueError, zipfile.BadZipFile, AssertionError) as exc:
        print("CLOUD_WHOLEGAME_WAREHOUSE_FAIL " + str(exc), file=sys.stderr)
        return 86


if __name__ == "__main__":
    raise SystemExit(main())
