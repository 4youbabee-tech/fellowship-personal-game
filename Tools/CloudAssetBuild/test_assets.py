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
        self.assertEqual(cloud.count("runs-on: ubuntu-latest"), 2)
        self.assertNotRegex(cloud, r"(?m)^\s*(?:-\s*)?self-hosted\s*$")
        self.assertIn("actions/upload-artifact@v4", cloud)
        self.assertNotIn("workflow_dispatch:", cloud)


    def test_bag_end_world_mesh_catalog_is_physical_source_only(self):
        import ast
        source = (ROOT / "Tools/CloudAssetBuild/blender_shire.py").read_text(encoding="utf-8")
        module = ast.parse(source)
        rows = [n for n in module.body
                if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "MODELS" for t in n.targets)]
        self.assertEqual(len(rows), 1)
        models = ast.literal_eval(rows[0].value)
        self.assertEqual(len(models), 22)
        self.assertEqual(len(set(models)), len(models))
        self.assertTrue({"BagEndFrontWall", "RoundRoomWallArc", "RoundRoomFloor",
                         "Hearth", "Bookcase", "HobbitBed", "WoodenFootbridge",
                         "PartyCanopy", "StonePath", "MillWheel"}.issubset(models))
        # Validate family literals used by geometry primitives before the
        # expensive hosted Blender run; this guards the missing earth palette.
        palette_rows = [n for n in module.body
                        if isinstance(n, ast.Assign)
                        and any(isinstance(t, ast.Name) and t.id == "PALETTE"
                                for t in n.targets)]
        self.assertEqual(len(palette_rows), 1)
        palette = ast.literal_eval(palette_rows[0].value)
        primitive_family_index = {"box": 3, "cylinder": 4, "torus": 4, "ico": 3}
        for node in ast.walk(module):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            arg_index = primitive_family_index.get(node.func.id)
            if arg_index is None or len(node.args) <= arg_index:
                continue
            for literal in ast.walk(node.args[arg_index]):
                if isinstance(literal, ast.Constant) and isinstance(literal.value, str):
                    self.assertIn(literal.value, palette, "Unregistered PBR palette family")
        self.assertIn("UCX_", source)
        self.assertIn("FBX_VERSION_NOT_7400", source)
        self.assertIn("collision_groups", source)
        self.assertNotIn('version="BIN7400"', source)
        self.assertIn("safe_bevel = min(bevel, min(scale) * 0.16)", source)

    def test_pbr_source_cache_fails_closed_on_changed_content(self):
        workflow = (ROOT / ".github/workflows/cloud-p1c01-asset-production.yml").read_text(encoding="utf-8")
        self.assertIn("actions/cache/restore@v4", workflow)
        self.assertIn("actions/cache/save@v4", workflow)
        self.assertIn("hashFiles('Tools/CloudAssetBuild/materials.py', 'Data/WholeGameRegionProductionPacketsV1.json')", workflow)
        self.assertIn("if: steps.material_cache.outputs.cache-hit != 'true'", workflow)
        self.assertIn("Tools/CloudAssetBuild/validate_bundle.py --out", workflow)
        self.assertEqual(workflow.count("runs-on: ubuntu-latest"), 2)


if __name__ == "__main__":
    unittest.main()
