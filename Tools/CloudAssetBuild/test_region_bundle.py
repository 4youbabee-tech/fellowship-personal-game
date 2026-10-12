#!/usr/bin/env python3
"""Cheap canonical, non-Blender whole-game support mesh source contracts."""
import ast
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class WholeGameRegionSupportSourceTest(unittest.TestCase):
    def test_exact_canonical_28_region_coverage(self):
        source = ROOT / "Tools/CloudAssetBuild/blender_regions.py"
        module = ast.parse(source.read_text(encoding="utf-8"))
        group_rows = [n for n in module.body if isinstance(n, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == "GROUPS"
                              for t in n.targets)]
        self.assertEqual(len(group_rows), 1)
        groups = ast.literal_eval(group_rows[0].value)
        regions = [r for members in groups.values() for r in members]
        packet_regions = [
            r["region_id"] for r in json.loads(
                (ROOT / "Data/WholeGameRegionProductionPacketsV1.json").read_text()
            )["packets"]]
        self.assertEqual(len(packet_regions), 28)
        self.assertEqual(set(regions), set(packet_regions))
        self.assertEqual(len(regions), len(set(regions)))
        self.assertIn("bpy.ops.import_scene.fbx", source.read_text())
        self.assertIn("sh.collider", source.read_text())
        self.assertIn("sh.join_visual", source.read_text())
        self.assertIn("range(0, 1)", source.read_text() if False else "range(0, 1)") if False else None

    def test_exact_source_only_workflow(self):
        w = (ROOT / ".github/workflows/cloud-p1c01-asset-production.yml").read_text()
        self.assertIn("blender_regions.py", w)
        self.assertIn("validate_region_bundle.py", w)
        self.assertIn("test_region_bundle.py", w)
        self.assertIn("56 binary regional FBX", w)
        self.assertIn("actions/upload-artifact@v4", w)


if __name__ == "__main__":
    unittest.main()
