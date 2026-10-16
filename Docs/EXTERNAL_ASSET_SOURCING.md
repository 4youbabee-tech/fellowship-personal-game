# Developer one-click 3D source shortlist — 2026-10-17 (PES-002 first)

**Start here:** `Data/ProjectGovernor.json#asset_source_navigation_2026_10_17` is the single decision authority. This page is the developer-friendly navigation view of that Governor entry; `Data/ExternalAssetManifest.json` remains the item-level license/provenance register. This is a **discovery catalog, not downloaded or approved game assets**. Current live session: **PES-002 Bag End Exterior**; do not open PES-003 or change the current runtime writer.

### Click once — useful sites, ordered for Shire production

| Source and direct link | Priority | Find / use | Required decision before importing |
|---|---|---|---|
| **[Fab: medieval cottages](https://www.fab.com/search?q=medieval%20cottage)** | A | Realistic modular Shire houses, furnishings, trees, props; PES-002/003/004/005/006 | Exact listing, game license and **UE4.27** content/version support. Launcher acquisition path; no UE5-only assumptions. |
| **[CGTrader: medieval cottages](https://www.cgtrader.com/3d-models?keywords=medieval%20cottage)** | A | Higher-fidelity hero buildings and original models; PES-002/004 | Confirm exact item's commercial/game rights, format, PBR, clean geometry and license receipt. |
| **[Sketchfab: downloadable cottages](https://sketchfab.com/search?q=medieval%20cottage&type=models&features=downloadable)** | A | Original buildings, props and smaller set dressing; PES-002/004/005 | License each **individual** model (prefer CC0; CC BY with attribution), creator rights/IP, GLB-to-FBX if needed. No NC/ND/Editorial. |
| **[Poly Haven textures](https://polyhaven.com/textures) / [models](https://polyhaven.com/models)** | A | True CC0 photoreal PBR wood, stone, soil, plaster, environment materials; PES-002/006 | Preserve metadata; use 1K/2K runtime textures unless measured need, packed masks as appropriate. |
| **[Adobe Mixamo](https://www.mixamo.com/)** | A — prep for later | Auto-rigging and original biped animations for PES-009/010/011, **not a substitute for high-quality mesh/skin** | Adobe login and original character permissions; imported skeletal FBX must deform under real animation tests. |
| **[Meshy AI](https://www.meshy.ai/)** | B — assist | Generate *original* Shire-style detail props, furniture and trim; manually clean topology and texture | Free generations have CC BY 4.0 attribution; paid ownership differs. Check the creation-plan terms and rights in uploaded references. |
| **[Quaternius](https://quaternius.com/)** | B — supporting | Low-cost modular/animation/background candidates, source-only until needed; often stylized, not hero photoreal | Check **per-pack** current license: current QAL 1.0 and older CC0 packs differ; manual acquisition and art-direction check. |
| **[3DExport: medieval houses](https://3dexport.com/3d-models?search=medieval%20house)** | B — review | Alternative source for furniture/architecture if A providers do not yield a usable result | License and exact asset format not independently cleared; `REVIEW_REQUIRED` only. |

### Exactly what to do for active PES-002 (minimum clicks)

1. Open the **three A-priority building searches** above. Choose only **non-franchise**, visually good, low-spec-feasible original cottage candidates that exceed current Unreal screenshots; compare against existing accepted warehouse inventory before downloading anything.
2. Open **Poly Haven** for matching believable PBR plaster/wood/stone/bark; don't solve poor geometry with a huge texture or unnecessarily increase draw calls.
3. For each selected **specific item**, register creator, direct asset URL, item ID, license version/evidence, costs, format (FBX/GLB/BLEND), mesh count, textures, target PES, and whether access is legal in `Data/ExternalAssetManifest.json`; quarantine unclear rights. No paid provider is silently purchased.
4. Prepare source in existing `SourceAssets/ExternalLicensed/Inbox` (or segregated private lane where existing Governor permits); inspect in Blender, normalize FBX/PNG/TGA, UV/PBR/LOD/collision and license receipts. Follow the existing Warehouse and UE4.27 import flow; **do not add a new import subsystem**.
5. Record evidence separately: `SOURCE_AVAILABLE -> WAREHOUSE_PERSISTED -> UE_IMPORTED -> WORLD_PLACED -> RENDER_OBSERVED -> ACCEPTED`. Compare real UE4 4-view render and FPS/device data; only one active Unreal writer and the active PES gate apply.

**Deprioritized from the owner's 15 suggestions:** Thangs, Cults3D, Printables and MakerWorld are primarily STL/3D-print workflows, not rigged/UV/PBR game assets; Steam Workshop, Nexus Mods and converted LOTR armor/game models are high rights/provenance risk; Patreon Steve Lund or creator channels and LOTR/VRM forums may be used as research contacts only until creator *and underlying franchise* rights are established. Do not treat internet model counts, search hits, model thumbnails, a T-pose or UE5 compatibility as evidence of a UE4.27-ready asset.

**Primary official policy links (checked 2026-10-17):** [Fab Standard License](https://www.fab.com/eula), [Sketchfab download/licensing](https://sketchfab.com/developers/download-api/guidelines), [Poly Haven CC0](https://polyhaven.com/license), [CGTrader game-use context](https://help.cgtrader.com/hc/en-us/articles/360015124517-Do-I-get-exclusive-rights-to-use-the-3D-model-after-purchase), [Meshy free/paid generated-asset ownership](https://help.meshy.ai/en/articles/10137554-what-is-the-ownership-of-the-generated-models), [Quaternius current QAL](https://quaternius.com/license.html), [Mixamo game-use FAQ](https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html). Item license and author provenance still govern actual use.

---

## Fast production smart fence - DEC-041

The production pipeline now separates administrative friction from technical safety.

- Warehouse/preparation candidates that are not downloaded yet stay `PENDING_SOURCE`; they do not fail unrelated work.
- PRIVATE_OFFLINE_ONLY may continue with unknown commercial-clearance status for the owner's local experiment, but access controls and technical safety remain strict and private payloads cannot leak into distributable output.
- Always blocking: provider-access bypass, dangerous/corrupt payloads, BMP production textures, animated final production assets that are not FBX, broken runtime dependencies, synchronous heavy loading, pooling/memory/performance violations, and world/save/grounding/collision defects.
- Supplied project PDFs are bound by hash/role in `Data/ProjectSourcePdfRegistryV1.json`; VISUAL-ONLY sources do not become canon evidence.
- Runtime integration remains exactly one changing lane while material/audio/character/world preparation can run in parallel.

# External Asset Sourcing Policy

This project may use high-quality third-party assets, but only through a license-tracked production pipeline.

## Why this exists

The visual-production plan benefits from Fab, Megascans, Sketchfab, commercial model libraries, and professional audio libraries. The risk is accidentally importing an editorial-only, non-commercial, no-derivatives, unlicensed, or franchise-ripped asset and later discovering it cannot legally ship or cannot be reproduced on the UE4.27.2 build machine.

## Approved workflow

1. Discover an asset.
2. Record provider, item name/ID, source URL, acquisition date, license class, attribution text if required, and proof/receipt reference in `Data/ExternalAssetManifest.json`.
3. Put downloads first in `SourceAssets/ExternalLicensed/Inbox`. This directory is intentionally ignored by Git.
4. Review technical compatibility, provenance, and license.
5. Only approved files move to `SourceAssets/ExternalLicensed/Approved/<Provider>/<AssetId>/`.
6. If the asset is an Unreal package obtained through Fab/Marketplace for UE4, use the Epic Games Launcher "Add to Project" path where appropriate. Do not assume the UE5-only in-editor Fab plugin exists in UE4.27.
7. Run Pre-Unreal Validation and the real UE4.27.2 build/import gate before relying on the asset.

## Provider decisions

- **Fab / Quixel Megascans:** preferred environment source when entitlement is clear. For UE4.27, Fab in Launcher supports UE4 project operations; the in-editor Fab integration is for UE5.3+.
- **Sketchfab:** use CC0, CC BY with attribution, or a store/game-use license. Do not use NC, ND, Editorial, or unknown-license models.
- **TurboSquid / CGTrader:** acceptable only after exact item license review. Editorial or brand/IP models are not automatically usable in a game.
- **Sonniss:** strong source for game SFX; record the specific bundle/license version.
- **Freesound:** prefer CC0; CC BY is acceptable with attribution. Reject NC for production.
- **Artlist / Epidemic Sound:** useful for music/SFX only after the account/project license is verified for game use.
- **Incompetech:** possible attribution-based music source when the exact track/license is recorded.
- **ArtStation:** reference/inspiration only unless a work is separately licensed.
- **Tolkien Gateway / LOTR Wiki:** story research/reference only. Do not import their fair-use images/maps or copy large copyrighted passages/dialogue.

## Franchise/IP rule

An asset being downloadable or purchasable does **not** automatically grant rights to somebody else's franchise, trademark, costume design, actor likeness, movie prop, or game model. "Lord of the Rings" fan models, ripped movie/game assets, branded editorial models, exact actor likenesses, and copied film dialogue are blocked unless separate rights/clearance exists.

The production target is an original project-owned interpretation informed by research, not a repository of ripped franchise assets.

## Private offline vs distributable framework

The owner has explicitly separated two asset lanes:

- **PRIVATE_OFFLINE_ONLY:** for the owner's local, non-public interactive-film build. Commercial-clearance uncertainty does not by itself block local experimental intake. The asset must stay tagged as private-only, retain source/provenance information when known, remain replaceable, and stay outside every distributable/commercial Framework package.
- **DISTRIBUTABLE_FRAMEWORK:** for any reusable product, public build, marketplace package, sample project or future commercial release. This lane remains strict: assets require clear redistribution/commercial entitlement plus provenance/attribution/receipt metadata as applicable.

This split does **not** relax provider access rules. Do not bypass login, account entitlement, paywalls, DRM, anti-bot controls or prohibited scraping. A downloadable asset is not automatically redistributable, and PRIVATE_OFFLINE_ONLY is not a rights claim.

The preferred local isolation root is `SourceAssets/PrivateOffline`. Framework code/data must not hard-require those payloads; private assets should remain swappable through data/soft-reference boundaries where runtime integration needs them.
