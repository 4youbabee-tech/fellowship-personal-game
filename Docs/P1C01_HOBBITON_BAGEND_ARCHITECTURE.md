# P1C01 Hobbiton + Bag End Architecture Drop B

## Source-grounded brief

This drop follows the project world bible:
- The Shire/Hobbiton: pastoral hills, lanes, farms, Hobbit-holes, warm domestic scale, circular doors, gardens.
- Bag End: dense lived-in Hobbit interior language, round geometry, narrative-hub function, deterministic chapter-state variants.
- F1-01: Shire onboarding/social/birthday setup with Bilbo/Frodo/Gandalf.

The implementation must preserve mission-state ownership and stable IDs. Architecture presents the world; it does not become gameplay identity.

## Canon correction

The prototype currently uses a "The Green Dragon" label inside the compact Hobbiton layout. Tolkien places The Green Dragon at Bywater. Drop B removes that Hobbiton canon claim and treats the current building as a generic village social/common yard until Bywater receives its own authored location.

## Drop B runtime work

1. Bag End hero approach:
   - garden arch / gate sequence,
   - mailbox / bench / flower boxes,
   - dry-stone property edge,
   - warm lantern accents,
   - clear path framing toward the round door.

2. Hobbiton domestic hierarchy:
   - preserve circular-door Hobbit-hole silhouettes,
   - reinforce gardens/property boundaries,
   - keep cottages subordinate to Bag End,
   - avoid dense actor spam.

3. Party Field:
   - authored canopy/table/lantern layout for F1-01,
   - keep optional/social content spatially readable.

4. Mill / village commons:
   - authored bridge/mill/common-yard composition,
   - no canonical Bywater inn claim inside Hobbiton.

## Deferred

The repository does not yet contain a dedicated production Bag End interior shell. Do not claim the interior complete. A hero interior modular kit must enter through the approved FBX/provenance pipeline before room/portal streaming and final interior acceptance.

## Performance

Architecture remains bounded and reuses existing resident production meshes. No synchronous heavy asset load is introduced. Final HLOD/collision/shadow budgets are measured on target hardware before Gate 6/7.

## Evidence boundary

Drop B begins STATIC-VALIDATED only. COMPILE-TESTED/PIE-TESTED/VISUALLY-ACCEPTED require matching evidence.
