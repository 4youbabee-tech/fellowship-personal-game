# Master Execution Board

This file is a human-readable execution board. **Data/ProjectGovernor.json remains the sole project-management authority.** Data/MasterExecutionRoadmap.json is the machine-readable execution map.

## Current control point

- PR: #62 `production/early-realms-world-life-v1`
- Green integration baseline: `develop@f4886b39feea29973543bf6cfb1be4659f10ff9d`
- Baseline Pre-Unreal: **SUCCESS #543**
- Baseline Unreal Build: **SUCCESS #378**
- Previous candidate `88e3c7308599a7d11820dda7479ab03c42ed5122`: Pre-Unreal #550 failed only on stale roadmap/orphan tracking; Unreal #385 stopped before compilation because Engine Content was temporarily unreadable by the runner service.
- The same `NETWORK SERVICE` runner read that exact Engine Content and completed Unreal Build #381 earlier, so #385 is classified as an environment/preflight block, not a demonstrated C++ build failure.
- Runner state: **ONLINE**.
- Gate rule: repair exact-head metadata first, then require fresh Pre-Unreal + full UE4.27.2 exact-head proof before V10 merge.
- Comprehensive next wave after green V10: PR #63 reconciliation -> transactional transition safety -> ambient pooling -> residual async-load burn-down -> diegetic living-NPC vertical slice -> chapter/device evidence.

## Execution order

1. **B0 - Exact-head stability.** Repair and validate the integrated PR head.
2. **B1 - Part I story/gameplay complete.** Film anchors, Ring, exploration, side content, ensemble missions, modern player-life/progression.
3. **B2 - Characters and world production.** Replace proxies, rig/animate the cast, raise every region toward the cinematic beauty benchmark.
4. **B3 - Living world and presentation.** NPC goals/memory/dialogue, companion life, sound/camera/lighting polish.
5. **B4 - Acceptance and merge.** Exact-SHA engine/device/human evidence, then merge.
6. **B5/B6 - Part II/III.** Only after source verification and the Part I production baseline.

## Active work, now uniquely ordered

| Rank | Work ID | Bundle | Work |
|---:|---|---|---|
| 0 | WORK-MEGA-001 | B0_EXACT_HEAD_STABILITY | CP56 whole-game mega integration and green-head repair loop |
| 1 | WORK-QA-001 | B0_EXACT_HEAD_STABILITY | Automation-first delivery and regression coverage |
| 2 | WORK-EXEC-001 | CONTINUOUS_CONTROL | Master execution control and orphan-work prevention |
| 3 | WORK-QA-002 | B0_EXACT_HEAD_STABILITY | Local Pre-Unreal preflight before one-click build/share |
| 34 | WORK-PERF-003 | B3_LIVING_WORLD_AND_PRESENTATION | Ambient NPC object-pool migration after V10/transition reconciliation |
| 35 | WORK-PERF-004 | B0_EXACT_HEAD_STABILITY | Residual synchronous asset-load debt guard and burn-down |
| 10 | WORK-EXP-003 | B1_PART1_STORY_GAMEPLAY_COMPLETE | CP56 Fellowship film-experience mega-pass |
| 11 | WORK-RING-001 | B1_PART1_STORY_GAMEPLAY_COMPLETE | Trilogy Ring-quest systemic core |
| 12 | WORK-SIDE-001 | B1_PART1_STORY_GAMEPLAY_COMPLETE | Film-derived side-content rollout |
| 13 | WORK-ENSEMBLE-001 | B1_PART1_STORY_GAMEPLAY_COMPLETE | Film-ensemble playable mission rollout |
| 14 | WORK-EXP-004 | B1_PART1_STORY_GAMEPLAY_COMPLETE | Journey Discovery rewards and exploration progression |
| 15 | WORK-EXP-005 | B1_PART1_STORY_GAMEPLAY_COMPLETE | Contextual side-play implementation |
| 16 | WORK-GAME-001 | B1_PART1_STORY_GAMEPLAY_COMPLETE | Modern game systems and side-content rollout |
| 20 | WORK-CHAR-004 | B2_CHARACTERS_AND_WORLD_PRODUCTION | Full production-character replacement mega-pass |
| 21 | WORK-CHAR-001 | B2_CHARACTERS_AND_WORLD_PRODUCTION | Playable Frodo/Gandalf character production motion pass |
| 30 | WORK-WORLD-003 | B2_CHARACTERS_AND_WORLD_PRODUCTION | Cinematic world beauty mega-pass |
| 31 | WORK-WORLD-002 | B2_CHARACTERS_AND_WORLD_PRODUCTION | Part I mass resource saturation and playable integration |
| 32 | WORK-WORLD-001 | B2_CHARACTERS_AND_WORLD_PRODUCTION | Expand environmental micro-life and production polish chapter by chapter |
| 40 | WORK-LW-004 | B3_LIVING_WORLD_AND_PRESENTATION | Offline Living NPC intelligence expansion |
| 41 | WORK-DLG-001 | B3_LIVING_WORLD_AND_PRESENTATION | Source-grounded living dialogue expansion |

## No-forget rule

PG-078 compares the Governor against the master roadmap on every Pre-Unreal run. If an accepted unfinished requirement or ACTIVE work item is added without being assigned to an execution bundle, validation fails. This turns “do not forget anything” into an executable project rule rather than a chat reminder.

## Immediate large actions

- Finish the exact-head UE4.27 validation/repair loop.
- Complete Part I film/gameplay gaps and the lightweight modern-game/player-life layer.
- Start production-character waves: Frodo/Gandalf -> Sam/Merry/Pippin -> Aragorn/Boromir/Legolas/Gimli -> remaining named cast/enemies/crowds.
- Start cinematic world waves: Shire/Bree/Rivendell first, then Weathertop/Caradhras/Moria/Lothlorien/Anduin/Isengard.
- Continue offline NPC/dialogue/presentation work behind source-knowledge and performance guards.
