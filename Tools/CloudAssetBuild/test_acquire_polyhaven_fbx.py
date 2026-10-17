"""Network-free contracts for the official Poly Haven FBX intake."""
import hashlib
import tempfile
import unittest
from pathlib import Path

import acquire_polyhaven_fbx as intake


class PolyHavenFbxIntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.payloads = {
            "mesh": b"actual-fbx-bytes",
            "maps/bench_basecolor.jpg": b"base-color",
            "maps/bench_normal.jpg": b"normal",
        }
        self.info = {
            "name": "Painted Wooden Bench", "type": 2,
            "authors": {"Kirill Sannikov": "All"},
            "files_hash": "6" * 40, "dimensions": [1165, 497, 889], "polycount": 630,
        }
        self.files = {
            "fbx": {
                "2k": {
                    "fbx": {
                        "url": "https://dl.polyhaven.org/models/painted_wooden_bench_2k.fbx",
                        "md5": hashlib.md5(self.payloads["mesh"]).hexdigest(),
                        "include": {
                            "maps/bench_basecolor.jpg": {
                                "url": "https://dl.polyhaven.org/maps/basecolor.jpg",
                                "md5": hashlib.md5(self.payloads["maps/bench_basecolor.jpg"]).hexdigest(),
                            },
                            "maps/bench_normal.jpg": {
                                "url": "https://dl.polyhaven.org/maps/normal.jpg",
                                "md5": hashlib.md5(self.payloads["maps/bench_normal.jpg"]).hexdigest(),
                            },
                        },
                    }
                },
                "1k": {"fbx": {"url": "https://dl.polyhaven.org/models/bench_1k.fbx"}},
            }
        }

    def tearDown(self):
        self.tmp.cleanup()

    def providers(self, url):
        return self.info if "/info/" in url else self.files

    def fake_download(self, url, target, md5):
        key = "mesh" if target.name == "painted_wooden_bench.fbx" else target.relative_to(self.root / "inbox").as_posix()
        payload = self.payloads[key]
        self.assertEqual(hashlib.md5(payload).hexdigest(), md5)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        return {"path": str(target), "bytes": len(payload),
                "md5": hashlib.md5(payload).hexdigest(), "sha256": hashlib.sha256(payload).hexdigest()}

    def test_acquires_dependency_complete_fbx_and_receipt_hashes(self):
        out = self.root / "inbox"
        receipt = intake.acquire("painted_wooden_bench", out, "painted_wooden_bench.fbx",
                                 get_json=self.providers, download=self.fake_download)
        self.assertEqual(receipt["status"], "CC0_POLYHAVEN_FBX_SOURCE_ACQUIRED")
        self.assertEqual(receipt["creator"], "Kirill Sannikov")
        self.assertEqual(receipt["resolution"], "2k")
        self.assertEqual(len(receipt["files"]), 3)
        self.assertTrue((out / "maps/bench_normal.jpg").is_file())
        self.assertTrue((out / "source_receipt.json").is_file())
        self.assertEqual(receipt["files"][0]["sha256"], hashlib.sha256(self.payloads["mesh"]).hexdigest())

    def test_selects_low_resolution_only_when_preferred_absent(self):
        resolution, entry = intake.select_fbx({"fbx": {"1k": {"fbx": {"url": "https://dl.polyhaven.org/bench.fbx"}}}})
        self.assertEqual(resolution, "1k")
        self.assertEqual(entry["url"], "https://dl.polyhaven.org/bench.fbx")

    def test_rejects_unsafe_api_include_path_before_writing(self):
        self.files["fbx"]["2k"]["fbx"]["include"] = {"../../escape.jpg": {"url": "https://dl.polyhaven.org/x.jpg"}}
        with self.assertRaisesRegex(ValueError, "PATH_TRAVERSAL"):
            intake.acquire("painted_wooden_bench", self.root / "out", "painted_wooden_bench.fbx",
                           get_json=self.providers, download=self.fake_download)

    def test_rejects_non_polyhaven_download_host(self):
        with self.assertRaisesRegex(ValueError, "HOST_REJECTED"):
            intake._safe_provider_url("https://attacker.example/bench.fbx")

    def test_existing_nonempty_inbox_is_never_overwritten(self):
        out = self.root / "existing"
        out.mkdir()
        sentinel = out / "keep.txt"
        sentinel.write_text("keep")
        with self.assertRaisesRegex(RuntimeError, "MUST_BE_NEW_OR_EMPTY"):
            intake.acquire("painted_wooden_bench", out, "painted_wooden_bench.fbx",
                           get_json=self.providers, download=self.fake_download)
        self.assertEqual(sentinel.read_text(), "keep")


if __name__ == "__main__":
    unittest.main()
