#!/usr/bin/env python3
"""Fail-closed evaluator for P1C01 Gate 6/7 evidence.

This tool does not run Unreal or invent observations. It validates a captured
evidence JSON against the declared target profile and writes an evaluation JSON.
"""
import argparse
import json
from pathlib import Path

TARGET = {
    "renderer": "DX11",
    "width": 1280,
    "height": 720,
    "quality": "Balanced Medium / selective High where visually important",
    "fps_floor": 30.0,
    "cpu": "Intel Core i7-6498DU",
    "gpu": "AMD Radeon R5 M330",
    "vram_mb": 2039,
    "os": "Windows 11 Pro",
}
ROUTES = [
    "Bag End interior traversal",
    "Bag End exterior transition",
    "Hobbiton lane traversal",
    "dense vegetation view",
    "active NPC/fauna area",
    "canon-beat return-to-control state",
    "save/load resumed traversal",
]

def fail(reason):
    return {"status":"FAIL","accepted":False,"reason":reason}

def evaluate(payload):
    head=str(payload.get("exact_head","")).strip()
    hardware=payload.get("hardware",{})
    profile=payload.get("profile",{})
    routes=payload.get("routes",[])
    human=payload.get("human_review",{})

    if not head or len(head) < 7:
        return fail("missing exact_head")
    if not str(hardware.get("cpu","")).strip() or not hardware.get("ram_gb") or not hardware.get("vram_gb_class") or not str(hardware.get("gpu","")).strip() or not str(hardware.get("os","")).strip() or hardware.get("vram_mb") is None:
        return {"status":"INCOMPLETE","accepted":False,"reason":"missing hardware identity"}
    cpu = " ".join(str(hardware["cpu"]).lower().split())
    gpu = " ".join(str(hardware["gpu"]).lower().split())
    os_name = " ".join(str(hardware["os"]).lower().split())
    if (TARGET["cpu"].lower() not in cpu or TARGET["gpu"].lower() not in gpu or
            TARGET["os"].lower() not in os_name or
            "64-bit" not in os_name or int(hardware["ram_gb"]) != 8 or
            int(hardware["vram_gb_class"]) != 2 or int(hardware["vram_mb"]) != TARGET["vram_mb"]):
        return fail("hardware does not match owner target device")
    if hardware.get("directx_ultimate_supported") is True:
        return fail("inconsistent reported DirectX Ultimate hardware contract")
    # OS-installed DX12 is not the Unreal DX11 renderer; the actual RHI is checked in profile.
    if not str(payload.get("device_runtime_evidence","")).strip() or not str(payload.get("executable_identity","")).strip():
        return {"status":"INCOMPLETE","accepted":False,"reason":"missing physical gameplay execution evidence"}
    if profile.get("renderer") != TARGET["renderer"] or profile.get("width") != TARGET["width"] or profile.get("height") != TARGET["height"] or profile.get("quality") != TARGET["quality"]:
        return fail("wrong target profile")

    by_name={str(r.get("name","")):r for r in routes}
    missing=[name for name in ROUTES if name not in by_name]
    if missing:
        return {"status":"INCOMPLETE","accepted":False,"reason":"missing route measurements","missing_routes":missing}

    for name in ROUTES:
        row=by_name[name]
        minimum=row.get("min_fps")
        average=row.get("avg_fps")
        if minimum is None or average is None:
            return {"status":"INCOMPLETE","accepted":False,"reason":f"missing fps measurement: {name}"}
        if row.get("p95_frame_ms") is None or row.get("p99_frame_ms") is None or row.get("resident_ram_mb") is None or row.get("texture_or_vram_mb") is None:
            return {"status":"INCOMPLETE","accepted":False,"reason":f"missing frame-time or memory measurement: {name}"}
        if float(minimum) < TARGET["fps_floor"]:
            return fail(f"route below 30 FPS floor: {name}")
        if row.get("blocking_streaming_hitch") is True:
            return fail(f"blocking streaming hitch: {name}")
        if row.get("synchronous_heavy_load_observed") is True:
            return fail(f"synchronous heavy load observed: {name}")

    if payload.get("save_load_continuity") is not True:
        return fail("save/load continuity not proven")
    if payload.get("return_to_control_continuity") is not True:
        return fail("return-to-control continuity not proven")

    required_human=("visual_readability","world_life_believability","quest_cinematic_audio_pacing")
    missing_human=[k for k in required_human if human.get(k) is not True]
    if missing_human:
        return {"status":"GATE67_NOT_ACCEPTED","accepted":False,"reason":"human review incomplete","missing_human":missing_human}

    return {
        "status":"MEASUREMENTS_MEET_DECLARED_GATE",
        "accepted":True,
        "exact_head":head,
        "labels":{
            "DEVICE_TESTED":True,
            "PERFORMANCE_ACCEPTED":True,
            "VISUALLY_ACCEPTED":True,
            "PACING_ACCEPTED":True,
        }
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--evidence",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    payload=json.loads(args.evidence.read_text(encoding="utf-8"))
    result=evaluate(payload)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,sort_keys=True))
    return 0 if result.get("accepted") else 2

if __name__ == "__main__":
    raise SystemExit(main())
