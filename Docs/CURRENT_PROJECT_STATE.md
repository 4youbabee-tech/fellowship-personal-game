# CURRENT PROJECT STATE / HANDOFF

> **START HERE after a lost chat, a new developer handoff, or a long break.**
>
> This file is the operational snapshot of where the project is now.
> **Project-management authority lives only in `Data/ProjectGovernor.json`.**
> Story canon lives in `Docs/STORY_CANON_BIBLE.md`.
> Development rules live in `Docs/DEVELOPMENT_GATES.md`.
> Automated regression rules live in `Data/ProjectGuardRules.json`.
> World/chapter/checkpoint engineering lives in `Docs/WORLD_PRODUCTION_BLUEPRINT.md`.
> Machine-readable player checkpoint intent lives in `Data/WorldCheckpointPlan.csv`.

## Repository

- Repository: `4youbabee-tech/fellowship-personal-game`
- Active branch: `develop`
- Do not develop directly on `main`.
- Engine: Unreal Engine 4.27.2
- Target: Windows / DX11 / 720p / 30 FPS / Low-Medium
- Hardware floor: Intel i7 6th gen, 8 GB RAM, AMD GPU around 2 GB VRAM
- Local update/build/launch entry point: `SHIRE_UPDATE_BUILD_LAUNCH.bat`

Latest validated baseline before the current source-handoff governance maintenance:
- `e739ba6e364d0316cf5b7fe10c1f8ecaa13d417e` — `docs: sync CP30 handoff to validated head`
- Pre-Unreal Validation #113: **SUCCESS**.
- Unreal Build Validation #11: **SUCCESS** on the exact commit with UE4.27.2 C++ build and production asset import (`50 files, 0 failures`).
- CP30 world/checkpoint engineering is therefore STATIC-VALIDATED, COMPILE-TESTED and ASSET-IMPORT-TESTED. Dedicated automatic checkpoint/respawn runtime behavior remains planned, not implemented.
- The Shire visual content introduced at `8b0c13f...` still requires focused PIE/device review before VISUALLY-ACCEPTED.
- Intermediate CP30 commit `10ac91e...` had Pre-Unreal Validation #111 fail with `NameError: story_plan_ids is not defined`; `bd3d0be...` fixed that validator-order bug and restored both green gates.

Runtime-code baseline documented by this handoff:
`177f6cdbd073eaf0e2fd2c39da4a80fc82acf4ae`
(`world: add lightweight ambient NPC awareness`).

Documentation/guardian commits may naturally be newer than that runtime-code baseline.

## Validation vocabulary

Never say a feature is simply "ready". Record what was actually proven:

- **STATIC-VALIDATED**: GitHub Pre-Unreal Validation is green.
- **COMPILE-TESTED**: UE4.27.2 C++ build + UnrealHeaderTool succeeded.
- **ASSET-IMPORT-TESTED**: the UE4.27 production import commandlet completed successfully for the planned source assets.
- **PIE-TESTED**: relevant gameplay was exercised in Play In Editor.
- **DEVICE-TESTED**: relevant gameplay was exercised on the target laptop.
- **VISUALLY-ACCEPTED**: the user reviewed and accepted the visual/gameplay direction.

A green GitHub action is not a substitute for engine testing.

## Current proof level

Historically, an earlier project baseline:
- compiled and opened successfully in UE4.27.2,
- ran PIE,
- showed working movement, quest flow and HUD.

The current runtime-code baseline is now:
- **STATIC-VALIDATED** through Pre-Unreal Validation #80.
- **COMPILE-TESTED** on the target machine with UE4.27.2 after the PG-010/PG-011 fixes.
- **PIE-TESTED (BASIC BOOT ONLY)**: the Shire entered PIE successfully and rendered the current HUD.
- **DEVICE-TESTED (BASIC BOOT ONLY)** on the target laptop; full gameplay/performance acceptance is still pending.

Real UE4.27.2 validation history on 2026-09-18:
- Git update succeeded.
- UnrealHeaderTool completed successfully and generated reflection code.
- The first C++ build exposed:
  - C2660: one stale one-argument `MovePlayerToChapterStart` call.
  - C2440: direct base-to-derived light component pointer assignment from `GetLightComponent()`.
- Both source issues were fixed and converted into Project Guardian regression checks PG-010 and PG-011.
- A fresh build after those fixes completed successfully.
- Unreal Editor launched.
- PIE entered the Shire successfully.
- The HUD visibly showed:
  - `Frodo | P1C01_Main`
  - `An Unexpected Arrival`
  - `Reach the Shire lane and meet Gandalf.`

Additional PIE evidence on 2026-09-18:
- F5 Quick Save succeeded in PIE and displayed `Journey saved.`.
- UE4.27 emitted one runtime warning that the existing Directional Light had to be Movable before rotation.
- That warning was traced to `ConfigureMorningAtmosphere`, fixed by setting mobility before actor rotation, and recorded as Guardian regression PG-012.
- Quick Load (F9) is still pending verification.

CP22 milestone evidence on 2026-09-18:
- the enlarged Shire world-scale commit was pulled to the target laptop,
- UE4.27.2 Build completed successfully,
- no compile error was reported by the user,
- CP22 is therefore COMPILE-TESTED on the target laptop,
- the enlarged traversal itself still needs a focused PIE traversal/performance review.

CP23 milestone evidence on 2026-09-18:
- the living-world commits were pulled to the target laptop,
- UE4.27.2 launched into PIE successfully,
- the Shire rendered with Frodo / P1C01_Main, the opening objective and the enlarged world,
- The Mill landmark was visible,
- no compile/runtime error was reported for that launch,
- CP23 is therefore COMPILE-TESTED and BASIC PIE-TESTED on the target laptop.

Current post-CP23 source status:
- CP24A/CP24B voice/performance foundations, CP25 combat, CP26 biome/geography, CP27 runtime audio/proxy acting, CP28 production assets, CP29 self-hosted UE4 validation and CP30 world/checkpoint engineering are present in the current source.
- Current head `bd3d0be...` is STATIC-VALIDATED through Pre-Unreal Validation #112.
- Current head `bd3d0be...` is COMPILE-TESTED and ASSET-IMPORT-TESTED through Unreal Build Validation #10 on UE4.27.2 (`50 files, 0 failures`).
- The current head is NOT yet fully PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED.

The remaining hard gate is now the functional smoke-test layer: movement/interactions, F9 load round-trip, F8 route round-trip, chapter smoke tests and target-device performance/visual observation.

## Authoritative runtime chapter IDs

| Runtime ID | Chapter bucket |
| --- | --- |
| `P1C01` | Shire: Hobbiton, party, eastern fields, Black Rider road, ferry |
| `P1C02` | Bree |
| `P1C03` | Weathertop / Flight to the Ford |
| `P1C04` | Rivendell |
| `P1C05` | Fellowship road / camp / Caradhras / West Gate |
| `P1C06` | Moria: threshold, halls, Balin, Orc/Troll escalation, Balrog, bridge |
| `P1C07` | Lothlorien |
| `P1C08` | Anduin / Argonath / Amon Hen / Part I ending |

Do not reintroduce `P1C09`-`P1C12` as runtime chapter IDs.
Older planning used twelve narrative segments; those are now subregions/story segments inside eight runtime buckets.

## Current playable-route model

Main route:
- `RouteId = FrodoMain`
- episode convention: `P1C01_Main`, `P1C04_Main`, etc.
- playable character: Frodo

Parallel prototype:
- `RouteId = GandalfParallel`
- `EpisodeId = P1G01_Isengard`
- playable character: Gandalf
- region: Isengard / Orthanc

Per-route state is intended to preserve:
- quest stages,
- active quest,
- chapter,
- completed story beats,
- playable character,
- player transform.

A parallel route must not overwrite Frodo's main-route progress.

## Source-level handoff / architecture memory

The runtime module now has a code-local recovery entry point:
- `Source/ShireJourney/README.md` — start here when entering the runtime source tree.
- `Data/SourceArchitecturePlan.json` — machine-readable ownership/domain/target-path map for every runtime `.h`, `.cpp` and module `.cs` file.
- Project Guardian PG-019 requires the source handoff and architecture plan, and Pre-Unreal Validation rejects runtime source files that are missing from the manifest.

Current physical layout remains the guarded flat UE4.27 module. The planned maintenance layout is `Public/<Domain>` + `Private/<Domain>` with domains for Core, Characters, World, Subsystems, UI, SaveGame and Prototypes.

The physical folder migration has **not** happened yet. It must be a dedicated maintenance change, not mixed with gameplay, and must update includes plus static-validator path assumptions before a real UE4.27.2 build is accepted.

## Permanent user-requirement memory

The project no longer treats chat history as the authoritative record of user requests.

- `Data/ProjectGovernor.json` records persistent requirements with stable IDs, current status, evidence, missing work and acceptance criteria.
- `Docs/PROJECT_MEMORY_SYSTEM.md` defines how every meaningful future request must be captured and updated.
- `Docs/LIVING_WORLD_AI_BLUEPRINT.md` and `Data/LivingWorldFeaturePlan.json` preserve the user's living-world/NPC intelligence direction separately from current implementation status.
- Project Guardian validates the required memory artifacts and critical requirement/phase IDs.

Recovered/reaffirmed living-world intent is currently **PARTIAL/PLANNED**, not complete: ambient routines, awareness and social pauses exist, while full NPC-to-NPC dialogue, bounded dialogue creativity, persistent named-NPC memory/relationships and broader environmental micro-life remain future work.

## Project Governor / quality control

The project now has a deterministic internal control layer in addition to memory:

- `Data/ProjectGovernor.json` — the single authoritative source for requirements, priorities, conflicts, decisions, active gate and region quality states.
- `Scripts/project_governor.py` — CI validation of the single Governor.

This layer is specifically meant to stop silent requirement contradictions, false completion claims, inaccessible required routes, target-device performance regressions and acceptance of boring/frustrating sections without human pacing review.

It does not promise zero bugs. It enforces evidence and prevents known uncertainty from being hidden.

## Current architecture map

### Story / quest
`ShireQuestSubsystem.*`
- active quest and stages,
- current chapter,
- persistent one-time story beats,
- route / episode / playable-character state,
- per-route snapshots.

### Save
`ShireSaveGame.h`
- transform,
- quest/chapter state,
- completed story beats,
- route/episode/character,
- per-route progress.

### World routing
`ChapterWorldRouter.*`
- keeps one major generated region active at a time,
- removes previous generated prototype actors,
- builds current chapter,
- routes GandalfParallel to Isengard,
- restores route transform when appropriate.

### World builders
- `ShirePrototypeWorldBuilder.*`
- `BreePrototypeWorldBuilder.*`
- `FellowshipChapterWorldBuilder.*`
- `IsengardPrototypeWorldBuilder.*`

### Player / HUD
`ShirePlayerCharacter.*`
- movement / interaction / quick save-load,
- prototype appearance by playable character,
- temporary F8 route toggle,
- story-gated melee foundation for dangerous Part I chapters,
- persistent prototype health with a story-safe nonlethal floor until checkpoint/respawn UX is authored.

`ShireHUD.*`
- playable character / episode,
- active quest/objective,
- dialogue and alerts.

### Story presentation / dialogue / audio
- `ShireStoryPresentationSubsystem.*`
- `ShireDialogueSubsystem.*`
- `ShireAudioSubsystem.*`

The audio subsystem now resolves runtime ambience, music, SFX and voice assets by convention, keeps persistent ambience/music components, attaches world voice to matching actors, and ducks music during voiced dialogue.
Runtime voice playback now resolves `/Game/Audio/Voice/<Speaker>/<VO_ID>`, plays from the matching world actor when available, falls back to controlled 2D playback, and preserves subtitles when an asset is still missing.
`Data/VoiceCuePlan.csv` is statically synchronized with all runtime `VO_*` identifiers.
`Data/MusicCuePlan.csv` defines original music direction; final authored music and voice assets are not falsely claimed complete.

### Ambient life
`ShireAmbientNPC.*`
- walking/waiting routine,
- humanoid proxy movement,
- low-cost nearby-player awareness,
- look / cooldown / resume routine.

## Major work already present in current source

- Shire humanoid proxy pass.
- more Hobbiton paths, homes, fences, gardens, population and instanced foliage.
- optional Shire side stories.
- warm Shire morning presentation.
- deeper original Shire story dialogue.
- film-first story/canon bible.
- synchronized story/dialogue/music planning data.
- persistent multi-route story architecture.
- playable Gandalf/Isengard prototype route.
- Saruman / Orthanc / prison / industry / escape beats.
- deeper Rivendell social hub prototype.
- Fellowship camp / Boromir training / Crebain beat.
- Moria Watcher / Orc / Cave Troll / Balrog escalation.
- Lothlorien grief / Mirror material.
- Amon Hen Boromir pressure / defense / Fellowship break.
- lightweight ambient NPC awareness.
- CP21 Shire mega-pass source adds a mill/stream landmark, market detail, denser party preparation, crop rows, wooded-road cover, richer ferry geometry, more ambient residents/optional talkers and Black Rider last-known-position investigation behavior.
- CP22 Shire world-scale source pass expands Bag End-to-Ferry travel from roughly 50m to roughly 260m, separates Hobbiton/fields/wooded road/ferry with occlusion hills, introduces continuous curved roads and exploration loops, redistributes story/side-story actors to the larger geography, expands instanced ground cover and adds distance-adaptive ambient-NPC tick rates for the low-spec target.
- CP23 living-world source pass adds story-reactive atmosphere, reusable story-aware dialogue variants, persisted landmark discoveries, lightweight NPC-to-NPC social pauses near the player, running-sensitive Black Rider detection, and extra route/playable-character repair for restored saves.

## Story/data source hierarchy

Use all of these, with this priority for their purpose:

1. `Docs/CURRENT_PROJECT_STATE.md` — implementation/handoff truth and current hard gate.
2. `Data/ProjectGovernor.json` — single authority for user requirements, decisions, conflicts, active gate and region quality.
3. `Docs/PROJECT_MEMORY_SYSTEM.md` — rules for preserving requests and decisions across lost chats/developer changes.
4. `Docs/WORLD_PRODUCTION_BLUEPRINT.md` — world/chapter/checkpoint engineering map.
5. `Docs/LIVING_WORLD_AI_BLUEPRINT.md` — living-world/NPC intelligence design authority.
6. `Data/LivingWorldFeaturePlan.json` — machine-readable living-world implementation phases.
7. `Docs/DEVELOPMENT_GATES.md` — process and acceptance rules.
8. `Docs/PROJECT_GUARDIAN.md` — regression-memory model.
9. `Docs/STORY_CANON_BIBLE.md` — film-first canon and route vision.
10. `Docs/PART1_FELLOWSHIP_MASTERPLAN.md` — Part I production plan.
11. `Data/StoryBeatPlan.csv` — presentation beat plan.
12. `Data/DialogueIntent.csv` — dialogue intent.
13. `Data/MusicCuePlan.csv` — original music direction.
14. `Data/BiomePlan.csv` — chapter terrain/vegetation/water/weather/traversal/hazard/audio/performance contract.
15. Runtime C++ — actual implementation.

If runtime and documentation disagree, stop and reconcile them in the same change.

## Canon/content rules

- Peter Jackson film continuity is the primary Part I story spine.
- Extended Edition detail may enrich the game when it does not contradict the core route.
- Tolkien lore may enrich the world but must not silently replace film continuity.
- Side content may fill believable gaps but must not change required story outcomes.
- New dialogue is original; do not copy screenplay dialogue.
- Music must be original in melody/rhythm/theme; film music is only broad emotional reference.
- Frodo is the Ring-bearer main line, but the wider story is ensemble-based.
- Parallel playable routes require a clear canonical/story reason.

## Scope rule

Part II and Part III remain roadmap/design work until the current Part I production gate is healthy.

Do not stack another large feature on a current head that has not passed the real UE4.27 compile + PIE + target-device smoke test.

Active production order:
1. validate current head,
2. stabilize the Shire as the vertical slice,
3. continue chapter-by-chapter,
4. keep the trilogy documented without destabilizing the active build.

## Exact next hard gate

The current build/editor/PIE boot gate has passed. Continue with functional smoke testing in the already working build.

### Shire smoke test
- PIE starts in Shire.
- movement/camera/sprint/crouch/interact work.
- HUD shows Frodo and current episode.
- Shire quest advances.
- ambient Hobbits walk/wait and briefly notice/face the player.
- dialogue/alerts render.
- F5 saves.
- after moving, F9 restores expected player/story state.

### Parallel-route smoke test
- F8 switches to Gandalf / `P1G01_Isengard`.
- Isengard/Orthanc prototype exists.
- Gandalf can approach/interact with Saruman.
- parallel quest can advance through prison / industry / escape.
- F8 returns to Frodo.
- Frodo location and story progress are preserved.

### Chapter smoke test
Use F6/F7 only as developer navigation and confirm each world builds:
- P1C02 Bree
- P1C03 Weathertop/Ford
- P1C04 Rivendell
- P1C05 road/Caradhras/West Gate
- P1C06 Moria
- P1C07 Lothlorien
- P1C08 Anduin/Amon Hen

This does not mean those worlds are visually finished.

### Device observations
Record:
- crash/freeze,
- obvious hitching,
- severe memory pressure,
- unplayable frame-rate drops.

Target floor remains 720p / 30 FPS / Low-Medium / DX11.

## Failure procedure

If any gate fails:
1. stop feature expansion,
2. save/copy the exact log,
3. fix the smallest failing layer,
4. push to `develop`,
5. require green static CI,
6. rerun UE build,
7. rerun the exact failed PIE step,
8. update this handoff if project state materially changed.

Local one-click build failure log:
`Saved/Logs/LastOneClickBuildFailure.txt`

## Recovery procedure if chat context is lost

A new developer/assistant should:
1. open this file first,
2. confirm repo and `develop`,
3. inspect latest `develop` commit and both validation workflows,
4. read `Data/ProjectGovernor.json` so no recorded user request is lost,
5. read `Data/ProjectGovernor.json`, then `Docs/PROJECT_MEMORY_SYSTEM.md` and `Docs/PROJECT_GOVERNOR.md`,
7. open `Source/ShireJourney/README.md` before changing runtime code,
8. inspect `Data/SourceArchitecturePlan.json` for ownership and planned file location,
9. read `Docs/LIVING_WORLD_AI_BLUEPRINT.md` and `Data/LivingWorldFeaturePlan.json` before NPC/world-life work,
10. read `Docs/DEVELOPMENT_GATES.md` and `Docs/PROJECT_GUARDIAN.md`,
11. read `Docs/STORY_CANON_BIBLE.md` before story changes,
12. inspect the relevant StoryBeat/Dialogue/Music/Biome/Checkpoint data files,
13. never claim engine testing without a real UE4.27 result,
14. resume from "Exact next hard gate".

## Temporary developer controls

- F5 — Quick Save
- F9 — Quick Load
- F6/F7 — previous/next chapter debug navigation
- F8 — temporary Frodo/Gandalf route toggle

These are developer controls, not final player-facing menu design.


## Character / voice completeness rule

Character quality is now governed by:
- `Docs/CHARACTER_PERFORMANCE_STANDARD.md`
- `Docs/PRODUCTION_COMPLETENESS_MATRIX.md`
- `Data/VoiceCuePlan.csv`

These files are required Project Guardian inputs.
They explicitly cover facial acting, gaze, blink behavior, lip-sync, voice, body language, locomotion,
interaction animation, environmental reaction, combat reaction, crowd behavior, continuity and low-spec LOD/performance.
Current proxy characters do not satisfy final character quality; final rigs/animations/voice assets remain future production work.
