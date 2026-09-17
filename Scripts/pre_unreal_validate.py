#!/usr/bin/env python3
"""Pre-Unreal validation for the Fellowship personal game.

This intentionally checks only invariants that can be verified without an Unreal Engine
installation. A green result does NOT replace a real UE4.27 compile or PIE run.
"""

from __future__ import annotations

import json
import re
import sys
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
    chapter_refs.update(re.findall(r'TEXT\("(P1C\d+)"\)\s*,\s*TEXT\("[A-Za-z0-9_]+"\)\s*,\s*\d+\s*\)', text))
unknown_chapters = sorted(ref for ref in chapter_refs if ref not in expected_chapters)
if unknown_chapters:
    fail("Unknown runtime chapter references: " + ", ".join(unknown_chapters))

# Story presentation coverage: every story beat referenced by runtime builders must have a cue.
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

for dirname in ["Binaries", "DerivedDataCache", "Intermediate", "Saved", ".vs"]:
    if (ROOT / dirname).exists():
        fail(f"Generated directory should not be committed: {dirname}")

engine_ini = read(ROOT / "Config" / "DefaultEngine.ini")
if "ShireGameMode" not in engine_ini:
    fail("DefaultEngine.ini does not reference ShireGameMode")
if "r.DefaultFeature.MotionBlur=False" not in engine_ini:
    warn("Motion blur low-spec default is not explicitly disabled")

# Input mappings must match the names bound by ShirePlayerCharacter. This catches
# harmless-looking renames that would otherwise break quick save/load or PIE chapter jumps.
input_ini = read(ROOT / "Config" / "DefaultInput.ini")
player_cpp = read(SOURCE / "ShirePlayerCharacter.cpp")
required_actions = ["QuickSave", "QuickLoad", "DebugNextChapter", "DebugPreviousChapter"]
for action in required_actions:
    if f'ActionName="{action}"' not in input_ini:
        fail(f"DefaultInput.ini missing action mapping: {action}")
    if f'BindAction(TEXT("{action}")' not in player_cpp:
        fail(f"ShirePlayerCharacter.cpp missing action binding: {action}")

print(
    f"Validated {len(list(SOURCE.glob('*.cpp')))} cpp files, "
    f"{len(list(SOURCE.glob('*.h')))} headers, {len(definitions)} quest definitions, "
    f"{len(expected_chapters)} runtime chapters, {len(presentation_beats)} presentation cues."
)
for message in warnings:
    print(f"WARNING: {message}")
for message in errors:
    print(f"ERROR: {message}")

if errors:
    print(f"PRE-UNREAL VALIDATION FAILED: {len(errors)} error(s)")
    sys.exit(1)

print("PRE-UNREAL VALIDATION PASSED")
