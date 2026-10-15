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
        self.add_group("BagEndPlaster", [
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
                (f1, f2, b2, b1),
                (f3, f0, b0, b3),
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
        # Consolidate by material: one render section per finish, not per plank.
        grouped = {}
        for material, faces in self.groups:
            grouped.setdefault(material, []).extend(faces)
        uv_index = 1
        for material, faces in grouped.items():
            lines.extend((f"g hero_{material}", f"usemtl {material}", "s off"))
            for face in faces:
                vertices = [self.vertices[i - 1] for i in face]
                a, b, c = vertices[:3]
                ab = [b[i] - a[i] for i in range(3)]
                ac = [c[i] - a[i] for i in range(3)]
                normal = (ab[1]*ac[2]-ab[2]*ac[1], ab[2]*ac[0]-ab[0]*ac[2], ab[0]*ac[1]-ab[1]*ac[0])
                axis = max(range(3), key=lambda i: abs(normal[i]))
                axes = [i for i in range(3) if i != axis]
                # Planar 100 cm texel scale; no stretched full texture per sliver.
                for v in vertices:
                    lines.append(f"vt {v[axes[0]] / 100:.6f} {v[axes[1]] / 100:.6f}")
                refs = [f"{v}/{uv_index+i}" for i, v in enumerate(face)]
                for i in range(1, len(face)-1):
                    triangle = (vertices[0], vertices[i], vertices[i+1])
                    u = [triangle[1][k]-triangle[0][k] for k in range(3)]
                    v = [triangle[2][k]-triangle[0][k] for k in range(3)]
                    cross = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
                    if sum(c*c for c in cross) > 1e-12:
                        lines.append(f"f {refs[0]} {refs[i]} {refs[i+1]}")
                uv_index += len(face)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build(path: Path) -> None:
    obj = Obj()
    steps = 32
    ys = [-126.0 + 252.0 * i / steps for i in range(steps + 1)]
    heights = [16.0 + 132.0 * math.sqrt(max(0, 1-(y/126)**2)) for y in ys]
    for i in range(steps):
        obj.facade_slice(ys[i], ys[i+1], heights[i], heights[i+1])

    # Earth-covered roof joins the same front profile, spreads into the hillside,
    # then meets the ground behind the house. No detached spherical mound.
    rows = []
    for j in range(13):
        t = j / 12
        x = -10 + 390*t
        width = 126*(1-t) + 125*math.sin(math.pi*t)
        height = 132*(1-t)**0.65
        rows.append(obj.add_vertices([(x, -width*math.cos(math.pi*i/24),
            16*(1-t) + height*math.sin(math.pi*i/24)) for i in range(25)]))
    for j in range(12):
        for i in range(24):
            if j == 11:
                face = (rows[j][i], rows[j][i+1], rows[j+1][i])
            else:
                face = (rows[j][i], rows[j][i+1], rows[j+1][i+1], rows[j+1][i])
            obj.add_group("Grass", [tuple(reversed(face))])

    obj.cuboid("Stone", -27, 18, -126, 126, 0, 14)
    obj.ring("Stone", 0, 62, 49, 57, -29, -14, 40)
    obj.ring("Wood", 0, 62, 45, 49, -33, -26, 40)
    # A recessed closed door made of fitted planks, with a central brass knob.
    # Slot-based finishes persist with the imported mesh; no emissive discs.
    for i in range(12):
        y0, y1 = -45 + i*7.5 + .12, -45 + (i+1)*7.5 - .12
        z0 = math.sqrt(max(0, 45**2-y0**2))
        z1 = math.sqrt(max(0, 45**2-y1**2))
        ids = obj.add_vertices([(-31,y0,62-z0),(-31,y1,62-z1),
            (-31,y1,62+z1),(-31,y0,62+z0)])
        obj.add_group("BagEndDoor", [tuple(reversed(ids))])
    obj.ring("BagEndBrass", 0, 62, 0, 2.4, -35, -31, 12)
    for side in (-1, 1):
        y = 87*side
        obj.ring("Stone", y, 66, 20, 26, -28, -14, 24)
        obj.ring("Wood", y, 66, 17, 20, -32, -26, 24)
        obj.ring("BagEndGlass", y, 66, 0, 17, -30, -28, 24)
        obj.cuboid("Wood", -33,-29,y-.8,y+.8,49,83)
        obj.cuboid("Wood", -33,-29,y-17,y+17,65.2,66.8)
        obj.cuboid("Stone", -38,-14,y-28,y+28,38,43)
    obj.cuboid("Stone", -38,-20,-55,55,8,16)
    obj.write(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    build(args.output)


if __name__ == "__main__":
    main()
