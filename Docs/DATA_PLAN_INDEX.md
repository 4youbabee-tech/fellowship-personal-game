# DATA PLAN INDEX

Purpose: stop overlapping JSON plans from becoming competing sources of truth. Each file below owns one bounded concern. Cross-domain decisions belong in ProjectGovernor/MasterExecutionRoadmap; domain files must not silently redefine film canon, production readiness, or another file's scope.

## Authority order

1. Film/story canon and immutable outcomes.
2. `Data/ProjectGovernor.json` — project-wide decision/state authority.
3. `Data/MasterExecutionRoadmap.json` — dependency-ordered execution bundles.
4. `Data/Part1MegaProductionPlan.json` — coordinated Part I mega-production operation.
5. `Data/Production100ReadinessGate.json` — proof boundary for any 100% production claim.
6. Domain plans below — implementation contracts for one bounded concern.
7. Evidence/inventory files — measurements and records; they never override the authorities above.

## Overlap-prone domain ownership

| File | Sole scope |
|---|---|
| `BoundedDialoguePlan.json` | Bounded contextual dialogue variation/selection; no unrestricted runtime invention. |
| `NPCConversationPlan.json` | NPC-to-NPC ambient conversation eligibility, intent, cooldown and repetition rules. |
| `NPCMemoryPlan.json` | Bounded persistent NPC memory and save-growth limits. |
| `NPCSocialModel.json` | NPC identity, role, knowledge, schedule and relationship data contract. |
| `NPCRegionalMoodPlan.json` | Shared chapter/region emotional climate used by eligible NPC behavior/dialogue. |
| `LivingNPCIntelligencePlan.json` | Umbrella runtime integration for bounded NPC intelligence; it coordinates but does not replace the narrower contracts above. |
| `LivingWorldEventPlan.json` | Low-cost environmental/micro-event categories, eligibility, density and caps. |
| `WorldLifeSaturationPlan.json` | Baseline regional population density and continuous low-cost inhabited-world saturation. |
| `WorldActivityMovementPlan.json` | CP55 visible movement/fauna expansion; no story/save/route topology changes. |
| `WorldDressingPlan.json` | Deterministic decorative world-dressing placement and reusable environment dressing. |
| `ChapterAtmospherePlan.json` | Chapter-specific low-cost lighting/fog/material response; no story topology changes. |
| `CharacterPopulationPlan.json` | Named cast presence and visual-tier expectations by chapter. |
| `CharacterMotionPlan.json` | Character locomotion/acting motion plus skeletal-rig handoff and motion performance rules. |
| `ExplorationEnvelopePlan.json` | Safe free-roam windows between fixed film-story anchors. |
| `ContextualSideActivityPlan.json` | Optional game-like activities allowed inside those safe canon windows. |
| `JourneyDiscoveryRewardPlan.json` | Exploration discovery persistence/reward state without altering mandatory film chronology. |
| `ChronicleMapKnowledgePlan.json` | Persistent Chronicle/map knowledge presentation and browsing. |
| `FilmExperiencePlan.json` | High-level film anchor coverage and intended player treatment; not acceptance evidence. |
| `FellowshipExperienceMegaPassCP56.json` | CP56 experiential enrichment over the fixed Part I film spine. |
| `ChapterAtmospherePlan.json` | Visual atmosphere identity only; it does not own cinematics, story or performance acceptance. |

## Production coordination files

- `Part1ProductionAtlas.json`: source-grounded geography, landmark chains and production targets.
- `Part1VisualProductionPass.json`: current source-grounded chapter/encounter visual-production wave; it cannot promote visual acceptance without evidence.
- `CharacterProductionMatrix.json`: character production coverage/readiness, not runtime behavior authority.
- `CinematicWorldProductionMatrix.json`: region/world art-production coverage/readiness, not story authority.
- `GameCompletenessMatrix.json`: whole-game completeness tracking across pillars.
- `ProductionExecutionGraph.json`: dependency graph for execution order.
- `CP56MegaIntegrationPlan.json`: CP56 integration/validation coordination only.
- `FilmSideContentMasterPlan.json`: audited side-content catalog/placement policy under film canon.
- `EnsembleFilmMissionPlan.json`: playable-viewpoint assignment where film action belongs to ensemble characters.

## Evidence, gates and inventories

`AssetPerformanceBudget.json` owns the measurement-first performance-budget policy. It may report source/cooked/device metrics but may not invent hard limits before reproducible target-device evidence.

The following record facts or enforce gates and must not become alternate design authorities: `PIEVerificationEvidence.json`, `AssetPerformanceBudget.json`, `VerificationGate.json`, `ProjectGuardRules.json`, `ProjectOwnedProductionAssetInventory.json`, `ExternalAssetManifest.json`, `OwnerSourceReferenceIndex.json`, `FilmDialogueSourceContext.json`, `ResourceIntegrationPlan.json`, `RightsHolderContactPlan.json`, and `WorldResourceBankCP54.json`.

## Anti-duplication rule

Before adding a new JSON plan, first identify the owning row in this index. Extend the existing owner whenever possible. If a genuinely new concern requires a new file, add it here in the same change and state which existing files it may read but may not override.
