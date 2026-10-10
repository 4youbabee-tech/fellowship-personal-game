# DEVELOPMENT GATES

These rules are mandatory project discipline, not optional advice.

## Gate 0 — Branch safety
- `develop` is the integration baseline; `main` is the stable release branch,
- implement on a short-lived single-purpose candidate branch/PR targeting `develop` (or the one Governor-approved integration train),
- inspect both the current `develop` baseline and exact candidate HEAD before editing,
- do not use direct `develop` commits as the normal production workflow,
- do not merge/release only because static CI is green.

## Gate 1 — Static validation
Every implementation change must:
- push the exact candidate HEAD to its branch/PR targeting `develop`,
- pass Pre-Unreal Validation on that exact HEAD,
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
Test early on the owner's primary physical laptop:
- Intel Core i7-6498DU @ 2.50GHz,
- AMD Radeon R5 M330 GPU (2039 MB reported VRAM, 2 GB class),
- Windows 11 Pro 64-bit; OS DirectX 12 present, no DX12 Ultimate,
- UE4.27.2 **DX11 RHI**, not a forced DX12 renderer,
- 1280x720; Balanced Medium with selective High for important visuals,
- 8 GB RAM,
- stable 30 FPS target (not yet performance accepted).

Record exact executable/commit and device identity, per-route FPS and p95/p99 frame time, hitch counts, resident RAM/texture/VRAM measurements and representative traversal. Build/runner hardware snapshots alone are NOT DEVICE-TESTED. Performance testing is not an end-of-project task.

## Gate 5 — Documentation/data sync
Story, chapter, route, dialogue or music changes must update matching reference material in the same logical change.

Relevant files:
- `Docs/CURRENT_PROJECT_STATE.md`
- `Docs/WORLD_PRODUCTION_BLUEPRINT.md`
- `Docs/PRODUCTION_COMPLETENESS_MATRIX.md`
- `Source/ShireJourney/README.md`
- `Data/SourceArchitecturePlan.json`
- `Docs/STORY_CANON_BIBLE.md`
- `Data/OwnerSourceReferenceIndex.json`
- `Docs/WORLD_DETAIL_LEDGER.md`
- `Docs/PART1_FELLOWSHIP_MASTERPLAN.md`
- `Data/WorldCheckpointPlan.csv`
- `Data/StoryBeatPlan.csv`
- `Data/DialogueIntent.csv`
- `Data/MusicCuePlan.csv`

Source-layout changes must update the source handoff README, architecture plan and static-validator path assumptions in the same logical change.

Do not knowingly create "we will fix docs later" debt.

Source/story coverage rule:
- story/world/mission/chapter changes must preserve the Timeline -> film/screenplay -> Tolkien -> Sources 02-11 routing contract;
- meaningful discovered source detail must be implemented or explicitly dispositioned rather than silently omitted;
- compatible Tolkien book-only events/details may be playable when they preserve locked film outcomes and knowledge boundaries;
- story compression is not an optimization technique.

Single-authority rule:
- `Data/ProjectGovernor.json` is the only project-management decision authority;
- supporting plans/docs may add implementation detail but cannot independently change priorities, conflicts, active gate or acceptance state;
- reintroducing secondary authority files is a CI failure.

Governor rule:
- every major region tracks STATIC / COMPILE / BOOT / TRAVERSAL / PERSISTENCE / PERFORMANCE / PACING / VISUAL in `Data/ProjectGovernor.json`;
- declared requirement conflicts must have an explicit decision or open-conflict record;
- a FAILED previously-passed critical gate blocks feature expansion until repaired/retested;
- PACING and VISUAL require human evidence and cannot be inferred from CI.

Requirement memory rule:
- meaningful user feature/design requests must be added or updated in `Data/ProjectGovernor.json`;
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
- Gate 6/7 may delay when a chapter/runtime lane opens, but it does not authorize deleting or shortening planned source-backed story/detail coverage.
- Part II / Part III stay roadmap/design only,
- do not implement a large system only because it is interesting,
- do not add a playable route without a strong story reason,
- prefer extending proven systems over creating parallel systems.

## Gate 8 — Failure discipline
When a technical gate fails:
1. stop the affected runtime/integration lane,
2. isolate the concrete failure,
3. fix the smallest failing layer,
4. rerun that gate,
5. resume that lane only after it passes.

Independent source/PDF/warehouse/design preparation may continue when the failure does not invalidate it. Do not stack new runtime changes on a known failing runtime checkpoint.

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


## Gate 11 — Production acceleration
- The repository Project Manager may publish a 24-hour owner progress report; it is informational and never a production gate.
- Closed W00 repairs remain historical unless concrete regression evidence reopens them.
- Live PR numbers and candidate branch names come from GitHub and are not duplicated as fail-closed build requirements.
- Batch management/documentation updates by meaningful production wave.
- Source indexing, provenance capture and non-runtime warehouse staging do not require an Unreal build.
- Gate 6/7 still controls broad runtime expansion; whole-game source and asset preparation may proceed in parallel.
