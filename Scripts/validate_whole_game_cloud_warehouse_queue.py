#!/usr/bin/env python3
"""Validate the whole-game cloud warehouse/material queue."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_REGION_COUNT = 28
REQUIRED_QC = {
    "source_rights_receipt",
    "sha256_original_receipt",
    "derived_copy_only",
    "blender_static_qc",
    "material_slot_validation",
    "lod_or_culling_plan",
    "collision_strategy",
    "import_batch_manifest",
}
REQUIRED_BLOCKERS = {
    "Git terminal clone/credentials unavailable",
    "Self-hosted UE4 job queued by source-only metadata",
    "Linux Blender failed because NumPy was missing",
    "Binary FBX sources lacked LayerElementSmoothing",
    "Degenerate faces risk during normalization",
    "Repeated full scans/builds slowed production",
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate(queue: dict) -> list[str]:
    errors: list[str] = []

    if queue.get("status") != "ACTIVE_CLOUD_SOURCE_PREP_SELF_HOSTED_RUNTIME_LOCKED":
        errors.append("QUEUE_STATUS_NOT_CLOUD_LOCKED")

    regions = queue.get("regions", [])
    if len(regions) != REQUIRED_REGION_COUNT:
        errors.append(f"REGION_COUNT_INVALID:{len(regions)}")

    ids = [region.get("id") for region in regions]
    if len(ids) != len(set(ids)):
        errors.append("REGION_IDS_NOT_UNIQUE")

    if not any(region.get("runtime_status") == "RUNTIME_FIRST" and "SHIRE" in region.get("id", "") for region in regions):
        errors.append("P1C01_SHIRE_RUNTIME_FIRST_MISSING")

    for region in regions:
        region_id = region.get("id", "<missing>")
        missing_qc = REQUIRED_QC - set(region.get("qc_required_before_unreal", []))
        if missing_qc:
            errors.append(f"REGION_QC_MISSING:{region_id}:{','.join(sorted(missing_qc))}")
        if not region.get("material_targets"):
            errors.append(f"REGION_MATERIAL_TARGETS_EMPTY:{region_id}")
        if not region.get("required_asset_groups"):
            errors.append(f"REGION_ASSET_GROUPS_EMPTY:{region_id}")

    blockers = {entry.get("blocker") for entry in queue.get("root_cause_fixes", [])}
    missing_blockers = REQUIRED_BLOCKERS - blockers
    if missing_blockers:
        errors.append("ROOT_CAUSE_FIXES_MISSING:" + ",".join(sorted(missing_blockers)))

    material_contract = queue.get("material_quality_contract", {})
    for key in ("texture_sets", "ue4_compatibility", "blender_qc", "unreal_import_contract"):
        if not material_contract.get(key):
            errors.append(f"MATERIAL_CONTRACT_EMPTY:{key}")

    boundary = queue.get("evidence_boundary", "").lower()
    forbidden = ("pie accepted", "windows package complete", "gate 6/7 accepted", "visual accepted")
    for phrase in forbidden:
        if phrase in boundary:
            errors.append("EVIDENCE_BOUNDARY_OVERCLAIMS:" + phrase)

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", default="Data/WholeGameCloudWarehouseMaterialQueueV1.json")
    args = parser.parse_args(argv)

    errors = validate(load_json(Path(args.queue)))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("WHOLE_GAME_CLOUD_WAREHOUSE_QUEUE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
