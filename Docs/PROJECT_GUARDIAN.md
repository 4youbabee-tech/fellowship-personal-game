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
