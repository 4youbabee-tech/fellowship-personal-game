"""Inspect actual MPFB game-skeleton deformation before exporting a UE4 FBX.

This is an offline Blender pose test, NOT an Unreal PIE/deformation claim.
"""
import math


def inspect_deform_and_pose(body, armature):
    """Require weighted deform bones and measurable forearm + calf vertex movement.

    Restores the armature pose and doesn't write any animation.
    """
    import bpy

    deform_bones = {bone.name for bone in armature.data.bones if bone.use_deform}
    deform_groups = {group.index: group.name for group in body.vertex_groups
                     if group.name in deform_bones}
    if not any(mod.type == "ARMATURE" and mod.object == armature for mod in body.modifiers):
        raise RuntimeError("MPFB_EXPORTED_BODY_ARMATURE_MODIFIER_MISSING")
    weighted_indices = [vertex.index for vertex in body.data.vertices
                        if any(binding.group in deform_groups and binding.weight > 0.0
                               for binding in vertex.groups)]
    if len(weighted_indices) < max(256, len(body.data.vertices) // 2):
        raise RuntimeError("MPFB_DEFORM_BONE_WEIGHTS_MISSING_OR_SPARSE")

    depsgraph = bpy.context.evaluated_depsgraph_get()

    def evaluated_coords():
        evaluated = body.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            return [vertex.co.copy() for vertex in mesh.vertices]
        finally:
            evaluated.to_mesh_clear()

    bpy.context.view_layer.update()
    rest = evaluated_coords()
    if len(rest) != len(body.data.vertices):
        raise RuntimeError("MPFB_POSE_QC_TOPOLOGY_UNSTABLE")
    groups_by_name = {name: idx for idx, name in deform_groups.items()}
    families = {
        "arm": ("lowerarm_l", "lowerarm_r",
                "mixamorig:LeftForeArm", "mixamorig:RightForeArm"),
        "leg": ("calf_l", "calf_r",
                "mixamorig:LeftLeg", "mixamorig:RightLeg"),
    }
    results = {}
    for family, names in families.items():
        chosen = next((name for name in names if name in groups_by_name
                       and armature.pose.bones.get(name) is not None), None)
        if not chosen:
            raise RuntimeError("MPFB_DEFORM_POSE_BONE_MISSING_" + family.upper())
        idx = groups_by_name[chosen]
        affected = [v.index for v in body.data.vertices
                    if any(g.group == idx and g.weight >= 0.1 for g in v.groups)]
        if len(affected) < 12:
            raise RuntimeError("MPFB_POSE_BONE_INFLUENCE_TOO_SMALL_" + chosen)
        pose_bone = armature.pose.bones[chosen]
        prior_mode = pose_bone.rotation_mode
        prior_euler = pose_bone.rotation_euler.copy()
        prior_quaternion = pose_bone.rotation_quaternion.copy()
        try:
            pose_bone.rotation_mode = "XYZ"
            pose_bone.rotation_euler.x += math.radians(25.0)
            bpy.context.view_layer.update()
            posed = evaluated_coords()
            if len(posed) != len(rest):
                raise RuntimeError("MPFB_POSE_QC_TOPOLOGY_CHANGED")
            maximum_shift = max((posed[i] - rest[i]).length for i in affected)
        finally:
            pose_bone.rotation_mode = prior_mode
            pose_bone.rotation_euler = prior_euler
            pose_bone.rotation_quaternion = prior_quaternion
            bpy.context.view_layer.update()
        if maximum_shift <= max(0.0005, body.dimensions.length * 0.0004):
            raise RuntimeError("MPFB_POSE_BONE_DOES_NOT_DEFORM_" + chosen)
        results[family] = {
            "bone": chosen,
            "affected_vertices": len(affected),
            "max_position_delta_blender_units": round(maximum_shift, 7),
        }
    return len(weighted_indices), results
