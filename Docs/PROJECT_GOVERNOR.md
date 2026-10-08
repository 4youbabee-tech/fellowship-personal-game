# PROJECT GOVERNOR — SINGLE PROJECT AUTHORITY

> **READ THIS FIRST FOR PROJECT DECISIONS.**
>
> `Data/ProjectGovernor.json` is the **only authoritative project-management decision source**.
> It owns user requirements, priorities, conflicts, decisions, the active hard gate and region quality status.
>
> Other documents and plans may describe implementation details, story, world design or engineering,
> but they do not independently override the Governor.

## New developer / new AI session entry

The repository has one onboarding path:

If GitHub opened the repository on `main`, treat it only as the stable/release landing surface and switch to `develop` before reading current execution state or editing code.

`README.md` → `Docs/PROJECT_GOVERNOR.md` → `Data/ProjectGovernor.json` → `Docs/CURRENT_PROJECT_STATE.md` → `Docs/DEVELOPMENT_GATES.md` → `Docs/PROJECT_GUARDIAN.md`.

A new worker may run `Scripts/new_developer_onboarding.ps1` from the repository root to print the current Governor lane, gate, benchmark, next actions, Git branch/HEAD and proof boundary.

This script is a reader, not a second manager. It derives durable direction from ProjectGovernor and live transport state from Git/GitHub.

## Permanent story/source contract

For story, mission, world, character, dialogue or exploration work, the worker must also read `Data/OwnerSourceReferenceIndex.json`.

The permanent hierarchy is:
- the Timeline Bible organizes F1-F3 sequence, safe windows and locked outcomes; it is not a detail ceiling,
- the film trilogy and supplied screenplays control film-driven chronology/staging/outcomes,
- Tolkien's supplied *The Lord of the Rings* + Appendices supplies compatible deeper lore, geography, culture, chronology, journey detail and book-only events,
- Sources 02-11 convert that material into production/gameplay/technical execution.

The project is **experience-first, not summary-first**. Compatible Tolkien material omitted/compressed by the films can be implemented as real gameplay when it preserves locked film outcomes and knowledge boundaries. Every meaningful discovered source detail must be implemented or explicitly dispositioned; Gate 6/7 may delay runtime scope but does not authorize narrative compression.

## Permanent localization contract

Spoken VO remains English. Arabic covers subtitles, objectives/quest directions, menus, settings, HUD/system guidance and tutorial text. Canonical Middle-earth location labels on the map remain in their original English names. Arabic production requires correct RTL shaping/layout/wrapping/font support and subtitle synchronization. Runtime/device acceptance remains separate from registering this product rule.

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

## Runner ownership hard invariant

The UE4.27 self-hosted runner is **not** a Windows-service lane. The legacy `actions.runner.*` service path is eliminated: it should be absent, or only **Stopped + Disabled** while Windows completes pending deletion. Execution is owned solely by the proven interactive Windows user through the `ShireJourney-GitHubRunner-Watchdog` Scheduled Task. `NETWORK SERVICE`, `LOCAL SERVICE`, and `SYSTEM` are forbidden. The watchdog continuously enforces this through `runner_service_guard.ps1`. A human/AI worker may inspect runner health, but must not change runner ownership/topology without explicit owner authorization.

## Active-gate execution control

The Governor does not treat every `ACTIVE` backlog item as permission to execute it.

`execution_control` defines the one active development lane, the bundles allowed now, frozen backlog bundles and the concrete next actions for the current gate. An owner-directed stabilization freeze overrides generic unrelated-production work.

`Scripts/project_governor.py` cross-checks execution control, current focus, development mode, handoff branch/PR metadata and supporting management docs so those surfaces cannot silently drift apart.

## Reminder / pacing behavior

Every Pre-Unreal run prints **PROJECT GOVERNOR EXECUTION DIRECTIVE** first: active gate/lane, allowed bundles, frozen bundles and concrete next actions.

It then prints **BACKLOG MEMORY (NOT EXECUTION ORDER)** for unfinished CRITICAL/HIGH requirements. This preserves commitments without making frozen backlog look executable.

`Data/PlayerExperiencePacingPlan.json` remains the human review contract for boredom, repetition, waiting, clarity, discovery and story/combat/dialogue rhythm. CI may validate the contract exists; only human play may accept PACING.

## Development-mode contract

Development phases are registered in `development_mode_contract` inside the Governor. That contract owns mode identity, supersedes relationships and the labels that require manual/device evidence. Validators consume the shared semantic helper; they must not keep independent mode allowlists or decide proof honesty from prose wording.

## Continuous Verified Build Protocol (CVBP) — permanent operating method

The authoritative policy is `Data/ProjectGovernor.json#continuous_verified_build_protocol_2026_10_08`; this is a human-readable guide, **not a second manager or gate**. CVBP is the established milestone-based Continuous Engineering Progress practice, formalized for live, evidenced delivery.

- **Act through the tools:** choose the active Governor-authorized P1C01 production milestone and actually work/commit/verify it; do not substitute planning for deliverables.
- **Keep the owner informed during work:** stage number, what really changed, commit/PR, CI run/job and logs, artifacts/real screenshots, evidence grade, blocker, next action. Provide updates as milestones finish, not only in a huge final recap.
- **Repair precise root causes:** inspect failing exact-head logs, fix the smallest broken layer, rerun the relevant gate and continue unrelated allowed preparation; never delete genuine technical, save, canon, license or device safeguards.
- **Prioritize visible improvement:** coherent production packets and real art/character/world/audio/runtime quality over bureaucracy, repeated documentation-only builds or meaningless micro-commits.
- **Resume without chat history:** on the live PR/Governor-linked record, write compact branch/SHA, last green CI, artifact IDs/URLs, proven and pending levels, open blocker and exact next production task. Re-read it when a chat fills.
- **Stay honest:** static/build/headless tests do not imply PIE, target-device FPS, accepted visuals or Gate 6/7. No autonomous background execution without an active job or specifically requested automation.

Historical working example, not a permanent active-head instruction: P1C01 PR #329, `c371b5b2f14e`, Unreal Build Validation #1746 succeeded at source/compile/import/render/headless/package/startup while human visual, PIE, device performance and Gate 6/7 remained pending.

Follow Governor `execution_control` for current direction, dependencies and scope. No new runtime chapter opens from this reporting policy.
## Current rule

The active lane is **W01_P1C01_PRODUCTION_VERTICAL_SLICE** under the P1C01 vertical-slice gate.

W00 architectural stabilization is closed. Historical W00 repair text is reference history only and must not reopen the repair lane without concrete regression evidence.

C3/C4 and the D fixed-state lighting/sky/fog/low-cost-water stage are historical production milestones, not execution authority. The current runtime order must be read from `Data/ProjectGovernor.json` (`current_focus` + `execution_control.next_actions`) and checked against live GitHub exact-head/CI state. Do not infer the next drop from copied milestone prose in this guide.

Administrative state must not become a production bottleneck. Live PR numbers and candidate branch names come from GitHub, not copied governance fields. The repository-native 24-hour Project Manager report is informational only. Technical runtime/save/canon/performance gates remain fail-closed for the affected lane.

## Important limitation

The Governor reduces drift and makes bugs/contradictions hard to hide. It cannot truthfully guarantee zero bugs in a large game.
Real UE4.27.2 compile, PIE, device tests and human play review remain mandatory.
