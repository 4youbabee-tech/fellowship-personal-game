# DEVELOPMENT GATES

These rules are mandatory project discipline, not optional advice.

## Gate 0 — Branch safety
- work on `develop`,
- do not develop directly on `main`,
- inspect current `develop` head before editing,
- do not merge/release only because static CI is green.

## Gate 1 — Static validation
Every implementation change must:
- push to `develop`,
- pass Pre-Unreal Validation,
- fix every error before moving forward.

Static validation can check repository invariants. It cannot replace Unreal.

## Gate 2 — UE4.27 compile
Before a new major checkpoint:
- compile with UE4.27.2,
- pass UnrealHeaderTool,
- fix compile/UHT failures immediately.

A feature is not COMPILE-TESTED until this actually happens.

## Gate 3 — PIE
Exercise the relevant gameplay in Play In Editor.

For story/world changes test:
- entering the area,
- quest progression,
- interactions,
- dialogue,
- story beats,
- save/load,
- chapter/route transitions,
- alternate-route return.

A compiled feature is not automatically PIE-TESTED.

## Gate 4 — Target-device test
Test early on the intended laptop:
- DX11,
- 720p,
- Low/Medium,
- 8 GB RAM target,
- ~2 GB VRAM target,
- 30 FPS floor.

Performance testing is not an end-of-project task.

## Gate 5 — Documentation/data sync
Story, chapter, route, dialogue or music changes must update matching reference material in the same logical change.

Relevant files:
- `Docs/CURRENT_PROJECT_STATE.md`
- `Docs/WORLD_PRODUCTION_BLUEPRINT.md`
- `Docs/PRODUCTION_COMPLETENESS_MATRIX.md`
- `Source/ShireJourney/README.md`
- `Data/SourceArchitecturePlan.json`
- `Docs/STORY_CANON_BIBLE.md`
- `Docs/PART1_FELLOWSHIP_MASTERPLAN.md`
- `Data/WorldCheckpointPlan.csv`
- `Data/StoryBeatPlan.csv`
- `Data/DialogueIntent.csv`
- `Data/MusicCuePlan.csv`

Source-layout changes must update the source handoff README, architecture plan and static-validator path assumptions in the same logical change.

Do not knowingly create "we will fix docs later" debt.

Governor rule:
- every major region tracks STATIC / COMPILE / BOOT / TRAVERSAL / PERSISTENCE / PERFORMANCE / PACING / VISUAL in `Data/ExperienceQualityGates.json`;
- declared requirement conflicts must have an explicit decision or open-conflict record;
- a FAILED previously-passed critical gate blocks feature expansion until repaired/retested;
- PACING and VISUAL require human evidence and cannot be inferred from CI.

Requirement memory rule:
- meaningful user feature/design requests must be added or updated in `Data/ProjectRequirements.json`;
- living-world/NPC scope changes must update `Docs/LIVING_WORLD_AI_BLUEPRINT.md` and `Data/LivingWorldFeaturePlan.json`;
- a feature checkpoint must not silently mark an open requirement complete.

## Gate 6 — Vertical-slice priority
The Shire is the current quality bar.

Before aggressive scope expansion, prove:
- world readability,
- exploration rhythm,
- NPC life,
- quest flow,
- save/load,
- story presentation,
- audio routing,
- performance.

Other chapters may exist as prototype skeletons, but that does not make them production-complete.

## Gate 7 — Scope control
Until current Part I is stable:
- Part II / Part III stay roadmap/design only,
- do not implement a large system only because it is interesting,
- do not add a playable route without a strong story reason,
- prefer extending proven systems over creating parallel systems.

## Gate 8 — Failure discipline
When a gate fails:
1. stop feature expansion,
2. isolate failure,
3. fix failure,
4. rerun that gate,
5. continue only after it passes.

Do not stack new features on a known failing checkpoint.

## Gate 9 — Acceptance labels
Every checkpoint should record which are proven:
- STATIC-VALIDATED
- COMPILE-TESTED
- PIE-TESTED
- DEVICE-TESTED
- VISUALLY-ACCEPTED

## Gate 10 — Regression memory
A meaningful failure should not be fixed only once.

When a bug exposes a repeatable invariant:
1. fix the bug,
2. add or strengthen an automated guard where practical,
3. record the regression in `Docs/PROJECT_GUARDIAN.md`,
4. update `Data/ProjectGuardRules.json` when the rule is machine-checkable.

That is how this project "learns from mistakes".
