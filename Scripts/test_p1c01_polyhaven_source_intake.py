"""Source-only bounded Poly Haven intake regression fixtures. Network never needed."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stage_p1c01_polyhaven as impl


def spec(name, content=b'FBX sample'):
    return {'url': 'https://dl.polyhaven.org/asset/' + name,
            'size': len(content), 'md5': hashlib.md5(content).hexdigest()}


class StageTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {'schema_version': 1, 'asset_category': 'STATIC_MESH',
                         'candidates': [{'provider_asset_id': 'painted_wooden_bench'}]}
        self.payload = {'fbx': {'1k': {'fbx': {
            **spec('bench.fbx'), 'include': {'textures/diff.png': spec('diff.png', b'12345')}
        }}}}

    def test_fbx_plan_with_texture_dependency(self):
        plan = impl.plan_from_fbx_files(self.payload, 'painted_wooden_bench')
        self.assertEqual(len(plan), 2)
        self.assertEqual(plan[0]['path'], 'painted_wooden_bench.fbx')
        self.assertEqual(plan[1]['path'], 'textures/diff.png')

    def test_reject_unsafe_texture_path(self):
        payload = {'fbx': {'1k': {'fbx': {
            **spec('bench.fbx'), 'include': {'../outside.png': spec('diff.png')}
        }}}}
        with self.assertRaisesRegex(impl.IntakeError, 'UNSAFE_FILENAME'):
            impl.plan_from_fbx_files(payload, 'painted_wooden_bench')

    def test_reject_untrusted_download_host(self):
        with self.assertRaisesRegex(impl.IntakeError, 'UNTRUSTED'):
            impl.file_spec('x.png', {'url': 'https://other.example/x.png', 'size': 5, 'md5': '0'*32})

    def test_no_texture_dependencies_rejected(self):
        bad = {'fbx': {'1k': {'fbx': spec('bench.fbx')}}}
        with self.assertRaisesRegex(impl.IntakeError, 'NO_SURFACE_TEXTURE_DEPENDENCIES'):
            impl.plan_from_fbx_files(bad, 'painted_wooden_bench')

    def test_missing_native_fbx_fails_early(self):
        with self.assertRaisesRegex(impl.IntakeError, 'NO_NATIVE_FBX_AT_1K'):
            impl.plan_from_fbx_files({'gltf': {'1k': {}}}, 'painted_wooden_bench')

    def test_source_stage_success_receipt_does_not_claim_ue(self):
        def save(specification, path):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'x' * specification['size'])
            return {'relative_file': specification['path'], 'bytes': specification['size'], 'sha256': '1'*64}
        with tempfile.TemporaryDirectory() as tmp, patch.object(impl, 'read_json', return_value=self.payload), patch.object(impl, 'download_verified', side_effect=save):
            d=impl.stage(self.manifest, Path(tmp), max_bytes=1000)
            self.assertEqual(d['source_assets_staged'],1)
            self.assertEqual(d['asset_results'][0]['stage'],'STAGED_SOURCE_ONLY')
            self.assertIn('No Unreal import',d['evidence_boundary'])
            self.assertTrue((Path(tmp)/'p1c01_polyhaven_source_receipt.json').exists())

    def test_download_budget_quarantines_but_writes_receipt(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(impl, 'read_json', return_value=self.payload):
            d=impl.stage(self.manifest, Path(tmp), max_bytes=2)
            self.assertEqual(d['source_assets_staged'],0)
            self.assertEqual(d['asset_results'][0]['stage'],'QUARANTINED_SOURCE_INTAKE')
            self.assertEqual(d['state'],'NO_QUALIFIED_ASSETS_STAGED')


    def test_source_delta_guard_ignores_docs_but_not_asset_scripts(self):
        import re
        import subprocess
        workflow = (Path(__file__).resolve().parents[1] / ".github" / "workflows" /
                    "p1c01-polyhaven-source-stage.yml").read_text(encoding="utf-8")
        self.assertIn("docs_only_no_source_changes", workflow)
        self.assertIn("needs_stage=false", workflow)
        self.assertIn("PR_BEFORE:", workflow)
        self.assertIn("if: always() && steps.source_delta.outputs.needs_stage == 'true'", workflow)
        match = re.search(r"grep -Eq '([^']+)'", workflow)
        self.assertIsNotNone(match)
        pattern = match.group(1)
        for filename in [
            "Docs/CURRENT_PROJECT_STATE.md",
            "Docs/PRODUCTION_COMPLETENESS_MATRIX.md",
            "Data/ProjectGovernor.json",
            "Data/P1C01PolyHavenFirstWaveQCV1.json",
        ]:
            result = subprocess.run(["grep", "-Eq", pattern], input=filename + "\n",
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 1, filename)
        for filename in [
            "Data/P1C01PhotorealSourcePilotV1.json",
            "Scripts/stage_p1c01_polyhaven.py",
            "Scripts/build_p1c01_png_materials.py",
            ".github/workflows/p1c01-polyhaven-source-stage.yml",
        ]:
            result = subprocess.run(["grep", "-Eq", pattern], input=filename + "\n",
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, filename)



if __name__ == '__main__':
    unittest.main()
