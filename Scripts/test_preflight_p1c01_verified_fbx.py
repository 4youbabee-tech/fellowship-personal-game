"""Offline cheap regression: PBR normalization refuses stale, broken or missing mesh derivatives."""
import hashlib,json,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import preflight_p1c01_verified_fbx as qc

BINARY=b"Kaydara FBX Binary"+b"X"*350
NORMAL=BINARY+b"LayerElementSmoothing"+b"Y"*300

class DerivedFBXTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.original=self.root/"SourceAssets/Production/World/Shire/VerifiedPBR/barrel_01/barrel_01.fbx"
        self.original.parent.mkdir(parents=True)
        self.original.write_bytes(BINARY)
    def test_normalizes_without_mutating_source_then_uses_hash_cache(self):
        original=qc.sha(self.original)
        def pretend(args,**kwargs):
            Path(args[args.index("--output")+1]).write_bytes(NORMAL)
            return subprocess.CompletedProcess(args,0,"P1C01_FBX_NORMALIZED asset=barrel_01", "")
        with patch.object(qc,"blender_exec",return_value="/fake/blender"),patch.object(qc.subprocess,"run",side_effect=pretend) as run:
            self.assertEqual(len(qc.execute(self.root)),1)
            self.assertEqual(qc.sha(self.original),original)
            qc.execute(self.root,verify_only=True)
            self.assertEqual(run.call_count,1)
    def test_missing_blender_fails_before_unreal(self):
        with patch.object(qc,"blender_exec",return_value=None):
            with self.assertRaisesRegex(qc.SourceQCError,"BLENDER_REQUIRED_BEFORE_UNREAL"):
                qc.execute(self.root)
    def test_unverified_derivative_fails_closed(self):
        with self.assertRaisesRegex(qc.SourceQCError,"DERIVED_FBX_NOT_READY"):
            qc.execute(self.root,verify_only=True)
    def test_stale_original_hash_fails(self):
        target=self.root/"Saved/P1C01NormalizedFBX/barrel_01/barrel_01.fbx"
        target.parent.mkdir(parents=True)
        target.write_bytes(NORMAL)
        (target.parent.parent/"receipt.json").write_text(json.dumps({"assets":[{
            "id":"barrel_01","source_sha256":qc.sha(self.original),
            "derived_sha256":qc.sha(target)}]}))
        self.original.write_bytes(BINARY+b"CHANGED")
        with self.assertRaisesRegex(qc.SourceQCError,"DERIVED_FBX_NOT_READY"):
            qc.execute(self.root,verify_only=True)
    def test_corrupt_derivative_fails(self):
        target=self.root/"Saved/P1C01NormalizedFBX/barrel_01/barrel_01.fbx"
        target.parent.mkdir(parents=True)
        target.write_bytes(BINARY)
        (target.parent.parent/"receipt.json").write_text(json.dumps({"assets":[{
            "id":"barrel_01","source_sha256":qc.sha(self.original),
            "derived_sha256":qc.sha(target)}]}))
        with self.assertRaisesRegex(qc.SourceQCError,"DERIVED_FBX_NOT_READY"):
            qc.execute(self.root,verify_only=True)
    def test_optional_missing_no_acceptance(self):
        self.original.unlink()
        self.assertEqual(qc.execute(self.root),[])
        with self.assertRaisesRegex(qc.SourceQCError,"VERIFIED_FBX_SOURCE_EMPTY"):
            qc.execute(self.root,required=True)

if __name__=="__main__":
    unittest.main()
