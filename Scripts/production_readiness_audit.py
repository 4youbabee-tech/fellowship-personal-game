#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
errors=[]; warnings=[]
def load(rel):
 p=ROOT/rel
 if not p.exists(): errors.append(f"missing required production contract: {rel}"); return {}
 try: return json.loads(p.read_text(encoding="utf-8"))
 except Exception as exc: errors.append(f"invalid {rel}: {exc}"); return {}
atlas=load("Data/Part1ProductionAtlas.json"); gate=load("Data/Production100ReadinessGate.json")
mega=load("Data/Part1MegaProductionPlan.json"); chars=load("Data/CharacterProductionMatrix.json")
world=load("Data/CinematicWorldProductionMatrix.json"); sources=load("Data/OwnerSourceReferenceIndex.json")
external=load("Data/ExternalAssetManifest.json")
required={("FrodoMain",f"P1C0{i}") for i in range(1,9)}|{("GandalfParallel","P1C01")}
actual={(str(x.get("route") or ""),str(x.get("chapter") or "")) for x in atlas.get("chapters",[]) if isinstance(x,dict)}
if actual!=required: errors.append(f"Part1ProductionAtlas chapter coverage mismatch: {sorted(actual)}")
for row in atlas.get("chapters",[]):
 if not isinstance(row,dict): continue
 key=f"{row.get('route')}/{row.get('chapter')}"
 for field in ("display_name","macro_region","primary_region"):
  if not row.get(field): errors.append(f"{key} missing {field}")
 for field in ("landmark_sequence","required_cast","source_asset_roots","hero_vistas","production_focus"):
  if not row.get(field): errors.append(f"{key} missing/nonempty {field}")
 for root in row.get("source_asset_roots",[]):
  if not (ROOT/root).exists(): errors.append(f"{key} source asset root missing: {root}")
for row in chars.get("characters",[]):
 if not isinstance(row,dict): continue
 root=row.get("asset_root")
 if root and not (ROOT/root).exists(): errors.append(f"character {row.get('id')} asset root missing: {root}")
for row in chars.get("threats",[]):
 if not isinstance(row,dict): continue
 root=row.get("asset_root")
 if root and not (ROOT/root).exists(): errors.append(f"threat {row.get('id')} asset root missing: {root}")
 if not root and not row.get("final_gaps"): errors.append(f"missing threat {row.get('id')} has no explicit final gap")
world_rows=world.get("regions",[])
if len(world_rows)<9: errors.append(f"CinematicWorldProductionMatrix has only {len(world_rows)} region rows")
for row in world_rows:
 if not isinstance(row,dict): continue
 for root in row.get("project_owned_asset_roots",[]):
  if not (ROOT/root).exists(): errors.append(f"world {row.get('chapter')} asset root missing: {root}")
source_ids={str(x.get("id") or "") for x in sources.get("sources",[]) if isinstance(x,dict)}
for sid in {"SRC_FILM_FOTR_SCREENPLAY","SRC_OWNER_MASTER_PACK","SRC_OWNER_PROJECT_SOURCE_PACK","SRC_OWNER_BATTLES_WEAPONS_ARMIES_BIBLE","SRC_OWNER_SIDE_ACTIVITIES_BIBLE"}:
 if sid not in source_ids: errors.append(f"source reference missing: {sid}")
if gate.get("production_100") is not False: errors.append("production_100 must remain false until final acceptance")
if mega.get("status")!="ACTIVE": errors.append("Part1MegaProductionPlan must remain ACTIVE")
for item in external.get("assets",[]):
 if isinstance(item,dict) and str(item.get("status") or "").upper()=="APPROVED":
  for field in ("provider","license_class","source","license_evidence"):
   if not item.get(field): errors.append(f"approved external asset missing {field}: {item.get('id')}")
obj_count=len(list((ROOT/"SourceAssets"/"Production").rglob("*.obj")))
print(f"PRODUCTION_READINESS: atlas_chapters={len(actual)} character_rows={len(chars.get('characters',[]))} threat_rows={len(chars.get('threats',[]))} world_rows={len(world_rows)} obj_files={obj_count}")
print("PRODUCTION_READINESS: production_100=false")
if errors:
 print(f"PRODUCTION_READINESS_AUDIT: FAIL ({len(errors)} error(s))")
 for error in errors: print("ERROR:",error)
 sys.exit(1)
print("PRODUCTION_READINESS_AUDIT: PASS")
