# PROJECT GOVERNOR — SINGLE PROJECT AUTHORITY

> **READ THIS FIRST FOR PROJECT DECISIONS.**
>
> `Data/ProjectGovernor.json` is the **only authoritative project-management decision source**.
> It owns user requirements, priorities, conflicts, decisions, the active hard gate and region quality status.
>
> Other documents and plans may describe implementation details, story, world design or engineering,
> but they do not independently override the Governor.

## Why one authority

This project is large, chat history can disappear, and different human/automated programmers may work on it.

A single authority prevents:
- two programmers making incompatible decisions,
- one request silently replacing another,
- a new developer assuming an unfinished feature is complete,
- story, save, performance or traversal rules drifting apart,
- several "manager" files disagreeing about what is true.

## The one authoritative file

`Data/ProjectGovernor.json`

It contains:
- permanent user requirements,
- requirement status and priority,
- hard invariants,
- conflict-resolution rules,
- recorded decisions,
- unresolved conflicts,
- region quality gates,
- the current active gate,
- the update protocol,
- the target hardware/profile,
- the product north star.

## Supporting files are references, not managers

Examples:
- `CURRENT_PROJECT_STATE.md` explains the current operational state.
- `CHECKPOINTS.md` is milestone history.
- `STORY_CANON_BIBLE.md` explains story/canon detail.
- `WORLD_PRODUCTION_BLUEPRINT.md` explains world engineering.
- `SourceArchitecturePlan.json` maps source ownership.
- `FilmExperiencePlan.json`, `LivingWorldFeaturePlan.json`, biome/story/dialogue/audio/checkpoint plans give detailed implementation contracts.

If any of those contradict `Data/ProjectGovernor.json` on requirement status, priority, conflict resolution, active gate or acceptance state, reconcile them to the Governor.

## How a new request is handled

1. Read `Data/ProjectGovernor.json`.
2. Add or update one stable requirement entry.
3. Check dependencies and conflicts.
4. If it conflicts with an existing request, preserve both and add a decision/open conflict.
5. Only then implement.
6. After implementation, record repository evidence.
7. After testing, update only the proof actually obtained.
8. Never mark a region accepted without the required technical and human evidence.

## Decision order

The Governor preserves this priority order:
1. explicit current user direction,
2. build/save/story integrity,
3. film canon and chronology,
4. target-device performance,
5. playability and traversal,
6. player clarity and pacing,
7. living-world depth,
8. visual polish,
9. optional scope.

A lower-priority convenience cannot silently break a higher-priority invariant.

## Quality gates

Every major Part I region tracks:
- STATIC
- COMPILE
- BOOT
- TRAVERSAL
- PERSISTENCE
- PERFORMANCE
- PACING
- VISUAL

A compile success is not a traversal test.
A boot success is not a save/load test.
CI cannot decide that a section is fun or visually accepted.

## Team rule

Human or automated programmers may specialize in different areas, but **none of them is a second project manager**.

Each worker:
- reads the Governor,
- works within the assigned requirement/domain,
- updates evidence,
- does not change global direction independently.

The Governor is the project lead / traffic controller.

## Active-gate execution control

The Governor does not treat every `ACTIVE` backlog item as permission to execute it.

`execution_control` defines the one active development lane, the bundles allowed now, frozen backlog bundles and the concrete next actions for the current gate. An owner-directed stabilization freeze overrides generic unrelated-production work.

`Scripts/project_governor.py` cross-checks execution control, current focus, development mode, handoff branch/PR metadata and supporting management docs so those surfaces cannot silently drift apart.

## Reminder / pacing behavior

Every Pre-Unreal run prints **PROJECT GOVERNOR EXECUTION DIRECTIVE** first: active gate/lane, allowed bundles, frozen bundles and concrete next actions.

It then prints **BACKLOG MEMORY (NOT EXECUTION ORDER)** for unfinished CRITICAL/HIGH requirements. This preserves commitments without making frozen backlog look executable.

`Data/PlayerExperiencePacingPlan.json` remains the human review contract for boredom, repetition, waiting, clarity, discovery and story/combat/dialogue rhythm. CI may validate the contract exists; only human play may accept PACING.

## Current rule

The active lane is **W00_ARCHITECTURAL_STABILIZATION** under `ARCHITECTURAL_STABILIZATION_GATE`.

Exact parent `96398e7cc48277324113c7879a8d28e3b659757e` passed Pre-Unreal #781, Warehouse #197 and Unreal #616. That proves static/compile/import/headless-runtime behavior for the exercised suite, including CP-W00-147 fault semantics. It does **not** prove rendered PIE, target-device performance, audio playback, pacing or visual acceptance.

B1/B2/B3 stay frozen. W00 next closes packaged Data JSON execution, real audio playback, isolated Public/Private migration, target-device profiling and chapter-specific human acceptance before W01 may open.

## Important limitation

The Governor reduces drift and makes bugs/contradictions hard to hide. It cannot truthfully guarantee zero bugs in a large game.
Real UE4.27.2 compile, PIE, device tests and human play review remain mandatory.
