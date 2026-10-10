#!/usr/bin/env python3
"""Stage already-downloaded Poly Haven CC0 source and PBR outputs into ONE persistent warehouse.

Does not fetch provider URLs, run UE4, promote assets to /Game, or accept Gate 6/7.
Requires verified source receipt, PBR receipt, all source MD5/SHA256, output SHA256,
atomic same-volume promotion, and 6 GiB (or greater) remaining free disk space.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import struct

RESERVE_BYTES = 6 * 1024 ** 3
SLUG = re.compile(r"[a-z0-9_]{3,80}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
MD5 = re.compile(r"[0-9a-f]{32}\Z")
SOURCE_EXTENSIONS = {".fbx", ".png", ".jpg", ".jpeg", ".tga", ".exr", ".webp"}
PNG_MAGIC = bytes.fromhex("89504e470d0a1a0a")
FBX_MAGIC = b"Kaydara FBX Binary"


class StageError(ValueError):
    pass


def safe_path(value: str) -> Path:
    if not isinstance(value, str) or not value or len(value) > 245:
        raise StageError("UNSAFE_RELATIVE_PATH")
    if "\\" in value or "\x00" in value or ":" in value:
        raise StageError("UNSAFE_RELATIVE_PATH")
    posix = PurePosixPath(value)
    if posix.is_absolute() or any(p in ("", ".", "..") for p in posix.parts):
        raise StageError("UNSAFE_RELATIVE_PATH")
    return Path(*posix.parts)


def file_hashes(path: Path) -> tuple[int, str, str]:
    if path.is_symlink() or not path.is_file():
        raise StageError("FILE_MISSING_OR_SYMLINK:" + str(path))
    h256, hmd5 = hashlib.sha256(), hashlib.md5()
    count = 0
    with path.open("rb") as inp:
        while True:
            block = inp.read(1024 * 1024)
            if not block:
                break
            count += len(block)
            h256.update(block)
            hmd5.update(block)
    return count, h256.hexdigest(), hmd5.hexdigest()


def read_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise StageError("RECEIPT_MISSING:" + str(path))
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise StageError("RECEIPT_NOT_OBJECT")
    return obj


def validate_png(path: Path) -> None:
    with path.open("rb") as inp:
        header = inp.read(26)
    if len(header) < 26 or not header.startswith(PNG_MAGIC) or header[12:16] != b"IHDR":
        raise StageError("PNG_HEADER_INVALID:" + str(path))
    width, height = struct.unpack(">II", header[16:24])
    if (width, height) != (1024, 1024):
        raise StageError("PBR_NOT_1K:" + str(path))


def checked_file(root: Path, relative: str, expected_bytes: int, expected_sha256: str,
                 expected_md5: str | None = None, extension: set[str] | None = None) -> Path:
    rel = safe_path(relative)
    if extension is not None and rel.suffix.lower() not in extension:
        raise StageError("SOURCE_EXTENSION_NOT_ALLOWED:" + relative)
    candidate = root / rel
    actual_size, actual_sha, actual_md5 = file_hashes(candidate)
    if (not isinstance(expected_bytes, int) or actual_size != expected_bytes
            or not isinstance(expected_sha256, str) or not SHA256.fullmatch(expected_sha256)
            or actual_sha != expected_sha256):
        raise StageError("SOURCE_SIZE_OR_SHA256_MISMATCH:" + relative)
    if expected_md5 is not None and (
            not isinstance(expected_md5, str) or not MD5.fullmatch(expected_md5)
            or actual_md5 != expected_md5):
        raise StageError("SOURCE_MD5_MISMATCH:" + relative)
    return candidate


def validate_inputs(source_root: Path, pbr_root: Path, expected_source: int,
                    expected_prepared: int) -> dict:
    source_receipt_file = source_root / "p1c01_adaptive_polyhaven_receipt.json"
    pbr_receipt_file = pbr_root / "p1c01_adaptive_pbr_receipt.json"
    source = read_json(source_receipt_file)
    pbr = read_json(pbr_receipt_file)
    if source.get("license") != "CC0" or source.get("mode") != (
            "HOSTED_SOURCE_ONLY_NO_UNREAL_NO_PERSISTENT_WAREHOUSE_MUTATION"):
        raise StageError("SOURCE_LICENSE_OR_MODE_UNTRUSTED")
    accepted = source.get("accepted")
    if not isinstance(accepted, list) or len(accepted) != expected_source or (
            source.get("source_assets_staged") != expected_source):
        raise StageError("SOURCE_COUNT_INCORRECT")
    if pbr.get("input_assets") != expected_source or (
            pbr.get("prepared_assets") != expected_prepared):
        raise StageError("PBR_COUNT_INCORRECT")
    if pbr.get("source_receipt_sha256") != file_hashes(source_receipt_file)[1]:
        raise StageError("PBR_SOURCE_RECEIPT_SHA256_MISMATCH")
    generated = pbr.get("assets")
    quarantine = pbr.get("quarantined")
    if not isinstance(generated, list) or len(generated) != expected_prepared or (
            not isinstance(quarantine, list) or len(quarantine) != expected_source - expected_prepared):
        raise StageError("PBR_QUARANTINE_ACCOUNTING_MISMATCH")

    originals: dict[str, list[dict]] = {}
    seen_sources, expected_source_files = set(), {"p1c01_adaptive_polyhaven_receipt.json"}
    seen_lower = set()
    for item in accepted:
        slug = item.get("id")
        if not isinstance(slug, str) or not SLUG.fullmatch(slug) or slug in seen_sources:
            raise StageError("INVALID_OR_DUPLICATED_SLUG")
        seen_sources.add(slug)
        if item.get("license") != "CC0" or item.get("provider_page") != (
                "https://polyhaven.com/a/" + slug):
            raise StageError("SOURCE_PROVENANCE_INCOMPLETE:" + slug)
        if not isinstance(item.get("files"), list) or not item["files"]:
            raise StageError("SOURCE_FILES_MISSING:" + slug)
        rows = []
        for f in item["files"]:
            rel = safe_path(f.get("relative_file")).as_posix()
            src_rel = "assets/" + slug + "/" + rel.replace("\\", "/")
            key = src_rel.lower()
            if key in seen_lower:
                raise StageError("DUPLICATE_SOURCE_FILENAME:" + src_rel)
            seen_lower.add(key)
            expected_source_files.add(src_rel)
            src = checked_file(source_root, src_rel, f.get("bytes"), f.get("sha256"),
                               f.get("md5"), SOURCE_EXTENSIONS)
            if src.suffix.lower() == ".fbx":
                with src.open("rb") as fh:
                    if not fh.read(len(FBX_MAGIC)).startswith(FBX_MAGIC):
                        raise StageError("SOURCE_NOT_BINARY_FBX:" + slug)
            rows.append({"src": src, "rel": rel, "size": f["bytes"],
                         "sha256": f["sha256"], "source_page": item["provider_page"],
                         "slug": slug})
        if not any(r["rel"] == slug + ".fbx" for r in rows):
            raise StageError("PRIMARY_FBX_MISSING:" + slug)
        originals[slug] = rows

    expected_pbr_files = {"p1c01_adaptive_pbr_receipt.json"}
    converted: dict[str, list[dict]] = {}
    seen_prepared, seen_pbr_casefold = set(), set()
    ready_count, png_count, held_count = 0, 0, 0
    for item in generated:
        slug = item.get("id")
        if slug not in originals or slug in seen_prepared:
            raise StageError("PBR_DUPLICATE_OR_UNSOURCED_ID")
        seen_prepared.add(slug)
        fbx_rel = item.get("fbx_path")
        if fbx_rel != "assets/" + slug + "/" + slug + ".fbx":
            raise StageError("PBR_FBX_PATH_MISMATCH:" + slug)
        src_fbx = next(x for x in originals[slug] if x["rel"] == slug + ".fbx")
        if item.get("fbx_sha256") != src_fbx["sha256"] or (
                item.get("fbx_bytes") != src_fbx["size"]):
            raise StageError("PBR_FBX_NOT_ORIGINAL:" + slug)
        fb = checked_file(pbr_root, fbx_rel, item["fbx_bytes"], item["fbx_sha256"], 
                          extension={".fbx"})
        rows = [{"src": fb, "rel": slug + ".fbx", "size": item["fbx_bytes"],
                 "sha256": item["fbx_sha256"], "role": "STATIC_FBX"}]
        expected_pbr_files.add(fbx_rel)
        seen_pbr_casefold.add(fbx_rel.lower())
        for group, is_held in (("maps", False), ("held_material_variants", True)):
            entries = item.get(group, [])
            if not isinstance(entries, list):
                raise StageError("MATERIAL_RECEIPT_NOT_ARRAY:" + slug)
            if group == "maps" and len(entries) == 0:
                raise StageError("PBR_HAS_NO_MATERIALS:" + slug)
            for record in entries:
                rel = record.get("path")
                safe_path(rel)
                prefix = "assets/" + slug + "/"
                if not rel.startswith(prefix):
                    raise StageError("MATERIAL_OUTSIDE_ASSET:" + slug)
                if rel.lower() in seen_pbr_casefold:
                    raise StageError("DUPLICATED_PBR_MATERIAL_PATH:" + slug)
                seen_pbr_casefold.add(rel.lower())
                if is_held:
                    if (record.get("eligible_for_ue_import") is not False or
                            record.get("status") != "HOLD_MATERIAL_VARIANT_NO_INDEPENDENT_NORMAL_ROUGHNESS"
                            or not rel.startswith(prefix + "holds/")):
                        raise StageError("HELD_MATERIAL_NOT_ISOLATED:" + slug)
                    held_count += 1
                else:
                    if record.get("role") not in {"BaseColor", "NormalDX", "ORM", "OpacityMask"}:
                        raise StageError("INVALID_MATERIAL_ROLE:" + slug)
                    if record.get("resolution") != [1024, 1024]:
                        raise StageError("MATERIAL_RESOLUTION_NOT_1K:" + slug)
                    png_count += 1
                found = checked_file(pbr_root, rel, record.get("bytes"),
                                     record.get("sha256"), extension={".png"})
                validate_png(found)
                expected_pbr_files.add(rel)
                rows.append({"src": found, "rel": rel[len(prefix):],
                             "size": record["bytes"], "sha256": record["sha256"],
                             "role": "HELD_DRY_COLOR" if is_held else record["role"]})
        converted[slug] = rows
        ready_count += 1

    quarantined_ids = set()
    for row in quarantine:
        slug = row.get("id")
        if slug not in originals or slug in seen_prepared or slug in quarantined_ids:
            raise StageError("INVALID_QUARANTINE_ID")
        quarantined_ids.add(slug)
    if set(originals) != seen_prepared | quarantined_ids:
        raise StageError("SOURCE_TO_PBR_DISPOSITION_INCOMPLETE")

    # Reject silent payload additions, including archive path tricks or unreceipted third-party files.
    actual_sources = {p.relative_to(source_root).as_posix() for p in source_root.rglob("*")
                      if p.is_file()}
    actual_pbr = {p.relative_to(pbr_root).as_posix() for p in pbr_root.rglob("*")
                  if p.is_file()}
    if actual_sources != expected_source_files or actual_pbr != expected_pbr_files:
        raise StageError("UNRECEIPTED_SOURCE_OR_PBR_FILES")

    return {"source": source, "pbr": pbr, "originals": originals, "converted": converted,
            "quarantined_ids": quarantined_ids, "prepared_count": ready_count,
            "png_count": png_count, "held_count": held_count,
            "source_receipt_sha256": file_hashes(source_receipt_file)[1],
            "pbr_receipt_sha256": file_hashes(pbr_receipt_file)[1]}


def verify_existing(wave_dir: Path, src_digest: str, pbr_digest: str) -> dict:
    receipt = read_json(wave_dir / "receipt_adaptive_pbr.json")
    if (receipt.get("source_receipt_sha256") != src_digest or
            receipt.get("pbr_receipt_sha256") != pbr_digest):
        raise StageError("PERSISTENT_RECEIPT_MISMATCH_NO_OVERWRITE")
    for row in receipt.get("files", []):
        f = Path(row["file"])
        if not f.is_relative_to(wave_dir):
            raise StageError("PERSISTENT_FILE_OUTSIDE_WAVE")
        checked_file(wave_dir, f.relative_to(wave_dir).as_posix(),
                     row["bytes"], row["sha256"])
    return receipt



def check_staged_wave(warehouse_root: Path, wave: str, expected_source: int,
                      expected_prepared: int) -> bool:
    """Fail closed on tampered existing files; skip expensive download only after full digest audit."""
    if not SLUG.fullmatch(wave):
        raise StageError("WAVE_ID_UNSAFE")
    final = warehouse_root / "_p1c01_adaptive_polyhaven" / wave
    if not final.exists():
        print("P1C01_PBR_WAREHOUSE_NOT_PRESENT wave=" + wave, flush=True)
        return False
    if final.is_symlink():
        raise StageError("PERSISTENT_WAVE_SYMLINK_FORBIDDEN")
    receipt = read_json(final / "receipt_adaptive_pbr.json")
    if (receipt.get("stage") != "PERSISTENT_WAREHOUSE_SOURCE_ONLY"
            or receipt.get("wave") != wave
            or receipt.get("original_source_count") != expected_source
            or receipt.get("converted_fbx_count") != expected_prepared
            or len(receipt.get("asset_ids", [])) != expected_source):
        raise StageError("PERSISTENT_WAVE_METADATA_MISMATCH")
    src_digest = file_hashes(final / "source_receipt_original.json")[1]
    pbr_digest = file_hashes(final / "pbr_receipt_original.json")[1]
    verify_existing(final, src_digest, pbr_digest)
    if len(receipt.get("files", [])) < expected_source:
        raise StageError("PERSISTENT_WAVE_FILE_COUNT_MISMATCH")
    print("P1C01_PBR_WAREHOUSE_REUSE_PASS wave=" + wave
          + " files=" + str(len(receipt["files"])) + " sha256=pass", flush=True)
    return True


def stage(source_root: Path, pbr_root: Path, warehouse_root: Path, wave: str,
          expected_source: int, expected_prepared: int, reserve_bytes: int = RESERVE_BYTES,
          run_id: str = "local", reject_prior_ids: Path | None = None) -> dict:
    if not SLUG.fullmatch(wave):
        raise StageError("WAVE_ID_UNSAFE")
    plan = validate_inputs(source_root, pbr_root, expected_source, expected_prepared)
    parent = warehouse_root / "_p1c01_adaptive_polyhaven"
    if warehouse_root.is_symlink() or parent.is_symlink():
        raise StageError("WAREHOUSE_SYMLINK_FORBIDDEN")
    if reject_prior_ids:
        prior = read_json(reject_prior_ids)
        old_ids = set(prior.get("asset_ids", []))
        if old_ids.intersection(plan["originals"]):
            raise StageError("PREVIOUS_ASSET_REDUPLICATED")
    parent.mkdir(parents=True, exist_ok=True)
    final = parent / wave
    if final.exists():
        receipt = verify_existing(final, plan["source_receipt_sha256"],
                                  plan["pbr_receipt_sha256"])
        print("P1C01_PBR_WAREHOUSE_REUSED wave=" + wave + " sha256=pass", flush=True)
        return receipt

    payload_bytes = sum(r["size"] for rows in plan["originals"].values() for r in rows)
    payload_bytes += sum(r["size"] for rows in plan["converted"].values() for r in rows)
    current_free = shutil.disk_usage(parent).free
    if current_free - payload_bytes < reserve_bytes:
        raise StageError("WAREHOUSE_6GIB_RESERVE_FAIL free=" + str(current_free)
                         + " required=" + str(payload_bytes + reserve_bytes))
    txn = parent / (".incoming_" + wave + "_" + re.sub(r"[^a-zA-Z0-9_]", "_", run_id))
    if txn.exists():
        raise StageError("WAREHOUSE_TRANSACTION_ALREADY_EXISTS")
    txn.mkdir()
    files = []
    source = plan["source"]
    by_id = {a["id"]: a for a in source["accepted"]}
    license_body = {
        "license_claim": "CC0",
        "provider": "Poly Haven",
        "provider_license_url": "https://polyhaven.com/license",
        "source_receipt_sha256": plan["source_receipt_sha256"],
        "scope": "Original CC0 provider staging receipt; does not imply a character/film likeness license",
    }

    try:
        license_file = txn / "polyhaven_license_claim.json"
        license_file.write_text(json.dumps(license_body, sort_keys=True, indent=2) + "\n",
                                encoding="utf-8")
        license_sha = file_hashes(license_file)[1]
        def persist(record: dict, target_rel: str, status: str) -> None:
            safe_path(target_rel)
            dst = txn / target_rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(record["src"], dst)
            length, digest, _ = file_hashes(dst)
            if digest != record["sha256"] or length != record["size"]:
                raise StageError("TRANSACTION_COPY_HASH_FAIL:" + target_rel)
            slug = record["slug"]
            page = by_id[slug]["provider_page"]
            files.append({
                "file": str(final / target_rel),
                "bytes": length,
                "sha256": digest,
                "asset_slug": slug,
                "asset_id": slug,
                "provider": "POLY_HAVEN",
                "license": "CC0",
                "category": "PBR_STATIC_MODEL_SOURCE",
                "source_page": page,
                "source_url": "https://api.polyhaven.com/files/" + slug,
                "source_url_kind": "EXACT_PROVIDER_METADATA_ENDPOINT_NOT_DIRECT_FILE_URL",
                "license_snapshot": str(final / "polyhaven_license_claim.json"),
                "license_sha256": license_sha,
                "state": status,
            })
        for slug, rows in sorted(plan["originals"].items()):
            for record in rows:
                persist(record, "assets/" + slug + "/original/" + record["rel"],
                        "SOURCE_ONLY_QUARANTINED_PBR" if slug in plan["quarantined_ids"]
                        else "SOURCE_ONLY_ORIGINAL_MAPS")
        for slug, rows in sorted(plan["converted"].items()):
            status = next(a["status"] for a in plan["pbr"]["assets"] if a["id"] == slug)
            for record in rows:
                kind = "HELD_COLOR_NOT_FOR_UE" if record["role"] == "HELD_DRY_COLOR" else (
                    "SOURCE_PBR_BIOME_HOLD" if status == "HOLD_BIOME" else (
                        "SOURCE_PBR_IDENTITY_HOLD" if status == "HOLD_IDENTITY"
                        else "SOURCE_PBR_PENDING_STATIC_GEOMETRY_LOD_COLLISION_QC"))
                persist({**record, "slug": slug}, "assets/" + slug + "/prepared/" + record["rel"], kind)
        source_report = txn / "source_receipt_original.json"
        pbr_report = txn / "pbr_receipt_original.json"
        shutil.copyfile(source_root / "p1c01_adaptive_polyhaven_receipt.json", source_report)
        shutil.copyfile(pbr_root / "p1c01_adaptive_pbr_receipt.json", pbr_report)
        receipt = {
            "batch_id": "P1C01_ADAPTIVE_POLYHAVEN_" + wave.upper(),
            "provider": "POLY_HAVEN",
            "license": "CC0",
            "staged_at_utc": datetime.now(timezone.utc).isoformat(),
            "stage": "PERSISTENT_WAREHOUSE_SOURCE_ONLY",
            "wave": wave, "original_source_count": expected_source,
            "converted_fbx_count": plan["prepared_count"],
            "converted_png_count": plan["png_count"],
            "held_color_count": plan["held_count"],
            "quarantined_ids": sorted(plan["quarantined_ids"]),
            "asset_ids": sorted(plan["originals"]),
            "source_receipt_sha256": plan["source_receipt_sha256"],
            "pbr_receipt_sha256": plan["pbr_receipt_sha256"],
            "files": files,
            "bytes": payload_bytes,
            "evidence_boundary": (
                "Permanent source only; no UE4 import, geometric/LOD/collision QC, "
                "PIE, named character likeness, target-device FPS, visual or Gate 6/7 acceptance. "
                "Direct provider file URLs were not in original download receipts."
            ),
        }
        (txn / "receipt_adaptive_pbr.json").write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if shutil.disk_usage(parent).free < reserve_bytes:
            raise StageError("WAREHOUSE_RESERVE_BREACH_AFTER_STAGING")
        os.rename(txn, final)
    except BaseException:
        if txn.exists():
            shutil.rmtree(txn)
        raise
    print("P1C01_PBR_WAREHOUSE_STAGE_PASS wave=" + wave +
          " originals=" + str(expected_source) + " convertedFBX=" +
          str(plan["prepared_count"]) + " convertedPNG=" + str(plan["png_count"]) +
          " quarantined=" + str(len(plan["quarantined_ids"])) +
          " persistedFiles=" + str(len(files)) + " bytes=" + str(payload_bytes) +
          " diskFree=" + str(shutil.disk_usage(parent).free) +
          " NOT_UE4_IMPORTED", flush=True)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--pbr-root", type=Path)
    parser.add_argument("--warehouse-root", type=Path, required=True)
    parser.add_argument("--wave", required=True)
    parser.add_argument("--expected-source", type=int, required=True)
    parser.add_argument("--expected-prepared", type=int, required=True)
    parser.add_argument("--run-id", default="local")
    parser.add_argument("--reject-prior-ids", type=Path)
    parser.add_argument("--check-existing", action="store_true", help="verify persistent wave to skip re-download; 3=absent")
    args = parser.parse_args()
    if args.check_existing:
        return 0 if check_staged_wave(args.warehouse_root, args.wave,
                                      args.expected_source, args.expected_prepared) else 3
    if args.source_root is None or args.pbr_root is None:
        parser.error("--source-root and --pbr-root required for staging")
    stage(args.source_root, args.pbr_root, args.warehouse_root, args.wave,
          args.expected_source, args.expected_prepared,
          run_id=args.run_id, reject_prior_ids=args.reject_prior_ids)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
