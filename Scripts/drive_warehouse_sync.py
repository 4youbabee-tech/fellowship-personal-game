#!/usr/bin/env python3
"""Managed Google Drive source ZIP intake. Never imports or deletes unverified sources."""
import argparse
import configparser
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
import zipfile

FOLDER_ID = "1bMZp-XKcQjCj3fYxLoISDtqG9W5aSzyq"
CATEGORIES = {"01_Characters_Animations", "02_Shire_P1C01", "03_WholeGame_28Regions", "04_PBR_Materials"}
WAREHOUSE = Path(r"D:\actions-runner\_warehouse\ShireJourney")
RESERVE = 6 * 1024 ** 3
FILE_ID = re.compile(r"^[A-Za-z0-9_-]{8,200}$")

def require_remote(config, remote):
    cp = configparser.RawConfigParser()
    if not cp.read(str(config), encoding="utf-8"):
        raise RuntimeError("DRIVE_AUTH_MISSING")
    if cp.get(remote, "type", fallback="") != "drive" or cp.get(remote, "root_folder_id", fallback="") != FOLDER_ID:
        raise RuntimeError("DRIVE_REMOTE_NOT_SCOPED_TO_APPROVED_FOLDER")

def run_rclone(binary, config, *args):
    proc = subprocess.run([binary, "--config", str(config), "--ask-password=false", *args],
                          capture_output=True, text=True, timeout=3600)
    if proc.returncode:
        raise RuntimeError("RCLONE_OPERATION_FAILED code=%d operation=%s" % (proc.returncode, args[0]))
    return proc.stdout

def sha(path, kind="sha256"):
    h = hashlib.new(kind)
    with path.open("rb") as f:
        for data in iter(lambda: f.read(1024 * 1024), b""):
            h.update(data)
    return h.hexdigest()

def archive_qc(path):
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        if not 0 < len(members) <= 12000 or sum(z.file_size for z in members) > 3 * 1024 ** 3:
            raise RuntimeError("ARCHIVE_BUDGET_EXCEEDED")
        for z in members:
            n = z.filename.replace("\\", "/")
            if n.startswith("/") or ".." in PurePosixPath(n).parts or ":" in n or "\x00" in n:
                raise RuntimeError("ARCHIVE_UNSAFE_PATH")
            if z.flag_bits & 1 or (z.create_system == 3 and ((z.external_attr >> 16) & 0o170000) == 0o120000):
                raise RuntimeError("ARCHIVE_UNSAFE_MEMBER")
        if archive.testzip() is not None:
            raise RuntimeError("ARCHIVE_BAD_CRC")
        return len(members)

def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".receipt-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(value, out, indent=2, sort_keys=True)
            out.flush()
            os.fsync(out.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)

def inventory(binary, config, remote):
    records = json.loads(run_rclone(binary, config, "lsjson", "--recursive", "--files-only", "--hash", remote + ":"))
    if not isinstance(records, list):
        raise RuntimeError("DRIVE_INVENTORY_INVALID")
    result = []
    for f in records:
        parts = PurePosixPath(f.get("Path", "")).parts
        if len(parts) != 2 or parts[0] not in CATEGORIES or not parts[1].lower().endswith(".zip"):
            continue
        size = f.get("Size")
        md5 = (f.get("Hashes") or {}).get("MD5", "").lower()
        if not FILE_ID.fullmatch(f.get("ID", "")) or type(size) is not int or not 0 < size <= 1024 ** 3:
            raise RuntimeError("DRIVE_OBJECT_ID_OR_SIZE_INVALID")
        if not re.fullmatch(r"[0-9a-f]{32}", md5) or "\\" in f["Path"]:
            raise RuntimeError("DRIVE_OBJECT_CHECKSUM_OR_PATH_INVALID")
        result.append(f)
    return sorted(result, key=lambda x: (x["Path"], x["ID"]))

def ingest(binary, config, remote, root, max_files):
    base = root / "_drive_temp_staging"
    receipts = base / "receipts"
    staged = reused = 0
    items = inventory(binary, config, remote)
    for f in items[:max_files]:
        remote_id, rel, size = f["ID"], f["Path"], f["Size"]
        md5 = f["Hashes"]["MD5"].lower()
        old = list(receipts.glob(remote_id + "-*.json")) if receipts.exists() else []
        if any((lambda rec: rec.get("remote_path") == rel and rec.get("remote_size") == size
                and rec.get("remote_md5") == md5 and Path(rec.get("local_path", "__missing__")).is_file()
                and Path(rec.get("local_path", "__missing__")).resolve().parent == (base / "files" / PurePosixPath(rel).parts[0]).resolve()
                and sha(Path(rec["local_path"])) == rec.get("sha256"))
               (json.loads(p.read_text(encoding="utf-8"))) for p in old):
            reused += 1
            continue
        if shutil.disk_usage(root).free - size < RESERVE:
            raise RuntimeError("PERSISTENT_WAREHOUSE_RESERVE_BELOW_6GIB")
        directory = base / "files" / PurePosixPath(rel).parts[0]
        directory.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(prefix=".drive-", suffix=".partial", dir=str(directory))
        os.close(fd)
        temp = Path(name)
        try:
            run_rclone(binary, config, "copyto", "--retries", "2", remote + ":" + rel, str(temp))
            if temp.stat().st_size != size or sha(temp, "md5") != md5:
                raise RuntimeError("DRIVE_DOWNLOAD_CHECKSUM_MISMATCH")
            count = archive_qc(temp)
            h = sha(temp)
            local = directory / (remote_id + "-" + h[:16] + "-" + PurePosixPath(rel).name)
            if local.exists() and sha(local) != h:
                raise RuntimeError("LOCAL_WAREHOUSE_FILE_COLLISION")
            os.replace(temp, local)
            atomic_json(receipts / (remote_id + "-" + h + ".json"), {
                "remote_id": remote_id, "remote_path": rel, "remote_size": size,
                "remote_md5": md5, "sha256": h, "local_path": str(local),
                "zip_entries": count, "state": "LOCAL_STAGED_NOT_IMPORTED",
                "license_status": "UNVERIFIED_NOT_IMPORTABLE",
                "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })
            staged += 1
            print("DRIVE_STAGED id=%s entries=%d" % (remote_id, count))
        finally:
            temp.unlink(missing_ok=True)
    print("DRIVE_WAREHOUSE_RESULT staged=%d reused=%d discovered=%d" % (staged, reused, len(items)))

def cleanup(binary, config, remote, root, backup):
    base = root / "_drive_temp_staging"
    proofs = base / "accepted_for_cleanup"
    if not backup.is_dir():
        print("DRIVE_CLEANUP_HELD: separate backup unavailable")
        return
    if os.name == "nt" and os.path.splitdrive(str(root.resolve()))[0].lower() == os.path.splitdrive(str(backup.resolve()))[0].lower():
        raise RuntimeError("CLEANUP_BACKUP_MUST_BE_SEPARATE_VOLUME")
    for p in sorted(proofs.glob("*.json")) if proofs.exists() else []:
        proof = json.loads(p.read_text(encoding="utf-8"))
        fid, h = proof.get("remote_id", ""), proof.get("sha256", "")
        if proof.get("disposition") != "IMPORTED_ACCEPTED_SOURCE_RETAINED_IN_BACKUP" or not proof.get("engine_acceptance_evidence"):
            continue
        if not FILE_ID.fullmatch(fid) or not re.fullmatch(r"[0-9a-f]{64}", h):
            continue
        if (base / "deleted_receipts" / (fid + "-" + h + ".json")).exists():
            continue
        receipt = base / "receipts" / (fid + "-" + h + ".json")
        if not receipt.is_file():
            continue
        rec = json.loads(receipt.read_text(encoding="utf-8"))
        local = Path(rec["local_path"]).resolve()
        rel = rec["remote_path"]
        parts = PurePosixPath(rel).parts
        if len(parts) != 2 or parts[0] not in CATEGORIES or not parts[1].lower().endswith(".zip"):
            continue
        if local.parent != (base / "files" / parts[0]).resolve() or not local.is_file() or sha(local) != h:
            continue
        backup_file = (backup / parts[0] / local.name).resolve()
        if backup_file.parent != (backup / parts[0]).resolve() or not backup_file.is_file() or sha(backup_file) != h:
            continue
        obj = json.loads(run_rclone(binary, config, "lsjson", "--stat", "--hash", remote + ":" + rel))
        if obj.get("ID") != fid or obj.get("Size") != rec["remote_size"] or (obj.get("Hashes") or {}).get("MD5", "").lower() != rec["remote_md5"]:
            continue
        atomic_json(base / "deletion_intents" / (fid + "-" + h + ".json"),
                    {"remote_id": fid, "remote_path": rel, "sha256": h, "backup": str(backup_file)})
        run_rclone(binary, config, "deletefile", remote + ":" + rel)
        atomic_json(base / "deleted_receipts" / (fid + "-" + h + ".json"),
                    {"remote_id": fid, "sha256": h, "remote_path": rel, "backup": str(backup_file),
                     "engine_acceptance_evidence": proof["engine_acceptance_evidence"],
                     "deleted_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()})
        print("DRIVE_MANAGED_ARCHIVE_REMOVED id=" + fid)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", required=True, choices=["ingest", "cleanup"])
    p.add_argument("--warehouse-root", type=Path, default=WAREHOUSE)
    p.add_argument("--rclone-config", type=Path, required=True)
    p.add_argument("--rclone-bin", default="rclone")
    p.add_argument("--remote", default="shirecloud")
    p.add_argument("--backup-root", type=Path)
    p.add_argument("--max-files", type=int, default=100)
    a = p.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", a.remote) or not 0 < a.max_files <= 500:
        p.error("unsafe remote or file limit")
    if not a.warehouse_root.is_dir():
        raise RuntimeError("PERSISTENT_WAREHOUSE_MISSING")
    require_remote(a.rclone_config, a.remote)
    if a.mode == "ingest":
        ingest(a.rclone_bin, a.rclone_config, a.remote, a.warehouse_root, a.max_files)
    elif a.backup_root:
        cleanup(a.rclone_bin, a.rclone_config, a.remote, a.warehouse_root, a.backup_root)
    else:
        raise RuntimeError("CLEANUP_BACKUP_ROOT_REQUIRED")

if __name__ == "__main__":
    main()
