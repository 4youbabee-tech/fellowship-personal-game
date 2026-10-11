import copy
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_whole_game_cloud_warehouse_queue import validate


def _valid_queue():
    regions = []
    qc = [
        "source_rights_receipt",
        "sha256_original_receipt",
        "derived_copy_only",
        "blender_static_qc",
        "material_slot_validation",
        "lod_or_culling_plan",
        "collision_strategy",
        "import_batch_manifest",
    ]
    for index in range(28):
        region_id = "REGION_01_SHIRE_HOBBITON" if index == 0 else f"REGION_{index + 1:02d}_TEST"
        regions.append(
            {
                "id": region_id,
                "runtime_status": "RUNTIME_FIRST" if index == 0 else "SOURCE_ONLY_PREP",
                "material_targets": ["stone", "wood"],
                "required_asset_groups": ["core"],
                "qc_required_before_unreal": qc,
            }
        )

    return {
        "status": "ACTIVE_CLOUD_SOURCE_PREP_SELF_HOSTED_RUNTIME_LOCKED",
        "regions": regions,
        "root_cause_fixes": [
            {"blocker": "Git terminal clone/credentials unavailable"},
            {"blocker": "Self-hosted UE4 job queued by source-only metadata"},
            {"blocker": "Linux Blender failed because NumPy was missing"},
            {"blocker": "Binary FBX sources lacked LayerElementSmoothing"},
            {"blocker": "Degenerate faces risk during normalization"},
            {"blocker": "Repeated full scans/builds slowed production"},
        ],
        "material_quality_contract": {
            "texture_sets": ["base_color"],
            "ue4_compatibility": ["PNG_or_TGA"],
            "blender_qc": ["preserve_uvs"],
            "unreal_import_contract": ["material_slot_count_nonzero"],
        },
        "evidence_boundary": "Cloud/source production queue only.",
    }


class WholeGameCloudWarehouseQueueTests(unittest.TestCase):
    def test_valid_minimal_queue_passes(self):
        self.assertEqual(validate(_valid_queue()), [])

    def test_requires_28_regions(self):
        queue = _valid_queue()
        queue["regions"] = queue["regions"][:-1]

        self.assertIn("REGION_COUNT_INVALID:27", validate(queue))

    def test_requires_prior_blocker_root_fixes(self):
        queue = _valid_queue()
        queue["root_cause_fixes"] = queue["root_cause_fixes"][:-1]

        self.assertTrue(any(error.startswith("ROOT_CAUSE_FIXES_MISSING:") for error in validate(queue)))

    def test_requires_region_qc_contract(self):
        queue = copy.deepcopy(_valid_queue())
        queue["regions"][0]["qc_required_before_unreal"] = []

        self.assertTrue(any(error.startswith("REGION_QC_MISSING:REGION_01_SHIRE_HOBBITON") for error in validate(queue)))


if __name__ == "__main__":
    unittest.main()
