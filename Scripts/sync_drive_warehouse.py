#!/usr/bin/env python3
"""Fail-closed, idempotent private Drive ZIP intake to persistent Windows warehouse."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT_FOLDERS = ("01_Characters_Animations", "02_Shire_P1C01", "03_WholeGame_28Regions", "04_PBR_Materials")

def call(rclone, *args):
    p = subprocess.run([rclone, *args], capture_output=True, text=True, timeout=120)
    if p.returncode:
        raise RuntimeError("rclone operation failed: " + " ".join(args[:2]) + " " + p.stderr[-400:])
    return p.stdout

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def safe_remote_name(name):
    if not name or name in (".", "..") or "/" in name or "\\" in name or ":" in name:
        raise ValueError("unsafe Drive item name")
    return name

def inventory(rclone, remote):
    found = []
    for folder in ROOT_FOLDERS:
        output = call(rclone, "lsjson", "--files-only", remote + "/" + folder)
        for item in json.loads(output):
            name = safe_remote_name(item["Name"])
            if not name.lower().endswith(".zip"):
                continue
            size = int(item.get("Size", -1))
            if size <= 0 or size > 4 * 1024**3:
                raise ValueError("invalid Drive archive size")
            found.append((folder, name, size, item.get("Hashes", {}).get("MD5")))
    return found

def ingest(rclone, remote, root, min_free_gb=6):
    import shutil
    root.mkdir(parents=True, exist_ok=True)
    archive_dir = root / "_drive_intake" / "archives"
    receipts = root / "_drive_intake" / "receipts"
    archive_dir.mkdir(parents=True, exist_ok=True)
    receipts.mkdir(parents=True, exist_ok=True)
    # Lock is exclusive and local to the persistent intake lane, not the UE checkout.
    lock = root / "_drive_intake" / "sync.lock"
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        with os.fdopen(fd, "w") as f:
            f.write(str(os.getpid()))
        items = inventory(rclone, remote)
        for folder, name, size, md5 in items:
            destination = archive_dir / folder / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            receipt_path = receipts / folder / (name + ".json")
            receipt_path.parent.mkdir(parents=True, exist_ok=True)
            existing = None
            if receipt_path.exists():
                existing = json.loads(receipt_path.read_text(encoding="utf-8"))
            if (existing and destination.is_file() and destination.stat().st_size == size
                    and existing.get("sha256") == sha256(destination)
                    and existing.get("remote_md5") == md5):
                print("DRIVE_INTAKE_REUSED", folder, name, flush=True)
                continue
            free = shutil.disk_usage(root).free
            if free < int(min_free_gb * 1024**3) + size * 2:
                raise RuntimeError("WAREHOUSE_DISK_RESERVE_LOW")
            temp = destination.with_suffix(destination.suffix + ".partial")
            try:
                call(rclone, "copyto", "--retries", "3", "--low-level-retries", "5",
                     remote + "/" + folder + "/" + name, str(temp))
                if temp.stat().st_size != size:
                    raise RuntimeError("REMOTE_SIZE_MISMATCH")
                if md5:
                    h = hashlib.md5()
                    with open(temp, "rb") as f:
                        for part in iter(lambda: f.read(1024 * 1024), b""):
                            h.update(part)
                    if h.hexdigest().lower() != md5.lower():
                        raise RuntimeError("REMOTE_MD5_MISMATCH")
                with zipfile.ZipFile(temp) as z:
                    bad = z.testzip()
                    if bad:
                        raise RuntimeError("ZIP_CRC_FAILED")
                    for entry in z.infolist():
                        parts = Path(entry.filename.replace("\\", "/")).parts
                        if entry.filename.startswith("/") or ".." in parts or ":" in entry.filename:
                            raise RuntimeError("ZIP_UNSAFE_ENTRY")
                digest = sha256(temp)
                os.replace(temp, destination)
                receipt = {"schema_version": 1, "source_folder": folder, "file": name,
                           "remote_md5": md5, "size": size, "sha256": digest,
                           "ingested_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                           "storage": str(destination), "import_accepted": False,
                           "backup_verified": False, "drive_delete_permitted": False}
                staged = receipt_path.with_suffix(".json.tmp")
                staged.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
                os.replace(staged, receipt_path)
                print("DRIVE_INTAKE_VERIFIED", folder, name, digest, flush=True)
            finally:
                if temp.exists():
                    temp.unlink()
        print("DRIVE_INTAKE_COMPLETE count=" + str(len(items)), flush=True)
    finally:
        lock.unlink(missing_ok=True)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--rclone", default="rclone")
    p.add_argument("--remote", required=True, help="Preconfigured private rclone remote path")
    p.add_argument("--warehouse", type=Path, required=True)
    args = p.parse_args()
    if ":" not in args.remote:
        p.error("Drive remote must be rclone remote:path")
    ingest(args.rclone, args.remote.rstrip("/"), args.warehouse)

if __name__ == "__main__":
    main()
