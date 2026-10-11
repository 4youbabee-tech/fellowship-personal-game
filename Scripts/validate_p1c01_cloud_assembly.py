#!/usr/bin/env python3
"""Validate the cloud-safe P1C01 Shire assembly plan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_AREAS = {
    "BAG_END_EXTERIOR",
    "BAG_END_INTERIOR",
    "HOBBITON_CORE",
    "BAGSHOT_ROW",
    "PARTY_FIELD",
    "SHIRE_ROADS",
    "WATER_MILL_BRIDGE",
    "GARDENS_ORCHARDS",
    "AMBIENT_NATURE",
}

REQUIRED_CHARACTERS = {
    "PLAYER_FRODO",
    "NPC_BILBO",
    "NPC_GANDALF",
    "NPC_SAM",
    "NPC_MERRY",
    "NPC_PIPPIN",
}

REQUIRED_ACTIVITIES = {"ACT_F1_01", "ACT_F1_02", "ACT_F1_03", "ACT_F1_04"}


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate(plan: dict) -> list[str]:
    errors: list[str] = []

    if plan.get("chapter") != "P1C01":
        errors.append("P1C01_PLAN_CHAPTER_MISMATCH")
    if plan.get("status") != "CLOUD_READY_SELF_HOSTED_IMPORT_PENDING":
        errors.append("P1C01_PLAN_STATUS_NOT_CLOUD_READY")

    covered_areas = set(plan.get("required_scene_coverage", []))
    for batch in plan.get("scene_assembly_batches", []):
        covered_areas.update(batch.get("areas", []))
        if batch.get("runner_gate") != "SELF_HOSTED_IMPORT_REQUIRED":
            errors.append(f"BATCH_RUNNER_GATE_INVALID:{batch.get('id')}")
        if not batch.get("asset_families"):
            errors.append(f"BATCH_ASSET_FAMILIES_EMPTY:{batch.get('id')}")
        if not batch.get("materials_from_wave"):
            errors.append(f"BATCH_MATERIALS_EMPTY:{batch.get('id')}")

    missing_areas = sorted(REQUIRED_AREAS - covered_areas)
    if missing_areas:
        errors.append("MISSING_SCENE_AREAS:" + ",".join(missing_areas))

    characters = {entry.get("id") for entry in plan.get("character_roster", [])}
    missing_characters = sorted(REQUIRED_CHARACTERS - characters)
    if missing_characters:
        errors.append("MISSING_CHARACTERS:" + ",".join(missing_characters))

    activities = set()
    for batch in plan.get("scene_assembly_batches", []):
        activities.update(batch.get("activities", []))
    missing_activities = sorted(REQUIRED_ACTIVITIES - activities)
    if missing_activities:
        errors.append("MISSING_ACTIVITIES:" + ",".join(missing_activities))

    if len(plan.get("living_shire_director_inputs", [])) < 3:
        errors.append("LIVING_SHIRE_INPUTS_TOO_FEW")

    boundary = plan.get("evidence_boundary", "").lower()
    overclaim_phrases = (
        "pie accepted",
        "is packaged",
        "gate 6/7 accepted",
        "device accepted",
        "target hardware accepted",
    )
    for forbidden_claim in overclaim_phrases:
        if forbidden_claim in boundary:
            errors.append("EVIDENCE_BOUNDARY_OVERCLAIMS:" + forbidden_claim)

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plan",
        default="Data/P1C01CloudShireAssemblyPlanV1.json",
        help="Path to the P1C01 cloud assembly plan JSON.",
    )
    args = parser.parse_args(argv)

    errors = validate(_load_json(Path(args.plan)))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("P1C01_CLOUD_SHIRE_ASSEMBLY_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
