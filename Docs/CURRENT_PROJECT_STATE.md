## 2026-09-24 - W00 checkpoint CP-W00-155: final consolidated repair-closure wave

Head `f524a83cd39510b956e4977571448d43100b628d` passed **Unreal #624 SUCCESS** and **Warehouse #205 SUCCESS**. Unreal #624 completed UE4.27.2 build/import, Automation, startup, P1C01-P1C08, state, transitions, faults, pending, persistence-edge and zero-warning-debt checks; material persistence reported `missing=0 tracked=225`.

Pre #789 failed at one governance invariant only: `PG-078: tracked unfinished requirement snapshot is stale`. The exact mismatch is `REQ-ORG-001`, correctly VALIDATED in ProjectGovernor but still present in MasterExecutionRoadmap's unfinished snapshot. CP155 reconciles that snapshot without weakening the validator.

The same final wave adds explicit already-resident bank recommit runtime evidence and a fail-safe Unreal fast path for governance/docs-only deltas whose direct parent already has successful Unreal evidence. Any source/runtime/CI/config/asset or unknown delta still runs the full UE4.27.2 chain.

This is the last planned root-repair wave. CP155 gets one full run because it changes CI/runtime audit contracts. After it is green, root-code/validator/Governor cleanup stays closed unless a concrete new regression appears; W00 proceeds only to packaged Data, real audio, target-device profiling and human PIE/pacing/visual acceptance.

No PIE/device/visual/performance acceptance is claimed here.

## 2026-09-24 - W00 checkpoint CP-W00-154: exact-head machine-green reconciliation

Exact head `ab7889d6b2dafc059220a0c0a3dc63decfe6b72e` is now **STATIC-VALIDATED + COMPILE-TESTED + HEADLESS-RUNTIME-VALIDATED**: **Pre-Unreal #788 SUCCESS** (run 35929433094), **Unreal Build #623 SUCCESS** (run 35929433086), and **Warehouse #204 SUCCESS** (run 35929433089).

Pre #788 completed the full project-structure/Governor/asset-quality/readiness/deep/unit-test chain. Unreal #623 completed exact checkout, migrated-layout preparation, UE4.27.2 verification, MSVC setup, clean intermediates, ShireJourneyEditor build, production asset import, Automation Framework QA, startup smoke, P1C01-P1C08 headless chapter audit, route/story state roundtrip and warning-debt guard. Warehouse #204 correctly detected no staging-required delta and skipped heavy provider stages.

The Public/Private migration and its known validator/persistent-runner correction families are therefore **machine-accepted on CP-W00-154**. Do not reopen root-code/validator/Governor cleanup unless a new concrete regression appears. W00 remains open only for packaged Data JSON runtime proof, real authored audio playback, target-device profiling and chapter-specific human PIE/pacing/visual acceptance.

No **PIE-TESTED**, **DEVICE-TESTED**, **VISUALLY-ACCEPTED** or **PERFORMANCE-ACCEPTED** claim is made by this machine evidence.

## 2026-09-24 - W00 checkpoint CP-W00-153: migration-consumer and persistent-runner repair

CP152 head `9acc72b16e058a422428389fcefeb9af12fa0e98` has the intended physical Git tree: zero flat runtime .h/.cpp files, 32 headers under `Public/<Domain>` and 30 implementations under `Private/<Domain>`. Warehouse #202 succeeded.

Its proof failed in two concrete migration-tooling families. Pre #786 still had historical direct reads such as `Source/ShireJourney/ShireGameMode.cpp`, so missing-file reads cascaded into false PG-109/129/131/133/136/137/138/140/142 failures. Unreal #621 reached UHT and failed on duplicate leaf headers because the persistent self-hosted worktree retained the old flat headers as **untracked leftovers** after the tracked files moved.

CP153 fixes both systemically without changing gameplay: all real Pre-Unreal source reads resolve migrated basenames, the central runtime-evidence registry points at actual `Private/<Domain>` paths, the streaming source-contract test is layout-aware, and the Unreal workflow removes only obsolete architecture-mapped legacy files after confirming their migrated targets exist.

Status: **SOURCE-LAYOUT INTACT / MIGRATION INTEGRATION REPAIRED / EXACT-HEAD VALIDATION PENDING**. No PIE/device/visual/audio/package acceptance is claimed.

## 2026-09-24 - W00 checkpoint CP-W00-152: isolated Public/Private runtime-source migration

Exact CP151 head `92f6d3aaad79f33eaf2385de292e6886d2c1b5da` is the new fully machine-green baseline: **Pre-Unreal #785 SUCCESS + Unreal #620 SUCCESS + Warehouse #201 SUCCESS**. The full static/governor/asset/readiness/deep/unit-test chain passed, and Unreal #620 passed compile/import/Automation/startup/chapter/state/transition/fault/pending/persistence-edge/warning-debt coverage.

With the correction loop green, CP152 performs the already-approved architecture-only migration: all 62 runtime .h/.cpp entries move from the module root to their mapped `Public/<Domain>` and `Private/<Domain>` paths. Gameplay source blobs are unchanged. Build.cs no longer exports the entire module root; it exposes only explicit public domain include roots. Pre-Unreal and DeepProjectAudit now resolve runtime filenames recursively, and PG-154 rejects flat-root regression.

CP152 is **SOURCE-LAYOUT-MIGRATED / EXACT-HEAD VALIDATION PENDING** until fresh Pre-Unreal and UE4.27.2 proof. No PIE/device/visual/audio/package acceptance is claimed.

## 2026-09-24 - W00 checkpoint CP-W00-151: handoff evidence-lineage correction

Exact CP150 head `2259242a772d3dd21a90cc10a8a4a2761be3b3dd` passed **Unreal #619 SUCCESS** and **Warehouse #200 SUCCESS**. Pre-Unreal #784 also passed **PRE-UNREAL CORE VALIDATION**, proving the prior PG-056 NameError is gone, then stopped in `project_governor.py` on one data-lineage invariant:

`Legacy verified handoff must refer to the same last-green baseline`.

The validator is correct. `session_handoff.source_head` is the verified historical baseline and must equal `validation_snapshot.last_green.sha`; the newer partially proven candidate belongs in `validation_snapshot.latest_observed`. CP151 corrects only that Governor data and does not weaken or duplicate the handoff validator.

Status: **SOURCE/DATA-REPAIRED / EXACT-HEAD VALIDATION PENDING**. No PIE/device/visual/performance/audio-playback claim is added.

## 2026-09-24 - W00 checkpoint CP-W00-150: close the CP149 refactor regression

Exact CP149 head `e0b66dbccdf9e91f3cd6af0190008cf58ca31198` produced **Unreal #618 SUCCESS** and **Warehouse #199 SUCCESS**. Pre-Unreal #783 failed before the later static suite because PG-056 still referenced the local symbol `governor_mode_id`, which CP149 had intentionally removed while centralizing development-mode validation.

This is a validator execution regression, not evidence of a new gameplay/runtime defect. CP150 removes the orphan alias completely: PG-056 reads `development_mode.id` directly from the Governor data only to decide whether the historical PIE verification-freeze guard is active. The data-owned mode contract remains the sole validation authority.

CP150 status is **SOURCE-REPAIRED / EXACT-HEAD VALIDATION PENDING**. No PIE/device/visual/performance/audio-playback claim is added.

## 2026-09-23 - W00 checkpoint CP-W00-149: data-owned development-mode validation

CP-W00-148 parent `32af3140d1d297283de640144a58c3b32133d3d1` produced a clean split result: Unreal #617 SUCCESS and Warehouse #198 SUCCESS, while Pre-Unreal #782 stopped immediately on two PG-033 validator errors. No C++/runtime failure was reported by #617.

Root cause: PG-033 carried a second hard-coded list of acceptable development modes and inferred manual-proof honesty by searching rule prose for words such as PIE/evidence/device/visual/performance. The Governor's legitimate `W00_ARCHITECTURAL_STABILIZATION` mode therefore looked invalid to the validator.

CP-W00-149 moves mode IDs, supersedes relations and manual-only acceptance labels into structured `development_mode_contract` data owned by ProjectGovernor. Both Pre-Unreal and `project_governor.py` consume one shared `governance_contracts.py` helper, and unit tests guard unknown modes, supersedes drift, missing manual labels and prose-only fake proof.

Status of this child checkpoint: **SOURCE-REPAIRED / EXACT-HEAD VALIDATION PENDING**. No PIE/device/visual/performance/audio-playback acceptance is claimed and no completeness percentage changes.

## 2026-09-23 - W00 checkpoint CP-W00-148: Governor execution-truth hardening

Exact parent `96398e7cc48277324113c7879a8d28e3b659757e` is **STATIC-VALIDATED + COMPILE-TESTED + HEADLESS-RUNTIME-VALIDATED**: Pre-Unreal #781 SUCCESS, Unreal #616 SUCCESS and Warehouse #197 SUCCESS. #616 passed UE4.27.2 compile/import, Automation 2/2, startup, P1C01-P1C08, state/continuous-transition/fault/pending/persistence-edge modes and warning-debt guard. #197 detected no staging-required delta and skipped heavy provider staging by design.

The screenshot/log with `ShireRollbackAudit ... revisionAdvanced=no` belongs to older #615 on `6944cc0...`. #616 on the current parent passed the corrected split semantics.

The next audit found governance drift, not a gameplay regression: stale PR #61/#53 metadata, `VISUAL_PRODUCTION_FIRST`, broad production actions, direct-develop workflow text and a source hierarchy that could make supporting docs/backlog look authoritative despite the W00 freeze.

CP-W00-148 centralizes active-gate-first execution, explicitly freezes B1/B2/B3, reconciles PR #67/branch metadata and adds PG-150 so supporting management surfaces cannot drift silently. This child checkpoint is **SOURCE-REPAIRED / EXACT-HEAD VALIDATION PENDING** until fresh CI proves it.

No PIE/device/visual/pacing/audio-playback acceptance is claimed and no production-completeness percentage is increased.

## 2026-09-23 - W00 checkpoint CP-W00-147: separate invalid-request preflight from real rollback

Two reds were collected before this repair.

Pre-Unreal #780 on `6944cc0f...` failed PG-136 for `StartExperience`, but source inspection shows the authoritative subsystem identity still follows the correct order: transition intent is broadcast before bare `CurrentRouteId / CurrentChapterId / CurrentEpisodeId / PlayableCharacterId` mutation. The helper was falsely treating `TargetExisting->CurrentChapterId` and related route-progress sanitation fields as authoritative subsystem mutation. The structural helper is now qualifier-aware: writes through another object are ignored, while bare and `this->` member writes still count. DeepProjectAudit consumes the same helper.

Unreal #614 on parent `333cbd0d...` exposed a second stale assumption. The new identity preflight correctly logged `ShireExperienceIdentity: rejected ... chapter=P1C99` before any transition request. The legacy fault audit then failed only because it expected `revisionAdvanced=yes`. That expectation is now wrong by design: a request rejected before transaction publication must leave identity, player state, NPC/LivingWorld authority and world revision unchanged. Real rollback remains tested separately by the forced valid-bank P1C02 async streaming failure, which must restore the origin and advance revision.

Accordingly the fault evidence contract now distinguishes `ShireInvalidTransitionAudit` (rejected-before-transaction, revision unchanged) from `ShireStreamFailureAudit` (entered transaction, rollback, revision advanced). No production revision is artificially bumped merely to satisfy an obsolete test.

Status of CP-W00-147: **SOURCE-REPAIRED / FRESH EXACT-HEAD PROOF PENDING**. The last exact head with both static and Unreal success remains `3ea40ce1...` (#778/#613). W01 remains blocked.

## 2026-09-23 - W00 checkpoint CP-W00-146: PG-136 false red fixed at the validator architecture layer

Pre-Unreal #779 on `333cbd0dd51d82215d4b9cc94793be507299f349` failed with `PG-136 StartChapter must publish transition intent before logical chapter mutation`. Direct source inspection shows the production transaction order is already correct: `OnWorldTransitionRequested.Broadcast(...)` executes before the authoritative `CurrentChapterId`, `CurrentEpisodeId`, and `PlayableCharacterId` assignments. The red was caused by validator drift: PG-136 searched specifically for the obsolete text `CurrentChapterId = ChapterId;`, while CP-W00-145 correctly canonicalized the destination through `TargetChapterId` and now assigns `CurrentChapterId = TargetChapterId;`.

No C++ transaction reorder is made. CP-W00-146 fixes the root validation family instead. `Scripts/source_contracts.py` provides a reusable structural check that finds protected member assignments regardless of RHS spelling, ignores comments/string literals, and proves the transition signal occurs first. PG-136 uses the same helper for StartChapter and StartExperience, and a dedicated unit suite proves alias-RHS changes pass while mutation-first ordering fails.

At reconciliation time Unreal #614 was still running: build/import/Automation/startup/chapter sweep had already passed, with the state/edge phase still active; Warehouse #195 remained queued. Therefore CP-W00-146 is **SOURCE-REPAIRED / FRESH EXACT-HEAD PROOF PENDING**. W01 remains blocked and no production-completeness percentage is increased.

## 2026-09-23 - W00 checkpoint CP-W00-145: large root-cause closure wave

Exact parent `3ea40ce1d68b6d5b961ed56a00117a75528e833e` is **STATIC-VALIDATED + COMPILE-TESTED + HEADLESS-RUNTIME-VALIDATED** by Pre-Unreal #778 and Unreal #613. #613 passed UE4.27.2 compile/import, Automation 2/2, startup, P1C01-P1C08, state, continuous transitions, rollback/stream-failure faults, delayed pending authority, persistence edges and all tracked project warning-debt ceilings at zero.

Warehouse is still an infrastructure lane, not a gameplay regression. Push run #192 failed before project code on self-hosted network/DNS instability while acquiring checkout/repository data. PR run #193 then checked out successfully but failed immediately in `Detect current warehouse delta`: Windows PowerShell refused GitHub's generated temporary script under the machine execution policy (`PSSecurityException`, scripts disabled). Provider staging never began.

CP-W00-145 folds several remaining W00 families into one guarded repair wave rather than waiting for them to surface one by one. Warehouse inline PowerShell now runs with explicit `-ExecutionPolicy Bypass`; marketplace `actions/checkout` is removed from that lane and replaced by bounded exact-head native Git retries. The experience-state contract is also centralized: authoritative Gandalf identity is `GandalfParallel / P1C01 / P1G01_Isengard / Gandalf`, matching the existing production data. Direct malformed requests fail closed before transition publication, while save/route-progress restore repairs known legacy aliases and rejects unsupported identities before publication.

Persistence coverage is deepened from a synthetic stale callback to a real queued async-disk race. The CI-only edge audit now schedules two actual `AsyncSaveGameToSlot` writes from one committed world revision, crosses to another committed world, defers completion processing deterministically, and requires both writes to succeed while neither stale callback applies checkpoint effects. A separate static guard also compares every runtime C++ `Data/*.json` load with `ShireJourney.Build.cs` `RuntimeDependencies` so packaged-data declarations cannot drift unnoticed.

Status of the new CP-W00-145 head is **SOURCE-REPAIRED / FRESH EXACT-HEAD PROOF PENDING**. W01 remains blocked; no production-completeness percentage is increased.

## 2026-09-23 - W00 checkpoint CP-W00-144: warehouse red isolated from gameplay and repaired as an execution-family defect

Exact parent `67ebc4ee4142c4df9c479c6b326631b767bc903a` is **STATIC-VALIDATED + COMPILE-TESTED + HEADLESS-RUNTIME-VALIDATED** by Pre-Unreal #777 and Unreal #612. Warehouse #191 alone failed after 32m57s. GitHub's structured job record ended with `Stage first Poly Haven CC0 batch` still marked `in_progress`; OpenGameArt/Quaternius/ambientCG/Kenney/KayKit and the final inventory audit never started, and the job exposes no finalized log blob. Therefore no unsupported claim is made about a specific provider exception. Previous Warehouse #190 completed the full provider chain successfully.

The systemic issue is clear even without the missing terminal log: pull-request path matching is cumulative, so the heavy warehouse workflow can run again on stabilization commits that did not change warehouse inputs; provider scripts also used raw web calls and re-queried providers despite persistent receipts. CP-W00-144 adds a current-update delta gate, reusable receipt validation, a shared bounded retry/timeout layer, and atomic `.partial` downloads before rename. A provider/network interruption can no longer leave a partial file looking complete, and unrelated code commits should skip acquisition instead of spending many minutes touching external providers.

PG-144 statically prevents warehouse provider scripts from bypassing the shared network helper and requires every heavy workflow step to be delta-gated. Status of the new head is **SOURCE-REPAIRED / FRESH EXACT-HEAD PROOF PENDING**. W01 remains blocked.

## 2026-09-23 - W00 checkpoint CP-W00-143: semantic evidence-contract consolidation

Parent head `aa8f80c89de1193728c1ff82b5876fdac0fdc7d3` split again: Warehouse #190 SUCCESS, Unreal #611 SUCCESS, Pre-Unreal #776 FAILURE. #611 gives exact-parent **COMPILE-TESTED + HEADLESS-RUNTIME-VALIDATED** evidence for compile/import, Automation 2/2, startup, P1C01-P1C08, state, transitions, rollback/stream-failure faults, delayed pending authority and persistence edges. The warning-debt gate remained zero for all tracked project categories, including the streaming-pool precedence warning.

#776 exposed the remaining root of the repeated static reds. PG-070/074/079/080 and PG-129 still assumed that exact evidence strings physically lived in `runtime_smoke.py`. After PG-142 correctly moved those strings to a central registry, those older guards became stale even though the real runtime was green. CP-W00-143 therefore deepens the repair: `runtime_audit_contracts.py` now owns semantic evidence IDs, exact marker text, mode membership and C++ source anchors. Static validators ask for semantic IDs such as ring continuity, persistence commit, rollback or stale-checkpoint proof rather than searching another Python file for copied text.

The same wave migrates DeepProjectAudit and runtime unit tests to the semantic registry and strengthens the de-duplication test so exact runtime evidence text is forbidden in all Python consumers. This is intended to eliminate the recurring class where a correct C++/runtime change turns Pre-Unreal red because a second or third copy of the old marker survives elsewhere.

Status of CP-W00-143: **SOURCE-REPAIRED / FRESH EXACT-HEAD PROOF PENDING**. W00 remains open; W01 remains blocked.

## 2026-09-23 - W00 checkpoint CP-W00-142: validation-contract consolidation wave

Parent head `7636c7779156831660964cc5d44125efa4b480d1` produced a split result: Warehouse #189 SUCCESS, Unreal #610 SUCCESS, Pre-Unreal #775 FAILURE. #610 is concrete **COMPILE-TESTED + HEADLESS-RUNTIME-VALIDATED** evidence for that exact parent: UE4.27.2 compile/import, Automation 2/2, startup, P1C01-P1C08, state, transitions, rollback/stream-failure faults, delayed pending authority and the persistence-edge sweep all passed. Warning debt also reported `Streaming pool scalability override warnings = 0`. #775 failed on one stale static contract: PG-140 still searched for the old formatted checkpoint log template after #609 forced the C++ logger to split PASS/FAIL into static UE_LOG branches.

That failure belongs to a recurring family: runtime evidence strings were copied independently into C++, `runtime_smoke.py`, `pre_unreal_validate.py` and unit tests. CP-W00-142 therefore does not patch one string. It introduces `Scripts/runtime_audit_contracts.py` as the single Python contract owner for required markers, mode arguments, log names, source anchors and warning-debt runtime log scope. Consumers import the registry; PG-124/133/136/137/138/139/140 consume registry semantics; a dedicated contract unit suite checks source anchors, state-mode execution and de-duplication.

Status of the new CP-W00-142 head is **SOURCE-REPAIRED / FRESH EXACT-HEAD PROOF PENDING**. W00 remains open and W01 remains blocked.

## 2026-09-23 - W00 checkpoint CP-W00-141: #774/#609 root causes repaired at source

Candidate `621ad8617f7ebf1b973887fb61b4f46672d1226c` did **not** pass validation. Pre-Unreal #774 reached `PRE-UNREAL CORE VALIDATION PASSED`, then ProjectGovernor failed because CP-W00-140 had replaced `session_handoff` without its required `validation_snapshot.last_green/latest_observed` exact-SHA/run-ID/status records. Unreal #609 reached real UE4.27 compilation and failed first at `ShirePlayerCharacter.cpp:1954`: a runtime ternary was used as the `UE_LOG` verbosity token. UE4.27 requires a static verbosity token; the later parser/member diagnostics are treated as cascade from that root error.

CP-W00-141 restores evidence lineage: last green remains `80fc54dc...` with Pre-Unreal #773 / Unreal #608, while latest observed records `621ad861...` with #774/#609 FAILURE. The checkpoint audit now logs through explicit Display/Error branches. PG-141 rejects future conditional `UE_LOG` verbosity before engine compilation, and the handoff regression tests explicitly reject checkpoint rewrites that drop `validation_snapshot`.

Status: **SOURCE-REPAIRED / FRESH EXACT-HEAD PROOF PENDING**. W00 remains open and W01 remains blocked. No COMPILE-TESTED / STATIC-VALIDATED claim is made for CP-W00-141 yet.

## 2026-09-23 - W00 checkpoint CP-W00-140: exact-head #608 green; closure/validation-authority wave started

Exact PR #67 head `80fc54dc4e4571e57206bef28cc809e2dcb3ec62` completed Pre-Unreal #773, Warehouse #187 and Unreal Build #608 successfully. #608 compiled UE4.27.2 C++, imported production assets, passed ShireJourney.QA 2/2, startup, P1C01-P1C08, state persistence, continuous transitions, rollback fault injection, forced valid-bank stream failure, delayed pending-window authority and the zero-tolerance project warning-debt categories. This evidence is **COMPILE-TESTED + STATIC-VALIDATED + HEADLESS-RUNTIME-VALIDATED** for that exact SHA only. It is not PIE/device/visual/performance/audio-playback acceptance.

The #608 log exposed a separate low-spec configuration authority defect: `DefaultEngine.ini` hard-set `r.Streaming.PoolSize=900`, so UE reported that TextureQuality scalability pool values were ignored as lower priority. The W00 closure wave removes the project-level override so `DefaultScalability.ini` owns 600/800/1000 MB tiers, adds a zero-tolerance warning guard for this precedence warning, and expands runtime warning-debt scope to transition/fault/pending/persistence-edge logs instead of only startup/chapter/state logs.

PG-140 adds deterministic headless regression coverage for two persistence edges that were previously source-only: a legacy P1C01 terminal save must repair to one final canonical P1C02 publication/world commit, and a stale checkpoint completion carrying an older world revision must not heal or message the newer committed world. The real queued asynchronous write-across-revision case remains separately pending; this new callback guard does not overclaim that disk race.

This checkpoint is the durable restart point if chat is lost. W00 remains open and W01 remains blocked. The new source/config wave is **SOURCE-REPAIRED / FRESH EXACT-HEAD PROOF PENDING** until its own Pre-Unreal and Unreal runs complete.

## 2026-09-23 - Unreal #606 failure-path evidence exposed two more W00 contracts

Unreal Build #606 on `1fdca1166cfd72099a42bbd02c9355b5f035562d` passed UE4.27.2 compile, production import, Automation, startup, P1C01-P1C08, state persistence and continuous transitions, then failed only in the new rollback fault audit. The failure was `freshSnapshot=no` while the same engine log showed rollback applying `health=67.0 stamina=54.0 resolve=43.0 supplies=2`, movement released, NPC context restored, LivingWorld synchronized and world revision advanced. The test sampled stamina/resolve after normal life ticking had resumed, so those values had legitimately begun changing. The fix is not to loosen rollback correctness: rollback now emits a dedicated `ShireRollbackSnapshotApplied` marker at the exact application point, while the later timer checks only stable health/supplies plus committed-system invariants.

The same failure-path review found two additional systemic gaps. First, save restore changes world identity without necessarily calling `StartChapter`/`StartExperience` before persistence mutation, so it did not share PG-136's request-time rollback snapshot boundary. Save restore now begins the persistence transaction, publishes `PreparePersistenceWorldTransition` while the old logical world is still intact, and only then applies restored quest/route state. A failed save-driven world swap therefore has the same exact-origin rollback semantics as a normal chapter transition.

Second, `ShireChapterAssetStreamingSubsystem` still treated a missing/empty bank or unavailable async handle as a compatibility success, and async completion did not verify that every bank asset actually resolved. That could allow a valid logical chapter to commit with fallback geometry rather than treating residency failure as a transaction failure. The next source wave removes that compatibility-success path: missing/empty banks, invalid handles and unresolved assets publish `OnChapterAssetsFailed`; ChapterWorldRouter keeps the previous resident bank pinned and executes atomic rollback. A CI-only forced P1C02 async failure proves the old bank remains resident and player/NPC/LivingWorld state returns to the exact origin.

The same wave adds a bounded non-blocking CI delayed-ready hook. A dedicated pending-transition audit holds P1C02 ready publication for two seconds and requires, during the window, destination logical state to remain unusable by gameplay/NPC logic while LivingWorld remains on the prior committed revision. It then requires destination context, LivingWorld and player controls to move together only after final commit.

PG-137 covers save-restore pre-mutation ownership and delayed transition authority. PG-138 covers fail-closed bank residency and streaming failure rollback. These changes are **source-level pending a fresh exact-head engine run**. Pre-Unreal #772 is green for the current PG-136 head, but no newer engine run yet proves PG-137/PG-138. W01 remains closed.

## 2026-09-23 - Pre-Unreal #771 diagnostic correction for PG-136 fault injection

Pre-Unreal #771 on `1fdca1166cfd72099a42bbd02c9355b5f035562d` failed before engine validation. The validator correctly rejected literal test-only references `P1C99` and `CI_InvalidTransition` as unknown production chapter/quest IDs, and the new PG-136 ordering check accidentally matched the fail-safe no-subsystem hold rather than the normal transition hold. The fault test now constructs its unsupported chapter ID at runtime and reuses the current authored quest identity, so production-reference validation remains strict. PG-136 now checks snapshot ordering against the normal transition hold while preserving the no-subsystem fail-safe hold.

This is a validation/harness correction only. Unreal #606 for the failed static head is not acceptance evidence, and the PG-136 runtime repair still requires a fresh exact-head run.

## 2026-09-23 - Unreal #605 exact-head green; rollback freshness root cause exposed and repaired at source

Exact head `ddd0957d6201c8bf553825acd671c98a9be545ef` completed Pre-Unreal #770, Warehouse #184 and Unreal Build #605 successfully. #605 passed UE4.27.2 C++ build, production import, Automation, startup, the aggregate P1C01-P1C08 sweep, persistence/state roundtrip, continuous transitions and the zero-tolerance warning gate. The warning gate reported zero missing smoothing groups, zero degenerate tangent bases, zero nearly-zero tangents/binormals, zero missing production master surface/world packages, zero optional audio/rig debt, zero defaultMat references, zero light-mobility warnings and zero NPC spawn-collision failures. This is exact-head engine evidence for `ddd0957...` only; it is not PIE/device/visual/performance acceptance.

Continued transaction simulation found a deeper rollback freshness defect that the green path did not exercise. `LastCommittedRollbackSnapshot` was refreshed when a world committed, but not necessarily at the instant a later transition was requested. If the player advanced quest/NPC/player-life state within a chapter and the next world swap failed, rollback could restore the older chapter-commit snapshot instead of the exact state immediately before the failed request. A second defect existed in the unsupported destination path: `CommitChapterWorld` cancelled pending work and returned without restoring the logical origin, potentially leaving the player hold active around an invalid destination.

The source repair introduces a native pre-mutation `OnWorldTransitionRequested` boundary in `UShireQuestSubsystem`. `StartChapter` and `StartExperience` publish the intended destination before mutating logical chapter/route identity. `ChapterWorldRouter` subscribes at that boundary, captures a fresh rollback snapshot only when the current origin is fully committed, then raises the world/gameplay hold before destination mutation. Pending/uncommitted requests cannot overwrite that origin snapshot. Unsupported chapter/route pairs now execute the same atomic rollback path instead of clearing pending IDs and returning.

The route/world support contract is also explicit: `FrodoMain` accepts P1C01-P1C08; `GandalfParallel` accepts its current P1C01/Isengard world identity. A new CI fault mode deliberately requests unsupported P1C99 after setting distinct live player values and requires rollback to restore exact origin identity, player-life state, NPC committed context, LivingWorld revision and movement release. Required marker: `ShireRollbackAudit: PASS unsupported-request restored=yes movementReleased=yes freshSnapshot=yes npcContext=yes livingWorld=yes`.

PG-136 and the deep-project audit guard the pre-mutation snapshot, rollback-on-rejection and fault-injection evidence chain. This new wave is **source-level pending fresh exact-head validation**; #605 remains the proof boundary for its parent head. W01 remains closed and the production percentage is unchanged.

## 2026-09-23 - PG-135 queued checkpoint snapshot ownership hardening

Pre-Unreal #769 on exact head `e8b69e5b61f94ada054cbe5c7b1ed6408796c43e` passed every static gate, including the now-strict source asset audit with zero degenerate-UV assets, zero opposed-normal assets and zero structural errors. Unreal #604 had not completed when this follow-up source audit began.

A further save-path simulation found a distinct async race that the PG-133 callback-origin guard did not fully close. When one automatic checkpoint save was already in flight, a second checkpoint stored only its `CheckpointId`. After the first callback completed, the second request called `SaveAutomaticCheckpoint` again and rebuilt its snapshot from whatever live world happened to exist at that later time. If a chapter transition occurred meanwhile, an old checkpoint ID could therefore serialize destination-world state, or the queued checkpoint could be discarded because the transition hold was active.

PG-135 changes queued checkpoint ownership from ID-only to snapshot+origin. The second checkpoint now captures its full `UShireSaveGame` snapshot plus chapter, route, episode and committed world revision at the instant the checkpoint is reached. The queued request is dispatched directly from that captured snapshot after the current async write completes; it is never reconstructed from later live state. Its completion can still write the disk snapshot after a transition, while the existing origin/revision guard prevents old-world health/resolve/HUD effects from mutating the newer committed world. Both in-flight and queued snapshots are held by UPROPERTY references so GC cannot invalidate them during async serialization.

PG-135 and deep-project audit now reject any return to ID-only queued checkpoint reconstruction. This is **source-level pending fresh exact-head validation** and does not advance W00 or production completion.

## 2026-09-23 - Pre-Unreal #768 exposed the broader tangent-basis family; full source wave + strict CI

Exact head `be5914d9b94d8e8bb5e25de88edab8a0dc089baf` passed the core validator, governor, source asset-quality script and production-readiness stages, then deep-project audit failed on one stale diagnostic token. More importantly, the asset-quality log exposed that the earlier three Unreal warning identities were only the visible edge of a broader authored-source class: 23 additional project-owned static OBJ assets contained degenerate UV triangles, and 7 of those also contained normals opposed to geometric face direction.

This is being handled as one root-cause wave, not as 23 future warning patches. Every asset named by #768 is normalized to explicit triangulated face-local UVs and face-aligned normals. The set includes Balrog/Lurtz static proxy pieces, the Watcher tentacle proxy, Isengard industrial/static structures and Shire props. These remain static/non-animated OBJ assets; no exception is made to the final animated skeletal-FBX contract.

The CI contract is also corrected. `asset_quality_audit.py` previously printed structural `ERROR:` lines but the Pre-Unreal workflow invoked it without `--strict`, so that step still appeared green. The workflow now runs `python Scripts/asset_quality_audit.py --strict`. PG-134 and deep-project audit both check that strict mode remains wired, so structural asset errors cannot silently become advisory again.

The deep-audit diagnostic token is synchronized with the real opposed-normal error wording. No warning ceiling is raised and no W01 work is opened. This wave remains **SOURCE-REPAIRED / FRESH EXACT-HEAD PROOF PENDING**.

## 2026-09-23 - Pre-Unreal #767 exposed a validator self-check mismatch, not a project defect

Exact head `274b5d0dfd12d57e9250001409ea28e43e56d41c` entered the PG-134 tangent-space repair wave. Pre-Unreal #767 stopped in the core validator with one error before the asset-quality stage. The cause was internal validator drift: PG-134 searched for the phrase `opposes geometric face normal` while the source audit deliberately emits `oppose the geometric face normal`. The guarded behavior was present; the literal self-check was stale.

The PG-134 token is synchronized with the actual source-audit contract. The early Pre-Unreal failure block is also changed to print every accumulated error before exit, matching the later failure block, so future validator failures are diagnostic rather than opaque.

This is a validator-source correction only. It does not upgrade the PG-134 mesh repair to engine-proven status; Unreal #602 on the parent head remains separate evidence.

## 2026-09-23 - Unreal #601 narrowed W00 to three source-mesh tangent defects; PG-134 repairs source data

Exact head `34a9a2a8b2cf8f944ce4eae7e90fc7492809b9ab` reached substantially farther than the preceding failed heads. Unreal Build #601 completed UE4.27.2 C++ build, production import, Automation, startup, aggregate P1C01-P1C08 runtime, state roundtrip and continuous-transition runtime. The final warning-debt gate failed with exactly three unique nearly-zero tangent identities and the same three nearly-zero binormal identities: `SM_Balrog_Wing`, `SM_Lurtz_Blade`, and `SM_Isengard_IndustrialPitRim`. Missing smoothing groups, degenerate tangent bases, missing production master surface, missing runtime world packages, optional audio/rig debt, defaultMat references, light mobility warnings and NPC spawn collision failures were all zero in that gate.

Source analysis isolated actual asset-data causes instead of relaxing the zero-warning policy. `SM_Balrog_Wing` and `SM_Lurtz_Blade` each contained four UV-degenerate triangles, which makes tangent derivation singular. `SM_Isengard_IndustrialPitRim` contained authored normals that oppose the geometric face direction on many triangles. These three project-owned procedural static OBJ sources are repaired with face-local non-degenerate UVs and face-aligned normals. This is an asset-source correction, not an animated-OBJ exception; final animated characters/creatures remain skeletal FBX only.

The source-quality audit is also hardened so this class cannot silently return: degenerate UV triangles are structural errors, and strongly opposed/zero authored normals are structural errors before Unreal import. PG-134 requires both the guard and the repaired face-local basis. Warning ceilings remain zero.

Pre-Unreal #766 separately failed because PG-037 still searched for the old async-checkpoint completion log format after PG-133 added `stateApplied` and `sameCommittedContext` evidence fields. The validator is updated to require the new stronger completion marker rather than reverting the runtime guard.

Current status for this new wave is **source repair pending fresh exact-head proof**. #601 evidence remains valid only for `34a9a2a8...`; it does not prove the new mesh repairs. No PIE, device, visual or performance acceptance is claimed.

## 2026-09-23 - Unreal #599 compile failure exposed API ownership defect; PG-133 transaction wave

Exact head `cb8c789aff25d2d1f53c0bc7e37f47fe92607eeb` passed Pre-Unreal #764, then Unreal Build #599 failed during UE4.27.2 C++ compile at `ShireNPC.cpp(1394)`: `UShireNPCContextSubsystem::IsLogicalWorldContextCommitted` was called by the named-NPC runtime while still declared private. Import, Automation and runtime stages were skipped, so #599 provides no evidence for those stages.

The compile root cause is corrected by making the read-only committed-context query part of the public NPCContext API while keeping committed-state mutation owned by the subsystem/router contract. A broader source simulation then found that the PG-131 world barrier still began too late: logical quest identity could advance and asynchronous preload could start before `SetPlayerWorldHold(true)`. The router now raises the authoritative hold at destination request time, not at destination construction time. Rapid A -> pending B -> A cancellation releases the hold only after stale async work is cancelled and the exact old world identity is again committed. Transition CI now requires one marker proving both held-during-swap and cancel-release.

Persistent NPC memory aging is moved out of `StartChapter` into `CommitWorldBoundState`, called only after destination world/context commit. Restore-time NPC memory pruning is likewise deferred until the final canonical world commit. This prevents destructive persistent-state housekeeping from running against an uncommitted or intermediate repaired chapter.

Async checkpoint completion is now origin-bound. The save captures chapter, route, episode and world revision when scheduled; a late callback may still complete its disk write, but health/stamina/resolve healing and HUD success effects are applied only if the callback still belongs to the exact same committed world revision. This closes cross-transition completion mutation without turning asynchronous disk I/O back into synchronous loading.

Ambient social partner evaluation now uses one actor traversal instead of two, and ambient/named/enemy/mythic/Black Rider context-dependent logic is held behind the committed gameplay barrier during world swaps. This is architecture/performance hardening only; no FPS or device-performance claim is made.

PG-133 plus deep-project audit guards these contracts. This new wave is **source-level pending fresh exact-head validation**. W01 remains closed; no completion percentage is increased.

## 2026-09-23 - Restore repair ordering hardened before final world publication

A further source simulation found a deeper save/restore race that was not covered by the earlier atomic restore patch. `CommitPersistenceRestore(true)` previously cleared the restore-in-progress flag and published `OnExperienceChanged` / `OnChapterChanged` before broadcasting `OnQuestStateRestored`. The StoryFlow legacy-repair handler therefore could run only after the router had already seen and potentially committed an intermediate legacy chapter/route identity. On already-resident banks this could become a synchronous double-commit window.

The transaction is now ordered as: rebuild all persistence domains -> invoke the legacy-repair hook while persistence broadcasts remain suppressed -> let `StartChapter`, `StartExperience`, and `StartQuest` canonicalize silently -> release the restore barrier -> publish exactly one final repaired experience/chapter/quest snapshot. `StartExperience` also no longer captures the current pre-commit player transform into RouteProgress while restore is in progress.

Player health/stamina/resolve/supplies are now restored before the final persistence publication because a matching resident bank can commit synchronously from the final broadcast and capture a rollback snapshot immediately. This prevents a rollback snapshot from containing restored quest state paired with stale player-life state.

PG-132 and the deep-project audit enforce the repair-before-publish ordering and player-life-before-commit invariant. This wave is source-level pending fresh exact-head validation; no new compile/runtime acceptance is claimed yet.

## 2026-09-23 - Pre-Unreal #762 test-harness regression isolated during transaction-barrier wave

On exact head `7cb6ccf8e3e5d29c13048cb5eb9862b2268bd18a`, Pre-Unreal #762 failed in `test_runtime_smoke.py`, not in project structure/deep audit. Two harness defects were introduced while extending transition evidence: the new test referenced `runtime_smoke.required_markers` although only `required_markers` was imported, and the older transition test still assumed the mode had exactly one required marker. Both are corrected so transition mode requires the complete marker set, including `ShireTransitionBarrier: PASS held-during-swap=yes`.

Unreal #597 was still compiling this SHA when the harness correction was prepared. Therefore #762 is not treated as a gameplay/runtime failure, and no engine acceptance is inferred for the follow-up head until fresh workflows run.

## 2026-09-23 - Unreal #596 compile blocker isolated; world-transaction mutation barrier added

Exact head `02e4dfb81dc4dababb3c0085369cc628c4704bb3` passed Pre-Unreal #761 and Warehouse #175, then Unreal Build #596 failed in C++ compile before import/runtime. The concrete blocker was UE4.27 overload ambiguity at `FPackageName::ObjectPathToPackageName(ProductionSurfacePath)` where `ProductionSurfacePath` was a `const TCHAR*`. No import/runtime claim is made for #596 because every later engine stage was skipped.

The compile root cause is fixed by constructing an explicit `FString ProductionSurfaceObjectPath` before calling `ObjectPathToPackageName`, removing compiler overload ambiguity without changing runtime behavior.

The broader audit also found a transaction-boundary gap: ChapterWorldRouter disabled CharacterMovement during async world swaps, but several gameplay mutation paths could still be invoked while the quest destination had moved ahead of committed geometry. This could allow interaction, quest triggers, traversal/puzzle completion, supplies, combat, or save actions to observe/mutate half-transition state even though movement itself was held.

A shared player-side world-transition barrier is now mirrored directly from `ChapterWorldRouter::SetPlayerWorldHold`. Movement/jump/sprint, combat, interaction, supplies, checkpoint save/restore, quick save/load and player-life ticking all refuse gameplay mutation while the barrier is active. Quest triggers, traversal challenges, environmental puzzles, world-event interactions and named NPC interaction also require `IsGameplayWorldCommitted()`. Companion banter now requires `ShireNPCContextSubsystem::IsLogicalWorldContextCommitted()`, so old-world dialogue cannot start from destination quest state.

The transition CI now deliberately requests a new chapter and checks, before destination commit, that the player is held and `IsGameplayWorldCommitted()==false`. Required marker: `ShireTransitionBarrier: PASS held-during-swap=yes`. PG-131 and the deep-project audit enforce these contracts statically.

This source wave is **STATIC-VALIDATION PENDING** until the fresh Pre-Unreal workflow completes and **COMPILE-TESTED PENDING** until a new exact-head Unreal build passes C++ compile. W01 remains closed.

## 2026-09-23 - Build #595 full chain green; warning tolerance converted into root-cause closure work

Exact head `a148d1afa919fa63725e3760684d6eed061c5e40` completed Pre-Unreal #760, Warehouse #174 and Unreal Build #595 successfully. Unreal #595 passed UE4.27.2 C++ build, deterministic production import, Automation, startup, aggregate P1C01-P1C08 runtime, state persistence roundtrip, continuous transitions and the warning-debt step. This is the first exact head in this stabilization sequence to complete the entire required CI chain.

That green result is not being treated as permission to ignore remaining evidence. The warning-debt report still contained 137 unique nearly-zero binormal identities plus matching tangent warnings, and the source audit reported 321/352 OBJ files without UVs and 334/352 without explicit normals. The previous guard allowed a ceiling of 150, so this class could remain permanently green without being eliminated.

A new root-cause import-quality wave therefore changes the policy and the importer together. The production importer now normalizes UV-less OBJ files only in its ignored `Saved/ShireProductionImportWorking` copy, generating deterministic dominant-plane face UVs before import. It fails closed if a face cannot be safely parsed/projected. The tracked SourceAssets remain byte-stable. `M_ProductionSurface` also receives a package-existence preflight before any attempted synchronous editor-only recovery load, removing avoidable missing-package warning spam. The warning guard now requires zero degenerate tangent bases, zero nearly-zero tangents, zero nearly-zero binormals and zero missing-production-master-surface warnings. PG-130 makes those contracts fail-closed in Pre-Unreal.

This stricter wave is **source-level pending fresh exact-head proof**. Build #595 remains valid evidence for its own SHA only. No PIE/device/visual/performance acceptance is claimed, and W01 remains closed until the stricter import gate is green.

## 2026-09-23 - W00 persistence/transition root-cause repair wave after Unreal #594

Unreal Build #594 on exact head `38c2c958121576b68a0bfaf4e276498d4fe89dad` materially narrowed the remaining W00 fault set. Runner/Engine Content access, clean intermediates, UE4.27.2 C++ build, deterministic production import, ShireJourney.QA, startup, and the aggregate P1C01-P1C08 sweep all passed. The previous production-surface defect is now engine-proven on that SHA: `CharacterSurfaceAudit: PASS persisted player skin/cloth surface state`. The state gate still failed with `disk-save-details written=yes restored=yes verified=no cleaned=yes`, so persistence is the active blocker.

The new source wave fixes three architectural defects rather than relaxing the failing test. First, save restore now has an atomic logical transaction: quest/route, NPC memory, discoveries, progression and chronicle/map knowledge rebuild while broadcasts are suppressed, then publish once through `CommitPersistenceRestore`. Rollback uses the same transaction but publishes only after old-world geometry and player placement have been restored; a failed rollback invalidates committed-world identity and keeps movement fail-closed. Legacy terminal-save repair is also prevented from applying an old-world transform after it intentionally changes chapter identity.

Second, the disk audit is expanded from a single `verified=yes/no` into field-level persistence evidence. It writes and reloads quest stages, route progress, a seeded Sam NPC-memory bucket, relationships/dialogue history, discoveries/milestones, progression, chronicle/map knowledge, player-life state and transform data. Serialized transforms remain exact; runtime player placement allows only the small vertical canonicalization caused by safe capsule grounding while horizontal drift remains tightly bounded. A failure now prints the exact field names instead of forcing another blind debug cycle.

Third, two async ownership races were found by source simulation. An already-resident chapter bank could be reported ready but then fail `CommitPendingRequest` because no pending IDs existed, causing a false rollback during same-bank episode/save transitions; that path now commits the matching resident bank. Cancelled audio requests also now require their `LoadKey` to remain owned before a late async callback may resolve or play sound, preventing stale playback resurrection.

PG-129 guards these transaction, same-bank and stale-audio invariants. This wave is **source repair pending fresh exact-head validation**. Do not call it PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED. W01 remains closed and the whole-game planning percentage is unchanged.

## 2026-09-23 - Unreal #593 root cause isolated; commit-bound residency hardening applied

Exact PR #67 head `5840863632d04a5fac284b472fe9e5641cd522b8` passed Pre-Unreal #758 and Warehouse #172. Unreal Build #593 passed runner/Engine Content preflight, UE4.27.2 C++ build, deterministic production import, ShireJourney.QA 2/2, startup, and the aggregate P1C01-P1C08 chapter sweep. The remaining state gate failed specifically at `CharacterSurfaceAudit: FAIL persisted player skin/cloth surface state`, followed by `ShireStateAudit: disk-save-roundtrip=FAIL`. The same log showed P1C03 world commit, NPC committed context, LivingWorld committed sync, and stable grounding.

Source inspection identified a residency-order defect rather than a missing material package: `M_ProductionSurface` is an async chapter-bank member, while `AShirePlayerCharacter::BeginPlay` applied prototype MIDs before that bank became resident and had no post-residency reapply signal. The state audit also ran on the next tick before world commit and returned early on the surface check, masking the independent disk-save path.

This W00 source wave adds a post-residency `OnChapterAssetsCommitted` contract, reapplies player surface state at that residency boundary, makes the state audit wait for the exact committed chapter/route/episode, and keeps disk-save testing running even when the surface invariant fails. Player movement now remains held until `OnWorldCommitted` publishes the committed revision/context on both normal commit and rollback. The previously implicit audio-residency assumption is replaced by bounded asynchronous `FStreamableManager` ownership in `ShireAudioSubsystem`; weak caches and short-lived request handles avoid pinning every sound for the GameInstance lifetime.

PG-127 is now fail-closed: its escaped-newline check had been after the script success/exit block and could not fail CI. PG-128 adds regression guards for committed surface residency, state-audit ordering, movement-release ordering, and bounded asynchronous audio ownership.

Evidence for this new source wave is not promoted beyond source inspection until fresh exact-head workflows run. No PIE, device, visual or target-FPS claim is made.

## 2026-09-23 - systemic hardening phase, importer compile artifact repaired

The project is still in W00 hardening / exact-head recovery rather than content expansion. Pre-Unreal #753 and Warehouse #167 are green on the prior head, while Unreal Build #588 reached the real 76-action UE4.27.2 C++ compile and failed only in `ShireProductionImportCommandlet.cpp` because a literal escaped `\n` sequence had been committed between the PNG and TGA discovery statements. That text produced C2017/C2065/C2143 at line 58.

The importer source now contains a real newline, and PG-127 is strengthened so any literal `\n` or `\r\n` text artifact in that C++ source is rejected during Pre-Unreal instead of surviving until Unreal compilation. This is a source fix pending fresh exact-head compile proof.

No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED promotion is claimed yet.

## 2026-09-22 - stabilization gate status schema correction

Pre-Unreal #748 surfaced a governance-schema mistake introduced by the stabilization freeze: `active_gate.status` was set to `ACTIVE`, but the Governor quality-gate vocabulary is `NOT_TESTED / PARTIAL / PASSED / FAILED / BLOCKED`. The stabilization gate remains the active execution focus, while its evidence state is correctly `PARTIAL` until the full exact-head chain passes. No runtime behavior or maturity is changed by this correction.

## 2026-09-22 - stabilization static-gate self-correction

Pre-Unreal #747 correctly rejected the stabilization head because the new PG-121 contract required a `RUNTIME_SWEEP_SUMMARY` marker, while `runtime_smoke.py` had already removed fail-fast behavior but had not actually emitted the aggregate marker. The harness now emits attempted/expected/failed chapter summary after completing the sequential sweep. This is a QA-contract repair only; no engine/runtime maturity is promoted until the new exact head passes the full gate.

## 2026-09-22 - architectural stabilization freeze / root-cause hardening

Owner direction is now explicit: **do not continue feature expansion by patching individual symptoms**. The project is in `W00_ARCHITECTURAL_STABILIZATION`; validation builds are required evidence, but new gameplay/region/warehouse expansion is frozen until the stabilization gate is green.

Last real engine evidence remains Unreal Build #547 on `a42679a4de808ce1f9bada7974ad87d52ee18fa9`: UE4.27.2 C++ build PASS, production import PASS, `ShireJourney.QA` 2/2 PASS, startup and P1C01-P1C04 headless audits PASS, then P1C05 failed with `no-blocking-ground`. The old runtime harness stopped at that first failure, so it provided no P1C06-P1C08 evidence.

The P1C05 response has been converted from a chapter patch into a shared world contract. `ChapterWorldRouter::ResolveGroundedSpawnLocation` now probes a bounded deterministic ring around authored/restored positions, rejects steep surfaces, checks full pawn-capsule clearance, and chooses the nearest valid ground. The temporary P1C01 and P1C05 `RuntimeSpawnFoundation` support pads were removed; Project Guardian now rejects reintroduction of chapter-specific spawn pads.

Runtime QA no longer stops at the first chapter failure. A single chapter sweep now attempts all P1C01-P1C08 sequentially on the low-RAM runner and emits `RUNTIME_SWEEP_SUMMARY`, so one engine build exposes the whole failure set instead of forcing serial red-build discovery.

Character rig requests are also hardened. Missing future-production skeletal mesh / AnimBP packages are checked with `FPackageName::DoesPackageExist` before `RequestAsyncLoad`. Missing rigs remain on modular fallback without flooding Unreal with missing-package async-load errors; completed real rig handles still release after actor-owned handoff.

Source-asset hygiene was repaired at the source, not hidden in importer logs. All 24 tracked BMP textures were converted to TGA, all MTL diffuse references were migrated, the importer now discovers PNG/TGA only, and Guardian rejects BMP. Seven project-owned OBJ files contained consecutive duplicate-position face vertices; 304 affected faces were normalized, and triangulation-risk faces are now strict asset-audit failures instead of warnings.

Material persistence remains evidence-bounded rather than guessed. The importer already performs deterministic master/MTL synthesis, explicit pre/post material package saves, on-disk verification and import failure on missing material packages. Build #547 import passed, but the full warning-debt/material gate was not reached because the old chapter harness stopped at P1C05. Fresh exact-head proof is therefore still required.

No post-#547 hardening change is called COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED yet. The next permitted activity is exact-head stabilization validation, not feature construction.

## 2026-09-22 - W00 engine recovery reached runtime; P1C05 grounding gap repaired

Unreal Build #547 on exact head `a42679a4de808ce1f9bada7974ad87d52ee18fa9` proved the runner recovery beyond the former ACL gate. UE4.27.2 C++ build succeeded, production asset import succeeded, both `ShireJourney.QA` Automation Framework tests passed, and headless startup plus P1C01-P1C04 chapter audits passed. The run then failed at P1C05 with `ShireStartupGrounding: FAIL chapter=P1C05 reason=no-blocking-ground requested=(-2400.0,0.0,130.0)`.

Source inspection found a deterministic geometry gap: the broad P1C05 fallback ground centered at X=0 with X scale 46 ends near X=-2300, while the first route slab centered at X=-2600 ends near X=-2480. The authored chapter start at X=-2400 therefore sat between both collision surfaces. `BuildFellowshipRoad` now adds a small hidden Engine BasicShapes collision foundation under the exact P1C05 start, matching the deterministic support strategy already used for P1C01.

This is a source fix pending fresh exact-head engine proof. The previous run is valid COMPILE evidence for `a42679a...`, but the new repair head is not yet COMPILE-TESTED/PIE-TESTED/DEVICE-TESTED/VISUALLY-ACCEPTED.

## 2026-09-22 - runner ACL recovered; first real compile defect repaired

Unreal Build #534 attempt 3 proved the Windows runner can now read UE4.27 Engine Content: the log reported `UE4_ACL_REMEDIATION_PASS action=none reason=already-readable`, UHT generated reflection code, and the exact head entered a 76-action `ShireJourneyEditor` C++ build. The runner/Engine Content ACL blocker is therefore no longer the immediate failure.

The first real project compile failure was cross-module visibility: `ShireJourneyEditorTools/Private/Tests/ShireQAAutomationTests.cpp` could not include `ShireSaveGame.h` while the runtime module remains intentionally `FLAT_GUARDED`. The repair exports `Source/ShireJourney` as a temporary public include root in `ShireJourney.Build.cs`, avoiding a relative/private include hack and preserving the rule that the physical Public/Private migration remains a separate engine-tested maintenance change. The importer also replaces deprecated direct `UStaticMesh::StaticMaterials` access with `GetStaticMaterials()` to remove the two C4996 warnings observed in the same build.

No COMPILE-TESTED claim is made until the new exact-head build completes successfully.

## 2026-09-22 - PIE StaticMesh mobility warning source fix

A live PIE screenshot showed repeated warnings of the form `SetStaticMesh ... but Mobility is Static` on runtime-generated `AStaticMeshActor` components. The source cause was confirmed in the Shire, Bree, Fellowship and Isengard runtime world-builder spawn helpers: each helper assigned the mesh first, then changed component mobility to Movable. Runtime-spawned `AStaticMeshActor` components begin as Static, so the mesh mutation generated warning spam.

The four helpers now set mobility to Movable before `SetStaticMesh`, preserving their existing final mobility behavior while removing the invalid mutation order. A DeepProjectAudit guard now rejects reintroduction of the old ordering.

This warning flood can contribute to editor log overhead/hitch perception, but it is not the GitHub runner ACL failure. The runner remains separately blocked because `NT AUTHORITY\\NETWORK SERVICE` cannot read UE4.27 Engine Content. No compile/PIE/device acceptance is claimed for this source fix until a fresh exact-head engine run is available.

## 2026-09-22 - precise integration-gap source closure

The deep audit findings were acted on immediately instead of being left as notes. The source branch now contains a committed-world NPC context bridge: ChapterWorldRouter publishes committed chapter/route/episode/revision on normal commit and rollback; regional mood/profile availability follows that committed identity; danger uses live quest state only while logical and committed world identity still match; and new bounded dialogue/film-context selection is suppressed during the async mismatch window rather than leaking destination context into the old visible world.

Character-rig streaming remains asynchronous, but the completed per-character streamable handle is now released after the ready broadcast, when player/NPC components have taken their own UObject references. This removes the GameInstance-lifetime handle pinning identified by the audit while retaining active-character ownership and modular fallback behavior.

The synchronous production-asset debt was also burned down at source level. Shire/Bree/Fellowship/Isengard world builders no longer directly LoadObject production meshes; they resolve only objects already resident in the async chapter bank. Black Rider, standard Fellowship enemies and mythic threats use resident-only production visual resolution, and the chapter streaming plan now includes the relevant enemy banks. Player/named-NPC production proxy pieces use resident-only soft resolution while their skeletal rig path remains asynchronous. ShireAudioSubsystem no longer synchronously LoadObject<USoundBase>; production sound must be resident through an async ownership path, otherwise subtitle/story/silent fallback remains safe.

A continuous guard was added to deep_project_audit.py: non-/Engine/BasicShapes synchronous LoadObject is now rejected, as are regressions in committed NPC context publication, completed rig-handle release, synchronous audio load, builder ticking and existing social-scan bounds.

These are source fixes only until the runner is restored. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED promotion is claimed. The active priority remains W00 runner/exact-head unlock.

## 2026-09-22 - deep organization and integration audit before runner repair

A repository-wide source/governance audit was performed against PR #67 exact head `17689b194ddca281aa9881b9ac50594712a65df6` before touching the laptop runner. Three current workflow facts are now authoritative for this checkpoint: Pre-Unreal #685 failed only because the newly accepted third-person camera requirement was not yet mapped into MasterExecutionRoadmap; Unreal Build #520 again stopped before C++ compilation because `NT AUTHORITY\\NETWORK SERVICE` could not read `Engine/Content/EngineMaterials/WorldGridMaterial.uasset`; Warehouse #99 succeeded and the persistent inventory audit reported `payloadFiles=240 bytes=3816657674 receipts=8 receiptRecords=278 duplicateGroups=22`, with total footprint `files=249 bytes=3816866382`.

The roadmap drift is repaired: REQ-CAMERA-001 is now assigned to the Part I gameplay bundle and the tracked unfinished-requirement snapshot is regenerated from the Governor. This was a management consistency defect, not a gameplay defect.

The deeper integration simulation found two additional source risks worth carrying into W00/W01 rather than hiding them. First, `LivingWorldDirector` correctly waits for `ChapterWorldRouter` committed-world revision before switching active life/weather, but `UShireNPCContextSubsystem` independently reads the logical quest chapter/route for regional mood, profile availability, film-dialogue context and pressure. During asynchronous chapter load the quest can advance while old geometry is still visible, so old-world NPCs can transiently react using destination context. Second, asynchronous character-rig handles are retained per requested character for the GameInstance lifetime; this is safe functionally but needs measured chapter-cast residency/eviction on the ~2 GB VRAM target before full-cast skeletal rollout.

The audit also corrected stale debt tracking: ambient NPC pooling is already source-implemented with bounded reuse and disabled pooled ticks; it is now pending engine/device proof rather than missing. Conversely, synchronous runtime asset debt is still real: the inspected exact head contains 77 direct `LoadObject` calls in `FellowshipChapterWorldBuilder`, 55 in `ShirePrototypeWorldBuilder`, 22 in Bree, 10 in Isengard, plus remaining player/named-NPC fallback loads. These must be burned down incrementally after the runner is restored, without deleting the two-phase async bank/fallback architecture.

No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED status is promoted by this audit.

## 2026-09-22 - final pre-runner warehouse saturation batch

One final source-safe warehouse expansion is committed before runner repair becomes the active priority. Three official KayKit public-GitHub packs were source-checked as CC0 and added to the non-interactive staging lane: Restaurant Bits for food/kitchen/interior support, Halloween Bits for selectively filtered cemetery/crypt/dark-region props, and City Builder Bits only as a manually filtered source of period-neutral civic props. Their FBX/GLTF/OBJ source presence does not override the project rule that animated final characters are skeletal FBX and production textures are PNG/TGA/channel-packed.

This commit authorizes staging only. Until Warehouse Stage emits actual receipts, these additions are not claimed STAGED. After receipt/audit, broad warehouse expansion pauses and W00 runner/Engine Content ACL repair becomes the next active production priority.

## 2026-09-22 - whole-game completion wave map

A durable finish map is now registered in `Data/CompletionWaveMapV1.json`. It treats the current whole-game planning position as approximately 40/100 and organizes the remaining 60 planning points into 12 production waves (W00-W11), from runner/exact-head unlock through Shire visible skeletal-character conversion, Part I production/acceptance, Part II/III runtime+production, and final trilogy integration.

The execution unit is a major coherent production drop rather than an individual Git commit or raw file upload. The map currently estimates roughly 30-40 remaining major drops, with actual commit count allowed to be higher. These percentages/drop counts are planning estimates only; they do not alter any compile, PIE, device, performance or visual acceptance state.

## 2026-09-22 - character visibility bridge and warehouse receipt hardening

Owner priority is now explicit in the Governor and WORLD_DETAIL_LEDGER: warehouse growth must convert into visible humans/enemies, with P1C01 Shire still the first assembled benchmark. The official KayKit Skeletons 1.0 public GitHub package was source-checked as CC0 and documents fully rigged/animated characters, FBX/GLTF delivery and 90+ animations. It is registered strictly as technical enemy rig/import/retarget QA stock, not canonical LOTR enemy art or a visually accepted production character.

The KayKit staging batch now includes that pack, and the warehouse inventory audit now recognizes archive-style receipt records in addition to legacy file records and verifies recorded license-snapshot hashes when present. This closes a bookkeeping blind spot where KayKit archives could contribute payload bytes without participating in receipt-record hash validation.

Evidence boundary remains unchanged: the last proven engine run is still blocked before C++ compilation/import by the non-elevated NETWORK SERVICE runner lacking read access to UE4.27.2 Engine Content. These changes are source/warehouse preparation only. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made.

## 2026-09-22 - hourly continuation: non-interactive KayKit public-GitHub lane

Exact-head inspection started from PR #67 head `d856a716d5bc270ce0ddc2d649acbb1656ae112c`. Pre-Unreal Validation #670 completed successfully and Warehouse Stage #80 completed successfully. Unreal Build Validation #505 stopped before C++ compilation: the runner identity was `NT AUTHORITY\\NETWORK SERVICE`; the guarded ACL remediation reported `UE4_ACL_REMEDIATION_DEFERRED reason=runner-not-elevated`; the unchanged UE4.27.2 preflight then failed six reads of `Engine/Content/EngineMaterials/WorldGridMaterial.uasset` with access denied. Build/import/Automation/startup/chapter/state steps were skipped. This is machine ACL evidence, not compile evidence, and this run does not retry the same elevated fix.

Warehouse saturation now adds `Data/WarehouseKayKitGitHubAcquisitionBatchV1.json` and `Scripts/stage_kaykit_github_warehouse.ps1`. The lane uses only exact official public KayKit GitHub repositories/direct archives and license snapshots; it forbids login, purchase/name-your-price, OAuth, Patreon/Discord and other interactive routes. Per-pack and batch byte caps, CC0 license markers, SHA256 provenance and STAGED-only state are enforced. The Warehouse Stage workflow now executes this lane before inventory audit.

The concrete KayKit support candidates cover low-spec medieval settlement/layout stock, dungeon/interior modules, rigged/animated background-character pipeline testing and furniture props. `TrilogyWorldFoundationPlanV1.json` maps them into Shire/Bree/Rivendell/Moria/Lothlorien/Rohan/Gondor/Osgiliath/Minas Morgul/Cirith Ungol/Paths of the Dead/Grey Havens support roles. P1C01 Shire remains the first assembled benchmark; later-film use is warehouse/preproduction only. Final animated characters still require real skeletal FBX rigs, skin/deformation review; repeated detail remains ISM/HISM-classed; heavy integrated assets remain soft/async through FStreamableManager.

Integration-repair inspection found no new demonstrated source regression behind the green static gate. Runtime/compile progression remains blocked only by the already-demonstrated local Engine Content ACL condition. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made for this wave.

## 2026-09-22 - autonomous hourly lane: exact-head evidence + Quaternius saturation

PR #67 exact head entering this iteration was `f41d5e91ac2a789387e987ff759b9e674cd86e10`. Exact-head Pre-Unreal Validation #667 succeeded, and Warehouse Stage #76 succeeded across Poly Haven, OpenGameArt, Quaternius, ambientCG base/trilogy batches, Kenney, inventory audit and footprint reporting. Unreal Build Validation #502 did not reach C++ compilation: the guarded Engine Content ACL remediation step completed, then the unchanged UE4.27.2 verification step failed; build, import, Automation Framework, startup, chapter and state audits were skipped. This remains a machine/Engine Content preflight blocker, not compile evidence, and the gate was not weakened.

Warehouse saturation expanded `WarehouseQuaterniusAcquisitionBatchV1.json` and `TrilogyAssetCandidateQueue.json` with official-page CC0 lanes for additional modular background humans, creature rig/deformation pipeline stock, supporting textured buildings and dungeon/interior support. These remain CANDIDATE/AUTHORIZED_FOR_STAGING until actual staging receipts and intake checks exist. Canonical hero characters/creatures still require real skeletal FBX rigs, skin/deformation review and their own visual acceptance.

`TrilogyWorldFoundationPlanV1.json` now maps the added stock into reusable regional-preproduction roles for Shire/Bree/Rivendell/Lothlorien, Moria, Rohan, Gondor/Osgiliath, Cirith Ungol, Paths of the Dead, Mordor and Grey Havens while preserving P1C01 Shire as the first assembled benchmark. Later-film mappings are warehouse/preproduction only and do not open Part II/III runtime chapters. Intake ordering reiterates SHA256/provenance retention, FBX rig requirements, PNG/TGA/channel-packed texture preference, ISM/HISM classification for repeated detail, and FStreamableManager soft/async ownership for heavy runtime content.

Integration-repair inspection found no new demonstrated source regression on the green pre-Unreal head. The unresolved failure is still the local UE4 Engine Content preflight, so source/runtime gates remain fail-closed. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made for this iteration.

## 2026-09-22 - active wave: ACL repair attempt + trilogy material expansion

The Unreal Build workflow now contains a guarded Engine Content ACL remediation step before the existing UE4.27.2 verification. It grants only read/execute to the runner service identity when the workflow has elevation; if the runner is not elevated, it records the exact required action and leaves the original verify gate unchanged. This does not weaken validation and does not create a compile-tested claim.

Warehouse execution also expanded beyond Shire with `WarehouseAmbientCGTrilogyBatchV2.json`, targeting material families for Caradhras, Moria, Rohan, Gondor, Osgiliath/Ithilien, Mordor, Isengard, Bree/battlefields, Pelennor support and Shelob-lair support. The warehouse workflow now stages this batch in addition to the existing Shire/material/audio/Quaternius/Kenney lanes.

No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED status is claimed by this wave.

## 2026-09-22 - autonomous three-lane production iteration

PR #67 exact head before this production batch was `0c8130a33f8df3648d270d8bd0ee6b24aee882fb`. Pre-Unreal Validation #653 completed successfully on that exact SHA. Unreal Build Validation #488 did **not** reach C++ compilation: the self-hosted `UE4-27-Windows` runner executed as `NT AUTHORITY\\NETWORK SERVICE` and was denied read access to `Engine/Content/EngineMaterials/WorldGridMaterial.uasset` on all six preflight probes. Build, import, Automation Framework, startup, chapter and state steps were therefore skipped. This remains an Engine Content ACL/environment blocker, not compile evidence.

Warehouse saturation advanced without promoting asset maturity. `TrilogyAssetCandidateQueue.json` now includes concrete Quaternius animation/prop and Kenney world/fortification/nature/interior/UI support candidates already tied to official CC0 pack pages. `TrilogyAudioAssetCandidateQueue.json` now mirrors stage-authorized OpenGameArt CC0 prototype music/SFX candidates across Shire, Bree, Rohan and large-battle routing tests. `WarehouseAmbientCGAcquisitionBatchV1.json` is expanded into a trilogy-foundation material intake covering snow/ice, cave stone, wetland ground, white stone, volcanic/ash surfaces, industrial metal, Rohan pastoral surfaces, ruins and river/wet materials. AUTHORIZED_FOR_STAGING and STAGED remain distinct from READY_FOR_IMPORT / IMPORTED / INTEGRATED / ACCEPTED.

Multi-region world-foundation preproduction is no longer a list of region names only. Every declared region from Shire through Grey Havens now carries explicit stock contracts for architecture, terrain/materials, vegetation/ecology, props, populations/factions, audio, lighting/atmosphere, VFX and traversal/collision, plus preferred warehouse source lanes. P1C01 remains the first assembled benchmark; later-film regions are explicitly PREPRODUCTION_ONLY and this work does not open Part II/III runtime chapters.

Current code/runtime acceptance is unchanged by these warehouse/world-plan edits. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made for the new head.

## 2026-09-22 - failed-swap rollback transaction expanded to player-life state

The integration repair wave now closes another source-level rollback gap. `ChapterWorldRouter` rollback snapshots already preserved quest, route/chapter/episode, NPC memory, exploration, progression, knowledge and player transform. They now also capture player health, stamina, resolve and supplies from `AShirePlayerCharacter`. During `RestoreCommittedWorldFromSnapshot`, those values are reapplied through `RestoreTransactionalPlayerState` after grounded placement succeeds and before world hold is released.

Source-contract regression coverage now requires this full transaction ordering. This is still source/static work only: exact-head UE4.27 compile/runtime proof is required before the rollback requirement can be considered closed.

No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made.

## 2026-09-22 - world foundation work expanded beyond Shire

P1C01 remains the first fully assembled visual benchmark, but production prework is no longer Shire-only. `Data/TrilogyWorldFoundationPlanV1.json` now tracks reusable world-foundation lanes for Bree, Weathertop, Rivendell, Caradhras, Moria, Lothlorien, Anduin/Amon Hen, Fangorn, Edoras/Meduseld, Helm's Deep, Isengard, Emyn Muil, Dead Marshes, Ithilien/Henneth Annun, Minas Tirith, Osgiliath, Minas Morgul, Cirith Ungol/Shelob's Lair, Pelennor, Paths of the Dead, Black Gate, Mordor/Gorgoroth, Mount Doom and Grey Havens.

Each region has parallel architecture, terrain/material, vegetation/ecology, population/faction, audio, lighting/VFX and traversal/collision stock requirements. This is preproduction/warehouse foundation work only; it does not bypass runtime chapter gates for Part II/III.

## 2026-09-22 - pooled visual fallback hardening

The async living-world ownership wave now also resets every reused ambient actor to constructor-owned Engine primitive meshes before resolving role-specific production soft objects. This prevents a pooled NPC that changes regional role from retaining a stale Human/Elf/Hobbit mesh when a production asset is unavailable. Active density and streaming policy are unchanged. Exact-head CI/UE evidence remains required; no runtime verification claim is made.

## 2026-09-22 - Resource Bible 09 operationalized into warehouse execution

The project source `09_EXTERNAL_HELPFUL_RESOURCES_BIBLE_PERSONAL_LOCAL` has now been converted into `Data/ResourceBibleSourceExpansionV1.json` and merged into `Data/GlobalWarehouseSourceRegistryV2.json`. Its source families now explicitly cover voice/TTS, music, SFX/field recording, visual/UI reference, 3D/models/scans, architecture, environments/materials, animation/mocap, LOTR-specific reference and AI creation tools. This preserves the Bible's own separation between personal-local candidate material, temporary/reference material and tools rather than flattening every website into an automatic production source.

Concrete staging also widened beyond the previous Poly Haven/Quaternius/OpenGameArt lanes. ambientCG now has a public-API 2K-PNG material batch for timber, plaster, terrain, stone, bark, leather/fabric and roofing/cobble families, and Kenney now has an official-pack-page CC0 resolver for world/support stock such as fantasy town, castle, nature, furniture, building, dungeon, food, UI and background-character packs. Both are wired into the persistent Warehouse Stage workflow.

These changes expand warehouse sourcing and STAGED stock only. They do not promote UE import, integration, visual/audio acceptance, or any COMPILE/PIE/device status.

## 2026-09-22 - asynchronous living-world asset ownership

The registered living-world synchronous production-load defect is now repaired at source level using the existing two-phase chapter streaming architecture rather than introducing another loader. `Data/ChapterAssetStreamingPlan.json` now explicitly places the ambient production surface, Hobbit/Human/Elf resident meshes, and chapter-used fauna meshes into the relevant soft chapter banks. Their lifetime is therefore owned by the resident `FStreamableHandle`, which remains alive until a replacement world successfully commits.

`AShireAmbientNPC::ApplyVisualStyle` no longer synchronously `LoadObject`s production meshes or the production surface. It resolves only already-resident soft objects and keeps constructor-owned Engine primitive/material fallbacks when a production asset is unavailable. `LivingWorldDirector` likewise resolves its ambient motion production meshes from the resident bank instead of initiating synchronous package loads. This preserves the current async/no-game-thread-wait policy and does not increase active density.

Exact-head static/CI validation is still required for this change. Runtime rendering and transition behavior remain unproven until matching UE4.27.2 evidence exists; no COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made.

## 2026-09-22 - bounded ambient NPC pooling foundation

The registered baseline SpawnActor/Destroy churn is now repaired at source level with lazy bounded reuse. `LivingWorldDirector` owns an ambient-NPC pool capped at 24 cached actors but does not preallocate it or change authored active-density targets. Baseline culling, chapter reset, and expired micro-events return ambient NPC actors to the cache when capacity is available; non-NPC event actors still destroy normally, and excess cached candidates are destroyed rather than growing memory without bound.

`AShireAmbientNPC` now has an explicit deactivate/reactivate lifecycle that clears social/awareness/caption state, disables tick and visibility while cached, and fully reapplies routine role, prop, movement and lightweight needs state on reuse. Pooled actors are excluded from social-partner selection. This targets spawn/destroy churn while preserving the i7 Gen6 / 8 GB RAM / ~2 GB VRAM budget and does not increase world density.

This remains source-only until exact-head validation runs. It is not COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED.

## 2026-09-22 - ground-safe living-world ambient placement

The next registered foundation defect is repaired at source level without increasing density. `LivingWorldDirector::SpawnAmbientActor` now proves blocking ground with a vertical visibility trace before spawning ground-bound ambient roles and separately grounds their routine endpoint. If the initial point has no blocking ground the spawn is rejected; if only the travel endpoint is unproven, the actor remains at its grounded start rather than walking toward an unsafe Z. Bird and butterfly roles retain their authored airborne placement, while rabbit and humanoid residents use the ground-safe path.

This is a low-cost placement guard for the existing UE4.27.2 / low-spec architecture; it does not add navmesh cost or new population. Wall/obstacle avoidance and rendered placement quality still require runtime observation. Exact-head static validation must pass before the next lifecycle repair. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made.

## 2026-09-22 - failed world-swap rollback transaction repair

The registered transition-persistence defect wave now includes a source-level rollback transaction repair. `ChapterWorldRouter` captures the last committed quest/route/world identity plus player transform after each successful world commit. If destination construction, grounding, or asset-bank commit fails, the pending request is cancelled, the prior logical state and builder are restored under a rollback guard, the player is grounded back at the committed transform, movement is released only after that succeeds, and a fresh `WorldRevision` is broadcast for the rebuilt committed world.

This closes the known source-level gap where rollback rebuilt prior geometry but left movement held and logical/player state incoherent. It is **not** runtime closure yet: exact-head static validation is required next, and UE4.27 compile/PIE/device evidence remains separate. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made.

## 2026-09-22 - global warehouse source circle expanded and ranked

The warehouse source registry is no longer a short-list. It now tracks a broader global source matrix with an explicit scoring/tiering policy so acquisition can widen without becoming chaotic. Newly added lanes include ambientCG, ShareTextures, KayKit, PolygonalMind CC0 releases, Poly Pizza, Gobkit, NASA 3D resources and supplemental HDRI sources. Tier A is reserved for clear, automatable, high-value sources; auth/marketplace sources are Tier B; supporting/niche sources are Tier C; ripped/unclear proprietary-port communities remain reference-only.

The selection rule is intentionally not “download everything from every site.” For each warehouse slot, retain the best-fit one to three candidates based on visual fit, engine readiness, license clarity, format, performance, reuse breadth and source stability. This keeps the trilogy warehouse large but searchable and prevents duplicate low-value stock from consuming staging/storage time.

## 2026-09-22 - warehouse runner execution-policy blocker repaired

Warehouse Stage #18 reached the self-hosted runner and failed before any download because GitHub's `shell: powershell` wrapper attempted to dot-source its temporary script while the Windows service account has script execution disabled. The warehouse workflow now invokes each checked-in staging script from `cmd` using `powershell.exe -NoProfile -ExecutionPolicy Bypass -File`, matching the proven pattern already used elsewhere on the runner. This repairs the staging launcher only; actual staged-file counts remain pending the next exact-head Warehouse Stage run.

Unreal Build #449 remains a separate pre-compile blocker: the same runner account is still denied read access to `WorldGridMaterial.uasset`. Pre-Unreal #614 succeeded on the same prior head. No compile/PIE/device/visual acceptance claim is made.

## 2026-09-22 - multi-lane warehouse staging expanded

Warehouse fill now runs as three concrete intake lanes on the integration train: Poly Haven CC0 environment/material stock, OpenGameArt CC0 music/foley stock, and Quaternius CC0 character/animation/fauna/world-kit discovery/staging. The audio lane contains direct OpenGameArt WAV/ZIP endpoints with source-page/license records and SHA256 receipt generation. The Quaternius lane resolves only public direct archives from official pack pages and records unresolved/store-only packs without fabricating download URLs.

The warehouse workflow remains independent from UE4 compile/PIE. Staged assets remain STAGED until their category-specific intake validation passes; animated production characters still require real FBX rigs and hero-character visual acceptance is not implied by background/base packs.

## 2026-09-22 - warehouse fill execution expanded beyond catalogue-only state

The warehouse lane has moved into an actual staged-download implementation. `Data/WarehouseAcquisitionBatchV1.json` now contains a source-page-verified Poly Haven P1C01 material/prop batch covering wood interiors, dirt/path variants, plaster families, cobblestone, mossy stone and barrel props. `Scripts/stage_polyhaven_warehouse.ps1` now handles provider/API failures per asset instead of aborting the entire batch, records skipped reasons, and preserves successful downloads/receipts so one bad slug cannot stop warehouse growth.

The dedicated `Warehouse Stage` self-hosted workflow remains separate from the UE4 build path. The current exact-head Pre-Unreal gate is green; runtime/PIE/device proof remains separate. No staged warehouse item is promoted to imported/integrated/accepted by this download infrastructure alone.

## 2026-09-22 - persistent warehouse staging lane activated

The asset warehouse is no longer catalogue-only. A dedicated `Warehouse Stage` workflow and `Scripts/stage_polyhaven_warehouse.ps1` now target a persistent self-hosted storage root at `C:\\actions-runner\\_warehouse\\ShireJourney`, independent from the blocked UE4 Engine Content build path. `Data/WarehouseAcquisitionBatchV1.json` defines the first CC0 Poly Haven material/prop batch with 2K intake and a hard byte cap; every staged file is intended to receive size/SHA256/source metadata in a local receipt before later import.

The workflow listens to the integration branch, PR exact-head changes affecting the warehouse batch/scripts, and manual dispatch. Staging does not imply UE import, runtime integration or visual acceptance. Existing exact-head evidence remains: Pre-Unreal #603 succeeded on `2e7424c9c63c2bbdb419c4bed10e01ca5cbd282a`; the UE build path remains separately blocked by the self-hosted Windows account's Engine Content read permissions.

No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED status is promoted by warehouse staging.

## 2026-09-22 - Pre-Unreal #597 PG-078 warehouse-roadmap reconciliation

Exact-head Pre-Unreal #597 on `f7ef04c4b36d6664bdb06324a9652f1572584f28` failed with four deterministic governance errors: `REQ-WAREHOUSE-001` and `WORK-PROD-011` were registered in ProjectGovernor but not yet assigned to the master roadmap, and the tracked unfinished/active snapshots were therefore stale. The warehouse requirement/work item is now assigned to B2 Characters & World Production and both snapshots are regenerated directly from the live Governor.

Unreal Build #432 on that SHA again failed before C++ compilation because the self-hosted runner identity `NT AUTHORITY\\NETWORK SERVICE` was denied access to UE4.27.2 `WorldGridMaterial.uasset`. Warehouse catalogue/candidate/staging work continues independently under DEC-033; this runner blocker still prevents compile/PIE/device evidence.

No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED status is claimed.

## 2026-09-22 - warehouse testing boundary clarified

The warehouse lane is now explicitly decoupled from runtime test availability. We do **not** wait for UE4 compile/PIE/device validation to discover, catalogue, download or stage trilogy assets. That work is intentionally parallel and may continue while the self-hosted runner is blocked.

The engineering boundary is staged rather than test-free: raw stock must pass a lightweight intake gate before `READY_FOR_IMPORT` (file integrity, archive/malware hygiene, correct format, units/scale, naming, texture packing/dimensions, topology/UV/skeleton/animation sanity where relevant, plus provenance/metadata). UE4 import/build evidence begins at `IMPORTED`; runtime/PIE evidence begins at `INTEGRATED`; visual/audio/device acceptance is required only for `ACCEPTED`.

This rule is durable as `DEC-033` and hard invariant `INV-WAREHOUSE-STAGING`. It prevents runner outages from starving the asset warehouse without turning the warehouse into an untrusted file dump.

## 2026-09-22 - first concrete trilogy asset candidate queue seeded

Warehouse-first production moved from catalogue-only planning into concrete sourcing. `Data/TrilogyAssetCandidateQueue.json` now contains the first official-source candidates: CC0 Quaternius rigged/background character, fantasy outfit, medieval village, modular ruins, nature and farm/animated-animal packs, plus Poly Haven high-fidelity barrel and wood/stone/mossy PBR material lanes. These are candidates, not automatic final hero art; low/stylized packs are explicitly limited to supporting/background/pipeline roles where appropriate.

The next sourcing pass is deliberately aimed at the remaining high-value gaps: realistic hero humanoid bases, non-stylized rural/medieval architecture, photoreal biome libraries, rigged hero creatures, professional animation libraries and the approved audio-bank lanes. No candidate is called INTEGRATED or ACCEPTED until an actual asset is acquired/imported and earns the required evidence.

## 2026-09-22 - trilogy warehouse-first production plan activated

The owner explicitly changed the production emphasis: final-looking characters, world art and audio may no longer remain vague downstream gaps while backend/governance continues to grow. The project now has a machine-readable trilogy warehouse at `Data/TrilogyProductionAssetWarehouse.json` and a new Governor requirement `REQ-WAREHOUSE-001`, decision `DEC-032`, and active work item `WORK-PROD-011`.

The first-pass catalogue spans all three films: major and supporting named characters, population/faction families, 28 major location slots with state variants, cultures, creatures/fauna, battles, weapons/artifacts, material families, architecture/props, animation families, audio, cinematic/VFX and UI support. The supporting-cast layer was seeded from the supplied trilogy screenplay speaker pass; the world/culture/creature layers were grounded in Sources 03/04/05 and Source 11.

Important proof boundary: the catalogue is now broad enough to prevent forgotten categories, but this is not a claim that all final binary assets already exist. `CATALOGUED`, `READY`, `APPROVED`, `INTEGRATED` and `ACCEPTED` are intentionally separate states. The immediate production target is P1C01 as the first complete natural-looking vertical slice while Part II/III asset-bank preparation proceeds in parallel.

No new COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made by the warehouse plan itself.

## 2026-09-22 - cinematic audio sourcing directive registered

The owner-forwarded audio-engineering message is now durable repository state. The project already has `UShireAudioSubsystem` routing, ambience/music crossfades, voice ducking and speaker-attachment rules in `Part1SonicWorldPlan`; the major missing layer is authored final audio content. `Data/AudioAssetSourcingWaveV2.json` now defines the offline bank strategy for voice, music, ambience/fauna, foley and creature/combat audio, plus 3D spatialization, concurrency and low-spec profiling requirements.

ElevenLabs, BOOM Library and Pro Sound Effects are registered as candidate production sources subject to exact authorization/license/entitlement. LOTR Complete Recordings, Blu-ray center-channel dialogue and classic EA LOTR game audio are stored as reference-only unless separately cleared. This prevents source discovery from being lost while keeping the Approved bank deterministic and auditable.

No final voice/music/SFX asset, mix acceptance, PIE/device audio acceptance or new COMPILE-TESTED claim follows from this registration.

## 2026-09-22 - cinematic asset-source shortlist expanded

The owner-forwarded asset-manager message has been registered rather than kept in chat memory. `Data/ExternalAssetManifest.json` now stores DeviantArt 3D/XNALara ports, SFMLab, Open3DLab, Nexus Mods and ArtStation Marketplace as additional cinematic-quality discovery/review sources, alongside the already tracked CGTrader, TurboSquid, Sketchfab, Quixel/Fab and legacy Unreal Marketplace paths.

The private/non-distributed project intent and exact-film visual target are recorded, but discovery is not automatic approval: ripped/ported proprietary film or game assets still require explicit item-level reuse rights/provenance before entering `SourceAssets/ExternalLicensed/Approved`. The project should still aggressively search these sources for legal high-quality bases, original artist work, reusable marketplace items, commissions and environment/material packs so the visual warehouse can be filled without reverting to low-detail placeholders.

## 2026-09-22 - Pre-Unreal #578 character-guard reconciliation

Exact-head Pre-Unreal #578 passed its core structural phase, then reported four character handoff guard failures because PG-051/PG-089 still required the removed synchronous package-probe symbols inside ShirePlayerCharacter/ShireNPC. The V7 runtime now owns heavy rig paths in ShireChapterAssetStreamingSubsystem and requests them with FStreamableManager::RequestAsyncLoad.

The guards are updated to protect the new architecture instead of restoring the obsolete LoadObject/FPackageName path: player/NPC fallback and motion symbols remain required; the streaming subsystem must expose RequestCharacterRig/ResolveCharacterRig, SK_/ABP naming and RequestAsyncLoad; and the player path is explicitly rejected if synchronous USkeletalMesh/UAnimInstance loading returns.

This is a static-validator reconciliation only. No final character art is claimed and no COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED status is promoted.

## 2026-09-22 - exact-head runner retest preparation: duplicate EndPlay regression fixed

Pre-Unreal #576 on `c9a0eaafc273aeaa2fd1a0fb0aa0f41903a0c2a8` stopped in static validation with one concrete source error: `Unbalanced braces in ShirePlayerCharacter.cpp: balance=1`. Inspection found a duplicated `AShirePlayerCharacter::EndPlay` function signature introduced while wiring async character-rig delegates. The duplicate declaration/opening brace is removed; no intended gameplay behavior is changed by this correction.

The same exact head's Unreal Build #411 proved the Windows self-hosted runner is online and executing the workflow, but it still stopped before C++ compilation because the runner identity `NT AUTHORITY\\NETWORK SERVICE` received access denied reading UE4.27.2 `WorldGridMaterial.uasset`. A new exact-head workflow run is required to determine whether the laptop-side permission state has changed since #411.

No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED status is claimed by this source fix.

## 2026-09-22 - persistence/world-commit repair wave started

After Pre-Unreal #564 turned green on `685dc63ff94fec0a1f6b3d57d60fce3bffcde31d`, the integration train moved to the first registered runtime defect wave instead of opening new features. Transition checkpoint capture no longer clears and saves on the next player Tick unconditionally. It now waits until `ChapterWorldRouter::IsWorldCommitted` confirms the current chapter/route/episode identity, so an asynchronous preload cannot produce a destination chapter snapshot with a source-world transform.

Cross-chapter save restore is also changed from immediate teleport to deferred committed-world placement. `AShirePlayerCharacter` stores the saved transform and identity, waits for the matching committed world, and asks `AChapterWorldRouter::PlacePlayerAtCommittedTransform` to ground the saved XY location against destination geometry before teleporting. The initial P1C01 checkpoint is routed through the same commit barrier.

This is a source implementation wave only. It has not yet earned UE4.27 compile or runtime proof, and the failed-swap rollback transaction is still open. Unreal Build #399 is still expected to encounter the separate runner Engine Content permission blocker unless that machine permission changes. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made.

## 2026-09-22 - Pre-Unreal #562 stale streaming-cancellation test repaired

Exact-head Pre-Unreal #562 on `830b986d36d2563d11d7b3ed18c94b64e6741090` passed the core validator, Project Governor and Deep Project Audit, then failed one source-contract unittest in `Scripts/test_streaming_cancellation_contract.py`. The test still expected `ResidentHandle = PendingHandle` inside `HandleAsyncLoadComplete`, which contradicts the integrated two-phase streaming contract: async completion only reports preload readiness, while resident promotion belongs to `CommitPendingRequest` after world construction and grounding succeed.

The regression test is updated to require the stale-serial guard before the preload-ready broadcast, explicitly reject resident promotion inside the async callback, and require `ResidentHandle = PendingHandle` only inside `CommitPendingRequest` after its readiness guard. Runtime streaming code is unchanged by this correction.

Unreal Build #397 on the same SHA again failed before C++ compilation because `NT AUTHORITY\\NETWORK SERVICE` could not read UE4.27.2 `WorldGridMaterial.uasset` across all six probes. No compile/runtime/PIE/device/visual status is promoted. The registered transition persistence/rollback/NPC lifecycle defects remain the next runtime repair wave once static validation is green on the exact new head.

## 2026-09-22 - Pre-Unreal #561 deep-audit false regression isolated

Exact-head Pre-Unreal #561 on `ed5af300852e6e2ce2264334c560af658250434b` reached `PRE-UNREAL CORE VALIDATION PASSED` and `PRE-UNREAL VALIDATION PASSED`, then failed in `Scripts/deep_project_audit.py` with one error: `async chapter streaming contract missing: FStreamableManager`. The streaming implementation is still asynchronous: `FStreamableManager` is declared in `ShireChapterAssetStreamingSubsystem.h`, while `FSoftObjectPath` and `RequestAsyncLoad` are used in the cpp. The audit had incorrectly required all three literal markers to appear in the cpp alone.

The deep audit now validates the async contract across the subsystem header+cpp while still forbidding `LoadObject<` in the streaming cpp. This is a static-audit repair only; chapter streaming runtime behavior is unchanged. The Work-session persistence/rollback/NPC findings remain open and registered under `EXT-REV-2026-09-22-018`.

Status remains **STATIC-PENDING** until a fresh exact-head workflow completes successfully. Unreal Build #396 is independent engine evidence and must be read on its own result. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made by this audit change.

## 2026-09-22 - Work-session playability audit reconciled and PG-117 guard repaired

The owner-forwarded Work review was rechecked against integration head `170ebd857bece56a6d7f76f4928efe0eb3426af2` rather than copied into governance verbatim. The review identified current-source risks that remain open: next-Tick chapter checkpoint capture is not synchronized to asynchronous world commit; save restore may apply a saved transform before the matching world is committed; failed-swap rollback can rebuild the prior builder while leaving movement held and logical/player state un-restored as one transaction; ambient residents use approximate-Z placement with collisionless body meshes; and living baseline population still uses SpawnActor/Destroy plus direct LoadObject in ambient visual setup. These findings are now durable under `EXT-REV-2026-09-22-018`, and REQ-SAVE-001 is downgraded from IMPLEMENTED to PARTIAL until the transition/persistence contract is repaired.

Two forwarded details were corrected rather than promoted: the indexed inventory reports 24 image files total, not 24 BMP files, with seven explicit Shire BMP paths visible in that inventory; and current Pre-Unreal diagnostics no longer stop at the historical #558 summary. Exact-head Pre-Unreal #560 on `170ebd857bece56a6d7f76f4928efe0eb3426af2` reported `PRE-UNREAL CORE VALIDATION PASSED` followed by one concrete failure: `PG-117 Part I visual current wave is not hero equipment V4`.

That #560 failure is another stale historical guard, not evidence that the hero-equipment V4 assets disappeared. `Part1VisualProductionPass.current_wave` is now the V10 early-realm world/life wave, while the dedicated `hero_character_equipment_v4` historical block and CharacterProductionMatrix V4 character wave remain present. PG-117 is therefore changed to preserve the V4 historical asset contract without requiring V4 to remain the global current visual wave.

This update changes governance/documentation and the static validator only; it does not yet modify the save/transition/NPC runtime defects above. Status remains **STATIC-PENDING** until a fresh exact-head Pre-Unreal run passes. Unreal Build #395 is a separate engine gate; no COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made here.

## 2026-09-22 - PR #67 exact-head Pre-Unreal #558 failure isolated

Exact-head Pre-Unreal run #558 on `809325a64547744f0cc4992d76c42fb7e0862d82` reached the project validator and reported exactly two static errors after validating 30 cpp files, 32 headers, 63 architecture entries, 32 quest definitions, 8 runtime chapters, 62 presentation cues and 50 dialogue sequences. Source inspection isolated both errors to the stale PG-111 guard: it still required the V9 world-life status and the old fixed half-density implementation marker after the integrated branch intentionally advanced to V10 chapter density profiles and `DangerPopulationFraction`.

The repair updates PG-111 to protect the V10 plan identity/status, require bounded per-chapter density profiles, preserve the P1C05/P1C06 civilian-empty and P1C08 bird-only rules, and assert the chapter-driven danger-thinning runtime path rather than the removed fixed-halving string. This is a validator-contract repair; it does not change LivingWorldDirector runtime behavior.

Unreal Build #393 on the same SHA failed earlier than compilation: the UE4.27.2 preflight ran as `NT AUTHORITY\\NETWORK SERVICE` and received access denied while opening `C:\\Program Files\\Epic Games\\UE_4.27\\Engine\\Content\\EngineMaterials\\WorldGridMaterial.uasset` on all six probes. The workflow remains fail-closed. This is not C++ compile evidence. Current integration status remains **STATIC-PENDING** until a new exact-head Pre-Unreal run passes, and it remains **NOT COMPILE-TESTED / NOT PIE-TESTED / NOT DEVICE-TESTED / NOT VISUALLY-ACCEPTED** until the engine-runner access blocker is repaired and the corresponding gates execute.

## 2026-09-21 - continuous transition audit integrated

The comprehensive integration branch now includes a same-session transition audit across P1C01-P1C08, FrodoMain/GandalfParallel route changes, committed-world/living-world revision agreement and a disk-save roundtrip. Separate chapter boot success is no longer accepted as evidence for continuous transition integrity. PG-124 protects the audit wiring while preserving the startup-grounding markers.

This remains **IMPLEMENTED / STATIC-PENDING** until the exact integration head passes Pre-Unreal. UE4 engine execution remains a separate gate.

## 2026-09-21 - comprehensive foundation integration train active

The owner directed the project to stop accumulating isolated proposals/repair branches and resume coherent construction. The active convergence branch is now `integration/comprehensive-foundation-v1`, recorded by `REQ-INTEGRATION-001`, `DEC-031` and `WORK-INTEGRATION-001`.

The branch currently integrates the startup-grounding/QA/performance stack with V10 regional living-world work and a stronger transactional transition model. Chapter asset streaming is now two-phase: preload completion does not replace the resident bank. `ChapterWorldRouter` freezes the player only at the swap boundary, constructs the destination, proves blocking-ground placement, commits the pending asset bank, then publishes a new `WorldRevision`. Failure does not publish a revision and attempts to restore the prior builder while keeping movement held.

`LivingWorldDirector` now combines V10 chapter density/role profiles with committed-world synchronization. Quest state may move ahead while streaming, but destination residents/weather/context are not applied until the router publishes the matching committed revision.

PG-123 statically protects the integrated two-phase asset/world/living-world contract. This is **IMPLEMENTED / STATIC-PENDING** on the newest integration code. It is not COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or visually accepted until exact-head gates run.

## 2026-09-21 - visual-performance proposal adopted with measured guardrails

A new programmer proposal for Witcher-class visual ambition with low-spec UE4.27 optimization was reviewed against the live architecture and promoted into durable project memory as `EXT-REV-2026-09-21-017`, `REQ-PERF-003`, `DEC-030` and `WORK-PERF-006`.

Useful parts are active now: preserve soft/asynchronous heavy-asset ownership, HISM/ISM + explicit culling for repeated detail, non-ticking world builders, and no heavy synchronous work inside Tick. `Scripts/deep_project_audit.py` now protects those already-working architecture contracts and `Data/VisualPerformanceOptimizationPlan.json` records the staged optimization path.

The proposal was not copied literally. Current generated chapter geometry makes blanket Lightmass inappropriate; Distance Field Shadows are not assumed cheaper on the ~2 GB VRAM target; World Composition will not replace the working ChapterWorldRouter/async-bank architecture without a measured topology need; LOD/material policies remain role- and profile-driven.

This wave is **STATIC-PENDING** until the exact branch head passes Pre-Unreal. No FPS, VRAM, device, PIE or visual improvement is claimed yet.

## 2026-09-21 - QA immune-system foundation implementation

The first `REQ-QA-002` implementation wave is now in source on dependent branch `qa/automated-immune-system-v1`. `ShireJourneyEditorTools` contains two initial Unreal Automation Framework tests: `ShireJourney.QA.Save.DefaultState` and `ShireJourney.QA.Assets.StreamingBankPackages`. The first checks SaveGame schema/default invariants; the second checks that every soft-path package declared by `ChapterAssetStreamingPlan.json` exists after the production import step, without synchronously loading those heavy assets.

`ci_run_project_automation.cmd` runs the suite through UE4Editor-Cmd and `parse_automation_report.py` rejects missing or failed required test results. The self-hosted workflow places this new engine-level layer after compile/import and before existing runtime startup/chapter/state audits.

The P1C01 fall-through regression is also strengthened: placement now logs `PLACED`; CI only receives `ShireStartupGrounding: PASS` after two seconds with blocking ground, no falling movement mode, and bounded displacement. This prevents an immediate line trace from being mistaken for sustained grounding.

Evidence boundary: **IMPLEMENTED / STATIC-PENDING** until Pre-Unreal runs on the exact head. No COMPILE-TESTED or PIE-TESTED claim is made.

## 2026-09-21 - automated QA immune-system direction adopted

The owner supplied a programmer proposal to expand CI into a broader automated QA immune system. The direction is adopted after live-repository review, with project-specific corrections recorded in `EXT-REV-2026-09-21-016`, `REQ-QA-002`, `DEC-029` and `WORK-QA-003`.

The first implementation wave is deliberately dependent on the active startup-grounding repair rather than competing with it. It will add UE Automation Framework tests and an exact-head runner after compile/import, while preserving `runtime_smoke.py` as the end-to-end chapter/state layer. Deterministic authored probes replace random-point tests; target-device measurements will set memory/hitch thresholds; headless checks do not become visual acceptance.

Status before code wave: **PLANNED / STATIC-PENDING**.

## 2026-09-21 - deterministic P1C01 spawn support

The startup-grounding repair now also removes imported-mesh collision from the first-frame dependency. P1C01 receives a hidden Engine BasicShapes collision pad centered at the authored start `(-2410,-120)` with its top at the authored road height. The larger hidden Shire collision foundation remains underneath the region. This means initial grounding can succeed even if the imported OBJ road/ground mesh has no usable generated simple collision.

This remains a **FIX_CANDIDATE**. No claim is made that the owner-observed fall-through is resolved until exact-head engine validation and defect-specific P1C01 PIE observation pass.

## 2026-09-21 - startup fall-through root cause and regression repair

Owner reproduced a previously claimed startup fix as still broken: on first PIE launch the player can fall below the world. Source inspection identified the ordering defect. `AShireGameMode::BeginPlay` teleported the pawn to P1C01 coordinates immediately, while `AChapterWorldRouter` intentionally waits for asynchronous chapter asset streaming before spawning the Shire world. Raising the spawn Z did not close that race because there can still be no blocking ground under the pawn when gravity begins.

The isolated repair branch `fix/startup-grounding-regression-v1` removes the GameMode pre-commit teleport. ChapterWorldRouter now holds initial character movement while the first bank streams, moves the pawn only after the builder commits, line-traces a blocking floor, places the capsule from the measured floor height, and releases movement only on success. Missing ground fails closed with `ShireStartupGrounding: FAIL` rather than allowing indefinite falling.

Automation now requires a chapter-specific `ShireStartupGrounding: PASS` marker for normal startup, state audit and P1C01-P1C08 chapter audits. PG-121 rejects reintroduction of the old pre-commit GameMode teleport.

Status is **FIX_CANDIDATE / STATIC-PENDING** until the exact branch head passes Pre-Unreal. It is not COMPILE-TESTED or PIE-verified. The self-hosted Unreal runner also has a separate local UE4 Engine Content file-access blocker that must be repaired before engine proof can complete.

## 2026-09-21 - path cleanup before post-V5 production

Authority remains `Data/ProjectGovernor.json`. The integration baseline is `develop` at `8d7247d229b5cd51e8aea5617e1e2030b38229bf`, green after PR #60 with Pre-Unreal #532 and Unreal Build #367. There is exactly one open production PR: #61, `production/chapter-streaming-v5`.

The latest V5 code head before this cleanup is `b882b052a59c8d4e19437d7877dc30c9b1ea5daf`. Pre-Unreal #538 passed; Unreal Build #373 was pending when this reconciliation was written. Earlier V5 failures were narrowed to concrete UE4.27 issues and repaired: the `FStreamableHandle` declaration conflict (#370), invalid conditional `UE_LOG` verbosity (#371), and a stale async completion edge case after returning to an already resident world. This cleanup commit is newer than those checks and must earn fresh exact-head proof.

The path is now explicit: finish V5 -> merge only after exact-head Pre-Unreal + full Unreal validation -> confirm develop returns green -> measure chapter seam hitch/streaming pool/resident memory on representative target hardware -> open the next short production branch. No V5 FPS/RAM/VRAM improvement is claimed from architecture alone.

The next production branch is intentionally focused on visible world life rather than another mixed mega-branch: Shire, Bree, Rivendell and Lothlorien first for architecture density, culture-specific dressing, bounded NPC density, routines and ambient life. The character-quality lane advances through real skeleton/skin/Skeletal Mesh/AnimBP/animation work; OBJ-to-FBX container conversion alone is not treated as rigging.

Repository hygiene was reconciled. PR54 and PR56-PR60 short branches are historical cleanup candidates after external-reference checks. `recovery/stached-charcter` and `repair/post-merge-unreal-339` are preserved. The scheduled "Develop 20-Min Validation" appearing under `main` is expected GitHub scheduler behavior because `main` is the default branch; that workflow explicitly checks out `develop` and does not change the rule that production work integrates through `develop`.

## 2026-09-20 — V6 continuation and source/governor audit

Authority remains `Data/ProjectGovernor.json`. Its previous handoff was stale at #303; the actual verified baseline is `cd58be1e1cea033295a163ef2a90985f30471c2b`, Pre-Unreal #484 and Unreal #319, including import/startup/eight chapters/state/save/warnings. V6 head `93092a82b95418552728c73e02d31c220a7457ac` passed Pre-Unreal #485. Unreal #320 attempt 1 was interrupted during UHT/build (Ctrl-C, -1073741510); this is not a demonstrated C++ code defect. The single rerun (attempt 2) was also interrupted, before compilation at the editor-wait step. The cancellation trigger is not established; no further blind reruns were requested.

V6 refines original modular head/torso/hair geometry for nine Fellowship characters; it is not final skeletal animation or visual acceptance. Preserve that distinction.

The Governor now validates exact SHA scope for baseline/current workflow evidence and prints when a checkout is not covered by the recorded snapshot. A successful ancestor cannot silently certify the current checkout. Six regression cases cover mixed SHA evidence, cancelled current runs, invalid green baselines and missing experiential boundaries.

Uploaded source identities were verified against the reference index. Bible 09 now has its fingerprint. Targeted review of story, mission and visual-reference guidance confirms safe optional windows, explicit mission state/QA and the separation of visual inspiration from canon. The reference books' F1-xx identifiers do not equal runtime P1Cxx identifiers; numeric suffix matching is unsafe. Full scene-level provenance and rendered/device acceptance remain open. Green #319 still carries 132 unique near-zero-binormal identities under the existing 150 limit; passing the warning guard does not mean zero asset debt.

## 2026-09-20 — final lightweight geometry-warning cleanup

The green #302 baseline still carried 50 degenerate-tangent and 53 nearly-zero-binormal import identities. Inspection of representative production OBJ sources confirmed that these flat-color meshes have no `vt` texture-coordinate records. MikkTSpace therefore had no valid UV basis and was generating warning debt that did not improve the current material path.

The production importer now detects untextured OBJ meshes and explicitly computes normals with UE4's built-in tangent generator while keeping MikkTSpace/default behavior available for any future OBJ that actually supplies texture UVs. The exact-head chain must prove the warnings are removed before the debt is marked fixed or warning ceilings are tightened.

Two obsolete bootstrap/checkout PowerShell scripts are removed in the same cleanup because the workflow now bootstraps and checks out safely before repository scripts are available.

## 2026-09-20 — warning evidence scope repair

Run #300 confirmed the material persistence repair itself works: 225 authored material packages were explicitly saved with zero failures and the commandlet verified zero missing physical files. The warning gate remained red because import-time `LoadObject` existence probes intentionally asked for not-yet-created material packages, generating 216 warnings before synthesis.

That is now corrected at both ends: importer probes use `FindObject` plus `FPackageName::DoesPackageExist` before any load, and missing-package debt is evaluated from runtime startup/chapter/state logs rather than the import log. Exact-head CI logs are also cleared before each run so stale evidence cannot contaminate a new SHA.

The runtime missing-world-package ceiling is now zero. Any package that is genuinely absent after import will still fail the gate.

## 2026-09-20 — exact-head material persistence final blocker

Run #299 proved the entire machine chain through real UE4.27.2 build/import/startup, P1C01-P1C08 and isolated disk save/state roundtrip. The only failing gate is warning debt: 216 unique world material packages are referenced by imported meshes but are absent on disk.

The importer already synthesizes the intended authored material instances. The repair now bypasses unreliable unattended editor save helpers for these packages and writes each package explicitly with `UPackage::SavePackage` to its deterministic `.uasset` path, then verifies physical file existence before the commandlet can report success.

No threshold was raised and no debt was hidden. The next exact-head run must prove this repair.

## 2026-09-20 — mega-wave runway repair

The pre-production runway was repaired before the next mega build wave. REQ-AUDIT-001 is now represented in the master roadmap/tracked snapshot, PG-037 validates the new asynchronous checkpoint contract, and the Windows UE4 CI target now uses project-only clean intermediates, single-action compilation and CI-only disabled debug symbols to remove the recurring VS2019 D8050 debug-record failure mode. Local developer/editor builds retain normal debug symbols.

This is preparation, not a green claim: the new exact head must still pass Pre-Unreal and the real UE4.27.2 compile/import/startup/eight-chapter/state/warning chain.

## 2026-09-20 — deep exact-head validation reconciliation

Exact head `c023a735e3e390b8d591e1f6df9d07aeaa054754` reached the strongest automated evidence chain so far: Pre-Unreal #450 passed, and Unreal Build Validation #285 passed the isolated MSVC probe, UE4.27.2 C++ build, production asset import, Python resolution, playable startup, every P1C01-P1C08 chapter audit, and the route/story/state audit with an actual isolated disk save/load roundtrip.

The workflow failed only at warning-debt aggregation. Audit of the guard found a validation-harness defect: identical tangent/binormal warnings copied through multiple CI logs were counted repeatedly as separate debt. The guard now counts unique mesh/package identities and prints those identities. This does **not** waive real asset debt; it makes the next repair target exact instead of occurrence-inflated. The remaining world-package identities will be repaired from the next rerun.

No rendered/PIE visual acceptance, FPS claim or Production 100 promotion is made from this machine evidence.

## 2026-09-20 — MSVC execution blocker

Runs 35500465321 and 35500597711 failed with MSVC D8050 (`failed to get command line into debug records`) across compilation actions, also on single-process retry. This has not yet tested the new disk-audit C++ code. The workflow now prepares a writable per-run TEMP/TMP and probes one-line C++ compilation with plain, /Z7 and /Zi settings before invoking UnrealBuildTool. These are job-local changes only; compiler failures remain failures and no debug verification is disabled.

## 2026-09-20 — state fixture correction after eight chapter passes

Run 35500242164 passed startup and all eight chapter audits. The state audit exposed an outdated test fixture: `StartExperience` correctly restores stored route progress, so calling it on the initial Frodo route did not advance to P1C03; the fixture also bypassed the activity reward entry point. The audit now explicitly starts P1C03, verifies the closed activity window rejects reward, opens `MidgewaterRoad`, verifies direct reward bypass is rejected, then completes the activity through its guarded API and verifies duplicate reward rejection. Required expected reward values remain unchanged. This fixes the test setup without weakening production story/reward guards. Full rerun remains required.

## 2026-09-20 — close the disk persistence evidence gap

The Python resolver repair passed on Windows and startup succeeded on `15e9d2228f6e7e5ceb1e8aed2aab8b698dba4cb8` ([run 35500242164](https://github.com/4youbabee-tech/fellowship-personal-game/actions/runs/35500242164)). Chapter/state checks were still running when this update was written.

Source audit confirmed the existing route/state test did not write a save file. The new `disk-save-roundtrip` audit calls the production player snapshot/restore path, writes a unique CI save slot, mutates live quest/progression/knowledge/player values, loads from disk, verifies restored fields, and deletes only its own temporary slot. It checks health/stamina/resolve/supplies, transform, route/chapter/episode/character, quest stages, story beats, discoveries, progression and Chronicle/map knowledge. It is not yet full NPC-memory or cross-process migration coverage. The observer requires the disk marker for state success. CI runs cannot overwrite or load the owner's manual/checkpoint slots. Thirteen observer tests pass locally; real UE compilation and disk execution of this change remain pending.

## 2026-09-20 — exact-head runtime validation repair

Authority: `Data/ProjectGovernor.json`, including `session_handoff`.

On `b0a4d2614e5744d8a0fa3b1c373c23a491274955`, Pre-Unreal #446 passed. Unreal run [35499375838](https://github.com/4youbabee-tech/fellowship-personal-game/actions/runs/35499375838) built UE4.27.2 C++ and imported production assets successfully. Runtime audits did **not** execute: Python discovery selected a Microsoft Store alias and exited 61.

The repair validates local interpreter candidates, excludes WindowsApps aliases, checks installed/launcher/toolcache/UE-bundled interpreters, and supports Python 3.7 in the observer. It neither installs software nor modifies Windows settings. State audit now has a separate log from startup. Twelve observer regression tests pass locally; Windows execution and full runtime proof remain pending the new CI run.

Next: complete exact-head startup, all eight chapters and actual save/load proof; only then resume visible production. No new visual, performance or gameplay acceptance is claimed.

## PHYSICAL SIDE-ACTIVITY GAMEPLAY WAVE — 2026-09-20

B1 now includes reusable physical challenge gameplay instead of relying entirely on proximity discovery triggers. `AShireTraversalChallenge` implements an ordered three-gate route, verifies opening/closing story beats, awards only the linked first-time Journey Discovery, and therefore feeds the existing Chronicle/map/progression systems without changing FILM_CORE.

The Shire field race now uses the ordered route and completes `Side_SharedShireMemory` only after the route. Moria's `MORIA_ECHO_ROUTE` now uses the same mechanic for Follow the Echo before MoriaUnease closes the optional window. PG-081 guards both runtime placements.

This is implementation evidence; exact-head UE4.27 compile, runtime placement and PIE pacing remain required.

## CHRONICLE + MAP KNOWLEDGE + SIDE-ACTIVITY PROGRESSION MEGA-SLICE — 2026-09-20

B1 expanded again from plan-only into persistent runtime. First-time Journey Discoveries now create main-film Chronicle entries and mark the current route/chapter as known map knowledge. Both collections persist through save schema v6. Book Chronicles remain explicitly separate and are not inserted into this main-film runtime registry.

The C key now opens a Chronicle & Journey HUD panel showing recent Chronicle entries, known regions, Journey Insight and all seven progression tracks/ranks. Contextual side activities are also parsed at runtime: when a linked first-time discovery completes, its authored activity type adds bounded XP (for example CAMP_PREPARATION -> CAMPCRAFT, TRACKING/OBSERVATION -> PERCEPTION, SOCIAL_MEMORY -> FELLOWSHIP). Anti-farm behavior remains first-time-only.

State automation now requires `ShireStateAudit: knowledge-core=PASS`, and PG-080 checks save/UI/input/continuity/side-activity wiring. Exact-head UE4.27 compile/import/startup/state evidence remains required before engine validation is claimed.

## PLAYER-LIFE + PROGRESSION RUNTIME MEGA-SLICE — 2026-09-20

B1 modern-game work is now runtime, not only planning. The player has lightweight Stamina, Ring-pressure-sensitive Resolve and capped travel Supplies alongside Health. Sprinting drains/rebuilds Stamina; damage and Ring pressure affect Resolve; R consumes one supply only when recovery is useful. No hunger/thirst timers, gear score or random rarity loop was introduced.

Seven persistent progression tracks now exist: WAYFINDING, PERCEPTION, QUIET_STEP, CAMPCRAFT, FELLOWSHIP, LORE and RESOLVE. First-time Journey Discoveries award track XP by category, so repeated discovery cannot farm progression. Fellowship Bond is derived from the FELLOWSHIP track. Save schema v5 persists life state and ProgressionXP.

PG-079 guards the full contract and state-mode automation requires `ShireStateAudit: progression-core=PASS`. Exact-head UE4.27 compile/import/startup/state proof is still required before this becomes engine-validated.

## MASTER EXECUTION CONTROL — 2026-09-20

The growing request set is now consolidated into `Data/MasterExecutionRoadmap.json` and the human board `Docs/MASTER_EXECUTION_BOARD.md`. The roadmap is subordinate to the Governor and maps every unfinished requirement plus every ACTIVE work item into large dependency-ordered production bundles. PG-078 makes orphan accepted work a static-validation failure.

Execution order is now explicit: exact-head stability; Part I story/gameplay completeness; production characters/world; living-world/presentation; acceptance/merge; then source-verified Part II/III. Active work items have unique execution ranks/bundle labels so the project no longer behaves like a flat unordered list.

## FILM SIDE-CONTENT MASTER AUDIT — 2026-09-20

The owner supplied a programmer proposal covering trilogy-wide side play and asked for one reconciled, future-proof request set. `Data/FilmSideContentMasterPlan.json` is now the side-content master taxonomy: FILM_MOMENT = verified film action turned into gameplay; FILM_EXPANDED = small plausible play around an existing film scene/place; CHRONICLE = book-only/history/past-character content kept visibly separate from Film Main Canon.

The audit also records continuity corrections: Fellowship does not literally begin at the birthday party; Weathertop fire cannot prevent the Nazgul attack; Prancing Pony attention cannot avoid the Ring incident; Moria's door is a guided canonical puzzle; Entmoot side play cannot replace the film decision causality; Oliphaunt observation does not grant a canon-breaking future weakness; Return of the King's beacon prototype centers on Pippin lighting the Minas Tirith beacon; Glorfindel/Scouring stay Chronicle-only.

PG-077 guards taxonomy/canon separation. Runtime rollout remains behind the current exact-head UE4.27 validation gate.

## SIDE-CONTENT CANON AUDIT — programmer proposal reconciled

The programmer's trilogy proposal is retained but normalized into four continuity classes: FILM_CORE, FILM_EXPANDED, FILM_INTERSTITIAL and BOOK_CHRONICLE, with source-verification tracked separately. The audit corrects one important opening claim: Fellowship does not begin at Bilbo's party; the prologue and Bilbo/Frodo-Gandalf opening precede it.

Part I and Part II entries are now source-audited against the supplied screenplays/project canon where available. Part III remains FUTURE_SOURCE_CHECK at scene level. Book-only Tom Bombadil/Barrow-downs, Glorfindel-at-the-Ford and Scouring content is explicitly isolated from main film continuity. PG-077 protects this separation.

## ENSEMBLE FILM MISSIONS — 2026-09-20

Frodo remains the Ring-quest center, but the film itself now decides who should be playable for each event. `Data/EnsembleFilmMissionPlan.json` maps Gandalf, Arwen, Aragorn, Boromir, Legolas, Gimli and later Merry/Pippin/Sam/Faramir/Eowyn opportunities. The design rule is film action first, character-specialty gameplay second, small original gap-fill last.

Part III mission details remain source-check-only until exact film/script verification. PG-076 guards the ensemble contract.

## ENSEMBLE FILM-MISSION RULE — 2026-09-20

The owner clarified that the film itself already supplies many mission opportunities outside Frodo. Frodo remains the Ring-quest center but is no longer treated as the default controller for every event. `Data/EnsembleFilmMissionPlan.json` now prioritizes playable film actions for Gandalf, Arwen, Aragorn, Boromir, Legolas, Gimli, Merry/Pippin and later-film characters, then allows only small source-safe gap-fill around those verified scenes.

Part I now explicitly identifies Gandalf Ring investigation/Isengard, Arwen at the Ford, Boromir training and Amon Hen defense, Legolas scouting, Gimli/Moria cultural gameplay and Aragorn scouting/leadership as viewpoint opportunities. Part II maps the Three Hunters, Merry/Pippin/Fangorn, Gandalf/Rohan and source-checked Faramir/Eowyn focused episodes. Part III remains FUTURE_SOURCE_CHECK at mission-detail level until exact film/script verification is available.

PG-076 protects viewpoint/source/canon rules. This is a production/design contract; runtime mission handoffs and character-specific mechanics remain pending implementation and UE4.27 proof.

## MODERN GAME LAYER LOCKED — 2026-09-20

The owner explicitly requested a broad modern-game research pass and adoption of fitting game systems throughout the film-based experience. `Data/ModernGameLayerPlan.json` now locks the rule: mandatory Peter Jackson film anchors stay fixed, while optional play may expand only inside story-safe gaps.

The plan adapts modern design patterns - meaningful exploration rewards, short world events, semi-open chapter hubs, companion dialogue during free play, earned map knowledge, environmental/traversal puzzles and reactive inhabitants - into original Middle-earth gameplay. Character life is also defined beyond a health bar through bounded Stamina, Resolve, Fellowship Bond and Supplies, with progression in Wayfinding, Perception, Quiet Step, Campcraft, Fellowship, Lore and Resolve. Survival micromanagement, gear-score grind, loot spam and canon-changing upgrades are explicitly excluded.

P1C01-P1C08 plus P1G01 now each have chapter-specific optional activity families while fixed film outcomes remain mandatory. PG-075 guards this contract. Runtime rollout remains staged and exact-head UE4.27 evidence is still required before any implementation is called validated.

## JOURNEY DISCOVERY RUNTIME MEGA-SLICE — 2026-09-20

Journey Discovery has moved beyond a static design contract. The existing quest subsystem now owns a data-driven first-time discovery registry loaded from `Data/JourneyDiscoveryRewardPlan.json`; all 26 current Part I discoveries are wired into Shire, Bree, P1C03-P1C08 and Isengard world triggers with explicit opening/closing story-beat windows. Rewards derive Journey Insight, region-completion bonuses and milestones without changing required story state.

Discovery IDs/Insight/milestones now persist through the existing save/load path with sanitation on restore. A dedicated HUD discovery card presents the first-time reward separately from combat/error alerts. State-mode automation also requires `ShireStateAudit: discovery-core=PASS`, proving a discovery cannot be farmed by repeat activation and survives the Frodo/Gandalf/Frodo route roundtrip in subsystem state.

This remains implementation evidence until the exact current PR head passes real UE4.27 compile/import/startup/chapter/state validation.

## MEGA-PASS RED-TO-GREEN REPAIR — current exact head

Intermediate head `5699ef0` passed Pre-Unreal Validation #348. The previous Unreal engine attempt reached real compilation and exposed a UE4.27-specific incompatibility in the new non-destructive production importer: `IFileManager::CopyDirectoryTree` is not available there. The importer now keeps the same safety design but uses UE4.27-compatible `IPlatformFile::CopyDirectoryTree`.

The current exact head is intentionally still pending validation. No merge, compile-success, import-success or visual acceptance is claimed until the new head completes the full gate.

## MEGA PRODUCTION BATCH — RING / CHARACTERS / CINEMATIC WORLD — 2026-09-20

The owner closed Unreal and ordered immediate large-scale continuation. This batch turns three previously discussed directions into durable production contracts. The One Ring is now a CRITICAL systemic axis with a runtime bearer/state/pressure API and a headless route-roundtrip audit requirement. The full Part I named cast is now tracked through a model → material → rig → skin → animation → UE4 → LOD pipeline with provenance rules and a custom-character fallback. Every active Part I region now has a cinematic hero-vista and layered foreground/midground/background target based on the owner's dense forest reference.

New production authorities: `Data/TrilogyRingQuestPlan.json`, `Data/CharacterProductionMatrix.json`, `Data/CinematicWorldProductionMatrix.json`, and `Data/OwnerSourceReferenceIndex.json`. Static guards PG-070 through PG-073 protect the new contracts.

Proof boundary remains strict: these are source/data/runtime implementation changes. They are not yet UE4.27-validated or visually accepted until the exact PR head passes Pre-Unreal and real engine validation.

## WORLD BEAUTY BAR RAISED — 2026-09-20

The owner rejected the earlier plain reference-image quality as the final target. The project now explicitly targets a more beautiful cinematic world: layered vistas, richer terrain/materials/vegetation, stronger water/fog/light atmosphere, hero landmark composition and region-specific visual identity. This does not relax the target-device budget; the visual strategy is selective hero detail plus LOD/instancing/culling so 720p Low-Medium / 30 FPS remains the floor target.

## CONTEXTUAL SIDE-PLAY CONTRACT — film story stays fixed, game expands between scenes

The owner reaffirmed the core rule: this remains the Peter Jackson film story. Original side content is allowed only as plausible off-camera gap-fill inside the same time, location, companions, knowledge and emotional/danger context. `Data/ContextualSideActivityPlan.json` now defines 18 optional mini-game/social/exploration activities across FrodoMain P1C01-P1C08 plus GandalfParallel P1C01.

Examples include Shire party errands and a friendship race, Bree observation/tracking, Strider trail-reading, Rivendell map/memory moments, Fellowship camp practice, West Gate stone observation, Moria echo navigation, Lothlorien grief/boat preparation, Anduin river reading, Amon Hen tension observation and Orthanc prisoner observation. Every activity is bounded between exact film story anchors, forbids future knowledge, cannot advance a required anchor, and yields only the existing Journey Discovery/Chronicle/dialogue-memory rewards.

PG-063 now guards those constraints statically. Runtime side-activity triggers, save/UI wiring and UE4.27 play validation remain pending; the exact-head merge gate is unchanged.

## JOURNEY DISCOVERY SYSTEM — exploration now has persistent game rewards

The owner requested the satisfying feeling of discovering a place and receiving a bonus, similar in spirit to exploration RPGs, but adapted to this world's tone. `Data/JourneyDiscoveryRewardPlan.json` now maps 26 declared optional discoveries to first-time Journey Insight rewards. Rewards prioritize Chronicle entries, map memory, lore/dialogue topics, companion memories and local hazard knowledge rather than generic combat-stat inflation.

Four thematic tracks keep the system in-world: Road Wisdom, Peoples and Places, Fellowship Bonds and Peril Sense. Every active Part I exploration route/chapter also has a region-completion bonus. Milestones unlock subtle navigation/content benefits, never story skips or alternate canon outcomes. PG-062 enforces one-time rewards, complete discovery coverage, no canon mutation and packaging.

Runtime trigger/save/HUD/Chronicle wiring is still pending; this commit is a static/game-design contract while Unreal remains busy. Full acceptance still requires UE4.27 and save/load automation on the exact final head.

## PARALLEL NON-UNREAL MEGA-PASS — shader-compile time used productively

While the target machine is busy compiling shaders, CP56 continues with work that does not require interrupting the editor. `Data/ExplorationEnvelopePlan.json` now defines safe free-roam windows, optional discoveries and return-to-main-story behavior for FrodoMain P1C01-P1C08 plus GandalfParallel P1C01. PG-060 checks that optional exploration cannot reorder, advance or replace mandatory film-story anchors.

The source-grounded original dialogue bank has also expanded from 26 to 53 validated variants across Shire, Bree, wilderness, Rivendell, Fellowship travel, Moria, Lothlorien, Amon Hen and Isengard. PG-061 locks in the production-import hygiene fix: OBJ normalization/import must operate on an ignored `Saved/` working copy rather than dirtying tracked `SourceAssets`.

This is productive parallel work, not a merge bypass. The final PR #53 exact head still must pass Pre-Unreal plus UE4.27 compile/import/startup/chapter/state/warning validation before integration into `develop`.

## CP56 SOURCE-GROUNDED LIVING DIALOGUE MEGA-PASS - 2026-09-19

The owner-supplied Fellowship and Two Towers screenplay PDFs are now durable story/dialogue reference sources. `Data/FilmDialogueSourceContext.json` stores only derived context: source identity/hash, scene windows, route/chapter/story-beat progression, tone, safe topics and future-knowledge blocks. Runtime dialogue remains original and offline; raw screenplay passages are not shipped.

Part I contexts cover P1C01-P1C08 plus Gandalf's Isengard route. The Two Towers source is indexed into future Part II arc seeds for Frodo/Sam/Gollum, the Rohan hunters, Merry/Pippin/Ents, Gandalf/Rohan and Saruman/Isengard, without claiming Part II runtime completion.

PR #53 still requires exact-head Pre-Unreal and UE4.27 validation before merge.

## CP56 MEGA INTEGRATION ACTIVE — whole-game coherence pass

PR #53 is the single continuation path above PR #52. The mega batch is tracked by `REQ-MEGA-001`, `WORK-MEGA-001`, `Data/CP56MegaIntegrationPlan.json` and `Data/GameCompletenessMatrix.json`.

Current runtime expansion now reaches named-character behavior, not just data: companion spacing and catch-up respond to regional pressure, named profiles expose a personality-aware emotional state, free interactions choose mood-aware intents with deterministic greeting fallback, and authored regional dialogue covers Shire peace, Bree suspicion, pursued wilderness, Rivendell refuge, Fellowship pressure, Moria dread, Lothlorien grief/refuge, Anduin fracture and Isengard corruption. All shipped logic remains offline and subordinate to story, knowledge and memory gates.

This does not claim final rigs, voice, materials, device performance, cinematic acceptance or trilogy completion. The merge gate is unchanged: the current PR #53 head must pass Pre-Unreal plus the complete UE4.27 compile/import/startup/chapter/warning chain before develop integration.

## CP56 continuation — contextual companion dialogue, 2026-09-19

Recovered prior-session stopping point: CP56 head 3705fe4, PR52 awaiting Unreal. Its latest engine attempt failed during checkout, before compilation. Follow-up PR53 now includes the tracked-source checkout fix plus a correction to regional dialogue selection and 30 original Moria/Lothlorien companion lines. Actual engine build and gameplay validation remain pending. No new checkpoint or trilogy completion is declared.

## Automation-first delivery follow-up — 2026-09-19

REQ-QA-001 records the owner request to reduce manual technical testing. Runtime boot observation and subprocess regression tests are implemented on a follow-up branch based on CP56; Windows UE validation remains pending. See `Docs/AUTOMATION_FIRST_DELIVERY.md` for the trilogy/opening/side-exploration contract and ordered engine-test work. This adds no completed gameplay chapter and grants no new visual, performance or owner sign-off. Existing CP56 requirements remain active.

## CP56 ACTIVE — FELLOWSHIP EXPERIENCE MEGA-PASS

CP55 was merged after Pre-Unreal #273 and Unreal Build Validation #108 passed on the validated branch head. CP56 now expands moment-to-moment play while preserving the same Part I film chronology.

What CP56 changes now:
- P1C01 adds visible pre-adventure Shire friendship/play: Green Dragon revelry, party-field mischief, a shared-memory race/play beat, extra party revelers and play runners.
- P1C02 adds denser Prancing Pony/common-room life.
- P1C03 adds optional road companionship before Weathertop tension.
- P1C05 strengthens camp companionship around the Fellowship training stop.
- P1C06 adds a dead-city discovery beat without adding civilians/fauna to Moria.
- P1C07 adds a shared-grief clearing before Lothlorien story pressure.
- P1C08 adds a river-camp tension beat before the Fellowship fractures.
- `Data/FellowshipExperienceMegaPassCP56.json` and PG-058 preserve the film-spine/non-blocking contract.

Story rule remains unchanged: required film outcomes are fixed; optional friendship, exploration and local-life content fills the spaces between them. Dialogue remains original game writing rather than screenplay reproduction.

This is implementation-in-progress and still requires its own Pre-Unreal and real UE4.27 build/import/startup/chapter regression pass before merge.

## POST-VERIFICATION RESUME — CP55 OPENED

### CP55 activity/movement implementation

CP55 now adds a bounded visible world-life layer on top of the existing LivingWorldDirector:
- project-owned low-poly bird, rabbit and butterfly production meshes,
- distinct flight / hop-rest / flutter motion,
- chapter-aware fauna selection through disposable micro-events,
- no quest/save ownership and no persistent fauna transforms,
- Moria remains dead-city/fauna-empty by design,
- PG-055 guards the new plan/assets/runtime wiring.

Proof boundary: implemented in source/data/assets, but CP55 itself still requires its new Pre-Unreal and real UE4.27.2 compile/import/runtime regression pass before it is called validated.


The post-CP54 current-head verification freeze is now closed by explicit project-owner confirmation.

Verified merged baseline:
- `develop@f7c2b081e7b064fcf27bb4c80124b21f351331ab`
- Pre-Unreal Validation #264: SUCCESS.
- Unreal Build Validation #99: SUCCESS.
- UE4.27.2 build/import: SUCCESS.
- playable startup smoke: SUCCESS.
- headless P1C01-P1C08 chapter audit: SUCCESS.
- runtime warning-debt guard: SUCCESS.
- human verification/check/fix pass: owner-confirmed complete on 2026-09-19.

The owner sign-off is recorded in `Docs/PIE_VERIFICATION_SIGNOFF_2026-09-19.md` and `Data/PIEVerificationEvidence.json`. Numeric FPS/hitch/memory values that were not supplied are intentionally not fabricated.

Current development mode is restored to visible production/expansion. CP55 resumes environmental activity/movement and world-life depth while preserving story/save/route integrity, the 720p Low-Medium target, and the existing CI/UE4 regression gates.

## VERIFICATION MEGA-PASS — PR #45

The verification branch now has a successful real UE4.27.2 machine pass across all eight Part I runtime chapter boots.

Evidence on PR #45 before the hard-gate follow-up commit:
- Pre-Unreal Validation: SUCCESS.
- UE4.27.2 C++ build: SUCCESS.
- Production asset import: SUCCESS (307 imported files, 0 import failures).
- Headless playable startup: SUCCESS.
- Headless chapter audit: P1C01, P1C02, P1C03, P1C04, P1C05, P1C06, P1C07 and P1C08 all loaded their expected runtime builder plus living-world/weather context without a fatal/assert/ensure blocker.

This is a major machine-verification improvement, but it is deliberately **not** recorded as PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED.

The same verification batch now adds executable freeze enforcement (PG-056), structured human PIE evidence enforcement (PG-057), and a fast production-source asset-quality audit. This allows repair/verification work to continue quickly while CI rejects new checkpoint/content expansion during the freeze.

## IMMEDIATE FREEZE — current-head PIE/device verification

**Content baseline:** CP54 at `ed235ff4fb332660d2af8ce1385d9ca038a6337b`. **Develop head entering PR #45:** `043476f4353a44c1d08bf60ab87af5c3e10543f2`. Manual PIE evidence must always record the exact tested post-merge commit.

**CI evidence already green:** PR #44 Pre-Unreal #240 and Unreal Build Validation #75. This proves static validation, real UE4.27 compile/import and headless startup for the PR head. It does **not** prove current-head PIE traversal, visual quality, NPC behavior in play, save/load round trips, or target-laptop performance.

**Current rule:** no CP55 and no new feature/content batch until the existing CP24-CP54 body of work is inspected in real UE4.27 PIE on the target laptop, chapter by chapter.

Order:
1. P1C01 Shire
2. P1C02 Bree
3. P1C03 Weathertop/Ford
4. P1C04 Rivendell
5. P1C05 Road/Caradhras/West Gate
6. P1C06 Moria
7. P1C07 Lothlorien
8. P1C08 Anduin/Amon Hen

For each chapter record: WORKING / INTERMITTENT / BROKEN / CRASH, FPS/hitch/memory observations, NPC routines, ambient NPC-to-NPC conversations, named-NPC memory/context where applicable, and actual atmosphere/weather behavior.

Important implementation truth before testing:
- CP36 is ambient resident micro-life/props/gestures.
- CP38 is ambient NPC-to-NPC conversation.
- CP39 is the named-NPC memory **foundation**; memory-aware bounded dialogue was completed later in CP44.
- CP49 is the LivingWorldDirector/micro-event runtime.
- CP51 provides chapter-specific sun/skylight/fog profiles; final rain/snow VFX are still listed as open.
- CP53 adds continuous regional baseline populations.
- A true day/night cycle is not currently proven by the repository and must not be marked working unless observed/implemented.

Formal rights-holder outreach is deferred. Future asset effort, after the baseline audit, should go to visible quality and performance-safe materials rather than outreach.

Ideas discovered during this freeze belong in `Docs/WORLD_DETAIL_LEDGER.md`; do not implement them until the current baseline audit is complete.

## Current bulk-resource status — CP54

The repository now contains a much larger project-owned production bank instead of waiting for external acquisition. CP54 adds 75 new regional/common OBJ meshes, 17 procedural BMP textures, regional MTL palettes and runtime placement across all P1C01-P1C08 world builders.

Machine-readable authority:
- `Data/WorldResourceBankCP54.json`

Validation boundary:
- source bank: implemented on `mega/activity-movement-v1`,
- PG-054: pending CI,
- UE4.27 compile/import: pending CI,
- headless startup: pending CI,
- PIE/device visual and performance acceptance: pending.

## Current mass-content production status — CP50

The project is now in a comprehensive visible-content phase. Backend foundations remain implemented; active work is world density, materials, character animation production, interiors, lighting and audio.

CP50 adds a reusable common environment kit plus deterministic regional dressing across P1C03-P1C08. The intent is to move the game away from landmark-only prototypes and toward continuous readable environments without changing story topology.

Machine-readable visual-density authority:
- `Data/WorldDressingPlan.json`

Current proof boundary:
- source/runtime integration: implemented on the CP50 branch,
- Pre-Unreal / UE4.27 build-import: pending for CP50,
- PIE/device visual acceptance: pending.


## Current character-motion and atmosphere status — CP51

CP51 is the next visible-production layer after CP50. The runtime now has a safe skeletal-rig handoff contract for named characters plus richer procedural fallback motion, and P1C03-P1C08 have distinct bounded sun/sky/fog profiles.

Machine-readable authorities:
- `Data/CharacterMotionPlan.json`
- `Data/ChapterAtmospherePlan.json`

Current proof boundary:
- source/runtime integration: implemented on `mega/atmosphere-character-motion-v1`,
- Pre-Unreal validation: pending on the CP51 branch until CI completes,
- UE4.27 compile/import: pending,
- PIE/device visual acceptance: pending.

## Current mass-integration status — CP52

CP52 is intentionally larger than the previous incremental passes. The playable runtime now reuses the shared production resource family across the Shire, Bree and P1C03-P1C08, and the build rules explicitly package the living-world/production data needed outside the editor.

Machine-readable authority:
- `Data/ResourceIntegrationPlan.json`

Playable startup remains:
- route: `FrodoMain`,
- chapter: `P1C01`,
- first quest: `ShireArrival`,
- runtime world: `AChapterWorldRouter`,
- ambient runtime: `ALivingWorldDirector`.

External-resource truth boundary:
- the sourcing pipeline supports approved/licensed resources,
- `Data/ExternalAssetManifest.json` currently contains zero approved asset records,
- CP52 therefore uses all currently available project-owned production resources and does not fabricate external approvals.

Current proof boundary:
- source/runtime integration: implemented on `mega/resource-saturation-playable-v1`,
- Pre-Unreal PG-052: pending CI,
- real UE4.27 compile/import: now triggered on the CP52 pull request,
- headless playable boot smoke: now part of Unreal Build Validation and requires GameMode + P1C01/FrodoMain markers,
- PIE/device playability and performance: pending.
- runner autostart: post-reboot verification trigger issued on 2026-09-19.

## Current world-life status — CP53

The game has moved beyond isolated ambient encounters. CP53 keeps a chapter-specific baseline population alive around the player and layers denser micro-events on top of it, while reusing the existing schedule/social/awareness runtime and distance-based tick throttling.

Population targets:
- P1C01 Shire: 18
- P1C02 Bree: 16
- P1C03 Weathertop/Ford: 5
- P1C04 Rivendell: 12
- P1C05 Caradhras/road: 6
- P1C06 Moria: 0 civilians
- P1C07 Lothlorien: 10
- P1C08 Anduin/Amon Hen: 6

Machine-readable authority:
- `Data/WorldLifeSaturationPlan.json`

Current proof boundary:
- source/runtime integration: implemented on `mega/world-alive-saturation-v2`,
- Pre-Unreal PG-053: pending CI,
- real UE4.27 compile/import: pending CI,
- headless startup: pending CI,
- PIE/device crowd density and FPS acceptance: pending.
- resource flood: 15 new project-owned low-poly meshes are now source-controlled and runtime-wired across P1C01-P1C08.

# CURRENT PROJECT STATE

> **Operational recovery note — reconciled 2026-09-19**
>
> Current production baseline now includes CP44 backend completion, CP45 named-cast dedicated modular identities, CP46 threat production art, CP47 licensed asset sourcing, CP48 Weta/rights-holder/global resource mapping, and CP49 living-world/terrain engineering on its validation branch.
>
> The authoritative requirement/decision source is `Data/ProjectGovernor.json`. The machine-readable execution/dependency map is `Data/ProductionExecutionGraph.json`. Use `Docs/ENGINEERING_EXECUTION_PATH.md` for the human-readable implementation order.
>
> Older historical sections below are retained as evidence and may mention earlier heads/checkpoints. They must not be read as the latest status when they conflict with the Governor or this recovery note.


> **START HERE after a lost chat, a new developer handoff, or a long break.**
>
> This file is the operational snapshot of where the project is now.
> **Project-management authority lives only in `Data/ProjectGovernor.json`.**
> Story canon lives in `Docs/STORY_CANON_BIBLE.md`.
> Development rules live in `Docs/DEVELOPMENT_GATES.md`.
> Automated regression rules live in `Data/ProjectGuardRules.json`.
> World/chapter/checkpoint engineering lives in `Docs/WORLD_PRODUCTION_BLUEPRINT.md`.
> Machine-readable player checkpoint intent lives in `Data/WorldCheckpointPlan.csv`.

## Repository

- Repository: `4youbabee-tech/fellowship-personal-game`
- Active branch: `develop`
- Do not develop directly on `main`.
- Engine: Unreal Engine 4.27.2
- Target: Windows / DX11 / 720p / 30 FPS / Low-Medium
- Hardware floor: Intel i7 6th gen, 8 GB RAM, AMD GPU around 2 GB VRAM
- Local update/build/launch entry point: `SHIRE_UPDATE_BUILD_LAUNCH.bat`

Latest validated baseline before the current source-handoff governance maintenance:
- `e739ba6e364d0316cf5b7fe10c1f8ecaa13d417e` — `docs: sync CP30 handoff to validated head`
- Pre-Unreal Validation #113: **SUCCESS**.
- Unreal Build Validation #11: **SUCCESS** on the exact commit with UE4.27.2 C++ build and production asset import (`50 files, 0 failures`).
- CP30 world/checkpoint engineering is therefore STATIC-VALIDATED, COMPILE-TESTED and ASSET-IMPORT-TESTED. Dedicated automatic checkpoint/respawn runtime behavior remains planned, not implemented.
- The Shire visual content introduced at `8b0c13f...` still requires focused PIE/device review before VISUALLY-ACCEPTED.
- Intermediate CP30 commit `10ac91e...` had Pre-Unreal Validation #111 fail with `NameError: story_plan_ids is not defined`; `bd3d0be...` fixed that validator-order bug and restored both green gates.

Runtime-code baseline documented by this handoff:
`177f6cdbd073eaf0e2fd2c39da4a80fc82acf4ae`
(`world: add lightweight ambient NPC awareness`).

Documentation/guardian commits may naturally be newer than that runtime-code baseline.

## Validation vocabulary

Never say a feature is simply "ready". Record what was actually proven:

- **STATIC-VALIDATED**: GitHub Pre-Unreal Validation is green.
- **COMPILE-TESTED**: UE4.27.2 C++ build + UnrealHeaderTool succeeded.
- **ASSET-IMPORT-TESTED**: the UE4.27 production import commandlet completed successfully for the planned source assets.
- **PIE-TESTED**: relevant gameplay was exercised in Play In Editor.
- **DEVICE-TESTED**: relevant gameplay was exercised on the target laptop.
- **VISUALLY-ACCEPTED**: the user reviewed and accepted the visual/gameplay direction.

A green GitHub action is not a substitute for engine testing.

## Current proof level

Historically, an earlier project baseline:
- compiled and opened successfully in UE4.27.2,
- ran PIE,
- showed working movement, quest flow and HUD.

The current runtime-code baseline is now:
- **STATIC-VALIDATED** through Pre-Unreal Validation #80.
- **COMPILE-TESTED** on the target machine with UE4.27.2 after the PG-010/PG-011 fixes.
- **PIE-TESTED (BASIC BOOT ONLY)**: the Shire entered PIE successfully and rendered the current HUD.
- **DEVICE-TESTED (BASIC BOOT ONLY)** on the target laptop; full gameplay/performance acceptance is still pending.

Real UE4.27.2 validation history on 2026-09-18:
- Git update succeeded.
- UnrealHeaderTool completed successfully and generated reflection code.
- The first C++ build exposed:
  - C2660: one stale one-argument `MovePlayerToChapterStart` call.
  - C2440: direct base-to-derived light component pointer assignment from `GetLightComponent()`.
- Both source issues were fixed and converted into Project Guardian regression checks PG-010 and PG-011.
- A fresh build after those fixes completed successfully.
- Unreal Editor launched.
- PIE entered the Shire successfully.
- The HUD visibly showed:
  - `Frodo | P1C01_Main`
  - `An Unexpected Arrival`
  - `Reach the Shire lane and meet Gandalf.`

Additional PIE evidence on 2026-09-18:
- F5 Quick Save succeeded in PIE and displayed `Journey saved.`.
- UE4.27 emitted one runtime warning that the existing Directional Light had to be Movable before rotation.
- That warning was traced to `ConfigureMorningAtmosphere`, fixed by setting mobility before actor rotation, and recorded as Guardian regression PG-012.
- Quick Load (F9) is still pending verification.

CP22 milestone evidence on 2026-09-18:
- the enlarged Shire world-scale commit was pulled to the target laptop,
- UE4.27.2 Build completed successfully,
- no compile error was reported by the user,
- CP22 is therefore COMPILE-TESTED on the target laptop,
- the enlarged traversal itself still needs a focused PIE traversal/performance review.

CP23 milestone evidence on 2026-09-18:
- the living-world commits were pulled to the target laptop,
- UE4.27.2 launched into PIE successfully,
- the Shire rendered with Frodo / P1C01_Main, the opening objective and the enlarged world,
- The Mill landmark was visible,
- no compile/runtime error was reported for that launch,
- CP23 is therefore COMPILE-TESTED and BASIC PIE-TESTED on the target laptop.

Current post-CP23 source status:
- CP24A/CP24B voice/performance foundations, CP25 combat, CP26 biome/geography, CP27 runtime audio/proxy acting, CP28 production assets, CP29 self-hosted UE4 validation and CP30 world/checkpoint engineering are present in the current source.
- Current head `bd3d0be...` is STATIC-VALIDATED through Pre-Unreal Validation #112.
- Current head `bd3d0be...` is COMPILE-TESTED and ASSET-IMPORT-TESTED through Unreal Build Validation #10 on UE4.27.2 (`50 files, 0 failures`).
- The current head is NOT yet fully PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED.

The remaining hard gate is now the functional smoke-test layer: movement/interactions, F9 load round-trip, F8 route round-trip, chapter smoke tests and target-device performance/visual observation.

## Authoritative runtime chapter IDs

| Runtime ID | Chapter bucket |
| --- | --- |
| `P1C01` | Shire: Hobbiton, party, eastern fields, Black Rider road, ferry |
| `P1C02` | Bree |
| `P1C03` | Weathertop / Flight to the Ford |
| `P1C04` | Rivendell |
| `P1C05` | Fellowship road / camp / Caradhras / West Gate |
| `P1C06` | Moria: threshold, halls, Balin, Orc/Troll escalation, Balrog, bridge |
| `P1C07` | Lothlorien |
| `P1C08` | Anduin / Argonath / Amon Hen / Part I ending |

Do not reintroduce `P1C09`-`P1C12` as runtime chapter IDs.
Older planning used twelve narrative segments; those are now subregions/story segments inside eight runtime buckets.

## Current playable-route model

Main route:
- `RouteId = FrodoMain`
- episode convention: `P1C01_Main`, `P1C04_Main`, etc.
- playable character: Frodo

Parallel prototype:
- `RouteId = GandalfParallel`
- `EpisodeId = P1G01_Isengard`
- playable character: Gandalf
- region: Isengard / Orthanc

Per-route state is intended to preserve:
- quest stages,
- active quest,
- chapter,
- completed story beats,
- playable character,
- player transform.

A parallel route must not overwrite Frodo's main-route progress.

## Source-level handoff / architecture memory

The runtime module now has a code-local recovery entry point:
- `Source/ShireJourney/README.md` — start here when entering the runtime source tree.
- `Data/SourceArchitecturePlan.json` — machine-readable ownership/domain/target-path map for every runtime `.h`, `.cpp` and module `.cs` file.
- Project Guardian PG-019 requires the source handoff and architecture plan, and Pre-Unreal Validation rejects runtime source files that are missing from the manifest.

Current physical layout remains the guarded flat UE4.27 module. The planned maintenance layout is `Public/<Domain>` + `Private/<Domain>` with domains for Core, Characters, World, Subsystems, UI, SaveGame and Prototypes.

The physical folder migration has **not** happened yet. It must be a dedicated maintenance change, not mixed with gameplay, and must update includes plus static-validator path assumptions before a real UE4.27.2 build is accepted.

## Permanent user-requirement memory

The project no longer treats chat history as the authoritative record of user requests.

- `Data/ProjectGovernor.json` records persistent requirements with stable IDs, current status, evidence, missing work and acceptance criteria.
- `Docs/PROJECT_MEMORY_SYSTEM.md` defines how every meaningful future request must be captured and updated.
- `Docs/LIVING_WORLD_AI_BLUEPRINT.md` and `Data/LivingWorldFeaturePlan.json` preserve the user's living-world/NPC intelligence direction separately from current implementation status.
- Project Guardian validates the required memory artifacts and critical requirement/phase IDs.

Recovered/reaffirmed living-world intent is currently **PARTIAL/PLANNED**, not complete: ambient routines, awareness and social pauses exist, while full NPC-to-NPC dialogue, bounded dialogue creativity, persistent named-NPC memory/relationships and broader environmental micro-life remain future work.

## Project Governor / quality control

The project now has a deterministic internal control layer in addition to memory:

- `Data/ProjectGovernor.json` — the single authoritative source for requirements, priorities, conflicts, decisions, active gate and region quality states.
- `Scripts/project_governor.py` — CI validation of the single Governor.

This layer is specifically meant to stop silent requirement contradictions, false completion claims, inaccessible required routes, target-device performance regressions and acceptance of boring/frustrating sections without human pacing review.

It does not promise zero bugs. It enforces evidence and prevents known uncertainty from being hidden.

## Active visible-gameplay work: CP31-CP32 characters

The project has moved from governance-only preparation into visible character/gameplay production.

Current character state:
- Frodo and Gandalf have dedicated imported modular production meshes and the CP31 production-aware motion pass.
- Sam, Merry, Pippin and Bilbo use the imported Hobbit production archetype with character-specific color/proportion treatment.
- Aragorn/Strider, Boromir, Legolas, Gimli, Arwen, Elrond, Haldir, Galadriel, Saruman and other non-Hobbit named cast are runtime-present distinct procedural proxies; these are **not** final character art.
- `Data/CharacterPopulationPlan.json` is the implementation map for required cast presence by Part I chapter/route.
- Bree, Rivendell and Lothlorien now carry region-aware moving ambient populations rather than one Hobbit silhouette everywhere.

Next character-production work after compile/PIE proof is dedicated visual asset/rigging production in the order recorded by the population plan.

## Current architecture map

### Story / quest
`ShireQuestSubsystem.*`
- active quest and stages,
- current chapter,
- persistent one-time story beats,
- route / episode / playable-character state,
- per-route snapshots.

### Save
`ShireSaveGame.h`
- transform,
- quest/chapter state,
- completed story beats,
- route/episode/character,
- per-route progress.

### World routing
`ChapterWorldRouter.*`
- keeps one major generated region active at a time,
- removes previous generated prototype actors,
- builds current chapter,
- routes GandalfParallel to Isengard,
- restores route transform when appropriate.

### World builders
- `ShirePrototypeWorldBuilder.*`
- `BreePrototypeWorldBuilder.*`
- `FellowshipChapterWorldBuilder.*`
- `IsengardPrototypeWorldBuilder.*`

### Player / HUD
`ShirePlayerCharacter.*`
- movement / interaction / quick save-load,
- prototype appearance by playable character,
- temporary F8 route toggle,
- story-gated melee foundation for dangerous Part I chapters,
- persistent prototype health with a story-safe nonlethal floor until checkpoint/respawn UX is authored.

`ShireHUD.*`
- playable character / episode,
- active quest/objective,
- dialogue and alerts.

### Story presentation / dialogue / audio
- `ShireStoryPresentationSubsystem.*`
- `ShireDialogueSubsystem.*`
- `ShireAudioSubsystem.*`

The audio subsystem now resolves runtime ambience, music, SFX and voice assets by convention, keeps persistent ambience/music components, attaches world voice to matching actors, and ducks music during voiced dialogue.
Runtime voice playback now resolves `/Game/Audio/Voice/<Speaker>/<VO_ID>`, plays from the matching world actor when available, falls back to controlled 2D playback, and preserves subtitles when an asset is still missing.
`Data/VoiceCuePlan.csv` is statically synchronized with all runtime `VO_*` identifiers.
`Data/MusicCuePlan.csv` defines original music direction; final authored music and voice assets are not falsely claimed complete.

### Ambient life
`ShireAmbientNPC.*`
- walking/waiting routine,
- humanoid proxy movement,
- low-cost nearby-player awareness,
- look / cooldown / resume routine.

## Major work already present in current source

- Shire humanoid proxy pass.
- more Hobbiton paths, homes, fences, gardens, population and instanced foliage.
- optional Shire side stories.
- warm Shire morning presentation.
- deeper original Shire story dialogue.
- film-first story/canon bible.
- synchronized story/dialogue/music planning data.
- persistent multi-route story architecture.
- playable Gandalf/Isengard prototype route.
- Saruman / Orthanc / prison / industry / escape beats.
- deeper Rivendell social hub prototype.
- Fellowship camp / Boromir training / Crebain beat.
- Moria Watcher / Orc / Cave Troll / Balrog escalation.
- Lothlorien grief / Mirror material.
- Amon Hen Boromir pressure / defense / Fellowship break.
- lightweight ambient NPC awareness.
- CP21 Shire mega-pass source adds a mill/stream landmark, market detail, denser party preparation, crop rows, wooded-road cover, richer ferry geometry, more ambient residents/optional talkers and Black Rider last-known-position investigation behavior.
- CP22 Shire world-scale source pass expands Bag End-to-Ferry travel from roughly 50m to roughly 260m, separates Hobbiton/fields/wooded road/ferry with occlusion hills, introduces continuous curved roads and exploration loops, redistributes story/side-story actors to the larger geography, expands instanced ground cover and adds distance-adaptive ambient-NPC tick rates for the low-spec target.
- CP23 living-world source pass adds story-reactive atmosphere, reusable story-aware dialogue variants, persisted landmark discoveries, lightweight NPC-to-NPC social pauses near the player, running-sensitive Black Rider detection, and extra route/playable-character repair for restored saves.

## Story/data source hierarchy

Use these for their proper role. **Management authority exists only in the Governor:**

1. `Data/ProjectGovernor.json` — **sole project-management authority** for requirements, priority, conflicts, active gate, execution lane and acceptance status.
2. `Docs/CURRENT_PROJECT_STATE.md` — operational handoff/implementation summary; it follows the Governor.
3. `Docs/PROJECT_MEMORY_SYSTEM.md` — request/decision preservation rules.
4. `Docs/WORLD_PRODUCTION_BLUEPRINT.md` — world/chapter/checkpoint engineering map.
5. `Docs/LIVING_WORLD_AI_BLUEPRINT.md` — living-world/NPC intelligence design reference.
6. `Data/LivingWorldFeaturePlan.json` — machine-readable living-world implementation detail.
7. `Docs/DEVELOPMENT_GATES.md` — process/acceptance rules subordinate to the Governor.
8. `Docs/PROJECT_GUARDIAN.md` — regression memory.
9. `Docs/STORY_CANON_BIBLE.md` — film-first canon/route vision.
10. `Docs/PART1_FELLOWSHIP_MASTERPLAN.md` — Part I production plan.
11. Story/dialogue/music/biome/checkpoint data — authored detail contracts.
12. Runtime C++ — actual implementation behavior.

If a supporting document disagrees with the Governor on management state, reconcile it in the same change. Do not invent acceptance evidence.

## Canon/content rules

- Peter Jackson film continuity is the primary Part I story spine.
- Extended Edition detail may enrich the game when it does not contradict the core route.
- Tolkien lore may enrich the world but must not silently replace film continuity.
- Side content may fill believable gaps but must not change required story outcomes.
- New dialogue is original; do not copy screenplay dialogue.
- Music must be original in melody/rhythm/theme; film music is only broad emotional reference.
- Frodo is the Ring-bearer main line, but the wider story is ensemble-based.
- Parallel playable routes require a clear canonical/story reason.

## Scope rule

Part II and Part III remain roadmap/design work until the current Part I production gate is healthy.

Do not stack another large feature on a current head that has not passed the real UE4.27 compile + PIE + target-device smoke test.

Active production order:
1. validate current head,
2. stabilize the Shire as the vertical slice,
3. continue chapter-by-chapter,
4. keep the trilogy documented without destabilizing the active build.

## Exact next hard gate

The Public/Private/root-correction loop is closed machine-wise on CP-W00-154 and is not an active cleanup lane unless a concrete regression appears.

1. Validate packaged runtime Data JSON staging/read execution.
2. Validate actual authored audio-bank presence/playback without `-NoSound`; missing authored assets remain an explicit production blocker, not a fake pass.
3. Run target-device DX11 / 720p / Low-Medium profiling and record FPS, frame time, obvious hitching, GC spikes, RAM/VRAM pressure and tick hotspots where measurable.
4. Collect chapter-specific human PIE traversal, onboarding/core-loop, pacing, visual readability, collision/movement and NPC-behavior observations.

W01 and B1/B2/B3 remain frozen until the Governor records these remaining W00 acceptance evidence families.

## Failure procedure

If any gate fails:
1. stop feature expansion,
2. save/copy the exact log,
3. fix the smallest failing layer,
4. push to `develop`,
5. require green static CI,
6. rerun UE build,
7. rerun the exact failed PIE step,
8. update this handoff if project state materially changed.

Local one-click build failure log:
`Saved/Logs/LastOneClickBuildFailure.txt`

## Recovery procedure if chat context is lost

A new developer/assistant should:
1. open this file first,
2. confirm repo and `develop`,
3. inspect latest `develop` commit and both validation workflows,
4. read `Data/ProjectGovernor.json` so no recorded user request is lost,
5. read `Data/ProjectGovernor.json`, then `Docs/PROJECT_MEMORY_SYSTEM.md` and `Docs/PROJECT_GOVERNOR.md`,
7. open `Source/ShireJourney/README.md` before changing runtime code,
8. inspect `Data/SourceArchitecturePlan.json` for ownership and planned file location,
9. read `Docs/LIVING_WORLD_AI_BLUEPRINT.md` and `Data/LivingWorldFeaturePlan.json` before NPC/world-life work,
10. read `Docs/DEVELOPMENT_GATES.md` and `Docs/PROJECT_GUARDIAN.md`,
11. read `Docs/STORY_CANON_BIBLE.md` before story changes,
12. inspect the relevant StoryBeat/Dialogue/Music/Biome/Checkpoint data files,
13. never claim engine testing without a real UE4.27 result,
14. resume from "Exact next hard gate".

## Temporary developer controls

- F5 — Quick Save
- F9 — Quick Load
- F6/F7 — previous/next chapter debug navigation
- F8 — temporary Frodo/Gandalf route toggle

These are developer controls, not final player-facing menu design.


## Character / voice completeness rule

Character quality is now governed by:
- `Docs/CHARACTER_PERFORMANCE_STANDARD.md`
- `Docs/PRODUCTION_COMPLETENESS_MATRIX.md`
- `Data/VoiceCuePlan.csv`

These files are required Project Guardian inputs.
They explicitly cover facial acting, gaze, blink behavior, lip-sync, voice, body language, locomotion,
interaction animation, environmental reaction, combat reaction, crowd behavior, continuity and low-spec LOD/performance.
Current proxy characters do not satisfy final character quality; final rigs/animations/voice assets remain future production work.


