"""Offline regression fixtures for the P1C01 material receipt gate."""
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from verify_p1c01_material_receipt import PNG_SIGNATURE, ReceiptFailure, inspect_receipt


class MaterialReceiptGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.folder = self.root / "SourceAssets/Production/Imported/P1C01Materials/SH_TEST"
        self.folder.mkdir(parents=True)
        self.tex = self.folder / "TX_SH_TEST_BaseColor.png"
        self.mtl = self.folder / "MI_Sh_Test.mtl"
        self.png_bytes = PNG_SIGNATURE + b"fixture-content"
        self.tex.write_bytes(self.png_bytes)
        self.mtl_bytes = (
            b"# source\nnewmtl MI_Sh_Test\nKd 1.0 1.0 1.0\n"
            b"Pr 0.8000\nPm 0.0000\nKs 0.0200 0.0200 0.0200\n"
            b"map_Kd TX_SH_TEST_BaseColor.png\n\n"
        )
        self.mtl.write_bytes(self.mtl_bytes)
        self.receipt = {
            "schema_version": 2,
            "material_count": 1,
            "quarantined_count": 0,
            "items": [{
                "id": "SH_TEST", "material_name": "MI_Sh_Test",
                "license": "CC0", "provider": "POLY_HAVEN",
                "state": "SOURCE_READY_FOR_UE_IMPORT",
                "source_url": "https://dl.polyhaven.org/file/valid.png",
                "basecolor_sha256": hashlib.sha256(self.png_bytes).hexdigest(),
                # Producer receipt written before Git CRLF -> LF conversion.
                "mtl_sha256": hashlib.sha256(self.mtl_bytes.replace(b"\n", b"\r\n")).hexdigest(),
                "roughness": 0.8, "metallic": 0.0,
            }],
        }
        self.receipt_path = self.folder.parent / "P1C01MaterialSourceReceipt.json"
        self.write_receipt()

    def write_receipt(self):
        self.receipt_path.write_text(json.dumps(self.receipt), encoding="utf-8")

    def inspect(self, hydrated=True):
        return inspect_receipt(self.root, require_hydrated=hydrated, minimum_materials=1)

    def test_hydrated_png_and_git_normalized_mtl_pass(self):
        self.assertEqual(self.inspect(), {"materials": 1, "hydrated": 1, "pointers": 0, "mtl_eol_normalized": 1})

    def test_unhydrated_pointer_passes_source_only_but_fails_import(self):
        sha = self.receipt["items"][0]["basecolor_sha256"]
        self.tex.write_text(f"version https://git-lfs.github.com/spec/v1\noid sha256:{sha}\nsize {len(self.png_bytes)}\n", encoding="ascii")
        self.assertEqual(self.inspect(hydrated=False)["pointers"], 1)
        with self.assertRaisesRegex(ReceiptFailure, "lfs-pointer-not-hydrated"):
            self.inspect()

    def test_wrong_pointer_oid_rejected_even_for_source_only(self):
        self.tex.write_text("version https://git-lfs.github.com/spec/v1\noid sha256:" + "0" * 64 + "\nsize 24\n", encoding="ascii")
        with self.assertRaisesRegex(ReceiptFailure, "lfs-pointer-oid-mismatch"):
            self.inspect(hydrated=False)

    def test_corrupt_png_hash_rejected(self):
        self.tex.write_bytes(self.png_bytes + b"tamper")
        with self.assertRaisesRegex(ReceiptFailure, "png-hash-mismatch"):
            self.inspect()

    def test_corrupt_mtl_rejected(self):
        self.mtl.write_bytes(self.mtl_bytes.replace(b"0.8000", b"0.1000"))
        with self.assertRaisesRegex(ReceiptFailure, "mtl-hash-mismatch"):
            self.inspect()

    def test_duplicate_or_unapproved_source_rejected(self):
        self.receipt["items"].append(dict(self.receipt["items"][0]))
        self.receipt["material_count"] = 2
        self.write_receipt()
        with self.assertRaisesRegex(ReceiptFailure, "duplicate-family"):
            inspect_receipt(self.root, require_hydrated=True, minimum_materials=1)

    def test_unsafe_id_rejected_before_path_access(self):
        self.receipt["items"][0]["id"] = "../OTHER"
        self.write_receipt()
        with self.assertRaisesRegex(ReceiptFailure, "unsafe-material-id"):
            self.inspect()


if __name__ == "__main__":
    unittest.main()
