#!/usr/bin/env python3
"""Source-only verified Poly Haven FBX/PBR intake for P1C01, without provider downloads."""
import argparse, hashlib, json, pathlib, re, shutil, struct, sys

SOURCES=(("p1c01_wave39",39,39),("p1c01_wave60",60,59))
FAMILY=("barrel","basket","bench","bucket","crate","hay","wood","rock","stone","log","stump","garden","flower","pot","fence","plank")
MAX_SELECTED=18
MAX_BYTES=160*1024*1024
ROOT=pathlib.Path(__file__).resolve().parents[1]
class IntakeError(ValueError): pass

def need(ok,reason):
    if not ok: raise IntakeError(reason)

def digest(p):
    need(p.is_file() and not p.is_symlink(),"FILE_MISSING:"+str(p))
    h=hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()

def obj(p):
    need(p.is_file() and not p.is_symlink(),"RECEIPT_MISSING:"+str(p))
    x=json.loads(p.read_text(encoding="utf-8-sig"))
    need(isinstance(x,dict),"BAD_RECEIPT")
    return x

def inspect(warehouse,wave,expected,prepared):
    root=warehouse/"_p1c01_adaptive_polyhaven"/wave
    need(root.is_dir() and not root.is_symlink(),"WAVE_NOT_STAGED:"+wave)
    receipt=obj(root/"receipt_adaptive_pbr.json")
    need(receipt.get("stage")=="PERSISTENT_WAREHOUSE_SOURCE_ONLY" and
         receipt.get("wave")==wave and receipt.get("original_source_count")==expected and
         receipt.get("converted_fbx_count")==prepared and receipt.get("license")=="CC0" and
         receipt.get("provider")=="POLY_HAVEN","WAVE_QC_FAILED:"+wave)
    need(digest(root/"source_receipt_original.json")==receipt.get("source_receipt_sha256")
         and digest(root/"pbr_receipt_original.json")==receipt.get("pbr_receipt_sha256"),
         "ORIGINAL_RECEIPT_CHANGED:"+wave)
    pbr=obj(root/"pbr_receipt_original.json")
    rows={}
    for row in receipt.get("files",[]):
        path=pathlib.Path(str(row.get("file","")))
        need(path.is_absolute() and root.resolve() in path.resolve().parents and
             not path.is_symlink(),"UNSAFE_SOURCE_FILE")
        key=path.relative_to(root).as_posix()
        need(key not in rows and row.get("provider")=="POLY_HAVEN" and row.get("license")=="CC0",
             "DUPLICATE_OR_UNLICENSED_FILE")
        rows[key]=row
    selected=[]
    for a in pbr.get("assets",[]):
        slug=a.get("id","")
        if not isinstance(slug,str) or not re.fullmatch(r"[a-z0-9_]{3,80}",slug):
            continue
        if a.get("status")!="STATIC_SOURCE_QC_ONLY" or not any(k in slug for k in FAMILY):
            continue
        prefix="assets/"+slug+"/prepared/"
        key=prefix+slug+".fbx"
        fbx=rows.get(key)
        if not fbx or fbx.get("state")!="SOURCE_PBR_PENDING_STATIC_GEOMETRY_LOD_COLLISION_QC":
            continue
        if fbx.get("bytes",0)>18*1024*1024: continue
        maps={}
        for m in a.get("maps",[]):
            role=m.get("role")
            if role not in ("BaseColor","NormalDX","ORM") or m.get("resolution")!=[1024,1024]:
                continue
            tpath=m.get("path","")
            texkey=prefix+pathlib.Path(tpath).name
            entry=rows.get(texkey)
            if entry and entry.get("state")=="SOURCE_PBR_PENDING_STATIC_GEOMETRY_LOD_COLLISION_QC":
                maps.setdefault(role,[]).append((texkey,entry))
        if not all(len(maps.get(k,[]))==1 for k in ("BaseColor","NormalDX","ORM")):
            continue
        if len(a.get("maps",[]))!=3: continue # complex/multi-material or opacity deferred
        selected.append((slug,wave,root,[(key,fbx)]+[maps[k][0] for k in ("BaseColor","NormalDX","ORM")]))
    return selected

def stage(warehouse,project):
    found=[]
    for w,source,prepared in SOURCES:
        found.extend(inspect(warehouse,w,source,prepared))
    found.sort(key=lambda x:x[0])
    chosen=[];total=0;seen=set()
    for slug,w,root,files in found:
        need(slug not in seen,"DUPLICATE_ASSET_ACROSS_WAVES:"+slug)
        seen.add(slug)
        size=sum(row["bytes"] for _,row in files)
        if len(chosen)>=MAX_SELECTED or total+size>MAX_BYTES: continue
        chosen.append((slug,w,root,files));total+=size
    need(chosen,"NO_PBR_SOURCE_ELIGIBLE_FOR_SINGLE_MATERIAL_IMPORT")
    results=[]
    overlay=project/"SourceAssets/Production/World/Shire/VerifiedPBR"
    for slug,w,root,files in chosen:
        dest=overlay/slug
        dest.mkdir(parents=True,exist_ok=True)
        copied=[]
        for key,row in files:
            source=root/key
            want=str(row.get("sha256",""))
            need(re.fullmatch(r"[a-f0-9]{64}",want) is not None and
                 source.stat().st_size==row.get("bytes") and digest(source)==want,
                 "PBR_SOURCE_HASH_FAIL:"+slug+":"+key)
            with source.open("rb") as f: header=f.read(32)
            if source.suffix==".fbx":
                need(header.startswith(b"Kaydara FBX Binary"),"NOT_BINARY_FBX:"+slug)
            else:
                need(header[:8]==bytes.fromhex("89504e470d0a1a0a") and
                     struct.unpack(">II",header[16:24])==(1024,1024),
                     "INVALID_1K_PNG:"+slug)
            target=dest/source.name
            if target.exists():
                need(digest(target)==want,"OUTPUT_ALREADY_EXISTS_WRONG_SHA:"+slug)
            else:
                tmp=dest/(source.name+".part")
                need(not tmp.exists(),"INCOMPLETE_PREVIOUS_COPY:"+slug)
                try:
                    shutil.copyfile(source,tmp)
                    need(digest(tmp)==want,"COPY_HASH_FAIL:"+slug)
                    tmp.replace(target)
                finally:
                    if tmp.exists():tmp.unlink()
            copied.append({"name":target.name,"bytes":row["bytes"],"sha256":want})
        # Use the established UE4 material-synthesis importer. The new FBX slot
        # binding below is limited to one verified material per static mesh.
        material_name="MI_P1C01_"+slug
        mtl=dest/(slug+".mtl")
        albedo=next(f["name"] for f in copied if f["name"].endswith("_BaseColor.png"))
        mtl_text=("newmtl "+material_name+"\\nKd 1 1 1\\nPr 0.68\\n"
                  "Pm 0\\nKs 0.1 0.1 0.1\\nmap_Kd "+albedo+"\\n")
        if mtl.exists():
            need(mtl.read_text(encoding="utf-8")==mtl_text,
                 "MATERIAL_SIDECAR_DRIFT:"+slug)
        else:
            mtl.write_text(mtl_text,encoding="utf-8")
        copied.append({"name":mtl.name,"bytes":mtl.stat().st_size,
                       "sha256":digest(mtl),"role":"MTL_ALBEDO_BINDING"})
        results.append({"id":slug,"wave":w,"files":copied,
                        "asset":"/Game/Production/World/Shire/VerifiedPBR/"+slug+"/"+slug+"."+slug,
                        "qc":"SOURCE_SHA256_PASSED_UE_GEOMETRY_LOD_COLLISION_AND_VISUAL_PENDING"})
    out=project/"Saved/P1C01VerifiedPBR"
    out.mkdir(parents=True,exist_ok=True)
    receipt={"schema_version":1,"chapter":"P1C01","source":"POLY_HAVEN_CC0",
             "state":"SOURCE_VERIFIED_ONLY","filesets":results,"selected":len(results),
             "selected_bytes":total,"not_imported":True,
             "gate67_accepted":False}
    (out/"intake_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print("P1C01_PBR_SOURCE_IMPORT_READY selected="+str(len(results))+
          " bytes="+str(total)+" UE_IMPORTED=false")
    return receipt

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--warehouse-root",type=pathlib.Path,required=True)
    ap.add_argument("--project-root",type=pathlib.Path,default=ROOT)
    args=ap.parse_args()
    try:stage(args.warehouse_root,args.project_root)
    except (IntakeError,OSError,ValueError,KeyError) as e:
        print("P1C01_PBR_SOURCE_IMPORT_FAILED:"+str(e),file=sys.stderr)
        return 2
    return 0

if __name__=="__main__":sys.exit(main())
