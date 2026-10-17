"""Small deterministic scalp-tangent shaping for authored MPFB curl tufts."""
import math


def remap_curl_offset(dx, dy, dz, angle, tangential=1.45, radial=0.58, vertical=1.45):
    """Shape a round tuft into a soft lock aligned to the scalp's tangent."""
    cosine, sine = math.cos(angle), math.sin(angle)
    radial_offset = dx * cosine + dy * sine
    tangent_offset = -dx * sine + dy * cosine
    return (
        cosine * radial_offset * radial - sine * tangent_offset * tangential,
        sine * radial_offset * radial + cosine * tangent_offset * tangential,
        dz * vertical,
    )
