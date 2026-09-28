from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []

def read(relative: str) -> str:
    path = ROOT / relative
    if not path.exists():
        errors.append(f"missing required file: {relative}")
        return ""
    return path.read_text(encoding="utf-8")

header = read("Source/ShireJourney/Public/Settings/ShireGameUserSettings.h")
source = read("Source/ShireJourney/Private/Settings/ShireGameUserSettings.cpp")
engine = read("Config/DefaultEngine.ini")
scalability = read("Config/DefaultScalability.ini")
plan = read("Docs/P1C01_VISUAL_ECONOMY_SETTINGS.md")
state = read("Docs/CURRENT_PROJECT_STATE.md")
matrix = read("Docs/PRODUCTION_COMPLETENESS_MATRIX.md")

for token in ["EShireVideoPreset", "CinematicBalanced", "ApplyPreset", "ApplyCustomScalability", "ApplyDisplaySettings", "ApplyAndSave"]:
    if token not in header:
        errors.append(f"settings header missing contract token: {token}")

for token in ["SetScreenResolution(FIntPoint(1280, 720))", "SetResolutionScaleValueEx", "ApplyNonResolutionSettings", "ConfirmVideoMode", "Profile.ShadowQuality = 0", "Profile.ResolutionScalePercent = 85.0f"]:
    if token not in source:
        errors.append(f"settings source missing contract token: {token}")

if "GameUserSettingsClassName=/Script/ShireJourney.ShireGameUserSettings" not in engine:
    errors.append("DefaultEngine does not select UShireGameUserSettings")

for group in ["ViewDistanceQuality", "AntiAliasingQuality", "ShadowQuality", "PostProcessQuality", "TextureQuality", "EffectsQuality", "FoliageQuality"]:
    for tier in range(4):
        if f"[{group}@{tier}]" not in scalability:
            errors.append(f"scalability tier missing: {group}@{tier}")

if not re.search(r"\[TextureQuality@1\][\s\S]*?r\.Streaming\.PoolSize=800", scalability):
    errors.append("balanced texture tier must retain the bounded 800 MB pool")
if not re.search(r"\[ShadowQuality@1\][\s\S]*?r\.Shadow\.CSM\.MaxCascades=2", scalability):
    errors.append("balanced shadow tier must retain two bounded cascades")
if "recover cost first" not in plan.lower():
    errors.append("visual-economy cost-recovery doctrine missing from settings plan")
if "P1C01 visual-economy graphics/video settings backend" not in state:
    errors.append("CURRENT_PROJECT_STATE missing this source increment")
if "P1C01 visual-economy Graphics/Video settings" not in matrix:
    errors.append("PRODUCTION_COMPLETENESS_MATRIX missing this source increment")

try:
    governor = json.loads(read("Data/ProjectGovernor.json"))
except json.JSONDecodeError as exc:
    errors.append(f"invalid ProjectGovernor JSON: {exc}")
    governor = {}

requirement_ids = {item.get("id") for item in governor.get("requirements", [])}
decision_ids = {item.get("id") for item in governor.get("decisions", [])}
if "REQ-PERF-004" not in requirement_ids:
    errors.append("REQ-PERF-004 missing from ProjectGovernor")
if "DEC-069" not in decision_ids:
    errors.append("DEC-069 missing from ProjectGovernor")

if errors:
    print(f"GRAPHICS_SETTINGS_CONTRACT_FAIL errors={len(errors)}")
    for error in errors:
        print(f"ERROR: {error}")
    sys.exit(1)

print("GRAPHICS_SETTINGS_CONTRACT_PASS presets=4 custom=true target=1280x720")
