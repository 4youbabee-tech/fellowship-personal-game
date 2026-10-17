"""Verify exact original whole-game physical source pack, stage to UE4.27, then attest persisted .uassets."""
import argparse, hashlib, json, re, shutil, zipfile
from pathlib import Path

SHA_PIN = 11767251532
REGION_DEST = {"BREE":"Bree","WEATHERTOP":"Weathertop","RIVENDELL":"Rivendell","MORIA":"Moria","CARADHRAS":"Road","LOTHLORIEN":"Lothlorien","ANDUIN_AMON_HEN":"Anduin","ISENGARD_ORTHANC":"Isengard","EDORAS_MEDUSELD":"Edoras","HELMS_DEEP":"HelmsDeep","MINAS_TIRITH":"MinasTirith","OSGILIATH":"Osgiliath","PELENNOR_FIELDS":"PelennorFields","FANGORN":"Fangorn","BAG_END":"Shire","SHIRE_HOBBITON":"Shire"}
def sha(data): return hashlib.sha256(data).hexdigest()
def filename(src):
    m=re.fullmatch(r"regional_meshes/SM_Region_([A-Z_]+)_Support_LOD[01]\.fbx",src)
    if m:
        folder=REGION_DEST.get(m.group(1),"Regions/"+m.group(1))
        return "World/"+folder+"/RegionalSupport/"+src.rsplit("/",1)[-1], "StaticMesh"
    m=re.fullmatch(r"materials/([a-z0-9_]+)/([A-Za-z0-9_]+\.png)",src)
    if m:
        return "World/RegionalSupport/Materials/"+m.group(1)+"/"+m.group(2),"Texture2D"
    raise ValueError("REGIONAL_UNSAFE_SOURCE:"+src)
def stage(project,artifact,pin):
    index=json.loads((artifact/"index.json").read_text(encoding="utf-8"))
    selected=[p for p in index["packs"] if p["pack"]=="WHOLEGAME_28_SUPPORT"]
    if len(selected)!=1 or index["source_artifact_id"]!=pin["artifact_id"] or index["regions"]!=28 or index["physical_support_fbx"]!=56 or index["physical_pbr_png"]!=36: raise ValueError("REGIONAL_INDEX_INVALID")
    archive=artifact/selected[0]["zip"]
    if sha(archive.read_bytes())!=selected[0]["sha256"]: raise ValueError("REGIONAL_ARCHIVE_SHA_FAILED")
    result=[]
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None: raise ValueError("REGIONAL_ARCHIVE_BAD_ZIP")
        receipt=json.loads(z.read("preproduction_receipt.json"))
        if receipt["stage"]!="SOURCE_QC_ONLY_NOT_UE_IMPORTED" or receipt["source_artifact_id"]!=SHA_PIN or receipt["source_commit"]!=pin["source_commit"] or receipt["source_zip_sha256"]!=pin["source_zip_sha256"] or receipt["fbx"]!=56 or receipt["png"]!=36: raise ValueError("REGIONAL_RECEIPT_INVALID")
        roster=receipt["files"]
        if len(roster)!=92 or len({x["path"] for x in roster})!=92 or set(z.namelist())!={x["path"] for x in roster}|{"preproduction_receipt.json"}: raise ValueError("REGIONAL_ROSTER_INVALID")
        for row in roster:
            data=z.read(row["path"])
            if len(data)!=row["bytes"] or sha(data)!=row["sha256"]: raise ValueError("REGIONAL_FILE_SHA_FAILED:"+row["path"])
            dest,kind=filename(row["path"])
            if kind=="StaticMesh" and not data.startswith(b"Kaydara FBX Binary"): raise ValueError("REGIONAL_FBX_HEADER")
            if kind=="Texture2D" and not data.startswith(bytes.fromhex("89504e470d0a1a0a")): raise ValueError("REGIONAL_PNG_HEADER")
            target=project/"SourceAssets"/"Production"/dest
            target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists() and sha(target.read_bytes())!=row["sha256"]: raise ValueError("REGIONAL_EXISTING_SOURCE_CHANGED:"+str(target))
            if not target.exists(): target.write_bytes(data)
            rel=Path(dest).with_suffix(".uasset")
            obj="/Game/Production/"+rel.with_suffix("").as_posix()+"."+rel.stem
            result.append({"path":rel.as_posix(),"object":obj,"class":kind})
    saved=project/"Saved"/"RegionalSupportIntake.json";saved.parent.mkdir(parents=True,exist_ok=True)
    saved.write_text(json.dumps({"artifact":SHA_PIN,"source_commit":pin["source_commit"],"files":result},indent=2),encoding="utf-8")
    print("PES002_REGIONAL_SOURCE_STAGED regions=28 fbx=56 png=36 userFacingQuality=SUPPORT_ONLY",flush=True)
def persist(project,warehouse):
    receipt=json.loads((project/"Saved"/"RegionalSupportIntake.json").read_text(encoding="utf-8"))
    if receipt["artifact"]!=SHA_PIN or len(receipt["files"])!=92: raise ValueError("REGIONAL_STAGE_MISSING")
    log=(project/"Saved"/"PES002VisualProof"/"PES002ProductionImport.log").read_text(encoding="utf-8",errors="replace")
    bank=warehouse/"RegionalSupport"/receipt["source_commit"]
    items=[]
    for r in receipt["files"]:
        needle="PES002_REGIONAL_SUPPORT_IMPORT path=%s class=%s validated=1"%(r["object"],r["class"])
        if needle not in log: raise ValueError("REGIONAL_CLASS_NOT_VERIFIED:"+r["object"])
        path=project/"Content"/"Production"/r["path"]
        if not path.is_file() or path.stat().st_size<512: raise ValueError("REGIONAL_UASSET_MISSING:"+str(path))
        output=bank/r["path"];output.parent.mkdir(parents=True,exist_ok=True)
        if not output.exists() or sha(output.read_bytes())!=sha(path.read_bytes()): shutil.copyfile(path,output)
        if sha(output.read_bytes())!=sha(path.read_bytes()): raise ValueError("REGIONAL_PERSIST_HASH_FAILED")
        items.append({"path":r["path"],"class":r["class"],"sha256":sha(path.read_bytes()),"bytes":path.stat().st_size})
    summary={"status":"UE_IMPORTED_WAREHOUSE_PERSISTED_NOT_WORLD_PLACED","source_commit":receipt["source_commit"],"artifact":SHA_PIN,"classes":{"StaticMesh":sum(x["class"]=="StaticMesh" for x in items),"Texture2D":sum(x["class"]=="Texture2D" for x in items)},"files":items,"visualAccepted":False,"runtimeEnabled":False}
    (bank/"UE_import_receipt.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print("PES002_REGIONAL_UE_IMPORT_PHYSICAL_PASS staticMeshes=%d textures=%d worldPlaced=0 runtimeChapterOpened=0"%(summary["classes"]["StaticMesh"],summary["classes"]["Texture2D"]),flush=True)
def main():
    p=argparse.ArgumentParser();p.add_argument("--mode",required=True,choices=["stage","persist"]);p.add_argument("--project",type=Path,required=True);p.add_argument("--artifact",type=Path);p.add_argument("--pin",type=Path);p.add_argument("--warehouse",type=Path)
    a=p.parse_args()
    try:
        if a.mode=="stage":
            if not a.artifact or not a.pin: raise ValueError("REGIONAL_ARGUMENTS_MISSING")
            stage(a.project,a.artifact,json.loads(a.pin.read_text(encoding="utf-8")))
        else:
            if not a.warehouse: raise ValueError("REGIONAL_WAREHOUSE_MISSING")
            persist(a.project,a.warehouse)
    except (OSError,ValueError,KeyError,zipfile.BadZipFile) as e:
        print("PES002_REGIONAL_INTAKE_FAIL "+str(e),flush=True);return 86
    return 0
if __name__=="__main__":raise SystemExit(main())
