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

## CRITICAL RUNNER OWNERSHIP RULE

Before touching GitHub Actions runner configuration: **do not enable or start the legacy `actions.runner.*` Windows service.** The UE4 runner must stay in supervised **interactive-user watchdog mode** through `ShireJourney-GitHubRunner-Watchdog`. `NETWORK SERVICE`, `LOCAL SERVICE`, and `SYSTEM` are forbidden identities for the UE4 runner. If runner topology looks wrong, fail closed and inspect `Scripts/install_runner_watchdog.ps1` + `Scripts/verify_runner_session.ps1`; do not improvise a service-mode repair.

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

- Intel Core i7 6th gen
- 8 GB RAM
- GPU around 2 GB VRAM
- Windows / DirectX 11
- 720p / 30 FPS initial floor
- Low/Medium scalability

## Engine

Unreal Engine 4.27.2.

## Key references

- project authority: `Data/ProjectGovernor.json`
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
