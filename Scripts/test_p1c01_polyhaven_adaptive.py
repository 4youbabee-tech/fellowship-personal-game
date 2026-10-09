"""No-network regression for Shire CC0 adaptive source staging."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stage_p1c01_polyhaven_adaptive as impl


def record(filename, data):
    return {'url': 'https://dl.polyhaven.org/example/' + filename,
            'size': len(data), 'md5': hashlib.md5(data).hexdigest()}


class AdaptiveSourceTests(unittest.TestCase):
    def test_reject_path_traversal_and_untrusted_host(self):
        with self.assertRaisesRegex(impl.IntakeError, "BAD_RELATIVE_NAME"):
            impl.safe_relative("../bad.png")
        with self.assertRaisesRegex(impl.IntakeError, "UNTRUSTED_SOURCE_HOST"):
            impl.source_file('x.fbx', {'url':'https://evil.invalid/a.fbx','size':3,'md5':'0'*32},30)

    def test_native_fbx_source_and_surface_dependency_required(self):
        with self.assertRaisesRegex(impl.IntakeError, "NATIVE_1K_FBX_UNAVAILABLE"):
            impl.plan_for_model('old_wood_gate', {}, single_limit=200)
        fbx = record('old_wood_gate.fbx', b'Kaydara FBX Binary')
        with self.assertRaisesRegex(impl.IntakeError, "NO_SOURCE_SURFACE_TEXTURE"):
            impl.plan_for_model('old_wood_gate', {'fbx':{'1k':{'fbx':fbx}}}, single_limit=200)

    def test_stage_all_fitting_qualified_candidates_instead_of_five(self):
        listing = {f'weathered_wooden_gate_{i}': {'type':2,'name':f'Weathered Wooden Gate {i}','tags':['wooden','garden']}
                   for i in range(8)}
        fbx=b'Kaydara FBX Binary  \x00\x1a\x00'
        tex=b'\x89PNG\r\n\x1a\n'
        data={'fbx':{'1k':{'fbx':{**record('f.fbx',fbx),'include':{'textures/diff_1k.png':record('t.png',tex)}}}}}
        def fake_download(spec, target, deadline):
            target.parent.mkdir(parents=True,exist_ok=True)
            data=fbx if target.suffix=='.fbx' else tex
            target.write_bytes(data)
            return {'relative_file':spec['name'],'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
        with tempfile.TemporaryDirectory() as temp:
            out=impl.stage(Path(temp),max_total_bytes=100000,single_limit=1024,seconds=60,
                           listing=listing,metadata_loader=lambda _:data,file_loader=fake_download)
            self.assertEqual(out['source_assets_staged'],8)
            self.assertEqual(out['source_assets_quarantined_or_deferred'],0)
            self.assertEqual(out['mode'],'HOSTED_SOURCE_ONLY_NO_UNREAL_NO_PERSISTENT_WAREHOUSE_MUTATION')

    def test_resume_hash_verified_and_no_reacquisition(self):
        original=b'Kaydara FBX Binary  \x00\x1a\x00'
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'prior'
            path=root/'assets'/'shrub_01'/'shrub_01.fbx'
            path.parent.mkdir(parents=True)
            path.write_bytes(original)
            receipt={'license':'CC0','source_assets_staged':1,
                     'accepted':[{'id':'shrub_01','files':[{
                         'relative_file':'shrub_01.fbx','bytes':len(original),
                         'sha256':hashlib.sha256(original).hexdigest(),
                         'md5':hashlib.md5(original).hexdigest()}]}]}
            (root/'p1c01_adaptive_polyhaven_receipt.json').write_text(json.dumps(receipt))
            old=impl.verify_previous_source(root)
            self.assertEqual(old,{'shrub_01'})
            listing={'shrub_01':{'type':2,'name':'Shrub garden'},
                     'shrub_02':{'type':2,'name':'Shrub garden'}}
            filedata={'fbx':{'1k':{'fbx':{**record('f.fbx',original),
                                        'include':{'textures/diff_1k.png':record('a.png',b'123')}}}}}
            def loader(spec,target,deadline):
                payload=original if target.suffix=='.fbx' else b'123'
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(payload)
                return {'relative_file':spec['name'],'bytes':len(payload),
                        'sha256':hashlib.sha256(payload).hexdigest()}
            got=impl.stage(Path(temp)/'next', max_total_bytes=10000,single_limit=1024,seconds=60,
                           listing=listing,metadata_loader=lambda _:filedata,
                           file_loader=loader,verified_previous_ids=old)
            self.assertEqual(got['source_assets_staged'],1)
            self.assertEqual(got['accepted'][0]['id'],'shrub_02')
            self.assertEqual(got['previous_staged_verified_and_excluded'],1)
            path.write_bytes(b'bad')
            with self.assertRaisesRegex(impl.IntakeError,'PREVIOUS_SOURCE_HASH_MISMATCH'):
                impl.verify_previous_source(root)
    def test_existing_five_not_redownloaded(self):
        self.assertEqual(impl.score_asset('painted_wooden_bench', {'type':2,'name':'Wooden Bench'}),0)
        self.assertGreater(impl.score_asset('old_wood_gate',{'type':2,'name':'Old Wood Gate'}),0)

    def test_oversize_and_non_textures_block(self):
        with self.assertRaisesRegex(impl.IntakeError,'SOURCE_FILE_OVER_SINGLE_LIMIT'):
            impl.source_file('x.fbx',{'url':'https://dl.polyhaven.org/a.fbx','size':500,'md5':'0'*32},10)


if __name__=='__main__':
    unittest.main()
