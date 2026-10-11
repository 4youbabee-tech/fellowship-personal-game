#!/usr/bin/env python3
"""Classify repository changes for source-only production while the UE runner is offline."""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from dataclasses import dataclass
from pathlib import PurePosixPath


SOURCE_ONLY_PATTERNS = (
    "Docs/**",
    "Data/OfflineFastProductionQueueV1.json",
    "Data/MaximumSafeProductionModeV1.json",
    "Scripts/offline_production_classifier.py",
    "Scripts/test_offline_production_classifier.py",
    "Data/*Warehouse*.json",
    "Data/*Source*.json",
    "Data/*Prep*.json",
    "Data/*Queue*.json",
    "Data/*Plan*.json",
    "Data/*Receipt*.json",
)

MANUAL_RUNNER_PATTERNS = (
    ".github/workflows/**",
    "Source/**",
    "Config/**",
    "Content/**",
    "Plugins/**",
    "ShireJourney.uproject",
    "**/*.Build.cs",
    "**/*.Target.cs",
)

ASSET_PREP_PATTERNS = (
    "SourceAssets/**",
    "Saved/P1C01NormalizedFBX/**",
    "Scripts/normalize_verified_pbr_blender.py",
    "Scripts/preflight_p1c01_verified_fbx.py",
    "Scripts/p1c01_verified_pbr_bridge.py",
    "Scripts/*blender*.py",
    "Scripts/*fbx*.py",
    "Scripts/*pbr*.py",
)


@dataclass(frozen=True)
class Classification:
    path: str
    bucket: str
    reason: str


def _matches(path: str, patterns: tuple[str, ...]) -> str | None:
    normalized = PurePosixPath(path).as_posix()
    for pattern in patterns:
        if fnmatch.fnmatch(normalized, pattern):
            return pattern
    return None


def classify_path(path: str) -> Classification:
    runner_match = _matches(path, MANUAL_RUNNER_PATTERNS)
    if runner_match:
        return Classification(path, "manual_runner_required", runner_match)

    prep_match = _matches(path, ASSET_PREP_PATTERNS)
    if prep_match:
        return Classification(path, "asset_prep_source_only", prep_match)

    source_match = _matches(path, SOURCE_ONLY_PATTERNS)
    if source_match:
        return Classification(path, "hosted_source_only", source_match)

    return Classification(path, "review_required", "no matching offline production rule")


def classify(paths: list[str]) -> dict[str, object]:
    entries = [classify_path(path) for path in paths if path.strip()]
    buckets: dict[str, list[str]] = {}
    for entry in entries:
        buckets.setdefault(entry.bucket, []).append(entry.path)

    blocked = any(entry.bucket == "manual_runner_required" for entry in entries)
    source_only = bool(entries) and not blocked and all(
        entry.bucket in {"hosted_source_only", "asset_prep_source_only"} for entry in entries
    )

    return {
        "runner_offline_safe": source_only,
        "windows_runner_blocked": blocked,
        "summary": buckets,
        "entries": [entry.__dict__ for entry in entries],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Changed repository paths. Reads stdin when omitted.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a short text verdict.")
    args = parser.parse_args(argv)

    paths = args.paths or [line.strip() for line in sys.stdin if line.strip()]
    result = classify(paths)

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        if result["windows_runner_blocked"]:
            print("OFFLINE_PRODUCTION_BLOCKED_WINDOWS_RUNNER")
        elif result["runner_offline_safe"]:
            print("OFFLINE_PRODUCTION_SOURCE_ONLY_PASS")
        else:
            print("OFFLINE_PRODUCTION_REVIEW_REQUIRED")

    return 2 if result["windows_runner_blocked"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
