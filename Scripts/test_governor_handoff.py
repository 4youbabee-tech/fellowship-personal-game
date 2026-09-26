import unittest
from governor_handoff import validate_handoff, evidence_summary


def fixture():
    def record(sha, status):
        return {'sha': sha, 'pre_unreal': {'sha': sha, 'run_id': 1, 'status': 'SUCCESS'},
                'unreal': {'sha': sha, 'run_id': 2, 'status': status}}
    return {'session_handoff': {'source_head': 'a' * 40, 'next_actions': ['Verify'],
            'unverified_acceptance': ['Visual'], 'validation_snapshot': {
                'last_green': record('a' * 40, 'SUCCESS'),
                'latest_observed': record('b' * 40, 'CANCELLED')}}}


class HandoffTests(unittest.TestCase):
    def test_cancelled_current_does_not_erase_green_ancestor(self):
        self.assertEqual(validate_handoff(fixture()), [])

    def test_cannot_mix_old_success_into_new_head(self):
        g = fixture()
        g['session_handoff']['validation_snapshot']['latest_observed']['unreal']['sha'] = 'a' * 40
        self.assertTrue(validate_handoff(g))

    def test_failed_baseline_is_not_green(self):
        g = fixture()
        g['session_handoff']['validation_snapshot']['last_green']['unreal']['status'] = 'FAILURE'
        self.assertTrue(validate_handoff(g))

    def test_stale_legacy_copy_warns_without_blocking_valid_evidence(self):
        g = fixture()
        g['session_handoff']['source_head'] = 'c' * 40
        self.assertEqual(validate_handoff(g), [])
        summary = evidence_summary(g)
        self.assertIn('WARNING: legacy source_head differs', summary)
        self.assertIn('Last verified baseline: ' + 'a' * 40, summary)

    def test_checkpoint_rewrite_must_preserve_validation_snapshot(self):
        g = fixture()
        del g['session_handoff']['validation_snapshot']
        self.assertTrue(validate_handoff(g))

    def test_new_checkout_is_explicitly_unproven(self):
        self.assertIn('does not certify', evidence_summary(fixture(), 'c' * 40))

    def test_missing_experiential_boundary_is_rejected(self):
        g = fixture()
        del g['session_handoff']['unverified_acceptance']
        self.assertTrue(validate_handoff(g))


if __name__ == '__main__':
    unittest.main()
