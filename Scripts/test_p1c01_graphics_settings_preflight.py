#!/usr/bin/env python3
"""Runnerless preflight for the P1C01 Graphics/Video settings lane.

This test intentionally validates only source/governance readiness. It does not
claim Unreal compilation, PIE, device, visual, FPS, VRAM, hitch, or performance
verification.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "Data" / "P1C01GraphicsSettingsImplementationContractV1.json"
GOVERNOR = ROOT / "Data" / "ProjectGovernor.json"
SCALABILITY = ROOT / "Config" / "DefaultScalability.ini"

EXPECTED_TEXTURE_POOLS = {0: 600, 1: 800, 2: 1000}
EXPECTED_FOLIAGE_TIER_2 = 0.70
RESERVED_REQUIREMENT = "REQ-PERF-004"
RESERVED_DECISION = "DEC-075"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def parse_scalability_value(text: str, section: str, key: str) -> float:
    match = re.search(
        rf"(?ms)^\[{re.escape(section)}\]\s*(.*?)(?=^\[|\Z)",
        text,
    )
    require(match is not None, f"Missing scalability section: {section}")
    body = match.group(1)
    value_match = re.search(
        rf"(?m)^{re.escape(key)}\s*=\s*([^\r\n]+)\s*$",
        body,
    )
    require(value_match is not None, f"Missing {key} in {section}")
    return float(value_match.group(1).strip())


def main() -> int:
    contract = load_json(CONTRACT)
    governor = load_json(GOVERNOR)
    scalability_text = SCALABILITY.read_text(encoding="utf-8")

    require(
        contract.get("scope") == "W01_P1C01_PRODUCTION_VERTICAL_SLICE",
        "Graphics settings contract must remain P1C01-scoped.",
    )
    authority = contract.get("authority", {})
    require(
        authority.get("governor_requirement") == RESERVED_REQUIREMENT,
        "Contract requirement reservation drifted.",
    )
    require(
        authority.get("governor_decision_reserved") == RESERVED_DECISION,
        "Contract decision reservation drifted.",
    )

    requirements = {item.get("id"): item for item in governor.get("requirements", [])}
    decisions = {item.get("id"): item for item in governor.get("decisions", [])}

    # The reservation may be absent before the ledger/governor commit lands.
    # If another lane occupies either ID, fail closed instead of silently
    # renumbering the settings authority.
    if RESERVED_REQUIREMENT in requirements:
        req = requirements[RESERVED_REQUIREMENT]
        require(
            "graphics" in (req.get("title", "") + " " + req.get("intent", "")).lower()
            or "video" in (req.get("title", "") + " " + req.get("intent", "")).lower(),
            f"{RESERVED_REQUIREMENT} is occupied by an unrelated requirement.",
        )

    if RESERVED_DECISION in decisions:
        decision = decisions[RESERVED_DECISION]
        title_and_resolution = (
            decision.get("title", "") + " " + decision.get("resolution", "")
        ).lower()
        require(
            "graphics" in title_and_resolution
            or "video" in title_and_resolution
            or "visual-economy" in title_and_resolution,
            f"{RESERVED_DECISION} is occupied by an unrelated decision.",
        )

    presets = contract.get("presets", {})
    require(
        list(presets.keys())
        == ["Performance", "CinematicBalanced", "High", "Ultra", "Custom"],
        "Preset set/order drifted.",
    )
    require(
        presets["CinematicBalanced"].get("intent")
        == "visually strong default with bounded cost",
        "Cinematic Balanced must remain the visually strong default contract.",
    )
    require(
        contract.get("target_floor", {}).get("resolution") == "1280x720",
        "Target floor resolution changed.",
    )
    require(
        contract.get("target_floor", {}).get("fps_target") == 30,
        "Target floor FPS changed.",
    )

    for tier, expected_pool in EXPECTED_TEXTURE_POOLS.items():
        actual = parse_scalability_value(
            scalability_text, f"TextureQuality@{tier}", "r.Streaming.PoolSize"
        )
        require(
            int(actual) == expected_pool,
            f"Texture pool tier {tier} drifted: expected {expected_pool}, got {actual}.",
        )

    foliage_tier_2 = parse_scalability_value(
        scalability_text, "FoliageQuality@2", "foliage.DensityScale"
    )
    require(
        abs(foliage_tier_2 - EXPECTED_FOLIAGE_TIER_2) < 1e-6,
        "Foliage tier 2 density anchor drifted.",
    )

    visual_economy = contract.get("visual_economy", {})
    recover_first = set(visual_economy.get("recover_cost_first", []))
    required_recovery = {
        "duplicate_actors",
        "far_shadows",
        "overdraw",
        "translucency",
        "redundant_lights",
        "uninstanced_repetition",
        "unnecessary_tick",
        "invisible_or_far_detail",
    }
    require(
        required_recovery.issubset(recover_first),
        "Permanent visual-economy recovery order is incomplete.",
    )

    print(
        "P1C01_GRAPHICS_SETTINGS_PREFLIGHT_PASS "
        f"requirement={RESERVED_REQUIREMENT} decision={RESERVED_DECISION} "
        "target=1280x720@30 hosted_static_only=true"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
