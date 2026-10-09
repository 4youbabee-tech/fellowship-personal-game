## 2026-10-09 — Asset-first #198 evidence and focused repair candidate
- Source wave #198 exact SHA d338e5ec1dbb completed SUCCESS; real log `P1C01_NEW_ONLY_SOURCE_SUMMARY new=191 new_bytes=3242599256 reused=0 deferred=3`, and `P1C01_MEGA_PROMOTION_PASS_WITH_MANUAL_QUEUE prepared=191 intakeQC=188 pending=3 manual=175 badReceipts=0`. These were *prepared warehouse entries*, not UE runtime imports, final visuals or necessarily unique upstream downloaded assets.
- 175 manual queue entries mostly stale C: Warehouse receipt paths while active root is D:. Correct canonical Warehouse-root rebasing before receipt selection; SHA256 is still required after rebasing. One KayKit archive source extracted to an overlong Windows destination; choose compact hashed extraction root only where safely necessary while retaining paths and ZIP bomb/traversal checks.
- Material source car: `P1C01_MATERIAL_INTAKE_PASS prepared=17 pending=9 manual=0` but previous arbitrary minimum 18 caused QUARANTINED. In AssetFirst only, export any >=1 receipt-verified valid material, retaining the original final-closeout 18 requirement. LFS branch publish remains contingent on actual credential, quota and safe export bytes; do not count prepared as published.
- Quaternius: `QUATERNIUS_WAREHOUSE_STAGE_ZERO_PAYLOAD_FAIL files=0 unresolved=17`, quarantine this provider without halting independent stock; no invented third-party download. Source wave overall had 8 PASS, 2 provider/material QUARANTINED, 0 infrastructure failures. Do not present SUCCESS of runner as all cars passing.
- CI policy: DEC-109 permanent maximum-eligible-new-only source batch and selective risk gates; no KayKit auto tests every PR. Full exact-head UE4, render, quest/save/package, human PIE/visual/pacing, device FPS and Gate6/7 remain P1C01 closeout tasks.
- Current correction is SOURCE-IMPLEMENTED only until next GitHub run produces quantified reused/new/qualified/export figures; no self-hosted UE4 character or human visuals proven by source wave.

## 2026-10-09 — DEC-109: P1C01 new-assets-first throughput / defer redundant admin (staged)
- Owner direction: **stop repeated global administrative audits and full builds for source-only additions; accumulate NEW eligible assets first**. The full chapter Unreal/PIE/visual/device/30FPS and Gate 6/7 acceptance is still mandatory when P1C01 is actually ready; impactful runtime changes retain targeted safety checks.
- Source-only `-AssetFirst` mode retains storage reserve/preflight, provider acquisition, selected SHA256 receipt-verified intake/promotion, character and material preparation. It defers the redundant `INVENTORY_AUDIT`, `SATURATION_REPORT`, `CRITICAL_GAP_PREP`, `PROVIDER_RESOLUTION` and `FINAL_INVENTORY_AUDIT` cars to full closeout. Global full-warehouse file enumeration is omitted from the asset-first report, not falsified as a known zero.
- Source promotion no longer truncates receipt candidates to legacy per-class First-N ceilings. For every new eligible source, validate the staged SHA, safe ZIP paths/formats and at least 6GiB free disk before extraction. Reuse only prepared outputs with previous source hash and every output file's SHA256/size still matching. Report NEW count/bytes separately from reused and deferred. Provider-local failures quarantine, not abort unrelated sources.
- KayKit #314 evidence: Mage skeletal import reported 48 bones/registered at 09:43:42 UTC, while generic importer entered unrelated `P1C01_FRODO_LFS_HYDRATE_BEGIN` at 09:43:49 UTC; `timeout-minutes: 90` interrupted at 11:07:21 UTC. Dedicated bridge now manual only, bounded at 45m, with isolated one-command Frodo bypass. Full ordinary production Frodo import remains required. The earlier missing smoothing warning is a separate technical candidate-rejection criterion.
- Dedicated new-only branch `production/p1c01-bulk-smart-ci-governor-2026-10-09` runs one source wave from the existing P1C01 chapter closure Workflow on its push; no heavy `pull_request` closure jobs. No active PR #329 mutation or job cancellation is required.
- **Evidence boundary:** Code/metadata only until the staging source wave returns real run/artifact. Not PIE/device/visually accepted, not proof of higher FPS or of final FBX character quality; no P1C02 runtime.

## 2026-10-09 — DEC-108 permanent qualified bulk production and Smart CI candidate
- Owner policy: all future Work sessions default to largest *qualified* chapter-scale batch and avoid micro-commit/heavy-UE churn. Existing Governor DEC-078/104 remain binding. Raise upload thresholds only after measured runner headroom/LFS quota, not arbitrary byte targets.
- Exact PR delta: Unreal classifier now compares the candidate with its direct Git first parent, not the PR integration base; unresolvable parent fails closed to full. Prior exact-head ancestor proof conditions and final P1C01 Gate 6/7 remain mandatory.
- Current KayKit Rig #314 and Unreal #1803 were active at audit; this work is isolated to separate branch, preserving the active P1C01 PR. No final art assets or new UE4 import results claimed.
- Proof: SOURCE-IMPLEMENTED / CI NOT YET EXECUTED. Human PIE/device/visual and target FPS still pending. P1C02 runtime locked.

## 2026-10-09 - P1C01 Bucklebury Ferry riverbank utility detail

- Added two resident `SM_CommonFishingRack` placements on the Bucklebury Ferry riverbanks through a single non-colliding `AWorldDetailCluster`, improving the worked-river crossing read without importing assets.
- The placements stay outside gameplay-owned crossing logic and do not move the ferry boat, dock segments, footbridge, quest triggers, route endpoints, save keys, NPC ownership, NavMesh or collision.
- Updated the Road Threat/Ferry canon contract and source test to account for two clustered utility instances while keeping limited hero actors at three and P1C02 locked.
- Evidence boundary: STATIC-VALIDATED source contract only until exact-head UE4.27.2 CI proof runs. No PIE, device, visual, performance or Gate 6/7 acceptance is claimed.

## 2026-10-09 - P1C01 Bucklebury Ferry dock segment boarding detail

- Added two resident `SM_CommonDockSegment` placements at the Bucklebury Ferry near/far landing through a single `AWorldDetailCluster`, improving the boarding-stage read with existing production geometry.
- The dock dressing is non-colliding, tagged for existing runtime cleanup, and does not move the Ferry boat, footbridge, quest triggers, route endpoints, NavMesh, save keys, story state or Bucklebury crossing collision.
- Updated the Road Threat/Ferry canon contract and source test to account for two clustered dock instances while keeping limited hero actors at three and P1C02 locked.
- Evidence boundary: STATIC-VALIDATED source contract only until exact-head UE4.27.2 CI proof runs. No PIE, device, visual, performance or Gate 6/7 acceptance is claimed.

## 2026-10-09 - P1C01 Bag End garden arch and mailbox dressing

- Added existing resident Shire production meshes for a Bag End garden arch and mailbox inside `AShirePrototypeWorldBuilder::SpawnBagEndHeroPass`, closing two visible `BAG_END_EXTERIOR_GARDEN` micro-detail slots without introducing new asset imports.
- The props are non-colliding hero dressing around the Bag End approach; no quest anchors, NPCs, save keys, NavMesh corridors, chapter transitions, synchronous loads, Tick, P1C02 activation or interior-completion claim changed.
- Added a focused source contract proving the resident asset paths and exact Bag End placements remain in the bounded Bag End hero pass.
- Evidence boundary: STATIC-VALIDATED source contract only until exact-head CI/UE4.27.2 proof runs. No PIE, device, visual, performance or Gate 6/7 acceptance is claimed.

## 2026-10-09 - P1C01 Party Field fireworks visual anchor alignment

- Repositioned the existing Party Field loaded-cart and paired barrel dressing inside `AShirePrototypeWorldBuilder::SpawnPartySocialLoopPass` so the already-authored props frame the `SHIRE_FIREWORKS_SAFETY` activity near Gandalf's fireworks beat.
- This is a placement-only runtime polish pass: no new meshes, no new HISM instances, no new actors, no collision changes, no quest/save/NavMesh movement, no synchronous loads and no P1C02 activation.
- Added a focused source contract proving the old distant cart placement is gone and the new party-field prop anchors remain inside the existing bounded party social loop.
- Evidence boundary: STATIC-VALIDATED source contract only until exact-head CI/UE4.27.2 build/import/render/runtime proof runs. No PIE, device, visual, performance or Gate 6/7 acceptance is claimed.

## 2026-10-09 — P1C01 Party Field static dressing HISM batch

- Reused the existing resident meshes in `AShirePrototypeWorldBuilder::SpawnPartySocialLoopPass` to batch the same 14 non-colliding static placements: six picnic tables, two benches, two canopies, one loaded cart, two barrels and one haystack.
- Grouped placements by `UStaticMesh*` into up to six existing `AWorldDetailCluster` actors. The source transforms, authored materials, dynamic-shadow flag and non-collision behavior are preserved; no placement or world density was added.
- Party setup/celebration state variants remain their current actors so their hidden/state transitions retain the existing owner and lifecycle. Quest anchors, save keys, NPC population, NavMesh and route ownership are untouched.
- Updated the existing cluster configuration to opt into dynamic shadows only for these Party Field props; other clusters keep the previous default. Generated clusters carry the existing cleanup tag.
- Validation boundary: focused source regression is required, then fresh exact-head UE4.27.2 proof. This change has no measured draw-call/FPS claim and does not prove PIE, target-device, visual, or Gate 6/7 acceptance. P1C02 remains locked.

## 2026-10-09 — P1C01 scenic-instancing optimization registered for existing production assets

- **Authorized chapter/scope:** Only P1C01, existing `AShirePrototypeWorldBuilder::SpawnScenicDetailPass`; no new chapter, story event, actor behavior, imported source, character animation or texture.
- **Source basis:** Source 03 Shire/Hobbiton pastoral hills, warm domestic scale, road/river spatial readability; existing `Data/P1C01VisibleWorldReuseBindingPacketV1.json`; programmer report's HISM/draw-call recommendation. Reuse already-resident Shire/Common FBX/static-source asset results through the existing streaming bank.
- **Change:** Batch the existing 65 maximum decorative instances across 11 repeated placement call sites into up to 15 existing `AWorldDetailCluster` HISM actors (only actual resident meshes). Preserve world transforms, imported materials and all visual counts. Do not change the Ferry footbridge collision actor, quest anchors, gameplay route or save keys.
- **Root maintenance defect:** `AChapterWorldRouter::ClearPrototypeBuilders` did not explicitly destroy tagged `AWorldDetailCluster` instances while it destroyed tagged `AStaticMeshActor` instances. Add tagged-cluster cleanup so Shire decorative objects cannot survive a route/chapter rebuild.
- **Safety constraints:** no synchronous heavy load, new Tick, spawning NPCs, unrestricted geometry growth, or HLOD generation on the small runner. Conservative 32,000cm visual cull endpoint prevents unintended near-route missing props; tune only after DX11 720p frame-time/VRAM evidence.
- **Gate:** source implementation + focused regression added. Status `SOURCE_IMPLEMENTED / COMPILE_PENDING`; no PIE/DEVICE/VISUAL/PERFORMANCE acceptance, no Gate 6/7 closure.

## 2026-10-09 - P1C01 visual successor packet staged after #1772 evidence, no runtime replacement yet

- Source: exact-head #1772 seven rendered evidence shots (Bag End, Hobbiton, Party Field, Mill Bridge, Bywater edge, Ferry, wooded road). Visual diagnostic: low-poly village/folliage, sparse Party Field framing, simplistic bridge and ferry shoreline. Existing builder and asset-streaming subsystem remain sole consumers and loading owners.
- REGISTERED NEXT VISIBLE WAVE only: (1) licensed final animated FBX Bilbo/Gandalf/Sam/Merry/Pippin/Black Rider/horse and Frodo human deformation review, (2) physically believable pastoral terrain/tree/hedge/architecture silhouettes through preexisting HISM and soft/async banks, (3) Bag End/Party Field identity and real WAV, (4) seven-angle plus manual PIE device review. Do not add anonymous filler assets or density beyond profile until measured.
- Gate: unchanged UE4.27.2 DX11 720p 30 FPS target, 8GB RAM, ~2GB VRAM, 1K/2K packed PNG/TGA, async FStreamableManager, pooled NPCs. Runtime implementation of new art is **NOT** completed in this administrative/CI packet; register and require provenance/QC before production promotion. Gate 6/7 remains open; Bree locked.

## 2026-10-08 - P1C01 HIGH_FIDELITY_SURFACE_REPLACEMENT: Bucklebury ferry shoreline land-foliage correction
- Authorized under registered P1C01 `HIGH_FIDELITY_SURFACE_REPLACEMENT` after seven-shot visual triage: `06_Bucklebury_Ferry` displays land vegetation intruding into the water. Corrected geometry ownership rather than camera/capture masking or added density.
- `SpawnVillage` Brandywine surface (FerryX=23500,Y=-500) is a 14x60 basic cube with 700cm X and 3000cm Y half-size. The deterministic `ShireLayout::IsInsideFerryWaterBuffer` excludes three land-tree HISM generators (+260cm bank buffer) and grass (+95cm); relocates one existing flower bed by 335cm to dry land. Keep native river reeds under their existing dedicated wetland pass.
- No new mesh actors, synchronous loads, density, tick, collision, quest/world-route moves, new chapter or P1C02. Paired scenic trunk/canopy HISM instances are skipped together. Source regression and exact-head build/import/render/runtime proof pending; no human visual/PIE/device/720p FPS/VRAM/Gate 6/7 signoff.

## 2026-10-08 - P1C01 CVBP visual production packet: authored Hobbit-hole facade cleanup (pending exact-head proof)
- Reused the existing `AShirePrototypeWorldBuilder::SpawnHobbitHole` production asset path (already resident/soft-streamed), retaining authored turf mound + round facade and unchanged quest/route/collision placement. Removed primitive cylinder window glass, proxy knob and cube chimney overlays **only** when the production facade exists; retained them for the no-asset fallback. No new actors/instances beyond prior counts, no asset format/loading changes, no World Composition migration.
- Added a focused source regression test; existing One-Shot PR #329 must provide exact-head Static and UE4.27.2 compile/import/render/runtime proof. #1746 PASS belongs solely to previous `c371b5b` head and does not validate this new visual delta. No PIE/device/visual/FPS/Gate 6/7 acceptance is claimed.
- CVBP and nonessential administrative-friction policy are documented in separate Governance PR #331; active P1C01 still uses one existing runtime writer, batched integration and technical fail-closed safety.

## 2026-10-05 - P1C01 HIGH_FIDELITY_SURFACE_REPLACEMENT registered

- Scope: replace owner-rejected flat/proxy Shire surface presentation inside the existing P1C01 world only; no new chapter, no Bree runtime opening, no density wave.
- Owner visual evidence: current PIE screenshots read as grey/flat terrain, weak material depth, simple low-poly vegetation and proxy-quality presentation. This is a human visual rejection, not a request to increase instance counts.
- Approved source lane: receipt/SHA256-verified Poly Haven CC0 surfaces already staged through the project warehouse/intake system. Historical generated output is not reusable unchanged because its MTL directives were malformed.
- Root-fix requirement: P1C01 material intake must emit one complete directive per line (`newmtl`, `Pr`, `Pm`, `Ks`, `map_Kd`) and fail static regression before any UE import.
- Runtime ownership: `AShirePrototypeWorldBuilder` remains the sole Shire geometry/material consumer; `UShireChapterAssetStreamingSubsystem` remains the async residency owner. No second world authority is introduced.
- Low-spec boundary: 1K/2K runtime textures by default, one visible albedo sample plus bounded scalar roughness/metallic/specular in this wave, no blanket 4K, no synchronous heavy load, no foliage-density increase.
- Intended authored bindings after validated import: grass/ground, dirt/garden/riverbank, stony paths, bark, warm plaster, moss/stone and wood. Leaves/foliage keep the current bounded foliage master path until a separately profiled replacement is proven.
- Geometry boundary: this material car alone does not resolve the already-identified low-poly tree/terrain silhouette problem. Natural foliage/terrain geometry replacement remains a separate MW5 visual car after the surface pipeline is healthy.
- Gate: fresh exact-head static + UE4.27.2 import/build evidence, then fresh render capture and human chapter review. No VISUALLY-ACCEPTED, PERFORMANCE-ACCEPTED, PIE-TESTED, DEVICE-TESTED or Gate 6/7 acceptance is implied by this registration.

## 2026-10-01 - P1C01 FOUNDATION_CORRECTIONS_V1 registered

- Scope: corrective foundation pass before additional visible P1C01 construction; no new chapter or story outcome.
- Confirmed runtime defect: manually builder-authored humanoid ambient residents in Bree/Rivendell/Lorien can reach social-life logic without being visible to the Director's candidate registry.
- Corrective architecture: `ALivingWorldDirector` performs one committed-world reconciliation scan, weakly registers persistent social-capable residents, excludes `LivingWorldManaged` pooled actors and fauna, and keeps `GatherActiveAmbientNPCsNear()` as the single bounded candidate query. Persistent registration does not transfer lifecycle ownership.
- Startup-order rationale: world routing/build can precede LivingWorldDirector spawn, therefore builder-local `SetLivingWorldDirector()` calls are not accepted as the sole fix.
- Audio-surface correction: establish Grass/Dirt/Stone/Wood project SurfaceTypes and prefer Physical Material identity in footsteps, retaining name/tag fallback until production material instances are fully authored.
- Character asset correction: animated production candidates must be UE4.27 FBX 2018-compatible; existing OBJ character pieces remain static modular fallback only until real skeleton/weights/deformation/AnimBP proof exists.
- Material strategy remains **Balanced Medium + selective High**: no blanket multi-map expansion on the ~2 GB VRAM target; selective normal/channel-packed detail only after bounded intake/profile work.
- No Niagara conversion is authorized for current fauna without profiling evidence; pooled bounded fauna and HISM world detail remain the default architecture.
- Gate: exact-head Pre-Unreal + UE4.27.2 validation required before merge. Human PIE/device/visual/pacing/performance acceptance remains separate.

## 2026-09-30 - P1C01 SAVE_LOAD_LONG_SESSION chapter registered before runtime implementation

- Scope: next serialized P1C01 reliability car after SHIRE_AUDIO_IDENTITY exact-head machine-green and merge.
- Predecessor evidence: PR #199 exact head `c258cebda8ae5749c54ed0aa6717582b89988fc3`; Pre-Unreal #1486 SUCCESS; Unreal Build #1159 SUCCESS; merge `ec96e9e487ecbe91d9563848f685df4bd5c11b0d`.
- Persistence ownership: AShirePlayerCharacter keeps the production snapshot/restore path, UShireQuestSubsystem owns logical persistence domains, AChapterWorldRouter owns committed-world identity/revision. No parallel save manager.
- Existing long-session protections retained: transactional restore publication, async checkpoint world-revision guard, queued snapshot preservation, legacy identity canonicalization and deferred grounded transform restore.
- New admission contract: reject structurally oversized/corrupt save payloads before BeginPersistenceRestore or any player/quest mutation.
- Restore ceilings: quest stages 128; story beats 512; route entries 16; NPC memory buckets 128; discoveries 512; insight milestones 128; progression tracks 64; Chronicle entries 1024; known map regions 128.
- Gate: exact-head Pre-Unreal + UE4.27.2 required before merge. Human long-session PIE/device hitch/persistence-stress acceptance remains separate and is not claimed.
- Machine contract: `Data/P1C01SaveLoadLongSessionV1.json`; guard target PG-222.

## 2026-09-30 - P1C01 SHIRE_AUDIO_IDENTITY chapter registered before runtime implementation

- Scope: next serialized P1C01 runtime car after CINEMATIC_CONTROL_HANDOFF exact-head machine-green and merge.
- Predecessor evidence: PR #198 exact head `46655d2ecdc02a3f1698c9fd0b1b14c09f767946`; Pre-Unreal #1484 SUCCESS; Unreal Build #1157 SUCCESS; merge `3b38698c19a244fde8f2979d73f12cd829576b7f`.
- Source identity: birds, hedge breeze, farm work, distant laughter, carts, warm interiors and fire/cutlery.
- Runtime ownership: UShireAudioSubsystem remains sole runtime audio owner; cue requests continue from StoryPresentation/Dialogue systems.
- Streaming invariant: heavy/nonresident audio uses FSoftObjectPath + FStreamableManager async; missing authored assets remain silent and never trigger synchronous fallback loading.
- Low-spec concurrency invariant: decorative localized SFX use shared attenuation plus a bounded start window of at most 6 starts per 0.25 seconds; the existing per-cue 0.06-second repeat guard remains.
- Priority invariant: story-critical SFX are not dropped merely because decorative spatial ambience/foley exhausted its burst budget.
- Asset boundary: final WAV masters/intake/listening/mix remain separate work; this chapter does not claim final audio-bank integration or listening acceptance.
- Gate: exact-head Pre-Unreal + UE4.27.2 required before merge. PIE/device/listening/pacing/performance acceptance remains separate and is not claimed.
- Machine contract: `Data/P1C01ShireAudioIdentityV1.json`; guard target PG-221.

## 2026-09-30 - P1C01 CINEMATIC_CONTROL_HANDOFF chapter registered before runtime implementation

- Scope: next serialized P1C01 runtime car after QUEST_SIDE_ACTIVITY_COHERENCE exact-head machine-green and merge.
- Predecessor evidence: PR #197 exact head `10fa10ac47deed372d3a29c14dd30c1c3b5a5522`; Pre-Unreal #1481 SUCCESS; Unreal Build #1154 SUCCESS; merge `e926889f9328e238afaffb16f9f9dabf58ce9040`.
- Runtime ownership: UShireStoryPresentationSubsystem owns presentation lock/state, AStoryPresentationDirector owns runtime camera handoff, UShireQuestSubsystem remains sole quest/story truth, and AChapterWorldRouter remains world-commit truth.
- Handoff contract: timed release, explicit skip release and chapter-change release all converge on the same presentation exit path; runtime camera must return to the previously embodied player view and may not outlive cinematic unlock.
- External-camera invariant: authored external cameras/Level Sequences remain authoritative; the runtime presentation director may not steal their view target.
- Transaction invariant: presentation may not mutate route, save, quest or world-commit state. Skipping presentation changes presentation only; locked story postconditions remain owned by quest/story systems.
- P1C01 focus: BilboDisappearance is the primary cinematic beat covered by this car. No new story outcome is introduced.
- Gate: exact-head Pre-Unreal + UE4.27.2 required before merge. PIE/device/visual/pacing/performance acceptance remains separate and is not claimed.
- Machine contract: `Data/P1C01CinematicControlHandoffV1.json`; guard target PG-220.

## 2026-09-30 - P1C01 QUEST_SIDE_ACTIVITY_COHERENCE chapter registered before runtime implementation

- Scope: next serialized P1C01 runtime car after LIVING_SHIRE exact-head machine-green and merge.
- Predecessor evidence: PR #196 exact head `149c9570c2cbac4295b0b1c41dca5e06f2e7f5bc`; Pre-Unreal #1478 SUCCESS; Unreal Build #1151 SUCCESS; merge `a478127559ab54f0ec938377a4962e6a75479d36`.
- Source basis: Source 01 F1-01/F1-02/F1-03 optional windows; Source 06 optional activity/quest rules; Source 07 mission package rules requiring optional branches to rejoin safely and rewards to remain idempotent.
- Runtime ownership: UShireQuestSubsystem remains sole quest/story truth and side-activity availability/completion owner. No parallel quest brain.
- Coherence contract: one bounded safe-window projection, story-beat closing windows, explicit P1C01 urgency suppression, and duplicate-completion rejection.
- Urgency guard: RingSecret, LeavingHome, KeepOffRoad and FerryEscape suppress casual optional activities even if stale/legacy beat state appears open.
- Canon invariant: optional activity cannot advance required anchors, alter locked outcomes, or become a hidden dependency of the main quest.
- Gate: exact-head Pre-Unreal + UE4.27.2 required before merge. PIE/device/visual/pacing/performance acceptance remains separate and is not claimed.
- Machine contract: `Data/P1C01QuestSideActivityCoherenceV1.json`; guard target PG-219.

## 2026-09-30 - P1C01 LIVING_SHIRE chapter registered before runtime implementation

- Scope: next serialized P1C01 runtime car after CHARACTER_PRESENTATION exact-head machine-green and merge.
- Predecessor evidence: PR #195 exact head `24ffa0ddb35756a606fb166d010b1e7ca2940308`; Pre-Unreal #1475 SUCCESS; Unreal Build #1148 SUCCESS; merge `66caf6168157e0ec171a1e7249ead245e45d8b42`.
- Runtime ownership stays decoupled: ALivingWorldDirector owns population budgets, pooled lifecycle, active-NPC admission/query, micro-events and fauna caps; UShireNPCContextSubsystem owns bounded context/knowledge/schedules/relationship projection; UShireQuestSubsystem owns story/progression truth.
- Bottleneck repair: ambient social pairing must not perform a full-world `TActorIterator<AShireAmbientNPC>` scan from every NPC. Social candidates are restricted to the Director's bounded managed active population.
- Context contract: NPC routine updates consume one bounded behavior snapshot per scheduled refresh rather than rebuilding danger/weather/schedule context through repeated independent calls.
- Fauna contract: the existing `max_active_fauna_groups_near_player=2` budget becomes an enforced runtime cap, not data-only guidance.
- Population invariant: P1C01 ambient target stays 18. No crowd-density increase is authorized by this car.
- Performance invariants: pooling remains mandatory; no synchronous heavy load; no per-frame global context reconstruction; fauna/environment motion remains distance/activity-budget driven.
- Story/canon invariant: ambient life cannot own locked outcomes, danger/story overrides outrank ambient schedules, and existing knowledge gates remain authoritative.
- Gate: exact-head Pre-Unreal + UE4.27.2 required before merge. PIE/device/visual/pacing/performance acceptance remains separate and is not claimed.
- Machine contract: `Data/P1C01LivingShireChapterV1.json`; guard target PG-218.

## 2026-09-30 - P1C01 CHARACTER_PRESENTATION chapter registered before runtime implementation

- Scope: next serialized P1C01 runtime car after PARTY_AND_SOCIAL_LOOP exact-head machine-green and merge.
- Source basis: Source 02 defines Frodo as a Hobbit/Ring-bearer whose named equipment is story-state driven and must not turn him into a conventional power-fantasy warrior; Gandalf remains a guide whose magic is rare/purposeful. Source 11 requires believable authored presentation, reduced distant animation cost and low-spec character/crowd budgets.
- Runtime ownership: AShirePlayerCharacter owns playable presentation, AShireNPC owns named-NPC presentation, UShireChapterAssetStreamingSubsystem remains the only skeletal-rig async residency owner, and UShireQuestSubsystem remains story-state truth.
- Identity contract: named production characters use a stable ProductionCharacterId separate from DisplayName/localization. P1C01 hero cast in this car is Frodo, Gandalf, Bilbo and Sam.
- Canon equipment guard: Frodo must not show future named sword gear inside P1C01; Gandalf's staff presentation is allowed. No future-knowledge/equipment leak is authorized.
- Low-spec contract: no synchronous heavy load, no per-frame asset scan, no extra crowd population, existing modular fallback stays visible until a complete skeletal mesh + AnimBP pair resolves, and skeletal meshes use update-rate optimization with rendered-only pose ticking.
- Gate: exact-head Pre-Unreal + UE4.27.2 required before merge. PIE/device/visual/deformation/performance acceptance remains separate and is not claimed.

## 2026-09-30 - P1C01 SHIRE_WORLD_DENSITY car registered before runtime implementation

- Scope: first post-mega runtime car for the existing P1C01 aggregation; no chapter renumbering and no new story outcome.
- Source basis: Shire/Hobbiton pastoral hills, lanes, farms, Hobbit-holes, gardens and warm domestic scale; chapter-state population remains owned by LivingWorldDirector rather than the world builder.
- Runtime ownership: ShirePrototypeWorldBuilder may add geometry/dressing only. Ambient NPC population stays owned by LivingWorldDirector; quest/story truth stays owned by ShireQuestSubsystem.
- Low-spec implementation contract: add at most 5 zero-Tick AWorldDetailCluster HISM clusters / 70 non-collision decorative instances using already-resident production meshes only. No synchronous load, no new hard heavy-asset reference, no crowd Spawn/Destroy path, no per-frame scan.
- Categories: wood piles near homes/farms, fern clumps near hedges/wooded road, reed clusters near The Water/ferry, path markers along readable travel corridors, and fallen logs inside wooded-road dressing.
- Population invariant: P1C01 ambient target remains 18; this car improves perceived density through spatial/detail variety, not more full AI.
- Traversal invariant: all new detail is non-collision and stays outside story/quest anchor ownership.
- Gate: source implementation must pass exact-head Pre-Unreal + UE4.27.2 before merge; target-device FPS/hitch/RAM/VRAM and human visual/pacing review remain separate Gate 6/7 evidence.
- Implementation: `ShirePrototypeWorldBuilder::SpawnWorldDensityDetailPass()` now uses five bounded `AWorldDetailCluster` HISM categories with a 70-instance ceiling and no collision/Tick ownership.
- Regression guard: PG-214 + source-contract test lock population target 18, HISM cluster/instance ceilings, resident-only asset behavior and the no-load/no-ambient-NPC-spawn boundary.
- Evidence boundary after implementation: **SOURCE-IMPLEMENTED / EXACT-HEAD PRE-UNREAL + UE4.27.2 PROOF PENDING**. No PIE/device/visual/pacing/performance acceptance is claimed.

## 2026-09-30 - P1C01 Maximum-Safe Mega Build V1 + LivingWorld cull safety

- P1C01 legacy mega-pack path drift found during the train audit was corrected to the D-backed Warehouse authority; this is infrastructure consistency only, not content/runtime acceptance.
- Registered before further runtime expansion: owner authorizes one large P1C01 production train with many bounded work cars under one approval, rather than repeated tiny approvals.
- Source basis rechecked from the supplied Story/Timeline, World/Locations, Gameplay/Side Activities, Mission Matrix and Master Production Systems PDFs.
- Source boundary: F1-01 owns Ring-history/birthday/Gandalf/party material; F1-02 owns Bag End Ring-danger/departure; F1-03 owns Shire-road/Black Rider/ferry material. Current runtime P1C01 is broader than source F1-01, so this wave preserves current topology while explicitly recording the mismatch instead of silently redefining canon chapters.
- Confirmed programmer finding: grouped micro-event distance cleanup could retire nearby event members because one roaming member exceeded EventCullDistance.
- Registered and implemented repair: event lifetime expiry stays event-wide; distance retirement is member-local through existing ALivingWorldDirector pool ownership. No second world-life brain is created.
- Audit correction: ShireAmbientNPC already centralizes its only direct UGameplayStatics::GetPlayerPawn call in GetPlayerPawnCached(); no redundant cache rewrite is authorized.
- Save-schema work is evidence-gated: schema 6/newer-save rejection and legacy canonicalization are present, but no verified v1-v6 transform history exists. No migration ladder may be invented until history/fixtures are recovered.
- Machine-readable train: Data/P1C01MaximumSafeMegaBuildV1.json + Data/P1C01OvernightMegaBuildTrainV1.json. Source disposition: Data/P1C01SourceToRuntimeDispositionV1.json. Save boundary: Data/SaveSchemaMigrationAuditV1.json.
- Architecture remains decoupled: ALivingWorldDirector owns population/event budgets and pooling; UShireNPCContextSubsystem owns bounded NPC context/knowledge/schedules; UShireQuestSubsystem owns story/progression; world builders own geometry/dressing/story placement.
- Low-spec rules remain mandatory: FBX for animated production assets; PNG/TGA production textures; soft references + FStreamableManager for heavy assets; pooled transient crowds; ISM/HISM + LOD/culling for repeated detail.
- Runtime feature cars beyond the defect repair remain gated by W00 exact-head UE4 evidence and later Gate 6/7 requirements. Source/QC/data/static/documentation preparation may proceed in parallel.
- Evidence boundary: SOURCE IMPLEMENTATION/PREPARATION ONLY until exact-head CI/UE4 and later chapter-specific PIE/device/human evidence exist.

## 2026-09-29 - F2-04 Road & Helm's Deep Prep Maximum-Safe Source V1

- Canonical mission: F2-04 Road & Helm's Deep Prep.
- Primary location: Rohan / Helm's Deep.
- Present focus: Rohan party.
- Canonical beat: refugees move under threat; defenses are prepared.
- Safe optional window: escort, rescue, armory, wall prep, civilians.
- Locked postcondition: Uruk army arrives.
- Tolkien-compatible source detail supports the Westfold approach, Helm's Dike, Hornburg, Deeping Wall, Deeping-stream/culvert, caves/refuge, stored food/animals, sentinels, scouts, guard placement and preparation of defenders.
- Permanent story rule applies: preserve source-grounded road/refugee/fortification/civilian/defense-preparation detail instead of jumping directly from Edoras to siege combat.
- F2-05 siege phases, breach response, retreat, mounted sortie and dawn counterattack remain outside this pack.
- Source/preparation only. Do not invent a Part II runtime ID.
- Low-spec rules remain mandatory: FBX animated candidates, PNG/TGA textures, soft/async heavy loading, pooled transient crowds, repeated fortification dressing through ISM/HISM + LOD/culling.
- Evidence boundary: SOURCE ARCHITECTURE REGISTRATION ONLY. No runtime integration, PIE, device, visual, pacing or performance acceptance is implied.

## 2026-09-29 - P1C01 Frodo/Gandalf skeletal candidate production wave V1

- Existing owner priority remains unchanged: replace proxy/modular character bodies with real skeletal FBX production characters, beginning with Frodo and Gandalf inside the active P1C01 runtime benchmark.
- This wave is a **source/intake/QC preparation wave**, not a runtime replacement claim.
- Frodo is priority 1 because he is the primary playable Shire quality bar; Gandalf is priority 1 because he proves the tall-humanoid/parallel playable route.
- Accepted source candidates must be legal/provenanced, FBX for animated character delivery, with PNG/TGA production textures. OBJ may remain static fallback only and BMP is forbidden.
- Candidate selection must preserve real rigging requirements: skeleton, skin weights, deformation, retarget compatibility, locomotion coverage, material slots, LOD/cull plan and equipment sockets. Container conversion alone is never rigging evidence.
- Runtime handoff target remains /Game/Production/Characters/Rigs/<Character>/ with SK_<Character> + ABP_<Character>_Locomotion and soft/async loading.
- Existing modular character remains visible until both skeletal mesh and AnimBP resolve; do not create a broken half-rig state.
- ShireNPCContextSubsystem / LivingWorldDirector ownership is unchanged by this wave; presentation assets must not create a second AI/state authority or per-character global polling.
- Evidence boundary: SOURCE/INTAKE/QC PREPARATION ONLY. No character is called rigged, imported, PIE-tested, device-tested, visually accepted or performance accepted by this ledger entry.


## 2026-09-29 - F2-03 Edoras Maximum-Safe Source V1

- Canonical mission: F2-03 Edoras.
- Primary location: Rohan / Edoras.
- Present focus: Theoden, Eowyn, Eomer, Gandalf, Aragorn.
- Canonical beat: Theoden restored; political and military crisis clarified.
- Optional window: court exploration, stables, equipment, social scenes.
- Locked postcondition: Rohan evacuates toward Helm's Deep.
- Keep F2-04 road/Helm's Deep preparation and later battle resolution outside this pack.
- Source/preparation only. Do not invent a Part II runtime ID.
- Permanent story rule applies: preserve compatible court, settlement, stable, relationship and departure detail instead of reducing the chapter to one set-piece.
- Low-spec rules remain: FBX animated assets, PNG/TGA textures, async soft references, pooled crowds, ISM/HISM + LOD/culling.
- Evidence boundary: SOURCE ARCHITECTURE REGISTRATION ONLY.

## 2026-09-29 - F2-02 reconciliation with full-journey story contract

- F2-02 Fangorn & Gandalf Returned remains the canonical source wave after F2-01 and before F2-03 Edoras.
- The existing Fangorn/Ent/Gandalf source plan is now explicitly governed by the permanent no-story-shortcuts / zero-silent-omission rule.
- Compatible Tolkien Fangorn, Ent, relationship, travel and environmental detail discovered during chapter review must be implemented or dispositioned; later F2-08 Isengard resolution remains excluded.
- Runtime identity remains NOT_ASSIGNED_DO_NOT_INVENT until a dedicated Part II mapping decision exists.
- Decision owner: DEC-083.
- Evidence boundary: source/governance reconciliation only; no runtime or human acceptance promotion.

## 2026-09-29 - Permanent full-journey story/source + Arabic localization contract

- Owner direction is now permanent project memory: **Shire Journey must be experienced as a rich journey, not a shortened recap connecting only major film set pieces.**
- `01_STORY_AND_TIMELINE_BIBLE` is the F1-F3 navigation/order spine and locked-outcome guide. It is **not** the maximum amount of story/world detail allowed in a chapter.
- Film trilogy + supplied screenplays remain primary for film-driven chronology, visible staging, cast presence, character knowledge and required outcomes.
- Tolkien *The Lord of the Rings* + Appendices is the primary supplied deep-detail source for compatible lore, geography, culture, chronology, relationships, material culture, travel detail and book-only events.
- Tolkien events/details omitted or compressed by the films are eligible for **real playable treatment** when they fit without breaking a locked film outcome, chronology, knowledge boundary, save/route integrity or required story handoff. They are not automatically reduced to text lore.
- Required source packet for each F1-01 through F3-07 chapter: Timeline -> film/screenplay -> Tolkien narrative chapter(s) -> Appendix B/other appendices -> Sources 02-11 -> implementation/disposition.
- **Zero Silent Omission:** every meaningful source-backed detail discovered in chapter review is IMPLEMENTED, LINKED_FOR_LATER, DEFERRED_PERFORMANCE, BOOK_ONLY_COMPATIBLE, BLOCKED_BY_FILM_CONTINUITY, NOT_APPLICABLE or NEEDS_SOURCE_RESOLUTION. Non-implementation must have a reason.
- Gate 6/7 may delay runtime integration, but it never authorizes deleting story/detail coverage from the source plan.
- Low-spec performance is solved through soft/async residency, pooling, ISM/HISM, LOD/culling and bounded simulation rather than by silently shrinking the designed journey.
- Localization contract: English spoken VO stays English; Arabic covers subtitles, objectives/quest directions, menus, settings, HUD/system guidance and tutorial text; map location labels keep their canonical English Middle-earth names. Arabic requires proper RTL/shaping/wrapping/font support and subtitle synchronization.
- Evidence boundary: **GOVERNANCE/SOURCE/LOCALIZATION CONTRACT REGISTERED.** This does not claim all source details or Arabic runtime UI are already implemented, and it does not promote COMPILE/PIE/device/visual/pacing/performance acceptance.

## 2026-09-29 - F2-01 Three Hunters / Captives Maximum-Safe Source V1

- Canonical mission authority: **F2-01 Three Hunters / Captives**.
- Primary location: **Rohan / Fangorn edge**.
- Present/playable focus: Aragorn, Legolas, Gimli, Merry, Pippin.
- Canonical critical path: the Three Hunters pursue the Uruk-hai while Merry and Pippin escape into Fangorn.
- Safe optional window: tracking, stamina and evidence reading.
- Locked postcondition: **paths converge around Fangorn/Rohan**.
- Entry/save contract: validate previous chapter outcome, roster and knowledge flags; clean-entry autosave; pre-set-piece checkpoint; postcondition save after committed state.
- World-state rule: chapter-specific population, weather, damage, patrol and prop variants only; do not leak future-state changes early.
- Fangorn production grammar: ancient forest, dense trunks, roots, mist and a living environment; exploration/disorientation now, Ent interactions remain canon-aware and the later mobilization state is not opened early.
- This is a **source/preparation wave only**. No Part II runtime chapter ID is invented because the repository currently has no documented Part II runtime-ID migration mapping.
- Maximum-safe architecture uses independent preparation banks for hunter tracking, Uruk trail/evidence, captive escape, Rohan edge traversal, Fangorn threshold, character/animation, audio/weather and transition aftermath.
- Existing low-spec rules remain mandatory: animated candidates FBX-only; production textures PNG/TGA, BMP blocked; heavy runtime assets soft-referenced/asynchronously loaded; crowds pooled; repeated dressing ISM/HISM + LOD/culling.
- Evidence boundary: **SOURCE ARCHITECTURE REGISTRATION ONLY**. No runtime integration, PIE, device, visual, pacing or performance acceptance is implied.

## 2026-09-29 - F1-08 Amon Hen / Breaking of the Fellowship Maximum-Safe Mega Source V1

- Canonical mission authority: **F1-08 Breaking of the Fellowship**. Legacy runtime consumer remains **P1C08** under DEC-067; no runtime renumbering is introduced.
- Source-verified critical path: Boromir falls; Merry/Pippin are captured; Frodo chooses Mordor; Sam follows. Locked postcondition: **three parallel campaigns begin**.
- Mission package requires stable-ID objective graph, documented encounter spawn/role/escalation/cleanup/fail rules, identical cinematic skip postconditions, entry + pre-set-piece + postcondition save coverage, and postcondition validation before unlocking the next campaign state.
- Amon Hen world grammar: river corridor / ancient ruins; water, cliffs, stone monuments and forest; gameplay roles include scouting and the Fellowship break; required world-state variants include river journey and Uruk attack.
- Canon/character guardrail: Boromir's arc remains tragic redemption after temptation, never generic villainization. Dialogue/loadout/state support remains chapter-aware and future-event safe.
- Tolkien cross-reference is used only for compatible landscape/landmark detail: Amon Hen high-seat/watchwork, ancient stone road/stairs, Parth Galen shore/lawn, Rauros/Tol Brandir sightline language. The film-first mission outcome remains authoritative.
- Maximum-safe source architecture will use bounded multi-bank preparation rather than one giant future resident set: calm arrival, decision/Seat route, Uruk attack, Boromir defense/aftermath, Merry-Pippin capture/pursuit, Sam/Frodo departure, and campaign-split aftermath support.
- Runtime promotion remains blocked behind predecessor Gate 6/7. Source/candidate preparation may proceed now under DEC-078.
- Existing low-spec rules remain mandatory: animated candidates FBX-only; production textures PNG/TGA, BMP blocked; heavy runtime assets soft-referenced/asynchronously loaded; crowds pooled; repeated dressing ISM/HISM + LOD/culling.
- Evidence boundary: **SOURCE ARCHITECTURE REGISTRATION ONLY**. No UE integration, PIE, device, visual, pacing or performance acceptance is implied.

## 2026-09-29 - Maximum Safe Production Mode V1

- Owner direction: production speed becomes a first-class project objective. The project should run at the **maximum safe throughput** allowed by current evidence instead of advancing through tiny isolated preparation increments.
- This is an execution-mode change, not permission to weaken canon, provenance, runtime, save, Gate 6/7, device, visual or performance acceptance.
- Maximum-safe means adaptive saturation of all independent preparation lanes until a real guard trips: persistent warehouse integrity, storage reserve, format/provenance policy, exact-head CI, runtime dependency safety, measured residency/memory limits or human Gate 6/7 requirements.
- Runtime-changing integration remains exactly one lane at a time. Source/PDF indexing, warehouse acquisition, candidate indexing, material/audio/character preparation, later-region authoring and documentation may advance in large coherent waves in parallel with the active runtime lane.
- Prefer **large coherent production waves** over one-small-PR-per-idea churn. Shared authority files must be updated in the same wave so branch-conflict overhead does not become the production bottleneck.
- Persistent warehouse writers remain serialized because they share one runner-local warehouse and inventory truth. Index-only/source-prep work that does not mutate the warehouse may proceed independently.
- Latest live warehouse evidence on Warehouse #286: inventory audit passed with payloadFiles=18697, bytes=6688457009, receipts=14, receiptRecords=667, activeRecords=239, superseded=428, duplicateGroups=0. The workflow later failed in the saturation report on an empty-sum StrictMode tooling defect, not on inventory corruption.
- Existing low-spec rules remain mandatory: animated production assets FBX-only, PNG/TGA production textures, no BMP, soft references + async loading, pooled crowds, ISM/HISM + LOD/culling.
- Evidence boundary: **PRODUCTION POLICY REGISTRATION + TOOLING REPAIR WAVE**. This does not constitute PIE/device/visual/performance acceptance.

## 2026-09-29 - F1-07 Lórien & Anduin Mega Landmark Source Pack V1

- Canonical mission authority: **F1-07 Lórien & Anduin** from the supplied Story/Timeline and Mission/Chapter source PDFs.
- Runtime boundary remains **P1C07 = F1-07** under DEC-067. This source pack may establish the Anduin journey and Amon Hen approach/readability required by F1-07, but **Breaking of the Fellowship / F1-08 runtime content remains outside this pack**.
- Canonical critical path is grief -> rest -> gifts -> river journey -> mounting group pressure. Safe optional window is quiet exploration, provisioning and boats. Locked postcondition is the Fellowship reaching Amon Hen.
- Lothlórien world grammar: golden forest sanctuary; vertical flets, organic bridges, luminous forest; recovery, gifts, reflection and exploration; night-arrival/departure variants.
- Anduin approach world grammar: river corridor with water, cliffs, stone monuments and forest; boat traversal/scouting; this pack prepares journey/readability assets but does not claim the later F1-08 Fellowship-break set piece.
- Landmark-first requirement: Lothlórien must read through a dominant vertical flet/tree-canopy sanctuary vista; Anduin must read through river-axis/cliff/stone-monument silhouettes and a clear Amon Hen approach focal vista.
- Source policy remains shared-warehouse/index-only. Animated candidates are FBX-only; production textures PNG/TGA; BMP blocked. Heavy runtime assets remain soft-referenced/asynchronously streamed, crowds pooled, repeated dressing ISM/HISM + LOD/culling.
- Heavy execution remains warehouse-inventory-gated until the active receipt supersession repair produces a clean persistent audit.
- Evidence boundary: **SOURCE ARCHITECTURE REGISTRATION ONLY**. No UE integration, PIE, device, visual, pacing or performance acceptance is implied.

## 2026-09-29 - Part I Landmark Identity Plan V1 + F1-06 Caradhras & Moria Landmark Mega Source Superpack

Registered before any runtime implementation.

Part I landmark identity direction:
- Every production region must expose at least one dominant silhouette/vista or interior focal vista that supports navigation and cinematic continuity.
- This is a visual-identity/streaming/source-preparation contract, not permission to bypass chapter runtime gates.
- Current Part I anchors:
  - The Shire / Hobbiton: pastoral hill / Hobbit-hole / circular-door garden vista language.
  - Bag End: dominant round-geometry interior focal vista using dense lived-in dressing.
  - Bree: town-gate + timber/stone/crowded-inn identity.
  - Weathertop: ancient stone ring against exposed skyline.
  - Rivendell: layered terraces with stone/wood integration and waterfall vista.
  - Caradhras: high mountain-pass ridge silhouette readable through snow/wind/low-visibility states.
  - Moria: monumental underground geometry with entrance threshold / hall-axis / tomb-alert / escape-state landmark sequencing.
- Landmark visibility must survive low-spec constraints. Prefer strong composition, silhouette, LOD/HLOD or simplified distance proxies, instancing for repeated dressing, bounded lighting/fog layers, and preloaded critical vistas rather than brute-force geometry density.

F1-06 canonical source scope:
- Mission package: **F1-06 Caradhras & Moria**.
- Runtime consumers: legacy implementation chapters **P1C05 + P1C06** under the recorded F1/P1 reconciliation.
- Critical path: mountain route fails; Moria reveals Balin's fate; Balrog attacks.
- Safe optional window: survival, puzzle door, routefinding, tomb battle, escape.
- Locked postcondition: Gandalf falls; Fellowship escapes.
- Caradhras world grammar: high mountain pass; snow, rock, wind, low visibility; survival traversal and group assists; storm escalation.
- Moria world grammar: Dwarven underground kingdom; monumental geometry, darkness, mines and halls; puzzle/navigation/combat escalation/horror; entrance/tomb-alert/Balrog-escape variants.

Production intent:
- Build the largest Part I source-preparation pack so far, centered on landmark readability and traversal/cinematic continuity.
- Reuse persistent warehouse stock first and index rather than duplicate payloads.
- Heavy execution is inventory-clean gated while the current warehouse hash mismatch remains unresolved.
- Animated candidates remain FBX-only; production textures PNG/TGA; BMP blocked; heavy runtime assets remain soft-referenced/asynchronously streamed; background populations remain pooled; repeated static dressing uses ISM/HISM + LOD/culling.
- Runtime integration for P1C05/P1C06 remains blocked until predecessor Gate 6/7 acceptance.

Status: **REGISTERED / LANDMARK ARCHITECTURE AUTHORIZED / SOURCE ARCHITECTURE AUTHORIZED / HEAVY EXECUTION INVENTORY-GATED / RUNTIME GATED**.

## 2026-09-29 - F1-05 Rivendell & Fellowship Mega Source Superpack V1

Registered before any runtime implementation.

Canonical source scope:
- Mission package: **F1-05 Rivendell & Fellowship**.
- Runtime consumer: legacy implementation chapter **P1C04** under the recorded F1/P1 reconciliation.
- Critical path: the Council chooses destruction of the Ring; the Fellowship forms.
- Safe optional window: exploration, lore, equipment and relationship scenes.
- Locked postcondition: Nine depart.
- Rivendell world grammar: Elven valley sanctuary; stone/wood integration; waterfalls; layered terraces; lore/relationships/equipment/council transition; arrival-wounded and Fellowship-formed state variants.

Production intent:
- Build a very large shared source-preparation pack for Rivendell world layers, Council/Fellowship presentation, equipment, lore-space dressing, relationship-scene support, sanctuary ambience, traversal, cinematic support, fauna and systemic interaction.
- Reuse persistent warehouse stock first; index and score existing candidates rather than duplicate multi-gigabyte payloads.
- Because P1C01 Closure #2 exposed a warehouse hash mismatch, this pack is **inventory-clean gated**: heavy execution must hard-stop unless the warehouse inventory audit is clean.
- Animated candidates remain FBX-only; production textures PNG/TGA; BMP blocked; heavy runtime assets remain soft-referenced/asynchronously streamed; background populations remain pooled; repeated static dressing remains ISM/HISM + LOD/culling.
- Source preparation may be authored before predecessor Gate 6/7 acceptance; P1C04 runtime integration remains blocked behind predecessor acceptance.
- No source index or warehouse score is evidence of PIE/device/visual/performance acceptance.

Status: **REGISTERED / SOURCE ARCHITECTURE AUTHORIZED / HEAVY EXECUTION INVENTORY-GATED / RUNTIME GATED**.

## 2026-09-29 - F1-04 Bree & Weathertop Mega Source Superpack V1

Registered before any runtime implementation.

Canonical source scope:
- Mission package: **F1-04 Bree & Weathertop**.
- Runtime consumers: legacy implementation chapters **P1C02 + P1C03** under the recorded F1/P1 reconciliation; do not rename runtime IDs in place.
- Story boundary: the Hobbits reach Bree from the previous package; Aragorn becomes the guide; Ring use increases danger; Frodo is wounded; the locked postcondition is the party racing for Rivendell.
- Safe optional window: tavern attention, travel, camp decisions and defensive combat.
- Bree world grammar: crossroads town; timber/stone; rain; gates; crowded inn; social stealth, supplies, rumors and pursuit pressure; night-arrival/departure variants.
- Weathertop world grammar: ruined hilltop watchtower; ancient stone ring; exposed skyline; camp tension and the Nazgul encounter; calm-approach/night-attack variants.

Production intent:
- Build one **shared, very large source-preparation pack** for both Bree and Weathertop instead of duplicating payloads between P1C02 and P1C03.
- Reuse the persistent warehouse first. The pack indexes candidates; it does not duplicate multi-gigabyte source payloads.
- Cover surfaces, architecture, settlement props, inn/interior props, roads/travel, ruins, vegetation, weather/audio, fauna, character/animation support, encounter/combat support, cinematic dressing and systemic-interaction support.
- Preserve low-spec constraints: final animated candidates FBX only; textures PNG/TGA; no BMP; runtime heavy assets remain soft-referenced/asynchronously streamed; background populations remain pooled; repeated static dressing remains ISM/HISM + LOD/culling.
- This source-preparation pack may run before P1C01 Gate 6/7 acceptance, but **P1C02/P1C03 runtime integration remains blocked** until predecessor acceptance.
- No source index, warehouse count or candidate score is evidence of PIE/device/visual/performance acceptance.

Status: **REGISTERED / SOURCE PREPARATION AUTHORIZED / RUNTIME GATED**.

## 2026-09-29 - Part I full sequential runtime train and canonical-ID reconciliation

Registered for the owner's continuous overnight production direction.

Purpose:
- Keep P1C01 as the active runtime benchmark while preparing shared warehouse/source indexes for P1C02-P1C08 immediately.
- Runtime remains serialized: only the immediate successor may open after the predecessor Gate 6/7 is genuinely ACCEPTED.
- Canonical mission IDs from the supplied Mission & Chapter Implementation Matrix remain F1-01 through F1-08.
- Existing runtime chapter IDs P1C01-P1C08 are legacy implementation boundaries and do not map one-to-one to canonical mission packages.
- Current reconciliation: P1C01 spans F1-01/F1-02/F1-03; P1C02 and P1C03 split F1-04; P1C04 maps to F1-05; P1C05 and P1C06 split F1-06; P1C07 maps to F1-07; P1C08 maps to F1-08.
- Do not rename runtime IDs in place until a dedicated save/quest/state migration is source-checked and validated.
- Shared warehouse stock is indexed rather than copied per chapter to avoid disk duplication.
- Preparation status never implies READY_FOR_IMPORT, UE import, runtime integration, PIE/device/visual/performance acceptance.

Status: **REGISTERED / SOURCE PREPARATION AUTOMATION IMPLEMENTED / RUNTIME SERIALIZED**.

## 2026-09-29 - Unreal process ownership root repair after #1068

- Unreal Build #1068 exact-head editor compile succeeded, then production-import preflight failed on PID 14144.
- The preceding wait step had reported the editor closed because it checked only UE4Editor, while the import preflight checked both UE4Editor and UE4Editor-Cmd.
- The wait contract now observes both process families and emits owner/session/start-time/command-line/parent-PID diagnostics.
- Interactive UE4Editor processes are never killed by name.
- Bounded recovery is allowed only for an old, workspace-owned, unattended UE4Editor-Cmd with a recognized CI commandlet signature and no live parent process.
- Production-import preflight also emits process ownership evidence if a process still blocks import.

Status: **SOURCE-IMPLEMENTED / EXACT-HEAD VALIDATION PENDING**.

## 2026-09-29 - Core production direction + systemic environmental reactivity contract

Registered before any new runtime implementation.

Purpose:
- Keep the project formula explicit: **AAA Visual Quality + Systemic Reactivity + Intelligent NPCs + Living World + Strict Optimization**.
- Extend the existing `ALivingWorldDirector`, `UShireNPCContextSubsystem`, `UShireQuestSubsystem`, chapter router and interaction contracts; do **not** create a second parallel world brain or NPC brain.
- Add the missing long-term capability as a **bounded systemic environmental reaction contract** so meaningful player/world events can produce appropriate visible/audible responses across supported trees/foliage, water, doors/tools/props, fauna and NPC observers.
- Candidate event families include `Hit`, `Interact`, `PlayerNear`, `WeatherChanged`, `DangerChanged` and `StoryStateChanged`; the authoritative world/story systems publish context while each responder owns its local reaction.
- `ALivingWorldDirector` remains responsible for coarse population budgets, activation/culling, pooling and chapter-aware micro-events; it must not become a per-object God Object.
- `UShireNPCContextSubsystem` remains responsible for bounded NPC context projection; `UShireQuestSubsystem` remains story/quest/memory truth.
- Low-spec rule: no full physics or full-rate Actor Tick for every tree/plant/prop. Prefer material/WPO responses, pooled transient FX/audio, bounded timers/delegates and distance/activity budgets.
- This direction is **not** permission to bypass P1C01 closure. Runtime implementation waits behind the active #145 repair/merge, Closure Pack execution and Shire integration/character/living-world work, and must still satisfy Gate 6/7 and target-device evidence.

Status: **REGISTERED / ARCHITECTURE DIRECTION ACCEPTED / RUNTIME IMPLEMENTATION DEFERRED**.

## 2026-09-28 - Sequential two-chapter production queue: P1C01 -> P1C02

Registered before implementation under the active Part I production lane.

Purpose:
- Keep the current maximum-throughput P1C01 Shire/Hobbiton/Bag End closure pack as the active runtime chapter.
- Prepare the next canonical chapter, F1-02 Shadow of the Past, as a queued source/production packet without opening its runtime lane early.
- Reuse Bag End/Shire assets where valid instead of downloading or importing duplicate stock.
- Allow P1C02 source/warehouse preparation to exist in advance, but keep runtime integration blocked until P1C01 satisfies the real Gate 6/7 acceptance contract and the F1-01 canonical postcondition is validated.
- Once the gate record becomes accepted, the sequential queue may start P1C02 automatically without requiring another owner "continue" prompt.
- Every queued chapter keeps a cheap preflight before any heavy source/import wave.

Canon boundary for P1C02:
- Owner location: Bag End / Shire.
- Playable roster: Frodo, Gandalf, Sam.
- Critical path: Gandalf confirms the Ring danger and Sauron connection.
- Optional window: investigation tutorial, packing, stealth departure.
- Locked postcondition: Frodo leaves the Shire.
- Runtime work remains blocked until the previous chapter is accepted.

Status: **REGISTERED / IMPLEMENTATION QUEUED / P1C02 RUNTIME CLOSED UNTIL P1C01 GATE 6/7**.

## 2026-09-28 - P1C01 Mega Chapter Pack production batching

Registered before execution under W01_P1C01_PRODUCTION_VERTICAL_SLICE.

Purpose:
- Treat the Shire/Hobbiton + Bag End benchmark as one large production package at the preparation layer while preserving bounded internal cars and evidence.
- Reduce workflow/PR churn by batching source preparation, promotion and export coherently.
- Keep runtime integration separate and exact-head gated; this pack does not authorize later chapter runtime expansion.
- Prefer already-staged warehouse stock and quarantine isolated corrupt/missing/licensing blockers rather than stopping unrelated cars.

Status: **REGISTERED / SOURCE IMPLEMENTATION ACTIVE / RUNNER EXECUTION PENDING**.

## 2026-09-27 - Warehouse provider-resolution train V3

Registered before implementation as the fourth warehouse preparation layer, stacked behind V2.

Purpose:
- Resolve access/source blockers revealed by real warehouse staging instead of repeatedly reporting the same gaps.
- Use current provider registry/access policy to distinguish PUBLIC_DIRECT, PUBLIC_PAGE_NO_DIRECT_ARCHIVE, AUTH_REQUIRED, ACCOUNT_MARKETPLACE, PURCHASE, MANUAL_TOOL and REFERENCE_ONLY lanes.
- Preserve all original source/license restrictions; never automate an interactive/login/purchase lane.
- Prefer a legal, technically suitable alternate provider when a primary source cannot be staged automatically.
- Keep hero identity/canon acceptance separate from generic technical stock.
- Animated final production candidates remain FBX-only; production textures PNG/TGA; audio production masters WAV.
- Provider-resolution output is planning/staging guidance only and cannot promote READY_FOR_IMPORT.

V3 car families:
1. Quaternius critical access resolution.
2. Character-base alternates.
3. Humanoid-animation alternates.
4. Fauna/creature alternates.
5. Architecture/world-kit alternates.
6. Vegetation/nature alternates.
7. PBR-material alternates.
8. Audio/foley alternates.
9. Music identity sources.
10. Voice pipeline sources.
11. VFX/weather sources.
12. UI/icon/font sources.
13. Terrain/heightmap sources.
14. Enemy/monster sources.
15. Hero-creature sources.
16. Battle/siege sources.
17. Region-kit source coverage.
18. Marketplace/manual review queue.
19. Provider-overlap/dedupe.
20. Unresolved blocker report.

Status: **REGISTERED / IMPLEMENTATION STARTED**.

## 2026-09-27 - Critical warehouse gap preparation train V2

Registered after V1 warehouse saturation merged green.

Purpose:
- Convert staged warehouse payloads into evidence-rich INTAKE_QC candidates instead of leaving archives and mixed-format source stock unclassified.
- Focus directly on the largest remaining gaps: skeletal characters, animation, creatures/fauna, architecture, vegetation, materials, audio, VFX, UI/localization and terrain.
- Preserve original staged payloads. Preparation happens under a separate persistent prepared root.
- Verify receipt SHA256 before extraction/classification.
- ZIP extraction is allowed; RAR/7Z remain pending without an approved extractor.
- Executable/script payloads and BMP textures are blocking.
- Animated production assets remain FBX-only; audio requires WAV masters; PNG/TGA remain the production texture formats.
- The train stops at INTAKE_QC and cannot promote READY_FOR_IMPORT automatically.
- Runtime integration remains serialized behind project gates.

Status: **REGISTERED / IMPLEMENTATION STARTED**.

## 2026-09-27 - Consolidate stale-base prep branches into warehouse train

To keep the long production queue orderly, the substantive preparation work from PR #119 and PR #120 is folded into the 20-car warehouse saturation train based on current `develop`. This avoids re-running duplicated stale-base CI while preserving the prepared architecture, character, audio and fauna intake lanes.

Status: **CONSOLIDATED / OLD PREP PRS SUPERSEDED**.

## 2026-09-27 - 20-car warehouse saturation train

Owner requested aggressive but orderly warehouse saturation and a much longer production sequence.

Registered scope:
- One preparation train with **20 coherent warehouse cars**, not 20 competing runtime branches.
- Cars cover global PBR surfaces, pastoral architecture, hero character bases, humanoid animation, Shire audio, music, voice pipeline, vegetation, water/coast, caves/ruins, fortifications, enemies, hero creatures, battle sets, VFX, UI/localization, terrain, Part II/III region kits, general props and warehouse coverage/dedupe.
- Source selection follows the Master External Resource Bible / GlobalWarehouseSourceRegistry rule: best-fit 1-3 source lanes per slot; no blind provider mirroring.
- Public/source-compatible staging may run through existing provider scripts. Authentication/account/purchase/manual-license sources remain candidate/manual lanes.
- Every staged payload remains evidence-gated by source/license/receipt/SHA256; no preparation report can promote to READY_FOR_IMPORT.
- Runtime/import promotion stays serialized behind exact-head gates even while preparation runs in parallel.

Status: **REGISTERED / PREPARATION IMPLEMENTED / VALIDATION PENDING**.

## 2026-09-27 - P1C01 material train scope expansion

Owner requested a larger monitored production train. The active material batch is expanded coherently rather than opening many tiny branches:

- Poly Haven staging/intake scope increases from 8 to all 16 already-authorized Shire/Bag End surface candidates.
- External promotion remains fail-closed: no candidate may advance beyond `AUTHORIZED_FOR_STAGING` without real warehouse source/license/receipt/SHA256 and prepared-file QC.
- The preparation script now carries bounded specular response through generated MTL `Ks` while keeping the one-albedo low-spec runtime contract.
- Pre-Unreal enforces the expanded material-wave contract.
- No new chapter, no foliage-density increase and no visual/device acceptance claim are introduced by this expansion.

Status: **IMPLEMENTATION EXPANDED / ENGINE VALIDATION BLOCKED BY RUNNER HEALTH**.

## 2026-09-27 - P1C01 Shire material surface-set production train

Registered before implementation under existing `REQ-WORLD-002`, `REQ-PROD-007`, `REQ-ASSET-001` and `REQ-WAREHOUSE-001`.

Scope for this batch:
- Promote the project-owned Shire TGA palette into a documented surface set rather than leaving it as an implicit MTL collection.
- Extend the production surface/foliage masters with a bounded specular response driven from authored MTL `Ks` data.
- Keep the current low-spec contract: no extra texture samples, no 4K content, no runtime synchronous heavy loads, and no foliage density increase.
- Preserve existing roughness/metallic authoring and foliage near/far parent split.
- Produce exact-head UE4.27 build/import evidence before merge; no PIE/device/visual acceptance is implied.

Train order after this batch:
1. Shire project-owned material surface set.
2. Evidence-backed external surface intake (Poly Haven) only with source/license/receipt/SHA256.
3. Shire support architecture/interior prop intake.
4. Living-world visual integration/polish under the existing P1C01 lane.

Status: **REGISTERED / IMPLEMENTATION STARTED**.

## 2026-09-27 - P1C01 player-experience convergence defect batch

Registered before implementation from source review on `develop@c79168cf385ba02f4b542940de3b089e700f1f18`.

- Bilbo authored dialogue must complete before the `ShireArrival -> LongExpectedParty` hand-off.
- Mouse look must be frame-rate independent for raw `MouseX/MouseY` input.
- Quick-load rejection must surface a player-facing failure message while retaining detailed developer logs.
- Quest triggers must re-evaluate eligibility event-driven while the player remains overlapping; no per-frame trigger Tick is allowed.
- Dialogue subtitles require bounded wrapping for the 720p target HUD.
- Map/Chronicle pause/damage policy remains a later explicit UX decision and is not silently changed in this defect batch.

Status: **REGISTERED / IMPLEMENTATION STARTED**. This entry does not promote PIE/device/visual acceptance.

## 2026-09-27 - Legacy planning roots consolidated

- Reviewed remaining unique branches before deletion rather than bulk-merging stale snapshots into current production.
- Current production truth stays with ProjectGovernor and the merged P1C01 sequence: Mega Asset Promotion -> character presentation/skeletal-animation -> Living Shire motion/fauna -> quest/audio polish -> target-device profiling -> Gate 6/7.
- Older localization and parallel-preparation branches are retained as intent/history through current Governor/backlog memory, not as active execution roots.
- Old CI/report and warehouse-audit variants are explicitly superseded where later proven infrastructure/evidence exists.
- No new world detail or canon change is authorized by this cleanup entry.

## 2026-09-26 - P1C01 C4 machine closure / D next

- C4 candidate machine evidence: Pre-Unreal #1064 SUCCESS + Unreal Build #869 SUCCESS on `e881b32da6ae9713ccc096e8f213056aeef6af76`.
- UE4.27 production import completed with `376 files, 0 failures`; warning debt returned to `defaultMat references = 0`.
- Concrete C4 foliage evidence: all five audited P1C01 foliage meshes expose `lodCount=1` only. Grass/Hedge/Shrub/TreeCanopy remain near/mid on `M_ProductionFoliage`; TreeTrunk remains on `M_ProductionSurface` with authored `Bark`.
- Because no `lodIndex > 0` exists, C4 closes with **NO far-parent binding**. `M_ProductionFoliageFar` remains available but unused until a real far LOD asset/section exists.
- Existing HISM/ISM cull bands and foliage density remain unchanged.
- C4 does not establish target-device overdraw/FPS acceptance; that remains a later profiling gate.
- Next production drop after merge: **D — fixed-state lighting / sky / fog / low-cost water**.
- Evidence state: machine-green / COMPILE-TESTED and import-observed. No new PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED, PACING-ACCEPTED, or PERFORMANCE-ACCEPTED claim.

## 2026-09-26 - P1C01 C4 foliage LOD/cull/overdraw evidence capture implemented

- Candidate branch `production/p1c01-c4-foliage-lod-cull-v1` starts C4 only after merged C3 and merged-develop exact-head machine proof.
- UE4.27 production import now audits exact P1C01 foliage mesh identities after import: `SM_ShGrassClump`, `SM_ShHedge`, `SM_ShShrub`, `SM_ShTreeCanopy`, and `SM_ShTreeTrunk`.
- For every imported foliage mesh LOD section, the commandlet emits `C4_FOLIAGE_EVIDENCE` with LOD count/index, section/material indices, authored material identity, current parent, proposed parent, decision and reason.
- Only a real `lodIndex > 0` plus an approved foliage material identity can become `FAR_LOD_ELIGIBLE_FOR_REVIEW`.
- This evidence-capture step performs no far-parent rebind. `M_ProductionFoliageFar` remains unused unless engine evidence proves a qualifying far LOD.
- Existing HISM cull bands remain unchanged: grass 1200/5200, flowers 800/3200, shrubs 1500/6500, distant tree trunk/canopy 5000/19000; no density increase.
- Gameplay IDs, save/quest state, LivingWorld ownership, collision ownership and deterministic asset paths are unchanged.
- Evidence boundary: **STATIC-VALIDATED candidate implementation** only. Exact-head Pre-Unreal + UE4.27.2 production import evidence is still required. No PIE/device/visual/performance acceptance is claimed.

## 2026-09-26 - P1C01 C3 stable foliage identity implemented

- Candidate branch `production/p1c01-c3-foliage-identity-v1` implements the prepared C3 contract in `ShireProductionImportCommandlet.cpp`.
- Exact approved authored material identities are limited to `Grass`, `Leaves`, `LeafGreen`, and `LeafGold` after trimming.
- Approved identities bind their deterministic material instances to `M_ProductionFoliage`; all other authored identities remain on `M_ProductionSurface`.
- `M_ProductionFoliageFar` remains unassigned in C3 and stays reserved for C4 after mesh/LOD/cull evidence.
- Existing material instance object paths, AlbedoTexture bindings, Color/Roughness/Metallic values, world ownership, HISM/ISM population and foliage density are unchanged.
- Pre-Unreal PG-169 now guards the exact identity set and rejects broad `Contains("Leaf")` / `Contains("Grass")` classification and premature far-parent binding.
- Evidence boundary: **STATIC-VALIDATED candidate implementation** only until exact-head Pre-Unreal and UE4.27.2 asset/editor validation succeed. No PIE/device/visual/performance acceptance is claimed.

## 2026-09-26 - C2 closure and C3 stable foliage identity gate

- C2 lightweight foliage wind is merged on `develop@1d0580926299e4fac635bcb847343a49c444d4f1` after exact-head #1030/#837 and merged-develop #1031/#838 machine success.
- C3 is the next runtime world-detail step and is intentionally narrow: only exact normalized material identities `Grass`, `Leaves`, `LeafGreen`, `LeafGold` may move to `M_ProductionFoliage`.
- C3 preserves deterministic material object paths, authored albedo/Color/Roughness/Metallic values, HISM/ISM population ownership, gameplay IDs, quest/save state, LivingWorld ownership and current foliage density.
- Broad `Contains("Leaf")` / `Contains("Grass")` inference is forbidden. Far no-WPO parent assignment remains C4 work backed by actual mesh/LOD/material-slot/cull evidence.
- No PIE/device/visual/performance acceptance is claimed from the machine closure.

## 2026-09-26 - P1C01 C4 and D world-presentation preparation

- C4 preparation now records the evidence required for far foliage treatment: actual mesh object path, material identity, LOD section, cull band, screen-size transition and masked-overdraw observation before a far no-WPO parent can be chosen.
- D preparation now defines the next world-presentation layer after C4: fixed-state Shire lighting, sky fill, bounded fog and low-cost water presentation compatible with UE4.27 / DX11 / 720p Low-Medium.
- D explicitly rejects a free-running day/night cycle, per-frame skylight/reflection recapture and expensive water reflection paths without measured justification.
- Neither preparation changes quest/save/story state, traversal ownership, LivingWorld ownership, material object paths or foliage density.
- Whole-game region packets and Master Resource Bible sourcing continue under DEC-037/038/039. SOURCE_REGISTERED, CANDIDATE, STAGED, READY_FOR_IMPORT, IMPORTED, INTEGRATED and ACCEPTED remain distinct evidence states.
- No rendered, audio, device or performance acceptance is implied by preparation.

## 2026-09-25 - Multi-threaded campaign world-state rule registered

- Post-Amon-Hen world building must track route-specific chapter states and synchronization barriers rather than assuming one global linear timeline.
- Rohan, Ring-bearer, Gondor and late-Rohan world states may prepare in parallel, but shared cinematics and global world-state transitions require source-defined synchronization.
- Explicit chapter-state assets are required for major transformations such as Isengard aftermath/flooding, Helm's Deep damage and Minas Tirith siege states; do not derive these from generic dynamic simulation.

## 2026-09-25 - Whole-game region build coverage registered

- Every canonical playable region is now represented in `Data/WholeGameWorldBuildCoverageV1.json` with a complete cross-discipline build checklist.
- The checklist is deliberately larger than visual art: it includes story-safe interaction windows, traversal, collision/navmesh, streaming/memory, NPC/fauna life, sensory audio, cinematics, localization and acceptance evidence.
- Later-region runtime work remains blocked until the P1C01 Gate 6/7 benchmark; however their asset/source/design packets may advance continuously in parallel.
- New regional details must continue to be logged here before runtime implementation.

## 2026-09-25 - Whole-game source diversity expansion from Master External Resource Bible

- The new 225-source external-resource Bible is adopted as a world-production sourcing map, not a canon source.
- Whole-game world detail may now draw from broader generic/open/licensed material, vegetation, architecture, prop, character-base, animation, VFX, audio, terrain/scanning and authoring-tool lanes while story/location identity remains governed by project canon sources.
- P1C01 remains the first fully assembled benchmark, but warehouse preparation now explicitly covers every region and biome through the nine `BigProductionBuildLaunchV1` waves.
- LOTR/fan/franchise-specific search lanes remain reference/quarantine unless separately cleared; generic sources are preferred for production building blocks.
- Real-world terrain/GIS/scanning sources inform authored fantasy terrain and material creation only; they do not redefine Middle-earth geography.
- New external world-detail assets remain subject to scale/pivot/UV/collision/LOD/material/overdraw/memory review before READY_FOR_IMPORT or integration.

## 2026-09-25 - Global world rule: playable-film safe windows

- Every major chapter/world state must be designed as: **Locked Canon Beat -> Playable Safe Window -> Locked/Bounded Set-Piece -> Persistent World-State Change -> Player Control** where chronology permits.
- Safe windows are where world detail becomes gameplay: interiors, props, NPC routines, fauna, ambient conversations, interaction objects, optional tasks, discovery, weather/audio/foley and local traversal.
- These additions exist to make the player feel physically present inside the film continuity; they must never create a contradictory route, outcome, character presence or chronology.
- Post-beat world state must visibly/sonically communicate what changed before normal exploration resumes.
- This is a whole-game world rule covering every chapter and region from the opening through the final ending. P1C01 Bag End/Shire is only the first benchmark pattern; later chapters/regions must apply the same doctrine with chapter-specific canon constraints.
- New safe-window content must still be recorded in this ledger before runtime implementation.

## 2026-09-25 - P1C01 Warehouse visual/sensory stock expansion

- New Shire-support stock is registered for later art-directed use: pastoral grass/soil/leaf-litter/path breakup, farm outbuilding silhouettes, cave/architecture support kits, multi-surface footsteps, hearth fire, wood/metal interactions and daytime bird ambience.
- These are production-support resources, not new canon claims. Hero Hobbit-hole/Bag End silhouettes and named-character identity still require project-specific art direction and approval.
- Source 11 performance rules remain binding: foliage/material overdraw, texture memory, HISM/LOD/cull cost and audio concurrency are measured before density expansion.
- All external stock must retain provenance/license records and pass format/intake review before READY_FOR_IMPORT. Animated production assets remain FBX-only; production textures remain PNG/TGA.
- Runtime world ownership, quest IDs, save keys, LivingWorld/NPC systems and merged C2 foliage integration are untouched by this preparation lane.

# WORLD DETAIL LEDGER

## 2026-09-25 - W01 P1C01 Drop C1: authored material texture binding

- Source 03 keeps the Shire pastoral/domestic visual grammar; Source 11 makes foliage overdraw/material complexity/texture memory explicit review gates.
- Existing project source already contains Shire TGA textures and MTL `map_Kd` references, but the importer previously synthesized only Color/Roughness/Metallic and did not bind the authored textures.
- C1 now binds `map_Kd` to an `AlbedoTexture` parameter after texture import and changes the generated `M_ProductionSurface` BaseColor to `AlbedoTexture * Color`.
- This is an editor production-import change only. Quest/state/AI/LivingWorld/audio/streaming/runtime asset ownership is untouched.
- C2 wind/WPO remains gated behind C1 exact-head engine proof.
- Evidence boundary: STATIC-VALIDATED only.

## 2026-09-25 - W01 P1C01 Mega Production Drop B: Hobbiton + Bag End architecture

- **Source basis:** Source 03 requires Shire/Hobbiton pastoral domestic scale, circular doors and gardens; Bag End must read as a dense lived-in Hobbit narrative hub with round geometry and deterministic state variants. Source 07 anchors F1-01 to Shire onboarding/social/birthday setup. Source 11 requires modular reuse, simple collision/visibility cost and measured target-hardware budgets.
- **Canon correction:** Tolkien places The Green Dragon at Bywater. The compact prototype previously displayed it inside the Hobbiton composition. Drop B corrects only player-visible presentation while retaining the legacy `Discover_GreenDragon` internal ID for save compatibility.
- **Implemented:** `SpawnHobbitonArchitecturePass()` adds a Bag End hero garden/property approach, four subordinate domestic garden clusters, a generic Hobbiton village common, Party Field canopy/produce dressing, and lived-in working-edge props. It reuses resident project meshes and adds no synchronous heavy load.
- **Story boundary:** quest/chapter IDs and stable story anchors are unchanged. Architecture is presentation/world-space composition only.
- **Interior boundary:** a dedicated production Bag End interior shell does not exist in the current asset bank; interior completion is explicitly deferred instead of being falsely claimed.
- **Regression guard:** PG-164 requires the architecture pass/log/canon-corrected display copy and rejects a visible Green Dragon-at-Hobbiton regression while preserving the legacy save ID.
- **Evidence boundary:** STATIC-VALIDATED until fresh exact-head Pre-Unreal + UE4.27.2 core validation; no PIE/device/visual acceptance claimed.

## 2026-09-25 - W01 P1C01 Mega Production Drop A: terrain/geography foundation

- **Source basis checked before implementation:** Source 03 defines the Shire/Hobbiton as pastoral hills, lanes, farms and Hobbit-holes with warm domestic scale, readable landmark/vista navigation, sightline/terrain-aware streaming and collision/navmesh/backtracking QA. Source 07 keeps F1-01 in the Shire as an onboarding/social/birthday mission package with deterministic mission-state ownership. Source 09 requires modular reuse, provenance and per-asset validation. Source 10 is visual/modeling aid only. Source 11 remains the systems/performance/audio authority.
- **Runtime scope:** geography only. Quest IDs, story postconditions, named-character canon state and established quest coordinates are not moved by this drop.
- **Implemented:** dedicated HISM geography groups for terraced hills, village slopes and river banks; route-framing placements across Bag End/Hobbiton -> East Fields -> Wooded Road -> Brandywine/Ferry; old repeated CP49 terrain AStaticMeshActor layer removed.
- **Performance:** explicit cull bands now cover grass, flowers, shrubs, distant trees, rocks, path stones and the new geography groups. The broad collision foundation and router grounding contract remain the gameplay safety net.
- **Asset sourcing lane:** existing project-owned Shire/Common meshes are used first. External terrain/material candidates remain item-level reviewed through the existing manifest; ambientCG/Poly Haven are preferred low-friction material/environment sources, with entitled Fab/Megascans, Quaternius and Kenney evaluated where useful. Provider listing never equals item approval.
- **Next dependency:** after this exact head is machine-green, proceed directly to Hobbiton + Bag End architecture. Do not detour into unrelated regions or reopen W00 without a concrete regression.
- **Evidence boundary:** STATIC-VALIDATED at implementation time. Fresh exact-head engine validation and owner PIE/visual review remain required.

## 2026-09-25 - W01 implementation drop 1: single-owner ambient life + budget authority

- **Runtime ownership change implemented:** `ShirePrototypeWorldBuilder` no longer directly spawns `AShireAmbientNPC` crowds. P1C01 ambient population now converges on `ALivingWorldDirector`, which already owns pooling, culling, chapter targets, danger thinning and micro-event/fauna lifecycle. Named/story `AShireNPC` actors remain builder-owned.
- **Budget drift resolved at source:** `LivingWorldEventPlan.json#region_budgets` is now the sole micro-event cap/cadence authority. `WorldLifeSaturationPlan.json` controls baseline population density only, and `ALivingWorldDirector::LoadLifeSaturationContract` no longer overwrites micro-event caps/cadence.
- **P1C01 life preservation:** `PlayRunner` is retained in the director-owned P1C01 role mix. Fauna remains available through the existing living-world event path instead of a second permanent builder-owned bird crowd.
- **Static verification on branch:** zero `SpawnActor<AShireAmbientNPC>` occurrences remain in `ShirePrototypeWorldBuilder.cpp`; the old `ShireAmbientNPC.h` include is removed; the life-saturation loader no longer reads the two micro-event budget fields.
- **Evidence boundary:** STATIC-VALIDATED only. Fresh Pre-Unreal + UE4.27.2 compile/runtime/PIE evidence is still required before calling this W01 code COMPILE-TESTED or PIE-TESTED.

## 2026-09-25 - W01 kickoff: verified sensory/reactive review intake

- W00 repair lane is closed on canonical `develop@809e56a9e1dc4b453e02a0b04b6875a71df21933`. Owner-side P1C01 PIE showed `ShireStartupGrounding: PASS chapter=P1C01 commitBarrier=yes stableSeconds=2.0 ground=yes drop=1.8 drift=0.0`, the player remained on blocking ground, and the owner reported zero same-session Output Log search matches for `Mobility is Static` and `SetStaticMesh`. This is P1C01 startup-grounding/warning-tail PIE evidence only; it is not DEVICE-TESTED, VISUALLY-ACCEPTED or PERFORMANCE-ACCEPTED.
- The owner-forwarded "Sensory & Reactive Layer" review was checked against the live W00-close head before adoption. Useful verified gaps are retained here; stale claims are corrected rather than copied.
- **Accepted gap — spatial environmental audio:** `UShireAudioSubsystem` already performs async audio loading, ambience transitions and music ducking, but the current source has no AudioVolume/attenuation/concurrency/physical-surface footstep layer. Add a P1C01-first spatial ambience/foley layer later in W01 using soft/async assets, bounded concurrency and distance/importance virtualization.
- **Accepted gap — vegetation/material motion:** current source contains no `WorldPositionOffset`, `SimpleGrassWind` or `WindDirectionalSource` implementation. Add performance-scaled foliage/grass motion through shared material-instance parameters, not per-actor Tick. Near/hero vegetation may receive richer motion; distant/repeated detail remains HISM/LOD/culling friendly.
- **Accepted gap — skeletal micro-reaction presentation:** true head/eye Look-At IK and Foot IK are not implemented. They are gated behind production skeletal FBX rigs + Animation Blueprint readiness; do not bolt expensive IK onto static proxy meshes. Use distance/significance LOD so only nearby relevant NPCs evaluate higher-cost presentation.
- **Corrected stale claim — NPC awareness/weather:** `AShireAmbientNPC` already has bounded player observation/turning, deterministic idle head-look variation, distance-throttled Tick, and inclement-weather-aware behavior/dialogue. W01 should deepen presentation, not duplicate those systems.
- **Corrected stale claim — audio architecture:** the audio system is not "silent logic"; it already owns ambience/music/voice routing, async loading, fades and ducking. The missing production layer is richer authored/spatial environmental sound and surface-aware foley.
- **Corrected stale claim — pooling:** `ALivingWorldDirector` already contains an ambient-NPC pool. The actual W01 architectural debt is duplicate direct `AShireAmbientNPC` spawning in `ShirePrototypeWorldBuilder`; ambient population ownership must converge on `LivingWorldDirector` while named/story actors remain separately owned.
- **Verified budget drift:** `LivingWorldEventPlan.json` currently caps 3 active micro-events with a 12 s cadence, while `WorldLifeSaturationPlan.json` declares 5 active micro-events with a 6 s cadence. W01 must establish one runtime authority before density increases.
- **Asset-name correction:** the forwarded review referenced `SM_ShBroadleafTree.obj`, which is not present on the verified head. Current Shire tree sources include `SM_ShTreeCanopy.obj` and `SM_ShTreeTrunk.obj`; `SM_CommonTerracedHill.obj` and the cited Shire TGA textures do exist.
- **Execution order:** (1) centralize ambient ownership/pooling, (2) reconcile living-world budgets, then continue the P1C01 production sequence: terrain/geography -> Hobbiton/Bag End architecture -> materials/vegetation -> lighting/sky/fog/water -> character presentation -> NPC/fauna/environment motion -> quest/audio polish -> target-device profiling. The sensory/reactive items above are folded into those stages rather than opened as a competing feature wave.

## Architectural stabilization directive - 2026-09-22
- Owner explicitly rejects symptom-by-symptom patching before further production expansion.
- Active mode is W00 architectural stabilization: validation is allowed/required; new features and broad content expansion are frozen.
- Grounding is a router/world invariant: bounded nearby-ground probing + walkable-slope rejection + capsule-clearance validation. Chapter-specific RuntimeSpawnFoundation pads are forbidden.
- Chapter CI must attempt P1C01-P1C08 in one sequential sweep and aggregate failures; no first-red early exit.
- Optional/future skeletal rig packages must be preflighted before async load; missing rigs use fallback without engine missing-package errors.
- Source textures are PNG/TGA only; BMP is forbidden. Current 24 BMP sources were migrated to TGA and MTL references updated.
- Duplicate-position OBJ face vertices are a source defect. The seven known affected project-owned meshes were normalized and triangulation-risk faces are now strict audit failures.
- Feature construction resumes only after the exact stabilization head passes static + compile/import + all chapter + state/transition + warning/material gates.

## Precise integration-gap closure - 2026-09-22
- Close discovered cross-system gaps immediately at source level; do not merely record them.
- NPC world-facing context now follows committed visible world identity/revision. During logical/visible mismatch, no new bounded NPC dialogue/film context may start.
- Same-world quest-stage/danger reactions remain live; the committed snapshot is used only across the async mismatch window.
- Completed character-rig streamable handles are released after actor-owned handoff so inactive rigs are not pinned for the full GameInstance lifetime.
- Chapter builders resolve production meshes only from resident async banks. Enemy bank coverage was extended for Black Rider, Moria threats and Amon Hen enemies.
- Player/named-NPC/enemy production proxies use resident-only soft resolution; primitive fallback remains safe until skeletal production rigs become available.
- Production audio no longer performs synchronous USoundBase loading.
- Continuous audit now rejects non-engine synchronous LoadObject and verifies committed-context/rig-handle invariants.
- Defect closure still requires fresh exact-head UE4.27 compile/runtime proof after W00 runner repair.

## Deep organization / cross-system audit - 2026-09-22
- Audit checkpoint exact head: `17689b194ddca281aa9881b9ac50594712a65df6`.
- Management drift found: REQ-CAMERA-001 was accepted into ProjectGovernor but not mapped into MasterExecutionRoadmap, causing Pre-Unreal #685 PG-078 failure. Mapping/snapshot reconciliation is now applied.
- Cross-system simulation: LivingWorldDirector is committed-world synchronized, but ShireNPCContextSubsystem derives regional mood/profile availability/film dialogue directly from QuestSubsystem logical chapter/route. Register a committed-world context bridge before scaling NPC intelligence.
- Character rig streaming is async and fallback-safe, but rig handles currently persist for GameInstance lifetime. Measure multi-chapter skeletal residency before full-cast rollout; add bounded inactive-cast release only if safe and needed.
- Ambient NPC pooling exists and disables pooled tick/visibility/collision; previous “pooling missing” audit text was stale.
- Remaining runtime synchronous LoadObject debt is still high in world builders and present in player/named-NPC fallback styling. Migrate incrementally after runner recovery; do not replace one stable loader with a competing manager.
- Public/Private physical source migration remains pending and must stay isolated from gameplay changes.
- Next priority after this audit: W00 runner/Engine Content ACL repair and fresh exact-head validation.

## Final pre-runner warehouse saturation batch - 2026-09-22
- Owner authorized one final source-safe warehouse fill before switching focus to the UE4.27 runner ACL repair.
- Added only verified official KayKit public-GitHub CC0 lanes: Restaurant Bits (food/kitchen/interior support), Halloween Bits (selective cemetery/crypt/dark-region props), and City Builder Bits (manual-filter generic civic props only).
- City Builder stock is explicitly period-filtered: modern-looking items are not eligible for Middle-earth integration merely because the archive is staged.
- These are STAGED candidates only after workflow receipts exist. No READY_FOR_IMPORT / IMPORTED / INTEGRATED / ACCEPTED promotion is implied.
- After this batch, active priority returns to W00 runner/exact-head unlock; broad warehouse sourcing pauses except blocker-safe bookkeeping until the runner gate is repaired.

## Embodied third-person camera direction - 2026-09-22
- Owner explicitly rejects top-down/isometric/RTS-style normal gameplay. Shire Journey must feel like directly inhabiting Middle-earth through the active character.
- Default gameplay perspective: **third-person action-adventure**, camera behind or slightly over the controlled character, broadly comparable to GTA V / Red Dead camera relationship rather than a strategy camera.
- Tune distance/height/FOV/camera collision contextually for Hobbit/Human/Elf/Dwarf scale, interiors, traversal, interaction and combat readability.
- Temporary cinematic framing is allowed only as bounded presentation; control must return cleanly to the embodied gameplay camera.
- Acceptance requires PIE review of world-scale immersion, interaction reach/readability, camera collision and interior/exterior transitions. This direction alone is not PIE/DEVICE/VISUAL acceptance.

## Completion Wave Map / Milestone Ladder - 2026-09-22
- Owner requested a bounded finish map from the current approximately 40/100 whole-game planning position to 100/100, expressed as production waves rather than hours.
- Planning unit is a **major production drop**, not an individual Git commit or raw file upload. One drop should be coherent enough to review, validate and roll back as a unit.
- The completion map uses 12 remaining waves totaling 60 planning percentage points. These percentages are roadmap estimates only; they are not compile/PIE/device/visual acceptance evidence.
- Every wave closes only on its listed exit criteria. Asset-only staging, code-only implementation or a green static gate cannot by itself close a visual/runtime wave.
- Expected repository activity is roughly 30-40 major coherent production drops across the remaining waves; actual Git commits may be higher because fixes/documentation/validation can split a drop.
- Shire/P1C01 remains the first visible benchmark. Part II/III runtime opens only after the relevant gates, while warehouse/preproduction may continue in parallel.

## Character visibility / warehouse-to-runtime bridge - 2026-09-22
- Owner priority: stop letting asset-bank growth remain invisible; keep broad legal/free sourcing active, but turn the first proven humanoid/enemy rig stock into a real import path as soon as engine gates permit.
- Register this before implementation: audit staged character archives for usable FBX/texture inventory, strengthen receipt/hash/license validation, expand only from verified official/public sources, and close the documented FBX/PNG/TGA importer gap without treating static OBJ conversion as rigging.
- Shire remains the first visible benchmark. Part II/III assets stay warehouse/preproduction only; technical enemy-rig QA stock must not be treated as canon population.
- Acceptance boundary: archive presence or a provider README can prove source/package facts only. Skeletal import, skin/deformation, locomotion, runtime replacement, PIE/device performance and visual acceptance each require their own evidence.
- Runtime architecture remains soft/async for heavy character packages and pooled for crowd-scale NPC reuse.


Purpose: retain visual, material, life, ambience and world-detail ideas discovered during the post-CP54 verification cycle and promote them deliberately during resumed production.

## Post-freeze rule
- The post-CP54 verification freeze is complete and CP55+ production is authorized.
- Promote ideas in bounded batches behind Pre-Unreal and real UE4.27 regression gates.
- Preserve story/save/route topology and the target-laptop performance budget.
- Shire remains the visual/readability reference, but region-appropriate differences are encouraged.
- Do not convert an idea into a validated/accepted claim until the corresponding implementation and evidence exist.

## P1C01 — Shire
### Ideas
- Better performance-safe ground material variation.
- Stronger cloth/material identity for market/party props.
- Lighting polish only after actual PIE/FPS baseline is known.
### Verification discoveries
- Post-CP54 verification pass owner-confirmed complete; numeric device measurements were not retained in chat.

## P1C02 — Bree
### Ideas
- Rainy-night material/lighting differentiation.
- Inn/street material quality pass after Shire reference is accepted.
### Verification discoveries
- Post-CP54 verification pass owner-confirmed complete; numeric device measurements were not retained in chat.

## P1C03 — Weathertop/Ford
### Ideas
- Weathered stone/soil material upgrade.
- Verify whether atmosphere reads as distinct without expensive VFX.
### Verification discoveries
- Post-CP54 verification pass owner-confirmed complete; numeric device measurements were not retained in chat.

## P1C04 — Rivendell
### Ideas
- Pale stone, water and foliage material quality pass.
### Verification discoveries
- Post-CP54 verification pass owner-confirmed complete; numeric device measurements were not retained in chat.

## P1C05 — Road/Caradhras/West Gate
### Ideas
- Snow/rock material upgrade and weather presentation after performance baseline.
### Verification discoveries
- Post-CP54 verification pass owner-confirmed complete; numeric device measurements were not retained in chat.

## P1C06 — Moria
### Ideas
- Stone/metal/brazier material polish; preserve civilian-empty design.
### Verification discoveries
- Post-CP54 verification pass owner-confirmed complete; numeric device measurements were not retained in chat.

## P1C07 — Lothlorien
### Ideas
- Golden foliage/wood/material differentiation.
### Verification discoveries
- Post-CP54 verification pass owner-confirmed complete; numeric device measurements were not retained in chat.

## P1C08 — Anduin/Amon Hen
### Ideas
- River/boat/ruin material differentiation.
### Verification discoveries
- Post-CP54 verification pass owner-confirmed complete; numeric device measurements were not retained in chat.

## Cross-region backlog
- True day/night cycle only if target-laptop performance allows it.
- Real rain/snow/weather VFX only after current fixed weather-context behavior is verified.
- Material upgrades should be measured against 720p Low-Medium and the 30 FPS floor target.
- Prefer source quality and runtime efficiency over raw asset count.


## Cross-system QA immune-system idea — 2026-09-21
- Owner-approved external programmer proposal: build a layered automated QA immune system for recurring game-breaking defects.
- Adopt Unreal Automation Framework / FAutomationTestBase as an additional engine-level layer, not a replacement for the existing headless runtime harness.
- First wave: exact-head automation runner, save-schema/default-state contract, chapter streaming package integrity, and strengthened startup-grounding regression.
- Later waves: deterministic authored collision/traversal probes, navigation stuck coordinates, production-rig animation readiness, transition hitch measurement, memory-growth/churn soak, material/shader integrity and exact-SHA reports.
- Corrections: do not use random world locations, universal Z<0, fixed 4 GB/100 ms thresholds, or proxy-NPC T-pose rules as project-wide truth. Use reproducible authored probes and measured target-device budgets.
- No automated layer may promote PIE/device/visual/pacing acceptance by itself.


## Cross-system visual-performance optimization proposal — 2026-09-21
- Owner-approved programmer proposal reviewed against the live UE4.27.2 project.
- Adopt: soft/asynchronous heavy-asset ownership, HISM/ISM for repeated detail, explicit culling, role-appropriate LODs, shared material-instance families, and event/timer/throttled logic over unnecessary Tick.
- Already present: chapter asset banks use FSoftObjectPath + FStreamableManager; WorldDetailCluster uses HISM + cull distances; world builders are non-ticking; DeepProjectAudit rejects LoadObject inside Tick.
- Corrected: do not force World Composition over the working chapter-router architecture; evaluate it only if later authored contiguous sublevels need it.
- Corrected: baked Lightmass is selective for authored static scenes, not a blanket rule for runtime-generated chapter geometry.
- Corrected: Distance Field Shadows are a benchmark candidate, not assumed cheaper on the ~2 GB VRAM target.
- Corrected: Material Instances are preferred, but MIDs are only for runtime variation; LODs are role/budget based rather than blindly mandatory for every tiny asset.
- Machine-readable plan: `Data/VisualPerformanceOptimizationPlan.json`.
- Runtime lighting/world-topology changes wait for startup/QA gate health and target-device profiling.


## Comprehensive foundation convergence — 2026-09-21
- Owner authorized one integration train instead of continued isolated repair/proposal branches.
- Ordered convergence: startup grounding -> automated QA -> visual-performance guardrails -> V10 regional living world -> transactional chapter transition synchronization.
- New features remain gated until this foundation earns exact-head machine proof.
- After merge: ambient pooling, residual synchronous-load burn-down, living-NPC witness/share/learn, character production, and cinematic world-art passes resume in dependency order.


## Cross-system playability audit — 2026-09-22
- Rechecked the owner-forwarded Work review against integration head `170ebd857bece56a6d7f76f4928efe0eb3426af2` before promotion.
- Confirmed: chapter checkpoint capture waits only one player Tick even though chapter world commit is asynchronous; this is not a safe persistence barrier.
- Confirmed: RestoreSaveSnapshot can apply the saved transform after logical chapter restore without first proving the matching world revision is committed.
- Confirmed: failed world-swap rollback rebuilds the prior builder where possible but leaves player movement held and does not restore one coherent prior world/quest/player transaction.
- Confirmed: ambient baseline origins use approximate Z with no ground trace; ambient body meshes have collision disabled, so ground/wall placement needs a bounded trace/placement contract plus rendered observation.
- Confirmed performance debt: living baseline population uses SpawnActor/Destroy rather than pooling, and AShireAmbientNPC visual setup still performs direct LoadObject calls. Do not expand density until pooled reuse and asynchronous asset ownership are designed around the existing chapter-bank system.
- Source organization remains 62 flat runtime .h/.cpp files with zero migrated entries. Preserve DEC-003: Public/Private movement is a separate path-only maintenance pass, not part of the transition repair.
- Asset-count correction: the indexed production inventory reports 24 image files total, not 24 BMP files. Seven explicit Shire BMP paths are currently visible in the inventory; do not state a larger BMP count without repository evidence.
- Priority order: exact-head static gate -> committed-world persistence/rollback repair -> engine gates -> ambient ground/pooling/async-load debt -> later source-layout migration and production expansion.
- Evidence boundary: these are source-confirmed findings and planning records only. No COMPILE-TESTED, PIE-TESTED, DEVICE-TESTED or VISUALLY-ACCEPTED promotion follows from this audit.


## Character humanization production wave V7 - 2026-09-22
- Owner explicitly prioritized visible, natural, human-readable character quality instead of continuing to look at modular dolls/placeholders.
- This is an extension of REQ-CHAR-001/002/004, not a new chapter or alternate gameplay system.
- Existing character OBJ pieces are retained only as static/prototype fallback. Animated production delivery is FBX-only and must include actual skeleton/skin/deformation work.
- Source basis reviewed before implementation: Character & Relationships Bible, 3D Visual Asset Atlas, CharacterProductionMatrix and CHARACTER_PERFORMANCE_STANDARD.
- First production order: Frodo -> Gandalf -> Sam -> Aragorn -> Gimli/Legolas -> Merry/Pippin/Boromir.
- Runtime direction: central soft/async character-rig residency via FStreamableManager; no final heavy skeletal LoadObject path.
- Import direction: production importer accepts PNG/TGA and a dedicated Characters/Rigs FBX path without changing the legacy static OBJ bank in-place.
- Natural visual acceptance remains separate from source implementation and requires real FBX assets plus UE/PIE/device evidence.


## Cinematic asset-source expansion — 2026-09-22
- Owner forwarded an asset-manager sourcing directive prioritizing a visually full, cinematic private-project warehouse for characters, creatures, weapons, architecture, materials and environments.
- Persisted discovery sources now include DeviantArt 3D/XNALara ports, SFMLab, Open3DLab, Nexus Mods and a separate ArtStation Marketplace path, alongside the already tracked CGTrader, TurboSquid, Sketchfab, Quixel Megascans, Fab and legacy Unreal Marketplace sources.
- Storage in the discovery registry is not automatic production approval. Ripped/ported proprietary film/game assets remain blocked unless explicit reuse rights/provenance are established for the specific item.
- Visual target remains high-fidelity/cinematic; when exact source reuse is not cleared, prefer legally reusable high-quality bases, project-authored reconstruction or commission rather than accepting primitive placeholders.
- Final animated-character intake remains skeletal FBX with genuine rig/skin/deformation; production textures remain PNG/TGA and heavy runtime assets follow soft/asynchronous loading.


## Cinematic audio warehouse directive — 2026-09-22
- Owner forwarded a dedicated audio-engineering directive: the project should sound as intentionally produced as it looks, with region-specific ambience, fauna, foley, creature/combat effects, dynamic music and character voice routed through the existing audio system.
- Registered discovery sources: ElevenLabs, BOOM Library, Pro Sound Effects, LOTR Complete Recordings (reference), Blu-ray center-channel dialogue (reference), and classic EA LOTR audio (reference), in addition to previously tracked licensed/review sources.
- UShireAudioSubsystem already owns logical routing/crossfades/ducking; the missing layer is the authored/approved offline bank itself.
- Real-actor voice cloning, extracted film dialogue, commercial soundtrack recordings and extracted proprietary game audio are not automatically production-approved by private-project intent; authorization/rights remain item-level gates.
- First implementation priority is a dense P1C01 Shire bank, then Bree, Moria, Lothlorien and Anduin/Amon Hen, with 3D attenuation/concurrency and target-laptop profiling.


## Trilogy warehouse-first production directive — 2026-09-22
- Owner changed the production emphasis: the project must no longer treat final characters/world/audio as a late downstream concern. Build and maintain a trilogy-wide asset warehouse in parallel with foundation repair so visible content coverage is never ad hoc or forgotten.
- Warehouse scope is trilogy-wide preproduction/asset readiness, not permission to skip current runtime gates. Runtime integration of new chapters/features remains gated by the existing dependency/validation rules.
- Required stock families include major/supporting named characters, generic NPC/crowd families, enemies, creatures, fauna, culture/faction kits, all major film locations/state variants, architecture, terrain, vegetation, props, materials, weapons/equipment, animation, VFX, audio, cinematics and UI/readability support.
- Source basis for the first master inventory: Source 02 character roster/dossiers; Source 03 location catalog/state variants; Source 04 peoples/cultures/artifacts; Source 05 battles/weapons/creatures; Source 11 source-governance/audio/cinematic rules; supplied trilogy screenplays for supporting-cast/scene demand.
- Warehouse completeness and runtime completeness are separate: an asset slot can be catalogued before a final file exists, but it may not be called READY/APPROVED until the actual asset/provenance/format/compatibility requirements are satisfied.
- Priority is now WAREHOUSE-FIRST + VERTICAL-SLICE: make the stock catalog comprehensive across F1-F3, then aggressively acquire/author usable content while P1C01 remains the first fully assembled visual benchmark.


## Multi-region world-foundation parallel lane — 2026-09-22
- Owner explicitly directed that P1C01 Shire remain the first assembled benchmark but must not monopolize production attention. World foundations for the rest of the trilogy are to be established in parallel as warehouse/preproduction work.
- This lane covers reusable architecture kits, terrain/material families, vegetation/ecology, props, faction/population kits, audio beds, lighting/atmosphere, VFX and traversal/collision requirements for Bree, Weathertop, Rivendell, Caradhras, Moria, Lothlorien, Anduin/Amon Hen, Fangorn, Edoras/Meduseld, Helm's Deep, Isengard, Emyn Muil, Dead Marshes, Ithilien/Henneth Annun, Minas Tirith, Osgiliath, Minas Morgul, Cirith Ungol/Shelob's Lair, Pelennor, Paths of the Dead, Black Gate, Mordor/Gorgoroth, Mount Doom and Grey Havens.
- Runtime chapter implementation for later parts remains gated. The new work is preproduction/warehouse/shared-foundation preparation, not permission to bypass Gate 6/7.
- Shared-kit principle: build culture/material/biome families once and reuse across related locations instead of authoring every city from zero. Examples include Gondor pale-stone/citadel kit, Rohan timber-hall/stable kit, Mordor black-metal/ash/fortification kit, Elven stone/wood/foliage kit, Dwarven monumental-stone kit and Shire/Bree rural timber/plaster kit.
- Performance remains bounded for the target laptop: repeated world detail must prefer ISM/HISM + culling/LOD, high-cost hero architecture stays selective, and world stock may be large on disk without being resident in memory at once.

## 2026-09-26 - P1C01 D + bounded Mega Asset Promotion launch

- Owner direction: continue immediately from merged C4 into **D — fixed-state lighting / sky / fog / low-cost water** while starting the large asset-promotion effort in parallel.
- Runtime ownership stays narrow: D may change presentation only. Quest/save/story topology, traversal anchors, LivingWorld ownership, NPC pooling and C2/C3/C4 foliage density/material identity remain unchanged.
- D water scope is limited to the established Shire water bodies already represented in P1C01 (The Water by the Mill and the Brandywine/Bucklebury Ferry composition). Default presentation is an opaque, low-cost production material path with no planar reflection, no scene-capture dependency and no per-frame CPU simulation.
- Mega Asset Promotion reuses `Data/P1C01WarehousePromotionQueueV1.json` and `Data/ProductionAssetPromotionPolicyV1.json`; this is not a second inventory. Work may advance through staging/intake QC, but no item is promoted to `READY_FOR_IMPORT` without provider/source/license, local staging receipt, SHA256 and class-specific QC.
- Final animated production assets remain FBX-only. Final production textures remain PNG/TGA; BMP cannot be accepted as final promotion evidence. Heavy runtime assets stay soft-referenced/asynchronously owned; crowds remain pooled and repeated detail remains ISM/HISM + LOD/culling.
- Evidence boundary: **EXECUTION AUTHORIZED / NOT YET VALIDATED**. C4 candidate exact head passed Pre-Unreal #1070 and Unreal Build #875 before merge. D needs its own exact-head machine proof plus later rendered/device evidence; no PIE/device/visual/performance acceptance is claimed here.
## 2026-09-30 - P1C01 overnight preparation reconciliation (no new runtime feature)

- W00 packaged-runtime machine closure is inherited from merged PR #184 exact head `d6ca8aac03f5a1da07609e61e790ddf8faad8eed`: Pre-Unreal #1435 and Unreal Build #1108 succeeded, including real Windows packaging, 37/37 Runtime Data payload verification and packaged executable observation.
- The live P1C01 consolidation PR remains a separate exact-head gate. Its parent head `66fd2c38aa5d6db815c4e6eaba957add89094b0d` had Pre-Unreal #1461 green while Unreal Build #1134 was still queued, so no runtime expansion or merge was authorized from that proof.
- Preparation advanced without runtime feature expansion: direct F1-01/F1-02/F1-03 source review, two explicit zero-silent-omission rows (knowledge/skip equivalence and safe optional-window expiry), warehouse/source QC contract review, stronger static disposition guards, and a targeted save-schema history reconstruction.
- Reachable `develop` history now proves explicit save schemas 3, 4, 5 and 6. Versions 1/2 remain undocumented; no migration behavior is invented.
- Ownership remains unchanged: LivingWorldDirector owns population/pooling/events, ShireNPCContextSubsystem owns NPC context/knowledge/schedules, and ShireQuestSubsystem owns quest/progression truth.
- Low-spec constraints remain UE4.27.2, DX11 1280x720 Low-Medium, 6th-gen i7 / 8 GB RAM / ~2 GB VRAM, 30 FPS floor target, soft/async heavy loading, pooled transient crowds, ISM/HISM + LOD/culling, FBX animated assets and PNG/TGA final textures.
- Evidence boundary: preparation/static bookkeeping only. No PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED or PERFORMANCE-ACCEPTED promotion is made here.

## 2026-09-30 - P1C01 BAG_END_LIVED_IN_PASS hero chapter registration

- Predecessor SHIRE_WORLD_DENSITY is machine-green: PR #192 exact head `5a489781c23ed582f9203bd5c6df20d969fef467` passed Pre-Unreal #1467 and Unreal Build #1140; merged `develop@6abc675cacfe9c9b37a63420d72d0b1621b3b7c6` passed Pre-Unreal #1468 and Unreal Build #1141.
- Registered next serialized runtime car: **BAG_END_LIVED_IN_PASS / P1C01_BAG_END_HERO_CHAPTER_V1**.
- Source intent: Bag End becomes the dominant lived-in Hobbiton hero landmark with warm domestic approach framing and deterministic Birthday/departure variants. Existing F1-01/F1-02 locked outcomes and story anchors are not moved.
- Runtime budget before implementation: <=3 zero-Tick/no-collision HISM clusters, <=36 HISM instances, <=12 unique lived-in props, <=6 state-variant props per state, ambient population remains 18.
- State ownership: ShireQuestSubsystem delegates only; no Tick, global scan, duplicate story authority or extra AI population.
- Asset boundary: P1C01 already-resident production meshes only. Missing optional detail skips without load. Dedicated Bag End interior is still **CONTENT_PENDING** because the repository has no approved production interior shell/kit.
- Evidence boundary: **REGISTERED / RUNTIME NOT IMPLEMENTED**. No PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED or PERFORMANCE-ACCEPTED claim.

## 2026-09-30 - P1C01 BAG_END_LIVED_IN_PASS runtime implementation

- Implemented the registered Bag End hero pass after its ledger/data registration.
- Exterior composition uses only P1C01 resident meshes and bounded zero-Tick/no-collision dressing: 3 HISM clusters, 34 instances and 8 static lived-in props.
- Added deterministic Birthday and Departure prop sets (5 each) controlled through existing ShireQuestSubsystem delegate events. No extra state owner, per-frame scan, synchronous load or AI population increase was introduced.
- Existing Bag End story triggers/NPC anchors are not moved.
- Interior remains CONTENT_PENDING pending an approved FBX/provenance modular shell.
- Evidence boundary: **SOURCE-IMPLEMENTED / exact-head Pre-Unreal + UE4.27.2 pending**. Human PIE/device/visual/performance evidence remains separate.

## 2026-09-30 - P1C01 PARTY_AND_SOCIAL_LOOP chapter registration

- Predecessor BAG_END_LIVED_IN_PASS is machine-green: PR #193 exact head `45ea51bc64609d2781a4bb5bdbbdbdef3c9094a1` passed Pre-Unreal #1469 and Unreal Build #1142, then merged as `488159e0eeb2f2c6ee892ef4018da8f60d117744`.
- Registered next serialized runtime car: **PARTY_AND_SOCIAL_LOOP / P1C01_PARTY_SOCIAL_LOOP_V1**.
- Source scope is F1-01 only: birthday setup/social onboarding/fireworks. ACT_F1_01 requires tables, food, decorations and guest interactions; ACT_F1_02 requires select/place/aim/time launch safely; ACT_F1_03 permits a comic stealth/interact firework mishap with fixed outcome.
- Locked outcome remains unchanged: Bilbo leaves and the Ring passes to Frodo.
- Runtime budget before implementation: <=4 HISM clusters / <=56 decorative instances, <=16 unique party props, <=8 state-variant props, <=6 new optional trigger/challenge actors, ambient population remains 18.
- Optional content must expire at story escalation, be safe to abandon/retry, and never own mandatory progression.
- Evidence boundary: **REGISTERED / RUNTIME NOT IMPLEMENTED**.

## 2026-09-30 - P1C01 PARTY_AND_SOCIAL_LOOP runtime implementation

- Implemented the registered F1-01 party/social/fireworks car after BAG_END_LIVED_IN_PASS exact-head machine closure.
- Party-field presentation now adds 4 zero-Tick/no-collision HISM clusters (48 configured instances), 14 authored non-collision party props, 4 setup-state props and 4 celebration-state props.
- Story-state visibility remains event-driven from ShireQuestSubsystem: setup before PartyArrival, celebration after PartyArrival, all casual party variants hidden after BilboDisappearance.
- Birthday setup now has three sequential optional local beats for decorations, food stores and guest readiness; each expires at PartyArrival and owns no mandatory progression.
- Gandalf Fireworks is implemented as a bounded timing activity and Dragon Firework Mishap as a bounded stealth-lite activity with a fixed optional completion beat. Both exist only from PartyArrival until BilboDisappearance.
- Activity rewards use the existing ContextualSideActivityPlan -> JourneyDiscoveryRewardPlan -> ShireQuestSubsystem first-time discovery path, preserving anti-farm/save behavior.
- P1C01 population target remains 18. No new AI owner, Tick loop, synchronous heavy load or crowd Spawn/Destroy churn was introduced.
- Locked F1-01 outcome remains Bilbo departure + Ring transfer; no copied book/film dialogue was added.
- Evidence boundary: **SOURCE-IMPLEMENTED / exact-head Pre-Unreal + UE4.27.2 pending**. PIE/device/visual/pacing/performance remain separate.

## Future Ancient Lore candidate — Carcharoth / Huan / Beren legend

- User reference captured from a Carcharoth lore post + wolf mood-art image.
- Classification: **FUTURE WORLD DETAIL / ANCIENT LORE / CHRONICLE CANDIDATE**, not an active Part I runtime feature.
- Canon guard: Carcharoth must **not** appear as a living contemporary creature/boss in P1C01 or the current Part I journey. Any implementation must preserve the First Age historical placement and current-age chronology.
- Safe future uses: Chronicle/Ancient Tales entry, source-grounded manuscript/book inspection, Rivendell lore reference, mural/carving/storytelling detail, or optional bestiary-history presentation.
- Visual reference rule: supplied artwork is mood/reference only; do not copy it 1:1 or treat it as a production asset. Any future production depiction must be original.
- Story rule: no verbatim Tolkien or film dialogue/text. Any game-facing prose must be original and source-grounded.
- Scope gate: no runtime implementation until the current P1C01 Gate 6/7 lane is closed and the item is re-verified against Sources 01/04/05 and Tolkien source material.
- Status: **RECORDED / BACKLOG ONLY / NOT AUTHORIZED FOR RUNTIME**.

## 2026-10-01 - P1C01 Gate 6/7 and local visible-world tooling reconciled

- Gate 6/7 evidence infrastructure and local visible-world bootstrap are carried forward onto current develop instead of merging stale branch snapshots wholesale.
- Target-device contract remains fail-closed: DX11, 1280x720, 30 FPS floor, 8 GB RAM, ~2 GB VRAM, with Balanced Medium + selective High visual intent.
- The local bootstrap reuses the established production importer and Entry map; it creates no parallel runtime owner, no synchronous-heavy asset path, no crowd Spawn/Destroy policy change, and no permanent startup-map mutation.
- Animated final production delivery remains FBX-only; new production textures remain PNG/TGA; legacy OBJ source inputs remain static/source fallback only.
- No Gate 6/7, PIE, device, visual, pacing or performance acceptance is claimed by this reconciliation.


## 2026-10-01 - P1C02 Bree preproduction lane opened

Registered against the already-authorized **F1-04 Bree & Weathertop Mega Source Superpack V1**; this does not open P1C02 runtime.

- Runtime chapter: **P1C02 - Bree / The Prancing Pony**.
- Predecessor runtime gate remains: **P1C01 Gate 6/7 ACCEPTED**.
- Canon entry remains the F1-03 locked outcome: the Hobbits reach Bree.
- Bree world grammar remains source-locked: crossroads town; timber/stone; rain; gates; crowded inn; social stealth, supplies, rumors and pursuit pressure; night-arrival/departure states.
- Tolkien spatial anchors retained without reproducing source dialogue: Bree under Bree-hill, gated night access, old road-crossing identity, a large inn functioning as a social/news hub, and a mixed population of Men and Hobbits.
- P1C02 source work reuses `Data/F104BreeWeathertopMegaSourceSuperpackV1.json` and the persistent warehouse; no duplicate mega-download lane is created.
- Existing `SourceAssets/Production/World/Bree` assets remain **STATIC_SUPPORT_STOCK_REQUIRES_QC**, not visual acceptance.
- Heavy runtime assets remain soft/async; animated final character candidates remain FBX-only; textures PNG/TGA; background populations pooled; repeated detail ISM/HISM + LOD/culling.
- No P1C02 gameplay/story/runtime mutation is authorized by this registration.

Status: **SOURCE PREPRODUCTION OPEN / RUNTIME PREDECESSOR-GATED / NO PIE-DEVICE-VISUAL ACCEPTANCE CLAIM**.


## 2026-10-01 - P1C03 Weathertop / Ford preproduction lane opened

Registered against the already-authorized **F1-04 Bree & Weathertop Mega Source Superpack V1** with explicit handoff awareness toward **F1-05 Rivendell & Fellowship**. This does not open P1C03 runtime.

- Runtime chapter: **P1C03 - Weathertop / Ford**.
- Runtime predecessor gate remains: **P1C02 Gate 6/7 ACCEPTED**.
- F1-04 critical path remains source-locked: Aragorn guides; Ring use raises danger; the Weathertop camp is attacked; Frodo is wounded; the locked outcome is the party racing for Rivendell.
- Weathertop world grammar remains source-locked: ruined hilltop watchtower, ancient stone ring, exposed skyline, wind/darkness, camp tension, travel decisions, defensive combat and Nazgul encounter support.
- Ford preparation is restricted to the source-supported wounded-pursuit / river-crossing handoff into Rivendell; no independent Ford outcome or early Rivendell state is invented.
- Existing `SourceAssets/Production/World/Weathertop` stock remains **STATIC_SUPPORT_STOCK_REQUIRES_QC**.
- Source work reuses `Data/F104BreeWeathertopMegaSourceSuperpackV1.json`, persistent warehouse stock and the existing F1-05 handoff pack; no duplicate heavy payload lane is created.
- Animated final character candidates remain FBX-only; production textures PNG/TGA; heavy runtime assets soft/async; repeated detail ISM/HISM + LOD/culling; populations remain pooled.

Status: **SOURCE PREPRODUCTION OPEN / RUNTIME PREDECESSOR-GATED / NO PIE-DEVICE-VISUAL ACCEPTANCE CLAIM**.


## 2026-10-02 — P1C01 warehouse-first world expansion V1

- Registered a warehouse-first acquisition/build batch covering Bag End hero ring, Hobbiton village, Shire road corridor and Bucklebury/Ferry.
- Existing warehouse evidence is consumed before new acquisition; new lanes prioritize Poly Haven/ambientCG for PBR, licensed/manual hero character and motion sources, optimized vegetation, professional audio/VFX and terrain-reference tooling.
- Quaternius remains BLOCKED_MANUAL after prior zero-payload provider evidence; it cannot stop independent lanes and no undocumented archive URL may be fabricated.
- Animated production candidates remain FBX; production textures PNG/TGA with 1K/2K default; repeated world assets use HISM/ISM/LOD/culling; heavy runtime assets remain soft/async.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD STATIC VALIDATION PENDING**. No PIE/device/visual/performance acceptance claim.


## 2026-10-02 — P1C01 warehouse-first world expansion V1

- Registered a warehouse-first acquisition/build batch covering Bag End hero ring, Hobbiton village, Shire road corridor and Bucklebury/Ferry.
- Existing warehouse evidence is consumed before new acquisition; new lanes prioritize Poly Haven/ambientCG for PBR, licensed/manual hero character and motion sources, optimized vegetation, professional audio/VFX and terrain-reference tooling.
- Quaternius remains BLOCKED_MANUAL after prior zero-payload provider evidence; it cannot stop independent lanes and no undocumented archive URL may be fabricated.
- Animated production candidates remain FBX; production textures PNG/TGA with 1K/2K default; repeated world assets use HISM/ISM/LOD/culling; heavy runtime assets remain soft/async.
- Status: **SOURCE-IMPLEMENTED / EXACT-HEAD STATIC VALIDATION PENDING**. No PIE/device/visual/performance acceptance claim.


## 2026-10-02 - Whole-game chapter preproduction mega-train registration

- Registered the 23 normalized trilogy chapter packages from **F1-01 through F3-07** as source/preproduction production waves inside `ContinuousProductionWaveQueueV2`.
- This registration introduces no new canon outcome and does not alter any chapter postcondition; it mirrors the existing Story/Mission Bible chapter spine and location/state contracts.
- P1C01 remains the sole runtime-changing production lane. All later chapter packets are explicitly source/preproduction only until predecessor Gate 6/7 acceptance.
- Preproduction domains per chapter: canon/state contract, location/world packet, roster/character needs, props/materials/vegetation, animation/encounters, audio/VFX, quest/checkpoint/save contract, streaming/performance plan and QA matrix.
- Status: **SOURCE/PREPRODUCTION REGISTERED / NO FUTURE RUNTIME ACTIVATION**.

## 2026-10-02 - P1C01 visible-world mega execution registration

- Registered a source-only production continuation specifically to shorten time-to-visible-Shire while M001 Frodo skeletal validation remains on the serialized runtime lane.
- This execution is not a new feature and does not open a second runtime authority. It activates the already-registered P1C01 warehouse-first cells for **Bag End hero ring, Hobbiton village, Shire road corridor and Bucklebury/Ferry**.
- Priority source domains are the already-authorized M003-M007 visual stack: production surfaces/materials, architecture/props, vegetation support and world dressing. Existing warehouse bytes are reused first.
- `Data/P1C01MegaChapterPackV1.json` remains source/preparation only. Its material export, promotion and character-intake cars do not mutate P1C01 runtime while PR #247 owns the current runtime-changing skeletal lane.
- Animated production candidates remain FBX-only. Production textures remain PNG/TGA, 1K/2K by default. Repeated world detail remains ISM/HISM + LOD/culling. Heavy runtime residency remains soft/async under the existing streaming subsystem.
- Player-visible intent: replace the strongest current proxy/material read blockers first so the next authorized runtime integration can materially improve what the owner sees in Bag End/Hobbiton rather than only expanding backend systems.
- Evidence boundary: **REGISTERED / SOURCE EXECUTION NOT YET RUN**. No PIE-TESTED, DEVICE-TESTED, VISUALLY-ACCEPTED or PERFORMANCE-ACCEPTED claim.

## 2026-10-02 - P1C01 visible-world reuse-first correction

- Before acquiring more ferry/road assets, exact Unreal import evidence was checked against the visible proxy list.
- Existing imported production stock already includes `SM_CommonRiverBoat`, `SM_CommonRopePost`, `SM_CommonRopeCoil`, `SM_CommonFootbridge`, `SM_CommonReedCluster`, `SM_CommonFallenLog`, `SM_CommonBroadleafTree` and `SM_CommonBoulderCluster`.
- Therefore Bucklebury/Ferry and the wooded-road corridor are now **reuse-first**, not automatically classified as new-source gaps. The next serialized runtime visual pass must try these resident production roles before requesting another provider asset.
- This remains source/routing work only while PR #247 owns the runtime-changing lane.
- Evidence boundary: **STATIC-VALIDATED ROUTING / NO VISUAL ACCEPTANCE**.

## 2026-10-02 - P1C01 visible-world resident binding packet

- Registered exact resident-production bindings for the two strongest reuse-first cells: **Bucklebury/Ferry** and the **Shire road corridor**.
- Ferry source bindings now point to the existing Common river boat, footbridge, rope post, rope coil, reed cluster and boulder cluster assets instead of defaulting to another acquisition pass.
- Road-corridor bindings now point to the existing Common fallen log, broadleaf tree, boulder cluster, village fence, wood pile and fern cluster assets.
- Runtime integration remains serialized elsewhere; this packet does not remove a primitive or change story/world authority by itself.
- Repeated detail remains ISM/HISM + LOD/culling; heavy runtime residency remains soft/async through the existing streaming architecture.
- Evidence boundary: **SOURCE/STATIC BINDING PREPARATION ONLY**. No PIE/device/visual/performance acceptance claim.

## 2026-10-02 - P1C01 Party Field primitive-overlay suppression

- Registered a bounded visible-runtime cleanup for the existing F1-01 Party Field only.
- Deep source inspection found that `SpawnVillage()` still always spawns a large cube centerpiece at the Party Field even though the later Hobbiton architecture pass already places the resident production `SM_ShPicnicCanopy` at the same story destination.
- This pass removes only that duplicate greybox visual when the production canopy is resident; the cube remains a deterministic fallback when the production mesh is absent.
- Story location, quest triggers, party-state ownership, NPC population, collision authority and chapter postconditions remain unchanged.
- No new heavy asset load is introduced; the existing resident production pointer is reused.
- Evidence boundary: **REGISTERED / RUNTIME CHANGE NOT YET IMPLEMENTED**. No PIE/device/visual/performance acceptance claim.

## 2026-10-02 - P1C01 East Fields crop-row proxy replacement registration

- Registered the next visible-world cleanup after the serialized Party Field pass: replace the twelve long non-collision cube crop-row strips in the East Fields.
- Proposed implementation is one bounded instanced production-vegetation treatment using the existing resident production grass-clump mesh unless a more crop-appropriate already-imported production mesh is identified before runtime work.
- Budget before implementation: <=1 zero-Tick/no-collision detail cluster, <=96 instances, start/end cull about 900/6500 cm.
- Current cube strips remain deterministic fallback if the resident production mesh is unavailable.
- Story geography, traversal, quest/NPC authority and P1C02 runtime remain unchanged.
- Evidence boundary: **REGISTERED / SOURCE PREPARATION ONLY**. No PIE/device/visual/performance acceptance claim.

## 2026-10-02 - P1C01 East Fields HISM crop-row implementation

- The previously registered East Fields cleanup is now implemented in source on its stacked runtime lane.
- Twelve long non-collision cube strips are replaced when `SM_ShGrassClump` is resident by one dedicated builder-owned HISM component with 96 deterministic instances total.
- HISM budget: no Tick, no collision/overlap, no shadow, cull start 900 cm, cull end 6500 cm. Cube strips remain deterministic fallback-only.
- No new world authority, story state, NPC state, synchronous heavy load or P1C02 activation is introduced.
- Evidence boundary: **SOURCE IMPLEMENTATION ONLY** until fresh exact-head Pre-Unreal + UE4.27.2 validation completes; no PIE/device/visual/performance acceptance.

## 2026-10-02 - Alternate Frodo source-family escalation registration

- Registered a new bounded CC0 rig-base source family for Frodo candidate QC: KayKit Adventurers at immutable revision `672074b73ba276876a19e8816ecdc5241817ab47`.
- This does not alter canon, chapter state, gameplay authority or final Frodo likeness requirements. It is only a technical rig-base source escalation after prior candidate families failed their technical gates.
- Animated production candidates remain FBX-only; final likeness/deformation/retarget/runtime acceptance remain separately gated.
- Status: **SOURCE REGISTERED / RUNTIME NOT AUTHORIZED**.


## 2026-10-03 - P1C01 KayKit Knight technical source probe

- Registered the already-discovered `Knight.fbx` row from the same immutable KayKit Adventurers family as a second bounded technical rig-base probe after Rogue's real UE4 technical rejection.
- This is not a world-detail addition and introduces no runtime actor, NPC authority, story state, save state or visual placement.
- If Knight reproduces Rogue's missing-smoothing-groups and missing-bind-pose-bones debt under the same real UE4.27.2 gate, treat the KayKit export family as a technical closure candidate before spending runs on Mage/Barbarian.
- Evidence boundary: **SOURCE REGISTRATION ONLY** until staging/static/UE evidence exists.


## 2026-10-03 - Bag End entry shrub refresh

- No new lore/location concept is introduced; this refresh only replaces the already-registered planted-entry primitive visual with resident production stock.
- Existing planted-entry transforms remain unchanged. `SM_ShShrub` is used when resident; primitive spheres remain deterministic no-asset fallback.
- Hero architectural door/window/trim and interior-shell debt remain separately gated; no fallback is removed without exact replacement import/QC evidence.
- Evidence boundary: **SOURCE IMPLEMENTATION ONLY** pending fresh exact-head workflows.

## 2026-10-03 - Bag End hero trim source probe V3

- Continues the existing Bag End Hero Ring source requirement only; no new world/detail concept is introduced.
- Current architectural primitive fallbacks remain untouched until an exact replacement passes provenance, static QC and real UE4 import.
- No story, quest, NPC, save, traversal, streaming or runtime placement authority changes.

## 2026-10-03 - Bag End hero trim exact-file candidates

- Existing Bag End Hero Ring requirement is refined to exact modular FBX candidates; no new lore/detail concept is added.
- Candidate geometry is limited to round door/doorway/window support consistent with the already-recorded circular domestic geometry requirement.
- Current primitive architectural fallbacks remain untouched until official receipt, static QC and real UE4 import succeed.


## 2026-10-03 - Bag End hero trim official source resolution

- Existing Bag End round-door/window/trim debt remains unchanged; this wave records source evidence only.
- Kenney Building Kit official download URL is resolved and pinned for the next warehouse receipt step.
- Architectural primitive fallbacks remain mandatory until archive receipt, extracted-file identity match, static FBX QC and real UE4.27.2 import evidence exist.
- Evidence boundary: **SOURCE PREPRODUCTION ONLY**.


## 2026-10-03 - Reconciled source/preproduction packets from stale open PRs

- Recovered the P1C01 Shire production pack and 180-slot visual production wave onto fresh current develop ancestry without activating any new runtime chapter.
- Recovered the 23-chapter source-backed production packet/demand matrix with every row still runtime_integration_allowed=false.
- This reconciliation records source/detail planning only; it does not add runtime actors, alter story/quest/NPC authority, or remove any visual fallback.
- Evidence boundary: **SOURCE PREPRODUCTION ONLY / EXACT-HEAD VALIDATION PENDING**.


## 2026-10-03 - Bag End/Hobbiton garden production pass

- World-bible basis remains the Shire/Hobbiton domestic visual grammar: pastoral hills/lanes/farms/Hobbit-holes with warm domestic scale, circular doors and gardens.
- The five existing garden locations are preserved; this wave changes representation only, replacing cube/sphere production-path treatment with resident ground + shrub production assets.
- Repeated garden plants remain bounded under the existing HISM/cull architecture; no new world authority or procedural system is introduced.
- Primitive fallbacks remain until exact production assets resolve at runtime.
- Evidence boundary: **SOURCE-IMPLEMENTED / EXACT-HEAD VALIDATION PENDING**.


## 2026-10-03 - P1C01 VISIBLE_SHIRE_MEGA_PASS registered before runtime implementation

- Scope: one large visible-world runtime pass for the existing P1C01 Shire route only; no new chapter, story outcome, quest ownership, save ownership or character authority.
- Player-facing target: make the route read as a coherent lived-in landscape from Bag End through Hobbiton, worked fields, enclosed wooded road and the Ferry approach instead of scattered props/proxies.
- Runtime ownership stays with `AShirePrototypeWorldBuilder` as the single P1C01 world writer. `ALivingWorldDirector` continues to own ambient population/pooling and `UShireNPCContextSubsystem` continues to own bounded NPC context; this pass does not spawn or schedule NPCs.
- Architecture: add bounded HISM lanes for repeated production hedge, broadleaf tree, rural fence, fern and reed meshes; no per-instance ticking, no crowd Spawn/Destroy churn, no synchronous heavy asset load, no new hard asset references.
- Residency rule: the pass may bind only already-resident production meshes supplied by the existing chapter streaming/import path; missing optional meshes skip detail rather than falling back to new runtime loads.
- Collision rule: decorative woodland/fern/reed instances remain non-colliding; route-shaping hedges/fences remain bounded and may use collision only where needed without changing story/traversal anchors.
- Composition rule: preserve the existing Bag End/Hobbiton/Fields/WoodedRoad/Ferry anchors and reveal sequence; increase foreground/midground layering, hedge enclosure, orchard/woodland depth and river-edge vegetation without moving quest triggers.
- Performance target: 720p / 30 FPS floor on i7 Gen6 / 8 GB RAM / ~2 GB VRAM; recover cost through HISM, explicit cull bands and shadow suppression rather than reducing the hero world to low-quality primitives.
- Gate: exact-head Pre-Unreal + UE4.27.2 build required before merge. PIE/device/rendered visual acceptance remains separate and is not claimed by machine validation.


## 2026-10-03 - P1C01 Frodo OGA Lowpoly Dummy technical probe disposition

- Exact UE4.27 probe completed for the registered CC0 Lowpoly Dummy Idle FBX payload SHA256 `00177d777d324e2eb807f5f94b573026c94226c6574267900213863a0dc8014d`.
- UE4 skeletal registration succeeded with 41 bones; the candidate is nevertheless rejected because the import emitted missing smoothing-group information and missing bind-pose bones.
- This is a technical source rejection only. It does not alter story/world/NPC ownership and does not authorize runtime character integration.
- The rejected hash is durable project memory and may not be retried. Next candidate must be a distinct licensed payload/corrected export and must pass the same or stricter technical gate.


## 2026-10-03 - P1C01 NATURAL_ROUTE_MEGA_PASS registered before runtime implementation

- Scope: second large visible-world pass for the existing P1C01 route only. No chapter expansion, no story outcome changes and no quest/save/NPC authority changes.
- Player-facing target: break the remaining straight/blocky road-edge read between Bag End, Hobbiton, the worked fields, wooded road and Ferry with irregular path-edge stones, grass verges, shrub pockets and flower/meadow breakup using already-resident production meshes.
- Runtime writer remains `AShirePrototypeWorldBuilder`. `ALivingWorldDirector` continues to own pooled ambient population; `UShireNPCContextSubsystem` continues to own NPC context. This pass creates no NPCs and performs no global actor scan.
- Instancing rule: extend the existing HISM lanes (`PathStoneInstances`, `GrassInstances`, `ShrubInstances`, `FlowerInstances`) after their normal rebuild instead of creating per-prop actors.
- Residency rule: use only meshes already resolved by the existing chapter streaming/import path. No synchronous heavy asset load and no new hard content reference.
- Traversal rule: all new route breakup instances are decorative/non-colliding and stay outside the authored centerline and quest trigger corridor.
- Performance rule: deterministic bounded instance counts, existing HISM cull bands and no per-instance Tick. Target remains 720p / 30 FPS floor on i7 Gen6 / 8 GB RAM / ~2 GB VRAM.
- Gate: exact-head Pre-Unreal + UE4.27.2 build required before merge. Rendered/PIE/device/FPS acceptance remains a separate human/device gate and is not claimed by source implementation.
## 2026-10-04 - P1C01 AUTHORED_SHIRE_MEGA_WAVE_B registered before runtime implementation

- Scope: existing P1C01 only. This wave strengthens visible terrain/landmark/material-presentation composition without opening P1C02 runtime or changing story outcomes.
- Source basis: supplied Story/Timeline anchors F1-02 at Bag End/Shire and F1-03 at Shire roads/Bucklebury; Tolkien source describes wooded shelter opening into grasslands and well-tended fields/meadows with hedges, gates and drainage dikes, then a well-kept Ferry lane, broad wooden landing stage, reeds/mist at the bank, a broad slow river and a steep winding path on the far side.
- Runtime authority: AShirePrototypeWorldBuilder remains the sole P1C01 world-construction writer. ALivingWorldDirector remains population/pooling authority; UShireNPCContextSubsystem remains bounded context; UShireQuestSubsystem remains story truth.
- Implementation intent: add authored HISM terrain masses/terraces and sightline occlusion around Bag End/Hobbiton, preserve broad worked-field openness, intensify wooded-road enclosure, strengthen Ferry bank/far-bank silhouette and approach readability, and tune the existing low-cost atmosphere without introducing a second world system.
- Performance boundary: existing resident production meshes only for runtime geometry; HISM/ISM for repeated landform/vegetation; explicit culling; no per-instance Tick; no synchronous heavy load; no actor-per-prop density expansion; no new NPC ownership.
- Material boundary: imported production materials remain authoritative. Engine primitive color materials remain fallback-only. New external textures/assets, if later required, must pass provenance/license, PNG/TGA/channel-packing, material-slot, LOD and VRAM review before admission.
- Evidence boundary: REGISTERED / SOURCE-GROUNDED PLAN. No PIE, device, visual, pacing or FPS acceptance is claimed.

## 2026-10-04 - P1C01 PRESENTATION_COMPOSITION_WAVE_C registered before implementation

- Scope: P1C01 visual presentation only; follows the authored landform packet on the same branch. No chapter expansion, new story owner or NPC lifecycle change.
- Source/production basis: Bag End garden should read bright and cultivated; Shire travel should alternate open pastoral views with deeper wooded enclosure and mist/stream depth. The production resource bible prioritizes restrained runtime texture resolution, packed masks where appropriate, reduced material slots/draw calls, and low-LOD/atlas vegetation for the ~2 GB VRAM target.
- Implementation intent: strengthen foreground/midground vegetation composition with existing HISM components and resident meshes, improve wooded-road canopy/understory layering and Ferry-bank framing, and make the existing morning atmosphere less prototype-heavy through bounded light/fog/post-process tuning.
- Material rule: preserve imported production materials; do not override them with generic color MIDs. External PBR intake is not required for this source pass; if a material gap remains after PIE review, prefer recorded CC0 sources such as Poly Haven/ambientCG and package PNG/TGA/channel-packed textures under the existing material budget.
- Performance boundary: HISM only for repeated new vegetation, existing cull distances, no per-instance Tick/collision, no volumetric fog, no planar reflection/scene capture, no new synchronous heavy asset load.
- Evidence boundary: REGISTERED / SOURCE-GROUNDED PLAN. Visual acceptance requires later PIE/device evidence.

## 2026-10-04 - P1C01 KAYKIT_RIG_TECHNICAL_BRIDGE registered before implementation

- Scope: existing P1C01 character-pipeline blocker only. This does not replace Frodo likeness art, does not open P1C02, and does not alter story/NPC ownership.
- Trigger: Quaternius RPG normalized family exhausted exact UE4.27 technical gates; Quaternius Universal Base Characters remains source-suitable but its free distribution is currently behind an interactive itch.io download flow rather than a stable direct archive accepted by the automated warehouse policy.
- Technical bridge source: KayKit official public GitHub repository `KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0`, CC0, direct public archive, FBX/PNG content, fully rigged/animated characters and 75 animations. Existing project manifest already authorizes this pack as rigged-character pipeline support.
- Intended use: prove a clean UE4.27 skeletal import + bind pose + UV + real skeleton + animation/deformation bridge on one bounded candidate. It is not final Frodo likeness and cannot be promoted as named-character final art.
- Candidate policy: prefer one smallest/most neutral suitable FBX candidate first; exact archive/payload SHA256 recorded; hard reject on invalid bind pose, missing bind-pose bones, missing UVs, smoothing failure or missing skeletal registration.
- Performance boundary: low-poly/mobile-oriented source; PNG textures only; no runtime hard reference; any later integration remains soft/async via FStreamableManager; modular Frodo remains fallback.
- Ownership boundary: ALivingWorldDirector remains population/pooling authority; UShireNPCContextSubsystem remains context; UShireQuestSubsystem remains story truth.
- Evidence boundary: REGISTERED / SOURCE-GROUNDED PLAN ONLY. No UE4 import, deformation, runtime, PIE, device, rendered visual or FPS acceptance is claimed yet.

## 2026-10-04 - P1C01 VISIBLE_SHIRE_MEGA_WAVE_D registered before implementation

- Scope: existing P1C01 only. This wave is a visible-world completion push, not a new chapter or duplicate world authority.
- Canon/source anchors: F1-02 Bag End/Shire and F1-03 Shire roads/Bucklebury remain the playable visual spine. The source route explicitly supports a transition from steep green banks and tangled woodland into flatter open country with ditches/fences, then a well-kept Ferry lane, broad landing stage, reeds/mist, broad slow river, steep opposite bank and a winding uphill path. 
- Runtime authority remains AShirePrototypeWorldBuilder. ALivingWorldDirector remains ambient population/pooling authority; UShireNPCContextSubsystem remains bounded NPC context; UShireQuestSubsystem remains story truth.
- Visible objectives: (1) stronger Bag End hero silhouette and garden/entry framing, (2) Hobbiton settlement depth and terrace identity, (3) authored road/field edge rhythm, (4) woodland threshold/canopy/understory enclosure, (5) Ferry destination readability and opposite-bank silhouette, (6) cleanup of obvious prototype repetition from player-facing sightlines.
- Performance contract: repeated detail through existing HISM/ISM components only; explicit culling; no per-instance Tick; no actor-per-prop density wave; no synchronous heavy loading; no new hard runtime references.
- Asset rule: reuse resident production meshes/materials first. Any missing external visual material must pass provenance/license and PNG/TGA/channel-packed/LOD/VRAM review before admission.
- Validation boundary: SOURCE-GROUNDED PLAN ONLY. No PIE/device/rendered-visual/FPS acceptance is claimed until direct evidence exists.


## 2026-10-04 - P1C01 SHIRE_VISUAL_FINISH_WAVE registered before implementation

- Scope: existing P1C01 only; visible-world finish packet; no P1C02 and no second world authority.
- Source anchors: F1-02 Bag End/Shire + F1-03 Shire roads/Bucklebury. The route supports rolling/green land, tangled woodland, ordered open fields with fences/ditches, then the well-kept Ferry approach, reeds, broad river and a steeper opposite bank with an uphill path silhouette.
- Runtime authority remains AShirePrototypeWorldBuilder. ALivingWorldDirector remains ambient population/pooling authority; UShireNPCContextSubsystem remains bounded NPC context; UShireQuestSubsystem remains story truth.
- Visible objectives: terrain silhouette rhythm; stronger Bag End camera framing; Hobbiton property separation; low-cost road/verge breakup; foreground/midground woodland layering; final Ferry bank/path framing; anti-prototype cleanup.
- Performance contract: maximum new budget **212 HISM instances + 4 limited hero actors**; resident meshes only; existing culling; no per-instance Tick; no actor-per-prop density; no synchronous heavy loading; traversal corridor remains open.
- VRAM rule: no new texture set/material permutation in this packet. Surface variation is geometric/verge breakup only pending a separately budgeted PNG/TGA/channel-packed material pass for the ~2 GB VRAM target.
- Evidence boundary: REGISTERED / SOURCE-GROUNDED PLAN before implementation. No PIE/device/rendered-visual/FPS acceptance.


## 2026-10-04 - P1C01 HUMAN_CHARACTER_PRODUCTION_WAVE_2 registered before implementation

- Scope: P1C01 Frodo visible-character production only. No P1C02 runtime opening and no duplicate NPC/quest/world authority.
- Trigger: Quaternius RPG and KayKit exact payload families produced real UE4.27 skeletal registration but failed unchanged smoothing/bind-pose/UV technical gates. Their exact rejected payload hashes remain forbidden for retry.
- New source-family strategy: use a genuinely different CC0 human source/export family rather than another payload from the same rejected exporter lineage. First automated family is OpenGameArt Character Base Model by Overaction Game Studio, advertised as a rigged low-poly fantasy character base under CC0 with a direct downloadable source archive.
- Repair policy: hosted intake may accept FBX directly or a source .blend only as an intermediate authoring file. Final animated candidate delivered to UE4 must be FBX. If direct FBX is absent or technically unsuitable for static structure, Blender normalization/re-export is authorized to produce a new exact FBX payload identity; hard UE4 smoothing/bind-pose/UV/skeletal-registration gates remain unchanged.
- Source provenance requirements: source page, creator, CC0 marker, direct archive URL, archive SHA256, source entry identity, normalized payload SHA256, conversion tool/version and all technical rejection reasons are durable evidence.
- Candidate budget: max two distinct normalized FBX payloads per source family before moving on. Do not brute-force a large archive on the self-hosted UE4 runner.
- Next-on-pass: reference pose + root/scale/hierarchy + shoulder/elbow/knee + hand/foot deformation readiness artifact, then Idle/Walk/Run locomotion/retarget preparation and AnimBP; runtime promotion remains blocked until those pass.
- Runtime contract: modular Frodo remains fallback. Heavy character assets must remain soft references and load asynchronously through FStreamableManager. No synchronous heavy LoadObject path is authorized.
- Target: UE4.27.2 / DX11 / 720p / 30 FPS floor / i7 Gen6 / 8 GB RAM / ~2 GB VRAM.
- Evidence boundary: REGISTERED / SOURCE-GROUNDED PLAN ONLY. No technical pass, deformation acceptance, runtime, PIE, device, rendered-visual or FPS acceptance is claimed.


## 2026-10-04 - P1C01 SHIRE_SETTLEMENT_COMPLETION registered before implementation

- Scope: finish the authored P1C01 Shire settlement layer before any P1C02 runtime expansion. Runtime writer remains `AShirePrototypeWorldBuilder`.
- Source basis: F1-01/F1-02 plus supplied Tolkien material supports Hobbiton around the Hill/Bag End, Bagshot Row adjoining the Party Field, gardens and hedges, domestic lanes, the Water, mill/bridge, nearby Bywater-facing settlement activity, fields and orchards.
- This packet does **not** claim survey-accurate geography where the supplied production sources do not provide coordinates; it converts the supported relationships into a readable authored game composition.
- Visible completion targets: Bagshot Row visual smials; stronger property boundaries; domestic garden/laundry/mail detail; orchard rhythm; Party Field seating; village common/market; mill-wheel read; wells; carts/crates/barrels/benches; field work detail; wayfinding; lived-in transition toward Bywater.
- Performance budget: 160 placements on existing native HISM components + 185 instances inside at most 24 `AWorldDetailCluster` actors = target 345 new visual instances. Detail clusters are non-colliding and zero-Tick; existing traversal collision remains authoritative.
- Asset rule: resident production Shire/Common meshes only. No runtime `LoadObject`, no BMP, no new hard heavy references, no per-prop actor density.
- Architecture: `ALivingWorldDirector` remains population/pooling authority; `UShireNPCContextSubsystem` context authority; `UShireQuestSubsystem` story truth. No duplicate manager.
- Evidence boundary: REGISTERED / SOURCE-GROUNDED PLAN. No PIE/device/rendered visual/FPS acceptance claimed.


## 2026-10-04 - P1C01 SHIRE_SETTLEMENT_CANON_FINISH_B registered before implementation

- Predecessor settlement packet #314 is machine-green and merged: exact head `3ee80ffeaa03ee0acce131d098eb3f7967f36480`, Pre-Unreal #1849 SUCCESS, Unreal Build #1446 SUCCESS, merge `b3f31134e97d58362f486e09796eaf34852fe328`.
- Purpose: close remaining source-grounded Hobbiton settlement details without opening P1C02 or changing locked F1-01/F1-02 outcomes.
- Source-safe details: Ivy Bush roadside inn identity; Number 3 Bagshot Row visual anchor; Party Field special entrance/steps and open-air kitchen; mill-yard stores; tree-lined Bywater-road transition.
- Green Dragon is explicitly not placed in Hobbiton; it remains a Bywater landmark. Existing legacy save/discovery IDs are preserved for compatibility.
- Performance budget: 10 HISM placements + 45 WorldDetailCluster instances + 1 persistent landmark actor + 8 story-state party actors = 64 new visual instances. Clusters are no-collision/zero-Tick and use resident production meshes only.
- Existing quest/NPC anchors are not moved. Party props reuse the setup/celebration state arrays.
- Evidence boundary: REGISTERED / SOURCE-GROUNDED PLAN. No PIE/device/rendered-visual/FPS acceptance.


### 2026-10-04 - PR #315 selective salvage disposition

- Closed unmerged head `be04e90053d997eee6085d8adc9b07d3e87baaf0` was reviewed before disposal.
- Retained only unique source-grounded reads: Party Field boundary shell, Water/mill edge reeds + stepping stones, and three Bywater-facing cottages.
- Rejected duplicate density from that branch where #314/B already owns the same visual role.
- This is a bounded salvage into the active Canon Finish B authority, not a second settlement system.


### 2026-10-04 - Shire settlement source-construction closure

- PR #314 and PR #318 are exact-head machine-green and merged; the authored P1C01 Hobbiton/Shire settlement checklist is source-complete.
- No further settlement density wave is authorized before the existing local visual bootstrap and human rendered review, because the Governor requires observation of the generated production Content rather than blind source-density escalation.
- Remaining world work is acceptance/polish: generate local `Content/Production`, launch `/Engine/Maps/Entry`, inspect composition/material/lighting/traversal, then correct only observed defects and measure the 720p/DX11 target.
- This closure does not promote Gate 6/7, PIE/device/visual/pacing/performance acceptance, or P1C02 runtime.


## 2026-10-04 - P1C01 DEFINITIVE_CHAPTER_CLOSEOUT_V1 registered before implementation

- Owner direction: stop branch-per-packet churn, clean completed/dead refs, and accelerate P1C01 on one active closeout branch until the Shire-through-Bucklebury/Ferry chapter is actually closed.
- Baseline: `develop@fd08c1c719f4b754384f03a10751dd748eacc74f`.
- Render evidence reviewed from PR #322 run `37207780989`, artifact `11306540563`: six successful bounded screenshots exist for Bag End/Hill, Hobbiton Common, Party Field, Water/Mill/Bridge, Bywater-facing edge, and Bucklebury Ferry.
- Human visual disposition for that artifact: **REJECTED / POLISH REQUIRED**. The player is still a blocky proxy; broad terrain/foliage/settlement surfaces read flat/grey; landmark framing and lighting/depth are below the intended production target; Ferry remains under-authored.
- This is now an evidence-driven closeout wave, not a blind density wave. First repair causal pipeline/ownership defects, then re-render and only add geometry where the new images prove a real gap.
- Known root-cause lanes to repair in this wave: render-capture final count parser; Human Wave 3 artifact handoff/deformation false-green; Party Field single-owner/traversable entrance; authored property-fence lifecycle ownership.
- Architecture remains unchanged: `AShirePrototypeWorldBuilder` world writer, `ALivingWorldDirector` population/pooling, `UShireNPCContextSubsystem` context, `UShireQuestSubsystem` story truth; repeated detail HISM/AWorldDetailCluster; no synchronous heavy loading; no P1C02.
- Branch policy: `production/p1c01-definitive-chapter-closeout-2026-10-04` is the single active P1C01 closeout branch. Continue by sequential commits on this branch rather than opening a branch per sub-packet.
- Evidence boundary: REGISTERED + RENDERED DEFECT EVIDENCE. No PIE/device/performance/Gate 6/7 acceptance.


## 2026-10-04 - P1C01 SHIRE_LOCAL_MATERIAL_AND_GROUND_TILING_ROOT_FIX registered before implementation

- Trigger evidence: rendered artifact run `37207780989` shows a systemic flat/dark/grey read across the ground, distant terrain and repeated woodland despite a successful production import.
- Import evidence rules out a missing-import blanket failure: `376 files, 0 failures`, `161/161` requested albedo bindings bound, and `229` tracked material packages with zero missing persistence files.
- Source audit isolates two causal presentation problems:
  - repeated Shire geography/woodland currently uses shared Common meshes whose source materials are flat-color and have no authored UVs: Common Terraced Hill = `Turf`, Village Slope = `Turf`, River Bank = `RiverMud`, Broadleaf Tree = `Bark/Foliage`;
  - the visible Shire ground uses one `SM_ShGroundBlock` scaled to approximately 34,000 x 13,000 cm while its top UV spans only 0..1, stretching one grass texture over most of the chapter floor.
- Root-fix plan is Shire-local; do **not** mutate `CommonLandscapeMaterials.mtl` globally because Common assets are shared by other chapters.
- Repeated Common components in P1C01 will receive component-level overrides from already-resident Shire textured material instances (`Grass/Earth/Bark/Leaves/Wood`) via `ResolveResidentMaterial`; no synchronous runtime load is introduced.
- The one giant visible production ground actor will be replaced by one non-colliding HISM owner with a bounded 34 x 13 grid = 442 `SM_ShGroundBlock` instances. The hidden deterministic collision foundation remains the collision authority. This increases texture repetition/readability without actor-per-tile cost or extra texture memory.
- Garden soil remains a dedicated HISM and will explicitly use the Shire Earth material instead of inheriting the ground block's Grass material.
- Performance boundary: one additional HISM component, 442 trivial 12-triangle tiles, existing resident meshes/textures only, no per-instance Tick, no new movable lights, no new world authority.
- Evidence boundary: SOURCE-GROUNDED ROOT-FIX PLAN. It is not visual acceptance; a fresh exact-head render must prove whether the grey/flat defect is materially improved.

## 2026-10-06 - P1C01 OFFLINE SATURATION / MICRO DETAIL COMPLETENESS

- Source-preparation only while UE4-27-Windows is unavailable. No blind density wave and no new runtime chapter.
- `Data/P1C01WorldMicroDetailCompletionV1.json` tracks Bag End exterior/interior, Hobbiton/Bagshot Row, Party Field, Water/Mill/Bridge, fields/orchards, wooded hiding corridor and Bucklebury Ferry down to player-facing details such as door hardware, furniture, books/pantry/hearth, flowers/gardens, carts/tools, ferry rope/boarding detail and localized audio roles.
- Existing resident Shire sources remain first choice; missing hero/detail items become provenance/QC gaps rather than primitive spam.
- Repeated detail remains HISM/ISM/`AWorldDetailCluster`; no synchronous heavy loading or per-instance Tick.
- Evidence boundary: SOURCE-PREPARED MATRIX ONLY. Placement/collision/render/PIE/device/FPS acceptance remains pending.

## 2026-10-06 - P1C01 HERO SOURCE GAP + FERRY TERMINAL LOCK packet

- Scope remains P1C01 only. This packet does not open Bree and does not add a second world/story authority.
- World hero-source gaps are now explicitly routed before implementation: Bag End interior hero clutter/hardware; natural wooded-road tree/understory silhouettes; Ferry deck/landing/rope/boarding construction; riverbank/reeds/water-edge transition; and bounded lighting/sky/water presentation.
- Resident Shire/Common sources remain first choice. Poly Haven Tree Small 02 and Quaternius Ultimate Nature are source candidates only; the Poly Haven tree's very high source triangle count means it must be reduced into project-owned LOD/cull derivatives before any repeated runtime use.
- Repeated vegetation/riverbank/detail remains HISM/ISM/`AWorldDetailCluster`; no actor-per-tree wave, no synchronous heavy load, no BMP texture source, and no density added merely to fill space.
- The same audit exposed a chapter-topology defect: Ferry far-side completion and terminal-state restore could auto-open P1C02. The registered repair makes `FerryEscape stage 2` a valid P1C01 terminal state, records `FerryEscapeComplete`, and queues `WC_P1C01_FERRY_END` without starting Bree.
- This is not a new canon outcome: it enforces the existing production ownership boundary (P1C01 through FerryEscape; P1C02 owns Bree arrival/opening) and keeps the source-locked wider F1-03 postcondition separate.
- Evidence boundary: **SOURCE-IMPLEMENTED / SOURCE-CANDIDATE-ROUTED** only. UE4 compile, PIE, visual, device, audio playback, disk save/load and FPS evidence remain pending.

## 2026-10-06 - WHOLE_GAME_OFFLINE_SATURATION registered and source-demand corrected

- Temporary source/preproduction exception only while the UE4 runner is unavailable. Runtime writer ownership and chapter serialization do not change; P1C01 remains the sole runtime-changing chapter and Bree/P1C02 remains locked.
- Whole-game preparation now spans the canonical F1-01..F3-07 mission set at source/data/provenance/QC level. Source 11 supersedes older Sources 01-07 ROTK screenplay-absence notes; future ROTK production verification must use the supplied ROTK screenplay and film before old MASTER-SUMMARY shorthand.
- Chapter-demand reconciliation removes concrete future-lane contamination from Amon Hen, Pelennor, Return/Farewell and several Ent-unrelated chapters before warehouse growth continues.
- Warehouse expansion is selective rather than indiscriminate: reusable humanoid bases/outfits/animation, horse/fauna, support nature/architecture, static medieval props and audio depth are prioritized because they unlock many future regions.
- Candidate sources are registered with access/license/role boundaries. They are not promoted to STAGED/READY_FOR_IMPORT until actual payload receipts, SHA256 and technical QC exist.
- Static system simulation result: `ALivingWorldDirector` remains population/pooling authority and consumes committed context without transferring spawn ownership to `UShireNPCContextSubsystem`; the context subsystem stores committed chapter/route/episode/quest state and resolves schedules/dialogue from loaded data rather than rebuilding context from world actors each frame.
- Transition-time scans/pool resets and synchronous user QuickSave/QuickLoad remain measurement risks, not proven defects. Cold/warm streaming, collision, render hitching, p95/p99 frame tails, VRAM, audio playback and human visual quality remain runner/device evidence.
- Repeated world detail remains HISM/ISM/`AWorldDetailCluster`; heavy assets remain soft/async; crowds remain pooled; PNG/TGA texture rule and FBX-only final animated delivery remain unchanged.
- Evidence boundary: **SOURCE-IMPLEMENTED / STATIC-RISK-AUDITED** only. No PIE/device/visual/performance acceptance.

## 2026-10-06 - Ferry terminal ownership clarified before runner return

- P1C01 ends on the far side of the Brandywine with `FerryEscapeComplete`; this is a chapter-terminal presentation/checkpoint beat, not permission to instantiate Bree.
- `FerryEscapeComplete` reuses the existing ferry camera/ambience/music/SFX family for a short confirmation and returns player control.
- No world trigger, StoryFlow repair, persistence repair or validator is allowed to auto-open `P1C02 / RoadToBree`.
- A restored terminal save at `P1C01 / FrodoMain / P1C01_Main / FerryEscape stage 2` must remain in that committed Shire identity.
- This change preserves the One-Shot chapter policy and prevents runtime/save tooling from bypassing the Gate 6/7 predecessor lock.
- Evidence boundary: source/runtime contract correction only; hosted validation and UE4 evidence remain pending.

## 2026-10-06 - Final pre-runner structural hygiene sweep

- No new world density was added during this sweep. The pass is structural: source format, ownership, loading, pooling, chapter boundary and repository hygiene.
- Repeated environmental detail remains HISM/ISM/`AWorldDetailCluster`; no actor-per-prop expansion was authorized.
- `ALivingWorldDirector` remains the sole ambient population/pooling authority. Its pool acquisition paths may create an actor only when the relevant pool is empty; normal release returns actors to bounded pools, with destruction only for pool overflow/shutdown.
- `UShireNPCContextSubsystem` remains data/context/schedule authority only and has no actor enumeration or spawn path.
- Heavy production residency stays soft/async. The only direct runtime `LoadObject` forms found by the sweep are Engine BasicShapes fallback assets/materials, not production warehouse assets.
- The Bucklebury far-bank terminal remains inside the committed Shire world; Bree geometry/population/runtime may not be instantiated by that trigger, story-flow repair or save restoration.
- Runtime collision, silhouette/readability, foliage/material presentation, water/rope/ferry traversal and frame-time quality remain runner/human evidence and are not inferred from this static sweep.


## 2026-10-06 - Final static cleanup closeout before P1C01 runtime execution

- Exact source head reviewed: `591cebb1000984cec62141f516d4018d646c939f`.
- Closure source train is no longer pending runner return: P1C01 Chapter Closure Pack #40 succeeded, including its runner-session-health, preflight and Mega Pack V2 steps. This does not establish UE import, PIE, device, visual, audio-playback or performance acceptance.
- Runtime source audit found no synchronous production-heavy loader to root-fix: no `StaticLoadObject`, no `LoadSynchronous`, and direct `LoadObject` findings are limited to Engine BasicShapes fallback meshes/material. Production-heavy residency remains soft/async through the established streaming architecture.
- No animated runtime OBJ or BMP texture path was found. The tracked OBJ stock remains source/static inventory only; final animated production delivery remains FBX.
- `ALivingWorldDirector` remains ambient population/pooling authority. It acquires pooled NPC/interaction/motion actors and only spawns when the corresponding pool is empty; maintenance remains bounded. `UShireNPCContextSubsystem` remains context/schedule/knowledge authority.
- Transition-time actor scans in `AChapterWorldRouter` and named-voice resolution scanning in `UShireAudioSubsystem` are retained as explicit measurement risks; neither was proven to be a per-frame traversal bottleneck by this static audit.
- Ferry far-side ownership remains P1C01 terminal state: `FerryEscapeComplete` -> `WC_P1C01_FERRY_END`; no reviewed live story/world/restore path auto-opens Bree.
- No density, actor-per-prop expansion or authority duplication was introduced in this cleanup.
- The next unresolved chapter work is runtime evidence and real production content integration, not another planning/micro-wave pass.
- Evidence boundary: **STATIC-RISK-AUDITED / SOURCE-CLOSURE-RUN-PROVEN**. P1C02 remains locked until real P1C01 Gate 6/7 plus explicit owner command.


## 2026-10-06 - P1C01 closure workflow anti-churn guard

- A docs/governance-only PR synchronization retriggered Closure Pack #41 even though the source closure payload had already passed on #40. The cause is accumulated PR-diff path matching, not a new world/content requirement.
- The workflow now compares the latest event delta to the six actual closure payload inputs before expensive work. No relevant delta means the source train is inherited and the heavy closure steps are skipped.
- Manual dispatch and unresolvable delta identity remain fail-safe full execution.
- No world, character, density, story, loading or runtime authority was changed by this guard.
- Evidence boundary: **SOURCE-IMPLEMENTED CI HYGIENE**, fresh workflow behavior pending.


## 2026-10-06 - Closure anti-churn guard repair

- Closure #42 never reached a job; the first guard edit malformed the workflow definition itself.
- The closure workflow has been rebuilt from the known-good #40 source before reapplying the latest-event delta classifier.
- This repair changes CI orchestration only. No Shire world, quest, NPC, loading, audio, save or performance behavior changed.
- Evidence boundary: **SOURCE-REPAIRED; fresh workflow proof pending**.


## 2026-10-06 - Continuous P1C01 build lane under hosted CI outage

- The engine lane is no longer allowed to deadlock solely because a GitHub-hosted classifier receives zero executable steps.
- Hosted classification remains first choice. If it fails before producing a valid classification, the available self-hosted UE4 runner performs the exact same classifier after exact-head checkout and runner-health verification.
- Closure delta classification now uses the actual PR head rather than the temporary merge commit and explicitly fetches its comparison base before running `git diff`.
- No Shire world density, story flow, population authority, asset-loading rule, audio rule or Gate 6/7 criterion changed.
- This packet exists only to keep the already-authorized P1C01 One-Shot build moving while preserving fail-closed validation.


## 2026-10-06 - Closure definition clean rebuild

- Closure #44 did not execute a runner job; its failure was workflow-definition syntax caused by duplicated classifier text.
- The workflow has been reconstructed from the exact #40 known-good source rather than patched in place.
- No game/runtime/world data changed in this repair. P1C01 remains active and P1C02 remains locked.


## 2026-10-06 - P1C01 Bag End departure + wooded-road gameplay integration

- Bag End now carries source-backed playable investigation and packing loops during the RingSecret window, using the existing traversal-challenge actor and Journey Discovery pipeline rather than adding a parallel quest system.
- The Hobbiton departure corridor now carries a crouch-gated stealth-departure loop that expires when `LeavingHomeRoad` commits.
- The wooded-road hollow-root corridor now carries a crouch-gated RootHide mastery loop while `KeepOffRoad` remains the mandatory quest authority.
- These actors are bounded, non-ticking traversal challenges; no heavy asset residency or actor-density wave is introduced.
- Optional completion never advances a mandatory quest anchor. Main story triggers remain the only authority for RingSecret/LeavingHome/KeepOffRoad/FerryEscape progression.
- P1C01 remains geographically bounded to the Shire through Bucklebury Ferry. No Bree geometry, population or story runtime is authorized.
- Evidence boundary: **SOURCE-IMPLEMENTED**. Collision readability, crouch behavior, retry/abandon, return-to-control and pacing require fresh UE4/PIE evidence.


## 2026-10-06 - Wooded-road Root Hide gameplay lock

- The Black Rider wooded-road beat now requires the existing crouched `SHIRE_ROOT_HIDE` challenge to publish `Side_RootHideMasteryComplete` before the main `HideUnderRoad` quest trigger may advance.
- This keeps the environmental hiding beat playable rather than decorative and reuses the existing story-beat-trigger re-evaluation path.
- No new Tick, scan, population owner, heavy asset load or chapter transition was introduced.
- P1C01 still ends at FerryEscape; Bree remains locked.


## 2026-10-06 - P1C01 imported Shire material cook residency repair

- Packaged P1C01 startup exposed four missing imported Shire material instances required by the chapter streaming bank.
- These are legitimate soft-bank members, not candidates for synchronous fallback. Their identities live in runtime JSON and therefore require explicit cooker inclusion.
- `/Game/Production/Imported/P1C01Materials` is now a bounded always-cook directory, covering DirtSoil, StonyPath, TreeBark and MossStone without broad warehouse residency.
- No new texture family, density, hard reference or synchronous load is introduced.
- Fresh packaged startup must prove the bank resolves all four before this blocker is considered closed.


## 2026-10-06 - P1C01 final cleanup stabilization ledger entry

- Runtime chapter authority remains **P1C01 only**; P1C02/Bree remains locked.
- Exact audited head `9706cc72367be7e8dd14422808abba63597c8511` completed the self-hosted UE4.27.2 engine chain inside Unreal Build #1654 job `112468931752`: runner health, compile, production import, Automation QA, headless chapter/state/reliability audits, package, packaged Data and packaged startup.
- No new gameplay/world actor authority was introduced. `AShirePrototypeWorldBuilder`, `ALivingWorldDirector`, `UShireNPCContextSubsystem`, `UShireQuestSubsystem`, `UShireAudioSubsystem` and `UShireChapterAssetStreamingSubsystem` ownership remains unchanged.
- Static cleanup root-fix is validator/governance truth repair: Whole Game Offline Saturation now models DEC-105 as a conditional outage exception instead of falsely requiring it to stay active after runner return.
- Character-prep and audio-master manifests no longer describe “runner unavailable” as the blocker. Actual blockers are final production FBX/WAV content and chapter-specific human/device evidence.
- Ferry terminal contract remains `FerryEscape stage 2 -> FerryEscapeComplete -> WC_P1C01_FERRY_END`, with no automatic P1C02 transition.
- No blind density, synchronous heavy production loading, crowd Spawn/Destroy churn, animated final OBJ, BMP texture, or extra AI/story/audio authority was added.
- Evidence state: **parent audited head COMPILE/IMPORT/PACKAGE/HEADLESS-RUNTIME PROVEN; human PIE/device/visual/performance/Gate 6/7 pending**.


## 2026-10-06 - Frodo import gate CI availability hardening

- No character/world runtime authority changed.
- The Frodo technical import lane now has a fail-closed self-hosted fallback when its GitHub-hosted preflight cannot start.
- Fallback repeats the static import contract before exact artifact hashes, UE4.27.2 build/import and the existing 48-bone technical checks.
- Final animated delivery remains FBX-only; no OBJ/BMP/synchronous heavy-load path is introduced.
- Evidence boundary remains technical import only until exact-head rendered/human/device proof exists.


## 2026-10-07 - Closure checkout anti-waste ledger

- Corrected the self-hosted Closure source-train ordering after #49 showed an almost twelve-minute checkout before a no-op delta classification.
- Closure classification now precedes working-tree checkout and runs from a lightweight exact Git graph with LFS smudge disabled.
- No closure-relevant delta means no working-tree checkout at all.
- If closure execution is required, the exact head is checked out with LFS hydration disabled; persistent Warehouse content remains the source-payload authority for the source train.
- No runtime/world authority or chapter boundary changed.


## 2026-10-07 - Frodo technical import evidence + render lane resilience

- Frodo 48-bone technical rig and three tracked animation clips completed the exact-head UE4.27.2 import gate successfully on `f652af9d20e724d5990eaf3d7e4f8382d59e70a5`.
- This is technical import/package evidence only; no visual acceptance was inferred.
- Render Capture now has a fail-closed self-hosted classifier fallback for GitHub-hosted zero-step failures.
- The fallback classifies from a lightweight Git graph with LFS smudge disabled. Heavy exact-head checkout, P1C01 material LFS hydration, editor build and screenshot capture occur only when the classification requires fresh visual evidence.
- No new world actors, density, hard refs, synchronous loads or chapter transitions were added.


## 2026-10-07 - Character scope/metadata cleanup

- Corrected active P1C01 character priority to the exact required Shire cast: Frodo, Bilbo, Gandalf, Sam, Merry, Pippin, Black Rider and Black Rider horse.
- Removed later Fellowship characters from active P1C01 priority while preserving them as future source-preparation-only entries.
- Reconciled historical 161-bone Human Wave 2 metadata to the current 48-bone tracked Frodo technical winner.
- No runtime character acceptance was invented; seven final FBX bundles plus Frodo rendered/human review remain open.


## 2026-10-07 - Render fallback / character intake dependency repair

- Fixed a CI-only parser defect that prevented the self-hosted Shire render classifier from running.
- Added the active P1C01 character-rig preparation manifest as a first-class closure trigger/input because Character Intake directly consumes it.
- No gameplay/world authority, population ownership, asset-loading policy or chapter boundary changed.
- Fresh exact-head runtime/visual evidence is still required before any acceptance promotion.


## 2026-10-07 - Render workflow structural integrity repair

- Rebuilt the P1C01 Shire Render Capture workflow cleanly after duplicate trailing YAML/PowerShell content was detected.
- The resulting workflow retains the intended no-waste classifier-first architecture and one self-hosted capture authority.
- No world geometry, density, character authority, audio authority or chapter transition behavior changed.
- Fresh rendered evidence remains required before any visual acceptance claim.


## 2026-10-07 - Frodo self-hosted runner budget protection

- Added a classifier-first guard to the Frodo UE4 technical import lane so unrelated PR synchronizations do not repeatedly consume self-hosted UE4 time.
- Technical evidence may be inherited only when the explicit Frodo/import impact tree is unchanged.
- No character asset, skeleton, gameplay authority or runtime acceptance state was changed by this infrastructure guard.


## 2026-10-07 - P1C01 visual runtime integration root fix

- The first useful six-shot render artifact was inspected directly. It confirms the authored Shire route exists but remains visually prototype-heavy.
- Runtime logs identified exact causes rather than a generic “art quality” problem: Frodo production packages missing, foliage material compile failure, and HISM material usage debt.
- Production import now makes the tracked Frodo 48-bone rig + Idle/Walk/Run packages part of the normal active workspace instead of transient gate-only evidence.
- The persistent character path still uses runtime soft object paths and `FStreamableManager::RequestAsyncLoad`; no synchronous heavy runtime load was introduced.
- Foliage/surface material master repair is editor/import-time only and preserves HISM/ISM ownership for repeated detail.
- No new density wave, no new population authority, no P1C02 transition, and no Bree runtime opening were introduced.
- Fresh rendered evidence is mandatory before visual acceptance.


## 2026-10-07 - Frodo async render evidence guard

- Corrected the render evidence guard to distinguish runtime identity `Frodo` from content-folder token `FRODO`.
- The P1C01 render now requires proof that the async rig is both loaded and applied before it can report production readiness.
- No runtime authority, asset format, density, chapter transition or synchronous-load policy changed.


## 2026-10-07 - Frodo production input hydration

- Added the exact tracked Frodo FBX bundle to the existing bounded P1C01 pre-import LFS hydration pass.
- Runtime remains soft/async through `UShireChapterAssetStreamingSubsystem`; no synchronous heavy runtime loading or new authority was introduced.
- P1C02 remains locked.


## 2026-10-07 - P1C01 self-hosted runner consolidation

- Consolidated production import and Shire render into the main Unreal build workspace to eliminate duplicate editor build/import work on the single self-hosted runner.
- The capture script can reuse the already-imported workspace but still performs all six viewpoints and the technical presentation blocker scan.
- The standalone render workflow is retained for manual diagnostics only.
- No gameplay/world/audio authority, chapter boundary, density or runtime loading policy changed.


## 2026-10-07 - P1C01 production runner focus

- Automatic work is now concentrated on the unified Unreal build/import/render lane and delta-relevant Closure/Character Intake.
- Historical Frodo source-generation, legacy material-promotion and runner-outage saturation workflows are retained as manual diagnostics only.
- No world writer, population, NPC-context, quest, audio or streaming authority changed; P1C02/Bree remains locked.


## 2026-10-07 - Frodo package persistence hardening

- Added direct disk existence checks for the five production Frodo UE packages after the existing exact-SHA FBX import.
- No runtime authority, world density, synchronous runtime load or P1C02 transition was introduced.


## 2026-10-07 - Definitive One-Shot production-train topology

- P1C01 automatic execution is consolidated into one self-hosted train so runner time is spent on the chapter instead of competing historical lanes.
- Integrated render reuses the production-imported workspace; no second world writer or asset authority is introduced.
- Specialized historical workflows remain available for explicit diagnostics/manual use but do not automatically compete on PR #329.


## 2026-10-07 - Playable artifact / precursor retirement ledger

- The definitive P1C01 train now emits a playable Windows package artifact only after the integrated exact-head production path succeeds.
- The superseded KayKit Frodo precursor no longer auto-runs on the definitive branch, protecting the single UE4 runner for visible Shire production.
- No gameplay/world authority, population ownership, asset streaming law, or P1C02 boundary changed.


## 2026-10-07 - Definitive Unreal train non-cancelling completion rule

- The definitive P1C01 UE train is allowed to finish instead of being cancelled by branch churn.
- This is runner scheduling only; no world density/authority, loading policy, NPC lifecycle or Bree boundary changed.


## 2026-10-07 - One-Shot source-gate harness repair

- Added explicit `Scripts/` Python module resolution to the self-hosted One-Shot static/source gate.
- The repair removes a harness-level blocker that prevented the actual Shire engine build from starting.
- No world density, streaming authority, character ownership, quest flow or P1C02 boundary changed.
- Fresh exact-head engine evidence is required before any runtime/visual acceptance promotion.


## 2026-10-07 - Static contract drift repair

- Reconciled six stale source-contract assertions to current project schemas and explicit P1C01 progress states.
- No runtime/world/content authority changed in this packet.
- The repaired tests continue to enforce async character loading, bounded streaming/cook paths, known-rejection retirement, persistent Frodo production import, and render rejection of prototype/default-material fallback.
- P1C02/Bree remains locked.


## 2026-10-07 - Test placement correction

- Corrected two misplaced status assertions introduced during schema reconciliation.
- No world, quest, character, audio, streaming or chapter authority changed.
- P1C02/Bree remains locked.


## 2026-10-07 - Runner throughput and validator-root repair

- Corrected persistent-runner hygiene validation to distinguish generated local directories from committed generated content.
- Extended discovery-reward declaration coherence to implemented contextual side activities without changing canon/story outcomes.
- Restored safe cancellation of superseded same-PR Unreal runs to free the single UE4 device for the newest exact head.
- Made artifact transport non-blocking; local build/log validation remains authoritative.
- No runtime ownership, density, synchronous heavy-loading policy, or chapter boundary changed.


## 2026-10-07 - Queue-policy test cleanup

- Removed the final obsolete test assertion that required definitive-branch builds to remain non-cancelling.
- The enforced policy now matches the low-waste runner architecture: same-PR superseded work cancels; unrelated branch work remains isolated.
- No Shire world/gameplay/content authority changed.


## 2026-10-07 - Chronicle provenance and runner fail-fast ordering

- Added explicit Chronicle display labels to the four implemented P1C01 contextual side activities and bound validation to those labels.
- Moved runner-session health verification ahead of bounded LFS hydration so an unhealthy self-hosted session fails before heavy file work.
- No runtime authority, population ownership, story outcome or Bree boundary changed.


## 2026-10-07 - Discovery label authority single-owner repair

- Refined Chronicle/discovery validation to avoid duplicate authority while preserving strict label coherence.
- ExplorationEnvelope owns labels for exploration discoveries; ContextualSideActivityPlan owns labels only for contextual side-only discoveries.
- The four P1C01 side-only activity rewards remain explicitly labelled and story-neutral.
- No world density, runtime authority, chapter transition or P1C02 scope changed.


## 2026-10-08 - P1C01 production-importer validation ownership repair

- No new world feature is introduced. This entry closes a validation ownership defect that could let Shire material/presentation importer changes inherit old engine proof without fresh captures.
- `ShireProductionImportCommandlet.cpp` now belongs only to the definitive P1C01 full visual train for automatic validation. Historical Human Wave2 inheritance no longer owns it.
- Any future importer change must rebuild/import/capture before world-detail presentation evidence can be promoted.


## 2026-10-08 - P1C01 importer exact-head reproof anchor

- No world/detail behavior changed. A comment-only source touch on the production importer intentionally routes the next exact head through the corrected full visual train so the existing Shire material correction receives real UE4 import/render evidence.


## 2026-10-08 - P1C01 wooded-road threat / Bucklebury Ferry canon detail

- Existing chapter detail only; no new feature/chapter. Source alignment comes from the supplied story/canon material: the road encounter reads as a mounted Black Rider passing a roadside tree/root shelter, while Bucklebury Ferry reads as a broad landing/flat ferry with water-edge posts/lamps/reeds and a rising far-bank path.
- Added bounded RootHide visual enclosure around the existing gameplay corridor: 6 tree, 8 shrub and 4 rock HISM instances plus one non-colliding fallen-log hero detail. Existing `RootHide`, `KeepOffRoad`, Black Rider patrol and detection logic are untouched.
- Added 12 HISM path stones to make the far bank climb away from the Ferry landing plus two non-colliding rope-coil landing details.
- Repeated detail stays on existing HISM components; no new collision, Tick, synchronous production load, world authority or population ownership.
- P1C02/Bree remains locked. Fresh exact-head full UE4/render evidence is required before visual acceptance.

- Added a seventh exact-head review shot for the wooded-road hide corridor; the capture finalizer now fails closed unless all 7 images exist.


## 2026-10-08 - #1730 visual review and Black Rider material preservation

- Exact head `2a2158c2...` produced fresh six-shot rendered evidence and a launched Windows package. Review confirms material/importer correction is machine-proven, but the chapter is not visually accepted.
- The rendered settlement is materially more coherent than the earlier blank/blockout state, yet the visible asset language is still low-poly/proxy and Party/Ferry presentation still needs construction.
- Current Black Rider production proxy had a concrete presentation defect: after resident production meshes resolved, `ApplyPrototypeStyle` replaced their authored materials with Engine BasicShape dynamic material. The pending packet preserves authored production materials and colours only unresolved primitive fallbacks.
- Runtime synchronous `LoadObject` is removed from this Black Rider presentation path; fallback material is constructor-resident Engine content.
- This does not substitute for the required final animated Black Rider/horse FBX bundles.
