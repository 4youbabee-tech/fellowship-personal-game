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

## CP11 — Companion Restore Continuity
- Recruited lightweight companions now recover their follow state after a save/load or runtime world rebuild by checking persisted quest-stage progress.
- Follow restoration is delayed until the first NPC tick so runtime world builders have already assigned each companion's quest and follow configuration.
- Repeating recruitment dialogue is no longer required just to make Sam, Merry or Pippin resume following after restored Shire state.

## CP12 — Black Rider LOS + Low-Spec Detection Pass
- Black Rider detection now subscribes to active-quest changes and performs detection work only while `KeepOffRoad` is active; inactive Shire play no longer polls the quest subsystem every detection interval.
- Line-of-sight uses simple `ECC_Visibility` collision instead of complex triangle tracing, matching the primitive greybox cover and lowering trace cost on the low-spec target.
- Detection now requires configurable consecutive visible samples before alerting, reducing one-frame edge/occlusion false positives while preserving crouch radius and forward-cone checks.
- Quest-change handling resets detection confidence immediately and save-state restoration remains compatible because the quest subsystem rebroadcasts the active quest during restore.

## CP13 — Real UE4.27 Baseline
- An earlier source baseline compiled and opened successfully in Unreal Engine 4.27.2.
- PIE was observed working on that earlier baseline.
- Movement, quests and HUD were observed working.
- Later C++ changes must be revalidated; historical engine success is not inherited automatically.

## CP14 — Shire Vertical-Slice Expansion
- Humanoid story/ambient proxies, richer paths/homes/gardens/fences/population and instanced foliage.
- Optional Shire side stories that do not replace the main quest.
- Warm morning presentation and deeper original Shire dialogue.
- Low-cost ambient population remains the target.

## CP15 — Canon / Data Alignment
- Added the Story Canon Bible.
- Runtime chapter truth standardized to P1C01-P1C08.
- DialogueIntent and StoryBeatPlan aligned with current runtime buckets.
- Added MusicCuePlan for original music direction.

## CP16 — Persistent Multi-Route State
- Added RouteId / EpisodeId / PlayableCharacterId.
- Added per-route quest/story/transform progress.
- Quick save/load persists route state.
- Parallel-route state is designed not to overwrite Frodo's main route.

## CP17 — Gandalf / Isengard Parallel Prototype
- Added Gandalf parallel route.
- Added Isengard/Orthanc runtime prototype.
- Added Saruman, prison, industry and escape progression.
- Added original dialogue and presentation/audio cue wiring.
- F8 is the temporary developer route toggle.
- Pre-Unreal Validation #74 caught missing presentation cues immediately after the world commit.
- The following presentation commit fixed the gap and #75 returned green.

## CP18 — Part I Depth + Ambient Awareness
- Rivendell expanded with Bilbo and wider Fellowship social presence.
- Fellowship road expanded with camp/training and Crebain.
- Moria expanded with Watcher, Orc/Troll escalation and stronger bridge approach.
- Lothlorien expanded with grief and Mirror material.
- Amon Hen expanded with Boromir pressure/defense before the split.
- Ambient Shire residents can notice/face the nearby player briefly, then resume routines.
- Runtime-code baseline reached Pre-Unreal Validation #77 successfully.

## CP19 — Project Memory / Guardian
- CURRENT_PROJECT_STATE is the recovery/handoff entry point.
- DEVELOPMENT_GATES defines build/PIE/device acceptance.
- PROJECT_GUARDIAN records repeatable regressions.
- ProjectGuardRules.json makes chapter/route/canon/document rules machine-readable.
- Pre-Unreal Validation is extended to detect story/data drift automatically.

## CP20 — Current UE4.27 Compile + Basic PIE Boot
- Pre-Unreal Validation #80 is green.
- UE4.27.2 + UnrealHeaderTool completed successfully on the target laptop after PG-010/PG-011 fixes.
- Unreal Editor launched successfully.
- PIE entered the Shire.
- Current HUD rendered Frodo / P1C01_Main and the opening objective correctly.
- This proves compile + basic PIE boot only; save/load, route round-trip and chapter smoke tests remain pending.

## Current hard gate
The current runtime-code baseline has passed static validation, real UE4.27 compile and basic Shire PIE boot.

It must still pass:
1. Shire movement / interaction / NPC-awareness smoke test,
2. save/load round-trip,
3. Gandalf/Isengard F8 round-trip,
4. chapter smoke tests P1C02-P1C08,
5. target-device performance observation.

No new major feature checkpoint should open before this functional gate is healthy.

See `Docs/CURRENT_PROJECT_STATE.md` for the exact current test checklist.
