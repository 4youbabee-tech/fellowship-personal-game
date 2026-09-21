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
5. `Data/OwnerSourceReferenceIndex.json` — durable Project Source IDs, SHA-256 fingerprints, authority and precedence.
6. `Docs/CHECKPOINTS.md` — chronological development history.
7. `Docs/WORLD_PRODUCTION_BLUEPRINT.md` — world/chapter/checkpoint engineering map.
8. `Docs/LIVING_WORLD_AI_BLUEPRINT.md` — NPC/world-life intelligence design.
9. `Data/LivingWorldFeaturePlan.json` — living-world implementation/detail plan.
10. `Docs/PRODUCTION_COMPLETENESS_MATRIX.md` — production-pillar completeness.
11. `Docs/DEVELOPMENT_GATES.md` — build/PIE/device discipline.
12. `Docs/PROJECT_GUARDIAN.md` — regression memory.
13. `Docs/STORY_CANON_BIBLE.md` — story/canon detail.
14. `Data/SourceArchitecturePlan.json` — runtime source ownership/target paths.
15. `Data/WorldCheckpointPlan.csv` — player/world checkpoint detail.

If code, data, and documentation disagree, stop and reconcile them in the same logical change.


## User-request rule

Before implementing a meaningful feature request, find or create its stable ID in `Data/ProjectGovernor.json`.
After implementation, update the same Governor entry with repository evidence, remaining gaps and actual proof level.
Never mark a request complete merely because the conversation moved on.


## Current runtime module state

The module is currently a guarded flat UE4.27 layout. This is historical structure, not the final organization target.

Project Guardian now requires every runtime C++/header/build file in this module to be represented in
`Data/SourceArchitecturePlan.json`. Adding a new source file without assigning a domain is a CI failure.

Current domains:

- **Core** — module entry point, game mode, interaction interface.
- **Characters** — player, story NPC, ambient NPC.
- **World** — chapter router, world builders, quest/world triggers.
- **Subsystems** — quest, dialogue, audio, story flow and presentation.
- **UI** — HUD.
- **SaveGame** — save object and per-route state.
- **Prototypes** — Black Rider and Fellowship enemy prototypes.

## Target folder layout

The planned organization is:

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

Headers intended for module-wide use move to `Public/<Domain>/`.
Implementation files move to `Private/<Domain>/`.

The exact current-to-target mapping is defined in `Data/SourceArchitecturePlan.json`.
Do not invent a different folder structure during a handoff.

## Refactor rule

Physical source-file migration is an organizational maintenance change, not a gameplay feature.

When performing the migration:

1. change paths only; do not redesign gameplay at the same time,
2. update module-local `#include` paths in the same change,
3. update `Scripts/pre_unreal_validate.py` path lookups and recursive scans,
4. update `Data/SourceArchitecturePlan.json` from `CURRENT_FLAT` to `MIGRATED`,
5. require green Pre-Unreal Validation,
6. require a real UE4.27.2 self-hosted C++ build,
7. require production asset import success,
8. then rerun the exact functional PIE smoke tests listed in `CURRENT_PROJECT_STATE.md`.

Never mix a large source-layout migration with a new gameplay feature.

## Handoff protocol

Before editing:

- confirm repository `4youbabee-tech/fellowship-personal-game`,
- confirm active development branch is `develop`,
- inspect the latest `develop` head and GitHub Actions,
- read `CURRENT_PROJECT_STATE.md`,
- for story/world/character work, read `Data/OwnerSourceReferenceIndex.json` and verify the needed Project Source material/precedence instead of relying on chat memory,
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
