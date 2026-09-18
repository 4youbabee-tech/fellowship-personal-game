# ShireJourney Runtime Module — Engineering Handoff

> **READ THIS BEFORE EDITING RUNTIME CODE.**
>
> This file lives inside `Source/ShireJourney` intentionally. The repository, not chat history, is the project memory.
> A new human or automated programmer must be able to resume from GitHub without depending on a previous conversation.

## Authoritative project memory

Read these in order:

1. `Docs/CURRENT_PROJECT_STATE.md` — exact operational state, proof level, and next hard gate.
2. `Docs/CHECKPOINTS.md` — chronological development checkpoints and what each one proved.
3. `Docs/WORLD_PRODUCTION_BLUEPRINT.md` — world/chapter/checkpoint engineering map.
4. `Docs/PRODUCTION_COMPLETENESS_MATRIX.md` — what exists versus what is still incomplete across production pillars.
5. `Docs/DEVELOPMENT_GATES.md` — mandatory build/PIE/device discipline.
6. `Docs/PROJECT_GUARDIAN.md` — regression memory and permanent lessons from failures.
7. `Docs/STORY_CANON_BIBLE.md` — story/canon authority before story changes.
8. `Data/SourceArchitecturePlan.json` — machine-readable ownership and target folder for every runtime module source file.
9. `Data/WorldCheckpointPlan.csv` — machine-readable player/world checkpoint intent.

If code, data, and documentation disagree, stop and reconcile them in the same logical change.

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
