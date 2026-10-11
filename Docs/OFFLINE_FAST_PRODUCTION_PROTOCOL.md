# Offline Fast Production Protocol

Date: 2026-10-11

This protocol applies while the owner laptop and `UE4-27-Windows` runner are unavailable. It keeps Shire Journey production moving without claiming runtime evidence that cannot be produced offline.

## Active Rule

Work may continue on source-only preparation, manifests, conversion scripts, receipt reuse, candidate ranking, and documentation. Do not dispatch, open, or update work in a way that queues self-hosted Windows Unreal jobs unless the owner explicitly makes the runner available.

## Immediate P1C01 Queue

1. Reuse the existing verified warehouse receipts for unchanged Poly Haven and ambientCG sources.
2. Prepare derived FBX/PNG/TGA/ORM outputs only from copies, preserving original warehouse payloads and SHA256 receipts.
3. Keep Bag End, Hobbiton, Bagshot Row, Party Field, roads, water, gardens, and hero-character source readiness as the first queue.
4. Stage 28-region material and identity manifests in parallel, but do not activate later chapter runtime before P1C01 Gate 6/7.
5. Use `Scripts/offline_production_classifier.py` before opening PRs or dispatching workflows while the runner is offline.

## PR Rule

If changed paths include runtime source, Unreal config, Content, workflow files, or project files, treat the PR as runner-gated. Source-only branches may be created and tested locally or with hosted-only checks, but PR creation must wait until workflow filters are confirmed safe or the runner is intentionally back online.

## Evidence Boundary

This protocol does not prove PIE, visual acceptance, packaged Windows startup, device FPS, runtime imports, or Gate 6/7. Those claims require actual runner/device evidence.
