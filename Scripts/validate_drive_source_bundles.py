#!/usr/bin/env python3
"""Fail-closed offline provenance preflight for Shire Journey Drive ZIP source batches.

This never imports assets, runs embedded scripts, deletes Drive objects, or marks
UE asset acceptance. A passing archive means only source integrity was audited.
"""
import argparse
import hashlib
import io
import json
import re
import stat
import struct
import zipfile
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

MAX_MEMBERS = 20000
MAX_UNPACKED = 4 * (1024 ** 3)
MAX_MEMBER = 2 * (1024 ** 3)
MAX_NESTED_BYTES = 64 * (1024 ** 2)
FBX_MAGIC = b"Kaydara FBX Binary  \x00\x1a\x00"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
ALLOWED = {".fbx", ".png", ".tga", ".json", ".txt", ".md", ".zip", ".blend", ".html", ".py", ".license"}


def digest_stream(stream):
    h = hashlib.sha256()
    size = 0
    while True:
        b = stream.read(1024 * 1024)
        if not b:
            return h.hexdigest(), size
        h.update(b)
        size += len(b)


def hash_file(path):
    with path.open("rb") as f:
        return digest_stream(f)[0]


def safe_member(member):
    name = member.filename.replace("\\", "/")
    parts = PurePosixPath(name).parts
    if not name or name.startswith("/") or ".." in parts or ":" in name or "\x00" in name:
        raise ValueError("UNSAFE_ARCHIVE_PATH " + repr(name))
    unix_mode = member.external_attr >> 16
    if member.flag_bits & 1 or (member.create_system == 3 and stat.S_IFMT(unix_mode) == stat.S_IFLNK):
        raise ValueError("UNSAFE_ARCHIVE_MEMBER " + repr(name))
    if member.file_size > MAX_MEMBER:
        raise ValueError("OVERSIZED_ARCHIVE_MEMBER " + repr(name))
    return name


def png_info(raw):
    if len(raw) < 33 or raw[:8] != PNG_MAGIC or raw[12:16] != b"IHDR":
        raise ValueError("NOT_PNG_FORMAT")
    w, h, depth, col, _, _, _ = struct.unpack(">IIBBBBB", raw[16:29])
    if not (0 < w <= 4096 and 0 < h <= 4096 and depth in (8, 16) and col in (0, 2, 3, 4, 6)):
        raise ValueError("PNG_DIMENSIONS_OR_COLOR_UNSUPPORTED")
    return [w, h]


def classify_fbx(prefix):
    if prefix.startswith(FBX_MAGIC):
        if len(prefix) < len(FBX_MAGIC) + 4:
            return "FBX_CORRUPT_HEADER"
        return "FBX_BINARY_7400" if struct.unpack("<I", prefix[len(FBX_MAGIC):len(FBX_MAGIC)+4])[0] == 7400 else "FBX_BINARY_OTHER_VERSION"
    if prefix.startswith(b"; FBX 7.4.0"):
        return "FBX_ASCII_SOURCE_ONLY"
    return "FBX_UNSUPPORTED"


def require_receipt_items(z, objects, failures, label):
    validated = 0
    for row in objects:
        name = row.get("path")
        expected = row.get("sha256")
        if not name or not re.fullmatch(r"[0-9a-fA-F]{64}", expected or ""):
            failures.append(label + ":BAD_RECEIPT_PATH_OR_SHA")
            continue
        try:
            with z.open(name) as f:
                actual, size = digest_stream(f)
            if actual != expected.lower() or ("bytes" in row and int(row["bytes"]) != size):
                failures.append(label + ":HASH_OR_SIZE_MISMATCH:" + name)
            else:
                validated += 1
        except (KeyError, OSError, ValueError) as exc:
            failures.append(label + ":RECEIPT_MISSING:" + name + ":" + str(exc)[:80])
    return validated


def require_receipt_map(z, hashes, failures, label):
    if not isinstance(hashes, dict):
        failures.append(label + ":RECEIPT_HASH_MAP_INVALID")
        return 0
    return require_receipt_items(z, [{"path": p, "sha256": h} for p, h in hashes.items()], failures, label)


def evaluate_receipts(z, failures, warnings, metadata):
    names = set(z.namelist())
    if "nature_receipt.json" in names:
        r = json.loads(z.read("nature_receipt.json"))
        metadata["nature_mesh_receipt_matches"] = require_receipt_items(z, r.get("objects", []), failures, "nature")
        if metadata["nature_mesh_receipt_matches"] != r.get("fbx_count"):
            failures.append("NATURE_FBX_COUNT_MISMATCH")
    if "fbx_receipt.json" in names:
        r = json.loads(z.read("fbx_receipt.json"))
        metadata["modular_fbx_receipt_matches"] = require_receipt_items(z, r.get("objects", []), failures, "modular")
        if metadata["modular_fbx_receipt_matches"] != r.get("fbx_count"):
            failures.append("MODULAR_FBX_COUNT_MISMATCH")
    if "receipt.json" in names:
        r = json.loads(z.read("receipt.json"))
        if "materials" in r and "shard" in r:
            materials = r.get("materials", [])
            expected_paths = []
            quarantined = r.get("quarantined", [])
            for m in materials:
                if m.get("license") != "CC0" or not str(m.get("source_page", "")).startswith("https://polyhaven.com/a/"):
                    failures.append("POLYHAVEN_LICENSE_OR_SOURCE_MISSING:" + str(m.get("slug")))
                outputs = m.get("outputs", [])
                if set(x.get("kind") for x in outputs) != {"BaseColor", "NormalDX", "ORM"}:
                    failures.append("POLYHAVEN_MISSING_TRIPLET:" + str(m.get("slug")))
                expected_paths.extend(outputs)
            metadata["polyhaven_mat_receipt_matches"] = require_receipt_items(z, expected_paths, failures, "polyhaven")
            metadata["polyhaven_materials"] = len(materials)
            metadata["polyhaven_quarantined"] = quarantined
            if r.get("staged") != len(materials) or r.get("physical_png") != len(expected_paths):
                failures.append("POLYHAVEN_COUNT_MISMATCH")
            if quarantined:
                warnings.append("SOURCE_SHARD_PARTIAL_QUARANTINED")
    if "Receipts/import_bindings.json" in names:
        r = json.loads(z.read("Receipts/import_bindings.json"))
        m = r.get("family_lod_meshes", [])
        metadata["nature_bundle_fbx_binding_count"] = len(m)
        for obj in m:
            if obj.get("source_file") not in names:
                failures.append("NATURE_BUNDLE_MISSING:" + str(obj.get("source_file")))
        metadata["nature_bundle_hashes_matched"] = require_receipt_map(
            z, r.get("source_file_hashes"), failures, "nature_bundle")
        if metadata["nature_bundle_hashes_matched"] != 63:
            failures.append("NATURE_BUNDLE_HASH_COUNT_MISMATCH")
        if not r.get("source_only") or r.get("unreal_imported"):
            failures.append("SOURCE_BUNDLE_FALSE_UE_STATE")
    if "Receipts/provenance_and_material_bindings.json" in names:
        r = json.loads(z.read("Receipts/provenance_and_material_bindings.json"))
        metadata["priority_material_sets"] = sorted(r.get("material_sets", {}).keys())
        if len(metadata["priority_material_sets"]) != 4:
            failures.append("PRIORITY_PBR_SET_COUNT_MISMATCH")
        for family, spec in r.get("material_sets", {}).items():
            if spec.get("license") != "CC0" or spec.get("provider") != "Poly Haven":
                failures.append("PRIORITY_PBR_LICENSE_INVALID:" + family)
            vals = spec.get("files", {})
            if set(vals) != {"BaseColor", "NormalDX", "ORM"}:
                failures.append("PRIORITY_PBR_TRIPLET_MISSING:" + family)
            else:
                require_receipt_items(z, list(vals.values()), failures, "priority_pbr:" + family)
        if r.get("runtime_imported") is not False:
            failures.append("PRIORITY_PBR_FALSE_IMPORT_STATE")
    if "materials_receipt.json" in names:
        r = json.loads(z.read("materials_receipt.json"))
        metadata["regional_bindings"] = len(r.get("region_bindings", []))
        if metadata["regional_bindings"] != 28 or r.get("state") != "PHYSICAL_SOURCE_GENERATED_NOT_UNREAL_IMPORTED":
            failures.append("REGION_PACKET_CANNOT_PROMOTE")
    if "p1c01_human_wave2_hosted.json" in names:
        r = json.loads(z.read("p1c01_human_wave2_hosted.json"))
        if r.get("license") != "CC0" or not str(r.get("source_page", "")).startswith("https://opengameart.org/"):
            failures.append("HERO_LICENSE_PROVENANCE_MISSING")
        for obj in r.get("normalized_results", []):
            name = obj.get("normalized_relative_path")
            expected = obj.get("normalized_sha256")
            if name and expected:
                require_receipt_items(z, [{"path": name, "sha256": expected, "bytes": obj.get("normalized_bytes")}], failures, "hero")
        metadata["hero_source_only"] = True
        warnings.append("HERO_VISUAL_RETARGET_NOT_UE_ACCEPTED")


def scan_archive(z, depth=0):
    members = [x for x in z.infolist() if not x.is_dir()]
    if not 0 < len(members) <= MAX_MEMBERS:
        raise ValueError("ZIP_MEMBER_COUNT_INVALID")
    if sum(i.file_size for i in members) > MAX_UNPACKED:
        raise ValueError("ZIP_EXPANSION_BUDGET_EXCEEDED")
    results = {"members": len(members), "types": {}, "fbx_formats": {}, "png_resolutions": {},
               "receipt": {}, "failures": [], "warnings": [], "nested": []}
    failures = results["failures"]
    warnings = results["warnings"]
    kinds = Counter()
    fbx = Counter()
    png = Counter()
    for member in members:
        try:
            name = safe_member(member)
        except ValueError as e:
            failures.append(str(e))
            continue
        kind = Path(name).suffix.lower()
        kinds[kind or "(none)"] += 1
        if kind not in ALLOWED:
            failures.append("UNEXPECTED_ARCHIVE_MEMBER:" + name)
            continue
        if kind == ".fbx":
            with z.open(member) as f:
                fmt = classify_fbx(f.read(80))
            fbx[fmt] += 1
            if fmt not in ("FBX_BINARY_7400", "FBX_ASCII_SOURCE_ONLY"):
                failures.append("UNSUPPORTED_FBX:" + name)
        elif kind == ".png":
            with z.open(member) as f:
                head = f.read(40)
            try:
                dim = png_info(head)
                png["%dx%d" % tuple(dim)] += 1
            except ValueError as e:
                failures.append("BAD_PNG:" + name + ":" + str(e))
        elif kind == ".zip":
            if depth >= 1:
                failures.append("NESTED_ZIP_DEPTH_EXCEEDED:" + name)
            elif member.file_size > MAX_NESTED_BYTES:
                failures.append("NESTED_ZIP_SIZE_EXCEEDED:" + name)
            else:
                with zipfile.ZipFile(io.BytesIO(z.read(member))) as inner:
                    nested = scan_archive(inner, depth+1)
                results["nested"].append({"path": name, **nested})
                if nested["failures"]:
                    failures.append("BAD_NESTED_ZIP:" + name)
        elif kind in (".py", ".html", ".blend"):
            warnings.append("SOURCE_ONLY_NOT_AUTORUN:" + name)
    try:
        bad = z.testzip()
        if bad:
            failures.append("ZIP_CRC_FAIL:" + bad)
    except (zipfile.BadZipFile, RuntimeError) as e:
        failures.append("ZIP_CRC_FAIL:" + str(e))
    try:
        evaluate_receipts(z, failures, warnings, results["receipt"])
    except (ValueError, KeyError, TypeError) as e:
        failures.append("RECEIPT_PARSE_FAIL:" + str(e))
    results["types"] = dict(sorted(kinds.items()))
    results["fbx_formats"] = dict(sorted(fbx.items()))
    results["png_resolutions"] = dict(sorted(png.items()))
    results["warnings"] = sorted(set(warnings))
    return results


def scan_files(files):
    archives = []
    for path in sorted(Path(x) for x in files):
        summary = {"file": path.name, "byte_size": path.stat().st_size, "sha256": hash_file(path)}
        try:
            with zipfile.ZipFile(path) as z:
                summary.update(scan_archive(z))
        except (zipfile.BadZipFile, ValueError, OSError) as e:
            summary.update({"members": 0, "failures": ["ARCHIVE_INVALID:" + str(e)]})
        summary["source_integrity"] = "PASS" if not summary["failures"] else "FAIL"
        summary["unreal_import_status"] = "NOT_TESTED"
        archives.append(summary)
    return {"schema_version": 1, "scope": "OFFLINE_SOURCE_INTEGRITY_ONLY_NOT_UNREAL",
            "archives": archives,
            "summary": {"archives": len(archives), "source_integrity_pass": sum(a["source_integrity"] == "PASS" for a in archives),
                        "source_integrity_fail": sum(a["source_integrity"] == "FAIL" for a in archives),
                        "source_bytes": sum(a["byte_size"] for a in archives),
                        "unreal_imported": 0, "pie_validated": 0, "device_validated": 0}}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("archives", nargs="*", type=Path)
    p.add_argument("--directory", type=Path)
    p.add_argument("--out", type=Path)
    a=p.parse_args()
    paths = list(a.archives)
    if a.directory:
        paths += sorted(a.directory.glob("*.zip"))
    if not paths:
        p.error("at least one ZIP archive required")
    report=scan_files(paths)
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"summary":report["summary"], "failures":[{"file":x["file"],"errors":x["failures"]} for x in report["archives"] if x["failures"]]},sort_keys=True))
    raise SystemExit(0 if report["summary"]["source_integrity_fail"] == 0 else 3)

if __name__=="__main__":
    main()