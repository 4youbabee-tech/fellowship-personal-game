#!/usr/bin/env python3
"""Fail-closed P1C01 original-source -> existing UE4 importer post-import plan.

This standalone module has no Unreal dependency; UE4 editor invokes the matching
post-import script after ShireProductionImport has materialized LOD0 assets.
Source-stage receipts are not a substitute for the ten-ZIP Windows QC receipt.
"""
import hashlib
import json
import re
from pathlib import Path, PurePosixPath

MANIFEST_SHA = '65ae0447840725746614220d8135a65c9b897ba8326d69c756cf5e1a50519b7b'
CONTENT_ROOT = Path('SourceAssets/Production/World/Shire/CuratedP1C01')
LOD_ROOT = Path('Saved/P1C01CuratedLOD')
RECEIPT = Path('Saved/P1C01CuratedStage/receipt.json')
ASSET_ROOT = '/Game/Production/World/Shire/CuratedP1C01/'
FALSE_GATES = ('unreal_asset_imported', 'ue_lods_built', 'collision_tested',
               'nav_tested', 'quest_tested', 'audio_verified', 'pie_tested',
               'device_tested', 'visual_accepted', 'gate6_7_closed')


class CuratedBridgeError(ValueError):
    pass


def require(ok, code):
    if not ok:
        raise CuratedBridgeError(code)


def safe_relative(value):
    require(isinstance(value, str) and value and '\\' not in value and ':' not in value,
            'INVALID_SOURCE_PATH')
    p = PurePosixPath(value)
    require(not p.is_absolute() and '..' not in p.parts and str(p) == value,
            'SOURCE_PATH_TRAVERSAL')
    return Path(*p.parts)


def sha256_file(path):
    d = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            d.update(chunk)
    return d.hexdigest()


def checked_file(workspace, relative, expected_sha, extension):
    require(isinstance(expected_sha, str) and re.fullmatch(r'[a-f0-9]{64}', expected_sha),
            'UNTRUSTED_ASSET_DIGEST')
    path = workspace / relative
    resolved = path.resolve()
    require(resolved != workspace and workspace in resolved.parents,
            'STAGED_ASSET_OUTSIDE_WORKSPACE')
    require(not path.is_symlink() and resolved.is_file() and path.suffix.lower() == extension,
            'STAGED_ASSET_MISSING_OR_WRONG_FORMAT:' + str(relative))
    require(sha256_file(resolved) == expected_sha, 'STAGED_ASSET_HASH_MISMATCH:' + str(relative))
    return str(resolved)


def build_plan(workspace, receipt_path=None):
    workspace = Path(workspace).resolve()
    receipt_path = Path(receipt_path) if receipt_path else workspace / RECEIPT
    require(receipt_path.resolve() == (workspace / RECEIPT).resolve(), 'UNTRUSTED_RECEIPT_LOCATION')
    require(receipt_path.is_file() and not receipt_path.is_symlink(), 'SOURCE_RECEIPT_MISSING')
    data = json.loads(receipt_path.read_text(encoding='utf-8-sig'))
    require(data.get('chapter') == 'P1C01' and data.get('schema_version') == 1,
            'SOURCE_RECEIPT_WRONG_CHAPTER')
    require(data.get('mode') == 'ORIGINAL_SOURCE_STAGED_NOT_UE4_IMPORTED',
            'SOURCE_MODE_NOT_SAFE')
    require(data.get('source_manifest_sha256') == MANIFEST_SHA, 'CURATED_MANIFEST_MISMATCH')
    require(Path(data.get('workspace', '')).resolve() == workspace, 'SOURCE_WORKSPACE_MISMATCH')
    require(data.get('engine_import_allowed_now') is False, 'UNSAFE_AUTO_PROMOTION')
    for flag in FALSE_GATES:
        require(data.get(flag) is False, 'SOURCE_FALSE_EVIDENCE:' + flag)
    require(data.get('source_stage_count') == 143 and data.get('lod_sidecars') == 46 and
            data.get('source_png') == 63 and data.get('importable_ue_base_meshed_families') == 34,
            'CURATED_STAGE_COUNTS_DRIFT')
    require(data.get('external_license_held_count') == 120 and
            len(data.get('external_license_held', [])) == 120,
            'EXTERNAL_RIGHTS_QUARANTINE_DRIFT')
    rows = data.get('source_stage_files', [])
    require(len(rows) == 143 and len({row.get('source') for row in rows}) == 143,
            'STAGE_INVENTORY_NOT_DEDUPLICATED')
    for row in rows:
        require(row.get('track') not in ('L07_CHARACTER_QC_REVIEW_ONLY',
                                         'L08_AUDIO_AND_RUNTIME_QA_REVIEW_ONLY'),
                'UNREVIEWED_CHARACTER_AUDIO_PROMOTION')
    sources = {row['source'] for row in rows}
    held = {row.get('source') for row in data['external_license_held']}
    require(not (sources & held), 'EXTERNAL_LICENSE_SOURCE_IN_STAGE')
    meshes, textures = [], []
    for family in data.get('mesh_families', []):
        lods = family.get('lods', {})
        expected = 3 if family.get('id', '').startswith('Nature/') else 2
        require(family.get('expected_lod_count') == expected and
                set(lods) == {str(i) for i in range(expected)},
                'MESH_LOD_FAMILY_INCOMPLETE:' + str(family.get('id')))
        paths = []
        for index in range(expected):
            row = lods[str(index)]
            source_file = row.get('source_file')
            require(source_file in sources, 'LOD_NOT_IN_SELECTED_SOURCE_INVENTORY')
            rel = safe_relative(source_file)
            require(rel.suffix.lower() == '.fbx' and rel.stem.endswith('_LOD' + str(index)),
                    'LOD_SOURCE_NAMING_MISMATCH')
            source_root = CONTENT_ROOT if index == 0 else LOD_ROOT
            paths.append(checked_file(workspace, source_root / rel, row.get('sha256'), '.fbx'))
        asset = family.get('base_asset_path')
        base_rel = safe_relative(lods['0']['source_file']).with_suffix('')
        require(asset == ASSET_ROOT + base_rel.as_posix(), 'LOD0_ASSET_PATH_MISMATCH')
        meshes.append({'id': family['id'], 'asset_path': asset, 'lod_paths': paths,
                       'expected_lod_count': expected,
                       'collision_policy': family.get('collision_policy'),
                       'hism_candidate': bool(family.get('hism_candidate'))})
    require(len(meshes) == 34 and len({row['asset_path'] for row in meshes}) == 34 and
            sum(len(row['lod_paths'])-1 for row in meshes) == 46,
            'EXPECTED_34_MESHES_46_LODS')
    for group, maps in data.get('material_triplets', {}).items():
        require(set(maps) == {'BaseColor', 'NormalDX', 'ORM'}, 'INCOMPLETE_MATERIAL:' + group)
        for kind, row in maps.items():
            source = row.get('source_file')
            require(source in sources, 'MATERIAL_MAP_NOT_IN_SELECTED_INVENTORY')
            rel = safe_relative(source)
            require(rel.suffix.lower() == '.png', 'PACKED_TEXTURE_MUST_BE_PNG')
            require(row.get('asset_path') == ASSET_ROOT + rel.with_suffix('').as_posix(),
                    'TEXTURE_ASSET_PATH_MISMATCH')
            require(row.get('srgb') is (kind == 'BaseColor'), 'TEXTURE_SRGB_MISMATCH')
            require(row.get('compression') == {'BaseColor':'TC_DEFAULT','NormalDX':'TC_NORMALMAP',
                                               'ORM':'TC_MASKS'}[kind],
                    'TEXTURE_COMPRESSION_MISMATCH')
            textures.append({'asset_path': row['asset_path'], 'kind': kind,
                             'file': checked_file(workspace, CONTENT_ROOT / rel,
                                                  row.get('sha256'), '.png')})
    require(len(textures) == 63 and len({r['asset_path'] for r in textures}) == 63,
            'EXPECTED_63_PACKED_PNG')
    return {'chapter': 'P1C01', 'mesh_families': meshes, 'textures': textures,
            'counts': {'mesh_families':34,'sidecar_lods':46,'packed_textures':63,
                       'license_held_external':120},
            'stage_receipt_sha256': sha256_file(receipt_path),
            'source_manifest_sha256': MANIFEST_SHA}


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--workspace', required=True, type=Path)
    ap.add_argument('--receipt', type=Path)
    opts = ap.parse_args()
    p = build_plan(opts.workspace, opts.receipt)
    print('P1C01_CURATED_UE_PREFLIGHT_PASS', json.dumps(p['counts'], sort_keys=True))
    print('BOUNDARY SOURCE_VERIFIED_EDITOR_IMPORT_LOD_NAV_PIE_DEVICE_VISUAL_PENDING')
