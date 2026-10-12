#!/usr/bin/env python3
"""Fail-closed checks for 1000-task source/preproduction queue. Does not execute tasks."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/"Data/WholeGame1000TaskExecutionBacklog20261013.json").read_text())
packets=json.loads((ROOT/"Data/WholeGameRegionProductionPacketsV1.json").read_text())["packets"]
regions={p["region_id"] for p in packets}
tasks=data["tasks"]
assert len(regions)==28 and len(tasks)==1000
assert len({t["id"] for t in tasks})==1000
assert [t["id"] for t in tasks]==["WGP-"+str(i).zfill(4) for i in range(1,1001)]
assert sum(t["kind"]=="CHAPTER_CLOSURE" for t in tasks)==20
for t in tasks:
    assert t["work"] and t["qc"] and t["status"]=="QUEUED_UNEXECUTED"
    if t["region"]=="P1C01_CHAPTER_ROUTE":
        assert t["gate"]=="P1C01_RUNTIME_ONLY"
    else:
        assert t["region"] in regions
        assert t["gate"]==("P1C01_ALLOWED_IF_GOVERNOR" if t["region"] in {"SHIRE_HOBBITON","BAG_END"} else "SOURCE_PREP_ONLY")
assert data["status"]=="TASKS_QUEUED_NOT_EXECUTED"
print("WHOLEGAME_1000_BACKLOG_STATIC_PASS tasks=1000 regions=28 closure=20 runtime=P1C01_only")
