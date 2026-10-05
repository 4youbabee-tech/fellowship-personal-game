#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")

def check(condition, code, errors):
    if not condition:
        errors.append(code)

def main():
    errors = []

    bundles = load("Data/P1C01CharacterBundleCompletionV1.json")
    micro = load("Data/P1C01WorldMicroDetailCompletionV1.json")
    audio = load("Data/P1C01AudioMasterSlotMapV1.json")
    mission = load("Data/P1C01MissionRuntimeAcceptanceMatrixV1.json")
    offline = load("Data/P1C01OfflineSaturationPackV1.json")
    intake = load("Data/P1C01OfflineSourceIntakeV1.json")
    side = load("Data/ContextualSideActivityPlan.json")
    discoveries = load("Data/JourneyDiscoveryRewardPlan.json")

    world_cpp = read("Source/ShireJourney/Private/World/ShirePrototypeWorldBuilder.cpp")
    flow_cpp = read("Source/ShireJourney/Private/Subsystems/ShireStoryFlowSubsystem.cpp")
    trigger_cpp = read("Source/ShireJourney/Private/World/ShireQuestTrigger.cpp")

    required = {"FRODO", "BILBO", "GANDALF", "SAM", "MERRY", "PIPPIN", "BLACK_RIDER", "BLACK_RIDER_HORSE"}
    observed = {x["id"] for x in bundles["required_characters"]}
    check(observed == required, "cast_required_set", errors)

    routed = {x["id"] for x in intake["character_source_routing"]["targets"]}
    check(routed == required - {"FRODO"}, "character_gap_routing_set", errors)
    check(all(x["final_fbx_present"] is False for x in intake["character_source_routing"]["targets"]),
          "character_false_completion_guard", errors)
    check(intake["character_source_routing"]["final_animated_format"] == "FBX",
          "character_final_format", errors)

    check(len(micro["regions"]) >= 8, "world_region_completeness", errors)
    expected_world_gaps = {
        "BAG_END_INTERIOR_HERO_SET",
        "WOODED_ROAD_NATURAL_TREE_FOLIAGE",
        "FERRY_CONSTRUCTION_ROPE_LANDING",
        "RIVERBANK_REEDS_WATER_EDGE",
        "LIGHTING_SKY_WATER_PRESENTATION",
    }
    check({x["id"] for x in intake["world_hero_source_gaps"]["gaps"]} == expected_world_gaps,
          "world_hero_gap_routing", errors)

    check(len(audio["required_families"]) >= 13, "audio_family_coverage", errors)
    check(intake["audio_master_intake"]["tracked_production_audio_master_files_at_snapshot"] == 0,
          "audio_master_snapshot_truth", errors)
    check(intake["audio_master_intake"]["production_master_format"]["container"] == "WAV",
          "audio_master_format", errors)

    check([x["id"] for x in mission["missions"]] == ["F1-01", "F1-02", "F1-03"],
          "mission_source_set", errors)
    check(mission["runtime_sequence"] == [
        "ShireArrival", "LongExpectedParty", "RingSecret", "LeavingHome",
        "Shortcut", "KeepOffRoad", "FerryEscape"
    ], "mission_runtime_sequence", errors)

    terminal = mission.get("p1c01_terminal_contract", {})
    check(terminal.get("quest_id") == "FerryEscape" and terminal.get("terminal_stage") == 2,
          "ferry_terminal_contract", errors)
    check(terminal.get("auto_start_p1c02") is False, "p1c02_owner_lock_manifest", errors)
    check(terminal.get("checkpoint_id") == "WC_P1C01_FERRY_END",
          "ferry_terminal_checkpoint_manifest", errors)

    check('FerryFarSide->NextChapterId=TEXT("P1C02")' not in world_cpp,
          "p1c02_world_auto_open", errors)
    check('FerryFarSide->StoryBeatId=TEXT("FerryEscapeComplete")' in world_cpp,
          "ferry_completion_beat_source", errors)
    check('StartChapter(TEXT("P1C02"), TEXT("RoadToBree"), 0);' not in flow_cpp,
          "p1c02_restore_auto_open", errors)
    check('{ TEXT("FerryEscapeComplete"), TEXT("WC_P1C01_FERRY_END") }' in trigger_cpp,
          "ferry_checkpoint_binding_source", errors)

    shire_side = []
    for chapter in side.get("chapters", []):
        if chapter.get("route") == "FrodoMain" and chapter.get("chapter") == "P1C01":
            shire_side.extend(chapter.get("activities", []))
    check(len(shire_side) >= 5, "shire_side_activity_baseline", errors)

    shire_rewards = [
        x for x in discoveries.get("discovery_rewards", [])
        if x.get("route") == "FrodoMain" and x.get("chapter") == "P1C01"
    ]
    check(len(shire_rewards) >= 6, "shire_discovery_baseline", errors)

    gap_ids = {x["id"] for x in intake["gameplay_coverage_audit"]["findings"]}
    check({"F1_02_INVESTIGATION_TUTORIAL", "F1_02_PACKING", "F1_03_ENVIRONMENTAL_HIDING",
           "SAVE_CHECKPOINT_COVERAGE", "RETRY_SKIP_BACKTRACK"}.issubset(gap_ids),
          "gameplay_gap_accounting", errors)

    artifacts = set(offline.get("offline_artifacts", []))
    check("Data/P1C01OfflineSourceIntakeV1.json" in artifacts, "offline_pack_intake_ref", errors)

    check("P1C02 Bree runtime" in intake["scope"]["excludes"], "bree_explicitly_excluded", errors)

    if errors:
        for error in errors:
            print("P1C01_OFFLINE_SATURATION_ERROR", error)
        print("P1C01_OFFLINE_SATURATION_FAIL", "errors=" + str(len(errors)))
        raise SystemExit(1)

    print(
        "P1C01_OFFLINE_SATURATION_PASS",
        "errors=0",
        "cast=" + str(len(required)),
        "remaining_character_routes=" + str(len(routed)),
        "world_regions=" + str(len(micro["regions"])),
        "audio_families=" + str(len(audio["required_families"])),
        "shire_side_activities=" + str(len(shire_side)),
        "shire_discovery_rewards=" + str(len(shire_rewards)),
        "p1c02_auto_open=blocked",
    )

if __name__ == "__main__":
    main()
