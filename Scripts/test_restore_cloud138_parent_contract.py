#!/usr/bin/env python3
"""Regression: Cloud138 restore cannot roll back newer UE4 curated PBR master."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from restore_cloud138_unreal import CURRENT_MASTER_REL, CURRENT_MASTER, SOURCE, restore


def digest(data):
    return hashlib.sha256(data).hexdigest()


class Cloud138SharedParentTests(unittest.TestCase):
    def make_case(self, root, bad_master=False):
        source = root / "warehouse" / "_unreal_cloud138" / SOURCE
        checkout = root / "checkout"
        rows = []
        old = b"old-authoritative-master-package" * 150
        current = (old if bad_master else b"new-current-ue4-compiled-pbr-parent" * 150)
        paths = [CURRENT_MASTER_REL] + [
            "Content/Production/World/Shire/Cloud138/Cloud138Test%03d.uasset" % n
            for n in range(89)
        ]
        total = 0
        for i, rel in enumerate(paths):
            raw = old if i == 0 else ("cloud138-synthetic-%03d" % i).encode() * 160
            path = source / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            total += len(raw)
            rows.append({"relative": rel,
                         "game_asset": "/Game/" + rel[8:-7],
                         "sha256": digest(raw), "bytes": len(raw)})
        report = {"source_commit": SOURCE,
                  "stage": "UE4_IMPORTED_REOPENED_PERSISTED_NOT_WORLD_PLACED",
                  "new_uassets": 89, "dependent_parent_uassets": 1,
                  "world_placed": False, "nav_quarantined_assets": [],
                  "files": rows, "payload_bytes": total}
        (source / "unreal_receipt.json").write_text(json.dumps(report), encoding="utf-8")
        master = checkout / CURRENT_MASTER_REL
        master.parent.mkdir(parents=True, exist_ok=True)
        master.write_bytes(current)
        return source, checkout, master, paths, current

    def test_old_parent_is_not_restored_over_current_one(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, checkout, master, paths, original = self.make_case(root)
            self.assertEqual(restore(root / "warehouse", checkout), 90)
            self.assertEqual(master.read_bytes(), original)
            self.assertEqual(
                (checkout / paths[44]).read_bytes(),
                (source / paths[44]).read_bytes())
            receipt = json.loads((checkout / "Saved/Cloud138Unreal/restored.json").read_text())
            self.assertEqual(receipt["restored_cloud138_packages"], 89)
            self.assertEqual(receipt["preserved_current_pbr_parent_packages"], 1)
            self.assertEqual(receipt["current_pbr_parent"], CURRENT_MASTER)
            self.assertEqual(receipt["current_pbr_parent_sha256"], digest(original))
            self.assertEqual(restore(root / "warehouse", checkout), 90)
            self.assertEqual(master.read_bytes(), original)

    def test_missing_current_master_fails_closed_before_restoration(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, checkout, master, paths, original = self.make_case(root)
            master.unlink()
            with self.assertRaisesRegex(AssertionError, "MASTER_NOT_PRODUCED"):
                restore(root / "warehouse", checkout)
            self.assertFalse((checkout / paths[1]).exists())

    def test_stale_current_master_fails_closed_before_restoration(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, checkout, master, paths, original = self.make_case(root, bad_master=True)
            with self.assertRaisesRegex(AssertionError, "STALE_PARENT"):
                restore(root / "warehouse", checkout)
            self.assertFalse((checkout / paths[1]).exists())

    def test_corrupt_source_fails_before_restoration(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, checkout, master, paths, original = self.make_case(root)
            (source / paths[2]).write_bytes(b"corrupted")
            with self.assertRaises(AssertionError):
                restore(root / "warehouse", checkout)
            self.assertEqual(master.read_bytes(), original)
            self.assertFalse((checkout / paths[1]).exists())


if __name__ == "__main__":
    unittest.main()
