#!/usr/bin/env python3
"""Generate original P1C01 source WAV audio for off-runner production."""

from __future__ import annotations

import hashlib
import json
import math
import random
import shutil
import struct
import tempfile
import wave
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SourceAssets" / "Production" / "Audio" / "Shire" / "Batch01OffRunner"
ARCHIVE = OUT / "P1C01_AudioBatch01_SourceAudio.zip"
MANIFEST = ROOT / "Data" / "P1C01AudioSourceBatch01Manifest.json"
SAMPLE_RATE = 22050


CLIPS = [
    ("A_P1C01_BagEnd_RoomTone_Morning_01", "ambience", "Bag End Interior", 2.4, 92, 0.22, "warm indoor room tone with low hearth air"),
    ("A_P1C01_BagEnd_Hearth_Crackles_01", "foley", "Bag End Interior", 1.7, 310, 0.38, "small hearth crackles for Bag End"),
    ("A_P1C01_BagEnd_Ceramic_Setdown_01", "object", "Bag End Interior", 0.9, 520, 0.34, "ceramic cup and pantry setdown"),
    ("A_P1C01_BagEnd_RoundDoor_Creak_01", "object", "Bag End", 1.2, 185, 0.42, "round wooden door creak source"),
    ("A_P1C01_BagEnd_Garden_Breeze_01", "ambience", "Bag End Garden", 2.6, 145, 0.26, "soft garden breeze through leaves"),
    ("A_P1C01_BagEnd_Garden_ToolTap_01", "foley", "Bag End Garden", 0.8, 640, 0.3, "small hand tool tap on wood"),
    ("A_P1C01_Hobbiton_Lane_Murmur_01", "ambience", "Hobbiton", 2.8, 118, 0.24, "distant village lane murmur without dialogue"),
    ("A_P1C01_Hobbiton_FenceLatch_01", "object", "Hobbiton", 0.7, 430, 0.36, "small fence latch click"),
    ("A_P1C01_Hobbiton_ClothLine_Flap_01", "foley", "Bagshot Row", 1.4, 255, 0.28, "laundry cloth flutter"),
    ("A_P1C01_Hobbiton_Broom_Sweep_01", "foley", "Bagshot Row", 1.1, 180, 0.31, "dry broom sweep on path"),
    ("A_P1C01_PartyField_Crowd_SoftLoop_01", "ambience", "Party Field", 2.9, 132, 0.25, "soft nonverbal party field bed"),
    ("A_P1C01_PartyField_CupClink_01", "object", "Party Field", 0.8, 760, 0.37, "small cup clink"),
    ("A_P1C01_PartyField_Bench_Shift_01", "object", "Party Field", 1.0, 210, 0.34, "wooden bench shift"),
    ("A_P1C01_PartyField_Ribbon_Flap_01", "foley", "Party Field", 1.3, 275, 0.27, "ribbon and bunting flap"),
    ("A_P1C01_Road_GrassStep_Light_01", "footstep", "Hobbiton Road", 0.55, 120, 0.3, "light grass footstep"),
    ("A_P1C01_Road_GrassStep_Light_02", "footstep", "Hobbiton Road", 0.58, 126, 0.31, "alternate light grass footstep"),
    ("A_P1C01_Road_DirtStep_Soft_01", "footstep", "Bywater Road", 0.52, 105, 0.32, "soft dirt footstep"),
    ("A_P1C01_Road_DirtStep_Soft_02", "footstep", "Bywater Road", 0.56, 111, 0.33, "alternate soft dirt footstep"),
    ("A_P1C01_WoodedRoad_Leaves_Rustle_01", "foley", "Wooded Road", 1.2, 165, 0.36, "leaf rustle by road edge"),
    ("A_P1C01_WoodedRoad_Branch_Snap_01", "foley", "Wooded Road", 0.7, 510, 0.4, "small twig snap"),
    ("A_P1C01_WoodedRoad_Bird_Chirp_01", "nature", "Wooded Road", 1.1, 1180, 0.28, "procedural distant bird chirp"),
    ("A_P1C01_WoodedRoad_Bird_Chirp_02", "nature", "Wooded Road", 1.0, 1320, 0.27, "alternate procedural distant bird chirp"),
    ("A_P1C01_MillPond_Water_Edge_01", "ambience", "Mill Pond", 2.7, 82, 0.3, "soft water edge loop"),
    ("A_P1C01_MillPond_Wheel_Creak_01", "object", "Mill Pond", 1.4, 155, 0.38, "slow wooden wheel creak"),
    ("A_P1C01_MillPond_Sack_Drop_01", "foley", "Mill Pond", 0.9, 145, 0.35, "flour sack drop"),
    ("A_P1C01_Bywater_Waystone_Tap_01", "object", "Bywater Road", 0.65, 390, 0.34, "small stone marker tap"),
    ("A_P1C01_Ferry_River_Lap_01", "ambience", "Bucklebury Ferry", 2.8, 76, 0.34, "river lap at ferry landing"),
    ("A_P1C01_Ferry_Rope_Coil_01", "foley", "Bucklebury Ferry", 1.0, 170, 0.36, "rope coil movement"),
    ("A_P1C01_Ferry_Dock_Plank_Creak_01", "object", "Bucklebury Ferry", 1.1, 135, 0.39, "dock plank creak"),
    ("A_P1C01_Ferry_Oar_WoodTap_01", "object", "Bucklebury Ferry", 0.75, 450, 0.33, "oar wooden tap"),
    ("A_P1C01_EastFields_FieldWind_01", "ambience", "East Fields", 2.6, 96, 0.29, "open field wind"),
    ("A_P1C01_EastFields_Crate_Shuffle_01", "foley", "East Fields", 0.9, 235, 0.35, "harvest crate shuffle"),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def envelope(t: float, duration: float) -> float:
    attack = min(0.04, duration * 0.15)
    release = min(0.18, duration * 0.25)
    if t < attack:
        return t / attack
    if t > duration - release:
        return max(0.0, (duration - t) / release)
    return 1.0


def synth_sample(kind: str, t: float, duration: float, freq: float, noise: float, rng: random.Random) -> float:
    env = envelope(t, duration)
    n = (rng.random() * 2.0 - 1.0) * noise
    low = math.sin(math.tau * freq * t)
    wobble = math.sin(math.tau * (freq * 0.49) * t + 0.7) * 0.35
    if kind == "footstep":
        thump = math.sin(math.tau * 88 * t) * math.exp(-t * 9.0)
        scrape = n * math.exp(-t * 4.5)
        return env * (thump * 0.55 + scrape * 0.45)
    if kind == "object":
        hit = math.sin(math.tau * freq * t) * math.exp(-t * 5.5)
        overtone = math.sin(math.tau * freq * 1.77 * t) * math.exp(-t * 6.8)
        return env * (hit * 0.45 + overtone * 0.22 + n * 0.26)
    if kind == "nature":
        chirp_freq = freq + math.sin(t * 18.0) * 80.0
        chirp = math.sin(math.tau * chirp_freq * t) * (0.5 + 0.5 * math.sin(math.tau * 5.5 * t))
        return env * (chirp * 0.42 + n * 0.08)
    if kind == "foley":
        return env * (low * 0.18 + wobble * 0.12 + n * 0.46)
    return env * (low * 0.12 + wobble * 0.16 + n * 0.32)


def write_wav(path: Path, name: str, kind: str, duration: float, freq: float, noise: float) -> dict[str, int | float]:
    rng = random.Random(hashlib.sha256(name.encode("utf-8")).hexdigest())
    frames = int(duration * SAMPLE_RATE)
    peak = 0
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        data = bytearray()
        for i in range(frames):
            t = i / SAMPLE_RATE
            sample = synth_sample(kind, t, duration, freq, noise, rng)
            value = max(-0.92, min(0.92, sample)) * 28000
            ivalue = int(value)
            peak = max(peak, abs(ivalue))
            data.extend(struct.pack("<h", ivalue))
        wav.writeframes(bytes(data))
    return {"frames": frames, "sample_rate": SAMPLE_RATE, "peak_abs": peak, "duration_seconds": round(frames / SAMPLE_RATE, 3)}


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)
    build_dir = Path(tempfile.mkdtemp(prefix="p1c01_audio_batch01_"))
    audio_dir = build_dir / "P1C01_AudioBatch01_SourceAudio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    records = []

    for index, (name, kind, zone, duration, freq, noise, description) in enumerate(CLIPS, 1):
        wav_path = audio_dir / f"{name}.wav"
        stats = write_wav(wav_path, name, kind, duration, freq, noise)
        records.append({
            "id": f"P1C01-AUD-B01-{index:03d}",
            "asset_name": name,
            "asset_type": "wav_pcm_mono",
            "category": kind,
            "target_zone": zone,
            "description": description,
            "source_license": "CC0-project-owned-procedural",
            "status": "SOURCE_GENERATED_STATIC_VALIDATION_PENDING",
            "archive_member": wav_path.relative_to(audio_dir).as_posix(),
            "sha256": sha256(wav_path),
            "sample_rate": stats["sample_rate"],
            "channels": 1,
            "bit_depth": 16,
            "frames": stats["frames"],
            "duration_seconds": stats["duration_seconds"],
            "peak_abs": stats["peak_abs"],
            "unreal_import_status": "PENDING",
            "sound_cue_status": "PENDING",
            "world_binding_status": "PENDING",
        })

    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(audio_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(audio_dir).as_posix())

    manifest = {
        "schema_version": 1,
        "batch_id": "P1C01_AUDIO_SOURCE_BATCH01_OFFRUNNER",
        "authority": "Data/ProjectGovernor.json",
        "production_scope": "P1C01 source audio generation outside Windows Runner",
        "runner_policy": "Windows Runner not used or required for this batch",
        "archive": ARCHIVE.relative_to(ROOT).as_posix(),
        "archive_sha256": sha256(ARCHIVE),
        "counts": {
            "generated_wav": len(records),
            "unique_audio_assets": len(records),
            "sample_rate": SAMPLE_RATE,
            "channels": 1,
            "bit_depth": 16,
        },
        "records": records,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    shutil.rmtree(build_dir)
    print(
        "P1C01_AUDIO_SOURCE_BATCH01_GENERATED "
        f"wav={len(records)} archive={ARCHIVE.relative_to(ROOT)} manifest={MANIFEST.relative_to(ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
