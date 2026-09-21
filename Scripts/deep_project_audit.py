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
# AAA architecture debt guardrails: preserve current legacy debt while preventing regressions.
guardrail_path=ROOT/"Data"/"ArchitectureGuardrails.json"
if not guardrail_path.exists():
 errors.append("architecture guardrails missing: Data/ArchitectureGuardrails.json")
else:
 try:
  guardrails=json.loads(read(guardrail_path))
 except Exception as exc:
  guardrails={}
  errors.append(f"invalid architecture guardrails: {exc}")
 if guardrails:
  ceiling=guardrails.get("legacy_ceiling",{})
  load_ceiling=ceiling.get("direct_loadobject_by_cpp",{})
  for filename,limit in load_ceiling.items():
   actual=loads.get(filename,0)
   if actual>int(limit):
    errors.append(f"direct LoadObject debt grew: {filename} {actual}>{limit}")
  unexpected=sorted(set(loads)-set(load_ceiling))
  if unexpected:
   errors.append("new runtime LoadObject file(s) outside legacy allowlist: "+", ".join(unexpected))

  production=ROOT/"SourceAssets"/"Production"
  bmp_count=len(list(production.rglob("*.bmp")))
  character_obj=len(list((production/"Characters").rglob("*.obj")))
  enemy_obj=len(list((production/"Enemies").rglob("*.obj")))
  if bmp_count>int(ceiling.get("production_bmp",bmp_count)):
   errors.append(f"production BMP debt grew: {bmp_count}>{ceiling.get('production_bmp')}")
  if character_obj>int(ceiling.get("character_obj",character_obj)):
   errors.append(f"character OBJ debt grew: {character_obj}>{ceiling.get('character_obj')}")
  if enemy_obj>int(ceiling.get("enemy_obj",enemy_obj)):
   errors.append(f"enemy OBJ debt grew: {enemy_obj}>{ceiling.get('enemy_obj')}")

  sk_obj=sorted(
   p.relative_to(ROOT).as_posix()
   for root in [production/"Characters",production/"Enemies"]
   if root.exists()
   for p in root.rglob("SK_*.obj")
  )
  if sk_obj:
   errors.append("skeletal-prefixed animated production assets may not use OBJ: "+", ".join(sk_obj[:12]))

  living=read(SRC/"LivingWorldDirector.cpp")
  ambient_spawn_sites=len(re.findall(r"SpawnActor\s*<\s*AShireAmbientNPC\s*>",living))
  if ambient_spawn_sites>int(ceiling.get("living_world_direct_ambient_spawn_sites",ambient_spawn_sites)):
   errors.append(
    f"LivingWorldDirector direct ambient SpawnActor sites grew: {ambient_spawn_sites}>"
    f"{ceiling.get('living_world_direct_ambient_spawn_sites')}"
   )

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
