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
