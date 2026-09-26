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
