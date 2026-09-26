# P1C01 Drop C - Materials + Vegetation

## Production intent

Raise the Shire from flat/proxy material treatment toward a coherent production surface and foliage layer without sacrificing the low-spec target.

The source hierarchy is preserved:
- world/canon bibles define Shire identity and landmark hierarchy;
- the systems bible defines material/foliage review gates;
- external sources provide candidate assets only after provenance/license review.

## Current production truth

- **C1 merged and machine-proven:** deterministic production material instances bind authored MTL `map_Kd` albedo paths.
- **C2 merged and machine-proven:** `M_ProductionFoliage` uses UE4.27 `SimpleGrassWind` through `UMaterialExpressionMaterialFunctionCall`; `M_ProductionFoliageFar` remains no-WPO.
- C2 exact candidate passed Pre-Unreal #1030 + Unreal #837; merged `develop@1d0580926299e4fac635bcb847343a49c444d4f1` passed #1031 + #838.
- **C3 next:** assign the near/mid foliage parent only for exact normalized identities `Grass`, `Leaves`, `LeafGreen`, `LeafGold`. Do not use broad filename/color/substring inference.
- **C4 after C3:** review real mesh LOD/material-slot/cull evidence before any far-parent assignment or density change.
- Shared weather/audio wind control remains a later bounded bridge after the visual material path is established.

## Asset and architecture rules

- Animated production assets are FBX-only.
- Production textures are PNG/TGA; no BMP.
- New PBR acquisitions should use channel-packed masks where useful.
- Heavy runtime assets remain soft/asynchronous; C3 is editor-import parent selection only.
- Repeated vegetation remains HISM/ISM. No foliage Actor/component Tick and no density growth in C3.
- Deterministic material instance object paths and existing AlbedoTexture/Color/Roughness/Metallic values remain unchanged.
- `M_ProductionFoliageFar` is not bound during C3; far LOD binding belongs to C4.

## Visual target

The Shire should read as soft pastoral grass/earth transition, warm domestic surfaces, restrained moss/stone, layered hedges/gardens/orchards, and subtle non-mechanical wind.

## Evidence boundary

C2 is **COMPILE-TESTED + exact-head automated import/QA/startup machine green**. C3 is **PREPARED_NOT_RUNTIME_STARTED** until post-C2 cleanup is complete. No PIE/device/visual/performance acceptance is inferred.
