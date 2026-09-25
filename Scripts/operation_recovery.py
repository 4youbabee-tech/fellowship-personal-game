#!/usr/bin/env python3
"""Durable operational checkpoint / anti-stuck state for long project tasks.

A completed step on the same exact target SHA is reusable. A running step that
outlives its declared timeout is marked STUCK and forces an audit before the
operation can be trusted again. This is operational evidence only; it never
promotes PIE/device/visual acceptance.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load(path: Path) -> dict:
    if not path.exists():
        return {"schema_version": 1, "operations": {}, "history": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    os.close(fd)
    Path(tmp).write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def opkey(operation: str, sha: str) -> str:
    return operation + "@" + sha


def cmd_begin(args) -> int:
    path = Path(args.state)
    state = load(path)
    key = opkey(args.operation, args.target_sha)
    op = state["operations"].setdefault(
        key,
        {
            "operation": args.operation,
            "target_sha": args.target_sha,
            "steps": {},
            "last_confirmed_step": None,
            "audit_required": False,
        },
    )
    step = op["steps"].get(args.step)
    if step and step.get("status") == "COMPLETED":
        print(
            "RECOVERY_SKIP_COMPLETED operation=%s step=%s sha=%s"
            % (args.operation, args.step, args.target_sha)
        )
        return 0
    if step and step.get("status") == "RUNNING":
        elapsed = (datetime.now(timezone.utc) - parse_time(step["started_at"])).total_seconds()
        timeout = int(step.get("timeout_seconds") or args.timeout_seconds)
        if elapsed > timeout:
            step["status"] = "STUCK"
            step["detected_stuck_at"] = now_iso()
            step["elapsed_seconds"] = int(elapsed)
            op["audit_required"] = True
            op["stuck_step"] = args.step
            save(path, state)
            print(
                "RECOVERY_STUCK_DETECTED operation=%s step=%s elapsed=%s timeout=%s recheck_required=true"
                % (args.operation, args.step, int(elapsed), timeout)
            )
            return 2
        print(
            "RECOVERY_ALREADY_RUNNING operation=%s step=%s elapsed=%s timeout=%s"
            % (args.operation, args.step, int(elapsed), timeout)
        )
        return 3
    op["steps"][args.step] = {
        "status": "RUNNING",
        "started_at": now_iso(),
        "timeout_seconds": args.timeout_seconds,
        "attempt": int((step or {}).get("attempt", 0)) + 1,
    }
    op["current_step"] = args.step
    save(path, state)
    print(
        "RECOVERY_BEGIN operation=%s step=%s sha=%s timeout=%s"
        % (args.operation, args.step, args.target_sha, args.timeout_seconds)
    )
    return 0


def cmd_complete(args) -> int:
    path = Path(args.state)
    state = load(path)
    key = opkey(args.operation, args.target_sha)
    op = state["operations"].get(key)
    if not op or args.step not in op["steps"]:
        print("RECOVERY_ERROR no_started_step", file=sys.stderr)
        return 4
    step = op["steps"][args.step]
    if step.get("status") == "COMPLETED":
        print("RECOVERY_ALREADY_COMPLETED operation=%s step=%s" % (args.operation, args.step))
        return 0
    step["status"] = "COMPLETED"
    step["completed_at"] = now_iso()
    step["evidence"] = args.evidence or ""
    op["last_confirmed_step"] = args.step
    op["current_step"] = None
    if op.get("stuck_step") == args.step:
        op.pop("stuck_step", None)
    save(path, state)
    print("RECOVERY_COMPLETE operation=%s step=%s" % (args.operation, args.step))
    return 0


def cmd_fail(args) -> int:
    path = Path(args.state)
    state = load(path)
    key = opkey(args.operation, args.target_sha)
    op = state["operations"].setdefault(
        key,
        {
            "operation": args.operation,
            "target_sha": args.target_sha,
            "steps": {},
            "last_confirmed_step": None,
            "audit_required": False,
        },
    )
    step = op["steps"].setdefault(
        args.step, {"started_at": now_iso(), "timeout_seconds": 0, "attempt": 1}
    )
    step["status"] = "FAILED"
    step["failed_at"] = now_iso()
    step["reason"] = args.reason
    op["audit_required"] = True
    op["failed_step"] = args.step
    op["current_step"] = None
    save(path, state)
    print(
        "RECOVERY_FAIL operation=%s step=%s recheck_required=true reason=%s"
        % (args.operation, args.step, args.reason)
    )
    return 0


def cmd_audit_clear(args) -> int:
    path = Path(args.state)
    state = load(path)
    key = opkey(args.operation, args.target_sha)
    op = state["operations"].get(key)
    if not op:
        print("RECOVERY_ERROR unknown_operation", file=sys.stderr)
        return 4
    op["audit_required"] = False
    op["audit_cleared_at"] = now_iso()
    op["audit_evidence"] = args.evidence
    save(path, state)
    print("RECOVERY_AUDIT_CLEAR operation=%s sha=%s" % (args.operation, args.target_sha))
    return 0


def cmd_status(args) -> int:
    state = load(Path(args.state))
    key = opkey(args.operation, args.target_sha)
    op = state["operations"].get(key)
    if not op:
        print(json.dumps({"exists": False, "operation": args.operation, "target_sha": args.target_sha}))
        return 0
    print(json.dumps({"exists": True, **op}, indent=2, sort_keys=True))
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True)
    sub = parser.add_subparsers(dest="cmd", required=True)

    begin = sub.add_parser("begin")
    begin.add_argument("--operation", required=True)
    begin.add_argument("--target-sha", required=True)
    begin.add_argument("--step", required=True)
    begin.add_argument("--timeout-seconds", type=int, required=True)
    begin.set_defaults(func=cmd_begin)

    complete = sub.add_parser("complete")
    complete.add_argument("--operation", required=True)
    complete.add_argument("--target-sha", required=True)
    complete.add_argument("--step", required=True)
    complete.add_argument("--evidence", default="")
    complete.set_defaults(func=cmd_complete)

    fail = sub.add_parser("fail")
    fail.add_argument("--operation", required=True)
    fail.add_argument("--target-sha", required=True)
    fail.add_argument("--step", required=True)
    fail.add_argument("--reason", required=True)
    fail.set_defaults(func=cmd_fail)

    audit_clear = sub.add_parser("audit-clear")
    audit_clear.add_argument("--operation", required=True)
    audit_clear.add_argument("--target-sha", required=True)
    audit_clear.add_argument("--evidence", required=True)
    audit_clear.set_defaults(func=cmd_audit_clear)

    status = sub.add_parser("status")
    status.add_argument("--operation", required=True)
    status.add_argument("--target-sha", required=True)
    status.set_defaults(func=cmd_status)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
