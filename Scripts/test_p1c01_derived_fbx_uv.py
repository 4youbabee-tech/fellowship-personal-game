"""Offline P1C01 UV repair regression (does not invoke Blender or Unreal)."""
import unittest
from pathlib import Path

import p1c01_derived_fbx_uv as uv


class SelectiveUVTests(unittest.TestCase):
    def test_valid_island_is_not_eligible_for_repair(self):
        self.assertFalse(uv.needs_uv_repair([(0, 0), (1, 0), (1, 1), (0, 1)]))

    def test_nearly_collapsed_uv_is_detected(self):
        self.assertTrue(uv.needs_uv_repair([(0, 0), (1e-9, 0), (0, 1e-9)]))

    def test_nonfinite_uv_is_detected(self):
        self.assertTrue(uv.needs_uv_repair([(0, 0), (float('nan'), 0), (0, 1)]))

    def test_projected_square_is_nondegenerate_and_aspect_safe(self):
        result = uv.project_face_uv([(10, 0, 2), (12, 0, 2), (12, 1, 2), (10, 1, 2)], (0, 0, 1))
        self.assertEqual(result, [(0, 0), (1, 0), (1, 0.5), (0, 0.5)])
        self.assertFalse(uv.needs_uv_repair(result))

    def test_axis_projection_supports_walls(self):
        self.assertFalse(uv.needs_uv_repair(uv.project_face_uv([(0, 7, 0), (2, 7, 0), (0, 7, 1)], (0, 1, 0))))

    def test_irrecoverable_geometry_fails_closed(self):
        with self.assertRaises(uv.DegenerateUVError):
            uv.project_face_uv([(0, 0, 0), (1, 0, 0), (2, 0, 0)], (0, 0, 1))

    def test_normalizer_only_repairs_invalid_uv_on_derivative(self):
        s = (Path(__file__).parent / 'normalize_verified_pbr_blender.py').read_text(encoding='utf-8')
        self.assertIn('if needs_uv_repair(old_uv):', s)
        self.assertIn('loop[uv_layer].uv = new_uv', s)
        self.assertIn('repair_degenerate_uvs(mesh)', s)
        self.assertNotIn('bmesh.ops.remove_doubles', s)

    def test_preflight_cache_changes_with_normalizer(self):
        s = (Path(__file__).parent / 'preflight_p1c01_verified_fbx.py').read_text(encoding='utf-8')
        self.assertIn('normalizer_sha256', s)
        self.assertIn('uv_helper_sha256', s)
        self.assertIn('"schema_version":2', s)


if __name__ == '__main__':
    unittest.main()
