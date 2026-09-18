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

## Reminder / pacing behavior

Every Pre-Unreal validation run now prints a **PROJECT GOVERNOR WORK REMINDER**:
- the active hard gate,
- whether it blocks major feature expansion,
- every unfinished CRITICAL/HIGH requirement,
- the first recorded missing-work item for each.

This is the repository-level reminder the user requested after the lost chat. It works whenever project validation/work review runs; it is not an autonomous phone notification.

`Data/PlayerExperiencePacingPlan.json` defines the chapter-by-chapter human review contract for boredom, repetition, waiting, clarity, discovery and story/combat/dialogue rhythm. CI may validate that the review contract exists, but only actual human play can mark PACING accepted.

## Current rule

The current functional hard gate remains open:
- Shire functional traversal,
- F9 save/load round-trip,
- F8 Frodo/Gandalf round-trip,
- P1C02-P1C08 chapter smoke tests,
- target-laptop traversal/performance observation,
- human pacing/clarity observations where applicable.

Major feature expansion remains blocked until the recorded gate is healthy.

## Important limitation

The Governor reduces drift and makes bugs/contradictions hard to hide. It cannot truthfully guarantee zero bugs in a large game.
Real UE4.27.2 compile, PIE, device tests and human play review remain mandatory.
