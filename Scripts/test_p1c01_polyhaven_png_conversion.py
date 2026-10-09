"""Regression tests for P1C01 Poly Haven 1K PNG conversion; offline only."""
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_p1c01_png_materials as converter


class PNGSourceMaterialTests(unittest.TestCase):
    def test_opengl_to_directx_flips_green_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nor_gl_1k.png"
            pixels = np.zeros((1024, 1024, 3), dtype=np.uint8)
            pixels[:, :, 0] = 127
            pixels[:, :, 1] = 64
            pixels[:, :, 2] = 255
            Image.fromarray(pixels, "RGB").save(path)
            converted = np.asarray(converter.normal_dx(path))
            self.assertEqual(tuple(int(x) for x in converted[0, 0]), (127, 191, 255))

    def test_missing_source_map_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "one map expected"):
                converter.file_of(Path(tmp), "missing_map")

    def test_empty_staged_directory_cannot_claim_conversion(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "expected five staged assets"):
                converter.build(Path(tmp), Path(tmp) / "out")

    def test_corrupt_normal_dimensions_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "normal.png"
            Image.new("RGB", (64, 64), color=(127, 128, 255)).save(path)
            with self.assertRaisesRegex(ValueError, "normal not 1024"):
                converter.normal_dx(path)


if __name__ == "__main__":
    unittest.main()
