# P1C01 Runnerless Source Backlog

This is an operational queue for `W01_P1C01_PRODUCTION_VERTICAL_SLICE` when the UE4/Warehouse self-hosted runner cannot be proven available.

It does not open a new runtime chapter and does not promote any asset to STAGED, READY_FOR_IMPORT, IMPORTED, INTEGRATED, COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED, or performance-accepted state.

Execution order stays bounded and reuses existing project work:

1. Material source preparation from `Data/P1C01MaterialImportWaveV1.json`; source promotion may produce `generated/p1c01-material-source-v1`, but Unreal import proof remains a separate exact-head gate.
2. Architecture/prop preparation from `Data/P1C01ArchitectureInteriorPropMegabatchV1.json`.
3. Audio/foley preparation from `Data/P1C01AudioFoleyAmbiencePrepV1.json`, retaining WAV-master QC before import.
4. Fauna preparation from `Data/P1C01LivingWorldFaunaPrepV1.json`, preserving existing fauna caps and requiring FBX for animated production assets.
5. Character/animation preparation from `Data/P1C01CharacterRigAnimationPrepV1.json`, preserving FBX + provenance + skeleton/skin/retarget/deformation QC.

Global production rules remain unchanged: PNG/TGA for production textures, soft references plus asynchronous `FStreamableManager` loading for heavy runtime assets, pooled/bounded ambient crowds, and manual-queue/quarantine continuation when one provider or payload is blocked.

When the matching self-hosted runner returns, consume prepared batches in bounded Warehouse/Unreal order. Freeze any exact head awaiting machine proof and continue unrelated source-only preparation on a separate branch instead of mutating that head.
