#!/usr/bin/env python3
"""Network-free Drive intake safety regressions."""
import ast
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"Scripts/sync_drive_warehouse.py"
WORKFLOW=ROOT/".github/workflows/private-drive-warehouse-intake.yml"

class DriveIntakeContracts(unittest.TestCase):
    def test_python_compiles(self):
        ast.parse(SCRIPT.read_text(encoding="utf-8"))
    def test_private_exact_folder_scope(self):
        text=SCRIPT.read_text(encoding="utf-8")
        for name in ("01_Characters_Animations", "02_Shire_P1C01", "03_WholeGame_28Regions", "04_PBR_Materials"):
            self.assertIn(name,text)
        self.assertIn("REMOTE_MD5_REQUIRED_FAIL_CLOSED",text)
        self.assertIn("ZIP_CRC_FAILED",text)
        self.assertIn("WAREHOUSE_DISK_RESERVE_LOW",text)
        self.assertIn("sha256",text)
        self.assertNotIn('"delete"',text)
        self.assertNotIn('"purge"',text)
    def test_job_is_independent_and_no_remote_delete(self):
        workflow=WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("cron: '17 * * * *'",workflow)
        self.assertIn("runs-on: [self-hosted, Windows, X64, ue4-27]",workflow)
        self.assertIn("secrets.SHIRE_DRIVE_RCLONE_CONFIG_B64",workflow)
        self.assertIn("persist-credentials: false",workflow)
        self.assertNotIn("rclone delete",workflow)
        self.assertNotIn("rclone purge",workflow)
        self.assertNotIn("run_self_hosted",workflow)
    def test_reject_unsafe_names(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location("sync_drive_warehouse",SCRIPT)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for item in ("../escape.zip","a\\escape.zip","x:y.zip",""):
            with self.assertRaises(ValueError):
                module.safe_remote_name(item)
        self.assertEqual(module.safe_remote_name("ShireAssets.zip"),"ShireAssets.zip")
if __name__=="__main__": unittest.main()
