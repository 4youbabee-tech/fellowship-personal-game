import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from offline_production_classifier import classify, classify_path


class OfflineProductionClassifierTests(unittest.TestCase):
    def test_docs_and_offline_queue_are_safe_without_runner(self):
        result = classify(
            [
                "Docs/OFFLINE_FAST_PRODUCTION_PROTOCOL.md",
                "Data/OfflineFastProductionQueueV1.json",
                "Scripts/offline_production_classifier.py",
            ]
        )

        self.assertTrue(result["runner_offline_safe"])
        self.assertFalse(result["self_hosted_runner_blocked"])

    def test_runtime_source_requires_self_hosted_runner(self):
        result = classify(["Source/ShireJourney/Private/ShirePrototypeWorldBuilder.cpp"])

        self.assertFalse(result["runner_offline_safe"])
        self.assertTrue(result["self_hosted_runner_blocked"])

    def test_pbr_prep_scripts_stay_source_only(self):
        entry = classify_path("Scripts/preflight_p1c01_verified_fbx.py")

        self.assertEqual(entry.bucket, "asset_prep_source_only")

    def test_unknown_path_needs_review_but_does_not_trigger_runner(self):
        result = classify(["Tools/new-helper.txt"])

        self.assertFalse(result["runner_offline_safe"])
        self.assertFalse(result["self_hosted_runner_blocked"])


if __name__ == "__main__":
    unittest.main()
