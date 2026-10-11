# Shire Journey — Recovery checkpoint (2026-10-11, live-wave-1)

Authority: `Data/ProjectGovernor.json`; integration `develop`; release `main`; never delete `archive/pre-build-salvage-20260930`.

## Exact inspected GitHub state
- Baseline `develop@86966cfde730a7e9b3432d73da46fc67995d6ba7` (merged PR #381 local fast-preview source/tool recovery).
- Branch GET returned **31 refs**, PR GET returned **13 open pull requests** at this snapshot; re-query before writes or deletion.
- PR #380 `salvage/p1c01-final-closure-evidence-20261011@9f5b6fd53d6c004bc728b479c46af680ea0d3b1f`: open draft; **not merged**; mergeable_state=`dirty`; compare against develop: **6 ahead, 1 behind**. Exact-head Pre-Unreal Validation **38141627675 SUCCESS**. Unreal Build Validation **38141627681 queued**; owner Windows self-hosted runner must **not be started, dispatched or booked** during owner-offline work. A green hosted check is NOT a UE compile.
- Open PRs at inspection: #380, #367, #366, #362, #356, #355, #353, #352, #350, #339, #332, #331, #329. No assumption that PR labels, draft status or prior run status authorizes merge.
- Branch `salvage/p1c01-fast-pie-ci-guard-20261011` is Git-compare **0 ahead / 0 behind** and points at exact develop SHA. Eligible for **verified zero-ahead retirement** through the existing GitHub-hosted Branch Cleanup policy once it re-checks SHA and PR protections; deletion not asserted until remote ref-absence proof.
- Important divergent candidate examples: #367 is 1 ahead / 44 behind; #366 is 2 ahead / 44 behind; #362 is 5 ahead / 47 behind; #355 is 6 ahead / 50 behind. Other unique branches include Frodo deformation, warning debt, Edoras v1/v2 and historical production trees. Preserve all unique histories unless selective salvage or explicit supersession is proven.

## Physical source-assets audit, without laptop
- Branch `generated/p1c01-material-source-v1@f90b607e9c81184c4f4746c713bb09c707f61f88` contains 17 Git tree entries under `SourceAssets/Production/Imported/P1C01Materials/`: eight **Git LFS pointers** to Poly Haven CC0 BaseColor PNG files, eight small `.mtl` sidecars and one source receipt.
- Compared all 8 LFS SHA-256 object identifiers with `P1C01MaterialSourceReceipt.json`: **8/8 metadata OIDs match**; aggregate LFS-declared BaseColor bytes **137,972,730** (about 131.58 MiB). Git blob sizes of 132–133 bytes are normal **LFS pointers**, NOT image payloads and NOT proof the actual 2K PNG assets are accessible.
- Receipt records source provenance and `SOURCE_READY_FOR_UE_IMPORT`; this does **not** prove LFS hydration, PNG decode/dimensions, visual quality, license-per-file recheck, UE package import or material bindings. Do not equate LFS pointers or `.mtl` files with imported `.uasset` materials.
- No binary pointers are copied into `develop` by this administrative recovery checkpoint. Physical-source promotion requires an isolated preparation candidate, LFS hydration/QC, provenance and applicable CI; do not queue Unreal hardware merely to satisfy administrative documentation.

## Hard operating boundaries
1. Exact head Pre-Unreal is mandatory before merging this checkpoint PR. Documentation-only updates must not schedule the Windows self-hosted runner.
2. P1C01 remains the only runtime integration lane; owner approval is required to reactivate the Windows runner. Gate 6/7 remains unaccepted.
3. Whole-game/28-region source preparation, legal receipts, Blender scripts, character/terrain/material preprocessing and five-lane analysis may progress off-device; future runtime chapters may not open.
4. Do not bulk-merge divergent PRs. For #380 preserve the two unique source-only contract/test files and resolve the live `develop` documentation conflict in a separate exact-head validated integration candidate.
5. Do not clean storage again without a new storage problem; archive and unique commits are recovery-critical.

## Wave status / next specific actions
- Completed in this wave: current GitHub snapshot, 29 working-branch comparisons, source-only PR #380 conflict and CI classification, 8 independent LFS OID/receipt cross-checks, checkpoint/documentation reconciliation. Changes in this PR are **documentation only**.
- Pending: exact-head hosted Pre-Unreal for this checkpoint PR; no assumptions about checks or merges. Continue preparing real assets and portable QC tools on isolated branches; do not turn on the Windows runner.
- Next: if hosted validation passes and the live PR is clean, merge this checkpoint; inspect actual Branch Cleanup log/ref deletion; then selectively preserve/rebase #380, verified material sources, and character/FBX/tool candidates without opening P1C02 Runtime.

## Evidence and acceptance boundary
**SOURCE-AUDIT / DOCUMENTATION ONLY** pending exact-head Pre-Unreal. No new `COMPILE-TESTED`, `PIE-TESTED`, `DEVICE-TESTED`, `VISUALLY-ACCEPTED`, 720p/30 FPS proof, actual assets imported into Unreal, or Gate 6/7 result.
