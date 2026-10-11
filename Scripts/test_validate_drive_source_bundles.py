#!/usr/bin/env python3
"""Cheap network-free regressions for physical source ZIP preflight."""
import io
import json
import struct
import tempfile
import unittest
import zipfile
from pathlib import Path
import validate_drive_source_bundles as v

class DriveSourcePreflightTests(unittest.TestCase):
    def scan_entries(self, entries):
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w", zipfile.ZIP_DEFLATED) as z:
            for name, value in entries.items():
                z.writestr(name, value)
        b.seek(0)
        with zipfile.ZipFile(b) as z:
            return v.scan_archive(z)

    def test_reject_zip_path_traversal(self):
        out = self.scan_entries({"../../overwrite.txt": "x"})
        self.assertTrue(any("UNSAFE_ARCHIVE_PATH" in x for x in out["failures"]))

    def test_reject_unknown_executable_payload(self):
        out = self.scan_entries({"tools/game.exe": b"MZ"})
        self.assertIn("UNEXPECTED_ARCHIVE_MEMBER:tools/game.exe", out["failures"])

    def test_reject_corrupted_binary_fbx(self):
        out = self.scan_entries({"Meshes/SM_Test_LOD0.fbx":v.FBX_MAGIC})
        self.assertTrue(any("UNSUPPORTED_FBX" in x for x in out["failures"]))

    def test_valid_binary_7400_header(self):
        out = self.scan_entries({"Meshes/SM_Test_LOD0.fbx":v.FBX_MAGIC+struct.pack("<I",7400)+b"xyz"})
        self.assertFalse(out["failures"])
        self.assertEqual(out["fbx_formats"], {"FBX_BINARY_7400": 1})

    def test_ascii_fbx_does_not_claim_binary(self):
        out = self.scan_entries({"source/mesh.fbx":b"; FBX 7.4.0 project source\n"})
        self.assertFalse(out["failures"])
        self.assertEqual(out["fbx_formats"], {"FBX_ASCII_SOURCE_ONLY":1})

    def test_missing_receipt_physical_output_blocks_promotion(self):
        receipt={"status":"CLOUD_SOURCE_STAGED","shard":1,"staged":1,"physical_png":3,
                 "materials":[{"slug":"mossy_stone","license":"CC0","source_page":"https://polyhaven.com/a/mossy_stone",
                               "outputs":[{"kind":x,"path":"materials/"+x+".png","sha256":"0"*64,"bytes":2}
                                          for x in ("BaseColor","NormalDX","ORM")]}],"quarantined":[]}
        out=self.scan_entries({"receipt.json":json.dumps(receipt)})
        self.assertTrue(any("RECEIPT_MISSING" in x for x in out["failures"]))

    def test_nested_archive_traversal_is_rejected(self):
        b=io.BytesIO()
        with zipfile.ZipFile(b,"w") as nested:
            nested.writestr("../unsafe.fbx","any")
        out=self.scan_entries({"pack.zip":b.getvalue()})
        self.assertIn("BAD_NESTED_ZIP:pack.zip",out["failures"])

    def test_full_file_scan_never_grants_runtime_acceptance(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"probe.zip"
            with zipfile.ZipFile(p,"w") as z:z.writestr("README.txt","sample")
            result=v.scan_files([p])
            self.assertEqual(result["summary"]["source_integrity_pass"],1)
            self.assertEqual(result["summary"]["unreal_imported"],0)
            self.assertEqual(result["archives"][0]["unreal_import_status"],"NOT_TESTED")

if __name__=="__main__": unittest.main()