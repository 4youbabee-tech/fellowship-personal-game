#!/usr/bin/env python3
"""Validate P1C01 cloud asset production manifests."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "Data" / "P1C01CloudAssetProductionManifestsV1.json"

REQUIRED_STATIC_BATCHES = {
    "P1C01_STATIC_BAG_END_EXTERIOR",
    "P1C01_STATIC_BAG_END_INTERIOR",
    "P1C01_STATIC_HOBBITON_BAGSHOT_ROW",
    "P1C01_STATIC_PARTY_FIELD_FIREWORKS",
    "P1C01_STATIC_ROADS_WATER_MILL_BRIDGES",
    "P1C01_STATIC_NATURE_FARMS_GARDENS",
}

REQUIRED_CHARACTER_BATCHES = {
    "CHAR_FRODO_P1C01",
    "CHAR_BILBO_P1C01",
    "CHAR_GANDALF_P1C01",
    "CHAR_SAM_MERRY_PIPPIN_P1C01",
    "CHAR_BACKGROUND_HOBBITS_P1C01",
}

REQUIRED_MATERIAL_BATCHES = {
    "MAT_SHIRE_WARM_PLASTER",
    "MAT_SHIRE_AGED_WOOD",
    "MAT_SHIRE_THATCH_AND_GRASS",
    "MAT_SHIRE_STONE_SOIL_WATER",
    "MAT_CHARACTER_HOBBIT_CLOTH_LEATHER",
}

REQUIRED_STATIC_QC = {
    "uv0_present",
    "normals_present",
    "material_slots_named",
}

REQUIRED_BLENDER_STATIC_CHECKS = {
    "degenerate_faces_repaired_on_derived_copy",
    "uv0_present",
    "normals_present",
    "smoothing_or_custom_normals_present",
    "material_slots_preserved",
}

FORBIDDEN_RUNTIME_CLAIMS = {
    "IMPORTED_IN_UNREAL",
    "MATERIALS_BOUND_IN_RUNTIME",
    "PIE_TESTED",
    "DEVICE_TESTED",
    "VISUALLY_ACCEPTED",
    "GATE_6_ACCEPTED",
    "GATE_7_ACCEPTED",
    "P1C01_COMPLETE",
}


def load_manifest(path: Path = MANIFEST_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require_ids(label: str, expected: set[str], rows: list[dict]) -> None:
    actual = {row.get("id") for row in rows}
    missing = sorted(expected - actual)
    if missing:
        raise SystemExit(f"{label}_MISSING: {', '.join(missing)}")


def validate_manifest(manifest: dict) -> None:
    if manifest.get("status") != "ACTIVE_SOURCE_ONLY_PRODUCTION_READY":
        raise SystemExit("P1C01_ASSET_MANIFEST_STATUS_INVALID")

    require_ids("STATIC_BATCH", REQUIRED_STATIC_BATCHES, manifest.get("static_world_asset_batches", []))
    require_ids("CHARACTER_BATCH", REQUIRED_CHARACTER_BATCHES, manifest.get("character_factory_batches", []))
    require_ids("MATERIAL_BATCH", REQUIRED_MATERIAL_BATCHES, manifest.get("material_application_batches", []))

    for row in manifest.get("static_world_asset_batches", []):
        checks = set(row.get("qc_checks", []))
        if not REQUIRED_STATIC_QC.issubset(checks):
            raise SystemExit(f"STATIC_BATCH_QC_INCOMPLETE: {row.get('id')}")

    blender_checks = set(manifest.get("blender_qc_pipeline", {}).get("static_mesh_checks", []))
    missing_blender = sorted(REQUIRED_BLENDER_STATIC_CHECKS - blender_checks)
    if missing_blender:
        raise SystemExit(f"BLENDER_STATIC_QC_MISSING: {', '.join(missing_blender)}")

    regions = manifest.get("whole_game_seed_material_families", [])
    if len(regions) < 28:
        raise SystemExit(f"WHOLE_GAME_REGION_SEED_COUNT_TOO_LOW: {len(regions)}")

    boundary = set(manifest.get("evidence_boundary", {}).get("not_claimed_until_runner_evidence", []))
    missing_boundary = sorted(FORBIDDEN_RUNTIME_CLAIMS - boundary)
    if missing_boundary:
        raise SystemExit(f"EVIDENCE_BOUNDARY_MISSING: {', '.join(missing_boundary)}")


def main() -> int:
    validate_manifest(load_manifest())
    print("P1C01_CLOUD_ASSET_PRODUCTION_MANIFESTS_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
