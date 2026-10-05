#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(r): return json.loads((ROOT/r).read_text(encoding="utf-8"))
def main():
    errors=[]
    bundles=load("Data/P1C01CharacterBundleCompletionV1.json")
    micro=load("Data/P1C01WorldMicroDetailCompletionV1.json")
    audio=load("Data/P1C01AudioMasterSlotMapV1.json")
    mission=load("Data/P1C01MissionRuntimeAcceptanceMatrixV1.json")
    required={"FRODO","BILBO","GANDALF","SAM","MERRY","PIPPIN","BLACK_RIDER","BLACK_RIDER_HORSE"}
    if {x["id"] for x in bundles["required_characters"]}!=required: errors.append("cast")
    if len(micro["regions"])<8: errors.append("world")
    if len(audio["required_families"])<13: errors.append("audio")
    if [x["id"] for x in mission["missions"]]!=["F1-01","F1-02","F1-03"]: errors.append("missions")
    print("P1C01_OFFLINE_SATURATION_"+("FAIL" if errors else "PASS"), "errors="+str(len(errors)))
    if errors: raise SystemExit(1)
if __name__=="__main__": main()
