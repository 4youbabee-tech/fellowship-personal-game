# PRODUCTION COMPLETENESS MATRIX

## Post-CP54 verification completion and expansion resume

Verified merged baseline: `develop@f7c2b081e7b064fcf27bb4c80124b21f351331ab`.

Pre-Unreal Validation #264 and Unreal Build Validation #99 passed on the merged baseline, including compile/import, playable startup, all eight headless chapter audits and the warning-debt guard. The project owner then explicitly confirmed the planned verification/check/fix pass complete and directed construction/expansion to resume.

The owner sign-off is recorded in `Docs/PIE_VERIFICATION_SIGNOFF_2026-09-19.md` and `Data/PIEVerificationEvidence.json`. Numeric FPS/hitch/memory values were not supplied in chat and are therefore not invented.

### Current machine verification candidate

PR #45 successfully boot-audited **all eight Part I runtime chapters** in UE4.27.2 headless mode, including the expected chapter builder, living-world initialization and weather-context initialization, with no fatal/assert/ensure blocker in that audit. This is stronger than the previous P1C01-only startup smoke, but it still does **not** change any Real PIE cell below from NOT_RUN.

Structured human evidence for any future PIE status change must also be written to `Data/PIEVerificationEvidence.json`; PG-057 rejects unsupported claims.

| Chapter | Real PIE on CP54 head | Stability | Crash | Target laptop perf | NPC routines | NPC-to-NPC | Named memory/context | Weather/atmosphere | Notes |
|---|---|---|---|---|---|---|---|---|---|
| P1C01 Shire | PIE_TESTED | OWNER_CONFIRMED | NO_BLOCKER_REPORTED | CHECKED_NO_NUMERIC_LOG | OWNER_CONFIRMED | OWNER_CONFIRMED | OWNER_CONFIRMED | OWNER_CONFIRMED | Owner-completed verification pass; see sign-off record |
| P1C02 Bree | PIE_TESTED | OWNER_CONFIRMED | NO_BLOCKER_REPORTED | CHECKED_NO_NUMERIC_LOG | OWNER_CONFIRMED | OWNER_CONFIRMED | OWNER_CONFIRMED | OWNER_CONFIRMED | Owner-completed verification pass |
| P1C03 Weathertop/Ford | PIE_TESTED | OWNER_CONFIRMED | NO_BLOCKER_REPORTED | CHECKED_NO_NUMERIC_LOG | OWNER_CONFIRMED | OWNER_CONFIRMED | OWNER_CONFIRMED | OWNER_CONFIRMED | Owner-completed verification pass |
| P1C04 Rivendell | PIE_TESTED | OWNER_CONFIRMED | NO_BLOCKER_REPORTED | CHECKED_NO_NUMERIC_LOG | OWNER_CONFIRMED | OWNER_CONFIRMED | OWNER_CONFIRMED | OWNER_CONFIRMED | Owner-completed verification pass |
| P1C05 Road/Caradhras/West Gate | PIE_TESTED | OWNER_CONFIRMED | NO_BLOCKER_REPORTED | CHECKED_NO_NUMERIC_LOG | OWNER_CONFIRMED | OWNER_CONFIRMED | OWNER_CONFIRMED | OWNER_CONFIRMED | Owner-completed verification pass |
| P1C06 Moria | PIE_TESTED | OWNER_CONFIRMED | NO_BLOCKER_REPORTED | CHECKED_NO_NUMERIC_LOG | OWNER_CONFIRMED | OWNER_CONFIRMED | OWNER_CONFIRMED | OWNER_CONFIRMED | Civilian baseline remains intentionally zero |
| P1C07 Lothlorien | PIE_TESTED | OWNER_CONFIRMED | NO_BLOCKER_REPORTED | CHECKED_NO_NUMERIC_LOG | OWNER_CONFIRMED | OWNER_CONFIRMED | OWNER_CONFIRMED | OWNER_CONFIRMED | Owner-completed verification pass |
| P1C08 Anduin/Amon Hen | PIE_TESTED | OWNER_CONFIRMED | NO_BLOCKER_REPORTED | CHECKED_NO_NUMERIC_LOG | OWNER_CONFIRMED | OWNER_CONFIRMED | OWNER_CONFIRMED | OWNER_CONFIRMED | Owner-completed verification pass |

Blocking failure means crash, progression dead-end, save/load failure, missing required runtime system, or severe target-device performance regression. The post-CP54 baseline audit is now owner-confirmed complete; CP55+ may proceed behind the existing regression gates.

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
| P1C01 Shire | FUNCTIONAL | FUNCTIONAL | FUNCTIONAL | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | FUNCTIONAL | FUNCTIONAL stealth | FUNCTIONAL | FUNCTIONAL | PROTOTYPE | FUNCTIONAL | PROTOTYPE | FUNCTIONAL |
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
