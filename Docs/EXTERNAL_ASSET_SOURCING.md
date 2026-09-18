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
