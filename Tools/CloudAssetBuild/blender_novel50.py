#!/usr/bin/env python3
"""Generate 50 NEW region-role families (100 FBX LODs) absent from wave140.

Uses the already-tested project original Blender primitives and exporters. This
is a SOURCE-ONLY candidate and never promises automatic UE import or appearance.
Each family is an ordered, fail-closed batch with an atomic progress receipt.
"""
import hashlib
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import blender_wave140 as wave

PLAN = ROOT / "Data/WholeGameRegionProductionPacketsV1.json"


def sequence():
    packets = json.loads(PLAN.read_text(encoding="utf-8"))["packets"]
    regions = [item["region_id"] for item in packets]
    if len(regions) != 28 or len(set(regions)) != 28:
        raise RuntimeError("INVALID_CANONICAL_REGION_PACKET_SET")
    old = [(region, wave.PART_NAMES[i % 5]) for i, region in enumerate(regions)]
    old += [(region, wave.PART_NAMES[(i + 1) % 5]) for i, region in enumerate(regions)]
    old += [(region, wave.PART_NAMES[(i + 2) % 5]) for i, region in enumerate(regions[:14])]
    previous = set(old)
    remaining = [(region, role) for region in regions for role in wave.PART_NAMES
                 if (region, role) not in previous]
    if len(previous) != 70 or len(remaining) != 70:
        raise RuntimeError("PREVIOUS_WAVE_IDENTITY_DRIFT")
    # Balanced: one new family in every canonical region, then 22 additional
    # region-specific families. Never relabel a previous geometry as new.
    selection = []
    for region in regions:
        selection.append(next(pair for pair in remaining if pair[0] == region))
    for pair in remaining:
        if pair not in selection and len(selection) < 50:
            selection.append(pair)
    if len(selection) != 50 or len(set(selection)) != 50 or previous.intersection(selection):
        raise RuntimeError("NOVEL_SELECTION_DRIFT")
    return selection


def atomic_json(destination, data):
    path = destination / "batch_progress.json"
    tmp = destination / "batch_progress.json.tmp"
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def main(destination):
    destination.mkdir(parents=True, exist_ok=True)
    batches = sequence()
    objects = []
    for i, (region, role) in enumerate(batches, 1):
        # Do not continue when either LOD creation/reimport fails.
        for lod in (0, 1):
            record = wave.export_one(region, role, lod, i + 140, destination)
            path = destination / record["path"]
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
                raise RuntimeError("BATCH_HASH_MISMATCH:" + str(i))
            objects.append(record)
        atomic_json(destination, {
            "status": "SOURCE_ONLY_IN_PROGRESS",
            "completed_batches": i, "total_batches": 50,
            "files_written": len(objects), "warehouse_persisted": False,
            "unreal_imported": False
        })
        print("NOVEL_REGION_BATCH_PASS batch=%02d/50 region=%s role=%s lods=2" % (i, region, role), flush=True)
    unique = {o["sha256"] for o in objects}
    if len(objects) != 100 or len(unique) != 100:
        raise RuntimeError("DUPLICATE_SOURCE_PAYLOADS")
    manifest = {
        "id": "NOVEL_50_REGION_BATCHES_20261013",
        "status": "BLENDER_REIMPORTED_SOURCE_ONLY",
        "baseline_source_fbx_owner_reported": 334,
        "prior_wave_families": 70, "new_batch_count": 50,
        "new_fbx_count": 100, "regions_covered": len({x["region_id"] for x in objects}),
        "source_generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "wave140_generator_sha256": hashlib.sha256(Path(wave.__file__).read_bytes()).hexdigest(),
        "region_plan_sha256": hashlib.sha256(PLAN.read_bytes()).hexdigest(),
        "objects": objects, "warehouse_persisted": False,
        "unreal_imported": False, "world_placed": False,
        "pie_tested": False, "device_tested": False, "visual_accepted": False
    }
    atomic_json(destination, manifest)
    (destination / "novel50_receipt.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("NOVEL_REGION_50_BATCH_SOURCE_PASS batches=50 fbx=100", flush=True)


if __name__ == "__main__":
    arguments = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(arguments) != 2 or arguments[0] != "--out":
        raise SystemExit("usage: blender -b --python blender_novel50.py -- --out DIR")
    main(Path(arguments[1]).resolve())
