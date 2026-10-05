import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrodoAnimationSourceContract(unittest.TestCase):
    def test_manifest_is_public_cc0_fbx_only_and_ue4_deferred(self):
        data = json.loads((ROOT / 'Data' / 'P1C01FrodoAnimationSourceV1.json').read_text(encoding='utf-8'))
        src = data['animation_source']
        self.assertEqual(src['provider'], 'OpenGameArt')
        self.assertEqual(src['creator'].lower(), 'quaternius')
        self.assertEqual(src['observed_license'].upper(), 'CC0')
        self.assertEqual(src['required_final_animation_format'].upper(), 'FBX')
        self.assertTrue(src['download_url'].startswith('https://opengameart.org/'))
        self.assertEqual(data['archive_policy']['animated_obj_policy'], 'IGNORE_NOT_ACCEPTED')
        self.assertEqual(data['archive_policy']['accepted_animation_source_format'], 'FBX')
        self.assertFalse(data['execution_contract']['self_hosted_ue4_reserved_before_source_inventory_pass'])
        self.assertFalse(data['execution_contract']['runtime_integration_allowed'])
        self.assertEqual(set(data['required_clips']), {'idle', 'walk', 'run'})
        self.assertEqual(data['technical_target']['normalized_sha256'], '75d715f6ce4673a650a4382bc4f86b7ae0baf0fe548cc63f9b6ded1800f669be')

    def test_inventory_script_fail_closed_markers(self):
        text = (ROOT / 'Scripts' / 'run_p1c01_frodo_animation_source_inventory.py').read_text(encoding='utf-8')
        for token in (
            'ANIMATION_SOURCE_FBX_MISSING',
            'ANIM_ARCHIVE_SHA256_FAIL',
            'ANIMATION_REQUIRED_CLIPS_MISSING',
            "'retarget_accepted': False",
            "'runtime_integration_allowed': False",
            "ext == '.obj'",
            "'.bmp'",
        ):
            self.assertIn(token, text)

    def test_workflow_is_hosted_only(self):
        text = (ROOT / '.github' / 'workflows' / 'p1c01-frodo-animation-source.yml').read_text(encoding='utf-8')
        self.assertIn('runs-on: ubuntu-latest', text)
        self.assertNotIn('self-hosted', text)
        self.assertNotIn('ci_build_unreal', text)
        self.assertIn('P1C01_FRODO_ANIMATION_SOURCE_CONTRACT_PASS', text)


if __name__ == '__main__':
    unittest.main()
