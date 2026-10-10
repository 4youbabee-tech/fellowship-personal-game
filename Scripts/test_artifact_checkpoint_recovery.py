#!/usr/bin/env python3
"""Network-free, sandbox-only regression tests for pinned Artifact recovery."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock
import zipfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("checkpoint", HERE / "resume_p1c01_artifact_checkpoint.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class CheckpointRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.payload = bytes(range(251)) * 19
        self.entry = dict(
            artifact_id=701, source_run_id=77, name="offline-fixture",
            digest="sha256:" + hashlib.sha256(self.payload).hexdigest(),
            size_bytes=len(self.payload))
        self.calls = []

    def cache(self):
        p = self.root / "artifact_701"
        p.mkdir(exist_ok=True)
        return p

    def fetch(self, start, end, total):
        self.calls.append((start, end))
        self.assertEqual(total, len(self.payload))
        return self.payload[start:end + 1]

    def go(self, fetch=None, entry=None, reserve_bytes=0):
        with contextlib.redirect_stdout(io.StringIO()):
            return m.download_chunks(self.root, entry or self.entry,
                                     fetch or self.fetch, chunk_size=1024,
                                     reserve_bytes=reserve_bytes, sleep_fn=lambda _x: None)

    def test_full_archive_reuse_without_network(self):
        result = self.go()
        self.assertEqual(result.read_bytes(), self.payload)
        self.calls.clear()
        self.assertEqual(self.go(), result)
        self.assertEqual(self.calls, [])

    def test_power_or_network_loss_resumes_without_first_chunks(self):
        def interrupted(start, end, total):
            if start >= 2048:
                raise TimeoutError("injected disconnect")
            return self.fetch(start, end, total)
        with self.assertRaisesRegex(m.CheckpointError, "RANGE_RETRIES_EXHAUSTED"):
            self.go(interrupted)
        self.assertEqual((self.cache() / "download.part").read_bytes(), self.payload[:2048])
        self.calls.clear()
        self.assertEqual(self.go().read_bytes(), self.payload)
        self.assertEqual(self.calls[0][0], 2048)

    def test_uncommitted_tail_is_retried(self):
        c = self.cache()
        (c / "download.part").write_bytes(self.payload[:1024] + b"uncommitted-tail")
        journal = m.checkpoint_identity(self.entry, 1024)
        journal["completed_chunks"] = [hashlib.sha256(self.payload[:1024]).hexdigest()]
        m.atomic_json(c / "download.checkpoint.json", journal)
        self.go()
        self.assertEqual(self.calls[0][0], 1024)

    def test_crash_between_empty_journal_and_open_part(self):
        c = self.cache()
        m.atomic_json(c / "download.checkpoint.json", m.checkpoint_identity(self.entry, 1024))
        self.assertEqual(self.go().read_bytes(), self.payload)

    def test_too_short_responses_never_persist(self):
        with self.assertRaisesRegex(m.CheckpointError, "RANGE_RETRIES_EXHAUSTED"):
            self.go(lambda *_: b"bad")
        self.assertEqual((self.cache() / "download.part").stat().st_size, 0)
        journal = json.loads((self.cache() / "download.checkpoint.json").read_text())
        self.assertEqual(journal["completed_chunks"], [])

    def test_short_then_network_exception_does_not_persist_short_response(self):
        n = [0]
        def bad(*_):
            n[0] += 1
            if n[0] == 1:
                return b"bad"
            raise TimeoutError("disconnected")
        with self.assertRaisesRegex(m.CheckpointError, "RANGE_RETRIES_EXHAUSTED"):
            self.go(bad)
        self.assertEqual((self.cache() / "download.part").stat().st_size, 0)

    def test_corrupt_durable_chunk_fails_closed(self):
        c = self.cache()
        bad = b"X" * 1024
        (c / "download.part").write_bytes(bad)
        journal = m.checkpoint_identity(self.entry, 1024)
        journal["completed_chunks"] = [hashlib.sha256(self.payload[:1024]).hexdigest()]
        m.atomic_json(c / "download.checkpoint.json", journal)
        with self.assertRaisesRegex(m.CheckpointError, "CHUNK_HASH_MISMATCH"):
            self.go()
        self.assertEqual(self.calls, [])
        self.assertEqual((c / "download.part").read_bytes(), bad)

    def test_final_sha_mismatch_is_not_promoted(self):
        wrong = dict(self.entry, digest="sha256:" + "0" * 64)
        with self.assertRaisesRegex(m.CheckpointError, "FINAL_SHA256_MISMATCH"):
            self.go(entry=wrong)
        self.assertFalse((self.cache() / "verified.zip").exists())

    def test_preexisting_invalid_verified_archive_is_preserved_as_evidence(self):
        c = self.cache()
        (c / "verified.zip").write_bytes(b"invalid-archive")
        with self.assertRaisesRegex(m.CheckpointError, "EXISTING_ARCHIVE_HASH_MISMATCH"):
            self.go()
        self.assertEqual(self.calls, [])
        self.assertEqual((c / "verified.zip").read_bytes(), b"invalid-archive")

    def test_reserve_failure_before_network(self):
        with mock.patch.object(m.shutil, "disk_usage", return_value=SimpleNamespace(free=20)):
            with self.assertRaisesRegex(m.CheckpointError, "RESERVE_BLOCK"):
                self.go(reserve_bytes=100)
        self.assertEqual(self.calls, [])

    def test_second_writer_is_rejected_before_network(self):
        attempted = [False]
        def nested(start, end, total):
            if not attempted[0]:
                attempted[0] = True
                inner_calls = []
                with self.assertRaisesRegex(m.CheckpointError, "WRITER_LOCKED"):
                    self.go(lambda *args: inner_calls.append(args) or b"")
                self.assertEqual(inner_calls, [])
            return self.fetch(start, end, total)
        self.assertEqual(self.go(nested).read_bytes(), self.payload)

    def test_lock_is_released_after_failure(self):
        with self.assertRaises(m.CheckpointError):
            self.go(lambda *_: (_ for _ in ()).throw(TimeoutError("down")))
        self.assertEqual(self.go().read_bytes(), self.payload)

    def test_invalid_checkpoint_json_fails_closed(self):
        c = self.cache()
        (c / "download.checkpoint.json").write_text("[]")
        with self.assertRaisesRegex(m.CheckpointError, "CHECKPOINT_CORRUPT"):
            self.go()

    def test_extra_journal_entries_fails_closed(self):
        c = self.cache()
        journal = m.checkpoint_identity(self.entry, 1024)
        journal["completed_chunks"] = ["0" * 64] * 100
        m.atomic_json(c / "download.checkpoint.json", journal)
        with self.assertRaisesRegex(m.CheckpointError, "CHUNK_JOURNAL_MALFORMED"):
            self.go()

    def archive(self, members):
        archive = self.cache() / "verified.zip"
        with zipfile.ZipFile(archive, "w") as zipped:
            for name, data in members:
                zipped.writestr(name, data)
        return archive

    def test_zip_extract_reuse(self):
        a = self.archive([("model.fbx", b"valid"), ("textures/albedo.png", b"PNG")])
        with contextlib.redirect_stdout(io.StringIO()):
            dest = m.extract_verified_zip(a, reserve_bytes=0)
            modified = (dest / "model.fbx").stat().st_mtime_ns
            m.extract_verified_zip(a, reserve_bytes=0)
        self.assertEqual((dest / "model.fbx").stat().st_mtime_ns, modified)

    def test_zip_escape_rejected(self):
        a = self.archive([("../evil.fbx", b"bad")])
        with self.assertRaisesRegex(m.CheckpointError, "UNSAFE_PATH"):
            m.extract_verified_zip(a, reserve_bytes=0)
        self.assertFalse((self.root / "evil.fbx").exists())

    def test_zip_collision_rejected(self):
        a = self.archive([("Model.fbx", b"a"), ("model.fbx", b"b")])
        with self.assertRaisesRegex(m.CheckpointError, "DUPLICATE_CASEFOLD"):
            m.extract_verified_zip(a, reserve_bytes=0)

    def test_windows_device_and_normalized_paths_rejected(self):
        for name in ["CON.fbx", "aux/file.png", "LPT1.tga", "foo/./bar.fbx", "foo//bar.png", "foo/../bar.png", "bad?/a.png"]:
            with self.subTest(name=name):
                with self.assertRaises(m.CheckpointError):
                    m.secure_relative(name)

    def test_zip_partial_symlink_rejected(self):
        a = self.archive([("model.fbx", b"payload")])
        dest = a.parent / "extracted"
        dest.mkdir()
        outside = self.root / "outside.bin"
        outside.write_bytes(b"safe")
        try:
            (dest / "model.fbx.partial").symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation unavailable")
        with self.assertRaisesRegex(m.CheckpointError, "TEMP_SYMLINK"):
            m.extract_verified_zip(a, reserve_bytes=0)
        self.assertEqual(outside.read_bytes(), b"safe")

    def test_invalid_manifest_fields_rejected(self):
        for key, value in [("artifact_id", True), ("size_bytes", True), ("source_run_id", -1), ("digest", None)]:
            with self.subTest(field=key):
                with self.assertRaises(m.CheckpointError):
                    m.validate_entry(dict(self.entry, **{key: value}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
