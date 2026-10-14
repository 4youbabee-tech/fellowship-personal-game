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
