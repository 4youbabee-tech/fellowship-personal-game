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

## CP5 — Chapter Framework + Save Persistence
- Added `CurrentChapterId` to the quest subsystem and save state.
- Save/load restores active chapter in addition to player transform and quest state.
- Quest triggers can transition directly into the next chapter and starting quest.
- Chapter 1 can hand off to `P1C02` without loading both regions at once.

## CP6 — Bree / Prancing Pony Greybox
- Added a dedicated Chapter 2 runtime world builder for Bree.
- Greybox includes the East Road approach, western gate, compact town streets, Prancing Pony exterior, common-room proxy, simple crowd flow and story interaction points.
- Added Chapter 2 progression: road to Bree, gate entry, Prancing Pony, Butterbur, common-room attention, Strider, private-room sequence, Nazgul night attack and dawn departure.
- All new dialogue is original game dialogue that follows scene intent rather than copying screenplay lines.

## CP7 — Cinematic Hooks + Weathertop Handoff
- Added generic `StoryBeatId` events that can later drive Sequencer/camera/audio without hard-wiring cinematics into quest logic.
- Bree story beats now expose hooks for nightfall, inn exterior, Ring incident, Strider private-room beat, Nazgul attack and departure.
- Added Chapter 3 quest data for road-to-Weathertop and the Weathertop attack.
- Added a chapter world router so the active prototype region can change without keeping both Shire and Bree builders active.

## Next
1. Static-audit the new Bree/router code for UE4.27 API compatibility and obvious compile hazards.
2. Add player spawn/teleport points per chapter so chapter transitions reposition the player safely.
3. Add Chapter 3 Weathertop runtime greybox and story flow.
4. Add shared story flags for one-time cinematic/story events and persist them in save data.
5. Continue Part I chapter foundations toward Rivendell while keeping regions separate for the target hardware.
6. Once Unreal is installed: generate project files, compile Development Editor, run PIE from Chapter 1 through the Bree transition, fix compile/runtime errors, then benchmark 720p target settings.
