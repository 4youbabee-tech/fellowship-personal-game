## 2026-09-26 - Mega-production source/asset preparation registered

- The next runtime world-detail order remains C3 -> C4 -> D for P1C01.
- A parallel preparation lane is now authorized for cleared Project Source assets covering characters/animation, architecture/interiors, audio/foley, VFX/sky/weather and later-region packets.
- This preparation lane does not change quest/save/story state, LivingWorld ownership, foliage density or later-region runtime availability.
- External assets remain separated by evidence state: SOURCE_REGISTERED -> CANDIDATE -> STAGED -> READY_FOR_IMPORT -> IMPORTED -> INTEGRATED -> ACCEPTED.
- Animated production assets remain FBX-only. Production textures remain PNG/TGA, preferably channel packed.
- Heavy runtime assets must remain soft-referenced and asynchronously loaded; ambient crowds remain pooled; repeated world detail remains HISM/ISM/LOD/cull controlled.
- Gate 6/7 still blocks broad later-region runtime promotion. This entry authorizes preparation, not runtime acceptance.
- No PIE/device/visual/performance acceptance is claimed by this registration.

## 2026-09-26 - C2 closure and C3 stable foliage identity gate

- C2 lightweight foliage wind is merged on `develop@1d0580926299e4fac635bcb847343a49c444d4f1` after exact-head #1030/#837 and merged-develop #1031/#838 machine success.
- C3 is the next runtime world-detail step and is intentionally narrow: only exact normalized material identities `Grass`, `Leaves`, `LeafGreen`, `LeafGold` may move to `M_ProductionFoliage`.
- C3 preserves deterministic material object paths, authored albedo/Color/Roughness/Metallic values, HISM/ISM population ownership, gameplay IDs, quest/save state, LivingWorld ownership and current foliage density.
- Broad `Contains("Leaf")` / `Contains("Grass")` inference is forbidden. Far no-WPO parent assignment remains C4 work backed by actual mesh/LOD/material-slot/cull evidence.
- No PIE/device/visual/performance acceptance is claimed from the machine closure.

## 2026-09-26 - P1C01 C4 and D world-presentation preparation

- C4 preparation now records the evidence required for far foliage treatment: actual mesh object path, material identity, LOD section, cull band, screen-size transition and masked-overdraw observation before a far no-WPO parent can be chosen.
- D preparation now defines the next world-presentation layer after C4: fixed-state Shire lighting, sky fill, bounded fog and low-cost water presentation compatible with UE4.27 / DX11 / 720p Low-Medium.
- D explicitly rejects a free-running day/night cycle, per-frame skylight/reflection recapture and expensive water reflection paths without measured justification.
- Neither preparation changes quest/save/story state, traversal ownership, LivingWorld ownership, material object paths or foliage density.
- Whole-game region packets and Master Resource Bible sourcing continue under DEC-037/038/039. SOURCE_REGISTERED, CANDIDATE, STAGED, READY_FOR_IMPORT, IMPORTED, INTEGRATED and ACCEPTED remain distinct evidence states.
- No rendered, audio, device or performance acceptance is implied by preparation.

## 2026-09-25 - Multi-threaded campaign world-state rule registered

- Post-Amon-Hen world building must track route-specific chapter states and synchronization barriers rather than assuming one global linear timeline.
- Rohan, Ring-bearer, Gondor and late-Rohan world states may prepare in parallel, but shared cinematics and global world-state transitions require source-defined synchronization.
- Explicit chapter-state assets are required for major transformations such as Isengard aftermath/flooding, Helm's Deep damage and Minas Tirith siege states; do not derive these from generic dynamic simulation.

## 2026-09-25 - Whole-game region build coverage registered

- Every canonical playable region is now represented in `Data/WholeGameWorldBuildCoverageV1.json` with a complete cross-discipline build checklist.
- The checklist is deliberately larger than visual art: it includes story-safe interaction windows, traversal, collision/navmesh, streaming/memory, NPC/fauna life, sensory audio, cinematics, localization and acceptance evidence.
- Later-region runtime work remains blocked until the P1C01 Gate 6/7 benchmark; however their asset/source/design packets may advance continuously in parallel.
- New regional details must continue to be logged here before runtime implementation.

## 2026-09-25 - Whole-game source diversity expansion from Master External Resource Bible

- The new 225-source external-resource Bible is adopted as a world-production sourcing map, not a canon source.
- Whole-game world detail may now draw from broader generic/open/licensed material, vegetation, architecture, prop, character-base, animation, VFX, audio, terrain/scanning and authoring-tool lanes while story/location identity remains governed by project canon sources.
- P1C01 remains the first fully assembled benchmark, but warehouse preparation now explicitly covers every region and biome through the nine `BigProductionBuildLaunchV1` waves.
- LOTR/fan/franchise-specific search lanes remain reference/quarantine unless separately cleared; generic sources are preferred for production building blocks.
- Real-world terrain/GIS/scanning sources inform authored fantasy terrain and material creation only; they do not redefine Middle-earth geography.
- New external world-detail assets remain subject to scale/pivot/UV/collision/LOD/material/overdraw/memory review before READY_FOR_IMPORT or integration.

## 2026-09-25 - Global world rule: playable-film safe windows

- Every major chapter/world state must be designed as: **Locked Canon Beat -> Playable Safe Window -> Locked/Bounded Set-Piece -> Persistent World-State Change -> Player Control** where chronology permits.
- Safe windows are where world detail becomes gameplay: interiors, props, NPC routines, fauna, ambient conversations, interaction objects, optional tasks, discovery, weather/audio/foley and local traversal.
- These additions exist to make the player feel physically present inside the film continuity; they must never create a contradictory route, outcome, character presence or chronology.
- Post-beat world state must visibly/sonically communicate what changed before normal exploration resumes.
- This is a whole-game world rule covering every chapter and region from the opening through the final ending. P1C01 Bag End/Shire is only the first benchmark pattern; later chapters/regions must apply the same doctrine with chapter-specific canon constraints.
- New safe-window content must still be recorded in this ledger before runtime implementation.

## 2026-09-25 - P1C01 Warehouse visual/sensory stock expansion

- New Shire-support stock is registered for later art-directed use: pastoral grass/soil/leaf-litter/path breakup, farm outbuilding silhouettes, cave/architecture support kits, multi-surface footsteps, hearth fire, wood/metal interactions and daytime bird ambience.
- These are production-support resources, not new canon claims. Hero Hobbit-hole/Bag End silhouettes and named-character identity still require project-specific art direction and approval.
- Source 11 performance rules remain binding: foliage/material overdraw, texture memory, HISM/LOD/cull cost and audio concurrency are measured before density expansion.
- All external stock must retain provenance/license records and pass format/intake review before READY_FOR_IMPORT. Animated production assets remain FBX-only; production textures remain PNG/TGA.
- Runtime world ownership, quest IDs, save keys, LivingWorld/NPC systems and merged C2 foliage integration are untouched by this preparation lane.

# WORLD DETAIL LEDGER

## 2026-09-25 - W01 P1C01 Drop C1: authored material texture binding

- Source 03 keeps the Shire pastoral/domestic visual grammar; Source 11 makes foliage overdraw/material complexity/texture memory explicit review gates.
- Existing project source already contains Shire TGA textures and MTL `map_Kd` references, but the importer previously synthesized only Color/Roughness/Metallic and did not bind the authored textures.
- C1 now binds `map_Kd` to an `AlbedoTexture` parameter after texture import and changes the generated `M_ProductionSurface` BaseColor to `AlbedoTexture * Color`.
- This is an editor production-import change only. Quest/state/AI/LivingWorld/audio/streaming/runtime asset ownership is untouched.
- C2 wind/WPO remains gated behind C1 exact-head engine proof.
- Evidence boundary: STATIC-VALIDATED only.

## 2026-09-25 - W01 P1C01 Mega Production Drop B: Hobbiton + Bag End architecture

- **Source basis:** Source 03 requires Shire/Hobbiton pastoral domestic scale, circular doors and gardens; Bag End must read as a dense lived-in Hobbit narrative hub with round geometry and deterministic state variants. Source 07 anchors F1-01 to Shire onboarding/social/birthday setup. Source 11 requires modular reuse, simple collision/visibility cost and measured target-hardware budgets.
- **Canon correction:** Tolkien places The Green Dragon at Bywater. The compact prototype previously displayed it inside the Hobbiton composition. Drop B corrects only player-visible presentation while retaining the legacy `Discover_GreenDragon` internal ID for save compatibility.
- **Implemented:** `SpawnHobbitonArchitecturePass()` adds a Bag End hero garden/property approach, four subordinate domestic garden clusters, a generic Hobbiton village common, Party Field canopy/produce dressing, and lived-in working-edge props. It reuses resident project meshes and adds no synchronous heavy load.
- **Story boundary:** quest/chapter IDs and stable story anchors are unchanged. Architecture is presentation/world-space composition only.
- **Interior boundary:** a dedicated production Bag End interior shell does not exist in the current asset bank; interior completion is explicitly deferred instead of being falsely claimed.
- **Regression guard:** PG-164 requires the architecture pass/log/canon-corrected display copy and rejects a visible Green Dragon-at-Hobbiton regression while preserving the legacy save ID.
- **Evidence boundary:** STATIC-VALIDATED until fresh exact-head Pre-Unreal + UE4.27.2 core validation; no PIE/device/visual acceptance claimed.

## 2026-09-25 - W01 P1C01 Mega Production Drop A: terrain/geography foundation

- **Source basis checked before implementation:** Source 03 defines the Shire/Hobbiton as pastoral hills, lanes, farms and Hobbit-holes with warm domestic scale, readable landmark/vista navigation, sightline/terrain-aware streaming and collision/navmesh/backtracking QA. Source 07 keeps F1-01 in the Shire as an onboarding/social/birthday mission package with deterministic mission-state ownership. Source 09 requires modular reuse, provenance and per-asset validation. Source 10 is visual/modeling aid only. Source 11 remains the systems/performance/audio authority.
- **Runtime scope:** geography only. Quest IDs, story postconditions, named-character canon state and established quest coordinates are not moved by this drop.
- **Implemented:** dedicated HISM geography groups for terraced hills, village slopes and river banks; route-framing placements across Bag End/Hobbiton -> East Fields -> Wooded Road -> Brandywine/Ferry; old repeated CP49 terrain AStaticMeshActor layer removed.
- **Performance:** explicit cull bands now cover grass, flowers, shrubs, distant trees, rocks, path stones and the new geography groups. The broad collision foundation and router grounding contract remain the gameplay safety net.
- **Asset sourcing lane:** existing project-owned Shire/Common meshes are used first. External terrain/material candidates remain item-level reviewed through the existing manifest; ambientCG/Poly Haven are preferred low-friction material/environment sources, with entitled Fab/Megascans, Quaternius and Kenney evaluated where useful. Provider listing never equals item approval.
- **Next dependency:** after this exact head is machine-green, proceed directly to Hobbiton + Bag End architecture. Do not detour into unrelated regions or reopen W00 without a concrete regression.
- **Evidence boundary:** STATIC-VALIDATED at implementation time. Fresh exact-head engine validation and owner PIE/visual review remain required.

## 2026-09-25 - W01 implementation drop 1: single-owner ambient life + budget authority

- **Runtime ownership change implemented:** `ShirePrototypeWorldBuilder` no longer directly spawns `AShireAmbientNPC` crowds. P1C01 ambient population now converges on `ALivingWorldDirector`, which already owns pooling, culling, chapter targets, danger thinning and micro-event/fauna lifecycle. Named/story `AShireNPC` actors remain builder-owned.
- **Budget drift resolved at source:** `LivingWorldEventPlan.json#region_budgets` is now the sole micro-event cap/cadence authority. `WorldLifeSaturationPlan.json` controls baseline population density only, and `ALivingWorldDirector::LoadLifeSaturationContract` no longer overwrites micro-event caps/cadence.
- **P1C01 life preservation:** `PlayRunner` is retained in the director-owned P1C01 role mix. Fauna remains available through the existing living-world event path instead of a second permanent builder-owned bird crowd.
- **Static verification on branch:** zero `SpawnActor<AShireAmbientNPC>` occurrences remain in `ShirePrototypeWorldBuilder.cpp`; the old `ShireAmbientNPC.h` include is removed; the life-saturation loader no longer reads the two micro-event budget fields.
- **Evidence boundary:** STATIC-VALIDATED only. Fresh Pre-Unreal + UE4.27.2 compile/runtime/PIE evidence is still required before calling this W01 code COMPILE-TESTED or PIE-TESTED.

## 2026-09-25 - W01 kickoff: verified sensory/reactive review intake

- W00 repair lane is closed on canonical `develop@809e56a9e1dc4b453e02a0b04b6875a71df21933`. Owner-side P1C01 PIE showed `ShireStartupGrounding: PASS chapter=P1C01 commitBarrier=yes stableSeconds=2.0 ground=yes drop=1.8 drift=0.0`, the player remained on blocking ground, and the owner reported zero same-session Output Log search matches for `Mobility is Static` and `SetStaticMesh`. This is P1C01 startup-grounding/warning-tail PIE evidence only; it is not DEVICE-TESTED, VISUALLY-ACCEPTED or PERFORMANCE-ACCEPTED.
- The owner-forwarded "Sensory & Reactive Layer" review was checked against the live W00-close head before adoption. Useful verified gaps are retained here; stale claims are corrected rather than copied.
- **Accepted gap — spatial environmental audio:** `UShireAudioSubsystem` already performs async audio loading, ambience transitions and music ducking, but the current source has no AudioVolume/attenuation/concurrency/physical-surface footstep layer. Add a P1C01-first spatial ambience/foley layer later in W01 using soft/async assets, bounded concurrency and distance/importance virtualization.
- **Accepted gap — vegetation/material motion:** current source contains no `WorldPositionOffset`, `SimpleGrassWind` or `WindDirectionalSource` implementation. Add performance-scaled foliage/grass motion through shared material-instance parameters, not per-actor Tick. Near/hero vegetation may receive richer motion; distant/repeated detail remains HISM/LOD/culling friendly.
- **Accepted gap — skeletal micro-reaction presentation:** true head/eye Look-At IK and Foot IK are not implemented. They are gated behind production skeletal FBX rigs + Animation Blueprint readiness; do not bolt expensive IK onto static proxy meshes. Use distance/significance LOD so only nearby relevant NPCs evaluate higher-cost presentation.
- **Corrected stale claim — NPC awareness/weather:** `AShireAmbientNPC` already has bounded player observation/turning, deterministic idle head-look variation, distance-throttled Tick, and inclement-weather-aware behavior/dialogue. W01 should deepen presentation, not duplicate those systems.
- **Corrected stale claim — audio architecture:** the audio system is not "silent logic"; it already owns ambience/music/voice routing, async loading, fades and ducking. The missing production layer is richer authored/spatial environmental sound and surface-aware foley.
- **Corrected stale claim — pooling:** `ALivingWorldDirector` already contains an ambient-NPC pool. The actual W01 architectural debt is duplicate direct `AShireAmbientNPC` spawning in `ShirePrototypeWorldBuilder`; ambient population ownership must converge on `LivingWorldDirector` while named/story actors remain separately owned.
- **Verified budget drift:** `LivingWorldEventPlan.json` currently caps 3 active micro-events with a 12 s cadence, while `WorldLifeSaturationPlan.json` declares 5 active micro-events with a 6 s cadence. W01 must establish one runtime authority before density increases.
- **Asset-name correction:** the forwarded review referenced `SM_ShBroadleafTree.obj`, which is not present on the verified head. Current Shire tree sources include `SM_ShTreeCanopy.obj` and `SM_ShTreeTrunk.obj`; `SM_CommonTerracedHill.obj` and the cited Shire TGA textures do exist.
- **Execution order:** (1) centralize ambient ownership/pooling, (2) reconcile living-world budgets, then continue the P1C01 production sequence: terrain/geography -> Hobbiton/Bag End architecture -> materials/vegetation -> lighting/sky/fog/water -> character presentation -> NPC/fauna/environment motion -> quest/audio polish -> target-device profiling. The sensory/reactive items above are folded into those stages rather than opened as a competing feature wave.

## Architectural stabilization directive - 2026-09-22
- Owner explicitly rejects symptom-by-symptom patching before further production expansion.
- Active mode is W00 architectural stabilization: validation is allowed/required; new features and broad content expansion are frozen.
- Grounding is a router/world invariant: bounded nearby-ground probing + walkable-slope rejection + capsule-clearance validation. Chapter-specific RuntimeSpawnFoundation pads are forbidden.
- Chapter CI must attempt P1C01-P1C08 in one sequential sweep and aggregate failures; no first-red early exit.
- Optional/future skeletal rig packages must be preflighted before async load; missing rigs use fallback without engine missing-package errors.
- Source textures are PNG/TGA only; BMP is forbidden. Current 24 BMP sources were migrated to TGA and MTL references updated.
- Duplicate-position OBJ face vertices are a source defect. The seven known affected project-owned meshes were normalized and triangulation-risk faces are now strict audit failures.
- Feature construction resumes only after the exact stabilization head passes static + compile/import + all chapter + state/transition + warning/material gates.

## Precise integration-gap closure - 2026-09-22
- Close discovered cross-system gaps immediately at source level; do not merely record them.
- NPC world-facing context now follows committed visible world identity/revision. During logical/visible mismatch, no new bounded NPC dialogue/film context may start.
- Same-world quest-stage/danger reactions remain live; the committed snapshot is used only across the async mismatch window.
- Completed character-rig streamable handles are released after actor-owned handoff so inactive rigs are not pinned for the full GameInstance lifetime.
- Chapter builders resolve production meshes only from resident async banks. Enemy bank coverage was extended for Black Rider, Moria threats and Amon Hen enemies.
- Player/named-NPC/enemy production proxies use resident-only soft resolution; primitive fallback remains safe until skeletal production rigs become available.
- Production audio no longer performs synchronous USoundBase loading.
- Continuous audit now rejects non-engine synchronous LoadObject and verifies committed-context/rig-handle invariants.
- Defect closure still requires fresh exact-head UE4.27 compile/runtime proof after W00 runner repair.

## Deep organization / cross-system audit - 2026-09-22
- Audit checkpoint exact head: `17689b194ddca281aa9881b9ac50594712a65df6`.
- Management drift found: REQ-CAMERA-001 was accepted into ProjectGovernor but not mapped into MasterExecutionRoadmap, causing Pre-Unreal #685 PG-078 failure. Mapping/snapshot reconciliation is now applied.
- Cross-system simulation: LivingWorldDirector is committed-world synchronized, but ShireNPCContextSubsystem derives regional mood/profile availability/film dialogue directly from QuestSubsystem logical chapter/route. Register a committed-world context bridge before scaling NPC intelligence.
- Character rig streaming is async and fallback-safe, but rig handles currently persist for GameInstance lifetime. Measure multi-chapter skeletal residency before full-cast rollout; add bounded inactive-cast release only if safe and needed.
- Ambient NPC pooling exists and disables pooled tick/visibility/collision; previous “pooling missing” audit text was stale.
- Remaining runtime synchronous LoadObject debt is still high in world builders and present in player/named-NPC fallback styling. Migrate incrementally after runner recovery; do not replace one stable loader with a competing manager.
- Public/Private physical source migration remains pending and must stay isolated from gameplay changes.
- Next priority after this audit: W00 runner/Engine Content ACL repair and fresh exact-head validation.

## Final pre-runner warehouse saturation batch - 2026-09-22
- Owner authorized one final source-safe warehouse fill before switching focus to the UE4.27 runner ACL repair.
- Added only verified official KayKit public-GitHub CC0 lanes: Restaurant Bits (food/kitchen/interior support), Halloween Bits (selective cemetery/crypt/dark-region props), and City Builder Bits (manual-filter generic civic props only).
- City Builder stock is explicitly period-filtered: modern-looking items are not eligible for Middle-earth integration merely because the archive is staged.
- These are STAGED candidates only after workflow receipts exist. No READY_FOR_IMPORT / IMPORTED / INTEGRATED / ACCEPTED promotion is implied.
- After this batch, active priority returns to W00 runner/exact-head unlock; broad warehouse sourcing pauses except blocker-safe bookkeeping until the runner gate is repaired.

## Embodied third-person camera direction - 2026-09-22
- Owner explicitly rejects top-down/isometric/RTS-style normal gameplay. Shire Journey must feel like directly inhabiting Middle-earth through the active character.
- Default gameplay perspective: **third-person action-adventure**, camera behind or slightly over the controlled character, broadly comparable to GTA V / Red Dead camera relationship rather than a strategy camera.
- Tune distance/height/FOV/camera collision contextually for Hobbit/Human/Elf/Dwarf scale, interiors, traversal, interaction and combat readability.
- Temporary cinematic framing is allowed only as bounded presentation; control must return cleanly to the embodied gameplay camera.
- Acceptance requires PIE review of world-scale immersion, interaction reach/readability, camera collision and interior/exterior transitions. This direction alone is not PIE/DEVICE/VISUAL acceptance.

## Completion Wave Map / Milestone Ladder - 2026-09-22
- Owner requested a bounded finish map from the current approximately 40/100 whole-game planning position to 100/100, expressed as production waves rather than hours.
- Planning unit is a **major production drop**, not an individual Git commit or raw file upload. One drop should be coherent enough to review, validate and roll back as a unit.
- The completion map uses 12 remaining waves totaling 60 planning percentage points. These percentages are roadmap estimates only; they are not compile/PIE/device/visual acceptance evidence.
- Every wave closes only on its listed exit criteria. Asset-only staging, code-only implementation or a green static gate cannot by itself close a visual/runtime wave.
- Expected repository activity is roughly 30-40 major coherent production drops across the remaining waves; actual Git commits may be higher because fixes/documentation/validation can split a drop.
- Shire/P1C01 remains the first visible benchmark. Part II/III runtime opens only after the relevant gates, while warehouse/preproduction may continue in parallel.

## Character visibility / warehouse-to-runtime bridge - 2026-09-22
- Owner priority: stop letting asset-bank growth remain invisible; keep broad legal/free sourcing active, but turn the first proven humanoid/enemy rig stock into a real import path as soon as engine gates permit.
- Register this before implementation: audit staged character archives for usable FBX/texture inventory, strengthen receipt/hash/license validation, expand only from verified official/public sources, and close the documented FBX/PNG/TGA importer gap without treating static OBJ conversion as rigging.
- Shire remains the first visible benchmark. Part II/III assets stay warehouse/preproduction only; technical enemy-rig QA stock must not be treated as canon population.
- Acceptance boundary: archive presence or a provider README can prove source/package facts only. Skeletal import, skin/deformation, locomotion, runtime replacement, PIE/device performance and visual acceptance each require their own evidence.
- Runtime architecture remains soft/async for heavy character packages and pooled for crowd-scale NPC reuse.


Purpose: retain visual, material, life, ambience and world-detail ideas discovered during the post-CP54 verification cycle and promote them deliberately during resumed production.

## Post-freeze rule
- The post-CP54 verification freeze is complete and CP55+ production is authorized.
- Promote ideas in bounded batches behind Pre-Unreal and real UE4.27 regression gates.
- Preserve story/save/route topology and the target-laptop performance budget.
- Shire remains the visual/readability reference, but region-appropriate differences are encouraged.
- Do not convert an idea into a validated/accepted claim until the corresponding implementation and evidence exist.

## P1C01 — Shire
### Ideas
- Better performance-safe ground material variation.
- Stronger cloth/material identity for market/party props.
- Lighting polish only after actual PIE/FPS baseline is known.
### Verification discoveries
- Post-CP54 verification pass owner-confirmed complete; numeric device measurements were not retained in chat.

## P1C02 — Bree
### Ideas
- Rainy-night material/lighting differentiation.
- Inn/street material quality pass after Shire reference is accepted.
### Verification discoveries
- Post-CP54 verification pass owner-confirmed complete; numeric device measurements were not retained in chat.

## P1C03 — Weathertop/Ford
### Ideas
- Weathered stone/soil material upgrade.
- Verify whether atmosphere reads as distinct without expensive VFX.
### Verification discoveries
- Post-CP54 verification pass owner-confirmed complete; numeric device measurements were not retained in chat.

## P1C04 — Rivendell
### Ideas
- Pale stone, water and foliage material quality pass.
### Verification discoveries
- Post-CP54 verification pass owner-confirmed complete; numeric device measurements were not retained in chat.

## P1C05 — Road/Caradhras/West Gate
### Ideas
- Snow/rock material upgrade and weather presentation after performance baseline.
### Verification discoveries
- Post-CP54 verification pass owner-confirmed complete; numeric device measurements were not retained in chat.

## P1C06 — Moria
### Ideas
- Stone/metal/brazier material polish; preserve civilian-empty design.
### Verification discoveries
- Post-CP54 verification pass owner-confirmed complete; numeric device measurements were not retained in chat.

## P1C07 — Lothlorien
### Ideas
- Golden foliage/wood/material differentiation.
### Verification discoveries
- Post-CP54 verification pass owner-confirmed complete; numeric device measurements were not retained in chat.

## P1C08 — Anduin/Amon Hen
### Ideas
- River/boat/ruin material differentiation.
### Verification discoveries
- Post-CP54 verification pass owner-confirmed complete; numeric device measurements were not retained in chat.

## Cross-region backlog
- True day/night cycle only if target-laptop performance allows it.
- Real rain/snow/weather VFX only after current fixed weather-context behavior is verified.
- Material upgrades should be measured against 720p Low-Medium and the 30 FPS floor target.
- Prefer source quality and runtime efficiency over raw asset count.


## Cross-system QA immune-system idea — 2026-09-21
- Owner-approved external programmer proposal: build a layered automated QA immune system for recurring game-breaking defects.
- Adopt Unreal Automation Framework / FAutomationTestBase as an additional engine-level layer, not a replacement for the existing headless runtime harness.
- First wave: exact-head automation runner, save-schema/default-state contract, chapter streaming package integrity, and strengthened startup-grounding regression.
- Later waves: deterministic authored collision/traversal probes, navigation stuck coordinates, production-rig animation readiness, transition hitch measurement, memory-growth/churn soak, material/shader integrity and exact-SHA reports.
- Corrections: do not use random world locations, universal Z<0, fixed 4 GB/100 ms thresholds, or proxy-NPC T-pose rules as project-wide truth. Use reproducible authored probes and measured target-device budgets.
- No automated layer may promote PIE/device/visual/pacing acceptance by itself.


## Cross-system visual-performance optimization proposal — 2026-09-21
- Owner-approved programmer proposal reviewed against the live UE4.27.2 project.
- Adopt: soft/asynchronous heavy-asset ownership, HISM/ISM for repeated detail, explicit culling, role-appropriate LODs, shared material-instance families, and event/timer/throttled logic over unnecessary Tick.
- Already present: chapter asset banks use FSoftObjectPath + FStreamableManager; WorldDetailCluster uses HISM + cull distances; world builders are non-ticking; DeepProjectAudit rejects LoadObject inside Tick.
- Corrected: do not force World Composition over the working chapter-router architecture; evaluate it only if later authored contiguous sublevels need it.
- Corrected: baked Lightmass is selective for authored static scenes, not a blanket rule for runtime-generated chapter geometry.
- Corrected: Distance Field Shadows are a benchmark candidate, not assumed cheaper on the ~2 GB VRAM target.
- Corrected: Material Instances are preferred, but MIDs are only for runtime variation; LODs are role/budget based rather than blindly mandatory for every tiny asset.
- Machine-readable plan: `Data/VisualPerformanceOptimizationPlan.json`.
- Runtime lighting/world-topology changes wait for startup/QA gate health and target-device profiling.


## Comprehensive foundation convergence — 2026-09-21
- Owner authorized one integration train instead of continued isolated repair/proposal branches.
- Ordered convergence: startup grounding -> automated QA -> visual-performance guardrails -> V10 regional living world -> transactional chapter transition synchronization.
- New features remain gated until this foundation earns exact-head machine proof.
- After merge: ambient pooling, residual synchronous-load burn-down, living-NPC witness/share/learn, character production, and cinematic world-art passes resume in dependency order.


## Cross-system playability audit — 2026-09-22
- Rechecked the owner-forwarded Work review against integration head `170ebd857bece56a6d7f76f4928efe0eb3426af2` before promotion.
- Confirmed: chapter checkpoint capture waits only one player Tick even though chapter world commit is asynchronous; this is not a safe persistence barrier.
- Confirmed: RestoreSaveSnapshot can apply the saved transform after logical chapter restore without first proving the matching world revision is committed.
- Confirmed: failed world-swap rollback rebuilds the prior builder where possible but leaves player movement held and does not restore one coherent prior world/quest/player transaction.
- Confirmed: ambient baseline origins use approximate Z with no ground trace; ambient body meshes have collision disabled, so ground/wall placement needs a bounded trace/placement contract plus rendered observation.
- Confirmed performance debt: living baseline population uses SpawnActor/Destroy rather than pooling, and AShireAmbientNPC visual setup still performs direct LoadObject calls. Do not expand density until pooled reuse and asynchronous asset ownership are designed around the existing chapter-bank system.
- Source organization remains 62 flat runtime .h/.cpp files with zero migrated entries. Preserve DEC-003: Public/Private movement is a separate path-only maintenance pass, not part of the transition repair.
- Asset-count correction: the indexed production inventory reports 24 image files total, not 24 BMP files. Seven explicit Shire BMP paths are currently visible in the inventory; do not state a larger BMP count without repository evidence.
- Priority order: exact-head static gate -> committed-world persistence/rollback repair -> engine gates -> ambient ground/pooling/async-load debt -> later source-layout migration and production expansion.
- Evidence boundary: these are source-confirmed findings and planning records only. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED promotion follows from this audit.


## Character humanization production wave V7 - 2026-09-22
- Owner explicitly prioritized visible, natural, human-readable character quality instead of continuing to look at modular dolls/placeholders.
- This is an extension of REQ-CHAR-001/002/004, not a new chapter or alternate gameplay system.
- Existing character OBJ pieces are retained only as static/prototype fallback. Animated production delivery is FBX-only and must include actual skeleton/skin/deformation work.
- Source basis reviewed before implementation: Character & Relationships Bible, 3D Visual Asset Atlas, CharacterProductionMatrix and CHARACTER_PERFORMANCE_STANDARD.
- First production order: Frodo -> Gandalf -> Sam -> Aragorn -> Gimli/Legolas -> Merry/Pippin/Boromir.
- Runtime direction: central soft/async character-rig residency via FStreamableManager; no final heavy skeletal LoadObject path.
- Import direction: production importer accepts PNG/TGA and a dedicated Characters/Rigs FBX path without changing the legacy static OBJ bank in-place.
- Natural visual acceptance remains separate from source implementation and requires real FBX assets plus UE/PIE/device evidence.


## Cinematic asset-source expansion — 2026-09-22
- Owner forwarded an asset-manager sourcing directive prioritizing a visually full, cinematic private-project warehouse for characters, creatures, weapons, architecture, materials and environments.
- Persisted discovery sources now include DeviantArt 3D/XNALara ports, SFMLab, Open3DLab, Nexus Mods and a separate ArtStation Marketplace path, alongside the already tracked CGTrader, TurboSquid, Sketchfab, Quixel Megascans, Fab and legacy Unreal Marketplace sources.
- Storage in the discovery registry is not automatic production approval. Ripped/ported proprietary film/game assets remain blocked unless explicit reuse rights/provenance are established for the specific item.
- Visual target remains high-fidelity/cinematic; when exact source reuse is not cleared, prefer legally reusable high-quality bases, project-authored reconstruction or commission rather than accepting primitive placeholders.
- Final animated-character intake remains skeletal FBX with genuine rig/skin/deformation; production textures remain PNG/TGA and heavy runtime assets follow soft/asynchronous loading.


## Cinematic audio warehouse directive — 2026-09-22
- Owner forwarded a dedicated audio-engineering directive: the project should sound as intentionally produced as it looks, with region-specific ambience, fauna, foley, creature/combat effects, dynamic music and character voice routed through the existing audio system.
- Registered discovery sources: ElevenLabs, BOOM Library, Pro Sound Effects, LOTR Complete Recordings (reference), Blu-ray center-channel dialogue (reference), and classic EA LOTR audio (reference), in addition to previously tracked licensed/review sources.
- UShireAudioSubsystem already owns logical routing/crossfades/ducking; the missing layer is the authored/approved offline bank itself.
- Real-actor voice cloning, extracted film dialogue, commercial soundtrack recordings and extracted proprietary game audio are not automatically production-approved by private-project intent; authorization/rights remain item-level gates.
- First implementation priority is a dense P1C01 Shire bank, then Bree, Moria, Lothlorien and Anduin/Amon Hen, with 3D attenuation/concurrency and target-laptop profiling.


## Trilogy warehouse-first production directive — 2026-09-22
- Owner changed the production emphasis: the project must no longer treat final characters/world/audio as a late downstream concern. Build and maintain a trilogy-wide asset warehouse in parallel with foundation repair so visible content coverage is never ad hoc or forgotten.
- Warehouse scope is trilogy-wide preproduction/asset readiness, not permission to skip current runtime gates. Runtime integration of new chapters/features remains gated by the existing dependency/validation rules.
- Required stock families include major/supporting named characters, generic NPC/crowd families, enemies, creatures, fauna, culture/faction kits, all major film locations/state variants, architecture, terrain, vegetation, props, materials, weapons/equipment, animation, VFX, audio, cinematics and UI/readability support.
- Source basis for the first master inventory: Source 02 character roster/dossiers; Source 03 location catalog/state variants; Source 04 peoples/cultures/artifacts; Source 05 battles/weapons/creatures; Source 11 source-governance/audio/cinematic rules; supplied trilogy screenplays for supporting-cast/scene demand.
- Warehouse completeness and runtime completeness are separate: an asset slot can be catalogued before a final file exists, but it may not be called READY/APPROVED until the actual asset/provenance/format/compatibility requirements are satisfied.
- Priority is now WAREHOUSE-FIRST + VERTICAL-SLICE: make the stock catalog comprehensive across F1-F3, then aggressively acquire/author usable content while P1C01 remains the first fully assembled visual benchmark.


## Multi-region world-foundation parallel lane — 2026-09-22
- Owner explicitly directed that P1C01 Shire remain the first assembled benchmark but must not monopolize production attention. World foundations for the rest of the trilogy are to be established in parallel as warehouse/preproduction work.
- This lane covers reusable architecture kits, terrain/material families, vegetation/ecology, props, faction/population kits, audio beds, lighting/atmosphere, VFX and traversal/collision requirements for Bree, Weathertop, Rivendell, Caradhras, Moria, Lothlorien, Anduin/Amon Hen, Fangorn, Edoras/Meduseld, Helm's Deep, Isengard, Emyn Muil, Dead Marshes, Ithilien/Henneth Annun, Minas Tirith, Osgiliath, Minas Morgul, Cirith Ungol/Shelob's Lair, Pelennor, Paths of the Dead, Black Gate, Mordor/Gorgoroth, Mount Doom and Grey Havens.
- Runtime chapter implementation for later parts remains gated. The new work is preproduction/warehouse/shared-foundation preparation, not permission to bypass Gate 6/7.
- Shared-kit principle: build culture/material/biome families once and reuse across related locations instead of authoring every city from zero. Examples include Gondor pale-stone/citadel kit, Rohan timber-hall/stable kit, Mordor black-metal/ash/fortification kit, Elven stone/wood/foliage kit, Dwarven monumental-stone kit and Shire/Bree rural timber/plaster kit.
- Performance remains bounded for the target laptop: repeated world detail must prefer ISM/HISM + culling/LOD, high-cost hero architecture stays selective, and world stock may be large on disk without being resident in memory at once.
