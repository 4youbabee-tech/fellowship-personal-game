import re
import tempfile
import unittest
from pathlib import Path

import warning_debt_guard as guard


class WarningDebtGuardTests(unittest.TestCase):
    def test_smoothing_warning_source_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "CI-ProductionAssetImport.log"
            log.write_text("Importing /assets/shire/bridge.fbx\nNo smoothing group information was found\n", encoding="utf-8")
            evidence = guard.smoothing_warning_sources([log])
            self.assertEqual(len(evidence), 1)
            self.assertEqual(evidence[0][2], "/assets/shire/bridge.fbx")
            self.assertEqual(evidence[0][1], 2)

    def test_repeated_same_mesh_counts_once(self):
        text = "\n".join([
            "FBXImport: Warning: SM_Frodo_Head has degenerate tangent bases",
            "LogInit: Display: FBXImport: Warning: SM_Frodo_Head has degenerate tangent bases",
            "FBXImport: Warning: SM_Frodo_Head has degenerate tangent bases",
        ])
        pattern = re.compile(r"\b(SM_[A-Za-z0-9_]+) has degenerate tangent bases", re.I)
        count, identities = guard.measure(text, pattern, 1)
        self.assertEqual(count, 1)
        self.assertEqual(identities, ["SM_Frodo_Head"])

    def test_distinct_meshes_remain_distinct_debt(self):
        text = "\n".join([
            "SM_Frodo_Head has some nearly zero bi-normals",
            "SM_Gandalf_Head has some nearly zero bi-normals",
            "SM_Frodo_Head has some nearly zero bi-normals",
        ])
        pattern = re.compile(r"\b(SM_[A-Za-z0-9_]+) has some nearly zero bi-normals", re.I)
        count, identities = guard.measure(text, pattern, 1)
        self.assertEqual(count, 2)
        self.assertEqual(identities, ["SM_Frodo_Head", "SM_Gandalf_Head"])

    def test_tangent_warning_categories_are_zero_tolerance(self):
        checks = {name: ceiling for name, _pattern, ceiling, _group, _scope in guard.CHECKS}
        self.assertEqual(checks["Degenerate tangent bases"], 0)
        self.assertEqual(checks["Nearly-zero tangents"], 0)
        self.assertEqual(checks["Nearly-zero binormals"], 0)
        self.assertEqual(checks["Missing production master surface"], 0)
        self.assertEqual(checks["Streaming pool scalability override warnings"], 0)

    def test_missing_package_deduplicates_across_runtime_logs(self):
        text = "\n".join([
            "Failed to load '/Game/Production/World/Moria/M_Missing.M_Missing'",
            "Failed to load '/Game/Production/World/Moria/M_Missing.M_Missing'",
        ])
        pattern = re.compile(r"Failed to load '(/Game/Production/World/[^']+)'", re.I)
        count, identities = guard.measure(text, pattern, 1)
        self.assertEqual(count, 1)
        self.assertEqual(identities, ["/Game/Production/World/Moria/M_Missing.M_Missing"])

    def test_import_probe_warning_is_not_runtime_debt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            import_log = root / "CI-ProductionAssetImport.log"
            runtime_log = root / "CI-PlayableStartup.log"
            import_log.write_text(
                "Failed to load '/Game/Production/World/Shire/Grass': Can't find file.\n",
                encoding="utf-8",
            )
            runtime_log.write_text("PlayableStartup: PASS\n", encoding="utf-8")
            text = guard.collect_text([import_log, runtime_log], "runtime")
            self.assertNotIn("/Game/Production/World/Shire/Grass", text)

    def test_runtime_missing_package_is_still_hard_debt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runtime_log = root / "CI-ChapterAudit-P1C01.log"
            runtime_log.write_text(
                "Failed to load '/Game/Production/World/Shire/Grass': Can't find file.\n",
                encoding="utf-8",
            )
            text = guard.collect_text([runtime_log], "runtime")
            self.assertIn("/Game/Production/World/Shire/Grass", text)

    def test_all_transaction_runtime_logs_are_in_runtime_scope(self):
        for name in [
            "CI-TransitionAudit.log",
            "CI-FaultAudit.log",
            "CI-PendingTransitionAudit.log",
            "CI-PersistenceEdgeAudit.log",
        ]:
            self.assertTrue(guard.is_runtime_log(Path(name)), name)

    def test_smoothing_diagnostics_include_file_and_line_without_suppressing_debt(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "CI-ProductionAssetImport.log"
            log.write_text("Importing /tmp/test_house.fbx\\nFBXImport: No smoothing group information was found\\n", encoding="utf-8")
            evidence = guard.smoothing_warning_sources([log])
            self.assertEqual(len(evidence), 1)
            self.assertEqual(evidence[0][:3], ("CI-ProductionAssetImport.log", 2, "/tmp/test_house.fbx"))
            self.assertEqual(guard.measure(guard.decode(log), guard.CHECKS[0][1], None)[0], 1)

    def test_smoothing_warning_source_context_retains_failure_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "CI-ProductionAssetImport.log"
            log.write_text("Importing Props/TestProp.fbx\\nNo smoothing group information was found\\n", encoding="utf-8")
            evidence = guard.smoothing_warning_sources([log])
            self.assertEqual(len(evidence), 1)
            self.assertIn("TestProp.fbx", evidence[0][2])
            self.assertEqual(evidence[0][1], 2)

    def test_occurrence_gate_still_counts_each_unidentified_warning(self):
        pattern = re.compile(r"No smoothing group information", re.I)
        count, identities = guard.measure(
            "No smoothing group information\nNo smoothing group information",
            pattern,
            None,
        )
        self.assertEqual(count, 2)
        self.assertEqual(identities, [])


if __name__ == "__main__":
    unittest.main()
