#!/usr/bin/env python3
"""Fast CPU-only regressions: source region IDs, repeatability and CI isolation."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from materials import REGION_FAMILIES, SURFACES, generate, sha256, validate_canon_map
from validate_bundle import validate

ROOT = Path(__file__).resolve().parents[2]


class CloudShireAssetTests(unittest.TestCase):
    def test_regions_are_exact_production_packet_set(self):
        self.assertEqual(len(validate_canon_map()), 28)
        self.assertEqual(len(SURFACES), 12)
        self.assertEqual(len(REGION_FAMILIES), 28)
        self.assertEqual(REGION_FAMILIES["BAG_END"][:2], ["bagend_plaster", "oak_timber"])

    def test_original_pbr_is_physical_and_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            first = Path(d) / "a"
            second = Path(d) / "b"
            m1 = generate(first, 128)
            m2 = generate(second, 128)
            self.assertTrue(validate(first, require_meshes=False))
            self.assertEqual(m1["physical_textures"], 36)
            self.assertEqual(m1["material_families"], 12)
            self.assertEqual(len(m1["region_bindings"]), 28)
            self.assertEqual(
                [f["sha256"] for f in m1["textures"]],
                [f["sha256"] for f in m2["textures"]],
                "Repeated generation must not silently change warehouse materials")
            self.assertFalse(m1["runtime_imported"])

    def test_owner_runner_is_not_triggered_by_source_prep(self):
        workflow = (ROOT / ".github/workflows/unreal-build-validation.yml").read_text(encoding="utf-8")
        cloud = (ROOT / ".github/workflows/cloud-p1c01-asset-production.yml").read_text(encoding="utf-8")
        self.assertGreaterEqual(workflow.count("'Tools/CloudAssetBuild/**'"), 2)
        self.assertIn("runs-on: ubuntu-latest", cloud)
        self.assertNotIn("self-hosted", cloud)
        self.assertIn("actions/upload-artifact@v4", cloud)
        self.assertNotIn("workflow_dispatch:", cloud)


if __name__ == "__main__":
    unittest.main()
