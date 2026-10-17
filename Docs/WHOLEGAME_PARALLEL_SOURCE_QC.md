# Parallel whole-game SOURCE_QC lane - October 17, 2026

Source-only, no active second Unreal writer. PES-002 / P1C01 remains the sole runtime chapter under Data/ProjectGovernor.json. Earlier cloud-wholegame-140-source workflow was disabled; this change restores precisely ONE GitHub-hosted Ubuntu source-only production job and does not activate the old disabled F104-F204 writer stubs.

This job reuses pinned GitHub artifact 11767251532 from Run 38292163970, exact source commit 1e1e5c9df5aeee75e130eed7891fdfb7b129c9fc. Scripts/stage_cloud_wholegame_source.py validates the entire physical archive and individual SHA256s; Tools/CloudAssetBuild/package_wholegame_regions.py constructs ten chapter/F3 support-source ZIP archives plus one full 28-region pack, each with actual LOD0/LOD1 FBX, PBR PNG, SHA256 receipts and machine-readable index.

Boundary: 28 region support meshes, each LOD0+LOD1 (56 FBX), 12 PBR families (36 PNG). These are project-original low-polygon SUPPORT ONLY (Minas Tirith LOD0=24 polygons) and ARE NOT real playable cities, hero-grade castles, real rigged Orcs, kings, Balrogs, 22 playable Skeletal villagers, .uasset imports, placement, PIE, device or visual acceptance. Other 82 Shire FBX from the same source bundle are not counted as other-region import.

The workflow writes only to its ephemeral RUNNER_TEMP. It does NOT modify the canonical Windows Warehouse, launch Unreal, touch any WorldBuilder or Stage/CI for later runtime, or consume the single persistent Warehouse Writer. Canonical warehouse adoption later requires an independent SHA256 receipt and one writer, then UE4.27 import and Gate 6/7 for later runtime.

External Quaternius/Mixamo/Fab/Poly Haven items require per-item legal source bytes, per-item rights checks, geometry/skin/animation QC and authoring. Filenames, plans or offline source packs must not be reported as runtime or visual readiness.
