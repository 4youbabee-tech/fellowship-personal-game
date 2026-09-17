# Development Checkpoints

## CP1 — Repository + UE4.27 Base
- Private repository initialized.
- `main` kept as stable baseline.
- `develop` created for active work.
- UE4.27 project descriptor and low-spec configuration added.
- Core systems present: player movement/camera, interaction, HUD dialogue, quest state, quick save/load, ambient NPCs, companion-follow prototype, Black Rider stealth prototype.

## CP2 — Chapter 1 Story Chain
- NPC interactions can transition into the next active quest.
- Quest triggers validate active quest + stage before progression.
- Chapter 1 chain defined from Shire arrival through Bucklebury Ferry.
- Gandalf, Bilbo, Sam, Merry and Pippin prototype story actors wired into progression.
- Sam/Merry/Pippin can enter lightweight follow mode after their story interactions.

## CP3 — The Shire Greybox World
- Runtime world builder implemented in C++ so the chapter can boot without a final `.umap`.
- Greybox includes Bag End, Hobbiton lane, Hobbit holes, Green Dragon silhouette, party field, eastern fields, Brandywine and Bucklebury Ferry destination.
- Lightweight ambient hobbit routines populate the village.
- Story progression locations are spatially connected in one playable route.
- Black Rider patrol/detection section placed before the ferry escape.

## CP4 — Logic Audit / Dead-End Fix
- Fixed NPC transition logic so `NextQuestId` calls `StartQuest`, ensuring HUD/objective and downstream triggers follow the new story beat.
- NPC story interactions now reject interaction when the required quest is not currently active.
- Current limitation: full C++ compile and in-engine runtime validation remain pending until Unreal Engine 4.27 is available on the target machine or CI runner.

## Next
1. Static audit all Chapter 1 C++ for UE4.27 compatibility.
2. Add chapter-completion state and transition hook toward Bree.
3. Add low-cost cinematic event hooks for party, Ring warning, Black Rider approach and ferry escape.
4. Prepare Chapter 2 (Bree / Prancing Pony) data without loading its world into Chapter 1.
5. Once Unreal is installed: generate project files, compile Development Editor, run PIE, fix compile/runtime errors, then benchmark 720p target settings.
