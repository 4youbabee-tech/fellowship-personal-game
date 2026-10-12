#!/usr/bin/env python3
"""GitHub-hosted cleanup: delete *only proven merged* abandoned branches.

No broad 'stale date' deletion. A diverged head (ahead_by > 0) is NOT safe.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


API = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")
REPO = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ["GITHUB_TOKEN"]
KEEP = {"develop", "main"}
PROTECTED_PREFIX = ("archive/", "salvage/", "generated/")
MAX_DELETES = 25


def get(path, method="GET"):
    req = urllib.request.Request(API + "/repos/" + REPO + path, method=method,
        headers={"Authorization": "Bearer " + TOKEN,
                 "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        if method == "DELETE" and exc.code == 422:
            return {"protected": True}
        raise


def q(s):
    return urllib.parse.quote(s, safe="")


def pages(path):
    all_rows = []
    for page in range(1, 11):
        separator = "&" if "?" in path else "?"
        rows = get(path + separator + "per_page=100&page=" + str(page))
        all_rows.extend(rows)
        if len(rows) < 100:
            return all_rows
    raise RuntimeError("PAGINATION_LIMIT_REACHED")


def audit():
    refs = pages("/branches")
    prs = pages("/pulls?state=open")
    open_heads = {p["head"]["ref"] for p in prs
                  if p.get("head", {}).get("repo", {}).get("full_name") == REPO}
    result = {"schema_version": 1, "mode": "HOSTED_MERGED_BRANCH_SAFETY_CLEANUP",
              "branches_seen": len(refs), "open_pr_heads": len(open_heads),
              "deleted": [], "kept": [], "errors": []}
    for branch in refs:
        name, sha = branch["name"], branch["commit"]["sha"]
        reason = None
        if name in KEEP or name.startswith(PROTECTED_PREFIX) or branch.get("protected"):
            reason = "PROTECTED_OR_ARCHIVE"
        elif name in open_heads:
            reason = "OPEN_PR"
        if reason:
            result["kept"].append({"name": name, "reason": reason})
            continue
        try:
            comparison = get("/compare/" + q("develop") + "..." + q(name))
            if comparison["ahead_by"] != 0:
                result["kept"].append({"name": name, "reason": "UNMERGED_COMMITS",
                                       "ahead_by": comparison["ahead_by"]})
                continue
            latest = get("/git/ref/heads/" + q(name))
            if latest["object"]["sha"] != sha:
                result["kept"].append({"name": name, "reason": "RACE_REF_MOVED"})
                continue
            if len(result["deleted"]) >= MAX_DELETES:
                raise RuntimeError("MAX_DELETES_REACHED")
            if os.getenv("CLEANUP_DRY_RUN") == "1":
                result["kept"].append({"name": name, "reason": "MERGED_DRY_RUN"})
                continue
            deletion = get("/git/refs/heads/" + q(name), "DELETE")
            if deletion and deletion.get("protected"):
                result["kept"].append({"name": name, "reason": "SERVER_PROTECTION"})
            else:
                result["deleted"].append({"name": name, "verified_sha": sha})
        except (urllib.error.URLError, ValueError, KeyError, RuntimeError) as exc:
            result["errors"].append({"name": name, "error": str(exc)[:250]})
    return result


def main():
    report = audit()
    out = os.environ.get("BRANCH_AUDIT_PATH")
    if out:
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    print("HOSTED_BRANCH_SAFETY_AUDIT branches=%d deleted=%d kept=%d errors=%d" %
          (report["branches_seen"], len(report["deleted"]),
           len(report["kept"]), len(report["errors"])))
    if report["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
