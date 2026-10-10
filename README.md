# Fellowship Personal Game — UE4.27

A low-spec-targeted personal 3D game project using Peter Jackson's *The Lord of the Rings* film continuity as the primary Part I story spine, expanded with exploration, living-world behavior and original game dialogue/music direction.

# NEW DEVELOPER / NEW AI SESSION — START HERE

> **GitHub default branch note:** `main` is the stable/release landing branch. Active development truth lives on `develop`. If GitHub opened this repository on `main`, switch to `develop` before inferring current project state or editing code.

There is **one project manager and one entry path**. Do not reconstruct project direction from chat history, old pull requests, or scattered planning notes.

**Canonical entry path:**

1. **Project authority:** read [Docs/PROJECT_GOVERNOR.md](Docs/PROJECT_GOVERNOR.md).
2. **Machine-readable authority:** read [Data/ProjectGovernor.json](Data/ProjectGovernor.json).
3. **Current operational state:** read [Docs/CURRENT_PROJECT_STATE.md](Docs/CURRENT_PROJECT_STATE.md).
4. **Development gates:** read [Docs/DEVELOPMENT_GATES.md](Docs/DEVELOPMENT_GATES.md).
5. **Regression memory:** read [Docs/PROJECT_GUARDIAN.md](Docs/PROJECT_GUARDIAN.md).
6. Inspect the live `develop` HEAD and current GitHub checks before editing.
7. Work on a short-lived candidate branch targeting `develop`; never use `main` as the normal development branch.

## STORY / SOURCE ENTRY — REQUIRED FOR STORY, WORLD OR CHAPTER WORK

Before touching story, missions, characters, dialogue, exploration or world content, read `Data/OwnerSourceReferenceIndex.json` and the permanent story/source contract in `Data/ProjectGovernor.json`.

The project rule is:

**Timeline organizes the journey; it does not shorten it. Film/screenplays lock film-driven chronology and outcomes. Tolkien supplies compatible deeper detail and book-only events. Sources 02-11 translate that material into production. Meaningful discovered detail is never silently omitted.**

For every chapter, use the source packet chain:

`Timeline chapter -> film/screenplay -> Tolkien narrative -> Appendix B/other appendices -> Sources 02-11 -> implementation/disposition`.

Compatible Tolkien material omitted/compressed by the films may become real playable traversal, exploration, quests, encounters, puzzles, NPC/social scenes or environmental storytelling when it preserves the locked film outcome and knowledge boundaries. Gate 6/7 may delay implementation; it is not permission to compress the planned story.

Localization product rule: **English VO + Arabic subtitles/UI/objectives**, while canonical Middle-earth location labels on the map remain in their original English names.

## CRITICAL RUNNER OWNERSHIP RULE

Before touching GitHub Actions runner configuration: **service mode is permanently excluded.** `actions.runner.*` should be absent; if Windows still exposes a pending-deletion entry it must be **Stopped + Disabled**. The only supported UE4 runner path is the supervised **interactive-user watchdog** through `ShireJourney-GitHubRunner-Watchdog`. `NETWORK SERVICE`, `LOCAL SERVICE`, and `SYSTEM` are forbidden. The watchdog continuously runs `Scripts/runner_service_guard.ps1` so a recreated service is stopped/deleted again. If topology looks wrong, fail closed and use the repository installer/verifier; do not improvise a service-mode repair.

## One-command onboarding

On Windows/PowerShell from the repository root:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Scripts\new_developer_onboarding.ps1
```

The script reads the **current** Governor and Git state and prints:
- the canonical authority,
- current branch and HEAD,
- active production lane and gate,
- current benchmark,
- next allowed actions,
- target hardware,
- required reading order,
- proof/acceptance boundaries.

It does not create a second manager and it does not copy live PR numbers into governance.

## Authority rule

`Data/ProjectGovernor.json` is the **only project-management decision authority**.

If a supporting document disagrees with it on priorities, active gate, requirement status, conflicts, or acceptance state, reconcile the supporting document to the Governor. GitHub remains the live authority for volatile transport state such as current PR number, branch open/closed state, mergeability, and workflow status.

## WHERE ARE WE NOW? — 60-second handoff

Do **not** decide current work from a milestone sentence copied into this README. Milestones move; the Governor is live project authority.

From the repository root, run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Scripts\new_developer_onboarding.ps1
```

That command prints the current production status directly from `Data/ProjectGovernor.json`: active lane, active gate, visible benchmark, current focus and **NEXT ALLOWED ACTIONS**, together with the checked-out Git branch/HEAD.

Then read [Docs/CURRENT_PROJECT_STATE.md](Docs/CURRENT_PROJECT_STATE.md) for the latest evidence-backed handoff.

**Decision rule:**
- `Data/ProjectGovernor.json` owns durable direction, priorities, active lane/gate and proof boundaries.
- `Docs/CURRENT_PROJECT_STATE.md` explains the latest evidence-backed operational handoff.
- Git/GitHub owns volatile branch, HEAD, PR and workflow/check state.
- If any of those disagree, **stop and reconcile to the Governor before editing**. Never guess from chat history or stale milestone prose.
- STATIC/COMPILE/import evidence never implies PIE/DEVICE/VISUAL/PERFORMANCE acceptance.

## Active quality target

The Shire is the first vertical slice and quality bar.

The broader Part I skeleton and later-region warehouse/source preparation may progress in parallel, but broad later-region runtime expansion remains controlled by Gate 6/7.

## Hardware target

- CPU: Intel Core i7-6498DU @ 2.50GHz
- GPU: AMD Radeon R5 M330, 2039 MB reported VRAM (2 GB class)
- RAM: 8 GB
- OS: Windows 11 Pro 64-bit (DirectX 12 installed, no DX12 Ultimate)
- Unreal Engine 4.27.2 runtime renderer: DX11 (the OS DirectX version does not change this)
- 1280x720; Balanced Medium with selective High where visually important
- Goal: stable 30 FPS, **not measured/accepted** until a real owner-laptop gameplay run proves it

## Engine

Unreal Engine 4.27.2.

## Key references

- project authority: `Data/ProjectGovernor.json`
- canonical source routing: `Data/OwnerSourceReferenceIndex.json`
- world/detail decision ledger: `Docs/WORLD_DETAIL_LEDGER.md`
- authority guide: `Docs/PROJECT_GOVERNOR.md`
- current handoff: `Docs/CURRENT_PROJECT_STATE.md`
- development gates: `Docs/DEVELOPMENT_GATES.md`
- regression memory: `Docs/PROJECT_GUARDIAN.md`
- story/canon: `Docs/STORY_CANON_BIBLE.md`
- Part I plan: `Docs/PART1_FELLOWSHIP_MASTERPLAN.md`
- story beats: `Data/StoryBeatPlan.csv`
- dialogue intent: `Data/DialogueIntent.csv`
- original music direction: `Data/MusicCuePlan.csv`

## Content policy inside the project

Major film-story outcomes are preserved.
Exploration and side content fill believable gaps without rewriting those outcomes.
Dialogue is newly written for the game.
Music direction is original and must not reproduce copyrighted film themes.
