"""Normalize the pinned CC0 KayKit Rogue into a unified UE4 source packet.

Run with Blender --python-exit-code 93 --python this_file -- --source-fbx ...
--texture ... --license ... --out ... . Does not promote runtime acceptance.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree

SOURCE_SHA = '93a9ee0a67ae69b2d815050234acad2004c3b8af7d294b916e52609c8195eb71'
TEXTURE_SHA = 'a4032e877c3b91939f5cdbb630349c1998fdbc3211bbd587c111125500fe4cc5'
LICENSE_SHA = 'ae322141814056dda0deea7540d74c41d87aee1da319977cd1bd84ee5a923629'
SOURCE_COMMIT = '672074b73ba276876a19e8816ecdc5241817ab47'
CLIPS = {'Idle': 'Rig|Idle', 'Walk': 'Rig|Walking_A',
         'Run': 'Rig|Running_A', 'Talk': 'Rig|Interact'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def points(obj):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        return [evaluated.matrix_world @ v.co for v in mesh.vertices]
    finally:
        evaluated.to_mesh_clear()


def geometry_error(expected, actual):
    if not expected or len(expected) != len(actual):
        raise RuntimeError('KAYKIT_VERTEX_CORRESPONDENCE_FAILED')
    if not all(math.isfinite(v) for p in expected + actual for v in p):
        raise RuntimeError('KAYKIT_NONFINITE_GEOMETRY')
    diagonal = Vector(tuple(max(p[k] for p in expected) - min(p[k] for p in expected)
                            for k in range(3))).length
    if diagonal <= 0:
        raise RuntimeError('KAYKIT_EMPTY_BOUNDS')
    # Joining/reimport can reorder vertices. Check both directions, same count.
    errors = []
    for a, b in ((expected, actual), (actual, expected)):
        tree = KDTree(len(b))
        for index, point in enumerate(b):
            tree.insert(point, index)
        tree.balance()
        errors.append(max(tree.find(point)[2] for point in a))
    error = max(errors)
    tolerance = max(1e-6, diagonal * 1e-4)
    if error > tolerance:
        raise RuntimeError('KAYKIT_GEOMETRY_CHANGED error=%r tolerance=%r' % (error, tolerance))
    return {'max_error': error, 'tolerance': tolerance}


def skin_metrics(arm, mesh):
    names = {b.name for b in arm.data.bones if b.use_deform}
    groups = {g.index: g.name for g in mesh.vertex_groups}
    counts = [sum(g.weight > 1e-6 and groups[g.group] in names for g in vertex.groups)
              for vertex in mesh.data.vertices]
    if not counts or min(counts) < 1 or max(counts) > 4:
        raise RuntimeError('KAYKIT_SKIN_BUDGET_FAILED')
    if not any(m.type == 'ARMATURE' and m.object == arm for m in mesh.modifiers):
        raise RuntimeError('KAYKIT_BINDING_MISSING')
    return {'vertices': len(counts), 'max_influences': max(counts),
            'zero_weight_vertices': sum(n == 0 for n in counts),
            'triangles': sum(len(p.vertices) - 2 for p in mesh.data.polygons)}


def signature(arm):
    rows = [(b.name, b.parent.name if b.parent else None,
             [round(float(v), 5) for row in b.matrix_local for v in row])
            for b in sorted(arm.data.bones, key=lambda bone: bone.name)]
    return hashlib.sha256(json.dumps(rows).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    for name in ('source-fbx', 'texture', 'license', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    source, texture, license_file = args.source_fbx.resolve(), args.texture.resolve(), args.license.resolve()
    for path, required in ((source, SOURCE_SHA), (texture, TEXTURE_SHA), (license_file, LICENSE_SHA)):
        if digest(path) != required:
            raise RuntimeError('KAYKIT_PINNED_SOURCE_HASH_MISMATCH ' + path.name)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(source))
    scene = bpy.context.scene
    arms = [o for o in scene.objects if o.type == 'ARMATURE']
    if len(arms) != 1 or len(arms[0].data.bones) != 41:
        raise RuntimeError('KAYKIT_PINNED_SKELETON_CHANGED')
    arm = arms[0]
    for name in CLIPS.values():
        if name not in bpy.data.actions:
            raise RuntimeError('KAYKIT_AUTHORED_CLIP_MISSING ' + name)
    arm.animation_data.action = bpy.data.actions[CLIPS['Idle']]
    scene.frame_set(1)
    body = [o for o in scene.objects if o.type == 'MESH' and o.name.startswith('Rogue_')]
    if {o.name for o in body} != {'Rogue_Cape', 'Rogue_Head', 'Rogue_Body',
            'Rogue_ArmLeft', 'Rogue_ArmRight', 'Rogue_LegLeft', 'Rogue_LegRight'}:
        raise RuntimeError('KAYKIT_BODY_INVENTORY_CHANGED')
    original = [point for obj in body for point in points(obj)]
    arm.data.pose_position = 'REST'
    bpy.context.view_layer.update()
    # Existing rigid chest cape becomes equivalent one-bone skin in rest space.
    # All six authored body skins retain original weights; no automatic binding.
    for obj in body:
        if obj.parent_type == 'BONE':
            if obj.name != 'Rogue_Cape' or obj.parent_bone != 'chest':
                raise RuntimeError('KAYKIT_UNEXPECTED_RIGID_ATTACHMENT')
            matrix = obj.matrix_world.copy()
            obj.parent_type, obj.parent = 'OBJECT', arm
            obj.matrix_world = matrix
            obj.vertex_groups.new(name='chest').add(list(range(len(obj.data.vertices))), 1.0, 'REPLACE')
            obj.modifiers.new('Armature', 'ARMATURE').object = arm
    removed = []
    for obj in list(scene.objects):
        if obj.type == 'MESH' and obj not in body:
            if obj.name not in {'Knife_Offhand', '1H_Crossbow', 'Throwable', 'Knife', '2H_Crossbow'}:
                raise RuntimeError('KAYKIT_UNEXPECTED_NONBODY_MESH ' + obj.name)
            removed.append(obj.name)
            bpy.data.objects.remove(obj, do_unlink=True)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in body:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = next(o for o in body if o.name == 'Rogue_Body')
    bpy.ops.object.join()
    mesh = bpy.context.object
    mesh.name = 'SK_KayKit_Rogue_SourceCandidate'
    arm.data.pose_position = 'POSE'
    bpy.context.view_layer.update()
    join_proof = geometry_error(original, points(mesh))
    skin = skin_metrics(arm, mesh)
    portable_atlas = out / 'rogue_texture.png'
    shutil.copyfile(texture, portable_atlas)
    linked_images = []
    for image in bpy.data.images:
        if image.source == 'FILE':
            image.filepath = str(portable_atlas)
            image.reload()
            if len(image.pixels) < 4:
                raise RuntimeError('KAYKIT_TEXTURE_NOT_LOADED')
            linked_images.append(image.name)
    if not linked_images:
        raise RuntimeError('KAYKIT_TEXTURE_BINDING_MISSING')
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True)
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = arm
    references, rows = {}, []
    for label, name in CLIPS.items():
        action = bpy.data.actions[name]
        arm.animation_data.action = action
        start, end = map(int, action.frame_range)
        scene.frame_start, scene.frame_end = start, end
        frames = sorted({start, start + (end-start)//4,
                         start + (end-start)//2, start + 3*(end-start)//4})
        references[label] = {}
        for frame in frames:
            scene.frame_set(frame)
            references[label][frame] = points(mesh)
        scene.frame_set(start)
        path = out / ('SK_Frodo.fbx' if label == 'Idle' else 'AN_Frodo_' + label + '.fbx')
        bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True,
            object_types={'ARMATURE', 'MESH'}, use_mesh_modifiers=True,
            mesh_smooth_type='FACE', use_tspace=False, add_leaf_bones=False,
            use_armature_deform_only=True, bake_anim=True, bake_anim_use_all_bones=True,
            bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False,
            bake_anim_simplify_factor=0.0, axis_forward='-Z', axis_up='Y',
            path_mode='STRIP', embed_textures=False)
        rows.append({'clip': label, 'authored_action': name, 'frames': [start, end],
                     'fps': scene.render.fps / scene.render.fps_base, 'file': path.name,
                     'bytes': path.stat().st_size, 'sha256': digest(path)})
    # Preserve imported FBX time exactly. Blender's default anim_offset=1 would
    # shift a [1,33] clip to [2,34], invalidating matching-frame comparisons.
    skeletons, source_bounds = set(), None
    for row in rows:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=str(out / row['file']), anim_offset=0.0)
        arms = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']
        meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
        if len(arms) != 1 or len(meshes) != 1:
            raise RuntimeError('KAYKIT_REIMPORT_CARDINALITY_FAILED')
        arm, mesh = arms[0], meshes[0]
        if len(arm.data.bones) != 41:
            raise RuntimeError('KAYKIT_REIMPORT_BONES_CHANGED')
        texture_refs = []
        for image in bpy.data.images:
            if image.source == 'FILE':
                resolved = Path(bpy.path.abspath(image.filepath)).resolve()
                if not resolved.is_file() or digest(resolved) != TEXTURE_SHA:
                    raise RuntimeError('KAYKIT_REIMPORT_TEXTURE_MISSING_OR_CHANGED '+image.name)
                texture_refs.append(resolved.name)
        if not texture_refs or set(texture_refs) != {'rogue_texture.png'}:
            raise RuntimeError('KAYKIT_NONPORTABLE_TEXTURE_REFERENCE')
        row['reimport_texture_references'] = texture_refs
        row['reimport_skin'] = skin_metrics(arm, mesh)
        row['skeleton_signature'] = signature(arm)
        skeletons.add(row['skeleton_signature'])
        row['pose_comparisons'], motion, baseline = [], [], None
        for frame, expected in references[row['clip']].items():
            bpy.context.scene.frame_set(frame)
            actual = points(mesh)
            row['pose_comparisons'].append(dict(frame=frame, **geometry_error(expected, actual)))
            if baseline is None:
                baseline = actual
            motion.append(max((a-b).length for a, b in zip(baseline, actual)))
            if row['clip'] == 'Idle' and source_bounds is None:
                source_bounds = {'min': [min(p[k] for p in actual) for k in range(3)],
                                 'max': [max(p[k] for p in actual) for k in range(3)]}
        if max(motion) < 0.001:
            raise RuntimeError('KAYKIT_NO_ACTUAL_SKIN_MOTION ' + row['clip'])
        row['reimport_sampled_motion'] = motion
    if len(skeletons) != 1:
        raise RuntimeError('KAYKIT_CLIP_SKELETON_MISMATCH')
    shutil.copyfile(out / 'SK_Frodo.fbx', out / 'AN_Frodo_Idle.fbx')
    shutil.copyfile(license_file, out / 'LICENSE-KayKit-CC0.txt')
    if digest(source) != SOURCE_SHA:
        raise RuntimeError('KAYKIT_ORIGINAL_SOURCE_CHANGED')
    receipt = {'status': 'NORMALIZED_KAYKIT_CHARACTER_SOURCE_PASS',
        'source_repository': 'KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0',
        'source_commit': SOURCE_COMMIT, 'source_sha256': SOURCE_SHA,
        'license': 'CC0-1.0', 'license_sha256': LICENSE_SHA,
        'blender_version': bpy.app.version_string, 'source_blender_bounds_m': source_bounds,
        'source_blender_forward': '-Y', 'source_blender_up': '+Z',
        'fbx_axis_forward': '-Z', 'fbx_axis_up': 'Y', 'bones': 41,
        'mesh': {'vertex_count': skin['vertices'], 'bone_count': 41, 'max_influences': skin['max_influences'], 'zero_weight_vertices': skin['zero_weight_vertices'], 'triangle_count': skin['triangles']},
        'skin': skin, 'unified_geometry_comparison': join_proof,
        'removed_weapon_accessories': sorted(removed), 'cape_binding': 'authored rigid chest attachment converted in REST space',
        'smoothing': 'FACE', 'selected_complete_armature': True,
        'clips': rows, 'final_frodo_likeness': False,
        'generated_geometry': False, 'generated_animation': False,
        'unreal_imported': False, 'runtime_promoted': False,
        'visually_accepted': False, 'device_tested': False,
        'files': {p.name: digest(p) for p in sorted(out.iterdir()) if p.suffix.lower() in {'.fbx', '.png', '.txt'}},
        'evidence_boundary': 'Numerical Blender source proof. UE4 bind-pose/smoothing import gate and runtime/visual acceptance remain required.'}
    (out / 'source_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('KAYKIT_NORMALIZED_SOURCE_PASS ' + json.dumps({'skin': skin, 'clips': len(rows),
          'max_reimport_error': max(p['max_error'] for row in rows for p in row['pose_comparisons'])}), flush=True)


if __name__ == '__main__':
    main()
