# PRODUCTION COMPLETENESS MATRIX

## 2026-09-21 - V10 recovery/documentation synchronization

PR #62 contains real runtime/source changes for early-realm cultural life and chapter-tuned density in Shire, Bree, Rivendell and Lothlorien. Exact head `d6533289dda37458b54bf5b63b82251502900eab` passed Pre-Unreal #546 and Unreal Build #381 before this recovery/documentation synchronization.

Because this synchronization creates a newer PR #62 head, the d653 result is ancestor evidence only for the refreshed candidate. The new head must earn fresh exact-head Pre-Unreal and Unreal validation before integration. No new `PIE-TESTED`, `DEVICE-TESTED` or `VISUALLY-ACCEPTED` status is claimed.

PR #63 transition coordination is not integrated into V10. Its Pre-Unreal #547 is green, while Unreal #382 remains queued/not started. Its `LivingWorldDirector` and Governor changes must be reconciled on top of the post-V10 develop baseline rather than overwriting the V10 density/profile work.

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
