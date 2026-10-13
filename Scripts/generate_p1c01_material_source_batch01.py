#!/usr/bin/env python3
"""Generate original P1C01 PBR texture source maps for off-runner production."""

from __future__ import annotations

import hashlib
import json
import math
import tempfile
import zipfile
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SourceAssets" / "Production" / "Materials" / "Shire" / "Batch01OffRunner"
ARCHIVE = OUT / "P1C01_MaterialBatch01_PBRTextures.zip"
MANIFEST = ROOT / "Data" / "P1C01MaterialSourceBatch01Manifest.json"
SIZE = 64

SURFACES = [
    ("M_P1C01_BagEnd_GreenDoor_PBR", "painted wood", "Bag End", (63, 111, 72), 0.42, 0.64, 0.18),
    ("M_P1C01_BagEnd_RoundBrick_PBR", "warm brick", "Bag End", (151, 92, 63), 0.88, 0.7, 0.04),
    ("M_P1C01_BagEnd_HearthStone_PBR", "hearth stone", "Bag End Interior", (106, 99, 87), 0.95, 0.76, 0.02),
    ("M_P1C01_BagEnd_HoneyWood_PBR", "polished wood", "Bag End Interior", (142, 92, 46), 0.46, 0.52, 0.0),
    ("M_P1C01_Garden_LeafyGround_PBR", "leafy soil", "Bag End Garden", (77, 97, 48), 1.0, 0.86, 0.0),
    ("M_P1C01_Garden_DarkSoil_PBR", "tilled soil", "Bag End Garden", (72, 50, 33), 1.0, 0.92, 0.0),
    ("M_P1C01_Hobbiton_ThatchDry_PBR", "dry thatch", "Hobbiton", (173, 142, 82), 1.0, 0.82, 0.0),
    ("M_P1C01_Hobbiton_Whitewash_PBR", "lime plaster", "Hobbiton", (198, 190, 163), 0.9, 0.74, 0.0),
    ("M_P1C01_Bagshot_RowFence_PBR", "aged fence", "Bagshot Row", (126, 89, 55), 0.72, 0.78, 0.0),
    ("M_P1C01_PartyField_TentCanvas_PBR", "party canvas", "Party Field", (194, 176, 133), 0.98, 0.86, 0.0),
    ("M_P1C01_PartyField_RibbonCloth_PBR", "dyed ribbon cloth", "Party Field", (148, 42, 54), 1.0, 0.84, 0.0),
    ("M_P1C01_PartyField_ServiceCeramic_PBR", "cream ceramic", "Party Field", (211, 196, 163), 0.7, 0.38, 0.0),
    ("M_P1C01_Road_CompactedDirt_PBR", "compacted road dirt", "Hobbiton Road", (117, 82, 48), 1.0, 0.9, 0.0),
    ("M_P1C01_Road_PebbleScatter_PBR", "road pebbles", "Bywater Road", (130, 124, 103), 1.0, 0.78, 0.0),
    ("M_P1C01_WoodedRoad_MossBark_PBR", "mossy bark", "Wooded Road", (83, 74, 46), 1.0, 0.88, 0.0),
    ("M_P1C01_WoodedRoad_RootWet_PBR", "wet roots", "Wooded Road", (71, 48, 34), 0.74, 0.58, 0.0),
    ("M_P1C01_MillPond_WetPlank_PBR", "wet plank", "Mill Pond", (91, 70, 45), 0.56, 0.48, 0.0),
    ("M_P1C01_MillPond_StoneEdge_PBR", "pond edge stone", "Mill Pond", (103, 106, 94), 0.98, 0.73, 0.0),
    ("M_P1C01_Ferry_DockPlank_PBR", "dock plank", "Bucklebury Ferry", (116, 79, 49), 0.67, 0.66, 0.0),
    ("M_P1C01_Ferry_RopeFiber_PBR", "rope fiber", "Bucklebury Ferry", (165, 137, 84), 1.0, 0.91, 0.0),
    ("M_P1C01_EastFields_WheatStalk_PBR", "wheat stalk", "East Fields", (184, 151, 75), 1.0, 0.84, 0.0),
    ("M_P1C01_EastFields_TurnipLeaf_PBR", "turnip leaves", "East Fields", (69, 113, 52), 1.0, 0.79, 0.0),
    ("M_P1C01_Market_AwningBlue_PBR", "market awning cloth", "Hobbiton Market", (64, 93, 137), 1.0, 0.82, 0.0),
    ("M_P1C01_Market_WickerBasket_PBR", "wicker basket", "Hobbiton Market", (167, 120, 64), 0.95, 0.8, 0.0),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return len(data).to_bytes(4, "big") + kind + data + zlib.crc32(kind + data).to_bytes(4, "big")


def write_png(path: Path, pixels: list[tuple[int, int, int, int]]) -> None:
    raw = bytearray()
    for y in range(SIZE):
        raw.append(0)
        row = pixels[y * SIZE:(y + 1) * SIZE]
        for r, g, b, a in row:
            raw.extend((r, g, b, a))
    ihdr = SIZE.to_bytes(4, "big") + SIZE.to_bytes(4, "big") + bytes([8, 6, 0, 0, 0])
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", ihdr) + png_chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + png_chunk(b"IEND", b""))


def clamp(v: float) -> int:
    return max(0, min(255, int(round(v))))


def surface_noise(seed: int, x: int, y: int) -> float:
    v = math.sin((x + 1) * 12.9898 + (y + 3) * 78.233 + seed * 37.719) * 43758.5453
    return v - math.floor(v)


def base_pixels(base: tuple[int, int, int], seed: int, stripe: float) -> list[tuple[int, int, int, int]]:
    pixels = []
    for y in range(SIZE):
        for x in range(SIZE):
            n = surface_noise(seed, x, y) - 0.5
            weave = math.sin((x * stripe) + seed) * 0.06 + math.cos((y * stripe * 0.7) + seed) * 0.04
            pixels.append(tuple(clamp(c * (1.0 + n * 0.18 + weave)) for c in base) + (255,))
    return pixels


def orm_pixels(ao: float, roughness: float, metallic: float, seed: int) -> list[tuple[int, int, int, int]]:
    pixels = []
    for y in range(SIZE):
        for x in range(SIZE):
            n = surface_noise(seed + 31, x, y) - 0.5
            pixels.append((clamp(ao * 255 + n * 10), clamp(roughness * 255 + n * 14), clamp(metallic * 255), 255))
    return pixels


def normal_pixels(seed: int, strength: float) -> list[tuple[int, int, int, int]]:
    pixels = []
    for y in range(SIZE):
        for x in range(SIZE):
            h_l = surface_noise(seed, max(0, x - 1), y)
            h_r = surface_noise(seed, min(SIZE - 1, x + 1), y)
            h_u = surface_noise(seed, x, max(0, y - 1))
            h_d = surface_noise(seed, x, min(SIZE - 1, y + 1))
            nx = (h_l - h_r) * strength
            ny = (h_u - h_d) * strength
            pixels.append((clamp(128 + nx * 90), clamp(128 + ny * 90), 255, 255))
    return pixels


def main() -> int:
    if OUT.exists():
        for p in OUT.rglob("*"):
            if p.is_file():
                p.unlink()
    OUT.mkdir(parents=True, exist_ok=True)
    temp_root = Path(tempfile.mkdtemp(prefix="p1c01_material_batch01_"))
    records = []

    for idx, (name, family, zone, color, ao, roughness, metallic) in enumerate(SURFACES, start=1):
        material_dir = temp_root / name
        material_dir.mkdir(parents=True)
        seed = idx * 97
        members = {}
        maps = {
            "base_color": (f"{name}_BaseColor.png", base_pixels(color, seed, 0.31 + idx * 0.01)),
            "orm_packed": (f"{name}_ORM.png", orm_pixels(ao, roughness, metallic, seed)),
            "normal": (f"{name}_Normal.png", normal_pixels(seed, 1.4 + (idx % 5) * 0.18)),
        }
        hashes = {}
        for map_type, (filename, pixels) in maps.items():
            path = material_dir / filename
            write_png(path, pixels)
            rel = f"{name}/{filename}"
            members[map_type] = rel
            hashes[map_type] = sha256(path)
        records.append({
            "material_name": name,
            "surface_family": family,
            "target_zone": zone,
            "texture_set_members": members,
            "texture_sha256": hashes,
            "pbr_contract": {
                "base_color": "RGBA PNG albedo/color only",
                "orm_packed": "R=ambient occlusion, G=roughness, B=metallic, A=255",
                "normal": "RGBA tangent-space normal candidate, blue-up"
            },
            "source_license": "Project-owned procedural generation; CC0-compatible for project use",
            "warehouse_status": "PENDING",
            "unreal_import_status": "PENDING",
            "material_instance_status": "PENDING",
            "world_binding_status": "PENDING"
        })

    with zipfile.ZipFile(ARCHIVE, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(temp_root.rglob("*.png")):
            zf.write(path, path.relative_to(temp_root).as_posix())

    manifest = {
        "schema_version": 1,
        "batch_id": "P1C01_MATERIAL_SOURCE_BATCH01_OFFRUNNER",
        "created_utc": "2026-10-13T09:15:00Z",
        "runner_policy": "Windows Runner not used or required for this batch",
        "archive": ARCHIVE.relative_to(ROOT).as_posix(),
        "archive_sha256": sha256(ARCHIVE),
        "counts": {
            "material_sets": len(records),
            "generated_png": len(records) * 3,
            "base_color": len(records),
            "orm_packed": len(records),
            "normal": len(records)
        },
        "records": records,
        "evidence_boundary": "SOURCE_CREATED and SOURCE_QC_PASSED only after hosted validator passes; no Warehouse persistence, Unreal import, MaterialInstance creation, world placement, PIE, device, visual acceptance, FPS or Gate 6/7 claim."
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"P1C01_MATERIAL_SOURCE_BATCH01_GENERATED materials={len(records)} png={len(records)*3} archive={ARCHIVE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
