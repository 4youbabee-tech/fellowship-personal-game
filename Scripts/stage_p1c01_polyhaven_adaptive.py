#!/usr/bin/env python3
"""P1C01 selective, max-safe OFFLINE-ONLY source staging from Poly Haven CC0.

Downloads exact suitable native 1K static FBX and original map dependencies,
never UE4 imports. Inputs are the provider's current public metadata; this is
not a bulk mirror. Dynamic item count is limited by real byte/time budgets.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
import time
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

API = 'https://api.polyhaven.com'
USER_AGENT = 'ShireJourney-MaxSafe-CC0-P1C01/1.0 (Powered by Poly Haven)'
ALLOWED_HOSTS = {'dl.polyhaven.org', 'cdn.polyhaven.org', 'cdn.polyhaven.com'}
ALLOWED_FORMATS = {'.fbx', '.png', '.tga', '.jpeg', '.jpg', '.exr', '.webp'}
EXISTING = {'painted_wooden_bench', 'wooden_crate_01', 'folding_wooden_stool',
            'wooden_lantern_01', 'wicker_basket_01'}
KEYWORDS = {
    'wood': 2, 'wooden': 3, 'bench': 2, 'crate': 1, 'barrel': 3, 'basket': 2,
    'fence': 4, 'gate': 3, 'log': 2, 'plank': 2, 'tree': 4, 'branch': 2,
    'rock': 3, 'stone': 3, 'moss': 3, 'grass': 3, 'flower': 3, 'plant': 3,
    'stump': 3, 'bush': 3, 'shrub': 3, 'rural': 4, 'garden': 4, 'farm': 4,
    'leaf': 2, 'leaves': 2, 'cobblestone': 4, 'lantern': 2, 'sack': 2,
    'medieval': 3, 'old': 1, 'weathered': 2, 'vintage': 2, 'wheel': 2,
    'field': 2, 'fern': 3, 'hedge': 4, 'dirt': 2, 'mud': 2, 'watermill': 4,
}
BLOCK = {'sci-fi','scifi','cyber','space','factory','computer','machine','car',
         'automobile','vehicle','electric','plastic','neon','modern','urban',
         'gun','rifle','industrial','engine','concrete','construction','railway',
         'skyscraper','electronics','keyboard','office','airplane'}
SLUG = re.compile(r'^[a-z0-9_]{3,80}$')


class IntakeError(ValueError):
    pass


def read_json(url: str) -> dict:
    if not url.startswith(API + '/'):
        raise IntakeError('UNTRUSTED_API')
    req = Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'application/json'})
    with urlopen(req, timeout=25) as response:
        if response.status != 200 or not response.geturl().startswith(API + '/'):
            raise IntakeError('API_NOT_TRUSTED_OR_HTTP')
        raw = response.read(6 * 1024 * 1024 + 1)
    if len(raw) > 6 * 1024 * 1024:
        raise IntakeError('API_RESPONSE_TOO_LARGE')
    obj = json.loads(raw)
    if not isinstance(obj, dict):
        raise IntakeError('API_RESPONSE_NOT_DICT')
    return obj


def score_asset(slug: str, entry: dict) -> int:
    if slug in EXISTING or not SLUG.fullmatch(slug):
        return 0
    if not isinstance(entry, dict) or entry.get('type') not in (2, None):
        return 0
    text = ' '.join([slug.replace('_', ' '), str(entry.get('name') or ''),
                     str(entry.get('category') or '')] +
                    [str(t) for t in entry.get('tags', []) if isinstance(t, str)]).lower()
    if any(re.search(r'\b' + re.escape(block) + r'\b', text) for block in BLOCK):
        return 0
    return sum(weight for keyword, weight in KEYWORDS.items()
               if re.search(r'\b' + re.escape(keyword) + r'\b', text))


def safe_relative(value: str) -> Path:
    if not isinstance(value, str) or '\\' in value or '\x00' in value or len(value) > 180:
        raise IntakeError('BAD_RELATIVE_NAME')
    p = PurePosixPath(value)
    if p.is_absolute() or not p.parts or any(part in ('', '.', '..') for part in p.parts):
        raise IntakeError('BAD_RELATIVE_NAME')
    if p.suffix.lower() not in ALLOWED_FORMATS:
        raise IntakeError('DISALLOWED_SOURCE_EXTENSION')
    return Path(*p.parts)


def source_file(name: str, block: dict, single_limit: int) -> dict:
    if not isinstance(block, dict):
        raise IntakeError('INVALID_SOURCE_FILE')
    rel = safe_relative(name)
    url, size, md5 = block.get('url'), block.get('size'), block.get('md5')
    parsed = urlparse(url) if isinstance(url, str) else None
    if (not parsed or parsed.scheme != 'https' or parsed.hostname not in ALLOWED_HOSTS
        or parsed.username or parsed.password or parsed.port is not None
        or parsed.fragment or not parsed.path):
        raise IntakeError('UNTRUSTED_SOURCE_HOST')
    if not isinstance(size, int) or isinstance(size, bool) or size <= 0 or size > single_limit:
        raise IntakeError('SOURCE_FILE_OVER_SINGLE_LIMIT')
    if not isinstance(md5, str) or not re.fullmatch(r'[a-fA-F0-9]{32}', md5):
        raise IntakeError('INVALID_PROVIDER_MD5')
    return {'name': str(rel), 'url': url, 'size': size, 'md5': md5.lower()}


def plan_for_model(slug: str, metadata: dict, *, single_limit: int) -> list[dict]:
    try:
        block = metadata['fbx']['1k']['fbx']
    except (KeyError, TypeError):
        raise IntakeError('NATIVE_1K_FBX_UNAVAILABLE')
    if not isinstance(block, dict):
        raise IntakeError('BAD_FBX_BLOCK')
    includes = block.get('include', {})
    if not isinstance(includes, dict):
        raise IntakeError('BAD_INCLUDE')
    if not any(Path(name).suffix.lower() in ('.png', '.tga', '.jpg', '.jpeg') for name in includes):
        raise IntakeError('NO_SOURCE_SURFACE_TEXTURE')
    files = [source_file(slug + '.fbx', block, single_limit)]
    for name, record in sorted(includes.items()):
        files.append(source_file(name, record, single_limit))
    paths = [x['name'].casefold() for x in files]
    if len(set(paths)) != len(paths):
        raise IntakeError('DUPLICATE_FILE_NAME')
    return files


def save_verified(spec: dict, target: Path, deadline: float) -> dict:
    if time.monotonic() >= deadline:
        raise IntakeError('WAVE_TIME_BUDGET')
    target.parent.mkdir(parents=True, exist_ok=True)
    part = target.with_name(target.name + '.part')
    size = 0
    digest_md5, digest_sha = hashlib.md5(), hashlib.sha256()
    try:
        request = Request(spec['url'], headers={'User-Agent': USER_AGENT})
        with urlopen(request, timeout=32) as response, part.open('wb') as out:
            actual = urlparse(response.geturl())
            if (response.status != 200 or actual.scheme != 'https' or
                actual.hostname not in ALLOWED_HOSTS):
                raise IntakeError('UNTRUSTED_SOURCE_REDIRECT')
            while True:
                if time.monotonic() >= deadline:
                    raise IntakeError('WAVE_TIME_BUDGET')
                chunk = response.read(256 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > spec['size']:
                    raise IntakeError('FILE_OVER_DECLARED_SIZE')
                digest_md5.update(chunk)
                digest_sha.update(chunk)
                out.write(chunk)
        if size != spec['size'] or digest_md5.hexdigest() != spec['md5']:
            raise IntakeError('SOURCE_HASH_OR_SIZE_MISMATCH')
        if target.suffix.lower() == '.fbx':
            if not part.read_bytes()[:32].startswith(b'Kaydara FBX Binary'):
                raise IntakeError('NOT_BINARY_FBX')
        part.replace(target)
        return {'relative_file': spec['name'], 'bytes': size, 'md5': digest_md5.hexdigest(),
                'sha256': digest_sha.hexdigest(), 'format': target.suffix.lower()}
    finally:
        part.unlink(missing_ok=True)


def stage(output: Path, *, max_total_bytes: int, single_limit: int, seconds: int,
          listing: dict | None = None, metadata_loader=read_json, file_loader=save_verified) -> dict:
    start = time.monotonic()
    deadline = start + seconds
    assets = listing if listing is not None else read_json(API + '/assets?t=models')
    if not isinstance(assets, dict):
        raise IntakeError('BAD_MODEL_LIST')
    ranked = sorted(((score_asset(slug, entry), slug, entry) for slug, entry in assets.items()
                     if isinstance(slug, str)), key=lambda x: (-x[0], x[1]))
    eligible = [(score, slug, entry) for score, slug, entry in ranked if score >= 3]
    output.mkdir(parents=True, exist_ok=True)
    accepted, quarantine = [], []
    used = 0
    for score, slug, entry in eligible:
        if time.monotonic() >= deadline - 12 or max_total_bytes - used < 1024 * 1024:
            break
        asset_dir = output / 'assets' / slug
        try:
            metadata = metadata_loader(API + '/files/' + slug)
            plan = plan_for_model(slug, metadata, single_limit=single_limit)
            required = sum(x['size'] for x in plan)
            if required > (max_total_bytes - used):
                quarantine.append({'id': slug, 'reason': 'BUDGET_SHARD_DEFER', 'planned_bytes': required})
                continue
            receipts = []
            for file in plan:
                receipts.append(file_loader(file, asset_dir / safe_relative(file['name']), deadline))
            used += required
            accepted.append({
                'id': slug, 'name': entry.get('name'), 'score': score,
                'provider_page': 'https://polyhaven.com/a/' + slug, 'license': 'CC0',
                'stage': 'SOURCE_ONLY_ORIGINAL_FORMAT_PENDING_PNG_QC',
                'bytes': required, 'files': receipts,
                'evidence_boundary': 'Native static FBX + original maps only; no UE4 import, converted PNG, LOD, collision, device or visual approval',
            })
        except (IntakeError, HTTPError, URLError, OSError, ValueError, TimeoutError) as error:
            quarantine.append({'id': slug, 'reason': type(error).__name__ + ':' + str(error)[:150]})
            if asset_dir.exists():
                shutil.rmtree(asset_dir)
    result = {
        'schema_version': 1, 'packet': 'P1C01_ADAPTIVE_POLYHAVEN_SOURCE_INTAKE_V1',
        'source': 'https://api.polyhaven.com/assets?t=models',
        'credit': 'Powered by Poly Haven', 'license': 'CC0',
        'mode': 'HOSTED_SOURCE_ONLY_NO_UNREAL_NO_PERSISTENT_WAREHOUSE_MUTATION',
        'source_assets_eligible': len(eligible),
        'source_assets_staged': len(accepted),
        'source_assets_quarantined_or_deferred': len(quarantine),
        'source_bytes_staged': used, 'max_source_bytes': max_total_bytes,
        'max_single_file_bytes': single_limit, 'seconds_budget': seconds,
        'source_library_stage': 'SOURCE_STAGED_ONLY',
        'evidence_boundary': 'Source hashes and files; not converted, optimized, UE imported, visually accepted, PIE or device tested.',
        'accepted': accepted, 'quarantine_or_deferred': quarantine,
    }
    (output / 'p1c01_adaptive_polyhaven_receipt.json').write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f"P1C01_ADAPTIVE_SOURCE_STAGE eligible={len(eligible)} staged={len(accepted)} "
          f"files={sum(len(x['files']) for x in accepted)} bytes={used} "
          f"quarantine={len(quarantine)}; NOT_UE4_IMPORTED", flush=True)
    return result


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--max-total-mb', type=int, default=240)
    p.add_argument('--max-single-mb', type=int, default=30)
    p.add_argument('--max-seconds', type=int, default=420)
    args = p.parse_args()
    if not 1 <= args.max_total_mb <= 512 or not 1 <= args.max_single_mb <= 30 or not 20 <= args.max_seconds <= 900:
        raise SystemExit('SOURCE_STAGE_RESOURCE_BUDGET_INVALID')
    result = stage(args.output, max_total_bytes=args.max_total_mb * 1024**2,
                   single_limit=args.max_single_mb * 1024**2, seconds=args.max_seconds)
    # No falsely-green empty artifact: if all source models are rejected,
    # a receipt still exists but the source lane reports failure for diagnosis.
    return 0 if result['source_assets_staged'] > 0 else 2


if __name__ == '__main__':
    raise SystemExit(main())
