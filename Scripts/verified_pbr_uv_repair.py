"""Repair collapsed UV face corners in disposable PBR derivatives only.

Never weld vertices, edit valid UV seams, change normals or mutate original FBX.
The exact-head UE4 zero-warning gate is the authoritative test of repair.
"""
import math

UV_AREA2_EPS = 1e-8


def triangle_uv_area2(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def collapsed_uv_face(uvs):
    if len(uvs) < 3:
        return True
    if not all(math.isfinite(float(x)) for uv in uvs for x in uv):
        return True
    anchor = uvs[0]
    return any(abs(triangle_uv_area2(anchor, uvs[i], uvs[i+1])) <= UV_AREA2_EPS
               for i in range(1, len(uvs)-1))


def repaired_face_uvs(uvs, positions, normal):
    """Return (UV corners, changed). Valid authored corner UVs are untouched."""
    if len(uvs) != len(positions) or len(uvs) < 3:
        raise ValueError("UV_CORNER_OR_POSITION_COUNT_INVALID")
    if not collapsed_uv_face(uvs):
        return tuple(tuple(uv) for uv in uvs), False
    if not all(math.isfinite(float(x)) for p in positions for x in p):
        raise ValueError("NONFINITE_VERTEX")
    if not all(math.isfinite(float(x)) for x in normal):
        raise ValueError("NONFINITE_NORMAL")
    dominant = max(range(3), key=lambda i: abs(normal[i]))
    axes = ((1, 2), (0, 2), (0, 1))[dominant]
    projected = [(float(p[axes[0]]), float(p[axes[1]])) for p in positions]
    min_u = min(p[0] for p in projected)
    min_v = min(p[1] for p in projected)
    scale = max(max(p[0] for p in projected)-min_u,
                max(p[1] for p in projected)-min_v, 1e-12)
    candidate = tuple(((p[0]-min_u)/scale, (p[1]-min_v)/scale) for p in projected)
    if collapsed_uv_face(candidate):
        n = len(uvs)
        candidate = tuple((0.5+0.5*math.cos(2*math.pi*i/n),
                           0.5+0.5*math.sin(2*math.pi*i/n)) for i in range(n))
    if collapsed_uv_face(candidate):
        raise ValueError("UNREPAIRABLE_UV_FACE")
    return candidate, True
