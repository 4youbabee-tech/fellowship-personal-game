"""Export-only Rigify DEF skeleton for a UE4.27 skeletal FBX.

Keeps licensed source DEF vertex groups and rest matrices; never invents skin
weights, animation clips or a runtime-ready Frodo. The original ORG/MCH/IK
control rig remains the SOURCE authoring rig; the game rig is a distinct armature.
"""
from __future__ import annotations

import math
import re


def compact(name):
    return re.sub(r"[^a-z0-9]+", "", name.lower())


def side_match(name, side):
    raw = name.lower()
    return ("left" in raw or ".l" in raw or "_l" in raw or "-l" in raw or raw.endswith(" l")) if side == "L" else (
        "right" in raw or ".r" in raw or "_r" in raw or "-r" in raw or raw.endswith(" r"))


def choose_roles(weight_by_bone, deform_names):
    """Choose the same weighted, deform-priority joint families as Wave3."""
    names = set(deform_names)
    def find(tokens, side=None, exclude=()):
        candidates = []
        for name in names:
            stem = compact(name)
            if side and not side_match(name, side):
                continue
            if any(t in stem for t in exclude):
                continue
            if any(t in stem for t in tokens):
                weight = float(weight_by_bone.get(name, 0))
                if weight > 1e-6:
                    candidates.append((-weight, len(name), name))
        return min(candidates)[2] if candidates else None
    roles = {
        "pelvis": find(("pelvis", "hips", "hip")),
        "spine": find(("spine", "chest")),
        "head": find(("head",)),
    }
    for side in ("L", "R"):
        prefix = "left" if side == "L" else "right"
        roles.update({
            prefix + "_upper_arm": find(("upperarm", "uparm"), side, ("forearm", "lowerarm")),
            prefix + "_forearm": find(("forearm", "lowerarm"), side),
            prefix + "_hand": find(("hand",), side),
            prefix + "_thigh": find(("thigh", "upleg"), side),
            prefix + "_shin": find(("shin", "calf", "lowerleg"), side),
            prefix + "_foot": find(("foot",), side),
        })
    missing = [role for role, name in roles.items() if name is None]
    if missing or len(set(roles.values())) != len(roles):
        raise RuntimeError("GAME_RIG_WEIGHTED_JOINT_ROLES_MISSING " + ",".join(missing))
    return roles


def build_parent_map(source_parents, deform_names, roles):
    """Skip Rigify controllers, mapping ORG ancestors to matching DEF names.

    An explicit anatomical chain for the five previously failing families is
    constructed, instead of accepting a child of its own ORG controller.
    """
    deform = set(deform_names)
    def closest_deform_parent(name):
        seen = {name}
        parent = source_parents.get(name)
        while parent is not None and parent not in seen:
            seen.add(parent)
            if parent in deform:
                return parent
            for prefix in ("ORG-", "MCH-", "ORG_", "MCH_"):
                if parent.startswith(prefix):
                    def_name = "DEF-" + parent[len(prefix):]
                    if def_name in deform and def_name != name:
                        return def_name
            parent = source_parents.get(parent)
        return None
    parents = {name: closest_deform_parent(name) for name in deform}
    pelvis, spine, head = (roles[k] for k in ("pelvis", "spine", "head"))
    parents[pelvis] = None

    def numbered_segments(stem, side=None):
        matches = [n for n in deform if compact(n).startswith("def" + stem)
                   and (side is None or side_match(n, side))]
        def order(name):
            tail = name.split("DEF-", 1)[-1]
            nums = [int(part) for part in re.findall(r"\.(\d+)", tail)]
            return (nums + [0, 0, 0])[:3], name
        return sorted(matches, key=order)

    def chain(nodes, parent):
        for name in nodes:
            if name != parent:
                parents[name] = parent
                parent = name
        return parent

    # Preserve both weight-bearing Rigify bend segments (.01/.02) in a
    # continuous game chain. Selecting only one 'most weighted' DEF bone and
    # parenting it directly misses the other half of the arm or leg.
    spine_end = chain(numbered_segments("spine") + numbered_segments("chest"), pelvis)
    if spine_end == pelvis:
        raise RuntimeError("GAME_RIG_SPINE_SEGMENTS_MISSING")
    # Match the source chain's selected spine to every downstream head bone:
    # head.001 must not remain suspended from a stripped ORG controller.
    neck_end = chain(numbered_segments("neck"), spine_end)
    head_end = chain(numbered_segments("head"), neck_end)
    if head_end == neck_end:
        raise RuntimeError("GAME_RIG_HEAD_SEGMENTS_MISSING")
    for side in ("L", "R"):
        shoulder_end = chain(numbered_segments("shoulder", side), spine_end)
        upper_end = chain(numbered_segments("upperarm", side), shoulder_end)
        fore_end = chain(numbered_segments("forearm", side), upper_end)
        hand_end = chain(numbered_segments("hand", side), fore_end)
        thigh_end = chain(numbered_segments("thigh", side), pelvis)
        shin_end = chain(numbered_segments("shin", side), thigh_end)
        foot_end = chain(numbered_segments("foot", side), shin_end)
        if None in (upper_end, fore_end, hand_end, thigh_end, shin_end, foot_end):
            raise RuntimeError("GAME_RIG_MISSING_LIMB_SEGMENTS " + side)
    # Validate the exact joint selections used by Wave3, including any .02
    # segment that has greater influence than .01; no role is exempt.
    def descendant(child, ancestor):
        seen=set()
        node=child
        while node is not None and node not in seen:
            if node == ancestor:
                return True
            seen.add(node)
            node=parents.get(node)
        return False
    for side in ("left", "right"):
        for child, ancestor in (("_forearm", "_upper_arm"), ("_hand", "_forearm"),
                                ("_shin", "_thigh"), ("_foot", "_shin")):
            if not descendant(roles[side + child], roles[side + ancestor]):
                raise RuntimeError("GAME_RIG_LIMB_PARENT_REJECT " + side + child)
    if not descendant(head, spine):
        raise RuntimeError("GAME_RIG_HEAD_PARENT_REJECT")
    # Other DEF fingers, face and twist segments preserve their mapped source
    # ancestry where possible. Any source cycle is a strict export failure.
    for name in deform:
        visited = set()
        node = name
        while node is not None:
            if node in visited:
                raise RuntimeError("GAME_RIG_PARENT_CYCLE " + name)
            visited.add(node)
            node = parents.get(node)
    return parents


def make_game_deform_rig(source_armature, bound_meshes):
    """Run inside Blender 4.0 with the source armature in REST position."""
    import bpy
    from mathutils import Vector

    bpy.ops.object.mode_set(mode="OBJECT") if bpy.context.object and bpy.context.object.mode != "OBJECT" else None
    source_armature.data.pose_position = "REST"
    bpy.context.view_layer.update()
    original_matrices = {mesh.name: mesh.matrix_world.copy() for mesh in bound_meshes}

    def evaluated_positions():
        depsgraph = bpy.context.evaluated_depsgraph_get()
        points = []
        for mesh in bound_meshes:
            evaluated = mesh.evaluated_get(depsgraph)
            temp = evaluated.to_mesh()
            try:
                points.extend(evaluated.matrix_world @ v.co for v in temp.vertices)
            finally:
                evaluated.to_mesh_clear()
        return points

    baseline = evaluated_positions()
    if not baseline:
        raise RuntimeError("GAME_RIG_EMPTY_SOURCE")
    source_bones = {b.name: b for b in source_armature.data.bones}
    deform_bones = {b.name: b for b in source_bones.values() if b.use_deform}
    if len(deform_bones) < 13:
        raise RuntimeError("GAME_RIG_DEFORM_BONES_INSUFFICIENT")
    influence = {}
    for mesh in bound_meshes:
        names = {g.index: g.name for g in mesh.vertex_groups}
        for vertex in mesh.data.vertices:
            for membership in vertex.groups:
                name = names.get(membership.group)
                if name in deform_bones and membership.weight > 1e-6:
                    influence[name] = influence.get(name, 0.0) + float(membership.weight)
    roles = choose_roles(influence, deform_bones)
    source_parents = {n: b.parent.name if b.parent else None for n, b in source_bones.items()}
    parents = build_parent_map(source_parents, deform_bones, roles)
    saved_rest = {name: (bone.matrix_local.copy(), float(bone.length)) for name, bone in deform_bones.items()}

    data = bpy.data.armatures.new("Frodo_GameDeformSkeleton")
    game = bpy.data.objects.new("Frodo_GameDeformArmature", data)
    bpy.context.scene.collection.objects.link(game)
    game.matrix_world = source_armature.matrix_world.copy()
    bpy.ops.object.select_all(action="DESELECT")
    game.select_set(True)
    bpy.context.view_layer.objects.active = game
    bpy.ops.object.mode_set(mode="EDIT")
    for name, (rest, length) in saved_rest.items():
        if not math.isfinite(length) or length <= 1e-6:
            raise RuntimeError("GAME_RIG_INVALID_REST_LENGTH " + name)
        eb = data.edit_bones.new(name)
        eb.matrix = rest
        eb.length = length
        eb.use_deform = True
    for name, parent in parents.items():
        if parent is not None:
            eb = data.edit_bones[name]
            eb.parent = data.edit_bones[parent]
            eb.use_connect = False
            rest, length = saved_rest[name]
            eb.matrix = rest
            eb.length = length
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.update()
    for name, (rest, length) in saved_rest.items():
        new_bone = data.bones[name]
        if max(abs(new_bone.matrix_local[i][j]-rest[i][j]) for i in range(4) for j in range(4)) > 1e-4:
            raise RuntimeError("GAME_RIG_REST_CHANGED " + name)
    if len(data.bones) != len(deform_bones):
        raise RuntimeError("GAME_RIG_EXPORTED_BONE_COUNT_CHANGED")
    for mesh in bound_meshes:
        original = original_matrices[mesh.name]
        mesh.parent = None
        mesh.matrix_world = original
        modifiers = [mod for mod in mesh.modifiers if mod.type == "ARMATURE"]
        if not modifiers:
            modifiers = [mesh.modifiers.new(name="FrodoGameDeform", type="ARMATURE")]
        for modifier in modifiers:
            if modifier.object and modifier.object != source_armature:
                raise RuntimeError("GAME_RIG_CONFLICTING_ARMATURE " + mesh.name)
            modifier.object = game
        mesh.matrix_world = original
        if not any(mod.type == "ARMATURE" and mod.object == game for mod in mesh.modifiers):
            raise RuntimeError("GAME_RIG_MESH_BINDING_MISSING " + mesh.name)
    bpy.context.view_layer.update()
    new_points = evaluated_positions()
    if len(baseline) != len(new_points):
        raise RuntimeError("GAME_RIG_REST_VERTEX_COUNT_CHANGED")
    mins = [min(p[i] for p in baseline) for i in range(3)]
    maxs = [max(p[i] for p in baseline) for i in range(3)]
    diagonal = math.sqrt(sum((maxs[i] - mins[i])**2 for i in range(3)))
    if not math.isfinite(diagonal) or diagonal < 1e-6:
        raise RuntimeError("GAME_RIG_INVALID_BASELINE_BOUNDS")
    max_delta = max((a-b).length for a,b in zip(baseline,new_points))
    # This protects against a well-parented but badly rebound or offset mesh.
    if not math.isfinite(max_delta) or max_delta > diagonal*0.01:
        raise RuntimeError("GAME_RIG_REST_SKIN_MISMATCH delta=" + str(max_delta))
    for mesh in bound_meshes:
        if not all(math.isfinite(float(c)) for corner in mesh.bound_box for c in corner):
            raise RuntimeError("GAME_RIG_NONFINITE_MESH_BOUNDS")
    print("GAME_RIG_SOURCE_REST_PASS " + str({
        "source_bones":len(source_bones), "game_bones":len(deform_bones),
        "weighted_deform":len(influence),"max_rest_delta":max_delta,
        "reference_diagonal":diagonal,"required_roles":roles,
    }), flush=True)
    return game, {"game_bones":len(deform_bones), "weighted_game_bones":len(influence),
                  "max_rest_delta":max_delta, "reference_diagonal":diagonal,
                  "role_names":roles, "parent_map":parents}
