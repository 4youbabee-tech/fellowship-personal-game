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

    def test_wardrobe_keeps_full_length_shire_trousers(self):
        source = (ROOT / "prepare_mpfb_shire_variant.py").read_text(encoding="utf-8")
        garment = source.split("# Keep the source trousers full length.", 1)[1].split(
            "# Duplicate fitted upper garment", 1
        )[0]
        self.assertNotIn("bisect_plane", garment)
        self.assertIn("dark wool", garment)

    def test_waistcoat_front_stays_closed_to_prevent_topology_slits(self):
        source = (ROOT / "prepare_mpfb_shire_variant.py").read_text(encoding="utf-8")
        garment = source.split("# Duplicate fitted upper garment", 1)[1].split(
            "# A thin applied shell", 1
        )[0]
        self.assertIn("Keep the fitted source garment closed across the front", garment)
        self.assertNotIn("bmesh.ops.delete", garment)
        self.assertNotIn("for x in (-.052, .052)", garment)
        self.assertIn("# torso bounds; never duplicate the full clothing object", garment)
        self.assertEqual(garment.count("bmesh.ops.bisect_plane"), 1)
        self.assertIn("# a narrow wool panel", garment)
        self.assertIn("placket.faces.new(pv)", garment)
        self.assertIn("waistcoat_front_placket", source)
        self.assertIn("v.co+=v.normal*.004", garment)

    def test_reimport_gate_measures_new_hair_and_caps_total_triangles(self):
        source = (ROOT / "inspect_mpfb_shire_variant.py").read_text(encoding="utf-8")
        self.assertIn("report['hair_triangles']<6000", source)
        self.assertIn("report['total_triangles']>60000", source)

    def test_uv_sphere_faces_are_discovered_without_operator_result_key(self):
        source = (ROOT / "prepare_mpfb_shire_variant.py").read_text(encoding="utf-8")
        self.assertIn("old_faces = set(buttons.faces)", source)
        self.assertIn("set(buttons.faces) - old_faces", source)
        self.assertNotIn("created['faces']", source)


if __name__ == "__main__":
    unittest.main()
