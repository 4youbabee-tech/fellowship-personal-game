## 2026-10-11 — Root-cause repair of local PIE classifier (PR #359)

- Regression: transitive proof allowlist != main classifier allowlist. Execute actual classifier with positive and negative exact-path cases; do not whitelist unknown executables or disable required Unreal, PBR and Gate 6/7 validations. Pre-Unreal Run #38093231196 failed `pie-preview-safe-with-proof: expected inherit, got full`: the two exact paths appeared only in the transitive core-proof allowlist, not in the main `$safeExact` set used by `$fullImpact`. Add them to the actual exact-path classifier and cover lookalike names, mixed runtime and Config changes in the real classifier regression. Parent engine proof remains mandatory, otherwise full validation. PR #358's actual preview command/test still requires exact-head static execution prior to merging. Candidate awaiting CI; no new Unreal/PIE/device/visual/FPS acceptance.

## 2026-10-10 — P1C01 package inventory and UE4 import false-green protections

- Risk: hashed FBX, saved `.uasset` pairs and generic Unreal startup may be green, yet material-slot binding is not proven and package preflight fails because `total_unique_production_packages` is stale after PBR bank promotion. Fail-closed rule: require each selected P1C01 FBX's own UE import material-slot log evidence, then atomically recompute existing streaming audit counts from the actual resident-bank manifest and require runtime actor placement log before Windows package delivery. Add deterministic positive and negative regression tests; do not mark human visual or hardware gates from headless CI.

## 2026-10-10 — P1C01 missing physical PBR placement false-green prevention

- Regression risk: a successful import and gameplay startup can still display zero verified PBR decorations when soft objects are not resident at world build time. New deterministic offline cases plus a real headless-runtime placement-count verifier must block shipping the P1C01 PBR test candidate if `P1C01_PBR_DECOR_RUNTIME` is missing, partial, or has omitted objects, even when all `.uasset` packages exist. Retain one runtime writer and no false PIE/device/visual labels. Exact-head runtime evidence pending.

## 2026-10-10 — P1C01 verified PBR material-parent regression (PG-169)

- CI #38052565591 FAILED: original C3 foliage parent invariant `DesiredMaterialParent = ProductionMaterialParent` was displaced by conditional new PBR master selection. Restored original default assignment with explicit verified-PBR-only override, preserving foliage identity and preventing regression. Exact-head Pre-Unreal retest pending; no Unreal visual/P1C01 Gate6/7 proof yet.

## 2026-10-10 — P1C01 physical CC0 PBR-to-UE4 visual production bridge (candidate, evidence pending)

- Manager authority: DEC-078/104/105, REQ-PROD-011, W01/P1C01 only. Actual persistent warehouse Run #38049193046 completed SUCCESS, providing immutable 39+60 source and 39+59 prepared PBR files; this is source storage evidence, not engine/render evidence.
- This PR adds an exact SHA256 checked, bounded (up to 16 static assets / 144 MiB) source bridge from the persistent two-wave CC0 warehouse into the existing `SourceAssets/Production/World/Shire/VerifiedPBR` importer. Reject held-identity, held-biome, corrupted, multimap/multi-material and non-Shire/unrelated candidates. Avoid provider redownload, hard runtime references and any character FBX.
- Unreal importer now binds verified single-material FBX to a real PBR master: BaseColor + tangent-space NormalDX + packed ORM (ambient occlusion R, roughness G, metallic B), with non-sRGB packed/normal imports. Preserve existing OBJ asset bank unchanged.
- Existing `UShireChapterAssetStreamingSubsystem` preloads selected soft paths via `Data/ChapterAssetStreamingPlan.json`. Existing `AShirePrototypeWorldBuilder` adds at most 16 optional, non-colliding, low-shadow static decorative pieces after world commit and never synchronously loads meshes. Canonical route/story/quest ownership and actor pooling remain unchanged.
- A dedicated GitHub-hosted offline source test + serialized Windows UE4.27.2 workflow runs actual source stage, editor build, production import, `.uasset` presence, automation, startup, all chapters, state persistence, warning guard, cook and packaged startup. Only success can publish a playable Windows **test candidate**. The new visual packet is NOT declared PIE, device, human visual or Gate 6/7 accepted.
- Until exact-head tests run, this is a source implementation candidate. Fix compile/import/runtime failures on this same PR before merge; avoid new feature lanes until machine-green. No final Windows release requested.

## 2026-10-10 — ambientCG cross-lane duplicate download regression guard (candidate)

- Observed live warehouse #38057877090 SUCCESS: `AMBIENTCG_WAREHOUSE_STAGE_PASS files=22 skipped=24 bytes=1178435662`, `REGION_SOURCE_RECEIPT_AUDIT_PASS files=22 skipped=24 reserve=175388110848`. These are actual SHA256-audited source-only bytes, not Unreal imports.
- Root-cause in `Scripts/stage_ambientcg_warehouse.ps1`: ten regional material queries can return the same provider asset ID. Run logs show repeated downloads of Rock064, Ground111 and PavingStones151; prior script only guarded identical destination paths and did not deduplicate across category folders. Add accepted-ID set updated ONLY after successful source SHA256 receipt; skip later duplicate IDs before network requests. Byte-cap failure must not remove previously valid cached archive; do not trigger or repeat the completed batch. Existing Quaternius zero-payload Pre-Unreal step also checks the ambientCG dedup code order offline.
- Candidate until exact-head preflight. One persistent warehouse writer and 6 GiB reserve retained. No P1C01 runtime change, PIE, target-device FPS, visual or Gate6/7 credit.

## 2026-10-10 — ambientCG cross-lane duplicate download regression guard (candidate)

- Observed live warehouse #38057877090 SUCCESS: `AMBIENTCG_WAREHOUSE_STAGE_PASS files=22 skipped=24 bytes=1178435662`, `REGION_SOURCE_RECEIPT_AUDIT_PASS files=22 skipped=24 reserve=175388110848`. These are actual SHA256-audited source-only bytes, not Unreal imports.
- Root-cause in `Scripts/stage_ambientcg_warehouse.ps1`: ten regional material queries can return the same provider asset ID. Run logs show repeated downloads of Rock064, Ground111 and PavingStones151; prior script only guarded identical destination paths and did not deduplicate across category folders. Add accepted-ID set updated ONLY after successful source SHA256 receipt; skip later duplicate IDs before network requests. Byte-cap failure must not remove previously valid cached archive; do not trigger or repeat the completed batch. Existing Quaternius zero-payload Pre-Unreal step also checks the ambientCG dedup code order offline.
- Candidate until exact-head preflight. One persistent warehouse writer and 6 GiB reserve retained. No P1C01 runtime change, PIE, target-device FPS, visual or Gate6/7 credit.

## 2026-10-10 — P1C01 mandatory Project Governor work-start and five-lane enforcement

- DEC-104 is enforced as a mandatory physical production entrypoint. Existing five-lane read-only preflight is NOT proof of generated assets. Scripts/governor_work_start.py runs the full Project Governor and checks DEC-078/104/105, REQ-PROD-011, active P1C01 gate, one runtime writer, one warehouse writer, 6 GiB reserve and five lane identities before production.
- Production workflows for Unreal, warehouse, skeletal characters, visual source and chapter closure now require the manager. Pre-Unreal regression tests forbid their bypass. Chapter closure source writer shares warehouse-stage concurrency with durable source staging.
- Evidence: source changes submitted for exact-head CI. No new Unreal asset import, chapter PIE, target device measurement or visual acceptance is inferred. The existing warehouse #38049193046 is independent and not cancelled.

## 2026-10-10 — PG-026 release artifact versus failure-logs contract

- Pre-Unreal #38045489962 failed: PG-026 failure logging may not depend on artifact upload quota. On isolated fix PR #336, removed `always()` log artifact upload, kept console failure logs and allowed a success-only packaged Windows playable candidate. Static exact-head checks and UE results pending. No Gate6/7 credit.

## 2026-10-10 — Windows warehouse nested original texture path

Observed `StageError: UNSAFE_RELATIVE_PATH` at `persist()` in Windows job 114185324499; nested provider `Path` was stringified using Windows separators. Enforce platform-independent `.as_posix()` serialization for receipt keys and add real nested PNG offline test. Full source39/pbr39 archives remain durable and must not be re-fetched. See run #38042482514.

## 2026-10-10 — Regression: P1C01 default map, cook and packaged startup must agree

Root issue: UE4 template default floor can visually occlude world generated by `AShirePrototypeWorldBuilder`, while the local preview uses Entry. Permanent guard: `Scripts/test_p1c01_delivery_entry_map.py` validates the engine defaults, runtime smoke, cook map, packaged startup and downloadable artifact step. Do not classify source-only tests as PIE/device/human visual evidence. Any drift fails hosted CI before reserving UE4 runner.

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

### PG-018 — Checkpoint validation must use initialized story data
**Observed failure:** Pre-Unreal Validation #111 on CP30 commit `10ac91e...` crashed with `NameError: name 'story_plan_ids' is not defined` while validating `Data/WorldCheckpointPlan.csv`.

**Root cause:** the new checkpoint-validation block depended on a derived variable that was initialized later in `pre_unreal_validate.py`, so the validator failed before it could evaluate project data.

**Fix pattern:** derive checkpoint story-beat membership directly from the already-loaded `story_rows` at the point of validation, or otherwise ensure every derived dependency is initialized before first use.

**Guard:** Pre-Unreal Validation executes `Scripts/pre_unreal_validate.py` on every `develop` push, and the default-branch 20-minute workflow independently checks the current `develop` tree. A validator crash is a hard gate failure and must be fixed before feature expansion.

### PG-019 — Runtime source architecture drift
**Risk:** the game grows across many C++ files, a chat/handoff is lost, or a new programmer adds/moves files without knowing module ownership and validator assumptions.

**Contract:** `Source/ShireJourney/README.md` is the code-level handoff entry point and `Data/SourceArchitecturePlan.json` maps every runtime `.h`, `.cpp` and module `.cs` file to an engineering domain and controlled target path.

**Guard:** Pre-Unreal Validation compares the runtime module's actual source files with the architecture plan, rejects missing/duplicate/stale entries, validates approved domains/status values and enforces the planned Public/Private target-path convention.

**Migration rule:** physical folder migration must be a dedicated maintenance change. It must update include paths, validator path lookups and the architecture manifest together, then pass static validation and the real UE4.27.2 self-hosted build before acceptance.

### PG-020 — User requirements must survive lost chats and developer handoffs
**Risk:** a meaningful user request exists only in conversation memory, then disappears when a chat is deleted, context is truncated or a new programmer takes over.

**Contract:** `Data/ProjectGovernor.json` is the single authoritative machine-readable project governor containing the permanent requirement ledger. Each meaningful request has a stable ID, intent, priority, status, evidence, missing work and acceptance criteria.

**Guard:** Pre-Unreal Validation validates unique requirement IDs, approved statuses/priorities and required acceptance criteria. Critical long-lived requirements such as project memory, living world, NPC intelligence, save continuity and performance must remain present.

**Process rule:** implementation/checkpoint changes must update the relevant requirement entry instead of silently leaving the ledger stale.

### PG-021 — Living-world/NPC intelligence scope must remain explicit
**Risk:** the project says "living world" or "smart NPCs" without distinguishing foundations from the much larger unfinished target, causing future developers to assume social pauses or authored dialogue already satisfy the requirement.

**Contract:** `Docs/LIVING_WORLD_AI_BLUEPRINT.md` defines the target behavior and `Data/LivingWorldFeaturePlan.json` records phases LW0-LW6 and individual feature status.

**Guard:** Pre-Unreal Validation requires all living-world phases and critical feature contracts including routines, NPC conversation runtime, memory schema, micro-events, fauna/environment motion and knowledge guards.

**Acceptance rule:** current ambient routines/awareness/social pauses are foundations only. NPC-to-NPC dialogue, persistent named-NPC memory/relationships and bounded dialogue intelligence may not be called implemented until runtime evidence exists.

### PG-023 — Secondary project authority is forbidden
**Risk:** multiple requirements/decision/quality files evolve independently and different programmers follow different project managers.

**Contract:** `Data/ProjectGovernor.json` is the sole authority for requirements, priorities, conflicts, decisions, active gate and region acceptance state.

**Guard:** `Scripts/project_governor.py` fails if deprecated secondary authority files reappear. Supporting docs/plans remain references only.

### PG-026 — Self-hosted checkout must survive transient GitHub network failures
**Observed failure:** Unreal Build Validation #14 on `e98186dc...` never reached UE4.27 compilation. `actions/checkout` retried Git fetches but the target runner repeatedly hit `RPC failed`, connection reset, `early EOF` and `invalid index-pack output`. The failure path then also hit the repository artifact-storage quota.

**Root cause class:** infrastructure/network acquisition failure, not a C++ or Unreal regression.

**Fix pattern:** the Windows self-hosted build downloads the exact `GITHUB_SHA` repository archive directly from the GitHub API with explicit retry/all-error handling, extracts it into the workspace, verifies `ShireJourney.uproject`, and continues with the same UE4.27.2 build/import gate. Failure logs are printed in the workflow and kept locally instead of depending on artifact upload.

**Guard:** static validation rejects reintroducing `actions/checkout` or `actions/upload-artifact` into the self-hosted Unreal workflow, and requires exact-SHA archive download with resilient retries.

### PG-027 — Self-hosted PowerShell execution policy
**Observed failure:** Unreal Build Validation #18 reached the new exact-commit checkout step but Windows PowerShell refused to load the temporary GitHub Actions script because script execution was disabled on the target machine.

**Root cause class:** runner shell policy, not game code.

**Fix pattern:** invoke the checkout shell explicitly with `-NoProfile -ExecutionPolicy Bypass` for the generated Actions script.

**Guard:** static validation requires the explicit bypass shell declaration in the self-hosted Unreal workflow.

### PG-025 — NPC conversation contract drift
**Risk:** ambient conversation expands without story priority, knowledge limits or repetition controls.

**Guard:** validate required conversation sets, known NPC profiles/intents, two-participant cap, and story/danger preemption.

### PG-028 — NPC memory becomes unbounded or story-breaking
**Risk:** persistent NPC memory bloats saves, splits alias identities, leaks route knowledge or changes mandatory story outcomes.

**Guard:** require compact event IDs, no raw transcript persistence, canonical alias sharing, route-partitioned/versioned save intent and a bounded soft save budget.

### PG-029 — Living-world micro-events exceed low-spec/story budget
**Risk:** ambient events become expensive, repetitive or block story traversal.

**Guard:** require P1C01-P1C08 event contracts, story-safe templates, strict near-player caps and state-only offscreen simulation.

### PG-030 — Dialogue intelligence escapes authored/canon bounds
**Risk:** dialogue variation invents knowledge, future events or relationships, or introduces runtime model latency as a hard dependency.

**Guard:** require deny-unlisted knowledge, deny cross-route leakage, deterministic fallback, bounded line/cache sizes and zero required runtime-generation latency.

### PG-031 — Production character motion must preserve production transforms
**Risk:** modular production Frodo/Gandalf meshes load correctly, but the per-frame prototype animation reuses fallback-only face/hat/beard coordinates and visually tears the character apart as soon as Tick begins.

**Contract:** runtime character motion must know whether production meshes are active and must use production-aware face/accessory transforms. Frodo/Gandalf motion may add gait, lean, crouch, airborne, foot, cloak/satchel and weapon motion, but must not modify quest/save/route state.

**Guard:** Pre-Unreal Validation checks that the player character records production-character state, logs the resolved production/fallback visual path, and keeps production-aware face/hat/beard animation branches.

**Acceptance:** static/build success is not visual acceptance. Frodo and Gandalf still require PIE visual review on the target build.

### PG-032 — Part I cast population must not silently thin out or fake visual completion
**Risk:** later edits remove companions from travel chapters, make Frodo appear alone, reuse Hobbit silhouettes in Bree/Elven regions, or call a procedural proxy a finished production character.

**Contract:** `Data/CharacterPopulationPlan.json` defines the required Part I core cast per chapter/route and records each character's visual tier. Film/story separation beats may release companions, but chapter population cannot silently omit the required cast.

**Guard:** Pre-Unreal Validation checks required cast IDs, chapter contracts, runtime source representation, story-aware companion release, Bree/Elf ambient roles, and role-specific ambient visual bases.

**Proof rule:** `PROCEDURAL_DISTINCT_PROXY` means runtime presence only. It is not final visual acceptance. Dedicated meshes/rigging/animation and PIE/device review remain required.

### PG-033 — Build-first mode must keep visual identity distinct and proof labels honest
**Risk:** batch-building many visible features makes it easy to let major characters collapse back into identical proxies or to confuse "compiled" with "looks finished".

**Contract:** the Part I named cast may use low-cost modular proxy accessories during build-out, but core characters must remain visually distinguishable and the population plan must keep the explicit proxy/final-art boundary.

**Build-first rule:** Pre-Unreal + real UE4.27.2 compile/import remain mandatory for merged runtime batches. PIE/device/performance/pacing/visual evidence may be deferred to the later integration pass but may not be marked passed early.

### PG-034 — Batch-built world detail must stay chapter-specific and low-cost
**Risk:** world fill becomes generic repeated clutter, erases chapter identity, blocks traversal, or grows into expensive always-active simulation.

**Contract:** Bree, Weathertop/Ford, Rivendell, Fellowship road/Caradhras, Moria, Lothlorien and Anduin/Amon Hen each receive region-specific low-cost static/procedural environmental detail. Detail must support readability/atmosphere and remain separate from unproven final art claims.

**Guard:** static validation checks the chapter-specific detail markers remain present. Real UE4.27.2 build is mandatory; traversal/performance/visual acceptance remains deferred to the later batch integration pass.

### PG-035 — Lightweight fauna motion must not become expensive ambient AI
**Risk:** adding movement everywhere can turn a visual-life feature into many always-active actors that hurt the target laptop, or generic fauna can appear in chapters where it breaks the mood.

**Contract:** outdoor sky life uses the existing distance-throttled `AShireAmbientNPC` with a special `Bird` role, simple 3D point-to-point motion and procedural wing movement. Moria intentionally receives no natural bird population.

**Guard:** Pre-Unreal Validation requires the Bird role, 3D movement, distance-throttled tick contract and outdoor-region spawn coverage across Shire, Bree, Fellowship outdoor chapters and Isengard.

**Proof rule:** compile success proves integration only; final population density/performance/visual quality remains part of the later batch integration pass.

### PG-036 — Ambient micro-life must stay cheap, role-driven and visually readable
**Risk:** world-life implementation can grow into a heavy per-NPC AI system, or role activity can disappear so residents return to identical walkers.

**Contract:** ambient residents reuse `AShireAmbientNPC` and may carry a single lightweight activity prop selected by role/region. Work/social gestures are procedural and local. Expensive persistent simulation is not required for ambient archetypes.

**Guard:** Pre-Unreal Validation requires the activity-prop contract, all approved prop styles, Shire role assignments, Bree town activity assignments and Elven resident activity assignments.

**Proof rule:** this is runtime micro-life foundation only; final event variety, animation quality and target-device performance remain for the later integration pass.

### PG-037 — Automatic checkpoints must never overwrite manual saves or capture the wrong world
**Risk:** an automatic checkpoint can destroy a user's F5 save, capture a transform from the old chapter during a synchronous world hand-off, or claim runtime coverage while a planned checkpoint has no code binding.

**Contract:** manual save uses `ShireJourney_Auto`; automatic recovery uses the separate `ShireJourney_Checkpoint` slot. Safe/pre-danger story checkpoints are written after quest/story state mutates. Chapter-transition checkpoints are deferred until the next player Tick so the destination world/router transform is authoritative.

**Respawn rule:** combat defeat restores the latest automatic checkpoint at full health when available. It may not silently modify the manual save slot.

**Guard:** Pre-Unreal Validation requires every non-PLANNED `WorldCheckpointPlan` ID to appear in runtime checkpoint code and protects the separate-slot/save/restore/pending-transition invariants.

**Proof rule:** `FOUNDATION` means runtime implementation exists. It does not mean checkpoint placement, respawn, hitching or story continuity has been PIE/device verified.

### PG-038 — Ambient conversations must remain bounded, local and subordinate to story
**Risk:** world chatter can spam the player, repeat constantly, include non-social actors, overwhelm the HUD, or be mistaken for the still-unimplemented named/story-reactive conversation system.

**Contract:** ambient Shire/Bree/Elf residents may run short original two-turn conversations only near the player. Captions render in world space rather than taking over the main HUD. At most two pairs may converse near the player, the same pair has a 90-second cooldown, and Bird/Courier/RoadWalker roles are excluded.

**Scope rule:** ambient conversation remains bounded and local; CP44 adds named Fellowship/story-reactive bounded dialogue and persistent memory without changing this ambient-pair cap.

**Guard:** Pre-Unreal Validation protects the caption runtime, pair cap/cooldown, role exclusions, authored local lines and explicit partial-scope declaration.

### PG-039 — Named-NPC memory must stay compact, bounded and route-partitioned
**Risk:** persistent NPC memory can grow without limit, leak knowledge between Frodo/Gandalf routes, serialize dialogue transcripts, or corrupt save/checkpoint compatibility.

**Contract:** runtime memory stores compact event IDs plus small relationship deltas only. Each named-NPC route bucket is capped at 12 events and 8 relationship entries, relationship values are clamped, and route ID is part of the memory key.

**Persistence rule:** the same bounded `NPCMemoryState` travels through manual save and automatic checkpoint snapshots. Restore sanitizes oversized records before use.

**Scope rule:** CP44 completed alias resolution, tier-specific budgets, expiry, repetition history and memory-aware selection. PIE/device acceptance remains separate.

**Guard:** Pre-Unreal Validation protects the structs, caps, route key, save/restore wiring and explicit partial-scope declaration.

### PG-040 — Visual production must replace blockout without breaking story/runtime
**Risk:** a large art pass can accidentally move story anchors, reintroduce engine primitives as the primary visual language, or add assets that never import on the real UE4.27.2 machine.

**Contract:** production visual layers may replace or overlay blockout geometry, but quest/story trigger coordinates and mandatory story routing remain unchanged unless separately reviewed. New production meshes live under `SourceAssets/Production`, are imported by `ShireProductionImport`, and are referenced through `/Game/Production`.

**Asset rule:** project-owned original assets and clearly licensed reusable assets are allowed. Ripped or unauthorized film/game assets are not part of the production pipeline.

**Proof rule:** source + Pre-Unreal + UE build/import success proves assets are loadable, not that final visual quality, PIE composition or device performance is accepted.

### PG-041 — Bree production art must preserve Chapter 2 story coordinates
**Risk:** replacing the Bree greybox can visually improve the town while accidentally burying, moving or disconnecting the gate, inn, Strider, night-attack and departure story flow.

**Contract:** the production Bree layer overlays the current runtime layout. The existing chapter trigger coordinates remain authoritative until a separately reviewed world-layout migration updates both story data and validation together.

**Visual rule:** imported production meshes keep their materials. Engine primitives may remain only as fallback/support geometry, and prototype world labels are hidden by default.

**Guard:** Pre-Unreal Validation checks the Bree production source assets, runtime production-mesh references and key story-anchor coordinates.

### PG-042 — Regional production overlays must not rewrite story topology
**Risk:** rapidly replacing greybox landmarks across six chapters can break authored trigger corridors, chapter transitions or imported-material behavior.

**Contract:** P1C03-P1C08 production landmarks are a visual overlay invoked by chapter ID after the existing chapter build. Existing story actors, quest triggers and transition code remain authoritative.

**Material rule:** imported production meshes retain their source materials. Engine BasicShapes may still provide collision/support/fallback geometry but are not the intended dominant visual layer.

**Guard:** Pre-Unreal Validation requires every regional production source asset, the chapter-aware loader/overlay, hidden prototype labels and all six chapter branches.

### PG-043 — Dedicated heroes must not silently fall back to one shared visual identity
**Risk:** named companions can remain technically present while looking interchangeable, undermining the production pass even when world art improves.

**Contract:** Sam, Merry, Pippin and Aragorn/Strider each have dedicated project-owned torso/head/hair source meshes and runtime resolution before generic archetype fallback.

**Reuse rule:** common limbs and gear may remain shared to control scope, but dedicated identity meshes and character-specific styling must remain distinct.

**Proof rule:** dedicated modular meshes are production progress, not final skeletal rigs, facial animation, cloth/hair shading or animation acceptance.

### PG-044 — Backend completion must stay bounded, canonical and save-safe
**Risk:** finishing the backend in one pass can create alias-split memory, unbounded save growth, NPC knowledge leaks, repetitive dialogue, story-overriding banter, or incompatible saves.

**Contract:** NPC identity is canonicalized before persistent access. Persistence budgets derive from profile tier. Low-priority memory expires. Story memory only records already-completed beats for eligible profiles. Bounded dialogue is deterministic, knowledge-gated and always subordinate to authored story interactions.

**Conversation rule:** Fellowship banter may run only outside danger/story dialogue conflicts and uses the same logical voice-cue transport as authored dialogue. Ambient schedules remain cheap and react to danger/weather without creating per-instance persistent state.

**Save rule:** new snapshots are schema-versioned. Future unsupported schemas and invalid numeric state are rejected instead of partially restoring corrupt state. Legacy snapshots remain loadable through defaulted fields and restore sanitation.

**Proof rule:** IMPLEMENTED is not VALIDATED. Static checks and UE4.27.2 compilation prove integration; PIE/device round trips remain mandatory acceptance evidence.

### PG-045 — Named cast must keep dedicated identity before generic fallback
**Risk:** a large cast can silently collapse back to shared Hobbit/Human/Elf/Dwarf bodies even when source assets exist, making major characters visually interchangeable again.

**Contract:** every named Part I cast entry resolves to a dedicated project-owned torso/head/hair folder before generic archetype fallback. Shared limbs and gear are allowed where useful, but the primary silhouette identity must remain character-specific.

**Dialogue companion rule:** named local/story characters added in this pass must retain bounded authored dialogue coverage under the same CP44 knowledge, memory, canon and repetition guards.

**Proof rule:** dedicated modular identity does not equal final rigged character art. Skeletal rigs, facial rigs, cloth/hair shading and bespoke animation remain separate production milestones.

### PG-046 — Threat production art must not weaken encounter logic
**Risk:** replacing primitive enemy silhouettes can accidentally bypass quest gating, detection, combat damage, defeat state or low-spec tick throttling.

**Contract:** Black Rider, Orc, Uruk-hai and Cave Troll may replace their visible meshes with project-owned production assets, but encounter activation, patrol/detection, attack/health and quest progression logic remain authoritative.

**Fallback rule:** engine primitives may remain only as fallback if a production asset fails to resolve; production paths are the intended primary visual route.

**Proof rule:** dedicated enemy meshes are visual-production progress, not final rigged combat animation, VFX/audio or target-device combat acceptance.

### PG-047 — External production assets must be licensed, attributable and reproducible
**Risk:** high-quality marketplace/community assets can accelerate production but can also introduce editorial-only, non-commercial, no-derivatives, unknown-license, subscription-expired or franchise-ripped content that cannot safely ship or cannot be reproduced on the build machine.

**Contract:** every third-party production asset must be represented in `Data/ExternalAssetManifest.json` before entering `SourceAssets/ExternalLicensed/Approved`. Provider, asset ID, source URL, acquisition date, license class, approval status and required attribution/proof are mandatory.

**Blocked rule:** Editorial, NC, ND, unknown-license and ripped film/game/franchise assets are rejected. Reference-only sources such as ArtStation, Tolkien Gateway and LOTR Wiki may guide original work but are not production asset sources without separate item rights.

**UE4.27 rule:** Fab in Launcher may be used for UE4 project operations. Do not make the pipeline depend on the in-editor Fab integration because Epic documents that integration for UE5.3+.

**Guard:** Pre-Unreal Validation checks provider policy, blocked license classes and one-to-one manifest coverage for every file placed in the Approved external asset tree.

### PG-048 — Service providers, resource libraries and rights holders are different roles
**Risk:** the project may mistake a famous production company or reference site for an IP licensor, or assume that a personal/private project automatically authorizes use of protected Tolkien/film material.

**Contract:** Weta Workshop is recorded as a design/game-development/private-commission partner. Middle-earth Enterprises is the primary recorded LOTR/Hobbit game/franchise licensing contact. Warner Bros/New Line, Tolkien Estate and HarperCollins are separate rights channels for film-specific, Estate-controlled and published-text material.

**Private-project rule:** personal, non-commercial and non-distributed status may be stated in a permission request, but it is not treated by the project as automatic permission to copy protected assets, actor likenesses, film props/costumes, maps, artwork, soundtrack, screenplay or book text.

**Resource rule:** CC0/generic libraries such as Poly Haven and ambientCG can accelerate production under their licenses; animation/character libraries such as Mixamo or ActorCore retain their own distribution terms.

**Guard:** Pre-Unreal Validation protects the rights-holder map, Weta service classification and expanded provider list.

### PG-049 — Living-world intelligence and engineering path must remain bounded and recoverable
**Risk:** large uninterrupted production can create unbounded ambient simulation, story-interfering random events, duplicate AI systems or a project plan that exists only in chat memory.

**Contract:** `ALivingWorldDirector` consumes the existing LivingWorldEventPlan, honors per-chapter eligibility, active-event/cull/cooldown budgets, suppresses peaceful events during danger and never persists ambient event transforms. The Frodo main route receives chapter micro-events; the authored Gandalf parallel route is not polluted by them.

**World rule:** common production terrain may strengthen hills/cliffs/river silhouettes but must overlay rather than relocate established quest/story anchors.

**Engineering rule:** `Data/ProductionExecutionGraph.json` records workstream dependencies and proof status. It organizes work but never overrides `Data/ProjectGovernor.json`.

**Proof rule:** implementation-complete does not mean PIE/device/visual acceptance.

### PG-050 — Mass world dressing must remain deterministic and story-safe
**Risk:** a large visual-density pass can accidentally move quest topology, add unbounded runtime actor counts, or create regionally generic scenery that erases chapter identity.

**Contract:** common production dressing is source-controlled, chapter-aware and deterministic. Story/quest trigger coordinates remain authoritative. Distant dressing is non-colliding by default and must respect the target laptop budget.

**Regional rule:** each P1C03-P1C08 chapter uses a deliberately different combination of common trees/foliage/river/ruin props on top of its dedicated landmark kit.

**Engineering memory:** `Data/WorldDressingPlan.json` is the machine-readable owner/density/asset map for this layer and must remain synchronized with runtime placement.

**Guard:** Pre-Unreal Validation checks the common source assets, runtime mesh references, chapter branches and all eight world-dressing profiles.

### PG-051 — Character motion / atmosphere handoff must stay honest
**Risk:** rig-ready code or chapter atmosphere profiles can be mistaken for final character animation, weather, day/night or visual acceptance.

**Contract:** skeletal production presentation activates only when both the named skeletal mesh and locomotion AnimBP resolve. Otherwise modular fallbacks remain visible. Chapter atmosphere remains a bounded sun/skylight/fog profile and does not imply a dynamic day/night cycle or final weather VFX.

**Proof rule:** compile/import/headless startup are regression evidence only. Real PIE/device observation is required before any chapter is marked visually or behaviorally accepted.

### PG-052 — Mass resource integration must preserve playable startup
**Risk:** large asset/data batches can compile while breaking runtime packaging, initial quest state, router bootstrap or the living-world director.

**Contract:** the production integration plans remain packaged runtime dependencies; startup remains FrodoMain / P1C01 / ShireArrival and spawns the chapter router plus LivingWorldDirector.

**Guard:** Pre-Unreal validation and the UE4.27 headless startup smoke require the GameMode and P1C01/FrodoMain markers.

### PG-053 — Continuous population must remain bounded and chapter-specific
**Risk:** population saturation can create runaway actor counts, inappropriate civilians, or expensive behavior on the target laptop.

**Contract:** chapter-specific baseline targets, cull/replenish budgets and role mixes remain bounded. Moria keeps a zero-civilian baseline. Ambient schedules/social/awareness reuse the throttled ambient actor.

**Proof rule:** source/CI evidence does not establish crowd-flow or target-device FPS acceptance; those remain manual PIE/device checks.

### PG-054 — Mega resource bank must remain present and runtime-wired
**Risk:** later cleanup can silently drop regional assets or runtime references while static counts still look healthy.

**Contract:** the CP54 regional/common bank, texture floor and runtime references for all Part I regions remain guarded by WorldResourceBankCP54.json and Pre-Unreal checks.

**Proof rule:** successful import proves that UE4 can ingest the source bank; it does not prove correct scale, shading, materials, placement or visual quality.

### PG-055 — Import warnings are evidence, not visual acceptance
**Symptom exposed by:** current-head UE4.27.2 audit on 2026-09-19. Exact-head build/import/startup succeeded and imported **307 files with 0 import failures**, while the Unreal log still emitted substantial visual-quality warnings.

**Observed warning classes:**
- generated OBJ meshes frequently report missing smoothing-group data,
- many meshes report degenerate tangent bases / nearly-zero binormals,
- several modular character assets reference unresolved defaultMat material assets,
- Shire-loaded named characters probe skeletal rig / locomotion assets that are not present yet and correctly fall back to modular presentation.

**Contract:** zero import failures must never be translated into zero asset-quality problems. These warnings are non-blocking for the verification freeze unless they cause runtime failure, but they must be inspected in real PIE before visual acceptance and should be cleaned during the later material/asset-quality pass.

**Manual check:** during each chapter PIE pass, inspect obvious shading corruption, missing/default materials, scale/orientation, and fallback character presentation. Record concrete findings in PRODUCTION_COMPLETENESS_MATRIX.md / CURRENT_PROJECT_STATE.md.

### PG-056 — Verification freeze must be technically enforced
**Risk:** a written freeze can be bypassed accidentally by opening CP55, adding more production assets, or adding new runtime files before current-head PIE/device proof exists.

**Contract:** while Project Governor mode is `PIE_VERIFICATION_FREEZE`, CI enforces the CP54 ceiling, the production-source file ceiling, and the exact current runtime-source file set recorded in `Data/VerificationGate.json`. Existing files may still be repaired, instrumented and optimized.

**Guard:** Pre-Unreal Validation fails on CP55+ checkpoint definitions, net-new production source files, or net-new/remapped ShireJourney runtime source files during the freeze.

### PG-057 — PIE claims require exact-commit human evidence
**Risk:** changing a matrix cell to FUNCTIONAL/PASSED can create the appearance of a playtest that never happened.

**Contract:** `Data/PIEVerificationEvidence.json` is the structured evidence companion to the current-head matrix. Any chapter moved away from NOT_RUN requires a 40-character tested commit SHA, tester, timestamp, at least one artifact/log reference, and at least two concrete observations.

**Guard:** CI cross-checks the structured evidence against the current-head table in `PRODUCTION_COMPLETENESS_MATRIX.md`. Human release sign-off cannot become APPROVED until all eight chapters are PIE_TESTED.

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

## PG-055 — CP55 activity/movement contract
Guards the post-verification fauna/activity expansion:
- `Data/WorldActivityMovementPlan.json` must exist and parse.
- project-owned bird/rabbit/butterfly OBJ source assets must remain present.
- `AShireAmbientNPC` must retain Bird/Rabbit/Butterfly runtime roles and production-mesh preference.
- `ALivingWorldDirector` must retain chapter-bounded spawning for those roles.
- `LivingWorldEventPlan.json` must retain bird, small-animal and butterfly fauna templates.

Purpose: prevent later cleanup from silently deleting CP55 world-life movement or replacing it with untracked/persistent AI scope.

## PG-058 — Film-spine experiential expansion must remain canon-safe and optional
**Risk:** adding more play, humor, friendship and exploration can accidentally reorder film events, alter required outcomes, bloat the low-spec simulation or turn adapted scene intent into copied screenplay material.

**Contract:** `Data/FellowshipExperienceMegaPassCP56.json` must retain eight Part I chapter entries, Peter Jackson film continuity as the primary spine, original game writing, and optional/non-blocking enrichment between mandatory anchors.

**Runtime guard:** Shire friendship/revelry beats, PlayRunner activity, Bree common-room life and the P1C03/P1C05/P1C06/P1C07/P1C08 companionship/discovery beats must remain wired to existing lightweight NPC/quest-trigger systems.

**Packaging guard:** CP55 activity and CP56 experience plans remain runtime dependencies.

**Proof boundary:** static/compile/headless evidence proves regression safety only. Final cinematic quality, character acting, voice, pacing and target-device visual acceptance remain separate production proof.

## PG-059 — Living NPC intelligence must remain bounded and offline-safe
Guards the programmer-requested Living NPC layer:
- `Data/LivingNPCIntelligencePlan.json` must exist, parse and remain packaged.
- character knowledge remains `DENY_UNLISTED` by default.
- ambient runtime must retain bounded hunger, fatigue, social need, fear, emotion and goal state.
- needs/emotions may bias routine/social behavior but may not own quest progression or mandatory film outcomes.
- the game must remain playable without an always-on LLM/STT/TTS service.

A future generative dialogue provider is allowed only as an optional bounded wording layer with deterministic local fallback.

## Runtime observation regression — 2026-09-19

Ready markers previously ended startup checking immediately; chapter checks slept four seconds after markers without reading the resulting log again. A late fatal/assert/ensure or spontaneous exit could therefore escape those checks. `Scripts/runtime_smoke.py` now observes a live process throughout that window and scans the final log after cleanup. `Scripts/test_runtime_smoke.py` reproduces these failures with subprocess fixtures in Pre-Unreal CI. This is boot stability evidence only, not traversal, save/load, performance or visual approval. Missing markers and intermittent starts fail explicitly rather than being hidden by retries.

## CP56 continuation — checkout and mood selection

Unreal run 35461908616 fetched successfully on retry but checkout failed with exit 73: recreating .git left existing CI source files untracked. The dedicated runner checkout now forces only fetched tracked paths, retaining unrelated generated content and save files. No git clean is added. The retry delay uses PowerShell sleep because cmd timeout reported unsupported input redirection. This does not explain or claim to fix separate action-download cancellation during job setup.

Regional mood previously altered only a random seed, permitting emotionally mismatched authored replies. Explicit mood eligibility and context priority now precede freshness/random selection. Existing story/memory/knowledge gates remain in place; five UE automation assertions guard ranking semantics. Engine validation is pending.

## Interrupted build investigation — 2026-09-19

Run 35463567281 proves the source checkout repair worked. Build then received Ctrl-C and exit -1073741510; no C++ compiler error was observed. The cancellation source is not proven. Review found detached lifecycle cleanup can kill listeners after its 20-minute deadline even with workers still running. Removed scheduling of this unsafe cleanup. Repository-wide Unreal concurrency now serializes PR/develop jobs on the shared device and does not cancel active builds on new pushes. These are preventive repairs, not proof of the cancellation's cause. A fresh engine run must establish success.

### PG-150 — Governor owns durable truth; GitHub owns volatile transport state
**Symptom exposed by:** repeated Pre-Unreal failures caused only by copied PR numbers, branch names, or stale human-readable execution-board labels while runtime/source state was otherwise unchanged.

**Risk:** rapidly changing transport metadata becomes a false build gate. Opening or closing a PR can make Pre-Unreal red even though requirements, code, assets, save integrity and runtime behavior did not regress.

**Contract:** `Data/ProjectGovernor.json` owns durable requirements, active lane/gate, accepted decisions and evidence boundaries. GitHub owns live PR number, candidate branch and open/closed transport state. Human-readable boards may summarize that state but must not be required to mirror it exactly for Pre-Unreal to pass.

**Guard:** `Scripts/project_governor.py` still enforces authority, lane, gate, branch-policy and evidence semantics, but no longer compares volatile PR/branch copies across Governor and `MASTER_EXECUTION_BOARD.md`. Supporting docs must continue to defer authority to ProjectGovernor.

**Proof boundary:** this removes a false administrative blocker only. It does not weaken exact-head source/engine validation or promote PIE/device/visual/performance acceptance.

### PG-151 — Development-mode validation must have one data owner
**Symptom exposed by:** Pre-Unreal #782 on `32af3140d1d297283de640144a58c3b32133d3d1`.

**Risk:** a validator-owned mode allowlist becomes a second project manager. A legitimate Governor phase change can turn red until Python is edited, and proof honesty can accidentally depend on exact sentence wording.

**Contract:** `Data/ProjectGovernor.json/development_mode_contract` owns registered mode IDs, supersedes relations and mandatory manual-only acceptance labels. `development_mode.proof_boundary` is structured data. Validators consume the shared semantic helper and do not infer acceptance boundaries from prose.

**Guard:** `Scripts/governance_contracts.py` is consumed by both Pre-Unreal and ProjectGovernor validation; `test_governance_contracts.py` covers unknown mode, supersedes drift, missing labels and prose-only fake proof.

**Proof boundary:** this guard repairs governance validation semantics only. Fresh exact-head Pre-Unreal/UE4 evidence is required before the child checkpoint is promoted.

### PG-152 — Validator refactors must not leave orphan phase aliases
**Symptom exposed by:** Pre-Unreal #783 on `e0b66dbccdf9e91f3cd6af0190008cf58ca31198`.

**Failure:** CP149 removed the old `governor_mode_id` validation block, but the later PG-056 freeze guard still referenced that local name and crashed with `NameError`.

**Contract:** development-mode validity stays owned by `development_mode_contract`. A guard that only needs the current mode identity reads `development_mode.id` directly from Governor structured data and must not introduce a second allowlist or validator-owned alias.

**Evidence boundary:** Unreal #618 and Warehouse #199 succeeded on the failing static head; fresh Pre-Unreal is still required before CP150 can be STATIC-VALIDATED.

### PG-153 — Handoff source_head is verified-baseline lineage, not candidate-head storage
**Symptom exposed by:** Pre-Unreal #784 on `2259242a772d3dd21a90cc10a8a4a2761be3b3dd`.

**Evidence:** PRE-UNREAL CORE VALIDATION passed; ProjectGovernor then emitted one error: `Legacy verified handoff must refer to the same last-green baseline`. Unreal #619 and Warehouse #200 succeeded on that exact head.

**Contract:** `session_handoff.source_head == validation_snapshot.last_green.sha`. Newer partial candidate evidence belongs in `validation_snapshot.latest_observed`. Never rewrite historical baseline lineage merely to point at the newest repair parent.

**Guard:** existing `test_governor_handoff.py::test_historical_handoff_cannot_disagree_with_baseline` remains authoritative. The correction is data-only; the validator is not weakened.

**Proof boundary:** fresh full Pre-Unreal and exact-head Unreal validation are still required for CP151.

### PG-154 — Runtime module may not regress to flat-root source layout
**Baseline:** CP-W00-151 `92f6d3aaad79f33eaf2385de292e6886d2c1b5da` passed Pre #785, Unreal #620 and Warehouse #201 before the isolated migration.

**Contract:** runtime headers live under `Source/ShireJourney/Public/<Domain>/`; implementation files live under `Private/<Domain>/`; `ShireJourney.Build.cs` remains at module root. All mapped .h/.cpp entries are `MIGRATED`.

**Visibility rule:** never reintroduce `PublicIncludePaths.Add(ModuleDirectory)`. Only explicit `Public/<Domain>` include roots may be exported, keeping private implementation and module-root files out of dependent-module visibility.

**Guard:** Pre-Unreal recursively resolves runtime files, rejects root-level .h/.cpp files, rejects `CURRENT_FLAT` entries after migration and checks all public domain include roots. DeepProjectAudit also scans recursively.

**Proof boundary:** CP152 is organizational only. Fresh exact-head Pre-Unreal and UE4.27.2 compile/runtime validation are required; no PIE/device/visual claim follows from moving files.

### PG-155 — Public/Private migration consumers and persistent runners must follow the architecture map
**Symptom exposed by:** Pre #786 and Unreal #621 on `9acc72b16e058a422428389fcefeb9af12fa0e98`.

**Static failure:** validators still opened historical flat paths after the physical files moved, creating missing-read cascades that looked like dozens of lost gameplay invariants.

**Engine failure:** the self-hosted runner intentionally does not `git clean`; after the migration, old tracked root headers became untracked leftovers. UHT therefore saw both the stale flat header and the new Public header and rejected duplicate leaf names.

**Contract:** validator file access resolves the active migrated source tree; centralized runtime evidence anchors name the physical migrated files. Before Unreal verification/build, the persistent runner reads `SourceArchitecturePlan.json` and removes only an obsolete `current_path` whose entry is `MIGRATED` and whose `target_path` exists. No broad `git clean` is allowed.

**Proof boundary:** fulfilled on CP-W00-154 exact head `ab7889d6b2dafc059220a0c0a3dc63decfe6b72e` by Pre #788 SUCCESS, Unreal #623 SUCCESS and Warehouse #204 SUCCESS. The migration is machine-accepted; this does not imply PIE/device/visual/performance acceptance.

### PG-156 — No hidden direct flat runtime Path constructors after migration
**Symptom exposed by:** Pre #787 on `b7ad48fc927c522dcb5f4a386cde561360739278`.

**Evidence:** migration-aware reads and the persistent-runner cleanup worked; Unreal #622 passed the full engine/headless suite. Pre #787 then reported only PG-116 because `StoryPresentationDirector.h/.cpp` were still constructed at the historical module root before `.exists()` and read checks.

**Contract:** after `PUBLIC_PRIVATE_BY_DOMAIN`, Pre-Unreal may not construct any runtime .h/.cpp/.cs path as `ROOT / "Source" / "ShireJourney" / "<leaf>"`. Runtime source access must use the migration-aware resolver or an authoritative physical target path.

**Guard:** PG-155 now scans for any direct historical flat runtime Path construction, not only `read(...)` calls.

**Proof boundary:** fulfilled on CP-W00-154 exact head `ab7889d6b2dafc059220a0c0a3dc63decfe6b72e`: Pre #788, Unreal #623 and Warehouse #204 all succeeded. Keep PG-155/PG-156 as regression guards; do not reopen cleanup without a concrete failure.

### PG-157 — Canonical develop helper / branch drift guard
**Observed failure:** the local Update/Build/Launch helper silently executed `checkout develop` while the owner was testing another branch. That changed the runtime under test without an explicit decision.

**Guard:** local Update/Build/Launch and PIE helpers require the developer clone to already be on `develop`, refuse the self-hosted runner `_work` tree, refuse tracked dirty state before pulling, and never issue a branch-switch command.

### PG-158 — Persistent self-hosted source-tree integrity
**Observed failure:** Unreal #653 reached UBT on exact head `8397922a...` then raised `DirectoryNotFoundException` for `Source/ShireJourney/Private/Characters/ShireAmbientNPC.cpp`, even though that file exists on the exact Git commit.

**Guard:** immediately before UBT, the workflow enumerates Git-tracked Source .h/.cpp/.cs files, restores any missing tracked path from exact HEAD, then validates every current target in `Data/SourceArchitecturePlan.json`. The build may not start if any tracked or architecture target source is absent.


### PG-159 — UE4.27 StaticMaterials deprecation warning
**Observed warning:** an earlier local build showed C4996 for direct `UStaticMesh::StaticMaterials` access in the production importer.

**Current state:** canonical `develop` already uses `GetStaticMaterials()` and contains no direct `.StaticMaterials` / `->StaticMaterials` access in `ShireProductionImportCommandlet.cpp`.

**Guard:** Pre-Unreal rejects any direct deprecated member access and requires the accessor-based API.

### PG-160 — SetStaticMesh mobility ordering
**Observed warning:** PIE showed repeated `Calling SetStaticMesh ... but Mobility is Static` warnings on generated `StaticMeshActor` components.

**Current state:** the Shire, Bree, Fellowship and Isengard procedural `SpawnShape` paths set `Movable` before `SetStaticMesh`.

**Guard:** Pre-Unreal structurally checks that ordering in all four builders so the warning family cannot silently return.

### PG-161 — Do not repeat expensive Unreal/package proof across safe metadata ancestry
**Observed waste:** after branch consolidation, the direct parent Unreal run had been cancelled even though a recent ancestor had full green engine/package proof. A governance/docs-only develop update therefore fell through the classifier fail-safe and Unreal #704 repeated build/import/runtime/cook/package work that the content delta itself did not require.

**Root cause:** validation inheritance looked only at the immediate parent workflow result. A cancelled metadata parent erased visibility of still-valid nearby green proof.

**Permanent rule:** governance/docs-only changes may inherit the nearest first-parent green Unreal proof only when every changed path from that green ancestor to the candidate head is still inside the explicit safe-governance set. Any runtime, SourceAssets, Config, Build.cs/Target.cs, streaming, packaging/release or unclassified path breaks inheritance and fails back to the required core/full lane. Changes to the classifier/Pre-Unreal policy itself may inherit a green parent without rerunning the engine, but only through the explicit validation-policy-only path.

**Guard:** Pre-Unreal requires `Test-NearestSafeGovernanceAncestorGreen`, `Test-SafeGovernanceDelta`, the transitive-proof marker and the validation-policy-only marker. This turns evidence reuse into an explicit fail-closed contract instead of a shortcut.

### PG-162 — Local update/PIE launchers must be immutable while Git pulls
**Observed failure:** the Documents-clone launcher ran `git pull` while CMD was still parsing the same batch file. Git rewrote the running file and execution continued at the wrong offsets, producing `'defined' is not recognized`, an empty branch value and `CANONICAL_BRANCH_REQUIRED`.

**Root cause:** a self-updating batch controller was executing directly from the tracked repository path.

**Permanent rule:** `SHIRE_UPDATE_BUILD_LAUNCH.bat` and `SHIRE_PIE_VERIFY.bat` first copy themselves to a unique temporary file, run from that immutable copy, pass the real repository root explicitly, and delete the temporary copy afterward. Interactive Unreal remains forbidden from the Actions runner workspace.

**Guard:** Pre-Unreal requires the immutable-bootstrap markers in both launchers.

### PG-163 — Historical branch sprawl must never become programmer handoff state
**Observed risk:** many repair/production/verification/warehouse branches accumulated overlapping snapshots, making it unclear which branch contained the complete project and creating a temptation to bulk-merge stale code.

**Resolution:** unique still-valid data/ops content was selectively salvaged, stale pre-Public/Private runtime branches were classified as superseded, old PRs were closed, and Branch Cleanup reduced the remote repository to `develop` + `main`.

**Permanent rule:** `develop` is the sole canonical development/programmer-handoff lane; `main` is stable/release only. Future implementation uses short-lived single-purpose PRs targeting develop. After merge, the temporary branch must self-clean once meaningful content is integrated. Never bulk-merge an old diverged branch merely because it is ahead by commit count.

**Guard:** `Data/BranchCleanupPlan.json`, the branch-cleanup workflow, the Governor branch workflow contract, and Gate 0 together preserve this rule.

### PG-164 — Regression guards must validate semantics, not reject the intended explicit path
**Observed failure:** Pre-Unreal #871 rejected the new PG-161 classifier policy because its guard searched too broadly for the classifier filename and mistook the intended explicit validation-policy-only branch for ordinary governance/docs classification.

**Root cause:** the new guard used a textual range that included both the forbidden ordinary-safe block and the allowed explicit policy-only hook.

**Permanent rule:** source guards must inspect the smallest structural region that represents the forbidden behavior. A guard may not ban the exact explicit path it is supposed to require.

**Follow-up evidence:** Pre-Unreal #875 showed the first correction still anchored at the first `Docs/` test in the helper function, so its text slice crossed later declarations and again produced the same false positive.

**Fix:** PG-161 now anchors its search inside the main `foreach($p in $changed)` classification loop, isolates only the ordinary safe-governance branch there, and separately requires the explicit validation-policy-only marker.

**Evidence boundary:** second correction committed; exact-head Pre-Unreal rerun required before calling PG-164 proven.



### PG-165 — Hero candidate QC must stage its declared provider prerequisites
**Symptom exposed by:** Warehouse #307 on `develop@2363d3f97d9158cd64a9e5f2f19b864092f69555`.

**Evidence:** runner health passed; persistent inventory audit passed; critical-gap preparation reported `verified=239 pending=0 manualQueue=0`. The final candidate wave then reported `prepared=0 pending=4 blocked=0`, `FRODO candidates=0`, `GANDALF candidates=0`; every pending row named an authorized Quaternius pack with reason `warehouse_source_not_staged_yet`.

**Root cause:** the exact-head hero candidate report ran on every Warehouse push, but its four declared Quaternius source-pack prerequisites were only staged when unrelated provider paths happened to trigger the general Quaternius stage. Candidate execution and prerequisite execution were therefore not coupled.

**Permanent rule:** any push that executes the P1C01 hero candidate report must first execute a bounded provider prerequisite batch containing exactly the wave's declared `authorized_source_packs`. Do not substitute a full-provider refresh.

**Guard:** `Scripts/test_p1c01_hero_candidate_provider_contract.ps1` checks exact authorized-pack parity, FBX/CC0 boundaries, Warehouse path triggering and stage-before-report order.

**Evidence boundary:** repair is SOURCE-IMPLEMENTED until fresh exact-head Pre-Unreal/Unreal validation succeeds and the next develop Warehouse run produces nonzero candidate coverage or a new concrete provider-access blocker.


### PG-166 — Provider page reachability is not staged-payload evidence
**Symptom exposed by:** Warehouse #308 on `develop@bb4faa05984c4015e90eb1d3bfeea032679492b1`.

**Evidence:** the targeted Quaternius prerequisite step reached all four official pack pages and ended with `QUATERNIUS_WAREHOUSE_STAGE_PASS files=0 unresolved=4`. The downstream exact-head hero candidate report then produced `prepared=0 pending=4 blocked=0`, `FRODO candidates=0`, `GANDALF candidates=0` and `P1C01_HERO_RIG_CANDIDATE_COVERAGE_FAIL total=0 required=2`.

**Root cause class:** metadata/page resolution was allowed to report a staging PASS without any staged payload file.

**Permanent rule:** a source-acquisition/staging step that produces zero payload files must not satisfy a downstream asset-availability prerequisite. Page/license metadata may be recorded, but payload state remains unresolved/manual until a provider-supported direct download or explicit manual acquisition yields a verified file receipt.

**Provider correction:** Quaternius is now treated as `MANUAL_CLEAR_LICENSE` / manual item download unless a provider-supported direct payload URL is known. Do not fabricate or scrape undocumented archive URLs.

**Evidence boundary:** governance/source-access correction only; it does not produce Frodo/Gandalf candidates or authorize runtime integration.


### PG-167 — P1C01 hero FBX candidates require file-level provenance
**Risk:** candidate ranking could previously consume an extracted FBX by filename/keywords without carrying the provider asset, receipt, source payload and SHA256 into the ranked candidate record.

**Permanent rule:** every FBX admitted to the P1C01 hero candidate pool must have exactly one intake provenance row binding its extracted candidate path to provider, asset ID, receipt, source payload and verified SHA256. Missing or ambiguous provenance fails closed before character ranking.

**Guard:** `Scripts/test_p1c01_hero_candidate_provenance_contract.ps1` requires intake provenance emission and exact-file fail-closed enforcement in the candidate wave.

**Evidence boundary:** SOURCE-IMPLEMENTED until exact-head Pre-Unreal/Unreal validation and Warehouse candidate evidence succeed. This is not skeletal/deformation/visual/runtime acceptance.
