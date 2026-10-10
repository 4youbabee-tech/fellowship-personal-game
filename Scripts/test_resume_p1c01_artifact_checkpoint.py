"""No-network loss/restart tests for pinned GitHub Artifact checkpoint transport."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import resume_p1c01_artifact_checkpoint as cp


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fake_entry(content: bytes, artifact_id=111) -> dict:
    return {"artifact_id": artifact_id, "source_run_id": 222, "name": "unit-mock-checkpoint",
            "size_bytes": len(content), "digest": "sha256:" + sha(content)}


def zipped(files: dict[str, bytes]) -> bytes:
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for filename, content in files.items():
            z.writestr(filename, content)
    return out.getvalue()


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.payload = b"fellowship" * 740
        self.entry = fake_entry(self.payload)

    def download(self, fetch, entry=None):
        return cp.download_chunks(self.root, entry or self.entry, fetch,
                                  chunk_size=1024, reserve_bytes=0, sleep_fn=lambda _: None)

    def fetcher(self, start, end, total):
        self.assertEqual(total, len(self.payload))
        return self.payload[start:end + 1]

    def test_interrupted_chunk_recovery_and_no_duplicate_requests(self):
        chunk_requests = []
        def fail_once_range(start, end, total):
            chunk_requests.append(start)
            if start >= 1024:
                raise TimeoutError("electricity/network loss")
            return self.fetcher(start, end, total)

        with self.assertRaisesRegex(cp.CheckpointError, "RETRIES_EXHAUSTED"):
            self.download(fail_once_range)
        journal_path = self.root / "artifact_111" / "download.checkpoint.json"
        journal = json.loads(journal_path.read_text(encoding="utf-8"))
        self.assertEqual(len(journal["completed_chunks"]), 1)
        self.assertEqual(journal["completed_chunks"][0], sha(self.payload[:1024]))
        self.assertEqual((self.root / "artifact_111" / "download.part").stat().st_size, 1024)
        resumed_calls = []
        def resume(start, end, total):
            resumed_calls.append(start)
            return self.fetcher(start, end, total)
        verified = self.download(resume)
        self.assertEqual(sha(verified.read_bytes()), sha(self.payload))
        self.assertTrue(resumed_calls)
        self.assertEqual(resumed_calls[0], 1024)
        self.assertTrue(all(i >= 1024 for i in resumed_calls))
        self.assertEqual(self.download(lambda *a: self.fail("should not fetch")).read_bytes(),
                         self.payload)

    def test_corrupted_checkpoint_file_is_rejected_without_new_download(self):
        self.download(self.fetcher)
        checkpoint_dir = self.root / "artifact_111"
        (checkpoint_dir / "verified.zip").unlink()
        part = checkpoint_dir / "download.part"
        part.write_bytes(b"forged")
        with self.assertRaisesRegex(cp.CheckpointError, "CHECKPOINT_WITH_MISSING_BYTES"):
            self.download(lambda *a: self.fail("should not fetch"))

    def test_checkpoint_hash_mismatch_fails_closed(self):
        self.download(self.fetcher)
        directory = self.root / "artifact_111"
        archive = directory / "verified.zip"
        archive.rename(directory / "download.part")
        with (directory / "download.part").open("r+b") as output:
            output.seek(0)
            output.write(b"invalid")
        with self.assertRaisesRegex(cp.CheckpointError, "CHUNK_HASH_MISMATCH"):
            self.download(lambda *a: self.fail("should not fetch"))

    def test_uncommitted_tail_is_discarded_not_entire_valid_prefix(self):
        self.download(self.fetcher)
        directory = self.root / "artifact_111"
        archive = directory / "verified.zip"
        archive.rename(directory / "download.part")
        journal_file = directory / "download.checkpoint.json"
        journal = json.loads(journal_file.read_text(encoding="utf-8"))
        journal["completed_chunks"] = journal["completed_chunks"][:2]
        cp.atomic_json(journal_file, journal)
        resumed = []
        def get(start, end, total):
            resumed.append(start)
            return self.fetcher(start, end, total)
        result = self.download(get)
        self.assertEqual(result.read_bytes(), self.payload)
        self.assertEqual(resumed[0], 2048)

    def test_zip_reuse_crc_and_no_network(self):
        payload = zipped({"p1c01_adaptive_polyhaven_receipt.json": b'{"license":"CC0"}',
                          "assets/good_mesh/good_mesh.fbx": b"Kaydara FBX Binary  " + b"\x00" * 1024})
        entry = fake_entry(payload, artifact_id=333)
        archive = cp.download_chunks(self.root, entry,
                                     lambda a, b, _: payload[a:b + 1],
                                     chunk_size=1024, reserve_bytes=0)
        root = cp.extract_verified_zip(archive, reserve_bytes=0)
        self.assertEqual((root / "assets/good_mesh/good_mesh.fbx").read_bytes(),
                         b"Kaydara FBX Binary  " + b"\x00" * 1024)
        self.assertEqual(cp.extract_verified_zip(archive, reserve_bytes=0), root)
        self.assertEqual(json.loads((archive.parent / "extract.checkpoint.json").read_text())
                         ["status"], "CRC_CHECKED_FROM_SHA256_VERIFIED_ARTIFACT")

    def test_zip_traversal_and_untrusted_extensions_rejected(self):
        for filename in ("../escape.json", "/absolute.json", "assets/thing/virus.exe"):
            with self.subTest(filename=filename):
                payload = zipped({filename: b"bad"})
                archive = self.root / "verified.zip"
                archive.write_bytes(payload)
                with self.assertRaises(cp.CheckpointError):
                    cp.extract_verified_zip(archive, reserve_bytes=0)

    def test_wrong_archive_digest_must_not_promote(self):
        invalid = {**self.entry, "digest": "sha256:" + "0" * 64}
        with self.assertRaisesRegex(cp.CheckpointError, "FINAL_SHA256_MISMATCH"):
            self.download(self.fetcher, invalid)
        self.assertFalse((self.root / "artifact_111" / "verified.zip").exists())

    def test_forged_or_changed_manifest_does_not_reuse_untrusted_chunks(self):
        def fail_after_first(start, end, total):
            if start:
                raise TimeoutError("loss")
            return self.fetcher(start, end, total)
        with self.assertRaises(cp.CheckpointError):
            self.download(fail_after_first)
        altered = {**self.entry, "name": "new-artifact-name"}
        with self.assertRaisesRegex(cp.CheckpointError, "IDENTITY_DRIFT"):
            self.download(self.fetcher, altered)

    def test_fail_safe_disk_reserve(self):
        with self.assertRaisesRegex(cp.CheckpointError, "WAREHOUSE_6GIB_RESERVE_BLOCK"):
            cp.download_chunks(self.root, self.entry, self.fetcher, chunk_size=1024,
                               reserve_bytes=2**60)


if __name__ == "__main__":
    unittest.main()
