#!/usr/bin/env python3
"""Hash-verified Poly Haven CC0 static PBR source -> existing Shire UE import.
No provider downloads, no skeleton/character import, no false acceptance.
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

WAREHOUSE_WAVES = (("p1c01_wave39", 39, 39), ("p1c01_wave60", 60, 59))
FAMILIES = {"village": ("barrel","basket","bench","bucket","crate","pot","sack","wooden","wheel","cart","hay"),
            "garden": ("flower","mushroom","planter","garden","plant"),
            "road": ("rock","stone","log","stump","plank","moss","wood","fence","gate")}
LOCATIONS = {"village": [(2600,2050,0),(3500,-1900,0),(4900,1800,0),(6200,-1950,0)],
             "garden": [(500,1150,0),(1200,-1650,0),(4100,2150,0),(5850,-1700,0)],
             "road": [(8700,2100,0),(10000,-2200,0),(15700,2200,0),(17200,-2000,0)]}
FBX_MAGIC = b"Kaydara FBX Binary"
PNG_MAGIC = bytes.fromhex("89504e470d0a1a0a")
OVERLAY = Path("World/Shire/VerifiedPBR")
SHA = re.compile(r"[0-9a-f]{64}\Z")
SLUG = re.compile(r"[a-z0-9_]{3,80}\Z")

class Reject(ValueError): pass
def require(value, reason):
    if not value: raise Reject(reason)
def digest(file):
    require(file.is_file() and not file.is_symlink(), "MISSING_OR_LINK:" + str(file))
    h=hashlib.sha256(); n=0
    with file.open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):
            n+=len(block);h.update(block)
    return n,h.hexdigest()
def read(path):
    obj=json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(obj,dict), "INVALID_JSON:" + str(path))
    return obj
def kind(slug):
    pieces=slug.split("_")
    for family, words in FAMILIES.items():
        if any(any(part.startswith(x) for x in words) for part in pieces):return family
    return None
def inventory(warehouse):
    selected=[]
    previous=set()
    for wave, count, converted in WAREHOUSE_WAVES:
        root=warehouse/"_p1c01_adaptive_polyhaven"/wave
        require(root.is_dir() and not root.is_symlink(), "WAREHOUSE_WAVE_UNAVAILABLE:"+wave)
        receipt=read(root/"receipt_adaptive_pbr.json")
        require(receipt.get("wave")==wave and receipt.get("stage")=="PERSISTENT_WAREHOUSE_SOURCE_ONLY"
                and receipt.get("provider")=="POLY_HAVEN" and receipt.get("license")=="CC0"
                and receipt.get("original_source_count")==count and receipt.get("converted_fbx_count")==converted,
                "UNVERIFIED_WAVE:"+wave)
        for original,field in (("source_receipt_original.json","source_receipt_sha256"),
                               ("pbr_receipt_original.json","pbr_receipt_sha256")):
            require(digest(root/original)[1]==receipt.get(field),"RECEIPT_SHA256_MISMATCH:"+wave)
        pbr=read(root/"pbr_receipt_original.json")
        require(pbr.get("prepared_assets")==converted,"PBR_COUNT_MISMATCH")
        rows={}
        for r in receipt["files"]:
            src=Path(r["file"])
            require(src.is_relative_to(root) and not src.is_symlink(),"RECEIPT_PATH_OUTSIDE_WAREHOUSE")
            relative=src.relative_to(root).as_posix()
            require(relative not in rows and r.get("provider")=="POLY_HAVEN" and r.get("license")=="CC0",
                    "DUPLICATE_OR_UNLICENSED_RECEIPT")
            rows[relative]=r
        for a in pbr["assets"]:
            slug=a["id"]
            require(SLUG.fullmatch(slug) and slug not in previous,"DUPLICATE_OR_INVALID_ASSET")
            previous.add(slug)
            family=kind(slug)
            if a.get("status")!="STATIC_SOURCE_QC_ONLY" or not family:continue
            meshkey="assets/"+slug+"/prepared/"+slug+".fbx"
            mesh=rows.get(meshkey)
            if not mesh or mesh.get("state")!="SOURCE_PBR_PENDING_STATIC_GEOMETRY_LOD_COLLISION_QC":continue
            if mesh.get("bytes",0)>16*1024*1024:continue
            groups={}
            for m in a.get("maps",[]):
                name=Path(m["path"]).name
                v=re.fullmatch(r"TX_(.+)_(BaseColor|NormalDX|ORM|OpacityMask)\.png",name)
                if not v or m.get("resolution")!=[1024,1024]:groups={};break
                group,role=v.groups()
                groups.setdefault(group,{})[role]=(m,name)
            if len(groups)!=1:continue
            textures=next(iter(groups.values()))
            if set(textures)!={"BaseColor","NormalDX","ORM"}:continue
            entries={"fbx":(meshkey,mesh)}
            for role,(meta,name) in textures.items():
                key="assets/"+slug+"/prepared/"+name
                row=rows.get(key)
                if not row or row.get("state")!="SOURCE_PBR_PENDING_STATIC_GEOMETRY_LOD_COLLISION_QC":
                    entries={};break
                entries[role]=(key,row)
            if entries:
                selected.append((wave,root,slug,family,entries))
    return selected

def checked_copy(root,key,meta,target,magic):
    src=root/key
    require(src.is_relative_to(root) and not src.is_symlink(),"UNSAFE_PAYLOAD_PATH")
    require(isinstance(meta.get("sha256"),str) and SHA.fullmatch(meta["sha256"])
            and isinstance(meta.get("bytes"),int),"UNSAFE_PAYLOAD_RECEIPT")
    n,sha=digest(src)
    require((n,sha)==(meta["bytes"],meta["sha256"]),"PAYLOAD_SHA256_MISMATCH:"+key)
    with src.open("rb") as f: header=f.read(32)
    require(header.startswith(magic),"FILE_MAGIC_INVALID:"+key)
    if magic==PNG_MAGIC:
        require(len(header)>=24 and struct.unpack(">II",header[16:24])==(1024,1024),"TEXTURE_NOT_1K")
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        require(digest(target)==(n,sha),"EXISTING_DESTINATION_TAMPERED")
    else:
        temp=target.with_name(target.name+".partial")
        require(not temp.exists(),"INCOMPLETE_OLD_COPY")
        try:
            shutil.copyfile(src,temp)
            require(digest(temp)==(n,sha),"COPY_CHECKSUM_FAILED")
            os.replace(temp,target)
        finally:
            if temp.exists():temp.unlink()
    return {"file":str(target),"sha256":sha,"bytes":n}

def stage(warehouse,project):
    candidates=inventory(warehouse)
    candidates.sort(key=lambda t:(list(FAMILIES).index(t[3]),t[2]))
    selected=[];bytes_total=0;counts={x:0 for x in FAMILIES}
    for wave,root,slug,family,entries in candidates:
        n=sum(x[1]["bytes"] for x in entries.values())
        if len(selected)>=16:break
        if counts[family]>=6 or bytes_total+n>144*1024*1024:continue
        counts[family]+=1;bytes_total+=n
        target=project/"SourceAssets/Production"/OVERLAY/slug
        products=[]
        for role,(name,receipt) in entries.items():
            products.append(checked_copy(root,name,receipt,target/Path(name).name,
                                         FBX_MAGIC if role=="fbx" else PNG_MAGIC))
        mname="MI_P1C01_"+slug
        material="\n".join(("newmtl "+mname,"Kd 1 1 1","Pr 0.68","Pm 0",
                            "map_Kd "+Path(entries["BaseColor"][0]).name,
                            "map_Bump "+Path(entries["NormalDX"][0]).name,
                            "map_ORM "+Path(entries["ORM"][0]).name,""))
        mtl=target/(slug+".mtl")
        if mtl.exists():require(mtl.read_text(encoding="utf-8")==material,"MTL_SIDE_CAR_DRIFT")
        else:mtl.write_text(material,encoding="utf-8")
        products.append({"file":str(mtl),"sha256":digest(mtl)[1]})
        position=LOCATIONS[family][(counts[family]-1)%len(LOCATIONS[family])]
        selected.append({"id":slug,"category":family,"wave":wave,"files":products,
          "asset":"/Game/Production/World/Shire/VerifiedPBR/"+slug+"/"+slug+"."+slug,
          "material":"/Game/Production/World/Shire/VerifiedPBR/"+slug+"/"+mname+"."+mname,
          "location":position,"target_radius_cm":90})
    require(selected,"NO_ELIGIBLE_PBR_STATIC_ASSETS")
    report={"schema_version":1,"status":"SOURCE_HASH_VERIFIED_NOT_UE_IMPORTED",
            "chapter":"P1C01","license":"CC0","selected":selected,
            "selected_count":len(selected),"payload_bytes":bytes_total,
            "evidence_boundary":"Source QC only. No UE import, LOD, collision, PIE, FPS or visual acceptance."}
    p=project/"Saved/P1C01VerifiedPBR/source_stage_receipt.json"
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("P1C01_PBR_VERIFIED_SOURCE_PASS items="+str(len(selected))+" bytes="+str(bytes_total))
    return report

def activate(project):
    report=read(project/"Saved/P1C01VerifiedPBR/source_stage_receipt.json")
    require(report.get("status")=="SOURCE_HASH_VERIFIED_NOT_UE_IMPORTED","SOURCE_STAGE_NOT_READY")
    for item in report["selected"]:
        base=project/"Content/Production"/OVERLAY/item["id"]
        for asset in (item["id"],"MI_P1C01_"+item["id"]):
            p=base/(asset+".uasset")
            require(p.is_file() and p.stat().st_size>2048,"UE_PACKAGE_MISSING:"+str(p))
    planpath=project/"Data/ChapterAssetStreamingPlan.json"
    plan=read(planpath)
    bank=plan["banks"]["P1C01"]["assets"]
    for item in report["selected"]:
        if item["asset"] not in bank:bank.append(item["asset"])
    planpath.write_text(json.dumps(plan,indent=2)+"\n",encoding="utf-8")
    metadata={"schema_version":1,"status":"UE_PACKAGE_PRESENCE_ONLY",
      "chapter":"P1C01","selected_count":len(report["selected"]),
      "accents":[{k:item[k] for k in ("id","category","asset","location","target_radius_cm")}
                 for item in report["selected"]],
      "evidence_boundary":"uasset presence; gameplay, collision, PIE, visual and device unaccepted."}
    (project/"Data/P1C01VerifiedWorldDecor.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
    print("P1C01_PBR_UE_PACKAGE_PRESENCE_PASS count="+str(metadata["selected_count"]))
    return metadata

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--project-root",type=Path,required=True)
    p.add_argument("--warehouse-root",type=Path)
    p.add_argument("--activate-after-unreal-import",action="store_true")
    args=p.parse_args()
    try:
        if args.activate_after_unreal_import:activate(args.project_root)
        else:
            require(args.warehouse_root is not None,"WAREHOUSE_ROOT_REQUIRED")
            stage(args.warehouse_root,args.project_root)
    except (OSError,ValueError,KeyError,TypeError) as e:
        print("P1C01_PBR_SOURCE_BRIDGE_FAILED "+str(e),file=sys.stderr)
        return 2
    return 0
if __name__=="__main__":raise SystemExit(main())
