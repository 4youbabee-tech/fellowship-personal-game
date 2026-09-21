# WORLD DETAIL LEDGER

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
