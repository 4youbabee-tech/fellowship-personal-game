"""Read live GitHub evidence. Never commit CI snapshots back into the source branch."""
import argparse
from datetime import datetime, timezone
import json
import os
import urllib.parse
import urllib.request


GATES = {"pre_unreal": "Pre-Unreal Validation", "unreal": "Unreal Build Validation"}


def select_evidence(sha, runs):
    evidence = {}
    for gate, name in GATES.items():
        candidates = [r for r in runs if r.get("head_sha") == sha and r.get("name") == name]
        run = max(candidates, key=lambda r: (r["id"], r.get("run_attempt", 1)), default=None)
        evidence[gate] = ({"sha": sha, "run_id": run["id"],
                           "attempt": run.get("run_attempt", 1),
                           "status": run["status"], "conclusion": run.get("conclusion"),
                           "url": run.get("html_url")}
                          if run else {"sha": sha, "status": "NOT_OBSERVED"})
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="4youbabee-tech/fellowship-personal-game")
    args = parser.parse_args()
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        parser.error("Set GH_TOKEN or GITHUB_TOKEN with read access; no write permission is needed")
    base = "https://api.github.com/repos/" + args.repo

    def get(path):
        request = urllib.request.Request(base + path, headers={
            "Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"})
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)

    def pages(path, key=None):
        result = []
        for page in range(1, 101):
            data = get(path + ("&" if "?" in path else "?") + "per_page=100&page=" + str(page))
            chunk = data[key] if key else data
            result.extend(chunk)
            if len(chunk) < 100:
                return result
        raise RuntimeError("Pagination limit reached; refusing an incomplete snapshot")

    develop = get("/branches/develop")["commit"]["sha"]
    prs = pages("/pulls?state=open&base=develop")
    targets = [{"kind": "integration", "branch": "develop", "sha": develop}]
    targets.extend({"kind": "candidate", "pr": p["number"], "branch": p["head"]["ref"],
                    "sha": p["head"]["sha"]} for p in prs)
    for target in targets:
        runs = pages("/actions/runs?head_sha=" + urllib.parse.quote(target["sha"]), "workflow_runs")
        target["evidence"] = select_evidence(target["sha"], runs)
        target["machine_green"] = all(e.get("status") == "completed" and
            e.get("conclusion") == "success" for e in target["evidence"].values())
    # Detect concurrent movement instead of publishing an old head as live.
    stable = get("/branches/develop")["commit"]["sha"] == develop
    latest_prs = pages("/pulls?state=open&base=develop")
    stable = stable and {(p["number"], p["head"]["sha"]) for p in prs} == {
        (p["number"], p["head"]["sha"]) for p in latest_prs}
    print(json.dumps({"observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "heads_stable_during_read": stable, "targets": targets,
        "scope": "Read-time machine evidence only. Requests remain in ProjectGovernor.json; "
                 "visuals, performance and continuous gameplay acceptance need separate evidence."}, indent=2))
    return 0 if stable else 2


if __name__ == "__main__":
    raise SystemExit(main())
