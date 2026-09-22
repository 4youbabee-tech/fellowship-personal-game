# Deep Organization and Cross-System Audit - 2026-09-22

## Scope and evidence boundary

This audit was requested before returning to the laptop runner. Runtime/source review is grounded in PR #67 exact head `17689b194ddca281aa9881b9ac50594712a65df6`; later commits in this audit are governance/document reconciliation only until fresh CI runs complete.

Current hard evidence entering the audit:

- Warehouse Stage #99: SUCCESS.
- Warehouse inventory: `payloadFiles=240 bytes=3816657674 receipts=8 receiptRecords=278 duplicateGroups=22`.
- Persistent warehouse footprint: `files=249 bytes=3816866382`.
- Pre-Unreal #685: FAILURE from PG-078 because newly accepted `REQ-CAMERA-001` was not yet mapped into `MasterExecutionRoadmap` and the unfinished snapshot was stale.
- Unreal Build #520: FAILURE before C++ compilation. Runner identity `NT AUTHORITY\NETWORK SERVICE` cannot read `Engine/Content/EngineMaterials/WorldGridMaterial.uasset`; guarded ACL remediation deferred because the service is not elevated.

No current-head COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim follows from this audit.

## Manager / Governor review

### What is working

1. **Request capture is durable.** The third-person camera requirement entered `ProjectGovernor` instead of remaining chat-only.
2. **PG-078 caught coordination drift.** The validator correctly rejected a requirement that existed in the Governor but was missing from the execution roadmap.
3. **Evidence levels remain separated.** Warehouse staging, compile/runtime evidence and human visual/device acceptance are not silently promoted into each other.
4. **The current finish path is explicit.** `CompletionWaveMapV1` gives W00-W11 and keeps P1C01 Shire as the first visible benchmark.

### What was weak and is now hardened

1. Camera capture and roadmap mapping were not atomic. `REQ-CAMERA-001` is now mapped into B1 and the tracked unfinished snapshot is regenerated.
2. `active_gate` still described the older V5 / PR #60 state. It is updated to W00 and now blocks broad feature expansion while allowing only source-safe audit/governance/blocker preparation.
3. The final pre-runner warehouse status still said “waiting for receipt” after Warehouse #99 had succeeded. It is updated to staged-and-audited.
4. `REQ-NPC-004` said `IMPLEMENTED` while its note still said “Not implemented yet.” The note now states the real boundary: source implementation exists; PIE/device acceptance is pending.
5. `REQ-ORG-001` still claimed 43 mapped runtime files while `SourceArchitecturePlan` now contains 63 mapped runtime source/build entries (62 flat .h/.cpp + one stable-root build entry). The requirement is updated.
6. A new atomic mapping rule now requires every accepted unfinished requirement to enter the roadmap in the same logical change. PG-078 remains the backstop.

### Priority-load observation

The Governor currently carries 59 requirements, 46 marked CRITICAL, and 20 ACTIVE work items. That is too many labels to use as a literal concurrency plan. No owner priority was downgraded. Instead, execution order is explicitly controlled by `active_gate`, `current_focus` and `CompletionWaveMapV1`. Current execution focus is W00 only; the rest is accepted backlog, not simultaneous execution.

## Cross-system mental simulation

### Transition path

1. Player is walking in the current committed chapter.
2. Quest/story state advances to a new chapter/route.
3. `ChapterWorldRouter` holds player movement and asks `UShireChapterAssetStreamingSubsystem` to preload the destination bank asynchronously.
4. Old geometry remains visible while the pending bank loads.
5. Destination world is built and grounded.
6. Pending asset bank is committed.
7. Router updates committed chapter/route/episode, increments `WorldRevision`, captures rollback state and broadcasts `OnWorldCommitted`.
8. `LivingWorldDirector` sees the committed revision and only then resets regional population/weather/life.

This is the correct high-level two-phase architecture.

### Finding A - NPC context can still get ahead of the visible world

`LivingWorldDirector` is commit-synchronized, but `UShireNPCContextSubsystem` separately reads `UShireQuestSubsystem` current chapter/route/quest for:

- regional mood and pressure,
- profile availability,
- film-dialogue context,
- danger state,
- bounded dialogue context/seed.

Because logical quest state can advance before destination geometry commits, an NPC still visible in the old world can transiently speak/react using destination mood or film context.

**Severity:** HIGH.

**Required repair:** give NPC world-context queries one committed-world identity/revision snapshot. QuestSubsystem remains the authority for memories, story beats and relationship state; regional/world-context eligibility must follow the committed world.

### Finding B - skeletal rig residency can grow across the journey

Character rigs are correctly requested through `FStreamableManager::RequestAsyncLoad`, and player/named-NPC modular fallback remains intact while a rig is unavailable. However, `CharacterRigRequests` retains a `FStreamableHandle` for every requested character until GameInstance shutdown.

For a full Fellowship/trilogy cast on the ~2 GB VRAM target, that can become avoidable resident-memory pressure.

**Severity:** HIGH scaling risk.

**Required repair:** after runner recovery, measure multi-chapter skeletal/animation residency. Keep the active player/current companions pinned; release inactive previous-chapter rig handles only after a safe committed-world transition and only if measurement shows value.

### Finding C - synchronous production asset debt still exists

Current exact-head source contains direct `LoadObject` calls in production paths:

- FellowshipChapterWorldBuilder: 77
- ShirePrototypeWorldBuilder: 55
- BreePrototypeWorldBuilder: 22
- IsengardPrototypeWorldBuilder: 10
- ShireNPC: 3
- ShirePlayerCharacter: 3

The async bank architecture reduces transition risk, and several loads may resolve already-resident objects, but they are still synchronous runtime lookups and become riskier as art grows.

**Severity:** HIGH scaling debt.

**Required repair:** after W00, burn these down incrementally into resident soft-object resolution / async ownership. Do not introduce another loader or remove compatibility fallback blindly.

### Finding D - ambient pooling is already implemented

The previous audit text was stale. Ambient NPC reuse now:

- clears social/awareness state,
- disables tick,
- hides the actor,
- disables collision,
- restores routine/visual state on reuse,
- keeps pooled actors out of social pairing.

This is structurally aligned with the project rule. Target-device Spawn/Destroy/GC measurement is still needed before claiming a performance win or increasing density.

### Finding E - social scans remain measurable debt, not a blocker

Ambient social pairing still uses bounded `TActorIterator` scans, and companion banter scans named NPC candidates. Tick rates are distance-throttled and pooled actors stop ticking.

Do not rewrite this pre-emptively. Profile on the target laptop first; centralize candidate registries only if the game-thread cost becomes material.

### Finding F - source organization is still intentionally flat

The authoritative target remains `Public/<Domain>` for headers and `Private/<Domain>` for implementation. The current source tree is still flat but guarded.

The physical migration must be a dedicated maintenance batch after the runner is healthy, with no gameplay changes mixed into it, because a real UE4.27 build is required to accept the move.

## Systems that currently line up well at source level

- Chapter async preload -> world build -> grounding -> bank commit -> world revision.
- LivingWorldDirector waits for committed world before changing population/weather.
- Rollback snapshot covers quest/world identity, player transform, NPC memory, exploration/progression/knowledge and player health/stamina/resolve/supplies.
- Automatic active-play checkpoint writing uses asynchronous save; synchronous save remains in deterministic test/roundtrip paths.
- Third-person camera foundation already matches the new embodied-camera direction.
- Ambient NPC pooling disables pooled tick and resets social state.
- Heavy character rigs use soft paths + FStreamableManager and retain modular fallback.

These are source-level architectural observations, not runtime acceptance.

## Current execution order

1. **Finish governance/static reconciliation** and get a fresh exact-head Pre-Unreal result.
2. **W00 runner ACL repair** on the laptop with elevation.
3. Verify UE4.27 Engine Content is readable under the runner identity.
4. Run exact-head C++ compile + production import.
5. Run Automation/startup/P1C01-P1C08/state/transition evidence.
6. Repair any real engine/runtime regression found by those gates.
7. Move to **W01**: first visible skeletal humanoid + hostile rig path in Shire.
8. Then repair the committed-world NPC-context mismatch and measured rig-residency / LoadObject debt in bounded engine-tested batches.
9. Public/Private physical migration remains a separate maintenance pass once engine validation is reliable.

## Stop conditions

Until W00 is healthy:

- no broad new warehouse saturation,
- no Part II/III runtime opening,
- no visual/device acceptance claims,
- no density increase merely because pooling exists,
- no mass source-layout migration without engine proof.
