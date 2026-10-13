#!/usr/bin/env python3
"""Reconcile cloud FBX receipts without claiming warehouse or Unreal import.

Usage: python Scripts/audit_source_receipts.py RECEIPT.json [RECEIPT.json ...]
Prints one JSON report; strict mode exits nonzero for identity conflicts.
"""
import argparse
import hashlib
import json
from pathlib import Path


def audit(paths):
    records = {}
    conflicts = []
    for filename in paths:
        receipt_path = Path(filename).resolve()
        data = json.loads(receipt_path.read_text(encoding="utf-8"))
        items = data.get("objects")
        if not isinstance(items, list):
            raise ValueError("receipt must contain an objects array: " + str(receipt_path))
        for item in items:
            relative = item["path"]
            if not isinstance(relative, str) or not relative.lower().endswith(".fbx"):
                raise ValueError("invalid FBX path")
            target = (receipt_path.parent / relative).resolve()
            if not target.is_relative_to(receipt_path.parent) or not target.is_file():
                raise ValueError("unsafe or missing source: " + relative)
            raw = target.read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            if digest != item["sha256"] or len(raw) != item["bytes"]:
                raise ValueError("source checksum/length mismatch: " + relative)
            if not raw.startswith(b"Kaydara FBX Binary") or len(raw) < 27 or int.from_bytes(raw[23:27], "little") != 7400:
                raise ValueError("not FBX binary 7400: " + relative)
            key = (str(receipt_path.parent), relative)
            if key in records and records[key]["sha256"] != digest:
                conflicts.append(relative)
            records[key] = {"sha256": digest, "bytes": len(raw), "source": str(target)}
    return {
        "source_files_verified": len(records),
        "unique_payload_sha256": len({v["sha256"] for v in records.values()}),
        "duplicate_payloads": len(records) - len({v["sha256"] for v in records.values()}),
        "identity_conflicts": sorted(set(conflicts)),
        "warehouse_persisted": "NOT_ASSESSED",
        "unreal_imported": "NOT_ASSESSED",
        "world_placed": "NOT_ASSESSED",
        "pie_tested": "NOT_ASSESSED",
        "device_tested": "NOT_ASSESSED",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("receipts", nargs="+", type=Path)
    args = parser.parse_args()
    result = audit(args.receipts)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["identity_conflicts"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
