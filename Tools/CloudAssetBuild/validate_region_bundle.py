#!/usr/bin/env python3
"""Fail-closed physical/receipt checks for the 28-region support source kit."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path


def verify(output: Path) -> None:
    output = output.resolve()
    plan = Path(__file__).resolve().parents[2] / "Data/WholeGameRegionProductionPacketsV1.json"
    regions = {x["region_id"] for x in json.loads(plan.read_text(encoding="utf-8"))["packets"]}
    assert len(regions) == 28
    receipt = json.loads((output / "regional_fbx_receipt.json").read_text(encoding="utf-8"))
    assert receipt["region_count"] == 28 and receipt["fbx_count"] == 56
    assert receipt["region_packet_sha256"] == hashlib.sha256(plan.read_bytes()).hexdigest()
    assert receipt["provenance"] == "ORIGINAL_PROJECT_PROCEDURAL"
    assert receipt["unreal_imported"] is False and receipt["warehouse_persisted"] is False
    items = receipt["objects"]
    assert len(items) == 56
    assert len({x["path"] for x in items}) == 56
    assert {(x["region_id"], x["lod"]) for x in items} == {
        (r, lod) for r in regions for lod in (0, 1)}
    assert len(list((output / "regional_meshes").glob("*.fbx"))) == 56
    for item in items:
        path = (output / item["path"]).resolve()
        assert path.is_relative_to(output) and path.is_file()
        assert path.stat().st_size > 1024 and path.stat().st_size == item["bytes"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]
        with path.open("rb") as stream:
            h = stream.read(27)
        assert h.startswith(b"Kaydara FBX Binary")
        assert int.from_bytes(h[23:27], "little") == 7400
        assert item["format"] == "FBX_BINARY_7400"
        assert 0 < item["reimport_polygons"] <= 12000
        assert item["uv_layers"] >= 1 and item["collider_count"] >= 1
        assert item["unreal_imported"] is False and item["visual_accepted"] is False
    print("WHOLEGAME_ORIGINAL_REGION_FBX_QC_PASS regions=28 fbx=56")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    verify(ap.parse_args().out)
