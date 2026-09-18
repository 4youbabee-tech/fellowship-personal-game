# Production source assets

The production source pipeline is original project work and is imported automatically by `ShireProductionImport` into `/Game/Production`.

Current Shire production set includes:
- Frodo, Gandalf and Hobbit source meshes,
- authored Shire trees, rocks, crates, barrels and signposts,
- textured production ground/road blocks,
- turf mounds, hedges, shrubs, grass clumps and path stones,
- Hobbit-hole facade geometry,
- production fence segments,
- carts, benches, lanterns and a mill wheel,
- original procedural TGA surface maps for grass, soil, bark, leaves, stone, wood and painted doors.

The one-click launcher and the editor commandlet import textures before OBJ meshes so OBJ/MTL material references can resolve. Engine BasicShapes remain fallbacks only when a production asset is missing.

These assets are an intermediate game-production layer, not a claim of final photorealistic character/environment art.
