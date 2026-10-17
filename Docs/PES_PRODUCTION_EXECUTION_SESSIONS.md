## 2026-10-17 PES-002 exact-head cottage HISM import — screenshot/performance proof blocked by background window
- Runtime owner remains PR #484; exact SHA `75176532cf77e3236fa5ff5be04cd406bb3e56b8`. UE4.27.2 C++ build, 484-file production import (0 failures), Automation QA and playable startup passed. Markers confirmed 7 existing house actors styled, two authored visual HISM families and retained collision owners; no duplicate facades.
- Initial ArtifactService lookup failed with `ENOTFOUND`; retry of failed jobs succeeded on the same SHA.
- Capture guard observed 20/20 `active=False` foreground samples and failed closed with `PES002_PERF_INCONCLUSIVE_BACKGROUND_THROTTLE`; no screenshot was produced. This is not a renderer or game-frame performance measurement. Keep Gate 6/7 open; do not bypass foreground validation.
- Exact focused source tests on the candidate: visual contract 17, curated PBR contract 3, joined facade contract 3, hero texture contract 3 — PASS.

2026-10-14 PES-002 CAMERA-EVIDENCE ROOT-CAUSE HERO FACADE CORRECTION: Inspected three actual UE4.27.2 1280x720 PNGs from Run 38563272174 artifact 11892194952, SHA256 view0 3128205E4EB4A7864C3BEE5CCFB9B65FA6AB26B1664BC3B8916763ACA80E0F28 / view1 1D58E33689BB179E890AFE2082F51D6A37717995D909DDF09DC92B59D7382FDE / view2 2BF76E5A5A040A19388771134F5EB0B87B3EBAF671C6585181C9DD51287ECAB9. Real images show restored textures/color but oversized green mound hides facade, plus dense foreground proxy fences/NPCs; no visual acceptance. Focused C++ candidate shifts only Bag End's earth mound +260cm behind its west-facing facade, reduces mass, gives hero turf nonblocking collision, retains existing blocking facade/story anchors, and adds a recognizable low-cost green round door silhouette and static source regression. This is a candidate pending exact-head build, new visual images and real traversal/collision evidence; physical authored facade mesh/material and target-device 30 FPS still not accepted. No PES-003.

2026-10-14 PES-002 VISUAL REAL-RUNTIME DEFECT REPAIR WAVE: Exact-head PR #477 Run 38561717050 proved UE4.27 C++ build, 90 Cloud138 restored .uasset packages, three Automation tests, headless startup, runtime 1280x720 BagEnd-directed screenshot SHA256 EC7F6789E8B2F96F88BC0FFD417D857D787EE28F93D92C9640703F332AA98936 and 12/12 grounded Bag End Cloud138 props. Human examination of actual image REJECTED visual: rough grey buildings, low-detail NPCs, heavily occluded hero facade. The screenshot log directly identified M_ProductionFoliage shader default fallback due SimpleGrassWind required AdditionalWPO missing, and both M_ProductionSurface/M_ProductionFoliage bUsedWithInstancedStaticMeshes missing. Repair candidate modifies existing UE editor import material masters (including persisted assets) to add mandatory AdditionalWPO zero input, enable instanced material usage, save changed master .uasset; captures three Bag End angles to avoid accepting a misleading occlusion. This repair must be recompiled and inspected on a NEW Windows run; no visual/traversal/PIE/device acceptance claim and PES-002 remains OPEN.

2026-10-14 PES-002 ROOT-CAUSE CI RETEST candidate: PR #477 exact-head af9e827 failed Pre-Unreal Run 38561472948 at PG-172 because three SkyLight RecaptureSky() calls violated the existing precisely two-call invariant. Root-cause change moves startup recapture exclusively to the deferred one-shot post-sky-init timer, retains the authored quest/story recapture, removes immediate duplicate and adds exact count regression to the focused PES contract test. No gate bypass; retest required. UE Build Run 38561473150 was still in progress at diagnosis. PES-002 OPEN.

2026-10-14 PES-002 ROOT-CAUSE AND CAMERA/LIGHTING CORRECTION CANDIDATE (DEC-PES-ROOT-20261014): Source audit of develop@03df3c3 found prior HighResShot used the ordinary player view without aiming at Bag End; the received 1280x720 Unreal image shows dark/unpolished architecture and no accepted Bag End facade. This wave adds opt-in proof-only Bag End camera/framing after runtime world initialization, delayed capture and strict PNG/log/dimension checks; raises baseline sun/skylight/exposure and adds deferred sky recapture to address premature dim sky illumination. The camera is gated by -PES002VisualProof outside shipping and never moves the gameplay player or changes quest, nav, NPC or save ownership. Exact-head hosted static, real UE4.27.2 C++ build and a NEW screenshot/traversal proof must still pass. No physical new FBX/PNG/material import, no visual/PIE/device/traversal acceptance, and no Gate 6/7 closure are claimed. Active PES-002 remains OPEN; do not open PES-003.

2026-10-14 PES ONE COMPLETE BATCH CONTRACT: Before each PES begins, inspect current develop HEAD, ProjectGovernor, gates, source/warehouse/Unreal receipts and chapter canon; enumerate the full named session deliverable and its exact assets, C++ changes, placement, focused tests and synchronized documents. Prepare one cohesive complete change wave and one PR whenever technically possible, not a parade of partial micro-PRs requiring owner 'continue'. After hosted source/static and necessary Unreal compile/import/startup run, repair verified failures in bounded corrective commits and retest; deliver a single evidence-based session report. Keep one Unreal writer/one Warehouse writer and no broad audits/package until chapter closeout. If missing actual screenshot/traversal/PIE/device evidence, remain OPEN and report blocker, not fake completeness. No automatic ongoing background work promise beyond a live execution.

2026-10-14 PRE-UNREAL FOCUSED PES CHANGE (PR candidate): default pre-unreal hosted checks retain exact-head source checkout, classifier regression, Windows packaging safety contract, PowerShell syntax, project structural validation, Project Governor, source-to-Unreal PBR integrity, Governor work-start and semantics, strict asset quality audit. 35 broader cross-chapter, historical provider/hero, warehouse regression, deep audit and reporting test steps are deferred to explicit workflow_dispatch chapter_closeout_audits=true, without disabling GitHub Unreal focused compile/import/startup or Gate 6/7. This is CI scheduling only, not a claim of FPS/visual acceptance.

2026-10-14 VERIFIED SESSION TRANSITION (owner authorized): PES-001 Asset Recovery & Import = COMPLETE for its bounded import-and-placement deliverable only, supported by Windows Run 38526869417 on develop@e1acb85a5f972f521de2f5888a52561d77bf6877: UE4.27.2 ShireJourneyEditor build SUCCESS; CLOUD138_UE_RESTORED_SHA256_PASS files=90 bytes=19394460; AUTOMATION_SUITE_PASS tests=3; P1C01 headless startup PASS cloud138 families=8 grounded=48 cap=48. PES-001 PIE=false, device=false, visual_accepted=false, chapter Gate 6/7 remains OPEN; no FPS or human render claim. Owner explicitly defers human visual review to PES-002. PES-002 Bag End Exterior = ACTIVE, NOT COMPLETE: architecture/garden/terrain/packed-PBR and actual screenshot/traversal are its required deliverable, not demonstrated yet. Existing SM_ShWoodenFootbridge remains NAV_QUARANTINED; no unsupported traversal claims.

# SHIRE JOURNEY — PES Production Execution Sessions (24)

Status: **REGISTERED ON DEVELOP** (PR #462 merged 319e07c8). This file is a subordinate execution schedule; **Data/ProjectGovernor.json** and **Docs/DEVELOPMENT_GATES.md** govern all decisions and chapter gates.

## Naming and delivery contract

- **Execution Order** = owner command; **PES-NNN** = one accountable production execution session; **Task/Milestone** = work inside it; **Commit/PR/Actions Run** = separate evidence artifacts.
- One PES targets a bounded, real deliverable in one execution session. This is a target **not** a promise to pass Unreal or visual tests in a fixed time. If blocked, retain **OPEN/BLOCKED** and finish in the next session without renumbering, losing existing work, or counting retries as net-new production.
- Keep **one runtime writer** for P1C01, **one persistent Warehouse writer** and up to **five independent source-only lanes**. No P1C02+ runtime activation before predecessor Gate 6/7 evidence. Preserve existing 28-region source preparation contract.
- Track source-generated, source-QC, persistent Warehouse, imported/reopened UE .uasset, world-placed/observed, PIE-tested, device-tested and visually accepted **separately**. Filename counts, ZIP members, CI success, screenshots from references and duplicated source must never be promoted.
- Follow DEC-042 branch lifecycle: create -> exact-head validate -> merge eligible work into develop -> safely delete temporary ref. Reuse existing cleanup tools. No blind deletion.
- For actual C++ deltas, update CURRENT_PROJECT_STATE and PRODUCTION_COMPLETENESS_MATRIX in the same PR; update WORLD_DETAIL_LEDGER when world/decision changes. Source .h under Public; .cpp under Private. Observe async soft refs, FStreamableManager, HISM/ISM, pooled NPC, FBX rigged, packed PNG/TGA and target 8GB/2GB DX11 720p 30FPS proof.


## Focused owner-authorized Windows PES proof

2026-10-14 PES FOCUSED WINDOWS EXECUTION: fix previous manual Run 38525471144 incorrectly classified `static` and skipped Unreal. New explicitly owner-authorized workflow_dispatch input `pes_focused_unreal=true` with `run_self_hosted=true` forces classifier `core` (UE4 editor compile, importer, persisted Cloud138 restore, automation and P1C01 headless startup) while `package_windows=false`, `part1_closeout_approved=false` keeps Cook/Package and broad all-chapter audits off. Runtime evidence is not a visual screenshot/PIE claim. Current PES-001 OPEN until specific evidence proves its closure.

This is an opt-in escape hatch when the exact-source classifier has already reused a green ancestor and a new physical Windows check is needed; ordinary push/PR stays cheapest-safe, and the single runner remains serialized.

## Owner-authorized expensive closeout switch (2026-10-14)

2026-10-14 OWNER CI THROUGHPUT POLICY (implementation candidate; PES-001 OPEN): ordinary PES runs retain mandatory exact-head hosted/static guards, required changed-C++ UE build, asset import/reopen and focused startup only. Deferred until explicitly owner-approved Part I/chapter closeout: full chapter runtime sweep, full route/story roundtrip, global warning debt and Windows Cook/Stage/Package. Workflow now requires BOTH package_windows=true and part1_closeout_approved=true; accidental package_windows alone cannot activate these expensive stages. Does not delete Gate 6/7, PIE, device, visuals or project acceptance obligations. No new asset/PIE/device claim.

Do not enable `part1_closeout_approved` during PES-001/PES-002 ordinary asset production. At Part I/chapter acceptance, explicitly approve closeout with both inputs and collect remaining PIE, target-device and human visual evidence separately.

## PES fast-batch operating protocol (PES_FAST_BATCH_2026_10_14)

- **One accountable PES, one finalized candidate wave.** Diagnose read-only first, group the repair + regression + required docs and Governor updates in **one atomic multi-file commit** rather than one commit per file. Each push restarts relevant PR workflows, so avoid premature pushes.
- **Stage the cheap checks first.** Confirm exact HEAD, input receipts, source families and cached SHA results on the candidate. Then exact-head static/hosted tests, **one warranted Windows UE/warehouse run** after the set of changes is stable. Reuse the closest valid existing evidence only where current Governor classifier explicitly allows it.
- **Failure batch discipline.** Extract exact failing assets and inventory siblings before fixing. Fix verified root causes collectively; quarantine independent failures without letting one unrelated defective asset block other source-only prep. Never broaden collision fallback without source evidence and a regression guard. A failed Windows run justifies a new bounded repair wave, not many guesses or repetitive full runs.
- **Protected expensive lanes.** Exactly one Windows Unreal writer and one persistent Warehouse writer; no interrupting a currently active writer merely to start a newer speculative build. Prepping five source-only lanes remains allowed.
- **Hard requirements untouched.** Keep Gate 6/7, file licensing, UE4.27 source/import/reopen/persistence proofs, world placement, PIE, device performance and visual review, mandatory doc sync and PR exact-head acceptance. Do not claim this policy change itself imports anything or suppresses CI automatically.
- **Session-end scoreboard:** previous->current for all five asset funnel stages, newly committed files/SHAs, count of heavy runs *and wasted/cancelled runs*, evidence for real Unreal imports and placed instances, elapsed time if recorded, status and exact blocker. A PES one-session closeout is a target, not guaranteed technical success.

## Fixed PES map

| PES | Name | Runtime scope | Session deliverable |
|---|---|---|---|
| PES-001 | Asset Recovery & Import | P1C01 runtime (subject to gate) | Inventory source/warehouse/asset-registry and import a bounded first eligible batch; prove reopened uassets and placed samples |
| PES-002 | Bag End Exterior | P1C01 runtime (subject to gate) | Restore and place exterior architecture, garden, terrain, packed PBR; verify actual screenshot and traversal |
| PES-003 | Bag End Interior | P1C01 runtime (subject to gate) | Furniture, doorway, interior materials and accessible entry only if implemented and tested |
| PES-004 | Hobbiton Houses | P1C01 runtime (subject to gate) | Modular hobbit houses, roofs, windows, doorways, fences and collision |
| PES-005 | Hobbiton Streets | P1C01 runtime (subject to gate) | Road surfaces, market props, signs, clutter and walkable connected lanes |
| PES-006 | Shire Vegetation | P1C01 runtime (subject to gate) | Tree/hedge/grass families and realistic distributed LOD/HISM vegetation |
| PES-007 | Shire Roads & Fields | P1C01 runtime (subject to gate) | Roads, worked fields, fences and continuous traversal |
| PES-008 | Rivers Bridges & Ferry | P1C01 runtime (subject to gate) | Water-edge dressing, bridges, ferry platform, collision and nav |
| PES-009 | Frodo Skeletal | P1C01 runtime (subject to gate) | Licensed skeletal FBX, deformation, materials, anim blueprint and playable movement |
| PES-010 | Gandalf Skeletal | P1C01 runtime (subject to gate) | Licensed skeletal FBX, materials, locomotion and interaction after Frodo evidence |
| PES-011 | Hobbit NPC Population | P1C01 runtime (subject to gate) | Distinct NPC visual variants with pooling and safe trace interaction |
| PES-012 | Living Village | P1C01 runtime (subject to gate) | NPC activities, contextual schedules and ambient response with bounded overhead |
| PES-013 | Animals & Wildlife | P1C01 runtime (subject to gate) | Ambient wildlife assets, motion and audio with distance culling |
| PES-014 | Dialogue & Sound | P1C01 runtime (subject to gate) | Rights-cleared ambient/foley/audio, dialogue/voice/subtitle correctness |
| PES-015 | Quest & Cinematic Integration | P1C01 runtime (subject to gate) | Whole route quest, chapter chronology, cinematic input, save/load and rollback |
| PES-016 | Shire Gate 6/7 Acceptance | P1C01 runtime (subject to gate) | Real PIE, DX11 720p target FPS/VRAM and human scene/pacing approval; gate closure only on evidence |
| PES-017 | Bree Preparation | SOURCE ONLY until predecessor Gate 6/7 | Source-only kits until predecessor accepted; after gate, integrate and test chapter |
| PES-018 | Weathertop Ford Preparation | SOURCE ONLY until predecessor Gate 6/7 | Source-only ruin, terrain and water kits; later gated runtime integration |
| PES-019 | Rivendell Preparation | SOURCE ONLY until predecessor Gate 6/7 | Source-only elven architecture/landscape/character kits; later gated runtime |
| PES-020 | Caradhras West Gate Preparation | SOURCE ONLY until predecessor Gate 6/7 | Source-only mountain/snow/gate kits; later gated runtime |
| PES-021 | Moria Preparation | SOURCE ONLY until predecessor Gate 6/7 | Source-only halls/mines/enemies/lighting kits; later gated runtime |
| PES-022 | Lothlorien Preparation | SOURCE ONLY until predecessor Gate 6/7 | Source-only foliage/structures kits; later gated runtime |
| PES-023 | Anduin Preparation | SOURCE ONLY until predecessor Gate 6/7 | Source-only river/bank/boats kits; later gated runtime |
| PES-024 | Amon Hen Preparation | SOURCE ONLY until predecessor Gate 6/7 | Source-only ruins/woodland/encounter kits; later gated runtime |

**Quantity planning is not evidence:** size batches by actual available sources, machine capacity and verified import/reopen capacity; report target vs achieved without inventing counts. Part II and III are future source-design lanes, not accepted runtime chapters.

## Exact beginning command (copy and replace PES number)

> Execute **PES-NNN** from this schedule on live GitHub develop. Read Data/ProjectGovernor.json, current gates and exact HEAD; inspect sources/Warehouse/Runner capacity, reuse verified assets; deliver the named bounded result in P1C01 or source-only for future gated chapters. Use single writers, original licensed content, incremental safe import and actual gameplay/visual proof. Validate the exact candidate, merge only when eligible and safely clean its branch. Emit the PES end report below. If acceptance blocks, leave this PES OPEN/BLOCKED and report exact blocker, not a fake completion.

## Required end report (no fabricated zeros or percentages)

| Field | Value / evidence |
|---|---|
| Session and status | PES-NNN / OPEN, BLOCKED, or COMPLETE |
| Actual output / target | Named player-visible deliverable vs intended |
| Start -> end HEAD | SHA -> SHA |
| Assets SOURCE_CREATED / QC_PASSED | Distinct SHA256 counts, license receipt |
| WAREHOUSE_PERSISTED | Distinct hashes, durable receipt |
| UE_IMPORTED_PERSISTED | .uasset paths, import log, reopen/cook proof |
| WORLD_PLACED_OBSERVED | Real actors/instances, map, scene capture |
| Characters / quests / defects | Named playable tests and results |
| Build / PIE / device / visuals | Actual labels with logs, FPS/VRAM when measured; otherwise NOT TESTED |
| Commits / PRs / Actions | Exact IDs and checks |
| Branch count / deletions | Baseline, end, verified deleted refs |
| Previous vs current / delta / percent | Separate per-funnel counters; (current-previous)/previous * 100; N/A if unknown/zero |
| Blockers and next step | Exact technical blocker; do not silently close the PES |

A PES is **COMPLETE** only when its own required outcome and evidence exist; documentation or source-only completion cannot claim visible-world acceptance. Where stage is defined SOURCE ONLY, mark that scope explicitly; never claim chapter complete.

## Closeout-only broad tests — policy 2026-10-14
During an ordinary PES development commit, keep only checks relevant to its changed files: hosted static/Governor, targeted source regressions, UE C++ build if engine/runtime source changed, quick startup smoke when runtime compile is needed, and dedicated editor import-reopen-persist when assets change. Do not run the **chapter-by-chapter sweep**, **route/story state roundtrip** or **global runtime warning-debt sweep** on every commit. They run together on explicit owner chapter closeout (`workflow_dispatch` with `package_windows=true`). Gate 6/7 still needs real PIE/device/visual/performance and other acceptance evidence; no skipped fatal safety conditions. This policy does not imply PES-001 is complete or any game asset is placed.
2026-10-14 PES-002 RENDER-REJECTED COMPOSITION ROOT-CAUSE REPAIR: Exact-head PR #477 Unreal Run 38599254268 succeeded for UE4.27.2 compile, import/rehydration, Automation, startup and three mandatory 1280x720 captures; artifact 11913641348 digest sha256:066d0e4addd738639f9681dff57ab9db25060b7a01c30541d6c0967fc63aec0b. Human inspection REJECTED all three images: Bag End remained a flat proxy facade, cameras were too close, dense repeated hedge/grass/prop layers obscured the entrance, and modular characters were obvious placeholders. Runtime log independently confirmed Frodo/Bilbo/Gandalf and other named rigs packages-missing with fallback=modular. Bounded repair moves the decorative mound farther behind and reduces it, widens all three proof views, reduces only Bag End hero detail/density layers while preserving quest anchors, blocking facade/step and population ownership, and adds exact source regression assertions. Character final-art remains blocked on real skeletal FBX packages and is not claimed fixed. STATIC-VALIDATED locally; exact-head UE rebuild/new screenshots/traversal required. PES-002 OPEN; PES-003 locked.\n\n

## Permanent owner mandate — Professional preproduction before every PES (2026-10-14)
Every one of the 24 PES sessions must begin with a **read-only preproduction inventory and professional reference review** before code, asset creation, PR upload or costly Windows runner. Relevant official Epic UE4.27/Blender technical documentation and reproduced professional pipelines must be attached as methods/links, matched to actual missing requirements of the **current** chapter, legal provenance and low-end limits. Include things the owner may not know to ask about: scale, UVs, skin weights, bind pose, material slots, package path, collision/NavMesh, NPC ownership, animations, water, lighting, shaders, performance and screenshot tests. Package all dependencies, checks, docs and rollback plan into one preflighted cohesive candidate and ONE planned push. No guaranteed zero errors; no repeated unchanged failures. Use exact-head engine proof, corrective retest when truly necessary, and Gate 6/7 evidence. Governor authoritative policy: `pes_professional_preproduction_gate_2026_10_14`.

## Owner-approved asset-first acceleration (2026-10-14)
Governor key: `pes_asset_first_production_acceleration_policy_2026_10_14`. Prioritize licensed ready-made assets with real UE4 import/placement/render evidence; avoid redundant automation, use verified fast PIE, keep Windows builds planned, prepare 30-45 minute owner review and report actual assets, net game-code LOC and gate-based chapter progress. Keep existing per-code-batch state/matrix updates, M0-M7 evidence and Gate 6/7. No arbitrary 50% file quota. PES-002 remains OPEN.

## 2026-10-15 M0 focused reference intake (supplement, no gate waiver)
Read `Docs/CURRENT_STATE_SHORT.md` first for current *orientation only*. Then inspect live `Data/ProjectGovernor.json` and PR HEAD/Gate 6/7, existing source/test data, actual Unreal screenshots/warehouse rights and use targeted search into existing long historical ledgers. Short index NEVER replaces the Governor, Stage M0 evidence obligations, or exact-HEAD verification; historical ledgers stay intact. One runtime PES and one coherent PR, tracked under Governor key `pes002_owner_acceleration_2026_10_15`.

## 2026-10-17 PES-002 settlement cottage visual replacement candidate
- This is a continuation inside active PES-002 / W01 P1C01, not a new PES or a second runtime owner. M0 reviewed current `develop@6c5261a`, Governor W01 `PARTIAL`, Gate 6/7 open, the existing PR #484 runtime lane and the latest four-view Unreal evidence.
- The observed six-cottage backdrop still mixed authored and 71-triangle prototype shells. Candidate batches the two already-imported 1,148-triangle cottage families in two no-collision HISM clusters across the six existing domestic placements and village-common backdrop. Original blocking meshes and all positions/rotations/scales remain unchanged.
- Focused local source tests passed: `test_pes002_visual_contract.py` (17), `test_pes002_curated_pbr_shader_contract.py` (3), `test_pes002_joined_facade_source.py` (3), and `test_pes002_hero_texture_contract.py` (3). Exact-head UE4.27 compile/import/PIE and rendered review are still required; session remains OPEN.

## 2026-10-17 PR #484 repeated capture failure — recovery candidate
- Exact-head runs 39019099042 (`75176532...`) and 39020520026 (`cc577de...`) both passed build/import/automation/startup, then failed after PIE because 20 consecutive probes found the owned Unreal window inactive. Run 2236 artifact 12096323695 includes no fresh PNG; older profiler CSVs are not fresh proof. Do not infer visual/FPS acceptance from log markers.
- Candidate change attaches the worker input queue to only the owned editor and observed foreground thread during activation, then detaches in `finally`. Preserve the active-window guard. The new source regression checks activation and cleanup. If exact-head focus still fails, stop repeating and report the interactive desktop blocker. No package dispatch.
- Scope remains existing PES-002 / P1C01. No new runtime PES, no gate waiver.

- Follow-up run 39021746348 showed the first activation recovery had a P/Invoke defect: `GetCurrentThreadId` belongs to `kernel32.dll`, not `user32.dll`; the job timed out before requesting any screenshot. Correct the import and emit the inner exception in any future probe error. Validate once on exact head; if still blocked, stop repeated retries and repair the interactive desktop owner-side.

## 2026-10-17 — Run 39022384250/#2238 visual and runtime evidence
- Exact-head Windows CI passed build/import/automation/startup and produced four real PIE PNGs; 16/16 foreground samples confirmed the editor active. Artifact 12096524213 carries four 1280x720 views, a fresh CPU/GPU CSV and incident stats.
- Captured FPS windows were 21.39–28.27, with hitches up to 362.15 ms. Dedicated/shared per-process memory peaked at 534.71/102.82 MiB; target-device acceptance remains false.
- Visual inspection rejects final Shire acceptance due to conspicuously angular/primitive vegetation and props, repetitive density, and unresolved terrain/ground composition. Continue bounded PES-002 art correction; Gate 6/7 remains open.
