#!/usr/bin/env python3
"""Fast M0 source-only guard. No simulation of Unreal evidence."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class M0QuickIndexContract(unittest.TestCase):
    def test_manager_remains_sole_authority_and_status_is_short(self):
        text=(ROOT/"Docs/CURRENT_STATE_SHORT.md").read_text(encoding="utf-8")
        lines=text.splitlines()
        self.assertLess(len(lines),200)
        for token in ("Data/ProjectGovernor.json","PES-002","PR #477","Frodo",
                      "NOT RUN","M0 fast route","unverified"):
            self.assertTrue(token.lower() in text.lower(),token)
        gov=json.loads((ROOT/"Data/ProjectGovernor.json").read_text(encoding="utf-8"))
        p=gov["pes002_owner_acceleration_2026_10_15"]
        self.assertEqual(p["active_pes"],gov["pes_session_transition_2026_10_14"]["active_session"])
        self.assertEqual(p["integration_pr"],477)
        self.assertTrue(p["operating_policy"]["no_deleted_history"])
        self.assertEqual(p["operating_policy"]["m0_quick_index"],"Docs/CURRENT_STATE_SHORT.md")
        self.assertEqual(p["planned_implementation"][4]["status"],"NOT_RUN")
        self.assertTrue((ROOT/"Docs/PES002_PRODUCTION_ACCELERATION_DECISIONS.md").exists())
        for old in ("CURRENT_PROJECT_STATE.md","PRODUCTION_COMPLETENESS_MATRIX.md","WORLD_DETAIL_LEDGER.md"):
            self.assertTrue((ROOT/"Docs"/old).stat().st_size>100000)

if __name__=="__main__":
    unittest.main()
