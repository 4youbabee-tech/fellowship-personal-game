## 2026-10-08 - P1C01 common Hobbit fallback preservation

- The named-identity bank reduction was correct in scope, but its first implementation filtered out the five common Hobbit meshes that the existing modular fallback still owns. That is a source/data defect in the in-flight #1711 head, not valid runtime evidence.
- Root fix: restore only the common Hobbit torso/head/hair/arm/leg packages while retaining the bounded Gandalf/Bilbo/Sam promotion set. The P1C01 audit is recalculated from the corrected bank.
- Fresh exact-head #1712 UE4/render/package proof is required. No visual/device/performance/Gate 6/7 claim is made; named skeletal rigs remain open and P1C02 Bree remains LOCKED.

## 2026-10-08 - P1C01 named identity bank startup correction

- #1710 passed source/static, C++ build, and production import, but its first integrated capture timed out before BeginPlay/world logs after the P1C01 bank was expanded by 36 named static packages. No render or runtime acceptance evidence was produced.
- Root fix: keep only the bounded visible core cast identity set (Gandalf, Bilbo, and Sam) in the initial P1C01 resident bank; retain other named static source inputs for a later staged packet. Audit metadata is recalculated from the reduced bank.
- This preserves async ownership and avoids synchronous loads or per-frame scans. Fresh exact-head #1711 UE4/render/package proof is required; named skeletal rigs, visual/device/performance/Gate 6/7 remain unclaimed and P1C02 Bree remains LOCKED.

## 2026-10-08 - P1C01 named static identity residency packet

- #1709 is technically green and its six render logs show hfGrass=resident, but named cast requests still report core-packages-missing for skeletal rigs and the reviewed frames retain primitive/modular identity fallback.
- Root cause: OBJ-imported named identity packages are present in SourceAssets/Production/Characters, while the P1C01 async bank carried only common Hobbit/static pieces. ResolveObject therefore could not promote the dedicated Gandalf/Bilbo/Sam/Merry/Pippin/Hamfast/Rosie/FarmerMaggot meshes at presentation time.
- Source fix: promote the bounded named static identity set into the P1C01 ChapterAssetStreamingPlan and record its ownership in the character presentation manifest. This does not invent skeletal rigs or synchronous loads; the missing named skeletal core remains explicitly unaccepted.
- Fresh exact-head #1710 UE4/render/package proof is required. P1C01 visual/device/performance/Gate 6/7 remain unclaimed and P1C02 Bree remains LOCKED.

## 2026-10-08 - P1C01 streaming audit reconciliation

- #1708 passed the source contract after the five-material expectation was corrected, then stopped in PG-226 preflight because the valid grass-bank addition changed the derived P1C01 bank count from 88 to 89 and the unique package total from 243 to 244.
- Root fix: ChapterAssetStreamingPlan.audit now records the derived 89 P1C01 assets and 244 unique production packages. The runtime bank remains async-owned; no synchronous load, density, collision, or gameplay authority changed.
- Fresh exact-head #1709 UE4/build/render/package evidence is required. #1708 has no Unreal evidence; visual/device/performance/Gate 6/7 remain unclaimed and P1C02 Bree remains LOCKED.

## 2026-10-08 - P1C01 grass-bank contract reconciliation

- #1707 reached the exact-head static gate but correctly stopped before Unreal: the streaming-bank fix added the persisted MI_Sh_GrassPath_PH package, while the source contract still asserted the previous four-material count.
- Root cause is closed in the contract owner: the P1C01 bank now has five imported production materials (dirt, grass path, stony path, tree bark, and moss stone), and the test explicitly verifies all five.
- No runtime code, synchronous load, density, collision, or asset ownership was weakened. Fresh exact-head #1708 UE4/build/render/package evidence is required; visual/device/performance/Gate 6/7 remain unclaimed and P1C02 Bree remains LOCKED.

## 2026-10-08 - P1C01 grass material streaming-bank root fix

- #1706 was correctly blocked by the exact-head source contract before Unreal: the temporary LoadObject fallback inside ShirePrototypeWorldBuilder::BeginPlay violated the no-synchronous-production-load rule.
- Root cause is now closed at the ownership boundary: MI_Sh_GrassPath_PH was imported/persisted but absent from the P1C01 ChapterAssetStreamingPlan bank, so ResolveResidentMaterial could legitimately remain deferred at BeginPlay.
- Root fix: add MI_Sh_GrassPath_PH to the P1C01 async resident bank and remove the BeginPlay LoadObject fallback. The world builder remains ResolveResident-only; no new streaming owner, asset sweep, density, collision, or per-frame work is added.
- Fresh exact-head #1707 source/UE4/render/package reproof is required. #1705 remains a failed screenshot-timeout run and #1706 has no Unreal evidence. Visual/device/performance/Gate 6/7 remain unclaimed; P1C02 Bree remains LOCKED.

## 2026-10-08 - P1C01 grass/ground packet capture root fix

- #1705 passed source/static gate, C++ build, Unreal verification, and production import, but failed during the first six-shot screenshot with P1C01_RENDER_CAPTURE_FAIL reason=screenshot_timeout; all runtime/package steps were correctly skipped.
- The #1705 render log also reported hfGrass=deferred at BeginPlay, proving the new resident grass-path material was not yet resolved when the terrain HISM override ran. The imported material package exists in the commandlet path, so this is a bounded residency timing defect, not evidence of a new world or gameplay failure.
- Root fix: load only the persisted MI_Sh_GrassPath_PH package as a one-time fallback when ResolveResidentMaterial has not resolved it. No asset sweep, per-frame work, actor density, collision, or common-asset mutation is introduced.
- Fresh exact-head #1706 capture/package evidence is required. The screenshot timeout remains a failed run; no current visual/device/performance/Gate 6/7 status is promoted, and P1C02 Bree remains LOCKED.

## 2026-10-08 - P1C01 high-fidelity grass/ground readability packet

- #1704 is technically green on the exact branch head: C++ build, production import, six-shot render capture, runtime QA, chapter audit, route/save roundtrip, cook/package, packaged launch, runner hardware-boundary collection, and artifact upload all passed.
- The reviewed #1704 artifact is still diagnostic rather than visual acceptance: the Shire is readable and the Frodo rig reports active at scale 0.010, but broad ground/terrain surfaces remain visibly low-detail/blockout.
- Root cause targeted in this packet: the resident SH_GRASS_PATH material was imported but not promoted onto the broad repeated ground/hill/slope HISM surfaces; the previous path only used the grass-family fallback.
- Runtime repair: resolve the already-imported MI_Sh_GrassPath_PH resident material and apply it only to the existing GroundTileInstances, GeographyHillInstances, and GeographySlopeInstances. No new actor density, collision, sync load, per-instance tick, or common-asset mutation is introduced.
- A fresh exact-head #1705 render/package run is required. VISUALLY-ACCEPTED, DEVICE-TESTED, PERFORMANCE-ACCEPTED, and Gate 6/7 remain unclaimed; P1C02 Bree remains LOCKED.

## 2026-10-08 - P1C01 all-slot patch compile root fix

- Unreal Build Validation #1703 failed at the C++ build, not at Unreal runtime: MSVC C4456 reported a nested MID declaration in ShirePlayerCharacter.cpp after the all-slot patch retained the previous outer MID guard.
- Root fix: removed the redundant outer guard and kept one MID allocation per material slot. The intended all-slot coverage is preserved for player and NPC modular surfaces.
- #1703 did not produce valid new runtime evidence; the prior #1702 render remains diagnostic only. A fresh exact-head One-Shot is required.

## 2026-10-08 - P1C01 character material slot coverage root fix

- #1702 captured the intended material branch: the foreground ambient Hobbit body changed to the production green palette, proving M_ProductionSurface was selected. The head and limb meshes still retained white/grey regions because the runtime override touched slot 0 only while those meshes expose additional material slots.
- Root fix: player modular pieces and NPC modular pieces now apply their bounded production MID across every material slot, preserving each component's chosen color/roughness/metallic values. Skeletal palette coverage remains unchanged and also already iterates all skeletal slots.
- A fresh exact-head render/package run is required. The world is still not visually accepted; no device/performance/Gate 6/7 claim is made.

## 2026-10-08 - P1C01 static NPC material branch root fix

- #1701 reproof logs confirmed the loaded M_ProductionSurface fallback was available, but generic ambient NPCs still selected BasicShapeMaterial because ApplySurface gated the production parent on bProductionVisual.
- Root fix: all modular NPC residents now use the resident production surface whenever available; BasicShapeMaterial is retained only as the final unavailable-material fail-safe. Named-character mesh selection, skeletal rig ownership, and bounded LivingWorld population remain unchanged.
- A fresh exact-head render/package run is required. Visual/device/performance/Gate 6/7 acceptance remains unclaimed.

## 2026-10-08 - P1C01 material fallback root fix

- The #1700 render artifact proved the skeletal Frodo palette path executed, but the white figures in the reviewed frames were modular NPCs whose static presentation had fallen back to UE Engine BasicShapeMaterial because M_ProductionSurface was only resolved, not loaded, at first style application.
- Root fix in this packet: player and NPC presentation now load the existing M_ProductionSurface synchronously only as a one-time material fallback when the resident object is not yet resolved; Engine BasicShapeMaterial remains the final fail-safe. This is bounded to style application and does not add per-frame work, new assets, or a new streaming owner.
- #1700 remained technically in progress at the time of this correction; its render artifact is evidence for diagnosis only. A fresh exact-head #1701 render/package run is required. Visual acceptance, device acceptance, performance acceptance, and Gate 6/7 remain unclaimed.

## 2026-10-08 - P1C01 character identity and living-world packet

- The exact-head #1699 integrated render/package run is technically green: six-shot capture, runtime audits, cook/package, packaged launch, and hardware-boundary collection all passed. Real artifact review improved composition/lighting, but still showed low-poly/blockout world surfaces and weak/white skeletal character identity.
- Root cause targeted in this packet: async-resolved skeletal rigs did not receive a resident production material palette at the rig handoff, so a technically active Frodo/NPC rig could read as a white mannequin while modular identity pieces were hidden.
- Runtime repair: both AShirePlayerCharacter and AShireNPC now apply a bounded palette using the existing /Game/Production/Materials/M_ProductionSurface to every resolved skeletal material slot, with no new streaming path, no per-frame work, and existing URO/visibility-tick controls preserved.
- P1C01 living-world population, dialogue, quest ownership, save/load, audio ownership, and P1C02 lock are unchanged. This packet is not visual acceptance; a fresh exact-head render and packaged evidence are required before any gate status changes.

## 2026-10-01 - Critical-gap receipt supersession parity

- Warehouse #306 at `develop@5ec1307aa749741fa10c801c288b101ef4b5292a` proved the canonical inventory audit is clean: 18,925 payload files / 6,745,968,858 bytes / 239 active receipt records / 428 superseded / zero hash, missing, license, dangerous, or duplicate-hash failures.
- The next critical-gap preflight still read all historical receipt rows literally and therefore re-reported three retired `C:` records after the authoritative audit had superseded them.
- Root fix: critical-gap preparation now applies the same active-root canonicalization and newest-receipt-per-normalized-payload selection before SHA256 verification. Same-receipt duplicates remain counted separately; genuine newest-record corruption remains fail-closed.
- Hosted regression coverage now executes both the inventory audit and critical-gap preparation against the same real Windows migration fixture.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD PRE-UNREAL + WAREHOUSE PROOF PENDING**. No payload refresh, Frodo/Gandalf acceptance, PIE, device, visual, pacing, performance, or Gate 6/7 claim.

## 2026-10-01 - PG-207 real legacy-path fixture guard

- Exact-head Pre-Unreal correctly rejected the real `C:\\actions-runner` migration fixture as though it were live runner configuration. This was a validator false positive after the fixture was corrected to the real Windows path form.
- PG-207 now permits exactly one known historical-path literal in the dedicated receipt-supersession test and requires it to be the canonical fixture assignment. Any additional occurrence, any different test/script occurrence, or any workflow/config occurrence remains a fail-closed retired-root violation.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD PRE-UNREAL PENDING**. The D-root operational authority is unchanged.

## 2026-10-01 - Warehouse real Windows path canonicalization correction

- Warehouse #305 proved the prior root-rebase implementation still failed for real receipt paths such as `C:\actions-runner\_warehouse\ShireJourney\...`: the PowerShell source used C-style doubled backslashes, which are literal double characters in PowerShell rather than an escape sequence.
- Root fix: receipt normalization now uses single Windows separators in replacement, marker matching, trim, and normalized-key operations. The regression fixture now uses the real single-backslash `C:\actions-runner\...` form recorded by the runner.
- The two affected records are preserved for the targeted candidate gate: missing `snow_01_diff_2k.png` and hash-mismatched `rock_01_arm_2k.png` remain fail-closed until the bounded staging path repairs only them.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD PRE-UNREAL + WAREHOUSE PROOF PENDING**. No blanket refresh and no Frodo/Gandalf or human/device acceptance claim.

## 2026-10-01 - Warehouse candidate gate trigger hardening

- Confirmed integration defect: Warehouse Stage #305 at `develop@9e87b1b45556e8429c1ef14dc12a931ce5a95fce` skipped both targeted provenance repair and the Frodo/Gandalf candidate report because GitHub's final merge subject did not retain the prior `P1C01_FRODO_CANDIDATE_QC` text marker.
- Root fix: every relevant `Warehouse Stage` push now executes the bounded targeted provenance repair and exact-head candidate-report lane. These operations reuse verified payloads, purge only hash-mismatched payloads, and never authorize a blanket refresh.
- This removes merge-subject wording as a runtime control plane while keeping the existing 20-minute repair bound, SHA256 receipt enforcement, fail-closed corruption handling, and artifact upload.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD PRE-UNREAL + WAREHOUSE PROOF PENDING**. No Frodo/Gandalf acceptance, PIE, device, visual, pacing, performance, or Gate 6/7 claim is made.

## 2026-10-01 - Warehouse migrated-receipt root rebasing

- Warehouse Stage #304 on `develop@a75b2f810996289ba5795995563a7c83e406c526` proved the active payload root is `D:\\actions-runner\\_warehouse\\ShireJourney`, but two records inside the migrated Poly Haven V3 receipt still named the retired absolute `C:` root.
- The inventory audit now canonicalizes any receipt path under `*\\actions-runner\\_warehouse\\ShireJourney` onto the explicitly supplied active warehouse root before provenance grouping, SHA256 verification, and license-snapshot verification.
- This preserves payloads and lets newer same-payload receipts supersede historical records across runner-drive migration; it does not suppress genuine active-root missing files or hash mismatches.
- Hosted regression coverage models a stale `C:` receipt against the active root and retains fail-closed enforcement for a tampered newest receipt.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD PRE-UNREAL + WAREHOUSE PROOF PENDING**.
- No full Poly Haven refresh is authorized by this repair; no gameplay, PIE, device, visual, pacing, performance, or Frodo-candidate acceptance is claimed.

## 2026-10-01 - P1C01 Frodo candidate warehouse targeted-repair lane

- Canonical failure head: `develop@b8cee93c01673fc2635f672ca0a0fbe1f543311a`; Warehouse Stage #302 ended **FAILURE** during `Repair candidate-gate material warehouse provenance` after approximately 54 minutes of job execution.
- GitHub retained the active step without a terminal step conclusion and published neither job log nor candidate artifact. Therefore the terminal runner/service cause is not claimed, and no Frodo/Gandalf candidate result exists from #302.
- Source inspection confirmed a failure amplifier: the candidate-gate path passed `-Refresh` to the full Poly Haven V4 batch (37 material/prop slugs, 2.6 GB byte cap), deleting every already-staged payload even when only one receipt hash was stale.
- Root-fix candidate: receipt reuse now verifies recorded SHA256, purges only the mismatched payload, and lets the existing staging path redownload only missing/corrupt files. The candidate-gate repair step no longer forces full-batch refresh and is independently bounded to 20 minutes.
- Regression coverage exercises a same-size content corruption so size-only validation cannot regress.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD PRE-UNREAL + WAREHOUSE PROOF PENDING**.
- Not claimed: COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED, Frodo candidate acceptance, or runtime integration.

## 2026-10-01 - P1C01 FOUNDATION_CORRECTIONS_V1 active

- Canonical base: `develop@3ec3f725cb1dff42a762e36e39790b82a4801714`, which is machine-green after PR #207 (Pre-Unreal and Unreal Build Validation SUCCESS).
- Confirmed Living Shire defect repair: builder-authored humanoid ambient residents were outside `LivingWorldDirector::GatherActiveAmbientNPCsNear()` candidate sources. The Director now performs a committed-world reconciliation pass, weakly registers persistent social-capable ambient residents, excludes Director-managed pooled actors/fauna, and includes that registry in the bounded nearby social query without taking lifecycle ownership.
- Startup-order constraint is preserved: `AChapterWorldRouter` may commit/build before `ALivingWorldDirector` exists, so registration is Director-owned at committed-world reconciliation rather than pushed into each builder spawn site.
- Footstep foundation hardening: `DefaultEngine.ini` defines Grass/Dirt/Stone/Wood physical surface types; `UShireFootstepComponent` prefers `UPhysicalMaterial::DetermineSurfaceType` and retains the existing identity fallback for legacy/proxy materials.
- Hero skeletal intake policy now explicitly requires UE4.27 FBX 2018-compatible exports, keeps OBJ character pieces as `STATIC_MODULAR_FALLBACK_ONLY`, and aligns the visual target to **Balanced Medium / selective High** while retaining the 720p/30 FPS low-spec performance floor.
- No fauna density increase, Niagara rewrite, Part II runtime expansion, synchronous heavy load, parallel AI/audio owner, or story/canon change is introduced.
- Current status: **SOURCE-IMPLEMENTED / EXACT-HEAD PRE-UNREAL + UE4.27.2 PROOF PENDING** on this repair branch.
- Not claimed: PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED, PACING-ACCEPTED or PERFORMANCE-ACCEPTED.

## 2026-09-30 - P1C01 SAVE_LOAD_LONG_SESSION active

- Predecessor SHIRE_AUDIO_IDENTITY: exact-head machine-green on PR #199 at `c258cebda8ae5749c54ed0aa6717582b89988fc3` with Pre-Unreal #1486 SUCCESS + Unreal Build #1159 SUCCESS; merged as `ec96e9e487ecbe91d9563848f685df4bd5c11b0d`.
- Active runtime/reliability car: SAVE_LOAD_LONG_SESSION.
- Existing restore transaction, world-revision checkpoint guard, queued snapshot coalescing, legacy canonicalization and committed-world transform grounding remain authoritative.
- This car adds fail-closed bounded save-payload admission before restore mutation so long sessions/corrupt saves cannot expand persistence containers without limit.
- Status: SOURCE-IMPLEMENTED / EXACT-HEAD PRE-UNREAL + UE4.27.2 PROOF PENDING.
- Human long-session PIE, device save/restore hitching and persistence-stress acceptance: PENDING / NOT CLAIMED.

## 2026-09-30 - P1C01 SHIRE_AUDIO_IDENTITY active

- Predecessor CINEMATIC_CONTROL_HANDOFF: exact-head machine-green on PR #198 at `46655d2ecdc02a3f1698c9fd0b1b14c09f767946` with Pre-Unreal #1484 SUCCESS + Unreal Build #1157 SUCCESS; merged as `3b38698c19a244fde8f2979d73f12cd829576b7f`.
- Active runtime car: SHIRE_AUDIO_IDENTITY.
- UShireAudioSubsystem remains sole runtime audio owner.
- Shire identity targets: birds, breeze/hedges, farm/work, distant laughter, carts, warm interiors, fire/cutlery.
- Runtime source adds a bounded decorative localized-SFX start budget while preserving story-critical cue priority, async loading, weak caching, shared attenuation, ambience/music fades and voice ducking.
- Status: SOURCE-IMPLEMENTED / EXACT-HEAD PRE-UNREAL + UE4.27.2 PROOF PENDING.
- Final audio-bank import, playback/listening, PIE/device/pacing/performance acceptance: PENDING / NOT CLAIMED.

## 2026-09-30 - P1C01 CINEMATIC_CONTROL_HANDOFF active

- Predecessor QUEST_SIDE_ACTIVITY_COHERENCE: exact-head machine-green on PR #197 at `10fa10ac47deed372d3a29c14dd30c1c3b5a5522` with Pre-Unreal #1481 SUCCESS + Unreal Build #1154 SUCCESS; merged as `e926889f9328e238afaffb16f9f9dabf58ce9040`.
- Active runtime car: CINEMATIC_CONTROL_HANDOFF.
- UShireStoryPresentationSubsystem remains presentation-state owner; AStoryPresentationDirector remains transient camera owner; quest/save/world truth ownership is unchanged.
- Scope: unify timed release / skip / chapter handoff onto one exit path so transient presentation cannot leave a stale camera or mutate story state.
- Status: SOURCE-IMPLEMENTED / EXACT-HEAD PRE-UNREAL + UE4.27.2 PROOF PENDING.
- No PIE/device/visual/pacing/performance acceptance is claimed.

## 2026-09-30 - P1C01 QUEST_SIDE_ACTIVITY_COHERENCE active

- Predecessor LIVING_SHIRE: exact-head machine-green on PR #196 at `149c9570c2cbac4295b0b1c41dca5e06f2e7f5bc` with Pre-Unreal #1478 SUCCESS + Unreal Build #1151 SUCCESS; merged as `a478127559ab54f0ec938377a4962e6a75479d36`.
- Active runtime car: QUEST_SIDE_ACTIVITY_COHERENCE.
- UShireQuestSubsystem remains sole quest/story authority.
- Runtime source now adds a bounded current-window activity projection, P1C01 urgency suppression and explicit duplicate-completion rejection.
- Status: SOURCE-IMPLEMENTED / EXACT-HEAD PRE-UNREAL + UE4.27.2 PROOF PENDING.
- No PIE/device/visual/pacing/performance acceptance is claimed.

## 2026-09-30 - P1C01 LIVING_SHIRE source implementation

- CHARACTER_PRESENTATION predecessor closed on PR #195 exact head `24ffa0ddb35756a606fb166d010b1e7ca2940308`: Pre-Unreal #1475 SUCCESS, Unreal Build #1148 SUCCESS, merged as `66caf6168157e0ec171a1e7249ead245e45d8b42`.
- Registered LIVING_SHIRE first in `Docs/WORLD_DETAIL_LEDGER.md`, `Data/P1C01LivingShireChapterV1.json` and Governor DEC-095.
- Added `FShireNPCBehaviorSnapshot` / `BuildBehaviorSnapshot()` so scheduled ambient routine refresh coalesces danger, weather, schedule, anchor, regional mood and emotional state instead of rebuilding context through repeated independent queries.
- Replaced per-NPC full-world `TActorIterator<AShireAmbientNPC>` social scans with `ALivingWorldDirector::GatherActiveAmbientNPCsNear()`, bounded to Director-managed baseline and active micro-event NPCs inside the requested radius.
- Loaded and enforced the existing `max_active_fauna_groups_near_player=2` admission budget before FAUNA micro-events are selected.
- Existing AmbientNPC / interaction / ambient-motion pools remain lifecycle owners; no parallel AI brain or streaming owner was added.
- P1C01 ambient population target remains **18**. No density increase, synchronous heavy load or per-frame global context reconstruction was introduced.
- Current status: **SOURCE-IMPLEMENTED / EXACT-HEAD PRE-UNREAL + UE4.27.2 PROOF PENDING**.
- Not claimed: PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED, PACING-ACCEPTED or PERFORMANCE-ACCEPTED.

## 2026-09-30 - P1C01 CHARACTER_PRESENTATION source implementation

- Predecessor PARTY_AND_SOCIAL_LOOP is exact-head machine-green: PR #194 head `5e4814c9f2ec9acc3bae3df389936c1621bde9e0` passed Pre-Unreal #1472 and Unreal Build #1145, then merged to develop as `584b9522298e04f8a5a3d79e246c5f0483cce7c0`.
- Registered CHARACTER_PRESENTATION before runtime code in `Data/P1C01CharacterPresentationChapterV1.json` and WORLD_DETAIL_LEDGER.
- Added stable `AShireNPC::ProductionCharacterId` so hero rig/asset identity no longer depends on localized `DisplayName`. P1C01 story actors explicitly bind Gandalf Road, Bilbo, Gandalf at Bag End and Sam to stable production IDs.
- Existing `UShireChapterAssetStreamingSubsystem` remains the only skeletal-rig residency owner: soft paths + `FStreamableManager::RequestAsyncLoad`, bounded package availability retry, modular fallback until mesh + AnimBP resolve, URO and rendered-only pose ticking.
- Added story-aware player equipment presentation: Frodo's modular future sword presentation is suppressed inside P1C01 rather than leaking later named gear backward into the Shire chapter.
- No population increase, new AI brain, per-frame asset scan, synchronous heavy production load or crowd Spawn/Destroy path was added.
- Current status: **SOURCE-IMPLEMENTED / EXACT-HEAD PRE-UNREAL + UE4.27.2 PROOF PENDING**.
- Not claimed: PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED, DEFORMATION-ACCEPTED or PERFORMANCE-ACCEPTED.

## 2026-09-30 - P1C01 SHIRE_WORLD_DENSITY runtime car source implementation

- Predecessor mega integration is machine-green: PR #189 exact head `3680ab2fa52b7ebd7ec896ec10d2d2f9a60dd63c` passed Pre-Unreal #1465 and UE4.27.2 Unreal Build #1138, then merged to `develop@64b70c4532a7412a47c031d71bb4f972e7720096`.
- LivingWorld member-local culling and the ambient pawn-cache regression guard therefore have exact-head machine proof on that PR. This is compile/headless-machine evidence, not human PIE/device/visual/performance acceptance.
- First post-mega runtime car: `SHIRE_WORLD_DENSITY`. It adds only geometry/dressing through `ShirePrototypeWorldBuilder::SpawnWorldDensityDetailPass()` and existing zero-Tick `AWorldDetailCluster` HISM ownership.
- Fixed budget: at most 5 cluster actors / 70 non-collision instances across wood piles, ferns, reeds, path markers and fallen logs. Missing production meshes are skipped; no synchronous load is introduced.
- `WorldLifeSaturationPlan` P1C01 ambient population target remains **18**. LivingWorldDirector still owns ambient NPC budgets/pooling; ShireQuestSubsystem still owns story/quest state.
- No quest coordinate, story anchor, crowd cap or chapter topology is changed by this car.
- Current car status: **SOURCE-IMPLEMENTED / EXACT-HEAD PRE-UNREAL + UE4.27.2 PROOF PENDING**.
- Still not claimed: PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED, PACING-ACCEPTED or PERFORMANCE-ACCEPTED.

## 2026-09-30 - W00 automated machine closure + P1C01 maximum-safe mega train V2

- PR #184 exact head `d6ca8aac03f5a1da07609e61e790ddf8faad8eed` passed hosted Pre-Unreal #1435 and full UE4.27.2 Unreal Build #1108, then merged to `develop@4fb15dfff70bfda5a2c023c3d82b3008fb831edc`.
- Exact machine evidence includes editor build, production import, Automation Framework QA, headless startup, chapter audit, route/state roundtrip, warning-debt guard, real Windows package, Runtime Data staging and packaged startup.
- Packaged Data proof: `W00_PACKAGED_DATA_PASS expected=37 verified=37`.
- Packaged runtime-consumption proof: `W00_PACKAGED_RUNTIME_DATA_READ_PASS marker=NPCContext: ready=yes`.
- Packaged startup proof: `W00_PACKAGED_STARTUP_PASS observed=6s`.
- Runner hardware snapshot: Intel i7-6498DU, 8,457,560,064 RAM bytes. This is a hardware snapshot only and is **not DEVICE-TESTED** because representative FPS/frame-time/VRAM acceptance has not been captured.
- Automated W00 machine gates are therefore closed on the exact acceptance head. Human chapter traversal/readability/pacing, real audio playback/mix and target-device performance/visual evidence remain separate gates.
- P1C01 mega train V2 is rebuilt from the merged canonical develop instead of resolving the old #185 conflict wholesale. It selectively preserves the confirmed LivingWorld member-local cull repair, PG-208/209/210/211/212+ guards, source-to-runtime disposition, save-schema audit and the 12-car maximum-safe production program.
- No new runtime expansion car is promoted solely by W00 machine closure; each dependent car still follows Governor prerequisites and its own exact-head UE4 / later Gate 6/7 evidence.
- No new PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made by this record.

## 2026-09-30 - W00 packaged runtime Data-read proof guard

- Remote branch-salvage cleanup is closed machine-wise: the 26 legacy heads are recoverable from `archive/pre-build-salvage-20260930`, and the final cleanup pass reduced persistent refs to `develop`, `main`, and the recovery-only archive before this short-lived validation branch was opened.
- Construction resume is following the Governor's current W00 acceptance order rather than opening a new gameplay feature prematurely.
- `Scripts/verify_packaged_startup.ps1` now requires the packaged executable to emit `NPCContext: ready=yes` in addition to startup/grounding/route markers. This closes the evidence gap between staged/parseable RuntimeDependencies and actual runtime consumption by `UShireNPCContextSubsystem`.
- `Data/W00FinalClosurePlanV1.json` now defines W00-DATA-001 as staging + JSON syntax + packaged runtime consumption.
- Current status: **SOURCE-IMPLEMENTED / EXACT-HEAD CI PROOF PENDING**. No PIE, device, FPS, audio-playback, pacing, or visual acceptance is claimed by this change.

## 2026-09-30 - Final zero-ahead maintenance sweep before construction resume

- PR #180 merged the last orphan-ref closeout after exact-head hosted Pre-Unreal SUCCESS.
- The remaining non-canonical maintenance refs are now limited to the superseded `maintenance/final-prebuild-branch-cleanout-v1` plus this short-lived sweep branch.
- This sweep explicitly queues both refs for guarded deletion; the merged sweep head will also be deleted by DEC-088 exact-head closeout.
- Expected persistent refs after Branch Cleanup: `develop`, `main`, and recovery-only `archive/pre-build-salvage-20260930`.
- After that branch-cleanup SUCCESS, repository hygiene is closed and substantive build work resumes from canonical `develop`.
- Evidence boundary: repository hygiene only. No compile/PIE/device/visual/performance acceptance is claimed.

## 2026-09-30 - Last orphan maintenance ref closeout

- PR #178 merged the final legacy-ref retirement policy before PR #179 could merge; PR #179 therefore became a superseded maintenance branch rather than production work.
- PR #179 exact head `a6b8bc300980bd2e8bc7c0132ea5e8b2d9d25e77` completed the full hosted Pre-Unreal chain successfully, then was closed unmerged after #178 landed first.
- Branch Cleanup for #178 completed SUCCESS and explicitly deleted all 26 archived legacy working refs; its log ended with `deletedExplicit=26`, `keptUnique=1`, `planProtected=3`.
- The only extra live ref after that pass is `maintenance/final-prebuild-branch-cleanout-v1`; it is now explicitly queued for deletion by this final closeout.
- Expected final live refs: `develop`, `main`, and recovery-only `archive/pre-build-salvage-20260930`.
- Evidence boundary: repository hygiene only. No compile/PIE/device/visual/performance acceptance is claimed.

## 2026-09-30 - Final legacy-ref retirement before build resume

- Recovery archive created at `archive/pre-build-salvage-20260930@a47eda59f31352676de44777845fbc01c38d2d0d`.
- The archive commit captures all **26** remaining non-canonical legacy branch heads as commit parents; it is recovery-only and must never become an execution trunk.
- All 26 captured legacy working refs are now explicitly queued for guarded deletion after this maintenance merge.
- Canonical survivors after cleanup are `develop`, `main`, and the recovery-only archive branch.
- Build-resume rule: once Branch Cleanup reports success and the canonical/archive refs remain present, branch cleanup is complete and substantive game construction resumes from `develop`.
- Evidence boundary: repository/process hygiene only; no compile, PIE, device, visual or performance acceptance is claimed.

## 2026-09-30 - Final runner-path and branch-lifecycle reconciliation

- Owner-side cleanup finished with `OLD_C_RESIDUE_EXISTS=False` and `D_RUNNER_EXISTS=True`; the active persistent runner authority remains `D:\\actions-runner` and Warehouse authority remains `D:\\actions-runner\\_warehouse\\ShireJourney`.
- Quick repository audit confirmed current runner/watchdog/service-guard defaults point to D, Warehouse Stage remains self-hosted on the D-backed persistent Warehouse, and hosted Pre-Unreal / Branch Cleanup remain off the UE4 device lane.
- Governor drift is reconciled: REQ-STABILITY-003 / DEC-043 / DEC-047 now describe the current hosted static/admin architecture instead of the retired self-hosted static/admin design.
- DEC-042 is strengthened by DEC-088: every merged temporary branch is closed by exact remote-head SHA deletion first, then guarded zero-ahead pruning. If the remote branch moved after merge, it is preserved as new work.
- The next cleanup run explicitly removes strict ancestor/exact-head duplicate refs while unique production/provenance/material/graphics branches remain preserved for selective salvage.
- Evidence boundary: infrastructure and repository hygiene only. No PIE/device/visual/performance or chapter acceptance is claimed.

## 2026-09-30 - Second branch-hygiene pass

- Eight clearly superseded remote branches are approved for post-merge deletion: duplicate main-entry workflow experiments, obsolete Warehouse diagnostic/supersession repairs, the pre-reconciliation hero skeletal candidate branch, and three stale repair branches.
- Unique production/art/provenance/settings branches are explicitly protected in `preserve_pending_salvage`; branch age alone is not a deletion criterion.
- Evidence boundary: repository hygiene only; no gameplay/PIE/device/visual/performance acceptance is claimed.

## 2026-09-30 - Stale PR branch cleanup authorization

- Closed stale PRs #171, #163, #167, #154, #159, #162 and #125 after live supersession/integration review.
- Branch cleanup plan now explicitly authorizes deletion of their remote heads after this maintenance merge.
- PR #125 runtime changes were checked by current-source symbols before closure: player pawn caching, pooled world interactions/ambient motion, SFX repeat guard and bounded character-rig availability retry are already present on develop.
- PR #154 latest-receipt/supersession behavior is present in the current warehouse audit and regression test.
- Evidence boundary: repository/branch hygiene only; no PIE/device/visual/performance acceptance is claimed.

## 2026-09-30 - Runner root migration C -> D

- Persistent self-hosted runner authority is now `D:\\actions-runner`; persistent Warehouse authority is `D:\\actions-runner\\_warehouse\\ShireJourney`.
- Live GitHub runner proof after the move reported `RUNNER_HEALTH_WORKSPACE_PASS temp=D:\\actions-runner\\_work\\_temp` and `RUNNER_HEALTH_PASS` under the interactive watchdog-owned user session.
- Repository runner/Warehouse defaults were migrated away from active `C:\\actions-runner` assumptions, including chapter source waves, Warehouse trains, watchdog/service guard defaults, and Warehouse Stage explicit paths.
- The old C-side runner is retirement residue only; quarantine preserved the pre-retirement baseline of 28,252 files / 7,604,599,440 bytes before cleanup.
- Evidence boundary: RUNNER ROOT / WORKSPACE / TOPOLOGY RUN-PROVEN. No PIE, packaged gameplay, visual, target-device performance, or chapter acceptance is claimed.

## 2026-09-29 - P1C01 hero skeletal candidate diagnostic repair

- Post-merge P1C01 Frodo/Gandalf skeletal candidate workflow run #1 reached the candidate-build step and failed there; checkout, runner health and PowerShell preflight all passed.
- The candidate runner now prints bounded diagnostic counts and pending/blocked reasons before enforcing candidate coverage thresholds.
- This change does not weaken candidate QC or promote generic FBX files; it only exposes why the persistent Warehouse did not satisfy the first candidate-run threshold.
- Evidence boundary: DIAGNOSTIC TOOLING CHANGE / exact-head static validation pending. No rig import, PIE, device, visual or performance acceptance is claimed.


## 2026-09-29 - F2-04 Road & Helm's Deep Prep Maximum-Safe Source V1

- F2-04 is now the active Part II source/preparation wave after merged F2-03 Edoras.
- Canonical chapter contract: refugees move under threat; defenses are prepared; optional window is escort/rescue/armory/wall prep/civilians; locked postcondition is Uruk army arrives.
- Permanent full-journey governance applies: preserve road/refugee/fortress/civilian/preparation detail rather than jumping directly into siege combat.
- Data/F204RoadHelmsDeepPrepMaximumSafeMegaSourceV1.json defines 36 categories, 19 landmark-tagged categories and 9 source banks under a 34,000-candidate fair-share ceiling.
- Source success requires at least 16 populated landmark categories and 8 ready banks.
- F2-05 siege phases/breach/retreat/mounted sortie/dawn counterattack remain outside this pack.
- runtime_consumers=[] and runtime_mapping_status=NOT_ASSIGNED_DO_NOT_INVENT remain hard boundaries.
- PG-206 protects canon, chapter boundaries, source breadth, format rules, warehouse reserve and runtime-ID safety.
- DEC-086 owns this source wave.
- P1C01 remains the sole runtime-changing chapter lane; Frodo/Gandalf skeletal-candidate preparation can continue in parallel as source/QC work.
- Evidence boundary: SOURCE-IMPLEMENTED / STATIC-VALIDATION PENDING. No runtime integration, PIE, device, visual, pacing or performance acceptance is claimed.

## 2026-09-29 - P1C01 Frodo/Gandalf skeletal candidate wave V1

- The active P1C01 character-production path now includes a bounded Frodo/Gandalf skeletal candidate discovery/QC wave.
- This wave is intentionally source/intake/QC only: it searches the already authorized staged character packs for real FBX candidates and ranks them into Frodo/Gandalf rig-family pools.
- No candidate defaults to READY_FOR_IMPORT. Skeleton hierarchy, skin weights, retarget, deformation, animation coverage, materials, sockets and LOD/cull remain explicit QC gates.
- Runtime handoff remains /Game/Production/Characters/Rigs/<Character>/ with SK_<Character> + ABP_<Character>_Locomotion, soft references and FStreamableManager asynchronous loading.
- Existing modular characters remain visible until the full rig pair resolves; ShireNPCContextSubsystem and LivingWorldDirector ownership is unchanged.
- DEC-085 owns this visible-character priority wave.
- Evidence boundary: SOURCE/INTAKE/QC TOOLING IMPLEMENTED / EXACT-HEAD STATIC VALIDATION PENDING. No imported rig, PIE, device, visual or performance acceptance is claimed.

## 2026-09-29 - F2-03 Edoras Maximum-Safe Source V1

- F2-03 Edoras is the next Part II source-production wave; runtime identity remains unassigned.
- Source-verified chapter contract: Theoden restored; political and military crisis clarified; optional window is court exploration, stables, equipment and social scenes; locked postcondition is Rohan evacuates toward Helm's Deep.
- Permanent story governance applies: Edoras is not reduced to a single restoration set-piece. Compatible settlement, Meduseld/court, horse/stable, relationship, muster and departure detail remains in source scope.
- Data/F203EdorasMaximumSafeMegaSourceV1.json defines 32 categories, 20 landmark-tagged categories and 8 source banks under a 32,000-candidate fair-share ceiling.
- Source success requires at least 14 populated landmark categories and 7 ready banks.
- F2-04 road/refugee escort/Helm's Deep preparation and F2-05 battle resolution remain outside this pack.
- runtime_consumers=[] and runtime_mapping_status=NOT_ASSIGNED_DO_NOT_INVENT remain hard boundaries.
- PG-204 protects canon, breadth, format rules, warehouse reserve and runtime-ID safety.
- DEC-084 owns this F2-03 source wave.
- Evidence boundary: SOURCE-IMPLEMENTED / STATIC-VALIDATION PENDING. No runtime integration, PIE, device, visual, pacing or performance acceptance is claimed.

## 2026-09-29 - F2-02 exact-head static repair

- Pre-Unreal #1401 reached the project-structure validator and failed because PG-203 requires every F2-02 tooling-only path to be ignored in both Unreal push and pull-request filters, while the reconciliation branch contained each path only once.
- The Unreal workflow filter is corrected so all three F2-02 tooling paths are present in both filter lists.
- This is a CI routing repair only; F2-02 story/source scope and runtime boundaries are unchanged.
- Evidence boundary: fresh exact-head static validation is pending on the repaired head. No runtime or human acceptance promotion is claimed.

## 2026-09-29 - F2-02 reconciled after permanent story/source governance

- F2-02 Fangorn & Gandalf Returned source architecture is reconciled onto the post-PR #164 governance baseline.
- Canonical outcome remains: Gandalf leads the hunters to Edoras.
- Source pack remains 40 categories, 20 landmark categories, 9 banks, 32,000 candidate ceiling, fair-share scheduling and minimum 8 ready banks / 16 landmark categories.
- Part II runtime identity remains unassigned: runtime_consumers=[] and runtime_mapping_status=NOT_ASSIGNED_DO_NOT_INVENT.
- The permanent story contract now applies to this pack: no story shortcuts, no silent omission, and compatible Tolkien detail may enrich playable content without changing locked film outcomes.
- Governor decision is DEC-083; DEC-081 and DEC-082 remain reserved for the permanent full-journey story/source rule and Arabic localization rule.
- PG-203 and the F2-02 source runner/workflow are present on this reconciliation branch.
- Evidence boundary: SOURCE / GOVERNANCE / TOOLING ONLY. Fresh exact-head Pre-Unreal is required on this reconciled head. No PIE, device, visual, pacing or performance acceptance is claimed.

## 2026-09-29 - permanent full-journey story/source and Arabic localization governance

- Owner direction is captured as permanent repository governance: the game is experience-first, not a shortened recap. Timeline is navigation/order only; film/screenplays lock film-driven continuity; Tolkien supplies compatible deeper detail and book-only events; Sources 02-11 drive production.
- Compatible Tolkien material omitted/compressed by the films is a playable-content candidate when it preserves locked outcomes, chronology and character knowledge.
- Zero-silent-omission disposition tracking is now part of the source contract for F1-01 through F3-07 chapter packets.
- Localization product rule is fixed: English VO; Arabic subtitles/objectives/menus/settings/HUD/tutorial guidance; canonical Middle-earth map location labels remain in English; proper RTL/shaping/wrapping/font support is required.
- New-developer entry is strengthened so story/source routing is discoverable from repository onboarding without chat history.
- `Scripts/new_developer_onboarding.ps1` now exposes the source index/story rule/localization rule. This is tooling/onboarding code only; no gameplay runtime behavior or chapter maturity is promoted.
- Evidence boundary: **SOURCE/GOVERNANCE/ONBOARDING IMPLEMENTED ON CANDIDATE BRANCH; exact-head static validation required before merge.** No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made.

## 2026-09-29 - F2-01 Three Hunters / Captives Maximum-Safe Source V1

- F2-01 is now the active **Part II maximum-safe source-production wave** after F1-08.
- Canonical mission scope was checked against the supplied Mission, Story and World PDFs: Aragorn/Legolas/Gimli pursue the Uruk-hai; Merry/Pippin escape into Fangorn; locked postcondition is **Paths converge around Fangorn/Rohan**.
- Safe optional focus is tracking, stamina and evidence reading.
- The pack explicitly excludes F2-02 Treebeard/Ent mobilization and Gandalf-return resolution.
- No Part II runtime ID is invented. `runtime_consumers=[]` and `runtime_mapping_status=NOT_ASSIGNED_DO_NOT_INVENT` remain hard guardrails until a dedicated runtime-ID migration/mapping decision exists.
- `Data/F201ThreeHuntersCaptivesMaximumSafeMegaSourceV1.json` defines **38 categories**, **17 landmark-oriented categories**, **8 source banks**, **28,000 total candidate ceiling**, **2,600/category hard ceiling**, fair-share scheduling and landmark bonus 8.
- Source banks cover Rohan pursuit, tracking/evidence, Uruk trail pressure, captive escape, Fangorn threshold, hunter characters/animation, audio/weather/foley and convergence handoff.
- Source success requires at least **14 populated landmark categories** and **7 ready banks**.
- Fangorn use is threshold-only in F2-01: dense trunks, roots, mist and disorientation setup without opening later Ent-state content.
- `PG-202` protects canon outcome, later-chapter exclusions, candidate breadth, bank minimums, FBX-only animation, BMP rejection, inventory gate and the unassigned Part II runtime-ID boundary.
- Exact-head validation and heavy source execution are **pending**.
- Evidence boundary: **SOURCE-IMPLEMENTED / STATIC-VALIDATION PENDING**. No runtime integration, PIE, device, visual, pacing or performance acceptance is claimed.

## 2026-09-29 - F1-08 Amon Hen / Breaking of the Fellowship Maximum-Safe Source V1

- F1-08 is now the active **maximum-safe source-production wave** under `DEC-078`; legacy runtime consumer remains `P1C08` and runtime integration is still blocked behind P1C07 Gate 6/7.
- Canonical mission scope was rechecked against the supplied Mission, Story, Character and World PDFs plus the supplied Fellowship screenplay. Locked outcome remains: Boromir falls; Merry/Pippin are captured; Frodo chooses Mordor; Sam follows; **three parallel campaigns begin**.
- Boromir's character guardrail is preserved: his fall is tragic/redemptive after temptation, not generic villainization.
- `Data/F108AmonHenBreakingMaximumSafeMegaSourceV1.json` defines **34 categories**, **18 landmark-oriented categories**, **7 source/streaming banks**, **24,000 total candidate ceiling**, **2,400/category hard ceiling**, and **landmark score bonus 8**.
- Candidate selection uses a fair-share effective per-category budget so early broad categories cannot consume the whole pack before combat/capture/departure/aftermath banks receive coverage.
- F1-08 banks cover calm arrival, decision/high-seat route, Uruk attack, Boromir defense/aftermath, capture/pursuit, Sam/Frodo departure and campaign-split aftermath.
- Source success requires at least **14 populated landmark categories** and **6 ready banks**.
- Amon Hen landmark identity now distinguishes the F1-07 river approach from the F1-08 break state: ancient high-seat/stone-route focal vista above the Parth Galen river shore, with calm/attack/aftermath state variants.
- Tolkien material is used only as compatible landscape/landmark support (high-seat/watchwork, old stone route/stairs, Parth Galen, Rauros/Tol Brandir sightline language); the project film-first mission outcome remains authoritative.
- `PG-201` guards canon outcome, Boromir guardrail, 34-category breadth, bank coverage, landmark minimums, FBX-only animation, BMP rejection, inventory gate, fair-share scheduling and tooling isolation from the Unreal build lane.
- Exact-head validation and heavy source execution are **pending** for this branch.
- Evidence boundary: **SOURCE-IMPLEMENTED / STATIC-VALIDATION PENDING**. No UE integration, PIE, device, visual, pacing or performance acceptance is claimed.

## 2026-09-29 - Adaptive Maximum Safe Production Mode V1

- Owner direction is now permanent project policy through `DEC-078` and `REQ-PROD-011`: use the already-built CI/warehouse/streaming/governance infrastructure to maximize real production throughput instead of advancing in tiny isolated increments.
- `Data/MaximumSafeProductionModeV1.json` is the machine-readable execution contract. It defines parallel preparation lanes, the single runtime-changing lane, hard stops, quarantine/continue behavior, runtime residency policy and the ordered next production waves.
- `Data/WholeGameProductionExecutionQueueV1.json` now runs in `ACTIVE_MAXIMUM_SAFE_PREPARATION_RUNTIME_SERIALIZED` mode. Persistent warehouse mutation remains single-writer; source/index/material/audio/character/world-prep lanes may proceed independently when dependencies permit.
- `Data/MasterExecutionRoadmap.json` is reconciled away from stale W00/PR#67 control state. Current mode is P1C01 runtime closure plus parallel whole-game preparation, with F1-08 as the next maximum-safe mega source wave after F1-07.
- Live Warehouse #286 evidence proved the receipt-supersession repair worked: `WAREHOUSE_INVENTORY_AUDIT_PASS payloadFiles=18697 bytes=6688457009 receipts=14 receiptRecords=667 activeRecords=239 superseded=428 duplicateGroups=0`.
- Warehouse #286 later failed in `run_warehouse_saturation_train.ps1` because an empty verified set under StrictMode exposed no `.Sum` property. This is a reporting/tooling defect, not an inventory-capacity failure.
- Saturation reporting now uses an empty-safe Int64 sum helper; `Scripts/test_warehouse_saturation_empty_sum.ps1` is wired into Pre-Unreal so an empty source lane must report `verified_bytes=0` instead of stopping the train.
- Existing safety boundaries remain unchanged: FBX-only animated production assets, PNG/TGA production textures, no BMP, 6 GiB warehouse reserve, soft/async heavy runtime loading, pooled crowds, ISM/HISM + LOD/culling, predecessor Gate 6/7 and target-device profiling.
- Evidence boundary: **SOURCE-IMPLEMENTED / exact-head validation pending** for this production-mode wave. Warehouse inventory clean is evidenced at the #286 audit step; the full Warehouse #286 workflow was not successful because of the later saturation-report defect. No PIE/device/visual/pacing/performance acceptance is claimed.

## 2026-09-29 - F1-07 Lórien & Anduin Landmark Mega Source V1

- Canonical F1-07 source architecture is now registered for legacy runtime consumer `P1C07`.
- Canon boundary is explicit: F1-07 prepares grief/recovery, rest/gifts, river journey, Lothlórien and the Anduin/Amon Hen approach; **Breaking of the Fellowship / Uruk-attack resolution remains F1-08**.
- `Data/F107LorienAnduinLandmarkMegaSourceSuperpackV1.json` defines **26 categories**, an **18,000 total candidate ceiling**, **2,000/category**, **landmark score bonus 7**, and at least **10 populated landmark categories** before source success.
- Lothlórien identity centers a golden/luminous sanctuary with vertical flets and organic bridges. Anduin identity centers river-axis readability, cliffs, ancient stone monuments and a readable Amon Hen approach.
- `Data/Part1LandmarkIdentityPlanV1.json` now records `LOTHLORIEN` and `ANDUIN_F107_APPROACH` without renumbering runtime chapters.
- `Scripts/run_f107_lorien_anduin_landmark_mega_source.ps1` reuses the proven inventory-gated shared-stock index architecture; animated candidates remain FBX-only and BMP is blocked.
- `PG-200` guards size, landmark breadth, source formats, inventory gate, F1-08 exclusion, workflow contract and Unreal tooling isolation.
- Governor `DEC-077` records the durable scope/architecture contract.
- Heavy source execution remains blocked until persistent warehouse inventory is clean. P1C07 runtime integration remains predecessor Gate 6/7 gated.
- Evidence boundary: **SOURCE-IMPLEMENTED / exact-head static validation pending**. No UE runtime, PIE, device, visual, pacing or performance acceptance is claimed.

## 2026-09-29 - Warehouse receipt supersession semantics

- Warehouse #285 isolated the current inventory blocker to `ambientCG\PLASTER\Plaster007_2K-PNG.zip`: historical batch `WAREHOUSE_AMBIENTCG_P1C01_V1` declares the old payload hash while the refreshed current payload is represented by the newer trilogy-foundation receipt path.
- `Scripts/audit_warehouse_inventory.ps1` now resolves **one active provenance record per normalized payload path**. Newer parseable receipt provenance is active; older receipts stay preserved as `superseded` history instead of being treated as simultaneous hash authorities.
- Windows path case/slash variants are normalized before grouping. Active-record hash, missing-reference and license checks remain fail-closed.
- The inventory report now records total/active/superseded provenance counts and the old-to-new receipt relationship without rewriting or deleting historical receipts.
- New `Scripts/test_warehouse_inventory_receipt_supersession.ps1` proves that a stale V1 hash is superseded by a valid newer V2 receipt, then proves a tampered active V2 payload still fails.
- Pre-Unreal runs this synthetic regression on `windows-latest`.
- Governor `DEC-076` records the permanent provenance rule.
- Evidence boundary: **SOURCE-IMPLEMENTED / exact-head Pre-Unreal pending / persistent warehouse rerun pending**. Warehouse clean state and P1C01 closure continuation are not yet claimed.

## 2026-09-29 - Interactive CI orchestration anti-hang rule

- PR #153 is merged on develop; exact-head Pre-Unreal #1379 and Unreal #1095 both completed SUCCESS.
- The recent apparent chat hangs were caused by repeated interactive polling while long GitHub Actions jobs were still running, not by a proven Unreal deadlock.
- Governor `DEC-075` now limits repeated status polling for the same long-running workflow inside one interactive response.
- After bounded checks, continuation moves to the scheduled automation/next run while independent safe work may continue on separate branches.
- Exact-head validation, Gate 6/7 and evidence standards are unchanged.
- Evidence boundary: **ORCHESTRATION FIX RECORDED**; no new runtime/device/visual/performance acceptance is claimed.

## 2026-09-29 - F1-06 landmark scoring strengthened

- F1-06 landmark categories now use a manifest-driven **landmark score bonus = 6** instead of a fixed small inline boost.
- The source indexer therefore prioritizes strong landmark candidates ahead of generic dressing when keyword evidence is otherwise comparable.
- `PG-199` now rejects a landmark score bonus below 6 and guards the runtime marker that consumes the configured bonus.
- Duplicate older PR #152 was closed without merge; PR #153 is the single F1-06 path and is based on current develop with warehouse diagnostics preserved.
- Evidence boundary: **SOURCE-IMPLEMENTED / fresh exact-head checks pending / no visual acceptance claimed**.

## 2026-09-29 - PG-199 landmark/F1-06 regression guard

- `PG-199` now statically guards the Part I landmark identity plan and F1-06 superpack.
- It prevents silent reduction of the 16,000 total candidate ceiling, 1,800/category throughput, FBX-only animated rule, BMP block, inventory-clean gate, minimum landmark coverage, required Caradhras/Moria landmark categories, and tooling-only Unreal filter contract.
- Evidence boundary remains **SOURCE-IMPLEMENTED / exact-head validation pending**.

## 2026-09-29 - Part I Landmark Identity + F1-06 Caradhras/Moria Mega Source V1

- New `Data/Part1LandmarkIdentityPlanV1.json` defines recognizable visual anchors for Shire/Hobbiton, Bag End, Bree, Weathertop, Rivendell, Caradhras and Moria.
- The landmark rule is source/visual architecture: each production region must expose at least one dominant silhouette/vista or interior focal vista supporting navigation and cinematic continuity.
- Low-spec landmark strategy prioritizes composition, silhouette, lighting/fog hierarchy, critical-vista preloading, LOD/HLOD or simplified distance proxies, and instanced repeated dressing over brute-force geometry.
- Canonical **F1-06 Caradhras & Moria** now has `Data/F106CaradhrasMoriaLandmarkMegaSourceSuperpackV1.json` with **24 categories**, **16,000 total candidate ceiling** and **1,800/category**.
- Runtime consumers remain legacy `P1C05 + P1C06` under the recorded F1/P1 reconciliation.
- Caradhras identity centers high mountain-pass ridge readability under snow/wind/low visibility and storm escalation.
- Moria identity centers monumental entrance/hall-axis geometry, routefinding landmarks, tomb-alert space and Balrog-escape visual hierarchy.
- `Scripts/run_f106_caradhras_moria_landmark_mega_source.ps1` produces category indexes plus a separate landmark coverage report and fails if the configured landmark-source minimum is not populated.
- Heavy F1-06 execution remains **WAREHOUSE-INVENTORY-GATED** while the current hash mismatch is unresolved.
- Governor `DEC-073` and `DEC-074` record these contracts.
- Evidence boundary: **SOURCE-IMPLEMENTED / exact-head validation pending / no visual acceptance claimed**.

## 2026-09-29 - Warehouse hash-mismatch diagnostics hardening

- P1C01 Closure Pack #2 reached inventory audit after seven successful cars, then hard-stopped on `hashMismatch=1` with no missing references, license mismatch, dangerous payload or bad receipt count.
- Existing `warehouse_inventory_latest.json` already contains detailed mismatch rows, but the workflow log exposed only aggregate counts.
- `Scripts/audit_warehouse_inventory.ps1` now emits bounded exact mismatch evidence (provider, batch, asset, kind, path, declared hash, actual hash) before failing.
- Missing-reference and license-hash mismatch evidence are also emitted, capped at 20 rows per defect class.
- No auto-delete, auto-quarantine or receipt rewrite is introduced.
- Governor `DEC-072` records the evidence-first repair rule.
- Evidence boundary: **SOURCE-IMPLEMENTED / mismatch itself unresolved until rerun evidence identifies the record**.

## 2026-09-29 - F1-05 Rivendell & Fellowship Mega Source Superpack V1

- Canonical scope: **F1-05 Rivendell & Fellowship**; legacy runtime consumer **P1C04**.
- Critical path: Council chooses destruction of the Ring; Fellowship forms. Locked postcondition: Nine depart.
- Rivendell world grammar: stone/wood integration, waterfalls, layered terraces; lore/relationships/equipment/council transition; arrival-wounded/Fellowship-formed variants.
- New manifest defines **20 categories**, **12,000 total candidate ceiling**, **1,500/category**.
- Coverage includes architecture/terraces, waterfalls/river, gardens, interiors, Council space, lore/library, equipment/armory, Fellowship characters/animations, Elven population, relationship scenes, healing/recovery, sanctuary audio/lighting, traversal, mounts, cinematic dressing, departure support, fauna and systemic interactions.
- Heavy execution is inventory-clean gated because P1C01 Closure #2 reported `hashMismatch=1`.
- Animated candidates remain FBX-only; BMP blocked; shared-stock indexing avoids multi-GB duplication.
- Governor `DEC-071` records the permanent contract.
- Runtime integration remains **GATED**.
- Evidence boundary: **SOURCE-IMPLEMENTED / exact-head validation pending / heavy workflow not yet authorized until inventory clean**.

## 2026-09-29 - F1-04 Bree & Weathertop Mega Source Superpack V1

- New source-preparation lane registered for canonical **F1-04 Bree & Weathertop**, consumed by legacy runtime chapters **P1C02 + P1C03** under the existing F1/P1 reconciliation.
- Canonical story boundary remains: Aragorn becomes guide; Ring use increases danger; Frodo is wounded; locked postcondition is the party racing for Rivendell.
- Bree production grammar: timber/stone, rain, gates, crowded inn; social stealth, supplies, rumors and pursuit pressure; night-arrival/departure variants.
- Weathertop production grammar: ruined hilltop watchtower, ancient stone ring, exposed skyline; camp tension and defensive encounter support; calm-approach/night-attack variants.
- `Data/F104BreeWeathertopMegaSourceSuperpackV1.json` defines 16 source categories with a total candidate ceiling of 9000 and per-category ceiling of 1200.
- `Scripts/run_f104_bree_weathertop_mega_source.ps1` indexes shared warehouse stock without duplicating payloads; animated categories accept FBX only and BMP textures are blocked.
- `.github/workflows/f104-bree-weathertop-mega-source.yml` provides an isolated 180-minute source-preparation lane with exact-head checkout, runner-health gate and PowerShell syntax preflight.
- F1-04 tooling-only paths are excluded from expensive Unreal validation.
- Governor `DEC-070` records the permanent architecture/scope contract.
- Runtime integration for P1C02/P1C03 remains **GATED behind predecessor acceptance**.
- Evidence boundary: **SOURCE-IMPLEMENTED / exact-head validation pending**. No PIE/device/visual/performance acceptance is claimed.

## 2026-09-29 - Develop production-train failures isolated and repaired in source

- Develop merge head `d012f4c68f4e9d83b4b8ec4043b5df06c7a4d9a0` retained green core validation: Pre-Unreal #1363 SUCCESS and Unreal #1085 SUCCESS.
- P1C01 Chapter Closure Pack #1 fast preflight passed with `cars=15`, ~23.3 GiB free and 6 GiB reserve, then the first storage car incorrectly hard-failed because `$LASTEXITCODE` had never been initialized after a pure PowerShell scriptblock.
- Warehouse #283 prepared `8` material sources, created local generated commit `ef65959`, then failed during generated-branch remote-head lookup. The lookup used native `git ls-remote` inside a truncating PowerShell pipeline before checking the native exit code.
- Part I Chapter Preparation Train #1 reached `chapters=7` and ignored `2964` blocked-format stock entries as designed, then Windows PowerShell 5.1 raised `Argument types do not match` while embedding a generic `List[object]` into the ordered report.
- Source repairs now provide deterministic child-process exit handling, bounded non-pipelined remote lookup retries, and explicit `ToArray()` candidate materialization.
- Governor `DEC-069` and Pre-Unreal `PG-196` lock the regression contract.
- Sequential Chapter Queue #1 was SUCCESS and correctly skipped P1C02 source release because P1C01 Gate 6/7 is not ACCEPTED.
- Evidence boundary: **SOURCE-IMPLEMENTED / rerun validation pending**. No PIE/device/visual/performance acceptance is claimed.

## 2026-09-29 - #1082 direct-PID/CIM stale-commandlet recovery refinement

- Unreal #1082 proved the stale CI commandlet still survived `Stop-Process -Force` and `taskkill /T /F`.
- The blocker remained PID 14144, `UE4Editor-Cmd.exe` running the repository's unattended `Automation RunTests ShireJourney.QA;Quit` command against the active ShireJourney workspace under the same interactive owner.
- Recovery now avoids tree-mode as the first Windows fallback because the commandlet's recorded parent is already dead. The sequence is now: `Stop-Process -Id -Force` -> direct `taskkill /PID <pid> /F` -> `Win32_Process.Terminate` via CIM, with explicit result markers.
- The recovery path remains available only after the previously recorded workspace/project/unattended/recognized-commandlet/same-owner/orphan/age proof passes.
- Interactive `UE4Editor` remains protected from kill-by-name recovery.
- Evidence boundary: **SOURCE-IMPLEMENTED / fresh exact-head validation pending**.

## 2026-09-29 - #1358/#1080 follow-up: proven stale CI commandlet + bounded tree recovery

- Pre-Unreal #1358 failed only at legacy `PG-015` because that validator still expected the historical editor-only wait implementation.
- Unreal Build #1080 produced concrete blocker identity for PID 14144: `UE4Editor-Cmd.exe`, owner `IDEAPAD320\user`, session 2, age ~4699 seconds, command line running the repository's unattended `Automation RunTests ShireJourney.QA;Quit` against the active ShireJourney workspace.
- The parent PID reported by the process snapshot was no longer alive, satisfying the stale/orphan branch of the bounded recovery contract.
- Initial `Stop-Process -Force` did not remove PID 14144 within the original 750 ms window; the source repair now waits longer and uses `taskkill /PID <pid> /T /F` only as a fallback after the same workspace/project/unattended/recognized-commandlet/same-owner/orphan/age proof succeeds.
- Interactive `UE4Editor` is still never terminated by name.
- `PG-015` now recognizes the shared editor+commandlet waiter and `PG-195` requires same-owner proof plus the bounded taskkill fallback marker.
- Evidence boundary: **SOURCE-IMPLEMENTED / fresh exact-head validation pending**. This is not PIE/device/visual/performance acceptance.

## 2026-09-29 - Continuous Part I train + Unreal #1068 root repair

- Owner granted standing authorization for safe routine reversible production work without repeated "continue" prompts; real login/purchase/licensing/canon/destructive/human-acceptance boundaries still require owner action.
- Unreal Build #1068 compiled `ShireJourneyEditor` successfully, then failed before import on `PRODUCTION_IMPORT_PREFLIGHT_EDITOR_RUNNING pids=14144`.
- Root cause in the CI contract: `ci_wait_for_unreal_editor.cmd` observed only `UE4Editor` while production-import preflight observed `UE4Editor` and `UE4Editor-Cmd`. A false-clear path therefore existed for commandlets.
- New `Scripts/wait_for_unreal_processes.ps1` observes both process families and emits PID/PPID/session/owner/age/command-line evidence. It never kills an interactive editor by name; bounded stale-commandlet recovery requires workspace ownership, unattended recognized CI commandlet, age threshold and no live parent.
- `preflight_production_asset_import.ps1` now emits the same ownership diagnostics when a blocker survives.
- `PG-195` statically guards this process-ownership contract.
- Part I downstream preparation is now represented by `Data/Part1SequentialRuntimeChapterTrainV1.json` and `Scripts/run_part1_runtime_chapter_prep.ps1`.
- Canonical source mission IDs remain F1-01..F1-08; existing runtime P1C01..P1C08 IDs remain legacy implementation boundaries. Current reconciliation: P1C01 spans F1-01/F1-02/F1-03; P1C02+P1C03 split F1-04; P1C04 maps F1-05; P1C05+P1C06 split F1-06; P1C07 maps F1-07; P1C08 maps F1-08.
- `.github/workflows/part1-chapter-preparation.yml` prepares shared-stock candidate indexes for P1C02-P1C08 without duplicating warehouse payloads.
- Runtime remains serialized. P1C01 is still active; P1C02 may open only after P1C01 Gate 6/7 becomes genuinely ACCEPTED.
- Governor decisions `DEC-066`, `DEC-067` and `DEC-068` record these rules.
- Evidence boundary: **SOURCE-IMPLEMENTED / fresh exact-head Pre-Unreal + Unreal validation pending**. No new PIE/device/visual/pacing/performance acceptance is claimed.

## 2026-09-29 - Governor sync: sequential two-chapter queue + systemic reactivity direction

- `DEC-064` now records the sequential production queue: **P1C01 remains the sole active runtime closure chapter; P1C02 Shadow of the Past may prepare source/warehouse work in advance but runtime integration stays closed until the official P1C01 Gate 6/7 acceptance record is ACCEPTED.**
- Expected waiting state before that gate: `SEQUENTIAL_CHAPTER_QUEUE_WAIT`; waiting is not a workflow failure and does not imply P1C02 runtime progress.
- `DEC-065` now records the durable production direction: **AAA Visual Quality + Systemic Reactivity + Intelligent NPCs + Living World + Strict Optimization**.
- The new systemic-reactivity direction extends existing ownership (`ALivingWorldDirector`, `UShireNPCContextSubsystem`, `UShireQuestSubsystem` and world-router committed context). It explicitly rejects a second parallel world/NPC brain.
- The identified future gap is a bounded environmental reaction contract for supported trees/foliage, water, doors/tools/props, fauna and NPC observers. Runtime implementation remains deferred behind the active P1C01 closure/integration sequence and target-device gates.
- Documentation/governance status: **SOURCE-IMPLEMENTED / NOT ENGINE-VALIDATED BY THIS DOC CHANGE**.
- No PIE, device, visual, pacing or performance acceptance is created by these records.

## 2026-09-28 - Pre-Unreal #1332 seven-failure root fix

- Pre-Unreal #1332 passed the repository-wide PowerShell parser gate: `POWERSHELL_SYNTAX_PASS files=47 errors=0`.
- It then failed seven static contracts. Five were watchdog service-guard symbols removed by the earlier clean-source restoration; one was the new closure preflight missing from Unreal `paths-ignore`; one was PG-193 checking a doubly escaped workflow path literal.
- The watchdog is now rebuilt from the clean single-body source with continuous service exclusion restored: `ServiceGuardPath`, `Invoke-ServiceOwnershipGuard`, `Invoke-RunnerServiceGuard`, and `SHIRE_RUNNER_WATCHDOG_SERVICE_GUARD_TRIGGER`. The guard executes at boot and every watchdog loop.
- `Scripts/preflight_p1c01_chapter_closure_pack_v2.ps1` is now excluded from Unreal Build in both push and PR filters.
- PG-193 now checks the real `test_powershell_syntax.ps1` workflow reference.
- Unreal Build #1054 on the previous exact head completed **SUCCESS** after the new production-import preflight/retry changes; this does not validate the newer static fixes above.
- Current maturity: **SOURCE-FIXED / EXACT-HEAD PRE-UNREAL RE-RUN PENDING / PR #145 NOT MERGED**.

## 2026-09-28 - Red CI failures root-caused and architecture split

- Pre-Unreal #1325 reached the new PowerShell parser gate successfully (`POWERSHELL_SYNTAX_PASS files=45 errors=0`) and then failed on PG-168 because the normal Warehouse workflow had been changed from its proven `cancel-in-progress: true` contract.
- Root fix: the normal Warehouse workflow is restored to **60 minutes + cancellable**, while the large P1C01 Closure Pack moves to a dedicated `p1c01-chapter-closure.yml` workflow with its own concurrency group, **180-minute timeout**, and **cancel-in-progress: false**.
- A cheap `preflight_p1c01_chapter_closure_pack_v2.ps1` now validates required scripts, parses the closure PowerShell set, validates child JSON manifests, and checks the disk reserve before any heavy acquisition car starts.
- Unreal Build #1047 compiled `ShireJourneyEditor` successfully. Production import then reported `376 files, 0 failures`, but UE emitted a file-system save failure for `Content/Production/Textures/T_Cloth_Green.uasset` and the workflow correctly stopped.
- The log does **not** prove whether that file was read-only or exclusively locked. DEC-062 therefore adds a measured preflight: no active editor process, write/delete probe, tracked-vs-untracked protection, read-only repair only for untracked generated uassets, and exclusive write-open checks. A save/delete-class importer failure gets exactly one bounded retry after re-preflight; all other importer failures fail immediately.
- Current maturity: **SOURCE-REPAIRED / ROOT-CAUSE GUARDS IMPLEMENTED / EXACT-HEAD PRE-UNREAL + UNREAL RE-RUN PENDING / NO PIE OR DEVICE CLAIM**.

## 2026-09-28 - PR #145 root-cause hardening after Pre-Unreal #1318

- Pre-Unreal #1318 **FAILED** at the new repository-wide PowerShell parser gate. This is expected fail-closed behavior: the new guard found real syntax corruption before merge.
- It found two source defects: a duplicated tail in `export_p1c01_material_source_branch.ps1`, plus an older duplicated/corrupted `runner_watchdog.ps1`.
- The exporter duplicate tail is removed. The watchdog is restored from exact historical commit `1066cf022723fcdef9bfac66519f5b0f9c1e03a4`, the newest inspected clean watchdog revision retaining later stale-worker protection.
- DEC-060 records the watchdog restoration provenance; DEC-059 parser coverage remains active.
- Maximum-throughput execution is hardened further: Warehouse Stage timeout is now 180 minutes and `cancel-in-progress=false`, so a large closure pack is allowed to finish while newer pushes queue instead of killing the active train.
- Current PR #145 maturity after these fixes: **SOURCE-REPAIRED / EXACT-HEAD PRE-UNREAL RE-RUN PENDING / WAREHOUSE V2 EXECUTION PENDING / UE IMPORT NOT CLAIMED**.

## 2026-09-28 - Warehouse #282 parser failure converted into a permanent prevention gate

- Develop `0adc090f1caa92425322ac15d44b08b031f2ece0` passed Pre-Unreal #1317, but Warehouse #282 failed before material execution because `Scripts/export_p1c01_material_source_branch.ps1` contained an unterminated PowerShell expression/string around the explicit remote-SHA lease block.
- This exposed a validation gap: Pre-Unreal checked policy/semantic markers but did not parse all PowerShell scripts.
- The exporter publish block is repaired on the active P1C01 Closure Pack V2 branch.
- DEC-059 adds `Scripts/test_powershell_syntax.ps1`, which recursively parses every `Scripts/**/*.ps1` with `System.Management.Automation.Language.Parser` on the hosted Windows Pre-Unreal lane and fails with file/line/column details on any parser error.
- The parser guard is tooling-only and is excluded from Unreal Build triggers.
- Current maturity for this repair: **SOURCE-FIXED / EXACT-HEAD PRE-UNREAL PROOF PENDING / WAREHOUSE RE-RUN PENDING**.

## 2026-09-28 - P1C01 Chapter Closure Mega Pack V2 launched

- DEC-058 encodes maximum P1C01 source throughput while keeping raw Warehouse, Git/LFS promotion and UE import as separate bounded layers.
- One closure pack covers 37 Poly Haven assets, 17 ambientCG search lanes, 17 Quaternius packs, 12 Kenney packs, 8 KayKit packs and 17 OpenGameArt assets.
- Internal promotion selector ceiling is 187 candidates across surfaces, architecture/props, nature, audio, fauna and character/animation support.
- Material closure wave expands from 16 to 26 explicit Shire/Bag End materials. Generated-source promotion remains bounded at 48 MiB/source and 640 MiB/batch with minimum 18 exported items.
- Closure Pack V2 enforces a 6 GiB free-disk reserve, never deletes original Warehouse payloads for space, and quarantines provider/asset/source failures while allowing independent cars to continue.
- Overlapping legacy P1C01 Warehouse steps are suppressed while V2 owns the run. Unreal Build ignores the new control-plane manifests/scripts; actual binary/content integration remains a later bounded engine lane.
- Current maturity: **SOURCE-IMPLEMENTED / EXACT-HEAD STATIC VALIDATION PENDING / V2 WAREHOUSE EXECUTION PENDING / UE IMPORT NOT CLAIMED**.

## 2026-09-28 - Warehouse #281 root-cause publish-race repair

- Pre-Unreal #1315: **SUCCESS** on develop `a8f78c897c838a82a12ed61ddfb899a4c1ded03a`.
- Warehouse #281 reached the revised albedo/provenance lane and reported `P1C01_MATERIAL_INTAKE_PASS prepared=8 pending=8 manual=0`.
- It then created local generated commit `2474500` with 17 material-source files, but publish failed with Git `stale info` on `generated/p1c01-material-source-v1`.
- Root cause: bare `--force-with-lease` depends on a local remote-tracking ref, while isolated Warehouse checkouts intentionally do not fetch the generated branch. The source/QC result itself had already passed.
- DEC-057 changes generated-branch publication to query the authoritative remote head with `ls-remote` and use an explicit `refs/heads/<branch>:<remote-sha>` lease. New branches use a normal create push. Ephemeral workflow auth no longer asks WinCred to persist credentials.
- PG-191 statically rejects regression to implicit lease publishing.
- Current maturity: **ROOT-CAUSE SOURCE-FIXED / EXACT-HEAD VALIDATION PENDING / GENERATED BRANCH REPUBLISH PENDING / UE IMPORT NOT STARTED**.

## 2026-09-28 - Warehouse #280 PowerShell compatibility repair

- Pre-Unreal #1313 passed on develop `1aa387353cb2e5d00ea934318e2eade3aa1a9094`.
- Warehouse Stage #280 reached the selective P1C01 material-export lane and failed before material selection because Windows PowerShell 5.1 interpreted `return if(...)` as an invalid command at `prepare_p1c01_material_intake.ps1:122`.
- The selector now uses PowerShell-compatible explicit control flow: null returns through an `if` block, otherwise the selected file path is returned on the following statement.
- PG-190 now rejects the incompatible `return if(` form so this syntax regression cannot silently return.
- No UE import, runtime C++, PIE, device, visual, or performance status changes from this repair.
- Current maturity: **SOURCE-FIXED / PRE-UNREAL EXACT-HEAD PROOF PENDING / WAREHOUSE RE-RUN PENDING**.

## 2026-09-28 - Warehouse #279 passed; generated material branch held for exact albedo provenance repair

- Develop exact head `c1c3beeaa382086a320448bb95ce952f929fe6a6` passed Pre-Unreal #1311 and Warehouse Stage #279.
- Warehouse #279 material lane succeeded: intake `prepared=8 pending=8 manual=0`; generated branch `generated/p1c01-material-source-v1` at `537d9e724e064dac8af52f1a8d6e3bc6f5111858` with 8 materials / 137,974,221 source bytes.
- Mega Chapter Pack architecture is now machine-proven at the previous #279 input state: the revised material exporter no longer quarantines the car on the old 16 MiB source cap.
- Before UE import, source review found an evidence-quality flaw in material intake: provenance was captured from the first matching warehouse row before the final base-color file was selected. Therefore the generated receipt cannot prove that `source_url` belongs to the exact selected PNG/TGA; two wood entries currently expose AO URLs.
- DEC-056 holds this generated branch from UE import until intake requires explicit basecolor/albedo/diffuse/color semantics, rejects support-map/ambiguous names, and binds provenance to the exact selected file.
- This is a QC hold, not a claim that the generated texture bytes are visually wrong. No UE import has been started from the held branch.
- Current maturity: **WAREHOUSE SOURCE EXPORT RUN-PROVEN / UE IMPORT HELD FOR SOURCE-QC REGENERATION / PIE-DEVICE-VISUAL NOT CLAIMED**.

## 2026-09-28 - PR #141 Pre-Unreal #1309 stale guard repair

- Exact-head Pre-Unreal #1309 reached project-structure validation and failed on one stale PG-184 literal that still required the retired text `128 MB bounded limit`.
- The failure was in static validation policy, not in the revised exporter execution path.
- PG-184 now checks for the bounded batch-control symbol `MaxBatchSourceBytes`; PG-188 remains the exact authority for the new 32 MiB/source + 256 MiB/batch + minimum-six contract.
- Current maturity: **SOURCE-FIXED / EXACT-HEAD STATIC RE-RUN PENDING / NO UE OR VISUAL ACCEPTANCE CLAIM**.

## 2026-09-28 - Warehouse #278 proved Mega Chapter Pack; material export large-batch repair in progress

- Develop exact head `14d34d2813544caf192d4edeca7a2cf11de7799f` merged PR #140 and passed Pre-Unreal #1308 plus Warehouse Stage #278.
- Warehouse #278 executed P1C01 Mega Chapter Pack as one bounded step: `passed=3 quarantined=1 hard=0`.
- Inventory proof moved to `payloadFiles=18676 bytes=6622954088 receipts=14 receiptRecords=667 duplicateGroups=215`.
- Mega promotion remained `prepared=36 intakeQC=34 pending=3 manual=2 badReceipts=0`; ambientCG Plaster007 and KayKit Medieval Hexagon remain isolated manual blockers.
- Material intake passed at `prepared=8 pending=8 manual=0`, but MATERIAL_SOURCE_EXPORT quarantined because `SH_DIRT_SOIL/TX_SH_DIRT_SOIL_BaseColor.png` exceeded the old 16 MiB per-source cap before the generated branch could be pushed.
- DEC-055 now authorizes a larger but still bounded material promotion lane: 32 MiB per source, 256 MiB per generated batch, minimum six exported materials, and item-level quarantine instead of aborting the whole material car.
- TGA is still not promoted until an explicit `*.tga` Git LFS rule exists; PNG remains LFS-tracked.
- Runtime material cost is unchanged: one base-color sample plus scalar Roughness/Metallic/Specular. No extra runtime texture samples are authorized by this source-batch increase.
- Current maturity of this repair: **SOURCE-IMPLEMENTED / EXACT-HEAD STATIC PROOF PENDING / POST-MERGE WAREHOUSE RE-RUN PENDING / UE IMPORT PENDING**.

## 2026-09-28 - P1C01 Mega Chapter Pack V1 launched as the new batching model

- ProjectGovernor DEC-054 now makes chapter-scale batching and workflow minimization a durable production rule.
- `P1C01MegaChapterPackV1` groups four bounded cars into one Warehouse execution: inventory audit, mega promotion, material source export, and character intake.
- The existing mega-promotion selector ceiling is 62 items across surfaces (20), architecture/props (18), audio/foley (10), fauna (6), and character/animation support (8). Actual promotion still depends on staged receipt-backed stock.
- Warehouse #276 remains the latest concrete stock evidence: 13,389 payload files / 5,590,510,073 bytes / 14 receipts / 667 receipt records / 215 duplicate groups; prior mega promotion prepared 36 with 34 INTAKE_QC and two manual blockers.
- Chapter-pack execution suppresses overlapping legacy P1C01 audit/promotion/export/character steps, so one coherent pack does not pay the same work twice.
- Asset/source blockers quarantine their car and later independent cars continue; infrastructure failure remains fail-closed.
- TGA LFS policy is intentionally deferred to the first binary promotion wave that needs it, so this control-plane pack does not wake Unreal unnecessarily.
- Current maturity: **SOURCE-IMPLEMENTED / STATIC PROOF PENDING / RUNNER EXECUTION PENDING**.

## 2026-09-28 - P1C01 material-tooling Unreal CI fast path

- PR #137 exact head `bf7e08c8...` passed Pre-Unreal #1301 and full Unreal Build #1038, including editor build, production import, Automation Framework QA, startup smoke, chapter/route audits, Windows cook/package, packaged-data verification and packaged executable launch.
- That evidence showed the rooted-manifest exporter repair was safe, but also exposed avoidable runner cost: source-only P1C01 material tooling changes were still waking the full Unreal pipeline.
- Unreal Build Validation now ignores source-only changes to `prepare_p1c01_material_intake.ps1`, `promote_p1c01_material_intake.ps1`, `run_p1c01_material_pipeline.ps1` and `export_p1c01_material_source_branch.ps1` on pull requests; push already ignored the first three and now also ignores the exporter.
- The classifier safe-tooling lists now include the exporter as well, so manual dispatch or safe mixed tooling/docs deltas can inherit a proven parent instead of falling through to full cook/package.
- Runtime C++, SourceAssets, Config, Build.cs, Target.cs, streaming, cook/package and unclassified deltas retain their existing full/core/asset gates.
- Current maturity: **CI POLICY SOURCE-IMPLEMENTED / PRE-UNREAL PROOF PENDING / NO RUNTIME ACCEPTANCE CLAIM**.

## 2026-09-28 - Warehouse #276 rooted manifest exporter repair

- Develop exact head `f24480b379fa544c6d1ad01e7a6247d69aac0c93` reached Warehouse Stage #276 on the supervised `IDEAPAD320` runner. Runner health passed with `listenerPid=524` and `workerCount=1`.
- Upstream warehouse work completed before the final exporter failure: inventory `payloadFiles=13389 bytes=5590510073 receipts=14 receiptRecords=667 duplicateGroups=215`; P1C01 character intake `prepared=0 pending=4 blocked=0`; mega promotion `prepared=36 intakeQC=34 pending=3 manual=2 badReceipts=0`.
- The two mega-promotion blockers remain isolated in manual queue: ambientCG `Plaster007` has a structurally corrupt ZIP, and KayKit `KAYKIT_MEDIEVAL_HEXAGON_1_0` failed selected extraction. Neither is allowed to stop the rest of the train.
- P1C01 material intake itself passed with `prepared=8 pending=8 manual=0`. The run then failed only because `export_p1c01_material_source_branch.ps1` re-joined an already absolute `ManifestPath` with `ProjectRoot`, producing an invalid duplicated Windows path.
- The exporter now keeps rooted manifest paths unchanged and joins only relative paths. PG-184 static validation now guards `IsPathRooted`, `ResolvedManifestPath`, the resolved-path `Get-Content` call, and rejects the old re-join expression.
- No gameplay/runtime C++ changed in this repair.
- Current maturity: **SOURCE-FIXED / EXACT-HEAD STATIC VALIDATION PENDING / GENERATED MATERIAL BRANCH PENDING / UE IMPORT PENDING**.

## 2026-09-28 - P1C01 large material source promotion train

- A concrete source-promotion bridge now converts the existing receipt-verified warehouse stock into a bounded Git branch instead of leaving material candidates only in the runner warehouse.
- `prepare_p1c01_material_intake.ps1` now supports heterogeneous direct-file/archive receipt schemas, verifies SHA256 before use, performs bounded ZIP safety checks, isolates blocked items into a manual queue, and allows good prepared materials to continue.
- `export_p1c01_material_source_branch.ps1` requires at least 8 prepared materials, caps each source file at 16 MB and the whole batch at 128 MB, and promotes only PNG/TGA base color plus scalar-material MTL files into `SourceAssets/Production/Imported/P1C01Materials`.
- The Warehouse workflow owns a narrowly scoped generated branch `generated/p1c01-material-source-v1`; it does not merge that branch automatically. The next PR from that branch must pass normal exact-head Unreal validation so the existing UE4.27 production importer proves actual import.
- Selective routing adds `WH_RUN_P1C01_MATERIAL_EXPORT`; provider refreshes can feed the material export, while unrelated Warehouse control-plane changes do not.
- No gameplay/runtime C++ changed in this train.
- Current maturity: **SOURCE-IMPLEMENTED / EXACT-HEAD STATIC VALIDATION PENDING / GENERATED MATERIAL BRANCH PENDING / UE IMPORT PENDING**.

## 2026-09-28 - P1C01 immediate large intake unfreeze repair

- Warehouse #275 failed only in P1C01 character intake after the Quaternius staging lane completed. Exact failure: PowerShell StrictMode raised `PropertyNotFoundStrict` while reading heterogeneous receipt rows that do not all expose `file/sha256/asset_slug` fields.
- Character intake now reads both direct-file receipts (`file/sha256`) and archive receipts (`archive/archive_sha256`) through optional-property access, so one provider schema cannot stop the whole train.
- The staged-stock mega promotion path also had 28 selected archives isolated in #274 because Windows PowerShell had not loaded `System.IO.Compression.FileSystem`; both P1C01 extraction paths now load that assembly explicitly before using `ZipFile`.
- This repair intentionally targets the existing 5.4 GB staged warehouse first. On merge, selective Warehouse routing will rerun bounded inventory + P1C01 mega promotion + character intake, without restaging unrelated providers or running full saturation.
- No gameplay/runtime C++ changed in this repair. Existing runtime develop validation remains independent.
- Current maturity: **SOURCE-IMPLEMENTED / EXACT-HEAD STATIC VALIDATION PENDING / PERSISTENT WAREHOUSE EXECUTION PENDING**.

## 2026-09-28 - P1C01 runtime salvage rebased onto current develop

- PR #133 exact head `970a52f73ed5242d371ae7061011093765af42f6` completed Unreal Build #1033 successfully, including `Build ShireJourneyEditor` and `Import production assets in UE4.27.2`.
- PR #133 could not be merged after develop advanced through the staged-stock promotion train, so its unique runtime/character-intake delta is being reapplied semantically on current develop instead of merging stale CI files.
- Runtime delta retained: bounded interaction and ambient-motion pooling, cached player lookup, SFX repeat guard, and bounded asynchronous character-rig availability retry.
- Character intake delta retained: four officially captured CC0 Quaternius candidates, hashed archive intake, FBX-only animated promotion, and manual-queue isolation for bad warehouse payloads.
- Current develop Warehouse selective routing and P1C01 mega-promotion train remain authoritative; only additive character-intake routing is added.
- Fresh exact-head static and Unreal proof for this rebased branch are pending. The #1033 success is evidence for the original PR #133 head only.
- No PIE/device/visual/performance acceptance is claimed.

## 2026-09-28 - P1C01 mega promotion train wired into selective Warehouse execution

- The new P1C01 staged-stock promotion train is now part of the post-merge Warehouse path without reopening full provider staging.
- Warehouse classifier introduces `WH_RUN_P1C01_PROMOTION`; only the new manifest/script select this phase (plus the bounded inventory audit).
- Warehouse workflow executes the new phase only when selected. Existing control-plane, provider, saturation, critical-gap and provider-resolution routing remains unchanged.
- PG-184 now guards receipt-hash verification, bounded selected extraction, manual-queue continuation, INTAKE_QC ceiling and the five P1C01 priority classes.
- No C++/runtime source changed; PR #133 remains untouched while Unreal #1033 is queued.
- Current maturity: **SOURCE-IMPLEMENTED / EXACT-HEAD STATIC VALIDATION PENDING / POST-MERGE WAREHOUSE EXECUTION PENDING**.

## 2026-09-28 - P1C01 mega warehouse promotion preparation started

- Production is continuing while PR #133 exact-head Unreal #1033 remains queued; the PR #133 head is intentionally left unchanged.
- The fastest asset path is now to exploit the already-staged warehouse before adding more sources. The latest proven warehouse audit reported 13,377 payload files / 5,426,414,977 bytes.
- New `WarehouseP1C01MegaPromotionTrainV1` prioritizes Shire surfaces, architecture/props, ambience/foley, fauna and character/animation support from already-authorized/staged providers.
- New `run_warehouse_p1c01_mega_promotion.ps1` verifies receipt hashes, copies/extracts only selected bounded assets, rejects dangerous/BMP payloads, requires FBX for animated classes, and converts blockers into a manual queue instead of stopping the whole train.
- Original warehouse payloads are never modified. The promotion ceiling remains `INTAKE_QC`; no item is called READY_FOR_IMPORT automatically.
- No C++/runtime source changed in this preparation branch.
- Current maturity: **SOURCE-IMPLEMENTED / HOSTED STATIC VALIDATION PENDING / WAREHOUSE EXECUTION PENDING**.

## 2026-09-28 - PG-167 administrative runner guard aligned

- Pre-Unreal #1289 proved the new hosted Python fast path works, emitting `PYTHON_FAST_PATH_PASS` with Python 3.12.10.
- The only failure was stale PG-167 policy text that still required Branch Cleanup to run on the UE4 self-hosted runner, conflicting with the newly intended hosted-admin architecture.
- PG-167 now requires `runs-on: windows-latest` for Branch Cleanup and explicitly forbids `self-hosted/ue4-27` there, while preserving merged-PR-only execution, exact-head isolated checkout and branch-safety checks.
- This is a validator/policy-alignment repair only; no runtime/gameplay/acceptance gate is weakened.
- Current maturity: **SOURCE-IMPLEMENTED / NEW EXACT-HEAD STATIC VALIDATION PENDING**.

## 2026-09-28 - Administrative overhead trimmed without weakening gates

- Requirement-ID bureaucracy is narrowed: only material product/story/architecture/acceptance/priority/external-dependency changes create new Governor requirements; status questions, clarifications, evidence refreshes and routine CI bookkeeping do not.
- Branch Cleanup is moved from the supervised UE4 self-hosted runner to GitHub-hosted `windows-latest`; it keeps exact-head isolated checkout and active-PR/protected-branch safety.
- Pre-Unreal keeps the complete static/governance/asset/deep-audit suite, but now resolves the already-provisioned hosted Python through a fast PATH probe first and falls back to the existing robust resolver only when needed.
- PG-167/PG-176 guard the fast-path/fallback contract and forbid administrative branch cleanup from consuming the UE4 runner.
- No C++ runtime, gameplay, story, asset acceptance, Gate 6/7, or evidence-promotion rule is weakened.
- Current maturity: **SOURCE-IMPLEMENTED / EXACT-HEAD STATIC VALIDATION PENDING**.

## 2026-09-28 - CI/Warehouse root repair released; production resumes

- Exact repair head `0bd0e6952161f1c3fa5bb603d25813400c330f24` passed hosted Pre-Unreal #1285.
- Develop merge head `26ff8f8838b4c9680c793fea5d942a314ad29be4` passed hosted Pre-Unreal #1286.
- Self-hosted Warehouse #272 passed on the same develop head. Concrete runner proof: `RUNNER_HEALTH_PASS identity=IDEAPAD320\\user sessionId=1 listenerPid=6192 workerCount=1`.
- Warehouse #272 classified the merged control-plane delta as `mode=selective ... phases=WH_RUN_AUDIT`; all provider staging/saturation/preparation/resolution trains were skipped.
- Persistent inventory audit passed: `payloadFiles=13377 bytes=5426414977 receipts=14 receiptRecords=667 duplicateGroups=215`; final persistent footprint was `files=13392 bytes=5427039102`.
- The run emitted `WAREHOUSE_SELECTIVE_EXECUTION_PASS`. No Unreal Build Validation run was triggered by this Warehouse/control-plane-only merge, proving the intended routing separation.
- The Governor production freeze is therefore **RELEASED**. Resume the existing `W01_P1C01_PRODUCTION_VERTICAL_SLICE` only; this does not open a new chapter or waive Gate 6/7.
- Evidence boundary: **STATIC-VALIDATED + SELF-HOSTED WAREHOUSE ROUTING PROVEN**. No new COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED, or performance claim is created by this infrastructure repair.

## 2026-09-28 - Warehouse control-plane proof routing hardened

- PR #129 merged the #271 exact-source classifier correction at `61dd71845da4db3689c8a53f7d898ba5e81abb40`; hosted Pre-Unreal #1283 passed on its exact repair head.
- A second routing defect was identified before wasting another full Warehouse run: `Scripts/classify_warehouse_validation.ps1` itself was absent from Warehouse Stage push paths, so its post-merge fix could not automatically prove the repaired self-hosted path.
- Warehouse Stage now triggers on classifier changes. Workflow-only control-plane deltas select bounded persistent-inventory audit instead of all provider trains.
- The classifier now ignores unrelated Docs/static-validator/runtime files that happen to share a commit with a warehouse-triggering path; such files no longer escalate selective execution to `mode=all`.
- PG-184 now locks the exact-source classifier markers, classifier-trigger path, and bounded workflow-control-plane audit rule.
- No gameplay/runtime content changed.
- Current maturity: **SOURCE-IMPLEMENTED / EXACT-HEAD STATIC VALIDATION PENDING / POST-MERGE WAREHOUSE PROOF PENDING**.

## 2026-09-28 - Warehouse #271 exact-source classifier repair

- Post-merge Warehouse #271 ran on self-hosted runner `UE4-27-Windows` at develop merge head `542a6feef7e2985e40ed86f7242dd0a005be1395`.
- Runner topology/health passed with interactive identity `IDEAPAD320\\user`, `legacyService=absent`, watchdog task present, one listener/worker, GitHub:443 connectivity, and workspace/resource checks.
- The run failed before any provider/archive work because `classify_warehouse_validation.ps1` executed Git commands from the persistent runner workspace instead of the isolated `SHIRE_WAREHOUSE_SOURCE` checkout. Git therefore reported `fatal: bad object 542a6feef7e2985e40ed86f7242dd0a005be1395`.
- Root correction: the classifier now fail-closes onto the isolated warehouse checkout, changes directory to that repository before diffing, and on a shallow-history miss fetches both exact head and base commits once before retrying.
- No provider download, archive expansion, Unreal build, or gameplay source was executed by the failed run.
- Current maturity: **SOURCE-IMPLEMENTED / EXACT-HEAD STATIC VALIDATION PENDING / POST-MERGE WAREHOUSE PROOF PENDING**.

## 2026-09-28 - Pre-Unreal #1280 stale guard root correction

- Exact-head `a8714aa3a1fb8ff0fb7be970d4bcfedb49139035` on hosted Pre-Unreal #1280 proved the isolated checkout, Python resolution, and Unreal classifier tests all succeeded.
- Project structure validation reached `PRE-UNREAL CORE VALIDATION PASSED`, then failed on exactly three stale policy assertions in `pre_unreal_validate.py`: the old unconditional FULL-lane intermediate-reset expectation plus the old persistent self-hosted Pre-Unreal path/marker assumptions.
- PG-145C now validates the actual `SHIRE_RESET_INTERMEDIATES` classifier gate; normal CORE/ASSET work preserves intermediates, while `.Build.cs`, `.Target.cs`, or `ShireJourney.uproject` changes remain the clean-compile trigger.
- PG-176 now validates the GitHub-hosted isolated `%RUNNER_TEMP%\\shire-pre-unreal` checkout with `hosted=true` and rejects the legacy persistent self-hosted checkout tokens.
- No runtime/gameplay source changed.
- Current maturity: **SOURCE-IMPLEMENTED / NEW EXACT-HEAD STATIC VALIDATION PENDING**.

## 2026-09-28 - Legacy CI guard migration completed

- Hosted Pre-Unreal #1277 proved the classifier fix: all Unreal lane-selection tests passed, including the new build-rule reset case.
- The remaining failure was entirely legacy policy drift inside `pre_unreal_validate.py`: PG-134/PG-167 still required the old self-hosted static lane, while PG-185 required the new hosted lane.
- PG-134 and PG-167 are now migrated to the hosted exact-head static checkout contract; PG-185 now rejects the actual `- self-hosted` runner declaration instead of matching explanatory comments.
- No runtime/gameplay behavior changed.
- Current maturity: **SOURCE-IMPLEMENTED / NEW EXACT-HEAD STATIC RUN PENDING**.

## 2026-09-28 - Warehouse corrupt-cache purge hardened

- Receipt reuse now purges structurally corrupt cached ZIPs immediately instead of only returning non-reusable.
- Critical-gap manifest now explicitly defines ZIP handling as read-only metadata inspection; physical extraction is deferred to explicit class-specific conversion/import work.
- PG-184 now guards both the corrupt-cache purge marker and the metadata-only manifest contract.
- Current maturity: **SOURCE-IMPLEMENTED / EXACT-HEAD STATIC VALIDATION PENDING**.

## 2026-09-28 - Hosted Pre-Unreal classifier false-red repaired

- Hosted Pre-Unreal #1269 proved the new GitHub-hosted Windows lane itself works: exact-head checkout and Python 3.12 resolution both succeeded.
- The run failed only inside `test_unreal_classifier.ps1` because `$requiresCleanCompile` was referenced before initialization in the classifier path used by the test harness.
- The classifier now initializes `$requiresCleanCompile` directly after delta resolution, before any mode decision.
- This is a static classifier defect; it does not change runtime/gameplay state.
- Current maturity: **SOURCE-IMPLEMENTED / NEW EXACT-HEAD STATIC RUN PENDING**.

## 2026-09-28 - CI root repair V3: zero-waste trigger routing

- Unreal Build Validation now treats `Data/MasterExecutionRoadmap.json` as governance-only, preventing roadmap-only PR sync from consuming the UE4 runner.
- Warehouse critical-gap preparation now exits at receipt-integrity preflight before any archive inventory when missing/hash/bad-receipt blockers already exist.
- PG-184 now locks the preflight marker so future changes cannot silently reintroduce delayed failure.
- PR #128 is intentionally configured so repair commits should trigger only hosted Pre-Unreal validation; no Warehouse PR run and no Unreal run are expected from repair-only deltas.
- Current maturity: **SOURCE-IMPLEMENTED / EXACT-HEAD STATIC VALIDATION PENDING**.

## 2026-09-28 - CI root repair V2: split proof lanes and preserve build state

- Production remains frozen while infrastructure is repaired.
- Pre-Unreal static/policy validation is moved to GitHub-hosted `windows-latest`; it no longer consumes or queues behind the UE4 self-hosted runner.
- Warehouse Stage remains self-hosted for access to the persistent warehouse, but no longer runs on pull-request synchronize.
- New `Scripts/classify_warehouse_validation.ps1` selects only provider/phases affected by the landed `develop` delta; unknown/manual cases fail safe to the full warehouse path.
- Warehouse-only scripts/data are excluded from Unreal Build Validation triggers.
- Unreal validation keeps exact-head/fail-safe semantics but preserves `Intermediate/Build/Win64` and `Binaries/Win64` by default.
- Clean intermediate reset is now requested only for `.Build.cs`, `.Target.cs`, or `ShireJourney.uproject` changes; compiler-pressure failures still get one bounded clean retry inside `ci_build_unreal.cmd`.
- PG-184/PG-185 statically prevent regression to PR-synchronize warehouse runs, repeated ZIP extraction, self-hosted Pre-Unreal, or unconditional Unreal intermediate wipes.
- Current maturity: **SOURCE-IMPLEMENTED / EXACT-HEAD STATIC VALIDATION PENDING**. Runtime/gameplay acceptance is unchanged.

## 2026-09-28 - Production freeze for CI/warehouse root repair

- Owner explicitly stopped active production work after repeated Warehouse #269/#270 failures consumed ~12-13 minutes each.
- PRs #125, #126 and #127 were closed unmerged to stop new synchronize-triggered churn; their branches remain preserved so no source work is lost.
- One already-running Unreal job from the closed production PR may finish because the available GitHub connector does not expose workflow cancellation; no new rerun is being started.
- Root causes identified:
  - PR-synchronize Warehouse execution had been reintroduced on the production branch.
  - critical-gap QC physically re-extracted every ZIP on every run.
  - receipt reuse checked presence/size but not ZIP structural readability.
  - corrupt cached AmbientCG ZIPs could remain reusable forever.
  - KayKit GitHub ZIP extraction hit Windows path/symlink semantics even though intake QC only needed metadata.
  - duplicate receipt rows caused the same corrupt AmbientCG payload to be reported twice.
- Repair branch `repair/ci-warehouse-root-fix-v1` now:
  - keeps Warehouse off pull-request synchronize,
  - validates ZIP structure before receipt reuse,
  - removes/redownloads corrupt provider ZIPs,
  - inventories ZIP entries read-only via `ZipFile::OpenRead` instead of `Expand-Archive`,
  - deduplicates receipt records,
  - prints exact blockers,
  - guards the architecture with PG-184.
- Current maturity: **SOURCE-IMPLEMENTED / STATIC VALIDATION NOT YET RUN**. No gameplay or acceptance promotion.

## 2026-09-27 - Permanent runner topology machine proof

- Owner-side Windows evidence now shows the legacy `actions.runner.*` service absent after successful deletion.
- `ShireJourney-GitHubRunner-Watchdog` is Running as UserId `user` with `LogonType=Interactive`.
- `Runner.Listener.exe` PID **6192** is owned by `IDEAPAD320\user`; watchdog log reports `SHIRE_RUNNER_WATCHDOG_ONLINE pid=6192 brokerListening=true`.
- GitHub Unreal Build **#1021** on exact head `b22a5da34ba71ba583c8b5b2a026085a2e11feda` passed runner health with `legacyService=absent`, interactive identity/session, listener+worker ownership, GitHub:443 and workspace checks.
- This closes the **runner ownership/topology** root cause for that exact machine state.
- Unreal #1021 used the governance/docs-only fast path, so C++ build/import/PIE/package/gameplay/device/visual/performance acceptance was **not** produced.
- Pre-Unreal #1256 was a validator false-red only: PG-183 searched for the literal `legacyService=absent` even though the verifier emits that value dynamically. The guard is corrected to validate the dynamic contract without weakening it.

## 2026-09-27 - Runner root-cause architecture fix: remove service mode entirely

- Root cause confirmed from owner-side Windows state plus Unreal #1000: two runner ownership paths coexisted. The legacy `actions.runner.*` service was **Running** and owned `Runner.Listener.exe` as `NT AUTHORITY\NETWORK SERVICE` while the watchdog task was also Running.
- This is now treated as an architecture defect, not a daily repair task.
- New permanent design: `actions.runner.*` is deleted by `Scripts/runner_service_guard.ps1`; if Windows temporarily retains a pending-deletion entry it must be **Stopped + Disabled**.
- `install_runner_watchdog.ps1` installs the service guard beside the watchdog, removes service ownership, then starts the interactive-user watchdog.
- `runner_watchdog.ps1` invokes the service guard at boot and every supervision loop, so a recreated service-mode runner is automatically stopped/deleted again.
- `verify_runner_session.ps1` accepts only service absent or stopped-disabled plus the interactive-user listener/worker topology.
- PG-145B now statically guards the permanent service-exclusion contract.
- Physical machine repair still requires one elevated owner-side installer run; until that succeeds, current state is **ROOT-FIX SOURCE-IMPLEMENTED / DEVICE REPAIR PENDING**. No compile/PIE/device/visual/performance acceptance is implied.

## 2026-09-27 - Permanent runner service-mode elimination

- Root cause class confirmed by live evidence: the legacy `actions.runner.*` Windows service can be started under `NT AUTHORITY\NETWORK SERVICE` while the interactive watchdog also exists, creating competing runner ownership and repeated pre-build failures.
- The permanent design now removes service mode instead of merely leaving it stopped/manual.
- New `Scripts/runner_service_guard.ps1` stops, disables and deletes any `actions.runner.*` registration and terminates runner Listener/Worker processes owned by NETWORK SERVICE/LOCAL SERVICE/SYSTEM.
- `install_runner_watchdog.ps1` installs both watchdog and guard, purges service mode first, then starts the interactive-user watchdog.
- `runner_watchdog.ps1` invokes the guard at boot and during every supervision loop, so a resurrected service is automatically removed.
- `verify_runner_session.ps1` now accepts only an absent service or a stopped+disabled pending-deletion entry.
- PG-183 statically guards the permanent service-elimination contract.
- Evidence boundary: **SOURCE-IMPLEMENTED / exact-head static validation pending / physical machine repair pending one-time elevated install**. No compile/PIE/device/visual/performance claim.

## 2026-09-27 - Runner ownership directive promoted to top-level governance

- The runner rule previously existed in scripts/guards and buried runner-history fields, but was not prominent enough in the Governor/onboarding path for a zero-context Work session.
- New hard invariant: UE4-27-Windows runs only under the proven interactive Windows user through `ShireJourney-GitHubRunner-Watchdog`.
- Legacy `actions.runner.*` Windows service must remain **Stopped / Manual** and must never be enabled or started as a fallback.
- `NETWORK SERVICE`, `LOCAL SERVICE`, and `SYSTEM` are forbidden runner identities.
- Worker/AI sessions may inspect health but may not change runner ownership/topology without explicit owner authorization.
- README, PROJECT_GOVERNOR guide and one-command onboarding now surface this rule before production work.
- Existing source guards remain authoritative: `install_runner_watchdog.ps1`, `verify_runner_session.ps1`, PG-145 and PG-145B.
- Evidence boundary: **GOVERNANCE/HANDOFF SOURCE-IMPLEMENTED / exact-head static validation pending**. This does not prove the current physical Windows service/task state.

## 2026-09-27 - Zero-context developer entry hardening

- The repository default branch is `main`, while `develop` remains the canonical integration/programmer-handoff branch.
- Develop onboarding now explicitly warns that `main` is a stable/release landing surface and that current execution truth must be read from `develop`.
- `Docs/PROJECT_GOVERNOR.md` no longer hard-codes the historical D stage as the next runtime drop; current execution order comes from ProjectGovernor `current_focus` + `execution_control.next_actions` plus live GitHub state.
- `Scripts/new_developer_onboarding.ps1` now emits a branch warning whenever the local checkout is not the canonical development branch.
- A separate default-branch README redirect is required on `main` so a zero-context GitHub visitor reaches the develop Governor path immediately.
- Evidence boundary: **SOURCE-IMPLEMENTED / static validation pending**. No runtime/PIE/device/visual/performance acceptance is implied.

## 2026-09-27 - Warehouse provider-resolution train V3 prepared

- V3 is stacked behind the critical-gap V2 branch and resolves provider/access blockers rather than adding another uncontrolled source list.
- `WarehouseProviderResolutionTrainV3.json` defines 20 bounded resolution cars with at most three preferred and three fallback providers per technical slot.
- `run_warehouse_provider_resolution.ps1` reads the live provider registry and existing warehouse receipts, classifies each provider as auto-capable, manual-only, auth-required, review-required or reference-only, and selects an already-staged/auto-capable provider when available.
- It never converts login/OAuth/purchase/marketplace/reference lanes into automatic downloads and never promotes READY_FOR_IMPORT.
- Warehouse Stage is extended so provider-resolution reporting runs after V1 saturation and V2 critical-gap preparation.
- Current Quaternius V4 license capture opens staging attempts for 13 high-value packs, while store/interactive-only download resolution remains fail-closed.
- Evidence boundary: **PROVIDER-RESOLUTION PREPARATION / exact-head validation pending**.

## 2026-09-27 - Critical Quaternius license blockers reduced

- Official Quaternius pack pages were rechecked for the highest-value unresolved character/animation/fauna/creature/architecture/nature/prop candidates.
- `WarehouseQuaterniusAcquisitionBatchV1.json` advances to V4 and records explicit official-page `CC0` capture for 13 previously license-unresolved packs, including universal character bases, fantasy outfits, RPG characters, universal animations, monsters, medieval village megakit, buildings, modular ruins/dungeon, nature, animated animals, farm animals and fantasy props.
- This changes only staging authorization. Public-download discovery remains mandatory; interactive/store-only routes stay unresolved and are never bypassed.
- Receipt/SHA256 and extracted intake QC remain required before any `STAGED` or later promotion evidence is accepted.
- Evidence boundary: **LICENSE-CAPTURE / SOURCE-PREPARATION** only; no pack is claimed downloaded/imported/integrated/accepted from this change.

## 2026-09-27 - Warehouse receipt parser blocker repaired after first real V1 staging run

- Warehouse Stage #265 completed all provider staging steps successfully and the persistent inventory audit passed with **247 payload files / 3,851,680,492 bytes / 13 receipts / 667 receipt records / 215 duplicate-hash groups**.
- The run failed only in the V1 saturation report because heterogeneous receipt schemas omit optional fields such as `file`, `archive`, `sha256`, `asset_slug` or `state` on some rows while `Set-StrictMode -Version Latest` treated direct property access as fatal.
- `run_warehouse_saturation_train.ps1` now uses explicit optional-property access for receipt/header/item fields and safely handles file-vs-archive receipt shapes.
- `run_warehouse_critical_gap_preparation.ps1` received the same hardening before first execution so V2 does not repeat the same schema failure.
- The fix does not relax evidence requirements: actual files still require SHA256 verification before they count as verified/prepared.
- Evidence boundary: **warehouse staging/audit evidence is real; V1/V2 reporting fix requires fresh exact-head validation**. No READY_FOR_IMPORT, PIE, device, visual or performance acceptance is inferred.

## 2026-09-27 - Critical warehouse gap preparation train V2

- Warehouse saturation PR #121 completed exact-head Pre-Unreal #1159 SUCCESS and Unreal #926 SUCCESS and merged at `70e7a3c0a03a7dbebbe6c70d822bab7a06c59e87`.
- Warehouse Stage #265 was queued from that merge to pull/audit the public provider-compatible warehouse lanes.
- New V2 branch `warehouse/critical-gap-preparation-train-v2` adds a second 20-car train focused on the largest remaining production gaps rather than source discovery.
- `run_warehouse_critical_gap_preparation.ps1` verifies receipt SHA256, expands ZIP copies into a separate prepared root, blocks executable/BMP payloads, inventories FBX character/animation/creature/static-mesh candidates, separates mesh conversion debt, groups production texture/audio/UI/terrain source classes, and emits per-car prepared/pending/blocked counts.
- Warehouse Stage now invokes the V2 processor after normal staging, inventory audit and V1 saturation reporting.
- V2 cannot promote any file to `READY_FOR_IMPORT`; skeleton/skin/deformation, visual/canon, PIE/device/performance and class-specific QC remain required.
- Evidence boundary: **SOURCE/PREPARATION IMPLEMENTED / exact-head validation pending**.

## 2026-09-27 - Warehouse train consolidation replaces stale-base prep PRs

- The architecture/interiors/props preparation from former PR #119 and the character/audio/fauna preparation from former PR #120 are now consolidated onto `warehouse/p1c01-trilogy-saturation-train-v1`, which is based on post-#118 `develop`.
- Consolidated artifacts include the architecture six-pack intake/QC lane plus character rig/animation, five-item Shire audio, and living-world fauna preparation scripts/manifests.
- `pre_unreal_validate.py` now guards these consolidated lanes together with the 20-car warehouse saturation train.
- This removes duplicated stale-base validation work while preserving all substantive preparation.
- Evidence boundary remains **PREPARATION / STATIC CONTRACT**, pending exact-head validation of the consolidated branch.

## 2026-09-27 - Trilogy warehouse saturation train V1 prepared

- Material PR #118 reached exact-head Pre-Unreal #1155 SUCCESS and Unreal #922 SUCCESS and was merged to `develop` at `fc7c67123248d70e9f568ee83f7110210e556cd7`.
- New warehouse branch `warehouse/p1c01-trilogy-saturation-train-v1` defines a **20-car** preparation sequence covering the largest remaining warehouse families across P1C01 and reusable trilogy stock.
- `Data/WarehouseSaturationTrainV1.json` bounds each car to a small provider set and an explicit preparation ceiling. Authentication/account/purchase/manual-license lanes never auto-stage.
- `Scripts/run_warehouse_saturation_train.ps1` can optionally invoke the existing public/provider-compatible staging lanes (Poly Haven, ambientCG, Quaternius, Kenney, KayKit, OpenGameArt), run the persistent inventory audit, and produce per-car receipt/hash/byte/state coverage.
- `.github/workflows/warehouse-stage.yml` now triggers on the saturation manifest/orchestrator and emits the 20-car coverage report after normal staging/audit.
- Pre-Unreal guards exact car count/order, unique IDs, bounded provider fan-out, safe preparation ceilings, FBX/PNG-TGA/WAV/runtime-loading rules and receipt-SHA256 evidence reporting.
- Evidence boundary: **SOURCE/PREPARATION IMPLEMENTED / exact-head validation pending**. No newly planned car is READY_FOR_IMPORT, IMPORTED, INTEGRATED, PIE/device/visual/performance accepted from this change.

## 2026-09-27 - Runner watchdog state-contract blocker repaired on active material branch

- Unreal #915 and #920 both stopped before compilation at `Verify runner session health` with `RUNNER_HEALTH_FAIL watchdog-state state=Ready`.
- Root cause is a validator-policy mismatch: `install_runner_watchdog.ps1` explicitly accepts both `Running` and `Ready` as healthy scheduled-task states, while `verify_runner_session.ps1` accepted only `Running`.
- The verifier now accepts the same `Running|Ready` contract and continues into the stricter live process checks for exactly one interactive-user `Runner.Listener`, active `Runner.Worker`, session ownership, network, workspace and resources.
- `Ready` is logged explicitly as `RUNNER_HEALTH_WATCHDOG_READY`; it is not relabeled as engine proof.
- Evidence boundary: **CI validator-policy fix implemented / fresh exact-head rerun required**. No compile/import/PIE/device/visual claim is created by this repair.

## 2026-09-27 - P1C01 material train expanded to the full authorized Poly Haven surface set

- The active #118 material batch now covers all **16** Poly Haven Shire/Bag End surface candidates already authorized by `P1C01WarehousePromotionQueueV1.json`, rather than the earlier 8-item subset.
- `Data/P1C01MaterialImportWaveV1.json` now carries bounded authored Roughness/Metallic/Specular scalars for every item and keeps every external candidate at `AUTHORIZED_FOR_STAGING` until receipt-backed intake exists.
- `Scripts/prepare_p1c01_material_intake.ps1` now emits one PNG/TGA base-color candidate plus scalar `Pr/Pm/Ks`, SHA256 hashes for prepared base color and generated MTL, and richer prepared/pending/blocked counts.
- `Scripts/pre_unreal_validate.py` now guards the 16-item completeness, queue authority, duplicate IDs/slugs, scalar bounds, low-spec material parameter contract, SHA256 preparation and BMP prohibition.
- This expansion still adds no runtime texture sample beyond the existing albedo slot, does not increase foliage/detail density, and does not promote an external asset without source/license/receipt/SHA256 evidence.
- The current Unreal validation blocker remains runner infrastructure: run #915 has repeatedly failed at `Verify runner session health` with `RUNNER_HEALTH_FAIL watchdog-state state=Ready` before UE4 build/import starts. The material implementation itself therefore remains **SOURCE-IMPLEMENTED / exact-head engine proof pending**.

## 2026-09-27 - P1C01 Shire material surface-set train started

- Active production batch: `P1C01_SHIRE_MATERIAL_SURFACE_SET_V1` on branch `production/p1c01-shire-material-surface-set-v1`.
- Added `Data/P1C01ShireMaterialSurfaceSetV1.json` covering the existing project-owned Shire TGA palette (Bark, Dirt, DoorGreen, Grass, Leaves, Stone, Wood) and eight authored material identities.
- `ShireProductionImportCommandlet` now carries a bounded `Specular` scalar on production surface and foliage masters and derives authored instance specular response from MTL `Ks` values. No extra texture samples, no foliage density increase and no new runtime heavy-load path were introduced.
- Existing roughness/metallic values, foliage near/far split and TGA albedo bindings are preserved.
- Train sequence after this batch: evidence-backed Poly Haven surface intake -> Shire support architecture/interiors -> living-world visual integration/polish. External items remain fail-closed without source/license/receipt/SHA256.
- Evidence boundary: **SOURCE-IMPLEMENTED / exact-head validation pending**. No PIE/device/visual/performance acceptance is claimed.

## 2026-09-27 - P1C01 player-experience convergence implementation

Source-verified defects from the P1C01 interaction path are implemented as one bounded gameplay batch:

- Bilbo's `ShireArrival -> LongExpectedParty` transition now waits for completion of his authored multi-line dialogue sequence through an explicit NPC opt-in flag; existing NPC hand-offs remain unchanged by default.
- Raw `MouseX/MouseY` camera input no longer multiplies by frame DeltaSeconds; a direct `MouseLookSensitivity` scalar controls the mouse path.
- Quick-load now gives the player a visible rejection message when `RestoreSaveSnapshot` returns false, while detailed rejection reasons remain in logs.
- `AShireQuestTrigger` remains non-ticking and now tracks the overlapping player weakly, re-evaluating eligibility only on quest-stage, active-quest, story-beat and restored-state events. This closes the enter-too-early / remain-inside progression gap without a per-frame cost.
- Dialogue subtitle rendering now uses bounded word wrapping in a taller 720p-safe dialogue box.
- Map/Chronicle movement/damage behavior remains deliberately unchanged pending the explicit UX policy decision already registered in `WORLD_DETAIL_LEDGER.md`.

Evidence boundary: **SOURCE-IMPLEMENTED / STATIC-REVIEWED**. Exact-head UE4.27 compile/runtime validation is required before any COMPILE-TESTED or PIE claim.

## 2026-09-27 - Repeated MSVC stale-temp validation blocker contained

- Unreal Build #896 failed on both attempt 1 and attempt 2 before asset import with `fatal error C1083: Cannot open compiler intermediate file`.
- The MSVC probe proved the current temp root was writable (`shire-msvc-36281890705-2`), while the compiler failure referenced an older removed temp root (`shire-msvc-36280675863-1`). This isolates the failure to stale project build intermediates/action metadata rather than the production-import source change.
- `Scripts/ci_build_unreal.cmd` now treats this exact C1083/compiler-intermediate signature as recoverable compiler-environment pressure: it clears only project Win64 intermediates/binaries and retries the build once, using the already-current TEMP/TMP environment.
- Scope remains narrow and blocker-driven; this does not reopen general CI optimization work.
- Evidence boundary: **CI_INFRA FIX CANDIDATE / fresh exact-head Unreal validation pending**.

## 2026-09-27 - P1C01 one-click production import Engine-package dirty repair

- Owner device run of `SHIRE_UPDATE_BUILD_LAUNCH.bat` reached the production-import phase and failed while UE4.27 attempted to save `/Engine/EngineMaterials/WorldGridMaterial`.
- Root cause was source-confirmed in `ShireProductionImportCommandlet.cpp`: a referenced material package was marked dirty before the importer checked whether it belonged to `/Game/Production/`.
- Repair candidate now gates both mesh-material and registry-recovery dirty marking to project-owned `/Game/Production/` packages only. Engine/plugin fallback materials are no longer marked dirty by the importer.
- Scope is intentionally narrow: no gameplay, quest, save, world-layout or asset-content redesign.
- Evidence boundary: **DEVICE-OBSERVED FAILURE + SOURCE-IMPLEMENTED FIX CANDIDATE**. Fresh exact-head Pre-Unreal/UE4.27 build+import proof is still required before calling the repair COMPILE/IMPORT tested.

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

## Administrative repetition root fix — 2026-09-26

The validation snapshot is the sole handoff evidence authority. A stale legacy `source_head` is reported as a warning, not a production blocker. This supersedes the earlier requirement to keep duplicate fields synchronized by hand. Mixed-SHA evidence, unsuccessful green baselines, missing snapshots and missing human acceptance boundaries still fail validation. Regression tests cover both allowed metadata drift and rejected evidence corruption. Story continuity, living-world coherence, save/load integrity and target-device playability remain the production priorities. This change does not certify runtime or human acceptance.

# Review checkpoint — 2026-09-26

PR102 failed Governor validation because its historical `session_handoff.source_head` was moved to the current integration commit without matching validation evidence. Restore it to the recorded last-green SHA; keep the current integration baseline in `integration_train`. Future phase changes must preserve this distinction. No validation gate is disabled. Onboarding uses PG-174 because D lighting and Mega promotion already use PG-172/173 in PR101. C3/C4 are merged; D and bounded Mega promotion are in progress. Runtime, visual, device and performance acceptance remain separate and unproven by this administrative repair.

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

## 2026-09-26 - Production resume checkpoint

PR90, PR87/C2 and PR93 callback repair are merged. Candidate e2dd022 passed the full machine chain including rendered package startup. Post-merge verification is ongoing. C3 preparation and implementation can proceed independently of branch cleanup. Human pacing/visual/performance acceptance remains pending. Governor production_resume_checkpoint_2026_09_26 records completed and remaining work. Older cleanup prerequisites below are superseded by this checkpoint and the Governor maintenance policy.

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

- Root runner recurrence isolated: the scheduled watchdog can terminate while leaving a stale `Runner.Listener.exe`; GitHub then leaves jobs queued with `runner_id=0` even though a listener process still exists.
- Permanent runner policy remains interactive-user watchdog ownership, not the legacy Windows service. The installer now keeps `actions.runner.*` stopped/manual, adds a five-minute repeating self-heal trigger in addition to AtLogOn, and the watchdog recycles an orphaned listener on supervisor restart only when no `Runner.Worker` is active.
- The existing 150-second acknowledged-job-without-worker recovery remains in place.
- Validation classifier now supports transitive CORE proof inheritance across first-parent preparation-only commits. A runtime/asset delta can therefore run build/import/runtime audits without repeating Cook/Package when an earlier green core ancestor exists and every intervening commit is explicitly preparation-safe.
- Unsafe intervening files fail closed and force FULL validation.
- Static validation now guards both the watchdog self-heal contract and the transitive core-proof contract.
- Pre-Unreal no longer downloads/installs Python with `actions/setup-python`; it resolves the already installed local interpreter and runs under `cmd`, removing the repeated setup overhead and the execution-policy failure seen on #988 under the wrong service identity.
- Warehouse staging no longer runs on pull-request synchronize events; source/manifest changes stage once after integration to `develop`, while Pre-Unreal statically guards the warehouse workflow. This removes repeated provider/audit passes from maintenance commits.
- Live evidence before this change: Unreal #821 on exact C2 head `2af6648209d8722247ca6f9a75b2b5082b6654d5` completed Editor build, production import, Automation QA, startup smoke, chapter audit, route/state audit, warning guard, Cook and Runtime Data verification successfully; it then failed only at packaged executable launch. This demonstrates the waste the CORE path is intended to remove, but does not make #821 green.
- Evidence boundary for this hardening branch: **STATIC-VALIDATED SOURCE CHANGE / DEVICE WATCHDOG REINSTALL PENDING**. No PIE-TESTED, DEVICE-TESTED or performance claim.

## 2026-09-26 - P1C01 Poly Haven material staging wave V4 queued

- Warehouse manifest now lists a verified source-page record for every currently authorized Poly Haven material slug, including the Shire grass, woodland, soil, leaf-litter and rustic-path additions.
- Target remains 2K source intake; displacement/high-poly payloads remain excluded from this staging wave.
- The repaired Warehouse Stage workflow will run the real provider staging + SHA256 inventory audit on the supervised Windows runner.
- Evidence boundary: QUEUED FOR STAGING only; no STAGED/IMPORTED/INTEGRATED claim until receipts exist.

## 2026-09-26 - Warehouse staging removed from hosted-error path

- Warehouse staging now triggers from `develop` / relevant PR deltas instead of the obsolete comprehensive-foundation branch.
- GitHub-hosted delta/no-stage jobs were removed; one supervised Windows job stages Poly Haven, OpenGameArt, Quaternius, ambientCG, Kenney and KayKit and audits the persistent warehouse.
- Warehouse has its own concurrency group, so it no longer shares/cancels the UE4 validation group.
- PG-168 prevents regression to hosted runners or the obsolete branch trigger.
- Evidence boundary: workflow/source configuration only; a real warehouse staging receipt is still required before STAGED claims.

## 2026-09-26 - CI validator synchronized with the new supervised runner policy

- PG-026 now allows only acceptance/* or the sole active production/* PR to cancel superseded shared-device work.
- PG-167 now enforces event-driven self-hosted Pre-Unreal/Branch Cleanup and the preparation-only Unreal queue isolation contract.
- This removes a validator contradiction that would otherwise reject the newly adopted CI policy before repository tests could run.
- Evidence boundary: STATIC source correction; fresh supervised-runner execution still pending.

## 2026-09-26 - CI zero-step root bypass installed

- Recurrent hosted `steps=null` / BlobNotFound failures are removed from the critical path: Pre-Unreal and Branch Cleanup now run only on the supervised self-hosted Windows UE4 runner.
- The 20-minute Pre-Unreal schedule is removed.
- Unreal Build Validation now ignores CI/docs/known preparation-only deltas so the single UE device lane is reserved for runtime-relevant work.
- `Scripts/run_local_static_validation.ps1` mirrors the full static/governor/audit/unit-test chain for direct local execution independent of GitHub-hosted workers.
- Evidence boundary: STATIC SOURCE CHANGE ONLY until the supervised runner executes these workflows.

## 2026-09-26 - Immediate branch integration policy and dead-ref cleanup

- **Owner rule:** completed temporary branches must merge meaningful work into `develop` immediately, then delete the branch ref.
- **Safe dead refs queued now:** `ci/pr80-hosted-zero-step-fallback-20260926`, `production/w01-p1c01-hobbiton-bagend-v1`, `production/w01-p1c01-kickoff-v1`, `production/w01-p1c01-materials-vegetation-v1`, `production/w01-p1c01-world-foundation-v1`, `warehouse/p1c01-bulk-intake-v2`, plus this finished stability branch after merge.
- **Active work preserved:** PR #80 `production/w01-p1c01-foliage-wind-v2`, PR #81 `planning/whole-game-world-build-v1`, and `planning/whole-game-production-prep-v2`.
- **Unique-content quarantine:** old foliage-wind-v1, localization prototype and mega-prep branches are not deleted yet because they still contain commits unique versus develop; useful content must be selectively salvaged first.
- **Evidence boundary:** repository/process hygiene only; no runtime acceptance change.


## 2026-09-26 - P1C01 source-to-production bridge and local material pipeline

- **Source packet:** `Data/P1C01SourceExtractionV1.json` converts the supplied PDFs into a compact Shire/Hobbiton/Bag End implementation packet while preserving source priority and VISUAL-ONLY boundaries.
- **Production bridge:** `Data/P1C01SourceToProductionBridgeV1.json` maps source-grounded needs directly to the active material/warehouse candidate lanes.
- **One-command local path:** `Scripts/run_p1c01_material_pipeline.ps1` stages Poly Haven + ambientCG, audits warehouse receipts/hashes, prepares the P1C01 material intake, and can optionally call the real UE4 production importer with `-RunUnrealImport`.
- **CI independence:** this local preparation/import entry point exists specifically so public-source/material work can continue when GitHub-hosted checks or the Actions queue are unavailable; it does not bypass technical validation.
- **Evidence boundary:** tooling is authored but not claimed as UE4-import-tested in this session because no self-hosted UE4 commandlet log has run on this branch.

## 2026-09-26 - Massive build accelerated with source-PDF indexing and material-intake tooling

- **Parallel preparation authorized:** source/PDF, warehouse, materials, audio, character/animation and later-region preparation may proceed together; runtime-changing integration remains serialized.
- **Source PDFs indexed:** `Data/ProjectSourcePdfRegistryV1.json` records 15 owner-supplied PDFs by page count, byte size, SHA256 and authority role. Large source PDFs are not added to Git history.
- **Smart fence active:** `Data/FastProductionSmartFenceV1.json` downgrades administrative-only friction to warning/pending states while keeping technical/runtime/performance safety blocking.
- **P1C01 material intake:** `Data/P1C01MaterialImportWaveV1.json` selects eight Poly Haven CC0 Shire/Bag End surface families at the existing 2K intake target, with ambientCG fallback.
- **Import tooling added:** `Scripts/prepare_p1c01_material_intake.ps1` prepares deterministic BaseColor + MTL input from staged warehouse receipts; `Scripts/promote_p1c01_material_intake.ps1` can feed those materials through the existing production importer using a temporary source overlay that is always removed afterward.
- **Material master boundary preserved:** extra PBR maps are staged only; the current master remains AlbedoTexture + Color + scalar Roughness/Metallic until a separately gated material-cost pass.
- **Source architecture bug carried forward:** migrated source paths are synchronized to the actual Public/Private layout on this lane.
- **Evidence boundary:** STATIC/PREPARATION. No UE4 material import success is claimed until a real self-hosted intake receipt and commandlet log exist.

## 2026-09-26 - Whole-game reuse, streaming and pooled-population architecture prepared

- **Asset-family reuse:** `Data/WholeGameAssetFamilyCoverageV1.json` aggregates the 28 region packets into shared production families so repeated technical kits can be reused without erasing region-specific hero identity.
- **Streaming residency:** `Data/WholeGameStreamingResidencyPlanV1.json` defines GLOBAL_TINY / REGION_ACTIVE / TRANSITION_OVERLAP / WAREHOUSE_ONLY tiers, soft-reference ownership, async FStreamableManager loading and post-commit handle release.
- **Population architecture:** `Data/WholeGamePooledPopulationPlanV1.json` centralizes NPC/fauna pool admission under `LivingWorldDirector`, bounded context under `ShireNPCContextSubsystem`, quest facts under `ShireQuestSubsystem`, and forbids Spawn/Destroy bursts and global per-frame NPC scans.
- **Low-spec objective:** these plans explicitly prevent the massive production campaign from turning into a global hard-reference or always-resident world that would exceed the 8GB RAM / ~2GB VRAM target.
- **Evidence boundary:** PREPARATION only. No runtime memory, AI or performance acceptance is claimed.

## 2026-09-26 - P1C01 downstream production stages prepared

- **D prepared:** low-cost lighting/sky/fog/water plan with chapter-state ownership and no density escalation.
- **E prepared:** character presentation plan with FBX-only animated intake, soft references, async loading, retarget/LOD/shadow evidence and pooling boundaries.
- **F prepared:** Living Shire plan extends `LivingWorldDirector`, `ShireNPCContextSubsystem`, `ShireQuestSubsystem`, bounded dialogue/memory/social plans and pooled fauna without a parallel AI brain or per-NPC global polling.
- **G prepared:** quest/cinematic/audio polish plan preserves DEC-038 locked beats, bounded control loss, original dialogue, save/route continuity and audio subsystem ownership.
- **H prepared:** target-device profiling plan locks the i7 Gen6 / 8GB / ~2GB VRAM / DX11 / 720p Low-Medium / 30 FPS floor evidence route.
- **Gate 6/7 prepared:** `Data/P1C01Gate67AcceptanceChecklistV1.json` separates static/compile/PIE/device/visual/performance proof so no preparation state can be mislabeled as acceptance.
- **Runtime remains serialized:** these are preparation artifacts only; PR #80 C2 is still the sole runtime-changing lane.

## 2026-09-26 - Massive production preparation resumed without opening another runtime lane

- **Preparation branch:** `planning/whole-game-production-prep-v2` continues from PR #81 preparation head and is intentionally not opened as another runtime-changing PR.
- **Whole-game execution:** `Data/WholeGameProductionExecutionQueueV1.json` now drives all 28 existing region packets across BPB-W1..W9 while preserving the P1C01 Gate 6/7 runtime barrier.
- **P1C01 benchmark intake:** `Data/P1C01WarehousePromotionQueueV1.json` defines 28 concrete already-registered candidates across Shire/Bag End surfaces, support architecture/interiors, fauna review, support stock and audio/foley.
- **Asset promotion guard:** `Data/ProductionAssetPromotionPolicyV1.json` locks provenance, FBX-only animated production intake, PNG/TGA textures, WAV masters, 1K/2K defaults, soft-reference/async loading, pooling and ISM/HISM requirements before promotion.
- **Fail-closed sourcing:** Quaternius farm animals remain blocked at license capture because the current manifest does not record an observed per-pack license; no license was inferred.
- **Evidence boundary:** PREPARATION / STATIC DATA AUTHORING only. No new COMPILE/PIE/DEVICE/VISUAL/PERFORMANCE acceptance is claimed.

## 2026-09-25 - Source-grounded post-Amon-Hen promotion graph added

- Added `Data/WholeGameRoutePromotionGraphV1.json` from the supplied `01_STORY_AND_TIMELINE_BIBLE` and `07_MISSION_AND_CHAPTER_IMPLEMENTATION_MATRIX`.
- After Amon Hen, production/runtime planning is explicitly multi-threaded rather than falsely linear: Rohan, Ring-bearer, Gondor and late-Rohan lanes advance through synchronization barriers.
- F2-01 through F3-07 chapter titles, locations and locked outcomes are recorded in the graph from project sources.
- Shared cinematics/world-state changes wait for required peer-route barriers; local playable safe windows remain allowed under DEC-038.
- This is planning only. P1C01 remains the sole active runtime benchmark until Gate 6/7.

## 2026-09-25 - Whole-game region production packets created

- Added `Data/WholeGameRegionProductionPacketsV1.json` on the global preparation lane.
- Every registered world region now has a concrete production packet covering sourcing families and deliverables for terrain, materials, vegetation, architecture/interiors, water, lighting, characters, LivingWorld, audio, interactions, cinematics, collision/navmesh, streaming/memory, profiling and acceptance.
- Packets are PREPRODUCTION only outside P1C01 until Gate 6/7; they are not runtime-integration claims.

## 2026-09-25 - Whole-game world build campaign prepared in parallel

- New preparation branch: `planning/whole-game-world-build-v1`, based on canonical `develop@4980c3c8...`.
- Added `Data/WholeGameWorldBuildCoverageV1.json`, covering every world location in `TrilogyProductionAssetWarehouse.json`.
- Every region now has the same required build layers: canon beats, playable safe windows, terrain, materials, vegetation, architecture, interiors, water, lighting/sky/fog, characters, NPC life, fauna, audio/foley, quests/interactions, cinematics, UI/localization, collision/navmesh, streaming/memory, performance profiling and human visual/pacing acceptance.
- P1C01 remains the only active runtime benchmark until Gate 6/7. All later regions are preparation/authoring/warehouse lanes only for now.
- This campaign operationalizes DEC-038 globally and consumes the DEC-039 resource registry without allowing assets to redefine canon.

## 2026-09-25 - Master External Resource Bible audited and adopted

- Audited the uploaded 68-page `SHIRE_JOURNEY_MASTER_EXTERNAL_RESOURCE_BIBLE_V1_2026-09-25`, containing 225 classified external sources/tools.
- Adopted it globally as sourcing authority through Governor decision `DEC-039`; it does not override story/canon sources or `DEC-038`.
- Created `Data/MasterExternalResourceBibleAdoptionV1.json` with high-value adoption groups, conditional sources, reference/quarantine sources, disabled/redirected legacy sources and eight structured source waves.
- Expanded `Data/GlobalWarehouseSourceRegistryV2.json` from 102 to 142 registered sources/tools on the first adoption pass.
- Corrected `REPLICA_STUDIOS` to DISABLED and added redirects for legacy Unreal Marketplace, Texture Haven, CC0 Textures, old ArmorLab and Terrain.party routes.
- Added high-value missing lanes including SpeedTree, Xfrog, Globe Plants, Material Maker, Materialize, ActionVFX, EmberGen, AccuRIG, MakeHuman, DeepMotion, Plask, Cascadeur, Scott Buckley, FreePD, Tabler Icons, Google Fonts, Poedit, USGS EarthExplorer, OpenTopography, QGIS, Gaea, World Machine, RealityScan, Meshroom, MeshLab, CloudCompare, Blender, GIMP, Krita, Audacity, REAPER and native UE4.27 AI/localization references.
- Created `Data/BigProductionBuildLaunchV1.json` with nine whole-game production waves: surfaces; biomes; characters/animation; architecture/interiors; VFX/weather; audio/foley; music; terrain/scanning; Arabic/UI.
- Truth boundary: registered/adopted sources are not automatically downloaded, READY_FOR_IMPORT, integrated or accepted. Existing evidence-state ladder remains binding.

## 2026-09-25 - DEC-038 playable-film doctrine adopted

- The owner has formally defined Shire Journey as a **playable film-from-inside experience**, not a cutscene chain and not an unrelated open world.
- Locked film-continuity beats/outcomes remain immutable.
- Between locked beats, every chapter should expose bounded **interactive safe windows** for embodied third-person exploration, optional conversations, household/world interactions, NPC life, fauna, environmental storytelling and side activities where canon allows.
- Player freedom may change local flavor, discovery, pacing, minor relationship/state and optional content, but may not contradict chronology or invalidate a locked film outcome.
- Cinematic/set-piece control is bounded and must return cleanly to the player.
- When control returns after a canon beat, NPC/world/prop/audio state must reflect the new story state.
- This doctrine is GLOBAL across the entire game from the opening through the final ending. F1-01/Bag End is only the first implementation benchmark; every later chapter/region must apply the same locked-beat + playable-safe-window pattern under its own canon constraints.
- F1-01 example: playable pre-party/Bag End/Shire life may surround the locked Bilbo/Ring transition, but the transition itself follows project film continuity rather than an invented contradictory handoff.
- Added dialogue in safe windows remains original project-authored text; no verbatim Tolkien/film dialogue.
- Authority: `Data/ProjectGovernor.json` decision `DEC-038`.

## 2026-09-25 - Owner private-offline asset policy adopted

- Owner policy is now recorded as `DEC-037` in `Data/ProjectGovernor.json`.
- New authority file: `Data/PrivateOfflineAssetPolicyV1.json`.
- Two explicit lanes now exist:
  - `PRIVATE_OFFLINE_ONLY`: commercial-clearance uncertainty does not block the owner's local/offline experimental build by itself. Assets stay tagged, replaceable and non-distributable.
  - `DISTRIBUTABLE_FRAMEWORK`: remains strict; only assets with clear redistribution/commercial entitlement may ship in the reusable/sellable Framework.
- Provider-access rules are unchanged: no login/paywall/DRM/anti-bot bypass or prohibited scraping.
- Private payload isolation root: `SourceAssets/PrivateOffline/`; payloads are ignored by Git and must not become hard dependencies of the distributable Framework.
- Bulk link/file intake registry is ready at `Data/PrivateOfflineAssetIntakeQueueV1.json`.
- GitHub repository visibility was checked through the connected repository metadata and is currently `private`.
- This policy changes asset classification/export eligibility only; it does not promote assets to READY_FOR_IMPORT/INTEGRATED/ACCEPTED without technical/engine evidence.

## 2026-09-25 - Parallel Warehouse bulk-intake V2 active

- Preparation branch: `warehouse/p1c01-bulk-intake-v2`, based on the current merged C1 baseline. This is **not** a second runtime-changing lane.
- Poly Haven batch advanced to V2 with additional source-page-verified CC0 Shire ground families: leafy grass, forest floor, damp soil, leaf litter, rustic pathway and organic ground detail. Intake remains 2K and skips displacement/high-poly payloads.
- Kenney batch advanced to V2 with additional CC0 cave/architecture support stock. These packs remain support/background stock, not hero LOTR art.
- Quaternius intake now requires an explicit per-pack observed license before automatic download. Packs without per-page license evidence are skipped instead of inheriting a blanket provider assumption.
- Verified Quaternius Farm Buildings is added as Shire support architecture with FBX as the required final format.
- OpenGameArt audio batch advanced to V2 with CC0 multi-surface footsteps, fireplace loop, 100 wood/metal SFX and bird ambience. Non-WAV intake sources must be converted/auditioned to WAV masters before UE import.
- Warehouse states remain honest: CANDIDATE/AUTHORIZED_FOR_STAGING/STAGED only. No READY_FOR_IMPORT, UE integration, PIE/device/visual/audio acceptance is claimed without matching receipts and later gates.
- Runtime PR #78 remains isolated; warehouse preparation continues in parallel so production does not idle during Unreal validation.

## 2026-09-25 - PR #77 handoff-status contract corrected

- Unreal #731 completed **SUCCESS** on corrected Drop C1 head `3b2281c17b6111fd30f7614ca5d0df22a6dc572d`.
- Pre-Unreal #896 reached the Governor and failed because `validation_snapshot.latest_observed.pre_unreal.status` used the descriptive token `FAILURE_VALIDATOR_PATH_ONLY`, while the handoff schema allows only `SUCCESS | FAILURE | CANCELLED | PENDING | IN_PROGRESS`.
- Root correction: status is now the contract-valid `FAILURE`; the validator-only explanation is stored separately in a `note` field. This prevents recurrence without weakening the schema.
- No C++/runtime/material implementation changed in this correction. Fresh exact-head Pre-Unreal is required before merge.

## 2026-09-25 - PR #77 validator false-red root-fixed

- Pre-Unreal #895 failed only because PG-165 incorrectly used the runtime `resolve_source()` helper for `ShireProductionImportCommandlet.cpp`, which lives in the separate `ShireJourneyEditorTools` module.
- Unreal #730 on the same exact head `725ca99151b5438fab7ce48209c04a4ce05c681d` completed **SUCCESS**, so the Drop C1 editor build/production-import/core engine path itself is proven on that head.
- Root correction: Pre-Unreal now has a dedicated `resolve_editor_source()` helper rooted at `Source/ShireJourneyEditorTools`; PG-165 uses that helper, preventing future editor-tool guards from being silently routed into the runtime module.
- This correction is validator/docs/governance-only. Fresh exact-head Pre-Unreal is required; engine proof may inherit only under the established safe validation-policy ancestry rules.
- Evidence boundary: Drop C1 is engine/core proven on the prior exact runtime head, but no PIE/device/visual material acceptance is inferred.

## 2026-09-25 - W01/P1C01 Drop C1 material texture binding implemented

- Parent `develop@712a81cac150b7fdb338a4cf7554d4f27d4b5191` is post-merge green: Pre-Unreal #894 SUCCESS + Unreal #729 SUCCESS.
- Active branch: `production/w01-p1c01-materials-vegetation-v1`.
- Verified source gap addressed: authored Shire MTL `map_Kd` entries are now carried into deterministic production material instances through an `AlbedoTexture` parameter.
- `M_ProductionSurface` creation now uses `AlbedoTexture * Color` for BaseColor while preserving Roughness/Metallic.
- Texture binding happens in the editor import commandlet after texture import; no gameplay runtime loading path is changed and no new synchronous heavy gameplay load is introduced.
- This is **STATIC-VALIDATED / EXACT-HEAD PRE-UNREAL + UE4.27.2 CORE PROOF PENDING**. Wind/WPO is not yet claimed; that is Drop C2 after C1 is engine-green.

## 2026-09-25 - PR #76 governance false-red corrected atomically

- Pre-Unreal #890/#891/#892 did not reach an Unreal runtime failure. The remaining red was the Governor handoff invariant: `session_handoff.source_head` must equal `validation_snapshot.last_green.sha`.
- Last-green proof is now recorded consistently as `b9a312ce2321f55a58bc5f24dd478b4839871006` with Pre-Unreal #888 SUCCESS + Unreal #723 SUCCESS.
- Branch/PR surfaces already agree on `production/w01-p1c01-hobbiton-bagend-v1` / PR #76. This correction updates the baseline/evidence tuple in one atomic commit to avoid another chain of self-triggered governance runs.
- Drop B architecture remains STATIC-VALIDATED until fresh exact-head Pre-Unreal + UE4.27.2 core green.

## 2026-09-25 - W01/P1C01 Mega Production Drop B implemented

- Parent: `develop@430d0a26f3b441f072740fc58285c0c0eb842d8c` after PR #75 merge.
- Active branch: `production/w01-p1c01-hobbiton-bagend-v1`.
- Drop B adds a bounded Hobbiton/Bag End architecture pass using already-resident production meshes: Bag End hero approach/property framing, domestic garden clusters, village common, Party Field dressing and working-Shire props.
- Canon correction: visible Green Dragon-at-Hobbiton presentation was removed because the inn belongs at Bywater. The legacy `Discover_GreenDragon` ID remains unchanged for save compatibility.
- Bag End interior remains explicitly incomplete because no dedicated production interior shell exists yet; no false completion is recorded.
- Added PG-164 regression protection and synchronized architecture/performance plans.
- Status: **STATIC-VALIDATED / EXACT-HEAD PRE-UNREAL + UE4.27.2 CORE PROOF PENDING**.

## 2026-09-25 - PR #75 core engine proof passed; package red isolated to classifier/base-fetch path

- Unreal #721 attempt 2 reached and passed the required **core** chain on exact head `5a58c8d3d33f07a2b3440f0ab85e42ca20c00695`: ShireJourneyEditor build, production import, Automation QA, startup smoke, P1C01-P1C08 runtime audit, route/state audit and warning-debt guard all succeeded.
- The overall workflow red was **not** a C++/runtime failure. The classifier could not resolve the PR base because the stable checkout fetched only the PR head at depth 2; it fell back to `full` with `reason=delta-unavailable-fail-safe`.
- That unnecessary full lane then failed inside the legacy W00 package helper before cook at `W00_DBGHELP_DESTINATION_WRITE_FAIL`: access denied while probing the staged `dbghelp.dll` destination.
- This delta is ordinary C++/Data/world-production work, so project policy requires the **core** lane and no package/cook. The classifier now fetches the explicit PR base SHA on demand and retries the diff before any full-lane fail-safe.
- Drop A remains source-complete and core-engine-proven on the previous exact head; the new classifier head still requires fresh Pre-Unreal + Unreal core workflow success before merge.

## 2026-09-25 - W01/P1C01 Mega Production Drop A started

- Canonical parent: `develop@ec3208919910b58bd6a87ce59c17e31312bd7bab` with Pre-Unreal #885 SUCCESS + Unreal #720 SUCCESS.
- Active branch: `production/w01-p1c01-world-foundation-v1`; intended PR: #75 targeting `develop`.
- W00 remains closed. PR #74 ambient ownership + budget authority is merged and machine-green.
- Drop A implements the first production-world dependency: Shire terrain/geography foundation using deterministic HISM hills/slopes/riverbanks, explicit cull ranges and preserved quest/story anchors.
- The old repeated actor-owned CP49 terrain silhouette layer is removed in favor of instancing. Existing broad collision foundation and startup grounding contracts are untouched.
- Source-backed order remains: terrain/geography -> Hobbiton/Bag End -> materials/vegetation -> lighting/sky/fog/water -> character presentation -> living Shire -> quest/audio polish -> target-device profiling -> Gate 6/7.
- Regression guard: PG-163 now enforces instanced geography ownership/cull bands and rejects a return to repeated terrain actor spawning.
- Status: **STATIC-VALIDATED / EXACT-HEAD PRE-UNREAL + UE4.27.2 CORE PROOF PENDING**. No new PIE/device/visual/performance acceptance is claimed.

## 2026-09-25 - PR #74 repeated red isolated to incomplete W00->W01 governance transition

- Pre-Unreal #882 and #883 did **not** report an Unreal/runtime regression. They failed in Project Governor coherence because some fields still described the old W00 control point while current_focus/execution_control had already moved to W01.
- #883 errors were branch/PR handoff mismatch, development-mode mismatch, stale blocking W00 gate/freeze assumptions, MASTER_EXECUTION_BOARD still on PR #73, and a stale legacy handoff baseline.
- Root cause: the W00 -> W01 control-plane transition was only partially updated across governance surfaces. This is metadata/governance drift, not evidence that the ambient-ownership C++ change failed.
- Correction is being applied as one atomic multi-file commit so the branch produces one new validation head rather than another sequence of self-triggered runs.
- Status remains **STATIC-VALIDATED / FRESH PRE-UNREAL + UE4.27.2 CORE PROOF PENDING**.

## 2026-09-25 - W01 validator follow-up after Pre-Unreal #881

- Pre-Unreal #881 failed on the first W01 head because PG-035/PG-036/PG-111 still encoded the pre-W01 builder-owned Shire ambient implementation: they required direct Shire builder bird/activity assignments and the old WorldLifeSaturationPlan status.
- This was validator drift against the intentional single-owner architecture, not evidence that the new runtime ownership change failed in UE4.
- `Scripts/pre_unreal_validate.py` now validates Shire activity props through `LivingWorldDirector::ChooseBaselineProp`, Shire bird life through the P1C01 `FAUNA` + `EVT_FAUNA_BIRDS` data contract, the new single-owner world-life status/authority, and explicitly rejects any return of `SpawnActor<AShireAmbientNPC>` to `ShirePrototypeWorldBuilder`.
- Fresh exact-head validation is running on `03e886a6ecc0673680975b11fdda3fbc711041d2`: Pre-Unreal #882 in progress; Unreal #717 pending at the time of this record.
- Evidence boundary remains **STATIC-VALIDATED / FRESH ENGINE PROOF PENDING**.

## 2026-09-25 - W01 drop 1 implemented: ambient single ownership and budget authority

- Branch: `production/w01-p1c01-kickoff-v1`.
- `ShirePrototypeWorldBuilder` no longer creates its own `AShireAmbientNPC` population. Ambient crowds are now owned by `ALivingWorldDirector` and therefore use its existing object pool, culling, target density and danger-thinning path.
- Named/story NPCs and quest actors remain builder-owned; this change does not transfer canonical story ownership to the ambient system.
- `LivingWorldEventPlan.json#region_budgets` is now the sole runtime authority for micro-event caps and event-start cadence. `WorldLifeSaturationPlan.json` is baseline-population density/role authority only.
- P1C01 `PlayRunner` remains in the director-owned role set so the pre-adventure playful Shire beat is not silently lost when duplicate builder crowds are removed.
- Static source checks: direct builder ambient spawn count = 0; old life-saturation micro-event override reads = 0.
- Status: **STATIC-VALIDATED / FRESH PRE-UNREAL + UE4.27.2 COMPILE/RUNTIME PROOF PENDING**. No new PIE/device/visual/performance acceptance is claimed.

## 2026-09-25 - W00 closed; W01/P1C01 production vertical slice opened

- Canonical W00 close head: `develop@809e56a9e1dc4b453e02a0b04b6875a71df21933`.
- GitHub evidence on that head: Pre-Unreal #880 SUCCESS; Unreal #715 SUCCESS via the explicit validation-policy-only inherit path; Branch Cleanup #3 SUCCESS with only `develop` and `main` remaining.
- Owner-side P1C01 PIE evidence on the Documents clone: `ShireStartupGrounding: PASS chapter=P1C01 commitBarrier=yes stableSeconds=2.0 ground=yes drop=1.8 drift=0.0`; player remained grounded; owner reported no same-session Output Log matches for `Mobility is Static` or `SetStaticMesh`.
- W00 architectural/root-repair lane is therefore **CLOSED**. Reopen it only for a concrete regression. This does not promote whole-chapter PIE, DEVICE-TESTED, VISUALLY-ACCEPTED or PERFORMANCE-ACCEPTED status.
- W01/P1C01 is now the sole active production vertical slice. First code work remains: centralize ambient population ownership under `LivingWorldDirector` + pooling, then reconcile `LivingWorldEventPlan` vs `WorldLifeSaturationPlan` authority before any density increase.
- The owner-forwarded sensory/reactive review was checked against live source. Accepted additions are spatial environmental audio + surface foley, performance-scaled vegetation material motion, and later skeletal Look-At/Foot IK. Corrected stale claims: ambient NPC player awareness/weather reactions already exist; audio already has async routing/fades/ducking; ambient pooling already exists in `LivingWorldDirector`.
- Detailed accepted/corrected notes are registered in `Docs/WORLD_DETAIL_LEDGER.md` before implementation, satisfying the W01 scope gate.

## 2026-09-25 - W00 lessons lock after current develop machine-green
- Pre-Unreal #875 confirmed the PG-161 correction still used the wrong textual anchor (helper-function `Docs/` test instead of the main changed-file loop). The guard is now anchored inside `foreach($p in $changed)` so it inspects only the forbidden ordinary-safe branch. Exact-head rerun pending; this remains validator self-test work, not a game regression.
- Pre-Unreal #871 exposed one self-test false positive in the new PG-161 guard: it confused the required explicit validation-policy-only path with forbidden ordinary metadata classification. The guard is narrowed structurally (PG-164); exact-head rerun is pending. This is validator logic, not an Unreal/game regression.
- Current canonical `develop@ed3587aa9d1f0025a5f10778a6be8048e2c778d1` is now **COMPILE-TESTED + HEADLESS/PACKAGED-RUNTIME-VALIDATED** by Pre-Unreal #869 SUCCESS and Unreal #704 SUCCESS.
- #704 passed UE4.27.2 editor build, production import, Automation, startup, P1C01-P1C08 runtime sweep, route/story roundtrip, warning-debt guard, Windows cook/package, 37 packaged Runtime Data JSON verification, packaged startup and hardware snapshot. This does **not** promote DEVICE-TESTED, VISUALLY-ACCEPTED, PERFORMANCE-ACCEPTED, or final human PIE acceptance.
- Two-day regression memory is being locked before W01: PG-161 prevents redundant full UE/package work across cancelled metadata parents by allowing only path-bounded safe-ancestry proof reuse; PG-162 locks immutable temp-copy local launchers; PG-163 locks develop/main-only programmer handoff discipline.
- Root cause of the redundant #704 cook was classifier ancestry semantics, not a gameplay/package defect: a cancelled immediate metadata parent hid still-valid nearby green proof and triggered the fail-safe FULL lane. The classifier now has explicit safe transitive governance proof and validation-policy-only inheritance while remaining fail-closed for runtime/assets/config/streaming/packaging changes.
- W00 remains open only for the final owner-side canonical-develop P1C01 PIE tail: `ShireStartupGrounding: PASS`, no fall, and no project-owned `SetStaticMesh ... Mobility is Static` warning. The local immutable-launcher rerun is captured in the same session.
- No new gameplay feature wave starts before that evidence. If clean, close W00 and immediately open the P1C01 Shire production vertical slice under Gate 6/7.

## 2026-09-25 - Post-cleanup canonical handoff
- Remote branch cleanup is **complete**: Branch Cleanup run #1 succeeded and a live repository query returned exactly two branches: `develop` and `main`.
- `develop` is now the sole canonical development/programmer-handoff lane; `main` remains stable release/scheduler ownership only.
- No historical feature/repair PR remains open. The final metadata-only PR #72 exists only to remove stale PR #70 references from governance/docs and self-registers for deletion after merge.
- Consolidated develop after PR #70 is `3108b2dd6354b196d36406935057c25feab2fec2`; post-merge Pre-Unreal #865 succeeded. Exact post-consolidation Unreal #700 has not been claimed green here.
- W00 remains **AUTOMATED_CLOSURE_GREEN_HUMAN_PIE_WARNING_TAIL_PENDING**. The remaining owner-side proof is one P1C01 PIE observation with `ShireStartupGrounding: PASS`, no player fall, and no project-owned `SetStaticMesh ... Mobility is Static` warning.
- No DEVICE-TESTED or VISUALLY-ACCEPTED status is promoted by repository cleanup.

## 2026-09-25 - Final consolidation pass on PR #70
- Final branch target for programmer handoff is now exactly **`develop`**; `main` remains release-only. The temporary generated-audio archive ref is also approved for deletion because its branch-only diff contained Data/Docs metadata, not WAV/UE binary masters, and the valid registries are already consolidated.
- PR #70 is now the **single** maintenance consolidation train. The parallel PR #71 payload was selectively folded into #70; #71 is to be closed as superseded.
- Branch cleanup is finalized for post-merge execution: preserve only `develop` and `main`; approved stale refs are deleted by `.github/workflows/branch-cleanup.yml` after the cleanup plan lands on `develop`.
- Historical diverged runtime branches were audited rather than bulk-merged. Old pre-Public/Private runtime paths are superseded; only still-valid unique planning/audio/ops records were salvaged.
- Generated-audio registries for the 103 scripted cues, P1C01 ambient speech, P1C01 complete-bank contract and named-character efforts are now consolidated in sanitized form without expiring signed delivery URLs. This is registry/intake evidence only, **not** UE playback/audio acceptance.
- Both local launch controllers (`SHIRE_UPDATE_BUILD_LAUNCH.bat` and `SHIRE_PIE_VERIFY.bat`) execute from immutable temp copies so `git pull` cannot rewrite the batch currently being parsed. Local rerun proof remains pending.
- Unreal validation cost contract is corrected: ordinary C++/runtime/Data/SourceAssets deltas use the **core** lane (build/import/Automation/runtime/warning checks) with **no package/cook**; Config/Build.cs/Target.cs/chapter-streaming/Package/Cook/Release deltas use the full package lane. Governance/docs/offline-maintenance deltas inherit green parent proof.
- W00 remains **AUTOMATED CLOSURE GREEN / HUMAN PIE WARNING TAIL PENDING**. No new PIE/device/visual/performance acceptance is claimed by this maintenance pass.

## 2026-09-25 - Develop consolidation / branch cleanup
- Canonical development lane remains `develop`; stable release lane remains `main`.
- W00 automated machine closure is green on `develop@9066d649...` via Pre-Unreal #821 and Unreal #656, inheriting full core UE4.27.2 proof from parent `fdbb6492...` / Unreal #655. Human P1C01 PIE grounding/warning-tail evidence is still pending and is not promoted here.
- PR #70 is the active maintenance-only consolidation lane. Stale PR #62, #63 and #66 were closed as superseded; they must not be bulk-merged.
- The local one-click launcher now executes from a temporary stable copy so a `git pull` cannot mutate the running batch file and corrupt branch detection.
- Unreal validation now separates ordinary runtime/source/data changes from package/cook changes and classifies PRs against the canonical base SHA rather than only the previous branch commit; this prevents cancelled intermediate branch runs from forcing unnecessary full/package validation. Core runtime changes run build/import/Automation/runtime/warning gates without packaging; Build.cs/Target.cs/Config/streaming/packaging-critical changes still force the full package path.
- Planning/warehouse records missing from canonical develop were salvaged: `LivingWorldSensoryCompletenessPlanV1.json`, `VoiceProductionMasterPlanV1.json`, `operation_recovery.py` + tests, and `WarehouseGapAuditSource09V1.json`.
- Generated-audio intake metadata is consolidated directly into the canonical lane; no separate archive branch is required. Sanitized canonical registries for scripted voice, P1C01 ambient speech/barks, complete audio-bank coverage and named-character efforts are now also present on the consolidation lane; signed external download URLs are intentionally excluded.
- `Data/BranchCleanupPlan.json` + `.github/workflows/branch-cleanup.yml` will remove approved stale remote branches after PR #70 lands on develop while preserving develop/main and explicitly retained audit/archive refs.

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

## 2026-09-25 - Unreal #651 Attempt 2 closes automated W00 package/startup chain; runner background path proven

Exact head `efdb2e291505472247fae921945b083b3cc1ce2c` completed the repaired machine path successfully after the foreground legacy `run.cmd` session was removed and the user-context watchdog-owned runner remained active.

Fresh evidence:
- Pre-Unreal #816: SUCCESS.
- Warehouse #232: SUCCESS; hosted delta gate selected the no-delta fast path and the self-hosted Warehouse stage was skipped.
- Unreal #651 Attempt 2: SUCCESS.
- `Build ShireJourneyEditor`: SUCCESS.
- production import, Automation QA, playable startup, P1C01-P1C08 runtime audit, route/story roundtrip and warning-debt guard: SUCCESS.
- `W00_PACKAGE_PASS elapsedSeconds=182`.
- `W00_PACKAGED_DATA_PASS expected=37 verified=37`.
- `W00_PACKAGED_STARTUP_PASS observed=6s`.
- `W00_RUNNER_HARDWARE_SNAPSHOT_PASS cpu=Intel(R) Core(TM) i7-6498DU CPU @ 2.50GHz ramBytes=8457560064`.

The packaged-startup verifier requires the runtime marker `ShireStartupGrounding: PASS chapter=P1C01`, so automated packaged grounding reached that marker on #651. This is not human PIE evidence and does not close the player-fall issue by itself.

Runner conclusion: the previous zero-step ten-minute failures are no longer treated as project-code failures. Their timing and shape match the still-open upstream GitHub Actions runner acquire-job hang family, while the local mitigation is to keep the runner under the proven Windows user context, keep the legacy NetworkService service disabled/manual, isolate Warehouse from the UE4 device unless a real Warehouse delta exists, and supervise the listener externally. #651 proves normal background execution after this architecture change; the watchdog's forced recovery branch itself has not yet been observed firing in production.

Status: **AUTOMATED W00 CHAIN GREEN / HUMAN PIE GROUNDING PROOF PENDING**. Do not rerun green automated gates unless a dependency that can invalidate them changes.

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

## 2026-09-24 - W00 checkpoint CP-W00-156: one concrete PG-026 validator-drift repair

CP155 exact head `3534e632e2085351149648aa7ec2d9b88d0badf1` completed **Unreal #625 SUCCESS** and **Warehouse #206 SUCCESS**. **Pre #790 failed only PG-026** before the rest of the static chain because the validator hard-coded the exact checkout as `--depth=1`.

CP155 intentionally changed the bounded shallow checkout to `--depth=2` so the new fail-safe validation classifier can inspect the direct parent. Exact-head safety did not change: the workflow still resets hard to `TARGET_SHA`, rev-parses HEAD, compares the exact SHA, records `.ci-source-sha`, and fails on mismatch.

CP156 changes only PG-026's structural contract to accept bounded shallow depth **1 or 2** while retaining all exact-SHA requirements. No gameplay/runtime logic changes. If fresh Pre-Unreal is green, the machine-repair lane closes and W00 proceeds only to packaged Data JSON, real authored audio, target-device profiling and human PIE/pacing/visual acceptance.

## 2026-09-24 - W00 checkpoint CP-W00-155: final consolidated repair-closure wave

Head `f524a83cd39510b956e4977571448d43100b628d` passed **Unreal #624 SUCCESS** and **Warehouse #205 SUCCESS**. Unreal #624 completed UE4.27.2 build/import, Automation, startup, P1C01-P1C08, state, transitions, faults, pending, persistence-edge and zero-warning-debt checks; material persistence reported `missing=0 tracked=225`.

Pre #789 failed at one governance invariant only: `PG-078: tracked unfinished requirement snapshot is stale`. The exact mismatch is `REQ-ORG-001`, correctly VALIDATED in ProjectGovernor but still present in MasterExecutionRoadmap's unfinished snapshot. CP155 reconciles that snapshot without weakening the validator.

The same final wave adds explicit already-resident bank recommit runtime evidence and a fail-safe Unreal fast path for governance/docs-only deltas whose direct parent already has successful Unreal evidence. Any source/runtime/CI/config/asset or unknown delta still runs the full UE4.27.2 chain.

This is the last planned root-repair wave. CP155 gets one full run because it changes CI/runtime audit contracts. After it is green, root-code/validator/Governor cleanup stays closed unless a concrete new regression appears; W00 proceeds only to packaged Data, real audio, target-device profiling and human PIE/pacing/visual acceptance.

No PIE/device/visual/performance acceptance is claimed here.

## 2026-09-24 - W00 checkpoint CP-W00-154: exact-head machine-green reconciliation

Exact head `ab7889d6b2dafc059220a0c0a3dc63decfe6b72e` is now **STATIC-VALIDATED + COMPILE-TESTED + HEADLESS-RUNTIME-VALIDATED**: **Pre-Unreal #788 SUCCESS** (run 35929433094), **Unreal Build #623 SUCCESS** (run 35929433086), and **Warehouse #204 SUCCESS** (run 35929433089).

Pre #788 completed the full project-structure/Governor/asset-quality/readiness/deep/unit-test chain. Unreal #623 completed exact checkout, migrated-layout preparation, UE4.27.2 verification, MSVC setup, clean intermediates, ShireJourneyEditor build, production asset import, Automation Framework QA, startup smoke, P1C01-P1C08 headless chapter audit, route/story state roundtrip and warning-debt guard. Warehouse #204 correctly detected no staging-required delta and skipped heavy provider stages.

The Public/Private migration and its known validator/persistent-runner correction families are therefore **machine-accepted on CP-W00-154**. Do not reopen root-code/validator/Governor cleanup unless a new concrete regression appears. W00 remains open only for packaged Data JSON runtime proof, real authored audio playback, target-device profiling and chapter-specific human PIE/pacing/visual acceptance.

No **PIE-TESTED**, **DEVICE-TESTED**, **VISUALLY-ACCEPTED** or **PERFORMANCE-ACCEPTED** claim is made by this machine evidence.

## 2026-09-24 - W00 checkpoint CP-W00-153: migration-consumer and persistent-runner repair

CP152 head `9acc72b16e058a422428389fcefeb9af12fa0e98` has the intended physical Git tree: zero flat runtime .h/.cpp files, 32 headers under `Public/<Domain>` and 30 implementations under `Private/<Domain>`. Warehouse #202 succeeded.

Its proof failed in two concrete migration-tooling families. Pre #786 still had historical direct reads such as `Source/ShireJourney/ShireGameMode.cpp`, so missing-file reads cascaded into false PG-109/129/131/133/136/137/138/140/142 failures. Unreal #621 reached UHT and failed on duplicate leaf headers because the persistent self-hosted worktree retained the old flat headers as **untracked leftovers** after the tracked files moved.

CP153 fixes both systemically without changing gameplay: all real Pre-Unreal source reads resolve migrated basenames, the central runtime-evidence registry points at actual `Private/<Domain>` paths, the streaming source-contract test is layout-aware, and the Unreal workflow removes only obsolete architecture-mapped legacy files after confirming their migrated targets exist.

Status: **SOURCE-LAYOUT INTACT / MIGRATION INTEGRATION REPAIRED / EXACT-HEAD VALIDATION PENDING**. No PIE/device/visual/audio/package acceptance is claimed.

## 2026-09-24 - W00 checkpoint CP-W00-152: isolated Public/Private runtime-source migration

Exact CP151 head `92f6d3aaad79f33eaf2385de292e6886d2c1b5da` is the new fully machine-green baseline: **Pre-Unreal #785 SUCCESS + Unreal #620 SUCCESS + Warehouse #201 SUCCESS**. The full static/governor/asset/readiness/deep/unit-test chain passed, and Unreal #620 passed compile/import/Automation/startup/chapter/state/transition/fault/pending/persistence-edge/warning-debt coverage.

With the correction loop green, CP152 performs the already-approved architecture-only migration: all 62 runtime .h/.cpp entries move from the module root to their mapped `Public/<Domain>` and `Private/<Domain>` paths. Gameplay source blobs are unchanged. Build.cs no longer exports the entire module root; it exposes only explicit public domain include roots. Pre-Unreal and DeepProjectAudit now resolve runtime filenames recursively, and PG-154 rejects flat-root regression.

CP152 is **SOURCE-LAYOUT-MIGRATED / EXACT-HEAD VALIDATION PENDING** until fresh Pre-Unreal and UE4.27.2 proof. No PIE/device/visual/audio/package acceptance is claimed.

## 2026-09-24 - W00 checkpoint CP-W00-151: handoff evidence-lineage correction

Exact CP150 head `2259242a772d3dd21a90cc10a8a4a2761be3b3dd` passed **Unreal #619 SUCCESS** and **Warehouse #200 SUCCESS**. Pre-Unreal #784 also passed **PRE-UNREAL CORE VALIDATION**, proving the prior PG-056 NameError is gone, then stopped in `project_governor.py` on one data-lineage invariant:

`Legacy verified handoff must refer to the same last-green baseline`.

The validator is correct. `session_handoff.source_head` is the verified historical baseline and must equal `validation_snapshot.last_green.sha`; the newer partially proven candidate belongs in `validation_snapshot.latest_observed`. CP151 corrects only that Governor data and does not weaken or duplicate the handoff validator.

Status: **SOURCE/DATA-REPAIRED / EXACT-HEAD VALIDATION PENDING**. No PIE/device/visual/performance/audio-playback claim is added.

## 2026-09-24 - W00 checkpoint CP-W00-150: close the CP149 refactor regression

Exact CP149 head `e0b66dbccdf9e91f3cd6af0190008cf58ca31198` produced **Unreal #618 SUCCESS** and **Warehouse #199 SUCCESS**. Pre-Unreal #783 failed before the later static suite because PG-056 still referenced the local symbol `governor_mode_id`, which CP149 had intentionally removed while centralizing development-mode validation.

This is a validator execution regression, not evidence of a new gameplay/runtime defect. CP150 removes the orphan alias completely: PG-056 reads `development_mode.id` directly from the Governor data only to decide whether the historical PIE verification-freeze guard is active. The data-owned mode contract remains the sole validation authority.

CP150 status is **SOURCE-REPAIRED / EXACT-HEAD VALIDATION PENDING**. No PIE/device/visual/performance/audio-playback claim is added.

## 2026-09-23 - W00 checkpoint CP-W00-149: data-owned development-mode validation

CP-W00-148 parent `32af3140d1d297283de640144a58c3b32133d3d1` produced a clean split result: Unreal #617 SUCCESS and Warehouse #198 SUCCESS, while Pre-Unreal #782 stopped immediately on two PG-033 validator errors. No C++/runtime failure was reported by #617.

Root cause: PG-033 carried a second hard-coded list of acceptable development modes and inferred manual-proof honesty by searching rule prose for words such as PIE/evidence/device/visual/performance. The Governor's legitimate `W00_ARCHITECTURAL_STABILIZATION` mode therefore looked invalid to the validator.

CP-W00-149 moves mode IDs, supersedes relations and manual-only acceptance labels into structured `development_mode_contract` data owned by ProjectGovernor. Both Pre-Unreal and `project_governor.py` consume one shared `governance_contracts.py` helper, and unit tests guard unknown modes, supersedes drift, missing manual labels and prose-only fake proof.

Status of this child checkpoint: **SOURCE-REPAIRED / EXACT-HEAD VALIDATION PENDING**. No PIE/device/visual/performance/audio-playback acceptance is claimed and no completeness percentage changes.

## 2026-09-23 - W00 checkpoint CP-W00-148: Governor execution-truth hardening

Exact parent `96398e7cc48277324113c7879a8d28e3b659757e` is **STATIC-VALIDATED + COMPILE-TESTED + HEADLESS-RUNTIME-VALIDATED**: Pre-Unreal #781 SUCCESS, Unreal #616 SUCCESS and Warehouse #197 SUCCESS. #616 passed UE4.27.2 compile/import, Automation 2/2, startup, P1C01-P1C08, state/continuous-transition/fault/pending/persistence-edge modes and warning-debt guard. #197 detected no staging-required delta and skipped heavy provider staging by design.

The screenshot/log with `ShireRollbackAudit ... revisionAdvanced=no` belongs to older #615 on `6944cc0...`. #616 on the current parent passed the corrected split semantics.

The next audit found governance drift, not a gameplay regression: stale PR #61/#53 metadata, `VISUAL_PRODUCTION_FIRST`, broad production actions, direct-develop workflow text and a source hierarchy that could make supporting docs/backlog look authoritative despite the W00 freeze.

CP-W00-148 centralizes active-gate-first execution, explicitly freezes B1/B2/B3, reconciles PR #67/branch metadata and adds PG-150 so supporting management surfaces cannot drift silently. This child checkpoint is **SOURCE-REPAIRED / EXACT-HEAD VALIDATION PENDING** until fresh CI proves it.

No PIE/device/visual/pacing/audio-playback acceptance is claimed and no production-completeness percentage is increased.

## 2026-09-23 - W00 checkpoint CP-W00-147: separate invalid-request preflight from real rollback

Two reds were collected before this repair.

Pre-Unreal #780 on `6944cc0f...` failed PG-136 for `StartExperience`, but source inspection shows the authoritative subsystem identity still follows the correct order: transition intent is broadcast before bare `CurrentRouteId / CurrentChapterId / CurrentEpisodeId / PlayableCharacterId` mutation. The helper was falsely treating `TargetExisting->CurrentChapterId` and related route-progress sanitation fields as authoritative subsystem mutation. The structural helper is now qualifier-aware: writes through another object are ignored, while bare and `this->` member writes still count. DeepProjectAudit consumes the same helper.

Unreal #614 on parent `333cbd0d...` exposed a second stale assumption. The new identity preflight correctly logged `ShireExperienceIdentity: rejected ... chapter=P1C99` before any transition request. The legacy fault audit then failed only because it expected `revisionAdvanced=yes`. That expectation is now wrong by design: a request rejected before transaction publication must leave identity, player state, NPC/LivingWorld authority and world revision unchanged. Real rollback remains tested separately by the forced valid-bank P1C02 async streaming failure, which must restore the origin and advance revision.

Accordingly the fault evidence contract now distinguishes `ShireInvalidTransitionAudit` (rejected-before-transaction, revision unchanged) from `ShireStreamFailureAudit` (entered transaction, rollback, revision advanced). No production revision is artificially bumped merely to satisfy an obsolete test.

Status of CP-W00-147: **SOURCE-REPAIRED / FRESH EXACT-HEAD PROOF PENDING**. The last exact head with both static and Unreal success remains `3ea40ce1...` (#778/#613). W01 remains blocked.

## 2026-09-23 - W00 checkpoint CP-W00-146: PG-136 false red fixed at the validator architecture layer

Pre-Unreal #779 on `333cbd0dd51d82215d4b9cc94793be507299f349` failed with `PG-136 StartChapter must publish transition intent before logical chapter mutation`. Direct source inspection shows the production transaction order is already correct: `OnWorldTransitionRequested.Broadcast(...)` executes before the authoritative `CurrentChapterId`, `CurrentEpisodeId`, and `PlayableCharacterId` assignments. The red was caused by validator drift: PG-136 searched specifically for the obsolete text `CurrentChapterId = ChapterId;`, while CP-W00-145 correctly canonicalized the destination through `TargetChapterId` and now assigns `CurrentChapterId = TargetChapterId;`.

No C++ transaction reorder is made. CP-W00-146 fixes the root validation family instead. `Scripts/source_contracts.py` provides a reusable structural check that finds protected member assignments regardless of RHS spelling, ignores comments/string literals, and proves the transition signal occurs first. PG-136 uses the same helper for StartChapter and StartExperience, and a dedicated unit suite proves alias-RHS changes pass while mutation-first ordering fails.

At reconciliation time Unreal #614 was still running: build/import/Automation/startup/chapter sweep had already passed, with the state/edge phase still active; Warehouse #195 remained queued. Therefore CP-W00-146 is **SOURCE-REPAIRED / FRESH EXACT-HEAD PROOF PENDING**. W01 remains blocked and no production-completeness percentage is increased.

## 2026-09-23 - W00 checkpoint CP-W00-145: large root-cause closure wave

Exact parent `3ea40ce1d68b6d5b961ed56a00117a75528e833e` is **STATIC-VALIDATED + COMPILE-TESTED + HEADLESS-RUNTIME-VALIDATED** by Pre-Unreal #778 and Unreal #613. #613 passed UE4.27.2 compile/import, Automation 2/2, startup, P1C01-P1C08, state, continuous transitions, rollback/stream-failure faults, delayed pending authority, persistence edges and all tracked project warning-debt ceilings at zero.

Warehouse is still an infrastructure lane, not a gameplay regression. Push run #192 failed before project code on self-hosted network/DNS instability while acquiring checkout/repository data. PR run #193 then checked out successfully but failed immediately in `Detect current warehouse delta`: Windows PowerShell refused GitHub's generated temporary script under the machine execution policy (`PSSecurityException`, scripts disabled). Provider staging never began.

CP-W00-145 folds several remaining W00 families into one guarded repair wave rather than waiting for them to surface one by one. Warehouse inline PowerShell now runs with explicit `-ExecutionPolicy Bypass`; marketplace `actions/checkout` is removed from that lane and replaced by bounded exact-head native Git retries. The experience-state contract is also centralized: authoritative Gandalf identity is `GandalfParallel / P1C01 / P1G01_Isengard / Gandalf`, matching the existing production data. Direct malformed requests fail closed before transition publication, while save/route-progress restore repairs known legacy aliases and rejects unsupported identities before publication.

Persistence coverage is deepened from a synthetic stale callback to a real queued async-disk race. The CI-only edge audit now schedules two actual `AsyncSaveGameToSlot` writes from one committed world revision, crosses to another committed world, defers completion processing deterministically, and requires both writes to succeed while neither stale callback applies checkpoint effects. A separate static guard also compares every runtime C++ `Data/*.json` load with `ShireJourney.Build.cs` `RuntimeDependencies` so packaged-data declarations cannot drift unnoticed.

Status of the new CP-W00-145 head is **SOURCE-REPAIRED / FRESH EXACT-HEAD PROOF PENDING**. W01 remains blocked; no production-completeness percentage is increased.

## 2026-09-23 - W00 checkpoint CP-W00-144: warehouse red isolated from gameplay and repaired as an execution-family defect

Exact parent `67ebc4ee4142c4df9c479c6b326631b767bc903a` is **STATIC-VALIDATED + COMPILE-TESTED + HEADLESS-RUNTIME-VALIDATED** by Pre-Unreal #777 and Unreal #612. Warehouse #191 alone failed after 32m57s. GitHub's structured job record ended with `Stage first Poly Haven CC0 batch` still marked `in_progress`; OpenGameArt/Quaternius/ambientCG/Kenney/KayKit and the final inventory audit never started, and the job exposes no finalized log blob. Therefore no unsupported claim is made about a specific provider exception. Previous Warehouse #190 completed the full provider chain successfully.

The systemic issue is clear even without the missing terminal log: pull-request path matching is cumulative, so the heavy warehouse workflow can run again on stabilization commits that did not change warehouse inputs; provider scripts also used raw web calls and re-queried providers despite persistent receipts. CP-W00-144 adds a current-update delta gate, reusable receipt validation, a shared bounded retry/timeout layer, and atomic `.partial` downloads before rename. A provider/network interruption can no longer leave a partial file looking complete, and unrelated code commits should skip acquisition instead of spending many minutes touching external providers.

PG-144 statically prevents warehouse provider scripts from bypassing the shared network helper and requires every heavy workflow step to be delta-gated. Status of the new head is **SOURCE-REPAIRED / FRESH EXACT-HEAD PROOF PENDING**. W01 remains blocked.

## 2026-09-23 - W00 checkpoint CP-W00-143: semantic evidence-contract consolidation

Parent head `aa8f80c89de1193728c1ff82b5876fdac0fdc7d3` split again: Warehouse #190 SUCCESS, Unreal #611 SUCCESS, Pre-Unreal #776 FAILURE. #611 gives exact-parent **COMPILE-TESTED + HEADLESS-RUNTIME-VALIDATED** evidence for compile/import, Automation 2/2, startup, P1C01-P1C08, state, transitions, rollback/stream-failure faults, delayed pending authority and persistence edges. The warning-debt gate remained zero for all tracked project categories, including the streaming-pool precedence warning.

#776 exposed the remaining root of the repeated static reds. PG-070/074/079/080 and PG-129 still assumed that exact evidence strings physically lived in `runtime_smoke.py`. After PG-142 correctly moved those strings to a central registry, those older guards became stale even though the real runtime was green. CP-W00-143 therefore deepens the repair: `runtime_audit_contracts.py` now owns semantic evidence IDs, exact marker text, mode membership and C++ source anchors. Static validators ask for semantic IDs such as ring continuity, persistence commit, rollback or stale-checkpoint proof rather than searching another Python file for copied text.

The same wave migrates DeepProjectAudit and runtime unit tests to the semantic registry and strengthens the de-duplication test so exact runtime evidence text is forbidden in all Python consumers. This is intended to eliminate the recurring class where a correct C++/runtime change turns Pre-Unreal red because a second or third copy of the old marker survives elsewhere.

Status of CP-W00-143: **SOURCE-REPAIRED / FRESH EXACT-HEAD PROOF PENDING**. W00 remains open; W01 remains blocked.

## 2026-09-23 - W00 checkpoint CP-W00-142: validation-contract consolidation wave

Parent head `7636c7779156831660964cc5d44125efa4b480d1` produced a split result: Warehouse #189 SUCCESS, Unreal #610 SUCCESS, Pre-Unreal #775 FAILURE. #610 is concrete **COMPILE-TESTED + HEADLESS-RUNTIME-VALIDATED** evidence for that exact parent: UE4.27.2 compile/import, Automation 2/2, startup, P1C01-P1C08, state, transitions, rollback/stream-failure faults, delayed pending authority and the persistence-edge sweep all passed. Warning debt also reported `Streaming pool scalability override warnings = 0`. #775 failed on one stale static contract: PG-140 still searched for the old formatted checkpoint log template after #609 forced the C++ logger to split PASS/FAIL into static UE_LOG branches.

That failure belongs to a recurring family: runtime evidence strings were copied independently into C++, `runtime_smoke.py`, `pre_unreal_validate.py` and unit tests. CP-W00-142 therefore does not patch one string. It introduces `Scripts/runtime_audit_contracts.py` as the single Python contract owner for required markers, mode arguments, log names, source anchors and warning-debt runtime log scope. Consumers import the registry; PG-124/133/136/137/138/139/140 consume registry semantics; a dedicated contract unit suite checks source anchors, state-mode execution and de-duplication.

Status of the new CP-W00-142 head is **SOURCE-REPAIRED / FRESH EXACT-HEAD PROOF PENDING**. W00 remains open and W01 remains blocked.

## 2026-09-23 - W00 checkpoint CP-W00-141: #774/#609 root causes repaired at source

Candidate `621ad8617f7ebf1b973887fb61b4f46672d1226c` did **not** pass validation. Pre-Unreal #774 reached `PRE-UNREAL CORE VALIDATION PASSED`, then ProjectGovernor failed because CP-W00-140 had replaced `session_handoff` without its required `validation_snapshot.last_green/latest_observed` exact-SHA/run-ID/status records. Unreal #609 reached real UE4.27 compilation and failed first at `ShirePlayerCharacter.cpp:1954`: a runtime ternary was used as the `UE_LOG` verbosity token. UE4.27 requires a static verbosity token; the later parser/member diagnostics are treated as cascade from that root error.

CP-W00-141 restores evidence lineage: last green remains `80fc54dc...` with Pre-Unreal #773 / Unreal #608, while latest observed records `621ad861...` with #774/#609 FAILURE. The checkpoint audit now logs through explicit Display/Error branches. PG-141 rejects future conditional `UE_LOG` verbosity before engine compilation, and the handoff regression tests explicitly reject checkpoint rewrites that drop `validation_snapshot`.

Status: **SOURCE-REPAIRED / FRESH EXACT-HEAD PROOF PENDING**. W00 remains open and W01 remains blocked. No COMPILE-TESTED / STATIC-VALIDATED claim is made for CP-W00-141 yet.

## 2026-09-23 - W00 checkpoint CP-W00-140: exact-head #608 green; closure/validation-authority wave started

Exact PR #67 head `80fc54dc4e4571e57206bef28cc809e2dcb3ec62` completed Pre-Unreal #773, Warehouse #187 and Unreal Build #608 successfully. #608 compiled UE4.27.2 C++, imported production assets, passed ShireJourney.QA 2/2, startup, P1C01-P1C08, state persistence, continuous transitions, rollback fault injection, forced valid-bank stream failure, delayed pending-window authority and the zero-tolerance project warning-debt categories. This evidence is **COMPILE-TESTED + STATIC-VALIDATED + HEADLESS-RUNTIME-VALIDATED** for that exact SHA only. It is not PIE/device/visual/performance/audio-playback acceptance.

The #608 log exposed a separate low-spec configuration authority defect: `DefaultEngine.ini` hard-set `r.Streaming.PoolSize=900`, so UE reported that TextureQuality scalability pool values were ignored as lower priority. The W00 closure wave removes the project-level override so `DefaultScalability.ini` owns 600/800/1000 MB tiers, adds a zero-tolerance warning guard for this precedence warning, and expands runtime warning-debt scope to transition/fault/pending/persistence-edge logs instead of only startup/chapter/state logs.

PG-140 adds deterministic headless regression coverage for two persistence edges that were previously source-only: a legacy P1C01 terminal save must repair to one final canonical P1C02 publication/world commit, and a stale checkpoint completion carrying an older world revision must not heal or message the newer committed world. The real queued asynchronous write-across-revision case remains separately pending; this new callback guard does not overclaim that disk race.

This checkpoint is the durable restart point if chat is lost. W00 remains open and W01 remains blocked. The new source/config wave is **SOURCE-REPAIRED / FRESH EXACT-HEAD PROOF PENDING** until its own Pre-Unreal and Unreal runs complete.

## 2026-09-23 - Unreal #606 failure-path evidence exposed two more W00 contracts

Unreal Build #606 on `1fdca1166cfd72099a42bbd02c9355b5f035562d` passed UE4.27.2 compile, production import, Automation, startup, P1C01-P1C08, state persistence and continuous transitions, then failed only in the new rollback fault audit. The failure was `freshSnapshot=no` while the same engine log showed rollback applying `health=67.0 stamina=54.0 resolve=43.0 supplies=2`, movement released, NPC context restored, LivingWorld synchronized and world revision advanced. The test sampled stamina/resolve after normal life ticking had resumed, so those values had legitimately begun changing. The fix is not to loosen rollback correctness: rollback now emits a dedicated `ShireRollbackSnapshotApplied` marker at the exact application point, while the later timer checks only stable health/supplies plus committed-system invariants.

The same failure-path review found two additional systemic gaps. First, save restore changes world identity without necessarily calling `StartChapter`/`StartExperience` before persistence mutation, so it did not share PG-136's request-time rollback snapshot boundary. Save restore now begins the persistence transaction, publishes `PreparePersistenceWorldTransition` while the old logical world is still intact, and only then applies restored quest/route state. A failed save-driven world swap therefore has the same exact-origin rollback semantics as a normal chapter transition.

Second, `ShireChapterAssetStreamingSubsystem` still treated a missing/empty bank or unavailable async handle as a compatibility success, and async completion did not verify that every bank asset actually resolved. That could allow a valid logical chapter to commit with fallback geometry rather than treating residency failure as a transaction failure. The next source wave removes that compatibility-success path: missing/empty banks, invalid handles and unresolved assets publish `OnChapterAssetsFailed`; ChapterWorldRouter keeps the previous resident bank pinned and executes atomic rollback. A CI-only forced P1C02 async failure proves the old bank remains resident and player/NPC/LivingWorld state returns to the exact origin.

The same wave adds a bounded non-blocking CI delayed-ready hook. A dedicated pending-transition audit holds P1C02 ready publication for two seconds and requires, during the window, destination logical state to remain unusable by gameplay/NPC logic while LivingWorld remains on the prior committed revision. It then requires destination context, LivingWorld and player controls to move together only after final commit.

PG-137 covers save-restore pre-mutation ownership and delayed transition authority. PG-138 covers fail-closed bank residency and streaming failure rollback. These changes are **source-level pending a fresh exact-head engine run**. Pre-Unreal #772 is green for the current PG-136 head, but no newer engine run yet proves PG-137/PG-138. W01 remains closed.

## 2026-09-23 - Pre-Unreal #771 diagnostic correction for PG-136 fault injection

Pre-Unreal #771 on `1fdca1166cfd72099a42bbd02c9355b5f035562d` failed before engine validation. The validator correctly rejected literal test-only references `P1C99` and `CI_InvalidTransition` as unknown production chapter/quest IDs, and the new PG-136 ordering check accidentally matched the fail-safe no-subsystem hold rather than the normal transition hold. The fault test now constructs its unsupported chapter ID at runtime and reuses the current authored quest identity, so production-reference validation remains strict. PG-136 now checks snapshot ordering against the normal transition hold while preserving the no-subsystem fail-safe hold.

This is a validation/harness correction only. Unreal #606 for the failed static head is not acceptance evidence, and the PG-136 runtime repair still requires a fresh exact-head run.

## 2026-09-23 - Unreal #605 exact-head green; rollback freshness root cause exposed and repaired at source

Exact head `ddd0957d6201c8bf553825acd671c98a9be545ef` completed Pre-Unreal #770, Warehouse #184 and Unreal Build #605 successfully. #605 passed UE4.27.2 C++ build, production import, Automation, startup, the aggregate P1C01-P1C08 sweep, persistence/state roundtrip, continuous transitions and the zero-tolerance warning gate. The warning gate reported zero missing smoothing groups, zero degenerate tangent bases, zero nearly-zero tangents/binormals, zero missing production master surface/world packages, zero optional audio/rig debt, zero defaultMat references, zero light-mobility warnings and zero NPC spawn-collision failures. This is exact-head engine evidence for `ddd0957...` only; it is not PIE/device/visual/performance acceptance.

Continued transaction simulation found a deeper rollback freshness defect that the green path did not exercise. `LastCommittedRollbackSnapshot` was refreshed when a world committed, but not necessarily at the instant a later transition was requested. If the player advanced quest/NPC/player-life state within a chapter and the next world swap failed, rollback could restore the older chapter-commit snapshot instead of the exact state immediately before the failed request. A second defect existed in the unsupported destination path: `CommitChapterWorld` cancelled pending work and returned without restoring the logical origin, potentially leaving the player hold active around an invalid destination.

The source repair introduces a native pre-mutation `OnWorldTransitionRequested` boundary in `UShireQuestSubsystem`. `StartChapter` and `StartExperience` publish the intended destination before mutating logical chapter/route identity. `ChapterWorldRouter` subscribes at that boundary, captures a fresh rollback snapshot only when the current origin is fully committed, then raises the world/gameplay hold before destination mutation. Pending/uncommitted requests cannot overwrite that origin snapshot. Unsupported chapter/route pairs now execute the same atomic rollback path instead of clearing pending IDs and returning.

The route/world support contract is also explicit: `FrodoMain` accepts P1C01-P1C08; `GandalfParallel` accepts its current P1C01/Isengard world identity. A new CI fault mode deliberately requests unsupported P1C99 after setting distinct live player values and requires rollback to restore exact origin identity, player-life state, NPC committed context, LivingWorld revision and movement release. Required marker: `ShireRollbackAudit: PASS unsupported-request restored=yes movementReleased=yes freshSnapshot=yes npcContext=yes livingWorld=yes`.

PG-136 and the deep-project audit guard the pre-mutation snapshot, rollback-on-rejection and fault-injection evidence chain. This new wave is **source-level pending fresh exact-head validation**; #605 remains the proof boundary for its parent head. W01 remains closed and the production percentage is unchanged.

## 2026-09-23 - PG-135 queued checkpoint snapshot ownership hardening

Pre-Unreal #769 on exact head `e8b69e5b61f94ada054cbe5c7b1ed6408796c43e` passed every static gate, including the now-strict source asset audit with zero degenerate-UV assets, zero opposed-normal assets and zero structural errors. Unreal #604 had not completed when this follow-up source audit began.

A further save-path simulation found a distinct async race that the PG-133 callback-origin guard did not fully close. When one automatic checkpoint save was already in flight, a second checkpoint stored only its `CheckpointId`. After the first callback completed, the second request called `SaveAutomaticCheckpoint` again and rebuilt its snapshot from whatever live world happened to exist at that later time. If a chapter transition occurred meanwhile, an old checkpoint ID could therefore serialize destination-world state, or the queued checkpoint could be discarded because the transition hold was active.

PG-135 changes queued checkpoint ownership from ID-only to snapshot+origin. The second checkpoint now captures its full `UShireSaveGame` snapshot plus chapter, route, episode and committed world revision at the instant the checkpoint is reached. The queued request is dispatched directly from that captured snapshot after the current async write completes; it is never reconstructed from later live state. Its completion can still write the disk snapshot after a transition, while the existing origin/revision guard prevents old-world health/resolve/HUD effects from mutating the newer committed world. Both in-flight and queued snapshots are held by UPROPERTY references so GC cannot invalidate them during async serialization.

PG-135 and deep-project audit now reject any return to ID-only queued checkpoint reconstruction. This is **source-level pending fresh exact-head validation** and does not advance W00 or production completion.

## 2026-09-23 - Pre-Unreal #768 exposed the broader tangent-basis family; full source wave + strict CI

Exact head `be5914d9b94d8e8bb5e25de88edab8a0dc089baf` passed the core validator, governor, source asset-quality script and production-readiness stages, then deep-project audit failed on one stale diagnostic token. More importantly, the asset-quality log exposed that the earlier three Unreal warning identities were only the visible edge of a broader authored-source class: 23 additional project-owned static OBJ assets contained degenerate UV triangles, and 7 of those also contained normals opposed to geometric face direction.

This is being handled as one root-cause wave, not as 23 future warning patches. Every asset named by #768 is normalized to explicit triangulated face-local UVs and face-aligned normals. The set includes Balrog/Lurtz static proxy pieces, the Watcher tentacle proxy, Isengard industrial/static structures and Shire props. These remain static/non-animated OBJ assets; no exception is made to the final animated skeletal-FBX contract.

The CI contract is also corrected. `asset_quality_audit.py` previously printed structural `ERROR:` lines but the Pre-Unreal workflow invoked it without `--strict`, so that step still appeared green. The workflow now runs `python Scripts/asset_quality_audit.py --strict`. PG-134 and deep-project audit both check that strict mode remains wired, so structural asset errors cannot silently become advisory again.

The deep-audit diagnostic token is synchronized with the real opposed-normal error wording. No warning ceiling is raised and no W01 work is opened. This wave remains **SOURCE-REPAIRED / FRESH EXACT-HEAD PROOF PENDING**.

## 2026-09-23 - Pre-Unreal #767 exposed a validator self-check mismatch, not a project defect

Exact head `274b5d0dfd12d57e9250001409ea28e43e56d41c` entered the PG-134 tangent-space repair wave. Pre-Unreal #767 stopped in the core validator with one error before the asset-quality stage. The cause was internal validator drift: PG-134 searched for the phrase `opposes geometric face normal` while the source audit deliberately emits `oppose the geometric face normal`. The guarded behavior was present; the literal self-check was stale.

The PG-134 token is synchronized with the actual source-audit contract. The early Pre-Unreal failure block is also changed to print every accumulated error before exit, matching the later failure block, so future validator failures are diagnostic rather than opaque.

This is a validator-source correction only. It does not upgrade the PG-134 mesh repair to engine-proven status; Unreal #602 on the parent head remains separate evidence.

## 2026-09-23 - Unreal #601 narrowed W00 to three source-mesh tangent defects; PG-134 repairs source data

Exact head `34a9a2a8b2cf8f944ce4eae7e90fc7492809b9ab` reached substantially farther than the preceding failed heads. Unreal Build #601 completed UE4.27.2 C++ build, production import, Automation, startup, aggregate P1C01-P1C08 runtime, state roundtrip and continuous-transition runtime. The final warning-debt gate failed with exactly three unique nearly-zero tangent identities and the same three nearly-zero binormal identities: `SM_Balrog_Wing`, `SM_Lurtz_Blade`, and `SM_Isengard_IndustrialPitRim`. Missing smoothing groups, degenerate tangent bases, missing production master surface, missing runtime world packages, optional audio/rig debt, defaultMat references, light mobility warnings and NPC spawn collision failures were all zero in that gate.

Source analysis isolated actual asset-data causes instead of relaxing the zero-warning policy. `SM_Balrog_Wing` and `SM_Lurtz_Blade` each contained four UV-degenerate triangles, which makes tangent derivation singular. `SM_Isengard_IndustrialPitRim` contained authored normals that oppose the geometric face direction on many triangles. These three project-owned procedural static OBJ sources are repaired with face-local non-degenerate UVs and face-aligned normals. This is an asset-source correction, not an animated-OBJ exception; final animated characters/creatures remain skeletal FBX only.

The source-quality audit is also hardened so this class cannot silently return: degenerate UV triangles are structural errors, and strongly opposed/zero authored normals are structural errors before Unreal import. PG-134 requires both the guard and the repaired face-local basis. Warning ceilings remain zero.

Pre-Unreal #766 separately failed because PG-037 still searched for the old async-checkpoint completion log format after PG-133 added `stateApplied` and `sameCommittedContext` evidence fields. The validator is updated to require the new stronger completion marker rather than reverting the runtime guard.

Current status for this new wave is **source repair pending fresh exact-head proof**. #601 evidence remains valid only for `34a9a2a8...`; it does not prove the new mesh repairs. No PIE, device, visual or performance acceptance is claimed.

## 2026-09-23 - Unreal #599 compile failure exposed API ownership defect; PG-133 transaction wave

Exact head `cb8c789aff25d2d1f53c0bc7e37f47fe92607eeb` passed Pre-Unreal #764, then Unreal Build #599 failed during UE4.27.2 C++ compile at `ShireNPC.cpp(1394)`: `UShireNPCContextSubsystem::IsLogicalWorldContextCommitted` was called by the named-NPC runtime while still declared private. Import, Automation and runtime stages were skipped, so #599 provides no evidence for those stages.

The compile root cause is corrected by making the read-only committed-context query part of the public NPCContext API while keeping committed-state mutation owned by the subsystem/router contract. A broader source simulation then found that the PG-131 world barrier still began too late: logical quest identity could advance and asynchronous preload could start before `SetPlayerWorldHold(true)`. The router now raises the authoritative hold at destination request time, not at destination construction time. Rapid A -> pending B -> A cancellation releases the hold only after stale async work is cancelled and the exact old world identity is again committed. Transition CI now requires one marker proving both held-during-swap and cancel-release.

Persistent NPC memory aging is moved out of `StartChapter` into `CommitWorldBoundState`, called only after destination world/context commit. Restore-time NPC memory pruning is likewise deferred until the final canonical world commit. This prevents destructive persistent-state housekeeping from running against an uncommitted or intermediate repaired chapter.

Async checkpoint completion is now origin-bound. The save captures chapter, route, episode and world revision when scheduled; a late callback may still complete its disk write, but health/stamina/resolve healing and HUD success effects are applied only if the callback still belongs to the exact same committed world revision. This closes cross-transition completion mutation without turning asynchronous disk I/O back into synchronous loading.

Ambient social partner evaluation now uses one actor traversal instead of two, and ambient/named/enemy/mythic/Black Rider context-dependent logic is held behind the committed gameplay barrier during world swaps. This is architecture/performance hardening only; no FPS or device-performance claim is made.

PG-133 plus deep-project audit guards these contracts. This new wave is **source-level pending fresh exact-head validation**. W01 remains closed; no completion percentage is increased.

## 2026-09-23 - Restore repair ordering hardened before final world publication

A further source simulation found a deeper save/restore race that was not covered by the earlier atomic restore patch. `CommitPersistenceRestore(true)` previously cleared the restore-in-progress flag and published `OnExperienceChanged` / `OnChapterChanged` before broadcasting `OnQuestStateRestored`. The StoryFlow legacy-repair handler therefore could run only after the router had already seen and potentially committed an intermediate legacy chapter/route identity. On already-resident banks this could become a synchronous double-commit window.

The transaction is now ordered as: rebuild all persistence domains -> invoke the legacy-repair hook while persistence broadcasts remain suppressed -> let `StartChapter`, `StartExperience`, and `StartQuest` canonicalize silently -> release the restore barrier -> publish exactly one final repaired experience/chapter/quest snapshot. `StartExperience` also no longer captures the current pre-commit player transform into RouteProgress while restore is in progress.

Player health/stamina/resolve/supplies are now restored before the final persistence publication because a matching resident bank can commit synchronously from the final broadcast and capture a rollback snapshot immediately. This prevents a rollback snapshot from containing restored quest state paired with stale player-life state.

PG-132 and the deep-project audit enforce the repair-before-publish ordering and player-life-before-commit invariant. This wave is source-level pending fresh exact-head validation; no new compile/runtime acceptance is claimed yet.

## 2026-09-23 - Pre-Unreal #762 test-harness regression isolated during transaction-barrier wave

On exact head `7cb6ccf8e3e5d29c13048cb5eb9862b2268bd18a`, Pre-Unreal #762 failed in `test_runtime_smoke.py`, not in project structure/deep audit. Two harness defects were introduced while extending transition evidence: the new test referenced `runtime_smoke.required_markers` although only `required_markers` was imported, and the older transition test still assumed the mode had exactly one required marker. Both are corrected so transition mode requires the complete marker set, including `ShireTransitionBarrier: PASS held-during-swap=yes`.

Unreal #597 was still compiling this SHA when the harness correction was prepared. Therefore #762 is not treated as a gameplay/runtime failure, and no engine acceptance is inferred for the follow-up head until fresh workflows run.

## 2026-09-23 - Unreal #596 compile blocker isolated; world-transaction mutation barrier added

Exact head `02e4dfb81dc4dababb3c0085369cc628c4704bb3` passed Pre-Unreal #761 and Warehouse #175, then Unreal Build #596 failed in C++ compile before import/runtime. The concrete blocker was UE4.27 overload ambiguity at `FPackageName::ObjectPathToPackageName(ProductionSurfacePath)` where `ProductionSurfacePath` was a `const TCHAR*`. No import/runtime claim is made for #596 because every later engine stage was skipped.

The compile root cause is fixed by constructing an explicit `FString ProductionSurfaceObjectPath` before calling `ObjectPathToPackageName`, removing compiler overload ambiguity without changing runtime behavior.

The broader audit also found a transaction-boundary gap: ChapterWorldRouter disabled CharacterMovement during async world swaps, but several gameplay mutation paths could still be invoked while the quest destination had moved ahead of committed geometry. This could allow interaction, quest triggers, traversal/puzzle completion, supplies, combat, or save actions to observe/mutate half-transition state even though movement itself was held.

A shared player-side world-transition barrier is now mirrored directly from `ChapterWorldRouter::SetPlayerWorldHold`. Movement/jump/sprint, combat, interaction, supplies, checkpoint save/restore, quick save/load and player-life ticking all refuse gameplay mutation while the barrier is active. Quest triggers, traversal challenges, environmental puzzles, world-event interactions and named NPC interaction also require `IsGameplayWorldCommitted()`. Companion banter now requires `ShireNPCContextSubsystem::IsLogicalWorldContextCommitted()`, so old-world dialogue cannot start from destination quest state.

The transition CI now deliberately requests a new chapter and checks, before destination commit, that the player is held and `IsGameplayWorldCommitted()==false`. Required marker: `ShireTransitionBarrier: PASS held-during-swap=yes`. PG-131 and the deep-project audit enforce these contracts statically.

This source wave is **STATIC-VALIDATION PENDING** until the fresh Pre-Unreal workflow completes and **COMPILE-TESTED PENDING** until a new exact-head Unreal build passes C++ compile. W01 remains closed.

## 2026-09-23 - Build #595 full chain green; warning tolerance converted into root-cause closure work

Exact head `a148d1afa919fa63725e3760684d6eed061c5e40` completed Pre-Unreal #760, Warehouse #174 and Unreal Build #595 successfully. Unreal #595 passed UE4.27.2 C++ build, deterministic production import, Automation, startup, aggregate P1C01-P1C08 runtime, state persistence roundtrip, continuous transitions and the warning-debt step. This is the first exact head in this stabilization sequence to complete the entire required CI chain.

That green result is not being treated as permission to ignore remaining evidence. The warning-debt report still contained 137 unique nearly-zero binormal identities plus matching tangent warnings, and the source audit reported 321/352 OBJ files without UVs and 334/352 without explicit normals. The previous guard allowed a ceiling of 150, so this class could remain permanently green without being eliminated.

A new root-cause import-quality wave therefore changes the policy and the importer together. The production importer now normalizes UV-less OBJ files only in its ignored `Saved/ShireProductionImportWorking` copy, generating deterministic dominant-plane face UVs before import. It fails closed if a face cannot be safely parsed/projected. The tracked SourceAssets remain byte-stable. `M_ProductionSurface` also receives a package-existence preflight before any attempted synchronous editor-only recovery load, removing avoidable missing-package warning spam. The warning guard now requires zero degenerate tangent bases, zero nearly-zero tangents, zero nearly-zero binormals and zero missing-production-master-surface warnings. PG-130 makes those contracts fail-closed in Pre-Unreal.

This stricter wave is **source-level pending fresh exact-head proof**. Build #595 remains valid evidence for its own SHA only. No PIE/device/visual/performance acceptance is claimed, and W01 remains closed until the stricter import gate is green.

## 2026-09-23 - W00 persistence/transition root-cause repair wave after Unreal #594

Unreal Build #594 on exact head `38c2c958121576b68a0bfaf4e276498d4fe89dad` materially narrowed the remaining W00 fault set. Runner/Engine Content access, clean intermediates, UE4.27.2 C++ build, deterministic production import, ShireJourney.QA, startup, and the aggregate P1C01-P1C08 sweep all passed. The previous production-surface defect is now engine-proven on that SHA: `CharacterSurfaceAudit: PASS persisted player skin/cloth surface state`. The state gate still failed with `disk-save-details written=yes restored=yes verified=no cleaned=yes`, so persistence is the active blocker.

The new source wave fixes three architectural defects rather than relaxing the failing test. First, save restore now has an atomic logical transaction: quest/route, NPC memory, discoveries, progression and chronicle/map knowledge rebuild while broadcasts are suppressed, then publish once through `CommitPersistenceRestore`. Rollback uses the same transaction but publishes only after old-world geometry and player placement have been restored; a failed rollback invalidates committed-world identity and keeps movement fail-closed. Legacy terminal-save repair is also prevented from applying an old-world transform after it intentionally changes chapter identity.

Second, the disk audit is expanded from a single `verified=yes/no` into field-level persistence evidence. It writes and reloads quest stages, route progress, a seeded Sam NPC-memory bucket, relationships/dialogue history, discoveries/milestones, progression, chronicle/map knowledge, player-life state and transform data. Serialized transforms remain exact; runtime player placement allows only the small vertical canonicalization caused by safe capsule grounding while horizontal drift remains tightly bounded. A failure now prints the exact field names instead of forcing another blind debug cycle.

Third, two async ownership races were found by source simulation. An already-resident chapter bank could be reported ready but then fail `CommitPendingRequest` because no pending IDs existed, causing a false rollback during same-bank episode/save transitions; that path now commits the matching resident bank. Cancelled audio requests also now require their `LoadKey` to remain owned before a late async callback may resolve or play sound, preventing stale playback resurrection.

PG-129 guards these transaction, same-bank and stale-audio invariants. This wave is **source repair pending fresh exact-head validation**. Do not call it PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED. W01 remains closed and the whole-game planning percentage is unchanged.

## 2026-09-23 - Unreal #593 root cause isolated; commit-bound residency hardening applied

Exact PR #67 head `5840863632d04a5fac284b472fe9e5641cd522b8` passed Pre-Unreal #758 and Warehouse #172. Unreal Build #593 passed runner/Engine Content preflight, UE4.27.2 C++ build, deterministic production import, ShireJourney.QA 2/2, startup, and the aggregate P1C01-P1C08 chapter sweep. The remaining state gate failed specifically at `CharacterSurfaceAudit: FAIL persisted player skin/cloth surface state`, followed by `ShireStateAudit: disk-save-roundtrip=FAIL`. The same log showed P1C03 world commit, NPC committed context, LivingWorld committed sync, and stable grounding.

Source inspection identified a residency-order defect rather than a missing material package: `M_ProductionSurface` is an async chapter-bank member, while `AShirePlayerCharacter::BeginPlay` applied prototype MIDs before that bank became resident and had no post-residency reapply signal. The state audit also ran on the next tick before world commit and returned early on the surface check, masking the independent disk-save path.

This W00 source wave adds a post-residency `OnChapterAssetsCommitted` contract, reapplies player surface state at that residency boundary, makes the state audit wait for the exact committed chapter/route/episode, and keeps disk-save testing running even when the surface invariant fails. Player movement now remains held until `OnWorldCommitted` publishes the committed revision/context on both normal commit and rollback. The previously implicit audio-residency assumption is replaced by bounded asynchronous `FStreamableManager` ownership in `ShireAudioSubsystem`; weak caches and short-lived request handles avoid pinning every sound for the GameInstance lifetime.

PG-127 is now fail-closed: its escaped-newline check had been after the script success/exit block and could not fail CI. PG-128 adds regression guards for committed surface residency, state-audit ordering, movement-release ordering, and bounded asynchronous audio ownership.

Evidence for this new source wave is not promoted beyond source inspection until fresh exact-head workflows run. No PIE, device, visual or target-FPS claim is made.

## 2026-09-23 - systemic hardening phase, importer compile artifact repaired

The project is still in W00 hardening / exact-head recovery rather than content expansion. Pre-Unreal #753 and Warehouse #167 are green on the prior head, while Unreal Build #588 reached the real 76-action UE4.27.2 C++ compile and failed only in `ShireProductionImportCommandlet.cpp` because a literal escaped `\n` sequence had been committed between the PNG and TGA discovery statements. That text produced C2017/C2065/C2143 at line 58.

The importer source now contains a real newline, and PG-127 is strengthened so any literal `\n` or `\r\n` text artifact in that C++ source is rejected during Pre-Unreal instead of surviving until Unreal compilation. This is a source fix pending fresh exact-head compile proof.

No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED promotion is claimed yet.

## 2026-09-22 - stabilization gate status schema correction

Pre-Unreal #748 surfaced a governance-schema mistake introduced by the stabilization freeze: `active_gate.status` was set to `ACTIVE`, but the Governor quality-gate vocabulary is `NOT_TESTED / PARTIAL / PASSED / FAILED / BLOCKED`. The stabilization gate remains the active execution focus, while its evidence state is correctly `PARTIAL` until the full exact-head chain passes. No runtime behavior or maturity is changed by this correction.

## 2026-09-22 - stabilization static-gate self-correction

Pre-Unreal #747 correctly rejected the stabilization head because the new PG-121 contract required a `RUNTIME_SWEEP_SUMMARY` marker, while `runtime_smoke.py` had already removed fail-fast behavior but had not actually emitted the aggregate marker. The harness now emits attempted/expected/failed chapter summary after completing the sequential sweep. This is a QA-contract repair only; no engine/runtime maturity is promoted until the new exact head passes the full gate.

## 2026-09-22 - architectural stabilization freeze / root-cause hardening

Owner direction is now explicit: **do not continue feature expansion by patching individual symptoms**. The project is in `W00_ARCHITECTURAL_STABILIZATION`; validation builds are required evidence, but new gameplay/region/warehouse expansion is frozen until the stabilization gate is green.

Last real engine evidence remains Unreal Build #547 on `a42679a4de808ce1f9bada7974ad87d52ee18fa9`: UE4.27.2 C++ build PASS, production import PASS, `ShireJourney.QA` 2/2 PASS, startup and P1C01-P1C04 headless audits PASS, then P1C05 failed with `no-blocking-ground`. The old runtime harness stopped at that first failure, so it provided no P1C06-P1C08 evidence.

The P1C05 response has been converted from a chapter patch into a shared world contract. `ChapterWorldRouter::ResolveGroundedSpawnLocation` now probes a bounded deterministic ring around authored/restored positions, rejects steep surfaces, checks full pawn-capsule clearance, and chooses the nearest valid ground. The temporary P1C01 and P1C05 `RuntimeSpawnFoundation` support pads were removed; Project Guardian now rejects reintroduction of chapter-specific spawn pads.

Runtime QA no longer stops at the first chapter failure. A single chapter sweep now attempts all P1C01-P1C08 sequentially on the low-RAM runner and emits `RUNTIME_SWEEP_SUMMARY`, so one engine build exposes the whole failure set instead of forcing serial red-build discovery.

Character rig requests are also hardened. Missing future-production skeletal mesh / AnimBP packages are checked with `FPackageName::DoesPackageExist` before `RequestAsyncLoad`. Missing rigs remain on modular fallback without flooding Unreal with missing-package async-load errors; completed real rig handles still release after actor-owned handoff.

Source-asset hygiene was repaired at the source, not hidden in importer logs. All 24 tracked BMP textures were converted to TGA, all MTL diffuse references were migrated, the importer now discovers PNG/TGA only, and Guardian rejects BMP. Seven project-owned OBJ files contained consecutive duplicate-position face vertices; 304 affected faces were normalized, and triangulation-risk faces are now strict asset-audit failures instead of warnings.

Material persistence remains evidence-bounded rather than guessed. The importer already performs deterministic master/MTL synthesis, explicit pre/post material package saves, on-disk verification and import failure on missing material packages. Build #547 import passed, but the full warning-debt/material gate was not reached because the old chapter harness stopped at P1C05. Fresh exact-head proof is therefore still required.

No post-#547 hardening change is called COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED yet. The next permitted activity is exact-head stabilization validation, not feature construction.

## 2026-09-22 - W00 engine recovery reached runtime; P1C05 grounding gap repaired

Unreal Build #547 on exact head `a42679a4de808ce1f9bada7974ad87d52ee18fa9` proved the runner recovery beyond the former ACL gate. UE4.27.2 C++ build succeeded, production asset import succeeded, both `ShireJourney.QA` Automation Framework tests passed, and headless startup plus P1C01-P1C04 chapter audits passed. The run then failed at P1C05 with `ShireStartupGrounding: FAIL chapter=P1C05 reason=no-blocking-ground requested=(-2400.0,0.0,130.0)`.

Source inspection found a deterministic geometry gap: the broad P1C05 fallback ground centered at X=0 with X scale 46 ends near X=-2300, while the first route slab centered at X=-2600 ends near X=-2480. The authored chapter start at X=-2400 therefore sat between both collision surfaces. `BuildFellowshipRoad` now adds a small hidden Engine BasicShapes collision foundation under the exact P1C05 start, matching the deterministic support strategy already used for P1C01.

This is a source fix pending fresh exact-head engine proof. The previous run is valid COMPILE evidence for `a42679a...`, but the new repair head is not yet COMPILE-TESTED/PIE-TESTED/DEVICE-TESTED/VISUALLY-ACCEPTED.

## 2026-09-22 - runner ACL recovered; first real compile defect repaired

Unreal Build #534 attempt 3 proved the Windows runner can now read UE4.27 Engine Content: the log reported `UE4_ACL_REMEDIATION_PASS action=none reason=already-readable`, UHT generated reflection code, and the exact head entered a 76-action `ShireJourneyEditor` C++ build. The runner/Engine Content ACL blocker is therefore no longer the immediate failure.

The first real project compile failure was cross-module visibility: `ShireJourneyEditorTools/Private/Tests/ShireQAAutomationTests.cpp` could not include `ShireSaveGame.h` while the runtime module remains intentionally `FLAT_GUARDED`. The repair exports `Source/ShireJourney` as a temporary public include root in `ShireJourney.Build.cs`, avoiding a relative/private include hack and preserving the rule that the physical Public/Private migration remains a separate engine-tested maintenance change. The importer also replaces deprecated direct `UStaticMesh::StaticMaterials` access with `GetStaticMaterials()` to remove the two C4996 warnings observed in the same build.

No COMPILE-TESTED claim is made until the new exact-head build completes successfully.

## 2026-09-22 - PIE StaticMesh mobility warning source fix

A live PIE screenshot showed repeated warnings of the form `SetStaticMesh ... but Mobility is Static` on runtime-generated `AStaticMeshActor` components. The source cause was confirmed in the Shire, Bree, Fellowship and Isengard runtime world-builder spawn helpers: each helper assigned the mesh first, then changed component mobility to Movable. Runtime-spawned `AStaticMeshActor` components begin as Static, so the mesh mutation generated warning spam.

The four helpers now set mobility to Movable before `SetStaticMesh`, preserving their existing final mobility behavior while removing the invalid mutation order. A DeepProjectAudit guard now rejects reintroduction of the old ordering.

This warning flood can contribute to editor log overhead/hitch perception, but it is not the GitHub runner ACL failure. The runner remains separately blocked because `NT AUTHORITY\\NETWORK SERVICE` cannot read UE4.27 Engine Content. No compile/PIE/device acceptance is claimed for this source fix until a fresh exact-head engine run is available.

## 2026-09-22 - precise integration-gap source closure

The deep audit findings were acted on immediately instead of being left as notes. The source branch now contains a committed-world NPC context bridge: ChapterWorldRouter publishes committed chapter/route/episode/revision on normal commit and rollback; regional mood/profile availability follows that committed identity; danger uses live quest state only while logical and committed world identity still match; and new bounded dialogue/film-context selection is suppressed during the async mismatch window rather than leaking destination context into the old visible world.

Character-rig streaming remains asynchronous, but the completed per-character streamable handle is now released after the ready broadcast, when player/NPC components have taken their own UObject references. This removes the GameInstance-lifetime handle pinning identified by the audit while retaining active-character ownership and modular fallback behavior.

The synchronous production-asset debt was also burned down at source level. Shire/Bree/Fellowship/Isengard world builders no longer directly LoadObject production meshes; they resolve only objects already resident in the async chapter bank. Black Rider, standard Fellowship enemies and mythic threats use resident-only production visual resolution, and the chapter streaming plan now includes the relevant enemy banks. Player/named-NPC production proxy pieces use resident-only soft resolution while their skeletal rig path remains asynchronous. ShireAudioSubsystem no longer synchronously LoadObject<USoundBase>; production sound must be resident through an async ownership path, otherwise subtitle/story/silent fallback remains safe.

A continuous guard was added to deep_project_audit.py: non-/Engine/BasicShapes synchronous LoadObject is now rejected, as are regressions in committed NPC context publication, completed rig-handle release, synchronous audio load, builder ticking and existing social-scan bounds.

These are source fixes only until the runner is restored. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED promotion is claimed. The active priority remains W00 runner/exact-head unlock.

## 2026-09-22 - deep organization and integration audit before runner repair

A repository-wide source/governance audit was performed against PR #67 exact head `17689b194ddca281aa9881b9ac50594712a65df6` before touching the laptop runner. Three current workflow facts are now authoritative for this checkpoint: Pre-Unreal #685 failed only because the newly accepted third-person camera requirement was not yet mapped into MasterExecutionRoadmap; Unreal Build #520 again stopped before C++ compilation because `NT AUTHORITY\\NETWORK SERVICE` could not read `Engine/Content/EngineMaterials/WorldGridMaterial.uasset`; Warehouse #99 succeeded and the persistent inventory audit reported `payloadFiles=240 bytes=3816657674 receipts=8 receiptRecords=278 duplicateGroups=22`, with total footprint `files=249 bytes=3816866382`.

The roadmap drift is repaired: REQ-CAMERA-001 is now assigned to the Part I gameplay bundle and the tracked unfinished-requirement snapshot is regenerated from the Governor. This was a management consistency defect, not a gameplay defect.

The deeper integration simulation found two additional source risks worth carrying into W00/W01 rather than hiding them. First, `LivingWorldDirector` correctly waits for `ChapterWorldRouter` committed-world revision before switching active life/weather, but `UShireNPCContextSubsystem` independently reads the logical quest chapter/route for regional mood, profile availability, film-dialogue context and pressure. During asynchronous chapter load the quest can advance while old geometry is still visible, so old-world NPCs can transiently react using destination context. Second, asynchronous character-rig handles are retained per requested character for the GameInstance lifetime; this is safe functionally but needs measured chapter-cast residency/eviction on the ~2 GB VRAM target before full-cast skeletal rollout.

The audit also corrected stale debt tracking: ambient NPC pooling is already source-implemented with bounded reuse and disabled pooled ticks; it is now pending engine/device proof rather than missing. Conversely, synchronous runtime asset debt is still real: the inspected exact head contains 77 direct `LoadObject` calls in `FellowshipChapterWorldBuilder`, 55 in `ShirePrototypeWorldBuilder`, 22 in Bree, 10 in Isengard, plus remaining player/named-NPC fallback loads. These must be burned down incrementally after the runner is restored, without deleting the two-phase async bank/fallback architecture.

No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED status is promoted by this audit.

## 2026-09-22 - final pre-runner warehouse saturation batch

One final source-safe warehouse expansion is committed before runner repair becomes the active priority. Three official KayKit public-GitHub packs were source-checked as CC0 and added to the non-interactive staging lane: Restaurant Bits for food/kitchen/interior support, Halloween Bits for selectively filtered cemetery/crypt/dark-region props, and City Builder Bits only as a manually filtered source of period-neutral civic props. Their FBX/GLTF/OBJ source presence does not override the project rule that animated final characters are skeletal FBX and production textures are PNG/TGA/channel-packed.

This commit authorizes staging only. Until Warehouse Stage emits actual receipts, these additions are not claimed STAGED. After receipt/audit, broad warehouse expansion pauses and W00 runner/Engine Content ACL repair becomes the next active production priority.

## 2026-09-22 - whole-game completion wave map

A durable finish map is now registered in `Data/CompletionWaveMapV1.json`. It treats the current whole-game planning position as approximately 40/100 and organizes the remaining 60 planning points into 12 production waves (W00-W11), from runner/exact-head unlock through Shire visible skeletal-character conversion, Part I production/acceptance, Part II/III runtime+production, and final trilogy integration.

The execution unit is a major coherent production drop rather than an individual Git commit or raw file upload. The map currently estimates roughly 30-40 remaining major drops, with actual commit count allowed to be higher. These percentages/drop counts are planning estimates only; they do not alter any compile, PIE, device, performance or visual acceptance state.

## 2026-09-22 - character visibility bridge and warehouse receipt hardening

Owner priority is now explicit in the Governor and WORLD_DETAIL_LEDGER: warehouse growth must convert into visible humans/enemies, with P1C01 Shire still the first assembled benchmark. The official KayKit Skeletons 1.0 public GitHub package was source-checked as CC0 and documents fully rigged/animated characters, FBX/GLTF delivery and 90+ animations. It is registered strictly as technical enemy rig/import/retarget QA stock, not canonical LOTR enemy art or a visually accepted production character.

The KayKit staging batch now includes that pack, and the warehouse inventory audit now recognizes archive-style receipt records in addition to legacy file records and verifies recorded license-snapshot hashes when present. This closes a bookkeeping blind spot where KayKit archives could contribute payload bytes without participating in receipt-record hash validation.

Evidence boundary remains unchanged: the last proven engine run is still blocked before C++ compilation/import by the non-elevated NETWORK SERVICE runner lacking read access to UE4.27.2 Engine Content. These changes are source/warehouse preparation only. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made.

## 2026-09-22 - hourly continuation: non-interactive KayKit public-GitHub lane

Exact-head inspection started from PR #67 head `d856a716d5bc270ce0ddc2d649acbb1656ae112c`. Pre-Unreal Validation #670 completed successfully and Warehouse Stage #80 completed successfully. Unreal Build Validation #505 stopped before C++ compilation: the runner identity was `NT AUTHORITY\\NETWORK SERVICE`; the guarded ACL remediation reported `UE4_ACL_REMEDIATION_DEFERRED reason=runner-not-elevated`; the unchanged UE4.27.2 preflight then failed six reads of `Engine/Content/EngineMaterials/WorldGridMaterial.uasset` with access denied. Build/import/Automation/startup/chapter/state steps were skipped. This is machine ACL evidence, not compile evidence, and this run does not retry the same elevated fix.

Warehouse saturation now adds `Data/WarehouseKayKitGitHubAcquisitionBatchV1.json` and `Scripts/stage_kaykit_github_warehouse.ps1`. The lane uses only exact official public KayKit GitHub repositories/direct archives and license snapshots; it forbids login, purchase/name-your-price, OAuth, Patreon/Discord and other interactive routes. Per-pack and batch byte caps, CC0 license markers, SHA256 provenance and STAGED-only state are enforced. The Warehouse Stage workflow now executes this lane before inventory audit.

The concrete KayKit support candidates cover low-spec medieval settlement/layout stock, dungeon/interior modules, rigged/animated background-character pipeline testing and furniture props. `TrilogyWorldFoundationPlanV1.json` maps them into Shire/Bree/Rivendell/Moria/Lothlorien/Rohan/Gondor/Osgiliath/Minas Morgul/Cirith Ungol/Paths of the Dead/Grey Havens support roles. P1C01 Shire remains the first assembled benchmark; later-film use is warehouse/preproduction only. Final animated characters still require real skeletal FBX rigs, skin/deformation review; repeated detail remains ISM/HISM-classed; heavy integrated assets remain soft/async through FStreamableManager.

Integration-repair inspection found no new demonstrated source regression behind the green static gate. Runtime/compile progression remains blocked only by the already-demonstrated local Engine Content ACL condition. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made for this wave.

## 2026-09-22 - autonomous hourly lane: exact-head evidence + Quaternius saturation

PR #67 exact head entering this iteration was `f41d5e91ac2a789387e987ff759b9e674cd86e10`. Exact-head Pre-Unreal Validation #667 succeeded, and Warehouse Stage #76 succeeded across Poly Haven, OpenGameArt, Quaternius, ambientCG base/trilogy batches, Kenney, inventory audit and footprint reporting. Unreal Build Validation #502 did not reach C++ compilation: the guarded Engine Content ACL remediation step completed, then the unchanged UE4.27.2 verification step failed; build, import, Automation Framework, startup, chapter and state audits were skipped. This remains a machine/Engine Content preflight blocker, not compile evidence, and the gate was not weakened.

Warehouse saturation expanded `WarehouseQuaterniusAcquisitionBatchV1.json` and `TrilogyAssetCandidateQueue.json` with official-page CC0 lanes for additional modular background humans, creature rig/deformation pipeline stock, supporting textured buildings and dungeon/interior support. These remain CANDIDATE/AUTHORIZED_FOR_STAGING until actual staging receipts and intake checks exist. Canonical hero characters/creatures still require real skeletal FBX rigs, skin/deformation review and their own visual acceptance.

`TrilogyWorldFoundationPlanV1.json` now maps the added stock into reusable regional-preproduction roles for Shire/Bree/Rivendell/Lothlorien, Moria, Rohan, Gondor/Osgiliath, Cirith Ungol, Paths of the Dead, Mordor and Grey Havens while preserving P1C01 Shire as the first assembled benchmark. Later-film mappings are warehouse/preproduction only and do not open Part II/III runtime chapters. Intake ordering reiterates SHA256/provenance retention, FBX rig requirements, PNG/TGA/channel-packed texture preference, ISM/HISM classification for repeated detail, and FStreamableManager soft/async ownership for heavy runtime content.

Integration-repair inspection found no new demonstrated source regression on the green pre-Unreal head. The unresolved failure is still the local UE4 Engine Content preflight, so source/runtime gates remain fail-closed. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made for this iteration.

## 2026-09-22 - active wave: ACL repair attempt + trilogy material expansion

The Unreal Build workflow now contains a guarded Engine Content ACL remediation step before the existing UE4.27.2 verification. It grants only read/execute to the runner service identity when the workflow has elevation; if the runner is not elevated, it records the exact required action and leaves the original verify gate unchanged. This does not weaken validation and does not create a compile-tested claim.

Warehouse execution also expanded beyond Shire with `WarehouseAmbientCGTrilogyBatchV2.json`, targeting material families for Caradhras, Moria, Rohan, Gondor, Osgiliath/Ithilien, Mordor, Isengard, Bree/battlefields, Pelennor support and Shelob-lair support. The warehouse workflow now stages this batch in addition to the existing Shire/material/audio/Quaternius/Kenney lanes.

No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED status is claimed by this wave.

## 2026-09-22 - autonomous three-lane production iteration

PR #67 exact head before this production batch was `0c8130a33f8df3648d270d8bd0ee6b24aee882fb`. Pre-Unreal Validation #653 completed successfully on that exact SHA. Unreal Build Validation #488 did **not** reach C++ compilation: the self-hosted `UE4-27-Windows` runner executed as `NT AUTHORITY\\NETWORK SERVICE` and was denied read access to `Engine/Content/EngineMaterials/WorldGridMaterial.uasset` on all six preflight probes. Build, import, Automation Framework, startup, chapter and state steps were therefore skipped. This remains an Engine Content ACL/environment blocker, not compile evidence.

Warehouse saturation advanced without promoting asset maturity. `TrilogyAssetCandidateQueue.json` now includes concrete Quaternius animation/prop and Kenney world/fortification/nature/interior/UI support candidates already tied to official CC0 pack pages. `TrilogyAudioAssetCandidateQueue.json` now mirrors stage-authorized OpenGameArt CC0 prototype music/SFX candidates across Shire, Bree, Rohan and large-battle routing tests. `WarehouseAmbientCGAcquisitionBatchV1.json` is expanded into a trilogy-foundation material intake covering snow/ice, cave stone, wetland ground, white stone, volcanic/ash surfaces, industrial metal, Rohan pastoral surfaces, ruins and river/wet materials. AUTHORIZED_FOR_STAGING and STAGED remain distinct from READY_FOR_IMPORT / IMPORTED / INTEGRATED / ACCEPTED.

Multi-region world-foundation preproduction is no longer a list of region names only. Every declared region from Shire through Grey Havens now carries explicit stock contracts for architecture, terrain/materials, vegetation/ecology, props, populations/factions, audio, lighting/atmosphere, VFX and traversal/collision, plus preferred warehouse source lanes. P1C01 remains the first assembled benchmark; later-film regions are explicitly PREPRODUCTION_ONLY and this work does not open Part II/III runtime chapters.

Current code/runtime acceptance is unchanged by these warehouse/world-plan edits. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made for the new head.

## 2026-09-22 - failed-swap rollback transaction expanded to player-life state

The integration repair wave now closes another source-level rollback gap. `ChapterWorldRouter` rollback snapshots already preserved quest, route/chapter/episode, NPC memory, exploration, progression, knowledge and player transform. They now also capture player health, stamina, resolve and supplies from `AShirePlayerCharacter`. During `RestoreCommittedWorldFromSnapshot`, those values are reapplied through `RestoreTransactionalPlayerState` after grounded placement succeeds and before world hold is released.

Source-contract regression coverage now requires this full transaction ordering. This is still source/static work only: exact-head UE4.27 compile/runtime proof is required before the rollback requirement can be considered closed.

No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made.

## 2026-09-22 - world foundation work expanded beyond Shire

P1C01 remains the first fully assembled visual benchmark, but production prework is no longer Shire-only. `Data/TrilogyWorldFoundationPlanV1.json` now tracks reusable world-foundation lanes for Bree, Weathertop, Rivendell, Caradhras, Moria, Lothlorien, Anduin/Amon Hen, Fangorn, Edoras/Meduseld, Helm's Deep, Isengard, Emyn Muil, Dead Marshes, Ithilien/Henneth Annun, Minas Tirith, Osgiliath, Minas Morgul, Cirith Ungol/Shelob's Lair, Pelennor, Paths of the Dead, Black Gate, Mordor/Gorgoroth, Mount Doom and Grey Havens.

Each region has parallel architecture, terrain/material, vegetation/ecology, population/faction, audio, lighting/VFX and traversal/collision stock requirements. This is preproduction/warehouse foundation work only; it does not bypass runtime chapter gates for Part II/III.

## 2026-09-22 - pooled visual fallback hardening

The async living-world ownership wave now also resets every reused ambient actor to constructor-owned Engine primitive meshes before resolving role-specific production soft objects. This prevents a pooled NPC that changes regional role from retaining a stale Human/Elf/Hobbit mesh when a production asset is unavailable. Active density and streaming policy are unchanged. Exact-head CI/UE evidence remains required; no runtime verification claim is made.

## 2026-09-22 - Resource Bible 09 operationalized into warehouse execution

The project source `09_EXTERNAL_HELPFUL_RESOURCES_BIBLE_PERSONAL_LOCAL` has now been converted into `Data/ResourceBibleSourceExpansionV1.json` and merged into `Data/GlobalWarehouseSourceRegistryV2.json`. Its source families now explicitly cover voice/TTS, music, SFX/field recording, visual/UI reference, 3D/models/scans, architecture, environments/materials, animation/mocap, LOTR-specific reference and AI creation tools. This preserves the Bible's own separation between personal-local candidate material, temporary/reference material and tools rather than flattening every website into an automatic production source.

Concrete staging also widened beyond the previous Poly Haven/Quaternius/OpenGameArt lanes. ambientCG now has a public-API 2K-PNG material batch for timber, plaster, terrain, stone, bark, leather/fabric and roofing/cobble families, and Kenney now has an official-pack-page CC0 resolver for world/support stock such as fantasy town, castle, nature, furniture, building, dungeon, food, UI and background-character packs. Both are wired into the persistent Warehouse Stage workflow.

These changes expand warehouse sourcing and STAGED stock only. They do not promote UE import, integration, visual/audio acceptance, or any COMPILE/PIE/device status.

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

## 2026-09-22 - global warehouse source circle expanded and ranked

The warehouse source registry is no longer a short-list. It now tracks a broader global source matrix with an explicit scoring/tiering policy so acquisition can widen without becoming chaotic. Newly added lanes include ambientCG, ShareTextures, KayKit, PolygonalMind CC0 releases, Poly Pizza, Gobkit, NASA 3D resources and supplemental HDRI sources. Tier A is reserved for clear, automatable, high-value sources; auth/marketplace sources are Tier B; supporting/niche sources are Tier C; ripped/unclear proprietary-port communities remain reference-only.

The selection rule is intentionally not “download everything from every site.” For each warehouse slot, retain the best-fit one to three candidates based on visual fit, engine readiness, license clarity, format, performance, reuse breadth and source stability. This keeps the trilogy warehouse large but searchable and prevents duplicate low-value stock from consuming staging/storage time.

## 2026-09-22 - warehouse runner execution-policy blocker repaired

Warehouse Stage #18 reached the self-hosted runner and failed before any download because GitHub's `shell: powershell` wrapper attempted to dot-source its temporary script while the Windows service account has script execution disabled. The warehouse workflow now invokes each checked-in staging script from `cmd` using `powershell.exe -NoProfile -ExecutionPolicy Bypass -File`, matching the proven pattern already used elsewhere on the runner. This repairs the staging launcher only; actual staged-file counts remain pending the next exact-head Warehouse Stage run.

Unreal Build #449 remains a separate pre-compile blocker: the same runner account is still denied read access to `WorldGridMaterial.uasset`. Pre-Unreal #614 succeeded on the same prior head. No compile/PIE/device/visual acceptance claim is made.

## 2026-09-22 - multi-lane warehouse staging expanded

Warehouse fill now runs as three concrete intake lanes on the integration train: Poly Haven CC0 environment/material stock, OpenGameArt CC0 music/foley stock, and Quaternius CC0 character/animation/fauna/world-kit discovery/staging. The audio lane contains direct OpenGameArt WAV/ZIP endpoints with source-page/license records and SHA256 receipt generation. The Quaternius lane resolves only public direct archives from official pack pages and records unresolved/store-only packs without fabricating download URLs.

The warehouse workflow remains independent from UE4 compile/PIE. Staged assets remain STAGED until their category-specific intake validation passes; animated production characters still require real FBX rigs and hero-character visual acceptance is not implied by background/base packs.

## 2026-09-22 - warehouse fill execution expanded beyond catalogue-only state

The warehouse lane has moved into an actual staged-download implementation. `Data/WarehouseAcquisitionBatchV1.json` now contains a source-page-verified Poly Haven P1C01 material/prop batch covering wood interiors, dirt/path variants, plaster families, cobblestone, mossy stone and barrel props. `Scripts/stage_polyhaven_warehouse.ps1` now handles provider/API failures per asset instead of aborting the entire batch, records skipped reasons, and preserves successful downloads/receipts so one bad slug cannot stop warehouse growth.

The dedicated `Warehouse Stage` self-hosted workflow remains separate from the UE4 build path. The current exact-head Pre-Unreal gate is green; runtime/PIE/device proof remains separate. No staged warehouse item is promoted to imported/integrated/accepted by this download infrastructure alone.

## 2026-09-22 - persistent warehouse staging lane activated

The asset warehouse is no longer catalogue-only. A dedicated `Warehouse Stage` workflow and `Scripts/stage_polyhaven_warehouse.ps1` now target a persistent self-hosted storage root at `C:\\actions-runner\\_warehouse\\ShireJourney`, independent from the blocked UE4 Engine Content build path. `Data/WarehouseAcquisitionBatchV1.json` defines the first CC0 Poly Haven material/prop batch with 2K intake and a hard byte cap; every staged file is intended to receive size/SHA256/source metadata in a local receipt before later import.

The workflow listens to the integration branch, PR exact-head changes affecting the warehouse batch/scripts, and manual dispatch. Staging does not imply UE import, runtime integration or visual acceptance. Existing exact-head evidence remains: Pre-Unreal #603 succeeded on `2e7424c9c63c2bbdb419c4bed10e01ca5cbd282a`; the UE build path remains separately blocked by the self-hosted Windows account's Engine Content read permissions.

No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED status is promoted by warehouse staging.

## 2026-09-22 - Pre-Unreal #597 PG-078 warehouse-roadmap reconciliation

Exact-head Pre-Unreal #597 on `f7ef04c4b36d6664bdb06324a9652f1572584f28` failed with four deterministic governance errors: `REQ-WAREHOUSE-001` and `WORK-PROD-011` were registered in ProjectGovernor but not yet assigned to the master roadmap, and the tracked unfinished/active snapshots were therefore stale. The warehouse requirement/work item is now assigned to B2 Characters & World Production and both snapshots are regenerated directly from the live Governor.

Unreal Build #432 on that SHA again failed before C++ compilation because the self-hosted runner identity `NT AUTHORITY\\NETWORK SERVICE` was denied access to UE4.27.2 `WorldGridMaterial.uasset`. Warehouse catalogue/candidate/staging work continues independently under DEC-033; this runner blocker still prevents compile/PIE/device evidence.

No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED status is claimed.

## 2026-09-22 - warehouse testing boundary clarified

The warehouse lane is now explicitly decoupled from runtime test availability. We do **not** wait for UE4 compile/PIE/device validation to discover, catalogue, download or stage trilogy assets. That work is intentionally parallel and may continue while the self-hosted runner is blocked.

The engineering boundary is staged rather than test-free: raw stock must pass a lightweight intake gate before `READY_FOR_IMPORT` (file integrity, archive/malware hygiene, correct format, units/scale, naming, texture packing/dimensions, topology/UV/skeleton/animation sanity where relevant, plus provenance/metadata). UE4 import/build evidence begins at `IMPORTED`; runtime/PIE evidence begins at `INTEGRATED`; visual/audio/device acceptance is required only for `ACCEPTED`.

This rule is durable as `DEC-033` and hard invariant `INV-WAREHOUSE-STAGING`. It prevents runner outages from starving the asset warehouse without turning the warehouse into an untrusted file dump.

## 2026-09-22 - first concrete trilogy asset candidate queue seeded

Warehouse-first production moved from catalogue-only planning into concrete sourcing. `Data/TrilogyAssetCandidateQueue.json` now contains the first official-source candidates: CC0 Quaternius rigged/background character, fantasy outfit, medieval village, modular ruins, nature and farm/animated-animal packs, plus Poly Haven high-fidelity barrel and wood/stone/mossy PBR material lanes. These are candidates, not automatic final hero art; low/stylized packs are explicitly limited to supporting/background/pipeline roles where appropriate.

The next sourcing pass is deliberately aimed at the remaining high-value gaps: realistic hero humanoid bases, non-stylized rural/medieval architecture, photoreal biome libraries, rigged hero creatures, professional animation libraries and the approved audio-bank lanes. No candidate is called INTEGRATED or ACCEPTED until an actual asset is acquired/imported and earns the required evidence.

## 2026-09-22 - trilogy warehouse-first production plan activated

The owner explicitly changed the production emphasis: final-looking characters, world art and audio may no longer remain vague downstream gaps while backend/governance continues to grow. The project now has a machine-readable trilogy warehouse at `Data/TrilogyProductionAssetWarehouse.json` and a new Governor requirement `REQ-WAREHOUSE-001`, decision `DEC-032`, and active work item `WORK-PROD-011`.

The first-pass catalogue spans all three films: major and supporting named characters, population/faction families, 28 major location slots with state variants, cultures, creatures/fauna, battles, weapons/artifacts, material families, architecture/props, animation families, audio, cinematic/VFX and UI support. The supporting-cast layer was seeded from the supplied trilogy screenplay speaker pass; the world/culture/creature layers were grounded in Sources 03/04/05 and Source 11.

Important proof boundary: the catalogue is now broad enough to prevent forgotten categories, but this is not a claim that all final binary assets already exist. `CATALOGUED`, `READY`, `APPROVED`, `INTEGRATED` and `ACCEPTED` are intentionally separate states. The immediate production target is P1C01 as the first complete natural-looking vertical slice while Part II/III asset-bank preparation proceeds in parallel.

No new COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made by the warehouse plan itself.

## 2026-09-22 - cinematic audio sourcing directive registered

The owner-forwarded audio-engineering message is now durable repository state. The project already has `UShireAudioSubsystem` routing, ambience/music crossfades, voice ducking and speaker-attachment rules in `Part1SonicWorldPlan`; the major missing layer is authored final audio content. `Data/AudioAssetSourcingWaveV2.json` now defines the offline bank strategy for voice, music, ambience/fauna, foley and creature/combat audio, plus 3D spatialization, concurrency and low-spec profiling requirements.

ElevenLabs, BOOM Library and Pro Sound Effects are registered as candidate production sources subject to exact authorization/license/entitlement. LOTR Complete Recordings, Blu-ray center-channel dialogue and classic EA LOTR game audio are stored as reference-only unless separately cleared. This prevents source discovery from being lost while keeping the Approved bank deterministic and auditable.

No final voice/music/SFX asset, mix acceptance, PIE/device audio acceptance or new COMPILE-TESTED claim follows from this registration.

## 2026-09-22 - cinematic asset-source shortlist expanded

The owner-forwarded asset-manager message has been registered rather than kept in chat memory. `Data/ExternalAssetManifest.json` now stores DeviantArt 3D/XNALara ports, SFMLab, Open3DLab, Nexus Mods and ArtStation Marketplace as additional cinematic-quality discovery/review sources, alongside the already tracked CGTrader, TurboSquid, Sketchfab, Quixel/Fab and legacy Unreal Marketplace paths.

The private/non-distributed project intent and exact-film visual target are recorded, but discovery is not automatic approval: ripped/ported proprietary film or game assets still require explicit item-level reuse rights/provenance before entering `SourceAssets/ExternalLicensed/Approved`. The project should still aggressively search these sources for legal high-quality bases, original artist work, reusable marketplace items, commissions and environment/material packs so the visual warehouse can be filled without reverting to low-detail placeholders.

## 2026-09-22 - Pre-Unreal #578 character-guard reconciliation

Exact-head Pre-Unreal #578 passed its core structural phase, then reported four character handoff guard failures because PG-051/PG-089 still required the removed synchronous package-probe symbols inside ShirePlayerCharacter/ShireNPC. The V7 runtime now owns heavy rig paths in ShireChapterAssetStreamingSubsystem and requests them with FStreamableManager::RequestAsyncLoad.

The guards are updated to protect the new architecture instead of restoring the obsolete LoadObject/FPackageName path: player/NPC fallback and motion symbols remain required; the streaming subsystem must expose RequestCharacterRig/ResolveCharacterRig, SK_/ABP naming and RequestAsyncLoad; and the player path is explicitly rejected if synchronous USkeletalMesh/UAnimInstance loading returns.

This is a static-validator reconciliation only. No final character art is claimed and no COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED status is promoted.

## 2026-09-22 - exact-head runner retest preparation: duplicate EndPlay regression fixed

Pre-Unreal #576 on `c9a0eaafc273aeaa2fd1a0fb0aa0f41903a0c2a8` stopped in static validation with one concrete source error: `Unbalanced braces in ShirePlayerCharacter.cpp: balance=1`. Inspection found a duplicated `AShirePlayerCharacter::EndPlay` function signature introduced while wiring async character-rig delegates. The duplicate declaration/opening brace is removed; no intended gameplay behavior is changed by this correction.

The same exact head's Unreal Build #411 proved the Windows self-hosted runner is online and executing the workflow, but it still stopped before C++ compilation because the runner identity `NT AUTHORITY\\NETWORK SERVICE` received access denied reading UE4.27.2 `WorldGridMaterial.uasset`. A new exact-head workflow run is required to determine whether the laptop-side permission state has changed since #411.

No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED status is claimed by this source fix.

## 2026-09-22 - persistence/world-commit repair wave started

After Pre-Unreal #564 turned green on `685dc63ff94fec0a1f6b3d57d60fce3bffcde31d`, the integration train moved to the first registered runtime defect wave instead of opening new features. Transition checkpoint capture no longer clears and saves on the next player Tick unconditionally. It now waits until `ChapterWorldRouter::IsWorldCommitted` confirms the current chapter/route/episode identity, so an asynchronous preload cannot produce a destination chapter snapshot with a source-world transform.

Cross-chapter save restore is also changed from immediate teleport to deferred committed-world placement. `AShirePlayerCharacter` stores the saved transform and identity, waits for the matching committed world, and asks `AChapterWorldRouter::PlacePlayerAtCommittedTransform` to ground the saved XY location against destination geometry before teleporting. The initial P1C01 checkpoint is routed through the same commit barrier.

This is a source implementation wave only. It has not yet earned UE4.27 compile or runtime proof, and the failed-swap rollback transaction is still open. Unreal Build #399 is still expected to encounter the separate runner Engine Content permission blocker unless that machine permission changes. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made.

## 2026-09-22 - Pre-Unreal #562 stale streaming-cancellation test repaired

Exact-head Pre-Unreal #562 on `830b986d36d2563d11d7b3ed18c94b64e6741090` passed the core validator, Project Governor and Deep Project Audit, then failed one source-contract unittest in `Scripts/test_streaming_cancellation_contract.py`. The test still expected `ResidentHandle = PendingHandle` inside `HandleAsyncLoadComplete`, which contradicts the integrated two-phase streaming contract: async completion only reports preload readiness, while resident promotion belongs to `CommitPendingRequest` after world construction and grounding succeed.

The regression test is updated to require the stale-serial guard before the preload-ready broadcast, explicitly reject resident promotion inside the async callback, and require `ResidentHandle = PendingHandle` only inside `CommitPendingRequest` after its readiness guard. Runtime streaming code is unchanged by this correction.

Unreal Build #397 on the same SHA again failed before C++ compilation because `NT AUTHORITY\\NETWORK SERVICE` could not read UE4.27.2 `WorldGridMaterial.uasset` across all six probes. No compile/runtime/PIE/device/visual status is promoted. The registered transition persistence/rollback/NPC lifecycle defects remain the next runtime repair wave once static validation is green on the exact new head.

## 2026-09-22 - Pre-Unreal #561 deep-audit false regression isolated

Exact-head Pre-Unreal #561 on `ed5af300852e6e2ce2264334c560af658250434b` reached `PRE-UNREAL CORE VALIDATION PASSED` and `PRE-UNREAL VALIDATION PASSED`, then failed in `Scripts/deep_project_audit.py` with one error: `async chapter streaming contract missing: FStreamableManager`. The streaming implementation is still asynchronous: `FStreamableManager` is declared in `ShireChapterAssetStreamingSubsystem.h`, while `FSoftObjectPath` and `RequestAsyncLoad` are used in the cpp. The audit had incorrectly required all three literal markers to appear in the cpp alone.

The deep audit now validates the async contract across the subsystem header+cpp while still forbidding `LoadObject<` in the streaming cpp. This is a static-audit repair only; chapter streaming runtime behavior is unchanged. The Work-session persistence/rollback/NPC findings remain open and registered under `EXT-REV-2026-09-22-018`.

Status remains **STATIC-PENDING** until a fresh exact-head workflow completes successfully. Unreal Build #396 is independent engine evidence and must be read on its own result. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made by this audit change.

## 2026-09-22 - Work-session playability audit reconciled and PG-117 guard repaired

The owner-forwarded Work review was rechecked against integration head `170ebd857bece56a6d7f76f4928efe0eb3426af2` rather than copied into governance verbatim. The review identified current-source risks that remain open: next-Tick chapter checkpoint capture is not synchronized to asynchronous world commit; save restore may apply a saved transform before the matching world is committed; failed-swap rollback can rebuild the prior builder while leaving movement held and logical/player state un-restored as one transaction; ambient residents use approximate-Z placement with collisionless body meshes; and living baseline population still uses SpawnActor/Destroy plus direct LoadObject in ambient visual setup. These findings are now durable under `EXT-REV-2026-09-22-018`, and REQ-SAVE-001 is downgraded from IMPLEMENTED to PARTIAL until the transition/persistence contract is repaired.

Two forwarded details were corrected rather than promoted: the indexed inventory reports 24 image files total, not 24 BMP files, with seven explicit Shire BMP paths visible in that inventory; and current Pre-Unreal diagnostics no longer stop at the historical #558 summary. Exact-head Pre-Unreal #560 on `170ebd857bece56a6d7f76f4928efe0eb3426af2` reported `PRE-UNREAL CORE VALIDATION PASSED` followed by one concrete failure: `PG-117 Part I visual current wave is not hero equipment V4`.

That #560 failure is another stale historical guard, not evidence that the hero-equipment V4 assets disappeared. `Part1VisualProductionPass.current_wave` is now the V10 early-realm world/life wave, while the dedicated `hero_character_equipment_v4` historical block and CharacterProductionMatrix V4 character wave remain present. PG-117 is therefore changed to preserve the V4 historical asset contract without requiring V4 to remain the global current visual wave.

This update changes governance/documentation and the static validator only; it does not yet modify the save/transition/NPC runtime defects above. Status remains **STATIC-PENDING** until a fresh exact-head Pre-Unreal run passes. Unreal Build #395 is a separate engine gate; no COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED claim is made here.

## 2026-09-22 - PR #67 exact-head Pre-Unreal #558 failure isolated

Exact-head Pre-Unreal run #558 on `809325a64547744f0cc4992d76c42fb7e0862d82` reached the project validator and reported exactly two static errors after validating 30 cpp files, 32 headers, 63 architecture entries, 32 quest definitions, 8 runtime chapters, 62 presentation cues and 50 dialogue sequences. Source inspection isolated both errors to the stale PG-111 guard: it still required the V9 world-life status and the old fixed half-density implementation marker after the integrated branch intentionally advanced to V10 chapter density profiles and `DangerPopulationFraction`.

The repair updates PG-111 to protect the V10 plan identity/status, require bounded per-chapter density profiles, preserve the P1C05/P1C06 civilian-empty and P1C08 bird-only rules, and assert the chapter-driven danger-thinning runtime path rather than the removed fixed-halving string. This is a validator-contract repair; it does not change LivingWorldDirector runtime behavior.

Unreal Build #393 on the same SHA failed earlier than compilation: the UE4.27.2 preflight ran as `NT AUTHORITY\\NETWORK SERVICE` and received access denied while opening `C:\\Program Files\\Epic Games\\UE_4.27\\Engine\\Content\\EngineMaterials\\WorldGridMaterial.uasset` on all six probes. The workflow remains fail-closed. This is not C++ compile evidence. Current integration status remains **STATIC-PENDING** until a new exact-head Pre-Unreal run passes, and it remains **NOT COMPILE-TESTED / NOT PIE-TESTED / NOT DEVICE-TESTED / NOT VISUALLY-ACCEPTED** until the engine-runner access blocker is repaired and the corresponding gates execute.

## 2026-09-21 - continuous transition audit integrated

The comprehensive integration branch now includes a same-session transition audit across P1C01-P1C08, FrodoMain/GandalfParallel route changes, committed-world/living-world revision agreement and a disk-save roundtrip. Separate chapter boot success is no longer accepted as evidence for continuous transition integrity. PG-124 protects the audit wiring while preserving the startup-grounding markers.

This remains **IMPLEMENTED / STATIC-PENDING** until the exact integration head passes Pre-Unreal. UE4 engine execution remains a separate gate.

## 2026-09-21 - comprehensive foundation integration train active

The owner directed the project to stop accumulating isolated proposals/repair branches and resume coherent construction. The active convergence branch is now `integration/comprehensive-foundation-v1`, recorded by `REQ-INTEGRATION-001`, `DEC-031` and `WORK-INTEGRATION-001`.

The branch currently integrates the startup-grounding/QA/performance stack with V10 regional living-world work and a stronger transactional transition model. Chapter asset streaming is now two-phase: preload completion does not replace the resident bank. `ChapterWorldRouter` freezes the player only at the swap boundary, constructs the destination, proves blocking-ground placement, commits the pending asset bank, then publishes a new `WorldRevision`. Failure does not publish a revision and attempts to restore the prior builder while keeping movement held.

`LivingWorldDirector` now combines V10 chapter density/role profiles with committed-world synchronization. Quest state may move ahead while streaming, but destination residents/weather/context are not applied until the router publishes the matching committed revision.

PG-123 statically protects the integrated two-phase asset/world/living-world contract. This is **IMPLEMENTED / STATIC-PENDING** on the newest integration code. It is not COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or visually accepted until exact-head gates run.

## 2026-09-21 - visual-performance proposal adopted with measured guardrails

A new programmer proposal for Witcher-class visual ambition with low-spec UE4.27 optimization was reviewed against the live architecture and promoted into durable project memory as `EXT-REV-2026-09-21-017`, `REQ-PERF-003`, `DEC-030` and `WORK-PERF-006`.

Useful parts are active now: preserve soft/asynchronous heavy-asset ownership, HISM/ISM + explicit culling for repeated detail, non-ticking world builders, and no heavy synchronous work inside Tick. `Scripts/deep_project_audit.py` now protects those already-working architecture contracts and `Data/VisualPerformanceOptimizationPlan.json` records the staged optimization path.

The proposal was not copied literally. Current generated chapter geometry makes blanket Lightmass inappropriate; Distance Field Shadows are not assumed cheaper on the ~2 GB VRAM target; World Composition will not replace the working ChapterWorldRouter/async-bank architecture without a measured topology need; LOD/material policies remain role- and profile-driven.

This wave is **STATIC-PENDING** until the exact branch head passes Pre-Unreal. No FPS, VRAM, device, PIE or visual improvement is claimed yet.

## 2026-09-21 - QA immune-system foundation implementation

The first `REQ-QA-002` implementation wave is now in source on dependent branch `qa/automated-immune-system-v1`. `ShireJourneyEditorTools` contains two initial Unreal Automation Framework tests: `ShireJourney.QA.Save.DefaultState` and `ShireJourney.QA.Assets.StreamingBankPackages`. The first checks SaveGame schema/default invariants; the second checks that every soft-path package declared by `ChapterAssetStreamingPlan.json` exists after the production import step, without synchronously loading those heavy assets.

`ci_run_project_automation.cmd` runs the suite through UE4Editor-Cmd and `parse_automation_report.py` rejects missing or failed required test results. The self-hosted workflow places this new engine-level layer after compile/import and before existing runtime startup/chapter/state audits.

The P1C01 fall-through regression is also strengthened: placement now logs `PLACED`; CI only receives `ShireStartupGrounding: PASS` after two seconds with blocking ground, no falling movement mode, and bounded displacement. This prevents an immediate line trace from being mistaken for sustained grounding.

Evidence boundary: **IMPLEMENTED / STATIC-PENDING** until Pre-Unreal runs on the exact head. No COMPILE-TESTED or PIE-TESTED claim is made.

## 2026-09-21 - automated QA immune-system direction adopted

The owner supplied a programmer proposal to expand CI into a broader automated QA immune system. The direction is adopted after live-repository review, with project-specific corrections recorded in `EXT-REV-2026-09-21-016`, `REQ-QA-002`, `DEC-029` and `WORK-QA-003`.

The first implementation wave is deliberately dependent on the active startup-grounding repair rather than competing with it. It will add UE Automation Framework tests and an exact-head runner after compile/import, while preserving `runtime_smoke.py` as the end-to-end chapter/state layer. Deterministic authored probes replace random-point tests; target-device measurements will set memory/hitch thresholds; headless checks do not become visual acceptance.

Status before code wave: **PLANNED / STATIC-PENDING**.

## 2026-09-21 - deterministic P1C01 spawn support

The startup-grounding repair now also removes imported-mesh collision from the first-frame dependency. P1C01 receives a hidden Engine BasicShapes collision pad centered at the authored start `(-2410,-120)` with its top at the authored road height. The larger hidden Shire collision foundation remains underneath the region. This means initial grounding can succeed even if the imported OBJ road/ground mesh has no usable generated simple collision.

This remains a **FIX_CANDIDATE**. No claim is made that the owner-observed fall-through is resolved until exact-head engine validation and defect-specific P1C01 PIE observation pass.

## 2026-09-21 - startup fall-through root cause and regression repair

Owner reproduced a previously claimed startup fix as still broken: on first PIE launch the player can fall below the world. Source inspection identified the ordering defect. `AShireGameMode::BeginPlay` teleported the pawn to P1C01 coordinates immediately, while `AChapterWorldRouter` intentionally waits for asynchronous chapter asset streaming before spawning the Shire world. Raising the spawn Z did not close that race because there can still be no blocking ground under the pawn when gravity begins.

The isolated repair branch `fix/startup-grounding-regression-v1` removes the GameMode pre-commit teleport. ChapterWorldRouter now holds initial character movement while the first bank streams, moves the pawn only after the builder commits, line-traces a blocking floor, places the capsule from the measured floor height, and releases movement only on success. Missing ground fails closed with `ShireStartupGrounding: FAIL` rather than allowing indefinite falling.

Automation now requires a chapter-specific `ShireStartupGrounding: PASS` marker for normal startup, state audit and P1C01-P1C08 chapter audits. PG-121 rejects reintroduction of the old pre-commit GameMode teleport.

Status is **FIX_CANDIDATE / STATIC-PENDING** until the exact branch head passes Pre-Unreal. It is not COMPILE-TESTED or PIE-verified. The self-hosted Unreal runner also has a separate local UE4 Engine Content file-access blocker that must be repaired before engine proof can complete.

## 2026-09-21 - path cleanup before post-V5 production

Authority remains `Data/ProjectGovernor.json`. The integration baseline is `develop` at `8d7247d229b5cd51e8aea5617e1e2030b38229bf`, green after PR #60 with Pre-Unreal #532 and Unreal Build #367. There is exactly one open production PR: #61, `production/chapter-streaming-v5`.

The latest V5 code head before this cleanup is `b882b052a59c8d4e19437d7877dc30c9b1ea5daf`. Pre-Unreal #538 passed; Unreal Build #373 was pending when this reconciliation was written. Earlier V5 failures were narrowed to concrete UE4.27 issues and repaired: the `FStreamableHandle` declaration conflict (#370), invalid conditional `UE_LOG` verbosity (#371), and a stale async completion edge case after returning to an already resident world. This cleanup commit is newer than those checks and must earn fresh exact-head proof.

The path is now explicit: finish V5 -> merge only after exact-head Pre-Unreal + full Unreal validation -> confirm develop returns green -> measure chapter seam hitch/streaming pool/resident memory on representative target hardware -> open the next short production branch. No V5 FPS/RAM/VRAM improvement is claimed from architecture alone.

The next production branch is intentionally focused on visible world life rather than another mixed mega-branch: Shire, Bree, Rivendell and Lothlorien first for architecture density, culture-specific dressing, bounded NPC density, routines and ambient life. The character-quality lane advances through real skeleton/skin/Skeletal Mesh/AnimBP/animation work; OBJ-to-FBX container conversion alone is not treated as rigging.

Repository hygiene was reconciled. PR54 and PR56-PR60 short branches are historical cleanup candidates after external-reference checks. `recovery/stached-charcter` and `repair/post-merge-unreal-339` are preserved. The scheduled "Develop 20-Min Validation" appearing under `main` is expected GitHub scheduler behavior because `main` is the default branch; that workflow explicitly checks out `develop` and does not change the rule that production work integrates through `develop`.

## 2026-09-20 — V6 continuation and source/governor audit

Authority remains `Data/ProjectGovernor.json`. Its previous handoff was stale at #303; the actual verified baseline is `cd58be1e1cea033295a163ef2a90985f30471c2b`, Pre-Unreal #484 and Unreal #319, including import/startup/eight chapters/state/save/warnings. V6 head `93092a82b95418552728c73e02d31c220a7457ac` passed Pre-Unreal #485. Unreal #320 attempt 1 was interrupted during UHT/build (Ctrl-C, -1073741510); this is not a demonstrated C++ code defect. The single rerun (attempt 2) was also interrupted, before compilation at the editor-wait step. The cancellation trigger is not established; no further blind reruns were requested.

V6 refines original modular head/torso/hair geometry for nine Fellowship characters; it is not final skeletal animation or visual acceptance. Preserve that distinction.

The Governor now validates exact SHA scope for baseline/current workflow evidence and prints when a checkout is not covered by the recorded snapshot. A successful ancestor cannot silently certify the current checkout. Six regression cases cover mixed SHA evidence, cancelled current runs, invalid green baselines and missing experiential boundaries.

Uploaded source identities were verified against the reference index. Bible 09 now has its fingerprint. Targeted review of story, mission and visual-reference guidance confirms safe optional windows, explicit mission state/QA and the separation of visual inspiration from canon. The reference books' F1-xx identifiers do not equal runtime P1Cxx identifiers; numeric suffix matching is unsafe. Full scene-level provenance and rendered/device acceptance remain open. Green #319 still carries 132 unique near-zero-binormal identities under the existing 150 limit; passing the warning guard does not mean zero asset debt.

## 2026-09-20 — final lightweight geometry-warning cleanup

The green #302 baseline still carried 50 degenerate-tangent and 53 nearly-zero-binormal import identities. Inspection of representative production OBJ sources confirmed that these flat-color meshes have no `vt` texture-coordinate records. MikkTSpace therefore had no valid UV basis and was generating warning debt that did not improve the current material path.

The production importer now detects untextured OBJ meshes and explicitly computes normals with UE4's built-in tangent generator while keeping MikkTSpace/default behavior available for any future OBJ that actually supplies texture UVs. The exact-head chain must prove the warnings are removed before the debt is marked fixed or warning ceilings are tightened.

Two obsolete bootstrap/checkout PowerShell scripts are removed in the same cleanup because the workflow now bootstraps and checks out safely before repository scripts are available.

## 2026-09-20 — warning evidence scope repair

Run #300 confirmed the material persistence repair itself works: 225 authored material packages were explicitly saved with zero failures and the commandlet verified zero missing physical files. The warning gate remained red because import-time `LoadObject` existence probes intentionally asked for not-yet-created material packages, generating 216 warnings before synthesis.

That is now corrected at both ends: importer probes use `FindObject` plus `FPackageName::DoesPackageExist` before any load, and missing-package debt is evaluated from runtime startup/chapter/state logs rather than the import log. Exact-head CI logs are also cleared before each run so stale evidence cannot contaminate a new SHA.

The runtime missing-world-package ceiling is now zero. Any package that is genuinely absent after import will still fail the gate.

## 2026-09-20 — exact-head material persistence final blocker

Run #299 proved the entire machine chain through real UE4.27.2 build/import/startup, P1C01-P1C08 and isolated disk save/state roundtrip. The only failing gate is warning debt: 216 unique world material packages are referenced by imported meshes but are absent on disk.

The importer already synthesizes the intended authored material instances. The repair now bypasses unreliable unattended editor save helpers for these packages and writes each package explicitly with `UPackage::SavePackage` to its deterministic `.uasset` path, then verifies physical file existence before the commandlet can report success.

No threshold was raised and no debt was hidden. The next exact-head run must prove this repair.

## 2026-09-20 — mega-wave runway repair

The pre-production runway was repaired before the next mega build wave. REQ-AUDIT-001 is now represented in the master roadmap/tracked snapshot, PG-037 validates the new asynchronous checkpoint contract, and the Windows UE4 CI target now uses project-only clean intermediates, single-action compilation and CI-only disabled debug symbols to remove the recurring VS2019 D8050 debug-record failure mode. Local developer/editor builds retain normal debug symbols.

This is preparation, not a green claim: the new exact head must still pass Pre-Unreal and the real UE4.27.2 compile/import/startup/eight-chapter/state/warning chain.

## 2026-09-20 — deep exact-head validation reconciliation

Exact head `c023a735e3e390b8d591e1f6df9d07aeaa054754` reached the strongest automated evidence chain so far: Pre-Unreal #450 passed, and Unreal Build Validation #285 passed the isolated MSVC probe, UE4.27.2 C++ build, production asset import, Python resolution, playable startup, every P1C01-P1C08 chapter audit, and the route/story/state audit with an actual isolated disk save/load roundtrip.

The workflow failed only at warning-debt aggregation. Audit of the guard found a validation-harness defect: identical tangent/binormal warnings copied through multiple CI logs were counted repeatedly as separate debt. The guard now counts unique mesh/package identities and prints those identities. This does **not** waive real asset debt; it makes the next repair target exact instead of occurrence-inflated. The remaining world-package identities will be repaired from the next rerun.

No rendered/PIE visual acceptance, FPS claim or Production 100 promotion is made from this machine evidence.

## 2026-09-20 — MSVC execution blocker

Runs 35500465321 and 35500597711 failed with MSVC D8050 (`failed to get command line into debug records`) across compilation actions, also on single-process retry. This has not yet tested the new disk-audit C++ code. The workflow now prepares a writable per-run TEMP/TMP and probes one-line C++ compilation with plain, /Z7 and /Zi settings before invoking UnrealBuildTool. These are job-local changes only; compiler failures remain failures and no debug verification is disabled.

## 2026-09-20 — state fixture correction after eight chapter passes

Run 35500242164 passed startup and all eight chapter audits. The state audit exposed an outdated test fixture: `StartExperience` correctly restores stored route progress, so calling it on the initial Frodo route did not advance to P1C03; the fixture also bypassed the activity reward entry point. The audit now explicitly starts P1C03, verifies the closed activity window rejects reward, opens `MidgewaterRoad`, verifies direct reward bypass is rejected, then completes the activity through its guarded API and verifies duplicate reward rejection. Required expected reward values remain unchanged. This fixes the test setup without weakening production story/reward guards. Full rerun remains required.

## 2026-09-20 — close the disk persistence evidence gap

The Python resolver repair passed on Windows and startup succeeded on `15e9d2228f6e7e5ceb1e8aed2aab8b698dba4cb8` ([run 35500242164](https://github.com/4youbabee-tech/fellowship-personal-game/actions/runs/35500242164)). Chapter/state checks were still running when this update was written.

Source audit confirmed the existing route/state test did not write a save file. The new `disk-save-roundtrip` audit calls the production player snapshot/restore path, writes a unique CI save slot, mutates live quest/progression/knowledge/player values, loads from disk, verifies restored fields, and deletes only its own temporary slot. It checks health/stamina/resolve/supplies, transform, route/chapter/episode/character, quest stages, story beats, discoveries, progression and Chronicle/map knowledge. It is not yet full NPC-memory or cross-process migration coverage. The observer requires the disk marker for state success. CI runs cannot overwrite or load the owner's manual/checkpoint slots. Thirteen observer tests pass locally; real UE compilation and disk execution of this change remain pending.

## 2026-09-20 — exact-head runtime validation repair

Authority: `Data/ProjectGovernor.json`, including `session_handoff`.

On `b0a4d2614e5744d8a0fa3b1c373c23a491274955`, Pre-Unreal #446 passed. Unreal run [35499375838](https://github.com/4youbabee-tech/fellowship-personal-game/actions/runs/35499375838) built UE4.27.2 C++ and imported production assets successfully. Runtime audits did **not** execute: Python discovery selected a Microsoft Store alias and exited 61.

The repair validates local interpreter candidates, excludes WindowsApps aliases, checks installed/launcher/toolcache/UE-bundled interpreters, and supports Python 3.7 in the observer. It neither installs software nor modifies Windows settings. State audit now has a separate log from startup. Twelve observer regression tests pass locally; Windows execution and full runtime proof remain pending the new CI run.

Next: complete exact-head startup, all eight chapters and actual save/load proof; only then resume visible production. No new visual, performance or gameplay acceptance is claimed.

## PHYSICAL SIDE-ACTIVITY GAMEPLAY WAVE — 2026-09-20

B1 now includes reusable physical challenge gameplay instead of relying entirely on proximity discovery triggers. `AShireTraversalChallenge` implements an ordered three-gate route, verifies opening/closing story beats, awards only the linked first-time Journey Discovery, and therefore feeds the existing Chronicle/map/progression systems without changing FILM_CORE.

The Shire field race now uses the ordered route and completes `Side_SharedShireMemory` only after the route. Moria's `MORIA_ECHO_ROUTE` now uses the same mechanic for Follow the Echo before MoriaUnease closes the optional window. PG-081 guards both runtime placements.

This is implementation evidence; exact-head UE4.27 compile, runtime placement and PIE pacing remain required.

## CHRONICLE + MAP KNOWLEDGE + SIDE-ACTIVITY PROGRESSION MEGA-SLICE — 2026-09-20

B1 expanded again from plan-only into persistent runtime. First-time Journey Discoveries now create main-film Chronicle entries and mark the current route/chapter as known map knowledge. Both collections persist through save schema v6. Book Chronicles remain explicitly separate and are not inserted into this main-film runtime registry.

The C key now opens a Chronicle & Journey HUD panel showing recent Chronicle entries, known regions, Journey Insight and all seven progression tracks/ranks. Contextual side activities are also parsed at runtime: when a linked first-time discovery completes, its authored activity type adds bounded XP (for example CAMP_PREPARATION -> CAMPCRAFT, TRACKING/OBSERVATION -> PERCEPTION, SOCIAL_MEMORY -> FELLOWSHIP). Anti-farm behavior remains first-time-only.

State automation now requires `ShireStateAudit: knowledge-core=PASS`, and PG-080 checks save/UI/input/continuity/side-activity wiring. Exact-head UE4.27 compile/import/startup/state evidence remains required before engine validation is claimed.

## PLAYER-LIFE + PROGRESSION RUNTIME MEGA-SLICE — 2026-09-20

B1 modern-game work is now runtime, not only planning. The player has lightweight Stamina, Ring-pressure-sensitive Resolve and capped travel Supplies alongside Health. Sprinting drains/rebuilds Stamina; damage and Ring pressure affect Resolve; R consumes one supply only when recovery is useful. No hunger/thirst timers, gear score or random rarity loop was introduced.

Seven persistent progression tracks now exist: WAYFINDING, PERCEPTION, QUIET_STEP, CAMPCRAFT, FELLOWSHIP, LORE and RESOLVE. First-time Journey Discoveries award track XP by category, so repeated discovery cannot farm progression. Fellowship Bond is derived from the FELLOWSHIP track. Save schema v5 persists life state and ProgressionXP.

PG-079 guards the full contract and state-mode automation requires `ShireStateAudit: progression-core=PASS`. Exact-head UE4.27 compile/import/startup/state proof is still required before this becomes engine-validated.

## MASTER EXECUTION CONTROL — 2026-09-20

The growing request set is now consolidated into `Data/MasterExecutionRoadmap.json` and the human board `Docs/MASTER_EXECUTION_BOARD.md`. The roadmap is subordinate to the Governor and maps every unfinished requirement plus every ACTIVE work item into large dependency-ordered production bundles. PG-078 makes orphan accepted work a static-validation failure.

Execution order is now explicit: exact-head stability; Part I story/gameplay completeness; production characters/world; living-world/presentation; acceptance/merge; then source-verified Part II/III. Active work items have unique execution ranks/bundle labels so the project no longer behaves like a flat unordered list.

## FILM SIDE-CONTENT MASTER AUDIT — 2026-09-20

The owner supplied a programmer proposal covering trilogy-wide side play and asked for one reconciled, future-proof request set. `Data/FilmSideContentMasterPlan.json` is now the side-content master taxonomy: FILM_MOMENT = verified film action turned into gameplay; FILM_EXPANDED = small plausible play around an existing film scene/place; CHRONICLE = book-only/history/past-character content kept visibly separate from Film Main Canon.

The audit also records continuity corrections: Fellowship does not literally begin at the birthday party; Weathertop fire cannot prevent the Nazgul attack; Prancing Pony attention cannot avoid the Ring incident; Moria's door is a guided canonical puzzle; Entmoot side play cannot replace the film decision causality; Oliphaunt observation does not grant a canon-breaking future weakness; Return of the King's beacon prototype centers on Pippin lighting the Minas Tirith beacon; Glorfindel/Scouring stay Chronicle-only.

PG-077 guards taxonomy/canon separation. Runtime rollout remains behind the current exact-head UE4.27 validation gate.

## SIDE-CONTENT CANON AUDIT — programmer proposal reconciled

The programmer's trilogy proposal is retained but normalized into four continuity classes: FILM_CORE, FILM_EXPANDED, FILM_INTERSTITIAL and BOOK_CHRONICLE, with source-verification tracked separately. The audit corrects one important opening claim: Fellowship does not begin at Bilbo's party; the prologue and Bilbo/Frodo-Gandalf opening precede it.

Part I and Part II entries are now source-audited against the supplied screenplays/project canon where available. Part III remains FUTURE_SOURCE_CHECK at scene level. Book-only Tom Bombadil/Barrow-downs, Glorfindel-at-the-Ford and Scouring content is explicitly isolated from main film continuity. PG-077 protects this separation.

## ENSEMBLE FILM MISSIONS — 2026-09-20

Frodo remains the Ring-quest center, but the film itself now decides who should be playable for each event. `Data/EnsembleFilmMissionPlan.json` maps Gandalf, Arwen, Aragorn, Boromir, Legolas, Gimli and later Merry/Pippin/Sam/Faramir/Eowyn opportunities. The design rule is film action first, character-specialty gameplay second, small original gap-fill last.

Part III mission details remain source-check-only until exact film/script verification. PG-076 guards the ensemble contract.

## ENSEMBLE FILM-MISSION RULE — 2026-09-20

The owner clarified that the film itself already supplies many mission opportunities outside Frodo. Frodo remains the Ring-quest center but is no longer treated as the default controller for every event. `Data/EnsembleFilmMissionPlan.json` now prioritizes playable film actions for Gandalf, Arwen, Aragorn, Boromir, Legolas, Gimli, Merry/Pippin and later-film characters, then allows only small source-safe gap-fill around those verified scenes.

Part I now explicitly identifies Gandalf Ring investigation/Isengard, Arwen at the Ford, Boromir training and Amon Hen defense, Legolas scouting, Gimli/Moria cultural gameplay and Aragorn scouting/leadership as viewpoint opportunities. Part II maps the Three Hunters, Merry/Pippin/Fangorn, Gandalf/Rohan and source-checked Faramir/Eowyn focused episodes. Part III remains FUTURE_SOURCE_CHECK at mission-detail level until exact film/script verification is available.

PG-076 protects viewpoint/source/canon rules. This is a production/design contract; runtime mission handoffs and character-specific mechanics remain pending implementation and UE4.27 proof.

## MODERN GAME LAYER LOCKED — 2026-09-20

The owner explicitly requested a broad modern-game research pass and adoption of fitting game systems throughout the film-based experience. `Data/ModernGameLayerPlan.json` now locks the rule: mandatory Peter Jackson film anchors stay fixed, while optional play may expand only inside story-safe gaps.

The plan adapts modern design patterns - meaningful exploration rewards, short world events, semi-open chapter hubs, companion dialogue during free play, earned map knowledge, environmental/traversal puzzles and reactive inhabitants - into original Middle-earth gameplay. Character life is also defined beyond a health bar through bounded Stamina, Resolve, Fellowship Bond and Supplies, with progression in Wayfinding, Perception, Quiet Step, Campcraft, Fellowship, Lore and Resolve. Survival micromanagement, gear-score grind, loot spam and canon-changing upgrades are explicitly excluded.

P1C01-P1C08 plus P1G01 now each have chapter-specific optional activity families while fixed film outcomes remain mandatory. PG-075 guards this contract. Runtime rollout remains staged and exact-head UE4.27 evidence is still required before any implementation is called validated.

## JOURNEY DISCOVERY RUNTIME MEGA-SLICE — 2026-09-20

Journey Discovery has moved beyond a static design contract. The existing quest subsystem now owns a data-driven first-time discovery registry loaded from `Data/JourneyDiscoveryRewardPlan.json`; all 26 current Part I discoveries are wired into Shire, Bree, P1C03-P1C08 and Isengard world triggers with explicit opening/closing story-beat windows. Rewards derive Journey Insight, region-completion bonuses and milestones without changing required story state.

Discovery IDs/Insight/milestones now persist through the existing save/load path with sanitation on restore. A dedicated HUD discovery card presents the first-time reward separately from combat/error alerts. State-mode automation also requires `ShireStateAudit: discovery-core=PASS`, proving a discovery cannot be farmed by repeat activation and survives the Frodo/Gandalf/Frodo route roundtrip in subsystem state.

This remains implementation evidence until the exact current PR head passes real UE4.27 compile/import/startup/chapter/state validation.

## MEGA-PASS RED-TO-GREEN REPAIR — current exact head

Intermediate head `5699ef0` passed Pre-Unreal Validation #348. The previous Unreal engine attempt reached real compilation and exposed a UE4.27-specific incompatibility in the new non-destructive production importer: `IFileManager::CopyDirectoryTree` is not available there. The importer now keeps the same safety design but uses UE4.27-compatible `IPlatformFile::CopyDirectoryTree`.

The current exact head is intentionally still pending validation. No merge, compile-success, import-success or visual acceptance is claimed until the new head completes the full gate.

## MEGA PRODUCTION BATCH — RING / CHARACTERS / CINEMATIC WORLD — 2026-09-20

The owner closed Unreal and ordered immediate large-scale continuation. This batch turns three previously discussed directions into durable production contracts. The One Ring is now a CRITICAL systemic axis with a runtime bearer/state/pressure API and a headless route-roundtrip audit requirement. The full Part I named cast is now tracked through a model → material → rig → skin → animation → UE4 → LOD pipeline with provenance rules and a custom-character fallback. Every active Part I region now has a cinematic hero-vista and layered foreground/midground/background target based on the owner's dense forest reference.

New production authorities: `Data/TrilogyRingQuestPlan.json`, `Data/CharacterProductionMatrix.json`, `Data/CinematicWorldProductionMatrix.json`, and `Data/OwnerSourceReferenceIndex.json`. Static guards PG-070 through PG-073 protect the new contracts.

Proof boundary remains strict: these are source/data/runtime implementation changes. They are not yet UE4.27-validated or visually accepted until the exact PR head passes Pre-Unreal and real engine validation.

## WORLD BEAUTY BAR RAISED — 2026-09-20

The owner rejected the earlier plain reference-image quality as the final target. The project now explicitly targets a more beautiful cinematic world: layered vistas, richer terrain/materials/vegetation, stronger water/fog/light atmosphere, hero landmark composition and region-specific visual identity. This does not relax the target-device budget; the visual strategy is selective hero detail plus LOD/instancing/culling so 720p Low-Medium / 30 FPS remains the floor target.

## CONTEXTUAL SIDE-PLAY CONTRACT — film story stays fixed, game expands between scenes

The owner reaffirmed the core rule: this remains the Peter Jackson film story. Original side content is allowed only as plausible off-camera gap-fill inside the same time, location, companions, knowledge and emotional/danger context. `Data/ContextualSideActivityPlan.json` now defines 18 optional mini-game/social/exploration activities across FrodoMain P1C01-P1C08 plus GandalfParallel P1C01.

Examples include Shire party errands and a friendship race, Bree observation/tracking, Strider trail-reading, Rivendell map/memory moments, Fellowship camp practice, West Gate stone observation, Moria echo navigation, Lothlorien grief/boat preparation, Anduin river reading, Amon Hen tension observation and Orthanc prisoner observation. Every activity is bounded between exact film story anchors, forbids future knowledge, cannot advance a required anchor, and yields only the existing Journey Discovery/Chronicle/dialogue-memory rewards.

PG-063 now guards those constraints statically. Runtime side-activity triggers, save/UI wiring and UE4.27 play validation remain pending; the exact-head merge gate is unchanged.

## JOURNEY DISCOVERY SYSTEM — exploration now has persistent game rewards

The owner requested the satisfying feeling of discovering a place and receiving a bonus, similar in spirit to exploration RPGs, but adapted to this world's tone. `Data/JourneyDiscoveryRewardPlan.json` now maps 26 declared optional discoveries to first-time Journey Insight rewards. Rewards prioritize Chronicle entries, map memory, lore/dialogue topics, companion memories and local hazard knowledge rather than generic combat-stat inflation.

Four thematic tracks keep the system in-world: Road Wisdom, Peoples and Places, Fellowship Bonds and Peril Sense. Every active Part I exploration route/chapter also has a region-completion bonus. Milestones unlock subtle navigation/content benefits, never story skips or alternate canon outcomes. PG-062 enforces one-time rewards, complete discovery coverage, no canon mutation and packaging.

Runtime trigger/save/HUD/Chronicle wiring is still pending; this commit is a static/game-design contract while Unreal remains busy. Full acceptance still requires UE4.27 and save/load automation on the exact final head.

## PARALLEL NON-UNREAL MEGA-PASS — shader-compile time used productively

While the target machine is busy compiling shaders, CP56 continues with work that does not require interrupting the editor. `Data/ExplorationEnvelopePlan.json` now defines safe free-roam windows, optional discoveries and return-to-main-story behavior for FrodoMain P1C01-P1C08 plus GandalfParallel P1C01. PG-060 checks that optional exploration cannot reorder, advance or replace mandatory film-story anchors.

The source-grounded original dialogue bank has also expanded from 26 to 53 validated variants across Shire, Bree, wilderness, Rivendell, Fellowship travel, Moria, Lothlorien, Amon Hen and Isengard. PG-061 locks in the production-import hygiene fix: OBJ normalization/import must operate on an ignored `Saved/` working copy rather than dirtying tracked `SourceAssets`.

This is productive parallel work, not a merge bypass. The final PR #53 exact head still must pass Pre-Unreal plus UE4.27 compile/import/startup/chapter/state/warning validation before integration into `develop`.

## CP56 SOURCE-GROUNDED LIVING DIALOGUE MEGA-PASS - 2026-09-19

The owner-supplied Fellowship and Two Towers screenplay PDFs are now durable story/dialogue reference sources. `Data/FilmDialogueSourceContext.json` stores only derived context: source identity/hash, scene windows, route/chapter/story-beat progression, tone, safe topics and future-knowledge blocks. Runtime dialogue remains original and offline; raw screenplay passages are not shipped.

Part I contexts cover P1C01-P1C08 plus Gandalf's Isengard route. The Two Towers source is indexed into future Part II arc seeds for Frodo/Sam/Gollum, the Rohan hunters, Merry/Pippin/Ents, Gandalf/Rohan and Saruman/Isengard, without claiming Part II runtime completion.

PR #53 still requires exact-head Pre-Unreal and UE4.27 validation before merge.

## CP56 MEGA INTEGRATION ACTIVE — whole-game coherence pass

PR #53 is the single continuation path above PR #52. The mega batch is tracked by `REQ-MEGA-001`, `WORK-MEGA-001`, `Data/CP56MegaIntegrationPlan.json` and `Data/GameCompletenessMatrix.json`.

Current runtime expansion now reaches named-character behavior, not just data: companion spacing and catch-up respond to regional pressure, named profiles expose a personality-aware emotional state, free interactions choose mood-aware intents with deterministic greeting fallback, and authored regional dialogue covers Shire peace, Bree suspicion, pursued wilderness, Rivendell refuge, Fellowship pressure, Moria dread, Lothlorien grief/refuge, Anduin fracture and Isengard corruption. All shipped logic remains offline and subordinate to story, knowledge and memory gates.

This does not claim final rigs, voice, materials, device performance, cinematic acceptance or trilogy completion. The merge gate is unchanged: the current PR #53 head must pass Pre-Unreal plus the complete UE4.27 compile/import/startup/chapter/warning chain before develop integration.

## CP56 continuation — contextual companion dialogue, 2026-09-19

Recovered prior-session stopping point: CP56 head 3705fe4, PR52 awaiting Unreal. Its latest engine attempt failed during checkout, before compilation. Follow-up PR53 now includes the tracked-source checkout fix plus a correction to regional dialogue selection and 30 original Moria/Lothlorien companion lines. Actual engine build and gameplay validation remain pending. No new checkpoint or trilogy completion is declared.

## Automation-first delivery follow-up — 2026-09-19

REQ-QA-001 records the owner request to reduce manual technical testing. Runtime boot observation and subprocess regression tests are implemented on a follow-up branch based on CP56; Windows UE validation remains pending. See `Docs/AUTOMATION_FIRST_DELIVERY.md` for the trilogy/opening/side-exploration contract and ordered engine-test work. This adds no completed gameplay chapter and grants no new visual, performance or owner sign-off. Existing CP56 requirements remain active.

## CP56 ACTIVE — FELLOWSHIP EXPERIENCE MEGA-PASS

CP55 was merged after Pre-Unreal #273 and Unreal Build Validation #108 passed on the validated branch head. CP56 now expands moment-to-moment play while preserving the same Part I film chronology.

What CP56 changes now:
- P1C01 adds visible pre-adventure Shire friendship/play: Green Dragon revelry, party-field mischief, a shared-memory race/play beat, extra party revelers and play runners.
- P1C02 adds denser Prancing Pony/common-room life.
- P1C03 adds optional road companionship before Weathertop tension.
- P1C05 strengthens camp companionship around the Fellowship training stop.
- P1C06 adds a dead-city discovery beat without adding civilians/fauna to Moria.
- P1C07 adds a shared-grief clearing before Lothlorien story pressure.
- P1C08 adds a river-camp tension beat before the Fellowship fractures.
- `Data/FellowshipExperienceMegaPassCP56.json` and PG-058 preserve the film-spine/non-blocking contract.

Story rule remains unchanged: required film outcomes are fixed; optional friendship, exploration and local-life content fills the spaces between them. Dialogue remains original game writing rather than screenplay reproduction.

This is implementation-in-progress and still requires its own Pre-Unreal and real UE4.27 build/import/startup/chapter regression pass before merge.

## POST-VERIFICATION RESUME — CP55 OPENED

### CP55 activity/movement implementation

CP55 now adds a bounded visible world-life layer on top of the existing LivingWorldDirector:
- project-owned low-poly bird, rabbit and butterfly production meshes,
- distinct flight / hop-rest / flutter motion,
- chapter-aware fauna selection through disposable micro-events,
- no quest/save ownership and no persistent fauna transforms,
- Moria remains dead-city/fauna-empty by design,
- PG-055 guards the new plan/assets/runtime wiring.

Proof boundary: implemented in source/data/assets, but CP55 itself still requires its new Pre-Unreal and real UE4.27.2 compile/import/runtime regression pass before it is called validated.


The post-CP54 current-head verification freeze is now closed by explicit project-owner confirmation.

Verified merged baseline:
- `develop@f7c2b081e7b064fcf27bb4c80124b21f351331ab`
- Pre-Unreal Validation #264: SUCCESS.
- Unreal Build Validation #99: SUCCESS.
- UE4.27.2 build/import: SUCCESS.
- playable startup smoke: SUCCESS.
- headless P1C01-P1C08 chapter audit: SUCCESS.
- runtime warning-debt guard: SUCCESS.
- human verification/check/fix pass: owner-confirmed complete on 2026-09-19.

The owner sign-off is recorded in `Docs/PIE_VERIFICATION_SIGNOFF_2026-09-19.md` and `Data/PIEVerificationEvidence.json`. Numeric FPS/hitch/memory values that were not supplied are intentionally not fabricated.

Current development mode is restored to visible production/expansion. CP55 resumes environmental activity/movement and world-life depth while preserving story/save/route integrity, the 720p Low-Medium target, and the existing CI/UE4 regression gates.

## VERIFICATION MEGA-PASS — PR #45

The verification branch now has a successful real UE4.27.2 machine pass across all eight Part I runtime chapter boots.

Evidence on PR #45 before the hard-gate follow-up commit:
- Pre-Unreal Validation: SUCCESS.
- UE4.27.2 C++ build: SUCCESS.
- Production asset import: SUCCESS (307 imported files, 0 import failures).
- Headless playable startup: SUCCESS.
- Headless chapter audit: P1C01, P1C02, P1C03, P1C04, P1C05, P1C06, P1C07 and P1C08 all loaded their expected runtime builder plus living-world/weather context without a fatal/assert/ensure blocker.

This is a major machine-verification improvement, but it is deliberately **not** recorded as PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED.

The same verification batch now adds executable freeze enforcement (PG-056), structured human PIE evidence enforcement (PG-057), and a fast production-source asset-quality audit. This allows repair/verification work to continue quickly while CI rejects new checkpoint/content expansion during the freeze.

## IMMEDIATE FREEZE — current-head PIE/device verification

**Content baseline:** CP54 at `ed235ff4fb332660d2af8ce1385d9ca038a6337b`. **Develop head entering PR #45:** `043476f4353a44c1d08bf60ab87af5c3e10543f2`. Manual PIE evidence must always record the exact tested post-merge commit.

**CI evidence already green:** PR #44 Pre-Unreal #240 and Unreal Build Validation #75. This proves static validation, real UE4.27 compile/import and headless startup for the PR head. It does **not** prove current-head PIE traversal, visual quality, NPC behavior in play, save/load round trips, or target-laptop performance.

**Current rule:** no CP55 and no new feature/content batch until the existing CP24-CP54 body of work is inspected in real UE4.27 PIE on the target laptop, chapter by chapter.

Order:
1. P1C01 Shire
2. P1C02 Bree
3. P1C03 Weathertop/Ford
4. P1C04 Rivendell
5. P1C05 Road/Caradhras/West Gate
6. P1C06 Moria
7. P1C07 Lothlorien
8. P1C08 Anduin/Amon Hen

For each chapter record: WORKING / INTERMITTENT / BROKEN / CRASH, FPS/hitch/memory observations, NPC routines, ambient NPC-to-NPC conversations, named-NPC memory/context where applicable, and actual atmosphere/weather behavior.

Important implementation truth before testing:
- CP36 is ambient resident micro-life/props/gestures.
- CP38 is ambient NPC-to-NPC conversation.
- CP39 is the named-NPC memory **foundation**; memory-aware bounded dialogue was completed later in CP44.
- CP49 is the LivingWorldDirector/micro-event runtime.
- CP51 provides chapter-specific sun/skylight/fog profiles; final rain/snow VFX are still listed as open.
- CP53 adds continuous regional baseline populations.
- A true day/night cycle is not currently proven by the repository and must not be marked working unless observed/implemented.

Formal rights-holder outreach is deferred. Future asset effort, after the baseline audit, should go to visible quality and performance-safe materials rather than outreach.

Ideas discovered during this freeze belong in `Docs/WORLD_DETAIL_LEDGER.md`; do not implement them until the current baseline audit is complete.

## Current bulk-resource status — CP54

The repository now contains a much larger project-owned production bank instead of waiting for external acquisition. CP54 adds 75 new regional/common OBJ meshes, 17 procedural BMP textures, regional MTL palettes and runtime placement across all P1C01-P1C08 world builders.

Machine-readable authority:
- `Data/WorldResourceBankCP54.json`

Validation boundary:
- source bank: implemented on `mega/activity-movement-v1`,
- PG-054: pending CI,
- UE4.27 compile/import: pending CI,
- headless startup: pending CI,
- PIE/device visual and performance acceptance: pending.

## Current mass-content production status — CP50

The project is now in a comprehensive visible-content phase. Backend foundations remain implemented; active work is world density, materials, character animation production, interiors, lighting and audio.

CP50 adds a reusable common environment kit plus deterministic regional dressing across P1C03-P1C08. The intent is to move the game away from landmark-only prototypes and toward continuous readable environments without changing story topology.

Machine-readable visual-density authority:
- `Data/WorldDressingPlan.json`

Current proof boundary:
- source/runtime integration: implemented on the CP50 branch,
- Pre-Unreal / UE4.27 build-import: pending for CP50,
- PIE/device visual acceptance: pending.


## Current character-motion and atmosphere status — CP51

CP51 is the next visible-production layer after CP50. The runtime now has a safe skeletal-rig handoff contract for named characters plus richer procedural fallback motion, and P1C03-P1C08 have distinct bounded sun/sky/fog profiles.

Machine-readable authorities:
- `Data/CharacterMotionPlan.json`
- `Data/ChapterAtmospherePlan.json`

Current proof boundary:
- source/runtime integration: implemented on `mega/atmosphere-character-motion-v1`,
- Pre-Unreal validation: pending on the CP51 branch until CI completes,
- UE4.27 compile/import: pending,
- PIE/device visual acceptance: pending.

## Current mass-integration status — CP52

CP52 is intentionally larger than the previous incremental passes. The playable runtime now reuses the shared production resource family across the Shire, Bree and P1C03-P1C08, and the build rules explicitly package the living-world/production data needed outside the editor.

Machine-readable authority:
- `Data/ResourceIntegrationPlan.json`

Playable startup remains:
- route: `FrodoMain`,
- chapter: `P1C01`,
- first quest: `ShireArrival`,
- runtime world: `AChapterWorldRouter`,
- ambient runtime: `ALivingWorldDirector`.

External-resource truth boundary:
- the sourcing pipeline supports approved/licensed resources,
- `Data/ExternalAssetManifest.json` currently contains zero approved asset records,
- CP52 therefore uses all currently available project-owned production resources and does not fabricate external approvals.

Current proof boundary:
- source/runtime integration: implemented on `mega/resource-saturation-playable-v1`,
- Pre-Unreal PG-052: pending CI,
- real UE4.27 compile/import: now triggered on the CP52 pull request,
- headless playable boot smoke: now part of Unreal Build Validation and requires GameMode + P1C01/FrodoMain markers,
- PIE/device playability and performance: pending.
- runner autostart: post-reboot verification trigger issued on 2026-09-19.

## Current world-life status — CP53

The game has moved beyond isolated ambient encounters. CP53 keeps a chapter-specific baseline population alive around the player and layers denser micro-events on top of it, while reusing the existing schedule/social/awareness runtime and distance-based tick throttling.

Population targets:
- P1C01 Shire: 18
- P1C02 Bree: 16
- P1C03 Weathertop/Ford: 5
- P1C04 Rivendell: 12
- P1C05 Caradhras/road: 6
- P1C06 Moria: 0 civilians
- P1C07 Lothlorien: 10
- P1C08 Anduin/Amon Hen: 6

Machine-readable authority:
- `Data/WorldLifeSaturationPlan.json`

Current proof boundary:
- source/runtime integration: implemented on `mega/world-alive-saturation-v2`,
- Pre-Unreal PG-053: pending CI,
- real UE4.27 compile/import: pending CI,
- headless startup: pending CI,
- PIE/device crowd density and FPS acceptance: pending.
- resource flood: 15 new project-owned low-poly meshes are now source-controlled and runtime-wired across P1C01-P1C08.

# CURRENT PROJECT STATE

> **Operational recovery note — reconciled 2026-09-19**
>
> Current production baseline now includes CP44 backend completion, CP45 named-cast dedicated modular identities, CP46 threat production art, CP47 licensed asset sourcing, CP48 Weta/rights-holder/global resource mapping, and CP49 living-world/terrain engineering on its validation branch.
>
> The authoritative requirement/decision source is `Data/ProjectGovernor.json`. The machine-readable execution/dependency map is `Data/ProductionExecutionGraph.json`. Use `Docs/ENGINEERING_EXECUTION_PATH.md` for the human-readable implementation order.
>
> Older historical sections below are retained as evidence and may mention earlier heads/checkpoints. They must not be read as the latest status when they conflict with the Governor or this recovery note.


> **START HERE after a lost chat, a new developer handoff, or a long break.**
>
> This file is the operational snapshot of where the project is now.
> **Project-management authority lives only in `Data/ProjectGovernor.json`.**
> Story canon lives in `Docs/STORY_CANON_BIBLE.md`.
> Development rules live in `Docs/DEVELOPMENT_GATES.md`.
> Automated regression rules live in `Data/ProjectGuardRules.json`.
> World/chapter/checkpoint engineering lives in `Docs/WORLD_PRODUCTION_BLUEPRINT.md`.
> Machine-readable player checkpoint intent lives in `Data/WorldCheckpointPlan.csv`.

## Repository

- Repository: `4youbabee-tech/fellowship-personal-game`
- Active branch: `develop`
- Do not develop directly on `main`.
- Engine: Unreal Engine 4.27.2
- Target: Windows / DX11 / 720p / 30 FPS / Low-Medium
- Hardware floor: Intel i7 6th gen, 8 GB RAM, AMD GPU around 2 GB VRAM
- Local update/build/launch entry point: `SHIRE_UPDATE_BUILD_LAUNCH.bat`

Latest validated baseline before the current source-handoff governance maintenance:
- `e739ba6e364d0316cf5b7fe10c1f8ecaa13d417e` — `docs: sync CP30 handoff to validated head`
- Pre-Unreal Validation #113: **SUCCESS**.
- Unreal Build Validation #11: **SUCCESS** on the exact commit with UE4.27.2 C++ build and production asset import (`50 files, 0 failures`).
- CP30 world/checkpoint engineering is therefore STATIC-VALIDATED, COMPILE-TESTED and ASSET-IMPORT-TESTED. Dedicated automatic checkpoint/respawn runtime behavior remains planned, not implemented.
- The Shire visual content introduced at `8b0c13f...` still requires focused PIE/device review before VISUALLY-ACCEPTED.
- Intermediate CP30 commit `10ac91e...` had Pre-Unreal Validation #111 fail with `NameError: story_plan_ids is not defined`; `bd3d0be...` fixed that validator-order bug and restored both green gates.

Runtime-code baseline documented by this handoff:
`177f6cdbd073eaf0e2fd2c39da4a80fc82acf4ae`
(`world: add lightweight ambient NPC awareness`).

Documentation/guardian commits may naturally be newer than that runtime-code baseline.

## Validation vocabulary

Never say a feature is simply "ready". Record what was actually proven:

- **STATIC-VALIDATED**: GitHub Pre-Unreal Validation is green.
- **COMPILE-TESTED**: UE4.27.2 C++ build + UnrealHeaderTool succeeded.
- **ASSET-IMPORT-TESTED**: the UE4.27 production import commandlet completed successfully for the planned source assets.
- **PIE-TESTED**: relevant gameplay was exercised in Play In Editor.
- **DEVICE-TESTED**: relevant gameplay was exercised on the target laptop.
- **VISUALLY-ACCEPTED**: the user reviewed and accepted the visual/gameplay direction.

A green GitHub action is not a substitute for engine testing.

## Current proof level

Historically, an earlier project baseline:
- compiled and opened successfully in UE4.27.2,
- ran PIE,
- showed working movement, quest flow and HUD.

The current runtime-code baseline is now:
- **STATIC-VALIDATED** through Pre-Unreal Validation #80.
- **COMPILE-TESTED** on the target machine with UE4.27.2 after the PG-010/PG-011 fixes.
- **PIE-TESTED (BASIC BOOT ONLY)**: the Shire entered PIE successfully and rendered the current HUD.
- **DEVICE-TESTED (BASIC BOOT ONLY)** on the target laptop; full gameplay/performance acceptance is still pending.

Real UE4.27.2 validation history on 2026-09-18:
- Git update succeeded.
- UnrealHeaderTool completed successfully and generated reflection code.
- The first C++ build exposed:
  - C2660: one stale one-argument `MovePlayerToChapterStart` call.
  - C2440: direct base-to-derived light component pointer assignment from `GetLightComponent()`.
- Both source issues were fixed and converted into Project Guardian regression checks PG-010 and PG-011.
- A fresh build after those fixes completed successfully.
- Unreal Editor launched.
- PIE entered the Shire successfully.
- The HUD visibly showed:
  - `Frodo | P1C01_Main`
  - `An Unexpected Arrival`
  - `Reach the Shire lane and meet Gandalf.`

Additional PIE evidence on 2026-09-18:
- F5 Quick Save succeeded in PIE and displayed `Journey saved.`.
- UE4.27 emitted one runtime warning that the existing Directional Light had to be Movable before rotation.
- That warning was traced to `ConfigureMorningAtmosphere`, fixed by setting mobility before actor rotation, and recorded as Guardian regression PG-012.
- Quick Load (F9) is still pending verification.

CP22 milestone evidence on 2026-09-18:
- the enlarged Shire world-scale commit was pulled to the target laptop,
- UE4.27.2 Build completed successfully,
- no compile error was reported by the user,
- CP22 is therefore COMPILE-TESTED on the target laptop,
- the enlarged traversal itself still needs a focused PIE traversal/performance review.

CP23 milestone evidence on 2026-09-18:
- the living-world commits were pulled to the target laptop,
- UE4.27.2 launched into PIE successfully,
- the Shire rendered with Frodo / P1C01_Main, the opening objective and the enlarged world,
- The Mill landmark was visible,
- no compile/runtime error was reported for that launch,
- CP23 is therefore COMPILE-TESTED and BASIC PIE-TESTED on the target laptop.

Current post-CP23 source status:
- CP24A/CP24B voice/performance foundations, CP25 combat, CP26 biome/geography, CP27 runtime audio/proxy acting, CP28 production assets, CP29 self-hosted UE4 validation and CP30 world/checkpoint engineering are present in the current source.
- Current head `bd3d0be...` is STATIC-VALIDATED through Pre-Unreal Validation #112.
- Current head `bd3d0be...` is COMPILE-TESTED and ASSET-IMPORT-TESTED through Unreal Build Validation #10 on UE4.27.2 (`50 files, 0 failures`).
- The current head is NOT yet fully PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED.

The remaining hard gate is now the functional smoke-test layer: movement/interactions, F9 load round-trip, F8 route round-trip, chapter smoke tests and target-device performance/visual observation.

## Authoritative runtime chapter IDs

| Runtime ID | Chapter bucket |
| --- | --- |
| `P1C01` | Shire: Hobbiton, party, eastern fields, Black Rider road, ferry |
| `P1C02` | Bree |
| `P1C03` | Weathertop / Flight to the Ford |
| `P1C04` | Rivendell |
| `P1C05` | Fellowship road / camp / Caradhras / West Gate |
| `P1C06` | Moria: threshold, halls, Balin, Orc/Troll escalation, Balrog, bridge |
| `P1C07` | Lothlorien |
| `P1C08` | Anduin / Argonath / Amon Hen / Part I ending |

Do not reintroduce `P1C09`-`P1C12` as runtime chapter IDs.
Older planning used twelve narrative segments; those are now subregions/story segments inside eight runtime buckets.

## Current playable-route model

Main route:
- `RouteId = FrodoMain`
- episode convention: `P1C01_Main`, `P1C04_Main`, etc.
- playable character: Frodo

Parallel prototype:
- `RouteId = GandalfParallel`
- `EpisodeId = P1G01_Isengard`
- playable character: Gandalf
- region: Isengard / Orthanc

Per-route state is intended to preserve:
- quest stages,
- active quest,
- chapter,
- completed story beats,
- playable character,
- player transform.

A parallel route must not overwrite Frodo's main-route progress.

## Source-level handoff / architecture memory

The runtime module now has a code-local recovery entry point:
- `Source/ShireJourney/README.md` — start here when entering the runtime source tree.
- `Data/SourceArchitecturePlan.json` — machine-readable ownership/domain/target-path map for every runtime `.h`, `.cpp` and module `.cs` file.
- Project Guardian PG-019 requires the source handoff and architecture plan, and Pre-Unreal Validation rejects runtime source files that are missing from the manifest.

Current physical layout remains the guarded flat UE4.27 module. The planned maintenance layout is `Public/<Domain>` + `Private/<Domain>` with domains for Core, Characters, World, Subsystems, UI, SaveGame and Prototypes.

The physical folder migration has **not** happened yet. It must be a dedicated maintenance change, not mixed with gameplay, and must update includes plus static-validator path assumptions before a real UE4.27.2 build is accepted.

## Permanent user-requirement memory

The project no longer treats chat history as the authoritative record of user requests.

- `Data/ProjectGovernor.json` records persistent requirements with stable IDs, current status, evidence, missing work and acceptance criteria.
- `Docs/PROJECT_MEMORY_SYSTEM.md` defines how every meaningful future request must be captured and updated.
- `Docs/LIVING_WORLD_AI_BLUEPRINT.md` and `Data/LivingWorldFeaturePlan.json` preserve the user's living-world/NPC intelligence direction separately from current implementation status.
- Project Guardian validates the required memory artifacts and critical requirement/phase IDs.

Recovered/reaffirmed living-world intent is currently **PARTIAL/PLANNED**, not complete: ambient routines, awareness and social pauses exist, while full NPC-to-NPC dialogue, bounded dialogue creativity, persistent named-NPC memory/relationships and broader environmental micro-life remain future work.

## Project Governor / quality control

The project now has a deterministic internal control layer in addition to memory:

- `Data/ProjectGovernor.json` — the single authoritative source for requirements, priorities, conflicts, decisions, active gate and region quality states.
- `Scripts/project_governor.py` — CI validation of the single Governor.

This layer is specifically meant to stop silent requirement contradictions, false completion claims, inaccessible required routes, target-device performance regressions and acceptance of boring/frustrating sections without human pacing review.

It does not promise zero bugs. It enforces evidence and prevents known uncertainty from being hidden.

## Active visible-gameplay work: CP31-CP32 characters

The project has moved from governance-only preparation into visible character/gameplay production.

Current character state:
- Frodo and Gandalf have dedicated imported modular production meshes and the CP31 production-aware motion pass.
- Sam, Merry, Pippin and Bilbo use the imported Hobbit production archetype with character-specific color/proportion treatment.
- Aragorn/Strider, Boromir, Legolas, Gimli, Arwen, Elrond, Haldir, Galadriel, Saruman and other non-Hobbit named cast are runtime-present distinct procedural proxies; these are **not** final character art.
- `Data/CharacterPopulationPlan.json` is the implementation map for required cast presence by Part I chapter/route.
- Bree, Rivendell and Lothlorien now carry region-aware moving ambient populations rather than one Hobbit silhouette everywhere.

Next character-production work after compile/PIE proof is dedicated visual asset/rigging production in the order recorded by the population plan.

## Current architecture map

### Story / quest
`ShireQuestSubsystem.*`
- active quest and stages,
- current chapter,
- persistent one-time story beats,
- route / episode / playable-character state,
- per-route snapshots.

### Save
`ShireSaveGame.h`
- transform,
- quest/chapter state,
- completed story beats,
- route/episode/character,
- per-route progress.

### World routing
`ChapterWorldRouter.*`
- keeps one major generated region active at a time,
- removes previous generated prototype actors,
- builds current chapter,
- routes GandalfParallel to Isengard,
- restores route transform when appropriate.

### World builders
- `ShirePrototypeWorldBuilder.*`
- `BreePrototypeWorldBuilder.*`
- `FellowshipChapterWorldBuilder.*`
- `IsengardPrototypeWorldBuilder.*`

### Player / HUD
`ShirePlayerCharacter.*`
- movement / interaction / quick save-load,
- prototype appearance by playable character,
- temporary F8 route toggle,
- story-gated melee foundation for dangerous Part I chapters,
- persistent prototype health with a story-safe nonlethal floor until checkpoint/respawn UX is authored.

`ShireHUD.*`
- playable character / episode,
- active quest/objective,
- dialogue and alerts.

### Story presentation / dialogue / audio
- `ShireStoryPresentationSubsystem.*`
- `ShireDialogueSubsystem.*`
- `ShireAudioSubsystem.*`

The audio subsystem now resolves runtime ambience, music, SFX and voice assets by convention, keeps persistent ambience/music components, attaches world voice to matching actors, and ducks music during voiced dialogue.
Runtime voice playback now resolves `/Game/Audio/Voice/<Speaker>/<VO_ID>`, plays from the matching world actor when available, falls back to controlled 2D playback, and preserves subtitles when an asset is still missing.
`Data/VoiceCuePlan.csv` is statically synchronized with all runtime `VO_*` identifiers.
`Data/MusicCuePlan.csv` defines original music direction; final authored music and voice assets are not falsely claimed complete.

### Ambient life
`ShireAmbientNPC.*`
- walking/waiting routine,
- humanoid proxy movement,
- low-cost nearby-player awareness,
- look / cooldown / resume routine.

## Major work already present in current source

- Shire humanoid proxy pass.
- more Hobbiton paths, homes, fences, gardens, population and instanced foliage.
- optional Shire side stories.
- warm Shire morning presentation.
- deeper original Shire story dialogue.
- film-first story/canon bible.
- synchronized story/dialogue/music planning data.
- persistent multi-route story architecture.
- playable Gandalf/Isengard prototype route.
- Saruman / Orthanc / prison / industry / escape beats.
- deeper Rivendell social hub prototype.
- Fellowship camp / Boromir training / Crebain beat.
- Moria Watcher / Orc / Cave Troll / Balrog escalation.
- Lothlorien grief / Mirror material.
- Amon Hen Boromir pressure / defense / Fellowship break.
- lightweight ambient NPC awareness.
- CP21 Shire mega-pass source adds a mill/stream landmark, market detail, denser party preparation, crop rows, wooded-road cover, richer ferry geometry, more ambient residents/optional talkers and Black Rider last-known-position investigation behavior.
- CP22 Shire world-scale source pass expands Bag End-to-Ferry travel from roughly 50m to roughly 260m, separates Hobbiton/fields/wooded road/ferry with occlusion hills, introduces continuous curved roads and exploration loops, redistributes story/side-story actors to the larger geography, expands instanced ground cover and adds distance-adaptive ambient-NPC tick rates for the low-spec target.
- CP23 living-world source pass adds story-reactive atmosphere, reusable story-aware dialogue variants, persisted landmark discoveries, lightweight NPC-to-NPC social pauses near the player, running-sensitive Black Rider detection, and extra route/playable-character repair for restored saves.

## Story/data source hierarchy

Use these for their proper role. **Management authority exists only in the Governor:**

1. `Data/ProjectGovernor.json` — **sole project-management authority** for requirements, priority, conflicts, active gate, execution lane and acceptance status.
2. `Docs/CURRENT_PROJECT_STATE.md` — operational handoff/implementation summary; it follows the Governor.
3. `Docs/PROJECT_MEMORY_SYSTEM.md` — request/decision preservation rules.
4. `Docs/WORLD_PRODUCTION_BLUEPRINT.md` — world/chapter/checkpoint engineering map.
5. `Docs/LIVING_WORLD_AI_BLUEPRINT.md` — living-world/NPC intelligence design reference.
6. `Data/LivingWorldFeaturePlan.json` — machine-readable living-world implementation detail.
7. `Docs/DEVELOPMENT_GATES.md` — process/acceptance rules subordinate to the Governor.
8. `Docs/PROJECT_GUARDIAN.md` — regression memory.
9. `Docs/STORY_CANON_BIBLE.md` — film-first canon/route vision.
10. `Docs/PART1_FELLOWSHIP_MASTERPLAN.md` — Part I production plan.
11. Story/dialogue/music/biome/checkpoint data — authored detail contracts.
12. Runtime C++ — actual implementation behavior.

If a supporting document disagrees with the Governor on management state, reconcile it in the same change. Do not invent acceptance evidence.

## Canon/content rules

- Peter Jackson film continuity is the primary Part I story spine.
- Extended Edition detail may enrich the game when it does not contradict the core route.
- Tolkien lore may enrich the world but must not silently replace film continuity.
- Side content may fill believable gaps but must not change required story outcomes.
- New dialogue is original; do not copy screenplay dialogue.
- Music must be original in melody/rhythm/theme; film music is only broad emotional reference.
- Frodo is the Ring-bearer main line, but the wider story is ensemble-based.
- Parallel playable routes require a clear canonical/story reason.

## Scope rule

Part II and Part III remain roadmap/design work until the current Part I production gate is healthy.

Do not stack another large feature on a current head that has not passed the real UE4.27 compile + PIE + target-device smoke test.

Active production order:
1. validate current head,
2. stabilize the Shire as the vertical slice,
3. continue chapter-by-chapter,
4. keep the trilogy documented without destabilizing the active build.

## Exact next hard gate

The Public/Private/root-correction loop is closed machine-wise on CP-W00-154 and is not an active cleanup lane unless a concrete regression appears.

1. Validate packaged runtime Data JSON staging/read execution.
2. Validate actual authored audio-bank presence/playback without `-NoSound`; missing authored assets remain an explicit production blocker, not a fake pass.
3. Run target-device DX11 / 720p / Low-Medium profiling and record FPS, frame time, obvious hitching, GC spikes, RAM/VRAM pressure and tick hotspots where measurable.
4. Collect chapter-specific human PIE traversal, onboarding/core-loop, pacing, visual readability, collision/movement and NPC-behavior observations.

W00 is closed and the Governor has released the production freeze. W01/P1C01 is the active runtime lane; missing device/human evidence still blocks Gate 6/7 acceptance and later runtime chapters, not the current serialized P1C01 production car.

## Failure procedure

If any gate fails:
1. stop feature expansion,
2. save/copy the exact log,
3. fix the smallest failing layer,
4. push to `develop`,
5. require green static CI,
6. rerun UE build,
7. rerun the exact failed PIE step,
8. update this handoff if project state materially changed.

Local one-click build failure log:
`Saved/Logs/LastOneClickBuildFailure.txt`

## Recovery procedure if chat context is lost

A new developer/assistant should:
1. open this file first,
2. confirm repo and `develop`,
3. inspect latest `develop` commit and both validation workflows,
4. read `Data/ProjectGovernor.json` so no recorded user request is lost,
5. read `Data/ProjectGovernor.json`, then `Docs/PROJECT_MEMORY_SYSTEM.md` and `Docs/PROJECT_GOVERNOR.md`,
7. open `Source/ShireJourney/README.md` before changing runtime code,
8. inspect `Data/SourceArchitecturePlan.json` for ownership and planned file location,
9. read `Docs/LIVING_WORLD_AI_BLUEPRINT.md` and `Data/LivingWorldFeaturePlan.json` before NPC/world-life work,
10. read `Docs/DEVELOPMENT_GATES.md` and `Docs/PROJECT_GUARDIAN.md`,
11. read `Docs/STORY_CANON_BIBLE.md` before story changes,
12. inspect the relevant StoryBeat/Dialogue/Music/Biome/Checkpoint data files,
13. never claim engine testing without a real UE4.27 result,
14. resume from "Exact next hard gate".

## Temporary developer controls

- F5 — Quick Save
- F9 — Quick Load
- F6/F7 — previous/next chapter debug navigation
- F8 — temporary Frodo/Gandalf route toggle

These are developer controls, not final player-facing menu design.


## Character / voice completeness rule

Character quality is now governed by:
- `Docs/CHARACTER_PERFORMANCE_STANDARD.md`
- `Docs/PRODUCTION_COMPLETENESS_MATRIX.md`
- `Data/VoiceCuePlan.csv`

These files are required Project Guardian inputs.
They explicitly cover facial acting, gaze, blink behavior, lip-sync, voice, body language, locomotion,
interaction animation, environmental reaction, combat reaction, crowd behavior, continuity and low-spec LOD/performance.
Current proxy characters do not satisfy final character quality; final rigs/animations/voice assets remain future production work.
## 2026-09-30 - P1C01 overnight train checkpoint

PR #184 is already merged and supplies the current W00 packaged-runtime machine baseline: exact head `d6ca8aac03f5a1da07609e61e790ddf8faad8eed`, Pre-Unreal #1435 SUCCESS and Unreal Build #1108 SUCCESS through package/Data/runtime observation. Branch Cleanup #76 also succeeded.

PR #185 was closed without merge and superseded by the clean post-W00 consolidation path rather than wholesale-merging its 64-commit intermediate history. The live successor remains PR #189. Its parent exact head `66fd2c38aa5d6db815c4e6eaba957add89094b0d` had Pre-Unreal #1461 SUCCESS but Unreal Build #1134 was queued, so that head was not merge-eligible and no dependent runtime feature car was opened.

Allowed preparation work advanced instead: zero-silent-omission coverage was extended; source/QC and warehouse promotion boundaries were re-reviewed; static validators now require explicit disposition fields and preserve exact W00/per-car gates; and the save-schema audit recovered documented v3-v6 field evolution from reachable `develop` history while keeping v1/v2 explicitly unknown. No runtime C++ feature expansion was added by this checkpoint.

Acceptance truth remains narrow: machine proof may support STATIC/COMPILE/headless/package statements only where exact evidence exists. P1C01 PIE/device/visual/performance acceptance remains unclaimed.

## 2026-09-30 - P1C01 BAG_END_LIVED_IN_PASS hero runtime source implementation

- Predecessor SHIRE_WORLD_DENSITY is machine-green on PR #192 exact head `5a489781c23ed582f9203bd5c6df20d969fef467`: Pre-Unreal #1467 SUCCESS and Unreal Build #1140 SUCCESS; merged `develop@6abc675cacfe9c9b37a63420d72d0b1621b3b7c6` also passed #1468/#1141.
- Added `AShirePrototypeWorldBuilder::SpawnBagEndHeroPass()`: 3 zero-Tick/no-collision HISM clusters configured for 34 local instances (14 approach stones, 12 garden planters, 8 wood piles) plus 8 non-collision lived-in props.
- Added `ApplyBagEndStoryVariant()`: 5 Birthday props for `ShireArrival/LongExpectedParty` and 5 departure/packing props for `RingSecret/LeavingHome`. Existing ShireQuestSubsystem delegates drive visibility; no new Tick, global scan or Spawn/Destroy transition churn.
- P1C01 ambient population remains **18**. LivingWorldDirector, ShireNPCContextSubsystem and ShireQuestSubsystem ownership is unchanged.
- Existing quest/story anchors and locked F1-01/F1-02 outcomes are unchanged.
- Dedicated Bag End interior remains **CONTENT_PENDING** because the repository has no approved production interior FBX kit/shell.
- Current status: **SOURCE-IMPLEMENTED / EXACT-HEAD PRE-UNREAL + UE4.27.2 PROOF PENDING**.
- Not claimed: PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED, PACING-ACCEPTED or PERFORMANCE-ACCEPTED.

## 2026-09-30 - P1C01 PARTY_AND_SOCIAL_LOOP source implementation

- Predecessor BAG_END_LIVED_IN_PASS is exact-head machine-green: PR #193 head `45ea51bc64609d2781a4bb5bdbbdbdef3c9094a1` passed Pre-Unreal #1469 and Unreal Build #1142, then merged as `488159e0eeb2f2c6ee892ef4018da8f60d117744`.
- Implemented `SpawnPartySocialLoopPass()`: 4 zero-Tick/no-collision HISM clusters configured for 48 decorative instances, plus 14 authored non-collision party props.
- Added 4 setup-state props and 4 celebration-state props. `ApplyPartyStoryVariant()` reads existing ShireQuestSubsystem story beats: setup before `PartyArrival`, celebration after `PartyArrival`, both hidden after `BilboDisappearance`.
- Birthday setup gameplay adds three bounded optional beats: decorations, food stores, guest readiness. All are blocked after `PartyArrival`.
- Added two source-backed multi-step activities through existing `AShireTraversalChallenge`: `SHIRE_FIREWORKS_SAFETY` (timing) and `SHIRE_DRAGON_FIREWORK_MISHAP` (stealth-lite/fixed optional outcome). Both are available only from `PartyArrival` until `BilboDisappearance`.
- `ConfigureActivityChallenge` now accepts an optional completion story beat while remaining backward-compatible with existing callers; no new gameplay subsystem was introduced.
- Both activities are registered in `ContextualSideActivityPlan` and `JourneyDiscoveryRewardPlan`, preserving first-time reward / anti-farm / save semantics and canon-safe flags.
- P1C01 ambient population remains **18**; no crowd-cap increase, per-frame scan, synchronous heavy load or transition Spawn/Destroy churn was added.
- Locked F1-01 outcome remains unchanged: Bilbo leaves and the Ring passes to Frodo.
- Current status: **SOURCE-IMPLEMENTED / EXACT-HEAD PRE-UNREAL + UE4.27.2 PROOF PENDING**.
- Not claimed: PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED, PACING-ACCEPTED or PERFORMANCE-ACCEPTED.

## 2026-10-01 — Visual-quality/performance owner direction + Deep Audit V1

- Owner direction is now explicit: the target profile is **Balanced Medium with selective High treatment for visually important content**, not a blanket low-quality presentation. The 30 FPS / DX11 / 720p / 8 GB RAM / ~2 GB VRAM target remains unchanged.
- Perceived quality is protected first for hero characters, nearby architecture, terrain readability, key materials and primary lighting. Performance savings should come first from lower-salience costs such as distant shadow range, far-detail density, nonessential effects, LOD/culling and measured residency budgets.
- Owner-supplied **SHIRE JOURNEY — PRE-MORTEM PERFORMANCE & ARCHITECTURE DEEP AUDIT V1** is adopted as an engineering validation checklist. It reported **0 confirmed defects** and **10 plausible risk surfaces (R-01..R-10)**; those risks are not treated as discovered bugs without source/runtime proof.
- The highest-priority compound test remains settlement entry under simultaneous streaming/residency, NPC activation, AI/animation/collision, first-use rendering and cleanup pressure.
- Existing architecture already mitigates several audit concerns through async soft-reference streaming, bounded population pooling, explicit residency plans and bounded save/load contracts; these must be measured before speculative rewrites.
- Evidence boundary: governance/source review only. No new PIE/device/visual/pacing/performance acceptance claim.

## 2026-10-01 - P1C01 Gate 6/7 + local visible-world tooling reconciled

- SAVE_LOAD_LONG_SESSION predecessor #200 is merged at `7ad697ed146e356dea9e591ccf61a8268138bc3b` after exact-head Unreal success.
- TARGET_DEVICE_PROFILE_AND_GATE67 fail-closed evidence tooling is reconciled onto current develop. The target remains DX11 / 1280x720 / 30 FPS floor / 8 GB RAM / ~2 GB VRAM, with the Governor's **Balanced Medium + selective High** visual-quality rule.
- Missing target-device route evidence or human visual/pacing review remains INCOMPLETE/NOT_ACCEPTED; no device/performance/visual acceptance is inferred from CI.
- Local visible-world bootstrap tooling is reconciled: it reuses `ShireProductionImport`, verifies generated `.uasset` output, and launches `/Engine/Maps/Entry` without permanently changing DefaultEngine startup maps.
- Evidence boundary: SOURCE/TOOLING + STATIC validation pending on this exact head. No new PIE/device/visual/pacing/performance acceptance claim.

## 2026-10-01 - P1C01 Gate 6/7 + local visible-world tooling reconciled

- SAVE_LOAD_LONG_SESSION predecessor #200 is merged at `7ad697ed146e356dea9e591ccf61a8268138bc3b` after exact-head Unreal success.
- TARGET_DEVICE_PROFILE_AND_GATE67 fail-closed evidence tooling is reconciled onto current develop. The target remains DX11 / 1280x720 / 30 FPS floor / 8 GB RAM / ~2 GB VRAM, with the Governor's **Balanced Medium + selective High** visual-quality rule.
- Missing target-device route evidence or human visual/pacing review remains INCOMPLETE/NOT_ACCEPTED; no device/performance/visual acceptance is inferred from CI.
- Local visible-world bootstrap tooling is reconciled: it reuses `ShireProductionImport`, verifies generated `.uasset` output, and launches `/Engine/Maps/Entry` without permanently changing DefaultEngine startup maps.
- Evidence boundary: SOURCE/TOOLING reconciliation only on this branch. No new PIE/device/visual/pacing/performance acceptance claim.


## 2026-10-01 - Warehouse #307 hero-provider prerequisite root-fix candidate

- Warehouse #307 on `develop@2363d3f97d9158cd64a9e5f2f19b864092f69555` passed runner health, persistent inventory audit and critical-gap preparation. The critical-gap stage reported `verified=239`, `pending=0`, `manualQueue=0`.
- The actual failure occurred in the exact-head hero candidate report: character intake reported `prepared=0 pending=4 blocked=0`; the four pending rows were `QTN_UNIVERSAL_BASE_CHARACTERS`, `QTN_RPG_CHARACTERS`, `QTN_FANTASY_OUTFITS` and `QTN_UNIVERSAL_ANIMATION_LIBRARY`, each with `warehouse_source_not_staged_yet`. Frodo and Gandalf therefore each had `candidates=0`.
- Repair candidate adds a bounded four-pack Quaternius prerequisite manifest and stages it immediately before the Frodo/Gandalf candidate report. It does not refresh the full provider warehouse and does not promote any asset to runtime.
- Pre-Unreal now has a regression contract requiring exact pack parity with `authorized_source_packs`, FBX/CC0 boundaries, workflow triggering and provider staging before candidate ranking.
- Evidence boundary: **SOURCE-IMPLEMENTED repair candidate**. Fresh exact-head Pre-Unreal/Unreal proof and a subsequent develop Warehouse run are required. No PIE/device/visual/pacing/performance acceptance is claimed.


## 2026-10-01 - P1C02 Bree preproduction opened

- `Data/P1C02BreePreproductionV1.json` now opens the Bree / The Prancing Pony **source-preparation lane only**.
- The contract is bound to the existing F1-04 Bree/Weathertop mega source superpack and reuses persistent warehouse stock before any new acquisition.
- Canon/world anchors are sourced from the project Story, Characters, World and Mission bibles plus Tolkien Book One Chapters IX-X; no chapter-local outcome was invented where the source pack does not define one.
- Runtime remains fail-closed: `runtime_integration_allowed=false` until **P1C01 Gate 6/7 ACCEPTED** with real matching evidence.
- Current P1C01 blocker remains separate: Warehouse #308 staged the targeted Quaternius step but produced zero payload files and four unresolved source packs, so Frodo/Gandalf candidate coverage stayed at zero.
- Evidence boundary: **SOURCE-IMPLEMENTED preproduction contract**. No P1C02 PIE/device/visual/pacing/performance claim.


## 2026-10-01 - P1C03 Weathertop / Ford source preproduction opened

- `Data/P1C03WeathertopFordPreproductionV1.json` opens the **source/preproduction lane only** for P1C03.
- It reuses the existing F1-04 Bree/Weathertop mega source pipeline and references F1-05 only for a clean Rivendell handoff boundary.
- Source-backed Weathertop scope: ruined hilltop / ancient stone ring / exposed skyline, calm-approach + night-attack + wounded-departure state preparation, camp/terrain/ruin/weather/audio/encounter source QC.
- Source-backed Ford boundary: wounded eastward pursuit reaches the Ford of Bruinen before Rivendell recovery. No separate unsupported mission outcome is introduced.
- Runtime remains fail-closed: `runtime_integration_allowed=false` until **P1C02 Gate 6/7 ACCEPTED** with real evidence.
- Evidence boundary: **SOURCE-IMPLEMENTED preproduction contract** only; no P1C03 PIE/device/visual/pacing/performance acceptance.


## 2026-10-01 - Whole-game resource gap audit V2

- A whole-game source audit now cross-checks the 28-region production packets, culture/artifact requirements, battle/creature needs, gameplay interaction systems, the 3D Visual Asset Atlas and the Master External Resource Bible against current warehouse/source coverage.
- Strong coverage remains in generic PBR surfaces, support props, low-poly settlement/support kits, UI support and terrain/reference tooling.
- Highest-value remaining gaps are: hero humanoid bases, canonical creature rigs, professional humanoid/creature animation, realistic hero architecture, biome-specific vegetation, battle/siege stock, professional audio depth, battle/weather VFX, water/boat support, horse/mounted pipeline and culture-specific artifact/faction kits.
- `Data/WholeGameResourceGapAuditV2.json` records source lanes and acceptance boundaries for these gaps without opening any new runtime chapter.
- Provider policy correction: Warehouse #308 proved current Quaternius pack pages may be reachable while staging zero payload files. Quaternius is therefore no longer treated as a direct auto-stage provider; it is manual-clear-license unless a provider-supported direct payload URL exists.
- No new source count, download, candidate or web-discovery result is treated as READY_FOR_IMPORT, runtime integration or visual acceptance.


### Zero-payload provider guard implemented

- `Scripts/stage_quaternius_warehouse.ps1` now fails closed with `QUATERNIUS_WAREHOUSE_STAGE_ZERO_PAYLOAD_FAIL` when a run resolves only metadata/pages and produces zero payload files while unresolved packs remain.
- `Scripts/test_warehouse_provider_zero_payload_fail_closed.ps1` is wired into Pre-Unreal and verifies both the script guard and the Quaternius manual-access policy/registry classification.
- This prevents a repeat of Warehouse #308's false staging PASS and ensures downstream candidate gates cannot consume page-only evidence as asset availability.
- Evidence boundary: **SOURCE-IMPLEMENTED / exact-head validation pending** on this audit branch.

## 2026-10-01 - Warehouse #309 manual-provider continuation repair

- Exact merge `develop@8d138b93d1b3cf558f2f71e59354f0b6efd935b8` exposed the next real failure in Warehouse #309: the new fail-closed Quaternius guard correctly reported `files=0 unresolved=17`, but the generic support step stopped the job before persistent inventory audit, provider resolution, Frodo candidate reporting, or candidate-artifact creation.
- Root cause: the provider was reclassified to manual access, while both workflow call sites still treated the expected zero-payload/manual state as a terminal staging error.
- Repair candidate: `stage_quaternius_warehouse.ps1` retains exit code 3 by default, adds an explicit `-RecordManualQueue` mode that writes receipt state `MANUAL_QUEUE_REQUIRED` and never prints a staging PASS, and the two bounded workflow call sites opt into that mode.
- Unexpected failures remain fatal; no broad `continue-on-error` is used. The downstream exact-head Frodo report remains fail-closed when candidate coverage is zero, but it can now run and upload its blocker evidence.
- Poly Haven remains selective/reuse-first; #309 skipped its provider batch and no full refresh occurred.
- Evidence boundary: **SOURCE-IMPLEMENTED / exact-head validation pending**. No Quaternius payload, FBX candidate, import, runtime integration, PIE, device, visual, pacing or performance acceptance is claimed.


## 2026-10-02 - Warehouse #310 generated-worktree caller-checkout repair

- Post-merge `develop@e3563bb74a359e449398396b4ba52bddf26f5607` passed Pre-Unreal #1553 and Unreal Build #1205.
- Warehouse #310 preserved and hash-audited the persistent inventory: **18,925 payload files / 6,745,967,498 bytes / 239 active receipt records / 428 superseded / 0 duplicate groups**.
- Poly Haven and ambientCG were reuse-only: **219 + 8 receipt-verified files reused**, with no blind full refresh.
- P1C01 promotion prepared **36** items (**34** intake-QC, **3** pending, **2** manual) and exported **8** receipt-verified material sources.
- First real failure: material export removed the workflow-owned isolated source checkout while cleaning its generated worktree. The following Frodo provider step could not find `Scripts/stage_quaternius_warehouse.ps1`; candidate reporting and artifact upload never started.
- Repair candidate uses exact RUNNER_TEMP-bounded cleanup, rejects overlap with the caller checkout, prunes only worktree metadata, verifies the downstream script survived, and adds workflow/Pre-Unreal regression guards.
- Evidence boundary: **SOURCE-IMPLEMENTED / exact-head validation pending**. No Frodo FBX, import, PIE, device, visual, pacing, or performance acceptance is claimed.


## 2026-10-02 - Warehouse #311 exact Frodo blocker and direct CC0 fallback

- Post-merge `develop@0dd06344f6b839be5ef249933ebb18bf8e6c55bd`: Pre-Unreal #1556 and Unreal Build #1208 succeeded.
- Warehouse #311 proved the generated-worktree repair: both `P1C01_MATERIAL_SOURCE_CALLER_CHECKOUT_PASS` and `WAREHOUSE_SOURCE_CHECKOUT_SURVIVAL_PASS` appeared before the Frodo lane.
- Persistent inventory remained clean: **18,932 payload files / 6,808,598,106 bytes / 239 active / 428 superseded / 0 duplicates**. Poly Haven **219** and ambientCG **8** payloads were receipt-reused.
- Exact candidate artifact SHA256: `37b7a51113d8d3ddc750522e8f7c68ac6b277424f4bf4269108d82f4b82c1dc2`; local digest matched GitHub.
- True blocker: Quaternius manual queue contains four packs; candidate report contains **0 discovered FBX / 0 Frodo / 0 Gandalf / 4 pending / 0 blocked**.
- New bounded fallback candidate uses the direct OpenGameArt upload published by Quaternius under CC0: one 48.4 MB archive, ZIP safety budget, FBX-presence gate, receipt SHA256 reuse, and targeted redownload only when missing/mismatched.
- This source is a rig-base/QC candidate, not a final Frodo likeness. FBX 2018, skeleton, skin weights, deformation, retarget, import, runtime, PIE, device, visual and performance evidence remain required.


## 2026-10-02 - P1C01 hero candidate file-level provenance guard

- The hero intake now records a provenance row for every admitted FBX, binding candidate file path to provider, source asset ID, receipt, source payload and verified SHA256.
- The exact-head hero candidate wave fails closed before ranking when any discovered FBX lacks exactly one provenance row; ranked rows now carry the provenance fields into the evidence artifact.
- This closes the gap between `candidate_policy.require_provenance=true` and actual per-file candidate evidence without promoting any asset to READY_FOR_IMPORT.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD VALIDATION PENDING**. No skeleton, skin-weight, deformation, import, PIE, device, visual or performance acceptance is claimed.


## 2026-10-02 — P1C01 warehouse-first world expansion V1

- Registered a warehouse-first acquisition/build batch covering Bag End hero ring, Hobbiton village, Shire road corridor and Bucklebury/Ferry.
- Existing warehouse evidence is consumed before new acquisition; new lanes prioritize Poly Haven/ambientCG for PBR, licensed/manual hero character and motion sources, optimized vegetation, professional audio/VFX and terrain-reference tooling.
- Quaternius remains BLOCKED_MANUAL after prior zero-payload provider evidence; it cannot stop independent lanes and no undocumented archive URL may be fabricated.
- Animated production candidates remain FBX; production textures PNG/TGA with 1K/2K default; repeated world assets use HISM/ISM/LOD/culling; heavy runtime assets remain soft/async.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD STATIC VALIDATION PENDING**. No PIE/device/visual/performance acceptance claim.


## 2026-10-02 — P1C01 warehouse-first world expansion V1

- Added `Data/P1C01WarehouseWorldExpansionV1.json` and a hosted regression guard for a warehouse-first P1C01 asset/world expansion batch.
- The batch maps approved acquisition lanes to Bag End, Hobbiton, Shire roads and Bucklebury/Ferry while preserving FBX/PNG-TGA, provenance, HISM/ISM/LOD/culling and soft/async heavy-asset rules.
- Quaternius remains a manual provider blocker and does not block independent Poly Haven/ambientCG/licensed character-animation/audio/VFX lanes.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD STATIC VALIDATION PENDING**. No PIE/device/visual/performance acceptance claim.

## 2026-10-02 - Warehouse #312 Frodo candidate evidence and semantic QC repair

- Exact merged head `69c14d7ec08bf9c6b975966dfe016308ed0390a9`: Pre-Unreal #1558, Unreal Build #1210 and Warehouse #312 succeeded.
- Targeted OpenGameArt/Quaternius archive staged once: **48,430,012 bytes**, payload SHA256 `0295062cbc72da52ee804f39ac38694901a40458011f9b2638fc7ef13ed509da`, **52 FBX**.
- Persistent inventory remained clean: **18,933 payload files / 6,857,028,364 bytes / 240 active / 428 superseded / 0 duplicate groups**. Poly Haven 219 and ambientCG 8 payloads were receipt-reused.
- Candidate artifact `11198541662` ZIP SHA256 matched GitHub: `415c678706a6f258077fed877c45a155a016dea1092f0217a83042e03f2ec2fa`.
- Artifact review exposed semantic false positives: substring matching classified `Female` as `male` and `Soldier/Golden` as `old`.
- This repair changes ranking to exact filename tokens, bounds Frodo/Gandalf identity terms, adds regression examples, adds a Frodo-first static FBX header/Geometry/Model/LimbNode/Deformer/Skin/Cluster probe, and migrates PG-205 from the retired substring/state markers to the fail-closed V2 contract.
- Evidence boundary: **SOURCE-IMPLEMENTED / exact-head validation pending**. Static markers will not prove FBX 2018 export, UE4 skeletal import, deformation, final Frodo likeness, READY_FOR_IMPORT, runtime integration, PIE, device, visual or performance acceptance.



## 2026-10-02 - Warehouse #314 Frodo static-QC schema repair

- Exact develop head before repair: `de8bed40b94c3cd0d89f13ddbb260ba9df8449d5`.
- Pre-Unreal #1571 and Unreal Build #1223 succeeded on that head.
- Warehouse #314 reached the real Frodo lane with **52 staged FBX**, **5 Frodo candidates**, **4 Gandalf candidates**, and the Quaternius four-pack dependency recorded as manual queue rather than a factory-wide blocker.
- The candidate artifact itself is schema v2 and contains a valid `characters` array; the failing step was `Inspect Frodo FBX static structure`, where strict property access raised `property 'characters' cannot be found on this object`.
- Repair hardens candidate-report schema discovery, accepts the current v2 contract, retains a bounded legacy/flat-row compatibility path, and fails unsupported schemas with an explicit schema/key diagnostic.
- Regression coverage now executes the inspector against a generated schema-v2 fixture before Warehouse runtime use.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD VALIDATION PENDING**.
- No UE4 skeletal import, deformation, Frodo likeness, PIE, device, visual or performance acceptance is claimed.


## 2026-10-02 - P1C01 priority CC0 audio provenance refresh

- Ported the verified OpenGameArt priority-source metadata from the earlier draft onto current develop ancestry instead of merging a stale branch snapshot.
- Five P1C01 audio candidates now carry creator/uploader, primary-page verification timestamp, file label, CC0 page evidence, and an explicit provenance state.
- Boundary: source-page provenance only. Download receipt SHA256, audio QC, durable WAV-master conversion, UE import, playback/listening, device and performance acceptance remain pending.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD STATIC VALIDATION PENDING**.


## 2026-10-02 - Continuous Mega Wave Queue V2 registered

- Added `Data/ContinuousProductionWaveQueueV2.json` on current develop ancestry as the maximum-safe continuous production train.
- Capacity: **64 waves / 18,890 target work-items**.
- Composition: **12 P1C01 runtime waves + 12 global source waves + 23 trilogy chapter source/preproduction waves + 17 cross-cutting hardening waves**.
- The 23 chapter waves map directly to the production chapter IDs F1-01 through F3-07 from the project Mission/Story Bibles.
- Runtime remains fail-closed outside P1C01: every later chapter wave has `runtime_integration_allowed=false`; the queue cannot activate P1C02+ runtime by itself.
- Project Manager registration is embedded in the queue under `PMREQ_CONTINUOUS_MEGA_WAVE_QUEUE_V2_2026_10_02`.
- Performance/architecture boundary remains UE4.27.2 + DX11 + 1280x720 + 30 FPS floor, soft refs, async FStreamableManager, pooled crowds, ISM/HISM, FBX animated assets, PNG/TGA textures.
- Warehouse #315 on `develop@8c0f7b7da22e25ab723675d6d7a447d309c00bfe` succeeded and produced **5/5 Frodo static FBX structure passes** (FBX v7400, skeleton/skin/cluster markers present). This is **STATIC-VALIDATED** only; UE4 skeletal import, deformation and likeness remain pending.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD STATIC VALIDATION PENDING** for the new queue.

## 2026-10-02 - P1C01 visible-world mega source execution

- Opened a dedicated source/preparation branch from canonical develop to push the already-authorized M003-M007 visual stack while M001 Frodo skeletal validation remains serialized on PR #247.
- `Data/P1C01MegaChapterPackV1.json` is upgraded to schema v2 and now explicitly prioritizes four visible cells: Bag End hero ring, Hobbiton village, Shire road corridor and Bucklebury/Ferry.
- The pack continues to reuse the persistent warehouse before acquisition and keeps the existing promotion/material-export/character-intake machinery. It does not introduce a second runtime lane.
- Target constraints remain UE4.27.2 / DX11 / 720p / 30 FPS floor / 8 GB RAM / ~2 GB VRAM, FBX animated assets, PNG/TGA production textures, soft/async heavy runtime assets and ISM/HISM+LOD/culling for repeated detail.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD PRE-UNREAL PENDING**. No PIE/device/visual/performance acceptance claim.

## 2026-10-02 - Concrete visible-proxy inventory for the next P1C01 art pass

- Static source inspection of `ShirePrototypeWorldBuilder.cpp` confirms the world still retains Engine Cube/Sphere/Cylinder/Cone fallbacks when production meshes are unavailable.
- Added `Data/P1C01VisibleWorldProxyReplacementV1.json` to convert that observation into a concrete source-routing contract for Bag End, Hobbiton, Shire roads and Bucklebury/Ferry.
- The plan records existing production mesh identities separately from missing source needs, so later runtime work can remove a fallback only when a real imported replacement exists.
- A Pre-Unreal contract test now fails closed if the four visible cells, FBX/PNG-TGA rules, async-loading rule or HISM repeated-detail rule drift.
- Status: **STATIC-VALIDATED SOURCE CONTRACT PENDING EXACT-HEAD PRE-UNREAL**. No runtime/PIE/device/visual/performance acceptance claim.

## 2026-10-02 - Visible-world pack PG-187 repair

- Pre-Unreal #1599 reached the project-structure gate and failed only because the visible-world source branch changed the legacy mega-pack status token away from the PG-187 required value.
- Root fix keeps `status=RUNNER_EXECUTION_READY` and records the new intent separately as `execution_profile=VISIBLE_WORLD_PRIORITY_V2`; no guard is weakened.
- Status: **SOURCE-REPAIRED / FRESH EXACT-HEAD PRE-UNREAL PENDING**.

## 2026-10-02 - Visible-world reuse-first scan

- Deep scan found that several shapes still shown as primitive fallbacks already have imported production alternatives elsewhere in the project/import set.
- Reusable stock now explicitly routed before new acquisition: `SM_CommonRiverBoat`, `SM_CommonFootbridge`, rope post/coil, reeds, fallen log, broadleaf tree and boulder cluster.
- This materially reduces the true new-source gap for Bucklebury/Ferry and the wooded Shire road. New acquisition is now conditional on later visual failure of this existing stock, not the default.
- Status: **STATIC-VALIDATED SOURCE ROUTING / EXACT-HEAD PRE-UNREAL PENDING**.

## 2026-10-02 - Visible-world exact resident binding packet

- Added `Data/P1C01VisibleWorldReuseBindingPacketV1.json` on current develop ancestry.
- The packet converts the reuse-first scan into exact production object paths for Bucklebury/Ferry and the Shire road corridor, reducing unnecessary new-source acquisition.
- Ferry bindings cover river boat, footbridge, mooring post/rope, reeds and boulders. Road bindings cover fallen log, broadleaf tree, boulder, fence, wood pile and fern detail.
- Runtime remains unchanged by this source packet; P1C01 is still the only active runtime chapter.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD PRE-UNREAL PENDING**. No PIE/device/visual/performance acceptance claim.

## 2026-10-02 - P1C01 visible Ferry / Wooded Road runtime replacement pass

- Implemented a bounded P1C01 world-visual replacement using already-imported resident production meshes from the reuse-first packet.
- Wooded Road now prefers `SM_CommonFallenLog` for the prior cylinder+sphere obstacle and adds `SM_CommonBoulderCluster` support; the old primitives remain only as deterministic fallback when the production asset is not resident.
- Bucklebury/Ferry now prefers resident `SM_CommonFootbridge`, `SM_CommonRiverBoat`, `SM_CommonRopePost`, `SM_CommonRopeCoil`, `SM_CommonReedCluster` and `SM_CommonBoulderCluster` before the old cube/cylinder fallback shapes.
- No synchronous load was introduced: the builder still uses resident-only `FSoftObjectPath::ResolveObject`; chapter streaming ownership remains with the existing async streaming subsystem.
- Story/quest/NPC ownership is unchanged; no new Tick loop, crowd authority, Spawn/Destroy crowd churn or P1C02 runtime activation was introduced.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD UE4.27.2 BUILD + RUNTIME AUDIT PENDING**. No PIE/device/visual/performance acceptance claim.

## 2026-10-02 - UE4 self-hosted runner broker-stall root fix

- Live machine evidence showed `Runner.Listener.exe` alive with **no `Runner.Worker.exe`**, while Unreal jobs #1267/#1268/#1269 remained queued.
- Runner diagnostics showed broker transport failure (`SocketException 995`, aborted I/O) followed by a real log line in the form `[2026-10-02 15:19:29Z INFO BrokerMessageListener] Acknowledging runner request ...`.
- Root cause in `runner_watchdog.ps1`: `Get-RunnerTimestampUtc` only accepted the obsolete `[RUNNER yyyy-MM-dd HH:mm:ssZ ...]` prefix. Therefore `AckUtc` stayed null and the existing `ack-without-worker` recovery path never fired for the actual GitHub runner log format.
- Added `Scripts/runner_log_timestamp.ps1` supporting the real broker timestamp format while retaining the legacy parser, wired it into the watchdog, and updated the installer so the helper is copied into the supervisor directory.
- Added hosted regression `test_runner_watchdog_timestamp.ps1` and Pre-Unreal execution so this parser drift cannot silently disable stalled-acquire recovery again.
- Status: **SOURCE-IMPLEMENTED / HOSTED EXACT-HEAD VALIDATION PENDING / MACHINE WATCHDOG REINSTALL REQUIRED**. The queued Unreal jobs are not claimed recovered until the local supervisor is reinstalled/restarted and GitHub shows a job entering `in_progress`.

## 2026-10-02 - Runner recovery machine proof + transport-stall fail-safe

- Manual supervisor recycle on the UE4 machine produced concrete watchdog evidence:
  - `SHIRE_RUNNER_WATCHDOG_START root=D:\actions-runner`
  - `SHIRE_RUNNER_WATCHDOG_ONLINE pid=30020 brokerListening=true`
- GitHub then assigned queued Unreal work again: #1268 ran to a real C++ compile failure, and #1267 entered `in_progress`. This proves the queue stall was runner-broker acquisition related rather than a global GitHub Actions outage.
- The permanent source fix is stronger than the manual restart: the watchdog now parses real runner timestamps, tracks broker transport error vs later healthy evidence, and automatically recycles a listener that remains transport-failed for the configured bounded interval when no worker is active and github.com:443 is reachable.
- If github.com:443 itself is unreachable, the watchdog logs `SHIRE_RUNNER_WATCHDOG_NETWORK_BLOCKED` instead of restart-looping.
- Existing stale-worker and ack-without-worker recovery remain active; this change adds broker-transport-stall recovery rather than replacing them.
- Status: **MACHINE RECOVERY RUN-PROVEN FOR MANUAL RECYCLE / PERMANENT AUTO-RECOVERY SOURCE-IMPLEMENTED / FRESH EXACT-HEAD VALIDATION PENDING**.

## 2026-10-02 - Runner recovery static-contract reconciliation

- Exact-head Pre-Unreal #1627 passed the new timestamp/broker regression itself but stopped at legacy PG-145 because the marker `Acknowledging runner request` moved from `runner_watchdog.ps1` into the dedicated parser helper.
- PG-145 now validates the combined watchdog + timestamp-parser contract instead of requiring every marker to remain in one file.
- The new parser/test helper paths are also classified as runner-maintenance and ignored by the UE device lane in both push and PR path filters, preventing infrastructure-only edits from consuming the single UE4 runner.
- Status: **SOURCE-FIXED / FRESH EXACT-HEAD PRE-UNREAL PENDING**.

## 2026-10-02 - P1C01 Party Field primitive-overlay suppression

- Implemented the registered Party Field cleanup after the Ferry/Wooded Road runtime pass merged green.
- `SpawnVillage()` no longer leaves its large cube centerpiece underneath the later resident `SM_ShPicnicCanopy` production placement. The cube is now fallback-only when `ProductionPicnicCanopyMesh` is not resident.
- No story anchor, quest state, NPC ownership, collision contract, asset-loading policy or P1C02 runtime state changed.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD UE4.27.2 BUILD + RUNTIME AUDIT PENDING**. No PIE/device/visual/performance acceptance claim.

## 2026-10-02 - Party Field #1268 compile root fix

- Unreal Build #1268 reached the real UE4.27.2 C++ compiler and failed at `ShirePrototypeWorldBuilder.cpp(1191)` with `C2065: ProductionPicnicCanopyMesh: undeclared identifier`.
- Root cause: the Party Field fallback-suppression branch referenced a member that does not exist; the actual resident production canopy is `SM_CommonMarketCanopy`, previously resolved only as a local pointer inside the later Party social-detail pass.
- Added one shared resident pointer `ProductionCommonMarketCanopyMesh`, resolved in `BeginPlay()` through the existing resident-only soft-path resolver, and reused it both for the early primitive-fallback gate and the later Party social pass.
- No synchronous asset load was introduced and no story/quest/NPC authority changed.
- Status: **SOURCE-FIXED / FRESH EXACT-HEAD UE4.27.2 BUILD PENDING**. No PIE/device/visual/performance acceptance claim.

## 2026-10-02 - Maximum-safe CI lane reservation acceleration

- Implemented hosted-first Unreal classification so source/preproduction/static-only PRs can be classified on `windows-latest` before the single UE4.27 laptop is reserved.
- The self-hosted UE4 job now runs only for `full`, `core`, `asset` or `acceptance` modes; `inherit` source/admin work never enters the expensive device queue.
- Added explicit fast-lane coverage for East Fields source planning, KayKit/alternate hero source registration and whole-game chapter production packets, with regression cases in `test_unreal_classifier.ps1`.
- Preserved classifier outputs for package/reset/acceptance semantics so acceleration does not weaken exact-head engine gates.
- Status: **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD PRE-UNREAL PENDING**. No runtime, PIE, device, visual or performance acceptance claim.


### #1643 validator reconciliation

- Fresh Pre-Unreal #1643 proved the hosted classifier regression cases and PowerShell syntax, then failed only at PG-145B because the validator still searched for the retired self-hosted step name `Classify current delta for Unreal validation`.
- PG-145B remains fail-closed: `verify_runner_session.ps1` must still precede the first self-hosted post-checkout work step. The validator is updated to recognize the hosted-preflight handoff marker instead of weakening the health requirement.
- Status: **SOURCE-FIXED / FRESH EXACT-HEAD PRE-UNREAL PENDING**.

## 2026-10-02 - Hosted Unreal classifier exact-base diff fix

- East Fields refresh exposed a real acceleration defect: hosted classification used `fetch-depth: 2`, so multi-commit PR ancestry could not resolve the exact develop base and correctly fell back to `mode=full`.
- Hosted preflight now checks out full history (`fetch-depth: 0`) before classification, allowing exact base/head diff without reserving the UE4 laptop for source-only work.
- Pre-Unreal now guards this full-history + self-hosted-skip contract.
- Status: **SOURCE-FIXED / FRESH EXACT-HEAD PRE-UNREAL PENDING**. No runtime/PIE/device/visual/performance acceptance claim.

## 2026-10-02 - Hosted classifier local-history-first ancestor proof

- East Fields source-only run proved the UE laptop skip worked, but the hosted classifier still went red because the governance-ancestor proof performed an unnecessary private-repo `git fetch` after credentials had been scrubbed.
- The classifier now consumes the full local hosted history first and fetches only when ancestry is genuinely absent.
- This preserves `persist-credentials: false`, keeps the UE job skipped for source-only work, and retains fail-closed behavior when history really is unavailable.
- Status: **SOURCE-FIXED / FRESH EXACT-HEAD PRE-UNREAL PENDING**.

## 2026-10-02 - East Fields row replacement source plan

- Added `Data/P1C01EastFieldsRowReplacementV1.json` after deep scan identified twelve long cube strips still used as visible crop rows in the East Fields.
- Runtime work is predecessor-gated behind the current Party Field serialized runtime cleanup; this branch does not mutate runtime.
- Planned replacement uses one bounded zero-Tick/no-collision instanced cluster and existing resident production vegetation before any new asset acquisition.
- Status: **SOURCE-IMPLEMENTED / RUNTIME PREDECESSOR-GATED**. No PIE/device/visual/performance acceptance claim.

## 2026-10-02 - East Fields bounded HISM row runtime implementation

- Implemented the registered East Fields row replacement on top of the source-registration ancestry after Party Field #253 merged exact-head green.
- Added one dedicated `UHierarchicalInstancedStaticMeshComponent` owned by `AShirePrototypeWorldBuilder`; no Actor-per-row/per-plant spawning, no Tick and no collision.
- Production mode uses resident `ProductionGrassClumpMesh` with exactly 12 x 8 = 96 deterministic instances, cull band 900-6500 cm and no shadows; the twelve long cube strips remain fallback-only when the resident mesh is unavailable.
- Existing async/resident asset ownership, quest/NPC/LivingWorld authority and P1C02 gate remain unchanged.
- Status: **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD PRE-UNREAL + UE4.27.2 PENDING**. No PIE/device/visual/performance acceptance claim.

## 2026-10-02 - KayKit Adventurers alternate Frodo source family registration

- Registered immutable KayKit Adventurers revision `672074b73ba276876a19e8816ecdc5241817ab47` as a bounded alternate Frodo rig-base source family after the original five Quaternius candidates were technically rejected and the alternate Quaternius RPG ranked rows failed static skeletal structure.
- `KAYKIT_ADVENTURERS_CC0` is now admitted by the existing P1C01 character-intake and Frodo static-QC source allowlists.
- This branch is source/preparation only. It does not stage/import/promote a character by itself and does not authorize runtime replacement.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD STATIC VALIDATION PENDING**. No deformation, retarget, PIE, device, visual or performance acceptance claim.


## 2026-10-03 - KayKit Knight V2 bounded technical probe refresh

- Refreshed the second KayKit Adventurers technical rig-base probe on current `develop` ancestry using immutable revision `672074b73ba276876a19e8816ecdc5241817ab47`.
- Candidate is `Knight.fbx` only, recorded as `KAYKIT_ADVENTURERS_KNIGHT_CC0`, with source Git blob `101848795913dea0d37ac3ec9352fdf9dd024010`.
- This lane is deliberately source-only. It does not authorize Frodo likeness selection, runtime replacement, retarget, animation or chapter authority changes.
- Next gate remains staging receipt + static FBX QC; real UE4.27.2 skeletal import is allowed only after those gates pass.
- Status: **SOURCE-IMPLEMENTED / STATIC QC PENDING**. No UE import, PIE, device, visual or performance acceptance claim.


## 2026-10-03 - Branch lifecycle cleanup root fix

- Live audit confirmed the Actions branch filter mixes historical branch names with live refs; for example the exact #265 head was physically deleted by Branch Cleanup #137 even though its historical name can still appear in the Actions filter.
- A real hygiene gap also existed: Branch Cleanup executed only when a closed PR had `merged == true`. Closed-unmerged superseded PR heads and orphan refresh attempts with unique commits could therefore accumulate indefinitely.
- The cleanup workflow now runs on every PR close. It deletes the exact closed head only when the ref is non-canonical, not an active PR head, and its current remote SHA still equals the closed PR head SHA. A moved ref is preserved as new work.
- A verified stale batch is recorded in `Data/BranchCleanupPlan.json` for retirement after this maintenance merge; current open PR heads remain protected.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD HOSTED VALIDATION PENDING**. Repository hygiene only; no UE/PIE/device/visual claim.


### 2026-10-03 - Branch cleanup validation repair

- Pre-Unreal Validation #1671 **FAILED** at the PG-167 project-structure contract, not at PowerShell parsing. The failure correctly exposed that the validator still required the old `MERGED_HEAD_*` contract and that the workflow environment had not yet switched to `CLOSED_HEAD_*`.
- Repair on PR #268 updates the workflow environment, PG-167 validation contract, and the single Project Governor `REQ-EXEC-002` so closed-unmerged superseded PRs have an explicit salvage/disposition-before-delete lifecycle.
- The exact-SHA moved-ref guard, active-PR guard, canonical/protected refs and hosted-only administration boundary remain fail-closed.
- Status remains **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD PRE-UNREAL PENDING**. #1671 is failure evidence, not acceptance.

### 2026-10-03 - Per-branch active PR deletion guard

- Branch Cleanup #137 ended with `activePrHeads=0` even though PR #264 was already open, so global open-head discovery is not accepted as the sole deletion safety boundary.
- Every deletion path now performs a second, branch-specific GitHub API query for an open PR whose `head=owner:branch`. API failure is fatal; an active result blocks deletion.
- The guard applies both to exact closed-head deletion and explicit/zero-ahead cleanup through `Remove-RemoteBranch`.
- This is a safety hardening, not a cleanup-gate relaxation. Fresh exact-head validation remains pending.


## 2026-10-03 - Branch Cleanup #138 active-head batch fix

- Branch Cleanup #138 **FAILED** after correctly detecting `ops/actions-budget-isolation-v1` as an active PR head. The safety decision was correct, but `Remove-RemoteBranch` threw and aborted retirement of all unrelated stale refs.
- Repair changes active-PR handling from fatal exception to explicit `BRANCH_CLEANUP_KEEP_ACTIVE_PR` + continue. Canonical/protected/moved-ref guards remain fail-closed.
- Project Governor `REQ-EXEC-002` now requires active heads to be preserved without blocking unrelated stale cleanup.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD PRE-UNREAL PENDING**. #138 remains failure evidence only.


## 2026-10-03 - Branch Cleanup empty open-PR response repair

- Branch Cleanup #138 exposed a second safety-path bug: PowerShell wrapped an empty GitHub REST response as `@($null)`, yielding `Count=1` and falsely classifying dead refs as active.
- Fresh current-develop repair now filters null responses and requires an exact `head.ref == branch` match before a branch is considered active.
- API failures remain fatal/fail-closed. The already-merged KEEP + CONTINUE behavior for truly active PR heads remains intact.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD PRE-UNREAL PENDING**.


## 2026-10-03 - Stale branch retirement wave 2

Prepared a second governed cleanup wave while Branch Cleanup #140 processes the first batch. This wave adds only four refs with explicit dispositions:
- merged #268 maintenance head left behind by the earlier failed cleanup;
- closed audio provenance PR #241, explicitly superseded by merged #243;
- closed whole-game chapter packet PR #246, superseded as execution branch by current refresh #262;
- closed queued-mega-waves PR #239, explicitly superseded by merged #244 / ContinuousProductionWaveQueueV2.

This PR must not merge until the currently running cleanup finishes, so the cleanup concurrency group is not cancelled mid-batch.
Status: **SOURCE-IMPLEMENTED / HOSTED VALIDATION PENDING**.


## 2026-10-03 - Stale branch retirement wave 3

- Prepared final maintenance-only cleanup for three closed/superseded refs: PR #270, PR #272 and PR #273 heads.
- #270 is superseded by merged #271; #272 is superseded by merged #271 + #274; #273's optional fast-path was intentionally dropped after Branch Cleanup #140 and #141 both completed successfully under the current implementation.
- No active PR head or gameplay/runtime/source authority is included.
- Status: **SOURCE-IMPLEMENTED / HOSTED VALIDATION PENDING**.


## 2026-10-03 - Final stale maintenance retirement + active-queue compaction

Wave 3 now retires four live-but-dead refs: closed PR #270, closed PR #272, closed PR #273, and closed runtime PR #263. The #263 disposition is grounded in the current visible-world contract: hero round-door/window/trim support remains a source need and fallback removal is forbidden until exact replacement import/QC evidence exists.

The active `delete_after_merge` queue is compacted from 95 historical entries to these four live deletion targets. Historical dispositions remain preserved elsewhere in `BranchCleanupPlan.json`; absent refs are no longer re-queried on every cleanup run.

Status: **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD PRE-UNREAL PENDING**.


## 2026-10-03 - Final live-branch hygiene closeout

Live-ref audit after Branch Cleanup #142:
- total live refs: **15**;
- canonical/recovery refs: `develop`, `main`, `archive/pre-build-salvage-20260930`;
- open PR heads: **9**;
- unresolved unique-content refs without open PRs: **3**, now explicitly protected pending selective salvage.

The three pending-salvage refs are:
- `mega/p1c01-production-train-v1@793a57f8...`: contains P1C01 mega/visual packet files absent from develop;
- `prep/f2-03-edoras-mega-source-v1@46d2d26f...`: unique Edoras packet/regression content absent from develop;
- `prep/f2-03-edoras-mega-source-v2@d616be0c...`: independent later Edoras source lineage requiring selective reconciliation.

The active `delete_after_merge` execution queue is now cleared to zero because all reviewed dead refs have been physically retired. Historical dispositions remain recorded in audit sections.

Status: **SOURCE-IMPLEMENTED / FRESH PRE-UNREAL PENDING**. No gameplay acceptance claim.


## 2026-10-03 - Bag End planted-entry shrub replacement refreshed on current develop

- Single runtime writer refreshed from `develop@94ecdd6da09b4dbf9acc7ec7b99d18c696c64863`; stale PR #267 evidence is retained only as historical evidence for its old head.
- `SpawnHobbitHole()` now selects resident `ProductionShrubMesh` for the two planted-entry accents and retains `SphereMesh` only when that production mesh is unavailable.
- Existing transforms remain bounded to two actors. No new asset acquisition, synchronous heavy load, Tick, collision, NPC/story/quest/save authority, or P1C02 runtime activation is introduced.
- Hero round-door/window/trim and Bag End interior-shell debt remain content/import-QC gated and untouched.
- Status: **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD PRE-UNREAL + UE4.27.2 PENDING**. No PIE/device/visual/performance acceptance claim.

## 2026-10-03 - Hosted classifier local-tree proof + Bag End source packet

- Refreshes the stale #264 local-tree proof on current develop.
- Tree-equivalent proof now probes the already-present parent object before any credential-dependent fetch; network fetch remains a shallow-history fallback.
- Adds only `Data/P1C01BagEndHeroTrimSourceProbeV1.json` to the exact hosted-safe source-data allowlists; no `Data/` wildcard is introduced.
- Parent `82d5d9f8...` is tree-equivalent to the exact #277 candidate head `6e1b474e...` (compare shows one merge commit and zero file changes), whose Unreal Build Validation #1310 succeeded.
- Status: **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD HOSTED VALIDATION PENDING**. No gameplay/PIE/device/visual claim.

## 2026-10-03 - Transitive governance tree-equivalent proof

- Source-only PR #280 reached `governance-only-no-safe-green-ancestor-fail-safe` after #279 because the nearest safe engine-proven state is behind a merge commit (`82d5d9f8...`) with no workflow attached to the merge SHA itself.
- The merge tree is byte-equivalent to exact candidate `6e1b474e...`, which has Unreal Build Validation #1310 SUCCESS.
- `Test-NearestSafeGovernanceAncestorGreen` now accepts a safe ancestor only when the full intervening delta is governance/source-safe and the ancestor has either direct green Unreal evidence or existing exact tree-equivalent core proof.
- This does not broaden safe file classes and does not accept commit metadata similarity; tree equality remains mandatory.
- Status: **SOURCE-IMPLEMENTED / FRESH PRE-UNREAL PENDING**.

## 2026-10-03 - Bag End hero trim source probe V3

- Fresh source-only refresh from `develop@071a0ed2632c4919ed9160b817a965ed3b1eb76c` after hosted classifier transitive-tree proof #281 merged.
- Scope remains exact modular FBX discovery for the Bag End hero round-door/window/trim blocker; no runtime binding is allowed.
- Existing production facade and domestic props remain reusable, but no exact resident hero trim replacement is proven.
- Candidate families remain bounded to Kenney Building Kit, Kenney Modular Buildings, and Quaternius Medieval Village MegaKit.
- KayKit Medieval Hexagon remains rejected as an exact hero-trim family based on repository-tree inspection.
- Status: **SOURCE-IMPLEMENTED / EXACT FILE DISCOVERY + STATIC QC PENDING**. No staged file, UE import, PIE/device/visual claim.

## 2026-10-03 - Bag End hero trim exact-file discovery

- Kenney Building Kit now has exact independent FBX candidates for the visible Bag End blocker: round door leaves, round doorway wall/frame pieces, and round window pieces.
- Discovery mirror is pinned to `series-ai/jam-ready-assets@9cd5db46...` and is used only to discover filenames and Git-LFS payload SHA256 identities. It is not the license/provenance authority.
- Official Kenney remains the source authority; official receipt is still mandatory before static QC evidence can be promoted.
- Primary QC subset: `door-rotate-round-a.fbx`, `wall-doorway-round.fbx`, `wall-window-round-detailed.fbx`, plus `colormap.png`.
- The official archive should be staged whole because it is small, but UE import remains candidate-only.
- Status: **SOURCE-IMPLEMENTED / EXACT-FILE-DISCOVERED / OFFICIAL RECEIPT PENDING**. No static binary QC, UE import, runtime, PIE/device/visual claim.


## 2026-10-03 - Bag End hero trim official download URL resolved

- Official Kenney Building Kit page remains the provenance/license authority and reports 80 3D files under Creative Commons CC0.
- Its official download action resolves to `kenney_building-kit.zip`; the direct official URL is now recorded in `Data/P1C01BagEndHeroTrimSourceProbeV1.json`.
- Archive SHA256/size, extracted candidate hash match, static FBX QC and real UE4.27.2 import remain pending. No runtime fallback was removed.
- Status: **SOURCE-IMPLEMENTED / OFFICIAL RECEIPT HASH PENDING**. No PIE/device/visual/performance acceptance claim.


## 2026-10-03 - Local launch helper runner-root guard corrected

- `SHIRE_UPDATE_BUILD_LAUNCH.bat` no longer prints the retired `C:\\actions-runner\\_work` path as current authority.
- The interactive safety guard now rejects any project root under `\\actions-runner\\`, so both the persistent CI workspace and warehouse/runner subtrees remain unavailable for manual Unreal launches regardless of drive letter.
- The active runner authority remains `D:\\actions-runner`; interactive Unreal work remains in the Documents developer clone.
- Evidence boundary: **SOURCE-IMPLEMENTED** pending exact-head hosted validation. No PIE/device/visual/performance acceptance claim.


## 2026-10-03 - Safe reconciliation of stale open source/preproduction PR content

- Selectively salvaged current-useful, non-runtime content from stale open PRs instead of bulk-merging old ancestry: whole-game 23-chapter source packets/demand matrix, P1C01 Shire mega chapter pack, P1C01 180-slot visual production wave, and daily manager report generator/test.
- No stale branch-local Governor/state snapshots or old workflow bodies were copied wholesale. Current develop governance and current hosted Pre-Unreal architecture remain authoritative.
- Fresh current-ancestry Pre-Unreal coverage now executes the four salvaged contract tests directly.
- Runtime integration remains unchanged: P1C01 is still the sole runtime chapter; all salvaged whole-game chapter packets keep runtime_integration_allowed=false.
- Evidence boundary: **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD VALIDATION PENDING**. No PIE/device/visual/performance acceptance claim.


## 2026-10-03 - Static FBX world intake reconciled on latest develop

- Selectively ported the useful world/prop FBX intake delta from stale PR #237 onto current importer code; old branch ancestry and stale docs were not bulk-merged.
- Static FBX files outside `Characters/Rigs` are imported as UE4 static meshes with automatic animations/materials/textures disabled; `Characters/Rigs` FBX files remain deferred to the dedicated skeletal QC lane.
- Added a hosted source contract guard that forbids synchronous `LoadObject` in the static-FBX branch and checks the character deferral boundary.
- Existing legacy static OBJ handling remains untouched; animated/rigged production intake remains FBX-only.
- Status: **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD PRE-UNREAL + UE4.27.2 COMPILE PENDING**. No PIE/device/visual/performance acceptance claim.


## 2026-10-03 - P1C01 production garden proxy replacement

- The five authored Shire/Hobbiton garden patches now prefer the resident production ground mesh for soil rows and the resident production shrub mesh for plants.
- Production plants are emitted through the existing `ShrubInstances` HISM instead of 25 individual sphere actors per patch; across five patches this removes up to 125 primitive plant actors on the production path.
- Existing authored garden locations are unchanged. Cube/sphere treatment remains deterministic fallback only when the exact production mesh/HISM binding is unavailable.
- No quest/story/NPC authority changed. No new Tick, collision, synchronous heavy load, or runtime chapter activation was added.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD VALIDATION PENDING**. No PIE/device/visual/performance acceptance claim.


## 2026-10-03 - Owner-visible game delivery directive made durable

- Owner priority is now explicit repository authority: deliver a visibly real game first — natural Shire scenery and human-looking production characters — rather than accumulating backend-only progress.
- Programmer/external proposals remain advisory until checked against current `develop`, UE4.27.2, Project Sources and the i7/8 GB/~2 GB VRAM target.
- `VISIBLE SHIRE FIRST` and `FRODO FIRST REAL RIG` run in parallel source lanes, with exactly one runtime-changing P1C01 writer at a time.
- UE5 migration, MetaHuman Crowd, Nanite and UE5 PCG are not current production dependencies. UE4.27 HISM/ISM/foliage-compatible paths remain preferred.
- Every accepted direction, blocker and evidence boundary must be written back to repository memory; chat recall is never authoritative.


## 2026-10-03 - Frodo skeletal importer reconciled on current develop ancestry

- Restored the useful opt-in UE4.27 skeletal FBX import/QC capability from stale PR #257 onto current importer code without bulk-merging stale ancestry.
- Default production import still defers `Characters/Rigs` FBX. Skeletal import occurs only with explicit `-EnableCharacterRigImport`.
- The skeletal path uses AssetRegistry + in-memory `FindObject<USkeletalMesh>` for registration/bone proof and does not add synchronous runtime asset loading.
- Restored bounded direct-FBX warehouse staging so the exact KayKit Knight V2 probe can advance next.
- Status: **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD VALIDATION PENDING**. No deformation/retarget/AnimBP/runtime/PIE/device/visual acceptance claim.


## 2026-10-03 - Build-speed: dedicated source/probe PRs no longer reserve generic UE lane

- Generic Unreal validation now treats Bag End official-receipt source probes and Frodo dedicated technical-probe metadata/workflows as safe inherited deltas when the parent has green Unreal proof.
- Their dedicated workflows remain responsible for the real source/UE probe they own; the generic UE4 lane is no longer duplicated for the same PR.
- Runtime/C++/SourceAssets changes remain core/full and still reserve the UE4 runner.
- Evidence boundary: **SOURCE/CI IMPLEMENTED; hosted Pre-Unreal required before merge**.


## 2026-10-03 - Bag End hero trim official receipt completed

- Official Kenney Building Kit ZIP receipt completed on hosted CI: archive `1598905` bytes, SHA256 `2740ef5772fb5fb3d7aab881db22d129f6b68afe711b1a79e6d5e9e19cf3eec6`.
- Exact official extracted identities matched for `door-rotate-round-a.fbx`, `wall-doorway-round.fbx`, `wall-window-round-detailed.fbx` and the expected `colormap.png` payload.
- Evidence: `P1C01 Bag End Trim Official Receipt #7` SUCCESS on exact head `86c09549a67dec4f7083ca4ec18b03924d3f9f89`.
- Next gate is binary static FBX QC, then real UE4.27.2 import; runtime fallback removal remains blocked until those gates pass.


## 2026-10-03 - Bag End trim static FBX QC started

- Official door/frame/window payload hashes are already proven. A hosted static FBX QC now checks exact payloads for UE4-compatible FBX version plus Geometry/Model/UV/Material markers before any self-hosted UE import is scheduled.
- This keeps source rejection cheap and off the single UE4 runner.
- Status: **STATIC QC EXECUTION PENDING**; no UE import/runtime/visual claim.


## 2026-10-03 - Bag End Kenney trim candidate rejected before UE runner use

- Hosted static QC caught `door-rotate-round-a.fbx` as FBX **7700** with Geometry/Model/UV/Material markers present, but outside the project UE4.27-compatible accepted probe range (`<=7500`).
- The exact payload is therefore **REJECTED_STATIC_QC as-is** and is not sent to the self-hosted UE machine. This is the intended build-speed behavior: cheap hosted rejection before expensive UE validation.
- The hosted QC is being rerun to capture all three exact files in one durable report; then the hero-trim lane pivots to a compatible export/source family.


## 2026-10-03 - Next Frodo candidate family moved to hosted source inventory

- Registered a distinct CC0 OpenGameArt humanoid source (`Lowpoly Dummy Character`) after known Quaternius/KayKit/Kenney payloads were rejected.
- Hosted inventory downloads the public archive and records every FBX entry, exact SHA256, size, FBX version and skeletal/static markers before any UE4 machine time is spent.
- This candidate is a technical rig-base/deformation candidate only; it is not accepted as final Frodo likeness.
- Generic UE validation inherits green parent proof for this source-only lane; only a static-pass exact FBX is eligible for the dedicated UE4 skeletal probe.


## 2026-10-03 - Frodo technical rejection history reconciled after source-inventory merge

- Durable exact-payload rejection history is preserved on current `develop` ancestry so known-bad character assets are not retried after branch cleanup.
- Knight V2 exact payload `b25e35cc7eaaa3c7c103f10a4f41fde1cbd81936fede9aa9ae4efbd29d40ba1b` remains **REJECTED_TECHNICAL** after UE4.27 skeletal registration with **51 bones** because `MISSING_SMOOTHING_GROUPS` and `MISSING_BIND_POSE_BONES` were observed.
- Earlier rejected Quaternius/KayKit/Kenney payload hashes and reasons remain in `Data/P1C01FrodoTechnicalRejectionHistoryV1.json`.
- The distinct OpenGameArt Lowpoly Dummy source inventory has now landed separately; rejected-history preservation does not imply that candidate has passed UE4 import, deformation, retarget, AnimBP, runtime, PIE, device, visual, or performance gates.


## 2026-10-03 - P1C01 visible Shire mega runtime pass implemented

- Runtime construction now adds five bounded HISM lanes to the existing P1C01 world writer: production hedges, broadleaf woodland trees, rural fences, ferns and river reeds.
- Player-facing composition remains Bag End -> Hobbiton -> worked fields -> wooded road -> Ferry approach. Existing quest/story anchors are not moved.
- The pass targets roughly 487 repeated visible-world instances while avoiding hundreds of individual ticking actors: 148 hedge placements, 177 woodland/backdrop trees, 42 rural-fence placements, 72 ferns and 48 reeds when their already-resident production meshes are available.
- Explicit cull bands and shadow suppression bound the new repeated detail for the i7 Gen6 / 8 GB / ~2 GB VRAM target. Decorative woodland/fern/reed instances are non-colliding; route-shaping hedges/fences retain bounded collision.
- No NPC Spawn/Destroy lane was added. `ALivingWorldDirector` remains population/pooling owner and `UShireNPCContextSubsystem` remains NPC-context owner.
- Asset residency remains fail-soft: no synchronous heavy load and no new hard asset load path; optional detail is skipped when the production mesh is not resident.
- Machine status: **SOURCE-IMPLEMENTED / EXACT-HEAD VALIDATION PENDING**. No PIE/device/rendered visual/FPS acceptance claimed.


## 2026-10-03 - Frodo OGA Lowpoly Dummy rejected by real UE4.27 technical probe

- Exact source payload `00177d777d324e2eb807f5f94b573026c94226c6574267900213863a0dc8014d` (442604 bytes, FBX 7400) was staged from the verified CC0 archive and was not a previously rejected hash.
- Dedicated evidence: `P1C01 Frodo OGA Lowpoly Dummy UE4 Technical Probe #1` on exact head `ffaa3f6718a92b68f5112b040643846df277cd67`.
- UE4.27 registered the payload as a skeletal mesh with **41 bones**, but import emitted both `MISSING_SMOOTHING_GROUPS` and `MISSING_BIND_POSE_BONES`.
- Result: **REJECTED_TECHNICAL**. The exact payload is now added to the durable rejection history and must not consume UE runner time again.
- The transient probe FBX/uassets were cleaned by the workflow. No runtime Frodo promotion occurred.
- Next character action is a distinct licensed FBX/corrected export under the same technical gate; deformation/retarget/AnimBP remain blocked until a clean candidate passes.


## 2026-10-03 - Related stale branch retirement queued with Frodo probe closeout

- Three reviewed superseded refs are queued for post-merge deletion: the old Knight V2 rejection-history branch, the Knight V2 probe branch, and the obsolete Bag End official-receipt branch.
- Each has a durable successor on current `develop`; none is an active PR head.
- The older Frodo skeletal-import refresh branch and both Edoras preparation branches are **not** deleted because they still contain unique unsalvaged work. They remain explicit salvage targets rather than parallel execution trunks.
- This is repository hygiene only and carries no runtime/visual acceptance claim.


## 2026-10-03 - Maximum-safe P1C01 vertical-slice growth: natural route mega pass implemented

- The accepted scale-up strategy is being applied as **vertical-slice growth inside the active P1C01 chapter**, not by opening another runtime chapter: make one Shire route feel substantially larger, denser and more finished before asking the owner to reopen Unreal.
- `AShirePrototypeWorldBuilder` now extends the merged visible-Shire pass with a continuous natural-route layer from Bag End through Hobbiton, the worked fields, wooded road and Bucklebury Ferry.
- Source-level maximum when all already-resident production meshes are available: **up to 1,758 additional HISM instances** — 1,304 grass-verge clumps, 163 shoulder stones, 64 shrub pockets, 40 rock breakups, 51 terrain-bank instances, 72 vista trees and 64 river reeds.
- The pass deliberately breaks the long flat/test-strip read: route shoulders vary on both sides, terrain banks close the horizon, the worked fields stay broad, the wooded road becomes more enclosed, and the Ferry receives a denser river edge.
- All new repeated detail reuses existing HISM components and cull bands. No new synchronous heavy asset loading, no per-instance Tick, no NPC Spawn/Destroy lane and no new story/quest/save owner were added.
- This is intended as a **large player-visible change**, not another backend-only checkpoint.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD VALIDATION PENDING**. No PIE/device/rendered visual/FPS acceptance claimed.


## 2026-10-04 - Permanent professional Lead Game Architect operating method recorded

- The owner has made the delivery method itself a durable project requirement: professional senior-engineering judgment, continuous visible production, maximum practical quality and root-cause problem solving must survive programmer/agent changes.
- `Data/ProjectGovernor.json` now carries `lead_engineering_operating_policy_2026_10_04` as the persistent operating contract.
- Routine technical decisions no longer require owner interruption when they can be resolved inside canon, provenance, architecture, performance, gate and evidence constraints.
- Nontrivial blockers use an explicit evidence loop: live project/source evidence -> official UE4.27/Epic behavior -> mature open-source implementations/issues -> experienced developer practice -> compare viable remedies -> implement the strongest target-compatible root-cause fix.
- Asset rejection is no longer treated as proof that content is unavailable: broad legal/open-source discovery plus bounded candidate factories and lawful FBX normalization/re-export are the default when a source/export defect is repairable.
- Production batching is now explicit: prefer large coherent player-visible packets and one stable exact-head validation cycle over avoidable micro-commit/CI churn.
- Visible priority remains human/skeletal characters and a natural readable Shire: terrain silhouette, landmarks/architecture, roads/hedges/woodland/Ferry, vegetation/materials and lighting/presentation.
- Evidence discipline is unchanged: no PIE/device/visual/FPS acceptance is inferred from static/compile/CI evidence.

## 2026-10-04 - P1C01 authored Shire terrain/landmark mega wave B source implementation

- `AShirePrototypeWorldBuilder` remains the only P1C01 world-construction writer and now calls a dedicated `SpawnAuthoredShireLandmarkPass()` after the geography foundation and before Hobbiton architecture.
- The pass adds 52 bounded repeated placements using existing resident production meshes/HISM components only: 4 Bag End background earth masses, 8 Hobbiton settlement terraces, 6 worked-field outer ridges, 8 close wooded-road shoulders, 8 Ferry bank masses and 18 final-approach stones.
- The spatial intent is source-grounded: Bag End/Hobbiton gain hill/terrace integration; worked fields stay broad but stop reading as an infinite flat test plane; woodland becomes more enclosed; the Ferry gains stronger near/far bank silhouette while preserving the crossing corridor.
- No story/quest anchor, P1C02 runtime state, NPC lifecycle owner or crowd budget changes. No new synchronous load, per-instance Tick or actor-per-prop density lane was added.
- Imported production materials remain authoritative; the existing primitive-color path remains fallback-only.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD PRE-UNREAL + UE4.27 VALIDATION PENDING**. No PIE/device/rendered-visual/pacing/FPS acceptance is claimed.

## 2026-10-04 - P1C01 presentation composition wave C source implementation

- Existing production materials remain untouched and authoritative; no generic material override was added to imported meshes.
- A new `SpawnPresentationCompositionPass()` appends 120 bounded, non-colliding HISM instances after the natural-route pass: 28 cultivated foreground shrubs around Bag End/Hobbiton, 20 threshold trees at the wooded-road transition, 40 layered understory ferns and 32 Ferry-bank reed accents.
- Morning presentation defaults were refined in the existing low-cost path: slightly less orange direct light, softer/lighter distance fog, modestly stronger skylight, tighter exposure, and reduced bloom/vignette. Volumetric fog remains disabled and the water path still uses no planar reflection/scene capture.
- No new runtime material dependency, synchronous load, Tick, crowd owner or chapter expansion was introduced.
- Source resource review keeps CC0/open PBR sources such as Poly Haven/ambientCG as future intake options only if PIE review proves a real material gap; no external material was admitted by this code wave.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD VALIDATION PENDING**. No rendered visual, device or FPS acceptance is claimed.

## 2026-10-04 - Authored Shire B/C static regression guard

- `test_source_contracts.py` now reads `P1C01AuthoredShireMegaWaveBCV1.json` and locks the P1C01-only/single-writer boundary, 52-landform and 120-presentation budgets, HISM/resident-only/no-sync-load rules, and authored pass ordering inside `BuildPrototypeWorld()`.
- The guard explicitly rejects synchronous load calls, ambient/director spawning, and P1C02 tokens inside both new world passes.
- Status remains **SOURCE-IMPLEMENTED / HOSTED+UE4 EXACT-HEAD VALIDATION PENDING** until this branch is opened and run.

## 2026-10-04 - Hobbit facade material/overlay source correction

- Static source audit found `SM_ShHobbitFacade.obj` had five intended material switches (Earth -> Wood -> DoorGreen -> Wood -> Stone) written after the face list, so only the initial Earth material could own faces despite geometry already being cleanly separated into base, door frame, door, two window frames and two stone sill groups.
- The OBJ source now places each `usemtl` switch before its exact non-overlapping face range: 12 Earth faces, 48 Wood door-frame faces, 48 DoorGreen door faces, 96 Wood window-frame faces and 24 Stone sill faces.
- `SpawnHobbitHole()` no longer overlays duplicate primitive door/frame/window-frame/sill geometry when the production mound+facade are resident. Those structures remain deterministic fallback-only. Small warm-glass inserts, knob, chimney/step and planted-entry accents remain because the facade source does not provide those presentation details.
- This is a static-world asset/source correction only; no animated OBJ use was introduced. Exact-head hosted + UE4 import/build validation is still required before merge, and no rendered visual acceptance is claimed.

## 2026-10-04 - Authored Shire source-guard false-positive correction

- Pre-Unreal #1817 reached the new authored-Shire structural test and failed only because the guard rejected the literal word `P1C02` inside a source comment that explicitly stated the pass does not open P1C02.
- The guard now rejects the actual C++ chapter token `TEXT("P1C02")` inside the new runtime passes instead of prose comments. No runtime/world behavior changed and the P1C01-only contract remains fail-closed.
- Fresh exact-head Pre-Unreal remains required.

## 2026-10-04 - Hobbit facade material/overlay source correction

- Static source audit found `SM_ShHobbitFacade.obj` had five intended material switches (Earth -> Wood -> DoorGreen -> Wood -> Stone) written after the face list, so only the initial Earth material could own faces despite geometry already being cleanly separated into base, door frame, door, two window frames and two stone sill groups.
- The OBJ source now places each `usemtl` switch before its exact non-overlapping face range: 12 Earth faces, 48 Wood door-frame faces, 48 DoorGreen door faces, 96 Wood window-frame faces and 24 Stone sill faces.
- `SpawnHobbitHole()` no longer overlays duplicate primitive door/frame/window-frame/sill geometry when the production mound+facade are resident. Those structures remain deterministic fallback-only. Small warm-glass inserts, knob, chimney/step and planted-entry accents remain because the facade source does not provide those presentation details.
- This is a static-world asset/source correction only; no animated OBJ use was introduced. Exact-head hosted + UE4 import/build validation is still required before merge, and no rendered visual acceptance is claimed.

## 2026-10-04 - P1C01 KayKit rig technical bridge source implementation

- Registered a bounded technical bridge using the existing authorized CC0 KayKit Adventures GitHub source. This is pipeline evidence only, not final Frodo likeness.
- Added `P1C01KayKitRigTechnicalBridgeV1.json` with max-two candidate policy, exact direct GitHub archive/license URLs, FBX/PNG-only intake boundaries, unchanged UE4 bind/UV/smoothing/skeletal hard gates, and modular Frodo fallback.
- Added hosted staging/static-QC script `stage_p1c01_kaykit_rig_bridge.ps1`: downloads only the exact official archive/license, enforces archive and per-FBX byte caps, validates CC0 marker, rejects unsafe ZIP paths, records archive/license/payload SHA256, inspects FBX version + Geometry/Model/LimbNode/Skin/Cluster/animation markers, and selects at most two preferred candidates.
- Added `run_p1c01_kaykit_rig_bridge_ue4.ps1`: imports selected FBX payloads one at a time through the existing production importer, requires real skeletal registration/reference bones/generated mesh+skeleton, and rejects missing smoothing groups, invalid/missing bind pose, or missing UVs.
- Added exact-head workflow `p1c01-kaykit-rig-bridge.yml`: hosted source/static gate first, then one self-hosted UE4.27 editor build and serial candidate probes, with artifacts and transient cleanup.
- Runtime integration remains blocked. No deformation, AnimBP, PIE/device/rendered-visual/FPS acceptance is claimed.
- Status: **SOURCE-IMPLEMENTED / STATIC-VALIDATION + EXACT-HEAD UE4 PENDING**.

## 2026-10-04 - KayKit rig bridge hosted source-contract guard

- `test_source_contracts.py` now locks the KayKit bridge to P1C01, CC0/direct official GitHub URLs, FBX-only animated-character intake, max-two UE4 probes, modular Frodo fallback, no synchronous heavy runtime loading and no final-likeness claim.
- The guard also requires ZIP path/license/hash checks in hosted staging, all UE4 skeletal rejection tokens, exact-head workflow dependency ordering and artifact capture.
- Status remains **SOURCE-IMPLEMENTED / HOSTED + UE4 EXACT-HEAD VALIDATION PENDING**.

## 2026-10-04 - KayKit hosted ZIP path-filter root-cause correction

- KayKit Rig Technical Bridge run #1 failed before any FBX static/UE4 candidate judgment. The official archive downloaded, but the hosted ZIP selector returned `KAYKIT_RIG_NO_PREFERRED_FBX`.
- Root cause was path-leaf matching in the hosted staging script after path normalization. The selector now normalizes the full archive path to lowercase, splits the leaf explicitly on `/`, and matches only `*/characters/fbx/*` against the bounded preferred filename list.
- No KayKit FBX payload was rejected by run #1. Exact-head hosted/static + UE4 validation must rerun on the corrected head.
- Status remains **SOURCE-IMPLEMENTED / VALIDATION PENDING**; no deformation/runtime/PIE/device/visual/FPS acceptance is claimed.

## 2026-10-04 - KayKit hosted FBX discovery hardening

- KayKit bridge rerun #4 still failed before candidate QC with zero preferred FBX entries. No asset was judged.
- Hosted discovery is now decoupled from candidate ranking: the script first discovers every `.fbx` under any archive `/Characters/` path, then assigns preferred-name priority and falls back to the smallest static-pass character FBX only if a preferred name is absent.
- If character discovery is still empty, the script now emits up to 20 archive FBX paths before failing so the next root cause is evidence-based rather than inferred.
- Max-two UE4 probe budget and all technical rejection gates remain unchanged.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD RERUN PENDING**. No KayKit technical pass or runtime acceptance is claimed.

## 2026-10-04 - KayKit source-delivery root cause and direct-FBX correction

- Hosted bridge run #8 proved the official GitHub source ZIP contains no FBX entries. Repository `.gitattributes` is the direct cause: `Characters/fbx` and `Assets/fbx` are explicitly marked `export-ignore`, so GitHub source archives intentionally omit those folders.
- The bridge no longer depends on the source ZIP. It now downloads only two exact official raw FBX payloads from `raw.githubusercontent.com`: `Rogue.fbx` and `RogueHooded.fbx`, plus the exact official CC0 license snapshot.
- Hosted intake remains fail-closed: official raw-prefix allowlist, FBX-only candidate names, per-file byte cap, CC0 license marker, SHA256, FBX version and Geometry/Model/LimbNode/Skin/Cluster/animation static markers.
- The max-two UE4 probe budget and all real UE4 bind/UV/smoothing/skeletal gates are unchanged. Neither KayKit candidate has yet been judged by UE4.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD HOSTED+UE4 REVALIDATION PENDING**. No deformation/runtime/PIE/device/rendered-visual/FPS acceptance is claimed.

## 2026-10-04 - KayKit bridge exact rejection + anti-churn closeout packet

- Exact head `30b0392aa9abe5223d6adfe0958c93cd9cf28631` is **COMPILE-TESTED** by Pre-Unreal #1836 SUCCESS and Unreal Build #1433 SUCCESS.
- KayKit Rig Technical Bridge #13 completed hosted source/static staging and then produced real UE4.27 skeletal evidence for both bounded candidates: `Rogue.fbx` SHA256 `93a9ee0a67ae69b2d815050234acad2004c3b8af7d294b916e52609c8195eb71` -> 48 reference bones, REJECTED for MISSING_BIND_POSE_BONES + MISSING_SMOOTHING_GROUPS; `RogueHooded.fbx` SHA256 `4a773f074695c6c089cc6f059eed85da080928a4a4137af4e38b177139d4cc27` -> 48 reference bones, same rejection.
- The red workflow also exposed a secondary receipt-writer defect: direct-raw schema V2 has no `archive_sha256`, but the UE4 receipt writer still referenced that old archive field after candidate evaluation. This did not cause either candidate rejection.
- Anti-churn fix: both exact rejected hashes are now durable known rejections; hosted staging excludes them from `selected_candidates`. If the bounded source family contains only known rejected hashes, the hosted job records `STATIC_BRIDGE_EXHAUSTED_KNOWN_REJECTIONS` and the self-hosted UE4 job is skipped entirely.
- UE4 receipt generation now records direct-raw `delivery_mode`, `license_sha256`, and exact source payload hashes instead of the obsolete archive field.
- Modular Frodo remains the runtime fallback. No deformation, AnimBP, runtime promotion, PIE, device, rendered-visual or FPS acceptance is claimed.
- New anti-churn packet status: **SOURCE-IMPLEMENTED / EXACT-HEAD REVALIDATION PENDING**.
## 2026-10-04 - KayKit anti-churn regression-test indentation correction

- Pre-Unreal #1837 failed only while importing `test_source_contracts.py`: the earlier `test_p1c01_kaykit_rig_bridge_is_bounded_and_non_runtime` declaration was at module indentation while its body used class-method indentation; the newly added anti-churn method then exposed the mismatch.
- Root correction is limited to restoring that existing KayKit test declaration to the `SourceContractTests` class. No runtime, asset, workflow policy or technical gate behavior changed.
- Prior exact candidate evidence remains authoritative: Rogue and RogueHooded are both UE4.27 technical rejects with 48 bones and missing bind-pose/smoothing-group failures.
- Status: **TOOLING-FIXED / FRESH EXACT-HEAD PRE-UNREAL PENDING**. No PIE/device/visual/FPS acceptance.

## 2026-10-04 - P1C01 Visible Shire Mega Wave D source implementation

- Registered and implemented a new visible-first world pass `SpawnVisibleShireMegaWaveD()` inside the existing `AShirePrototypeWorldBuilder`; no second world writer or P1C02 runtime authority was introduced.
- The pass adds a bounded authored composition budget of **268 HISM instances + 12 limited Ferry hero actors** using resident production meshes only:
  - Bag End: 52 HISM instances for rear hill massing, garden hedge framing, cultivated shrubs and grass-framed approach.
  - Hobbiton: 48 HISM instances for settlement terraces, property hedges/fences and settlement trees.
  - Worked fields: 42 HISM edge instances to establish alternating hedge/fence boundaries and sparse working-edge vegetation while preserving open pastoral sightlines.
  - Wooded road: 64 HISM instances for canopy + fern understory enclosure while preserving the traversal corridor.
  - Bucklebury Ferry: 62 HISM instances plus 12 limited hero actors for river-bank massing, reeds, approach stones, landing, boat, rope posts/coils and four lamp posts.
- The pre-existing distant horizon tree line was also changed from regular 560-unit spacing to deterministic multi-frequency X/Y/scale offsets, specifically to remove the repeated test-strip silhouette without introducing non-deterministic placement.
- Runtime/performance boundaries remain unchanged: existing HISM/ISM components, explicit culling, no per-instance Tick, no synchronous heavy loading, no crowd/NPC ownership changes, and no actor-per-prop density wave.
- Canon/source basis remains the F1-02 Bag End/Shire and F1-03 Shire roads/Bucklebury visual spine; the Ferry treatment follows the source-supported well-kept approach / landing / reeds / broad river / steep opposite-bank read without opening Buckland runtime.
- Machine-readable budget contract: `Data/P1C01VisibleShireMegaWaveDV1.json`.
- Regression guard added to `test_source_contracts.py` for budgets, call order, single-writer boundaries, no sync loading and no P1C02 runtime tokens.
- Status: **SOURCE-IMPLEMENTED / STATIC-VALIDATION PENDING EXACT-HEAD PRE-UNREAL + UE4 BUILD**. No PIE/device/rendered-visual/FPS acceptance is claimed.


## 2026-10-04 - P1C01 Shire Visual Finish Wave source implementation

- Added SpawnShireVisualFinishWave() to the existing AShirePrototypeWorldBuilder after Visible Shire Mega Wave D and before generic density detail.
- Bounded visible budget: **212 HISM placements + 4 limited Ferry hero actors**, resident production meshes/components only.
- Terrain: 16 staggered route shoulders. Bag End: 40 hedge/shrub/grass. Hobbiton: 24 hedge/fence. Road/verge: 40 path-stone/grass. Woodland: 48 tree/fern. Ferry: 44 bank/reed + 4 lamp/path-marker hero actors.
- No duplicate writer, population ownership change, per-instance Tick, synchronous heavy load, or actor-per-prop density wave. P1C02 remains closed.
- Machine-readable contract: Data/P1C01ShireVisualFinishWaveV1.json; regression guard added to Scripts/test_source_contracts.py.
- Status: **SOURCE-IMPLEMENTED / STATIC-VALIDATION PENDING EXACT-HEAD PRE-UNREAL + UE4 BUILD**. No PIE/device/rendered-visual/FPS acceptance.


## 2026-10-04 - Human Character Production Wave 2 source factory

- KayKit anti-churn PR #310 merged at `develop@07bb5517ecbf4114520caececfa0fcbc535da8b3`; exact rejected KayKit hashes no longer reserve the UE4 skeletal runner.
- Wave 2 moves to a distinct CC0 human source/export family rather than retrying Quaternius/KayKit exporter lineage. The first bounded automated source is OpenGameArt Character Base Model by Overaction Game Studio, with source page + direct archive recorded in `P1C01HumanCharacterProductionWave2V1.json`.
- Hosted source factory accepts FBX directly or source `.blend` as an authoring intermediate, but emits only normalized FBX for the animated UE4 lane. Blender normalization records source/archive/payload SHA256, Blender version, FBX version, armature/mesh/bone counts, weighted/zero-weight vertices, UV-layer count, finite bounds and joint-name coverage.
- Max two normalized candidates can reach the self-hosted UE4 runner. Real UE4.27 gates remain unchanged: skeletal registration, reference bones, smoothing, bind pose, UV and generated skeletal mesh+skeleton assets.
- A clean technical winner advances immediately to reference-pose/root-scale/hierarchy + shoulder/elbow/knee + hands/feet deformation review and then Idle/Walk/Run retarget + AnimBP preparation. Runtime integration remains blocked and modular Frodo remains fallback.
- No synchronous heavy runtime loading was added. Final promotion remains soft-reference + FStreamableManager asynchronous loading only.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD HOSTED + UE4 VALIDATION PENDING**. No deformation/PIE/device/rendered-visual/FPS acceptance is claimed.

## 2026-10-04 - Human Wave 2 Rigify control-rig root fix / UE4 runner dedup

- Hosted Human Wave 2 run #1 succeeded on exact head `8afa53cdee648cef196b914c5123d3e38677fc2c` and captured source provenance before the self-hosted gate: archive SHA256 `a6837a6626b92776a358bc2a85c845af194b3ba2b4b2acc8531f107726cb0d9e`.
- Baseline Blender normalization exposed a production defect before UE4: the preferred `.blend` source exported 443 total bones with 1,787 weighted / 442 zero-weight vertices, while the direct-FBX path exported 656 bones with only 24 weighted / 2,205 zero-weight vertices. Artifact inspection shows Rigify `ORG-*`, `MCH-*` and `DEF-*` layers; candidate 1 contains 84 distinct DEF bone names versus hundreds of control/mechanism bones.
- Root fix: Blender export now uses `use_armature_deform_only=True`, keeps leaf bones disabled, preserves FACE smoothing/tangent-space/animation bake, records deform-bone count, and excludes control-rig layers except necessary hierarchy parents.
- Hosted admission now rejects candidates with zero deform bones or zero-weight ratio above 0.35 before they can reserve the UE4 runner. The pathological direct-FBX candidate therefore cannot consume an expensive probe.
- CI root fix: Human Wave 2 source/workflow/tooling paths are now an explicit dedicated lane. Generic Unreal validation returns `inherit` for a Wave2-only delta because the dedicated workflow already performs its own Editor build + UE4 skeletal probe; this removes the duplicate self-hosted build reservation.
- The superseded baseline UE4/generic runs may be cancelled by this new exact head; such cancellation is process supersession, not asset acceptance/rejection.
- Status: **SOURCE-IMPLEMENTED / HOSTED-BASELINE-EVIDENCED / FRESH EXACT-HEAD VALIDATION PENDING**. No UE4 technical winner, deformation acceptance, PIE/device/rendered-visual/FPS acceptance is claimed.


## 2026-10-04 - Human Wave 2 linked USkeleton probe correction

- Rebased the existing Human Wave 2 lane onto current `develop@3d0990bec48be182b291e266d321408c5d9ea034`; merged Shire world progress is preserved and P1C02 remains closed.
- Prior Wave2 run #2 established skeletal registration with 161 reference bones and no smoothing/bind-pose/UV hard-warning reasons, while the generated `SK_FRODO.uasset` mesh package existed. The previous rejection came from assuming a filename `SK_FRODO_Skeleton.uasset` rather than querying the mesh-linked skeleton object.
- `ShireProductionImportCommandlet` now records `skeletal-skeleton=yes/no` and `skeletal-skeleton-path=<object path>` from `USkeletalMesh::GetSkeleton()`.
- The Wave2 probe now requires skeletal registration, reference bones, generated skeletal mesh package, linked USkeleton, and unchanged smoothing/bind/UV gates. It no longer requires a guessed skeleton filename.
- PhysicsAsset presence is recorded separately as a sanity field; absence is not a hard skeletal-import rejection because current player collision remains capsule-owned.
- Status: **SOURCE-FIXED / FRESH EXACT-HEAD VALIDATION PENDING**. No deformation, retarget, PIE/device/rendered-visual/FPS acceptance is claimed.

## 2026-10-04 - Human Wave 2 technical winner

- Exact-head Human Wave 2 run #3 on `c0ad882792ccef8c9e639e4eb1d7c3e9e6ce5e90` completed SUCCESS.
- Technical winner: `eff0e79980f90d49deada0aa37ad8be5975a86330348e4ae6fa49d3171fad570`.
- UE4.27 evidence: `skeletal-registered=yes`, `skeletal-bones=161`, `skeletal-skeleton=yes`, linked path `/Game/Production/Characters/Rigs/FRODO/SK_FRODO_Skeleton.SK_FRODO_Skeleton`, and commandlet summary `377 files, 0 failures`.
- No smoothing-group, bind-pose, missing-bind-bone, UV, registration or linked-USkeleton rejection remained.
- PhysicsAsset auto-generation still emits the small-bone warning and remains a separate sanity gate; current movement collision is capsule-owned.
- CI hardening in the follow-up source packet adds the import commandlet to the dedicated Wave2 trigger and removes filename-based transient cleanup in favor of deleting only generated untracked Frodo `.uasset` files.
- Status: **TECHNICAL WINNER EVIDENCED / CI-HARDENING EXACT-HEAD VALIDATION PENDING**. Deformation, retarget, AnimBP, runtime, PIE/device/rendered-visual/FPS acceptance remains pending.


## 2026-10-04 - P1C01 Shire Settlement Completion Mega Packet

- Added `SpawnShireSettlementCompletionPass()` under the existing `AShirePrototypeWorldBuilder` authority.
- Visible budget: **345 new settlement instances** = 160 placements on existing native HISM components + 185 instances carried by bounded `AWorldDetailCluster` actors; no actor-per-prop density wave.
- Hobbiton/Hill: eight additional visual Bagshot Row smials, property hedges/fences, lane stones, verge grass, shrubs, flower boxes, benches, lamps, mailboxes, garden arches and wash lines.
- Party Field: retained the existing Party Tree/story destination and added a bounded completion layer of eight production picnic tables; no later-story state is inferred early.
- Village common / Bywater-facing edge: market stalls, produce stands, wells, carts, loaded carts, crates/barrels and signposts strengthen the lived-in settlement read without claiming an invented canonical inn placement.
- Working landscape: 12 orchard trees, orchard ladders, haystacks, ploughs and farm gates connect village properties to the surrounding Shire fields.
- Water/mill landmark: adds a bounded production mill-wheel accent while preserving the existing authored mill/bridge placement and traversal collision.
- All added repeated detail is non-colliding visual HISM/WorldDetailCluster data with explicit culling and no per-instance Tick. Existing resident production meshes are resolved only if already resident; no synchronous heavy load was added.
- P1C02 remains closed. Population/context/quest ownership is unchanged.
- Machine-readable contract: `Data/P1C01ShireSettlementCompletionV1.json`; source regression added to `Scripts/test_source_contracts.py`.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD VALIDATION PENDING**. This is not PIE-tested, device-tested, visually accepted, or an FPS acceptance claim.


## 2026-10-04 - P1C01 Shire Settlement Canon Finish B

- Settlement Completion predecessor #314 is **COMPILE-TESTED / MACHINE-GREEN / MERGED**: exact head `3ee80ffeaa03ee0acce131d098eb3f7967f36480`; Pre-Unreal #1849 SUCCESS; Unreal Build #1446 SUCCESS; merge `b3f31134e97d58362f486e09796eaf34852fe328`.
- Added `SpawnShireSettlementCanonFinishPass()` after the 345-instance settlement completion pass.
- Ivy Bush: bounded cottage landmark on the Bywater-facing road edge plus sign, benches and barrel yard; a new discovery identifies the Ivy Bush without reusing/misplacing the Green Dragon.
- Number 3 Bagshot Row: dedicated visual turf/facade/mailbox anchor near the existing Hamfast gameplay area; no quest coordinate moved.
- Party Field: ten visual step stones plus setup/celebration variants for the special entrance gate and cooking-stand/table/canopy open-air kitchen. A resident production material supplies a light gate treatment when resident; no synchronous load.
- Mill: bounded sacks/crates/barrels turn the landmark into a working yard.
- Bywater road: 12 low-cost visual trees (trunk+canopy clusters) frame the road transition while leaving the corridor open.
- Canon guard: Green Dragon remains a Bywater landmark; legacy discovery ID remains only for save compatibility with corrected visible copy.
- Added `Data/P1C01ShireSettlementCanonFinishBV1.json` and source-contract regression coverage.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD VALIDATION PENDING**. No PIE/device/human visual/FPS acceptance is claimed.


### Selective salvage from closed PR #315

- Closed unmerged PR #315 / head `be04e90053d997eee6085d8adc9b07d3e87baaf0` was inspected before disposition because its UE4 workflow was still occupying the self-hosted runner.
- Three unique visual reads were retained in Canon Finish B: Party Field hedge/grass boundary shell, Water/mill reeds + stepping-stone edge, and three bounded cottages on the Bywater-facing edge.
- Duplicate Bagshot Row homes, clutter, orchard/farm density, lamps/signs/mail/wash-line content were **not** reintroduced because #314/B already provide stronger or safer equivalents.
- Updated Canon Finish B maximum budget: 96 native HISM placements, 45 clustered instances, maximum 4 persistent landmark actors, 8 party-state actors; maximum visual budget 153.
- Status remains **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD VALIDATION REQUIRED** after this justified orphan-salvage head change.


## 2026-10-04 - P1C01 Shire settlement source-construction closure

- Settlement Completion PR #314 is **COMPILE-TESTED / MACHINE-GREEN / MERGED**: exact head `3ee80ffeaa03ee0acce131d098eb3f7967f36480`; Pre-Unreal #1849 SUCCESS; Unreal Build #1446 SUCCESS; merge `b3f31134e97d58362f486e09796eaf34852fe328`.
- Canon Finish B PR #318 is **COMPILE-TESTED / MACHINE-GREEN / MERGED**: exact head `c9b27bdefbe91ef123c28f8a70a5ce37bd6b5e96`; Pre-Unreal #1868 SUCCESS; Unreal Build #1465 SUCCESS; merge `437db07cc67d742dded52541d09d0ef849f6d286`.
- Source closure audit confirms authored representation for Bag End/Hill, Bagshot Row, Number 3 Gamgee anchor, Party Field/Party Tree/special entrance/open-air kitchen, village common, Ivy Bush, Water/mill/wheel/bridge, gardens/hedges/domestic life, orchard/working-field detail, Bywater-road avenue and a bounded Bywater-facing settlement edge.
- Green Dragon is not placed in Hobbiton. Existing legacy save/discovery identity remains compatibility-only with corrected visible copy.
- Architecture remains bounded: one world writer; repeated visual density through HISM/WorldDetailCluster; no per-instance Tick; no synchronous heavy load; no P1C02 runtime expansion.
- Machine-readable closure: `Data/P1C01ShireSettlementSourceClosureV1.json`.
- **Next required world gate is local visual bootstrap, not another blind density wave**: run `Scripts/bootstrap_local_p1c01_visuals.cmd` with UE4 closed, generate ignored `Content/Production`, and launch `/Engine/Maps/Entry` at DX11 1280x720.
- Status: **SOURCE CONSTRUCTION COMPLETE / STATIC+COMPILE MACHINE-GREEN / HUMAN VISUAL + DEVICE PERFORMANCE PENDING**. No PIE/device/visual/FPS acceptance is claimed.


## 2026-10-04 - Frodo targeted animation intake Wave 3

- Frodo technical winner remains `eff0e79980f90d49deada0aa37ad8be5975a86330348e4ae6fa49d3171fad570` with 161 UE4 reference bones and valid linked USkeleton; this wave does not reopen mesh hunting.
- Added one-pack warehouse manifest `Data/WarehouseQuaterniusAnimationBatchV1.json` for `QTN_UNIVERSAL_ANIMATION_LIBRARY` only.
- Warehouse classification gains `WH_STAGE_QUATERNIUS_ANIM`; this targeted path stages the one animation pack, runs character intake and inventory audit, but deliberately does **not** trigger the broad provider saturation/promotion/material trains.
- Required first clips remain Idle / Walk / Run. Successful staging only advances to clip inventory + retarget/deformation gates; it does not authorize AnimBP or runtime promotion.
- Existing `stage_quaternius_warehouse.ps1` is reused for license/public-download/SHA256 receipt behavior; no second downloader is introduced.
- Status: **SOURCE-IMPLEMENTED / TARGETED WAREHOUSE EXECUTION PENDING AFTER MERGE**. No animation, retarget, deformation, PIE/device/visual/FPS acceptance is claimed.


## 2026-10-04 - Frodo static deformation stress gate

- Extended the existing Human Wave 2 exact-head workflow rather than creating a second hero-source pipeline.
- After the self-hosted UE4 technical gate succeeds, a hosted Blender job downloads the **same exact normalized FBX artifact** and the UE4 technical-winner receipt from that run.
- Numerical stress covers bilateral upper arms/forearms/hands/thighs/shins/feet plus pelvis/spine/head hierarchy, then deterministic shoulder, elbow, knee, hand/foot and combined locomotion poses.
- Hard rejects cover missing joints, broken hierarchy, non-finite evaluated vertices/transforms, vertex-count changes and catastrophic bounds/displacement.
- This is a numerical deformation-readiness gate only. `visual_deformation_accepted=false`, `retarget_accepted=false`, and runtime integration remains blocked.
- Machine-readable gate: `Data/P1C01HumanDeformationGateV1.json`.
- Status: **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD HUMAN WAVE VALIDATION PENDING**.


### 2026-10-04 - Wave3 zero-payload guard root fix

- Exact-head Pre-Unreal #1872 failed only because the existing zero-payload regression encoded exactly two Quaternius `-RecordManualQueue` calls.
- Wave3 intentionally adds a third bounded/manual-safe call for `WarehouseQuaterniusAnimationBatchV1.json`.
- Root fix makes the regression semantic: it now requires exactly one manual-queue call for support, animation-only and hero-candidate manifests, while the broad `continue-on-error` prohibition and zero-payload fail-closed behavior remain unchanged.
- Status: **SOURCE-FIXED / FRESH EXACT-HEAD VALIDATION REQUIRED**. No animation/deformation/retarget acceptance is implied.


## 2026-10-04 - P1C01 definitive closeout wave opened

- Consolidation baseline is `develop@fd08c1c719f4b754384f03a10751dd748eacc74f`. One branch now owns the remaining P1C01 closeout work: `production/p1c01-definitive-chapter-closeout-2026-10-04`.
- We reviewed the actual PR #322 rendered artifact rather than guessing from source. Run `37207780989` produced six screenshots successfully; the workflow failed only after the six captures because its final PowerShell count expression received a literal cmd caret.
- Human visual result for those six renders is **REJECTED / NOT VISUALLY ACCEPTED**: blocky proxy player, flat/grey prototype read across much of the world, weak landmark framing/depth, and under-authored Ferry presentation.
- Separate evidence correction: merged PR #321 proves the UE4 technical skeletal winner (161 bones), but its hosted deformation-stress step did not execute successfully; the downloaded UE4 receipt was not at the assumed path and Blender raised `FileNotFoundError`. The workflow's overall green is therefore not deformation evidence. This wave will repair that handoff at the causal artifact-contract layer and rerun it.
- No P1C02 runtime work is opened. No blind density escalation is authorized before the material/lighting/ownership causes visible in the current render are addressed.


### 2026-10-04 - Definitive closeout implementation tranche A

Implemented on the single P1C01 closeout branch rather than opening additional subsystem branches:

- Render-capture finalizer root-fix: all six views were already generated by run 37207780989; the failure was the final cmd/PowerShell count pipeline. The finalizer now counts PNG files with a pipe-free PowerShell array expression and emits `P1C01_RENDER_CAPTURE_FINALIZER_PASS`.
- Frodo deformation evidence root-fix: UE4 evidence is staged into a stable single-root artifact, the hosted consumer verifies both receipts before Blender, Blender uses `--python-exit-code 17`, and the produced JSON must explicitly report `STATIC_DEFORMATION_STRESS_PASS`. This removes the prior false-green path where `FileNotFoundError` did not make the workflow fail.
- Party Field ownership/traversal: Settlement Completion no longer owns permanent picnic tables; `SpawnPartySocialLoopPass` is the sole event-furniture owner. A real collision opening is left in the hedge belt, with two visual gates and sixteen non-colliding approach stones.
- Village property fences: `PropertyFenceInstances` is now the authored-property HISM owner, independent from `RuralFenceInstances`, which is cleared/rebuilt by the later density pass.
- Garden soil: repeated production garden soil rows now use `GardenSoilInstances` HISM instead of actor-per-row production placement.
- Bounded final polish was selectively salvaged from the superseded exterior lineage: 44 native HISM + 54 clustered instances, <=6 cluster actors, zero hero actors and zero movable lights for mill/Water working-bank, Bagshot domestic detail and settlement lamp-mesh rhythm.
- Local Gate 6/7 acceptance route/harness from the former draft lane is integrated into this branch; acceptance flags remain false by default.
- Permanent no-patching/root-cause governance and definitive P1C01 closeout requirement are integrated into the same branch, including the corrected MasterExecutionRoadmap ownership required by PG-078.
- Branch retirement plan from the maintenance lane is integrated so obsolete P1C01 refs can be deleted after their supersession is recorded.

Current truth: **SOURCE-IMPLEMENTED / EXACT-HEAD VALIDATION PENDING / RENDERED VISUAL REVIEW REJECTED**. No PIE/device/performance/Gate 6/7 acceptance is claimed.


### 2026-10-04 - Shire grey/flat render root-cause repair implemented

- The prior six-shot artifact was not treated as a request for another blind density wave. Import logs prove the asset pipeline itself completed cleanly: **376 source files / 0 failures**, **161/161 albedo bindings**, and **229 tracked material packages / 0 missing**.
- Source inspection isolated a Shire presentation mismatch: the repeated terrain/woodland HISM layer uses shared Common meshes whose `Turf/Foliage/RiverMud/Bark` materials are flat-color and whose source OBJ files contain no authored UVs. The same Common bank is shared by other chapters, so it is intentionally **not** modified globally.
- P1C01 now applies component-level overrides from already-resident texture-backed Shire materials through `ResolveResidentMaterial`: Grass for hills/slopes/ground, Earth for river banks/garden soil, Bark+Leaves for repeated broadleaf woodland/ferns, Leaves for reeds, and Wood for village fence HISM. No synchronous load was added.
- A second causal defect was the visible chapter floor: one `SM_ShGroundBlock` with 0..1 UVs had been scaled to roughly **34,000 x 13,000 cm**, stretching one grass texture across most of the playable landscape. It is now represented by `GroundTileInstances`, a **34 x 13 = 442 instance HISM grid** at 1000 cm per tile. The existing hidden cube remains the only broad collision foundation; there is no actor-per-tile wave and no additional texture memory.
- Garden soil is now explicitly Earth-material HISM rather than inheriting the Grass material from `SM_ShGroundBlock`.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD REVALIDATION PENDING / PRIOR RENDER STILL REJECTED**. A fresh render must demonstrate whether this repair materially improves the world before any visual-acceptance label is allowed.


- Render-capture runner utilization root-fix: the P1C01 capture workflow now uses `cancel-in-progress: true` for its single capture concurrency group. A newer exact head invalidates an older capture result anyway, so stale capture builds must release the supervised UE4 runner instead of delaying the current chapter head. This policy is intentionally different from Branch Cleanup, where closed-PR events must remain serialized and non-cancelling.


### 2026-10-04 - Frodo deformation runner dependency root-fix

- Exact failing evidence from Human Character Production Wave 2 #15: Blender 4.0.2 failed inside the FBX importer with `ModuleNotFoundError: No module named 'numpy'`; the job correctly exited 17 and therefore did not produce deformation evidence.
- Root cause is the hosted deformation runner environment, not the Frodo candidate or UE4 import. The workflow now installs the explicit `python3-numpy` runtime dependency together with Blender and performs a Blender-internal NumPy preflight before importing the FBX.
- This does not promote deformation status by itself. The exact-head deformation job must rerun and emit `STATIC_DEFORMATION_STRESS_PASS` before merge.


### 2026-10-04 - P1C01 closeout branch lineage recovery

- The consolidated P1C01 closeout branch was briefly moved to current `develop` while reconciling the already-merged cleanup packet. The prior closeout head remained recoverable and the branch was restored to that reviewed lineage before further work.
- PR #328 cleanup state is being synchronized into this branch without dropping the 42 closeout commits.
- Evidence boundary is unchanged: this administrative lineage repair does not promote PIE/device/visual/performance/Gate 6/7 acceptance.

## 2026-10-04 - Light dead-ref cleanup wave

- Scope is deliberately small: six already-closed/superseded P1C01 working refs only.
- Queued refs: PR #317, #319, #322, #323, #324 and #326 heads.
- Active consolidated PR #327 is explicitly preserved, as are `develop`, `main`, the recovery archive and both Edoras prep refs.
- No production implementation, chapter scope, gameplay, asset, runtime or acceptance state is changed by this wave.


## 2026-10-04 - P1C01 two-mega-wave closure structure

- Owner-facing production structure is now locked to **two remaining mega waves** for P1C01, not many micro-waves.
- **P1C01-MW5 — Production Completion Mega Wave (ACTIVE):** Frodo/Gandalf production presentation, world/material/lighting/landmark completion, Living Shire, gameplay/traversal/collision/audio, save/load, localization-safe authoring foundation, and performance/streaming preparation.
- **P1C01-MW6 — Final Closure and Gate 6/7 Mega Wave (PENDING):** exact-head technical evidence, full PIE route, save/load roundtrip, human visual/pacing review, target-device 720p/DX11 30 FPS evidence, and final Gate 6/7 acceptance.
- A-I closeout lanes remain internal workstreams inside these two mega waves and must not become branch-per-lane churn.
- P1C02 Bree remains runtime-locked until P1C01 Gate 6/7 is accepted.
- Evidence boundary: planning/production structure only; no PIE/device/visual/performance acceptance is implied.


## 2026-10-04 - Continuous chapter train policy

- Owner command model: when the owner explicitly says to start a chapter, the Lead Game Architect continues that chapter through its registered production waves without requiring approval for routine technical decisions.
- Execution is large coherent packet -> exact-head validation -> root-cause repair if needed -> rerun failed gate -> continue, rather than owner-by-owner prompting or micro-branch churn.
- Routine progress is reported through the daily owner report / Slack instead of requiring continuous supervision.
- The train may autonomously reach READY_FOR_HUMAN_DEVICE_ACCEPTANCE, but Gate 6/7 cannot be claimed until chapter-specific human visual/pacing and target-device evidence exist.
- The next runtime chapter does not auto-open; after predecessor Gate 6/7 acceptance, wait for the owner's explicit start-next-chapter command.
- P1C01 remains the active train; continue MW5 then MW6. P1C02 remains locked.


## 2026-10-04 - Manual continuous chapter train + full P1C01 closure contract

- Hourly production scheduling is disabled. Production continues only when the owner explicitly says to continue/start; the owner may issue commands as often as desired (for example every 15 minutes).
- Each command resumes the active P1C01 train immediately from live GitHub state and continues routine engineering without micro-approval inside the current turn.
- P1C01 closure now explicitly requires the complete Shire experience: film-causal story spine, compatible source-backed depth, main quests, exploration/discoveries, optional routes, side activities/missions, named-character continuity, Living Shire, world/audio presentation, traversal/collision/navigation, save/load, localization-safe text, target-device performance, and human visual/pacing/enjoyment review.
- No meaningful supported chapter detail may be silently omitted: implement it or record an explicit disposition before closure.
- P1C02 remains locked until P1C01 Gate 6/7 is accepted with chapter-specific evidence.


## 2026-10-04 - Permanent manager continuity contract

- **ProjectGovernor is the persistent project manager/architect memory**, independent of any programmer/chat instance.
- Before meaningful work, the active worker must review Governor + CURRENT_PROJECT_STATE + PRODUCTION_COMPLETENESS_MATRIX + active chapter closeout + live GitHub gates.
- The manager owns reminder duty: localization, source/story completeness, exploration/side content, characters, Living World, audio, save/load, performance, human visual/pacing acceptance and documentation must be surfaced when relevant without waiting for the owner to remember them.
- Accepted unfinished obligations must live in repository governance/plans, not chat-only memory.
- When chat/context becomes long enough to risk omission, proactively warn the owner and prepare a complete handoff before further substantial work.
- Production remains **manual owner-command driven**; no hourly production schedule. The 24-hour owner status report remains separate.
- P1C01 remains the active chapter train; P1C02 stays locked until P1C01 Gate 6/7 evidence is accepted and the owner explicitly starts the next chapter.
- Evidence boundary: management continuity only; no runtime/visual/device/performance acceptance is implied.


## 2026-10-04 - Frodo deformation false-green root repair

- Prior Human Wave 3 artifact on `e76634d7154242e3e5a6e0dfcde3275afaa2802a` marked `STATIC_DEFORMATION_STRESS_PASS`, but every stress scenario recorded `max_vertex_displacement=0.0`.
- That artifact is **SUPERSEDED AS DEFORMATION PROOF**. It proves the workflow executed, not that the mesh deformed.
- Root cause: semantic joint selection could fall back to non-deform control bones, and the gate did not require weighted vertex influence or non-zero evaluated vertex motion.
- Fail-closed repair: required semantic joints must be deform bones, each must influence weighted vertices, and every pose scenario must exceed a scale-relative minimum displacement while retaining finite/bounds guards.
- Frodo remains a technical skeletal candidate. Retarget, AnimBP/runtime integration and human rendered deformation are **NOT ACCEPTED**.
- Exact-head repaired Human Wave rerun is required before any renewed deformation claim.


## 2026-10-04 - Human Wave #27 root-cause / no-repeat repair

- Exact head `77067204743927b64c8165358d59e1c4609f8dd9`: Pre-Unreal, Unreal Build and Shire Render Capture **SUCCESS**; Human Character Wave #27 failed only at hosted deformation.
- Exact failure: required Frodo semantic deform joints had zero weighted vertex influence. Binary FBX forensic inspection confirmed weighted skin clusters were confined to torso families; head/limb chains were unweighted.
- Root fix: normalized FBX now must pass hosted weighted-joint, Armature-link, hierarchy and non-zero pose-deformation checks **before** self-hosted UE4 is reserved. Zero survivors publish evidence and fail fast on hosted infrastructure.
- The rejected Character Base Model source is retired from the active probe; active bounded fallback is the direct public Quaternius CC0 Animated Characters Pack mirror on OpenGameArt.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD VALIDATION PENDING**. Retarget, AnimBP/runtime, PIE/device/visual/performance and Gate 6/7 remain not accepted.


## 2026-10-04 - Run #28 hosted source-factory root fix

- Human Wave run #28 on `6c8ab7b8f460d56ea3a6e442d3bf8dcbfccf22fb` failed on the hosted runner; both UE4 Human jobs were skipped, so the new frontload already prevented another 30-minute UE4 character waste.
- Exact cause: first fallback FBX had no UV layers. The inline Blender normalizer raised, but its invocation lacked `--python-exit-code`, so Blender returned success and the PowerShell stage failed later while reading a missing output FBX.
- Root fix: normalization now uses `--python-exit-code 18`; asset-quality failures are recorded per candidate and the hosted factory continues a bounded sweep of up to 12 candidates. Only up to 2 survivors may reserve UE4.
- Hosted outcome/evidence upload now runs with `if: always()` so failed source factories still leave evidence.
- Infrastructure/probe failures remain fail-closed; only candidate-quality failures continue.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD VALIDATION PENDING**.


## 2026-10-04 - Run #29 technical UV normalization + CI dedup

- Run #28/29 hosted evidence proved **12/12** bounded Quaternius fallback candidates were rejected before UE4 because the source pack has no UV layers. The self-hosted Human UE4 jobs were correctly skipped.
- This source is explicitly a **technical rig/deformation base**, not final Frodo likeness. Instead of weakening the UE4 UV gate, normalization now creates a deterministic Smart-UV layer only when a technical source has zero UVs. Final hero material/likeness/visual acceptance remains separately blocked and cannot inherit this technical UV.
- Generic Unreal validation previously compared every synchronize event against the PR base, so old runtime files kept forcing a full UE4 build even for human-CI-only commits. The workflow now prefers the previous PR head (`github.event.before`) and the classifier recognizes the complete dedicated Human Wave2 file set.
- Shire Render Capture now has a hosted visual-delta classifier. It may inherit only when the current delta has no visual-impact files **and** the previous head has a successful render workflow; otherwise it renders fail-safe.
- Goal: a Human pipeline iteration should spend hosted minutes first, reserve UE4 only for a surviving candidate, and avoid unrelated generic build/render reservations.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD VALIDATION PENDING**.


## 2026-10-04 - Run #30 armature export-selection root fix

- Human hosted run on `27db245d4136ee708afb2bb0e63b4a1108fc736f` tested 12 Quaternius candidates. All 12 had one armature, one mesh, generated technical UVs, and **100% weighted vertices before export**.
- All 12 then failed normalized-FBX deformation re-import with `ARMATURE_COUNT_NOT_ONE`.
- Root cause: Smart-UV generation changed Blender object selection; normalization later exported with `use_selection=True` without restoring the armature selection. This could produce mesh-only normalized FBX despite valid pre-export rig data.
- Root fix restores the exact armature + mesh selection and active armature immediately before FBX export. The deformation receipt now records armature/mesh counts and names.
- Render CI is also hardened to reuse the nearest successful ancestor only when the complete intervening **visual content** tree is unchanged; CI/control-file changes alone no longer require another self-hosted scene capture.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD REVALIDATION PENDING**.


## 2026-10-04 - Run #31 immutable KayKit source transition

- Quaternius is now closed as a Frodo rig-base family for this gate: after the export-selection repair, **12/12** hosted candidates retained a valid armature and full vertex weighting, but all failed the same required weighted semantic joints (`spine`, both `hand`, both `thigh`).
- The deformation gate is **not weakened**. Human Wave2 now targets **KayKit Character Pack: Adventurers** at immutable revision `672074b73ba276876a19e8816ecdc5241817ab47`.
- Provenance verification uses the immutable README for the CC0/rigged/animated marker while keeping the repository page as the human-readable source.
- Historical raw Rogue/Knight payload SHA256s remain forbidden as direct UE4 retries. The hosted factory may use them only as source inputs to create a **different normalized FBX SHA256**; a byte-identical derivative is hard-rejected before UE4.
- Candidate discovery is bounded to Rogue / RogueHooded / Knight names, hosted validation first, max 2 UE4 survivors, and runtime promotion remains blocked.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD HOSTED VALIDATION PENDING**.


## 2026-10-04 - Run #32 KayKit Git LFS intake repair

- Exact-head run `b8f336706e976b1cfc64285bda5c3bfcd3ab91a5` failed cheaply on hosted CI with `HUMAN_WAVE2_NO_CHARACTER_SOURCE`; **no UE4 Human reservation occurred**.
- Artifact inspection showed the immutable GitHub revision ZIP contains textures and GLB assets but omits the repository FBX/LFS character payloads. This was an intake-path mismatch, not a character deformation result.
- Human Wave2 now downloads the three immutable FBX endpoints directly: `Rogue.fbx`, `RogueHooded.fbx`, and `Knight.fbx`.
- Each raw download must match its already-recorded historical SHA256 exactly. Those raw bytes remain prohibited from direct UE4 retry; Blender must generate a **different normalized derivative SHA256** and that derivative must pass the unchanged hosted deformation gate before UE4 is allowed.
- Generic Unreal and Shire render self-hosted jobs were both skipped on this iteration by the CI dedup classifiers.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD DIRECT-FBX HOSTED VALIDATION PENDING**.


## 2026-10-04 - Run #33 KayKit upper-leg semantic resolver fix

- Exact-head hosted run `f613c0e11df8d948e7542ea4744cf219355bd8a3` successfully downloaded and SHA-verified all three immutable KayKit FBXs: Rogue, RogueHooded, Knight. Generic Unreal and Shire render self-hosted work were skipped.
- Normalized KayKit skeleton evidence is materially better than Quaternius: it contains weighted `spine`, `hand.l/r`, `upperarm`, `lowerarm`, `upperleg.l/r`, `lowerleg.l/r`, `foot.l/r`, `hips`, and `head`.
- Hosted rejection was a resolver defect: the required thigh semantic recognized `thigh` and `upleg`, but not the actual compact bone name `upperleg`.
- Root fix adds `upperleg` as an alias in **both** the hosted deformation preflight and the later Wave3 deformation gate. This does **not** weaken the requirement; left/right thigh still must exist, be deform bones, carry nonzero vertex influence, satisfy hierarchy, and move geometry under pose stress.
- Rogue already meets the existing zero-weight ratio ceiling (0.3366 <= 0.35); RogueHooded and Knight remain above that ceiling and therefore stay rejected unless their actual normalized payload independently meets the same threshold later.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD REVALIDATION PENDING**.


## 2026-10-04 - Run #34 UE4 T0 reference-pose remediation

- Exact-head `3dd5fe992910596895a93d9737a4c5521f8ac0e8` produced the first hosted KayKit winner: **Rogue** passed the hosted weighted-joint/deformation gate; RogueHooded and Knight remained rejected by the unchanged zero-weight ratio ceiling.
- UE4.27 then imported the normalized Rogue as a skeletal mesh with **48 reference bones**, a valid linked `USkeleton`, and the commandlet reported **377 files / 0 failures**.
- The candidate was still correctly rejected because UE4 emitted `MISSING_BIND_POSE_BONES`. The engine log explicitly recommends **Use T0 as ref pose** (or adding the bones to the bind pose).
- Root remediation is now implemented in the editor-only character-rig import path: `UFbxSkeletalMeshImportData::bUseT0AsRefPose = true`.
- This is **not a gate waiver**. The Human Wave script still rejects `MISSING_BIND_POSE_BONES` if it appears after re-import, and all existing smoothing/UV/skeleton/deformation requirements remain unchanged.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD UE4 REVALIDATION PENDING**.


## 2026-10-05 - Human-owned render deduplication

- Exact head `76d7609b1ab239abed1302c80b459c8a767120bb` exposed a CI ownership leak: the Human Wave2 T0-reference-pose editor import change caused the generic P1C01 Shire Render Capture workflow to reserve the self-hosted UE4 runner even though no runtime scene/content/config asset changed.
- The render classifier now recognizes a **dedicated Human Wave2-only delta**. The editor import commandlet is ignored for Shire scene capture only when every non-doc file in the current delta belongs to the Human pipeline allowlist; mixed or unrelated `Source/` changes still force a render.
- Existing green-parent proof remains mandatory before capture can be inherited. This does not create or imply fresh visual acceptance.
- Goal: the Human workflow owns its own compile/import/UE4 evidence, while the Shire render lane stops duplicating the same expensive runner reservation.
- Status: **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD CLASSIFIER PROOF PENDING**.


## 2026-10-05 - Transitive Human-only render proof fix

- Fresh classifier evidence on `c1683caba3f3542b0c7bc30bc445f40484b91b9b` correctly recognized the immediate delta as Human-only, but safe-ancestor reuse still treated the earlier Human editor commandlet change as generic visual `Source/` impact.
- Root fix extends the same **all-files-must-be-Human-owned** rule across the complete ancestor-to-head delta. The commandlet is ignored only when every non-doc file across that proof window is on the dedicated Human allowlist.
- Any mixed source/config/content delta still blocks inheritance and forces capture.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD TRANSITIVE CLASSIFIER PROOF PENDING**.


## 2026-10-05 - Human artifact transport pruning

- The exact-head Human lane was spending multiple minutes in **Download hosted source factory artifact** because the hosted artifact transported the entire downloaded KayKit raw source set plus rejected FBXs, even though UE4 consumes only the selected normalized candidate and JSON receipts.
- The hosted stage now writes the complete provenance/quality receipt first, then removes the raw download/extraction directories and rejected normalized FBXs from the transport tree. It preserves all JSON diagnostics plus only the selected normalized FBX payload(s).
- This changes transport size/cost only; source SHA provenance remains in the receipt and all technical gates remain unchanged.
- Status: **SOURCE-IMPLEMENTED / FRESH TRANSPORT-TIME EVIDENCE PENDING**.

## 2026-10-05 - Human Wave2 UFbxSkeletalMeshImportData compile root fix

- Exact-head Human Wave2 run `37238261738` on `62684319a343b7b183a73dd6b512d68f96ca5b11` passed the hosted KayKit source/Blender normalization job, then failed in the direct UE4.27.2 skeletal gate at **Build ShireJourneyEditor once**.
- Exact compiler evidence: `ShireProductionImportCommandlet.cpp(1213): error C2027: use of undefined type 'UFbxSkeletalMeshImportData'`; `FbxImportUI.h` supplied only the forward declaration.
- Root fix: the editor-only production importer now includes `Factories/FbxSkeletalMeshImportData.h`, providing the complete UE4.27 type before assigning `bUseT0AsRefPose`.
- T0 reference-pose remediation and the unchanged post-import `MISSING_BIND_POSE_BONES` hard rejection remain intact; no deformation, bind-pose, UV, skeleton, or visual gate is weakened.
- Status: **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD HUMAN COMPILE + UE4 REVALIDATION PENDING**. This is not yet COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED, PERFORMANCE-ACCEPTED, or Gate 6/7 acceptance.

## 2026-10-05 - Human Wave2 run #39 closes compile, T0 bind-pose and static deformation gates

- Fresh exact-head Human Wave2 run `37243788900` (workflow run #39) on `157e4e857406a2ce28c18c96cdacfedfd0b07ab5` completed **SUCCESS**.
- The direct UE4.27.2 job reached **Build ShireJourneyEditor once = SUCCESS**, so the `Factories/FbxSkeletalMeshImportData.h` root fix is now **COMPILE-TESTED** for this exact head. Generic Unreal classifier/inheritance is not being used as the compile proof.
- Rogue re-import ran with `use-t0-ref-pose=yes` and passed the unchanged technical hard gate: **48 reference bones**, valid linked `USkeleton`, and **377 files / 0 failures**. The prior `MISSING_BIND_POSE_BONES` rejection did not recur for the technical winner.
- Hosted Wave3 static deformation then produced `STATIC_DEFORMATION_STRESS_PASS` for normalized winner SHA256 `75d715f6ce4673a650a4382bc4f86b7ae0baf0fe548cc63f9b6ded1800f669be`.
- Required semantic deform joints all have nonzero weighted influence. Representative counts: spine=600, pelvis=495, head=613, left/right thigh=136 each, left/right shin=164 each, left/right foot=129 each, left/right hand=118 each.
- Every stress scenario produced nonzero evaluated displacement: shoulders=`1.3242740508125306`, elbows=`1.8153426847017398`, knees=`0.4075082909932559`, hands/feet=`0.34126040685103143`, locomotion=`0.6584697777759558`.
- Evidence boundary remains strict: `visual_deformation_accepted=false`, `retarget_accepted=false`, `runtime_integration_allowed=false`. This is **not** PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED, PERFORMANCE-ACCEPTED, or Gate 6/7 acceptance.

## 2026-10-05 - Frodo hosted Idle/Walk/Run animation-source inventory packet

- The earlier Quaternius animation warehouse attempt did not stage payload: historical run `37211720726` recorded `QUATERNIUS_WAREHOUSE_MANUAL_QUEUE files=0 unresolved=1`. Therefore it is not valid animation input and is not being promoted.
- A new bounded hosted-only source-inventory lane is implemented around the public OpenGameArt page for Quaternius **Universal Animation Library Standard**, marked CC0 and exposing a public Standard ZIP. The project does not automate the interactive/name-your-price Quaternius store path.
- New contract files: `Data/P1C01FrodoAnimationSourceV1.json`, `Scripts/run_p1c01_frodo_animation_source_inventory.py`, `Scripts/test_p1c01_frodo_animation_source_contract.py`, and `.github/workflows/p1c01-frodo-animation-source.yml`.
- The lane runs on hosted Ubuntu only, performs bounded safe ZIP extraction, rejects dangerous extensions including BMP, ignores OBJ as animated production input, inspects FBX actions in Blender, and requires discoverable animated Idle/Walk/Run roles before any self-hosted UE4 reservation.
- The archive SHA256 is intentionally captured on the first hosted receipt and must be pinned before retarget promotion. No retarget, UE4 animation import, AnimBP, runtime integration, PIE, device, visual, or FPS acceptance is implied.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD HOSTED SOURCE-INVENTORY VALIDATION PENDING**.

## 2026-10-05 - Frodo animation inventory run #3 numpy infrastructure root fix

- Exact-head hosted animation-source run `37272018993` on `f035babcd24eee31e601862dba27d9e72e49edd7` verified the OpenGameArt provenance page and downloaded the bounded Standard ZIP successfully.
- The downloaded archive identity is now pinned: SHA256 `18ff1a7215f4852b320203e8aaf02a1578b5c8eef9027fbaedfcedc7b85a3ac2` (logged after a 13.8 MiB download).
- The source inventory failed before evaluating FBX quality because Blender 4.0.2's FBX importer raised `ModuleNotFoundError: No module named 'numpy'`. This is classified as hosted probe infrastructure failure, not an animation-asset rejection.
- Root fix: the hosted workflow now installs `python3-numpy` with Blender and runs an in-Blender numpy import/version preflight before provenance/download/inventory work.
- The manifest now pins the observed archive SHA; future bytes must match before any FBX action inventory can pass.
- No self-hosted UE4 animation work was reserved by this failure. Retarget, AnimBP, runtime integration, PIE, visual and performance acceptance remain false/pending.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD HOSTED REVALIDATION PENDING**.

## 2026-10-05 - Frodo animation source inventory passes; selector semantics hardened

- Exact-head hosted source-inventory run `37272271829` on `836a6ae7aa5051fe9220eb41d95691439397a964` completed **SUCCESS** without reserving UE4.
- Evidence: pinned Standard archive SHA256 matched `18ff1a7215f4852b320203e8aaf02a1578b5c8eef9027fbaedfcedc7b85a3ac2`; safe scan found **11 entries**, **2 FBX files**, and no required Idle/Walk/Run role missing.
- Both FBXs provide full 15/15 semantic-joint coverage for the inventory probe. The archive includes an Unreal Engine variant `Animation Library[Standard]/Unreal Engine/AL_Standard.fbx` with 65 bones and a Unity variant with 53 bones.
- Inventory exposed a selector-quality issue before retarget: substring matching allowed `Crouch_Idle_Loop` to satisfy the Idle token and path tie-breaking selected the Unity FBX. No retarget/runtime gate had accepted this selection.
- Root fix now prioritizes exact action-leaf matches, then exact file-stem, then bounded fallback, and prefers the Unreal Engine FBX path before Unity. This prevents `Idle_Loop` from silently resolving to `Crouch_Idle_Loop`.
- Status: **SOURCE-INVENTORY HOSTED-PASS / SELECTOR ROOT-FIX SOURCE-IMPLEMENTED / EXACT-HEAD REVALIDATION PENDING**. Retarget, UE4 animation import, AnimBP, runtime, visual, PIE/device and performance acceptance remain pending.

## 2026-10-05 - Frodo exact UE animation selection passes; hosted retarget gate implemented

- Exact-head source-inventory run `37272572478` on `e87526dacfed91a47024c4e4ac915a17c90b0f82` completed **SUCCESS** after selector hardening.
- The deterministic selections are now all from `Animation Library[Standard]/Unreal Engine/AL_Standard.fbx`, each with `EXACT_ACTION_LEAF`: Idle=`Idle_Loop` (75-frame span), Walk=`Walk_Loop` (40-frame span), Run=`Jog_Fwd_Loop` (28-frame span). All carry 15/15 semantic coverage and source variant rank 0.
- This closes source discovery/selection only; it does not by itself accept retarget or runtime animation quality.
- A new hosted-only retarget packet is now source-implemented: `Data/P1C01FrodoAnimationRetargetV1.json`, `Scripts/run_p1c01_frodo_animation_retarget.py`, `Scripts/test_p1c01_frodo_animation_retarget_contract.py`, and `.github/workflows/p1c01-frodo-animation-retarget.yml`.
- The retarget gate regenerates the exact KayKit Rogue target from the immutable source and requires normalized SHA256 `75d715f6ce4673a650a4382bc4f86b7ae0baf0fe548cc63f9b6ded1800f669be`. It also pins the Standard archive SHA and Unreal FBX SHA before importing source motion.
- For Idle/Walk/Run it requires source semantic motion, hierarchy validity, nonzero target mesh deformation, finite bounded geometry, and re-importable animation-only FBX derivatives. It remains hosted-only; UE4 is not reserved before this gate passes.
- Status: **SOURCE-IMPLEMENTED / HOSTED RETARGET EXACT-HEAD VALIDATION PENDING**. UE4 animation import, AnimBP, runtime, human visual, PIE/device and performance acceptance remain pending.

## 2026-10-05 - Hosted retarget exact-target identity root fix

- Hosted retarget run `37273271779` on `5b5c1a76080caf833d82647614f09f76a385fb64` regenerated the current Rogue source successfully: immutable raw Rogue SHA matched, the candidate remained the hosted quality winner, and the structural metrics remained 41 bones / 3330 vertices / 2209 weighted vertices / 12 UV layers.
- The run correctly failed before retarget because a freshly exported normalized FBX did not satisfy the exact prior normalized byte-SHA lookup. No source animation was downloaded and no UE4 work was reserved after this identity failure.
- The retarget contract is now stricter about what exact bytes are animated: the actual retarget target is downloaded from successful Human Wave2 run `37243788900`, artifact `p1c01-human-wave2-hosted-157e4e857406a2ce28c18c96cdacfedfd0b07ab5`, and `normalized/candidate_02.fbx` must byte-match SHA256 `75d715f6ce4673a650a4382bc4f86b7ae0baf0fe548cc63f9b6ded1800f669be`.
- Fresh normalization remains a separate source/structure sanity check and may not substitute its bytes for the UE4-gated winner. The exact prior artifact receipt must also identify Rogue as that winner.
- Status: **ROOT-FIX SOURCE-IMPLEMENTED / EXACT-HEAD HOSTED RETARGET REVALIDATION PENDING**. No retarget technical pass, UE4 animation import, AnimBP, runtime, visual, PIE/device or performance acceptance is claimed.

## 2026-10-05 - Frodo hosted Idle/Walk/Run technical retarget passes

- Exact-head hosted retarget run `37273783111` on `be2815e278da30e3474158bc197686f521fb81c1` completed **SUCCESS**.
- Fresh Rogue regeneration remained a source/structure sanity check only and produced normalized SHA256 `28e51fcc8483ffe855c871cd2768463a60dbe88a84f815e1fa1b6aaee7db361d`. It did **not** replace the previously UE4-gated target bytes.
- The actual retarget target was the exact Human Wave2 #39 winner artifact from run `37243788900`, `normalized/candidate_02.fbx`, and passed byte verification at SHA256 `75d715f6ce4673a650a4382bc4f86b7ae0baf0fe548cc63f9b6ded1800f669be`.
- Animation source identity remained pinned: Standard archive SHA256 `18ff1a7215f4852b320203e8aaf02a1578b5c8eef9027fbaedfcedc7b85a3ac2`; Unreal `AL_Standard.fbx` SHA256 `c836c5d47de2a414818f7644632ac43aa84475df6709f4514b9410d232800fd9`.
- Retarget derivatives:
  - Idle: `Frodo_Idle_Retarget.fbx`, SHA256 `ee81650714587d2a1a638f3ff0c1a8239ea555bf84959e96ce5d037af3f33cd3`, 447084 bytes, max target vertex displacement `1.9948943913820651`, bounds ratio `0.7816054533133552..0.782846675089224`, loop endpoint ratio `0.00232035283394632`.
  - Walk: `Frodo_Walk_Retarget.fbx`, SHA256 `c4091b7881a4e9e810e70bb7f3abed58683dff5bacf54e26ccb2e926e4c9e688`, 366588 bytes, max target vertex displacement `2.4605389372972706`, bounds ratio `0.8011183850238995..0.8581567396010394`, loop endpoint ratio `0.0`.
  - Run: `Frodo_Run_Retarget.fbx`, SHA256 `4a4d10d91343dbd701c535d30ea9d9384ca74596cd7720cf6bfdd1c6328e1fc1`, 358860 bytes, max target vertex displacement `2.4000922383830474`, bounds ratio `0.7960923933008167..0.8296153019442178`, loop endpoint ratio `0.002081278016355056`.
- All three animation-only FBX derivatives re-imported in Blender with **41 bones**, **15/15 semantic coverage**, and one nonzero animation action each (**419 fcurves**). Idle re-import range was 2-77, Walk 2-42, Run 2-30.
- Evidence boundary remains strict: `retarget_technical_pass=true`, while `retarget_visual_accepted=false`, `ue4_animation_imported=false`, `anim_bp_allowed=false`, and `runtime_integration_allowed=false`.
- Status: **HOSTED RETARGET TECHNICAL PASS / UE4.27 ANIMATION-ONLY IMPORT GATE NEXT**. This is not PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED, PERFORMANCE-ACCEPTED, or Gate 6/7 acceptance.

## 2026-10-05 - Frodo UE4.27 animation-only import gate source packet

- Following hosted retarget technical PASS, a narrow editor-only import gate is now implemented rather than extending the broad production importer.
- New C++ files preserve Public/Private structure: `Source/ShireJourneyEditorTools/Public/ShireFrodoAnimationImportCommandlet.h` and `Source/ShireJourneyEditorTools/Private/ShireFrodoAnimationImportCommandlet.cpp`.
- The commandlet accepts the exact Human #39 Rogue target FBX plus the three exact hosted retarget FBXs. It first imports `SK_FRODO` with `bUseT0AsRefPose=true`, requires a linked `USkeleton` and the previously observed **48 UE4 reference bones**, then imports animations with UE4.27 `FBXIT_Animation`, `bImportMesh=false`, `bImportAnimations=true`, and the exact newly-created Rogue `USkeleton`.
- Required generated sequences are `A_Frodo_Idle`, `A_Frodo_Walk`, and `A_Frodo_Run`. Each must resolve to exactly one `UAnimSequence`, point to the identical `USkeleton`, contain more than one frame, and have finite nonzero play length.
- Hosted preflight is implemented in `.github/workflows/p1c01-frodo-ue4-animation-import.yml`: it verifies the exact Human #39 target SHA and all three exact retarget derivative SHAs before the self-hosted UE4 job is eligible.
- The self-hosted job builds `ShireJourneyEditor` once, runs only the dedicated commandlet, requires its `UE4_ANIMATION_IMPORT_TECHNICAL_PASS clips=3 bones=48` marker, verifies the five expected generated packages, uploads evidence, then removes only untracked transient gate assets.
- Static contract guard: `Scripts/test_p1c01_frodo_ue4_animation_import_contract.py`.
- Status: **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD COMPILE + UE4 ANIMATION IMPORT VALIDATION PENDING**. No AnimBP, runtime integration, human visual, PIE/device, performance, or Gate 6/7 acceptance is claimed.

## 2026-10-05 - Owner screenshot visual rejection + Frodo UE4 animation checkout isolation

- Owner-provided PIE screenshots show the current P1C01 runtime still reading as **proxy/greybox**, not finished Shire presentation: flat/grey terrain and vegetation, simple low-poly trees, weak material/lighting depth, and a visible blocky player fallback instead of production Frodo.
- This is direct human visual rejection evidence for the current runtime presentation. It does **not** invalidate the machine evidence that source/import/render jobs are green; it proves those jobs are insufficient for visual acceptance.
- Source audit confirms part of the visual problem is asset fidelity, not just missing residency: several files currently named Production are deliberately low-poly generated meshes. Examples include `SM_ShGroundBlock.obj` as a cube-based ground tile and simple low-poly trunk/canopy assets. Therefore further blind density of the same meshes is not authorized as a final-quality fix.
- Frodo proxy persistence is also expected from the current runtime contract: runtime promotion still requires the skeletal package plus `ABP_FRODO_Locomotion`; the technically validated rig/animations remain gate artifacts until UE4 animation import, AnimBP, runtime hookup and human visual review close.
- The first fresh UE4 animation-import run on exact head `c10cc6fa9abf122cb6efadb4be7e6c43921d7926` failed **before build/import** because `actions/checkout@v4` could not clean/recreate the self-hosted workspace and ended with `fatal: not a git repository`.
- Root fix is source-implemented on the same closeout branch: the self-hosted UE4 animation gate now uses an isolated temporary exact-SHA checkout, matching the project's proven self-hosted isolation pattern, and all build/import/cleanup paths are redirected to that isolated source root.
- Status: **VISUAL REJECT / INFRASTRUCTURE ROOT FIX SOURCE-IMPLEMENTED / EXACT-HEAD REVALIDATION PENDING**. No PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED, PERFORMANCE-ACCEPTED, or Gate 6/7 acceptance is claimed.

## 2026-10-05 - Frodo UE4 animation gate isolated-build root fix

- Exact-head animation-import run `37281245292` on `e209988496ddb5380f30596d608e7d95790fabaf` passed hosted artifact identity, isolated checkout, runner verification, exact Windows SHA checks, and the workflow's build step, then failed before the commandlet could enter `Main`.
- UE4 launch evidence: `ModuleManager: Unable to load module 'ShireJourney' - 0 instances of that module name found` and the same for `ShireJourneyEditorTools`.
- Root cause: the workflow invoked `ci_build_unreal.cmd` from the isolated checkout, but that script still derived project/log/intermediate roots from GitHub's original `GITHUB_WORKSPACE`. The green build therefore targeted the old runner workspace while `UE4Editor-Cmd` launched the isolated exact-head project, which had no matching project module DLLs.
- Root fix: `ci_build_unreal.cmd` now supports an explicit `SHIRE_BUILD_WORKSPACE` override, validates that root, uses it for project/log/retry cleanup paths, and prints `CI_BUILD_WORKSPACE` evidence. The Frodo animation workflow supplies the isolated source root through that override. A static contract guard now requires this wiring.
- Human Wave2 run `37281245185` on the same head completed **SUCCESS**, including the direct UE4 skeletal gate and hosted Frodo static deformation stress.
- Status: **ROOT-FIX SOURCE-IMPLEMENTED / FRESH EXACT-HEAD FRODO UE4 ANIMATION IMPORT REVALIDATION PENDING**. No AnimBP/runtime, PIE, device, visual, performance, or Gate 6/7 acceptance is claimed.

## 2026-10-05 - Frodo UE4 animation imported-object discovery root fix

- Exact-head animation run `37288340732` on `fc3b40621bc0b064139208b85a590e73e7377d11` proved the isolated build-root remediation: exact checkout, runner verification, payload SHA enforcement, and **Build ShireJourneyEditor once = SUCCESS** all completed before UE4 commandlet execution.
- The earlier module-loading failure did not recur. UE4 reached FBX skeletal digestion and logged **`Bones digested - 48`**, then the commandlet exited 46 because `UAssetImportTask::Result` did not contain a directly castable `USkeletalMesh`.
- This is an editor result-discovery defect, not a skeleton/FBX rejection. The existing production importer already uses the safer UE4.27 pattern: resolve the deterministic expected object path through AssetRegistry/resident object state after import.
- Root fix: the dedicated Frodo commandlet now resolves `SK_FRODO` at the exact destination object path through `FAssetRegistryModule::GetAssetByObjectPath` plus resident-object lookup, validates the registered class, and uses the same deterministic object-path pattern for Idle/Walk/Run `UAnimSequence` assets. `Task->Result` is retained only as diagnostic count.
- All previous hard gates remain: T0 ref pose, 48-bone sanity, identical linked `USkeleton`, >1 animation frame, finite nonzero play length, and exact hosted payload SHAs.
- Status: **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD UE4 ANIMATION IMPORT REVALIDATION PENDING**. No AnimBP/runtime, PIE, device, visual, performance, or Gate 6/7 acceptance is claimed.

## 2026-10-05 - Frodo AssetRegistry contract guard correction

- Exact-head run `37289335569` on `242a90707e7f9a9a4db88e6971487e83deaa288a` failed in the hosted static contract before any self-hosted UE4 reservation.
- The importer source was not the failing layer. The new test accidentally asserted the acceptance form `RigAssetData.AssetClass == USkeletalMesh...` while the implementation correctly expresses the fail-closed rejection condition as `RigAssetData.AssetClass != USkeletalMesh...`.
- Root fix: correct the hosted assertion to require the actual rejection condition. No runtime/import gate is weakened and no UE4 retry is spent until this static guard passes.
- Status: **TEST ROOT-FIX SOURCE-IMPLEMENTED / EXACT-HEAD REVALIDATION PENDING**.

## 2026-10-05 - Frodo UE4 animation technical import PASS; package persistence root fix

- Exact-head run `37289482279` on `a0713481121a76b2f226cd4358b2a470ffa4f90d` passed hosted artifact identity, isolated exact checkout, exact Windows payload SHA checks, and **Build ShireJourneyEditor once = SUCCESS**.
- The dedicated UE4 commandlet then passed the actual rig/animation technical gate:
  - exact rig: `/Game/Production/Characters/Rigs/FRODO/SK_FRODO.SK_FRODO`
  - **48 reference bones**, linked `/Game/Production/Characters/Rigs/FRODO/SK_FRODO_Skeleton.SK_FRODO_Skeleton`, T0 ref pose enabled
  - Idle: **76 frames / 2.500000 s**
  - Walk: **41 frames / 1.333333 s**
  - Run: **29 frames / 0.933333 s**
  - marker: `UE4_ANIMATION_IMPORT_TECHNICAL_PASS clips=3 bones=48`
- Post-import disk verification then failed only because `SK_FRODO_Skeleton.uasset` had not been persisted as a standalone package, despite the linked `USkeleton` being valid in memory. This is a persistence defect after technical import, not an FBX/retarget/skeleton rejection.
- Root fix: the commandlet now deterministically saves the skeletal mesh, linked skeleton, and all three animation-sequence packages via `UPackage::SavePackage`, verifies each file exists, and emits `UE4_ANIMATION_PACKAGE_PERSISTENCE_PASS assets=5` before the technical-pass marker.
- The existing workflow disk gate remains unchanged; the missing skeleton requirement is not waived.
- Status: **UE4 ANIMATION TECHNICAL IMPORT PASS / PERSISTENCE ROOT-FIX SOURCE-IMPLEMENTED / FRESH EXACT-HEAD REVALIDATION PENDING**. AnimBP/runtime integration, PIE/device, visual, performance, and Gate 6/7 remain unaccepted.

## 2026-10-05 - Frodo package-save UE_LOG compile root fix

- Exact-head Render Capture run `37290506368` on `94c97b1f0c4a1331bf128e7468b9c3b638ed8960` reached the editor build and failed before capture on the new package-save helper.
- Exact compiler root cause: UE4.27 `UE_LOG` requires a compile-time verbosity token; the helper passed `bSaved && bExists ? Display : Error` as the verbosity argument, producing the macro cascade beginning at `ShireFrodoAnimationImportCommandlet.cpp(217): error C3493`.
- Root fix: use explicit success/failure branches with literal `Display` and `Error` verbosity tokens. Deterministic package persistence, five-package requirement, and all animation hard gates are unchanged.
- The dedicated Frodo animation self-hosted job for the failing head was still queued when this defect was identified, so no additional UE4 import cycle is intentionally spent on the known compile error.
- Status: **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD COMPILE + PERSISTENCE REVALIDATION PENDING**.


## 2026-10-05 - Frodo runtime skeletal locomotion bridge

- Exact-head Frodo UE4 animation run `37291448630` on `555fe56e94fb7d4d7036a1e80462d9f2317cc322` closed the five-package persistence blocker with `UE4_ANIMATION_PACKAGE_PERSISTENCE_PASS assets=5`; mesh, skeleton, Idle, Walk and Run packages were all verified on disk inside the isolated UE4 checkout.
- Runtime root cause for the owner-visible blocky player was then isolated: `UShireChapterAssetStreamingSubsystem` required both `SK_FRODO` and the still-missing `ABP_FRODO_Locomotion` before it would broadcast rig readiness, so the technically valid mesh/animations could never replace the modular fallback.
- Source implementation now treats Frodo's skeletal mesh plus Idle/Walk/Run as the minimum async-resident locomotion set. The future AnimBP remains preferred when its package exists; until then the player component can use UE4 single-node skeletal playback and switch Idle/Walk/Run from movement speed.
- The path remains soft/async through `FStreamableManager::RequestAsyncLoad`. No heavy synchronous load was added. Existing NPC `ResolveCharacterRig` semantics remain intact.
- The modular fallback is retained until the skeletal core resolves; it is hidden only after the real skeletal mesh and locomotion sequences are resident and applied.
- Static regression guard: `Scripts/test_p1c01_frodo_runtime_promotion_contract.py`, wired into hosted Pre-Unreal validation.
- Status: **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD STATIC + UE4 COMPILE/RUNTIME VALIDATION PENDING**. This is not PIE/device/visual/performance acceptance. Local production promotion still needs the exact rig/animation payloads to be regenerated or staged outside the transient CI checkout.

## 2026-10-05 - Frodo validated source promotion + fail-closed local launch

- The dedicated Frodo UE4 animation workflow now promotes the exact hash-pinned target FBX and Idle/Walk/Run derivatives into `SourceAssets/ValidatedRuntime/FRODO` only after the UE4.27 package/import gate succeeds.
- Promotion preserves the validated SHAs and writes provenance for KayKit Rogue (CC0 normalized derivative) plus Quaternius Universal Animation Library Standard / OpenGameArt (CC0).
- `run_local_p1c01_visual_acceptance.ps1` now validates all four source hashes, runs `ShireFrodoAnimationImport`, requires both persistence and technical-pass markers, and refuses to launch if any of the five Frodo runtime packages are missing.
- This prevents another owner review session from silently falling back to the blocky player because CI-only assets were absent locally.
- Status: **SOURCE-IMPLEMENTED / SOURCE-PROMOTION WORKFLOW + LOCAL FAIL-CLOSED IMPORT PENDING FRESH EXACT-HEAD EXECUTION**. No visual/PIE/device/performance acceptance is claimed.

## 2026-10-05 - P1C01 Poly Haven MTL generator root fix

- `Scripts/prepare_p1c01_material_intake.ps1` no longer emits concatenated PowerShell array expressions that serialize MTL directives as split tokens/lines.
- The generator now formats complete one-line directives for `newmtl`, `Pr`, `Pm`, `Ks`, and `map_Kd`.
- New fail-closed regression guard: `Scripts/test_p1c01_material_mtl_contract.ps1`, wired into hosted Pre-Unreal validation.
- Historical malformed generated material commit remains rejected and is not merged/reused unchanged.
- Status: **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD STATIC + UE4 MATERIAL IMPORT VALIDATION PENDING**. Human visual and performance acceptance remain NOT ACCEPTED.

## 2026-10-05 - Frodo source promotion conflict-safe publish hardening

- The validated Frodo source-promotion step is being hardened so it does not assume the PR branch stayed frozen for the full self-hosted UE4 run.
- The promotion payload remains staged outside the checkout with the exact validated SHAs; before publishing, the isolated checkout refreshes to the latest PR branch head and reapplies only the validated runtime-source directory.
- Publish retries are bounded and fast-forward only. No force push is authorized.
- This prevents a long UE4 gate from overwriting or rejecting newer closeout work while preserving exact source identity.
- Status: **SOURCE-IMPLEMENTED PENDING FRESH EXACT-HEAD WORKFLOW PROOF**. No runtime/visual/device/performance acceptance is promoted by this infrastructure hardening.

## 2026-10-05 - P1C01 receipt-verified surface source promotion lane

- A dedicated P1C01 material source-promotion lane is added for the ledger-registered high-fidelity surface replacement.
- Hosted preflight validates the corrected MTL generator/contract before the warehouse runner is reserved.
- The self-hosted lane reads only receipt/SHA256-verified warehouse inputs through `prepare_p1c01_material_intake.ps1`, requires the known Shire material subset plus a minimum prepared count, verifies complete one-line MTL directives, and publishes prepared source files into `SourceAssets/Production/Imported/P1C01Materials`.
- PNG payloads remain Git LFS-managed; animated-asset rules are unaffected. Publish is conflict-safe, bounded, and never force-pushes.
- The source-promotion lane does not claim UE material import success. The resulting SourceAssets commit must still pass the existing generic Unreal production-import/build and fresh render capture before runtime material binding can be accepted.
- Status: **SOURCE-IMPLEMENTED / FRESH MATERIAL SOURCE-PROMOTION EXECUTION PENDING**. Human visual and performance acceptance remain NOT ACCEPTED.

## 2026-10-05 - Material promotion PowerShell invocation correction

- Pre-execution static review caught an invalid shell continuation in the new material-promotion workflow: PowerShell does not use a trailing backslash for command continuation.
- The intake invocation is normalized to a single PowerShell command line before the first warehouse execution; no failed runner evidence is being misclassified as a content failure.
- Status remains **SOURCE-IMPLEMENTED / FRESH EXECUTION PENDING**.

## 2026-10-05 - Poly Haven P1C01 source approval manifest reconciliation

- Eight previously receipt/SHA256-verified Poly Haven P1C01 material source files now have explicit asset-level APPROVED records in `Data/ExternalAssetManifest.json`.
- Each record preserves provider, CC0 license class, acquisition date, exact source URL, exact base-color SHA256, intended use, and an evidence boundary that does not overclaim UE/runtime/visual acceptance.
- `Data/ResourceIntegrationPlan.json` approved external count is reconciled from historical zero to 8.
- PG-052 no longer hardcodes an empty manifest assumption; it now compares the plan count against the actual number of APPROVED manifest records.
- This is a governance/source-truth correction required before production promotion. No new third-party geometry is approved by this change.
- Status: **SOURCE/GOVERNANCE RECONCILED / FRESH EXACT-HEAD STATIC VALIDATION PENDING**.

## 2026-10-05 - Pre-Unreal #1985 PG-176 stale MTL marker root fix

- Exact-head Pre-Unreal run `37348487318` / #1985 on `4d12a0984df77b5db37f69530c5f03b64e2a1309` failed at project structure validation only.
- Exact failure: `PG-176 material intake preparation guard missing: "Ks $ksText $ksText $ksText"`.
- Root cause: PG-176 still asserted the historical raw interpolation marker after the MTL generator was intentionally repaired to use the complete formatted directive `("Ks {0} {0} {0}" -f $ksText)`.
- The validator now requires the corrected formatted directive. The generator is not reverted and no material gate is weakened.
- Status: **ROOT-FIX SOURCE-IMPLEMENTED / FRESH EXACT-HEAD PRE-UNREAL REVALIDATION PENDING**.

## 2026-10-05 - Material promotion run #10 stale warehouse-root root fix

- Material Surface Promotion run `37349024980` prepared all 8 required P1C01 surfaces successfully, then failed the integrity step because `manual_queue_count=96`.
- Exact evidence showed historical receipt rows pointing at `C:\actions-runner\_warehouse\ShireJourney\...` while the active warehouse root is `D:\actions-runner\_warehouse\ShireJourney`; the same required assets were already found/prepared from the active root.
- Root fix: `prepare_p1c01_material_intake.ps1` now rebases a missing receipt path only when it contains the canonical `/ShireJourney/` warehouse boundary, keeps the relative suffix inside the configured WarehouseRoot, verifies the rebased file exists, and still enforces the receipt SHA256 before intake.
- Arbitrary missing absolute paths are not trusted or promoted. Manual queue semantics remain fail-closed for genuinely missing/hash-drifted payloads.
- Static regression guard now requires the bounded rebase logic plus SHA enforcement.
- Status: **ROOT-FIX SOURCE-IMPLEMENTED / FRESH MATERIAL PROMOTION REVALIDATION PENDING**.

## 2026-10-05 - Promotion wildcard copy root fix

- Pre-execution review found both Frodo and Shire-surface promotion publish steps used `Copy-Item -LiteralPath (... "*")` where wildcard expansion is required.
- `-LiteralPath` treats `*` literally and would have failed after otherwise-valid source preparation.
- Root fix: wildcard directory copies now use `Copy-Item -Path`; exact single-file copies continue using `-LiteralPath`.
- Static contract guards now forbid the literal-wildcard pattern in both promotion workflows.
- Status: **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD PROMOTION REVALIDATION PENDING**.

## 2026-10-05 - GitHub Actions approval-loop root fix

- The owner-visible `Action required / Approve and run` loop was traced to two workflow-authored branch commits: `996d56d...` (Frodo runtime source promotion) and `ea356bd...` (Shire material source promotion), both authored by `Shire Journey CI`.
- Those self-pushing workflows caused subsequent pull-request synchronize events to be treated as bot-originated runs requiring maintainer approval.
- Root fix: both workflows are now **verify-only**. They no longer commit or push to the PR branch, and their repository permission is reduced from `contents: write` to `contents: read`.
- Frodo gate now verifies the already-tracked four exact SHA-locked FBX runtime sources plus provenance after the UE4 technical import gate.
- Material lane now verifies the already-tracked eight receipt/SHA-locked Shire source surfaces against a freshly prepared warehouse receipt instead of mutating the branch.
- Source promotion into the branch is an owner/connector-side action only; CI remains evidence generation/verification and cannot create another approval loop.
- Regression tests forbid `git push` and `contents: write` in both affected workflows.
- Status: **SOURCE-IMPLEMENTED / FRESH OWNER-AUTHORED EXACT-HEAD ACTION BEHAVIOR VALIDATION PENDING**. No runtime/visual/device/performance/Gate 6/7 acceptance is claimed.

## 2026-10-05 - GitHub Actions approval-loop root fix

- Repeated `Action required / Approve and run` was traced to CI-authored branch mutations, not UE4 build instability.
- The Frodo runtime-source and Shire material-source workflows were committing/pushing back into the active PR branch with the workflow token, producing bot-authored synchronize events that GitHub placed behind maintainer approval.
- Both lanes are now **verify-only**: read-only contents permission, exact hash/receipt validation, no branch push, no CI-authored commit, and no promotion retry loop.
- The already-promoted Frodo FBX payload and eight receipt-verified Poly Haven surface sources remain tracked on the branch; CI now validates them without mutating repository state.
- Regression contracts explicitly require read-only workflow permissions and forbid the affected `git push` paths.
- Replacement head is owner-authored through the GitHub connector; subsequent workflow runs entered queued/pending states instead of `action_required`.
- Status: **ROOT CAUSE REMOVED / FRESH EXACT-HEAD VALIDATION RUNNING**. No PIE/device/visual/performance/Gate 6/7 acceptance is implied.

## 2026-10-05 - Material verify-only contract path assertion fix

- Material Surface Promotion #28 failed in hosted preflight before warehouse execution.
- Exact failure: the regression test expected `SourceAssets/Production/Imported/P1C01Materials` while the verify-only PowerShell workflow correctly uses the Windows path `SourceAssets\Production\Imported\P1C01Materials`.
- Root cause is test-path representation drift only. Runtime/source verification semantics are unchanged.
- The assertion now matches the actual Windows workflow path. No material gate or SHA verification is weakened.
- Status: **STATIC TEST ROOT-FIX SOURCE-IMPLEMENTED / FRESH EXACT-HEAD REVALIDATION PENDING**.

## 2026-10-05 - P1C01 high-fidelity surface runtime binding

- Four highest-impact, already receipt/SHA-verified Poly Haven surface materials are now added to the P1C01 chapter streaming bank as soft object paths: DirtSoil, StonyPath, TreeBark and MossStone.
- `AShirePrototypeWorldBuilder` consumes these only after chapter-bank residency through `ResolveResidentMaterial`; no synchronous `LoadObject`/sync stream path is introduced.
- Chapter-local bindings:
  - DirtSoil -> garden soil + river bank HISM;
  - StonyPath -> path-stone HISM;
  - TreeBark -> distant trunk + woodland tree slot 0;
  - MossStone -> rock HISM.
- Existing Common asset bank remains untouched and instance counts are unchanged.
- This packet deliberately does not preload WarmPlaster/Wood/GrassPath yet to keep the first visual replacement bounded for the ~2 GB VRAM target.
- New static guard: `Scripts/test_p1c01_high_fidelity_surface_binding_contract.py`, wired into Pre-Unreal.
- Status: **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD STATIC + UE4 IMPORT/RENDER VALIDATION PENDING**. No visual/performance/device/Gate 6/7 acceptance is claimed.

## 2026-10-05 - P1C01 PNG Git LFS hydration root fix

- Unreal Build #1608 / run `37363370894` on exact head `ae6dcf7c3a7879f6769465fad3a49afaf0505f7c` built `ShireJourneyEditor` successfully, then failed production import at exactly eight new P1C01 PNG albedo sources. Import summary: **384 files / 16 failures** = eight PNG import failures plus eight dependent albedo-binding failures.
- Root cause is now isolated below the UE4 importer: `.gitattributes` routes `*.png` through Git LFS, and the eight promoted Shire PNG Git blobs are LFS pointer records referencing real payloads of roughly 8-23 MB. The self-hosted exact-head checkout did not explicitly hydrate that P1C01 LFS material subtree before invoking UE4, while the 24 TGA texture sources are not covered by the PNG LFS rule and continued to import.
- Root fix: both the generic Unreal Build lane and P1C01 Render Capture lane now run `Scripts/hydrate_p1c01_material_lfs.ps1` before any editor build/import/capture. The helper performs a targeted `git lfs pull` only for `SourceAssets/Production/Imported/P1C01Materials/**`, then fail-closes unless every discovered PNG has the real PNG signature and emits `P1C01_LFS_TEXTURE_HYDRATION_PASS`.
- Importer hardening: `ShireProductionImportCommandlet` now rejects any residual Git LFS pointer source before `ImportAssetTasks` and emits the explicit `GIT_LFS_POINTER_SOURCE` marker instead of allowing a misleading generic texture-import failure.
- Hosted regression coverage is wired through `test_p1c01_material_lfs_hydration_contract.py`; no texture gate, albedo-binding requirement, package-persistence requirement, or visual/performance gate is weakened.
- Status: **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD PRE-UNREAL + UE4 IMPORT/BUILD + RENDER REVALIDATION PENDING**. No PIE, device, visual, performance, or Gate 6/7 acceptance is claimed.

## 2026-10-06 - P1C01 One-Shot Mega Chapter production start

- Owner-facing production model is now **one chapter = one mega wave**. P1C01 is `P1C01-ONE-SHOT-FINISH`, covering F1-01/F1-02/F1-03 through Bucklebury/Ferry. Internal dependency cars remain technical safety lanes only; they are not separate owner-facing waves.
- Complete chapter manifest: `Data/P1C01OneShotChapterFinishV1.json`. It includes characters, world route/detail, materials/vegetation, Living Shire, gameplay/exploration, audio, save/reliability, streaming/performance and Gate 6/7.
- Target clarification: **8 GB system RAM / ~2 GB GPU VRAM**. Production/Warehouse throughput may scale aggressively; runtime residency remains bounded and measured.
- Unreal Build #1609 on `b114a8e5ab3a91d35ae45fb561cedf5486ead2e5` already proved the repaired production import path: **384 files / 0 failures**, **169/169 albedo bindings**, **233 material packages / 0 missing**.
- Road-cleaning root fixes in this packet: PG-017 now checks the committed Git object instead of a correctly hydrated LFS working-tree file; `ChapterAssetStreamingPlan` derived totals are reconciled and hosted PG-226 catches future drift before the expensive package lane.
- The Daily Project Manager workflow was separately moved off the UE4 self-hosted runner via main maintenance PR #330, so scheduled reporting no longer competes with chapter production for the Unreal machine.
- Status: **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD VALIDATION PENDING**. No PIE/device/visual/performance/Gate 6/7 acceptance is claimed.

## 2026-10-06 - P1C01 exact-head preflight root-fix before mega chapter execution

- Exact head `99bd0f93dcbb783451da638a87816891195dd852` triggered Pre-Unreal #2016 and the expected P1C01/UE4 lanes. The visible "stopped" state was mostly self-hosted jobs queued behind the single UE4 runner plus a fast Pre-Unreal failure.
- Pre-Unreal #2016 failed on two control-contract regressions only:
  - `PG-127`: the new Git-LFS pointer detector introduced escaped CR/LF literals in `ShireProductionImportCommandlet.cpp`. Root fix removes escaped newline tokens entirely while preserving fail-closed pointer detection using the LFS version/OID/size signatures.
  - `PG-192`: `P1C01ChapterClosureMegaPackV2.status` was repurposed for owner-facing One-Shot wording even though `RUNNER_EXECUTION_READY` is a machine execution contract. Root fix restores `RUNNER_EXECUTION_READY` and records One-Shot state in separate owner-facing fields.
- No chapter scope, provenance gate, texture gate, runtime residency rule, or Gate 6/7 evidence requirement is weakened.
- Status: **SOURCE-IMPLEMENTED / FRESH EXACT-HEAD STATIC + UE4 QUEUE REVALIDATION PENDING**.

## 2026-10-06 - Runner queue incident + P1C01 closure trigger repair

- Live branch head before this repair: `2092dace6a8e3f7ea93ad2c2a5186745be4ee8a9`.
- Repository Actions observation: **0 jobs in progress / 6 runs queued**. Queued self-hosted work included Unreal Build, Material Surface Promotion, Frodo UE4 Animation Import, Shire Render Capture, Human Character Wave 2 and one older Daily Manager run.
- Last proven runner health before the stall: `RUNNER_HEALTH_PASS identity=IDEAPAD320\user sessionId=2 listenerPid=30472 workerCount=1` at 2026-10-05 21:15 UTC. The same runner reached W00 package preflight at approximately 21:25 UTC. A self-hosted scheduled job remained queued from 21:35 UTC onward, so the runner stopped accepting repository jobs between approximately 21:25 and 21:35 UTC.
- Current classification: **RUNNER UNAVAILABLE / NOT ACCEPTING JOBS**, based on queue behavior. GitHub evidence cannot distinguish machine sleep/logout from listener/watchdog/registration failure without the Windows host responding.
- Independent workflow defect found: `P1C01 Chapter Closure Pack` previously triggered only on push to `develop` or manual dispatch, so PR #329 could not automatically launch the One-Shot chapter source train.
- Root fix: the closure workflow now supports `pull_request` to `develop`, includes the One-Shot manifest in path routing, uses PR-specific concurrency and cancels superseded PR closure runs.
- This earlier outage classification is superseded by the later exact-source-head Closure Pack #40 proof below. No PIE/device/visual/performance acceptance is claimed.

## 2026-10-06 - Offline saturation world/audio/mission packet

- Runner-independent preparation now covers full-route micro detail, audio master slots/provenance and F1-01/F1-02/F1-03 mission/QA handoff.
- Audio truth remains explicit: tracked `SourceAssets/Production/Audio` master count is **0** at this snapshot; 25 scripted and 58 contextual generated/external sources are upstream material only until production WAV masters+receipts exist.
- F1-03 topology is preserved: P1C01 owns Shire roads/Bucklebury through FerryEscape; P1C02 owns Bree arrival/opening.
- GitHub-hosted `P1C01 Offline Source Saturation` validates these source contracts without the UE4 runner.
- Status: **SOURCE/DATA PREPARATION ADVANCED / HOSTED STATIC VALIDATION PENDING**.

## 2026-10-06 - Offline source intake + Ferry owner-lock root fix

- Exact source audit on PR #329 parent head `df575f04f4c573fe832523a0cbf374882a2df898` found a chapter-boundary conflict: the Ferry far-side trigger assigned `NextChapterId=P1C02`, and `UShireStoryFlowSubsystem` also promoted a restored `P1C01/FerryEscape stage 2` state directly into `RoadToBree`. That contradicted the active Governor rule that Bree remains owner-explicit.
- Root fix keeps `FerryEscape stage 2` as the committed P1C01 terminal state, removes both automatic P1C02 openings, emits `FerryEscapeComplete`, and binds `WC_P1C01_FERRY_END` after authoritative quest mutation so the chapter-end state has an explicit checkpoint path.
- `Data/P1C01OfflineSourceIntakeV1.json` now routes the seven non-Frodo named character FBX gaps, production WAV-master intake, five visible world hero-source gaps, and a gameplay/save coverage audit. Candidate provider records are source candidates only; no binary acquisition or runtime promotion is claimed.
- The gameplay audit makes F1-02 investigation/packing explicit authoring gaps, keeps stealth departure/Black Rider hiding/Ferry runtime proof open, and records retry/skip/backtrack/disk-roundtrip as evidence gaps rather than silently treating them as complete.
- Hosted `P1C01 Offline Source Saturation` now fail-closes if either P1C01->P1C02 automatic source path returns and also checks the new source-intake contract.
- Status: **SOURCE-IMPLEMENTED / HOSTED STATIC VALIDATION PENDING / UE4 COMPILE+RUNTIME PROOF PENDING**. No PIE/device/visual/performance/Gate 6/7 acceptance is claimed.

## 2026-10-06 - Whole-game offline saturation / source-demand reconciliation

- Owner-authorized exception while the UE4 runner is unavailable: prepare the whole game from F1-01 through F3-07 at source/data/provenance/QC level, while runtime remains serialized to P1C01 only.
- Static audit found concrete cross-chapter demand pollution in `Data/WholeGameChapterAssetDemandMatrixV1.json`: Bree/inn and Ent families leaked into F1-03, Ent demand leaked into unrelated Rivendell/Edoras/Paths rows, Mordor/Black Gate/lava demand leaked into Amon Hen and Pelennor, and active siege demand leaked into Return/Farewell. The affected rows are reconciled to `Data/WholeGameChapterProductionPacketsV1.json` source title/location/focus/locked outcome.
- `Data/GlobalWarehouseSourceRegistryV2.json` had declared `source_count=102` while the array contained 142 unique source records. The declared count is corrected to the actual array length.
- `Data/WholeGameWarehouseSaturationBatchV3.json` records a selective, provenance-first candidate queue for reusable humanoid bases/outfits/animations, horse/fauna, support nature/architecture, medieval props and whole-game audio. Candidate presence is not staging/import/runtime evidence.
- Repository source census at this packet: 423 SourceAssets files, 416 under Production, 5 under ValidatedRuntime; extension counts include 352 OBJ, 30 MTL, 8 PNG, 24 TGA and 4 FBX. The four FBX files are the established Frodo technical runtime bundle; OBJ volume is not animated-character completion.
- Architecture static review preserves ownership: `UShireQuestSubsystem` story truth, `AChapterWorldRouter` world commit, `UShireChapterAssetStreamingSubsystem` async heavy-asset residency, `ALivingWorldDirector` pooled population/events and `UShireNPCContextSubsystem` committed context/schedules. No per-frame full-world context rebuild was found in the reviewed LivingWorld/NPCContext path.
- Important evidence boundary: static reasoning does **not** prove collision-free traversal, visual-artifact absence, hitch-free play, audio quality or target FPS. Those remain chapter-specific runner/PIE/device/human evidence.
- Branch hygiene is prepared through the existing fail-closed hosted cleanup path. The active PR branch plus develop/main, archive recovery and the two unique Edoras preparation refs are explicitly protected.
- Status: **SOURCE-IMPLEMENTED / HOSTED STATIC VALIDATION PENDING**. P1C02 runtime remains LOCKED.

## 2026-10-06 - Pre-runner terminal-gate reconciliation

- Latest hosted Pre-Unreal exposed three real consistency failures around the P1C01 ferry terminal: the far-bank story beat `FerryEscapeComplete` had no presentation cue, the validator still expected an automatic P1C01 -> P1C02 bridge, and the persistence edge audit still expected a terminal P1C01 save to canonicalize into Bree.
- The owner-facing chapter policy is the opposite: P1C01 must end cleanly at FerryEscape stage 2 and P1C02 remains owner/predecessor gated until P1C01 Gate 6/7 acceptance.
- Source fix: `FerryEscapeComplete` now has a bounded presentation cue and a StoryBeatPlan row that reuses the existing ferry camera/audio family without opening Bree.
- Validation fix: Pre-Unreal now forbids automatic FerryEscape -> P1C02/RoadToBree bridging and requires the far-bank terminal beat instead.
- Persistence audit fix: restoring a terminal P1C01 FerryEscape stage-2 save must preserve P1C01, publish exactly once, cause zero extra world commits, and leave the committed Shire world intact.
- Status remains **SOURCE-IMPLEMENTED / HOSTED VALIDATION PENDING**. No compile/PIE/device/visual/performance claim is made.

## 2026-10-06 - Final pre-runner comprehensive sweep

- Final offline pre-runner sweep is now machine-guarded in `Scripts/audit_whole_game_offline_saturation.py`.
- Repository census: 946 tracked files; 0 BMP; 0 tracked Binaries/DerivedDataCache/Intermediate/Saved/.vs; all runtime/editor headers are under Public and all .cpp are under Private.
- ValidatedRuntime contains the four established Frodo FBX files and no OBJ. Production character OBJ stock remains source/fallback only and is explicitly forbidden as final animated delivery.
- Runtime source scan found no `StaticLoadObject`. Direct runtime `LoadObject` occurrences are limited to `/Engine/BasicShapes/` fallback assets/material; production-heavy loading stays behind soft paths and the async chapter streaming subsystem.
- `UShireNPCContextSubsystem` contains no actor scan/spawn authority. `ALivingWorldDirector` retains bounded 0.75s maintenance plus pooled ambient NPC/interaction/motion acquisition/release; its persistent ambient registry scan is commit/reset reconciliation, not a per-frame context rebuild.
- P1C01 terminal contract is now guarded end-to-end: FerryEscape stage 2 / FerryEscapeComplete; no automatic P1C02 start; terminal restore remains P1C01 with one persistence publication and zero extra world commits.
- PG-192 closure workflow drift was root-fixed: P1C01 Chapter Closure Pack is non-cancellable so a newer PR event cannot abort the long one-shot source train.
- Current ProjectGovernor performance note now reflects the actual tracked tree: 0 BMP. Historical review records remain historical and were not rewritten.
- Remaining proof is engine/device/human only: compile/import/package, collision/traversal, animation/render, audio playback, disk roundtrip, FPS/RAM/VRAM/frame-time tails and Gate 6/7.
- Status: **SOURCE-IMPLEMENTED / HOSTED STATIC VALIDATION PENDING**. P1C02 remains LOCKED.

## 2026-10-06 - Governor one-shot validator root correction

- Hosted Pre-Unreal reached full core validation, then exposed a governance-validator regression: `Data/ProjectGovernor.json` had already moved to the accepted DEC-104 owner-facing mode `ACTIVE_ONE_SHOT_CHAPTER_FINISH`, while `Scripts/project_governor.py` still hard-required the older `ACTIVE_GATE_FIRST` identity and required the owner-facing lane to equal the technical W01 lane.
- Root correction preserves both layers rather than reverting the Governor: the owner-facing lane is `P1C01_ONE_SHOT_SHIRE_CHAPTER_FINISH`; the technical production focus/development mode remains `W01_P1C01_PRODUCTION_VERTICAL_SLICE`.
- The validator now accepts only the legacy gate-first mode or the explicit one-shot mode; in one-shot mode it requires active `P1C01-ONE-SHOT-FINISH` plus `P1C01_ONLY` runtime authority during offline saturation.
- Evidence remains **SOURCE-IMPLEMENTED / HOSTED VALIDATION PENDING** until the new exact-head hosted run completes.

## 2026-10-06 - Final sweep governance regressions are now guarded

- The hosted whole-game sweep now also fails if DEC-104 one-shot execution drifts back to the older execution identity, if the owner-facing P1C01 lane and technical W01 lane are conflated, or if current REQ-PERF-001 texture truth regresses to the obsolete 24-BMP inventory statement.
- Historical external-review records are intentionally preserved as historical snapshots; only current authoritative implementation truth is required to say 0 tracked BMP.
- This turns the two concrete governance drifts found during the final audit into regression guards rather than one-time manual fixes.

## 2026-10-06 - Frodo source-contract stale SHA root correction

- Exact-head Pre-Unreal progressed through core/governor/deep audits and exposed one stale source-contract assertion: `test_p1c01_targeted_quaternius_animation_intake_is_one_pack_only` still hard-coded the superseded Frodo normalized SHA `eff0e799...`.
- The authoritative technical winner remains the tracked KayKit Rogue normalized FBX with SHA `75d715f6ce4673a650a4382bc4f86b7ae0baf0fe548cc63f9b6ded1800f669be`.
- Root fix removes the isolated historical assertion: the test now cross-checks `P1C01CharacterRigAnimationPrepV1.json` against `SourceAssets/ValidatedRuntime/FRODO/provenance.json`, then pins the current winner SHA. Future winner changes must update provenance and preparation truth together rather than leaving a hidden test constant.
- Status: **SOURCE-IMPLEMENTED / exact-head hosted proof pending**.

## 2026-10-06 - Offline audit failure diagnostics hardened

- The final hosted whole-game audit is fail-closed and now preserves its complete stdout/stderr as a short-lived GitHub artifact on every run, including failures.
- Bash `pipefail` keeps the Python audit exit code authoritative; the diagnostic artifact cannot turn a failed audit green.
- This removes a control-plane blind spot where GitHub's job-log download endpoint could temporarily return BlobNotFound and hide the exact static failure code from the architect.
- Evidence boundary remains static/hosted only.

## 2026-10-06 - Frodo deformation gate metadata reconciled

- Final sweep found a second stale Frodo metadata surface: `Data/P1C01HumanDeformationGateV1.json` still exposed the superseded `eff0e799...` / 161-bone predecessor as operational metadata even though the current winner is the tracked 48-bone KayKit Rogue derivative.
- The gate now points operationally to SHA `75d715f6ce4673a650a4382bc4f86b7ae0baf0fe548cc63f9b6ded1800f669be`, 48 bones, T0 reference pose, and the established STATIC_DEFORMATION_STRESS_PASS displacement evidence.
- The old 161-bone predecessor is retained only inside an explicitly `HISTORICAL_SUPERSEDED` snapshot so rejection/history evidence is not erased.
- Source-contract regression coverage now requires deformation-gate winner == tracked Frodo provenance winner and 48-bone/T0 truth.
- Fresh exact-head UE4 runtime/render/human evidence remains pending.


## 2026-10-06 - Final comprehensive static cleanup / Closure #40 reconciliation

- PR #329 source head audited for this cleanup: `591cebb1000984cec62141f516d4018d646c939f`.
- `P1C01 Chapter Closure Pack #40` (run `37429971478`) completed successfully on that source head. Its exact checkout, `Verify runner session health`, fast closure preflight and Mega Pack V2 steps all succeeded. This is runner/session + source-closure evidence only.
- The red hosted/prerequisite runs on the same source head did not execute a single workflow step; downstream UE jobs were skipped where applicable. They are classified **CI PRE-STEP INFRASTRUCTURE/SETUP / EXACT CAUSE UNAVAILABLE**, not validator failure and not UE compile/runtime failure.
- Full ShireJourney C++ static risk sweep found no `StaticLoadObject`, no `LoadSynchronous`, no runtime `.obj` path and no runtime `.bmp` path. Direct `LoadObject` use found by the sweep is Engine BasicShapes fallback content only.
- P1C01 Ferry ownership is coherent: `FerryEscape stage 2` + `FerryEscapeComplete` + `WC_P1C01_FERRY_END` remain inside P1C01; neither the ferry trigger nor restored-terminal repair auto-opens `P1C02 / RoadToBree`.
- Reviewed `ShireGameMode` P1C02 `StartChapter` calls are non-shipping runtime audit harnesses, not live auto-open gameplay. `AChapterWorldRouter` scans are transition cleanup, while `ALivingWorldDirector` remains bounded/pool-based and commit-synchronized.
- Branch inventory is clean for the current policy: `main`, `develop`, active P1C01, archive recovery, and the two unique Edoras prep branches remain. The Edoras branches carry unique source-prep work and are intentionally preserved.
- No gameplay/world/architecture C++ was changed merely for cleanup because no causal defect was proven in the reviewed paths.
- Remaining evidence is explicit, not hidden: fresh hosted/static execution after this stabilization commit; UE4.27.2 compile/import/package; Frodo runtime; seven remaining named-character final FBX bundles; production WAV import/playback; full P1C01 mission/save/retry/skip/backtrack pass; target-device profiling; and human Gate 6/7 review.
- Current evidence state after this packet: **STATIC-RISK-AUDITED / SOURCE-CLOSURE-RUN-PROVEN; COMPILE/PIE/DEVICE/VISUAL/PERFORMANCE/GATE 6/7 PENDING**. P1C02 remains locked.


## 2026-10-06 - Closure retrigger churn root fix

- A documentation/governance-only synchronize on PR #329 still launched P1C01 Chapter Closure Pack #41 because GitHub pull-request path filtering continues to see closure files already present in the accumulated PR diff.
- Root fix is in the closure workflow itself: after exact checkout it classifies the latest event delta against the six closure payload inputs. If none changed, runner-health/preflight/Mega Pack steps are skipped; manual dispatch and missing delta-base identity remain fail-safe full runs.
- This prevents later docs/static stabilization commits from needlessly repeating an already-proven multi-hour source closure train while preserving fail-closed execution when closure payload really changes.
- Evidence boundary: **SOURCE-IMPLEMENTED CI ROOT FIX / fresh workflow execution pending**. No UE4, PIE, device, visual or performance state changes.


## 2026-10-06 - Closure guard definition repair

- Closure #42 failed at workflow-definition time before any job existed because the first anti-churn edit malformed the YAML while composing the embedded PowerShell block.
- This was an orchestration-source defect introduced by the cleanup packet, not a runner, validator, game-code or UE4 failure.
- The workflow was rebuilt from the last known-good Closure #40 definition, then the delta classifier was reapplied with structural checks confirming exactly one classifier, runner-health, preflight, Mega Pack and cleanup step.
- Evidence boundary: **SOURCE-REPAIRED / fresh workflow execution required**. No runtime acceptance is implied.


## 2026-10-06 - Hosted classifier outage bypass without gate weakening

- Closure #43 proved the self-hosted runner was accepting work and exact checkout succeeded, then failed only in the newly added delta classifier. Root cause from the job log: PR execution used the temporary merge SHA instead of the PR head, and PowerShell `ErrorActionPreference=Stop` terminated on `git cat-file` stderr before the intended fetch fallback.
- The closure workflow now targets `github.event.pull_request.head.sha || github.sha` and performs an explicit bounded fetch of the delta base before diff classification.
- Separately, GitHub-hosted jobs continue to fail with zero executable steps before any validator logic runs. Unreal Build Validation is therefore fail-closed but non-blocking: hosted classification stays preferred; if that job itself fails before producing a valid mode, the self-hosted UE4 job performs the same `classify_unreal_validation.ps1` after exact-head checkout and runner-health verification.
- This is not a gate bypass. The same classifier still decides full/core/asset/acceptance/inherit. It only moves classification onto the available runner when GitHub-hosted infrastructure supplies no executable job.
- Current goal remains immediate P1C01 engine execution. P1C02/Bree remains locked.
- Evidence boundary: **SOURCE-IMPLEMENTED CI ORCHESTRATION FIX / fresh exact-head workflow proof pending**.


## 2026-10-06 - Closure workflow rebuilt again from #40 after #44 parse failure

- Closure #44 failed at workflow-definition time before any job. Inspection showed the previous text patch had duplicated/misplaced the classifier block even though the intended logic was correct.
- The closure workflow has now been rebuilt again from the exact known-good #40 source, with only three controlled changes: exact PR-head identity, explicit delta-base fetch, and conditional skip of runner-health/preflight/Mega Pack when no closure payload changed.
- Structural verification before commit: exactly one checkout, classifier, runner-health, preflight, Mega Pack and cleanup step.
- This corrects the prior documentation wording that treated the anti-churn definition as already repaired. Fresh workflow execution is still required.


## 2026-10-06 - P1C01 One-Shot gameplay execution begins: F1-02/F1-03 source gaps wired

- P1C01 is now in direct chapter execution, not another planning/cleanup wave.
- Source review confirms F1-02 requires investigation tutorial, packing and stealth departure; F1-03 Shire ownership requires road hiding/environmental hiding and FerryEscape while Bree remains P1C02.
- A real runtime-authoring defect was found: P1C01 urgency suppression disabled every side activity during `RingSecret`, `LeavingHome`, `KeepOffRoad` and `FerryEscape`, making the required F1-02/F1-03 optional gameplay impossible to express through the existing side-activity system.
- Root fix keeps fail-closed main-quest priority but adds two explicit data fields: `required_active_quest` and `allow_during_p1c01_urgency`. Urgency exceptions are accepted only when both are present; ordinary optional content remains suppressed.
- New P1C01 runtime-authored loops: `SIDE_SHIRE_RING_INVESTIGATION`, `SIDE_SHIRE_BAG_END_PACKING`, `SIDE_SHIRE_STEALTH_DEPARTURE`, and `SIDE_SHIRE_ROOT_HIDE`.
- `AShirePrototypeWorldBuilder` now places bounded three-gate challenges for all four loops. Investigation/packing do not advance the story; stealth departure and RootHide require crouch. Their availability is still owned by `UShireQuestSubsystem`.
- Four matching Journey Discovery rewards were added; all are first-time/idempotent, story_effect=NONE, cannot advance required anchors, and cannot change canon.
- F1-03 still terminates P1C01 at `FerryEscapeComplete / WC_P1C01_FERRY_END`; no Bree runtime was opened.
- Evidence state: **SOURCE-IMPLEMENTED / STATIC CONTRACTS ADDED / fresh exact-head compile+runtime proof pending**. No PIE/device/visual/performance/Gate 6/7 acceptance is claimed.


## 2026-10-06 - Root Hide main-path bypass closed

- Live-head review found that `SHIRE_ROOT_HIDE` existed as a crouched challenge, but the main `HideUnderRoad` quest trigger did not yet require its completion. A player could therefore advance `KeepOffRoad` by entering the trigger without completing the intended hiding sequence.
- Root fix: `HideUnderRoad->RequiredSideStoryBeat = Side_RootHideMasteryComplete`.
- `AShireQuestTrigger` already re-evaluates an overlapping player when a story beat is published, so completing the challenge releases the existing main trigger without polling or a second authority.
- Static source-contract coverage now asserts the gate explicitly.
- Evidence boundary: **SOURCE-IMPLEMENTED / STATIC-CONTRACTED; exact-head UE4 runtime proof pending**.


## 2026-10-06 - P1C01 packaged-startup imported-material cook blocker root fix

- Exact prior UE baseline `906131be878f2ec8ebe82ff22814061099711908` compiled ShireJourneyEditor, imported 384 production files with 0 failures, passed Automation QA, headless startup, chapter audits, route/state/fault/persistence audits, built the Windows package, and verified all 37 packaged runtime Data JSON files.
- Packaged launch then failed because the P1C01 streaming bank could not resolve four imported material instances: `MI_Sh_DirtSoil_PH`, `MI_Sh_StonyPath_PH`, `MI_Sh_TreeBark_PH`, and `MI_Sh_MossStone_PH`.
- Root cause: these packages are referenced through soft paths stored in runtime JSON, which UE4 cooker dependency discovery does not treat as package references. Existing packaging settings did not include `/Game/Production/Imported/P1C01Materials`.
- Root fix adds that bounded chapter material folder to `DirectoriesToAlwaysCook`. Runtime loading remains soft/async through `UShireChapterAssetStreamingSubsystem`; no synchronous fallback or broad warehouse residency is introduced.
- A regression contract now proves the P1C01 bank contains exactly those four imported soft material identities and packaging explicitly cooks their folder.
- Evidence boundary: **SOURCE-IMPLEMENTED ROOT FIX / fresh exact-head cook+packaged-launch proof pending**. Prior-head engine proof applies only to its SHA; current-head PIE/device/visual/performance/Gate 6/7 remain pending.


## 2026-10-06 - Final static cleanup stabilization / exact-head engine reconciliation

- Cleanup baseline: PR #329 exact head `9706cc72367be7e8dd14422808abba63597c8511`.
- Fresh runner evidence exists on that exact head from Unreal Build Validation #1654 self-hosted job `112468931752`: `RUNNER_HEALTH_PASS identity=IDEAPAD320\\user sessionId=2 listenerPid=69276 workerCount=1`.
- The self-hosted job completed UE4.27.2 ShireJourneyEditor compile, production import, Automation QA, headless P1C01-P1C08 chapter/state/fault/persistence audits, Windows package, `37/37` packaged runtime Data verification and a 6-second packaged-startup observation.
- The aggregate workflow is red only because its GitHub-hosted classifier failed before executable steps. Pre-Unreal #2060 and Whole Game Offline Saturation #41 likewise failed before executable steps and produced no validator evidence.
- Root-fix: `Scripts/audit_whole_game_offline_saturation.py` incorrectly required the temporary DEC-105 outage exception to remain `ACTIVE_WHILE_UE4_RUNNER_UNAVAILABLE` after the Governor had deactivated it on proven runner return. The audit now accepts only the governed active/inactive states and requires explicit runner-return evidence when inactive; source-contract regression coverage was added.
- Governor, runner handoff, character-prep blocker, audio-master status and offline-saturation status were reconciled to current truth. P1C01 remains the sole runtime-changing chapter.
- Ferry ownership remains unchanged: `FerryEscape stage 2 -> FerryEscapeComplete -> WC_P1C01_FERRY_END`. No P1C02/RoadToBree auto-open path was reintroduced.
- Source boundary remains explicit: F1-03 locks the eventual canonical postcondition “Hobbits reach Bree”; runtime topology keeps P1C01 ending at Ferry and P1C02 owning Bree arrival, so Ferry completion alone is not recorded as full F1-03 completion.
- Remaining blockers are content/human/device evidence: Frodo character-specific render/runtime proof, seven final production FBX character bundles, production WAV masters/playback, full human P1C01 gameplay/reliability, target-device measurements and Gate 6/7.
- Evidence boundary for `9706cc72367b`: **COMPILE/IMPORT/PACKAGE/HEADLESS-RUNTIME PROVEN**. Human PIE, DEVICE-TESTED, VISUALLY-ACCEPTED, PERFORMANCE-ACCEPTED and Gate 6/7 remain **NOT CLAIMED**. This stabilization commit itself requires fresh static validation after publication.


## 2026-10-06 - Frodo exact-head hosted-preflight fallback hardening

- The next required P1C01 character lane was blocked before UE4 execution because `P1C01 Frodo UE4 Animation Import` required a GitHub-hosted preflight job, and that hosted job is currently failing with zero executable steps.
- Root-fix keeps the hosted preflight preferred, but allows the self-hosted UE4 gate to start when the hosted job itself fails. On fallback, the Windows job performs exact-head checkout, resolves an existing local Python interpreter, re-runs the static Frodo import contract, re-downloads the exact historical rig/retarget artifacts, re-verifies all SHA256 bytes, builds ShireJourneyEditor and performs the existing 48-bone technical import checks.
- A real hosted validation failure cannot silently promote content: the fallback repeats the static contract and the downstream exact-byte/UE4 checks remain fail-closed.
- This is CI availability hardening only. Frodo remains **NOT VISUALLY ACCEPTED / NOT PIE-TESTED / NOT DEVICE-TESTED** until new evidence exists.


## 2026-10-07 - Closure checkout anti-waste root fix

- P1C01 Closure #49 exposed a real runner-efficiency defect: the workflow fetched the exact head quickly, then spent almost twelve minutes materializing a working tree before discovering `run=False reason=no-closure-input-delta`.
- Root cause: closure classification happened after working-tree checkout, and repository Git LFS filters apply to FBX/PNG/WAV/uasset/umap/exr paths.
- Root fix: build only a lightweight Git object graph first with `GIT_LFS_SKIP_SMUDGE=1`, classify the exact base/head delta before any checkout, skip checkout entirely when no closure payload changed, and when closure work is required checkout with LFS hydration still disabled because the closure source train consumes manifests/scripts and persistent Warehouse state rather than repository binary payloads.
- New Pre-Unreal contracts enforce classifier-before-checkout and reject any `git lfs pull` in this closure workflow.
- This is runner-throughput infrastructure only; no gameplay, world, story, asset-residency or acceptance claim changed.


## 2026-10-07 - Frodo technical import proven / render lane fallback hardening

- Exact head `f652af9d20e724d5990eaf3d7e4f8382d59e70a5` now has successful self-hosted Frodo UE4.27.2 technical import evidence from `P1C01 Frodo UE4 Animation Import #113`, job `112508429836`.
- Exact log markers include `P1C01_FRODO_HOSTED_PREFLIGHT_FALLBACK_PASS`, `P1C01_FRODO_UE4_ANIMATION_WINDOWS_HASH_PASS`, `UE4_ANIMATION_IMPORT_TECHNICAL_PASS clips=3 bones=48`, `P1C01_FRODO_UE4_ANIMATION_IMPORT_GATE_PASS`, `P1C01_FRODO_UE4_ANIMATION_EVIDENCE_PASS` and `P1C01_FRODO_RUNTIME_SOURCE_TRACKED_PASS assets=4 mutation=no`.
- The same exact head also completed the self-hosted Unreal Build Validation #1657 engine chain successfully: compile/import/Automation/headless chapter+state audits/package/packaged startup all passed inside job `112514218554`. Aggregate workflow red remains hosted-classifier infrastructure only.
- This promotes Frodo from technical-source-only to **UE4 TECHNICAL IMPORT PROVEN** for the 48-bone rig + Idle/Walk/Run package path. It does **not** promote Frodo to human visual, PIE, device or performance acceptance.
- Next blocker was `P1C01 Shire Render Capture`: hosted visual classifier zero-step failure caused both inherit and capture jobs to skip. Root-fix makes hosted classification preferred, but on hosted failure the self-hosted render job runs a lightweight no-LFS classifier. Only an actual/fail-safe visual delta is allowed to trigger heavy checkout/LFS/build/capture; an unchanged tree records an inherited boundary and exits without waste.
- No gameplay/world/story authority changed; P1C02/Bree remains locked.


## 2026-10-07 - Character lane scope correction after Frodo technical import

- Frodo exact-head UE4 technical animation import is now proven on `f652af9d20e724d5990eaf3d7e4f8382d59e70a5`: 48-bone linked skeleton, exact tracked rig/Idle/Walk/Run hashes, generated packages and technical gate all passed.
- A stale character-planning defect was removed: `P1C01CharacterRigAnimationPrepV1.json` still prioritized Aragorn/Gimli/Legolas/Boromir inside the active P1C01 character list while omitting Bilbo/Black Rider/horse. Active priority is now exactly Frodo, Bilbo, Gandalf, Sam, Merry, Pippin, Black Rider and Black Rider horse. Later Part-I characters remain preparation-only and cannot steal P1C01 runtime/source priority.
- `P1C01HumanCharacterProductionWave2V1.json` still exposed its historical 161-bone winner as `latest_technical_winner`. It now records the current tracked 48-bone Frodo exact-head import as latest and marks the old source-factory transition superseded for Frodo.
- Frodo is still not visually accepted. Current character gap is seven final production FBX bundles plus Frodo rendered/human review.
- Regression coverage now enforces the exact eight-character P1C01 priority set and current 48-bone winner metadata.


## 2026-10-07 - Render fallback parser root-fix + character-intake trigger repair

- Render Capture #219 reached the self-hosted fallback but failed before classification with a PowerShell parser error. Exact defect: malformed regex token `-notmatch '^0+){` left the string unterminated.
- Root-fix restores the intended `-notmatch '^0+$'` condition and replaces the inline `git show` target interpolation with an explicit `$targetSpec` string before extraction.
- A second production-flow defect was corrected: `Data/P1C01CharacterRigAnimationPrepV1.json` is the manifest consumed by `prepare_p1c01_character_rig_intake.ps1`, but it was missing from P1C01 Closure workflow triggers and closure-delta inputs. Character-priority/source changes could therefore skip Character Intake entirely.
- Closure now treats that manifest as a closure-relevant input in push, PR path filtering, and runtime delta classification.
- Regression contracts assert the render fallback parse-safe tokens and the character-prep closure dependency.
- Evidence boundary: **SOURCE-IMPLEMENTED root fixes only until fresh exact-head workflow execution**.


## 2026-10-07 - Render workflow full root-rebuild after structural corruption

- Follow-up inspection found the prior render fallback file had duplicated tail content in addition to the PowerShell parser defect. The malformed duplicate started after the first complete upload block and made the workflow structurally invalid.
- Root repair is a full clean rebuild of `.github/workflows/p1c01-shire-render-capture.yml` from the last known-good three-job structure, then re-application of the fail-closed self-hosted classifier fallback exactly once.
- The rebuilt workflow has one `classify`, one `inherit`, one `capture` job, one fallback classifier step and one rendered-evidence upload step.
- Hosted classification remains preferred. Hosted zero-step failure routes to a lightweight self-hosted Git/LFS-smudge-disabled classification. Heavy checkout/LFS/build/capture happens only when the classifier requires fresh visual evidence.
- Regression tests now assert singular job/block structure in addition to the parse-safe `'^0+$'` condition and explicit `$targetSpec`.
- Evidence boundary: **SOURCE-IMPLEMENTED structural root repair; fresh exact-head workflow proof pending**.


## 2026-10-07 - Frodo import anti-repeat classifier

- Exact-head Frodo technical import is already proven for the tracked 48-bone rig and Idle/Walk/Run bundle.
- Because the Frodo workflow file is part of the long-lived PR diff, GitHub may schedule the workflow again on unrelated PR synchronizations. That was causing redundant self-hosted checkout/build/import work.
- The self-hosted Frodo gate now performs a lightweight Git delta classification before checkout. Only changes to the Frodo validated-runtime bundle, Frodo import commandlet/editor-tools tree, relevant build/runner scripts, Config/uproject, or the workflow/contract itself require a fresh heavy import.
- Unrelated changes record `P1C01_FRODO_IMPORT_INHERITED` and skip checkout, artifact download, build, import, package verification and cleanup work.
- This inherits technical evidence only. It never upgrades human visual/PIE/device/performance acceptance.


## 2026-10-07 - P1C01 visual bottleneck root-fix: persistent Frodo + production materials

Fresh exact-head render evidence on `e85e7be9dc619d24063dc5b89c55267a801a5eaa` proved the render pipeline itself works: six DX11 1280x720 captures were produced and uploaded, and the self-hosted UE4 render job completed successfully. Human visual acceptance is **not** granted because the captures/logs exposed real production blockers.

Root causes from the capture logs:
- `CharacterRigStreaming: unavailable id=Frodo reason=core-packages-missing fallback=modular`: the tracked 48-bone FBX technical winner was being imported only in a transient technical gate, then removed, so normal production import/render did not have persistent Frodo UE packages.
- `M_ProductionFoliage ... Failed to compile Material` with `SimpleGrassWind: Missing function input 'AdditionalWPO'`: foliage fell back to the UE default material.
- `M_ProductionFoliage` and `M_ProductionSurface` reported missing `bUsedWithInstancedStaticMeshes=True`, causing HISM/ISM material fallback/recompile debt.

Root repair:
- Normal production import now verifies/hydrates only the exact tracked Frodo FBX bundle, enforces the known SHA256 identities, runs `ShireFrodoAnimationImport`, and persists the skeletal mesh/skeleton/Idle/Walk/Run packages in the active production workspace.
- Frodo rig/animation folders are explicitly included in cook because runtime soft paths/JSON do not create hard cook dependencies.
- Production surface/foliage/far-foliage masters are explicitly enabled for Instanced Static Mesh usage.
- `SimpleGrassWind` now receives an explicit zero `AdditionalWPO` input; existing generated foliage masters are repaired deterministically on import.
- Render Capture is upgraded from “six screenshots exist” to a fail-closed production-readiness gate: it fails if Frodo core packages are missing, if production foliage compile falls back, if instanced-mesh usage warnings appear, or if the skeletal Frodo production rig is never observed active.

Evidence boundary: **SOURCE-IMPLEMENTED root fix** on top of previously proven UE4 compile/import/package/headless evidence. Fresh exact-head render is required before claiming the visual blockers are closed. No PIE/device/visual/performance/Gate 6/7 acceptance is claimed.


## 2026-10-07 - Frodo render identity gate correction

- Runtime character streaming uses the stable gameplay id `Frodo`, while the content folder token is `FRODO`. The first strict render gate accidentally searched for `CharacterVisual: skeletal production rig active id=FRODO`, which cannot match the player runtime log emitted from `TryApplyProductionRig(VisualId.ToString())`.
- The render gate now requires both exact runtime signals before the six-shot evidence can pass:
  - `CharacterRigStreaming: ready id=Frodo`
  - `CharacterVisual: skeletal production rig active id=Frodo`
- It still fails immediately on `core-packages-missing`, production material compile failure, or missing instanced-static-mesh material usage.
- This prevents a false red from identifier casing while also strengthening the evidence requirement from “package absent warning not seen” to “async rig actually became ready and active.”
- Fresh exact-head execution is still required. No visual/PIE/device acceptance is claimed from this source correction.


## 2026-10-07 - Frodo pre-import hydration dependency closed

- The normal production import already persists the proven Frodo 48-bone rig + Idle/Walk/Run packages.
- The P1C01 hydration pass now explicitly pulls the four tracked `SourceAssets/ValidatedRuntime/FRODO/*.fbx` LFS objects before the runner scrubs credentials or starts UE import.
- The exact four known SHA256 identities are verified immediately after hydration.
- This closes the remaining pointer/stale-binary risk in the production path. Fresh exact-head UE4 import/render evidence is still required.


## 2026-10-07 - Unified Unreal/Render execution lane to remove duplicate heavy work

The single self-hosted UE4 runner was spending time twice on the same exact head: the standalone Shire Render workflow performed its own checkout/build/production import, then Unreal Build Validation repeated checkout/build/import before QA/package.

The P1C01 render is now integrated into the existing Unreal Build Validation workspace immediately after production import. `ci_capture_p1c01_visuals.cmd` supports `SHIRE_SKIP_PRODUCTION_IMPORT=1` so the integrated lane reuses the already-built editor and already-imported production assets. Render evidence is uploaded from the same Unreal run.

The standalone `P1C01 Shire Render Capture` workflow remains available only through manual dispatch for diagnostics; it no longer auto-runs on every PR synchronize/push.

This is a runner-throughput change only. It does not weaken the fail-closed presentation gate or acceptance boundary.


## 2026-10-07 - Active production lane focus after Unreal/Render unification

- The automatic Shire render now reuses the exact Unreal Build workspace after production import, removing the second editor build/import previously required by the standalone render job.
- To stop historical/outage pipelines from creating repeated red noise on every PR synchronize, six lanes are now manual-only while the active UE4 runner is available: Human Wave 2, Frodo Hosted Retarget, Frodo Animation Source Inventory, Material Surface Promotion, P1C01 Offline Saturation, and Whole Game Offline Saturation.
- These lanes remain available through manual dispatch if the current winner is invalidated, source regeneration is explicitly needed, or the runner becomes unavailable.
- Automatic heavy work is now concentrated on Unreal Build + integrated Shire render, with Closure/Character Intake remaining delta-gated.
- No acceptance claim is changed by this scheduling correction.


## 2026-10-07 - Frodo persistent package file gate

- The normal production-import path already persists the tracked 48-bone Frodo rig plus Idle/Walk/Run through the UE4 commandlet.
- The gate now verifies the five expected .uasset files physically exist on disk immediately after commandlet success instead of trusting log markers alone.
- Exact required files: skeletal mesh, skeleton, Idle, Walk and Run packages under Content/Production/Characters.
- This change exists to trigger and harden the current unified Unreal build/import/render proof. It is not visual/PIE/device acceptance.


## 2026-10-07 - Definitive P1C01 automatic train consolidation

PR #329 now consolidates automatic heavy execution around the existing Unreal Build Validation self-hosted workspace. The historical Closure, dedicated Frodo UE4 import and hosted Pre-Unreal roots are skipped for this definitive PR branch while remaining available outside it/manual pathways. The Unreal hosted classifier is also skipped here; its existing fail-closed self-hosted classifier resolves the exact-head delta locally.

The same train now owns exact-head source/static contracts, UE4 build, persistent production import, integrated six-shot Shire capture on the already-imported workspace, runtime audits, package and packaged startup. This removes repeated build/import work and avoids hosted-startup red noise from determining the chapter's visible progress.


## 2026-10-07 - Definitive train playable output + KayKit precursor retirement

- The consolidated Unreal Build train is the sole automatic heavy P1C01 production path on the definitive branch: exact-head static gate, editor build, persistent Frodo production import, integrated six-shot render readiness gate, Automation/headless runtime audits, Windows package and packaged startup.
- A successful full run now uploads the packaged `Saved/W00Package/WindowsNoEditor` tree as `p1c01-playable-windows-<exact-head>` for direct owner inspection/play.
- The historical KayKit Rig Technical Bridge is retired from automatic PR execution on this branch because the current Frodo 48-bone tracked technical winner already supersedes that precursor. It remains available outside the definitive branch for explicit forensic/regeneration use.
- Evidence remains exact-head fail-closed: artifact availability does not imply DEVICE-TESTED, VISUALLY-ACCEPTED, PERFORMANCE-ACCEPTED or Gate 6/7 acceptance.


## 2026-10-07 - Definitive Unreal train non-cancelling completion rule

- The definitive P1C01 branch now lets an in-progress unified Unreal build/import/render/runtime/package run finish even when a newer commit arrives. This removes the observed cancel/requeue loop that repeatedly discarded useful UE4 work.
- Other PR branches keep normal superseded-run cancellation.
- The unified lane already produces integrated six-shot Shire render evidence and, on full success, uploads a playable Windows package artifact.
- This scheduling repair does not itself prove the current head; fresh completed engine evidence is still required.


## 2026-10-07 - One-Shot static gate Python path root fix

- Unreal Build #1674 did not fail in C++ or UE4.27.2. It stopped before engine execution in the exact-head One-Shot source gate because `Scripts/test_source_contracts.py` imports `source_contracts` as a sibling module while the workflow launched unittest from repository root without `Scripts/` on `PYTHONPATH`.
- Exact failure: `ModuleNotFoundError: No module named 'source_contracts'`, followed by `P1C01_ONE_SHOT_SOURCE_CONTRACT_FAIL exit=1`.
- Root fix: the self-hosted One-Shot gate now resolves `$GITHUB_WORKSPACE/Scripts`, prepends it to `PYTHONPATH`, preserves any existing Python path, and only then runs the source-contract suite and Pre-Unreal validator.
- Regression coverage locks the Python-path setup ahead of unittest execution.
- This is a CI harness repair only. It does not change gameplay acceptance status. The current production-material and persistent Frodo runtime fixes remain in the exact-head source and still require fresh engine/render proof after this gate is cleared.


## 2026-10-07 - One-Shot source-contract schema reconciliation

- One-Shot Build #1675 confirmed the Python module-path repair: `source_contracts` imported correctly and the suite executed all 55 tests.
- The remaining stop was six stale assertions, not UE4/game failure:
  - streaming plan test still expected removed `chapter_banks/P1C01/FrodoMain` schema instead of current `banks/P1C01/assets`;
  - animation-intake test expected obsolete `stage_scope=ONE_PACK_ONLY` even though Frodo now owns a tracked exact-head validated runtime core;
  - character-presentation and quest-side-activity tests expected older generic status strings instead of the current explicit progress states;
  - KayKit test expected the pre-retirement exact `if` line instead of the stronger definitive-train retirement guard;
  - render-readiness test expected `id=FRODO` while runtime evidence uses `id=Frodo` and `findstr /I` is intentionally case-insensitive.
- The tests were reconciled to current schemas/statuses while preserving their safety intent: four imported P1C01 material soft paths still must be cooked, Frodo remains 48-bone/Idle-Walk-Run tracked, rejected KayKit payloads stay non-requeueable, render capture still rejects fallback Frodo/default materials, and no acceptance boundary is weakened.
- Fresh exact-head One-Shot execution is required after this test-only reconciliation.


## 2026-10-07 - Final source-contract placement correction

- One-Shot Build #1676 reduced the static gate to exactly two failures.
- Both were test-reconciliation placement mistakes: the persistent-Frodo status assertion had been applied to the Party Social Loop test, while Character Presentation still expected its prior generic status.
- Party Social Loop remains `SOURCE_IMPLEMENTED_EXACT_HEAD_PROOF_PENDING`; Character Presentation is correctly `FRODO_PERSISTENT_RUNTIME_IMPORT_SOURCE_IMPLEMENTED_RENDER_REPROOF_PENDING`.
- No production/gameplay/runtime source changed in this correction.
- Fresh exact-head One-Shot execution remains required before engine evidence can advance.


## 2026-10-07 - One-Shot pipeline root fix: persistent-runner-safe validation and queue isolation

- Build #1677 proved the full 55-test source-contract suite is green; the remaining stop was Pre-Unreal validation drift plus one discovery-declaration model gap.
- Root fixes:
  - generated build directories are now rejected only when **Git-tracked**, not merely because `Binaries/DerivedDataCache/Intermediate/Saved/.vs` exist on the persistent self-hosted runner;
  - Journey discovery validation now treats `ContextualSideActivityPlan.discovery_reward_id` values as declared discoveries alongside exploration-envelope discoveries, matching the implemented Ring investigation / Bag End packing / stealth-departure / Root Hide loops;
  - Unreal concurrency again cancels superseded runs from the **same PR branch**, eliminating obsolete builds queued behind newer heads while branch-specific groups preserve unrelated work;
  - rendered-evidence and playable-package artifact uploads are non-blocking transport steps so storage/quota failures cannot mask engine/logging truth.
- PG-026/PG-167 validators were updated to enforce the stronger current semantics rather than obsolete exact strings.
- No gameplay/story/world authority was weakened. P1C02 remains locked.


## 2026-10-07 - Final queue-policy test reconciliation

- Build #1678 reduced the One-Shot source gate to one failure.
- The remaining failure was an obsolete test named `test_p1c01_definitive_unreal_run_is_non_cancelling`, which demanded the exact branch exception that had been removed to stop superseded builds consuming the single UE4 runner.
- The test now asserts the intended safe policy: concurrency remains scoped by repository + PR branch, while `cancel-in-progress` is true for pull requests so only superseded work from the same branch is cancelled.
- No production/runtime source changed.


## 2026-10-07 - Chronicle side-discovery authority + runner-health ordering root fix

- Build #1679 reduced Pre-Unreal to five failures with two shared roots.
- PG-085 now has an explicit source-of-truth for contextual side-activity Chronicle labels. The four P1C01 side-only discovery rewards now carry `discovery_display_label` directly in `ContextualSideActivityPlan.json`, matching the corresponding `JourneyDiscoveryRewardPlan.display_label`.
- PG-145B now validates the real first heavy self-hosted action: runner health must precede P1C01 LFS hydration. The Unreal workflow order was changed to verify the interactive/watchdog-owned runner session immediately after exact checkout, then hydrate bounded LFS content.
- This removes unnecessary heavy I/O when the runner session is unhealthy and preserves the side-activity Chronicle provenance contract without relaxing display-label coherence.
- No canon outcome, quest authority, world density or chapter boundary changed.


## 2026-10-07 - PG-085 side-only discovery label authority refinement

- Unreal Build #1680 passed exact checkout, runner-health-before-hydration, bounded LFS hydration and the 55-test source-contract suite.
- Its remaining Pre-Unreal blocker was PG-085 overreach: contextual activities whose discovery IDs already exist in `ExplorationEnvelopePlan` were incorrectly required to duplicate `discovery_display_label`.
- Root rule is now single-owner and fail-closed: `ExplorationEnvelopePlan.label` remains authoritative for exploration-declared discoveries; only contextual **side-only** discovery IDs require `ContextualSideActivityPlan.discovery_display_label`. If both are authored they must match.
- The four P1C01 side-only discoveries retain explicit labels matching `JourneyDiscoveryRewardPlan.display_label`.
- No gameplay, canon, chapter, streaming or acceptance state changed. Fresh exact-head One-Shot engine proof remains required.


## 2026-10-07 — P1C01 render-evidence calibration remediation

- **Observed exact-head evidence:** Unreal Build Validation #1681 on 7bae402f8726addd577a838e074ce4ed04bc91de succeeded through real UE4.27.2 build, production import, six rendered captures, Automation Framework/runtime audits, Windows cook/package and packaged startup. This is technical/playable evidence only.
- **Visual finding:** all six integrated captures were obstructed by an uncalibrated, oversized skeletal Frodo. The captures therefore cannot be used as visual-quality or character-presentation acceptance.
- **Root-level remediation:** the production skeletal attachment now converts the validated metre-space source to Unreal centimetres (0.010) at the mesh boundary and aligns it to the active collision capsule. It does not alter quest, route, save, collision, streaming ownership, NPC context, or LivingWorldDirector population authority.
- **Regression gate:** the render-capture train now requires the Frodo calibration log before accepting a capture artifact.
- **Status:** implementation is pending fresh exact-head UE4 build/render evidence. No PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED, PERFORMANCE-ACCEPTED, or Gate 6/7 claim is made. P1C02/Bree remains locked.


## 2026-10-07 — P1C01 calibrated render evidence, exact-head result

- **Exact head:** b7521522b8085c88fed2adeb2a73f1aa64a512a4.
- **Unreal Build Validation #1682:** SUCCESS. Exact checkout, runner health, LFS hydration, static/source gate, UE4.27.2 C++ build, production import, integrated six-shot capture, Automation Framework QA, headless startup/chapter/story audits, warning-debt guard, Windows cook/package, package-data verification, packaged EXE launch and artifact upload all completed successfully.
- **Render evidence:** the capture logs observed `CharacterVisual: skeletal production rig calibration id=Frodo scale=0.010 capsuleHalfHeight=60.0`; Frodo no longer occludes the six views. This validates the calibration remediation in rendered evidence.
- **Visual disposition:** the unobstructed views still show a low-detail/blockout Shire and capture presentation with debug HUD/high overview framing. They are evidence for diagnosis, not production visual acceptance.
- **Next bounded production target:** replace prototype/blockout presentation across the six P1C01 checkpoints and produce a character-scale, HUD-free review route. Do not open Bree/P1C02.
- **Acceptance boundary:** STATIC/COMPILE/RUNTIME/PACKAGE evidence is current for this exact head; PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED, PERFORMANCE-ACCEPTED and Gate 6/7 remain unclaimed.


## 2026-10-07 — P1C01 review-route framing correction

- The prior six renders were technically clean after Frodo calibration, but the harness positioned the player 390–520 Unreal units above the Shire. That made the evidence an aerial overview instead of a production review at character scale.
- The capture harness now uses road-level actor Z values (75–105), a low review pitch, and `ShowFlag.HUD 0` / `ShowFlag.2D 0` for HUD-free screenshots. This is capture-only; gameplay camera, world coordinates, quest state and runtime authority are unchanged.
- Fresh exact-head UE4 evidence is required before judging visual quality again.


## 2026-10-07 — P1C01 HUD-free capture guard

- Road-level review captures succeeded, but the native Canvas HUD remained visible because `AShireHUD::DrawHUD()` is independent of the engine HUD show flag.
- Added a capture-only `-ShireVisualCapture` commandline guard inside `AShireHUD::DrawHUD()`. Normal gameplay HUD behavior is unchanged; review captures now omit quest card, bars, and debug journey counters.
- Fresh exact-head UE4 render evidence is required again. No visual acceptance or Gate 6/7 claim is made.


### P1C01 production presentation packet (2026-10-07)

The playable camera now uses a wider third-person composition (320 cm spring arm, 74° FOV, raised socket) and a bounded +1.25 exposure bias to reduce geometry clipping and underexposed Shire presentation in the actual runtime camera. This is a presentation improvement only; it does not establish VISUALLY-ACCEPTED, DEVICE-TESTED, PERFORMANCE-ACCEPTED, or Gate 6/7 acceptance. Fresh packaged evidence from the resulting One-Shot run is required.


### Camera packet corrective note (2026-10-07)

The first camera-presentation patch had a source line-ending serialization defect and was rejected by the C++ gate before Unreal execution. The source was corrected at commit `90a9c0d9`; fresh full One-Shot evidence is required. No visual or performance acceptance is claimed from the failed run.


### P1C01 world atmosphere pass (2026-10-07)

Runtime Shire atmosphere was adjusted in `ShirePrototypeWorldBuilder`: stronger warm sun/sky contribution, lower exponential fog density/opacity, and longer fog start distance. The intent is to make the playable Shire readable on the validated DX11 hardware profile while preserving bounded post-process cost. This remains a presentation pass; fresh build/render evidence is required and no VISUALLY-ACCEPTED or PERFORMANCE-ACCEPTED claim is made.


### P1C01 broad-surface material pass (2026-10-08)

The exact #1694 render was reviewed from the integrated artifact. Exposure and camera readability improved, but the six views still showed large flat-color green/white terrain surfaces and low-detail blockout presentation. The next production packet applies the already-verified P1C01 grass-path material locally to the broad ground, hill, and slope HISM components. It does not mutate the common asset bank, add synchronous loads, change collision, or increase actor density. Fresh exact-head UE4 build/render/package evidence is required; no visual, device, performance, or Gate 6/7 acceptance is claimed.


### P1C01 visual-delta classifier correction (2026-10-08)

The material packet changed Source/ShireJourney/Private/World/ShirePrototypeWorldBuilder.cpp, but #1695 correctly proved only the core lane because the classifier inherited the green parent and skipped capture/package. That evidence boundary is insufficient for a world-presentation change. The classifier now routes world-builder deltas through the full UE4 lane, forcing fresh six-shot render, cook/package, packaged startup, and artifact review. No visual, device, performance, or Gate 6/7 acceptance is inferred from #1695.


### P1C01 full-render trigger completion (2026-10-08)

The latest visual packet manifest is now also a full-lane trigger. This closes the last-commit classifier gap: a visual/material packet cannot inherit a core-only result merely because its world-builder source landed in the previous commit. The next exact-head run must include six fresh captures, cook/package, packaged startup, and artifact inspection. Acceptance remains unclaimed.


### P1C01 material packet runtime-stability root fix (2026-10-08)

Unreal Build Validation #1697 proved the broad-surface grass-path override was not runtime-safe on the validated DX11 runner: build and import passed, but the first HUD-free capture stalled before BeginPlay and failed with `screenshot_timeout` after 75 seconds. The override is removed from the large ground/hill/slope HISM components; the previously proven local Shire materials and bounded imported detail-material overrides remain. This is a root-fix commit only. Fresh exact-head render, packaged startup, performance, and human/device acceptance remain required; no visual, device, performance, or Gate 6/7 acceptance is claimed.


### P1C01 presentation composition and lighting packet (2026-10-08)

The #1698 artifact was technically complete but visual review still found low-detail blockout surfaces, close/occluded compositions, dark interior framing, and no visible character hero read in the six HUD-free views. The next packet adjusts only the review-route camera anchors and bounded runtime presentation: lower sun intensity, stronger sky fill, lighter/shorter fog contribution, controlled exposure, saturation, and contrast. Fresh exact-head capture/package evidence is required; this is not VISUALLY-ACCEPTED, DEVICE-TESTED, PERFORMANCE-ACCEPTED, or Gate 6/7 evidence.
