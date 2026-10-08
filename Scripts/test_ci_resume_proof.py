"""Offline, engine-free checks for same-HEAD stage reuse safety."""

import json
import tempfile
import unittest
from pathlib import Path

from ci_resume_proof import FRODO_FILES, MODES, probe, record, verify

HEAD = "a" * 40
OTHER = "b" * 40


class ResumeProofTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.editor = self.make("UE4/UE4Editor-Cmd.exe", "engine")
        self.make("Binaries/Win64/UE4Editor-ShireJourney.dll", "compiled-binary")
        for rel in FRODO_FILES:
            self.make(rel, "asset:" + rel)
        self.make("Saved/Logs/CI-ProductionAssetImport.log", "ShireProductionImport: 0 failures")
        self.make("Saved/Logs/CI-FrodoPersistentRuntimeImport.log", "UE4_ANIMATION_IMPORT_TECHNICAL_PASS clips=3 bones=48")

    def make(self, rel, data):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, encoding="utf-8")
        return path

    def capture_and_runtime(self):
        for i in range(7):
            self.make(f"Saved/Automation/P1C01VisualCapture/{HEAD[:12]}/{i + 1:02}.png", "PNG:" + str(i))
            self.make(f"Saved/Automation/P1C01VisualCapture/{HEAD[:12]}/{i + 1:02}.log", "UE4 capture:" + str(i))
        self.make("Saved/Logs/CI-ProjectAutomation.log", "Automation Test Succeeded")
        for mode in MODES:
            count = 8 if mode == "chapters" else 1
            rows = [{"passed": True, "chapter": f"P1C{index + 1:02}"} for index in range(count)]
            self.make(f"Saved/Logs/CI-{mode}-result.json", json.dumps(rows))

    def package(self):
        self.make("Saved/W00Package/WindowsNoEditor/ShireJourney.exe", "exe")
        self.make("Saved/W00Package/WindowsNoEditor/ShireJourney/Content/Paks/ShireJourney-WindowsNoEditor.pak", "pak")
        self.make("Saved/Logs/CI-W00-PackagedData.json", json.dumps({"expected_count": 37, "verified_count": 37, "missing": [], "invalid_json": []}))

    def test_fail_closed_without_receipt_and_on_different_head(self):
        self.assertFalse(probe(self.root, HEAD, self.editor)["import"])
        record(self.root, HEAD, "import", self.editor)
        self.assertTrue(verify(self.root, HEAD, "import", self.editor)[0])
        self.assertFalse(verify(self.root, OTHER, "import", self.editor)[0])

    def test_sequential_resume_and_dependency_invalidation(self):
        record(self.root, HEAD, "import", self.editor)
        self.capture_and_runtime()
        record(self.root, HEAD, "core", self.editor)
        self.package()
        record(self.root, HEAD, "package", self.editor)
        self.assertEqual(probe(self.root, HEAD, self.editor), {"import": True, "core": True, "package": True})
        self.make(FRODO_FILES[0], "changed-asset")
        self.assertEqual(probe(self.root, HEAD, self.editor), {"import": False, "core": False, "package": False})

    def test_missing_photo_or_failed_runtime_denies_core(self):
        record(self.root, HEAD, "import", self.editor)
        self.capture_and_runtime()
        record(self.root, HEAD, "core", self.editor)
        (self.root / f"Saved/Automation/P1C01VisualCapture/{HEAD[:12]}/01.png").unlink()
        self.assertFalse(verify(self.root, HEAD, "core", self.editor)[0])
        self.make(f"Saved/Automation/P1C01VisualCapture/{HEAD[:12]}/01.png", "PNG:0")
        self.assertTrue(verify(self.root, HEAD, "core", self.editor)[0])
        self.make("Saved/Logs/CI-state-result.json", json.dumps([{"passed": False}]))
        self.assertFalse(verify(self.root, HEAD, "core", self.editor)[0])

    def test_missing_package_and_failed_data_denies_package(self):
        record(self.root, HEAD, "import", self.editor)
        self.capture_and_runtime()
        record(self.root, HEAD, "core", self.editor)
        self.package()
        record(self.root, HEAD, "package", self.editor)
        self.make("Saved/Logs/CI-W00-PackagedData.json", json.dumps({"expected_count": 37, "verified_count": 36, "missing": [], "invalid_json": []}))
        self.assertFalse(verify(self.root, HEAD, "package", self.editor)[0])

    def test_engine_change_invalidates_receipt(self):
        record(self.root, HEAD, "import", self.editor)
        self.make("UE4/UE4Editor-Cmd.exe", "new-engine-binary")
        self.assertFalse(verify(self.root, HEAD, "import", self.editor)[0])

    def test_cannot_record_core_or_package_without_predecessor(self):
        with self.assertRaisesRegex(ValueError, "predecessor"):
            record(self.root, HEAD, "core", self.editor)
        with self.assertRaisesRegex(ValueError, "predecessor"):
            record(self.root, HEAD, "package", self.editor)


if __name__ == "__main__":
    unittest.main()
