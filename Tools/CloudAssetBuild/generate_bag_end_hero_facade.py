#!/usr/bin/env python3
"""Generate the dedicated, low-cost Bag End exterior hero facade OBJ.

The generic Hobbit-hole facade is intentionally reusable and reads as a flat
rectangle in the current 720p proof.  This asset gives Bag End its own curved
earth silhouette, stone plinth, round stone/timber entrance and paired round
windows without adding runtime procedural mesh work or extra ticking actors.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path


class Obj:
    def __init__(self) -> None:
        self.vertices: list[tuple[float, float, float]] = []
        self.groups: list[tuple[str, list[tuple[int, ...]]]] = []

    def add_group(self, material: str, faces: list[tuple[int, ...]]) -> None:
        self.groups.append((material, faces))

    def add_vertices(self, vertices: list[tuple[float, float, float]]) -> list[int]:
        start = len(self.vertices) + 1
        self.vertices.extend(vertices)
        return list(range(start, start + len(vertices)))

    def cuboid(self, material: str, x0: float, x1: float, y0: float, y1: float,
               z0: float, z1: float) -> None:
        ids = self.add_vertices([
            (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
            (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
        ])
        a, b, c, d, e, f, g, h = ids
        self.add_group(material, [
            (a, d, c, b), (e, f, g, h), (a, b, f, e),
            (b, c, g, f), (c, d, h, g), (d, a, e, h),
        ])

    def facade_slice(self, y0: float, y1: float, h0: float, h1: float) -> None:
        ids = self.add_vertices([
            (-15, y0, 12), (10, y0, 12), (10, y1, 12), (-15, y1, 12),
            (-15, y0, h0), (10, y0, h0), (10, y1, h1), (-15, y1, h1),
        ])
        a, b, c, d, e, f, g, h = ids
        self.add_group("Earth", [
            (a, d, c, b), (e, f, g, h), (a, b, f, e),
            (b, c, g, f), (c, d, h, g), (d, a, e, h),
        ])

    def ring(self, material: str, center_y: float, center_z: float,
             inner: float, outer: float, x_front: float, x_back: float,
             segments: int = 24) -> None:
        faces: list[tuple[int, ...]] = []
        for i in range(segments):
            a0 = 2.0 * math.pi * i / segments
            a1 = 2.0 * math.pi * (i + 1) / segments
            yz = []
            for x in (x_front, x_back):
                for radius, angle in ((inner, a0), (outer, a0), (outer, a1), (inner, a1)):
                    yz.append((x, center_y + math.cos(angle) * radius,
                               center_z + math.sin(angle) * radius))
            ids = self.add_vertices(yz)
            f0, f1, f2, f3, b0, b1, b2, b3 = ids
            faces.extend([
                (f0, f3, f2, f1), (b0, b1, b2, b3),
                (f0, f1, b1, b0), (f1, f2, b2, b1),
                (f2, f3, b3, b2), (f3, f0, b0, b3),
            ])
        self.add_group(material, faces)

    def write(self, path: Path) -> None:
        lines = [
            "# Dedicated Bag End hero exterior facade for Shire Journey",
            "# Generated deterministically; centimeters; west-facing front is -X",
            "mtllib ShireMaterials.mtl",
            "o SM_ShBagEndHeroFacade",
        ]
        lines.extend(f"v {x:.4f} {y:.4f} {z:.4f}" for x, y, z in self.vertices)
        for index, (material, faces) in enumerate(self.groups):
            lines.append(f"g hero_{index:03d}_{material}")
            lines.append(f"usemtl {material}")
            lines.extend("f " + " ".join(str(v) for v in face) for face in faces)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build(path: Path) -> None:
    obj = Obj()
    steps = 16
    ys = [-120.0 + 240.0 * i / steps for i in range(steps + 1)]
    heights = [108.0 + 52.0 * (1.0 - (abs(y) / 120.0) ** 1.65) for y in ys]
    for i in range(steps):
        obj.facade_slice(ys[i], ys[i + 1], heights[i], heights[i + 1])

    obj.cuboid("Stone", -27, 18, -126, 126, 0, 14)
    obj.ring("Stone", 0, 66, 57, 70, -30, -17, 28)
    obj.ring("Wood", 0, 66, 50, 57, -34, -28, 28)
    for side in (-1.0, 1.0):
        window_y = 84.0 * side
        obj.ring("Stone", window_y, 78, 24, 31, -28, -17, 20)
        obj.ring("Wood", window_y, 78, 19, 24, -32, -26, 20)
        obj.cuboid("Wood", -35, -24, window_y - 34, window_y + 34, 43, 48)
        obj.cuboid("Wood", -35, -24, window_y - 34, window_y + 34, 108, 113)

    obj.cuboid("Wood", -29, -17, -118, -110, 12, 112)
    obj.cuboid("Wood", -29, -17, 110, 118, 12, 112)
    obj.cuboid("Stone", -38, -20, -55, 55, 8, 16)
    obj.write(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    build(args.output)


if __name__ == "__main__":
    main()
