#!/usr/bin/env python3
"""Static validation for P1C01 off-runner generated PBR material source maps."""

from __future__ import annotations

import hashlib
import json
import struct
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "Data" / "P1C01MaterialSourceBatch01Manifest.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    require(data.startswith(b"\x89PNG\r\n\x1a\n"), f"not png: {path}")
    require(data[12:16] == b"IHDR", f"missing IHDR: {path}")
    width, height = struct.unpack(">II", data[16:24])
    require(data[24] == 8 and data[25] == 6, f"expected RGBA8 png: {path}")
    require(path.stat().st_size > 512, f"png too small: {path}")
    return width, height


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    archive = ROOT / manifest["archive"]
    records = manifest["records"]
    require(archive.exists(), f"missing archive: {archive}")
    require(sha256(archive) == manifest["archive_sha256"], "archive sha mismatch")
    require(manifest["runner_policy"] == "Windows Runner not used or required for this batch", "runner policy mismatch")
    require(len(records) == 24, "material batch01 must contain 24 material sets")
    require(manifest["counts"]["generated_png"] == 72, "png count mismatch")
    require(manifest["counts"]["base_color"] == 24, "base color count mismatch")
    require(manifest["counts"]["orm_packed"] == 24, "orm count mismatch")
    require(manifest["counts"]["normal"] == 24, "normal count mismatch")

    temp_root = Path(tempfile.mkdtemp(prefix="p1c01_material_batch01_validate_"))
    with zipfile.ZipFile(archive) as zipped:
        names = zipped.namelist()
        require(len([n for n in names if n.lower().endswith(".png")]) == 72, "archive png count mismatch")
        zipped.extractall(temp_root)

    material_names = set()
    texture_hashes = set()
    zones = set()
    families = set()
    for record in records:
        name = record["material_name"]
        require(name not in material_names, f"duplicate material: {name}")
        material_names.add(name)
        zones.add(record["target_zone"])
        families.add(record["surface_family"])
        require(record["warehouse_status"] == "PENDING", f"warehouse status must remain pending: {name}")
        require(record["unreal_import_status"] == "PENDING", f"unreal import status must remain pending: {name}")
        require(record["material_instance_status"] == "PENDING", f"material instance status must remain pending: {name}")
        require(record["world_binding_status"] == "PENDING", f"world binding status must remain pending: {name}")
        members = record["texture_set_members"]
        hashes = record["texture_sha256"]
        require(set(members.keys()) == {"base_color", "orm_packed", "normal"}, f"map set mismatch: {name}")
        for map_type, member in members.items():
            path = temp_root / member
            require(path.exists(), f"missing map: {member}")
            require(png_size(path) == (64, 64), f"unexpected size: {member}")
            digest = sha256(path)
            require(digest == hashes[map_type], f"hash mismatch: {member}")
            require(digest not in texture_hashes, f"duplicate texture hash: {member}")
            texture_hashes.add(digest)

    require(len(zones) >= 10, "expected at least 10 target zones")
    require(len(families) >= 20, "expected broad surface-family coverage")
    require("SOURCE_CREATED" in manifest["evidence_boundary"], "missing evidence boundary")
    print(f"P1C01_MATERIAL_SOURCE_BATCH01_STATIC_PASS materials={len(records)} png={len(texture_hashes)} zones={len(zones)} families={len(families)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
