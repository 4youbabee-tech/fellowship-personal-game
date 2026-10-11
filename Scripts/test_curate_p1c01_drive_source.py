#!/usr/bin/env python3
"""Offline regression for source-only curation and archive allowlists."""
import hashlib
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import curate_p1c01_drive_source as c

class CuratedShireSourceTests(unittest.TestCase):
    def test_exact_ten_owner_source_checksums_are_pinned(self):
        self.assertEqual(len(c.EXPECTED),10)
        self.assertEqual(len(set(c.EXPECTED)),10)
        self.assertTrue(all(len(s)==64 and all(k in '0123456789abcdef' for k in s) for s in c.EXPECTED.values()))

    def test_unsafe_members_are_rejected(self):
        for name in ('../escape.fbx','C:/escape.fbx','/absolute/file.png','safe/../escape.fbx'):
            with self.subTest(path=name), self.assertRaises(ValueError):
                c.valid_path(name)
        self.assertTrue(c.valid_path('Nature/Meshes/SM_Sh_tree_oak_LOD0.fbx'))

    def test_png_header_contract(self):
        raw=b'\x89PNG\r\n\x1a\n'+b'\x00\x00\x00\x0dIHDR'+(1024).to_bytes(4,'big')+(512).to_bytes(4,'big')
        self.assertEqual(c.png_size(raw),[1024,512])
        with self.assertRaises(ValueError): c.png_size(b'not a png')

    def test_empty_archive_directory_never_claims_production(self):
        with TemporaryDirectory() as t:
            root=Path(t)
            out=root/'SafeStage'
            p=subprocess.run([sys.executable,str(Path(c.__file__)), '--archive-dir',str(root),'--output-dir',str(out)],capture_output=True,text=True)
            self.assertNotEqual(p.returncode,0)
            self.assertIn('MISSING_OWNER_ZIP',p.stderr)
            self.assertFalse(list(out.glob('*.zip')))

    def test_unreal_content_path_is_blocked(self):
        with TemporaryDirectory() as t:
            root=Path(t)
            p=subprocess.run([sys.executable,str(Path(c.__file__)),'--archive-dir',str(root),'--output-dir',str(root/'Content'/'Production')],capture_output=True,text=True)
            self.assertNotEqual(p.returncode,0)
            self.assertIn('SOURCE_CURATION_MUST_NOT_WRITE_TO_UNREAL_CONTENT',p.stderr)

    def test_no_unattended_import_or_cleanup_in_source_curator(self):
        content=Path(c.__file__).read_text(encoding='utf-8')
        self.assertNotIn('deletefile',content)
        self.assertNotIn('UE4Editor-Cmd.exe',content)
        self.assertIn("'engine_imported':False",content)
        self.assertIn("'gate6_7_closed':False",content)
        self.assertIn("'lod_assigned_in_ue4':False",content)

if __name__=='__main__': unittest.main()