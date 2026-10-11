#!/usr/bin/env python3
"""Reject incomplete source-only PBR/FBX packs before any Unreal import attempt."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

from materials import REGION_PLAN, REGION_FAMILIES, SURFACES, sha256, validate_canon_map

REQUIRED_MESHES = {"RoundDoor", "PicketFence", "PartyTable", "GardenCart",
                   "RoundWindow", "GardenHedge", "OakTree", "StorageBarrel",
                   "FarmGate", "GardenPlanter",
                   "BagEndFrontWall", "RoundRoomWallArc", "RoundRoomFloor", "Hearth", "Bookcase", "HobbitBed", "WoodenFootbridge", "MillWheel", "PartyCanopy", "StonePath", "LanternPost", "VillageWell"}


def validate(out: Path, require_meshes: bool = True):
    out = out.resolve()
    material_receipt = json.loads((out / "materials_receipt.json").read_text(encoding="utf-8"))
    assert material_receipt["runtime_imported"] is False
    assert material_receipt["region_packet_sha256"] == sha256(REGION_PLAN)
    assert material_receipt["material_families"] == 12
    assert material_receipt["physical_textures"] == 36
    assert len(material_receipt["region_bindings"]) == 28
    assert {r["id"] for r in material_receipt["region_bindings"]} == set(validate_canon_map())
    assert all(set(r["support_surfaces"]) <= set(SURFACES) for r in material_receipt["region_bindings"])
    assert {t["family"] for t in material_receipt["textures"]} == set(SURFACES)
    assert {t["type"] for t in material_receipt["textures"]} == {"BaseColor", "NormalDX", "ORM"}
    assert len({t["path"] for t in material_receipt["textures"]}) == 36

    for item in material_receipt["textures"]:
        path = (out / item["path"]).resolve()
        assert path.is_relative_to(out), "Unsafe path"
        assert path.is_file() and sha256(path) == item["sha256"]
        assert path.stat().st_size == item["bytes"]
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            assert im.format == "PNG" and im.mode == "RGB"
            assert list(im.size) == item["dimensions"]
            # A direct metallic channel check keeps all 12 support surfaces nonmetal.
            if item["type"] == "ORM":
                assert im.getchannel("B").getextrema() == (0, 0)
                assert item["color_space"] == "linear"
            if item["type"] == "BaseColor":
                assert item["color_space"] == "sRGB"
            if item["type"] == "NormalDX":
                assert item["color_space"] == "linear"

    if require_meshes:
        mesh_receipt = json.loads((out / "fbx_receipt.json").read_text(encoding="utf-8"))
        assert mesh_receipt["runtime_imported"] is False and mesh_receipt["skeletal_or_animated"] is False
        objects = mesh_receipt["objects"]
        assert len(objects) == 2 * len(REQUIRED_MESHES) and mesh_receipt["asset_count"] == len(REQUIRED_MESHES)
        assert {x["asset"] for x in objects} == REQUIRED_MESHES
        assert {(x["asset"], x["lod"]) for x in objects} == {
            (asset, lod) for asset in REQUIRED_MESHES for lod in (0, 1)}
        for x in objects:
            path = (out / x["path"]).resolve()
            assert path.is_relative_to(out) and path.is_file()
            assert x["sha256"] == sha256(path) and x["bytes"] == path.stat().st_size
            assert path.open("rb").read(22).startswith(b"Kaydara FBX Binary")
            assert 0 < x["reimport_polygons"] <= 15000
            assert x["reimport_uv_layers"] >= 1
            assert x["collider_count"] >= 1
            assert len(x["ucx_boxes"]) == x["collider_count"]
            assert all(all(float(d) > 0 for d in box["dimensions_m"])
                       for box in x["ucx_boxes"])
            if x["asset"] == "BagEndFrontWall":
                # The hero doorway must remain physically open at walking height.
                # Do not certify Unreal collision from this source-space guard.
                lower_obstacles = [
                    b for b in x["ucx_boxes"]
                    if b["center_m"][2] - b["dimensions_m"][2] / 2 < 2.05
                    and b["center_m"][2] + b["dimensions_m"][2] / 2 > 0.1
                ]
                assert all(abs(b["center_m"][0]) - b["dimensions_m"][0]/2 > 1.05
                           for b in lower_obstacles)
            if x["asset"] == "PartyCanopy":
                assert len(x["ucx_boxes"]) == 4
                assert all(abs(b["center_m"][0]) > 1.8
                           for b in x["ucx_boxes"])
            assert 1 <= x["material_slots"] <= 6
        print(f"CLOUD_ASSET_STATIC_VALIDATION_PASS materials=12 textures=36 region_bindings=28 binary_fbx={len(objects)}")
    else:
        print("CLOUD_MATERIAL_STATIC_VALIDATION_PASS materials=12 textures=36 region_bindings=28")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--materials-only", action="store_true")
    args = parser.parse_args()
    validate(args.out, require_meshes=not args.materials_only)
