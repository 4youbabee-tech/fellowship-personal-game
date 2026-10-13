#!/usr/bin/env python3
"""Static validation for generated P1C01 source WAV audio."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import wave
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "Data" / "P1C01AudioSourceBatch01Manifest.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_wav(path: Path, record: dict) -> None:
    require(path.read_bytes().startswith(b"RIFF"), f"missing RIFF header: {path}")
    with wave.open(str(path), "rb") as wav:
        require(wav.getnchannels() == 1, f"not mono: {path}")
        require(wav.getsampwidth() == 2, f"not 16-bit pcm: {path}")
        require(wav.getframerate() == 22050, f"unexpected sample rate: {path}")
        require(wav.getnframes() == record["frames"], f"frame mismatch: {path}")
        duration = wav.getnframes() / wav.getframerate()
        require(0.45 <= duration <= 3.1, f"duration out of range: {path}")
    require(path.stat().st_size > 10000, f"wav too small: {path}")


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    records = manifest["records"]
    archive = ROOT / manifest["archive"]
    require(archive.exists(), f"missing archive: {archive}")
    require(sha256(archive) == manifest["archive_sha256"], "archive sha mismatch")
    require(manifest["runner_policy"] == "Windows Runner not used or required for this batch", "runner policy mismatch")
    require(manifest["counts"]["generated_wav"] == len(records), "generated_wav count mismatch")
    require(len(records) == 32, "audio batch01 must contain 32 wav assets")

    temp_root = Path(tempfile.mkdtemp(prefix="p1c01_audio_batch01_validate_"))
    with zipfile.ZipFile(archive) as zipped:
        names = zipped.namelist()
        require(len([name for name in names if name.lower().endswith(".wav")]) == 32, "archive wav count mismatch")
        zipped.extractall(temp_root)

    seen_assets = set()
    seen_hashes = set()
    categories = set()
    zones = set()
    total_frames = 0
    for record in records:
        wav_path = temp_root / record["archive_member"]
        require(wav_path.exists(), f"missing wav: {wav_path}")
        require(record["asset_name"] not in seen_assets, f"duplicate asset: {record['asset_name']}")
        seen_assets.add(record["asset_name"])
        categories.add(record["category"])
        zones.add(record["target_zone"])
        validate_wav(wav_path, record)
        require(sha256(wav_path) == record["sha256"], f"wav sha mismatch: {wav_path}")
        require(record["sha256"] not in seen_hashes, f"duplicate wav content hash: {wav_path}")
        seen_hashes.add(record["sha256"])
        require(record["unreal_import_status"] == "PENDING", "must not claim UE import")
        require(record["sound_cue_status"] == "PENDING", "must not claim SoundCue setup")
        require(record["world_binding_status"] == "PENDING", "must not claim world binding")
        total_frames += record["frames"]

    require(categories >= {"ambience", "foley", "footstep", "object", "nature"}, f"missing category coverage: {sorted(categories)}")
    require(len(zones) >= 7, f"too few audio zones: {sorted(zones)}")
    print(
        "P1C01_AUDIO_SOURCE_BATCH01_STATIC_PASS "
        f"wav={len(records)} categories={len(categories)} zones={len(zones)} frames={total_frames}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"P1C01_AUDIO_SOURCE_BATCH01_STATIC_FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)
