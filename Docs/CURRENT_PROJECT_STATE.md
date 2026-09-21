## 2026-09-21 - diegetic living-NPC requirement reaffirmed

The owner explicitly reaffirmed the intended player experience: the surrounding world should feel intelligent from inside the fiction. Each named character should respond from their own identity, source-grounded history, home/region, role, relationships, valid memories and what they could plausibly know at the current chronology. Ambient inhabitants receive cheaper regional/cultural archetype intelligence so the target laptop is not asked to persist a full individual brain for every crowd actor.

This is not fourth-wall AI. NPCs must never know they are in a game, identify themselves as software/NPCs, address the user as an external player, or expose quest/chapter IDs, HUD/UI, save/load/checkpoint, debug/developer controls, prompts/scripts or AI/LLM/model internals. Chapter/route/quest state remains hidden system context used only to gate/rank appropriate in-world behavior.

Current source already provides a real foundation: NPCSocialModel has 22 profiles; all 22 have region, knowledge tags and knowledge limits, while 19 currently carry explicit origin, occupation and biography facts. UShireNPCContextSubsystem gates profile availability by current region/chapter, enforces intent knowledge tags, story-beat/memory requirements, regional mood and relationship-influenced deterministic selection. This is source-level evidence, not PIE/device acceptance.

PG-120 now statically protects the diegetic self-model in BoundedDialoguePlan, LivingNPCIntelligencePlan and LivingNPCIntelligenceRoadmap. Future optional local language expression must consume only bounded in-world context and preserve deterministic fallback.

## 2026-09-21 - runner-offline programmer-proposal hardening wave

Owner requested immediate production restart after the deleted-chat interruption, with periodic programmer proposals reviewed against live repository evidence and only useful verified parts promoted.

The self-hosted UE4.27.2 laptop runner is intentionally offline. Current PR #62 head before this hardening batch is `ba00144b833de47f80da541b940830b17d7585a5`: Pre-Unreal #548 passed; Unreal #383 is pending because the runner is unavailable. Pending/queued runner state is not a demonstrated code failure.

This static-safe batch implements the previously tracked local-preflight recommendation: `SHIRE_UPDATE_BUILD_LAUNCH.bat` now runs `Scripts/run_local_preflight.ps1` before Unreal compilation/import. The resolver avoids Windows Store aliases and runs the static/governor/audit/test family before the engine build. This implementation is not yet Windows-observed; do not label it COMPILE-TESTED or DEVICE-TESTED.

Verified useful programmer guidance is now durable architecture policy: no new heavy synchronous `LoadObject` debt, bounded ambient NPC pooling required after V10/transition reconciliation, animated production characters/creatures use skeletal FBX, new authored textures use PNG/TGA, and PBR masks are channel-packed where applicable. `Data/ArchitectureGuardrails.json` plus `Scripts/deep_project_audit.py` enforce legacy debt ceilings so current debt may decrease but may not silently grow.

Legacy debt snapshot: 24 production BMP files, 115 character OBJ files, 30 enemy OBJ files, one direct `SpawnActor<AShireAmbientNPC>` site in LivingWorldDirector, and direct LoadObject counts of FellowshipChapterWorldBuilder=77, ShirePrototypeWorldBuilder=55, BreePrototypeWorldBuilder=22, IsengardPrototypeWorldBuilder=10, LivingWorldDirector=13, ShireNPC=4, ShireAmbientNPC=3.

Runtime pooling and residual async-load migration are intentionally not edited on this overlapping V10 branch. First machine-prove/merge V10, then reconcile PR #63 world-transition coordination, then change LivingWorldDirector lifecycle/asset ownership on a focused branch.

## 2026-09-21 - lost-chat recovery reconciliation and production restart

Authority remains `Data/ProjectGovernor.json`. Live repository reconciliation establishes `develop@f4886b39feea29973543bf6cfb1be4659f10ff9d` as the current green integration baseline. That exact develop head passed Pre-Unreal #543 and Unreal Build #378, including build/import/startup/P1C01-P1C08/state/warning machine gates. This is machine evidence only; no new PIE/device/visual acceptance is inferred.

PR #62 (`production/early-realms-world-life-v1`) reached exact head `d6533289dda37458b54bf5b63b82251502900eab` and passed Pre-Unreal #546 plus Unreal Build #381. It contains the V10 culture-specific Shire/Bree/Rivendell/Lothlorien world-life/density work. This recovery/documentation synchronization advances the PR head beyond d653, so the refreshed exact head must pass fresh machine gates before merge.

PR #63 (`repair/world-transition-coordination-v1`) remains a separate draft repair at `f4ef3a188b1a278a796e0c34d7158c2af8c72e80`. Pre-Unreal #547 passed. Unreal Build #382 is queued and the UE job has not started, so there is no Unreal result for that repair. It overlaps PR #62 in `LivingWorldDirector` and Governor state and must be reconciled rather than blindly merged.

The Project Source library is treated as recoverable external reference state, not chat memory. `Data/OwnerSourceReferenceIndex.json` remains the durable identity/precedence map for Sources 01-11, the three supplied film screenplays and the full Tolkien volume. The owner reports the previously missing Project Source files are restored. This repository update records that report but does not claim a fresh SHA-256 recheck for newly re-added files that are not exposed as bytes to the current worker.

Branch policy is now explicit in DEC-028: `develop` remains the canonical integration/recovery trunk. `main` stays the stable/default scheduler branch for now. Do not force-copy or rewrite history merely to make `main` look current.

Immediate path: re-prove the refreshed PR #62 exact head -> merge V10 only if green -> reconcile/port PR #63 on top of the new develop while preserving V10 density/profile logic -> harden builder-failure rollback/transaction behavior -> re-prove that repair -> resume visible world/character production. Public/Private C++ migration remains a separate later maintenance branch.

## 2026-09-21 - path cleanup before post-V5 production

Authority remains `Data/ProjectGovernor.json`. The integration baseline is `develop` at `8d7247d229b5cd51e8aea5617e1e2030b38229bf`, green after PR #60 with Pre-Unreal #532 and Unreal Build #367. There is exactly one open production PR: #61, `production/chapter-streaming-v5`.

The latest V5 code head before this cleanup is `b882b052a59c8d4e19437d7877dc30c9b1ea5daf`. Pre-Unreal #538 passed; Unreal Build #373 was pending when this reconciliation was written. Earlier V5 failures were narrowed to concrete UE4.27 issues and repaired: the `FStreamableHandle` declaration conflict (#370), invalid conditional `UE_LOG` verbosity (#371), and a stale async completion edge case after returning to an already resident world. This cleanup commit is newer than those checks and must earn fresh exact-head proof.

The path is now explicit: finish V5 -> merge only after exact-head Pre-Unreal + full Unreal validation -> confirm develop returns green -> measure chapter seam hitch/streaming pool/resident memory on representative target hardware -> open the next short production branch. No V5 FPS/RAM/VRAM improvement is claimed from architecture alone.

The next production branch is intentionally focused on visible world life rather than another mixed mega-branch: Shire, Bree, Rivendell and Lothlorien first for architecture density, culture-specific dressing, bounded NPC density, routines and ambient life. The character-quality lane advances through real skeleton/skin/Skeletal Mesh/AnimBP/animation work; OBJ-to-FBX container conversion alone is not treated as rigging.

Repository hygiene was reconciled. PR54 and PR56-PR60 short branches are historical cleanup candidates after external-reference checks. `recovery/stached-charcter` and `repair/post-merge-unreal-339` are preserved. The scheduled "Develop 20-Min Validation" appearing under `main` is expected GitHub scheduler behavior because `main` is the default branch; that workflow explicitly checks out `develop` and does not change the rule that production work integrates through `develop`.

## 2026-09-20 — V6 continuation and source/governor audit

Authority remains `Data/ProjectGovernor.json`. Its previous handoff was stale at #303; the actual verified baseline is `cd58be1e1cea033295a163ef2a90985f30471c2b`, Pre-Unreal #484 and Unreal #319, including import/startup/eight chapters/state/save/warnings. V6 head `93092a82b95418552728c73e02d31c220a7457ac` passed Pre-Unreal #485. Unreal #320 attempt 1 was interrupted during UHT/build (Ctrl-C, -1073741510); this is not a demonstrated C++ code defect. The single rerun (attempt 2) was also interrupted, before compilation at the editor-wait step. The cancellation trigger is not established; no further blind reruns were requested.

V6 refines original modular head/torso/hair geometry for nine Fellowship characters; it is not final skeletal animation or visual acceptance. Preserve that distinction.

The Governor now validates exact SHA scope for baseline/current workflow evidence and prints when a checkout is not covered by the recorded snapshot. A successful ancestor cannot silently certify the current checkout. Six regression cases cover mixed SHA evidence, cancelled current runs, invalid green baselines and missing experiential boundaries.

Uploaded source identities were verified against the reference index. Bible 09 now has its fingerprint. Targeted review of story, mission and visual-reference guidance confirms safe optional windows, explicit mission state/QA and the separation of visual inspiration from canon. The reference books' F1-xx identifiers do not equal runtime P1Cxx identifiers; numeric suffix matching is unsafe. Full scene-level provenance and rendered/device acceptance remain open. Green #319 still carries 132 unique near-zero-binormal identities under the existing 150 limit; passing the warning guard does not mean zero asset debt.

## 2026-09-20 — final lightweight geometry-warning cleanup

The green #302 baseline still carried 50 degenerate-tangent and 53 nearly-zero-binormal import identities. Inspection of representative production OBJ sources confirmed that these flat-color meshes have no `vt` texture-coordinate records. MikkTSpace therefore had no valid UV basis and was generating warning debt that did not improve the current material path.

The production importer now detects untextured OBJ meshes and explicitly computes normals with UE4's built-in tangent generator while keeping MikkTSpace/default behavior available for any future OBJ that actually supplies texture UVs. The exact-head chain must prove the warnings are removed before the debt is marked fixed or warning ceilings are tightened.

Two obsolete bootstrap/checkout PowerShell scripts are removed in the same cleanup because the workflow now bootstraps and checks out safely before repository scripts are available.

## 2026-09-20 — warning evidence scope repair

Run #300 confirmed the material persistence repair itself works: 225 authored material packages were explicitly saved with zero failures and the commandlet verified zero missing physical files. The warning gate remained red because import-time `LoadObject` existence probes intentionally asked for not-yet-created material packages, generating 216 warnings before synthesis.

That is now corrected at both ends: importer probes use `FindObject` plus `FPackageName::DoesPackageExist` before any load, and missing-package debt is evaluated from runtime startup/chapter/state logs rather than the import log. Exact-head CI logs are also cleared before each run so stale evidence cannot contaminate a new SHA.

The runtime missing-world-package ceiling is now zero. Any package that is genuinely absent after import will still fail the gate.

## 2026-09-20 — exact-head material persistence final blocker

Run #299 proved the entire machine chain through real UE4.27.2 build/import/startup, P1C01-P1C08 and isolated disk save/state roundtrip. The only failing gate is warning debt: 216 unique world material packages are referenced by imported meshes but are absent on disk.

The importer already synthesizes the intended authored material instances. The repair now bypasses unreliable unattended editor save helpers for these packages and writes each package explicitly with `UPackage::SavePackage` to its deterministic `.uasset` path, then verifies physical file existence before the commandlet can report success.

No threshold was raised and no debt was hidden. The next exact-head run must prove this repair.

## 2026-09-20 — mega-wave runway repair

The pre-production runway was repaired before the next mega build wave. REQ-AUDIT-001 is now represented in the master roadmap/tracked snapshot, PG-037 validates the new asynchronous checkpoint contract, and the Windows UE4 CI target now uses project-only clean intermediates, single-action compilation and CI-only disabled debug symbols to remove the recurring VS2019 D8050 debug-record failure mode. Local developer/editor builds retain normal debug symbols.

This is preparation, not a green claim: the new exact head must still pass Pre-Unreal and the real UE4.27.2 compile/import/startup/eight-chapter/state/warning chain.

## 2026-09-20 — deep exact-head validation reconciliation

Exact head `c023a735e3e390b8d591e1f6df9d07aeaa054754` reached the strongest automated evidence chain so far: Pre-Unreal #450 passed, and Unreal Build Validation #285 passed the isolated MSVC probe, UE4.27.2 C++ build, production asset import, Python resolution, playable startup, every P1C01-P1C08 chapter audit, and the route/story/state audit with an actual isolated disk save/load roundtrip.

The workflow failed only at warning-debt aggregation. Audit of the guard found a validation-harness defect: identical tangent/binormal warnings copied through multiple CI logs were counted repeatedly as separate debt. The guard now counts unique mesh/package identities and prints those identities. This does **not** waive real asset debt; it makes the next repair target exact instead of occurrence-inflated. The remaining world-package identities will be repaired from the next rerun.

No rendered/PIE visual acceptance, FPS claim or Production 100 promotion is made from this machine evidence.

## 2026-09-20 — MSVC execution blocker

Runs 35500465321 and 35500597711 failed with MSVC D8050 (`failed to get command line into debug records`) across compilation actions, also on single-process retry. This has not yet tested the new disk-audit C++ code. The workflow now prepares a writable per-run TEMP/TMP and probes one-line C++ compilation with plain, /Z7 and /Zi settings before invoking UnrealBuildTool. These are job-local changes only; compiler failures remain failures and no debug verification is disabled.

## 2026-09-20 — state fixture correction after eight chapter passes

Run 35500242164 passed startup and all eight chapter audits. The state audit exposed an outdated test fixture: `StartExperience` correctly restores stored route progress, so calling it on the initial Frodo route did not advance to P1C03; the fixture also bypassed the activity reward entry point. The audit now explicitly starts P1C03, verifies the closed activity window rejects reward, opens `MidgewaterRoad`, verifies direct reward bypass is rejected, then completes the activity through its guarded API and verifies duplicate reward rejection. Required expected reward values remain unchanged. This fixes the test setup without weakening production story/reward guards. Full rerun remains required.

## 2026-09-20 — close the disk persistence evidence gap

The Python resolver repair passed on Windows and startup succeeded on `15e9d2228f6e7e5ceb1e8aed2aab8b698dba4cb8` ([run 35500242164](https://github.com/4youbabee-tech/fellowship-personal-game/actions/runs/35500242164)). Chapter/state checks were still running when this update was written.

Source audit confirmed the existing route/state test did not write a save file. The new `disk-save-roundtrip` audit calls the production player snapshot/restore path, writes a unique CI save slot, mutates live quest/progression/knowledge/player values, loads from disk, verifies restored fields, and deletes only its own temporary slot. It checks health/stamina/resolve/supplies, transform, route/chapter/episode/character, quest stages, story beats, discoveries, progression and Chronicle/map knowledge. It is not yet full NPC-memory or cross-process migration coverage. The observer requires the disk marker for state success. CI runs cannot overwrite or load the owner's manual/checkpoint slots. Thirteen observer tests pass locally; real UE compilation and disk execution of this change remain pending.

## 2026-09-20 — exact-head runtime validation repair

Authority: `Data/ProjectGovernor.json`, including `session_handoff`.

On `b0a4d2614e5744d8a0fa3b1c373c23a491274955`, Pre-Unreal #446 passed. Unreal run [35499375838](https://github.com/4youbabee-tech/fellowship-personal-game/actions/runs/35499375838) built UE4.27.2 C++ and imported production assets successfully. Runtime audits did **not** execute: Python discovery selected a Microsoft Store alias and exited 61.

The repair validates local interpreter candidates, excludes WindowsApps aliases, checks installed/launcher/toolcache/UE-bundled interpreters, and supports Python 3.7 in the observer. It neither installs software nor modifies Windows settings. State audit now has a separate log from startup. Twelve observer regression tests pass locally; Windows execution and full runtime proof remain pending the new CI run.

Next: complete exact-head startup, all eight chapters and actual save/load proof; only then resume visible production. No new visual, performance or gameplay acceptance is claimed.

## PHYSICAL SIDE-ACTIVITY GAMEPLAY WAVE — 2026-09-20

B1 now includes reusable physical challenge gameplay instead of relying entirely on proximity discovery triggers. `AShireTraversalChallenge` implements an ordered three-gate route, verifies opening/closing story beats, awards only the linked first-time Journey Discovery, and therefore feeds the existing Chronicle/map/progression systems without changing FILM_CORE.

The Shire field race now uses the ordered route and completes `Side_SharedShireMemory` only after the route. Moria's `MORIA_ECHO_ROUTE` now uses the same mechanic for Follow the Echo before MoriaUnease closes the optional window. PG-081 guards both runtime placements.

This is implementation evidence; exact-head UE4.27 compile, runtime placement and PIE pacing remain required.

## CHRONICLE + MAP KNOWLEDGE + SIDE-ACTIVITY PROGRESSION MEGA-SLICE — 2026-09-20

B1 expanded again from plan-only into persistent runtime. First-time Journey Discoveries now create main-film Chronicle entries and mark the current route/chapter as known map knowledge. Both collections persist through save schema v6. Book Chronicles remain explicitly separate and are not inserted into this main-film runtime registry.

The C key now opens a Chronicle & Journey HUD panel showing recent Chronicle entries, known regions, Journey Insight and all seven progression tracks/ranks. Contextual side activities are also parsed at runtime: when a linked first-time discovery completes, its authored activity type adds bounded XP (for example CAMP_PREPARATION -> CAMPCRAFT, TRACKING/OBSERVATION -> PERCEPTION, SOCIAL_MEMORY -> FELLOWSHIP). Anti-farm behavior remains first-time-only.

State automation now requires `ShireStateAudit: knowledge-core=PASS`, and PG-080 checks save/UI/input/continuity/side-activity wiring. Exact-head UE4.27 compile/import/startup/state evidence remains required before engine validation is claimed.

## PLAYER-LIFE + PROGRESSION RUNTIME MEGA-SLICE — 2026-09-20

B1 modern-game work is now runtime, not only planning. The player has lightweight Stamina, Ring-pressure-sensitive Resolve and capped travel Supplies alongside Health. Sprinting drains/rebuilds Stamina; damage and Ring pressure affect Resolve; R consumes one supply only when recovery is useful. No hunger/thirst timers, gear score or random rarity loop was introduced.

Seven persistent progression tracks now exist: WAYFINDING, PERCEPTION, QUIET_STEP, CAMPCRAFT, FELLOWSHIP, LORE and RESOLVE. First-time Journey Discoveries award track XP by category, so repeated discovery cannot farm progression. Fellowship Bond is derived from the FELLOWSHIP track. Save schema v5 persists life state and ProgressionXP.

PG-079 guards the full contract and state-mode automation requires `ShireStateAudit: progression-core=PASS`. Exact-head UE4.27 compile/import/startup/state proof is still required before this becomes engine-validated.

## MASTER EXECUTION CONTROL — 2026-09-20

The growing request set is now consolidated into `Data/MasterExecutionRoadmap.json` and the human board `Docs/MASTER_EXECUTION_BOARD.md`. The roadmap is subordinate to the Governor and maps every unfinished requirement plus every ACTIVE work item into large dependency-ordered production bundles. PG-078 makes orphan accepted work a static-validation failure.

Execution order is now explicit: exact-head stability; Part I story/gameplay completeness; production characters/world; living-world/presentation; acceptance/merge; then source-verified Part II/III. Active work items have unique execution ranks/bundle labels so the project no longer behaves like a flat unordered list.

## FILM SIDE-CONTENT MASTER AUDIT — 2026-09-20

The owner supplied a programmer proposal covering trilogy-wide side play and asked for one reconciled, future-proof request set. `Data/FilmSideContentMasterPlan.json` is now the side-content master taxonomy: FILM_MOMENT = verified film action turned into gameplay; FILM_EXPANDED = small plausible play around an existing film scene/place; CHRONICLE = book-only/history/past-character content kept visibly separate from Film Main Canon.

The audit also records continuity corrections: Fellowship does not literally begin at the birthday party; Weathertop fire cannot prevent the Nazgul attack; Prancing Pony attention cannot avoid the Ring incident; Moria's door is a guided canonical puzzle; Entmoot side play cannot replace the film decision causality; Oliphaunt observation does not grant a canon-breaking future weakness; Return of the King's beacon prototype centers on Pippin lighting the Minas Tirith beacon; Glorfindel/Scouring stay Chronicle-only.

PG-077 guards taxonomy/canon separation. Runtime rollout remains behind the current exact-head UE4.27 validation gate.

## SIDE-CONTENT CANON AUDIT — programmer proposal reconciled

The programmer's trilogy proposal is retained but normalized into four continuity classes: FILM_CORE, FILM_EXPANDED, FILM_INTERSTITIAL and BOOK_CHRONICLE, with source-verification tracked separately. The audit corrects one important opening claim: Fellowship does not begin at Bilbo's party; the prologue and Bilbo/Frodo-Gandalf opening precede it.

Part I and Part II entries are now source-audited against the supplied screenplays/project canon where available. Part III remains FUTURE_SOURCE_CHECK at scene level. Book-only Tom Bombadil/Barrow-downs, Glorfindel-at-the-Ford and Scouring content is explicitly isolated from main film continuity. PG-077 protects this separation.

## ENSEMBLE FILM MISSIONS — 2026-09-20

Frodo remains the Ring-quest center, but the film itself now decides who should be playable for each event. `Data/EnsembleFilmMissionPlan.json` maps Gandalf, Arwen, Aragorn, Boromir, Legolas, Gimli and later Merry/Pippin/Sam/Faramir/Eowyn opportunities. The design rule is film action first, character-specialty gameplay second, small original gap-fill last.

Part III mission details remain source-check-only until exact film/script verification. PG-076 guards the ensemble contract.

## ENSEMBLE FILM-MISSION RULE — 2026-09-20

The owner clarified that the film itself already supplies many mission opportunities outside Frodo. Frodo remains the Ring-quest center but is no longer treated as the default controller for every event. `Data/EnsembleFilmMissionPlan.json` now prioritizes playable film actions for Gandalf, Arwen, Aragorn, Boromir, Legolas, Gimli, Merry/Pippin and later-film characters, then allows only small source-safe gap-fill around those verified scenes.

Part I now explicitly identifies Gandalf Ring investigation/Isengard, Arwen at the Ford, Boromir training and Amon Hen defense, Legolas scouting, Gimli/Moria cultural gameplay and Aragorn scouting/leadership as viewpoint opportunities. Part II maps the Three Hunters, Merry/Pippin/Fangorn, Gandalf/Rohan and source-checked Faramir/Eowyn focused episodes. Part III remains FUTURE_SOURCE_CHECK at mission-detail level until exact film/script verification is available.

PG-076 protects viewpoint/source/canon rules. This is a production/design contract; runtime mission handoffs and character-specific mechanics remain pending implementation and UE4.27 proof.

## MODERN GAME LAYER LOCKED — 2026-09-20

The owner explicitly requested a broad modern-game research pass and adoption of fitting game systems throughout the film-based experience. `Data/ModernGameLayerPlan.json` now locks the rule: mandatory Peter Jackson film anchors stay fixed, while optional play may expand only inside story-safe gaps.

The plan adapts modern design patterns - meaningful exploration rewards, short world events, semi-open chapter hubs, companion dialogue during free play, earned map knowledge, environmental/traversal puzzles and reactive inhabitants - into original Middle-earth gameplay. Character life is also defined beyond a health bar through bounded Stamina, Resolve, Fellowship Bond and Supplies, with progression in Wayfinding, Perception, Quiet Step, Campcraft, Fellowship, Lore and Resolve. Survival micromanagement, gear-score grind, loot spam and canon-changing upgrades are explicitly excluded.

P1C01-P1C08 plus P1G01 now each have chapter-specific optional activity families while fixed film outcomes remain mandatory. PG-075 guards this contract. Runtime rollout remains staged and exact-head UE4.27 evidence is still required before any implementation is called validated.

## JOURNEY DISCOVERY RUNTIME MEGA-SLICE — 2026-09-20

Journey Discovery has moved beyond a static design contract. The existing quest subsystem now owns a data-driven first-time discovery registry loaded from `Data/JourneyDiscoveryRewardPlan.json`; all 26 current Part I discoveries are wired into Shire, Bree, P1C03-P1C08 and Isengard world triggers with explicit opening/closing story-beat windows. Rewards derive Journey Insight, region-completion bonuses and milestones without changing required story state.

Discovery IDs/Insight/milestones now persist through the existing save/load path with sanitation on restore. A dedicated HUD discovery card presents the first-time reward separately from combat/error alerts. State-mode automation also requires `ShireStateAudit: discovery-core=PASS`, proving a discovery cannot be farmed by repeat activation and survives the Frodo/Gandalf/Frodo route roundtrip in subsystem state.

This remains implementation evidence until the exact current PR head passes real UE4.27 compile/import/startup/chapter/state validation.

## MEGA-PASS RED-TO-GREEN REPAIR — current exact head

Intermediate head `5699ef0` passed Pre-Unreal Validation #348. The previous Unreal engine attempt reached real compilation and exposed a UE4.27-specific incompatibility in the new non-destructive production importer: `IFileManager::CopyDirectoryTree` is not available there. The importer now keeps the same safety design but uses UE4.27-compatible `IPlatformFile::CopyDirectoryTree`.

The current exact head is intentionally still pending validation. No merge, compile-success, import-success or visual acceptance is claimed until the new head completes the full gate.

## MEGA PRODUCTION BATCH — RING / CHARACTERS / CINEMATIC WORLD — 2026-09-20

The owner closed Unreal and ordered immediate large-scale continuation. This batch turns three previously discussed directions into durable production contracts. The One Ring is now a CRITICAL systemic axis with a runtime bearer/state/pressure API and a headless route-roundtrip audit requirement. The full Part I named cast is now tracked through a model → material → rig → skin → animation → UE4 → LOD pipeline with provenance rules and a custom-character fallback. Every active Part I region now has a cinematic hero-vista and layered foreground/midground/background target based on the owner's dense forest reference.

New production authorities: `Data/TrilogyRingQuestPlan.json`, `Data/CharacterProductionMatrix.json`, `Data/CinematicWorldProductionMatrix.json`, and `Data/OwnerSourceReferenceIndex.json`. Static guards PG-070 through PG-073 protect the new contracts.

Proof boundary remains strict: these are source/data/runtime implementation changes. They are not yet UE4.27-validated or visually accepted until the exact PR head passes Pre-Unreal and real engine validation.

## WORLD BEAUTY BAR RAISED — 2026-09-20

The owner rejected the earlier plain reference-image quality as the final target. The project now explicitly targets a more beautiful cinematic world: layered vistas, richer terrain/materials/vegetation, stronger water/fog/light atmosphere, hero landmark composition and region-specific visual identity. This does not relax the target-device budget; the visual strategy is selective hero detail plus LOD/instancing/culling so 720p Low-Medium / 30 FPS remains the floor target.

## CONTEXTUAL SIDE-PLAY CONTRACT — film story stays fixed, game expands between scenes

The owner reaffirmed the core rule: this remains the Peter Jackson film story. Original side content is allowed only as plausible off-camera gap-fill inside the same time, location, companions, knowledge and emotional/danger context. `Data/ContextualSideActivityPlan.json` now defines 18 optional mini-game/social/exploration activities across FrodoMain P1C01-P1C08 plus GandalfParallel P1C01.

Examples include Shire party errands and a friendship race, Bree observation/tracking, Strider trail-reading, Rivendell map/memory moments, Fellowship camp practice, West Gate stone observation, Moria echo navigation, Lothlorien grief/boat preparation, Anduin river reading, Amon Hen tension observation and Orthanc prisoner observation. Every activity is bounded between exact film story anchors, forbids future knowledge, cannot advance a required anchor, and yields only the existing Journey Discovery/Chronicle/dialogue-memory rewards.

PG-063 now guards those constraints statically. Runtime side-activity triggers, save/UI wiring and UE4.27 play validation remain pending; the exact-head merge gate is unchanged.

## JOURNEY DISCOVERY SYSTEM — exploration now has persistent game rewards

The owner requested the satisfying feeling of discovering a place and receiving a bonus, similar in spirit to exploration RPGs, but adapted to this world's tone. `Data/JourneyDiscoveryRewardPlan.json` now maps 26 declared optional discoveries to first-time Journey Insight rewards. Rewards prioritize Chronicle entries, map memory, lore/dialogue topics, companion memories and local hazard knowledge rather than generic combat-stat inflation.

Four thematic tracks keep the system in-world: Road Wisdom, Peoples and Places, Fellowship Bonds and Peril Sense. Every active Part I exploration route/chapter also has a region-completion bonus. Milestones unlock subtle navigation/content benefits, never story skips or alternate canon outcomes. PG-062 enforces one-time rewards, complete discovery coverage, no canon mutation and packaging.

Runtime trigger/save/HUD/Chronicle wiring is still pending; this commit is a static/game-design contract while Unreal remains busy. Full acceptance still requires UE4.27 and save/load automation on the exact final head.

## PARALLEL NON-UNREAL MEGA-PASS — shader-compile time used productively

While the target machine is busy compiling shaders, CP56 continues with work that does not require interrupting the editor. `Data/ExplorationEnvelopePlan.json` now defines safe free-roam windows, optional discoveries and return-to-main-story behavior for FrodoMain P1C01-P1C08 plus GandalfParallel P1C01. PG-060 checks that optional exploration cannot reorder, advance or replace mandatory film-story anchors.

The source-grounded original dialogue bank has also expanded from 26 to 53 validated variants across Shire, Bree, wilderness, Rivendell, Fellowship travel, Moria, Lothlorien, Amon Hen and Isengard. PG-061 locks in the production-import hygiene fix: OBJ normalization/import must operate on an ignored `Saved/` working copy rather than dirtying tracked `SourceAssets`.

This is productive parallel work, not a merge bypass. The final PR #53 exact head still must pass Pre-Unreal plus UE4.27 compile/import/startup/chapter/state/warning validation before integration into `develop`.

## CP56 SOURCE-GROUNDED LIVING DIALOGUE MEGA-PASS - 2026-09-19

The owner-supplied Fellowship and Two Towers screenplay PDFs are now durable story/dialogue reference sources. `Data/FilmDialogueSourceContext.json` stores only derived context: source identity/hash, scene windows, route/chapter/story-beat progression, tone, safe topics and future-knowledge blocks. Runtime dialogue remains original and offline; raw screenplay passages are not shipped.

Part I contexts cover P1C01-P1C08 plus Gandalf's Isengard route. The Two Towers source is indexed into future Part II arc seeds for Frodo/Sam/Gollum, the Rohan hunters, Merry/Pippin/Ents, Gandalf/Rohan and Saruman/Isengard, without claiming Part II runtime completion.

PR #53 still requires exact-head Pre-Unreal and UE4.27 validation before merge.

## CP56 MEGA INTEGRATION ACTIVE — whole-game coherence pass

PR #53 is the single continuation path above PR #52. The mega batch is tracked by `REQ-MEGA-001`, `WORK-MEGA-001`, `Data/CP56MegaIntegrationPlan.json` and `Data/GameCompletenessMatrix.json`.

Current runtime expansion now reaches named-character behavior, not just data: companion spacing and catch-up respond to regional pressure, named profiles expose a personality-aware emotional state, free interactions choose mood-aware intents with deterministic greeting fallback, and authored regional dialogue covers Shire peace, Bree suspicion, pursued wilderness, Rivendell refuge, Fellowship pressure, Moria dread, Lothlorien grief/refuge, Anduin fracture and Isengard corruption. All shipped logic remains offline and subordinate to story, knowledge and memory gates.

This does not claim final rigs, voice, materials, device performance, cinematic acceptance or trilogy completion. The merge gate is unchanged: the current PR #53 head must pass Pre-Unreal plus the complete UE4.27 compile/import/startup/chapter/warning chain before develop integration.

## CP56 continuation — contextual companion dialogue, 2026-09-19

Recovered prior-session stopping point: CP56 head 3705fe4, PR52 awaiting Unreal. Its latest engine attempt failed during checkout, before compilation. Follow-up PR53 now includes the tracked-source checkout fix plus a correction to regional dialogue selection and 30 original Moria/Lothlorien companion lines. Actual engine build and gameplay validation remain pending. No new checkpoint or trilogy completion is declared.

## Automation-first delivery follow-up — 2026-09-19

REQ-QA-001 records the owner request to reduce manual technical testing. Runtime boot observation and subprocess regression tests are implemented on a follow-up branch based on CP56; Windows UE validation remains pending. See `Docs/AUTOMATION_FIRST_DELIVERY.md` for the trilogy/opening/side-exploration contract and ordered engine-test work. This adds no completed gameplay chapter and grants no new visual, performance or owner sign-off. Existing CP56 requirements remain active.

## CP56 ACTIVE — FELLOWSHIP EXPERIENCE MEGA-PASS

CP55 was merged after Pre-Unreal #273 and Unreal Build Validation #108 passed on the validated branch head. CP56 now expands moment-to-moment play while preserving the same Part I film chronology.

What CP56 changes now:
- P1C01 adds visible pre-adventure Shire friendship/play: Green Dragon revelry, party-field mischief, a shared-memory race/play beat, extra party revelers and play runners.
- P1C02 adds denser Prancing Pony/common-room life.
- P1C03 adds optional road companionship before Weathertop tension.
- P1C05 strengthens camp companionship around the Fellowship training stop.
- P1C06 adds a dead-city discovery beat without adding civilians/fauna to Moria.
- P1C07 adds a shared-grief clearing before Lothlorien story pressure.
- P1C08 adds a river-camp tension beat before the Fellowship fractures.
- `Data/FellowshipExperienceMegaPassCP56.json` and PG-058 preserve the film-spine/non-blocking contract.

Story rule remains unchanged: required film outcomes are fixed; optional friendship, exploration and local-life content fills the spaces between them. Dialogue remains original game writing rather than screenplay reproduction.

This is implementation-in-progress and still requires its own Pre-Unreal and real UE4.27 build/import/startup/chapter regression pass before merge.

## POST-VERIFICATION RESUME — CP55 OPENED

### CP55 activity/movement implementation

CP55 now adds a bounded visible world-life layer on top of the existing LivingWorldDirector:
- project-owned low-poly bird, rabbit and butterfly production meshes,
- distinct flight / hop-rest / flutter motion,
- chapter-aware fauna selection through disposable micro-events,
- no quest/save ownership and no persistent fauna transforms,
- Moria remains dead-city/fauna-empty by design,
- PG-055 guards the new plan/assets/runtime wiring.

Proof boundary: implemented in source/data/assets, but CP55 itself still requires its new Pre-Unreal and real UE4.27.2 compile/import/runtime regression pass before it is called validated.


The post-CP54 current-head verification freeze is now closed by explicit project-owner confirmation.

Verified merged baseline:
- `develop@f7c2b081e7b064fcf27bb4c80124b21f351331ab`
- Pre-Unreal Validation #264: SUCCESS.
- Unreal Build Validation #99: SUCCESS.
- UE4.27.2 build/import: SUCCESS.
- playable startup smoke: SUCCESS.
- headless P1C01-P1C08 chapter audit: SUCCESS.
- runtime warning-debt guard: SUCCESS.
- human verification/check/fix pass: owner-confirmed complete on 2026-09-19.

The owner sign-off is recorded in `Docs/PIE_VERIFICATION_SIGNOFF_2026-09-19.md` and `Data/PIEVerificationEvidence.json`. Numeric FPS/hitch/memory values that were not supplied are intentionally not fabricated.

Current development mode is restored to visible production/expansion. CP55 resumes environmental activity/movement and world-life depth while preserving story/save/route integrity, the 720p Low-Medium target, and the existing CI/UE4 regression gates.

## VERIFICATION MEGA-PASS — PR #45

The verification branch now has a successful real UE4.27.2 machine pass across all eight Part I runtime chapter boots.

Evidence on PR #45 before the hard-gate follow-up commit:
- Pre-Unreal Validation: SUCCESS.
- UE4.27.2 C++ build: SUCCESS.
- Production asset import: SUCCESS (307 imported files, 0 import failures).
- Headless playable startup: SUCCESS.
- Headless chapter audit: P1C01, P1C02, P1C03, P1C04, P1C05, P1C06, P1C07 and P1C08 all loaded their expected runtime builder plus living-world/weather context without a fatal/assert/ensure blocker.

This is a major machine-verification improvement, but it is deliberately **not** recorded as PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED.

The same verification batch now adds executable freeze enforcement (PG-056), structured human PIE evidence enforcement (PG-057), and a fast production-source asset-quality audit. This allows repair/verification work to continue quickly while CI rejects new checkpoint/content expansion during the freeze.

## IMMEDIATE FREEZE — current-head PIE/device verification

**Content baseline:** CP54 at `ed235ff4fb332660d2af8ce1385d9ca038a6337b`. **Develop head entering PR #45:** `043476f4353a44c1d08bf60ab87af5c3e10543f2`. Manual PIE evidence must always record the exact tested post-merge commit.

**CI evidence already green:** PR #44 Pre-Unreal #240 and Unreal Build Validation #75. This proves static validation, real UE4.27 compile/import and headless startup for the PR head. It does **not** prove current-head PIE traversal, visual quality, NPC behavior in play, save/load round trips, or target-laptop performance.

**Current rule:** no CP55 and no new feature/content batch until the existing CP24-CP54 body of work is inspected in real UE4.27 PIE on the target laptop, chapter by chapter.

Order:
1. P1C01 Shire
2. P1C02 Bree
3. P1C03 Weathertop/Ford
4. P1C04 Rivendell
5. P1C05 Road/Caradhras/West Gate
6. P1C06 Moria
7. P1C07 Lothlorien
8. P1C08 Anduin/Amon Hen

For each chapter record: WORKING / INTERMITTENT / BROKEN / CRASH, FPS/hitch/memory observations, NPC routines, ambient NPC-to-NPC conversations, named-NPC memory/context where applicable, and actual atmosphere/weather behavior.

Important implementation truth before testing:
- CP36 is ambient resident micro-life/props/gestures.
- CP38 is ambient NPC-to-NPC conversation.
- CP39 is the named-NPC memory **foundation**; memory-aware bounded dialogue was completed later in CP44.
- CP49 is the LivingWorldDirector/micro-event runtime.
- CP51 provides chapter-specific sun/skylight/fog profiles; final rain/snow VFX are still listed as open.
- CP53 adds continuous regional baseline populations.
- A true day/night cycle is not currently proven by the repository and must not be marked working unless observed/implemented.

Formal rights-holder outreach is deferred. Future asset effort, after the baseline audit, should go to visible quality and performance-safe materials rather than outreach.

Ideas discovered during this freeze belong in `Docs/WORLD_DETAIL_LEDGER.md`; do not implement them until the current baseline audit is complete.

## Current bulk-resource status — CP54

The repository now contains a much larger project-owned production bank instead of waiting for external acquisition. CP54 adds 75 new regional/common OBJ meshes, 17 procedural BMP textures, regional MTL palettes and runtime placement across all P1C01-P1C08 world builders.

Machine-readable authority:
- `Data/WorldResourceBankCP54.json`

Validation boundary:
- source bank: implemented on `mega/activity-movement-v1`,
- PG-054: pending CI,
- UE4.27 compile/import: pending CI,
- headless startup: pending CI,
- PIE/device visual and performance acceptance: pending.

## Current mass-content production status — CP50

The project is now in a comprehensive visible-content phase. Backend foundations remain implemented; active work is world density, materials, character animation production, interiors, lighting and audio.

CP50 adds a reusable common environment kit plus deterministic regional dressing across P1C03-P1C08. The intent is to move the game away from landmark-only prototypes and toward continuous readable environments without changing story topology.

Machine-readable visual-density authority:
- `Data/WorldDressingPlan.json`

Current proof boundary:
- source/runtime integration: implemented on the CP50 branch,
- Pre-Unreal / UE4.27 build-import: pending for CP50,
- PIE/device visual acceptance: pending.


## Current character-motion and atmosphere status — CP51

CP51 is the next visible-production layer after CP50. The runtime now has a safe skeletal-rig handoff contract for named characters plus richer procedural fallback motion, and P1C03-P1C08 have distinct bounded sun/sky/fog profiles.

Machine-readable authorities:
- `Data/CharacterMotionPlan.json`
- `Data/ChapterAtmospherePlan.json`

Current proof boundary:
- source/runtime integration: implemented on `mega/atmosphere-character-motion-v1`,
- Pre-Unreal validation: pending on the CP51 branch until CI completes,
- UE4.27 compile/import: pending,
- PIE/device visual acceptance: pending.

## Current mass-integration status — CP52

CP52 is intentionally larger than the previous incremental passes. The playable runtime now reuses the shared production resource family across the Shire, Bree and P1C03-P1C08, and the build rules explicitly package the living-world/production data needed outside the editor.

Machine-readable authority:
- `Data/ResourceIntegrationPlan.json`

Playable startup remains:
- route: `FrodoMain`,
- chapter: `P1C01`,
- first quest: `ShireArrival`,
- runtime world: `AChapterWorldRouter`,
- ambient runtime: `ALivingWorldDirector`.

External-resource truth boundary:
- the sourcing pipeline supports approved/licensed resources,
- `Data/ExternalAssetManifest.json` currently contains zero approved asset records,
- CP52 therefore uses all currently available project-owned production resources and does not fabricate external approvals.

Current proof boundary:
- source/runtime integration: implemented on `mega/resource-saturation-playable-v1`,
- Pre-Unreal PG-052: pending CI,
- real UE4.27 compile/import: now triggered on the CP52 pull request,
- headless playable boot smoke: now part of Unreal Build Validation and requires GameMode + P1C01/FrodoMain markers,
- PIE/device playability and performance: pending.
- runner autostart: post-reboot verification trigger issued on 2026-09-19.

## Current world-life status — CP53

The game has moved beyond isolated ambient encounters. CP53 keeps a chapter-specific baseline population alive around the player and layers denser micro-events on top of it, while reusing the existing schedule/social/awareness runtime and distance-based tick throttling.

Population targets:
- P1C01 Shire: 18
- P1C02 Bree: 16
- P1C03 Weathertop/Ford: 5
- P1C04 Rivendell: 12
- P1C05 Caradhras/road: 6
- P1C06 Moria: 0 civilians
- P1C07 Lothlorien: 10
- P1C08 Anduin/Amon Hen: 6

Machine-readable authority:
- `Data/WorldLifeSaturationPlan.json`

Current proof boundary:
- source/runtime integration: implemented on `mega/world-alive-saturation-v2`,
- Pre-Unreal PG-053: pending CI,
- real UE4.27 compile/import: pending CI,
- headless startup: pending CI,
- PIE/device crowd density and FPS acceptance: pending.
- resource flood: 15 new project-owned low-poly meshes are now source-controlled and runtime-wired across P1C01-P1C08.

# CURRENT PROJECT STATE

> **Operational recovery note — reconciled 2026-09-19**
>
> Current production baseline now includes CP44 backend completion, CP45 named-cast dedicated modular identities, CP46 threat production art, CP47 licensed asset sourcing, CP48 Weta/rights-holder/global resource mapping, and CP49 living-world/terrain engineering on its validation branch.
>
> The authoritative requirement/decision source is `Data/ProjectGovernor.json`. The machine-readable execution/dependency map is `Data/ProductionExecutionGraph.json`. Use `Docs/ENGINEERING_EXECUTION_PATH.md` for the human-readable implementation order.
>
> Older historical sections below are retained as evidence and may mention earlier heads/checkpoints. They must not be read as the latest status when they conflict with the Governor or this recovery note.


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

## Active visible-gameplay work: CP31-CP32 characters

The project has moved from governance-only preparation into visible character/gameplay production.

Current character state:
- Frodo and Gandalf have dedicated imported modular production meshes and the CP31 production-aware motion pass.
- Sam, Merry, Pippin and Bilbo use the imported Hobbit production archetype with character-specific color/proportion treatment.
- Aragorn/Strider, Boromir, Legolas, Gimli, Arwen, Elrond, Haldir, Galadriel, Saruman and other non-Hobbit named cast are runtime-present distinct procedural proxies; these are **not** final character art.
- `Data/CharacterPopulationPlan.json` is the implementation map for required cast presence by Part I chapter/route.
- Bree, Rivendell and Lothlorien now carry region-aware moving ambient populations rather than one Hobbit silhouette everywhere.

Next character-production work after compile/PIE proof is dedicated visual asset/rigging production in the order recorded by the population plan.

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


