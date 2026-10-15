#!/usr/bin/env python3
"""Restore persisted Cloud138 UE packages by SHA256 before bounded startup observation."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile

SOURCE = "1e1e5c9df5aeee75e130eed7891fdfb7b129c9fc"
BRIDGE = "/Game/Production/World/Shire/Cloud138/SM_ShWoodenFootbridge"
# Cloud138 source warehouse includes one *historical* dependency package.
# It must NEVER override the current project's authoritative UE4-built master.
CURRENT_MASTER = "/Game/Production/Materials/M_P1C01VerifiedPBR"
CURRENT_MASTER_REL = "Content/Production/Materials/M_P1C01VerifiedPBR.uasset"

def hash_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def restore(warehouse, checkout):
    checkout = Path(checkout).resolve()
    source = Path(warehouse).resolve() / "_unreal_cloud138" / SOURCE
    report = json.loads((source / "unreal_receipt.json").read_text(encoding="utf-8"))
    assert report["source_commit"] == SOURCE
    assert report["stage"] == "UE4_IMPORTED_REOPENED_PERSISTED_NOT_WORLD_PLACED"
    assert report["new_uassets"] == 89 and report["dependent_parent_uassets"] == 1
    assert report["world_placed"] is False
    assert report["nav_quarantined_assets"] in ([], [BRIDGE])
    rows = report["files"]
    assert len(rows) == 90 and len(set(r["relative"] for r in rows)) == 90
    verified = []
    for row in rows:
        rel = row["relative"]
        parts = PurePosixPath(rel)
        assert rel.startswith("Content/Production/") and rel.endswith(".uasset")
        assert parts.as_posix() == rel and all(p not in (".", "..") for p in parts.parts)
        assert row["game_asset"] == "/Game/" + rel[8:-7]
        assert re.fullmatch("[0-9a-f]{64}", row["sha256"])
        asset = source.joinpath(*parts.parts)
        assert asset.is_file() and not asset.is_symlink() and asset.stat().st_size == row["bytes"]
        assert hash_file(asset) == row["sha256"], "CLOUD138_SOURCE_HASH_MISMATCH:" + rel
        target = checkout.joinpath(*parts.parts)
        assert target.resolve().is_relative_to(checkout), "CLOUD138_ESCAPE"
        verified.append((asset, target, row))
    assert sum(r["bytes"] for _,_,r in verified) == report["payload_bytes"]
    masters = [(asset, target, row) for asset, target, row in verified
               if row["relative"] == CURRENT_MASTER_REL]
    assert len(masters) == 1, "CLOUD138_CURRENT_PBR_PARENT_IDENTITY_MISSING"
    old_master, current_master, master_row = masters[0]
    assert master_row["game_asset"] == CURRENT_MASTER, "CLOUD138_PARENT_PATH_DRIFT"
    assert current_master.is_file() and not current_master.is_symlink(), (
        "CLOUD138_CURRENT_PBR_MASTER_NOT_PRODUCED_BY_ENGINE_IMPORT")
    assert current_master.stat().st_size > 2048, "CLOUD138_CURRENT_PBR_MASTER_EMPTY"
    current_master_sha = hash_file(current_master)
    # Fail closed for a stale copy as well as a missing copy. The old version
    # is known to lack the PBR masks sampler/instanced shader permutation.
    assert current_master_sha != master_row["sha256"], (
        "CLOUD138_STALE_PARENT_MUST_NOT_BE_REUSED")
    # Validate all 90 archive payloads above, but restore ONLY 89 Cloud138-
    # owned packages. Editor-imported current material is a dependency, not
    # a Cloud138-owned asset: never overwrite it with source-archive history.
    for asset, target, row in verified:
        if row["relative"] == CURRENT_MASTER_REL:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_file() and target.stat().st_size == row["bytes"] and hash_file(target) == row["sha256"]:
            continue
        fd, name = tempfile.mkstemp(dir=target.parent, prefix=".cloud138_")
        try:
            with os.fdopen(fd, "wb") as dst, open(asset, "rb") as src:
                shutil.copyfileobj(src, dst)
            assert hash_file(name) == row["sha256"]
            os.replace(name, target)
        finally:
            if os.path.exists(name):
                os.unlink(name)
    for _, target, row in verified:
        if row["relative"] == CURRENT_MASTER_REL:
            assert target.is_file() and hash_file(target) == current_master_sha, (
                "CLOUD138_CURRENT_PBR_PARENT_OVERWRITTEN")
        else:
            assert target.stat().st_size == row["bytes"] and hash_file(target) == row["sha256"]
    receipt = checkout / "Saved/Cloud138Unreal/restored.json"
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps({
        "packages":90, "restored_cloud138_packages":89,
        "preserved_current_pbr_parent_packages":1,
        "current_pbr_parent":CURRENT_MASTER,
        "current_pbr_parent_sha256":current_master_sha,
        "verified_archive_bytes":report["payload_bytes"],
        "source_commit":SOURCE,"world_placed":False,"pie_tested":False
    },sort_keys=True)+"\n",encoding="utf-8")
    print("CLOUD138_UE_RESTORED_SHA256_PASS files=90 restored=89 preserved_current_pbr_parent=1 bytes=%d world_placed=unproven" % report["payload_bytes"])
    return 90

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--warehouse",required=True)
    p.add_argument("--checkout",required=True)
    a=p.parse_args()
    restore(a.warehouse,a.checkout)
