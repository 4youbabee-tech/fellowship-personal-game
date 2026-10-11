#!/usr/bin/env python3
"""Generate reproducible, original 1K support PBR surfaces for 28 canon-grounded regions.

Source PREPRODUCTION only. This program does not create Unreal materials or claim
visual acceptance, provenance for third-party files, or imported assets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
REGION_PLAN = ROOT / "Data" / "WholeGameRegionProductionPacketsV1.json"

# Original procedural support palette, not a likeness of any supplied artwork.
# Roughness is a linear scalar; metallic = 0 for all organic/stone surfaces.
SURFACES = {
    "shire_meadow": ((87, 120, 65), 0.91, "grass"),
    "shire_earth": ((103, 77, 51), 0.92, "earth"),
    "bagend_plaster": ((198, 173, 133), 0.86, "plaster"),
    "oak_timber": ((116, 78, 48), 0.77, "wood"),
    "mossy_stone": ((107, 112, 86), 0.90, "stone"),
    "weathered_granite": ((119, 118, 119), 0.87, "stone"),
    "frosted_rock": ((175, 185, 190), 0.85, "stone"),
    "ancient_bark": ((82, 71, 57), 0.88, "wood"),
    "golden_leaf_floor": ((150, 121, 65), 0.94, "grass"),
    "wetland_peat": ((69, 70, 55), 0.97, "earth"),
    "white_limestone": ((190, 186, 167), 0.85, "stone"),
    "charred_basalt": ((67, 65, 67), 0.93, "stone"),
}

# These keys must match the 28 production packets exactly. These are REGIONS,
# not 28 towns. A different cloud-intake index includes Erebor/Mirkwood/Lake
# Town; this production binding intentionally uses the existing world packets.
REGION_FAMILIES = {
    "SHIRE_HOBBITON": ["shire_meadow", "shire_earth", "mossy_stone", "oak_timber"],
    "BAG_END": ["bagend_plaster", "oak_timber", "shire_earth"],
    "BREE": ["oak_timber", "mossy_stone", "shire_earth"],
    "WEATHERTOP": ["weathered_granite", "mossy_stone"],
    "RIVENDELL": ["mossy_stone", "white_limestone", "ancient_bark"],
    "CARADHRAS": ["frosted_rock", "weathered_granite"],
    "MORIA": ["weathered_granite", "charred_basalt"],
    "LOTHLORIEN": ["golden_leaf_floor", "ancient_bark", "mossy_stone"],
    "ANDUIN_AMON_HEN": ["mossy_stone", "weathered_granite", "ancient_bark"],
    "FANGORN": ["ancient_bark", "wetland_peat", "mossy_stone"],
    "EDORAS_MEDUSELD": ["oak_timber", "shire_meadow", "shire_earth"],
    "HELMS_DEEP": ["weathered_granite", "mossy_stone"],
    "ISENGARD_ORTHANC": ["charred_basalt", "weathered_granite", "wetland_peat"],
    "EMYN_MUIL": ["weathered_granite", "mossy_stone"],
    "DEAD_MARSHES": ["wetland_peat", "mossy_stone"],
    "ITHILIEN": ["shire_meadow", "mossy_stone", "ancient_bark"],
    "HENNETH_ANNUN": ["mossy_stone", "weathered_granite"],
    "MINAS_TIRITH": ["white_limestone", "weathered_granite"],
    "OSGILIATH": ["white_limestone", "weathered_granite", "mossy_stone"],
    "MINAS_MORGUL": ["weathered_granite", "charred_basalt"],
    "CIRITH_UNGOL": ["charred_basalt", "weathered_granite"],
    "SHELOBS_LAIR": ["charred_basalt", "wetland_peat"],
    "PELENNOR_FIELDS": ["shire_earth", "shire_meadow", "weathered_granite"],
    "PATHS_OF_THE_DEAD": ["weathered_granite", "charred_basalt"],
    "BLACK_GATE_MORANNON": ["charred_basalt", "weathered_granite"],
    "MORDOR_GORGOROTH": ["charred_basalt", "shire_earth"],
    "MOUNT_DOOM": ["charred_basalt", "weathered_granite"],
    "GREY_HAVENS": ["white_limestone", "oak_timber", "mossy_stone"],
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_canon_map() -> list[str]:
    packet = json.loads(REGION_PLAN.read_text(encoding="utf-8"))
    names = [p["region_id"] for p in packet["packets"]]
    if len(names) != 28 or len(set(names)) != 28 or set(names) != set(REGION_FAMILIES):
        raise ValueError("28_REGION_PACKET_ID_MISMATCH; no unreviewed regions may be inserted")
    if set(x for families in REGION_FAMILIES.values() for x in families) != set(SURFACES):
        raise ValueError("MATERIAL_FAMILY_MISMATCH")
    return names


def height_field(size: int, name: str, kind: str) -> np.ndarray:
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    xx *= (2 * math.pi / size)
    yy *= (2 * math.pi / size)
    digest = hashlib.sha256(name.encode("ascii")).digest()
    phases = [v / 255 * 2 * math.pi for v in digest[:12]]
    h = np.full((size, size), 0.48, dtype=np.float32)
    for i, (kx, ky) in enumerate(((1, 2), (3, 2), (7, 5), (13, 11), (23, 17))):
        h += (0.115 / (1 + i * 0.72)) * np.sin(kx * xx + phases[i]) * np.cos(ky * yy + phases[i + 5])
    if kind == "wood":
        h += 0.070 * np.sin(24 * xx + 2.4 * np.sin(2 * yy + phases[10]))
    elif kind == "grass":
        h += 0.052 * np.sin(29 * xx + phases[10]) * np.sin(31 * yy + phases[11])
    elif kind == "stone":
        h += 0.055 * np.sin(17 * xx + phases[10]) * np.cos(19 * yy + phases[11])
    elif kind == "earth":
        h += 0.045 * np.cos(33 * xx + phases[10]) * np.sin(27 * yy + phases[11])
    return np.clip(h, 0.08, 0.93)


def make_set(folder: Path, name: str, size: int) -> list[dict]:
    rgb, roughness, kind = SURFACES[name]
    h = height_field(size, name, kind)
    color = np.empty((size, size, 3), dtype=np.uint8)
    deviation = (h - 0.48) * (55 if kind != "plaster" else 26)
    for channel, base in enumerate(rgb):
        color[..., channel] = np.clip(base + deviation * (1 if channel != 1 else 0.8), 0, 255).astype(np.uint8)

    # Tile-wrapped derivative. DirectX green Y handedness is intentional.
    dx = (np.roll(h, -1, axis=1) - np.roll(h, 1, axis=1)) * 4.0
    dy = (np.roll(h, -1, axis=0) - np.roll(h, 1, axis=0)) * 4.0
    scale = 1.0 / np.sqrt(1.0 + dx * dx + dy * dy)
    normal = np.stack(((-dx * scale * 0.5 + 0.5) * 255,
                       (dy * scale * 0.5 + 0.5) * 255,
                       (scale * 0.5 + 0.5) * 255), axis=2)
    normal = np.clip(normal, 0, 255).astype(np.uint8)

    orm = np.empty((size, size, 3), dtype=np.uint8)
    orm[..., 0] = np.clip((0.85 + 0.15 * h) * 255, 0, 255).astype(np.uint8)  # Ambient occlusion
    orm[..., 1] = np.clip((roughness + (0.48 - h) * 0.08) * 255, 0, 255).astype(np.uint8)
    orm[..., 2] = 0  # Nonmetal

    folder.mkdir(parents=True, exist_ok=True)
    entries = []
    for suffix, data, colorspace in (("BaseColor", color, "sRGB"),
                                      ("NormalDX", normal, "linear"),
                                      ("ORM", orm, "linear")):
        filename = folder / f"TX_{name}_{suffix}.png"
        Image.fromarray(data, "RGB").save(filename, optimize=True)
        entries.append({
            "family": name, "type": suffix, "file": filename.name,
            "sha256": sha256(filename), "bytes": filename.stat().st_size,
            "dimensions": [size, size], "color_space": colorspace,
        })
    return entries


def generate(out: Path, size: int = 1024) -> dict:
    if size not in (128, 256, 512, 1024, 2048):
        raise ValueError("POT_SIZE_NOT_ALLOWED")
    region_ids = validate_canon_map()
    out.mkdir(parents=True, exist_ok=True)
    textures = []
    for name in sorted(SURFACES):
        textures += make_set(out / "materials" / name, name, size)
    for entry in textures:
        entry["path"] = f"materials/{entry['family']}/{entry['file']}"
        del entry["file"]
    bindings = [{"id": region_id, "support_surfaces": REGION_FAMILIES[region_id],
                 "ue_imported": False} for region_id in region_ids]
    manifest = {
        "schema_version": 1, "id": "SHIRE_JOURNEY_28_REGION_ORIGINAL_SUPPORT_PBR_V1",
        "state": "PHYSICAL_SOURCE_GENERATED_NOT_UNREAL_IMPORTED",
        "provenance": "ORIGINAL_DETERMINISTIC_PROCEDURAL", "license": "ORIGINAL_PROJECT_ASSET",
        "authority": "Data/ProjectGovernor.json",
        "region_packet_sha256": sha256(REGION_PLAN),
        "generator_sha256": sha256(Path(__file__)),
        "format": "PNG", "size_px": size,
        "material_families": len(SURFACES), "physical_textures": len(textures),
        "region_bindings": bindings, "textures": textures,
        "channel_packing": "ORM: R=AO G=Roughness B=Metallic",
        "normal_space": "DirectX", "normal_and_orm_srgb": False,
        "runtime_imported": False, "target_runtime_profile": "UE4.27.2 DX11 720p 2GB VRAM",
        "quality_boundary": "Procedural support PBR only; no hero textures, visual review or UE runtime proof."
    }
    (out / "materials_receipt.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"PBR_SOURCE_GENERATED families={len(SURFACES)} textures={len(textures)} regions={len(bindings)} size={size}")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--size", type=int, default=1024)
    a = parser.parse_args()
    generate(a.out, a.size)
