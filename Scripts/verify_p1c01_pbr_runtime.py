#!/usr/bin/env python3
"""Fail closed when imported Shire PBR assets exist on disk but none appear in the running world.

Checks headless UE4 runtime logs; does NOT certify render quality, PIE, device or FPS.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


class RuntimePresenceError(ValueError):
    pass


def require(condition: bool, code: str) -> None:
    if not condition:
        raise RuntimePresenceError(code)


def read_json(path: Path) -> dict:
    require(path.is_file() and not path.is_symlink(), "PBR_RUNTIME_INPUT_MISSING")
    result = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(result, dict), "PBR_RUNTIME_JSON_INVALID")
    return result


def read_log(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), "PBR_RUNTIME_LOG_MISSING")
    data = path.read_bytes()
    encoding = "utf-16" if data.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
    return data.decode(encoding, errors="replace")


def verify(project: Path, runtime_log: Path) -> dict:
    source = read_json(project / "Data/P1C01VerifiedWorldDecor.json")
    require(source.get("chapter") == "P1C01" and source.get("status") ==
            "UE_PACKAGES_PRESENT_RENDER_QC_PENDING", "PBR_RUNTIME_NOT_ACTIVATED")
    accents = source.get("accents")
    require(isinstance(accents, list) and 1 <= len(accents) <= 16,
            "PBR_RUNTIME_NO_BOUND_DECOR")
    expected_assets = []
    prefix = "/Game/Production/World/Shire/VerifiedPBR/"
    for row in accents:
        require(isinstance(row, dict), "PBR_RUNTIME_ENTRY_INVALID")
        path = row.get("asset")
        require(isinstance(path, str) and path.startswith(prefix) and
                "." in path[len(prefix):] and
                isinstance(row.get("location"), list) and len(row["location"]) == 3,
                "PBR_RUNTIME_UNAUTHORIZED_ASSET")
        expected_assets.append(path)
    require(len(expected_assets) == len(set(expected_assets)),
            "PBR_RUNTIME_DUPLICATE_ASSET")
    bank = read_json(project / "Data/ChapterAssetStreamingPlan.json")
    resident = bank.get("banks", {}).get("P1C01", {}).get("assets", [])
    require(isinstance(resident, list) and
            all(path in resident for path in expected_assets),
            "PBR_NOT_IN_ACTIVE_ASYNC_BANK")

    records = re.findall(
        r"P1C01_PBR_DECOR_RUNTIME placed=(\d+) omitted=(\d+) collision=none visual=pending",
        read_log(runtime_log))
    require(records, "PBR_RUNTIME_PLACEMENT_LOG_MISSING")
    count = len(expected_assets)
    require(all(int(placed) == count and int(omitted) == 0
                for placed, omitted in records),
            "PBR_RUNTIME_PLACEMENT_MISMATCH")
    result = {
        "schema_version": 1,
        "chapter": "P1C01",
        "status": "HEADLESS_RUNTIME_PLACEMENT_PASS_VISUAL_PENDING",
        "expected_decor": count,
        "log_placement_observations": len(records),
        "source_log": str(runtime_log),
        "evidence_boundary": "Headless runtime mesh residency and actor placement only; no visual, PIE, device, FPS or Gate 6/7 acceptance.",
    }
    receipt = project / "Saved/P1C01VerifiedPBR/runtime_presence_receipt.json"
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("P1C01_PBR_RUNTIME_PRESENCE_PASS placed=" + str(count) +
          " observations=" + str(len(records)) + " visualAccepted=false")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--runtime-log", required=True, type=Path)
    args = parser.parse_args()
    try:
        verify(args.project_root, args.runtime_log)
        return 0
    except (RuntimePresenceError, ValueError, TypeError, OSError) as exc:
        print("P1C01_PBR_RUNTIME_PRESENCE_FAIL " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
