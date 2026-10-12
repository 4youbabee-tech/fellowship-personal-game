#!/usr/bin/env python3
"""Network-free Cloud138 source-to-Unreal intake safety regression."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from cloud138_unreal_intake import (
    SOURCE_COMMIT, STAGE_REL, copy_exact, load_plan, saved_asset_path,
    persist, write_json,
)


def h(value):
    return hashlib.sha256(value).hexdigest()


class Cloud138IntakeTests(unittest.TestCase):
    def fixture(self, root):
        rows = []
        for i in range(118):
            path = root / "Saved/Cloud138Unreal/src" / ("asset%03d.fbx" % i)
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = ("source%d" % i).encode("ascii")
            path.write_bytes(payload)
            rows.append({"target": path.relative_to(root).as_posix(),
                         "sha256": h(payload), "asset": "/Game/Production/Synthetic%d" % i,
                         "family": "Synthetic%d" % i, "kind": "mesh", "lod": 0})
        write_json(root / STAGE_REL, {
            "source_commit": SOURCE_COMMIT,
            "mode": "P1C01_SOURCE_STAGED_NO_UNREAL_CLAIMS",
            "source_rows": rows, "regional_fbx_held_in_warehouse": 56,
            "ue_imported": False,
        })
        return rows

    def test_118_staged_hashes_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            self.assertEqual(len(load_plan(root)["source_rows"]), 118)

    def test_mutation_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = self.fixture(root)
            (root / rows[3]["target"]).write_bytes(b"modified")
            with self.assertRaisesRegex(ValueError, "STAGED_FILE_DRIFT"):
                load_plan(root)

    def test_relative_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = self.fixture(root)
            rows[0]["target"] = "../../escape.fbx"
            value = json.loads((root / STAGE_REL).read_text())
            value["source_rows"] = rows
            write_json(root / STAGE_REL, value)
            with self.assertRaisesRegex(ValueError, "STAGED_FILE_DRIFT"):
                load_plan(root)

    def test_existing_output_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, dest = root / "source.fbx", root / "dest.fbx"
            source.write_bytes(b"authored")
            dest.write_bytes(b"some-other-file")
            with self.assertRaisesRegex(ValueError, "STAGE_CONFLICT"):
                copy_exact(source, dest, h(source.read_bytes()))

    def test_package_destination_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(
                saved_asset_path(root, "/Game/Production/World/Shire/Cloud138/X"),
                root / "Content/Production/World/Shire/Cloud138/X.uasset")
            with self.assertRaisesRegex(ValueError, "UNSAFE_GAME_ASSET_PATH"):
                saved_asset_path(root, "/Game/Maps/P1C02")

    def test_source_only_is_not_a_persistence_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.fixture(root)
            with self.assertRaises((ValueError, FileNotFoundError)):
                persist(root, root, {"source_zip_sha256": "unknown"})


if __name__ == "__main__":
    unittest.main()
