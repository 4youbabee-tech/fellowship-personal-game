# PES-002 — Professional asset production method (UE4.27.2)

**Status:** professional reference applied to targeted source import repair; not a claim of rendered acceptance.

## Proven methods chosen for this project

| Discipline | Established professional method | PES-002 implementation / next gate |
|---|---|---|
| Character modeling | licensed humanoid art source, proportions and silhouette before rig; author face/hair/clothes appropriate to chapter | Frodo needs genuine model & costume QC from character bible; source CC0 base model is NOT final likeness |
| Skinning & animation | bone hierarchy -> deform-bone vertex groups -> verified Armature modifier -> normalized weights -> real shoulder/elbow/knee stress -> common Skeleton -> Idle/Walk/Run, AnimBP retarget | imported candidate has just **4 weighted bones** in exported FBX, so reject; do not hide/fake pass; Blender weight paint or source replacement first |
| Bag End architecture | compose curved earth-integrated hero silhouette, circular doorway, window trim, walkable threshold and proper UV/material slots; keep meshes grouped by authored asset | old unattended import split one OBJ into **30 assets**; importer now combines ONLY Bag End hero static facade and asserts expected named `UStaticMesh` |
| Landscape and vegetation | repeated non-interactive foliage via ISM/HISM / Static Mesh Foliage, scalable LOD and cull distances; intentional near/far readability | prepare on existing world assets; no unmeasured NPC spawn or foliage density surge |
| World interactions | one owner for NPC decisions, soft/async loaded assets, collision and traversal tested at quest anchor | no new director, keep NPCContext/LivingWorldDirector and pool |
| Quality and delivery | stage art -> package identity -> exact-head imported and runtime mesh -> screenshot review -> traversal -> target hardware frame cost | Pre-Unreal alone cannot accept runtime; real Unreal 720p screenshots, Gate 6/7 and 30 FPS measurement remain open |

### Primary professional references
- Epic UE4.27 Static FBX Mesh Pipeline: https://dev.epicgames.com/documentation/unreal-engine/fbx-static-mesh-pipeline?application_version=4.27
- Epic UE4.27 Skeletal Mesh Pipeline: https://dev.epicgames.com/documentation/unreal-engine/how-to-import-skeletal-meshes?application_version=4.27
- Epic UE4.27 Skeleton Assets: https://dev.epicgames.com/documentation/en-us/unreal-engine/skeleton-assets?application_version=4.27
- Epic UE4.27 Retargeting: https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-retargeting?application_version=4.27
- Epic UE4.27 Static Mesh Foliage: https://dev.epicgames.com/documentation/en-us/unreal-engine/foliage-tool?application_version=4.27
- Epic UE4.27 Performance Profiling: https://dev.epicgames.com/documentation/en-us/unreal-engine/performance-and-profiling-overview?application_version=4.27
- Blender 4.0 Rigify: https://docs.blender.org/manual/en/4.0/addons/rigging/rigify/index.html
- Blender 4.0 Vertex Group Weight Painting: https://docs.blender.org/manual/sr/4.0/sculpt_paint/weight_paint/usage.html

### Source-level acceptance contract
1. Only a **single object** named `/Game/Production/World/Shire/SM_ShBagEndHeroFacade.SM_ShBagEndHeroFacade` counts as hero facade import; split `ImportedObjectPaths` count alone does not.
2. Do not auto-promote FBX solely for having 161 bones, UVs or nonzero aggregate vertex weights; limbs and head must deform numerically under pose stress and be reviewed visually.
3. No new PES runtime chapter, no synthetic screenshots, no source validation relabelled as PIE/device or visual acceptance.
4. On a failing hardware build, inspect and repair that specific failure before further costly run; keep PES-002 OPEN.

## 2026-10-14 Frodo source-skin repair candidate (no false green)

- Actual hosted runs 38632883899 / 38632883791 at 166656aed failed before UE4: 4 exported weighted bones, missing all head/bilateral limb role weights. Do not requeue the unchanged payload or label the prior skeletal registration as an animation-ready Frodo.
- Blender's armature automatic weights are applied only to the largest already-skinned character mesh when source DEF influence is insufficient; preserve licensed source geometry and armature, fail closed on missing binding, insufficient influence, failed bone heat or any of 13 post-export limb/head roles. This is a **repair experiment**, not accepted animation. Subsequent numerical stress and true UE4/visual acceptance remain obligatory.
- Reference: Blender 4.0 Rigify docs https://docs.blender.org/manual/en/4.0/addons/rigging/rigify/index.html and Blender rigging source practice https://github.com/ahujasid/mcp-for-blender/blob/main/src/blender_mcp/guides/rigging.md . No import, FPS or rendered acceptance follows from a successful source workflow alone.

## 2026-10-15 bounded exterior repair M0 preflight and method
- Scope/previous gates: PES-002 only, PR477; bounded PES001 import proof remains historical, Gate6/7 open. Latest authority and candidate read before changes.
- Lore/reference: supplied 00 source rules and 10 visual atlas require source-backed domestic scale and no canon inferred from visual plates; existing WORLD_DETAIL_LEDGER Bag End exterior policy. This is original visual implementation, no story event or dialogue change.
- Primary professional methods verified: Epic UE4.27 FBX Material Pipeline https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-material-pipeline?application_version=4.27 (named material slots and face assignments); Static Mesh Pipeline https://dev.epicgames.com/documentation/en-us/unreal-engine/fbx-static-mesh-pipeline?application_version=4.27 (explicit triangulation, UVs, authored pivot). Applied through this project's already-established OBJ importer, not a claim that OBJ and FBX are identical formats.
- Decision: reuse/repair original licensed project mesh, MTL and existing surface master instead of sourcing an unrelated house or adding floating runtime primitives. Each finish owns explicit faces; one section per finish, 100cm planar UV scale; no external source acquisition, no additional streaming bank or manager.
- Asset provenance: original project-generated static OBJ + existing TGA, permission unchanged; generator provides reproducible source, public repository contains no restricted third-party asset. Physical hash recorded in Governor. Exact package `/Game/Production/World/Shire/SM_ShBagEndHeroFacade.SM_ShBagEndHeroFacade` remains unchanged.
- Inputs/dependencies: all source files and 7 MTL definitions present; existing material synthesis, texture, OBJ import, async P1C01 bank and Windows UE4.27.2 runner. No active run observed before candidate. No Blender/Unreal local installation: engine validation through existing Windows CI only. Skeletal work is independent and remains rejected at its existing source gate.
- Source tests: deterministic regeneration, all triangle/UV indices, no zero-area triangles, 7 defined finish slots, <=3000 triangles; strict asset audit, pre-Unreal structure and Governor checks. UE tests: actual compile, import with all 7 bindings, existing package automation/startup, 4 unchanged camera captures. Runtime movement/collision/PIE and DX11 720p device measurements remain mandatory but unproven.
- Budget: 2704 triangles, 7 material sections, one existing resident hero mesh actor instead of hero mound plus disc/rim/knob actors; no extra textures, ticking actors, blocking geometry or physics. Actual draw calls/memory/FPS must still be measured.
- Acceptance: legible integrated doorway, paired recessed windows, roof joining facade, all four angles inspected; luminance >=35 is only screening. Owner visual/traversal/device acceptance still needed.
- Rollback: revert this bounded candidate as one change on PR477 if import/build/render regresses; never merge failing head, never overwrite active writer, no force push. Do not revert unrelated character source work.
