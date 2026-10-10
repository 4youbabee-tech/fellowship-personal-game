"""Small no-network canonical warehouse integration and long-run regression."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stage_p1c01_adaptive_pbr_warehouse as impl


def dig(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def png_1024() -> bytes:
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
    ihdr = struct.pack(">IIBBBBB", 1024, 1024, 8, 2, 0, 0, 0)
    data = (b"\x00" + b"\x0f\x40\x80" * 1024) * 1024
    return impl.PNG_MAGIC + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(data)) + chunk(b"IEND", b"")


def put(root, rel, data):
    file = root / rel
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_bytes(data)
    return file


class PersistentIntakeTests(unittest.TestCase):
    def fake_inputs(self, base):
        source, pbr = base / "source", base / "pbr"
        slug = "weathered_gate_01"
        fbx = b"Kaydara FBX Binary  " + b"\x00\x1a\x00" + b"test-static-model"
        color = png_1024()
        original_files = []
        for rel, data in ((slug + ".fbx", fbx), ("textures/gate_diff_1k.png", color)):
            put(source, "assets/" + slug + "/" + rel, data)
            original_files.append({"relative_file": rel, "bytes": len(data), "sha256": dig(data),
                                   "md5": hashlib.md5(data).hexdigest()})
        source_receipt = {
            "license": "CC0",
            "mode": "HOSTED_SOURCE_ONLY_NO_UNREAL_NO_PERSISTENT_WAREHOUSE_MUTATION",
            "source_assets_staged": 1,
            "accepted": [{"id": slug, "license": "CC0",
                          "provider_page": "https://polyhaven.com/a/" + slug,
                          "files": original_files}],
        }
        receipt_bytes = (json.dumps(source_receipt, indent=2) + "\n").encode()
        put(source, "p1c01_adaptive_polyhaven_receipt.json", receipt_bytes)
        put(pbr, "assets/" + slug + "/" + slug + ".fbx", fbx)
        mat = "assets/" + slug + "/TX_gate_BaseColor.png"
        put(pbr, mat, color)
        pbr_receipt = {
            "input_assets": 1, "prepared_assets": 1, "quarantined": [],
            "source_receipt_sha256": dig(receipt_bytes),
            "assets": [{
                "id": slug, "status": "STATIC_SOURCE_QC_ONLY",
                "fbx_path": "assets/" + slug + "/" + slug + ".fbx",
                "fbx_sha256": dig(fbx), "fbx_bytes": len(fbx),
                "maps": [{"path": mat, "bytes": len(color), "sha256": dig(color),
                          "resolution": [1024, 1024], "role": "BaseColor"}],
                "held_material_variants": []
            }],
        }
        put(pbr, "p1c01_adaptive_pbr_receipt.json",
            (json.dumps(pbr_receipt, indent=2) + "\n").encode())
        return source, pbr

    def test_staged_wave_persists_and_is_reusable(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source, pbr = self.fake_inputs(base)
            warehouse = base / "warehouse"
            self.assertFalse(impl.check_staged_wave(warehouse, "p1c01_wave39", 1, 1))
            receipt = impl.stage(source, pbr, warehouse, "p1c01_wave39", 1, 1, reserve_bytes=0)
            self.assertEqual(receipt["original_source_count"], 1)
            self.assertEqual(receipt["converted_fbx_count"], 1)
            self.assertGreaterEqual(len(receipt["files"]), 3)
            self.assertTrue(impl.check_staged_wave(warehouse, "p1c01_wave39", 1, 1))
            repeated = impl.stage(source, pbr, warehouse, "p1c01_wave39", 1, 1, reserve_bytes=0)
            self.assertEqual(repeated["source_receipt_sha256"], receipt["source_receipt_sha256"])
            self.assertEqual(repeated["pbr_receipt_sha256"], receipt["pbr_receipt_sha256"])

    def test_tampered_source_fails_before_any_persistent_write(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source, pbr = self.fake_inputs(base)
            put(source, "assets/weathered_gate_01/weathered_gate_01.fbx", b"modified")
            with self.assertRaisesRegex(impl.StageError, "SOURCE_SIZE_OR_SHA256_MISMATCH"):
                impl.stage(source, pbr, base/"warehouse", "p1c01_wave39", 1, 1, reserve_bytes=0)

    def test_tampered_saved_payload_blocks_reuse(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source, pbr = self.fake_inputs(base)
            warehouse = base/"warehouse"
            rec = impl.stage(source, pbr, warehouse, "p1c01_wave39", 1, 1, reserve_bytes=0)
            Path(rec["files"][0]["file"]).write_bytes(b"altered")
            with self.assertRaisesRegex(impl.StageError, "SOURCE_SIZE_OR_SHA256_MISMATCH"):
                impl.check_staged_wave(warehouse, "p1c01_wave39", 1, 1)

    def test_tampered_pbr_receipt_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source, pbr = self.fake_inputs(base)
            report = pbr/"p1c01_adaptive_pbr_receipt.json"
            data = json.loads(report.read_text())
            data["source_receipt_sha256"] = "a"*64
            report.write_text(json.dumps(data))
            with self.assertRaisesRegex(impl.StageError, "PBR_SOURCE_RECEIPT_SHA256_MISMATCH"):
                impl.validate_inputs(source, pbr, 1, 1)


    def test_nested_original_relative_path_remains_posix_on_windows(self):
        """Nested provider textures must retain '/' for portable persistent receipts."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source, pbr = self.fake_inputs(root)
            plan = impl.validate_inputs(source, pbr, 1, 1)
            rows = plan["originals"]["weathered_gate_01"]
            self.assertTrue(any(row["rel"] == "textures/gate_diff_1k.png" for row in rows))
            self.assertTrue(all("\\\\" not in row["rel"] for row in rows))
            receipt = impl.stage(source, pbr, root / "warehouse", "p1c01_wave39", 1, 1, reserve_bytes=0)
            self.assertTrue(any("textures/gate_diff_1k.png" in row["file"].replace(chr(92), "/") for row in receipt["files"]))

    def test_no_symlink_or_traversal_receipts(self):
        for value in ("../bad.fbx", "/absolute.fbx", "C:/evil.fbx", "..\\bad.fbx"):
            with self.assertRaisesRegex(impl.StageError, "UNSAFE_RELATIVE_PATH"):
                impl.safe_path(value)


if __name__ == "__main__":
    unittest.main()
