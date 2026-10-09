"""Bounded P1C01 material-source provenance gate before UE4 production import.

Only the designated receipt and its named material families are inspected. This
script never downloads, transforms, or synchronously loads Unreal assets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
ID_RE = re.compile(r"SH_[A-Z0-9_]+\Z")
MATERIAL_RE = re.compile(r"MI_Sh_[A-Za-z0-9_]+\Z")
SHA_RE = re.compile(r"[0-9a-f]{64}\Z")
POINTER_RE = re.compile(
    r"version https://git-lfs.github.com/spec/v1\n"
    r"oid sha256:([0-9a-f]{64})\nsize ([0-9]+)\n?\Z"
)
SOURCE_SUBDIR = Path("SourceAssets/Production/Imported/P1C01Materials")


class ReceiptFailure(ValueError):
    pass


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ReceiptFailure(reason)


def digest_file(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def inspect_receipt(repo_root: Path, *, require_hydrated: bool, minimum_materials: int = 17) -> dict:
    source = repo_root / SOURCE_SUBDIR
    receipt_file = source / "P1C01MaterialSourceReceipt.json"
    require(receipt_file.is_file(), "receipt-missing")
    try:
        receipt = json.loads(receipt_file.read_text(encoding="utf-8-sig"))
    except (ValueError, UnicodeError) as exc:
        raise ReceiptFailure("receipt-invalid-json") from exc

    require(receipt.get("schema_version") == 2, "receipt-schema-unexpected")
    items = receipt.get("items")
    require(isinstance(items, list), "receipt-items-invalid")
    require(len(items) >= minimum_materials, f"too-few-qualified-materials count={len(items)} minimum={minimum_materials}")
    require(receipt.get("material_count") == len(items), "receipt-material-count-mismatch")
    require(receipt.get("quarantined_count") == 0, "receipt-has-quarantined-items")
    seen = set()
    hydrated = pointers = normalized_mtls = 0

    for item in items:
        require(isinstance(item, dict), "receipt-item-not-object")
        family = item.get("id", "")
        material = item.get("material_name", "")
        require(isinstance(family, str) and ID_RE.fullmatch(family) is not None, "unsafe-material-id")
        require(family not in seen, f"duplicate-family {family}")
        seen.add(family)
        require(isinstance(material, str) and MATERIAL_RE.fullmatch(material) is not None, f"unsafe-material-name {family}")
        require(item.get("license") == "CC0" and item.get("provider") == "POLY_HAVEN", f"unapproved-provenance {family}")
        require(item.get("state") == "SOURCE_READY_FOR_UE_IMPORT", f"material-not-qualified {family}")
        require(str(item.get("source_url", "")).startswith("https://dl.polyhaven.org/"), f"unapproved-source-url {family}")
        tex_sha = item.get("basecolor_sha256", "")
        mtl_sha = item.get("mtl_sha256", "")
        require(isinstance(tex_sha, str) and SHA_RE.fullmatch(tex_sha) is not None, f"bad-texture-digest {family}")
        require(isinstance(mtl_sha, str) and SHA_RE.fullmatch(mtl_sha) is not None, f"bad-mtl-digest {family}")

        folder = source / family
        tex = folder / f"TX_{family}_BaseColor.png"
        mtl = folder / f"{material}.mtl"
        for path in (tex, mtl):
            require(path.is_file() and not path.is_symlink(), f"qualified-file-missing {family} file={path.name}")
        text = mtl.read_bytes()
        mtl_actual = hashlib.sha256(text).hexdigest()
        if mtl_actual != mtl_sha:
            # Source receipt was generated on Windows before Git's text eol
            # normalization. Only the equivalent CRLF spelling is accepted.
            require(b"\r" not in text, f"mtl-bytes-tampered {family}")
            windows_mtl = text.replace(b"\n", b"\r\n")
            require(hashlib.sha256(windows_mtl).hexdigest() == mtl_sha, f"mtl-hash-mismatch {family}")
            normalized_mtls += 1
        require(f"newmtl {material}".encode() in text.splitlines(), f"mtl-material-mismatch {family}")
        require(f"map_Kd {tex.name}".encode() in text.splitlines(), f"mtl-albedo-mismatch {family}")
        for directive, number in (("Pr", item.get("roughness")), ("Pm", item.get("metallic"))):
            require(isinstance(number, (int, float)) and 0 <= number <= 1, f"mtl-scalar-out-of-range {family}")
            require(f"{directive} {number:.4f}".encode() in text.splitlines(), f"mtl-scalar-mismatch {family}")

        with tex.open("rb") as stream:
            header = stream.read(256)
        if header.startswith(b"version https://git-lfs.github.com/spec/v1"):
            require(not require_hydrated, f"lfs-pointer-not-hydrated {family}")
            try:
                pointer = POINTER_RE.fullmatch(tex.read_text(encoding="ascii"))
            except UnicodeError as exc:
                raise ReceiptFailure(f"invalid-lfs-pointer {family}") from exc
            require(pointer is not None and pointer.group(1) == tex_sha and int(pointer.group(2)) > 8, f"lfs-pointer-oid-mismatch {family}")
            pointers += 1
        else:
            require(header.startswith(PNG_SIGNATURE), f"png-signature-invalid {family}")
            require(digest_file(tex) == tex_sha, f"png-hash-mismatch {family}")
            hydrated += 1

    actual_families = {p.name for p in source.iterdir() if p.is_dir()}
    require(actual_families == seen, f"unlisted-or-missing-material-family registered={len(seen)} actual={len(actual_families)}")
    return {"materials": len(items), "hydrated": hydrated, "pointers": pointers, "mtl_eol_normalized": normalized_mtls}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--require-hydrated", action="store_true")
    parser.add_argument("--min-materials", type=int, default=17)
    args = parser.parse_args()
    try:
        evidence = inspect_receipt(args.root, require_hydrated=args.require_hydrated, minimum_materials=args.min_materials)
    except (ReceiptFailure, OSError) as exc:
        print(f"P1C01_MATERIAL_RECEIPT_QC_FAIL reason={exc}", file=sys.stderr)
        return 1
    print("P1C01_MATERIAL_RECEIPT_QC_PASS " + " ".join(f"{key}={value}" for key, value in evidence.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
