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
OUT = ROOT / "SourceAssets" / "Production" / "World" / "Shire" / "Batch03OffRunner"
ARCHIVE = OUT / "P1C01_Batch03_SourceAssets.zip"
MANIFEST = ROOT / "Data" / "P1C01SourceAssetBatch03Manifest.json"


ASSETS = [
    ('SM_B03_PantryJarCluster_A', 'crate', 'M_B03_CeramicCream', 'Bag End Interior', 0.42, 0.24, 0.32),
    ('SM_B03_PantryJarCluster_B', 'crate', 'M_B03_CeramicCream', 'Bag End Interior', 0.36, 0.22, 0.28),
    ('SM_B03_RoundHearthKettle_A', 'barrel', 'M_B03_IronWarm', 'Bag End Interior', 0.48, 0.38, 0.42),
    ('SM_B03_RoundHearthKettle_B', 'barrel', 'M_B03_IronWarm', 'Bag End Interior', 0.38, 0.32, 0.34),
    ('SM_B03_MapTubeStack_A', 'plank', 'M_B03_LeatherBrown', 'Bag End Interior', 0.74, 0.18, 0.18),
    ('SM_B03_MapTubeStack_B', 'plank', 'M_B03_LeatherBrown', 'Bag End Interior', 0.58, 0.16, 0.16),
    ('SM_B03_CoatPegRack_A', 'rack', 'M_B03_WoodHoney', 'Bag End', 0.76, 0.18, 0.52),
    ('SM_B03_CoatPegRack_B', 'rack', 'M_B03_WoodHoney', 'Bag End', 0.62, 0.16, 0.46),
    ('SM_B03_DoorstepMat_A', 'plank', 'M_B03_WovenRush', 'Bag End', 0.9, 0.46, 0.05),
    ('SM_B03_DoorstepMat_B', 'plank', 'M_B03_WovenRush', 'Bag End', 0.72, 0.38, 0.05),
    ('SM_B03_SeedTrayRack_A', 'rack', 'M_B03_LeafSeedling', 'Bag End Garden', 0.86, 0.34, 0.42),
    ('SM_B03_SeedTrayRack_B', 'rack', 'M_B03_LeafSeedling', 'Bag End Garden', 0.68, 0.3, 0.34),
    ('SM_B03_GardenStool_A', 'table', 'M_B03_WoodHoney', 'Bag End Garden', 0.42, 0.42, 0.44),
    ('SM_B03_GardenStool_B', 'table', 'M_B03_WoodHoney', 'Bag End Garden', 0.34, 0.34, 0.38),
    ('SM_B03_PlateStack_A', 'cap', 'M_B03_CeramicCream', 'Party Field', 0.38, 0.38, 0.18),
    ('SM_B03_PlateStack_B', 'cap', 'M_B03_CeramicCream', 'Party Field', 0.3, 0.3, 0.14),
    ('SM_B03_CupTray_A', 'crate', 'M_B03_PaintedBlue', 'Party Field', 0.58, 0.34, 0.16),
    ('SM_B03_CupTray_B', 'crate', 'M_B03_PaintedBlue', 'Party Field', 0.48, 0.3, 0.14),
    ('SM_B03_RibbonStake_A', 'post', 'M_B03_RibbonRed', 'Party Field', 0.12, 0.12, 1.18),
    ('SM_B03_RibbonStake_B', 'post', 'M_B03_RibbonRed', 'Party Field', 0.1, 0.1, 1.02),
    ('SM_B03_FoodBasket_A', 'crate', 'M_B03_BasketWarm', 'Party Field', 0.54, 0.36, 0.3),
    ('SM_B03_FoodBasket_B', 'crate', 'M_B03_BasketWarm', 'Party Field', 0.44, 0.3, 0.26),
    ('SM_B03_GrainScoop_A', 'plank', 'M_B03_WoodHoney', 'Mill Pond', 0.62, 0.22, 0.12),
    ('SM_B03_GrainScoop_B', 'plank', 'M_B03_WoodHoney', 'Mill Pond', 0.52, 0.18, 0.1),
    ('SM_B03_WaterTrough_A', 'crate', 'M_B03_WetWood', 'Mill Pond', 1.08, 0.36, 0.3),
    ('SM_B03_WaterTrough_B', 'crate', 'M_B03_WetWood', 'Mill Pond', 0.86, 0.32, 0.26),
    ('SM_B03_RopeCoil_A', 'cap', 'M_B03_RopeHemp', 'Bucklebury Ferry', 0.5, 0.5, 0.16),
    ('SM_B03_RopeCoil_B', 'cap', 'M_B03_RopeHemp', 'Bucklebury Ferry', 0.4, 0.4, 0.14),
    ('SM_B03_MooringRingPost_A', 'post', 'M_B03_IronWarm', 'Bucklebury Ferry', 0.16, 0.16, 0.72),
    ('SM_B03_MooringRingPost_B', 'post', 'M_B03_IronWarm', 'Bucklebury Ferry', 0.14, 0.14, 0.62),
    ('SM_B03_LanternHook_A', 'post', 'M_B03_IronWarm', 'Bucklebury Ferry', 0.12, 0.12, 1.24),
    ('SM_B03_LanternHook_B', 'post', 'M_B03_IronWarm', 'Bucklebury Ferry', 0.1, 0.1, 1.08),
    ('SM_B03_DockBumper_A', 'root', 'M_B03_WetWood', 'Bucklebury Ferry', 0.92, 0.18, 0.22),
    ('SM_B03_DockBumper_B', 'root', 'M_B03_WetWood', 'Bucklebury Ferry', 0.72, 0.16, 0.18),
    ('SM_B03_PassengerStool_A', 'table', 'M_B03_WoodHoney', 'Bucklebury Ferry', 0.38, 0.34, 0.36),
    ('SM_B03_PassengerStool_B', 'table', 'M_B03_WoodHoney', 'Bucklebury Ferry', 0.32, 0.3, 0.32),
    ('SM_B03_Waystone_A', 'stone', 'M_B03_StoneLichen', 'Bywater Road', 0.34, 0.26, 0.58),
    ('SM_B03_Waystone_B', 'stone', 'M_B03_StoneLichen', 'Bywater Road', 0.28, 0.22, 0.48),
    ('SM_B03_PuddlePlank_A', 'plank', 'M_B03_WetWood', 'Bywater Road', 1.04, 0.22, 0.06),
    ('SM_B03_PuddlePlank_B', 'plank', 'M_B03_WetWood', 'Bywater Road', 0.82, 0.2, 0.05),
    ('SM_B03_HollowStumpCap_A', 'cap', 'M_B03_BarkDark', 'Wooded Road', 0.56, 0.48, 0.34),
    ('SM_B03_HollowStumpCap_B', 'cap', 'M_B03_BarkDark', 'Wooded Road', 0.44, 0.4, 0.28),
    ('SM_B03_RootStep_A', 'root', 'M_B03_BarkDark', 'Wooded Road', 0.84, 0.24, 0.18),
    ('SM_B03_RootStep_B', 'root', 'M_B03_BarkDark', 'Wooded Road', 0.68, 0.22, 0.16),
    ('SM_B03_TurnipCrate_A', 'crate', 'M_B03_TurnipLeaf', 'East Fields', 0.58, 0.38, 0.3),
    ('SM_B03_TurnipCrate_B', 'crate', 'M_B03_TurnipLeaf', 'East Fields', 0.48, 0.32, 0.26),
    ('SM_B03_HoeBundle_A', 'rack', 'M_B03_WoodHoney', 'East Fields', 0.76, 0.18, 0.5),
    ('SM_B03_HoeBundle_B', 'rack', 'M_B03_WoodHoney', 'East Fields', 0.62, 0.16, 0.44),
]


PALETTES = {
    "M_B03_WoodHoney": ((166, 105, 48), (108, 68, 32)),
    "M_B03_CeramicCream": ((218, 207, 178), (154, 136, 104)),
    "M_B03_IronWarm": ((96, 91, 83), (49, 48, 45)),
    "M_B03_LeatherBrown": ((113, 69, 39), (64, 39, 24)),
    "M_B03_WovenRush": ((176, 151, 92), (116, 94, 55)),
    "M_B03_LeafSeedling": ((89, 146, 73), (42, 91, 43)),
    "M_B03_PaintedBlue": ((74, 102, 139), (38, 58, 86)),
    "M_B03_RibbonRed": ((173, 55, 48), (95, 30, 30)),
    "M_B03_BasketWarm": ((171, 121, 62), (102, 69, 37)),
    "M_B03_WetWood": ((92, 72, 55), (48, 41, 36)),
    "M_B03_RopeHemp": ((157, 133, 91), (94, 77, 52)),
    "M_B03_StoneLichen": ((126, 130, 112), (68, 101, 62)),
    "M_B03_BarkDark": ((78, 55, 36), (42, 30, 22)),
    "M_B03_TurnipLeaf": ((131, 142, 82), (67, 103, 47)),
    "M_B03_Parchment": ((205, 181, 133), (145, 112, 72)),
    "M_B03_MossSoft": ((76, 117, 62), (39, 78, 38)),
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
; generator=generate_p1c01_source_asset_batch03.py
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
    build_dir = Path(tempfile.mkdtemp(prefix="p1c01_batch03_assets_"))
    asset_dir = build_dir / "P1C01_Batch03_SourceAssets"
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
                "id": f"P1C01-B03-{index:03d}",
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
