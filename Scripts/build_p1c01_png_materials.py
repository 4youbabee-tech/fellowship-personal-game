"""Prepare staged Poly Haven 1K PBR sources as FBX + UE4-friendly PNG.

Source-only: no Unreal import, no geometry edits, no PIE or device acceptance.
Uses original downloaded 1K JPEG/EXR/PNG maps and preserves FBX bytes exactly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
import shutil
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def file_of(directory: Path, name: str) -> Path:
    matches = [
        path for path in directory.glob(name + ".*")
        if path.suffix.lower() in (".png", ".jpg", ".jpeg", ".exr", ".tga")
    ]
    if len(matches) != 1:
        raise ValueError(f"one map expected for {name}, found={len(matches)}")
    return matches[0]


def scalar(path: Path) -> np.ndarray:
    if path.suffix.lower() == ".exr":
        data = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if data is None:
            raise ValueError(f"unsupported EXR: {path}")
        if data.ndim == 3:
            data = data[:, :, 0]
        return np.clip(data.astype(np.float32), 0, 1)
    return np.asarray(Image.open(path).convert("L"), dtype=np.float32) / 255.0


def normal_dx(path: Path) -> Image.Image:
    if path.suffix.lower() == ".exr":
        data = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if data is None or data.ndim != 3 or data.shape[2] < 3:
            raise ValueError(f"invalid EXR normal {path}")
        rgb = data[:, :, :3][:, :, ::-1].astype(np.float32)
    else:
        rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
    if rgb.shape[:2] != (1024, 1024):
        raise ValueError(f"normal not 1024x1024 {path}")
    rgb = np.clip(rgb, 0, 1)
    rgb[:, :, 1] = 1 - rgb[:, :, 1]
    return Image.fromarray(np.round(rgb * 255).astype("uint8"), "RGB")


def required_map(directory: Path, prefix: str, suffix: str) -> Path:
    return file_of(directory, prefix + suffix + "_1k")


def build(source: Path, output: Path) -> dict:
    if not source.is_dir():
        raise ValueError("source staging directory missing")
    folders = sorted(p for p in source.iterdir() if p.is_dir())
    if len(folders) != 5:
        raise ValueError(f"expected five staged assets, got {len(folders)}")
    output.mkdir(parents=True, exist_ok=True)
    results = []
    for folder in folders:
        slug = folder.name
        fbx = folder / (slug + ".fbx")
        tex = folder / "textures"
        if not fbx.is_file() or not tex.is_dir():
            raise ValueError("missing staged FBX or textures " + slug)
        dest = output / slug
        dest.mkdir(exist_ok=True)
        shutil.copy2(fbx, dest / fbx.name)
        maps = []
        prefixes = [(slug + "_", "Main")]
        if slug == "wooden_lantern_01":
            prefixes.append((slug + "_glass_", "Glass"))
        for prefix, material in prefixes:
            src_diff = required_map(tex, prefix, "diff")
            src_nor = required_map(tex, prefix, "nor_gl")
            src_rough = required_map(tex, prefix, "rough")
            try:
                src_metal = required_map(tex, prefix, "metal")
            except ValueError:
                src_metal = None
            color = Image.open(src_diff).convert("RGB")
            if color.size != (1024, 1024):
                raise ValueError("diffuse dimensions differ from 1K " + slug)
            rough = scalar(src_rough)
            if rough.shape != (1024, 1024):
                raise ValueError("roughness dimensions differ from 1K " + slug)
            metal = scalar(src_metal) if src_metal else np.zeros_like(rough)
            if metal.shape != (1024, 1024):
                raise ValueError("metal dimensions differ from 1K " + slug)
            dx = normal_dx(src_nor)
            orm = np.stack(
                [
                    np.full_like(rough, 255, dtype=np.uint8),
                    np.round(rough * 255).astype("uint8"),
                    np.round(metal * 255).astype("uint8"),
                ], axis=-1
            )
            output_images = {
                "BaseColor": color,
                "NormalDX": dx,
                "ORM": Image.fromarray(orm, "RGB"),
            }
            if material == "Glass":
                opacity_src = required_map(tex, prefix, "opacity")
                output_images["Opacity"] = Image.open(opacity_src).convert("L")
            files = []
            for kind, image in output_images.items():
                target = dest / f"TX_{slug}_{material}_{kind}.png"
                image.save(target, format="PNG", optimize=True)
                files.append({
                    "role": kind, "file": str(target.relative_to(output)),
                    "bytes": target.stat().st_size,
                    "sha256": digest(target), "resolution": [1024, 1024],
                })
            maps.append({
                "material": material, "source_prefix": prefix,
                "maps": files, "source_diffuse_sha256": digest(src_diff),
                "source_normal_gl_sha256": digest(src_nor),
                "source_roughness_sha256": digest(src_rough),
                "source_metallic_sha256": digest(src_metal) if src_metal else None,
                "normal_convention": "DirectX green inverted from OpenGL",
                "orm_channels": "R=AO=white fallback; G=Roughness; B=Metallic",
            })
        results.append({
            "asset_id": slug, "fbx_path": str((dest / fbx.name).relative_to(output)),
            "fbx_sha256": digest(fbx), "fbx_bytes": fbx.stat().st_size,
            "material_count": len(maps), "materials": maps,
            "unreal_imported": False, "visual_accepted": False,
        })
    report = {
        "schema_version": 1,
        "packet": "P1C01_POLYHAVEN_FBX_PNG_STATIC_CANDIDATE_V1",
        "status": "SOURCE_TEXTURES_CONVERTED_STATIC_ONLY",
        "asset_count": len(results),
        "source_provider": "Poly Haven CC0",
        "conversion": "1K base PNG; 1K OpenGL normal to DirectX PNG; 1K ORM RGB AO=white G roughness B metallic",
        "caution": "Preserved source FBX normals and UV, but source FBX has no separate smoothing-group node. Must review UE4 import and LODs.",
        "evidence_boundary": "Not Unreal imported, not PIE tested, not human visually accepted, no device FPS measurement.",
        "assets": results,
    }
    (output / "p1c01_png_material_conversion_receipt.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    options = parser.parse_args()
    result = build(options.source, options.output)
    print(
        f"P1C01_POLYHAVEN_PNG_PREPARED assets={result['asset_count']} "
        f"status={result['status']}"
    )
