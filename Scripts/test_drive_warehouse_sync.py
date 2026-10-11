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
    def test_bad_md5_fails_closed(self):
        entry={"Path":"02_Shire_P1C01/nature.zip","ID":"1Abcdefghi12345","Size":100,"Hashes":{}}
        with patch.object(d,"run_rclone",return_value=json.dumps([entry])):
            with self.assertRaisesRegex(RuntimeError,"CHECKSUM"): d.inventory("rclone",Path("x"),"shirecloud")
if __name__=="__main__": unittest.main()
