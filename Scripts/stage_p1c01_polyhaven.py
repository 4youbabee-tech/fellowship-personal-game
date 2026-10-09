#!/usr/bin/env python3
"""Bounded, official-API Poly Haven static-FBX candidate intake for P1C01.

Produces a verifiable receipt and an artifact-only staging directory. It never
edits source runtime, invokes UE4 or claims imported/accepted 3D game assets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

API_ROOT = 'https://api.polyhaven.com'
ALLOWED_FILE_HOSTS = {'dl.polyhaven.org', 'cdn.polyhaven.org', 'cdn.polyhaven.com'}
MAX_ASSETS = 5
MAX_TOTAL_BYTES = 80 * 1024 * 1024
MAX_SINGLE_BYTES = 30 * 1024 * 1024
ALLOWED_EXT = {'.fbx', '.png', '.tga', '.jpg', '.jpeg', '.exr', '.bin', '.webp'}
ASSET_ID = re.compile(r'^[a-z0-9_]{3,80}$')
USER_AGENT = 'ShireJourney-P1C01-Photoreal-CC0-Intake/1.0 (Powered by Poly Haven)'


class IntakeError(Exception):
    pass


def read_json(url: str) -> dict:
    req = Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'application/json'})
    with urlopen(req, timeout=22) as response:
        if response.status != 200:
            raise IntakeError(f'API_HTTP_{response.status}')
        data = response.read(3 * 1024 * 1024 + 1)
    if len(data) > 3 * 1024 * 1024:
        raise IntakeError('API_METADATA_TOO_LARGE')
    val = json.loads(data)
    if not isinstance(val, dict):
        raise IntakeError('API_INVALID_JSON_TYPE')
    return val


def safe_name(value: str) -> Path:
    if not isinstance(value, str) or '\\' in value or '\x00' in value or value.startswith('/'):
        raise IntakeError('UNSAFE_FILENAME')
    obj = PurePosixPath(value)
    if not value or '..' in obj.parts or any(p in ('', '.', '..') for p in obj.parts):
        raise IntakeError('UNSAFE_FILENAME')
    if obj.suffix.lower() not in ALLOWED_EXT or len(str(obj)) > 180:
        raise IntakeError('UNSUPPORTED_STAGED_FILE_FORMAT')
    return Path(*obj.parts)


def verify_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != 'https' or parsed.netloc.lower() not in ALLOWED_FILE_HOSTS or not parsed.path:
        raise IntakeError('UNTRUSTED_ASSET_DOWNLOAD_HOST')
    if parsed.username or parsed.password:
        raise IntakeError('URL_CREDENTIALS_FORBIDDEN')


def file_spec(name: str, node: dict) -> dict:
    if not isinstance(node, dict):
        raise IntakeError('INVALID_PROVIDER_FILE_RECORD')
    url = node.get('url')
    verify_url(url)
    size = node.get('size')
    md5 = node.get('md5')
    if not isinstance(size, int) or size <= 0 or size > MAX_SINGLE_BYTES:
        raise IntakeError('INVALID_OR_OVERSIZED_FILE')
    if not isinstance(md5, str) or not re.fullmatch(r'[a-fA-F0-9]{32}', md5):
        raise IntakeError('MISSING_PROVIDER_MD5')
    return {'path': str(safe_name(name)), 'url': url, 'size': size, 'expected_md5': md5.lower()}


def plan_from_fbx_files(files: dict, asset_id: str, resolution: str = '1k') -> list[dict]:
    """Parse only the documented FBX resolution + include dependency records."""
    try:
        block = files['fbx'][resolution]['fbx']
    except (KeyError, TypeError):
        raise IntakeError('NO_NATIVE_FBX_AT_1K')
    if not isinstance(block, dict) or not isinstance(block.get('url'), str):
        raise IntakeError('INVALID_FBX_RECORD')
    records = [file_spec(asset_id + '.fbx', block)]
    depends = block.get('include', {})
    if not isinstance(depends, dict):
        raise IntakeError('INVALID_FBX_DEPENDENCIES')
    for key, value in sorted(depends.items()):
        records.append(file_spec(key, value))
    paths = [x['path'].lower() for x in records]
    if len(set(paths)) != len(paths):
        raise IntakeError('DUPLICATED_DESTINATION_FILE')
    # Do not silently stage a model without any surface source. That would
    # falsely imply that it is suitable for the visual-fidelity experiment.
    if not any(Path(p).suffix in {'.png', '.jpg', '.jpeg', '.tga'} for p in paths[1:]):
        raise IntakeError('NO_SURFACE_TEXTURE_DEPENDENCIES')
    return records


def download_verified(spec: dict, dest: Path) -> dict:
    verify_url(spec['url'])
    dest.parent.mkdir(parents=True, exist_ok=True)
    temp = dest.with_name(dest.name + '.part')
    total = 0
    md5 = hashlib.md5()
    sha256 = hashlib.sha256()
    try:
        req = Request(spec['url'], headers={'User-Agent': USER_AGENT})
        with urlopen(req, timeout=50) as response, temp.open('wb') as stream:
            if response.status != 200:
                raise IntakeError(f'DOWNLOAD_HTTP_{response.status}')
            for chunk in iter(lambda: response.read(256 * 1024), b''):
                total += len(chunk)
                if total > spec['size'] or total > MAX_SINGLE_BYTES:
                    raise IntakeError('DOWNLOAD_EXCEEDED_FILE_LIMIT')
                stream.write(chunk)
                md5.update(chunk)
                sha256.update(chunk)
        if total != spec['size'] or md5.hexdigest() != spec['expected_md5']:
            raise IntakeError('PROVIDER_SIZE_OR_MD5_MISMATCH')
        if dest.suffix.lower() == '.png' and dest.with_name(dest.name + '.part').read_bytes()[:8] != b'\x89PNG\r\n\x1a\n':
            raise IntakeError('PNG_SIGNATURE_MISMATCH')
        if dest.suffix.lower() == '.fbx':
            with temp.open('rb') as stream:
                header = stream.read(128)
            if not (header.startswith(b'Kaydara FBX Binary') or b'FBX' in header):
                raise IntakeError('FBX_SIGNATURE_MISMATCH')
        temp.replace(dest)
        return {'relative_file': spec['path'], 'bytes': total, 'provider_md5': md5.hexdigest(), 'sha256': sha256.hexdigest(), 'format': dest.suffix.lower()}
    except Exception:
        temp.unlink(missing_ok=True)
        raise


def stage(manifest: dict, root: Path, *, max_bytes: int = MAX_TOTAL_BYTES) -> dict:
    if manifest.get('schema_version') != 1 or manifest.get('asset_category') != 'STATIC_MESH':
        raise IntakeError('INVALID_PILOT_MANIFEST')
    candidates = manifest.get('candidates', [])
    if not isinstance(candidates, list) or not 1 <= len(candidates) <= MAX_ASSETS:
        raise IntakeError('INVALID_CANDIDATE_COUNT')
    root.mkdir(parents=True, exist_ok=True)
    receipts = []
    cumulative = 0
    for candidate in candidates:
        slug = candidate.get('provider_asset_id') if isinstance(candidate, dict) else None
        if not isinstance(slug, str) or not ASSET_ID.fullmatch(slug):
            raise IntakeError('UNSAFE_ASSET_ID')
        row = {'id': slug, 'source_page': f'https://polyhaven.com/a/{slug}', 'stage': 'NOT_STAGED', 'files': [], 'planned_total_bytes': 0, 'errors': []}
        receipts.append(row)
        output = root / 'assets' / slug
        try:
            metadata = read_json(f'{API_ROOT}/files/{slug}')
            planned = plan_from_fbx_files(metadata, slug, '1k')
            amount = sum(x['size'] for x in planned)
            row['planned_total_bytes'] = amount
            if cumulative + amount > max_bytes:
                raise IntakeError('WAVE_DOWNLOAD_BUDGET_EXCEEDED')
            row['planned_files'] = len(planned)
            for spec in planned:
                row['files'].append(download_verified(spec, output / safe_name(spec['path'])))
            cumulative += amount
            row['stage'] = 'STAGED_SOURCE_ONLY'
            row['notes'] = 'Includes native FBX plus original downloaded textures; JPG/EXR if present must be converted to PNG/TGA. Not Unreal imported or visual-accepted.'
        except (HTTPError, URLError, IntakeError, TimeoutError, ValueError, OSError) as error:
            row['stage'] = 'QUARANTINED_SOURCE_INTAKE'
            row['errors'].append(type(error).__name__ + ':' + str(error)[:180])
            # Prevent partial files from being mistaken for a completed source.
            if output.exists():
                for item in sorted(output.rglob('*'), reverse=True):
                    if item.is_file():
                        item.unlink()
                for item in sorted(output.rglob('*'), reverse=True):
                    if item.is_dir():
                        item.rmdir()
                output.rmdir()
            row['files'] = []
            print('P1C01_POLYHAVEN_QUARANTINE id=' + slug + ' reason=' + row['errors'][0], flush=True)
        else:
            print('P1C01_POLYHAVEN_STAGED id=' + slug + ' files=' + str(len(row['files'])) + ' source_bytes=' + str(amount), flush=True)
    staged = sum(r['stage'] == 'STAGED_SOURCE_ONLY' for r in receipts)
    result = {
        'schema_version': 1,
        'source': 'Poly Haven Public API (Powered by Poly Haven)',
        'source_cc0_license': 'https://polyhaven.com/license',
        'execution_scope': 'HOSTED_SOURCE_ONLY_NO_UNREAL',
        'source_assets_staged': staged,
        'source_assets_quarantined': len(receipts) - staged,
        'total_staged_file_bytes': cumulative,
        'max_download_bytes': max_bytes,
        'state': 'SOURCE_STAGING_PARTIAL_OR_FULL' if staged else 'NO_QUALIFIED_ASSETS_STAGED',
        'evidence_boundary': 'No Unreal import, no FBX retopology, no PIE, no GPU/device visual acceptance, no presumed 30 FPS.',
        'asset_results': receipts,
    }
    (root / 'p1c01_polyhaven_source_receipt.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return result


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--max-total-mb', type=int, default=80)
    args = p.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
        report = stage(manifest, args.output, max_bytes=args.max_total_mb * 1024 * 1024)
    except (IntakeError, OSError, ValueError, TypeError) as err:
        print('P1C01_POLYHAVEN_SCRIPT_ERROR ' + str(err), file=sys.stderr)
        return 2
    print(f"P1C01_POLYHAVEN_WAVE_RECEIPT stage={report['state']} sourced={report['source_assets_staged']} quarantined={report['source_assets_quarantined']} bytes={report['total_staged_file_bytes']}")
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a', encoding='utf-8') as out:
            out.write(f"### P1C01 Poly Haven source-only intake\n\nStaged: **{report['source_assets_staged']}**, quarantined: **{report['source_assets_quarantined']}**. Raw bytes: {report['total_staged_file_bytes']}.\n\n**This does not imply Unreal/visual acceptance.**\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
