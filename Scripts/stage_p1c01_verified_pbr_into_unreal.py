#!/usr/bin/env python3
"""Verify and stage permitted static P1C01 PBR sources from pinned, durable CC0 waves.
Never fetch providers, touch character rigs, or imply Unreal/visual acceptance.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import sys

WAVES=(("p1c01_wave39",39,39),("p1c01_wave60",60,59))
WORDS={"village":("barrel","basket","bench","bucket","crate","cart","wooden"),
       "road":("rock","stone","log","stump","plank","moss","fence"),
       "garden":("flower","mushroom","planter","garden","plant")}
ANCHORS={"village":((2700,2000,0),(4900,-2200,0),(6200,2050,0)),
         "road":((8700,2400,0),(15700,-2400,0),(17300,2200,0)),
         "garden":((800,1500,0),(4200,-2000,0),(5600,1900,0))}
PREFIX=Path("World/Shire/VerifiedPBR")
MAGIC=b"Kaydara FBX Binary"
class StageError(ValueError): pass
def guard(ok,msg):
    if not ok: raise StageError(msg)
def digest(file):
    guard(file.is_file() and not file.is_symlink(),"MISSING_FILE:"+str(file))
    sha=hashlib.sha256()
    with file.open("rb") as f:
        for block in iter(lambda:f.read(1048576),b""):sha.update(block)
    return file.stat().st_size,sha.hexdigest()
def obj(file):
    x=json.loads(file.read_text(encoding="utf-8-sig"))
    guard(isinstance(x,dict),"BAD_JSON:"+str(file))
    return x
def check(root,row):
    path=Path(row.get("file",""))
    guard(path.is_absolute() and not path.is_symlink() and root.resolve() in path.resolve().parents,
          "UNSAFE_RECEIPT_PATH")
    size,hash=digest(path)
    guard(size==row.get("bytes") and hash==row.get("sha256"),"SOURCE_HASH_MISMATCH:"+str(path))
    return path
def classify(slug):
    for group,words in WORDS.items():
        if any(word in slug.split("_") for word in words):return group
    return None
def scan(warehouse):
    choices=[]
    for wave,expected_source,expected_pbr in WAVES:
        root=warehouse/"_p1c01_adaptive_polyhaven"/wave
        receipt=obj(root/"receipt_adaptive_pbr.json")
        guard(receipt.get("wave")==wave and receipt.get("license")=="CC0"
              and receipt.get("stage")=="PERSISTENT_WAREHOUSE_SOURCE_ONLY"
              and receipt.get("original_source_count")==expected_source
              and receipt.get("converted_fbx_count")==expected_pbr,
              "UNVERIFIED_WAVE:"+wave)
        for name,key in (("source_receipt_original.json","source_receipt_sha256"),
                         ("pbr_receipt_original.json","pbr_receipt_sha256")):
            guard(digest(root/name)[1]==receipt.get(key),"RECEIPT_DIGEST_MISMATCH")
        pbr=obj(root/"pbr_receipt_original.json")
        guard(pbr.get("prepared_assets")==expected_pbr,"PBR_RECEIPT_COUNT")
        rows={}
        for row in receipt.get("files",[]):
            file=Path(row.get("file",""))
            guard(file.is_absolute() and root.resolve() in file.resolve().parents,
                  "UNSAFE_SOURCE_RECORD")
            key=file.relative_to(root).as_posix()
            guard(key not in rows and row.get("provider")=="POLY_HAVEN"
                  and row.get("license")=="CC0","BAD_SOURCE_RECORD")
            rows[key]=row
        for item in pbr.get("assets",[]):
            slug=item.get("id","")
            group=classify(slug)
            if not re.fullmatch("[a-z0-9_]{3,80}",slug) or not group or item.get("status")!="STATIC_SOURCE_QC_ONLY":
                continue
            base="assets/"+slug+"/prepared/"
            fbx=rows.get(base+slug+".fbx")
            if not fbx or fbx.get("state")!="SOURCE_PBR_PENDING_STATIC_GEOMETRY_LOD_COLLISION_QC" or fbx.get("bytes",0)>16777216:
                continue
            groups={}
            for image in item.get("maps",[]):
                match=re.fullmatch(r"TX_(.+)_(BaseColor|NormalDX|ORM)\\.png",Path(image.get("path","")).name)
                if match and image.get("resolution")==[1024,1024]:
                    groups.setdefault(match.group(1),{})[match.group(2)]=rows.get(base+Path(image["path"]).name)
            if len(groups)!=1:continue
            maps=next(iter(groups.values()))
            if set(maps)!={"BaseColor","NormalDX","ORM"} or not all(maps.values()):continue
            if any(x.get("state")!="SOURCE_PBR_PENDING_STATIC_GEOMETRY_LOD_COLLISION_QC" for x in maps.values()):continue
            choices.append((slug,group,root,fbx,maps))
    return choices
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--warehouse-root",type=Path,required=True)
    ap.add_argument("--project-root",type=Path,required=True)
    ap.add_argument("--max-items",type=int,default=9)
    args=ap.parse_args()
    overlay=args.project_root/"SourceAssets/Production"/PREFIX
    guard(args.max_items>0 and args.max_items<=12,"BUDGET_UNSAFE")
    choices=sorted(scan(args.warehouse_root),key=lambda x:(list(WORDS).index(x[1]),x[0]))
    counts={key:0 for key in WORDS}
    selected=[]
    total=0
    for slug,group,root,fbx,maps in choices:
        if len(selected)>=args.max_items:break
        size=fbx["bytes"]+sum(x["bytes"] for x in maps.values())
        if counts[group]>=3 or total+size>100663296:continue
        total+=size
        directory=overlay/slug
        directory.mkdir(parents=True,exist_ok=True)
        for row in [fbx,*maps.values()]:
            src=check(root,row)
            dest=directory/src.name
            if dest.exists():guard(digest(dest)==digest(src),"DESTINATION_DIGEST_DRIFT")
            else:
                tmp=dest.with_name(dest.name+".partial")
                guard(not tmp.exists(),"INCOMPLETE_TRANSACTION")
                shutil.copyfile(src,tmp)
                guard(digest(tmp)==digest(src),"COPY_DIGEST_MISMATCH")
                os.replace(tmp,dest)
        # Importer creates this authored material instance and binds BaseColor.
        sidecar=directory/(slug+".mtl")
        material="MI_P1C01_"+slug
        lines=["newmtl "+material,"Kd 1 1 1","Pr 0.68","Pm 0","Ks 0.1 0.1 0.1",
               "map_Kd "+Path(maps["BaseColor"]["file"]).name,
               "map_Bump "+Path(maps["NormalDX"]["file"]).name,
               "map_ORM "+Path(maps["ORM"]["file"]).name,""]
        text="\n".join(lines)
        if sidecar.exists():guard(sidecar.read_text(encoding="utf-8")==text,"MTL_DRIFT")
        else:sidecar.write_text(text,encoding="utf-8")
        counts[group]+=1
        location=ANCHORS[group][(counts[group]-1)%len(ANCHORS[group])]
        selected.append({"id":slug,"group":group,"location":list(location),
                         "asset":"/Game/Production/"+PREFIX.as_posix()+"/"+slug+"/"+slug+"."+slug,
                         "material":"/Game/Production/"+PREFIX.as_posix()+"/"+slug+"/"+material+"."+material,
                         "basecolor_asset":Path(maps["BaseColor"]["file"]).stem,
                         "radius_cm":90,"source_wave":root.name})
    # Physical importer has not run yet. Keep the runtime registry empty until
    # exact UE4 packages are subsequently proven on disk.
    out=args.project_root/"Saved/P1C01VerifiedPBR/source_stage_receipt.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"status":"HASH_VERIFIED_SOURCE_ONLY","selected":selected,
            "selected_count":len(selected),"source_bytes":total,"ue_imported":False},indent=2)+"\n")
    guard(bool(selected),"NO_ELIGIBLE_SHIRE_STATIC_PBR_SOURCE")
    print("P1C01_PBR_STAGE_PASS count="+str(len(selected))+" bytes="+str(total)+" ueImported=false")
if __name__=="__main__":
    try:main()
    except (OSError,ValueError,KeyError) as e:
        print("P1C01_PBR_STAGE_FAILED "+str(e),file=sys.stderr)
        sys.exit(2)
