#!/usr/bin/env python3
from __future__ import annotations
import json,re,sys
from pathlib import Path
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

# UE4.27 importer overload regression and deterministic normalization stay fail-closed.
if "ObjectPathToPackageName(ProductionSurfacePath)" in importer:
 errors.append("ambiguous UE4.27 ObjectPathToPackageName(const TCHAR*) call reintroduced")
if "ObjectPathToPackageName(ProductionSurfaceObjectPath)" not in importer:
 errors.append("explicit FString package-name preflight missing from production importer")



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
