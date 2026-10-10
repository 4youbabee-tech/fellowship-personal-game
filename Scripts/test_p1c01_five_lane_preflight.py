"""Regression for the governor-authorized five independent hosted preflights."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p1c01_five_lane_preflight import LANES, LaneError, evaluate


class FiveLaneTests(unittest.TestCase):
    def test_all_five_lanes_have_authorized_read_only_reports(self):
        self.assertEqual(len(LANES), 5)
        self.assertEqual(len(set(LANES)), 5)
        for lane in LANES:
            with self.subTest(lane=lane):
                report = evaluate(lane)
                self.assertEqual(report["result"], "SOURCE_READ_ONLY_PREFLIGHT_PASS")
                self.assertEqual(report["truth_state"], "STATIC_METADATA_ONLY")
                self.assertFalse(report["persistent_warehouse_changed"])
                self.assertFalse(report["unreal_runtime_changed"])

    def test_warehouse_covers_entire_candidate_queue(self):
        item = evaluate("WAREHOUSE_ASSET_INTAKE")["detail"]
        self.assertEqual(item["source_candidates_reviewed"], len(item["candidate_rows"]))
        self.assertGreaterEqual(item["source_candidates_reviewed"], 20)
        self.assertEqual(item["downloaded_file_count_this_lane"], 0)

    def test_shire_visible_world_is_complete_as_inventory_not_runtime(self):
        item = evaluate("VISUAL_WORLD_PREP")["detail"]
        self.assertGreaterEqual(item["all_visual_slots_reviewed"], 150)
        self.assertIn("BUCKLEBURY_FERRY", item["priority_cells"])
        self.assertEqual(item["new_ue_import_count"], 0)

    def test_unsafe_unknown_lane_is_rejected(self):
        with self.assertRaisesRegex(LaneError, "UNKNOWN_LANE"):
            evaluate("IMPORT_P1C02")


if __name__ == "__main__":
    unittest.main()
