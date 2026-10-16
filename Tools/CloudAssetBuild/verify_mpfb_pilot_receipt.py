"""Validate actual produced MPFB source FBX, pose receipt and sidecar texture hashes."""
import hashlib
import json
from pathlib import Path
import sys


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for b in iter(lambda: stream.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    root = Path(sys.argv[1]).resolve()
    d = json.loads((root / "source_receipt.json").read_text(encoding="utf-8"))
    if d.get("status") != "SOURCE_FBX_PREPARED_NOT_UE_IMPORTED" or d.get("ue_import") != "NOT_RUN":
        raise RuntimeError("MPFB_SOURCE_RECEIPT_FALSE_ACCEPTANCE")
    motion = d.get("blender_joint_deformation", {})
    if d.get("bone_count", 0) < 30 or d.get("weighted_body_vertices", 0) < 1000 or set(motion) != {"arm", "leg"}:
        raise RuntimeError("MPFB_SKIN_POSE_PROOF_MISSING")
    fbx = root / d["fbx_name"]
    if fbx.stat().st_size < 100000 or sha(fbx) != d["fbx_sha256"]:
        raise RuntimeError("MPFB_FBX_HASH_MISMATCH")
    sidecars = d.get("texture_sidecars", [])
    if not sidecars:
        raise RuntimeError("MPFB_TEXTURE_SIDECARS_MISSING")
    for sidecar in sidecars:
        p = root / "Textures" / sidecar["name"]
        if not p.is_file() or sha(p) != sidecar["sha256"]:
            raise RuntimeError("MPFB_TEXTURE_SHA_MISMATCH: " + str(p))
    print("MPFB_SOURCE_FBX_PASS bones=" + str(d["bone_count"]) +
          " weighted=" + str(d["weighted_body_vertices"]) +
          " textures=" + str(len(sidecars)) + " UE=NOT_RUN", flush=True)


if __name__ == "__main__":
    main()
