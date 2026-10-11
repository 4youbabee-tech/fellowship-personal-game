# Cloud-First Fast Production Protocol

Date: 2026-10-11

This protocol applies while the owner laptop and `UE4-27-Windows` self-hosted runner are resting. Production should continue in the cloud wherever possible, without pretending that cloud/source evidence equals runtime acceptance.

## Active Rule

Use GitHub and cloud-hosted checks for source-only preparation, manifests, conversion scripts, receipt reuse, candidate ranking, and documentation. Do not queue self-hosted Windows Unreal jobs unless the work truly requires Unreal import/build/package/runtime evidence and the owner has made the runner available.

## Immediate P1C01 Queue

1. Reuse existing verified warehouse receipts for unchanged Poly Haven and ambientCG sources.
2. Prepare derived FBX/PNG/TGA/ORM outputs only from copies, preserving original warehouse payloads and SHA256 receipts.
3. Keep Bag End, Hobbiton, Bagshot Row, Party Field, roads, water, gardens, and hero-character source readiness as the first queue.
4. Stage 28-region material and identity manifests in parallel, but do not activate later chapter runtime before P1C01 Gate 6/7.
5. Use `Scripts/offline_production_classifier.py` before opening PRs or dispatching workflows while the self-hosted runner is offline.

## PR Rule

PRs are allowed when the changed paths select only cloud-hosted/static workflows. If changed paths include runtime source, Unreal config, Content, workflow files, packaging files, or project files that route to self-hosted UE4 jobs, keep the branch ready and wait for intentional runner availability.

## Evidence Boundary

This protocol does not prove PIE, visual acceptance, packaged Windows startup, device FPS, runtime imports, or Gate 6/7. Those claims require actual runner/device evidence.
