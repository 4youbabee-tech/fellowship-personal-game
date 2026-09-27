# NEW DEVELOPER / NEW AI SESSION — START HERE

> **Do not use this `main` branch to infer current development state.**  
> `main` is the stable/release and GitHub default landing branch. Active development, the live Project Governor, current handoff, and current CI state live on **`develop`**.
>
> Before editing:
> 1. Switch GitHub/local checkout to `develop`.
> 2. Read `README.md` on `develop`.
> 3. Follow `Docs/PROJECT_GOVERNOR.md` → `Data/ProjectGovernor.json` → `Docs/CURRENT_PROJECT_STATE.md`.
> 4. Inspect live `develop` HEAD and GitHub Actions.
> 5. If local, run `Scripts/new_developer_onboarding.ps1`.
>
> **Project-management authority:** `Data/ProjectGovernor.json` on `develop`.  
> Do not reconstruct direction from old chats, old PR text, or this release-branch README.

---

# Shire Journey — UE4.27 Personal Game Project

A low-spec-targeted personal 3D game project that treats Peter Jackson's *The Fellowship of the Ring* as the primary continuity reference for **Part I**.

## Current state
This package is a C++/greybox starter, not the final visual game. It currently contains:
- third-person movement and camera,
- interaction + lightweight dialogue HUD,
- quest progression,
- quick save/load,
- cheap companion-follow prototype,
- Black Rider stealth prototype,
- low-cost ambient Hobbit routines,
- a generated Shire greybox reorganized around film-visible continuity,
- a complete Part I production bible from the Shire through Amon Hen,
- chapter, mission, location, character and dialogue-intent datasets.

## Active build scope
Chapter 01 — **The Shire**.

The whole film is planned as Part I, but production remains chapter-by-chapter so the project stays performant and finishable.

## Hardware target
- Intel Core i7 6th gen
- 8 GB DDR3 RAM
- AMD GPU with about 2 GB VRAM
- Windows / DirectX 11
- 720p / 30 FPS initial target

## Engine
Designed for Unreal Engine **4.27** because the target laptop is well below current UE5 recommended hardware.

## Film-reference rule
See `Docs/FILM_REFERENCE_POLICY.md`.

## Full Part I plan
See `Docs/PART1_FELLOWSHIP_MASTERPLAN.md` and `Data/Part1MissionFlow.csv`.

## Important
No final copyrighted film/game assets are included. The project uses original placeholder geometry and newly written game dialogue while using film continuity as design reference.
