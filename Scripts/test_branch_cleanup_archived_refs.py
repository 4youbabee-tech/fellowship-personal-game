#!/usr/bin/env python3
"""Regression guard: archived branch deletion needs SHA-pinned ancestry and active-PR protection."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent.parent


class BranchArchiveRetirementTests(unittest.TestCase):
    def test_immutable_full_archive_coverage(self):
        plan = json.loads((ROOT / "Data/BranchCleanupPlan.json").read_text(encoding="utf-8"))
        archive = plan["archived_retirement_2026_10_16"]
        self.assertEqual(archive["source_heads_count"], 43)
        self.assertEqual(len(archive["refs"]), 43)
        self.assertRegex(archive["archive_head_sha"], r"^[0-9a-f]{40}$")
        names = [e["branch"] for e in archive["refs"]]
        self.assertEqual(len(names), len(set(names)))
        self.assertFalse({"develop", "main", archive["archive_branch"]} & set(names))
        self.assertTrue(all(re.fullmatch(r"[0-9a-f]{40}", e["expected_head_sha"]) for e in archive["refs"]))
        self.assertEqual([e["branch"] for e in plan["preserve_pending_salvage"]], [archive["archive_branch"]])

    def test_deletion_is_fail_closed_for_moved_unarchived_or_active_heads(self):
        script = (ROOT / "Scripts/run_branch_cleanup.ps1").read_text(encoding="utf-8")
        for marker in ("BRANCH_CLEANUP_ARCHIVE_HEAD_MOVED", "BRANCH_CLEANUP_ARCHIVED_SOURCE_NOT_PROVEN",
                       "BRANCH_CLEANUP_ARCHIVE_PROOF_PASS", "BRANCH_CLEANUP_ARCHIVED_HEAD_MOVED",
                       "$archiveParentShas.Contains($sha)", "$archiveParentShas.Contains($expectedArchivedSha)",
                       "BRANCH_CLEANUP_KEEP_ACTIVE_PR", "--force-with-lease=",
                       "owner-approved-archive-parent-proven"):
            self.assertIn(marker, script)
        self.assertLess(script.index("BRANCH_CLEANUP_ARCHIVE_PROOF_PASS"), script.index("function Remove-RemoteBranch"))
        self.assertLess(script.index("$activeHeads -contains $Branch"), script.index("BRANCH_CLEANUP_ARCHIVED_PROOF_PASS"))

    def test_existing_branch_cleanup_workflow_remains_hosted_and_serial(self):
        source = (ROOT / ".github/workflows/branch-cleanup.yml").read_text(encoding="utf-8")
        self.assertIn("runs-on: windows-latest", source)
        self.assertIn("contents: write", source)
        self.assertIn("branch-cleanup-", source)
        self.assertIn("Scripts\\run_branch_cleanup.ps1", source)


if __name__ == "__main__":
    unittest.main()
