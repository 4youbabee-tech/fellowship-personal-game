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
OUT = ROOT / "SourceAssets" / "Production" / "World" / "Shire" / "Batch02OffRunner"
ARCHIVE = OUT / "P1C01_Batch02_SourceAssets.zip"
MANIFEST = ROOT / "Data" / "P1C01SourceAssetBatch02Manifest.json"


ASSETS = [
    ('SM_B02_BagEndWindowHerbBox_A', 'planter', 'M_B02_LeafHerb', 'Bag End', 0.74, 0.22, 0.26),
    ('SM_B02_BagEndWindowHerbBox_B', 'planter', 'M_B02_LeafHerb', 'Bag End', 0.58, 0.2, 0.24),
    ('SM_B02_BagEndRoundDoorTrim_A', 'arch', 'M_B02_DoorGreen', 'Bag End', 1.05, 0.18, 1.15),
    ('SM_B02_BagEndRoundDoorTrim_B', 'arch', 'M_B02_DoorGreen', 'Bag End', 0.92, 0.16, 1.04),
    ('SM_B02_GardenToolRack_A', 'rack', 'M_B02_WoodWarm', 'Bag End Garden', 0.84, 0.2, 0.78),
    ('SM_B02_GardenToolRack_B', 'rack', 'M_B02_WoodWarm', 'Bag End Garden', 0.68, 0.18, 0.66),
    ('SM_B02_BagshotLaundryLine_A', 'line', 'M_B02_LinenCream', 'Bagshot Row', 1.42, 0.08, 0.95),
    ('SM_B02_BagshotLaundryLine_B', 'line', 'M_B02_LinenCream', 'Bagshot Row', 1.2, 0.08, 0.86),
    ('SM_B02_BagshotSmokeCap_A', 'cap', 'M_B02_StoneMoss', 'Bagshot Row', 0.36, 0.3, 0.42),
    ('SM_B02_BagshotSmokeCap_B', 'cap', 'M_B02_StoneMoss', 'Bagshot Row', 0.3, 0.26, 0.36),
    ('SM_B02_HobbitonGateHalf_A', 'gate', 'M_B02_WoodPale', 'Hobbiton', 0.82, 0.14, 0.72),
    ('SM_B02_HobbitonGateHalf_B', 'gate', 'M_B02_WoodPale', 'Hobbiton', 0.74, 0.14, 0.66),
    ('SM_B02_PartyFieldServingBar_A', 'table', 'M_B02_WoodWarm', 'Party Field', 1.55, 0.52, 0.7),
    ('SM_B02_PartyFieldServingBar_B', 'table', 'M_B02_WoodWarm', 'Party Field', 1.32, 0.48, 0.64),
    ('SM_B02_PartyFieldKegStand_A', 'barrel', 'M_B02_WoodDark', 'Party Field', 0.46, 0.46, 0.72),
    ('SM_B02_PartyFieldKegStand_B', 'barrel', 'M_B02_WoodDark', 'Party Field', 0.38, 0.38, 0.6),
    ('SM_B02_PartyFieldFireworkCrate_A', 'crate', 'M_B02_PaintedRed', 'Party Field', 0.58, 0.42, 0.44),
    ('SM_B02_PartyFieldFireworkCrate_B', 'crate', 'M_B02_PaintedRed', 'Party Field', 0.48, 0.36, 0.38),
    ('SM_B02_MillBridgeRail_A', 'rail', 'M_B02_WoodPale', 'Mill Bridge', 1.7, 0.12, 0.66),
    ('SM_B02_MillBridgeRail_B', 'rail', 'M_B02_WoodPale', 'Mill Bridge', 1.42, 0.1, 0.58),
    ('SM_B02_MillWheelSpokeSet_A', 'wheel', 'M_B02_WoodDark', 'Mill Pond', 0.86, 0.18, 0.86),
    ('SM_B02_MillWheelSpokeSet_B', 'wheel', 'M_B02_WoodDark', 'Mill Pond', 0.7, 0.16, 0.7),
    ('SM_B02_MillFlourSack_A', 'sack', 'M_B02_CanvasTan', 'Mill Pond', 0.42, 0.3, 0.52),
    ('SM_B02_MillFlourSack_B', 'sack', 'M_B02_CanvasTan', 'Mill Pond', 0.36, 0.26, 0.44),
    ('SM_B02_BywaterSignPost_A', 'post', 'M_B02_WoodPale', 'Bywater Road', 0.18, 0.18, 1.35),
    ('SM_B02_BywaterSignPost_B', 'post', 'M_B02_WoodPale', 'Bywater Road', 0.16, 0.16, 1.18),
    ('SM_B02_RoadPebbleCluster_A', 'stone', 'M_B02_StoneMoss', 'Hobbiton Road', 0.56, 0.36, 0.16),
    ('SM_B02_RoadPebbleCluster_B', 'stone', 'M_B02_StoneMoss', 'Hobbiton Road', 0.44, 0.3, 0.14),
    ('SM_B02_RoadMuddyRut_A', 'plank', 'M_B02_MudBrown', 'Hobbiton Road', 1.25, 0.24, 0.06),
    ('SM_B02_RoadMuddyRut_B', 'plank', 'M_B02_MudBrown', 'Hobbiton Road', 0.95, 0.22, 0.05),
    ('SM_B02_WoodedRoadFernPatch_A', 'reed', 'M_B02_FernGreen', 'Wooded Road', 0.68, 0.44, 0.56),
    ('SM_B02_WoodedRoadFernPatch_B', 'reed', 'M_B02_FernGreen', 'Wooded Road', 0.52, 0.36, 0.48),
    ('SM_B02_WoodedRoadFallenBranch_A', 'root', 'M_B02_BarkDark', 'Wooded Road', 1.2, 0.2, 0.22),
    ('SM_B02_WoodedRoadFallenBranch_B', 'root', 'M_B02_BarkDark', 'Wooded Road', 0.96, 0.18, 0.2),
    ('SM_B02_WoodedRoadMushroomRing_A', 'cap', 'M_B02_Mushroom', 'Wooded Road', 0.42, 0.42, 0.22),
    ('SM_B02_WoodedRoadMushroomRing_B', 'cap', 'M_B02_Mushroom', 'Wooded Road', 0.34, 0.34, 0.18),
    ('SM_B02_FerryDockCleat_A', 'cleat', 'M_B02_RopeWeathered', 'Bucklebury Ferry', 0.42, 0.18, 0.18),
    ('SM_B02_FerryDockCleat_B', 'cleat', 'M_B02_RopeWeathered', 'Bucklebury Ferry', 0.34, 0.16, 0.16),
    ('SM_B02_FerryOarRack_A', 'rack', 'M_B02_WoodWarm', 'Bucklebury Ferry', 0.88, 0.22, 0.58),
    ('SM_B02_FerryOarRack_B', 'rack', 'M_B02_WoodWarm', 'Bucklebury Ferry', 0.76, 0.2, 0.52),
    ('SM_B02_FerryWetPlank_A', 'plank', 'M_B02_WetWood', 'Bucklebury Ferry', 1.18, 0.22, 0.07),
    ('SM_B02_FerryWetPlank_B', 'plank', 'M_B02_WetWood', 'Bucklebury Ferry', 0.96, 0.2, 0.06),
    ('SM_B02_FieldScarecrowPole_A', 'post', 'M_B02_CanvasTan', 'East Fields', 0.18, 0.18, 1.52),
    ('SM_B02_FieldScarecrowPole_B', 'post', 'M_B02_CanvasTan', 'East Fields', 0.16, 0.16, 1.34),
    ('SM_B02_FieldPumpkinCrate_A', 'crate', 'M_B02_Pumpkin', 'East Fields', 0.62, 0.42, 0.32),
    ('SM_B02_FieldPumpkinCrate_B', 'crate', 'M_B02_Pumpkin', 'East Fields', 0.52, 0.36, 0.28),
    ('SM_B02_MarketAwningPole_A', 'post', 'M_B02_PaintedRed', 'Hobbiton Market', 0.14, 0.14, 1.48),
    ('SM_B02_MarketAwningPole_B', 'post', 'M_B02_PaintedRed', 'Hobbiton Market', 0.12, 0.12, 1.32),
]


PALETTES = {
    "M_B02_WoodWarm": ((148, 93, 44), (103, 64, 31)),
    "M_B02_WoodPale": ((180, 130, 75), (130, 88, 44)),
    "M_B02_WoodDark": ((86, 50, 28), (54, 32, 19)),
    "M_B02_StoneMoss": ((121, 126, 108), (66, 101, 56)),
    "M_B02_RopeWeathered": ((154, 131, 90), (96, 79, 53)),
    "M_B02_LeafHerb": ((94, 138, 72), (43, 86, 42)),
    "M_B02_DoorGreen": ((42, 103, 73), (26, 63, 48)),
    "M_B02_LinenCream": ((212, 199, 162), (154, 137, 105)),
    "M_B02_PaintedRed": ((154, 57, 44), (93, 32, 27)),
    "M_B02_CanvasTan": ((176, 145, 92), (119, 89, 55)),
    "M_B02_MudBrown": ((92, 63, 39), (55, 39, 28)),
    "M_B02_FernGreen": ((78, 131, 61), (40, 82, 39)),
    "M_B02_BarkDark": ((80, 57, 38), (45, 32, 23)),
    "M_B02_Mushroom": ((181, 150, 121), (111, 75, 61)),
    "M_B02_WetWood": ((95, 73, 54), (50, 43, 37)),
    "M_B02_Pumpkin": ((191, 105, 42), (110, 62, 25)),
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
; generator=generate_p1c01_source_asset_batch02.py
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
    build_dir = Path(tempfile.mkdtemp(prefix="p1c01_batch02_assets_"))
    asset_dir = build_dir / "P1C01_Batch02_SourceAssets"
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
                "id": f"P1C01-B02-{index:03d}",
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
        "batch_id": "P1C01_SOURCE_ASSET_BATCH02_OFFRUNNER",
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
        "P1C01_SOURCE_ASSET_BATCH02_GENERATED "
        f"fbx={len(records)} png={len(texture_paths)} archive={ARCHIVE.relative_to(ROOT)} manifest={MANIFEST.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
