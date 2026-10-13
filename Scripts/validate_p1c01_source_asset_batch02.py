#!/usr/bin/env python3
"""Static validation for P1C01 off-runner generated FBX/PNG assets."""

from __future__ import annotations

import hashlib
import json
import struct
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "Data" / "P1C01SourceAssetBatch02Manifest.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_png(path: Path) -> None:
    data = path.read_bytes()
    require(data.startswith(b"\x89PNG\r\n\x1a\n"), f"not a png: {path}")
    require(len(data) > 512, f"png too small: {path}")
    require(data[12:16] == b"IHDR", f"missing IHDR: {path}")
    width, height = struct.unpack(">II", data[16:24])
    require(width == 64 and height == 64, f"unexpected png dimensions {width}x{height}: {path}")


def validate_fbx(path: Path, asset_name: str, material_slot: str, vertices: int, polygons: int) -> None:
    text = path.read_text(encoding="utf-8")
    require("; FBX 7.4.0" in text, f"missing fbx header: {path}")
    require(f"Geometry::{asset_name}" in text, f"missing geometry name: {path}")
    require(f"Model::{asset_name}" in text, f"missing model name: {path}")
    require(f"Material::{material_slot}" in text, f"missing material slot: {path}")
    require("UVChannel_1" in text, f"missing uv channel: {path}")
    require(f"Vertices: *{vertices * 3}" in text, f"unexpected vertex count: {path}")
    require(f"UV: *{polygons * 8}" in text, f"unexpected uv count: {path}")
    require("UCX_" in text, f"missing collision metadata marker: {path}")
    require(path.stat().st_size > 900, f"fbx too small: {path}")


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    records = manifest["records"]
    archive = ROOT / manifest["archive"]
    require(archive.exists(), f"missing archive: {archive}")
    require(sha256(archive) == manifest["archive_sha256"], "archive sha mismatch")
    require(manifest["runner_policy"] == "Windows Runner not used or required for this batch", "runner policy mismatch")
    require(manifest["counts"]["generated_fbx"] == len(records), "generated_fbx count mismatch")
    require(len(records) == 48, "batch02 must contain 48 mesh assets")
    temp_root = Path(tempfile.mkdtemp(prefix="p1c01_batch02_validate_"))
    with zipfile.ZipFile(archive) as zipped:
        names = zipped.namelist()
        require(len([name for name in names if name.lower().endswith(".fbx")]) == 48, "archive fbx count mismatch")
        require(len([name for name in names if name.lower().endswith(".png")]) == 16, "archive png count mismatch")
        zipped.extractall(temp_root)
    seen_hashes = set()
    seen_assets = set()
    seen_textures = set()
    zones = set()
    for record in records:
        fbx = temp_root / record["fbx_archive_member"]
        png = temp_root / record["base_color_archive_member"]
        require(fbx.exists(), f"missing fbx: {fbx}")
        require(png.exists(), f"missing png: {png}")
        require(record["asset_name"] not in seen_assets, f"duplicate asset: {record['asset_name']}")
        seen_assets.add(record["asset_name"])
        zones.add(record["target_zone"])
        validate_fbx(fbx, record["asset_name"], record["material_slot"], record["vertices"], record["polygons"])
        validate_png(png)
        require(sha256(fbx) == record["fbx_sha256"], f"fbx sha mismatch: {fbx}")
        require(sha256(png) == record["base_color_sha256"], f"png sha mismatch: {png}")
        require(record["fbx_sha256"] not in seen_hashes, f"duplicate fbx content hash: {fbx}")
        seen_hashes.add(record["fbx_sha256"])
        seen_textures.add(record["base_color_archive_member"])
        require(record["unreal_import_status"] == "PENDING", "must not claim UE import")
        require(record["world_population_status"] == "PENDING", "must not claim world placement")
    require(len(zones) >= 6, f"too few target zones: {sorted(zones)}")
    require(manifest["counts"]["generated_png"] == len(seen_textures), "generated_png unique count mismatch")
    print(
        "P1C01_SOURCE_ASSET_BATCH02_STATIC_PASS "
        f"fbx={len(records)} png={len(seen_textures)} zones={len(zones)}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"P1C01_SOURCE_ASSET_BATCH02_STATIC_FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)
