# Deep Project Audit

This is a continuous engineering and player-experience audit, not a completion claim.

## Current conclusions

The project Governor is structurally coherent, the film-first invariant remains intact, and the backend now has real compile/import/startup/eight-chapter/save-state evidence. The audit also found several player-experience and scaling risks that were not acceptable to leave implicit.

Immediate repairs applied in this wave:
- F6/F7/F8 developer route/chapter controls are non-shipping only.
- Lightweight cinematic presentation can no longer hard-lock movement for 10-27 seconds; the current lock is capped at 3.5 seconds while dialogue/audio may continue.
- Story checkpoints now write asynchronously and serialize overlapping requests instead of synchronously hitting disk during active play.

Tracked scaling risks:
- Ambient social pairing and companion banter still use periodic actor iteration. It is distance/cooldown bounded, but must be profiled on the target laptop before population grows further.
- Chapter world builders use many direct LoadObject calls. They are construction-time rather than per-frame, but may become transition hitches as production art grows.
- Repeated environment geometry should continue moving toward instancing/culling where interaction is not required.
- Tangent/binormal debt remains real even after duplicate-log inflation was removed.

## External practice alignment

Epic's UE4.27 save guidance recommends asynchronous saving during active gameplay to avoid hitches. Epic's asset-loading guidance recommends soft references/asynchronous loading when hard loads would otherwise create stalls or memory pressure. Unreal performance guidance emphasizes profiling the actual target device instead of inventing budgets, and instancing guidance supports grouping repeated meshes rather than multiplying actor cost.

## Audit rule

A critical red exact-head gate blocks unrelated expansion. Audit and repair work may continue while red. Once the exact head is green, large visible production waves resume behind the same evidence chain. Rendered PIE, target-device performance and human visual/pacing acceptance remain separate gates.
