import copy
import json
from pathlib import Path
import unittest
from governor_work_start import ROOT, PRODUCERS, ManagerRejected, validate_contract

class GovernorWorkStartTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g=json.loads((ROOT/"Data/ProjectGovernor.json").read_text(encoding="utf-8"))
        cls.m=json.loads((ROOT/"Data/MaximumSafeProductionModeV1.json").read_text(encoding="utf-8"))
    def test_five_lanes(self):
        for lane in PRODUCERS:
            with self.subTest(lane=lane):
                self.assertEqual(validate_contract(self.g,self.m,lane,ROOT)["lane"],lane)
    def test_decision_cannot_disappear(self):
        g=copy.deepcopy(self.g)
        next(d for d in g["decisions"] if d["id"]=="DEC-104")["status"]="PROPOSED"
        with self.assertRaisesRegex(ManagerRejected,"DEC-104"):
            validate_contract(g,self.m,"VISUAL_WORLD_PREP",ROOT)
    def test_unsafe_second_warehouse_writer(self):
        m=copy.deepcopy(self.m)
        m["five_lane_operating_overlay"]["tracks"][2]["persistent_writer"]=True
        with self.assertRaisesRegex(ManagerRejected,"WAREHOUSE_WRITER_COUNT_UNSAFE"):
            validate_contract(self.g,m,"WAREHOUSE_ASSET_INTAKE",ROOT)
    def test_runtime_gate_blocks_runtime_only(self):
        g=copy.deepcopy(self.g)
        g["active_gate"]["blocks_major_feature_expansion"]=True
        with self.assertRaisesRegex(ManagerRejected,"RUNTIME_BLOCKED"):
            validate_contract(g,self.m,"RUNTIME_BUILD",ROOT)
        validate_contract(g,self.m,"VISUAL_WORLD_PREP",ROOT)
    def test_workflow_manager_entries(self):
        required={
          ".github/workflows/unreal-build-validation.yml":"governor_work_start.py --lane RUNTIME_BUILD",
          ".github/workflows/p1c01-two-wave-checkpoint-warehouse.yml":"governor_work_start.py --lane WAREHOUSE_ASSET_INTAKE",
          ".github/workflows/p1c01-hero-skeletal-candidate-wave.yml":"-Lane SKELETAL_CHARACTER_PREP",
          ".github/workflows/p1c01-human-wave2.yml":"governor_work_start.py --lane SKELETAL_CHARACTER_PREP",
          ".github/workflows/p1c01-adaptive-highfidelity-source.yml":"governor_work_start.py --lane VISUAL_WORLD_PREP",
          ".github/workflows/p1c01-chapter-closure.yml":"-Lane GAMEPLAY_PRESENTATION_PREP",
          ".github/workflows/p1c01-five-lane-maxsafe.yml":'governor_work_start.py --lane "${{ matrix.lane }}"',
        }
        for p,needle in required.items():
            with self.subTest(p=p):
                self.assertIn(needle,(ROOT/p).read_text(encoding="utf-8"))
        self.assertIn("group: warehouse-stage-${{ github.repository }}",(ROOT/".github/workflows/p1c01-chapter-closure.yml").read_text(encoding="utf-8"))
if __name__=="__main__": unittest.main()
