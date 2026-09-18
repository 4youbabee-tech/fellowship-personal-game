#!/usr/bin/env python3
"""Validate the single authoritative project governor.

Data/ProjectGovernor.json is the only project-management decision authority.
This validator checks its internal coherence. It does not replace UE4.27
compile, PIE, target-device testing, or human pacing/visual review.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOVERNOR_PATH = ROOT / "Data" / "ProjectGovernor.json"

errors: list[str] = []

def fail(message: str) -> None:
    errors.append(message)

try:
    governor = json.loads(GOVERNOR_PATH.read_text(encoding="utf-8"))
except Exception as exc:
    print(f"PROJECT GOVERNOR FAILED: cannot parse Data/ProjectGovernor.json: {exc}")
    sys.exit(1)

if governor.get("authority_id") != "FELLOWSHIP_SINGLE_PROJECT_GOVERNOR_V2":
    fail("Unexpected or missing single-governor authority_id")

if "sole authoritative project-management decision source" not in str(governor.get("authority_rule", "")):
    fail("Governor must explicitly declare sole decision authority")

reqs = governor.get("requirements", [])
req_ids: set[str] = set()
allowed_status = set(governor.get("requirement_status_values", []))
allowed_priority = set(governor.get("priority_values", []))

for index, item in enumerate(reqs, start=1):
    req_id = str(item.get("id") or "").strip()
    if not req_id:
        fail(f"Requirement entry {index} has no id")
        continue
    if req_id in req_ids:
        fail(f"Duplicate requirement id: {req_id}")
    req_ids.add(req_id)
    if str(item.get("status") or "") not in allowed_status:
        fail(f"{req_id} has invalid status '{item.get('status')}'")
    if str(item.get("priority") or "") not in allowed_priority:
        fail(f"{req_id} has invalid priority '{item.get('priority')}'")
    if not str(item.get("intent") or "").strip():
        fail(f"{req_id} has no intent")
    if not item.get("acceptance_criteria"):
        fail(f"{req_id} has no acceptance criteria")

for item in reqs:
    req_id = str(item.get("id") or "").strip()
    for dep in item.get("dependencies", []):
        if dep not in req_ids:
            fail(f"{req_id} depends on unknown requirement {dep}")
    for other in item.get("conflicts_with", []):
        if other not in req_ids:
            fail(f"{req_id} conflicts with unknown requirement {other}")

for required in [
    "REQ-MEM-001", "REQ-GOV-001", "REQ-VISION-001", "REQ-EXP-001",
    "REQ-WORLD-001", "REQ-WORLD-002", "REQ-NPC-001", "REQ-NPC-002",
    "REQ-NPC-003", "REQ-SAVE-001", "REQ-PERF-001",
    "REQ-QUALITY-001", "REQ-QUALITY-002", "REQ-CI-001", "REQ-CHAR-001"
]:
    if required not in req_ids:
        fail(f"Governor is missing critical requirement {required}")

invariants = governor.get("hard_invariants", [])
invariant_ids = [str(item.get("id") or "").strip() for item in invariants]
if len(invariant_ids) != len(set(invariant_ids)):
    fail("Duplicate hard invariant id")
for required in [
    "INV-MEMORY", "INV-STORY", "INV-INTEGRITY",
    "INV-TRAVERSAL", "INV-PERFORMANCE", "INV-PROOF"
]:
    if required not in invariant_ids:
        fail(f"Governor missing hard invariant {required}")

decision_ids: set[str] = set()
covered_pairs: set[tuple[str, str]] = set()
allowed_decision_status = set(governor.get("decision_status_values", []))
for item in governor.get("decisions", []):
    decision_id = str(item.get("id") or "").strip()
    refs = [str(value).strip() for value in item.get("requirements", []) if str(value).strip()]
    if not decision_id:
        fail("Decision without id")
        continue
    if decision_id in decision_ids:
        fail(f"Duplicate decision id: {decision_id}")
    decision_ids.add(decision_id)
    if str(item.get("status") or "") not in allowed_decision_status:
        fail(f"{decision_id} has invalid decision status")
    for ref in refs:
        if ref not in req_ids:
            fail(f"{decision_id} references unknown requirement {ref}")
    for i, left in enumerate(refs):
        for right in refs[i + 1:]:
            covered_pairs.add(tuple(sorted((left, right))))

open_conflicts = governor.get("open_conflicts", [])
open_pairs: set[tuple[str, str]] = set()
for item in open_conflicts:
    conflict_id = str(item.get("id") or "").strip()
    refs = [str(value).strip() for value in item.get("requirements", []) if str(value).strip()]
    if not conflict_id or len(refs) < 2:
        fail("Open conflict must have an id and at least two requirements")
    for ref in refs:
        if ref not in req_ids:
            fail(f"Open conflict {conflict_id} references unknown requirement {ref}")
    for i, left in enumerate(refs):
        for right in refs[i + 1:]:
            open_pairs.add(tuple(sorted((left, right))))

for item in reqs:
    req_id = str(item.get("id") or "").strip()
    for other in item.get("conflicts_with", []):
        pair = tuple(sorted((req_id, other)))
        if pair not in covered_pairs and pair not in open_pairs:
            fail(f"Declared conflict {req_id} <-> {other} has no decision/open conflict")

required_gates = set(governor.get("required_quality_gate_ids", []))
allowed_gate_status = set(governor.get("quality_gate_status_values", []))
regions = governor.get("region_quality", [])
region_ids: set[str] = set()

for region in regions:
    region_id = str(region.get("id") or "").strip()
    if not region_id:
        fail("Region quality entry without id")
        continue
    if region_id in region_ids:
        fail(f"Duplicate region quality id: {region_id}")
    region_ids.add(region_id)
    gates = region.get("gates", {})
    missing = sorted(required_gates - set(gates))
    if missing:
        fail(f"{region_id} missing gates: {', '.join(missing)}")
    for gate_id, status in gates.items():
        if gate_id not in required_gates:
            fail(f"{region_id} has unknown gate {gate_id}")
        if status not in allowed_gate_status:
            fail(f"{region_id}/{gate_id} has invalid status {status}")

for required_region in governor.get("required_regions", []):
    if required_region not in region_ids:
        fail(f"Governor missing required region quality map {required_region}")

active_gate = governor.get("active_gate", {})
if not str(active_gate.get("id") or "").strip():
    fail("Governor has no active_gate id")
if not active_gate.get("required_evidence"):
    fail("Governor active_gate has no required evidence")

if not governor.get("update_protocol"):
    fail("Governor has no update protocol")

for relative in governor.get("deprecated_secondary_authority_files", []):
    if (ROOT / relative).exists():
        fail(f"Deprecated secondary authority file must not exist: {relative}")

if not governor.get("worker_contract"):
    fail("Governor has no worker_contract")

# Player-experience pacing contract is required, but human review remains the authority for PACING.
PACING_PATH = ROOT / "Data" / "PlayerExperiencePacingPlan.json"
try:
    pacing = json.loads(PACING_PATH.read_text(encoding="utf-8"))
except Exception as exc:
    fail(f"Cannot parse Data/PlayerExperiencePacingPlan.json: {exc}")
    pacing = {}

pacing_chapters = {str(item.get("chapter") or "").strip() for item in pacing.get("chapter_reviews", [])}
required_pacing = {"P1C01","P1C02","P1C03","P1C04","P1C05","P1C06","P1C07","P1C08","P1G01"}
missing_pacing = sorted(required_pacing - pacing_chapters)
if missing_pacing:
    fail("Pacing plan missing chapters/routes: " + ", ".join(missing_pacing))

print(
    f"Single Project Governor checked {len(req_ids)} requirements, "
    f"{len(decision_ids)} decisions, {len(open_conflicts)} open conflicts, "
    f"{len(region_ids)} region quality maps."
)
for message in errors:
    print(f"ERROR: {message}")

if errors:
    print(f"PROJECT GOVERNOR FAILED: {len(errors)} error(s)")
    sys.exit(1)

print("PROJECT GOVERNOR PASSED")

# Work-start reminder: surface unfinished high-priority commitments every validation run.
open_statuses = {"REQUESTED", "PLANNED", "PARTIAL", "DEFERRED"}
reminders = [
    item for item in reqs
    if str(item.get("status") or "") in open_statuses
    and str(item.get("priority") or "") in {"CRITICAL", "HIGH"}
]
priority_rank = {"CRITICAL": 0, "HIGH": 1}
reminders.sort(key=lambda item: (priority_rank.get(str(item.get("priority") or ""), 9), str(item.get("id") or "")))

print("PROJECT GOVERNOR WORK REMINDER")
print(
    f"Active gate: {active_gate.get('id', 'UNKNOWN')} | "
    f"status={active_gate.get('status', 'UNKNOWN')} | "
    f"blocks_major_feature_expansion={active_gate.get('blocks_major_feature_expansion', False)}"
)
for item in reminders:
    missing = item.get("missing_work", [])
    next_item = str(missing[0]) if missing else "Review acceptance criteria/evidence."
    print(
        f"REMINDER [{item.get('priority')}] {item.get('id')} "
        f"{item.get('title')} | status={item.get('status')} | next={next_item}"
    )
