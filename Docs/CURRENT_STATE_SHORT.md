# CURRENT STATE SHORT — Shire Journey
_Last verified: 2026-10-15; source of truth: Data/ProjectGovernor.json; this file is a read-only M0 orientation index, not a second manager._

## Governing state (source: Governor on develop; verify live HEAD at each M0)
- Project: Shire Journey, UE 4.27.2 C++, Windows/DX11, 720p, i7 6th gen / 8 GB RAM / ~2 GB VRAM / target >=30 FPS.
- Canonical integration: `develop` at `03df3c34a7a5faa47a69bf882edc0a7afd01000e` as checked 2026-10-15.
- Active runtime: **PES-002 Bag End Exterior, OPEN**; PES-001 bounded import/placement complete, NOT visually accepted; PES-003+ runtime locked by Gate 6/7.
- Active candidate: [PR #477](https://github.com/4youbabee-tech/fellowship-personal-game/pull/477), `fix/pes002-bag-end-lighting-20261014`, verified pre-update HEAD `85cfda35c24f2a574f768cff806ddbfdfd0c1381`.
- One Unreal Writer, one Warehouse Writer, one active runtime PES, one coherent PES PR; do not auto-merge or cancel a running writer.

## Proven evidence (specific HEAD, never extrapolate to successor)
- On `f7ae873...`: Pre-Unreal 38638641156 PASS, hosted Unreal classifier 38638641056 PASS but Windows UE job SKIPPED; Frodo source FAILED. Earlier Unreal builds do not validate later changed C++.
- Human Character Wave 2 Run 38634791736 FAIL and Frodo Locomotion Run 38634791700 FAIL. No real five-character rig/motion acceptance.
- Historical 90 restored UE assets and 48 placed Cloud138 instances proven for PES-001 only (Run 38526869417).
- Bag End real screenshots historically reviewed and REJECTED. No current visual/traversal/PIE/device/30FPS acceptance. No saved terrain .umap proof.

## Immediate critical blockers
1. Exact-head faaee053 Windows capture FAILED because fixed 86-second watcher killed UE4 during initial RHI/shader DDC start; candidate fail-closed readiness polling pending new engine proof. Bag End image quality: primitive/occluded silhouettes, darkness diagnosis needs fixed Lit/BaseColor/WorldNormal evidence; no cause assumed without matched captures.
2. Frodo rig: insufficient exported bilateral limb/head skin influence and failed hosted source runs; preserve rigorous deformation guard, no premature promotion.
3. P1C01: real saved/reopened .umap, geographic route, river crossing collision/NavMesh and 720p aerial screenshot NOT PROVEN.
4. Low-spec profiling and 30 FPS are UNMEASURED on target hardware.

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
