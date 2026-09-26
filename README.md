# Fellowship Personal Game — UE4.27

A low-spec-targeted personal 3D game project using Peter Jackson's *The Lord of the Rings* film continuity as the primary Part I story spine, expanded with exploration, living-world behavior and original game dialogue/music direction.

# NEW DEVELOPER / NEW AI SESSION — START HERE

There is **one project manager and one entry path**. Do not reconstruct project direction from chat history, old pull requests, or scattered planning notes.

**Canonical entry path:**

1. **Project authority:** read [Docs/PROJECT_GOVERNOR.md](Docs/PROJECT_GOVERNOR.md).
2. **Machine-readable authority:** read [Data/ProjectGovernor.json](Data/ProjectGovernor.json).
3. **Current operational state:** read [Docs/CURRENT_PROJECT_STATE.md](Docs/CURRENT_PROJECT_STATE.md).
4. **Development gates:** read [Docs/DEVELOPMENT_GATES.md](Docs/DEVELOPMENT_GATES.md).
5. **Regression memory:** read [Docs/PROJECT_GUARDIAN.md](Docs/PROJECT_GUARDIAN.md).
6. Inspect the live `develop` HEAD and current GitHub checks before editing.
7. Work on a short-lived candidate branch targeting `develop`; never use `main` as the normal development branch.

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

## Current production rule

The Shire / P1C01 vertical slice remains the active quality benchmark. C4 foliage LOD/cull evidence is closed at the candidate level with exact-head machine proof; the next production drop is **D — fixed-state lighting / sky / fog / low-cost water**, while **Mega Asset Promotion** may continue in parallel through the registered warehouse/intake pipeline.

Do not promote static/compile/import evidence into PIE/device/visual/performance acceptance without matching proof.

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
