#!/usr/bin/env python3
"""Validate the 1000-task source-preproduction queue without claiming completion."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
queue=json.loads((ROOT/"Data/WholeGame1000TaskExecutionBacklog20261013.json").read_text())
packets=json.loads((ROOT/"Data/WholeGameRegionProductionPacketsV1.json").read_text())["packets"]
regions={p["region_id"] for p in packets}
tasks=queue["tasks"]
assert len(regions)==28 and queue["total_tasks"]==1000 and len(tasks)==1000
assert len({t["id"] for t in tasks})==1000
assert [t["id"] for t in tasks]==["WGP-%04d"%i for i in range(1,1001)]
assert {t["region"] for t in tasks if t["kind"]!="CHAPTER_CLOSURE"}==regions
assert len([t for t in tasks if t["kind"]=="CHAPTER_CLOSURE"])==20
assert all(t["status"]=="QUEUED_UNEXECUTED" and t["qc"] for t in tasks)
assert all(t["gate"]=="SOURCE_PREP_ONLY" for t in tasks if t["region"] not in {"SHIRE_HOBBITON","BAG_END","P1C01_CHAPTER_ROUTE"})
assert queue["no_generated_assets_claim"] is True
print("WHOLEGAME_1000_TASK_STATIC_PASS queued=1000 regions=28 runtime=P1C01_ONLY assets_claimed=0")
