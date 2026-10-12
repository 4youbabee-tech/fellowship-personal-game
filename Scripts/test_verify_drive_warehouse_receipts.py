#!/usr/bin/env python3
"""Network-free physical warehouse source attestation and quarantine regressions."""
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zipfile

import validate_drive_source_bundles as source_qc
import verify_drive_warehouse_receipts as audit

A = "SHIRE_NATURE_UE427_BINARY_FBX_PNG_SOURCE_INTAKE_20261011.zip"
B = "GH11706518373_Shire_Nature_Binary_36_FBX.zip"
FBX = source_qc.FBX_MAGIC + struct.pack("<I", 7400) + b"mesh-payload"


class PhysicalWarehouseAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "warehouse"
        self.receipts = self.root / "_drive_temp_staging" / "receipts"
        self.receipts.mkdir(parents=True)
        self.expected = []

    def add(self, name, members=None):
        members = members or {"Mesh/tree_LOD0.fbx": FBX}
        folder = self.root / "_drive_temp_staging" / "files" / audit.CATEGORIES[name]
        folder.mkdir(parents=True, exist_ok=True)
        provisional = folder / "raw.zip"
        with zipfile.ZipFile(provisional, "w", zipfile.ZIP_DEFLATED) as z:
            for p, payload in members.items():
                z.writestr(p, payload)
        sha, md5 = audit.digests(provisional)
        ident = ("fakeid" + str(len(self.expected) + 100))
        path = folder / (ident + "-" + sha[:16] + "-" + name)
        provisional.rename(path)
        with zipfile.ZipFile(path) as z:
            qc = source_qc.scan_archive(z)
            entries = len(z.infolist())
        receipt = {"remote_id": ident, "remote_path": audit.CATEGORIES[name] + "/" + name,
                   "remote_size": path.stat().st_size, "remote_md5": md5,
                   "sha256": sha, "local_path": str(path), "zip_entries": entries,
                   "state": "LOCAL_STAGED_NOT_IMPORTED", "license_status": "UNVERIFIED_NOT_IMPORTABLE"}
        receipt_file = self.receipts / (ident + "-" + sha + ".json")
        receipt_file.write_text(json.dumps(receipt), encoding="utf-8")
        self.expected.append({"file": name, "byte_size": path.stat().st_size,
                              "sha256": sha, "types": qc["types"], "fbx_formats": qc["fbx_formats"]})
        return path, receipt_file

    def snapshot(self):
        path = self.root / "snapshot.json"
        path.write_text(json.dumps({"archives": self.expected}), encoding="utf-8")
        return path

    def assess(self):
        return audit.assess(self.root, self.snapshot(), required_count=len(self.expected))

    def test_canonical_ten_file_source_snapshot_matches_allowlist(self):
        expected = audit.load_expected(audit.SNAPSHOT)
        self.assertEqual(len(expected), 10)
        self.assertEqual(set(expected), set(audit.CATEGORIES))

    def test_actual_bytes_md5_sha256_and_cross_pack_duplicates(self):
        self.add(A)
        self.add(B)
        result = self.assess()
        self.assertEqual(result["state"], "SOURCE_QC_PASS_IMPORT_BLOCKED")
        self.assertEqual(result["verified_archive_count"], 2)
        self.assertEqual(len(result["duplicate_groups"]), 1)
        self.assertTrue(result["duplicate_groups"][0]["retain_source_candidate"].startswith(A))
        self.assertFalse(result["unreal_imported"])
        self.assertFalse(result["automated_license_approval"])
        self.assertFalse(result["gate_6_7_closed"])

    def test_tampered_physical_file_fails_even_with_receipt(self):
        file, _ = self.add(A)
        self.add(B)
        with file.open("ab") as f:
            f.write(b"tamper")
        result = self.assess()
        self.assertEqual(result["state"], "SOURCE_QC_FAILED")
        self.assertTrue(any("SIZE_MISMATCH" in row["reason"] for row in result["errors"]))

    def test_local_md5_with_pinned_sha_is_explicitly_distinguished(self):
        _, path = self.add(A)
        record = json.loads(path.read_text())
        record["remote_md5_source"] = "LOCAL_CALCULATED_PINNED_SHA256"
        path.write_text(json.dumps(record))
        result = self.assess()
        self.assertEqual(result["state"], "SOURCE_QC_PASS_IMPORT_BLOCKED")
        self.assertEqual(result["archive_rows"][0]["md5_provenance"],
                         "LOCAL_CALCULATED_PINNED_SHA256")

    def test_remote_md5_disagreement_fails(self):
        _, path = self.add(A)
        record = json.loads(path.read_text())
        record["remote_md5"] = "0" * 32
        path.write_text(json.dumps(record))
        result = self.assess()
        self.assertIn("REMOTE_MD5_MISMATCH", result["errors"][0]["reason"])

    def test_path_escape_or_receipt_path_spoof_fails(self):
        _, receipt_path = self.add(A)
        record = json.loads(receipt_path.read_text())
        record["local_path"] = str(self.root / "elsewhere" / "false.zip")
        receipt_path.write_text(json.dumps(record))
        result = self.assess()
        self.assertIn("WAREHOUSE_PATH_OR_FILE_INVALID", result["errors"][0]["reason"])

    def test_absent_staged_archive_fails_closed(self):
        self.add(A)
        result = self.assess()
        self.assertEqual(result["verified_archive_count"], 1)
        self.assertFalse(result["errors"])
        self.expected.append({"file": B, "byte_size": 100, "sha256": "0" * 64,
                              "types": {}, "fbx_formats": {}})
        result = self.assess()
        self.assertEqual(result["verified_archive_count"], 1)
        self.assertEqual(result["state"], "SOURCE_QC_FAILED")

    def test_ascii_fbx_quarantined_not_promoted(self):
        self.add(A, {"source/mesh.fbx": b"; FBX 7.4.0 project source\n"})
        result = self.assess()
        self.assertEqual(result["state"], "SOURCE_QC_PASS_IMPORT_BLOCKED")
        self.assertEqual(len(result["quarantine"]), 1)
        self.assertEqual(result["quarantine"][0]["reason"], "ASCII_OR_UNSUPPORTED_FBX_SOURCE_ONLY")

    def test_unsafe_zip_member_never_passes_physical_scan(self):
        self.add(A, {"../bad.fbx": FBX})
        result = self.assess()
        self.assertEqual(result["state"], "SOURCE_QC_FAILED")
        self.assertIn("PHYSICAL_ARCHIVE_CONTENT_INVALID", result["errors"][0]["reason"])

    def test_automated_wave_never_claims_ue_or_license(self):
        self.add(A)
        result = self.assess()
        self.assertEqual(len(result["production_wave_queue"]), 5)
        self.assertTrue(all(not w["engine_promotion"] for w in result["production_wave_queue"]))
        self.assertTrue(all(w["unreal_import"] == "BLOCKED_LICENSE_AND_ENGINE_QC"
                            for w in result["production_wave_queue"]))


if __name__ == "__main__":
    unittest.main()
