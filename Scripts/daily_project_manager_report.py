#!/usr/bin/env python3
"""Generate the repository-native daily Shire Journey project-manager report."""
from __future__ import annotations
import json
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOV = json.loads((ROOT / "Data" / "ProjectGovernor.json").read_text(encoding="utf-8"))
WAVES = json.loads((ROOT / "Data" / "CompletionWaveMapV1.json").read_text(encoding="utf-8"))

daily = GOV.get("daily_progress_reporting", {})
current = int(daily.get("current_planning_percent", WAVES.get("baseline", {}).get("planning_completion_percent", 40)))
previous = int(daily.get("previous_planning_percent", current))
delta = current - previous
focus = GOV.get("current_focus", {})
gate = GOV.get("active_gate", {})
handoff = GOV.get("session_handoff", {})

now = datetime.now(timezone.utc)
since = now - timedelta(hours=24)

def git_lines(*args: str) -> list[str]:
    try:
        p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False)
    except OSError:
        return []
    if p.returncode != 0:
        return []
    return [line.strip() for line in p.stdout.splitlines() if line.strip()]

recent = git_lines("log", f"--since={since.isoformat()}", "--pretty=%h %s", "--no-merges")
recent_merges = git_lines("log", f"--since={since.isoformat()}", "--pretty=%h %s", "--merges")
head = (git_lines("rev-parse", "HEAD") or ["UNKNOWN"])[0]

wave = None
for item in WAVES.get("waves", []):
    if int(item.get("from_percent", -1)) <= current < int(item.get("to_percent", 101)):
        wave = item
        break
if wave is None and current >= 100 and WAVES.get("waves"):
    wave = WAVES["waves"][-1]

next_unlock = "No higher wave registered."
if wave:
    next_unlock = f"{wave.get('to_percent')}% after: " + "; ".join(wave.get("exit", [])[:4])

lines = [
    "# Shire Journey — Daily Project Manager Report",
    "",
    f"- Generated UTC: {now.strftime('%Y-%m-%d %H:%M')}",
    f"- Repository head observed: `{head}`",
    f"- Planning / production completion: **{current}%**",
    f"- 24h planning delta: **{delta:+d} percentage points**",
    f"- Active lane: **{focus.get('production_lane', 'UNKNOWN')}**",
    f"- Active gate: **{gate.get('id', 'UNKNOWN')}** — {gate.get('status', 'UNKNOWN')}",
]
if wave:
    lines += [
        f"- Current completion wave: **{wave.get('id')} — {wave.get('name')}**",
        f"- Wave range: {wave.get('from_percent')}% → {wave.get('to_percent')}%",
    ]
lines += [
    "",
    "## Meaningful movement in the last 24 hours",
]
if recent_merges:
    lines += [f"- Merge: {x}" for x in recent_merges[:8]]
if recent:
    lines += [f"- Change: {x}" for x in recent[:12]]
if not recent and not recent_merges:
    lines.append("- No repository commits recorded in the last 24 hours.")
lines += [
    "",
    "## Next percentage unlock",
    f"- {next_unlock}",
    "",
    "## Evidence boundary",
    "- This percentage is a planning/production estimate, not a test-acceptance label.",
    "- Commit count alone never raises the percentage.",
    "- STATIC/COMPILE evidence does not imply PIE, DEVICE, VISUAL, PACING, or PERFORMANCE acceptance.",
]
pending = handoff.get("unverified_acceptance", [])
if pending:
    lines += ["", "## Still unaccepted / awaiting human-device evidence"]
    lines += [f"- {x}" for x in pending[:8]]

print("\n".join(lines))
