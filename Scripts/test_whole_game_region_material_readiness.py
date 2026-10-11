#!/usr/bin/env python3
"""Regression tests for whole-game region packet and P1C01 readiness audit."""
from copy import deepcopy
from pathlib import Path
import unittest

import audit_whole_game_region_material_readiness as audit


ROOT = Path(__file__).resolve().parents[1]


class WholeGameRegionMaterialReadinessTests(unittest.TestCase):
    def load_docs(self):
        packets = audit.read_json(ROOT / 'Data' / 'WholeGameRegionProductionPacketsV1.json')
        curated = audit.read_json(ROOT / 'Data' / 'P1C01DrivePhysicalCuratedSource20261012.json')
        disposition = audit.read_json(ROOT / 'Data' / 'P1C01SourceToRuntimeDispositionV1.json')
        return packets, curated, disposition

    def test_current_region_packets_and_p1c01_sources_are_readiness_clean(self):
        packets, curated, disposition = self.load_docs()

        errors = audit.audit_region_packets(packets)
        errors.extend(audit.audit_p1c01_curated_support(curated, disposition))

        self.assertEqual([], errors)
        summary = audit.build_readiness_summary(packets, curated)
        self.assertEqual(28, summary['region_packet_count'])
        self.assertTrue(summary['later_runtime_locked_until_p1c01_gate67'])
        self.assertGreaterEqual(summary['ready_source_summary']['P1C01_nature_lod_families'], 12)

    def test_rejects_missing_region_deliverable(self):
        packets, _, _ = self.load_docs()
        broken = deepcopy(packets)
        del broken['packets'][0]['deliverables']['materials']

        errors = audit.audit_region_packets(broken)

        self.assertTrue(any(error.startswith('MISSING_DELIVERABLES:SHIRE_HOBBITON') for error in errors))

    def test_rejects_claimed_p1c01_engine_import_before_evidence(self):
        _, curated, disposition = self.load_docs()
        broken = deepcopy(curated)
        broken['engine_imported'] = True

        errors = audit.audit_p1c01_curated_support(broken, disposition)

        self.assertIn('CURATED_FALSE_ENGINE_EVIDENCE_REQUIRED:engine_imported', errors)

    def test_rejects_later_runtime_unlock_disposition_drift(self):
        _, curated, disposition = self.load_docs()
        broken = deepcopy(disposition)
        broken['status'] = 'P1C02_RUNTIME_OPEN'

        errors = audit.audit_p1c01_curated_support(curated, broken)

        self.assertIn('DISPOSITION_STATUS_NOT_GATED', errors)


if __name__ == '__main__':
    unittest.main()
