# WORLD PRODUCTION BLUEPRINT

> **Engineering map for the whole game.**
>
> This file exists so the project never depends on chat memory and nobody gets lost when the world becomes large.
> Read this together with `CURRENT_PROJECT_STATE.md`, `CHECKPOINTS.md`, `STORY_CANON_BIBLE.md` and the machine-readable plans in `Data/`.

## 1. Two checkpoint systems — do not confuse them

### Development checkpoints
Recorded in `Docs/CHECKPOINTS.md`.
They describe what was built and what proof exists for that milestone.

### Player/world checkpoints
Planned in `Data/WorldCheckpointPlan.csv`.
They are safe story/world positions for autosave, restart, recovery and chapter transition.

The game already has quick save/load foundations and per-route persistence, but the dedicated automatic checkpoint/respawn system is **not yet claimed complete**. The checkpoint plan is now explicit so it can be implemented without inventing positions later.

## 2. Source-of-truth hierarchy

1. `Docs/CURRENT_PROJECT_STATE.md` — current operational truth and latest validated head.
2. `Docs/WORLD_PRODUCTION_BLUEPRINT.md` — world/chapter/checkpoint engineering map.
3. `Docs/CHECKPOINTS.md` — milestone history.
4. `Docs/DEVELOPMENT_GATES.md` — proof required before acceptance.
5. `Docs/STORY_CANON_BIBLE.md` — story/canon rules.
6. `Docs/PART1_FELLOWSHIP_MASTERPLAN.md` — Part I production direction.
7. `Data/WorldCheckpointPlan.csv` — machine-readable world checkpoint contract.
8. `Data/StoryBeatPlan.csv` — story/presentation beat contract.
9. `Data/BiomePlan.csv` — chapter visual/geography identity.
10. Runtime C++ — what the game actually does.

If these disagree, stop and reconcile them in the same change.

## 3. Runtime world map

| Chapter | Main world / route | Required journey landmarks | Engineering state |
|---|---|---|---|
| P1C01 | Shire | Bag End/Hobbiton → Party Field → eastern fields → wooded Black Rider road → Bucklebury Ferry | Active vertical slice / production pass |
| P1C02 | Bree | road/nightfall → gate → Prancing Pony → private room → attack aftermath → departure | Prototype |
| P1C03 | Weathertop / Ford | Midgewater → Weathertop → wound → flight → Ford | Prototype |
| P1C04 | Rivendell | awakening → Bilbo → Council → Fellowship → departure | Prototype |
| P1C05 | Fellowship road | march/camp → Crebain → Caradhras → Moria lake/door | Prototype |
| P1C06 | Moria | entry → halls → Balin's Tomb → Orc/Troll pressure → Balrog/bridge → escape | Prototype |
| P1C07 | Lothlorien | entry → grief/rest → Mirror → farewell → river departure | Prototype |
| P1C08 | Anduin / Amon Hen | river → Argonath → landing → Boromir pressure → Uruk attack → split / Part I end | Prototype |

Parallel route:
- `GandalfParallel / P1G01_Isengard` remains a controlled parallel route under the same save/route architecture.

## 4. Shire spatial engineering anchors

The Shire is the current visual-quality bar. Its runtime journey is intentionally spread across one continuous travel space.

| Anchor | Approximate runtime X | Purpose |
|---|---:|---|
| Chapter spawn / Bag End side | -2410 | safe start / tutorial orientation |
| Hobbiton exit | 1500 | leaving-home threshold |
| Eastern fields | 7600 | open-travel contrast |
| Wooded road | 14500 | Black Rider stealth / root-hide threat |
| Bucklebury Ferry | 23500 | escape and P1C02 handoff |

These are engineering anchors, not final art coordinates. Art may reshape the terrain, but the route order and story readability must remain intact.

## 5. Player checkpoint rules

A valid player checkpoint must:
- be at a safe location, never inside active combat or an unavoidable detection state;
- persist route, episode, playable character, chapter, active quest/stage, completed story beats and player transform;
- restore the matching world before restoring the exact transform;
- preserve the independent Frodo and Gandalf route snapshots;
- never allow a checkpoint to skip a required story result;
- place a pre-danger checkpoint before major stealth/combat sequences;
- place a transition checkpoint after a chapter handoff becomes authoritative;
- be tested by save → move/progress → reload → verify world/story/position.

Checkpoint IDs and intended save/respawn behavior are defined in `Data/WorldCheckpointPlan.csv`.

## 6. Production gate per world section

A region is not “done” because it looks better or because CI is green. Each major section moves through:

`PLANNED → BUILT → STATIC-VALIDATED → COMPILE-TESTED → ASSET-IMPORT-TESTED → PIE-TESTED → DEVICE-TESTED → VISUALLY-ACCEPTED`

For the current Shire production branch:
- static validation is green through Pre-Unreal Validation #112 on `bd3d0be...`;
- UE4.27.2 C++ build and production-asset import are green through Unreal Build Validation #10 on the same exact head;
- the import gate reported `50 files, 0 failures`;
- the new visual pass still requires focused PIE/device visual review before VISUALLY-ACCEPTED.

## 7. Current construction rule

Do not expand every chapter at the same visual depth at once.

Current order:
1. make P1C01 Shire the reference-quality vertical slice;
2. prove checkpoint/save/load and traversal on the target laptop;
3. lock the reusable environment/character/audio pipeline;
4. apply that production pattern chapter-by-chapter through P1C08;
5. keep Part II/III as roadmap until Part I is stable.

## 8. Handoff rule

If a new developer/assistant opens the project:
1. read `CURRENT_PROJECT_STATE.md`;
2. read this blueprint;
3. read the latest entries in `CHECKPOINTS.md`;
4. inspect latest `develop` head and both GitHub validation workflows;
5. inspect `WorldCheckpointPlan.csv`, `StoryBeatPlan.csv` and `BiomePlan.csv` for the chapter being changed;
6. never infer acceptance from an old checkpoint or from chat history.

## Visual beauty target — owner direction 2026-09-20

The visual bar is higher than the plain external reference screenshots previously discussed. The target is a distinctly beautiful, cinematic Middle-earth world rather than a generic fantasy landscape.

Production composition rules:
- every chapter needs at least one memorable hero vista/reveal;
- build foreground/midground/background depth with elevation, occlusion and landmark framing;
- favor cohesive terrain materials, vegetation clusters, water, fog, sky and lighting over raw object count;
- reserve the highest detail for hero landmarks and the player's near field; use LODs, instancing, culling and simpler distant silhouettes to preserve the 720p Low-Medium / 30 FPS target;
- keep each region visually unique: Shire lush/warm, Bree wet/lamplit, Weathertop austere/windy, Rivendell luminous/layered, Caradhras severe/snowbound, Moria monumental/dark, Lothlorien golden/ethereal, Anduin grand/open, Isengard ordered-to-corrupted industrial.

A region is not visually accepted merely because assets are present; it must read as beautiful and memorable in motion on the target device.
