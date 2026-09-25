# P1C01 Drop C - Materials + Vegetation

## Production intent

Raise the Shire from flat/proxy material treatment toward a coherent production surface and foliage layer without sacrificing the low-spec target.

The source hierarchy is preserved:
- world/canon bibles define Shire identity and landmark hierarchy;
- the systems bible defines material/foliage review gates;
- external sources provide candidate assets only after provenance/license review.

## Verified current gap

The repository already has Shire TGA textures and authored MTL entries such as Grass, Dirt, Bark, Leaves, Stone, Wood and DoorGreen. The production importer synthesizes material instances with Color/Roughness/Metallic, but its MTL parser currently does not bind `map_Kd` into the synthesized material instances.

This means Drop C begins with the material pipeline itself, not with blind density growth.

## Runtime sequence

1. **C1 complete / merged:** authored MTL albedo paths bind into the deterministic production surface master.
2. **C2 implemented in source:** create `M_ProductionFoliage` with parameterized `SimpleGrassWind` WPO for near/mid grass/leaves only.
3. **C2 implemented in source:** create `M_ProductionFoliageFar` with no WPO so far LODs have a genuinely cheaper shader target instead of running wind math at zero amplitude.
4. **C3 next:** bind foliage parents by stable material identity without changing gameplay IDs, world ownership, or density.
5. **C4 after C3:** keep HISM/ISM, existing cull bands and LOD policy, then measure masked overdraw/shadow/material cost on target hardware before any density increase.
6. Only after the visual wind path is engine-green and visually accepted, prepare a shared weather/wind parameter bridge for materials and adaptive ambience.

## Asset rules

- Static world assets may remain OBJ where already established; animated production assets remain FBX-only.
- Textures remain PNG/TGA; no BMP production textures.
- New PBR acquisitions should use channel-packed masks where useful.
- Heavy runtime assets remain soft/asynchronous.
- Provider lists are sourcing candidates, not blanket approval.

## Visual target

The Shire should read as:
- soft pastoral grass/earth transition,
- warm wood and domestic surfaces,
- moss/stone restraint rather than glossy stone,
- layered hedges/gardens/orchards,
- subtle wind rather than synchronized mechanical swaying.

## Evidence boundary

This document prepares Drop C only. Runtime material/foliage changes do not start until the current post-merge world/architecture validation is green.

## C2 architecture boundary

- Wind lives in the material vertex path; there is no per-tree or per-grass Tick. C2 deliberately avoids the non-exported UE4.27 DistanceCullFade expression dependency.
- `WindIntensity`, `WindSpeed`, and `WindWeight` are scalar parameters so presentation can be tuned without code changes.
- The far material intentionally omits World Position Offset. Actual distance/LOD material assignment is deferred to C3/C4; C2 does not claim that the far path is visually active yet.
- Density stays unchanged until target-device profiling. No synchronous heavy gameplay loading is introduced.

## C2 evidence

C1 exact head passed Pre-Unreal #897 and Unreal Build Validation #732 before merge. C2 is **STATIC-VALIDATED** until its own exact head passes Pre-Unreal and UE4.27.2 production-import/core validation. No PIE/device/visual acceptance is claimed.
