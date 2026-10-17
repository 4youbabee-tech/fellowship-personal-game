#!/usr/bin/env python3
"""Acquire one dependency-complete CC0 Poly Haven FBX into the licensed inbox.

The asset id and destination come from the reviewed Shire kit manifest. API
metadata chooses a pinned resolution and direct FBX entry; all sidecars keep
the provider's relative paths and MD5/SHA256 provenance in a receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse
from urllib.request import Request, urlopen

API_ROOT = "https://api.polyhaven.com"
LICENSE_URL = "https://polyhaven.com/license"
MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_TOTAL_BYTES = 128 * 1024 * 1024
USER_AGENT = "ShireJourneyAssetIntake/1.0 (+https://github.com/4youbabee-tech/fellowship-personal-game)"


def _safe_provider_url(url: object) -> str:
    if not isinstance(url, str):
        raise ValueError("POLYHAVEN_DOWNLOAD_URL_MISSING")
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or not (
        parsed.hostname == "polyhaven.com" or parsed.hostname.endswith(".polyhaven.com") or
        parsed.hostname == "polyhaven.org" or parsed.hostname.endswith(".polyhaven.org")
    ):
        raise ValueError("POLYHAVEN_DOWNLOAD_URL_HOST_REJECTED")
    return url


def select_fbx(files: dict, preference: tuple[str, ...] = ("2k", "1k")) -> tuple[str, dict]:
    formats = files.get("fbx") if isinstance(files, dict) else None
    if not isinstance(formats, dict):
        raise ValueError("POLYHAVEN_FBX_FORMAT_UNAVAILABLE")
    for resolution in preference:
        variants = formats.get(resolution)
        candidate = variants.get("fbx") if isinstance(variants, dict) else None
        if isinstance(candidate, dict) and candidate.get("url"):
            return resolution, candidate
    raise ValueError("POLYHAVEN_FBX_PREFERRED_RESOLUTION_UNAVAILABLE")


def _safe_relative_path(value: object) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("POLYHAVEN_INCLUDE_PATH_INVALID")
    relative = PurePosixPath(value)
    if relative.is_absolute() or any(part in ("", ".", "..") for part in relative.parts):
        raise ValueError("POLYHAVEN_INCLUDE_PATH_TRAVERSAL")
    return Path(*relative.parts)


def _fetch_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"POLYHAVEN_API_HTTP_{response.status}:{url}")
        return json.loads(response.read().decode("utf-8"))


def _download(url: str, target: Path, expected_md5: object) -> dict:
    url = _safe_provider_url(url)
    if expected_md5 is not None and not re.fullmatch(r"[0-9a-fA-F]{32}", str(expected_md5)):
        raise ValueError("POLYHAVEN_MD5_FORMAT_INVALID")
    request = Request(url, headers={"User-Agent": USER_AGENT})
    target.parent.mkdir(parents=True, exist_ok=True)
    md5 = hashlib.md5()
    sha = hashlib.sha256()
    size = 0
    with urlopen(request, timeout=60) as response, tempfile.NamedTemporaryFile(
        dir=target.parent, prefix=".shire-download-", delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)
        try:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_FILE_BYTES:
                    raise ValueError("POLYHAVEN_FILE_SIZE_LIMIT_EXCEEDED")
                md5.update(chunk)
                sha.update(chunk)
                temporary.write(chunk)
            if size == 0:
                raise ValueError("POLYHAVEN_EMPTY_DOWNLOAD")
            if expected_md5 is not None and md5.hexdigest().lower() != str(expected_md5).lower():
                raise ValueError("POLYHAVEN_MD5_MISMATCH")
            os.replace(temporary_path, target)
        except Exception:
            temporary_path.unlink(missing_ok=True)
            raise
    return {"path": str(target), "bytes": size, "md5": md5.hexdigest(), "sha256": sha.hexdigest()}


def acquire(asset_id: str, out: Path, primary_name: str,
            get_json=_fetch_json, download=_download) -> dict:
    if not re.fullmatch(r"[a-z0-9_]+", asset_id):
        raise ValueError("POLYHAVEN_ASSET_ID_INVALID")
    if not re.fullmatch(r"[A-Za-z0-9_-]+\.fbx", primary_name):
        raise ValueError("POLYHAVEN_PRIMARY_FILENAME_INVALID")
    out = out.resolve()
    if out.exists() and any(out.iterdir()):
        raise RuntimeError("POLYHAVEN_INTAKE_OUTPUT_MUST_BE_NEW_OR_EMPTY")
    out.mkdir(parents=True, exist_ok=True)
    info = get_json(f"{API_ROOT}/info/{asset_id}")
    if not isinstance(info, dict) or info.get("type") != 2:
        raise ValueError("POLYHAVEN_ASSET_NOT_A_MODEL")
    file_tree = get_json(f"{API_ROOT}/files/{asset_id}")
    resolution, model = select_fbx(file_tree)
    records = []
    model_record = download(_safe_provider_url(model["url"]), out / primary_name, model.get("md5"))
    model_record.update({"path": primary_name, "provider_path": f"fbx/{resolution}/fbx", "role": "mesh"})
    records.append(model_record)
    include = model.get("include", {})
    if not isinstance(include, dict):
        raise ValueError("POLYHAVEN_INCLUDE_TREE_INVALID")
    total = model_record["bytes"]
    for relative_name, item in sorted(include.items()):
        relative = _safe_relative_path(relative_name)
        if not isinstance(item, dict):
            raise ValueError("POLYHAVEN_INCLUDE_ENTRY_INVALID")
        target = out / relative
        if out not in target.resolve().parents:
            raise ValueError("POLYHAVEN_INCLUDE_PATH_ESCAPES_OUTPUT")
        record = download(_safe_provider_url(item.get("url")), target, item.get("md5"))
        total += record["bytes"]
        if total > MAX_TOTAL_BYTES:
            raise ValueError("POLYHAVEN_TOTAL_SIZE_LIMIT_EXCEEDED")
        record.update({"path": relative.as_posix(), "provider_path": relative_name, "role": "dependency"})
        records.append(record)
    creator = ", ".join(sorted(info.get("authors", {}).keys())) if isinstance(info.get("authors"), dict) else "Poly Haven"
    receipt = {
        "schema_version": 1,
        "status": "CC0_POLYHAVEN_FBX_SOURCE_ACQUIRED",
        "asset_id": asset_id,
        "title": info.get("name", asset_id),
        "provider": "Poly Haven",
        "creator": creator,
        "source_url": f"https://polyhaven.com/a/{asset_id}",
        "api_info_url": f"{API_ROOT}/info/{asset_id}",
        "api_files_url": f"{API_ROOT}/files/{asset_id}",
        "files_hash": info.get("files_hash"),
        "license": "CC0",
        "license_url": LICENSE_URL,
        "format": "FBX",
        "resolution": resolution,
        "provider_dimensions_mm": info.get("dimensions"),
        "provider_triangles": info.get("polycount"),
        "files": records,
        "total_bytes": total,
    }
    (out / "source_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"POLYHAVEN_SOURCE_ACQUIRED id={asset_id} resolution={resolution} files={len(records)} bytes={total}", flush=True)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset-id", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--primary-name", default="painted_wooden_bench.fbx")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else None)
    acquire(args.asset_id, args.out, args.primary_name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
