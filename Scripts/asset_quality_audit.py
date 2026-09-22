#!/usr/bin/env python3
"""Fast source-asset quality audit for the UE4.27 production bank.

This is a pre-engine diagnostic. It reports structural OBJ/MTL/PNG/TGA risks quickly and
does not pretend to replace Unreal import, PIE, or visual review.
"""

from __future__ import annotations

import argparse
import math
import os
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCTION = ROOT / "SourceAssets" / "Production"


def parse_face_index(token: str, vertex_count: int) -> int | None:
    raw = token.split("/", 1)[0]
    try:
        index = int(raw)
    except ValueError:
        return None
    if index < 0:
        return vertex_count + index
    return index - 1


def triangle_area(a, b, c) -> float:
    ab = (b[0]-a[0], b[1]-a[1], b[2]-a[2])
    ac = (c[0]-a[0], c[1]-a[1], c[2]-a[2])
    cross = (
        ab[1]*ac[2] - ab[2]*ac[1],
        ab[2]*ac[0] - ab[0]*ac[2],
        ab[0]*ac[1] - ab[1]*ac[0],
    )
    return 0.5 * math.sqrt(sum(value * value for value in cross))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="Fail on structural asset defects.")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    stats = Counter()
    dimension_counts = Counter()
    production_bucket_bytes = Counter()
    production_bucket_triangles = Counter()
    largest_obj_triangles: tuple[int, str] = (0, "")

    obj_files = sorted(PRODUCTION.rglob("*.obj"))
    mtl_files = sorted(PRODUCTION.rglob("*.mtl"))
    legacy_bmp_files = sorted(PRODUCTION.rglob("*.bmp"))
    texture_files = sorted(PRODUCTION.rglob("*.png")) + sorted(PRODUCTION.rglob("*.tga"))
    if legacy_bmp_files:
        errors.extend(
            f"{path.relative_to(ROOT)} uses forbidden uncompressed BMP; convert to PNG/TGA"
            for path in legacy_bmp_files
        )

    mtl_cache: dict[Path, set[str]] = {}

    for mtl in mtl_files:
        materials: set[str] = set()
        try:
            lines = mtl.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception as exc:
            errors.append(f"{mtl.relative_to(ROOT)} unreadable: {exc}")
            continue
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("newmtl "):
                name = stripped[7:].strip()
                if name in materials:
                    warnings.append(f"{mtl.relative_to(ROOT)} duplicates material {name}")
                materials.add(name)
            elif stripped.lower().startswith("map_kd "):
                texture_ref = stripped[7:].strip()
                texture_path = (mtl.parent / texture_ref).resolve()
                if not texture_path.exists():
                    warnings.append(
                        f"{mtl.relative_to(ROOT)} references missing diffuse texture {texture_ref}"
                    )
        mtl_cache[mtl.resolve()] = materials

    for obj in obj_files:
        stats["obj"] += 1
        relative_parts = obj.relative_to(PRODUCTION).parts
        bucket = "/".join(relative_parts[:2]) if len(relative_parts) >= 2 else relative_parts[0]
        try:
            source_bytes = obj.stat().st_size
        except OSError:
            source_bytes = 0
        stats["obj_source_bytes"] += source_bytes
        production_bucket_bytes[bucket] += source_bytes
        vertices: list[tuple[float, float, float]] = []
        material_libraries: list[str] = []
        used_materials: set[str] = set()
        normal_count = 0
        uv_count = 0
        smoothing_seen = False
        zero_area_faces = 0
        malformed_faces = 0

        try:
            lines = obj.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception as exc:
            errors.append(f"{obj.relative_to(ROOT)} unreadable: {exc}")
            continue

        face_tokens: list[list[str]] = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("v "):
                parts = stripped.split()
                if len(parts) >= 4:
                    try:
                        vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
                    except ValueError:
                        errors.append(f"{obj.relative_to(ROOT)} contains malformed vertex data")
            elif stripped.startswith("vn "):
                normal_count += 1
            elif stripped.startswith("vt "):
                uv_count += 1
            elif stripped.startswith("s ") and stripped.lower() not in {"s off", "s 0"}:
                smoothing_seen = True
            elif stripped.startswith("mtllib "):
                material_libraries.extend(stripped[7:].strip().split())
            elif stripped.startswith("usemtl "):
                used_materials.add(stripped[7:].strip())
            elif stripped.startswith("f "):
                face_tokens.append(stripped.split()[1:])

        if normal_count == 0:
            stats["obj_without_normals"] += 1
        if uv_count == 0:
            stats["obj_without_uvs"] += 1
        if not smoothing_seen:
            stats["obj_without_smoothing_groups"] += 1

        defined_materials: set[str] = set()
        for library in material_libraries:
            mtl_path = (obj.parent / library).resolve()
            if not mtl_path.exists():
                errors.append(
                    f"{obj.relative_to(ROOT)} references missing mtllib {library}"
                )
                continue
            defined_materials.update(mtl_cache.get(mtl_path, set()))

        if used_materials and material_libraries:
            undefined = sorted(used_materials - defined_materials)
            if undefined:
                warnings.append(
                    f"{obj.relative_to(ROOT)} uses undefined materials: {', '.join(undefined)}"
                )

        triangulation_risk_faces = 0
        obj_triangle_equivalents = 0
        for tokens in face_tokens:
            if len(tokens) < 3:
                malformed_faces += 1
                continue

            obj_triangle_equivalents += max(0, len(tokens) - 2)
            indices = [parse_face_index(token, len(vertices)) for token in tokens]
            if any(index is None or index < 0 or index >= len(vertices) for index in indices):
                malformed_faces += 1
                continue

            polygon_area = 0.0
            fan_areas: list[float] = []
            for offset in range(1, len(indices) - 1):
                area = triangle_area(
                    vertices[indices[0]],
                    vertices[indices[offset]],
                    vertices[indices[offset + 1]],
                )
                fan_areas.append(area)
                polygon_area += area

            if polygon_area <= 1e-7:
                zero_area_faces += 1
            elif any(area <= 1e-7 for area in fan_areas):
                triangulation_risk_faces += 1

        if malformed_faces:
            errors.append(
                f"{obj.relative_to(ROOT)} has {malformed_faces} malformed/out-of-range faces"
            )
        if zero_area_faces:
            warnings.append(
                f"{obj.relative_to(ROOT)} has {zero_area_faces} truly near-zero-area faces"
            )
            stats["obj_with_zero_area_faces"] += 1
        if triangulation_risk_faces:
            errors.append(
                f"{obj.relative_to(ROOT)} has {triangulation_risk_faces} triangulation-risk faces"
            )
            stats["obj_with_triangulation_risk"] += 1

        stats["obj_triangle_equivalents"] += obj_triangle_equivalents
        production_bucket_triangles[bucket] += obj_triangle_equivalents
        if obj_triangle_equivalents > largest_obj_triangles[0]:
            largest_obj_triangles = (obj_triangle_equivalents, obj.relative_to(ROOT).as_posix())

    for texture in texture_files:
        stats["texture"] += 1
        relative_parts = texture.relative_to(PRODUCTION).parts
        bucket = "/".join(relative_parts[:2]) if len(relative_parts) >= 2 else relative_parts[0]
        try:
            data = texture.read_bytes()
        except Exception as exc:
            errors.append(f"{texture.relative_to(ROOT)} unreadable: {exc}")
            continue

        width = height = 0
        suffix = texture.suffix.lower()
        if suffix == ".tga":
            if len(data) < 18 or data[2] not in (2, 10):
                errors.append(f"{texture.relative_to(ROOT)} is not a supported TGA")
                continue
            width = struct.unpack_from("<H", data, 12)[0]
            height = struct.unpack_from("<H", data, 14)[0]
        elif suffix == ".png":
            if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
                errors.append(f"{texture.relative_to(ROOT)} is not a valid PNG header")
                continue
            width = struct.unpack_from(">I", data, 16)[0]
            height = struct.unpack_from(">I", data, 20)[0]

        if width <= 0 or height <= 0:
            errors.append(f"{texture.relative_to(ROOT)} has invalid dimensions")
            continue
        stats["texture_source_bytes"] += len(data)
        production_bucket_bytes[bucket] += len(data)
        dimension_counts[(width, height)] += 1
        if width > 1024 or height > 1024:
            warnings.append(
                f"{texture.relative_to(ROOT)} is {width}x{height}; review target-device cost"
            )

    summary = [
        "# Asset Quality Audit",
        "",
        f"- OBJ files: {len(obj_files)}",
        f"- MTL files: {len(mtl_files)}",
        f"- PNG/TGA files: {len(texture_files)}",
        f"- Forbidden BMP files: {len(legacy_bmp_files)}",
        f"- OBJ without explicit normals: {stats['obj_without_normals']}",
        f"- OBJ without UV coordinates: {stats['obj_without_uvs']}",
        f"- OBJ without smoothing groups: {stats['obj_without_smoothing_groups']}",
        f"- OBJ with truly near-zero-area faces: {stats['obj_with_zero_area_faces']}",
        f"- OBJ with triangulation-risk faces: {stats['obj_with_triangulation_risk']}",
        f"- Approx source triangle equivalents: {stats['obj_triangle_equivalents']:,}",
        f"- OBJ source bytes: {stats['obj_source_bytes']:,}",
        f"- Texture source bytes: {stats['texture_source_bytes']:,}",
        f"- Largest OBJ by triangle equivalents: {largest_obj_triangles[1] or 'n/a'} ({largest_obj_triangles[0]:,})",
        f"- Structural errors: {len(errors)}",
        f"- Warnings: {len(warnings)}",
    ]
    if dimension_counts:
        summary.append(
            "- Texture dimensions: "
            + ", ".join(
                f"{w}x{h}={count}"
                for (w, h), count in sorted(dimension_counts.items())
            )
        )
    if production_bucket_bytes:
        summary.append("- Production source buckets (bytes / triangle equivalents):")
        for bucket, byte_count in sorted(
            production_bucket_bytes.items(), key=lambda item: (-item[1], item[0])
        )[:24]:
            summary.append(
                f"  - {bucket}: {byte_count:,} bytes / {production_bucket_triangles.get(bucket, 0):,} tris"
            )

    print("\n".join(summary))
    if warnings:
        print("\nWarning sample:")
        for warning in warnings[:40]:
            print(f"WARNING: {warning}")
        if len(warnings) > 40:
            print(f"WARNING: ... {len(warnings)-40} more warnings omitted from console")

    if errors:
        print("\nStructural error sample:")
        for error in errors[:40]:
            print(f"ERROR: {error}")
        if len(errors) > 40:
            print(f"ERROR: ... {len(errors)-40} more errors omitted from console")

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write("\n".join(summary) + "\n")

    if args.strict and errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
