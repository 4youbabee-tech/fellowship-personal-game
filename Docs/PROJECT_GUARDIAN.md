# PROJECT GUARDIAN

Project Guardian is the project's regression memory.

It is intentionally deterministic. It does not use an LLM to rewrite story, code or design.
Its job is to catch known classes of mistakes early and force a human/developer to make an explicit decision.

## What "learning from mistakes" means here

When a meaningful error appears:
1. identify the invariant that was violated,
2. fix the immediate bug,
3. encode the invariant in automated validation when possible,
4. record the incident below,
5. require future commits to pass that guard.

This converts failures into permanent project knowledge.

## Machine-readable policy

`Data/ProjectGuardRules.json` stores rules such as:
- allowed runtime chapter IDs,
- approved current route IDs,
- allowed canon classes,
- required governance docs,
- required story/dialogue/music datasets,
- route episode naming rules.

`Scripts/pre_unreal_validate.py` consumes these rules on every CI run.

## Current hard guards

### PG-001 — Runtime chapter drift
**Past risk:** old design files used P1C09-P1C12 while runtime moved to eight chapter buckets.

**Guard:** StoryBeatPlan, DialogueIntent and MusicCuePlan may only use approved runtime chapter IDs from ProjectGuardRules.

### PG-002 — Story beat exists in one layer only
**Observed failure:** Isengard world beats landed before their presentation cues, causing Pre-Unreal Validation #74 to fail.

**Guard:** runtime presentation cue IDs and StoryBeatPlan story-beat IDs must match exactly; runtime story beat references must have presentation cues.

### PG-003 — Music plan drifts from runtime
**Risk:** presentation could reference music that is absent from the music plan, or the plan could describe dead cues.

**Guard:** non-empty runtime music cue references and MusicCuePlan cue IDs must match exactly.

### PG-004 — Unapproved route silently appears
**Risk:** adding parallel routes casually can overwrite scope and save assumptions.

**Guard:** CSV route IDs must be explicitly approved in ProjectGuardRules. Adding a future route requires consciously updating the rules.

### PG-005 — Canon class ambiguity
**Risk:** film, extended-film, lore-only and original gap-fill content can be mixed without labeling.

**Guard:** planning CSV CanonClass values are restricted to approved classes.

### PG-006 — Missing project memory
**Risk:** a lost conversation or a new programmer resumes from outdated assumptions.

**Guard:** CI requires CURRENT_PROJECT_STATE, DEVELOPMENT_GATES, PROJECT_GUARDIAN and STORY_CANON_BIBLE.

### PG-007 — Static green mistaken for playable
**Risk:** repository checks pass while C++/UHT/PIE has not been exercised.

**Guard:** this cannot be fully machine-proven by GitHub CI. The process guard is explicit acceptance labels and the hard UE4.27 gate in CURRENT_PROJECT_STATE.

### PG-008 — Route/save architecture disappears
**Risk:** future refactors accidentally remove route identity or per-route persistence.

**Guard:** validator checks for key route-state symbols in QuestSubsystem, SaveGame and ChapterWorldRouter.

### PG-009 — Audio/dialogue presentation dangling references
**Risk:** story cues reference dialogue/audio paths that do not exist.

**Guard:** existing validator checks runtime dialogue sequence coverage and audio subsystem event wiring.

### PG-010 — Route helper signature drift
**Observed failure:** the 2026-09-18 target-machine UE4.27 build reached C++ compilation and failed with C2660 because one fallback call still invoked `MovePlayerToChapterStart` with one argument after the helper was changed to require `(ChapterId, bRestoreRouteTransform)`.

**Guard:** static validation rejects known one-argument `MovePlayerToChapterStart` call forms.

### PG-011 — UE4.27 light-component downcast
**Observed failure:** the same real UE4.27 build failed with C2440 because `ADirectionalLight::GetLightComponent()` was assigned directly to `UDirectionalLightComponent*`. The static type in UE4.27 is a base light component pointer.

**Fix pattern:** use an explicit Unreal `Cast<UDirectionalLightComponent>(...)` or `Cast<USkyLightComponent>(...)` before using subclass APIs.

**Guard:** static validation rejects direct subclass-pointer assignment from `GetLightComponent()`.

### PG-012 — Move a light only after setting Movable
**Observed failure:** after the compile fixes, PIE launched successfully but UE4.27 logged: `LightComponent0 has to be 'Movable' if you'd like to move`.

**Root cause:** the Shire morning-atmosphere code rotated the existing Directional Light before setting its component mobility to `Movable`.

**Fix pattern:** set the Directional Light component mobility first, then change actor rotation.

**Guard:** static validation checks this ordering inside `ConfigureMorningAtmosphere`.

### PG-013 — UE4.27 AssetImportTask API compatibility
**Observed failure:** the 2026-09-18 target-machine build of the CP28 production-asset importer failed with C2039 because `UAssetImportTask` in UE4.27 does not expose a `bAsync` member.

**Root cause:** the editor import commandlet used a newer-engine task property while the project is locked to UE4.27.2.

**Fix pattern:** use only the UE4.27-supported `UAssetImportTask` fields and let `ImportAssetTasks` run without assigning `bAsync`.

**Guard:** static validation rejects `Task->bAsync` / `->bAsync` in the production import commandlet.

### PG-014 — Editor commandlet module must load before commandlet discovery
**Observed failure:** the 2026-09-18 target-machine asset-import run exited with `Failed to find commandlet class ShireProductionImportCommandlet` even though the editor-tools module and generated commandlet code had compiled.

**Root cause:** `ShireJourneyEditorTools` was configured with `LoadingPhase: PostEngineInit`. UE4.27 resolves the requested `-run=` commandlet before that phase, so the class was not registered when lookup occurred.

**Fix pattern:** keep `ShireJourneyEditorTools` as an `Editor` module but load it at the `Default` phase.

**Guard:** static validation requires the editor-tools module to remain `Type: Editor` with `LoadingPhase: Default`.

### PG-015 — Windows cmd success branch must clear stale ERRORLEVEL
**Observed failure:** Unreal Build Validation #3 reached the target machine, bootstrapped Git, checked out the exact commit, verified UE4.27.2, and correctly reported `Unreal Editor is closed.`, but the step still exited with code 1 and skipped the real build.

**Root cause:** `tasklist | find` intentionally returns 1 when UE4Editor is absent. In `cmd.exe`, the following `echo` does not clear that stale ERRORLEVEL, so the otherwise-successful step inherited exit code 1.

**Fix pattern:** after confirming the editor is closed, explicitly `exit /b 0`.

**Guard:** static validation requires the self-hosted workflow's editor-closed success branch to explicitly return zero.

### PG-016 — UE4.27 AtmosphericFog public-header compatibility
**Observed failure:** Unreal Build Validation #5 compiled the new Shire production pass on the self-hosted UE4.27.2 machine and failed with C1083 because `Engine/AtmosphericFog.h` is not available as a public include in that installed engine build.

**Root cause:** the atmosphere cleanup referenced a legacy fog class/header directly instead of using an engine-version-neutral actor cleanup path.

**Fix pattern:** do not include `Engine/AtmosphericFog.h`; locate the legacy actor generically and remove it without a compile-time dependency on that unavailable header.

**Guard:** static validation rejects that direct include.

### PG-017 — LFS-tracked binaries must be Git LFS pointers
**Observed failure:** the same run reported seven texture files that “should have been pointers, but weren't” because raw TGA blobs were committed through the GitHub contents/Git-data path while `.gitattributes` routes `.tga` through Git LFS.

**Root cause:** the file extension was LFS-managed, but the stored Git object was the raw binary instead of an LFS pointer.

**Fix pattern:** assets with LFS-managed extensions must enter Git through a real LFS upload. Small generated source textures that do not need LFS may use an Unreal-supported non-LFS extension such as BMP.

**Guard:** static validation rejects raw production binaries using extensions managed by the repository's current LFS policy.

## What Guardian must never do automatically

- change canon,
- invent a replacement scene,
- rewrite dialogue,
- auto-merge branches,
- silently alter quest results,
- "fix" a compile error by deleting gameplay,
- expand scope,
- mark a feature PIE-tested without a real PIE test.

Guardian detects and blocks. Humans/developers decide the correction.

## Adding a new regression rule

When a new repeatable failure is found, add a new PG entry with:
- symptom,
- root invariant,
- automated check if possible,
- manual test if automation is impossible,
- commit/run that exposed it when useful.

Then update ProjectGuardRules or pre_unreal_validate.py in the same fix when practical.
