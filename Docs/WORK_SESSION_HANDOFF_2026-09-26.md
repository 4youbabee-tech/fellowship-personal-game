# Work Session Handoff — 2026-09-26

## Purpose
This file preserves the current owner/architect conversation state so a later ChatGPT/AI session or returning developer can continue without rediscovering CI latency causes, evidence boundaries, or the active production direction.

## Active production direction
- C3/C4 foliage work is already merged.
- D — fixed-state lighting / sky / fog / low-cost water — is the next runtime production lane.
- Mega Asset Promotion may proceed in parallel through warehouse staging/intake QC, but it must not bypass provenance, format, runtime-safety or Gate 6/7 evidence.
- Story continuity, game stability, movement/traversal, save integrity, NPC/world-system coherence and target-device performance remain higher priority than administrative cleanup.
- Nonessential administrative work must not repeatedly block the production train.

## CI latency evidence already measured
Measured from GitHub Actions on 2026-09-26:

| Case | Queue / wait | Execution |
| --- | ---: | ---: |
| PR102 administrative repair | 00:04 | 13:46 |
| PR102 new-developer onboarding | 10:37 | 13:54 |
| PR101 Pre-Unreal | 05:04 | 00:48 |

The confirmed cause for the PR102 administrative/onboarding cases was unnecessary FULL Unreal classification. Files such as README and the onboarding/developer-entry helper were treated as unknown full-impact changes, so the runner repeated expensive editor build, asset import, runtime audits and packaging even though the changed files were administrative.

## CI corrections implemented in PR102
- Explicit classification exists for README/onboarding/Governor evidence helpers as non-runtime.
- There is no broad exemption for Scripts/ or Data/; mixed runtime, story, config, streaming, packaging or unknown changes still take the appropriate heavier path.
- Validation-policy-only changes may reuse a proven nearby green candidate only after checking the complete intervening delta.
- Shallow history is fetched when ancestry proof is needed.
- Nine classifier regression cases protect against incorrectly downgrading story/gameplay/config/streaming changes.
- Related administrative edits should be batched instead of producing repeated superseded full runs.

## Checkout stall root cause
Unreal #888 was created before the checkout low-speed fix. Its generated Git fetch could retry without a bounded low-speed transfer cutoff, so an old stalled download could keep the single Windows runner occupied for an unreasonable period.

The correction adds a Git low-speed boundary of 1000 bytes/sec for 20 seconds while preserving bounded retries, exact SHA verification and normal authentication/provenance requirements. The goal is to stop a dead transfer from holding the runner indefinitely; it does not weaken exact-head validation.

## Verified workflow state at handoff
- PR #102 is open and mergeable.
- PR #102 head at the time this handoff was written: `d8eaea795d19b5ca81e4aa9bff15eff90a0f4cd2`.
- Pre-Unreal #1083: SUCCESS on `b7c30909229024a9721f8b554b193c90e7f4f8c0`.
- Unreal #887: SUCCESS on `0e20fadbd420f1e4213afa49e7f5b63d96e187e5`; it still repeated a full Unreal path for an older administrative state.
- Unreal #888: CANCELLED. It had been the pre-fix stalled checkout run and was superseded.
- Unreal #889: IN PROGRESS on `d8eaea795d19b5ca81e4aa9bff15eff90a0f4cd2` when this handoff was written.
- Therefore the checkout/latency improvement is **not yet claimed as measured-success** until the corrected run completes and its actual duration/steps are reviewed.

## Engineering rule learned from repeated red runs
Do not treat every red workflow as a game regression. Classify failures first:
1. GAME / RUNTIME BUG — gameplay, movement, save, streaming, NPC/world state, import/runtime correctness.
2. VALIDATOR BUG — stale phase assumptions, duplicate truth, magic constants, false-positive policy checks.
3. CI / INFRA FAILURE — checkout/network/runner/process ownership/queue issues.
4. ADMIN / GOVERNANCE DRIFT — duplicated metadata or stale handoff fields that do not alter runtime.

Only the affected lane should be blocked. A validator or infrastructure failure must not be described as a gameplay failure.

## Root architectural correction policy
- Prefer invariants over historical phase labels.
- Do not duplicate mutable truth across multiple files when one authoritative source can be read.
- Do not hard-code counts that can be derived from manifests.
- A value derivable from source data should not be manually synchronized in a second place.
- A safe administrative change should not consume full UE4 build/import/package time.
- A runtime-impacting change must never be hidden inside a lightweight path merely to reduce CI time.
- Exact-head evidence remains required when the runtime lane changes.
- Machine-green does not imply PIE/device/visual/pacing/performance acceptance.

## Continuation instructions
When work resumes:
1. Check the latest PR #102 / #889 state first; do not assume the speedup succeeded.
2. Record the actual corrected checkout, queue and execution times before changing validation policy again.
3. If #889 fails, inspect whether the failure is GAME, VALIDATOR, INFRA or ADMIN before editing runtime code.
4. Merge PR102 only after its required evidence is green.
5. Resume D + Mega Asset Promotion from the current verified develop baseline; do not reopen C3/C4 unless concrete regression evidence requires it.
6. Continue removing duplicate truth / magic constants when they are encountered, but do not create a broad cleanup lane that delays the playable production slice.
7. Keep the owner priority: stable story/game/system integration and movement first; trivial/nonessential administration must not repeatedly consume production time.

## Evidence boundary
This handoff preserves conversation and workflow state. It is not PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED, PACING-ACCEPTED or PERFORMANCE-ACCEPTED evidence.
