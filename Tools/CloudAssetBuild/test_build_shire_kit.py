import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import build_shire_kit as kit


class ShireKitManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        source = self.root / "source.obj"
        source.write_text("licensed source placeholder", encoding="utf-8")
        self.row = {
            "id": "Bench",
            "source": {"path": "source.obj"},
            "license": {"status": "VERIFIED", "evidence_url": "https://example.test/license"},
            "target_tris": 630,
            "lods": [1.0, 0.5, 0.25],
            "collision": "convex_hull",
            "material_groups": ["wood"],
        }

    def tearDown(self):
        self.tmp.cleanup()

    def test_licensed_physical_source_passes_preflight(self):
        good, rejected = kit.preflight({"assets": [self.row]}, self.root)
        self.assertEqual([x["id"] for x in good], ["Bench"])
        self.assertEqual(rejected, [])

    def test_missing_source_is_quarantined_without_stopping_other_rows(self):
        missing = dict(self.row, id="Missing", source={"path": "absent.fbx"})
        good, rejected = kit.preflight({"assets": [missing, self.row]}, self.root)
        self.assertEqual([x["id"] for x in good], ["Bench"])
        self.assertEqual(rejected[0]["errors"], ["SOURCE_FILE_MISSING"])

    def test_unverified_license_is_quarantined(self):
        row = dict(self.row, license={"status": "PENDING"})
        _, rejected = kit.preflight({"assets": [row]}, self.root)
        self.assertIn("LICENSE_NOT_VERIFIED", rejected[0]["errors"])

    def test_duplicate_ids_and_path_traversal_are_rejected(self):
        escape = dict(self.row, source={"path": "../outside.obj"})
        _, rejected = kit.preflight({"assets": [self.row, escape]}, self.root)
        self.assertIn("DUPLICATE_ID", rejected[0]["errors"])
        self.assertIn("SOURCE_PATH_ESCAPES_ROOT", rejected[0]["errors"])

    def test_preflight_cli_writes_receipt_and_row_quarantine_without_blender(self):
        manifest = self.root / "manifest.json"
        out = self.root / "out"
        manifest.write_text(json.dumps({"assets": [dict(self.row, source={"path": "missing.fbx"})]}), encoding="utf-8")
        script = Path(kit.__file__).resolve()
        result = subprocess.run([sys.executable, str(script), "--manifest", str(manifest), "--root",
            str(self.root), "--out", str(out), "--preflight-only"], capture_output=True, text=True, check=True)
        self.assertIn("SHIRE_KIT_PREFLIGHT loaded=1 placed=0 rejected=1", result.stdout)
        receipt = json.loads((out / "shire_kit_receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(receipt["quarantine"][0]["errors"], ["SOURCE_FILE_MISSING"])
        self.assertTrue((out / "quarantine" / "Bench.json").is_file())


if __name__ == "__main__":
    unittest.main()
