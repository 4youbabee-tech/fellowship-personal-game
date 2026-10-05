import argparse
import hashlib
import json
import math
import os
import re
import sys
import zipfile

import bpy
from mathutils import Matrix

argv = sys.argv
argv = argv[argv.index('--') + 1:] if '--' in argv else []
parser = argparse.ArgumentParser()
parser.add_argument('--manifest', required=True)
parser.add_argument('--human-receipt', required=True)
parser.add_argument('--human-root', required=True)
parser.add_argument('--animation-archive', required=True)
parser.add_argument('--output-root', required=True)
parser.add_argument('--receipt', required=True)
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


def compact(name):
    return re.sub(r'[^a-z0-9]+', '', str(name).lower())


def side_match(name, side):
    raw = str(name).lower()
    if side == 'L':
        return 'left' in raw or '.l' in raw or '_l' in raw or '-l' in raw or raw.endswith(' l')
    if side == 'R':
        return 'right' in raw or '.r' in raw or '_r' in raw or '-r' in raw or raw.endswith(' r')
    return True


def bone_map(armature):
    bones = list(armature.data.bones)

    def find(tokens, side=None, exclude=()):
        rows = []
        for bone in bones:
            packed = compact(bone.name)
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


def require_semantics(mapping, label):
    missing = sorted(k for k, v in mapping.items() if not v)
    if missing:
        raise RuntimeError(label + '_SEMANTIC_BONES_MISSING ' + ','.join(missing))


def is_descendant(armature, child_name, parent_name):
    child = armature.data.bones.get(child_name)
    parent = armature.data.bones.get(parent_name)
    if child is None or parent is None:
        return False
    node = child.parent
    while node is not None:
        if node == parent:
            return True
        node = node.parent
    return False


def hierarchy_receipt(armature, mapping):
    result = {
        'left_arm': is_descendant(armature, mapping['left_forearm'], mapping['left_upper_arm']) and is_descendant(armature, mapping['left_hand'], mapping['left_forearm']),
        'right_arm': is_descendant(armature, mapping['right_forearm'], mapping['right_upper_arm']) and is_descendant(armature, mapping['right_hand'], mapping['right_forearm']),
        'left_leg': is_descendant(armature, mapping['left_shin'], mapping['left_thigh']) and is_descendant(armature, mapping['left_foot'], mapping['left_shin']),
        'right_leg': is_descendant(armature, mapping['right_shin'], mapping['right_thigh']) and is_descendant(armature, mapping['right_foot'], mapping['right_shin']),
        'spine_head': is_descendant(armature, mapping['head'], mapping['spine']),
    }
    if not all(result.values()):
        raise RuntimeError('RETARGET_HIERARCHY_FAIL ' + ','.join(k for k, v in result.items() if not v))
    return result


def extract_exact_member(archive, member_name, dest, max_bytes):
    with zipfile.ZipFile(archive, 'r') as zf:
        matches = [x for x in zf.infolist() if x.filename.replace('\\', '/') == member_name]
        if len(matches) != 1:
            raise RuntimeError('RETARGET_SOURCE_MEMBER_FAIL count=%d member=%s' % (len(matches), member_name))
        info = matches[0]
        if info.file_size <= 0 or info.file_size > max_bytes:
            raise RuntimeError('RETARGET_SOURCE_MEMBER_SIZE_FAIL bytes=%d' % info.file_size)
        parts = [p for p in member_name.split('/') if p]
        if '..' in parts or member_name.startswith('/'):
            raise RuntimeError('RETARGET_SOURCE_MEMBER_PATH_UNSAFE')
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with zf.open(info, 'r') as src, open(dest, 'wb') as out:
            while True:
                chunk = src.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
    return info.file_size


def action_by_leaf(expected_leaf):
    rows = []
    for action in bpy.data.actions:
        leaf = str(action.name).split('|')[-1]
        if compact(leaf) == compact(expected_leaf):
            rows.append(action)
    if len(rows) != 1:
        raise RuntimeError('RETARGET_SOURCE_ACTION_FAIL action=%s count=%d' % (expected_leaf, len(rows)))
    return rows[0]


def reset_pose(armature):
    for pb in armature.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()


def capture_source_clip(armature, mapping, action, frame_start, frame_end):
    armature.animation_data_create()
    armature.animation_data.action = action
    captured = []
    motion = {key: 0.0 for key in mapping}
    for frame in range(frame_start, frame_end + 1):
        bpy.context.scene.frame_set(frame)
        row = {'frame': frame, 'bones': {}}
        for semantic, bone_name in mapping.items():
            pb = armature.pose.bones[bone_name]
            quat = pb.matrix_basis.to_quaternion().normalized()
            row['bones'][semantic] = [float(quat.w), float(quat.x), float(quat.y), float(quat.z)]
            motion[semantic] = max(motion[semantic], float(quat.angle))
        captured.append(row)
    armature.animation_data.action = None
    reset_pose(armature)
    return captured, motion


def evaluated_points(meshes):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    points = []
    for obj in meshes:
        evaluated = obj.evaluated_get(depsgraph)
        temp = evaluated.to_mesh()
        try:
            for vertex in temp.vertices:
                p = evaluated.matrix_world @ vertex.co
                points.append((float(p.x), float(p.y), float(p.z)))
        finally:
            evaluated.to_mesh_clear()
    return points


def point_metrics(points):
    if not points:
        raise RuntimeError('RETARGET_TARGET_POINTS_MISSING')
    finite = all(math.isfinite(v) for p in points for v in p)
    mins = [min(p[i] for p in points) for i in range(3)]
    maxs = [max(p[i] for p in points) for i in range(3)]
    diag = math.sqrt(sum((maxs[i] - mins[i]) ** 2 for i in range(3)))
    return {'finite': finite, 'min': mins, 'max': maxs, 'diag': diag, 'vertex_count': len(points)}


def max_point_displacement(a, b):
    if len(a) != len(b):
        raise RuntimeError('RETARGET_VERTEX_COUNT_CHANGED')
    return max(math.sqrt(sum((a[i][axis] - b[i][axis]) ** 2 for axis in range(3))) for i in range(len(a)))


def apply_clip_to_target(armature, mapping, clip_name, frames, meshes, rest_points, rest_metrics, policy, out_path):
    action = bpy.data.actions.new(name='Frodo_' + clip_name + '_Retarget')
    armature.animation_data_create()
    armature.animation_data.action = action
    reset_pose(armature)
    for row in frames:
        frame = int(row['frame'])
        bpy.context.scene.frame_set(frame)
        for semantic, values in row['bones'].items():
            pb = armature.pose.bones[mapping[semantic]]
            pb.rotation_mode = 'QUATERNION'
            pb.rotation_quaternion = values
            pb.keyframe_insert(data_path='rotation_quaternion', frame=frame, group=pb.name)
    for curve in action.fcurves:
        for key in curve.keyframe_points:
            key.interpolation = 'LINEAR'

    sample_frames = sorted(set([frames[0]['frame'], frames[-1]['frame']] + [row['frame'] for row in frames[::max(1, len(frames)//8)]]))
    samples = []
    max_disp = 0.0
    max_ratio = 0.0
    min_ratio = 999.0
    for frame in sample_frames:
        bpy.context.scene.frame_set(int(frame))
        points = evaluated_points(meshes)
        metrics = point_metrics(points)
        if not metrics['finite']:
            raise RuntimeError('RETARGET_NONFINITE_BOUNDS clip=' + clip_name)
        ratio = metrics['diag'] / rest_metrics['diag'] if rest_metrics['diag'] > 0 else 999.0
        disp = max_point_displacement(rest_points, points)
        max_disp = max(max_disp, disp)
        max_ratio = max(max_ratio, ratio)
        min_ratio = min(min_ratio, ratio)
        samples.append({'frame': int(frame), 'bounds_ratio': ratio, 'max_vertex_displacement_from_rest': disp})
    min_required = max(rest_metrics['diag'] * float(policy['min_displacement_ratio']), 1e-6)
    if max_disp < min_required:
        raise RuntimeError('RETARGET_NO_NONTRIVIAL_TARGET_DEFORMATION clip=%s displacement=%s required=%s' % (clip_name, max_disp, min_required))
    if min_ratio < float(policy['min_bounds_ratio']) or max_ratio > float(policy['max_bounds_ratio']):
        raise RuntimeError('RETARGET_BOUNDS_RATIO_FAIL clip=%s min=%s max=%s' % (clip_name, min_ratio, max_ratio))

    first_frame = int(frames[0]['frame'])
    last_frame = int(frames[-1]['frame'])
    bpy.context.scene.frame_set(first_frame)
    first_points = evaluated_points(meshes)
    bpy.context.scene.frame_set(last_frame)
    last_points = evaluated_points(meshes)
    loop_delta = max_point_displacement(first_points, last_points)
    loop_ratio = loop_delta / rest_metrics['diag'] if rest_metrics['diag'] > 0 else 999.0

    bpy.ops.object.select_all(action='DESELECT')
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.context.scene.frame_start = first_frame
    bpy.context.scene.frame_end = last_frame
    bpy.ops.export_scene.fbx(
        filepath=out_path,
        use_selection=True,
        object_types={'ARMATURE'},
        add_leaf_bones=False,
        use_armature_deform_only=True,
        bake_anim=True,
        bake_anim_use_all_bones=True,
        bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=False,
        bake_anim_force_startend_keying=True,
        bake_anim_simplify_factor=0.0,
        path_mode='AUTO',
        axis_forward='-Z',
        axis_up='Y',
    )
    if not os.path.isfile(out_path) or os.path.getsize(out_path) <= 0:
        raise RuntimeError('RETARGET_DERIVATIVE_EXPORT_FAIL clip=' + clip_name)
    result = {
        'action': action.name,
        'frame_start': first_frame,
        'frame_end': last_frame,
        'frame_count': len(frames),
        'sample_count': len(sample_frames),
        'max_target_vertex_displacement': max_disp,
        'min_required_displacement': min_required,
        'min_bounds_ratio': min_ratio,
        'max_bounds_ratio': max_ratio,
        'loop_endpoint_displacement_ratio': loop_ratio,
        'samples': samples,
        'derivative_file': os.path.basename(out_path),
        'derivative_bytes': os.path.getsize(out_path),
        'derivative_sha256': sha256_file(out_path),
    }
    armature.animation_data.action = None
    reset_pose(armature)
    return result


def verify_derivative(path, required_semantic_count):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    result = bpy.ops.import_scene.fbx(filepath=path, use_custom_normals=True)
    if 'FINISHED' not in result:
        raise RuntimeError('RETARGET_DERIVATIVE_REIMPORT_FAIL file=' + path)
    arms = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
    if len(arms) != 1:
        raise RuntimeError('RETARGET_DERIVATIVE_ARMATURE_COUNT_FAIL file=' + path)
    mapping = bone_map(arms[0])
    coverage = sum(1 for v in mapping.values() if v)
    actions = []
    for action in bpy.data.actions:
        start, end = action.frame_range
        if len(action.fcurves) > 0 and end > start:
            actions.append({'name': action.name, 'frame_start': float(start), 'frame_end': float(end), 'fcurves': len(action.fcurves)})
    if coverage < required_semantic_count or not actions:
        raise RuntimeError('RETARGET_DERIVATIVE_CONTENT_FAIL coverage=%d actions=%d' % (coverage, len(actions)))
    return {'armature_bones': len(arms[0].data.bones), 'semantic_coverage': coverage, 'actions': actions}


manifest = load_json(args.manifest)
human = load_json(args.human_receipt)
policy = manifest['retarget_policy']
expected_target_sha = manifest['target']['normalized_sha256'].lower()
expected_archive_sha = manifest['source']['archive_sha256'].lower()
expected_source_fbx_sha = manifest['source']['unreal_fbx_sha256'].lower()

if sha256_file(args.animation_archive) != expected_archive_sha:
    raise RuntimeError('RETARGET_ARCHIVE_SHA256_FAIL')

candidate = None
for row in human.get('normalized_candidates', []):
    if str(row.get('normalized_sha256', '')).lower() == expected_target_sha:
        candidate = row
        break
if candidate is None:
    raise RuntimeError('RETARGET_EXACT_TARGET_WINNER_MISSING')
target_path = os.path.join(args.human_root, str(candidate['normalized_relative_path']).replace('/', os.sep))
if not os.path.isfile(target_path):
    raise RuntimeError('RETARGET_TARGET_FBX_MISSING')
if sha256_file(target_path) != expected_target_sha:
    raise RuntimeError('RETARGET_TARGET_SHA256_FAIL')

os.makedirs(args.output_root, exist_ok=True)
source_fbx = os.path.join(args.output_root, 'AL_Standard.fbx')
extract_exact_member(args.animation_archive, manifest['source']['archive_member'], source_fbx, int(policy['max_source_fbx_bytes']))
if sha256_file(source_fbx) != expected_source_fbx_sha:
    raise RuntimeError('RETARGET_SOURCE_FBX_SHA256_FAIL')

bpy.ops.wm.read_factory_settings(use_empty=True)
result = bpy.ops.import_scene.fbx(filepath=source_fbx, use_custom_normals=True)
if 'FINISHED' not in result:
    raise RuntimeError('RETARGET_SOURCE_FBX_IMPORT_FAIL')
source_arms = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
if len(source_arms) != 1:
    raise RuntimeError('RETARGET_SOURCE_ARMATURE_COUNT_FAIL count=%d' % len(source_arms))
source_arm = source_arms[0]
source_map = bone_map(source_arm)
require_semantics(source_map, 'RETARGET_SOURCE')
source_hierarchy = hierarchy_receipt(source_arm, source_map)
source_clips = {}
for role, clip in manifest['clips'].items():
    action = action_by_leaf(clip['action_leaf'])
    start, end = action.frame_range
    start_i = int(round(float(start)))
    end_i = int(round(float(end)))
    if end_i <= start_i or end_i - start_i > int(policy['max_clip_frames']):
        raise RuntimeError('RETARGET_SOURCE_FRAME_RANGE_FAIL role=%s start=%s end=%s' % (role, start_i, end_i))
    captured, motion = capture_source_clip(source_arm, source_map, action, start_i, end_i)
    moving = sorted(k for k, v in motion.items() if v >= math.radians(float(policy['min_source_motion_degrees'])))
    if len(moving) < int(policy['min_moving_semantic_bones']):
        raise RuntimeError('RETARGET_SOURCE_MOTION_FAIL role=%s moving=%d' % (role, len(moving)))
    source_clips[role] = {
        'source_action': action.name,
        'action_leaf': clip['action_leaf'],
        'frame_start': start_i,
        'frame_end': end_i,
        'frame_count': len(captured),
        'max_semantic_motion_radians': motion,
        'moving_semantic_bones': moving,
        'frames': captured,
    }

bpy.ops.wm.read_factory_settings(use_empty=True)
result = bpy.ops.import_scene.fbx(filepath=target_path, use_custom_normals=True)
if 'FINISHED' not in result:
    raise RuntimeError('RETARGET_TARGET_FBX_IMPORT_FAIL')
target_arms = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
target_meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
if len(target_arms) != 1 or not target_meshes:
    raise RuntimeError('RETARGET_TARGET_SCENE_FAIL arms=%d meshes=%d' % (len(target_arms), len(target_meshes)))
target_arm = target_arms[0]
target_map = bone_map(target_arm)
require_semantics(target_map, 'RETARGET_TARGET')
target_hierarchy = hierarchy_receipt(target_arm, target_map)
if target_arm.animation_data:
    target_arm.animation_data.action = None
reset_pose(target_arm)
rest_points = evaluated_points(target_meshes)
rest_metrics = point_metrics(rest_points)
if not rest_metrics['finite'] or rest_metrics['diag'] <= 1e-6:
    raise RuntimeError('RETARGET_TARGET_REST_BOUNDS_FAIL')

clip_results = {}
derivative_paths = []
for role in ('idle', 'walk', 'run'):
    clip = source_clips[role]
    out_path = os.path.join(args.output_root, 'Frodo_%s_Retarget.fbx' % role.capitalize())
    result = apply_clip_to_target(
        target_arm,
        target_map,
        role.capitalize(),
        clip['frames'],
        target_meshes,
        rest_points,
        rest_metrics,
        policy,
        out_path,
    )
    clip_results[role] = result
    derivative_paths.append((role, out_path))

derivative_verification = {}
for role, path in derivative_paths:
    derivative_verification[role] = verify_derivative(path, len(target_map))

receipt = {
    'schema_version': 1,
    'status': 'HOSTED_RETARGET_TECHNICAL_PASS',
    'target': {
        'source_entry': candidate.get('source_entry'),
        'normalized_sha256': expected_target_sha,
        'normalized_bytes': os.path.getsize(target_path),
        'semantic_bones': target_map,
        'hierarchy': target_hierarchy,
        'rest_bounds': rest_metrics,
    },
    'source': {
        'archive_sha256': expected_archive_sha,
        'unreal_fbx_sha256': expected_source_fbx_sha,
        'archive_member': manifest['source']['archive_member'],
        'semantic_bones': source_map,
        'hierarchy': source_hierarchy,
    },
    'source_clips': {k: {kk: vv for kk, vv in v.items() if kk != 'frames'} for k, v in source_clips.items()},
    'retargeted_clips': clip_results,
    'derivative_verification': derivative_verification,
    'retarget_technical_pass': True,
    'retarget_visual_accepted': False,
    'ue4_animation_imported': False,
    'anim_bp_allowed': False,
    'runtime_integration_allowed': False,
    'evidence_boundary': 'Hosted Blender technical retarget only: exact source/target identities, semantic hierarchy, source motion, nonzero target mesh deformation, finite bounds, and re-importable animation-only FBX derivatives. No UE4 animation import, AnimBP, runtime, PIE, device, visual or performance acceptance.',
    'next_gate': 'UE4.27 animation-only import against the exact Rogue USkeleton, then AnimBP locomotion and fresh runtime visual review.'
}
os.makedirs(os.path.dirname(os.path.abspath(args.receipt)), exist_ok=True)
with open(args.receipt, 'w', encoding='utf-8') as f:
    json.dump(receipt, f, indent=2, sort_keys=True)
print('P1C01_FRODO_HOSTED_RETARGET_PASS target=%s idle=%s walk=%s run=%s' % (
    expected_target_sha,
    clip_results['idle']['derivative_sha256'],
    clip_results['walk']['derivative_sha256'],
    clip_results['run']['derivative_sha256'],
))
