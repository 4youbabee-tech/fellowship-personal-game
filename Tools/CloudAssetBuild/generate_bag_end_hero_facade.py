#!/usr/bin/env python3
"""Deterministic, joined and ground-buried Bag End hero exterior (centimetres).

UE4.27 uses the existing single OBJ/MTL importer and material binding. The roof
front border is IDENTICAL to and shares OBJ vertex IDs with the plaster wall's
curved upper border; both side skirts and the rear edge terminate below ground.
No mesh collision, quest anchors or runtime ownership are changed here.
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

    def continuous_facade(self, ys: list[float], heights: list[float]) -> list[int]:
        """Build one wall surface instead of 32 closed slices; return shared crown.

        Top-front vertices MUST be reused as the roof's first row. The rear wall
        is contained beneath the turf, and the foundation is buried 9cm.
        """
        assert len(ys) == len(heights) and len(ys) >= 3
        crown = self.add_vertices([(-15.0, y, z) for y, z in zip(ys, heights)])
        foot = self.add_vertices([(-15.0, y, -9.0) for y in ys])
        back_crown = self.add_vertices([(10.0, y, z - 3.0) for y, z in zip(ys, heights)])
        back_foot = self.add_vertices([(10.0, y, -9.0) for y in ys])
        faces = []
        for i in range(len(ys) - 1):
            faces.extend([
                (foot[i], crown[i], crown[i+1], foot[i+1]),
                (back_foot[i+1], back_crown[i+1], back_crown[i], back_foot[i]),
                (foot[i+1], back_foot[i+1], back_foot[i], foot[i]),
            ])
        faces.extend([
            (foot[0], back_foot[0], back_crown[0], crown[0]),
            (back_foot[-1], foot[-1], crown[-1], back_crown[-1]),
        ])
        self.add_group("BagEndPlaster", faces)
        return crown

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
                (f1, f2, b2, b1), (f3, f0, b0, b3),
            ])
        self.add_group(material, faces)

    def write(self, path: Path) -> None:
        lines = [
            "# Dedicated Bag End hero exterior facade for Shire Journey",
            "# Generated deterministically; centimeters; west-facing front is -X",
            "# Shared roof/front crown; buried sides+rear; no runtime collision",
            "mtllib ShireMaterials.mtl",
            "o SM_ShBagEndHeroFacade",
        ]
        lines.extend(f"v {x:.4f} {y:.4f} {z:.4f}" for x, y, z in self.vertices)
        grouped = {}
        for material, faces in self.groups:
            grouped.setdefault(material, []).extend(faces)
        uv_index = 1
        for material, faces in grouped.items():
            # Smooth the continuous turf only; stone/wood/plaster retain sharp edges.
            lines.extend((f"g hero_{material}", f"usemtl {material}",
                          "s 1" if material == "Grass" else "s off"))
            for face in faces:
                vertices = [self.vertices[i - 1] for i in face]
                a, b, c = vertices[:3]
                ab = [b[i] - a[i] for i in range(3)]
                ac = [c[i] - a[i] for i in range(3)]
                normal = (ab[1]*ac[2]-ab[2]*ac[1], ab[2]*ac[0]-ab[0]*ac[2], ab[0]*ac[1]-ab[1]*ac[0])
                axis = max(range(3), key=lambda i: abs(normal[i]))
                axes = [i for i in range(3) if i != axis]
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
    segments = 32
    ys = [-126.0 + 252.0 * i / segments for i in range(segments+1)]
    heights = [16.0 + 132.0 * math.sqrt(max(0.0, 1.0-(y/126.0)**2)) for y in ys]
    crown = obj.continuous_facade(ys, heights)

    # One continuous, shared roof-wall boundary. Intermediate rows reproduce a
    # hillside; the last edge sinks 8cm below terrain rather than hovering.
    rows = [crown]
    for j in range(1, 13):
        t = j / 12.0
        x = -15.0 + 395.0*t
        width = 126.0*(1.0-t) + 120.0*math.sin(math.pi*t) + 32.0*t
        crown_base = 16.0*(1.0-t) - 8.0*t
        dome = 132.0*(1.0-t)**0.68
        rows.append(obj.add_vertices([
            (x, -width + 2.0*width*i/segments,
             crown_base + dome*math.sqrt(max(0.0, 1.0-(-1.0+2.0*i/segments)**2)))
            for i in range(segments+1)
        ]))
    grass_faces = []
    for j in range(12):
        for i in range(segments):
            grass_faces.append((rows[j][i], rows[j+1][i], rows[j+1][i+1], rows[j][i+1]))

    # Two flared, deliberately buried turf aprons eliminate oblique camera
    # gaps without touching the walkable doorstep or any quest/collision anchor.
    # These side surfaces share the *same* upper-edge vertex IDs as the roof.
    skirts = []
    for j in range(13):
        t = j / 12.0
        x, y, _ = obj.vertices[rows[j][0]-1]
        offset = 46.0*(1.0-0.35*t)
        skirts.append(obj.add_vertices([(x, y-offset, -12.0-3.0*t),
                                       (x, -y+offset, -12.0-3.0*t)]))
    for j in range(12):
        grass_faces.append((rows[j][0], skirts[j][0], skirts[j+1][0], rows[j+1][0]))
        grass_faces.append((rows[j][-1], rows[j+1][-1], skirts[j+1][1], skirts[j][1]))
    obj.add_group("Grass", grass_faces)

    obj.cuboid("Stone", -27, 18, -126, 126, 0, 14)
    obj.ring("Stone", 0, 62, 49, 57, -29, -14, 40)
    obj.ring("Wood", 0, 62, 45, 49, -33, -26, 40)
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
