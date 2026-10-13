# P1C01 — Windows UE4.27.2 Runner Re-entry Sequence (13 Oct 2026)

**Authority:** Data/ProjectGovernor.json; Docs/DEVELOPMENT_GATES.md. **Owner status:** runner OFF until explicit owner signal. **Evidence boundary:** this is a static dispatch manifest, not an executed engine run. Do not enable a runner, dispatch workflow or assume COMPILE/PIE/DEVICE by reading this manifest. Fourth expansion is not frozen or cancelled.

## A. Canonical inputs
- Integration branch: develop; fetch and record fresh HEAD when the owner enables the runner. Never use a cached SHA. Main remains the release branch.
- Use one Windows Unreal writer at a time; no overlapping UE import, Editor save, Cook or package commands. Honor existing GitHub Action concurrency, warehouse pins and receipts.
- Existing engine workflow: .github/workflows/unreal-build-validation.yml; manual workflow_dispatch **run_self_hosted=true only after owner signal**. package_windows=false for ordinary engine repair builds.
- Existing headless runtime tests include Scripts/ci_runtime_startup.cmd, Scripts/ci_runtime_chapters.cmd and Scripts/ci_runtime_state.cmd.
- Before any Editor writer: inspect installation UE4.27.2, disk capacity, DX11 availability, workspace cleanliness, existing warehouse asset SHA256, pinned branch/PR heads and outstanding queued Unreal workflows. Do not blindly reimport or overwrite preserved .uasset.

## B. Merge / validation train (serial, exact-head)
1. **No runner required first:** finish hosted static/source PRs only after resolving latest-develop conflicts and passing exact-head Pre-Unreal. Relevant open sources include #446, #442 and #444; inspect Governor changes in #444 for owner intent before accepting. Do not merge queues as evidence of finished assets.
2. **First UE diagnostic:** compile canonical develop with an exact SHA; run UHT and startup/core Automation without asset reimport. Capture job and log IDs. If this fails, root repair only; do not add more branches to the engine lane.
3. **Gameplay fixes:** isolate/rebase #453 (NPC Visibility), #454 (dialogue + voice cancellation), #455 (world-event HUD), #456 (cinematic F9 + corrupted save transforms). Re-run hosted static and UE4 C++ build on each current head. Merge in that order only after required proof; do not overwrite latest develop docs. Then test the combined develop head for interaction, repeated dialogue, subtitle/no-voice, skip, F9 and corrupted save rollback.
4. **Ferry asset fix #435 last among root repairs:** preserve exact imported source and warehouse receipts. Execute import and simple collision check of /Game/Production/World/Shire/Cloud138/SM_ShFerryLanding; save and REOPEN .uasset to confirm persistence and UCX/simple collision. Then verify character capsule grounding, bank approach, traversal and navigation. A Python source-contract SUCCESS is not UE proof.
5. **Only after root repairs:** stage selected source FBX/PNG assets from already successful #441/#443/#445 receipts; inventory SHA256, unique paths, LOD/UV/UCX, packed PNG and prior warehouse states. Never count source artifacts as UE-imported/world-placed. No broad reimport of unchanged assets.
6. **Runtime P1C01 route:** Bag End -> Hobbiton -> Bagshot Row -> roads -> Bucklebury Ferry. Check movement/camera, NPC pool reuse and story knowledge gating; dialogue/subtitles/audio, world transitions, F9 save/load/rollback, route quest progression. Record exact engine logs per test. Human visual/audible acceptance cannot be inferred from headless logs.
7. **Hardware pass:** on owner-approved i7 6th-gen/8GB/approx 2GB VRAM, DX11 720p gather FPS/frame-time/VRAM/peak memory. 30 FPS is a goal, not established result. Collect screenshots/recordings before any VISUALLY-ACCEPTED state.

## C. Git branch cleanup fence
- Existing .github/workflows/branch-cleanup.yml and Scripts/run_branch_cleanup.ps1 are the sole branch janitor. Never add parallel cleanup writers.
- Safe to delete only after confirmed merge/approved supersession plus exact remote SHA recheck; never delete an active-PR head, develop/main, or a unique-ahead branch that has not been salvaged. Current ProjectGovernor branch_workflow / DEC-042 controls.
- Preserve archive/pre-build-salvage-20260930 and prep/f2-03-edoras-mega-source-v1/v2 per Data/BranchCleanupPlan.json.
- Orphan branches are NOT automatically dead: compare develop...branch and inspect semantic unique paths before taking action. Split useful source-only files into a focused PR if original branch bundles unsafe or obsolete changes.

## D. Stop/go reporting
For every batch capture base/head SHA, PR, merged SHA, exact GitHub Actions IDs and status, changed/added/deleted files, regression names, UE log excerpts, imported asset SHA receipts, actual FPS/VRAM if available, unresolved defects and Gate 6/7 status. No new runtime feature or fourth-expansion closeout without its gate.
