"""Bounded UE startup observation; this does not certify gameplay or visuals."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import time


FAILURE = re.compile(r"Fatal error:|Assertion failed|Ensure condition failed", re.I)


def read_log(path):
    if not path.exists():
        return ""
    raw = path.read_bytes()
    encoding = "utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
    return raw.decode(encoding, errors="replace")


def required_markers(chapter, mode):
    if mode == "transitions":
        return ["ShireTransitionAudit: sequence=PASS chapters=8 routes=2 disk-save=PASS"]
    if mode == "state":
        return ["ShirePlayableStartup: GameMode ready",
                "ShireStartupGrounding: PASS chapter=P1C03",
                "ShireStateAudit: route-roundtrip=PASS",
                "ShireStateAudit: ring-core=PASS",
                "ShireStateAudit: discovery-core=PASS",
                "ShireStateAudit: progression-core=PASS",
                "ShireStateAudit: knowledge-core=PASS",
                "ShireStateAudit: disk-save-roundtrip=PASS"]
    if chapter is None:
        return ["ShirePlayableStartup: GameMode ready",
                "ShireStartupGrounding: PASS chapter=P1C01",
                "ShirePlayableStartup: chapter=P1C01 route=FrodoMain"]
    return [f"ShireChapterAudit: requested={chapter}",
            f"ShireStartupGrounding: PASS chapter={chapter}",
            f"ShireChapterAudit: loaded={chapter}",
            f"ShireChapterAudit: living-world chapter={chapter}",
            f"ShireChapterAudit: weather chapter={chapter}"]


def missing_markers(text, markers):
    return [marker for marker in markers
            if not re.search(re.escape(marker) + r"(?=$|[\s,;])", text)]


def observe(command, log_path, markers, timeout=45.0, observation=4.0, poll=0.25):
    """Require readiness AND a live observation window, then scan the final log.

    A spontaneous exit (even exit 0) is not a successful persistent game boot.
    Only the termination initiated here after observation may be nonzero.
    Every started direct child is reaped, including on timeout or exception.
    """
    if timeout <= 0 or observation <= 0 or poll <= 0 or timeout <= observation:
        raise ValueError("timeout must exceed a positive observation window; poll must be positive")
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        log_path.unlink()
    except FileNotFoundError:
        pass
    start = time.monotonic()
    ready_at = None
    error = None
    deliberate_stop = False
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    launch_seconds = time.monotonic() - start
    last_poll = time.monotonic()
    max_poll_gap = 0.0
    stop_started = last_poll
    try:
        while True:
            text = read_log(log_path)
            if FAILURE.search(text):
                error = "fatal/assert/ensure in runtime log"
                break
            if process.poll() is not None:
                error = f"runtime exited before observation completed (exit {process.returncode})"
                break
            now = time.monotonic()
            max_poll_gap = max(max_poll_gap, now - last_poll)
            last_poll = now
            # A suspended/starved runner must not turn late readiness into a pass.
            # Check the deadline before accepting a completed observation window.
            if now - start >= timeout:
                error = "runtime readiness/observation timed out"
                break
            if not missing_markers(text, markers) and ready_at is None:
                ready_at = now
            if ready_at is not None and now - ready_at >= observation:
                deliberate_stop = True
                break
            time.sleep(poll)
    finally:
        stop_started = time.monotonic()
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)
        else:
            process.wait()
            if deliberate_stop:
                error = "runtime exited before harness shutdown"
    final_text = read_log(log_path)
    if FAILURE.search(final_text):
        error = "fatal/assert/ensure in final runtime log"
    missing = missing_markers(final_text, markers)
    if missing and error is None:
        error = "required runtime markers missing from final log"
    return {"passed": error is None and deliberate_stop and not missing,
            "error": error, "missing_markers": missing,
            "observation_seconds": observation,
            "elapsed_seconds": round(time.monotonic() - start, 3),
            "timeout_seconds": timeout,
            "launch_seconds": round(launch_seconds, 3),
            "max_poll_gap_seconds": round(max_poll_gap, 3),
            "cleanup_seconds": round(time.monotonic() - stop_started, 3),
            "exit_code": process.returncode,
            "harness_terminated": deliberate_stop, "log": str(log_path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--editor", required=True, type=Path)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--mode", choices=("startup", "chapters", "state", "transitions"), required=True)
    parser.add_argument("--timeout", type=float, default=45)
    parser.add_argument("--observation", type=float, default=4)
    args = parser.parse_args()
    if not args.editor.is_file() or not args.project.is_file():
        parser.error("editor and project must exist")
    if args.observation <= 0 or args.timeout <= args.observation:
        parser.error("timeout must exceed a positive observation window")
    log_dir = args.project.resolve().parent / "Saved" / "Logs"
    chapters = [None] if args.mode in ("startup", "state", "transitions") else [f"P1C{i:02d}" for i in range(1, 9)]
    results = []
    for chapter in chapters:
        name = ("CI-StateAudit" if args.mode == "state" else
                "CI-PlayableStartup" if chapter is None else f"CI-ChapterAudit-{chapter}")
        if args.mode == "transitions":
            name = "CI-TransitionAudit"
        log = log_dir / (name + ".log")
        command = [str(args.editor.resolve()), str(args.project.resolve()),
                   "/Engine/Maps/Templates/Template_Default", "-game", "-nullrhi",
                   "-unattended", "-nop4", "-nosplash", "-NoSound",
                   "-ShireCIRuntimeAudit", f"-abslog={log}"]
        if chapter:
            command.append(f"-AuditChapter={chapter}")
        if args.mode == "state":
            command.append("-AuditState")
        if args.mode == "transitions":
            command.append("-AuditTransitions")
        try:
            result = observe(command, log, required_markers(chapter, args.mode), args.timeout, args.observation)
        except Exception as exc:
            result = {"passed": False, "error": str(exc), "log": str(log)}
        result["chapter"] = chapter or "startup"
        results.append(result)
        print(json.dumps(result), flush=True)
        if not result["passed"]:
            print(read_log(log)[-16000:], flush=True)
            # Do not fail-fast chapter sweeps. One engine build should expose every
            # broken chapter entry point so grounding/streaming defects are fixed as
            # a set instead of being discovered serially across many CI reruns.
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / f"CI-{args.mode}-result.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return 0 if len(results) == len(chapters) and all(r["passed"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
