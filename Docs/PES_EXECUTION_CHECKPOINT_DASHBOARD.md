# SHIRE JOURNEY — PES Checkpoint Dashboard and Continuous Work Handoff

**Authority:** `Data/ProjectGovernor.json` -> `pes_execution_dashboard_2026_10_14`. **Fixed 24-session roadmap:** `Docs/PES_PRODUCTION_EXECUTION_SESSIONS.md`. **Gates:** `Docs/DEVELOPMENT_GATES.md`.

This document is a subordinate, developer-readable progress display. It cannot independently authorize chapter transitions or change accepted evidence. Work in numbered PES sessions. Preserve the 24 fixed session IDs and objectives across developers; any authoritative change must go through the Project Governor. New developer: start at Governor, then this dashboard and live GitHub, then persistent Windows receipts.

## Five permanent checkpoints for every PES

| Indicator | Checkpoint | Acceptance |
|---|---|---|
| CP1 | SOURCE + ASSET REGISTRY AUDIT | Deduplicated source and Unreal Asset Registry gap map; verified file provenance and licenses |
| CP2 | PERSISTENT WAREHOUSE | SHA-checked persisted source/reuse receipts on approved Windows storage |
| CP3 | UNREAL IMPORT + REOPEN | Actual `.uasset` files saved and reopened in a fresh UE4.27.2 process, receipt and package hashes |
| CP4 | WORLD BINDING + OBSERVATION | P1C01 production level binding, actual placed actors/instances, observed evidence and relevant collision/material checks |
| CP5 | VERIFICATION + MERGE + REPORT | Exact candidate-head required checks; PIE/device/visual evidence when applicable; merged PR, safe branch closure, numeric session report |

**Display:** `PES-NNN | CP1:PARTIAL | CP2:PASSED | CP3:BLOCKED | CP4:PENDING | CP5:PENDING`. Only write PASSED when its own evidence exists; the five cells are **not** an invented completion percentage. Record blocked reasons, exact asset paths/SHAs and next action. Do not conflate static, build, PIE, device, visual, and gameplay/placement acceptance.

## PES-001 — Historical evidence checkpoint (refresh before acting)

- Canonical `develop` HEAD at recorded inspection: `319e07c8db898f310ac5dc3e2ad52c344a17ea9b`.
- Open candidate: PR **#463**, last inspected head `37fef5717601f341ea3f854badf6c8c1ed05cc1e`.
- CP1 **PARTIAL**: Cloud138 source batch identified, but entire source / Asset Registry gap audit not proved.
- CP2 **PASSED_FOR_CLOUD138_SOURCE_BATCH**: Windows Run **38460938061** logged `CLOUD_WHOLEGAME_WAREHOUSE_REUSED fbx=138 png=36 regions=28`. This is not a complete Warehouse inventory.
- CP3 **BLOCKED**: Run **38460938061** failed UE editor inspection with `CLOUD138_WALKABLE_UCX_NOT_IMPORTED:/Game/Production/World/Shire/Cloud138/SM_ShRoundDoor`. PR #463 contains a narrowly guarded candidate repair. Run **38467646516** passed Pre-Unreal on that candidate head. Windows UE import/reopen/persist is NOT accepted until the appropriate new exact-head workflow succeeds and emits receipts.
- CP4 **PENDING**: The Cloud138 importer explicitly reports `world_placed=false` and must not be presented as in-world integration.
- CP5 **PENDING**: No proven PES-001 closure; cannot start PES-002 runtime production based on source/compile-only proof.

**Live GitHub Actions status is volatile.** Check newest PR head and workflow attempts, then compare their exact SHAs with any evidence. Never treat the snapshot above as a live status or an acceptance assertion.

## Owner update format — show at start, checkpoint completion, blocker, final

```text
SHIRE JOURNEY | PES-NNN — <session name> | OPEN / BLOCKED / COMPLETE
CP1 [status] — source/Asset Registry
CP2 [status] — Warehouse
CP3 [status] — Unreal .uasset import/reopen
CP4 [status] — world placement/observation
CP5 [status] — tests/merge/report
Current work: <one grounded line>
Actual change this update: <paths/commit/PR and verified counts>
Blocker: <exact error or "none proven">
Required to unlock next PES: <specific gate/evidence>
```

For each session closeout, record previous/current/delta/growth% **separately** for unique source QC, Warehouse persisted, imported/reopened packages, actual world instances, functional gameplay, accepted gates and remaining Git refs. Formula: `(current - previous) / previous * 100`; **N/A** for unknown or zero comparable baseline. Record exact commit, PR, workflow run and observed logs/screenshots/FPS if genuinely obtained. Distinguish NEW from REUSED and FROM SOURCE ONLY.

## Unattended execution and handoff

- Aim to complete each *bounded* PES in a single Work execution when no blocker occurs. **Do not promise permanent nonstop Work sessions**: availability, request/approval boundaries, Windows runner health, timeouts, Actions job limits and gate failures can stop work. The owner can leave the phone; durable GitHub Actions can continue separately while the host is available.
- Work as far as safely possible and reuse successful unchanged receipts/SHAs, without repeatedly queueing duplicate heavy runner jobs; one UE4 runtime writer and one persisted Warehouse writer. Five independent source-only preparation lanes may run in parallel.
- On root failure, stop only the affected lane, write the exact failure, fix the smallest verified cause and add an appropriate regression test, then rerun exact-head gates. Unrelated safe source preparation may continue. Do not merge/close before evidence.
- At every voluntary or forced stop, commit durable handoff status in the relevant repo documents through validated PR as applicable: current PES/CP, latest SHA, counts/evidence, GitHub jobs, active blocker, next exact command; do not falsify testing or acceptance.
- After **actual PES completion**, increment to the next fixed session and initialize CP1..CP5 from proven reused evidence, not from guesses. A new engineer must be able to continue without this conversation.

**No runtime chapter beyond P1C01 activates before its predecessor Gate 6/7; future source prep is allowed under Governor.**
