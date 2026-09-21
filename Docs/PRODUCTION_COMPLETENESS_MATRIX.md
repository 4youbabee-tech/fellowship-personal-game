# PRODUCTION COMPLETENESS MATRIX

## 2026-09-22 - Pre-Unreal #561 deep-audit contract repair

On exact head `ed5af300852e6e2ce2264334c560af658250434b`, the core Pre-Unreal validator passed, but the subsequent deep audit failed because it searched only `ShireChapterAssetStreamingSubsystem.cpp` for the `FStreamableManager` type marker. The type is declared in the subsystem header while the cpp contains the async request path. The deep audit is corrected to validate the header+cpp contract together and still reject synchronous `LoadObject` in the streaming cpp.

This changes static validation only. It does not close the registered checkpoint/save-restore/rollback or ambient-life findings and does not promote compile, PIE, device, performance or visual status.

## 2026-09-22 - playability audit intake and PG-117 static-gate repair

A source review of the owner-forwarded Work findings on `170ebd857bece56a6d7f76f4928efe0eb3426af2` confirms open persistence/transition and living-world risks: checkpoint capture is not world-commit synchronized, cross-chapter restore can apply a transform before world commit, rollback is not yet a coherent playable prior-state transaction, ambient placement lacks a ground-safe collision contract, and ambient population still has SpawnActor/Destroy plus direct LoadObject debt. These are registered repair work, not accepted runtime fixes.

Pre-Unreal #560 reached and passed the core validation phase, then failed one stale PG-117 assertion because V10 world/life is now the global current visual wave. The guard is narrowed to preserve the historical hero-equipment V4 asset block without pinning the whole visual plan to V4. No chapter maturity, compile, PIE, device, performance or visual column is promoted by this static-guard correction.

## 2026-09-22 - PR #67 validation-gate repair

Pre-Unreal #558 on exact head `809325a64547744f0cc4992d76c42fb7e0862d82` failed with two static-guard errors caused by PG-111 still describing the V9 fixed-halving world-life contract. The integration branch already uses the V10 chapter density profile and `DangerPopulationFraction` model. PG-111 is being aligned to that existing V10 runtime/data contract without changing gameplay behavior.

Unreal Build #393 on the same SHA did not reach C++ compilation. The self-hosted runner identity `NT AUTHORITY\\NETWORK SERVICE` was denied read access to UE4.27.2 `WorldGridMaterial.uasset` on six consecutive engine-content probes. Therefore this wave remains **STATIC-PENDING** and no COMPILE/PIE/device/visual column is promoted by this repair.

## 2026-09-21 - continuous-session transition regression

A new runtime audit now requires one live session to traverse all eight Part I chapter identities, route switching, committed-world/living-world revision synchronization and disk-save roundtrip. This is implementation coverage only; no chapter is promoted to PIE/device acceptance until exact-head engine and owner evidence exist.

## 2026-09-21 - comprehensive foundation integration

Startup grounding, QA/performance guardrails, V10 regional living-world behavior and transactional chapter commit coordination are now being consolidated on one integration branch. Asset preload and visible-world commit are separated; living-world chapter state follows committed world revision rather than requested quest state.

Current status: **IMPLEMENTED / STATIC-PENDING** for the newest integration changes. No chapter validation column is promoted until exact-head Pre-Unreal, UE4 build/runtime and defect-specific PIE evidence exist.

## 2026-09-21 - visual-performance architecture guardrails

The project now tracks a measured visual-performance architecture contract: async/soft heavy assets, instanced+cull repeated detail, bounded Tick usage, role-appropriate LOD/material policy and evidence-driven lighting/shadow selection. Static guards protect the currently proven async/HISM/non-ticking-builder patterns.

This does not promote any chapter's performance, PIE, device or visual status. Draw-call, frame-time, streaming-pool, resident-memory, LOD and lighting/shadow comparisons remain target-device work.

## 2026-09-21 - engine Automation Framework QA wave

The project now has an initial UE Automation Framework layer in addition to static validation and runtime smoke. The first tests cover SaveGame default/schema invariants and post-import existence of all streamed chapter packages. Startup grounding proof now waits two seconds before PASS. These are implementation changes only; engine execution and defect-specific PIE evidence remain pending.

## 2026-09-21 - automated QA immune-system foundation

A layered automated QA initiative is now tracked as `REQ-QA-002`. The first wave adds Unreal Automation Framework coverage and exact-head CI execution after compile/import. Later world/nav/animation/performance/memory suites remain pending measured implementation. This does not alter any PIE/device/visual acceptance status.

## 2026-09-21 - deterministic P1C01 spawn collision support

The startup repair adds a hidden Engine BasicShapes support pad at the P1C01 authored road start so initial collision no longer depends on imported OBJ simple-collision generation. This strengthens the fix candidate only; COMPILE/PIE/device/visual status remains unchanged until exact-head proof exists.

## 2026-09-21 - startup grounding regression repair

A P1C01 PIE fall-through remains an open runtime defect despite an earlier spawn-height/placement change. The isolated fix removes pre-world GameMode teleporting, holds initial gravity until world commit, resolves a blocking floor before release, and adds startup/chapter grounding regression markers.

This is a **FIX_CANDIDATE**, not an accepted fix. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED status is added until the exact fix head completes engine validation and the original owner-observed P1C01 symptom is rechecked.

## Verification evidence correction and production continuation

Historical machine baseline: `develop@f7c2b081e7b064fcf27bb4c80124b21f351331ab`.

Pre-Unreal Validation #264 and Unreal Build Validation #99 passed on that baseline, including compile/import, startup, headless chapter audits and warning-debt checks. Those are valid machine checks, but they are **not** Real PIE/device visual-performance proof.

A prior conversation-level owner confirmation was incorrectly promoted into `PIE_TESTED` for all eight chapters without chapter-specific FPS, screenshot/video, or chapter-specific notes. That promotion is withdrawn. The owner confirmation remains historical authorization to resume construction; it is not chapter-by-chapter verification evidence.

Future `PIE_TESTED` / `PIE_TESTED_WITH_ISSUES` promotion requires an exact commit plus at least one chapter-specific signal: numeric FPS, screenshot/video evidence, or a concrete note unique to that chapter. Generic copied wording is rejected by PG-057.

### Current Real PIE/device evidence

| Chapter | Real PIE evidence | Stability | Crash | Target laptop perf | NPC routines | NPC-to-NPC | Named memory/context | Weather/atmosphere | Notes |
|---|---|---|---|---|---|---|---|---|---|
| P1C01 Shire | NOT_RUN | HEADLESS_ONLY | NO_HEADLESS_BLOCKER | NOT_MEASURED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | Re-establish as the chapter-specific visual/performance reference first |
| P1C02 Bree | NOT_RUN | HEADLESS_ONLY | NO_HEADLESS_BLOCKER | NOT_MEASURED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | Await chapter-specific evidence |
| P1C03 Weathertop/Ford | NOT_RUN | HEADLESS_ONLY | NO_HEADLESS_BLOCKER | NOT_MEASURED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | Await chapter-specific evidence |
| P1C04 Rivendell | NOT_RUN | HEADLESS_ONLY | NO_HEADLESS_BLOCKER | NOT_MEASURED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | Await chapter-specific evidence |
| P1C05 Road/Caradhras/West Gate | NOT_RUN | HEADLESS_ONLY | NO_HEADLESS_BLOCKER | NOT_MEASURED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | Await chapter-specific evidence |
| P1C06 Moria | NOT_RUN | HEADLESS_ONLY | NO_HEADLESS_BLOCKER | NOT_MEASURED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | Civilian baseline remains intentionally zero; Real PIE evidence still required |
| P1C07 Lothlorien | NOT_RUN | HEADLESS_ONLY | NO_HEADLESS_BLOCKER | NOT_MEASURED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | Await chapter-specific evidence |
| P1C08 Anduin/Amon Hen | NOT_RUN | HEADLESS_ONLY | NO_HEADLESS_BLOCKER | NOT_MEASURED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | Await chapter-specific evidence |

Engineering, source, asset-foundation and automated regression work may continue behind existing gates. Visual/performance acceptance and any `Production 100%` claim remain blocked until chapter-specific evidence exists.

This file prevents major game pillars from depending on chat memory.

A chapter is not complete because its quest path works. Every chapter must be checked across all production pillars.

## Status
NOT_STARTED / FOUNDATION / PROTOTYPE / FUNCTIONAL / POLISH_PENDING / ACCEPTED

## Mandatory pillars
1. Canon/story
2. Main gameplay loop
3. Exploration/side content
4. Character visual identity
5. Body animation
6. Facial acting / gaze / lip-sync
7. Spoken voice
8. Subtitles/dialogue
9. Music
10. SFX/foley
11. Ambience
12. NPC routines/social life
13. Enemy/creature AI
14. Combat/stealth when story requires it
15. Terrain/geography/scale
16. Architecture/props
17. Vegetation/biome
18. Weather/time/atmosphere
19. Cinematic presentation
20. Save/load continuity
21. Performance on target laptop
22. Accessibility/readability
23. Guardian/static validation
24. UE4.27 compile
25. PIE/device test

| Chapter | Story | Gameplay | Exploration | Characters | Face/Anim | Voice | Audio | AI/Life | Combat | Geography | Atmosphere | Cinematic | Save | Perf | PIE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1C01 Shire | FUNCTIONAL | FUNCTIONAL | FUNCTIONAL | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | FUNCTIONAL | FUNCTIONAL stealth | FUNCTIONAL | FUNCTIONAL | PROTOTYPE | FUNCTIONAL | PROTOTYPE | PENDING |
| P1C02 Bree | FUNCTIONAL | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | NOT_STARTED | PENDING |
| P1C03 Weathertop/Ford | FUNCTIONAL | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | NOT_STARTED | PENDING |
| P1C04 Rivendell | FUNCTIONAL | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | PROTOTYPE | N/A | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | NOT_STARTED | PENDING |
| P1C05 Road/Caradhras/West Gate | FUNCTIONAL | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | NOT_STARTED | PENDING |
| P1C06 Moria | FUNCTIONAL | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | NOT_STARTED | PENDING |
| P1C07 Lothlorien | FUNCTIONAL | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | PROTOTYPE | N/A | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | NOT_STARTED | PENDING |
| P1C08 Anduin/Amon Hen | FUNCTIONAL | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | NOT_STARTED | PENDING |

## Validation evidence versus maturity

The status table above describes **production maturity**. Validation proof is recorded separately so a successful compile/import is never confused with visual or gameplay acceptance.

### P1C01 Shire production environment
- CP28 introduced project-managed production source assets for Shire environment/props and runtime code now prefers imported production meshes while retaining BasicShapes as fallbacks.
- The production asset pipeline is COMPILE-TESTED and ASSET-IMPORT-TESTED on UE4.27.2.
- Validated baseline `e739ba6e364d0316cf5b7fe10c1f8ecaa13d417e` passed Pre-Unreal Validation #113 and Unreal Build Validation #11; the production importer reported `50 files, 0 failures`.
- The newer Shire visual content is still pending focused PIE traversal, target-device performance review and VISUALLY-ACCEPTED status.
- Character visual identity remains PROTOTYPE/FOUNDATION where the final rigged/animated/voiced production character standard is not yet satisfied.

### Repository build gate
- CP29 established a self-hosted Windows UE4.27.2 runner on the target laptop.
- Every pushed `develop` commit is eligible for the exact-commit UE4.27.2 C++ build and production asset-import gate.
- Green CI never substitutes for PIE, device or visual acceptance.

### Source architecture / handoff
- `Source/ShireJourney/README.md` is the code-level handoff entry point inside the runtime module.
- `Data/SourceArchitecturePlan.json` assigns every runtime source file to a domain and a controlled target path for the planned Public/Private folder migration.
- Project Guardian must reject untracked runtime source files so a new human or automated programmer cannot silently expand the module without updating the architecture map.

## Voice rule
Every runtime non-empty VO_* identifier must exist in Data/VoiceCuePlan.csv.
Voice status remains FOUNDATION while required voice assets are ASSET_PENDING.

## Update rule
Whenever a chapter, route, enemy, biome, mechanic or major story beat changes:
- update this matrix,
- update the relevant story/audio plan,
- add Guardian validation where machine-checkable,
- do not mark ACCEPTED without real UE4.27/PIE evidence.
