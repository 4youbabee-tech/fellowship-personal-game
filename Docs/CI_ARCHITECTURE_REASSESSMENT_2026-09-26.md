# CI / Production Architecture Reassessment — 2026-09-26

## Executive decision

The project direction remains valid: exact-head validation, strict story/save/streaming guards, UE4.27.2 machine proof, and Gate 6/7 evidence should remain. The recurring friction came primarily from **validation architecture and workflow ownership**, not from a need to weaken engineering rigor.

The key correction is to preserve exactly one persistent UE4 project workspace for UnrealBuildTool while moving every non-Unreal checkout into isolated temporary directories.

## Evidence reviewed

Recent workflow window reviewed:
- 31 Unreal Build Validation runs: **11 success, 17 cancelled, 3 failure**.
- 31 Pre-Unreal Validation runs: **11 success, 16 cancelled, 4 failure**.
- Legitimate D exact-head validation #884 succeeded.
- Administrative runs #885-#887 repeated full engine work.
- #888 spent roughly eleven minutes in checkout before cancellation and produced no useful engine proof.
- #889 passed compile/import/runtime core evidence and later failed a packaging DbgHelp destination ACL probe.
- #891, an older administrative head, eventually succeeded but occupied the single Windows runner for about twenty-three minutes.

Representative failure taxonomy:
- **GAME_RUNTIME / source defect:** #867 detected a real defaultMat warning-debt regression.
- **VALIDATOR_POLICY:** #1068 stale phase/status expectations; #1074 PG-172 false-positive recapture assumption; #1082 classifier regression test.
- **ADMIN_GOVERNANCE:** #1052 board/handoff disagreement; #1075 handoff baseline drift.
- **CI_INFRA:** #1074 transient low-speed Git transfer; #888 stalled checkout; #889 DbgHelp destination ACL/package infrastructure failure.
- **SUPERSEDED:** the majority of cancelled runs were older SHAs made irrelevant by immediate follow-up commits.

Conclusion: red status must no longer be interpreted as a gameplay regression until its failure class is identified.

## Root causes

### 1. Lightweight workflows destroyed the Unreal workspace

Pre-Unreal, Runner Health and Branch Cleanup all used the same self-hosted repository workspace as Unreal validation and contained destructive checkout logic such as deleting GITHUB_WORKSPACE. Warehouse staging removed root .git metadata.

This erased Git working-state continuity and could invalidate project Intermediate/Binaries timestamps between engine runs.

### 2. UBT incremental state was repeatedly lost

Multiple runs reported:
- Creating makefile for ShireJourneyEditor (no existing makefile)
- Building 76 actions with 1 process
- roughly 238-252 seconds of editor compilation

Epic documents that UnrealBuildTool adaptive working-set detection uses Git status for Git repositories, and UBT makefile reuse is intended to accelerate iterative builds. Destroying Git/workspace continuity works directly against that mechanism.

### 3. Classification was too conservative around merge/administration state

A merge commit could have a different commit SHA but the exact same Git tree as an already-green candidate. Before tree-equivalent proof reuse, a cancelled post-merge run forced a redundant FULL validation despite byte-identical content.

### 4. Too many tiny commits caused CI churn

Sequential single-file commits produced long chains of immediately superseded Pre-Unreal/Unreal runs. Cancellation prevents full waste but does not eliminate queue/log overhead.

Policy: one coherent wave should become one atomic multi-file commit whenever the Git tooling permits.

### 5. Infrastructure/package failures were replaying proven core work

Package ACL or CI-policy repairs should not cause C++ compile + import + eight chapter audits to rerun when the parent core proof is exact and safe to inherit.

## New lane architecture

### Lane A — Pre-Unreal static/policy
- Existing self-hosted machine, no additional hosted-runner dependency or cost.
- Exact source checkout under RUNNER_TEMP.
- Never deletes or replaces GITHUB_WORKSPACE.
- Does not own Unreal Intermediate/Binaries.
- Runs Python/static/governance/source-quality tests only.

### Lane B — Unreal machine proof
- Sole owner of the persistent GITHUB_WORKSPACE.
- Exact SHA verification remains mandatory.
- Preserves .git between jobs.
- Runtime/config/source classification selects asset/core/full scope.
- Full remains mandatory for Config, Build.cs, Target.cs, streaming/package/cook/release/unknown-impact deltas.

### Lane C — Warehouse
- Self-hosted because it needs persistent local warehouse storage.
- Source checkout under RUNNER_TEMP.
- Downloaded warehouse payload stays under C:\actions-runner\_warehouse\ShireJourney.
- Never mutates Unreal project .git or build intermediates.

### Lane D — Runner health / branch administration
- Source checkout under RUNNER_TEMP.
- No project-workspace deletion.
- Branch cleanup is repository administration, not Unreal project ownership.

## Safety rules retained

- Exact PR head SHA is still verified.
- No heavy runtime asset synchronous loading is authorized.
- Story, save, streaming, movement and runtime audits remain mandatory for relevant deltas.
- No change converts machine-green into PIE/device/visual/performance acceptance.
- No blind binary cache restore is introduced.
- MaxParallelActions remains 1 until CPU/RAM evidence justifies a change.
- Full package/cook remains for package-critical changes.

## External engineering cross-check

The rearchitecture aligns with current GitHub Actions guidance on concurrency/cancel-in-progress and with Epic guidance that Git status participates in adaptive C++ working-set detection. Current actions/checkout and setup-python releases also reinforce that standard hosted actions are viable where account policy allows them, but this project intentionally does not depend on hosted capacity because the present account failed hosted jobs before step execution.

Community UE CI examples also emphasize incremental builds on persistent self-hosted machines. Community caching reports are mixed for Unreal Intermediate/Engine caches, so this project will not introduce aggressive cache restore until the simpler persistent-workspace design is measured.

## Next measurements before returning to feature production

1. Complete one fresh Pre-Unreal run on the isolated static checkout and record:
   - queue delay
   - exact checkout duration
   - static execution duration
2. Complete one genuine runtime C++ delta and record:
   - whether UBT says it reuses the makefile or creates a new one
   - number of actions compiled
   - C++ build seconds
3. Complete one administrative-only change and verify:
   - no Unreal Build Validation is triggered
4. Verify Warehouse/Runner Health/Branch Cleanup leave the Unreal workspace Git tree and Intermediate/Binaries untouched.
5. Only after these measurements decide whether compile parallelism or explicit caching is necessary.

## Production re-entry gate

D + Mega Asset Promotion should resume immediately after the CI architecture branch is green and the first measurements show that the runner no longer destroys its own incremental state.

Evidence status: **ARCHITECTURE REASSESSED / SOURCE CORRECTIONS IMPLEMENTED / FRESH MEASUREMENT PENDING**.
