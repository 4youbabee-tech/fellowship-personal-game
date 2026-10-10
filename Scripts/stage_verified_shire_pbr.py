#!/usr/bin/env python3
"""Hash-verified CC0 static-source bridge. No source downloads, no false UE acceptance."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

WAVES=(("p1c01_wave39",39,39),("p1c01_wave60",60,59))
SLUG=re.compile(r"[a-z0-9_]{3,80}\Z")
SHA=re.compile(r"[a-f0-9]{64}\Z")
MAX_FILES=16
MAX_BYTES=144*1024*1024
CATEGORIES={"village":("barrel","basket","bench","bucket","crate","sack","cart","hay"),
            "garden":("flower","plant","pot","mushroom"),
            "road":("rock","stone","log","stump","plank","wood","moss")}
ROLES=("BaseColor","NormalDX","ORM")

class IntakeError(ValueError): pass
def demand(ok,msg):
    if not ok: raise IntakeError(msg)
def digest(path):
    demand(path.is_file() and not path.is_symlink(),"MISSING_OR_SYMLINK:"+str(path))
    h=hashlib.sha256(); size=0
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block);size+=len(block)
    return size,h.hexdigest()
def load(path):
    demand(path.is_file() and not path.is_symlink(),"MISSING_RECEIPT:"+str(path))
    data=json.loads(path.read_text(encoding="utf-8-sig"))
    demand(isinstance(data,dict),"RECEIPT_NOT_OBJECT")
    return data
def within(base,path):
    demand(base.resolve() in path.resolve().parents and not path.is_symlink(),
           "SOURCE_OUTSIDE_WAREHOUSE:"+str(path))
def source_file(base,row):
    path=Path(str(row["file"]))
    within(base,path)
    demand(row.get("provider")=="POLY_HAVEN" and row.get("license")=="CC0","UNLICENSED_PAYLOAD")
    demand(isinstance(row.get("bytes"),int) and isinstance(row.get("sha256"),str)
           and SHA.fullmatch(row["sha256"]),"BAD_RECEIPT_HASH")
    demand(digest(path)==(row["bytes"],row["sha256"]),"SOURCE_SHA256_MISMATCH:"+str(path))
    return path
def stage(warehouse,project,max_items=MAX_FILES,max_bytes=MAX_BYTES):
    demand(max_items>0 and max_bytes>0,"INVALID_BUDGET")
    found=[];seen=set()
    for wave,n,ready in WAVES:
        root=warehouse/"_p1c01_adaptive_polyhaven"/wave
        meta=load(root/"receipt_adaptive_pbr.json")
        demand(meta.get("wave")==wave and meta.get("stage")=="PERSISTENT_WAREHOUSE_SOURCE_ONLY"
               and meta.get("original_source_count")==n and meta.get("converted_fbx_count")==ready
               and meta.get("license")=="CC0","WAVE_QC_NOT_PROVEN:"+wave)
        demand(digest(root/"source_receipt_original.json")[1]==meta.get("source_receipt_sha256")
               and digest(root/"pbr_receipt_original.json")[1]==meta.get("pbr_receipt_sha256"),
               "PINNED_RECEIPT_HASH_MISMATCH")
        pbr=load(root/"pbr_receipt_original.json")
        demand(len(meta.get("asset_ids",[]))==n
               and pbr.get("prepared_assets")==ready
               and len(pbr.get("assets",[]))==ready,
               "RECEIPT_ASSET_COUNT_DRIFT")
        rows={}
        for row in meta.get("files",[]):
            path=Path(str(row["file"]))
            within(root,path)
            rel=path.relative_to(root).as_posix()
            demand(rel not in rows,"DUPLICATE_FILE_RECEIPT")
            rows[rel]=row
        for item in pbr.get("assets",[]):
            slug=item.get("id","")
            if (not isinstance(slug,str) or not SLUG.fullmatch(slug)
                    or slug in seen or item.get("status")!="STATIC_SOURCE_QC_ONLY"):continue
            category=next((key for key,terms in CATEGORIES.items()
                           if any(part.startswith(term) for part in re.split(r"[_-]",slug)
                                  for term in terms)),None)
            if not category:continue
            fbx="assets/"+slug+"/prepared/"+slug+".fbx"
            if fbx not in rows or rows[fbx].get("state")!="SOURCE_PBR_PENDING_STATIC_GEOMETRY_LOD_COLLISION_QC":continue
            groups={}
            for item_map in item.get("maps",[]):
                match=re.fullmatch(r"TX_(.+)_(BaseColor|NormalDX|ORM)\.png",
                                   Path(str(item_map.get("path",""))).name)
                if not match or item_map.get("resolution")!=[1024,1024]:
                    groups={};break
                groups.setdefault(match.group(1),{})[match.group(2)]=item_map
            if len(groups)!=1:continue
            maps=next(iter(groups.values()))
            if set(maps)!=set(ROLES):continue
            paths={}
            for role,info in maps.items():
                rel="assets/"+slug+"/prepared/"+Path(info["path"]).name
                if rel not in rows or rows[rel].get("state")!="SOURCE_PBR_PENDING_STATIC_GEOMETRY_LOD_COLLISION_QC":
                    paths={};break
                paths[role]=rel
            if len(paths)!=3:continue
            sources=[fbx,*paths.values()]
            bytes_needed=sum(rows[k]["bytes"] for k in sources)
            if rows[fbx]["bytes"]>16*1024*1024:continue
            if len(found)>=max_items or bytes_needed>max_bytes:continue
            found.append((category,slug,wave,root,rows,fbx,paths,bytes_needed))
            seen.add(slug)
    found.sort(key=lambda r:(tuple(CATEGORIES).index(r[0]),r[1]))
    overlay=project/"SourceAssets/Production/World/Shire/VerifiedPBR"
    demand(not overlay.is_symlink(),"OVERLAY_SYMLINK")
    selected=[];total=0
    for category,slug,wave,root,rows,fbx,paths,size in found:
        if len(selected)>=max_items:break
        if total+size>max_bytes:continue
        if sum(x["category"]==category for x in selected)>=6:continue
        dst=overlay/slug
        copies=[]
        for relative in [fbx,*paths.values()]:
            original=source_file(root,rows[relative])
            with original.open("rb") as f:header=f.read(26)
            if relative.endswith(".fbx"):demand(header.startswith(b"Kaydara FBX Binary"),"BAD_BINARY_FBX")
            else:demand(header.startswith(bytes.fromhex("89504e470d0a1a0a"))
                        and int.from_bytes(header[16:20],"big")==1024
                        and int.from_bytes(header[20:24],"big")==1024,"BAD_PNG_1K")
            target=dst/original.name
            target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists():
                demand(digest(target)==digest(original),"EXISTING_TARGET_DRIFT")
            else:
                temp=target.with_suffix(target.suffix+".partial")
                demand(not temp.exists(),"UNFINISHED_COPY_PRESENT")
                shutil.copyfile(original,temp)
                demand(digest(temp)==digest(original),"COPY_HASH_MISMATCH")
                temp.replace(target)
            copies.append({"path":str(target),"sha256":rows[relative]["sha256"]})
        mat="MI_P1C01_"+slug
        mtl=dst/(slug+".mtl")
        content="newmtl "+mat+"\nKd 1 1 1\nPr 0.68\nPm 0\nmap_Kd "+Path(paths["BaseColor"]).name+"\n"
        if mtl.exists():demand(mtl.read_text(encoding="utf-8")==content,"MATERIAL_SIDECAR_DRIFT")
        else:mtl.write_text(content,encoding="utf-8")
        selected.append({"id":slug,"wave":wave,"category":category,
                         "asset":"/Game/Production/World/Shire/VerifiedPBR/"+slug+"/"+slug+"."+slug,
                         "material":"/Game/Production/World/Shire/VerifiedPBR/"+slug+"/"+mat+"."+mat,
                         "source_bytes":size,"files":copies,
                         "status":"SOURCE_STAGED_UNREAL_IMPORT_QC_PENDING"})
        total+=size
    demand(bool(selected),"NO_SAFE_SHIRE_STATIC_PBR_CANDIDATES")
    receipt={"schema_version":1,"chapter":"P1C01","stage":"HASH_VERIFIED_SOURCE_ONLY",
             "selected_count":len(selected),"source_bytes":total,"assets":selected,
             "evidence_boundary":"Not Unreal-imported, material-bound, visually reviewed, PIE or device tested."}
    path=project/"Saved/P1C01VerifiedPBR/stage_receipt.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print("P1C01_VERIFIED_PBR_SOURCE_STAGE_PASS selected="+str(len(selected))+" bytes="+str(total))
    return receipt
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--warehouse-root",type=Path,required=True)
    parser.add_argument("--project-root",type=Path,required=True)
    a=parser.parse_args()
    try:stage(a.warehouse_root,a.project_root)
    except (IntakeError,ValueError,KeyError,TypeError,OSError) as e:
        print("P1C01_VERIFIED_PBR_SOURCE_STAGE_FAIL "+str(e),file=sys.stderr);return 2
    return 0
if __name__=="__main__":raise SystemExit(main())
