import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MOD = Path(__file__).with_name("build_shire_kit.py")
spec = importlib.util.spec_from_file_location("shire_kit", MOD)
shire_kit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shire_kit)

def row(**overrides):
    value = {
        "id": "PH_TREE_SMALL_02",
        "source": "Approved/PH_TREE_SMALL_02/model.fbx",
        "source_url": "https://polyhaven.com/a/tree_small_02",
        "provider": "POLY_HAVEN",
        "license": "CC0",
        "license_evidence": "https://polyhaven.com/license",
        "external_asset_id": "PH_TREE_SMALL_02",
        "target_tris": 11000,
        "lods": [1.0, 0.5, 0.25],
        "collision": {"mode": "convex"},
        "material_group": "Nature/TreeCanopyBark",
        "status": "PENDING_SOURCE",
    }
    value.update(overrides)
    return value

class BuildShireKitTests(unittest.TestCase):
    def test_accepts_complete_pending_row_without_promoting_it(self):
        self.assertEqual(shire_kit.validate_manifest({"schema_version": 1, "assets": [row()]}), [])
        with tempfile.TemporaryDirectory() as tmp:
            source, reason = shire_kit.validate_input(row(), Path(tmp), {"assets": []})
        self.assertIsNone(source)
        self.assertEqual(reason, "PENDING_SOURCE")

    def test_rejects_duplicate_ids_and_bad_lod_sequence(self):
        errors = shire_kit.validate_manifest({"schema_version": 1, "assets": [
            row(), row(lods=[1.0, 0.25, 0.5])
        ]})
        self.assertIn("ROW_1_DUPLICATE_ID_PH_TREE_SMALL_02", errors)
        self.assertIn("ROW_1_LOD_RATIOS_MUST_DESCEND_FROM_ONE", errors)

    def test_blocks_unreceipted_or_unhashed_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "Approved/PH_TREE_SMALL_02/model.fbx"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"not-real-fbx")
            candidate = row(status="APPROVED", source="Approved/PH_TREE_SMALL_02/model.fbx")
            approved = {"assets": [{
                "id": "PH_TREE_SMALL_02", "status": "APPROVED",
                "source_url": candidate["source_url"], "license_class": "CC0",
                "provider": "POLY_HAVEN", "sha256": "0" * 64,
            }]}
            resolved, reason = shire_kit.validate_input(candidate, root, approved)
        self.assertIsNone(resolved)
        self.assertEqual(reason, "SOURCE_SHA256_MISMATCH")

    def test_source_builder_never_creates_primitive_geometry(self):
        source = MOD.read_text(encoding="utf-8")
        self.assertNotIn("primitive_cube_add", source)
        self.assertNotIn("primitive_cone_add", source)
        self.assertNotIn("primitive_ico_sphere_add", source)

    def test_rejects_path_escape_and_unknown_source_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            approved = {"assets": [{"id": "PH_TREE_SMALL_02", "status": "APPROVED"}]}
            resolved, reason = shire_kit.validate_input(row(
                status="APPROVED", source="../../outside.fbx"), root, approved)
        self.assertIsNone(resolved)
        self.assertEqual(reason, "SOURCE_PATH_ESCAPES_ROOT")

    def test_blocks_sources_outside_approved_external_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "Inbox" / "model.fbx"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"source")
            candidate = row(status="APPROVED", source="Inbox/model.fbx")
            receipt = {"assets": [{
                "id": candidate["external_asset_id"], "status": "APPROVED",
                "source_url": candidate["source_url"], "license_class": candidate["license"],
                "provider": candidate["provider"], "sha256": shire_kit.sha256_file(source),
            }]}
            resolved, reason = shire_kit.validate_input(candidate, root, receipt)
        self.assertIsNone(resolved)
        self.assertEqual(reason, "SOURCE_NOT_IN_APPROVED_ROOT")

if __name__ == "__main__":
    unittest.main()
