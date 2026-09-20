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

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Source" / "ShireJourney"

errors: list[str] = []
warnings: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def warn(message: str) -> None:
    warnings.append(message)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        fail(f"Cannot read {path.relative_to(ROOT)}: {exc}")
        return ""


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
    ROOT / "Config" / "DefaultEngine.ini",
    ROOT / "Config" / "DefaultGame.ini",
    ROOT / "Config" / "DefaultInput.ini",
    SOURCE / "ShireGameMode.cpp",
    SOURCE / "ShirePlayerCharacter.cpp",
    SOURCE / "ShireQuestSubsystem.cpp",
    SOURCE / "ShireQuestTrigger.cpp",
    SOURCE / "ChapterWorldRouter.cpp",
    SOURCE / "ShirePrototypeWorldBuilder.cpp",
    SOURCE / "BreePrototypeWorldBuilder.cpp",
    SOURCE / "FellowshipChapterWorldBuilder.cpp",
    SOURCE / "ShireStoryPresentationSubsystem.h",
    SOURCE / "ShireStoryPresentationSubsystem.cpp",
    SOURCE / "ShireDialogueSubsystem.h",
    SOURCE / "ShireDialogueSubsystem.cpp",
    SOURCE / "ShireAudioSubsystem.h",
    SOURCE / "ShireAudioSubsystem.cpp",
    SOURCE / "ShireStoryFlowSubsystem.h",
    SOURCE / "ShireStoryFlowSubsystem.cpp",
    SOURCE / "FellowshipEnemyPrototype.h",
    SOURCE / "FellowshipEnemyPrototype.cpp",
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

allowed_requirement_statuses = set(governor_data.get("requirement_status_values", []))
allowed_requirement_priorities = set(governor_data.get("priority_values", []))
requirement_ids: set[str] = set()
for index, item in enumerate(governor_data.get("requirements", []), start=1):
    req_id = str(item.get("id") or "").strip()
    title = str(item.get("title") or "").strip()
    intent = str(item.get("intent") or "").strip()
    status = str(item.get("status") or "").strip()
    priority = str(item.get("priority") or "").strip()
    acceptance = item.get("acceptance_criteria", [])

    if not req_id or not title or not intent:
        fail(f"ProjectGovernor requirement entry {index} is missing id/title/intent")
        continue
    if req_id in requirement_ids:
        fail(f"Duplicate ProjectGovernor requirement id: {req_id}")
    requirement_ids.add(req_id)
    if allowed_requirement_statuses and status not in allowed_requirement_statuses:
        fail(f"ProjectGovernor requirement {req_id} uses unknown status '{status}'")
    if allowed_requirement_priorities and priority not in allowed_requirement_priorities:
        fail(f"ProjectGovernor requirement {req_id} uses unknown priority '{priority}'")
    if not isinstance(acceptance, list) or not acceptance:
        fail(f"ProjectGovernor requirement {req_id} has no acceptance criteria")

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

    build_text = read(SOURCE / "ShireJourney.Build.cs")
    if "Data/FilmDialogueSourceContext.json" not in build_text:
        fail("Film dialogue source context is not packaged as a runtime dependency")
    npc_context_text = read(SOURCE / "ShireNPCContextSubsystem.cpp")
    for marker in ["LoadFilmDialogueSourceContext", "GetFilmDialogueContextSummary", "SourceContextId"]:
        if marker not in npc_context_text and marker not in read(SOURCE / "ShireNPCContextSubsystem.h"):
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

    build_text_pg62 = read(SOURCE / "ShireJourney.Build.cs")
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

    build_text_pg63 = read(SOURCE / "ShireJourney.Build.cs")
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
    if symbol not in read(SOURCE / "ShireQuestSubsystem.h") or symbol not in read(SOURCE / "ShireQuestSubsystem.cpp"):
        fail(f"PG-070: Ring runtime API missing {symbol}")
if "ShireStateAudit: ring-core=PASS" not in read(ROOT / "Scripts" / "runtime_smoke.py"):
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
journey_h = read(SOURCE / "ShireQuestSubsystem.h")
journey_cpp = read(SOURCE / "ShireQuestSubsystem.cpp")
journey_save = read(SOURCE / "ShireSaveGame.h")
journey_player = read(SOURCE / "ShirePlayerCharacter.cpp")
journey_trigger_h = read(SOURCE / "ShireQuestTrigger.h")
journey_trigger_cpp = read(SOURCE / "ShireQuestTrigger.cpp")
journey_hud_h = read(SOURCE / "ShireHUD.h")
journey_hud_cpp = read(SOURCE / "ShireHUD.cpp")
journey_game_mode = read(SOURCE / "ShireGameMode.cpp")
journey_smoke = read(ROOT / "Scripts" / "runtime_smoke.py")

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

if "ShireStateAudit: discovery-core=PASS" not in journey_game_mode:
    fail("PG-074: engine state audit does not prove discovery first-time continuity")
if "ShireStateAudit: discovery-core=PASS" not in journey_smoke:
    fail("PG-074: runtime smoke does not require discovery continuity")

journey_plan_runtime = json.loads(read(ROOT / "Data" / "JourneyDiscoveryRewardPlan.json"))
journey_reward_ids = {
    str(item.get("discovery_id") or "").strip()
    for item in journey_plan_runtime.get("discovery_rewards", [])
    if isinstance(item, dict)
}
journey_builder_text = "\n".join([
    read(SOURCE / "ShirePrototypeWorldBuilder.cpp"),
    read(SOURCE / "BreePrototypeWorldBuilder.cpp"),
    read(SOURCE / "FellowshipChapterWorldBuilder.cpp"),
    read(SOURCE / "IsengardPrototypeWorldBuilder.cpp"),
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
player_h = read(SOURCE / "ShirePlayerCharacter.h")
player_cpp = read(SOURCE / "ShirePlayerCharacter.cpp")
quest_h = read(SOURCE / "ShireQuestSubsystem.h")
quest_cpp = read(SOURCE / "ShireQuestSubsystem.cpp")
save_h = read(SOURCE / "ShireSaveGame.h")
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
if "ShireStateAudit: progression-core=PASS" not in read(SOURCE / "ShireGameMode.cpp"):
    fail("PG-079: progression state audit missing")
if "ShireStateAudit: progression-core=PASS" not in read(ROOT / "Scripts" / "runtime_smoke.py"):
    fail("PG-079: runtime smoke does not require progression proof")
if "Data/PlayerLifeProgressionPlan.json" not in read(SOURCE / "ShireJourney.Build.cs"):
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

quest_h_pg80 = read(SOURCE / "ShireQuestSubsystem.h")
quest_cpp_pg80 = read(SOURCE / "ShireQuestSubsystem.cpp")
save_h_pg80 = read(SOURCE / "ShireSaveGame.h")
player_cpp_pg80 = read(SOURCE / "ShirePlayerCharacter.cpp")
hud_cpp_pg80 = read(SOURCE / "ShireHUD.cpp")
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
if "ShireStateAudit: knowledge-core=PASS" not in read(SOURCE / "ShireGameMode.cpp"):
    fail("PG-080: knowledge state audit missing")
if "ShireStateAudit: knowledge-core=PASS" not in read(ROOT / "Scripts" / "runtime_smoke.py"):
    fail("PG-080: runtime smoke missing knowledge proof")
activity_count_pg80 = sum(
    len(chapter.get("activities", []))
    for chapter in side_plan_pg80.get("chapters", [])
    if isinstance(chapter, dict)
)
if activity_count_pg80 < 18:
    fail(f"PG-080: contextual side-activity catalog regressed below 18 entries: {activity_count_pg80}")


# PG-081: real traversal challenge runtime must replace pure touch-to-discover for selected activities.
traversal_h = read(SOURCE / "ShireTraversalChallenge.h")
traversal_cpp = read(SOURCE / "ShireTraversalChallenge.cpp")
shire_builder_pg81 = read(SOURCE / "ShirePrototypeWorldBuilder.cpp")
fellowship_builder_pg81 = read(SOURCE / "FellowshipChapterWorldBuilder.cpp")
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
    read(SOURCE / "ShirePlayerCharacter.cpp"),
    read(SOURCE / "ShirePrototypeWorldBuilder.cpp"),
    read(SOURCE / "BreePrototypeWorldBuilder.cpp"),
    read(SOURCE / "FellowshipChapterWorldBuilder.cpp"),
    read(SOURCE / "IsengardPrototypeWorldBuilder.cpp"),
])
for item in population_plan.get("core_cast", []):
    display_name = str(item.get("display_name") or "").strip()
    aliases = [str(value).strip() for value in item.get("aliases", []) if str(value).strip()]
    names = [display_name] + aliases
    if not any(f'TEXT("{name}")' in population_runtime_source for name in names):
        fail(f"CharacterPopulationPlan cast has no runtime source representation: {display_name}")

npc_cpp_for_population = read(SOURCE / "ShireNPC.cpp")
npc_h_for_population = read(SOURCE / "ShireNPC.h")
ambient_cpp_for_population = read(SOURCE / "ShireAmbientNPC.cpp")
bree_cpp_for_population = read(SOURCE / "BreePrototypeWorldBuilder.cpp")
fellowship_cpp_for_population = read(SOURCE / "FellowshipChapterWorldBuilder.cpp")
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
ambient_life_cpp = read(SOURCE / "ShireAmbientNPC.cpp")
ambient_life_h = read(SOURCE / "ShireAmbientNPC.h")
shire_life_cpp = read(SOURCE / "ShirePrototypeWorldBuilder.cpp")
bree_life_cpp = read(SOURCE / "BreePrototypeWorldBuilder.cpp")
fellowship_life_cpp = read(SOURCE / "FellowshipChapterWorldBuilder.cpp")

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

for role_marker in [
    'ActivityPropType=TEXT("Mug")',
    'ActivityPropType=TEXT("Satchel")',
    'ActivityPropType=TEXT("Basket")',
    'ActivityPropType=TEXT("Crate")',
]:
    if role_marker not in shire_life_cpp:
        fail(f"PG-036 Shire role activity assignment missing: {role_marker}")

if "Townsperson->ActivityPropType" not in bree_life_cpp:
    fail("PG-036 Bree townspeople lost visible activity assignments")
if "Resident->ActivityPropType" not in fellowship_life_cpp:
    fail("PG-036 Elven residents lost visible activity assignments")

# PG-035: lightweight world motion must remain cheap, 3D and region-aware.
ambient_motion_cpp = read(SOURCE / "ShireAmbientNPC.cpp")
shire_world_motion_cpp = read(SOURCE / "ShirePrototypeWorldBuilder.cpp")
bree_world_motion_cpp = read(SOURCE / "BreePrototypeWorldBuilder.cpp")
fellowship_world_motion_cpp = read(SOURCE / "FellowshipChapterWorldBuilder.cpp")
isengard_world_motion_cpp = read(SOURCE / "IsengardPrototypeWorldBuilder.cpp")

for symbol in [
    'RoutineRole == TEXT("Bird")',
    "AddActorWorldOffset(Direction * WalkSpeed * DeltaSeconds, false)",
    "WalkPhase += DeltaSeconds * 9.0f",
]:
    if symbol not in ambient_motion_cpp:
        fail(f"PG-035 lightweight bird-motion invariant missing: {symbol}")

for source_name, source_text in [
    ("Shire", shire_world_motion_cpp),
    ("Bree", bree_world_motion_cpp),
    ("Fellowship outdoor regions", fellowship_world_motion_cpp),
    ("Isengard", isengard_world_motion_cpp),
]:
    if 'RoutineRole = TEXT("Bird")' not in source_text:
        fail(f"PG-035 {source_name} lost lightweight outdoor sky-life population")

if "Distance > DormantTickDistance ? 0.75f" not in ambient_motion_cpp:
    fail("PG-035 Bird role must continue using the distance-throttled ambient actor tick budget")

# PG-034: Part I batch-build world detail must keep chapter-specific visual-density markers.
bree_world_cpp = read(SOURCE / "BreePrototypeWorldBuilder.cpp")
fellowship_world_cpp = read(SOURCE / "FellowshipChapterWorldBuilder.cpp")
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
npc_visual_cpp = read(SOURCE / "ShireNPC.cpp")
npc_visual_h = read(SOURCE / "ShireNPC.h")
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

governor_mode = governor_data.get("development_mode", {}) if governor_data else {}
governor_mode_id = governor_mode.get("id")
governor_mode_rules = [str(rule) for rule in governor_mode.get("rules", [])]
if governor_mode_id not in {"BUILD_FIRST_BATCH_MODE", "VISUAL_PRODUCTION_FIRST", "PIE_VERIFICATION_FREEZE"}:
    fail("PG-033 Governor development mode must record an approved build/visual/verification mode")
if governor_mode_id == "VISUAL_PRODUCTION_FIRST" and governor_mode.get("supersedes") != "BUILD_FIRST_BATCH_MODE":
    fail("PG-033 VISUAL_PRODUCTION_FIRST must explicitly supersede BUILD_FIRST_BATCH_MODE")
if governor_mode_id == "PIE_VERIFICATION_FREEZE" and governor_mode.get("supersedes") != "VISUAL_PRODUCTION_FIRST":
    fail("PG-033 PIE_VERIFICATION_FREEZE must explicitly supersede VISUAL_PRODUCTION_FIRST")
proof_honesty_rule = any(
    "PIE" in rule
    and "evidence" in rule.lower()
    and any(marker in rule.lower() for marker in ("performance", "fps", "device", "visual"))
    for rule in governor_mode_rules
)
if not proof_honesty_rule:
    fail("PG-033 production/verification mode must preserve manual-proof honesty")

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

black_rider_cpp = read(SOURCE / "BlackRiderPrototype.cpp")
for symbol in ["SM_BlackRider_Horse", "SM_BlackRider_Rider", "SM_BlackRider_Head"]:
    if symbol not in black_rider_cpp:
        fail(f"PG-046 Black Rider production runtime missing: {symbol}")

enemy_cpp = read(SOURCE / "FellowshipEnemyPrototype.cpp")
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

named_visual_cpp = read(SOURCE / "ShireNPC.cpp")
for folder_name in dedicated_named_assets:
    if f'DedicatedFolder = TEXT("{folder_name}")' not in named_visual_cpp:
        fail(f"PG-045 runtime dedicated-folder mapping missing: {folder_name}")

character_plan_core = population_plan.get("core_cast", []) if population_plan else []
for character in character_plan_core:
    if character.get("visual_tier") != "PRODUCTION_DEDICATED":
        fail(f"PG-045 named cast not promoted to PRODUCTION_DEDICATED: {character.get('id')}")

dialogue_context_cpp = read(SOURCE / "ShireNPCContextSubsystem.cpp")
for profile_id in [
    "NPC_BILBO","NPC_ARWEN","NPC_ELROND","NPC_SARUMAN",
    "NPC_HAMFAST_GAMGEE","NPC_ROSIE_COTTON","NPC_FARMER_MAGGOT",
    "NPC_BARLIMAN_BUTTERBUR","NPC_BREE_GATEKEEPER","NPC_HALDIR","NPC_GALADRIEL"
]:
    if profile_id not in dialogue_context_cpp:
        fail(f"PG-045 expanded named dialogue coverage missing: {profile_id}")

# PG-044: backend hardening must keep NPC context, memory, dialogue and save contracts connected.
backend_context_h = read(SOURCE / "ShireNPCContextSubsystem.h")
backend_context_cpp = read(SOURCE / "ShireNPCContextSubsystem.cpp")
backend_quest_h = read(SOURCE / "ShireQuestSubsystem.h")
backend_quest_cpp = read(SOURCE / "ShireQuestSubsystem.cpp")
backend_npc_cpp = read(SOURCE / "ShireNPC.cpp")
backend_ambient_cpp = read(SOURCE / "ShireAmbientNPC.cpp")
backend_dialogue_h = read(SOURCE / "ShireDialogueSubsystem.h")
backend_dialogue_cpp = read(SOURCE / "ShireDialogueSubsystem.cpp")
backend_save_h = read(SOURCE / "ShireSaveGame.h")
backend_player_cpp = read(SOURCE / "ShirePlayerCharacter.cpp")
backend_build_cs = read(SOURCE / "ShireJourney.Build.cs")

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

hero_visual_cpp = read(SOURCE / "ShireNPC.cpp")
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

regional_cpp = read(SOURCE / "FellowshipChapterWorldBuilder.cpp")
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

bree_visual_cpp = read(SOURCE / "BreePrototypeWorldBuilder.cpp")
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

shire_visual_cpp = read(SOURCE / "ShirePrototypeWorldBuilder.cpp")
named_visual_cpp = read(SOURCE / "ShireNPC.cpp")
ambient_visual_cpp = read(SOURCE / "ShireAmbientNPC.cpp")
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
memory_route_h = read(SOURCE / "ShireRouteState.h")
memory_quest_h = read(SOURCE / "ShireQuestSubsystem.h")
memory_quest_cpp = read(SOURCE / "ShireQuestSubsystem.cpp")
memory_context_cpp = read(SOURCE / "ShireNPCContextSubsystem.cpp")
memory_save_h = read(SOURCE / "ShireSaveGame.h")
memory_player_cpp = read(SOURCE / "ShirePlayerCharacter.cpp")

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
ambient_conversation_cpp = read(SOURCE / "ShireAmbientNPC.cpp")
ambient_conversation_h = read(SOURCE / "ShireAmbientNPC.h")
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
    named_npc_cpp = read(SOURCE / "ShireNPC.cpp")
    dialogue_h = read(SOURCE / "ShireDialogueSubsystem.h")
    dialogue_cpp = read(SOURCE / "ShireDialogueSubsystem.cpp")
    context_cpp = read(SOURCE / "ShireNPCContextSubsystem.cpp")
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
    read(SOURCE / "ShirePlayerCharacter.cpp"),
    read(SOURCE / "ShirePlayerCharacter.h"),
    read(SOURCE / "ShireQuestTrigger.cpp"),
    read(SOURCE / "ShireSaveGame.h"),
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
    "SafeCheckpoint: id=%s saved=%s",
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

for path in sorted(SOURCE.glob("*.[ch]pp")) + sorted(SOURCE.glob("*.h")):
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

for path in sorted(SOURCE.glob("*.h")):
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

living_h = read(SOURCE / "LivingWorldDirector.h")
living_cpp = read(SOURCE / "LivingWorldDirector.cpp")
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

game_mode_cpp = read(SOURCE / "ShireGameMode.cpp")
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

shire_world_cpp = read(SOURCE / "ShirePrototypeWorldBuilder.cpp")
fellowship_world_cpp = read(SOURCE / "FellowshipChapterWorldBuilder.cpp")
for symbol in ["SM_CommonTerracedHill", "SM_CommonVillageSlope", "SM_CommonRiverBank", "SM_CommonBoulderCluster"]:
    if symbol not in shire_world_cpp:
        fail(f"PG-049 Shire terrain runtime reference missing: {symbol}")
for symbol in ["SM_CommonMountainRidge", "SM_CommonCliffWall", "SM_CommonRiverBank", "SpawnTerrainBand"]:
    if symbol not in fellowship_world_cpp:
        fail(f"PG-049 Fellowship terrain runtime reference missing: {symbol}")

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
shire_world_for_headers = read(SOURCE / "ShirePrototypeWorldBuilder.cpp")
if '#include "Engine/AtmosphericFog.h"' in shire_world_for_headers:
    fail("PG-016: do not include Engine/AtmosphericFog.h on the locked UE4.27.2 toolchain")

# PG-017: files covered by .gitattributes LFS rules must be actual LFS pointers in Git.
# Raw binary blobs under an LFS-tracked extension make checkout report "should have been
# pointers, but weren't" and make the self-hosted workspace nondeterministic.
production_root = ROOT / "SourceAssets" / "Production"
lfs_extensions = {".uasset", ".umap", ".fbx", ".wav", ".png", ".tga", ".exr"}
if production_root.exists():
    for asset_path in production_root.rglob("*"):
        if asset_path.is_file() and asset_path.suffix.lower() in lfs_extensions:
            if not is_git_lfs_pointer(asset_path):
                fail(
                    "PG-017: LFS-tracked production asset is committed as a raw blob: "
                    + str(asset_path.relative_to(ROOT))
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
editor_wait_contract_ok = (
    "Get-Process -Name UE4Editor" in unreal_ci
    and "AddMinutes(20)" in unreal_ci
    and "Start-Sleep -Seconds 10" in unreal_ci
    and "exit 40" in unreal_ci
)
if editor_probe_marker not in unreal_ci and not editor_wait_contract_ok:
    fail("PG-015: Unreal self-hosted validation must either prove the editor is closed or wait safely for it without terminating the user's editor")
checkout_action_ok = (
    "uses: actions/checkout@v4" in unreal_ci
    and "ref: ${{ github.event.pull_request.head.sha || github.sha }}" in unreal_ci
    and "persist-credentials: false" in unreal_ci
    and "git rev-parse HEAD" in unreal_ci
    and "Checkout SHA mismatch" in unreal_ci
)
exact_checkout_markers = [
    "zipball/$env:GITHUB_SHA",
    "GET /repos/{owner}/{repo}/zipball/{ref}",
    "git fetch --no-tags --prune --depth=1 origin %GITHUB_SHA%",
    "git fetch --no-tags --prune --depth=1 origin %TARGET_SHA%",
    "& git fetch --no-tags --prune --depth=1 origin $env:TARGET_SHA",
]
custom_checkout_ok = any(marker in unreal_ci for marker in exact_checkout_markers)
if not checkout_action_ok and not custom_checkout_ok:
    fail("PG-026: Unreal self-hosted build must acquire and verify the exact validated PR-head SHA")
if "TARGET_SHA: ${{ github.event.pull_request.head.sha || github.sha }}" not in unreal_ci:
    fail("PG-026: pull-request Unreal validation must resolve TARGET_SHA to the PR head, not the synthetic merge commit")
retry_contract_ok = (
    ("--retry 6" in unreal_ci and "--retry-all-errors" in unreal_ci)
    or ("attempt <= 7" in unreal_ci and "retrying in 5 seconds" in unreal_ci)
    or ("for /L %%A in (1,1,7)" in unreal_ci and "Start-Sleep -Seconds 5" in unreal_ci)
    or ("$attempt -le 7" in unreal_ci and "Start-Sleep -Seconds 5" in unreal_ci)
)
if custom_checkout_ok and not retry_contract_ok:
    fail("PG-026: custom exact-commit acquisition must use resilient retries")
if "uses: actions/upload-artifact@v4" in unreal_ci:
    fail("PG-026: failure logging must not depend on artifact upload while storage quota can mask the primary error")
if "group: unreal-build-${{ github.repository }}-ue4-device" not in unreal_ci or "cancel-in-progress: false" not in unreal_ci:
    fail("PG-026: shared Unreal device builds must serialize without interrupting active validation")
if "post-job-runner-dedupe.ps1" in unreal_ci or "delete env.RUNNER_TRACKING_ID" in unreal_ci:
    fail("PG-026: validation must not launch detached runner lifecycle cleanup")
if 'shell: powershell -NoProfile -ExecutionPolicy Bypass -Command ". \'{0}\'"' not in unreal_ci:
    fail("PG-027: self-hosted PowerShell steps must bypass the target machine script execution policy")

quest_cpp = read(SOURCE / "ShireQuestSubsystem.cpp")
definitions = set(re.findall(r'AddQuestDefinition\s*\(\s*TEXT\("([^"]+)"\)', quest_cpp))
if not definitions:
    fail("No quest definitions found in ShireQuestSubsystem.cpp")

references: set[str] = set()
for path in sorted(SOURCE.glob("*.cpp")):
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

router_cpp = read(SOURCE / "ChapterWorldRouter.cpp")

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
shire_world_cpp = read(SOURCE / "ShirePrototypeWorldBuilder.cpp")
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
for path in sorted(SOURCE.glob("*.cpp")):
    text = read(path)
    chapter_refs.update(re.findall(r'NextChapterId\s*=\s*TEXT\("(P1C\d+)"\)', text))
    chapter_refs.update(re.findall(r'StartChapter\s*\(\s*TEXT\("(P1C\d+)"\)', text))
    chapter_refs.update(re.findall(r'TEXT\("(P1C\d+)"\)\s*,\s*TEXT\("[A-Za-z0-9_]+"\)\s*,\s*\d+\s*\)', text))
unknown_chapters = sorted(ref for ref in chapter_refs if ref not in expected_chapters)
if unknown_chapters:
    fail("Unknown runtime chapter references: " + ", ".join(unknown_chapters))

story_beat_refs: set[str] = set()
for path in sorted(SOURCE.glob("*.cpp")):
    if path.name == "ShireStoryPresentationSubsystem.cpp":
        continue
    text = read(path)
    story_beat_refs.update(re.findall(r'StoryBeatId\s*=\s*TEXT\("([^"]+)"\)', text))
    story_beat_refs.update(re.findall(
        r'SpawnQuestTrigger\s*\([^;]*?TEXT\("([A-Za-z0-9_]+)"\)\s*(?:,\s*TEXT\("[A-Za-z0-9_]+"\)|,\s*NAME_None)',
        text,
        flags=re.S,
    ))

presentation_cpp = read(SOURCE / "ShireStoryPresentationSubsystem.cpp")
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
dialogue_cpp = read(SOURCE / "ShireDialogueSubsystem.cpp")
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

audio_cpp = read(SOURCE / "ShireAudioSubsystem.cpp")
if "ResolveVoiceAsset" not in audio_cpp or "/Game/Audio/Voice/" not in audio_cpp:
    fail("Runtime voice asset resolver missing from ShireAudioSubsystem")
if "SpawnSoundAttached" not in audio_cpp or "SpawnSound2D" not in audio_cpp:
    fail("Runtime voice playback must support attached spatial world voice and controlled 2D fallback")

player_cpp = read(SOURCE / "ShirePlayerCharacter.cpp")
player_h = read(SOURCE / "ShirePlayerCharacter.h")

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

enemy_cpp = read(SOURCE / "FellowshipEnemyPrototype.cpp")
save_h = read(SOURCE / "ShireSaveGame.h")
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
npc_cpp = read(SOURCE / "ShireNPC.cpp")
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
for path in sorted(SOURCE.glob("*.cpp")):
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

# Critical runtime handoff guard must explicitly bridge the Shire terminal quest to Bree.
story_flow_cpp = read(SOURCE / "ShireStoryFlowSubsystem.cpp")
if 'QuestId == TEXT("FerryEscape")' not in story_flow_cpp:
    fail("Story-flow guard does not monitor FerryEscape terminal state")
if 'StartChapter(TEXT("P1C02"), TEXT("RoadToBree"), 0)' not in story_flow_cpp:
    fail("Story-flow guard does not hand off Shire terminal state to P1C02 / RoadToBree")
transition_graph["FerryEscape"].add("RoadToBree")

reachable: set[str] = set()
queue = deque([chapter_start_quests["P1C01"]])
while queue:
    quest = queue.popleft()
    if quest in reachable:
        continue
    reachable.add(quest)
    for next_quest in transition_graph.get(quest, set()):
        if next_quest not in reachable:
            queue.append(next_quest)

# Chapter starts are independently testable through debug navigation even when the parser cannot prove every positional call.
for quest in chapter_start_quests.values():
    reachable.add(quest)

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
player_cpp = read(SOURCE / "ShirePlayerCharacter.cpp")
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
audio_h = read(SOURCE / "ShireAudioSubsystem.h")
audio_cpp = read(SOURCE / "ShireAudioSubsystem.cpp")
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
save_h = read(SOURCE / "ShireSaveGame.h")
route_h = read(SOURCE / "ShireRouteState.h")
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

if governor_mode_id == "PIE_VERIFICATION_FREEZE" and verification_gate:
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

# PG-057: current-head PIE claims require exact-commit human evidence.
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
                    "without matching human evidence"
                )
            continue

        tested_commit = str(row.get("tested_commit") or "")
        tested_at = str(row.get("tested_at") or "")
        tester = str(row.get("tester") or "")
        artifacts = row.get("evidence_artifacts", [])
        observations = row.get("observed_details", [])

        if not re.fullmatch(r"[0-9a-fA-F]{40}", tested_commit):
            fail(f"PG-057 {chapter_id} PIE evidence requires an exact 40-char commit SHA")
        if not tested_at:
            fail(f"PG-057 {chapter_id} PIE evidence requires tested_at")
        if not tester:
            fail(f"PG-057 {chapter_id} PIE evidence requires tester")
        if not isinstance(artifacts, list) or len(artifacts) < 1:
            fail(f"PG-057 {chapter_id} PIE evidence requires at least one artifact/log reference")
        if not isinstance(observations, list) or len(observations) < 2:
            fail(f"PG-057 {chapter_id} PIE evidence requires at least two concrete observations")
        if matrix_state == "NOT_RUN":
            fail(
                f"PG-057 {chapter_id} has human PIE evidence but the current-head matrix "
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

if errors:
    print(f"PRE-UNREAL VALIDATION FAILED: {len(errors)} error(s)")
    sys.exit(1)

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

world_builder_h = read(SOURCE / "FellowshipChapterWorldBuilder.h")
world_builder_cpp = read(SOURCE / "FellowshipChapterWorldBuilder.cpp")
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

npc_motion_h = read(SOURCE / "ShireNPC.h")
npc_motion_cpp = read(SOURCE / "ShireNPC.cpp")
for symbol in [
    "TryApplyProductionRig",
    "bUsingSkeletalProductionRig",
    "MotionCadenceScale",
    "MotionStrideScale",
    "MotionIdleScale",
    "DialogueGesture",
    "ABP_%s_Locomotion",
]:
    if symbol not in (npc_motion_h + npc_motion_cpp):
        fail(f"PG-051 character motion invariant missing: {symbol}")

chapter_world_h = read(SOURCE / "FellowshipChapterWorldBuilder.h")
chapter_world_cpp = read(SOURCE / "FellowshipChapterWorldBuilder.cpp")
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

shire_h_cp52 = read(SOURCE / "ShirePrototypeWorldBuilder.h")
shire_cpp_cp52 = read(SOURCE / "ShirePrototypeWorldBuilder.cpp")
bree_h_cp52 = read(SOURCE / "BreePrototypeWorldBuilder.h")
bree_cpp_cp52 = read(SOURCE / "BreePrototypeWorldBuilder.cpp")
fellowship_cpp_cp52 = read(SOURCE / "FellowshipChapterWorldBuilder.cpp")
build_cs_cp52 = read(SOURCE / "ShireJourney.Build.cs")
game_mode_cpp_cp52 = read(SOURCE / "ShireGameMode.cpp")
router_cpp_cp52 = read(SOURCE / "ChapterWorldRouter.cpp")
quest_cpp_cp52 = read(SOURCE / "ShireQuestSubsystem.cpp")
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
    "ShirePlayableStartup: GameMode ready",
    "ShirePlayableStartup: chapter=P1C01 route=%s",
]:
    if startup_symbol not in (game_mode_cpp_cp52 + router_cpp_cp52 + quest_cpp_cp52):
        fail(f"PG-052 playable startup invariant missing: {startup_symbol}")

for workflow_symbol in [
    "pull_request:",
    "Headless playable startup smoke",
    "--mode startup",
    "--mode chapters",
    "--mode state",
]:
    if workflow_symbol not in unreal_workflow_cp52:
        fail(f"PG-052 Unreal boot validation workflow missing: {workflow_symbol}")

if (
    "Scripts/runtime_smoke.py" not in unreal_workflow_cp52
    and "Scripts\\runtime_smoke.py" not in unreal_workflow_cp52
):
    fail("PG-052 Unreal boot validation workflow missing runtime_smoke.py invocation")

# The extracted observer now owns the log name and readiness contract.
runtime_observer_path = ROOT / "Scripts" / "runtime_smoke.py"
if not runtime_observer_path.exists():
    fail("PG-052 runtime observer missing")
else:
    runtime_observer = runtime_observer_path.read_text(encoding="utf-8")
    for observer_symbol in [
        "CI-PlayableStartup",
        "ShirePlayableStartup: GameMode ready",
        "ShirePlayableStartup: chapter=P1C01 route=FrodoMain",
        "FAILURE.search(final_text)",
    ]:
        if observer_symbol not in runtime_observer:
            fail(f"PG-052 runtime observer missing: {observer_symbol}")

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

living_world_h = read(SOURCE / "LivingWorldDirector.h")
living_world_cpp = read(SOURCE / "LivingWorldDirector.cpp")
ambient_cpp = read(SOURCE / "ShireAmbientNPC.cpp")

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
cp54_textures = list(cp54_texture_root.glob("*.bmp")) if cp54_texture_root.exists() else []
if len(cp54_textures) < 17:
    fail(f"PG-054 production texture bank below 17 BMP floor: {len(cp54_textures)}")

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

cp55_ambient_cpp = read(ROOT / "Source" / "ShireJourney" / "ShireAmbientNPC.cpp")
cp55_director_cpp = read(ROOT / "Source" / "ShireJourney" / "LivingWorldDirector.cpp")
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

cp56_shire_cpp = read(ROOT / "Source" / "ShireJourney" / "ShirePrototypeWorldBuilder.cpp")
cp56_ambient_cpp = read(ROOT / "Source" / "ShireJourney" / "ShireAmbientNPC.cpp")
cp56_bree_cpp = read(ROOT / "Source" / "ShireJourney" / "BreePrototypeWorldBuilder.cpp")
cp56_fellowship_cpp = read(ROOT / "Source" / "ShireJourney" / "FellowshipChapterWorldBuilder.cpp")
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

ambient_header_pg59 = read(ROOT / "Source" / "ShireJourney" / "ShireAmbientNPC.h")
ambient_cpp_pg59 = read(ROOT / "Source" / "ShireJourney" / "ShireAmbientNPC.cpp")
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

npc_context_header_pg59 = read(ROOT / "Source" / "ShireJourney" / "ShireNPCContextSubsystem.h")
npc_context_cpp_pg59 = read(ROOT / "Source" / "ShireJourney" / "ShireNPCContextSubsystem.cpp")
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

npc_h_pg60 = read(ROOT / "Source" / "ShireJourney" / "ShireNPC.h")
npc_cpp_pg60 = read(ROOT / "Source" / "ShireJourney" / "ShireNPC.cpp")
ctx_h_pg60 = read(ROOT / "Source" / "ShireJourney" / "ShireNPCContextSubsystem.h")
ctx_cpp_pg60 = read(ROOT / "Source" / "ShireJourney" / "ShireNPCContextSubsystem.cpp")

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

if '? TEXT("Mug") : NAME_None' in read(ROOT / "Source" / "ShireJourney" / "ShirePrototypeWorldBuilder.cpp"):
    fail("PG-060 Shire crowd prop ternary regressed to UE4-incompatible mixed FName/string types")
if '? TEXT("Mug") : NAME_None' in read(ROOT / "Source" / "ShireJourney" / "BreePrototypeWorldBuilder.cpp"):
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

pg81_qh = read(ROOT / "Source" / "ShireJourney" / "ShireQuestSubsystem.h")
pg81_qc = read(ROOT / "Source" / "ShireJourney" / "ShireQuestSubsystem.cpp")
pg81_tc = read(ROOT / "Source" / "ShireJourney" / "ShireTraversalChallenge.cpp")
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

pg82_shire = read(ROOT / "Source" / "ShireJourney" / "ShirePrototypeWorldBuilder.cpp")
pg82_traversal = read(ROOT / "Source" / "ShireJourney" / "ShireTraversalChallenge.cpp")
pg82_player_h = read(ROOT / "Source" / "ShireJourney" / "ShirePlayerCharacter.h")
for pg82_symbol in [
    "SHIRE_QUIET_FEET",
    'TEXT("STEALTH_LITE")',
    "IsCrouchingForStealth",
    "CompleteSideActivityDiscovery",
]:
    if pg82_symbol not in (pg82_shire + pg82_traversal + pg82_player_h):
        fail(f"PG-082 stealth runtime symbol missing: {pg82_symbol}")


# PG-083: PATTERN_MATCH side play must have a real interactable environmental puzzle runtime.
pg83_h = read(SOURCE / "ShireEnvironmentalPuzzle.h")
pg83_cpp = read(SOURCE / "ShireEnvironmentalPuzzle.cpp")
pg83_builder = read(SOURCE / "FellowshipChapterWorldBuilder.cpp")
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

pg84_h = read(SOURCE / "ShireWorldEventInteraction.h")
pg84_cpp = read(SOURCE / "ShireWorldEventInteraction.cpp")
pg84_director_h = read(SOURCE / "LivingWorldDirector.h")
pg84_director_cpp = read(SOURCE / "LivingWorldDirector.cpp")
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

pg85_qh = read(SOURCE / "ShireQuestSubsystem.h")
pg85_qc = read(SOURCE / "ShireQuestSubsystem.cpp")
pg85_ph = read(SOURCE / "ShirePlayerCharacter.h")
pg85_pc = read(SOURCE / "ShirePlayerCharacter.cpp")
pg85_hud = read(SOURCE / "ShireHUD.cpp")
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
pg87_cpp = read(ROOT / "Source" / "ShireJourney" / "ShirePlayerCharacter.cpp")
pg87_h = read(ROOT / "Source" / "ShireJourney" / "ShirePlayerCharacter.h")
for pg87_character in sorted(pg87_required_playables | {"Frodo", "Sam", "Merry", "Pippin"}):
    if f'TEXT("{pg87_character}")' not in pg87_cpp:
        fail(f"PG-087 playable visual mapping missing: {pg87_character}")
for pg87_symbol in ["SupportedPlayableIds", "PrototypeMotionProfile", "SM_ProductionSword", "SM_ProductionBow", "SM_ProductionAxe"]:
    if pg87_symbol not in (pg87_cpp + pg87_h):
        fail(f"PG-087 ensemble production visual symbol missing: {pg87_symbol}")
if "unsupported playable id=%s; using Frodo fallback" not in pg87_cpp:
    fail("PG-087 unsupported playable visual fallback is not explicit")


# PG-088: source-grounded Part I geography must be packaged and visible at runtime.
pg88_build = read(ROOT / "Source" / "ShireJourney" / "ShireJourney.Build.cs")
pg88_qh = read(ROOT / "Source" / "ShireJourney" / "ShireQuestSubsystem.h")
pg88_qc = read(ROOT / "Source" / "ShireJourney" / "ShireQuestSubsystem.cpp")
pg88_hud = read(ROOT / "Source" / "ShireJourney" / "ShireHUD.cpp")
if "Part1ProductionAtlas.json" not in pg88_build:
    fail("PG-088 Part1ProductionAtlas is not packaged")
for pg88_symbol in [
    "FShireChapterProductionDefinition",
    "LoadPart1ProductionAtlas",
    "GetCurrentChapterDisplayName",
    "GetCurrentPrimaryRegionName",
    "GetCurrentMacroRegionName",
    "GetCurrentLandmarkSummary",
    "ProductionAtlas: ready=%s chapters=%d",
]:
    if pg88_symbol not in (pg88_qh + pg88_qc):
        fail(f"PG-088 runtime geography symbol missing: {pg88_symbol}")
if "GetCurrentPrimaryRegionName()" not in pg88_hud:
    fail("PG-088 HUD is not using source-grounded current region naming")

if errors:
    print(f"PRE-UNREAL VALIDATION FAILED: {len(errors)} error(s)")
    for message in errors:
        print(f"ERROR: {message}")
    sys.exit(1)

print("PRE-UNREAL VALIDATION PASSED")
