#!/usr/bin/env python3
"""Fail-closed evidence for real P1C01 verified static FBX/material UE4 import.

Inspect the exact import commandlet log, staged source receipt and generated UE
packages. No render, PIE, target-device or visual acceptance is implied.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


class ImportProofError(ValueError):
    pass


def require(valid: bool, marker: str) -> None:
    if not valid:
        raise ImportProofError(marker)


def verify(project_root: Path, import_log: Path) -> dict:
    staged = project_root / "Saved/P1C01VerifiedPBR/source_stage_receipt.json"
    require(staged.is_file() and not staged.is_symlink(), "SOURCE_RECEIPT_MISSING")
    receipt = json.loads(staged.read_text(encoding="utf-8-sig"))
    rows = receipt.get("assets", [])
    require(receipt.get("stage") == "HASHED_SOURCE_ONLY" and
            isinstance(rows, list) and 1 <= len(rows) <= 16 and
            receipt.get("count") == len(rows), "SOURCE_RECEIPT_INVALID")
    require(import_log.is_file() and not import_log.is_symlink(), "UE_IMPORT_LOG_MISSING")
    raw = import_log.read_bytes()
    encoding = "utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
    log = raw.decode(encoding, errors="replace")
    prefix = "/Game/Production/World/Shire/VerifiedPBR/"
    ids = set()
    for row in rows:
        require(isinstance(row, dict), "SOURCE_ROW_INVALID")
        slug = row.get("id")
        require(isinstance(slug, str) and re.fullmatch(r"[a-z0-9_]{3,80}", slug),
                "UNSAFE_SOURCE_SLUG")
        require(slug not in ids, "DUPLICATE_SOURCE_SLUG")
        ids.add(slug)
        expected_material = prefix + slug + "/MI_P1C01_" + slug + ".MI_P1C01_" + slug
        require(row.get("material") == expected_material and
                row.get("mesh") == prefix + slug + "/" + slug + "." + slug,
                "SOURCE_PACKAGE_IDENTITY_INVALID")
        folder = project_root / "Content/Production/World/Shire/VerifiedPBR" / slug
        for file in (slug + ".uasset", "MI_P1C01_" + slug + ".uasset"):
            package = folder / file
            require(package.is_file() and not package.is_symlink() and
                    package.stat().st_size > 2048,
                    "UE_PACKAGE_MISSING:" + slug + "/" + file)
        marker = ("P1C01_VERIFIED_PBR_IMPORT_QC mesh=" + slug +
                  " material=" + expected_material + " lodCount=")
        require(marker in log, "PBR_MATERIAL_SLOT_NOT_PROVEN:" + slug)
        lods = re.findall(re.escape(marker) + r"(\d+)\s+collision=decor-only", log)
        require(lods and any(int(n) >= 1 for n in lods),
                "PBR_RENDER_LOD_NOT_PROVEN:" + slug)
    proof = {
        "schema_version": 1,
        "chapter": "P1C01",
        "status": "UE4_STATIC_MESH_MATERIAL_SLOT_QC_PASS_VISUAL_PENDING",
        "source_count": len(rows),
        "confirmed_mesh_material_pairs": len(ids),
        "import_log": str(import_log),
        "evidence_boundary": "Exact UE commandlet mesh/material slot and package existence. No rendered normal/ORM shader, PIE, device, FPS or Gate 6/7 acceptance.",
    }
    out = project_root / "Saved/P1C01VerifiedPBR/ue_import_receipt.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
    print("P1C01_PBR_UNREAL_IMPORT_QC_PASS bound=" + str(len(ids)) +
          " unbound=0 visualAccepted=false")
    return proof


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--import-log", type=Path, required=True)
    args = parser.parse_args()
    try:
        verify(args.project_root, args.import_log)
        return 0
    except (ImportProofError, KeyError, ValueError, TypeError, OSError) as exc:
        print("P1C01_PBR_IMPORT_FAIL " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
