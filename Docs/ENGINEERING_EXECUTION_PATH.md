# Engineering Execution Path

This is the practical engineering route for finishing the project. It does not replace `Data/ProjectGovernor.json`; the Governor remains the single requirement/decision authority. This document and `Data/ProductionExecutionGraph.json` organize implementation order, dependencies and proof.

## Current engineering baseline

The current production line contains:
- CP44 backend completion/hardening,
- CP45 full named-cast modular identity expansion,
- CP46 major threat production meshes,
- CP47 licensed external asset pipeline,
- CP48 Weta/rights-holder/global resource map,
- CP49 living-world micro-event director plus reusable production terrain/mountain kit.

Backend code is treated as **implementation-complete pending integration acceptance**, not as an excuse to stop production. World, character, audio and presentation work continue in large batches while every batch preserves the same quest/save/story contracts.

## Runtime intelligence architecture

The intelligence stack is deliberately bounded for UE4.27.2 and the low-spec target:

1. **Quest/route state** is authoritative for chapter, quest stage, route and story beats.
2. **NPCContextSubsystem** resolves canonical identity, aliases, knowledge, schedule, danger/weather context and bounded dialogue.
3. **QuestSubsystem NPC memory** stores compact named-NPC memories, relationships and repetition history.
4. **ShireNPC** consumes those systems for named interactions and two-way Fellowship banter.
5. **ShireAmbientNPC** provides cheap local routines, awareness, contextual social conversation, props and schedule/weather/danger response.
6. **LivingWorldDirector** reads `Data/LivingWorldEventPlan.json` and injects capped disposable micro-events around the player without persisting transforms or blocking story.
7. Distant simulation stays cheap; no always-on remote LLM is required.

This gives the requested "AI touch": characters remember selected events, react to context, converse inside knowledge/canon limits and participate in a living world, while deterministic fallbacks keep the game reliable offline.

## World-production architecture

World production is layered instead of rewriting quest coordinates:
- story/quest topology stays authoritative,
- production architecture overlays the working gameplay blockout,
- common terrain silhouettes add hills, cliffs, river banks and boulders,
- chapter-specific kits provide recognizable landmarks,
- licensed external assets can later replace or enrich generic pieces through the manifest gate,
- final terrain materials/vegetation/weather/interiors are separate production layers.

## Definition of finished

"Finished" is not one flag. A workstream becomes:
- **IMPLEMENTED_PENDING_VALIDATION** when source/runtime integration exists and compile/import is green;
- **PIE_TESTED** after actual gameplay is exercised;
- **DEVICE_TESTED** after the target laptop proves performance/stability;
- **VISUALLY_ACCEPTED** only after human visual/pacing review.

The project does not hide remaining acceptance work by calling compile success "finished".

## Handoff rule

A new developer/assistant resumes in this order:
1. `Data/ProjectGovernor.json`
2. `Data/ProductionExecutionGraph.json`
3. `Docs/CURRENT_PROJECT_STATE.md`
4. `Docs/ENGINEERING_EXECUTION_PATH.md`
5. `Data/SourceArchitecturePlan.json`
6. relevant world/NPC/story plans
7. latest develop HEAD and both validation workflows

No chat transcript is required to recover the engineering path.
