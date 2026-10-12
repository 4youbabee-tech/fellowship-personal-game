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
            self.assertEqual(d.inventory("rclone",Path("dummy"),"shirecloud"),[entry])
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
        self.assertNotIn("winget install", workflow)
        self.assertNotIn("--mode cleanup", workflow)

    def test_bad_md5_is_quarantined_without_stopping_other_eligible_archives(self):
        entry={"Path":"02_Shire_P1C01/nature.zip","ID":"1Abcdefghi12345","Size":100,"Hashes":{}}
        valid={**entry,"Path":"02_Shire_P1C01/valid.zip","Hashes":{"MD5":"a"*32}}
        with patch.object(d,"run_rclone",return_value=json.dumps([entry,valid])):
            self.assertEqual(d.inventory("rclone",Path("x"),"shirecloud"),[valid])
        with patch.object(d,"run_rclone",return_value=json.dumps([entry])):
            self.assertEqual(d.inventory("rclone",Path("x"),"shirecloud"),[])
if __name__=="__main__": unittest.main()
