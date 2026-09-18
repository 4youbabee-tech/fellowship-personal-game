#!/usr/bin/env python3
"""Deterministic project-governor validation.

This program validates the structured memory/control layer. It does not replace
UE4.27 compile, PIE, target-device testing, or human pacing/visual review.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Data"

errors: list[str] = []

def fail(message: str) -> None:
    errors.append(message)

def load_json(name: str) -> dict:
    path = DATA / name
    if not path.exists():
        fail(f"Missing governor data file: Data/{name}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"Cannot parse Data/{name}: {exc}")
        return {}

requirements = load_json("ProjectRequirements.json")
policy = load_json("ProjectGovernorPolicy.json")
decisions = load_json("ProjectDecisions.json")
quality = load_json("ExperienceQualityGates.json")

reqs = requirements.get("requirements", [])
req_ids = {str(item.get("id") or "").strip() for item in reqs if str(item.get("id") or "").strip()}

for item in reqs:
    req_id = str(item.get("id") or "").strip()
    for dep in item.get("dependencies", []):
        if dep not in req_ids:
            fail(f"{req_id} depends on unknown requirement {dep}")
    for conflict in item.get("conflicts_with", []):
        if conflict not in req_ids:
            fail(f"{req_id} conflicts_with unknown requirement {conflict}")

hard_invariants = policy.get("hard_invariants", [])
invariant_ids = [str(item.get("id") or "").strip() for item in hard_invariants]
if len(invariant_ids) != len(set(invariant_ids)):
    fail("ProjectGovernorPolicy has duplicate hard invariant IDs")
for required in ["INV-MEMORY", "INV-STORY", "INV-INTEGRITY", "INV-TRAVERSAL", "INV-PERFORMANCE", "INV-PROOF"]:
    if required not in invariant_ids:
        fail(f"ProjectGovernorPolicy missing hard invariant {required}")

decision_ids: set[str] = set()
covered_pairs: set[tuple[str, str]] = set()
for item in decisions.get("decisions", []):
    decision_id = str(item.get("id") or "").strip()
    status = str(item.get("status") or "").strip()
    refs = [str(value).strip() for value in item.get("requirements", []) if str(value).strip()]
    if not decision_id:
        fail("ProjectDecisions contains decision without id")
        continue
    if decision_id in decision_ids:
        fail(f"Duplicate project decision id: {decision_id}")
    decision_ids.add(decision_id)
    if status not in set(policy.get("decision_status_values", [])):
        fail(f"Decision {decision_id} uses unknown status '{status}'")
    if status == "ACCEPTED":
        if not str(item.get("resolution") or "").strip():
            fail(f"Accepted decision {decision_id} has no resolution")
        if not str(item.get("rationale") or "").strip():
            fail(f"Accepted decision {decision_id} has no rationale")
    for ref in refs:
        if ref not in req_ids:
            fail(f"Decision {decision_id} references unknown requirement {ref}")
    for i, left in enumerate(refs):
        for right in refs[i + 1:]:
            covered_pairs.add(tuple(sorted((left, right))))

open_conflicts = decisions.get("open_conflicts", [])
for item in open_conflicts:
    conflict_id = str(item.get("id") or "").strip()
    refs = [str(value).strip() for value in item.get("requirements", []) if str(value).strip()]
    if not conflict_id or len(refs) < 2:
        fail("Open conflict must have id and at least two requirement references")
    for ref in refs:
        if ref not in req_ids:
            fail(f"Open conflict {conflict_id} references unknown requirement {ref}")

# If requirements explicitly declare a conflict, it must be either open or covered by a recorded decision.
open_pairs: set[tuple[str, str]] = set()
for item in open_conflicts:
    refs = [str(value).strip() for value in item.get("requirements", []) if str(value).strip()]
    for i, left in enumerate(refs):
        for right in refs[i + 1:]:
            open_pairs.add(tuple(sorted((left, right))))

for item in reqs:
    req_id = str(item.get("id") or "").strip()
    for other in item.get("conflicts_with", []):
        pair = tuple(sorted((req_id, other)))
        if pair not in covered_pairs and pair not in open_pairs:
            fail(f"Declared conflict {req_id} <-> {other} has no decision/open-conflict record")

required_gate_ids = set(policy.get("required_quality_gate_ids", []))
allowed_gate_statuses = set(policy.get("quality_gate_status_values", []))
regions = quality.get("regions", [])
region_ids: set[str] = set()
for region in regions:
    region_id = str(region.get("id") or "").strip()
    if not region_id:
        fail("ExperienceQualityGates contains region without id")
        continue
    if region_id in region_ids:
        fail(f"Duplicate quality-gate region id: {region_id}")
    region_ids.add(region_id)
    gates = region.get("gates", {})
    missing = sorted(required_gate_ids - set(gates.keys()))
    if missing:
        fail(f"{region_id} missing quality gates: {', '.join(missing)}")
    for gate_id, status in gates.items():
        if gate_id not in required_gate_ids:
            fail(f"{region_id} has unknown quality gate {gate_id}")
        if status not in allowed_gate_statuses:
            fail(f"{region_id}/{gate_id} uses unknown status '{status}'")

for required_region in quality.get("required_regions", []):
    if required_region not in region_ids:
        fail(f"ExperienceQualityGates missing required region {required_region}")

print(
    f"Project Governor checked {len(req_ids)} requirements, "
    f"{len(decision_ids)} decisions, {len(open_conflicts)} open conflicts, "
    f"{len(region_ids)} region quality maps."
)
for message in errors:
    print(f"ERROR: {message}")

if errors:
    print(f"PROJECT GOVERNOR FAILED: {len(errors)} error(s)")
    sys.exit(1)

print("PROJECT GOVERNOR PASSED")
