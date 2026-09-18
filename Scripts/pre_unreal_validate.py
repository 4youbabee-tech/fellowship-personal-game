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

# PG-013: UE4.27 UAssetImportTask does not expose bAsync. Keep the production
# import commandlet on the UE4.27-compatible task API so the real editor build
# cannot regress to C2039 before asset import even begins.
production_import_cpp = read(
    ROOT / "Source" / "ShireJourneyEditorTools" / "Private" / "ShireProductionImportCommandlet.cpp"
)
if "Task->bAsync" in production_import_cpp or "->bAsync" in production_import_cpp:
    fail("PG-013: UE4.27 UAssetImportTask must not use unsupported bAsync")

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
    f"Validated {len(list(SOURCE.glob('*.cpp')))} cpp files, "
    f"{len(list(SOURCE.glob('*.h')))} headers, {len(definitions)} quest definitions, "
    f"{len(expected_chapters)} runtime chapters, {len(presentation_beats)} presentation cues, "
    f"{len(dialogue_sequences)} dialogue sequences."
)
for message in warnings:
    print(f"WARNING: {message}")
for message in errors:
    print(f"ERROR: {message}")

if errors:
    print(f"PRE-UNREAL VALIDATION FAILED: {len(errors)} error(s)")
    sys.exit(1)

print("PRE-UNREAL VALIDATION PASSED")
