#!/usr/bin/env python3
"""Regression: chapter without a density override must use loaded global defaults."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
cpp = (ROOT / "Source/ShireJourney/Private/World/LivingWorldDirector.cpp").read_text(encoding="utf-8")
hdr = (ROOT / "Source/ShireJourney/Public/World/LivingWorldDirector.h").read_text(encoding="utf-8")
capture = cpp.index("BasePopulationInnerRadius = PopulationInnerRadius;")
profiles = cpp.index("PopulationProfilesByChapter.Empty();")
assert capture < profiles, "Base values must be snapshotted before chapter profiles load"
match = re.search(r"void ALivingWorldDirector::ApplyPopulationProfile\(\)\s*\{(.*?)\n\}", cpp, re.S)
assert match, "ApplyPopulationProfile missing"
body = match.group(1)
fallback = re.search(r"if \(!Profile\)\s*\{(.*?)\n\s*return;", body, re.S)
assert fallback, "No missing-profile fallback"
for field in ("SpawnInterval", "InnerRadius", "OuterRadius", "CullRadius"):
    assert f"Population{field} = BasePopulation{field};" in fallback.group(1), field
    assert f"BasePopulation{field}" in hdr, field
assert "DangerPopulationFraction = 0.50f;" in fallback.group(1)
print("LIVING_WORLD_DENSITY_FALLBACK_STATIC_PASS")

# Guard against accidentally declaring the actor fallback values inside the
# chapter-profile struct, which compiles in static text tests but fails UE4 C++.
struct_start = hdr.index("struct FChapterPopulationProfile")
struct_end = hdr.index("UPROPERTY()", struct_start)
actor_member_start = hdr.index("float PopulationInnerRadius")
actor_member_end = hdr.index("int32 MaxActiveMicroEvents", actor_member_start)
for field in ("BasePopulationInnerRadius", "BasePopulationOuterRadius", "BasePopulationCullRadius", "BasePopulationSpawnInterval"):
    assert field not in hdr[struct_start:struct_end], f"{field} must not be inside FChapterPopulationProfile"
    assert field in hdr[actor_member_start:actor_member_end], f"{field} must be an ALivingWorldDirector member"
