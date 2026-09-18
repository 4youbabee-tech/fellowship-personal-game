# PROJECT GOVERNOR — INTERNAL DEVELOPMENT CONTROL SYSTEM

> The Project Governor is the project's pacing/control layer.
> It exists so the game does not depend on one chat, one programmer, or one person's memory.

## Responsibilities

The Governor combines four kinds of project memory:

1. **Requirements** — `Data/ProjectRequirements.json`
2. **Decisions/conflicts** — `Data/ProjectDecisions.json`
3. **Hard policy / priority rules** — `Data/ProjectGovernorPolicy.json`
4. **Region quality gates** — `Data/ExperienceQualityGates.json`

It works together with Project Guardian, CURRENT_PROJECT_STATE, CHECKPOINTS and the source architecture map.

## What it must prevent

- silently forgetting a user request,
- silently replacing an older request with a contradictory newer request,
- changing the film story spine by accident,
- claiming a feature complete because it compiled,
- accepting a region that cannot be traversed,
- accepting save/load or route switching without round-trip proof,
- adding visual/NPC complexity that makes the target laptop unplayable,
- continuing feature expansion while a previously passed critical gate is broken,
- letting long empty/repetitive sections become accepted without human pacing review.

## Conflict resolution

If two requests conflict:
1. preserve both requests in the ledger,
2. mark/record the conflict,
3. create a decision in `Data/ProjectDecisions.json`,
4. use the priority rules in `Data/ProjectGovernorPolicy.json`,
5. if product direction itself must change, record the user's explicit override,
6. never silently delete the losing/older request; mark it SUPERSEDED/DEFERRED/REJECTED with reason when appropriate.

The Governor is deterministic in CI. It cannot magically understand every future natural-language request by itself.
The assistant/developer must translate each meaningful request into the structured ledger. CI then enforces that the structured project memory stays coherent.

## Quality gate philosophy

A large game cannot truthfully promise "zero bugs".
Instead, we make bugs expensive to hide:

- STATIC catches contract/data regressions,
- COMPILE proves the actual UE4.27 code builds,
- BOOT proves a region can enter play,
- TRAVERSAL proves intended paths/anchors are reachable and not trapping,
- PERSISTENCE proves save/load and route continuity,
- PERFORMANCE checks the actual target laptop,
- PACING is human play review for boredom/friction/repetition/clarity,
- VISUAL is explicit user acceptance.

A region is not accepted merely because an earlier gate passed.

## Player enjoyment rule

The product goal is not only technical correctness. The player should enjoy the journey.

Therefore each major region needs human review for:
- control responsiveness,
- objective clarity,
- travel rhythm,
- repetition,
- unnecessary waiting,
- frustrating blockers,
- empty stretches,
- combat/dialogue pacing,
- sense of discovery,
- reward for exploration.

The Governor can require that review; it cannot automatically measure "fun" from CI.

## Current active rule

Until the current functional hard gate is healthy, major feature expansion remains blocked.
The next functional evidence remains:
- F9 save/load round-trip,
- F8 Frodo/Gandalf round-trip,
- P1C02-P1C08 chapter smoke,
- target-device traversal/performance observations.

After those gates are healthy, the Governor can permit the next planned maintenance/feature checkpoint according to the requirement ledger.
