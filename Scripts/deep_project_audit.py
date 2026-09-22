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
if ambient_it>2: errors.append(f"ambient actor scans grew: {ambient_it}")
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
audio=read(SRC/"ShireAudioSubsystem.cpp")
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
