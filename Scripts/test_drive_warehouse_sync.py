import io
import hashlib
import json
import shutil
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

    def test_pinned_missing_remote_md5_downloads_only_on_matching_sha256(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "warehouse"
            root.mkdir()
            source = Path(temp) / "known.zip"
            with zipfile.ZipFile(source, "w") as z:
                z.writestr("Mesh/valid.fbx", b"KayKit-or-owner-source")
            raw = source.read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            rel = "02_Shire_P1C01/known.zip"
            record = {"Path": rel, "ID": "1Abcdefghi12345",
                      "Size": len(raw), "Hashes": {}}
            pin = {rel: {"sha256": digest, "byte_size": len(raw)}}
            def fake_rclone(_binary, _config, *args):
                if args[0] == "lsjson":
                    return json.dumps([record])
                if args[0] == "copyto":
                    shutil.copyfile(source, args[-1])
                    return ""
                raise AssertionError("Unexpected operation")
            with patch.object(d, "pinned_archives", return_value=pin), (
                 patch.object(d, "run_rclone", side_effect=fake_rclone)):
                d.ingest("rclone", Path("rclone.conf"), "shirecloud", root, 10)
            receipts = list((root / "_drive_temp_staging" / "receipts").glob("*.json"))
            self.assertEqual(len(receipts), 1)
            saved = json.loads(receipts[0].read_text())
            self.assertEqual(saved["sha256"], digest)
            self.assertEqual(saved["remote_md5_source"], "LOCAL_CALCULATED_PINNED_SHA256")
            self.assertEqual(saved["license_status"], "UNVERIFIED_NOT_IMPORTABLE")
            self.assertTrue(Path(saved["local_path"]).is_file())

    def test_pinned_changed_bytes_do_not_enter_warehouse(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "warehouse"
            root.mkdir()
            rel = "02_Shire_P1C01/known.zip"
            valid = b"original"
            record = {"Path": rel, "ID": "1Abcdefghi12345",
                      "Size": len(valid), "Hashes": {}}
            pin = {rel: {"sha256": hashlib.sha256(valid).hexdigest(),
                         "byte_size": len(valid)}}
            def fake_rclone(_binary, _config, *args):
                if args[0] == "lsjson":
                    return json.dumps([record])
                if args[0] == "copyto":
                    Path(args[-1]).write_bytes(b"tampered")
                    return ""
                raise AssertionError("Unexpected operation")
            with patch.object(d, "pinned_archives", return_value=pin), (
                 patch.object(d, "run_rclone", side_effect=fake_rclone)):
                with self.assertRaisesRegex(RuntimeError, "DRIVE_PINNED_SHA256_MISMATCH"):
                    d.ingest("rclone", Path("rclone.conf"), "shirecloud", root, 10)
            self.assertFalse(list((root / "_drive_temp_staging" / "receipts").glob("*.json")))

    def test_bad_md5_is_quarantined_without_stopping_other_eligible_archives(self):
        entry={"Path":"02_Shire_P1C01/nature.zip","ID":"1Abcdefghi12345","Size":100,"Hashes":{}}
        valid={**entry,"Path":"02_Shire_P1C01/valid.zip","Hashes":{"MD5":"a"*32}}
        with patch.object(d,"run_rclone",return_value=json.dumps([entry,valid])):
            self.assertEqual(d.inventory("rclone",Path("x"),"shirecloud"),[valid])
        with patch.object(d,"run_rclone",return_value=json.dumps([entry])):
            self.assertEqual(d.inventory("rclone",Path("x"),"shirecloud"),[])
if __name__=="__main__": unittest.main()
