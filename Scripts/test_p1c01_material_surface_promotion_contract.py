import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class P1C01MaterialSurfacePromotionContract(unittest.TestCase):
    def test_generator_uses_complete_mtl_directives(self):
        text = (ROOT/'Scripts'/'prepare_p1c01_material_intake.ps1').read_text(encoding='utf-8')
        for token in (
            'function Resolve-WarehousePayloadPath',
            "$marker = '/ShireJourney/'",
            '$candidate.StartsWith($rootPrefix, [StringComparison]::OrdinalIgnoreCase)',
            'P1C01_MATERIAL_WAREHOUSE_PATH_REBASED',
            'Get-FileHash -LiteralPath $p -Algorithm SHA256',
        ):
            self.assertIn(token, text)
        for token in (
            '("newmtl {0}" -f [string]$item.material_name)',
            '("Pr {0}" -f $roughnessText)',
            '("Pm {0}" -f $metallicText)',
            '("Ks {0} {0} {0}" -f $ksText)',
            '("map_Kd {0}" -f [IO.Path]::GetFileName($dest))',
        ):
            self.assertIn(token, text)

    def test_approved_material_manifest_and_plan_count_match(self):
        import json
        manifest = json.loads((ROOT/'Data'/'ExternalAssetManifest.json').read_text(encoding='utf-8'))
        plan = json.loads((ROOT/'Data'/'ResourceIntegrationPlan.json').read_text(encoding='utf-8'))
        approved = [
            x for x in manifest.get('assets', [])
            if isinstance(x, dict)
            and x.get('provider') == 'POLY_HAVEN'
            and x.get('approval_status') == 'APPROVED'
            and str(x.get('asset_id', '')).startswith('P1C01_')
        ]
        self.assertEqual(len(approved), 8)
        self.assertEqual(plan['external_resource_policy']['current_approved_asset_count'], 8)
        for item in approved:
            self.assertEqual(item.get('license_class'), 'CC0')
            self.assertEqual(len(str(item.get('sha256', ''))), 64)
            self.assertTrue(str(item.get('source_url', '')).startswith('https://dl.polyhaven.org/'))
            self.assertTrue(str(item.get('relative_path', '')).startswith(
                'SourceAssets/Production/Imported/P1C01Materials/'))

    def test_promotion_workflow_is_bounded_and_conflict_safe(self):
        workflow = (ROOT/'.github'/'workflows'/'p1c01-material-surface-promotion.yml').read_text(encoding='utf-8')
        for token in (
            'Hosted material promotion preflight',
            'runs-on: ubuntu-latest',
            'self-hosted',
            'prepare_p1c01_material_intake.ps1',
            r'D:\actions-runner\_warehouse\ShireJourney',
            'P1C01_MATERIAL_SURFACE_PREPARED_PASS',
            'SourceAssets/Production/Imported/P1C01Materials',
            'git.exe lfs version',
            'git.exe -C $env:SHIRE_MATERIAL_SOURCE fetch --no-tags origin $env:HEAD_BRANCH',
            'reset --hard FETCH_HEAD',
            'P1C01_MATERIAL_SOURCE_PROMOTION_PASS',
        ):
            self.assertIn(token, workflow)
        self.assertIn('contents: write', workflow)
        self.assertNotIn('push --force', workflow.lower())
        trigger_block = workflow.split('jobs:', 1)[0]
        self.assertNotIn('SourceAssets/Production/Imported/P1C01Materials', trigger_block)


if __name__ == '__main__':
    unittest.main()
