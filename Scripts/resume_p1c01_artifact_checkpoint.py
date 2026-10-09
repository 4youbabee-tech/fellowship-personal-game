#!/usr/bin/env python3
"""Power-loss-resumable, digest-pinned GitHub Artifact staging for P1C01.

Stores verified 4 MiB transfer checkpoints on the *persistent* warehouse disk.
Never deletes or redownloads valid chunks, touches Unreal, or changes the
persistent source inventory. The separate single-writer promotes source assets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import struct
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
import zlib

CHUNK_BYTES = 4 * 1024 * 1024
DISK_RESERVE = 6 * 1024 ** 3
MAX_ENTRY_BYTES = 80 * 1024 ** 2
MAX_EXPANDED_BYTES = 2 * 1024 ** 3
MAX_ENTRY_COUNT = 1500
SUFFIXES = {".json", ".fbx", ".png", ".tga", ".jpg", ".jpeg", ".exr", ".webp"}
DIGEST = re.compile(r"sha256:[0-9a-f]{64}\Z")
RANGE = re.compile(r"bytes (\d+)-(\d+)/(\d+)\Z")
USER_AGENT = "ShireJourney-ResumableCC0/1.0"


class CheckpointError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, document: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".writing")
    with tmp.open("w", encoding="utf-8") as out:
        json.dump(document, out, indent=2, sort_keys=True)
        out.write("\n")
        out.flush()
        os.fsync(out.fileno())
    os.replace(tmp, path)


def secure_relative(raw: str) -> Path:
    if not isinstance(raw, str) or not raw or len(raw) > 245 or "\\" in raw or ":" in raw or "\x00" in raw:
        raise CheckpointError("ARTIFACT_UNSAFE_PATH")
    posix = PurePosixPath(raw)
    if posix.is_absolute() or any(p in (".", "..", "") for p in posix.parts):
        raise CheckpointError("ARTIFACT_UNSAFE_PATH")
    if any(p.endswith(".") or p.endswith(" ") for p in posix.parts):
        raise CheckpointError("ARTIFACT_WINDOWS_PATH_UNSAFE")
    if posix.suffix.lower() not in SUFFIXES:
        raise CheckpointError("ARTIFACT_UNAPPROVED_EXTENSION:" + raw)
    return Path(*posix.parts)


def validate_entry(entry: dict) -> None:
    if not isinstance(entry, dict):
        raise CheckpointError("INVALID_TRANSFER_MANIFEST")
    if (not isinstance(entry.get("artifact_id"), int) or entry["artifact_id"] <= 0
            or not isinstance(entry.get("size_bytes"), int) or entry["size_bytes"] <= 0
            or not isinstance(entry.get("name"), str) or not entry["name"]
            or not DIGEST.fullmatch(entry.get("digest", ""))
            or not isinstance(entry.get("source_run_id"), int)):
        raise CheckpointError("INVALID_PINNED_ARTIFACT_METADATA")


def check_free_space(directory: Path, additional_bytes: int, reserve_bytes: int) -> None:
    free = shutil.disk_usage(directory).free
    if free - additional_bytes < reserve_bytes:
        raise CheckpointError("WAREHOUSE_6GIB_RESERVE_BLOCK free=" + str(free)
                              + " need=" + str(additional_bytes + reserve_bytes))


def checkpoint_identity(entry: dict, chunk_size: int) -> dict:
    return {
        "artifact_id": entry["artifact_id"], "name": entry["name"],
        "digest": entry["digest"], "size_bytes": entry["size_bytes"],
        "chunk_size": chunk_size, "completed_chunks": [],
    }


def _check_chunk_journal(part: Path, journal_path: Path, entry: dict, chunk_size: int) -> dict:
    expected = checkpoint_identity(entry, chunk_size)
    if not journal_path.exists():
        if part.exists() and part.stat().st_size:
            raise CheckpointError("ARTIFACT_PART_WITHOUT_CHECKPOINT")
        return expected
    try:
        checkpoint = json.loads(journal_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise CheckpointError("ARTIFACT_CHECKPOINT_CORRUPT") from exc
    for key in ("artifact_id", "name", "digest", "size_bytes", "chunk_size"):
        if checkpoint.get(key) != expected[key]:
            raise CheckpointError("ARTIFACT_CHECKPOINT_IDENTITY_DRIFT:" + key)
    chunks = checkpoint.get("completed_chunks")
    if not isinstance(chunks, list) or not all(isinstance(x, str) and re.fullmatch("[0-9a-f]{64}", x) for x in chunks):
        raise CheckpointError("ARTIFACT_CHUNK_JOURNAL_MALFORMED")
    length = sum(min(chunk_size, entry["size_bytes"] - i * chunk_size)
                 for i in range(len(chunks)))
    if not part.exists() or part.stat().st_size < length:
        raise CheckpointError("ARTIFACT_CHECKPOINT_WITH_MISSING_BYTES")
    with part.open("rb+") as handle:
        for i, expected_sha in enumerate(chunks):
            byte_count = min(chunk_size, entry["size_bytes"] - i * chunk_size)
            if byte_count <= 0 or hashlib.sha256(handle.read(byte_count)).hexdigest() != expected_sha:
                raise CheckpointError("ARTIFACT_CHUNK_HASH_MISMATCH index=" + str(i))
        if part.stat().st_size > length:
            # Interruption after writing a chunk but before its journal was fsynced:
            # only the uncommitted tail is retried; all durable chunks are kept.
            handle.truncate(length)
            handle.flush()
            os.fsync(handle.fileno())
    return checkpoint


def download_chunks(cache_root: Path, entry: dict, fetch_range,
                    *, chunk_size: int = CHUNK_BYTES, reserve_bytes: int = DISK_RESERVE,
                    sleep_fn=time.sleep) -> Path:
    """fetch_range(start,end,total) returns EXACT bytes; dependency-injectable for offline tests."""
    validate_entry(entry)
    if chunk_size < 1024 or chunk_size > 16 * 1024 * 1024:
        raise CheckpointError("ARTIFACT_CHUNK_BUDGET_INVALID")
    cache = cache_root / ("artifact_" + str(entry["artifact_id"]))
    cache.mkdir(parents=True, exist_ok=True)
    archive = cache / "verified.zip"
    partial = cache / "download.part"
    journal_path = cache / "download.checkpoint.json"
    expected_sha = entry["digest"].split(":", 1)[1]
    if archive.exists():
        if archive.stat().st_size != entry["size_bytes"] or sha256(archive) != expected_sha:
            raise CheckpointError("ARTIFACT_EXISTING_ARCHIVE_HASH_MISMATCH")
        print("P1C01_ARTIFACT_REUSE_VERIFIED id=" + str(entry["artifact_id"])
              + " bytes=" + str(entry["size_bytes"]), flush=True)
        return archive

    check_free_space(cache, 0, reserve_bytes)
    journal = _check_chunk_journal(partial, journal_path, entry, chunk_size)
    completed = journal["completed_chunks"]
    offset = sum(min(chunk_size, entry["size_bytes"] - i * chunk_size)
                 for i in range(len(completed)))
    if not journal_path.exists():
        atomic_json(journal_path, journal)
    with partial.open("ab") as out:
        while offset < entry["size_bytes"]:
            count = min(chunk_size, entry["size_bytes"] - offset)
            check_free_space(cache, count, reserve_bytes)
            last_exc = None
            block = None
            for attempt in range(3):
                try:
                    block = fetch_range(offset, offset + count - 1, entry["size_bytes"])
                    if not isinstance(block, bytes) or len(block) != count:
                        raise CheckpointError("ARTIFACT_RANGE_LENGTH_MISMATCH")
                    break
                except (CheckpointError, TimeoutError, OSError, urllib.error.URLError) as exc:
                    last_exc = exc
                    if attempt < 2:
                        sleep_fn(min(2 ** attempt, 4))
            if block is None:
                raise CheckpointError("ARTIFACT_RANGE_RETRIES_EXHAUSTED offset="
                                      + str(offset) + " cause=" + str(last_exc))
            out.write(block)
            out.flush()
            os.fsync(out.fileno())
            completed.append(hashlib.sha256(block).hexdigest())
            atomic_json(journal_path, journal)
            offset += count
            print("P1C01_ARTIFACT_CHECKPOINT id=" + str(entry["artifact_id"])
                  + " committed=" + str(offset) + " total=" + str(entry["size_bytes"]), flush=True)
    if sha256(partial) != expected_sha:
        raise CheckpointError("ARTIFACT_FINAL_SHA256_MISMATCH_KEEP_CHECKPOINT")
    os.replace(partial, archive)
    print("P1C01_ARTIFACT_SHA256_PASS id=" + str(entry["artifact_id"])
          + " bytes=" + str(entry["size_bytes"]) + " cache=durable", flush=True)
    return archive


class _DoNotFollowRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def _headers(token: str) -> dict:
    return {"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28", "User-Agent": USER_AGENT}


def verify_remote(entry: dict, repository: str, token: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise CheckpointError("ARTIFACT_REPOSITORY_UNTRUSTED")
    url = "https://api.github.com/repos/" + repository + "/actions/artifacts/" + str(entry["artifact_id"])
    req = urllib.request.Request(url, headers=_headers(token))
    with urllib.request.urlopen(req, timeout=30) as response:
        remote = json.load(response)
    if (remote.get("id") != entry["artifact_id"] or remote.get("expired") is True
            or remote.get("name") != entry["name"] or remote.get("digest") != entry["digest"]
            or remote.get("size_in_bytes") != entry["size_bytes"]
            or remote.get("workflow_run", {}).get("id") != entry["source_run_id"]):
        raise CheckpointError("ARTIFACT_REMOTE_PROVENANCE_MISMATCH")


def _signed_download_url(repository: str, artifact_id: int, token: str) -> str:
    url = ("https://api.github.com/repos/" + repository
           + "/actions/artifacts/" + str(artifact_id) + "/zip")
    opener = urllib.request.build_opener(_DoNotFollowRedirect())
    try:
        with opener.open(urllib.request.Request(url, headers=_headers(token)), timeout=30) as response:
            raise CheckpointError("ARTIFACT_EXPECTED_REDIRECT_NOT_RECEIVED")
    except urllib.error.HTTPError as exc:
        if exc.code not in (302, 303, 307, 308):
            raise CheckpointError("ARTIFACT_API_DOWNLOAD_HTTP_" + str(exc.code)) from exc
        location = exc.headers.get("Location", "")
    parsed = urllib.parse.urlparse(location)
    if (parsed.scheme != "https" or parsed.username or parsed.password or parsed.fragment
            or not parsed.hostname or not (
                parsed.hostname.endswith(".blob.core.windows.net")
                or parsed.hostname.endswith(".actions.githubusercontent.com")
                or parsed.hostname == "objects.githubusercontent.com")):
        raise CheckpointError("ARTIFACT_REDIRECT_HOST_UNTRUSTED")
    return location


def _remote_range(repository: str, entry: dict, token: str, start: int, end: int, total: int) -> bytes:
    # Signed links expire. Fetch a new one per bounded chunk; NEVER leak token to Azure.
    url = _signed_download_url(repository, entry["artifact_id"], token)
    request = urllib.request.Request(url, headers={"Range": "bytes=" + str(start) + "-" + str(end),
                                                    "User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=130) as response:
        if response.status != 206:
            raise CheckpointError("ARTIFACT_RANGE_NOT_SUPPORTED http=" + str(response.status))
        match = RANGE.fullmatch(response.headers.get("Content-Range", ""))
        if not match or tuple(int(x) for x in match.groups()) != (start, end, total):
            raise CheckpointError("ARTIFACT_CONTENT_RANGE_MISMATCH")
        data = response.read(end - start + 2)
        if len(data) != end - start + 1 or response.read(1):
            raise CheckpointError("ARTIFACT_TRUNCATED_OR_OVERSIZE_CHUNK")
        return data


def _entry_map(archive: zipfile.ZipFile) -> list:
    entries, seen, expanded = [], set(), 0
    for info in archive.infolist():
        if info.is_dir():
            continue
        if len(entries) >= MAX_ENTRY_COUNT or info.flag_bits & 1:
            raise CheckpointError("ARTIFACT_ZIP_ENTRY_BUDGET_OR_ENCRYPTION")
        rel = secure_relative(info.filename)
        key = str(rel).casefold()
        if key in seen:
            raise CheckpointError("ARTIFACT_DUPLICATE_CASEFOLD_NAME")
        seen.add(key)
        mode = (info.external_attr >> 16)
        if stat.S_IFMT(mode) == stat.S_IFLNK:
            raise CheckpointError("ARTIFACT_SYMLINK_FORBIDDEN")
        if info.file_size > MAX_ENTRY_BYTES:
            raise CheckpointError("ARTIFACT_OVERSIZE_UNCOMPRESSED_FILE")
        expanded += info.file_size
        if expanded > MAX_EXPANDED_BYTES:
            raise CheckpointError("ARTIFACT_ZIP_UNCOMPRESSED_BUDGET")
        entries.append((info, rel))
    if not entries:
        raise CheckpointError("ARTIFACT_ZIP_EMPTY")
    return entries


def _crc_existing(path: Path, expected_size: int, crc32_expected: int) -> bool:
    if not path.is_file() or path.is_symlink() or path.stat().st_size != expected_size:
        return False
    crc = 0
    with path.open("rb") as inp:
        for chunk in iter(lambda: inp.read(1024 * 1024), b""):
            crc = zlib.crc32(chunk, crc)
    return (crc & 0xffffffff) == crc32_expected


def extract_verified_zip(archive: Path, *, reserve_bytes: int = DISK_RESERVE) -> Path:
    # Archive SHA256 has already been matched against pinned GitHub metadata.
    if archive.name != "verified.zip":
        raise CheckpointError("ARTIFACT_ZIP_NOT_PINNED_VERIFIED")
    parent = archive.parent
    dest = parent / "extracted"
    dest.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive) as zipped:
        entries = _entry_map(zipped)
        for info, relative in entries:
            target = dest / relative
            if target.is_symlink() or any(p.is_symlink() for p in target.parents if p != dest.parent):
                raise CheckpointError("ARTIFACT_EXTRACT_SYMLINK_FORBIDDEN")
            if _crc_existing(target, info.file_size, info.CRC):
                continue
            check_free_space(parent, info.file_size, reserve_bytes)
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp = target.with_name(target.name + ".partial")
            crc, count = 0, 0
            try:
                with zipped.open(info) as src, tmp.open("wb") as out:
                    while True:
                        block = src.read(1024 * 1024)
                        if not block:
                            break
                        count += len(block)
                        if count > info.file_size:
                            raise CheckpointError("ARTIFACT_UNZIP_OVERRUN")
                        crc = zlib.crc32(block, crc)
                        out.write(block)
                    out.flush()
                    os.fsync(out.fileno())
                if count != info.file_size or crc & 0xffffffff != info.CRC:
                    raise CheckpointError("ARTIFACT_UNZIP_CRC_MISMATCH")
                os.replace(tmp, target)
            finally:
                if tmp.exists():
                    tmp.unlink()
        # Confirm the complete extracted set equals the pinned archive entries.
        expected = {str(rel).replace("\\", "/") for _, rel in entries}
        actual = {x.relative_to(dest).as_posix() for x in dest.rglob("*") if x.is_file()}
        if actual != expected:
            raise CheckpointError("ARTIFACT_EXTRACTED_SET_MISMATCH")
        atomic_json(parent / "extract.checkpoint.json", {
            "archive_sha256": sha256(archive),
            "files": len(entries), "expanded_bytes": sum(i.file_size for i, _ in entries),
            "status": "CRC_CHECKED_FROM_SHA256_VERIFIED_ARTIFACT",
        })
    print("P1C01_ARTIFACT_EXTRACT_PASS cache=" + str(parent)
          + " files=" + str(len(entries)), flush=True)
    return dest


def cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--key", required=True)
    ap.add_argument("--warehouse-root", required=True, type=Path)
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", ""))
    args = ap.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("status") != "PINNED_IMMUTABLE_SOURCE_ONLY":
        raise CheckpointError("ARTIFACT_MANIFEST_STATUS_INVALID")
    entry = manifest.get("artifacts", {}).get(args.key)
    validate_entry(entry)
    token = os.environ.get("GH_TOKEN", "")
    if not token:
        raise CheckpointError("GITHUB_ACTIONS_READ_TOKEN_MISSING")
    cache_root = args.warehouse_root / "_p1c01_transfer_checkpoints"
    cache_root.mkdir(parents=True, exist_ok=True)
    archive = cache_root / ("artifact_" + str(entry["artifact_id"])) / "verified.zip"
    if not archive.is_file():
        verify_remote(entry, args.repo, token)
    def fetch(start: int, end: int, total: int) -> bytes:
        return _remote_range(args.repo, entry, token, start, end, total)
    result = download_chunks(cache_root, entry, fetch)
    expanded = extract_verified_zip(result)
    print("P1C01_DURABLE_CHECKPOINT_READY key=" + args.key
          + " stage=EXTRACTED_SOURCE_ONLY root=" + str(expanded)
          + " no_unreal_import=true", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
