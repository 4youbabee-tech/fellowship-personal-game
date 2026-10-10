#!/usr/bin/env python3
"""Hash-verified Poly Haven static PBR source bridge to existing UE4 importer.

No provider downloads; persistent warehouse is read-only. CLI does not claim UE,
PIE, target hardware, or human visual acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import sys

SLUG = re.compile(r"[a-z0-9_]{3,80}$")
MAGIC = b"Kaydara FBX Binary"
PNG = bytes.fromhex("89504e470d0a1a0a")
WAVES = (("p1c01_wave39", 39, 39), ("p1c01_wave60", 60, 59))
TAGS = {
  "village": ("barrel", "basket", "bench", "bucket", "crate", "wooden", "cart", "hay", "pot"),
  "road": ("stone", "rock", "log", "stump", "plank", "moss", "wood", "fence"),
  "garden": ("flower", "mushroom", "planter", "garden", "plant"),
}
LOCATIONS = {
  "village": ((2700, 2100, 0), (4700, -1900, 0), (6100, 2150, 0)),
  "road": ((9300, 2250, 0), (15900, -2400, 0), (19400, 1900, 0)),
  "garden": ((600, 1350, 0), (1400, -1650, 0), (5300, 2250, 0)),
}
ROOT = Path("World/Shire/VerifiedPBR")
MAX_FILES_BYTES = 144 * 1024 * 1024
MAX_MESH_BYTES = 16 * 1024 * 1024

class IntakeError(ValueError):
    pass

def ensure(ok, code):
    if not ok:
        raise IntakeError(code)

def digest(path):
    ensure(path.is_file() and not path.is_symlink(), "FILE_NOT_REGULAR:" + str(path))
    sha = hashlib.sha256()
    size = 0
    with path.open("rb") as fh:
        for data in iter(lambda: fh.read(1048576), b""):
            sha.update(data)
            size += len(data)
    return size, sha.hexdigest()

def doc(path):
    ensure(path.is_file() and not path.is_symlink(), "RECEIPT_MISSING:" + str(path))
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    ensure(isinstance(value, dict), "RECEIPT_INVALID")
    return value

def category(slug):
    parts = re.split("[-_]", slug)
    for name, words in TAGS.items():
        if any(part.startswith(word) for part in parts for word in words):
            return name
    return None

def select(warehouse, limit=16):
    ensure(1 <= limit <= 32, "ASSET_SELECTION_LIMIT_UNSAFE")
    candidates = []
    seen = set()
    for wave, expected, prepared in WAVES:
        base = warehouse / "_p1c01_adaptive_polyhaven" / wave
        ensure(base.is_dir() and not base.is_symlink(), "WAVE_NOT_PERSISTED:" + wave)
        receipt = doc(base / "receipt_adaptive_pbr.json")
        pbr = doc(base / "pbr_receipt_original.json")
        ensure(receipt.get("stage") == "PERSISTENT_WAREHOUSE_SOURCE_ONLY" and
               receipt.get("wave") == wave and receipt.get("license") == "CC0" and
               receipt.get("original_source_count") == expected and
               receipt.get("converted_fbx_count") == prepared and
               len(receipt.get("asset_ids", [])) == expected and
               pbr.get("prepared_assets") == prepared, "SOURCE_RECEIPT_DRIFT:" + wave)
        for name, field in (("source_receipt_original.json", "source_receipt_sha256"),
                            ("pbr_receipt_original.json", "pbr_receipt_sha256")):
            ensure(digest(base / name)[1] == receipt.get(field), "RECEIPT_HASH_DRIFT:" + wave)
        rows = {}
        for row in receipt.get("files", []):
            p = Path(str(row.get("file", "")))
            ensure(p.is_absolute() and p.resolve().is_relative_to(base.resolve()) and
                   row.get("provider") == "POLY_HAVEN" and row.get("license") == "CC0",
                   "SOURCE_PATH_OR_LICENSE_UNSAFE")
            rel = p.relative_to(base).as_posix()
            ensure(rel not in rows, "DUPLICATE_RECEIPT_PATH")
            rows[rel] = row
        held = set(receipt.get("quarantined_ids", []))
        for item in pbr.get("assets", []):
            slug = item.get("id")
            if not isinstance(slug, str) or not SLUG.fullmatch(slug) or slug in held:
                continue
            ensure(slug not in seen, "DUPLICATE_SOURCE_ID")
            seen.add(slug)
            kind = category(slug)
            if item.get("status") != "STATIC_SOURCE_QC_ONLY" or not kind:
                continue
            mesh = "assets/" + slug + "/prepared/" + slug + ".fbx"
            if mesh not in rows or rows[mesh].get("bytes", 0) > MAX_MESH_BYTES:
                continue
            maps = {}
            for itemmap in item.get("maps", []):
                match = re.fullmatch(r"TX_.*_(BaseColor|NormalDX|ORM|OpacityMask)\.png", Path(str(itemmap.get("path",""))).name)
                if not match or itemmap.get("resolution") != [1024,1024]:
                    maps = {}
                    break
                role = match.group(1)
                if role in maps:
                    maps = {}
                    break
                target = "assets/" + slug + "/prepared/" + Path(itemmap["path"]).name
                if target not in rows:
                    maps = {}
                    break
                maps[role] = target
            if set(maps) != {"BaseColor", "NormalDX", "ORM"}:
                continue
            selected = [mesh, *maps.values()]
            size = sum(rows[p]["bytes"] for p in selected)
            if size > MAX_FILES_BYTES:
                continue
            candidates.append((slug, kind, wave, base, mesh, maps, rows, size))
    candidates.sort(key=lambda x:(list(TAGS).index(x[1]), x[0]))
    chosen = []
    counts = {k:0 for k in TAGS}
    total = 0
    for c in candidates:
        if len(chosen) >= limit:
            break
        if counts[c[1]] >= 6 or total + c[-1] > MAX_FILES_BYTES:
            continue
        chosen.append(c)
        total += c[-1]
        counts[c[1]] += 1
    ensure(chosen, "NO_ELIGIBLE_STATIC_SHIRE_PBR_MODELS")
    return chosen

def safe_copy(base, key, receipt, dest, magic):
    original = base / key
    ensure(original.resolve().is_relative_to(base.resolve()) and not original.is_symlink(),
           "SOURCE_PATH_ESCAPED_WAREHOUSE")
    size, sha = digest(original)
    ensure(size == receipt.get("bytes") and sha == receipt.get("sha256"), "SOURCE_DIGEST_FAILED:" + key)
    with original.open("rb") as fh:
        head = fh.read(32)
    ensure(head.startswith(magic), "SOURCE_MAGIC_FAILED:" + key)
    if magic == PNG:
        ensure(struct.unpack(">II", head[16:24]) == (1024,1024), "TEXTURE_NOT_1K")
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        ensure(digest(dest) == (size,sha), "EXISTING_SOURCE_OVERLAY_CHANGED")
    else:
        temp = dest.with_suffix(dest.suffix + ".part")
        ensure(not temp.exists(), "INCOMPLETE_COPY_PRESENT")
        try:
            shutil.copyfile(original, temp)
            ensure(digest(temp) == (size,sha), "COPY_SHA256_FAILED")
            temp.replace(dest)
        finally:
            if temp.exists(): temp.unlink()

def stage(warehouse, project, limit=16):
    chosen = select(warehouse, limit)
    root = project / "SourceAssets/Production" / ROOT
    ensure(not root.is_symlink(), "OVERLAY_SYMLINK_FORBIDDEN")
    planfile = project / "Data/ChapterAssetStreamingPlan.json"
    plan = doc(planfile)
    bank = plan["banks"]["P1C01"]["assets"]
    entries = []
    for idx, (slug, kind, wave, base, mesh, maps, rows, size) in enumerate(chosen):
        dest = root / slug
        safe_copy(base, mesh, rows[mesh], dest/(slug+".fbx"), MAGIC)
        for role, path in maps.items():
            safe_copy(base, path, rows[path], dest/Path(path).name, PNG)
        material = "MI_P1C01_" + slug
        mtl = dest/(slug+".mtl")
        body = "newmtl " + material + "\nKd 1 1 1\nPr 0.68\nPm 0\nKs 0.1 0.1 0.1\nmap_Kd " + Path(maps["BaseColor"]).name + "\n"
        if mtl.exists():
            ensure(mtl.read_text(encoding="utf-8") == body, "SIDECAR_MTL_DRIFT")
        else:
            mtl.write_text(body, encoding="utf-8")
        asset = "/Game/Production/World/Shire/VerifiedPBR/" + slug + "/" + slug + "." + slug
        if asset not in bank:
            bank.append(asset)
        entries.append({"id":slug,"asset":asset,"category":kind,
                        "location":list(LOCATIONS[kind][idx%len(LOCATIONS[kind])]),
                        "target_radius_cm":85,"collision":False,"source_wave":wave,
                        "state":"PENDING_UNREAL_IMPORT_AND_VISUAL_QC"})
    # The preloader and world builder read one runtime source of truth.
    plan["p1c01_verified_world_decoration"] = entries
    planfile.write_text(json.dumps(plan,indent=2)+"\n",encoding="utf-8")
    status = {"stage":"VERIFIED_STATIC_SOURCE_STAGED_FOR_UNREAL","count":len(entries),
              "assets":[x["id"] for x in entries],
              "acceptance":"NOT_PIE_TESTED_OR_VISUALLY_ACCEPTED"}
    output = project/"Saved/P1C01VerifiedPBR/production_stage_receipt.json"
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(status,indent=2)+"\n",encoding="utf-8")
    print("P1C01_PBR_VERIFIED_SOURCE_STAGE_PASS count="+str(len(entries))+
          " runtime=UNTESTED importer=NEXT")
    return status

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--warehouse-root",type=Path,required=True)
    parser.add_argument("--project-root",type=Path,required=True)
    parser.add_argument("--limit",type=int,default=16)
    args=parser.parse_args()
    try: stage(args.warehouse_root,args.project_root,args.limit)
    except (IntakeError,OSError,KeyError,ValueError,TypeError) as exc:
        print("P1C01_PBR_VERIFIED_STAGE_FAILED "+str(exc),file=sys.stderr)
        return 2
    return 0

if __name__=="__main__":
    raise SystemExit(main())
