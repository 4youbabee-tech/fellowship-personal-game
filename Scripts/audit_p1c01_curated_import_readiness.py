#!/usr/bin/env python3
"""Fail-closed audit for the P1C01 curated source receipt before UE4 import promotion.

This is intentionally source-only: it verifies that staged meshes, LOD sidecars,
material triplets, collision policies, and held external-license files are safe
to hand to the existing Unreal import path without claiming engine acceptance.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ALLOWED_COLLISION_POLICIES = {
    'SIMPLE_REVIEW_TREE_TRUNK',
    'SIMPLE_REVIEW_ROCK',
    'DECORATIVE_NO_BLOCKER',
    'SIMPLIFIED_AUTHOR_COLLIDER_REVIEW',
    'NO_AUTOGEN_COLLIDER_REVIEW',
}
REQUIRED_MATERIAL_MAPS = {'BaseColor', 'NormalDX', 'ORM'}


def load_receipt(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def audit_receipt(receipt: dict) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    require(receipt.get('chapter') == 'P1C01', 'WRONG_CHAPTER')
    require(receipt.get('mode') == 'ORIGINAL_SOURCE_STAGED_NOT_UE4_IMPORTED', 'WRONG_MODE')
    require(receipt.get('engine_import_allowed_now') is False, 'SOURCE_STAGE_MUST_NOT_AUTO_ALLOW_ENGINE_IMPORT')

    for flag in (
        'unreal_asset_imported',
        'ue_lods_built',
        'collision_tested',
        'nav_tested',
        'quest_tested',
        'audio_verified',
        'pie_tested',
        'device_tested',
        'visual_accepted',
        'gate6_7_closed',
    ):
        require(receipt.get(flag) is False, f'FALSE_EVIDENCE_FLAG_REQUIRED:{flag}')

    mesh_families = receipt.get('mesh_families', [])
    require(len(mesh_families) == 34, 'MESH_FAMILY_COUNT_NOT_34')
    for family in mesh_families:
        family_id = family.get('id', '<missing>')
        lods = family.get('lods', {})
        require(family.get('expected_lod_count') == len(lods), f'LOD_COUNT_MISMATCH:{family_id}')
        require('0' in lods, f'MISSING_LOD0:{family_id}')
        if '0' in lods:
            require(
                lods['0'].get('import_mode') == 'UE4_COMMANDLET_BASE_STATIC_MESH',
                f'LOD0_IMPORT_MODE:{family_id}',
            )
        for lod_key, lod in lods.items():
            if lod_key != '0':
                require(
                    lod.get('import_mode') == 'UE4_EDITOR_LOD_ONLY_NOT_SEPARATE_MESH',
                    f'SIDE_LOD_IMPORT_MODE:{family_id}:{lod_key}',
                )
        require(
            family.get('collision_policy') in ALLOWED_COLLISION_POLICIES,
            f'COLLISION_POLICY_UNKNOWN:{family_id}',
        )
        if str(family_id).startswith('Nature/'):
            require(family.get('hism_candidate') is True, f'NATURE_NOT_HISM:{family_id}')

    material_triplets = receipt.get('material_triplets', {})
    require(len(material_triplets) == 21, 'MATERIAL_TRIPLET_COUNT_NOT_21')
    for material_name, maps in material_triplets.items():
        require(set(maps) == REQUIRED_MATERIAL_MAPS, f'MATERIAL_TRIPLET_INCOMPLETE:{material_name}')
        if 'BaseColor' in maps:
            require(maps['BaseColor'].get('srgb') is True, f'BASECOLOR_SRGB:{material_name}')
            require(maps['BaseColor'].get('compression') == 'TC_DEFAULT', f'BASECOLOR_COMPRESSION:{material_name}')
        if 'NormalDX' in maps:
            require(maps['NormalDX'].get('srgb') is False, f'NORMAL_SRGB:{material_name}')
            require(maps['NormalDX'].get('compression') == 'TC_NORMALMAP', f'NORMAL_COMPRESSION:{material_name}')
        if 'ORM' in maps:
            require(maps['ORM'].get('srgb') is False, f'ORM_SRGB:{material_name}')
            require(maps['ORM'].get('compression') == 'TC_MASKS', f'ORM_COMPRESSION:{material_name}')

    held_external = receipt.get('external_license_held', [])
    require(
        receipt.get('external_license_held_count') == len(held_external) == 120,
        'EXTERNAL_HELD_COUNT_NOT_120',
    )
    staged_sources = {entry.get('source') for entry in receipt.get('source_stage_files', [])}
    for item in held_external:
        require(item.get('source') not in staged_sources, f"EXTERNAL_SOURCE_STAGED:{item.get('source')}")

    tracks = receipt.get('logical_tracks_eight_inside_governor_five_lanes', {})
    require(len(tracks) == 8, 'LOGICAL_TRACKS_NOT_8')
    require(tracks.get('L07_CHARACTER_QC_REVIEW_ONLY') == 0, 'CHARACTER_TRACK_MUST_REMAIN_REVIEW_ONLY')
    require(tracks.get('L08_AUDIO_AND_RUNTIME_QA_REVIEW_ONLY') == 0, 'AUDIO_TRACK_MUST_REMAIN_REVIEW_ONLY')

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('receipt', type=Path)
    args = parser.parse_args()

    errors = audit_receipt(load_receipt(args.receipt))
    if errors:
        for error in errors:
            print('P1C01_CURATED_IMPORT_READINESS_ERROR', error)
        return 1

    print('P1C01_CURATED_IMPORT_READINESS_PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
