#!/usr/bin/env python3
"""Generate a P1C01 living-world binding packet for off-runner production handoff."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Data" / "P1C01LivingWorldBindingBatch01.json"
ZONES = [
 ("Bag End Interior","quiet_home",7,["M_P1C01_BagEnd_HearthStone_PBR","M_P1C01_BagEnd_HoneyWood_PBR"],["S_P1C01_BagEnd_RoomTone_A","S_P1C01_BagEnd_Hearth_A"]),
 ("Bag End","home_threshold",9,["M_P1C01_BagEnd_GreenDoor_PBR","M_P1C01_BagEnd_RoundBrick_PBR"],["S_P1C01_BagEnd_RoundDoor_Creak_A","S_P1C01_BagEnd_GardenBreeze_A"]),
 ("Bag End Garden","domestic_garden",13,["M_P1C01_Garden_LeafyGround_PBR","M_P1C01_Garden_DarkSoil_PBR"],["S_P1C01_BagEnd_ToolTap_A","S_P1C01_Footstep_GrassSoft_A"]),
 ("Bagshot Row","settlement_row",10,["M_P1C01_Bagshot_RowFence_PBR","M_P1C01_Hobbiton_Whitewash_PBR"],["S_P1C01_Hobbiton_FenceLatch_A","S_P1C01_Hobbiton_ClothLine_A"]),
 ("Hobbiton","village_lane",16,["M_P1C01_Hobbiton_ThatchDry_PBR","M_P1C01_Hobbiton_Whitewash_PBR"],["S_P1C01_Hobbiton_LaneMurmur_A","S_P1C01_Hobbiton_Broom_A"]),
 ("Party Field","festival_setup",18,["M_P1C01_PartyField_TentCanvas_PBR","M_P1C01_PartyField_RibbonCloth_PBR","M_P1C01_PartyField_ServiceCeramic_PBR"],["S_P1C01_PartyField_CrowdSoft_A","S_P1C01_PartyField_CupClink_A","S_P1C01_PartyField_RibbonFlap_A"]),
 ("Hobbiton Road","travel_path",12,["M_P1C01_Road_CompactedDirt_PBR","M_P1C01_Road_PebbleScatter_PBR"],["S_P1C01_Footstep_DirtRoad_A","S_P1C01_Bywater_WaystoneTap_A"]),
 ("Bywater Road","crossroad",11,["M_P1C01_Road_CompactedDirt_PBR","M_P1C01_Road_PebbleScatter_PBR"],["S_P1C01_Footstep_DirtRoad_B","S_P1C01_Bywater_WaystoneTap_A"]),
 ("Wooded Road","sheltered_path",14,["M_P1C01_WoodedRoad_MossBark_PBR","M_P1C01_WoodedRoad_RootWet_PBR"],["S_P1C01_WoodedRoad_Leaves_A","S_P1C01_WoodedRoad_BranchSnap_A"]),
 ("Mill Pond","water_work",13,["M_P1C01_MillPond_WetPlank_PBR","M_P1C01_MillPond_StoneEdge_PBR"],["S_P1C01_MillPond_WaterLap_A","S_P1C01_MillPond_WheelCreak_A"]),
 ("Bucklebury Ferry","river_crossing",12,["M_P1C01_Ferry_DockPlank_PBR","M_P1C01_Ferry_RopeFiber_PBR"],["S_P1C01_Ferry_RiverLap_A","S_P1C01_Ferry_RopeCoil_A","S_P1C01_Ferry_DockPlank_A"]),
 ("East Fields","working_field",13,["M_P1C01_EastFields_WheatStalk_PBR","M_P1C01_EastFields_TurnipLeaf_PBR"],["S_P1C01_EastFields_Wind_A","S_P1C01_EastFields_CrateShuffle_A"]),
 ("Hobbiton Market","market_day",15,["M_P1C01_Market_AwningBlue_PBR","M_P1C01_Market_WickerBasket_PBR"],["S_P1C01_Hobbiton_LaneMurmur_A","S_P1C01_PartyField_CupClink_A"]),
]
NPC_ROLES=[("gardener","tend rows","idle_tend_garden"),("baker","carry basket","idle_chat_trade"),("miller","inspect sacks","idle_work_mill"),("ferry_keeper","check rope","idle_watch_river"),("market_vendor","arrange stall","idle_trade_counter"),("walker","slow walk loop","walk_social_slow"),("child","safe play loop","idle_play_near_adult"),("elder","bench conversation","idle_bench_talk")]
PROP_PREFIXES=["SM_B02_WindowBox","SM_B02_Gate","SM_B02_Rut","SM_B02_ReedCluster","SM_B03_PantryJarCluster","SM_B03_RibbonStake","SM_B03_RopeCoil","SM_B03_Waystone","SM_B03_StumpCluster","SM_B03_TurnipCrate"]

def digest_record(record: dict) -> str:
    return hashlib.sha256(json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()

def main() -> int:
    records=[]; idx=1
    for zi,(zone,mood,density,materials,sounds) in enumerate(ZONES):
        for band in ("morning","midday","evening"):
            role=NPC_ROLES[(zi+len(band))%len(NPC_ROLES)]
            rec={"binding_id":f"P1C01_LWB01_{idx:03d}","target_zone":zone,"chapter":"P1C01","time_band":band,"ambient_mood":mood,"density_budget_units":density,"material_candidates":materials,"audio_candidates":sounds,"prop_family_candidate":PROP_PREFIXES[(zi+idx)%len(PROP_PREFIXES)],"npc_role_candidate":{"role":role[0],"activity_label":role[1],"animation_intent":role[2],"requires_real_character_mesh":True,"placeholder_mesh_allowed":False},"performance_contract":{"use_hism_or_ism_for_repeated_props":True,"soft_reference_required":True,"streaming_priority":"P1C01_player_route","max_tick_dependency":"none_for_static_props","target_device_note":"i7 gen6, 8GB RAM, approx 2GB VRAM, DX11, 720p/30FPS requires later device proof"},"implementation_status":{"source_assets_available":"PARTIAL_FROM_BATCH02_BATCH03_AUDIO01_MATERIAL01","warehouse_persisted":"PENDING","unreal_imported":"PENDING","world_placed":"PENDING","pie_tested":"PENDING","device_tested":"PENDING","visually_accepted":"PENDING"}}
            rec["record_sha256"]=digest_record(rec)
            records.append(rec); idx += 1
    packet={"schema_version":1,"batch_id":"P1C01_LIVING_WORLD_BINDING_BATCH01_OFFRUNNER","created_utc":"2026-10-13T09:25:00Z","purpose":"Off-runner binding packet that maps verified source asset families, PBR material candidates, source audio cues and NPC activity intents into P1C01 player-route zones for later Unreal import and placement.","runner_policy":"Windows Runner not used or required for this batch","counts":{"binding_records":len(records),"zones":len({r["target_zone"] for r in records}),"time_bands":len({r["time_band"] for r in records}),"npc_roles":len({r["npc_role_candidate"]["role"] for r in records})},"records":records,"evidence_boundary":"SOURCE_BINDING_PACKET_CREATED and STATIC_QC_PASSED only after hosted validator passes; no Warehouse persistence, Unreal import, world placement, PIE, device, visual/audio acceptance, FPS or Gate 6/7 claim."}
    OUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(f"P1C01_LIVING_WORLD_BINDING_BATCH01_GENERATED records={len(records)} zones={packet['counts']['zones']}")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
