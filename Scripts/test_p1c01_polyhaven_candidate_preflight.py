"""Offline negative and positive regression for existing Poly Haven artifact QC."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_p1c01_polyhaven_candidate as impl


def digest(b):
    return hashlib.sha256(b).hexdigest()


class ExistingArtifactPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.bundle = self.root / 'bundle'
        self.bundle.mkdir()
        self.qc = self.root / 'qc.json'
        original = []
        converted = []
        for i, slug in enumerate(impl.ASSETS):
            folder = self.bundle / slug
            folder.mkdir()
            content = b'Kaydara FBX Binary  \x00\x1a\x00' + bytes([i]) * 5
            (folder / f'{slug}.fbx').write_bytes(content)
            materials = []
            for mname in (('Main', 'Glass') if slug == 'wooden_lantern_01' else ('Main',)):
                maps = []
                for role in sorted(impl.EXPECTED_ROLES[mname]):
                    filename = f'TX_{slug}_{mname}_{role}.png'
                    path = folder / filename
                    mode = 'L' if role == 'Opacity' else 'RGB'
                    color = 127 if mode == 'L' else ((255, 127, 0) if role == 'ORM' else (127, 127, 255))
                    Image.new(mode, (1024, 1024), color).save(path)
                    maps.append({'role': role, 'file': f'{slug}/{filename}', 'bytes': path.stat().st_size,
                                 'sha256': impl.sha256_file(path), 'resolution': [1024, 1024]})
                materials.append({'material': mname, 'maps': maps})
            original.append({'id': slug, 'fbx_sha256': digest(content), 'triangles': 22276 if slug == 'wicker_basket_01' else 630,
                             'uv_layers': 1, 'normal_layers': 1, 'png_count': sum(len(m['maps']) for m in materials)})
            converted.append({'asset_id': slug, 'fbx_path': f'{slug}/{slug}.fbx', 'fbx_sha256': digest(content),
                              'fbx_bytes': len(content), 'material_count': len(materials), 'materials': materials})
        self.qc.write_text(json.dumps({'schema_version': 1, 'assets': original}))
        self.receipt = self.bundle / 'p1c01_png_material_conversion_receipt.json'
        self.receipt.write_text(json.dumps({'schema_version': 1, 'status': 'SOURCE_TEXTURES_CONVERTED_STATIC_ONLY',
                                            'asset_count': 5, 'assets': converted}))

    def test_all_five_unchanged_artifacts_pass_but_basket_is_held(self):
        report = impl.audit(self.bundle, self.qc)
        self.assertEqual(report['fbx_verified'], 5)
        self.assertEqual(report['png_verified'], 19)
        self.assertEqual(report['assets_held_for_lod'], ['wicker_basket_01'])
        self.assertTrue(all(not item['ue_imported'] for item in report['assets']))

    def test_corrupt_fbx_fails_before_unreal(self):
        path = self.bundle / f'{impl.ASSETS[0]}.fbx'
        # The real artifact layout has the mesh inside its own asset folder.
        path = self.bundle / impl.ASSETS[0] / f'{impl.ASSETS[0]}.fbx'
        path.write_bytes(b'bad')
        with self.assertRaisesRegex(impl.PreflightError, 'FBX_SIZE_MISMATCH'):
            impl.audit(self.bundle, self.qc)

    def test_wrong_orm_ao_fails_even_with_matching_receipt_hash(self):
        slug = impl.ASSETS[0]
        png = self.bundle / slug / f'TX_{slug}_Main_ORM.png'
        Image.new('RGB', (1024, 1024), (13, 127, 0)).save(png)
        receipt = json.loads(self.receipt.read_text())
        for item in receipt['assets']:
            if item['asset_id'] == slug:
                for m in item['materials'][0]['maps']:
                    if m['role'] == 'ORM':
                        m['bytes'], m['sha256'] = png.stat().st_size, impl.sha256_file(png)
        self.receipt.write_text(json.dumps(receipt))
        with self.assertRaisesRegex(impl.PreflightError, 'INVALID_WHITE_AO_FALLBACK'):
            impl.audit(self.bundle, self.qc)

    def test_unlisted_extra_file_rejected(self):
        (self.bundle / 'not_in_receipt.txt').write_text('unverified')
        with self.assertRaisesRegex(impl.PreflightError, 'UNTRACKED_OR_MISSING_BUNDLE_FILES'):
            impl.audit(self.bundle, self.qc)

    def test_path_traversal_rejected(self):
        with self.assertRaisesRegex(impl.PreflightError, 'UNSAFE_ARTIFACT_PATH'):
            impl.safe_file(self.bundle, '../outside.png')


if __name__ == '__main__':
    unittest.main()
