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
            "dimensions_m": [1.2, 0.55, 0.85],
            "collision": "convex_hull",
            "material_groups": ["wood"],
        }

    def tearDown(self):
        self.tmp.cleanup()

    def test_licensed_physical_source_passes_preflight(self):
        good, rejected = kit.preflight({"assets": [self.row]}, self.root)
        self.assertEqual([x["id"] for x in good], ["Bench"])
        self.assertEqual(rejected, [])

    def test_source_sha256_is_checked_when_manifest_pins_a_digest(self):
        digest = kit.sha256(self.root / "source.obj")
        row = dict(self.row, source={"path": "source.obj", "source_sha256": digest})
        good, rejected = kit.preflight({"assets": [row]}, self.root)
        self.assertEqual([x["id"] for x in good], ["Bench"])
        self.assertEqual(rejected, [])
        row = dict(row, id="WrongHash", source={"path": "source.obj", "source_sha256": "0" * 64})
        good, rejected = kit.preflight({"assets": [row, self.row]}, self.root)
        self.assertEqual([x["id"] for x in good], ["Bench"])
        self.assertIn("SOURCE_SHA256_MISMATCH", rejected[0]["errors"])

    def test_provider_receipt_hash_is_bound_to_physical_source(self):
        source_root = self.root / "SourceAssets" / "ExternalLicensed" / "Inbox" / "painted_wooden_bench"
        source_root.mkdir(parents=True)
        source = source_root / "painted_wooden_bench.fbx"
        source.write_bytes(b"licensed FBX bytes")
        digest = kit.sha256(source)
        receipt = source_root / "source_receipt.json"
        receipt.write_text(json.dumps({
            "status": "CC0_POLYHAVEN_FBX_SOURCE_ACQUIRED",
            "license": "CC0", "asset_id": "painted_wooden_bench",
            "files": [{"path": source.name, "sha256": digest}],
        }), encoding="utf-8")
        row = dict(self.row, source={
            "path": source.relative_to(self.root).as_posix(),
            "asset_id": "painted_wooden_bench",
            "receipt_path": receipt.relative_to(self.root).as_posix(),
        })
        good, rejected = kit.preflight({"assets": [row]}, self.root)
        self.assertEqual([x["id"] for x in good], ["Bench"])
        self.assertEqual(rejected, [])
        receipt.write_text("{}", encoding="utf-8")
        _, rejected = kit.preflight({"assets": [row]}, self.root)
        self.assertIn("SOURCE_RECEIPT_PROVENANCE_MISMATCH", rejected[0]["errors"])

    def test_malformed_and_unsafe_rows_are_quarantined_without_stopping_batch(self):
        malformed = dict(self.row, id="../../outside", source=None)
        good, rejected = kit.preflight({"assets": [None, malformed, self.row]}, self.root)
        self.assertEqual([x["id"] for x in good], ["Bench"])
        self.assertEqual(rejected[0]["errors"], ["ROW_NOT_OBJECT"])
        self.assertIn("INVALID_ID", rejected[1]["errors"])
        self.assertIn("SOURCE_PATH_MISSING", rejected[1]["errors"])

    def test_dimension_validation_fails_before_blender(self):
        bad_dimensions = dict(self.row, id="BadDimensions", dimensions_m=[1.2, "wide", 0.85])
        good, rejected = kit.preflight({"assets": [bad_dimensions, self.row]}, self.root)
        self.assertEqual([x["id"] for x in good], ["Bench"])
        self.assertIn("INVALID_DIMENSIONS_M", rejected[0]["errors"])

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
        self.assertTrue((out / "quarantine" / "Bench__row_0001.json").is_file())

    def test_quarantine_paths_are_unique_and_cannot_escape_output(self):
        manifest = self.root / "manifest.json"
        out = self.root / "out"
        bad = dict(self.row, id="../../escape", source={"path": "missing.fbx"})
        manifest.write_text(json.dumps({"assets": [bad, bad]}), encoding="utf-8")
        script = Path(kit.__file__).resolve()
        subprocess.run([sys.executable, str(script), "--manifest", str(manifest), "--root",
            str(self.root), "--out", str(out), "--preflight-only"], capture_output=True, text=True, check=True)
        files = sorted((out / "quarantine").glob("*.json"))
        self.assertEqual([path.name for path in files], [
            "escape__row_0001.json", "escape__row_0002.json"])
        self.assertFalse((self.root / "escape.json").exists())


if __name__ == "__main__":
    unittest.main()
