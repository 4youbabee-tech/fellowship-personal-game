#!/usr/bin/env python3
"""Five parallel source/read-only production preflight lanes.

Never accesses network, Git LFS, UE4, or the persistent warehouse. All eligible
candidate rows are inspected in bounded memory; output is a truth-labelled JSON
report of concrete work available to the independent workers.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANES = (
    "RUNTIME_BUILD",
    "WAREHOUSE_ASSET_INTAKE",
    "SKELETAL_CHARACTER_PREP",
    "VISUAL_WORLD_PREP",
    "GAMEPLAY_PRESENTATION_PREP",
)
INPUTS = {
    "RUNTIME_BUILD": ("Data/MaximumSafeProductionModeV1.json",),
    "WAREHOUSE_ASSET_INTAKE": ("Data/GlobalWarehouseSourceRegistryV2.json",
                                "Data/TrilogyAssetCandidateQueue.json", "Data/WarehouseSaturationTrainV1.json"),
    "SKELETAL_CHARACTER_PREP": ("Data/CharacterProductionMatrix.json", "Data/P1C01HeroSkeletalCandidateWaveV1.json"),
    "VISUAL_WORLD_PREP": ("Data/P1C01VisualProductionMegaWaveV2.json",
                           "Data/P1C01VisibleWorldProxyReplacementV1.json"),
    "GAMEPLAY_PRESENTATION_PREP": ("Data/LivingWorldFeaturePlan.json", "Data/P1C01MegaChapterPackV1.json"),
}


class LaneError(ValueError):
    pass


def source(path: str, root: Path) -> dict:
    file = root / path
    doc = json.loads(file.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise LaneError("INVALID_SOURCE_DOCUMENT:" + path)
    return doc


def _assert(ok: bool, message: str) -> None:
    if not ok:
        raise LaneError(message)


def evaluate(lane: str, root: Path = ROOT) -> dict:
    if lane not in LANES:
        raise LaneError("UNKNOWN_LANE:" + lane)
    governor = source("Data/ProjectGovernor.json", root)
    decisions = {x["id"]: x for x in governor["decisions"]}
    requirements = {x["id"]: x for x in governor["requirements"]}
    _assert(decisions.get("DEC-078", {}).get("status") == "ACCEPTED", "MAX_SAFE_AUTHORITY_MISSING")
    _assert(decisions.get("DEC-104", {}).get("status") == "ACCEPTED", "FIVE_LANE_AUTHORITY_MISSING")
    _assert(requirements.get("REQ-PROD-011", {}).get("priority") == "CRITICAL", "PRODUCTION_REQ_MISSING")
    mode = source("Data/MaximumSafeProductionModeV1.json", root)
    overlay = mode.get("five_lane_operating_overlay", {})
    tracks = overlay.get("tracks", [])
    ids = [x.get("id") for x in tracks]
    _assert(len(tracks) == 5 and set(ids) == set(LANES), "FIVE_TRACK_CONTRACT_MISMATCH")
    _assert(sum(bool(x.get("persistent_writer")) for x in tracks) == 1, "WAREHOUSE_WRITER_NOT_SERIALIZED")
    _assert(sum(bool(x.get("runtime_writer")) for x in tracks) == 1, "RUNTIME_WRITER_NOT_SERIALIZED")
    _assert(overlay.get("persistent_free_space_reserve_gib", 0) >= 6, "WAREHOUSE_FREE_SPACE_RESERVE_TOO_LOW")
    _assert(mode.get("throughput_model", {}).get("runtime_lane_count") == 1, "RUNTIME_LANE_LIMIT_BROKEN")
    _assert(mode.get("throughput_model", {}).get("persistent_warehouse_writer_count") == 1, "WAREHOUSE_LANE_LIMIT_BROKEN")
    _assert(governor.get("active_gate", {}).get("id", "").find("P1C01") >= 0, "P1C01_ACTIVE_GATE_MISSING")

    details = {}
    if lane == "RUNTIME_BUILD":
        details = {
            "active_gate": governor["active_gate"]["id"],
            "integration_branch": governor.get("branch_workflow", {}).get("integration_branch"),
            "current_only_runtime_chapter": "P1C01",
            "work": "Continue existing serialized Unreal CI/PR #329; this hosted metadata preflight does NOT dispatch/build/package Unreal.",
            "new_unreal_run_requested": False,
        }
        _assert(details["integration_branch"] == "develop", "INTEGRATION_BRANCH_CHANGED")
    elif lane == "WAREHOUSE_ASSET_INTAKE":
        registry = source(INPUTS[lane][0], root)
        queue = source(INPUTS[lane][1], root)
        saturation = source(INPUTS[lane][2], root)
        sources = registry.get("sources", [])
        candidates = queue.get("candidates", [])
        cars = saturation.get("cars", [])
        _assert(isinstance(sources, list) and len(sources) >= 100, "REGISTRY_INCOMPLETE")
        _assert(isinstance(candidates, list) and len(candidates) >= 20, "CANDIDATE_QUEUE_INCOMPLETE")
        _assert(isinstance(cars, list) and len(cars) >= 15, "SATURATION_CARS_INCOMPLETE")
        # Review the entire current queue, without a fixed count-based reduction.
        rows = []
        for item in candidates:
            name = item.get("id")
            _assert(isinstance(name, str) and name, "SOURCE_CANDIDATE_MISSING_ID")
            rows.append({
                "id": name, "provider": item.get("provider"),
                "source_page": item.get("source_page"),
                "license_observed": item.get("license_observed"),
                "status": "CATALOGUED_CANDIDATE_NOT_DOWNLOADED_BY_THIS_LANE",
                "next_action": "Reconcile with active receipts and provider entitlement, then existing serialized warehouse/source intake."
            })
        details = {"registry_entries_reviewed": len(sources),
                   "source_candidates_reviewed": len(rows),
                   "saturation_cars_reviewed": len(cars),
                   "candidate_rows": rows,
                   "warehouse_mutated": False,
                   "downloaded_file_count_this_lane": 0,
                   "max_safe_rule": "Select all eligible candidates, shard by measured file sizes/verified source, provider budget, runner time and disk reserve; no arbitrary fixed five-file goal."}
    elif lane == "SKELETAL_CHARACTER_PREP":
        m = source(INPUTS[lane][0], root)
        wave = source(INPUTS[lane][1], root)
        chars = m.get("characters", [])
        _assert(len(chars) >= 15, "CHARACTER_MATRIX_MISSING")
        _assert(wave.get("runtime_scope") == "P1C01_ONLY", "RIG_WAVE_SCOPE_CHANGED")
        details = {
            "named_characters_reviewed": len(chars),
            "priority_shire": [item["id"] for item in chars if item.get("id") in
                               ("FRODO", "GANDALF", "BILBO", "SAM", "MERRY", "PIPPIN")],
            "character_status_counts": dict(Counter(x.get("status", "UNKNOWN") for x in chars)),
            "source_only": True,
            "block_known_bad_kaykit_payloads": True,
            "animation_final_format": "Skeletal FBX",
            "missing_runtime_proof": ["deformation", "UE4 skeletal import", "human visual acceptance"],
        }
    elif lane == "VISUAL_WORLD_PREP":
        wave = source(INPUTS[lane][0], root)
        visible = source(INPUTS[lane][1], root)
        slots = wave.get("slots", [])
        cells = visible.get("replacement_cells", [])
        _assert(len(slots) == wave.get("total_slots") and len(slots) >= 150, "WORLD_SLOTS_INCOMPLETE")
        required = {"BAG_END_HERO_RING", "HOBBITON_VILLAGE", "SHIRE_ROAD_CORRIDOR", "BUCKLEBURY_FERRY"}
        _assert(required <= {c.get("cell") for c in cells}, "SHIRE_VISIBLE_CELL_MISSING")
        _assert(visible.get("runtime_integration_allowed") is False, "WORLD_PREP_CANNOT_PROMOTE_RUNTIME")
        details = {
            "all_visual_slots_reviewed": len(slots),
            "slot_families": dict(Counter(x.get("family", "UNKNOWN") for x in slots)),
            "priority_cells": sorted(required),
            "candidate_slot_ids": [x.get("id") for x in slots],
            "next": "Map existing legal assets to P1C01 silhouettes/materials; UE import, LOD/collision and appearance remain separate.",
            "new_ue_import_count": 0,
        }
    else:
        living = source(INPUTS[lane][0], root)
        pack = source(INPUTS[lane][1], root)
        phases = living.get("phases", [])
        _assert(len(phases) >= 5, "LIVING_WORLD_PHASES_MISSING")
        features = [f for p in phases for f in p.get("features", [])]
        details = {
            "living_world_phases_reviewed": len(phases),
            "npc_features_reviewed": len(features),
            "npc_feature_status_counts": dict(Counter(f.get("status", "UNKNOWN") for f in features)),
            "chapter_pack_cars": len(pack.get("cars", [])),
            "requires": ["NPC pooling", "quest/save disk roundtrip", "English voice / Arabic UI & subtitles",
                         "audio integration", "pacing and performance on target laptop"],
            "source_and_contract_only": True,
        }
    return {
        "schema_version": 1,
        "lane": lane,
        "result": "SOURCE_READ_ONLY_PREFLIGHT_PASS",
        "truth_state": "STATIC_METADATA_ONLY",
        "governor_decision": "DEC-104",
        "source_inputs": list(INPUTS[lane]) + ["Data/ProjectGovernor.json"],
        "persistent_warehouse_changed": False,
        "unreal_runtime_changed": False,
        "evidence_boundary": "Candidate/source metadata and existing manifests only; no asset download, persistent warehouse mutation, Unreal execution, PIE/device FPS or human visual acceptance.",
        "detail": details,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lane", choices=LANES, required=True)
    ap.add_argument("--output", type=Path, required=True)
    opts = ap.parse_args()
    report = evaluate(opts.lane)
    opts.output.parent.mkdir(parents=True, exist_ok=True)
    opts.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("P1C01_FIVE_LANE_PREFLIGHT_PASS lane=" + opts.lane +
          " scope=ALL_ELIGIBLE_METADATA never_claim_unreal_or_download=yes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
