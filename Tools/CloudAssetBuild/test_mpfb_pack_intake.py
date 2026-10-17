"""Cheap source regression: prove ZIP tree preservation before hosted Blender."""
from pathlib import Path
import tempfile
import unittest
import zipfile

from mpfb_pack_intake import extract_verified_pack, relative_asset_path


class TestMpfbPackIntake(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.zip = self.root / "pack.zip"
        self.dest = self.root / "extracted"
        self.required = [("skins", "young_caucasian_male.mhmat"),
                         ("eyes", "low-poly.mhclo"),
                         ("hair", "short01.mhclo"),
                         ("clothes", "male_casualsuit01.mhclo")]

    def make_zip(self, extra=None, missing=None):
        entries = {}
        for kind, filename in self.required:
            if (kind, filename) != missing:
                entries[f"makehuman_system_assets_cc0/{kind}/{Path(filename).stem}/{filename}"] = b"material"
        entries["makehuman_system_assets_cc0/skins/young_caucasian_male/albedo.png"] = b"png"
        for i in range(50):
            entries[f"makehuman_system_assets_cc0/targets/test/{i:03d}.target"] = b"0"
        if extra:
            entries.update(extra)
        with zipfile.ZipFile(self.zip, "w") as handle:
            handle.writestr("makehuman_system_assets_cc0/skins/", b"")
            for name, data in entries.items():
                handle.writestr(name, data)

    def test_realistic_nested_core_layout_and_relative_texture(self):
        self.make_zip()
        count, total = extract_verified_pack(self.zip, self.dest, self.required)
        self.assertGreaterEqual(count, 50)
        self.assertGreater(total, 0)
        self.assertEqual((self.dest / "skins/young_caucasian_male/young_caucasian_male.mhmat").read_bytes(), b"material")
        self.assertEqual((self.dest / "skins/young_caucasian_male/albedo.png").read_bytes(), b"png")
        self.assertTrue((self.dest / "clothes/male_casualsuit01/male_casualsuit01.mhclo").is_file())

    def test_missing_required_fails_before_writing(self):
        self.make_zip(missing=("skins", "young_caucasian_male.mhmat"))
        with self.assertRaisesRegex(RuntimeError, "MPFB_CORE_ASSET_PACK_MISSING"):
            extract_verified_pack(self.zip, self.dest, self.required)
        self.assertFalse(self.dest.exists())

    def test_duplicate_normalized_target_rejected(self):
        self.make_zip(extra={"other-prefix/skins/young_caucasian_male/young_caucasian_male.mhmat": b"other"})
        with self.assertRaisesRegex(RuntimeError, "MPFB_DUPLICATE_ZIP_TARGET"):
            extract_verified_pack(self.zip, self.dest, self.required)
        self.assertFalse(self.dest.exists())

    def test_ambiguous_filename_in_same_category_rejected(self):
        self.make_zip(extra={"another/hair/different/short01.mhclo": b"other"})
        with self.assertRaisesRegex(RuntimeError, "MPFB_CORE_ASSET_PACK_MISSING_OR_AMBIGUOUS"):
            extract_verified_pack(self.zip, self.dest, self.required)
        self.assertFalse(self.dest.exists())

    def test_path_traversal_and_windows_escapes_rejected(self):
        for bad in ("prefix/skins/../skins/nope.mhmat", "C:/skins/a.mhmat",
                    "skins\\bad.mhmat", "/skins/bad.mhmat"):
            with self.subTest(path=bad):
                with self.assertRaisesRegex(RuntimeError, "MPFB_UNSAFE_ZIP_NAME|MPFB_ZIP_TRAVERSAL"):
                    relative_asset_path(bad)

    def test_flat_category_layout_also_supported(self):
        self.assertEqual(relative_asset_path("skins/young_caucasian_male.mhmat").as_posix(),
                         "skins/young_caucasian_male.mhmat")


if __name__ == "__main__":
    unittest.main()
