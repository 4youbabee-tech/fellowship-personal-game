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

## Runtime sequence after post-merge green

1. Add a texture parameter to the deterministic production surface master and bind authored MTL albedo paths.
2. Create a lightweight foliage master for grass/leaves only.
3. Add parameterized foliage WPO/wind while keeping repeated vegetation under HISM/ISM.
4. Keep existing cull bands/LOD policy and measure masked overdraw/shadow cost before raising density.
5. After the visual wind path is stable, bridge weather/wind state to both material response and adaptive ambience in a later bounded step.

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
