#!/usr/bin/env python3
"""Regression checks for the P1C01 final Shire closure contract."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "Data" / "P1C01FinalChapterClosureWaveV1.json"


class P1C01FinalClosureContractTests(unittest.TestCase):
    def load_contract(self) -> dict:
        self.assertTrue(CONTRACT_PATH.is_file(), f"Missing {CONTRACT_PATH}")
        return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_final_closure_contract_is_source_only_and_truthful(self) -> None:
        contract = self.load_contract()

        self.assertEqual(contract["runtime_chapter"], "P1C01")
        self.assertEqual(contract["status"], "SOURCE_ONLY_CLOSURE_CONTRACT_NOT_RUNTIME_ACCEPTED")
        self.assertEqual(contract["salvage_provenance"]["source_pr"], 355)
        self.assertEqual(contract["current_primary_blocker"]["status"], "HISTORICAL_EVIDENCE_NOT_LIVE_GATE")

        blocker = contract["current_primary_blocker"]
        self.assertEqual(blocker["latest_failed_run"], 38083290428)
        self.assertIn("DEGENERATE_FACE:rock_face_02", blocker["failed_log_signal"])

        acceptance = contract["acceptance_boundary"]
        for key in ("pie_tested", "device_tested", "visually_accepted", "gate_6_accepted", "gate_7_accepted"):
            self.assertFalse(acceptance[key], f"{key} must stay false until evidence is recorded")

    def test_final_closure_tracks_required_p1c01_surface(self) -> None:
        contract = self.load_contract()
        dod = contract["definition_of_done"]
        for key in ("visual_world", "living_world", "characters", "gameplay", "acceptance_evidence_required"):
            self.assertIn(key, dod)

        required_characters = set(dod["characters"])
        self.assertTrue({"Frodo", "Bilbo", "Gandalf", "Sam", "Merry", "Pippin"}.issubset(required_characters))

        proof_items = "\n".join(contract["current_primary_blocker"]["proof_needed_next"])
        self.assertIn("P1C01_PBR_DECOR_RUNTIME", proof_items)
        self.assertIn("LayerElementSmoothing", proof_items)


if __name__ == "__main__":
    unittest.main()
