#!/usr/bin/env python3
"""Fail-closed, offline preflight of an ALREADY converted P1C01 Poly Haven artifact.

This is not a downloader, Unreal importer, LOD generator, or visual approval.
The input is an existing GitHub Actions FBX/PNG artifact extracted on a hosted runner.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from PIL import Image

ASSETS = ('painted_wooden_bench', 'wooden_crate_01', 'folding_wooden_stool',
          'wooden_lantern_01', 'wicker_basket_01')
SHA = re.compile(r'^[0-9a-f]{64}$')
EXPECTED_ROLES = {'Main': {'BaseColor', 'NormalDX', 'ORM'},
                  'Glass': {'BaseColor', 'NormalDX', 'ORM', 'Opacity'}}


class PreflightError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def safe_file(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or '\\' in relative or '\x00' in relative:
        raise PreflightError('UNSAFE_ARTIFACT_PATH')
    parts = PurePosixPath(relative)
    if parts.is_absolute() or not parts.parts or any(p in ('.', '..') for p in parts.parts):
        raise PreflightError('UNSAFE_ARTIFACT_PATH')
    candidate = root.joinpath(*parts.parts)
    if not candidate.is_file() or candidate.is_symlink() or root.resolve() not in candidate.resolve().parents:
        raise PreflightError('MISSING_OR_UNSAFE_ARTIFACT_FILE:' + relative)
    return candidate


def checked_digest(path: Path, expected: str) -> None:
    if not isinstance(expected, str) or not SHA.fullmatch(expected) or sha256_file(path) != expected:
        raise PreflightError('SHA256_MISMATCH:' + path.name)


def audit(bundle: Path, qc_reference: Path) -> dict:
    """Verify actual FBX+PNG bytes against archived per-file receipts and source QC.

    The original triangle/UV/normal counts are PRIOR evidence, not newly inferred
    from this artifact. A checksum match ties current bytes to that prior inspection.
    """
    if not bundle.is_dir():
        raise PreflightError('MISSING_CONVERTED_ARTIFACT')
    qc = json.loads(qc_reference.read_text(encoding='utf-8'))
    report_path = safe_file(bundle, 'p1c01_png_material_conversion_receipt.json')
    receipt = json.loads(report_path.read_text(encoding='utf-8'))
    if (qc.get('schema_version') != 1 or receipt.get('schema_version') != 1 or
        receipt.get('status') != 'SOURCE_TEXTURES_CONVERTED_STATIC_ONLY' or
        receipt.get('asset_count') != 5):
        raise PreflightError('INVALID_CONVERTED_RECEIPT')
    recorded = qc.get('assets')
    assets = receipt.get('assets')
    if (not isinstance(recorded, list) or not isinstance(assets, list) or
        {x.get('id') for x in recorded} != set(ASSETS) or
        {x.get('asset_id') for x in assets} != set(ASSETS) or
        len(recorded) != 5 or len(assets) != 5):
        raise PreflightError('ASSET_SET_NOT_EXACT_FIVE')
    qc_by_id = {x['id']: x for x in recorded}
    expected_paths = {report_path.resolve()}
    rows = []
    for item in sorted(assets, key=lambda x: x['asset_id']):
        slug = item['asset_id']
        old = qc_by_id[slug]
        fbx = safe_file(bundle, item.get('fbx_path'))
        if fbx.suffix.lower() != '.fbx' or fbx.parent.name != slug:
            raise PreflightError('INVALID_FBX_PATH:' + slug)
        expected_paths.add(fbx.resolve())
        if fbx.stat().st_size != item.get('fbx_bytes'):
            raise PreflightError('FBX_SIZE_MISMATCH:' + slug)
        if item.get('fbx_sha256') != old['fbx_sha256']:
            raise PreflightError('FBX_SOURCE_QC_DISAGREEMENT:' + slug)
        checked_digest(fbx, old['fbx_sha256'])
        with fbx.open('rb') as fh:
            if not fh.read(25).startswith(b'Kaydara FBX Binary'):
                raise PreflightError('INVALID_BINARY_FBX:' + slug)
        materials = item.get('materials')
        if not isinstance(materials, list) or len(materials) != item.get('material_count'):
            raise PreflightError('MATERIAL_COUNT_MISMATCH:' + slug)
        expected_materials = {'Main', 'Glass'} if slug == 'wooden_lantern_01' else {'Main'}
        if {m.get('material') for m in materials} != expected_materials:
            raise PreflightError('MATERIAL_ROLES_MISMATCH:' + slug)
        count_png = 0
        for mat in materials:
            mat_name = mat['material']
            maps = mat.get('maps')
            if not isinstance(maps, list) or {m.get('role') for m in maps} != EXPECTED_ROLES[mat_name] or len(maps) != len(EXPECTED_ROLES[mat_name]):
                raise PreflightError('MAP_ROLES_MISMATCH:' + slug + ':' + mat_name)
            for entry in maps:
                path = safe_file(bundle, entry.get('file'))
                if path.suffix.lower() != '.png' or path.parent.name != slug:
                    raise PreflightError('INVALID_PNG_PATH:' + slug)
                if path.resolve() in expected_paths:
                    raise PreflightError('DUPLICATE_ARTIFACT_FILE:' + path.name)
                expected_paths.add(path.resolve())
                if path.stat().st_size != entry.get('bytes'):
                    raise PreflightError('PNG_SIZE_MISMATCH:' + path.name)
                checked_digest(path, entry.get('sha256'))
                with Image.open(path) as im:
                    im.load()
                    if im.size != (1024, 1024) or entry.get('resolution') != [1024, 1024]:
                        raise PreflightError('INVALID_PNG_RESOLUTION:' + path.name)
                    if im.mode != ('L' if entry['role'] == 'Opacity' else 'RGB'):
                        raise PreflightError('INVALID_PNG_MODE:' + path.name)
                    if entry['role'] == 'ORM' and im.getchannel('R').getextrema() != (255, 255):
                        raise PreflightError('INVALID_WHITE_AO_FALLBACK:' + path.name)
                count_png += 1
        if count_png != old.get('png_count'):
            raise PreflightError('SOURCE_QC_PNG_COUNT_MISMATCH:' + slug)
        tri = old.get('triangles')
        if not isinstance(tri, int) or tri <= 0 or old.get('uv_layers', 0) < 1 or old.get('normal_layers', 0) < 1:
            raise PreflightError('INSUFFICIENT_SOURCE_GEOMETRY_EVIDENCE:' + slug)
        needs_lod = tri > 10000
        rows.append({
            'asset_id': slug, 'fbx_sha256': old['fbx_sha256'], 'source_triangles_prior_qc': tri,
            'source_uv_layers_prior_qc': old['uv_layers'], 'source_normal_layers_prior_qc': old['normal_layers'],
            'png_verified': count_png, 'material_count': len(materials),
            'next_gate': 'HOLD_FOR_LOD_COLLISION_AND_UE_IMPORT' if needs_lod else 'UE4_STATIC_IMPORT_TECHNICAL_REVIEW_REQUIRED',
            'hism_allowed_now': False,
            'ue_imported': False, 'visually_accepted': False,
            'recommended_texture_import': {'BaseColor': 'sRGB ON; Default', 'NormalDX': 'sRGB OFF; Normalmap',
                                           'ORM': 'sRGB OFF; Masks (R AO white, G roughness, B metallic)',
                                           'Opacity': 'sRGB OFF; Grayscale'},
            'collision_proven': False, 'lod_proven': False,
        })
    actual_paths = {p.resolve() for p in bundle.rglob('*') if p.is_file()}
    if actual_paths != expected_paths:
        raise PreflightError('UNTRACKED_OR_MISSING_BUNDLE_FILES:' + str(len(actual_paths ^ expected_paths)))
    if sum(x['png_verified'] for x in rows) != 19:
        raise PreflightError('TOTAL_PNG_COUNT_NOT_19')
    return {
        'schema_version': 1, 'chapter': 'P1C01', 'status': 'OFFLINE_SOURCE_ARTIFACT_PREFLIGHT_PASS',
        'truth_label': 'STATIC-VALIDATED_ONLY', 'source_artifact_only': True,
        'source_qc_sha256_anchor': qc_reference.name, 'assets_verified': len(rows),
        'fbx_verified': 5, 'png_verified': 19,
        'assets_held_for_lod': [x['asset_id'] for x in rows if x['source_triangles_prior_qc'] > 10000],
        'evidence_boundary': 'Existing artifact bytes/hash/1K maps only; no UE4 import, LOD/mesh optimization, collision, human visual review, PIE or target-device FPS.',
        'assets': rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--bundle', type=Path, required=True)
    ap.add_argument('--qc-reference', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    result = audit(args.bundle, args.qc_reference)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('P1C01_EXISTING_ARTIFACT_PREFLIGHT_PASS FBX=5 PNG=19 HOLD_LOD=' + ','.join(result['assets_held_for_lod']) + '; NOT_UE4_IMPORTED')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
