# Branch Consolidation Audit — 2026-09-25

Status: ACTIVE CLEANUP / CANONICAL LANE = `develop`

## Purpose
Reduce repository ambiguity before programmer handoff. `develop` remains the sole interactive/integration source. `main` remains the stable/release lane. Historical branches are not to be merged wholesale into `develop`.

## Completed in this pass
- Closed stale open PRs #62 (`production/early-realms-world-life-v1`), #63 (`repair/world-transition-coordination-v1`) and #66 (`perf/visual-performance-guardrails-v1`) as superseded by newer develop systems/contracts.
- Hardened `SHIRE_UPDATE_BUILD_LAUNCH.bat` and `SHIRE_PIE_VERIFY.bat` by running from immutable temporary copies, preventing `git pull` from rewriting the batch file CMD is currently parsing.
- Salvaged unique safe planning/warehouse data into the consolidation branch:
  - `Data/LivingWorldSensoryCompletenessPlanV1.json`
  - `Data/VoiceProductionMasterPlanV1.json`
  - `Data/GeneratedAudioWarehouseV1.json`
  - `Data/P1C01AmbientSpeechAndBarksV1.json`
  - `Data/P1C01CompleteAudioBankV1.json`
  - `Data/P1C01NamedCharacterEffortsV1.json`
  - `Data/WarehouseGapAuditSource09V1.json`
- Expiring signed delivery URLs were removed from consolidated generated-audio registries. Cue/task identity and truth boundaries remain; temporary delivery URLs are not durable project state.

## Branch disposition

### KEEP
- `develop` — canonical development/integration lane.
- `main` — stable/release lane.
- `maintenance/repository-consolidation-v1` — temporary cleanup branch for PR #71 only.

### SAFE DELETE CANDIDATES — merged/fully behind or directly superseded
These branches have no reason to remain active after PR #71 is merged and the final audit is recorded:
- `acceptance/w00-final-closure-v1`
- `ci/w00-acceptance-fast-path-v1` — superseded by newer classifier/workflow on develop.
- `cp55/activity-movement-expansion-v1`
- `cp56/fellowship-experience-megapass-v1`
- `fix/startup-grounding-regression-v1`
- `governance/programmer-asset-pipeline-review-v2`
- `governance/programmer-findings-v1` — later reconciliation exists on develop.
- `integration/comprehensive-foundation-v1`
- `perf/visual-performance-guardrails-v1` — obsolete base/PR #66 closed; current performance contracts live on develop.
- `production/chapter-streaming-v5`
- `production/character-surface-parity-v1`
- `production/cinematic-audio-life-v3`
- `production/early-realms-world-life-v1` — stale pre-migration runtime paths; PR #62 closed.
- `production/hero-character-world-polish-v4`
- `production/mega-material-world-wave-v1`
- `production/realm-detail-saturation-v2`
- `qa/automated-immune-system-v1`
- `recovery/stached-charcter`
- `repair/import-pipeline-megapass-v3`
- `repair/post-merge-unreal-339`
- `repair/pr67-work-review-intake`
- `repair/verification-quality-v1`
- `repair/warning-quality-v2`
- `repair/world-transition-coordination-v1` — newer committed-world synchronization is already on develop; PR #63 closed.
- `verification/current-head-audit-v1`
- `verification/current-head-pie-handoff-v1`
- `work/automation-first-runtime-observation`
- `work/repository-hygiene-cleanup`

### PRESERVE UNTIL FINAL SALVAGE CHECK
Do not bulk-delete these until their remaining unique data is explicitly classified:
- `audit/pre-mega-integration-v1` — 67 commits ahead of its old base but hundreds behind develop; contains stale pre-Public/Private runtime paths and must not be wholesale-merged.
- `planning/living-world-completeness-v1` — key unique sensory/voice plans have now been salvaged; remaining differences are mainly stale governance/docs/roadmap snapshots and recovery tooling, pending final supersession check.
- `warehouse/generated-audio-v1` — core manifests have been salvaged in sanitized form; preserve until confirming no binary/master asset intake depends on branch-only state.
- `warehouse/source09-gapfill-v1` — gap audit has been salvaged; preserve until final candidate-registry equivalence check.

## Merge policy
- Never bulk-merge an old diverged branch merely because it is ahead by commit count.
- Salvage only still-valid unique content.
- Current `Public/Private` runtime layout and current `develop` systems win over stale pre-migration branch paths.
- W00 closure truth remains unchanged: automated proof is green, but human PIE grounding/traversal/warning-tail evidence is still required before claiming final closure.
