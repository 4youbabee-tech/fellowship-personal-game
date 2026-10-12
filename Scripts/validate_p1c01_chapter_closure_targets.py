#!/usr/bin/env python3
"""Validate the P1C01 chapter closure production target matrix."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET_PATH = ROOT / "Data" / "P1C01ChapterClosureProductionTargetsV1.json"
VISIBLE_PATH = ROOT / "Data" / "P1C01VisibleShireMegaPassV1.json"

REQUIRED_SHIRE_AREAS = {
    "Bag End exterior",
    "Bag End approved interiors",
    "Hobbiton",
    "Bagshot Row",
    "Party Field",
    "Bywater-facing edge",
}

REQUIRED_CHARACTERS = ["Frodo", "Bilbo", "Gandalf", "Sam", "Merry", "Pippin"]

FORBIDDEN_CLAIMS = {
    "UE Imported",
    "COMPILE-TESTED",
    "PIE-TESTED",
    "DEVICE-TESTED",
    "VISUALLY-ACCEPTED",
    "P1C01 Gate 6/7 accepted",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def validate_targets(target: dict, visible: dict) -> None:
    require(target.get("runtime_chapter") == "P1C01", "P1C01_TARGET_CHAPTER_INVALID")
    require(
        target.get("status") == "SOURCE_TARGETS_LOCKED_RUNTIME_IMPORT_PENDING",
        "P1C01_TARGET_STATUS_INVALID",
    )
    require(
        target.get("next_chapter_source_preparation", {}).get("runtime_activation_rule")
        == "Do not activate P1C02 runtime before P1C01 Gate 6/7 acceptance.",
        "NEXT_CHAPTER_RUNTIME_GATE_NOT_ENFORCED",
    )

    closure = target["p1c01_closure_targets"]
    nature = closure["shire_nature"]
    require(nature["source_family_target"] >= 18, "NATURE_FAMILY_TARGET_TOO_LOW")
    require(nature["derived_fbx_lod_target"] >= nature["source_family_target"] * 3, "NATURE_LOD_TARGET_TOO_LOW")

    visible_lanes = visible["hism_lanes"]
    for lane, value in nature["runtime_instance_targets"].items():
        require(lane in visible_lanes, f"NATURE_RUNTIME_LANE_MISSING:{lane}")
        require(value == visible_lanes[lane]["planned_instances"], f"NATURE_RUNTIME_LANE_COUNT_MISMATCH:{lane}")

    architecture = closure["shire_architecture"]
    require(architecture["unique_modular_family_target"] >= 12, "ARCHITECTURE_FAMILY_TARGET_TOO_LOW")
    require(architecture["placed_home_or_facade_target"] >= 18, "PLACED_HOME_TARGET_TOO_LOW")
    missing_areas = sorted(REQUIRED_SHIRE_AREAS - set(architecture["required_areas"]))
    require(not missing_areas, "SHIRE_AREA_TARGETS_MISSING:" + ",".join(missing_areas))

    props = closure["shire_props_and_daily_life"]
    require(props["reusable_prop_family_target"] >= 80, "PROP_FAMILY_TARGET_TOO_LOW")

    characters = closure["main_characters"]
    require(characters["runtime_character_order"] == REQUIRED_CHARACTERS, "MAIN_CHARACTER_ORDER_INVALID")
    require(characters["final_character_target"] == 6, "MAIN_CHARACTER_TARGET_INVALID")
    require(characters["ambient_npc_target"] >= 18, "AMBIENT_NPC_TARGET_TOO_LOW")
    require("OBJ body parts are static production foundations only" in characters["not_final_evidence"], "CHARACTER_EVIDENCE_BOUNDARY_MISSING")

    mission = closure["p1c01_mission_audio_cinematic"]
    require(len(mission["audio_source_targets"]) >= 7, "AUDIO_TARGETS_TOO_LOW")
    require(len(mission["cinematic_targets"]) >= 5, "CINEMATIC_TARGETS_TOO_LOW")

    not_claimed = set(target["acceptance_boundary"]["not_claimed"])
    missing_claims = sorted(FORBIDDEN_CLAIMS - not_claimed)
    require(not missing_claims, "ACCEPTANCE_BOUNDARY_MISSING:" + ",".join(missing_claims))


def main() -> int:
    validate_targets(load_json(TARGET_PATH), load_json(VISIBLE_PATH))
    print("P1C01_CHAPTER_CLOSURE_TARGETS_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
