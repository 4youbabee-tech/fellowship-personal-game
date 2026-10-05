import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class P1C01MaterialSurfacePromotionContract(unittest.TestCase):
    def test_generator_uses_complete_mtl_directives(self):
        text = (ROOT/'Scripts'/'prepare_p1c01_material_intake.ps1').read_text(encoding='utf-8')
        for token in (
            '("newmtl {0}" -f [string]$item.material_name)',
            '("Pr {0}" -f $roughnessText)',
            '("Pm {0}" -f $metallicText)',
            '("Ks {0} {0} {0}" -f $ksText)',
            '("map_Kd {0}" -f [IO.Path]::GetFileName($dest))',
        ):
            self.assertIn(token, text)

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
