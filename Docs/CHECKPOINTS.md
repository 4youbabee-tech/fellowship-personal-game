# Development Checkpoints

## CP1 — Repository + UE4.27 Base
- Private repository initialized.
- `main` kept as stable baseline.
- `develop` created for active work.
- UE4.27 project descriptor and low-spec configuration added.
- Core systems present: player movement/camera, interaction, HUD dialogue, quest state, quick save/load, ambient NPCs, companion-follow prototype, Black Rider stealth prototype.

## CP2 — Chapter 1 Story Chain
- NPC interactions can transition into the next active quest.
- Quest triggers validate active quest + stage before progression.
- Chapter 1 chain defined from Shire arrival through Bucklebury Ferry.
- Gandalf, Bilbo, Sam, Merry and Pippin prototype story actors wired into progression.
- Sam/Merry/Pippin can enter lightweight follow mode after their story interactions.

## CP3 — The Shire Greybox World
- Runtime world builder implemented in C++ so the chapter can boot without a final `.umap`.
- Greybox includes Bag End, Hobbiton lane, Hobbit holes, Green Dragon silhouette, party field, eastern fields, Brandywine and Bucklebury Ferry destination.
- Lightweight ambient hobbit routines populate the village.
- Story progression locations are spatially connected in one playable route.
- Black Rider patrol/detection section placed before the ferry escape.

## CP4 — Logic Audit / Dead-End Fix
- Fixed NPC transition logic so `NextQuestId` calls `StartQuest`, ensuring HUD/objective and downstream triggers follow the new story beat.
- NPC story interactions now reject interaction when the required quest is not currently active.
- Full C++ compile and in-engine runtime validation remain pending until Unreal Engine 4.27 is available.

## CP5 — Chapter Framework + Save Persistence
- Added `CurrentChapterId` to the quest subsystem and save state.
- Save/load restores active chapter in addition to player transform and quest state.
- Quest triggers can transition directly into the next chapter and starting quest.
- Chapter 1 can hand off to `P1C02` without loading both regions at once.

## CP6 — Bree / Prancing Pony Greybox
- Added a dedicated Chapter 2 runtime world builder for Bree.
- Greybox includes the East Road approach, western gate, compact town streets, Prancing Pony exterior, common-room proxy, simple crowd flow and story interaction points.
- Added Chapter 2 progression: road to Bree, gate entry, Prancing Pony, Butterbur, common-room attention, Strider, private-room sequence, Nazgul night attack and dawn departure.
- All new dialogue is original game dialogue that follows scene intent rather than copying screenplay lines.

## CP7 — Cinematic Hooks + Weathertop Handoff
- Added generic `StoryBeatId` events that can later drive Sequencer/camera/audio without hard-wiring cinematics into quest logic.
- Bree story beats expose hooks for nightfall, inn exterior, Ring incident, Strider private-room beat, Nazgul attack and departure.
- Added Chapter 3 quest data for road-to-Weathertop and the Weathertop attack.
- Added a chapter world router so the active prototype region can change without keeping Shire and Bree builders active.

## CP8 — Full Part I Runtime Greybox Skeleton
- Added shared runtime greybox builders for Chapter 3 through Chapter 8.
- Chapter 3: wilderness, Weathertop, Nazgul pressure, Arwen/Flight-to-Ford handoff.
- Chapter 4: Rivendell valley, recovery, Council of Elrond and Fellowship formation.
- Chapter 5: southward road, Caradhras, western gate of Moria.
- Chapter 6: Moria halls, Balin's Tomb and Bridge of Khazad-dum progression.
- Chapter 7: Lothlorien rest/farewell and river departure.
- Chapter 8: Anduin, Argonath proxy, Amon Hen and Breaking of the Fellowship through Part I completion.
- Chapter router now recognizes all eight low-memory runtime regions used by the current prototype architecture.

## CP9 — Chapter Transition Safety Audit
- Fixed quest triggers so only `AShirePlayerCharacter` can progress story triggers; companion characters can no longer accidentally advance missions.
- Chapter changes now remove generated greybox geometry, labels, NPCs, riders and triggers from the previous region before building the next one.
- Added safe player spawn locations per runtime chapter so the pawn does not remain at coordinates from the previous region.
- Quick-load restores chapter/world state before applying the exact saved player transform.

## CP10 — Full Quest/Story State + Pre-Unreal CI
- Added quest definitions for every currently referenced Part I gameplay chain through Amon Hen/Part I completion.
- Added persistent one-time story beats so cinematic hooks do not replay after save/load.
- Save data now includes completed story beats along with chapter, active quest and quest stages.
- Added `Scripts/pre_unreal_validate.py` to check required files, `.uproject` JSON/UE4.27 target, C++ brace balance, Unreal `generated.h` include ordering, quest-definition coverage, chapter routing and generated-folder hygiene.
- Added GitHub Actions workflow `Pre-Unreal Validation` on pushes to `develop` and pull requests.

## CP11 — Companion Restore Continuity
- Recruited lightweight companions now recover their follow state after a save/load or runtime world rebuild by checking persisted quest-stage progress.
- Follow restoration is delayed until the first NPC tick so runtime world builders have already assigned each companion's quest and follow configuration.
- Repeating recruitment dialogue is no longer required just to make Sam, Merry or Pippin resume following after restored Shire state.

## CP12 — Black Rider LOS + Low-Spec Detection Pass
- Black Rider detection now subscribes to active-quest changes and performs detection work only while `KeepOffRoad` is active; inactive Shire play no longer polls the quest subsystem every detection interval.
- Line-of-sight uses simple `ECC_Visibility` collision instead of complex triangle tracing, matching the primitive greybox cover and lowering trace cost on the low-spec target.
- Detection now requires configurable consecutive visible samples before alerting, reducing one-frame edge/occlusion false positives while preserving crouch radius and forward-cone checks.
- Quest-change handling resets detection confidence immediately and save-state restoration remains compatible because the quest subsystem rebroadcasts the active quest during restore.

## CP13 — Real UE4.27 Baseline
- An earlier source baseline compiled and opened successfully in Unreal Engine 4.27.2.
- PIE was observed working on that earlier baseline.
- Movement, quests and HUD were observed working.
- Later C++ changes must be revalidated; historical engine success is not inherited automatically.

## CP14 — Shire Vertical-Slice Expansion
- Humanoid story/ambient proxies, richer paths/homes/gardens/fences/population and instanced foliage.
- Optional Shire side stories that do not replace the main quest.
- Warm morning presentation and deeper original Shire dialogue.
- Low-cost ambient population remains the target.

## CP15 — Canon / Data Alignment
- Added the Story Canon Bible.
- Runtime chapter truth standardized to P1C01-P1C08.
- DialogueIntent and StoryBeatPlan aligned with current runtime buckets.
- Added MusicCuePlan for original music direction.

## CP16 — Persistent Multi-Route State
- Added RouteId / EpisodeId / PlayableCharacterId.
- Added per-route quest/story/transform progress.
- Quick save/load persists route state.
- Parallel-route state is designed not to overwrite Frodo's main route.

## CP17 — Gandalf / Isengard Parallel Prototype
- Added Gandalf parallel route.
- Added Isengard/Orthanc runtime prototype.
- Added Saruman, prison, industry and escape progression.
- Added original dialogue and presentation/audio cue wiring.
- F8 is the temporary developer route toggle.
- Pre-Unreal Validation #74 caught missing presentation cues immediately after the world commit.
- The following presentation commit fixed the gap and #75 returned green.

## CP18 — Part I Depth + Ambient Awareness
- Rivendell expanded with Bilbo and wider Fellowship social presence.
- Fellowship road expanded with camp/training and Crebain.
- Moria expanded with Watcher, Orc/Troll escalation and stronger bridge approach.
- Lothlorien expanded with grief and Mirror material.
- Amon Hen expanded with Boromir pressure/defense before the split.
- Ambient Shire residents can notice/face the nearby player briefly, then resume routines.
- Runtime-code baseline reached Pre-Unreal Validation #77 successfully.

## CP19 — Project Memory / Guardian
- CURRENT_PROJECT_STATE is the recovery/handoff entry point.
- DEVELOPMENT_GATES defines build/PIE/device acceptance.
- PROJECT_GUARDIAN records repeatable regressions.
- ProjectGuardRules.json makes chapter/route/canon/document rules machine-readable.
- Pre-Unreal Validation is extended to detect story/data drift automatically.

## CP20 — Current UE4.27 Compile + Basic PIE Boot
- Pre-Unreal Validation #80 is green.
- UE4.27.2 + UnrealHeaderTool completed successfully on the target laptop after PG-010/PG-011 fixes.
- Unreal Editor launched successfully.
- PIE entered the Shire.
- Current HUD rendered Frodo / P1C01_Main and the opening objective correctly.
- This proves compile + basic PIE boot only; save/load, route round-trip and chapter smoke tests remain pending.

## CP22 — Shire World Scale & Traversal Mega Pass
- Expanded the Shire travel footprint so Bag End-to-Ferry is roughly 260m instead of one compressed arena.
- Kept Hobbiton socially dense while separating eastern fields, wooded road and ferry into distinct travel regions.
- Added terrain/hill occlusion so later landmarks are discovered through travel rather than visible from spawn.
- Rebuilt the main lane as a continuous curved road and added field/exploration loops.
- Redistributed Merry/Pippin, Black Rider, side stories and ferry progression to the new geography.
- Expanded HISM foliage across the larger world rather than multiplying ground-cover actors.
- Added distance-adaptive ambient-NPC tick intervals to protect the 30 FPS target.
- UE4.27.2 build was later confirmed successful on the target laptop.
- Focused traversal/performance acceptance is still pending.

## CP23 — Living Shire / Story-Reactive World
- Shire atmosphere can now react to active story phase through sun/sky/post-process changes.
- Added reusable contextual dialogue variants driven by persisted story beats and quest stage.
- Optional residents can change what they say after major local events.
- Ambient residents can enter short low-cost social pauses with nearby residents while the player is close.
- Running increases Black Rider detection range while crouching/cover remain meaningful.
- Added one-time persisted landmark discoveries for major Shire locations.
- Restored saves receive an additional route/playable-character identity repair.
- CP22 world-scale build was confirmed successful on UE4.27.2 target hardware before this pass.
- CP23 was later pulled, built and launched into PIE successfully on the target laptop.
- Basic PIE evidence showed Frodo / P1C01_Main, the opening objective, the enlarged Shire and The Mill landmark.
- Focused functional/performance acceptance is still pending.


## CP24A — Character Performance + Voice Completeness Guard
- Added a permanent Character Performance Standard covering face, eyes, gaze, blink, brows, lip-sync, voice, body language, locomotion, interactions, combat reactions, environmental reactions and continuity.
- Added a Production Completeness Matrix so a chapter cannot be treated as complete while major pillars are missing.
- Added Data/VoiceCuePlan.csv generated from all current runtime VO_* identifiers.
- Voice direction explicitly requires original performance and forbids cloning or deliberate imitation of a specific film actor.
- Current authored voice assets remain ASSET_PENDING; this checkpoint creates the contract and guardrails, not fake completion.

## CP24B — Runtime Voice Bridge
- Added deterministic runtime voice asset resolution using /Game/Audio/Voice/<Speaker>/<VO_ID>.
- Voice lines play spatially from the matching playable/NPC actor when available.
- Offscreen/unresolved speakers use controlled 2D fallback.
- Missing authored audio never breaks subtitles or quest progression.
- Added voice playback-state events so music ducking/facial-performance systems can react later without changing dialogue data.
- Pre-Unreal Validation now enforces a one-to-one contract between runtime VO_* identifiers and Data/VoiceCuePlan.csv.
- Actual SoundWave/SoundCue files remain ASSET_PENDING until authored/imported.

## CP25 — Part I Combat Foundation
- Added reusable lightweight Orc, Uruk-hai and Cave Troll enemy profiles.
- Enemy activation follows current quest/stage so threats do not leak into unrelated story moments.
- Low-cost enemy behavior covers range/LOS/chase/attack/home return with distance-adaptive ticking.
- Player melee is mapped to left mouse only when the current route/chapter permits combat; the Shire remains non-combat.
- Player health is visible during combat and persisted through F5/F9 save/load.
- Prototype health intentionally stops at 1 HP until death/checkpoint/respawn UX is authored, preventing story deadlocks.
- Moria now contains quest-gated Orc/Cave Troll combat pressure.
- Amon Hen now contains quest-gated Uruk-hai combat pressure.
- Chapter routing explicitly clears combat enemies between generated regions.
- Guardian checks the combat input, enemy profiles, health persistence and region cleanup.
- This commit still requires real UE4.27 compile/PIE before COMPILE-TESTED or PIE-TESTED status.

## CP26 — Part I Biome / Geography Mega Pass
- Added Data/BiomePlan.csv as a machine-checked identity contract for every runtime chapter.
- Weathertop now has distant broken ridges, wet lowlands/marsh pools and a readable Ford river approach.
- Rivendell now has enclosing valley walls, layered terraces and waterfall ribbons.
- Caradhras now has a stronger mountain silhouette and layered snow sheets along the pass.
- Moria now reads as one route through a much larger underground city with side walls, ceiling ribs, rubble and a deeper bridge abyss.
- Lothlorien now has a distinct golden canopy and leaf-bed palette rather than generic green forest language.
- Anduin/Amon Hen now has canyon walls and river islands to enlarge the Argonath/river scale.
- These are low-cost runtime prototype biomes using basic shapes; final authored terrain/material/vegetation assets are still pending.
- Guardian now fails if any P1C01-P1C08 chapter lacks a complete biome contract.

## CP27 — Runtime Audio Mix + Proxy Acting Foundation
- Runtime ambience, music and SFX now resolve deterministic asset paths under /Game/Audio/.
- Persistent ambience/music components stop and replace cleanly when story cues change.
- Voiced dialogue ducks music to roughly 36% and restores it when the line finishes.
- World voice is attached to the matching speaker actor instead of remaining at the initial location.
- Current NPC proxies now have temporary eye/mouth geometry, natural-offset blinking, near-player head gaze and approximate mouth motion during direct dialogue.
- This acting layer is a development bridge only; it does not replace final skeletal face rigs, visemes or authored animation.
- Guardian checks runtime audio categories, dialogue ducking and the proxy acting foundation.
- Final audio assets and final facial animation remain pending production.

## CP28 — Production Asset Pipeline + Shire Environment Pass
- Added original project-managed production source assets under `SourceAssets/Production`.
- Added automatic UE4.27 editor import through `ShireProductionImport`.
- Shire runtime now prefers imported production meshes and keeps BasicShapes as fallbacks.
- Added production ground/road, Hobbit facade, fences, vegetation/rocks and lived-in props such as carts, benches, lanterns and mill-wheel geometry.
- Added original project-generated surface maps/material references for Shire environment assets.
- Fixed UE4.27 import/build regressions and recorded them in Project Guardian.
- This checkpoint is compile/import validated but still needs focused PIE/device visual acceptance.

## CP29 — Self-Hosted UE4 Compile + Asset-Import Gate
- Repository-level Windows self-hosted runner is active on the UE4.27.2 target laptop.
- `Unreal Build Validation` checks the exact pushed commit.
- The workflow verifies UE4.27.2, compiles `ShireJourneyEditor`, and runs the production asset import commandlet.
- Pre-Unreal Validation #110 succeeded for `8b0c13f...`.
- Unreal Build Validation #8 succeeded for the same head, including production asset import.
- A green build/import gate still does not replace PIE/device/visual acceptance.

## CP30 — World Engineering / Player Checkpoint Contract
- Added `Docs/WORLD_PRODUCTION_BLUEPRINT.md` as the project-wide world engineering map.
- Added `Data/WorldCheckpointPlan.csv` with safe checkpoint intent for every P1C01-P1C08 chapter.
- Guardian now requires both files and validates unique checkpoint IDs, approved chapters, known story beats and supported save/status values.
- Dedicated automatic checkpoint/respawn runtime behavior remains pending implementation; this checkpoint establishes the non-ambiguous contract first.
- Initial CP30 commit `10ac91e...` passed Unreal Build Validation #9 but Pre-Unreal Validation #111 failed because the new checkpoint validator referenced `story_plan_ids` before that value existed.
- Follow-up `bd3d0be...` derived the checkpoint story-beat set directly from the already-loaded story rows; Pre-Unreal Validation #112 then succeeded.
- Unreal Build Validation #10 also succeeded on exact head `bd3d0be...`: UE4.27.2 C++ build passed and the production import reported `50 files, 0 failures`.

## CP30A — Source Architecture / Handoff Contract
- Added `Source/ShireJourney/README.md` as the runtime-code handoff entry point so recovery does not depend on chat history.
- Added `Data/SourceArchitecturePlan.json` with one explicit domain/role/current path/target path record for every runtime module `.h`, `.cpp` and `.cs` file.
- Defined the controlled target layout as `Public/<Domain>` and `Private/<Domain>` across Core, Characters, World, Subsystems, UI, SaveGame and Prototypes.
- Added Project Guardian PG-019 so untracked, duplicate, stale or misclassified runtime source files fail Pre-Unreal Validation.
- Updated the production completeness matrix through CP28-CP30 and documented CP29 self-hosted UE4.27.2 build/import evidence separately from gameplay/visual maturity.
- This is a governance/maintenance checkpoint only. It does **not** claim the physical source-folder migration has happened and it does not change gameplay.
- Physical migration remains a dedicated follow-up maintenance change after the current functional smoke-test gate is healthy.

## CP30B — Permanent Requirement Memory + Living World Intelligence Contract
- Added `Docs/PROJECT_MEMORY_SYSTEM.md` so project continuity no longer depends on chat history or one programmer's memory.
- Added `Data/ProjectRequirements.json` as a stable-ID ledger for user requests, current status, evidence, missing work and acceptance criteria.
- Recovered and explicitly recorded major long-lived requirements for living-world traversal, rich geography, NPC routines/social life, NPC-to-NPC conversation, bounded dialogue creativity, persistent named-NPC memory, save continuity and target-laptop performance.
- Added `Docs/LIVING_WORLD_AI_BLUEPRINT.md` defining the intended living-world/NPC intelligence architecture and its low-spec boundaries.
- Added `Data/LivingWorldFeaturePlan.json` with phases LW0-LW6 so future developers can distinguish existing foundations from planned work.
- Added Guardian PG-020/PG-021 and static checks for requirement-ledger integrity and living-world plan completeness.
- Existing ambient NPC routines, awareness, social pauses and proxy acting are recorded as foundations only; full NPC conversation/memory/intelligence is **not** falsely claimed implemented.
- This checkpoint is governance/design memory. It does not open a new gameplay feature while the current functional F9/F8/chapter/device gate remains pending.

## CP30C — Film-First Playable Experience Contract
- Reaffirmed the product vision: the Peter Jackson film continuity is the story spine to be lived through, not replaced by a newly invented main plot.
- Added `REQ-VISION-001`, `REQ-EXP-001`, `REQ-EXP-002` and `REQ-COVERAGE-001` to the permanent requirement ledger.
- Added `Data/FilmExperiencePlan.json` with high-level Part I film anchors for P1C01-P1C08 plus the Gandalf/Isengard parallel route.
- Each anchor records canon class, intended gameplay/presentation treatment and current coverage state without copying screenplay dialogue.
- Added Guardian PG-022 so every runtime Part I chapter and required route must remain represented in the coverage plan.
- Clarified the design rule that player freedom/exploration lives mainly between fixed story anchors and must not erase or reorder required film outcomes without an explicit recorded decision.
- This checkpoint is a story/product-governance contract, not a claim that all film scenes are already implemented or visually accepted.

## CP30D — Project Governor / Quality and Conflict Control
- Added `Docs/PROJECT_GOVERNOR.md` as the human-readable control contract.
- Added `Data/ProjectGovernorPolicy.json` with hard invariants for project memory, film story, integrity, traversal, target-device performance and proof-level honesty.
- Added `Data/ProjectDecisions.json` so conflicting requests are resolved explicitly rather than one silently replacing another.
- Recorded current accepted tradeoffs for film anchors versus exploration freedom, living-world richness versus low-spec performance, and source reorganization versus the active functional gate.
- Added `Data/ExperienceQualityGates.json` for P1C01-P1C08 plus Gandalf/Isengard with STATIC, COMPILE, BOOT, TRAVERSAL, PERSISTENCE, PERFORMANCE, PACING and VISUAL evidence states.
- Added `Scripts/project_governor.py` and wired it into Pre-Unreal Validation.
- Added permanent requirements for governor continuity, accessible required gameplay spaces and human pacing/enjoyment review.
- The Governor does not claim zero bugs or automatically judge fun; it forces uncertainty, conflicts and missing evidence to remain visible and blocks malformed/contradictory structured state.

## CP30E — Single Project Governor Authority
- Consolidated requirements, priorities, conflicts, decisions, active hard gate and region quality states into one authoritative file: `Data/ProjectGovernor.json`.
- Removed the former secondary authority files `ProjectRequirements.json`, `ProjectGovernorPolicy.json`, `ProjectDecisions.json` and `ExperienceQualityGates.json`.
- Updated `Scripts/project_governor.py` so CI rejects any attempt to reintroduce those secondary authority files.
- Supporting story/world/source/living-world/checkpoint plans remain detailed references, not independent project managers.
- Added a worker contract: programmers may specialize, but no worker changes global direction independently of the Governor.
- Recorded large-team integration discipline as `REQ-CI-001`: required checks/branch protection should guard shared integration; repository administration enforcement is still pending because the current connection does not expose admin-write access.
- This checkpoint is governance-only; current gameplay hard gate remains F9/F8/chapter/device validation.

## CP30F — LW1 NPC Social Data Foundation
- Added `Data/NPCSocialModel.json` as the Part I data-first identity/schedule/relationship contract.
- Added stable named NPC identities plus Shire/Bree ambient archetypes, including alias handling so one character cannot accidentally split into duplicate persistent identities.
- Added roles, communities, temperament tags, bounded knowledge tags, persistence tiers and location/anchor intent.
- Added low-cost Shire/Bree/story-driven schedule templates with STORY_OVERRIDE/DANGER_OVERRIDE precedence.
- Added an initial authored relationship graph and external player-actor reference support.
- Added PG-024 static validation for required named profiles, identity uniqueness, aliases, relationship endpoints/types, schedule assignment and normalized schedule weights.
- Updated LW1 planning and the single Project Governor to record the data layer as PARTIAL while runtime scheduler/social-context consumption remains pending.
- No runtime gameplay behavior changed; this was deliberately selected as remote-safe work while the F9/F8/chapter/device gate remains open.

## CP30H — Self-Hosted Runner Network Resilience
- Investigated Unreal Build Validation #14 and confirmed it failed before UE compilation because the Windows runner's Git fetch repeatedly suffered connection resets / early EOF / invalid pack data.
- The failure path also hit GitHub artifact-storage quota, which was secondary noise rather than the primary build failure.
- Replaced `actions/checkout` in the Unreal self-hosted workflow with exact-`GITHUB_SHA` GitHub API archive download using explicit retry/all-error handling.
- Removed failure-path dependency on `actions/upload-artifact`; UE build/import logs remain printed in the workflow and available in the local self-hosted workspace.
- Added PG-026 to prevent returning to the flaky acquisition/log-upload pattern.
- This checkpoint changes CI infrastructure only. A new green self-hosted run is required before claiming the hardened path validated.

## CP30I — Self-Hosted PowerShell Policy Fix
- Unreal Build Validation #18 reached the resilient exact-commit checkout step but failed before download because Windows PowerShell blocked the generated Actions script under the target machine execution policy.
- Updated the checkout shell to run with `-NoProfile -ExecutionPolicy Bypass`.
- Added PG-027 so the self-hosted workflow cannot silently return to the blocked shell form.
- This remains CI infrastructure work only; a new green UE4.27.2 compile/import run is still required.

## CP30K — LW2-LW5 Remote-Safe Intelligence Contracts
- Added `Data/NPCConversationPlan.json` for bounded NPC-to-NPC conversation eligibility, intents, knowledge/story gates, priority, cooldowns and repetition policy.
- Added `Data/NPCMemoryPlan.json` for compact named-NPC memory tiers, expiry, route partitioning, save budgets and alias identity sharing.
- Added `Data/LivingWorldEventPlan.json` for chapter-specific workers/travelers/social moments/fauna/weather/prop motion/danger reactions and low-spec activity caps.
- Added `Data/BoundedDialoguePlan.json` for authored/template/cached dialogue variation, default-deny knowledge, canon safety, line/cache limits and deterministic fallback.
- Added static guards PG-025/PG-028/PG-029/PG-030 so these contracts cannot silently drift or become unbounded.
- Updated LW2-LW5 planning and the single Project Governor to record data-contract progress while leaving runtime behavior gated.
- No new gameplay runtime system was enabled by this checkpoint.

## CP30L — Self-Hosted Runner Resilience Validated
- Unreal Build Validation #19 succeeded on exact commit `0936f2e779c6a6d1b4d209628d206f5d11ca3f9c`.
- The runner successfully used the resilient exact-SHA archive checkout with PowerShell execution-policy bypass.
- Unreal Engine 4.27.2 was detected, UnrealHeaderTool/C++ build completed, and the production importer reported `50 files, 0 failures`.
- This closes the CI infrastructure regression from Builds #14/#18. It does not replace the still-pending gameplay PIE/device hard gate.

## CP30M — Governor Work Reminders + Pacing Review Contract
- Added `Data/PlayerExperiencePacingPlan.json` with human-review dimensions and chapter-specific pacing focus/risk flags for P1C01-P1C08 plus Gandalf/Isengard.
- Updated `Scripts/project_governor.py` so every validation run prints the active gate and unfinished CRITICAL/HIGH requirements with the next recorded missing-work item.
- Updated `REQ-MEM-002` to IMPLEMENTED for project-session reminders.
- Updated `REQ-QUALITY-002` to PARTIAL: pacing criteria are structured, but human play review/tuning is still pending.
- CI validates coverage of the pacing-review contract but does not claim that any chapter is fun or accepted.

## CP31 — Playable Character Production Motion Pass
- Began visible gameplay production work with the existing imported Frodo/Gandalf modular character meshes rather than another planning-only checkpoint.
- Added explicit production-character runtime state so per-frame animation no longer assumes fallback BasicShape face/accessory coordinates.
- Added distinct movement presentation for idle, walk, sprint, crouch and airborne states.
- Added torso/head lean, foot lift/rotation, cloak sway, Frodo satchel motion, Gandalf hat/beard follow-through and character-specific attack/weapon motion.
- Added a runtime `CharacterVisual` log showing whether Frodo/Gandalf resolved production meshes or fell back to prototype shapes.
- Recorded `REQ-CHAR-001` and `DEC-004` in the single Project Governor. This is a bounded user-directed exception to the normal hard-gate order: no story/save/route architecture is changed.
- This pass is **not yet accepted** until Pre-Unreal is green, UE4.27.2 compile/import is green, and Frodo/Gandalf receive PIE visual review.

## CP32 — Part I Character Population Pass
- Added `Data/CharacterPopulationPlan.json` with 20 core named characters, threat cast, ambient population roles, chapter-by-chapter cast requirements and explicit visual tiers.
- Kept Sam, Merry and Pippin physically present through Bree and P1C03 travel instead of leaving Frodo visually alone.
- Completed the Rivendell social/council cast with Sam, Merry, Pippin and Arwen alongside Gandalf, Aragorn, Boromir, Legolas, Gimli, Bilbo and Elrond.
- Added Fellowship travel presence across P1C05-P1C08, including story-aware formation release so authored separation/capture beats stop the appropriate companions from following.
- Added region-aware ambient silhouettes: Shire residents remain Hobbit production archetypes, Bree crowds become human-townsperson proxies, and Rivendell/Lothlorien receive moving Elf residents.
- Fixed post-spawn ambient role assignment so the visual style reapplies when a builder changes `RoutineRole`.
- Added PG-032 and `REQ-CHAR-002` / `DEC-005` so full-cast population and unfinished visual tiers remain explicit.
- This checkpoint does **not** claim final character art. Frodo/Gandalf have dedicated production meshes; Hobbit companions currently share the Hobbit production archetype; many other named characters remain distinct procedural proxies pending dedicated character production.
- Requires Pre-Unreal + real UE4.27.2 build before merge, followed by PIE visual/population/performance review.

## CP33 — Core Cast Visual Identity + Build-First Batch Mode
- Activated the user-directed `BUILD_FIRST_BATCH_MODE`: continue substantial construction now, keep static + real UE4.27.2 compile/import gates mandatory, and defer detailed PIE/device/pacing/visual acceptance to a later integration/repair pass.
- Added lightweight modular identity pieces to `AShireNPC`: cloak, primary prop, secondary prop, beard and headpiece.
- Added distinct runtime silhouettes for Sam, Merry, Pippin, Aragorn/Strider, Boromir, Legolas, Gimli, Gandalf/Saruman and major Elven story characters.
- Accessories move with the existing procedural gait so cloaks/weapons/beards do not remain completely rigid while the NPC walks.
- Updated `Data/CharacterPopulationPlan.json` with an explicit visual-identity pass and a proof limit: procedural identity is not final character art.
- Added PG-033 to preserve distinct cast identity and prevent build-first mode from falsely marking manual evidence as passed.

## CP34 — Part I World Density / Landmark Detail Pass
- Deepened Bree streets and Prancing Pony surroundings with market stalls, puddles, lantern posts and crate/prop clusters.
- Deepened the P1C03 marsh/Weathertop approach with reeds, route-edge rocks and summit camp remains.
- Deepened Rivendell with arcades/columns, garden detail and resting places.
- Deepened the Fellowship road/Caradhras with scree, cairns, route markers, camp bedrolls and packs.
- Deepened Moria with a pillar forest, architectural caps and cold brazier/fire-color proxies.
- Deepened Lothlorien with elevated talan platforms, path spans and warm canopy lights.
- Deepened Anduin/Amon Hen with boat silhouettes, reeds, shoreline camp details, ascending stair fragments and broken lookout stones.
- Added PG-034 and updated the single Project Governor.
- This is a low-cost procedural world-density pass for build-first mode, not final environment-art or visual acceptance.

## CP35 — Lightweight Outdoor World Motion
- Added a low-cost `Bird` visual/motion role to the existing `AShireAmbientNPC` instead of introducing a separate heavy fauna system.
- Bird actors use 3D point-to-point motion, procedural wing flap and the existing distance-based tick throttling.
- Added sparse sky-life groups to Shire, Bree, Weathertop/Ford, Rivendell, Fellowship road/Caradhras, Lothlorien, Anduin/Amon Hen and Isengard.
- Moria intentionally receives no natural fauna so its dead-city atmosphere remains distinct.
- Updated LW4 runtime evidence and the single Project Governor.
- Added PG-035 to preserve the low-cost movement/performance contract.
- This is a runtime world-motion foundation, not final fauna art, final density or device/performance acceptance.

## CP36 — Ambient Resident Micro-Life
- Added `ActivityPropType` and a single cheap `ActivityProp` component to `AShireAmbientNPC`.
- Added role-driven visible activities: Shire party mugs, courier satchels, field-worker baskets, ferry crates, mixed Bree goods/mugs/crates and Elven books/lanterns.
- Added lightweight work/social arm gestures and carried-prop bob/sway using the existing ambient tick.
- Reused the existing distance-throttled ambient actor rather than adding a separate expensive AI/runtime system.
- Updated LW4 runtime evidence and the single Project Governor.
- Added PG-036 so resident activity variety cannot silently regress.
- This is not final authored animation or full micro-event direction; those remain future batch work and integration review.

## CP37 — Automatic Safe Checkpoint / Respawn Runtime Foundation
- Added a separate `ShireJourney_Checkpoint` SaveGame slot; automatic saves never overwrite the user's F5 manual save.
- Refactored F5/F9 and checkpoint recovery through shared snapshot/restore helpers so quest, chapter, story beats, route, episode, playable character, route snapshots, transform and health use one persistence path.
- Added authored story-beat checkpoint bindings for safe/pre-danger checkpoints in `WorldCheckpointPlan.csv`.
- Added post-world-rebuild chapter-transition checkpoint queuing so transition transforms belong to the destination region rather than the destroyed source region.
- Added an initial `WC_P1C01_START` checkpoint when a new Frodo/Shire session has no checkpoint yet.
- Combat defeat now restores the most recent automatic safe checkpoint at full health when one exists.
- Advanced `WorldCheckpointPlan.csv` runtime statuses from `PLANNED` to `FOUNDATION`; this records implementation only and does not claim PIE/device verification.
- Added PG-037 to protect manual/automatic slot separation and reject checkpoint-plan/runtime drift.

## Current hard gate
Current CP30 head `bd3d0be...` is STATIC-VALIDATED, COMPILE-TESTED and ASSET-IMPORT-TESTED. It is not yet fully PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED.

It must still pass:
1. Shire movement / interaction / NPC-awareness smoke test,
2. save/load round-trip,
3. Gandalf/Isengard F8 round-trip,
4. chapter smoke tests P1C02-P1C08,
5. target-device performance observation.

No new major feature checkpoint should open before this functional gate is healthy.

See `Docs/CURRENT_PROJECT_STATE.md` for the exact current test checklist.
