#!/usr/bin/env python3
"""Read-only physical Warehouse attestation for the ten known Drive ZIPs.

This verifies bytes on D: (not just a hosted CI result) and generates a
quarantined source candidate queue. It NEVER unpacks to Content, imports UE4
assets, approves third-party licenses, deletes Drive data, or accepts Gate 6/7.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
import zipfile

import validate_drive_source_bundles as source_qc

SNAPSHOT = Path(__file__).resolve().parents[1] / "Data/DriveSourceLocalPreflight20261011.json"
CATEGORIES = {
    "GH11705468534_frodo_source.zip": "01_Characters_Animations",
    "GH11705009927_shire_28regions.zip": "02_Shire_P1C01",
    "GH11706518373_Shire_Nature_Binary_36_FBX.zip": "02_Shire_P1C01",
    "SHIRE_NATURE_UE427_BINARY_FBX_PNG_SOURCE_INTAKE_20261011.zip": "02_Shire_P1C01",
    "Shire_Nature_Wave_20261011.zip": "02_Shire_P1C01",
    "GH11704614644_polyhaven_shard1.zip": "04_PBR_Materials",
    "GH11704654471_polyhaven_shard2.zip": "04_PBR_Materials",
    "GH11705438692_polyhaven_shard3.zip": "04_PBR_Materials",
    "GH11705506123_polyhaven_shard0.zip": "04_PBR_Materials",
    "SHIRE_PRIORITY_LICENSED_PBR_4_MATERIALS_20261011.zip": "04_PBR_Materials",
}
PREFERRED_NATURE = "SHIRE_NATURE_UE427_BINARY_FBX_PNG_SOURCE_INTAKE_20261011.zip"
WAVES = [
    {"order": 1, "category": "Shire foliage/trees", "sources": [
        PREFERRED_NATURE, "GH11706518373_Shire_Nature_Binary_36_FBX.zip"]},
    {"order": 2, "category": "Shire surface materials", "sources": [
        "SHIRE_PRIORITY_LICENSED_PBR_4_MATERIALS_20261011.zip",
        "GH11705506123_polyhaven_shard0.zip", "GH11704614644_polyhaven_shard1.zip",
        "GH11704654471_polyhaven_shard2.zip", "GH11705438692_polyhaven_shard3.zip"]},
    {"order": 3, "category": "Architecture and regional source kits", "sources": [
        "GH11705009927_shire_28regions.zip"]},
    {"order": 4, "category": "Hero rig candidate, not a finished character", "sources": [
        "GH11705468534_frodo_source.zip"]},
    {"order": 5, "category": "Authored sound", "sources": []},
]


def digests(path):
    sha256 = hashlib.sha256()
    md5 = hashlib.md5()
    with path.open("rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            sha256.update(part)
            md5.update(part)
    return sha256.hexdigest(), md5.hexdigest()


def load_expected(path, count=10):
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("archives", [])
    names = [row.get("file") for row in entries]
    if (len(entries) != count or len(set(names)) != len(names)
            or (count == 10 and set(names) != set(CATEGORIES))
            or any(not re.fullmatch(r"[0-9a-f]{64}", row.get("sha256", "")) for row in entries)
            or any(type(row.get("byte_size")) is not int or row["byte_size"] <= 0 for row in entries)):
        raise ValueError("EXPECTED_SOURCE_SNAPSHOT_INVALID")
    return {row["file"]: row for row in entries}


def member_hashes(z, archive_name, label="", depth=0):
    """Digest actual FBX/PNG/TGA content, including one bounded nested ZIP."""
    for member in z.infolist():
        if member.is_dir():
            continue
        name = source_qc.safe_member(member)
        ext = Path(name).suffix.lower()
        if ext in (".fbx", ".png", ".tga"):
            with z.open(member) as f:
                digest, size = source_qc.digest_stream(f)
            if ext == ".fbx":
                with z.open(member) as f:
                    fmt = source_qc.classify_fbx(f.read(80))
            else:
                fmt = "TEXTURE"
            yield {"archive": archive_name, "member": label + name,
                   "sha256": digest, "bytes": size, "extension": ext, "format": fmt}
        elif ext == ".zip" and depth == 0 and member.file_size <= source_qc.MAX_NESTED_BYTES:
            with zipfile.ZipFile(io.BytesIO(z.read(member))) as child:
                yield from member_hashes(child, archive_name, label + name + "::", depth + 1)


def verify_receipt(warehouse, name, expected, receipts):
    category = CATEGORIES[name]
    relative = category + "/" + name
    matches = [r for r in receipts if r.get("remote_path") == relative
               and r.get("sha256") == expected["sha256"]]
    if len(matches) != 1:
        raise ValueError("MISSING_OR_DUPLICATE_SHA_BOUND_RECEIPT")
    record = matches[0]
    remote_id = record.get("remote_id", "")
    remote_md5 = str(record.get("remote_md5", "")).lower()
    if (not re.fullmatch(r"[A-Za-z0-9_-]{8,200}", remote_id)
            or not re.fullmatch(r"[0-9a-f]{32}", remote_md5)
            or record.get("remote_size") != expected["byte_size"]
            or record.get("state") != "LOCAL_STAGED_NOT_IMPORTED"
            or record.get("license_status") != "UNVERIFIED_NOT_IMPORTABLE"):
        raise ValueError("RECEIPT_FIELDS_INVALID")
    expected_dir = (warehouse / "_drive_temp_staging" / "files" / category).resolve()
    path = Path(record.get("local_path", ""))
    if (path.name != remote_id + "-" + expected["sha256"][:16] + "-" + name
            or path.resolve().parent != expected_dir
            or not path.is_file()):
        raise ValueError("WAREHOUSE_PATH_OR_FILE_INVALID")
    if path.stat().st_size != expected["byte_size"]:
        raise ValueError("WAREHOUSE_SIZE_MISMATCH")
    local_sha, local_md5 = digests(path)
    if local_sha != expected["sha256"] or local_md5 != remote_md5:
        raise ValueError("WAREHOUSE_SHA256_OR_REMOTE_MD5_MISMATCH")
    return path, remote_id, local_md5


def assess(warehouse, snapshot, required_count=10):
    expected = load_expected(snapshot, count=required_count)
    receipt_dir = warehouse / "_drive_temp_staging" / "receipts"
    records = []
    if receipt_dir.is_dir():
        for file in sorted(receipt_dir.glob("*.json")):
            try:
                record = json.loads(file.read_text(encoding="utf-8"))
                if isinstance(record, dict):
                    records.append(record)
            except (ValueError, OSError):
                # Corrupt receipts are never silently accepted for a source.
                records.append({"remote_path": "__INVALID_RECEIPT__"})
    actual = []
    digested_members = []
    errors = []
    for name, item in sorted(expected.items()):
        row = {"file": name, "category": CATEGORIES.get(name, "UNKNOWN"),
               "expected_sha256": item["sha256"], "physical_qc": "FAIL",
               "unreal_import_status": "NOT_TESTED",
               "license_status": "MANUAL_REVIEW_REQUIRED"}
        try:
            if name not in CATEGORIES:
                raise ValueError("ARCHIVE_NOT_IN_APPROVED_TEN_FILE_SET")
            path, remote_id, remote_md5 = verify_receipt(warehouse, name, item, records)
            with zipfile.ZipFile(path) as archive:
                qc = source_qc.scan_archive(archive)
                if qc["failures"]:
                    raise ValueError("PHYSICAL_ARCHIVE_CONTENT_INVALID:" + ",".join(qc["failures"][:4]))
                if qc["fbx_formats"] != item.get("fbx_formats", {}):
                    raise ValueError("PHYSICAL_FBX_FORMAT_PROFILE_CHANGED")
                if qc["types"] != item.get("types", {}):
                    raise ValueError("PHYSICAL_ARCHIVE_MEMBER_TYPES_CHANGED")
                if len(archive.infolist()) != next(
                        (r.get("zip_entries") for r in records
                         if r.get("remote_id") == remote_id
                         and r.get("sha256") == item["sha256"]), -1):
                    raise ValueError("ZIP_RECEIPT_ENTRY_COUNT_MISMATCH")
                digested_members.extend(member_hashes(archive, name))
            receipt_match = next(r for r in records if r.get("remote_id") == remote_id
                                 and r.get("sha256") == item["sha256"])
            row.update({"remote_id": remote_id, "local_md5": remote_md5,
                        "md5_provenance": receipt_match.get("remote_md5_source", "REMOTE_VERIFIED"),
                        "physical_qc": "PASS", "archive_members": qc["members"],
                        "fbx_formats": qc["fbx_formats"], "material_receipt": qc["receipt"]})
        except (ValueError, OSError, KeyError, zipfile.BadZipFile) as err:
            row["failure"] = str(err)[:450]
            errors.append({"file": name, "reason": row["failure"]})
        actual.append(row)
    hashes = defaultdict(list)
    counts = Counter()
    quarantines = []
    for m in digested_members:
        hashes[(m["extension"], m["sha256"])].append(m)
        counts[m["format"]] += 1
        if m["format"] != "FBX_BINARY_7400" and m["extension"] == ".fbx":
            quarantines.append({"file": m["archive"], "member": m["member"],
                                "reason": "ASCII_OR_UNSUPPORTED_FBX_SOURCE_ONLY"})
    dupes = []
    for (_, digest), entries in sorted(hashes.items()):
        if len(entries) > 1:
            entries.sort(key=lambda m: (m["archive"] != PREFERRED_NATURE, m["archive"], m["member"]))
            dupes.append({"sha256": digest, "bytes": entries[0]["bytes"],
                          "retain_source_candidate": entries[0]["archive"] + "::" + entries[0]["member"],
                          "duplicates_to_skip": [e["archive"] + "::" + e["member"] for e in entries[1:]]})
    for row in actual:
        for item in row.get("material_receipt", {}).get("polyhaven_quarantined", []):
            quarantines.append({"file": row["file"], "member": item.get("slug"),
                                "reason": item.get("reason", "INCOMPLETE_MATERIAL_RECEIPT")})
    if required_count == 10 and len(actual) != 10:
        errors.append({"file": "SNAPSHOT", "reason": "TEN_SOURCE_PACKS_REQUIRED"})
    report = {
        "schema_version": 1,
        "scope": "PHYSICAL_WAREHOUSE_SOURCE_QC_ONLY",
        "run_id": os.environ.get("GITHUB_RUN_ID", "LOCAL"),
        "control_sha": os.environ.get("GITHUB_SHA", "LOCAL"),
        "state": "SOURCE_QC_PASS_IMPORT_BLOCKED" if not errors else "SOURCE_QC_FAILED",
        "verified_archive_count": sum(a["physical_qc"] == "PASS" for a in actual),
        "expected_archive_count": len(expected),
        "archive_rows": actual,
        "sha256_and_remote_md5": "PINNED_SHA256_AND_LOCAL_MD5;REMOTE_MD5_IF_AVAILABLE",
        "asset_inventory": dict(sorted(counts.items())),
        "distinct_content_hash_count": len(hashes),
        "duplicate_groups": dupes,
        "quarantine": quarantines,
        "production_wave_queue": [{**wave, "unreal_import": "BLOCKED_LICENSE_AND_ENGINE_QC",
                                   "engine_promotion": False} for wave in WAVES],
        "automated_license_approval": False,
        "unreal_imported": False,
        "pie_tested": False,
        "device_tested": False,
        "human_visual_acceptance": False,
        "gate_6_7_closed": False,
        "errors": errors,
    }
    return report


def write_atomic(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, tmp = tempfile.mkstemp(prefix=".physical-qc-", dir=str(path.parent))
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--warehouse-root", type=Path, required=True)
    parser.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report = assess(args.warehouse_root, args.snapshot)
    output = args.out or args.warehouse_root / "_drive_temp_staging" / "reports" / "source_qc_latest.json"
    write_atomic(output, report)
    print("DRIVE_PHYSICAL_SOURCE_QC result=%s matched=%d/%d duplicates=%d quarantines=%d report=%s" %
          (report["state"], report["verified_archive_count"], report["expected_archive_count"],
           len(report["duplicate_groups"]), len(report["quarantine"]), output))
    for row in report["errors"]:
        print("DRIVE_PHYSICAL_SOURCE_QC_ERROR file=%s reason=%s" % (row["file"], row["reason"]))
    raise SystemExit(0 if not report["errors"] else 5)


if __name__ == "__main__":
    main()
