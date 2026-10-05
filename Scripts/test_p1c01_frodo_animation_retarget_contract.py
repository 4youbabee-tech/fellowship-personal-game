import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrodoAnimationRetargetContract(unittest.TestCase):
    def test_manifest_pins_exact_source_and_target(self):
        data=json.loads((ROOT/'Data'/'P1C01FrodoAnimationRetargetV1.json').read_text(encoding='utf-8'))
        self.assertEqual(data['target']['normalized_sha256'],'75d715f6ce4673a650a4382bc4f86b7ae0baf0fe548cc63f9b6ded1800f669be')
        self.assertEqual(data['source']['archive_sha256'],'18ff1a7215f4852b320203e8aaf02a1578b5c8eef9027fbaedfcedc7b85a3ac2')
        self.assertEqual(data['source']['unreal_fbx_sha256'],'c836c5d47de2a414818f7644632ac43aa84475df6709f4514b9410d232800fd9')
        self.assertEqual(data['source']['animated_format'],'FBX')
        self.assertEqual({x['action_leaf'] for x in data['clips'].values()},{'Idle_Loop','Walk_Loop','Jog_Fwd_Loop'})
        self.assertFalse(data['execution_contract']['self_hosted_ue4_reserved_before_hosted_retarget_pass'])
        self.assertFalse(data['execution_contract']['runtime_integration_allowed'])
        self.assertTrue(data['execution_contract']['use_exact_prior_ue4_gated_winner_artifact'])
        self.assertEqual(data['target']['exact_winner_workflow_run'],37243788900)

    def test_script_is_fail_closed_and_keeps_acceptance_boundaries(self):
        text=(ROOT/'Scripts'/'run_p1c01_frodo_animation_retarget.py').read_text(encoding='utf-8')
        for token in (
            'RETARGET_TARGET_SHA256_FAIL',
            'RETARGET_ARCHIVE_SHA256_FAIL',
            'RETARGET_SOURCE_FBX_SHA256_FAIL',
            'RETARGET_NO_NONTRIVIAL_TARGET_DEFORMATION',
            'RETARGET_BOUNDS_RATIO_FAIL',
            "'retarget_visual_accepted': False",
            "'ue4_animation_imported': False",
            "'runtime_integration_allowed': False",
            "object_types={'ARMATURE'}",
        ):
            self.assertIn(token,text)

    def test_workflow_is_hosted_and_regenerates_target(self):
        text=(ROOT/'.github'/'workflows'/'p1c01-frodo-animation-retarget.yml').read_text(encoding='utf-8')
        self.assertIn('runs-on: ubuntu-latest',text)
        self.assertNotIn('self-hosted',text)
        self.assertIn('stage_p1c01_human_wave2.ps1',text)
        self.assertIn('P1C01_FRODO_HOSTED_RETARGET_RECEIPT_PASS',text)
        self.assertIn('actions/download-artifact@v4',text)
        self.assertIn('P1C01_FRODO_RETARGET_PRIOR_WINNER_PASS',text)
        self.assertIn('actions: read',text)


if __name__=='__main__':
    unittest.main()
