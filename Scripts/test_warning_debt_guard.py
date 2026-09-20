import re
import unittest

import warning_debt_guard as guard


class WarningDebtGuardTests(unittest.TestCase):
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

    def test_missing_package_deduplicates_across_chapter_logs(self):
        text = "\n".join([
            "Failed to load '/Game/Production/World/Moria/M_Missing.M_Missing'",
            "Failed to load '/Game/Production/World/Moria/M_Missing.M_Missing'",
        ])
        pattern = re.compile(r"Failed to load '(/Game/Production/World/[^']+)'", re.I)
        count, identities = guard.measure(text, pattern, 1)
        self.assertEqual(count, 1)
        self.assertEqual(identities, ["/Game/Production/World/Moria/M_Missing.M_Missing"])

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
