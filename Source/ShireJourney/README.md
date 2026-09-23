# ShireJourney Runtime Module — Engineering Handoff

> **READ THIS BEFORE EDITING RUNTIME CODE.**
>
> This file lives inside `Source/ShireJourney` intentionally. The repository, not chat history, is the project memory.
> A new human or automated programmer must be able to resume from GitHub without depending on a previous conversation.

## Authoritative project memory

Read these in order:

1. `Data/ProjectGovernor.json` — **single project authority** for requirements, priorities, conflicts, decisions, active gate and region quality.
2. `Docs/CURRENT_PROJECT_STATE.md` — operational snapshot, proof level and exact next hard gate.
3. `Docs/PROJECT_GOVERNOR.md` — explains how the single authority is used.
4. `Docs/PROJECT_MEMORY_SYSTEM.md` — persistence/recovery rules.
5. `Docs/CHECKPOINTS.md` — chronological development history.
6. `Docs/WORLD_PRODUCTION_BLUEPRINT.md` — world/chapter/checkpoint engineering map.
7. `Docs/LIVING_WORLD_AI_BLUEPRINT.md` — NPC/world-life intelligence design.
8. `Data/LivingWorldFeaturePlan.json` — living-world implementation/detail plan.
9. `Docs/PRODUCTION_COMPLETENESS_MATRIX.md` — production-pillar completeness.
10. `Docs/DEVELOPMENT_GATES.md` — build/PIE/device discipline.
11. `Docs/PROJECT_GUARDIAN.md` — regression memory.
12. `Docs/STORY_CANON_BIBLE.md` — story/canon detail.
13. `Data/SourceArchitecturePlan.json` — runtime source ownership/target paths.
14. `Data/WorldCheckpointPlan.csv` — player/world checkpoint detail.

If code, data, and documentation disagree, stop and reconcile them in the same logical change.


## User-request rule

Before implementing a meaningful feature request, find or create its stable ID in `Data/ProjectGovernor.json`.
After implementation, update the same Governor entry with repository evidence, remaining gaps and actual proof level.
Never mark a request complete merely because the conversation moved on.


## Current runtime module state

CP-W00-152 physically migrated the runtime module to **PUBLIC_PRIVATE_BY_DOMAIN**. The old flat layout is no longer active.

Project Guardian requires every runtime C++/header/build file in this module to be represented in `Data/SourceArchitecturePlan.json`. Adding a new source file without assigning a domain is a CI failure.

Current domains:
- **Core** — module entry point, game mode, interaction interface.
- **Characters** — player, story NPC, ambient NPC.
- **World** — chapter router, world builders, quest/world triggers.
- **Subsystems** — quest, dialogue, audio, story flow and presentation.
- **UI** — HUD.
- **SaveGame** — save object and per-route state.
- **Prototypes** — Black Rider and Fellowship enemy prototypes.

Runtime headers live under `Public/<Domain>/`; implementations live under `Private/<Domain>/`. `ShireJourney.Build.cs` remains at the module root. The module root itself is no longer exported as a public include path.

## Active folder layout

```text
Source/ShireJourney/
  ShireJourney.Build.cs
  README.md
  Public/
    Core/
    Characters/
    World/
    Subsystems/
    UI/
    SaveGame/
    Prototypes/
  Private/
    Core/
    Characters/
    World/
    Subsystems/
    UI/
    SaveGame/
    Prototypes/
```

The exact mapping and migration status are defined in `Data/SourceArchitecturePlan.json`. Existing basename includes remain legal because Build.cs exports only the explicit `Public/<Domain>` directories, never the whole module root.

## Source-layout rule

The physical migration is complete. Future maintenance must preserve these invariants:

1. headers belong under `Public/<Domain>/`,
2. implementation files belong under `Private/<Domain>/`,
3. `ShireJourney.Build.cs` remains at module root,
4. do not reintroduce flat root .h/.cpp files,
5. do not reintroduce `PublicIncludePaths.Add(ModuleDirectory)`,
6. register every new runtime file in `Data/SourceArchitecturePlan.json`,
7. source-layout changes require green Pre-Unreal and a real UE4.27.2 build,
8. never mix a large source-layout change with gameplay redesign.

## Handoff protocol

Before editing:

- confirm repository `4youbabee-tech/fellowship-personal-game`,
- confirm active development branch is `develop`,
- inspect the latest `develop` head and GitHub Actions,
- read `CURRENT_PROJECT_STATE.md`,
- locate the file/domain in `SourceArchitecturePlan.json`,
- read the relevant checkpoint/data plans.

After editing:

- update affected documentation/data in the same logical change,
- run/require static validation,
- run/require UE4.27.2 compile when C++ or build structure changed,
- perform the relevant PIE/device test before claiming it,
- record repeatable failures in Project Guardian.

## Acceptance language

Do not say a feature is simply "done" or "ready".

Use the project proof vocabulary:

- STATIC-VALIDATED
- COMPILE-TESTED
- ASSET-IMPORT-TESTED
- PIE-TESTED
- DEVICE-TESTED
- VISUALLY-ACCEPTED

The latest proof belongs in `Docs/CURRENT_PROJECT_STATE.md`, not in chat memory and not duplicated here.
