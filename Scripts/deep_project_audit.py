#!/usr/bin/env python3
from __future__ import annotations
import json,re,sys
from pathlib import Path
from runtime_audit_contracts import MODE_EXTRA_ARGS, mode_has_evidence
from source_contracts import signal_precedes_member_mutation
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"Source"/"ShireJourney"
errors=[]
def read(p): return p.read_text(encoding="utf-8",errors="replace")
gov=json.loads(read(ROOT/"Data"/"ProjectGovernor.json"))
ids=[str(r.get("id") or "") for r in gov.get("requirements",[]) if isinstance(r,dict)]
if len(ids)!=len(set(ids)): errors.append("duplicate Governor requirement IDs")
player=read(SRC/"ShirePlayerCharacter.cpp")
presentation=read(SRC/"ShireStoryPresentationSubsystem.cpp")
ambient=read(SRC/"ShireAmbientNPC.cpp")
named=read(SRC/"ShireNPC.cpp")
d=player.find('BindAction(TEXT("DebugPreviousChapter")')
a=player.rfind("#if !UE_BUILD_SHIPPING",0,d)
b=player.find("#endif",d)
if d<0 or a<0 or b<d: errors.append("shipping debug bindings are not guarded")
if "AsyncSaveGameToSlot" not in player or "bCheckpointSaveInFlight" not in player: errors.append("automatic checkpoint path is not async guarded")
if "FMath::Clamp(ActiveCue.SuggestedDuration, 1.0f, 3.5f)" not in presentation: errors.append("cinematic lock cap missing")
ambient_it=len(re.findall(r"TActorIterator<AShireAmbientNPC>",ambient))
named_it=len(re.findall(r"TActorIterator<AShireNPC>",named))
if ambient_it>1: errors.append(f"ambient actor scans grew: {ambient_it}")
if named_it>1: errors.append(f"named actor scans grew: {named_it}")
loads={}
for p in SRC.glob("*.cpp"):
 t=read(p); n=len(re.findall(r"\bLoadObject<",t))
 if n: loads[p.name]=n
 if re.search(r"void\s+\w+::Tick\s*\([^)]*\)[\s\S]{0,12000}?LoadObject<",t): errors.append(f"possible LoadObject in Tick: {p.name}")
 for match in re.finditer(r"LoadObject<[^>]+>\s*\([^;]+;", t, re.S):
  if "/Engine/BasicShapes/" not in match.group(0):
   errors.append(f"non-engine synchronous LoadObject remains: {p.name}")

# VISUAL PERFORMANCE ARCHITECTURE GUARD
perf_plan_path=ROOT/"Data"/"VisualPerformanceOptimizationPlan.json"
if not perf_plan_path.exists():
 errors.append("visual performance optimization plan missing")
else:
 try:
  perf_plan=json.loads(read(perf_plan_path))
 except Exception as exc:
  perf_plan={}
  errors.append(f"invalid visual performance optimization plan: {exc}")
 if perf_plan and perf_plan.get("plan_id")!="VISUAL_PERFORMANCE_OPTIMIZATION_V1":
  errors.append("visual performance optimization plan identity changed")

streaming_h=read(SRC/"ShireChapterAssetStreamingSubsystem.h")
streaming_cpp=read(SRC/"ShireChapterAssetStreamingSubsystem.cpp")
streaming_contract=streaming_h+"\n"+streaming_cpp
router=read(SRC/"ChapterWorldRouter.cpp")
npc_context=read(SRC/"ShireNPCContextSubsystem.cpp")
npc_context_h=read(SRC/"ShireNPCContextSubsystem.h")
audio=read(SRC/"ShireAudioSubsystem.cpp")
quest=read(SRC/"ShireQuestSubsystem.cpp")
player_h=read(SRC/"ShirePlayerCharacter.h")
importer=read(ROOT/"Source"/"ShireJourneyEditorTools"/"Private"/"ShireProductionImportCommandlet.cpp")
for symbol in ["FStreamableManager","FSoftObjectPath","RequestAsyncLoad"]:
 if symbol not in streaming_contract:
  errors.append(f"async chapter streaming contract missing: {symbol}")
if "LoadObject<" in streaming_cpp:
 errors.append("chapter streaming subsystem must not add synchronous LoadObject")
if "SetCommittedWorldContext" not in npc_context or router.count("SetCommittedWorldContext(") < 2:
 errors.append("committed NPC context bridge missing from normal commit/rollback paths")
for symbol in ["IsLogicalWorldContextCommitted()", "GetContextChapterId()", "GetContextRouteId()", "GetContextActiveQuestId()", "GetContextActiveQuestStage()"]:
 if symbol not in npc_context:
  errors.append(f"NPC committed-context query missing: {symbol}")
if "OnCharacterRigReady.Broadcast(CharacterId);" not in streaming_cpp or "Rig->Handle.Reset();" not in streaming_cpp:
 errors.append("character rig completion must release streamable handle after actor-owned handoff")
if "FPackageName::DoesPackageExist" not in streaming_cpp or "bAvailabilityChecked" not in streaming_h:
 errors.append("character rig request must preflight package existence before RequestAsyncLoad")
if "LoadObject<USoundBase>" in audio:
 errors.append("audio subsystem must not synchronously LoadObject production sound")
if "SetWorldTransitionHeld(bHold)" not in router:
 errors.append("router does not mirror world hold into player gameplay mutation barrier")
if "IsGameplayWorldCommitted()" not in player:
 errors.append("player committed-world gameplay mutation barrier missing")
for barrier_name in [
 "ShireQuestTrigger.cpp",
 "ShireTraversalChallenge.cpp",
 "ShireEnvironmentalPuzzle.cpp",
 "ShireWorldEventInteraction.cpp",
]:
 barrier_text=read(SRC/barrier_name)
 if "IsGameplayWorldCommitted()" not in barrier_text:
  errors.append(f"world-transition gameplay mutation guard missing: {barrier_name}")
if "IsLogicalWorldContextCommitted()" not in named:
 errors.append("named NPC banter/interaction committed-context guard missing")
restore_commit_start=quest.find("void UShireQuestSubsystem::CommitPersistenceRestore")
restore_commit_end=quest.find("void UShireQuestSubsystem::AbortPersistenceRestore",restore_commit_start)
restore_commit=quest[restore_commit_start:restore_commit_end]
repair_index=restore_commit.find("OnQuestStateRestored.Broadcast();")
release_index=restore_commit.find("bPersistenceRestoreInProgress = false;")
publish_index=restore_commit.find("OnExperienceChanged.Broadcast")
if min(repair_index,release_index,publish_index)<0 or not (repair_index<release_index<publish_index):
 errors.append("legacy restore repair may publish intermediate world identity")
if "CurrentRouteId != NAME_None && !bPersistenceRestoreInProgress" not in quest:
 errors.append("restore repair may overwrite restored route progress")

# WORLD TRANSACTION / COMMIT-BOUND HOUSEKEEPING
load_start=router.find("void AChapterWorldRouter::LoadChapterWorld")
load_end=router.find("void AChapterWorldRouter::HandleChapterAssetsReady",load_start)
load_body=router[load_start:load_end]
hold_index=load_body.find("SetPlayerWorldHold(true);")
pending_index=load_body.find("PendingRouteId = RouteId;")
if hold_index<0 or pending_index<0 or hold_index>pending_index:
 errors.append("world hold must begin before pending destination identity/preload")
if "SetPlayerWorldHold(false);" not in load_body:
 errors.append("A->pending B->A cancellation does not release world hold after exact-current recovery")

start_chapter_start=quest.find("void UShireQuestSubsystem::StartChapter")
start_chapter_end=quest.find("FShireRouteProgress UShireQuestSubsystem::CaptureCurrentRouteProgress",start_chapter_start)
start_chapter_body=quest[start_chapter_start:start_chapter_end]
if "PruneNPCMemoryForCurrentChapter();" in start_chapter_body:
 errors.append("StartChapter destructively prunes NPC memory before world commit")
if "CommitWorldBoundState()" not in quest or "CommitWorldBoundState();" not in router:
 errors.append("commit-bound NPC-memory housekeeping contract missing")

restore_memory_start=quest.find("void UShireQuestSubsystem::RestoreNPCMemoryState")
restore_memory_body=quest[restore_memory_start:]
if "if (!bPersistenceRestoreInProgress)" not in restore_memory_body:
 errors.append("restore NPC memory may prune before final canonical world identity")

# NPC committed-context query must be callable by consumers and fail closed before first commit.
public_end=npc_context_h.find("private:")
public_api=npc_context_h[:public_end if public_end>=0 else None]
if "IsLogicalWorldContextCommitted() const;" not in public_api:
 errors.append("NPC committed-context query is not public to world-facing consumers")
ctx_start=npc_context.find("bool UShireNPCContextSubsystem::IsLogicalWorldContextCommitted() const")
ctx_end=npc_context.find("FName UShireNPCContextSubsystem::GetContextChapterId",ctx_start)
ctx_body=npc_context[ctx_start:ctx_end]
if "if (!bHasCommittedWorldContext)" not in ctx_body or "return false;" not in ctx_body:
 errors.append("NPC context is permissive before first committed world")

# Async checkpoint completion may write disk later, but old-world completion cannot mutate new-world player life.
for token in [
 "CheckpointSaveInFlightChapterId",
 "CheckpointSaveInFlightRouteId",
 "CheckpointSaveInFlightEpisodeId",
 "CheckpointSaveInFlightWorldRevision",
]:
 if token not in player_h:
  errors.append(f"async checkpoint context token missing: {token}")
if "bSameCommittedContext" not in player or "bApplyCheckpointEffects" not in player:
 errors.append("async checkpoint completion is not bound to originating committed world")

# QUEUED ASYNC CHECKPOINTS MUST PRESERVE THE ORIGINAL SNAPSHOT.
for token in [
 "CheckpointSaveInFlightSnapshot",
 "QueuedCheckpointSnapshot",
 "QueuedCheckpointWorldRevision",
 "StartCheckpointSnapshotSave",
]:
 if token not in (player_h + player):
  errors.append(f"queued checkpoint snapshot/origin guard missing: {token}")
checkpoint_callback_start=player.find("void AShirePlayerCharacter::HandleCheckpointSaveComplete")
checkpoint_callback_end=player.find("bool AShirePlayerCharacter::RestoreAutomaticCheckpoint",checkpoint_callback_start)
checkpoint_callback=player[checkpoint_callback_start:checkpoint_callback_end]
if "SaveAutomaticCheckpoint(NextId" in checkpoint_callback:
 errors.append("queued checkpoint is reconstructed from later live state after async completion")

# PRE-MUTATION TRANSITION SNAPSHOT / ROLLBACK FAILURE CONTRACT
quest_h=read(SRC/"ShireQuestSubsystem.h")
game_mode=read(SRC/"ShireGameMode.cpp")
runtime_smoke=read(ROOT/"Scripts"/"runtime_smoke.py")
state_cmd=read(ROOT/"Scripts"/"ci_runtime_state.cmd")
if "FOnWorldTransitionRequested" not in quest_h or "OnWorldTransitionRequested" not in quest_h:
 errors.append("pre-mutation world transition request contract missing")
start_chapter_start=quest.find("void UShireQuestSubsystem::StartChapter")
start_chapter_end=quest.find("FShireRouteProgress UShireQuestSubsystem::CaptureCurrentRouteProgress",start_chapter_start)
start_chapter=quest[start_chapter_start:start_chapter_end]
if not signal_precedes_member_mutation(
    start_chapter,
    "OnWorldTransitionRequested.Broadcast",
    ("CurrentChapterId","CurrentEpisodeId","PlayableCharacterId")):
 errors.append("StartChapter transition signal is not pre-mutation")
start_experience_start=quest.find("void UShireQuestSubsystem::StartExperience")
start_experience_end=quest.find("TMap<FName, FShireRouteProgress>",start_experience_start)
start_experience=quest[start_experience_start:start_experience_end]
if not signal_precedes_member_mutation(
    start_experience,
    "OnWorldTransitionRequested.Broadcast",
    ("CurrentRouteId","CurrentChapterId","CurrentEpisodeId","PlayableCharacterId")):
 errors.append("StartExperience transition signal is not pre-mutation")
request_start=router.find("void AChapterWorldRouter::HandleWorldTransitionRequested")
request_end=router.find("void AChapterWorldRouter::HandleChapterChanged",request_start)
request_body=router[request_start:request_end]
request_capture=request_body.find("CaptureCommittedRollbackSnapshot();")
request_hold=request_body.rfind("SetPlayerWorldHold(true);")
if request_capture<0 or request_hold<0 or request_capture>request_hold:
 errors.append("router does not snapshot exact committed origin before the normal transition hold")
commit_start=router.find("void AChapterWorldRouter::CommitChapterWorld")
commit_body=router[commit_start:]
reject_start=commit_body.find("if (!bSupported)")
reject_end=commit_body.find("SetPlayerWorldHold(true);",reject_start)
reject_body=commit_body[reject_start:reject_end]
if reject_start<0 or "RollbackFailedWorldSwap" not in reject_body:
 errors.append("unsupported chapter/route request does not rollback atomically")
if not mode_has_evidence("faults", "fault.invalid_request_rejected") or "-AuditFaults" not in MODE_EXTRA_ARGS.get("faults", ()) or "--mode faults" not in state_cmd:
 errors.append("invalid-request preflight evidence chain missing")

# SAVE-RESTORE PRE-MUTATION BOUNDARY + DELAYED ASYNC AUTHORITY
streaming_test=streaming_cpp
game_mode=read(SRC/"ShireGameMode.cpp")
runtime_smoke=read(ROOT/"Scripts"/"runtime_smoke.py")
state_cmd=read(ROOT/"Scripts"/"ci_runtime_state.cmd")
if "PreparePersistenceWorldTransition" not in quest or "PreparePersistenceWorldTransition" not in player:
 errors.append("save restore does not share pre-mutation world transition boundary")
restore_start=player.find("bool AShirePlayerCharacter::RestoreSaveSnapshot")
restore_end=player.find("bool AShirePlayerCharacter::StartCheckpointSnapshotSave",restore_start)
restore_body=player[restore_start:restore_end]
restore_begin=restore_body.find("BeginPersistenceRestore()")
restore_prepare=restore_body.find("PreparePersistenceWorldTransition")
restore_mutate=restore_body.find("RestoreQuestState(")
if min(restore_begin,restore_prepare,restore_mutate)<0 or not (restore_begin<restore_prepare<restore_mutate):
 errors.append("save restore transition snapshot ordering is unsafe")
for token in ["PublishPendingReady","ShireCIAssetReadyDelay=","CompletedSerial != RequestSerial"]:
 if token not in streaming_test:
  errors.append(f"delayed async transition guard missing: {token}")
if not mode_has_evidence("pending", "pending.commit") or "-AuditPendingTransition" not in MODE_EXTRA_ARGS.get("pending", ()) or "--mode pending" not in state_cmd:
 errors.append("delayed transition old-world-authority evidence chain missing")

# FAIL-CLOSED CHAPTER BANK RESIDENCY / ROLLBACK OWNERSHIP
if "FOnShireChapterAssetsFailed" not in streaming_h or "OnChapterAssetsFailed" not in streaming_h:
 errors.append("chapter streaming failure delegate missing")
if "compatibility path continues" in streaming_cpp:
 errors.append("chapter streaming still contains compatibility-success fallback for missing residency")
for token in ["AreBankAssetsResolved","FailPendingRequest","async-complete-with-unresolved-assets"]:
 if token not in streaming_cpp:
  errors.append(f"chapter streaming fail-closed contract missing: {token}")
if "HandleChapterAssetsFailed" not in router or "OnChapterAssetsFailed.AddUObject" not in router:
 errors.append("router is not subscribed to chapter streaming failures")
router_fail_start=router.find("void AChapterWorldRouter::HandleChapterAssetsFailed")
router_fail_end=router.find("AActor* AChapterWorldRouter::SpawnWorldForRequest",router_fail_start)
router_fail=router[router_fail_start:router_fail_end]
if "RollbackFailedWorldSwap" not in router_fail:
 errors.append("chapter streaming failure does not rollback committed origin")
if "ShireCIForceChapterAssetFailure=" not in streaming_cpp:
 errors.append("deterministic non-production streaming failure injection missing")
if not mode_has_evidence("faults", "fault.stream_failure") or "-ShireCIForceChapterAssetFailure=P1C02" not in MODE_EXTRA_ARGS.get("faults", ()):
 errors.append("streaming failure runtime evidence chain missing")

# UE4.27 importer overload regression and deterministic normalization stay fail-closed.
if "ObjectPathToPackageName(ProductionSurfacePath)" in importer:
 errors.append("ambiguous UE4.27 ObjectPathToPackageName(const TCHAR*) call reintroduced")
if "ObjectPathToPackageName(ProductionSurfaceObjectPath)" not in importer:
 errors.append("explicit FString package-name preflight missing from production importer")

pre_unreal_workflow=read(ROOT/".github"/"workflows"/"pre-unreal-validation.yml")
if "python Scripts/asset_quality_audit.py --strict" not in pre_unreal_workflow:
 errors.append("Pre-Unreal workflow does not fail closed on structural asset-quality defects")

asset_quality=read(ROOT/"Scripts"/"asset_quality_audit.py")
for token in [
 "obj_with_degenerate_uv_triangles",
 "degenerate UV triangle",
 "obj_with_opposed_normals",
 "oppose the geometric face normal",
]:
 if token not in asset_quality:
  errors.append(f"source tangent-basis quality guard missing: {token}")



for builder_name in [
 "ShirePrototypeWorldBuilder.cpp",
 "BreePrototypeWorldBuilder.cpp",
 "FellowshipChapterWorldBuilder.cpp",
 "IsengardPrototypeWorldBuilder.cpp",
]:
 builder_text=read(SRC/builder_name)
 if "LoadObject<UStaticMesh>" in builder_text:
  errors.append(f"world builder reintroduced synchronous production mesh loading: {builder_name}")

detail=read(SRC/"WorldDetailCluster.cpp")
for symbol in ["UHierarchicalInstancedStaticMeshComponent","SetCullDistances","PrimaryActorTick.bCanEverTick = false"]:
 if symbol not in detail:
  errors.append(f"instanced detail/cull contract missing: {symbol}")

for builder_name in [
 "ShirePrototypeWorldBuilder.cpp",
 "BreePrototypeWorldBuilder.cpp",
 "FellowshipChapterWorldBuilder.cpp",
 "IsengardPrototypeWorldBuilder.cpp",
]:
 builder_text=read(SRC/builder_name)
 if "PrimaryActorTick.bCanEverTick = false" not in builder_text:
  errors.append(f"world builder unexpectedly became ticking: {builder_name}")

audit=json.loads(read(ROOT/"Data"/"DeepProjectAudit.json"))
if audit.get("status")!="ACTIVE_CONTINUOUS_AUDIT": errors.append("deep audit record inactive")
print("DEEP PROJECT AUDIT")
print(f"- governor requirements: {len(ids)}")
print(f"- open conflicts: {len(gov.get('open_conflicts',[]))}")
print(f"- ambient social iterators: {ambient_it}")
print(f"- named companion iterators: {named_it}")
print("- direct LoadObject counts: "+", ".join(f"{k}={v}" for k,v in sorted(loads.items())))
if errors:
 [print("ERROR:",e) for e in errors]
 print(f"DEEP PROJECT AUDIT FAILED: {len(errors)} error(s)")
 sys.exit(1)
print("DEEP PROJECT AUDIT PASSED")
