#!/usr/bin/env python3
"""Generate a bounded, project-owned broadleaf canopy source for UE4.27."""
from __future__ import annotations
import argparse
import math
from pathlib import Path

LOBE_DATA = (
    ((0.0, 0.0, 166.0), (92.0, 82.0, 112.0), 0.1),
    ((-66.0, -2.0, 164.0), (78.0, 72.0, 80.0), 1.3),
    ((66.0, 4.0, 170.0), (78.0, 72.0, 84.0), 2.1),
    ((0.0, -56.0, 168.0), (78.0, 70.0, 80.0), 2.9),
    ((0.0, 56.0, 165.0), (78.0, 70.0, 80.0), 3.7),
)
SEGMENTS = 10
LATITUDE_RINGS = 6


def generate() -> str:
    vertices: list[tuple[float, float, float]] = []
    uvs: list[tuple[float, float]] = []
    faces: list[tuple[int, int, int]] = []
    for center, radii, phase in LOBE_DATA:
        cx, cy, cz = center
        rx, ry, rz = radii
        top = len(vertices) + 1
        vertices.append((cx, cy, cz + rz))
        uvs.append((0.5, 1.0))
        rings: list[list[int]] = []
        for latitude in range(1, LATITUDE_RINGS):
            phi = math.pi * latitude / LATITUDE_RINGS
            ring: list[int] = []
            for segment in range(SEGMENTS + 1):
                theta = 2.0 * math.pi * segment / SEGMENTS
                wobble = 1.0 + 0.035 * math.sin(theta * 3.0 + phase) * math.sin(phi * 4.0 + phase)
                ring.append(len(vertices) + 1)
                vertices.append((
                    cx + rx * math.sin(phi) * math.cos(theta) * wobble,
                    cy + ry * math.sin(phi) * math.sin(theta) * wobble,
                    cz + rz * math.cos(phi) * wobble,
                ))
                uvs.append((segment / SEGMENTS, 1.0 - latitude / LATITUDE_RINGS))
            rings.append(ring)
        bottom = len(vertices) + 1
        vertices.append((cx, cy, cz - rz))
        uvs.append((0.5, 0.0))
        first = rings[0]
        for segment in range(SEGMENTS):
            faces.append((top, first[segment], first[segment + 1]))
        for upper, lower in zip(rings, rings[1:]):
            for segment in range(SEGMENTS):
                faces.append((upper[segment], lower[segment], lower[segment + 1]))
                faces.append((upper[segment], lower[segment + 1], upper[segment + 1]))
        last = rings[-1]
        for segment in range(SEGMENTS):
            faces.append((last[segment], bottom, last[segment + 1]))
    lines = [
        "# Original project-owned broadleaf crown; five overlapped, UV-mapped foliage lobes.",
        "# Unreal units: centimeters, Z-up; source budget 285 vertices / 500 triangles.",
        "mtllib ShireMaterials.mtl",
        "o SM_ShTreeCanopy",
    ]
    lines.extend("v %.4f %.4f %.4f" % v for v in vertices)
    lines.extend("vt %.6f %.6f" % uv for uv in uvs)
    lines.extend(("usemtl Leaves", "s 1"))
    lines.extend("f " + " ".join("%d/%d" % (i, i) for i in face) for face in faces)
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(generate(), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
