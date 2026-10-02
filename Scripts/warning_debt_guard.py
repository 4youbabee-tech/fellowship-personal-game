"""Guard UE4.27 warning debt by defect identity and evidence scope."""
import argparse
from pathlib import Path
import re

from runtime_audit_contracts import RUNTIME_LOG_PREFIXES

SMOOTHING_RE = re.compile(r"No smoothing group information", re.I)
IMPORT_RESULT_RE = re.compile(r"ShireProductionImport result:\s*(.+?)\s+\|", re.I)
SKELETAL_BEGIN_RE = re.compile(r"ShireProductionImport: skeletal FBX import .*?asset=([A-Za-z0-9_]+)", re.I)

# name, regex, ceiling, identity_group, scope
# scope="all": build/import/runtime evidence.
# scope="runtime": startup/chapter/state logs only.
CHECKS = [
    ("Missing smoothing groups", SMOOTHING_RE, 0, None, "all"),
    ("Degenerate tangent bases", re.compile(r"\b(SM_[A-Za-z0-9_]+) has degenerate tangent bases", re.I), 0, 1, "all"),
    ("Nearly-zero tangents", re.compile(r"\b(SM_[A-Za-z0-9_]+) has some nearly zero tangents", re.I), 0, 1, "all"),
    ("Nearly-zero binormals", re.compile(r"\b(SM_[A-Za-z0-9_]+) has some nearly zero bi-normals", re.I), 0, 1, "all"),
    ("Missing production master surface", re.compile(r"(M_ProductionSurface).*?(?:Can't find file|Failed to find object)", re.I), 0, 1, "all"),
    ("Missing world packages", re.compile(r"Failed to load '(/Game/Production/World/[^']+)'", re.I), 0, 1, "runtime"),
    ("Missing optional audio", re.compile(r"Failed to load '(/Game/Audio/[^']+)'", re.I), 0, 1, "runtime"),
    ("Missing optional rigs", re.compile(r"Failed to load '(/Game/Production/Characters/Rigs/[^']+)'", re.I), 0, 1, "runtime"),
    ("defaultMat references", re.compile(r"(defaultMat)", re.I), 0, 1, "all"),
    ("DirectionalLight mobility warnings", re.compile(r"(DirectionalLight_0.*has to be 'Movable')", re.I), 0, 1, "runtime"),
    ("NPC spawn collision failures", re.compile(r"SpawnActor failed because of collision at the spawn location \[([^\]]+)\] for \[ShireNPC\]", re.I), 0, 1, "runtime"),
    ("Streaming pool scalability override warnings", re.compile(r"r\.Streaming\.PoolSize.*(?:ignored|lower priority)", re.I), 0, None, "all"),
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

def is_runtime_log(path: Path) -> bool:
    return any(path.name.startswith(prefix) for prefix in RUNTIME_LOG_PREFIXES)

def _asset_basename(source: str) -> str:
    return source.strip().replace("\\", "/").rsplit("/", 1)[-1]

def measure_missing_smoothing(files):
    """Count concrete import defects, not repeated UE warning-summary echoes."""
    identities = set()
    unresolved = set()

    for path in files:
        lines = decode(path).splitlines()
        attributed_in_file = set()
        orphan_count = 0

        for index, line in enumerate(lines):
            if not SMOOTHING_RE.search(line):
                continue

            identity = None

            # Live importer warning: deterministic result follows shortly after it.
            for following in lines[index + 1:min(len(lines), index + 48)]:
                match = IMPORT_RESULT_RE.search(following)
                if match:
                    identity = _asset_basename(match.group(1))
                    break

            # Skeletal fallback: explicit begin marker precedes the warning.
            if identity is None:
                for prior in reversed(lines[max(0, index - 48):index]):
                    match = SKELETAL_BEGIN_RE.search(prior)
                    if match:
                        identity = match.group(1) + ".fbx"
                        break

            if identity:
                attributed_in_file.add(identity)
            else:
                orphan_count += 1

        identities.update(attributed_in_file)

        # UE4 repeats live warnings in its final Warning/Error Summary. One
        # unattributed repeat in a log that already has an attributed warning
        # is an echo, not a second asset defect. Anything else remains fail-closed.
        if orphan_count:
            if not attributed_in_file:
                unresolved.add(f"UNIDENTIFIED@{path.name}")
            elif orphan_count > 1:
                unresolved.add(f"UNIDENTIFIED@{path.name}")

    measured = sorted(identities | unresolved)
    return len(measured), measured

def measure_missing_smoothing(files):
    identities = set()
    unresolved = set()
    for path in files:
        lines = decode(path).splitlines()
        local_ids = set()
        orphan = 0
        for index, line in enumerate(lines):
            if not SMOOTHING_RE.search(line):
                continue
            identity = None
            for following in lines[index + 1:min(len(lines), index + 48)]:
                match = IMPORT_RESULT_RE.search(following)
                if match:
                    identity = match.group(1).strip().replace("\\\\", "/").rsplit("/", 1)[-1]
                    break
            if identity:
                local_ids.add(identity)
            else:
                orphan += 1
        identities.update(local_ids)
        if orphan and not local_ids:
            unresolved.add("UNIDENTIFIED@" + path.name)
        elif orphan > 1:
            unresolved.add("UNIDENTIFIED@" + path.name)
    measured = sorted(identities | unresolved)
    return len(measured), measured

def collect_text(files, scope: str) -> str:
    if scope == "runtime":
        files = [path for path in files if is_runtime_log(path)]
    return "\n".join(decode(path) for path in files)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log-dir", required=True, type=Path)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()

    files = sorted(args.log_dir.glob("CI-*.log"))
    if not files:
        print("ERROR: No CI Unreal logs found for warning-debt analysis.")
        return 2

    texts = {
        "all": collect_text(files, "all"),
        "runtime": collect_text(files, "runtime"),
    }
    runtime_files = [path.name for path in files if is_runtime_log(path)]
    if not runtime_files:
        print("ERROR: No runtime CI logs found for runtime warning-debt analysis.")
        return 2

    print("Warning-debt evidence files: " + " | ".join(path.name for path in files))
    print("Warning-debt runtime files: " + " | ".join(runtime_files))

    rows, failures = [], []
    for name, pattern, ceiling, identity_group, scope in CHECKS:
        scoped_files = files if scope == "all" else [path for path in files if is_runtime_log(path)]
        if name == "Missing smoothing groups":
            count, identities = measure_missing_smoothing(scoped_files)
        else:
            count, identities = measure(texts[scope], pattern, identity_group)
        rows.append((name, count, ceiling, scope))
        print(f"Warning debt: {name} = {count} (ceiling {ceiling}, scope {scope})")
        if identities:
            print(f"Warning debt identities [{name}]: " + " | ".join(identities))
        if count > ceiling:
            failures.append(f"{name}: {count} > {ceiling}")

    if args.summary:
        with args.summary.open("a", encoding="utf-8") as handle:
            handle.write("\n### UE4.27 warning-debt guard\n")
            handle.write("| Category | Unique defects | Ceiling | Scope |\n|---|---:|---:|---|\n")
            for name, count, ceiling, scope in rows:
                handle.write(f"| {name} | {count} | {ceiling} | {scope} |\n")

    if failures:
        print("ERROR: Warning-debt regression detected: " + "; ".join(failures))
        return 1
    print("Warning-debt guard passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
