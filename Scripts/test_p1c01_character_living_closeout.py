#!/usr/bin/env python3
"""Guard P1C01 character and living-world closeout truth boundary."""
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "Data" / "P1C01CharacterLivingShireCloseoutV1.json"


class P1C01CharacterLivingShireCloseoutTests(unittest.TestCase):
    def load_contract(self):
        return json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_required_named_characters_are_tracked(self):
        data = self.load_contract()
        expected = {
            "PLAYER_FRODO",
            "NPC_BILBO",
            "NPC_GANDALF",
            "NPC_SAM",
            "NPC_MERRY",
            "NPC_PIPPIN",
        }
        actual = {row["id"] for row in data["required_named_characters"]}
        self.assertEqual(expected, actual)

    def test_frodo_is_not_overpromoted_from_technical_winner(self):
        data = self.load_contract()
        frodo = next(row for row in data["required_named_characters"] if row["id"] == "PLAYER_FRODO")
        self.assertEqual("TECHNICAL_WINNER_ONLY_NOT_FINAL_VISUAL", frodo["current_status"])
        self.assertIn("deformation review", frodo["missing_evidence"])
        self.assertIn("PIE visual review", frodo["missing_evidence"])

    def test_living_world_closeout_covers_schedule_dialogue_and_fauna(self):
        data = self.load_contract()
        items = {row["id"] for row in data["living_world_closeout"]}
        self.assertEqual(
            {"NPC_DAILY_SCHEDULES", "CONTEXT_DIALOGUE_GATES", "FAUNA_AMBIENCE_BUDGET"},
            items,
        )

    def test_no_final_acceptance_is_claimed(self):
        data = self.load_contract()
        forbidden = {
            "P1C01_COMPLETE",
            "CHARACTERS_FINAL_VISUAL",
            "PIE_TESTED",
            "DEVICE_TESTED",
            "VISUALLY_ACCEPTED",
            "GATE_6_7_CLOSED",
        }
        self.assertEqual(forbidden, set(data["not_claimed"]))
        self.assertEqual(
            "ENGINE_IMPORT_GREEN_CHARACTER_VISUAL_RUNTIME_CLOSEOUT_PENDING",
            data["status"],
        )


if __name__ == "__main__":
    unittest.main()
