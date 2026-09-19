# Automation-first delivery — owner direction, 2026-09-19

Authority: `Data/ProjectGovernor.json`, especially REQ-QA-001 and REQ-VISION-001.
This is an implementation roadmap, not a competing project authority.

## Product contract

Deliver the three-film journey with its opening, chronology, major characters and fixed outcomes. Optional exploration belongs between film anchors. Audit the opening/prologue explicitly rather than assuming starting in the Shire covers the film opening. Use original game dialogue. Keep gameplay and any future language/speech model offline. Every character participates at an affordable intelligence tier.

The owner wants to play for enjoyment, not act as the routine technical test operator. Developers own reproducible defect discovery, regression scenarios and evidence. Human feedback on atmosphere and pacing still matters; automated boot success must never be represented as cinematic acceptance.

## Implemented in this change

- Startup and all eight Part I chapter boots require a live four-second observation after all required markers, within a total 45-second deadline per boot.
- Fatal/assert/ensure detection continues throughout observation and includes the final log after shutdown.
- A spontaneous process exit is failure even if ready markers were printed and the exit code is zero.
- Stale logs are removed, chapter marker prefixes cannot impersonate another chapter, and the harness reaps its launched process on completion/failure.
- JSON results and failure log tails describe the actual proof boundary. There is no automatic retry to turn intermittent startup failure into a pass.
- Eleven subprocess/parser regression scenarios run in Pre-Unreal CI. They test the observer, not the Unreal game.

Windows engine execution is required before calling the new observer engine-validated. Python 3.11 is provisioned in the existing Unreal workflow. This development dependency does not add an online dependency to the shipped game.

## Next executable batches, in order

1. **Story and persistence:** engine-driven scenarios traverse mandatory quest edges using production APIs; compare story/route/transform/NPC memories across save-load and Frodo/Gandalf return; isolate test saves from owner slots; verify optional exploration cannot skip anchors. Do not award traversal coverage to forced chapter boot alone.
2. **Intelligent inhabitants:** test alternate wording of supported requests, ignorance outside knowledge limits, prevention of future-story spoilers, relationship memory after reload, and changing peace/fear/grief context. Implement understanding-to-action before claiming free conversation. A small local model remains an experiment subject to measured latency/RAM; deterministic fallback stays mandatory.
3. **Exploration and companions:** route samples, stuck detection, companion following/recovery and interactions with obstructed targets. Capture failures with deterministic seeds and locations so the owner need not reconstruct them.
4. **Film presentation:** authored playable treatment of each anchor, camera continuity, spatial ambience, original sound/music, coherent character motion and region identity. Generate rendered captures for review. Boot markers cannot prove these qualities.
5. **Device and packaging:** automated rendered traversal with frame-time/RAM observations on the target Windows device; packaged-build startup and save round-trip. Separate null-renderer evidence from GPU performance evidence.

## Trilogy rollout

| Part | Scope | Current proof boundary |
|---|---|---|
| Fellowship | Opening coverage audit, Shire through Amon Hen, companion and side-exploration depth | Existing eight-chapter runtime; current work remains incomplete |
| Two Towers | Design Rohan, divided-party chronology, Fangorn and the journey toward Mordor | Roadmap/design, not playable completion |
| Return of the King | Design Gondor, parallel war/ring journey and conclusion | Roadmap/design, not playable completion |

Expand production after Part I stability under existing gates. Reuse story, persistence, NPC and observation systems across parts; do not invent three independent engines.

## Delivery evidence

Each batch reports requirement IDs, actual code changes, tested commit, passing/failing checks and remaining gaps. Preserve requests in the Governor. Prefer a coherent visible capability with automated regression over accumulating unrelated checkpoint numbers. No claim of bug-free delivery or fully finished trilogy follows from this infrastructure change.
