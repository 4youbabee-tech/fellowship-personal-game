#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")

def check(ok, code, errors):
    if not ok:
        errors.append(code)

def no_tokens(row, fields, tokens):
    values = []
    for field in fields:
        values.extend(row.get(field, []))
    return all(token not in values for token in tokens)

def main():
    errors = []
    canonical = [
        "F1-01","F1-02","F1-03","F1-04","F1-05","F1-06","F1-07","F1-08",
        "F2-01","F2-02","F2-03","F2-04","F2-05","F2-06","F2-07","F2-08",
        "F3-01","F3-02","F3-03","F3-04","F3-05","F3-06","F3-07"
    ]

    matrix = load("Data/WholeGameChapterAssetDemandMatrixV1.json")
    packets = load("Data/WholeGameChapterProductionPacketsV1.json")
    audit = load("Data/WholeGameOfflineDeepAuditV1.json")
    batch = load("Data/WholeGameWarehouseSaturationBatchV3.json")
    registry = load("Data/GlobalWarehouseSourceRegistryV2.json")
    governor = load("Data/ProjectGovernor.json")
    branches = load("Data/BranchCleanupPlan.json")
    workflow = read(".github/workflows/whole-game-offline-saturation.yml")

    rows = matrix.get("rows", [])
    row_by_id = {x["chapter_id"]: x for x in rows}
    packet_by_id = {x["id"]: x for x in packets.get("packets", [])}

    check(matrix.get("chapter_count") == 23, "matrix_declared_chapter_count", errors)
    check(len(rows) == 23, "matrix_actual_chapter_count", errors)
    check([x.get("chapter_id") for x in rows] == canonical, "matrix_canonical_sequence", errors)
    check(set(packet_by_id) == set(canonical), "source_packet_set", errors)
    check(audit.get("source_governance", {}).get("canonical_sequence") == canonical,
          "audit_canonical_sequence", errors)

    for chapter_id in canonical:
        r = row_by_id.get(chapter_id)
        p = packet_by_id.get(chapter_id)
        if not r or not p:
            continue
        check(r.get("source_title") == p.get("title"), f"{chapter_id}_title", errors)
        check(r.get("source_primary_location") == p.get("location"), f"{chapter_id}_location", errors)
        check(r.get("source_playable_present_focus") == p.get("focus"), f"{chapter_id}_focus", errors)
        check(r.get("source_locked_postcondition") == p.get("locked_postcondition"),
              f"{chapter_id}_outcome", errors)
        check(r.get("runtime_integration_allowed") is False, f"{chapter_id}_runtime_gate", errors)

    check(no_tokens(row_by_id["F1-03"],
                    ["environment_families","character_families","animation_families","audio_families"],
                    ["bree_timber_stone_town","inn_stable_gate_interiors","ent_scale_creature_support",
                     "large_creature_walk_interact","crowded_inn_rain_night_town"]),
          "F1-03_cross_chapter_pollution", errors)
    check(no_tokens(row_by_id["F1-04"], ["character_families","animation_families"],
                    ["ent_scale_creature_support","large_creature_walk_interact"]),
          "F1-04_ent_pollution", errors)
    check(no_tokens(row_by_id["F1-05"], ["character_families","animation_families"],
                    ["ent_scale_creature_support","large_creature_walk_interact"]),
          "F1-05_ent_pollution", errors)
    check(no_tokens(row_by_id["F1-08"], ["environment_families","vfx_families"],
                    ["mordor_volcanic_wasteland","black_gate_fortification","lava_ash_rock","ash_smoke_fire_lava"]),
          "F1-08_mordor_pollution", errors)
    check(no_tokens(row_by_id["F2-01"], ["character_families","interaction_families"],
                    ["ent_scale_creature_support","large_creature_traversal"]),
          "F2-01_ent_early_pollution", errors)
    check(no_tokens(row_by_id["F2-03"], ["character_families","animation_families"],
                    ["ent_scale_creature_support","large_creature_walk_interact"]),
          "F2-03_ent_pollution", errors)
    check(no_tokens(row_by_id["F3-03"], ["character_families","animation_families"],
                    ["ent_scale_creature_support","large_creature_walk_interact"]),
          "F3-03_ent_pollution", errors)
    check(no_tokens(row_by_id["F3-04"], ["environment_families","vfx_families"],
                    ["mordor_volcanic_wasteland","black_gate_fortification","lava_ash_rock","ash_smoke_fire_lava"]),
          "F3-04_mordor_environment_pollution", errors)
    check(no_tokens(row_by_id["F3-07"], ["environment_families","vfx_families"],
                    ["pelennor_field","siege_fortification","siege_fire_smoke_dust"]),
          "F3-07_active_siege_pollution", errors)

    sources = registry.get("sources", [])
    check(registry.get("source_count") == len(sources), "registry_count_drift", errors)
    check(len({x.get("id") for x in sources}) == len(sources), "registry_duplicate_ids", errors)

    candidates = batch.get("candidates", [])
    check(len(candidates) >= 15, "warehouse_candidate_depth", errors)
    check(len({x.get("id") for x in candidates}) == len(candidates), "warehouse_candidate_duplicate_ids", errors)
    check(all(str(x.get("state","")).startswith("CANDIDATE") for x in candidates),
          "warehouse_false_staging_guard", errors)

    exception = governor.get("whole_game_offline_saturation_exception_2026_10_06", {})
    check(exception.get("status") == "ACTIVE_WHILE_UE4_RUNNER_UNAVAILABLE",
          "governor_offline_exception", errors)
    check(exception.get("runtime_authority") == "P1C01_ONLY",
          "governor_runtime_serialization", errors)
    check(any(x.get("id") == "DEC-105" and x.get("status") == "ACCEPTED"
              for x in governor.get("decisions", [])), "governor_dec105", errors)

    active = "production/p1c01-definitive-chapter-closeout-2026-10-04"
    preserve = {x.get("branch") for x in branches.get("preserve_pending_salvage", [])}
    check(active in set(branches.get("active_work_branches", [])), "active_branch_protection", errors)
    check({"prep/f2-03-edoras-mega-source-v1","prep/f2-03-edoras-mega-source-v2"}.issubset(preserve),
          "edoras_unique_salvage_protection", errors)

    check("runs-on: self-hosted" not in workflow and "UE4-27-Windows" not in workflow,
          "offline_workflow_runner_isolation", errors)
    check("ubuntu-latest" in workflow and "windows-latest" in workflow,
          "offline_hosted_jobs", errors)

    # Final pre-runner repository hygiene and architecture sweep.
    repo_files = [p for p in ROOT.rglob("*") if p.is_file()]
    repo_rel = [p.relative_to(ROOT).as_posix() for p in repo_files]

    check(not any(p.lower().endswith(".bmp") for p in repo_rel),
          "forbidden_bmp_source_present", errors)
    check(not any(p.startswith(("Binaries/","DerivedDataCache/","Intermediate/","Saved/",".vs/"))
                  for p in repo_rel), "generated_runtime_directory_tracked", errors)

    source_headers = [p for p in repo_rel if p.startswith("Source/") and p.lower().endswith(".h")]
    source_cpp = [p for p in repo_rel if p.startswith("Source/") and p.lower().endswith(".cpp")]
    check(all("/Public/" in p for p in source_headers),
          "cpp_header_outside_public", errors)
    check(all("/Private/" in p for p in source_cpp),
          "cpp_source_outside_private", errors)

    validated_runtime = [p for p in repo_rel if p.startswith("SourceAssets/ValidatedRuntime/")]
    check(not any(p.lower().endswith(".obj") for p in validated_runtime),
          "validated_runtime_contains_obj", errors)
    check(all(not p.lower().endswith(".fbx") or "/ValidatedRuntime/" in p
              for p in repo_rel if p.startswith("SourceAssets/ValidatedRuntime/")),
          "validated_runtime_fbx_path_guard", errors)

    runtime_cpp_paths = [
        p for p in ROOT.glob("Source/ShireJourney/Private/**/*.cpp")
        if p.is_file()
    ]
    runtime_loads = []
    runtime_static_loads = []
    runtime_finders = []
    load_re = re.compile(
        r'LoadObject<[^>]+>\s*\([^;]*?TEXT\("([^"]+)"\)[^;]*?\);',
        flags=re.S,
    )
    finder_re = re.compile(
        r'ConstructorHelpers::FObjectFinder<[^>]+>\s+[A-Za-z_][A-Za-z0-9_]*'
        r'\s*\(\s*TEXT\("([^"]+)"\)\s*\)',
        flags=re.S,
    )
    for source_path in runtime_cpp_paths:
        source_text = source_path.read_text(encoding="utf-8", errors="replace")
        rel = source_path.relative_to(ROOT).as_posix()
        for match in load_re.finditer(source_text):
            runtime_loads.append((rel, match.group(1)))
        if "StaticLoadObject" in source_text:
            runtime_static_loads.append(rel)
        for match in finder_re.finditer(source_text):
            runtime_finders.append((rel, match.group(1)))

    check(all(asset.startswith("/Engine/BasicShapes/") for _, asset in runtime_loads),
          "heavy_runtime_loadobject_detected", errors)
    check(not runtime_static_loads, "runtime_staticloadobject_detected", errors)
    check(all(asset.startswith("/Engine/BasicShapes/") for _, asset in runtime_finders),
          "runtime_fobjectfinder_non_engine_asset", errors)

    streaming_cpp = read("Source/ShireJourney/Private/Subsystems/ShireChapterAssetStreamingSubsystem.cpp")
    check("RequestAsyncLoad" in streaming_cpp,
          "chapter_streaming_async_request_missing", errors)
    check("LoadObject<" not in streaming_cpp and "StaticLoadObject" not in streaming_cpp,
          "chapter_streaming_sync_load_returned", errors)

    npc_context_cpp = read("Source/ShireJourney/Private/Subsystems/ShireNPCContextSubsystem.cpp")
    for forbidden_context_scan in ["GetAllActorsOfClass", "TActorIterator<", "SpawnActor<"]:
        check(forbidden_context_scan not in npc_context_cpp,
              "npc_context_authority_or_fullworld_scan_" + forbidden_context_scan.replace("<",""),
              errors)

    living_cpp = read("Source/ShireJourney/Private/World/LivingWorldDirector.cpp")
    for required_pool_symbol in [
        "AcquireAmbientNPC", "ReleaseAmbientNPCToPool",
        "AcquireInteraction", "ReleaseInteractionToPool",
        "AcquireAmbientMotionActor", "ReleaseAmbientMotionToPool",
    ]:
        check(required_pool_symbol in living_cpp,
              "living_world_pool_contract_" + required_pool_symbol, errors)
    check("NextMaintenanceTime = Now + 0.75f;" in living_cpp,
          "living_world_bounded_maintenance_interval", errors)
    check("GetAllActorsOfClass" not in living_cpp,
          "living_world_fullworld_getallactors_scan", errors)

    router_cpp = read("Source/ShireJourney/Private/World/ChapterWorldRouter.cpp")
    check("PrimaryActorTick.bCanEverTick = false;" in router_cpp,
          "chapter_router_tick_disabled", errors)

    shire_builder_cpp = read("Source/ShireJourney/Private/World/ShirePrototypeWorldBuilder.cpp")
    story_flow_cpp = read("Source/ShireJourney/Private/Subsystems/ShireStoryFlowSubsystem.cpp")
    presentation_cpp = read("Source/ShireJourney/Private/Subsystems/ShireStoryPresentationSubsystem.cpp")
    story_plan = read("Data/StoryBeatPlan.csv")
    for forbidden_bridge in [
        'StartChapter(TEXT("P1C02"), TEXT("RoadToBree"), 0)',
        'FerryFarSide->NextChapterId=TEXT("P1C02")',
        'FerryFarSide->NextChapterQuestId=TEXT("RoadToBree")',
    ]:
        check(forbidden_bridge not in (shire_builder_cpp + story_flow_cpp),
              "p1c01_auto_bree_bridge_returned", errors)
    check('FerryFarSide->StoryBeatId=TEXT("FerryEscapeComplete");' in shire_builder_cpp,
          "ferry_terminal_storybeat_missing", errors)
    check('AddCue(TEXT("FerryEscapeComplete")' in presentation_cpp,
          "ferry_terminal_presentation_missing", errors)
    check(",FerryEscapeComplete," in story_plan,
          "ferry_terminal_storyplan_missing", errors)

    runtime_contracts = read("Scripts/runtime_audit_contracts.py")
    check("legacy-terminal preserved=yes canonical-publications=1 worldCommits=0 chapter=P1C01"
          in runtime_contracts, "terminal_restore_contract_drift", errors)

    closure_workflow = read(".github/workflows/p1c01-chapter-closure.yml")
    check("cancel-in-progress: false" in closure_workflow,
          "closure_train_cancellable", errors)

    char_map = load("Data/P1C01CharacterBundleCompletionV1.json")
    required_cast = {
        "FRODO","BILBO","GANDALF","SAM","MERRY","PIPPIN","BLACK_RIDER","BLACK_RIDER_HORSE"
    }
    actual_cast = {x.get("id") for x in char_map.get("required_characters", [])}
    check(actual_cast == required_cast, "p1c01_required_cast_drift", errors)
    check("OBJ_AS_FINAL_ANIMATED_CHARACTER" in char_map.get("forbidden", []),
          "animated_obj_guard_missing", errors)

    audio_map = load("Data/P1C01AudioMasterSlotMapV1.json")
    required_audio = {
        "VOICE_SCRIPTED","VOICE_CONTEXTUAL","CHARACTER_EFFORTS","FOOTSTEPS",
        "CHARACTER_FOLEY","BAG_END_INTERIOR","FARM_CART_WORK","NATURE_AMBIENCE",
        "SOCIAL_PARTY","FERRY_WATER","BLACK_RIDER_THREAT","MUSIC","ACCESSIBILITY_METADATA"
    }
    actual_audio = {x.get("id") for x in audio_map.get("required_families", [])}
    check(actual_audio == required_audio, "p1c01_audio_family_drift", errors)

    mission_map = load("Data/P1C01MissionRuntimeAcceptanceMatrixV1.json")
    terminal = mission_map.get("p1c01_terminal_contract", {})
    check(terminal.get("quest_id") == "FerryEscape" and
          terminal.get("terminal_stage") == 2 and
          terminal.get("terminal_story_beat") == "FerryEscapeComplete" and
          terminal.get("auto_start_p1c02") is False,
          "p1c01_terminal_contract_drift", errors)
    f103 = next((x for x in mission_map.get("missions", []) if x.get("id") == "F1-03"), {})
    check(f103.get("source_locked_postcondition") == "Hobbits reach Bree." and
          "P1C02 owns Bree arrival/opening" in f103.get("topology_rule", ""),
          "f1_03_source_runtime_boundary_drift", errors)

    handoff = load("Data/P1C01RunnerHandoffV1.json")
    check("opening P1C02 automatically" in handoff.get("forbidden", []),
          "runner_handoff_p1c02_lock_missing", errors)

    if errors:
        for error in errors:
            print("WHOLE_GAME_OFFLINE_SATURATION_ERROR", error)
        print("WHOLE_GAME_OFFLINE_SATURATION_FAIL", "errors="+str(len(errors)))
        raise SystemExit(1)

    print(
        "WHOLE_GAME_OFFLINE_SATURATION_PASS",
        "chapters=23",
        "registry_sources="+str(len(sources)),
        "candidate_batch="+str(len(candidates)),
        "runtime=P1C01_ONLY",
        "errors=0",
    )

if __name__ == "__main__":
    main()
