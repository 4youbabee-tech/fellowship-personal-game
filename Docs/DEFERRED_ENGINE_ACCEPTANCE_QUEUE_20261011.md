# Shire Journey — Deferred Engine Acceptance Queue (2026-10-11)

This is a **deferred validation queue**, not proof of defect resolution. No Windows self-hosted runner is authorized. Do not change P1C01 Gate 6/7 status until exact-head evidence and human review exist.

| Priority | Offline disposition | Required when owner authorizes UE runner | Passing evidence |
|---|---|---|---|
| P0 Save/restore/checkpoint | PR #391 merged; pending-restore input guard candidate | Compile UE4.27.2, QuickSave/QuickLoad, checkpoint queue/rejected dispatch and restored position under interruptions | Exact build SHA, state runtime logs showing save/restore and restored transform; no lost checkpoint |
| P0 World movement | PR #392 unsafe ground teleport fix merged | PIE walk at Bag End interior/exterior, round doors, bridges, hills, farms and Bucklebury Ferry, forced failed ground probe, rollback | Routes and collision probes with screenshots + zero player stuck/fall-through incidents |
| P0 Cinematic control | PR #391 merged source | PIE start/interrupt/skip/replay cinematic, player respawn, pause/return control | Log event order, restored input, quest outcome unchanged |
| P0 Audio race | PR #391 token owner fix merged | UE play ambience/music/SFX/voice, cancel-requeue same cue, spatial attenuation, Arabic cue variants | Audio playback + no stale callback/wrong line |
| P0 Character/animation | FBX sources staged; no Engine import acceptance | Import/retarget Frodo/Gandalf/Bilbo/Sam/Merry/Pippin rigs, idle/walk/run and interactions | Skeleton and motion deformation visual capture, no warnings |
| P0 Source materials | Drive holds original 36 FBX / 27 PNG intake; 36 CC0 PBR triplets, one source quarantined | Import real FBX/PNG, build/assign UE materials, verify NormalDX orientation, packed ORM, UV, LOD and collision | Asset Registry counts, UE import logs and side-by-side visual capture |
| P1 NPC life and routes | Existing object pool/context systems retained | PIE NPC daily schedule, interactions, environmental collision/nav on each Shire route | No deadlock, blocked nav, pool leak or quest blocker |
| P1 Free exploration and canon | Film spine/Tolkien/source bibles remain authoritative; side activity gates source-defined | Play optional discoveries before/after story anchors, save-return replays, verify no canon outcome changes | State log and walkthrough matrix for 17 P1C01 disposition requirements |
| P1 720p/30 FPS | LOD and 2GB VRAM design budgets only | Profile Shire representative routes at 1280x720 DX11 on i7 6th gen/8GB/~2GB VRAM | Real FPS/frame-time/VRAM CSV, streaming hitch report |
| P1 Human visual/audio acceptance | Source files and technical checks only | Human review of atmosphere, camera, lighting, subtitles, animations, audio mix, narrative continuity | Chapter-specific signed review and repro shots |

**Release rule:** No claims of COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED or P1C01 Gate 6/7 closure until relevant matching evidence exists. All tests are *deferred*, not silently passed.

**At runner startup:** Obtain explicit owner approval; validate runner hardware/engine; build current develop exact SHA; run headless startup/route, state/save, import tests and PIE; profile device and perform human visual checks. Resolve any failures in PRs with synchronous status docs. Never run P1C02 runtime before P1C01 Gate 6/7 acceptance.

## Added Offline Fix Candidate — Stale Asset-Ready Rollback

Source-only audit identified that a stale `OnChapterAssetsReady` callback could previously return after quest/save state changed without clearing the pending world transaction. The fix adds stale-ready rollback plus shared cleanup for pending route/episode/chapter and grounding-barrier timers. Required runner validation when authorized: force overlapping chapter/route/episode changes while async asset preload is pending, then verify no player hold deadlock, no stale world commit, and no delayed grounding timer mutates the restored world.

## Added Offline Fix Candidate — LivingWorld Initial Commit Sync

Source-only audit identified that the living-world director could skip first-run chapter reset if the first committed `AChapterWorldRouter` revision was `0`, because `AppliedWorldRevision` also started at `0`. The source fix uses an unapplied sentinel and applies `ActiveChapterId` only after router commit confirmation. Required runner validation when authorized: start P1C01 from a clean save and from a restored save, verify `LivingWorldCommitSync` logs on first visible world, confirm baseline Hobbiton/Bag End population, weather context and micro-event timing initialize once, and verify no duplicate NPCs after route/episode transitions.

## Added Offline Fix Candidate — NPC Committed Context Revision Guard

Source-only audit identified that `UShireNPCContextSubsystem::SetCommittedWorldContext` rejected `WorldRevision == 0`. The fix treats revision as an ordering token, not a validity flag, and validates the actual world identity fields instead. Required runner validation when authorized: force initial and rollback world commits, confirm NPC dialogue/schedule context reports committed immediately, and verify no conversation uses destination quest state before router commit.\n\n## Added Offline Fix Candidate — NPC Context Teardown Reset\n\nSource-only audit identified that NPC committed world context could remain populated through subsystem teardown. The fix clears committed world identity, quest snapshot, revision and weather during `Deinitialize()`. Required runner validation when authorized: restart PIE/session after setting a non-default route/weather context, confirm NPC context starts uncommitted/clear until the router publishes a fresh committed world, and verify no stale dialogue mood leaks into P1C01.\n\n