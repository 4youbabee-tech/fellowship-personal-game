#!/usr/bin/env python3
"""Validate P1C01 living-world binding batch01 off-runner packet."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "Data" / "P1C01LivingWorldBindingBatch01.json"
def require(condition: bool, message: str) -> None:
    if not condition: raise AssertionError(message)
def digest_record(record: dict) -> str:
    clean=dict(record); clean.pop("record_sha256", None)
    return hashlib.sha256(json.dumps(clean, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
def main() -> int:
    packet=json.loads(PACKET.read_text(encoding="utf-8")); records=packet["records"]
    require(packet["runner_policy"]=="Windows Runner not used or required for this batch","runner policy mismatch")
    require(len(records)==39,"expected 39 binding records")
    require(packet["counts"]["binding_records"]==len(records),"binding count mismatch")
    zones={r["target_zone"] for r in records}; bands={r["time_band"] for r in records}; roles={r["npc_role_candidate"]["role"] for r in records}
    require(len(zones)==13,"expected 13 zones"); require(bands=={"morning","midday","evening"},"time band coverage mismatch"); require(len(roles)>=7,"expected broad NPC role coverage")
    seen=set()
    for r in records:
        bid=r["binding_id"]; require(bid not in seen, f"duplicate binding id: {bid}"); seen.add(bid)
        require(r["record_sha256"]==digest_record(r), f"record hash mismatch: {bid}")
        require(r["chapter"]=="P1C01", f"chapter mismatch: {bid}")
        require(r["density_budget_units"]<=18, f"density budget too high: {bid}")
        require(len(r["material_candidates"])>=2, f"missing material candidates: {bid}")
        require(len(r["audio_candidates"])>=2, f"missing audio candidates: {bid}")
        npc=r["npc_role_candidate"]; require(npc["requires_real_character_mesh"] is True, f"real character requirement missing: {bid}"); require(npc["placeholder_mesh_allowed"] is False, f"placeholder mesh incorrectly allowed: {bid}")
        perf=r["performance_contract"]; require(perf["use_hism_or_ism_for_repeated_props"] is True, f"missing HISM/ISM contract: {bid}"); require(perf["soft_reference_required"] is True, f"missing soft reference contract: {bid}")
        status=r["implementation_status"]
        for key in ("warehouse_persisted","unreal_imported","world_placed","pie_tested","device_tested","visually_accepted"):
            require(status[key]=="PENDING", f"{key} must remain pending: {bid}")
    require("no Warehouse persistence" in packet["evidence_boundary"],"missing evidence boundary")
    print(f"P1C01_LIVING_WORLD_BINDING_BATCH01_STATIC_PASS records={len(records)} zones={len(zones)} roles={len(roles)}")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
