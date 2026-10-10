#!/usr/bin/env python3
"""Static regression: a playable Windows candidate boots Shire, not the UE template floor.

This checks source/config contracts only, never claims PIE, visual or device acceptance.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ENTRY = "/Engine/Maps/Entry"
TEMPLATE = "/Engine/Maps/Templates/Template_Default"


def source(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


class P1C01DeliveryEntryMapContract(unittest.TestCase):
    def test_engine_editor_and_game_default(self):
        cfg = source("Config/DefaultEngine.ini")
        for key in ("EditorStartupMap", "GameDefaultMap"):
            self.assertEqual(cfg.count(key + "=" + ENTRY), 1)
            self.assertNotIn(key + "=" + TEMPLATE, cfg)

    def test_cook_uses_entry(self):
        script = source("Scripts/ci_package_w00.ps1")
        self.assertEqual(script.count('"-map=' + ENTRY + '"'), 1)
        self.assertNotIn('"-map=' + TEMPLATE + '"', script)
        self.assertIn('W00_PACKAGE_PASS', script)

    def test_headless_runtime_uses_entry(self):
        smoke = source("Scripts/runtime_smoke.py")
        self.assertIn('"' + ENTRY + '"', smoke)
        self.assertNotIn('"' + TEMPLATE + '"', smoke)
        self.assertIn("RUNTIME_SWEEP_SUMMARY", smoke)

    def test_packaged_startup_observes_p1c01(self):
        ps = source("Scripts/verify_packaged_startup.ps1")
        self.assertIn('"' + ENTRY + '"', ps)
        self.assertIn("ShireStartupGrounding: PASS chapter=P1C01", ps)
        self.assertIn("W00_PACKAGED_STARTUP_PASS", ps)
        self.assertNotIn('"' + TEMPLATE + '"', ps)

    def test_download_requires_build_and_runtime_success(self):
        wf = source(".github/workflows/unreal-build-validation.yml")
        self.assertIn("name: Upload P1C01 Windows playable candidate", wf)
        self.assertIn("if: success() &&", wf)
        self.assertIn("path: Saved/W00Package/WindowsNoEditor/", wf)
        self.assertIn("if-no-files-found: error", wf)
        self.assertIn("actions/upload-artifact@v4", wf)
        self.assertNotIn("name: Upload P1C01 packaging evidence", wf)
        self.assertLess(wf.index("name: Launch and observe packaged executable"),
                        wf.index("name: Upload P1C01 Windows playable candidate"))

    def test_does_not_claim_final_visual_or_device(self):
        workflow = source(".github/workflows/unreal-build-validation.yml")
        self.assertIn("name: Upload P1C01 Windows playable candidate", workflow)
        cfg = source("Data/P1C01Gate67AcceptanceChecklistV1.json")
        self.assertIn("PREPARED_NOT_ACCEPTED", cfg)


if __name__ == "__main__":
    unittest.main(verbosity=2)
