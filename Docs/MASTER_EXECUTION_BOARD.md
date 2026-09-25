## W01 P1C01 Mega Production control point - Drop C2
- Canonical parent: `develop@82fc4deaf2e2a99cfebd0d8d1b99a42b5d922ffe` (Drop C1 merge).
- Active candidate: PR #78 on `production/w01-p1c01-foliage-wind-v1` targeting `develop`.
- Scope: dedicated near/mid foliage master + parameterized SimpleGrassWind WPO + DistanceCullFade attenuation, plus a stripped `M_ProductionFoliageFar` with no WPO for later far-LOD binding.
- Explicit non-scope: no density increase, no C3 material reassignment, no gameplay runtime loading changes, no NPC/LivingWorld ownership changes.
- Required machine gate: exact-head Pre-Unreal + UE4.27.2 production-import/core validation.
- Human/device boundary: no visual, pacing, FPS, VRAM, overdraw or target-device acceptance until separately observed.

## W01 P1C01 Mega Production control point - Drop C1
- Canonical parent: `develop@712a81cac150b7fdb338a4cf7554d4f27d4b5191`.
- Parent proof: Pre-Unreal #894 SUCCESS; Unreal #729 SUCCESS.
- Active candidate: PR #77 on `production/w01-p1c01-materials-vegetation-v1` targeting `develop`.
- Active lane: **W01_P1C01_PRODUCTION_VERTICAL_SLICE**.
- Current drop: **C1 - Authored Material Texture Binding**.
- Next dependency after exact-head green: **C2 - Lightweight Foliage Master + Wind WPO**.
- W00 remains CLOSED; reopen only for a concrete regression.
- Evidence boundary: STATIC-VALIDATED until PR #77 exact-head machine proof.

# Master Execution Board

This file is a human-readable execution board. **Data/ProjectGovernor.json remains the sole project-management authority.** Data/MasterExecutionRoadmap.json is the machine-readable execution map.

## Current control point

- PR: #78 (W01/P1C01 lightweight foliage wind candidate)
- Branch: `production/w01-p1c01-foliage-wind-v1`
- Active lane: **W01_P1C01_PRODUCTION_VERTICAL_SLICE**
- Active production drop: **C2_LIGHTWEIGHT_FOLIAGE_WIND**
- Previous lane: **W00_ARCHITECTURAL_STABILIZATION — CLOSED**
- Canonical integration/programmer-handoff branch: `develop`
- Stable release branch: `main`
- Repository branch cleanup: **COMPLETE**; remote branch query after cleanup returned only `develop` and `main`.
- Full machine-green baseline: `fdbb6492b71d03fe0df70a9d6ac38b8e1ac0e0be`
- Pre-Unreal baseline: **SUCCESS #820**
- Unreal baseline: **SUCCESS #655**
- Automated closure head before consolidation: `9066d6494248def59680820bbd6ca8e10038ea6e`
- Pre-Unreal: **SUCCESS #821**
- Unreal: **SUCCESS #656 acceptance-only**, inheriting parent core proof.
- Consolidated develop head after PR #70: `3108b2dd6354b196d36406935057c25feab2fec2`; Pre-Unreal #865 **SUCCESS**.
- Performance rule: Windows / DX11 / 720p Low-Medium / 30 FPS floor.
- Acceptance boundary: human P1C01 grounding/warning-tail, target-device performance and visual/audio acceptance remain open.

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

- Validate packaged runtime Data JSON staging/read behavior.
- Validate actual authored audio-bank presence/playback without `-NoSound`.
- Perform isolated Public/Private runtime-source migration without gameplay redesign, then re-run exact-head Pre-Unreal and UE4.27.2 validation.
- Run target-device DX11/720p Low-Medium profiling and chapter-specific human PIE/pacing/visual checks.
- W00 is closed; keep broad Part II/III runtime production gated until P1C01 clears Gate 6/7 human visual/pacing/performance evidence.

