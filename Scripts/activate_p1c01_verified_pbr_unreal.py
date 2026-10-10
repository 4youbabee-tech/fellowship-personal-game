#!/usr/bin/env python3
"""Commit only physically imported static FBX after UE4 commandlet completed."""
import json
from pathlib import Path
import sys

def main(root: Path):
    receipt_path=root/"Saved/P1C01VerifiedPBR/source_stage_receipt.json"
    if not receipt_path.is_file():raise ValueError("SOURCE_STAGE_RECEIPT_MISSING")
    receipt=json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("status")!="HASH_VERIFIED_SOURCE_ONLY":raise ValueError("STAGE_NOT_VERIFIED")
    records=receipt["selected"]
    if not records or len(records)>12:raise ValueError("PBR_COUNT_UNSAFE")
    for row in records:
        slug=row["id"]
        package=root/"Content/Production/World/Shire/VerifiedPBR"/slug
        paths=(package/(slug+".uasset"),package/("MI_P1C01_"+slug+".uasset"),
               package/(row["basecolor_asset"]+".uasset"))
        for path in paths:
            if not path.is_file() or path.stat().st_size<1024:
                raise ValueError("UNREAL_IMPORT_PACKAGE_MISSING:"+str(path))
    path=root/"Data/ChapterAssetStreamingPlan.json"
    plan=json.loads(path.read_text(encoding="utf-8"))
    assets=plan["banks"]["P1C01"]["assets"]
    for row in records:
        if row["asset"] not in assets:assets.append(row["asset"])
    # Exactly the existing async streamable bank preloads these decorative meshes.
    path.write_text(json.dumps(plan,indent=2)+"\\n",encoding="utf-8")
    visual={"schema_version":1,"chapter":"P1C01",
            "status":"IMPORTED_STATIC_UASSETS_PENDING_GEOMETRY_AND_RENDER_REVIEW",
            "accents":[{"asset":r["asset"],"id":r["id"],"location":r["location"],
                        "radius_cm":r["radius_cm"]} for r in records],
            "evidence_boundary":"UE import files exist, not PIE, DEVICE, VISUAL or Gate6/7"}
    (root/"Data/P1C01VerifiedWorldDecor.json").write_text(
        json.dumps(visual,indent=2)+"\\n",encoding="utf-8")
    print("P1C01_PBR_UE_PACKAGE_ACTIVATION_PASS count="+str(len(records))+
          " pendingVisualAndDevice=true")

if __name__=="__main__":
    try:main(Path(sys.argv[1]))
    except (OSError,ValueError,KeyError,IndexError) as exc:
        print("P1C01_PBR_ACTIVATION_FAIL "+str(exc),file=sys.stderr)
        sys.exit(2)
