# Shire Journey: fast P1C01 PIE iteration (2026-10-11)

## Primary owner workflow
1. Keep Unreal Engine 4.27.2 and the local Shire Journey checkout on the owner's Windows 11 Pro PC (i7-6498DU, Radeon R5 M330 2039 MB, 8 GB RAM).
2. **After synchronizing the required branch and completing a C++/asset import once**, double-click `SHIRE_FAST_PIE_PREVIEW.bat` in the local project folder. It uses only existing local files and existing compiled editor modules; it performs **no git pull, no C++ rebuild, no cook and no Windows package**.
3. After Unreal opens, click **Play** (PIE). Inspect Bag End, Hobbiton, Bagshot Row, Party Field, PBR material presence, interaction, NPCs, cinematics and save/restore.
4. For changed C++/UHT files, missing modules, shader/asset import or material changes that have not been applied locally, run the existing normal update/build/import helper **before** using fast preview. Fast preview does not conceal stale binaries, sync a PR or perform asset imports.
5. Keep the full `SHIRE_PIE_VERIFY.bat` for evidence-tagged canonical develop sessions. The fast preview is not a substitute for real acceptance signoff.
6. At chapter delivery/critical integration milestones, retain the normal build/import, packaged Windows executable, user device frame-time/VRAM sampling, visual/pacing review, Gate 6/7. No automatic quality/30 FPS labels.

## Production acceleration without unsafe shortcuts
- Reuse intact source hashes, license receipts and unchanged green validation outputs. Isolate changed-asset QC instead of repeating whole warehouse conversions.
- Continue concurrent **independent** source preparation for character rigs, animation, environment art, audio, localization and QA; maintain exactly one runtime/world code writer and one persistent warehouse writer.
- For ordinary visual iteration use PIE (or Standalone from Editor) after import. Do not run Windows package after every source-only change; keep a full package for release/integration and runtime-delivery boundaries.
- PR #365 is merged with 16 real PBR mesh/material bindings on UE4.27.2; use the observed run receipts before deciding whether expensive jobs can be skipped. PR #355 remains a stale competing branch, not the canonical PBR integration.
- Production HISM/LOD/culling, async FStreamableManager banks and bounded NPC pooling already exist. HLOD, extra streaming worlds, Editor Utility Widgets or Gauntlet are optional measured upgrades, not prerequisites or guarantees.
- Asset and license integrity, engine import/material correctness, story canon, save safety, real P1C01 playthrough, and final DX11 720p stable 30 FPS measurements on the user's machine remain hard requirements.
- Do not open P1C02 runtime before P1C01 Gate 6/7 evidence; source-only parallel preparation is allowed.

## Honest evidence boundary
This is a tooling and workflow optimization only. Merely opening the Editor, creating a marker file, or compiling a module is **not** PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED or FPS acceptance.
