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
- Full C++ compile and in-engine runtime validation remain pending until Unreal Engine 4.27 is available.

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
- Bree story beats expose hooks for nightfall, inn exterior, Ring incident, Strider private-room beat, Nazgul attack and departure.
- Added Chapter 3 quest data for road-to-Weathertop and the Weathertop attack.
- Added a chapter world router so the active prototype region can change without keeping Shire and Bree builders active.

## CP8 — Full Part I Runtime Greybox Skeleton
- Added shared runtime greybox builders for Chapter 3 through Chapter 8.
- Chapter 3: wilderness, Weathertop, Nazgul pressure, Arwen/Flight-to-Ford handoff.
- Chapter 4: Rivendell valley, recovery, Council of Elrond and Fellowship formation.
- Chapter 5: southward road, Caradhras, western gate of Moria.
- Chapter 6: Moria halls, Balin's Tomb and Bridge of Khazad-dum progression.
- Chapter 7: Lothlorien rest/farewell and river departure.
- Chapter 8: Anduin, Argonath proxy, Amon Hen and Breaking of the Fellowship through Part I completion.
- Chapter router now recognizes all eight low-memory runtime regions used by the current prototype architecture.

## CP9 — Chapter Transition Safety Audit
- Fixed quest triggers so only `AShirePlayerCharacter` can progress story triggers; companion characters can no longer accidentally advance missions.
- Chapter changes now remove generated greybox geometry, labels, NPCs, riders and triggers from the previous region before building the next one.
- Added safe player spawn locations per runtime chapter so the pawn does not remain at coordinates from the previous region.
- Quick-load restores chapter/world state before applying the exact saved player transform.

## CP10 — Full Quest/Story State + Pre-Unreal CI
- Added quest definitions for every currently referenced Part I gameplay chain through Amon Hen/Part I completion.
- Added persistent one-time story beats so cinematic hooks do not replay after save/load.
- Save data now includes completed story beats along with chapter, active quest and quest stages.
- Added `Scripts/pre_unreal_validate.py` to check required files, `.uproject` JSON/UE4.27 target, C++ brace balance, Unreal `generated.h` include ordering, quest-definition coverage, chapter routing and generated-folder hygiene.
- Added GitHub Actions workflow `Pre-Unreal Validation` on pushes to `develop` and pull requests.

## Current gate
- Repository-side architecture/story validation is now automated on GitHub.
- The remaining hard gate is a real Unreal Engine 4.27 compile + UnrealHeaderTool pass + Play In Editor runtime test. No static checker can honestly replace those engine tests.

## Next before Unreal
1. Watch and fix every failure from `Pre-Unreal Validation` until the branch is green.
2. Continue UE4.27 API/static audit of world builders, save/load and chapter transitions.
3. Improve companion formation/follow behavior and Black Rider line-of-sight logic without increasing the hardware target.
4. Add a small developer chapter-jump/debug path for fast PIE testing once Unreal is available.
5. Prepare an Unreal test checklist covering Chapter 1 through Part I completion, save/load, transitions and 720p performance.

## Once Unreal is installed
1. Generate project files and compile Development Editor.
2. Fix every compiler/UnrealHeaderTool error before PIE.
3. Run Chapter 1 end-to-end, then each chapter handoff through Part I completion.
4. Validate save/load at chapter boundaries and after one-time story beats.
5. Benchmark 720p/DX11/Low-Medium on the target laptop and tune until stable enough for the intended 30 FPS target.
