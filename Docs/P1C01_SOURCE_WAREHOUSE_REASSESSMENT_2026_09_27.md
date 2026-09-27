# P1C01 source and warehouse reassessment — 2026-09-27

Authority: `Data/ProjectGovernor.json`. Scope: W01/P1C01 Shire, Hobbiton and Bag End. This is a source and repository/CI inventory; it is not UE import, PIE, device, visual, or performance acceptance.

## Evidence and corrections

- Owner sources 00, 01, 03, 06, 10 and 11 call for the Shire opening, Bilbo's party and departure, a warm lived-in Hobbiton/Bag End, social play and bounded world detail. Source 10 is a modeling aid only; the film/script hierarchy in source 00 governs story facts.
- The tracked `SourceAssets/Production` tree contains project-owned static OBJ components and TGA foundation textures, including Shire grass, dirt, bark, leaves, stone, wood and green-door surfaces. File presence does not prove realistic finished materials, hero architecture, usable skeletons, animations or engine integration.
- Warehouse #264 passed on 2026-09-26: 247 payload files, 3,851,680,492 bytes, 13 receipts, 667 receipt records, 215 duplicate hash groups. The receipt-record count is not a count of unique assets. Poly Haven 219 reused files, OpenGameArt 17, ambientCG 11+8, Kenney 12, KayKit 8; Quaternius reported 0 files and 17 unresolved candidates. These figures describe runner storage at that run, not a fresh inspection of the machine now.
- Warehouse #265–#267 failed at `run_warehouse_saturation_train.ps1` while accessing `.Sum` for an empty verified car under StrictMode. Consequently the later critical-gap preparation and provider-resolution steps were skipped. The script now sums sizes safely for empty cars and provider groups; an actual Windows run is still required to prove it.

## Prioritized intake within the active P1C01 gate

| Need from project sources | Existing evidence | Next asset action | Ceiling until proof |
| --- | --- | --- | --- |
| Grass, dirt lanes, plaster, timber, mossy stone, bark | Project-owned TGA foundation and staged Poly Haven/ambientCG receipts | Dedupe by hash; inspect source/license receipt, dimensions, channel maps and 1K/2K conversions; select bounded material set | INTAKE_QC; UE import/runtime/visual pending |
| Hobbiton/Bag End architecture and furnishings | Project-owned static shells/props; Kenney/KayKit support packs; Quaternius candidates unresolved | Inspect geometry and license; fill support furniture, fences, farm/building stock; separately art-direct round-door hero silhouettes and dense Bag End interior | Support stock only; hero composition pending |
| Frodo/Bilbo/Gandalf/Sam character presence | Existing modular OBJ proxies | Obtain or author actual skeletal FBX, compatible animations, skin weights and deformation; never count OBJ as final animated art | Candidate/preparation until FBX QC |
| Bounded fauna and foliage | Project-owned static bird/rabbit/butterfly fallbacks, Kenney support, Quaternius unresolved | Resolve actual licensed/available animated FBX and inspect LOD, overdraw, collision, skeleton and caps | No density increase |
| Party, ambient, hearth and footstep sound | OpenGameArt receipt reuse and audio candidate lists | Inspect/convert masters to WAV; listen for loops, channels and noise, then test in UE without `-NoSound` | STAGED or INTAKE_QC; playback pending |
| Bilbo's party and Ring narrative clarity | Source 01 and source 06 activity beats; chapter data and runtime code | Preserve locked departure/Ring outcome, readable party props and interactions; validate state/save/transition once UE resumes | No claim of gameplay acceptance |

## Execution order

1. Repair the runner ownership issue separately. Once the supervised interactive user owns it, rerun the warehouse stage workflow at the exact PR head so the fixed saturation report and downstream gap preparation/provider resolution execute. Record fresh receipt counts and unresolved reasons.
2. Use the resulting receipts to select a small P1C01 batch via the existing `Data/P1C01WarehousePromotionQueueV1.json` and `Data/ProductionAssetPromotionPolicyV1.json`; inspect licenses and formats before `READY_FOR_IMPORT`. Quaternius zero-file candidates must remain unresolved until a real downloadable, licensed payload exists.
3. Only after the core Unreal lane recovers: import and bind the selected material/prop/audio batch; run the necessary UE build, Automation and runtime checks, then human rendered and target-device checks for claims they alone can establish.

No downloaded payload or new production-ready state is asserted by this document.
