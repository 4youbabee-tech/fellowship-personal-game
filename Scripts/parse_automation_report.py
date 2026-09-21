#!/usr/bin/env python3
"""Fail closed when the Unreal Automation report is missing, incomplete, or contains failed required tests."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

PASS_STATES = {"success", "succeeded", "passed", "pass"}
FAIL_STATES = {"fail", "failed", "failure", "error", "notrun", "not_run", "skipped"}

def iter_dicts(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_dicts(child)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--required-prefix", required=True)
    args = parser.parse_args()

    candidates = sorted(args.report.rglob("index.json"))
    if not candidates:
        print(f"ERROR: Unreal Automation report index.json missing under {args.report}")
        return 2

    data = json.loads(candidates[-1].read_text(encoding="utf-8-sig"))
    matched = []
    failed = []

    for row in iter_dicts(data):
        name = str(row.get("fullTestPath") or row.get("FullTestPath") or
                   row.get("testDisplayName") or row.get("TestDisplayName") or "")
        if not name.startswith(args.required_prefix):
            continue
        state = str(row.get("state") or row.get("State") or "").strip().lower()
        if not state:
            continue
        matched.append((name, state))
        errors = row.get("errors", row.get("Errors", 0))
        error_count = errors if isinstance(errors, int) else len(errors) if isinstance(errors, list) else 0
        if state in FAIL_STATES or state not in PASS_STATES or error_count > 0:
            failed.append((name, state, error_count))

    if not matched:
        print(f"ERROR: no completed tests found for prefix {args.required_prefix}")
        return 3

    for name, state in matched:
        print(f"AUTOMATION_RESULT name={name} state={state}")

    if failed:
        for name, state, errors in failed:
            print(f"ERROR: automation failed name={name} state={state} errors={errors}")
        return 4

    print(f"AUTOMATION_SUITE_PASS prefix={args.required_prefix} tests={len(matched)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
