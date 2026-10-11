#!/usr/bin/env python3
"""Regression guard for recorded P1C01 UE4 import/runtime evidence."""
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'Data' / 'P1C01EngineImportRuntimeEvidence20261012.json'


class P1C01EngineImportRuntimeEvidenceTests(unittest.TestCase):
    def load_evidence(self):
        return json.loads(EVIDENCE.read_text(encoding='utf-8'))

    def test_import_and_headless_runtime_evidence_is_complete(self):
        data = self.load_evidence()

        self.assertEqual('P1C01', data['chapter'])
        self.assertEqual('success', data['workflow_run']['conclusion'])
        self.assertEqual(440, data['import_evidence']['imported_file_count'])
        self.assertEqual(0, data['import_evidence']['import_failure_count'])
        self.assertEqual(16, data['import_evidence']['verified_pbr_material_bind_count'])
        self.assertEqual(16, data['import_evidence']['verified_pbr_import_qc_count'])
        self.assertEqual(16, data['import_evidence']['derived_fbx_working_copy_count'])
        self.assertTrue(data['evidence_status']['compile_tested'])
        self.assertTrue(data['evidence_status']['production_import_tested'])
        self.assertTrue(data['evidence_status']['headless_runtime_audited'])

    def test_warning_debt_remains_zero_tolerance(self):
        data = self.load_evidence()

        for key, value in data['warning_debt'].items():
            self.assertEqual(0, value, key)

    def test_does_not_claim_package_device_visual_or_gate_acceptance(self):
        data = self.load_evidence()
        status = data['evidence_status']

        self.assertFalse(status['pie_tested'])
        self.assertFalse(status['windows_package_created'])
        self.assertFalse(status['device_tested'])
        self.assertFalse(status['visually_accepted'])
        self.assertFalse(status['gate_6_7_closed'])
        self.assertGreaterEqual(len(data['blockers_remaining']), 4)


if __name__ == '__main__':
    unittest.main()
