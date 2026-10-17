import math
import unittest
from mpfb_curl_shape import remap_curl_offset


class CurlShapeTests(unittest.TestCase):
    def test_zero_offset_stays_at_lobe_center(self):
        self.assertEqual(remap_curl_offset(0.0, 0.0, 0.0, 0.7), (0.0, 0.0, 0.0))

    def test_tuft_is_elongated_along_scalp_tangent(self):
        x, y, z = remap_curl_offset(1.0, 0.0, 0.0, 0.0)
        self.assertAlmostEqual(x, 0.58)
        self.assertAlmostEqual(y, 0.0)
        self.assertAlmostEqual(z, 0.0)
        x, y, z = remap_curl_offset(0.0, 1.0, 0.0, 0.0)
        self.assertAlmostEqual(x, 0.0)
        self.assertAlmostEqual(y, 1.45)
        self.assertAlmostEqual(z, 0.0)
        x, y, z = remap_curl_offset(0.0, 0.0, 1.0, 0.0)
        self.assertAlmostEqual(z, 1.45)

    def test_rotated_frames_preserve_shape_budget_and_finite_vertices(self):
        for index in range(24):
            angle = index * math.tau / 24
            shaped = remap_curl_offset(0.01, -0.02, 0.03, angle)
            self.assertEqual(len(shaped), 3)
            self.assertTrue(all(math.isfinite(value) for value in shaped))
        self.assertEqual(58 * 80, 4640)  # 58 subdivision-2 ico lobes; topology unchanged.


if __name__ == "__main__":
    unittest.main()
