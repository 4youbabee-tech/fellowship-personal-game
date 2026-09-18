# Fellowship Personal Game — UE4.27

A low-spec-targeted personal 3D game project using Peter Jackson's *The Lord of the Rings* film continuity as the primary Part I story spine, expanded with exploration, living-world behavior and original game dialogue/music direction.

## Start here

If you are a new programmer, a new ChatGPT session, or returning after a long break:

1. read `Docs/CURRENT_PROJECT_STATE.md`,
2. read `Docs/DEVELOPMENT_GATES.md`,
3. read `Docs/PROJECT_GUARDIAN.md`,
4. inspect the latest `develop` commit,
5. do not work directly on `main`.

## Current production rule

The current source must pass real UE4.27.2 compile + PIE + target-device smoke testing before another major feature checkpoint is opened.

GitHub static validation is useful but is not a substitute for engine testing.

## Active quality target

The Shire is the first vertical slice and quality bar.

The broader Part I skeleton and Gandalf/Isengard parallel prototype exist, but production remains chapter-by-chapter.

## Hardware target

- Intel Core i7 6th gen
- 8 GB RAM
- AMD GPU around 2 GB VRAM
- Windows / DirectX 11
- 720p / 30 FPS initial floor
- Low/Medium scalability

## Engine

Unreal Engine 4.27.2.

## Key references

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
