import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
import drive_warehouse_sync as d

class DriveWarehouseTests(unittest.TestCase):
    def test_remote_must_be_scoped(self):
        with tempfile.TemporaryDirectory() as temp:
            c=Path(temp)/"rclone.conf"
            c.write_text("[shirecloud]\ntype = drive\nroot_folder_id = wrong\n")
            with self.assertRaisesRegex(RuntimeError,"NOT_SCOPED"):
                d.require_remote(c,"shirecloud")
    def test_only_approved_direct_zip(self):
        entry={"Path":"02_Shire_P1C01/nature.zip","ID":"1Abcdefghi12345","Size":100,"Hashes":{"MD5":"a"*32}}
        with patch.object(d,"run_rclone",return_value=json.dumps([entry,{**entry,"Path":"private/secret.zip"},{**entry,"Path":"02_Shire_P1C01/inner/other.zip"}])):
            items = d.inventory("rclone",Path("dummy"),"shirecloud")
        self.assertEqual(len(items), 1)
        for key, value in entry.items():
            self.assertEqual(items[0][key], value)
    def test_zip_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"bad.zip"
            with zipfile.ZipFile(p,"w") as z: z.writestr("../escape.fbx","unsafe")
            with self.assertRaisesRegex(RuntimeError,"UNSAFE_PATH"): d.archive_qc(p)
    def test_cleanup_requires_real_backup(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/"warehouse"
            root.mkdir()
            with patch.object(d,"run_rclone",side_effect=AssertionError("unallowed")):
                d.cleanup("rclone",Path("x"),"shirecloud",root,Path(temp)/"missing")
    def test_exactly_one_scheduled_writer_and_no_unattended_deletion(self):
        root = Path(__file__).resolve().parents[1]
        workflows = root / ".github" / "workflows"
        self.assertFalse((workflows / "private-drive-warehouse-intake.yml").exists())
        source = (workflows / "drive-warehouse-auto-intake.yml").read_text(encoding="utf-8")
        self.assertIn("verify_runner_session.ps1", source)
        self.assertNotIn("--mode cleanup", source)
        script = (root / "Scripts" / "drive_warehouse_sync.py").read_text(encoding="utf-8")
        self.assertIn('"license_status": "UNVERIFIED_NOT_IMPORTABLE"', script)

    def test_runner_uses_refreshed_user_path_not_stale_watchdog_environment(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github" / "workflows" / "drive-warehouse-auto-intake.yml").read_text(encoding="utf-8")
        self.assertIn("[Environment]::GetEnvironmentVariable('Path', 'User')", workflow)
        self.assertIn("[Environment]::GetEnvironmentVariable('Path', 'Machine')", workflow)
        self.assertIn("RCLONE_MISSING_AFTER_PATH_REFRESH", workflow)
        self.assertIn("PYTHON_MISSING_AFTER_PATH_REFRESH", workflow)
        self.assertIn("--rclone-bin $rclone.Source", workflow)
        self.assertIn("$safeSha = $env:GITHUB_SHA", workflow)
        self.assertIn("Join-Path $originalStageRoot $safeSha", workflow)
        self.assertIn("P1C01_CURATED_ORIGINAL_STAGE_RECEIPT_MISSING", workflow)
        self.assertIn("latest_stage.json", workflow)
        self.assertNotIn("winget install", workflow)
        self.assertNotIn("--mode cleanup", workflow)

    def test_bad_md5_is_quarantined_without_stopping_other_eligible_archives(self):
        entry={"Path":"02_Shire_P1C01/nature.zip","ID":"1Abcdefghi12345","Size":100,"Hashes":{}}
        valid={**entry,"Path":"02_Shire_P1C01/valid.zip","Hashes":{"MD5":"a"*32}}
        with patch.object(d,"expected_sources",return_value={}):
          with patch.object(d,"run_rclone",return_value=json.dumps([entry,valid])):
            items=d.inventory("rclone",Path("x"),"shirecloud")
        self.assertEqual(len(items),1)
        for key, value in valid.items():
            self.assertEqual(items[0][key], value)
        with patch.object(d,"expected_sources",return_value={}):
          with patch.object(d,"run_rclone",return_value=json.dumps([entry])):
            self.assertEqual(d.inventory("rclone",Path("x"),"shirecloud"),[])
    def test_missing_drive_md5_is_allowed_for_sha_bound_snapshot_archive(self):
        entry={"Path":"02_Shire_P1C01/SHIRE_NATURE_UE427_BINARY_FBX_PNG_SOURCE_INTAKE_20261011.zip",
               "ID":"1Abcdefghi12345","Size":551245,"Hashes":{}}
        expected={"SHIRE_NATURE_UE427_BINARY_FBX_PNG_SOURCE_INTAKE_20261011.zip":{
            "byte_size":551245,
            "sha256":"940bd5679ff27e97fbf9ae214fd62cb57c0d760ca99a3a37e6353e3afa423fc6"}}
        with patch.object(d,"expected_sources",return_value=expected):
          with patch.object(d,"run_rclone",return_value=json.dumps([entry])):
            items=d.inventory("rclone",Path("x"),"shirecloud")
        self.assertEqual(len(items),1)
        self.assertFalse(items[0]["_md5_available"])
        self.assertEqual(items[0]["_expected_sha256"], expected[Path(entry["Path"]).name]["sha256"])
if __name__=="__main__": unittest.main()
