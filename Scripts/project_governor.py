#!/usr/bin/env python3
"""Validate the single authoritative project governor.

Data/ProjectGovernor.json is the only project-management decision authority.
This validator checks its internal coherence. It does not replace UE4.27
compile, PIE, target-device testing, or human pacing/visual review.
"""

from __future__ import annotations

import json
import re
import sys
import subprocess
from pathlib import Path
from governor_handoff import validate_handoff, evidence_summary

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

# Formal requirement contract: keep accepted requests machine-checkable instead of
# relying on chat memory or a worker remembering field names.
SCHEMA_PATH = ROOT / "Data" / "ProjectGovernor.schema.json"
if not SCHEMA_PATH.exists():
    fail("Project Governor JSON schema is missing")
else:
    try:
        schema_doc = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"Cannot parse Data/ProjectGovernor.schema.json: {exc}")
        schema_doc = {}
    if schema_doc and schema_doc.get("title") != "Fellowship Project Governor":
        fail("Project Governor schema identity changed unexpectedly")

requirement_contract = governor.get("requirement_contract", {})
canonical_required_fields = [
    "id", "title", "category", "priority", "status", "origin",
    "intent", "acceptance_criteria", "dependencies",
]
if requirement_contract.get("schema_file") != "Data/ProjectGovernor.schema.json":
    fail("Governor requirement_contract must point to Data/ProjectGovernor.schema.json")
if requirement_contract.get("required_fields") != canonical_required_fields:
    fail("Governor requirement_contract required_fields changed or are out of order")
if requirement_contract.get("authoritative_intent_field") != "intent":
    fail("Governor requirement intent authority must remain the intent field")

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
    if not str(item.get("title") or "").strip():
        fail(f"{req_id} has no title")
    if not str(item.get("category") or "").strip():
        fail(f"{req_id} has no category")
    if not str(item.get("origin") or "").strip():
        fail(f"{req_id} has no origin")
    if not str(item.get("intent") or "").strip():
        fail(f"{req_id} has no intent")
    if not isinstance(item.get("acceptance_criteria"), list) or not item.get("acceptance_criteria"):
        fail(f"{req_id} has no acceptance criteria")
    if not isinstance(item.get("dependencies"), list):
        fail(f"{req_id} dependencies must be a list")

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
    "REQ-QUALITY-001", "REQ-QUALITY-002", "REQ-CI-001", "REQ-CHAR-001",
    "REQ-CHAR-002"
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
if active_gate.get("status") not in set(governor.get("quality_gate_status_values", [])):
    fail("Governor active_gate has invalid status")
if active_gate.get("status") == "FAILED" and active_gate.get("blocks_major_feature_expansion") is not True:
    fail("A failed active gate must quarantine major feature expansion")

if not governor.get("update_protocol"):
    fail("Governor has no update protocol")

for relative in governor.get("deprecated_secondary_authority_files", []):
    if (ROOT / relative).exists():
        fail(f"Deprecated secondary authority file must not exist: {relative}")

if not governor.get("worker_contract"):
    fail("Governor has no worker_contract")

request_capture = governor.get("request_capture_contract", {})
for field in (
    "important_request_definition",
    "capture_rule",
    "external_advice_rule",
    "anti_loss_rule",
    "coordination_rule",
):
    value = request_capture.get(field)
    if not value or (isinstance(value, str) and not value.strip()):
        fail(f"Governor request_capture_contract missing {field}")

work_ids = {
    str(item.get("id") or "").strip()
    for item in governor.get("work_queue", [])
    if str(item.get("id") or "").strip()
}
review_ids: set[str] = set()
for index, finding in enumerate(governor.get("external_review_findings", []), start=1):
    finding_id = str(finding.get("id") or "").strip()
    if not finding_id:
        fail(f"External review finding {index} has no id")
        continue
    if finding_id in review_ids:
        fail(f"Duplicate external review finding id: {finding_id}")
    review_ids.add(finding_id)
    if not re.fullmatch(r"[0-9a-f]{40}", str(finding.get("verification_sha") or "")):
        fail(f"{finding_id} requires an exact verification SHA")
    for field in ("source", "verification_status", "claim", "disposition", "next_action"):
        if not str(finding.get(field) or "").strip():
            fail(f"{finding_id} missing {field}")
    if "verified_result" not in finding:
        fail(f"{finding_id} missing verified_result")
    for ref in finding.get("linked_requirements", []):
        if ref not in req_ids:
            fail(f"{finding_id} links unknown requirement {ref}")
    for ref in finding.get("linked_work", []):
        if ref not in work_ids:
            fail(f"{finding_id} links unknown work item {ref}")

living_npc_plan = ROOT / "Data" / "LivingNPCIntelligenceRoadmap.json"
if not living_npc_plan.exists():
    fail("Accepted living-NPC intelligence roadmap is missing")
else:
    living_npc = json.loads(living_npc_plan.read_text(encoding="utf-8"))
    if living_npc.get("plan_id") != "LIVING_NPC_INTELLIGENCE_ROADMAP_V2":
        fail("Living-NPC intelligence roadmap identity changed")
    if "Do not require GPT, Claude, cloud APIs, internet connectivity or runtime API keys in the shipped gameplay path." not in living_npc.get("non_goals", []):
        fail("Living-NPC roadmap lost offline/non-cloud runtime boundary")

if not any(r.get("id") == "REQ-NPC-006" for r in governor.get("requirements", [])):
    fail("Governor lost REQ-NPC-006 living-NPC intelligence requirement")
if not any(w.get("id") == "WORK-LW-005" for w in governor.get("work_queue", [])):
    fail("Governor lost WORK-LW-005 living-NPC vertical-slice work item")

# Owner-directed governor role: coordination must not become a project-wide bottleneck.
governor_role = governor.get("governor_role", {})
if governor_role.get("mode") != "OVERSEER_NOT_BOTTLENECK":
    fail("Governor role must remain OVERSEER_NOT_BOTTLENECK")
non_blocking_policy = governor_role.get("non_blocking_policy", [])
if not any("unrelated safe production work" in str(item) for item in non_blocking_policy):
    fail("Governor must explicitly preserve unrelated safe production work during a failing gate")
if governor.get("active_branch") != "develop":
    fail("Governor active_branch must track develop as the integration baseline after PR #53 consolidation")
branch_workflow = governor.get("branch_workflow", {})
if branch_workflow.get("integration_branch") != "develop":
    fail("Governor branch workflow must keep develop as the integration branch")
if "keep the branch short" not in str(branch_workflow.get("rule") or ""):
    fail("Governor branch workflow must require short-lived production branches")

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

errors.extend(validate_handoff(governor))

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
try:
    checkout = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                              capture_output=True, text=True)
    checkout_sha = checkout.stdout.strip() if checkout.returncode == 0 else ''
except OSError:
    checkout_sha = ''  # Exported source archives need not have Git installed.
print(evidence_summary(governor, checkout_sha))

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
