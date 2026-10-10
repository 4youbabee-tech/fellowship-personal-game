#!/usr/bin/env python3
"""Promote SHA256-verified CC0 single-material static FBX from existing P1C01 warehouse.

No provider downloads, no character imports, no acceptance claims.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import sys

WAVES=(("p1c01_wave39",39,39),("p1c01_wave60",60,59))
ROOT_REL=Path("World/Shire/VerifiedPBR")
WORDS={"village":("barrel","basket","bench","bucket","crate","pot","sack","cart","hay"),
       "road":("rock","stone","log","stump","moss","wood","fence","gate"),
       "garden":("flower","mushroom","planter","garden","plant")}
PNG=bytes.fromhex("89504e470d0a1a0a")
FBX=b"Kaydara FBX Binary"

class PromotionError(ValueError): pass
def check(ok,msg):
    if not ok: raise PromotionError(msg)
def digest(path):
    check(path.is_file() and not path.is_symlink(),"FILE_MISSING_OR_SYMLINK:"+str(path))
    sha=hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda:f.read(1024*1024),b""): sha.update(part)
    return path.stat().st_size,sha.hexdigest()
def obj(path):
    value=json.loads(path.read_text(encoding="utf-8-sig"))
    check(isinstance(value,dict),"INVALID_RECEIPT:"+str(path))
    return value
def identify(name):
    for cat,words in WORDS.items():
        if any(w in name.split("_") or name.startswith(w+"_") for w in words): return cat
    return None
def validate_wave(base,wave,source_count,converted_count):
    folder=base/"_p1c01_adaptive_polyhaven"/wave
    check(folder.is_dir() and not folder.is_symlink(),"MISSING_VERIFIED_WAVE:"+wave)
    r=obj(folder/"receipt_adaptive_pbr.json")
    check(r.get("wave")==wave and r.get("stage")=="PERSISTENT_WAREHOUSE_SOURCE_ONLY" and
          r.get("license")=="CC0" and r.get("provider")=="POLY_HAVEN" and
          r.get("original_source_count")==source_count and
          r.get("converted_fbx_count")==converted_count and
          len(r.get("asset_ids",[]))==source_count,"WAVE_IDENTITY_MISMATCH:"+wave)
    for name,key in (("source_receipt_original.json","source_receipt_sha256"),
                     ("pbr_receipt_original.json","pbr_receipt_sha256")):
        check(digest(folder/name)[1]==r.get(key),"RECEIPT_SHA_MISMATCH:"+wave)
    pbr=obj(folder/"pbr_receipt_original.json")
    check(pbr.get("prepared_assets")==converted_count,"PBR_COUNT_MISMATCH")
    rows={}
    for record in r.get("files",[]):
        path=Path(record.get("file",""))
        check(path.is_absolute() and path.resolve().is_relative_to(folder.resolve()) and
              not path.is_symlink(),"WAREHOUSE_PATH_UNSAFE")
        key=path.relative_to(folder).as_posix()
        check(key not in rows and record.get("provider")=="POLY_HAVEN" and
              record.get("license")=="CC0","UNTRUSTED_OR_DUPLICATE_RECEIPT")
        rows[key]=record
    selected=[]
    for item in pbr.get("assets",[]):
        slug=item.get("id")
        if not isinstance(slug,str) or not re.fullmatch("[a-z0-9_]{3,80}",slug): continue
        if slug in r.get("quarantined_ids",[]) or item.get("status")!="STATIC_SOURCE_QC_ONLY": continue
        category=identify(slug)
        if not category: continue
        prefix="assets/"+slug+"/prepared/"
        fbx=prefix+slug+".fbx"
        fbxrow=rows.get(fbx)
        if not fbxrow or fbxrow.get("state")!="SOURCE_PBR_PENDING_STATIC_GEOMETRY_LOD_COLLISION_QC" or fbxrow.get("bytes",0)>16*1024*1024: continue
        maps={}
        valid=True
        for m in item.get("maps",[]):
            rel=m.get("path","")
            role=m.get("role")
            if role not in ("BaseColor","NormalDX","ORM") or m.get("resolution")!=[1024,1024]: valid=False;break
            k=prefix+rel.split("assets/"+slug+"/",1)[-1]
            if k not in rows or rows[k].get("state")!="SOURCE_PBR_PENDING_STATIC_GEOMETRY_LOD_COLLISION_QC":valid=False;break
            maps[role]=(k,rows[k])
        # Every asset uses exactly one material group. Multiple groups/masks require a
        # dedicated UE slot QC implementation; never silently apply one diffuse map.
        prefixes={re.sub(r"_(BaseColor|NormalDX|ORM)[.]png$","",Path(k).name) for k,_ in maps.values()}
        if not valid or set(maps)!={"BaseColor","NormalDX","ORM"} or len(prefixes)!=1 or len(item.get("maps",[]))!=3:continue
        selected.append(dict(slug=slug,category=category,wave=wave,files={"FBX":(fbx,fbxrow),**maps}))
    return selected

def copy_qc(warehouse,wave,key,record,target,magic):
    source=warehouse/"_p1c01_adaptive_polyhaven"/wave/key
    check(source.resolve().is_relative_to(warehouse.resolve()),"PATH_ESCAPE")
    size,sha=digest(source)
    check(size==record.get("bytes") and sha==record.get("sha256"),"SOURCE_HASH_MISMATCH:"+key)
    with source.open("rb") as f:head=f.read(30)
    check(head.startswith(magic),"SOURCE_FORMAT_MISMATCH:"+key)
    if magic==PNG:
        check(struct.unpack(">II",head[16:24])==(1024,1024),"SOURCE_PNG_RESOLUTION_MISMATCH")
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        check(digest(target)==(size,sha),"DESTINATION_CHANGED:"+str(target))
    else:
        temp=target.with_suffix(target.suffix+".partial")
        check(not temp.exists(),"INCOMPLETE_STAGING:"+str(temp))
        shutil.copyfile(source,temp)
        check(digest(temp)==(size,sha),"COPY_HASH_FAILED")
        temp.replace(target)
    return {"bytes":size,"sha256":sha}

def stage(warehouse,project,limit=16,max_bytes=144*1024*1024):
    choices=[]
    for wave,original,prepared in WAVES:choices.extend(validate_wave(warehouse,wave,original,prepared))
    choices.sort(key=lambda i:(tuple(WORDS).index(i["category"]),i["slug"]))
    chosen=[];size=0;counts={x:0 for x in WORDS};ids=set()
    for item in choices:
        check(item["slug"] not in ids,"DUPLICATE_CROSS_WAVE_ID")
        ids.add(item["slug"])
        n=sum(r["bytes"] for _,r in item["files"].values())
        if len(chosen)>=limit or size+n>max_bytes or counts[item["category"]]>=6:continue
        size+=n;counts[item["category"]]+=1;chosen.append(item)
    check(chosen,"NO_SUITABLE_VERIFIED_PBR_STATIC_ASSETS")
    outputs=[]
    for item in chosen:
        slug=item["slug"];dest=project/"SourceAssets/Production"/ROOT_REL/slug
        material="MI_P1C01_"+slug
        files={}
        for role,(key,record) in item["files"].items():
            extension=".fbx" if role=="FBX" else ".png"
            name=slug+".fbx" if role=="FBX" else "TX_"+slug+"_"+role+extension
            files[role]=name
            copy_qc(warehouse,item["wave"],key,record,dest/name,FBX if role=="FBX" else PNG)
        # Existing importer uses authored .mtl map_Kd and synthesizes the material.
        # Normal and ORM remain imported as source textures, awaiting a real PBR
        # material-slot wiring pass; never call material visually complete.
        mtl=dest/(slug+".mtl")
        material_text="newmtl "+material+"\nKd 1 1 1\nPr 0.68\nPm 0\nmap_Kd "+files["BaseColor"]+"\n"
        if mtl.exists():check(mtl.read_text(encoding="utf-8")==material_text,"MTL_CHANGED")
        else:mtl.write_text(material_text,encoding="utf-8")
        outputs.append({"id":slug,"category":item["category"],"wave":item["wave"],
                        "mesh":"/Game/Production/"+ROOT_REL.as_posix()+"/"+slug+"/"+slug+"."+slug,
                        "material":"/Game/Production/"+ROOT_REL.as_posix()+"/"+slug+"/"+material+"."+material,
                        "state":"SOURCE_HASH_QC_ONLY"})
    output=project/"Saved/P1C01VerifiedPBR/source_stage_receipt.json"
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps({"schema_version":1,"stage":"HASHED_SOURCE_ONLY",
        "count":len(outputs),"source_bytes":size,"assets":outputs,
        "note":"FBX/PNG source only; NOT UE imported, PBR complete, PIE-tested, or Gate 6/7 accepted"},indent=2)+"\n")
    print("P1C01_SOURCE_PBR_STAGE_PASS count="+str(len(outputs))+" sourceBytes="+str(size)+" ueImported=false")
    return outputs

def activate(project):
    path=project/"Saved/P1C01VerifiedPBR/source_stage_receipt.json"
    receipt=obj(path)
    check(receipt.get("stage")=="HASHED_SOURCE_ONLY","NO_STAGED_RECEIPT")
    for row in receipt["assets"]:
        slug=row["id"];root=project/"Content/Production"/ROOT_REL/slug
        for asset in (slug,"MI_P1C01_"+slug):
            f=root/(asset+".uasset")
            check(f.is_file() and f.stat().st_size>2048,"UE_PACKAGE_MISSING:"+str(f))
    plan_path=project/"Data/ChapterAssetStreamingPlan.json"
    plan=obj(plan_path);bank=plan["banks"]["P1C01"]["assets"]
    for row in receipt["assets"]:
        if row["mesh"] not in bank:bank.append(row["mesh"])
    bank.sort()
    plan_path.write_text(json.dumps(plan,indent=2)+"\n")
    print("P1C01_UE_PBR_SOURCE_ASSETS_PRESENT count="+str(len(receipt["assets"]))+
          " runtimeBank="+str(len(bank))+" visualNotAccepted=true")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--warehouse-root",type=Path)
    p.add_argument("--project-root",required=True,type=Path)
    p.add_argument("--activate-after-import",action="store_true")
    args=p.parse_args()
    try:
        if args.activate_after_import:activate(args.project_root)
        else:
            check(args.warehouse_root is not None,"WAREHOUSE_REQUIRED")
            stage(args.warehouse_root,args.project_root)
        return 0
    except (PromotionError,KeyError,ValueError,OSError) as e:
        print("P1C01_SOURCE_BRIDGE_FAIL "+str(e),file=sys.stderr)
        return 2
if __name__=="__main__":raise SystemExit(main())
