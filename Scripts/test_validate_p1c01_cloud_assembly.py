import copy
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_p1c01_cloud_assembly import validate


def _valid_plan():
    return {
        "chapter": "P1C01",
        "status": "CLOUD_READY_SELF_HOSTED_IMPORT_PENDING",
        "required_scene_coverage": [
            "BAG_END_EXTERIOR",
            "BAG_END_INTERIOR",
            "HOBBITON_CORE",
            "BAGSHOT_ROW",
            "PARTY_FIELD",
            "SHIRE_ROADS",
            "WATER_MILL_BRIDGE",
            "GARDENS_ORCHARDS",
            "AMBIENT_NATURE",
        ],
        "scene_assembly_batches": [
            {
                "id": "CORE",
                "areas": ["BAG_END_EXTERIOR"],
                "materials_from_wave": ["SH_GRASS_GROUND"],
                "asset_families": ["round door"],
                "runner_gate": "SELF_HOSTED_IMPORT_REQUIRED",
                "activities": ["ACT_F1_01", "ACT_F1_02", "ACT_F1_03", "ACT_F1_04"],
            }
        ],
        "character_roster": [
            {"id": "PLAYER_FRODO"},
            {"id": "NPC_BILBO"},
            {"id": "NPC_GANDALF"},
            {"id": "NPC_SAM"},
            {"id": "NPC_MERRY"},
            {"id": "NPC_PIPPIN"},
        ],
        "living_shire_director_inputs": [{}, {}, {}],
        "evidence_boundary": "No runtime acceptance is claimed.",
    }


class ValidateP1C01CloudAssemblyTests(unittest.TestCase):
    def test_valid_minimal_plan_passes(self):
        self.assertEqual(validate(_valid_plan()), [])

    def test_missing_character_fails(self):
        plan = _valid_plan()
        plan["character_roster"] = plan["character_roster"][:-1]

        self.assertTrue(any(error.startswith("MISSING_CHARACTERS") for error in validate(plan)))

    def test_runner_gate_is_required_for_batches(self):
        plan = copy.deepcopy(_valid_plan())
        plan["scene_assembly_batches"][0]["runner_gate"] = "CLOUD_ONLY"

        self.assertIn("BATCH_RUNNER_GATE_INVALID:CORE", validate(plan))


if __name__ == "__main__":
    unittest.main()
