#!/usr/bin/env python3
"""Pre-Unreal validation for the Fellowship personal game.

This intentionally checks only invariants that can be verified without an Unreal Engine
installation. A green result does NOT replace a real UE4.27 compile or PIE run.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict, deque
from pathlib import Path

from source_contracts import has_nonufs_runtime_dependency, signal_precedes_member_mutation
from governance_contracts import validate_development_mode

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Source" / "ShireJourney"
EDITOR_SOURCE = ROOT / "Source" / "ShireJourneyEditorTools"

errors: list[str] = []
warnings: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def warn(message: str) -> None:
    warnings.append(message)


def resolve_source(filename: str) -> Path:
    """Resolve one runtime source filename after the Public/Private migration."""
    candidates = [p for p in SOURCE.rglob(filename) if p.is_file()]
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        return SOURCE / filename
    fail(f"Runtime source filename is ambiguous after migration: {filename}")
    return candidates[0]


def resolve_editor_source(filename: str) -> Path:
    """Resolve one editor-tools source filename without misrouting it into the runtime module."""
    candidates = [p for p in EDITOR_SOURCE.rglob(filename) if p.is_file()]
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        return EDITOR_SOURCE / filename
    fail(f"Editor source filename is ambiguous: {filename}")
    return candidates[0]


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        fail(f"Cannot read {path.relative_to(ROOT)}: {exc}")
        return ""


try:
    from runtime_audit_contracts import (
        CHAPTER_EVIDENCE_KINDS,
        EVIDENCE_MARKERS,
        EVIDENCE_SOURCE_ANCHORS,
        MODE_EVIDENCE_IDS,
        MODE_EXTRA_ARGS,
        MODE_MARKERS,
        RUNTIME_LOG_PREFIXES,
        SOURCE_MARKER_ANCHORS,
        STATE_SEQUENCE_MODES,
        chapter_has_evidence,
        mode_has_evidence,
    )
except Exception as exc:
    fail(f"Cannot import runtime audit contract registry: {exc}")
    CHAPTER_EVIDENCE_KINDS = ()
    EVIDENCE_MARKERS = {}
    EVIDENCE_SOURCE_ANCHORS = {}
    MODE_EVIDENCE_IDS = {}
    MODE_EXTRA_ARGS = {}
    MODE_MARKERS = {}
    RUNTIME_LOG_PREFIXES = ()
    SOURCE_MARKER_ANCHORS = {}
    STATE_SEQUENCE_MODES = ()
    chapter_has_evidence = lambda _kind: False
    mode_has_evidence = lambda _mode, _evidence: False


def is_git_lfs_pointer(path: Path) -> bool:
    try:
        return path.read_bytes().startswith(b"version https://git-lfs.github.com/spec/v1\n")
    except Exception as exc:
        fail(f"Cannot inspect {path.relative_to(ROOT)} for Git LFS pointer: {exc}")
        return False


def strip_comments_and_strings(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r'"(?:\\.|[^"\\])*"', '""', text)
    return text


required_files = [
    ROOT / "ShireJourney.uproject",
    ROOT / "Scripts" / "runtime_audit_contracts.py",
    ROOT / "Scripts" / "test_runtime_audit_contracts.py",
    ROOT / "Scripts" / "source_contracts.py",
    ROOT / "Scripts" / "test_source_contracts.py",
    ROOT / "Scripts" / "governance_contracts.py",
    ROOT / "Scripts" / "test_governance_contracts.py",
    ROOT / "Config" / "DefaultEngine.ini",
    ROOT / "Config" / "DefaultGame.ini",
    ROOT / "Config" / "DefaultInput.ini",
    resolve_source("ShireGameMode.cpp"),
    resolve_source("ShirePlayerCharacter.cpp"),
    resolve_source("ShireQuestSubsystem.cpp"),
    resolve_source("ShireQuestTrigger.cpp"),
    resolve_source("ChapterWorldRouter.cpp"),
    resolve_source("ShirePrototypeWorldBuilder.cpp"),
    resolve_source("BreePrototypeWorldBuilder.cpp"),
    resolve_source("FellowshipChapterWorldBuilder.cpp"),
    resolve_source("ShireStoryPresentationSubsystem.h"),
    resolve_source("ShireStoryPresentationSubsystem.cpp"),
    resolve_source("ShireDialogueSubsystem.h"),
    resolve_source("ShireDialogueSubsystem.cpp"),
    resolve_source("ShireAudioSubsystem.h"),
    resolve_source("ShireAudioSubsystem.cpp"),
    resolve_source("ShireStoryFlowSubsystem.h"),
    resolve_source("ShireStoryFlowSubsystem.cpp"),
    resolve_source("FellowshipEnemyPrototype.h"),
    resolve_source("FellowshipEnemyPrototype.cpp"),
    ROOT / "Source" / "ShireJourneyEditorTools" / "Private" / "ShireProductionImportCommandlet.cpp",
]

for path in required_files:
    if not path.exists():
        fail(f"Required file missing: {path.relative_to(ROOT)}")

# Project Guardian: machine-readable project memory.
guard_rules_path = ROOT / "Data" / "ProjectGuardRules.json"
guard_rules = {}
if not guard_rules_path.exists():
    fail("Project Guardian rules missing: Data/ProjectGuardRules.json")
else:
    try:
        guard_rules = json.loads(read(guard_rules_path))
    except json.JSONDecodeError as exc:
        fail(f"Invalid Data/ProjectGuardRules.json: {exc}")

for relative in guard_rules.get("required_governance_docs", []):
    if not (ROOT / relative).exists():
        fail(f"Required governance document missing: {relative}")

for relative in guard_rules.get("required_story_data", []):
    if not (ROOT / relative).exists():
        fail(f"Required story data missing: {relative}")

for relative in guard_rules.get("required_source_docs", []):
    if not (ROOT / relative).exists():
        fail(f"Required source handoff document missing: {relative}")

for relative in guard_rules.get("required_engineering_data", []):
    if not (ROOT / relative).exists():
        fail(f"Required engineering data missing: {relative}")

# PG-019: source architecture must be explicit and complete so a lost chat or
# developer handoff never leaves runtime ownership implicit.
source_architecture_path = ROOT / "Data" / "SourceArchitecturePlan.json"
source_architecture = {}
if not source_architecture_path.exists():
    fail("Source architecture plan missing: Data/SourceArchitecturePlan.json")
else:
    try:
        source_architecture = json.loads(read(source_architecture_path))
    except json.JSONDecodeError as exc:
        fail(f"Invalid Data/SourceArchitecturePlan.json: {exc}")

architecture_entries = source_architecture.get("files", [])
allowed_source_domains = set(source_architecture.get("allowed_domains", []))
allowed_migration_statuses = set(source_architecture.get("migration_status_values", []))
seen_current_paths: set[str] = set()
seen_target_paths: set[str] = set()
expected_active_source_paths: set[str] = set()

if source_architecture and source_architecture.get("module") != "ShireJourney":
    fail("SourceArchitecturePlan module must be ShireJourney")

for index, entry in enumerate(architecture_entries, start=1):
    current_path = str(entry.get("current_path") or "").strip()
    target_path = str(entry.get("target_path") or "").strip()
    domain = str(entry.get("domain") or "").strip()
    kind = str(entry.get("kind") or "").strip()
    role = str(entry.get("role") or "").strip()
    migration_status = str(entry.get("migration_status") or "").strip()

    if not current_path or not target_path or not domain or not kind or not role or not migration_status:
        fail(f"SourceArchitecturePlan entry {index} is incomplete")
        continue

    if current_path in seen_current_paths:
        fail(f"SourceArchitecturePlan duplicates current_path: {current_path}")
    seen_current_paths.add(current_path)

    if target_path in seen_target_paths:
        fail(f"SourceArchitecturePlan duplicates target_path: {target_path}")
    seen_target_paths.add(target_path)

    if not current_path.startswith("Source/ShireJourney/"):
        fail(f"SourceArchitecturePlan current_path escapes runtime module: {current_path}")
    if not target_path.startswith("Source/ShireJourney/"):
        fail(f"SourceArchitecturePlan target_path escapes runtime module: {target_path}")

    if allowed_source_domains and domain not in allowed_source_domains:
        fail(f"SourceArchitecturePlan entry {current_path} uses unknown domain '{domain}'")
    if allowed_migration_statuses and migration_status not in allowed_migration_statuses:
        fail(f"SourceArchitecturePlan entry {current_path} uses unknown migration status '{migration_status}'")

    filename = Path(current_path).name
    if domain == "ModuleRoot":
        if target_path != current_path:
            fail(f"Module-root file must remain at its current path: {current_path}")
    elif kind == "Header":
        expected_target = f"Source/ShireJourney/Public/{domain}/{filename}"
        if target_path != expected_target:
            fail(f"Header target path must be {expected_target}: {current_path}")
    elif kind == "Source":
        expected_target = f"Source/ShireJourney/Private/{domain}/{filename}"
        if target_path != expected_target:
            fail(f"Source target path must be {expected_target}: {current_path}")
    elif kind != "Build":
        fail(f"SourceArchitecturePlan entry {current_path} uses unknown kind '{kind}'")

    active_path = target_path if migration_status == "MIGRATED" else current_path
    expected_active_source_paths.add(active_path)
    if not (ROOT / active_path).exists():
        fail(f"SourceArchitecturePlan active file is missing: {active_path}")

actual_runtime_source_paths = {
    str(path.relative_to(ROOT)).replace("\\", "/")
    for path in SOURCE.rglob("*")
    if path.is_file() and path.suffix.lower() in {".h", ".cpp", ".cs"}
}
missing_architecture_entries = sorted(actual_runtime_source_paths - expected_active_source_paths)
stale_architecture_entries = sorted(expected_active_source_paths - actual_runtime_source_paths)
if missing_architecture_entries:
    fail("Runtime source files missing from SourceArchitecturePlan: " + ", ".join(missing_architecture_entries))
if stale_architecture_entries:
    fail("SourceArchitecturePlan references inactive/missing runtime files: " + ", ".join(stale_architecture_entries))

# PG-154: the isolated runtime-module migration is now a physical invariant.
if source_architecture.get("current_layout") == "PUBLIC_PRIVATE_BY_DOMAIN":
    remaining_flat = [
        str(p.relative_to(ROOT)).replace("\\", "/")
        for p in list(SOURCE.glob("*.h")) + list(SOURCE.glob("*.cpp"))
    ]
    if remaining_flat:
        fail("PG-154 flat runtime source files reintroduced at module root: " + ", ".join(sorted(remaining_flat)))
    if any(entry.get("migration_status") == "CURRENT_FLAT" for entry in architecture_entries):
        fail("PG-154 SourceArchitecturePlan still contains CURRENT_FLAT entries after migration")
    migrated_build = read(resolve_source("ShireJourney.Build.cs"))
    if "PublicIncludePaths.Add(ModuleDirectory)" in migrated_build:
        fail("PG-154 module-root public include export was reintroduced after migration")
    for domain in ["Core","Characters","World","Subsystems","UI","SaveGame","Prototypes"]:
        expected = f'Path.Combine(ModuleDirectory, "Public", "{domain}")'
        if expected not in migrated_build:
            fail(f"PG-154 public domain include path missing: {domain}")

# PG-155: migration-aware validators and persistent self-hosted checkouts use the
# architecture map rather than historical flat paths.
pg155_self = read(ROOT / "Scripts" / "pre_unreal_validate.py")
pg155_legacy_path = re.compile(
    r'ROOT\s*/\s*["\']Source["\']\s*/\s*["\']ShireJourney["\']\s*/\s*["\'][A-Za-z0-9_.-]+\.(?:h|cpp|cs)["\']'
)
if pg155_legacy_path.search(pg155_self):
    fail("PG-155 Pre-Unreal still constructs a historical flat runtime source path")
pg155_workflow = read(ROOT / ".github" / "workflows" / "unreal-build-validation.yml")
if "prepare_runtime_source_layout.ps1" not in pg155_workflow:
    fail("PG-155 Unreal workflow must remove stale pre-migration source leftovers on the persistent runner")
if not (ROOT / "Scripts" / "prepare_runtime_source_layout.ps1").exists():
    fail("PG-155 persistent-runner source-layout preparation script is missing")

# PG-020: the single Project Governor is the authoritative project-management memory.
governor_path = ROOT / "Data" / "ProjectGovernor.json"
governor_data = {}
if not governor_path.exists():
    fail("Single project governor missing: Data/ProjectGovernor.json")
else:
    try:
        governor_data = json.loads(read(governor_path))
    except json.JSONDecodeError as exc:
        fail(f"Invalid Data/ProjectGovernor.json: {exc}")

if governor_data and governor_data.get("authority_id") != "FELLOWSHIP_SINGLE_PROJECT_GOVERNOR_V2":
    fail("Data/ProjectGovernor.json has unexpected authority_id")

governor_schema_path = ROOT / "Data" / "ProjectGovernor.schema.json"
if not governor_schema_path.exists():
    fail("ProjectGovernor schema missing: Data/ProjectGovernor.schema.json")
else:
    try:
        governor_schema = json.loads(read(governor_schema_path))
    except json.JSONDecodeError as exc:
        fail(f"Invalid Data/ProjectGovernor.schema.json: {exc}")
        governor_schema = {}
    schema_required = governor_schema.get("properties", {}).get("requirements", {}).get("items", {}).get("required", [])
    expected_required = ["id","title","category","priority","status","origin","intent","acceptance_criteria","dependencies"]
    if schema_required != expected_required:
        fail("ProjectGovernor schema requirement contract changed unexpectedly")

allowed_requirement_statuses = set(governor_data.get("requirement_status_values", []))
allowed_requirement_priorities = set(governor_data.get("priority_values", []))
requirement_ids: set[str] = set()
for index, item in enumerate(governor_data.get("requirements", []), start=1):
    req_id = str(item.get("id") or "").strip()
    title = str(item.get("title") or "").strip()
    category = str(item.get("category") or "").strip()
    origin = str(item.get("origin") or "").strip()
    intent = str(item.get("intent") or "").strip()
    status = str(item.get("status") or "").strip()
    priority = str(item.get("priority") or "").strip()
    acceptance = item.get("acceptance_criteria", [])
    dependencies = item.get("dependencies")

    if not req_id or not title or not category or not origin or not intent:
        fail(f"ProjectGovernor requirement entry {index} is missing required identity/intent fields")
        continue
    if not isinstance(dependencies, list):
        fail(f"ProjectGovernor requirement {req_id} dependencies must be a list")
    if req_id in requirement_ids:
        fail(f"Duplicate ProjectGovernor requirement id: {req_id}")
    requirement_ids.add(req_id)
    if allowed_requirement_statuses and status not in allowed_requirement_statuses:
        fail(f"ProjectGovernor requirement {req_id} uses unknown status '{status}'")
    if allowed_requirement_priorities and priority not in allowed_requirement_priorities:
        fail(f"ProjectGovernor requirement {req_id} uses unknown priority '{priority}'")
    if not isinstance(acceptance, list) or not acceptance:
        fail(f"ProjectGovernor requirement {req_id} has no acceptance criteria")

capture_contract = governor_data.get("request_capture_contract", {})
for capture_field in ["important_request_definition","capture_rule","external_advice_rule","anti_loss_rule","coordination_rule"]:
    if not capture_contract.get(capture_field):
        fail(f"ProjectGovernor request capture contract missing {capture_field}")
if not governor_data.get("external_review_findings"):
    fail("ProjectGovernor has no durable external/programmer review findings")
if not any(str(req.get("id") or "") == "REQ-PROD-007" for req in governor_data.get("requirements", [])):
    fail("ProjectGovernor missing REQ-PROD-007 mega material/world wave")
if not any(str(work.get("id") or "") == "WORK-PROD-007" for work in governor_data.get("work_queue", [])):
    fail("ProjectGovernor missing WORK-PROD-007 mega material/world work item")

for required_req in [
    "REQ-MEM-001", "REQ-GOV-001", "REQ-WORLD-001", "REQ-WORLD-002",
    "REQ-NPC-001", "REQ-NPC-002", "REQ-NPC-003", "REQ-SAVE-001", "REQ-PERF-001",
    "REQ-VISION-001", "REQ-EXP-001", "REQ-EXP-002", "REQ-COVERAGE-001",
    "REQ-QUALITY-001", "REQ-QUALITY-002", "REQ-CHAR-001", "REQ-CHAR-002"
]:
    if required_req not in requirement_ids:
        fail(f"Single ProjectGovernor missing critical requirement: {required_req}")

# PG-059: screenplay-derived dialogue source context must be complete and bounded.
film_source_path = ROOT / "Data" / "FilmDialogueSourceContext.json"
film_source_data = {}
if not film_source_path.exists():
    fail("Film dialogue source context missing: Data/FilmDialogueSourceContext.json")
else:
    try:
        film_source_data = json.loads(read(film_source_path))
    except json.JSONDecodeError as exc:
        fail(f"Invalid Data/FilmDialogueSourceContext.json: {exc}")

if film_source_data:
    source_ids = {str(item.get("id") or "").strip() for item in film_source_data.get("sources", [])}
    for required_source in {"SRC-FOTR-2001-SCREENPLAY", "SRC-TTT-2002-SCREENPLAY"}:
        if required_source not in source_ids:
            fail(f"Film dialogue source context missing required source: {required_source}")

    policy = film_source_data.get("policy", {})
    if not policy.get("no_verbatim_screenplay_dialogue"):
        fail("Film dialogue source context must explicitly forbid verbatim screenplay dialogue")

    contexts = film_source_data.get("part1_contexts", [])
    covered = set()
    has_gandalf = False
    seen = set()
    for index, context in enumerate(contexts, start=1):
        context_id = str(context.get("context_id") or "").strip()
        source_id = str(context.get("source_id") or "").strip()
        route = str(context.get("route") or "").strip()
        chapter = str(context.get("chapter") or "").strip()
        if not context_id or not source_id or not route or not chapter:
            fail(f"Film dialogue context entry {index} is incomplete")
            continue
        if context_id in seen:
            fail(f"Duplicate film dialogue context id: {context_id}")
        seen.add(context_id)
        if source_id not in source_ids:
            fail(f"Film dialogue context {context_id} references unknown source {source_id}")
        if not context.get("safe_topics"):
            fail(f"Film dialogue context {context_id} has no safe_topics")
        if not context.get("future_knowledge_blocks"):
            fail(f"Film dialogue context {context_id} has no future_knowledge_blocks")
        forbidden = {"dialogue", "dialogue_text", "screenplay_text", "verbatim_quote", "quote"}
        if forbidden.intersection(context.keys()):
            fail(f"Film dialogue context {context_id} contains a forbidden raw-dialogue field")
        if route == "FrodoMain":
            covered.add(chapter)
        elif route == "GandalfParallel":
            has_gandalf = True

    expected = {f"P1C{i:02d}" for i in range(1, 9)}
    missing = sorted(expected - covered)
    if missing:
        fail("Film dialogue source context missing Part I chapters: " + ", ".join(missing))
    if not has_gandalf:
        fail("Film dialogue source context missing GandalfParallel coverage")

    build_text = read(resolve_source("ShireJourney.Build.cs"))
    if "Data/FilmDialogueSourceContext.json" not in build_text:
        fail("Film dialogue source context is not packaged as a runtime dependency")
    npc_context_text = read(resolve_source("ShireNPCContextSubsystem.cpp"))
    for marker in ["LoadFilmDialogueSourceContext", "GetFilmDialogueContextSummary", "SourceContextId"]:
        if marker not in npc_context_text and marker not in read(resolve_source("ShireNPCContextSubsystem.h")):
            fail(f"Film dialogue runtime wiring missing marker: {marker}")
    # Source-grounded authored variants must resolve to existing runtime contracts.
    context_ids = {str(item.get("context_id") or "").strip() for item in contexts}
    story_rows = []
    story_path = ROOT / "Data" / "StoryBeatPlan.csv"
    if story_path.exists():
        with story_path.open(encoding="utf-8-sig", newline="") as handle:
            story_rows = list(csv.DictReader(handle))
    story_ids = {str(row.get("StoryBeatId") or "").strip() for row in story_rows}

    social_path = ROOT / "Data" / "NPCSocialModel.json"
    social_data = {}
    try:
        social_data = json.loads(read(social_path))
    except json.JSONDecodeError as exc:
        fail(f"Invalid Data/NPCSocialModel.json while checking film dialogue variants: {exc}")
    profile_ids = {str(item.get("id") or "").strip() for item in social_data.get("profiles", [])}

    conversation_path = ROOT / "Data" / "NPCConversationPlan.json"
    conversation_data = {}
    try:
        conversation_data = json.loads(read(conversation_path))
    except json.JSONDecodeError as exc:
        fail(f"Invalid Data/NPCConversationPlan.json while checking film dialogue variants: {exc}")
    intent_ids = {str(item.get("id") or "").strip() for item in conversation_data.get("intent_contracts", [])}

    mood_path = ROOT / "Data" / "NPCRegionalMoodPlan.json"
    mood_data = {}
    try:
        mood_data = json.loads(read(mood_path))
    except json.JSONDecodeError as exc:
        fail(f"Invalid Data/NPCRegionalMoodPlan.json while checking film dialogue variants: {exc}")
    mood_ids = {str(item.get("mood") or "").strip() for item in mood_data.get("chapter_moods", [])}

    source_variants = film_source_data.get("original_dialogue_variants", [])
    if len(source_variants) < 40:
        fail("Film dialogue source context must provide a substantial original dialogue set (at least 40 variants)")

    variant_ids = set()
    for index, variant in enumerate(source_variants, start=1):
        variant_id = str(variant.get("variant_id") or "").strip()
        speaker = str(variant.get("speaker") or "").strip()
        intent = str(variant.get("intent") or "").strip()
        beat = str(variant.get("required_story_beat") or "").strip()
        mood = str(variant.get("required_mood") or "").strip()
        context_id = str(variant.get("context_id") or "").strip()
        text_value = str(variant.get("text") or "").strip()

        if not variant_id or not speaker or not intent or not text_value:
            fail(f"Film dialogue authored variant {index} is incomplete")
            continue
        if variant_id in variant_ids:
            fail(f"Duplicate film dialogue authored variant id: {variant_id}")
        variant_ids.add(variant_id)
        if speaker not in profile_ids:
            fail(f"Film dialogue variant {variant_id} references unknown speaker {speaker}")
        if intent not in intent_ids:
            fail(f"Film dialogue variant {variant_id} references unknown intent {intent}")
        if beat and beat not in story_ids:
            fail(f"Film dialogue variant {variant_id} references unknown story beat {beat}")
        if mood and mood not in mood_ids:
            fail(f"Film dialogue variant {variant_id} references unknown mood {mood}")
        if context_id and context_id not in context_ids:
            fail(f"Film dialogue variant {variant_id} references unknown source context {context_id}")
        if len(text_value.split()) > 38:
            fail(f"Film dialogue variant {variant_id} exceeds the 38-word story-reactive limit")



# PG-060: optional exploration must be explicitly bounded between mandatory story anchors.
exploration_path = ROOT / "Data" / "ExplorationEnvelopePlan.json"
exploration_data = {}
if not exploration_path.exists():
    fail("Exploration envelope plan missing: Data/ExplorationEnvelopePlan.json")
else:
    try:
        exploration_data = json.loads(read(exploration_path))
    except json.JSONDecodeError as exc:
        fail(f"Invalid Data/ExplorationEnvelopePlan.json: {exc}")

if exploration_data:
    chapter_entries = exploration_data.get("chapters", [])
    expected_pairs = {("FrodoMain", f"P1C{i:02d}") for i in range(1, 9)}
    expected_pairs.add(("GandalfParallel", "P1C01"))
    found_pairs = set()

    story_rows_for_exploration = []
    story_plan_path = ROOT / "Data" / "StoryBeatPlan.csv"
    if story_plan_path.exists():
        with story_plan_path.open(encoding="utf-8-sig", newline="") as handle:
            story_rows_for_exploration = list(csv.DictReader(handle))

    story_order_by_pair = {}
    for row in story_rows_for_exploration:
        key = (str(row.get("Route") or "").strip(), str(row.get("Chapter") or "").strip())
        story_order_by_pair.setdefault(key, []).append(str(row.get("StoryBeatId") or "").strip())

    for entry in chapter_entries:
        route = str(entry.get("route") or "").strip()
        chapter = str(entry.get("chapter") or "").strip()
        key = (route, chapter)
        if not route or not chapter:
            fail("Exploration envelope entry missing route/chapter")
            continue
        if key in found_pairs:
            fail(f"Duplicate exploration envelope for {route}/{chapter}")
        found_pairs.add(key)

        declared_order = [str(x).strip() for x in entry.get("anchor_order", []) if str(x).strip()]
        actual_order = story_order_by_pair.get(key, [])
        if not declared_order:
            fail(f"Exploration envelope {route}/{chapter} has no anchor_order")
            continue
        missing_anchors = [beat for beat in declared_order if beat not in actual_order]
        if missing_anchors:
            fail(f"Exploration envelope {route}/{chapter} references unknown story beats: {', '.join(missing_anchors)}")
        positions = [actual_order.index(beat) for beat in declared_order if beat in actual_order]
        if positions != sorted(positions):
            fail(f"Exploration envelope {route}/{chapter} reorders mandatory story beats")

        index = {beat: i for i, beat in enumerate(declared_order)}
        for window in entry.get("free_roam_windows", []):
            wid = str(window.get("id") or "").strip()
            opens = str(window.get("opens_after") or "").strip()
            closes = str(window.get("closes_before") or "").strip()
            if not wid or opens not in index or closes not in index:
                fail(f"Exploration window {wid or '<unnamed>'} in {route}/{chapter} has invalid anchors")
                continue
            if index[opens] >= index[closes]:
                fail(f"Exploration window {wid} in {route}/{chapter} crosses/reverses mandatory anchor order")

        discoveries = entry.get("optional_discoveries", [])
        if route == "FrodoMain" and chapter != "P1C01" and len(discoveries) < 2:
            fail(f"Exploration envelope {route}/{chapter} must define at least two non-Shire optional discoveries")
        for discovery in discoveries:
            did = str(discovery.get("id") or "").strip()
            window = discovery.get("available_between", [])
            if len(window) != 2 or window[0] not in index or window[1] not in index:
                fail(f"Optional discovery {did or '<unnamed>'} in {route}/{chapter} has invalid availability anchors")
                continue
            if index[window[0]] > index[window[1]]:
                fail(f"Optional discovery {did} in {route}/{chapter} reverses story order")
            if discovery.get("story_effect") != "NONE":
                fail(f"Optional discovery {did} must have story_effect NONE")
            if discovery.get("may_advance_required_anchor") is not False:
                fail(f"Optional discovery {did} may not advance required anchors")
            if discovery.get("may_change_canon_outcome") is not False:
                fail(f"Optional discovery {did} may not change canon outcomes")

        if not entry.get("return_policy"):
            fail(f"Exploration envelope {route}/{chapter} has no return_policy")

    missing_pairs = sorted(expected_pairs - found_pairs)
    if missing_pairs:
        fail("Exploration envelope coverage missing: " + ", ".join(f"{r}/{c}" for r, c in missing_pairs))

# PG-061: one-click/CI import must never normalize tracked SourceAssets in place.
production_import_hygiene = read(
    ROOT / "Source" / "ShireJourneyEditorTools" / "Private" / "ShireProductionImportCommandlet.cpp"
)
for marker in [
    "ProjectSavedDir()",
    "ShireProductionImportWorking",
    "CopyDirectoryTree",
    "FindFilesRecursive(TextureFiles, *WorkingRoot",
    "FindFilesRecursive(MeshFiles, *WorkingRoot",
]:
    if marker not in production_import_hygiene:
        fail(f"PG-061: production importer missing non-destructive working-copy marker: {marker}")
if "FindFilesRecursive(TextureFiles, *SourceRoot" in production_import_hygiene:
    fail("PG-061: production importer must not import/normalize textures directly from tracked SourceAssets")
if "FindFilesRecursive(MeshFiles, *SourceRoot" in production_import_hygiene:
    fail("PG-061: production importer must not import/normalize meshes directly from tracked SourceAssets")


# PG-062: Journey Discovery rewards must cover declared exploration without enabling canon/story farming.
discovery_reward_path = ROOT / "Data" / "JourneyDiscoveryRewardPlan.json"
discovery_reward_data = {}
if not discovery_reward_path.exists():
    fail("Journey discovery reward plan missing: Data/JourneyDiscoveryRewardPlan.json")
else:
    try:
        discovery_reward_data = json.loads(read(discovery_reward_path))
    except json.JSONDecodeError as exc:
        fail(f"Invalid Data/JourneyDiscoveryRewardPlan.json: {exc}")

if discovery_reward_data:
    exploration_for_rewards = {}
    try:
        exploration_for_rewards = json.loads(read(ROOT / "Data" / "ExplorationEnvelopePlan.json"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid ExplorationEnvelopePlan.json while validating discovery rewards: {exc}")

    declared_discoveries = {
        str(item.get("id") or "").strip()
        for chapter in exploration_for_rewards.get("chapters", [])
        for item in chapter.get("optional_discoveries", [])
        if isinstance(item, dict)
    }
    reward_rows = discovery_reward_data.get("discovery_rewards", [])
    reward_ids = [str(item.get("discovery_id") or "").strip() for item in reward_rows]
    if len(reward_ids) != len(set(reward_ids)):
        fail("Journey discovery reward plan has duplicate discovery_id entries")
    missing_rewards = sorted(declared_discoveries - set(reward_ids))
    unknown_rewards = sorted(set(reward_ids) - declared_discoveries)
    if missing_rewards:
        fail("Journey discovery rewards missing declared discoveries: " + ", ".join(missing_rewards))
    if unknown_rewards:
        fail("Journey discovery rewards reference unknown discoveries: " + ", ".join(unknown_rewards))

    allowed_categories = {"ROAD_WISDOM", "PEOPLES_AND_PLACES", "FELLOWSHIP_BONDS", "PERIL_SENSE"}
    for row in reward_rows:
        did = str(row.get("discovery_id") or "").strip()
        if row.get("first_time_only") is not True:
            fail(f"Journey discovery reward {did} must be first_time_only")
        if int(row.get("journey_insight") or 0) <= 0:
            fail(f"Journey discovery reward {did} must award positive Journey Insight")
        if str(row.get("category") or "") not in allowed_categories:
            fail(f"Journey discovery reward {did} has invalid category")
        if row.get("story_effect") != "NONE":
            fail(f"Journey discovery reward {did} may not mutate story state")
        if row.get("may_advance_required_anchor") is not False:
            fail(f"Journey discovery reward {did} may not advance required anchors")
        if row.get("may_change_canon_outcome") is not False:
            fail(f"Journey discovery reward {did} may not change canon outcomes")

    hard_rules = discovery_reward_data.get("hard_rules", {})
    for rule in ["first_time_points_only", "mandatory_story_skip", "route_skip", "canon_outcome_change", "network_dependency", "raw_screenplay_reward_text"]:
        if rule == "first_time_points_only":
            if hard_rules.get(rule) is not True:
                fail("Journey discovery hard rule first_time_points_only must remain true")
        elif hard_rules.get(rule) is not False:
            fail(f"Journey discovery hard rule {rule} must remain false")
    if hard_rules.get("combat_stat_boosts") is not False or hard_rules.get("health_damage_armor_inflation") is not False:
        fail("Journey discovery rewards must not become generic combat-stat inflation")

    expected_region_pairs = {
        (str(ch.get("route") or ""), str(ch.get("chapter") or ""))
        for ch in exploration_for_rewards.get("chapters", [])
    }
    actual_region_pairs = {
        (str(item.get("route") or ""), str(item.get("chapter") or ""))
        for item in discovery_reward_data.get("region_completion_bonuses", [])
    }
    if expected_region_pairs - actual_region_pairs:
        fail("Journey discovery plan missing region-completion coverage")

    build_text_pg62 = read(resolve_source("ShireJourney.Build.cs"))
    if "Data/JourneyDiscoveryRewardPlan.json" not in build_text_pg62:
        fail("Journey discovery reward plan is not packaged as a runtime dependency")


# PG-063: contextual side activities must remain plausible gap-fill inside film story windows.
side_activity_path = ROOT / "Data" / "ContextualSideActivityPlan.json"
side_activity_data = {}
if not side_activity_path.exists():
    fail("Contextual side activity plan missing: Data/ContextualSideActivityPlan.json")
else:
    try:
        side_activity_data = json.loads(read(side_activity_path))
    except json.JSONDecodeError as exc:
        fail(f"Invalid Data/ContextualSideActivityPlan.json: {exc}")

if side_activity_data:
    try:
        exploration_for_side = json.loads(read(ROOT / "Data" / "ExplorationEnvelopePlan.json"))
    except json.JSONDecodeError as exc:
        exploration_for_side = {}
        fail(f"Invalid ExplorationEnvelopePlan.json while checking side activities: {exc}")

    try:
        rewards_for_side = json.loads(read(ROOT / "Data" / "JourneyDiscoveryRewardPlan.json"))
    except json.JSONDecodeError as exc:
        rewards_for_side = {}
        fail(f"Invalid JourneyDiscoveryRewardPlan.json while checking side activities: {exc}")

    envelope_by_pair = {
        (str(ch.get("route") or ""), str(ch.get("chapter") or "")): ch
        for ch in exploration_for_side.get("chapters", [])
        if isinstance(ch, dict)
    }
    reward_ids = {
        str(row.get("discovery_id") or "")
        for row in rewards_for_side.get("discovery_rewards", [])
        if isinstance(row, dict)
    }

    seen_side_ids = set()
    coverage = set()
    for chapter in side_activity_data.get("chapters", []):
        route = str(chapter.get("route") or "")
        chapter_id = str(chapter.get("chapter") or "")
        pair = (route, chapter_id)
        envelope = envelope_by_pair.get(pair)
        if not envelope:
            fail(f"Side activity chapter has no exploration envelope: {route}/{chapter_id}")
            continue
        coverage.add(pair)
        anchor_order = [str(x) for x in envelope.get("anchor_order", [])]
        anchor_index = {beat: i for i, beat in enumerate(anchor_order)}
        activities = chapter.get("activities", [])
        if route == "FrodoMain" and len(activities) < 2:
            fail(f"Contextual side activity coverage too thin for {route}/{chapter_id}")

        for activity in activities:
            aid = str(activity.get("id") or "")
            opens = str(activity.get("available_after") or "")
            closes = str(activity.get("ends_before") or "")
            reward = str(activity.get("discovery_reward_id") or "")
            if not aid:
                fail(f"Unnamed side activity in {route}/{chapter_id}")
                continue
            if aid in seen_side_ids:
                fail(f"Duplicate contextual side activity id: {aid}")
            seen_side_ids.add(aid)
            if opens not in anchor_index or closes not in anchor_index or anchor_index[opens] >= anchor_index[closes]:
                fail(f"Contextual side activity {aid} has invalid story window")
            if activity.get("canon_effect") != "NONE":
                fail(f"Contextual side activity {aid} may not mutate canon")
            if activity.get("may_advance_required_anchor") is not False:
                fail(f"Contextual side activity {aid} may not advance required story anchors")
            if activity.get("may_change_canon_outcome") is not False:
                fail(f"Contextual side activity {aid} may not change canon outcomes")
            if activity.get("future_knowledge_allowed") is not False:
                fail(f"Contextual side activity {aid} must forbid future knowledge")
            if not activity.get("film_context"):
                fail(f"Contextual side activity {aid} must document why it fits the film context")
            if not activity.get("urgency_policy"):
                fail(f"Contextual side activity {aid} must define an urgency override")
            if reward not in reward_ids:
                fail(f"Contextual side activity {aid} references unknown Journey Discovery reward {reward}")

    expected_side_coverage = {("FrodoMain", f"P1C{i:02d}") for i in range(1, 9)}
    expected_side_coverage.add(("GandalfParallel", "P1C01"))
    missing_side_coverage = sorted(expected_side_coverage - coverage)
    if missing_side_coverage:
        fail("Contextual side activity coverage missing: " + ", ".join(f"{r}/{c}" for r, c in missing_side_coverage))

    build_text_pg63 = read(resolve_source("ShireJourney.Build.cs"))
    if "Data/ContextualSideActivityPlan.json" not in build_text_pg63:
        fail("Contextual side activity plan is not packaged as a runtime dependency")


# PG-070: Ring quest systemic axis must remain explicit and runtime-audited.
ring_plan_path = ROOT / "Data" / "TrilogyRingQuestPlan.json"
if not ring_plan_path.exists():
    fail("PG-070: TrilogyRingQuestPlan.json missing")
else:
    ring_plan = json.loads(read(ring_plan_path))
    if ring_plan.get("axis_policy") != "RING_IS_CENTRAL":
        fail("PG-070: Ring axis policy changed")
    windows = ring_plan.get("part1_windows", [])
    covered = {str(x.get("chapter") or "") for x in windows if x.get("route") == "FrodoMain"}
    if {f"P1C{i:02d}" for i in range(1, 9)} - covered:
        fail("PG-070: Ring plan must cover P1C01-P1C08")
    gandalf = [x for x in windows if x.get("route") == "GandalfParallel"]
    if not gandalf or any(x.get("bearer") != "Frodo" for x in gandalf):
        fail("PG-070: GandalfParallel must preserve Frodo as off-route Ring-bearer")
for symbol in ["IsRingQuestActive", "GetRingBearerId", "GetRingStateTag", "GetRingPressureTier"]:
    if symbol not in read(resolve_source("ShireQuestSubsystem.h")) or symbol not in read(resolve_source("ShireQuestSubsystem.cpp")):
        fail(f"PG-070: Ring runtime API missing {symbol}")
if not mode_has_evidence("state", "state.ring_core"):
    fail("PG-070: runtime state audit must require Ring continuity")

# PG-071: character-production matrix must cover the Part I core cast and retain provenance rules.
character_matrix_path = ROOT / "Data" / "CharacterProductionMatrix.json"
if not character_matrix_path.exists():
    fail("PG-071: CharacterProductionMatrix.json missing")
else:
    character_matrix = json.loads(read(character_matrix_path))
    ids = {str(x.get("id") or "") for x in character_matrix.get("characters", [])}
    required = {"FRODO","SAM","MERRY","PIPPIN","GANDALF","ARAGORN","BOROMIR","LEGOLAS","GIMLI","BILBO","ARWEN","ELROND","GALADRIEL","SARUMAN","NAZGUL"}
    if required - ids:
        fail("PG-071: character-production matrix missing core cast")
    policy = character_matrix.get("sourcing_policy", {})
    if "Free availability is not treated as permission by itself" not in str(policy.get("rule") or ""):
        fail("PG-071: external-character provenance rule missing")

# PG-072: cinematic world-production matrix must cover every current Part I region.
world_matrix_path = ROOT / "Data" / "CinematicWorldProductionMatrix.json"
if not world_matrix_path.exists():
    fail("PG-072: CinematicWorldProductionMatrix.json missing")
else:
    world_matrix = json.loads(read(world_matrix_path))
    pairs = {(str(x.get("chapter") or ""), str(x.get("region") or "")) for x in world_matrix.get("regions", [])}
    chapters = {x[0] for x in pairs}
    expected = {f"P1C{i:02d}" for i in range(1, 9)} | {"P1G01"}
    if expected - chapters:
        fail("PG-072: cinematic world matrix missing Part I chapter coverage")
    for region in world_matrix.get("regions", []):
        if not region.get("hero_vistas") or not region.get("foreground") or not region.get("background"):
            fail(f"PG-072: incomplete layered composition for {region.get('chapter')}")

# PG-073: owner-supplied source references must stay indexed and runtime-reference-only.
source_index_path = ROOT / "Data" / "OwnerSourceReferenceIndex.json"
if not source_index_path.exists():
    fail("PG-073: OwnerSourceReferenceIndex.json missing")
else:
    source_index = json.loads(read(source_index_path))
    source_ids = {str(x.get("id") or "") for x in source_index.get("sources", [])}
    for required_id in ["SRC_FILM_FOTR_SCREENPLAY","SRC_FILM_TTT_SCREENPLAY","SRC_OWNER_MASTER_PACK","SRC_OWNER_FOREST_BEAUTY_BENCHMARK"]:
        if required_id not in source_ids:
            fail(f"PG-073: owner source index missing {required_id}")
    if any(bool(x.get("runtime_ship")) for x in source_index.get("sources", [])):
        fail("PG-073: raw owner reference sources must not be required/shipped at runtime")


# PG-074: Journey Discovery runtime must be first-time-only, persisted and story-window bounded.
journey_h = read(resolve_source("ShireQuestSubsystem.h"))
journey_cpp = read(resolve_source("ShireQuestSubsystem.cpp"))
journey_save = read(resolve_source("ShireSaveGame.h"))
journey_player = read(resolve_source("ShirePlayerCharacter.cpp"))
journey_trigger_h = read(resolve_source("ShireQuestTrigger.h"))
journey_trigger_cpp = read(resolve_source("ShireQuestTrigger.cpp"))
journey_hud_h = read(resolve_source("ShireHUD.h"))
journey_hud_cpp = read(resolve_source("ShireHUD.cpp"))
journey_game_mode = read(resolve_source("ShireGameMode.cpp"))

for symbol in [
    "RegisterJourneyDiscovery",
    "HasJourneyDiscovery",
    "GetJourneyInsight",
    "RestoreJourneyDiscoveryState",
]:
    if symbol not in journey_h or symbol not in journey_cpp:
        fail(f"PG-074: Journey Discovery runtime API missing {symbol}")

for marker in ["JourneyDiscoveryIds", "JourneyInsight", "JourneyInsightMilestones"]:
    if marker not in journey_save or marker not in journey_player:
        fail(f"PG-074: Journey Discovery save/load persistence missing {marker}")

for marker in ["DiscoveryId", "DiscoveryDisplayName", "BlockedAfterStoryBeat"]:
    if marker not in journey_trigger_h or marker not in journey_trigger_cpp:
        fail(f"PG-074: discovery trigger window/reward field missing {marker}")

if "ShowDiscovery" not in journey_hud_h or "ShowDiscovery" not in journey_hud_cpp:
    fail("PG-074: player-facing discovery toast is missing")

if EVIDENCE_SOURCE_ANCHORS.get("state.discovery_core", ("", ""))[1] not in journey_game_mode:
    fail("PG-074: engine state audit does not prove discovery first-time continuity")
if not mode_has_evidence("state", "state.discovery_core"):
    fail("PG-074: runtime smoke does not require discovery continuity")

journey_plan_runtime = json.loads(read(ROOT / "Data" / "JourneyDiscoveryRewardPlan.json"))
journey_reward_ids = {
    str(item.get("discovery_id") or "").strip()
    for item in journey_plan_runtime.get("discovery_rewards", [])
    if isinstance(item, dict)
}
journey_builder_text = "\n".join([
    read(resolve_source("ShirePrototypeWorldBuilder.cpp")),
    read(resolve_source("BreePrototypeWorldBuilder.cpp")),
    read(resolve_source("FellowshipChapterWorldBuilder.cpp")),
    read(resolve_source("IsengardPrototypeWorldBuilder.cpp")),
])
missing_runtime_discoveries = sorted(
    discovery_id for discovery_id in journey_reward_ids
    if discovery_id and discovery_id not in journey_builder_text
)
if missing_runtime_discoveries:
    fail("PG-074: Journey Discovery runtime trigger coverage missing: " + ", ".join(missing_runtime_discoveries))


# PG-075: modern game layer must preserve fixed film anchors while expanding optional play.
modern_game_path = ROOT / "Data" / "ModernGameLayerPlan.json"
if not modern_game_path.exists():
    fail("PG-075: ModernGameLayerPlan.json missing")
else:
    modern_game = json.loads(read(modern_game_path))
    canon = modern_game.get("canon_contract", {})
    if "fixed" not in str(canon.get("fixed_story") or "").lower():
        fail("PG-075: film story must remain explicitly fixed")
    side_rule = str(canon.get("side_content_rule") or "").lower()
    for required_phrase in ["may not replace", "skip", "reorder", "change"]:
        if required_phrase not in side_rule:
            fail("PG-075: side-content canon guard is incomplete")
            break

    source_rule = str(canon.get("source_verification_rule") or "").lower()
    if "verified" not in source_rule or "do not rely on memory" not in source_rule:
        fail("PG-075: FILM_CORE source-verification rule is missing")
    uncertainty_rule = str(canon.get("uncertainty_rule") or "").lower()
    if "unverified" not in uncertainty_rule or "do not invent" not in uncertainty_rule:
        fail("PG-075: unresolved film beats must remain unverified rather than invented")

    axes = {str(x.get("id") or "") for x in modern_game.get("player_life_layer", {}).get("persistent_axes", [])}
    for required_axis in {"HEALTH", "STAMINA", "RESOLVE", "FELLOWSHIP_BOND", "SUPPLIES"}:
        if required_axis not in axes:
            fail(f"PG-075: player-life layer missing {required_axis}")

    tracks = {str(x.get("id") or "") for x in modern_game.get("progression_tracks", [])}
    for required_track in {"WAYFINDING","PERCEPTION","QUIET_STEP","CAMPCRAFT","FELLOWSHIP","LORE","RESOLVE"}:
        if required_track not in tracks:
            fail(f"PG-075: progression track missing {required_track}")

    chapters = {str(x.get("chapter") or "") for x in modern_game.get("chapter_gameplay_examples", [])}
    expected = {f"P1C{i:02d}" for i in range(1, 9)} | {"P1G01"}
    if expected - chapters:
        fail("PG-075: modern game layer missing Part I/Gandalf chapter coverage")

    forbidden_rewards = " ".join(modern_game.get("reward_rules", {}).get("forbidden", [])).lower()
    for marker in ["canon", "ring ownership", "loot"]:
        if marker not in forbidden_rewards:
            fail(f"PG-075: reward safety contract missing {marker}")


# PG-076: ensemble film missions must use verified film viewpoints and bounded gap-fill.
ensemble_path = ROOT / "Data" / "EnsembleFilmMissionPlan.json"
if not ensemble_path.exists():
    fail("PG-076: EnsembleFilmMissionPlan.json missing")
else:
    ensemble = json.loads(read(ensemble_path))
    rules = " ".join(ensemble.get("non_negotiable_rules", [])).lower()
    for marker in ["viewpoint", "film", "required film scene", "original gap-fill"]:
        if marker not in rules:
            fail(f"PG-076: ensemble mission safety contract missing {marker}")

    part1_ids = {str(x.get("id") or "") for x in ensemble.get("part1", [])}
    for required_id in {
        "P1_GANDALF_RING_INVESTIGATION",
        "P1_GANDALF_ISENGARD",
        "P1_ARWEN_FORD",
        "P1_GIMLI_MORIA",
        "P1_BOROMIR_AMON_HEN_DEFENSE",
    }:
        if required_id not in part1_ids:
            fail(f"PG-076: missing Part I ensemble mission {required_id}")

    for section in ["part1", "part2", "part3"]:
        for mission in ensemble.get(section, []):
            if not mission.get("source_basis") or not mission.get("canon_lock"):
                fail(f"PG-076: {mission.get('id')} missing source basis or canon lock")

    for mission in ensemble.get("part3", []):
        if mission.get("tag") != "FUTURE_SOURCE_CHECK":
            fail(f"PG-076: Part III mission {mission.get('id')} must remain FUTURE_SOURCE_CHECK until exact source verification")

    forbidden = " ".join(ensemble.get("expansion_budget", {}).get("forbidden", [])).lower()
    for marker in ["ring bearer", "war outcome", "canonical death", "required film scene"]:
        if marker not in forbidden:
            fail(f"PG-076: ensemble expansion guard missing {marker}")


# PG-077: side-content catalog must keep film, gap-fill and book continuity separated.
side_catalog_path = ROOT / "Data" / "SideContentCanonCatalog.json"
if not side_catalog_path.exists():
    fail("PG-077: SideContentCanonCatalog.json missing")
else:
    side_catalog = json.loads(read(side_catalog_path))
    classes = set(side_catalog.get("authority_order", []))
    for required_class in {"FILM_CORE","FILM_EXPANDED","FILM_INTERSTITIAL","BOOK_CHRONICLE"}:
        if required_class not in classes:
            fail(f"PG-077: missing side-content class {required_class}")

    allowed_status = set(side_catalog.get("source_status_values", []))
    for section in ["part1","part2","part3","chronicles"]:
        for row in side_catalog.get(section, []):
            if len(row) != 4:
                fail(f"PG-077: malformed {section} row")
                continue
            if row[2] not in allowed_status:
                fail(f"PG-077: invalid source status {row[2]} for {row[0]}")

    for row in side_catalog.get("part3", []):
        if row[2] != "FUTURE_SOURCE_CHECK":
            fail(f"PG-077: Part III item promoted before source verification: {row[0]}")

    for row in side_catalog.get("chronicles", []):
        if row[1] != "BOOK_CHRONICLE" or row[3] != "BOOK_CHRONICLE_NONCANON_TO_FILM":
            fail(f"PG-077: book Chronicle leaked into film continuity: {row[0]}")

    notes = " ".join(side_catalog.get("audit_notes", [])).lower()
    if "does not begin at bilbo's birthday party" not in notes:
        fail("PG-077: Fellowship opening-order correction missing")


# PG-077: all trilogy side content must use one canon-safe taxonomy.
side_master_path = ROOT / "Data" / "FilmSideContentMasterPlan.json"
if not side_master_path.exists():
    fail("PG-077: FilmSideContentMasterPlan.json missing")
else:
    side_master = json.loads(read(side_master_path))
    allowed_types = {"FILM_MOMENT", "FILM_EXPANDED", "CHRONICLE"}
    for section in ["fellowship", "two_towers", "return_of_king", "chronicles"]:
        for item in side_master.get(section, []):
            if item.get("type") not in allowed_types:
                fail(f"PG-077: {item.get('id')} has invalid side-content type")
            if not item.get("canon_lock") and section != "chronicles":
                fail(f"PG-077: {item.get('id')} missing canon lock")
    for item in side_master.get("chronicles", []):
        if item.get("type") != "CHRONICLE":
            fail(f"PG-077: book/history item {item.get('id')} must remain CHRONICLE")
    corrections = " ".join(
        str(x.get("correction") or "") for x in side_master.get("audits_and_corrections", [])
    ).lower()
    for marker in ["attack must still happen", "ring incident", "treebeard", "pippin", "book-only"]:
        if marker not in corrections:
            fail(f"PG-077: continuity correction missing {marker}")
    if len(side_master.get("prototype_priority", [])) < 10:
        fail("PG-077: prototype priority set must contain at least 10 entries")


# PG-078: master execution roadmap must cover every unfinished accepted requirement and ACTIVE work item.
master_path = ROOT / "Data" / "MasterExecutionRoadmap.json"
if not master_path.exists():
    fail("PG-078: MasterExecutionRoadmap.json missing")
else:
    master = json.loads(read(master_path))
    if master.get("authority") != "Data/ProjectGovernor.json":
        fail("PG-078: master roadmap must remain subordinate to ProjectGovernor")

    roadmap_req_ids = set()
    roadmap_work_ids = set()
    for bundle in master.get("bundles", []):
        roadmap_req_ids.update(str(x) for x in bundle.get("requirement_ids", []))
        roadmap_work_ids.update(str(x) for x in bundle.get("work_ids", []))
        if not bundle.get("deliverables") or not bundle.get("exit_evidence"):
            fail(f"PG-078: bundle {bundle.get('id')} missing deliverables or exit evidence")
    for lane in master.get("continuous_lanes", []):
        roadmap_req_ids.update(str(x) for x in lane.get("requirement_ids", []))
        roadmap_work_ids.update(str(x) for x in lane.get("work_ids", []))

    governor = json.loads(read(ROOT / "Data" / "ProjectGovernor.json"))
    open_req_ids = {
        str(req.get("id"))
        for req in governor.get("requirements", [])
        if req.get("status") not in {"VALIDATED","REJECTED","SUPERSEDED","DEFERRED"}
        and req.get("missing_work")
    }
    active_work_ids = {
        str(work.get("id"))
        for work in governor.get("work_queue", [])
        if work.get("status") == "ACTIVE"
    }

    missing_reqs = sorted(open_req_ids - roadmap_req_ids)
    missing_work = sorted(active_work_ids - roadmap_work_ids)
    if missing_reqs:
        fail("PG-078: unfinished Governor requirements orphaned from master roadmap: " + ", ".join(missing_reqs))
    if missing_work:
        fail("PG-078: ACTIVE work items orphaned from master roadmap: " + ", ".join(missing_work))

    tracked_reqs = set(str(x) for x in master.get("tracked_unfinished_requirement_ids", []))
    tracked_work = set(str(x) for x in master.get("tracked_active_work_ids", []))
    if tracked_reqs != open_req_ids:
        fail("PG-078: tracked unfinished requirement snapshot is stale")
    if tracked_work != active_work_ids:
        fail("PG-078: tracked active work snapshot is stale")

    invariant_text = " ".join(master.get("invariants", [])).lower()
    for marker in ["film", "ring", "offline", "30 fps", "exact candidate head"]:
        if marker not in invariant_text:
            fail(f"PG-078: master roadmap invariant missing {marker}")


# PG-079: player-life and progression must remain lightweight, persisted and film-safe.
life_path = ROOT / "Data" / "PlayerLifeProgressionPlan.json"
if not life_path.exists():
    fail("PG-079: PlayerLifeProgressionPlan.json missing")
else:
    life = json.loads(read(life_path))
    axes = {str(x.get("id") or "") for x in life.get("runtime_axes", [])}
    for axis in {"HEALTH","STAMINA","RESOLVE","FELLOWSHIP_BOND","SUPPLIES"}:
        if axis not in axes:
            fail(f"PG-079: player-life axis missing {axis}")
    tracks = {str(x.get("id") or "") for x in life.get("progression_tracks", [])}
    for track in {"WAYFINDING","PERCEPTION","QUIET_STEP","CAMPCRAFT","FELLOWSHIP","LORE","RESOLVE"}:
        if track not in tracks:
            fail(f"PG-079: progression track missing {track}")
    hard = " ".join(life.get("hard_rules", [])).lower()
    for marker in ["no hunger", "no thirst", "no gear score", "film scenes"]:
        if marker not in hard:
            fail(f"PG-079: anti-grind/canon rule missing {marker}")
player_h = read(resolve_source("ShirePlayerCharacter.h"))
player_cpp = read(resolve_source("ShirePlayerCharacter.cpp"))
quest_h = read(resolve_source("ShireQuestSubsystem.h"))
quest_cpp = read(resolve_source("ShireQuestSubsystem.cpp"))
save_h = read(resolve_source("ShireSaveGame.h"))
for symbol in ["GetCurrentStamina","GetCurrentResolve","GetSupplies","UseSupply","UpdatePlayerLife"]:
    if symbol not in player_h and symbol not in player_cpp:
        fail(f"PG-079: player-life runtime symbol missing {symbol}")
for symbol in ["AwardProgressionXP","GetProgressionXP","GetProgressionRank","GetFellowshipBond","RestoreProgressionState"]:
    if symbol not in quest_h or symbol not in quest_cpp:
        fail(f"PG-079: progression runtime symbol missing {symbol}")
for marker in ["PlayerStamina","PlayerResolve","PlayerSupplies","ProgressionXP","CurrentSchemaVersion = 6"]:
    if marker not in save_h:
        fail(f"PG-079: save schema missing {marker}")
if 'ActionName="UseSupply"' not in read(ROOT / "Config" / "DefaultInput.ini"):
    fail("PG-079: supply input mapping missing")
if EVIDENCE_SOURCE_ANCHORS.get("state.progression_core", ("", ""))[1] not in read(resolve_source("ShireGameMode.cpp")):
    fail("PG-079: progression state audit missing")
if not mode_has_evidence("state", "state.progression_core"):
    fail("PG-079: runtime smoke does not require progression proof")
if "Data/PlayerLifeProgressionPlan.json" not in read(resolve_source("ShireJourney.Build.cs")):
    fail("PG-079: player-life plan not packaged")


# PG-080: Chronicle/map knowledge and side-activity progression must be persistent and story-safe.
knowledge_path = ROOT / "Data" / "ChronicleMapKnowledgePlan.json"
if not knowledge_path.exists():
    fail("PG-080: ChronicleMapKnowledgePlan.json missing")
else:
    knowledge = json.loads(read(knowledge_path))
    if knowledge.get("main_film_continuity_only") is not True:
        fail("PG-080: Chronicle runtime must not silently mix Book Chronicle continuity")
    if knowledge.get("save_schema_version") != 6:
        fail("PG-080: Chronicle/map plan save schema must be 6")
    if knowledge.get("story_effect") != "NONE":
        fail("PG-080: Chronicle/map knowledge must not advance story")

quest_h_pg80 = read(resolve_source("ShireQuestSubsystem.h"))
quest_cpp_pg80 = read(resolve_source("ShireQuestSubsystem.cpp"))
save_h_pg80 = read(resolve_source("ShireSaveGame.h"))
player_cpp_pg80 = read(resolve_source("ShirePlayerCharacter.cpp"))
hud_cpp_pg80 = read(resolve_source("ShireHUD.cpp"))
input_pg80 = read(ROOT / "Config" / "DefaultInput.ini")
side_plan_pg80 = json.loads(read(ROOT / "Data" / "ContextualSideActivityPlan.json"))

for symbol in ["ChronicleEntryIds","KnownMapRegionIds","RestoreKnowledgeState","LoadSideActivityPlan","AwardSideActivityProgression"]:
    if symbol not in (quest_h_pg80 + quest_cpp_pg80):
        fail(f"PG-080: runtime knowledge/side-progression symbol missing {symbol}")
for marker in ["ChronicleEntryIds","KnownMapRegionIds","CurrentSchemaVersion = 6"]:
    if marker not in save_h_pg80:
        fail(f"PG-080: save persistence missing {marker}")
for marker in ["GetChronicleEntryIds","GetKnownMapRegionIds","RestoreKnowledgeState"]:
    if marker not in player_cpp_pg80:
        fail(f"PG-080: player save/load knowledge wiring missing {marker}")
if 'ActionName="ToggleChronicle"' not in input_pg80:
    fail("PG-080: Chronicle panel input missing")
if "CHRONICLE & JOURNEY" not in hud_cpp_pg80:
    fail("PG-080: Chronicle/map HUD panel missing")
if EVIDENCE_SOURCE_ANCHORS.get("state.knowledge_core", ("", ""))[1] not in read(resolve_source("ShireGameMode.cpp")):
    fail("PG-080: knowledge state audit missing")
if not mode_has_evidence("state", "state.knowledge_core"):
    fail("PG-080: runtime smoke missing knowledge proof")
activity_count_pg80 = sum(
    len(chapter.get("activities", []))
    for chapter in side_plan_pg80.get("chapters", [])
    if isinstance(chapter, dict)
)
if activity_count_pg80 < 18:
    fail(f"PG-080: contextual side-activity catalog regressed below 18 entries: {activity_count_pg80}")


# PG-081: real traversal challenge runtime must replace pure touch-to-discover for selected activities.
traversal_h = read(resolve_source("ShireTraversalChallenge.h"))
traversal_cpp = read(resolve_source("ShireTraversalChallenge.cpp"))
shire_builder_pg81 = read(resolve_source("ShirePrototypeWorldBuilder.cpp"))
fellowship_builder_pg81 = read(resolve_source("FellowshipChapterWorldBuilder.cpp"))
for symbol in ["ConfigureChallenge","HandleGateOverlap","CurrentGateIndex","RegisterJourneyDiscovery","TraversalChallenge: PASS"]:
    if symbol not in (traversal_h + traversal_cpp):
        fail(f"PG-081: traversal runtime symbol missing {symbol}")
for discovery_id in ["SHIRE_FIELD_RACE","MORIA_ECHO_ROUTE"]:
    if discovery_id not in (shire_builder_pg81 + fellowship_builder_pg81):
        fail(f"PG-081: traversal challenge placement missing {discovery_id}")
if "AShireTraversalChallenge* FieldRace" not in shire_builder_pg81:
    fail("PG-081: Shire field race must use ordered traversal gates")
if "AShireTraversalChallenge* MoriaEchoPath" not in fellowship_builder_pg81:
    fail("PG-081: Moria echo path must use ordered traversal gates")

# PG-021: living-world plan must explicitly preserve the phased NPC/world intelligence roadmap.
living_world_path = ROOT / "Data" / "LivingWorldFeaturePlan.json"
living_world_data = {}
if not living_world_path.exists():
    fail("Living world feature plan missing: Data/LivingWorldFeaturePlan.json")
else:
    try:
        living_world_data = json.loads(read(living_world_path))
    except json.JSONDecodeError as exc:
        fail(f"Invalid Data/LivingWorldFeaturePlan.json: {exc}")

expected_lw_phases = set(guard_rules.get("living_world_phase_ids", []))
actual_lw_phases = {str(phase.get("id") or "").strip() for phase in living_world_data.get("phases", [])}
missing_lw_phases = sorted(expected_lw_phases - actual_lw_phases)
if missing_lw_phases:
    fail("LivingWorldFeaturePlan missing phases: " + ", ".join(missing_lw_phases))

lw_feature_ids: set[str] = set()
for phase in living_world_data.get("phases", []):
    phase_id = str(phase.get("id") or "").strip()
    for feature in phase.get("features", []):
        feature_id = str(feature.get("id") or "").strip()
        status = str(feature.get("status") or "").strip()
        if not feature_id:
            fail(f"Living world phase {phase_id} has a feature without id")
            continue
        if feature_id in lw_feature_ids:
            fail(f"Duplicate living world feature id: {feature_id}")
        lw_feature_ids.add(feature_id)
        if not status:
            fail(f"Living world feature {feature_id} has no status")

for required_feature in [
    "LW-AWARENESS", "LW-ROUTINES", "LW-SOCIAL-PAUSE",
    "NPC-CONVERSATION-RUNTIME", "NPC-MEMORY-SCHEMA",
    "WORLD-MICRO-EVENTS", "WORLD-FAUNA", "WORLD-MOTION",
    "NPC-KNOWLEDGE-GUARD"
]:
    if required_feature not in lw_feature_ids:
        fail(f"Living world plan missing required feature contract: {required_feature}")

# PG-022: film-first adaptation must keep machine-readable film-to-game coverage.
film_plan_path = ROOT / "Data" / "FilmExperiencePlan.json"
film_plan = {}
if not film_plan_path.exists():
    fail("Film experience plan missing: Data/FilmExperiencePlan.json")
else:
    try:
        film_plan = json.loads(read(film_plan_path))
    except json.JSONDecodeError as exc:
        fail(f"Invalid Data/FilmExperiencePlan.json: {exc}")

film_chapters = film_plan.get("chapters", [])
covered_frodo_chapters: set[str] = set()
covered_routes: set[str] = set()
film_anchor_ids: set[str] = set()
for index, chapter_entry in enumerate(film_chapters, start=1):
    chapter = str(chapter_entry.get("chapter") or "").strip()
    route = str(chapter_entry.get("route") or "").strip()
    anchors = chapter_entry.get("anchors", [])
    if not chapter or not route or not isinstance(anchors, list) or not anchors:
        fail(f"FilmExperiencePlan chapter entry {index} is incomplete")
        continue
    covered_routes.add(route)
    if route == "FrodoMain":
        covered_frodo_chapters.add(chapter)
    for anchor in anchors:
        anchor_id = str(anchor.get("id") or "").strip()
        label = str(anchor.get("label") or "").strip()
        canon_class = str(anchor.get("canon_class") or "").strip()
        coverage = str(anchor.get("coverage") or "").strip()
        treatment = anchor.get("treatment", [])
        if not anchor_id or not label or not canon_class or not coverage or not treatment:
            fail(f"FilmExperiencePlan anchor in {chapter}/{route} is incomplete")
            continue
        if anchor_id in film_anchor_ids:
            fail(f"Duplicate FilmExperiencePlan anchor id: {anchor_id}")
        film_anchor_ids.add(anchor_id)
        if canon_class not in set(guard_rules.get("canon_classes", [])):
            fail(f"FilmExperiencePlan anchor {anchor_id} uses unknown canon class '{canon_class}'")

expected_film_chapters = set(guard_rules.get("film_experience_required_chapters", []))
missing_film_chapters = sorted(expected_film_chapters - covered_frodo_chapters)
if missing_film_chapters:
    fail("FilmExperiencePlan missing FrodoMain chapter coverage: " + ", ".join(missing_film_chapters))

expected_film_routes = set(guard_rules.get("film_experience_required_routes", []))
missing_film_routes = sorted(expected_film_routes - covered_routes)
if missing_film_routes:
    fail("FilmExperiencePlan missing required routes: " + ", ".join(missing_film_routes))

# PG-032: Part I character population and visual-tier contract must stay complete.
population_plan_path = ROOT / "Data" / "CharacterPopulationPlan.json"
population_plan = {}
if not population_plan_path.exists():
    fail("Character population plan missing: Data/CharacterPopulationPlan.json")
else:
    try:
        population_plan = json.loads(read(population_plan_path))
    except json.JSONDecodeError as exc:
        fail(f"Invalid Data/CharacterPopulationPlan.json: {exc}")

population_ids: set[str] = set()
allowed_visual_tiers = set(population_plan.get("visual_tiers", []))
for index, item in enumerate(population_plan.get("core_cast", []), start=1):
    cast_id = str(item.get("id") or "").strip()
    display_name = str(item.get("display_name") or "").strip()
    visual_tier = str(item.get("visual_tier") or "").strip()
    chapters = item.get("chapters", [])
    if not cast_id or not display_name or not visual_tier or not chapters:
        fail(f"CharacterPopulationPlan core cast entry {index} is incomplete")
        continue
    if cast_id in population_ids:
        fail(f"Duplicate CharacterPopulationPlan cast id: {cast_id}")
    population_ids.add(cast_id)
    if visual_tier not in allowed_visual_tiers:
        fail(f"CharacterPopulationPlan {cast_id} uses unknown visual tier '{visual_tier}'")

missing_population_ids = sorted(set(guard_rules.get("character_population_required_ids", [])) - population_ids)
if missing_population_ids:
    fail("CharacterPopulationPlan missing required cast ids: " + ", ".join(missing_population_ids))

chapter_contracts = population_plan.get("chapter_cast_contracts", [])
population_chapters = {str(item.get("chapter") or "").strip() for item in chapter_contracts}
missing_population_chapters = sorted(
    set(guard_rules.get("character_population_required_chapters", [])) - population_chapters
)
if missing_population_chapters:
    fail("CharacterPopulationPlan missing chapter contracts: " + ", ".join(missing_population_chapters))

for entry in chapter_contracts:
    chapter = str(entry.get("chapter") or "").strip()
    required_named = entry.get("required_named", [])
    if not required_named:
        fail(f"CharacterPopulationPlan chapter {chapter} has no required_named cast")
    for cast_id in required_named:
        if cast_id not in population_ids:
            fail(f"CharacterPopulationPlan chapter {chapter} references unknown cast id {cast_id}")

population_runtime_source = "\n".join([
    read(resolve_source("ShirePlayerCharacter.cpp")),
    read(resolve_source("ShirePrototypeWorldBuilder.cpp")),
    read(resolve_source("BreePrototypeWorldBuilder.cpp")),
    read(resolve_source("FellowshipChapterWorldBuilder.cpp")),
    read(resolve_source("IsengardPrototypeWorldBuilder.cpp")),
])
for item in population_plan.get("core_cast", []):
    display_name = str(item.get("display_name") or "").strip()
    aliases = [str(value).strip() for value in item.get("aliases", []) if str(value).strip()]
    names = [display_name] + aliases
    if not any(f'TEXT("{name}")' in population_runtime_source for name in names):
        fail(f"CharacterPopulationPlan cast has no runtime source representation: {display_name}")

npc_cpp_for_population = read(resolve_source("ShireNPC.cpp"))
npc_h_for_population = read(resolve_source("ShireNPC.h"))
ambient_cpp_for_population = read(resolve_source("ShireAmbientNPC.cpp"))
bree_cpp_for_population = read(resolve_source("BreePrototypeWorldBuilder.cpp"))
fellowship_cpp_for_population = read(resolve_source("FellowshipChapterWorldBuilder.cpp"))
for symbol in ["StopFollowingStoryBeat", "HasStoryBeatTriggered(StopFollowingStoryBeat)"]:
    if symbol not in npc_cpp_for_population and symbol not in npc_h_for_population:
        fail(f"PG-032 story-aware companion release missing: {symbol}")
if 'RoutineRole = TEXT("BreeTownsperson")' not in bree_cpp_for_population:
    fail("PG-032 Bree ambient population lost BreeTownsperson role")
if 'RoutineRole = TEXT("Elf")' not in fellowship_cpp_for_population:
    fail("PG-032 Rivendell/Lothlorien ambient population lost Elf role")
for symbol in ["VisualTorsoBaseZ", "VisualHeadBaseZ", "VisualHairBaseZ"]:
    if symbol not in ambient_cpp_for_population:
        fail(f"PG-032 ambient role-specific visual base missing: {symbol}")

# PG-036: ambient micro-life must remain role-driven and reuse the cheap ambient actor.
ambient_life_cpp = read(resolve_source("ShireAmbientNPC.cpp"))
ambient_life_h = read(resolve_source("ShireAmbientNPC.h"))
shire_life_cpp = read(resolve_source("ShirePrototypeWorldBuilder.cpp"))
bree_life_cpp = read(resolve_source("BreePrototypeWorldBuilder.cpp"))
fellowship_life_cpp = read(resolve_source("FellowshipChapterWorldBuilder.cpp"))

for symbol in [
    "ActivityPropType",
    "ActivityProp",
    "ActivityPhase",
    "ActivityPropBase",
    "bSocializing",
]:
    if symbol not in ambient_life_cpp and symbol not in ambient_life_h:
        fail(f"PG-036 ambient micro-life invariant missing: {symbol}")

for prop in ["Basket", "Crate", "Satchel", "Mug", "Book", "Lantern"]:
    if f'TEXT("{prop}")' not in ambient_life_cpp:
        fail(f"PG-036 ambient activity prop style missing: {prop}")

living_world_life_cpp = read(resolve_source("LivingWorldDirector.cpp"))
for role_marker in [
    'RoleName == TEXT("PartyGuest") || RoleName == TEXT("InnGuest")',
    'RoleName == TEXT("BreeCourier") || RoleName == TEXT("RoadWalker")',
    'RoleName == TEXT("FieldWorker") || RoleName == TEXT("Gardener")',
    'RoleName == TEXT("FerryWorker") || RoleName == TEXT("GateWorker")',
]:
    if role_marker not in living_world_life_cpp:
        fail(f"PG-036 director-owned Shire role activity mapping missing: {role_marker}")
for prop_marker in [
    'FName(TEXT("Mug"))',
    'TEXT("Satchel")',
    'FName(TEXT("Basket"))',
    'FName(TEXT("Crate"))',
    'FName(TEXT("Lantern"))',
]:
    if prop_marker not in living_world_life_cpp:
        fail(f"PG-036 director-owned ambient prop mapping missing: {prop_marker}")

if "Townsperson->ActivityPropType" not in bree_life_cpp:
    fail("PG-036 Bree townspeople lost visible activity assignments")
if "Resident->ActivityPropType" not in fellowship_life_cpp:
    fail("PG-036 Elven residents lost visible activity assignments")

# PG-035: lightweight world motion must remain cheap, 3D and region-aware.
ambient_motion_cpp = read(resolve_source("ShireAmbientNPC.cpp"))
shire_world_motion_cpp = read(resolve_source("ShirePrototypeWorldBuilder.cpp"))
bree_world_motion_cpp = read(resolve_source("BreePrototypeWorldBuilder.cpp"))
fellowship_world_motion_cpp = read(resolve_source("FellowshipChapterWorldBuilder.cpp"))
isengard_world_motion_cpp = read(resolve_source("IsengardPrototypeWorldBuilder.cpp"))

for symbol in [
    'RoutineRole == TEXT("Bird")',
    "AddActorWorldOffset(Direction * WalkSpeed * DeltaSeconds, false)",
    "WalkPhase += DeltaSeconds * 9.0f",
]:
    if symbol not in ambient_motion_cpp:
        fail(f"PG-035 lightweight bird-motion invariant missing: {symbol}")

# P1C01 Shire ambient life is director-owned after W01 crowd ownership convergence.
# Prove sky-life through the data-owned fauna contract instead of requiring a
# second builder-owned permanent bird population.
pg035_event_plan = json.loads(read(ROOT / "Data" / "LivingWorldEventPlan.json"))
pg035_shire_contract = next(
    (row for row in pg035_event_plan.get("chapter_contracts", [])
     if isinstance(row, dict) and row.get("chapter") == "P1C01"),
    {},
)
if "FAUNA" not in set(pg035_shire_contract.get("allowed", [])):
    fail("PG-035 Shire lost director-owned fauna eligibility")
pg035_bird_template = next(
    (row for row in pg035_event_plan.get("event_templates", [])
     if isinstance(row, dict) and row.get("id") == "EVT_FAUNA_BIRDS"),
    {},
)
if "P1C01" not in set(pg035_bird_template.get("regions", [])):
    fail("PG-035 Shire lost lightweight bird event coverage")

for source_name, source_text in [
    ("Bree", bree_world_motion_cpp),
    ("Fellowship outdoor regions", fellowship_world_motion_cpp),
    ("Isengard", isengard_world_motion_cpp),
]:
    if 'RoutineRole = TEXT("Bird")' not in source_text:
        fail(f"PG-035 {source_name} lost lightweight outdoor sky-life population")

if "Distance > DormantTickDistance ? 0.75f" not in ambient_motion_cpp:
    fail("PG-035 Bird role must continue using the distance-throttled ambient actor tick budget")

# PG-034: Part I batch-build world detail must keep chapter-specific visual-density markers.
bree_world_cpp = read(resolve_source("BreePrototypeWorldBuilder.cpp"))
fellowship_world_cpp = read(resolve_source("FellowshipChapterWorldBuilder.cpp"))
for symbol in [
    "Street-life pass: stalls, rain puddles, lantern posts, crates and hitching details.",
    "Reeds, low rocks and abandoned camp remains keep the marsh approach from feeling empty.",
    "Garden paths, arcades and resting places make the valley read as an inhabited refuge.",
    "Loose scree, cairns and route markers increase mountain scale without expensive simulation.",
    "Pillar forest and cold braziers make the halls feel architectural rather than a single tunnel.",
    "Talan platforms, rope-bridge proxies and warm lights make the canopy feel inhabited vertically.",
    "Boat silhouettes, reeds and shoreline camps make the river journey feel travelled rather than empty.",
    "Amon Hen stair fragments and broken lookout stones make the final arena readable from the river.",
]:
    if symbol not in bree_world_cpp and symbol not in fellowship_world_cpp:
        fail(f"PG-034 Part I world-detail marker missing: {symbol}")

# PG-033: core-cast visual identity must remain distinct without pretending proxies are final art.
npc_visual_cpp = read(resolve_source("ShireNPC.cpp"))
npc_visual_h = read(resolve_source("ShireNPC.h"))
for symbol in [
    "PrototypeCloak",
    "PrototypePrimaryProp",
    "PrototypeSecondaryProp",
    "PrototypeBeard",
    "PrototypeHeadpiece",
    'Name.Equals(TEXT("Sam")',
    'Name.Equals(TEXT("Merry")',
    'Name.Equals(TEXT("Pippin")',
    'Name.Equals(TEXT("Boromir")',
    'Name.Equals(TEXT("Legolas")',
    'Name.Equals(TEXT("Gimli")',
    'Name.Equals(TEXT("Galadriel")',
]:
    if symbol not in npc_visual_cpp and symbol not in npc_visual_h:
        fail(f"PG-033 core-cast visual identity invariant missing: {symbol}")

population_identity = population_plan.get("visual_identity_pass", {}) if population_plan else {}
population_proof = str(population_identity.get("proof_limit") or "")
if not population_proof or ("final" not in population_proof.lower()) or ("modular" not in population_proof.lower() and "not final" not in population_proof.lower()):
    fail("PG-033 CharacterPopulationPlan must preserve proxy/production-archetype versus final-art proof boundary")

for pg033_error in validate_development_mode(governor_data):
    fail("PG-033 " + pg033_error)

# PG-024: NPC identity/schedule/relationship data must stay coherent before runtime intelligence consumes it.
npc_social_path = ROOT / "Data" / "NPCSocialModel.json"
npc_social = {}
if not npc_social_path.exists():
    fail("NPC social model missing: Data/NPCSocialModel.json")
else:
    try:
        npc_social = json.loads(read(npc_social_path))
    except json.JSONDecodeError as exc:
        fail(f"Invalid Data/NPCSocialModel.json: {exc}")

profile_ids: set[str] = set()
profile_aliases: set[str] = set()
for index, profile in enumerate(npc_social.get("profiles", []), start=1):
    profile_id = str(profile.get("id") or "").strip()
    display_name = str(profile.get("display_name") or "").strip()
    profile_type = str(profile.get("type") or "").strip()
    regions = profile.get("regions", [])
    roles = profile.get("roles", [])
    knowledge_tags = profile.get("knowledge_tags", [])

    if not profile_id or not display_name or not profile_type:
        fail(f"NPCSocialModel profile entry {index} is missing id/display_name/type")
        continue
    if profile_id in profile_ids:
        fail(f"Duplicate NPCSocialModel profile id: {profile_id}")
    profile_ids.add(profile_id)

    if profile_type not in set(npc_social.get("profile_types", [])):
        fail(f"NPCSocialModel profile {profile_id} uses unknown type '{profile_type}'")
    if not isinstance(regions, list) or not regions:
        fail(f"NPCSocialModel profile {profile_id} has no region coverage")
    if not isinstance(roles, list) or not roles:
        fail(f"NPCSocialModel profile {profile_id} has no roles")
    if not isinstance(knowledge_tags, list):
        fail(f"NPCSocialModel profile {profile_id} knowledge_tags must be a list")

    for alias in profile.get("aliases", []):
        alias_key = str(alias).strip().lower()
        if not alias_key:
            fail(f"NPCSocialModel profile {profile_id} contains empty alias")
        elif alias_key in profile_aliases:
            fail(f"Duplicate NPCSocialModel alias: {alias}")
        else:
            profile_aliases.add(alias_key)

required_named_profiles = set(guard_rules.get("npc_social_required_named_ids", []))
missing_named_profiles = sorted(required_named_profiles - profile_ids)
if missing_named_profiles:
    fail("NPCSocialModel missing required named profiles: " + ", ".join(missing_named_profiles))

valid_actor_ids = profile_ids | set(npc_social.get("external_actor_ids", []))
relationship_pairs: set[tuple[str, str, str]] = set()
for rel in npc_social.get("relationships", []):
    source = str(rel.get("from") or "").strip()
    target = str(rel.get("to") or "").strip()
    rel_type = str(rel.get("type") or "").strip()
    if source not in valid_actor_ids:
        fail(f"NPCSocialModel relationship references unknown source: {source}")
    if target not in valid_actor_ids:
        fail(f"NPCSocialModel relationship references unknown target: {target}")
    if rel_type not in set(npc_social.get("relationship_types", [])):
        fail(f"NPCSocialModel relationship {source}->{target} uses unknown type '{rel_type}'")
    key = (source, target, rel_type)
    if key in relationship_pairs:
        fail(f"Duplicate NPCSocialModel relationship: {source}->{target} ({rel_type})")
    relationship_pairs.add(key)

schedule_ids: set[str] = set()
scheduled_profiles: set[str] = set()
for schedule in npc_social.get("schedule_templates", []):
    schedule_id = str(schedule.get("id") or "").strip()
    if not schedule_id:
        fail("NPCSocialModel schedule template missing id")
        continue
    if schedule_id in schedule_ids:
        fail(f"Duplicate NPCSocialModel schedule template id: {schedule_id}")
    schedule_ids.add(schedule_id)

    total_weight = 0.0
    for phase in schedule.get("phases", []):
        phase_id = str(phase.get("phase") or "").strip()
        if phase_id not in set(npc_social.get("schedule_phase_types", [])):
            fail(f"NPCSocialModel schedule {schedule_id} uses unknown phase '{phase_id}'")
        try:
            total_weight += float(phase.get("weight", 0.0))
        except (TypeError, ValueError):
            fail(f"NPCSocialModel schedule {schedule_id} has invalid phase weight")
    if abs(total_weight - 1.0) > 0.001:
        fail(f"NPCSocialModel schedule {schedule_id} phase weights must sum to 1.0 (got {total_weight:.3f})")

    for profile_id in schedule.get("applies_to", []):
        if profile_id not in profile_ids:
            fail(f"NPCSocialModel schedule {schedule_id} references unknown profile {profile_id}")
        if profile_id in scheduled_profiles:
            fail(f"NPCSocialModel profile {profile_id} appears in multiple schedule templates")
        scheduled_profiles.add(profile_id)

unscheduled_profiles = sorted(profile_ids - scheduled_profiles)
if unscheduled_profiles:
    fail("NPCSocialModel profiles missing schedule assignment: " + ", ".join(unscheduled_profiles))

# PG-025/028/029/030: remote-safe living-world contracts must stay bounded and coherent.
npc_conversation_path = ROOT / "Data" / "NPCConversationPlan.json"
npc_conversation = {}
if not npc_conversation_path.exists():
    fail("NPC conversation plan missing: Data/NPCConversationPlan.json")
else:
    try:
        npc_conversation = json.loads(read(npc_conversation_path))
    except json.JSONDecodeError as exc:
        fail(f"Invalid Data/NPCConversationPlan.json: {exc}")

npc_profile_ids = {str(p.get("id") or "").strip() for p in npc_social.get("profiles", [])}
intent_ids: set[str] = set()
for item in npc_conversation.get("intent_contracts", []):
    intent_id = str(item.get("id") or "").strip()
    if not intent_id:
        fail("NPCConversationPlan intent contract missing id")
        continue
    if intent_id in intent_ids:
        fail(f"Duplicate NPCConversationPlan intent id: {intent_id}")
    intent_ids.add(intent_id)

conversation_set_ids: set[str] = set()
for convo in npc_conversation.get("conversation_sets", []):
    convo_id = str(convo.get("id") or "").strip()
    if not convo_id:
        fail("NPCConversationPlan conversation set missing id")
        continue
    if convo_id in conversation_set_ids:
        fail(f"Duplicate NPCConversationPlan conversation set id: {convo_id}")
    conversation_set_ids.add(convo_id)
    for profile_id in convo.get("participant_filters", {}).get("allowed_profiles", []):
        if profile_id not in npc_profile_ids:
            fail(f"NPCConversationPlan {convo_id} references unknown profile {profile_id}")
    for intent_id in convo.get("intents", []):
        if intent_id not in intent_ids:
            fail(f"NPCConversationPlan {convo_id} references unknown intent {intent_id}")
    if int(convo.get("max_exchange_turns", 0)) <= 0:
        fail(f"NPCConversationPlan {convo_id} must have positive max_exchange_turns")

missing_conversation_sets = sorted(set(guard_rules.get("npc_conversation_required_sets", [])) - conversation_set_ids)
if missing_conversation_sets:
    fail("NPCConversationPlan missing required sets: " + ", ".join(missing_conversation_sets))

speaker_rules = npc_conversation.get("speaker_rules", {})
if int(speaker_rules.get("max_active_conversations_near_player", 0)) < 1:
    fail("NPCConversationPlan must allow and cap near-player conversations")
if int(speaker_rules.get("max_participants_per_conversation", 0)) != 2:
    fail("NPCConversationPlan currently requires two-participant conversations")
if not speaker_rules.get("story_critical_preempts_ambient", False):
    fail("NPCConversationPlan must let story-critical dialogue preempt ambient chatter")
if not speaker_rules.get("danger_override_preempts_social", False):
    fail("NPCConversationPlan must let danger override ambient social chatter")

npc_memory_path = ROOT / "Data" / "NPCMemoryPlan.json"
npc_memory = {}
if not npc_memory_path.exists():
    fail("NPC memory plan missing: Data/NPCMemoryPlan.json")
else:
    try:
        npc_memory = json.loads(read(npc_memory_path))
    except json.JSONDecodeError as exc:
        fail(f"Invalid Data/NPCMemoryPlan.json: {exc}")

memory_template_ids: set[str] = set()
for item in npc_memory.get("memory_templates", []):
    memory_id = str(item.get("id") or "").strip()
    tier = str(item.get("tier") or "").strip()
    scope = str(item.get("default_scope") or "").strip()
    if not memory_id:
        fail("NPCMemoryPlan memory template missing id")
        continue
    if memory_id in memory_template_ids:
        fail(f"Duplicate NPCMemoryPlan memory template id: {memory_id}")
    memory_template_ids.add(memory_id)
    if tier not in set(npc_memory.get("memory_tiers", [])):
        fail(f"NPCMemoryPlan {memory_id} uses unknown tier '{tier}'")
    if scope not in set(npc_memory.get("persistence_scopes", [])):
        fail(f"NPCMemoryPlan {memory_id} uses unknown scope '{scope}'")

missing_memory_templates = sorted(set(guard_rules.get("npc_memory_required_templates", [])) - memory_template_ids)
if missing_memory_templates:
    fail("NPCMemoryPlan missing required templates: " + ", ".join(missing_memory_templates))

memory_policies = npc_memory.get("policies", {})
for key in ["store_compact_event_ids_only", "never_persist_raw_dialogue_text", "aliases_share_one_identity_memory", "mandatory_story_outcomes_are_immutable"]:
    if not memory_policies.get(key, False):
        fail(f"NPCMemoryPlan policy must remain true: {key}")
save_contract = npc_memory.get("save_contract", {})
soft_budget = int(save_contract.get("estimated_soft_budget_kb", 0))
if soft_budget <= 0 or soft_budget > 256:
    fail("NPCMemoryPlan save soft budget must be within 1..256 KB")
if not save_contract.get("route_partitioned", False) or not save_contract.get("versioned_schema", False):
    fail("NPCMemoryPlan save contract must be route-partitioned and versioned")

living_event_path = ROOT / "Data" / "LivingWorldEventPlan.json"
living_events = {}
if not living_event_path.exists():
    fail("Living world event plan missing: Data/LivingWorldEventPlan.json")
else:
    try:
        living_events = json.loads(read(living_event_path))
    except json.JSONDecodeError as exc:
        fail(f"Invalid Data/LivingWorldEventPlan.json: {exc}")

event_ids: set[str] = set()
for event in living_events.get("event_templates", []):
    event_id = str(event.get("id") or "").strip()
    event_type = str(event.get("type") or "").strip()
    if not event_id:
        fail("LivingWorldEventPlan event template missing id")
        continue
    if event_id in event_ids:
        fail(f"Duplicate LivingWorldEventPlan event id: {event_id}")
    event_ids.add(event_id)
    if event_type not in set(living_events.get("event_types", [])):
        fail(f"LivingWorldEventPlan {event_id} uses unknown type '{event_type}'")
    if not event.get("story_safe", False):
        fail(f"LivingWorldEventPlan event must be story-safe: {event_id}")

covered_event_chapters = {str(item.get("chapter") or "").strip() for item in living_events.get("chapter_contracts", [])}
missing_event_chapters = sorted(set(guard_rules.get("living_world_event_required_chapters", [])) - covered_event_chapters)
if missing_event_chapters:
    fail("LivingWorldEventPlan missing chapter contracts: " + ", ".join(missing_event_chapters))
event_budget = living_events.get("region_budgets", {})
if int(event_budget.get("max_active_micro_events_near_player", 0)) > 4:
    fail("LivingWorldEventPlan active micro-event cap exceeds low-spec budget")
if int(event_budget.get("max_active_fauna_groups_near_player", 0)) > 2:
    fail("LivingWorldEventPlan fauna cap exceeds low-spec budget")
if str(event_budget.get("offscreen_simulation") or "") != "STATE_ONLY":
    fail("LivingWorldEventPlan offscreen simulation must remain STATE_ONLY")

bounded_dialogue_path = ROOT / "Data" / "BoundedDialoguePlan.json"
bounded_dialogue = {}
if not bounded_dialogue_path.exists():
    fail("Bounded dialogue plan missing: Data/BoundedDialoguePlan.json")
else:
    try:
        bounded_dialogue = json.loads(read(bounded_dialogue_path))
    except json.JSONDecodeError as exc:
        fail(f"Invalid Data/BoundedDialoguePlan.json: {exc}")

bounded_intents = {str(item.get("intent") or "").strip() for item in bounded_dialogue.get("intent_policies", [])}
missing_bounded_intents = sorted(set(guard_rules.get("bounded_dialogue_required_intents", [])) - bounded_intents)
if missing_bounded_intents:
    fail("BoundedDialoguePlan missing required intents: " + ", ".join(missing_bounded_intents))
dialogue_limits = bounded_dialogue.get("limits", {})
if int(dialogue_limits.get("max_words_ambient_line", 0)) > 30:
    fail("BoundedDialoguePlan ambient line limit exceeds project bound")
if not dialogue_limits.get("deterministic_fallback_required", False):
    fail("BoundedDialoguePlan must require deterministic fallback")
if int(dialogue_limits.get("generation_timeout_ms_target", -1)) != 0:
    fail("BoundedDialoguePlan must not require runtime generation latency")
knowledge_guard = bounded_dialogue.get("knowledge_guard", {})
if knowledge_guard.get("default") != "DENY_UNLISTED" or knowledge_guard.get("cross_route_knowledge_default") != "DENY":
    fail("BoundedDialoguePlan knowledge guard must default-deny unlisted and cross-route knowledge")

# PG-046: major Part I threat silhouettes must use dedicated production meshes before primitive fallback.
enemy_assets = {
    "BlackRider": ["SM_BlackRider_Horse.obj", "SM_BlackRider_Rider.obj", "SM_BlackRider_Head.obj"],
    "Orc": ["SM_Orc_Torso.obj", "SM_Orc_Head.obj", "SM_Orc_Arm.obj", "SM_Orc_Leg.obj", "SM_Orc_Weapon.obj"],
    "UrukHai": ["SM_UrukHai_Torso.obj", "SM_UrukHai_Head.obj", "SM_UrukHai_Arm.obj", "SM_UrukHai_Leg.obj", "SM_UrukHai_Weapon.obj"],
    "CaveTroll": ["SM_CaveTroll_Torso.obj", "SM_CaveTroll_Head.obj", "SM_CaveTroll_Arm.obj", "SM_CaveTroll_Leg.obj", "SM_CaveTroll_Weapon.obj"],
}
for folder_name, asset_names in enemy_assets.items():
    enemy_root = ROOT / "SourceAssets" / "Production" / "Enemies" / folder_name
    for asset_name in asset_names:
        if not (enemy_root / asset_name).exists():
            fail(f"PG-046 enemy production asset missing: {folder_name}/{asset_name}")

black_rider_cpp = read(resolve_source("BlackRiderPrototype.cpp"))
for symbol in ["SM_BlackRider_Horse", "SM_BlackRider_Rider", "SM_BlackRider_Head"]:
    if symbol not in black_rider_cpp:
        fail(f"PG-046 Black Rider production runtime missing: {symbol}")

enemy_cpp = read(resolve_source("FellowshipEnemyPrototype.cpp"))
for symbol in [
    'ProductionFolder = TEXT("Orc")',
    'ProductionFolder = TEXT("UrukHai")',
    'ProductionFolder = TEXT("CaveTroll")',
    '/Game/Production/Enemies/%s/SM_%s_',
]:
    if symbol not in enemy_cpp:
        fail(f"PG-046 Fellowship enemy production runtime missing: {symbol}")

threat_plan = population_plan.get("threat_cast", []) if population_plan else []
for threat in threat_plan:
    if threat.get("visual_tier") != "PRODUCTION_DEDICATED":
        fail(f"PG-046 threat not promoted to PRODUCTION_DEDICATED: {threat.get('id')}")

# PG-045: every named Part I cast member must keep a dedicated modular visual identity.
dedicated_named_assets = {
    "Bilbo": ["SM_Bilbo_Torso.obj", "SM_Bilbo_Head.obj", "SM_Bilbo_Hair.obj"],
    "Boromir": ["SM_Boromir_Torso.obj", "SM_Boromir_Head.obj", "SM_Boromir_Hair.obj"],
    "Legolas": ["SM_Legolas_Torso.obj", "SM_Legolas_Head.obj", "SM_Legolas_Hair.obj"],
    "Gimli": ["SM_Gimli_Torso.obj", "SM_Gimli_Head.obj", "SM_Gimli_Hair.obj"],
    "Arwen": ["SM_Arwen_Torso.obj", "SM_Arwen_Head.obj", "SM_Arwen_Hair.obj"],
    "Elrond": ["SM_Elrond_Torso.obj", "SM_Elrond_Head.obj", "SM_Elrond_Hair.obj"],
    "Haldir": ["SM_Haldir_Torso.obj", "SM_Haldir_Head.obj", "SM_Haldir_Hair.obj"],
    "Galadriel": ["SM_Galadriel_Torso.obj", "SM_Galadriel_Head.obj", "SM_Galadriel_Hair.obj"],
    "Saruman": ["SM_Saruman_Torso.obj", "SM_Saruman_Head.obj", "SM_Saruman_Hair.obj"],
    "Butterbur": ["SM_Butterbur_Torso.obj", "SM_Butterbur_Head.obj", "SM_Butterbur_Hair.obj"],
    "GateKeeper": ["SM_GateKeeper_Torso.obj", "SM_GateKeeper_Head.obj", "SM_GateKeeper_Hair.obj"],
    "Hamfast": ["SM_Hamfast_Torso.obj", "SM_Hamfast_Head.obj", "SM_Hamfast_Hair.obj"],
    "Rosie": ["SM_Rosie_Torso.obj", "SM_Rosie_Head.obj", "SM_Rosie_Hair.obj"],
    "FarmerMaggot": ["SM_FarmerMaggot_Torso.obj", "SM_FarmerMaggot_Head.obj", "SM_FarmerMaggot_Hair.obj"],
}
for folder_name, asset_names in dedicated_named_assets.items():
    character_root = ROOT / "SourceAssets" / "Production" / "Characters" / folder_name
    for asset_name in asset_names:
        if not (character_root / asset_name).exists():
            fail(f"PG-045 dedicated named character asset missing: {folder_name}/{asset_name}")

named_visual_cpp = read(resolve_source("ShireNPC.cpp"))
for folder_name in dedicated_named_assets:
    if f'DedicatedFolder = TEXT("{folder_name}")' not in named_visual_cpp:
        fail(f"PG-045 runtime dedicated-folder mapping missing: {folder_name}")

character_plan_core = population_plan.get("core_cast", []) if population_plan else []
for character in character_plan_core:
    if character.get("visual_tier") != "PRODUCTION_DEDICATED":
        fail(f"PG-045 named cast not promoted to PRODUCTION_DEDICATED: {character.get('id')}")

dialogue_context_cpp = read(resolve_source("ShireNPCContextSubsystem.cpp"))
for profile_id in [
    "NPC_BILBO","NPC_ARWEN","NPC_ELROND","NPC_SARUMAN",
    "NPC_HAMFAST_GAMGEE","NPC_ROSIE_COTTON","NPC_FARMER_MAGGOT",
    "NPC_BARLIMAN_BUTTERBUR","NPC_BREE_GATEKEEPER","NPC_HALDIR","NPC_GALADRIEL"
]:
    if profile_id not in dialogue_context_cpp:
        fail(f"PG-045 expanded named dialogue coverage missing: {profile_id}")

# PG-044: backend hardening must keep NPC context, memory, dialogue and save contracts connected.
backend_context_h = read(resolve_source("ShireNPCContextSubsystem.h"))
backend_context_cpp = read(resolve_source("ShireNPCContextSubsystem.cpp"))
backend_quest_h = read(resolve_source("ShireQuestSubsystem.h"))
backend_quest_cpp = read(resolve_source("ShireQuestSubsystem.cpp"))
backend_npc_cpp = read(resolve_source("ShireNPC.cpp"))
backend_ambient_cpp = read(resolve_source("ShireAmbientNPC.cpp"))
backend_dialogue_h = read(resolve_source("ShireDialogueSubsystem.h"))
backend_dialogue_cpp = read(resolve_source("ShireDialogueSubsystem.cpp"))
backend_save_h = read(resolve_source("ShireSaveGame.h"))
backend_player_cpp = read(resolve_source("ShirePlayerCharacter.cpp"))
backend_build_cs = read(resolve_source("ShireJourney.Build.cs"))

for symbol in [
    "ResolveCanonicalProfileId",
    "GetPersistentMemoryBudget",
    "GetRelationshipBudget",
    "ResolveSchedulePhase",
    "SelectBoundedDialogue",
    "IsDangerStateActive",
    "IsInclementWeather",
]:
    if symbol not in backend_context_h or symbol not in backend_context_cpp:
        fail(f"PG-044 NPC context runtime missing symbol: {symbol}")

for symbol in [
    "ResolveCanonicalNPCProfile",
    "PruneNPCMemoryForCurrentChapter",
    "RecordStoryBeatForEligibleNPCs",
    "HasRecentNPCDialogueVariant",
    "RecordNamedNPCDialogueUse",
    "GetNamedNPCRelationship",
]:
    if symbol not in backend_quest_h or symbol not in backend_quest_cpp:
        fail(f"PG-044 NPC memory hardening missing symbol: {symbol}")

for invariant in [
    'Tier == TEXT("NAMED_STORY")',
    'Tier == TEXT("NAMED_LIGHT")',
    "return 12;",
    "return 4;",
    "return 8;",
    "return 3;",
    "CurrentOrdinal - EventOrdinal > 2",
    "Event.Priority >= 80",
]:
    if invariant not in (backend_context_cpp + backend_quest_cpp):
        fail(f"PG-044 memory budget/expiry invariant missing: {invariant}")

for symbol in [
    "PlayDynamicLine",
    "PlayDynamicSequence",
]:
    if symbol not in backend_dialogue_h or symbol not in backend_dialogue_cpp:
        fail(f"PG-044 dynamic dialogue transport missing: {symbol}")

for symbol in [
    "UpdateCompanionBanter",
    "COMPANION_BANTER",
    "TActorIterator<AShireNPC>",
    "PLAYER_INTERACTED",
    "AdjustNamedNPCRelationship",
]:
    if symbol not in backend_npc_cpp:
        fail(f"PG-044 named NPC integration missing: {symbol}")

for symbol in [
    "UpdateScheduleContext",
    "ResolveRuntimeProfileHint",
    "DANGER_OVERRIDE",
    "IsInclementWeather",
]:
    if symbol not in backend_ambient_cpp:
        fail(f"PG-044 ambient schedule/reaction runtime missing: {symbol}")

for symbol in [
    "CurrentSchemaVersion = 6",
    "SaveSchemaVersion",
    "SnapshotCreatedUnixSeconds",
]:
    if symbol not in backend_save_h:
        fail(f"PG-044 versioned save contract missing: {symbol}")

for symbol in [
    "Save->SaveSchemaVersion = UShireSaveGame::CurrentSchemaVersion",
    "Save snapshot schema is newer than this build",
    "invalid numeric state",
]:
    if symbol not in backend_player_cpp:
        fail(f"PG-044 save hardening runtime missing: {symbol}")

for module_name in ["\"Json\"", "\"JsonUtilities\""]:
    if module_name not in backend_build_cs:
        fail(f"PG-044 JSON runtime dependency missing: {module_name}")

profiles = npc_social.get("profiles", []) if npc_social else []
profile_ids = {str(p.get("id") or "") for p in profiles}
aliases = {}
for profile in profiles:
    pid = str(profile.get("id") or "")
    display = str(profile.get("display_name") or "")
    for alias in [display, *profile.get("aliases", [])]:
        key = str(alias).strip().lower()
        if not key:
            continue
        if key in aliases and aliases[key] != pid:
            fail(f"PG-044 duplicate NPC alias/display mapping: {alias}")
        aliases[key] = pid

if aliases.get("strider") != "NPC_ARAGORN":
    fail("PG-044 Strider must canonically resolve to NPC_ARAGORN")

memory_policies = {
    p.get("profile_selector"): p for p in npc_memory.get("profile_memory_policy", [])
} if npc_memory else {}
if memory_policies.get("persistence_tier=NAMED_STORY", {}).get("persistent_budget") != 12:
    fail("PG-044 NAMED_STORY persistent budget drifted from 12")
if memory_policies.get("persistence_tier=NAMED_LIGHT", {}).get("persistent_budget") != 4:
    fail("PG-044 NAMED_LIGHT persistent budget drifted from 4")
if memory_policies.get("persistence_tier=AMBIENT_AGGREGATE", {}).get("persistent_budget") != 0:
    fail("PG-044 ambient archetypes must never receive persistent per-instance memory")

for conversation_set in npc_conversation.get("conversation_sets", []) if npc_conversation else []:
    allowed_profiles = conversation_set.get("participant_filters", {}).get("allowed_profiles", [])
    for profile_id in allowed_profiles:
        if profile_id not in profile_ids:
            fail(f"PG-044 conversation set references unknown profile: {profile_id}")

# PG-043: dedicated hero identity meshes must remain distinct and runtime-wired.
dedicated_characters = {
    "Sam": ["SM_Sam_Torso.obj", "SM_Sam_Head.obj", "SM_Sam_Hair.obj"],
    "Merry": ["SM_Merry_Torso.obj", "SM_Merry_Head.obj", "SM_Merry_Hair.obj"],
    "Pippin": ["SM_Pippin_Torso.obj", "SM_Pippin_Head.obj", "SM_Pippin_Hair.obj"],
    "Aragorn": ["SM_Aragorn_Torso.obj", "SM_Aragorn_Head.obj", "SM_Aragorn_Hair.obj"],
}
for character_name, asset_names in dedicated_characters.items():
    character_root = ROOT / "SourceAssets" / "Production" / "Characters" / character_name
    for asset_name in asset_names:
        if not (character_root / asset_name).exists():
            fail(f"PG-043 dedicated character asset missing: {character_name}/{asset_name}")

hero_visual_cpp = read(resolve_source("ShireNPC.cpp"))
for symbol in [
    "DedicatedFolder",
    'DedicatedFolder = TEXT("Sam")',
    'DedicatedFolder = TEXT("Merry")',
    'DedicatedFolder = TEXT("Pippin")',
    'DedicatedFolder = TEXT("Aragorn")',
    '/Game/Production/Characters/%s/SM_%s_Torso.SM_%s_Torso',
]:
    if symbol not in hero_visual_cpp:
        fail(f"PG-043 dedicated hero runtime reference missing: {symbol}")

dedicated_pass = population_plan.get("dedicated_modular_character_pass", {}) if population_plan else {}
if dedicated_pass.get("status") not in {
    "RUNTIME_IMPLEMENTED_PENDING_BUILD",
    "FULL_NAMED_CAST_RUNTIME_IMPLEMENTED_PENDING_BUILD",
}:
    fail("PG-043 dedicated modular character pass must stay explicitly build-pending until UE validation")
if "skeletal" not in str(dedicated_pass.get("proof_limit") or "").lower():
    fail("PG-043 dedicated character pass must preserve the skeletal/final-art proof boundary")

# PG-042: Part I regional production overlays must stay source-controlled and story-safe.
regional_assets = {
    "Weathertop": ["SM_WeathertopRuinedArch.obj", "SM_WeathertopBrokenPillar.obj", "SM_WeathertopCampRing.obj"],
    "Rivendell": ["SM_RivendellPavilion.obj", "SM_RivendellArch.obj", "SM_RivendellBridge.obj", "SM_RivendellLantern.obj"],
    "Road": ["SM_RoadCampTent.obj", "SM_RoadSupplyRack.obj", "SM_CaradhrasRock.obj"],
    "Moria": ["SM_MoriaPillar.obj", "SM_MoriaDoor.obj", "SM_MoriaBrazier.obj", "SM_MoriaBridgeSegment.obj"],
    "Lothlorien": ["SM_LorienTalan.obj", "SM_LorienLantern.obj", "SM_LorienMirror.obj"],
    "Anduin": ["SM_AnduinBoat.obj", "SM_AmonHenStair.obj", "SM_AmonHenRuin.obj", "SM_ArgonathSentinel.obj"],
}
for region_name, asset_names in regional_assets.items():
    region_root = ROOT / "SourceAssets" / "Production" / "World" / region_name
    for asset_name in asset_names:
        if not (region_root / asset_name).exists():
            fail(f"PG-042 regional production asset missing: {region_name}/{asset_name}")

regional_cpp = read(resolve_source("FellowshipChapterWorldBuilder.cpp"))
for symbol in [
    "EnsureProductionMeshes",
    "SpawnProductionChapterLayer",
    "WeathertopArchMesh",
    "RivendellPavilionMesh",
    "MoriaPillarMesh",
    "LorienTalanMesh",
    "AnduinBoatMesh",
    "ArgonathSentinelMesh",
    "ShowPrototypeWorldLabels = false",
]:
    if symbol not in regional_cpp:
        fail(f"PG-042 regional production runtime invariant missing: {symbol}")

for chapter_id in ["P1C03", "P1C04", "P1C05", "P1C06", "P1C07", "P1C08"]:
    if f'ChapterId == TEXT("{chapter_id}")' not in regional_cpp:
        fail(f"PG-042 lost chapter production branch: {chapter_id}")

# PG-041: Bree production layer must replace dominant blockout visuals without moving story flow.
bree_asset_root = ROOT / "SourceAssets" / "Production" / "World" / "Bree"
for asset_name in [
    "SM_BreeHouse.obj",
    "SM_BreeInn.obj",
    "SM_BreeGate.obj",
    "SM_BreeStall.obj",
    "SM_BreeLantern.obj",
    "SM_BreeHitchingPost.obj",
    "SM_BreeTable.obj",
    "SM_BreeCrateStack.obj",
]:
    if not (bree_asset_root / asset_name).exists():
        fail(f"PG-041 Bree production asset missing: {asset_name}")

bree_visual_cpp = read(resolve_source("BreePrototypeWorldBuilder.cpp"))
for symbol in [
    "SpawnProductionBreeDetailLayer",
    "ProductionHouseMesh",
    "ProductionInnMesh",
    "ProductionGateMesh",
    "ProductionLanternMesh",
    "ShowPrototypeWorldLabels = false",
]:
    if symbol not in bree_visual_cpp:
        fail(f"PG-041 Bree production runtime invariant missing: {symbol}")

for story_marker in [
    'FVector(-2050.0f, 0.0f, 90.0f)',
    'FVector(-1250.0f, 0.0f, 90.0f)',
    'FVector(850.0f, 90.0f, 90.0f)',
    'FVector(1640.0f, 1030.0f, 90.0f)',
]:
    if story_marker not in bree_visual_cpp:
        fail(f"PG-041 Bree story anchor moved or missing: {story_marker}")

# PG-040: visual-production-first assets must stay source-controlled, importable and runtime-referenced.
shire_asset_root = ROOT / "SourceAssets" / "Production" / "World" / "Shire"
common_character_root = ROOT / "SourceAssets" / "Production" / "Characters" / "Common"
for asset_name in [
    "SM_ShCottageHouse.obj",
    "SM_ShMillHouse.obj",
    "SM_ShStoneBridge.obj",
    "SM_ShWell.obj",
    "SM_ShMarketStall.obj",
    "SM_ShStoneWall.obj",
    "SM_ShFarmGate.obj",
    "SM_ShHaystack.obj",
    "SM_ShFlowerBox.obj",
    "SM_ShLampPost.obj",
    "SM_ShPicnicTable.obj",
    "SM_ShCartLoaded.obj",
]:
    if not (shire_asset_root / asset_name).exists():
        fail(f"PG-040 Shire production asset missing: {asset_name}")

for asset_name in [
    "SM_Human_Torso.obj",
    "SM_Human_Head.obj",
    "SM_Human_Hair.obj",
    "SM_Human_Arm.obj",
    "SM_Human_Leg.obj",
    "SM_Elf_Torso.obj",
    "SM_Elf_Head.obj",
    "SM_Elf_Hair.obj",
    "SM_Dwarf_Torso.obj",
    "SM_Dwarf_Head.obj",
    "SM_Dwarf_Beard.obj",
    "SM_Dwarf_Arm.obj",
    "SM_Dwarf_Leg.obj",
    "SM_ProductionCloak.obj",
    "SM_ProductionSword.obj",
    "SM_ProductionShield.obj",
    "SM_ProductionAxe.obj",
    "SM_ProductionBow.obj",
]:
    if not (common_character_root / asset_name).exists():
        fail(f"PG-040 common production character asset missing: {asset_name}")

shire_visual_cpp = read(resolve_source("ShirePrototypeWorldBuilder.cpp"))
named_visual_cpp = read(resolve_source("ShireNPC.cpp"))
ambient_visual_cpp = read(resolve_source("ShireAmbientNPC.cpp"))
for symbol in [
    "SpawnProductionVillageDetailLayer",
    "ProductionCottageHouseMesh",
    "ProductionMillHouseMesh",
    "ProductionStoneBridgeMesh",
    "ProductionMarketStallMesh",
]:
    if symbol not in shire_visual_cpp:
        fail(f"PG-040 Shire visual-production runtime reference missing: {symbol}")

for symbol in [
    "SM_Human_Torso",
    "SM_Elf_Torso",
    "SM_Dwarf_Torso",
    "SM_ProductionCloak",
    "SM_ProductionSword",
]:
    if symbol not in named_visual_cpp:
        fail(f"PG-040 named-character production archetype reference missing: {symbol}")

for symbol in ["SM_Human_Torso", "SM_Elf_Torso"]:
    if symbol not in ambient_visual_cpp:
        fail(f"PG-040 ambient production archetype reference missing: {symbol}")

# PG-039: named-NPC memory must remain compact, bounded, route-partitioned and save-backed.
memory_route_h = read(resolve_source("ShireRouteState.h"))
memory_quest_h = read(resolve_source("ShireQuestSubsystem.h"))
memory_quest_cpp = read(resolve_source("ShireQuestSubsystem.cpp"))
memory_context_cpp = read(resolve_source("ShireNPCContextSubsystem.cpp"))
memory_save_h = read(resolve_source("ShireSaveGame.h"))
memory_player_cpp = read(resolve_source("ShirePlayerCharacter.cpp"))

for symbol in [
    "FShireNPCMemoryEvent",
    "FShireNPCMemoryBucket",
    "RememberNamedNPCEvent",
    "HasNamedNPCMemory",
    "AdjustNamedNPCRelationship",
    "RestoreNPCMemoryState",
    "ResolveCanonicalNPCProfile",
    "ResolvePersistentMemoryBudget",
    "ResolveRelationshipBudget",
    "PruneNPCMemoryForCurrentChapter",
    'TEXT("%s|%s")',
]:
    if symbol not in (memory_route_h + memory_quest_h + memory_quest_cpp):
        fail(f"PG-039 named-NPC memory invariant missing: {symbol}")

for symbol in [
    'Tier == TEXT("NAMED_STORY")',
    'Tier == TEXT("NAMED_LIGHT")',
    "return 12;",
    "return 4;",
    "return 8;",
    "return 3;",
]:
    if symbol not in memory_context_cpp:
        fail(f"PG-039 tiered memory budget invariant missing: {symbol}")

if "TMap<FName, FShireNPCMemoryBucket> NPCMemoryState" not in memory_save_h:
    fail("PG-039 SaveGame lost NPCMemoryState")
if "Save->NPCMemoryState = QuestSubsystem->GetNPCMemorySnapshot()" not in memory_player_cpp:
    fail("PG-039 save snapshot no longer captures NPC memory")
if "QuestSubsystem->RestoreNPCMemoryState(Save->NPCMemoryState)" not in memory_player_cpp:
    fail("PG-039 restore path no longer restores NPC memory")

memory_runtime = npc_memory.get("runtime_implementation", {}) if npc_memory else {}
if memory_runtime.get("status") not in {"RUNTIME_FOUNDATION", "RUNTIME_COMPLETE_PENDING_VALIDATION"}:
    fail("PG-039 NPCMemoryPlan runtime status is unsupported")
if memory_runtime.get("status") == "RUNTIME_COMPLETE_PENDING_VALIDATION":
    for requirement in [
        "canonical alias resolution through UShireNPCContextSubsystem before read/write",
        "NAMED_LIGHT 4-event/3-relationship budgets",
        "low-priority memory expires after two chapters while priority >=80 story/relationship memories survive",
        "recent dialogue variant and partner histories persist for repetition control",
    ]:
        if requirement not in memory_runtime.get("implementation", []):
            fail(f"PG-039 completed NPC memory runtime declaration missing: {requirement}")
if memory_runtime.get("proof_limit") is None:
    fail("PG-039 NPCMemoryPlan must keep its proof limit explicit")

# PG-038: ambient NPC-to-NPC conversation runtime must stay bounded and near-player.
ambient_conversation_cpp = read(resolve_source("ShireAmbientNPC.cpp"))
ambient_conversation_h = read(resolve_source("ShireAmbientNPC.h"))
for symbol in [
    "SocialCaption",
    "BeginSocialCaption",
    "UpdateSocialCaption",
    "ResolveAmbientConversationLine",
    "NearbySocialActors >= 4",
    "LastPartnerCooldownRemaining = 90.0f",
    'RoutineRole == TEXT("Bird")',
]:
    if symbol not in ambient_conversation_cpp and symbol not in ambient_conversation_h:
        fail(f"PG-038 ambient conversation invariant missing: {symbol}")

for authored_line in [
    "Have you seen the lanterns?",
    "The field will not tend itself.",
    "The road is busy tonight.",
    "The wind changed beyond the trees.",
]:
    if authored_line not in ambient_conversation_cpp:
        fail(f"PG-038 role-specific ambient line missing: {authored_line}")

conversation_runtime = npc_conversation.get("runtime_implementation", {}) if npc_conversation else {}
conversation_status = conversation_runtime.get("status")
if conversation_status not in {"RUNTIME_PARTIAL", "RUNTIME_COMPLETE_PENDING_VALIDATION"}:
    fail("PG-038 NPCConversationPlan runtime status is unsupported")

if conversation_status == "RUNTIME_PARTIAL":
    if "named Fellowship companion banter runtime" not in conversation_runtime.get("not_yet_implemented", []):
        fail("PG-038 partial NPC conversation runtime must keep named Fellowship conversation gap explicit")
else:
    named_npc_cpp = read(resolve_source("ShireNPC.cpp"))
    dialogue_h = read(resolve_source("ShireDialogueSubsystem.h"))
    dialogue_cpp = read(resolve_source("ShireDialogueSubsystem.cpp"))
    context_cpp = read(resolve_source("ShireNPCContextSubsystem.cpp"))
    for symbol in [
        "UpdateCompanionBanter",
        "COMPANION_BANTER",
        "TActorIterator<AShireNPC>",
        "PlayDynamicSequence",
        "SelectBoundedDialogue",
    ]:
        if symbol not in (named_npc_cpp + dialogue_h + dialogue_cpp + context_cpp):
            fail(f"PG-038 completed named conversation runtime missing: {symbol}")

approved_chapters = set(guard_rules.get("runtime_chapters", []))
approved_routes = set(guard_rules.get("approved_routes", []))
approved_canon_classes = set(guard_rules.get("canon_classes", []))
route_episode_patterns = guard_rules.get("route_episode_patterns", {})

def read_csv_rows(relative: str, required_columns: set[str]) -> list[dict[str, str]]:
    path = ROOT / relative
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            columns = set(reader.fieldnames or [])
            missing = sorted(required_columns - columns)
            if missing:
                fail(f"{relative} missing columns: {', '.join(missing)}")
                return []
            return [dict(row) for row in reader]
    except Exception as exc:
        fail(f"Cannot parse {relative}: {exc}")
        return []

dialogue_rows = read_csv_rows("Data/DialogueIntent.csv", {
    "Route", "Chapter", "Episode", "Scene", "Character", "Intent", "Tone", "CanonClass", "OriginalDialogueRule"
})
story_rows = read_csv_rows("Data/StoryBeatPlan.csv", {
    "Route", "Chapter", "Episode", "StoryBeatId", "SequenceType", "CameraIntent", "AudioIntent",
    "MusicIntent", "GameplayLock", "CanonClass", "Notes"
})
music_rows = read_csv_rows("Data/MusicCuePlan.csv", {
    "Route", "Chapter", "Region", "MusicCue", "StoryFunction", "Palette", "Intensity", "Looping", "OriginalityRule"
})

voice_rows = read_csv_rows("Data/VoiceCuePlan.csv", {
    "VoiceCue", "Speaker", "VoiceDirection", "SpatialMode", "AssetPath", "Status", "OriginalityRule"
})

biome_rows = read_csv_rows("Data/BiomePlan.csv", {
    "Chapter", "Region", "TerrainIdentity", "VegetationIdentity", "WaterIdentity",
    "WeatherAtmosphere", "TraversalIdentity", "StoryHazards", "AudioIdentity", "PerformanceRule"
})

checkpoint_rows = read_csv_rows("Data/WorldCheckpointPlan.csv", {
    "CheckpointId", "Chapter", "Region", "StoryBeat", "CheckpointType",
    "WorldAnchorStatus", "RuntimeCheckpointStatus", "SavePolicy", "RespawnPolicy", "Notes"
})

def validate_route_rows(relative: str, rows: list[dict[str, str]], check_canon: bool = False) -> None:
    for index, row in enumerate(rows, start=2):
        route = (row.get("Route") or "").strip()
        chapter = (row.get("Chapter") or "").strip()
        episode = (row.get("Episode") or "").strip()

        if approved_routes and route not in approved_routes:
            fail(f"{relative}:{index} uses unapproved Route '{route}'")

        if approved_chapters and chapter not in approved_chapters:
            fail(f"{relative}:{index} uses non-runtime Chapter '{chapter}'")

        pattern = route_episode_patterns.get(route)
        if pattern and episode and not re.match(pattern, episode):
            fail(f"{relative}:{index} Episode '{episode}' does not match route policy for {route}")

        if check_canon:
            canon_class = (row.get("CanonClass") or "").strip()
            if approved_canon_classes and canon_class not in approved_canon_classes:
                fail(f"{relative}:{index} uses unapproved CanonClass '{canon_class}'")

validate_route_rows("Data/DialogueIntent.csv", dialogue_rows, check_canon=True)
validate_route_rows("Data/StoryBeatPlan.csv", story_rows, check_canon=True)
validate_route_rows("Data/MusicCuePlan.csv", music_rows, check_canon=False)

checkpoint_ids: set[str] = set()
checkpoint_chapters: set[str] = set()
story_plan_id_set = {(row.get("StoryBeatId") or "").strip() for row in story_rows if (row.get("StoryBeatId") or "").strip()}
for index, row in enumerate(checkpoint_rows, start=2):
    checkpoint_id = (row.get("CheckpointId") or "").strip()
    chapter = (row.get("Chapter") or "").strip()
    story_beat = (row.get("StoryBeat") or "").strip()
    runtime_status = (row.get("RuntimeCheckpointStatus") or "").strip()
    save_policy = (row.get("SavePolicy") or "").strip()

    if not checkpoint_id:
        fail(f"Data/WorldCheckpointPlan.csv:{index} has empty CheckpointId")
    elif checkpoint_id in checkpoint_ids:
        fail(f"Data/WorldCheckpointPlan.csv:{index} duplicates CheckpointId '{checkpoint_id}'")
    checkpoint_ids.add(checkpoint_id)

    if approved_chapters and chapter not in approved_chapters:
        fail(f"Data/WorldCheckpointPlan.csv:{index} uses non-runtime Chapter '{chapter}'")
    checkpoint_chapters.add(chapter)

    if story_beat and story_beat not in story_plan_id_set:
        fail(f"Data/WorldCheckpointPlan.csv:{index} references unknown StoryBeat '{story_beat}'")

    if runtime_status not in {"PLANNED", "FOUNDATION", "FUNCTIONAL", "VERIFIED"}:
        fail(f"Data/WorldCheckpointPlan.csv:{index} has unsupported RuntimeCheckpointStatus '{runtime_status}'")
    if save_policy not in {"AUTO_SAFE", "MANUAL_ONLY", "TRANSITION"}:
        fail(f"Data/WorldCheckpointPlan.csv:{index} has unsupported SavePolicy '{save_policy}'")

missing_checkpoint_chapters = sorted(approved_chapters - checkpoint_chapters)
if missing_checkpoint_chapters:
    fail("WorldCheckpointPlan missing runtime chapters: " + ", ".join(missing_checkpoint_chapters))

# PG-037: any checkpoint promoted beyond PLANNED must have a concrete runtime binding.
checkpoint_runtime_source = "\n".join([
    read(resolve_source("ShirePlayerCharacter.cpp")),
    read(resolve_source("ShirePlayerCharacter.h")),
    read(resolve_source("ShireQuestTrigger.cpp")),
    read(resolve_source("ShireSaveGame.h")),
])
for index, row in enumerate(checkpoint_rows, start=2):
    checkpoint_id = (row.get("CheckpointId") or "").strip()
    runtime_status = (row.get("RuntimeCheckpointStatus") or "").strip()
    if runtime_status != "PLANNED" and checkpoint_id and checkpoint_id not in checkpoint_runtime_source:
        fail(f"PG-037 checkpoint {checkpoint_id} is {runtime_status} but has no runtime binding")

for symbol in [
    'CheckpointSlotName(TEXT("ShireJourney_Checkpoint"))',
    "SaveAutomaticCheckpoint",
    "RestoreAutomaticCheckpoint",
    "PendingChapterCheckpointId",
    "AsyncSaveGameToSlot",
    "bCheckpointSaveInFlight",
    "QueuedCheckpointSaveId",
    "SafeCheckpoint: id=%s async-save=scheduled",
    "SafeCheckpoint: id=%s async-save=%s stateApplied=%s sameCommittedContext=%s slot=%s user=%d",
    "SafeCheckpoint: restored id=%s",
]:
    if symbol not in checkpoint_runtime_source:
        fail(f"PG-037 automatic checkpoint runtime invariant missing: {symbol}")

biome_chapters = {(row.get("Chapter") or "").strip() for row in biome_rows}
missing_biome_chapters = sorted(approved_chapters - biome_chapters)
unknown_biome_chapters = sorted(biome_chapters - approved_chapters)
if missing_biome_chapters:
    fail("BiomePlan missing runtime chapters: " + ", ".join(missing_biome_chapters))
if unknown_biome_chapters:
    fail("BiomePlan contains unknown runtime chapters: " + ", ".join(unknown_biome_chapters))
for index, row in enumerate(biome_rows, start=2):
    for field in ["Region", "TerrainIdentity", "VegetationIdentity", "WaterIdentity",
                  "WeatherAtmosphere", "TraversalIdentity", "StoryHazards",
                  "AudioIdentity", "PerformanceRule"]:
        if not (row.get(field) or "").strip():
            fail(f"Data/BiomePlan.csv:{index} has empty {field}")

dialogue_keys: set[tuple[str, str, str, str, str]] = set()
for index, row in enumerate(dialogue_rows, start=2):
    key = tuple((row.get(name) or "").strip() for name in ["Route", "Chapter", "Episode", "Scene", "Character"])
    if key in dialogue_keys:
        fail(f"Data/DialogueIntent.csv:{index} duplicates route/chapter/episode/scene/character key: {key}")
    dialogue_keys.add(key)
    if not (row.get("Intent") or "").strip():
        fail(f"Data/DialogueIntent.csv:{index} has empty Intent")
    if not (row.get("OriginalDialogueRule") or "").strip():
        fail(f"Data/DialogueIntent.csv:{index} has empty OriginalDialogueRule")

story_plan_ids = [(row.get("StoryBeatId") or "").strip() for row in story_rows]
empty_story_ids = [index for index, value in enumerate(story_plan_ids, start=2) if not value]
if empty_story_ids:
    fail("Data/StoryBeatPlan.csv has empty StoryBeatId rows: " + ", ".join(map(str, empty_story_ids)))
duplicate_story_plan_ids = sorted({value for value in story_plan_ids if value and story_plan_ids.count(value) > 1})
if duplicate_story_plan_ids:
    fail("Duplicate StoryBeatPlan StoryBeatId values: " + ", ".join(duplicate_story_plan_ids))

music_plan_ids = [(row.get("MusicCue") or "").strip() for row in music_rows]
duplicate_music_plan_ids = sorted({value for value in music_plan_ids if value and music_plan_ids.count(value) > 1})
if duplicate_music_plan_ids:
    fail("Duplicate MusicCuePlan MusicCue values: " + ", ".join(duplicate_music_plan_ids))
for index, row in enumerate(music_rows, start=2):
    if not (row.get("OriginalityRule") or "").strip():
        fail(f"Data/MusicCuePlan.csv:{index} has empty OriginalityRule")

voice_plan_ids = [(row.get("VoiceCue") or "").strip() for row in voice_rows]
duplicate_voice_plan_ids = sorted({value for value in voice_plan_ids if value and voice_plan_ids.count(value) > 1})
if duplicate_voice_plan_ids:
    fail("Duplicate VoiceCuePlan VoiceCue values: " + ", ".join(duplicate_voice_plan_ids))

for index, row in enumerate(voice_rows, start=2):
    for field in ["VoiceCue", "Speaker", "VoiceDirection", "SpatialMode", "AssetPath", "Status", "OriginalityRule"]:
        if not (row.get(field) or "").strip():
            fail(f"Data/VoiceCuePlan.csv:{index} has empty {field}")
    if (row.get("Status") or "").strip() not in {"ASSET_PENDING", "READY"}:
        fail(f"Data/VoiceCuePlan.csv:{index} has unsupported Status")
    originality = (row.get("OriginalityRule") or "").lower()
    if "do not clone" not in originality or "specific film actor" not in originality:
        fail(f"Data/VoiceCuePlan.csv:{index} must prohibit cloning a specific film actor voice")


uproject = ROOT / "ShireJourney.uproject"
if uproject.exists():
    try:
        descriptor = json.loads(read(uproject))
        if str(descriptor.get("EngineAssociation")) != "4.27":
            fail("ShireJourney.uproject must target EngineAssociation 4.27")
        modules = descriptor.get("Modules") or []
        if not any(module.get("Name") == "ShireJourney" for module in modules if isinstance(module, dict)):
            fail("ShireJourney module missing from .uproject")
        editor_tools = next(
            (module for module in modules if isinstance(module, dict)
             and module.get("Name") == "ShireJourneyEditorTools"),
            None,
        )
        if not editor_tools:
            fail("ShireJourneyEditorTools module missing from .uproject")
        else:
            if editor_tools.get("Type") != "Editor":
                fail("PG-014: ShireJourneyEditorTools must remain an Editor module")
            if editor_tools.get("LoadingPhase") != "Default":
                fail("PG-014: ShireJourneyEditorTools must load at Default phase so commandlets are discoverable")
    except json.JSONDecodeError as exc:
        fail(f"Invalid ShireJourney.uproject JSON: {exc}")

for path in sorted(SOURCE.rglob("*.[ch]pp")) + sorted(SOURCE.rglob("*.h")):
    text = read(path)
    cleaned = strip_comments_and_strings(text)
    balance = 0
    for index, char in enumerate(cleaned):
        if char == "{":
            balance += 1
        elif char == "}":
            balance -= 1
            if balance < 0:
                fail(f"Brace closes before opening in {path.name} near character {index}")
                break
    if balance != 0:
        fail(f"Unbalanced braces in {path.name}: balance={balance}")

for path in sorted(SOURCE.rglob("*.h")):
    lines = read(path).splitlines()
    generated_indexes = [i for i, line in enumerate(lines) if ".generated.h\"" in line]
    if not generated_indexes:
        continue
    generated_index = generated_indexes[-1]
    later_includes = [line.strip() for line in lines[generated_index + 1 :] if line.strip().startswith("#include")]
    if later_includes:
        fail(f"{path.name}: generated.h is not the last include ({later_includes[0]})")

# PG-049: living-world director and engineering execution graph must remain bounded and architecture-tracked.
execution_graph_path = ROOT / "Data" / "ProductionExecutionGraph.json"
execution_graph = {}
if not execution_graph_path.exists():
    fail("PG-049 ProductionExecutionGraph.json missing")
else:
    try:
        execution_graph = json.loads(read(execution_graph_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-049 invalid ProductionExecutionGraph.json: {exc}")

if execution_graph and execution_graph.get("authority_id") != "FELLOWSHIP_ENGINEERING_EXECUTION_GRAPH_V1":
    fail("PG-049 execution graph authority_id drifted")
for workstream_id in [
    "WS_BACKEND_CORE",
    "WS_LIVING_WORLD_AI",
    "WS_CHARACTER_PRODUCTION",
    "WS_WORLD_PRODUCTION",
    "WS_STORY_MISSIONS",
    "WS_AUDIO_PRESENTATION",
    "WS_ACCEPTANCE",
]:
    if workstream_id not in {str(x.get("id") or "") for x in execution_graph.get("workstreams", []) if isinstance(x, dict)}:
        fail(f"PG-049 execution workstream missing: {workstream_id}")

living_h = read(resolve_source("LivingWorldDirector.h"))
living_cpp = read(resolve_source("LivingWorldDirector.cpp"))
for symbol in [
    "LoadEventContract",
    "MaxActiveMicroEvents",
    "MinSecondsBetweenEventStarts",
    "EventCullDistance",
    "TryStartMicroEvent",
    "LivingWorldEphemeral",
    "GetCurrentRouteId() != TEXT(\"FrodoMain\")",
    "IsStoryDangerActive",
]:
    if symbol not in (living_h + living_cpp):
        fail(f"PG-049 living-world director invariant missing: {symbol}")

game_mode_cpp = read(resolve_source("ShireGameMode.cpp"))
if "SpawnActor<ALivingWorldDirector>" not in game_mode_cpp:
    fail("PG-049 ShireGameMode no longer bootstraps LivingWorldDirector")

common_world_root = ROOT / "SourceAssets" / "Production" / "World" / "Common"
for asset_name in [
    "SM_CommonMountainRidge.obj",
    "SM_CommonCliffWall.obj",
    "SM_CommonTerracedHill.obj",
    "SM_CommonRiverBank.obj",
    "SM_CommonVillageSlope.obj",
    "SM_CommonBoulderCluster.obj",
]:
    if not (common_world_root / asset_name).exists():
        fail(f"PG-049 common terrain production asset missing: {asset_name}")

shire_world_cpp = read(resolve_source("ShirePrototypeWorldBuilder.cpp"))
fellowship_world_cpp = read(resolve_source("FellowshipChapterWorldBuilder.cpp"))
for symbol in ["SM_CommonTerracedHill", "SM_CommonVillageSlope", "SM_CommonRiverBank", "SM_CommonBoulderCluster"]:
    if symbol not in shire_world_cpp:
        fail(f"PG-049 Shire terrain runtime reference missing: {symbol}")
for symbol in ["SM_CommonMountainRidge", "SM_CommonCliffWall", "SM_CommonRiverBank", "SpawnTerrainBand"]:
    if symbol not in fellowship_world_cpp:
        fail(f"PG-049 Fellowship terrain runtime reference missing: {symbol}")

# PG-165: Drop C1 authored material texture binding must remain deterministic and editor-only.
pg165_importer = read(resolve_editor_source("ShireProductionImportCommandlet.cpp"))
for pg165_symbol in [
    "MaterialExpressionTextureSampleParameter2D",
    'ParameterName = TEXT("AlbedoTexture")',
    'Line.StartsWith(TEXT("map_Kd ")',
    "PendingAlbedoBindings",
    "SetTextureParameterValueEditorOnly",
    'TEXT("ShireProductionImport albedo texture bindings:',
]:
    if pg165_symbol not in pg165_importer:
        fail(f"PG-165 authored albedo binding invariant missing: {pg165_symbol}")

pg165_plan = json.loads(read(ROOT / "Data" / "P1C01MaterialsVegetationPlanV1.json"))
# PG-165 protects the durable C1 albedo contract. The overall production-plan
# status is allowed to advance through C2/C3/C4/D without reopening C1.
if "AlbedoTexture" not in json.dumps(pg165_plan):
    fail("PG-165 Drop C1 lost AlbedoTexture contract")
if pg165_plan.get("material_contract", {}).get("master_surface") != "/Game/Production/Materials/M_ProductionSurface":
    fail("PG-165 Drop C1 production master surface contract changed")


# PG-166: Drop C2 lightweight foliage wind stays material-only and uses the UE4.27 material-function API.
pg166_importer = pg165_importer
for pg166_symbol in [
    "MaterialExpressionMaterialFunctionCall",
    'TEXT("M_ProductionFoliage")',
    'TEXT("M_ProductionFoliageFar")',
    'ParameterName = TEXT("WindIntensity")',
    'ParameterName = TEXT("WindSpeed")',
    'ParameterName = TEXT("WindWeight")',
    "/Engine/Functions/Engine_MaterialFunctions01/WorldPositionOffset/SimpleGrassWind.SimpleGrassWind",
    "WorldPositionOffset.Expression = SimpleWind",
    'TEXT("ShireProductionImport failed to bind UE4.27 SimpleGrassWind material function.")',
    'TEXT("ShireProductionImport created M_ProductionFoliageFar no-WPO master.")',
]:
    if pg166_symbol not in pg166_importer:
        fail(f"PG-166 foliage wind invariant missing: {pg166_symbol}")
pg166_plan = pg165_plan
# PG-166 protects C2 closure evidence and wind/performance invariants, not the
# mutable top-level phase label. Later production drops must be free to advance.
pg166_c2_evidence = pg166_plan.get("c2_machine_evidence", {})
for pg166_evidence_key in ["final_pr_head", "pre_unreal", "unreal", "merge_commit"]:
    if not pg166_c2_evidence.get(pg166_evidence_key):
        fail(f"PG-166 Drop C2 closure evidence missing: {pg166_evidence_key}")
pg166_perf = pg166_plan.get("performance_contract", {}).get("c2_wind_strategy", {})
if "no WorldPositionOffset" not in pg166_perf.get("far", ""):
    fail("PG-166 far foliage path lost the no-WPO complexity contract")
if pg166_perf.get("density") != "unchanged until target-device profiling":
    fail("PG-166 foliage density profiling gate changed")
if "MaterialExpressionDistanceCullFade" in pg166_importer or "DistanceScaledWindWeight" in pg166_importer:
    fail("PG-166 C2 must not regress to the non-exported DistanceCullFade dependency")


# PG-169: C3 stable foliage material identity must be narrow, deterministic and C4-safe before runtime implementation.
pg169_plan = json.loads(read(ROOT / "Data" / "P1C01C3FoliageMaterialIdentityPlanV1.json"))
if pg169_plan.get("status") not in {
    "PREPARED_NOT_RUNTIME_STARTED",
    "C3_IMPLEMENTED_PENDING_EXACT_HEAD_ENGINE_PROOF",
    "C3_EXACT_HEAD_GREEN_MERGED_C4_READY",
}:
    fail("PG-169 C3 plan has an invalid implementation status")
if pg169_plan.get("target_material_names") != ["Grass", "Leaves", "LeafGreen", "LeafGold"]:
    fail("PG-169 C3 approved foliage identity set changed")
pg169_parent = pg169_plan.get("parent_assignment_contract", {})
if pg169_parent.get("near_mid_parent") != "/Game/Production/Materials/M_ProductionFoliage":
    fail("PG-169 C3 near/mid foliage parent changed")
if pg169_parent.get("non_foliage_parent") != "/Game/Production/Materials/M_ProductionSurface":
    fail("PG-169 C3 non-foliage parent changed")
if pg169_parent.get("far_parent") != "/Game/Production/Materials/M_ProductionFoliageFar":
    fail("PG-169 C3 far parent contract changed")
if "exact normalized material identity" not in pg169_parent.get("identity_rule", ""):
    fail("PG-169 C3 lost exact material-identity classification")
if "C4" not in pg169_parent.get("c3_scope", "") or "near/mid" not in pg169_parent.get("c3_scope", ""):
    fail("PG-169 C3/C4 foliage parent boundary changed")
pg169_guards = json.dumps(pg169_plan.get("guards", []))
for pg169_guard in ["contains('Leaf')", "contains('Grass')", "M_ProductionFoliageFar"]:
    if pg169_guard not in pg169_guards:
        fail(f"PG-169 C3 guard missing: {pg169_guard}")

if pg169_plan.get("status") != "PREPARED_NOT_RUNTIME_STARTED":
    for pg169_symbol in [
        "IsApprovedFoliageMaterialIdentity",
        'TEXT("Grass")',
        'TEXT("Leaves")',
        'TEXT("LeafGreen")',
        'TEXT("LeafGold")',
        "DesiredMaterialParent = ProductionMaterialParent",
        "DesiredMaterialParent = ProductionFoliageParent",
        "Instance->SetParentEditorOnly(DesiredMaterialParent)",
    ]:
        if pg169_symbol not in pg166_importer:
            fail(f"PG-169 C3 implementation invariant missing: {pg169_symbol}")
    for pg169_forbidden in [
        'Contains(TEXT("Leaf")',
        'Contains(TEXT("Grass")',
        "SetParentEditorOnly(ProductionFoliageFarParent)",
    ]:
        if pg169_forbidden in pg166_importer:
            fail(f"PG-169 C3 forbidden broad/far binding found: {pg169_forbidden}")


# PG-170: volatile GitHub transport metadata must never become a production blocker.
project_governor_validator = read(ROOT / "Scripts" / "project_governor.py")
for pg170_forbidden in [
    "Governor branch workflow and session handoff disagree on current branch",
    "Governor branch workflow and session handoff disagree on current PR",
    "MASTER_EXECUTION_BOARD must expose no active PR",
    "MASTER_EXECUTION_BOARD current PR disagrees with handoff",
]:
    if pg170_forbidden in project_governor_validator:
        fail(f"PG-170 volatile GitHub transport metadata became a Governor build gate again: {pg170_forbidden}")

branch_cleanup_script = read(ROOT / "Scripts" / "run_branch_cleanup.ps1")
for pg170_cleanup_symbol in [
    "$_.PSObject.Properties['head']",
    "$_.head.PSObject.Properties['ref']",
]:
    if pg170_cleanup_symbol not in branch_cleanup_script:
        fail(f"PG-170 branch cleanup lost empty/open-PR response hardening: {pg170_cleanup_symbol}")


# PG-171: C4 foliage LOD/cull/overdraw evidence capture must remain fail-closed.
pg171_plan = json.loads(read(ROOT / "Data" / "P1C01C4FoliageLodCullOverdrawPlanV1.json"))
pg171_status = str(pg171_plan.get("status") or "")
if pg171_status != "PREPARED_NOT_RUNTIME_STARTED" and not pg171_status.startswith("C4_"):
    fail("PG-171 C4 plan has an invalid implementation status")
if pg171_plan.get("status") != "PREPARED_NOT_RUNTIME_STARTED":
    for pg171_symbol in [
        "IsP1C01FoliageMeshAssetName",
        "C4_FOLIAGE_EVIDENCE",
        "RenderData->LODResources",
        "FAR_LOD_ELIGIBLE_FOR_REVIEW",
        "actual-far-lod-and-approved-foliage-identity",
    ]:
        if pg171_symbol not in pg166_importer:
            fail(f"PG-171 C4 evidence invariant missing: {pg171_symbol}")
    for pg171_forbidden in [
        "SetParentEditorOnly(ProductionFoliageFarParent)",
        "SetStaticMeshLOD",
    ]:
        if pg171_forbidden in pg166_importer:
            fail(f"PG-171 C4 evidence-capture step performed premature far binding: {pg171_forbidden}")


# PG-174: new developer / AI sessions must have one stable path to the Project Governor.
pg174_readme = read(ROOT / "README.md")
pg174_onboarding = read(ROOT / "Scripts" / "new_developer_onboarding.ps1")
for pg174_required in [
    "NEW DEVELOPER / NEW AI SESSION — START HERE",
    "Docs/PROJECT_GOVERNOR.md",
    "Data/ProjectGovernor.json",
    "Scripts\\new_developer_onboarding.ps1",
]:
    if pg174_required not in pg174_readme:
        fail(f"PG-174 README developer entry missing: {pg174_required}")
for pg174_required in [
    "Data\\ProjectGovernor.json",
    "execution_control",
    "active_gate",
    "CURRENT_PROJECT_STATE.md",
    "DEVELOPMENT_GATES.md",
    "PROJECT_GUARDIAN.md",
]:
    if pg174_required not in pg174_onboarding:
        fail(f"PG-174 onboarding script contract missing: {pg174_required}")


# PG-172: P1C01 D lighting/sky/fog/water must remain fixed-state, resident-only and low-cost.
pg172_plan = json.loads(read(ROOT / "Data" / "P1C01DLightingSkyFogWaterPlanV1.json"))
pg172_status = str(pg172_plan.get("status") or "")
if pg172_status not in {
    "PREPARED_NOT_RUNTIME_STARTED",
    "D_IMPLEMENTED_PENDING_EXACT_HEAD_ENGINE_PROOF",
    "D_EXACT_HEAD_GREEN_MERGED_PRESENTATION_REVIEW_PENDING",
}:
    fail("PG-172 D plan has an invalid implementation status")

pg172_builder = read(resolve_source("ShirePrototypeWorldBuilder.cpp"))
pg172_header = read(resolve_source("ShirePrototypeWorldBuilder.h"))
pg172_importer = read(ROOT / "Source" / "ShireJourneyEditorTools" / "Private" / "ShireProductionImportCommandlet.cpp")
pg172_streaming = json.loads(read(ROOT / "Data" / "ChapterAssetStreamingPlan.json"))

if pg172_status != "PREPARED_NOT_RUNTIME_STARTED":
    for pg172_symbol in [
        "ResolveResidentMaterial",
        "ProductionWaterMaterial",
        "SpawnWaterSurface",
        "P1C01LowCostWaterSurface",
        "D_WATER_EVIDENCE",
        "M_ProductionWater",
        "D_WATER_MATERIAL_EVIDENCE",
    ]:
        if pg172_symbol not in (pg172_builder + pg172_header + pg172_importer):
            fail(f"PG-172 D runtime/import invariant missing: {pg172_symbol}")

    pg172_p1c01_assets = pg172_streaming.get("banks", {}).get("P1C01", {}).get("assets", [])
    pg172_water_path = "/Game/Production/Materials/M_ProductionWater.M_ProductionWater"
    if pg172_water_path not in pg172_p1c01_assets:
        fail("PG-172 P1C01 async bank lost M_ProductionWater")

    if pg172_builder.count("RecaptureSky()") != 2:
        fail("PG-172 skylight recapture must remain limited to startup plus authored story-event refresh in P1C01 D")
    if "PrimaryActorTick.bCanEverTick = false" not in pg172_builder:
        fail("PG-172 P1C01 world builder unexpectedly gained Actor Tick")

    for pg172_forbidden in [
        "LoadSynchronous",
        "TryLoad(",
        "APlanarReflection",
        "USceneCaptureComponent",
    ]:
        if pg172_forbidden in pg172_builder:
            fail(f"PG-172 forbidden P1C01 D runtime path found: {pg172_forbidden}")

# PG-173: Mega Asset Promotion may scale staging/QC, never evidence-free promotion.
pg173_policy = json.loads(read(ROOT / "Data" / "ProductionAssetPromotionPolicyV1.json"))
pg173_queue = json.loads(read(ROOT / "Data" / "P1C01WarehousePromotionQueueV1.json"))
pg173_execution = pg173_queue.get("execution", {})
if pg173_execution:
    if pg173_execution.get("state") != "MEGA_PROMOTION_LAUNCHED":
        fail("PG-173 mega promotion execution state changed unexpectedly")
    if pg173_execution.get("promotion_ceiling_without_new_receipts") != "INTAKE_QC":
        fail("PG-173 mega promotion ceiling must remain INTAKE_QC without new receipts")

pg173_states = pg173_policy.get("states", [])
for pg173_required_state in [
    "AUTHORIZED_FOR_STAGING",
    "STAGED",
    "INTAKE_QC",
    "READY_FOR_IMPORT",
    "IMPORTED",
    "INTEGRATED",
    "ACCEPTED",
]:
    if pg173_required_state not in pg173_states:
        fail(f"PG-173 promotion state missing from policy: {pg173_required_state}")

for pg173_group_name, pg173_items in pg173_queue.get("groups", {}).items():
    for pg173_item in pg173_items:
        pg173_state = str(pg173_item.get("state") or "")
        if pg173_state in {"READY_FOR_IMPORT", "IMPORTED", "INTEGRATED", "ACCEPTED"}:
            pg173_evidence = pg173_item.get("promotion_evidence", {})
            for pg173_field in ["provider_or_source", "license_or_entitlement", "local_staging_receipt", "sha256", "class_qc"]:
                if not pg173_evidence.get(pg173_field):
                    fail(
                        f"PG-173 {pg173_group_name}/{pg173_item.get('id')} reached "
                        f"{pg173_state} without {pg173_field}"
                    )

# PG-184: warehouse validation must be fail-fast, non-destructive and non-repeating on PR sync.
pg184_workflow = read(ROOT / ".github" / "workflows" / "warehouse-stage.yml")
pg184_prep = read(ROOT / "Scripts" / "run_warehouse_critical_gap_preparation.ps1")
pg184_network = read(ROOT / "Scripts" / "warehouse_network.ps1")
pg184_ambient = read(ROOT / "Scripts" / "stage_ambientcg_warehouse.ps1")
pg184_kaykit = read(ROOT / "Scripts" / "stage_kaykit_github_warehouse.ps1")
pg184_manifest = read(ROOT / "Data" / "WarehouseCriticalGapPreparationTrainV2.json")
pg184_p1c01 = read(ROOT / "Scripts" / "run_warehouse_p1c01_mega_promotion.ps1")
pg184_p1c01_manifest = read(ROOT / "Data" / "WarehouseP1C01MegaPromotionTrainV1.json")

if "pull_request:" in pg184_workflow:
    fail("PG-184 Warehouse Stage must not run on pull-request synchronize; stage only after develop promotion or manual dispatch")
if "metadata-only" not in pg184_manifest.lower() and "inspected read-only" not in pg184_manifest.lower():
    fail("PG-184 critical-gap manifest must preserve metadata-only archive contract")
for pg184_symbol in [
    "Test-WarehouseZipReadable",
    "WAREHOUSE_ZIP_INVALID",
    "WAREHOUSE_REUSE_PURGE_CORRUPT_ZIP",
]:
    if pg184_symbol not in pg184_network:
        fail(f"PG-184 warehouse ZIP structural reuse guard missing: {pg184_symbol}")
for pg184_symbol in [
    "ZipFile]::OpenRead",
    "duplicateReceiptRows",
    "WAREHOUSE_CRITICAL_GAP_BLOCKED_DETAIL",
    "archiveMode=metadata-only",
    "WAREHOUSE_CRITICAL_GAP_PREFLIGHT_BLOCKED",
]:
    if pg184_symbol not in pg184_prep:
        fail(f"PG-184 warehouse metadata-only fail-fast prep missing: {pg184_symbol}")
if "Expand-Archive" in pg184_prep:
    fail("PG-184 critical-gap QC must not repeatedly extract every ZIP")
for pg184_stage, pg184_name in [
    (pg184_ambient, "ambientCG"),
    (pg184_kaykit, "KayKit"),
]:
    for pg184_symbol in ["Test-WarehouseZipReadable", "removing corrupt archive"]:
        if pg184_symbol not in pg184_stage:
            fail(f"PG-184 {pg184_name} staging corrupt-archive self-repair missing: {pg184_symbol}")

for pg184_symbol in [
    "Classify warehouse delta",
    "classify_warehouse_validation.ps1",
    "env.WH_RUN_PREP == 'true'",
    "env.WH_STAGE_AMBIENTCG == 'true'",
    "env.WH_RUN_P1C01_PROMOTION == 'true'",
    "run_warehouse_p1c01_mega_promotion.ps1",
]:
    if pg184_symbol not in pg184_workflow:
        fail(f"PG-184 selective warehouse workflow contract missing: {pg184_symbol}")

pg184_classifier = read(ROOT / "Scripts" / "classify_warehouse_validation.ps1")
for pg184_symbol in [
    "WAREHOUSE_CLASSIFY mode=selective",
    "WH_STAGE_AMBIENTCG",
    "WH_STAGE_KAYKIT",
    "WH_RUN_PREP",
    "SHIRE_WAREHOUSE_SOURCE",
    "WAREHOUSE_CLASSIFY_SOURCE",
    "WAREHOUSE_CHANGED_IGNORED",
    "WH_RUN_P1C01_PROMOTION",
    "WarehouseP1C01MegaPromotionTrainV1.json",
    "run_warehouse_p1c01_mega_promotion.ps1",
]:
    if pg184_symbol not in pg184_classifier:
        fail(f"PG-184 warehouse delta classifier missing: {pg184_symbol}")
for pg184_p1c01_symbol in [
    "Get-FileHash",
    "receipt_sha256_mismatch",
    "selected_archive_materialization_failed",
    "INTAKE_QC_PREPARED",
    "ready_for_import=$false",
    "P1C01_MEGA_PROMOTION_PASS_WITH_MANUAL_QUEUE",
    "System.IO.Compression.FileSystem",
]:
    if pg184_p1c01_symbol not in pg184_p1c01:
        fail(f"PG-184 P1C01 bounded warehouse promotion contract missing: {pg184_p1c01_symbol}")
for pg184_p1c01_manifest_symbol in [
    '"promotion_ceiling": "INTAKE_QC"',
    '"P1C01_SURFACES"',
    '"P1C01_ARCHITECTURE_PROPS"',
    '"P1C01_AUDIO_AMBIENCE_FOLEY"',
    '"P1C01_FAUNA"',
    '"P1C01_CHARACTER_ANIMATION_SUPPORT"',
]:
    if pg184_p1c01_manifest_symbol not in pg184_p1c01_manifest:
        fail(f"PG-184 P1C01 mega promotion manifest contract missing: {pg184_p1c01_manifest_symbol}")

pg184_material_intake = read(ROOT / "Scripts" / "prepare_p1c01_material_intake.ps1")
pg184_material_export = read(ROOT / "Scripts" / "export_p1c01_material_source_branch.ps1")
for pg184_material_symbol in [
    "Get-OptionalPropertyValue",
    "receipt_sha256_mismatch",
    "System.IO.Compression.FileSystem",
    "P1C01_MATERIAL_INTAKE_PASS_WITH_MANUAL_QUEUE",
]:
    if pg184_material_symbol not in pg184_material_intake:
        fail(f"PG-184 P1C01 material intake guard missing: {pg184_material_symbol}")
for pg184_export_symbol in [
    "generated/p1c01-material-source-v1",
    "SourceAssets\\Production\\Imported\\P1C01Materials",
    "MaxBatchSourceBytes",
    "SOURCE_READY_FOR_UE_IMPORT",
    "P1C01_MATERIAL_SOURCE_BRANCH_PASS",
    "[IO.Path]::IsPathRooted($ManifestPath)",
    "$ResolvedManifestPath",
    "Get-Content -LiteralPath $ResolvedManifestPath",
]:
    if pg184_export_symbol not in pg184_material_export:
        fail(f"PG-184 P1C01 material source export guard missing: {pg184_export_symbol}")
if "Get-Content -LiteralPath (Join-Path $ProjectRoot $ManifestPath)" in pg184_material_export:
    fail("PG-184 P1C01 material exporter must not re-join an already rooted manifest path")
for pg184_workflow_symbol in [
    "contents: write",
    "WH_RUN_P1C01_MATERIAL_EXPORT",
    "export_p1c01_material_source_branch.ps1",
]:
    if pg184_workflow_symbol not in pg184_workflow:
        fail(f"PG-184 P1C01 material export workflow contract missing: {pg184_workflow_symbol}")
if "WH_RUN_P1C01_MATERIAL_EXPORT" not in pg184_classifier:
    fail("PG-184 warehouse classifier must expose the P1C01 material export phase")

if "- 'Scripts/classify_warehouse_validation.ps1'" not in pg184_workflow:
    fail("PG-184 classifier changes must trigger one post-merge Warehouse control-plane proof")
if '".github/workflows/warehouse-stage.yml" {' not in pg184_classifier or "$flags.WH_RUN_AUDIT=$true" not in pg184_classifier:
    fail("PG-184 warehouse workflow-only changes must select bounded audit proof instead of full staging")

# PG-185: keep strict exact-head Unreal proof while preserving incremental build products.
pg185_unreal_workflow = read(ROOT / ".github" / "workflows" / "unreal-build-validation.yml")
pg185_classifier = read(ROOT / "Scripts" / "classify_unreal_validation.ps1")
pg185_pre = read(ROOT / ".github" / "workflows" / "pre-unreal-validation.yml")

if "if: env.SHIRE_RESET_INTERMEDIATES == 'true'" not in pg185_unreal_workflow:
    fail("PG-185 Unreal workflow must not wipe intermediates for every full validation")
for pg185_symbol in [
    "SHIRE_RESET_INTERMEDIATES",
    "CLEAN_COMPILE_REQUIRED",
    '.EndsWith(".Build.cs")',
    '.EndsWith(".Target.cs")',
]:
    if pg185_symbol not in pg185_classifier:
        fail(f"PG-185 incremental compile classifier contract missing: {pg185_symbol}")
for pg185_symbol in [
    "Scripts/run_warehouse_*.ps1",
    "Scripts/warehouse_network.ps1",
    "Scripts/classify_warehouse_validation.ps1",
]:
    if pg185_symbol not in pg185_unreal_workflow:
        fail(f"PG-185 warehouse-only changes must not trigger Unreal validation: {pg185_symbol}")
if "runs-on: windows-latest" not in pg185_pre:
    fail("PG-185 static Pre-Unreal validation must stay off the UE4 self-hosted runner")
if "- self-hosted" in pg185_pre:
    fail("PG-185 Pre-Unreal must not consume the supervised UE4 runner")

# PG-176: the monitored P1C01 material train must stay complete, bounded and
# evidence-gated. This is preparation validation only; it never promotes an item.
pg176_wave_path = ROOT / "Data" / "P1C01MaterialImportWaveV1.json"
if not pg176_wave_path.exists():
    fail("PG-176 P1C01 material import wave is missing")
else:
    try:
        pg176_wave = json.loads(read(pg176_wave_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-176 invalid P1C01 material import wave: {exc}")
        pg176_wave = {}

    pg176_items = pg176_wave.get("immediate_open_source_items", [])
    if len(pg176_items) != 16:
        fail(f"PG-176 expected 16 authorized Poly Haven surface items, found {len(pg176_items)}")

    pg176_ids = set()
    pg176_slugs = set()
    for pg176_item in pg176_items:
        pg176_id = str(pg176_item.get("id") or "").strip()
        pg176_provider = str(pg176_item.get("provider") or "").strip()
        pg176_slug = str(pg176_item.get("asset_slug") or "").strip()
        pg176_material = str(pg176_item.get("material_name") or "").strip()
        pg176_state = str(pg176_item.get("state") or "").strip()
        pg176_roughness = pg176_item.get("roughness")
        pg176_metallic = pg176_item.get("metallic")
        pg176_specular = pg176_item.get("specular")

        if not pg176_id or not pg176_slug or not pg176_material:
            fail("PG-176 material wave item missing id/asset_slug/material_name")
            continue
        if pg176_id in pg176_ids:
            fail(f"PG-176 duplicate material-wave id: {pg176_id}")
        pg176_ids.add(pg176_id)
        if pg176_slug in pg176_slugs:
            fail(f"PG-176 duplicate material-wave asset slug: {pg176_slug}")
        pg176_slugs.add(pg176_slug)
        if pg176_provider != "POLY_HAVEN":
            fail(f"PG-176 unsupported immediate provider for {pg176_id}: {pg176_provider}")
        if pg176_state != "AUTHORIZED_FOR_STAGING":
            fail(f"PG-176 {pg176_id} must remain AUTHORIZED_FOR_STAGING before receipt-backed intake")
        if not isinstance(pg176_roughness, (int, float)) or not 0.0 <= float(pg176_roughness) <= 1.0:
            fail(f"PG-176 {pg176_id} roughness out of bounds")
        if not isinstance(pg176_metallic, (int, float)) or not 0.0 <= float(pg176_metallic) <= 1.0:
            fail(f"PG-176 {pg176_id} metallic out of bounds")
        if not isinstance(pg176_specular, (int, float)) or not 0.02 <= float(pg176_specular) <= 0.65:
            fail(f"PG-176 {pg176_id} specular out of bounds")

    pg176_authorized_slugs = {
        str(item.get("id") or "").strip()
        for item in pg173_queue.get("groups", {}).get("surfaces_and_ground", [])
        if str(item.get("state") or "") == "AUTHORIZED_FOR_STAGING"
    }
    pg176_missing_authority = sorted(pg176_slugs - pg176_authorized_slugs)
    if pg176_missing_authority:
        fail("PG-176 material-wave slugs missing AUTHORIZED_FOR_STAGING queue authority: " + ", ".join(pg176_missing_authority))

    pg176_bind_now = set(pg176_wave.get("current_master_limit", {}).get("bind_now", []))
    for pg176_parameter in ["AlbedoTexture", "Color", "Roughness scalar", "Metallic scalar", "Specular scalar"]:
        if pg176_parameter not in pg176_bind_now:
            fail(f"PG-176 low-spec material master contract missing {pg176_parameter}")

    pg176_prepare = read(ROOT / "Scripts" / "prepare_p1c01_material_intake.ps1")
    for pg176_marker in [
        "Get-FileHash -LiteralPath $dest -Algorithm SHA256",
        '"Ks $ksText $ksText $ksText"',
        'state="INTAKE_QC_PREPARED"',
        "forbidden_bmp",
    ]:
        if pg176_marker not in pg176_prepare:
            fail(f"PG-176 material intake preparation guard missing: {pg176_marker}")


# PG-179: long warehouse saturation train remains ordered, evidence-gated and non-chaotic.
pg179_path = ROOT / "Data" / "WarehouseSaturationTrainV1.json"
if not pg179_path.exists():
    fail("PG-179 warehouse saturation train manifest missing")
else:
    try:
        pg179 = json.loads(read(pg179_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-179 invalid warehouse saturation train manifest: {exc}")
        pg179 = {}

    pg179_cars = pg179.get("cars", [])
    if len(pg179_cars) != 20:
        fail(f"PG-179 expected exactly 20 ordered warehouse cars, found {len(pg179_cars)}")

    pg179_orders = [int(car.get("order", -1)) for car in pg179_cars]
    if pg179_orders != list(range(1, 21)):
        fail("PG-179 warehouse car order must remain exactly 1..20")

    pg179_ids = [str(car.get("id") or "").strip() for car in pg179_cars]
    if len(set(pg179_ids)) != len(pg179_ids) or any(not value for value in pg179_ids):
        fail("PG-179 warehouse car IDs must be unique and non-empty")

    pg179_allowed_ceilings = {"CANDIDATE", "INTAKE_QC", "STATIC_VALIDATED"}
    for car in pg179_cars:
        if str(car.get("ceiling") or "") not in pg179_allowed_ceilings:
            fail(f"PG-179 preparation car has unsafe promotion ceiling: {car.get('id')}")
        if not car.get("providers") or len(car.get("providers", [])) > 4:
            fail(f"PG-179 car must keep a bounded source set (1-4 providers): {car.get('id')}")

    for required_rule in [
        "Do not mirror entire providers indiscriminately.",
        "Animated final production assets must be FBX.",
        "Production textures must be PNG/TGA; use channel packing where appropriate; BMP is forbidden.",
        "Audio production masters must be WAV before UE import.",
        "Heavy runtime assets remain soft referenced and asynchronously loaded with FStreamableManager.",
    ]:
        if required_rule not in pg179.get("global_rules", []):
            fail(f"PG-179 warehouse saturation safety rule missing: {required_rule}")

pg179_script = read(ROOT / "Scripts" / "run_warehouse_saturation_train.ps1")
for marker in [
    "WAREHOUSE_SATURATION_STAGE_START",
    "Get-FileHash -LiteralPath $path -Algorithm SHA256",
    "STAGED_RECEIPT_VERIFIED",
    "PUBLIC_LANE_PENDING_STAGE",
    "MANUAL_OR_AUTH_SOURCE_PENDING",
    "No car becomes READY_FOR_IMPORT from this report.",
]:
    if marker not in pg179_script:
        fail(f"PG-179 warehouse saturation orchestrator guard missing: {marker}")


# PG-180: consolidated P1C01 prep cars from superseded #119/#120 remain present and fail-closed.
for pg180_rel in [
    "Data/P1C01ArchitectureInteriorPropMegabatchV1.json",
    "Scripts/prepare_p1c01_architecture_intake.ps1",
    "Data/P1C01CharacterRigAnimationPrepV1.json",
    "Scripts/prepare_p1c01_character_rig_intake.ps1",
    "Data/P1C01AudioFoleyAmbiencePrepV1.json",
    "Scripts/prepare_p1c01_audio_intake.ps1",
    "Data/P1C01LivingWorldFaunaPrepV1.json",
    "Scripts/prepare_p1c01_fauna_intake.ps1",
]:
    if not (ROOT / pg180_rel).exists():
        fail(f"PG-180 consolidated prep artifact missing: {pg180_rel}")

pg180_arch = json.loads(read(ROOT / "Data" / "P1C01ArchitectureInteriorPropMegabatchV1.json"))
if len(pg180_arch.get("external_items", [])) != 6:
    fail("PG-180 architecture/interior prep must retain the authorized six-pack scope")
for item in pg180_arch.get("external_items", []):
    if item.get("state") != "AUTHORIZED_FOR_STAGING" or item.get("license") != "CC0":
        fail(f"PG-180 architecture support item lost authorized CC0 state: {item.get('id')}")
    if item.get("final_exchange") != "FBX":
        fail(f"PG-180 architecture support final exchange must remain FBX: {item.get('id')}")

pg180_char = json.loads(read(ROOT / "Data" / "P1C01CharacterRigAnimationPrepV1.json"))
if pg180_char.get("required_bundle", {}).get("skeletal_mesh") != "FBX":
    fail("PG-180 character rig prep lost FBX-only skeletal requirement")
if "OBJ_AS_FINAL_ANIMATED_CHARACTER" not in pg180_char.get("forbidden", []):
    fail("PG-180 character prep lost animated OBJ prohibition")

pg180_audio = json.loads(read(ROOT / "Data" / "P1C01AudioFoleyAmbiencePrepV1.json"))
if len(pg180_audio.get("items", [])) != 5:
    fail("PG-180 audio prep must retain exactly five authorized P1C01 items")
for item in pg180_audio.get("items", []):
    if item.get("license") != "CC0" or item.get("master_requirement") != "WAV":
        fail(f"PG-180 audio prep lost CC0/WAV contract: {item.get('id')}")

pg180_fauna = json.loads(read(ROOT / "Data" / "P1C01LivingWorldFaunaPrepV1.json"))
pg180_caps = pg180_fauna.get("living_world_caps", {})
if pg180_caps.get("max_active_fauna_groups_near_player") != 2 or pg180_caps.get("fauna_cull_distance_cm") != 4200:
    fail("PG-180 fauna prep drifted from current LivingWorld caps")
for item in pg180_fauna.get("external_candidates", []):
    if item.get("state") != "BLOCKED_LICENSE_CAPTURE":
        fail(f"PG-180 fauna candidate advanced without explicit license capture: {item.get('id')}")

pg180_character_intake = read(ROOT / "Scripts" / "prepare_p1c01_character_rig_intake.ps1")
for marker in [
    "Get-OptionalPropertyValue",
    '"archive"',
    '"archive_sha256"',
    "System.IO.Compression.FileSystem",
]:
    if marker not in pg180_character_intake:
        fail(f"PG-180 character intake heterogeneous-receipt/ZIP runtime guard missing: {marker}")

pg180_scripts = "\n".join([
    read(ROOT / "Scripts" / "prepare_p1c01_architecture_intake.ps1"),
    read(ROOT / "Scripts" / "prepare_p1c01_character_rig_intake.ps1"),
    read(ROOT / "Scripts" / "prepare_p1c01_audio_intake.ps1"),
    read(ROOT / "Scripts" / "prepare_p1c01_fauna_intake.ps1"),
])
for marker in [
    "receipt_sha256_mismatch",
    "forbidden_bmp",
    "ready_for_import=$false",
    "STAGED_NEEDS_WAV_MASTER",
    "license_capture_required_before_staging",
]:
    if marker not in pg180_scripts:
        fail(f"PG-180 consolidated prep guard missing: {marker}")


# PG-181: critical-gap preparation train V2 must remain 20-car, evidence-gated and non-promoting.
pg181_path = ROOT / "Data" / "WarehouseCriticalGapPreparationTrainV2.json"
if not pg181_path.exists():
    fail("PG-181 critical-gap preparation manifest missing")
else:
    try:
        pg181 = json.loads(read(pg181_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-181 invalid critical-gap preparation manifest: {exc}")
        pg181 = {}

    pg181_cars = pg181.get("cars", [])
    if len(pg181_cars) != 20:
        fail(f"PG-181 expected 20 critical-gap preparation cars, found {len(pg181_cars)}")
    pg181_orders = [int(car.get("order", -1)) for car in pg181_cars]
    if pg181_orders != list(range(1, 21)):
        fail("PG-181 critical-gap car order must remain exactly 1..20")
    for car in pg181_cars:
        if car.get("ceiling") != "INTAKE_QC":
            fail(f"PG-181 preparation ceiling drifted beyond INTAKE_QC: {car.get('id')}")

    for required_rule in [
        "Verify staged source receipt SHA256 before extracting or classifying.",
        "Block executable/script payloads and BMP textures from production intake.",
        "Animated character/creature/fauna final production assets require FBX.",
        "Production textures accepted by the project are PNG/TGA; channel-packing debt remains explicit until actually authored.",
        "Audio production masters require WAV before UE import.",
        "No processing car may promote an item to READY_FOR_IMPORT without class-specific QC.",
    ]:
        if required_rule not in pg181.get("global_rules", []):
            fail(f"PG-181 critical-gap safety rule missing: {required_rule}")

pg181_script = read(ROOT / "Scripts" / "run_warehouse_critical_gap_preparation.ps1")
for marker in [
    "Get-FileHash -LiteralPath $row.path -Algorithm SHA256",
    "receipt_sha256_mismatch",
    "forbidden_bmp",
    "archive_requires_approved_extractor",
    "FBX_CHARACTER_CANDIDATE",
    "FBX_ANIMATION_CANDIDATE",
    "FBX_CREATURE_FAUNA_CANDIDATE",
    "AUDIO_WAV_MASTER_CANDIDATE",
    "No file is promoted to READY_FOR_IMPORT by this report.",
]:
    if marker not in pg181_script:
        fail(f"PG-181 critical-gap processor guard missing: {marker}")


# PG-182: provider-resolution V3 must remain bounded and must never bypass provider access policy.
pg182_path = ROOT / "Data" / "WarehouseProviderResolutionTrainV3.json"
if not pg182_path.exists():
    fail("PG-182 provider-resolution train manifest missing")
else:
    try:
        pg182 = json.loads(read(pg182_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-182 invalid provider-resolution train manifest: {exc}")
        pg182 = {}

    pg182_cars = pg182.get("cars", [])
    if len(pg182_cars) != 20:
        fail(f"PG-182 expected 20 provider-resolution cars, found {len(pg182_cars)}")
    if [int(car.get("order", -1)) for car in pg182_cars] != list(range(1, 21)):
        fail("PG-182 provider-resolution car order must remain 1..20")
    for car in pg182_cars:
        if len(car.get("preferred", [])) > 3:
            fail(f"PG-182 preferred provider fan-out exceeds 3: {car.get('id')}")
        if len(car.get("fallback", [])) > 3:
            fail(f"PG-182 fallback provider fan-out exceeds 3: {car.get('id')}")
        if car.get("ceiling") not in {"CANDIDATE", "AUTHORIZED_FOR_STAGING", "STATIC_VALIDATED"}:
            fail(f"PG-182 unsafe provider-resolution ceiling: {car.get('id')}")

    for rule in [
        "Never convert AUTH, REVIEW, PURCHASE, MARKETPLACE or REFERENCE lanes into automatic download lanes.",
        "Animated final production stock requires FBX.",
        "Production textures require PNG/TGA.",
        "Audio production masters require WAV.",
        "Provider resolution cannot promote READY_FOR_IMPORT.",
    ]:
        if rule not in pg182.get("rules", []):
            fail(f"PG-182 provider-resolution safety rule missing: {rule}")

pg182_script = read(ROOT / "Scripts" / "run_warehouse_provider_resolution.ps1")
for marker in [
    "AUTH_REQUIRED",
    "REVIEW_REQUIRED",
    "MANUAL_ONLY",
    "REFERENCE_ONLY",
    "AUTO_PROVIDER_AVAILABLE",
    "STAGED_PROVIDER_AVAILABLE",
    "Provider resolution never promotes READY_FOR_IMPORT.",
]:
    if marker not in pg182_script:
        fail(f"PG-182 provider-resolution processor guard missing: {marker}")


# PG-164: Hobbiton and Bag End architecture must preserve canon/presentation boundaries.
pg164_h = read(resolve_source("ShirePrototypeWorldBuilder.h"))
pg164_cpp = read(resolve_source("ShirePrototypeWorldBuilder.cpp"))
for pg164_symbol in [
    "SpawnHobbitonArchitecturePass",
    'TEXT("ShireArchitecture: DropB',
    'TEXT("Hobbiton Village Common")',
    'TEXT("Discovered: Hobbiton village common.")',
]:
    if pg164_symbol not in (pg164_h + pg164_cpp):
        fail(f"PG-164 P1C01 Hobbiton architecture invariant missing: {pg164_symbol}")

for pg164_bad_visible in [
    'FText::FromString(TEXT("The Green Dragon"))',
    'TEXT("Discovered: The Green Dragon',
]:
    if pg164_bad_visible in pg164_cpp:
        fail(f"PG-164 canonical Bywater inn is still presented as Hobbiton content: {pg164_bad_visible}")

pg164_plan = json.loads(read(ROOT / "Data" / "P1C01HobbitonArchitecturePlanV1.json"))
if pg164_plan.get("status") not in {
    "DROP_B_ACTIVE",
    "DROP_B_IMPLEMENTED_PENDING_EXACT_HEAD_ENGINE_PROOF",
}:
    fail("PG-164 Hobbiton/Bag End architecture plan status changed")

if "Discover_GreenDragon" not in pg164_cpp:
    fail("PG-164 legacy discovery ID disappeared; preserve save compatibility while correcting visible copy")


# PG-163: P1C01 production geography must stay instanced, bounded and story-safe.
pg163_shire_h = read(resolve_source("ShirePrototypeWorldBuilder.h"))
pg163_shire_cpp = read(resolve_source("ShirePrototypeWorldBuilder.cpp"))
for pg163_symbol in [
    "GeographyHillInstances",
    "GeographySlopeInstances",
    "GeographyRiverBankInstances",
    "SpawnGeographyFoundationPass",
    "GeographyHillInstances->AddInstance",
    "GeographySlopeInstances->AddInstance",
    "GeographyRiverBankInstances->AddInstance",
    "GeographyHillInstances->SetCullDistances",
    "GeographySlopeInstances->SetCullDistances",
    "GeographyRiverBankInstances->SetCullDistances",
    'TEXT("ShireWorldFoundation: geography-pass',
]:
    if pg163_symbol not in (pg163_shire_h + pg163_shire_cpp):
        fail(f"PG-163 P1C01 geography foundation invariant missing: {pg163_symbol}")

for pg163_actor_spawn in [
    "SpawnShape(ProductionCommonTerracedHillMesh",
    "SpawnShape(ProductionCommonVillageSlopeMesh",
    "SpawnShape(ProductionCommonRiverBankMesh",
]:
    if pg163_actor_spawn in pg163_shire_cpp:
        fail(f"PG-163 repeated geography regressed to actor spawning: {pg163_actor_spawn}")

pg163_perf = json.loads(read(ROOT / "Data" / "AssetPerformanceBudget.json"))
if pg163_perf.get("p1c01_world_foundation", {}).get("status") != "IMPLEMENTED_PENDING_TARGET_DEVICE_MEASUREMENT":
    fail("PG-163 P1C01 geography performance evidence boundary changed")

pg163_foundation = json.loads(read(ROOT / "Data" / "TrilogyWorldFoundationPlanV1.json"))
pg163_slice = pg163_foundation.get("p1c01_vertical_slice", {})
if pg163_slice.get("status") != "DROP_A_TERRAIN_GEOGRAPHY_IMPLEMENTED_PENDING_EXACT_HEAD_ENGINE_PROOF":
    fail("PG-163 P1C01 world-foundation drop status changed")
if pg163_slice.get("ordered_drops", [None])[0] != "A_TERRAIN_GEOGRAPHY_FOUNDATION":
    fail("PG-163 P1C01 ordered production sequence changed")


# PG-048: resource sources, service partners and rights holders must not be conflated.
rights_plan_path = ROOT / "Data" / "RightsHolderContactPlan.json"
rights_plan = {}
if not rights_plan_path.exists():
    fail("PG-048 rights-holder contact plan missing")
else:
    try:
        rights_plan = json.loads(read(rights_plan_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-048 invalid RightsHolderContactPlan.json: {exc}")

if rights_plan and rights_plan.get("authority_id") != "FELLOWSHIP_RIGHTS_HOLDER_CONTACT_PLAN_V1":
    fail("PG-048 rights-holder contact plan has unexpected authority_id")

contact_roles = {
    str(item.get("id") or ""): str(item.get("role") or "")
    for item in rights_plan.get("contacts", [])
    if isinstance(item, dict)
}
for required_contact in [
    "MIDDLE_EARTH_ENTERPRISES",
    "WETA_WORKSHOP",
    "WARNER_BROS_NEW_LINE",
    "TOLKIEN_ESTATE",
    "HARPERCOLLINS_PERMISSIONS",
]:
    if required_contact not in contact_roles:
        fail(f"PG-048 missing rights/service contact: {required_contact}")

if contact_roles.get("WETA_WORKSHOP") == "PRIMARY_GAME_AND_LOTR_HOBBIT_LICENSING_RIGHTS_CONTACT":
    fail("PG-048 Weta Workshop must not be classified as the primary Tolkien game-rights licensor")
if contact_roles.get("MIDDLE_EARTH_ENTERPRISES") != "PRIMARY_GAME_AND_LOTR_HOBBIT_LICENSING_RIGHTS_CONTACT":
    fail("PG-048 Middle-earth Enterprises must remain the primary recorded LOTR/Hobbit game licensing contact")

# PG-047: external production assets must remain license/provenance gated.
external_manifest_path = ROOT / "Data" / "ExternalAssetManifest.json"
external_manifest = {}
if not external_manifest_path.exists():
    fail("PG-047 external asset manifest missing: Data/ExternalAssetManifest.json")
else:
    try:
        external_manifest = json.loads(read(external_manifest_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-047 invalid ExternalAssetManifest.json: {exc}")

if external_manifest and external_manifest.get("authority_id") != "FELLOWSHIP_EXTERNAL_ASSET_MANIFEST_V1":
    fail("PG-047 external asset manifest has unexpected authority_id")

provider_modes = {
    str(p.get("id") or ""): str(p.get("mode") or "")
    for p in external_manifest.get("providers", [])
    if isinstance(p, dict)
}
for provider_id in ["FAB", "QUixel_MEGASCANS", "SKETCHFAB", "TURBOSQUID", "SONNISS", "FREESOUND", "ARTSTATION", "TOLKIEN_GATEWAY"]:
    if provider_id not in provider_modes:
        fail(f"PG-047 provider policy missing: {provider_id}")

for reference_provider in ["ARTSTATION", "TOLKIEN_GATEWAY", "LOTR_WIKI"]:
    if provider_modes.get(reference_provider) != "REFERENCE_ONLY":
        fail(f"PG-047 reference-only provider drifted: {reference_provider}")

resource_provider_modes = {
    str(p.get("id") or ""): str(p.get("mode") or "")
    for p in external_manifest.get("providers", [])
    if isinstance(p, dict)
}
for provider_id in ["WETA_WORKSHOP", "POLY_HAVEN", "AMBIENTCG", "ADOBE_MIXAMO", "ACTORCORE_REALLUSION", "KENNEY"]:
    if provider_id not in resource_provider_modes:
        fail(f"PG-048 expanded resource provider missing: {provider_id}")
if resource_provider_modes.get("WETA_WORKSHOP") != "SERVICE_OR_COMMISSION_ONLY":
    fail("PG-048 Weta Workshop provider mode must remain SERVICE_OR_COMMISSION_ONLY")

blocked_license_tokens = {"EDITORIAL", "CC_BY_NC", "CC_BY_ND", "UNKNOWN"}
approved_external_root = ROOT / "SourceAssets" / "ExternalLicensed" / "Approved"
asset_records = external_manifest.get("assets", [])
record_by_path = {
    str(item.get("relative_path") or "").replace("\\", "/"): item
    for item in asset_records
    if isinstance(item, dict)
}
for item in asset_records:
    if not isinstance(item, dict):
        fail("PG-047 external asset manifest contains non-object asset entry")
        continue
    for field in ["asset_id", "provider", "relative_path", "license_class", "acquired_on", "source_url", "approval_status"]:
        if not str(item.get(field) or "").strip():
            fail(f"PG-047 external asset record missing {field}: {item}")
    license_class = str(item.get("license_class") or "").upper()
    if any(token in license_class for token in blocked_license_tokens):
        fail(f"PG-047 blocked license class in approved asset record: {license_class}")
    if str(item.get("approval_status") or "") != "APPROVED":
        fail(f"PG-047 production manifest asset is not APPROVED: {item.get('asset_id')}")

if approved_external_root.exists():
    for path in approved_external_root.rglob("*"):
        if not path.is_file() or path.name.lower() == "readme.md":
            continue
        relative = str(path.relative_to(ROOT)).replace("\\", "/")
        if relative not in record_by_path:
            fail(f"PG-047 approved external file has no manifest record: {relative}")

# PG-016: the installed UE4.27.2 build does not expose Engine/AtmosphericFog.h
# as a public include. Cleanup of a legacy AtmosphericFog actor must avoid a direct
# dependency on that header/class so real Windows compilation cannot regress to C1083.
shire_world_for_headers = read(resolve_source("ShirePrototypeWorldBuilder.cpp"))
if '#include "Engine/AtmosphericFog.h"' in shire_world_for_headers:
    fail("PG-016: do not include Engine/AtmosphericFog.h on the locked UE4.27.2 toolchain")

# PG-017: files covered by .gitattributes LFS rules must be actual LFS pointers in Git.
# Raw binary blobs under an LFS-tracked extension make checkout report "should have been
# pointers, but weren't" and make the self-hosted workspace nondeterministic.
production_root = ROOT / "SourceAssets" / "Production"
lfs_extensions = {".uasset", ".umap", ".fbx", ".wav", ".png", ".exr"}
if production_root.exists():
    for asset_path in production_root.rglob("*"):
        if asset_path.is_file() and asset_path.suffix.lower() in lfs_extensions:
            if not is_git_lfs_pointer(asset_path):
                fail(
                    "PG-017: LFS-tracked production asset is committed as a raw blob: "
                    + str(asset_path.relative_to(ROOT))
                )

# Small TGA source textures are intentionally stored as regular Git blobs so the
# source bank remains self-contained without a hidden LFS object dependency. Large
# texture payloads must use PNG/LFS or be reduced/channel-packed before admission.
raw_tga_limit_bytes = 512 * 1024
for tga_path in production_root.rglob("*.tga"):
    if tga_path.stat().st_size > raw_tga_limit_bytes:
        fail(
            "PG-017: raw TGA exceeds 512 KiB source cap; reduce/channel-pack or use PNG/LFS: "
            + str(tga_path.relative_to(ROOT))
        )

# PG-125: source texture format is a hard pipeline rule, not a convention.
legacy_bmp_sources = sorted(production_root.rglob("*.bmp"))
if legacy_bmp_sources:
    fail(
        "PG-125 forbidden BMP production textures: "
        + ", ".join(str(path.relative_to(ROOT)) for path in legacy_bmp_sources[:12])
    )

# PG-013: UE4.27 UAssetImportTask does not expose bAsync. Keep the production
# import commandlet on the UE4.27-compatible task API so the real editor build
# cannot regress to C2039 before asset import even begins.
production_import_cpp = read(
    ROOT / "Source" / "ShireJourneyEditorTools" / "Private" / "ShireProductionImportCommandlet.cpp"
)
if "Task->bAsync" in production_import_cpp or "->bAsync" in production_import_cpp:
    fail("PG-013: UE4.27 UAssetImportTask must not use unsupported bAsync")
if "Task->ImportedObjectPaths.Num() > 0" not in production_import_cpp:
    fail("Production importer must inspect UE4.27 task path results")
if "Task->Result.Num() > 0" not in production_import_cpp:
    fail("Production importer must inspect UE4.27 task object results")
if "LoadObject<UObject>(nullptr, *ExpectedObjectPath)" not in production_import_cpp:
    fail("Production importer must verify the expected imported object path")

# PG-015: cmd.exe preserves the previous command's ERRORLEVEL. The self-hosted
# runner's "editor is closed" probe uses tasklist/find, which leaves ERRORLEVEL=1
# when no editor exists. The success branch must explicitly return 0 or Actions
# reports a false failure and skips the actual UE build.
unreal_ci = read(ROOT / ".github" / "workflows" / "unreal-build-validation.yml")
editor_probe_marker = "echo Unreal Editor is closed.\n          exit /b 0"
editor_wait_script_path = ROOT / "Scripts" / "ci_wait_for_unreal_editor.cmd"
editor_wait_script = read(editor_wait_script_path) if editor_wait_script_path.exists() else ""
shared_waiter_path = ROOT / "Scripts" / "wait_for_unreal_processes.ps1"
shared_waiter = read(shared_waiter_path) if shared_waiter_path.exists() else ""
editor_wait_contract_ok = (
    (
        "Get-Process -Name UE4Editor" in unreal_ci
        and "AddMinutes(20)" in unreal_ci
        and "Start-Sleep -Seconds 10" in unreal_ci
        and "exit 40" in unreal_ci
    )
    or (
        "ci_wait_for_unreal_editor.cmd" in unreal_ci
        and "wait_for_unreal_processes.ps1" in editor_wait_script
        and '@("UE4Editor","UE4Editor-Cmd")' in shared_waiter
        and "UNREAL_PROCESS_WAIT_TIMEOUT" in shared_waiter
        and "policy=never-kill-interactive-editor" in shared_waiter
        and "Test-StaleOwnedCommandlet" in shared_waiter
        and "sameOwner" in shared_waiter
    )
)
if editor_probe_marker not in unreal_ci and not editor_wait_contract_ok:
    fail("PG-015: Unreal self-hosted validation must either prove the editor is closed or wait safely for it without terminating the user's editor")
checkout_action_ok = (
    "uses: actions/checkout@v4" in unreal_ci
    and (
        "ref: ${{ env.TARGET_SHA }}" in unreal_ci
        or "ref: ${{ github.event.pull_request.head.sha || github.sha }}" in unreal_ci
    )
    and "persist-credentials: false" in unreal_ci
    and "git rev-parse HEAD" in unreal_ci
    and "Checkout SHA mismatch" in unreal_ci
)
stable_checkout_ok = (
    "fellowship_exact_checkout.cmd" in unreal_ci
    and re.search(
        r"fetch --no-tags --prune --depth=(?:1|2) origin %%TARGET_SHA%%",
        unreal_ci,
    ) is not None
    and "reset --hard %%TARGET_SHA%%" in unreal_ci
    and "rev-parse HEAD" in unreal_ci
    and "Checkout SHA mismatch" in unreal_ci
    and ".ci-source-sha" in unreal_ci
    and "ShireJourney.uproject missing after exact checkout" in unreal_ci
)
exact_checkout_markers = [
    "zipball/$env:GITHUB_SHA",
    "GET /repos/{owner}/{repo}/zipball/{ref}",
    "git fetch --no-tags --prune --depth=1 origin %GITHUB_SHA%",
    "git fetch --no-tags --prune --depth=1 origin %TARGET_SHA%",
    "& git fetch --no-tags --prune --depth=1 origin $env:TARGET_SHA",
]
custom_checkout_ok = stable_checkout_ok or any(marker in unreal_ci for marker in exact_checkout_markers)
if not checkout_action_ok and not custom_checkout_ok:
    fail("PG-026: Unreal self-hosted build must acquire and verify the exact validated PR-head SHA")
if "TARGET_SHA: ${{ github.event.pull_request.head.sha || github.sha }}" not in unreal_ci:
    fail("PG-026: pull-request Unreal validation must resolve TARGET_SHA to the PR head, not the synthetic merge commit")
retry_contract_ok = (
    ("--retry 6" in unreal_ci and "--retry-all-errors" in unreal_ci)
    or ("attempt <= 7" in unreal_ci and "retrying in 5 seconds" in unreal_ci)
    or ("for /L %%A in (1,1,7)" in unreal_ci and "Start-Sleep -Seconds 5" in unreal_ci)
    or ("$attempt -le 7" in unreal_ci and "Start-Sleep -Seconds 5" in unreal_ci)
    or ("if %%ATTEMPT%% GEQ 7 exit /b 72" in unreal_ci and "goto fetch" in unreal_ci)
    or (
        "if %%ATTEMPT%% GEQ 3 exit /b 72" in unreal_ci
        and "http.lowSpeedLimit=1000" in unreal_ci
        and "http.lowSpeedTime=20" in unreal_ci
        and "goto fetch" in unreal_ci
    )
)
if custom_checkout_ok and not retry_contract_ok:
    fail("PG-026: custom exact-commit acquisition must use bounded resilient retries")
if "uses: actions/upload-artifact@v4" in unreal_ci:
    fail("PG-026: failure logging must not depend on artifact upload while storage quota can mask the primary error")
concurrency_group_ok = (
    "group: unreal-build-${{ github.repository }}-${{ github.event_name == 'pull_request' && github.head_ref || 'develop' }}" in unreal_ci
    or "group: unreal-build-${{ github.repository }}-ue4-device" in unreal_ci
)
cancel_values = [
    value.strip()
    for value in re.findall(r"(?m)^\s*cancel-in-progress:\s*(.+?)\s*$", unreal_ci)
]
allowed_cancel_values = {
    "false",
    "${{ github.event_name == 'pull_request' }}",
    "${{ startsWith(github.head_ref, 'acceptance/') }}",
    "group: unreal-build-${{ github.repository }}-${{ github.event_name == 'pull_request' && github.head_ref || 'develop' }}",
    "cancel-in-progress: ${{ github.event_name == 'pull_request' }}",
}
if (
    not concurrency_group_ok
    or len(cancel_values) != 1
    or cancel_values[0] not in allowed_cancel_values
):
    fail(
        "PG-026: Unreal validation concurrency must preserve the single physical device while "
        "cancelling only superseded work from the same PR branch"
    )
if "group: unreal-build-${{ github.repository }}-ue4-device" in unreal_ci and "cancel-in-progress: true" in unreal_ci:
    fail("PG-026: unconditional shared-device cancellation across unrelated branches is forbidden")

packaging_config = read(ROOT / "Config" / "DefaultGame.ini")
for required_cook_dir in (
    '+DirectoriesToAlwaysCook=(Path="/Game/Production/Materials")',
    '+DirectoriesToAlwaysCook=(Path="/Game/Production/World")',
    '+DirectoriesToAlwaysCook=(Path="/Game/Production/Characters/Common")',
    '+DirectoriesToAlwaysCook=(Path="/Game/Production/Characters/Hobbit")',
    '+DirectoriesToAlwaysCook=(Path="/Game/Production/Enemies")',
):
    if required_cook_dir not in packaging_config:
        fail("PG-026: dynamic production streaming banks must be included in packaged cook directories")

package_script = read(ROOT / "Scripts" / "ci_package_w00.ps1")
if (
    "CI-W00-Package-wrapper.cmd" not in package_script
    or "CI-W00-Package-exitcode.txt" not in package_script
    or "SHIRE_UAT_EXIT=%ERRORLEVEL%" not in package_script
    or "W00_PACKAGE_RESULT_MISSING" not in package_script
    or "[int]::TryParse" not in package_script
    or "W00_PACKAGE_EXITCODE source=cmd-sidecar" not in package_script
    or "exit $exitCode" not in package_script
):
    fail(
        "PG-026: W00 package wrapper must capture synchronous RunUAT ERRORLEVEL "
        "through the cmd sidecar contract"
    )
if "$proc.ExitCode" in package_script:
    fail("PG-026: W00 package wrapper must not trust Start-Process .ExitCode for RunUAT.bat")
if (
    "W00_STREAMING_ASSET_PREFLIGHT_PASS" not in package_script
    or "W00_STREAMING_PLAN_COUNT_MISMATCH" not in package_script
    or "W00_STREAMING_ASSET_PREFLIGHT_FAIL" not in package_script
):
    fail("PG-026: package must fail fast if generated production streaming assets are absent before cook")

startup_verifier = read(ROOT / "Scripts" / "verify_packaged_startup.ps1")
if (
    '$text = ""' not in startup_verifier
    or "$rawText = Get-Content" not in startup_verifier
    or "if ($null -ne $rawText)" not in startup_verifier
):
    fail("PG-026: packaged startup verifier must tolerate an existing but still-empty log file")

if (
    "SHIRE_ACCEPTANCE_RESUME_STAGE" not in unreal_ci
    or "Validate inherited packaged artifact" not in unreal_ci
    or "W00_INHERITED_PACKAGE_DATA_PASS" not in unreal_ci
    or "PARENT_ACCEPTANCE_DATA_PROOF_PASS" not in read(ROOT / "Scripts" / "classify_unreal_validation.ps1")
):
    fail("PG-026: startup-verifier-only acceptance must resume after proven parent package/data gates")

# PG-157: one canonical interactive branch and no silent local branch switching.
local_update = read(ROOT / "SHIRE_UPDATE_BUILD_LAUNCH.bat")
local_pie = read(ROOT / "SHIRE_PIE_VERIFY.bat")
for forbidden in ["git checkout develop", "checkout develop", "Synchronizing exact develop head"]:
    if forbidden.lower() in local_update.lower() or forbidden.lower() in local_pie.lower():
        fail(f"PG-157: local helper silently switches branch: {forbidden}")
for required in [
    "RUNNER_WORKSPACE_BLOCKED",
    "CANONICAL_BRANCH_REQUIRED",
    'if /I not "!ACTIVE_BRANCH!"=="develop"',
    'pull --ff-only origin develop',
]:
    if required not in local_update:
        fail(f"PG-157: canonical develop update/build helper contract missing: {required}")
for required in [
    "DEVELOP PIE VERIFICATION",
    "RUNNER_WORKSPACE_BLOCKED",
    "CANONICAL_BRANCH_REQUIRED",
    'if /I not "!TESTED_BRANCH!"=="develop"',
]:
    if required not in local_pie:
        fail(f"PG-157: canonical develop PIE helper contract missing: {required}")

# PG-158: exact-head runner source tree must be present immediately before UBT.
source_integrity = read(ROOT / "Scripts" / "verify_runtime_source_workspace.ps1")
for required in [
    "RUNTIME_SOURCE_WORKSPACE_REPAIR_BEGIN",
    "RUNTIME_SOURCE_WORKSPACE_RESTORE",
    "RUNTIME_SOURCE_WORKSPACE_INTEGRITY_PASS",
    "RUNTIME_SOURCE_ARCHITECTURE_TARGET_MISSING",
    "git checkout HEAD",
]:
    if required not in source_integrity:
        fail(f"PG-158: runtime source workspace integrity contract missing: {required}")
if "Verify runtime source workspace integrity" not in unreal_ci:
    fail("PG-158: Unreal workflow must validate/repair the exact tracked source tree immediately before build")

classifier_guard = read(ROOT / "Scripts" / "classify_unreal_validation.ps1")
if "source=transitive-governance" not in classifier_guard:
    fail("PG-158: governance-only green parents must preserve transitive core Unreal proof")

# PG-159: deprecated StaticMaterials access must not return.
pg159_importer = read(ROOT / "Source" / "ShireJourneyEditorTools" / "Private" / "ShireProductionImportCommandlet.cpp")
if re.search(r'(?:->|\.)StaticMaterials\b', pg159_importer):
    fail("PG-159: direct UStaticMesh::StaticMaterials access is deprecated; use GetStaticMaterials/SetStaticMaterials")
if "GetStaticMaterials()" not in pg159_importer:
    fail("PG-159: production importer must use GetStaticMaterials()")

# PG-161: validation evidence may be reused only across safe governance/metadata ancestry.
# This prevents cancelled metadata parents from forcing an unnecessary full UE4 cook/package,
# while still failing closed when runtime/packaging/workflow-affecting files are present.
pg161_classifier = read(ROOT / "Scripts" / "classify_unreal_validation.ps1")
for pg161_symbol in [
    "Test-NearestSafeGovernanceAncestorGreen",
    "Test-SafeGovernanceDelta",
    "TRANSITIVE_GOVERNANCE_PROOF_PASS",
    "governance-docs-only-inherits-nearest-safe-green-ancestor",
    "VALIDATION_POLICY_ONLY_FILE",
    "validation-policy-only-inherits-green-parent-no-engine-repeat",
]:
    if pg161_symbol not in pg161_classifier:
        fail(f"PG-161 validation-cost/evidence-reuse guard missing: {pg161_symbol}")
pg161_loop_start = pg161_classifier.find("foreach($p in $changed)")
pg161_safe_start = pg161_classifier.find('$n.StartsWith("Docs/")', pg161_loop_start)
pg161_policy_start = pg161_classifier.find(
    'if($n -eq "Scripts/classify_unreal_validation.ps1"',
    pg161_safe_start,
)
pg161_safe_block = (
    pg161_classifier[pg161_safe_start:pg161_policy_start]
    if pg161_loop_start >= 0 and pg161_safe_start >= 0 and pg161_policy_start > pg161_safe_start
    else ""
)
if "Scripts/classify_unreal_validation.ps1" in pg161_safe_block:
    fail("PG-161 classifier script must not be silently treated as ordinary governance/docs-only input")

# PG-162: local launch controllers must execute from immutable temporary copies before git pull.
# This prevents CMD from continuing to parse a .bat file that git is rewriting in-place.
pg162_update = read(ROOT / "SHIRE_UPDATE_BUILD_LAUNCH.bat")
pg162_pie = read(ROOT / "SHIRE_PIE_VERIFY.bat")
for pg162_symbol in [
    "SHIRE_UPDATE_BOOTSTRAPPED",
    "ShireJourney_UpdateBuildLaunch_",
    "LOCAL_BOOTSTRAP_COPY_FAILED",
]:
    if pg162_symbol not in pg162_update:
        fail(f"PG-162 update/build launcher immutable-bootstrap guard missing: {pg162_symbol}")
for pg162_symbol in [
    "SHIRE_PIE_BOOTSTRAPPED",
    "ShireJourney_PIEVerify_",
    "PIE_BOOTSTRAP_COPY_FAILED",
]:
    if pg162_symbol not in pg162_pie:
        fail(f"PG-162 PIE launcher immutable-bootstrap guard missing: {pg162_symbol}")

# PG-160: procedural StaticMeshActor spawn paths must set Movable before SetStaticMesh.
for pg160_builder in [
    "ShirePrototypeWorldBuilder.cpp",
    "BreePrototypeWorldBuilder.cpp",
    "FellowshipChapterWorldBuilder.cpp",
    "IsengardPrototypeWorldBuilder.cpp",
]:
    pg160_text = read(ROOT / "Source" / "ShireJourney" / "Private" / "World" / pg160_builder)
    pg160_start = pg160_text.find("::SpawnShape(")
    if pg160_start < 0:
        fail(f"PG-160: SpawnShape missing in {pg160_builder}")
        continue
    pg160_end = pg160_text.find("\nvoid ", pg160_start + 1)
    if pg160_end < 0:
        pg160_end = len(pg160_text)
    pg160_block = pg160_text[pg160_start:pg160_end]
    pg160_mobility = pg160_block.find("SetMobility(EComponentMobility::Movable)")
    pg160_mesh = pg160_block.find("SetStaticMesh(")
    if pg160_mobility < 0 or pg160_mesh < 0 or pg160_mobility > pg160_mesh:
        fail(f"PG-160: {pg160_builder} must set Movable before SetStaticMesh")

game_target = read(ROOT / "Source" / "ShireJourney.Target.cs")
if (
    'Environment.GetEnvironmentVariable("SHIRE_CI_NO_DEBUGINFO") == "1"' not in game_target
    or "WindowsPlatform.bUseBundledDbgHelp = false;" not in game_target
):
    fail("PG-026: CI Game target must disable bundled DbgHelp rather than silently copying it")
if "post-job-runner-dedupe.ps1" in unreal_ci or "delete env.RUNNER_TRACKING_ID" in unreal_ci:
    fail("PG-026: validation must not launch detached runner lifecycle cleanup")
powershell_policy_ok = (
    'shell: powershell -NoProfile -ExecutionPolicy Bypass -Command ". \'{0}\'"' in unreal_ci
    or (
        "powershell.exe -NoProfile -ExecutionPolicy Bypass -File" in unreal_ci
        and "prepare_msvc_environment.ps1" in unreal_ci
        and "reset_project_build_intermediates.ps1" in unreal_ci
        and "resolve_runtime_python.ps1" in unreal_ci
    )
)
if not powershell_policy_ok:
    fail("PG-027: self-hosted PowerShell steps must bypass the target machine script execution policy")

quest_cpp = read(resolve_source("ShireQuestSubsystem.cpp"))
definitions = set(re.findall(r'AddQuestDefinition\s*\(\s*TEXT\("([^"]+)"\)', quest_cpp))
if not definitions:
    fail("No quest definitions found in ShireQuestSubsystem.cpp")

references: set[str] = set()
for path in sorted(SOURCE.rglob("*.cpp")):
    text = read(path)
    for pattern in [
        r'\bQuestId\s*=\s*TEXT\("([^"]+)"\)',
        r'\bNextQuestId\s*=\s*TEXT\("([^"]+)"\)',
        r'\bNextChapterQuestId\s*=\s*TEXT\("([^"]+)"\)',
        r'StartQuest\s*\(\s*TEXT\("([^"]+)"\)',
        r'StartChapter\s*\(\s*TEXT\("P1C\d+"\)\s*,\s*TEXT\("([^"]+)"\)',
        r'SpawnQuestTrigger\s*\(\s*FVector\([^)]*\)\s*,\s*TEXT\("([^"]+)"\)',
        r'SpawnNPC\s*\(\s*TEXT\("[^"]+"\)\s*,\s*FVector\([^)]*\)\s*,\s*FRotator\([^)]*\)\s*,\s*TEXT\("([^"]+)"\)',
    ]:
        references.update(re.findall(pattern, text, flags=re.S))

undefined = sorted(ref for ref in references if ref not in definitions)
if undefined:
    fail("Quest references without definitions: " + ", ".join(undefined))

router_cpp = read(resolve_source("ChapterWorldRouter.cpp"))

# Guardian regression PG-010: route helper takes (ChapterId, bRestoreRouteTransform).
# Catch the exact stale one-argument forms that escaped earlier static validation.
if re.search(r'MovePlayerToChapterStart\s*\(\s*ChapterId\s*\)\s*;', router_cpp):
    fail("PG-010: MovePlayerToChapterStart called with ChapterId only; pass restore-route flag too")
if re.search(r'MovePlayerToChapterStart\s*\(\s*TEXT\("P1C\d+"\)\s*\)\s*;', router_cpp):
    fail("PG-010: MovePlayerToChapterStart called with literal chapter only; pass restore-route flag too")

expected_chapters = {f"P1C{i:02d}" for i in range(1, 9)}
router_chapters = set(re.findall(r'ChapterId\s*==\s*TEXT\("(P1C\d+)"\)', router_cpp))
missing_chapters = sorted(expected_chapters - router_chapters)
if missing_chapters:
    fail("ChapterWorldRouter is missing runtime chapters: " + ", ".join(missing_chapters))

# Guardian regression PG-011: UE4.27 GetLightComponent returns a base pointer.
# Direct assignment to a derived light component pointer fails real C++ compilation.
shire_world_cpp = read(resolve_source("ShirePrototypeWorldBuilder.cpp"))
if re.search(r'UDirectionalLightComponent\s*\*\s*\w+\s*=\s*\w+->GetLightComponent\s*\(\s*\)\s*;', shire_world_cpp):
    fail("PG-011: direct GetLightComponent assignment to UDirectionalLightComponent*; use Cast<>")
if re.search(r'USkyLightComponent\s*\*\s*\w+\s*=\s*\w+->GetLightComponent\s*\(\s*\)\s*;', shire_world_cpp):
    fail("PG-011: direct GetLightComponent assignment to USkyLightComponent*; use Cast<>")

# Guardian regression PG-012: UE4.27 logs a PIE warning if the Directional Light is
# rotated before the light component is made Movable.
morning_start = shire_world_cpp.find("void AShirePrototypeWorldBuilder::ConfigureMorningAtmosphere()")
morning_end = shire_world_cpp.find("void AShirePrototypeWorldBuilder::SpawnVillage()", morning_start)
if morning_start < 0 or morning_end < 0:
    fail("PG-012: ConfigureMorningAtmosphere/SpawnVillage boundary not found")
else:
    morning_block = shire_world_cpp[morning_start:morning_end]
    mobility_pos = morning_block.find("SunComponent->SetMobility(EComponentMobility::Movable)")
    rotation_pos = morning_block.find("Sun->SetActorRotation(")
    if mobility_pos < 0 or rotation_pos < 0:
        fail("PG-012: morning atmosphere missing sun mobility or rotation step")
    elif rotation_pos < mobility_pos:
        fail("PG-012: Directional Light rotation occurs before mobility is set to Movable")

chapter_refs: set[str] = set()
for path in sorted(SOURCE.rglob("*.cpp")):
    text = read(path)
    chapter_refs.update(re.findall(r'NextChapterId\s*=\s*TEXT\("(P1C\d+)"\)', text))
    chapter_refs.update(re.findall(r'StartChapter\s*\(\s*TEXT\("(P1C\d+)"\)', text))
    chapter_refs.update(re.findall(r'TEXT\("(P1C\d+)"\)\s*,\s*TEXT\("[A-Za-z0-9_]+"\)\s*,\s*\d+\s*\)', text))
unknown_chapters = sorted(ref for ref in chapter_refs if ref not in expected_chapters)
if unknown_chapters:
    fail("Unknown runtime chapter references: " + ", ".join(unknown_chapters))

story_beat_refs: set[str] = set()
for path in sorted(SOURCE.rglob("*.cpp")):
    if path.name == "ShireStoryPresentationSubsystem.cpp":
        continue
    text = read(path)
    story_beat_refs.update(re.findall(r'StoryBeatId\s*=\s*TEXT\("([^"]+)"\)', text))
    story_beat_refs.update(re.findall(
        r'SpawnQuestTrigger\s*\([^;]*?TEXT\("([A-Za-z0-9_]+)"\)\s*(?:,\s*TEXT\("[A-Za-z0-9_]+"\)|,\s*NAME_None)',
        text,
        flags=re.S,
    ))

presentation_cpp = read(resolve_source("ShireStoryPresentationSubsystem.cpp"))
presentation_beats = set(re.findall(r'AddCue\s*\(\s*TEXT\("([^"]+)"\)', presentation_cpp))
missing_presentation = sorted(story_beat_refs - presentation_beats)
if missing_presentation:
    fail("Story beats without presentation cues: " + ", ".join(missing_presentation))

all_cues = re.findall(r'AddCue\s*\(\s*TEXT\("([^"]+)"\)', presentation_cpp)
duplicate_cues = sorted({cue for cue in all_cues if all_cues.count(cue) > 1})
if duplicate_cues:
    fail("Duplicate story presentation cues: " + ", ".join(duplicate_cues))

# Guardian: the authored story plan and runtime presentation layer must describe the same beat set.
planned_story_beats = {value for value in story_plan_ids if value}
missing_from_plan = sorted(presentation_beats - planned_story_beats)
missing_from_runtime = sorted(planned_story_beats - presentation_beats)
if missing_from_plan:
    fail("Runtime presentation cues missing from StoryBeatPlan: " + ", ".join(missing_from_plan))
if missing_from_runtime:
    fail("StoryBeatPlan beats missing from runtime presentation: " + ", ".join(missing_from_runtime))

# Guardian: the original music plan and runtime presentation music refs must stay synchronized.
presentation_music_refs = set(re.findall(
    r'AddCue\s*\(\s*TEXT\("[^"]+"\)\s*,\s*EShireStoryPresentationMode::[A-Za-z]+\s*,\s*'
    r'(?:TEXT\("[^"]+"\)|NAME_None)\s*,\s*'
    r'(?:TEXT\("[^"]+"\)|NAME_None)\s*,\s*'
    r'(?:TEXT\("[^"]+"\)|NAME_None)\s*,\s*TEXT\("([^"]+)"\)',
    presentation_cpp,
    flags=re.S,
))
planned_music_cues = {value for value in music_plan_ids if value}
missing_music_plan = sorted(presentation_music_refs - planned_music_cues)
dead_music_plan = sorted(planned_music_cues - presentation_music_refs)
if missing_music_plan:
    fail("Runtime music cues missing from MusicCuePlan: " + ", ".join(missing_music_plan))
if dead_music_plan:
    fail("MusicCuePlan cues missing from runtime presentation: " + ", ".join(dead_music_plan))

# Every non-empty dialogue cue referenced by a presentation cue must exist in the runtime dialogue library.
dialogue_cpp = read(resolve_source("ShireDialogueSubsystem.cpp"))
dialogue_sequences = set(re.findall(r'AddSequence\s*\(\s*TEXT\("([^"]+)"\)', dialogue_cpp))
presentation_dialogue_refs = set(
    re.findall(
        r'AddCue\s*\(\s*TEXT\("[^"]+"\)\s*,\s*EShireStoryPresentationMode::[A-Za-z]+\s*,\s*'
        r'(?:TEXT\("[^"]+"\)|NAME_None)\s*,\s*TEXT\("([^"]+)"\)',
        presentation_cpp,
        flags=re.S,
    )
)
missing_dialogue = sorted(presentation_dialogue_refs - dialogue_sequences)
if missing_dialogue:
    fail("Presentation dialogue cues without runtime sequences: " + ", ".join(missing_dialogue))

all_dialogue_sequences = re.findall(r'AddSequence\s*\(\s*TEXT\("([^"]+)"\)', dialogue_cpp)
duplicate_dialogue = sorted({cue for cue in all_dialogue_sequences if all_dialogue_sequences.count(cue) > 1})
if duplicate_dialogue:
    fail("Duplicate runtime dialogue sequences: " + ", ".join(duplicate_dialogue))

runtime_voice_cues = set(re.findall(r'TEXT\("(VO_[A-Za-z0-9_]+)"\)', dialogue_cpp))
planned_voice_cues = {value for value in voice_plan_ids if value}
missing_voice_plan = sorted(runtime_voice_cues - planned_voice_cues)
dead_voice_plan = sorted(planned_voice_cues - runtime_voice_cues)
if missing_voice_plan:
    fail("Runtime voice cues missing from VoiceCuePlan: " + ", ".join(missing_voice_plan))
if dead_voice_plan:
    fail("VoiceCuePlan cues missing from runtime dialogue: " + ", ".join(dead_voice_plan))

audio_cpp = read(resolve_source("ShireAudioSubsystem.cpp"))
if "ResolveVoiceAsset" not in audio_cpp or "/Game/Audio/Voice/" not in audio_cpp:
    fail("Runtime voice asset resolver missing from ShireAudioSubsystem")
if "SpawnSoundAttached" not in audio_cpp or "SpawnSound2D" not in audio_cpp:
    fail("Runtime voice playback must support attached spatial world voice and controlled 2D fallback")

player_cpp = read(resolve_source("ShirePlayerCharacter.cpp"))
player_h = read(resolve_source("ShirePlayerCharacter.h"))

# PG-031: production character motion must preserve production-aware transforms.
for symbol in [
    "bUsingProductionCharacter",
    "CharacterVisual:",
    "HatBaseZ = bUsingProductionCharacter ? 91.0f : 101.0f",
    "BeardX = bUsingProductionCharacter ? 14.0f : 10.0f",
    "FaceX = bUsingProductionCharacter ? 17.0f : 10.5f",
    "bSprintRequested",
    "bIsCrouched",
    "Movement->IsFalling()",
]:
    if symbol not in player_cpp and symbol not in player_h:
        fail(f"PG-031 production character motion invariant missing: {symbol}")

if "/Game/Production/Characters/Frodo/" not in player_cpp:
    fail("PG-031 player character lost Frodo production asset path")
if "/Game/Production/Characters/Gandalf/" not in player_cpp:
    fail("PG-031 player character lost Gandalf production asset path")

enemy_cpp = read(resolve_source("FellowshipEnemyPrototype.cpp"))
save_h = read(resolve_source("ShireSaveGame.h"))
for symbol in ["PrimaryAttack", "TakeDamage", "GetCurrentHealth", "IsCombatAvailable"]:
    if symbol not in player_cpp and symbol not in player_h:
        fail(f"Combat foundation missing player symbol: {symbol}")
if "PlayerHealth" not in save_h:
    fail("Combat foundation health is not persisted in ShireSaveGame")
for profile in ["EFellowshipEnemyType::Orc", "EFellowshipEnemyType::UrukHai", "EFellowshipEnemyType::CaveTroll"]:
    if profile not in enemy_cpp:
        fail(f"Combat foundation missing enemy profile: {profile}")
if "AFellowshipEnemyPrototype::StaticClass()" not in router_cpp:
    fail("ChapterWorldRouter does not clear combat enemies between runtime regions")

for category in ["/Game/Audio/Ambience/", "/Game/Audio/Music/", "/Game/Audio/SFX/"]:
    if category not in audio_cpp:
        fail(f"Runtime audio category resolver missing: {category}")
if "ApplyMusicDuck" not in audio_cpp:
    fail("Runtime audio mix missing dialogue music ducking")
npc_cpp = read(resolve_source("ShireNPC.cpp"))
for acting_symbol in ["PrototypeLeftEye", "PrototypeRightEye", "PrototypeMouth", "UpdatePrototypeActing"]:
    if acting_symbol not in npc_cpp:
        fail(f"Proxy acting foundation missing: {acting_symbol}")

# Quest/chapter reachability safety net. We model explicit transitions and runtime handoff guards.
chapter_start_quests = {
    "P1C01": "ShireArrival",
    "P1C02": "RoadToBree",
    "P1C03": "RoadToWeathertop",
    "P1C04": "RivendellRecovery",
    "P1C05": "SouthwardJourney",
    "P1C06": "MoriaDark",
    "P1C07": "LothlorienRest",
    "P1C08": "AnduinJourney",
}
for chapter, quest in chapter_start_quests.items():
    if quest not in definitions:
        fail(f"Chapter {chapter} starts with undefined quest: {quest}")

transition_graph: dict[str, set[str]] = defaultdict(set)
for path in sorted(SOURCE.rglob("*.cpp")):
    text = read(path)

    for match in re.finditer(
        r'(?:QuestId\s*=|->QuestId\s*=)\s*TEXT\("([^"]+)"\)(.*?)(?=(?:QuestId\s*=|->QuestId\s*=|\n\s*}\n|\Z))',
        text,
        flags=re.S,
    ):
        source_quest = match.group(1)
        block = match.group(2)
        for target in re.findall(r'NextQuestId\s*=\s*TEXT\("([^"]+)"\)', block):
            transition_graph[source_quest].add(target)
        for target in re.findall(r'NextChapterQuestId\s*=\s*TEXT\("([^"]+)"\)', block):
            transition_graph[source_quest].add(target)

    for match in re.finditer(
        r'SpawnQuestTrigger\s*\(\s*FVector\([^)]*\)\s*,\s*TEXT\("([^"]+)"\)\s*,.*?'
        r'(?:TEXT\("([A-Za-z0-9_]+)"\)\s*,\s*\d+\s*,\s*TEXT\("(P1C\d+)"\)\s*,\s*TEXT\("([A-Za-z0-9_]+)"\)|'
        r'TEXT\("([A-Za-z0-9_]+)"\)\s*,\s*\d+\s*\))',
        text,
        flags=re.S,
    ):
        source_quest = match.group(1)
        next_quest = match.group(2) or match.group(5)
        next_chapter_quest = match.group(4)
        if next_quest and next_quest in definitions and next_quest != source_quest:
            transition_graph[source_quest].add(next_quest)
        if next_chapter_quest:
            transition_graph[source_quest].add(next_chapter_quest)

    # Assignment-style builder wiring is the dominant form in the Shire/Bree/Isengard
    # builders. Capture transitions by the same actor variable so static reachability
    # does not under-report authored quest paths.
    for assign in re.finditer(
        r'([A-Za-z_][A-Za-z0-9_]*)->QuestId\s*=\s*TEXT\("([^"]+)"\)',
        text,
    ):
        variable = assign.group(1)
        source_quest = assign.group(2)
        tail = text[assign.end():]
        close = re.search(r'\n\s*}\s*(?:\n|$)', tail)
        block = tail[: close.start()] if close else tail[:1800]
        next_match = re.search(
            rf'{re.escape(variable)}->NextQuestId\s*=\s*TEXT\("([^"]+)"\)',
            block,
        )
        if next_match:
            target = next_match.group(1)
            if target in definitions and target != source_quest:
                transition_graph[source_quest].add(target)
        chapter_match = re.search(
            rf'{re.escape(variable)}->NextChapterQuestId\s*=\s*TEXT\("([^"]+)"\)',
            block,
        )
        if chapter_match:
            target = chapter_match.group(1)
            if target in definitions:
                transition_graph[source_quest].add(target)

    # Direct helper calls also carry quest handoffs (for example Strider leading into
    # the Weathertop attack). Model those positional contracts as graph edges.
    for direct_spawn_npc in re.finditer(
        r'SpawnNPC\s*\(\s*TEXT\("[^"]+"\)\s*,\s*FVector\([^)]*\)\s*,\s*FRotator\([^)]*\)\s*,'
        r'\s*TEXT\("([^"]+)"\)\s*,\s*-?\d+\s*,\s*-?\d+\s*,\s*TEXT\(".*?"\)\s*,'
        r'\s*TEXT\("([^"]+)"\)',
        text,
        flags=re.S,
    ):
        source_quest, target_quest = direct_spawn_npc.groups()
        if source_quest in definitions and target_quest in definitions and source_quest != target_quest:
            transition_graph[source_quest].add(target_quest)

# Critical runtime handoff guard must explicitly bridge the Shire terminal quest to Bree.
story_flow_cpp = read(resolve_source("ShireStoryFlowSubsystem.cpp"))
if 'QuestId == TEXT("FerryEscape")' not in story_flow_cpp:
    fail("Story-flow guard does not monitor FerryEscape terminal state")
if 'StartChapter(TEXT("P1C02"), TEXT("RoadToBree"), 0)' not in story_flow_cpp:
    fail("Story-flow guard does not hand off Shire terminal state to P1C02 / RoadToBree")
transition_graph["FerryEscape"].add("RoadToBree")

reachable: set[str] = set()
# Every chapter start is an authoritative runtime entry point through the world router/debug
# chapter navigation, so traverse the static graph from all of them rather than marking later
# starts reachable only after the BFS has already ended.
queue = deque(list(chapter_start_quests.values()) + ["IsengardCounsel"])
while queue:
    quest = queue.popleft()
    if quest in reachable:
        continue
    reachable.add(quest)
    for next_quest in transition_graph.get(quest, set()):
        if next_quest not in reachable:
            queue.append(next_quest)

important_unreachable = sorted(q for q in definitions if q not in reachable)
if important_unreachable:
    warn("Quest definitions not proven reachable by static graph: " + ", ".join(important_unreachable))

for dirname in ["Binaries", "DerivedDataCache", "Intermediate", "Saved", ".vs"]:
    if (ROOT / dirname).exists():
        fail(f"Generated directory should not be committed: {dirname}")

engine_ini = read(ROOT / "Config" / "DefaultEngine.ini")
if "ShireGameMode" not in engine_ini:
    fail("DefaultEngine.ini does not reference ShireGameMode")
if "r.DefaultFeature.MotionBlur=False" not in engine_ini:
    warn("Motion blur low-spec default is not explicitly disabled")

input_ini = read(ROOT / "Config" / "DefaultInput.ini")
player_cpp = read(resolve_source("ShirePlayerCharacter.cpp"))
required_actions = guard_rules.get(
    "required_debug_actions",
    ["QuickSave", "QuickLoad", "DebugNextChapter", "DebugPreviousChapter"]
)
required_actions = list(required_actions) + ["PrimaryAttack"]
for action in required_actions:
    if f'ActionName="{action}"' not in input_ini:
        fail(f"DefaultInput.ini missing action mapping: {action}")
    if f'BindAction(TEXT("{action}")' not in player_cpp:
        fail(f"ShirePlayerCharacter.cpp missing action binding: {action}")

# Cinematic safety: lock and automatic release are both mandatory.
if "OnCinematicStateChanged.Broadcast(true)" not in presentation_cpp:
    fail("Story presentation subsystem never broadcasts cinematic lock")
if "ReleaseCinematicLock" not in presentation_cpp or "OnCinematicStateChanged.Broadcast(false)" not in presentation_cpp:
    fail("Story presentation subsystem lacks a cinematic unlock path")
if "CinematicReleaseTimer" not in presentation_cpp:
    fail("Story presentation subsystem lacks automatic cinematic lock release")

# Audio runtime wiring: story ambience/music/SFX and queued voice cues must converge on one subsystem.
audio_h = read(resolve_source("ShireAudioSubsystem.h"))
audio_cpp = read(resolve_source("ShireAudioSubsystem.cpp"))
for required_symbol in ["OnAmbienceChanged", "OnMusicChanged", "OnSfxRequested", "OnVoiceRequested"]:
    if required_symbol not in audio_h:
        fail(f"Audio subsystem missing event: {required_symbol}")
for binding in [
    "OnAmbienceCueRequested.AddDynamic",
    "OnMusicCueRequested.AddDynamic",
    "OnSfxCueRequested.AddDynamic",
    "OnVoiceCueRequested.AddDynamic",
]:
    if binding not in audio_cpp:
        fail(f"Audio subsystem missing runtime binding: {binding}")
for unbinding in [
    "OnAmbienceCueRequested.RemoveDynamic",
    "OnMusicCueRequested.RemoveDynamic",
    "OnSfxCueRequested.RemoveDynamic",
    "OnVoiceCueRequested.RemoveDynamic",
]:
    if unbinding not in audio_cpp:
        fail(f"Audio subsystem missing cleanup binding: {unbinding}")

# Guardian: key multi-route persistence symbols must remain present after refactors.
save_h = read(resolve_source("ShireSaveGame.h"))
route_h = read(resolve_source("ShireRouteState.h"))
for symbol in ["CurrentRouteId", "CurrentEpisodeId", "PlayableCharacterId", "RouteProgress", "StartExperience"]:
    if symbol not in quest_cpp and symbol != "RouteProgress":
        fail(f"Quest subsystem missing route-state symbol: {symbol}")
for symbol in ["CurrentRouteId", "CurrentEpisodeId", "PlayableCharacterId", "RouteProgress"]:
    if symbol not in save_h:
        fail(f"Save game missing route persistence symbol: {symbol}")
for symbol in ["FShireRouteProgress", "PlayerLocation", "PlayerRotation", "CompletedStoryBeats"]:
    if symbol not in route_h:
        fail(f"Route state definition missing symbol: {symbol}")
if "GandalfParallel" not in router_cpp or "AIsengardPrototypeWorldBuilder" not in router_cpp:
    fail("ChapterWorldRouter lost the Gandalf/Isengard parallel-route branch")

print(
    f"Validated {len(list(SOURCE.rglob('*.cpp')))} cpp files, "
    f"{len(list(SOURCE.rglob('*.h')))} headers, {len(architecture_entries)} architecture entries, "
    f"{len(definitions)} quest definitions, {len(expected_chapters)} runtime chapters, "
    f"{len(presentation_beats)} presentation cues, {len(dialogue_sequences)} dialogue sequences."
)
for message in warnings:
    print(f"WARNING: {message}")
for message in errors:
    print(f"ERROR: {message}")

# PG-056: the post-CP54 verification freeze is an executable gate, not documentation only.
verification_gate_path = ROOT / "Data" / "VerificationGate.json"
verification_gate = {}
if not verification_gate_path.exists():
    fail("PG-056 verification gate missing: Data/VerificationGate.json")
else:
    try:
        verification_gate = json.loads(read(verification_gate_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-056 invalid VerificationGate.json: {exc}")

if str(governor_data.get("development_mode", {}).get("id") or "") == "PIE_VERIFICATION_FREEZE" and verification_gate:
    if verification_gate.get("mode") != "PIE_VERIFICATION_FREEZE":
        fail("PG-056 verification gate mode must match PIE_VERIFICATION_FREEZE")

    baseline = verification_gate.get("baseline", {})
    max_checkpoint = int(baseline.get("max_checkpoint_number", 54))

    checkpoints_text = read(ROOT / "Docs" / "CHECKPOINTS.md")
    checkpoint_numbers = [
        int(match.group(1))
        for match in re.finditer(r"^##+\s+CP(\d+)\b", checkpoints_text, flags=re.M)
    ]
    too_new_headings = sorted(number for number in checkpoint_numbers if number > max_checkpoint)
    if too_new_headings:
        fail(
            "PG-056 verification freeze blocks new checkpoint headings above "
            f"CP{max_checkpoint}: {too_new_headings}"
        )

    def collect_governor_checkpoint_numbers(value):
        found = []
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "checkpoint" and isinstance(child, str):
                    match = re.fullmatch(r"CP(\d+)", child.strip())
                    if match:
                        found.append(int(match.group(1)))
                found.extend(collect_governor_checkpoint_numbers(child))
        elif isinstance(value, list):
            for child in value:
                found.extend(collect_governor_checkpoint_numbers(child))
        return found

    too_new_governor = sorted(
        number
        for number in collect_governor_checkpoint_numbers(governor_data)
        if number > max_checkpoint
    )
    if too_new_governor:
        fail(
            "PG-056 verification freeze blocks Governor checkpoints above "
            f"CP{max_checkpoint}: {too_new_governor}"
        )

    production_root = ROOT / "SourceAssets" / "Production"
    production_files = [path for path in production_root.rglob("*") if path.is_file()]
    ceiling = baseline.get("production_source_ceiling", {})
    total_ceiling = int(ceiling.get("total_files", 0))
    if total_ceiling and len(production_files) > total_ceiling:
        fail(
            "PG-056 verification freeze blocks net-new production source files: "
            f"{len(production_files)} > {total_ceiling}"
        )

    actual_extension_counts = defaultdict(int)
    for path in production_files:
        actual_extension_counts[path.suffix.lower().lstrip(".")] += 1
    for extension, limit in ceiling.get("extensions", {}).items():
        actual = actual_extension_counts.get(str(extension).lower(), 0)
        if actual > int(limit):
            fail(
                "PG-056 verification freeze blocks production-source expansion for "
                f".{extension}: {actual} > {limit}"
            )

    baseline_runtime_paths = set(baseline.get("runtime_source_paths", []))
    actual_runtime_paths = {
        path.relative_to(ROOT).as_posix()
        for path in SOURCE.rglob("*")
        if path.is_file() and path.suffix.lower() in {".h", ".cpp", ".cs"}
    }
    unexpected_runtime_paths = sorted(actual_runtime_paths - baseline_runtime_paths)
    missing_runtime_paths = sorted(baseline_runtime_paths - actual_runtime_paths)
    if unexpected_runtime_paths:
        fail(
            "PG-056 verification freeze blocks net-new runtime source files: "
            + ", ".join(unexpected_runtime_paths)
        )
    if missing_runtime_paths:
        fail(
            "PG-056 verification freeze blocks source-layout/removal changes during the audit: "
            + ", ".join(missing_runtime_paths)
        )

# PG-057: current-head Real PIE claims require exact-commit and chapter-specific evidence.
pie_evidence_path = ROOT / "Data" / "PIEVerificationEvidence.json"
pie_evidence = {}
if not pie_evidence_path.exists():
    fail("PG-057 PIE evidence file missing: Data/PIEVerificationEvidence.json")
else:
    try:
        pie_evidence = json.loads(read(pie_evidence_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-057 invalid PIEVerificationEvidence.json: {exc}")

if pie_evidence:
    expected_chapters = ["P1C01","P1C02","P1C03","P1C04","P1C05","P1C06","P1C07","P1C08"]
    evidence_rows = pie_evidence.get("chapters", [])
    evidence_by_chapter = {
        str(row.get("chapter_id") or ""): row
        for row in evidence_rows
        if isinstance(row, dict)
    }
    if list(evidence_by_chapter.keys()) != expected_chapters:
        fail("PG-057 PIE evidence chapters must exist once each in P1C01-P1C08 order")

    matrix_text = read(ROOT / "Docs" / "PRODUCTION_COMPLETENESS_MATRIX.md")
    current_head_section = matrix_text.split(
        "This file prevents major game pillars from depending on chat memory.", 1
    )[0]
    matrix_pie_state = {}
    for line in current_head_section.splitlines():
        if not line.startswith("| P1C"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 2:
            chapter_match = re.match(r"(P1C0[1-8])\b", cells[0])
            if chapter_match:
                matrix_pie_state[chapter_match.group(1)] = cells[1]

    allowed_evidence_statuses = {
        "NOT_RUN",
        "BLOCKED",
        "PIE_TESTED_WITH_ISSUES",
        "PIE_TESTED",
    }
    used_specific_notes = {}
    used_observation_sets = {}

    for chapter_id in expected_chapters:
        row = evidence_by_chapter.get(chapter_id)
        if not row:
            fail(f"PG-057 PIE evidence missing chapter: {chapter_id}")
            continue

        status = str(row.get("status") or "")
        if status not in allowed_evidence_statuses:
            fail(f"PG-057 unsupported PIE evidence status for {chapter_id}: {status}")
            continue

        matrix_state = matrix_pie_state.get(chapter_id)
        if not matrix_state:
            fail(f"PG-057 current-head matrix row missing for {chapter_id}")
            continue

        if status == "NOT_RUN":
            if matrix_state != "NOT_RUN":
                fail(
                    f"PG-057 matrix claims PIE activity for {chapter_id} "
                    "without matching chapter-specific evidence"
                )
            continue

        if status == "BLOCKED":
            blockers = row.get("blockers", [])
            if not isinstance(blockers, list) or not blockers:
                fail(f"PG-057 BLOCKED status for {chapter_id} requires a concrete blocker")
            continue

        tested_commit = str(row.get("tested_commit") or "")
        tested_at = str(row.get("tested_at") or "")
        tester = str(row.get("tester") or "")
        observations = row.get("observed_details", [])
        specific = row.get("specific_evidence", {})
        if not isinstance(specific, dict):
            specific = {}

        if not re.fullmatch(r"[0-9a-fA-F]{40}", tested_commit):
            fail(f"PG-057 {chapter_id} PIE evidence requires an exact 40-char commit SHA")
        if not tested_at:
            fail(f"PG-057 {chapter_id} PIE evidence requires tested_at")
        if not tester:
            fail(f"PG-057 {chapter_id} PIE evidence requires tester")
        if not isinstance(observations, list) or len(observations) < 2:
            fail(f"PG-057 {chapter_id} PIE evidence requires at least two concrete observations")

        fps_value = specific.get("fps_value")
        has_fps = (
            isinstance(fps_value, (int, float))
            and not isinstance(fps_value, bool)
            and fps_value > 0
        )
        screenshots = specific.get("screenshot_artifacts", [])
        videos = specific.get("video_artifacts", [])
        has_visual = (
            isinstance(screenshots, list) and any(str(item).strip() for item in screenshots)
        ) or (
            isinstance(videos, list) and any(str(item).strip() for item in videos)
        )
        specific_note = " ".join(str(specific.get("chapter_specific_note") or "").split())
        has_specific_note = len(specific_note) >= 20

        if not (has_fps or has_visual or has_specific_note):
            fail(
                f"PG-057 {chapter_id} cannot be PIE-tested from generic sign-off: "
                "record numeric FPS, screenshot/video evidence, or a concrete chapter-specific note"
            )

        if has_specific_note:
            note_key = specific_note.casefold()
            previous = used_specific_notes.get(note_key)
            if previous and previous != chapter_id:
                fail(
                    f"PG-057 copied chapter-specific note reused by {previous} and {chapter_id}"
                )
            used_specific_notes[note_key] = chapter_id

        observation_key = tuple(
            " ".join(str(item).split()).casefold()
            for item in observations
            if str(item).strip()
        )
        if observation_key:
            previous = used_observation_sets.get(observation_key)
            if previous and previous != chapter_id:
                fail(
                    f"PG-057 copied observation set reused by {previous} and {chapter_id}"
                )
            used_observation_sets[observation_key] = chapter_id

        if matrix_state == "NOT_RUN":
            fail(
                f"PG-057 {chapter_id} has chapter-specific PIE evidence but the current-head matrix "
                "was not updated"
            )

    signoff = pie_evidence.get("human_release_signoff", {})
    if signoff.get("status") == "APPROVED":
        incomplete = [
            chapter_id
            for chapter_id in expected_chapters
            if evidence_by_chapter.get(chapter_id, {}).get("status") != "PIE_TESTED"
        ]
        if incomplete:
            fail(
                "PG-057 human release sign-off cannot be APPROVED while chapters remain "
                "unverified/blocked/issues: " + ", ".join(incomplete)
            )
        if not signoff.get("signed_by") or not signoff.get("signed_at"):
            fail("PG-057 APPROVED human release sign-off requires signer and timestamp")

# PG-112: long Windows validation must execute from repository-stable scripts.
pg112_workflow = read(ROOT / ".github" / "workflows" / "unreal-build-validation.yml")
pg112_scripts = [
    "ci_verify_unreal.cmd", "ci_wait_for_unreal_editor.cmd", "ci_build_unreal.cmd",
    "ci_import_production_assets.cmd", "ci_runtime_startup.cmd", "ci_runtime_chapters.cmd",
    "ci_runtime_state.cmd", "ci_warning_debt.cmd", "ci_collect_unreal_logs.cmd",
    "ci_report_failure.cmd",
]
for pg112_script in pg112_scripts:
    pg112_path = ROOT / "Scripts" / pg112_script
    if not pg112_path.exists():
        fail(f"PG-112 stable Windows validation script missing: {pg112_script}")
    if pg112_script not in pg112_workflow:
        fail(f"PG-112 workflow does not invoke stable Windows validation script: {pg112_script}")

# PG-109: V6 hero geometry is a structural production step, not a final-visual claim.
pg109_specs = {
    "Frodo": (328, 640, 254, 504, 421, 740),
    "Gandalf": (328, 640, 254, 504, 477, 836),
    "Sam": (328, 640, 254, 504, 393, 692),
    "Merry": (328, 640, 254, 504, 379, 668),
    "Pippin": (328, 640, 254, 504, 407, 716),
    "Aragorn": (328, 640, 254, 504, 449, 788),
    "Boromir": (328, 640, 254, 504, 379, 668),
    "Legolas": (328, 640, 254, 504, 477, 836),
    "Gimli": (328, 640, 254, 504, 421, 740),
}
for pg109_name, pg109_limits in pg109_specs.items():
    pg109_root = ROOT / "SourceAssets" / "Production" / "Characters" / pg109_name
    pg109_head = read(pg109_root / f"SM_{pg109_name}_Head.obj")
    pg109_torso = read(pg109_root / f"SM_{pg109_name}_Torso.obj")
    pg109_hair = read(pg109_root / f"SM_{pg109_name}_Hair.obj")
    if "Hero head wave V6" not in pg109_head:
        fail(f"PG-109 V6 head marker missing: {pg109_name}")
    if "Hero torso wave V6" not in pg109_torso:
        fail(f"PG-109 V6 torso marker missing: {pg109_name}")
    if "Hero hair wave V6" not in pg109_hair:
        fail(f"PG-109 V6 hair marker missing: {pg109_name}")
    pg109_counts = (
        sum(1 for line in pg109_head.splitlines() if line.startswith("v ")),
        sum(1 for line in pg109_head.splitlines() if line.startswith("f ")),
        sum(1 for line in pg109_torso.splitlines() if line.startswith("v ")),
        sum(1 for line in pg109_torso.splitlines() if line.startswith("f ")),
        sum(1 for line in pg109_hair.splitlines() if line.startswith("v ")),
        sum(1 for line in pg109_hair.splitlines() if line.startswith("f ")),
    )
    if any(actual < required for actual, required in zip(pg109_counts, pg109_limits)):
        fail(f"PG-109 hero geometry structural regression: {pg109_name} counts={pg109_counts} limits={pg109_limits}")

pg109_matrix = json.loads(read(ROOT / "Data" / "CharacterProductionMatrix.json"))
if pg109_matrix.get("geometry_refinement_wave", {}).get("status") != "ENGINE_PROVEN_PENDING_RENDERED_ACCEPTANCE":
    fail("PG-109 hero geometry must remain engine-proven while rendered acceptance is pending")
pg109_npc = read(resolve_source("ShireNPC.cpp"))
pg109_npch = read(resolve_source("ShireNPC.h"))
for pg109_symbol in [
    "bUsingProductionVisual",
    "SM_ProductionShield",
    "SM_ProductionBow",
    "SM_ProductionAxe",
    "SM_Gandalf_Staff",
]:
    if pg109_symbol not in (pg109_npc + pg109_npch):
        fail(f"PG-109 named-cast production visual integration missing: {pg109_symbol}")

# PG-110: core Fellowship characters use a project production surface, not flat-only tints.
pg110_importer = read(ROOT / "Source" / "ShireJourneyEditorTools" / "Private" / "ShireProductionImportCommandlet.cpp")
for pg110_symbol in [
    "M_ProductionSurface",
    "UMaterialExpressionVectorParameter",
    "UMaterialExpressionScalarParameter",
    "RoughnessParameter",
    "MetallicParameter",
    "SetParentEditorOnly",
    'TEXT("Pr ")',
    'TEXT("Pm ")',
]:
    if pg110_symbol not in pg110_importer:
        fail(f"PG-110 production surface master/import support missing: {pg110_symbol}")

pg110_npc = read(resolve_source("ShireNPC.cpp"))
for pg110_symbol in [
    "ProductionSurfaceMaterial",
    "ApplySurface",
    'SetScalarParameterValue(TEXT("Roughness")',
    'SetScalarParameterValue(TEXT("Metallic")',
    "0.82f, 0.0f",
    "0.54f, 0.0f",
    "0.34f, 0.78f",
]:
    if pg110_symbol not in pg110_npc:
        fail(f"PG-110 named-character surface response missing: {pg110_symbol}")

pg110_matrix = json.loads(read(ROOT / "Data" / "CharacterProductionMatrix.json"))
if pg110_matrix.get("geometry_refinement_wave", {}).get("status") != "ENGINE_PROVEN_PENDING_RENDERED_ACCEPTANCE":
    fail("PG-110 V6 geometry should remain engine-proven but not visually accepted")
if pg110_matrix.get("surface_material_wave", {}).get("status") != "ENGINE_PROVEN_PENDING_RENDERED_ACCEPTANCE":
    fail("PG-110 V7 surface wave must remain engine-proven while rendered acceptance is pending")

# PG-111: V10 regional life must stay canon-safe, route-readable and performance-bounded.
pg111_plan = json.loads(read(ROOT / "Data" / "WorldLifeSaturationPlan.json"))
pg111_targets = pg111_plan.get("baseline_population_targets", {})
pg111_roles = pg111_plan.get("population_roles", {})
if pg111_plan.get("plan_id") != "PART1_WORLD_ALIVE_SATURATION_V10":
    fail("PG-111 V10 world-life plan identity changed")
if pg111_plan.get("status") != "W01_P1C01_SINGLE_OWNER_BUDGET_AUTHORITY_IMPLEMENTED_PENDING_ENGINE_PROOF":
    fail("PG-111 W01 world-life proof boundary changed")
if pg111_plan.get("micro_event_budget_authority") != "Data/LivingWorldEventPlan.json#region_budgets":
    fail("PG-111 micro-event budget authority must remain LivingWorldEventPlan#region_budgets")
pg111_density = pg111_plan.get("density_profile", {})
for pg111_stale_field in [
    "max_active_micro_events_near_player",
    "min_seconds_between_event_starts",
]:
    if pg111_stale_field in pg111_density:
        fail(f"PG-111 WorldLifeSaturationPlan must not override micro-event authority: {pg111_stale_field}")
if int(pg111_targets.get("P1C05", -1)) != 0:
    fail("PG-111 Caradhras ambient civilian baseline must remain zero")
if int(pg111_targets.get("P1C06", -1)) != 0:
    fail("PG-111 Moria ambient civilian baseline must remain zero")
pg111_anduin_roles = set(pg111_roles.get("P1C08", []))
if pg111_anduin_roles != {"Bird"}:
    fail("PG-111 Anduin/Amon Hen baseline must remain bird-only under the proven fauna contract")
if "RoadWalker" in pg111_anduin_roles or "Villager" in pg111_anduin_roles:
    fail("PG-111 invented civilian walkers may not populate Anduin/Amon Hen")

pg111_profiles = pg111_plan.get("chapter_density_profiles", {})
for pg111_chapter in [f"P1C{i:02d}" for i in range(1, 9)]:
    pg111_profile = pg111_profiles.get(pg111_chapter, {})
    if not isinstance(pg111_profile, dict) or not pg111_profile:
        fail(f"PG-111 V10 chapter density profile missing: {pg111_chapter}")
        continue
    for pg111_field in [
        "spawn_interval_seconds",
        "baseline_inner_radius_cm",
        "baseline_outer_radius_cm",
        "baseline_cull_radius_cm",
        "danger_population_fraction",
    ]:
        if pg111_field not in pg111_profile:
            fail(f"PG-111 V10 density profile {pg111_chapter} missing {pg111_field}")
    pg111_fraction = float(pg111_profile.get("danger_population_fraction", 0.0))
    if not (0.10 <= pg111_fraction <= 1.0):
        fail(f"PG-111 V10 danger population fraction out of bounds for {pg111_chapter}: {pg111_fraction}")

pg111_event_plan = json.loads(read(ROOT / "Data" / "LivingWorldEventPlan.json"))
pg111_caradhras = next(
    (row for row in pg111_event_plan.get("chapter_contracts", [])
     if isinstance(row, dict) and row.get("chapter") == "P1C05"),
    {},
)
pg111_caradhras_allowed = set(pg111_caradhras.get("allowed", []))
if "SOCIAL_MOMENT" in pg111_caradhras_allowed or "FAUNA" in pg111_caradhras_allowed:
    fail("PG-111 Caradhras ambient contract may not spawn residents or fauna")

pg111_director = read(resolve_source("LivingWorldDirector.cpp"))
pg111_shire_builder = read(resolve_source("ShirePrototypeWorldBuilder.cpp"))
if "SpawnActor<AShireAmbientNPC>" in pg111_shire_builder:
    fail("PG-111 ShirePrototypeWorldBuilder must not own ambient crowd spawning after W01 convergence")
if "AcquireAmbientNPC" not in pg111_director or "ReleaseAmbientNPCToPool" not in pg111_director:
    fail("PG-111 LivingWorldDirector ambient pooling ownership missing")
for pg111_symbol in [
    "Random.FRand() < 0.72f",
    "GetActorForwardVector().GetSafeNormal2D()",
    "PopulationProfilesByChapter",
    "DangerPopulationFraction",
    "ApplyPopulationProfile",
    "FMath::RoundToInt(Target * DangerPopulationFraction)",
    'RoleName == TEXT("Bird")',
    'RoleName == TEXT("Rabbit")',
    'RoleName == TEXT("Butterfly")',
]:
    if pg111_symbol not in pg111_director:
        fail(f"PG-111 regional-life director behavior missing: {pg111_symbol}")

pg111_ambient = read(resolve_source("ShireAmbientNPC.cpp"))
pg111_ambient_h = read(resolve_source("ShireAmbientNPC.h"))
for pg111_symbol in [
    "ProductionSurfaceMaterial",
    "AnimationRateScale",
    "IdleLookAmplitude",
    "IdleLookPhase",
    "IdleYaw",
]:
    if pg111_symbol not in (pg111_ambient + pg111_ambient_h):
        fail(f"PG-111 ambient presentation behavior missing: {pg111_symbol}")

# PG-113: environmental-life motion keeps sparse chapters alive without inventing civilians.
pg113_motion_h = read(resolve_source("WorldAmbientMotionActor.h"))
pg113_motion_cpp = read(resolve_source("WorldAmbientMotionActor.cpp"))
for pg113_symbol in [
    "EWorldAmbientMotionMode",
    "ConfigureGlow",
    "SetCastShadows(false)",
    "PrimaryActorTick.TickInterval = 0.05f",
]:
    if pg113_symbol not in (pg113_motion_h + pg113_motion_cpp):
        fail(f"PG-113 ambient motion runtime missing: {pg113_symbol}")

for pg113_symbol in [
    "SpawnAmbientMotionActor",
    'EventType == TEXT("PROP_MOTION")',
    "SM_MoriaDebrisCluster",
    "SM_MoriaChainAnchor",
    "SM_LorienLeafLantern",
    "SM_RivendellLantern",
    "ConfigureGlow",
]:
    if pg113_symbol not in pg111_director:
        fail(f"PG-113 environmental-life director wiring missing: {pg113_symbol}")

pg113_event_plan = json.loads(read(ROOT / "Data" / "LivingWorldEventPlan.json"))
if pg113_event_plan.get("status") != "V9_ENVIRONMENTAL_LIFE_RUNTIME_IMPLEMENTED_PENDING_ENGINE_PROOF":
    fail("PG-113 living-world event proof boundary changed")
pg113_moria = next(
    (row for row in pg113_event_plan.get("chapter_contracts", [])
     if isinstance(row, dict) and row.get("chapter") == "P1C06"),
    {},
)
pg113_moria_allowed = set(pg113_moria.get("allowed", []))
if "PROP_MOTION" not in pg113_moria_allowed or "STORY_AFTERMATH" not in pg113_moria_allowed:
    fail("PG-113 Moria must retain environmental motion/aftermath without civilian life")
if int(pg111_targets.get("P1C06", -1)) != 0:
    fail("PG-113 Moria environmental-life wave may not introduce ambient civilians")

# PG-129: persistence restore must be atomic and replay-safe across already-resident banks.
pg129_quest_h = read(resolve_source("ShireQuestSubsystem.h"))
pg129_quest = read(resolve_source("ShireQuestSubsystem.cpp"))
pg129_player = read(resolve_source("ShirePlayerCharacter.cpp"))
pg129_router = read(resolve_source("ChapterWorldRouter.cpp"))
pg129_stream = read(resolve_source("ShireChapterAssetStreamingSubsystem.cpp"))
pg129_audio = read(resolve_source("ShireAudioSubsystem.cpp"))

for pg129_symbol in [
    "BeginPersistenceRestore",
    "CommitPersistenceRestore",
    "AbortPersistenceRestore",
    "bPersistenceRestoreInProgress",
]:
    if pg129_symbol not in (pg129_quest_h + pg129_quest):
        fail(f"PG-129 atomic persistence transaction missing: {pg129_symbol}")

restore_start = pg129_player.find("bool AShirePlayerCharacter::RestoreSaveSnapshot")
restore_end = pg129_player.find("bool AShirePlayerCharacter::SaveAutomaticCheckpoint", restore_start)
restore_body = pg129_player[restore_start:restore_end] if restore_start >= 0 and restore_end >= 0 else ""
begin_index = restore_body.find("BeginPersistenceRestore")
memory_index = restore_body.find("RestoreNPCMemoryState")
knowledge_index = restore_body.find("RestoreKnowledgeState")
commit_index = restore_body.find("CommitPersistenceRestore")
if min(begin_index, memory_index, knowledge_index, commit_index) < 0 or not (begin_index < memory_index < knowledge_index < commit_index):
    fail("PG-129 save restore must publish only after all logical persistence domains are rebuilt")
if "transform-skipped reason=identity-repaired" not in restore_body:
    fail("PG-129 repaired save identity must not apply an old-world transform")

rollback_start = pg129_router.find("bool AChapterWorldRouter::RestoreCommittedWorldFromSnapshot")
rollback_end = pg129_router.find("void AChapterWorldRouter::RollbackFailedWorldSwap", rollback_start)
rollback_body = pg129_router[rollback_start:rollback_end] if rollback_start >= 0 and rollback_end >= 0 else ""
for pg129_symbol in [
    "BeginPersistenceRestore",
    "AbortPersistenceRestore",
    "CommitPersistenceRestore(false)",
]:
    if pg129_symbol not in rollback_body:
        fail(f"PG-129 rollback persistence transaction missing: {pg129_symbol}")
if "LastLoadedChapterId = NAME_None;" not in rollback_body:
    fail("PG-129 failed rollback must invalidate committed-world identity")

for pg129_evidence in ["state.persistence_commit", "state.persistence_fields"]:
    if not mode_has_evidence("state", pg129_evidence):
        fail(f"PG-129 runtime persistence evidence missing: {pg129_evidence}")

for pg129_symbol in [
    "disk-npc-memory",
    "runtime-npc-memory",
    "disk-route-progress",
    "runtime-route-progress",
    "runtime-player-location-safe-ground",
]:
    if pg129_symbol not in pg129_player:
        fail(f"PG-129 disk persistence field coverage missing: {pg129_symbol}")

if "committed already-resident chapter=%s route=%s" not in pg129_stream:
    fail("PG-129 already-resident chapter bank must commit without false rollback")
if "IsChapterBankReady(ChapterId, RouteId)" not in pg129_stream:
    fail("PG-129 resident-bank replay guard missing")

if "if (!PendingAudioLoads.Contains(LoadKey))" not in pg129_audio:
    fail("PG-129 cancelled async audio callback can still resurrect stale playback")

# PG-130: import warning debt must converge toward zero instead of accepting a permanent ceiling.
pg130_importer = read(ROOT / "Source" / "ShireJourneyEditorTools" / "Private" / "ShireProductionImportCommandlet.cpp")
pg130_warning_guard = read(ROOT / "Scripts" / "warning_debt_guard.py")
pg130_warning_tests = read(ROOT / "Scripts" / "test_warning_debt_guard.py")

for pg130_symbol in [
    "InjectDeterministicFaceUVs",
    "HasObjTextureCoordinates",
    "GeneratedUVSourceMeshes",
    "DoesPackageExist(ProductionSurfacePackage)",
]:
    if pg130_symbol not in pg130_importer:
        fail(f"PG-130 deterministic import normalization missing: {pg130_symbol}")

for pg130_category in [
    '("Degenerate tangent bases", re.compile',
    '("Nearly-zero tangents", re.compile',
    '("Nearly-zero binormals", re.compile',
    '("Missing production master surface", re.compile',
]:
    start = pg130_warning_guard.find(pg130_category)
    if start < 0:
        fail(f"PG-130 zero-warning debt category missing: {pg130_category}")
    else:
        line_end = pg130_warning_guard.find("\n", start)
        row = pg130_warning_guard[start:line_end if line_end >= 0 else None]
        if ", 0," not in row:
            fail(f"PG-130 warning-debt category is not zero-tolerance: {pg130_category}")

if "test_tangent_warning_categories_are_zero_tolerance" not in pg130_warning_tests:
    fail("PG-130 zero-tolerance warning regression test missing")

# PG-132: legacy save repair must settle silently before final world publication.
pg132_quest = read(resolve_source("ShireQuestSubsystem.cpp"))
pg132_player = read(resolve_source("ShirePlayerCharacter.cpp"))

pg132_commit_start = pg132_quest.find("void UShireQuestSubsystem::CommitPersistenceRestore")
pg132_commit_end = pg132_quest.find("void UShireQuestSubsystem::AbortPersistenceRestore", pg132_commit_start)
pg132_commit = pg132_quest[pg132_commit_start:pg132_commit_end]
pg132_repair = pg132_commit.find("OnQuestStateRestored.Broadcast();")
pg132_release = pg132_commit.find("bPersistenceRestoreInProgress = false;")
pg132_experience = pg132_commit.find("OnExperienceChanged.Broadcast")
if min(pg132_repair, pg132_release, pg132_experience) < 0 or not (pg132_repair < pg132_release < pg132_experience):
    fail("PG-132 restore repair hook must run while broadcasts are suppressed and before final experience publication")

for pg132_function in ["StartQuest", "StartChapter", "StartExperience"]:
    pg132_start = pg132_quest.find(f"void UShireQuestSubsystem::{pg132_function}")
    pg132_next = pg132_quest.find("\nvoid UShireQuestSubsystem::", pg132_start + 1)
    pg132_body = pg132_quest[pg132_start:pg132_next if pg132_next >= 0 else None]
    if "!bPersistenceRestoreInProgress" not in pg132_body:
        fail(f"PG-132 {pg132_function} can publish intermediate restore state")

if "CurrentRouteId != NAME_None && !bPersistenceRestoreInProgress" not in pg132_quest:
    fail("PG-132 StartExperience may overwrite restored route progress with pre-commit player transform")

pg132_restore_start = pg132_player.find("bool AShirePlayerCharacter::RestoreSaveSnapshot")
pg132_restore_end = pg132_player.find("bool AShirePlayerCharacter::SaveAutomaticCheckpoint", pg132_restore_start)
pg132_restore = pg132_player[pg132_restore_start:pg132_restore_end]
pg132_health = pg132_restore.find("CurrentHealth = FMath::Clamp")
pg132_commit_call = pg132_restore.find("CommitPersistenceRestore(true)")
if pg132_health < 0 or pg132_commit_call < 0 or pg132_health > pg132_commit_call:
    fail("PG-132 player-life state must be restored before final world identity publication")

# PG-131: gameplay mutation must remain behind the committed-world transaction barrier.
pg131_player_h = read(resolve_source("ShirePlayerCharacter.h"))
pg131_player = read(resolve_source("ShirePlayerCharacter.cpp"))
pg131_router = read(resolve_source("ChapterWorldRouter.cpp"))
pg131_trigger = read(resolve_source("ShireQuestTrigger.cpp"))
pg131_traversal = read(resolve_source("ShireTraversalChallenge.cpp"))
pg131_puzzle = read(resolve_source("ShireEnvironmentalPuzzle.cpp"))
pg131_world_interaction = read(resolve_source("ShireWorldEventInteraction.cpp"))
pg131_npc = read(resolve_source("ShireNPC.cpp"))
pg131_game_mode = read(resolve_source("ShireGameMode.cpp"))
pg131_importer = read(ROOT / "Source" / "ShireJourneyEditorTools" / "Private" / "ShireProductionImportCommandlet.cpp")

for pg131_symbol in [
    "SetWorldTransitionHeld",
    "IsWorldTransitionHeld",
    "IsGameplayWorldCommitted",
    "bWorldTransitionHeld",
]:
    if pg131_symbol not in (pg131_player_h + pg131_player):
        fail(f"PG-131 player world-transaction barrier missing: {pg131_symbol}")

if "ShirePlayer->SetWorldTransitionHeld(bHold);" not in pg131_router:
    fail("PG-131 ChapterWorldRouter does not mirror authoritative hold into player mutation barrier")

for pg131_name, pg131_text in [
    ("quest trigger", pg131_trigger),
    ("traversal challenge", pg131_traversal),
    ("environmental puzzle", pg131_puzzle),
    ("world event interaction", pg131_world_interaction),
    ("named NPC interaction", pg131_npc),
]:
    if "IsGameplayWorldCommitted()" not in pg131_text:
        fail(f"PG-131 {pg131_name} can mutate gameplay before committed-world publication")

if "IsLogicalWorldContextCommitted()" not in pg131_npc:
    fail("PG-131 named NPC banter does not respect committed logical context")

if not mode_has_evidence("transitions", "transition.barrier"):
    fail("PG-131 transition barrier runtime evidence contract missing")
for pg131_symbol in ["IsWorldTransitionHeld()", "IsGameplayWorldCommitted()"]:
    if pg131_symbol not in (pg131_game_mode + pg131_player):
        fail(f"PG-131 committed-world mutation guard missing: {pg131_symbol}")

if "ProductionSurfaceObjectPath" not in pg131_importer or    "ObjectPathToPackageName(ProductionSurfaceObjectPath)" not in pg131_importer:
    fail("PG-131 UE4.27 package-name overload must receive an explicit FString")

# PG-133: transition starts at logical request time and all delayed side effects stay origin-bound.
pg133_router = read(resolve_source("ChapterWorldRouter.cpp"))
pg133_quest = read(resolve_source("ShireQuestSubsystem.cpp"))
pg133_quest_h = read(resolve_source("ShireQuestSubsystem.h"))
pg133_player = read(resolve_source("ShirePlayerCharacter.cpp"))
pg133_player_h = read(resolve_source("ShirePlayerCharacter.h"))
pg133_context = read(resolve_source("ShireNPCContextSubsystem.cpp"))
pg133_context_h = read(resolve_source("ShireNPCContextSubsystem.h"))
pg133_ambient = read(resolve_source("ShireAmbientNPC.cpp"))
pg133_named = read(resolve_source("ShireNPC.cpp"))
pg133_enemy = read(resolve_source("FellowshipEnemyPrototype.cpp"))
pg133_mythic = read(resolve_source("FellowshipMythicThreat.cpp"))
pg133_rider = read(resolve_source("BlackRiderPrototype.cpp"))
pg133_game_mode = read(resolve_source("ShireGameMode.cpp"))
pg133_runtime = read(ROOT / "Scripts" / "runtime_smoke.py")
pg133_importer = read(ROOT / "Source" / "ShireJourneyEditorTools" / "Private" / "ShireProductionImportCommandlet.cpp")

pg133_load_start = pg133_router.find("void AChapterWorldRouter::LoadChapterWorld")
pg133_load_end = pg133_router.find("void AChapterWorldRouter::HandleChapterAssetsReady", pg133_load_start)
pg133_load = pg133_router[pg133_load_start:pg133_load_end]
pg133_hold = pg133_load.find("SetPlayerWorldHold(true);")
pg133_pending = pg133_load.find("PendingRouteId = RouteId;")
if pg133_hold < 0 or pg133_pending < 0 or pg133_hold > pg133_pending:
    fail("PG-133 player/world transaction hold must begin before pending destination preload")
if "SetPlayerWorldHold(false);" not in pg133_load:
    fail("PG-133 rapid transition cancellation cannot release hold after returning to exact committed world")

pg133_start_chapter = pg133_quest.find("void UShireQuestSubsystem::StartChapter")
pg133_start_chapter_end = pg133_quest.find("FShireRouteProgress UShireQuestSubsystem::CaptureCurrentRouteProgress", pg133_start_chapter)
pg133_start_chapter_body = pg133_quest[pg133_start_chapter:pg133_start_chapter_end]
if "PruneNPCMemoryForCurrentChapter();" in pg133_start_chapter_body:
    fail("PG-133 StartChapter must not destructively prune persistent NPC memory before world commit")
if "void UShireQuestSubsystem::CommitWorldBoundState()" not in pg133_quest:
    fail("PG-133 quest committed-world housekeeping owner missing")
if "CommitQuests->CommitWorldBoundState();" not in pg133_router:
    fail("PG-133 router does not execute world-bound quest housekeeping at destination commit")

pg133_restore_memory = pg133_quest[pg133_quest.find("void UShireQuestSubsystem::RestoreNPCMemoryState"):]
if "if (!bPersistenceRestoreInProgress)" not in pg133_restore_memory:
    fail("PG-133 restore may prune NPC memory before final canonical commit")

pg133_public_context = pg133_context_h[:pg133_context_h.find("private:")]
if "IsLogicalWorldContextCommitted() const;" not in pg133_public_context:
    fail("PG-133 NPC committed-context query must be public to named/world consumers")
pg133_context_start = pg133_context.find("bool UShireNPCContextSubsystem::IsLogicalWorldContextCommitted() const")
pg133_context_end = pg133_context.find("FName UShireNPCContextSubsystem::GetContextChapterId", pg133_context_start)
pg133_context_body = pg133_context[pg133_context_start:pg133_context_end]
if "if (!bHasCommittedWorldContext)" not in pg133_context_body or "return false;" not in pg133_context_body:
    fail("PG-133 NPC context must fail closed before the first committed world")

for pg133_token in [
    "CheckpointSaveInFlightChapterId",
    "CheckpointSaveInFlightRouteId",
    "CheckpointSaveInFlightEpisodeId",
    "CheckpointSaveInFlightWorldRevision",
]:
    if pg133_token not in pg133_player_h:
        fail(f"PG-133 async checkpoint origin context missing: {pg133_token}")
for pg133_token in [
    "bSameCommittedContext",
    "bApplyCheckpointEffects",
    "Router->GetWorldRevision() == CompletedWorldRevision",
]:
    if pg133_token not in pg133_player:
        fail(f"PG-133 stale async checkpoint callback guard missing: {pg133_token}")

if pg133_ambient.count("TActorIterator<AShireAmbientNPC>") > 1:
    fail("PG-133 ambient social check regressed to multiple full actor scans")

for pg133_name, pg133_text in [
    ("ambient NPC", pg133_ambient),
    ("named NPC", pg133_named),
    ("enemy", pg133_enemy),
    ("mythic threat", pg133_mythic),
    ("Black Rider", pg133_rider),
]:
    if "IsGameplayWorldCommitted()" not in pg133_text:
        fail(f"PG-133 {pg133_name} can consume destination gameplay state while world swap is pending")

for pg133_evidence in ["transition.barrier", "transition.sequence"]:
    if not mode_has_evidence("transitions", pg133_evidence):
        fail(f"PG-133 continuous transition evidence missing: {pg133_evidence}")

if "ObjectPathToPackageName(ProductionSurfacePath)" in pg133_importer:
    fail("PG-133 ambiguous UE4.27 ObjectPathToPackageName(const TCHAR*) call reintroduced")
if "ObjectPathToPackageName(ProductionSurfaceObjectPath)" not in pg133_importer:
    fail("PG-133 explicit FString importer package-name call missing")

# PG-134: source geometry that can generate zero tangent/binormal basis is rejected before Unreal import.
pg134_asset_audit = read(ROOT / "Scripts" / "asset_quality_audit.py")
pg134_workflow = read(ROOT / ".github" / "workflows" / "pre-unreal-validation.yml")
if (
    '"%PYTHON_EXE%" Scripts\\asset_quality_audit.py --strict' not in pg134_workflow
    or "resolve_runtime_python.ps1" not in pg134_workflow
    or "%RUNNER_TEMP%\\shire-pre-unreal" not in pg134_workflow
    or "SHIRE_PRE_ROOT" not in pg134_workflow
    or "PRE_UNREAL_EXACT_CHECKOUT_PASS" not in pg134_workflow
    or "hosted=true" not in pg134_workflow
    or 'rmdir /S /Q "%GITHUB_WORKSPACE%"' in pg134_workflow
):
    fail("PG-134 Pre-Unreal must run strict asset audit from an isolated exact-head static checkout without touching the Unreal workspace")
for pg134_symbol in [
    "obj_with_degenerate_uv_triangles",
    "degenerate UV triangle",
    "obj_with_opposed_normals",
    "oppose the geometric face normal",
]:
    if pg134_symbol not in pg134_asset_audit:
        fail(f"PG-134 source tangent-basis guard missing: {pg134_symbol}")

for pg134_asset in [
    ROOT / "SourceAssets" / "Production" / "Enemies" / "Balrog" / "SM_Balrog_Wing.obj",
    ROOT / "SourceAssets" / "Production" / "Enemies" / "Lurtz" / "SM_Lurtz_Blade.obj",
    ROOT / "SourceAssets" / "Production" / "World" / "Isengard" / "SM_Isengard_IndustrialPitRim.obj",
]:
    pg134_text = read(pg134_asset)
    pg134_faces = [line for line in pg134_text.splitlines() if line.startswith("f ")]
    pg134_uvs = [line for line in pg134_text.splitlines() if line.startswith("vt ")]
    pg134_normals = [line for line in pg134_text.splitlines() if line.startswith("vn ")]
    if not pg134_faces or len(pg134_uvs) < len(pg134_faces) * 3 or len(pg134_normals) < len(pg134_faces):
        fail(f"PG-134 repaired tangent-basis asset is not face-local: {pg134_asset.name}")

# PG-135: queued async checkpoints preserve their captured snapshot/origin across world revisions.
pg135_player_h = read(resolve_source("ShirePlayerCharacter.h"))
pg135_player = read(resolve_source("ShirePlayerCharacter.cpp"))
for pg135_symbol in [
    "CheckpointSaveInFlightSnapshot",
    "QueuedCheckpointSnapshot",
    "QueuedCheckpointChapterId",
    "QueuedCheckpointRouteId",
    "QueuedCheckpointEpisodeId",
    "QueuedCheckpointWorldRevision",
    "StartCheckpointSnapshotSave",
    "async-save=queued-snapshot",
]:
    if pg135_symbol not in (pg135_player_h + pg135_player):
        fail(f"PG-135 queued checkpoint snapshot/origin contract missing: {pg135_symbol}")

pg135_save_start = pg135_player.find("bool AShirePlayerCharacter::SaveAutomaticCheckpoint")
pg135_save_end = pg135_player.find("void AShirePlayerCharacter::HandleCheckpointSaveComplete", pg135_save_start)
pg135_save = pg135_player[pg135_save_start:pg135_save_end]
pg135_snapshot = pg135_save.find("CreateSaveSnapshot")
pg135_queue = pg135_save.find("if (bCheckpointSaveInFlight)")
if pg135_snapshot < 0 or pg135_queue < 0 or pg135_snapshot > pg135_queue:
    fail("PG-135 queued checkpoint must capture its snapshot before entering the async queue")

pg135_callback_start = pg135_player.find("void AShirePlayerCharacter::HandleCheckpointSaveComplete")
pg135_callback_end = pg135_player.find("bool AShirePlayerCharacter::RestoreAutomaticCheckpoint", pg135_callback_start)
pg135_callback = pg135_player[pg135_callback_start:pg135_callback_end]
if "SaveAutomaticCheckpoint(NextId" in pg135_callback:
    fail("PG-135 queued checkpoint callback must not rebuild a queued snapshot from later live state")
for pg135_symbol in [
    "NextSnapshot",
    "NextWorldRevision",
    "StartCheckpointSnapshotSave(",
]:
    if pg135_symbol not in pg135_callback:
        fail(f"PG-135 queued checkpoint dispatch lost captured origin: {pg135_symbol}")

# PG-136: rollback state is captured at the pre-mutation transition boundary and every rejected destination fails back atomically.
pg136_quest_h = read(resolve_source("ShireQuestSubsystem.h"))
pg136_quest = read(resolve_source("ShireQuestSubsystem.cpp"))
pg136_router_h = read(resolve_source("ChapterWorldRouter.h"))
pg136_router = read(resolve_source("ChapterWorldRouter.cpp"))
pg136_game_mode = read(resolve_source("ShireGameMode.cpp"))
pg136_runtime = read(ROOT / "Scripts" / "runtime_smoke.py")
pg136_state_cmd = read(ROOT / "Scripts" / "ci_runtime_state.cmd")
pg136_runtime_tests = read(ROOT / "Scripts" / "test_runtime_smoke.py")

for pg136_symbol in [
    "FOnWorldTransitionRequested",
    "OnWorldTransitionRequested",
]:
    if pg136_symbol not in pg136_quest_h:
        fail(f"PG-136 pre-mutation transition contract missing: {pg136_symbol}")

pg136_start_chapter_start = pg136_quest.find("void UShireQuestSubsystem::StartChapter")
pg136_start_chapter_end = pg136_quest.find("FShireRouteProgress UShireQuestSubsystem::CaptureCurrentRouteProgress", pg136_start_chapter_start)
pg136_start_chapter = pg136_quest[pg136_start_chapter_start:pg136_start_chapter_end]
if not signal_precedes_member_mutation(
        pg136_start_chapter,
        "OnWorldTransitionRequested.Broadcast",
        ("CurrentChapterId", "CurrentEpisodeId", "PlayableCharacterId")):
    fail("PG-136 StartChapter must publish transition intent before logical chapter mutation")

pg136_start_experience_start = pg136_quest.find("void UShireQuestSubsystem::StartExperience")
pg136_start_experience_end = pg136_quest.find("TMap<FName, FShireRouteProgress>", pg136_start_experience_start)
pg136_start_experience = pg136_quest[pg136_start_experience_start:pg136_start_experience_end]
if not signal_precedes_member_mutation(
        pg136_start_experience,
        "OnWorldTransitionRequested.Broadcast",
        ("CurrentRouteId", "CurrentChapterId", "CurrentEpisodeId", "PlayableCharacterId")):
    fail("PG-136 StartExperience must publish transition intent before logical route mutation")

for pg136_symbol in [
    "HandleWorldTransitionRequested",
    "OnWorldTransitionRequested.AddUObject",
    "OnWorldTransitionRequested.RemoveAll",
]:
    if pg136_symbol not in (pg136_router_h + pg136_router):
        fail(f"PG-136 router transition-intent ownership missing: {pg136_symbol}")

pg136_request_start = pg136_router.find("void AChapterWorldRouter::HandleWorldTransitionRequested")
pg136_request_end = pg136_router.find("void AChapterWorldRouter::HandleChapterChanged", pg136_request_start)
pg136_request = pg136_router[pg136_request_start:pg136_request_end]
pg136_capture = pg136_request.find("CaptureCommittedRollbackSnapshot();")
pg136_hold = pg136_request.rfind("SetPlayerWorldHold(true);")
if pg136_capture < 0 or pg136_hold < 0 or pg136_capture > pg136_hold:
    fail("PG-136 exact committed rollback snapshot must be captured before the normal transition hold")
if "IsWorldCommitted(" not in pg136_request:
    fail("PG-136 pending requests may overwrite rollback snapshot with uncommitted state")

pg136_commit_start = pg136_router.find("void AChapterWorldRouter::CommitChapterWorld")
pg136_commit = pg136_router[pg136_commit_start:]
if 'RouteId == TEXT("FrodoMain")' not in pg136_commit or    'RouteId == TEXT("GandalfParallel")' not in pg136_commit or    'ChapterId == TEXT("P1C01")' not in pg136_commit:
    fail("PG-136 route/chapter compatibility contract is not explicit")
pg136_reject = pg136_commit.find("if (!bSupported)")
pg136_reject_tail = pg136_commit[pg136_reject:pg136_commit.find("SetPlayerWorldHold(true);", pg136_reject)]
if pg136_reject < 0 or "RollbackFailedWorldSwap" not in pg136_reject_tail:
    fail("PG-136 unsupported world request must execute rollback instead of leaving the transaction held")

if not mode_has_evidence("faults", "fault.invalid_request_rejected"):
    fail("PG-136 invalid direct destination must be proven rejected before a world transaction")
if "-AuditFaults" not in MODE_EXTRA_ARGS.get("faults", ()):
    fail("PG-136 runtime contract does not expose fault-injection mode")
if "--mode faults" not in pg136_state_cmd:
    fail("PG-136 state CI does not execute rollback fault injection")
if "test_fault_mode_requires_complete_rollback_evidence" not in pg136_runtime_tests:
    fail("PG-136 rollback evidence regression unit test missing")

# PG-137: save restores share the pre-mutation rollback boundary and delayed async readiness keeps old-world authority.
pg137_quest_h = read(resolve_source("ShireQuestSubsystem.h"))
pg137_quest = read(resolve_source("ShireQuestSubsystem.cpp"))
pg137_player = read(resolve_source("ShirePlayerCharacter.cpp"))
pg137_stream_h = read(resolve_source("ShireChapterAssetStreamingSubsystem.h"))
pg137_stream = read(resolve_source("ShireChapterAssetStreamingSubsystem.cpp"))
pg137_game_mode = read(resolve_source("ShireGameMode.cpp"))
pg137_runtime = read(ROOT / "Scripts" / "runtime_smoke.py")
pg137_state_cmd = read(ROOT / "Scripts" / "ci_runtime_state.cmd")
pg137_runtime_tests = read(ROOT / "Scripts" / "test_runtime_smoke.py")

for pg137_symbol in [
    "PreparePersistenceWorldTransition",
    "OnWorldTransitionRequested.Broadcast",
]:
    if pg137_symbol not in (pg137_quest_h + pg137_quest):
        fail(f"PG-137 persistence transition-intent contract missing: {pg137_symbol}")

pg137_restore_start = pg137_player.find("bool AShirePlayerCharacter::RestoreSaveSnapshot")
pg137_restore_end = pg137_player.find("bool AShirePlayerCharacter::StartCheckpointSnapshotSave", pg137_restore_start)
pg137_restore = pg137_player[pg137_restore_start:pg137_restore_end]
pg137_begin = pg137_restore.find("BeginPersistenceRestore()")
pg137_prepare = pg137_restore.find("PreparePersistenceWorldTransition")
pg137_mutation = pg137_restore.find("RestoreQuestState(")
if min(pg137_begin, pg137_prepare, pg137_mutation) < 0 or not (pg137_begin < pg137_prepare < pg137_mutation):
    fail("PG-137 save restore must snapshot/hold after transaction begin but before restored logical mutation")

pg137_prepare_start = pg137_quest.find("void UShireQuestSubsystem::PreparePersistenceWorldTransition")
pg137_prepare_end = pg137_quest.find("void UShireQuestSubsystem::CommitPersistenceRestore", pg137_prepare_start)
pg137_prepare_body = pg137_quest[pg137_prepare_start:pg137_prepare_end]
if "!bPersistenceRestoreInProgress" not in pg137_prepare_body or "OnWorldTransitionRequested.Broadcast" not in pg137_prepare_body:
    fail("PG-137 persistence transition intent may publish outside an active restore transaction")

for pg137_symbol in [
    "PublishPendingReady",
    "ShireCIAssetReadyDelay=",
    "ci-ready-delay",
    "CompletedSerial != RequestSerial",
]:
    if pg137_symbol not in (pg137_stream_h + pg137_stream):
        fail(f"PG-137 cancellable delayed-ready streaming test hook missing: {pg137_symbol}")

pg137_complete_start = pg137_stream.find("void UShireChapterAssetStreamingSubsystem::HandleAsyncLoadComplete")
pg137_publish_start = pg137_stream.find("void UShireChapterAssetStreamingSubsystem::PublishPendingReady")
pg137_stream_tail = pg137_stream[pg137_complete_start:]
if pg137_complete_start < 0 or pg137_publish_start < 0 or "SetTimer(" not in pg137_stream_tail:
    fail("PG-137 delayed-ready hook must be timer-based and non-blocking")
if 'FParse::Param(FCommandLine::Get(), TEXT("ShireCIRuntimeAudit"))' not in pg137_stream_tail:
    fail("PG-137 forced streaming delay must remain CI-only")

for pg137_evidence in ["pending.window", "pending.commit"]:
    if not mode_has_evidence("pending", pg137_evidence):
        fail(f"PG-137 delayed transition evidence missing: {pg137_evidence}")
pg137_args = MODE_EXTRA_ARGS.get("pending", ())
if "-AuditPendingTransition" not in pg137_args or "-ShireCIAssetReadyDelay=2.0" not in pg137_args:
    fail("PG-137 runtime contract does not force a bounded delayed-ready transition")
if "--mode pending" not in pg137_state_cmd:
    fail("PG-137 state CI does not execute delayed transition audit")
if "test_pending_mode_requires_both_window_and_commit_evidence" not in pg137_runtime_tests:
    fail("PG-137 delayed transition marker regression test missing")

# PG-138: chapter streaming failures are explicit rollback events; no compatibility-success path may hide missing residency.
pg138_stream_h = read(resolve_source("ShireChapterAssetStreamingSubsystem.h"))
pg138_stream = read(resolve_source("ShireChapterAssetStreamingSubsystem.cpp"))
pg138_router_h = read(resolve_source("ChapterWorldRouter.h"))
pg138_router = read(resolve_source("ChapterWorldRouter.cpp"))
pg138_game_mode = read(resolve_source("ShireGameMode.cpp"))
pg138_runtime = read(ROOT / "Scripts" / "runtime_smoke.py")

for pg138_symbol in [
    "FOnShireChapterAssetsFailed",
    "OnChapterAssetsFailed",
    "AreBankAssetsResolved",
    "FailPendingRequest",
    "async-complete-with-unresolved-assets",
]:
    if pg138_symbol not in (pg138_stream_h + pg138_stream):
        fail(f"PG-138 fail-closed chapter residency contract missing: {pg138_symbol}")

if "compatibility path continues" in pg138_stream:
    fail("PG-138 missing/invalid chapter bank may not be promoted through compatibility success")

pg138_fail_start = pg138_stream.find("void UShireChapterAssetStreamingSubsystem::FailPendingRequest")
pg138_fail_end = pg138_stream.find("void UShireChapterAssetStreamingSubsystem::HandleAsyncLoadComplete", pg138_fail_start)
pg138_fail = pg138_stream[pg138_fail_start:pg138_fail_end]
if "OnChapterAssetsFailed.Broadcast" not in pg138_fail:
    fail("PG-138 streaming failure does not publish rollback ownership")
if "ResidentHandle.Reset" in pg138_fail or "ResidentChapterId = NAME_None" in pg138_fail:
    fail("PG-138 failed pending load may not release the previous resident bank")

for pg138_symbol in [
    "HandleChapterAssetsFailed",
    "OnChapterAssetsFailed.AddUObject",
    "OnChapterAssetsFailed.RemoveAll",
]:
    if pg138_symbol not in (pg138_router_h + pg138_router):
        fail(f"PG-138 router streaming-failure bridge missing: {pg138_symbol}")

pg138_router_fail_start = pg138_router.find("void AChapterWorldRouter::HandleChapterAssetsFailed")
pg138_router_fail_end = pg138_router.find("AActor* AChapterWorldRouter::SpawnWorldForRequest", pg138_router_fail_start)
pg138_router_fail = pg138_router[pg138_router_fail_start:pg138_router_fail_end]
if "RollbackFailedWorldSwap" not in pg138_router_fail:
    fail("PG-138 chapter preload failure must rollback the committed origin")

if "#if !UE_BUILD_SHIPPING" not in pg138_stream or "ShireCIForceChapterAssetFailure=" not in pg138_stream:
    fail("PG-138 deterministic streaming failure injection must remain non-shipping")
if "-ShireCIForceChapterAssetFailure=P1C02" not in MODE_EXTRA_ARGS.get("faults", ()):
    fail("PG-138 fault runtime contract does not exercise a real valid-bank async failure")
for pg138_evidence in ["fault.snapshot_stream", "fault.stream_failure"]:
    if not mode_has_evidence("faults", pg138_evidence):
        fail(f"PG-138 streaming failure evidence missing: {pg138_evidence}")

# PG-139: texture-pool scalability must have one authority and every runtime audit log belongs to warning debt.
pg139_engine = read(ROOT / "Config" / "DefaultEngine.ini")
pg139_scalability = read(ROOT / "Config" / "DefaultScalability.ini")
pg139_warning_guard = read(ROOT / "Scripts" / "warning_debt_guard.py")
pg139_warning_tests = read(ROOT / "Scripts" / "test_warning_debt_guard.py")

if re.search(r"^\s*r\.Streaming\.PoolSize\s*=", pg139_engine, flags=re.M):
    fail("PG-139 DefaultEngine may not hard-set r.Streaming.PoolSize; TextureQuality scalability owns the low-spec pool")
for pg139_tier in ("0", "1", "2"):
    pg139_section = re.search(
        rf"\[TextureQuality@{pg139_tier}\](.*?)(?=\n\[|\Z)",
        pg139_scalability,
        flags=re.S)
    if not pg139_section or "r.Streaming.PoolSize=" not in pg139_section.group(1):
        fail(f"PG-139 TextureQuality@{pg139_tier} must define r.Streaming.PoolSize")
if "Streaming pool scalability override warnings" not in pg139_warning_guard:
    fail("PG-139 streaming-pool precedence warning guard missing")
if "from runtime_audit_contracts import RUNTIME_LOG_PREFIXES" not in pg139_warning_guard:
    fail("PG-139 warning-debt runtime scope must consume the central audit registry")
for pg139_prefix in RUNTIME_LOG_PREFIXES:
    if not pg139_prefix.startswith("CI-"):
        fail(f"PG-139 invalid runtime log prefix in central registry: {pg139_prefix}")
if "test_all_transaction_runtime_logs_are_in_runtime_scope" not in pg139_warning_tests:
    fail("PG-139 warning-debt runtime scope regression test missing")

# PG-140: legacy terminal restore publishes one canonical world and stale checkpoint completion cannot mutate a later revision.
pg140_quest_h = read(resolve_source("ShireQuestSubsystem.h"))
pg140_quest = read(resolve_source("ShireQuestSubsystem.cpp"))
pg140_player_h = read(resolve_source("ShirePlayerCharacter.h"))
pg140_player = read(resolve_source("ShirePlayerCharacter.cpp"))
pg140_game_mode = read(resolve_source("ShireGameMode.cpp"))
pg140_runtime = read(ROOT / "Scripts" / "runtime_smoke.py")
pg140_state_cmd = read(ROOT / "Scripts" / "ci_runtime_state.cmd")
pg140_runtime_tests = read(ROOT / "Scripts" / "test_runtime_smoke.py")

for pg140_symbol in [
    "PersistenceRestorePublicationSerial",
    "GetPersistenceRestorePublicationSerial",
    "ShirePersistenceRestorePublication:",
]:
    if pg140_symbol not in (pg140_quest_h + pg140_quest):
        fail(f"PG-140 persistence publication contract missing: {pg140_symbol}")

for pg140_symbol in [
    "RunLegacyTerminalRestoreAuditSetup",
    "RunStaleCheckpointCompletionAudit",
    "ShireCheckpointRevisionAudit:",
]:
    if pg140_symbol not in (pg140_player_h + pg140_player):
        fail(f"PG-140 player persistence-edge audit contract missing: {pg140_symbol}")

for pg140_evidence in ["edge.legacy_terminal", "edge.stale_checkpoint"]:
    if not mode_has_evidence("edges", pg140_evidence):
        fail(f"PG-140 persistence-edge evidence missing: {pg140_evidence}")
if "-AuditPersistenceEdges" not in MODE_EXTRA_ARGS.get("edges", ()):
    fail("PG-140 runtime contract does not expose persistence edge mode")
if "--mode edges" not in pg140_state_cmd:
    fail("PG-140 state CI does not execute persistence edge audit")
if "test_edges_mode_requires_canonical_restore_and_stale_checkpoint_evidence" not in pg140_runtime_tests:
    fail("PG-140 persistence edge marker regression test missing")


# PG-141: UE_LOG verbosity is a compile-time macro token in UE4.27. Runtime
# conditionals in that macro slot create a misleading cascade of compile errors.
for pg141_path in SOURCE.rglob("*.cpp"):
    pg141_text = read(pg141_path)
    if re.search(r"UE_LOG\s*\(\s*[^,]+,\s*[^,]*\?", pg141_text, flags=re.S):
        fail(
            "PG-141 dynamic UE_LOG verbosity is forbidden; use explicit static-verbosity branches: "
            + str(pg141_path.relative_to(ROOT)).replace("\\", "/")
        )

# PG-142: all Python consumers share semantic runtime-audit contracts.
pg142_runtime = read(ROOT / "Scripts" / "runtime_smoke.py")
pg142_runtime_tests = read(ROOT / "Scripts" / "test_runtime_smoke.py")
pg142_deep = read(ROOT / "Scripts" / "deep_project_audit.py")
pg142_warning = read(ROOT / "Scripts" / "warning_debt_guard.py")
pg142_contract_tests = read(ROOT / "Scripts" / "test_runtime_audit_contracts.py")
pg142_workflow = read(ROOT / ".github" / "workflows" / "pre-unreal-validation.yml")
pg142_state_cmd = read(ROOT / "Scripts" / "ci_runtime_state.cmd")
pg142_self = read(ROOT / "Scripts" / "pre_unreal_validate.py")

for pg142_consumer_name, pg142_consumer in [
    ("runtime_smoke.py", pg142_runtime),
    ("deep_project_audit.py", pg142_deep),
]:
    if "runtime_audit_contracts import" not in pg142_consumer:
        fail(f"PG-142 {pg142_consumer_name} must consume the central runtime-audit registry")
if "from runtime_audit_contracts import RUNTIME_LOG_PREFIXES" not in pg142_warning:
    fail("PG-142 warning-debt runtime scope must consume the central registry")
if "test_runtime_audit_contracts.py" not in pg142_workflow:
    fail("PG-142 Pre-Unreal workflow must execute the runtime-audit contract registry tests")
if "test_contract_consumers_do_not_copy_evidence_text" not in pg142_contract_tests:
    fail("PG-142 contract de-duplication regression test missing")

pg142_source_cache = {}
for pg142_evidence_id, pg142_anchor_info in EVIDENCE_SOURCE_ANCHORS.items():
    pg142_relative, pg142_anchor = pg142_anchor_info
    pg142_text = pg142_source_cache.get(pg142_relative)
    if pg142_text is None:
        pg142_text = read(ROOT / pg142_relative)
        pg142_source_cache[pg142_relative] = pg142_text
    if pg142_anchor not in pg142_text:
        fail(f"PG-142 runtime evidence source anchor missing: {pg142_evidence_id} -> {pg142_relative}")

for pg142_mode in STATE_SEQUENCE_MODES:
    if pg142_state_cmd.count(f"--mode {pg142_mode}") != 1:
        fail(f"PG-142 state CI must execute registered mode exactly once: {pg142_mode}")

for pg142_evidence_id, pg142_marker in EVIDENCE_MARKERS.items():
    for pg142_name, pg142_consumer in [
        ("runtime_smoke.py", pg142_runtime),
        ("test_runtime_smoke.py", pg142_runtime_tests),
        ("pre_unreal_validate.py", pg142_self),
        ("deep_project_audit.py", pg142_deep),
        ("warning_debt_guard.py", pg142_warning),
    ]:
        if pg142_marker in pg142_consumer:
            fail(f"PG-142 duplicated runtime evidence text in {pg142_name}: {pg142_evidence_id}")

# PG-167: CI capacity stays event-driven; lightweight static proof is hosted and heavy UE4 proof stays self-hosted.
pg167_pre = read(ROOT / ".github" / "workflows" / "pre-unreal-validation.yml")
for pg167_symbol in [
    "runs-on: windows-latest",
    "cancel-in-progress: true",
]:
    if pg167_symbol not in pg167_pre:
        fail(f"PG-167 hosted static-lane contract missing: {pg167_symbol}")
if "schedule:" in pg167_pre or "- self-hosted" in pg167_pre or "runs-on: ubuntu-latest" in pg167_pre:
    fail("PG-167 Pre-Unreal must be event-driven on hosted Windows and must not occupy the supervised UE4 runner")
if "actions/setup-python@" in pg167_pre or "resolve_runtime_python.ps1" not in pg167_pre or 'shell: cmd' not in pg167_pre:
    fail("PG-167 Pre-Unreal must use an already-provisioned Python interpreter through cmd without setup churn")
if "PYTHON_FAST_PATH_PASS" not in pg167_pre:
    fail("PG-167 Pre-Unreal must try the hosted PATH Python fast path before the robust fallback resolver")
if "uses: actions/checkout@" in pg167_pre:
    fail("PG-167 Pre-Unreal must keep the bounded exact-head checkout contract")
for pg167_checkout_symbol in [
    "PRE_UNREAL_EXACT_FETCH",
    "PRE_UNREAL_EXACT_CHECKOUT_PASS",
    "http.lowSpeedTime=20",
    "fetch --no-tags --prune --depth=2 origin %TARGET_SHA%",
    "reset --hard %TARGET_SHA%",
    "Checkout SHA mismatch",
]:
    if pg167_checkout_symbol not in pg167_pre:
        fail(f"PG-167 bounded exact-head Pre-Unreal checkout missing: {pg167_checkout_symbol}")

pg167_cleanup = read(ROOT / ".github" / "workflows" / "branch-cleanup.yml")
if "runs-on: windows-latest" not in pg167_cleanup:
    fail("PG-167 Branch Cleanup must run on GitHub-hosted Windows so administration never occupies the supervised UE4 runner")
if "- self-hosted" in pg167_cleanup or "- ue4-27" in pg167_cleanup:
    fail("PG-167 Branch Cleanup must not consume the supervised UE4 runner")
for pg167_post_merge_symbol in [
    "pull_request:",
    "- closed",
    "github.event.pull_request.merged == true",
    "github.event.pull_request.merge_commit_sha",
    "github.event.pull_request.head.ref",
    "github.event.pull_request.head.sha",
    "MERGED_HEAD_REF",
    "MERGED_HEAD_SHA",
    "group: branch-cleanup-${{ github.repository }}",
]:
    if pg167_post_merge_symbol not in pg167_cleanup:
        fail(f"PG-167 permanent post-merge cleanup contract missing: {pg167_post_merge_symbol}")
if "\n  push:\n" in pg167_cleanup:
    fail("PG-167 Branch Cleanup must not run on ordinary develop pushes; merged-PR closeout owns automatic cleanup")
for pg167_cleanup_symbol in [
    "BRANCH_CLEANUP_EXACT_CHECKOUT_PASS",
    "SHIRE_CLEANUP_ROOT",
    "isolated=true",
    "run_branch_cleanup.ps1",
    "pull-requests: read",
]:
    if pg167_cleanup_symbol not in pg167_cleanup:
        fail(f"PG-167 hardened branch-cleanup contract missing: {pg167_cleanup_symbol}")
if "uses: actions/checkout@" in pg167_cleanup or "shell: powershell" in pg167_cleanup:
    fail("PG-167 Branch Cleanup must use bounded local checkout and explicit PowerShell Bypass")

pg167_cleanup_script = read(ROOT / "Scripts" / "run_branch_cleanup.ps1")
for pg167_cleanup_guard in [
    "preserve_pending_salvage",
    "active_work_branches",
    "active_infrastructure_branches",
    "Refusing plan-protected branch in delete_after_merge",
    "Plan-protected branch missing after cleanup",
    "BRANCH_CLEANUP_AUTO_ZERO_AHEAD",
    "BRANCH_CLEANUP_KEEP_UNIQUE",
    "BRANCH_CLEANUP_MERGED_HEAD_DELETE",
    "BRANCH_CLEANUP_MERGED_HEAD_MOVED",
    "MERGED_HEAD_SHA is required",
    "compare/develop...",
]:
    if pg167_cleanup_guard not in pg167_cleanup_script:
        fail(f"PG-167 plan-protected branch cleanup guard missing: {pg167_cleanup_guard}")

pg167_classifier = read(ROOT / "Scripts" / "classify_unreal_validation.ps1")
pg167_maintenance_safe = [
    "Scripts/prepare_p1c01_material_intake.ps1",
    "Scripts/promote_p1c01_material_intake.ps1",
    "Scripts/run_p1c01_material_pipeline.ps1",
    "Scripts/install_runner_watchdog.ps1",
    "Scripts/runner_watchdog.ps1",
    "Scripts/runner_log_timestamp.ps1",
    "Scripts/test_runner_watchdog_timestamp.ps1",
    "Scripts/deep_project_audit.py",
    "Scripts/test_deep_project_audit.py",
    "Scripts/source_contracts.py",
    "Scripts/test_source_contracts.py",
    "Scripts/verify_runner_session.ps1",
    "Scripts/test_runtime_smoke.py",
    "Scripts/runtime_smoke.py",
    "Scripts/test_asset_quality_audit.py",
    "Scripts/asset_quality_audit.py",
    "Scripts/run_branch_cleanup.ps1",
]
for pg167_safe_path in pg167_maintenance_safe:
    if pg167_classifier.count(f'"{pg167_safe_path}"') < 2:
        fail(f"PG-167 maintenance path must remain safe in both classifier proof sets: {pg167_safe_path}")

pg167_runner_health = read(ROOT / ".github" / "workflows" / "runner-health.yml")
for pg167_health_symbol in [
    "RUNNER_HEALTH_EXACT_CHECKOUT_PASS",
    "verify_runner_session.ps1",
    "http.lowSpeedTime=20",
]:
    if pg167_health_symbol not in pg167_runner_health:
        fail(f"PG-167 hardened runner-health workflow missing: {pg167_health_symbol}")
if "uses: actions/checkout@" in pg167_runner_health:
    fail("PG-167 Runner Health must not depend on marketplace checkout")

pg167_unreal = read(ROOT / ".github" / "workflows" / "unreal-build-validation.yml")
for pg167_symbol in [
    "paths-ignore:",
    ".github/workflows/**",
    "Data/WholeGame*.json",
    "Data/*Warehouse*.json",
    "Data/P1C01WorldBuildIntakePacketV1.json",
    "Data/BranchCleanupPlan.json",
    "Scripts/run_branch_cleanup.ps1",
    "group: unreal-build-${{ github.repository }}-${{ github.event_name == 'pull_request' && github.head_ref || 'develop' }}",
    "cancel-in-progress: ${{ github.event_name == 'pull_request' }}",
]:
    if pg167_symbol not in pg167_unreal:
        fail(f"PG-167 Unreal queue-isolation contract missing: {pg167_symbol}")


# PG-168: Warehouse staging must not depend on GitHub-hosted workers or obsolete branches.
pg168 = read(ROOT / ".github" / "workflows" / "warehouse-stage.yml")
for pg168_symbol in [
    "branches:",
    "- develop",
    "- self-hosted",
    "- Windows",
    "- X64",
    "- ue4-27",
    "group: warehouse-stage-${{ github.repository }}",
    "cancel-in-progress: true",
]:
    if pg168_symbol not in pg168:
        fail(f"PG-168 warehouse execution contract missing: {pg168_symbol}")
if "runs-on: ubuntu-latest" in pg168 or "runs-on: windows-latest" in pg168:
    fail("PG-168 warehouse staging must not depend on GitHub-hosted runners")
if "integration/comprehensive-foundation-v1" in pg168:
    fail("PG-168 warehouse push trigger still points at an obsolete integration branch")


# PG-187: P1C01 mega chapter pack must batch work without weakening per-car evidence boundaries.
pg187_pack = json.loads(read(ROOT / "Data" / "P1C01MegaChapterPackV1.json"))
pg187_script = read(ROOT / "Scripts" / "run_p1c01_mega_chapter_pack.ps1")
pg187_warehouse = read(ROOT / ".github" / "workflows" / "warehouse-stage.yml")
pg187_classifier = read(ROOT / "Scripts" / "classify_warehouse_validation.ps1")
if pg187_pack.get("status") != "RUNNER_EXECUTION_READY":
    fail("PG-187 P1C01 mega chapter pack must remain execution-ready")
pg187_ids = [str(x.get("id", "")) for x in pg187_pack.get("cars", [])]
for pg187_car in ["INVENTORY_AUDIT","MEGA_PROMOTION","MATERIAL_SOURCE_EXPORT","CHARACTER_INTAKE"]:
    if pg187_car not in pg187_ids:
        fail(f"PG-187 chapter pack car missing: {pg187_car}")
for pg187_symbol in ["P1C01_MEGA_CHAPTER_PACK_PASS","QUARANTINED_CONTINUE","HARD_FAILURE","Asset/source blockers quarantine"]:
    if pg187_symbol not in pg187_script:
        fail(f"PG-187 chapter-pack orchestration contract missing: {pg187_symbol}")
if "WH_RUN_P1C01_CHAPTER_PACK" not in pg187_classifier or "Run P1C01 Mega Chapter Pack" not in pg187_warehouse:
    fail("PG-187 warehouse classifier/workflow is not wired to chapter-pack execution")
if "WH_RUN_P1C01_CHAPTER_PACK != 'true'" not in pg187_warehouse:
    fail("PG-187 legacy overlapping P1C01 warehouse steps must be suppressed during chapter-pack execution")


# PG-188: Material source promotion must scale by bounded batch budgets and item quarantine.
pg188_exporter = read(ROOT / "Scripts" / "export_p1c01_material_source_branch.ps1")
pg188_pack = json.loads(read(ROOT / "Data" / "P1C01MegaChapterPackV1.json"))
pg188_material_car = next((x for x in pg188_pack.get("cars", []) if x.get("id") == "MATERIAL_SOURCE_EXPORT"), {})
pg188_budget = pg188_material_car.get("export_budget", {})
if int(pg188_budget.get("max_single_source_bytes", 0)) != 33554432:
    fail("PG-188 material export single-source budget must remain 32 MiB")
if int(pg188_budget.get("max_batch_source_bytes", 0)) != 268435456:
    fail("PG-188 material export batch budget must remain 256 MiB")
if int(pg188_budget.get("minimum_exported_materials", 0)) != 6:
    fail("PG-188 material export minimum must remain six receipt-verified materials")
for pg188_symbol in [
    "P1C01_MATERIAL_SOURCE_BRANCH_PASS_WITH_QUARANTINE",
    "single_source_budget_exceeded",
    "batch_source_budget_exceeded",
    "tga_lfs_not_configured",
    "MinimumExportedMaterials",
]:
    if pg188_symbol not in pg188_exporter:
        fail(f"PG-188 bounded material export contract missing: {pg188_symbol}")
if "*.tga filter=lfs" in read(ROOT / ".gitattributes") and "tga_lfs_not_configured" not in pg188_exporter:
    fail("PG-188 TGA promotion guard disappeared after LFS policy changed")


# PG-189: Visible-color material intake must be semantic and preserve exact selected-file provenance.
pg189_intake = read(ROOT / "Scripts" / "prepare_p1c01_material_intake.ps1")
pg189_export = read(ROOT / "Scripts" / "export_p1c01_material_source_branch.ps1")
for pg189_symbol in [
    "Test-ExplicitBaseColorName",
    "no_explicit_albedo_png_tga_candidate",
    "selected_basecolor_provenance_missing",
    "provenanceByFile",
    "selected_source_filename",
    'selected_source_kind="EXPLICIT_ALBEDO"',
]:
    if pg189_symbol not in pg189_intake:
        fail(f"PG-189 explicit albedo/provenance contract missing: {pg189_symbol}")
for pg189_forbidden in [
    "$score=100",
    "preview|thumb|render|normal|rough|ao|metal|height|disp",
]:
    if pg189_forbidden in pg189_intake:
        fail(f"PG-189 obsolete permissive base-color ranking returned: {pg189_forbidden}")
for pg189_export_symbol in [
    "selected_source_filename=[string]$item.selected_source_filename",
    "selected_source_kind=[string]$item.selected_source_kind",
]:
    if pg189_export_symbol not in pg189_export:
        fail(f"PG-189 generated receipt selected-file evidence missing: {pg189_export_symbol}")


# PG-190: Windows PowerShell 5.1 compatibility for the material intake helper.
pg190_intake = read(ROOT / "Scripts" / "prepare_p1c01_material_intake.ps1")
if "return if(" in pg190_intake:
    fail("PG-190 PowerShell 5.1 cannot use 'return if(...)' expression syntax")
for pg190_symbol in [
    "if($null -eq $selected){ return $null }",
    "return [string]$selected.file",
]:
    if pg190_symbol not in pg190_intake:
        fail(f"PG-190 PowerShell-compatible base-color selector return missing: {pg190_symbol}")

# PG-204: F2-03 Edoras maximum-safe source wave must preserve canon, source breadth and unassigned Part II runtime identity.
pg204_manifest = json.loads(read(ROOT / "Data" / "F203EdorasMaximumSafeMegaSourceV1.json"))
pg204_runner = read(ROOT / "Scripts" / "run_f203_edoras_maximum_safe_source.ps1")
pg204_workflow = read(ROOT / ".github" / "workflows" / "f203-edoras-maximum-safe-source.yml")
pg204_unreal = read(ROOT / ".github" / "workflows" / "unreal-build-validation.yml")

if pg204_manifest.get("status") != "SOURCE_ARCHITECTURE_READY_INVENTORY_GATED_RUNTIME_MAPPING_UNASSIGNED":
    fail("PG-204 F2-03 source wave status drifted")
if pg204_manifest.get("canonical_mission_id") != "F2-03":
    fail("PG-204 F2-03 canonical mission ID drifted")
if pg204_manifest.get("canonical_title") != "Edoras":
    fail("PG-204 F2-03 canonical title drifted")
if pg204_manifest.get("runtime_consumers") not in ([], None):
    fail("PG-204 F2-03 must not invent a Part II runtime consumer")
if pg204_manifest.get("runtime_mapping_status") != "NOT_ASSIGNED_DO_NOT_INVENT":
    fail("PG-204 F2-03 runtime mapping boundary weakened")

pg204_story = pg204_manifest.get("story_contract", {})
if pg204_story.get("locked_postcondition") != "Rohan evacuates toward Helm's Deep.":
    fail("PG-204 F2-03 locked postcondition drifted")
critical = " ".join(str(x) for x in pg204_story.get("critical_path", []))
for required in ["Theoden restored", "Political and military crisis clarified"]:
    if required not in critical:
        fail(f"PG-204 F2-03 critical path missing: {required}")
for required in ["court exploration", "stables", "equipment", "social scenes"]:
    if required not in pg204_story.get("safe_optional_window", []):
        fail(f"PG-204 F2-03 optional window missing: {required}")
excluded = " ".join(str(x) for x in pg204_story.get("excluded_from_this_pack", []))
for required in ["F2-04", "F2-05"]:
    if required not in excluded:
        fail(f"PG-204 F2-03 later-chapter boundary missing: {required}")

pg204_world = pg204_manifest.get("world_contract", {})
if pg204_world.get("primary_location") != "Rohan / Edoras":
    fail("PG-204 F2-03 location drifted")
if len(pg204_manifest.get("categories", [])) < 32:
    fail("PG-204 F2-03 category breadth below 32")
if len(pg204_manifest.get("bank_policy", {}).get("banks", [])) < 8:
    fail("PG-204 F2-03 bank breadth below 8")
if pg204_manifest.get("bank_policy", {}).get("minimum_ready_banks", 0) < 7:
    fail("PG-204 F2-03 minimum ready bank contract weakened")
landmarks = [x for x in pg204_manifest.get("categories", []) if x.get("landmark")]
if len(landmarks) < 20:
    fail("PG-204 F2-03 configured landmark breadth below 20")
if pg204_manifest.get("landmark_policy", {}).get("minimum_landmark_categories", 0) < 14:
    fail("PG-204 F2-03 landmark readiness threshold weakened")

policy = pg204_manifest.get("source_policy", {})
if policy.get("animated_candidate_extension") != ".fbx":
    fail("PG-204 F2-03 animated candidate extension must remain FBX")
if ".bmp" not in policy.get("forbidden_texture_extensions", []):
    fail("PG-204 F2-03 BMP rejection missing")
if policy.get("minimum_free_disk_reserve_bytes", 0) < 6442450944:
    fail("PG-204 F2-03 warehouse reserve below 6 GiB")
if policy.get("max_total_candidates", 0) < 32000:
    fail("PG-204 F2-03 total candidate ceiling unexpectedly reduced")
if not policy.get("fair_share_across_categories"):
    fail("PG-204 F2-03 fair-share scheduling disabled")

for symbol in [
    "F203_MEGA_SOURCE_INVENTORY_GATE_BEGIN",
    "F203_MEGA_SOURCE_INVENTORY_GATE_PASS",
    "F203_BANK_SOURCE_PASS",
    "F203_LANDMARK_SOURCE_PASS",
    "F203_MEGA_SOURCE_PASS",
    'if($kind -eq "animated" -and $ext -ne $animatedExt)',
]:
    if symbol not in pg204_runner:
        fail(f"PG-204 F2-03 runner marker missing: {symbol}")

for symbol in [
    "name: F2-03 Edoras Maximum Safe Mega Source",
    "cancel-in-progress: false",
    "timeout-minutes: 180",
    "Build F2-03 Edoras maximum-safe source superpack",
]:
    if symbol not in pg204_workflow:
        fail(f"PG-204 F2-03 workflow marker missing: {symbol}")

for ignored in [
    "Data/F203EdorasMaximumSafeMegaSourceV1.json",
    "Scripts/run_f203_edoras_maximum_safe_source.ps1",
    ".github/workflows/f203-edoras-maximum-safe-source.yml",
]:
    if pg204_unreal.count(ignored) < 2:
        fail(f"PG-204 F2-03 tooling path must stay off Unreal push+PR filters: {ignored}")



# PG-205: P1C01 Frodo/Gandalf skeletal candidate wave must preserve real-rig evidence boundaries and low-spec/runtime safety.
pg205_manifest = json.loads(read(ROOT / "Data" / "P1C01HeroSkeletalCandidateWaveV1.json"))
pg205_runner = read(ROOT / "Scripts" / "run_p1c01_hero_skeletal_candidate_wave.ps1")
pg205_workflow = read(ROOT / ".github" / "workflows" / "p1c01-hero-skeletal-candidate-wave.yml")
pg205_unreal = read(ROOT / ".github" / "workflows" / "unreal-build-validation.yml")

if pg205_manifest.get("status") != "FRODO_FIRST_EXACT_TOKEN_AND_STATIC_FBX_QC":
    fail("PG-205 hero skeletal wave status drifted")
if pg205_manifest.get("schema_version", 0) < 2:
    fail("PG-205 exact-token candidate schema missing")
if pg205_manifest.get("owner_execution_order", [])[:2] != ["FRODO", "GANDALF"]:
    fail("PG-205 Frodo-first execution order drifted")
if pg205_manifest.get("runtime_scope") != "P1C01_ONLY":
    fail("PG-205 hero skeletal wave escaped P1C01 scope")
if pg205_manifest.get("runtime_integration_allowed", True):
    fail("PG-205 candidate wave must not claim runtime integration")
chars = pg205_manifest.get("priority_characters", [])
ids = {x.get("id") for x in chars}
for required in ["FRODO", "GANDALF"]:
    if required not in ids:
        fail(f"PG-205 missing priority character: {required}")
policy = pg205_manifest.get("candidate_policy", {})
if policy.get("animated_source_format") != ".fbx":
    fail("PG-205 animated hero candidates must remain FBX-only")
if ".bmp" not in policy.get("forbidden_texture_formats", []):
    fail("PG-205 BMP rejection missing")
if policy.get("ready_for_import_default") is not False:
    fail("PG-205 candidates must not default to READY_FOR_IMPORT")
if policy.get("ranking_semantics") != "EXACT_FILENAME_TOKENS_ONLY":
    fail("PG-205 exact filename-token ranking missing")
if policy.get("substring_matching_forbidden") is not True:
    fail("PG-205 substring-match rejection missing")
frodo_qc = pg205_manifest.get("frodo_static_fbx_qc", {})
if frodo_qc.get("active_character") != "FRODO":
    fail("PG-205 static FBX QC must remain Frodo-first")
if frodo_qc.get("ready_for_import") is not False:
    fail("PG-205 static FBX QC must not claim READY_FOR_IMPORT")
runtime = pg205_manifest.get("runtime_contract", {})
for token in ["TSoftObjectPtr", "FStreamableManager"]:
    if token not in json.dumps(runtime):
        fail(f"PG-205 runtime handoff missing {token}")
if "both skeletal mesh and AnimBP resolve" not in runtime.get("fallback_rule", ""):
    fail("PG-205 fallback must remain until full rig pair resolves")

for symbol in [
    "P1C01_HERO_RIG_INVENTORY_GATE_BEGIN",
    "P1C01_HERO_RIG_INVENTORY_GATE_PASS",
    "P1C01_HERO_RIG_CANDIDATE_PASS",
    "RIG_BASE_CANDIDATE_STATIC_QC_REQUIRED",
    "EXACT_FILENAME_TOKEN_MATCH",
    "ready_for_import=$false",
]:
    if symbol not in pg205_runner:
        fail(f"PG-205 runner marker missing: {symbol}")

for symbol in [
    "name: P1C01 Frodo Gandalf Skeletal Candidate Wave",
    "cancel-in-progress: false",
    "Rank Frodo Gandalf skeletal candidates",
]:
    if symbol not in pg205_workflow:
        fail(f"PG-205 workflow marker missing: {symbol}")

for ignored in [
    "Data/P1C01HeroSkeletalCandidateWaveV1.json",
    "Scripts/run_p1c01_hero_skeletal_candidate_wave.ps1",
    ".github/workflows/p1c01-hero-skeletal-candidate-wave.yml",
]:
    if pg205_unreal.count(ignored) < 2:
        fail(f"PG-205 candidate tooling path must stay off Unreal push+PR filters: {ignored}")




# PG-206: F2-04 Road & Helm's Deep Prep maximum-safe source wave must preserve prep/siege boundaries and unassigned Part II runtime identity.
pg206_manifest = json.loads(read(ROOT / "Data" / "F204RoadHelmsDeepPrepMaximumSafeMegaSourceV1.json"))
pg206_runner = read(ROOT / "Scripts" / "run_f204_road_helms_deep_prep_maximum_safe_source.ps1")
pg206_workflow = read(ROOT / ".github" / "workflows" / "f204-road-helms-deep-prep-maximum-safe-source.yml")
pg206_unreal = read(ROOT / ".github" / "workflows" / "unreal-build-validation.yml")

if pg206_manifest.get("status") != "SOURCE_ARCHITECTURE_READY_INVENTORY_GATED_RUNTIME_MAPPING_UNASSIGNED":
    fail("PG-206 F2-04 source wave status drifted")
if pg206_manifest.get("canonical_mission_id") != "F2-04":
    fail("PG-206 F2-04 mission ID drifted")
if pg206_manifest.get("canonical_title") != "Road & Helm's Deep Prep":
    fail("PG-206 F2-04 title drifted")
if pg206_manifest.get("runtime_consumers") not in ([], None):
    fail("PG-206 F2-04 must not invent a Part II runtime consumer")
if pg206_manifest.get("runtime_mapping_status") != "NOT_ASSIGNED_DO_NOT_INVENT":
    fail("PG-206 F2-04 runtime mapping boundary weakened")

story = pg206_manifest.get("story_contract", {})
if story.get("locked_postcondition") != "Uruk army arrives.":
    fail("PG-206 F2-04 locked postcondition drifted")
critical = " ".join(str(x) for x in story.get("critical_path", []))
for required in ["Refugees move under threat", "Defenses are prepared"]:
    if required not in critical:
        fail(f"PG-206 F2-04 critical path missing: {required}")
for required in ["escort","rescue","armory","wall prep","civilians"]:
    if required not in story.get("safe_optional_window", []):
        fail(f"PG-206 F2-04 optional window missing: {required}")
excluded = " ".join(str(x) for x in story.get("excluded_from_this_pack", []))
for required in ["F2-05", "siege", "breach", "dawn counterattack"]:
    if required not in excluded:
        fail(f"PG-206 F2-04 siege boundary missing: {required}")

world = pg206_manifest.get("world_contract", {})
if world.get("primary_location") != "Rohan / Helm's Deep":
    fail("PG-206 F2-04 location drifted")
if len(pg206_manifest.get("categories", [])) < 36:
    fail("PG-206 F2-04 category breadth below 36")
if len(pg206_manifest.get("bank_policy", {}).get("banks", [])) < 9:
    fail("PG-206 F2-04 bank breadth below 9")
if pg206_manifest.get("bank_policy", {}).get("minimum_ready_banks", 0) < 8:
    fail("PG-206 F2-04 ready-bank threshold weakened")
landmarks = [x for x in pg206_manifest.get("categories", []) if x.get("landmark")]
if len(landmarks) < 19:
    fail("PG-206 F2-04 configured landmark breadth below 19")
if pg206_manifest.get("landmark_policy", {}).get("minimum_landmark_categories", 0) < 16:
    fail("PG-206 F2-04 landmark readiness threshold weakened")

policy = pg206_manifest.get("source_policy", {})
if policy.get("animated_candidate_extension") != ".fbx":
    fail("PG-206 F2-04 animated candidates must remain FBX-only")
if ".bmp" not in policy.get("forbidden_texture_extensions", []):
    fail("PG-206 F2-04 BMP rejection missing")
if policy.get("minimum_free_disk_reserve_bytes", 0) < 6442450944:
    fail("PG-206 F2-04 warehouse reserve below 6 GiB")
if policy.get("max_total_candidates", 0) < 34000:
    fail("PG-206 F2-04 total candidate ceiling unexpectedly reduced")
if not policy.get("fair_share_across_categories"):
    fail("PG-206 F2-04 fair-share scheduling disabled")

for symbol in [
    "F204_MEGA_SOURCE_INVENTORY_GATE_BEGIN",
    "F204_MEGA_SOURCE_INVENTORY_GATE_PASS",
    "F204_BANK_SOURCE_PASS",
    "F204_LANDMARK_SOURCE_PASS",
    "F204_MEGA_SOURCE_PASS",
    'if($kind -eq "animated" -and $ext -ne $animatedExt)',
]:
    if symbol not in pg206_runner:
        fail(f"PG-206 F2-04 runner marker missing: {symbol}")

for symbol in [
    "name: F2-04 Road Helm's Deep Prep Maximum Safe Mega Source",
    "cancel-in-progress: false",
    "Build F2-04 Road Helm's Deep Prep maximum-safe source superpack",
]:
    if symbol not in pg206_workflow:
        fail(f"PG-206 F2-04 workflow marker missing: {symbol}")

for ignored in [
    "Data/F204RoadHelmsDeepPrepMaximumSafeMegaSourceV1.json",
    "Scripts/run_f204_road_helms_deep_prep_maximum_safe_source.ps1",
    ".github/workflows/f204-road-helms-deep-prep-maximum-safe-source.yml",
]:
    if pg206_unreal.count(ignored) < 2:
        fail(f"PG-206 F2-04 tooling path must stay off Unreal push+PR filters: {ignored}")



# PG-207: the persistent runner/Warehouse authority lives on D after the 2026-09-29 migration.
pg207_forbidden_runner_root = "C:\\actions-runner"
pg207_real_legacy_fixture = ROOT / "Scripts" / "test_warehouse_inventory_receipt_supersession.ps1"
pg207_real_legacy_fixture_line = '$oldPathVariant = "C:\\actions-runner\\_warehouse\\ShireJourney\\ambientCG\\PLASTER\\Plaster007_2K-PNG.zip"'
pg207_active_files = []
for pg207_pattern in ("*.ps1", "*.cmd"):
    pg207_active_files.extend((ROOT / "Scripts").glob(pg207_pattern))
for pg207_pattern in ("*.yml", "*.yaml"):
    pg207_active_files.extend((ROOT / ".github" / "workflows").glob(pg207_pattern))
for pg207_path in pg207_active_files:
    pg207_text = read(pg207_path)
    pg207_occurrences = pg207_text.count(pg207_forbidden_runner_root)
    if pg207_occurrences == 0:
        continue
    if (
        pg207_path == pg207_real_legacy_fixture
        and pg207_occurrences == 1
        and pg207_real_legacy_fixture_line in pg207_text
    ):
        continue
    fail(f"PG-207 active runner/Warehouse path still targets retired C root: {pg207_path.relative_to(ROOT)}")
for pg207_path, pg207_symbol in [
    (ROOT / "Scripts" / "install_runner_watchdog.ps1", 'D:\\actions-runner'),
    (ROOT / "Scripts" / "runner_watchdog.ps1", 'D:\\actions-runner'),
    (ROOT / "Scripts" / "runner_service_guard.ps1", 'D:\\actions-runner'),
    (ROOT / "Scripts" / "audit_warehouse_inventory.ps1", 'D:\\actions-runner\\_warehouse\\ShireJourney'),
]:
    if pg207_symbol not in read(pg207_path):
        fail(f"PG-207 D-root authority marker missing: {pg207_path.relative_to(ROOT)}")

# PG-208: living-world distance retirement must remain member-local.
pg208_living_cpp = read(resolve_source("LivingWorldDirector.cpp"))
pg208_start = pg208_living_cpp.find("void ALivingWorldDirector::CleanupExpiredEvents()")
pg208_end = pg208_living_cpp.find("FName ALivingWorldDirector::ChooseEventType()", pg208_start)
if pg208_start < 0 or pg208_end < 0:
    fail("PG-208 CleanupExpiredEvents function boundary missing")
else:
    pg208_cleanup = pg208_living_cpp[pg208_start:pg208_end]
    for pg208_symbol in [
        "distance-policy=member-local",
        "Event.Actors.RemoveAtSwap",
        "if (Event.ExpiresAt <= Now)",
        "if (Event.Actors.Num() == 0)",
    ]:
        if pg208_symbol not in pg208_cleanup:
            fail(f"PG-208 member-local event retirement invariant missing: {pg208_symbol}")
    if re.search(r"FVector::DistSquared2D\([^\n]+\)[\s\S]{0,260}?bExpired\s*=\s*true", pg208_cleanup):
        fail("PG-208 distance culling may not expire an entire micro-event from one far member")

# PG-209: P1C01 mega-build train remains gate-aware and source-grounded.
pg209_plan = json.loads(read(ROOT / "Data" / "P1C01MaximumSafeMegaBuildV1.json"))
if pg209_plan.get("status") != "PREP_ACTIVE_W00_CLOSED_RUNTIME_EXPANSION_GATED_BY_PER_CAR_EXACT_HEAD_UE4":
    fail("PG-209 mega-build status must keep runtime expansion behind per-car exact-head UE4 after W00 machine closure")
pg209_w00 = pg209_plan.get("gate_policy", {}).get("w00_machine_baseline", {})
if pg209_w00.get("exact_head") != "d6ca8aac03f5a1da07609e61e790ddf8faad8eed":
    fail("PG-209 W00 exact-head machine baseline drifted")
if pg209_w00.get("pre_unreal") != "#1435 SUCCESS" or pg209_w00.get("unreal_build") != "#1108 SUCCESS":
    fail("PG-209 W00 inherited machine evidence drifted")
pg209_cars = [row for row in pg209_plan.get("work_cars", []) if isinstance(row, dict)]
if len(pg209_cars) < 12:
    fail("PG-209 mega-build lost required multi-car breadth")
if any(row.get("state") == "ACTIVE" and row.get("id") != "DEFECT_EVENT_MEMBER_CULL" for row in pg209_cars):
    fail("PG-209 runtime feature car activated before W00 opened it")
for pg209_rule in [
    "No parallel AI brain.",
    "No heavy synchronous LoadObject path.",
    "Crowd-scale actors remain pooled.",
    "Heavy assets use soft references and FStreamableManager.",
]:
    if pg209_rule not in set(pg209_plan.get("architecture", {}).get("rules", [])):
        fail(f"PG-209 mega-build architecture guard missing: {pg209_rule}")

# PG-210: ambient player lookup stays centralized behind GetPlayerPawnCached.
pg210_ambient = read(resolve_source("ShireAmbientNPC.cpp"))
if pg210_ambient.count("UGameplayStatics::GetPlayerPawn(") != 1:
    fail("PG-210 ShireAmbientNPC direct GetPlayerPawn count must remain exactly one")
pg210_helper_start = pg210_ambient.find("APawn* AShireAmbientNPC::GetPlayerPawnCached()")
pg210_helper_end = pg210_ambient.find("void AShireAmbientNPC::BeginPlay()", pg210_helper_start)
if pg210_helper_start < 0 or pg210_helper_end < 0 or "UGameplayStatics::GetPlayerPawn(" not in pg210_ambient[pg210_helper_start:pg210_helper_end]:
    fail("PG-210 direct player lookup must remain inside GetPlayerPawnCached")

# PG-211: save-schema migrations may not be invented without recovered history.
pg211_audit = json.loads(read(ROOT / "Data" / "SaveSchemaMigrationAuditV1.json"))
if pg211_audit.get("current_schema_version") != 6:
    fail("PG-211 save-schema audit drifted from current schema version")
if pg211_audit.get("status") != "PARTIAL_HISTORY_RECOVERED_V3_TO_V6_V1_V2_UNDOCUMENTED_DO_NOT_INVENT":
    fail("PG-211 save migration audit must preserve recovered v3-v6 history and unknown v1/v2 boundary")
pg211_transitions = pg211_audit.get("documented_transitions", [])
pg211_versions = [row.get("schema_version") for row in pg211_transitions if isinstance(row, dict)]
if pg211_versions != [3, 4, 5, 6]:
    fail("PG-211 recovered save-schema transition map must remain exactly v3-v6")
pg211_unknown = " ".join(str(x) for x in pg211_audit.get("unknown_boundaries", []))
if "schema versions 1 or 2" not in pg211_unknown or "retroactively labeled schema 1 or 2" not in pg211_unknown:
    fail("PG-211 unknown schema 1/2 boundary must remain explicit")
pg211_player = read(resolve_source("ShirePlayerCharacter.cpp"))
if "Save->SaveSchemaVersion > UShireSaveGame::CurrentSchemaVersion" not in pg211_player:
    fail("PG-211 newer-than-build save rejection missing")

# PG-212: P1C01 source-to-runtime disposition prevents silent omission.
pg212_disposition = json.loads(read(ROOT / "Data" / "P1C01SourceToRuntimeDispositionV1.json"))
if pg212_disposition.get("status") != "PREPARATION_COMPLETE_RUNTIME_CARS_GATED":
    fail("PG-212 P1C01 disposition must remain preparation-only while runtime cars are gated")
pg212_rows = [row for row in pg212_disposition.get("dispositions", []) if isinstance(row, dict)]
for pg212_id in [
    "SHIRE_HOBBITON_WORLD",
    "BAG_END_WORLD",
    "F1_01_PARTY_SETUP",
    "F1_01_FIREWORKS",
    "F1_02_RING_DANGER",
    "F1_03_ROAD_HIDING",
    "F1_03_FERRY_ESCAPE",
    "SHIRE_LIVING_WORLD",
    "SHIRE_AUDIO_IDENTITY",
    "CHECKPOINT_AND_RETRY",
    "DIALOGUE_KNOWLEDGE_AND_CINEMATIC_SKIP",
    "SAFE_OPTIONAL_WINDOW_EXPIRY",
]:
    if pg212_id not in {row.get("id") for row in pg212_rows}:
        fail(f"PG-212 source disposition missing required item: {pg212_id}")
for pg212_row in pg212_rows:
    for pg212_field in ["id", "source", "source_requirement", "state", "next_car"]:
        if not str(pg212_row.get(pg212_field) or "").strip():
            fail(f"PG-212 disposition row missing explicit {pg212_field}: {pg212_row.get('id')}")
    if not isinstance(pg212_row.get("current_runtime"), list):
        fail(f"PG-212 disposition current_runtime must be a list: {pg212_row.get('id')}")



# PG-213: combined P1C01 overnight train/source-disposition contract remains gate-safe.
pg209_max = json.loads(read(ROOT / "Data" / "P1C01MaximumSafeMegaBuildV1.json"))
pg209_train = json.loads(read(ROOT / "Data" / "P1C01OvernightMegaBuildTrainV1.json"))
pg209_disp = json.loads(read(ROOT / "Data" / "P1C01SourceToRuntimeDispositionV1.json"))
if pg209_max.get("status") != "PREP_ACTIVE_W00_CLOSED_RUNTIME_EXPANSION_GATED_BY_PER_CAR_EXACT_HEAD_UE4":
    fail("PG-213 P1C01 maximum-safe build lost per-car exact-head runtime gate")
pg213_w00_cars = [x for x in pg209_train.get("cars", []) if isinstance(x, dict) and x.get("id") == "W00_ACCEPTANCE_CLOSE"]
if len(pg213_w00_cars) != 1 or pg213_w00_cars[0].get("status") != "CLOSED_MACHINE_PROVEN_PR184_EXACT_HEAD":
    fail("PG-213 W00 train car must remain closed on the proven PR #184 machine baseline")
if pg209_train.get("preparation_progress", {}).get("runtime_expansion") != "GATED_BY_RELEVANT_PER_CAR_EXACT_HEAD_UE4":
    fail("PG-213 runtime expansion must remain gated by relevant per-car exact-head UE4 proof")
if pg209_train.get("execution_policy", {}).get("one_approval_many_cars") is not True:
    fail("PG-213 one-approval many-cars contract missing")
if "synchronous heavy asset loads" not in pg209_train.get("execution_policy", {}).get("forbidden", []):
    fail("PG-213 synchronous heavy-load prohibition missing")
if "OBJ for animated production assets" not in pg209_train.get("execution_policy", {}).get("forbidden", []):
    fail("PG-213 animated OBJ prohibition missing")
if "BMP as final production texture" not in pg209_train.get("execution_policy", {}).get("forbidden", []):
    fail("PG-213 BMP final-texture prohibition missing")
if pg209_disp.get("zero_silent_omission_rule", "") == "":
    fail("PG-213 source-to-runtime zero-silent-omission rule missing")
pg209_ids = {str(x.get("id") or "") for x in pg209_max.get("work_cars", []) if isinstance(x, dict)}
for pg209_required in [
    "DEFECT_EVENT_MEMBER_CULL",
    "SAVE_SCHEMA_HISTORY_AUDIT",
    "CANON_ZERO_SILENT_OMISSION",
    "LIVING_SHIRE",
    "CHARACTER_PRESENTATION",
    "AUDIO_SONIC_IDENTITY",
    "QUEST_CINEMATIC_POLISH",
    "TARGET_DEVICE_AND_GATE67",
]:
    if pg209_required not in pg209_ids:
        fail(f"PG-213 P1C01 mega-build car missing: {pg209_required}")


# PG-214: P1C01 Shire world-density car stays bounded, instanced and outside AI/story ownership.
pg214_contract = json.loads(read(ROOT / "Data" / "P1C01ShireWorldDensityCarV1.json"))
if pg214_contract.get("status") != "EXACT_HEAD_MACHINE_GREEN_PR192_PRE1467_UE1140_DEVELOP_PRE1468_UE1141":
    fail("PG-214 density car status drifted")
pg214_budget = pg214_contract.get("budget", {})
if pg214_budget.get("ambient_population_target_p1c01") != 18:
    fail("PG-214 P1C01 ambient population target must remain 18")
if pg214_budget.get("max_cluster_actors") != 5:
    fail("PG-214 density cluster ceiling must remain exactly 5 for this car")
if pg214_budget.get("max_detail_instances") != 70:
    fail("PG-214 density detail-instance ceiling must remain exactly 70 for this car")
pg214_categories = pg214_budget.get("categories", [])
if len(pg214_categories) != 5:
    fail("PG-214 density category breadth must remain exactly 5")
if sum(int(row.get("max_instances", 0)) for row in pg214_categories if isinstance(row, dict)) != 70:
    fail("PG-214 category instance budgets must sum to 70")

pg214_life = json.loads(read(ROOT / "Data" / "WorldLifeSaturationPlan.json"))
if pg214_life.get("baseline_population_targets", {}).get("P1C01") != 18:
    fail("PG-214 WorldLifeSaturationPlan P1C01 population target drifted above/below 18")

pg214_h = read(resolve_source("ShirePrototypeWorldBuilder.h"))
pg214_cpp = read(resolve_source("ShirePrototypeWorldBuilder.cpp"))
pg214_cluster_cpp = read(resolve_source("WorldDetailCluster.cpp"))
if "void SpawnWorldDensityDetailPass();" not in pg214_h:
    fail("PG-214 density pass declaration missing")
pg214_start = pg214_cpp.find("void AShirePrototypeWorldBuilder::SpawnWorldDensityDetailPass()")
pg214_end = pg214_cpp.find("void AShirePrototypeWorldBuilder::SpawnScenicDetailPass()", pg214_start)
if pg214_start < 0 or pg214_end <= pg214_start:
    fail("PG-214 density pass function boundary missing")
    pg214_body = ""
else:
    pg214_body = pg214_cpp[pg214_start:pg214_end]
for pg214_symbol in [
    "AWorldDetailCluster",
    "ProductionCommonWoodPileMesh",
    "ProductionCommonFernClumpMesh",
    "ProductionCommonReedClusterMesh",
    "ProductionCommonPathMarkerMesh",
    "ProductionCommonFallenLogMesh",
    "SHIRE_WORLD_DENSITY_DETAIL_PASS",
    "populationTarget=18",
    "Cluster->Configure(Mesh, false",
]:
    if pg214_symbol not in pg214_body:
        fail(f"PG-214 density implementation marker missing: {pg214_symbol}")
if pg214_body.count("SpawnDetailCluster(") != 5:
    fail("PG-214 density pass must keep exactly five bounded cluster admissions")
for pg214_forbidden in [
    "LoadObject<",
    "StaticLoadObject",
    "RequestSyncLoad",
    "SpawnActor<AShireAmbientNPC>",
]:
    if pg214_forbidden in pg214_body:
        fail(f"PG-214 forbidden density implementation path returned: {pg214_forbidden}")
if pg214_cpp.count("SpawnWorldDensityDetailPass();") != 1:
    fail("PG-214 density pass must be invoked exactly once by the Shire world builder")
if "PrimaryActorTick.bCanEverTick = false;" not in pg214_cluster_cpp:
    fail("PG-214 WorldDetailCluster must remain zero-Tick")
if "Instances->SetCollisionEnabled(ECollisionEnabled::NoCollision);" not in pg214_cluster_cpp:
    fail("PG-214 WorldDetailCluster default no-collision boundary missing")


if errors:
    print(f"PRE-UNREAL VALIDATION FAILED: {len(errors)} error(s)")
    for message in errors:
        print(f"ERROR: {message}")
    sys.exit(1)


# PG-175: Unreal CI latency architecture must preserve exact-head safety without
# rebuilding superseded/admin-only commits or destroying incremental Git state.
pg175_workflow = read(ROOT / ".github" / "workflows" / "unreal-build-validation.yml")
pg175_classifier = read(ROOT / "Scripts" / "classify_unreal_validation.ps1")
pg175_latency = read(ROOT / "Docs" / "CI_LATENCY_REVIEW_2026-09-26.md")

for pg175_required in [
    "cancel-in-progress: ${{ github.event_name == 'pull_request' }}",
    "http.lowSpeedLimit=1000",
    "http.lowSpeedTime=20",
    "Fetching exact PR head attempt %%ATTEMPT%% of 3",
    "Scrub checkout credential from persistent Git metadata",
]:
    if pg175_required not in pg175_workflow:
        fail(f"PG-175 Unreal workflow latency/safety invariant missing: {pg175_required}")

for pg175_forbidden in [
    'if exist ".git" rmdir /S /Q ".git"',
    "attempt %%ATTEMPT%% of 7",
]:
    if pg175_forbidden in pg175_workflow:
        fail(f"PG-175 obsolete destructive/retry behavior returned: {pg175_forbidden}")

for pg175_ignored in [
    "'README.md'",
    "'Scripts/new_developer_onboarding.ps1'",
    "'Scripts/governor_handoff.py'",
    "'Scripts/test_governor_handoff.py'",
    "'Scripts/test_unreal_classifier.ps1'",
]:
    if pg175_workflow.count(pg175_ignored) < 2:
        fail(f"PG-175 administrative path is not excluded from both push and PR Unreal triggers: {pg175_ignored}")

for pg175_tree_marker in [
    "function Test-TreeEquivalentCoreProof",
    "TREE_EQUIVALENT_CORE_PROOF_PASS",
    'rev-parse "$ParentSha^{tree}"',
    'rev-parse "$candidate^{tree}"',
]:
    if pg175_tree_marker not in pg175_classifier:
        fail(f"PG-175 exact tree-equivalent proof guard missing: {pg175_tree_marker}")

if "same Git tree" not in pg175_latency and "tree" not in pg175_latency.lower():
    fail("PG-175 CI latency review must explain exact tree-equivalent proof reuse")


print("PRE-UNREAL CORE VALIDATION PASSED")

# PG-050: mass world dressing must remain deterministic, source-controlled and story-safe.
world_dressing_plan_path = ROOT / "Data" / "WorldDressingPlan.json"
if not world_dressing_plan_path.exists():
    fail("PG-050 world dressing plan missing")
else:
    try:
        world_dressing_plan = json.loads(read(world_dressing_plan_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-050 invalid WorldDressingPlan.json: {exc}")
        world_dressing_plan = {}

common_dressing_assets = [
    "SM_CommonPineTree.obj",
    "SM_CommonBroadleafTree.obj",
    "SM_CommonGoldenTree.obj",
    "SM_CommonFallenLog.obj",
    "SM_CommonDryStoneWall.obj",
    "SM_CommonPathMarker.obj",
    "SM_CommonVillageFence.obj",
    "SM_CommonWoodPile.obj",
    "SM_CommonFernClump.obj",
    "SM_CommonReedCluster.obj",
    "SM_CommonRuinSlab.obj",
    "SM_CommonFootbridge.obj",
]
common_dressing_root = ROOT / "SourceAssets" / "Production" / "World" / "Common"
for asset_name in common_dressing_assets:
    if not (common_dressing_root / asset_name).exists():
        fail(f"PG-050 common world dressing asset missing: {asset_name}")

world_builder_h = read(resolve_source("FellowshipChapterWorldBuilder.h"))
world_builder_cpp = read(resolve_source("FellowshipChapterWorldBuilder.cpp"))
for symbol in [
    "CommonPineTreeMesh",
    "CommonBroadleafTreeMesh",
    "CommonGoldenTreeMesh",
    "CommonFallenLogMesh",
    "CommonDryStoneWallMesh",
    "CommonPathMarkerMesh",
    "CommonFernClumpMesh",
    "CommonReedClusterMesh",
    "CommonRuinSlabMesh",
    "CommonFootbridgeMesh",
    "SpawnScatter",
]:
    if symbol not in (world_builder_h + world_builder_cpp):
        fail(f"PG-050 world dressing runtime symbol missing: {symbol}")

for chapter_id in ["P1C03", "P1C04", "P1C05", "P1C06", "P1C07", "P1C08"]:
    if f'ChapterId == TEXT("{chapter_id}")' not in world_builder_cpp:
        fail(f"PG-050 chapter dressing branch missing: {chapter_id}")

if world_dressing_plan:
    profiles = world_dressing_plan.get("chapter_profiles", [])
    profile_ids = {str(p.get("chapter") or "") for p in profiles if isinstance(p, dict)}
    for chapter_id in ["P1C01","P1C02","P1C03","P1C04","P1C05","P1C06","P1C07","P1C08"]:
        if chapter_id not in profile_ids:
            fail(f"PG-050 world dressing plan missing chapter profile: {chapter_id}")

# PG-051: character motion + regional atmosphere must stay rig-ready, bounded and topology-safe.
character_motion_plan_path = ROOT / "Data" / "CharacterMotionPlan.json"
chapter_atmosphere_plan_path = ROOT / "Data" / "ChapterAtmospherePlan.json"
for guarded_path, guard_name in [
    (character_motion_plan_path, "CharacterMotionPlan.json"),
    (chapter_atmosphere_plan_path, "ChapterAtmospherePlan.json"),
]:
    if not guarded_path.exists():
        fail(f"PG-051 production plan missing: {guard_name}")
    else:
        try:
            json.loads(read(guarded_path))
        except json.JSONDecodeError as exc:
            fail(f"PG-051 invalid {guard_name}: {exc}")

npc_motion_h = read(resolve_source("ShireNPC.h"))
npc_motion_cpp = read(resolve_source("ShireNPC.cpp"))
character_stream_h = read(resolve_source("ShireChapterAssetStreamingSubsystem.h"))
character_stream_cpp = read(resolve_source("ShireChapterAssetStreamingSubsystem.cpp"))
for symbol in [
    "TryApplyProductionRig",
    "bUsingSkeletalProductionRig",
    "MotionCadenceScale",
    "MotionStrideScale",
    "MotionIdleScale",
    "DialogueGesture",
]:
    if symbol not in (npc_motion_h + npc_motion_cpp):
        fail(f"PG-051 character motion invariant missing: {symbol}")
for symbol in [
    "RequestCharacterRig",
    "ResolveCharacterRig",
    "ABP_%s_Locomotion",
    "FStreamableManager",
]:
    if symbol not in (character_stream_h + character_stream_cpp):
        fail(f"PG-051 async character rig invariant missing: {symbol}")

chapter_world_h = read(resolve_source("FellowshipChapterWorldBuilder.h"))
chapter_world_cpp = read(resolve_source("FellowshipChapterWorldBuilder.cpp"))
for symbol in [
    "ConfigureChapterAtmosphere",
    "ADirectionalLight",
    "ASkyLight",
    "AExponentialHeightFog",
    "RuntimeAtmosphereManaged",
    "SetFogDensity",
    "RecaptureSky",
]:
    if symbol not in (chapter_world_h + chapter_world_cpp):
        fail(f"PG-051 atmosphere invariant missing: {symbol}")

for chapter_id in ["P1C03", "P1C04", "P1C05", "P1C06", "P1C07", "P1C08"]:
    if chapter_world_cpp.count(f'ChapterId == TEXT("{chapter_id}")') < 1:
        fail(f"PG-051 atmosphere/world chapter branch missing: {chapter_id}")

# PG-052: resource saturation must keep all current project-owned families integrated and startup data packaged.
resource_integration_path = ROOT / "Data" / "ResourceIntegrationPlan.json"
resource_integration = {}
if not resource_integration_path.exists():
    fail("PG-052 ResourceIntegrationPlan.json missing")
else:
    try:
        resource_integration = json.loads(read(resource_integration_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-052 invalid ResourceIntegrationPlan.json: {exc}")

shire_h_cp52 = read(resolve_source("ShirePrototypeWorldBuilder.h"))
shire_cpp_cp52 = read(resolve_source("ShirePrototypeWorldBuilder.cpp"))
bree_h_cp52 = read(resolve_source("BreePrototypeWorldBuilder.h"))
bree_cpp_cp52 = read(resolve_source("BreePrototypeWorldBuilder.cpp"))
fellowship_cpp_cp52 = read(resolve_source("FellowshipChapterWorldBuilder.cpp"))
build_cs_cp52 = read(resolve_source("ShireJourney.Build.cs"))
game_mode_cpp_cp52 = read(resolve_source("ShireGameMode.cpp"))
router_cpp_cp52 = read(resolve_source("ChapterWorldRouter.cpp"))
quest_cpp_cp52 = read(resolve_source("ShireQuestSubsystem.cpp"))
unreal_workflow_cp52 = read(ROOT / ".github" / "workflows" / "unreal-build-validation.yml")

for symbol in [
    "ProductionCommonBroadleafTreeMesh",
    "ProductionCommonFallenLogMesh",
    "ProductionCommonVillageFenceMesh",
    "ProductionCommonWoodPileMesh",
    "ProductionCommonFernClumpMesh",
    "ProductionCommonReedClusterMesh",
    "ProductionCommonFootbridgeMesh",
]:
    if symbol not in (shire_h_cp52 + shire_cpp_cp52):
        fail(f"PG-052 Shire shared-resource integration missing: {symbol}")

for symbol in [
    "CommonBroadleafTreeMesh",
    "CommonDryStoneWallMesh",
    "CommonVillageFenceMesh",
    "CommonWoodPileMesh",
    "CommonFernClumpMesh",
]:
    if symbol not in (bree_h_cp52 + bree_cpp_cp52):
        fail(f"PG-052 Bree shared-resource integration missing: {symbol}")

for symbol in [
    "CommonWoodPileMesh",
    "CommonPathMarkerMesh",
    "CommonDryStoneWallMesh",
    "CommonFallenLogMesh",
]:
    if symbol not in fellowship_cpp_cp52:
        fail(f"PG-052 Fellowship shared-resource saturation missing: {symbol}")

for runtime_data in [
    "LivingWorldEventPlan.json",
    "CharacterMotionPlan.json",
    "ChapterAtmospherePlan.json",
    "WorldDressingPlan.json",
    "ResourceIntegrationPlan.json",
]:
    if runtime_data not in build_cs_cp52:
        fail(f"PG-052 runtime data is not packaged: {runtime_data}")

for startup_symbol in [
    "SpawnActor<AChapterWorldRouter>",
    "SpawnActor<ALivingWorldDirector>",
    'CurrentChapterId = TEXT("P1C01")',
    'StartQuest(TEXT("ShireArrival"), 0)',
    EVIDENCE_SOURCE_ANCHORS.get("startup.ready", ("", ""))[1],
    EVIDENCE_SOURCE_ANCHORS.get("startup.route_p1c01", ("", ""))[1],
]:
    if startup_symbol not in (game_mode_cpp_cp52 + router_cpp_cp52 + quest_cpp_cp52):
        fail(f"PG-052 playable startup invariant missing: {startup_symbol}")

for workflow_symbol in [
    "pull_request:",
    "Headless playable startup smoke",
    "ci_runtime_startup.cmd",
    "ci_runtime_chapters.cmd",
    "ci_runtime_state.cmd",
]:
    if workflow_symbol not in unreal_workflow_cp52:
        fail(f"PG-052 Unreal boot validation workflow missing: {workflow_symbol}")

runtime_wrapper_cp52 = "\n".join(
    read(ROOT / "Scripts" / script_name)
    for script_name in ["ci_runtime_startup.cmd", "ci_runtime_chapters.cmd", "ci_runtime_state.cmd"]
)
for runtime_symbol in ["Scripts\\runtime_smoke.py", "--mode startup", "--mode chapters", "--mode state"]:
    if runtime_symbol not in runtime_wrapper_cp52:
        fail(f"PG-052 stable runtime observer wrapper missing: {runtime_symbol}")

# The extracted observer now owns the log name and readiness contract.
runtime_observer_path = ROOT / "Scripts" / "runtime_smoke.py"
if not runtime_observer_path.exists():
    fail("PG-052 runtime observer missing")
else:
    runtime_observer = runtime_observer_path.read_text(encoding="utf-8")
    if "from runtime_audit_contracts import" not in runtime_observer:
        fail("PG-052 runtime observer must consume the central audit registry")
    if "FAILURE.search(final_text)" not in runtime_observer:
        fail("PG-052 runtime observer lost final fatal/assert/ensure scan")
    for startup_evidence in ["startup.ready", "startup.route_p1c01"]:
        if not mode_has_evidence("startup", startup_evidence):
            fail(f"PG-052 central startup evidence missing: {startup_evidence}")

if resource_integration:
    external_policy = resource_integration.get("external_resource_policy", {})
    if external_policy.get("current_approved_asset_count") != 0:
        fail("PG-052 external approved count must match current empty ExternalAssetManifest assets list")

# PG-053: Part I must maintain continuous low-cost regional life, not only isolated micro-events.
world_life_plan_path = ROOT / "Data" / "WorldLifeSaturationPlan.json"
world_life_plan = {}
if not world_life_plan_path.exists():
    fail("PG-053 WorldLifeSaturationPlan.json missing")
else:
    try:
        world_life_plan = json.loads(read(world_life_plan_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-053 invalid WorldLifeSaturationPlan.json: {exc}")

living_world_h = read(resolve_source("LivingWorldDirector.h"))
living_world_cpp = read(resolve_source("LivingWorldDirector.cpp"))
ambient_cpp = read(resolve_source("ShireAmbientNPC.cpp"))

for symbol in [
    "BaselinePopulation",
    "BaselineTargetByChapter",
    "BaselineRolesByChapter",
    "LoadLifeSaturationContract",
    "MaintainBaselinePopulation",
    "CleanupBaselinePopulation",
    "ChooseBaselineRole",
    "ChooseBaselineProp",
    "ChoosePopulationOrigin",
    "LivingWorldBaseline",
]:
    if symbol not in (living_world_h + living_world_cpp):
        fail(f"PG-053 continuous-life runtime symbol missing: {symbol}")

for symbol in [
    "UpdateSocialLife",
    "UpdateScheduleContext",
    "UpdateAwareness",
    "ResolveAmbientConversationLine",
]:
    if symbol not in ambient_cpp:
        fail(f"PG-053 ambient social-life behavior missing: {symbol}")

if "WorldLifeSaturationPlan.json" not in build_cs_cp52:
    fail("PG-053 world-life saturation plan is not packaged")

if world_life_plan:
    targets = world_life_plan.get("baseline_population_targets", {})
    roles = world_life_plan.get("population_roles", {})
    for chapter_id in ["P1C01","P1C02","P1C03","P1C04","P1C05","P1C06","P1C07","P1C08"]:
        if chapter_id not in targets:
            fail(f"PG-053 baseline population target missing: {chapter_id}")
        if chapter_id not in roles:
            fail(f"PG-053 population role mix missing: {chapter_id}")
    if int(targets.get("P1C01", 0)) < 12:
        fail("PG-053 Shire baseline population is below the dense-world floor")
    if int(targets.get("P1C02", 0)) < 10:
        fail("PG-053 Bree baseline population is below the dense-world floor")
    if int(targets.get("P1C06", -1)) != 0:
        fail("PG-053 Moria must remain civilian-empty")

world_resource_flood_path = ROOT / "Data" / "WorldResourceFloodPlan.json"
if not world_resource_flood_path.exists():
    fail("PG-053 WorldResourceFloodPlan.json missing")
else:
    try:
        world_resource_flood = json.loads(read(world_resource_flood_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-053 invalid WorldResourceFloodPlan.json: {exc}")
        world_resource_flood = {}

resource_flood_assets = [
    "SM_CommonBarrel.obj",
    "SM_CommonCargoCrate.obj",
    "SM_CommonSackBale.obj",
    "SM_CommonLongBench.obj",
    "SM_CommonHayBale.obj",
    "SM_CommonCampTent.obj",
    "SM_CommonStoneArch.obj",
    "SM_CommonBrokenColumn.obj",
    "SM_CommonBrazier.obj",
    "SM_CommonRopePost.obj",
    "SM_CommonMarketCanopy.obj",
    "SM_CommonRiverBoat.obj",
    "SM_CommonCairn.obj",
    "SM_CommonTreeStump.obj",
    "SM_CommonMushroomCluster.obj",
]
for asset_name in resource_flood_assets:
    if not (common_dressing_root / asset_name).exists():
        fail(f"PG-053 resource flood asset missing: {asset_name}")

for runtime_symbol in [
    "SM_CommonBarrel",
    "SM_CommonCargoCrate",
    "SM_CommonCampTent",
    "SM_CommonStoneArch",
    "SM_CommonRiverBoat",
    "SM_CommonMushroomCluster",
]:
    if runtime_symbol not in (shire_cpp_cp52 + bree_cpp_cp52 + fellowship_cpp_cp52):
        fail(f"PG-053 resource flood runtime reference missing: {runtime_symbol}")

if "WorldResourceFloodPlan.json" not in build_cs_cp52:
    fail("PG-053 world resource flood plan is not packaged")

# PG-054 mega resource bank: large source-controlled inventory must exist before activity/movement builds on it.
cp54_plan_path = ROOT / "Data" / "WorldResourceBankCP54.json"
if not cp54_plan_path.exists():
    fail("PG-054 WorldResourceBankCP54.json missing")
else:
    try:
        cp54_plan = json.loads(read(cp54_plan_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-054 invalid WorldResourceBankCP54.json: {exc}")

cp54_regions = ["Common","Shire","Bree","Weathertop","Road","Rivendell","Moria","Lothlorien","Anduin"]
cp54_asset_files = []
for region in cp54_regions:
    region_root = ROOT / "SourceAssets" / "Production" / "World" / region
    if not region_root.exists():
        fail(f"PG-054 production region missing: {region}")
        continue
    cp54_asset_files.extend(region_root.glob("*.obj"))
if len(cp54_asset_files) < 75:
    fail(f"PG-054 mega resource bank below 75 OBJ floor: {len(cp54_asset_files)}")

cp54_texture_root = ROOT / "SourceAssets" / "Production" / "Textures"
cp54_textures = (
    list(cp54_texture_root.glob("*.png")) +
    list(cp54_texture_root.glob("*.tga"))
) if cp54_texture_root.exists() else []
if len(cp54_textures) < 17:
    fail(f"PG-054 production texture bank below 17 PNG/TGA floor: {len(cp54_textures)}")

for runtime_symbol in ["SM_ShFarmPlough","SM_BreeStreetAwning","SM_WeathertopRuinWall","SM_RoadTravelTent","SM_RivColumn","SM_MoriaMineCart","SM_LorienTreePlatform","SM_AnduinDockPier"]:
    if runtime_symbol not in (shire_cpp_cp52 + bree_cpp_cp52 + fellowship_cpp_cp52):
        fail(f"PG-054 runtime resource integration missing: {runtime_symbol}")
if "WorldResourceBankCP54.json" not in build_cs_cp52:
    fail("PG-054 mega resource bank plan is not packaged")

# PG-055: post-verification activity/movement expansion must stay bounded, source-controlled and story-safe.
cp55_plan_path = ROOT / "Data" / "WorldActivityMovementPlan.json"
cp55_plan = {}
if not cp55_plan_path.exists():
    fail("PG-055 WorldActivityMovementPlan.json missing")
else:
    try:
        cp55_plan = json.loads(read(cp55_plan_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-055 invalid WorldActivityMovementPlan.json: {exc}")

cp55_required_assets = [
    ROOT / "SourceAssets" / "Production" / "World" / "Common" / "SM_CommonBird.obj",
    ROOT / "SourceAssets" / "Production" / "World" / "Common" / "SM_CommonRabbit.obj",
    ROOT / "SourceAssets" / "Production" / "World" / "Common" / "SM_CommonButterfly.obj",
]
for asset_path in cp55_required_assets:
    if not asset_path.exists():
        fail(f"PG-055 required fauna asset missing: {asset_path.relative_to(ROOT).as_posix()}")

cp55_ambient_cpp = read(resolve_source("ShireAmbientNPC.cpp"))
cp55_director_cpp = read(resolve_source("LivingWorldDirector.cpp"))
for role in ['TEXT("Bird")', 'TEXT("Rabbit")', 'TEXT("Butterfly")']:
    if role not in cp55_ambient_cpp:
        fail(f"PG-055 ambient movement role missing: {role}")
    if role not in cp55_director_cpp:
        fail(f"PG-055 LivingWorldDirector fauna spawn missing: {role}")

for asset_name in ["SM_CommonBird", "SM_CommonRabbit", "SM_CommonButterfly"]:
    if asset_name not in cp55_ambient_cpp:
        fail(f"PG-055 production fauna mesh preference missing: {asset_name}")

cp55_event_plan_path = ROOT / "Data" / "LivingWorldEventPlan.json"
if cp55_event_plan_path.exists():
    try:
        cp55_event_plan = json.loads(read(cp55_event_plan_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-055 invalid LivingWorldEventPlan.json: {exc}")
        cp55_event_plan = {}
    cp55_templates = {
        str(item.get("id") or "")
        for item in cp55_event_plan.get("event_templates", [])
        if isinstance(item, dict)
    }
    for template_id in ["EVT_FAUNA_BIRDS", "EVT_FAUNA_SMALL_ANIMAL", "EVT_FAUNA_BUTTERFLIES"]:
        if template_id not in cp55_templates:
            fail(f"PG-055 fauna event template missing: {template_id}")
else:
    fail("PG-055 LivingWorldEventPlan.json missing")

# PG-058: CP56 film-spine experiential enrichment must remain canon-safe, optional and runtime-wired.
cp56_plan_path = ROOT / "Data" / "FellowshipExperienceMegaPassCP56.json"
cp56_plan = {}
if not cp56_plan_path.exists():
    fail("PG-058 FellowshipExperienceMegaPassCP56.json missing")
else:
    try:
        cp56_plan = json.loads(read(cp56_plan_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-058 invalid FellowshipExperienceMegaPassCP56.json: {exc}")

if cp56_plan:
    if cp56_plan.get("status") not in {"IMPLEMENTATION_IN_PROGRESS", "IMPLEMENTED_PENDING_VALIDATION", "VALIDATED"}:
        fail("PG-058 CP56 plan has invalid status")
    if len(cp56_plan.get("chapters", [])) != 8:
        fail("PG-058 CP56 must retain exactly eight Part I chapter entries")
    canon_policy = cp56_plan.get("canon_policy", {})
    if canon_policy.get("primary_reference") != "Peter Jackson film continuity":
        fail("PG-058 CP56 film-continuity spine changed")
    if "do not reproduce screenplay dialogue" not in str(canon_policy.get("dialogue_policy", "")).lower():
        fail("PG-058 CP56 dialogue policy must reject screenplay reproduction")

cp56_film_plan_path = ROOT / "Data" / "FilmExperiencePlan.json"
if not cp56_film_plan_path.exists():
    fail("PG-058 FilmExperiencePlan.json missing")
else:
    try:
        cp56_film_plan = json.loads(read(cp56_film_plan_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-058 invalid FilmExperiencePlan.json: {exc}")
        cp56_film_plan = {}
    cp56_anchor_ids = {
        str(anchor.get("id") or "")
        for chapter in cp56_film_plan.get("chapters", [])
        if isinstance(chapter, dict)
        for anchor in chapter.get("anchors", [])
        if isinstance(anchor, dict)
    }
    for anchor_id in ["P1C01_SHIRE_LIFE", "P1C01_PARTY", "P1C05_COMPANIONSHIP"]:
        if anchor_id not in cp56_anchor_ids:
            fail(f"PG-058 film-experience anchor missing: {anchor_id}")

cp56_shire_cpp = read(resolve_source("ShirePrototypeWorldBuilder.cpp"))
cp56_ambient_cpp = read(resolve_source("ShireAmbientNPC.cpp"))
cp56_bree_cpp = read(resolve_source("BreePrototypeWorldBuilder.cpp"))
cp56_fellowship_cpp = read(resolve_source("FellowshipChapterWorldBuilder.cpp"))
for runtime_symbol in [
    "Side_GreenDragonRevelry",
    "Side_PartyMischief",
    "Side_SharedShireMemory",
    'TEXT("PlayRunner")',
    "Side_BreeCommonRoomLife",
    "RoadCompanionship",
    "FellowshipCompanionship",
    "MoriaDeadCityDiscovery",
    "LorienSharedGrief",
    "AnduinCampTension",
]:
    if runtime_symbol not in (cp56_shire_cpp + cp56_ambient_cpp + cp56_bree_cpp + cp56_fellowship_cpp):
        fail(f"PG-058 CP56 runtime enrichment missing: {runtime_symbol}")

if "FellowshipExperienceMegaPassCP56.json" not in build_cs_cp52:
    fail("PG-058 CP56 experience plan is not packaged")
if "WorldActivityMovementPlan.json" not in build_cs_cp52:
    fail("PG-058 CP55 activity plan lost from runtime packaging")

# PG-059: living-NPC intelligence must remain bounded, packaged and story-safe.
living_npc_plan_path = ROOT / "Data" / "LivingNPCIntelligencePlan.json"
living_npc_plan = {}
if not living_npc_plan_path.exists():
    fail("PG-059 LivingNPCIntelligencePlan.json missing")
else:
    try:
        living_npc_plan = json.loads(read(living_npc_plan_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-059 invalid LivingNPCIntelligencePlan.json: {exc}")

if living_npc_plan:
    offline_policy = living_npc_plan.get("offline_runtime_policy", {})
    if offline_policy.get("mode") != "OFFLINE_ONLY":
        fail("PG-059 living-NPC runtime policy must remain OFFLINE_ONLY")
    if offline_policy.get("network_required") is not False:
        fail("PG-059 living-NPC runtime must not require network access")
    if offline_policy.get("remote_llm_allowed") is not False:
        fail("PG-059 remote/cloud LLM runtime must remain disabled")
    if offline_policy.get("cloud_api_dependency_allowed") is not False:
        fail("PG-059 cloud API gameplay dependency must remain disabled")
    if living_npc_plan.get("character_knowledge_policy", {}).get("default") != "DENY_UNLISTED":
        fail("PG-059 character knowledge default must remain DENY_UNLISTED")

ambient_header_pg59 = read(resolve_source("ShireAmbientNPC.h"))
ambient_cpp_pg59 = read(resolve_source("ShireAmbientNPC.cpp"))
for symbol in ["Hunger01", "Fatigue01", "SocialNeed01", "Fear01", "RuntimeEmotion", "RuntimeGoal", "UpdateNeedsAndEmotion"]:
    if symbol not in (ambient_header_pg59 + ambient_cpp_pg59):
        fail(f"PG-059 living-NPC runtime symbol missing: {symbol}")

social_model_pg59 = {}
try:
    social_model_pg59 = json.loads(read(ROOT / "Data" / "NPCSocialModel.json"))
except json.JSONDecodeError as exc:
    fail(f"PG-059 invalid NPCSocialModel.json: {exc}")

profiles_pg59 = {
    str(item.get("id") or ""): item
    for item in social_model_pg59.get("profiles", [])
    if isinstance(item, dict)
}
for profile_id in ["NPC_GANDALF", "NPC_SAM", "NPC_ARAGORN", "NPC_BILBO"]:
    profile = profiles_pg59.get(profile_id)
    if not profile:
        fail(f"PG-059 required core living-NPC profile missing: {profile_id}")
        continue
    if not profile.get("biography_facts"):
        fail(f"PG-059 biography facts missing for core profile: {profile_id}")
    if not profile.get("knowledge_limits"):
        fail(f"PG-059 knowledge limits missing for core profile: {profile_id}")
    if not profile.get("attitude_tags"):
        fail(f"PG-059 attitude tags missing for core profile: {profile_id}")

npc_context_header_pg59 = read(resolve_source("ShireNPCContextSubsystem.h"))
npc_context_cpp_pg59 = read(resolve_source("ShireNPCContextSubsystem.cpp"))
for symbol in ["BiographyFacts", "KnowledgeLimits", "AttitudeTags", "GetProfileContextSummary"]:
    if symbol not in (npc_context_header_pg59 + npc_context_cpp_pg59):
        fail(f"PG-059 named profile runtime context missing: {symbol}")

if "LivingNPCIntelligencePlan.json" not in build_cs_cp52:
    fail("PG-059 living-NPC intelligence plan is not packaged")

# PG-060: whole-game mega integration must remain explicit and coherent.
mega_plan_path = ROOT / "Data" / "CP56MegaIntegrationPlan.json"
completeness_path = ROOT / "Data" / "GameCompletenessMatrix.json"
for path, label in [
    (mega_plan_path, "CP56MegaIntegrationPlan.json"),
    (completeness_path, "GameCompletenessMatrix.json"),
]:
    if not path.exists():
        fail(f"PG-060 {label} missing")
    else:
        try:
            json.loads(read(path))
        except json.JSONDecodeError as exc:
            fail(f"PG-060 invalid {label}: {exc}")

if completeness_path.exists():
    try:
        completeness_pg60 = json.loads(read(completeness_path))
    except json.JSONDecodeError:
        completeness_pg60 = {}
    required_systems_pg60 = {
        "PLAYER_MOVEMENT", "CAMERA", "INTERACTION", "COMBAT", "COMPANIONS",
        "NAMED_CHARACTER_INTELLIGENCE", "AMBIENT_NPC_INTELLIGENCE", "DIALOGUE",
        "OFFLINE_AI", "WORLD_LIFE", "WORLD_GEOGRAPHY", "ATMOSPHERE",
        "EXPLORATION", "STORY", "SAVE_LOAD", "AUDIO", "CHARACTER_MOTION",
        "UI_HUD", "PERFORMANCE", "QA_AUTOMATION", "CINEMATIC_PRESENTATION",
        "ASSET_PRODUCTION", "HANDOFF_GOVERNANCE",
    }
    actual_systems_pg60 = {
        str(item.get("id") or "")
        for item in completeness_pg60.get("systems", [])
        if isinstance(item, dict)
    }
    missing_systems_pg60 = sorted(required_systems_pg60 - actual_systems_pg60)
    if missing_systems_pg60:
        fail("PG-060 completeness matrix missing systems: " + ", ".join(missing_systems_pg60))

npc_h_pg60 = read(resolve_source("ShireNPC.h"))
npc_cpp_pg60 = read(resolve_source("ShireNPC.cpp"))
ctx_h_pg60 = read(resolve_source("ShireNPCContextSubsystem.h"))
ctx_cpp_pg60 = read(resolve_source("ShireNPCContextSubsystem.cpp"))

for symbol in ["CachedWorldPressure", "CachedWorldMood", "CachedEmotionalState", "RefreshLivingContext"]:
    if symbol not in (npc_h_pg60 + npc_cpp_pg60):
        fail(f"PG-060 companion living-context symbol missing: {symbol}")

for symbol in ["GetProfileEmotionalState", "WorldMood", "EmotionalState"]:
    if symbol not in (ctx_h_pg60 + ctx_cpp_pg60):
        fail(f"PG-060 named-character context symbol missing: {symbol}")

for mood in [
    "PEACEFUL_HOME", "SUSPICIOUS_TOWN", "PURSUED_WILDERNESS", "SAFE_REFUGE",
    "FELLOWSHIP_UNDER_PRESSURE", "DEAD_CITY_DREAD", "GRIEF_AND_REFUGE",
    "FELLOWSHIP_FRACTURE", "WAR_CORRUPTION",
]:
    if mood not in ctx_cpp_pg60:
        fail(f"PG-060 regional dialogue/context missing mood: {mood}")

if '? TEXT("Mug") : NAME_None' in read(resolve_source("ShirePrototypeWorldBuilder.cpp")):
    fail("PG-060 Shire crowd prop ternary regressed to UE4-incompatible mixed FName/string types")
if '? TEXT("Mug") : NAME_None' in read(resolve_source("BreePrototypeWorldBuilder.cpp")):
    fail("PG-060 Bree crowd prop ternary regressed to UE4-incompatible mixed FName/string types")


# PG-081: contextual side activities are fail-closed runtime contracts.
pg81_side_path = ROOT / "Data" / "ContextualSideActivityPlan.json"
pg81_journey_path = ROOT / "Data" / "JourneyDiscoveryRewardPlan.json"
pg81_allowed_types = {
    "TRAVERSAL_CHALLENGE", "OBSERVATION_CHALLENGE", "TRACKING_CHALLENGE",
    "PATTERN_MATCH", "CAMP_PREPARATION", "SOCIAL_MEMORY", "STEALTH_LITE",
    "TIMING_CHALLENGE", "ROUTE_READING",
}
try:
    pg81_side = json.loads(read(pg81_side_path))
    pg81_journey = json.loads(read(pg81_journey_path))
except json.JSONDecodeError as exc:
    fail(f"PG-081 invalid side/discovery JSON: {exc}")
    pg81_side, pg81_journey = {}, {}

pg81_discoveries = {
    str(item.get("discovery_id") or ""): item
    for item in pg81_journey.get("discovery_rewards", [])
    if isinstance(item, dict)
}
pg81_activity_ids, pg81_reward_ids = set(), set()
pg81_count = 0
for pg81_chapter in pg81_side.get("chapters", []):
    if not isinstance(pg81_chapter, dict):
        fail("PG-081 non-object chapter entry")
        continue
    pg81_route = str(pg81_chapter.get("route") or "")
    pg81_chapter_id = str(pg81_chapter.get("chapter") or "")
    if not pg81_route or not pg81_chapter_id:
        fail("PG-081 side-activity chapter missing route/chapter")
        continue
    for pg81_activity in pg81_chapter.get("activities", []):
        if not isinstance(pg81_activity, dict):
            fail(f"PG-081 non-object activity in {pg81_route}/{pg81_chapter_id}")
            continue
        pg81_count += 1
        pg81_id = str(pg81_activity.get("id") or "")
        pg81_type = str(pg81_activity.get("type") or "")
        pg81_reward = str(pg81_activity.get("discovery_reward_id") or "")
        pg81_after = str(pg81_activity.get("available_after") or "")
        pg81_before = str(pg81_activity.get("ends_before") or "")
        if not all([pg81_id, pg81_reward, pg81_after, pg81_before]):
            fail(f"PG-081 incomplete side-activity contract in {pg81_route}/{pg81_chapter_id}")
        if pg81_type not in pg81_allowed_types:
            fail(f"PG-081 unsupported activity type {pg81_type}: {pg81_id}")
        if pg81_id in pg81_activity_ids:
            fail(f"PG-081 duplicate side-activity id: {pg81_id}")
        if pg81_reward in pg81_reward_ids:
            fail(f"PG-081 duplicate side-activity reward id: {pg81_reward}")
        pg81_activity_ids.add(pg81_id)
        pg81_reward_ids.add(pg81_reward)
        if pg81_activity.get("may_advance_required_anchor") is not False:
            fail(f"PG-081 side activity may advance required anchor: {pg81_id}")
        if pg81_activity.get("may_change_canon_outcome") is not False:
            fail(f"PG-081 side activity may change canon outcome: {pg81_id}")
        if pg81_activity.get("future_knowledge_allowed") is not False:
            fail(f"PG-081 future knowledge allowed in side activity: {pg81_id}")
        pg81_discovery = pg81_discoveries.get(pg81_reward)
        if not pg81_discovery:
            fail(f"PG-081 reward missing from JourneyDiscoveryRewardPlan: {pg81_reward}")
        else:
            if str(pg81_discovery.get("route") or "") != pg81_route:
                fail(f"PG-081 reward route mismatch: {pg81_id}")
            if str(pg81_discovery.get("chapter") or "") != pg81_chapter_id:
                fail(f"PG-081 reward chapter mismatch: {pg81_id}")

if pg81_count < 19:
    fail(f"PG-081 contextual side-activity coverage regressed below 19: {pg81_count}")

pg81_qh = read(resolve_source("ShireQuestSubsystem.h"))
pg81_qc = read(resolve_source("ShireQuestSubsystem.cpp"))
pg81_tc = read(resolve_source("ShireTraversalChallenge.cpp"))
for pg81_symbol in [
    "AvailableAfterStoryBeat", "EndsBeforeStoryBeat", "SideActivityDefinitionsById",
    "HasSideActivityForDiscovery", "IsSideActivityAvailable",
    "IsSideActivityDiscoveryAvailable", "GetSideActivityIdForDiscovery",
    "IsSideActivityDefinitionAvailable",
]:
    if pg81_symbol not in (pg81_qh + pg81_qc):
        fail(f"PG-081 side-activity runtime window symbol missing: {pg81_symbol}")
if "IsSideActivityDiscoveryAvailable(DiscoveryId)" not in pg81_tc:
    fail("PG-081 traversal challenge bypasses central side-activity window guard")


# PG-082: QUIET_STEP must have at least one authored physical STEALTH_LITE source.
try:
    pg82_side = json.loads(read(ROOT / "Data" / "ContextualSideActivityPlan.json"))
    pg82_journey = json.loads(read(ROOT / "Data" / "JourneyDiscoveryRewardPlan.json"))
except json.JSONDecodeError as exc:
    fail(f"PG-082 invalid side/discovery JSON: {exc}")
    pg82_side, pg82_journey = {}, {}

pg82_stealth = [
    activity
    for chapter in pg82_side.get("chapters", [])
    if isinstance(chapter, dict)
    for activity in chapter.get("activities", [])
    if isinstance(activity, dict) and activity.get("type") == "STEALTH_LITE"
]
if not pg82_stealth:
    fail("PG-082 no authored STEALTH_LITE side activity exists")

pg82_rewards = {
    str(item.get("discovery_id") or "")
    for item in pg82_journey.get("discovery_rewards", [])
    if isinstance(item, dict)
}
for pg82_activity in pg82_stealth:
    pg82_reward = str(pg82_activity.get("discovery_reward_id") or "")
    if not pg82_reward or pg82_reward not in pg82_rewards:
        fail(f"PG-082 stealth reward missing from JourneyDiscoveryRewardPlan: {pg82_reward}")

pg82_shire = read(resolve_source("ShirePrototypeWorldBuilder.cpp"))
pg82_traversal = read(resolve_source("ShireTraversalChallenge.cpp"))
pg82_player_h = read(resolve_source("ShirePlayerCharacter.h"))
for pg82_symbol in [
    "SHIRE_QUIET_FEET",
    'TEXT("STEALTH_LITE")',
    "IsCrouchingForStealth",
    "CompleteSideActivityDiscovery",
]:
    if pg82_symbol not in (pg82_shire + pg82_traversal + pg82_player_h):
        fail(f"PG-082 stealth runtime symbol missing: {pg82_symbol}")


# PG-083: PATTERN_MATCH side play must have a real interactable environmental puzzle runtime.
pg83_h = read(resolve_source("ShireEnvironmentalPuzzle.h"))
pg83_cpp = read(resolve_source("ShireEnvironmentalPuzzle.cpp"))
pg83_builder = read(resolve_source("FellowshipChapterWorldBuilder.cpp"))
for pg83_symbol in [
    "IShireInteractable",
    "ConfigurePuzzle",
    "Interact_Implementation",
    "CompleteSideActivityDiscovery",
    "EnvironmentalPuzzle: PASS",
]:
    if pg83_symbol not in (pg83_h + pg83_cpp):
        fail(f"PG-083 environmental puzzle runtime symbol missing: {pg83_symbol}")
for pg83_marker in [
    "AShireEnvironmentalPuzzle* RivendellMapTable",
    'TEXT("RIVENDELL_LIBRARY")',
    "AShireEnvironmentalPuzzle* MoriaReliefStudy",
    'TEXT("MORIA_DWARVEN_RELIEF")',
]:
    if pg83_marker not in pg83_builder:
        fail(f"PG-083 environmental puzzle placement missing: {pg83_marker}")


# PG-084: living-world player responses must remain bounded, ephemeral and story-neutral.
pg84_plan = json.loads(read(ROOT / "Data" / "LivingWorldEventPlan.json"))
pg84_policy = pg84_plan.get("player_interaction_policy", {})
pg84_expected_types = {"WORK_ACTIVITY", "TRAVELER_PASSING", "MARKET_ACTIVITY", "SOCIAL_MOMENT"}
if set(pg84_policy.get("enabled_event_types", [])) != pg84_expected_types:
    fail("PG-084 living-world interactive event types changed without contract update")
if pg84_policy.get("persistent_reward") != "NONE" or pg84_policy.get("story_effect") != "NONE":
    fail("PG-084 living-world interactions may not grant persistent rewards or story effects")
if pg84_policy.get("may_advance_required_anchor") is not False:
    fail("PG-084 living-world interactions may not advance required anchors")
if pg84_policy.get("may_change_canon_outcome") is not False:
    fail("PG-084 living-world interactions may not change canon outcomes")

pg84_h = read(resolve_source("ShireWorldEventInteraction.h"))
pg84_cpp = read(resolve_source("ShireWorldEventInteraction.cpp"))
pg84_director_h = read(resolve_source("LivingWorldDirector.h"))
pg84_director_cpp = read(resolve_source("LivingWorldDirector.cpp"))
for pg84_symbol in [
    "IShireInteractable",
    "ConfigureInteraction",
    "Interact_Implementation",
    "WorldEventInteraction: PASS",
    "storyEffect=NONE",
]:
    if pg84_symbol not in (pg84_h + pg84_cpp):
        fail(f"PG-084 living-world interaction runtime symbol missing: {pg84_symbol}")
for pg84_symbol in [
    "SpawnPlayerInteraction",
    "IsStoryDangerActive()",
    "OutEvent.Actors.Add(Interaction)",
]:
    if pg84_symbol not in (pg84_director_h + pg84_director_cpp):
        fail(f"PG-084 living-world director interaction wiring missing: {pg84_symbol}")


# PG-085: dedicated Chronicle browsing must remain source-grounded and explicit.
pg85_rewards = json.loads(read(ROOT / "Data" / "JourneyDiscoveryRewardPlan.json"))
pg85_envelope = json.loads(read(ROOT / "Data" / "ExplorationEnvelopePlan.json"))
pg85_labels = {
    str(item.get("id") or ""): str(item.get("label") or "")
    for chapter in pg85_envelope.get("chapters", [])
    if isinstance(chapter, dict)
    for item in chapter.get("optional_discoveries", [])
    if isinstance(item, dict)
}
for pg85_reward in pg85_rewards.get("discovery_rewards", []):
    if not isinstance(pg85_reward, dict):
        continue
    pg85_id = str(pg85_reward.get("discovery_id") or "")
    pg85_display = str(pg85_reward.get("display_label") or "")
    if not pg85_display:
        fail(f"PG-085 Journey Discovery missing display_label: {pg85_id}")
    if pg85_labels.get(pg85_id) != pg85_display:
        fail(f"PG-085 Chronicle display label drifted from exploration source: {pg85_id}")

pg85_qh = read(resolve_source("ShireQuestSubsystem.h"))
pg85_qc = read(resolve_source("ShireQuestSubsystem.cpp"))
pg85_ph = read(resolve_source("ShirePlayerCharacter.h"))
pg85_pc = read(resolve_source("ShirePlayerCharacter.cpp"))
pg85_hud = read(resolve_source("ShireHUD.cpp"))
pg85_input = read(ROOT / "Config" / "DefaultInput.ini")
for pg85_symbol in [
    "GetChronicleEntryDisplayLabel",
    "GetChronicleEntryContextLabel",
    "GetKnownMapRegionDisplayLabel",
]:
    if pg85_symbol not in (pg85_qh + pg85_qc):
        fail(f"PG-085 Chronicle presentation API missing: {pg85_symbol}")
for pg85_symbol in ["ChronicleBrowseIndex", "ChroniclePrevious", "ChronicleNext"]:
    if pg85_symbol not in (pg85_ph + pg85_pc):
        fail(f"PG-085 Chronicle browse state/input missing: {pg85_symbol}")
for pg85_mapping in ['ActionName="ChroniclePrevious"', 'ActionName="ChronicleNext"']:
    if pg85_mapping not in pg85_input:
        fail(f"PG-085 Chronicle input mapping missing: {pg85_mapping}")
for pg85_marker in ["ENTRY %d / %d", "KNOWN MAP REGIONS", "C Close"]:
    if pg85_marker not in pg85_hud:
        fail(f"PG-085 dedicated Chronicle HUD marker missing: {pg85_marker}")


# PG-086: mega production remains source-grounded and truthfully gated.
pg86_names = ["Part1ProductionAtlas.json", "Production100ReadinessGate.json", "Part1MegaProductionPlan.json"]
pg86_docs = []
for pg86_name in pg86_names:
    pg86_path = ROOT / "Data" / pg86_name
    if not pg86_path.exists():
        fail(f"PG-086 missing mega-production contract: {pg86_name}")
        pg86_docs.append({})
        continue
    try:
        pg86_docs.append(json.loads(read(pg86_path)))
    except json.JSONDecodeError as exc:
        fail(f"PG-086 invalid {pg86_name}: {exc}")
        pg86_docs.append({})
pg86_atlas, pg86_gate, pg86_mega = (pg86_docs + [{}, {}, {}])[:3]
pg86_required = {("FrodoMain", f"P1C0{i}") for i in range(1, 9)} | {("GandalfParallel", "P1C01")}
pg86_actual = {(str(row.get("route") or ""), str(row.get("chapter") or "")) for row in pg86_atlas.get("chapters", []) if isinstance(row, dict)}
if pg86_actual != pg86_required:
    fail("PG-086 Part1ProductionAtlas chapter/route coverage mismatch")
if pg86_gate.get("production_100") is not False:
    fail("PG-086 production_100 may not be promoted before final acceptance")
if pg86_mega.get("status") != "ACTIVE":
    fail("PG-086 Part1MegaProductionPlan must remain ACTIVE")
pg86_sources = json.loads(read(ROOT / "Data" / "OwnerSourceReferenceIndex.json"))
pg86_ids = {str(row.get("id") or "") for row in pg86_sources.get("sources", []) if isinstance(row, dict)}
for pg86_id in ["SRC_FILM_FOTR_SCREENPLAY","SRC_OWNER_MASTER_PACK","SRC_OWNER_PROJECT_SOURCE_PACK","SRC_OWNER_BATTLES_WEAPONS_ARMIES_BIBLE","SRC_OWNER_SIDE_ACTIVITIES_BIBLE"]:
    if pg86_id not in pg86_ids:
        fail(f"PG-086 owner source index missing {pg86_id}")
pg86_chars = json.loads(read(ROOT / "Data" / "CharacterProductionMatrix.json"))
pg86_world = json.loads(read(ROOT / "Data" / "CinematicWorldProductionMatrix.json"))
if pg86_chars.get("source_atlas") != "Data/Part1ProductionAtlas.json":
    fail("PG-086 character matrix not linked to Part1ProductionAtlas")
if pg86_world.get("source_atlas") != "Data/Part1ProductionAtlas.json":
    fail("PG-086 world matrix not linked to Part1ProductionAtlas")
if not (ROOT / "Scripts" / "production_readiness_audit.py").exists():
    fail("PG-086 production readiness audit missing")


# PG-087: every accepted Part I ensemble playable viewpoint must have a non-Frodo visual path.
pg87_plan = json.loads(read(ROOT / "Data" / "EnsembleFilmMissionPlan.json"))
pg87_required_playables = {"Gandalf", "Arwen", "Boromir", "Legolas", "Gimli", "Aragorn"}
for pg87_item in pg87_plan.get("part1", []):
    if not isinstance(pg87_item, dict):
        continue
    pg87_character = str(pg87_item.get("character") or "")
    if pg87_character and pg87_item.get("type") in {"FILM_CORE_PLAYABLE", "CHARACTER_SPECIALTY", "FILM_INTERSTITIAL"}:
        pg87_required_playables.add(pg87_character)
pg87_cpp = read(resolve_source("ShirePlayerCharacter.cpp"))
pg87_h = read(resolve_source("ShirePlayerCharacter.h"))
for pg87_character in sorted(pg87_required_playables | {"Frodo", "Sam", "Merry", "Pippin"}):
    if f'TEXT("{pg87_character}")' not in pg87_cpp:
        fail(f"PG-087 playable visual mapping missing: {pg87_character}")
for pg87_symbol in ["SupportedPlayableIds", "PrototypeMotionProfile", "SM_ProductionSword", "SM_ProductionBow", "SM_ProductionAxe"]:
    if pg87_symbol not in (pg87_cpp + pg87_h):
        fail(f"PG-087 ensemble production visual symbol missing: {pg87_symbol}")
if "unsupported playable id=%s; using Frodo fallback" not in pg87_cpp:
    fail("PG-087 unsupported playable visual fallback is not explicit")


# PG-088: source-grounded Part I geography must be packaged and visible at runtime.
pg88_build = read(resolve_source("ShireJourney.Build.cs"))
pg88_qh = read(resolve_source("ShireQuestSubsystem.h"))
pg88_qc = read(resolve_source("ShireQuestSubsystem.cpp"))
pg88_hud = read(resolve_source("ShireHUD.cpp"))
if "Part1ProductionAtlas.json" not in pg88_build:
    fail("PG-088 Part1ProductionAtlas is not packaged")
for pg88_symbol in [
    "FShireChapterProductionDefinition",
    "LoadPart1ProductionAtlas",
    "GetCurrentChapterDisplayName",
    "GetCurrentPrimaryRegionName",
    "GetCurrentMacroRegionName",
    "GetCurrentLandmarkSummary",
    "ProductionAtlas: ready=yes chapters=%d",
]:
    if pg88_symbol not in (pg88_qh + pg88_qc):
        fail(f"PG-088 runtime geography symbol missing: {pg88_symbol}")
if "GetCurrentPrimaryRegionName()" not in pg88_hud:
    fail("PG-088 HUD is not using source-grounded current region naming")


# PG-089: playable production characters must support async final-rig handoff with modular fallback.
pg89_h = read(resolve_source("ShirePlayerCharacter.h"))
pg89_cpp = read(resolve_source("ShirePlayerCharacter.cpp"))
pg89_stream_h = read(resolve_source("ShireChapterAssetStreamingSubsystem.h"))
pg89_stream_cpp = read(resolve_source("ShireChapterAssetStreamingSubsystem.cpp"))
for pg89_symbol in [
    "TryApplyProductionRig",
    "bUsingSkeletalProductionRig",
    "HandleProductionRigReady",
    "OnCharacterRigReady",
]:
    if pg89_symbol not in (pg89_h + pg89_cpp + pg89_stream_h + pg89_stream_cpp):
        fail(f"PG-089 playable skeletal production handoff missing: {pg89_symbol}")
for pg89_symbol in [
    "RequestCharacterRig",
    "ResolveCharacterRig",
    "SK_%s",
    "ABP_%s_Locomotion",
    "RequestAsyncLoad",
]:
    if pg89_symbol not in (pg89_stream_h + pg89_stream_cpp):
        fail(f"PG-089 async rig streaming contract missing: {pg89_symbol}")
if "if (bUsingSkeletalProductionRig)" not in pg89_cpp:
    fail("PG-089 modular animation does not yield to production skeletal rig")
if "LoadObject<USkeletalMesh>" in pg89_cpp or "LoadClass<UAnimInstance>" in pg89_cpp:
    fail("PG-089 playable rig handoff regressed to synchronous heavy loading")


# PG-090: missing Isengard/Lurtz/Watcher/Balrog roots must remain present and non-final.
for pg90_rel in [
    "SourceAssets/Production/World/Isengard/SM_Isengard_OrthancCore.obj",
    "SourceAssets/Production/World/Isengard/SM_Isengard_OrthancSpire.obj",
    "SourceAssets/Production/Enemies/Lurtz/SM_Lurtz_Torso.obj",
    "SourceAssets/Production/Enemies/Watcher/SM_Watcher_Core.obj",
    "SourceAssets/Production/Enemies/Balrog/SM_Balrog_Torso.obj",
]:
    if not (ROOT / pg90_rel).exists():
        fail(f"PG-090 production foundation missing: {pg90_rel}")
pg90_isengard = read(resolve_source("IsengardPrototypeWorldBuilder.cpp"))
for pg90_symbol in ["SM_Isengard_OrthancCore","SM_Isengard_OrthancSpire","SM_Isengard_IndustrialPitRim","SM_Isengard_FurnaceStack","SM_Isengard_FelledTrunk"]:
    if pg90_symbol not in pg90_isengard:
        fail(f"PG-090 Isengard runtime production wiring missing: {pg90_symbol}")
pg90_chars = json.loads(read(ROOT / "Data" / "CharacterProductionMatrix.json"))
pg90_threats = {str(row.get("id") or ""): row for row in pg90_chars.get("threats", []) if isinstance(row, dict)}
for pg90_id in ["LURTZ","WATCHER","BALROG"]:
    pg90_row = pg90_threats.get(pg90_id)
    if not pg90_row or not pg90_row.get("asset_root"):
        fail(f"PG-090 threat foundation root missing: {pg90_id}")
    if "PENDING" not in str(pg90_row.get("status") or ""):
        fail(f"PG-090 threat foundation lost explicit pending-final status: {pg90_id}")


# PG-091: Watcher and Balrog are film-locked pressure actors, never killable reward targets.
pg91_h = read(resolve_source("FellowshipMythicThreat.h"))
pg91_cpp = read(resolve_source("FellowshipMythicThreat.cpp"))
pg91_builder = read(resolve_source("FellowshipChapterWorldBuilder.cpp"))
for pg91_symbol in [
    "EFellowshipMythicThreatType",
    "Watcher",
    "Balrog",
    "ActivationStoryBeat",
    "DeactivationStoryBeat",
    "storyEffect=NONE",
    "gameplayCollision=off killable=no",
]:
    if pg91_symbol not in (pg91_h + pg91_cpp):
        fail(f"PG-091 mythic threat contract missing: {pg91_symbol}")
for pg91_symbol in [
    'TEXT("WatcherAttack")',
    'TEXT("MoriaEntry")',
    'TEXT("BalrogApproach")',
    'TEXT("MoriaEscape")',
    "EFellowshipMythicThreatType::Watcher",
    "EFellowshipMythicThreatType::Balrog",
]:
    if pg91_symbol not in pg91_builder:
        fail(f"PG-091 film-locked mythic threat wiring missing: {pg91_symbol}")
for pg91_forbidden in ["TakeDamage(", "ApplyDamage(", "JourneyInsight", "AwardProgressionXP", "TriggerStoryBeat("]:
    if pg91_forbidden in pg91_cpp:
        fail(f"PG-091 mythic threat may not mutate combat/reward/story state: {pg91_forbidden}")


# PG-092: source-grounded world map is packaged, spoiler-bounded and reachable from UI.
pg92_path = ROOT / "Data" / "Part1WorldMap.json"
if not pg92_path.exists():
    fail("PG-092 Part1WorldMap missing")
    pg92_map = {}
else:
    try:
        pg92_map = json.loads(read(pg92_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-092 invalid Part1WorldMap: {exc}")
        pg92_map = {}

pg92_nodes = {
    str(node.get("id") or ""): node
    for node in pg92_map.get("nodes", [])
    if isinstance(node, dict)
}
if len(pg92_nodes) < 16:
    fail(f"PG-092 world map node coverage regressed: {len(pg92_nodes)}")
for pg92_id, pg92_node in pg92_nodes.items():
    if not pg92_node.get("route") or not pg92_node.get("chapter") or not pg92_node.get("display_name"):
        fail(f"PG-092 incomplete world map node: {pg92_id}")
    try:
        pg92_x = float(pg92_node.get("x"))
        pg92_y = float(pg92_node.get("y"))
    except (TypeError, ValueError):
        fail(f"PG-092 invalid map coordinates: {pg92_id}")
        continue
    if not (0.0 <= pg92_x <= 1.0 and 0.0 <= pg92_y <= 1.0):
        fail(f"PG-092 map node outside normalized bounds: {pg92_id}")
for pg92_edge in pg92_map.get("edges", []):
    if not isinstance(pg92_edge, list) or len(pg92_edge) != 2:
        fail("PG-092 invalid world map edge shape")
        continue
    if str(pg92_edge[0]) not in pg92_nodes or str(pg92_edge[1]) not in pg92_nodes:
        fail(f"PG-092 world map edge references unknown node: {pg92_edge}")

pg92_build = read(resolve_source("ShireJourney.Build.cs"))
pg92_qh = read(resolve_source("ShireQuestSubsystem.h"))
pg92_qc = read(resolve_source("ShireQuestSubsystem.cpp"))
pg92_ph = read(resolve_source("ShirePlayerCharacter.h"))
pg92_pc = read(resolve_source("ShirePlayerCharacter.cpp"))
pg92_hud = read(resolve_source("ShireHUD.cpp"))
pg92_input = read(ROOT / "Config" / "DefaultInput.ini")
for pg92_symbol in ["Part1WorldMap.json","LoadPart1WorldMap","IsWorldMapNodeVisible","GetCurrentWorldMapNodeId"]:
    if pg92_symbol not in (pg92_build + pg92_qh + pg92_qc):
        fail(f"PG-092 runtime world-map symbol missing: {pg92_symbol}")
if 'ActionName="ToggleWorldMap"' not in pg92_input or 'BindAction(TEXT("ToggleWorldMap")' not in pg92_pc:
    fail("PG-092 M-key world-map control missing")
for pg92_marker in ["JOURNEY MAP","Undiscovered future chapters stay hidden","GetWorldMapEdges"]:
    if pg92_marker not in (pg92_hud + pg92_qh):
        fail(f"PG-092 world-map UI marker missing: {pg92_marker}")
if "return HasKnownMapRegion(MakeKnownMapRegionId" not in pg92_qc:
    fail("PG-092 future world-map visibility is not bounded by Map Knowledge")


# PG-093: Part I visual-production wave must stay source-grounded, packaged and film-safe.
pg93_visual_path = ROOT / "Data" / "Part1VisualProductionPass.json"
if not pg93_visual_path.exists():
    fail("PG-093 Part1VisualProductionPass missing")
    pg93_visual = {}
else:
    try:
        pg93_visual = json.loads(read(pg93_visual_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-093 invalid Part1VisualProductionPass: {exc}")
        pg93_visual = {}
if pg93_visual.get("status") != "ACTIVE_IMPLEMENTATION_PENDING_ENGINE_PROOF":
    fail("PG-093 visual production status must remain pending engine proof")
if len(pg93_visual.get("chapters", [])) != 8:
    fail("PG-093 visual production pass must cover P1C01-P1C08")
pg93_build = read(resolve_source("ShireJourney.Build.cs"))
if "Part1VisualProductionPass.json" not in pg93_build:
    fail("PG-093 visual production pass is not packaged")
pg93_enemy_h = read(resolve_source("FellowshipEnemyPrototype.h"))
pg93_enemy_cpp = read(resolve_source("FellowshipEnemyPrototype.cpp"))
pg93_builder = read(resolve_source("FellowshipChapterWorldBuilder.cpp"))
for pg93_symbol in ["Lurtz", "FilmLockedOutcome", 'ProductionFolder = TEXT("Lurtz")', 'TEXT("Blade")', "player-controlled branch"]:
    if pg93_symbol not in (pg93_enemy_h + pg93_enemy_cpp):
        fail(f"PG-093 film-locked Lurtz contract missing: {pg93_symbol}")
if "EFellowshipEnemyType::Lurtz" not in pg93_builder:
    fail("PG-093 Lurtz is not wired into Amon Hen runtime")
for pg93_asset in [
    "SM_MoriaBrokenStair", "SM_MoriaChainAnchor", "SM_MoriaTallBrazier", "SM_MoriaMineCart",
    "SM_AnduinBoatRack", "SM_AnduinCargoPile", "SM_AnduinRiverMarker", "SM_AnduinDockPier",
]:
    if pg93_asset not in pg93_builder:
        fail(f"PG-093 visual production asset not runtime-wired: {pg93_asset}")

# PG-094: performance budgets are measurement-first; no invented hard scene ceilings.
pg94_budget_path = ROOT / "Data" / "AssetPerformanceBudget.json"
if not pg94_budget_path.exists():
    fail("PG-094 AssetPerformanceBudget missing")
    pg94_budget = {}
else:
    try:
        pg94_budget = json.loads(read(pg94_budget_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-094 invalid AssetPerformanceBudget: {exc}")
        pg94_budget = {}
if pg94_budget.get("status") != "MEASUREMENT_BASELINE_REQUIRED":
    fail("PG-094 performance budget must remain measurement-baseline gated")
if pg94_budget.get("policy", {}).get("hard_scene_budgets_enabled") is not False:
    fail("PG-094 hard scene budgets may not be invented before device measurement")
if "AssetPerformanceBudget.json" not in pg93_build:
    fail("PG-094 asset performance budget is not packaged")
pg94_audit = read(ROOT / "Scripts" / "asset_quality_audit.py")
for pg94_symbol in ["obj_triangle_equivalents", "Production source buckets", "Largest OBJ by triangle equivalents"]:
    if pg94_symbol not in pg94_audit:
        fail(f"PG-094 asset audit measurement missing: {pg94_symbol}")

# PG-095: selected hero/threat camera moments use bounded player-camera framing only.
pg95_player_h = read(resolve_source("ShirePlayerCharacter.h"))
pg95_player_cpp = read(resolve_source("ShirePlayerCharacter.cpp"))
for pg95_symbol in [
    "HandleStoryCameraCue",
    "UpdateStoryCameraCue",
    "OnCameraCueRequested.AddDynamic",
    "Cam_PonyExteriorReveal",
    "Cam_WeathertopReveal",
    "Cam_LorienEntry",
    "Cam_ArgonathReveal",
    "Cam_BalrogApproach",
    "Cam_UrukAttack",
]:
    if pg95_symbol not in (pg95_player_h + pg95_player_cpp):
        fail(f"PG-095 bounded camera framing marker missing: {pg95_symbol}")
if "SetViewTarget" in pg95_player_cpp or "SceneCapture" in pg95_player_cpp:
    fail("PG-095 bounded camera pass must not introduce heavy alternate camera/capture systems")
pg95_visual = json.loads(read(ROOT / "Data" / "Part1VisualProductionPass.json"))
if pg95_visual.get("camera_execution", {}).get("status") != "RUNTIME_FRAMING_IMPLEMENTED_PENDING_ENGINE_PROOF":
    fail("PG-095 camera execution evidence boundary changed")

# PG-096: Isengard atmosphere stays bounded, production-driven and non-final.
pg96_isengard = read(resolve_source("IsengardPrototypeWorldBuilder.cpp"))
for pg96_symbol in [
    "ShowPrototypeWorldLabels = false",
    "ADirectionalLight",
    "AExponentialHeightFog",
    "ForgeGlowLocations",
    "SM_Isengard_ParapetSlab",
]:
    if pg96_symbol not in pg96_isengard:
        fail(f"PG-096 Isengard presentation symbol missing: {pg96_symbol}")
if pg96_isengard.count("FVector(50.0f, 810.0f, 120.0f)") != 1:
    fail("PG-096 Isengard furnace-light contract changed unexpectedly")
pg96_visual = json.loads(read(ROOT / "Data" / "Part1VisualProductionPass.json"))
if pg96_visual.get("parallel_route", {}).get("acceptance") != "IMPLEMENTED_PENDING_UE4_BUILD_RENDER_AND_DEVICE_PROOF":
    fail("PG-096 Isengard visual acceptance boundary changed")

# PG-097: named skeletal NPC handoff uses bounded animation-cost safeguards.
pg97_motion = json.loads(read(ROOT / "Data" / "CharacterMotionPlan.json"))
pg97_npc = read(resolve_source("ShireNPC.cpp"))
if pg97_motion.get("runtime_performance_handoff", {}).get("status") != "IMPLEMENTED_PENDING_ENGINE_PROOF":
    fail("PG-097 named NPC performance handoff status changed")
for pg97_symbol in [
    "bEnableUpdateRateOptimizations = true",
    "OnlyTickPoseWhenRendered",
    "PlayerDistance > 4200.0f",
    "PlayerDistance > 2200.0f",
]:
    if pg97_symbol not in pg97_npc:
        fail(f"PG-097 named NPC performance safeguard missing: {pg97_symbol}")
if "DistancePawn && !bFollowingPlayer && DialogueActingRemaining <= 0.0f" not in pg97_npc:
    fail("PG-097 follow/dialogue responsiveness guard missing")

# PG-098: Isengard production meshes retain an authored material palette.
pg98_isengard_root = ROOT / "SourceAssets" / "Production" / "World" / "Isengard"
pg98_mtl = pg98_isengard_root / "RegionalMaterials.mtl"
if not pg98_mtl.exists():
    fail("PG-098 Isengard RegionalMaterials.mtl missing")
else:
    pg98_mtl_text = read(pg98_mtl)
    for pg98_material in ["OrthancBlackStone","OrthancEdgeStone","IndustrialIron","FurnaceIron","ScorchedWood"]:
        if f"newmtl {pg98_material}" not in pg98_mtl_text:
            fail(f"PG-098 Isengard authored material missing: {pg98_material}")
for pg98_obj in [
    "SM_Isengard_OrthancCore.obj","SM_Isengard_OrthancSpire.obj",
    "SM_Isengard_IndustrialPitRim.obj","SM_Isengard_FurnaceStack.obj",
    "SM_Isengard_FelledTrunk.obj","SM_Isengard_ParapetSlab.obj",
]:
    pg98_text = read(pg98_isengard_root / pg98_obj)
    if "mtllib RegionalMaterials.mtl" not in pg98_text or "usemtl " not in pg98_text:
        fail(f"PG-098 Isengard OBJ lacks authored material binding: {pg98_obj}")
pg98_builder = read(resolve_source("IsengardPrototypeWorldBuilder.cpp"))
if "bFallbackPrimitive" not in pg98_builder:
    fail("PG-098 Isengard runtime no longer preserves production mesh materials")
pg98_visual = json.loads(read(ROOT / "Data" / "Part1VisualProductionPass.json"))
if pg98_visual.get("parallel_route", {}).get("authored_material_palette", {}).get("status") != "SOURCE_AUTHORED_PENDING_ENGINE_IMPORT_PROOF":
    fail("PG-098 Isengard authored-material proof boundary changed")

# PG-099: Lurtz/Watcher/Balrog authored materials survive production handoff.
pg99_specs = {
    "Lurtz": ["LurtzSkin","LurtzArmor","LurtzDarkIron"],
    "Watcher": ["WatcherCore","WatcherTentacle"],
    "Balrog": ["BalrogCharcoal","BalrogEmber","BalrogHorn","BalrogWing"],
}
for pg99_folder, pg99_materials in pg99_specs.items():
    pg99_root = ROOT / "SourceAssets" / "Production" / "Enemies" / pg99_folder
    pg99_mtl = pg99_root / "RegionalMaterials.mtl"
    if not pg99_mtl.exists():
        fail(f"PG-099 threat material library missing: {pg99_folder}")
        continue
    pg99_text = read(pg99_mtl)
    for pg99_material in pg99_materials:
        if f"newmtl {pg99_material}" not in pg99_text:
            fail(f"PG-099 threat authored material missing: {pg99_folder}/{pg99_material}")
    for pg99_obj in pg99_root.glob("*.obj"):
        pg99_obj_text = read(pg99_obj)
        if "mtllib RegionalMaterials.mtl" not in pg99_obj_text or "usemtl " not in pg99_obj_text:
            fail(f"PG-099 threat OBJ lacks authored material binding: {pg99_obj.relative_to(ROOT)}")
pg99_enemy = read(resolve_source("FellowshipEnemyPrototype.cpp"))
pg99_mythic = read(resolve_source("FellowshipMythicThreat.cpp"))
if "if (!bProductionVisual)" not in pg99_enemy:
    fail("PG-099 production enemy materials are being overwritten by fallback tint")
if "BasicMaterial && !bProductionFoundation" not in pg99_mythic:
    fail("PG-099 production mythic materials are being overwritten by fallback tint")
pg99_visual = json.loads(read(ROOT / "Data" / "Part1VisualProductionPass.json"))
if pg99_visual.get("threat_material_palettes", {}).get("status") != "SOURCE_AUTHORED_PENDING_ENGINE_IMPORT_PROOF":
    fail("PG-099 authored threat material proof boundary changed")

# PG-100: unattended production import must persist authored material packages.
pg100_importer = read(ROOT / "Source" / "ShireJourneyEditorTools" / "Private" / "ShireProductionImportCommandlet.cpp")
pg100_build = read(ROOT / "Source" / "ShireJourneyEditorTools" / "ShireJourneyEditorTools.Build.cs")
for pg100_symbol in [
    "AuthoredMaterialDestinationPaths",
    "RecoveredMaterialBindings",
    "FAssetRegistryModule",
    "GetAssetsByPath",
    "ImportedMaterialPackages.AddUnique",
    "SaveMaterialPackagesDeterministically",
    "UPackage::SavePackage",
    "material registry recovery",
]:
    if pg100_symbol not in pg100_importer:
        fail(f"PG-100 material persistence safeguard missing: {pg100_symbol}")
if '"AssetRegistry"' not in pg100_build:
    fail("PG-100 ShireJourneyEditorTools must depend on AssetRegistry")

# PG-101: authored MTL palettes must be materialized before OBJ import.
pg101_importer = read(ROOT / "Source" / "ShireJourneyEditorTools" / "Private" / "ShireProductionImportCommandlet.cpp")
for pg101_symbol in [
    "MaterialLibraryFiles",
    "UMaterialInstanceConstantFactoryNew",
    "synthesized authored materials",
    "SetVectorParameterValueEditorOnly",
    "ImportOptions->bImportMaterials = false",
    "StaticMaterial.MaterialInterface = AuthoredMaterial",
]:
    if pg101_symbol not in pg101_importer:
        fail(f"PG-101 deterministic material synthesis missing: {pg101_symbol}")

# PG-102: player-experience safety and deep-audit contracts.
pg102_player = read(resolve_source("ShirePlayerCharacter.cpp"))
pg102_presentation = read(resolve_source("ShireStoryPresentationSubsystem.cpp"))
for pg102_symbol in ["#if !UE_BUILD_SHIPPING","AsyncSaveGameToSlot","bCheckpointSaveInFlight","QueuedCheckpointSaveId"]:
    if pg102_symbol not in pg102_player:
        fail(f"PG-102 player-experience safeguard missing: {pg102_symbol}")
if "FMath::Clamp(ActiveCue.SuggestedDuration, 1.0f, 3.5f)" not in pg102_presentation:
    fail("PG-102 cinematic input lock must remain bounded to 3.5 seconds")
for pg102_path in [ROOT/"Data"/"DeepProjectAudit.json",ROOT/"Docs"/"DEEP_PROJECT_AUDIT.md",ROOT/"Scripts"/"deep_project_audit.py"]:
    if not pg102_path.exists():
        fail(f"PG-102 deep audit artifact missing: {pg102_path.relative_to(ROOT)}")

# PG-103: synthesized production materials must be physically persisted, not merely dirty in memory.
pg103_importer = read(ROOT / "Source" / "ShireJourneyEditorTools" / "Private" / "ShireProductionImportCommandlet.cpp")
for pg103_symbol in [
    "SaveMaterialPackagesDeterministically",
    "UPackage::SavePackage",
    "FPackageName::LongPackageNameToFilename",
    "GetAssetPackageExtension",
    "material persistence verification",
    "FileExists",
]:
    if pg103_symbol not in pg103_importer:
        fail(f"PG-103 deterministic material persistence safeguard missing: {pg103_symbol}")

# PG-104: material existence probes and warning debt must distinguish import-time probes from runtime failures.
pg104_importer = read(ROOT / "Source" / "ShireJourneyEditorTools" / "Private" / "ShireProductionImportCommandlet.cpp")
pg104_reset = read(ROOT / "Scripts" / "reset_project_build_intermediates.ps1")
pg104_warning = read(ROOT / "Scripts" / "warning_debt_guard.py")
for pg104_symbol in [
    "FindObject<UMaterialInstanceConstant>",
    "FPackageName::DoesPackageExist(PackageName)",
    "FindObject<UMaterialInterface>",
]:
    if pg104_symbol not in pg104_importer:
        fail(f"PG-104 quiet material existence probe missing: {pg104_symbol}")
if 'Filter "CI-*.log"' not in pg104_reset:
    fail("PG-104 exact-head validation must clear stale CI logs before generating new evidence")
for pg104_symbol in [
    'RUNTIME_LOG_PREFIXES',
    'scope="runtime"',
    'collect_text(files, "runtime")',
]:
    if pg104_symbol not in pg104_warning:
        fail(f"PG-104 warning-debt evidence scoping missing: {pg104_symbol}")

# PG-105: untextured OBJ meshes use a tangent generator that does not require UVs.
pg105_importer = read(ROOT / "Source" / "ShireJourneyEditorTools" / "Private" / "ShireProductionImportCommandlet.cpp")
for pg105_symbol in [
    "bHasTextureCoordinates",
    "FBXNIM_ComputeNormals",
    "EFBXNormalGenerationMethod::BuiltIn",
    "builtin-no-uv",
]:
    if pg105_symbol not in pg105_importer:
        fail(f"PG-105 untextured OBJ tangent safeguard missing: {pg105_symbol}")

# PG-106: the owner's eight production bibles are traceable references, never shipping dependencies.
pg106_index = json.loads(read(ROOT / "Data" / "OwnerSourceReferenceIndex.json"))
pg106_sources = {str(row.get("id") or ""): row for row in pg106_index.get("sources", []) if isinstance(row, dict)}
for pg106_id in [
    "SRC_OWNER_STORY_TIMELINE_BIBLE_V1",
    "SRC_OWNER_CHARACTERS_RELATIONSHIPS_BIBLE_V1",
    "SRC_OWNER_WORLD_LOCATIONS_MAP_BIBLE_V1",
    "SRC_OWNER_PEOPLES_LORE_ARTIFACTS_CULTURES_BIBLE_V1",
    "SRC_OWNER_BATTLES_WEAPONS_ARMIES_CREATURES_BIBLE_V1",
    "SRC_OWNER_GAMEPLAY_SIDE_ACTIVITIES_BIBLE_V1",
    "SRC_OWNER_MISSION_CHAPTER_IMPLEMENTATION_MATRIX_V1",
    "SRC_OWNER_VISUAL_REFERENCE_BIBLE_V1",
]:
    pg106_row = pg106_sources.get(pg106_id)
    if not pg106_row:
        fail(f"PG-106 owner source bible missing from reference index: {pg106_id}")
        continue
    if pg106_row.get("runtime_ship") is not False:
        fail(f"PG-106 raw owner source bible may not become a runtime dependency: {pg106_id}")
    if not pg106_row.get("sha256"):
        fail(f"PG-106 owner source bible provenance hash missing: {pg106_id}")

pg106_visual = json.loads(read(ROOT / "Data" / "Part1VisualProductionPass.json"))
pg106_wave = pg106_visual.get("current_wave", {})
if not str(pg106_wave.get("id") or ""):
    fail("PG-106 current production wave id missing")
if not str(pg106_wave.get("status") or ""):
    fail("PG-106 current production wave status missing")
pg106_alignment = pg106_visual.get("bible_alignment", {})
if pg106_alignment.get("status") != "IMPLEMENTED_PENDING_EXACT_HEAD_ENGINE_PROOF":
    fail("PG-106 Bible alignment provenance contract changed")
pg106_alignment_sources = set(pg106_alignment.get("sources", []))
for pg106_required_source in [
    "SRC_OWNER_WORLD_LOCATIONS_MAP_BIBLE_V1",
    "SRC_OWNER_BATTLES_WEAPONS_ARMIES_CREATURES_BIBLE_V1",
    "SRC_OWNER_MISSION_CHAPTER_IMPLEMENTATION_MATRIX_V1",
    "SRC_OWNER_VISUAL_REFERENCE_BIBLE_V1",
]:
    if pg106_required_source not in pg106_alignment_sources:
        fail(f"PG-106 Bible alignment source missing: {pg106_required_source}")

# PG-107/108: screenplay-first story authority plus complete 01-09 source hierarchy.
pg107_index = json.loads(read(ROOT / "Data" / "OwnerSourceReferenceIndex.json"))
pg107_sources = {
    str(row.get("id") or ""): row
    for row in pg107_index.get("sources", [])
    if isinstance(row, dict)
}
for pg107_id in ["SRC_FILM_FOTR_SCREENPLAY", "SRC_FILM_TTT_SCREENPLAY", "SRC_FILM_ROTK_SCREENPLAY"]:
    pg107_row = pg107_sources.get(pg107_id)
    if not pg107_row:
        fail(f"PG-107 primary screenplay source missing: {pg107_id}")
        continue
    if pg107_row.get("kind") != "PRIMARY_SCREENPLAY_STORY_AUTHORITY":
        fail(f"PG-107 screenplay not primary story authority: {pg107_id}")
    if pg107_row.get("runtime_ship") is not False:
        fail(f"PG-107 raw screenplay may not ship at runtime: {pg107_id}")
    if not pg107_row.get("sha256"):
        fail(f"PG-107 screenplay provenance hash missing: {pg107_id}")

pg107_authority = pg107_index.get("story_authority", {})
pg107_primary = {
    str(row.get("source_id") or "")
    for row in pg107_authority.get("primary_screenplays", [])
    if isinstance(row, dict)
}
for pg107_id in ["SRC_FILM_FOTR_SCREENPLAY", "SRC_FILM_TTT_SCREENPLAY", "SRC_FILM_ROTK_SCREENPLAY"]:
    if pg107_id not in pg107_primary:
        fail(f"PG-107 screenplay absent from primary authority list: {pg107_id}")
pg107_rule = str(pg107_authority.get("rule") or "")
pg107_rule_lower = pg107_rule.lower()
if "film" not in pg107_rule_lower or "screenplay" not in pg107_rule_lower or "primary" not in pg107_rule_lower:
    fail("PG-107 film/screenplay primary story-authority rule missing")
if "silently replace film" not in pg107_rule_lower:
    fail("PG-107 Tolkien-vs-film precedence boundary missing")

pg108_summary = pg107_index.get("source_set_summary", {})
if pg108_summary.get("core_pdf_count") != 15:
    fail("PG-108 core PDF source count must remain 15")
if pg108_summary.get("supplied_screenplays") != 3:
    fail("PG-108 screenplay count must remain 3")
if pg108_summary.get("numbered_production_bibles") != 11:
    fail("PG-108 numbered production source count must remain 11")
pg108_helper = pg107_sources.get("SRC_OWNER_EXTERNAL_HELPFUL_RESOURCES_BIBLE_V1")
if not pg108_helper:
    fail("PG-108 external helpful resources Bible 09 missing")
else:
    if pg108_helper.get("authority") != "HELPER_ONLY_NOT_CANON_NOT_STORY":
        fail("PG-108 Bible 09 must remain helper-only")
    if pg108_helper.get("runtime_ship") is not False:
        fail("PG-108 raw Bible 09 may not ship at runtime")
if "Bible 09 external-resource discovery" not in " ".join(pg107_authority.get("precedence", [])):
    fail("PG-108 Bible 09 authority boundary missing")

for pg108_id in [
    "SRC_OWNER_3D_VISUAL_ASSET_ATLAS_V1",
    "SRC_OWNER_MASTER_PRODUCTION_SYSTEMS_SOURCE_INDEX_V1",
    "SRC_TOLKIEN_LOTR_2010",
]:
    if pg108_id not in pg107_sources:
        fail(f"PG-108 expanded project source missing: {pg108_id}")
if "SRC_TOLKIEN_LOTR_2010" not in {
    str(row.get("source_id") or "")
    for row in pg107_authority.get("primary_deep_lore_sources", [])
    if isinstance(row, dict)
}:
    fail("PG-108 Tolkien full volume missing from deep-lore authority list")
if pg107_authority.get("master_production_systems_source") != "SRC_OWNER_MASTER_PRODUCTION_SYSTEMS_SOURCE_INDEX_V1":
    fail("PG-108 Source 11 master production systems authority missing")

# PG-112: mega material/world saturation wave must be large, source-controlled,
# film-safe and explicit about its evidence boundary.
pg112_plan_path = ROOT / "Data" / "MegaMaterialWorldWaveV1.json"
if not pg112_plan_path.exists():
    fail("PG-112 MegaMaterialWorldWaveV1.json missing")
    pg112_plan = {}
else:
    try:
        pg112_plan = json.loads(read(pg112_plan_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-112 invalid MegaMaterialWorldWaveV1.json: {exc}")
        pg112_plan = {}
if pg112_plan.get("wave_id") != "MEGA_MATERIAL_WORLD_WAVE_V1":
    fail("PG-112 mega-wave identity changed")
if pg112_plan.get("status") != "ACTIVE_IMPLEMENTATION_PENDING_EXACT_HEAD_PROOF":
    fail("PG-112 mega-wave status must remain pending exact-head proof")
if "MegaMaterialWorldWaveV1.json" not in pg93_build:
    fail("PG-112 mega-wave plan is not packaged")

pg112_moria_assets = [
    "SM_MoriaWallPanel", "SM_MoriaFloorSlab", "SM_MoriaArch", "SM_MoriaCeilingRib",
    "SM_MoriaBridgePier", "SM_MoriaTombDais", "SM_MoriaReliefPanel", "SM_MoriaMineRail",
    "SM_MoriaOreCrate", "SM_MoriaCollapsedBeam", "SM_MoriaTorchNiche",
    "SM_MoriaChasmButtress", "SM_MoriaSideDoor", "SM_MoriaDebrisCluster",
]
pg112_moria_root = ROOT / "SourceAssets" / "Production" / "World" / "Moria"
for pg112_asset in pg112_moria_assets:
    pg112_path = pg112_moria_root / f"{pg112_asset}.obj"
    if not pg112_path.exists():
        fail(f"PG-112 Moria mega-wave asset missing: {pg112_asset}")
    if pg112_asset not in pg93_builder:
        fail(f"PG-112 Moria mega-wave asset not runtime-wired: {pg112_asset}")

pg112_mtl_paths = [
    ROOT / "SourceAssets" / "Production" / "World" / "Anduin" / "RegionalMaterials.mtl",
    ROOT / "SourceAssets" / "Production" / "World" / "Anduin" / "WorldPack.mtl",
    ROOT / "SourceAssets" / "Production" / "World" / "Bree" / "BreeMaterials.mtl",
    ROOT / "SourceAssets" / "Production" / "World" / "Bree" / "WorldPack.mtl",
    ROOT / "SourceAssets" / "Production" / "World" / "Common" / "CommonLandscapeMaterials.mtl",
    ROOT / "SourceAssets" / "Production" / "World" / "Common" / "WorldPack.mtl",
    ROOT / "SourceAssets" / "Production" / "World" / "Lothlorien" / "RegionalMaterials.mtl",
    ROOT / "SourceAssets" / "Production" / "World" / "Lothlorien" / "WorldPack.mtl",
    ROOT / "SourceAssets" / "Production" / "World" / "Moria" / "RegionalMaterials.mtl",
    ROOT / "SourceAssets" / "Production" / "World" / "Moria" / "WorldPack.mtl",
    ROOT / "SourceAssets" / "Production" / "World" / "Rivendell" / "RegionalMaterials.mtl",
    ROOT / "SourceAssets" / "Production" / "World" / "Rivendell" / "WorldPack.mtl",
    ROOT / "SourceAssets" / "Production" / "World" / "Road" / "RegionalMaterials.mtl",
    ROOT / "SourceAssets" / "Production" / "World" / "Road" / "WorldPack.mtl",
    ROOT / "SourceAssets" / "Production" / "World" / "Shire" / "ShireMaterials.mtl",
    ROOT / "SourceAssets" / "Production" / "World" / "Shire" / "WorldPack.mtl",
    ROOT / "SourceAssets" / "Production" / "World" / "Weathertop" / "RegionalMaterials.mtl",
    ROOT / "SourceAssets" / "Production" / "World" / "Weathertop" / "WorldPack.mtl",
    ROOT / "SourceAssets" / "Production" / "World" / "Isengard" / "RegionalMaterials.mtl",
]
for pg112_mtl in pg112_mtl_paths:
    if not pg112_mtl.exists():
        fail(f"PG-112 material palette missing: {pg112_mtl.relative_to(ROOT).as_posix()}")
        continue
    pg112_text = read(pg112_mtl)
    if "newmtl " not in pg112_text or "Kd " not in pg112_text:
        fail(f"PG-112 invalid material palette: {pg112_mtl.relative_to(ROOT).as_posix()}")
    if "Pr " not in pg112_text or "Pm " not in pg112_text:
        fail(f"PG-112 material response missing Pr/Pm: {pg112_mtl.relative_to(ROOT).as_posix()}")

for pg112_story_symbol in [
    'ConfigureThreat(\n            EFellowshipMythicThreatType::Watcher',
    'EFellowshipEnemyType::CaveTroll',
    'ConfigureThreat(\n            EFellowshipMythicThreatType::Balrog',
    'TEXT("The Fellowship escapes the mountain, but Gandalf is gone.")',
]:
    if pg112_story_symbol not in pg93_builder:
        fail(f"PG-112 Moria film-locked outcome marker missing: {pg112_story_symbol}")

pg112_visual = json.loads(read(ROOT / "Data" / "Part1VisualProductionPass.json"))
if pg112_visual.get("mega_material_world_wave", {}).get("status") != "SOURCE_IMPLEMENTATION_ACTIVE_PENDING_EXACT_HEAD_PROOF":
    fail("PG-112 visual mega-wave historical evidence boundary changed")

# PG-114: dense decorative richness must use performance-aware instancing rather than actor spam.
pg114_cluster_h = read(resolve_source("WorldDetailCluster.h"))
pg114_cluster_cpp = read(resolve_source("WorldDetailCluster.cpp"))
for pg114_symbol in [
    "UHierarchicalInstancedStaticMeshComponent",
    "AddInstanceWorldSpace",
    "SetCullDistances",
    "bCastDynamicShadow = false",
    "bCastStaticShadow = false",
]:
    if pg114_symbol not in (pg114_cluster_h + pg114_cluster_cpp):
        fail(f"PG-114 detail-cluster performance contract missing: {pg114_symbol}")

for pg114_symbol in [
    "SpawnInstancedScatter",
    "WorldDetailCluster",
    "MoriaDebrisClusterMesh",
    "CommonFernClumpMesh",
    "CommonReedClusterMesh",
    "CommonRuinSlabMesh",
]:
    if pg114_symbol not in pg93_builder:
        fail(f"PG-114 instanced detail runtime wiring missing: {pg114_symbol}")

pg114_dressing = json.loads(read(ROOT / "Data" / "WorldDressingPlan.json"))
if pg114_dressing.get("status") not in {
    "V10_INSTANCED_DETAIL_AND_ENVIRONMENTAL_LIFE_PENDING_ENGINE_PROOF",
    "V11_REALM_SPECIFIC_DETAIL_PENDING_ENGINE_PROOF",
}:
    fail("PG-114 world-dressing proof boundary changed")
pg114_budget = json.loads(read(ROOT / "Data" / "AssetPerformanceBudget.json"))
if pg114_budget.get("runtime_detail_policy", {}).get("instanced_micro_detail", {}).get("status") != "IMPLEMENTED_PENDING_MEASUREMENT":
    fail("PG-114 instanced-detail performance evidence boundary missing")

# PG-115: realm-specific V2 must remain source-grounded, runtime-wired and canon-safe.
pg115_plan_path = ROOT / "Data" / "RealmDetailSaturationV2.json"
if not pg115_plan_path.exists():
    fail("PG-115 RealmDetailSaturationV2.json missing")
    pg115_plan = {}
else:
    try:
        pg115_plan = json.loads(read(pg115_plan_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-115 invalid RealmDetailSaturationV2.json: {exc}")
        pg115_plan = {}

if pg115_plan.get("wave_id") != "REALM_DETAIL_SATURATION_V2":
    fail("PG-115 realm-detail wave identity changed")
if pg115_plan.get("status") not in {
    "SOURCE_RUNTIME_IMPLEMENTED_PENDING_EXACT_HEAD_PROOF",
    "EXACT_HEAD_ENGINE_PROOF_GREEN_PR57",
}:
    fail("PG-115 realm-detail proof boundary changed")
if "RealmDetailSaturationV2.json" not in pg93_build:
    fail("PG-115 realm-detail plan is not packaged")

pg115_assets = {
    "Rivendell": ["SM_RivLibraryArcade","SM_RivSmithyRack","SM_RivCouncilSeat","SM_RivWaterChannel"],
    "Lothlorien": ["SM_LorienGiftTable","SM_LorienBoatSupplyRack","SM_LorienCanopyRail","SM_LorienRopeLampLine"],
    "Anduin": ["SM_AmonHenBrokenSeat","SM_AmonHenLookoutStone","SM_AnduinSupplyBundle","SM_AnduinOarRack"],
    "Isengard": ["SM_IsengardHoistFrame","SM_IsengardSlagCart","SM_IsengardTrenchGrate","SM_IsengardWaterGate"],
}
pg115_isengard = read(resolve_source("IsengardPrototypeWorldBuilder.cpp"))
for pg115_region, pg115_names in pg115_assets.items():
    pg115_root = ROOT / "SourceAssets" / "Production" / "World" / pg115_region
    for pg115_name in pg115_names:
        pg115_asset_path = pg115_root / f"{pg115_name}.obj"
        if not pg115_asset_path.exists():
            fail(f"PG-115 realm-detail asset missing: {pg115_region}/{pg115_name}")
        pg115_runtime = pg115_isengard if pg115_region == "Isengard" else pg93_builder
        if pg115_name not in pg115_runtime:
            fail(f"PG-115 realm-detail asset not runtime-wired: {pg115_region}/{pg115_name}")

pg115_visual = json.loads(read(ROOT / "Data" / "Part1VisualProductionPass.json"))
if pg115_visual.get("realm_detail_saturation_v2", {}).get("added_project_owned_obj_assets") != 16:
    fail("PG-115 visual plan must retain 16 new project-owned OBJ assets")
if pg115_visual.get("realm_detail_saturation_v2", {}).get("status") not in {
    "PENDING_EXACT_HEAD_ENGINE_PROOF",
    "EXACT_HEAD_ENGINE_PROOF_GREEN_PR57",
}:
    fail("PG-115 realm-detail visual evidence boundary changed")

pg115_bank = json.loads(read(ROOT / "Data" / "WorldResourceBankCP54.json"))
if pg115_bank.get("source_asset_count", 0) < 105:
    fail("PG-115 world resource bank did not register V2 source assets")

pg115_inventory = json.loads(read(ROOT / "Data" / "ProjectOwnedProductionAssetInventory.json"))
if pg115_inventory.get("totals", {}).get("obj_files", 0) < 334:
    fail("PG-115 project-owned OBJ inventory did not register V2 assets")

# Film outcomes are immutable while environmental detail grows.
for pg115_story_symbol in [
    'TEXT("Boromir turns back toward Merry and Pippin and fights to protect them.")',
    'TEXT("Merry and Pippin are taken while Aragorn turns to Boromir.")',
    'TEXT("Frodo chooses the eastern shore. Sam refuses to let him go alone.")',
    "EFellowshipEnemyType::Lurtz",
]:
    if pg115_story_symbol not in pg93_builder:
        fail(f"PG-115 Amon Hen locked-outcome marker missing: {pg115_story_symbol}")

# PG-116: cinematic/character/sonic V3 must remain bounded, source-controlled and runtime-wired.
pg116_cinematic_path = ROOT / "Data" / "CinematicPerformancePlanV3.json"
pg116_sonic_path = ROOT / "Data" / "Part1SonicWorldPlan.json"
for pg116_path, pg116_id, pg116_statuses in [
    (pg116_cinematic_path, "PART1_CINEMATIC_CHARACTER_PERFORMANCE_V3",
     {"RUNTIME_CAMERA_AND_PROCEDURAL_PERFORMANCE_IMPLEMENTED_PENDING_EXACT_HEAD_PROOF",
      "EXACT_HEAD_ENGINE_PROOF_GREEN_PR58"}),
    (pg116_sonic_path, "PART1_SONIC_WORLD_V1",
     {"RUNTIME_ROUTING_AND_TRANSITIONS_IMPLEMENTED_ASSET_AUTHORING_PENDING"}),
]:
    if not pg116_path.exists():
        fail(f"PG-116 production plan missing: {pg116_path.name}")
        continue
    try:
        pg116_data = json.loads(read(pg116_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-116 invalid {pg116_path.name}: {exc}")
        continue
    if pg116_data.get("plan_id") != pg116_id:
        fail(f"PG-116 plan identity changed: {pg116_path.name}")
    if pg116_data.get("status") not in pg116_statuses:
        fail(f"PG-116 plan evidence boundary changed: {pg116_path.name}")
    if pg116_path.name not in pg93_build:
        fail(f"PG-116 runtime production plan is not packaged: {pg116_path.name}")

pg116_director_h = resolve_source("StoryPresentationDirector.h")
pg116_director_cpp = resolve_source("StoryPresentationDirector.cpp")
if not pg116_director_h.exists() or not pg116_director_cpp.exists():
    fail("PG-116 StoryPresentationDirector runtime files missing")
    pg116_director = ""
else:
    pg116_director = read(pg116_director_h) + "\n" + read(pg116_director_cpp)

for pg116_symbol in [
    "OnStoryPresentationRequested",
    "RuntimePresentationGenerated",
    "SetViewTargetWithBlend",
    "LineTraceSingleByChannel",
    "FMath::Clamp(Profile.HoldSeconds, 0.65f, 2.60f)",
    "CurrentViewTarget != PlayerPawn && CurrentViewTarget != RuntimeCamera",
    "HandleChapterChanged",
]:
    if pg116_symbol not in pg116_director:
        fail(f"PG-116 bounded cinematic camera contract missing: {pg116_symbol}")

pg116_game_mode = read(resolve_source("ShireGameMode.cpp"))
for pg116_symbol in [
    '#include "StoryPresentationDirector.h"',
    "SpawnActor<AStoryPresentationDirector>",
]:
    if pg116_symbol not in pg116_game_mode:
        fail(f"PG-116 presentation director bootstrap missing: {pg116_symbol}")

pg116_npc = read(resolve_source("ShireNPC.cpp"))
pg116_npc_h = read(resolve_source("ShireNPC.h"))
for pg116_symbol in [
    "PerformanceGestureScale",
    "PerformanceGazeScale",
    "PerformanceWeightScale",
    "PerformanceComposure",
    'Name.Equals(TEXT("Boromir"), ESearchCase::IgnoreCase)',
    'Name.Equals(TEXT("Gandalf"), ESearchCase::IgnoreCase)',
    'Name.Equals(TEXT("Legolas"), ESearchCase::IgnoreCase)',
    "WeightShift",
]:
    if pg116_symbol not in (pg116_npc + pg116_npc_h):
        fail(f"PG-116 named-character fallback performance contract missing: {pg116_symbol}")

pg116_audio = read(resolve_source("ShireAudioSubsystem.cpp"))
for pg116_symbol in [
    "FadeOut(0.45f, 0.0f)",
    "FadeIn(0.55f, 1.0f)",
    "FadeOut(0.85f, 0.0f)",
    "FadeIn(0.95f, TargetVolume)",
    "bVoiceActive ? 0.36f : 1.0f",
]:
    if pg116_symbol not in pg116_audio:
        fail(f"PG-116 sonic transition contract missing: {pg116_symbol}")

pg116_arch = json.loads(read(ROOT / "Data" / "SourceArchitecturePlan.json"))
pg116_arch_paths = [
    str(row.get("current_path") or "")
    for row in pg116_arch.get("files", [])
    if isinstance(row, dict)
]
for pg116_resolved in [pg116_director_h, pg116_director_cpp]:
    pg116_path = str(pg116_resolved.relative_to(ROOT)).replace("\\", "/")
    if pg116_arch_paths.count(pg116_path) != 1:
        fail(f"PG-116 source architecture registration must be exactly once: {pg116_path}")

pg116_visual = json.loads(read(ROOT / "Data" / "Part1VisualProductionPass.json"))
if pg116_visual.get("cinematic_character_sonic_v3", {}).get("status") not in {
    "PENDING_EXACT_HEAD_ENGINE_PROOF",
    "EXACT_HEAD_ENGINE_PROOF_GREEN_PR58",
}:
    fail("PG-116 V3 visual evidence boundary changed")

# Existing safety gate remains authoritative while runtime camera grammar grows.
if "FMath::Clamp(ActiveCue.SuggestedDuration, 1.0f, 3.5f)" not in pg102_presentation:
    fail("PG-116 existing 3.5 second cinematic lock safety guard missing")

# PG-117: dedicated Fellowship equipment V4 must remain project-owned, imported and runtime-preferred.
pg117_plan_path = ROOT / "Data" / "HeroCharacterEquipmentSilhouetteV4.json"
if not pg117_plan_path.exists():
    fail("PG-117 HeroCharacterEquipmentSilhouetteV4.json missing")
    pg117_plan = {}
else:
    try:
        pg117_plan = json.loads(read(pg117_plan_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-117 invalid HeroCharacterEquipmentSilhouetteV4.json: {exc}")
        pg117_plan = {}

if pg117_plan.get("plan_id") != "HERO_CHARACTER_EQUIPMENT_SILHOUETTE_V4":
    fail("PG-117 hero-equipment wave identity changed")
if pg117_plan.get("status") != "SOURCE_RUNTIME_IMPLEMENTED_PENDING_EXACT_HEAD_PROOF":
    fail("PG-117 hero-equipment proof boundary changed")
if "HeroCharacterEquipmentSilhouetteV4.json" not in pg93_build:
    fail("PG-117 hero-equipment plan is not packaged")

pg117_assets = {
    "Sam": ["SM_Sam_Sword","SM_Sam_Pack"],
    "Merry": ["SM_Merry_Cloak","SM_Merry_Sword"],
    "Pippin": ["SM_Pippin_Cloak","SM_Pippin_Sword"],
    "Aragorn": ["SM_Aragorn_Cloak","SM_Aragorn_Sword","SM_Aragorn_Bow"],
    "Boromir": ["SM_Boromir_Cloak","SM_Boromir_Sword","SM_Boromir_Shield"],
    "Legolas": ["SM_Legolas_Cloak","SM_Legolas_Bow","SM_Legolas_WhiteKnife"],
    "Gimli": ["SM_Gimli_Axe","SM_Gimli_Beard","SM_Gimli_Helmet"],
}
pg117_asset_count = 0
for pg117_character, pg117_names in pg117_assets.items():
    pg117_root = ROOT / "SourceAssets" / "Production" / "Characters" / pg117_character
    for pg117_name in pg117_names:
        pg117_asset_count += 1
        pg117_path = pg117_root / f"{pg117_name}.obj"
        if not pg117_path.exists():
            fail(f"PG-117 dedicated character asset missing: {pg117_character}/{pg117_name}")
        if pg117_name not in pg116_npc:
            fail(f"PG-117 dedicated character asset not runtime-wired: {pg117_character}/{pg117_name}")
if pg117_asset_count != 18:
    fail("PG-117 dedicated equipment asset contract must remain exactly 18 assets")

for pg117_symbol in [
    "TryDedicatedThenFallback",
    "SM_Sam_Pack",
    "SM_Merry_Cloak",
    "SM_Pippin_Cloak",
    "SM_Aragorn_Sword",
    "SM_Boromir_Shield",
    "SM_Legolas_WhiteKnife",
    "SM_Gimli_Helmet",
]:
    if pg117_symbol not in pg116_npc:
        fail(f"PG-117 dedicated-first runtime identity contract missing: {pg117_symbol}")

pg117_matrix = json.loads(read(ROOT / "Data" / "CharacterProductionMatrix.json"))
pg117_wave = pg117_matrix.get("current_character_wave", {})
if pg117_wave.get("id") != "HERO_CHARACTER_EQUIPMENT_SILHOUETTE_V4":
    fail("PG-117 character production matrix current wave changed")
if pg117_wave.get("added_project_owned_obj_assets") != 18:
    fail("PG-117 character production matrix must retain 18 V4 OBJ assets")

pg117_visual = json.loads(read(ROOT / "Data" / "Part1VisualProductionPass.json"))
# Hero-equipment V4 is a preserved historical production wave, not the global current wave.
# Later world/life waves may legitimately become current without invalidating V4 evidence.
if pg117_visual.get("hero_character_equipment_v4", {}).get("added_project_owned_obj_assets") != 18:
    fail("PG-117 Part I visual plan must retain 18 V4 OBJ assets")

pg117_inventory = json.loads(read(ROOT / "Data" / "ProjectOwnedProductionAssetInventory.json"))
if pg117_inventory.get("totals", {}).get("obj_files", 0) < 352:
    fail("PG-117 project-owned OBJ inventory did not register V4 assets")

# Final skeletal rig handoff must continue to win over modular fallback when valid.
pg117_npc_h = read(resolve_source("ShireNPC.h"))
for pg117_symbol in [
    "bUsingSkeletalProductionRig",
    "TryApplyProductionRig",
]:
    if pg117_symbol not in (pg116_npc + pg117_npc_h):
        fail(f"PG-117 final-rig handoff contract missing: {pg117_symbol}")

# PG-118: chapter streaming V5 must preload asynchronously without exposing a broken narrative seam.
pg118_plan_path = ROOT / "Data" / "ChapterAssetStreamingPlan.json"
if not pg118_plan_path.exists():
    fail("PG-118 ChapterAssetStreamingPlan.json missing")
    pg118_plan = {}
else:
    try:
        pg118_plan = json.loads(read(pg118_plan_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-118 invalid ChapterAssetStreamingPlan.json: {exc}")
        pg118_plan = {}

if pg118_plan.get("plan_id") != "CHAPTER_ASSET_STREAMING_V1":
    fail("PG-118 chapter streaming plan identity changed")
if "ChapterAssetStreamingPlan.json" not in pg93_build:
    fail("PG-118 chapter streaming plan is not packaged")

pg118_banks = pg118_plan.get("banks", {})
for pg118_bank in [
    "P1C01","P1C02","P1C03","P1C04","P1C05","P1C06","P1C07","P1C08","GANDALF_ISENGARD"
]:
    pg118_row = pg118_banks.get(pg118_bank, {})
    if not isinstance(pg118_row, dict) or not pg118_row.get("assets"):
        fail(f"PG-118 chapter streaming bank missing/empty: {pg118_bank}")

pg118_stream_h = read(resolve_source("ShireChapterAssetStreamingSubsystem.h"))
pg118_stream_cpp = read(resolve_source("ShireChapterAssetStreamingSubsystem.cpp"))
pg118_router = read(resolve_source("ChapterWorldRouter.cpp"))
pg118_router_h = read(resolve_source("ChapterWorldRouter.h"))
pg118_fellowship_h = read(resolve_source("FellowshipChapterWorldBuilder.h"))
pg118_fellowship_cpp = read(resolve_source("FellowshipChapterWorldBuilder.cpp"))

for pg118_symbol in [
    "FStreamableManager",
    "RequestAsyncLoad",
    "FSoftObjectPath",
    "ResidentHandle",
    "PendingHandle",
    "OnChapterAssetsReady",
]:
    if pg118_symbol not in (pg118_stream_h + pg118_stream_cpp):
        fail(f"PG-118 async streaming contract missing: {pg118_symbol}")

for pg118_forbidden in [
    "WaitUntilComplete",
    "FlushAsyncLoading",
    "while (!PendingHandle",
]:
    if pg118_forbidden in pg118_stream_cpp:
        fail(f"PG-118 Game-Thread wait pattern forbidden: {pg118_forbidden}")

for pg118_symbol in [
    "router-wait",
    "HandleChapterAssetsReady",
    "CommitChapterWorld",
    "RequestChapterAssets",
    "ClearPrototypeBuilders();",
]:
    if pg118_symbol not in (pg118_router + pg118_router_h):
        fail(f"PG-118 seam-safe router contract missing: {pg118_symbol}")

pg118_wait_index = pg118_router.find("RequestChapterAssets")
pg118_clear_index = pg118_router.find("ClearPrototypeBuilders();", pg118_router.find("void AChapterWorldRouter::CommitChapterWorld"))
if pg118_wait_index < 0 or pg118_clear_index < 0:
    fail("PG-118 router preload/commit ordering cannot be verified")
elif pg118_wait_index > pg118_clear_index:
    fail("PG-118 router clears world before requesting async chapter bank")

for pg118_symbol in [
    "EnsureProductionMeshes(FName ChapterId)",
    'if (ChapterId == TEXT("P1C03"))',
    'else if (ChapterId == TEXT("P1C04"))',
    'else if (ChapterId == TEXT("P1C05"))',
    'else if (ChapterId == TEXT("P1C06"))',
    'else if (ChapterId == TEXT("P1C07"))',
    'else if (ChapterId == TEXT("P1C08"))',
    "EnsureProductionMeshes(ChapterId);",
]:
    if pg118_symbol not in (pg118_fellowship_h + pg118_fellowship_cpp):
        fail(f"PG-118 chapter-aware Fellowship bank contract missing: {pg118_symbol}")

pg118_arch = json.loads(read(ROOT / "Data" / "SourceArchitecturePlan.json"))
pg118_arch_paths = [
    str(row.get("current_path") or "")
    for row in pg118_arch.get("files", [])
    if isinstance(row, dict)
]
for pg118_resolved in [
    resolve_source("ShireChapterAssetStreamingSubsystem.h"),
    resolve_source("ShireChapterAssetStreamingSubsystem.cpp"),
]:
    pg118_path = str(pg118_resolved.relative_to(ROOT)).replace("\\", "/")
    if pg118_arch_paths.count(pg118_path) != 1:
        fail(f"PG-118 source architecture registration must be exactly once: {pg118_path}")

pg118_budget = json.loads(read(ROOT / "Data" / "AssetPerformanceBudget.json"))
if pg118_budget.get("chapter_asset_streaming_v5", {}).get("status") != "SOURCE_RUNTIME_IMPLEMENTED_PENDING_EXACT_HEAD_ENGINE_PROOF_AND_MEASUREMENT":
    fail("PG-118 streaming performance evidence boundary changed")

# PG-121: startup grounding must wait for committed world geometry.
pg121_game_mode = read(resolve_source("ShireGameMode.cpp"))
pg121_router = read(resolve_source("ChapterWorldRouter.cpp"))
pg121_router_h = read(resolve_source("ChapterWorldRouter.h"))
pg121_runtime_smoke = read(ROOT / "Scripts" / "runtime_smoke.py")
if "RUNTIME_SWEEP_SUMMARY" not in pg121_runtime_smoke:
    fail("PG-121 chapter runtime audit must aggregate all chapter failures in one sweep")

if "RestartPlayerAtTransform(PC" in pg121_game_mode or    'SetActorLocationAndRotation(FVector(-2410.0f, -120.0f, 130.0f)' in pg121_game_mode:
    fail("PG-121 GameMode may not teleport the pawn into chapter coordinates before async world commit")

for pg121_symbol in [
    "SetPlayerWorldHold(true);",
    "ResolveGroundedSpawnLocation",
    "LineTraceSingleByChannel",
    "ShireStartupGrounding: PASS",
    "ShireStartupGrounding: FAIL",
]:
    if pg121_symbol not in (pg121_router + pg121_router_h):
        fail(f"PG-121 world-ready grounding contract missing: {pg121_symbol}")

if not mode_has_evidence("startup", "startup.ground_p1c01"):
    fail("PG-121 startup grounding evidence missing")
if not mode_has_evidence("state", "state.ground_p1c03"):
    fail("PG-121 state grounding evidence missing")
if not chapter_has_evidence("grounding"):
    fail("PG-121 chapter sweep grounding evidence missing")

pg121_shire_builder = read(resolve_source("ShirePrototypeWorldBuilder.cpp"))
pg121_fellowship_builder = read(resolve_source("FellowshipChapterWorldBuilder.cpp"))
if "RuntimeCollisionFoundation" not in pg121_shire_builder:
    fail("PG-121 broad Shire fallback collision foundation missing")
for pg121_symbol in [
    "GroundProbeOffsets",
    "OverlapBlockingTestByChannel",
    "FCollisionShape::MakeCapsule",
    "GroundHit.ImpactNormal.Z < 0.55f",
    "adjusted-to-nearby-ground",
]:
    if pg121_symbol not in pg121_router:
        fail(f"PG-121 seam-tolerant grounding invariant missing: {pg121_symbol}")
if "RuntimeSpawnFoundation" in (pg121_shire_builder + pg121_fellowship_builder):
    fail("PG-121 chapter-specific spawn support pads are forbidden; fix grounding at router/world contract level")


# PG-122: automated QA immune-system foundation must stay wired into exact-head UE validation.
pg122_plan_path = ROOT / "Data" / "AutomatedQAPlan.json"
if not pg122_plan_path.exists():
    fail("PG-122 AutomatedQAPlan.json missing")
else:
    try:
        pg122_plan = json.loads(read(pg122_plan_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-122 invalid AutomatedQAPlan.json: {exc}")
        pg122_plan = {}
    if pg122_plan.get("plan_id") != "AUTOMATED_QA_IMMUNE_SYSTEM_V1":
        fail("PG-122 automated QA plan identity changed")

pg122_test_cpp = ROOT / "Source" / "ShireJourneyEditorTools" / "Private" / "Tests" / "ShireQAAutomationTests.cpp"
if not pg122_test_cpp.exists():
    fail("PG-122 ShireQAAutomationTests.cpp missing")
    pg122_tests = ""
else:
    pg122_tests = read(pg122_test_cpp)

for pg122_symbol in [
    "IMPLEMENT_SIMPLE_AUTOMATION_TEST",
    "ShireJourney.QA.Save.DefaultState",
    "ShireJourney.QA.Assets.StreamingBankPackages",
    "FPackageName::DoesPackageExist",
]:
    if pg122_symbol not in pg122_tests:
        fail(f"PG-122 Automation Framework contract missing: {pg122_symbol}")

pg122_runner = read(ROOT / "Scripts" / "ci_run_project_automation.cmd")
pg122_parser = read(ROOT / "Scripts" / "parse_automation_report.py")
pg122_workflow = read(ROOT / ".github" / "workflows" / "unreal-build-validation.yml")
for pg122_symbol in [
    "Automation RunTests ShireJourney.QA",
    "ReportOutputPath",
    "parse_automation_report.py",
]:
    if pg122_symbol not in pg122_runner:
        fail(f"PG-122 automation runner contract missing: {pg122_symbol}")
if "Run ShireJourney Automation Framework QA" not in pg122_workflow:
    fail("PG-122 Unreal workflow does not execute project automation QA")
if "AUTOMATION_SUITE_PASS" not in pg122_parser:
    fail("PG-122 automation report fail-closed parser missing")

pg122_router = read(resolve_source("ChapterWorldRouter.cpp"))
for pg122_symbol in [
    "ShireStartupGrounding: PLACED",
    "VerifyPlayerGroundingStability",
    "stableSeconds=2.0",
    "Movement->IsFalling()",
]:
    if pg122_symbol not in pg122_router:
        fail(f"PG-122 delayed grounding stability proof missing: {pg122_symbol}")


# PG-123: comprehensive transactional world-commit contract.
pg123_router_h = read(resolve_source("ChapterWorldRouter.h"))
pg123_router = read(resolve_source("ChapterWorldRouter.cpp"))
pg123_stream_h = read(resolve_source("ShireChapterAssetStreamingSubsystem.h"))
pg123_stream = read(resolve_source("ShireChapterAssetStreamingSubsystem.cpp"))
pg123_life_h = read(resolve_source("LivingWorldDirector.h"))
pg123_life = read(resolve_source("LivingWorldDirector.cpp"))

for pg123_symbol in [
    "CommitPendingRequest",
    "awaiting-world-commit",
    "ResidentHandle = PendingHandle",
]:
    if pg123_symbol not in (pg123_stream_h + pg123_stream):
        fail(f"PG-123 two-phase asset commit contract missing: {pg123_symbol}")

for pg123_symbol in [
    "IsWorldCommitted",
    "WorldRevision",
    "RollbackFailedWorldSwap",
    "ShireWorldCommit: PASS",
    "OnWorldCommitted.Broadcast",
]:
    if pg123_symbol not in (pg123_router_h + pg123_router):
        fail(f"PG-123 transactional world commit contract missing: {pg123_symbol}")

for pg123_symbol in [
    "SynchronizeCommittedWorld",
    "GetAppliedWorldRevision",
    "LivingWorldCommitSync",
    "LivingWorldManaged",
]:
    if pg123_symbol not in (pg123_life_h + pg123_life):
        fail(f"PG-123 committed living-world synchronization missing: {pg123_symbol}")

if "ActiveChapterId = NewChapterId;\n    ResetForCurrentChapter();" in pg123_life:
    fail("PG-123 LivingWorldDirector may not reset directly from requested quest chapter before world commit")

# PG-124: continuous transition audit must remain wired with startup grounding.
pg124_game_mode = read(resolve_source("ShireGameMode.cpp"))
pg124_runtime = read(ROOT / "Scripts" / "runtime_smoke.py")
pg124_runtime_tests = read(ROOT / "Scripts" / "test_runtime_smoke.py")
pg124_state_cmd = read(ROOT / "Scripts" / "ci_runtime_state.cmd")

for pg124_symbol in [
    "AuditTransitions",
    "GetAppliedWorldRevision",
    "GetWorldRevision",
]:
    if pg124_symbol not in pg124_game_mode:
        fail(f"PG-124 continuous transition GameMode audit missing: {pg124_symbol}")

if "-AuditTransitions" not in MODE_EXTRA_ARGS.get("transitions", ()):
    fail("PG-124 central runtime contract lost transition execution")
for pg124_evidence in ["transition.barrier", "transition.sequence"]:
    if not mode_has_evidence("transitions", pg124_evidence):
        fail(f"PG-124 central runtime contract lost transition evidence: {pg124_evidence}")

if "--mode transitions" not in pg124_state_cmd:
    fail("PG-124 state CI does not execute continuous transition audit")

if "test_separate_chapter_success_does_not_prove_continuous_transitions" not in pg124_runtime_tests:
    fail("PG-124 unit regression for continuous transition evidence missing")

# PG-127: generated/edited C++ source must not contain escaped newline artifacts.
for escaped_newline in ("\\\\n", "\\r\\n"):
    if escaped_newline in production_import_cpp:
        fail("PG-127 production importer contains literal escaped newline text in C++ source")

# PG-128: W00 commit-bound residency, movement and audio invariants.
pg128_player_h = read(resolve_source("ShirePlayerCharacter.h"))
pg128_player = read(resolve_source("ShirePlayerCharacter.cpp"))
pg128_game_mode = read(resolve_source("ShireGameMode.cpp"))
pg128_router = read(resolve_source("ChapterWorldRouter.cpp"))
pg128_stream_h = read(resolve_source("ShireChapterAssetStreamingSubsystem.h"))
pg128_stream = read(resolve_source("ShireChapterAssetStreamingSubsystem.cpp"))
pg128_audio_h = read(resolve_source("ShireAudioSubsystem.h"))
pg128_audio = read(resolve_source("ShireAudioSubsystem.cpp"))

for pg128_symbol in [
    "OnChapterAssetsCommitted",
    "HandleChapterAssetsCommitted",
]:
    if pg128_symbol not in (pg128_player_h + pg128_player + pg128_stream_h + pg128_stream):
        fail(f"PG-128 committed-residency surface contract missing: {pg128_symbol}")

if "OnChapterAssetsCommitted.Broadcast(ChapterId, RouteId);" not in pg128_stream:
    fail("PG-128 chapter bank does not publish post-residency commit")

if "reason=world-commit-timeout" not in pg128_game_mode or "IsWorldCommitted(" not in pg128_game_mode:
    fail("PG-128 state/save audit must wait for committed world")

surface_fail = pg128_player.find("CharacterSurfaceAudit: FAIL")
surface_disk = pg128_player.find("UGameInstance* GI = GetGameInstance();", surface_fail)
if surface_fail < 0 or surface_disk < 0:
    fail("PG-128 character surface/disk audit structure missing")
elif "return false;" in pg128_player[surface_fail:surface_disk]:
    fail("PG-128 surface audit may not mask the independent disk-save roundtrip")

move_start = pg128_router.find("bool AChapterWorldRouter::MovePlayerToChapterStart")
move_end = pg128_router.find("void AChapterWorldRouter::VerifyPlayerGroundingStability", move_start)
if move_start < 0 or move_end < 0:
    fail("PG-128 cannot inspect chapter-start movement hold")
elif "SetPlayerWorldHold(false);" in pg128_router[move_start:move_end]:
    fail("PG-128 movement may not unlock before world/context commit")

commit_start = pg128_router.find("void AChapterWorldRouter::CommitChapterWorld")
if commit_start < 0:
    fail("PG-128 normal world commit function missing")
else:
    commit_body = pg128_router[commit_start:]
    if "grounding-barrier-pending" not in commit_body:
        fail("PG-128 normal world commit must enter the grounding barrier before publication")
    if "SetPlayerWorldHold(false);" in commit_body:
        fail("PG-128 normal world commit setup may not release movement before grounding finalization")

finalize_start = pg128_router.find("void AChapterWorldRouter::VerifyPlayerGroundingStability")
finalize_end = pg128_router.find("void AChapterWorldRouter::LoadChapterWorld", finalize_start)
finalize_body = (
    pg128_router[finalize_start:finalize_end]
    if finalize_start >= 0 and finalize_end >= 0
    else ""
)
finalize_broadcast = finalize_body.find("OnWorldCommitted.Broadcast(WorldRevision);")
finalize_release = finalize_body.find("SetPlayerWorldHold(false);", finalize_broadcast)
if finalize_broadcast < 0 or finalize_release < 0 or finalize_release < finalize_broadcast:
    fail("PG-128 grounding finalization must broadcast world commit before movement release")

rollback_start = pg128_router.find("bool AChapterWorldRouter::RestoreCommittedWorldFromSnapshot")
rollback_end = pg128_router.find("void AChapterWorldRouter::RollbackFailedWorldSwap", rollback_start)
rollback_body = pg128_router[rollback_start:rollback_end] if rollback_start >= 0 and rollback_end >= 0 else ""
rollback_broadcast = rollback_body.find("OnWorldCommitted.Broadcast(WorldRevision);")
rollback_release = rollback_body.find("SetPlayerWorldHold(false);", rollback_broadcast)
if rollback_broadcast < 0 or rollback_release < 0 or rollback_release < rollback_broadcast:
    fail("PG-128 rollback commit must broadcast restored context before movement release")

for pg128_symbol in [
    "FStreamableManager",
    "RequestAsyncLoad",
    "PendingAudioLoads",
    "TWeakObjectPtr<USoundBase>",
    "HandleAsyncAudioReady",
    "CancelPendingAudioCategory",
]:
    if pg128_symbol not in (pg128_audio_h + pg128_audio):
        fail(f"PG-128 bounded async audio ownership missing: {pg128_symbol}")
if "LoadObject<USoundBase>" in pg128_audio:
    fail("PG-128 synchronous production audio loading is forbidden")


# PG-144: warehouse staging is bounded/resumable and runs only on the supervised
# Windows runner under a dedicated warehouse concurrency group.
pg144_helper = read(ROOT / "Scripts" / "warehouse_network.ps1")
pg144_workflow = read(ROOT / ".github" / "workflows" / "warehouse-stage.yml")
pg144_scripts = [
    ROOT / "Scripts" / "stage_polyhaven_warehouse.ps1",
    ROOT / "Scripts" / "stage_opengameart_audio.ps1",
    ROOT / "Scripts" / "stage_quaternius_warehouse.ps1",
    ROOT / "Scripts" / "stage_ambientcg_warehouse.ps1",
    ROOT / "Scripts" / "stage_kenney_warehouse.ps1",
    ROOT / "Scripts" / "stage_kaykit_github_warehouse.ps1",
]
for pg144_symbol in [
    "Invoke-WarehouseRestJson",
    "Invoke-WarehousePage",
    "Invoke-WarehouseDownload",
    "Test-WarehouseReceiptReusable",
    "-TimeoutSec",
    ".partial",
    "WAREHOUSE_NET",
]:
    if pg144_symbol not in pg144_helper:
        fail(f"PG-144 warehouse network helper missing: {pg144_symbol}")
for pg144_path in pg144_scripts:
    pg144_text = read(pg144_path)
    if "warehouse_network.ps1" not in pg144_text:
        fail(f"PG-144 provider script does not import bounded network helper: {pg144_path.name}")
    if "Test-WarehouseReceiptReusable" not in pg144_text:
        fail(f"PG-144 provider script lacks persistent receipt reuse: {pg144_path.name}")
    if re.search(r"\bInvoke-(?:WebRequest|RestMethod)\b", pg144_text):
        fail(f"PG-144 provider script bypasses bounded network helper: {pg144_path.name}")
for pg144_symbol in [
    "- develop",
    "- self-hosted",
    "- Windows",
    "- X64",
    "- ue4-27",
    "group: warehouse-stage-${{ github.repository }}",
    "cancel-in-progress: true",
    "warehouse_network.ps1",
    "WAREHOUSE_CHECKOUT_PASS",
]:
    if pg144_symbol not in pg144_workflow:
        fail(f"PG-144 warehouse supervised-runner guard missing: {pg144_symbol}")
if "runs-on: ubuntu-latest" in pg144_workflow or "runs-on: windows-latest" in pg144_workflow:
    fail("PG-144 warehouse staging must not depend on GitHub-hosted capacity")
if pg144_workflow.count("- self-hosted") != 1:
    fail("PG-144 exactly one warehouse job must own the supervised runner")
if "integration/comprehensive-foundation-v1" in pg144_workflow:
    fail("PG-144 warehouse workflow still targets an obsolete integration branch")

# PG-145: self-hosted Windows warehouse execution and runner supervision are explicit.
pg145_workflow = pg144_workflow
if "shell: powershell\n" in pg145_workflow:
    fail("PG-145 raw powershell shell can be blocked by the runner execution policy")
if pg145_workflow.count("powershell.exe -NoProfile -ExecutionPolicy Bypass") < 9:
    fail("PG-145 warehouse PowerShell work must execute through explicit Bypass wrappers")
for pg145_checkout_symbol in [
    "Checkout exact warehouse head",
    "Fetching exact warehouse head attempt",
    "fetch --no-tags --prune --depth=2",
    "WAREHOUSE_CHECKOUT_PASS",
]:
    if pg145_checkout_symbol not in pg145_workflow:
        fail(f"PG-145 resilient warehouse checkout missing: {pg145_checkout_symbol}")
if "  delta:" in pg145_workflow or "needs.delta" in pg145_workflow:
    fail("PG-145 obsolete hosted warehouse delta job was reintroduced")
if "  stage:" not in pg145_workflow:
    fail("PG-145 supervised warehouse stage job missing")
if "uses: actions/checkout@" in pg145_workflow:
    fail("PG-145 self-hosted warehouse stage must not depend on marketplace checkout download")

pg145_watchdog = read(ROOT / "Scripts" / "runner_watchdog.ps1")
pg145_watchdog_timestamp = read(ROOT / "Scripts" / "runner_log_timestamp.ps1")
pg145_watchdog_contract = pg145_watchdog + "\n" + pg145_watchdog_timestamp
pg145_watchdog_installer = read(ROOT / "Scripts" / "install_runner_watchdog.ps1")
for pg145_symbol in [
    "Acknowledging runner request",
    "Runner.Listener",
    "Runner.Worker",
    "AcquireHangSeconds",
    "SHIRE_RUNNER_WATCHDOG_RECOVERY",
    "Recover-OrphanedListenerOnSupervisorBoot",
    "SHIRE_RUNNER_WATCHDOG_BOOT_RECOVERY",
]:
    if pg145_symbol not in pg145_watchdog_contract:
        fail(f"PG-145 runner watchdog contract missing: {pg145_symbol}")
pg145_timeout = re.search(r"\[int\]\$AcquireHangSeconds\s*=\s*(\d+)", pg145_watchdog)
if not pg145_timeout or not (110 <= int(pg145_timeout.group(1)) <= 180):
    fail("PG-145 runner acquire watchdog must recover within 110-180 seconds")
for pg145_install_symbol in [
    "ShireJourney-GitHubRunner-Watchdog",
    "New-ScheduledTaskTrigger -AtLogOn",
    "RepetitionInterval (New-TimeSpan -Minutes 5)",
    "$taskTriggers",
    "MultipleInstances IgnoreNew",
    "-LogonType Interactive",
    "runner_service_guard.ps1",
    "serviceOwnership=absent-or-disabled-stopped",
    "actions.runner.*",
    "NETWORK SERVICE",
]:
    if pg145_install_symbol not in pg145_watchdog_installer:
        fail(f"PG-145 runner watchdog installer contract missing: {pg145_install_symbol}")

pg145_classifier = read(ROOT / "Scripts" / "classify_unreal_validation.ps1")
for pg145_classifier_symbol in [
    "Test-NearestSafeCoreAncestorGreen",
    "Test-CoreProofSafeInterveningDelta",
    "TRANSITIVE_CORE_PROOF_PASS",
    "runtime-or-asset-delta-inherits-nearest-safe-core-ancestor-no-package",
    "TRANSITIVE_CORE_PROOF_BLOCKED",
    'Set-Mode "asset"',
    "SHIRE_ASSET_IMPORT_ONLY",
    "editor-tool-or-p1c01-material-delta-build-import-startup-only",
    "ANCESTOR_HISTORY_FETCH_REQUIRED",
]:
    if pg145_classifier_symbol not in pg145_classifier:
        fail(f"PG-145 transitive core-proof optimization missing: {pg145_classifier_symbol}")

pg145_unreal_workflow = read(ROOT / ".github" / "workflows" / "unreal-build-validation.yml")
for pg145_hosted_classifier_symbol in [
    "Hosted Unreal lane classifier",
    "fetch-depth: 0",
    "needs.classify.outputs.mode != 'inherit'",
]:
    if pg145_hosted_classifier_symbol not in pg145_unreal_workflow:
        fail(f"PG-145 hosted Unreal preflight contract missing: {pg145_hosted_classifier_symbol}")
for pg145_maintenance_path in [
    "Scripts/classify_unreal_validation.ps1",
    "Scripts/runner_watchdog.ps1",
    "Scripts/runner_log_timestamp.ps1",
    "Scripts/test_runner_watchdog_timestamp.ps1",
    "Scripts/runner_service_guard.ps1",
    "Scripts/install_runner_watchdog.ps1",
    "Scripts/pre_unreal_validate.py",
    "Scripts/asset_quality_audit.py",
    "Scripts/test_asset_quality_audit.py",
    "Scripts/runtime_smoke.py",
    "Scripts/test_runtime_smoke.py",
    "Scripts/verify_runner_session.ps1",
]:
    if pg145_unreal_workflow.count(pg145_maintenance_path) < 2:
        fail(f"PG-145 maintenance path must stay off Unreal device lane in push and PR filters: {pg145_maintenance_path}")


# PG-145B: every self-hosted lane must fail fast when the runner falls back to a service
# identity or loses its interactive desktop/watchdog ownership.
pg145b_probe = read(ROOT / "Scripts" / "verify_runner_session.ps1")
for pg145b_symbol in [
    "NETWORK SERVICE",
    "SessionId",
    "Runner.Listener.exe",
    "Runner.Worker.exe",
    "actions.runner.*",
    "ShireJourney-GitHubRunner-Watchdog",
    "System.Net.Sockets.TcpClient",
    "ConnectAsync(\"github.com\", 443)",
    "RUNNER_HEALTH_NETWORK_ATTEMPT",
    "$NetworkProbeAttempts = 3",
    "$NetworkProbeTimeoutMilliseconds = 5000",
    "RUNNER_HEALTH_PASS",
]:
    if pg145b_symbol not in pg145b_probe:
        fail(f"PG-145B runner health probe missing: {pg145b_symbol}")

pg145b_watchdog = read(ROOT / "Scripts" / "runner_watchdog.ps1")
for pg145b_watchdog_symbol in [
    "WorkerIdleHangSeconds",
    "Listening for Jobs",
    "stale-worker",
]:
    if pg145b_watchdog_symbol not in pg145b_watchdog:
        fail(f"PG-145B runner watchdog recovery contract missing: {pg145b_watchdog_symbol}")

pg145b_service_guard = read(ROOT / "Scripts" / "runner_service_guard.ps1")
for pg145b_service_guard_symbol in [
    "actions.runner.*",
    "StartupType Disabled",
    "sc.exe delete",
    "NETWORK SERVICE",
    "LOCAL SERVICE",
    "SYSTEM",
    "RUNNER_SERVICE_GUARD_PASS",
]:
    if pg145b_service_guard_symbol not in pg145b_service_guard:
        fail(f"PG-145B permanent runner service guard missing: {pg145b_service_guard_symbol}")

pg145b_installer = read(ROOT / "Scripts" / "install_runner_watchdog.ps1")
for pg145b_installer_symbol in [
    "runner_service_guard.ps1",
    "installedServiceGuard",
    "serviceOwnership=absent-or-disabled-stopped",
]:
    if pg145b_installer_symbol not in pg145b_installer:
        fail(f"PG-145B watchdog installer must permanently exclude service mode: {pg145b_installer_symbol}")

for pg145b_watchdog_service_symbol in [
    "ServiceGuardPath",
    "Invoke-ServiceOwnershipGuard",
]:
    if pg145b_watchdog_service_symbol not in pg145b_watchdog:
        fail(f"PG-145B watchdog must continuously enforce service exclusion: {pg145b_watchdog_service_symbol}")

for pg145b_probe_service_symbol in [
    "legacyService=",
    "stopped-disabled",
]:
    if pg145b_probe_service_symbol not in pg145b_probe:
        fail(f"PG-145B runner health must require service absent/disabled: {pg145b_probe_service_symbol}")


pg145b_health_workflow = read(ROOT / ".github" / "workflows" / "runner-health.yml")
if "workflow_dispatch:" not in pg145b_health_workflow or "verify_runner_session.ps1" not in pg145b_health_workflow:
    fail("PG-145B manual runner health workflow is incomplete")

for pg145b_path, pg145b_before in [
    (ROOT / ".github" / "workflows" / "unreal-build-validation.yml", "Import hosted Unreal classification"),
    (ROOT / ".github" / "workflows" / "warehouse-stage.yml", "Stage Poly Haven CC0 batch"),
]:
    pg145b_text = read(pg145b_path)
    probe_pos = pg145b_text.find("verify_runner_session.ps1")
    work_pos = pg145b_text.find(pg145b_before)
    if probe_pos < 0 or work_pos < 0 or probe_pos > work_pos:
        fail(f"PG-145B runner health gate must precede heavy work: {pg145b_path.name}")

# PG-183: service mode must be impossible to silently resurrect.
pg183_guard = read(ROOT / "Scripts" / "runner_service_guard.ps1")
for pg183_symbol in [
    'Get-Service -Name "actions.runner.*"',
    "StartupType Disabled",
    "sc.exe delete",
    "NETWORK SERVICE",
    "LOCAL SERVICE",
    "SYSTEM",
    "RUNNER_SERVICE_GUARD_PASS",
]:
    if pg183_symbol not in pg183_guard:
        fail(f"PG-183 permanent runner service guard missing: {pg183_symbol}")
for pg183_symbol in [
    "runner_service_guard.ps1",
    "Invoke-RunnerServiceGuard",
    "SHIRE_RUNNER_WATCHDOG_SERVICE_GUARD_TRIGGER",
]:
    if pg183_symbol not in pg145_watchdog:
        fail(f"PG-183 watchdog self-heal contract missing: {pg183_symbol}")
for pg183_symbol in [
    "runner_service_guard.ps1",
    "serviceOwnership=absent-or-disabled-stopped",
]:
    if pg183_symbol not in pg145_watchdog_installer:
        fail(f"PG-183 installer purge contract missing: {pg183_symbol}")
for pg183_symbol in [
    'StartMode -ne "Disabled"',
    "legacyService=",
    '"absent"',
    '"stopped-disabled"',
]:
    if pg183_symbol not in pg145b_probe:
        fail(f"PG-183 runner verification contract missing: {pg183_symbol}")


# PG-145C: editor-tool/material-authoring deltas use the narrow exact-head engine lane:
# build + import + automation + startup, without unrelated chapter/state/package repetition.
pg145c_workflow = pg145_unreal_workflow
for pg145c_symbol in [
    "SHIRE_ASSET_IMPORT_ONLY",
    "ASSET_IMPORT_ONLY_FILE",
    "editor-tool-or-p1c01-material-delta-build-import-startup-only",
]:
    if pg145c_symbol not in (pg145_classifier + pg145c_workflow):
        fail(f"PG-145C fast asset-import lane missing: {pg145c_symbol}")
pg145c_reset_pos = pg145c_workflow.find("- name: Reset project build intermediates")
pg145c_reset_slice = pg145c_workflow[pg145c_reset_pos:pg145c_reset_pos + 420] if pg145c_reset_pos >= 0 else ""
if pg145c_reset_pos < 0 or "if: env.SHIRE_RESET_INTERMEDIATES == 'true'" not in pg145c_reset_slice:
    fail("PG-145C project intermediate reset must be gated only by the classifier clean-compile flag")
for pg145c_symbol in [
    "SHIRE_RESET_INTERMEDIATES=",
    "CLEAN_COMPILE_REQUIRED reason=build-rules-or-project-descriptor",
]:
    if pg145c_symbol not in pg145_classifier:
        fail(f"PG-145C clean-compile classifier contract missing: {pg145c_symbol}")
for pg145c_step in [
    "Headless chapter-by-chapter runtime audit",
    "Headless route/story state roundtrip audit",
    "Summarize and guard runtime warning debt",
]:
    pg145c_pos = pg145c_workflow.find("- name: " + pg145c_step)
    pg145c_slice = pg145c_workflow[pg145c_pos:pg145c_pos + 420] if pg145c_pos >= 0 else ""
    if "SHIRE_ASSET_IMPORT_ONLY != 'true'" not in pg145c_slice:
        fail(f"PG-145C asset-import lane still repeats unrelated runtime audit: {pg145c_step}")

# PG-176: lightweight/admin lanes must never destroy the Unreal build workspace.
pg176_pre = read(ROOT / ".github" / "workflows" / "pre-unreal-validation.yml")
pg176_health = read(ROOT / ".github" / "workflows" / "runner-health.yml")
pg176_cleanup = read(ROOT / ".github" / "workflows" / "branch-cleanup.yml")
pg176_warehouse = read(ROOT / ".github" / "workflows" / "warehouse-stage.yml")

for pg176_symbol in [
    "runs-on: windows-latest",
    "%RUNNER_TEMP%\\shire-pre-unreal",
    "SHIRE_PRE_ROOT",
    "PRE_UNREAL_EXACT_CHECKOUT_PASS",
    "isolated=true",
    "hosted=true",
]:
    if pg176_symbol not in pg176_pre:
        fail(f"PG-176 Pre-Unreal hosted isolated checkout contract missing: {pg176_symbol}")
for pg176_legacy_symbol in [
    "C:\\actions-runner\\_ci\\pre-unreal",
    "persistent=true",
]:
    if pg176_legacy_symbol in pg176_pre:
        fail(f"PG-176 Pre-Unreal must not restore legacy persistent self-hosted checkout semantics: {pg176_legacy_symbol}")
if 'rmdir /S /Q "%GITHUB_WORKSPACE%"' in pg176_pre:
    fail("PG-176 Pre-Unreal may not delete the Unreal workspace")

for pg176_symbol in [
    "runs-on: windows-latest",
    "%RUNNER_TEMP%\\shire-branch-cleanup-",
    "SHIRE_CLEANUP_ROOT",
    "BRANCH_CLEANUP_EXACT_CHECKOUT_PASS",
    "isolated=true",
    "hosted=true",
]:
    if pg176_symbol not in pg176_cleanup:
        fail(f"PG-176 branch-cleanup hosted isolated checkout contract missing: {pg176_symbol}")
if "- self-hosted" in pg176_cleanup:
    fail("PG-176 branch cleanup is administrative and must not occupy the supervised UE4 runner")
if 'rmdir /S /Q "%GITHUB_WORKSPACE%"' in pg176_cleanup:
    fail("PG-176 branch cleanup may not delete the Unreal workspace")

for pg176_symbol in [
    "%RUNNER_TEMP%\\shire-runner-health-",
    "SHIRE_HEALTH_ROOT",
    "isolated=true",
]:
    if pg176_symbol not in pg176_health:
        fail(f"PG-176 runner-health isolated checkout contract missing: {pg176_symbol}")
if 'rmdir /S /Q "%GITHUB_WORKSPACE%"' in pg176_health:
    fail("PG-176 runner-health may not delete the Unreal workspace")

for pg176_symbol in [
    "%RUNNER_TEMP%\\shire-warehouse-src-",
    "SHIRE_WAREHOUSE_SOURCE",
    "WAREHOUSE_CHECKOUT_PASS",
    "isolated=true",
]:
    if pg176_symbol not in pg176_warehouse:
        fail(f"PG-176 warehouse isolated source checkout contract missing: {pg176_symbol}")
if 'if exist ".git" rmdir /S /Q ".git"' in pg176_warehouse:
    fail("PG-176 warehouse staging may not destroy the Unreal workspace Git metadata")

# PG-146: route/chapter/episode/character identity is one fail-closed contract.
pg146_quest_h = read(resolve_source("ShireQuestSubsystem.h"))
pg146_quest = read(resolve_source("ShireQuestSubsystem.cpp"))
pg146_player_h = read(resolve_source("ShirePlayerCharacter.h"))
pg146_player = read(resolve_source("ShirePlayerCharacter.cpp"))
pg146_game_mode = read(resolve_source("ShireGameMode.cpp"))
for pg146_symbol in [
    "NormalizeExperienceIdentity",
    "CanonicalizeRestoredExperienceIdentity",
    "SanitizeRouteProgressMap",
    "ShireExperienceIdentity: rejected source=StartExperience",
    "ShireExperienceIdentity: rejected source=StartChapter",
]:
    if pg146_symbol not in (pg146_quest_h + pg146_quest):
        fail(f"PG-146 experience identity contract missing: {pg146_symbol}")
if "CanonicalizeRestoredExperienceIdentity(" not in pg146_player:
    fail("PG-146 save restore does not canonicalize identity before transaction publication")
for pg146_evidence in ["state.identity_guard", "edge.identity_restore"]:
    if not mode_has_evidence("state" if pg146_evidence.startswith("state.") else "edges", pg146_evidence):
        fail(f"PG-146 runtime identity evidence missing: {pg146_evidence}")
if "TEXT(\"P1G01\"), TEXT(\"IsengardCounsel\"), 1" in pg146_game_mode and    "direct-invalid-rejected=yes" not in pg146_game_mode:
    fail("PG-146 P1G01 chapter shorthand may appear only inside the explicit rejection audit")

# PG-147: every runtime JSON literal must be declared as a staged RuntimeDependency.
pg147_build = read(resolve_source("ShireJourney.Build.cs"))
pg147_runtime_json = set()
for pg147_path in SOURCE.rglob("*.cpp"):
    for pg147_name in re.findall(r'Data/([A-Za-z0-9_.-]+\.json)', read(pg147_path)):
        pg147_runtime_json.add(pg147_name)
for pg147_name in sorted(pg147_runtime_json):
    pg147_relative = f"Data/{pg147_name}"
    if not has_nonufs_runtime_dependency(pg147_build, pg147_relative):
        fail(
            f"PG-147 runtime JSON is not staged as project-relative NonUFS data: {pg147_name}"
        )

# PG-148: a real queued AsyncSaveGame race must cross a committed world revision inertly.
for pg148_symbol in [
    "RunQueuedCheckpointRevisionRaceAuditSetup",
    "FinalizeCheckpointSaveComplete",
    "CIAuditQueuedCheckpointOriginRevision",
    "AsyncSaveGameToSlot",
    "callback-deferred",
]:
    if pg148_symbol not in (pg146_player_h + pg146_player):
        fail(f"PG-148 queued checkpoint race contract missing: {pg148_symbol}")
if not mode_has_evidence("edges", "edge.queued_checkpoint_race"):
    fail("PG-148 queued checkpoint race runtime evidence missing")
if "RunMalformedExperienceRestoreAuditSetup" not in pg146_player:
    fail("PG-148 persistence-edge sequence must exercise malformed restore before async race")


# PG-149: transition-order validation checks protected member mutations, not exact RHS spelling.
pg149_self = read(ROOT / "Scripts" / "pre_unreal_validate.py")
pg149_tests = read(ROOT / "Scripts" / "test_source_contracts.py")
pg149_workflow = read(ROOT / ".github" / "workflows" / "pre-unreal-validation.yml")
if "from source_contracts import signal_precedes_member_mutation" not in pg149_self:
    fail("PG-149 Pre-Unreal must consume the structural transition-order helper")
if re.search(r'\.find\(["\']Current(?:Chapter|Route|Episode)Id\s*=', pg149_self):
    fail("PG-149 transition-order guards may not hard-code an assignment RHS")
for pg149_symbol in [
    "test_transition_signal_accepts_alias_rhs",
    "test_transition_signal_rejects_mutation_first",
    "test_comments_and_strings_do_not_fake_mutation",
    "test_nested_route_progress_write_is_not_authoritative_mutation",
    "test_explicit_this_member_still_counts_as_authoritative_mutation",
]:
    if pg149_symbol not in pg149_tests:
        fail(f"PG-149 source-contract regression test missing: {pg149_symbol}")
if "test_source_contracts.py" not in pg149_workflow:
    fail("PG-149 Pre-Unreal workflow must execute source-contract regression tests")


# PG-191: Generated source publication must lease the authoritative remote SHA.
pg191_export = read(ROOT / "Scripts" / "export_p1c01_material_source_branch.ps1")
for pg191_symbol in [
    "ls-remote --heads origin $remoteRef",
    "--force-with-lease=",
    "P1C01_MATERIAL_SOURCE_PUBLISH_LEASE",
    "P1C01_MATERIAL_SOURCE_PUBLISH_CREATE",
    "generated material branch push failed after explicit remote-SHA lease",
    "-c credential.helper=",
    "P1C01_MATERIAL_SOURCE_REMOTE_LOOKUP",
    "attempts=3",
    "$remoteLines=@(& $git",
]:
    if pg191_symbol not in pg191_export:
        fail(f"PG-191 explicit generated-branch publish contract missing: {pg191_symbol}")
if "push --force-with-lease origin" in pg191_export:
    fail("PG-191 implicit force-with-lease returned; generated branches must lease the exact remote SHA")


# PG-192: P1C01 Chapter Closure Mega Pack V2 maximum-throughput contract.
pg192_pack = json.loads(read(ROOT / "Data" / "P1C01ChapterClosureMegaPackV2.json"))
pg192_promo = json.loads(read(ROOT / "Data" / "WarehouseP1C01ClosurePromotionTrainV2.json"))
pg192_mat = json.loads(read(ROOT / "Data" / "P1C01MaterialImportWaveV2.json"))
pg192_runner = read(ROOT / "Scripts" / "run_p1c01_chapter_closure_pack_v2.ps1")
pg192_preflight = read(ROOT / "Scripts" / "preflight_p1c01_chapter_closure_pack_v2.ps1")
pg192_closure_workflow = read(ROOT / ".github" / "workflows" / "p1c01-chapter-closure.yml")
pg192_warehouse = read(ROOT / ".github" / "workflows" / "warehouse-stage.yml")
pg192_unreal = read(ROOT / ".github" / "workflows" / "unreal-build-validation.yml")

if pg192_pack.get("status") != "RUNNER_EXECUTION_READY":
    fail("PG-192 closure pack must remain RUNNER_EXECUTION_READY")
if int(pg192_pack.get("source_capacity", {}).get("promotion_selector_ceiling", 0)) < 150:
    fail("PG-192 closure promotion ceiling unexpectedly reduced below chapter-scale throughput")
if int(pg192_pack.get("storage_policy", {}).get("minimum_free_disk_reserve_bytes", 0)) < 4294967296:
    fail("PG-192 closure pack must retain at least a 4 GiB free-space reserve")
pg192_cars = {x.get("id"): x for x in pg192_pack.get("cars", [])}
for required in ["PREFLIGHT_STORAGE","STAGE_POLYHAVEN","STAGE_AMBIENTCG","STAGE_QUATERNIUS","STAGE_KENNEY","STAGE_KAYKIT","STAGE_AUDIO","INVENTORY_AUDIT","CRITICAL_GAP_PREP","MEGA_PROMOTION","MATERIAL_SOURCE_EXPORT","CHARACTER_INTAKE","FINAL_INVENTORY_AUDIT"]:
    if required not in pg192_cars:
        fail(f"PG-192 closure pack car missing: {required}")
pg192_budget = pg192_cars.get("MATERIAL_SOURCE_EXPORT", {}).get("export_budget", {})
if int(pg192_budget.get("max_batch_source_bytes", 0)) != 671088640:
    fail("PG-192 material source promotion must remain bounded at 640 MiB")
if int(pg192_budget.get("minimum_exported_materials", 0)) < 18:
    fail("PG-192 large material wave minimum unexpectedly reduced")
if len(pg192_mat.get("immediate_open_source_items", [])) < 24:
    fail("PG-192 material closure wave must remain chapter-scale")
if int(pg192_promo.get("selector_ceiling_total", 0)) < 150:
    fail("PG-192 promotion selector ceiling unexpectedly reduced")
for symbol in ["P1C01_CHAPTER_CLOSURE_PACK_V2_PASS","QUARANTINED_CONTINUE","P1C01_CLOSURE_PACK_STORAGE_PASS","Invoke-ChildPowerShell","child PowerShell failed exit="]:
    if symbol not in pg192_runner:
        fail(f"PG-192 closure runner marker missing: {symbol}")
for symbol in ["P1C01_CLOSURE_PREFLIGHT_PASS","CLOSURE_PREFLIGHT_DISK_RESERVE_FAIL","System.Management.Automation.Language.Parser"]:
    if symbol not in pg192_preflight:
        fail(f"PG-192 closure preflight marker missing: {symbol}")
for symbol in [
    "name: P1C01 Chapter Closure Pack",
    "cancel-in-progress: false",
    "timeout-minutes: 180",
    "Fast closure preflight",
    "Run P1C01 Chapter Closure Mega Pack V2",
]:
    if symbol not in pg192_closure_workflow:
        fail(f"PG-192 dedicated closure workflow contract missing: {symbol}")
for symbol in [
    "group: warehouse-stage-${{ github.repository }}",
    "cancel-in-progress: true",
    "timeout-minutes: 60",
]:
    if symbol not in pg192_warehouse:
        fail(f"PG-192 normal Warehouse workflow must remain short/cancellable: {symbol}")
for ignored in [
    "Data/P1C01MaterialImportWaveV2.json",
    "Data/P1C01ChapterClosureMegaPackV2.json",
    "Scripts/preflight_p1c01_chapter_closure_pack_v2.ps1",
    "Scripts/run_p1c01_chapter_closure_pack_v2.ps1",
]:
    if ignored not in pg192_unreal:
        fail(f"PG-192 tooling-only V2 path missing from Unreal paths-ignore: {ignored}")


# PG-193: Pre-Unreal must parse every PowerShell script.
pg193_parser = read(ROOT / "Scripts" / "test_powershell_syntax.ps1")
pg193_pre = read(ROOT / ".github" / "workflows" / "pre-unreal-validation.yml")
pg193_unreal = read(ROOT / ".github" / "workflows" / "unreal-build-validation.yml")
for symbol in [
    "System.Management.Automation.Language.Parser",
    "POWERSHELL_SYNTAX_FAIL",
    "POWERSHELL_SYNTAX_PASS",
    'Get-ChildItem -LiteralPath $Root -Recurse -File -Filter "*.ps1"',
]:
    if symbol not in pg193_parser:
        fail(f"PG-193 PowerShell parser gate marker missing: {symbol}")
if "Parse all PowerShell scripts" not in pg193_pre or "test_powershell_syntax.ps1" not in pg193_pre:
    fail("PG-193 Pre-Unreal PowerShell parser step missing")
if "Scripts/test_powershell_syntax.ps1" not in pg193_unreal:
    fail("PG-193 PowerShell parser guard must remain tooling-only in Unreal paths-ignore")


# PG-194: Sequential Part I queue must remain predecessor-gated while downstream prep stays source-only.
pg194_legacy = json.loads(read(ROOT / "Data" / "P1C02ShadowPastChapterPackV1.json"))
pg194_train = json.loads(read(ROOT / "Data" / "Part1SequentialRuntimeChapterTrainV1.json"))
pg194_queue = read(ROOT / "Scripts" / "run_sequential_chapter_queue.ps1")
pg194_prep = read(ROOT / "Scripts" / "run_part1_runtime_chapter_prep.ps1")
pg194_workflow = read(ROOT / ".github" / "workflows" / "sequential-chapter-queue.yml")
pg194_prep_workflow = read(ROOT / ".github" / "workflows" / "part1-chapter-preparation.yml")
pg194_unreal = read(ROOT / ".github" / "workflows" / "unreal-build-validation.yml")

if pg194_legacy.get("status") != "QUEUED_BEHIND_P1C01_GATE67":
    fail("PG-194 legacy Shadow-of-the-Past source packet status changed unexpectedly")
if pg194_train.get("status") != "PREPARATION_OPEN_RUNTIME_SERIALIZED":
    fail("PG-194 Part I train must keep prep open and runtime serialized")
release = pg194_train.get("runtime_release_contract", {})
if release.get("required_predecessor_gate_status") != "ACCEPTED":
    fail("PG-194 runtime successor release must require ACCEPTED predecessor gate")
if release.get("current_successor") != "P1C02":
    fail("PG-194 first runtime successor must remain P1C02")
mappings = pg194_train.get("id_reconciliation", {}).get("mappings", [])
runtime_ids = [x.get("runtime_chapter") for x in mappings]
if runtime_ids != ["P1C01","P1C02","P1C03","P1C04","P1C05","P1C06","P1C07","P1C08"]:
    fail("PG-194 Part I runtime mapping order drifted")
if mappings and mappings[0].get("canonical_missions") != ["F1-01","F1-02","F1-03"]:
    fail("PG-194 P1C01 canonical coverage reconciliation missing")
for symbol in [
    "SEQUENTIAL_CHAPTER_QUEUE_WAIT",
    "SEQUENTIAL_CHAPTER_QUEUE_RELEASE",
    "P1C02_QUEUE_RELEASE=true",
    "Part1SequentialRuntimeChapterTrainV1.json",
]:
    if symbol not in pg194_queue:
        fail(f"PG-194 queue controller marker missing: {symbol}")
for symbol in [
    "PART1_CHAPTER_PREP_BEGIN",
    "$matches.ToArray()",
    "[object[]]$candidateRows",
    "PART1_CHAPTER_PREP_PASS",
    "PART1_CHAPTER_PREP_COMPLETE",
    "SOURCE_CANDIDATE_INDEX_PREPARED",
]:
    if symbol not in pg194_prep:
        fail(f"PG-194 Part I prep marker missing: {symbol}")
for symbol in [
    "name: Sequential Chapter Queue",
    "cancel-in-progress: false",
    "Fast queue preflight",
    "Prepare P1C02 source train",
    "run_part1_runtime_chapter_prep.ps1",
]:
    if symbol not in pg194_workflow:
        fail(f"PG-194 sequential queue workflow marker missing: {symbol}")
for symbol in [
    "name: Part I Chapter Preparation Train",
    "cancel-in-progress: false",
    "Prepare P1C02-P1C08 shared-stock indexes",
]:
    if symbol not in pg194_prep_workflow:
        fail(f"PG-194 Part I preparation workflow marker missing: {symbol}")
for ignored in [
    "Data/Part1SequentialRuntimeChapterTrainV1.json",
    "Scripts/run_part1_runtime_chapter_prep.ps1",
    "Scripts/run_sequential_chapter_queue.ps1",
]:
    if pg194_unreal.count(ignored) < 2:
        fail(f"PG-194 queued chapter prep must stay off Unreal push+PR filters: {ignored}")


# PG-196: production trains must be PowerShell 5.1/native-command safe.
pg196_closure = read(ROOT / "Scripts" / "run_p1c01_chapter_closure_pack_v2.ps1")
pg196_part1 = read(ROOT / "Scripts" / "run_part1_runtime_chapter_prep.ps1")
pg196_export = read(ROOT / "Scripts" / "export_p1c01_material_source_branch.ps1")
if "$code=$LASTEXITCODE" in pg196_closure:
    fail("PG-196 closure cars may not read ambient LASTEXITCODE after non-native scriptblocks")
for symbol in ["Invoke-ChildPowerShell","Exception.Data[\"ExitCode\"]"]:
    if symbol not in pg196_closure:
        fail(f"PG-196 deterministic closure exit contract missing: {symbol}")
for symbol in ["$matches.ToArray()","[object[]]$candidateRows","candidates = $candidateRows"]:
    if symbol not in pg196_part1:
        fail(f"PG-196 PowerShell 5.1 Part I candidate materialization missing: {symbol}")
if "ls-remote --heads origin $remoteRef | Select-Object -First 1" in pg196_export:
    fail("PG-196 native git ls-remote may not be truncated inside the pipeline before exit capture")
for symbol in ["P1C01_MATERIAL_SOURCE_REMOTE_LOOKUP","for($attempt=1; $attempt -le 3; $attempt++)","$lookupExit=[int]$LASTEXITCODE"]:
    if symbol not in pg196_export:
        fail(f"PG-196 generated-branch lookup retry/exit contract missing: {symbol}")


# PG-197: F1-04 Bree & Weathertop source superpack must remain large, shared and runtime-gated.
pg197_manifest = json.loads(read(ROOT / "Data" / "F104BreeWeathertopMegaSourceSuperpackV1.json"))
pg197_runner = read(ROOT / "Scripts" / "run_f104_bree_weathertop_mega_source.ps1")
pg197_workflow = read(ROOT / ".github" / "workflows" / "f104-bree-weathertop-mega-source.yml")
pg197_unreal = read(ROOT / ".github" / "workflows" / "unreal-build-validation.yml")

if pg197_manifest.get("status") != "SOURCE_PREPARATION_READY_RUNTIME_GATED":
    fail("PG-197 F1-04 superpack must remain source-ready and runtime-gated")
if pg197_manifest.get("canonical_mission_id") != "F1-04":
    fail("PG-197 F1-04 canonical mission ID drifted")
if pg197_manifest.get("runtime_consumers") != ["P1C02", "P1C03"]:
    fail("PG-197 F1-04 runtime consumers must remain P1C02 + P1C03")
policy = pg197_manifest.get("source_policy", {})
if int(policy.get("max_total_candidates", 0)) < 8000:
    fail("PG-197 F1-04 total candidate ceiling unexpectedly reduced")
if int(policy.get("max_candidates_per_category", 0)) < 1000:
    fail("PG-197 F1-04 per-category throughput unexpectedly reduced")
if policy.get("animated_candidate_extension") != ".fbx":
    fail("PG-197 animated F1-04 candidates must remain FBX-only")
if ".bmp" not in policy.get("forbidden_texture_extensions", []):
    fail("PG-197 F1-04 source pack must continue blocking BMP textures")
if not policy.get("reuse_existing_warehouse_first", False):
    fail("PG-197 F1-04 source pack must reuse persistent warehouse stock first")
if policy.get("duplicate_payloads_per_runtime_chapter", True):
    fail("PG-197 F1-04 source pack may not duplicate payloads across P1C02/P1C03")
categories = pg197_manifest.get("categories", [])
if len(categories) < 16:
    fail("PG-197 F1-04 source pack lost required category breadth")
category_ids = {x.get("id") for x in categories}
for required in [
    "BREE_ARCHITECTURE",
    "BREE_INN_INTERIORS",
    "BREE_WEATHER_AUDIO",
    "BREE_POPULATION_SUPPORT",
    "WEATHERTOP_TERRAIN",
    "WEATHERTOP_RUINS",
    "WEATHERTOP_ENCOUNTER_SUPPORT",
    "F104_CHARACTER_ANIMATION_SUPPORT",
    "F104_FAUNA_AMBIENCE",
]:
    if required not in category_ids:
        fail(f"PG-197 F1-04 category missing: {required}")
for symbol in [
    "F104_MEGA_SOURCE_BEGIN",
    "F104_MEGA_SOURCE_CATEGORY_PASS",
    "F104_MEGA_SOURCE_PASS",
    "$matches.ToArray()",
    "blockedBmp",
    'if($kind -eq "animated" -and $ext -ne $animatedExt)',
]:
    if symbol not in pg197_runner:
        fail(f"PG-197 F1-04 source runner marker missing: {symbol}")
for symbol in [
    "name: F1-04 Bree Weathertop Mega Source",
    "cancel-in-progress: false",
    "timeout-minutes: 180",
    "Fast F1-04 PowerShell preflight",
    "Build Bree Weathertop mega source indexes",
]:
    if symbol not in pg197_workflow:
        fail(f"PG-197 F1-04 workflow contract missing: {symbol}")
for ignored in [
    "Data/F104BreeWeathertopMegaSourceSuperpackV1.json",
    "Scripts/run_f104_bree_weathertop_mega_source.ps1",
    ".github/workflows/f104-bree-weathertop-mega-source.yml",
]:
    if pg197_unreal.count(ignored) < 2:
        fail(f"PG-197 F1-04 tooling path must stay off Unreal push+PR filters: {ignored}")


# PG-198: F1-05 Rivendell & Fellowship source superpack must remain large, inventory-gated and runtime-gated.
pg198_manifest = json.loads(read(ROOT / "Data" / "F105RivendellFellowshipMegaSourceSuperpackV1.json"))
pg198_runner = read(ROOT / "Scripts" / "run_f105_rivendell_fellowship_mega_source.ps1")
pg198_workflow = read(ROOT / ".github" / "workflows" / "f105-rivendell-fellowship-mega-source.yml")
pg198_unreal = read(ROOT / ".github" / "workflows" / "unreal-build-validation.yml")

if pg198_manifest.get("status") != "SOURCE_ARCHITECTURE_READY_INVENTORY_GATED_RUNTIME_GATED":
    fail("PG-198 F1-05 superpack must remain inventory-gated and runtime-gated")
if pg198_manifest.get("canonical_mission_id") != "F1-05":
    fail("PG-198 F1-05 canonical mission ID drifted")
if pg198_manifest.get("runtime_consumers") != ["P1C04"]:
    fail("PG-198 F1-05 runtime consumer must remain P1C04")
policy = pg198_manifest.get("source_policy", {})
safety = pg198_manifest.get("safety_gate", {})
if int(policy.get("max_total_candidates", 0)) < 12000:
    fail("PG-198 F1-05 total candidate ceiling unexpectedly reduced")
if int(policy.get("max_candidates_per_category", 0)) < 1500:
    fail("PG-198 F1-05 per-category throughput unexpectedly reduced")
if policy.get("animated_candidate_extension") != ".fbx":
    fail("PG-198 animated F1-05 candidates must remain FBX-only")
if ".bmp" not in policy.get("forbidden_texture_extensions", []):
    fail("PG-198 F1-05 source pack must continue blocking BMP textures")
if not safety.get("requires_clean_warehouse_inventory", False):
    fail("PG-198 F1-05 heavy execution must require clean warehouse inventory")
for key in ["hard_stop_on_hash_mismatch","hard_stop_on_license_hash_mismatch","hard_stop_on_dangerous_file","hard_stop_on_bad_receipt"]:
    if not safety.get(key, False):
        fail(f"PG-198 F1-05 warehouse safety gate weakened: {key}")
categories = pg198_manifest.get("categories", [])
if len(categories) < 20:
    fail("PG-198 F1-05 source pack lost required category breadth")
for required in [
    "RIVENDELL_TERRACES_ARCHITECTURE",
    "COUNCIL_SPACE",
    "FELLOWSHIP_CHARACTER_SUPPORT",
    "FELLOWSHIP_ANIMATION_LIBRARY",
    "RIVENDELL_ELVEN_POPULATION",
    "RELATIONSHIP_SCENE_SUPPORT",
    "HEALING_RECOVERY_SUPPORT",
    "FELLOWSHIP_DEPARTURE_SUPPORT",
    "SYSTEMIC_INTERACTION_SUPPORT",
]:
    if required not in {x.get("id") for x in categories}:
        fail(f"PG-198 F1-05 category missing: {required}")
for symbol in [
    "F105_MEGA_SOURCE_INVENTORY_GATE_BEGIN",
    "F105_MEGA_SOURCE_INVENTORY_GATE_PASS",
    "F105_MEGA_SOURCE_INVENTORY_GATE_FAIL",
    "audit_warehouse_inventory.ps1",
    "F105_MEGA_SOURCE_CATEGORY_PASS",
    "F105_MEGA_SOURCE_PASS",
    'if($kind -eq "animated" -and $ext -ne $animatedExt)',
]:
    if symbol not in pg198_runner:
        fail(f"PG-198 F1-05 runner marker missing: {symbol}")
for symbol in [
    "name: F1-05 Rivendell Fellowship Mega Source",
    "cancel-in-progress: false",
    "timeout-minutes: 180",
    "Fast F1-05 PowerShell preflight",
    "Build Rivendell Fellowship mega source indexes",
]:
    if symbol not in pg198_workflow:
        fail(f"PG-198 F1-05 workflow contract missing: {symbol}")
for ignored in [
    "Data/F105RivendellFellowshipMegaSourceSuperpackV1.json",
    "Scripts/run_f105_rivendell_fellowship_mega_source.ps1",
    ".github/workflows/f105-rivendell-fellowship-mega-source.yml",
]:
    if pg198_unreal.count(ignored) < 2:
        fail(f"PG-198 F1-05 tooling path must stay off Unreal push+PR filters: {ignored}")


# PG-199: Part I landmark identity + F1-06 Caradhras/Moria superpack must stay large, landmark-centered and gated.
pg199_landmarks = json.loads(read(ROOT / "Data" / "Part1LandmarkIdentityPlanV1.json"))
pg199_manifest = json.loads(read(ROOT / "Data" / "F106CaradhrasMoriaLandmarkMegaSourceSuperpackV1.json"))
pg199_runner = read(ROOT / "Scripts" / "run_f106_caradhras_moria_landmark_mega_source.ps1")
pg199_workflow = read(ROOT / ".github" / "workflows" / "f106-caradhras-moria-landmark-mega-source.yml")
pg199_unreal = read(ROOT / ".github" / "workflows" / "unreal-build-validation.yml")

if pg199_landmarks.get("status") != "SOURCE_ARCHITECTURE_READY_RUNTIME_GATED":
    fail("PG-199 Part I landmark plan must remain source-ready and runtime-gated")
regions = pg199_landmarks.get("regions", [])
region_ids = [x.get("id") for x in regions]
for required in ["SHIRE_HOBBITON","BAG_END","BREE","WEATHERTOP","RIVENDELL","CARADHRAS","MORIA"]:
    if required not in region_ids:
        fail(f"PG-199 Part I landmark region missing: {required}")
if len(pg199_landmarks.get("global_rules", [])) < 6:
    fail("PG-199 Part I landmark global rules unexpectedly reduced")

if pg199_manifest.get("status") != "SOURCE_ARCHITECTURE_READY_INVENTORY_GATED_RUNTIME_GATED":
    fail("PG-199 F1-06 superpack must remain inventory-gated and runtime-gated")
if pg199_manifest.get("canonical_mission_id") != "F1-06":
    fail("PG-199 F1-06 canonical mission ID drifted")
if pg199_manifest.get("runtime_consumers") != ["P1C05","P1C06"]:
    fail("PG-199 F1-06 runtime consumers must remain P1C05 + P1C06")

policy = pg199_manifest.get("source_policy", {})
safety = pg199_manifest.get("safety_gate", {})
landmark_policy = pg199_manifest.get("landmark_policy", {})
if int(policy.get("max_total_candidates", 0)) < 16000:
    fail("PG-199 F1-06 total candidate ceiling unexpectedly reduced")
if int(policy.get("max_candidates_per_category", 0)) < 1800:
    fail("PG-199 F1-06 per-category throughput unexpectedly reduced")
if int(policy.get("landmark_score_bonus", 0)) < 6:
    fail("PG-199 F1-06 landmark score bonus unexpectedly reduced")
if policy.get("animated_candidate_extension") != ".fbx":
    fail("PG-199 animated F1-06 candidates must remain FBX-only")
if ".bmp" not in policy.get("forbidden_texture_extensions", []):
    fail("PG-199 F1-06 source pack must continue blocking BMP textures")
if not safety.get("requires_clean_warehouse_inventory", False):
    fail("PG-199 F1-06 heavy execution must require clean warehouse inventory")
for key in ["hard_stop_on_hash_mismatch","hard_stop_on_license_hash_mismatch","hard_stop_on_dangerous_file","hard_stop_on_bad_receipt"]:
    if not safety.get(key, False):
        fail(f"PG-199 F1-06 warehouse safety gate weakened: {key}")
if int(landmark_policy.get("minimum_landmark_categories", 0)) < 8:
    fail("PG-199 F1-06 landmark minimum unexpectedly reduced")
if not landmark_policy.get("require_dominant_vista_per_location", False):
    fail("PG-199 F1-06 dominant vista requirement removed")

categories = pg199_manifest.get("categories", [])
if len(categories) < 24:
    fail("PG-199 F1-06 source pack lost required category breadth")
landmark_categories = [x for x in categories if x.get("landmark")]
if len(landmark_categories) < 8:
    fail("PG-199 F1-06 configured landmark category count too small")
for required in [
    "CARADHRAS_RIDGE_LANDMARK",
    "CARADHRAS_PASS_TRAVERSAL",
    "CARADHRAS_STORM_VISIBILITY",
    "MORIA_ENTRANCE_THRESHOLD",
    "MORIA_MONUMENTAL_HALL_AXIS",
    "MORIA_ROUTEFINDING_LANDMARKS",
    "MORIA_TOMB_ALERT_SPACE",
    "MORIA_BALROG_ESCAPE_VISTA",
    "F106_LANDMARK_DISTANCE_PROXY_SUPPORT",
]:
    if required not in {x.get("id") for x in categories}:
        fail(f"PG-199 F1-06 landmark/source category missing: {required}")

for symbol in [
    "F106_MEGA_SOURCE_INVENTORY_GATE_BEGIN",
    "F106_MEGA_SOURCE_INVENTORY_GATE_PASS",
    "F106_LANDMARK_SOURCE_PASS",
    "F106_LANDMARK_SOURCE_COVERAGE_FAIL",
    "landmarkBonus",
    "F106_MEGA_SOURCE_CATEGORY_PASS",
    "F106_MEGA_SOURCE_PASS",
    "$matches.ToArray()",
    'if($kind -eq "animated" -and $ext -ne $animatedExt)',
]:
    if symbol not in pg199_runner:
        fail(f"PG-199 F1-06 runner marker missing: {symbol}")

for symbol in [
    "name: F1-06 Caradhras Moria Landmark Mega Source",
    "cancel-in-progress: false",
    "timeout-minutes: 180",
    "Fast F1-06 PowerShell preflight",
    "Build Caradhras Moria landmark mega source indexes",
]:
    if symbol not in pg199_workflow:
        fail(f"PG-199 F1-06 workflow contract missing: {symbol}")

for ignored in [
    "Data/Part1LandmarkIdentityPlanV1.json",
    "Data/F106CaradhrasMoriaLandmarkMegaSourceSuperpackV1.json",
    "Scripts/run_f106_caradhras_moria_landmark_mega_source.ps1",
    ".github/workflows/f106-caradhras-moria-landmark-mega-source.yml",
]:
    if pg199_unreal.count(ignored) < 2:
        fail(f"PG-199 F1-06 tooling path must stay off Unreal push+PR filters: {ignored}")



# PG-200: F1-07 Lorien/Anduin landmark superpack must stay large, canon-bounded and runtime-gated.
pg200_landmarks = json.loads(read(ROOT / "Data" / "Part1LandmarkIdentityPlanV1.json"))
pg200_manifest = json.loads(read(ROOT / "Data" / "F107LorienAnduinLandmarkMegaSourceSuperpackV1.json"))
pg200_runner = read(ROOT / "Scripts" / "run_f107_lorien_anduin_landmark_mega_source.ps1")
pg200_workflow = read(ROOT / ".github" / "workflows" / "f107-lorien-anduin-landmark-mega-source.yml")
pg200_unreal = read(ROOT / ".github" / "workflows" / "unreal-build-validation.yml")

pg200_region_ids = [x.get("id") for x in pg200_landmarks.get("regions", [])]
for required in ["LOTHLORIEN", "ANDUIN_F107_APPROACH"]:
    if required not in pg200_region_ids:
        fail(f"PG-200 Part I landmark region missing: {required}")

if pg200_manifest.get("status") != "SOURCE_ARCHITECTURE_READY_INVENTORY_GATED_RUNTIME_GATED":
    fail("PG-200 F1-07 superpack must remain inventory-gated and runtime-gated")
if pg200_manifest.get("canonical_mission_id") != "F1-07":
    fail("PG-200 F1-07 canonical mission ID drifted")
if pg200_manifest.get("runtime_consumers") != ["P1C07"]:
    fail("PG-200 F1-07 runtime consumer must remain P1C07")

pg200_policy = pg200_manifest.get("source_policy", {})
pg200_safety = pg200_manifest.get("safety_gate", {})
pg200_landmark_policy = pg200_manifest.get("landmark_policy", {})
if int(pg200_policy.get("max_total_candidates", 0)) < 18000:
    fail("PG-200 F1-07 total candidate ceiling unexpectedly reduced")
if int(pg200_policy.get("max_candidates_per_category", 0)) < 2000:
    fail("PG-200 F1-07 per-category throughput unexpectedly reduced")
if int(pg200_policy.get("landmark_score_bonus", 0)) < 7:
    fail("PG-200 F1-07 landmark score bonus unexpectedly reduced")
if pg200_policy.get("animated_candidate_extension") != ".fbx":
    fail("PG-200 animated F1-07 candidates must remain FBX-only")
if ".bmp" not in pg200_policy.get("forbidden_texture_extensions", []):
    fail("PG-200 F1-07 source pack must continue blocking BMP textures")
if not pg200_safety.get("requires_clean_warehouse_inventory", False):
    fail("PG-200 F1-07 heavy execution must require clean warehouse inventory")
for key in ["hard_stop_on_hash_mismatch", "hard_stop_on_license_hash_mismatch", "hard_stop_on_dangerous_file", "hard_stop_on_bad_receipt"]:
    if not pg200_safety.get(key, False):
        fail(f"PG-200 F1-07 warehouse safety gate weakened: {key}")
if int(pg200_landmark_policy.get("minimum_landmark_categories", 0)) < 10:
    fail("PG-200 F1-07 landmark minimum unexpectedly reduced")
if not pg200_landmark_policy.get("require_dominant_vista_per_location", False):
    fail("PG-200 F1-07 dominant vista requirement removed")
if not pg200_landmark_policy.get("amon_hen_approach_only_before_f108", False):
    fail("PG-200 F1-07 must preserve the F1-08 boundary at Amon Hen")

pg200_excluded = " ".join(str(x) for x in pg200_manifest.get("story_contract", {}).get("excluded_from_this_pack", []))
if "F1-08" not in pg200_excluded:
    fail("PG-200 F1-07 pack must explicitly exclude the F1-08 Fellowship-break set piece")

pg200_categories = pg200_manifest.get("categories", [])
if len(pg200_categories) < 26:
    fail("PG-200 F1-07 source pack lost required category breadth")
pg200_landmark_categories = [x for x in pg200_categories if x.get("landmark")]
if len(pg200_landmark_categories) < 10:
    fail("PG-200 F1-07 configured landmark category count too small")
for required in [
    "LORIEN_GOLDEN_CANOPY_LANDMARK",
    "LORIEN_VERTICAL_FLETS",
    "LORIEN_ORGANIC_BRIDGES",
    "LORIEN_LUMINOUS_FOREST",
    "LORIEN_DEPARTURE_BOAT_THRESHOLD",
    "ANDUIN_RIVER_AXIS_LANDMARK",
    "ANDUIN_CLIFFS_SHORES",
    "ANDUIN_STONE_MONUMENTS",
    "AMON_HEN_APPROACH_VISTA",
    "AMON_HEN_APPROACH_ROUTEFINDING",
    "F107_LANDMARK_DISTANCE_PROXY_SUPPORT",
]:
    if required not in {x.get("id") for x in pg200_categories}:
        fail(f"PG-200 F1-07 landmark/source category missing: {required}")

for symbol in [
    "F107_MEGA_SOURCE_INVENTORY_GATE_BEGIN",
    "F107_MEGA_SOURCE_INVENTORY_GATE_PASS",
    "F107_LANDMARK_SOURCE_PASS",
    "F107_LANDMARK_SOURCE_COVERAGE_FAIL",
    "landmarkBonus",
    "F107_MEGA_SOURCE_CATEGORY_PASS",
    "F107_MEGA_SOURCE_PASS",
    "$matches.ToArray()",
    '-Root $WarehouseRoot',
    'if($kind -eq "animated" -and $ext -ne $animatedExt)',
]:
    if symbol not in pg200_runner:
        fail(f"PG-200 F1-07 runner marker missing: {symbol}")

for symbol in [
    "name: F1-07 Lórien Anduin Landmark Mega Source",
    "cancel-in-progress: false",
    "timeout-minutes: 180",
    "Fast F1-07 PowerShell preflight",
    "Build Lórien Anduin landmark mega source indexes",
]:
    if symbol not in pg200_workflow:
        fail(f"PG-200 F1-07 workflow contract missing: {symbol}")

for ignored in [
    "Data/F107LorienAnduinLandmarkMegaSourceSuperpackV1.json",
    "Scripts/run_f107_lorien_anduin_landmark_mega_source.ps1",
    ".github/workflows/f107-lorien-anduin-landmark-mega-source.yml",
]:
    if pg200_unreal.count(ignored) < 2:
        fail(f"PG-200 F1-07 tooling path must stay off Unreal push+PR filters: {ignored}")


# PG-201: F1-08 Amon Hen maximum-safe source wave must preserve canon, bank breadth and runtime gating.
pg201_landmarks = json.loads(read(ROOT / "Data" / "Part1LandmarkIdentityPlanV1.json"))
pg201_manifest = json.loads(read(ROOT / "Data" / "F108AmonHenBreakingMaximumSafeMegaSourceV1.json"))
pg201_runner = read(ROOT / "Scripts" / "run_f108_amon_hen_breaking_maximum_safe_source.ps1")
pg201_workflow = read(ROOT / ".github" / "workflows" / "f108-amon-hen-breaking-maximum-safe-source.yml")
pg201_unreal = read(ROOT / ".github" / "workflows" / "unreal-build-validation.yml")

pg201_region_ids = [x.get("id") for x in pg201_landmarks.get("regions", [])]
if "AMON_HEN_BREAKING" not in pg201_region_ids:
    fail("PG-201 Part I landmark region missing: AMON_HEN_BREAKING")

if pg201_manifest.get("status") != "SOURCE_ARCHITECTURE_READY_INVENTORY_GATED_RUNTIME_GATED":
    fail("PG-201 F1-08 superpack must remain inventory-gated and runtime-gated")
if pg201_manifest.get("canonical_mission_id") != "F1-08":
    fail("PG-201 F1-08 canonical mission ID drifted")
if pg201_manifest.get("runtime_consumers") != ["P1C08"]:
    fail("PG-201 F1-08 runtime consumer must remain P1C08")

pg201_story = pg201_manifest.get("story_contract", {})
if pg201_story.get("locked_postcondition") != "Three parallel campaigns begin.":
    fail("PG-201 F1-08 locked postcondition drifted")
pg201_critical = " ".join(str(x) for x in pg201_story.get("critical_path", []))
for required in ["Boromir", "Merry", "Pippin", "Frodo", "Sam"]:
    if required not in pg201_critical:
        fail(f"PG-201 F1-08 critical path missing canonical participant/outcome token: {required}")
pg201_guardrails = " ".join(str(x) for x in pg201_story.get("character_guardrails", [])).lower()
if "tragic" not in pg201_guardrails or "villain" not in pg201_guardrails:
    fail("PG-201 Boromir tragic/redemptive guardrail missing")

pg201_policy = pg201_manifest.get("source_policy", {})
pg201_safety = pg201_manifest.get("safety_gate", {})
pg201_landmark_policy = pg201_manifest.get("landmark_policy", {})
pg201_bank_policy = pg201_manifest.get("bank_policy", {})

if pg201_policy.get("throughput_mode") != "ADAPTIVE_MAXIMUM_SAFE":
    fail("PG-201 F1-08 must remain in Adaptive Maximum Safe production mode")
if int(pg201_policy.get("max_total_candidates", 0)) < 24000:
    fail("PG-201 F1-08 total candidate ceiling unexpectedly reduced")
if int(pg201_policy.get("max_candidates_per_category", 0)) < 2400:
    fail("PG-201 F1-08 per-category throughput unexpectedly reduced")
if int(pg201_policy.get("landmark_score_bonus", 0)) < 8:
    fail("PG-201 F1-08 landmark score bonus unexpectedly reduced")
if not pg201_policy.get("fair_share_across_categories", False):
    fail("PG-201 F1-08 fair-share category scheduling removed")
if pg201_policy.get("animated_candidate_extension") != ".fbx":
    fail("PG-201 animated F1-08 candidates must remain FBX-only")
if ".bmp" not in pg201_policy.get("forbidden_texture_extensions", []):
    fail("PG-201 F1-08 source pack must continue blocking BMP textures")
if not pg201_safety.get("requires_clean_warehouse_inventory", False):
    fail("PG-201 F1-08 heavy execution must require clean warehouse inventory")
for key in ["hard_stop_on_hash_mismatch", "hard_stop_on_license_hash_mismatch", "hard_stop_on_dangerous_file", "hard_stop_on_bad_receipt"]:
    if not pg201_safety.get(key, False):
        fail(f"PG-201 F1-08 warehouse safety gate weakened: {key}")

if int(pg201_bank_policy.get("minimum_ready_banks", 0)) < 6:
    fail("PG-201 F1-08 minimum ready bank count unexpectedly reduced")
pg201_banks = pg201_bank_policy.get("banks", [])
if len(pg201_banks) < 7:
    fail("PG-201 F1-08 multi-bank source architecture lost required breadth")

if int(pg201_landmark_policy.get("minimum_landmark_categories", 0)) < 14:
    fail("PG-201 F1-08 landmark minimum unexpectedly reduced")
for key in [
    "require_dominant_vista_per_state",
    "amon_hen_high_seat_readability_required",
    "river_cliff_monument_readability_required",
    "battle_route_landmarks_required",
    "distance_proxy_or_lod_required_for_large_landmark_meshes",
    "critical_vista_preload_required",
]:
    if not pg201_landmark_policy.get(key, False):
        fail(f"PG-201 F1-08 landmark contract weakened: {key}")

pg201_categories = pg201_manifest.get("categories", [])
if len(pg201_categories) < 34:
    fail("PG-201 F1-08 source pack lost required category breadth")
pg201_landmark_categories = [x for x in pg201_categories if x.get("landmark")]
if len(pg201_landmark_categories) < 18:
    fail("PG-201 F1-08 configured landmark category count too small")
if any(not str(x.get("bank") or "").strip() for x in pg201_categories):
    fail("PG-201 every F1-08 source category must belong to a streaming/source bank")

for required in [
    "AMON_HEN_HIGH_SEAT_LANDMARK",
    "AMON_HEN_PARTH_GALEN_SHORE_LANDMARK",
    "AMON_HEN_ANCIENT_ROAD_STAIRS",
    "URUK_ATTACK_APPROACH_LANDMARK",
    "URUK_ATTACK_COMBAT_SPACE",
    "BOROMIR_FINAL_DEFENSE_LANDMARK",
    "BOROMIR_AFTERMATH_DRESSING",
    "MERRY_PIPPIN_CAPTURE_ROUTE",
    "FRODO_DECISION_ROUTE",
    "SAM_SHORE_PURSUIT_ROUTE",
    "SAM_FRODO_BOAT_DEPARTURE",
    "F108_CAMPAIGN_SPLIT_CINEMATIC_VISTAS",
    "F108_LANDMARK_DISTANCE_PROXY_SUPPORT",
]:
    if required not in {x.get("id") for x in pg201_categories}:
        fail(f"PG-201 F1-08 landmark/source category missing: {required}")

for symbol in [
    "F108_MEGA_SOURCE_INVENTORY_GATE_BEGIN",
    "F108_MEGA_SOURCE_INVENTORY_GATE_PASS",
    "F108_BANK_SOURCE_PASS",
    "F108_BANK_SOURCE_COVERAGE_FAIL",
    "F108_LANDMARK_SOURCE_PASS",
    "F108_LANDMARK_SOURCE_COVERAGE_FAIL",
    "$effectivePerCategory",
    "landmarkBonus",
    "F108_MEGA_SOURCE_CATEGORY_PASS",
    "F108_MEGA_SOURCE_PASS",
    "$matches.ToArray()",
    '-Root $WarehouseRoot',
    'if($kind -eq "animated" -and $ext -ne $animatedExt)',
]:
    if symbol not in pg201_runner:
        fail(f"PG-201 F1-08 runner marker missing: {symbol}")

for symbol in [
    "name: F1-08 Amon Hen Breaking Maximum Safe Mega Source",
    "cancel-in-progress: false",
    "timeout-minutes: 180",
    "Fast F1-08 PowerShell preflight",
    "Build Amon Hen Breaking maximum-safe mega source indexes",
]:
    if symbol not in pg201_workflow:
        fail(f"PG-201 F1-08 workflow contract missing: {symbol}")

for ignored in [
    "Data/F108AmonHenBreakingMaximumSafeMegaSourceV1.json",
    "Scripts/run_f108_amon_hen_breaking_maximum_safe_source.ps1",
    ".github/workflows/f108-amon-hen-breaking-maximum-safe-source.yml",
]:
    if pg201_unreal.count(ignored) < 2:
        fail(f"PG-201 F1-08 tooling path must stay off Unreal push+PR filters: {ignored}")


# PG-202: F2-01 maximum-safe source wave must preserve canon, bank breadth and the unassigned Part II runtime-ID boundary.
pg202_manifest = json.loads(read(ROOT / "Data" / "F201ThreeHuntersCaptivesMaximumSafeMegaSourceV1.json"))
pg202_runner = read(ROOT / "Scripts" / "run_f201_three_hunters_captives_maximum_safe_source.ps1")
pg202_workflow = read(ROOT / ".github" / "workflows" / "f201-three-hunters-captives-maximum-safe-source.yml")
pg202_unreal = read(ROOT / ".github" / "workflows" / "unreal-build-validation.yml")

if pg202_manifest.get("status") != "SOURCE_ARCHITECTURE_READY_INVENTORY_GATED_RUNTIME_MAPPING_UNASSIGNED":
    fail("PG-202 F2-01 source wave status drifted")
if pg202_manifest.get("canonical_mission_id") != "F2-01":
    fail("PG-202 F2-01 canonical mission ID drifted")
if pg202_manifest.get("canonical_title") != "Three Hunters / Captives":
    fail("PG-202 F2-01 canonical title drifted")
if pg202_manifest.get("runtime_consumers") not in ([], None):
    fail("PG-202 F2-01 must not invent a Part II runtime consumer before migration mapping exists")
if pg202_manifest.get("runtime_mapping_status") != "NOT_ASSIGNED_DO_NOT_INVENT":
    fail("PG-202 F2-01 runtime mapping boundary weakened")

pg202_story = pg202_manifest.get("story_contract", {})
if pg202_story.get("locked_postcondition") != "Paths converge around Fangorn/Rohan.":
    fail("PG-202 F2-01 locked postcondition drifted")
pg202_critical = " ".join(str(x) for x in pg202_story.get("critical_path", []))
for required in ["Aragorn", "Legolas", "Gimli", "Merry", "Pippin", "Uruk", "Fangorn"]:
    if required not in pg202_critical:
        fail(f"PG-202 F2-01 critical path missing canonical token: {required}")
pg202_excluded = " ".join(str(x) for x in pg202_story.get("excluded_from_this_pack", []))
for required in ["F2-02", "Ent mobilization", "Gandalf"]:
    if required not in pg202_excluded:
        fail(f"PG-202 F2-01 must explicitly exclude later-chapter content: {required}")

pg202_policy = pg202_manifest.get("source_policy", {})
pg202_safety = pg202_manifest.get("safety_gate", {})
pg202_landmark_policy = pg202_manifest.get("landmark_policy", {})
pg202_bank_policy = pg202_manifest.get("bank_policy", {})

if pg202_policy.get("throughput_mode") != "ADAPTIVE_MAXIMUM_SAFE":
    fail("PG-202 F2-01 must remain in Adaptive Maximum Safe production mode")
if int(pg202_policy.get("max_total_candidates", 0)) < 28000:
    fail("PG-202 F2-01 total candidate ceiling unexpectedly reduced")
if int(pg202_policy.get("max_candidates_per_category", 0)) < 2600:
    fail("PG-202 F2-01 per-category throughput unexpectedly reduced")
if int(pg202_policy.get("landmark_score_bonus", 0)) < 8:
    fail("PG-202 F2-01 landmark score bonus unexpectedly reduced")
if not pg202_policy.get("fair_share_across_categories", False):
    fail("PG-202 F2-01 fair-share category scheduling removed")
if pg202_policy.get("animated_candidate_extension") != ".fbx":
    fail("PG-202 animated F2-01 candidates must remain FBX-only")
if ".bmp" not in pg202_policy.get("forbidden_texture_extensions", []):
    fail("PG-202 F2-01 source pack must continue blocking BMP textures")
if not pg202_safety.get("requires_clean_warehouse_inventory", False):
    fail("PG-202 F2-01 heavy execution must require clean warehouse inventory")
if pg202_safety.get("runtime_integration_allowed", True):
    fail("PG-202 F2-01 runtime integration must remain disabled until explicit Part II runtime mapping exists")
if not pg202_safety.get("runtime_mapping_required_before_runtime_work", False):
    fail("PG-202 F2-01 runtime mapping requirement removed")
for key in ["hard_stop_on_hash_mismatch", "hard_stop_on_license_hash_mismatch", "hard_stop_on_dangerous_file", "hard_stop_on_bad_receipt"]:
    if not pg202_safety.get(key, False):
        fail(f"PG-202 F2-01 warehouse safety gate weakened: {key}")

if int(pg202_bank_policy.get("minimum_ready_banks", 0)) < 7:
    fail("PG-202 F2-01 minimum ready bank count unexpectedly reduced")
pg202_banks = pg202_bank_policy.get("banks", [])
if len(pg202_banks) < 8:
    fail("PG-202 F2-01 multi-bank source architecture lost required breadth")

if int(pg202_landmark_policy.get("minimum_landmark_categories", 0)) < 14:
    fail("PG-202 F2-01 landmark minimum unexpectedly reduced")
for key in [
    "require_open_to_dense_transition_readability",
    "rohan_route_silhouette_required",
    "fangorn_threshold_silhouette_required",
    "tracking_landmarks_required",
    "distance_proxy_or_lod_required_for_large_landmark_meshes",
    "critical_vista_preload_required",
]:
    if not pg202_landmark_policy.get(key, False):
        fail(f"PG-202 F2-01 landmark contract weakened: {key}")

pg202_categories = pg202_manifest.get("categories", [])
if len(pg202_categories) < 38:
    fail("PG-202 F2-01 source pack lost required category breadth")
pg202_landmark_categories = [x for x in pg202_categories if x.get("landmark")]
if len(pg202_landmark_categories) < 17:
    fail("PG-202 F2-01 configured landmark category count too small")
if any(not str(x.get("bank") or "").strip() for x in pg202_categories):
    fail("PG-202 every F2-01 source category must belong to a source bank")

for required in [
    "ROHAN_OPEN_PLAINS_ROUTE",
    "ROHAN_DISTANT_RIDGE_LANDMARK",
    "TRACKS_FOOTPRINT_EVIDENCE",
    "URUK_TRAIL_ROUTE_LANDMARK",
    "URUK_CAMP_REMAINS",
    "CAPTIVE_ESCAPE_ROUTE_LANDMARK",
    "FANGORN_EDGE_WALL_OF_TREES",
    "FANGORN_ROOTS_THRESHOLD",
    "FANGORN_MIST_THRESHOLD",
    "F201_CONVERGENCE_VISTA",
    "F201_LANDMARK_DISTANCE_PROXY_SUPPORT",
]:
    if required not in {x.get("id") for x in pg202_categories}:
        fail(f"PG-202 F2-01 landmark/source category missing: {required}")

for symbol in [
    "F201_MEGA_SOURCE_INVENTORY_GATE_BEGIN",
    "F201_MEGA_SOURCE_INVENTORY_GATE_PASS",
    "F201_BANK_SOURCE_PASS",
    "F201_BANK_SOURCE_COVERAGE_FAIL",
    "F201_LANDMARK_SOURCE_PASS",
    "F201_LANDMARK_SOURCE_COVERAGE_FAIL",
    "$effectivePerCategory",
    "landmarkBonus",
    "F201_MEGA_SOURCE_CATEGORY_PASS",
    "F201_MEGA_SOURCE_PASS",
    "$matches.ToArray()",
    '-Root $WarehouseRoot',
    'if($kind -eq "animated" -and $ext -ne $animatedExt)',
]:
    if symbol not in pg202_runner:
        fail(f"PG-202 F2-01 runner marker missing: {symbol}")

for symbol in [
    "name: F2-01 Three Hunters Captives Maximum Safe Mega Source",
    "cancel-in-progress: false",
    "timeout-minutes: 180",
    "Fast F2-01 PowerShell preflight",
    "Build Three Hunters Captives maximum-safe mega source indexes",
]:
    if symbol not in pg202_workflow:
        fail(f"PG-202 F2-01 workflow contract missing: {symbol}")

for ignored in [
    "Data/F201ThreeHuntersCaptivesMaximumSafeMegaSourceV1.json",
    "Scripts/run_f201_three_hunters_captives_maximum_safe_source.ps1",
    ".github/workflows/f201-three-hunters-captives-maximum-safe-source.yml",
]:
    if pg202_unreal.count(ignored) < 2:
        fail(f"PG-202 F2-01 tooling path must stay off Unreal push+PR filters: {ignored}")


# PG-203: F2-02 Fangorn/Gandalf maximum-safe source wave must preserve canon, character guardrails, bank breadth and the unassigned Part II runtime-ID boundary.
pg203_manifest = json.loads(read(ROOT / "Data" / "F202FangornGandalfReturnedMaximumSafeMegaSourceV1.json"))
pg203_runner = read(ROOT / "Scripts" / "run_f202_fangorn_gandalf_returned_maximum_safe_source.ps1")
pg203_workflow = read(ROOT / ".github" / "workflows" / "f202-fangorn-gandalf-returned-maximum-safe-source.yml")
pg203_unreal = read(ROOT / ".github" / "workflows" / "unreal-build-validation.yml")

if pg203_manifest.get("status") != "SOURCE_ARCHITECTURE_READY_INVENTORY_GATED_RUNTIME_MAPPING_UNASSIGNED":
    fail("PG-203 F2-02 source wave status drifted")
if pg203_manifest.get("canonical_mission_id") != "F2-02":
    fail("PG-203 F2-02 canonical mission ID drifted")
if pg203_manifest.get("canonical_title") != "Fangorn & Gandalf Returned":
    fail("PG-203 F2-02 canonical title drifted")
if pg203_manifest.get("runtime_consumers") not in ([], None):
    fail("PG-203 F2-02 must not invent a Part II runtime consumer before migration mapping exists")
if pg203_manifest.get("runtime_mapping_status") != "NOT_ASSIGNED_DO_NOT_INVENT":
    fail("PG-203 F2-02 runtime mapping boundary weakened")

pg203_story = pg203_manifest.get("story_contract", {})
if pg203_story.get("locked_postcondition") != "Gandalf leads hunters to Edoras.":
    fail("PG-203 F2-02 locked postcondition drifted")
pg203_critical = " ".join(str(x) for x in pg203_story.get("critical_path", []))
for required in ["Ents introduced", "Gandalf returns transformed"]:
    if required not in pg203_critical:
        fail(f"PG-203 F2-02 critical path missing canonical beat: {required}")
pg203_guardrails = " ".join(str(x) for x in pg203_story.get("character_guardrails", [])).lower()
for required in ["massive", "deliberate", "rare", "purposeful", "spam-casting"]:
    if required not in pg203_guardrails:
        fail(f"PG-203 F2-02 character guardrail missing token: {required}")
pg203_excluded = " ".join(str(x) for x in pg203_story.get("excluded_from_this_pack", []))
for required in ["F2-08", "Isengard", "Edoras"]:
    if required not in pg203_excluded:
        fail(f"PG-203 F2-02 later-state exclusion missing: {required}")

pg203_world = pg203_manifest.get("world_contract", {})
if pg203_world.get("primary_location") != "Fangorn":
    fail("PG-203 F2-02 primary location must remain Fangorn")
for token in ["dense trunks", "roots", "mist", "living environment"]:
    if token not in pg203_world.get("visual_grammar", []):
        fail(f"PG-203 Fangorn visual grammar missing: {token}")

pg203_policy = pg203_manifest.get("source_policy", {})
pg203_safety = pg203_manifest.get("safety_gate", {})
pg203_landmark_policy = pg203_manifest.get("landmark_policy", {})
pg203_bank_policy = pg203_manifest.get("bank_policy", {})

if pg203_policy.get("throughput_mode") != "ADAPTIVE_MAXIMUM_SAFE":
    fail("PG-203 F2-02 must remain in Adaptive Maximum Safe production mode")
if int(pg203_policy.get("max_total_candidates", 0)) < 32000:
    fail("PG-203 F2-02 total candidate ceiling unexpectedly reduced")
if int(pg203_policy.get("max_candidates_per_category", 0)) < 2800:
    fail("PG-203 F2-02 per-category throughput unexpectedly reduced")
if int(pg203_policy.get("landmark_score_bonus", 0)) < 9:
    fail("PG-203 F2-02 landmark score bonus unexpectedly reduced")
if not pg203_policy.get("fair_share_across_categories", False):
    fail("PG-203 F2-02 fair-share category scheduling removed")
if pg203_policy.get("animated_candidate_extension") != ".fbx":
    fail("PG-203 animated F2-02 candidates must remain FBX-only")
if ".bmp" not in pg203_policy.get("forbidden_texture_extensions", []):
    fail("PG-203 F2-02 source pack must continue blocking BMP textures")
if not pg203_safety.get("requires_clean_warehouse_inventory", False):
    fail("PG-203 F2-02 heavy execution must require clean warehouse inventory")
if pg203_safety.get("runtime_integration_allowed", True):
    fail("PG-203 F2-02 runtime integration must remain disabled until explicit Part II runtime mapping exists")
if not pg203_safety.get("runtime_mapping_required_before_runtime_work", False):
    fail("PG-203 F2-02 runtime mapping requirement removed")
for key in ["hard_stop_on_hash_mismatch", "hard_stop_on_license_hash_mismatch", "hard_stop_on_dangerous_file", "hard_stop_on_bad_receipt"]:
    if not pg203_safety.get(key, False):
        fail(f"PG-203 F2-02 warehouse safety gate weakened: {key}")

if int(pg203_bank_policy.get("minimum_ready_banks", 0)) < 8:
    fail("PG-203 F2-02 minimum ready bank count unexpectedly reduced")
pg203_banks = pg203_bank_policy.get("banks", [])
if len(pg203_banks) < 9:
    fail("PG-203 F2-02 multi-bank source architecture lost required breadth")

if int(pg203_landmark_policy.get("minimum_landmark_categories", 0)) < 16:
    fail("PG-203 F2-02 landmark minimum unexpectedly reduced")
for key in [
    "require_dominant_fangorn_vista",
    "dense_trunk_root_readability_required",
    "ent_scale_route_readability_required",
    "gandalf_reveal_landmark_required",
    "quiet_to_mobilization_state_readability_required",
    "distance_proxy_or_lod_required_for_large_landmark_meshes",
    "critical_vista_preload_required",
]:
    if not pg203_landmark_policy.get(key, False):
        fail(f"PG-203 F2-02 landmark contract weakened: {key}")

pg203_categories = pg203_manifest.get("categories", [])
if len(pg203_categories) < 40:
    fail("PG-203 F2-02 source pack lost required category breadth")
pg203_landmark_categories = [x for x in pg203_categories if x.get("landmark")]
if len(pg203_landmark_categories) < 20:
    fail("PG-203 F2-02 configured landmark category count too small")
if any(not str(x.get("bank") or "").strip() for x in pg203_categories):
    fail("PG-203 every F2-02 source category must belong to a source bank")

for required in [
    "FANGORN_ANCIENT_TRUNK_LANDMARK",
    "FANGORN_ROOT_MAZE_LANDMARK",
    "TREEBEARD_HERO_SILHOUETTE",
    "ENT_MASSIVE_TRAVERSAL_ROUTE",
    "HOBBIT_SCALE_FOREST_LANDMARK",
    "HUNTERS_FOREST_DISORIENTATION",
    "GANDALF_RETURN_REVEAL_LANDMARK",
    "GANDALF_RESTRAINED_MAGIC_VFX",
    "ENT_MOBILIZATION_GATHERING_LANDMARK",
    "EDORAS_DEPARTURE_ROUTE_LANDMARK",
    "F202_LANDMARK_DISTANCE_PROXY_SUPPORT",
]:
    if required not in {x.get("id") for x in pg203_categories}:
        fail(f"PG-203 F2-02 landmark/source category missing: {required}")

for symbol in [
    "F202_MEGA_SOURCE_INVENTORY_GATE_BEGIN",
    "F202_MEGA_SOURCE_INVENTORY_GATE_PASS",
    "F202_BANK_SOURCE_PASS",
    "F202_BANK_SOURCE_COVERAGE_FAIL",
    "F202_LANDMARK_SOURCE_PASS",
    "F202_LANDMARK_SOURCE_COVERAGE_FAIL",
    "$effectivePerCategory",
    "landmarkBonus",
    "F202_MEGA_SOURCE_CATEGORY_PASS",
    "F202_MEGA_SOURCE_PASS",
    "$matches.ToArray()",
    '-Root $WarehouseRoot',
    'if($kind -eq "animated" -and $ext -ne $animatedExt)',
]:
    if symbol not in pg203_runner:
        fail(f"PG-203 F2-02 runner marker missing: {symbol}")

for symbol in [
    "name: F2-02 Fangorn Gandalf Returned Maximum Safe Mega Source",
    "cancel-in-progress: false",
    "timeout-minutes: 180",
    "Fast F2-02 PowerShell preflight",
    "Build Fangorn Gandalf Returned maximum-safe mega source indexes",
]:
    if symbol not in pg203_workflow:
        fail(f"PG-203 F2-02 workflow contract missing: {symbol}")

for ignored in [
    "Data/F202FangornGandalfReturnedMaximumSafeMegaSourceV1.json",
    "Scripts/run_f202_fangorn_gandalf_returned_maximum_safe_source.ps1",
    ".github/workflows/f202-fangorn-gandalf-returned-maximum-safe-source.yml",
]:
    if pg203_unreal.count(ignored) < 2:
        fail(f"PG-203 F2-02 tooling path must stay off Unreal push+PR filters: {ignored}")

# PG-195: Unreal import must not trust an editor-only wait while a commandlet remains alive.
pg195_wait = read(ROOT / "Scripts" / "wait_for_unreal_processes.ps1")
pg195_wait_cmd = read(ROOT / "Scripts" / "ci_wait_for_unreal_editor.cmd")
pg195_preflight = read(ROOT / "Scripts" / "preflight_production_asset_import.ps1")
for symbol in [
    '@("UE4Editor","UE4Editor-Cmd")',
    "UNREAL_PROCESS_DIAGNOSTIC",
    "UNREAL_STALE_CI_COMMANDLET_RECOVERED",
    "policy=never-kill-interactive-editor",
    "ParentProcessId",
    "CommandLine",
    "sameOwner",
    "UNREAL_STALE_CI_COMMANDLET_TASKKILL_DIRECT",
    "UNREAL_STALE_CI_COMMANDLET_CIM_TERMINATE",
]:
    if symbol not in pg195_wait:
        fail(f"PG-195 Unreal process wait/diagnostic marker missing: {symbol}")
for forbidden in [
    'Stop-Process -Name UE4Editor',
    'Stop-Process -Name "UE4Editor"',
]:
    if forbidden in pg195_wait:
        fail("PG-195 interactive UE4Editor must never be killed by name")
if "wait_for_unreal_processes.ps1" not in pg195_wait_cmd:
    fail("PG-195 legacy wait wrapper must delegate to the shared Unreal process waiter")
for symbol in [
    "PRODUCTION_IMPORT_PREFLIGHT_PROCESS",
    "owner=",
    "ppid=",
    "sessionId=",
    "commandLine=",
]:
    if symbol not in pg195_preflight:
        fail(f"PG-195 production-import process diagnostics missing: {symbol}")


if errors:
    print(f"PRE-UNREAL VALIDATION FAILED: {len(errors)} error(s)")
    for message in errors:
        print(f"ERROR: {message}")
    sys.exit(1)

print("PRE-UNREAL VALIDATION PASSED")


# PG-215: P1C01 Bag End hero chapter remains bounded, resident-only and event-driven.
pg215_path = ROOT / "Data" / "P1C01BagEndHeroChapterV1.json"
if not pg215_path.exists():
    fail("PG-215 Bag End hero chapter contract missing")
else:
    try:
        pg215 = json.loads(read(pg215_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-215 invalid Bag End hero chapter contract: {exc}")
        pg215 = {}

    if pg215:
        if pg215.get("status") != "EXACT_HEAD_MACHINE_GREEN_PR193_PRE1469_UE1142":
            fail("PG-215 Bag End hero chapter status drifted")
        budget = pg215.get("runtime_budget", {})
        if budget.get("max_hism_cluster_actors") != 3:
            fail("PG-215 Bag End HISM cluster ceiling must remain 3")
        if budget.get("max_hism_instances") != 36:
            fail("PG-215 Bag End HISM instance ceiling must remain 36")
        if budget.get("max_unique_lived_in_props") != 12:
            fail("PG-215 Bag End unique prop ceiling must remain 12")
        if budget.get("max_state_variant_props_per_state") != 6:
            fail("PG-215 Bag End state prop ceiling must remain 6")
        if pg215.get("architecture", {}).get("ambient_population_target_p1c01") != 18:
            fail("PG-215 Bag End car must not raise P1C01 population above 18")

    pg215_source = read(resolve_source("World/ShirePrototypeWorldBuilder.cpp"))
    if "void AShirePrototypeWorldBuilder::SpawnBagEndHeroPass()" not in pg215_source:
        fail("PG-215 SpawnBagEndHeroPass implementation missing")
    if "void AShirePrototypeWorldBuilder::ApplyBagEndStoryVariant()" not in pg215_source:
        fail("PG-215 ApplyBagEndStoryVariant implementation missing")
    pg215_start = pg215_source.index("void AShirePrototypeWorldBuilder::SpawnBagEndHeroPass()")
    pg215_end = pg215_source.index("void AShirePrototypeWorldBuilder::SpawnWorldDensityDetailPass()", pg215_start)
    pg215_body = pg215_source[pg215_start:pg215_end]
    if pg215_body.count("SpawnDetailCluster(") != 3:
        fail("PG-215 Bag End pass must admit exactly three bounded HISM clusters")
    for required in ("BAG_END_HERO_PASS", "populationTarget=18", "Configure(Mesh, false"):
        if required not in pg215_body:
            fail(f"PG-215 Bag End hero pass missing required token: {required}")
    for forbidden in ("LoadObject<", "StaticLoadObject", "RequestSyncLoad", "SpawnActor<AShireAmbientNPC>"):
        if forbidden in pg215_body:
            fail(f"PG-215 Bag End pass contains forbidden runtime path: {forbidden}")

    pg215_variant_start = pg215_source.index("void AShirePrototypeWorldBuilder::ApplyBagEndStoryVariant()")
    pg215_variant_end = pg215_source.index("void AShirePrototypeWorldBuilder::ApplyStoryAtmosphere()", pg215_variant_start)
    pg215_variant = pg215_source[pg215_variant_start:pg215_variant_end]
    for required in ("ShireArrival", "LongExpectedParty", "RingSecret", "LeavingHome", "BAG_END_STORY_VARIANT"):
        if required not in pg215_variant:
            fail(f"PG-215 Bag End state variant missing required token: {required}")


# PG-216: P1C01 party/social loop is source-grounded, bounded and window-gated.
pg216_path = ROOT / "Data" / "P1C01PartySocialLoopChapterV1.json"
if not pg216_path.exists():
    fail("PG-216 party/social loop contract missing")
else:
    try:
        pg216 = json.loads(read(pg216_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-216 invalid party/social loop contract: {exc}")
        pg216 = {}

    if pg216:
        if pg216.get("status") != "SOURCE_IMPLEMENTED_EXACT_HEAD_PROOF_PENDING":
            fail("PG-216 party/social status drifted")
        budget = pg216.get("runtime_budget", {})
        if budget.get("max_hism_cluster_actors") != 4 or budget.get("max_hism_instances") != 56:
            fail("PG-216 party HISM budget drifted")
        if budget.get("max_unique_party_props") != 16 or budget.get("max_state_variant_props") != 8:
            fail("PG-216 party prop budget drifted")
        if budget.get("max_new_optional_trigger_or_challenge_actors") != 6:
            fail("PG-216 optional actor ceiling drifted")
        if pg216.get("architecture", {}).get("ambient_population_target_p1c01") != 18:
            fail("PG-216 party car must not raise P1C01 population above 18")

    pg216_source = read(resolve_source("World/ShirePrototypeWorldBuilder.cpp"))
    if "void AShirePrototypeWorldBuilder::SpawnPartySocialLoopPass()" not in pg216_source:
        fail("PG-216 party world pass missing")
    if "void AShirePrototypeWorldBuilder::ApplyPartyStoryVariant()" not in pg216_source:
        fail("PG-216 party story variant missing")
    pg216_start = pg216_source.index("void AShirePrototypeWorldBuilder::SpawnPartySocialLoopPass()")
    pg216_end = pg216_source.index("void AShirePrototypeWorldBuilder::SpawnSideStories()", pg216_start)
    pg216_body = pg216_source[pg216_start:pg216_end]
    if pg216_body.count("SpawnPartyCluster(") != 4:
        fail("PG-216 party pass must admit exactly four HISM clusters")
    for required in ("PARTY_SOCIAL_LOOP_PASS", "populationTarget=18", "Configure(Mesh, false"):
        if required not in pg216_body:
            fail(f"PG-216 party pass missing required token: {required}")
    for forbidden in ("LoadObject<", "StaticLoadObject", "RequestSyncLoad", "SpawnActor<AShireAmbientNPC>"):
        if forbidden in pg216_body:
            fail(f"PG-216 party pass contains forbidden runtime path: {forbidden}")

    pg216_side = pg216_source[pg216_source.index("void AShirePrototypeWorldBuilder::SpawnSideStories()"):]
    for required in (
        "Side_BirthdayDecorReady",
        "Side_BirthdayFoodReady",
        "Side_BirthdaySetupComplete",
        "SHIRE_FIREWORKS_SAFETY",
        "SHIRE_DRAGON_FIREWORK_MISHAP",
        "Side_FireworksSafetyComplete",
        "Side_DragonFireworkMishapComplete",
    ):
        if required not in pg216_side:
            fail(f"PG-216 party side-loop token missing: {required}")

    pg216_plan = json.loads(read(ROOT / "Data" / "ContextualSideActivityPlan.json"))
    p1_rows = []
    for chapter in pg216_plan.get("chapters", []):
        if chapter.get("route") == "FrodoMain" and chapter.get("chapter") == "P1C01":
            p1_rows = chapter.get("activities", [])
            break
    p1_by_id = {row.get("id"): row for row in p1_rows if isinstance(row, dict)}
    for activity_id, reward_id in (
        ("SIDE_SHIRE_FIREWORKS_SAFETY", "SHIRE_FIREWORKS_SAFETY"),
        ("SIDE_SHIRE_DRAGON_FIREWORK_MISHAP", "SHIRE_DRAGON_FIREWORK_MISHAP"),
    ):
        row = p1_by_id.get(activity_id)
        if not row:
            fail(f"PG-216 side activity missing: {activity_id}")
            continue
        if row.get("available_after") != "PartyArrival" or row.get("ends_before") != "BilboDisappearance":
            fail(f"PG-216 party activity window drifted: {activity_id}")
        if row.get("discovery_reward_id") != reward_id:
            fail(f"PG-216 party activity reward drifted: {activity_id}")
        if row.get("may_advance_required_anchor") or row.get("may_change_canon_outcome") or row.get("future_knowledge_allowed"):
            fail(f"PG-216 canon-unsafe party activity flags: {activity_id}")

# PG-217: P1C01 character presentation keeps stable identity, canon-safe gear and async rig ownership.
pg217_path = ROOT / "Data" / "P1C01CharacterPresentationChapterV1.json"
if not pg217_path.exists():
    fail("PG-217 character presentation contract missing")
else:
    try:
        pg217 = json.loads(read(pg217_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-217 invalid character presentation contract: {exc}")
        pg217 = {}

    if pg217:
        if pg217.get("status") != "SOURCE_IMPLEMENTED_EXACT_HEAD_PROOF_PENDING":
            fail("PG-217 character presentation status drifted")
        contract = pg217.get("runtime_contract", {})
        if contract.get("frodo_future_weapon_in_p1c01") is not False:
            fail("PG-217 Frodo future weapon must stay hidden in P1C01")
        if contract.get("named_story_npcs_use_explicit_character_ids") is not True:
            fail("PG-217 named story NPC stable identity contract drifted")
        if contract.get("synchronous_heavy_load") is not False or contract.get("per_frame_asset_scan") is not False:
            fail("PG-217 low-spec loading contract drifted")

    pg217_npc_h = read(resolve_source("Characters/ShireNPC.h"))
    pg217_npc_cpp = read(resolve_source("Characters/ShireNPC.cpp"))
    pg217_player = read(resolve_source("Characters/ShirePlayerCharacter.cpp"))
    pg217_streaming = read(resolve_source("Subsystems/ShireChapterAssetStreamingSubsystem.cpp"))
    pg217_world = read(resolve_source("World/ShirePrototypeWorldBuilder.cpp"))

    for required in ("ProductionCharacterId", "ResolveProductionCharacterId"):
        if required not in pg217_npc_h or required not in pg217_npc_cpp:
            fail(f"PG-217 stable NPC presentation identity missing token: {required}")

    for required in (
        'GandalfRoad->ProductionCharacterId=TEXT("Gandalf")',
        'Bilbo->ProductionCharacterId=TEXT("Bilbo")',
        'GandalfBagEnd->ProductionCharacterId=TEXT("Gandalf")',
        'Sam->ProductionCharacterId=TEXT("Sam")',
    ):
        if required not in pg217_world:
            fail(f"PG-217 P1C01 hero binding missing: {required}")

    for required in (
        "ShouldShowPrototypeWeaponForCurrentStory",
        'GetCurrentChapterId() == TEXT("P1C01")',
        "P1C01_CHARACTER_PRESENTATION",
    ):
        if required not in pg217_player:
            fail(f"PG-217 Frodo story-aware equipment guard missing: {required}")

    rig_start = pg217_streaming.index("void UShireChapterAssetStreamingSubsystem::RequestCharacterRig")
    rig_end = pg217_streaming.index("void UShireChapterAssetStreamingSubsystem::HandleCharacterRigLoadComplete", rig_start)
    rig_body = pg217_streaming[rig_start:rig_end]
    if "RequestAsyncLoad" not in rig_body:
        fail("PG-217 production rig request must remain asynchronous")
    for forbidden in ("LoadObject<", "StaticLoadObject", "RequestSyncLoad"):
        if forbidden in rig_body:
            fail(f"PG-217 production rig request contains forbidden synchronous path: {forbidden}")

    for source_text, label in ((pg217_player, "player"), (pg217_npc_cpp, "npc")):
        if "bEnableUpdateRateOptimizations = true" not in source_text:
            fail(f"PG-217 {label} skeletal presentation must keep URO enabled")
        if "OnlyTickPoseWhenRendered" not in source_text:
            fail(f"PG-217 {label} skeletal presentation must remain visibility-throttled")

# PG-218: P1C01 Living Shire keeps context/social/fauna work bounded under existing owners.
pg218_path = ROOT / "Data" / "P1C01LivingShireChapterV1.json"
if not pg218_path.exists():
    fail("PG-218 Living Shire contract missing")
else:
    try:
        pg218 = json.loads(read(pg218_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-218 invalid Living Shire contract: {exc}")
        pg218 = {}

    if pg218:
        if pg218.get("status") != "SOURCE_IMPLEMENTED_EXACT_HEAD_PROOF_PENDING":
            fail("PG-218 Living Shire status drifted")
        budget = pg218.get("runtime_budget", {})
        runtime = pg218.get("runtime_contract", {})
        if budget.get("p1c01_ambient_population_target") != 18:
            fail("PG-218 P1C01 population target must remain 18")
        if budget.get("max_active_fauna_groups_near_player") != 2:
            fail("PG-218 fauna-group cap must remain 2")
        if budget.get("full_world_social_actor_scan") is not False:
            fail("PG-218 full-world social actor scan must remain disabled")
        if runtime.get("bounded_context_snapshot") is not True:
            fail("PG-218 bounded context snapshot contract drifted")
        if runtime.get("social_pairing_uses_managed_active_query") is not True:
            fail("PG-218 managed active social query contract drifted")
        if runtime.get("fauna_group_cap_enforced") is not True:
            fail("PG-218 fauna admission cap must remain enforced")
        if runtime.get("synchronous_heavy_load") is not False or runtime.get("per_frame_context_reconstruction") is not False:
            fail("PG-218 low-spec context/loading contract drifted")

    pg218_ambient = read(resolve_source("Characters/ShireAmbientNPC.cpp"))
    pg218_director = read(resolve_source("World/LivingWorldDirector.cpp"))
    pg218_context_h = read(resolve_source("Subsystems/ShireNPCContextSubsystem.h"))
    pg218_context_cpp = read(resolve_source("Subsystems/ShireNPCContextSubsystem.cpp"))

    social_start = pg218_ambient.index("void AShireAmbientNPC::UpdateSocialLife")
    social_end = pg218_ambient.index("void AShireAmbientNPC::Tick", social_start)
    social_body = pg218_ambient[social_start:social_end]
    if "GatherActiveAmbientNPCsNear" not in social_body:
        fail("PG-218 social pairing must use Director bounded active query")
    if "TActorIterator<AShireAmbientNPC>" in social_body:
        fail("PG-218 social pairing reintroduced full-world ambient actor scan")

    schedule_start = pg218_ambient.index("void AShireAmbientNPC::UpdateScheduleContext")
    schedule_end = pg218_ambient.index("void AShireAmbientNPC::UpdateNeedsAndEmotion", schedule_start)
    if "BuildBehaviorSnapshot" not in pg218_ambient[schedule_start:schedule_end]:
        fail("PG-218 ambient schedule refresh must consume bounded behavior snapshot")

    for required in (
        "GatherActiveAmbientNPCsNear",
        "ReconcilePersistentAmbientNPCRegistry",
        "PersistentAmbientNPCs",
        "max_active_fauna_groups_near_player",
        "MaxActiveFaunaGroups",
    ):
        if required not in pg218_director:
            fail(f"PG-218 LivingWorldDirector missing required token: {required}")
    if "TActorIterator<AShireAmbientNPC>" not in pg218_director:
        fail("PG-218 persistent ambient registration must reconcile once from committed world actors")
    if 'ActorHasTag(TEXT("LivingWorldManaged"))' not in pg218_director:
        fail("PG-218 persistent ambient registration must exclude Director-managed pooled population")
    for required in ("FShireNPCBehaviorSnapshot", "BuildBehaviorSnapshot"):
        if required not in pg218_context_h:
            fail(f"PG-218 NPC context header missing required token: {required}")
    if "BuildBehaviorSnapshot" not in pg218_context_cpp:
        fail("PG-218 NPC context implementation missing bounded behavior snapshot")

    pg218_life = json.loads(read(ROOT / "Data" / "WorldLifeSaturationPlan.json"))
    if pg218_life.get("baseline_population_targets", {}).get("P1C01") != 18:
        fail("PG-218 WorldLifeSaturationPlan P1C01 population drifted above/below 18")



# PG-219: P1C01 quest/side-activity coherence remains quest-owned, windowed and idempotent.
pg219_path = ROOT / "Data" / "P1C01QuestSideActivityCoherenceV1.json"
if not pg219_path.exists():
    fail("PG-219 quest-side-activity coherence contract missing")
else:
    try:
        pg219 = json.loads(read(pg219_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-219 invalid quest-side-activity coherence contract: {exc}")
        pg219 = {}

    if pg219:
        if pg219.get("status") != "SOURCE_IMPLEMENTED_EXACT_HEAD_PROOF_PENDING":
            fail("PG-219 quest coherence status drifted")
        coherence = pg219.get("coherence_contract", {})
        if coherence.get("main_quest_priority") is not True:
            fail("PG-219 main quest priority must remain enabled")
        if coherence.get("clean_expiry_on_closing_story_beat") is not True:
            fail("PG-219 side activities must expire on closing story beats")
        if coherence.get("idempotent_completion") is not True:
            fail("PG-219 side activity completion must remain idempotent")
        expected_urgency = {"RingSecret", "LeavingHome", "KeepOffRoad", "FerryEscape"}
        if set(coherence.get("p1c01_urgency_suppression", [])) != expected_urgency:
            fail("PG-219 P1C01 urgency suppression set drifted")

    pg219_h = read(resolve_source("Subsystems/ShireQuestSubsystem.h"))
    pg219_cpp = read(resolve_source("Subsystems/ShireQuestSubsystem.cpp"))
    for required in (
        "GetAvailableSideActivityIdsForCurrentWindow",
        "IsMainQuestUrgencySuppressingSideActivities",
    ):
        if required not in pg219_h or required not in pg219_cpp:
            fail(f"PG-219 quest-owned activity projection missing token: {required}")

    for required in (
        'ActiveQuestId == TEXT("RingSecret")',
        'ActiveQuestId == TEXT("LeavingHome")',
        'ActiveQuestId == TEXT("KeepOffRoad")',
        'ActiveQuestId == TEXT("FerryEscape")',
        "JourneyDiscoveryIds.Contains(DiscoveryId)",
        "IsSideActivityDefinitionAvailable(Pair.Value)",
    ):
        if required not in pg219_cpp:
            fail(f"PG-219 quest coherence implementation missing: {required}")



# PG-220: P1C01 cinematic control handoff must converge unlock/skip/camera release under existing owners.
pg220_path = ROOT / "Data" / "P1C01CinematicControlHandoffV1.json"
if not pg220_path.exists():
    fail("PG-220 cinematic control handoff contract missing")
else:
    try:
        pg220 = json.loads(read(pg220_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-220 invalid cinematic control handoff contract: {exc}")
        pg220 = {}

    if pg220:
        if pg220.get("status") != "SOURCE_IMPLEMENTED_EXACT_HEAD_PROOF_PENDING":
            fail("PG-220 cinematic handoff status drifted")
        runtime = pg220.get("runtime_contract", {})
        for field in (
            "bounded_cinematic_lock",
            "skip_release_uses_same_exit_path",
            "camera_release_on_cinematic_unlock",
            "chapter_change_forces_release",
            "authored_external_camera_not_stolen",
        ):
            if runtime.get(field) is not True:
                fail(f"PG-220 required cinematic handoff contract drifted: {field}")
        if runtime.get("quest_route_save_state_mutation_from_presentation") is not False:
            fail("PG-220 presentation must not own quest/route/save mutation")
        if runtime.get("stale_runtime_camera_after_skip") is not False:
            fail("PG-220 stale runtime camera after skip must remain forbidden")

    pg220_presentation_h = read(resolve_source("Subsystems/ShireStoryPresentationSubsystem.h"))
    pg220_presentation_cpp = read(resolve_source("Subsystems/ShireStoryPresentationSubsystem.cpp"))
    pg220_director_h = read(resolve_source("World/StoryPresentationDirector.h"))
    pg220_director_cpp = read(resolve_source("World/StoryPresentationDirector.cpp"))

    for required in ("IsCinematicLocked", "RequestSkipActivePresentation", "ReleaseCinematicLock"):
        if required not in pg220_presentation_h or required not in pg220_presentation_cpp:
            fail(f"PG-220 presentation exit API missing: {required}")

    skip_start = pg220_presentation_cpp.index("void UShireStoryPresentationSubsystem::RequestSkipActivePresentation")
    release_start = pg220_presentation_cpp.index("void UShireStoryPresentationSubsystem::ReleaseCinematicLock", skip_start)
    skip_body = pg220_presentation_cpp[skip_start:release_start]
    if "ReleaseCinematicLock();" not in skip_body:
        fail("PG-220 skip must converge on ReleaseCinematicLock")
    for forbidden in ("SetQuestStage(", "AdvanceQuest(", "StartChapter(", "StartExperience(", "TriggerStoryBeat("):
        if forbidden in skip_body:
            fail(f"PG-220 skip path contains forbidden story mutation: {forbidden}")

    for required in (
        "HandleCinematicStateChanged",
        "OnCinematicStateChanged.AddDynamic",
        "OnCinematicStateChanged.RemoveDynamic",
        "Presentation->ReleaseCinematicLock();",
    ):
        if required not in pg220_director_cpp:
            fail(f"PG-220 director handoff missing token: {required}")
    if "HandleCinematicStateChanged" not in pg220_director_h:
        fail("PG-220 director header missing cinematic-state handler")

    state_start = pg220_director_cpp.index("void AStoryPresentationDirector::HandleCinematicStateChanged")
    release_camera_start = pg220_director_cpp.index("void AStoryPresentationDirector::ReleaseCamera", state_start)
    state_body = pg220_director_cpp[state_start:release_camera_start]
    if "if (!bLocked)" not in state_body or "ReleaseCamera();" not in state_body:
        fail("PG-220 cinematic unlock must release transient runtime camera")



# PG-221: P1C01 Shire audio identity keeps async ownership and bounded decorative concurrency.
pg221_path = ROOT / "Data" / "P1C01ShireAudioIdentityV1.json"
if not pg221_path.exists():
    fail("PG-221 Shire audio identity contract missing")
else:
    try:
        pg221 = json.loads(read(pg221_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-221 invalid Shire audio identity contract: {exc}")
        pg221 = {}

    if pg221:
        if pg221.get("status") != "SOURCE_IMPLEMENTED_EXACT_HEAD_PROOF_PENDING":
            fail("PG-221 Shire audio identity status drifted")
        runtime = pg221.get("runtime_contract", {})
        budget = pg221.get("low_spec_budget", {})
        if runtime.get("heavy_audio_loading") != "FSoftObjectPath + FStreamableManager async":
            fail("PG-221 heavy audio loading contract drifted")
        if runtime.get("decorative_spatial_sfx_burst_bounded") is not True:
            fail("PG-221 decorative SFX burst must remain bounded")
        if runtime.get("story_critical_sfx_not_blocked_by_decorative_burst") is not True:
            fail("PG-221 story-critical SFX priority contract drifted")
        if budget.get("max_decorative_spatial_sfx_starts_per_window") != 6:
            fail("PG-221 decorative SFX start cap must remain 6")
        if abs(float(budget.get("decorative_spatial_sfx_window_seconds", 0.0)) - 0.25) > 0.001:
            fail("PG-221 decorative SFX window must remain 0.25 seconds")

    pg221_h = read(resolve_source("Subsystems/ShireAudioSubsystem.h"))
    pg221_cpp = read(resolve_source("Subsystems/ShireAudioSubsystem.cpp"))

    for required in (
        "RecentDecorativeSfxStartTimes",
        "DecorativeSfxWindowSeconds = 0.25f",
        "MaxDecorativeSfxStartsPerWindow = 6",
        "CanPlaySfxNow(FName CueId, bool bStoryCritical)",
    ):
        if required not in pg221_h:
            fail(f"PG-221 audio header missing required token: {required}")

    sfx_start = pg221_cpp.index("bool UShireAudioSubsystem::CanPlaySfxNow")
    ambience_start = pg221_cpp.index("void UShireAudioSubsystem::SetAmbienceCue", sfx_start)
    sfx_budget_body = pg221_cpp[sfx_start:ambience_start]
    for required in (
        "RecentDecorativeSfxStartTimes.RemoveAll",
        "RecentDecorativeSfxStartTimes.Num() >= MaxDecorativeSfxStartsPerWindow",
        "RecentDecorativeSfxStartTimes.Add(Now)",
    ):
        if required not in sfx_budget_body:
            fail(f"PG-221 decorative SFX budget implementation missing: {required}")

    if "CanPlaySfxNow(CueId, true)" not in pg221_cpp:
        fail("PG-221 story-critical SFX path must bypass decorative burst budget")
    if "CanPlaySfxNow(CueId, false)" not in pg221_cpp:
        fail("PG-221 localized decorative SFX path must consume burst budget")

    async_start = pg221_cpp.index("void UShireAudioSubsystem::RequestAudioAssetAsync")
    async_end = pg221_cpp.index("void UShireAudioSubsystem::CancelPendingAudioCategory", async_start)
    async_body = pg221_cpp[async_start:async_end]
    if "RequestAsyncLoad" not in async_body:
        fail("PG-221 audio residency path must remain asynchronous")
    for forbidden in ("LoadObject<", "StaticLoadObject", "RequestSyncLoad"):
        if forbidden in pg221_cpp:
            fail(f"PG-221 audio source contains forbidden synchronous load path: {forbidden}")



# PG-222: P1C01 long-session persistence rejects oversized payloads before restore mutation.
pg222_path = ROOT / "Data" / "P1C01SaveLoadLongSessionV1.json"
if not pg222_path.exists():
    fail("PG-222 long-session persistence contract missing")
else:
    try:
        pg222 = json.loads(read(pg222_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-222 invalid long-session persistence contract: {exc}")
        pg222 = {}

    if pg222:
        if pg222.get("status") != "SOURCE_IMPLEMENTED_EXACT_HEAD_PROOF_PENDING":
            fail("PG-222 long-session status drifted")
        runtime = pg222.get("runtime_contract", {})
        if runtime.get("save_payload_bounds_checked_before_restore_mutation") is not True:
            fail("PG-222 save payload bounds must be checked before restore mutation")
        if runtime.get("long_session_unbounded_save_growth_forbidden") is not True:
            fail("PG-222 unbounded long-session save growth must remain forbidden")
        bounds = pg222.get("restore_bounds", {})
        expected = {
            "max_quest_stages": 128,
            "max_story_beats": 512,
            "max_route_progress_entries": 16,
            "max_npc_memory_buckets": 128,
            "max_discoveries": 512,
            "max_insight_milestones": 128,
            "max_progression_tracks": 64,
            "max_chronicle_entries": 1024,
            "max_known_map_regions": 128,
        }
        if bounds != expected:
            fail("PG-222 restore bounds drifted")

    pg222_h = read(resolve_source("Characters/ShirePlayerCharacter.h"))
    pg222_cpp = read(resolve_source("Characters/ShirePlayerCharacter.cpp"))
    if "ValidateSaveSnapshotBounds" not in pg222_h or "ValidateSaveSnapshotBounds" not in pg222_cpp:
        fail("PG-222 bounded save admission API missing")

    restore_start = pg222_cpp.index("bool AShirePlayerCharacter::RestoreSaveSnapshot")
    begin_restore = pg222_cpp.index("BeginPersistenceRestore", restore_start)
    pre_transaction = pg222_cpp[restore_start:begin_restore]
    if "ValidateSaveSnapshotBounds(Save)" not in pre_transaction:
        fail("PG-222 payload bounds must execute before BeginPersistenceRestore")

    for required in (
        'TEXT("QuestStages"), Save->QuestStages.Num(), 128',
        'TEXT("CompletedStoryBeats"), Save->CompletedStoryBeats.Num(), 512',
        'TEXT("RouteProgress"), Save->RouteProgress.Num(), 16',
        'TEXT("NPCMemoryState"), Save->NPCMemoryState.Num(), 128',
        'TEXT("JourneyDiscoveryIds"), Save->JourneyDiscoveryIds.Num(), 512',
        'TEXT("ChronicleEntryIds"), Save->ChronicleEntryIds.Num(), 1024',
    ):
        if required not in pg222_cpp:
            fail(f"PG-222 bounded save field missing: {required}")

    save_h = read(ROOT / "Source" / "ShireJourney" / "Public" / "SaveGame" / "ShireSaveGame.h")
    if "CurrentSchemaVersion = 6" not in save_h:
        fail("PG-222 must not change save schema solely for bounded admission")



# PG-223: P1C01 Gate 6/7 evidence tooling remains fail-closed and cannot self-certify missing device/human evidence.
pg223_path = ROOT / "Data" / "P1C01TargetDeviceGate67V1.json"
if not pg223_path.exists():
    fail("PG-223 target-device Gate67 contract missing")
else:
    try:
        pg223 = json.loads(read(pg223_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-223 invalid Gate67 contract: {exc}")
        pg223 = {}

    if pg223:
        if pg223.get("status") != "STATIC_ACCEPTANCE_PREP_IMPLEMENTED_PREDECESSOR_MERGED":
            fail("PG-223 Gate67 preparation status drifted")
        profile = pg223.get("target_profile", {})
        if profile.get("renderer") != "DX11":
            fail("PG-223 renderer target must remain DX11")
        if profile.get("resolution_width") != 1280 or profile.get("resolution_height") != 720:
            fail("PG-223 target resolution must remain 1280x720")
        if profile.get("quality") != "Balanced Medium / selective High where visually important" or profile.get("fps_floor") != 30:
            fail("PG-223 quality/FPS gate drifted")
        claims = pg223.get("current_claims", {})
        if any(claims.values()):
            fail("PG-223 static preparation may not claim runtime/device/human acceptance")

    evaluator_path = ROOT / "Scripts" / "evaluate_p1c01_gate67_evidence.py"
    if not evaluator_path.exists():
        fail("PG-223 Gate67 evidence evaluator missing")
    else:
        evaluator = read(evaluator_path)
        for required in (
            '"status":"INCOMPLETE"',
            '"status":"GATE67_NOT_ACCEPTED"',
            'route below 30 FPS floor',
            'blocking streaming hitch',
            'synchronous heavy load observed',
            'save/load continuity not proven',
            'return-to-control continuity not proven',
            '"DEVICE_TESTED":True',
            '"PERFORMANCE_ACCEPTED":True',
        ):
            if required not in evaluator:
                fail(f"PG-223 evidence evaluator missing fail-closed token: {required}")


# PG-224: Part I runtime production is serialized P1C01-P1C08 with Frodo first and fail-closed predecessor gates.
pg224_path = ROOT / "Data" / "P1C01RuntimeChapterSequenceV1.json"
pg224_warehouse = read(ROOT / ".github" / "workflows" / "warehouse-stage.yml")
if not pg224_path.exists():
    fail("PG-224 runtime chapter sequence contract missing")
else:
    try:
        pg224 = json.loads(read(pg224_path))
    except json.JSONDecodeError as exc:
        fail(f"PG-224 invalid runtime chapter sequence contract: {exc}")
        pg224 = {}

    if pg224:
        expected_order = [f"P1C0{i}" for i in range(1, 9)]
        actual_order = [str(row.get("id")) for row in pg224.get("runtime_chapter_order", [])]
        if actual_order != expected_order:
            fail("PG-224 runtime chapter order must remain P1C01 through P1C08")
        if pg224.get("current_chapter") != "P1C01":
            fail("PG-224 P1C01 must remain the active runtime chapter until Gate 6/7 acceptance")
        if pg224.get("current_car") != "P1C01-A_FRODO_SKELETAL_PRODUCTION":
            fail("PG-224 Frodo skeletal production must remain the current first car")
        if pg224.get("p1c01_character_order") != ["FRODO", "GANDALF"]:
            fail("PG-224 character production must remain Frodo then Gandalf")
        later = pg224.get("runtime_chapter_order", [])[1:]
        if any(row.get("runtime_status") != "PREDECESSOR_GATED" for row in later):
            fail("PG-224 later runtime chapters must remain predecessor-gated")

if pg205_manifest.get("owner_sequence_authority") != "Data/P1C01RuntimeChapterSequenceV1.json":
    fail("PG-224 hero candidate wave must reference the owner runtime sequence")
if pg205_manifest.get("owner_execution_order") != ["FRODO", "GANDALF"]:
    fail("PG-224 hero candidate execution must remain Frodo then Gandalf")
for symbol in [
    "pull_request:",
    "github.event.pull_request.head.sha || github.sha",
    "actions/upload-artifact@v4",
    "p1c01_hero_skeletal_candidate_summary.json",
    "p1c01_character_rig_intake_receipt.json",
]:
    if symbol not in pg205_workflow:
        fail(f"PG-224 exact-head candidate evidence workflow missing: {symbol}")


# PG-225: registered Warehouse Stage executes the one-shot exact-head Frodo candidate QC bridge on an explicit merge marker.
for symbol in [
    "Data/P1C01HeroSkeletalCandidateWaveV1.json",
    "P1C01_FRODO_CANDIDATE_QC",
    "run_p1c01_hero_skeletal_candidate_wave.ps1",
    "Build exact-head P1C01 Frodo Gandalf candidate report",
    "Upload exact-head P1C01 hero candidate evidence",
    "p1c01_hero_skeletal_candidate_summary.json",
    "p1c01_character_rig_intake_receipt.json",
]:
    if symbol not in pg224_warehouse:
        fail(f"PG-225 Warehouse candidate-QC bridge missing: {symbol}")
