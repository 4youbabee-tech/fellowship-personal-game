#!/usr/bin/env python3
"""Fail-closed runnerless preflight for the P1C01 Graphics/Video settings lane."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOVERNOR = ROOT / "Data" / "ProjectGovernor.json"
LEDGER = ROOT / "Docs" / "WORLD_DETAIL_LEDGER.md"
SCALABILITY = ROOT / "Config" / "DefaultScalability.ini"
PREP = ROOT / "Data" / "P1C01GraphicsSettingsV11Preparation.json"

REQ_ID = "REQ-PERF-004"
DEC_ID = "DEC-079"
LEDGER_MARKER = "P1C01 Graphics/Video Visual-Economy Doctrine V2"
RUNTIME_FILES = (
    ROOT / "Source" / "ShireJourney" / "Public" / "Settings" / "ShireGameUserSettings.h",
    ROOT / "Source" / "ShireJourney" / "Private" / "Settings" / "ShireGameUserSettings.cpp",
)

REQUIRED_SCALABILITY_ANCHORS = (
    "r.Streaming.PoolSize=600",
    "r.Streaming.PoolSize=800",
    "r.Streaming.PoolSize=1000",
    "r.Shadow.MaxResolution=512",
    "r.Shadow.MaxResolution=768",
    "r.Shadow.MaxResolution=1024",
    "r.Shadow.CSM.MaxCascades=1",
    "r.Shadow.CSM.MaxCascades=2",
    "r.Shadow.DistanceScale=0.45",
    "r.Shadow.DistanceScale=0.65",
    "r.Shadow.DistanceScale=0.80",
    "r.ViewDistanceScale=0.45",
    "r.ViewDistanceScale=0.65",
    "r.ViewDistanceScale=0.80",
    "foliage.DensityScale=0.70",
    "grass.DensityScale=0.70",
)


def fail(message: str) -> None:
    raise SystemExit(f"P1C01_GRAPHICS_SETTINGS_V11_PREFLIGHT_FAIL {message}")


def main() -> None:
    governor = json.loads(GOVERNOR.read_text(encoding="utf-8"))
    ledger = LEDGER.read_text(encoding="utf-8")
    scalability = SCALABILITY.read_text(encoding="utf-8")
    prep = json.loads(PREP.read_text(encoding="utf-8"))

    if LEDGER_MARKER not in ledger:
        fail("missing_ledger_registration")

    req = next((item for item in governor.get("requirements", []) if item.get("id") == REQ_ID), None)
    dec = next((item for item in governor.get("decisions", []) if item.get("id") == DEC_ID), None)

    if (req is None) != (dec is None):
        fail("partial_governance_registration")

    if req is not None:
        if "Graphics/Video" not in req.get("title", ""):
            fail("requirement_id_reused")
        if REQ_ID not in dec.get("requirements", []):
            fail("decision_missing_requirement_link")

    runtime_present = [str(path.relative_to(ROOT)) for path in RUNTIME_FILES if path.exists()]
    if runtime_present and (req is None or dec is None):
        fail("runtime_source_before_governor_authority:" + ",".join(runtime_present))

    for anchor in REQUIRED_SCALABILITY_ANCHORS:
        if anchor not in scalability:
            fail("lower_tier_anchor_changed:" + anchor)

    if prep.get("scope") != "W01_P1C01_PRODUCTION_VERTICAL_SLICE":
        fail("prep_scope_drift")
    if prep.get("runtime_scope") != "P1C01_ONLY":
        fail("runtime_scope_drift")
    preflight = prep.get("governor_preflight", {})
    if preflight.get("planned_requirement_id") != REQ_ID:
        fail("prep_requirement_id_drift")
    if preflight.get("planned_decision_id") != DEC_ID:
        fail("prep_decision_id_drift")

    state = "GOVERNOR_ACCEPTED" if req is not None else "GOVERNOR_PENDING"
    runtime = "PRESENT" if runtime_present else "UNOPENED"
    print(
        "P1C01_GRAPHICS_SETTINGS_V11_PREFLIGHT_PASS "
        f"governance={state} runtime={runtime} anchors={len(REQUIRED_SCALABILITY_ANCHORS)}"
    )


if __name__ == "__main__":
    main()
