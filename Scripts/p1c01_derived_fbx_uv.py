"""Blender-independent UV repair math for disposable static P1C01 FBX derivatives.

Valid UV islands remain untouched. Geometry, vertex indices, face topology and
source warehouse FBX are never changed by these helpers.
"""
from __future__ import annotations

import math


class DegenerateUVError(ValueError):
    pass


def signed_uv_area2(uv):
    """Twice the signed area of a UV polygon."""
    return sum(
        float(uv[i][0]) * float(uv[(i + 1) % len(uv)][1])
        - float(uv[(i + 1) % len(uv)][0]) * float(uv[i][1])
        for i in range(len(uv))
    )


def needs_uv_repair(uv, minimum_double_area=1e-7):
    """Select only clearly invalid whole-face UV islands.

    Per-triangle Unreal tangent quality remains a separate engine-side gate.
    """
    if len(uv) < 3:
        return True
    if any(not all(math.isfinite(float(v)) for v in pair) for pair in uv):
        return True
    return abs(signed_uv_area2(uv)) <= minimum_double_area


def project_face_uv(xyz, normal):
    """Project a single unusable UV polygon onto its dominant face plane.

    No vertices or normal vectors are modified. Normalize both axes by the same
    extent, retaining physical proportions without stretching a narrow face.
    """
    if len(xyz) < 3 or len(xyz) != len(set(tuple(p) for p in xyz)):
        raise DegenerateUVError("INVALID_FACE_VERTICES")
    if any(len(p) != 3 or not all(math.isfinite(float(v)) for v in p) for p in xyz):
        raise DegenerateUVError("NONFINITE_FACE_GEOMETRY")
    if len(normal) != 3 or not all(math.isfinite(float(v)) for v in normal):
        raise DegenerateUVError("NONFINITE_FACE_NORMAL")
    excluded = max(range(3), key=lambda dim: abs(normal[dim]))
    dims = tuple(dim for dim in range(3) if dim != excluded)
    planar = [(float(point[dims[0]]), float(point[dims[1]])) for point in xyz]
    us, vs = zip(*planar)
    extent = max(max(us) - min(us), max(vs) - min(vs))
    if extent <= 1e-10:
        raise DegenerateUVError("COLLAPSED_PLANAR_PROJECTION")
    result = [((u - min(us)) / extent, (v - min(vs)) / extent) for u, v in planar]
    if needs_uv_repair(result):
        raise DegenerateUVError("DEGENERATE_PROJECTED_UV")
    return result
