# CI latency review — 2026-09-26

## Measured GitHub jobs
Times are UTC; queue = job start minus workflow creation, execution = job completion minus job start.

| Run | Change | Queue | Execution |
| --- | --- | --- | --- |
| 36264586047 | PR102, 91ca7d5c, administrative repair | 00:04 | 13:46 |
| 36259793341 | PR102, 35002d9f, onboarding | 10:37 | 13:54 |
| 36262879092 | PR101, 65f3c687, Pre-Unreal | 05:04 | 00:48 |

Source: GitHub Actions run/job APIs and job 108466709220 log.
That log explicitly reports FULL_UNREAL_FILE README.md and FULL_UNREAL_FILE Scripts/new_developer_onboarding.ps1. This classified onboarding as unknown full-impact work and repeated editor build (4:10), asset import (0:55), chapter/state audits (3:16), and packaging (3:02). This repetition was unnecessary for those non-runtime files. A full runtime/package run taking this time on the existing device is not itself an error.

## Changes
- Explicitly classify README, onboarding and Governor evidence helpers as non-runtime. No broad Scripts/Data exemption.
- Validation-policy changes may inherit a successful candidate ancestor after checking the entire intervening delta. A non-green integration tip alone no longer forces repetition if a safe proven candidate ancestor exists.
- Fetch bounded history when shallow checkout lacks ancestor proof; inspect the delta before doing GitHub proof lookups.
- Keep mixed runtime changes in core/asset/full paths; packaging/config/streaming and unknown paths stay full.
- Add nine behavioral PowerShell classifier cases to Pre-Unreal, including no-proof fallback and mixed story/config/streaming cases.
- Batch related edits into one atomic commit. Superseded runs are not evidence of a gameplay failure.

## Boundaries and remaining work
No engine, story, movement, save/load or experiential acceptance checks were globally disabled. Queue time on the single Windows runner remains possible. This change targets needless full builds, not a guaranteed wall-clock SLA. PowerShell tests must pass on Windows CI; no local PowerShell runtime is available in this session. Record actual post-change durations before claiming a measured speedup. Broad concurrency/scheduling changes are deferred until this measured root cause is resolved.

## Checkout stall observed after previous review

Unreal #888 on the latest onboarding head was still in exact-head checkout more than six minutes after starting, although Pre-Unreal #1083 had passed. The generated Unreal Git fetch used seven retries without an HTTP low-speed bound. Add Git's 1000 bytes/s for 20 seconds low-speed cutoff to each retry, preserving seven attempts, depth two and exact SHA verification. This bounds stalled transfer attempts; it does not bypass Git authentication, provenance or engine checks. Verify the next run's checkout duration before claiming an improvement. A stalled already-running workflow uses its older script and is unaffected.

## Root-cause expansion after #888/#889

Additional direct log evidence:

| Run | Observed behavior | Concrete cost |
| --- | --- | ---: |
| #888 | Exact-head checkout stalled before Unreal build and was later cancelled | ~11m18s job life; no useful engine proof |
| #884 | Legitimate D full validation | ~13m40s job life |
| #885 | Administrative PR classified FULL | ~13m35s job life |
| #886 | Administrative/onboarding PR classified FULL | ~17m23s job life |
| #887 | Administrative/onboarding PR classified FULL | ~18m09s job life |
| #889 | Administrative/CI PR classified FULL after missing direct develop proof | build alone 232.41s before repeating import/runtime/package path |

Across #884-#887, the editor compile repeatedly reported `Creating makefile for ShireJourneyEditor (no existing makefile)` and rebuilt **76 actions with one process**, costing roughly **238-252 seconds** each time. This is not acceptable for documentation/onboarding/governance deltas.

### Confirmed root causes

1. **Unbounded/overlong exact-head checkout behavior**  
   Older generated checkout logic retried seven times and had no Git low-speed cutoff. #888 demonstrated that a dead/slow transfer could occupy the single Windows runner for many minutes before any validation began.

2. **Administrative files waking Unreal at all**  
   README/onboarding/handoff/classifier tests were not excluded at the workflow trigger layer, so the expensive workflow started before the classifier could decide they were safe.

3. **Superseded PR runs continuing to consume the only device**  
   Concurrency cancellation applied only to selected branch prefixes. An older SHA on an ops branch could continue running while the new SHA waited, even though exact-head evidence from the old SHA could never satisfy the current PR.

4. **Merge SHA differs even when content is identical**  
   The merged C4 develop commit `2845071119d926defd6ba94c970f43729bc51674` and the proven C4 candidate `bc1e04062d8079fef73eae64f68c81772b4fc56c` have the **same Git tree SHA** `3de99fa7951e889cf319e967a2225e962d9cc554`. The classifier previously required a workflow attached to the merge SHA itself, so a cancelled post-merge run could force a redundant FULL rebuild despite byte-for-byte identical repository content.

5. **Checkout destroyed Git state required for incremental build detection**  
   The Unreal workflow removed `.git` and reinitialized the repository every run. That discards checkout/index continuity and causes Git to rewrite the working tree broadly. UnrealBuildTool uses Git status for adaptive working-set detection and UBT Makefiles for fast iterative/outdatedness checks; preserving exact repository state is therefore a prerequisite for safe incremental compilation.

### Safe corrections now implemented

- Unreal workflow ignores README/onboarding/handoff/classifier-test administrative paths on both push and PR events; Pre-Unreal still validates them.
- Exact checkout keeps the existing `.git` metadata, fetches/reset-checkouts the exact SHA, verifies `rev-parse HEAD == TARGET_SHA`, and scrubs the temporary authenticated remote URL afterward.
- Fetch retries are reduced from seven to three and each uses `http.lowSpeedLimit=1000` plus `http.lowSpeedTime=20`.
- Concurrency is scoped by PR branch: a newer SHA cancels only the older SHA from the **same PR**, never a different runtime PR or develop run.
- The classifier may reuse core proof across a merge only when the merge tree SHA and a proven parent tree SHA are **exactly equal**. No filename heuristic or approximate comparison can grant this reuse.
- FULL validation remains mandatory for Config, Build.cs, Target.cs, chapter streaming/package/cook/release critical changes and unknown-impact files.
- Runtime/source/data changes still require the appropriate core/asset/full engine path.
- No gameplay, story, movement, save, streaming, warning-debt or package correctness gate is globally disabled.

### Build-cache policy

Do **not** add a blind compiled-artifact cache or increase `MaxParallelActions` yet. The current runner has historical MSVC resource-pressure handling and the target development device is memory constrained. First measure the effect of:
1. correct trigger classification,
2. superseded-run cancellation,
3. persistent exact Git checkout,
4. UBT incremental makefile reuse.

Only if real runtime C++ builds remain a bottleneck after those corrections should parallelism/cache tuning be evaluated with measured RAM/CPU data.

### External guidance cross-check

- GitHub Actions documents `concurrency` + `cancel-in-progress` specifically for cancelling obsolete in-progress work; branch-scoped grouping prevents unrelated workflows from cancelling one another.
- Epic's UnrealBuildTool documentation states that `bUseUBTMakefiles` exists for fast iterative builds by caching target data and checking only outdated dependencies, and that Git repositories are used for adaptive working-set detection.

These sources support the architecture above, but project acceptance still depends on our own exact-head measurements.

### Evidence boundary

The source changes above are **CI architecture changes pending fresh exact-head measurement**. Do not claim a measured speedup until the corrected workflow finishes and its checkout/build/total durations are recorded.
