#!/usr/bin/env python3
"""Regression checks for the P1C01 final Shire closure contract."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "Data" / "P1C01FinalChapterClosureWaveV1.json"
BUILD_CS_PATH = ROOT / "Source" / "ShireJourney" / "ShireJourney.Build.cs"


class P1C01FinalClosureContractTests(unittest.TestCase):
    def load_contract(self) -> dict:
        self.assertTrue(CONTRACT_PATH.is_file(), f"Missing {CONTRACT_PATH}")
        return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_final_closure_contract_is_staged_and_truthful(self) -> None:
        contract = self.load_contract()
        build_cs = BUILD_CS_PATH.read_text(encoding="utf-8")

        self.assertEqual(contract["runtime_chapter"], "P1C01")
        self.assertEqual(contract["status"], "RUNTIME_INTEGRATION_ACTIVE_NOT_ACCEPTED")
        self.assertIn(
            'RuntimeDependencies.Add("$(ProjectDir)/Data/P1C01FinalChapterClosureWaveV1.json", StagedFileType.NonUFS);',
            build_cs,
        )

        blocker = contract["current_primary_blocker"]
        self.assertEqual(blocker["latest_failed_run"], 38083290428)
        self.assertIn("DEGENERATE_FACE:rock_face_02", blocker["failed_log_signal"])

        acceptance = contract["acceptance_boundary"]
        for key in ("pie_tested", "device_tested", "human_visual_accepted", "gate_6", "gate_7"):
            self.assertFalse(acceptance[key], f"{key} must stay false until evidence is recorded")

    def test_final_closure_tracks_required_p1c01_surface(self) -> None:
        contract = self.load_contract()
        dod = contract["definition_of_done"]
        for key in ("visual_world", "living_world", "characters", "gameplay", "acceptance_evidence_required"):
            self.assertIn(key, dod)

        required_characters = set(dod["characters"]["principal_required"])
        self.assertTrue({"Frodo", "Bilbo", "Gandalf", "Sam", "Merry", "Pippin"}.issubset(required_characters))

        proof_items = "\n".join(contract["proof_needed_next"])
        self.assertIn("P1C01_PBR_DECOR_RUNTIME", proof_items)
        self.assertIn("LayerElementSmoothing", proof_items)


if __name__ == "__main__":
    unittest.main()
