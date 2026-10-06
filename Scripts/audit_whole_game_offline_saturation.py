#!/usr/bin/env python3
import json
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
