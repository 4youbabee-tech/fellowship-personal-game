import json
import unittest
from pathlib import Path

from validate_source_grounded_production_packets import (
    FORBIDDEN_CLAIMS,
    REQUIRED_LICENSE_TIERS,
    REQUIRED_PACKETS,
    load_packet,
    validate_packet,
)


class SourceGroundedProductionPacketsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = load_packet()

    def test_required_packets_are_present(self):
        packet_ids = {entry["id"] for entry in self.packet["p1c01_packets"]}
        self.assertTrue(REQUIRED_PACKETS.issubset(packet_ids))

    def test_license_tiers_preserve_fast_but_safe_intake(self):
        tiers = set(self.packet["external_resource_intake_policy"]["license_tiers"])
        self.assertTrue(REQUIRED_LICENSE_TIERS.issubset(tiers))

    def test_region_guidance_covers_whole_game_queue(self):
        regions = self.packet["whole_game_source_guided_regions"]
        self.assertGreaterEqual(len(regions), 28)
        self.assertTrue(any(region["id"] == "REGION_01_SHIRE_HOBBITON" for region in regions))

    def test_runtime_acceptance_claims_are_only_boundary_markers(self):
        serialized = json.dumps(self.packet, ensure_ascii=False)
        boundary = set(self.packet["evidence_boundary"]["not_claimed_until_runner_evidence"])
        self.assertTrue(FORBIDDEN_CLAIMS.issubset(boundary))
        for claim in FORBIDDEN_CLAIMS:
            self.assertIn(claim, serialized)

    def test_validator_accepts_current_packet(self):
        validate_packet(self.packet)


if __name__ == "__main__":
    unittest.main()
