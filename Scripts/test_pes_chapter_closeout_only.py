#!/usr/bin/env python3
"""Guard fast PES: broad runtime sweeps only on explicit chapter closeout."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / ".github/workflows/unreal-build-validation.yml"

class ChapterCloseoutOnlyTests(unittest.TestCase):
    def test_broad_runtime_sweeps_are_owner_closeout_only(self):
        text = WF.read_text(encoding="utf-8")
        names = (
            "Headless chapter-by-chapter runtime audit",
            "Headless route/story state roundtrip audit",
            "Summarize and guard runtime warning debt",
        )
        for name in names:
            pattern = rf"(?m)^\s*- name: {re.escape(name)}\n\s*if: ([^\n]+)"
            match = re.search(pattern, text)
            self.assertIsNotNone(match, name)
            clause = match.group(1)
            self.assertIn("github.event_name == 'workflow_dispatch'", clause)
            self.assertIn("inputs.package_windows == true", clause)
            self.assertIn("SHIRE_FULL_UNREAL_REQUIRED", clause)
        for name in ("Build ShireJourneyEditor", "Headless playable startup smoke"):
            self.assertRegex(text, rf"(?m)^\s*- name: {re.escape(name)}\n\s*if: ")
        self.assertIn("run_self_hosted:", text)
        self.assertIn("package_windows:", text)

if __name__ == "__main__":
    unittest.main()
