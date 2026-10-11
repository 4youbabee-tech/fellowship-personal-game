import unittest

from validate_p1c01_cloud_asset_manifests import (
    REQUIRED_CHARACTER_BATCHES,
    REQUIRED_MATERIAL_BATCHES,
    REQUIRED_STATIC_BATCHES,
    load_manifest,
    validate_manifest,
)


class P1C01CloudAssetManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load_manifest()

    def test_required_static_batches_exist(self):
        ids = {row["id"] for row in self.manifest["static_world_asset_batches"]}
        self.assertTrue(REQUIRED_STATIC_BATCHES.issubset(ids))

    def test_required_character_batches_exist(self):
        ids = {row["id"] for row in self.manifest["character_factory_batches"]}
        self.assertTrue(REQUIRED_CHARACTER_BATCHES.issubset(ids))

    def test_required_material_batches_exist(self):
        ids = {row["id"] for row in self.manifest["material_application_batches"]}
        self.assertTrue(REQUIRED_MATERIAL_BATCHES.issubset(ids))

    def test_whole_game_region_seed_rows_are_present(self):
        self.assertGreaterEqual(len(self.manifest["whole_game_seed_material_families"]), 28)

    def test_validator_accepts_current_manifest(self):
        validate_manifest(self.manifest)


if __name__ == "__main__":
    unittest.main()
