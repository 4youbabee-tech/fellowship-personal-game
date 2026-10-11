#!/usr/bin/env python3
"""Audit whole-game region production packets and current P1C01 warehouse readiness.

This check keeps broad Middle-earth preparation moving while preserving the
Governor boundary: later regions can be prepared, but P1C02+ runtime is not
opened before P1C01 Gate 6/7 evidence exists.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_DELIVERABLES = {
    'terrain',
    'materials',
    'vegetation',
    'architecture',
    'interiors',
    'water',
    'lighting',
    'characters',
    'living_world',
    'audio',
    'interaction',
    'cinematics',
    'collision_navmesh',
    'streaming_memory',
    'profiling',
    'acceptance',
}

REQUIRED_SOURCING_CATEGORIES = {
    'materials',
    'vegetation',
    'architecture_props',
    'animation',
    'audio',
    'vfx',
    'terrain_tools',
}

P1C01_REGION_IDS = {'SHIRE_HOBBITON', 'BAG_END'}
P1C01_MINIMUM_LANES = {
    'FOLIAGE_NATURE': 63,
    'REGIONAL_SURFACE_PREP': 36,
    'SHIRE_ARCHITECTURE': 44,
}
P1C01_MINIMUM_NATURE_FAMILIES = 12


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def audit_region_packets(packets_doc: dict) -> list[str]:
    errors: list[str] = []
    packets = packets_doc.get('packets', [])

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    require(packets_doc.get('packet_set_id') == 'WHOLE_GAME_REGION_PRODUCTION_PACKETS_V1', 'WRONG_PACKET_SET')
    require(len(packets) == 28, 'REGION_PACKET_COUNT_NOT_28')

    seen_ids: set[str] = set()
    expected_order = 1
    for packet in packets:
        region_id = packet.get('region_id', '<missing>')
        require(region_id not in seen_ids, f'DUPLICATE_REGION_ID:{region_id}')
        seen_ids.add(region_id)

        require(packet.get('order') == expected_order, f'REGION_ORDER_GAP:{region_id}')
        expected_order += 1

        missing_deliverables = REQUIRED_DELIVERABLES - set(packet.get('deliverables', {}))
        require(not missing_deliverables, f'MISSING_DELIVERABLES:{region_id}:{",".join(sorted(missing_deliverables))}')

        missing_sourcing = REQUIRED_SOURCING_CATEGORIES - set(packet.get('sourcing', {}))
        require(not missing_sourcing, f'MISSING_SOURCING:{region_id}:{",".join(sorted(missing_sourcing))}')

        require(bool(packet.get('canonical_kit_requirements')), f'MISSING_KIT_REQUIREMENTS:{region_id}')
        require(bool(packet.get('production_families')), f'MISSING_PRODUCTION_FAMILIES:{region_id}')

    return errors


def audit_p1c01_curated_support(curated_doc: dict, disposition_doc: dict) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)

    require(curated_doc.get('chapter') == 'P1C01', 'CURATED_NOT_P1C01')
    for lane, minimum in P1C01_MINIMUM_LANES.items():
        actual = curated_doc.get('counts_by_lane', {}).get(lane, 0)
        require(actual >= minimum, f'P1C01_LANE_UNDER_MINIMUM:{lane}:{actual}<{minimum}')

    require(
        len(curated_doc.get('nature_lod_families', {})) >= P1C01_MINIMUM_NATURE_FAMILIES,
        'P1C01_NATURE_FAMILIES_UNDER_MINIMUM',
    )

    for flag in ('engine_imported', 'collision_tested_in_ue4', 'lod_assigned_in_ue4', 'pie_tested', 'device_tested', 'visual_accepted', 'gate6_7_closed'):
        require(curated_doc.get(flag) is False, f'CURATED_FALSE_ENGINE_EVIDENCE_REQUIRED:{flag}')

    dispositions = {entry.get('id'): entry for entry in disposition_doc.get('dispositions', [])}
    for required in ('SHIRE_HOBBITON_WORLD', 'BAG_END_WORLD', 'SHIRE_LIVING_WORLD', 'F1_03_FERRY_ESCAPE'):
        require(required in dispositions, f'MISSING_P1C01_DISPOSITION:{required}')

    require(
        disposition_doc.get('status') == 'PREPARATION_COMPLETE_RUNTIME_CARS_GATED',
        'DISPOSITION_STATUS_NOT_GATED',
    )

    return errors


def build_readiness_summary(packets_doc: dict, curated_doc: dict) -> dict:
    packets = packets_doc.get('packets', [])
    ready_sources = {
        'P1C01_curated_physical_file_count': curated_doc.get('curated_physical_file_count', 0),
        'P1C01_logical_asset_bindings': curated_doc.get('logical_asset_bindings', 0),
        'P1C01_nature_lod_families': len(curated_doc.get('nature_lod_families', {})),
        'P1C01_counts_by_lane': curated_doc.get('counts_by_lane', {}),
    }
    return {
        'region_packet_count': len(packets),
        'p1c01_priority_regions': sorted(P1C01_REGION_IDS),
        'ready_source_summary': ready_sources,
        'later_runtime_locked_until_p1c01_gate67': True,
        'region_ids': [packet.get('region_id') for packet in packets],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--packets', type=Path, default=Path('Data/WholeGameRegionProductionPacketsV1.json'))
    parser.add_argument('--curated', type=Path, default=Path('Data/P1C01DrivePhysicalCuratedSource20261012.json'))
    parser.add_argument('--disposition', type=Path, default=Path('Data/P1C01SourceToRuntimeDispositionV1.json'))
    parser.add_argument('--summary', action='store_true')
    args = parser.parse_args()

    packets = read_json(args.packets)
    curated = read_json(args.curated)
    disposition = read_json(args.disposition)

    errors = audit_region_packets(packets)
    errors.extend(audit_p1c01_curated_support(curated, disposition))

    if errors:
        for error in errors:
            print('WHOLE_GAME_REGION_READINESS_ERROR', error)
        return 1

    if args.summary:
        print(json.dumps(build_readiness_summary(packets, curated), indent=2, sort_keys=True))
    else:
        print('WHOLE_GAME_REGION_READINESS_PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
