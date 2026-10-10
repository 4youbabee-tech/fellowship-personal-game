#!/usr/bin/env python3
"""Fail-closed UE4 package verification for staged P1C01 Poly Haven meshes."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--project-root",type=Path,required=True)
    ap.add_argument("--import-log",type=Path,required=True)
    x=ap.parse_args()
    receipt=x.project_root/"Saved/P1C01VerifiedPBR/stage_receipt.json"
    if not receipt.is_file() or not x.import_log.is_file():
        print("P1C01_PBR_IMPORT_MISSING_EVIDENCE",file=sys.stderr);return 2
    data=json.loads(receipt.read_text(encoding="utf-8-sig"))
    rows=data.get("assets",[])
    if data.get("stage")!="HASH_VERIFIED_SOURCE_ONLY" or not rows:
        print("P1C01_PBR_IMPORT_BAD_SOURCE_RECEIPT",file=sys.stderr);return 2
    log=x.import_log.read_text(encoding="utf-8-sig",errors="replace")
    verified=[];unbound=[];missing=[]
    for row in rows:
        slug=row["id"]
        folder=x.project_root/"Content/Production/World/Shire/VerifiedPBR"/slug
        mesh=folder/(slug+".uasset")
        mat=folder/("MI_P1C01_"+slug+".uasset")
        if not mesh.is_file() or mesh.stat().st_size<2048 or not mat.is_file() or mat.stat().st_size<2048:
            missing.append(slug);continue
        if "P1C01_VERIFIED_PBR_IMPORT_BIND_PASS mesh="+slug+" " in log:
            verified.append(slug)
        else:
            unbound.append(slug)
    result={"schema_version":1,"chapter":"P1C01","status":"UNREAL_IMPORT_QC_PARTIAL",
            "source_count":len(rows),"real_ue_mesh_material_packages":len(verified),
            "bound":verified,"unbound":unbound,"missing":missing,
            "evidence_boundary":"Source+editor import and one-material albedo bindings only; no normal/ORM shader claim, chapter visual, PIE, device or Gate 6/7 acceptance"}
    out=x.project_root/"Saved/P1C01VerifiedPBR/ue_import_receipt.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    if missing or not verified:
        print("P1C01_PBR_IMPORT_FAIL bound="+str(len(verified))+" missing="+str(len(missing))+
              " unbound="+str(len(unbound)),file=sys.stderr)
        return 2
    print("P1C01_PBR_UNREAL_IMPORT_QC_PASS bound="+str(len(verified))+
          " unbound="+str(len(unbound))+" pending_visual=true")
    return 0
if __name__=="__main__":raise SystemExit(main())
