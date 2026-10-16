## 2026-10-16 PES-002 Bag End final source candidate / real prior run
| Stage | Evidence |
|---|---|
| Baseline previous commit | d07df57c; UE4 Run 38938627683 PASS, four 1280x720 PIE PNG artifact 12063330802; 19/20 existing imported architectural FBX props actually placed, 25/25 garden items |
| Performance state | Foreground PID 15/15 confirmed; CI late 5s ~25–28 FPS and process GPU dedicated ~556 MiB; target laptop NOT TESTED, required ≥30 FPS unmet |
| New candidate | Existing HISM PBR curated gorse/hedge replace max 18 near hero low-poly no-collision shrub instances; reframe 20 imported cart/planter/hedge/lantern/stone props, minor non-volumetric fog distance adjustment |
| Scene fidelity | Previously dark generic shrubs, distant lowpoly trees and modular NPCs make visual gate FAIL |
| New code exact-HEAD UE4 and screenshots | NOT RUN until CI, accept only actual package, world placement and render |
| Governance | PES-002 active, PES-003 locked; visual/PIE/traversal/device Gate 6/7 OPEN |

## 2026-10-16 PR #484 Bag End imported architecture candidate
| Item | State |
|---|---|
| Scope | PES-002 exterior, 5 UE4 imported static FBX families, maximum 20 HISM decor instances |
| Code | Existing async loader, traced ground, no collision, no new manager; old rejected extra woodland swap removed |
| Runtime family/placed proof and 4 screenshots | NOT RUN on new head |
| Target device and visual acceptance | NOT RUN / NOT ACCEPTED; Gate 6/7 OPEN |

## 2026-10-16 PES-002 PR484 foreground and render-wait incident evidence
- PR484 incident diagnosis candidate, NOT ACCEPTED. Baseline early 3FPS late 25-28FPS; branch 3FPS exact despite only 12 trees. GPU ~44ms vs ~251ms render EventWait. Root discriminator: confirm owned PIE editor foreground PID, reject inconclusive if focus unproven; record bounded native UnrealStats .ue4stats. No new assets, texture import, cull changes, or FPS claim; exact-head Windows Run and target-device test PENDING. PES-002 active / PES-003 locked.

## 2026-10-16 PR #484 PBR woodland regression and bounded corrective retest
| Evidence | Result |
|---|---|
| First branch head bef5eefa257da222f49120adb47fc7929cc8bd94 | UE4.27 CI Run 38905549201 SUCCESS, 4 PIE shots artifact 12048517139 |
| Actual converted woodland tree actors | 67 (separate from earlier 21 matched proxies); source meshes physically imported from existing curated set |
| Game-frame FPS on Runner during proof | ~3.0 FPS at 15-50s in capture vs prior 25-28 steady; FAIL |
| GPU profiler mean / draw calls | ~44.1 ms / 731 vs baseline ~36.3 ms / 667; suspected heavy visible foliage contribution, not verified unique root |
| Windows OS dedicated GPU memory peak | ~589 MiB, comparable to baseline ~592 MiB; no device proof |
| Correction prepared | 12-per-scene sparse selection, deterministic 1/4 thinning, 67-replacement candidate NOT ACCEPTED |
| New exact-HEAD compile/PIE/FPS/visual | PENDING, Gate 6/7 OPEN; PES-002 ACTIVE, PES-003 LOCKED |

## 2026-10-16 PES-002 Bag End village-band tree replacement candidate
| Layer | Status |
|---|---|
| BASE | develop 3b9d90d5667b64ce46ec5613e6c6462ebf0cbac3; PR #482/#483 integrated |
| SOURCE | Real curated tree FBX/PBR package families already handled by existing async loader; no new external license claim |
| CODE | Candidate: replace up to 96 local non-colliding WoodlandTreeInstances proxy silhouettes with existing tree HISM only on package and ground success, preserving fallback otherwise |
| STATIC | Focused regression in existing Scripts/test_pes002_visual_contract.py; new candidate CI not yet run |
| UE4 COMPILE / REIMPORT | NOT RUN at new candidate SHA |
| WORLD_PLACED / RENDER_OBSERVED | Need actual PES002_BAG_END_WOODLAND_FBX_REPLACEMENT runtime counts and four new native UE4 1280x720 screenshots |
| DEVICE / FPS / VRAM / HUMAN VISUAL | NOT RUN / NOT ACCEPTED; Gate 6/7 OPEN |
| GOVERNANCE | PES-002 ACTIVE, PES-003 LOCKED; no other regions or writer ownership changed |

## 2026-10-16 PES-002 data-driven garden and resident variation candidate
- Baseline develop 2e190d6: engine build/import/PIE pass with 5 skeletal shared residents, 21 tree replacements and 4 screenshots. Full visual and performance gates OPEN.
- Candidate: 25 explicit garden data rows in existing Data/P1C01VerifiedWorldDecor.json, checked against actual UE-imported PBR FBX nature mesh packages. Candidate runtime evidence markers PES002_BAG_END_DATA_GARDEN and PES002_RESIDENT_PRESENTATION_SNAPSHOT; 5 proportional resident variants and optional safe authored-material tint.
- New candidate UE build/PIE screenshots and counts PENDING; named canonical cast 4 different rigs NOT PRODUCED; target Windows/DX11/720p minimum 30FPS NOT DEVICE-TESTED; PES-002 ACTIVE/PES-003 LOCKED.

## 2026-10-16 PES-002 in-engine import and runtime-evidence candidate (not a completed gate)
- Active PES-002 only: UE4 C++ FBX authored material/texture path + packed PBR exception, skeletal blend-weight QC and fail-closed import result, after-save actual Content/Production .uasset class/path/bytes ledger; runtime Bag End grounded authored-FBX HISM garden up to 24; capture-only 5-second FPS and RAM sampling. All statuses pending exact-HEAD CI and rendered review.
- SOURCE_AVAILABLE: existing curated FBX/PBR; WAREHOUSE_PERSISTED: existing receipts; UE_IMPORTED and WORLD_PLACED: require new on-disk UE4 ledger and runtime markers; RENDER_OBSERVED: require new 4 actual UE screenshots; ACCEPTED/PIE/DEVICE/PERFORMANCE: NO. Skeletal animation/AnimBP and approved deformed characters: NO.

## 2026-10-16 PES-002 bounded living-world terrain follow candidate
| Requirement | Actual state / evidence |
|---|---|
| Live canonical baseline | develop 1f5173f4285dac63d3bd0b0a602c9025aee3ba0c; Pre 38821850890 SUCCESS, UE 38821850726 SUCCESS before this candidate |
| Visual M0 input | Four actual UE4.27.2 1280x720 Bag End PNGs in artifact 12013596745: HERO RENDER_OBSERVED, human visuals NOT ACCEPTED |
| Ground-trace source | Director probes start/end locations for managed resident routines, but existing ShireAmbientNPC walking path changed XY only; missing Z progression (source root cause) |
| M1 patch | Resident-managed ground walk Z follows clamped ground-probed A/B endpoint gradient; no new assets, traces, collision, story anchors, quest logic, runtime owners |
| Focused source regressions | Existing Scripts/test_pes002_visual_contract.py extended; candidate static and Unreal CI required |
| Exact-head UE4.27 compile/import/render | NOT RUN for new candidate (do not substitute prior 38821850726) |
| Real route/collision/NavMesh and full PIE | NOT RUN / NOT ACCEPTED |
| 8 GB / 2 GB DX11 720p >=30 FPS, user visuals | NOT RUN / NOT ACCEPTED |
| PES control | PES-002 ACTIVE, PES-003 LOCKED; Gate 6/7 OPEN |

## 2026-10-16 develop handoff — selective PR #456 safety forward-port
| Scope | State |
|---|---|
| 43 outdated branch heads | SHA-archived, not automatically runtime-merged. Branch cleanup PR #478 merged as fe95cb82. |
| Cinematic QuickSave / QuickLoad and saved rotation | Source fix CANDIDATE selectively ported to up-to-date ShirePlayerCharacter.cpp and ShireQuestSubsystem.cpp; two focused regressions introduced. Prior PR #456 closed as old-lineage, not source-integrated. |
| Pre-Unreal and UE4.27 compile | PENDING fresh exact-head source candidate CI; do not substitute archival/legacy branch results. |
| PIE corrupt-save / route integrity, 720p FPS and human visuals | NOT RUN / NOT ACCEPTED. PES-002 remains ACTIVE; PES-003 remains LOCKED. |

## 2026-10-16 GitHub branch hygiene and truthful develop programmer handoff
| Gate | Actual outcome |
|---|---|
| develop PES-002 | PR #477 merged SHA 386a2968954ea6423ae37da011b35ef187f53849; Pre 38818365177 PASS, Unreal 38818365146 PASS |
| Remote ref inventory | 49 initial refs, 47 outside develop/main; first ordinary merge cleanup down to 46, 23 unmerged historical PRs |
| Immutable recovery | 43 divergent working heads preserved as 42 distinct direct parents of archival commit 5ca617729e359249e09aa6acc05734e814c594c4, separate from develop |
| Historical branch retirement | SHA + archive parent + no active PR guards prepared; hosted tests and physical deletion results PENDING |
| Unique unmerged changes | Preserved in Git archive ONLY, not build-validated or accepted; selective forward-port needed before any later use |
| UE4 PIE, device performance, human visuals | UNPROVEN / NOT RUN / NOT ACCEPTED; PES-002 ACTIVE, PES-003 LOCKED |

## 2026-10-16 PES-002 Cloud138 parent collision — strict evidence matrix
| Requirement | State / evidence |
|---|---|
| ROOT-CAUSE | CONFIRMED SOURCE ORDER: 90 archived Cloud138 .uassets include `/Game/Production/Materials/M_P1C01VerifiedPBR` shared parent; restoration ran after UE4 curated importer material repair, replacing master with archived copy. Runtime at 3b288ea logged SM5 fallback and missing instancing flag. |
| SOURCE / STATIC | Root-cause fix candidate: SHA-validate 90 archived, restore 89 owned, preserve 1 current shared master, fail closed for stale/missing/corrupt and verify parent checksum; focused regression tests introduced. Exact-head static CI PENDING. |
| COMPILE / UE4 RENDER | Previous 38814182452 compiled/imported/started but strict shader guard FAIL. Next commit compile and shader validation PENDING. |
| RENDER OBSERVED | 4 PNG real runtime artifact 12010491255 with default shader fallback; NOT ACCEPTED. |
| PIE / DEVICE / VISUAL / FPS | NOT RUN / NOT RUN / NOT ACCEPTED / NOT MEASURED, Gate 6/7 OPEN, PES-002 ACTIVE, PES-003 LOCKED. |

## 2026-10-16 PES-002 actual curated funnel and shader blocker
| Stage | Exact-run evidence / acceptance |
|---|---|
| SOURCE_AVAILABLE / WAREHOUSE_PERSISTED | 10 Drive source ZIPs verified by 38784273468; 120 externally held files unpromoted |
| UE_IMPORTED / PERSISTED | **118 exact checked packages** at 5943f38, 34 static meshes + 63 texture packages + 21 MI packages; 46 additional LOD imports (not separate packages) |
| WORLD_PLACED | **9 families, 92 grounded resident-only HISM instances** at P1C01 startup, confirmed by screenshot runtime log; 0 missing ground |
| RENDER_OBSERVED | **4 original 1280x720 PNGs** artifact 12009785712, actual PBR shader default fallback; human/assistant **REJECTED** |
| PASS | Source, importer, LOD, physical packages, Automation, startup, fresh screenshots; previous character Blender deformation run 38799014967 remains source-only |
| FAIL / BLOCKED | PBR SM5 master with invalid LinearColor/WhiteSquare fallback and missing instancing flag; 4 trees and 1 flower with unbound exact multi-slot finishes; named skeletal packages missing |
| PIE / VISUAL / DX11 720p FPS+VRAM | NOT RUN / NOT ACCEPTED / NOT RUN; no Gate6/7 or PES-003 opening |
- Actual exact-HEAD 5943f38f2288fe9575c44cc9712bf442bbad02bd: Pre-Unreal 38812432387 PASS, Windows Unreal 38812432393 PASS (curated .uasset import, LOD, editor material rebind/readback, Automation, headless startup, four 1280x720 Bag End captures). Artifact 12010085236 observed exactly 34 StaticMeshes + 46 authored sidecar LODs + 63 persisted PNG Texture .uassets + 21 Material Instances = **118 physically persisted checked packages**, NOT 118 newly created/accepted art assets. Artifact 12009785712 has four real images; assistant visual review REJECTED polished-world acceptance.
- Real runtime marker `P1C01_CURATED_NATURE_WORLD families=9 grounded=92 max=92 collision=none async=1` replaced prior `deferred=9 optional-packages-not-staged`. Screenshot now shows new grey rock/tree geom but is still stylized/primitive. No traversal/PIE/target-device FPS/VRAM; `LivingWorldCommitSync` and `NPCContextCommit` present but rig packages missing for Frodo/Sam/Gandalf/Bilbo/Merry/Pippin. XAudio2 hardware unavailable on headless runner; spoken audio NOT accepted.
- Root defects from same 5943f38 screenshot log: `M_P1C01VerifiedPBR` PCD3D_SM5 compiler says `(TextureSampleParameter2D) sampler Linear Color should be Color for WhiteSquareTexture` and `missing bUsedWithInstancedStaticMeshes=True`. Default shader used despite green import. Four tree meshes were correctly held because imported material labels are `M_Sh_Bark`+`M_Sh_Leaf`, not speculative `Bark`/`LeafGreen`; flower wild leaf/petal multi-slot remains HELD. Exact original `Tools/CloudAssetBuild/blender_nature.py` explicitly assigns M_Sh_Leaf=(0.16,0.39,0.11) green; this now licenses an explicit source-identity mapping, not a wildcard alias.
- Cohesive PES-002 source fix candidate: UE editor commandlet repairs both newly created and persisted PBR master AFTER real Bark ORM import by assigning an actual TC_Masks non-sRGB ORM default, matching `SAMPLERTYPE_Masks`, enabling `bUsedWithInstancedStaticMeshes`, and saving both packages; initial source WhiteSquare uses compatible Color sampler. Tree exact Blender-material names map to respective Bark/LeafGreen PBR MIs and are read back from persisted meshes. Focused static gates and PowerShell 4-view shader warning fail-closed guard added. No runtime NPC/story/collision/nav/save ownership edits; original modular fallback stays until skeletal UE motion accepted. Next exact-HEAD UE4 build/capture is NOT RUN at authoring; PES-002 OPEN, PES-003 LOCKED. Rollback cohesive batch on compile/import failure; do not label real screenshot visually accepted before owner/art and target-device checks.

## 2026-10-16 PES-002 bounded CI corrective candidate after 215cd6e
- Pre-Unreal Run 38811960960 FAIL only at test_unreal_classifier.ps1; test demanded core when existing strict classifier correctly returned full for mixed C++/curated changes. Unreal Run 38811960729 hosted classifier likewise FAIL; UE4 Windows job SKIPPED. No new .uasset/screenshot/PIE proof or cancelled writer.
- Fix preserves strict Full for C++/Config/unallowlisted deltas, corrects regression expectation, and permits at most TWO source-only/docs parent commits to reuse an existing green C++ engine proof only after exact path-diff audit. Current verified C++ boundary is 8982ca6 / UE4 Run 38803036724. Fresh imported LOD/PBR and 4-view proof remains mandatory on new exact HEAD. No relaxation of tests, Gate6/7, visual, PIE or device FPS.
- Single bounded correction on PR #477; PES-002 OPEN; PES-003 LOCKED. Rebuild is conditional on the newly passing static/classifier gates and available Windows writer; never rerun identical failed head.

## 2026-10-16 PES-002 curated import production funnel — exact-parent source wave
| Stage | Verified evidence / current boundary |
| --- | --- |
| SOURCE_AVAILABLE / WAREHOUSE_PERSISTED | 38784273468 PASS: 10 verified Drive ZIPs; 143 project-owned staged source files; 34 FBX families, 46 authored LODs, 63 packed PNG; 120 license-held third-party files excluded |
| UE_IMPORTED (new curated) | **NOT RUN**; 118 distinct `.uasset` mesh/texture/MI checks are a *target* of next exact-HEAD editor import, not an imported count |
| WORLD_PLACED (curated) | **NOT RUN**; existing 9 resident-only nature HISM groups (92 max) were deferred at baseline due package absence |
| RENDER_OBSERVED | Prior run 38803036724 produced 4 true 1280x720 images, but curated mesh layer absent; visual **REJECTED** |
| PIE_TESTED / DEVICE_TESTED / VISUALLY_ACCEPTED | NOT RUN / NOT RUN / NOT ACCEPTED; no FPS/VRAM measurements |
| Human skeletal/living-world completion | Frodo real Blender static deformation run 38799014967 PASS; runtime package still missing, no skeletal animation or conversational audio acceptance |
- Verified M0 source: `develop@03df3c34a7a5faa47a69bf882edc0a7afd01000e`, PR #477 baseline `8982ca6ff5493d361abd1507cd9a5b62dfaa8a19`. Pre-Unreal Run 38803036701 PASS; UE4.27 compile/import/startup/four 1280x720 Bag End PNG Run 38803036724 PASS, artifact 12006310058; *visual review rejected* (toy-like distant trees and modular NPCs). Actual log says `P1C01_CURATED_NATURE_WORLD deferred=9 optional-packages-not-staged` and `CharacterRigStreaming unavailable id=Frodo packages-missing`; screen proof is not PIE/device acceptance.
- Warehouse input already exists, no redownload: run 38784273468 PASS, ten SHA-pinned Drive ZIPs physically QC green; curated archive and project-owned 34 static FBX mesh families, 46 LOD sidecars, 63 PNG NormalDX/BaseColor/ORM maps (21 triplets) staged; 120 external license-ambiguous sources remain quarantined. The curated material/LOD stage is NOT a rendered/unreal-accepted asset.
- Scoped code wave on same PES-002/PR477: enhance existing UE4.27 curated editor post-import (no new importer) with provenance-bound Bark + LeafGreen/LeafAutumn tree section assignment and persisted `.uasset` readback; ambiguous section names are **HELD**, never silently applied. Keep exact 34 mesh/46 LOD/63 texture/21 MI = 118 distinct expected package checks. New classifier requires a green exact parent before single serialized curated Windows importer, followed by Cloud138 restore, automation/startup, fresh four-view Bag End capture, and upload of exact-HEAD editor receipt. Focused offline mock/regression now runs in ordinary Pre-Unreal; no whole-chapter Cook/Package, C++ runtime ownership, player collision, NPC, save, or story changes.
- Evidence at authoring: static helper local 4 tests PASS; changed full-repository mock CI and actual new-HEAD UE4 import/LOD, screenshot/PIE/traversal/device/FPS/VRAM **NOT RUN** until workflow completes. No imported/placed/accepted *new* assets claimed from source-stage counts. Only 1 Windows writer/1 Warehouse writer; PES-002 OPEN, PES-003 LOCKED. Roll back this one atomic source/tests/docs commit if existing engine import gate fails; fix root cause from actual log before any rerun.

## 2026-10-15 Owner CI throttle — prevent cumulative PR re-execution
- Actual PR #477 `ec92968ee92e22102f7890c6ad2020415c9d4930`: 7 workflows launched from a small mixed PR update, including unrelated human, KayKit and 28-region Blender prep, because GitHub `pull_request.paths` evaluates the entire accumulated PR diff (39 changed filenames), not only the latest commit. Merely narrowing PR paths cannot eliminate repeats. Last full exact-head Unreal 38799014982 PASS, character 38799014967 PASS; neither means new gameplay/visual/device acceptance.
- Implementation: five specialist source workflows use `push` with branch exclusions for canonical develop/main and explicit owned path lists; specialized human, Frodo, KayKit and five-lane remain available on workflow_dispatch; broad cloud 28-region build triggers only its own material/region generators/tests and region production packet, not all `Tools/CloudAssetBuild/**`. GitHub push path checks are the changed commit set of the push, not cumulative PR files. Never trigger a heavyweight unrelated builder solely due the importer's shared C++ file, ProjectGovernor logging or workflow edits.
- Essential automatic PR safety retained: Pre-Unreal strict source/rig/asset/Governor/PG-017 checks for non-doc changes, Unreal classifier with required actual C++/import/startup/visual evidence for runtime or asset changes. Manual specialist runs must still pass before promotion of their own changed rig/source inputs; for runtime unaffected files reuse SHA-grounded prior receipts. Gate6/7, no duplicate Writer, source licensing and 30FPS/device thresholds untouched.
- This is CI scheduling, not evidence of imported assets, in-game visual acceptance or measurable Windows speedup. Verify workflows on next relevant individual file changes; do not spam Windows merely to prove CI policy. PES-002 stays OPEN; PES-003 LOCKED.

## 2026-10-15 owner-requested CI administrative relief — docs-only trigger optimization
- Live PR #477 `ccde667d14f224382c63b63b6311c8806a717962`, develop 03df3c34: Pre-Unreal baseline 38795890147 PASS; Unreal 38795889983 PASS (actual UE4.27 build/import/screenshot), Human Wave2 38795889984 PASS. PES-002 still OPEN with visual, PIE, device acceptance pending. Existing Pre-Unreal already defers ~35 historical/cross-chapter audits to manual chapter-closeout and Unreal build workflow already defers cook/package/route audits. Screenshot UI lists those as skipped, not executed.
- Single narrow CI optimization: Pre-Unreal workflow push and PR triggers now ignore commits where ALL changes are docs-only (`Docs/**`, `**/*.md`). Mixed code+docs, ProjectGovernor JSON, script, 3D source, imports, workflow and policy changes still run exact-head validation unchanged. GitHub documented paths-ignore all-files semantics; workflow_dispatch can still run audits explicitly.
- No hard gate changes: Governor, asset rights, LFS PG-017, source/rig QA, Unreal compile/import, runtime screenshot, PIE, target performance, Gate6/7 and owner review remain mandatory where applicable. One runtime writer. No claim of new game content or reduced wall time for non-doc PRs.
- Verify via workflow trigger diff and one exact-head Pre-Unreal run, do not rerun Windows without runtime/code/asset change. Rollback paths-ignore filter if documentation-only changes are later found to carry executable policy (move such policy to Data/JSON or workflow and keep its tests).

## 2026-10-15 PES-002 PG-017 source binary governance correction (after 7119991)
- Actual exact-head Pre-Unreal Run 38795421128 FAIL at PG-017: four newly authored PNGs committed as raw blobs within LFS-controlled SourceAssets. This is a genuine content governance failure, not broken PNG/art material; no weakening/skip allowed. Subsequent Unreal run must not be promoted without fully green static validation.
- Root correction: remove those four raw binary paths from Git tree; keep reproducible project-owned generator under Tools and strict source-to-MTL checks. The existing Windows `ci_import_production_assets.cmd` will generate all four PNG textures into transient local SourceAssets path BEFORE Unreal importer. No LFS pointer with unpersisted payload, no artificial Git LFS object and no shared warehouse writer. CI on clean checkout generates texture inputs, validates MTL and real UE4 binding; missing generator/python fails closed. Windows source outputs are disposable/reproducible, NOT permanent Warehouse persistence.
- Regression updated: PNG byte checks operate on temporary output and do not require raw PNGs in Git; four PNG CRC/variation/size checks remain; no source-fidelity or visual standard lowered. Local focused source tests PASS 3/3 prior to this correction; exact new HEAD static/engine NOT RUN until push. No new PIE/device/owner visual acceptance; PES-002 OPEN, PES-003 LOCKED.

## PES-002 Bag End unique surface-art funnel — baseline a92d3971

| Deliverable | Baseline genuine evidence | This source-art candidate | Status |
| --- | --- | --- | --- |
| Roof-wall mesh / collision | Run 38789500278 import PASS, 2,780 triangles, 7 slots; collision/story anchors untouched | Same geometry and UVs; roof material rename Grass -> BagEndTurf; importer 7-slot hard gate updated | Static source candidate; new engine NOT RUN |
| Authored facade albedos | Old flat plaster / global Grass and dark door in real four-view images | 512px original Plaster/Turf/Door/Glass PNG, fixed seed and reproducible generator, MTL textures bound by existing UE4 importer | SOURCE_AVAILABLE/local source QC; no new UE import |
| Existing non-Bag-End Grass | Registered original MTL Grass and TX_ShGrass.tga | Left unchanged; unique BagEndTurf is hero-only | Preserved by source test |
| Unreal machine acceptance | a92d397 Run 38789500278 PASS 4 pictures artifact 12001805029, VISUAL REJECTED | Must prove new map textures in UE actual MI and all four rendered views | NOT RUN |
| Frodo human technical | Run 38789500373 ALL JOBS PASS; 90 bones / 5 hierarchy + 5 stress tests PASS | Separate source-only wave, not changed in art candidate | STATIC DEFORMATION PASS; no visual or runtime |
| World traversal/PIE/nav/collision | No exact route proof | No modifications | NOT RUN |
| DX11 720p >=30 FPS, RAM8GB VRAM~2GB | No measured device data | Worst-case four RGBA8 512px ~4MiB excluding mips; no claim of device FPS | NOT RUN |
| Owner visual & PES closeout | Existing screenshots rejected | Requires new capture and review | NOT ACCEPTED; PES-002 OPEN / PES-003 LOCKED |

## 2026-10-15 targeted Blender source-root correction after ee64aab
- Exact HEAD ee64aab, Pre-Unreal 38789083890 PASS (including six pure hierarchy tests). Hosted Human Wave2 38789084195 FAIL in Blender normalization before FBX: `GAME_RIG_REST_CHANGED DEF-hips` from `p1c01_game_deform_export.py` line 224; import/deformation steps SKIPPED. Actual log proves this is EDIT BONE parent / rest matrix sequencing, not a missing source or a reason to waive rest-pose protection. PowerShell downstream missing FBX is an effect, not the root cause.
- Corrective source-only candidate: set the new deform hierarchy first and then restore exact source world rest matrices in parent-before-child order, retaining the strict per-bone matrix equality and max 1% vertex rest-skin displacement checks. Do not reduce tolerances, invent animations or repeat source FBX without changed code.
- Exact-head Blender/FBX pose/UE acceptance pending next candidate; no new `UE_IMPORTED`, `WORLD_PLACED`, PIE, visual or target device evidence. PES-002 remains OPEN/PES-003 LOCKED; one writer.

## 2026-10-15 PES-002 Frodo rig M0 source-only repair candidate — awaiting new exact-HEAD proof
- Exact baseline: PR #477 at 73b82f13832711cec8d0f95067c83c86cc2e37f2, develop 03df3c34; all prior Unreal visual/PIE/device gates remain unchanged. Human Wave2 run 38781832030: licensed original CC0 .blend normalization PASS, UE4.27 skeletal technical gate PASS, deformation stress FAIL with five broken Rigify limb/spine chains. Inspect actual normalized FBX: deform 87 weighted bones, 2229 vertices (1787 weighted), 443 source rig bones / UE4 reference 161, source Rigify ORG/MCH parents disconnected from the selected DEF chains. Rejected sibling source .fbx remains quarantined.
- Root-cause repair preparation: export a SEPARATE lightweight game-only deform armature with direct weighted DEF family chains (including .01/.02 forearm/shin segments), preserve source bones' exact rest matrices, original per-vertex skin weights and mesh transforms; reject cycles, missing joint influence, non-finite bounds, changed vertex count and rest-pose displacement >1% of source bounds diagonal. Output only source candidate; do not attach speculative animation clips. FBX reimport hierarchy check runs on REAL exported file, before UE4. Strict downstream UE4 and hosted pose deformation remain unchanged.
- Locally validated pure hierarchy logic with six unit tests using both generic and actual Rigify .01/.02 segment naming: PASS; Blender 4.0 render/source FBX/real posed deformation NOT RUN locally because Blender is unavailable in this execution container. No new source/UE/Warehouse/runtime/visual accepted asset yet.
- M0 dependency: original source CC0 archived with exact receipt in prior hosted artifact, Blender hosted tool installation, UE4.27 importer and unchanged physics capsule, governor one writer; no new restricted models. Rollback one cohesive batch on failed host or UE import, prevent repeated heavy retry on identical failing input. PES-002 remains OPEN, PES-003 LOCKED. User acceptance + real Bag End PIE/traversal + target DX11 720p >=30FPS remain NOT RUN.

## PES-002 2026-10-15 source repair stage matrix — baseline 8058f6a, new candidate exact-head pending

| Deliverable | Existing prior evidence | This source candidate | Accepted |
| --- | --- | --- | --- |
| Bag End mesh source/UV/material identity | 7 drawn finishes, 2,704 tris, Unreal 38765635848 PASS on old mesh | New joined wall/turf/aprons, 2,780 tris, 7 finishes; deterministic/local 3 tests PASS | NO — new import/render pending |
| Bag End UE package and world presence | Actual existing package, section bindings, runtime marker and 4 views at 8058f6a | NO new UE import or visual claim from local geometry work | NO |
| Genuine images | Artifact 11989868346, all four 1280x720, visually REJECTED for shell/seam/terrain | Source-only preview, NOT a new Unreal render | NO |
| Collision/NavMesh/traversal/PIE | Not proven at 8058f6a | Unchanged existing runtime anchors; no collision modification | NOT RUN |
| DX11 720p target 8GB/~2GB FPS>=30 | Not measured | No new profiling claim; one source static asset, no extra runtime actors/texture | NOT RUN |
| Frodo rig/animation | Run 38765635822 UE skeletal gate PASS, deformation hierarchy FAIL | Original skinned .blend preserved, no retest of rejected FBX | NO |
| New source geometry regression | Old generator had independent wall strips and open roof edges | 33 shared crown vertices, 32 shared roof/wall edges, side apron underlay, exact output reproducibility; 3 local tests PASS | SOURCE-VALIDATED ONLY |

PR #477 is still the one active PES runtime PR. Pre-Unreal new-HEAD / Windows new-HEAD Run IDs are NOT RUN before push. Do not open PES-003 or claim visual/PIE/device closure.

2026-10-15 PES-002 exact-head 51c2ed1: Pre-Unreal Run 38762271198 PASS; UE4.27.2 C++ compilation PASS in Run 38762271397, importer FAILED `PES002_HERO_MATERIALS_REJECT slots=8 required=7`; no startup/new images credited. Source has 7 authored finishes; reimport backing array contains 8 entries. Do not assume an eighth rendered section or blindly delete a historical slot. Bounded repair validates every nonempty actual LOD0 section against the 7 required named, resolved materials, requires all seven finishes to be drawn, and logs names/triangle counts/material paths; any obsolete/unrecognized DRAWN finish remains a failure. Preserves source geometry, captures, binding requirements and acceptance gates. Fresh engine import/render still required. Epic UE-60152 documents historical unused-slot retention (4.19.2, Cannot Reproduce; precedent only, not proof about this UE4.27 asset). Current asset's actual unused-slot disposition will be proven by section logs. PES-002 OPEN, PES-003 locked.

2026-10-15 continuation at c92e940: preserve newer source binding fixes. Frodo locomotion Run 38755223105 PASS; Wave2 source and UE skeletal gate PASS but deformation Run 38755222797 FAIL (hierarchy sanity, both arms/legs/spine-head). Unreal Run 38755222958 compile/import/startup PASS, capture FAIL after 13 seconds: stale prior log view=3 can satisfy polling before new process initializes, then the new log has no camera marker. Clear proof log/old delivered PNGs before launch, retain 240s readiness, four fresh screenshots and luminance tests; no threshold waived. Joined exterior candidate rebased onto this exact newer head; engine/render validation pending.

## 2026-10-15 PES-002 M0-M3 joined Bag End exterior candidate

- Baseline: develop `03df3c34a7a5faa47a69bf882edc0a7afd01000e`; PR #477 head `d5f37b5e61722c4828170a729c5ae0f37aab1f58`. Unreal Run 38727751427 / artifact 11969310933 (archive SHA256 `5b5d9c410f2ad4358d39ab7be4ffb5e7172ea1a8a3e57ce622029817ee004978`) genuinely captured four 1280x720 views. Machine capture PASS; assistant inspection rejects floating door/windows, detached green mound and modular characters. This is not owner acceptance. Luminance: 66.36 / 61.49 / 86.68 / 69.13, all >=35 but not an artistic pass.
- Root cause: runtime explicitly suppressed `ProductionBagEndHeroFacadeMesh`; separate hero discs plus unconditional fallback glass duplicated windows. Contrary to the previous material-intake assumption, the actual baseline importer logged exact package `resolved=yes`, three material packages marked. The old asset contained Earth/Stone/Wood but no authored door/glass finish. Fix the missing geometry/material contract, not lighting or cameras.
- Candidate: extend the existing original facade source with an earth-covered roof joined to its front elevation, fitted green door planks, central brass knob and recessed paired glazing/mullions. Seven named material sections, authored planar UVs, explicit triangles, 2704 triangles, no new texture or external source license. Use the already async-resident exact asset and suppress duplicate primitives only for Bag End. Keep story anchors, proof camera positions, player/step collision, directors and streaming ownership. No new collision on this decorative asset; traversal remains unproven.
- Importer now rejects missing or unresolved required material slots instead of accepting package existence alone. Source regression checks geometry/UV indices/nonzero triangles, bounded triangle cost, deterministic regeneration and runtime path. Local 8 focused regressions, strict source asset audit and pre-Unreal structure validation PASS. New UE build/import/capture NOT RUN at authoring; do not reuse old build as validation of this changed code.
- Character source runs 38727751418 and 38727751421 FAILED `HUMAN_WAVE2_SKIN_REPAIR_BOUND_CHARACTER_TOO_SMALL` before FBX; unchanged, no retry or rig promotion in this architectural batch. Saved geographic .umap, traversal/PIE, target-device FPS/VRAM, final materials/foliage and owner visual review still pending. PES-002 OPEN; PES-003 LOCKED.

2026-10-15 PES-002 EXACT-HEAD ROOT CAUSE OF SCREENSHOT GATE FAILURE: UE4.27 Windows Run 38641340304 on faaee053 compiled ShireJourneyEditor, imported 377 files with zero import failures, finished project automation and startup smoke; only `Capture Bag End targeted P1C01 visual proof` FAILED with `PES002_CAPTURE_CAMERA_NOT_CONFIRMED`. Downloaded actual artifact 11930976349; `PES002VisualEditor.log` ended during fresh RHI/shader DDC init around 21:38:06 without Bag End camera markers, while fixed 86-second script killed the process at 21:39:27. Four existing PNGs in artifact have older 21:23/21:24 timestamps and must NOT count as faaee053 visual proof. Repair: replace wall-clock fixed kill with fail-closed polling for 4th screenshot request, bounded startup timeout 240 seconds, early-exit failure, 12-second file-settle, and keep existing fresh-stamp PNG + 720p + weighted RGB luminance requirements. Actual exact-head Unreal screenshot after changed timing is NOT RUN, no visual/PIE/device acceptance, PES-002 OPEN.

2026-10-15 PES-002 root cause confirmed at 01fbb1c1: Wave 2 first CC0 .blend source PASS (2229 bound vertices, 87 weighted deform bones, zero-weight ratio ~0.198); sibling .fbx source has 0 weighted body/hair vertices and fails mandatory source skinning. Correct production selection to prefer original .blend source exclusively when available, preserving max-two policy, full source inventory, all quality and UE deformation gates; do not force a known invalid alternate through normalization. Windows UE4 build and four-view capture run 38742152742 PASS. New exact-head source/UE checks required before acceptance.\n\n2026-10-15 PES-002 cohesive source repair: exact-head 364a4070 Blender logs confirm body hero_mesh 1661 vertices and hair 544 vertices already have deform weights but lost Armature modifiers; only 24 prop vertices were armature-bound. Repair adds modifier back to weighted >=100-vertex body/hair only, retaining original skeleton, original weights, minimum 1000 vertices, downstream limb/deformation gates. Same HEAD Windows Unreal C++ built but four-view capture failed PES002_CAPTURE_CAMERA_NOT_CONFIRMED after process exited before screenshot markers; watcher now checks last-request marker before treating process exit as failure, avoiding lost final-frame race. These are source candidates, NOT visual/animation acceptance; exact-head CI pending.\n\n2026-10-15 PES-002: exact-head d5f37b5e Windows UE4 Build PASS run 38727751427, but hosted Frodo and Human Wave 2 source-normalization FAILED runs 38727751418 / 38727751421 at HUMAN_WAVE2_SKIN_REPAIR_BOUND_CHARACTER_TOO_SMALL. Source code requires >=1000 armature-bound vertices; root cause (small source vs missing bindings) not yet proven. Added fail-closed Blender source diagnostics to print each mesh vertex count, armature modifier target, parent, weighted vertices, aggregate bound vs scene vertices. Threshold and downstream deform/limb gates UNCHANGED. Await exact-head source workflow logs before any mesh repair or PES closure.\n\n2026-10-15 PES-002 EXACT-HEAD ROOT CAUSE OF SCREENSHOT GATE FAILURE: UE4.27 Windows Run 38641340304 on faaee053 compiled ShireJourneyEditor, imported 377 files with zero import failures, finished project automation and startup smoke; only `Capture Bag End targeted P1C01 visual proof` FAILED with `PES002_CAPTURE_CAMERA_NOT_CONFIRMED`. Downloaded actual artifact 11930976349; `PES002VisualEditor.log` ended during fresh RHI/shader DDC init around 21:38:06 without Bag End camera markers, while fixed 86-second script killed the process at 21:39:27. Four existing PNGs in artifact have older 21:23/21:24 timestamps and must NOT count as faaee053 visual proof. Repair: replace wall-clock fixed kill with fail-closed polling for 4th screenshot request, bounded startup timeout 240 seconds, early-exit failure, 12-second file-settle, and keep existing fresh-stamp PNG + 720p + weighted RGB luminance requirements. Actual exact-head Unreal screenshot after changed timing is NOT RUN, no visual/PIE/device acceptance, PES-002 OPEN.

2026-10-15 PES-002 4-VIEW UNREAL ROOT-CAUSE FAÇADE REPAIR CANDIDATE: Verified exact-head 8aef99bb run 38639403183 actual UE4.27 C++ job PASS, four 1280x720 proof PNG artifact 11928994016, SHA256 per-view recorded in logs. Center luminance 57.34/55.77/79.58/62.07 passes >=35 brightness screen but HUMAN VISUAL STILL REJECTED for oversized Bag End mound, protruding green cylinder, bulky fences and NPC placeholders. This candidate only trims Bag End mound scale 3.40x3.20x2.80 to 2.92x2.85x2.34 and pulls decorative green thin door disc 10 cm toward facade while retaining west elevation, Bag End anchor and all existing collision/story triggers. No other homes altered, no cosmetic geometry collision. MUST visually inspect new 4-view exact-head screenshot and do traversal/collision and 8GB/2GB device FPS before any ACCEPTED state; no PES-003.

2026-10-15 PES-002 ONE-COHESIVE VISUAL GATE FIX (PR #477): Evidence from exact head f7ae873: Pre-Unreal 38638641156 SUCCESS, Unreal Build 38638641056 shows hosted classifier SUCCESS but Windows C++ job SKIPPED (not a fresh Unreal build), Frodo hosted runs 38638641193/38638641386 FAILED. Core scene remains VISUAL REJECTED by human prior views. Candidate expands opt-in actual UE 720p Bag End capture to FOUR stable positions, validates each fresh PNG and central-frame RGB weighted brightness >=35 (screening guard only, not artistic acceptance). Old 3-view static regression updated. NO Photoshop/synthetic images. Actual resulting Unreal screenshot, true engine compile, movement/collision, target device FPS and five character rig gates remain PENDING. This is NOT session closure, PES-003 locked. C++ changes require exact-head UE4 writer and owner visual proof before acceptance.

2026-10-15 PES-002 ACCELERATION M0 INDEX AND GOVERNOR REGISTRATION CANDIDATE: Owner requested non-CC0 personal-use legal-source prioritization, protected private warehouse/public metadata receipts, five key character source imports, one-PES PR, data-driven decoration, four-angle luminance proof, short M0 context and region sublevels. This batch establishes short index, decision reference and static governance guard; it does NOT import characters, move gameplay coordinate arrays, create sublevels or generate Unreal screenshots. All prior historical documents retained in place. Current active PES-002, PR #477; exact-head tests after commit pending; no PIE/device/visual acceptance.

2026-10-14 PES-002 M0→M1 FRODO SOURCE SKIN ROOT-CAUSE REPAIR CANDIDATE (PR #477): Inspected actual exact-head 166656aed hosted jobs 116088670093/116088671807 (Runs 38632883899/38632883791): two source normalizations exported a skinned-looking FBX with only four weighted bones and zero head/bilateral limb-role influence; both correctly FAILED before UE4, Blender 4.0.2. A materially changed SOURCE REPAIR now conditionally rebinds the existing CC0 source primary skinned humanoid mesh to its original armature using Blender ARMATURE_AUTO bone-heat only when source deform-weight coverage is deficient. It rejects absent/multiple armatures, tiny/unbound body mesh, bone-heat failure, missing Armature binding, insufficient deform groups and still requires the existing post-EXPORT 13-role influence gate, UV, weights and finite bounds; no threshold reduction, no dummy rig, no UE runtime promotion. Added embedded Blender Python syntax regression and re-trigger Frodo locomotion on shared normalizer/manifest changes. This is an untested changed processing candidate pending exact-head hosted Blender reimport + deformation stress; source may remain REJECTED if bone heat or role coverage fails. Existing Bag End scene VISUAL REJECTED, UE4/PIE/device/traversal and 30FPS NOT PROVEN; PES-002 OPEN, PES-003 LOCKED. Method reference: Blender Rigify/auto weights and Epic UE4.27 skeletal import; an actual character silhouette, costume and visual deformation review remain mandatory.

2026-10-14 PES-002 CAMERA-EVIDENCE ROOT-CAUSE HERO FACADE CORRECTION: Inspected three actual UE4.27.2 1280x720 PNGs from Run 38563272174 artifact 11892194952, SHA256 view0 3128205E4EB4A7864C3BEE5CCFB9B65FA6AB26B1664BC3B8916763ACA80E0F28 / view1 1D58E33689BB179E890AFE2082F51D6A37717995D909DDF09DC92B59D7382FDE / view2 2BF76E5A5A040A19388771134F5EB0B87B3EBAF671C6585181C9DD51287ECAB9. Real images show restored textures/color but oversized green mound hides facade, plus dense foreground proxy fences/NPCs; no visual acceptance. Focused C++ candidate shifts only Bag End's earth mound +260cm behind its west-facing facade, reduces mass, gives hero turf nonblocking collision, retains existing blocking facade/story anchors, and adds a recognizable low-cost green round door silhouette and static source regression. This is a candidate pending exact-head build, new visual images and real traversal/collision evidence; physical authored facade mesh/material and target-device 30 FPS still not accepted. No PES-003.

2026-10-14 PES-002 VISUAL REAL-RUNTIME DEFECT REPAIR WAVE: Exact-head PR #477 Run 38561717050 proved UE4.27 C++ build, 90 Cloud138 restored .uasset packages, three Automation tests, headless startup, runtime 1280x720 BagEnd-directed screenshot SHA256 EC7F6789E8B2F96F88BC0FFD417D857D787EE28F93D92C9640703F332AA98936 and 12/12 grounded Bag End Cloud138 props. Human examination of actual image REJECTED visual: rough grey buildings, low-detail NPCs, heavily occluded hero facade. The screenshot log directly identified M_ProductionFoliage shader default fallback due SimpleGrassWind required AdditionalWPO missing, and both M_ProductionSurface/M_ProductionFoliage bUsedWithInstancedStaticMeshes missing. Repair candidate modifies existing UE editor import material masters (including persisted assets) to add mandatory AdditionalWPO zero input, enable instanced material usage, save changed master .uasset; captures three Bag End angles to avoid accepting a misleading occlusion. This repair must be recompiled and inspected on a NEW Windows run; no visual/traversal/PIE/device acceptance claim and PES-002 remains OPEN.

2026-10-14 PES-002 ROOT-CAUSE CI RETEST candidate: PR #477 exact-head af9e827 failed Pre-Unreal Run 38561472948 at PG-172 because three SkyLight RecaptureSky() calls violated the existing precisely two-call invariant. Root-cause change moves startup recapture exclusively to the deferred one-shot post-sky-init timer, retains the authored quest/story recapture, removes immediate duplicate and adds exact count regression to the focused PES contract test. No gate bypass; retest required. UE Build Run 38561473150 was still in progress at diagnosis. PES-002 OPEN.

2026-10-14 PES-002 ROOT-CAUSE AND CAMERA/LIGHTING CORRECTION CANDIDATE (DEC-PES-ROOT-20261014): Source audit of develop@03df3c3 found prior HighResShot used the ordinary player view without aiming at Bag End; the received 1280x720 Unreal image shows dark/unpolished architecture and no accepted Bag End facade. This wave adds opt-in proof-only Bag End camera/framing after runtime world initialization, delayed capture and strict PNG/log/dimension checks; raises baseline sun/skylight/exposure and adds deferred sky recapture to address premature dim sky illumination. The camera is gated by -PES002VisualProof outside shipping and never moves the gameplay player or changes quest, nav, NPC or save ownership. Exact-head hosted static, real UE4.27.2 C++ build and a NEW screenshot/traversal proof must still pass. No physical new FBX/PNG/material import, no visual/PIE/device/traversal acceptance, and no Gate 6/7 closure are claimed. Active PES-002 remains OPEN; do not open PES-003.

2026-10-14 PES-002 VISUAL EVIDENCE PIPELINE candidate: Added Scripts/capture_pes002_bag_end_visual.ps1 to launch real UE4Editor -game windowed 1280x720 and request HighResShot, fail if screenshot missing or only BMP. Connected optional fail-safe attempt and log/image Actions artifact to focused Windows Unreal workflow. This does NOT assert rendered success, PIE, traveler camera alignment, visual acceptance or traversal; screenshot review and actual evidence pending. Workflow capture is continue-on-error to avoid blocking validated C++ on headless display failure; screenshot absence stays PES-002 OPEN.

2026-10-14 PES-002 Bag End Exterior follow-up: source-backed bounded HISM terrain-edge dressing using existing resident ProductionTurfMoundMesh and ProductionRockMesh: 6 garden slope pieces and 6 outer property stones, intentionally offset from the walkable door/road corridor, zero collision and no new draw-component per prop. Added runtime marker PES002_BAG_END_TERRAIN_EDGE (actual instances to be verified in UE). Existing facade uses ProductionHobbitFacadeMesh when resident; no new imported architecture or packed material claim. PIE/screenshot/traversal and Gate 6/7 still pending; PES-002 OPEN.

2026-10-14 PES-002 integrated exterior candidate: reused existing resident `ProductionFlowerBoxMesh` via bounded no-collision/no-tick AWorldDetailCluster HISM, eight new porch/approach positions outside primary roadway, with `PES002_BAG_END_PORCH_FLOWERS` runtime receipt; no synchronous heavy loads, no new NPC spawns, no unsafe bridge collision. Other previously merged Bag End garden Cloud138 dressing remains present. This is a tangible exterior landscaping addition, not proof of imported new architecture/packed PBR or accepted screenshot/traversal. Exact-head UE4 compile/startup and actual visual/traversal evidence outstanding; PES-002 OPEN, Gate 6/7 OPEN.

2026-10-14 PES ONE COMPLETE BATCH CONTRACT: Before each PES begins, inspect current develop HEAD, ProjectGovernor, gates, source/warehouse/Unreal receipts and chapter canon; enumerate the full named session deliverable and its exact assets, C++ changes, placement, focused tests and synchronized documents. Prepare one cohesive complete change wave and one PR whenever technically possible, not a parade of partial micro-PRs requiring owner 'continue'. After hosted source/static and necessary Unreal compile/import/startup run, repair verified failures in bounded corrective commits and retest; deliver a single evidence-based session report. Keep one Unreal writer/one Warehouse writer and no broad audits/package until chapter closeout. If missing actual screenshot/traversal/PIE/device evidence, remain OPEN and report blocker, not fake completeness. No automatic ongoing background work promise beyond a live execution.

2026-10-14 PES-002 BAG END EXTERIOR actual C++ candidate: updated the existing async Cloud138 HISM GardenPlanter and WindowFlowerBox anchor arrays to concentrate 12 capped non-colliding instances around previously established Bag End garden coordinates; preserve all 8 Cloud138 families, maximum 48 placements, soft reference async streaming, terrain tracing and steep-ground rejects. Added `PES002_BAG_END_EXTERIOR_GARDEN_DRESSING grounded=<n> requested=12 groups=2 collision=none async=1 visual=pending` marker for exact-head UE4 test evidence. This is garden dressing only, NOT exterior architecture/terrain/PBR completion; COMPILE-TESTED pending Windows CI, rendered screenshot and traversability pending. Existing WoodenFootbridge remains NAV_QUARANTINED.

2026-10-14 PRE-UNREAL FOCUSED PES CHANGE (PR candidate): default pre-unreal hosted checks retain exact-head source checkout, classifier regression, Windows packaging safety contract, PowerShell syntax, project structural validation, Project Governor, source-to-Unreal PBR integrity, Governor work-start and semantics, strict asset quality audit. 35 broader cross-chapter, historical provider/hero, warehouse regression, deep audit and reporting test steps are deferred to explicit workflow_dispatch chapter_closeout_audits=true, without disabling GitHub Unreal focused compile/import/startup or Gate 6/7. This is CI scheduling only, not a claim of FPS/visual acceptance.

2026-10-14 VERIFIED SESSION TRANSITION (owner authorized): PES-001 Asset Recovery & Import = COMPLETE for its bounded import-and-placement deliverable only, supported by Windows Run 38526869417 on develop@e1acb85a5f972f521de2f5888a52561d77bf6877: UE4.27.2 ShireJourneyEditor build SUCCESS; CLOUD138_UE_RESTORED_SHA256_PASS files=90 bytes=19394460; AUTOMATION_SUITE_PASS tests=3; P1C01 headless startup PASS cloud138 families=8 grounded=48 cap=48. PES-001 PIE=false, device=false, visual_accepted=false, chapter Gate 6/7 remains OPEN; no FPS or human render claim. Owner explicitly defers human visual review to PES-002. PES-002 Bag End Exterior = ACTIVE, NOT COMPLETE: architecture/garden/terrain/packed-PBR and actual screenshot/traversal are its required deliverable, not demonstrated yet. Existing SM_ShWoodenFootbridge remains NAV_QUARANTINED; no unsupported traversal claims.

2026-10-14 PES FOCUSED WINDOWS EXECUTION: fix previous manual Run 38525471144 incorrectly classified `static` and skipped Unreal. New explicitly owner-authorized workflow_dispatch input `pes_focused_unreal=true` with `run_self_hosted=true` forces classifier `core` (UE4 editor compile, importer, persisted Cloud138 restore, automation and P1C01 headless startup) while `package_windows=false`, `part1_closeout_approved=false` keeps Cook/Package and broad all-chapter audits off. Runtime evidence is not a visual screenshot/PIE claim. Current PES-001 OPEN until specific evidence proves its closure.

2026-10-14 OWNER CI THROUGHPUT POLICY (implementation candidate; PES-001 OPEN): ordinary PES runs retain mandatory exact-head hosted/static guards, required changed-C++ UE build, asset import/reopen and focused startup only. Deferred until explicitly owner-approved Part I/chapter closeout: full chapter runtime sweep, full route/story roundtrip, global warning debt and Windows Cook/Stage/Package. Workflow now requires BOTH package_windows=true and part1_closeout_approved=true; accidental package_windows alone cannot activate these expensive stages. Does not delete Gate 6/7, PIE, device, visuals or project acceptance obligations. No new asset/PIE/device claim.

2026-10-14 PES-001 ACTIVE IMPLEMENTATION CANDIDATE: 8 exact previously imported Cloud138 non-walkable FBX families are soft-streamed into the existing P1C01 ShirePrototypeWorldBuilder as 8 capped non-colliding HISM components (48 maximum instances, ground/steep-rejected); existing D: SHA256 persistent 90-uasset receipt is restored before headless runtime startup and required log marker P1C01_CLOUD138_WORLD_READY is audited. SM_ShWoodenFootbridge remains NAV_QUARANTINED and entirely excluded; no walking-surface collision acceptance is implied. Commit/source integration is not proof of successful engine build, persisted editor reopen on this HEAD, actual grounded instances, rendered image, PIE, device, Gate 6/7, or visual acceptance. PES-001 remains OPEN until evidence.

2026-10-14 PES performance policy CANDIDATE: owner requested removal of recurring full chapter/story/state/warning sweeps until chapter closeout. CI conditions now defer exactly those 3 expensive runtime audit steps to manual owner workflow_dispatch package_windows=true. Preserve quick development compile/startup, dedicated importer/reopen/persist evidence and all Gate 6/7 acceptance. Policy change does not establish imported-world placement, PIE, device or visual evidence. Verify PR exact-head hosted tests before merging.

2026-10-14 PES-001 quarantine candidate: last exact-head Windows Run 38475386875 found only SM_ShWoodenFootbridge missing imported simple UCX collision. To avoid a false box proxy or failing persistence of otherwise eligible assets, allow only this exact path as NAV_QUARANTINED in both editor and fresh reopen receipts; do not grant it world-placement or nav approval. Abort batch for ANY other critical missing collision; keep PIE/visual/device and Gate 6/7 unchanged. A successful import/persist receipt is NOT visual chapter completion. Physical tests on this proposed candidate are pending.

PES-001 intake report: recovered source warehouse 138 FBX and 36 PNG; UE collision import failures RoundDoor, StonePath, and WoodenFootbridge, fail-closed until UE import/reopen/persist and world-placement proof. 2026-10-14 PES-001 latest Windows Run 38471186190: source receipt and warehouse stage passed, editor followup failed for WoodenFootbridge missing imported UCX collision. Bounded recovery now audits all critical missing-collision meshes before returning a batch failure, rather than requiring repeated multi-minute Windows runs for each next offender. Open bridge is NOT given inaccurate BOX collision. No restored/imported persisted Unreal uasset count or placed-world count may be promoted until fresh editor reopen and durable receipt plus world verification. This fix itself is diagnostic and source-level only.

2026-10-14 PES-001 candidate follow-up: Cloud138 Windows import Run 38467646349 passed source stage and warehouse writer but failed editor mode on SM_ShStonePath with CLOUD138_WALKABLE_UCX_NOT_IMPORTED. Candidate now permits bounded BOX collision fallback for this known flat walkable source along with FerryLanding and closed RoundDoor, while preserving the guard against applying it to open WoodenFootbridge and foliage. This is only an import-proxy repair; traversal, world placement, PIE/device/visual and persistent UE package acceptance remain unproven. Exact-head revalidation required.

## 2026-10-13 - P1C01 off-runner material source Batch 01\n\n| Area | Status | Evidence |\n|---|---|---|\n| Generated source material sets | CI CANDIDATE | 24 procedural Shire PBR material records generated by `Scripts/generate_p1c01_material_source_batch01.py`; per-map SHA256 and PBR contract in generated manifest |\n| Generated textures | CI CANDIDATE | 72 PNG members: BaseColor, packed ORM and Normal maps for each material set |\n| Surface coverage | CI CANDIDATE | Bag End, Bag End Interior/Garden, Hobbiton, Bagshot Row, Party Field, roads, Wooded Road, Mill Pond, Bucklebury Ferry, East Fields and Hobbiton Market |\n| Windows Runner | NOT USED | Batch created and validated off-runner; classifier routes this path to hosted static mode |\n| Warehouse / Unreal import / MaterialInstance setup | PENDING | No Content Browser import, material instance creation or warehouse persistence claimed |\n| Runtime/world binding | PENDING | No level, Blueprint, subsystem or world placement binding claimed for this batch yet |\n| PIE / device / visual / performance / Gate 6-7 | NOT ACCEPTED | Requires UE4 import, material binding, visual review and target-device evidence |\n\n## 2026-10-13 - P1C01 off-runner source audio Batch 01\n\n| Area | Status | Evidence |\n|---|---|---|\n| Generated source audio | CI CANDIDATE | 32 mono 16-bit PCM WAV members generated by `Scripts/generate_p1c01_audio_source_batch01.py`; per-member SHA256, frames and duration in generated manifest |\n| Audio coverage | CI CANDIDATE | Ambience, foley, footsteps, object sounds and nature cues across Bag End, Hobbiton, Party Field, roads, woods, Mill Pond, Ferry and East Fields |\n| Windows Runner | NOT USED | Batch created and validated off-runner; classifier routes this path to hosted static mode |\n| Unreal import / SoundCue setup | PENDING | No Content Browser audio import or SoundCue asset claimed |\n| Runtime/world binding | PENDING | No level, Blueprint, subsystem or world placement binding claimed for this batch yet |\n| PIE / device / audio acceptance / performance / Gate 6-7 | NOT ACCEPTED | Requires UE4 import, runtime binding, listening review and target-device evidence |\n\n## 2026-10-13 - P1C01 off-runner source asset Batch 03

| Area | Status | Evidence |
|---|---|---|
| Generated source meshes | CI CANDIDATE | 48 FBX members generated by `Scripts/generate_p1c01_source_asset_batch03.py` into a workflow artifact ZIP; per-member SHA256 in generated manifest |
| Generated textures | CI CANDIDATE | 16 PNG base-color members in the same source archive; 64x64 RGBA validation and SHA256 receipt |
| Windows Runner | NOT USED | Batch created and validated off-runner; classifier routes this path to hosted static mode |
| Unreal import / `.uasset` persistence | PENDING | No Content Browser import or `.uasset` persistence claimed |
| World placement | PENDING | No saved level/World Builder placement claimed for this batch yet |
| PIE / device / visual / performance / Gate 6-7 | NOT ACCEPTED | Requires UE4 import, runtime placement, visual review and target-device evidence |

## 2026-10-13 - P1C01 off-runner source asset Batch 02

| Area | Status | Evidence |
|---|---|---|
| Generated source meshes | STATIC-VALIDATED locally / CI pending | 48 FBX members emitted by `Scripts/generate_p1c01_source_asset_batch02.py` into the workflow artifact ZIP; per-member SHA256 in the generated manifest |
| Generated textures | STATIC-VALIDATED locally / CI pending | 16 PNG base-color members in the same source archive; 64x64 RGBA validation and SHA256 receipt |
| Windows Runner | NOT USED | Batch created and validated off-runner; classifier routes this path to hosted static mode |
| Unreal import / `.uasset` persistence | PENDING | No Content Browser import or `.uasset` persistence claimed |
| World placement | PENDING | No saved level/World Builder placement claimed for this batch yet |
| PIE / device / visual / performance / Gate 6-7 | NOT ACCEPTED | Requires UE4 import, runtime placement, visual review and target-device evidence |

## 2026-10-12 - P1C01 off-runner source asset Batch 01

| Area | Status | Evidence |
|---|---|---|
| Generated source meshes | STATIC-VALIDATED locally / CI pending | 36 FBX members inside `SourceAssets/Production/World/Shire/Batch01OffRunner/P1C01_Batch01_SourceAssets.zip`; per-member SHA256 in `Data/P1C01SourceAssetBatch01Manifest.json` |
| Generated textures | STATIC-VALIDATED locally / CI pending | 9 PNG base-color members in the same source archive; 64x64 RGBA validation and SHA256 receipt |
| Windows Runner | NOT USED | Batch created and validated off-runner; classifier routes this path to hosted static mode |
| Unreal import / `.uasset` persistence | PENDING | No Content Browser import or `.uasset` persistence claimed |
| World placement | PENDING | No saved level/World Builder placement claimed for this batch yet |
| PIE / device / visual / performance / Gate 6-7 | NOT ACCEPTED | Requires UE4 import, runtime placement, visual review and target-device evidence |

2026-10-12 Cloud138 Windows warehouse runner blocker and recovery: develop PR #430 merged 9842ca5 with hosted static+Unreal exact-head validations green; first persistent transfer run 38294982859 failed before staging at Verify governor and persistent root because `pwsh: command not found` on self-hosted Windows machine. Fix candidate uses the installed Windows PowerShell (`shell: powershell`) on both Windows-only steps, preserving exact pinned artifact, SHA/CRC/UCX/LOD/provenance checks, one writer and source-only evidence boundary. Until repair run emits CLOUD_WHOLEGAME_PERSISTENT_WAREHOUSE_PASS and a persisted receipt, transferred file count for cloud138 remains 0 PROVEN. UE4 current-run evidence does not certify cloud138 import, PIE, device or visuals.

2026-10-12 P1C01 / 28-region 138-FBX physical warehouse transfer candidate: Existing verified source Artifact 11767251532 from Run 38292163970, head 1e1e5c9, has 82 Shire FBX, 56 whole-game regional FBX and 36 existing packed PNG. New pinned single-writer Windows transfer workflow downloads the precise GitHub artifact, compares wrapper and inner SHA256, inspects 174 physical payloads and 3 source receipts, enforces FBX 7400/UCX/UV/LOD, region identity and PNG signatures, rejects unsafe ZIP membership, enforces reserve, writes atomically and rehashes persisted D: storage. Transfer is source-only: does NOT import .uasset into UE4, run PIE, profile target FPS, visually approve, or close P1C01 Gate6/7. This is source code CANDIDATE until hosted tests and actual Windows persistent receipt pass. No new physical FBX generated in this integration step.

2026-10-12 DEC-109 / whole-game source candidate: Prior cloud Shire PR #428 produced 82 physically verified FBX, 28 more than prior 54. This candidate authors 28 original region support families x two LODs = 56 new FBX targeting +100% net-new throughput over the prior +28. Separate regional_meshes/ receipt, Blender reimport, UV, UCX and physical SHA256 integrity are mandatory. 36 existing packed PNGs reused without being counted as new. Preparation spans exactly the 28 canonical world packets, not final chapter runtime or hero landmarks; P1C02+ runtime remains gated. Source work and DEC-109 are candidates until exact-head checks pass. No new Warehouse persistence, UE import, PIE, device/FPS or visual approval.\n\n## 2026-10-12 - 82 Shire original FBX production candidate

Expands source candidate from hosted-proven 54 FBX / 27 Shire families (Run 38288336015) to 41 families / 82 FBX (14 new families, 28 additional LOD files; 51.85% target increase in comparable source count). New original procedural static props: FerryQueueBench, ReedPlanter, OrchardCrate, MarketStall, MarketBasket, HerbDryingRack, RusticSign, GrainSackStack, WindowFlowerBox, GateLantern, BridgeRailing, GardenTrellis, FarmToolRack, PartyServingCounter. Blender binary 7400, reimport UV/UCX, SHA receipts and 28-region material assets remain gated by exact-head GitHub Actions. This is NOT proof of actual 82 physical FBX yet. No automatic Warehouse/UE world residency, PIE, device FPS or visual acceptance claim. Preserve single Warehouse/UE runtime writers and Gate6/7.


## 2026-10-12 - DEC-108: accountable per-session growth and independent engineer judgement

- Owner is an enjoyment-first player; independent Lead Architect makes and explains professional engineering choices (including polite disagreement), while owner retains product vision.
- Each session reports exact baseline and new total, absolute change, comparable percentage, evidence/commit/PR/Actions, principal risk and recommended next high-player-value action. A +50% gain is a stretch target **only** for eligible, verified like-for-like production; missing baseline => N/A, no invented percentages.
- Keep physical source-generated FBX/PNG/TGA, **unique persisted** warehouse, **persistent UE .uasset imported**, **actual world-placed**, and playable/PIE/device/visual evidence as separate funnels. Do not infer one from another or count duplicated ZIP source contents twice.
- Prepare all 28 regions and P1C01-P1C08 through up to five safe parallel source lanes and one persistent warehouse writer, while one runtime writer remains on P1C01 until Gate6/7; future chapter preproduction is not runtime activation.
- Baseline for the Cloud Shire source wave: PR #426 commit 407b35b, merged b309d149; hosted run 38288336015 generated and Blender-reimport-validated 54 binary FBX (27 families x 2 LOD), 36 PNG and an Actions artifact 11764013609 (9,841,895 wrapper bytes). 44 was the *previous authored target*, not proof of a previous comparable physically generated run. No warehouse/UE world/PIE/device/visual promotion from this receipt.
- This policy-only change adds no game asset, importer, UE runtime or new CI workflow. Existing daily report remains; new **per-session** report is additional. Exact-head static CI is required before merging this candidate.

**2026-10-12 P1C01 route/party/ferry closure pass (STATIC source candidate):** Added a second bounded visible-world layer in `ShirePrototypeWorldBuilder` using existing production meshes only: Party Field lantern boundary and outer seating, readable road-to-ferry path markers, ferry queue rope posts, ferry-bank reed breakup and eight non-blocking hero props around the party/route/ferry handoff. Evidence status remains STATIC candidate until exact-head Pre-Unreal and Windows UE4 compile/runtime logs prove it; no PIE, DEVICE, VISUAL, FPS or Gate 6/7 completion is claimed.

**2026-10-12 P1C01 chapter-finish world art pass (STATIC source candidate):** Added a final bounded world-art layer in `ShirePrototypeWorldBuilder` using existing production meshes only: Bag End garden hedges, Hobbiton yard flower boxes, worked-field fence rhythm, wooded-road understory, ferry reeds and ten non-blocking hero props. Evidence status remains STATIC candidate until exact-head Pre-Unreal and Windows UE4 compile/runtime logs prove it; no PIE, DEVICE, VISUAL or Gate 6/7 completion is claimed.

**2026-10-12 P1C01 imported-tree runtime visibility evidence candidate (STATIC source preflight only; Windows exact-head pending):** Existing nine-family async HISM callback logs real per-family asset path, actually grounded instance count, missing/steep rejected traces and mesh material slot count. No new loading, instancing, authoring, NPC, quest or chapter authority, no extra workflow or per-Tick overhead. This closes an evidence blind spot, not the visual gate: real Unreal logs must prove loaded assets/placement; screenshots and human review still required. Existing regression updated; P1C01 Gate 6/7 remains open.

**2026-10-12 game-wide owner-visible production pivot (policy candidate):** Adopt DEC-107 in Data/ProjectGovernor.json: prioritize imported rendered scenery, skeletal locomotion, playable quest/audio/save routes over speculative new CI/docs; up to five independent future-chapter asset/source prep lanes run concurrently while one Warehouse writer and P1C01-only runtime writer remain. Report's zero-FBX snapshot is older than Windows receipt with 34 FBX families/46 LOD/63 PNG/21 MI; actual in-world residency/material appearance, Frodo deformation, PIE, target-device and human visual remain unaccepted. Git ignores Content/Production/ .uasset, requiring persistence and packaging audit. PR #421 still pending Unreal tests. P1C02 runtime remains Gate6/7 predecessor-gated.

**2026-10-12 P1C01 original-tree visual production candidate (STATIC-VALIDATED source only; UE4 Windows pending):** Extend the existing optional async-loaded original-Nature HISM world bridge from 5 ground-detail families (60 placements) to 9 families by adding the four previously source-curated/imported apple, elm, oak and willow FBX LOD0 meshes (8 placements each, maximum 92 total). Reuse three existing Shire route-area anchors per tree family, off-path ground traces, conservative height normalization and tree-specific distance culling. Missing .uasset packages safely skip, no hard reference/synchronous load, no new Tick, gameplay collision, NPC/quest/save ownership or P1C02 runtime. Update the existing runtime observation and regression, not a new workflow. Import receipts and code do not prove actual rendered trees, verified tree material slots, PIE, device FPS, visuals or Gate 6/7 acceptance.

**2026-10-12 P1C01 multi-zone curated nature follow-through (candidate; Windows exact-head checks pending):** Five existing optional async-loaded non-colliding HISM nature families retain the shared maximum of 60 instances; the candidate distributes each family among three pre-existing Shire location anchors, rejects steep ground traces, counts missing/steep traces, and extends headless runtime evidence with the actual observed loaded-family/grounded-instance count or optional-package absence. Exact-head static test was wired to Pre-Unreal. No new mission/story authority, gameplay Tick, synchronous heavy loading, or P1C02 implementation. Package staging/PIE, target-device FPS, visual approval and Gate 6/7 remain pending.

**2026-10-12 P1C01 in-world original mesh integration (new C++ candidate; COMPILE/PIE/DEVICE/visual pending):** After verified UE4.27 editor import 34 original mesh families, 46 sidecar LODs, 63 packed maps, 21 Material Instances and 7 nature single-slot bindings at Windows run 38228452433, the existing `AShirePrototypeWorldBuilder` requests five curated soft mesh paths using its own async `FStreamableManager`. It adds five capped non-colliding/no-Tick HISM groups at previously existing Shire anchors (12 placements per group, max 60), grounds them using actual world trace and normalizes bounds-based scale. Missing editor-only `.uasset` packages are entirely optional, never block chapter bank; pending request canceled at EndPlay. No changes to LivingWorldDirector, NPCContext, quest/save, or P1C02 Runtime. Flower multi-material unresolved; no guessed material overwrite. Static tests verify authored constraints but no world visual acceptance, 720p FPS, PIE, sound, NPC character completion, or Gate 6/7 evidence is claimed. Target exact head must pass UE4 C++ build and actual runtime placement audit.

**2026-10-12 exact-head UE4.27 Run 38227642493:** 21 newly owned source-identity MaterialInstanceConstant assets with all 63 PBR texture overrides passed per-instance post-save readback, then the first `flower_wild` mesh failed because its real imported FBX has multiple material slots (not the assumed single slot). Do not blanket assign one material to the entire mesh. New scoped visual intake preserves all 34 authored LOD families/46 LOD sidecars/63 PNG/21 MI when material slot count is ambiguous, binds only truly single-slot surfaces or one exactly named source slot, emits a non-accepted `unresolved_nature_slot_observations` list and actual `nature_bound` vs `nature_held` counts. This allows truthful asset pipeline progress with isolated unresolved topology and no Gate 6/7 promotion. Windows exact-head and actual slot observation pending.

**2026-10-12 P1C01 actual Unreal Python log Run 38226844047:** Commandlet entered (`P1C01_CURATED_EDITOR_PYTHON_ENTERED`) then falsely/actually rejected first texture setter: `P1C01_PBR_TEXTURE_PARAMETER_MISSING:...MI_Nature_T_Sh_Bark:AlbedoTexture`. Existing C++ verified master specifies exactly AlbedoTexture, NormalTexture, ORMTexture. Targeted remediation: check the real parent `get_texture_parameter_names`, refresh MI inheritance, set each override and judge by post-save `get_material_instance_texture_parameter_value` exact object identity, never setter bool alone; stop if stale master lacks authored parameter schema or any override is absent. Offline regressions cover setter False with applied value, absent value, stale master. No actual Windows material receipt, PIE, device or visual claim yet.

**2026-10-12 actual Windows UE4.27 import test Run 38226032895:** Existing ShireProductionImport commandlet completed `537 files, 0 failures` (2 minor tangent/binormal warnings), but `UE4Editor-Cmd -ExecutePythonScript` produced no Python entry or post-import receipt; fail reported `P1C01_CURATED_EDITOR_POSTIMPORT_RECEIPT_MISSING`. Follow Epic UE4.27 headless API: `-run=pythonscript -script=<file>` with explicit authorized environment entrypoint, stdout/abslog and targeted failure tail. No 21 MI/46 LOD success is claimed until next exact-head Windows receipt; old `537` file count is the legacy commandlet import only, not PIE/visual/device/scene acceptance.

**2026-10-12 UE4.27 MaterialInstanceConstantFactoryNew compatibility correction:** Epic's UE4.27 Python API does not expose `initial_parent` as an editor property on MaterialInstanceConstantFactoryNew. Do not write that unsupported property; create instance through the factory and call `unreal.MaterialEditingLibrary.set_material_instance_parent` (already supported and previously implemented). Offline mocked factory now rejects unsupported editor property setters to catch reintroduction. Exact-head Windows run, actual MI persisted bindings and visual/PIE/device proofs remain pending.

**2026-10-12 P1C01 ten-source pinned-SHA intake integration:** Merge `develop@ddf2b89dd06fa10c276886b6792411bfbc62a950` (PR #418) into PR #415, keeping exact-head automatic curated UE4 writer. Ten-source Drive ingestion may use verified snapshot SHA256 when remote MD5 is unavailable. Original unlicensed source promotion, final UE import, PIE, visual and device acceptance remain gated by real evidence; the develop transfer Run 38225413271 was launched and its physical result must be read, not presumed.

**2026-10-12 automated Windows/Drive dependency repair candidate:** Exact-head `fb6685a62edf178895f2713548ffcc143990fd36` Pre-Unreal and five-lane hosted PASS; Windows runner health PASS (interactive watchdog, disk 16.1GB). Actual automatic curated import FAILED `P1C01_CURATED_WAREHOUSE_ARCHIVE_MISSING` (run 38190185325). Scheduled Drive intake FAILED earlier `DRIVE_OBJECT_CHECKSUM_OR_PATH_INVALID` before transfer (run 38191426114). Targeted repair makes missing-MD5 ZIP candidates quarantined individually so one unrelated bad remote record cannot abort valid archive acquisition. Exact ten required source ZIPs, physical MD5/SHA/CRC, license, 6GiB reserve, and source-import Gate remain fail-closed. No manual dispatch, no bypass of engine or Gate 6/7 acceptance; fresh exact-head checks pending.

**2026-10-12 P1C01 PR #415 owned-material post-import refinement (candidate, STATIC-VALIDATED pending fresh exact-head CI):** Reuse the existing editor-created `M_P1C01VerifiedPBR` master, create/update 21 source-identity MaterialInstanceConstant assets and set all 63 original BaseColor/NormalDX/ORM parameters. Only 8 named, source-owned single-slot Nature mesh families are eligible for deterministic binding; trees/architecture retain their slots pending verified multi-surface maps. Require actual .uasset package existence, registry identity, saved parent/parameter/slot verification; fail closed with no successful receipt for missing master, map, parameter, file or ambiguous slot. Editor-only/offline regression does NOT prove Windows UE4 import, world placement, collision/nav, PIE, 720p FPS, human visuals or Gate 6/7. 120 external PNG remain rights-held. The exact SHA and CI run evidence must be recorded after push; no automatic warehouse or engine dispatch.

**2026-10-12 P1C01 curated editor Asset Registry fail-closed refinement (PR #415 candidate):** Both 34 base meshes and 63 owned PNG require EditorAssetLibrary registry visibility after editor save; missing registry objects abort without emitting acceptance receipt. Added offline regression. Exact-head engine import, real .uasset persistence, placed geometry, collisions/PIE/device/human visual remain pending.

**2026-10-12 P1C01 ORIGINAL-FBX LOD INTEGRATION CANDIDATE — STATIC-VALIDATED ONLY:** Source-only 34-family/46-authored-LOD/63-PNG import-postprocess scripts and fail-closed receipt verification added; no actual new Shire .uasset/presented world/NPC/PIE claim. Editor-only Python plugins require exact-head Windows UE4.27.2 test before promotion. All six offline mock tests passed. 120 outside license-uncertain PNG remain HELD. Runtime characters, collision/nav, P1C01 traversal/save-to-ferry, package, DX11 720p FPS and human acceptance unproven; Gate 6/7 OPEN.

**2026-10-12 P1C01 character and Living Shire closeout contract:** Added a named-character/living-world evidence contract to prevent Gate 6/7 closure until Frodo/Bilbo/Gandalf/Sam/Merry/Pippin and NPC daily-life behavior have runtime presence, animation/material evidence, PIE/device profiling, and human visual acceptance.\n\n**2026-10-12 P1C01 engine/import/runtime evidence upgrade:** P1C01 is now COMPILE-TESTED for the recorded self-hosted run and has production import/headless runtime/state/warning-debt success evidence (`38182847685`, `a101ee2`). This does not close Gate 6/7: package artifact, PIE traversal, target-device 720p profiling, and human visual review remain open.\n\n**2026-10-12 whole-game region readiness audit:** The 28-region production packet set now has a source regression guard, and P1C01 curated warehouse readiness is checked against minimum lanes before Unreal import. This improves whole-map material preparation without claiming engine import, PIE, visual acceptance, or Gate 6/7 closure.\n\n**2026-10-12 P1C01 curated import readiness guard:** Source-stage material and mesh promotion now has an explicit fail-closed audit covering LOD0-vs-sidecar import intent, material compression/sRGB rules, external-license quarantine, collision policy, and proof flags. It prepares the existing Shire source batch for safer Unreal import without marking Gate 6/7 complete.\n\n**2026-10-12 self-hosted compile blocker fix:** Run `38181832965` proved current-head UE4 compile failure (`C2065 BasePopulation* undeclared`) after UHT succeeded. The fix rehomes the base density fallback members into `ALivingWorldDirector` and expands source tests. Await rerun for COMPILE-TESTED.

**2026-10-12 P1C01 #400/#401 runtime regression integration:** NPC population profile fallback and CI-only checkpoint retry suppression are integrated on current develop with source regressions. This is not Gate 6/7 closure and does not claim current-head UE4 compile or PIE acceptance.

**2026-10-12 P1C01 restore quest-state sanitization source fix:** `RestoreQuestState` now rejects empty restored quest/stage keys, clamps restored stage values to non-negative integers, and de-duplicates non-empty completed story beats before restoring active route/chapter/episode/player state. Regression coverage lives in `Scripts/test_offline_runtime_safety.py`; UE4 compile/PIE evidence remains pending a self-hosted run.

**2026-10-12 P1C01 original source-to-UE4 staging candidate:** From the already-curated ten-Drive-ZIP batch, a strictly source-only tool prepares 34 original static FBX LOD0 families (12 nature, 22 architecture) plus 46 FBX LOD1/2 sidecars outside SourceAssets and 63 original PNG maps (21 BaseColor/NormalDX/ORM triplets). Source files and embedded manifest hashes are physically checked, fail-closed, path-safe, idempotent; third-party CC0-claimed 120 PNG are NOT auto-licensed or promoted. Eight logical asset/gameplay/QA workstreams run inside the existing authorized five producer lanes, not eight independent Windows writers. A 143-file source/sidecar stage was generated locally in ChatGPT container, and Python offline regressions passed; actual D: stage, UE import to .uasset, LOD binding, collision, NPC/gameplay, PIE, device, visual and Gate 6/7 acceptance remain UNPROVEN. New scheduled stage follows successful exact ten-ZIP Warehouse attestation without changing its concurrency/schedule/permissions or creating another persistent writer. Candidate requires exact-head Pre-Unreal/Drive CI.

**2026-10-12 physical Shire source curation (LOCAL-CONTAINER ONLY; exact ten Drive ZIPs):** Independently downloaded 10 owner ZIPs totaling 206,148,715 bytes, validated entire on-disk ZIP SHA256/CRC and embedded per-file receipts, then curated 263 asset bindings into 230 SHA-unique physical files (80 binary FBX, 183 PNG bindings with 33 content aliases) from 12 nature families x3 LOD, 22 modular architecture families x2 LOD, 12 original regional PBR families, 4 priority Poly Haven PBR sets and 36 CC0-receipt PBR sets. Removed 36 duplicate binary FBX and 36 legacy ASCII FBX; held incomplete wooden_barrels_01 and a failing rig-weight candidate. Locally emitted SHIRE_P1C01_CURATED_SOURCE_20261012.zip (181,360,681 bytes; SHA256 e1fb6687cb047bbead4eea8d177f11fd75e368cce169a5c30e66fbf39ecfd79f) plus complete manifest, material contact sheet and separate rig-review archive. Six source-tool tests passed locally; Scripts/curate_p1c01_drive_source.py now reproduces a SHA-checked D: curated batch only after physical ten-ZIP QC, with 6GiB reserve and unchanged authorized scheduled trigger. This is NOT proof of D: transfer or Unreal import, LOD integration, collision, PIE, target FPS, human visual, or Gate 6/7; external licenses still require review.

**2026-10-12 W01 source-only physical Warehouse QC candidate:** New Scripts/verify_drive_warehouse_receipts.py reads ten exact archived source SHA256 values from Data/DriveSourceLocalPreflight20261011.json, verifies every actual staged D: file SHA256 and computed MD5 against the transfer receipt, scans ZIP contents, exposes member-level FBX/PNG duplicate groups, quarantines ASCII FBX and incomplete provider material sets, and writes a read-only JSON source report with five explicitly blocked production waves. Integrated after the existing authorized Drive intake job, without changing its schedule/trigger/security identity, and with nine hosted regressions. Candidate status is STATIC-VALIDATED only after exact-head CI passes. No real new D: receipt, UE import, PIE/device/visual/performance or Gate 6/7 PASS claimed; licenses remain manual and import blocked.

**2026-10-12 Drive runner PATH regression candidate:** Manual Drive workflow run `38176536748` reached self-hosted Windows `UE4-27-Windows` but transfer failed before any copy at `RCLONE_MISSING`, despite owner interactive rclone connectivity and configuration. Candidate refreshes persisted machine/user PATH inside the existing watchdog job, resolves `rclone.exe` and Python/py without installing or changing the runner, then passes explicit rclone executable path to the source-only ingest script. No successful physical transfer, ZIP receipt, Unreal import, PIE/device/visual or Gate 6/7 claim; preserve read-only Drive and fail-closed auth and deletion guards.

**2026-10-11 P1C01 ten-bundle physical preflight (container, NOT Windows):** Retrieved all 10 owner Drive ZIPs into this session and audited 206,148,715 bytes; ZIP CRC/safe paths, source hash receipts, nested 28-region archive, FBX format and PNG headers passed 10/10. SHA-bound local receipt: `Data/DriveSourceLocalPreflight20261011.json`; permanent regression: `Scripts/validate_drive_source_bundles.py` + `Scripts/test_validate_drive_source_bundles.py` (8 offline tests passed). 36 binary Shire nature FBX are duplicated between two packages, distinct from the 36 old ASCII source FBX; modular nested pack contains 44 binary FBX and 36 PNG. Four Poly Haven shards contain 36 complete CC0-material triplets; `wooden_barrels_01` remained quarantined for MISSING_REQUIRED_MAPS. This is source-integrity evidence from ChatGPT container only, NOT a D: runner transfer, Unreal import, PIE, device test, visual approval or Gate 6/7 closure.

**2026-10-11 PR #402 single warehouse writer safety correction:** Consolidated duplicate hourly/two-hour Drive jobs into a single scheduled source intake and receipt tree, added watchdog session verification, explicitly blocked unattended Drive deletions and tagged staged ZIPs as unverified for license/import. This is a source-only correction; no physical D: transfer, engine import or Gate 6/7 PASS is claimed.

**2026-10-11 auto Drive warehouse candidate:** Added two-hour scheduled Windows source ZIP intake (Scripts/drive_warehouse_sync.py) and narrow exact-ID/hash/independent-backup/actual import-evidence cleanup. Uses isolated runner temp source and persistent D warehouse. One-time private rclone OAuth required; no first transfer, Unreal import or cleanup has been proven. Gate 6/7 unchanged. Hosted regressions pending.

**2026-10-11 Automatic private Drive intake candidate:** Introduced `Scripts/sync_drive_warehouse.py` and `.github/workflows/private-drive-warehouse-intake.yml` on dedicated infra branch. Hourly self-hosted warehouse-only schedule, exact-SHA temporary checkout, persistent `D:\actions-runner\_warehouse\ShireJourney\_drive_intake`, immutable SHA256 receipts, Drive MD5 match, ZIP CRC and path-safety checks, minimum 6 GiB free. This **does not** make Drive credentials available on runner: requires separately configured `SHIRE_DRIVE_RCLONE_CONFIG_B64` and rclone executable with private `shire-drive:` root restricted to the authorized Drive folder. No Drive deletion is implemented or allowed until independent backup, local integrity and import/disposition proof; do not purge sole sources. Candidate only, no actual runner sync or static CI proof yet; P1C01 Engine gate unchanged.

**2026-10-11 P1C01 save restore overlap trigger candidate:** UE runner #1969 observed P1C08 after-route-change restore fail (quest stages/story beats/NPC memory/route progress). Pre-commit overlapping trigger may mutate restored story while placement pending. Candidate sets pending saved-player transform before CommitPersistenceRestore and extends IsGameplayWorldCommitted guard. Source regression added; exact-head CI, UE transition audit and PIE remain pending. No Gate 6/7 promotion.

**2026-10-11 P1C01 quest stage idempotency source fix:** `SetQuestStage` now returns without broadcast for unchanged stages and suppresses stage broadcasts during persistence restore. Static regression added; not UE COMPILE/PIE/DEVICE/VISUAL accepted.\n\n**2026-10-11 P1C01 NPC danger committed-context source fix:** `IsDangerStateActive()` now requires committed world context before reading quest danger identity, preventing pre-commit threat leakage into NPC/world logic. Static regression added; not UE COMPILE/PIE/DEVICE/VISUAL accepted.\n\n**2026-10-11 P1C01 NPC context teardown source fix:** Deinitialize now clears committed chapter/route/episode, quest snapshot, revision, commit flag and weather state. Static regression added; not UE COMPILE/PIE/DEVICE/VISUAL accepted.\n\n**2026-10-11 P1C01 NPC context revision guard source fix:** `SetCommittedWorldContext` no longer treats revision `0` as invalid; committed NPC dialogue/schedule context can be established from any explicit router commit revision while still rejecting missing chapter/route/episode identity. Static regression added; not UE COMPILE/PIE/DEVICE/VISUAL accepted.

**2026-10-11 P1C01 LivingWorld initial commit sync source fix:** `ALivingWorldDirector` now fail-closes its first applied world revision with `MAX_uint32`, forcing the first committed router revision, including `0`, to run `ResetForCurrentChapter()` before population/event simulation. `BeginPlay` no longer trusts raw quest chapter as active world context before commit. Static regression added; not UE COMPILE/PIE/DEVICE/VISUAL accepted.

**2026-10-11 offline stale asset-ready rollback fix:** Source-only runtime audit found a live-lock risk in `AChapterWorldRouter::HandleChapterAssetsReady`: if quest/save state changed while async chapter assets loaded, the handler returned without clearing `PendingChapter/Route/Episode` or releasing/rolling back the player world hold. Added a shared pending world transaction cleanup path, stale-ready rollback, and grounding-barrier timer cleanup. Evidence target: GitHub-hosted Pre-Unreal/static tests only; UE compile/PIE remains deferred in `Docs/DEFERRED_ENGINE_ACCEPTANCE_QUEUE_20261011.md` until owner authorizes the runner.

2026-10-11 OFFLINE P1C01 DEFERRED RESTORE GUARD: ShirePlayerCharacter now blocks movement, jump, sprint, crouch, interaction, attack, supplies, QuickSave/QuickLoad and automatic checkpoint dispatch whenever bPendingSaveRestoreTransform is true. Camera look and cinematic skip remain available; no change to quest/world owner. Hosted source regression added. SOURCE CANDIDATE pending exact-head CI; not UE COMPILE/PIE/DEVICE/VISUAL accepted. Windows runner stays OFF.

2026-10-11 P1C01 NO-GROUND SPAWN FALLBACK SOURCE PATCH: ChapterWorldRouter::MovePlayerToChapterStart previously performed SetActorLocationAndRotation(RequestedLocation,...) even after ResolveGroundedSpawnLocation failed. Now retains pawn's last position, sets world hold and returns false for existing transaction rollback to recover. Added test_no_ground_never_teleports_to_unvalidated_requested_location in hosted Scripts/test_offline_runtime_safety.py; existing Pre-Unreal wiring runs it. This is SOURCE PATCH PENDING EXACT HEAD STATIC VALIDATION only. No UE compile, PIE, DEVICE, VRAM or VISUAL evidence; Windows Self-Hosted Runner not activated.

2026-10-11 OFFLINE P1C01 PLAYER RELIABILITY FIXES — SOURCE CANDIDATE (exact-head CI pending):
- Automatic checkpoint dispatch no longer loses pending ID on failed request; pending restore transform blocks checkpoint snapshots, rejected saves retry no faster than once per second. Async disk success remains separate callback evidence.
- ChapterWorldRouter now handles SetActorLocationAndRotation rejection on both save restore and chapter start: do not log PLACED or return true for rejected teleport.
- Cinematic→gameplay interrupts release presentation control lock immediately; Escape skips the active cinematic without mutating quest/canon state; pawn created mid-cinematic adopts active lock.
- Async SFX/ambience/music/voice callback matches a monotonically increasing request token, preventing stale canceled callback claiming an identical newer cue key.
- Self-hosted Unreal workflow is now manual opt-in only (workflow_dispatch run_self_hosted=true); Pre-Unreal/static and hosted classification remain automatic. Older already-queued runs have separate cancellation status and should not be assumed canceled until inspected.
- Added Scripts/test_offline_runtime_safety.py and wired it plus test_pending_checkpoint_dispatch.py into hosted Pre-Unreal Validation. Source-level checks are NOT UE4.27 COMPILE, PIE, device FPS, imported assets or visual acceptance. Runtime P1C02 remains unopened.

2026-10-11 P1C01 CHECKPOINT DISPATCH GUARD CANDIDATE: Repaired a provable source-level lost-checkpoint defect: Tick previously cleared PendingChapterCheckpointId before SaveAutomaticCheckpoint returned, while logging `commit-barrier=PASS` even on rejected dispatch. Now pending is cleared only if async/queued dispatch was accepted; disk-save completion remains callback-owned. Added Scripts/test_pending_checkpoint_dispatch.py regression guard and registered root cause in WORLD_DETAIL_LEDGER. Source-only candidate awaiting exact-head CI (STATIC-VALIDATED only after passing); no UE compile, PIE, device, FPS or visual acceptance. Windows self-hosted runner remains off.

2026-10-11 Shire nature hosted Blender regression: exact-head Run 38150281161 FAILED in physical FBX export because Ubuntu Blender 4.0.2 FBX exporter raises `ModuleNotFoundError: No module named 'numpy'` (job 114502125020); source geometry execution reached exporter but zero validated binary FBX are credited. Updated hosted workflow to install `python3-numpy` beside Blender. New exact-head rerun required. No UE proof.

2026-10-11 P1C01 Shire nature Blender production candidate: Added Tools/CloudAssetBuild/blender_nature.py and scheduled/PR hosted workflow p1c01-hosted-nature-lods.yml. Reuses twelve already defined nature families and produces 36 *proposed* binary FBX 7400 LOD0/1/2 with UV0, basic material slots, selective UCX trunk/rock collisions, Blender reimport and SHA256 receipts. No completed hosted run or new binary file may be credited before exact-head validation. Existing 27 PNG in Drive source batch are NOT republished by this workflow and require separate Unreal material binding. No Windows runner/UE4 compile/import/PIE/device/FPS/visual/Gate6/7 proof.

2026-10-11 OWNER DRIVE TEMPORARY STAGING POLICY: Governor now defines private Google Drive as temporary staging only while laptop is off. Automatic Drive deletion is authorized ONLY for managed batches with physical local persistent copy and matching SHA256 plus transfer/import disposition receipt. No TTL deletion of sole copies, no deletion of unrelated owner files, no auto transfer claim until separate GitHub Actions OAuth/rclone credential is configured. No Windows self-hosted runner authorized. This is policy/STATIC-VALIDATED only; no live sync, transfer or deletion run evidence.

**2026-10-11 licensed cloud stock intake candidate:** Existing 37 Poly Haven CC0 slug authority is now used to physically download/convert 1K BaseColor, NormalDX and packed ORM PNG files across four independent hosted shards; each shard writes SHA256/byte/provider URL/source receipt and quarantines missing maps without inventing assets. GitHub-hosted artifact stock is a temporary transfer source, not a permanent write to D:\\actions-runner\\_warehouse\\ShireJourney. 28-region packet index is available for reuse, but 28-region imported/rendered completion is NOT claimed. Local Pillow fixture regressions: 5 passed before GitHub candidate. GitHub exact-head production results pending. No owner Windows runner, no UE import, PIE, device, visual or Gate 6/7 acceptance. Runtime chapter remains P1C01 only.

**2026-10-11 P1C01 Frodo hosted locomotion source candidate:** Registered in WORLD_DETAIL_LEDGER and added Tools/CloudAssetBuild/frodo_locomotion.py plus hosted-only p1c01-frodo-locomotion-hosted.yml. The candidate imports the provenance-checked CC0 Frodo normalized base FBX, drives bilateral deform limb rotations across original cyclic Idle/Walk/Run keyed actions, physically exports three binary skeletal animation FBX files and reimports to audit curve/key presence and SHA256. Source-only: no final Frodo visual likeness, UE import, UHT/compile, PIE, device, FPS, human visual acceptance or Gate 6/7 credit. Exact-head hosted CI evidence pending; Windows/self-hosted runner is not invoked. Existing async hero stream owner and pooled NPC ownership unchanged.

**2026-10-11 P1C01 Blender thin-bevel geometry correction:** Exact-head hosted Run `38144899430` material tests and all physical 1K PNG source QC passed; GitHub Actions cache explicitly logged `Cache saved with key: p1c01-28region-original-materials-1k-v1-7a7920157b5d030369f21d7a2f85e6b86fa7209efb6242e7b506e6aeaddd812c`. The same run's FBX generator failed closed at `ValueError: DEGENERATE_FACE in SM_ShStonePath_LOD0` because the 0.018m edge bevel exceeded half the 0.025m stepping stone thickness. Universal root fix clamps each box's bevel to at most 16% of its thinnest dimension, with regression guard. No count credit for 44 FBX until the replacement exact-head Blender/validator job is SUCCESS. Frodo-hosted independent job again succeeded; owner self-hosted runner unchanged/off.

**2026-10-11 P1C01 44-FBX wave static root correction:** Exact source head `48de633534bcb1c0f6ab5eb304256a7a0e7aa625` had hosted Pre-Unreal Run `38144645925` SUCCESS; hosted asset Run `38144645916` FAILED during Blender export after successful 36 1K PNG material generation and material hash/PNG QC. Log evidence: `KeyError: 'shire_earth'` in `blender_shire.py` PALETTE (a registration omission, not a broken source image). Fixed earth color registration and added Python-AST regression checking all literal primitive surface families against palette *before* Blender execution. Source cache now saves only hash-validated PBR immediately after QC, independently of subsequent FBX failure; cache entries must pass receipt/PNG/SHA validation at reuse. New exact-head cloud run required to credit 44 FBX, Bag End portal clearance and asset archive. Existing validated 20 FBX PR #384 remain unaffected. No Windows Runner, UE import, PIE/device/FPS/visual/Gate6/7 evidence.

## 2026-10-11 — P1C01 real Bag End/Party Field architecture source wave, candidate

- **Exact prior physical proof**: PR #384 merged into develop `338afbb8ae62d9bff48b65274aef6c8d270c3973`. Cloud physical Run `38143969791` SUCCESS on exact source SHA `c4cb4410bdbe7c71e34b27b6fdc6646e698969b0` with logs `SHIRE_BINARY_FBX_GENERATED assets=10 files=20 blender=4.0.2` and `CLOUD_ASSET_STATIC_VALIDATION_PASS materials=12 textures=36 region_bindings=28 binary_fbx=20`. Pre-Unreal Run `38143969807` SUCCESS. Source artifact `11703917651` (9,492,335 artifact bytes; internal ZIP 9,492,111 bytes; SHA256 `e6eaf5ceba4c86e3878948eda55eda6a339412f1e68023fd662df27c0d0c2658`), expires 2026-10-18. Frodo CC0 **base rig** prep SUCCESS with artifact `11703892613`; no final likeness/retarget.
- **This separate active P1C01 physical production candidate** extends the existing modular static FBX generator (not Unreal runtime) from 10 to **22 original source mesh families / 44 binary FBX LOD0/LOD1**: BagEndFrontWall (separate portal blockers, walk-through gap), RoundRoomWallArc, RoundRoomFloor, Hearth, Bookcase, HobbitBed, WoodenFootbridge (separate walkway/rails), MillWheel (static-only source, rotation pending), PartyCanopy (open pole-only collision), StonePath, LanternPost, VillageWell. All are manually authored procedural DCC source parts, not film-exact replicas. Uses 36 original 1K PNG across 28 support-material region bindings unchanged. Blender 7400 binary export, real reimport and SHA256 proofs plus UCX AABB receipt and portal-clearance source guard. Material payload is now reusable via exact generator+regional packet SHA-bound GitHub-hosted cache; an unchanged cache must still pass complete file hash/PNG QC. All new physical outputs require *fresh exact-head hosted proof* and remain **pending until GitHub Actions success**.
- **Movement/NPC/engine boundary**: These parts are modular source-only, not a collision-tested level. Source-space portal clearance check does not replace player/companion navigation PIE, real material/level import or ownership integration. NPC population remains owned by LivingWorldDirector, per-character context and schedules by ShireNPCContextSubsystem; only one runtime writer. No user Windows runner, heavy synchronous loads, 28-region Unreal import, true human visual/target FPS, or Gate6/7 acceptance claimed. P1C02 runtime stays gated; physical source for later regions may progress independently.

## 2026-10-11 — REAL SOURCE DELIVERY #383 + Shire village-kit expansion candidate

- **Delivered to hosted artifact on exact head (not Unreal):** PR #383 merge `8679c2f00e140d42f2ec8c9b2cf5863ba946bf1f`; Pre-Unreal `38143599104` SUCCESS; GitHub-hosted physical-source `38143599164` SUCCESS. 12 original reusable support families produced **36 actual PNG 1024px**, mapped to exactly the 28 IDs in `Data/WholeGameRegionProductionPacketsV1.json`. Blender 4.0.2 produced **8 binary FBX static assets** (4 families, LOD0+LOD1) and successfully re-imported/checked their meshes, UV, UCX colliders and SHA256 receipts. Actual source ZIP 9,332,298 bytes, SHA256 `a3e81ebc6b47c8b962d0de3be97df5b8785bcc8e72ce7b4489c462d444f0757c`; Actions artifact `11703677680`, retained through 2026-10-18. One original CC0 Frodo base rig source candidate passed hosted readiness (`HUMAN_WAVE2_HOSTED_PASS selected=1`, 89 deform bones, 1787/2229 weighted vertices); separate artifact `11703722494`. These are real physical source assets, **NOT Unreal imported**.
- **This new source candidate expands P1C01 with 6 more original authored prop/foliage families:** RoundWindow, GardenHedge, OakTree, StorageBarrel, FarmGate, GardenPlanter; together 10 static models x 2 LOD = 20 FBX targets, keeping collision and UV static QC. The six are grounded in existing Hobbiton/Bag End domestic/cultural/settlement reference language, not claimed as film-exact replicas. Current expansion output / tests are pending exact-head hosted proof, and the first valid four families must not be re-labelled as an imported visual world.
- **Critical separation:** No change to Unreal runtime, multiplayer, crowd lifecycle, interaction/canon lock, async residency, P1C02 gate or Windows self-hosted scheduling. A character source with a rig is **not** final Frodo appearance, animation, behavioral QA or accepted Shire chapter. 28-region material bindings are not 28-region Unreal material import; follow asset promotion gate when the owner runner returns. Next manual evidence: P1C01 current real import, character deformation/retarget, PIE, save/quest/npc, device 720p 30FPS, human visual/pacing Gate 6/7.

**2026-10-11 cloud Blender FBX root fix:** Hosted Run `38143340309` generated and validated 36 physical 1024px PNG for 12 families / 28 region bindings but Blender 4.0 rejected the obsolete FBX operator argument `version=`. Static geometry construction succeeded only in memory; FBX receipts absent. Fix removes the argument, directly verifies binary FBX 7400 header version, and uses `--python-exit-code 3` so Blender script exceptions fail CI. Re-run exact-head required before counting binary FBX. No UE/PIE/device/visual acceptance.

**2026-10-11 CI source test root-fix:** Hosted Run `38143197367` Frodo source preparation PASS (`HUMAN_WAVE2_HOSTED_PASS selected=1`, armature=1, deform_bones=89, weighted_vertices=1787/2229); static material tests generated two 128px scratch preview sets with 36 PNG each and passed determinism / 28 region binding assertions. Main job FAIL was solely overbroad `self-hosted` substring in test against a harmless comment. Corrected guard to inspect `runs-on` labels, rerun exact head required. No 1024px production pack or Blender FBX yet claimed.

**2026-10-11 measurable asset wave (PREP CANDIDATE, not chapter completion):** Source code now targets physical delivery of 8 static binary FBX files (4 P1C01 families, LOD0/LOD1, Blender FBX reimport/UCX/UV) plus 36 PNG PBR channel-packed sources (12 reusable families; 28 exact region bindings), built via GitHub-hosted isolated source CI. All bytes and receipts are still **PENDING** until the exact-head workflow produces and checks them; this is not equivalent to 28-region Unreal import or character appearance. Frodo existing UE technical winner remains the only evidential character starting point: 161 bones in prior technical gate, deformation/animation/likeness/PIE incomplete. Optional hosted Frodo source acquisition will not reserve owner self-hosted Windows. Companion Gandalf next only after Frodo's proper stage. P1C01 still needs Bag End interiors/exteriors, Hobbiton houses, Party Field, road/river/vegetation, actual characters, contextual NPC behavior, quest flow, save/load, English VO/Arabic RTL, target DX11 720p 30FPS and human visual Gate 6/7 evidence. No new runtime acceptance label.

**2026-10-11 live recovery audit (source-only; PR candidate):** GitHub develop `86966cfde730a7e9b3432d73da46fc67995d6ba7` after PR #381; 31 refs / 13 open PRs at inspection. PR #380 head `9f5b6fd53d6c004bc728b479c46af680ea0d3b1f` remains open draft, diverged by one newer develop commit and merge-dirty; exact-head hosted Pre-Unreal Run `38141627675` SUCCESS but Unreal Run `38141627681` queued. No owner Windows runner was started or authorized by this wave. The only inspected zero-ahead noncanonical ref is `salvage/p1c01-fast-pie-ci-guard-20261011`; all other inspected working refs carry unique commits and are preserved. Eight Poly Haven CC0 P1C01 base-color Git-LFS pointer OIDs on `generated/p1c01-material-source-v1` match their source receipt; real LFS contents, image resolution, UE import and rendered quality remain unverified. See `Docs/RECOVERY_CHECKPOINT_2026-10-11.md`. No UE compile, PIE, FPS, device, human visual or Gate 6/7 acceptance implied.

**2026-10-11 fast preview salvage candidate:** PR #360 useful three-file launcher/test/guide ported to current develop candidate without stale workflow/governor merge; only source/tooling, not UE compile, PIE, device, visual or Gate 6/7 evidence. Exact-head CI pending.

**2026-10-11 P1C01 Bag End hub source-only production candidate:** `Data/P1C01BagEndHubAssemblyV1.json` adds a detailed canonical interior assembly handoff (shell, domestic props, interactive anchors, audio/light), state variants, traversal/collision/streaming/NPC ownership contracts and five-lane item-level receipt tasks. No geometry generated, warehouse bytes acquired, Unreal import, compile, PIE, device, visual or Gate 6/7 proof; exact-head hosted validation pending. Existing P1C01 runtime scope unchanged.

**2026-10-11 checkpoint reconciliation (candidate):** Live GitHub inventory observed 30 branches and 14 open PRs. Created `Docs/RECOVERY_CHECKPOINT_2026-10-11.md` on branch `ops/checkpoint-branch-reconciliation-20261011`; compared #366 (2 ahead/41 behind), #367 (1 ahead/41 behind), #374 (4 ahead/19 behind), and older checkpoint recovery (1 ahead/97 behind) against develop. All divergent: preserve pending selective salvage and exact-head checks. No PR merged, branch deleted, UE compile, PIE, device, FPS, visual or Gate 6/7 proof from this checkpoint. This is repository-source documentation only, pending exact-head static CI.

**PG-170 contract alignment (2026-10-11):** exact-head Pre-Unreal `38135715043` FAILED at outdated static assertions for legacy `$_` PR-row dereference. The *real* PowerShell array decoder regressions passed (flat=2, nested=2, single=1, empty=0). `Scripts/pre_unreal_validate.py` now checks the actual `$row` guards and `Get-OpenPullRefs` reuse rather than prior variable spelling. New exact-head hosted CI pending; no engine/PIE/device evidence.

## 2026-10-11 — Branch Cleanup live-open-PR array decoder regression (candidate)

- Investigated hosted cleanup run `38135341955` after successful reviewed retirement. The run logged `activePrHeads=0` even though GitHub had open PRs. Exact per-branch rechecks and nonzero-ahead fallback preserved unique heads in that run, but bulk PR protection was not reliably visible.
- Root-cause mitigation: normalize both flat and nested Windows PowerShell `Invoke-RestMethod` PR JSON arrays with `Get-OpenPullRefs`; use the same normalizer for the initial active-head set and exact per-branch recheck. Preserve fail-closed SHA lease, closed/replacement-PR proof, archive/Edoras protections and zero-ahead policy unchanged.
- Hosted PowerShell classifier regression now executes the actual helper against flat/two-level/single/empty PR samples. **Evidence status:** source candidate pending exact-head Pre-Unreal/Five-Lane; previous #373 branch deletion remains proven at `38135341955`. No UE compile, FBX import, PIE, device, FPS, visual, or Gate 6/7 claim.

## 2026-10-11 — Post-#372 reviewed stale-ref retirement (PR candidate)

- **Policy:** DEC-106 reconciled after merged PR #372 (merge `a004d47b6c7d4681a328d88a12fc5de4819e1f11`) with exact-head GitHub-hosted Pre-Unreal SUCCESS `38134887589` and Five-Lane SUCCESS `38134887757`. Classified **STATIC-VALIDATED**. All WindowsNoEditor packages remain owner-requested chapter/release closeout only; engine compile/PIE/device/visual/Gate6/7 remains unproven.
- **Branch reviewed for retirement:** `policy/cloud-first-no-routine-windows-package-20261011`, exact SHA `5ccc60523247138e324887929b6b8f1c85db0931`, closed/unmerged PR #369. Unique delta contains four policy/docs files; policy intent superseded by merged PR #372, not by a claim of identical Git ancestry.
- **Safety implementation:** `Data/BranchCleanupPlan.json` registers this exact ref/SHA, closed PR, replacement PR+merge. `Scripts/run_branch_cleanup.ps1` now fail-closes on moved SHA, active PR, missing replacement, missing merge ancestry, unknown unique refs and uses atomic Git `--force-with-lease` for both explicit and PR-head retirement.
- **Remaining branch rule:** every other inspected noncanonical branch still has unique commits vs develop. Preserve FBX/Tangents/Skeletal/PBR/preview/generated material/Edoras candidates until selective reconciliation and proof. Do not delete by age or branch title.
- **Current evidence boundary:** branch #369 cleanup is *authorized pending a successful hosted PR and actual cleanup log/ref-not-found proof*; no remote deletion or performance/visual acceptance claimed by this entry.

**PG-145 static regression correction (2026-10-11):** Exact-head Pre-Unreal run `38134722720` failed only at the outdated hosted Unreal guard token `needs.classify.outputs.mode != 'inherit'`, after real classifier cases and packaging contract had already passed. Replaced that old expectation with explicit `full/core/acceptance/package` selection markers and added `Scripts/pre_unreal_validate.py` to the narrow hosted-only policy allowlist. Five-Lane run `38134722700` SUCCESS on previous head; new exact-head preflight remains pending. This is a CI test-contract fix, NOT real UE compile, PIE, device or chapter acceptance.

## 2026-10-11 — Manual-only Windows packaging + hosted policy regression (PR candidate)

- DEC-106 production implementation on current develop after PR #370: `workflow_dispatch package_windows=true` exclusively enables WindowsNoEditor Cook, data proof, packaged startup, hardware capture and large artifact upload. Config/Build.cs/unknown/failed-classifier paths still take the appropriate UE compile/import/runtime lane when the owner runner is available, but never cause a routine package.
- Narrow exact-path-only `static` classification for governance/classifier workflow/Docs updates runs the real PowerShell classifier regression on GitHub-hosted Windows without reserving the owner's UE runner or implying an inherited Unreal build proof. Acceptance-only changes without packaged-startup resume also stay on hosted-only classification.
- Regression covers real Set-Mode output across pull request, default manual dispatch and explicitly requested chapter package; config/unknown/no-proof cases remain strictly classified. Governor and MaximumSafeMode updated together; P1C01 runtime scope and Gate 6/7 unchanged.
- Dedicated P1C01 Verified PBR workflow was a separate hidden duplicate self-hosted PR trigger. It is now manual `workflow_dispatch` only; optional `package_windows` defaults false, and cook, data/startup checks and artifact upload require true. The actual FBX import/UE QA remains available on deliberate dispatch; no import evidence is invented.
- **Evidence boundary:** Source policy candidate. Exact-head hosted CI results pending; no new UE4 compile, FBX import, PIE, device FPS, visual acceptance, Windows package, or Gate 6/7 credit.

## 2026-10-11 — #365 CI regression correction (candidate)

- Exact-head Pre-Unreal #38102533805 failed in two source contract assertions: one obsolete manual-only trigger expectation and one new test using literal escaped newlines. The dedicated PBR lane intentionally runs on PR but never cooks/packages except manual dispatch. Corrected assertions and tightened package gates; requires new exact-head CI success. No runtime/device/visual acceptance.

## 2026-10-11 — P1C01 verified PBR importer integration on PR #365 (candidate)

- Physical Blender FBX normalization from #355 is forward-ported into the active #365 source stage: copied from `Saved/P1C01NormalizedFBX` into ignored `Saved/ShireProductionImportWorking` only; tracked warehouse FBX is never altered. The commandlet rejects missing derivative receipt, malformed source layout, or missing derived FBX.
- Existing real UE4 material-slot/Asset Registry checks, /Game/Production packages, and chapter async world bank remain the activation authority. Exact hash validation runs in the dedicated workflow before the UE import commandlet; source-only/mocked tests do not claim imported geometry.
- FBX normalizer no longer welds coincident vertices across valid UV/hard-normal seams. Cache keys include exact original FBX hashes, normalization scripts and installed Blender version; a cache hit still runs receipt/SHA256 verification. Normalized/reused totals are logged.
- Dedicated PBR PR pipeline stages 16 sourced FBX, runs Blender, imports into UE4, audits materials and tests headless Shire placement. Windows package/upload is excluded from PR and develop push; final package requires explicit dispatch. Classifier treats named PBR toolchain changes as engine-impacting but not Windows-packaging-critical; unknown paths still fail closed.
- Evidence: PR #365 previous source-only head `90e69e6a` passed Pre-Unreal run `38102045664`. **These NEW importer/workflow edits require fresh exact-head Pre-Unreal and UE/PBR proof.** No PIE, device, visual, actual FPS, Gate 6/7 acceptance or 17-warning elimination is claimed; do not open P1C02 Runtime. $8 Actions ceiling unchanged.

## 2026-10-11 — P1C01 derived FBX hash-cache tooling candidate

- Forward-ported the verified Blender normalization script and SHA256-bound derived-FBX preflight from PR #355 onto current develop as a source-only integration candidate, with exact-head Pre-Unreal regression. This does NOT activate new runtime assets, modify the actual UE importer, or solve all 17 smoothing warnings on develop. Original CC0 FBX is immutable; generated derivatives live in ignored Saved/. The importer overlay/physical UE binding, PIE, device 30 FPS, full playthrough and Gate6/7 remain unaccepted. Windows packaging is not requested; preserve DEC-106 and $8 CI budget ceiling.

## 2026-10-11 — Whole-game regional CC0 material receipt cache correction (candidate)

- Root cause: `stage_ambientcg_warehouse.ps1` reused a previously green batch receipt based on batch ID and stored ZIP hashes alone. An edited region/query/quality manifest with the SAME batch ID could silently skip the new source intake, preventing material updates across the authorized whole-game region preparation. The repair writes `manifest_sha256` to new receipts and requires an exact manifest hash match for early reuse; legacy receipts fail closed and are re-evaluated without destroying valid cached ZIP bytes. Even `-Refresh` now keeps structurally valid archives rather than automatically deleting them. Existing SHA256/ZIP/disk reserve/CC0 checks and single warehouse writer remain active. A network-free PowerShell regression exercises unchanged, changed and legacy receipts with a real temporary ZIP, and checks that invalidating a receipt does not delete the archive. This is source-only preproduction for the existing 28-region packet set (Shire included), not proof of importing materials into 27 other runtime regions. Pre-Unreal and exact-head evidence pending; no Unreal/PIE/device/visual or Gate6/7 acceptance. User GitHub Actions budget ceiling $8 is unchanged.

## 2026-10-11 — DEC-106 whole-game Windows package cadence (CI candidate)

- Owner explicitly wants nonessential repeated engine checks minimized across the **entire Shire Journey game**, not P1C01 only; heavy Windows Cook/Package/WindowsNoEditor artifact upload should normally happen at chapter completion/release, not each source/asset/editing checkpoint. Sole authority is `Data/ProjectGovernor.json` DEC-106 and `chapter_closeout_package_policy_2026_10_11`, linked to REQ-PROD-011.
- Real prior UE CI log #1884 recorded `W00_PACKAGE_PASS elapsedSeconds=211` and Windows candidate upload ~144 s for 332276215 bytes. These are existing reference costs, NOT a measured speedup.
- `Scripts/classify_unreal_validation.ps1` now emits `package=true/false` independently from `full/core/asset/acceptance`. `.github/workflows/unreal-build-validation.yml` consumes that output for cook, packaged JSON, packaged executable startup and upload. Explicit `workflow_dispatch` `package_windows=true` forces full exact-head build + packaging. The standard full-mode fallback for changed game runtime/source **does not package** when the changed path is already known as non-packaging-impacting.
- Packaging-critical `Config/**`, Build.cs/Target.cs, streaming bank, Cook/Package/Release and unknown potentially impacting paths still require full package proof immediately; package/startup validator changes require package proof unless safe same-content proof can be inherited. Startup-only retesting does not redundantly upload a large package.
- `Scripts/test_unreal_classifier.ps1` includes whole-game example cases covering safe known runtime changes, no-proof fallback, manual closeout, config/streaming, package-tool changes, and unknown paths. Docs/Gates updated without changing code gameplay, canon, memory or renderer. No second Governor authority file.
- This CI change is **SOURCE CANDIDATE / STATIC CHECKS PENDING** until exact-head Pre-Unreal / classifier regressions and real runner classifications. No UE4 compile, package, PIE, DEVICE, VISUAL, FPS or Gate 6/7 credit for this branch. P1C01 is still the sole active runtime chapter; future chapters need their own acceptance evidence.

## 2026-10-11 — P1C01 GitHub Actions de-duplication and artifact transfer efficiency (candidate)

- Owner-requested CI throughput repair, no new chapter/gameplay feature. The generic `.github/workflows/unreal-build-validation.yml` already covers affected UE runtime source paths; the specialized `.github/workflows/p1c01-verified-pbr-production.yml` also auto-ran on `develop` changes to the Shire world builder/import commandlet/bridge, risking a second compile/import/cook/package on the same limited Windows self-hosted runner.
- The specialized 99-source Verified PBR import/package workflow is now `workflow_dispatch` only: it remains available for deliberate P1C01 visual asset promotion with checksum receipts, FBX/PNG source staging, actual UE4 import, material-slot/runtime-presence tests, save/route verification, cook/package and executable startup. This is not permission to bypass its evidence when promoting Verified PBR visuals or making Gate 6/7 claims.
- `actions/upload-artifact@v4` in that manual packaged binary lane now uses `compression-level: 0`, matching the existing general Unreal package artifact optimization to reduce compression CPU time; upload/network speed improvement is not yet measured.
- Added `Scripts/test_p1c01_verified_pbr_bridge.py` regression to ensure dispatch-only trigger, upload setting, and retention of import/runtime checks. The static test path is excluded from both general Unreal push/PR triggers and remains covered by Pre-Unreal Validation.
- Source/CI-config review only so far. Exact-head Pre-Unreal, fresh UE workflow behavior, transfer benchmarks, PIE, target-device, visual acceptance, FPS and Gate 6/7 evidence are **pending**. Existing compile/runtime acceptance is not inherited across this change until verified by the project's proof classifier.

## 2026-10-11 — Root-cause repair of local PIE classifier (PR #359)

- Pre-Unreal Run #38093231196 failed `pie-preview-safe-with-proof: expected inherit, got full`: the two exact paths appeared only in the transitive core-proof allowlist, not in the main `$safeExact` set used by `$fullImpact`. Add them to the actual exact-path classifier and cover lookalike names, mixed runtime and Config changes in the real classifier regression. Parent engine proof remains mandatory, otherwise full validation. PR #358's actual preview command/test still requires exact-head static execution prior to merging. Candidate awaiting CI; no new Unreal/PIE/device/visual/FPS acceptance.

## 2026-10-11 — Local PIE tooling CI reduction (proof-required)

- Corrects classification of exactly `SHIRE_FAST_PIE_PREVIEW.bat` and `Scripts/test_fast_pie_preview.py`, allowing established green exact-parent engine evidence reuse and preventing repeated full UE builds for unchanged gameplay. Fails closed to full Unreal when inherited proof is missing. Evidence: #38092759311 classifier `FULL_UNREAL_FILE` for these two paths. No chapter progression, gameplay, asset, device, visual or FPS acceptance produced.

## 2026-10-11 — Minimum redundant checks: device-evaluator CI classifier correction (candidate)

- Corrected file classification for `Scripts/evaluate_p1c01_gate67_evidence.py`: acceptance-only with proven exact-parent core engine run can reuse that engine evidence; absent engine proof retains full validation. Regression cases added to `Scripts/test_unreal_classifier.ps1`. This does not build/alter Shire visuals, imported meshes, quests or any P1C02 runtime; P1C01 PERFORMANCE / PIE / DEVICE / VISUAL / Gate 6/7 remain unaccepted. Run #38091586642 previously classified the evaluator as `mode=full`; fresh exact-head static/regression proof is required before merging.

## 2026-10-11 — Accelerated intake policy only, not content completion

- Owner-approved operational direction: remove redundant administrative admission checks, fast-path lawful repairable candidates, keep real asset rights and technical acceptance, consolidate large P1C01 waves and prepare 28-region art/characters concurrently. **Status: policy registered; implementation and runtime output pending**. No increase in visual, PIE, device, FPS or Gate 6/7 completion.

## 2026-10-10 — Owner living social landscape standard, Shire-first / all regions (design requirement)

- Scope/requirements documentation candidate only: living social landscape first in P1C01, later region-specific adaptation (28-region design coverage). Status PLANNED/DEFERRED as appropriate; no new asset files, UE import, character art, measurable visual acceptance, performance credit or Gate 6/7 completion.


## 2026-10-10 — Whole-game character CC0 source candidate research (preparation only)

- Created `Data/WholeGameCharacterSourceCandidates20261010.json` with Quaternius Modular Fantasy Outfits, Quaternius RPG Characters and Blender Human Base Meshes candidate sources for visual/rig research across the 28-region production scope. This is source-discovery metadata only: license-per-download, exact format, SHA256, rig compatibility, proportions, LODs and render/art acceptance are pending. No files downloaded to persistent warehouse, no Unreal import, no new runtime chapter, no P1C01 Gate 6/7 credit.
- Continue only within existing Governor-approved P1C01-first runtime + independent whole-game asset preparation policy. One warehouse writer, no duplicate downloads; no generic third-party mesh is accepted as a named Tolkien hero without original character-specific art and canon review.

## 2026-10-10 — physical source intake and Frodo correction (observed)

- Warehouse Run #38057877090 SUCCESS with real source result: AMBIENTCG_WAREHOUSE_STAGE_PASS files=22 skipped=24 bytes=1178435662 and REGION_SOURCE_RECEIPT_AUDIT_PASS files=22 skipped=24 reserve=175388110848. This is source QC only, not PBR imported into future regional runtime.
- Frodo fail-closed deformation correction PR #346 MERGED commit 3b20cac4d01d1b7cf05581b211f4f88f510a2c54; three exact-head workflows #38058581392/#38058581341/#38058581318 succeeded. Technical-only; no finished skeletal locomotion, human-rendered visual or chapter Gate 6/7 acceptance.

## 2026-10-10 — P1C01 package-audit and exact-material importer contract repair (candidate)

- Observed static cross-file inconsistency: `ci_package_w00.ps1` compares the unique `/Game/Production` package count with `Data/ChapterAssetStreamingPlan.json.audit.total_unique_production_packages`, but the verified PBR activation appended asset paths without adjusting the audit. Candidate repair computes unique packages from all actual banks and updates P1C01 bank count idempotently, no hard references or eager loads.
- Previously unused import verifier expected a receipt and log token the active PBR bridge never produces; replace with actual `HASHED_SOURCE_ONLY` receipt + exact importer `P1C01_VERIFIED_PBR_IMPORT_QC` proof for every selected FBX/material pair, and gate this before bank promotion. Offline suite covers missing/incorrect import log, unbound mesh, and stale package audit. Status PENDING exact-head workflow and real source/imported-package receipts; not PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED or 30FPS.

## 2026-10-10 — P1C01 PBR runtime presence truth gate (candidate)

- Closing a visual Shire requires actual world placement, not only FBX source QC, .uasset presence or `W00_PACKAGED_STARTUP_PASS`. PBR workflow now requires explicit non-zero full placement in `Saved/Logs/CI-PlayableStartup.log` with matching async P1C01 bank entries and no omitted assets, prior to packaging; emits `P1C01_PBR_RUNTIME_PRESENCE_PASS` only upon observed log evidence. Regression fixtures cover missing log, zero placement, absent streaming bank and UTF-16 log. This is source-candidate validation only until a real exact-head run; no P1C01 chapter visual, target FPS or human Gate 6/7 credit.

## 2026-10-10 — P1C01 verified PBR material-parent regression (PG-169)

- CI #38052565591 FAILED: original C3 foliage parent invariant `DesiredMaterialParent = ProductionMaterialParent` was displaced by conditional new PBR master selection. Restored original default assignment with explicit verified-PBR-only override, preserving foliage identity and preventing regression. Exact-head Pre-Unreal retest pending; no Unreal visual/P1C01 Gate6/7 proof yet.

## 2026-10-10 — P1C01 source-to-visible UE4 PBR bridge production (candidate)

- Reuse two immutable Poly Haven CC0 39/60 source waves, validate SHA256 original receipts and per-file hashes, choose at most 16 qualified single-material **static FBX** props within a 144 MiB source cap; imported textures are 1K PNG. Quarantine/hold, oversized, unknown-multi-material, and unsupported files are not promoted. No new source-provider downloads.
- Scripts/p1c01_verified_pbr_bridge.py stages ignored generated source assets into SourceAssets/Production/World/Shire/VerifiedPBR; the existing UE4.27.2 importer synthesizes a material instance and now fails on missing/wrong single-material slots and invalid mesh geometry. Only after .uasset files exist does the bridge append soft paths to the existing P1C01 async bank and materialize Data/P1C01VerifiedWorldDecor.json.
- AShirePrototypeWorldBuilder renders up to 16 small world accents from resident soft objects without collision, actor ticking, extra NPC ownership, canonical route transforms or new chapters. Verified subset source maps include BaseColor, NormalDX and packed ORM; BaseColor, tangent NormalDX and packed ORM wiring is present in source; actual UE import and visual shader fidelity require evidence.
- .github/workflows/p1c01-verified-pbr-production.yml schedules real UE editor build, source import, uasset verification, Automation, startup, chapter/save round-trip, compressed Windows package and packaged startup before uploading a test build. This workflow is not a five-lane read-only report.
- All evidence **PENDING exact-head CI and runner execution**; no PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED, 30 FPS, or Gate6/7 claims. No move to P1C02 runtime.

## 2026-10-10 — P1C01 physical CC0 PBR-to-UE4 visual production bridge (candidate, evidence pending)

- Manager authority: DEC-078/104/105, REQ-PROD-011, W01/P1C01 only. Actual persistent warehouse Run #38049193046 completed SUCCESS, providing immutable 39+60 source and 39+59 prepared PBR files; this is source storage evidence, not engine/render evidence.
- This PR adds an exact SHA256 checked, bounded (up to 16 static assets / 144 MiB) source bridge from the persistent two-wave CC0 warehouse into the existing `SourceAssets/Production/World/Shire/VerifiedPBR` importer. Reject held-identity, held-biome, corrupted, multimap/multi-material and non-Shire/unrelated candidates. Avoid provider redownload, hard runtime references and any character FBX.
- Unreal importer now binds verified single-material FBX to a real PBR master: BaseColor + tangent-space NormalDX + packed ORM (ambient occlusion R, roughness G, metallic B), with non-sRGB packed/normal imports. Preserve existing OBJ asset bank unchanged.
- Existing `UShireChapterAssetStreamingSubsystem` preloads selected soft paths via `Data/ChapterAssetStreamingPlan.json`. Existing `AShirePrototypeWorldBuilder` adds at most 16 optional, non-colliding, low-shadow static decorative pieces after world commit and never synchronously loads meshes. Canonical route/story/quest ownership and actor pooling remain unchanged.
- A dedicated GitHub-hosted offline source test + serialized Windows UE4.27.2 workflow runs actual source stage, editor build, production import, `.uasset` presence, automation, startup, all chapters, state persistence, warning guard, cook and packaged startup. Only success can publish a playable Windows **test candidate**. The new visual packet is NOT declared PIE, device, human visual or Gate 6/7 accepted.
- Until exact-head tests run, this is a source implementation candidate. Fix compile/import/runtime failures on this same PR before merge; avoid new feature lanes until machine-green. No final Windows release requested.

## 2026-10-10 — avoid pointless Unreal recompiles for standalone warehouse regression tests (candidate)

- `Scripts/test_warehouse_provider_zero_payload_fail_closed.ps1` is a network-free provider/ambientCG guard, not Runtime code. Its new source-only checks should run in Pre-Unreal without reserving the one UE4.27 machine. Add the explicit test script to both push/PR Unreal-workflow paths-ignore lists; the existing `Scripts/stage_*warehouse*.ps1` rule already excludes the warehouse adapter. Actual P1C01 runtime work remains on its own exact-head UE gate. No compile claim for this candidate.

## 2026-10-10 — ambientCG cross-lane duplicate download regression guard (candidate)

- Observed live warehouse #38057877090 SUCCESS: `AMBIENTCG_WAREHOUSE_STAGE_PASS files=22 skipped=24 bytes=1178435662`, `REGION_SOURCE_RECEIPT_AUDIT_PASS files=22 skipped=24 reserve=175388110848`. These are actual SHA256-audited source-only bytes, not Unreal imports.
- Root-cause in `Scripts/stage_ambientcg_warehouse.ps1`: ten regional material queries can return the same provider asset ID. Run logs show repeated downloads of Rock064, Ground111 and PavingStones151; prior script only guarded identical destination paths and did not deduplicate across category folders. Add accepted-ID set updated ONLY after successful source SHA256 receipt; skip later duplicate IDs before network requests. Byte-cap failure must not remove previously valid cached archive; do not trigger or repeat the completed batch. Existing Quaternius zero-payload Pre-Unreal step also checks the ambientCG dedup code order offline.
- Candidate until exact-head preflight. One persistent warehouse writer and 6 GiB reserve retained. No P1C01 runtime change, PIE, target-device FPS, visual or Gate6/7 credit.

## 2026-10-10 — avoid pointless Unreal recompiles for standalone warehouse regression tests (candidate)

- `Scripts/test_warehouse_provider_zero_payload_fail_closed.ps1` is a network-free provider/ambientCG guard, not Runtime code. Its new source-only checks should run in Pre-Unreal without reserving the one UE4.27 machine. Add the explicit test script to both push/PR Unreal-workflow paths-ignore lists; the existing `Scripts/stage_*warehouse*.ps1` rule already excludes the warehouse adapter. Actual P1C01 runtime work remains on its own exact-head UE gate. No compile claim for this candidate.

## 2026-10-10 — ambientCG cross-lane duplicate download regression guard (candidate)

- Observed live warehouse #38057877090 SUCCESS: `AMBIENTCG_WAREHOUSE_STAGE_PASS files=22 skipped=24 bytes=1178435662`, `REGION_SOURCE_RECEIPT_AUDIT_PASS files=22 skipped=24 reserve=175388110848`. These are actual SHA256-audited source-only bytes, not Unreal imports.
- Root-cause in `Scripts/stage_ambientcg_warehouse.ps1`: ten regional material queries can return the same provider asset ID. Run logs show repeated downloads of Rock064, Ground111 and PavingStones151; prior script only guarded identical destination paths and did not deduplicate across category folders. Add accepted-ID set updated ONLY after successful source SHA256 receipt; skip later duplicate IDs before network requests. Byte-cap failure must not remove previously valid cached archive; do not trigger or repeat the completed batch. Existing Quaternius zero-payload Pre-Unreal step also checks the ambientCG dedup code order offline.
- Candidate until exact-head preflight. One persistent warehouse writer and 6 GiB reserve retained. No P1C01 runtime change, PIE, target-device FPS, visual or Gate6/7 credit.

## 2026-10-10 — Frodo deformation gate forward-port onto current develop (candidate)

- PR #343 exact-head #38057554992: hosted source/normalization, UE4.27.2 skeletal technical gate, and Blender deformation jobs concluded SUCCESS; Unreal Build #38057555101 and Pre-Unreal #38057555072 concluded SUCCESS. Earlier PR #340 run #38056805116 recorded `BLENDER_NUMPY_READY`, `HUMAN_WAVE3_DEFORMATION_PASS`, `HUMAN_WAVE3_STATIC_DEFORMATION_RECEIPT_PASS`. PR #343 could not merge cleanly with evolved develop; preserve its exact code and contract regression on a fresh develop-based branch, without duplicating it from #340.
- Existing source-only fix enforces `--python-exit-code 93`, NumPy, unique hosted/UE4 receipts, nonempty result and `STATIC_DEFORMATION_STRESS_PASS` with visual/runtime acceptance explicitly false. This is a production candidate until its new exact-head tests pass; no Frodo final art, PIE/device, target FPS, VISUAL or Gate 6/7 acceptance is claimed. P1C02 remains CLOSED.

## 2026-10-10 — Confirmed GitHub default branch is develop

- Live GitHub repository metadata reports `default_branch=develop`. Owner confirms develop is canonical default/integration/programmer-handoff; `main` remains stable/release only. Updated existing `Data/ProjectGovernor.json` branch_workflow notes to remove stale assertion that main is default; no new Governor authority, no runtime content change.
- Whole-game ambientCG material query correction PR #344 merged to develop as commit `a50e117259c3f5b779af67adad9ec8f5855e139c`; exact-head physical source intake result still pending. The owner did not authorize extra runtime chapter; P1C01 only, Gate 6/7 remains unaccepted.

## 2026-10-10 — ambientCG whole-region intake zero-result correction (candidate)

- Real run #38057505000 reached official ambientCG API and returned `AMBIENTCG_WAREHOUSE_STAGE_PASS files=0 skipped=0 bytes=0`; hard receipt gate correctly FAILED with `REGION_INTAKE_ZERO_VERIFIED_FILES`. Multiword natural-language keyword queries found no eligible ZIP records. Replace them with ten concise asset-family terms while preserving region mapping, CC0 license, 2K-PNG source QC, single serialized warehouse writer and >=6 GiB free-space reserve. Await exact-head and real staged SHA256 evidence; no files or visual/PIE/device acceptance claimed.

## 2026-10-10 — Whole-game warehouse PowerShell stale exit code repair (candidate)

- Real warehouse run #38056824745 FAILED in manager/runner health step after its own `RUNNER_HEALTH_PASS` log. Root cause: checking stale `$LASTEXITCODE` after a PowerShell script invocation, which does not guarantee reset of that native command exit variable. Correct step guards to check `$?` immediately after script calls; preserve Project Governor, staged receipt SHA256 audit and 6 GiB reserve. No provider downloads occurred in failing run; correction awaits exact-head CI and rerun.

## 2026-10-10 — Whole-game licensed ambientCG regional intake V3 (candidate)

- Added ten bounded material search lanes for 16 source-indexed regional IDs (including Minas Tirith, Helm's Deep, Edoras, Osgiliath, Rivendell, Fangorn, Isengard, Pelennor and Grey Havens) using existing public ambientCG 2K-PNG CC0 adapter, not a new material system. Register source queries and multi-region reuse; exact provider asset IDs are only assigned by live API staging.
- New separate source-only intake workflow shares the existing serialized warehouse-stage concurrency group, requires Project Governor and Windows runner, checks 6 GiB disk floor before and after stage, requires SHA256 verified nonempty receipt, and does not access Unreal Content or open another runtime chapter.
- Branch/pre-merge state: MANIFEST_AND_WORKFLOW_CREATED, STAGING_NOT_RUN; no new downloads, verified inventory additions, Unreal integration, PIE, device, visual or Gate 6/7 acceptance. On merge to develop the path-scoped production workflow will run; check receipt results and quarantine failures before declaring intake success.

## 2026-10-10 — P1C01 mandatory Project Governor work-start and five-lane enforcement

- DEC-104 is enforced as a mandatory physical production entrypoint. Existing five-lane read-only preflight is NOT proof of generated assets. Scripts/governor_work_start.py runs the full Project Governor and checks DEC-078/104/105, REQ-PROD-011, active P1C01 gate, one runtime writer, one warehouse writer, 6 GiB reserve and five lane identities before production.
- Production workflows for Unreal, warehouse, skeletal characters, visual source and chapter closure now require the manager. Pre-Unreal regression tests forbid their bypass. Chapter closure source writer shares warehouse-stage concurrency with durable source staging.
- Evidence: source changes submitted for exact-head CI. No new Unreal asset import, chapter PIE, target device measurement or visual acceptance is inferred. The existing warehouse #38049193046 is independent and not cancelled.

## 2026-10-10 — P1C01 production bottleneck: source-only five lanes vs blocked durable warehouse (PENDING)

- Verified `five-lane` workflow is *five read-only preflight lanes*, not five concurrently writing Unreal production assets. The durable 99-asset warehouse workflow targeted a merged temporary source branch and required manual dispatch after merge, leaving real 39/60 receipt promotion unproven. This change targets a one-shot `develop` merge activation of the existing exact-head durable warehouse train with SHA256 cache reuse, serialized writer, and 6 GiB reserve.
- Status: `SOURCE_PIPELINE_TRIGGER_PREPARED_NOT_YET_RUN`; `99_SOURCE_FBX_UNREAL_IMPORT=NOT_PROVEN`; `P1C01_GATE67=NOT_ACCEPTED`. A real durable warehouse success and separate authored runtime import/PIE/performance evidence remain required.

## 2026-10-10 — PG-026 release artifact versus failure-logs contract

- Pre-Unreal #38045489962 failed: PG-026 failure logging may not depend on artifact upload quota. On isolated fix PR #336, removed `always()` log artifact upload, kept console failure logs and allowed a success-only packaged Windows playable candidate. Static exact-head checks and UE results pending. No Gate6/7 credit.

## 2026-10-10 — P1C01 warehouse Windows nested relative-path root cause isolated

- Real failure Run #38042482514: source39 245957831 B and pbr39 197353784 B **SHA256 verified and extracted** on persistent warehouse; staging wave39 then failed `StageError: UNSAFE_RELATIVE_PATH` at `stage_p1c01_adaptive_pbr_warehouse.py:358/331` on Windows. No wave39 permanent receipt, wave60 not started.
- Root cause: `str(safe_path(...))` uses Windows backslashes when nested provider receipt paths (e.g. `textures/gate_diff_1k.png`) are converted, but `safe_path` correctly disallows backslashes in durable receipt keys. Minimal patch changes validated relative path serialization to `.as_posix()`, with a nested texture real fixture regression. Preserve cache; do not download source39/pbr39 again.
- The exact-head Windows/Linux regression and real persistent warehouse evidence remain pending. No UE/PIE/device/visual acceptance claimed. This work lives on an isolated fix branch to avoid canceling active PR #335 packaging CI.

## 2026-10-10 — P1C01 first downloadable playable candidate, fail closed

- On the owner-approved P1C01 delivery lane, patched the game's default editor/game map, headless runtime smoke, packaging cook map and packaged startup observation to `/Engine/Maps/Entry`. This follows `Data/P1C01LocalVisualBootstrapV1.json` that identifies the engine `Template_Default` floor as a visual masking defect.
- The existing exact-head `Unreal Build Validation` workflow now runs `Scripts/test_p1c01_delivery_entry_map.py` on hosted Windows **before** the UE runner and uploads the real `WindowsNoEditor` folder **only after** full/acceptance packaged startup passes. The artifact is a Windows playable **candidate**, not automatically a finished or visually approved chapter.
- Exact-head CI, ZIP/artifact upload result, integration of warehouse Poly Haven PBR, hero animation, chapter-specific PIE, target 720p/30 FPS and human visual Gate 6/7 **remain unproven as of commit authoring**. Warehouse Run #38042482514 remains independently checkpointed; no second warehouse writer is launched.
- No C++ modifications; after CI the next user-visible result must be a working Windows candidate download if and only if GitHub Actions created it.

## 2026-10-10 — one coordinated P1C01 source warehouse production batch (99 FBX originals)

- Owner requested one completion batch rather than repeated administrative waves. Added `Data/P1C01TwoWaveWarehouseActivationV1.json` and push-triggered `.github/workflows/p1c01-two-wave-checkpoint-warehouse.yml`: exact-head single-writer Windows runner uses previously produced pinned GitHub Artifacts, 20-case plus legacy offline regression tests, 4 MiB SHA256/fsync recovery, wave39 persisted/audited before wave60 begins, no second provider download or rollback of wave39.
- Evidence status on commit creation: **PENDING new workflow run**. Wave39 and wave60 persistent receipts/audits are required; prior source conversion evidence is reusable, not a substitute. No UE import, player rig/animation, chapter PIE, device FPS or human visual acceptance is claimed. Existing acceptance gates remain unchanged.
- Canon/source boundary: Source 07 F1-01 birthday/party and Ring outcome; current P1C01 includes broader Shire/road runtime, so do not relabel later F1-02/F1-03 source outcomes as independently accepted.

## 2026-10-10 — P1C01 recovery convergence on PR #335 (source-only)

- Recovery source and network-free 20-case fault-injection suite are reused from validated side branch commit `8c5b296bd4cd024745f3666ce45802ea0e74f004` (prior Linux+Windows https://github.com/4youbabee-tech/fellowship-personal-game/actions/runs/38007549312 SUCCESS). An exact-merged-head rerun is **PENDING**; no fresh result is asserted before it finishes.
- The pinned 39-asset warehouse workflow now runs the network-free suite before any checkpoint download; existing single-writer concurrency and the 6 GiB storage reserve remain unchanged. Wave39 actual durable intake/audit is **NOT YET PROVEN**; wave60 stays separate and gated.
- No UE4 C++/runtime/content assets were modified by this change: no repeated Unreal build, import, PIE, device or visual acceptance is claimed. P1C01 remains open, Gate 6/7 pending. PR #335 production metadata from prior head is preserved.

## 2026-10-10 P1C01 checkpoint transport and source-only UE evidence reuse gate

- On PR #335 exact head `ce8faa666d368f11b868963e85aecf8c7cda351d`, Pre-Unreal #38003230133 SUCCESS, Five-Lane #38003230032 SUCCESS, UE4 #38003230111 SUCCESS incl Editor and package; no need to rebuild this source revision merely to stage external CC0 artifacts. Source-only PBR had 39/39 and 59/60 conversions at proven earlier runs, not UE imported.
- Source-only correction: added nine synthetic power/network-loss, corrupt-checkpoint, SHA256, ZIP safety and resume/no-double-fetch tests; tests must pass hosted CI before transferring large artifacts. Newly approved classifier checks only immediate-parent delta for an explicitly restricted set of source-only scripts/workflows/governance docs, verifies exact-parent full Unreal workflow SUCCESS via GitHub and chooses `inherit` only if both prove safe. This prevents cumulative PR diff from reclassifying successful source-only changes as new full UE compiles. Runtime changes still take existing full/core routes.
- Persistent checkpoint code remains unproven until the real Windows runner writes and verifies 4MiB chunks, full Artifact SHA256, source receipts and <=6GiB reserve. Manual single-writer wave39 persists before any wave60; Gate6/7 P1C01 not accepted. If hosted regression fails, repair it before dispatch; do not run another 75-minute all-artifact download.

## 2026-10-10 — Durable 4MiB restart checkpoints and no repeated expensive PR-wide acquisition

- Owner observed electricity/network instability and rejected repeated long downloads/builds. Root cause: GitHub PR path filters saw entire PR diff, retriggering expensive 39-PBR conversion and 60-model acquisition for governance-only commits. Two duplicated self-hosted warehouse writers also contended for one runner; 75-minute download canceled before writes.
- Corrective source-only transport `Scripts/resume_p1c01_artifact_checkpoint.py`: pinned source GitHub Actions artifact ID, exact archive byte length and SHA256; 4 MiB range transfers with per-chunk SHA256 journal in permanent warehouse, fsync and atomic checkpoint writes. Reuse completed chunks, re-fetch uncommitted tail only, fail closed on tampering, 6GiB free reserve and pinned archive SHA256. Whitelisted ZIP entry extraction with atomic CRC-checked files and durable extracted-state receipt. No provider re-download, UE4 import or visual claim.
- Exactly one manual serialized source-only warehouse job for wave39: check existing SHA256 first, recover 39 source and PBR chunks, persist 39 and run canonical warehouse audit. Separate 60 wave reserved for independent follow-up after first checkpoint. Removed automatic pull_request triggers from expensive **adaptive 39-PBR and 60-source** workflows, while five-lane *read-only* regression remains eligible. No re-execution of existing expensive successful workflows on unrelated changes.
- **Acceptance boundary:** workflow design change and manifest only until actual hosted regression and Windows warehouse logs. No permanent source promotion or P1C01 Gate6/7 acceptance claimed.

## 2026-10-10 — 75-minute warehouse Artifact download failure; remove duplicate writer and split durable checkpoints

- GitHub #37990910312 CANCELLED after 75 minutes: source 39 artifact took ~25m; PBR39 ~2.5m; source60 ~19m; PBR60 421,901,298-byte download ran 27m45s before cancellation. The first persistent commit and inventory audit were SKIPPED. No new persistent asset claim. Deprecation warning is not established cause.
- Corrected process: dedicated warehouse writer is manually dispatched only and operates on 39-source wave first. Full SHA256 existing-wave check skips already-stored files; two necessary verified artifacts are fetched only if missing; commit wave39 and run warehouse inventory audit immediately. Separate 60-source followup only after successful durable wave39, not part of long four-download job. Removed duplicate warehouse writer from five-lane preflight. Add offline no-network regression tests for staging, reuse, source/receipt corruption, and path attacks.
- Follow-up GitHub exact-head tests PENDING. The existing long-run failure is confirmed; final Gate6/7 remains UNACCEPTED, P1C02 CLOSED.

## 2026-10-09 — Persistent source writer Python Runner PATH failure and exact fix

- Workflow #37990747432 attempted serialized stage but failed **before downloading or writing assets**: actual step line `Python was not found; run without arguments to install from the Microsoft Store` on self-hosted Windows. The machine's previous UE run #37988147537 exposes installed toolchain `D:\\actions-runner\\_work\\_tool\\Python\\3.11.9\\x64\\python.exe`; writer workflow must resolve a known existing Python binary and persist the exact path to GITHUB_ENV, not depend on `python` App Execution Alias. Other source-only prep continues independent. Next exact-head workflow must demonstrate full receipt/hash copy and warehouse inventory audit; no persistent-stage success claimed yet.

## 2026-10-09 — 99 source FBX recovery wave, 98 PBR-ready source conversions and guarded persistent warehouse intake

- Exact-head PR #335 @ `08787c07`: source #37988147489 SUCCESS `P1C01_ADAPTIVE_SOURCE_STAGE eligible=183 staged=60 files=315 bytes=502931425 quarantine=123; NOT_UE4_IMPORTED`; conversion in same run SUCCESS `prepared=59 png=211 quarantined=1 NOT_UE4_IMPORTED`. The other 39 models are reused via prior artifact, not re-downloaded.
- Previous 39 converted in #37988147700 SUCCESS: `P1C01_ADAPTIVE_PBR_QC prepared=39 png=146 quarantined=0 NOT_UE4_IMPORTED`. The held extra dry diffuse is source-only, not an invented normal map. Combined original models 99; PBR-prepared 98; quarantine 1. Artifacts expire in 30 days.
- Unreal run #37988147537 SUCCESS exact head; Editor compile, existing production import, automation, headless P1C01 sweep, world-state roundtrip, packaging, startup. Log `W00_PACKAGE_PASS` and `W00_PACKAGED_STARTUP_PASS`; warning debt passed. This run does NOT import the new 99 external Poly Haven FBX.
- Add `Scripts/stage_p1c01_adaptive_pbr_warehouse.py` and manual dispatch `.github/workflows/p1c01-persistent-verified-pbr-warehouse.yml`: one self-hosted writer guarded by the existing `warehouse-stage-` concurrency name. Reuses 4 numbered Artifacts and checks original source license/source-page, file inventories, per-file size/MD5/SHA256, binary FBX, prepared 1K PNG dimensions/hash, matching source receipt hash, quarantines and double-staging. Copies originals and generated sources to transaction directory, creates SHA256/licensing receipts, preserves 6 GiB free-space reserve, atomically promotes same-volume source wave and runs existing inventory audit. No paid assets, no provider downloads, no deletion of existing valid warehouse files, no claimed runtime imports.
- **Unproven until dispatch logs**: persistent warehouse write and audit. Next real blocker: 99 FBX require UV/geometry/tangents/collision/LODs and visual matching before source-to-runtime import. Major hero Gandalf/Bilbo/Sam/Merry/Pippin rig/final presentation and human P1C01 DX11 720p 30FPS Gate 6/7 remain open. P1C02 remains CLOSED.

## 2026-10-09 — P1C01 39-source integrity audit, nettle dry-map recovery and no-redownload wave two

- **Observed exact-head evidence:** PR #335 @ `fac5bba5fac633ed9989d3b5f180b46b3ed43817`: CC0 source run 37985180302 SUCCESS (artifact 11643315007); PBR run 37985180453 SUCCESS (artifact 11641884955; `P1C01_ADAPTIVE_PBR_QC prepared=38 png=142 quarantined=1 NOT_UE4_IMPORTED`); Five-Lane Preflight 37985180297 SUCCESS; Pre-Unreal 37985180289 SUCCESS; UE4 run 37985180287 SUCCESS, including existing production import, Editor build, Automation, Windows package and packaged startup.
- **Independent read-only ZIP audit:** all 211 files spanning 39 original Poly Haven CC0 source models matched size/MD5/SHA256; all 142 previously converted PNGs matched SHA256 and 1024x1024. Original `nettle_plant` quarantine was caused by `nettle_plant_dry_diff_1k.png`, a secondary BaseColor-only variation with no independent normal/roughness; source normals must never be invented.
- **Follow-up code wave — exact-head CI pending:** convert the complete nettle primary PBR group, preserve the optional dry variant as a separate PNG with `HOLD_MATERIAL_VARIANT_NO_INDEPENDENT_NORMAL_ROUGHNESS` and source SHA256 (not UE import-eligible), require 39/39 prepared and zero quarantined after revalidation. Expand the next hosted Poly Haven source shard up to **480 MiB total / 30 MiB per source file / 660 seconds** with no arbitrary asset-count cap, hash-verify the existing 39 from prior GitHub Artifact and explicitly exclude them before new provider requests. New shard conversion is dependent on successful intake, while other hosted tracks stay independent.
- **Boundaries:** this is generated **source-only**; GitHub Artifacts have 30-day retention and are not persistent warehouse receipts. Exactly one persistent warehouse writer and >=6 GiB free reserve remain mandatory; none of these candidates proves UE geometry/UV/LOD/collision, hero skeletal animation, playable scenes, pacing, PIE, target-device DX11 720p/30 FPS or human Gate 6/7 acceptance. P1C02 remains closed.

## 2026-10-09 — Expanded P1C01 CC0 asset wave: 39 real FBX, now source-only PBR conversion

- GitHub hosted adaptive source stage #2 `37979256311` SUCCESS exact SHA `17aa93bf`. Actual log `P1C01_ADAPTIVE_SOURCE_STAGE eligible=222 staged=39 files=211 bytes=251537607 quarantine=183; NOT_UE4_IMPORTED`. Confirmed ZIP Artifact **11640236408**, 245,957,831 compressed bytes: 39 FBX + 172 original EXR/JPEG/PNG textures. Of the 183 non-staged, **159 exceeded per-wave remaining budget and were deferred; 24 had a file >30MiB**. These do not represent 183 bad source files.
- New `Scripts/prepare_p1c01_adaptive_pbr.py`, `Scripts/test_p1c01_adaptive_pbr.py` and hosted `.github/workflows/p1c01-adaptive-pbr-prep.yml` reuse the exact successful artifact **without provider/network acquisition, Git LFS or Unreal**; source SHA256/MD5 and inventory must match the receipt. Convert 1K BaseColor, DirectX green-flipped normal, R-AO/G-roughness/B-metallic masks plus 16-bit-safe alpha where present to PNG; preserve FBX bytes. Per-asset quarantine preserves source-only packet integrity.
- Four non-Shire tropical candidates (`anthurium_botany_01`, `calathea_orbifolia_01`, `didelta_spinosa`, `pachira_aquatica_01`) explicitly biome-held; two ambiguous identities held. Other source candidates still need static FBX geometry/UV/smoothing/tangent, LOD/collision, material import and quality/performance review. **No new UE imports or visual acceptance claimed**.
- Conversion Hosted exact-head run/test proof **PENDING** after this commit. Existing five parallel hosted preflights and UE4 #1821 are successful but not P1C01 Gate 6/7/DEVICE acceptance. The existing #329 remains sole runtime integration; all future library preparation may run independently.

## 2026-10-09 — Adaptive wave minimum-remaining-byte guard correction

- Static regression fixture for the new adaptive source wave uses 100,000 bytes of available storage; guard must not assume every candidate consumes >=1 MiB. Correct early-stop bound to <1024 remaining bytes, leaving the **actual per-file provider-size and overall byte caps** authoritative. This fixes exact source-layer gating rather than reducing testing or attempting unbounded retries.
- The hosted source-only workflow remains required to pass its own exact HEAD before any new staged asset receipts count as evidence; no UE4 build requested by this corrective commit.

## 2026-10-09 — Dynamic source acquisition beyond fixed five-model pilot

- New selectively searched P1C01 high-fidelity **Poly Haven official CC0** source-only workflow `.github/workflows/p1c01-adaptive-highfidelity-source.yml`, backed by `Scripts/stage_p1c01_polyhaven_adaptive.py` and five no-network tests. Selects matching Shire outdoor, rustic architecture, vegetation, stones, garden and prop model metadata from provider's public API, excludes five previously staged models, then acquires 1K native static FBX and original texture dependencies. Each asset receives provider MD5 verification + SHA256 receipt; rejects traversal, invalid extension/host, malformed sources and oversize payloads.
- **Real safety-driven scaling:** no arbitrary five-asset source limit; hosted wave limited by **240 MiB total source bytes, 30 MiB/file and 420 seconds** (plus GitHub 14-minute job), with per-asset quarantine and source-only artifact. Counts depend on actual suitable free provider content and cannot be claimed before the new run. Exceeding single-shard budget defers candidates rather than silently promoting them; future successful waves should process deferred candidates by verified resume/source checksums, never automatic blind redownload.
- Originals may contain JPEG/EXR source dependencies; these remain SOURCE_STAGED only pending PNG/TGA conversion and FBX geometry/UV/smoothing/LOD/collision/import review. This workflow does NOT persistently mutate the shared warehouse, change UE Content, open P1C02 or establish target-device 30 FPS. Repository still uses the 6 GiB single-writer warehouse free-space safety reserve.
- Five-lane hosted metadata preflight #1 was successful; on this commit the new adaptive acquisition/workflow status is **PENDING** until GitHub returns actual receipt/artifact. SOURCE != READY_FOR_IMPORT != VISUALLY_ACCEPTED.

## 2026-10-09 — Five hosted tracks live, precise PG-078 root repair

- New owner-confirmed DEC-104 / PR #335 first exact-head run [five-lane #1](https://github.com/4youbabee-tech/fellowship-personal-game/actions/runs/37978590310) **SUCCESS** on `e22434b812b71a20ba9375e71d7fc54e74baa486`: five distinct hosted matrix jobs completed successfully and published five source-only metadata reports, without Git LFS, UE4 or warehouse mutation.
- Concurrent Pre-Unreal [#2225](https://github.com/4youbabee-tech/fellowship-personal-game/actions/runs/37978590228) **FAILED** PG-078 `tracked unfinished requirement snapshot is stale` because REQ-PROD-011 gained a concrete missing-work tracking entry while `Data/MasterExecutionRoadmap.json.tracked_unfinished_requirement_ids` was not synchronized. The requirement was already mapped to `CONTINUOUS_MAXIMUM_SAFE_PRODUCTION`; this commit regenerates the tracked unfinished-ID snapshot from the exact Governor (60 entries), without disabling, weakening or changing validator semantics.
- **Revalidation pending** on the new exact HEAD. Five-lane PASS is source/read-only coordination proof, not binary warehouse upload or visual completion. Only serialized valid source intake may place eligible new files into persistent warehouse.

## 2026-10-09 — Owner-confirmed permanent five-lane maximum-safe throughput

- Direct live `develop` Governor review found **REQ-PROD-011 and DEC-078 already active**: throughput must be adaptive and maximal by default without further owner reminders. **DEC-104** explicitly groups existing preparation work into five independent operational tracks: serialized UE4 runtime; serialized persistent warehouse and legal asset intake; skeletal characters/animation; realistic visual Shire world; and gameplay/NPC/quest/save/audio/Arabic presentation.
- Candidate branch adds `Scripts/p1c01_five_lane_preflight.py` and five-way parallel hosted runner workflow `.github/workflows/p1c01-five-lane-maxsafe.yml`. Runs every lane against the exact PR SHA with **no Git LFS, Unreal, persistent warehouse write, login bypass, or synthetic claims of new downloads**; all eligible metadata candidates and existing 180 visual slots are scanned and five source-only receipt artifacts published. The existing single serialized UE and warehouse workflows remain responsible for mutating their resources; no duplicate runner contention.
- Maximum file intake is **not** unbounded single-job ZIP/VRAM/residency; follow `Data/MaximumSafeProductionModeV1.json` with >=6GiB warehouse reserve and measured per-file/wave/network/provider/artifact budgets. The warehouse source catalogue and existing legal source pipelines remain the actual acquisition path. Source/library inventory scales independently from the 2GB VRAM runtime working set.
- At authoring, exact-head hosted proof is **PENDING**. This wave itself does not import new FBX, produce new cinematic content, complete the Shire, or satisfy Gate 6/7. Keep P1C02 runtime closed. Existing PR #329 Unreal lane and #332 photoreal intake lane continue independently.

## 2026-10-01 - Critical-gap receipt parity matrix

| Area | Status | Evidence / boundary |
|---|---|---|
| Canonical Warehouse inventory | RUN-PROVEN CLEAN | #306: 18,925 payloads / 6,745,968,858 bytes / 239 active / 428 superseded / 0 integrity failures |
| Critical-gap receipt selection | SOURCE-REPAIRED / EXACT-HEAD PROOF PENDING | Same canonical root and newest-receipt rule as inventory audit |
| Same-receipt duplicates | PRESERVED | Counted separately from historical supersession |
| Newest active receipt corruption | FAIL-CLOSED | SHA256/missing-file preflight remains blocking and regression-covered |
| Runtime / Frodo / Gate 6-7 maturity | UNCHANGED | No human/device or visual acceptance supplied |

## 2026-10-01 - PG-207 fixture boundary

| Area | Status | Evidence / boundary |
|---|---|---|
| Operational runner / Warehouse root | D-root required | Any live C-root occurrence remains a validation failure |
| Historical C-root test fixture | SOURCE-IMPLEMENTED | Exactly one canonical fixture literal permitted only in receipt-supersession test |
| Broader C-root allowlist | FORBIDDEN | Scripts/workflows/configuration remain fail-closed |
| Exact-head validation | PENDING | Requires re-run after validator correction |

## 2026-10-01 - Warehouse real-path canonicalization correction

| Area | Status | Evidence / boundary |
|---|---|---|
| Real `C:\actions-runner\...` receipt paths | SOURCE-REPAIRED / EXACT-HEAD PROOF PENDING | Single Windows separators now canonicalize to active `D:\actions-runner\_warehouse\ShireJourney` root |
| Regression fixture | SOURCE-IMPLEMENTED | Uses real single-backslash Windows path, not a C-style doubled representation |
| Missing snow / mismatched rock records | FAIL-CLOSED PENDING TARGETED REPAIR | Candidate staging may repair only those payloads |
| Blanket material refresh | FORBIDDEN | Existing verified payloads preserved |
| Gate 6-7 and human/device acceptance | NOT ACCEPTED | Separate evidence required |

## 2026-10-01 - Warehouse candidate trigger hardening matrix

| Area | Status | Evidence / boundary |
|---|---|---|
| Candidate gate activation | SOURCE-IMPLEMENTED / EXACT-HEAD PROOF PENDING | Relevant Warehouse push invokes bounded provenance repair and candidate report without merge-subject matching |
| Receipt integrity and payload reuse | PRESERVED | SHA256 verification; only missing or mismatched payload is redownloaded |
| Broad refresh | FORBIDDEN | No `-Refresh` in the candidate gate |
| Frodo/Gandalf report and artifact | PENDING | Requires successful exact-head Warehouse execution |
| PIE / device / visual / pacing / performance / Gate 6-7 | NOT ACCEPTED | Separate real evidence required |

## 2026-10-01 - Warehouse migrated-receipt root repair matrix

| Area | Status | Evidence / boundary |
|---|---|---|
| Active Warehouse root | RUN-PROVEN | Warehouse #304 used `D:\\actions-runner\\_warehouse\\ShireJourney` |
| Historical absolute receipt paths | SOURCE-REPAIRED / EXACT-HEAD PROOF PENDING | Rebased to the explicit audit root before grouping and SHA256/license checks |
| Valid payload preservation | REQUIRED / PRESERVED | No blanket refresh or deletion; newer receipts supersede migrated historical records |
| Genuine active-root corruption | FAIL-CLOSED / REGRESSION-COVERED | Newest active receipt hash mismatch still exits with audit failure |
| P1C01 runtime / Frodo candidate / Gate 6-7 | UNCHANGED | No runtime or human/device acceptance supplied by this CI repair |

## 2026-10-01 - P1C01 FOUNDATION_CORRECTIONS_V1

| Area | Status | Evidence / boundary |
|---|---|---|
| Canonical predecessor | MACHINE-GREEN | `develop@3ec3f725cb1dff42a762e36e39790b82a4801714`; post-#207 Pre-Unreal + Unreal Build SUCCESS |
| Persistent ambient social registration | SOURCE-IMPLEMENTED / EXACT-HEAD CI PENDING | Director-owned committed-world reconciliation; weak registry; no lifecycle transfer; bounded nearby query includes persistent residents |
| Per-NPC full-world social scan | FORBIDDEN / PRESERVED | No `TActorIterator` in `AShireAmbientNPC::UpdateSocialLife`; one reconciliation scan occurs only at committed-world synchronization |
| Pool ownership | PRESERVED | LivingWorld-managed baseline/micro-event NPCs remain pooled under `ALivingWorldDirector`; persistent builder-authored residents are not pooled by this repair |
| Footstep surface resolution | SOURCE-IMPLEMENTED / EXACT-HEAD CI PENDING | Grass/Dirt/Stone/Wood SurfaceTypes + physical-material-first resolution; legacy identity fallback retained |
| Hero animated source policy | GOVERNOR-ALIGNED | UE4.27 FBX 2018-compatible skeletal intake; OBJ remains static modular fallback only |
| Visual quality target | GOVERNOR-ALIGNED | Balanced Medium + selective High; 720p / 30 FPS low-spec floor retained |
| PBR expansion | NOT IMPLEMENTED BY THIS REPAIR | Existing scalar PBR remains; selective Normal/channel-packed acquisitions stay future bounded material work |
| Fauna/Niagara rewrite | NOT AUTHORIZED / NO EVIDENCE NEED | Existing bounded pooled fauna retained until profiling shows a bottleneck |
| Part II runtime expansion | FROZEN | Source-preparation workflows remain non-runtime evidence; P1C01 remains active runtime lane |
| PIE / device / visual / pacing / performance | NOT TESTED / NOT ACCEPTED | Requires separate exact-head human/device evidence |

## 2026-09-30 - P1C01 SAVE_LOAD_LONG_SESSION car

- SHIRE_AUDIO_IDENTITY predecessor: **EXACT-HEAD MACHINE-GREEN** on PR #199 / Pre-Unreal #1486 / Unreal Build #1159; merged as `ec96e9e487ecbe91d9563848f685df4bd5c11b0d`.
- Long-session persistence hardening: **SOURCE-IMPLEMENTED / EXACT-HEAD CI PENDING**.
- Production save/restore ownership: **UNCHANGED**.
- Restore transaction + committed-world transform grounding + async checkpoint revision guards: **PRESERVED**.
- Oversized/corrupt save payload admission: **FAIL-CLOSED BEFORE RESTORE MUTATION**.
- Serialization schema version: **UNCHANGED (v6)**; this car does not invent undocumented v1/v2 history or force a migration.
- Human long-session PIE, save/load stress, target-device hitch/memory behavior: **PENDING / NOT CLAIMED**.

## 2026-09-30 - P1C01 SHIRE_AUDIO_IDENTITY car

- CINEMATIC_CONTROL_HANDOFF predecessor: **EXACT-HEAD MACHINE-GREEN** on PR #198 / Pre-Unreal #1484 / Unreal Build #1157; merged as `3b38698c19a244fde8f2979d73f12cd829576b7f`.
- Shire sonic-identity runtime implementation: **SOURCE-IMPLEMENTED / EXACT-HEAD CI PENDING**.
- Runtime audio owner: **UNCHANGED — UShireAudioSubsystem**.
- Heavy/nonresident audio: **SOFT-PATH + ASYNC FStreamableManager**.
- Decorative localized SFX concurrency: **BOUNDED — max 6 starts / 0.25 s + existing 0.06 s per-cue repeat guard**.
- Story-critical one-shot priority over decorative burst budget: **SOURCE-IMPLEMENTED**.
- Final P1C01 WAV masters/import/listening/mix/master: **PENDING / NOT CLAIMED**.
- PIE/device/audio-listening/pacing/performance acceptance: **PENDING / NOT CLAIMED**.

## 2026-09-30 - P1C01 CINEMATIC_CONTROL_HANDOFF car

- QUEST_SIDE_ACTIVITY_COHERENCE predecessor: **EXACT-HEAD MACHINE-GREEN** on PR #197 / Pre-Unreal #1481 / Unreal Build #1154; merged as `e926889f9328e238afaffb16f9f9dabf58ce9040`.
- Cinematic control-handoff source implementation: **SOURCE-IMPLEMENTED / EXACT-HEAD CI PENDING**.
- Presentation state owner: **UNCHANGED — UShireStoryPresentationSubsystem**.
- Runtime camera owner: **UNCHANGED — AStoryPresentationDirector**.
- Quest/save/world-commit mutation by presentation: **FORBIDDEN / UNCHANGED**.
- Timed release, explicit skip and chapter-change release: **TARGETED TO ONE EXIT PATH**.
- Stale transient runtime camera after presentation unlock: **FORBIDDEN**.
- Authored external camera/Level Sequence ownership: **PRESERVED**.
- PIE skip/return behavior, target-device performance and human visual/pacing review: **PENDING / NOT CLAIMED**.

## 2026-09-30 - P1C01 QUEST_SIDE_ACTIVITY_COHERENCE car

- LIVING_SHIRE predecessor: **EXACT-HEAD MACHINE-GREEN** on PR #196 / Pre-Unreal #1478 / Unreal Build #1151; merged as `a478127559ab54f0ec938377a4962e6a75479d36`.
- Quest/side-activity coherence implementation: **SOURCE-IMPLEMENTED / EXACT-HEAD CI PENDING**.
- Quest/story ownership: **UNCHANGED — UShireQuestSubsystem only**.
- Safe-window projection: **SOURCE-IMPLEMENTED** through `GetAvailableSideActivityIdsForCurrentWindow()`.
- P1C01 main-quest urgency suppression: **SOURCE-IMPLEMENTED** for RingSecret / LeavingHome / KeepOffRoad / FerryEscape.
- Side-activity duplicate reward prevention: **SOURCE-IMPLEMENTED / explicit guard + existing discovery idempotence**.
- Locked story outcomes / required anchors: **UNCHANGED**.
- PIE optional-window pacing, save/load behavior, target-device performance and human review: **PENDING / NOT CLAIMED**.

## 2026-09-30 - P1C01 LIVING_SHIRE

| Area | Status | Evidence / boundary |
|---|---|---|
| Predecessor CHARACTER_PRESENTATION | EXACT-HEAD MACHINE-GREEN / MERGED | PR #195; head `24ffa0ddb35756a606fb166d010b1e7ca2940308`; Pre-Unreal #1475 SUCCESS; Unreal Build #1148 SUCCESS; merge `66caf6168157e0ec171a1e7249ead245e45d8b42` |
| Bounded NPC context snapshot | SOURCE-IMPLEMENTED / EXACT-HEAD PROOF PENDING | `FShireNPCBehaviorSnapshot`, `UShireNPCContextSubsystem::BuildBehaviorSnapshot` |
| Bounded social candidate query | SOURCE-IMPLEMENTED / EXACT-HEAD PROOF PENDING | `ALivingWorldDirector::GatherActiveAmbientNPCsNear`; no per-NPC full-world social iterator |
| Fauna group admission cap | SOURCE-IMPLEMENTED / EXACT-HEAD PROOF PENDING | existing LivingWorldEventPlan cap 2 loaded/enforced before FAUNA event selection |
| Pool ownership | PRESERVED IN SOURCE / EXACT-HEAD PROOF PENDING | AmbientNPC, interaction and ambient-motion pools remain under LivingWorldDirector |
| P1C01 population | UNCHANGED | baseline target 18 |
| Story/canon ownership | PRESERVED IN SOURCE | ShireQuestSubsystem remains progression truth; ambient behavior cannot own locked outcomes |
| PIE / device / visual / pacing / performance | NOT TESTED / NOT ACCEPTED | Requires separate chapter-specific human/device evidence |

## 2026-09-30 - P1C01 CHARACTER_PRESENTATION car

- PARTY_AND_SOCIAL_LOOP predecessor: **STATIC-VALIDATED + UE4.27.2/headless machine-green** on PR #194 / Pre-Unreal #1472 / Unreal #1145.
- Character presentation implementation: **SOURCE-IMPLEMENTED / EXACT-HEAD CI PENDING**.
- Stable hero identity: **DATA/C++ WIRED** through `AShireNPC::ProductionCharacterId`; P1C01 Gandalf/Bilbo/Sam story actors no longer depend on display-name identity.
- Player canon presentation: **P1C01 Frodo future named sword fallback hidden**; no locked story outcome changed.
- Skeletal rig path: **EXISTING ASYNC OWNER RETAINED** via `UShireChapterAssetStreamingSubsystem` / `FStreamableManager`; modular fallback remains until complete mesh + AnimBP resolution.
- Low-spec skeletal controls: **URO + OnlyTickPoseWhenRendered retained**.
- Ambient AI population: **UNCHANGED at 18**.
- New AI subsystem / per-frame asset scan / synchronous heavy production load / crowd Spawn-Destroy churn: **NONE**.
- PIE silhouette/equipment continuity, skeletal deformation/animation, target-device FPS/frame-time/hitches/RAM/VRAM and human visual review: **PENDING / NOT CLAIMED**.

## 2026-09-30 - P1C01 SHIRE_WORLD_DENSITY car

- Predecessor PR #189 exact head `3680ab2fa52b7ebd7ec896ec10d2d2f9a60dd63c`: **STATIC-VALIDATED by Pre-Unreal #1465 + COMPILE/headless machine-green by Unreal Build #1138**.
- LivingWorld member-local cull repair: **EXACT-HEAD MACHINE-GREEN on PR #189**.
- SHIRE_WORLD_DENSITY source implementation: **SOURCE-IMPLEMENTED / EXACT-HEAD CI PENDING**.
- AI population: **UNCHANGED at P1C01 target 18**.
- Added density budget: **<=5 zero-Tick HISM clusters / <=70 non-collision decorative instances**; resident production meshes only; missing categories skip without load.
- Story/quest topology: **UNCHANGED**.
- PIE traversal/readability, target-device FPS/frame-time/hitches/RAM/VRAM, visual density and pacing: **PENDING / NOT CLAIMED**.

## 2026-09-30 - W00 machine closure / P1C01 mega train V2

- Exact acceptance head: `d6ca8aac03f5a1da07609e61e790ddf8faad8eed`.
- Pre-Unreal #1435: **SUCCESS**.
- UE4.27.2 Unreal Build #1108: **SUCCESS**, including C++ build, production import, Automation, startup, chapter audit, route/state roundtrip, warning debt, Windows package, packaged Data verification and packaged executable observation.
- Runtime Data staging: **RUN-PROVEN 37/37**.
- Packaged runtime Data consumption: **RUN-PROVEN** via `NPCContext: ready=yes`.
- LivingWorld member-local cull repair in mega V2: **EXACT-HEAD MACHINE-GREEN on PR #189 / Pre-Unreal #1465 + Unreal #1138**.
- P1C01 mega-build program: **REGISTERED / preparation active / dependent runtime cars remain Governor-gated**.
- Target-device FPS/frame-time/VRAM, chapter-wide human PIE, audio listening/mix and visual acceptance: **PENDING / NOT CLAIMED**.

## 2026-09-30 - W00 packaged runtime Data-read proof guard

- Packaged RuntimeDependencies staging/JSON syntax guard: **IMPLEMENTED**.
- Packaged executable Data-consumption guard: **SOURCE-IMPLEMENTED / EXACT-HEAD CI PENDING**, requiring `NPCContext: ready=yes` during packaged startup.
- This is acceptance evidence hardening only; chapter production maturity is unchanged.
- P1C01 PIE/device/performance/audio-listening/visual acceptance remains pending and is not promoted by this guard.

## 2026-09-30 - Final zero-ahead maintenance sweep

- Remaining maintenance refs before sweep: **2**.
- Post-sweep expected persistent refs: **develop + main + recovery-only archive**.
- Branch cleanup lifecycle: **EXACT MERGED-HEAD DELETE + EXPLICIT ORPHAN DELETE**.
- Build resume after cleanup success: **AUTHORIZED FROM CANONICAL develop**.
- Gameplay/compile/PIE/device/visual/performance maturity: **UNCHANGED / NOT CLAIMED**.

## 2026-09-30 - Last orphan ref closeout

- Legacy archived working refs: **26 / 26 DELETED by Branch Cleanup #178 closeout**.
- Recovery anchor: **PRESERVED** at `archive/pre-build-salvage-20260930`.
- Superseded PR #179 maintenance ref: **QUEUED FOR FINAL GUARDED DELETE**.
- Expected branch set after this merge cleanup: **develop + main + one recovery-only archive ref**.
- Gameplay/compile/PIE/device/visual/performance maturity: **UNCHANGED / NOT CLAIMED**.

## 2026-09-30 - Final branch-hygiene gate before construction resume

- Legacy branch histories captured in recovery archive: **26 / 26 heads captured**.
- Recovery archive: **`archive/pre-build-salvage-20260930@a47eda59f31352676de44777845fbc01c38d2d0d`**.
- Captured legacy working refs: **QUEUED FOR GUARDED POST-MERGE DELETE**.
- Expected persistent refs after cleanup: **develop + main + recovery archive**.
- Production/PIE/device/visual/performance maturity: **UNCHANGED / NOT CLAIMED**.

## 2026-09-30 - Infrastructure hygiene closeout

- Active runner root: **RUN-PROVEN on `D:\\actions-runner`** from prior GitHub health evidence; owner-side final cleanup reports old C runner residue absent.
- Persistent Warehouse root: **`D:\\actions-runner\\_warehouse\\ShireJourney`**.
- Hosted Pre-Unreal / Branch Cleanup routing: **SOURCE/GOVERNANCE RECONCILED** with current workflow truth.
- Exact merged-head branch deletion + moved-head guard + zero-ahead prune: **SOURCE-IMPLEMENTED / exact-head CI proof pending on this maintenance wave**.
- Gameplay/PIE/device/visual/performance maturity: **UNCHANGED / NOT CLAIMED**.

## 2026-09-30 - Runner root migration evidence

- Self-hosted runner root: **RUN-PROVEN on `D:\\actions-runner`**.
- Warehouse default root: **MIGRATED to `D:\\actions-runner\\_warehouse\\ShireJourney`**.
- Interactive watchdog/service-exclusion topology remains the required execution model.
- GitHub health evidence includes `RUNNER_HEALTH_WORKSPACE_PASS temp=D:\\actions-runner\\_work\\_temp` and `RUNNER_HEALTH_PASS`.
- This infrastructure evidence does not promote any gameplay, PIE, visual, device-performance, or chapter maturity status.

## 2026-09-29 - Hero skeletal candidate diagnostic note

- First post-merge candidate workflow failed during candidate construction after checkout/runner/preflight success.
- Diagnostic output is added without relaxing FBX/provenance/skeleton/skin/retarget/deformation gates.
- Character visual-completion status remains unchanged.


## 2026-09-29 - F2-04 Road & Helm's Deep Prep source-preparation note

- F2-04 has a maximum-safe source architecture with 36 categories / 19 landmarks / 9 banks and PG-206 protection.
- This wave preserves refugee movement, fortress orientation, civilians, supplies and defense preparation while keeping F2-05 combat closed.
- It does not promote Part II runtime chapter maturity or Gate 6/7 status.
- Runtime ID remains NOT_ASSIGNED_DO_NOT_INVENT.
- No PIE/device/visual/performance acceptance is added by this wave.

## 2026-09-29 - P1C01 hero skeletal candidate preparation

- Frodo/Gandalf real-character work advances from generic rig staging to an explicit ranked FBX candidate/QC wave.
- This is not a visual-completion promotion: all candidates remain QC_REQUIRED and not READY_FOR_IMPORT by default.
- P1C01 stays the sole runtime-changing chapter lane; candidate discovery stays preparation-only until an explicit bounded UE4 import/integration step.
- No PIE/device/visual/performance acceptance is added by this wave.

## 2026-09-29 - F2-03 Edoras source-preparation note

- F2-03 has a maximum-safe source architecture with 32 categories / 20 landmarks / 8 banks and PG-204 protection.
- This wave expands source preparation only. It does not promote Part II runtime chapter maturity or Gate 6/7 status.
- The chapter is governed by the permanent no-story-shortcuts / zero-silent-omission contract.
- Runtime ID remains NOT_ASSIGNED_DO_NOT_INVENT.
- No PIE/device/visual/performance acceptance is added by this wave.

## 2026-09-29 - F2-02 exact-head CI routing repair

- The first reconciled Pre-Unreal run failed at PG-203 tooling-filter coverage, not at canon/runtime/source-content validation.
- Unreal source-only filters are corrected for both push and PR paths.
- No chapter completeness or runtime acceptance status changes.

## 2026-09-29 - F2-02 reconciliation note

- F2-02 source-preparation metadata/tooling is reconciled with the permanent story/source rules without changing runtime chapter maturity.
- F2-02 remains SOURCE/PREPARATION ONLY and is not assigned a Part II runtime ID.
- DEC-083 owns the F2-02 source wave after DEC-081/DEC-082 were assigned to permanent story/source and localization governance.
- No production-completeness row is promoted to PIE/device/visual/performance accepted by this reconciliation.

## 2026-09-29 — Story/source completeness and localization governance note

- Story/source completeness definition is strengthened without promoting runtime maturity: chapter planning must route Timeline -> film/screenplay -> Tolkien narrative/Appendices -> Sources 02-11 and explicitly disposition meaningful discovered detail.
- Compatible Tolkien book-only content may be real gameplay when it preserves required film outcomes; the Timeline is not a detail ceiling and Gate 6/7 is not permission to shorten planned story coverage.
- Localization contract is now explicit: English VO, Arabic subtitles/UI/objectives, canonical English map location labels, correct RTL rendering.
- This governance/onboarding wave changes **no chapter production status** in the matrix and supplies no new PIE/device/visual/performance evidence.

## 2026-09-29 - F2-01 Three Hunters / Captives maximum-safe source wave

- Canonical F2-01 scope: **REGISTERED**.
- Part II runtime ID mapping: **UNASSIGNED / DO NOT INVENT**.
- Mission/story/world source verification: **SOURCE-REVIEWED**.
- F2-02 later-state exclusion: **PRESERVED**.
- 38-category / 8-bank / 28,000-candidate manifest: **SOURCE-IMPLEMENTED**.
- 17 configured landmark categories / minimum 14 ready: **SOURCE-IMPLEMENTED / EXECUTION PENDING**.
- Minimum 7 of 8 banks ready: **SOURCE-IMPLEMENTED / EXECUTION PENDING**.
- Fair-share candidate scheduling: **SOURCE-IMPLEMENTED**.
- FBX-only animated candidates / PNG-TGA texture policy / BMP rejection: **SOURCE-IMPLEMENTED**.
- Clean warehouse inventory + 6 GiB reserve gate: **SOURCE-IMPLEMENTED**.
- Dedicated 180-minute source workflow: **SOURCE-IMPLEMENTED**.
- PG-202 runtime-ID/source regression guard: **SOURCE-IMPLEMENTED**.
- Part II runtime integration: **BLOCKED UNTIL EXPLICIT RUNTIME-ID MAPPING + EXISTING RUNTIME GATES**.
- Exact-head Pre-Unreal: **PENDING**.
- Heavy F2-01 source execution: **PENDING CLEAN-INVENTORY RUN**.
- PIE/device/visual/pacing/performance acceptance: **NOT CLAIMED**.

## 2026-09-29 - F1-08 Amon Hen / Breaking of the Fellowship maximum-safe source wave

- Canonical F1-08 / P1C08 mapping: **REGISTERED / NO RUNTIME RENUMBERING**.
- Mission/story/world/character source verification: **SOURCE-REVIEWED**.
- Boromir tragic/redemptive guardrail: **PRESERVED**.
- 34-category / 7-bank / 24,000-candidate manifest: **SOURCE-IMPLEMENTED**.
- 18 configured landmark categories / minimum 14 ready: **SOURCE-IMPLEMENTED / EXECUTION PENDING**.
- Minimum 6 of 7 banks ready: **SOURCE-IMPLEMENTED / EXECUTION PENDING**.
- Fair-share candidate scheduling: **SOURCE-IMPLEMENTED**.
- Multi-bank future runtime residency blueprint: **SOURCE-IMPLEMENTED / RUNTIME NOT OPEN**.
- FBX-only animated candidates / PNG-TGA texture policy / BMP rejection: **SOURCE-IMPLEMENTED**.
- Clean warehouse inventory + 6 GiB reserve gate: **SOURCE-IMPLEMENTED**.
- Dedicated 180-minute source workflow: **SOURCE-IMPLEMENTED**.
- PG-201 regression guard: **SOURCE-IMPLEMENTED**.
- P1C08 runtime integration: **BLOCKED UNTIL P1C07 GATE 6/7 ACCEPTED**.
- Exact-head Pre-Unreal: **PENDING**.
- Heavy F1-08 source execution: **PENDING CLEAN-INVENTORY RUN**.
- PIE/device/visual/pacing/performance acceptance: **NOT CLAIMED**.

## 2026-09-29 - Adaptive Maximum Safe Production Mode V1

- Maximum-safe production governance (`DEC-078` / `REQ-PROD-011`): **SOURCE-IMPLEMENTED**.
- Machine-readable capacity/execution plan: **SOURCE-IMPLEMENTED**.
- Whole-game queue maximum-safe mode: **SOURCE-IMPLEMENTED**.
- Master roadmap stale W00 control-state reconciliation: **SOURCE-IMPLEMENTED**.
- Parallel preparation lanes + single runtime lane: **GOVERNED**.
- Persistent warehouse single-writer rule: **GOVERNED**.
- Warehouse #286 active-receipt inventory audit: **PASS — 18,697 payload files / 6,688,457,009 bytes / 239 active / 428 superseded / 0 duplicate hash groups**.
- Warehouse #286 full workflow: **FAILED AFTER CLEAN AUDIT — SATURATION REPORT STRICTMODE EMPTY-SUM DEFECT**.
- Empty-safe saturation byte aggregation: **SOURCE-REPAIRED**.
- Saturation empty-lane regression test in Pre-Unreal: **SOURCE-IMPLEMENTED / EXACT-HEAD EXECUTION PENDING**.
- P1C01 Closure Pack continuation: **NEXT AFTER SELECTIVE WAREHOUSE TRAIN GREEN**.
- F1-07 source architecture: **PARALLEL VALIDATION LANE**.
- F1-08 maximum-safe mega source wave: **NEXT SOURCE PRODUCTION WAVE**.
- Runtime Gate 6/7 / PIE / device / visual / pacing / performance acceptance: **UNCHANGED / NOT CLAIMED**.

## 2026-09-29 - F1-07 Lórien & Anduin landmark source preparation

- Canonical F1-07 scope / P1C07 mapping: **REGISTERED**.
- F1-08 Fellowship-break boundary: **EXPLICITLY PRESERVED**.
- 26-category / 18,000-candidate shared source manifest: **SOURCE-IMPLEMENTED**.
- 2,000/category ceiling / landmark score bonus 7: **SOURCE-IMPLEMENTED**.
- Minimum 10 populated landmark categories: **SOURCE-IMPLEMENTED / EXECUTION PENDING**.
- Lothlórien vertical flet/canopy landmark identity: **SOURCE-IMPLEMENTED**.
- Anduin river-axis/cliff/stone-monument/Amon Hen approach identity: **SOURCE-IMPLEMENTED**.
- FBX-only animated candidate filter / BMP rejection: **SOURCE-IMPLEMENTED**.
- Inventory-clean hard gate: **SOURCE-IMPLEMENTED**.
- Dedicated 180-minute F1-07 workflow: **SOURCE-IMPLEMENTED**.
- PG-200 regression coverage: **SOURCE-IMPLEMENTED**.
- Heavy source workflow execution: **BLOCKED UNTIL WAREHOUSE INVENTORY CLEAN**.
- P1C07 runtime integration: **BLOCKED UNTIL PREDECESSOR GATE ACCEPTED**.
- Exact-head static validation: **PENDING**.
- PIE/device/visual/pacing/performance acceptance: **NOT CLAIMED**.

## 2026-09-29 - Warehouse active-provenance supersession repair

- Historical receipt preservation: **RETAINED / NO RECEIPT REWRITE**.
- Active provenance selection: **SOURCE-IMPLEMENTED — latest valid receipt per normalized payload path**.
- Windows case/slash path coalescing: **SOURCE-IMPLEMENTED**.
- Superseded historical hash records: **NON-FAILING HISTORY / REPORTED**.
- Active latest-receipt hash mismatch: **HARD FAIL REMAINS ENFORCED**.
- Synthetic V1 -> V2 supersession regression: **SOURCE-IMPLEMENTED / PRE-UNREAL EXECUTION PENDING**.
- Persistent warehouse inventory clean state: **PENDING RERUN**.
- P1C01 Closure Pack continuation: **BLOCKED UNTIL PERSISTENT AUDIT PASSES**.
- Runtime/PIE/device/visual/pacing/performance acceptance: **UNCHANGED / NOT CLAIMED**.

## 2026-09-29 - Interactive orchestration responsiveness

- Repeated same-run interactive long polling: **PROHIBITED BY DEC-075**.
- Bounded status checks + automation continuation: **GOVERNED**.
- PR #153 exact-head Pre-Unreal #1379: **SUCCESS**.
- PR #153 exact-head Unreal #1095: **SUCCESS**.
- Gate 6/7 / PIE / device / visual / performance criteria: **UNCHANGED**.

## 2026-09-29 - F1-06 landmark scoring priority

- Configurable landmark score bonus (6): **SOURCE-IMPLEMENTED**.
- PG-199 minimum landmark-score regression guard: **SOURCE-IMPLEMENTED**.
- Duplicate PR #152: **CLOSED / NOT MERGED**.
- PR #153 exact-head Pre-Unreal/Unreal after scoring update: **PENDING**.
- Visual acceptance: **NOT CLAIMED**.

## 2026-09-29 - PG-199 landmark/F1-06 guard

- Part I landmark/F1-06 static regression guard: **SOURCE-IMPLEMENTED**.
- Exact-head Pre-Unreal validation after PG-199: **PENDING**.
- Visual/runtime acceptance: **NOT CLAIMED**.

## 2026-09-29 - Part I landmark identity / F1-06 Caradhras-Moria source mega pack

- Part I landmark identity plan: **SOURCE-IMPLEMENTED**.
- Shire/Hobbiton + Bag End landmark anchors: **PLANNED / CURRENT-CHAPTER VISUAL ACCEPTANCE PENDING**.
- Bree/Weathertop landmark anchors: **SOURCE-PREPARED / VISUAL ACCEPTANCE NOT CLAIMED**.
- Rivendell landmark anchor: **SOURCE-ARCHITECTURE READY / HEAVY EXECUTION INVENTORY-GATED**.
- Caradhras/Moria landmark anchors: **SOURCE-ARCHITECTURE READY / HEAVY EXECUTION INVENTORY-GATED**.
- F1-06 24-category / 16,000-candidate manifest: **SOURCE-IMPLEMENTED**.
- Landmark coverage report + minimum-source gate: **SOURCE-IMPLEMENTED**.
- FBX-only animated candidate filter / BMP rejection: **SOURCE-IMPLEMENTED**.
- Dedicated 180-minute F1-06 workflow: **SOURCE-IMPLEMENTED**.
- P1C05/P1C06 runtime integration: **BLOCKED UNTIL PREDECESSOR GATE ACCEPTED**.
- Exact-head static validation: **PENDING**.
- PIE/device/visual/pacing/performance acceptance: **NOT CLAIMED**.

## 2026-09-29 - Warehouse mismatch diagnostic hardening

- P1C01 Closure Pack #2 inventory audit: **HARD STOP / hashMismatch=1**.
- Exact hash-mismatch log evidence: **SOURCE-IMPLEMENTED**.
- Exact license-hash/missing-reference log evidence: **SOURCE-IMPLEMENTED**.
- Automatic deletion/quarantine/receipt rewrite: **NOT AUTHORIZED / NOT IMPLEMENTED**.
- Mismatch record identification by rerun: **PENDING**.
- Warehouse clean state: **NOT CLAIMED**.
- P1C01 closure continuation: **BLOCKED UNTIL INVENTORY REPAIRED OR EVIDENCE-QUARANTINED**.

## 2026-09-29 - F1-05 Rivendell & Fellowship mega source preparation

- Canonical F1-05 source scope: **REGISTERED**.
- Runtime consumer P1C04 mapping: **RECORDED**.
- 20-category / 12,000-candidate shared source manifest: **SOURCE-IMPLEMENTED**.
- Inventory-clean hard gate: **SOURCE-IMPLEMENTED**.
- FBX-only animated candidate filter: **SOURCE-IMPLEMENTED**.
- BMP texture rejection: **SOURCE-IMPLEMENTED**.
- Dedicated 180-minute F1-05 workflow: **SOURCE-IMPLEMENTED**.
- Heavy workflow execution: **BLOCKED UNTIL WAREHOUSE INVENTORY CLEAN**.
- P1C04 runtime integration: **BLOCKED UNTIL PREDECESSOR GATE ACCEPTED**.
- Exact-head static validation: **PENDING**.
- PIE/device/visual/pacing/performance acceptance: **NOT CLAIMED**.

## 2026-09-29 - F1-04 Bree & Weathertop mega source preparation

- Canonical F1-04 source scope: **REGISTERED**.
- Runtime consumers P1C02 + P1C03 mapping: **RECORDED / NO RUNTIME RENUMBERING**.
- 16-category shared warehouse source manifest: **SOURCE-IMPLEMENTED**.
- Shared-stock indexer with 9000 total candidate ceiling: **SOURCE-IMPLEMENTED**.
- Animated candidate FBX-only filter: **SOURCE-IMPLEMENTED**.
- BMP texture rejection: **SOURCE-IMPLEMENTED**.
- Isolated 180-minute F1-04 preparation workflow: **SOURCE-IMPLEMENTED**.
- Runtime integration P1C02/P1C03: **BLOCKED UNTIL PREDECESSOR GATE ACCEPTED**.
- Exact-head Pre-Unreal validation: **PENDING**.
- Source workflow execution on develop: **PENDING**.
- PIE/device/visual/pacing/performance acceptance: **NOT CLAIMED**.

## 2026-09-29 - Production train root-repair wave

- develop Pre-Unreal #1363: **SUCCESS**.
- develop Unreal #1085: **SUCCESS**.
- P1C01 Chapter Closure Pack #1: **FAILED AFTER STORAGE PASS / TOOLING EXIT-STATE DEFECT**.
- Warehouse #283 material intake: **8 PREPARED / LOCAL GENERATED COMMIT CREATED / REMOTE LOOKUP FAILED BEFORE PUBLISH**.
- Part I Chapter Preparation Train #1: **FAILED DURING POWERSHELL 5.1 REPORT MATERIALIZATION**.
- Sequential Chapter Queue #1: **SUCCESS / WAIT STATE HONORED / P1C02 RUNTIME NOT RELEASED**.
- Deterministic closure child-process exit handling: **SOURCE-IMPLEMENTED**.
- Generated-branch ls-remote retry/exit capture: **SOURCE-IMPLEMENTED**.
- Part I generic-list ToArray serialization guard: **SOURCE-IMPLEMENTED**.
- PG-196 static regression coverage: **SOURCE-IMPLEMENTED**.
- Fresh exact-head validation/reruns: **PENDING**.
- PIE/device/visual/pacing/performance acceptance: **NOT CLAIMED**.

## 2026-09-29 - #1082 direct-PID/CIM recovery refinement

- Pre-Unreal #1360 on prior exact head `98dcb4d...`: **SUCCESS**.
- Unreal #1082: **FAILED AT STALE CI COMMANDLET RECOVERY** after `taskkill /T /F` could not terminate PID 14144.
- Direct PID taskkill fallback: **SOURCE-IMPLEMENTED**.
- CIM `Win32_Process.Terminate` fallback + return-value evidence: **SOURCE-IMPLEMENTED**.
- Fresh exact-head Pre-Unreal: **PENDING**.
- Fresh exact-head Unreal Build/import: **PENDING**.
- P1C01 Chapter Closure Mega Pack: **NOT YET RELEASED; EXACT-HEAD UNREAL GATE STILL REQUIRED**.
- PIE/device/visual/pacing/performance acceptance: **NOT CLAIMED**.

## 2026-09-29 - #1358/#1080 stale commandlet recovery refinement

- Pre-Unreal #1358: **FAILED ONLY AT LEGACY PG-015 WAITER SHAPE CHECK**.
- Unreal #1080 blocker PID 14144: **CI COMMANDLET IDENTITY CAPTURED** (`UE4Editor-Cmd` / ShireJourney QA / same interactive owner / orphaned parent / >20 min old).
- Bounded stale-commandlet process-tree recovery: **SOURCE-IMPLEMENTED**.
- Interactive editor kill-by-name: **FORBIDDEN / NOT INTRODUCED**.
- PG-015 + PG-195 static regression coverage: **SOURCE-UPDATED**.
- Fresh exact-head Pre-Unreal: **PENDING**.
- Fresh exact-head Unreal Build/import: **PENDING**.
- P1C01 Chapter Closure Mega Pack execution: **BLOCKED UNTIL REQUIRED EXACT-HEAD GATES TURN GREEN**.
- PIE/device/visual/pacing/performance acceptance: **NOT CLAIMED**.

## 2026-09-29 - Continuous Part I preparation train / Unreal #1068 process ownership repair

- Unreal Build #1068 Editor compile: **COMPILE STEP SUCCESS** on prior exact head `c76e521e...`.
- Unreal Build #1068 production import: **BLOCKED BEFORE IMPORT** by `PRODUCTION_IMPORT_PREFLIGHT_EDITOR_RUNNING pids=14144`.
- Editor/commandlet wait mismatch root repair (`DEC-066` / `PG-195`): **SOURCE-IMPLEMENTED**.
- Fresh exact-head Pre-Unreal validation after repair: **PENDING**.
- Fresh exact-head Unreal Build/import validation after repair: **PENDING**.
- Part I canonical/runtime ID reconciliation (`DEC-067`): **REGISTERED**.
- P1C02-P1C08 shared warehouse candidate indexing: **SOURCE-IMPLEMENTED / POST-MERGE EXECUTION PENDING**.
- Downstream runtime integration: **SERIALIZED / BLOCKED UNTIL PREDECESSOR GATE ACCEPTED**.
- Standing routine execution authorization (`DEC-068`): **RECORDED; DOES NOT WAIVE QUALITY GATES**.
- PIE/device/visual/pacing/performance acceptance: **NOT CLAIMED**.

## 2026-09-29 - Two-chapter queue + systemic living-world architecture registration

- P1C01 -> P1C02 sequential queue governance (`DEC-064`): **SOURCE-IMPLEMENTED**.
- P1C02 source/warehouse preparation before P1C01 acceptance: **AUTHORIZED WHEN QUEUED**.
- P1C02 runtime integration before P1C01 Gate 6/7 acceptance: **BLOCKED BY CONTRACT**.
- Core production direction / systemic environmental reactivity (`DEC-065`): **ARCHITECTURE REGISTERED**.
- Existing LivingWorld/NPC context/memory/relationship/pooling systems: **REUSED; NO PARALLEL BRAIN AUTHORIZED**.
- Generic bounded environmental reaction contract (trees/foliage, water, doors/tools/props, fauna/NPC observers): **PLANNED / RUNTIME NOT STARTED**.
- Exact-head Pre-Unreal/Unreal evidence after these documentation/governance commits: **PENDING**.
- PIE/device/visual/performance acceptance: **NOT CLAIMED**.

## 2026-09-28 - Pre-Unreal #1332 root-fix matrix

- PowerShell parser gate: **PASS on #1332 — 47 files / 0 parser errors**.
- Watchdog service-guard contract: **SOURCE-REBUILT ON CLEAN SINGLE-BODY SCRIPT**.
- Closure preflight Unreal exclusion: **SOURCE-FIXED**.
- PG-193 workflow reference assertion: **SOURCE-FIXED**.
- Unreal Build #1054: **SUCCESS on previous exact head 61d629c4...**.
- Current exact-head static validation after commits `609c7eb...`, `c8271d8...`, `5f016df...`: **PENDING**.
- P1C01 Closure Pack V2 Warehouse execution: **PENDING MERGE + DEDICATED WORKFLOW RUN**.
- PIE/device/visual/performance acceptance: **NOT CLAIMED**.

## 2026-09-28 - CI red-run root-cause closure

- Pre-Unreal #1325 PowerShell parser gate: **PASS — files=45, errors=0**.
- Pre-Unreal #1325 PG-168 failure: **ROOT CAUSE IDENTIFIED** — long-pack cancellation policy was incorrectly applied to the normal Warehouse workflow.
- Normal Warehouse workflow: **RESTORED TO 60 MIN / cancel-in-progress=true**.
- Dedicated P1C01 closure workflow: **SOURCE-IMPLEMENTED — 180 MIN / cancel-in-progress=false / isolated concurrency**.
- Closure fast preflight: **SOURCE-IMPLEMENTED**.
- Unreal Build #1047 editor compile: **COMPILE-TESTED SUCCESS for that exact run/head**.
- Unreal Build #1047 production commandlet: **376 files processed / 0 commandlet import failures**, but workflow **FAILED** on `T_Cloth_Green.uasset` delete/save error.
- UE production import destination preflight + bounded single retry: **SOURCE-IMPLEMENTED / EXACT-HEAD RE-RUN PENDING**.
- PIE/device/visual/performance acceptance: **NOT CLAIMED**.

## 2026-09-28 - PR #145 parser-gate findings and long-pack execution hardening

- Pre-Unreal #1318: **FAILED AT POWERSHELL PARSER GATE**; merge correctly blocked.
- `export_p1c01_material_source_branch.ps1` duplicated-tail corruption: **SOURCE-REPAIRED**.
- `runner_watchdog.ps1` latent duplicated/corrupted source: **RESTORED FROM 1066cf022723fcdef9bfac66519f5b0f9c1e03a4** under DEC-060.
- Repository-wide PowerShell parser prevention (DEC-059): **ACTIVE IN SOURCE / EXACT-HEAD GREEN RE-RUN PENDING**.
- Warehouse large-pack timeout: **SOURCE-SET TO 180 MINUTES**.
- Warehouse cancellation policy: **SOURCE-SET TO QUEUE NEW WORK, DO NOT CANCEL ACTIVE PACK**.
- P1C01 Closure Pack V2 Warehouse execution: **PENDING**.
- UE4.27 import/runtime binding/PIE/device/visual/performance acceptance: **NOT CLAIMED**.

## 2026-09-28 - Warehouse #282 parser root-cause prevention

- Pre-Unreal #1317: **SUCCESS**, but missing repository-wide PowerShell parse coverage.
- Warehouse #282: **FAILED BEFORE MATERIAL EXECUTION** with a PowerShell `ParserError` in `export_p1c01_material_source_branch.ps1`.
- Exporter publish block: **SOURCE-REPAIRED** on the active closure-pack branch.
- DEC-059 repository-wide PowerShell parser gate: **SOURCE-IMPLEMENTED**.
- `Scripts/test_powershell_syntax.ps1`: **SOURCE-IMPLEMENTED**.
- Hosted Pre-Unreal parser step: **SOURCE-IMPLEMENTED / EXACT-HEAD RUN PENDING**.
- Warehouse/material publish after repair: **PENDING RE-RUN**.
- UE/PIE/device/visual/performance status: **UNCHANGED / NOT CLAIMED**.

## 2026-09-28 - P1C01 maximum-throughput Chapter Closure Mega Pack V2

- DEC-058 maximum-throughput chapter source pack: **SOURCE-IMPLEMENTED**.
- Single Warehouse closure-pack trigger: **SOURCE-IMPLEMENTED**.
- Provider/source capacity: **37 Poly Haven + 17 ambientCG lanes + 17 Quaternius + 12 Kenney + 8 KayKit + 17 OpenGameArt**.
- Promotion selector ceiling: **187**.
- Material closure wave: **26 requested materials**.
- Material generated-branch budget: **48 MiB/source / 640 MiB/batch / minimum 18 exported**.
- Storage guard: **6 GiB free-space reserve / no source deletion for space**.
- Provider/asset/source blocker behavior: **QUARANTINE_AND_CONTINUE**.
- Infrastructure/inventory/storage corruption: **HARD_FAILURE**.
- UE4.27 import/runtime binding/PIE/device/visual/performance acceptance: **NOT CLAIMED**.

## 2026-09-28 - Warehouse #281 generated-branch publish root cause

- Pre-Unreal #1315: **SUCCESS**.
- Material intake under DEC-056: **RUN-PROVEN** at `prepared=8 pending=8 manual=0`.
- Local generated source commit: **CREATED** at `2474500` before publish.
- Remote generated branch publish: **FAILED** with `stale info`; no UE import claim.
- Root cause: **implicit --force-with-lease depended on stale/unfetched remote-tracking state** in the isolated Warehouse checkout.
- DEC-057 explicit remote-SHA lease: **SOURCE-IMPLEMENTED**.
- PG-191 regression guard: **SOURCE-IMPLEMENTED**.
- Post-fix Warehouse publish: **PENDING RE-RUN**.
- UE4.27 import/runtime binding/PIE/device/visual/performance acceptance: **NOT CLAIMED**.

## 2026-09-28 - Warehouse #280 material-QC execution repair

- Pre-Unreal #1313: **SUCCESS**.
- Warehouse Stage #280: **FAILED BEFORE MATERIAL QC EXECUTION** at `prepare_p1c01_material_intake.ps1:122`.
- Exact error: **Windows PowerShell 5.1 `CommandNotFoundException` for `return if(...)`**.
- Selector control-flow repair: **SOURCE-FIXED**.
- PG-190 compatibility guard: **SOURCE-IMPLEMENTED**.
- Material provenance/albedo QC regeneration: **NOT YET RE-RUN**.
- UE4.27 import/runtime binding/PIE/device/visual/performance acceptance: **NOT CLAIMED**.

## 2026-09-28 - Warehouse #279 generated-material evidence and albedo-provenance hold

- Pre-Unreal #1311: **SUCCESS**.
- Warehouse Stage #279: **SUCCESS**.
- Material intake: **RUN-PROVEN** at `prepared=8 pending=8 manual=0`.
- Generated material branch: **RUN-PROVEN** at `537d9e72...`, 8 materials / 137,974,221 source bytes.
- Old 16 MiB blocker: **CLEARED BY RUN EVIDENCE** under DEC-055 bounded 32/256 MiB policy.
- Exact selected-file provenance: **QC DEFECT IDENTIFIED IN SOURCE**; first matching receipt row can differ from the file selected by `Select-BaseColor`.
- Generated branch UE import: **HELD** until post-DEC-056 Warehouse regeneration proves explicit albedo semantics and exact selected-file provenance.
- UE4.27 import/runtime binding/PIE/device/visual/performance acceptance: **NOT CLAIMED**.

## 2026-09-28 - PR #141 static guard follow-up

- Pre-Unreal #1309: **FAILED STATIC VALIDATION** on stale PG-184 text requirement `128 MB bounded limit`.
- Exporter/runtime evidence: **NOT REACHED / NOT IMPLIED BY THIS FAILURE**.
- Stale PG-184 literal: **SOURCE-FIXED** to validate `MaxBatchSourceBytes` while PG-188 owns the exact 32/256 MiB budget contract.
- Next evidence: **EXACT-HEAD PRE-UNREAL RE-RUN PENDING**.

## 2026-09-28 - Warehouse #278 Mega Chapter Pack evidence / larger bounded material source batch

- PR #140 merge head `14d34d28...`: **PRE-UNREAL #1308 SUCCESS / WAREHOUSE #278 SUCCESS**.
- Chapter-pack result: **RUN-PROVEN** at `passed=3 quarantined=1 hard=0`.
- Inventory: **RUN-PROVEN** at 18,676 payload files / 6,622,954,088 bytes / 14 receipts / 667 receipt records / 215 duplicate groups.
- Mega promotion: **RUN-PROVEN WITH MANUAL QUEUE** at `prepared=36 intakeQC=34 pending=3 manual=2 badReceipts=0`.
- Material intake: **RUN-PROVEN** at `prepared=8 pending=8 manual=0`.
- Old 16 MiB material source cap: **REAL BLOCKER OBSERVED** on SH_DIRT_SOIL base color.
- DEC-055 revised source-promotion budget: **SOURCE-IMPLEMENTED** at 32 MiB/source + 256 MiB/batch + minimum six exported items.
- Oversize behavior: **ITEM-LEVEL QUARANTINE SOURCE-IMPLEMENTED**; whole material car fails only if the post-quarantine export count falls below the manifest minimum.
- Generated material branch after revised budget: **PENDING WAREHOUSE RE-RUN**.
- UE4.27 import/runtime binding/PIE/device/visual/performance acceptance: **NOT CLAIMED**.

## 2026-09-28 - P1C01 Mega Chapter Pack / workflow consolidation

- Governor chapter-pack policy (DEC-054): **SOURCE-REGISTERED / OWNER-AUTHORIZED**.
- One pack / four bounded internal cars: **SOURCE-IMPLEMENTED**.
- Selector ceiling: **62 candidates** across materials / architecture-props / audio / fauna / character-animation support.
- Legacy overlapping P1C01 Warehouse steps during pack execution: **SUPPRESSED IN SOURCE**.
- Per-car quarantine + continue semantics: **SOURCE-IMPLEMENTED**.
- Infrastructure fail-closed semantics: **SOURCE-IMPLEMENTED**.
- TGA Git LFS migration: **DEFERRED TO FIRST BINARY PROMOTION WAVE** to avoid an unnecessary Unreal trigger here.
- Exact-head Pre-Unreal / Warehouse execution result: **PENDING**.
- UE import/integration/PIE/device/visual/performance acceptance: **NOT CLAIMED**.

## 2026-09-28 - Unreal runner cost reduction for P1C01 material tooling

- PR-triggered Unreal for P1C01 prepare/promote/run/export tooling-only changes: **PATH-FILTERED OUT IN SOURCE**.
- Push-triggered Unreal for exporter-only changes: **PATH-FILTERED OUT IN SOURCE**.
- Manual/mixed-safe classifier treatment for exporter tooling: **SAFE-INHERIT SOURCE RULE ADDED**.
- Existing classifier regression coverage for material-tooling fast path: **SOURCE-UPDATED**.
- Runtime/config/package-impacting validation behavior: **UNCHANGED**.
- Exact CI policy proof on this branch: **PRE-UNREAL PENDING**.

## 2026-09-28 - Warehouse #276 material-export unblock

- Warehouse #276 exact develop head `f24480b3...`: **SELF-HOSTED EXECUTION REACHED FINAL MATERIAL EXPORT STEP**.
- Inventory audit: **RUN-PROVEN** at 13,389 payload files / 5,590,510,073 bytes / 14 receipts / 667 receipt records / 215 duplicate groups.
- P1C01 mega promotion: **RUN-PROVEN WITH MANUAL QUEUE** at `prepared=36 intakeQC=34 pending=3 manual=2 badReceipts=0`.
- P1C01 material intake: **RUN-PROVEN** at `prepared=8 pending=8 manual=0`.
- Root cause of final failure: **IDENTIFIED** as absolute `ManifestPath` being re-joined with `ProjectRoot` before `Get-Content`.
- Rooted/relative manifest resolution repair: **SOURCE-FIXED**.
- PG-184 regression guard for rooted-path handling: **SOURCE-IMPLEMENTED**.
- Generated `generated/p1c01-material-source-v1` population after this repair: **PENDING WAREHOUSE RE-RUN**.
- UE4.27 import/integration and PIE/device/visual/performance acceptance: **NOT CLAIMED**.

## 2026-09-28 - P1C01 large material source promotion

- Heterogeneous receipt + SHA256-gated material intake: **SOURCE-IMPLEMENTED**.
- Bounded safe ZIP scan/extraction for selected material items: **SOURCE-IMPLEMENTED**.
- Partial-good continuation with manual queue: **SOURCE-IMPLEMENTED**.
- Generated source branch with 16 MB/file and 128 MB/batch caps: **SOURCE-IMPLEMENTED**.
- Tracked source destination `SourceAssets/Production/Imported/P1C01Materials`: **SOURCE-IMPLEMENTED**.
- Selective Warehouse phase `WH_RUN_P1C01_MATERIAL_EXPORT`: **SOURCE-IMPLEMENTED**.
- Generated material branch population from persistent warehouse: **PENDING MACHINE EXECUTION**.
- UE4.27 material import from generated branch: **PENDING EXACT-HEAD UNREAL RUN**.
- PIE/device/visual/performance acceptance: **NOT CLAIMED**.

## 2026-09-28 - P1C01 immediate large intake unfreeze

- Warehouse #275 character-intake root cause (`PropertyNotFoundStrict` on heterogeneous receipt schema): **ROOT-CAUSE IDENTIFIED / SOURCE-FIXED**.
- Character intake support for `file/sha256` and `archive/archive_sha256`: **SOURCE-IMPLEMENTED**.
- Windows PowerShell `System.IO.Compression.FileSystem` load for P1C01 selected ZIP extraction: **SOURCE-IMPLEMENTED**.
- Previously isolated P1C01 mega-promotion archives in #274: **28 candidates eligible for bounded retry after merge**.
- Exact-head hosted static validation: **PENDING**.
- Persistent Warehouse materialization/intake counts after repair: **PENDING**.
- UE runtime/PIE/device/visual/performance acceptance: **UNCHANGED / NOT CLAIMED**.

## 2026-09-28 - P1C01 runtime/character intake salvage v2

- PR #133 original-head UE4.27.2 build/import evidence: **COMPILE/IMPORT RUN SUCCESS on `970a52f7...` via Unreal #1033**.
- Rebased current-develop runtime source: **SOURCE-IMPLEMENTED / NEW EXACT-HEAD PROOF PENDING**.
- Living World interaction + ambient-motion pooling and cached player lookup: **SOURCE-IMPLEMENTED**.
- Audio SFX repeat guard and bounded rig-availability retry: **SOURCE-IMPLEMENTED**.
- Quaternius four-pack character/animation intake and FBX/provenance gate: **SOURCE-IMPLEMENTED**.
- Warehouse manual-queue continuation for isolated bad assets: **SOURCE-IMPLEMENTED**.
- READY_FOR_IMPORT character rigs, PIE, device, visual and target-performance acceptance: **NOT CLAIMED**.

## 2026-09-28 - P1C01 selective Warehouse promotion routing

- P1C01 promotion workflow trigger paths: **SOURCE-IMPLEMENTED**.
- Selective classifier flag `WH_RUN_P1C01_PROMOTION`: **SOURCE-IMPLEMENTED**.
- Bounded inventory audit + P1C01 promotion phase only for this delta: **SOURCE-IMPLEMENTED**.
- PG-184 regression coverage for the new promotion phase: **SOURCE-IMPLEMENTED**.
- Exact-head hosted static validation: **PENDING**.
- Persistent warehouse execution/counts: **PENDING**.
- READY_FOR_IMPORT/UE import/integration/PIE/device/visual/performance: **UNCHANGED / NOT CLAIMED**.

## 2026-09-28 - P1C01 mega warehouse promotion prep

- Existing staged warehouse-first strategy: **SOURCE-IMPLEMENTED**.
- Bounded P1C01 selection classes (surfaces, architecture/props, audio, fauna, character/animation support): **SOURCE-IMPLEMENTED**.
- Receipt SHA256 verification + non-destructive selected extraction: **SOURCE-IMPLEMENTED**.
- Dangerous/BMP rejection and FBX animated-class rule: **SOURCE-IMPLEMENTED**.
- Blocker isolation/manual queue instead of whole-train stop: **SOURCE-IMPLEMENTED**.
- READY_FOR_IMPORT/UE import/runtime integration: **NOT CLAIMED**.
- Hosted exact-head static validation: **PENDING**.
- Warehouse execution on persistent stock: **PENDING**.
- UE4 compile/PIE/device/visual/performance maturity: **UNCHANGED**.

## 2026-09-28 - PG-167 hosted administrative cleanup guard

- Hosted Python fast path: **RUN-PROVEN** by Pre-Unreal #1289 (`PYTHON_FAST_PATH_PASS`, Python 3.12.10).
- Branch Cleanup hosted-runner policy: **SOURCE-FIXED**.
- Merged-PR-only cleanup trigger and exact-head safety contract: **UNCHANGED**.
- Runtime/compile/PIE/device/visual/performance rules: **UNCHANGED**.
- New exact-head static proof: **PENDING**.

## 2026-09-28 - Lightweight administration / static-lane optimization

- Material-change-only Governor requirement-ID rule: **SOURCE-IMPLEMENTED**.
- Branch Cleanup off UE4 runner onto hosted Windows: **SOURCE-IMPLEMENTED**.
- Pre-Unreal PATH-Python fast path with robust fallback retained: **SOURCE-IMPLEMENTED**.
- Full static/governance/asset/deep-audit coverage: **UNCHANGED**.
- Runtime/compile/PIE/device/visual/performance acceptance rules: **UNCHANGED**.
- Exact-head static timing/proof after optimization: **PENDING**.

## 2026-09-28 - CI/Warehouse root-repair release gate

- Repair exact-head static validation: **STATIC-VALIDATED** by Pre-Unreal #1285 on `0bd0e6952161f1c3fa5bb603d25813400c330f24`.
- Develop post-merge static validation: **STATIC-VALIDATED** by Pre-Unreal #1286 on `26ff8f8838b4c9680c793fea5d942a314ad29be4`.
- Self-hosted runner health: **RUN-PROVEN** by Warehouse #272 with interactive user/watchdog topology.
- Warehouse exact-source/selective classifier: **RUN-PROVEN** by #272, `mode=selective`, `phases=WH_RUN_AUDIT`.
- Warehouse inventory audit: **RUN-PROVEN** by #272, 13,377 payload files / 5,426,414,977 bytes.
- Redundant provider trains on control-plane merge: **NOT RUN** by design; all provider staging/saturation/prep/provider-resolution steps skipped.
- Unreal routing for Warehouse/control-plane-only merge: **CORRECTLY NOT TRIGGERED**.
- Production infrastructure freeze: **RELEASED**; existing W01 P1C01 production may resume under its existing gates.
- UE4 compile/PIE/device/visual/performance maturity: **UNCHANGED** by this release.

## 2026-09-28 - Warehouse control-plane proof routing hardening

- Warehouse classifier post-merge trigger coverage: **SOURCE-FIXED**.
- Workflow-control-plane delta routes to bounded `WH_RUN_AUDIT` instead of all acquisition/provider trains: **SOURCE-FIXED**.
- Unrelated co-commit files no longer force Warehouse full mode: **SOURCE-FIXED**.
- PG-184 regression coverage for exact-source + trigger + bounded control-plane proof: **SOURCE-FIXED**.
- Hosted exact-head static proof and resulting post-merge self-hosted Warehouse proof: **PENDING**.
- Runtime/PIE/device/visual/performance maturity: **UNCHANGED**.

## 2026-09-28 - Warehouse #271 exact-source classifier repair

- Self-hosted runner identity/topology/network/workspace health: **RUN-PROVEN** by Warehouse #271 on `542a6feef7e2985e40ed86f7242dd0a005be1395`.
- Warehouse isolated exact-head checkout: **RUN-PROVEN** by `WAREHOUSE_CHECKOUT_PASS` on #271.
- Warehouse classifier working-directory defect: **ROOT-CAUSE IDENTIFIED** from `fatal: bad object 542a6feef7e2985e40ed86f7242dd0a005be1395`.
- Classifier binding to `SHIRE_WAREHOUSE_SOURCE` + bounded exact head/base fetch retry: **SOURCE-FIXED**.
- Provider/archive execution on #271: **NOT RUN**; all provider/phase steps were skipped after classifier failure.
- New exact-head static proof and post-merge warehouse proof: **PENDING**.
- Runtime/PIE/device/visual/performance maturity: **UNCHANGED**.

## 2026-09-28 - Pre-Unreal #1280 stale guard correction

- Hosted exact-head checkout, Python resolution, and Unreal classifier tests: **RUN-PROVEN** by #1280 on `a8714aa3a1fb8ff0fb7be970d4bcfedb49139035`.
- Core structural pass marker `PRE-UNREAL CORE VALIDATION PASSED`: **RUN-PROVEN** by #1280.
- PG-145C conditional intermediate-reset policy assertion: **SOURCE-FIXED**.
- PG-176 hosted ephemeral static-checkout policy assertion: **SOURCE-FIXED**.
- New exact-head static result after the validator correction: **PENDING**.
- Runtime/PIE/device/visual/performance maturity: **UNCHANGED**.

## 2026-09-28 - Static-lane guard migration

- Unreal classifier incremental/reset tests: **RUN-PROVEN** by hosted Pre-Unreal #1277.
- Legacy PG-134 hosted-checkout migration: **SOURCE-IMPLEMENTED**.
- Legacy PG-167 hosted static-lane migration: **SOURCE-IMPLEMENTED**.
- PG-185 runner-token precision fix: **SOURCE-IMPLEMENTED**.
- New exact-head static result: **PENDING**.
- Runtime/PIE/device/visual/performance maturity: **UNCHANGED**.

## 2026-09-28 - Warehouse cache self-repair hardening

- Corrupt cached ZIP purge during receipt reuse: **SOURCE-IMPLEMENTED**.
- Metadata-only archive contract in warehouse manifest: **SOURCE-IMPLEMENTED**.
- PG-184 regression coverage for purge + metadata-only contract: **SOURCE-IMPLEMENTED**.
- Exact-head static proof: **PENDING**.

## 2026-09-28 - Hosted classifier repair

- Hosted Windows Pre-Unreal lane boot/checkout/Python resolution: **RUN-PROVEN** by #1269.
- Clean-compile flag initialization defect: **SOURCE-FIXED** after #1269.
- New exact-head Pre-Unreal result: **PENDING**.
- Runtime/PIE/device/visual/performance maturity: **UNCHANGED**.

## 2026-09-28 - Zero-waste trigger routing

- MasterExecutionRoadmap governance-only Unreal exclusion: **SOURCE-IMPLEMENTED**.
- Receipt-integrity fail-fast before archive scan: **SOURCE-IMPLEMENTED**.
- PG-184 preflight regression guard: **SOURCE-IMPLEMENTED**.
- Repair-PR expected heavy-run count: **0 Warehouse / 0 Unreal**, hosted Pre-Unreal only.
- Exact-head proof: **PENDING**.

## 2026-09-28 - CI split-lane root repair

- Hosted Pre-Unreal static/policy lane: **SOURCE-IMPLEMENTED**.
- Warehouse pull-request churn removal: **SOURCE-IMPLEMENTED**.
- Selective warehouse provider/phase classifier: **SOURCE-IMPLEMENTED**.
- Metadata-only ZIP intake + corrupt-cache self-repair: **SOURCE-IMPLEMENTED**.
- Warehouse-only Unreal trigger exclusion: **SOURCE-IMPLEMENTED**.
- Conditional Unreal intermediate reset: **SOURCE-IMPLEMENTED**.
- Bounded compiler-failure clean retry retained: **SOURCE-IMPLEMENTED**.
- PG-184/PG-185 regression guards: **SOURCE-IMPLEMENTED**.
- Exact-head hosted static validation: **PENDING**.
- Selected machine validation before production unfreeze: **PENDING**.
- Runtime/PIE/device/visual/performance maturity: **UNCHANGED**.

## 2026-09-28 - CI/Warehouse root-repair freeze

- Production train execution: **PAUSED BY OWNER**.
- Repeated Warehouse PR-synchronize execution: **REMOVED IN REPAIR SOURCE**.
- ZIP structural validation before receipt reuse: **SOURCE-IMPLEMENTED**.
- Corrupt AmbientCG/KayKit cached ZIP self-repair: **SOURCE-IMPLEMENTED**.
- Critical-gap metadata-only ZIP inventory (no repeated extraction): **SOURCE-IMPLEMENTED**.
- Duplicate receipt suppression + exact blocker details: **SOURCE-IMPLEMENTED**.
- PG-184 regression guard: **SOURCE-IMPLEMENTED**.
- Exact-head static/machine validation: **PENDING**.
- Runtime/PIE/device/visual/performance maturity: **UNCHANGED**.

## 2026-09-27 - Runner single-path proof

- Legacy service path absent: **MACHINE-PROVEN** on owner Windows state and Unreal #1021.
- Watchdog interactive ownership: **MACHINE-PROVEN** (`IDEAPAD320\user`, session 1, PID 6192).
- Broker listening / worker ownership / GitHub:443: **MACHINE-PROVEN** by Unreal #1021 runner-health lines.
- Permanent service guard + continuous watchdog enforcement: **SOURCE-IMPLEMENTED**, exact-head Pre-Unreal rerun pending after PG-183 false-red correction.
- Game/runtime maturity: **UNCHANGED**. #1021 skipped C++ build/import/PIE/package on governance fast path.

## 2026-09-27 - Runner single-path ownership hardening

- Legacy Windows service execution path removed by service guard: **SOURCE-IMPLEMENTED**.
- Service state target: **ABSENT**, with **Stopped + Disabled** accepted only as transient pending-deletion state.
- Continuous watchdog re-enforcement against recreated service mode: **SOURCE-IMPLEMENTED**.
- Forbidden service identities (NETWORK SERVICE / LOCAL SERVICE / SYSTEM): **SOURCE-IMPLEMENTED**.
- Exact-head static guard PG-145B updated: **SOURCE-IMPLEMENTED / CI PENDING**.
- Physical Windows runner repair: **PENDING OWNER-SIDE ELEVATED INSTALLER RUN**.
- Current proof: **ROOT-FIX SOURCE-IMPLEMENTED** only; no new COMPILE/PIE/DEVICE/VISUAL/PERFORMANCE acceptance.

## 2026-09-27 - Permanent runner ownership hardening

- Legacy service elimination guard: **SOURCE-IMPLEMENTED**.
- Watchdog continuous anti-service self-heal: **SOURCE-IMPLEMENTED**.
- Installer purge-before-watchdog behavior: **SOURCE-IMPLEMENTED**.
- Health verifier absent-or-stopped-disabled service contract: **SOURCE-IMPLEMENTED**.
- Static PG-183 regression guard: **SOURCE-IMPLEMENTED**.
- Physical Windows runner repaired with new installer: **PENDING OWNER-SIDE ELEVATED APPLICATION**.
- Current maturity: **SOURCE-IMPLEMENTED / exact-head static validation pending**.

## 2026-09-27 - Runner ownership governance visibility

- Interactive-user watchdog ownership hard invariant: **SOURCE-IMPLEMENTED**.
- Legacy `actions.runner.*` service Stopped/Manual rule: **SOURCE-IMPLEMENTED**.
- Forbidden NETWORK SERVICE/LOCAL SERVICE/SYSTEM identities: **SOURCE-IMPLEMENTED**.
- README / Governor guide / onboarding visibility: **SOURCE-IMPLEMENTED**.
- Live physical runner state: **NOT RE-VERIFIED BY THIS GOVERNANCE CHANGE**.
- Current maturity: **SOURCE-IMPLEMENTED / exact-head static validation pending**.

## 2026-09-27 - Developer handoff entry integrity

- Develop-side canonical onboarding path: **SOURCE-IMPLEMENTED**.
- Off-develop branch warning in one-command onboarding: **SOURCE-IMPLEMENTED**.
- Stale copied next-drop prose removed from Governor guide: **SOURCE-IMPLEMENTED**.
- GitHub default-branch `main` landing redirect: **PENDING SEPARATE MAIN-BRANCH DOC CHANGE**.
- Current maturity: **SOURCE-IMPLEMENTED / static validation pending**. No gameplay or acceptance status changes.

## 2026-09-27 - Provider-resolution train V3

- 20 source-resolution cars cover characters, animation, fauna, creatures, architecture, vegetation, PBR, audio/music/voice, VFX, UI, terrain, enemies, battle support, regional kits and manual marketplace review.
- Resolver chooses only staged or access-policy-compatible automatic providers; auth/review/manual/reference sources remain explicit human lanes.
- Current maturity: **PREPARATION-IMPLEMENTED / exact-head validation pending**. No source-resolution result is READY_FOR_IMPORT.

## 2026-09-27 - Quaternius critical-source license capture

- 13 high-value Quaternius lanes now have explicit official-page CC0 capture in the acquisition manifest.
- Access/download resolution is still a separate gate; no interactive/store bypass is authorized.
- Current maturity: **AUTHORIZED_FOR_STAGING where public download can be resolved; receipt/QC pending**.

## 2026-09-27 - Warehouse parser hardening after V1 staging evidence

- Verified warehouse footprint from #265 before report failure: 247 payload files, 3.85 GB, 13 receipts and 667 receipt records; inventory audit PASS.
- V1 failure class: report-parser StrictMode incompatibility with heterogeneous receipt schemas, not provider staging or hash-audit failure.
- V1/V2 receipt parsing now uses optional-property-safe access while preserving SHA256 verification and promotion ceilings.
- Current status: **SOURCE-IMPLEMENTED / fresh exact-head validation pending**.

## 2026-09-27 - Critical warehouse gap train V2

- 20 additional preparation cars now target conversion of staged warehouse stock into classified INTAKE_QC candidates.
- Major gap lanes covered: hero character FBX candidates, humanoid animation, creatures/fauna, architecture/world kits, interiors/props, vegetation, PBR material sets, texture-format debt, WAV masters, ambience/foley, music/voice separation, VFX, UI/fonts/localization, terrain and 28-region mapping.
- Security/evidence gates: receipt SHA256, ZIP-only approved extraction path, executable/BMP blocking, FBX animated-format rule, PNG/TGA production-texture rule, WAV-master rule.
- Current maturity: **PREPARATION-IMPLEMENTED / exact-head validation pending**; no READY_FOR_IMPORT or runtime maturity promotion.

## 2026-09-27 - Consolidated prep lanes into warehouse saturation train

- Architecture/interiors/props, character rig/animation, Shire audio and fauna preparation are carried forward on the new post-#118 warehouse train.
- Old stale-base preparation PRs are superseded; their substantive manifests/scripts are preserved.
- No runtime maturity promotion is inferred from consolidation.

## 2026-09-27 - 20-car warehouse saturation train

- Warehouse preparation sequence expanded to 20 ordered cars spanning materials, architecture, characters, animation, audio/music/voice, vegetation, water, ruins, fortifications, enemies/creatures, battle assets, VFX, UI/localization, terrain, F2/F3 kits, props and coverage/dedupe.
- Public/provider-compatible lanes reuse existing staging scripts and SHA256 receipts; manual/auth/purchase lanes stop at candidate preparation.
- Runtime/import work remains serialized even while warehouse preparation is parallel.
- Current maturity: **PREPARATION-IMPLEMENTED / exact-head validation pending**. No car is promoted by metadata alone.

## 2026-09-27 - CI runner-health contract alignment

- Repeated #118 Unreal failures were pre-build CI policy failures, not material compiler/import failures.
- Watchdog installer and verifier now share the same accepted scheduled-task states: `Running` or `Ready`.
- All live listener/worker ownership/session/network/workspace checks remain mandatory after the state check.
- Status: **CI_INFRA / VALIDATOR_POLICY FIX CANDIDATE; exact-head validation pending**.

## 2026-09-27 - Expanded P1C01 16-surface material intake train

- Authorized material intake scope: 16/16 Poly Haven surface candidates from the P1C01 warehouse queue.
- Preparation contract: PNG/TGA base color + scalar Roughness/Metallic/Specular + SHA256 receipt; BMP remains forbidden.
- Pre-Unreal now fails closed on missing queue authority, duplicates, out-of-range scalars, incomplete low-spec bindings or missing intake guards.
- Runtime-cost boundary remains unchanged: one albedo texture sample per prepared material, no density increase, no new synchronous heavy runtime loading.
- Validation status: **SOURCE-IMPLEMENTED / exact-head UE4.27 build-import pending** because Unreal #915 is blocked before build by runner-health watchdog state, not by a compiler/import result.

## 2026-09-27 - P1C01 Shire material surface-set production batch

- Project-owned Shire material bank is now explicitly defined in `Data/P1C01ShireMaterialSurfaceSetV1.json`.
- Import-time material response expands from Albedo/Color/Roughness/Metallic to include bounded Specular sourced from authored MTL `Ks`.
- Runtime cost boundary for this batch: zero new texture samples, zero new heavy runtime asset loads, zero foliage-density increase.
- Current maturity: **SOURCE-IMPLEMENTED / Pre-Unreal + UE4.27 build/import validation pending**.
- Human visual quality, target-device FPS/VRAM and PIE acceptance remain open.

## 2026-09-27 - P1C01 player-experience convergence batch

- Story dialogue continuity, mouse-look frame independence, quick-load rejection feedback, event-driven quest-trigger re-evaluation and bounded subtitle wrapping are implemented on the active fix branch.
- The trigger repair preserves `PrimaryActorTick.bCanEverTick = false`; no per-frame quest-trigger polling was introduced.
- P1C01 maturity remains unchanged until exact-head UE4.27 validation. This batch is **SOURCE-IMPLEMENTED / validation pending**, not PIE/device/visual accepted.
- Map/Chronicle interaction policy is intentionally excluded from this defect batch and remains a later UX decision.

## 2026-09-27 - Import-fix validation infrastructure note

- Unreal Build #896 did not reach production import on either attempt because stale MSVC intermediate metadata referenced a removed prior-run temp directory.
- CI build recovery now includes the observed C1083/compiler-intermediate signature and performs one bounded project-intermediate reset/retry.
- No P1C01 gameplay/visual/PIE/device maturity changes. Fresh exact-head compile/import proof remains pending.

## 2026-09-27 - P1C01 production-import blocker status

- Local one-click import produced concrete failure evidence on `WorldGridMaterial.uasset` because the importer dirtied a non-project Engine package.
- The importer is now source-repaired to mutate/save material packages only when their package path begins with `/Game/Production/`.
- P1C01 production maturity is unchanged by this repair. No PIE/device/visual/performance acceptance is promoted.
- Validation state for this fix: **SOURCE-IMPLEMENTED / exact-head build+import pending**.

## 2026-09-27 - Legacy unique-root consolidation before final branch cleanup

- Live GitHub audit confirmed the branches still shown in the repository are real refs, not merely historical Actions filters. They were not deleted earlier because each had `ahead_by > 0` and the cleanup correctly refused to destroy unique commits without disposition.
- The seven remaining legacy refs have now been reviewed individually. None is allowed to become a second trunk: old CI/report experiments are superseded; `MegaProductionBuildV2.json` is already identical on develop; onboarding improvements are already integrated on current develop; old localization/P1C01-prep branch snapshots remain backlog/preparation intent only and do not override the current production order; the old Mega Promotion audit is superseded by later Warehouse #264 evidence.
- All seven are now explicitly scheduled for deletion after this consolidation merge: `ops/actions-budget-isolation-v1`, `ops/daily-project-manager-report-v1`, `ops/onboarding-handoff-v2`, `planning/mega-production-resume-v1`, `planning/w01-localization-prototype-v1`, `planning/w01-p1c01-mega-prep-v1`, `warehouse/p1c01-mega-promotion-audit-v1`.
- Expected repository roots after post-merge cleanup: **develop + main only**.
- Failure/safety boundary: no runtime/gameplay/source asset content is changed and no UE4 build is requested. This is ADMIN_GOVERNANCE repository hygiene.
- Evidence boundary: **STATIC-VALIDATED CANDIDATE / FRESH PRE-UNREAL + POST-MERGE CLEANUP PENDING**.

## 2026-09-27 - New-developer handoff made drift-proof

- The canonical entry remains `README.md -> PROJECT_GOVERNOR -> ProjectGovernor.json -> CURRENT_PROJECT_STATE -> DEVELOPMENT_GATES -> PROJECT_GUARDIAN`.
- The README no longer embeds a copied "next production drop" that can become stale after merges. It now directs every programmer to the one-command onboarding reader and the evidence-backed current-state handoff.
- `Scripts/new_developer_onboarding.ps1` now prints Governor-derived **Current status**, **Current focus**, active lane/gate/benchmark and **Next allowed actions**, plus the checked-out Git branch/HEAD.
- Live baseline before this change: `develop@6e3e33e16edf4660f05e130f8f05b9d043cea958`; Pre-Unreal #1122 completed SUCCESS and there were no open PRs targeting `develop`.
- This is administrative/onboarding only. It changes no gameplay/runtime/source asset behavior and creates no PIE/device/visual/performance acceptance.
- Evidence boundary: **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD PRE-UNREAL PENDING**.

## 2026-09-27 - Validator self-repair after cleanup-parser repair

- Pre-Unreal #1120 failed before project validation because the newly-added PG-167 parser-regression guard itself was malformed by the same unsafe text-splice method used in the prior cleanup optimization.
- Failure class: **VALIDATOR_POLICY / ADMIN_GOVERNANCE**. The restored cleanup PowerShell source remains the previously machine-proven implementation; no runtime/gameplay file changed.
- To avoid compounding the failure with another ad-hoc validator mutation, `Scripts/pre_unreal_validate.py` is restored exactly to the last develop-proven version from `77f4c01b625b426c27c08958b1f6468412ec1eaf`.
- The permanent policy still lives in DEC-042 and the merged post-merge cleanup workflow; this repair only restores validator integrity.
- Evidence boundary: **SOURCE CORRECTED / FRESH EXACT-HEAD PRE-UNREAL PENDING**.

## 2026-09-27 - Branch Cleanup parser regression closed before production resume

- Post-merge Branch Cleanup #12 failed in `Scripts/run_branch_cleanup.ps1` before deleting any branch because the attempted remote-enumeration optimization accidentally spliced `function Remove-RemoteBranch` into the `refs/heads/(.+)$` regex and duplicated the function body.
- Failure class: **CI_INFRA / ADMIN_GOVERNANCE**, not GAME_RUNTIME. The exact develop head still passed Pre-Unreal #1119.
- The cleanup script is restored to the previously machine-proven implementation from develop@4844e484, which already produced Branch Cleanup #11 SUCCESS and deleted 8 zero-ahead refs.
- The new post-merge trigger and empty historical delete backlog remain in force, so the restored script no longer pays the old 66-ref repeated-check cost.
- PG-167 now additionally rejects duplicate `Remove-RemoteBranch` definitions, missing/duplicated remote-ref parser lines, and the exact corruption signature seen in #12.
- Evidence boundary: **SOURCE CORRECTED / FRESH EXACT-HEAD PRE-UNREAL + POST-MERGE CLEANUP PROOF PENDING**. No runtime/PIE/device/visual/performance claim is created.

## 2026-09-27 - Permanent branch closeout agreement + interconnected-systems reassessment

- Owner direction is now a durable DEC-042 invariant: every completed temporary branch is exact-head validated, merged into `develop` immediately, then its remote ref is deleted. `develop` must not lag completed work. Only active PR heads or verified unique-unsalvaged branches may remain temporarily.
- Branch Cleanup is machine-guarded to run on merged-PR closeout, not ordinary develop pushes; it targets the merge commit, performs one live remote enumeration, preserves active/protected/unique branches, and removes merged/zero-ahead refs.
- Governor transport clutter was reduced: stale branch/PR snapshots are no longer execution inputs; GitHub owns live transport state while ProjectGovernor owns durable decisions, lane order and evidence boundaries.
- Quick static cross-system review found the ownership chain coherent: `ChapterWorldRouter` owns commit/rollback; `ShireChapterAssetStreamingSubsystem` owns async pending/resident asset handles; `ShireNPCContextSubsystem` consumes only committed world context; `LivingWorldDirector` applies life only after committed revision and pools ambient NPCs; checkpoint writes guard stale callbacks by committed context/revision.
- Build-file audit remains clean: no tracked generated Binaries/Intermediate/Saved/DerivedDataCache/.vs/StagedBuilds/PDB/log/tmp/cache debris. Production source assets are not deleted blindly; animated final promotion remains FBX-only.
- No concrete cross-system ownership cycle or new build-blocking architecture defect was found in this quick static reassessment. Production remains the active lane; root/administrative repair reopens only on concrete regression evidence.
- Evidence boundary: **STATIC-VALIDATED CANDIDATE / FRESH PRE-UNREAL PENDING**. No PIE/device/visual/performance acceptance is created.

## 2026-09-27 - Dead-branch cleanup made automatic and non-repetitive

- The remaining self-cleanup gap is closed: Branch Cleanup now triggers after every merged PR and runs only for `merged == true`; manual dispatch remains available.
- The old 66-entry historical `delete_after_merge` backlog is cleared. Cleanup no longer spends time rechecking already-absent branches on every run.
- The cleanup script now enumerates remote refs once per run and reuses that set for explicit and zero-ahead deletion instead of issuing a separate `git ls-remote` query for each historical branch.
- Zero-ahead auto-prune, active-PR protection, protected/salvage preservation and unique-commit retention remain fail-closed.
- This closes the concrete speed/cleanup regression discovered after PR #105 left its merged branch ref alive until another cleanup run.
- Evidence boundary: **SOURCE-IMPLEMENTED / FRESH PRE-UNREAL + POST-MERGE CLEANUP PROOF PENDING**. No runtime/PIE/device/visual/performance claim is created.

## 2026-09-27 - Post-D production resume gate

- D is complete at the machine-validation level: `develop@1066cf022723fcdef9bfac66519f5b0f9c1e03a4` passed Pre-Unreal #1109 and Unreal Build #893.
- The later cleanup/governance-only head `017c3bc26ecfa1dadc75f10398ead01b5fe0ca22` passed Branch Cleanup #11 and Pre-Unreal #1113. Branch Cleanup removed 8 dead refs and the repository now retains only `develop`, `main`, and six branches with unique commits preserved for selective salvage.
- Warehouse #264 is SUCCESS after the cleanup-shell repair.
- Repository-tree audit found no tracked generated build junk under Binaries/Intermediate/Saved/DerivedDataCache/.vs/StagedBuilds and no tracked PDB/log/tmp/cache artifacts. `SourceAssets/Production` remains source input and is not deleted blindly.
- The Governor is advanced past D. The next production order is: bounded evidence-backed Mega Asset Promotion/import-integration, then character presentation/skeletal-animation coverage, then Living Shire motion/fauna + quest/audio polish, with target-device profiling before density/expensive presentation expansion.
- Administrative/root-repair work is no longer the active lane and may reopen only on concrete regression evidence.
- Evidence boundary: **READY_FOR_SUBSTANTIVE_BUILD / STATIC + UE4 MACHINE PROOF AVAILABLE**. This is not PIE/device/visual/performance acceptance.

## 2026-09-27 - Dead-branch cleanup root cause fixed

- Live GitHub audit found the real gap: cleanup depended on a historical static `delete_after_merge` list, so newer merged branches created after that list could remain indefinitely even though DEC-042 required self-cleanup.
- Verified zero-ahead refs queued for permanent deletion are `ci/fix-pwsh-cleanup-shells-v1`, `fix/character-rig-callback-ownership`, `ops/new-developer-entry-v1`, `production/p1c01-c3-foliage-identity-v1`, `production/p1c01-c4-foliage-evidence-v1`, `production/p1c01-c4-foliage-lod-cull-v1`, and `production/p1c01-d-lighting-water-mega-promotion-v1`.
- Branch Cleanup now enumerates live remote refs every run and auto-deletes only refs that are not protected, are not active PR heads, and GitHub reports as exactly `ahead_by == 0` versus `develop`. The historical explicit list is now only a supplemental deletion queue.
- Divergent refs with unique commits are not destroyed blindly. Six currently have unique commits and are protected for selective salvage/supersession review: actions-budget (7 ahead), daily-project-manager (4), mega-production-resume (19), localization prototype (6), P1C01 mega-prep (2), and mega-promotion-audit (4).
- This repair branch `maintenance/root-auto-prune-v1` is itself queued for post-merge deletion so the fix cannot leave another dead ref behind.
- PG-167 now guards the automatic zero-ahead discovery markers to prevent regression to manual-only cleanup.
- Evidence boundary: **STATIC-VALIDATED CANDIDATE / FRESH PRE-UNREAL + POST-MERGE BRANCH-CLEANUP EXECUTION PENDING**. No gameplay/runtime/PIE/device/visual/performance claim is created.

## 2026-09-27 - Self-hosted cleanup shell false-red repair

- Branch Cleanup #9 completed its real cleanup logic and printed `BRANCH_CLEANUP_PASS deletedPlanCount=58 activePrHeads=0 planProtected=4 canonical=develop stable=main`, then the job was marked failed only because the final cleanup step used `shell: pwsh` and this Windows runner does not expose a `pwsh` executable.
- Warehouse Stage #263 successfully reused/staged all provider batches, passed `WAREHOUSE_INVENTORY_AUDIT_PASS payloadFiles=247 bytes=3851680492 receipts=13 receiptRecords=667 duplicateGroups=215`, and printed `WAREHOUSE_FOOTPRINT files=261 bytes=3852292570`; it likewise failed only at the final `pwsh` cleanup wrapper.
- Runner Health used the same unsupported cleanup shell and is corrected in the same atomic administrative wave.
- All three isolated-temp cleanup steps now use the workflow's native `cmd` shell with bounded `rmdir /S /Q`; no Unreal workspace, persistent warehouse payload, runtime/gameplay source, or validation acceptance criteria are changed.
- Failure class: **CI_INFRA cleanup-wrapper defect**, not GAME_RUNTIME and not warehouse-content failure.
- Evidence boundary: **SOURCE CORRECTED / FRESH ADMIN WORKFLOW EXECUTION PENDING**. No PIE/device/visual/performance acceptance is created.

## 2026-09-27 - D branch reconciled with merged CI architecture

- PR #102 is merged to `develop@0afcc3000b06179086215386fbc95247dff15d03`; its isolated/persistent CI architecture is retained as the new integration parent.
- PR #101 D runtime/content changes are preserved without reverting the CI/governance fixes. The D branch is reconciled as a two-parent merge rather than force-rebased.
- Historical D head `65f3c687f1f05d378431c206ce726f3a50652135` had Pre-Unreal #1079 SUCCESS and Unreal Build #884 SUCCESS, but that evidence does not certify the new reconciled head.
- Fresh exact-head Pre-Unreal and the UE4.27.2 validation lane are required on the reconciled head before PR #101 can merge.
- Mega Asset Promotion remains bounded to staging/intake QC unless item-level provenance, license/entitlement, local staging receipt, SHA256 and class-specific QC support further promotion.
- Evidence boundary: **RECONCILED SOURCE CANDIDATE / FRESH EXACT-HEAD MACHINE PROOF PENDING**. No PIE/device/visual/pacing/performance acceptance is claimed.

## 2026-09-26 - D exact-head guard/count correction after #1074/#879

- Exact D head `093c4950802eb9f58813dc232c9fffa5f6103f02` reached UE4.27.2 build/import/runtime execution before two guard-only failures.
- Pre-Unreal #1074 failed PG-172 because the new validator incorrectly required exactly one `RecaptureSky()` call. The existing P1C01 architecture has two bounded call sites: startup configuration plus event-driven authored story-atmosphere refresh. There is still no Actor Tick or free-running day/night recapture.
- Unreal Build #879 compiled and imported successfully; production import reported `376 files, 0 failures`. Startup, P1C01-P1C08, state, transitions, faults, pending-transition and persistence-edge runtime sweeps all reported passed. Warning debt also passed with zero tracked production/runtime debt.
- #879 failed only at the later package streaming preflight because the old script hard-coded 238 unique production packages while D correctly added `M_ProductionWater`, producing 239.
- The package preflight now reads the explicit audited `audit.total_unique_production_packages` manifest field and compares the independently reconstructed unique package set against it. The recorded D value is **239**.
- Evidence boundary: the failed runs provide concrete compile/import/runtime observations but do **not** make the D head accepted. Fresh exact-head Pre-Unreal + UE4.27.2 validation is required after these corrections; no device/visual/performance acceptance is claimed.

## 2026-09-26 - P1C01 D implementation candidate + Mega Asset Promotion launch

- D is now the sole runtime-changing W01/P1C01 lane on `production/p1c01-d-lighting-water-mega-promotion-v1`, based on merged C4 develop `2845071119d926defd6ba94c970f43729bc51674`.
- The existing fixed-state lighting stack remains bounded and event-driven: one primary directional sun strategy, SkyAtmosphere, non-volumetric ExponentialHeightFog, one startup skylight recapture, and no Actor Tick/day-night loop.
- A new project-owned `M_ProductionWater` is created by the editor import pipeline as a texture-free opaque DefaultLit material with color/roughness/metallic/specular parameters. It adds no WPO, translucency, scene capture or planar reflection path.
- P1C01's async chapter bank now owns `/Game/Production/Materials/M_ProductionWater.M_ProductionWater`; `AShirePrototypeWorldBuilder` only resolves the committed resident object and retains the existing lightweight blue fallback if it is absent.
- The two already-established water surfaces are upgraded without topology change: **The Water beside the Mill** and **the Brandywine at Bucklebury Ferry**. Both remain collision-free, cast no shadow, and add no per-frame CPU simulation.
- Quest/save/story state, traversal anchors, LivingWorldDirector ambient ownership, NPC pooling, C2/C3/C4 foliage density/material identity/cull ownership, and broad Part I/II/III runtime scope are unchanged.
- PG-172 guards D against synchronous runtime loading, repeated skylight recapture, Actor Tick, planar-reflection and scene-capture regressions. PG-173 guards Mega Asset Promotion against evidence-free promotion.
- Mega Asset Promotion is **launched only for staging/intake QC** using the existing queue and promotion policy. No candidate state has been advanced by metadata alone; READY_FOR_IMPORT still requires provenance/license, local staging receipt, SHA256 and class-specific QC.
- Prior C4 proof used to open this lane: exact candidate `bc1e04062d8079fef73eae64f68c81772b4fc56c` passed Pre-Unreal #1070 and Unreal Build #875 before merge.
- Evidence boundary for this D candidate: **SOURCE-IMPLEMENTED / EXACT-HEAD MACHINE PROOF PENDING**. No new PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED, PACING-ACCEPTED or PERFORMANCE-ACCEPTED claim is made.

## 2026-09-27 - Deep-audit command recognizer aligned to isolated Pre-Unreal

- Pre-Unreal #1105 reached the new head `2bcec3528619f07bd8917385d818d7a9be384d4c` through the persistent isolated checkout; exact-head checkout, classifier tests, project-structure validation, Project Governor, strict asset audit and production-readiness audit all passed.
- #1105 then failed only in `deep_project_audit.py` with `Pre-Unreal workflow does not fail closed on structural asset-quality defects`.
- The strict audit command was actually executed successfully in the same run as `cd /d "%SHIRE_PRE_ROOT%" && "%PYTHON_EXE%" Scripts\\asset_quality_audit.py --strict`; the shared recognizer still accepted only the pre-isolation slash-only command shape.
- `source_contracts.has_strict_asset_audit_command` now recognizes the isolated cmd working-directory prefix and either slash direction while retaining full-line rejection of comments, echo wrappers and failure-masking suffixes. Regression tests cover the exact Windows isolated command and the `|| true` rejection.
- This is VALIDATOR_POLICY only. No gameplay/runtime/import/cook/package code changed, and no Unreal build is requested for this repair.
- Evidence boundary: **STATIC VALIDATOR REPAIR / FRESH PRE-UNREAL EXACT-HEAD RERUN PENDING**.

## 2026-09-27 - PG-167 final queue-isolation guard repair

- Live PR state showed the branch had already advanced to `95dcdad171eb36b1309dadf248f9b1f98f12a05c` with the first PG-134/PG-167 repair commit.
- Pre-Unreal #1104 proved exact-head isolated persistent checkout and all classifier cases passed at that head.
- #1104 then failed only in project-structure validation with the exact stale policy requirement: `PG-167 Unreal queue-isolation contract missing: ${{ startsWith(github.head_ref, 'acceptance/') || startsWith(github.head_ref, 'production/') }}`.
- The remaining PG-167 queue-isolation guard now requires the adopted branch-scoped Unreal concurrency group plus `cancel-in-progress: ${{ github.event_name == 'pull_request' }}`, matching same-PR superseded-run cancellation.
- This wave changes validator policy/docs only. It does not request C++/import/runtime/cook/package work and does not create PIE/device/visual/performance evidence.
- Evidence boundary: **STATIC VALIDATOR PATCH / FRESH PRE-UNREAL EXACT-HEAD RERUN PENDING**.

## 2026-09-27 - Validator contracts aligned to isolated CI architecture

- Pre-Unreal #1103 proved the isolated persistent checkout path itself works and exact-head verification passes.
- Its failure was VALIDATOR_POLICY only: PG-134/PG-167 still required pre-rearchitecture implementation details.
- PG-134 now validates the stable invariant: strict asset audit runs from the isolated persistent static checkout and the Unreal workspace cannot be deleted.
- PG-167 now requires Branch Cleanup isolation instead of the interactive UE4 runner-health probe, and recognizes branch-scoped same-PR Unreal cancellation.
- No runtime/gameplay code, story, movement, save, streaming or package behavior changed.
- Evidence boundary: **STATIC VALIDATOR REPAIR / FRESH PRE-UNREAL RUN PENDING**.

## 2026-09-26 - Persistent isolated Pre-Unreal checkout refinement

- Isolation protected the Unreal workspace, but a fresh temporary Git repository still repeats repository transfer on every static validation.
- Pre-Unreal now keeps a dedicated source checkout at `C:\actions-runner\_ci\pre-unreal`, physically separate from the Unreal build workspace.
- Every run still fetches the exact target SHA, hard-resets to it, verifies HEAD equality and reruns all static/governance/source-quality checks.
- Only the static Git object database persists so unchanged objects can be reused; Unreal `Intermediate`, `Binaries` and engine acceptance evidence are not shared through this lane.
- Authenticated remote URL is scrubbed after exact checkout and again in the always-run cleanup step.
- Evidence boundary: **SOURCE IMPLEMENTED / FRESH TIMING MEASUREMENT PENDING**.

## 2026-09-26 - CI architecture reassessment and lane isolation

- Comprehensive review concluded that the project quality direction is correct, but CI ownership was causing self-inflicted rebuilds and misleading red runs.
- Recent reviewed window: 31 Unreal runs = 11 success / 17 cancelled / 3 failure; 31 Pre-Unreal runs = 11 success / 16 cancelled / 4 failure.
- Major root cause: Pre-Unreal, Runner Health and Branch Cleanup could delete the same self-hosted GITHUB_WORKSPACE used by Unreal; Warehouse could delete its root .git. This destroyed Git/UBT incremental continuity.
- Architecture is now redefined so Unreal Build Validation exclusively owns the persistent project workspace. Pre-Unreal, Runner Health, Branch Cleanup and Warehouse source checkouts use isolated RUNNER_TEMP directories.
- Pre-Unreal remains self-hosted to avoid hosted-runner billing/capacity dependency; hosted Windows was tested and failed before step execution, so it is not part of the production architecture.
- Failure triage is standardized as GAME_RUNTIME / VALIDATOR_POLICY / CI_INFRA / ADMIN_GOVERNANCE before runtime code is changed.
- Coherent waves should use one atomic multi-file commit when possible to reduce superseded workflow churn.
- Full runtime/story/save/streaming/package gates remain intact for relevant deltas; no quality gate was removed.
- Canonical review: `Docs/CI_ARCHITECTURE_REASSESSMENT_2026-09-26.md`.
- Evidence boundary: **SOURCE/ARCHITECTURE REASSESSED; FRESH TIMING MEASUREMENT PENDING**. No PIE/device/visual/performance acceptance is implied.

## 2026-09-26 - Unreal CI root acceleration implemented

- Measured logs confirmed three independent sources of wasted time: #888 spent about 11 minutes in exact checkout before cancellation; administrative PR heads repeatedly entered FULL Unreal; and repeated editor builds recreated the UBT makefile and compiled 76 actions at roughly 238-252 seconds each.
- Unreal PR concurrency is now branch-scoped. A newer SHA cancels only an older run from the same PR branch; it cannot cancel D/develop or another runtime PR.
- Unreal Build Validation no longer triggers for README/onboarding/handoff/classifier-test administrative-only changes. Pre-Unreal still validates those files.
- Exact checkout no longer deletes the repository .git metadata. It reuses the self-hosted workspace, fetches with a 1000 B/s for 20 s low-speed cutoff, limits attempts to three, hard-resets/checks out the exact TARGET_SHA, verifies HEAD equality, then scrubs the authenticated remote URL.
- The validation classifier now supports exact Git-tree proof reuse. A merge SHA may inherit core proof only when its tree SHA exactly equals a parent tree SHA that has the required green Unreal proof. This addresses the real C4 case where merged develop and the proven C4 candidate have the same tree object but different commit SHAs.
- Unreal workflow/classifier/pre-unreal orchestration changes are treated as validation-policy-only when no runtime delta exists. They exercise exact checkout/classification/Pre-Unreal but do not rebuild/import/package simply to validate CI policy.
- Packaging scripts themselves remain acceptance-impacting. Config, Build.cs, Target.cs, chapter-streaming, cook/package/release and unknown-impact paths remain fail-safe FULL.
- Compile parallelism remains MaxParallelActions=1 for now; no blind binary cache or RAM-risk increase is introduced. First measure gains from removing redundant work.
- PG-175 guards the bounded fetch, preserved Git checkout, administrative trigger exclusions, same-PR cancellation and exact tree-equivalent proof markers.
- Evidence boundary: **CI ARCHITECTURE IMPLEMENTED / FRESH MEASUREMENT PENDING**. No runtime, PIE, device, visual, pacing or performance acceptance is created by this optimization.

## 2026-09-26 - Persistent work-session handoff

- Owner requested that the current conversation state be preserved with the project so a later session can continue without rediscovering the same CI/production issues.
- Canonical continuation note: `Docs/WORK_SESSION_HANDOFF_2026-09-26.md`.
- It records the measured PR102 CI latency, unnecessary FULL Unreal classification root cause, the #888 stalled-checkout cause/cancellation, #1083 success, #889 pending corrected measurement, and the GAME vs VALIDATOR vs CI/INFRA vs ADMIN failure-classification rule.
- It also records the architectural policy: remove duplicate truth and magic constants, derive mutable counts from authoritative manifests, keep runtime safety strict, and prevent trivial administration from repeatedly blocking D + Mega Asset Promotion.
- Evidence boundary: documentation/handoff only; no new runtime, PIE, device, visual, pacing or performance acceptance is created.

## 2026-09-26 - Single new-developer / AI-session entry path

- `README.md` is now the single repository entry point for a new human programmer, a new AI session, or a developer returning after a long break.
- The canonical reading path is: `README` → `PROJECT_GOVERNOR` → `ProjectGovernor.json` → `CURRENT_PROJECT_STATE` → `DEVELOPMENT_GATES` → `PROJECT_GUARDIAN`.
- Added `Scripts/new_developer_onboarding.ps1`. It reads current Governor + Git state and prints authority, branch/HEAD, active lane/gate, benchmark, next actions, target hardware, required reading and evidence boundary.
- The onboarding script is read-only project guidance; it is not a second manager and does not copy live PR numbers into governance.
- ProjectGovernor handoff/next-actions were reconciled from old C3/C4 wording to the current train: **D lighting/sky/fog/low-cost water next + Mega Asset Promotion in parallel**.
- PG-174 now guards the README entry path and onboarding-script contract so later maintenance cannot silently remove the manager entrance.
- Evidence boundary: onboarding/governance change only. It does not create new PIE/device/visual/performance acceptance.

## 2026-09-26 - Historical foliage guards decoupled from mutable phase labels

- Final C4 closure exposed a validator design defect: PG-165/166 still required the overall materials/vegetation plan to retain a C1/C2-era top-level status, so legitimate progress to C4 was rejected even though C1/C2 invariants remained intact.
- PG-165 now validates the durable C1 albedo/master-surface contract instead of freezing the plan at an old phase label.
- PG-166 now validates recorded C2 machine evidence plus wind/performance invariants instead of requiring the top-level plan status to remain `C2_FOLIAGE_WIND_EXACT_HEAD_GREEN_MERGED_C3_READY`.
- PG-171 accepts the prepared state or any explicit `C4_...` state while still enforcing all C4 source/evidence invariants and forbidding premature far-parent binding.
- This prevents future D/later phase progression from reopening old C1/C2 validation failures solely because the project advanced.
- Evidence boundary: validator repair only; fresh exact-head Pre-Unreal is required after this change. Unreal #873 already succeeded on the immediately preceding closure head.

## 2026-09-26 - P1C01 C4 machine closure / D next

- C4 candidate machine evidence: Pre-Unreal #1064 SUCCESS + Unreal Build #869 SUCCESS on `e881b32da6ae9713ccc096e8f213056aeef6af76`.
- UE4.27 production import completed with `376 files, 0 failures`; warning debt returned to `defaultMat references = 0`.
- Concrete C4 foliage evidence: all five audited P1C01 foliage meshes expose `lodCount=1` only. Grass/Hedge/Shrub/TreeCanopy remain near/mid on `M_ProductionFoliage`; TreeTrunk remains on `M_ProductionSurface` with authored `Bark`.
- Because no `lodIndex > 0` exists, C4 closes with **NO far-parent binding**. `M_ProductionFoliageFar` remains available but unused until a real far LOD asset/section exists.
- Existing HISM/ISM cull bands and foliage density remain unchanged.
- C4 does not establish target-device overdraw/FPS acceptance; that remains a later profiling gate.
- Next production drop after merge: **D — fixed-state lighting / sky / fog / low-cost water**.
- Evidence state: machine-green / COMPILE-TESTED and import-observed. No new PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED, PACING-ACCEPTED, or PERFORMANCE-ACCEPTED claim.

## 2026-09-26 - C4 source-material debt repair

- C4 engine evidence exposed a real existing source-asset defect rather than a C4 runtime regression: `SM_ShTreeCanopy.obj` and `SM_ShTreeTrunk.obj` had no authored `mtllib/usemtl` declarations, so UE4.27 imported their only material slot as `defaultMat` / WorldGridMaterial.
- `SM_ShTreeCanopy.obj` now references `ShireMaterials.mtl` and uses authored material identity `Leaves`.
- `SM_ShTreeTrunk.obj` now references `ShireMaterials.mtl` and uses authored material identity `Bark`.
- The zero-tolerance warning-debt guard was not weakened or bypassed.
- C4 still performs no far-parent rebind, no foliage density increase, and no gameplay/save/LivingWorld ownership change.
- Evidence boundary: source repair is **STATIC-VALIDATED candidate** only until the refreshed exact-head Pre-Unreal and UE4.27.2 production import/build succeed.

## 2026-09-26 - P1C01 C4 foliage LOD/cull/overdraw evidence capture implemented

- Candidate branch `production/p1c01-c4-foliage-lod-cull-v1` starts C4 only after merged C3 and merged-develop exact-head machine proof.
- UE4.27 production import now audits exact P1C01 foliage mesh identities after import: `SM_ShGrassClump`, `SM_ShHedge`, `SM_ShShrub`, `SM_ShTreeCanopy`, and `SM_ShTreeTrunk`.
- For every imported foliage mesh LOD section, the commandlet emits `C4_FOLIAGE_EVIDENCE` with LOD count/index, section/material indices, authored material identity, current parent, proposed parent, decision and reason.
- Only a real `lodIndex > 0` plus an approved foliage material identity can become `FAR_LOD_ELIGIBLE_FOR_REVIEW`.
- This evidence-capture step performs no far-parent rebind. `M_ProductionFoliageFar` remains unused unless engine evidence proves a qualifying far LOD.
- Existing HISM cull bands remain unchanged: grass 1200/5200, flowers 800/3200, shrubs 1500/6500, distant tree trunk/canopy 5000/19000; no density increase.
- Gameplay IDs, save/quest state, LivingWorld ownership, collision ownership and deterministic asset paths are unchanged.
- Evidence boundary: **STATIC-VALIDATED candidate implementation** only. Exact-head Pre-Unreal + UE4.27.2 production import evidence is still required. No PIE/device/visual/performance acceptance is claimed.

## 2026-09-26 - Root administrative blocker removal / thread consolidation

- Owner direction: stop recurring stale-Governor/old-PR/board mismatch failures at the root and reduce parallel administrative threads.
- `Scripts/project_governor.py` no longer treats volatile PR numbers or candidate branch names as fail-closed Governor truth. GitHub is the live authority for PR/branch/open/mergeable/workflow transport state.
- `Data/ProjectGovernor.json` remains authoritative for durable requirements, priorities, active lane/gate, decisions and evidence boundaries.
- PG-150 now checks authority semantics instead of exact PR/branch mirroring across human-readable files.
- New PG-170 regression guard rejects reintroduction of the old PR/branch mismatch failure strings and requires branch-cleanup empty/open-PR response hardening.
- `Scripts/run_branch_cleanup.ps1` now safely handles API results that do not expose `head.ref` under PowerShell StrictMode.
- Failure discipline is lane-scoped: a real runtime/integration failure blocks that affected lane, while unrelated safe source/PDF/warehouse/design preparation may continue.
- W00 remains closed unless concrete regression evidence reopens it.
- The 24-hour Project Manager report remains informational and never blocks production.
- C3 foliage identity implementation remains the active runtime change on PR #98.
- Evidence boundary: these governance/maintenance changes are source-level only until exact-head validation completes; no PIE/device/visual/performance acceptance is claimed.

## 2026-09-26 - P1C01 C3 stable foliage identity implemented

- Candidate branch `production/p1c01-c3-foliage-identity-v1` implements the prepared C3 contract in `ShireProductionImportCommandlet.cpp`.
- Exact approved authored material identities are limited to `Grass`, `Leaves`, `LeafGreen`, and `LeafGold` after trimming.
- Approved identities bind their deterministic material instances to `M_ProductionFoliage`; all other authored identities remain on `M_ProductionSurface`.
- `M_ProductionFoliageFar` remains unassigned in C3 and stays reserved for C4 after mesh/LOD/cull evidence.
- Existing material instance object paths, AlbedoTexture bindings, Color/Roughness/Metallic values, world ownership, HISM/ISM population and foliage density are unchanged.
- Pre-Unreal PG-169 now guards the exact identity set and rejects broad `Contains("Leaf")` / `Contains("Grass")` classification and premature far-parent binding.
- Evidence boundary: **STATIC-VALIDATED candidate implementation** only until exact-head Pre-Unreal and UE4.27.2 asset/editor validation succeed. No PIE/device/visual/performance acceptance is claimed.

## 2026-09-26 - Post-C2 root cleanup and C3 launch gate
- Governor stale-control reconciliation: historical PR #53/V6 repair wording and the already-completed Public/Private migration were removed from active/missing work; W00 stabilization and source migration are recorded closed, while real profiling/pooling/async-load audit debt remains open.
- Classifier root fix: `Scripts/run_branch_cleanup.ps1` is now governance-safe when Unreal is otherwise awakened; cleanup-script maintenance may no longer force FULL/Cook/Package by falling through as an unclassified file.
- Classifier contract unified: all 15 exact maintenance scripts excluded by the Unreal workflow are now safe in both main classification and transitive-core proof; co-changes can no longer promote them to FULL by omission.
- PG-078 roadmap snapshot reconciled directly from current Governor after closing historical W00 stability work; the guard remains fail-closed against future active-work drift.





- C2 final PR head `fd521dc308580fc44d0cdfdfed24273bacc37ff9` passed Pre-Unreal #1030 and Unreal Build #837.
- C2 merged as `1d0580926299e4fac635bcb847343a49c444d4f1`; merged develop then passed Pre-Unreal #1031 and Unreal Build #838.
- Evidence status: **COMPILE-TESTED + exact-head automated import/QA/startup machine green**. No PIE/device/visual/performance acceptance is claimed.
- Root cleanup removes audited superseded CI/C2/warehouse refs and protects the two future-planning salvage branches that still contain content absent from develop.
- C3 is prepared but runtime-not-started; it may begin only after Branch Cleanup succeeds and the survivor set is rechecked.

## 2026-09-26 - C2 Governor handoff coherence correction

- Pre-Unreal #1029 on `981996e62d3c595783bb80a43aee2352aeb65541` passed exact-head checkout, runner health, and PRE-UNREAL CORE VALIDATION, then failed `project_governor.py` with: `Legacy verified handoff must refer to the same last-green baseline`.
- Root cause: the C2 rebase preparation incorrectly reused `session_handoff.source_head` for the current rebase parent. The Governor contract defines that legacy field as the last verified green baseline.
- Correction: `session_handoff.source_head` is restored to `712a81cac150b7fdb338a4cf7554d4f27d4b5191`; the current C2 rebase parent remains correctly recorded in `integration_train.baseline=f4028a89f7d2c541cddcb987f43963be87e944e0`.
- No C2 importer/material code changes are made by this correction. The branch remains one atomic C2 commit above hardened develop after the head rewrite.
- Evidence boundary: **STATIC-VALIDATED CONTRACT CORRECTION; fresh exact-head Pre-Unreal and Fast Asset Lane required**. No PIE/device/visual/performance acceptance is claimed.

## 2026-09-26 - C2 foliage wind rebased onto hardened develop

- PR #87 remains the sole runtime-changing C2 lane and is rebuilt from `develop@f4028a89f7d2c541cddcb987f43963be87e944e0` rather than carrying its old infrastructure/governor snapshot.
- C2 creates `M_ProductionFoliage` using UE4.27 SimpleGrassWind through `UMaterialExpressionMaterialFunctionCall` with `WindIntensity`, `WindSpeed`, and `WindWeight`.
- `M_ProductionFoliageFar` intentionally has no WPO. Foliage density is unchanged and no Actor Tick is added.
- C3 stable material identity and C4 LOD/cull/overdraw remain blocked until C2 exact-head Fast Asset Lane is green and C2 is merged.
- The transplanted importer blob is exactly `66f12ff5926b96118f59fbc3cab893ebd01f6fff`, which has historical Pre-Unreal #924 + Unreal #759 evidence; this rebased PR head still requires fresh exact-head proof.
- Evidence boundary: **STATIC-VALIDATED REBASE CANDIDATE; exact-head Pre-Unreal/Fast Asset Lane pending**. No PIE/device/visual/performance acceptance is claimed.

## 2026-09-26 - Runner network health false-negative hardening

- Pre-Unreal #1026 on `develop@8131166025fcceed7102e9a33844bd5e6f864cae` completed exact-head Git checkout and passed runner identity/service/watchdog/process ownership checks before one `github.com:443` probe returned false.
- The runner network gate is now bounded and retrying: three TCP attempts to `github.com:443`, five seconds maximum per attempt, with a two-second delay between failed attempts.
- The gate remains fail-closed: `RUNNER_HEALTH_FAIL github-443-unreachable` is emitted only after all three bounded attempts fail. Each attempt reports `RUNNER_HEALTH_NETWORK_ATTEMPT` and a success reports `RUNNER_HEALTH_NETWORK_PASS`.
- PG-145B now guards the bounded TCP/retry markers rather than requiring the previous single `Test-NetConnection` call.
- `Scripts/verify_runner_session.ps1` and `Scripts/pre_unreal_validate.py` remain excluded from the Unreal Build push/PR device lane, so this maintenance fix must not trigger FULL Unreal validation.
- Evidence boundary: **STATIC-VALIDATED SOURCE CHANGE; fresh exact-head Pre-Unreal proof pending**. No PIE, device, visual or performance acceptance is claimed.

## 2026-09-26 - Maintenance-only Unreal trigger closure

- Added `Data/BranchCleanupPlan.json` and `Scripts/run_branch_cleanup.ps1` to both push and PR `paths-ignore` in Unreal Build Validation.
- These branch-hygiene files are static/maintenance-only and must stay on Pre-Unreal; they must not consume the UE4 build device.
- PG-167 now guards both exclusions so the heavy Unreal lane cannot be re-triggered by branch-cleanup maintenance.
- Evidence boundary: **STATIC-VALIDATED SOURCE CHANGE; fresh Pre-Unreal proof pending**.

## 2026-09-26 - Final CI/branch-hygiene hardening before production resumes

- Removed the last known marketplace checkout dependencies from the self-hosted maintenance lanes: Branch Cleanup and Runner Health now use bounded local exact-head Git acquisition with three attempts and a 20-second low-speed cutoff.
- Branch Cleanup no longer uses the implicit `shell: powershell`; it calls an explicit `-NoProfile -ExecutionPolicy Bypass` script after runner-health verification.
- Added `Scripts/run_branch_cleanup.ps1`: cleanup now refuses protected refs, refuses any active PR head discovered from the GitHub API, treats already-absent approved refs as clean, hard-fails real deletion errors, and verifies `develop` plus `main` remain.
- BranchCleanupPlan is synchronized to the current runtime lane: PR #87 / `production/w01-p1c01-foliage-wind-v3`. Identical stale `ci/validator-sync-v5` and PR #90's infrastructure branch are approved for deletion after integration.
- PG-167 now guards these maintenance workflows against reintroducing marketplace checkout/raw PowerShell failure modes.
- Pre-Unreal #1023 already passed exact-head checkout, runner health, Governor and all static audits on `c408c4c85d8bde3afbd805545401667442b6af34` in under one minute; this new maintenance hardening still requires its own fresh static pass before merge.
- Evidence boundary: **STATIC-VALIDATED SOURCE CHANGE + prior exact-head Pre-Unreal success; fresh exact-head proof for this final hardening pending**. No PIE/device/visual/performance acceptance is claimed.

## 2026-09-26 - PG-145B false-negative correction

- Pre-Unreal #1020 proved runner session health and local Python resolution passed, then failed only because the static validator incorrectly searched `verify_runner_session.ps1` for three watchdog-only symbols: `WorkerIdleHangSeconds`, `Listening for Jobs`, and `stale-worker`.
- PG-145B now validates session/ownership markers in `verify_runner_session.ps1` and stale-worker/broker-listening recovery markers in `runner_watchdog.ps1`, matching the actual system split.
- This is a validator correction only; it does not weaken the runner health gate.
- Evidence boundary: **STATIC-VALIDATED SOURCE CHANGE; fresh Pre-Unreal run pending**.

## 2026-09-26 - Pre-Unreal checkout freeze root fix

- Pre-Unreal #1019 was assigned to runner_id 21 but remained inside marketplace `actions/checkout@v4` until cancellation; no project validator or runner-health step executed.
- Pre-Unreal now performs a bounded local exact-head Git checkout using the already installed Git client, the PR-head SHA, three fetch attempts, a 20-second Git low-speed cutoff, hard reset to the exact SHA, SHA verification, and `ShireJourney.uproject` presence verification.
- The marketplace checkout dependency is removed from Pre-Unreal, so a stalled action download cannot consume the whole static-validation window.
- PG-167 now fails static validation if marketplace checkout is reintroduced or the bounded exact-head checkout markers disappear.
- Evidence boundary: **STATIC-VALIDATED SOURCE CHANGE; fresh Pre-Unreal machine run pending**. This infrastructure change does not imply PIE/device/visual/performance acceptance.

## 2026-09-26 - Runner health owner normalization fix

- Pre-Unreal #1017 proved the supervised job itself was running correctly on `UE4-27-Windows` as `IDEAPAD320\user` in session 1 with the legacy service stopped/manual, then the new health probe produced a false negative because Task Scheduler reported the same account as short-form `user`.
- Runner health now compares the watchdog task owner by Windows SID rather than display-name string, so `user` and `IDEAPAD320\user` resolve to the same identity without weakening the ownership check.
- Evidence boundary: source correction only until a fresh Pre-Unreal run reaches `RUNNER_HEALTH_PASS`.

## 2026-09-26 - Fast production validation lane + stale-worker recovery

- Root cause of the recurring 15-20 minute waste was split into runner acquisition/session failures and an overly broad Unreal validation lane.
- Runner watchdog now verifies broker readiness with an actual `Listening for Jobs` log marker, not merely the existence of `Runner.Listener.exe`.
- A stale `Runner.Worker` can no longer block the supervisor forever: after 300 seconds, it is recycled only when it has no descendant processes and its Worker diagnostic log has also been idle for the same window. Active build/cook/editor child processes remain protected.
- Added a narrow `asset` Unreal mode for editor-tool/P1C01 material-authoring deltas. It still performs exact-head Editor build, production import, Automation QA and startup smoke, but skips unrelated chapter/state/warning-debt audits and never Cook/Packages.
- CORE and ASSET runs no longer delete `Intermediate/Build/Win64` and `Binaries/Win64` before every build. UBT incremental dependency checking is used; the existing compiler-pressure retry still performs a clean project-intermediate reset if the build actually needs it. FULL validation remains clean-reset.
- Runtime C++, Config, Build/Target, streaming/package/cook changes remain on CORE/FULL fail-closed paths. No gameplay/streaming/performance safety gate was waived.
- The independent #1001 CRLF test defect is fixed by newline normalization and is not treated as a runner failure.
- Evidence boundary: **STATIC-VALIDATED SOURCE CHANGE / fresh supervised exact-head run pending**. No PIE, device, visual or performance acceptance is claimed from this optimization.

## 2026-09-26 - Runner health certification and false-failure separation

- Added `Scripts/verify_runner_session.ps1` as a fail-fast machine/session probe for the supervised UE4 runner.
- The probe rejects service identities (`NETWORK SERVICE` / `SYSTEM` / `LOCAL SERVICE`), session 0, missing same-session Explorer, wrong runner name, non-Manual/non-Stopped legacy runner service ownership, unhealthy watchdog ownership/state, duplicate/missing Listener, wrong Listener/Worker owner or session, GitHub:443 loss, unwritable runner temp, and missing GPU enumeration. It also reports free disk/RAM and monitor/GPU inventory.
- Pre-Unreal, Unreal Build and Warehouse Stage now run this probe before expensive work. A dedicated manual `Runner Health Check` workflow provides a one-click, sub-minute runner-only diagnostic path.
- This creates a clean fault boundary: if `RUNNER_HEALTH_PASS` occurs and a later Unreal/package step fails, the failure is no longer attributed to runner identity/session ownership without new evidence.
- Fixed the independent Pre-Unreal #1001 failure by normalizing CRLF/CR newlines in decoded Unreal logs; the failure was `READY\r\n != READY\n`, not a runner fault.
- Expanded Unreal path isolation so runner-health, runtime-smoke harness, and asset-audit maintenance remain on the fast Pre-Unreal lane and do not trigger a full UE4 build by themselves.
- Corrected the PR-side mirror of the static-only ignore list so the same runner/CI maintenance paths are excluded consistently on both push and pull_request triggers.
- Existing #823 evidence remains historical failure: the job ran as `NT AUTHORITY\NETWORK SERVICE` and packaged startup failed at D3D11 swap-chain creation `887A0022`. The newly installed watchdog/device state must produce a fresh runner-health pass before that cause is considered closed.
- Evidence boundary: **STATIC-VALIDATED SOURCE CHANGE + OWNER DEVICE INSTALL OBSERVED; FRESH GITHUB RUNNER_HEALTH_PASS PENDING**. No PIE/device/performance acceptance is claimed yet.

## 2026-09-26 - Targeted validation friction reduction and historical evidence reconciliation

Owner requested immediate removal of unnecessary blockers without weakening game construction. Four explicit static-only Python audit/helper/test paths are excluded from automatic Unreal workflow triggers for both push and PR; Pre-Unreal still runs their checks. Mixed PRs and manual dispatch can still run Unreal. Runtime source, assets, configuration and package changes retain their existing gates. No error suppression or automatic acceptance was added.

Governor REQ-SAVE-001, REQ-INTEGRATION-001 and REQ-STARTUP-001 now preserve their old missing-work lists as history and record successful machine stages from C2 head `2af6648209d8722247ca6f9a75b2b5082b6654d5`, run 36200615260. Their status remains PARTIAL. That run failed at rendered package startup (`CreateSwapChainResult`, `887A0022`, process identity NETWORK SERVICE); it does not prove current-head or human/device acceptance. Owner grounding evidence cited in active_gate still needs exact-SHA reconciliation before requirement promotion.

Validation: targeted workflow filter checks only; no new engine/device proof. Existing run 36226722585 was left running. Current work remains W01/P1C01; remaining package-session/device and human acceptance work is not waived.

## 2026-09-26 - Recurring CI failure: Python launcher contract

Exact head `1e7be3da32a9d4f8cd85297260e5abce2e9492f2`, run 36226440287, passed structure, Governor, strict asset quality and readiness checks, then failed deep audit because it searched for a literal `python Scripts/asset_quality_audit.py --strict`. The workflow now correctly uses the resolved `"%PYTHON_EXE%"` interpreter. The guard recognizes supported direct one-line run commands without accepting comments, echoed commands, missing strict mode or masked shell failures.

Validation: 11 local source-contract unit tests passed, including accepted launchers and negative command cases. Full exact-head Pre-Unreal remains pending. This changes static validation only; no runtime or performance acceptance. Governor handoff: `ci_recurrence_review_2026_09_26`. Packaged executable launch remains a separate open investigation.

## 2026-09-26 - Runner supervision + fast core validation hardening

- **Runner ownership:** interactive-user watchdog remains authoritative; legacy `actions.runner.*` service must be **Stopped / Manual**.
- **Watchdog self-heal:** AtLogOn plus five-minute repeating relaunch trigger; `MultipleInstances IgnoreNew` prevents duplicates.
- **Orphan-listener recovery:** on supervisor restart, an existing `Runner.Listener` is recycled only when no `Runner.Worker` is active; the existing 150-second acknowledged-job/no-worker recovery remains.
- **Validation speed:** CORE runtime/asset changes may inherit the nearest green core proof through an explicitly preparation-only first-parent bridge, avoiding unnecessary Cook/Package repetition.
- **Fail-closed boundary:** any unsafe intervening file blocks inheritance and forces FULL validation.
- **Device-lane isolation:** classifier/watchdog/static-validator maintenance paths are excluded from Unreal Build triggering; Pre-Unreal remains the static gate.
- **Pre-Unreal startup cost:** `actions/setup-python` removed from the supervised lane; the workflow resolves the existing local Python interpreter through `resolve_runtime_python.ps1` and runs commands under `cmd`, avoiding repeated downloads and Windows execution-policy setup failures.
- **Warehouse PR repetition:** REMOVED; real staging is triggered only after merge/push to `develop` (or manual dispatch), not on every PR synchronization.
- **Observed C2 evidence before hardening:** Unreal #821 on `2af6648209d8722247ca6f9a75b2b5082b6654d5` passed Editor build, production import, Automation QA, startup/chapter/state audits, warning guard, Cook and Runtime Data verification, then failed at packaged executable launch. The run is **not green**.
- **Evidence state for this hardening change:** STATIC-VALIDATED SOURCE CHANGE / supervised-device reinstall and next-run proof pending. No PIE/DEVICE/VISUAL/PERFORMANCE acceptance is claimed.

## 2026-09-26 - P1C01 warehouse material staging V4

- **Poly Haven manifest:** V4 / all authorized slugs have source-page records.
- **Resolution:** 2K staging target.
- **High-poly/displacement:** excluded.
- **Execution:** warehouse staging workflow queued by this manifest delta.
- **Evidence:** AUTHORIZED_FOR_STAGING / QUEUED only; receipt required for STAGED.

## 2026-09-26 - Warehouse staging execution repair

- **REQ-STABILITY-004 / DEC-044:** IMPLEMENTED in workflow/source.
- **Push lane:** develop.
- **Hosted warehouse workers:** removed.
- **Concurrency:** dedicated warehouse-stage group.
- **Provider staging/audit:** preserved.
- **Evidence:** STATIC configuration; real staging run pending.

## 2026-09-26 - CI validator/policy synchronization

- **PG-026:** synchronized with serialized production-lane preemption.
- **PG-167:** added for self-hosted static/cleanup lanes and Unreal preparation isolation.
- **Runtime impact:** none.
- **Evidence state:** STATIC-VALIDATED SOURCE CHANGE; runner execution pending.

## 2026-09-26 - CI zero-step bypass

- **REQ-STABILITY-003 / DEC-043:** IMPLEMENTED in workflow/source configuration.
- **GitHub-hosted static/cleanup dependency:** REMOVED.
- **Periodic Pre-Unreal polling:** REMOVED.
- **UE4 queue isolation:** PREPARATION/DOCS/CI-only deltas excluded.
- **Local validation entry point:** ADDED.
- **Evidence:** STATIC-VALIDATED CONFIGURATION ONLY; supervised-runner execution pending.

## 2026-09-26 - Branch hygiene / immediate develop integration

- **REQ-EXEC-002:** IMPLEMENTED.
- **DEC-042:** ACCEPTED.
- **Safe stale refs queued for deletion:** 7 including the finished stability branch after merge.
- **Active runtime lane:** PR #80 only.
- **Active preparation:** PR #81 + whole-game-production-prep-v2.
- **Pending selective salvage:** foliage-wind-v1, localization-prototype-v1, p1c01-mega-prep-v1.
- **Acceptance impact:** none; branch cleanup does not promote gameplay/visual/performance state.


## 2026-09-26 - Source-to-production and local material execution path

- **P1C01SourceExtractionV1:** PREPARED from supplied PDFs.
- **P1C01SourceToProductionBridgeV1:** PREPARED.
- **run_p1c01_material_pipeline.ps1:** IMPLEMENTED as local orchestration for Poly Haven/ambientCG staging -> warehouse audit -> intake -> optional UE4 import.
- **Safety:** local execution does not disable hash/audit/format/import checks.
- **Acceptance:** STATIC/PREPARATION only until a real material intake receipt + UE4 commandlet log is captured.

## 2026-09-26 - High-throughput production / material intake

- **REQ-PROD-011:** PARTIAL.
- **DEC-041:** ACCEPTED.
- **15 source PDFs:** HASHED/INDEXED with authority roles.
- **P1C01 material wave:** 8 concrete Poly Haven CC0 candidates + ambientCG fallback at 2K intake scale.
- **Material tooling:** IMPLEMENTED IN PREPARATION SCRIPTS; missing downloads are PENDING, technical defects remain blocking.
- **Administrative relaxation:** naming/optional metadata/not-yet-downloaded candidates do not stop unrelated prep work.
- **Technical hard stops:** dangerous/corrupt payloads, BMP, invalid final animated format, provider-access bypass, runtime dependency/streaming/memory/pooling/world-state defects remain blocking.
- **Runtime lane:** unchanged; no second runtime-changing PR opened.
- **Acceptance:** STATIC/PREPARATION only; no fresh COMPILE/PIE/DEVICE/VISUAL/PERFORMANCE claim.

## 2026-09-26 - Global runtime-cost architecture preparation

- **WholeGameAssetFamilyCoverageV1:** PREPARED; 9 shared family groups derived from 28 region packets.
- **WholeGameStreamingResidencyPlanV1:** PREPARED_NOT_RUNTIME_STARTED.
- **WholeGamePooledPopulationPlanV1:** PREPARED_NOT_RUNTIME_STARTED.
- **System ownership:** LivingWorldDirector / ShireNPCContextSubsystem / ShireQuestSubsystem boundaries preserved; no parallel brain/world owner introduced.
- **Evidence state:** preparation only; no new COMPILE/PIE/DEVICE/PERFORMANCE acceptance.

## 2026-09-26 - P1C01 D-H + Gate 6/7 preparation

- **D Environment Presentation:** PREPARED_NOT_RUNTIME_STARTED.
- **E Character Presentation:** PREPARED_NOT_RUNTIME_STARTED.
- **F Living Shire:** PREPARED_NOT_RUNTIME_STARTED; existing system ownership retained and bottleneck guards defined.
- **G Quest/Cinematic/Audio Polish:** PREPARED_NOT_RUNTIME_STARTED.
- **H Target Device Profiling:** PREPARED_NOT_RUNTIME_STARTED.
- **Gate 6/7 checklist:** PREPARED_NOT_ACCEPTED.
- **Evidence boundary:** preparation only; no new COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED or PERFORMANCE-ACCEPTED claim.

## 2026-09-26 - Massive whole-game preparation batch

- **28 region packets:** active preparation tracks created without runtime promotion beyond P1C01.
- **9 production waves:** BPB-W1 through BPB-W9 remain active for surfaces, vegetation, characters/animation, architecture/interiors, VFX, audio, music, terrain/scanning and Arabic/UI.
- **P1C01 concrete intake queue:** 28 registered candidates organized for staging/QC; blocked license items remain blocked.
- **Production asset policy:** format/provenance/technical/performance contracts locked before READY_FOR_IMPORT.
- **Runtime status:** unchanged; PR #80 C2 remains the sole runtime-changing lane.
- **Acceptance status:** PREPARATION ONLY. No exact-head engine/PIE/device/visual/performance acceptance added by this batch.

## 2026-09-25 - Region production packets

- **Whole-game packets:** CREATED for every registered region.
- **Sourcing families:** MAPPED to the global resource registry by discipline.
- **Runtime state:** P1C01 active; later regions preparation-only until Gate 6/7.
- **Acceptance:** NONE claimed from packet creation.

## 2026-09-25 - Whole-game world build coverage

- **Coverage map:** CREATED — all registered world locations now carry the full production-layer checklist.
- **Global preparation:** ACTIVE — all regions may receive source/asset/design preparation in parallel.
- **Runtime expansion:** SERIALIZED — P1C01 only until Gate 6/7.
- **Cross-game layers:** REQUIRED — world streaming, save/load continuity, LivingWorld integration, weather/wind, accessibility and Arabic localization remain explicit build tracks.
- **Acceptance:** REGION-SPECIFIC — no later region is accepted from preparation alone.

## 2026-09-25 - Global external-resource production expansion

- **Resource Bible review:** COMPLETE FIRST PASS — 68 pages / 225 classified sources audited as a production sourcing map.
- **Governor:** DEC-039 ACCEPTED — whole-game sourcing authority, subordinate to canon/story rules.
- **Global source registry:** EXPANDED — 102 -> 142 structured providers/tools in first pass.
- **Legacy cleanup:** ACTIVE — Replica Studios disabled; old Marketplace/Texture Haven/CC0 Textures/ArmorLab/Terrain.party paths redirected or disabled.
- **Big production launch:** READY — nine structured source/warehouse waves registered in `BigProductionBuildLaunchV1.json`.
- **Performance contract:** PRESERVED — FBX animated production assets; PNG/TGA textures; 1K/2K default runtime texture target; async/soft heavy assets; pooling; HISM/LOD/culling.
- **Runtime expansion:** NOT CLAIMED — warehouse/source preparation can scale globally, while runtime chapter expansion remains gated and P1C01 remains first assembled benchmark.
- **Acceptance:** NOT CLAIMED — source registration is not download/import/integration/PIE/device/visual/audio acceptance.

## 2026-09-25 - Playable-film interaction doctrine

- **Governor decision:** DEC-038 ACCEPTED.
- **Canon beats/outcomes:** LOCKED by Story/Timeline/Mission sources.
- **Scope:** WHOLE GAME — every chapter and major playable region from beginning to final ending; P1C01 is only the first benchmark.
- **Interactive safe windows:** REQUIRED around major beats when source chronology permits.
- **Cutscene-only chapter design:** NOT ACCEPTABLE when meaningful interaction can exist without changing canon.
- **Open-world divergence:** NOT ACCEPTABLE when it contradicts chronology or locked outcomes.
- **Persistent consequence presentation:** REQUIRED before control returns after major canon transitions.
- **Dialogue:** original project-authored text only; no verbatim Tolkien/film reproduction.
- **Implementation proof:** chapter-specific; no chapter is called visually/pacing accepted until Gate 6/7 evidence exists.

## 2026-09-25 - Private-offline asset isolation lane

- **Owner decision:** RECORDED — DEC-037.
- **Private offline intake:** READY — `PrivateOfflineAssetIntakeQueueV1.json` can accept bulk owner links/files without commercial-clearance uncertainty blocking local experimental classification.
- **Isolation:** ACTIVE — `SourceAssets/PrivateOffline/` payloads are Git-ignored and excluded by policy from distributable Framework output.
- **Framework clearance:** STRICT — private-only/unknown-license/editorial/ripped payloads cannot be promoted into distributable/commercial output without separate clearance.
- **Provider access:** STRICT — no auth/paywall/DRM/anti-bot bypass.
- **Technical acceptance:** UNCHANGED — private/offline classification does not imply import/runtime/PIE/device/visual/audio acceptance.

## 2026-09-25 - Warehouse bulk-intake V2

- **P1C01 environment materials:** EXPANDED FOR STAGING — additional verified CC0 Poly Haven ground/woodland families added at 2K intake scale.
- **Shire support architecture:** EXPANDED FOR STAGING — page-licensed Quaternius Farm Buildings added with FBX requirement; unverified Quaternius pack licenses now fail closed.
- **Reusable support kits:** EXPANDED FOR STAGING — Kenney cave/building support stock added under CC0.
- **P1C01 ambience/foley:** EXPANDED FOR STAGING — CC0 multi-surface footsteps, fireplace, wood/metal interaction bank and bird ambience added to the OpenGameArt batch.
- **Provenance safety:** HARDENED — Quaternius automatic staging requires per-pack license evidence; no blanket-provider assumption.
- **Runtime integration:** UNCHANGED — this lane prepares/stages source assets only. No second runtime-changing PR is opened.
- **Acceptance:** NOT CLAIMED — STAGED does not equal READY_FOR_IMPORT, INTEGRATED, PIE-tested, device-tested, visually accepted or audio accepted.

## 2026-09-25 - PR #77 handoff status normalization

- **Unreal #731:** SUCCESS on `3b2281c17...`.
- **Pre-Unreal #896:** Governor metadata failure only; a descriptive non-schema status was used in the handoff snapshot.
- **Root fix:** use canonical `FAILURE` status plus a separate explanatory note.
- **Runtime conclusion:** Drop C1 engine/core implementation remains green on the corrected runtime head ancestry; fresh Pre-Unreal is still required. No PIE/device/visual promotion.

## 2026-09-25 - PR #77 PG-165 resolver correction

- **Pre-Unreal #895:** FAILED in validator path resolution only; PG-165 searched the runtime module for an EditorTools commandlet.
- **Unreal #730:** SUCCESS on exact head `725ca991...`; Drop C1 compiled and completed the production-import/core validation path.
- **Root fix:** add dedicated EditorTools source resolver and route PG-165 through it, so editor-module guards cannot regress to runtime-module lookup.
- **Current proof boundary:** prior runtime head is COMPILE/ENGINE-CORE PROVEN; corrected validator head still requires fresh Pre-Unreal. No PIE/device/visual acceptance.

## 2026-09-25 - W01 P1C01 Drop C1: material texture binding

- **Shire authored albedo pipeline:** IMPLEMENTED IN SOURCE — MTL `map_Kd` is parsed and bound into deterministic `AlbedoTexture` material-instance parameters.
- **Master material:** IMPLEMENTED IN SOURCE — BaseColor uses `AlbedoTexture * Color`; Roughness/Metallic contract remains intact.
- **Gameplay/runtime ownership:** UNCHANGED — editor import pipeline only.
- **Foliage wind/WPO:** NOT YET IMPLEMENTED; scheduled as C2 after C1 exact-head green.
- **Validation:** STATIC-VALIDATED only until fresh Pre-Unreal + UE4.27.2 production import/core validation succeeds.

## 2026-09-25 - PR #76 handoff-baseline coherence correction

- **Pre-Unreal #890/#891/#892:** FAILED in Governor handoff coherence, not in architecture runtime.
- **Root cause:** `session_handoff.source_head` pointed at the merged Drop A commit while `validation_snapshot.last_green` still pointed at an older baseline.
- **Correction:** handoff source/baseline now consistently use `b9a312ce...` with #888/#723 SUCCESS; latest observed PR #76 evidence is tracked separately.
- **Evidence boundary:** Drop B remains STATIC-VALIDATED until the corrected exact head passes Pre-Unreal and UE4.27.2 core validation.

## 2026-09-25 - W01 P1C01 Drop B: Hobbiton + Bag End architecture

- **Bag End exterior hierarchy:** IMPLEMENTED IN SOURCE — garden/property approach and landmark-supporting dressing added without moving story anchors.
- **Hobbiton domestic architecture:** IMPLEMENTED IN SOURCE — garden/property clusters and village-common composition reinforce warm domestic scale.
- **F1-01 Party Field architecture:** IMPLEMENTED IN SOURCE — canopy/produce dressing added to existing social destination.
- **Canon presentation:** CORRECTED — The Green Dragon is no longer presented as a Hobbiton landmark; legacy internal discovery ID retained for save compatibility.
- **Bag End production interior:** NOT YET IMPLEMENTED — dedicated interior shell/portal kit absent from current asset bank.
- **Performance:** existing resident meshes only; no synchronous heavy-load path; target-device shadow/collision/HLOD measurement pending.
- **Validation:** STATIC-VALIDATED only until exact-head Pre-Unreal + UE4.27.2 core green. No PIE/device/visual acceptance yet.

## 2026-09-25 - PR #75 validation classification correction

- **Exact-head core evidence on 5a58c8d3...:** COMPILE/ENGINE CORE PASSED — editor build, import, Automation, startup, chapter sweep, route/state and warning guard succeeded.
- **Workflow red cause:** validation classifier lacked the PR base object and chose `full` via `delta-unavailable-fail-safe`; package helper then failed on staged DbgHelp ACL probing before cook.
- **Policy applicability:** PR #75 contains C++/Data/docs/validator world-production changes, not Config/Build.cs/Target.cs/streaming/package/cook/release changes. Core validation is the required lane.
- **Correction:** classifier now fetches the explicit PR base SHA and retries `git diff`, preventing shallow-checkout history from escalating normal runtime work to package/cook.
- **Current status:** Drop A has prior exact-head core engine proof, but the corrected classifier head still needs a fresh green workflow before merge. No PIE/device/visual acceptance is inferred.

## 2026-09-25 - W01 P1C01 Drop A: terrain/geography foundation

- **Parent baseline:** `develop@ec320891...` = Pre-Unreal #885 SUCCESS + Unreal #720 SUCCESS.
- **Terrain/geography runtime:** IMPLEMENTED IN SOURCE - repeated terraced hills, village slopes and river banks moved to dedicated HISM groups; route-framing geography expanded across the P1C01 Shire traversal.
- **Performance contract:** IMPLEMENTED IN SOURCE - explicit HISM cull distances for foliage/scenic/geography groups; no new synchronous heavy-load path.
- **Story/quest boundary:** PRESERVED - no quest IDs, chapter postconditions or stable story anchors moved.
- **Grounding boundary:** PRESERVED - broad collision foundation and router grounding contract remain authoritative.
- **Regression guard:** PG-163 checks the HISM geography/cull contract and rejects repeated geography actor spawning.
- **Validation:** STATIC-VALIDATED only until PR #75 exact-head Pre-Unreal + UE4.27.2 core validation succeeds.
- **Next production dependency:** Hobbiton / Bag End architecture.

## 2026-09-25 - PR #74 governance-transition red diagnosis

- **Pre-Unreal #882/#883:** FAILED in Project Governor coherence, not UE4 runtime.
- **Failure family:** partial W00 -> W01 control-plane transition; old PR #73/branch/W00 mode/blocking-gate state remained beside new W01 focus.
- **Runtime impact:** no runtime conclusion can be drawn because validation stopped before engine proof.
- **Correction:** reconcile Governor active gate, development mode, branch workflow, session handoff, integration train and MASTER_EXECUTION_BOARD together in one atomic commit.
- **Evidence state:** W01 Drop 1 remains STATIC-VALIDATED; fresh exact-head Pre-Unreal + UE4.27.2 core validation required.

## 2026-09-25 - W01 validator reconciliation after #881

- **Pre-Unreal #881:** FAILED on stale PG-035/PG-036/PG-111 assumptions tied to builder-owned Shire ambient life and the old saturation-plan status.
- **Runtime conclusion:** no UE4 runtime failure is inferred from #881; the failure occurred in project-structure validation before Governor/deep/engine stages.
- **Validator correction:** guards now validate director-owned role/prop mappings, data-owned P1C01 fauna coverage, explicit single-owner budget authority, and absence of direct Shire builder ambient spawning.
- **Fresh proof:** `03e886a6...` has Pre-Unreal #882 running and Unreal #717 pending. Status remains STATIC-VALIDATED until those finish.

## 2026-09-25 - W01 P1C01 drop 1: living-world ownership/budget convergence

- **Ambient population ownership:** IMPLEMENTED in source — P1C01 builder duplicate `AShireAmbientNPC` spawning removed; `LivingWorldDirector` is the ambient crowd owner and uses the existing pool.
- **Story ownership boundary:** PRESERVED — named/story NPCs, quest triggers and canonical postconditions remain outside ambient crowd ownership.
- **Micro-event budget authority:** IMPLEMENTED — `LivingWorldEventPlan#region_budgets` is sole cap/cadence source; `WorldLifeSaturationPlan` no longer overrides those values.
- **P1C01 playful life role:** PRESERVED through director-owned `PlayRunner` role.
- **Validation state:** STATIC-VALIDATED only; Pre-Unreal/UE4.27 compile/runtime pending. Do not promote to COMPILE-TESTED/PIE-TESTED yet.
- **Next W01 production stage after engine-green:** terrain/geography foundation, then Hobbiton/Bag End architecture, while sensory/reactive notes remain queued inside their ordered stages.

## 2026-09-25 - W00 closure / W01 kickoff

- **W00 repair lane:** CLOSED on `develop@809e56a9e1dc4b453e02a0b04b6875a71df21933`.
- **Machine evidence:** Pre-Unreal #880 SUCCESS; Unreal #715 SUCCESS by safe validation-policy inheritance; prior full machine chain remains Unreal #704 on the safe ancestor.
- **Owner PIE evidence:** P1C01 startup grounding PASS with `commitBarrier=yes stableSeconds=2.0 ground=yes drop=1.8 drift=0.0`; player remained on ground; same-session owner searches returned no `Mobility is Static` or `SetStaticMesh` matches.
- **Evidence boundary:** startup-grounding/warning-tail is PIE-TESTED. Whole P1C01 remains not DEVICE-TESTED, not VISUALLY-ACCEPTED and not PERFORMANCE-ACCEPTED.
- **W01 status:** STARTED AS PRODUCTION GOVERNANCE/LEDGER KICKOFF; runtime code is unchanged in this kickoff change.
- **First implementation gates:** ambient ownership/pooling consolidation -> living-world event-budget authority reconciliation -> terrain/geography and the ordered P1C01 vertical-slice production stack.
- **Sensory/reactive intake:** VERIFIED/PARTIALLY ACCEPTED. Spatial environmental audio/surface foley, performance-scaled vegetation motion and skeletal IK presentation are tracked; duplicate implementations of already-present NPC awareness/weather and audio fade/duck systems are explicitly rejected.

## 2026-09-25 - W00 lessons-lock / current develop proof
- **PG-161 follow-up:** #875 exposed a wrong textual anchor in the self-guard. Loop-anchored correction committed; exact-head rerun pending. No gameplay/acceptance status changed.
- **PG-161 self-test:** #871 found a validator false positive; PG-164 correction committed. Exact-head Pre-Unreal rerun pending; no gameplay acceptance state changed.
- **Current develop machine baseline:** `ed3587aa...` — Pre-Unreal #869 SUCCESS + Unreal #704 SUCCESS.
- **Compile/import/runtime/package:** PROVEN on current canonical develop. #704 passed build/import/Automation/startup/P1C01-P1C08/route-state/warning/package/data/startup/hardware.
- **Human PIE tail:** PENDING on the final canonical develop after lessons-lock merge; do not call full P1C01 PIE-TESTED yet.
- **Validation-cost regression:** ROOT FIX COMMITTED. Safe governance/docs ancestry may inherit nearby green proof; runtime/assets/config/streaming/package changes still force core/full validation. Validation-policy-only changes no longer recook a green parent.
- **Local launcher self-update regression:** FIX COMMITTED; immutable temp-copy execution is guarded by Pre-Unreal, local rerun pending.
- **Branch hygiene:** develop + main only after cleanup; lessons-lock branch is temporary and registered for deletion after merge.
- **W01 status:** NOT STARTED. First production work begins only after final P1C01 PIE warning/grounding tail is clean.

## 2026-09-25 - Post-cleanup handoff state
- **Branch hygiene:** PROVEN CLEAN. Branch Cleanup run #1 succeeded; live GitHub branch enumeration returned only `develop` and `main`.
- **Programmer handoff:** canonical branch = `develop`; stable release = `main`. Historical feature/repair branches are no longer required for handoff.
- **PR/governance metadata:** PR #72 is metadata-only reconciliation so the merged Governor/Execution Board no longer point at completed PR #70. It self-cleans after merge.
- **Consolidated develop:** `3108b2dd6354b196d36406935057c25feab2fec2`; Pre-Unreal #865 SUCCESS. Do not infer a fresh UE compile/runtime result until the corresponding Unreal run is green.
- **W00:** automated machine closure remains green from the prior exact evidence chain; the final human P1C01 grounding/mobility-warning tail remains unproven.

## 2026-09-25 - Final consolidation / CI-cost / launcher hardening
- **Final branch survivor set:** `develop` + `main` only. The generated-audio archive ref is also safe-delete after registry consolidation; no branch-only WAV/UE master asset was found in its changed-file set.
- **Canonical handoff target:** `develop`; stable release lane: `main`.
- **Branch consolidation:** FINAL DELETE SET RECORDED on PR #70. Post-merge cleanup preserves only develop/main; stale refs are removed automatically by the branch-cleanup workflow.
- **Parallel consolidation PR #71:** SUPERSEDED after unique safe payload transfer into #70.
- **Generated-audio registries:** CONSOLIDATED/SANITIZED; expiring signed delivery URLs removed; no UE playback/listening acceptance promoted.
- **Local launcher self-update hazard:** FIX_COMMITTED for both update/build and PIE verification controllers; local rerun proof pending.
- **Unreal validation classifier/workflow:** FIX_COMMITTED. Core runtime changes compile/test without package/cook; packaging-critical deltas retain full package validation; maintenance/docs can inherit green parent proof.
- **W00:** AUTOMATED CLOSURE GREEN; remaining human P1C01 grounding/traversal + project-owned mobility-warning tail is still unproven on the final canonical post-maintenance head.

## 2026-09-25 - Consolidation and validation-cost correction
- Sanitized audio registry salvage: **DATA-CONSOLIDATED / RUNTIME-UNPROVEN**. Canonical develop receives the generated-audio/P1C01 bank metadata without signed external download URLs; WAV mastering, UE import, playback, lip-sync, listening and device acceptance remain pending.
- Repository/branch hygiene: **IMPLEMENTED ON PR #70 / MERGE-PENDING**. Canonical runtime handoff target remains `develop`; stale feature/repair branches are not authoritative.
- Local launcher self-update hazard: **FIX_COMMITTED / PROOF PENDING**. The running batch now uses a temp copy before pulling, preventing mid-execution mutation. No local rerun evidence is claimed yet.
- Unreal classifier cost correction: **FIX_COMMITTED / CI PROOF PENDING**. PR classification uses the canonical base SHA, so ordinary C++/runtime/data/SourceAssets deltas use a core lane (build/import/Automation/runtime/warning) with no package/cook even when intermediate branch runs were cancelled. Packaging remains mandatory for Build.cs/Target.cs/Config/streaming/packaging-critical deltas.
- W00 status remains **AUTOMATED_CLOSURE_GREEN_HUMAN_PIE_TAIL_PENDING**. Pre-Unreal #821 + Unreal #656 are machine evidence only; no new PIE/device/visual acceptance is claimed.
- Branch consolidation salvages planning/recovery/source09 records into develop and consolidates the generated-audio registry evidence directly into the canonical lane; no separate archive branch is required.

## 2026-09-25 - C4996 / SetStaticMesh warning-debt guards added

The remaining visible warning families are now encoded as hard regression guards. Canonical `develop` already uses `GetStaticMaterials()` in the production importer, so the old C4996 source pattern is absent. PG-159 now rejects any return to direct `UStaticMesh::StaticMaterials` access.

For the PIE `SetStaticMesh ... Mobility is Static` warning family, the current Shire/Bree/Fellowship/Isengard `SpawnShape` implementations already set `EComponentMobility::Movable` before assigning the mesh. PG-160 now locks that ordering.

Status: **STATIC-VALIDATED / FRESH COMPILE + PIE WARNING LOG PROOF PENDING**. Do not claim zero warnings until the fresh exact-head UE4.27 build and PIE log confirm it.

## 2026-09-25 - Final workflow repair batch committed to canonical develop

A single canonical interactive lane is now enforced: `develop`.

Root repairs in commit `09f89ab472832b8f03b56cf09eddb4ec7e268af9`:
- `SHIRE_UPDATE_BUILD_LAUNCH.bat` updates/builds/imports only the already-selected `develop` branch and never performs a silent branch switch.
- `SHIRE_PIE_VERIFY.bat` verifies only `develop` and refuses the GitHub Actions runner workspace.
- interactive Unreal use under `C:\actions-runner\_work` is blocked; the Documents developer clone and runner workspace remain physically isolated.
- `Scripts/verify_runtime_source_workspace.ps1` validates every tracked Source .h/.cpp/.cs immediately before UBT and restores a tracked file from exact HEAD if a persistent runner workspace is missing it.
- Unreal workflow now executes that source-integrity gate immediately before `Build ShireJourneyEditor`.
- the Unreal classifier recognizes governance-only green parents as transitive core proof, preventing evidence-only commits from needlessly returning to a full engine pass.

This batch responds to two observed regressions: the local launch helper previously returned the owner from the grounding-proven acceptance branch to stale `develop`, and Unreal #653 later reported a missing `ShireAmbientNPC.cpp` from the persistent runner workspace even though that file exists in Git.

Evidence status: **STATIC-VALIDATED / FRESH PRE-UNREAL + UE4 BUILD/PIE PROOF PENDING**. Existing #651 automated acceptance and the earlier real P1C01 grounding observation remain historical evidence; this new workflow batch itself is not yet COMPILE-TESTED or PIE-TESTED.

## 2026-09-25 - Real PIE closes P1C01 startup-grounding regression

Exact tested head: `2427e6594f5adb3ea81f143dc19d4ecede8eecc9`.

Owner real-PIE observation: the P1C01 player remained on the ground and did not fall.

Chapter-specific Output Log evidence from the owner-provided screenshot:
- `ShireStartupGrounding: PLACED chapter=P1C01 source=chapter-start requestedZ=130.0 groundedZ=76.0`
- `ShireStartupGrounding: PASS chapter=P1C01 commitBarrier=yes stableSeconds=2.0 ground=yes drop=1.0 drift=0.0`

This closes the specific player-fall/startup-grounding repair. It does **not** promote the whole P1C01 chapter to PIE-TESTED and does not claim DEVICE-TESTED, VISUALLY-ACCEPTED or PERFORMANCE-ACCEPTED. Chapter-wide traversal/quest/save-load/pacing/visual review remains a separate human acceptance tail.

Next action: final W00 branch ancestry/cleanup audit, then close the repair lane and open W01 under Gate 6/7.

## 2026-09-25 - Automated W00 acceptance chain green on Unreal #651 Attempt 2

Exact head `efdb2e291505472247fae921945b083b3cc1ce2c` is now machine-proven through the complete automated W00 chain: Pre-Unreal #816 SUCCESS, Warehouse #232 SUCCESS with no-delta self-hosted skip, and Unreal #651 Attempt 2 SUCCESS.

Accepted automated evidence on this head:
- UE4.27.2 Editor build and production import.
- Automation QA, headless startup, P1C01-P1C08 runtime audit, route/story roundtrip and warning-debt guard.
- Windows package: `W00_PACKAGE_PASS elapsedSeconds=182`.
- Runtime JSON: `W00_PACKAGED_DATA_PASS expected=37 verified=37`.
- Packaged startup: `W00_PACKAGED_STARTUP_PASS observed=6s`.
- Runner hardware snapshot: PASS on i7-6498DU with 8.45 GB reported RAM.
- Packaged startup also required `ShireStartupGrounding: PASS chapter=P1C01`.

This closes the runner/package/data/startup proof debt for the current contract. It does **not** promote PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED or PERFORMANCE-ACCEPTED. Human PIE grounding/traversal remains the next acceptance boundary.

## 2026-09-25 - Self-hosted runner pre-step failure isolated; warehouse contention removed; watchdog root mitigation added

Live GitHub evidence on exact head `a69147e4e34869bc43abfbce517ba8023b6027c8` isolates the new failure boundary outside repository steps. Unreal #650 was assigned to runner `UE4-27-Windows` (runner id 21) at 21:22:36Z, recorded **zero steps**, and failed at 21:32:37Z. Warehouse #231 was then assigned to the same runner at 21:32:39Z, also recorded **zero steps**, and failed at 21:42:39Z. Pre-Unreal #815, which runs on GitHub-hosted Ubuntu, succeeded on the same head. The a69147 commit did not modify the Unreal workflow.

The repository-side repair removes avoidable pressure on that machine: Warehouse now computes the synchronize delta on `ubuntu-latest` first and never schedules its self-hosted stage job unless the current update contains a real Warehouse staging input. Workflow-control-only changes stay on the hosted skip path. When real Warehouse staging is required, it shares the UE4 device concurrency group instead of competing independently.

A machine-side supervisor is now versioned as `Scripts/runner_watchdog.ps1` with installer `Scripts/install_runner_watchdog.ps1`. It watches the runner diagnostic stream for an acknowledged job that fails to produce a `Runner.Worker` within 150 seconds, then restarts only the stalled `Runner.Listener`; it also restarts a missing listener. The installer deliberately uses the interactive Windows user and disables legacy auto-start of any `actions.runner.*` service so the project does not silently fall back to the earlier NETWORK SERVICE identity.

Evidence status: **STATIC-VALIDATED / LOCAL WATCHDOG INSTALL + RUNNER PROOF PENDING**. This does not claim Package/Packaged Startup/PIE/device/visual success on the new head. After the local watchdog is installed, the next machine action is one acceptance run, not a broad rerun wave.

## 2026-09-25 - Packaged production streaming cook root fix after Unreal #649

Unreal #649 isolated the real packaged-runtime blocker. Package creation and all 37 Runtime Data JSON files passed, and the packaged executable launched. P1C01 then failed closed with `ChapterAssetStreaming: unresolved-bank-assets ... missing=82`.

The count proves the cook omission: P1C01 declares 83 streaming assets, while the prior packaging configuration always cooked only `/Game/Production/Materials`; exactly one P1C01 asset is in that directory. Therefore `83 - 1 = 82`, exactly matching runtime. The full streaming plan contains 238 unique production packages, and all 238 have matching project-owned import sources. Unreal #649 production import reported 376 files and 0 failures.

The repair always cooks the exact current streaming-bank directory set: Materials, World, Characters/Common, Characters/Hobbit, and Enemies. Static coverage before commit is 238/238 with zero uncovered streaming paths. The package wrapper now parses the streaming plan before UAT and requires all 238 generated `.uasset` files to exist, so missing imported content fails in seconds rather than after cook/startup. The classifier treats only this exact four-line packaging-config change as acceptance-safe and recognizes transitive acceptance proof so chained verifier/package fixes do not unnecessarily return to the full Unreal chain.

Status: **STATIC-VALIDATED / RUNNER_PROOF_PENDING**. No packaged-startup success is claimed on this repair head yet.

## 2026-09-24 - Unreal #648: Package + 37 Runtime Data proven; resume at packaged startup

Unreal #648 on exact head `9689a65ade82af5e1a87b63e344ed491c27c4079` produced the first valid packaged-acceptance proof:

- `W00_PACKAGE_EXITCODE source=cmd-sidecar exit=0`
- `W00_PACKAGE_PASS elapsedSeconds=300`
- `W00_PACKAGED_DATA_PASS expected=37 verified=37`

These gates are now green evidence and must **not** be repeated for a packaged-startup-verifier-only fix.

The next step failed before producing a game/runtime verdict. `verify_packaged_startup.ps1` read an existing but still-empty log with `Get-Content -Raw`; PowerShell returned `$null`, and line 58 called `$text.Contains($marker)`, raising `InvokeMethodOnNull`.

Repair:
- startup log polling initializes `$text` to `""` and only replaces it when the raw read is non-null;
- Pre-Unreal now rejects regressions of this empty-log case;
- the acceptance classifier can inherit parent Package + Runtime Data proof for startup-verifier-only deltas;
- that resume path skips UE verification, editor wait, package and Data gates;
- before launching the packaged executable, CI proves the persisted `ShireJourney.exe` and the successful 37-file packaged-data report are still present locally.

Next intended execution:
`Inherited package/data artifact check -> Packaged Startup -> Hardware Snapshot`.

Status: **PACKAGE PASS / 37 JSON PASS / PACKAGED STARTUP PROOF PENDING**. No PIE, visual, device, or player-falling closure is claimed.

## 2026-09-24 - Fast-path rule and package exit truth after Unreal #647

Unreal #647 on exact head `6fb1c5edd81989de853fface5e406d8cddab0099` provides fresh successful Core Unreal proof through the warning-debt guard. Those successful gates are **not to be repeated** for a package-wrapper-only fix.

The package step itself was still making forward progress after about 25 minutes: the last evidence was `Cooked packages 251 Packages Remain 12 Total 263` with shader compilation still active. No terminal UAT result was logged before `ci_package_w00.ps1` emitted `W00_PACKAGE_EXITCODE_FAIL exitCode=<null>` and exited 97. This is a wrapper-result failure, not proof of a UAT/package failure.

Repair:
- RunUAT is called synchronously by a dedicated `cmd.exe` wrapper.
- The wrapper writes the actual post-CALL `%ERRORLEVEL%` to `CI-W00-Package-exitcode.txt`.
- PowerShell keeps heartbeat and bounded timeout only; it no longer trusts `$proc.ExitCode` for UAT truth.
- Missing/invalid sidecar results fail immediately with explicit diagnostic codes.
- PG-026 rejects reintroduction of `$proc.ExitCode` as RunUAT result authority.

Execution rule: the child commit is acceptance-only and must inherit #647's green Core Unreal proof. The intended next sequence is only:
`Verify UE -> Package -> 37 Runtime JSON -> Packaged Startup -> Hardware`.
If classification unexpectedly becomes `full`, stop rather than spend another full Core Unreal cycle.

Status: **STATIC-VALIDATED / RUNNER_PROOF_PENDING**. No Package PASS or downstream packaged acceptance is claimed yet.

## 2026-09-24 - Grounding guard reconciliation after real PIE fall regression

The new two-phase grounding commit barrier exposed two stale/strict validation assumptions. PG-122 correctly required the established delayed stability proof, while the runtime barrier had been shortened to 0.35 seconds. The runtime now waits a real **2.0 seconds** before grounding finalization and logs `stableSeconds=2.0`.

PG-128 was stale relative to the new architecture: normal world publication moved out of `CommitChapterWorld` and into `VerifyPlayerGroundingStability`. The runtime already publishes `OnWorldCommitted.Broadcast(WorldRevision)` before `SetPlayerWorldHold(false)`. The validator now inspects that finalization function directly and also rejects any movement release from the pre-finalization commit setup.

Status: **STATIC-VALIDATED / RUNNER + PIE PROOF PENDING**. The player-falling issue remains open until fresh UE4.27 compile/runtime evidence and real PIE observation confirm stable grounding.

## 2026-09-24 - Player falling / grounding commit barrier root fix

Real PIE evidence showed the player can still fall despite the earlier grounding logic. Root review found that `ChapterWorldRouter` resolved a grounded placement, but published the world as committed and released movement before proving CharacterMovement had actually settled on blocking ground. The previous stability check was CI-only and log-only.

Root fix applied:
- world commit is now two-phase,
- player remains transition-held while CharacterMovement settles,
- grounding stability is checked before `WorldRevision` / `OnWorldCommitted` publication,
- one bounded re-ground attempt is allowed,
- persistent instability keeps the player held and triggers rollback instead of releasing the pawn into a fall,
- successful stability is now the condition that publishes the world and releases movement.

Changed files:
- `Source/ShireJourney/Private/World/ChapterWorldRouter.cpp`
- `Source/ShireJourney/Public/World/ChapterWorldRouter.h`

Status: STATIC-VALIDATED / COMPILE-AND-PIE-PROOF-PENDING. Do not claim the falling issue is closed until a fresh UE4.27 compile and real PIE observation show stable grounding without falling.

## 2026-09-24 - W00 package truth, DbgHelp policy, and PG-026 repair

Live PR #69 head `d94b7fe7797e9ef417b7dad2abde26dfc279e700` produced three decisive signals:

- Pre-Unreal #808 failed only at PG-026 because the validator still required literal `cancel-in-progress: false`.
- Unreal #643 completed Editor build, production import, Automation QA, headless startup, P1C01-P1C08 runtime audit, route/story roundtrip, and warning-debt guard successfully.
- The same Unreal #643 did **not** package successfully despite the GitHub package step being marked success: UAT reached NonUFS staging, repeatedly failed writing the destination `WindowsNoEditor/Engine/Binaries/ThirdParty/DbgHelp/dbghelp.dll` with Access denied, then logged `ExitCode=1` / `BUILD FAILED`. The runner context is NetworkService. The following 37/37 `MISSING_RUNTIME_DATA` result is therefore downstream of incomplete staging and is not accepted as a final Runtime Data verdict.

This repair applies four bounded changes before another acceptance run:

- CI Game TargetRules disable UE's bundled DbgHelp only when `SHIRE_CI_NO_DEBUGINFO=1`; normal local game builds keep the default policy.
- `ci_package_w00.ps1` proves the DbgHelp source is readable and the exact nested destination is writable before UAT, then calls `WaitForExit` / `Refresh`, rejects a null exit code, and propagates the concrete UAT code.
- PG-026 accepts cancellation only when the workflow uses the exact `acceptance/*` head-ref expression; unconditional or broader cancellation remains invalid.
- The Unreal classifier treats the Game `Target.cs` as acceptance-only **only** when its entire diff is the CI DbgHelp guard. Any other Target.cs change remains `full`.

Status: **STATIC-VALIDATED / RUNNER_PROOF_PENDING**. No PIE, device, visual, performance, packaged-startup, or Runtime-Data acceptance is claimed by this code change.

## 2026-09-24 - Acceptance Fast-Path and superseded-run cancellation

Implemented a three-mode Unreal validation classifier:

- `full`: C++ / Build.cs / Config / runtime-contract changes run the complete UE4 validation chain.
- `acceptance`: packaging/verifier/acceptance-only changes inherit proven parent **core Unreal** steps and run only package -> packaged Data JSON -> packaged startup -> hardware gates.
- `inherit`: docs/governance-only changes inherit a green parent workflow.

Parent core proof is accepted only when the prior run has successful Editor build, production import, Automation QA, startup, P1C01-P1C08 audit, route/story roundtrip and warning-debt guard. A run that later fails only at an acceptance gate may therefore still provide valid core-engine evidence for the next acceptance-only fix.

On `acceptance/*` branches, newer commits now cancel superseded runs in the shared UE4-device concurrency group. Normal/full validation branches remain serialized. This prevents obsolete acceptance heads from consuming another 20-25 minute engine pass.

Status: **IMPLEMENTED / RUNNER_PROOF_PENDING**. No acceptance result is claimed until a fresh run demonstrates the fast path and final package/data/startup/hardware gates.

## 2026-09-24 - PG-147 validator reconciled with explicit NonUFS runtime staging

After the runtime Data staging fix, Pre-Unreal #800 failed because PG-147 still matched only the legacy one-argument `RuntimeDependencies.Add("$(ProjectDir)/Data/...json")` spelling. That validator behavior was stale and incorrectly rejected the new explicit `StagedFileType.NonUFS` contract.

Fix applied: `source_contracts.py` now exposes `has_nonufs_runtime_dependency`, PG-147 requires the explicit NonUFS form, and regression tests cover correct NonUFS, legacy untyped rejection, and wrong UFS-type rejection.

Interpretation: this failure was a validation-contract mismatch, not a new runtime/game defect. The next exact-head run must prove both static validation and packaged runtime Data staging.

Status: STATIC_VALIDATOR_FIX_APPLIED / RUNNER_PROOF_PENDING.

## 2026-09-24 - Known failure: packaged runtime Data JSON missing after successful package

Unreal packaging progressed past the previous dbghelp.dll blocker. The package gate succeeded far enough for the next acceptance step to run, then `Verify packaged Runtime Data JSON` failed with `MISSING_RUNTIME_DATA` for the 37 JSON files declared in `ShireJourney.Build.cs`.

Repository inspection confirmed the runtime contract: systems including `LivingWorldDirector` and `ShireNPCContextSubsystem` read JSON via `FPaths::ProjectDir()/Data/...`. Therefore the acceptance package must preserve these files as loose project-relative data under `ShireJourney/Data`, not merely hide them inside a pak or move them to `Content/Data`.

Fix applied: all 37 `RuntimeDependencies.Add("$(ProjectDir)/Data/...")` entries in `ShireJourney.Build.cs` now explicitly use `StagedFileType.NonUFS`, so UE4 staging is instructed to copy them as loose NonUFS runtime files compatible with the existing loader paths.

Status: FIX_APPLIED / RUNNER_PROOF_PENDING. No packaged-data acceptance is claimed until a fresh runner execution proves all 37 files exist, parse as JSON, and the packaged executable reaches runtime startup successfully.

## 2026-09-24 - Known failure: UE4 packaging dbghelp.dll ACL loop

Repeated W00 packaging failures were traced to `Engine/Binaries/ThirdParty/DbgHelp/dbghelp.dll` staging under the self-hosted Windows service account. The game build, cook and UnrealPak were not the demonstrated failure point; prior run #627 completed cook/pak and then failed copying dbghelp.dll. Run #630 moved the failure to a fast preflight and reproduced the same permission denial within seconds.

The earlier mitigation (unique staging + explicit dbghelp copy preflight) was diagnostic, not a permanent fix. The packaging policy is now changed to add UE4 BuildCookRun `-nodebuginfo`, so debug-file staging is intentionally omitted for this acceptance package. The preflight now checks only generic staging-directory writability. This incident must not be rediscovered/reworked as a new defect unless a later log proves a different failure mode.

Status: FIX_APPLIED / RUNNER_PROOF_PENDING. No packaged-build acceptance is claimed until the new exact head passes package -> staged Data JSON -> packaged startup -> hardware gates.

## 2026-09-24 - W00 packaging delay root cause and bounded retry fix

Unreal #627 proved that compile/import/Automation/startup/chapter/state/warning gates remained green. The final package step ran for about 37 minutes and failed **after cook/pak succeeded**: UnrealPak added 1665 files and exited 0, then AutomationTool repeatedly failed to copy `Engine/Binaries/ThirdParty/DbgHelp/dbghelp.dll` into the staged build with Windows `Access denied`.

This is a staging/ACL file-copy blocker, not a demonstrated gameplay/source compile regression.

Added `Scripts/ci_package_w00.ps1` and routed `ci_package_w00.cmd` through it. New behavior:
- unique staging directory per workflow run/attempt,
- explicit DbgHelp copy preflight before any expensive cook,
- 30-second progress heartbeat,
- bounded internal package timeout,
- reuse of Unreal/DDC/cook cache where available,
- no broad repair-wave reopen.

Governor integration baseline was restored to `develop`; the acceptance branch is tracked separately.

Status remains **ACCEPTANCE_FIX_IN_PROGRESS** until the next runner execution proves the package/data/startup gates. No PACKAGE-TESTED/DEVICE-TESTED/PIE-TESTED claim is made yet.

## 2026-09-24 - W00 final closure wave started on isolated acceptance branch

Architectural/root repair remains closed on exact green head `31b6e1c9958b6121ec7a00c07e038fec4ab36408` (Pre #791 SUCCESS, Unreal #626 attempt 2 SUCCESS, Warehouse #207 SUCCESS).

A dedicated branch `acceptance/w00-final-closure-v1` now carries the final automatable W00 acceptance wave. Added `Data/W00FinalClosurePlanV1.json` plus runner scripts for: real Windows BuildCookRun packaging, verification of every `RuntimeDependencies` JSON staged into the package, packaged executable startup/grounding observation, and CPU/RAM/GPU/OS runner snapshot. The Unreal validation workflow now executes these gates after the existing compile/import/Automation/startup/chapter/state/warning suite.

This wave does not claim PIE/device/visual/audio acceptance. Human-only traversal/collision, visual composition, pacing/fun, NPC believability and final listening/mix remain separate evidence. Scripted/ambient voice source generation also remains distinct from UE audio acceptance.

W01 opening rule: if the new automated closure gates are green, the Governor may open the deferred W01-W06 large Part I production program. Broad architectural repair may reopen only for a concrete regression.

## 2026-09-24 - W00 CP-W00-156 bounded exact-checkout validator repair

CP155 `3534e632...` passed Unreal #625 and Warehouse #206. Pre #790 failed only PG-026 because its static contract recognized `--depth=1` but not the new bounded `--depth=2` checkout used for direct-parent classification. CP156 accepts depth 1 or 2 while preserving hard reset + exact SHA verification.

No production-completeness percentage changes. No gameplay/runtime change and no new acceptance claim.

## 2026-09-24 - W00 CP-W00-155 final consolidated repair closure

`f524a83c...` passed **Unreal #624** and **Warehouse #205**; Pre #789 failed only PG-078 stale roadmap tracking after REQ-ORG-001 became VALIDATED. CP155 reconciles that snapshot, adds dedicated resident-bank runtime evidence, and adds a fail-safe governance/docs-only Unreal fast path.

No production-completeness percentage changes. Remaining W00 closure evidence is packaged Data JSON runtime proof, authored audio playback, target-device profiling and chapter-specific human PIE/pacing/visual review.

## 2026-09-24 - W00 CP-W00-154 exact-head machine-green reconciliation

Exact head `ab7889d6...` passed **Pre #788 + Unreal #623 + Warehouse #204**. The Public/Private migration is machine-accepted: static validation, UE4.27.2 compile/import and the exercised headless runtime suite are green on the same SHA.

No production-completeness percentage changes. This does **not** promote PIE, device, visual, performance, packaged-runtime or real-audio acceptance. Remaining W00 closure evidence is packaged Data JSON runtime proof, authored audio playback, target-device profiling and chapter-specific human PIE/pacing/visual review.

## 2026-09-24 - W00 CP-W00-153 migration integration repair

CP152 `9acc72b1...` preserved the intended Public/Private Git tree, but Pre #786 failed on historical flat validator reads and Unreal #621 failed in UHT because the persistent runner retained old untracked flat headers. Warehouse #202 succeeded.

CP153 makes validators/tests layout-aware and adds bounded cleanup of only architecture-mapped obsolete source paths on the self-hosted runner. No gameplay source behavior and no production-completeness percentage change. Exact-head proof is pending.

## 2026-09-24 - W00 CP-W00-152 Public/Private source migration

Exact CP151 head `92f6d3aa...` passed Pre #785, Unreal #620 and Warehouse #201. CP152 performs only the pre-recorded physical runtime-module migration: 62 .h/.cpp files move to `Public/<Domain>` and `Private/<Domain>`; Build.cs stops exporting the module root; validators become layout-aware and PG-154 forbids flat regression.

No gameplay behavior or production-completeness percentage changes. CP152 is **SOURCE-LAYOUT-MIGRATED / EXACT-HEAD VALIDATION PENDING**.

## 2026-09-24 - W00 CP-W00-151 handoff-lineage correction

Exact CP150 head `2259242a...`: Unreal #619 SUCCESS + Warehouse #200 SUCCESS; Pre #784 passed core validation and then failed only because `session_handoff.source_head` no longer matched the recorded last-green baseline. CP151 restores the intended evidence lineage without weakening the validator.

No production-completeness percentage changes. CP151 remains **SOURCE/DATA-REPAIRED / EXACT-HEAD VALIDATION PENDING**.

## 2026-09-24 - W00 CP-W00-150 refactor-regression closure

Exact CP149 head `e0b66dbc...`: Unreal #618 SUCCESS + Warehouse #199 SUCCESS; Pre #783 crashed at PG-056 with `NameError: governor_mode_id` before the remaining static chain. CP150 removes that orphan alias and preserves the single data-owned development-mode contract.

No production-completeness percentage changes. CP150 is **SOURCE-REPAIRED / EXACT-HEAD VALIDATION PENDING**.

## 2026-09-23 - W00 CP-W00-149 data-owned development-mode contract

Parent `32af3140...`: Unreal #617 SUCCESS + Warehouse #198 SUCCESS; Pre #782 FAILURE only at the stale PG-033 development-mode/prose validator before the remaining static suite executed. CP-W00-149 replaces the hard-coded validator allowlist and wording heuristic with one structured Governor-owned contract shared by Pre-Unreal and project_governor.py, plus regression tests.

No production-completeness percentage is increased. Child head remains **SOURCE-REPAIRED / EXACT-HEAD VALIDATION PENDING**.

## 2026-09-23 - W00 CP-W00-148 governor execution-truth hardening

Exact parent `96398e7cc48277324113c7879a8d28e3b659757e` passed Pre-Unreal #781, Warehouse #197 and Unreal #616. This promotes that **parent only** to STATIC-VALIDATED + COMPILE-TESTED + HEADLESS-RUNTIME-VALIDATED for the exercised machine suite; it does not promote PIE, device, audio playback, pacing or visual acceptance.

The follow-up audit found stale management surfaces contradicting the active W00 freeze. CP-W00-148 centralizes executable-vs-frozen bundles in ProjectGovernor, reconciles branch/PR metadata and makes the Governor print current execution directives before backlog memory. No production percentage is increased. The governance child is **SOURCE-REPAIRED / EXACT-HEAD VALIDATION PENDING**.

## 2026-09-23 - W00 CP-W00-147 preflight-vs-rollback semantics

Pre #780 was a qualifier false positive in PG-136: nested `TargetExisting->CurrentChapterId` sanitation was mistaken for authoritative quest identity mutation. Unreal #614 separately showed the P1C99 request is now rejected before transaction publication; the old audit incorrectly demanded a rollback revision bump for a transaction that never began. CP-W00-147 makes source-order guards qualifier-aware and splits fault evidence into preflight rejection with revision unchanged versus real async streaming rollback with revision advanced. No production-completeness percentage is increased. Status: **SOURCE-REPAIRED / EXACT-HEAD VALIDATION PENDING**.

## 2026-09-23 - W00 CP-W00-146 structural validator repair

Head `333cbd0d...` produced Pre-Unreal #779 FAILURE on PG-136, but the production StartChapter source already publishes transition intent before authoritative identity mutation. Root cause: the guard hard-coded the old RHS spelling `CurrentChapterId = ChapterId;` and failed after canonicalization changed the assignment to `TargetChapterId`. CP-W00-146 replaces exact-spelling checks with reusable structural member-mutation ordering plus regression tests. No production percentage is increased. Status: **SOURCE-REPAIRED / EXACT-HEAD VALIDATION PENDING**.

## 2026-09-23 - W00 CP-W00-145 large closure wave

Parent `3ea40ce1...`: Pre-Unreal #778 SUCCESS and Unreal #613 SUCCESS; Warehouse #193 FAILURE before staging due Windows PowerShell execution policy, with separate #192 network/DNS checkout failure. CP-W00-145 repairs both warehouse infrastructure families and simultaneously closes source-level identity/persistence gaps: canonical Route/Chapter/Episode/PlayableCharacter validation, malformed-save/route-progress repair, real queued AsyncSaveGame cross-revision race evidence, and packaged-runtime JSON declaration guards. No production percentage is increased. New-head status: **SOURCE-REPAIRED / EXACT-HEAD VALIDATION PENDING**. W01 remains blocked.

## 2026-09-23 - W00 CP-W00-144 warehouse resilience

Parent `67ebc4ee...`: Pre-Unreal #777 SUCCESS, Unreal #612 SUCCESS, Warehouse #191 FAILURE at the still-in-progress Poly Haven step after 32m57s; no finalized job log blob exists. This is classified as warehouse acquisition/infrastructure debt, not a gameplay regression. CP-W00-144 adds current-update gating, persistent receipt reuse, bounded/retried provider I/O and atomic partial downloads. No production-completeness percentage is increased. New-head status: **SOURCE-REPAIRED / EXACT-HEAD VALIDATION PENDING**.

## 2026-09-23 - W00 CP-W00-143 semantic validation-contract wave

Parent `aa8f80c8...`: Unreal #611 SUCCESS, Warehouse #190 SUCCESS, Pre-Unreal #776 FAILURE on six legacy marker-location checks. No production-completeness percentage is increased. CP-W00-143 makes semantic evidence IDs the validation API and removes exact marker ownership from legacy Python consumers. New-head status: **SOURCE-REPAIRED / EXACT-HEAD VALIDATION PENDING**. W01 remains blocked.

## 2026-09-23 - W00 CP-W00-142 validation-contract consolidation

Parent `7636c777...`: Unreal #610 SUCCESS and Warehouse #189 SUCCESS; Pre-Unreal #775 FAILURE on one stale duplicated PG-140 marker template. No production percentage is increased. The repair is systemic: one runtime-audit registry now owns markers/modes/log names/source anchors, consumers import it, and regression tests forbid duplicated transaction marker text. New-head status: **SOURCE-REPAIRED / EXACT-HEAD VALIDATION PENDING**. W01 remains blocked.

## 2026-09-23 - W00 CP-W00-141 validation-repair checkpoint

Candidate `621ad861...` failed Pre-Unreal #774 at ProjectGovernor evidence validation and Unreal #609 at the first C++ compile error (conditional `UE_LOG` verbosity). No production-completeness percentage is increased. The repair restores exact last-green/latest-observed handoff records, replaces dynamic log verbosity with static branches, and adds PG-141 plus a handoff regression test. Status: **SOURCE-REPAIRED / EXACT-HEAD VALIDATION PENDING**. Last proven engine baseline remains `80fc54dc...` (#773/#608). W01 remains blocked.

## 2026-09-23 - W00 CP-W00-140 closure wave

Parent evidence boundary: `80fc54dc4e4571e57206bef28cc809e2dcb3ec62` is exact-head green on Pre-Unreal #773 / Warehouse #187 / Unreal #608, including compile/import, P1C01-P1C08, state, transitions, rollback/stream-failure faults, delayed pending authority and project warning-debt gates. No PIE/device/visual/performance/audio-playback promotion is made.

New closure work is intentionally not counted as production-percentage progress. It fixes texture-pool scalability authority, broadens warning-debt runtime evidence, and adds PG-140 legacy-terminal/stale-checkpoint runtime regression coverage. Status for the new head is **SOURCE-REPAIRED / EXACT-HEAD VALIDATION PENDING**. W01 stays blocked.

## 2026-09-23 - W00 failure-path expansion after Unreal #606

#606 compiled/imported and passed all established runtime paths through continuous transitions, then the new rollback audit produced a false-negative on time-varying stamina/resolve despite engine logs proving the exact rollback state was applied. The audit now captures exact restore values at the rollback application boundary and checks stable post-release values separately.

The source wave also extends the transaction contract to save-driven world restores, removes compatibility-success behavior for missing/failed chapter banks, adds explicit streaming failure rollback, and adds a deterministic delayed-ready audit for old-world authority during pending async transitions. These are stabilization changes only; no completion percentage advances until a fresh exact head passes PG-137/PG-138.

## 2026-09-23 - PG-136 static-harness correction

Pre-Unreal #771 rejected test-only literal chapter/quest identifiers and an over-broad snapshot/hold ordering check. The fault injection now creates the unsupported chapter dynamically while keeping authored quest identity, and the guard distinguishes the normal transition hold from the no-subsystem fail-safe hold. No production maturity is advanced.

## 2026-09-23 - W00 #605 green baseline followed by rollback-freshness hardening

Exact head `ddd0957d6201c8bf553825acd671c98a9be545ef` passed Pre-Unreal #770, Warehouse #184 and the full Unreal #605 chain: UE4.27.2 compile, production import, Automation, startup, P1C01-P1C08 aggregate runtime, persistence/state, continuous transitions and zero project warning debt. This is the current green technical baseline, not PIE/device/visual/performance acceptance.

A subsequent source audit found that rollback snapshots were commit-time snapshots rather than guaranteed request-time snapshots, and unsupported destinations could return without atomic rollback. PG-136 adds a pre-mutation transition-request boundary, fresh origin snapshot capture, strict route/chapter pairing, rollback for unsupported requests and a real headless failure-injection audit. These changes are stabilization only; no CompletionWave or percentage advancement is granted until a newer exact head passes.

## 2026-09-23 - W00 PG-135 queued checkpoint origin preservation

Source simulation found that the existing async checkpoint callback guard protected completion side effects but an ID-only queued checkpoint could still be reconstructed from a later world after the first save completed. The queue now retains the actual save snapshot plus chapter/route/episode/world revision and serializes that captured snapshot directly. UPROPERTY ownership protects both in-flight and queued snapshot objects from GC. PG-135 prevents ID-only reconstruction from returning.

Pre-Unreal #769 is static evidence for its parent head only; the PG-135 wave requires a newer exact-head validation. No completion percentage changes.

## 2026-09-23 - W00 broad tangent-basis source normalization and strict asset CI

Pre-Unreal #768 exposed 23 additional static OBJ assets with degenerate UV triangles and 7 with opposed normals. The whole exposed set is normalized in one source wave to triangulated face-local UV/normal bases. The Pre-Unreal asset-quality step is also changed from advisory execution to `--strict`, and PG-134/deep audit guard that fail-closed behavior.

This is stabilization only. No CompletionWave or percentage credit is added until a fresh exact head passes strict source validation and the full UE4.27 zero-warning runtime chain.

## 2026-09-23 - PG-134 validator diagnostics synchronization

Pre-Unreal #767 failed because its PG-134 literal self-check did not match the wording already present in `asset_quality_audit.py`. The check now targets the real structural-error phrase and the early validator gate prints exact accumulated errors before exiting. No gameplay/content completion credit is added.

## 2026-09-23 - W00 PG-134 tangent-space source repair after Unreal #601

Unreal #601 on `34a9a2a8b2cf8f944ce4eae7e90fc7492809b9ab` passed C++ build, production import, Automation, startup, P1C01-P1C08 aggregate runtime, state and continuous transitions. The final zero-warning gate isolated the remaining import debt to exactly three meshes: `SM_Balrog_Wing`, `SM_Lurtz_Blade`, and `SM_Isengard_IndustrialPitRim`.

The first two contained degenerate UV triangles; the rim contained authored normals opposing its geometric faces. Their project-owned procedural OBJ source data is repaired with face-local UV/normal bases, and `asset_quality_audit.py` now rejects these tangent-space source defects before engine import. PG-037 is also synchronized with the stronger async-checkpoint completion marker introduced by PG-133. No production-completeness percentage is advanced until a newer exact head reaches zero warning debt.

## 2026-09-23 - W00 PG-133 request-time transaction closure

Unreal #599 on `cb8c789aff25d2d1f53c0bc7e37f47fe92607eeb` failed at UE4.27.2 C++ compile because the named-NPC runtime called a private NPCContext committed-state query. The following source wave promotes that read-only query to the public API and hardens the transaction boundary further: request-time world hold, exact cancel-release, commit-bound NPC-memory pruning, origin-bound async checkpoint side effects, context-dependent NPC/enemy freeze during pending swaps, and a single ambient social actor scan.

These changes do not advance CompletionWave progress. Fresh exact-head compile/import/startup/P1C01-P1C08/state/transitions/zero-warning evidence is required before technical W00 closure, followed by the separately evidence-bound packaged/device/audio/human gates.

## 2026-09-23 - W00 restore-repair publication ordering

Source audit identified a save migration/repair ordering risk: the legacy repair callback ran after restore broadcasts had already exposed the un-repaired identity. The persistence transaction now keeps broadcasts suppressed through legacy canonicalization and publishes only the final repaired state. Player-life restoration also precedes final publication so synchronous same-bank world commit cannot capture stale life values in rollback state.

PG-132 guards the ordering. No CompletionWave or percentage advancement is granted until fresh exact-head engine evidence passes.

## 2026-09-23 - CI harness correction after PG-131 expansion

Pre-Unreal #762 failed because transition-unit tests had not been updated consistently after adding a second required transition marker. The correction changes only the regression harness semantics: imported `required_markers` is used directly and success requires the full transition marker list rather than the first marker alone. No production completion credit is added.

## 2026-09-23 - W00 compile/root transaction barrier follow-up

Unreal #596 on `02e4dfb81dc4dababb3c0085369cc628c4704bb3` did not reach import/runtime: UE4.27 C++ compile failed on an ambiguous `ObjectPathToPackageName(const TCHAR*)` call introduced by the stricter material preflight wave. That defect is fixed with explicit `FString` typing.

The same audit wave adds a systemic gameplay-mutation barrier tied to ChapterWorldRouter's authoritative world hold. Physical gameplay mutation paths now require committed world identity, and transition CI checks the barrier while a destination request is still uncommitted. These are stabilization changes only; no completion percentage or CompletionWave status is advanced.

## 2026-09-23 - W00 exact-head #595 green, followed by stricter import-quality closure

On `a148d1afa919fa63725e3760684d6eed061c5e40`, Pre-Unreal #760, Warehouse #174 and Unreal #595 all passed. Unreal #595 completed compile, production import, Automation, startup, P1C01-P1C08 aggregate runtime, persistence state roundtrip, continuous route/chapter transitions and warning-debt analysis. This validates the prior persistence/transaction/streaming repair wave on that exact head.

The build still reported 137 unique nearly-zero binormal import identities under a historical ceiling of 150. That ceiling is now removed rather than accepted as permanent debt. The next source wave generates deterministic UVs in the import working copy for UV-less static OBJ assets, preflights the project master material package, and enforces zero tangent/binormal/master-surface warning debt with PG-130. Production completeness percentage does not increase from cleanup alone; W00 remains the active gate until the stricter exact-head import run is green and device/human gates are handled separately.

## 2026-09-23 - W00 persistence transaction and replay-safe async ownership

Exact-head evidence entering this wave is Unreal #594 on `38c2c958121576b68a0bfaf4e276498d4fe89dad`: C++ build PASS, production import PASS, Automation PASS, startup PASS, P1C01-P1C08 aggregate sweep PASS, production character surface PASS, state persistence FAIL with write/load/restore successful but final field verification false.

The repair does not advance production completeness. It adds atomic logical save restore, rollback publication after world reconstruction, fail-closed rollback identity invalidation, detailed disk/runtime field diagnostics including NPC memory and route progress, safe-ground transform semantics, already-resident chapter-bank commit support, and cancelled-audio callback ownership checks. W00 remains open until a fresh exact head passes persistence, continuous transitions and the warning/material chain; target-device performance and human play acceptance remain separate gates.

## 2026-09-23 - W00 exact-head #593 diagnosis and systemic source repair

PR #67 head `5840863632d04a5fac284b472fe9e5641cd522b8`: Pre-Unreal #758 PASS, Warehouse #172 PASS; Unreal #593 passed UE4.27.2 C++ compile, deterministic import, Automation 2/2, startup and P1C01-P1C08 aggregate runtime, then failed the state gate at the player production-surface residency audit. This is defect-specific engine evidence for that SHA, not acceptance of the new repair head.

The repair is systemic: post-residency chapter-bank commit notification, committed-world-gated state/save audit, non-masking surface+disk audit, movement release only after committed-world broadcast, bounded async audio ownership with weak caches, and fail-closed PG-127/PG-128 guards. Whole-game planning remains approximately 40/100 and no completion wave is advanced by this cleanup.

## 2026-09-23 - W00 systemic hardening status

Current whole-game planning completion remains approximately 40/100. The active work is not a new feature wave; it is W00 architecture/build hardening so later waves do not inherit recurring defects. Unreal Build #588 reached C++ compilation and exposed a single importer-source text artifact, now repaired at source and guarded by Pre-Unreal. Production maturity does not advance until fresh exact-head engine proof succeeds.

## 2026-09-22 - stabilization gate schema correction

The architectural stabilization gate is the current execution focus but its quality status is correctly `PARTIAL`, not `ACTIVE`. This repairs Governor schema consistency only and does not promote compile, PIE, device, visual or whole-game completion status.

## 2026-09-22 - stabilization guard correction

Pre-Unreal #747 failed one intentional stabilization guard: the chapter harness was non-fail-fast but did not yet print the required aggregate `RUNTIME_SWEEP_SUMMARY`. The missing marker is now implemented. This does not change the 40/100 production estimate or promote compile/PIE/device/visual evidence.

## 2026-09-22 - architectural stabilization gate

Whole-game planning completion remains approximately **40/100**; this hardening wave does not manufacture production percentage from refactoring. Build #547 proved the recovered runner can compile/import and execute startup/P1C01-P1C04, but the exact hardening head has not yet passed engine validation.

Source-level stabilization now includes: shared seam-tolerant spawn grounding with slope/capsule checks and no chapter-specific support pads; all-eight non-fail-fast chapter QA; skeletal-rig package preflight before async load; BMP-to-TGA migration with BMP prohibition; and cleanup of all 304 known duplicate-vertex triangulation-risk faces with strict regression failure.

Status: **SOURCE HARDENED / EXACT-HEAD ENGINE PROOF PENDING**. No PIE/device/visual column is promoted. Feature expansion remains blocked by `REQ-STABILITY-001` until static, compile/import, P1C01-P1C08, state/transition and warning/material gates are green on one exact head.

## 2026-09-22 - P1C05 grounding regression repair

Exact-head `a42679a4de808ce1f9bada7974ad87d52ee18fa9` reached a successful UE4.27.2 C++ build, successful production import, successful two-test Automation Framework suite and successful headless startup/P1C01-P1C04 chapter audits. P1C05 failed before chapter readiness because its authored spawn at X=-2400 fell into a narrow gap between fallback ground and the first route slab. A hidden deterministic spawn-support pad is now added at that exact start. The repair head still requires fresh engine/headless proof and does not promote PIE/device/visual acceptance.

## 2026-09-22 - runner recovery / compile repair boundary

The self-hosted runner has crossed the former Engine Content ACL gate and reached real UE4.27.2 C++ compilation on Unreal Build #534 attempt 3. That attempt is not COMPILE-TESTED because it failed on an EditorTools-to-runtime header visibility defect. A source fix now exports the flat runtime module root temporarily for editor QA and removes the observed deprecated StaticMaterials access. Production maturity is unchanged until the new exact-head build turns green.

## 2026-09-22 - runtime StaticMesh mobility warning

A source-level warning fix is applied to the four runtime world builders: mobility is now changed before runtime `SetStaticMesh` assignment, matching the live PIE warning observed on the laptop. This is a warning/debt reduction only and does not promote gameplay completeness. Fresh exact-head UE4.27 compile/PIE proof is still blocked by W00 runner ACL until repaired.

## 2026-09-22 - integration gap closure status

Cross-system maturity improved at source level without changing the whole-game planning percentage. Three previously open architecture risks now have source fixes: committed-world NPC context synchronization, character-rig handle lifetime release, and removal of non-engine synchronous runtime LoadObject paths from world/character/enemy/audio production resolution. DeepProjectAudit now guards these invariants against regression.

Status remains **SOURCE FIX / STATIC EVIDENCE PENDING FINAL HEAD**, not compile/runtime acceptance. The W00 runner ACL blocker still prevents UE4.27.2 compile, PIE, device and visual proof, so no production-completeness percentage is promoted from this repair alone.

## 2026-09-22 - deep organization and integration audit

Current production maturity is unchanged by this audit. Warehouse #99 is real staged/audited evidence (240 payload files / 3,816,657,674 bytes), but Pre-Unreal #685 is red from roadmap/governor drift and Unreal #520 remains blocked before compilation by the runner Engine Content ACL. The camera requirement mapping is repaired at source/governance level; engine proof is still pending.

Cross-system review adds two tracked HIGH risks without promoting maturity: NPC regional/film context currently follows logical quest state rather than committed-world identity during async swaps, and character-rig async handles have no bounded inactive-cast eviction policy yet. Ambient NPC pooling is corrected from “missing” to “implemented pending proof.” Remaining direct LoadObject concentration is still a scaling debt for W01+ after W00 restores engine validation.

## 2026-09-22 - final pre-runner warehouse saturation batch

Warehouse breadth gains three verified official KayKit CC0 public-GitHub support lanes: food/kitchen/interior props, selective dark/cemetery props, and manually filtered generic civic props. This is sourcing/staging maturity only. No UE import, compile, PIE, device, performance or visual maturity is promoted by this batch. The next major gate is W00 runner/exact-head unlock.

## 2026-09-22 - character visibility warehouse bridge

Character production remains PARTIAL, but the next visible bridge is now concrete rather than abstract. Official KayKit Skeletons 1.0 is registered as CC0 rigged/animated FBX/GLTF technical QA stock, while KayKit Adventurers remains staged background/retarget support. The warehouse audit now validates archive-style payload receipts and license-snapshot hashes, improving provenance integrity for these non-interactive public-GitHub lanes.

This does not promote character maturity: no new skeletal asset has yet been imported into UE4.27.2 on the current head, no proxy has been replaced on screen by this change, and no compile/PIE/device/visual acceptance is claimed. The runner Engine Content ACL blocker still prevents the real import/runtime proof.

## 2026-09-22 - KayKit public-GitHub warehouse/world-foundation increment

Evidence entering this increment: PR #67 `d856a716d5bc270ce0ddc2d649acbb1656ae112c` had Pre-Unreal #670 SUCCESS and Warehouse Stage #80 SUCCESS. Unreal Build #505 did not execute C++ build/import/runtime because the non-elevated NETWORK SERVICE runner could not read UE4.27.2 `WorldGridMaterial.uasset` after the guarded remediation deferred. Therefore no compile, PIE, device, performance or visual maturity is promoted.

The warehouse now has a non-interactive official-public-GitHub KayKit lane for supporting medieval/world layout, dungeon/interior layout, background rig/retarget QA and furniture props. Every successful download remains STAGED with source/license/hash evidence; READY_FOR_IMPORT and later states remain separate. Regional mappings are preproduction/shared-foundation support only where Part II/III runtime gates are closed. P1C01 remains the first assembled benchmark.

## 2026-09-22 - hourly three-lane warehouse/world/integration continuation

Exact-head evidence before this batch: PR #67 `f41d5e91ac2a789387e987ff759b9e674cd86e10` had Pre-Unreal #667 SUCCESS and Warehouse Stage #76 SUCCESS. Unreal Build #502 stopped at the unchanged UE4.27.2 Engine Content verification after the guarded ACL-remediation attempt; C++ build/import/Automation/startup/chapter/state steps did not execute. Therefore no compile, PIE, device, performance or visual maturity is promoted.

The warehouse lane adds official Quaternius CC0 acquisition/candidate coverage for modular background humans, monster/creature pipeline testing, supporting buildings and dungeon/interior architecture. Their state is CANDIDATE or AUTHORIZED_FOR_STAGING only; final animated characters and creatures still require skeletal FBX with real rigs plus intake/deformation/visual review. The world-foundation lane assigns that stock to appropriate regions while retaining P1C01 as the first assembled benchmark and keeping Part II/III regions PREPRODUCTION_ONLY. Runtime architecture constraints remain soft/async heavy loading, ISM/HISM for repeated detail and bounded pooled populations.

## 2026-09-22 - ACL remediation attempt and trilogy material stock expansion

A safe read-only ACL remediation attempt now precedes the unchanged UE4 Engine Content preflight, and a second ambientCG batch adds non-Shire regional material stock across the trilogy. This advances integration readiness and warehouse breadth only; engine compile/runtime/visual acceptance remains pending.

## 2026-09-22 - autonomous three-lane production iteration

PR #67 exact head before this production batch was `0c8130a33f8df3648d270d8bd0ee6b24aee882fb`. Pre-Unreal Validation #653 completed successfully on that exact SHA. Unreal Build Validation #488 did **not** reach C++ compilation: the self-hosted `UE4-27-Windows` runner executed as `NT AUTHORITY\\NETWORK SERVICE` and was denied read access to `Engine/Content/EngineMaterials/WorldGridMaterial.uasset` on all six preflight probes. Build, import, Automation Framework, startup, chapter and state steps were therefore skipped. This remains an Engine Content ACL/environment blocker, not compile evidence.

Warehouse saturation advanced without promoting asset maturity. `TrilogyAssetCandidateQueue.json` now includes concrete Quaternius animation/prop and Kenney world/fortification/nature/interior/UI support candidates already tied to official CC0 pack pages. `TrilogyAudioAssetCandidateQueue.json` now mirrors stage-authorized OpenGameArt CC0 prototype music/SFX candidates across Shire, Bree, Rohan and large-battle routing tests. `WarehouseAmbientCGAcquisitionBatchV1.json` is expanded into a trilogy-foundation material intake covering snow/ice, cave stone, wetland ground, white stone, volcanic/ash surfaces, industrial metal, Rohan pastoral surfaces, ruins and river/wet materials. AUTHORIZED_FOR_STAGING and STAGED remain distinct from READY_FOR_IMPORT / IMPORTED / INTEGRATED / ACCEPTED.

Multi-region world-foundation preproduction is no longer a list of region names only. Every declared region from Shire through Grey Havens now carries explicit stock contracts for architecture, terrain/materials, vegetation/ecology, props, populations/factions, audio, lighting/atmosphere, VFX and traversal/collision, plus preferred warehouse source lanes. P1C01 remains the first assembled benchmark; later-film regions are explicitly PREPRODUCTION_ONLY and this work does not open Part II/III runtime chapters.

Current code/runtime acceptance is unchanged by these warehouse/world-plan edits. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made for the new head.

## 2026-09-22 - failed-swap rollback transaction source repair

Failed-swap rollback now restores player-life state (health, stamina, resolve, supplies) in addition to the previously restored world/quest/memory/progression/knowledge/player-transform state, and source-contract tests protect the ordering before movement release. Integration/save maturity remains PARTIAL until exact-head UE4.27 compile/runtime evidence exists.

## 2026-09-22 - trilogy-wide world foundation parallelism

World production planning is no longer Shire-only. Reusable foundations are now tracked across all major trilogy regions while P1C01 remains the first fully assembled benchmark. This advances preproduction and warehouse coverage only; it does not promote later chapters to runtime-ready status.

## 2026-09-22 - Resource Bible 09 source expansion and new warehouse stagers

Source 09 is now operational rather than passive documentation. Its broad resource families have been merged into the machine-readable global source registry, and concrete staging lanes now include ambientCG CC0 materials plus Kenney CC0 support/world kits in addition to the existing Poly Haven, Quaternius and OpenGameArt lanes. This advances warehouse source breadth and STAGED acquisition only; no UE import/runtime/visual/audio/device acceptance is promoted by this sourcing wave.

## 2026-09-22 - pooled visual fallback hardening

The async living-world ownership wave now also resets every reused ambient actor to constructor-owned Engine primitive meshes before resolving role-specific production soft objects. This prevents a pooled NPC that changes regional role from retaining a stale Human/Elf/Hobbit mesh when a production asset is unavailable. Active density and streaming policy are unchanged. Exact-head CI/UE evidence remains required; no runtime verification claim is made.

## 2026-09-22 - asynchronous living-world asset ownership

The registered living-world synchronous production-load defect is now repaired at source level using the existing two-phase chapter streaming architecture rather than introducing another loader. `Data/ChapterAssetStreamingPlan.json` now explicitly places the ambient production surface, Hobbit/Human/Elf resident meshes, and chapter-used fauna meshes into the relevant soft chapter banks. Their lifetime is therefore owned by the resident `FStreamableHandle`, which remains alive until a replacement world successfully commits.

`AShireAmbientNPC::ApplyVisualStyle` no longer synchronously `LoadObject`s production meshes or the production surface. It resolves only already-resident soft objects and keeps constructor-owned Engine primitive/material fallbacks when a production asset is unavailable. `LivingWorldDirector` likewise resolves its ambient motion production meshes from the resident bank instead of initiating synchronous package loads. This preserves the current async/no-game-thread-wait policy and does not increase active density.

Exact-head static/CI validation is still required for this change. Runtime rendering and transition behavior remain unproven until matching UE4.27.2 evidence exists; no COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made.

## 2026-09-22 - bounded ambient NPC pooling foundation

The registered baseline SpawnActor/Destroy churn is now repaired at source level with lazy bounded reuse. `LivingWorldDirector` owns an ambient-NPC pool capped at 24 cached actors but does not preallocate it or change authored active-density targets. Baseline culling, chapter reset, and expired micro-events return ambient NPC actors to the cache when capacity is available; non-NPC event actors still destroy normally, and excess cached candidates are destroyed rather than growing memory without bound.

`AShireAmbientNPC` now has an explicit deactivate/reactivate lifecycle that clears social/awareness/caption state, disables tick and visibility while cached, and fully reapplies routine role, prop, movement and lightweight needs state on reuse. Pooled actors are excluded from social-partner selection. This targets spawn/destroy churn while preserving the i7 Gen6 / 8 GB RAM / ~2 GB VRAM budget and does not increase world density.

This remains source-only until exact-head validation runs. It is not COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED.

## 2026-09-22 - ground-safe living-world ambient placement

The next registered foundation defect is repaired at source level without increasing density. `LivingWorldDirector::SpawnAmbientActor` now proves blocking ground with a vertical visibility trace before spawning ground-bound ambient roles and separately grounds their routine endpoint. If the initial point has no blocking ground the spawn is rejected; if only the travel endpoint is unproven, the actor remains at its grounded start rather than walking toward an unsafe Z. Bird and butterfly roles retain their authored airborne placement, while rabbit and humanoid residents use the ground-safe path.

This is a low-cost placement guard for the existing UE4.27.2 / low-spec architecture; it does not add navmesh cost or new population. Wall/obstacle avoidance and rendered placement quality still require runtime observation. Exact-head static validation must pass before the next lifecycle repair. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made.

## 2026-09-22 - failed world-swap rollback transaction repair

The registered transition-persistence defect wave now includes a source-level rollback transaction repair. `ChapterWorldRouter` captures the last committed quest/route/world identity plus player transform after each successful world commit. If destination construction, grounding, or asset-bank commit fails, the pending request is cancelled, the prior logical state and builder are restored under a rollback guard, the player is grounded back at the committed transform, movement is released only after that succeeds, and a fresh `WorldRevision` is broadcast for the rebuilt committed world.

This closes the known source-level gap where rollback rebuilt prior geometry but left movement held and logical/player state incoherent. It is **not** runtime closure yet: exact-head static validation is required next, and UE4.27 compile/PIE/device evidence remains separate. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made.

# PRODUCTION COMPLETENESS MATRIX

## 2026-09-22 - global source matrix expansion

Warehouse sourcing now uses a ranked multi-provider matrix rather than a few favored sites. Clear public/CC0 sources are prioritized for automatic staging; account/marketplace sources remain explicit review lanes; niche/reference-only sources cannot silently enter Approved. This advances sourcing breadth and intake discipline only, not import/integration/visual acceptance.

## 2026-09-22 - warehouse staging launcher repair

Warehouse Stage #18 failed before acquisition because the runner's PowerShell execution policy blocked GitHub's temporary `shell: powershell` wrapper. The workflow now launches repository-owned staging scripts from cmd with `-ExecutionPolicy Bypass -File`. No warehouse file is promoted until the next run reports actual staged receipts.

## 2026-09-22 - multi-lane warehouse acquisition

The persistent warehouse now has concrete staging lanes for environment/materials (Poly Haven), music/foley (OpenGameArt), and character/animation/fauna/world-kit candidates (Quaternius). Direct-download lanes preserve source/license/hash receipts; unresolved interactive-store packs remain candidates rather than being misreported as staged. This advances warehouse stock acquisition only and does not promote UE import, runtime, visual or device acceptance.

## 2026-09-22 - active warehouse fill execution

Warehouse production is now executing real staged-download batches rather than only cataloguing candidates. The first Poly Haven batch has verified source pages, resilient per-asset staging and receipt/skipped-item accounting. This advances asset acquisition infrastructure and stock readiness only; UE import/runtime/visual acceptance remain later states.

## 2026-09-22 - persistent asset warehouse staging

The project now has a dedicated persistent warehouse staging workflow separate from UE runtime validation. The first CC0 Poly Haven batch is machine-defined and stages to a persistent self-hosted folder with receipt/hash intent. This advances warehouse acquisition infrastructure only; staged files are not imported, integrated or visually accepted by this change.

## 2026-09-22 - warehouse roadmap reconciliation after Pre-Unreal #597

The new trilogy warehouse requirement/work item is now explicitly assigned to the master execution roadmap and the roadmap's unfinished/active snapshots are regenerated from ProjectGovernor. This repairs governance consistency only; asset/runtime maturity is unchanged. Unreal #432 remains pre-compile blocked by local Engine Content permissions.

## 2026-09-22 - trilogy warehouse-first production lane

A trilogy-wide production warehouse is now explicitly tracked. This closes the planning/coverage problem where characters, world art, creatures, materials, animation and audio could remain unspecific late-stage gaps. The catalogue includes all major trilogy production families and exact first-pass slots, but actual final assets remain at mixed readiness states and are not promoted merely because their slots are catalogued.

P1C01 remains the first full natural-character/world/audio benchmark. Part II/III warehouse sourcing and kit preparation may run in parallel without opening runtime chapter implementation ahead of the existing gates. No visual/audio/device acceptance column is promoted by this catalogue wave.

## 2026-09-22 - cinematic audio warehouse V2 registered

Audio production now has an explicit sourcing/warehouse plan covering voice, dynamic music, ambience/fauna, foley and creature/combat effects. Existing runtime routing remains intact; authored approved assets, spatial/concurrency listening review and target-device audio profiling are still pending, so Voice/Audio maturity is not promoted by this planning wave.

## 2026-09-22 - V7 async character static-guard reconciliation

Pre-Unreal #578 exposed four stale character-production assertions that still described the old synchronous rig probe. PG-051/PG-089 now validate the V7 FStreamableManager character-rig path and forbid synchronous skeletal-mesh/animation-class loading in the playable character handoff. Runtime behavior and visual acceptance are unchanged by this validator repair.

## 2026-09-22 - async character wave static regression repair

Pre-Unreal #576 identified one source-structure regression in the new async character-rig wave: a duplicated `AShirePlayerCharacter::EndPlay` signature left braces unbalanced. The duplicate is removed and the exact-head gates are being rerun. Unreal Build #411 had an online runner but stopped before compilation on the existing UE4 Engine Content read-permission failure, so compile/runtime maturity remains unchanged.

## 2026-09-22 - commit-synchronized persistence implementation

The first post-static-gate runtime repair now synchronizes automatic chapter checkpoint capture and saved-player transform restoration with `ChapterWorldRouter` committed chapter/route/episode identity. Saved transforms are grounded against committed destination geometry before placement. The initial P1C01 checkpoint uses the same barrier.

This advances source implementation only. Save/load remains PARTIAL until exact-head UE4.27 compilation and runtime regression evidence exist, and coherent failed-swap rollback remains open. No compile, PIE, device, performance or visual column is promoted.

## 2026-09-22 - Pre-Unreal #562 streaming regression-test repair

Pre-Unreal #562 passed core validation, Project Governor and Deep Project Audit, then failed a stale source-contract test that still expected async-load completion to promote `ResidentHandle`. The current two-phase architecture intentionally promotes the resident bank only in `CommitPendingRequest` after world commit prerequisites succeed. The test is aligned to that contract without changing runtime code.

Unreal Build #397 remains environment-blocked before compilation by UE4 Engine Content read permissions. No compile, PIE, device, performance or visual maturity is promoted by this change.

## 2026-09-22 - Pre-Unreal #561 deep-audit contract repair

On exact head `ed5af300852e6e2ce2264334c560af658250434b`, the core Pre-Unreal validator passed, but the subsequent deep audit failed because it searched only `ShireChapterAssetStreamingSubsystem.cpp` for the `FStreamableManager` type marker. The type is declared in the subsystem header while the cpp contains the async request path. The deep audit is corrected to validate the header+cpp contract together and still reject synchronous `LoadObject` in the streaming cpp.

This changes static validation only. It does not close the registered checkpoint/save-restore/rollback or ambient-life findings and does not promote compile, PIE, device, performance or visual status.

## 2026-09-22 - playability audit intake and PG-117 static-gate repair

A source review of the owner-forwarded Work findings on `170ebd857bece56a6d7f76f4928efe0eb3426af2` confirms open persistence/transition and living-world risks: checkpoint capture is not world-commit synchronized, cross-chapter restore can apply a transform before world commit, rollback is not yet a coherent playable prior-state transaction, ambient placement lacks a ground-safe collision contract, and ambient population still has SpawnActor/Destroy plus direct LoadObject debt. These are registered repair work, not accepted runtime fixes.

Pre-Unreal #560 reached and passed the core validation phase, then failed one stale PG-117 assertion because V10 world/life is now the global current visual wave. The guard is narrowed to preserve the historical hero-equipment V4 asset block without pinning the whole visual plan to V4. No chapter maturity, compile, PIE, device, performance or visual column is promoted by this static-guard correction.

## 2026-09-22 - PR #67 validation-gate repair

Pre-Unreal #558 on exact head `809325a64547744f0cc4992d76c42fb7e0862d82` failed with two static-guard errors caused by PG-111 still describing the V9 fixed-halving world-life contract. The integration branch already uses the V10 chapter density profile and `DangerPopulationFraction` model. PG-111 is being aligned to that existing V10 runtime/data contract without changing gameplay behavior.

Unreal Build #393 on the same SHA did not reach C++ compilation. The self-hosted runner identity `NT AUTHORITY\\NETWORK SERVICE` was denied read access to UE4.27.2 `WorldGridMaterial.uasset` on six consecutive engine-content probes. Therefore this wave remains **STATIC-PENDING** and no COMPILE/PIE/device/visual column is promoted by this repair.

## 2026-09-21 - continuous-session transition regression

A new runtime audit now requires one live session to traverse all eight Part I chapter identities, route switching, committed-world/living-world revision synchronization and disk-save roundtrip. This is implementation coverage only; no chapter is promoted to PIE/device acceptance until exact-head engine and owner evidence exist.

## 2026-09-21 - comprehensive foundation integration

Startup grounding, QA/performance guardrails, V10 regional living-world behavior and transactional chapter commit coordination are now being consolidated on one integration branch. Asset preload and visible-world commit are separated; living-world chapter state follows committed world revision rather than requested quest state.

Current status: **IMPLEMENTED / STATIC-PENDING** for the newest integration changes. No chapter validation column is promoted until exact-head Pre-Unreal, UE4 build/runtime and defect-specific PIE evidence exist.

## 2026-09-21 - visual-performance architecture guardrails

The project now tracks a measured visual-performance architecture contract: async/soft heavy assets, instanced+cull repeated detail, bounded Tick usage, role-appropriate LOD/material policy and evidence-driven lighting/shadow selection. Static guards protect the currently proven async/HISM/non-ticking-builder patterns.

This does not promote any chapter's performance, PIE, device or visual status. Draw-call, frame-time, streaming-pool, resident-memory, LOD and lighting/shadow comparisons remain target-device work.

## 2026-09-21 - engine Automation Framework QA wave

The project now has an initial UE Automation Framework layer in addition to static validation and runtime smoke. The first tests cover SaveGame default/schema invariants and post-import existence of all streamed chapter packages. Startup grounding proof now waits two seconds before PASS. These are implementation changes only; engine execution and defect-specific PIE evidence remain pending.

## 2026-09-21 - automated QA immune-system foundation

A layered automated QA initiative is now tracked as `REQ-QA-002`. The first wave adds Unreal Automation Framework coverage and exact-head CI execution after compile/import. Later world/nav/animation/performance/memory suites remain pending measured implementation. This does not alter any PIE/device/visual acceptance status.

## 2026-09-21 - deterministic P1C01 spawn collision support

The startup repair adds a hidden Engine BasicShapes support pad at the P1C01 authored road start so initial collision no longer depends on imported OBJ simple-collision generation. This strengthens the fix candidate only; COMPILE/PIE/device/visual status remains unchanged until exact-head proof exists.

## 2026-09-21 - startup grounding regression repair

A P1C01 PIE fall-through remains an open runtime defect despite an earlier spawn-height/placement change. The isolated fix removes pre-world GameMode teleporting, holds initial gravity until world commit, resolves a blocking floor before release, and adds startup/chapter grounding regression markers.

This is a **FIX_CANDIDATE**, not an accepted fix. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED status is added until the exact fix head completes engine validation and the original owner-observed P1C01 symptom is rechecked.

## Verification evidence correction and production continuation

Historical machine baseline: `develop@f7c2b081e7b064fcf27bb4c80124b21f351331ab`.

Pre-Unreal Validation #264 and Unreal Build Validation #99 passed on that baseline, including compile/import, startup, headless chapter audits and warning-debt checks. Those are valid machine checks, but they are **not** Real PIE/device visual-performance proof.

A prior conversation-level owner confirmation was incorrectly promoted into `PIE_TESTED` for all eight chapters without chapter-specific FPS, screenshot/video, or chapter-specific notes. That promotion is withdrawn. The owner confirmation remains historical authorization to resume construction; it is not chapter-by-chapter verification evidence.

Future `PIE_TESTED` / `PIE_TESTED_WITH_ISSUES` promotion requires an exact commit plus at least one chapter-specific signal: numeric FPS, screenshot/video evidence, or a concrete note unique to that chapter. Generic copied wording is rejected by PG-057.

### Current Real PIE/device evidence

| Chapter | Real PIE evidence | Stability | Crash | Target laptop perf | NPC routines | NPC-to-NPC | Named memory/context | Weather/atmosphere | Notes |
|---|---|---|---|---|---|---|---|---|---|
| P1C01 Shire | NOT_RUN | HEADLESS_ONLY | NO_HEADLESS_BLOCKER | NOT_MEASURED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | Re-establish as the chapter-specific visual/performance reference first |
| P1C02 Bree | NOT_RUN | HEADLESS_ONLY | NO_HEADLESS_BLOCKER | NOT_MEASURED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | Await chapter-specific evidence |
| P1C03 Weathertop/Ford | NOT_RUN | HEADLESS_ONLY | NO_HEADLESS_BLOCKER | NOT_MEASURED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | Await chapter-specific evidence |
| P1C04 Rivendell | NOT_RUN | HEADLESS_ONLY | NO_HEADLESS_BLOCKER | NOT_MEASURED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | Await chapter-specific evidence |
| P1C05 Road/Caradhras/West Gate | NOT_RUN | HEADLESS_ONLY | NO_HEADLESS_BLOCKER | NOT_MEASURED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | Await chapter-specific evidence |
| P1C06 Moria | NOT_RUN | HEADLESS_ONLY | NO_HEADLESS_BLOCKER | NOT_MEASURED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | Civilian baseline remains intentionally zero; Real PIE evidence still required |
| P1C07 Lothlorien | NOT_RUN | HEADLESS_ONLY | NO_HEADLESS_BLOCKER | NOT_MEASURED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | Await chapter-specific evidence |
| P1C08 Anduin/Amon Hen | NOT_RUN | HEADLESS_ONLY | NO_HEADLESS_BLOCKER | NOT_MEASURED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | NOT_HUMAN_VERIFIED | Await chapter-specific evidence |

Engineering, source, asset-foundation and automated regression work may continue behind existing gates. Visual/performance acceptance and any `Production 100%` claim remain blocked until chapter-specific evidence exists.

This file prevents major game pillars from depending on chat memory.

A chapter is not complete because its quest path works. Every chapter must be checked across all production pillars.

## Status
NOT_STARTED / FOUNDATION / PROTOTYPE / FUNCTIONAL / POLISH_PENDING / ACCEPTED

## Mandatory pillars
1. Canon/story
2. Main gameplay loop
3. Exploration/side content
4. Character visual identity
5. Body animation
6. Facial acting / gaze / lip-sync
7. Spoken voice
8. Subtitles/dialogue
9. Music
10. SFX/foley
11. Ambience
12. NPC routines/social life
13. Enemy/creature AI
14. Combat/stealth when story requires it
15. Terrain/geography/scale
16. Architecture/props
17. Vegetation/biome
18. Weather/time/atmosphere
19. Cinematic presentation
20. Save/load continuity
21. Performance on target laptop
22. Accessibility/readability
23. Guardian/static validation
24. UE4.27 compile
25. PIE/device test

| Chapter | Story | Gameplay | Exploration | Characters | Face/Anim | Voice | Audio | AI/Life | Combat | Geography | Atmosphere | Cinematic | Save | Perf | PIE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1C01 Shire | FUNCTIONAL | FUNCTIONAL | FUNCTIONAL | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | FUNCTIONAL | FUNCTIONAL stealth | FUNCTIONAL | FUNCTIONAL | PROTOTYPE | FUNCTIONAL | PROTOTYPE | PENDING |
| P1C02 Bree | FUNCTIONAL | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | NOT_STARTED | PENDING |
| P1C03 Weathertop/Ford | FUNCTIONAL | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | NOT_STARTED | PENDING |
| P1C04 Rivendell | FUNCTIONAL | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | PROTOTYPE | N/A | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | NOT_STARTED | PENDING |
| P1C05 Road/Caradhras/West Gate | FUNCTIONAL | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | NOT_STARTED | PENDING |
| P1C06 Moria | FUNCTIONAL | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | NOT_STARTED | PENDING |
| P1C07 Lothlorien | FUNCTIONAL | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | PROTOTYPE | N/A | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | NOT_STARTED | PENDING |
| P1C08 Anduin/Amon Hen | FUNCTIONAL | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | NOT_STARTED | PENDING |

## Validation evidence versus maturity

The status table above describes **production maturity**. Validation proof is recorded separately so a successful compile/import is never confused with visual or gameplay acceptance.

### P1C01 Shire production environment
- CP28 introduced project-managed production source assets for Shire environment/props and runtime code now prefers imported production meshes while retaining BasicShapes as fallbacks.
- The production asset pipeline is COMPILE-TESTED and ASSET-IMPORT-TESTED on UE4.27.2.
- Validated baseline `e739ba6e364d0316cf5b7fe10c1f8ecaa13d417e` passed Pre-Unreal Validation #113 and Unreal Build Validation #11; the production importer reported `50 files, 0 failures`.
- The newer Shire visual content is still pending focused PIE traversal, target-device performance review and VISUALLY-ACCEPTED status.
- Character visual identity remains PROTOTYPE/FOUNDATION where the final rigged/animated/voiced production character standard is not yet satisfied.

### Repository build gate
- CP29 established a self-hosted Windows UE4.27.2 runner on the target laptop.
- Every pushed `develop` commit is eligible for the exact-commit UE4.27.2 C++ build and production asset-import gate.
- Green CI never substitutes for PIE, device or visual acceptance.

### Source architecture / handoff
- `Source/ShireJourney/README.md` is the code-level handoff entry point inside the runtime module.
- `Data/SourceArchitecturePlan.json` assigns every runtime source file to its accepted Public/Private domain path; CP-W00-154 exact head `ab7889d6...` passed Pre #788, Unreal #623 and Warehouse #204 after the physical migration.
- Project Guardian must reject untracked runtime source files so a new human or automated programmer cannot silently expand the module without updating the architecture map.

## Voice rule
Every runtime non-empty VO_* identifier must exist in Data/VoiceCuePlan.csv.
Voice status remains FOUNDATION while required voice assets are ASSET_PENDING.

## Update rule
Whenever a chapter, route, enemy, biome, mechanic or major story beat changes:
- update this matrix,
- update the relevant story/audio plan,
- add Guardian validation where machine-checkable,
- do not mark ACCEPTED without real UE4.27/PIE evidence.
## 2026-09-30 - P1C01 overnight preparation / save-history reconciliation

This wave changes preparation contracts and static validation only; it does **not** promote any production-completeness acceptance column.

W00 machine closure is inherited from PR #184 exact head `d6ca8aac03f5a1da07609e61e790ddf8faad8eed` (Pre-Unreal #1435 SUCCESS, Unreal Build #1108 SUCCESS including packaged Runtime Data verification and packaged executable observation). The current P1C01 successor PR must still satisfy its own current exact-head engine gate before merge or runtime-car expansion.

The save audit now records only reachable, reviewable history: schema 3 introduced explicit version metadata; schema 4 added Journey Discovery fields; schema 5 added stamina/resolve/supplies/progression XP; schema 6 added Chronicle/map-knowledge fields. Explicit schema 1/2 semantics remain undocumented, so no compatibility or migration claim is promoted.

Zero-silent-omission preparation now explicitly tracks dialogue knowledge flags/cinematic-skip postcondition equivalence and safe optional-window expiry. Runtime gameplay, target-device performance, human PIE, visual quality and audio listening remain gated and unaccepted.

## 2026-09-30 - P1C01 BAG_END_LIVED_IN_PASS hero car

- SHIRE_WORLD_DENSITY predecessor: **STATIC-VALIDATED + UE4.27.2/headless machine-green** on PR #192 / Pre-Unreal #1467 / Unreal #1140; merged develop #1468/#1141 also green.
- Bag End hero source implementation: **SOURCE-IMPLEMENTED / EXACT-HEAD CI PENDING**.
- Exterior hero budget: **3 HISM clusters / 34 non-collision instances + 8 static lived-in props**.
- Quest-state variants: **5 Birthday props + 5 Departure props**, visibility-swapped from existing ShireQuestSubsystem delegate events; no Tick and no transition Spawn/Destroy churn.
- AI population: **UNCHANGED at 18**.
- Story anchors / locked F1-01/F1-02 outcomes: **UNCHANGED**.
- Dedicated Bag End interior: **CONTENT_PENDING**; no production interior shell/kit exists in the repository and no completion claim is made.
- PIE collision/readability, human visual acceptance and target-device performance: **PENDING / NOT CLAIMED**.

## 2026-09-30 - P1C01 PARTY_AND_SOCIAL_LOOP car

- BAG_END_LIVED_IN_PASS predecessor: **STATIC-VALIDATED + UE4.27.2/headless machine-green** on PR #193 / Pre-Unreal #1469 / Unreal #1142.
- Party/social source implementation: **SOURCE-IMPLEMENTED / EXACT-HEAD CI PENDING**.
- Visual budget: **4 HISM clusters / 48 non-collision decorative instances + 14 static party props + 8 state-variant props**.
- Optional gameplay: **3 birthday-setup beats + 2 multi-step activities** (Fireworks Safety and Dragon Firework Mishap), all story-window gated and non-mandatory.
- Progression/save: **DATA-WIRED** through existing side-activity/discovery first-time reward path; direct reward bypass remains rejected by ShireQuestSubsystem.
- Ambient AI population: **UNCHANGED at 18**.
- F1-01 locked outcome: **UNCHANGED**.
- New gameplay subsystem / per-frame scan / synchronous heavy load: **NONE**.
- PIE activity retry/window behavior, human party visual/pacing review and target-device performance: **PENDING / NOT CLAIMED**.

## 2026-10-01 — Deep Audit V1 / visual-quality governance

| Area | Current status | Evidence boundary |
|---|---|---|
| Balanced Medium visual target | GOVERNOR-LOCKED | Selective High for visually important content; no visual acceptance claimed |
| Deep Audit R-01..R-10 | ADOPTED AS VALIDATION MATRIX | 0 confirmed defects; 10 hypotheses requiring source/runtime measurement |
| Compound settlement-entry performance | MEASUREMENT REQUIRED | Target-device/standalone evidence pending |
| Tail-frame telemetry | REQUIRED FOR ACCEPTANCE | p95/p99/max + Game/Draw/GPU; not yet accepted |
| Long-session memory/save-load stability | SOURCE-GUARDED / DEVICE EVIDENCE PENDING | Existing bounded contracts retained |

## 2026-10-01 - Gate 6/7 + local visual bootstrap reconciliation

| Area | Status | Evidence boundary |
|---|---|---|
| SAVE_LOAD_LONG_SESSION predecessor | MERGED / machine-green | #200 merged at `7ad697ed146e356dea9e591ccf61a8268138bc3b` |
| Gate 6/7 evidence evaluator | RECONCILED / FAIL-CLOSED | Device + human evidence still pending |
| Visual quality target | GOVERNOR-LOCKED | Balanced Medium + selective High, 30 FPS floor retained |
| Local production import/bootstrap | SOURCE-IMPLEMENTED | Local execution/rendered review pending |
| Runtime ownership | UNCHANGED | Existing router/world/living-world/quest owners remain authoritative |
| PIE / device / visual / pacing / performance | NOT ACCEPTED | Requires real matching evidence |

## 2026-10-01 - Gate 6/7 + local visual bootstrap reconciliation

| Area | Status | Evidence boundary |
|---|---|---|
| SAVE_LOAD_LONG_SESSION predecessor | MERGED / machine-green | #200 merged at `7ad697ed146e356dea9e591ccf61a8268138bc3b` |
| Gate 6/7 evidence evaluator | RECONCILED / FAIL-CLOSED | Device + human evidence still pending |
| Visual quality target | GOVERNOR-LOCKED | Balanced Medium + selective High, 30 FPS floor retained |
| Local production import/bootstrap | SOURCE-IMPLEMENTED | Local execution/rendered review pending |
| Runtime ownership | UNCHANGED | Existing router/world/living-world/quest owners remain authoritative |
| PIE / device / visual / pacing / performance | NOT ACCEPTED | Requires real matching evidence |


## 2026-10-01 - Frodo candidate warehouse targeted repair

| Area | Status | Evidence boundary |
|---|---|---|
| Warehouse Stage #302 on `develop@b8cee93c` | FAILURE | Ended inside material-provenance repair; no terminal job log and no candidate artifact |
| Exact terminal runner/service cause | UNKNOWN / FAIL-CLOSED | GitHub retained the active step without a terminal step conclusion; do not invent a cause |
| Full Poly Haven `-Refresh` | REMOVED IN REPAIR CANDIDATE | Replaced by receipt SHA256 validation and targeted purge/redownload |
| Repair-step duration | BOUNDED TO 20 MINUTES | Exact-head workflow proof pending |
| Frodo/Gandalf candidate report | NOT PRODUCED | No character import, runtime promotion, visual acceptance, or Gate 6/7 closure |


## 2026-10-01 - P1C01 hero-provider prerequisite repair candidate

| Area | Status | Evidence boundary |
|---|---|---|
| Warehouse #307 on `develop@2363d3f9` | FAILURE | Inventory/critical-gap stages passed; hero candidate coverage failed |
| Persistent inventory | CLEAN IN RUN #307 | `239` active verified records; `0` pending; `0` manual queue |
| Frodo/Gandalf intake | BLOCKED BY MISSING STAGING | `prepared=0`, `pending=4`, `blocked=0`; both candidate pools were zero |
| Quaternius hero prerequisite | SOURCE-IMPLEMENTED REPAIR CANDIDATE | Bounded to four authorized FBX/CC0 source packs; exact-head proof pending |
| Regression guard | SOURCE-IMPLEMENTED | Pre-Unreal contract test requires exact pack parity and provider staging before candidate report |
| Runtime character promotion | NOT STARTED | No READY_FOR_IMPORT, skeletal import or runtime replacement claim |
| PIE / device / visual / pacing / performance | NOT ACCEPTED | Real matching evidence still required |


## 2026-10-01 - P1C02 Bree preproduction opening

| Area | Status | Evidence boundary |
|---|---|---|
| P1C02 Bree / The Prancing Pony source contract | SOURCE-IMPLEMENTED | `Data/P1C02BreePreproductionV1.json` |
| F1-04 shared source superpack binding | SOURCE-IMPLEMENTED | Existing Bree/Weathertop pack reused; no duplicate payload lane |
| Bree canon/world grammar | SOURCE-LOCKED | Project Bibles + Tolkien Book One IX-X |
| Existing Bree source stock | QC REQUIRED | Static support stock only; no visual acceptance |
| P1C02 runtime integration | PREDECESSOR-GATED / NOT STARTED | Requires P1C01 Gate 6/7 ACCEPTED |
| P1C02 PIE / device / visual / pacing / performance | NOT ACCEPTED | Real matching evidence required after runtime activation |


## 2026-10-01 - P1C03 Weathertop / Ford preproduction opening

| Area | Status | Evidence boundary |
|---|---|---|
| P1C03 Weathertop / Ford source contract | SOURCE-IMPLEMENTED | `Data/P1C03WeathertopFordPreproductionV1.json` |
| F1-04 Weathertop source binding | SOURCE-IMPLEMENTED | Existing shared pack reused; no duplicate payload lane |
| Ford handoff boundary | SOURCE-LOCKED / PREPRODUCTION | Wounded pursuit / Ford crossing / Rivendell handoff only |
| Existing Weathertop stock | QC REQUIRED | Static support stock only; no visual acceptance |
| P1C03 runtime integration | PREDECESSOR-GATED / NOT STARTED | Requires P1C02 Gate 6/7 ACCEPTED |
| P1C03 PIE / device / visual / pacing / performance | NOT ACCEPTED | Real matching evidence required after runtime activation |


## 2026-10-01 - Whole-game resource coverage audit V2

| Domain | Status | Evidence boundary |
|---|---|---|
| Generic PBR surfaces/materials | BROAD SOURCE COVERAGE | Poly Haven/ambientCG and existing warehouse lanes; runtime integration remains per-region |
| Supporting static props/interiors | BROAD SOURCE COVERAGE | Kenney/KayKit/project stock; hero visual acceptance not implied |
| Hero humanoid bases | CRITICAL GAP | Generic/support bases exist; final named-character skeletal FBX + deformation/art QC still required |
| Canonical creature bases | CRITICAL GAP | Species-specific rigs/deformation/LOD still required |
| Humanoid + creature animation | CRITICAL GAP | Manual/authenticated motion sources required; retarget QC per rig family |
| Realistic hero architecture | HIGH GAP | Support kits exist; culture/region-specific hero silhouettes need higher-fidelity licensed/custom sources |
| Biome-specific vegetation | HIGH GAP | Generic nature stock exists; ecology identity/LOD/overdraw QC still required |
| Battle/siege support | HIGH GAP | Modular/background support needs expansion and canon-specific silhouette filtering |
| Whole-game audio depth | HIGH GAP | Manual licensed libraries required for ambience/foley/creature/combat/weather breadth |
| Weather/battle VFX | HIGH GAP | Baked/flipbook/UE4.27-compatible source acquisition still required |
| Water/boats + mounted pipeline | MEDIUM GAP | Dedicated interaction/rig/source QC still required |
| Quaternius automated staging | CORRECTED TO MANUAL | #308: `files=0 unresolved=4`; page reachability no longer counts as payload staging |
| PIE / device / visual / performance acceptance | UNCHANGED | Source audit creates no runtime acceptance |


### Resource-audit guard delta

| Area | Status | Evidence boundary |
|---|---|---|
| Quaternius zero-payload staging | SOURCE-IMPLEMENTED FAIL-CLOSED | `files=0 && unresolved>0` now exits nonzero |
| Zero-payload regression test | SOURCE-IMPLEMENTED | Pre-Unreal wiring added; exact-head result pending |
| Provider access policy | SOURCE-IMPLEMENTED | Quaternius reclassified manual-clear-license |
| Whole-game gap audit | SOURCE-IMPLEMENTED | 28 regions + cross-cutting characters/creatures/animation/audio/VFX/gameplay-support domains |

## 2026-10-01 - Warehouse #309 manual-provider continuation repair

| Area | Status | Evidence boundary |
|---|---|---|
| Quaternius support resolution | MANUAL QUEUE REQUIRED | #309: `files=0 unresolved=17`; no payload staged |
| Default zero-payload behavior | FAIL-CLOSED RETAINED | Exit code 3 remains the default |
| Workflow manual-provider handling | SOURCE-IMPLEMENTED REPAIR CANDIDATE | Explicit `-RecordManualQueue`; no staging PASS and no broad error suppression |
| Persistent warehouse payloads | PRESERVED | No full Poly Haven rerun; valid staged files are untouched |
| Frodo candidate artifact | REPAIR PENDING | Workflow must reach candidate report/upload on a fresh exact head |
| Runtime / Gate 6/7 acceptance | UNCHANGED / NOT ACCEPTED | No character import or human/device evidence |


## 2026-10-02 - Warehouse #310 generated-worktree caller-checkout repair

| Area | Status | Evidence boundary |
|---|---|---|
| Persistent Warehouse inventory | RUN-PROVEN CLEAN | #310: 18,925 payload files / 6,745,967,498 bytes / 239 active / 428 superseded / 0 duplicate groups |
| Poly Haven / ambientCG provenance | REUSE-PROVEN | 219 + 8 receipt-verified files reused; no blind refresh |
| P1C01 mega promotion | RUN-PROVEN WITH MANUAL QUEUE | 36 prepared / 34 intake-QC / 3 pending / 2 manual |
| Generated P1C01 materials | SOURCE BRANCH CREATED | 8 receipt-verified sources; runtime/visual acceptance not implied |
| Caller-checkout survival | SOURCE-IMPLEMENTED REPAIR CANDIDATE | Bounded cleanup, overlap rejection, metadata prune, downstream script guard |
| Frodo candidate evidence | BLOCKED BY #310 INFRASTRUCTURE FAILURE | Report did not run; artifact did not exist |
| Runtime / Gate 6/7 acceptance | UNCHANGED / NOT ACCEPTED | No character import or human/device evidence |


## 2026-10-02 - Warehouse #311 exact Frodo blocker and direct CC0 fallback

| Area | Status | Evidence boundary |
|---|---|---|
| Caller checkout survival | RUN-PROVEN | #311 reached hero staging/report after generated material export |
| Warehouse inventory | RUN-PROVEN CLEAN | 18,932 files / 6,808,598,106 bytes / 0 duplicate groups |
| Candidate artifact | RUN-PROVEN / DIGEST MATCHED | SHA256 `37b7a51113d8d3ddc750522e8f7c68ac6b277424f4bf4269108d82f4b82c1dc2` |
| Frodo / Gandalf candidates | TRUE BLOCKER | 0 FBX / 0 pools; four Quaternius manual-source packs pending |
| OpenGameArt Quaternius fallback | SOURCE-IMPLEMENTED CANDIDATE | Direct CC0 archive, bounded ZIP scan, FBX gate, SHA reuse |
| READY_FOR_IMPORT / runtime | NOT STARTED | Skeleton/skin/deformation/FBX-2018 QC still required |
| Gate 6/7 | UNCHANGED / NOT ACCEPTED | No human/device evidence |


## 2026-10-02 - P1C01 hero candidate file-level provenance guard

- The hero intake now records a provenance row for every admitted FBX, binding candidate file path to provider, source asset ID, receipt, source payload and verified SHA256.
- The exact-head hero candidate wave fails closed before ranking when any discovered FBX lacks exactly one provenance row; ranked rows now carry the provenance fields into the evidence artifact.
- This closes the gap between `candidate_policy.require_provenance=true` and actual per-file candidate evidence without promoting any asset to READY_FOR_IMPORT.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD VALIDATION PENDING**. No skeleton, skin-weight, deformation, import, PIE, device, visual or performance acceptance is claimed.


## 2026-10-02 — P1C01 warehouse-first world expansion V1

- Added `Data/P1C01WarehouseWorldExpansionV1.json` and a hosted regression guard for a warehouse-first P1C01 asset/world expansion batch.
- The batch maps approved acquisition lanes to Bag End, Hobbiton, Shire roads and Bucklebury/Ferry while preserving FBX/PNG-TGA, provenance, HISM/ISM/LOD/culling and soft/async heavy-asset rules.
- Quaternius remains a manual provider blocker and does not block independent Poly Haven/ambientCG/licensed character-animation/audio/VFX lanes.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD STATIC VALIDATION PENDING**. No PIE/device/visual/performance acceptance claim.

## 2026-10-02 - Frodo skeletal candidate semantic QC

| Area | Status | Evidence boundary |
|---|---|---|
| Direct CC0 archive | RUN-PROVEN STAGED | 48,430,012 bytes; SHA256 `0295062cbc72da52ee804f39ac38694901a40458011f9b2638fc7ef13ed509da` |
| FBX discovery | RUN-PROVEN | 52 FBX in Warehouse #312; receipt hash verified |
| Old candidate ranking | REJECTED AS SEMANTICALLY UNSAFE | Substring collisions: Female→male and Soldier/Golden→old |
| Exact-token ranking repair | SOURCE-IMPLEMENTED | Filename-only tokens, identity filters, exclusions, bounded pools; PG-205 enforces the V2 state/order/policy |
| Frodo static FBX structure probe | SOURCE-IMPLEMENTED | Header/version plus Geometry/Model/LimbNode/Deformer/Skin/Cluster markers |
| UE4 skeletal import / deformation / likeness | NOT STARTED | Requires exact-head Unreal evidence and human visual review |
| READY_FOR_IMPORT / Runtime / Gate 6/7 | NOT ACCEPTED | P1C01 remains active; P1C02 remains predecessor-gated |



## 2026-10-02 - Warehouse #314 Frodo static-QC schema repair

| Area | Status | Evidence boundary |
|---|---|---|
| Candidate artifact schema | RUN-PROVEN | Warehouse #314 artifact: schema v2, `characters` array present, 5 Frodo / 4 Gandalf candidates |
| Frodo inspector crash | ROOT CAUSE ISOLATED | Strict property access failed before FBX marker inspection |
| Schema parser hardening | SOURCE-IMPLEMENTED | Current v2 + bounded legacy/flat compatibility; explicit unsupported-schema diagnostic |
| Regression fixture | SOURCE-IMPLEMENTED | Generated schema-v2 report is parsed by inspector self-test |
| Static FBX marker QC | PENDING FRESH RUN | Warehouse #314 failed before marker pass/fail could be trusted |
| UE4 import / deformation / likeness | NOT STARTED | Separate engine/human evidence required |


## 2026-10-02 - P1C01 priority CC0 audio provenance refresh

| Area | Status | Evidence boundary |
|---|---|---|
| Priority OpenGameArt audio pages | SOURCE-PROVENANCE RECORDED | 5/5 entries carry uploader, primary-page CC0 evidence and source file label |
| Download/hash evidence | PENDING | No receipt SHA256 claimed by this metadata update |
| Audio QC / WAV masters / UE import | PENDING | Separate intake and listening/import evidence required |
| Runtime / device / performance | NOT ACCEPTED | No experiential evidence created by this source metadata change |


## 2026-10-02 - Continuous Mega Wave Queue V2

| Area | Status | Evidence boundary |
|---|---|---|
| Mega production queue | SOURCE-IMPLEMENTED | 64 waves / 18,890 target work-items |
| P1C01 runtime waves | REGISTERED | 12 serialized runtime waves; Governor order remains authoritative |
| Global source waves | REGISTERED | 12 source-only acquisition families |
| Trilogy chapter packages | SOURCE-PREPARED | 23 chapter waves covering F1-01 through F3-07 |
| Future chapter runtime | FORBIDDEN BY QUEUE | Every future chapter row carries `runtime_integration_allowed=false` |
| Cross-cutting hardening | REGISTERED | 17 system/QA/streaming/performance waves |
| Project Manager traceability | REGISTERED | `PMREQ_CONTINUOUS_MEGA_WAVE_QUEUE_V2_2026_10_02` |
| Frodo static FBX structure | STATIC-VALIDATED | Warehouse #315: 5/5 allowlisted candidates, FBX v7400, skeleton/skin/cluster markers present |
| Frodo UE4 skeletal import / deformation / likeness | PENDING | Separate engine and human visual evidence still required |
| PIE / device / visual / performance acceptance | NOT ACCEPTED | Queue/source capacity does not create experiential evidence |

## 2026-10-02 - P1C01 visible-world mega source execution

| Area | Status | Evidence boundary |
|---|---|---|
| Bag End hero ring source priority | SOURCE-IMPLEMENTED | Materials/props/garden/fence support routed through existing warehouse-first pack; runtime/visual acceptance not implied |
| Hobbiton village source priority | SOURCE-IMPLEMENTED | Paths/fences/farm/social-prop/vegetation support prioritized; runtime/visual acceptance not implied |
| Shire road corridor source priority | SOURCE-IMPLEMENTED | Ground/path/hedge/tree/rock support prioritized; runtime/visual acceptance not implied |
| Bucklebury/Ferry source priority | SOURCE-IMPLEMENTED | Riverbank/wood/vegetation/transition support prioritized; runtime/visual acceptance not implied |
| Runtime mutation | NOT AUTHORIZED BY THIS PACK | PR #247 remains serialized Frodo runtime lane; P1C02+ runtime stays gated |
| Exact-head validation | PENDING | Pre-Unreal required before merge to develop |
| PIE / device / visual / performance acceptance | NOT ACCEPTED | Requires later matching runtime and human/device evidence |

## 2026-10-02 - Visible proxy replacement inventory

| Area | Status | Evidence boundary |
|---|---|---|
| Current Engine primitive fallbacks | STATIC-IDENTIFIED | Shire builder retains Cube/Sphere/Cylinder/Cone fallback paths |
| Bag End replacement routing | SOURCE-IMPLEMENTED | Existing production identities + missing interior/hero-detail source needs recorded |
| Hobbiton replacement routing | SOURCE-IMPLEMENTED | Existing village assets + remaining party/crop/log/clutter source needs recorded |
| Shire road replacement routing | SOURCE-IMPLEMENTED | Existing road/hedge/tree/rock assets + remaining road-edge/variation source needs recorded |
| Bucklebury/Ferry replacement routing | SOURCE-IMPLEMENTED | Riverbank/water exist; ferry/dock/mooring support remains source debt |
| Runtime replacement | NOT STARTED IN THIS BRANCH | Serialized runtime lane remains PR #247 |
| Exact-head static validation | PENDING | Pre-Unreal contract added |
| Visual/device/performance acceptance | NOT ACCEPTED | Requires later runtime and human/device evidence |

| Visible-world pack PG-187 compatibility | SOURCE-REPAIRED | Keep required `RUNNER_EXECUTION_READY` status; new priority carried by separate execution profile |

## 2026-10-02 - Visible-world reuse-first correction

| Area | Status | Evidence boundary |
|---|---|---|
| Ferry reusable production stock | STATIC-IDENTIFIED | River boat, footbridge, rope post/coil, reed cluster already present/imported |
| Road reusable production stock | STATIC-IDENTIFIED | Fallen log, broadleaf tree and boulder cluster already present/imported |
| New source acquisition | CONDITIONAL | Only after existing stock fails later composition/visual review |
| Runtime binding | NOT STARTED HERE | Serialized runtime lane remains separate |
| Visual/device/performance acceptance | NOT ACCEPTED | No matching evidence |

## 2026-10-02 - Visible-world exact resident binding packet

| Area | Status | Evidence boundary |
|---|---|---|
| Bucklebury/Ferry resident bindings | SOURCE-IMPLEMENTED | Exact production identities prepared for boat/footbridge/rope/reeds/boulder roles |
| Shire road resident bindings | SOURCE-IMPLEMENTED | Exact production identities prepared for fallen-log/tree/boulder/fence/woodpile/fern roles |
| New acquisition pressure | REDUCED | Existing production stock must be tried before new provider acquisition |
| Runtime mutation | NOT STARTED IN THIS PACKET | Serialized P1C01 runtime lane remains separate |
| PIE / device / visual / performance acceptance | NOT ACCEPTED | No matching runtime/human/device evidence |

## 2026-10-02 - P1C01 Ferry / Wooded Road visible-runtime replacement

| Area | Status | Evidence boundary |
|---|---|---|
| Wooded Road primitive obstacle | SOURCE-IMPLEMENTED | Resident fallen-log + boulder production meshes preferred; primitive fallback retained only if assets are not resident |
| Bucklebury/Ferry landing/body/posts/detail | SOURCE-IMPLEMENTED | Footbridge/river-boat/rope/reeds/boulder resident production meshes preferred |
| Heavy-asset loading policy | PRESERVED | Resident-only soft-path resolution; no synchronous heavy load added |
| Quest/NPC/LivingWorld authority | UNCHANGED | No parallel state or crowd owner introduced |
| Exact-head UE4 compile/runtime audit | PENDING | Required before merge |
| PIE / device / visual / target performance acceptance | NOT ACCEPTED | Human/device evidence still required |

## 2026-10-02 - Runner broker-stall recovery

| Area | Status | Evidence boundary |
|---|---|---|
| Listener process | OBSERVED ALIVE | Local screenshot showed Runner.Listener PID present |
| Worker process | OBSERVED ABSENT | No Runner.Worker process while Unreal jobs remained queued |
| Broker transport | OBSERVED FAILED | Runner log showed SocketException 995 / aborted I/O |
| Watchdog timestamp parser | ROOT CAUSE FIX SOURCE-IMPLEMENTED | Real `[yyyy-MM-dd HH:mm:ssZ INFO ...]` format now parsed; legacy form retained |
| Stalled acquire recovery | SOURCE-IMPLEMENTED | Existing ack-without-worker recycle can now receive a real AckUtc |
| Hosted regression | SOURCE-IMPLEMENTED | Pre-Unreal test covers real + legacy timestamp forms |
| Local machine recovery | PENDING USER-SIDE WATCHDOG REINSTALL/RESTART | No claim of runner recovery until a queued job starts |

| Runner manual recovery | RUN-PROVEN | Watchdog emitted `START` then `ONLINE ... brokerListening=true`; queued Unreal work resumed |
| Broker transport-stall auto-recovery | SOURCE-IMPLEMENTED | Bounded recycle when transport error remains newer than healthy broker evidence, no worker is active, and github.com:443 is reachable |
| Network outage behavior | SOURCE-IMPLEMENTED | Logs `NETWORK_BLOCKED`; avoids restart loop when GitHub control plane is unreachable |
| Runner auto-recovery exact-head validation | PENDING | Fresh Pre-Unreal + subsequent machine deployment/restart required |

| Runner PG-145 split-helper compatibility | SOURCE-FIXED | Validator now checks watchdog + timestamp helper as one contract; fresh exact-head Pre-Unreal pending |
| Runner maintenance UE queue isolation | SOURCE-FIXED | New helper/test paths are maintenance-safe and path-filtered off Unreal push/PR triggers |

## 2026-10-02 - P1C01 Party Field primitive-overlay suppression

| Area | Status | Evidence boundary |
|---|---|---|
| Party Field large cube centerpiece | SOURCE-IMPLEMENTED | Suppressed when resident `SM_ShPicnicCanopy` is available; deterministic fallback retained |
| Story / quest / NPC authority | UNCHANGED | No state or population ownership changes |
| Runtime loading | UNCHANGED | Existing resident mesh pointer reused; no synchronous heavy load added |
| Exact-head UE4 compile/runtime audit | PENDING | Required before merge |
| PIE / device / visual / performance acceptance | NOT ACCEPTED | No matching evidence |

| Party Field #1268 compile blocker | SOURCE-FIXED | Replaced undeclared `ProductionPicnicCanopyMesh` reference with shared resident `ProductionCommonMarketCanopyMesh`; exact-head UE4 build pending |

## 2026-10-02 - Maximum-safe CI lane reservation acceleration

| Area | Status | Evidence boundary |
|---|---|---|
| Hosted Unreal preflight classifier | SOURCE-IMPLEMENTED | Decides engine requirement before reserving UE4 machine |
| Source/preproduction fast lanes | SOURCE-IMPLEMENTED | East Fields plan, KayKit/alternate source registration and whole-game packets stay hosted/static when parent proof is valid |
| UE4 device lane reservation | SOURCE-IMPLEMENTED | Reserved only for full/core/asset/acceptance modes |
| Classifier regression coverage | SOURCE-IMPLEMENTED | New source-only cases added to test_unreal_classifier.ps1 |
| Exact-head static validation | PENDING | Fresh Pre-Unreal required before merge |
| Runtime / PIE / device / visual / performance acceptance | NOT ACCEPTED | No matching evidence |

| Hosted-classifier PG-145B reconciliation | SOURCE-FIXED | Validator recognizes hosted-preflight handoff while preserving runner-health-before-heavy-work invariant; fresh exact-head Pre-Unreal pending |

| Hosted classifier exact-base diff | SOURCE-FIXED | Full hosted history required before Unreal impact classification; source-only work must not fail-safe to UE solely because PR ancestry exceeds shallow depth |

| Hosted ancestor proof network avoidance | SOURCE-FIXED | Full local hosted history is consumed before any fallback fetch; private-repo credentials remain non-persistent and source-only UE reservations stay skipped |

## 2026-10-02 - East Fields row replacement plan

| Area | Status | Evidence boundary |
|---|---|---|
| Twelve cube crop-row strips | STATIC-IDENTIFIED | Current builder source |
| Instanced production-row replacement | SOURCE-IMPLEMENTED PLAN | <=1 cluster / <=96 instances / no collision / no Tick |
| Runtime implementation | PREDECESSOR-GATED | Wait for current Party Field runtime pass to merge green |
| New acquisition | NOT REQUIRED BY DEFAULT | Reuse resident production vegetation first |
| PIE / device / visual / performance acceptance | NOT ACCEPTED | No matching evidence |

| East Fields 12 cube crop strips | SOURCE-REPLACED | Dedicated builder-owned HISM path; primitive rows fallback-only |
| East Fields production row instances | SOURCE-IMPLEMENTED | 96 deterministic resident `SM_ShGrassClump` instances, no collision/no Tick/no shadow, cull 900-6500 cm |
| East Fields exact-head UE4 compile/runtime audit | PENDING | Requires fresh current-develop ancestry after source registration merges |
| East Fields PIE / device / visual / performance acceptance | NOT ACCEPTED | No matching human/device evidence |

## 2026-10-02 - KayKit Adventurers alternate Frodo source family

| Area | Status | Evidence boundary |
|---|---|---|
| KayKit Adventurers immutable source registration | SOURCE-IMPLEMENTED | Revision `672074b73ba276876a19e8816ecdc5241817ab47` |
| Character-intake admission | SOURCE-IMPLEMENTED | `KAYKIT_ADVENTURERS_CC0` added to external candidate manifest |
| Frodo static-QC source admission | SOURCE-IMPLEMENTED | Source asset ID allowlist updated |
| Warehouse staging / UE4 skeletal import | PENDING | Separate exact-head execution required |
| Runtime / deformation / visual acceptance | NOT ACCEPTED | No matching evidence |


## 2026-10-03 - KayKit Knight V2 technical probe

| Area | Status | Evidence boundary |
|---|---|---|
| Immutable candidate registration | SOURCE-IMPLEMENTED | KayKit revision `672074b73ba276876a19e8816ecdc5241817ab47`, `Knight.fbx` |
| Source blob identity | SOURCE-IMPLEMENTED | Git blob `101848795913dea0d37ac3ec9352fdf9dd024010` |
| Warehouse staging / payload SHA256 | PENDING | Must be produced by targeted staging |
| Static FBX skeletal QC | PENDING | Must pass before UE runner reservation |
| UE4.27.2 skeletal import | PENDING | Same smoothing/bind-pose/UV rejection gate as Rogue |
| Runtime / likeness / deformation / retarget | NOT AUTHORIZED | Technical probe only |


## 2026-10-03 - Closed-PR branch lifecycle enforcement

| Area | Status | Evidence boundary |
|---|---|---|
| Root cause | IDENTIFIED | Cleanup job previously skipped closed-unmerged PRs |
| Exact closed-head deletion | SOURCE-IMPLEMENTED | SHA-match + active-PR + canonical/protected guards retained |
| Existing stale branch retirement | SOURCE-IMPLEMENTED | 19 verified superseded/orphan refs queued in cleanup plan |
| Active PR protection | PRESERVED | Live open PR heads are excluded |
| Hosted validation | PENDING | Fresh exact-head Pre-Unreal/cleanup evidence required |


### 2026-10-03 - Branch lifecycle root-fix validation

| Area | Status | Evidence |
|---|---|---|
| Pre-Unreal #1671 | FAILED / DIAGNOSTIC | PG-167 caught stale merged-head contract |
| Workflow CLOSED_HEAD env | SOURCE-REPAIRED | exact close head + base/merge checkout distinction |
| PG-167 contract | SOURCE-REPAIRED | validates closed-PR lifecycle markers |
| Project Governor REQ-EXEC-002 | UPDATED | salvage/disposition-before-delete + live-ref audit rule |
| Fresh exact-head validation | PENDING | new run required before merge |

| Branch deletion active-PR safety recheck | SOURCE-HARDENED | Per-branch `head=owner:branch` API query before deletion; API failure blocks cleanup |


## 2026-10-03 - Branch cleanup batch continuation

| Area | Status | Evidence boundary |
|---|---|---|
| Branch Cleanup #138 | FAILED / DIAGNOSTIC | Active PR correctly protected; batch aborted |
| Active PR deletion behavior | SOURCE-REPAIRED | Keep + continue instead of abort |
| Canonical / moved-ref protection | PRESERVED | No relaxation |
| Exact-head validation | PENDING | Fresh Pre-Unreal required |


## 2026-10-03 - Empty active-PR query repair

| Area | Status | Evidence boundary |
|---|---|---|
| Empty REST response handling | SOURCE-REPAIRED | Null-filter + exact `head.ref` match |
| True active PR handling | PRESERVED | KEEP + CONTINUE |
| API failure behavior | PRESERVED | Fatal / fail-closed |
| Exact-head validation | PENDING | Fresh Pre-Unreal required |


## 2026-10-03 - Stale branch retirement wave 2

| Scope | Status | Evidence boundary |
|---|---|---|
| Additional disposed refs | 4 QUEUED | #268 head, #241, #246, #239 |
| Active PR heads | EXCLUDED | none of the four has an open PR |
| Cleanup execution | NOT STARTED | do not merge while #140 is running |
| Hosted validation | PENDING | fresh Pre-Unreal required |


## 2026-10-03 - Stale branch retirement wave 3

| Scope | Status | Evidence boundary |
|---|---|---|
| Closed maintenance refs | 3 QUEUED | #270, #272, #273 heads |
| Active PR heads | EXCLUDED | none of the three remains open |
| Production/runtime content | UNCHANGED | maintenance-only retirement |
| Hosted validation | PENDING | fresh Pre-Unreal required |


## 2026-10-03 - Final branch cleanup wave

| Area | Status | Evidence boundary |
|---|---|---|
| Live dead refs targeted | 4 | #270, #272, #273, #263 heads |
| Active delete queue | COMPACTED 95 -> 4 | historical absent refs removed from execution queue |
| Active PR heads | EXCLUDED | none of the four targets is open |
| #263 runtime authority | SUPERSEDED | exact replacement support still import/QC pending; #267 remains bounded writer |
| Exact-head validation | PENDING | fresh Pre-Unreal required |


## 2026-10-03 - Final branch hygiene closeout

| Live-ref class | Count | Status |
|---|---:|---|
| Canonical/recovery | 3 | PRESERVED |
| Open PR heads | 9 | ACTIVE / PRESERVED |
| Explicit pending salvage | 3 | UNIQUE CONTENT / PRESERVED |
| Unexplained dead refs | 0 | CLEAN |
| Active delete queue | 0 | COMPACTED |


## 2026-10-03 - Bag End planted-entry shrub runtime refresh

| Area | Status | Evidence boundary |
|---|---|---|
| Runtime writer | ACTIVE / SINGLE | fresh branch from `94ecdd6da09b4dbf9acc7ec7b99d18c696c64863` |
| Entry sphere shrubs | SOURCE-REPLACED | resident `SM_ShShrub`; sphere remains no-asset fallback |
| Actor / Tick / collision budget | UNCHANGED | two existing placements; no Tick/collision added |
| Door/window/trim debt | PRESERVED | exact replacement remains import/QC gated |
| Fresh exact-head Pre-Unreal | PENDING | new head required |
| Fresh UE4.27.2 compile/build | PENDING | old #1305 does not validate refreshed head |

## 2026-10-03 - Hosted classifier current-tree proof refresh

| Area | Status | Evidence boundary |
|---|---|---|
| Local parent-object probe | SOURCE-IMPLEMENTED | fetch only if local object absent |
| Bag End source packet allowlist | EXACT-PATH ONLY | no broad Data wildcard |
| Parent tree evidence | AVAILABLE | `82d5...` vs `6e1b...`: zero file delta |
| Prior engine proof | AVAILABLE | #277 Unreal Build #1310 SUCCESS on `6e1b...` |
| Fresh classifier validation | PENDING | exact current head required |

| Transitive governance ancestor proof | SOURCE-IMPLEMENTED | safe delta + direct green OR exact tree-equivalent core proof |
| Broad safety relaxation | NONE | existing safe-file and tree-equality requirements preserved |
| Fresh hosted validation | PENDING | exact-head Pre-Unreal required |

## 2026-10-03 - Bag End hero trim source probe V3

| Gate | Status |
|---|---|
| Current ancestry | `develop@071a0ed2632c4919ed9160b817a965ed3b1eb76c` |
| Runtime integration | BLOCKED / false |
| Exact modular FBX discovery | PENDING |
| Immutable receipt/SHA256 | PENDING |
| Static FBX UV/material/perf QC | PENDING |
| Real UE4.27.2 static-mesh import | BLOCKED UNTIL STATIC GATES |
| Visual acceptance | NOT CLAIMED |

## 2026-10-03 - Bag End hero trim exact-file gate

| Gate | Status | Evidence |
|---|---|---|
| Provider/license family | COMPLETE | official Kenney Building Kit / CC0 |
| Exact FBX filenames | COMPLETE | round door/doorway/window candidates identified |
| Discovery payload identities | COMPLETE-DISCOVERY | Git-LFS SHA256 + byte size pinned to mirror revision |
| Official Kenney archive receipt | PENDING | production provenance not yet captured |
| Binary static FBX QC | PENDING | no binary payload available in current execution environment |
| UE4.27.2 import | BLOCKED | requires official receipt + static QC |
| Runtime replacement | BLOCKED | exact import/QC evidence required first |


## 2026-10-03 - Bag End hero trim source receipt progression

| Gate | Status | Evidence boundary |
|---|---|---|
| Official provider page | RESOLVED | Kenney Building Kit / CC0 / 80 files |
| Official direct ZIP URL | RESOLVED | recorded in `P1C01BagEndHeroTrimSourceProbeV1.json` |
| Archive SHA256 + byte size | PENDING | warehouse receipt required |
| Extracted candidate hash match | PENDING | must match discovery identities |
| Static FBX QC / UE4.27.2 import | PENDING | no promotion/runtime binding yet |


## 2026-10-03 - Interactive launcher / runner-root isolation

| Control | Status | Evidence boundary |
|---|---|---|
| Retired C-runner message | REMOVED | launcher no longer names `C:\\actions-runner` as active authority |
| Runner-root interactive guard | STRENGTHENED | rejects any `\\actions-runner\\` project root independent of drive letter |
| Active self-hosted authority | UNCHANGED | `D:\\actions-runner` remains CI-only |
| Manual Unreal clone | UNCHANGED | Documents developer clone only |


## 2026-10-03 - Stale open source/preproduction reconciliation

| Salvaged lane | Current ancestry disposition | Runtime boundary |
|---|---|---|
| 23 chapter production packets + asset demand matrix | SELECTIVELY SALVAGED | all rows runtime=false |
| P1C01 Shire mega chapter pack | SELECTIVELY SALVAGED | source/preproduction only |
| P1C01 180-slot visual mega wave | SELECTIVELY SALVAGED | candidate discovery only; provenance/QC required |
| Daily manager report generator/test | SELECTIVELY SALVAGED | informational tooling only |
| Old branch-local docs/workflow snapshots | NOT COPIED | current develop remains authority |
| Fresh exact-head Pre-Unreal | PENDING | required before merge |


## 2026-10-03 - Static FBX world intake reconciliation

| Area | Status | Evidence boundary |
|---|---|---|
| Static world/prop FBX discovery/import | SOURCE-IMPLEMENTED | latest develop ancestry |
| Characters/Rigs FBX | DEFERRED | dedicated skeletal QC lane |
| Auto animation/material/texture import | DISABLED | deterministic bounded static intake |
| Synchronous heavy LoadObject in FBX branch | GUARDED FORBIDDEN | hosted source contract |
| Fresh UE4.27.2 compile | PENDING | required before merge |
| PIE/device/visual/performance | NOT CLAIMED | separate gates |


## 2026-10-03 - P1C01 garden visual replacement

| Item | Status | Evidence boundary |
|---|---|---|
| Garden soil rows | production ground mesh preferred | source implemented |
| Garden plants | existing shrub HISM, max 125 added instances | source implemented |
| Primitive plant actors | fallback-only when production binding unavailable | source implemented |
| Actor/Tick growth | none; production path reduces per-plant actors | source inspection |
| Exact-head UE4.27.2 validation | PENDING | required before merge |
| PIE/device/visual/performance | NOT CLAIMED | separate acceptance gates |


## 2026-10-03 - Visible-game delivery authority

| Direction | Status |
|---|---|
| Visible Shire first | ACTIVE AUTHORITY |
| Frodo first real skeletal character | ACTIVE AUTHORITY |
| One P1C01 runtime writer | REQUIRED |
| UE5 migration / Nanite / MetaHuman Crowd / UE5 PCG | NOT CURRENT STACK |
| Proposal adoption | VERIFY AGAINST LIVE DEVELOP + PROJECT SOURCES |
| Durable repository memory | REQUIRED FOR EVERY ACCEPTED MAJOR DIRECTION |


## 2026-10-03 - Frodo real-rig lane current-ancestry reconciliation

| Item | Status | Evidence boundary |
|---|---|---|
| Opt-in UE4.27 skeletal FBX importer | SOURCE-IMPLEMENTED | exact-head build pending |
| Direct FBX character staging | SOURCE-IMPLEMENTED | hosted contract pending |
| Default character FBX behavior | DEFERRED unless explicit flag | preserved |
| Nonzero skeleton/bone proof | IMPLEMENTED in import commandlet | candidate run pending |
| Frodo deformation/retarget/AnimBP/runtime | NOT STARTED | requires clean technical candidate |


## 2026-10-03 - CI build-speed lane split

| Change class | Generic UE4 runner |
|---|---|
| Bag End hosted official receipt source-only delta | INHERIT/SKIP |
| Frodo dedicated probe metadata/workflow-only delta | INHERIT/SKIP |
| Runtime C++ / SourceAssets / engine config | REQUIRED |
| Dedicated Frodo skeletal technical probe | OWN UE4 WORKFLOW REQUIRED |


## 2026-10-03 - Bag End hero trim source receipt completion

| Gate | Status |
|---|---|
| Official archive SHA256/size | PASS |
| Exact door/frame/window payload identity | PASS |
| Expected colormap payload identity | PASS |
| Binary static FBX QC | NEXT |
| UE4.27.2 static import | PENDING |
| Runtime hero trim replacement | BLOCKED UNTIL IMPORT/QC |


## 2026-10-03 - Bag End trim static QC

| Gate | Status |
|---|---|
| Official exact payload receipt | PASS |
| Hosted FBX static structure QC | ACTIVE |
| UE4.27.2 import | PENDING |
| Runtime replacement | PENDING |


## 2026-10-03 - Bag End trim static QC result

| Candidate | Static result |
|---|---|
| Kenney Building Kit round door | REJECTED: FBX 7700 |
| UE4 self-hosted import | NOT SCHEDULED for rejected payload |
| Next | compatible export/source family |


## 2026-10-03 - Next Frodo candidate source lane

| Gate | Status |
|---|---|
| Distinct CC0 humanoid source | REGISTERED |
| Hosted archive/FBX inventory | ACTIVE |
| UE4 runner reservation | BLOCKED UNTIL HOSTED STATIC PASS |
| Final Frodo likeness/runtime | NOT CLAIMED |


## 2026-10-03 - Frodo rejected-payload guard reconciled on current develop

| Control | Status |
|---|---|
| Exact rejected payload hashes | DURABLY RECORDED |
| Knight V2 UE4 skeletal registration | PASS, 51 bones |
| Knight V2 smoothing groups | FAIL |
| Knight V2 bind pose | FAIL |
| Retry same exact payload | FORBIDDEN |
| Distinct OGA Lowpoly Dummy family | SOURCE INVENTORY PASS ONLY; UE4 TECHNICAL PROBE NEXT |


## 2026-10-03 - P1C01 visible Shire mega pass

| Gate | Status |
|---|---|
| World-detail ledger registration | COMPLETE |
| Runtime HISM mega-pass source | IMPLEMENTED |
| Bag End/Hobbiton hedge enclosure | IMPLEMENTED IN SOURCE |
| Field boundaries / shelterbelts | IMPLEMENTED IN SOURCE |
| Wooded-road layered vegetation | IMPLEMENTED IN SOURCE |
| Ferry-bank reeds / approach framing | IMPLEMENTED IN SOURCE |
| New synchronous heavy loading | NONE ADDED |
| New NPC lifecycle owner | NONE; LivingWorldDirector remains authoritative |
| Exact-head Pre-Unreal | PENDING |
| Exact-head UE4.27.2 build | PENDING |
| PIE/device/rendered visual/FPS acceptance | NOT CLAIMED |


## 2026-10-03 - Frodo OGA Lowpoly Dummy technical result

| Gate | Status |
|---|---|
| Exact CC0 archive receipt | PASS |
| Exact Idle FBX identity | PASS: `00177d777d324e2eb807f5f94b573026c94226c6574267900213863a0dc8014d` |
| FBX version | PASS: 7400 |
| UE4.27 skeletal registration | PASS |
| Reference bone count | PASS: 41 |
| Smoothing-group gate | FAIL |
| Bind-pose gate | FAIL |
| Technical candidate | REJECTED |
| Retry same payload | FORBIDDEN |
| Deformation / retarget / AnimBP | BLOCKED |
| Runtime Frodo promotion | BLOCKED |


## 2026-10-03 - P1C01 natural route mega pass

| Gate / Visible Domain | Status |
|---|---|
| Strategy | MAXIMUM-SAFE VERTICAL-SLICE GROWTH |
| Runtime chapter | P1C01 ONLY |
| Runtime writer | AShirePrototypeWorldBuilder |
| Bag End -> Hobbiton route breakup | IMPLEMENTED IN SOURCE |
| Worked-field verge / horizon breakup | IMPLEMENTED IN SOURCE |
| Wooded-road enclosure | IMPLEMENTED IN SOURCE |
| Ferry river-edge density | IMPLEMENTED IN SOURCE |
| Additional repeated detail budget | UP TO 1,758 HISM INSTANCES |
| New synchronous heavy loads | NONE |
| New per-instance Tick | NONE |
| New NPC lifecycle owner | NONE |
| P1C02 runtime expansion | NOT OPENED |
| Exact-head Pre-Unreal | PENDING |
| Exact-head UE4.27.2 validation | PENDING |
| PIE/device/rendered visual/FPS acceptance | NOT CLAIMED |


## 2026-10-04 - Lead engineering delivery method

| Control | Status |
|---|---|
| Professional lead method stored in Governor | IMPLEMENTED IN GOVERNANCE BRANCH |
| Routine technical decisions owned by Lead Architect | ENABLED WITH CANON/PROVENANCE/PERF/GATE BOUNDARIES |
| Root-cause blocker research loop | REQUIRED |
| Official UE4.27 + mature OSS/expert evidence review | REQUIRED FOR NONTRIVIAL BLOCKERS |
| Broad legal/open asset discovery | REQUIRED WHEN CURRENT SOURCE IS INSUFFICIENT |
| Repairable FBX export normalization path | AUTHORIZED WITH PROVENANCE + STRICT RE-VALIDATION |
| Large coherent visible production packets | DEFAULT |
| Avoidable micro-commit / superseded-CI churn | PROCESS DEFECT TO REDUCE |
| Visible Shire + human characters | PRIMARY DELIVERY TARGET |
| Low-spec DX11 / 720p / 30 FPS architecture constraints | UNCHANGED |
| PIE/device/visual/FPS claims without direct evidence | FORBIDDEN |

## 2026-10-04 - Authored Shire mega wave B

| Visible domain | Status | Evidence boundary |
|---|---|---|
| World-detail ledger registration | COMPLETE BEFORE CODE | P1C01 AUTHORED_SHIRE_MEGA_WAVE_B |
| Runtime writer | PRESERVED | AShirePrototypeWorldBuilder only |
| Bag End earth/hill framing | SOURCE-IMPLEMENTED | 4 resident HISM landform placements |
| Hobbiton terrain terraces | SOURCE-IMPLEMENTED | 8 resident HISM slope placements |
| Worked-field outer ridges | SOURCE-IMPLEMENTED | 6 resident HISM hill placements |
| Wooded-road enclosure shoulders | SOURCE-IMPLEMENTED | 8 resident HISM slope placements |
| Ferry near/far bank framing | SOURCE-IMPLEMENTED | 8 resident HISM river-bank placements |
| Ferry final-approach stones | SOURCE-IMPLEMENTED | 18 non-collision production HISM instances |
| New synchronous heavy loading | NONE ADDED | resident meshes only |
| New per-instance Tick | NONE | existing HISM architecture |
| P1C02 runtime expansion | NOT OPENED | visual P1C01 only |
| Exact-head Pre-Unreal | PENDING | branch validation required |
| Exact-head UE4.27.2 build | PENDING | branch validation required |
| PIE/device/visual/pacing/FPS | NOT ACCEPTED | direct evidence still required |

## 2026-10-04 - Presentation composition wave C

| Area | Status | Evidence boundary |
|---|---|---|
| Wave C ledger registration | COMPLETE BEFORE CODE | presentation/material/vegetation rules captured |
| Cultivated Bag End/Hobbiton foreground | SOURCE-IMPLEMENTED | 28 shrub HISM instances |
| Wooded-road threshold canopy | SOURCE-IMPLEMENTED | 20 broadleaf HISM instances |
| Wooded-road understory | SOURCE-IMPLEMENTED | 40 fern HISM instances |
| Ferry-bank vegetation framing | SOURCE-IMPLEMENTED | 32 reed HISM instances |
| Imported material preservation | PRESERVED | no production-mesh color MID override |
| Morning light/fog/exposure refinement | SOURCE-IMPLEMENTED | existing low-cost actors/settings only |
| Volumetric fog | DISABLED | low-spec policy preserved |
| Planar reflection / scene capture | NONE | low-cost water path preserved |
| External PBR intake | NOT REQUIRED YET | only after visual review proves gap |
| Exact-head Pre-Unreal / UE4 build | PENDING | branch not opened for validation yet |
| PIE/device/visual/FPS | NOT ACCEPTED | direct evidence required |

| Authored Shire B/C source regression guard | SOURCE-IMPLEMENTED | `test_source_contracts.py`; locks budgets, call order, no-sync-load, no duplicate authority and P1C01-only boundary |

## 2026-10-04 - Hobbit facade production cleanup

| Area | Status | Evidence boundary |
|---|---|---|
| Hobbit facade geometry grouping | STATIC-AUDITED | 228 faces; no mixed face groups |
| Authored material assignment | SOURCE-REPAIRED | Earth 12 / Wood door 48 / DoorGreen 48 / Wood windows 96 / Stone sills 24 faces |
| Production duplicate primitive door/frame/sills | SOURCE-REMOVED | fallback-only when production facade unavailable |
| Warm glass / knob / chimney-step accents | RETAINED BOUNDED | non-structural presentation accents |
| UE4.27 static import/build | PENDING EXACT-HEAD | PR validation required |
| PIE/device/rendered visual/FPS | NOT ACCEPTED | direct evidence required |

| Authored Shire B/C P1C02 guard false-positive | TEST-REPAIRED / REVALIDATION PENDING | #1817 failed on prose comment only; guard now targets `TEXT("P1C02")` runtime token |

## 2026-10-04 - Hobbit facade production cleanup

| Area | Status | Evidence boundary |
|---|---|---|
| Hobbit facade geometry grouping | STATIC-AUDITED | 228 faces; no mixed face groups |
| Authored material assignment | SOURCE-REPAIRED | Earth 12 / Wood door 48 / DoorGreen 48 / Wood windows 96 / Stone sills 24 faces |
| Production duplicate primitive door/frame/sills | SOURCE-REMOVED | fallback-only when production facade unavailable |
| Warm glass / knob / chimney-step accents | RETAINED BOUNDED | non-structural presentation accents |
| UE4.27 static import/build | PENDING EXACT-HEAD | PR validation required |
| PIE/device/rendered visual/FPS | NOT ACCEPTED | direct evidence required |

## 2026-10-04 - KayKit rig technical bridge

| Area | Status | Evidence boundary |
|---|---|---|
| Ledger registration before code | COMPLETE | P1C01 KAYKIT_RIG_TECHNICAL_BRIDGE |
| Source | AUTHORIZED | KayKit official GitHub, CC0 |
| Final Frodo likeness | NOT CLAIMED | technical bridge only |
| Candidate budget | LOCKED | max 2 UE4 probes |
| Hosted direct-source/license/hash gate | SOURCE-IMPLEMENTED | exact GitHub URLs + CC0 + SHA256 |
| ZIP/path/size safety | SOURCE-IMPLEMENTED | bounded extraction |
| FBX static rig markers | SOURCE-IMPLEMENTED | version/Geometry/Model/LimbNode/Skin/Cluster/animation |
| UE4 skeletal hard gate | SOURCE-IMPLEMENTED | registration/bones/assets + smoothing/bind/UV rejects |
| Runtime hard reference | NONE ADDED | modular Frodo fallback preserved |
| Sync heavy runtime load | NONE ADDED | later integration remains soft/async |
| Deformation / locomotion / AnimBP | BLOCKED | clean technical winner required |
| Exact-head Pre-Unreal / UE4 | PENDING | PR validation required |
| PIE/device/rendered visual/FPS | NOT ACCEPTED | direct evidence required |

| KayKit bridge source-contract regression guard | SOURCE-IMPLEMENTED | `test_source_contracts.py`; locks CC0/direct-source, max-two budget, hard rejection reasons and non-runtime boundary |

## 2026-10-04 - KayKit hosted path-filter correction

| Check | Status | Evidence boundary |
|---|---|---|
| Official KayKit archive download | REACHED | run #1 progressed to archive scan |
| Preferred FBX discovery | TOOLING-FAILED BEFORE CANDIDATE QC | path selector returned zero |
| Root-cause correction | SOURCE-IMPLEMENTED | lowercase normalized archive path + explicit leaf split |
| KayKit asset technical disposition | UNCHANGED / UNTESTED | no FBX was judged by run #1 |
| Exact-head hosted/UE4 rerun | PENDING | corrected head required |

## 2026-10-04 - KayKit character discovery hardening

| Check | Status | Evidence boundary |
|---|---|---|
| KayKit rerun #4 candidate judgment | NOT REACHED | discovery failed before FBX static QC |
| Character FBX discovery | SOURCE-HARDENED | all `/Characters/*.fbx` first, ranking second |
| Preferred candidate order | PRESERVED | Rogue -> RogueHooded -> Mage -> Barbarian -> Knight |
| Fallback ranking | BOUNDED | smallest static-pass character FBX only |
| UE4 probe cap | UNCHANGED | max 2 |
| Exact-head rerun | PENDING | corrected head required |

## 2026-10-04 - KayKit direct raw FBX source correction

| Check | Status | Evidence boundary |
|---|---|---|
| GitHub source ZIP FBX availability | PROVEN ABSENT | repository `.gitattributes` export-ignore for FBX directories |
| Root cause | PROVEN | hosted run #8 + official `.gitattributes` |
| Source delivery | SOURCE-CORRECTED | exact official raw `Rogue.fbx` + `RogueHooded.fbx` |
| License snapshot | REQUIRED | official raw CC0 LICENSE.txt |
| Raw source allowlist | SOURCE-IMPLEMENTED | exact KayKit repository prefix only |
| Candidate format | FBX ONLY | max 2 |
| Exact payload SHA256/static QC | PENDING RERUN | hosted gate |
| UE4 technical gate | PENDING | no candidate judgment yet |
| Deformation / runtime / PIE / device / visual / FPS | BLOCKED / NOT ACCEPTED | technical winner required first |

## 2026-10-04 - KayKit exact technical result / runner anti-churn

| Check | Status | Evidence boundary |
|---|---|---|
| Prior exact head | COMPILE-TESTED | `30b0392aa9abe5223d6adfe0958c93cd9cf28631`; Pre-Unreal #1836 SUCCESS + Unreal Build #1433 SUCCESS |
| Rogue raw FBX | REJECTED TECHNICAL | 48 bones; MISSING_BIND_POSE_BONES + MISSING_SMOOTHING_GROUPS |
| RogueHooded raw FBX | REJECTED TECHNICAL | 48 bones; MISSING_BIND_POSE_BONES + MISSING_SMOOTHING_GROUPS |
| Same exact payload retry | FORBIDDEN / AUTOMATICALLY EXCLUDED | known SHA256 registry |
| Direct-raw receipt schema bug | SOURCE-FIXED | obsolete `archive_sha256` reference removed |
| Known-rejection-only hosted result | SOURCE-IMPLEMENTED | controlled `STATIC_BRIDGE_EXHAUSTED_KNOWN_REJECTIONS` |
| Self-hosted UE4 reservation on zero new candidates | SOURCE-BLOCKED | job-level selected_count gate |
| Modular Frodo fallback | PRESERVED | no failed candidate runtime promotion |
| Deformation / AnimBP | BLOCKED | no clean technical candidate |
| New exact-head Pre-Unreal | PENDING | anti-churn packet revalidation |
| New exact-head Unreal build | PENDING ONLY IF CI CLASSIFIER REQUIRES | no runtime C++/asset change in this packet |
| PIE/device/rendered visual/FPS | NOT ACCEPTED | no matching evidence |
| KayKit anti-churn source-contract import error | TOOLING-FIXED / REVALIDATION PENDING | #1837 IndentationError only; existing class method declaration indentation restored |

## 2026-10-04 - P1C01 Visible Shire Mega Wave D

| Visible domain | Status | Evidence boundary |
|---|---|---|
| Ledger registration before code | COMPLETE | P1C01 VISIBLE_SHIRE_MEGA_WAVE_D |
| Runtime writer | PRESERVED | AShirePrototypeWorldBuilder only |
| Bag End hero composition | SOURCE-IMPLEMENTED | 52 HISM instances |
| Hobbiton settlement depth | SOURCE-IMPLEMENTED | 48 HISM instances |
| Worked-field edge rhythm | SOURCE-IMPLEMENTED | 42 HISM instances |
| Wooded-road enclosure | SOURCE-IMPLEMENTED | 64 HISM instances |
| Ferry authored framing | SOURCE-IMPLEMENTED | 62 HISM instances |
| Ferry limited hero landmarks | SOURCE-IMPLEMENTED | 12 actors: landing/boat/rope/lamp silhouettes |
| Repeated horizon cleanup | SOURCE-IMPLEMENTED | deterministic multi-frequency tree-line offsets |
| New world authority | NONE | existing writer preserved |
| New synchronous heavy load | NONE | resident meshes only |
| New per-instance Tick | NONE | HISM/ISM architecture |
| Actor-per-prop density wave | NONE | only 12 bounded Ferry hero actors |
| P1C02 runtime expansion | NOT OPENED | P1C01 visual scope only |
| Static source regression | SOURCE-IMPLEMENTED | budget/authority/order/no-sync-load guard |
| Exact-head Pre-Unreal | PENDING | PR validation required |
| Exact-head UE4.27.2 build | PENDING | PR validation required |
| PIE visual/pacing/device/FPS | NOT ACCEPTED | direct evidence still required |


## 2026-10-04 - P1C01 Shire Visual Finish Wave

| Visible domain | Status | Evidence boundary |
|---|---|---|
| Ledger registration before code | COMPLETE | P1C01 SHIRE_VISUAL_FINISH_WAVE |
| Runtime writer | PRESERVED | AShirePrototypeWorldBuilder only |
| Terrain silhouette refinement | SOURCE-IMPLEMENTED | 16 HISM route shoulders |
| Bag End final framing | SOURCE-IMPLEMENTED | 40 HISM placements |
| Hobbiton property identity | SOURCE-IMPLEMENTED | 24 HISM placements |
| Road/verge breakup | SOURCE-IMPLEMENTED | 40 HISM placements |
| Woodland layering | SOURCE-IMPLEMENTED | 48 HISM placements |
| Ferry final framing | SOURCE-IMPLEMENTED | 44 HISM placements + 4 bounded hero actors |
| New texture/material memory | NONE | geometry/verge breakup only |
| New world authority | NONE | existing writer preserved |
| New synchronous heavy load | NONE | resident meshes/components only |
| New per-instance Tick | NONE | HISM architecture |
| P1C02 runtime expansion | NOT OPENED | P1C01 only |
| Exact-head Pre-Unreal | PENDING | PR validation required |
| Exact-head UE4.27.2 build | PENDING | PR validation required |
| PIE visual/pacing/device/FPS | NOT ACCEPTED | direct evidence required |


## 2026-10-04 - Human Character Production Wave 2

| Gate | Status | Evidence boundary |
|---|---|---|
| New source family | SOURCE-REGISTERED | OpenGameArt Character Base Model / CC0 |
| Source page + archive provenance | SOURCE-IMPLEMENTED | page + archive SHA256 captured by hosted factory |
| Animated final format | FBX ONLY | .blend permitted only as hosted authoring intermediate |
| Blender normalization | SOURCE-IMPLEMENTED | smoothing/armature/animation bake + exact normalized SHA |
| Hosted deformation readiness | SOURCE-IMPLEMENTED | bones/weights/UV/bounds/joint-name coverage; not visual acceptance |
| Self-hosted candidate budget | LOCKED | max 2 |
| UE4 registration/bones/smoothing/bind/UV gate | SOURCE-IMPLEMENTED | unchanged hard rejects |
| Technical winner | PENDING | exact-head run required |
| Deformation visual acceptance | BLOCKED | clean technical winner first |
| Idle/Walk/Run retarget | BLOCKED | clean deformation readiness first |
| AnimBP | BLOCKED | locomotion proof first |
| Runtime Frodo promotion | BLOCKED | soft/async only after all gates |
| Modular fallback | PRESERVED | current runtime remains safe |
| PIE/device/rendered visual/FPS | NOT ACCEPTED | direct evidence required |

## 2026-10-04 - Human Wave 2 deform-only + runner dedup

| Gate | Status | Evidence boundary |
|---|---|---|
| Hosted source factory baseline | PASS | run #1 on `8afa53cdee648cef196b914c5123d3e38677fc2c`; archive/provenance + Blender artifact captured |
| Baseline preferred source | NEEDS NORMALIZATION ROOT FIX | 443 total bones; 1,787 weighted / 442 zero-weight |
| Baseline direct-FBX source | HOSTED QUALITY REJECT TARGET | 656 total bones; 24 weighted / 2,205 zero-weight |
| Rigify control/mechanism bones | PROVEN PRESENT | ORG/MCH/DEF strings in normalized artifact |
| Deform-only FBX export | SOURCE-IMPLEMENTED | `use_armature_deform_only=True`; leaf bones off |
| Deform-bone count receipt | SOURCE-IMPLEMENTED | hosted readiness JSON |
| Zero-weight ratio pre-UE4 gate | SOURCE-IMPLEMENTED | maximum 0.35 |
| Duplicate generic Unreal runner reservation | SOURCE-FIXED | Wave2-only delta classifies `inherit`; dedicated job owns Editor build + UE4 gate |
| Fresh hosted normalization | PENDING | new exact head required |
| UE4 skeletal technical winner | PENDING | unchanged hard gates |
| Deformation / locomotion / AnimBP | BLOCKED | clean technical winner required |
| Runtime Frodo promotion | BLOCKED | existing soft/async subsystem only after all gates |
| PIE/device/rendered visual/FPS | NOT ACCEPTED | direct evidence required |


## 2026-10-04 - Human Wave 2 linked USkeleton probe correction

| Gate | Status | Evidence boundary |
|---|---|---|
| Rebase onto current develop | COMPLETE | base `3d0990bec48be182b291e266d321408c5d9ea034` |
| Prior skeletal registration | EVIDENCED / NOT YET WINNER | run #2: registered, 161 reference bones |
| Prior smoothing/bind/UV warning gate | CLEAN IN RUN #2 | no matching hard-warning reasons reported |
| Skeletal mesh package | EVIDENCED | `SK_FRODO.uasset` existed |
| Linked USkeleton probe | SOURCE-FIXED | authoritative `USkeletalMesh::GetSkeleton()` path |
| Guessed skeleton filename requirement | REMOVED | no `SK_FRODO_Skeleton.uasset` hard dependency |
| PhysicsAsset | SEPARATE SANITY | not hard import failure; capsule owns runtime collision |
| Fresh exact-head hosted + UE4 gate | PENDING | new SHA required |
| Deformation / retarget / AnimBP | BLOCKED | clean technical winner first |
| PIE/device/rendered visual/FPS | NOT ACCEPTED | direct evidence required |

## 2026-10-04 - Human Wave 2 technical winner

| Gate | Status | Evidence boundary |
|---|---|---|
| Exact-head Wave2 run #3 | SUCCESS | `c0ad882792ccef8c9e639e4eb1d7c3e9e6ce5e90` |
| Normalized winner | TECHNICAL PASS | `eff0e79980f90d49deada0aa37ad8be5975a86330348e4ae6fa49d3171fad570` |
| Skeletal registration | PASS | yes |
| Reference bones | PASS | 161 |
| Linked USkeleton | PASS | `/Game/Production/Characters/Rigs/FRODO/SK_FRODO_Skeleton.SK_FRODO_Skeleton` |
| Import batch | PASS | 377 files / 0 failures |
| Smoothing / bind / UV hard gates | PASS | no matching rejection reasons |
| PhysicsAsset | SEPARATE SANITY | small-bone auto-generation warning; not skeletal rejection |
| Dedicated trigger includes commandlet | SOURCE-HARDENED / EXACT-HEAD PENDING | prevents commandlet-only probe drift |
| Transient cleanup | SOURCE-HARDENED / EXACT-HEAD PENDING | generated untracked Frodo uassets only |
| Deformation + retarget | NEXT | technical predecessor now satisfied |
| AnimBP / runtime promotion | BLOCKED | deformation/retarget evidence required first |
| PIE/device/rendered visual/FPS | NOT ACCEPTED | no direct evidence |


## 2026-10-04 - P1C01 Shire Settlement Completion Mega Packet

| Settlement area | Status | Evidence boundary |
|---|---|---|
| Runtime writer | PRESERVED | `AShirePrototypeWorldBuilder` only |
| Bagshot Row visual smials | SOURCE-IMPLEMENTED | 8 turf/facade pairs; visual clusters only |
| Hobbiton property boundaries | SOURCE-IMPLEMENTED | hedge + fence HISM completion |
| Domestic gardens / mail / laundry | SOURCE-IMPLEMENTED | garden arches, flower boxes, mailboxes, wash lines, shrubs |
| Village lanes / verge breakup | SOURCE-IMPLEMENTED | path-stone + grass HISM |
| Village common / market | SOURCE-IMPLEMENTED | market stalls, produce stands, wells, benches |
| Party Field completion | SOURCE-IMPLEMENTED | 8 production picnic-table instances; existing Party Tree retained |
| Orchard / farm work | SOURCE-IMPLEMENTED | 12 orchard trees + hay/plough/gate/ladder detail |
| Water / mill landmark | SOURCE-IMPLEMENTED | bounded mill-wheel accent; existing mill/bridge preserved |
| Lived-in clutter | SOURCE-IMPLEMENTED | barrels, crates, carts, loaded carts, lamps, signs |
| Native HISM budget | 160 | existing components, explicit culling |
| WorldDetailCluster instance budget | 185 | <=24 bounded cluster actors, no collision, zero Tick |
| New per-prop actor density | NONE | cluster/HISM only |
| New synchronous heavy load | NONE | resident production meshes only |
| Population / NPC / quest authority | UNCHANGED | LivingWorldDirector / NPCContext / QuestSubsystem |
| P1C02 runtime | NOT OPENED | P1C01 only |
| Exact-head Pre-Unreal / UE4 compile | PENDING | PR validation required |
| PIE visual walkthrough | NOT ACCEPTED | direct human evidence required |
| Target-device 720p / 30 FPS | NOT ACCEPTED | measured device evidence required |


## 2026-10-04 - P1C01 Shire Settlement Canon Finish B

| Settlement canon detail | Status | Evidence boundary |
|---|---|---|
| #314 predecessor | COMPILE-TESTED / MERGED | head `3ee80ffe...`; Pre #1849 + Unreal #1446 SUCCESS; merge `b3f31134...` |
| Ivy Bush roadside inn identity | SOURCE-IMPLEMENTED | bounded cottage + clustered sign/bench/barrels |
| Number 3 Bagshot Row | SOURCE-IMPLEMENTED | visual turf/facade/mailbox anchor; quest anchors unchanged |
| Party special entrance | SOURCE-IMPLEMENTED | 10 HISM step stones + setup/celebration gate variants |
| Party open-air kitchen | SOURCE-IMPLEMENTED | cooking stand + table + canopy in setup/celebration state arrays |
| Mill yard work detail | SOURCE-IMPLEMENTED | 12 clustered sacks/crates/barrels |
| Bywater-road avenue | SOURCE-IMPLEMENTED | 12 trunk + 12 canopy cluster instances |
| Green Dragon in Hobbiton | FORBIDDEN / NOT PLACED | canonical Bywater ownership preserved |
| New synchronous heavy load | NONE | resident soft-path resolution only |
| Per-instance Tick | NONE | existing HISM / WorldDetailCluster |
| P1C02 runtime | NOT OPENED | P1C01 only |
| Fresh exact-head Pre-Unreal | PENDING | PR validation required |
| Fresh exact-head Unreal build/package | PENDING | PR validation required |
| PIE/device/human visual/FPS | NOT ACCEPTED | direct evidence required |


### Closed PR #315 selective salvage

| Item | Disposition | Reason |
|---|---|---|
| Party Field boundary shell | RETAINED IN CANON FINISH B | unique source-grounded field read |
| Water/mill reeds + stepping stones | RETAINED IN CANON FINISH B | unique mill/Water environmental read |
| 3 Bywater-facing cottages | RETAINED IN CANON FINISH B | unique settlement-edge silhouette |
| Duplicate Bagshot homes | SUPERSEDED | #314 + Number 3 anchor already stronger |
| Duplicate clutter / lamps / mail / wash | SUPERSEDED | #314 already covers with clustered/limited detail |
| Duplicate orchard/farm density | SUPERSEDED | avoid unnecessary low-spec density growth |
| Canon Finish B visual budget | LOCKED MAX 153 | 96 HISM + 45 cluster + 4 landmarks + 8 state actors |
| Fresh exact-head validation | PENDING | required after salvage commit |


## 2026-10-04 - P1C01 Shire settlement source closure

| Closure area | Status | Evidence boundary |
|---|---|---|
| Settlement Completion #314 | COMPILE-TESTED / MERGED | head `3ee80ffe...`; Pre #1849 SUCCESS; Unreal #1446 SUCCESS; merge `b3f31134...` |
| Canon Finish B #318 | COMPILE-TESTED / MERGED | head `c9b27bde...`; Pre #1868 SUCCESS; Unreal #1465 SUCCESS; merge `437db07c...` |
| Bag End / Hill | SOURCE-COMPLETE | hero composition + garden/property framing |
| Bagshot Row / Number 3 | SOURCE-COMPLETE | row + dedicated Gamgee visual anchor |
| Party Field | SOURCE-COMPLETE | Party Tree + boundary + special entrance + state-aware kitchen/social detail |
| Hobbiton village common | SOURCE-COMPLETE | market/well/benches/produce/social space |
| Ivy Bush | SOURCE-COMPLETE | bounded Bywater-road inn identity |
| Water / mill / wheel / bridge | SOURCE-COMPLETE | landmark + working-yard + water-edge detail |
| Gardens / hedges / household life | SOURCE-COMPLETE | clustered/HISM domestic detail |
| Orchard / working-field transition | SOURCE-COMPLETE | trees, hay, ploughs, gates, ladders |
| Bywater-road avenue / facing edge | SOURCE-COMPLETE | bounded road framing + three edge cottages |
| Green Dragon in Hobbiton | NOT PLACED | Bywater ownership preserved |
| World construction authority | PRESERVED | AShirePrototypeWorldBuilder only |
| New synchronous heavy loading | NONE | resident/soft pipeline preserved |
| P1C02 runtime | NOT OPENED | predecessor Gate 6/7 still required |
| Local production bootstrap | REQUIRED | `Scripts/bootstrap_local_p1c01_visuals.cmd` |
| Human PIE/rendered visual acceptance | PENDING | direct owner evidence required |
| Target-device 720p / 30 FPS | PENDING | measured device evidence required |


## 2026-10-04 - Frodo targeted animation intake Wave 3

| Gate | Status | Evidence boundary |
|---|---|---|
| Frodo skeletal technical winner | PASS / PRESERVED | `eff0e799...`; 161 bones + linked USkeleton |
| Hero-mesh hunting | CLOSED | do not reopen while technical winner remains valid |
| Animation source | SOURCE-REGISTERED | Quaternius Universal Animation Library / CC0 |
| Animation warehouse scope | BOUNDED | one pack only |
| Warehouse classifier | SOURCE-IMPLEMENTED | `WH_STAGE_QUATERNIUS_ANIM` |
| Broad Quaternius support staging | NOT REQUESTED BY TARGETED PATH | avoids unrelated pack churn |
| Required initial clips | LOCKED | Idle / Walk / Run |
| Receipt/SHA256/public-download proof | PENDING | Warehouse execution after merge |
| FBX clip inventory | PENDING | staged archive required |
| Retarget compatibility | BLOCKED | valid clip inventory first |
| Deformation review | BLOCKED | technical winner + selected clips |
| AnimBP locomotion | BLOCKED | retarget/deformation proof first |
| Async runtime Frodo promotion | BLOCKED | AnimBP/rig bundle proof first |
| PIE/device/rendered visual/FPS | NOT ACCEPTED | direct evidence required |


## 2026-10-04 - Frodo static deformation stress gate

| Gate | Status | Evidence boundary |
|---|---|---|
| Input candidate | EXACT-RUN UE4 WINNER ONLY | same workflow artifacts; no new mesh hunt |
| Required limb joints | SOURCE-GATED | pelvis/spine/head + bilateral arm/hand/leg/foot families |
| Limb hierarchy | SOURCE-GATED | descendant-chain sanity |
| Shoulder stress | SOURCE-IMPLEMENTED | +/-45 degrees |
| Elbow stress | SOURCE-IMPLEMENTED | 75 degrees |
| Knee stress | SOURCE-IMPLEMENTED | 65 degrees |
| Hand/foot stress | SOURCE-IMPLEMENTED | 20 degrees |
| Locomotion combined stress | SOURCE-IMPLEMENTED | deterministic numerical pose |
| Catastrophic deformation guard | SOURCE-IMPLEMENTED | finite vertices + bounds/displacement thresholds |
| Human rendered deformation acceptance | NOT ACCEPTED | direct visual review required |
| Idle/Walk/Run retarget | BLOCKED | targeted animation intake + compatibility proof |
| AnimBP/runtime promotion | BLOCKED | retarget + visual deformation first |


### 2026-10-04 - Wave3 zero-payload guard root fix

| Guard | Status | Evidence boundary |
|---|---|---|
| Pre-Unreal #1872 | FAIL / ROOT-CAUSED | stale exact-count regression only |
| Support Quaternius manual queue | REQUIRED | one explicit manifest call |
| Animation-only manual queue | REQUIRED | one explicit targeted manifest call |
| Hero-candidate manual queue | REQUIRED | one explicit manifest call |
| Broad continue-on-error | FORBIDDEN / PRESERVED | fail-closed policy unchanged |
| Fresh exact-head validation | PENDING | new PR head required |


## 2026-10-04 - Light branch hygiene wave

| Item | State |
|---|---|
| Reviewed dead refs queued | 6 |
| Active P1C01 closeout branch | PRESERVED |
| develop / main / archive | PRESERVED |
| Edoras prep refs | PRESERVED |
| Runtime or Gate 6/7 effect | NONE |


## 2026-10-12 - P1C01 cloud-source 54 FBX candidate (source-only)

- Current develop cloud source producer exports 22 modular static mesh families x LOD0/LOD1 = 44 binary FBX; target in this candidate is 27 x 2 = 54. The five newly prepared families are FerryLanding, MooringPost, WaymarkPost, PartyBannerFrame and GardenStoneBorder, bounded to the already-authorized Shire / Party Field / Bucklebury Ferry visual needs.
- Use the existing CloudAssetBuild Blender generator, material receipt, 28-region original PNG/ORM pack, UCX collision and Blender FBX reimport; no new source manager or runtime owner. Open passage and walkable ferry deck retain narrowly scoped UCX collision geometry.
- Fail closed on 54 distinct physical files, FBX binary version 7400, exact SHA256/bytes, real reimport geometry and UVs, and 27 x 2 identity coverage. This is a candidate until exact-head GitHub-hosted Blender job and artifact are observed.
- Warehouse promotion, UE4 importer / Content/Production persistence, package/PIE, screenshots, DX11 device FPS, human visual and Gate 6/7 acceptance remain separate and UNPROVEN. One warehouse writer and one UE4 runtime writer remain authoritative. No P1C02 runtime activation.


## 2026-10-12 — Cloud138 warehouse closed and P1C01 Unreal intake candidate
- GitHub develop 71efe55668f065117f42d0959c2867f3dfe0eacc. Warehouse Run 38295455001 SUCCESS; log: CLOUD_WHOLEGAME_PERSISTENT_WAREHOUSE_PASS fbx=138 shire=82 regional=56 png=36 regions=28.
- Exact receipt artifact 11767989049: 177 payload files (138 FBX + 36 PNG + 3 source receipts), summed payload 13,095,116 bytes, SHA-pinned against source artifact 11767251532. 28/28 canonical region support packs are source-only, not playable.
- Cloud138 proposed Unreal bridge: 41 Shire LOD0 meshes + 41 LOD1 sidecars + 36 PNG are eligible; 56 regional FBX remain warehouse-only. Import via existing ShireProductionImport under isolated /Game/Production/World/Shire/Cloud138 and /Game/Production/Materials/Cloud138. A further UE4 editor post-import/second-process readback attempts 41 static mesh packages, 36 texture packages and 12 PBR instances (89 **TARGET**, not observed), plus one prior master-parent dependency, followed by hash-receipted D: persistence. Source identity is original project material, not external licensing.
- LOCAL STATIC-VALIDATED only: genuine source archive + Warehouse SHA receipt reassembled offline and 118 source files staged (41 LOD0, 41 LOD1, 36 PNG; 0 regional runtime). Six isolated safety regression cases passed. NOT COMPILE-TESTED for the new bridge, NOT UE_IMPORTED_PERSISTED; 89 is a candidate target until exact-head Windows Unreal process and receipt demonstrate it.
- No Cloud138 mesh is counted as world-placed; no current P1C01 screenshot, quest/collision/nav/PIE/device FPS evidence from the new batch. Gate 6/7 remains OPEN; no P1C02+ runtime. Maintain one warehouse writer and one UE runtime writer. Owner-facing source total stays 138 FBX, not 278; no new net FBX was produced this session.
- Engineering decision: prioritize converting 41 finished Shire source families into durable UE4 packages and player-visible Bag End-to-Ferry placement before pursuing aspirational 140 extra FBX. Avoid creating a parallel importer or claiming regional visual progress.

## 2026-10-12 — Whole-game 140-FBX original source wave (CANDIDATE)
- Source-only hosted Blender wave proposes 70 distinct functional modular families across the 28 Governor-authorized production regions, each with authored LOD0/LOD1, UV and UCX FBX binary 7400; real Blender reimport plus independent SHA256 identity QC is required by `.github/workflows/cloud-wholegame-140-source.yml`.
- This is NOT 140 produced FBX before exact-head hosted workflow and artifact receipt. Prior baseline remains 138 source FBX total; target 278 if all 140 are new unique and PASS. Previous session increment 56; prospective incremental growth +150%. Asset quality and Shire playable closure outrank the numeric target.
- Warehouse transfer remains exclusively single writer; no second permanent-storage writer, no Unreal runtime promotion, no P1C02+ activation. External content rights unaffected (original procedural static source). P1C01 Gate 6/7 remains open; no new PIE/device/visual proof.
- New gameplay/world ideas are not introduced by this wave; only support geometry categories (route, boundary, work, environment, wayfinding) constrained to existing regional production packets. Any physical world placement still requires source-to-runtime gate.

## 2026-10-13 — Cloud-only CC0 Poly Haven material intake strengthening
- Strengthened existing hosted Poly Haven 37 approved texture source lane; four independent hosted shards use documented Poly Haven API and verify real 1K PNG BaseColor, NormalDX, and packed ORM with SHA256 and CC0 source provenance. Network failures quarantine individual sources; no unverified files count.
- Extra fail-closed QC demands complete triplets, individual original-map SHA/source URL, approved official CC0 attribution, and exact observed output count. PR run artifact required before any materials are counted as produced. Intended for existing 28-region source preparation, not runtime activation.
- New Windows UE4 writer jobs: none. P1C01 Gate 6/7 open; .uasset count and visual placement unchanged by this source-only lane.

## 2026-10-13 — P1C01 56-FBX detailed-route source wave (candidate until QC)
- New hosted-only Blender batch proposes 28 distinct Shire support-detail families, dual LOD0/LOD1, actual binary FBX7400, authored UCX shape sidecars, UV+polygon reimport and hash QC, with permanent high-quality runtime asset admission still gated. Includes entry/door hardware, interiors, orchards/gardens, roads, mill and ferry. Does NOT implement or claim animated working doors, physics-walkable ferry or playable route; they require Unreal and PIE after Windows Runner returns.
- Output target: 56 net-new FBX. 140 prior FBX + 108 new Poly Haven PNG already generated and QC-passed in different lanes; additive per-session growth is a source-pipeline goal and never a claim of visual completion.
- Only accepted when GitHub exact-head `SHIRE_DETAIL_56_FBX_QC_PASS` and file artifact exist. Warehouse persistence, Content/Production `.uasset`, in-world placement, 720p 30FPS, Gate6/7 are separate and not proven here.

## 2026-10-13 — Conflict-free FerryLanding collision source candidate (#435)
- Reconciled #435 with develop using a non-force branch merge; carried only the scoped FerryLanding UE4.27 simple Box collision fallback and focused source regression. Excluded the duplicate world-event HUD change, which belongs exclusively to #455, to prevent competing edits.
- Fail closed if the UE EditorStaticMeshLibrary.add_simple_collisions return index is negative, or if simple collision count remains zero. Only FerryLanding with zero imported simple collision in non-reopen editor mode may receive the fallback; other walkable assets retain strict required collision checks.
- The repair path still requires actual UE4.27 Python commandlet execution, physical .uasset save/reopen/collision receipt, P1C01 ferry traversal/navigation, target-device DX11 720p FPS and human visual acceptance. No Gate 6/7 closure or fourth-expansion freeze.
2026-10-14 PES-002 RENDER-REJECTED COMPOSITION ROOT-CAUSE REPAIR: Exact-head PR #477 Unreal Run 38599254268 succeeded for UE4.27.2 compile, import/rehydration, Automation, startup and three mandatory 1280x720 captures; artifact 11913641348 digest sha256:066d0e4addd738639f9681dff57ab9db25060b7a01c30541d6c0967fc63aec0b. Human inspection REJECTED all three images: Bag End remained a flat proxy facade, cameras were too close, dense repeated hedge/grass/prop layers obscured the entrance, and modular characters were obvious placeholders. Runtime log independently confirmed Frodo/Bilbo/Gandalf and other named rigs packages-missing with fallback=modular. Bounded repair moves the decorative mound farther behind and reduces it, widens all three proof views, reduces only Bag End hero detail/density layers while preserving quest anchors, blocking facade/step and population ownership, and adds exact source regression assertions. Character final-art remains blocked on real skeletal FBX packages and is not claimed fixed. STATIC-VALIDATED locally; exact-head UE rebuild/new screenshots/traversal required. PES-002 OPEN; PES-003 locked.\n\n

## 2026-10-14 — PES-002 fresh real-render root-cause: west-facing round geometry (PR #477 follow-up)
- Exact source observed: PR #477 head `c6f55835a4b82c52e765aee7ad247d1a5e67f51b`, Unreal Build Run [38604332835](https://github.com/4youbabee-tech/fellowship-personal-game/actions/runs/38604332835) SUCCESS (engine build/import/automation/headless startup/capture), real screenshot Artifact `11915428403`, archive SHA256 `9a0f79f1478f582aa14c8a9c8a2c48d2ae87486e9e4d626b04ad68aef78aaac7`. The 3 captured 1280×720 PNG views were visually inspected: REJECTED due to flat/cluttered facade and simplistic terrain/NPCs. Image evidence alone does not prove traversal.
- Root cause confirmed in `SpawnHobbitHole`: six CylinderMesh calls used yaw 90 around world Z; Engine cylinder has circular faces perpendicular to local Z, so yaw leaves doors/rings/glass horizontally oriented. Reorient ONLY six Hobbit-hole round details to pitch 90, making the circular fronts parallel to the west-facing YZ facade. No quest anchor, population controller, player collision or asset loading changed. Add focused source regression test.
- Runtime log evidence: `CharacterRigStreaming: unavailable id=Frodo reason=packages-missing fallback=modular retry=bounded`; analogous lines for Bilbo/Gandalf and neighbors. This code fix does **not** manufacture rigged characters or close their asset-source/import/runtime chain.
- Validation boundary: SOURCE PATCH / STATIC source-contract regression added; fresh exact-head UE4.27.2 build, renewed actual screenshots and traversal/collision, DX11 720p target FPS/VRAM and visual acceptance remain REQUIRED. PES-002 OPEN; PES-003 locked.

## 2026-10-14 — Owner-started Frodo-first character source work (PES-002)
- Owner approved immediate real-character production preparation alongside PES-002; this is not opening PES-003, PES-009 or PES-010 runtime. Governor: `pes002_character_visual_pilot_2026_10_14`; source packet: `Data/P1C01CharacterVisualPilotV1.json`.
- Existing Frodo technical rig basis and FBX Idle/Walk/Run exporter are reused. Source edit in `Tools/CloudAssetBuild/frodo_locomotion.py` handles DEF/Mixamo-style left/right bone naming and rejects differing reimported skeleton signatures between the three clips. New regression `Tools/CloudAssetBuild/test_frodo_locomotion.py` is wired to focused hosted workflow.
- The last actual PES-002 runtime render still showed modular placeholders; `CharacterRigStreaming` reported packages-missing. No finished face/material, imported `SK_Frodo`, Animation Blueprint, deformation/retarget quality, PIE, device FPS, or rendered Frodo acceptance is asserted from this source edit. PES-002 remains OPEN, PES-003 LOCKED.

## 2026-10-14 — PES-002 professional-production corrective batch (exact-package identity + honest Frodo skin QC)
- Observed Unreal 4.27 [Run 38623027754](https://github.com/4youbabee-tech/fellowship-personal-game/actions/runs/38623027754): `ShireProductionImport result ... SM_ShBagEndHeroFacade.obj | paths=30 result=0 resolved=no`, followed by `Failed to load '/Game/Production/World/Shire/SM_ShBagEndHeroFacade'`. General import 377/0 was a **false positive for the hero facade**, and `ShireJourney.QA.Assets.StreamingBankPackages` failed. Root cause: authored facade groups split during unattended import. Set `UFbxStaticMeshImportData::bCombineMeshes` for this static facade only, prevent decorative auto-collision, and fail import immediately unless the exact `UStaticMesh` object path exists. Preserve 100% existing story anchors and NPC/streaming ownership.
- Independent Frodo evidence on [Run 38626721769](https://github.com/4youbabee-tech/fellowship-personal-game/actions/runs/38626721769): exported FBX has only 4 weighted bones; mandatory bilateral limb chains/head absent. This is **SOURCE ASSET REJECTED**, not resolved by retargeting tricks, resetting checks, or animation export success. Blender Rigify `DEF` bones require actual per-limb vertex-group weights and active Armature binding; seek properly licensed, genuinely skinned candidate or repair weight paint with source provenance, then run stress/deformation and human visual review before UE4.27 character promotion.
- Professional references: Epic UE4.27 FBX Static Mesh Pipeline (combine mesh option and object import), Skeletal Mesh Pipeline/Skeleton assets/animation retargeting, Static Mesh Foliage instancing/LOD, performance profiling; Blender 4.0 Rigify and Vertex Groups/Weight Paint documentation. New reference packet `Docs/PES002_PROFESSIONAL_ASSET_PRODUCTION_METHOD.md`. Reference knowledge is **not** evidence that finished art/PIE/device/visual acceptance exists.
- Candidate-level source test added for single named Bag End package. Fresh exact-head UE4 build/asset import/streaming package test/screenshots required to validate. Target hardware FPS and VRAM unmeasured, traversal/PIE unverified; PES-002 OPEN; PES-003 locked.
2026-10-15 PES-002 candidate status: `RENDER_OBSERVED` for Bag End at Run 38710725850/Artifact 11960756267, but `VISUALLY-ACCEPTED=NO` after direct four-view review; compile/import/automation/startup are PASS and traversal/PIE/device/performance remain NOT RUN. Frodo source is `SOURCE_AVAILABLE` but `WAREHOUSE_PERSISTED/UE_IMPORTED/WORLD_PLACED/RENDER_OBSERVED/ACCEPTED=NO`; Wave 2 and locomotion both reject pre-export at `HUMAN_WAVE2_SKIN_REPAIR_PRIMARY_MESH_TOO_SMALL`. Candidate root fix changes only group-level source selection/rebinding plus strict exported limb influence receipt; hosted re-run required. PES-002 remains OPEN and PES-003 LOCKED.
2026-10-15 Exact-head `093ab4f`: Pre-Unreal PASS; UE4.27 compile/import/automation/startup PASS; screenshot capture FAIL `PES002_CAPTURE_CAMERA_NOT_CONFIRMED`; Human Wave 2/Frodo locomotion FAIL before FBX at aggregate bound-character selection. Parent-bound relation correction is STATIC-VALIDATED only. No new `UE_IMPORTED`, `WORLD_PLACED`, `RENDER_OBSERVED`, PIE, device, performance, or acceptance state.
