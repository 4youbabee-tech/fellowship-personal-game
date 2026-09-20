# Repository Hygiene / Consolidated Baseline

This document records the non-destructive cleanup policy after PR #53 was merged into `develop`.

## Current audited snapshot

- Integration branch: `develop`.
- PR #53 exact candidate head `833c3679e19290a2b046ea7f53013a76ae1b29f4` passed Pre-Unreal #500 and Unreal Build #335 before merge.
- PR #53 merged as `b9de4fd4a1aa6b4edeb25459a23b78c077dfcef7`.
- Runtime module currently has 55 tracked .h/.cpp/.cs files in the flat `Source/ShireJourney` root.
- `SourceAssets/Production` contains 351 tracked files: 304 OBJ, 22 MTL, 24 BMP and one Markdown file.
- `Docs/CHECKPOINTS.md` contains 68 CP headings and is due for an archive split before uncontrolled growth.
- Generated Unreal/editor directories remain untracked through `.gitignore`.
- Duplicate production sources are reported, never deleted automatically.

## Branch discipline

- `develop` is the only integration baseline.
- New production work starts from the latest green `develop` on one short, single-purpose branch.
- The exact candidate head must pass its relevant gates before merge.
- After merge, do not continue building on the old feature/repair branch.
- Historical checkpoint branches are not sources of truth after their meaningful content is present in `develop`.
- Diverged branches with unique commits are preserved until those commits are explicitly audited, absorbed or rejected.

## Safe cleanup

Allowed without gameplay redesign:

- harden ignore rules for developer/editor debris;
- audit tracked generated artifacts;
- keep the source architecture manifest synchronized;
- report duplicate production-source content without deleting it;
- move superseded documentation into `Docs/Archive/` only when validators and references are updated in the same change;
- identify stale branches after their content is proven present or superseded.

Do not:

- delete production OBJ/MTL/BMP assets because they look duplicated;
- move runtime C++ files during gameplay feature work;
- rename loaded assets during validation cleanup;
- rewrite story/save authority as part of repository housekeeping;
- treat Markdown/JSON file count as an FPS problem.

## Deferred structural cleanup

1. Split old checkpoint history into `Docs/Archive/` while keeping current handoff links valid.
2. Migrate `Source/ShireJourney` to the already-defined Public/Private domain layout in a dedicated compile-only wave.
3. Audit production source references before removing any duplicate or superseded asset source.
4. Replace remaining BMP sources only through an import-verified migration; file-format conversion must not silently change material references.
