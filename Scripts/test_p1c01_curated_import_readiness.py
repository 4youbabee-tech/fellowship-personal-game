#!/usr/bin/env python3
"""Regression tests for P1C01 curated source import-readiness guards."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import audit_p1c01_curated_import_readiness as audit
import stage_p1c01_curated_original as stage
from test_stage_p1c01_curated_original import fixture


class P1C01CuratedImportReadinessTests(unittest.TestCase):
    def build_receipt(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            archive = Path(temp_dir) / 'curated.zip'
            archive_sha = fixture(archive)
            workspace = Path(temp_dir) / 'workspace'
            with patch.object(stage, 'CURATED_MANIFEST_SHA', archive_sha):
                return stage.stage_archive(archive, workspace)

    def assertHasError(self, receipt, prefix):
        errors = audit.audit_receipt(receipt)
        self.assertTrue(
            any(error.startswith(prefix) for error in errors),
            f'{prefix} not found in {errors}',
        )

    def test_generated_stage_receipt_is_import_ready_without_engine_claims(self):
        receipt = self.build_receipt()

        self.assertEqual([], audit.audit_receipt(receipt))
        self.assertFalse(receipt['engine_import_allowed_now'])
        self.assertFalse(receipt['unreal_asset_imported'])
        self.assertFalse(receipt['gate6_7_closed'])

    def test_rejects_side_lod_promoted_as_independent_runtime_mesh(self):
        receipt = self.build_receipt()
        family = receipt['mesh_families'][0]
        side_lod = next(key for key in family['lods'] if key != '0')
        family['lods'][side_lod]['import_mode'] = 'UE4_COMMANDLET_BASE_STATIC_MESH'

        self.assertHasError(receipt, 'SIDE_LOD_IMPORT_MODE')

    def test_rejects_external_license_file_leaking_into_source_stage(self):
        receipt = self.build_receipt()
        held_source = receipt['external_license_held'][0]['source']
        receipt['source_stage_files'].append({'source': held_source})

        self.assertHasError(receipt, 'EXTERNAL_SOURCE_STAGED')

    def test_rejects_material_texture_setting_drift(self):
        receipt = self.build_receipt()
        first_material = next(iter(receipt['material_triplets'].values()))
        first_material['ORM']['compression'] = 'TC_DEFAULT'

        self.assertHasError(receipt, 'ORM_COMPRESSION')


if __name__ == '__main__':
    unittest.main()
