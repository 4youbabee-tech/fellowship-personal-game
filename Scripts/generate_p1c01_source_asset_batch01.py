#!/usr/bin/env python3
"""Generate original P1C01 source FBX/PNG assets for off-runner production."""

from __future__ import annotations

import hashlib
import json
import math
import shutil
import struct
import tempfile
import zipfile
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SourceAssets" / "Production" / "World" / "Shire" / "Batch01OffRunner"
ARCHIVE = OUT / "P1C01_Batch01_SourceAssets.zip"
MANIFEST = ROOT / "Data" / "P1C01SourceAssetBatch01Manifest.json"


ASSETS = [
    ("SM_B01_BagEndGardenBench_A", "bench", "M_B01_WoodWarm", "Bag End", 1.05, 0.42, 0.48),
    ("SM_B01_BagEndGardenBench_B", "bench", "M_B01_WoodWarm", "Bag End", 1.22, 0.44, 0.50),
    ("SM_B01_BagEndRoundStep_A", "step", "M_B01_StoneMoss", "Bag End", 1.15, 0.32, 0.22),
    ("SM_B01_BagEndRoundStep_B", "step", "M_B01_StoneMoss", "Bag End", 1.42, 0.34, 0.24),
    ("SM_B01_HobbitonFenceCurve_A", "fence", "M_B01_WoodPale", "Hobbiton", 1.60, 0.15, 0.65),
    ("SM_B01_HobbitonFenceCurve_B", "fence", "M_B01_WoodPale", "Hobbiton", 1.35, 0.15, 0.58),
    ("SM_B01_BagshotGardenCrate_A", "crate", "M_B01_WoodDark", "Bagshot Row", 0.46, 0.38, 0.32),
    ("SM_B01_BagshotGardenCrate_B", "crate", "M_B01_WoodDark", "Bagshot Row", 0.52, 0.41, 0.36),
    ("SM_B01_PartyFieldLanternPost_A", "post", "M_B01_WoodPale", "Party Field", 0.16, 0.16, 1.45),
    ("SM_B01_PartyFieldLanternPost_B", "post", "M_B01_WoodPale", "Party Field", 0.18, 0.18, 1.32),
    ("SM_B01_PartyFieldTable_A", "table", "M_B01_WoodWarm", "Party Field", 1.25, 0.62, 0.56),
    ("SM_B01_PartyFieldTable_B", "table", "M_B01_WoodWarm", "Party Field", 1.05, 0.55, 0.52),
    ("SM_B01_FieldBasket_A", "basket", "M_B01_Wicker", "East Fields", 0.42, 0.42, 0.36),
    ("SM_B01_FieldBasket_B", "basket", "M_B01_Wicker", "East Fields", 0.36, 0.36, 0.30),
    ("SM_B01_FieldHayBundle_A", "bundle", "M_B01_HayGold", "East Fields", 0.78, 0.42, 0.34),
    ("SM_B01_FieldHayBundle_B", "bundle", "M_B01_HayGold", "East Fields", 0.66, 0.36, 0.30),
    ("SM_B01_WoodedRoadRootClump_A", "root", "M_B01_BarkDark", "Wooded Road", 0.92, 0.42, 0.25),
    ("SM_B01_WoodedRoadRootClump_B", "root", "M_B01_BarkDark", "Wooded Road", 0.70, 0.38, 0.22),
    ("SM_B01_WoodedRoadStoneMarker_A", "stone", "M_B01_StoneMoss", "Wooded Road", 0.32, 0.22, 0.72),
    ("SM_B01_WoodedRoadStoneMarker_B", "stone", "M_B01_StoneMoss", "Wooded Road", 0.26, 0.20, 0.58),
    ("SM_B01_FerryLandingRopePost_A", "post", "M_B01_RopeWeathered", "Bucklebury Ferry", 0.20, 0.20, 0.92),
    ("SM_B01_FerryLandingRopePost_B", "post", "M_B01_RopeWeathered", "Bucklebury Ferry", 0.18, 0.18, 0.78),
    ("SM_B01_FerryLandingDockCrate_A", "crate", "M_B01_WoodDark", "Bucklebury Ferry", 0.62, 0.48, 0.44),
    ("SM_B01_FerryLandingDockCrate_B", "crate", "M_B01_WoodDark", "Bucklebury Ferry", 0.50, 0.40, 0.38),
    ("SM_B01_FerryBankReedPatch_A", "reed", "M_B01_ReedGreen", "Bucklebury Ferry", 0.72, 0.42, 0.90),
    ("SM_B01_FerryBankReedPatch_B", "reed", "M_B01_ReedGreen", "Bucklebury Ferry", 0.58, 0.35, 0.72),
    ("SM_B01_RoadSideFlowerTub_A", "planter", "M_B01_WoodPale", "Hobbiton Road", 0.68, 0.30, 0.28),
    ("SM_B01_RoadSideFlowerTub_B", "planter", "M_B01_WoodPale", "Hobbiton Road", 0.56, 0.28, 0.25),
    ("SM_B01_RoadRuttedPlank_A", "plank", "M_B01_WoodDark", "Hobbiton Road", 1.10, 0.18, 0.08),
    ("SM_B01_RoadRuttedPlank_B", "plank", "M_B01_WoodDark", "Hobbiton Road", 0.90, 0.16, 0.07),
    ("SM_B01_MillPondBucket_A", "bucket", "M_B01_WoodWarm", "Mill Pond", 0.32, 0.32, 0.42),
    ("SM_B01_MillPondBucket_B", "bucket", "M_B01_WoodWarm", "Mill Pond", 0.28, 0.28, 0.36),
    ("SM_B01_VillageMarketShelf_A", "shelf", "M_B01_WoodPale", "Hobbiton Market", 0.92, 0.36, 0.72),
    ("SM_B01_VillageMarketShelf_B", "shelf", "M_B01_WoodPale", "Hobbiton Market", 0.78, 0.34, 0.64),
    ("SM_B01_PartyFieldBuntingPole_A", "post", "M_B01_WoodPale", "Party Field", 0.12, 0.12, 1.60),
    ("SM_B01_PartyFieldBuntingPole_B", "post", "M_B01_WoodPale", "Party Field", 0.12, 0.12, 1.42),
]


PALETTES = {
    "M_B01_WoodWarm": ((145, 92, 46), (106, 64, 32)),
    "M_B01_WoodPale": ((172, 124, 70), (126, 82, 42)),
    "M_B01_WoodDark": ((91, 55, 32), (59, 35, 21)),
    "M_B01_StoneMoss": ((126, 130, 112), (69, 104, 55)),
    "M_B01_Wicker": ((178, 140, 78), (120, 82, 41)),
    "M_B01_HayGold": ((202, 169, 67), (145, 105, 40)),
    "M_B01_BarkDark": ((83, 59, 39), (49, 35, 24)),
    "M_B01_RopeWeathered": ((156, 133, 91), (100, 82, 55)),
    "M_B01_ReedGreen": ((99, 132, 67), (58, 90, 48)),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write_png(path: Path, colors: tuple[tuple[int, int, int], tuple[int, int, int]], seed: int) -> None:
    width = height = 64
    rows = []
    a, b = colors
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            t = ((x * 7 + y * 13 + seed * 17) % 64) / 63.0
            stripe = 0.15 if ((x + seed) // 8) % 2 else -0.05
            r = int(max(0, min(255, a[0] * (1 - t) + b[0] * t + stripe * 255)))
            g = int(max(0, min(255, a[1] * (1 - t) + b[1] * t + stripe * 180)))
            bl = int(max(0, min(255, a[2] * (1 - t) + b[2] * t + stripe * 120)))
            row.extend((r, g, bl, 255))
        rows.append(bytes(row))
    raw = b"".join(rows)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def box_mesh(width: float, depth: float, height: float, kind: str) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int, int]]]:
    w = width * 50.0
    d = depth * 50.0
    h = height * 100.0
    z0 = 0.0
    z1 = h
    if kind in {"step", "plank"}:
        h *= 0.55
        z1 = h
    verts = [
        (-w, -d, z0), (w, -d, z0), (w, d, z0), (-w, d, z0),
        (-w, -d, z1), (w, -d, z1), (w, d, z1), (-w, d, z1),
    ]
    faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    if kind in {"post", "reed"}:
        radius = max(width, depth) * 35.0
        verts = []
        for z in (0.0, z1):
            for i in range(8):
                a = math.tau * i / 8.0
                lean = (i % 3 - 1) * (4.0 if kind == "reed" else 1.0)
                verts.append((math.cos(a) * radius + lean, math.sin(a) * radius, z))
        faces = []
        for i in range(8):
            faces.append((i, (i + 1) % 8, (i + 1) % 8 + 8, i + 8))
    return verts, faces


def write_fbx(path: Path, name: str, kind: str, material: str, width: float, depth: float, height: float) -> dict[str, int]:
    verts, faces = box_mesh(width, depth, height, kind)
    vertices = ",".join(f"{x:.3f},{y:.3f},{z:.3f}" for x, y, z in verts)
    poly = []
    for face in faces:
        poly.extend([face[0], face[1], face[2], -face[3] - 1])
    polygons = ",".join(str(i) for i in poly)
    uvs = ",".join("0,0,1,0,1,1,0,1" for _ in faces)
    normals = ",".join("0,0,1" for _ in verts)
    path.write_text(
        f"""; FBX 7.4.0 project-owned generated source asset
; generator=generate_p1c01_source_asset_batch01.py
; license=CC0-project-owned-procedural
; unreal_units=centimeters
FBXHeaderExtension:  {{
  FBXHeaderVersion: 1003
  FBXVersion: 7400
}}
Objects:  {{
  Geometry: 1, "Geometry::{name}", "Mesh" {{
    Vertices: *{len(verts) * 3} {{ a: {vertices} }}
    PolygonVertexIndex: *{len(poly)} {{ a: {polygons} }}
    LayerElementNormal: 0 {{ Normals: *{len(verts) * 3} {{ a: {normals} }} }}
    LayerElementUV: 0 {{
      Name: "UVChannel_1"
      MappingInformationType: "ByPolygonVertex"
      ReferenceInformationType: "Direct"
      UV: *{len(faces) * 8} {{ a: {uvs} }}
    }}
    LayerElementMaterial: 0 {{
      MappingInformationType: "AllSame"
      ReferenceInformationType: "IndexToDirect"
      Materials: *1 {{ a: 0 }}
    }}
  }}
  Material: 2, "Material::{material}", "" {{
    ShadingModel: "phong"
  }}
  Model: 3, "Model::{name}", "Mesh" {{
    Version: 232
    Properties70:  {{
      P: "Lcl Translation", "Lcl Translation", "", "A",0,0,0
    }}
  }}
  Model: 4, "Model::UCX_{name}_00", "Mesh" {{
    Version: 232
  }}
}}
Connections:  {{
  C: "OO",1,3
  C: "OO",2,3
}}
""",
        encoding="utf-8",
    )
    return {"vertices": len(verts), "polygons": len(faces)}


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)
    build_dir = Path(tempfile.mkdtemp(prefix="p1c01_batch01_assets_"))
    asset_dir = build_dir / "P1C01_Batch01_SourceAssets"
    texture_dir = asset_dir / "Textures"
    texture_dir.mkdir(parents=True, exist_ok=True)
    records = []
    texture_paths = {}
    for index, material in enumerate(sorted(PALETTES)):
        texture_path = texture_dir / f"T_{material[2:]}_BaseColor.png"
        write_png(texture_path, PALETTES[material], index + 11)
        texture_paths[material] = texture_path

    for index, (name, kind, material, zone, width, depth, height) in enumerate(ASSETS, 1):
        fbx_path = asset_dir / f"{name}.fbx"
        mesh_stats = write_fbx(fbx_path, name, kind, material, width, depth, height)
        tex_path = texture_paths[material]
        records.append(
            {
                "id": f"P1C01-B01-{index:03d}",
                "asset_name": name,
                "asset_type": "static_mesh_fbx",
                "category": kind,
                "target_zone": zone,
                "source_license": "CC0-project-owned-procedural",
                "status": "SOURCE_GENERATED_STATIC_VALIDATION_PENDING",
                "fbx_archive_member": str(fbx_path.relative_to(asset_dir)).replace("\\", "/"),
                "fbx_sha256": sha256(fbx_path),
                "base_color_archive_member": str(tex_path.relative_to(asset_dir)).replace("\\", "/"),
                "base_color_sha256": sha256(tex_path),
                "material_slot": material,
                "lod_policy": "LOD0 source now; UE LOD generation/import pending",
                "collision_policy": "Simple UCX placeholder metadata present; UE collision import pending",
                "vertices": mesh_stats["vertices"],
                "polygons": mesh_stats["polygons"],
                "unreal_import_status": "PENDING",
                "world_population_status": "PENDING",
            }
        )

    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(asset_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(asset_dir).as_posix())

    manifest = {
        "schema_version": 1,
        "batch_id": "P1C01_SOURCE_ASSET_BATCH01_OFFRUNNER",
        "authority": "Data/ProjectGovernor.json",
        "production_scope": "P1C01 source asset generation outside Windows Runner",
        "runner_policy": "Windows Runner not used or required for this batch",
        "archive": str(ARCHIVE.relative_to(ROOT)).replace("\\", "/"),
        "archive_sha256": sha256(ARCHIVE),
        "counts": {
            "generated_fbx": len(records),
            "generated_png": len(texture_paths),
            "unique_mesh_assets": len(records),
            "unique_material_textures": len(texture_paths),
        },
        "records": records,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(build_dir)
    print(
        "P1C01_SOURCE_ASSET_BATCH01_GENERATED "
        f"fbx={len(records)} png={len(texture_paths)} archive={ARCHIVE.relative_to(ROOT)} manifest={MANIFEST.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
