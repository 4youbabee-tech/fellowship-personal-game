import unittest
from live_governor_status import select_evidence


class LiveEvidenceTests(unittest.TestCase):
    def test_old_sha_cannot_certify_new_head(self):
        runs = [{"id": 9, "name": "Unreal Build Validation", "head_sha": "old",
                 "status": "completed", "conclusion": "success"}]
        self.assertEqual(select_evidence("new", runs)["unreal"]["status"], "NOT_OBSERVED")

    def test_new_pending_run_supersedes_old_success(self):
        runs = [{"id": i, "name": "Unreal Build Validation", "head_sha": "same",
                 "status": status, "conclusion": conclusion}
                for i, status, conclusion in [(1, "completed", "success"), (2, "queued", None)]]
        self.assertEqual(select_evidence("same", runs)["unreal"]["status"], "queued")

    def test_latest_attempt_failure_overrides_prior_attempt_success(self):
        runs = [{"id": 1, "run_attempt": i, "name": "Unreal Build Validation", "head_sha": "same",
                 "status": "completed", "conclusion": conclusion}
                for i, conclusion in [(1, "success"), (2, "failure")]]
        self.assertEqual(select_evidence("same", runs)["unreal"]["conclusion"], "failure")


if __name__ == "__main__":
    unittest.main()
