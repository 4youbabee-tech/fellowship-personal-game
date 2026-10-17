"""Guard the source-model hair and garment details that are judged in Blender."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent


class WardrobeQualityContractTests(unittest.TestCase):
    def test_old_stacked_ico_clumps_are_replaced_by_head_weighted_locks(self):
        source = (ROOT / "prepare_mpfb_shire_variant.py").read_text(encoding="utf-8")
        self.assertIn("for i in range(24):", source)
        self.assertIn("centers.append(hair.matrix_world.inverted()", source)
        self.assertIn("head_group.add(list(range(start_curl_vertex", source)
        self.assertNotIn("create_icosphere", source)

    def test_fasteners_are_built_into_the_skinned_waistcoat(self):
        source = (ROOT / "prepare_mpfb_shire_variant.py").read_text(encoding="utf-8")
        self.assertIn("for index in range(5):", source)
        self.assertIn("SHIRE_WAISTCOAT_UPPER_TORSO_WEIGHT_GROUP_MISSING", source)
        self.assertIn("'waistcoat_button_count':5", source)

    def test_reimport_gate_measures_new_hair_and_caps_total_triangles(self):
        source = (ROOT / "inspect_mpfb_shire_variant.py").read_text(encoding="utf-8")
        self.assertIn("report['hair_triangles']<6000", source)
        self.assertIn("report['total_triangles']>60000", source)


if __name__ == "__main__":
    unittest.main()
