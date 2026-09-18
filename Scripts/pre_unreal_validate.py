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

# PG-035: lightweight world motion must remain cheap, 3D and region-aware.
ambient_motion_cpp = read(SOURCE / "ShireAmbientNPC.cpp")
shire_world_motion_cpp = read(SOURCE / "ShirePrototypeWorldBuilder.cpp")
bree_world_motion_cpp = read(SOURCE / "BreePrototypeWorldBuilder.cpp")
fellowship_world_motion_cpp = read(SOURCE / "FellowshipChapterWorldBuilder.cpp")
isengard_world_motion_cpp = read(SOURCE / "IsengardPrototypeWorldBuilder.cpp")

for symbol in [
    'RoutineRole == TEXT("Bird")',
    "AddActorWorldOffset(Direction * WalkSpeed * DeltaSeconds, false)",
    "PrototypeWalkPhase += DeltaSeconds * 9.0f",
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
if population_identity.get("proof_limit") != "This is a procedural visual-identity pass, not final character art or visual acceptance.":
    fail("PG-033 CharacterPopulationPlan must preserve proxy/final-art proof boundary")

governor_mode = governor_data.get("development_mode", {}) if governor_data else {}
if governor_mode.get("id") != "BUILD_FIRST_BATCH_MODE":
    fail("PG-033 Governor development mode must record BUILD_FIRST_BATCH_MODE")
if "Do not mark PIE, device, pacing, performance or visual gates PASSED without real evidence." not in governor_mode.get("rules", []):
    fail("PG-033 build-first mode must preserve manual-proof honesty")

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
if editor_probe_marker not in unreal_ci:
    fail("PG-015: Unreal self-hosted editor-closed probe must explicitly exit /b 0")
if "uses: actions/checkout@v4" in unreal_ci:
    fail("PG-026: Unreal self-hosted build must not depend on actions/checkout for exact-commit acquisition")
if "zipball/$env:GITHUB_SHA" not in unreal_ci:
    fail("PG-026: Unreal self-hosted build must download the exact GITHUB_SHA archive")
if "--retry 6" not in unreal_ci or "--retry-all-errors" not in unreal_ci:
    fail("PG-026: exact-commit archive download must use resilient retries")
if "uses: actions/upload-artifact@v4" in unreal_ci:
    fail("PG-026: failure logging must not depend on artifact upload while storage quota can mask the primary error")
if "cancel-in-progress: true" not in unreal_ci:
    fail("PG-026: superseded develop Unreal builds must not block the latest validation run")
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

if errors:
    print(f"PRE-UNREAL VALIDATION FAILED: {len(errors)} error(s)")
    sys.exit(1)

print("PRE-UNREAL VALIDATION PASSED")
