import argparse
import hashlib
import json
import os
import re
import sys
import zipfile

import bpy

argv = sys.argv
argv = argv[argv.index('--') + 1:] if '--' in argv else []
parser = argparse.ArgumentParser()
parser.add_argument('--manifest', required=True)
parser.add_argument('--archive', required=True)
parser.add_argument('--work-root', required=True)
parser.add_argument('--output', required=True)
args = parser.parse_args(argv)


def load_json(path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest().lower()


def norm(value):
    return re.sub(r'[^a-z0-9]+', '', str(value).lower())


def safe_extract_zip(archive, dest, policy):
    os.makedirs(dest, exist_ok=True)
    max_entries = int(policy.get('max_archive_entries', 5000))
    max_entry_bytes = int(policy.get('max_entry_bytes', 256 * 1024 * 1024))
    max_expanded_bytes = int(policy.get('max_expanded_bytes', 1024 * 1024 * 1024))
    forbidden = {'.exe', '.msi', '.cmd', '.bat', '.ps1', '.vbs', '.js', '.scr', '.com', '.bmp'}
    count = 0
    expanded = 0
    extracted = []
    ignored_obj = []
    with zipfile.ZipFile(archive, 'r') as zf:
        for info in zf.infolist():
            count += 1
            if count > max_entries:
                raise RuntimeError('ANIM_ARCHIVE_ENTRY_BUDGET_FAIL')
            name = info.filename.replace('\\', '/')
            parts = [p for p in name.split('/') if p]
            if name.startswith('/') or re.match(r'^[A-Za-z]:', name) or '..' in parts:
                raise RuntimeError('ANIM_ARCHIVE_PATH_UNSAFE entry=' + name)
            if info.file_size > max_entry_bytes or expanded + info.file_size > max_expanded_bytes:
                raise RuntimeError('ANIM_ARCHIVE_EXPANDED_BUDGET_FAIL entry=' + name)
            ext = os.path.splitext(name)[1].lower()
            if ext in forbidden:
                raise RuntimeError('ANIM_ARCHIVE_FORBIDDEN_EXTENSION entry=' + name)
            expanded += int(info.file_size)
            if info.is_dir():
                continue
            if ext == '.obj':
                ignored_obj.append(name)
                continue
            target = os.path.abspath(os.path.join(dest, *parts))
            root = os.path.abspath(dest) + os.sep
            if not target.startswith(root):
                raise RuntimeError('ANIM_ARCHIVE_PATH_ESCAPE entry=' + name)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with zf.open(info, 'r') as src, open(target, 'wb') as out:
                while True:
                    chunk = src.read(1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
            extracted.append((name, target, int(info.file_size)))
    return {
        'entry_count': count,
        'expanded_bytes': expanded,
        'ignored_obj_entries': ignored_obj,
        'extracted': extracted,
    }


def side_match(name, side):
    raw = name.lower()
    if side == 'L':
        return 'left' in raw or '.l' in raw or '_l' in raw or '-l' in raw or raw.endswith(' l')
    if side == 'R':
        return 'right' in raw or '.r' in raw or '_r' in raw or '-r' in raw or raw.endswith(' r')
    return True


def semantic_bone_map(arm):
    bones = list(arm.data.bones)

    def find(tokens, side=None, exclude=()):
        rows = []
        for bone in bones:
            packed = norm(bone.name)
            if side and not side_match(bone.name, side):
                continue
            if any(x in packed for x in exclude):
                continue
            if any(token in packed for token in tokens):
                rows.append((len(bone.name), bone.name.lower(), bone.name))
        return sorted(rows)[0][2] if rows else None

    return {
        'pelvis': find(('pelvis', 'hips', 'hip')),
        'spine': find(('spine', 'chest')),
        'head': find(('head',)),
        'left_upper_arm': find(('upperarm', 'uparm'), 'L', ('forearm', 'lowerarm')),
        'right_upper_arm': find(('upperarm', 'uparm'), 'R', ('forearm', 'lowerarm')),
        'left_forearm': find(('forearm', 'lowerarm'), 'L'),
        'right_forearm': find(('forearm', 'lowerarm'), 'R'),
        'left_hand': find(('hand',), 'L'),
        'right_hand': find(('hand',), 'R'),
        'left_thigh': find(('thigh', 'upleg', 'upperleg'), 'L'),
        'right_thigh': find(('thigh', 'upleg', 'upperleg'), 'R'),
        'left_shin': find(('shin', 'calf', 'lowerleg'), 'L'),
        'right_shin': find(('shin', 'calf', 'lowerleg'), 'R'),
        'left_foot': find(('foot',), 'L'),
        'right_foot': find(('foot',), 'R'),
    }


def inspect_fbx(path, relative):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    result = bpy.ops.import_scene.fbx(filepath=path, use_custom_normals=True)
    if 'FINISHED' not in result:
        return {'file': relative, 'imported': False, 'reason': 'FBX_IMPORT_FAILED'}
    arms = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
    actions = []
    for action in bpy.data.actions:
        start, end = action.frame_range
        actions.append({
            'name': action.name,
            'frame_start': float(start),
            'frame_end': float(end),
            'frame_span': float(end - start),
            'fcurves': len(action.fcurves),
        })
    arm_rows = []
    for arm in arms:
        mapping = semantic_bone_map(arm)
        arm_rows.append({
            'name': arm.name,
            'bone_count': len(arm.data.bones),
            'semantic_bones': mapping,
            'semantic_coverage': sum(1 for v in mapping.values() if v),
        })
    return {
        'file': relative,
        'imported': True,
        'armature_count': len(arms),
        'armatures': arm_rows,
        'actions': actions,
    }


def choose_role(role, spec, inventory, preferred_path_tokens):
    tokens = [norm(x) for x in spec.get('preferred_tokens', []) if norm(x)]
    path_tokens = [norm(x) for x in preferred_path_tokens if norm(x)]
    rows = []
    for fbx in inventory:
        if not fbx.get('imported') or fbx.get('armature_count', 0) < 1:
            continue
        file_key = norm(os.path.basename(fbx['file']))
        file_stem = norm(os.path.splitext(os.path.basename(fbx['file']))[0])
        full_path_key = norm(fbx['file'])
        variant_rank = len(path_tokens)
        for i, path_token in enumerate(path_tokens):
            if path_token in full_path_key:
                variant_rank = i
                break
        actions = fbx.get('actions') or []
        if not actions:
            actions = [{'name': os.path.splitext(os.path.basename(fbx['file']))[0], 'frame_start': 0.0, 'frame_end': 0.0, 'frame_span': 0.0, 'fcurves': 0}]
        for action in actions:
            action_leaf = str(action.get('name', '')).split('|')[-1]
            action_key = norm(action_leaf)
            match_mode = None
            token_rank = None
            matched = None
            for i, token in enumerate(tokens):
                if action_key == token:
                    match_mode, token_rank, matched = 0, i, token
                    break
            if match_mode is None:
                for i, token in enumerate(tokens):
                    if file_stem == token:
                        match_mode, token_rank, matched = 1, i, token
                        break
            if match_mode is None:
                combined = file_key + action_key
                for i, token in enumerate(tokens):
                    if token and token in combined:
                        match_mode, token_rank, matched = 2, i, token
                        break
            if match_mode is None:
                continue
            animated = float(action.get('frame_span', 0.0)) > 0.0 and int(action.get('fcurves', 0)) > 0
            coverage = max([int(a.get('semantic_coverage', 0)) for a in fbx.get('armatures', [])] or [0])
            rows.append((match_mode, token_rank, variant_rank, 0 if animated else 1, -coverage, fbx['file'], action.get('name', ''), {
                'role': role,
                'file': fbx['file'],
                'action': action.get('name', ''),
                'action_leaf': action_leaf,
                'matched_token': matched,
                'match_mode': ['EXACT_ACTION_LEAF', 'EXACT_FILE_STEM', 'BOUNDED_TOKEN_FALLBACK'][match_mode],
                'variant_rank': variant_rank,
                'animated': animated,
                'frame_start': action.get('frame_start'),
                'frame_end': action.get('frame_end'),
                'frame_span': action.get('frame_span'),
                'fcurves': action.get('fcurves'),
                'max_semantic_coverage': coverage,
            }))
    rows.sort(key=lambda x: x[:-1])
    return rows[0][-1] if rows else None


manifest = load_json(args.manifest)
source = manifest['animation_source']
policy = manifest['archive_policy']
archive_bytes = os.path.getsize(args.archive)
minimum = int(policy['minimum_archive_bytes'])
maximum = int(policy['maximum_archive_bytes'])
if archive_bytes < minimum or archive_bytes > maximum:
    raise RuntimeError('ANIM_ARCHIVE_SIZE_FAIL bytes=%d min=%d max=%d' % (archive_bytes, minimum, maximum))
archive_sha = sha256_file(args.archive)
expected_sha = str(source.get('expected_sha256') or '').lower().strip()
if expected_sha and archive_sha != expected_sha:
    raise RuntimeError('ANIM_ARCHIVE_SHA256_FAIL actual=%s expected=%s' % (archive_sha, expected_sha))

extract_root = os.path.join(args.work_root, 'extracted')
scan = safe_extract_zip(args.archive, extract_root, policy)
fbx_entries = [(rel, path, size) for rel, path, size in scan['extracted'] if os.path.splitext(rel)[1].lower() == '.fbx']
if not fbx_entries:
    raise RuntimeError('ANIMATION_SOURCE_FBX_MISSING')
if len(fbx_entries) > int(policy.get('max_fbx_files', 96)):
    raise RuntimeError('ANIMATION_SOURCE_FBX_COUNT_FAIL count=%d' % len(fbx_entries))

inventory = []
for relative, path, size in fbx_entries:
    row = inspect_fbx(path, relative)
    row['bytes'] = size
    row['sha256'] = sha256_file(path)
    inventory.append(row)

selected = {}
preferred_path_tokens = manifest.get('source_selection_policy', {}).get('preferred_fbx_path_tokens', [])
for role, spec in manifest['required_clips'].items():
    selected[role] = choose_role(role, spec, inventory, preferred_path_tokens)
missing = sorted([role for role, row in selected.items() if row is None or not row.get('animated')])
status = 'ANIMATION_SOURCE_INVENTORY_PASS' if not missing else 'ANIMATION_SOURCE_INVENTORY_REJECT'

receipt = {
    'schema_version': 1,
    'status': status,
    'source': {
        'provider': source['provider'],
        'creator': source['creator'],
        'source_page': source['source_page'],
        'download_url': source['download_url'],
        'license': source['observed_license'],
        'archive_file': os.path.basename(args.archive),
        'archive_bytes': archive_bytes,
        'archive_sha256': archive_sha,
        'sha_pinned_in_manifest': bool(expected_sha),
    },
    'archive_scan': {
        'entry_count': scan['entry_count'],
        'expanded_bytes': scan['expanded_bytes'],
        'fbx_count': len(fbx_entries),
        'ignored_obj_entries': scan['ignored_obj_entries'],
    },
    'fbx_inventory': inventory,
    'selected_clips': selected,
    'missing_required_clips': missing,
    'animated_character_format': 'FBX_ONLY',
    'retarget_accepted': False,
    'anim_bp_allowed': False,
    'runtime_integration_allowed': False,
    'evidence_boundary': 'Hosted public-source receipt, safe archive scan, FBX/action inventory and required Idle/Walk/Run discovery only. No retarget, UE4 animation import, AnimBP, runtime, PIE, device, visual or FPS acceptance.',
    'next_gate': 'Pin observed archive SHA256, then prove Idle/Walk/Run retarget compatibility against the exact Rogue technical winner with nonzero target deformation.'
}
os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
with open(args.output, 'w', encoding='utf-8') as f:
    json.dump(receipt, f, indent=2, sort_keys=True)
print('P1C01_FRODO_ANIMATION_SOURCE_%s sha256=%s fbx=%d selected=%s' % (
    'PASS' if status.endswith('_PASS') else 'REJECT',
    archive_sha,
    len(fbx_entries),
    ','.join(sorted(k for k, v in selected.items() if v)),
))
if missing:
    raise RuntimeError('ANIMATION_REQUIRED_CLIPS_MISSING roles=' + ','.join(missing))
