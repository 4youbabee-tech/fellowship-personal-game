#!/usr/bin/env python3
"""Mandatory fail-closed Project Governor entrypoint for P1C01 production workers.

This is authorization-only. It cannot dispatch work or grant acceptance labels.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PRODUCERS = {
    "RUNTIME_BUILD": ".github/workflows/unreal-build-validation.yml",
    "WAREHOUSE_ASSET_INTAKE": ".github/workflows/p1c01-two-wave-checkpoint-warehouse.yml",
    "SKELETAL_CHARACTER_PREP": ".github/workflows/p1c01-human-wave2.yml",
    "VISUAL_WORLD_PREP": ".github/workflows/p1c01-adaptive-highfidelity-source.yml",
    "GAMEPLAY_PRESENTATION_PREP": ".github/workflows/p1c01-chapter-closure.yml",
}

class ManagerRejected(ValueError):
    pass

def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ManagerRejected(reason)

def validate_contract(governor: dict, mode: dict, lane: str, root: Path) -> dict:
    require(lane in PRODUCERS, "UNKNOWN_LANE")
    require(governor.get("authority_id") == "FELLOWSHIP_SINGLE_PROJECT_GOVERNOR_V2",
            "AUTHORITY_CHANGED")
    require("sole authoritative project-management decision source" in
            governor.get("authority_rule", ""), "SINGLE_MANAGER_DISABLED")
    decisions = {d["id"]: d for d in governor.get("decisions", [])}
    for decision in ("DEC-078", "DEC-104", "DEC-105"):
        require(decisions.get(decision, {}).get("status") == "ACCEPTED",
                "FIVE_LANE_DECISION_MISSING:" + decision)
    reqs = {r["id"]: r for r in governor.get("requirements", [])}
    require(reqs.get("REQ-PROD-011", {}).get("priority") == "CRITICAL",
            "MAX_SAFE_REQUIREMENT_MISSING")
    active = governor.get("active_gate", {})
    require(active.get("id") == "W01_P1C01_VERTICAL_SLICE_GATE", "ACTIVE_GATE_CHANGED")
    focus = governor.get("current_focus", {}).get("production_lane")
    control = governor.get("execution_control", {})
    require(focus == "W01_P1C01_PRODUCTION_VERTICAL_SLICE" and
            focus == control.get("active_lane") == governor.get("development_mode", {}).get("id"),
            "ACTIVE_LANE_CHANGED")
    require(control.get("mode") == "ACTIVE_GATE_FIRST", "GATE_CONTROL_DISABLED")
    require(governor.get("governor_role", {}).get("mode") == "OVERSEER_NOT_BOTTLENECK",
            "MANAGER_ROLE_CHANGED")
    require(governor.get("branch_workflow", {}).get("integration_branch") == "develop",
            "INTEGRATION_BRANCH_CHANGED")
    if lane == "RUNTIME_BUILD":
        require(active.get("blocks_major_feature_expansion") is not True,
                "RUNTIME_BLOCKED_BY_ACTIVE_GATE")
    overlay = mode.get("five_lane_operating_overlay", {})
    tracks = overlay.get("tracks", [])
    require(overlay.get("policy") == "DEC-104" and overlay.get("track_count") == 5,
            "FIVE_LANE_POLICY_DISABLED")
    require(len(tracks) == 5 and {t.get("id") for t in tracks} == set(PRODUCERS),
            "FIVE_LANE_TRACKS_CHANGED")
    require(sum(t.get("runtime_writer") is True for t in tracks) == 1 and
            mode.get("throughput_model", {}).get("runtime_lane_count") == 1,
            "RUNTIME_WRITER_COUNT_UNSAFE")
    require(sum(t.get("persistent_writer") is True for t in tracks) == 1 and
            mode.get("throughput_model", {}).get("persistent_warehouse_writer_count") == 1,
            "WAREHOUSE_WRITER_COUNT_UNSAFE")
    require(overlay.get("persistent_free_space_reserve_gib", 0) >= 6,
            "WAREHOUSE_DISK_RESERVE_UNSAFE")
    require(mode.get("governor_work_start") == "Scripts/governor_work_start.py" and
            overlay.get("governor_work_start") == "Scripts/governor_work_start.py",
            "WORK_START_REGISTRATION_MISSING")
    for relative in PRODUCERS.values():
        require((root / relative).is_file(), "PRODUCER_WORKFLOW_MISSING:" + relative)
    return {"lane": lane, "gate": active["id"], "runtime_writers": 1,
            "warehouse_writers": 1, "proof": "AUTHORIZATION_ONLY_NOT_PIE_DEVICE_VISUAL"}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", choices=tuple(PRODUCERS), required=True)
    args = parser.parse_args()
    try:
        governor = json.loads((ROOT / "Data/ProjectGovernor.json").read_text(encoding="utf-8"))
        mode = json.loads((ROOT / "Data/MaximumSafeProductionModeV1.json").read_text(encoding="utf-8"))
        result = validate_contract(governor, mode, args.lane, ROOT)
        full = subprocess.run(
            [sys.executable, str(ROOT / "Scripts/project_governor.py")],
            cwd=ROOT, capture_output=True, text=True, timeout=100, check=False
        )
        if full.returncode != 0 or "PROJECT GOVERNOR PASSED" not in full.stdout:
            raise ManagerRejected("FULL_MANAGER_FAILED: " + (full.stdout + full.stderr)[-6500:])
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print("GOVERNOR_WORK_START_BLOCKED lane=" + args.lane + " " + str(exc), file=sys.stderr)
        return 2
    print("PROJECT GOVERNOR PASSED")
    print("GOVERNOR_WORK_START_PASS " + " ".join(str(k) + "=" + str(v) for k, v in result.items()))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
