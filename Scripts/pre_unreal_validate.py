#!/usr/bin/env python3
"""Pre-Unreal validation for the Fellowship personal game.

This intentionally checks only invariants that can be verified without an Unreal Engine
installation. A green result does NOT replace a real UE4.27 compile or PIE run.
"""

from __future__ import annotations

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
]

for path in required_files:
    if not path.exists():
        fail(f"Required file missing: {path.relative_to(ROOT)}")

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
expected_chapters = {f"P1C{i:02d}" for i in range(1, 9)}
router_chapters = set(re.findall(r'ChapterId\s*==\s*TEXT\("(P1C\d+)"\)', router_cpp))
missing_chapters = sorted(expected_chapters - router_chapters)
if missing_chapters:
    fail("ChapterWorldRouter is missing runtime chapters: " + ", ".join(missing_chapters))

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
required_actions = ["QuickSave", "QuickLoad", "DebugNextChapter", "DebugPreviousChapter"]
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
