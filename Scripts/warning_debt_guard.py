"""Guard UE4.27 warning debt by defect identity, not duplicated log occurrence."""
import argparse
from pathlib import Path
import re

# name, regex, ceiling, identity_group
# identity_group=1 means one defect is counted per captured asset/package identity.
CHECKS = [
    ("Missing smoothing groups", re.compile(r"No smoothing group information", re.I), 0, None),
    ("Degenerate tangent bases", re.compile(r"\b(SM_[A-Za-z0-9_]+) has degenerate tangent bases", re.I), 150, 1),
    ("Nearly-zero binormals", re.compile(r"\b(SM_[A-Za-z0-9_]+) has some nearly zero bi-normals", re.I), 150, 1),
    ("Missing world packages", re.compile(r"Failed to load '(/Game/Production/World/[^']+)'", re.I), 71, 1),
    ("Missing optional audio", re.compile(r"Failed to load '(/Game/Audio/[^']+)'", re.I), 0, 1),
    ("Missing optional rigs", re.compile(r"Failed to load '(/Game/Production/Characters/Rigs/[^']+)'", re.I), 0, 1),
    ("defaultMat references", re.compile(r"(defaultMat)", re.I), 0, 1),
    ("DirectionalLight mobility warnings", re.compile(r"(DirectionalLight_0.*has to be 'Movable')", re.I), 0, 1),
    ("NPC spawn collision failures", re.compile(r"SpawnActor failed because of collision at the spawn location \[([^\]]+)\] for \[ShireNPC\]", re.I), 0, 1),
]

def decode(path: Path) -> str:
    raw = path.read_bytes()
    encoding = "utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
    return raw.decode(encoding, errors="replace")

def measure(text: str, pattern: re.Pattern, identity_group):
    matches = list(pattern.finditer(text))
    if identity_group is None:
        return len(matches), []
    identities = sorted({m.group(identity_group) for m in matches})
    return len(identities), identities

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
    for name, pattern, ceiling, identity_group in CHECKS:
        count, identities = measure(text, pattern, identity_group)
        rows.append((name, count, ceiling))
        print(f"Warning debt: {name} = {count} (ceiling {ceiling})")
        if identities:
            print(f"Warning debt identities [{name}]: " + " | ".join(identities))
        if count > ceiling:
            failures.append(f"{name}: {count} > {ceiling}")

    if args.summary:
        with args.summary.open("a", encoding="utf-8") as handle:
            handle.write("\n### UE4.27 warning-debt guard\n")
            handle.write("| Category | Unique defects | Ceiling |\n|---|---:|---:|\n")
            for name, count, ceiling in rows:
                handle.write(f"| {name} | {count} | {ceiling} |\n")

    if failures:
        print("ERROR: Warning-debt regression detected: " + "; ".join(failures))
        return 1
    print("Warning-debt guard passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
