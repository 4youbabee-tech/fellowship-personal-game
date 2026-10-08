"""Fail-closed same-HEAD Unreal CI stage receipts for the persistent Windows runner.

These receipts are cache hints, never project acceptance. A stage is reusable only
when its original inputs, materialized output bytes and predecessor receipt match.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SCHEMA = 1
ORDER = ("import", "core", "package")
SHA40 = re.compile(r"[0-9a-f]{40}\Z")
MODES = ("startup", "chapters", "state", "transitions", "faults", "pending", "edges")
FRODO_FILES = (
    "Content/Production/Characters/Rigs/FRODO/SK_FRODO.uasset",
    "Content/Production/Characters/Rigs/FRODO/SK_FRODO_Skeleton.uasset",
    "Content/Production/Characters/Animations/FRODO/A_Frodo_Idle.uasset",
    "Content/Production/Characters/Animations/FRODO/A_Frodo_Walk.uasset",
    "Content/Production/Characters/Animations/FRODO/A_Frodo_Run.uasset",
)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical_json(data: dict) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")


def stamp_root(root: Path, head: str) -> Path:
    if not SHA40.fullmatch(head):
        raise ValueError("exact 40-character lowercase commit SHA required")
    return root / "Saved" / "CIResume" / head


def _stage_file(root: Path, head: str, stage: str) -> Path:
    if stage not in ORDER:
        raise ValueError("invalid stage")
    return stamp_root(root, head) / (stage + ".json")


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _required_files(root: Path, head: str, stage: str) -> list[Path]:
    files: list[Path] = []
    if stage == "import":
        dlls = sorted((root / "Binaries" / "Win64").glob("*ShireJourney*.dll"))
        if not dlls:
            raise ValueError("compiled UE4 ShireJourney binary missing")
        files.extend(dlls)
        assets = sorted((root / "Content" / "Production").rglob("*.uasset"))
        if len(assets) < len(FRODO_FILES):
            raise ValueError("production asset import not present")
        for relative in FRODO_FILES:
            if not (root / relative).is_file():
                raise ValueError("required Frodo production asset missing: " + relative)
        files.extend(assets)
        for name, marker in (
            ("CI-ProductionAssetImport.log", "0 failures"),
            ("CI-FrodoPersistentRuntimeImport.log", "UE4_ANIMATION_IMPORT_TECHNICAL_PASS clips=3 bones=48"),
        ):
            path = root / "Saved" / "Logs" / name
            if not path.is_file() or marker not in path.read_text(encoding="utf-8-sig", errors="replace"):
                raise ValueError("required import log marker missing: " + name)
            files.append(path)
    elif stage == "core":
        images = root / "Saved" / "Automation" / "P1C01VisualCapture" / head[:12]
        pngs = sorted(images.glob("*.png"))
        logs = sorted(images.glob("*.log"))
        if len(pngs) != 7 or len(logs) != 7:
            raise ValueError("seven-shot visual capture evidence missing")
        files.extend(pngs + logs)
        qa = root / "Saved" / "Logs" / "CI-ProjectAutomation.log"
        if not qa.is_file() or not qa.stat().st_size:
            raise ValueError("Automation Framework log missing")
        files.append(qa)
        reports = root / "Saved" / "Logs"
        for mode in MODES:
            path = reports / ("CI-" + mode + "-result.json")
            if not path.is_file():
                raise ValueError("runtime report missing: " + mode)
            rows = _read_json(path)
            if not isinstance(rows, list) or not rows or any(not isinstance(r, dict) or r.get("passed") is not True for r in rows):
                raise ValueError("runtime report is not fully passing: " + mode)
            if mode == "chapters" and len(rows) != 8:
                raise ValueError("chapter audit incomplete")
            files.append(path)
    elif stage == "package":
        package = root / "Saved" / "W00Package" / "WindowsNoEditor"
        exe = package / "ShireJourney.exe"
        paks = sorted(package.rglob("*.pak"))
        report = root / "Saved" / "Logs" / "CI-W00-PackagedData.json"
        if not exe.is_file() or not paks or not report.is_file():
            raise ValueError("packaged executable, pak or runtime data report missing")
        data = _read_json(report)
        if not isinstance(data, dict) or data.get("expected_count") != 37 or data.get("verified_count") != 37 or data.get("missing") or data.get("invalid_json"):
            raise ValueError("packaged runtime data verification incomplete")
        files.extend([exe, report] + paks)
    else:
        raise ValueError("unknown stage")
    for path in files:
        if not path.is_file() or not path.stat().st_size:
            raise ValueError("empty or missing stage output: " + str(path))
    return sorted(set(files))


def _engine(root: Path, editor: Path) -> dict:
    # Protects against reusing outputs after the local UE4 engine installation changes.
    if not editor.is_file():
        raise ValueError("UE4Editor-Cmd.exe absent")
    st = editor.stat()
    return {"path": str(editor.resolve()), "size": st.st_size, "mtime_ns": st.st_mtime_ns}


def _file_records(root: Path, paths: list[Path]) -> list[dict]:
    records = []
    for path in paths:
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise ValueError("symlink proof is not permitted: " + relative)
        records.append({"path": relative, "size": path.stat().st_size, "sha256": digest(path)})
    return records


def verify(root: Path, head: str, stage: str, editor: Path) -> tuple[bool, str]:
    """Verify one stage and all its dependencies. On any doubt, rerun the stage."""
    try:
        if stage not in ORDER:
            raise ValueError("unknown stage")
        filepath = _stage_file(root, head, stage)
        doc = _read_json(filepath)
        if doc.get("schema") != SCHEMA or doc.get("head") != head or doc.get("stage") != stage:
            raise ValueError("stage identity does not match exact HEAD")
        if doc.get("engine") != _engine(root, editor):
            raise ValueError("UE4 engine identity changed")
        previous = ORDER[ORDER.index(stage) - 1] if stage != "import" else None
        if previous:
            ok, reason = verify(root, head, previous, editor)
            if not ok:
                raise ValueError("predecessor proof invalid: " + reason)
            if doc.get("predecessor_sha256") != digest(_stage_file(root, head, previous)):
                raise ValueError("predecessor proof changed")
        files = doc.get("files")
        if not isinstance(files, list) or not files:
            raise ValueError("receipt has no outputs")
        actual = _file_records(root, _required_files(root, head, stage))
        if files != actual:
            raise ValueError("stage output file bytes or inventory changed")
        return True, "same-head-artifacts-verified"
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        return False, str(exc)


def record(root: Path, head: str, stage: str, editor: Path) -> Path:
    root = root.resolve()
    destination = _stage_file(root, head, stage)
    predecessor = ORDER[ORDER.index(stage) - 1] if stage != "import" else None
    if predecessor:
        ok, reason = verify(root, head, predecessor, editor)
        if not ok:
            raise ValueError("cannot record without passing predecessor: " + reason)
    doc = {
        "schema": SCHEMA,
        "head": head,
        "stage": stage,
        "engine": _engine(root, editor),
        "predecessor_sha256": digest(_stage_file(root, head, predecessor)) if predecessor else None,
        "files": _file_records(root, _required_files(root, head, stage)),
        "acceptance": "MACHINE_STAGE_ONLY_NOT_PIE_DEVICE_VISUAL_GATE_6_7",
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_suffix(".tmp")
    temp.write_bytes(canonical_json(doc) + b"\n")
    os.replace(temp, destination)
    return destination


def probe(root: Path, head: str, editor: Path) -> dict[str, bool]:
    proof = {name: False for name in ORDER}
    for stage in ORDER:
        accepted, reason = verify(root, head, stage, editor)
        proof[stage] = accepted
        print(f"SHIRE_STAGE_RESUME_PROBE stage={stage} reuse={str(accepted).lower()} reason={reason}", flush=True)
    return proof


def _current_git_sha(root: Path) -> str:
    proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, timeout=15)
    if proc.returncode:
        raise ValueError("cannot validate exact HEAD")
    return proc.stdout.strip().lower()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("probe", "record"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--stage", choices=ORDER)
    parser.add_argument("--editor", type=Path, default=Path(r"C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\Win64\UE4Editor-Cmd.exe"))
    args = parser.parse_args()
    root = args.root.resolve()
    head = args.head.strip().lower()
    if not SHA40.fullmatch(head) or _current_git_sha(root) != head:
        print("SHIRE_STAGE_RESUME_DENIED reason=exact-checkout-mismatch", flush=True)
        return 2
    if args.action == "probe":
        reuse = probe(root, head, args.editor)
        env_path = os.environ.get("GITHUB_ENV")
        if env_path:
            with open(env_path, "a", encoding="utf-8") as env_file:
                for stage in ORDER:
                    env_file.write(f"SHIRE_RESUME_{stage.upper()}={str(reuse[stage]).lower()}\n")
        return 0
    if not args.stage:
        parser.error("record requires --stage")
    try:
        destination = record(root, head, args.stage, args.editor)
        print(f"SHIRE_STAGE_RESUME_RECORDED stage={args.stage} sha={head} receipt={destination}", flush=True)
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("SHIRE_STAGE_RESUME_RECORD_UNAVAILABLE stage=" + args.stage + " reason=" + str(exc), flush=True)
        # Optional optimization only. Do not turn proven game success into a red CI run.
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
