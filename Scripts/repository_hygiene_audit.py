#!/usr/bin/env python3
"""Repository hygiene audit for the Fellowship UE4.27 project.

This script is deliberately non-destructive. It catches tracked build/editor debris,
checks the flat runtime source manifest, and reports duplicate production source
content without deleting anything.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "Source" / "ShireJourney"
ARCH_PATH = ROOT / "Data" / "SourceArchitecturePlan.json"
CHECKPOINTS_PATH = ROOT / "Docs" / "CHECKPOINTS.md"
PRODUCTION_ROOT = ROOT / "SourceAssets" / "Production"

TRACKED_FORBIDDEN_PREFIXES = (
    "Binaries/",
    "DerivedDataCache/",
    "Intermediate/",
    "Saved/",
    ".vs/",
    ".vscode/",
    "Content/Production/",
)
TRACKED_FORBIDDEN_SUFFIXES = (
    ".log",
    ".tmp",
    ".bak",
    ".user",
    ".userprefs",
    ".VC.db",
)

errors: list[str] = []
warnings: list[str] = []


def tracked_files() -> list[str]:
    try:
        output = subprocess.check_output(
            ["git", "ls-files"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.STDOUT,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        errors.append(f"Unable to enumerate tracked files with git: {exc}")
        return []
    return [line.strip().replace("\\", "/") for line in output.splitlines() if line.strip()]


tracked = tracked_files()

for path in tracked:
    if path.startswith(TRACKED_FORBIDDEN_PREFIXES):
        errors.append(f"Tracked generated/editor path is forbidden: {path}")
    if path.endswith(TRACKED_FORBIDDEN_SUFFIXES):
        errors.append(f"Tracked developer debris is forbidden: {path}")

# Keep the architecture manifest exact for runtime C++/header/build files.
try:
    architecture = json.loads(ARCH_PATH.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    errors.append(f"Unable to read SourceArchitecturePlan.json: {exc}")
    architecture = {}

manifest_paths = {
    str(row.get("current_path") or "").replace("\\", "/")
    for row in architecture.get("files", [])
    if isinstance(row, dict)
}
actual_source_paths = {
    path.replace("\\", "/")
    for path in tracked
    if path.startswith("Source/ShireJourney/")
    and (
        path.endswith(".h")
        or path.endswith(".cpp")
        or path.endswith(".cs")
    )
}
missing_from_manifest = sorted(actual_source_paths - manifest_paths)
stale_manifest_rows = sorted(manifest_paths - actual_source_paths)
for path in missing_from_manifest:
    errors.append(f"SourceArchitecturePlan missing runtime source: {path}")
for path in stale_manifest_rows:
    errors.append(f"SourceArchitecturePlan references missing runtime source: {path}")

flat_entries = [
    p for p in SOURCE_ROOT.iterdir()
    if p.is_file() and p.suffix.lower() in {".h", ".cpp", ".cs"}
]
if len(flat_entries) > 60:
    errors.append(
        f"Flat Source/ShireJourney root grew to {len(flat_entries)} runtime files; "
        "run the planned domain migration instead of adding more root-level files."
    )
elif len(flat_entries) >= 54:
    warnings.append(
        f"Flat Source/ShireJourney root is near the migration threshold: {len(flat_entries)} runtime files."
    )

# Checkpoint history is useful, but the active file should not grow without bound.
try:
    checkpoint_text = CHECKPOINTS_PATH.read_text(encoding="utf-8")
    checkpoint_count = sum(
        1 for line in checkpoint_text.splitlines()
        if line.startswith("## CP") and line[5:6].isdigit()
    )
    if checkpoint_count > 72:
        errors.append(
            f"Docs/CHECKPOINTS.md has {checkpoint_count} checkpoint headings; archive older history."
        )
    elif checkpoint_count >= 60:
        warnings.append(
            f"Docs/CHECKPOINTS.md has {checkpoint_count} checkpoint headings; archive split is due."
        )
except OSError as exc:
    errors.append(f"Unable to read Docs/CHECKPOINTS.md: {exc}")
    checkpoint_count = 0

# Duplicate production sources are reported only. Relative OBJ->MTL relationships
# mean identical files are not necessarily redundant.
hash_groups: dict[tuple[int, str], list[str]] = defaultdict(list)
production_counts: dict[str, int] = defaultdict(int)
if PRODUCTION_ROOT.exists():
    for path in PRODUCTION_ROOT.rglob("*"):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        production_counts[suffix or "<none>"] += 1
        try:
            data = path.read_bytes()
        except OSError as exc:
            warnings.append(f"Could not hash production source {path.relative_to(ROOT)}: {exc}")
            continue
        digest = hashlib.sha256(data).hexdigest()
        hash_groups[(len(data), digest)].append(path.relative_to(ROOT).as_posix())

duplicate_groups = [
    paths for paths in hash_groups.values()
    if len(paths) > 1
]

print("REPOSITORY HYGIENE AUDIT")
print(f"- tracked files: {len(tracked)}")
print(f"- runtime source files in flat module root: {len(flat_entries)}")
print(f"- source architecture manifest entries: {len(manifest_paths)}")
print(f"- checkpoint headings: {checkpoint_count}")
print(
    "- production sources: "
    + ", ".join(
        f"{suffix or '<none>'}={count}"
        for suffix, count in sorted(production_counts.items())
    )
)
print(f"- duplicate production-content groups: {len(duplicate_groups)}")

for group in sorted(duplicate_groups, key=lambda rows: (-len(rows), rows[0]))[:12]:
    print("  duplicate: " + " | ".join(group))

for warning in warnings:
    print(f"WARNING: {warning}")

if errors:
    print(f"REPOSITORY HYGIENE FAILED: {len(errors)} error(s)")
    for error in errors:
        print(f"ERROR: {error}")
    sys.exit(1)

print("REPOSITORY HYGIENE PASSED")
