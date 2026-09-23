import copy
import unittest

from governance_contracts import validate_development_mode


def fixture():
    return {
        "development_mode_contract": {
            "authority": "Data/ProjectGovernor.json",
            "modes": {
                "W00_ARCHITECTURAL_STABILIZATION": {
                    "supersedes": "VISUAL_PRODUCTION_FIRST",
                    "class": "STABILIZATION",
                }
            },
            "required_manual_only_labels": [
                "PIE-TESTED",
                "DEVICE-TESTED",
                "VISUALLY-ACCEPTED",
                "PERFORMANCE-ACCEPTED",
            ],
        },
        "development_mode": {
            "id": "W00_ARCHITECTURAL_STABILIZATION",
            "supersedes": "VISUAL_PRODUCTION_FIRST",
            "proof_boundary": {
                "machine_evidence_cannot_promote_manual_acceptance": True,
                "manual_only_labels": [
                    "PIE-TESTED",
                    "DEVICE-TESTED",
                    "VISUALLY-ACCEPTED",
                    "PERFORMANCE-ACCEPTED",
                ],
            },
        },
    }


class DevelopmentModeContractTests(unittest.TestCase):
    def test_registered_mode_with_structured_proof_boundary_passes(self):
        self.assertEqual(validate_development_mode(fixture()), [])

    def test_unknown_mode_fails_without_validator_allowlist_change(self):
        value = fixture()
        value["development_mode"]["id"] = "FUTURE_MODE"
        self.assertTrue(validate_development_mode(value))

    def test_supersedes_drift_fails(self):
        value = fixture()
        value["development_mode"]["supersedes"] = "SOMETHING_ELSE"
        self.assertTrue(validate_development_mode(value))

    def test_missing_manual_label_fails(self):
        value = fixture()
        value["development_mode"]["proof_boundary"]["manual_only_labels"].remove("DEVICE-TESTED")
        self.assertTrue(validate_development_mode(value))

    def test_prose_is_not_used_as_proof(self):
        value = fixture()
        value["development_mode"]["rules"] = [
            "PIE evidence device performance visual words are all present"
        ]
        value["development_mode"]["proof_boundary"]["machine_evidence_cannot_promote_manual_acceptance"] = False
        self.assertTrue(validate_development_mode(value))


if __name__ == "__main__":
    unittest.main()
