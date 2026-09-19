"""Guard known UE4.27 warning debt without hiding new regressions."""
import argparse
from pathlib import Path
import re

CHECKS = [
    ("Missing smoothing groups", re.compile(r"No smoothing group information", re.I), 0, False),
    ("Degenerate tangent bases", re.compile(r"degenerate tangent bases", re.I), 150, False),
    ("Nearly-zero binormals", re.compile(r"nearly zero bi-normals", re.I), 150, False),
    ("Missing world material packages", re.compile(r"Failed to load '(/Game/Production/World/[^']+)'", re.I), 71, True),
    ("Missing optional audio", re.compile(r"Failed to load '(/Game/Audio/[^']+)'", re.I), 0, True),
    ("Missing optional rigs", re.compile(r"Failed to load '(/Game/Production/Characters/Rigs/[^']+)'", re.I), 0, True),
    ("defaultMat references", re.compile(r"(defaultMat)", re.I), 0, True),
    ("DirectionalLight mobility warnings", re.compile(r"(DirectionalLight_0.*has to be 'Movable')", re.I), 0, True),
    ("NPC spawn collision failures", re.compile(r"SpawnActor failed because of collision at the spawn location \[([^\]]+)\] for \[ShireNPC\]", re.I), 0, True),
]

def decode(path: Path) -> str:
    raw = path.read_bytes()
    encoding = "utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
    return raw.decode(encoding, errors="replace")

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log-dir", required=True, type=Path)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()

    files = sorted(args.log_dir.glob("CI-*.log"))
    if not files:
        print("ERROR: No CI Unreal logs found for warning-debt analysis.")
        return 2

    text = "\n".join(decode(path) for path in files)
    rows, failures = [], []
    for name, pattern, ceiling, unique in CHECKS:
        matches = list(pattern.finditer(text))
        count = len({m.group(1) if m.lastindex else m.group(0) for m in matches}) if unique else len(matches)
        rows.append((name, count, ceiling))
        print(f"Warning debt: {name} = {count} (ceiling {ceiling})")
        if count > ceiling:
            failures.append(f"{name}: {count} > {ceiling}")

    if args.summary:
        with args.summary.open("a", encoding="utf-8") as handle:
            handle.write("\n### UE4.27 warning-debt guard\n")
            handle.write("| Category | Count | Ceiling |\n|---|---:|---:|\n")
            for name, count, ceiling in rows:
                handle.write(f"| {name} | {count} | {ceiling} |\n")

    if failures:
        print("ERROR: Warning-debt regression detected: " + "; ".join(failures))
        return 1
    print("Warning-debt guard passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
