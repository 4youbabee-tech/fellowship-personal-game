# PES-002 Production Acceleration Decision & Evidence Registry

**Authority:** `Data/ProjectGovernor.json`; **status:** architecture/operations adopted, implementations explicitly staged. No shadow Governor. Do not change runtime ownership without Gate 6/7.

| Workstream | Professional source | Applied decision | Verification boundary |
|---|---|---|---|
| M0 quick index | Existing project Governor, preflight and CI; no new authority | `Docs/CURRENT_STATE_SHORT.md` <=200 lines, live exact HEAD + scoped searches of unchanged ledgers | Static short-index test; content freshness independently verified in each M0 |
| Data-driven decoration | Epic UE4.27 Data Driven Gameplay Elements: https://dev.epicgames.com/documentation/unreal-engine/data-driven-gameplay-elements?application_version=4.27 | Existing runtime builder owns spawning, but P1C01 non-gameplay decor rows will move to schema-validated data. One loader, known asset IDs, resident-only pointers; no `LoadObject` in runtime. | Source/schema test first; Unreal imported asset presence + world placement exact-head receipt later. NOT RUN |
| Regional stream | Epic UE4.27 Level Streaming Overview: https://dev.epicgames.com/documentation/unreal-engine/level-streaming-overview?application_version=4.27 | Persistent world + per-area streamable sublevels after actual .umap creation; no UE5 World Partition and no inactive chapter runtime activation. | Persist/reopen exact .umap, scene entrance/collision and memory capture. NOT RUN |
| Texture memory | Epic UE4.27 Texture Streaming Overview: https://dev.epicgames.com/documentation/en-us/unreal-engine/texture-streaming-overview?application_version=4.27 | Keep HISM/LOD/mip/streaming pool discipline, profile before choosing LOD & atlas size. | Target laptop stat unit/GPU, VRAM, DX11, 720p >=30 FPS. NOT RUN |
| Screenshots | Existing UE4.27 runtime capture + PNG exact dimensions and per-view logs | Replace best-effort with four fixed-angle captures at identical conditions; automatic mean luminance is a **screening signal only**, not a visual-acceptance decision (intentional dusk is possible). Require actual before/after SHA pairs and reviewer. | Current pipeline has three angles; fourth and luminance gate NOT IMPLEMENTED |
| Character pipeline | Epic UE4.27 skeletal mesh/retarget documentation; provider terms separately | Prioritize suitable Paragon/Mixamo hero sources and lighter legally obtained crowd art, but do not conflate generic rig with final Frodo likeness. 5 characters with skin deformation, Idle/Walk and LODs. | Candidate/source/license receipt -> private warehouse -> UE imported -> skin/animation observed -> low-spec performance -> visual approval. NONE of five accepted |
| Licensing | Fab official license: https://www.fab.com/eula; actual specific Epic/Adobe/author page terms govern every acquisition | No unrestricted asset source/re-export in public GitHub. For assets with no permission to redistribute, only asset ID, link, author, license evidence URL, SHA256, warehouse-private locator in repo (never access credentials). Reject game/film rips, regardless of home use. | Per-asset provenance/rights audit before any binary download/upload; no license assumed from aggregate provider name |
| Single PES PR | Existing Governor DEC-PES root-cause rules | One existing PR #477, commit cohesive fixes on its existing branch until Gate 6/7 permit closeout. | Assert live PR head and reject independent runtime PES PRs at M0 |

## Candidate license-source shortlist — **not downloaded or imported**
- **Paragon (Epic):** potentially high-detail hero asset; exact item entitlement/allowed engine use and source re-distribution restrictions must be checked, then triangle/texture/LOD budgets. *Artist-character role is prototype only, not licensed as a Tolkien actor likeness.*
- **Mixamo:** exact account-use agreement and per-character/motion download receipt; retarget compatibility, no public source redistribution assumed.
- **Poly Haven:** CC0 PBR/meshes selected for Shire environmental identity; register URL and file SHA for each.
- **Quixel/Fab:** check asset-specific Fab license, eligible acquisition path and UE4.27 manual-import compatibility, not assumed Bridge plugin support.
- **Quaternius, KayKit, 100 Avatars:** author license must be confirmed per file; previously rejected KayKit raw rigs are NOT requeued without material correction.
- **Sketchfab:** verify exact license/version/author; CC-BY-NC (where actually offered and applicable) requires attribution and genuine noncommercial compliance; no unauthorized public source mirrors.

## Mandatory receipt for each of five characters
`character_id`, `source_provider`, `asset_identifier`, `creator`, `license_label`, `license_terms_url`, `download_timestamp`, `sha256`, `redistribution_allowed`, `private_warehouse_receipt`, `source_polycount`, `lod_counts`, `texture_memory`, `ue4_mesh_package`, `skeleton_package`, `idle_animation`, `walk_animation`, `deformation_evidence`, `render_artifact_sha`, `device_fps`, `acceptance_state`. Unproven fields stay null.

## Before/after tracking (GitHub HEAD inspected 2026-10-15)
| Metric | Before | After this **index/governance** candidate | Acceptance |
|---|---:|---:|---|
| Read-to-orient current-state lines | 4,830 in legacy status | <=200 in new short index; legacy remains unchanged | CI structural check, not measured time savings |
| Legacy Governor / current-state / matrix / ledger | 664,982 / 643,255 / 421,983 / 263,758 chars | Original full files preserved; Governor grows slightly to record owner directives | No history deleted |
| WorldBuilder authored lines | 6,427 | 6,427; data migration pending | Runtime data conversion not claimed |
| Newly placed Unreal characters | 0 of required 5 verified | 0 verified | Unreal import/screenshots NOT RUN |
| Four-angle luminance-gated screenshots | 0 proven | 0 proven | Not accepted |

## Extra Windows build option (not authorized)
- **Existing runner:** incremental marginal hardware charge may be lowest, but current queue/runtime cost must be measured first.
- **Second physical Windows workstation:** capital + Windows/UE4 storage + electricity + backup + setup/maintenance; no purchase before owner approval and writer serialization design.
- **Windows cloud VM:** hourly compute + persistent storage + egress + licensing; valuable for occasional builds but can be costlier if left running. Compare **measured** baseline build-hours before selecting a vendor. This is not a quotation.
