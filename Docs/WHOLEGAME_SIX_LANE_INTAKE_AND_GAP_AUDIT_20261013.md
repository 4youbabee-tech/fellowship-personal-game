# Whole-game source intake: six production lanes (2026-10-13)

Authority: Data/ProjectGovernor.json. This packet records candidate discoveries and QC requirements; it neither changes runtime gate status nor claims downloads or imports. Baseline 334 source FBX + 144 source PNG, sourced from owner handoff (not recount independently); 478 total. This packet creates **zero** FBX, PNG, warehouse files, .uassets or in-world actors. Existing source entries must be deduplicated by provider URL, version and SHA256 before any download.

## Lane A: P1C01 chapter closure — FIRST PRIORITY
- Audit Bag End → Hobbiton → Party Field → wooded road → Bucklebury Ferry interactions, path obstacles, collision fallback, save/load near banks, NPC pool reset, quest-story flags and prompt arbitration.
- #435 FerryLanding collision pending actual UE evidence; #437 route audit/branch cleanup pending branch reconciliation. Do not bypass exact-head checks.
- Reuse the P1C01 living-world eight-question audit from PR #439 after it is accepted, keeping owner authority in Governor.

## Lane B: Landscape, ecology and architectural PBR
- Reuse existing Poly Haven inventory first. Identify missing signature families by region: Shire soil/thatch/wood/stone; Bree plaster/cobble; Rivendell rock/foliage; Moria dark stone/metal; Rohan timber/grass; Gondor pale stone; Mordor volcanic rock/ash.
- Official provider https://polyhaven.com ; CC0 source assets. Its live API has separate ToS (see https://github.com/Poly-Haven/Public-API/blob/master/ToS.md): identify the app, comply with limits and never bulk-scrape site.
- Convert to packed PNG/TGA maps appropriate to UE4.27; preserve height/normal semantics, texture dimensions and color-space. Validate channel mapping in material instances after import.

## Lane C: Modular world-kit candidates (PREP ONLY future regions)
- Quaternius Modular Dungeons Pack: https://quaternius.com/packs/modulardungeon.html — official page lists 48 models, FBX/OBJ/Blend, CC0. Take **FBX** derivative path only, verify extracted member license, scale, topology, UV, collision and LOD. Proposed as generic dungeon dressing for Moria/other underground spaces, never a canonical hero landmark.
- Existing Quaternius character/outfit queue is useful only as background rig/retarget starter; not hero fidelity or automatically story-correct architecture.
- Kenney packs can be generic interaction markers/UI/supporting graybox kits after per-pack license and format verification. Do not conflate purchasable All-in-One bundle with free packs or spend without authorization.

## Lane D: Living populations, fauna and animations
- Each biome receives an independently costed ambient catalogue: day/night schedules, danger override, audio, interactability, pool identity reset, LOD/impostor tier, story reveal gate.
- Prefer existing Quaternius CC0 per-pack FBX sources for generic bases; final hero likeness, dialogue and animations require separate approval and skeletal proof.
- Separate far-field events from near-player characters: no high-rate spawning, no per-NPC unconditional tick, no owning second NPC AI subsystem.

## Lane E: World audio and sensory identity
- Before download, separate provider asset provenance and precise per-item audio license. Map each biome to authored wind/water/bird/cloth/footstep/reverb layers, capped voices, quiet zones and story danger overrides.
- Avoid unlicensed Tolkien film score/dialogue. Foley assets from third-party are **UNSOURCED** until license/URL/sha256 and file-by-file examination exist.

## Lane F: Narrative, mission gating and readiness
- For all 28 Governor-approved region packets, create source-only story reveal, mission dependency, environmental change and save migration checklists. Future chapters remain PREPRODUCTION until predecessor Gate 6/7 acceptance.
- Lock spoilers behind authoritative story-state flags, not streaming distance. For any film-core beat verify attached film/script and story timeline before authoring.
- Only one runtime writer for P1C01; no P1C02 activation.

## Intake gate for every physical external asset
1. Verify official provider and item-specific license/permissions, downloadable direct URL, version and file/member identity.
2. Record source URL, source license, original filename and archive member, attribution policy, provenance note, SHA256, byte count and optional conversion tool/version.
3. Quarantine archives with traversal/symlinks, mismatched signatures, ambiguous rights or duplicate hashes.
4. Static mesh FBX with true LOD, UV, normals, collision mesh where walkable; skeletal FBX with rig, skinning and importable animation semantics. Never final animated OBJ.
5. PBR packed PNG/TGA: precise ORM/RMA order plus sRGB/linear conventions explicitly recorded; no BMP.
6. Stage artifact in immutable verified Warehouse with single writer and receipts; only then READY_FOR_IMPORT. Import via existing Unreal integration process, not fake .uasset status. Record independently source_verified, warehouse_persisted, unreal_imported, world_placed, pie_tested, device_tested, visual_accepted.
7. Any code change requires same-batch updates to Docs/CURRENT_PROJECT_STATE.md, Docs/PRODUCTION_COMPLETENESS_MATRIX.md and Docs/WORLD_DETAIL_LEDGER.md. This candidate is documentation only.
8. Rendered acceptance requires chapter-specific screenshots and route traversal; 720p 30FPS is a target not a measured result.

## Highest-value gaps (hypotheses, not verified absent inventory)
Frodo and Gandalf final skeletal animation/deformation, FerryLanding grounding, pooled NPC reactions across save/load, distinct night ecology, region-specific signature props and legal ambient sound beds. Confirm exact inventory before purchasing/downloading duplicates.

## Growth accounting for this packet
Source produced 0; physically inspected 0; Warehouse persisted 0; Unreal imported 0; world-visible 0; new chapter Gate acceptance 0. Relative production growth for new physical assets: 0/478 = **0%**. Source discovery/planning value does not masquerade as gameplay completion.
