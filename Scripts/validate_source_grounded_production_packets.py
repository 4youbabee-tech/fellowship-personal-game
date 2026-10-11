#!/usr/bin/env python3
"""Validate source-grounded production packets for cloud-safe Shire production."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET_PATH = ROOT / "Data" / "SourceGroundedProductionPacketsV1.json"

REQUIRED_AUTHORITY = {
    "current_project_rules_and_owner_approved_decisions",
    "film_trilogy_and_supplied_screenplays",
    "tolkien_book_appendices_and_project_lore_files",
    "project_sources_01_to_10",
    "external_references_fan_art_and_generated_visual_aids",
}

REQUIRED_LICENSE_TIERS = {
    "GREEN-OPEN",
    "GREEN-LICENSED",
    "BLUE-PERSONAL",
    "YELLOW-PER-ASSET",
    "REFERENCE-ONLY",
    "QUARANTINE",
    "DISABLED",
}

REQUIRED_PACKETS = {
    "P1C01_SHIRE_LOCATION_STATE_PACKET",
    "P1C01_BAG_END_INTERIOR_PACKET",
    "P1C01_HOBBIT_CHARACTER_PACKET",
    "P1C01_GAMEPLAY_MISSION_PACKET",
    "P1C01_AUDIO_UI_ARABIC_PACKET",
    "P1C01_LIVING_WORLD_PACKET",
    "P1C01_MATERIAL_TECH_PACKET",
}

FORBIDDEN_CLAIMS = {
    "PIE_TESTED",
    "DEVICE_TESTED",
    "VISUALLY_ACCEPTED",
    "GATE_6_ACCEPTED",
    "GATE_7_ACCEPTED",
    "P1C01_COMPLETE",
}


def load_packet(path: Path = PACKET_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_subset(name: str, expected: set[str], actual: list[str]) -> None:
    missing = sorted(expected.difference(actual))
    if missing:
        raise SystemExit(f"{name}_MISSING: {', '.join(missing)}")


def validate_packet(packet: dict) -> None:
    if packet.get("status") != "ACTIVE_CLOUD_SOURCE_PREP_READY":
        raise SystemExit("SOURCE_GROUNDED_PACKET_STATUS_INVALID")

    assert_subset(
        "SOURCE_AUTHORITY_PRIORITY",
        REQUIRED_AUTHORITY,
        packet.get("source_authority_priority", []),
    )

    tiers = packet.get("external_resource_intake_policy", {}).get("license_tiers", [])
    assert_subset("LICENSE_TIER", REQUIRED_LICENSE_TIERS, tiers)

    packet_ids = [entry.get("id") for entry in packet.get("p1c01_packets", [])]
    assert_subset("P1C01_PACKET", REQUIRED_PACKETS, packet_ids)

    regions = packet.get("whole_game_source_guided_regions", [])
    if len(regions) < 28:
        raise SystemExit(f"REGION_GUIDANCE_COUNT_TOO_LOW: {len(regions)}")

    required_evidence = packet.get("evidence_boundary", {}).get("not_claimed_until_runner_evidence", [])
    assert_subset("RUNNER_EVIDENCE_BOUNDARY", FORBIDDEN_CLAIMS, required_evidence)

    serialized = json.dumps(packet, ensure_ascii=False)
    for claim in FORBIDDEN_CLAIMS:
        if claim in serialized and claim not in required_evidence:
            raise SystemExit(f"FORBIDDEN_RUNTIME_ACCEPTANCE_CLAIM_OUTSIDE_BOUNDARY: {claim}")


def main() -> int:
    validate_packet(load_packet())
    print("SOURCE_GROUNDED_PRODUCTION_PACKETS_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
