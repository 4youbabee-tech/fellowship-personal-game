# CURRENT STATE SHORT — Shire Journey
_Last verified: 2026-10-15; source of truth: Data/ProjectGovernor.json; this file is a read-only M0 orientation index, not a second manager._

## Governing state (source: Governor on develop; verify live HEAD at each M0)
- Project: Shire Journey, UE 4.27.2 C++, Windows/DX11, 720p, i7 6th gen / 8 GB RAM / ~2 GB VRAM / target >=30 FPS.
- Canonical integration: `develop` at `03df3c34a7a5faa47a69bf882edc0a7afd01000e` as checked 2026-10-15.
- Active runtime: **PES-002 Bag End Exterior, OPEN**; PES-001 bounded import/placement complete, NOT visually accepted; PES-003+ runtime locked by Gate 6/7.
- Active candidate: [PR #477](https://github.com/4youbabee-tech/fellowship-personal-game/pull/477), `fix/pes002-bag-end-lighting-20261014`, verified pre-repair HEAD `8058f6a7025145e1e6bb98bb624e235d330e1d9b`.
- One Unreal Writer, one Warehouse Writer, one active runtime PES, one coherent PES PR; do not auto-merge or cancel a running writer.

## Proven evidence (specific HEAD, never extrapolate to successor)
- `d5f37b5e61722c4828170a729c5ae0f37aab1f58`: Pre-Unreal 38727751411 PASS; Windows Unreal 38727751427 PASS for build/import/automation/startup/four 720p captures; artifact 11969310933. All four inspected by assistant: visually rejected, not owner acceptance.
- Latest c92e940: Frodo locomotion 38755223105 PASS; Wave2 38755222797 source + UE skeletal import PASS, hierarchy deformation FAIL. Unreal 38755222958 compile/import/startup PASS, capture FAIL; stale proof log race repair in current candidate. No accepted skin/deformation.
- Historical 90 restored UE assets and 48 placed Cloud138 instances are PES-001 evidence only.

## 2026-10-15 M0/M4 source-art patch currently pending GitHub exact-head validation
- On baseline 8058f6a: Pre-Unreal 38765636036 PASS, Unreal 38765635848 PASS with real four views (artifact 11989868346), VISUAL REJECTED for roof side shell and stepped facade seam. Character Wave2 38765635822 FAIL static rig hierarchy after UE technical PASS.
- New bounded source patch: joined roof/wall 33 shared crown vertices, 32 edges, buried turf side aprons, deterministic 2,780 triangles, 7 material finishes. Three local source tests PASS; new CI check prepared. No UE screenshot or target-device evidence for the changed mesh yet, NOT RUN.
- Mesh repair retains quest, player collision, streaming, NPC/Save authority, and one active runtime writer; rollback as one cohesive batch on verified import/render regression.

## Immediate critical blockers
1. Bag End authored mesh was suppressed; current candidate restores it with joined roof, recessed entrance and seven material finishes. Local source checks PASS; new exact-head engine evidence pending. See latest CURRENT_PROJECT_STATE entry.
2. Frodo hierarchy deformation fails after source and UE import; inspect bone chains before repair. No rig promotion.
3. Saved/reopened geographic .umap, playable route/collision/NavMesh and target-device DX11 720p >=30 FPS/VRAM not proven.
4. Owner visual/traversal acceptance missing. PES-002 OPEN; no PES-003 runtime.

## Owner-approved acceleration decisions — status distinctions
- M0 reads this short index **plus live Governor/HEAD/Gates and targeted source excerpts**; historical ledgers are referenced by keyword, never discarded.
- Keep the existing large docs; archive/index old entries without deleting history or silently bypassing Governor.
- Change source decoration placement to one validated data loader + schema/asset-residency check, preserving existing asynchronous bank (NOT IMPLEMENTED).
- Exactly one runtime PES, one existing PR #477 with cohesive commits, one writer per resource.
- Four fixed-angle real UE screenshots with center-frame weighted RGB luminance floor 35/255: SOURCE CANDIDATE; UE4 exact-HEAD visual proof PENDING, manual review required.
- Character sources: Paragon, Mixamo, Poly Haven, Fab/Quixel, Quaternius, KayKit, 100 Avatars, Sketchfab **subject to per-asset rights/compatibility**. Public repo stores metadata only where source redistributions are not granted; private warehouse required.
- Frodo, Sam, Merry, Pippin, Gandalf: five distinct licensed rigged sources with Idle/Walk and 8GB/2GB LOD+device evidence REQUIRED. **Actual import NOT RUN**.
- No extracted/leaked film or game assets; no approval inferred from personal/noncommercial use alone.
- Windows cloud/second builder: compare after measured current bottleneck and explicit owner cost authorization.

## M0 fast route
- Unverified screenshots, source rigs, asset imports or CI signals never count as accepted production evidence; verify per-artifact SHA and stage.
1. Read actual HEAD, active PR, live Actions, `Data/ProjectGovernor.json` relevant keys: `pes_session_transition_2026_10_14`, `pes_professional_preproduction_gate_2026_10_14`, `pes_single_cohesive_batch_policy_2026_10_14`, active gate and newest owner additions.
2. Read `Docs/DEVELOPMENT_GATES.md`, PES-002 scope; search `Docs/CURRENT_PROJECT_STATE.md`, `Docs/PRODUCTION_COMPLETENESS_MATRIX.md`, `Docs/WORLD_DETAIL_LEDGER.md` and `Docs/PROJECT_GUARDIAN.md` for affected defect/asset/SHA, not full linear re-reading.
3. Inspect genuine Unreal screenshots, licensing, dependencies, writer locks; choose one coherent candidate; cheapest static tests then exact-head Unreal and evidence.
4. If branch/CI differs from this snapshot, correct this short index in the same planned batch. Never trust this as latest runtime acceptance.
