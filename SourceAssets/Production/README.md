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
- original procedural BMP surface maps for grass, soil, bark, leaves, stone, wood and painted doors.

The one-click launcher and the editor commandlet import textures before OBJ meshes so OBJ/MTL material references can resolve. Engine BasicShapes remain fallbacks only when a production asset is missing.

These assets are an intermediate game-production layer, not a claim of final photorealistic character/environment art.

## CP40 visual-production expansion

The production source tree now also includes an original reusable Shire architecture/prop kit:
- cottage house, mill house and stone bridge,
- village well, market stall, dry-stone wall and farm gate,
- haystack, flower box, lamp post, picnic table and loaded farm cart.

`Characters/Common` adds reusable original production archetypes for:
- human body parts,
- elf body parts,
- dwarf body/beard parts,
- cloak, sword, shield, axe and bow gear.

These source meshes are intentionally repository-owned and import through the same UE4.27.2 commandlet. They are a visible step beyond engine primitive proxies, while final dedicated skeletal rigs, facial rigs, cloth simulation and hero-quality materials remain later production work.

## CP41 Bree production expansion

`World/Bree` adds original production meshes for the Chapter 2 visual pass:
- timber/plaster town house,
- Prancing Pony inn shell,
- West Gate,
- market stall,
- street lantern,
- hitching post,
- common-room table,
- stacked goods/crates.

The runtime Bree builder places these as a production overlay while preserving all existing story trigger coordinates.

## CP42 Part I regional production expansion

Production world source now includes original chapter-specific landmark kits for:
- Weathertop,
- Rivendell,
- Fellowship road / Caradhras,
- Moria,
- Lothlorien,
- Anduin / Amon Hen.

These are imported by the standard production commandlet and overlaid by `FellowshipChapterWorldBuilder` without changing story trigger topology.
