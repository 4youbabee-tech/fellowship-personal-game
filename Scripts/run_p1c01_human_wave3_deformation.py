import argparse
import hashlib
import json
import math
import os
import re
import sys

import bpy
from mathutils import Matrix

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
parser = argparse.ArgumentParser()
parser.add_argument("--hosted-receipt", required=True)
parser.add_argument("--ue4-receipt", required=True)
parser.add_argument("--artifact-root", required=True)
parser.add_argument("--output", required=True)
args = parser.parse_args(argv)

with open(args.hosted_receipt, "r", encoding="utf-8-sig") as f:
    hosted = json.load(f)
with open(args.ue4_receipt, "r", encoding="utf-8-sig") as f:
    ue4 = json.load(f)

winner = ue4.get("technical_winner")
if not winner or not winner.get("technical_pass"):
    raise RuntimeError("technical winner missing from UE4 receipt")
winner_sha = str(winner.get("normalized_sha256", "")).lower()
if not winner_sha:
    raise RuntimeError("winner SHA missing")

candidate = None
for row in hosted.get("normalized_candidates", []):
    if str(row.get("normalized_sha256", "")).lower() == winner_sha:
        candidate = row
        break
if candidate is None:
    raise RuntimeError("winner payload not present in hosted normalized candidates")

relative_path = str(candidate.get("normalized_relative_path", "")).replace("/", os.sep)
fbx_path = os.path.join(args.artifact_root, relative_path)
if not os.path.isfile(fbx_path):
    raise RuntimeError("winner FBX missing: " + fbx_path)
with open(fbx_path, "rb") as f:
    actual_sha = hashlib.sha256(f.read()).hexdigest().lower()
if actual_sha != winner_sha:
    raise RuntimeError("winner FBX hash mismatch")

bpy.ops.wm.read_factory_settings(use_empty=True)
result = bpy.ops.import_scene.fbx(filepath=fbx_path, use_custom_normals=True)
if "FINISHED" not in result:
    raise RuntimeError("FBX import failed")

armatures = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
if len(armatures) != 1:
    raise RuntimeError("expected exactly one armature")
if not meshes:
    raise RuntimeError("no mesh objects")
armature = armatures[0]
armature.data.pose_position = "POSE"

def compact(name):
    return re.sub(r"[^a-z0-9]+", "", name.lower())

def side_match(name, side):
    raw = name.lower()
    if side == "L":
        return "left" in raw or ".l" in raw or "_l" in raw or "-l" in raw or raw.endswith(" l")
    if side == "R":
        return "right" in raw or ".r" in raw or "_r" in raw or "-r" in raw or raw.endswith(" r")
    return True

def bone_influence_count(bone_name):
    influenced=0
    for obj in meshes:
        group=obj.vertex_groups.get(bone_name)
        if group is None: continue
        influenced += sum(1 for vertex in obj.data.vertices if any(link.group==group.index and link.weight>1e-5 for link in vertex.groups))
    return influenced

def find_joint(tokens, side=None, exclude=()):
    matches=[]
    for pb in armature.pose.bones:
        packed=compact(pb.name)
        if not pb.bone.use_deform or (side and not side_match(pb.name,side)) or any(x in packed for x in exclude): continue
        if any(token in packed for token in tokens): matches.append((-bone_influence_count(pb.name),len(pb.name),pb.name.lower(),pb))
    if not matches:return None
    matches.sort(key=lambda item:(item[0],item[1],item[2]))
    return matches[0][3]

joints = {
    "pelvis": find_joint(("pelvis", "hips", "hip")),
    "spine": find_joint(("spine", "chest")),
    "head": find_joint(("head",)),
    "left_upper_arm": find_joint(("upperarm", "uparm"), "L", ("forearm", "lowerarm")),
    "right_upper_arm": find_joint(("upperarm", "uparm"), "R", ("forearm", "lowerarm")),
    "left_forearm": find_joint(("forearm", "lowerarm"), "L"),
    "right_forearm": find_joint(("forearm", "lowerarm"), "R"),
    "left_hand": find_joint(("hand",), "L"),
    "right_hand": find_joint(("hand",), "R"),
    "left_thigh": find_joint(("thigh", "upleg", "upperleg"), "L"),
    "right_thigh": find_joint(("thigh", "upleg", "upperleg"), "R"),
    "left_shin": find_joint(("shin", "calf", "lowerleg"), "L"),
    "right_shin": find_joint(("shin", "calf", "lowerleg"), "R"),
    "left_foot": find_joint(("foot",), "L"),
    "right_foot": find_joint(("foot",), "R"),
}
missing = sorted([key for key, value in joints.items() if value is None])
if missing:
    raise RuntimeError("required deformation joints missing: " + ",".join(missing))

def is_descendant(child, parent):
    node = child.bone.parent
    while node is not None:
        if node == parent.bone:
            return True
        node = node.parent
    return False

hierarchy = {
    "left_arm": is_descendant(joints["left_forearm"], joints["left_upper_arm"]) and is_descendant(joints["left_hand"], joints["left_forearm"]),
    "right_arm": is_descendant(joints["right_forearm"], joints["right_upper_arm"]) and is_descendant(joints["right_hand"], joints["right_forearm"]),
    "left_leg": is_descendant(joints["left_shin"], joints["left_thigh"]) and is_descendant(joints["left_foot"], joints["left_shin"]),
    "right_leg": is_descendant(joints["right_shin"], joints["right_thigh"]) and is_descendant(joints["right_foot"], joints["right_shin"]),
    "spine_head": is_descendant(joints["head"], joints["spine"]),
}
if not all(hierarchy.values()):
    failed = [key for key, value in hierarchy.items() if not value]
    raise RuntimeError("hierarchy sanity failed: " + ",".join(failed))

def weighted_vertex_influence_count(bone_name):
    return bone_influence_count(bone_name)

joint_influence_counts = {
    key: weighted_vertex_influence_count(pb.name)
    for key, pb in joints.items()
}
uninfluenced_joints = sorted(
    key for key, count in joint_influence_counts.items()
    if count <= 0
)
if uninfluenced_joints:
    raise RuntimeError(
        "required deform joints have no weighted vertex influence: " +
        ",".join(uninfluenced_joints)
    )

def evaluated_points():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    points = []
    for obj in meshes:
        evaluated = obj.evaluated_get(depsgraph)
        temp = evaluated.to_mesh()
        try:
            for vertex in temp.vertices:
                point = evaluated.matrix_world @ vertex.co
                points.append((float(point.x), float(point.y), float(point.z)))
        finally:
            evaluated.to_mesh_clear()
    return points

def metrics(points):
    if not points:
        raise RuntimeError("no evaluated mesh vertices")
    finite = all(math.isfinite(v) for point in points for v in point)
    mins = [min(point[i] for point in points) for i in range(3)]
    maxs = [max(point[i] for point in points) for i in range(3)]
    diag = math.sqrt(sum((maxs[i] - mins[i]) ** 2 for i in range(3)))
    return {"finite": finite, "min": mins, "max": maxs, "diag": diag, "vertex_count": len(points)}

def reset_pose():
    for pb in armature.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()

def rotate(key, axis, degrees):
    pb = joints[key]
    pb.rotation_mode = "XYZ"
    pb.rotation_euler[axis] = math.radians(degrees)

reset_pose()
rest_points = evaluated_points()
rest = metrics(rest_points)
if not rest["finite"] or rest["diag"] <= 1e-6:
    raise RuntimeError("invalid rest-pose bounds")

scenarios = [
    ("shoulders", [("left_upper_arm", 2, -45.0), ("right_upper_arm", 2, 45.0)]),
    ("elbows", [("left_forearm", 0, -75.0), ("right_forearm", 0, -75.0)]),
    ("knees", [("left_shin", 0, 65.0), ("right_shin", 0, 65.0)]),
    ("hands_feet", [("left_hand", 1, -20.0), ("right_hand", 1, 20.0), ("left_foot", 0, 20.0), ("right_foot", 0, 20.0)]),
    ("locomotion_stress", [("left_upper_arm", 0, 22.0), ("right_upper_arm", 0, -22.0), ("left_thigh", 0, -28.0), ("right_thigh", 0, 28.0), ("left_shin", 0, 28.0), ("right_shin", 0, 12.0)]),
]
scenario_results = []
for name, rotations in scenarios:
    reset_pose()
    for key, axis, degrees in rotations:
        rotate(key, axis, degrees)
    bpy.context.view_layer.update()
    posed_points = evaluated_points()
    posed = metrics(posed_points)
    max_displacement = None
    min_required_displacement = max(rest["diag"] * 1e-5, 1e-6)
    passed = False
    reject_reason = None
    if posed["vertex_count"] == rest["vertex_count"]:
        max_displacement = max(
            math.sqrt(sum((posed_points[i][axis] - rest_points[i][axis]) ** 2 for axis in range(3)))
            for i in range(len(rest_points))
        )
        ratio = posed["diag"] / rest["diag"] if rest["diag"] > 0 else 999.0
        if max_displacement < min_required_displacement:
            reject_reason = "NO_NONTRIVIAL_DEFORMATION"
        passed = (
            posed["finite"] and
            0.20 <= ratio <= 5.0 and
            min_required_displacement <= max_displacement <= rest["diag"] * 5.0
        )
    else:
        reject_reason = "VERTEX_COUNT_CHANGED"
    scenario_results.append({
        "name": name,
        "passed": passed,
        "reject_reason": reject_reason,
        "bounds": posed,
        "bounds_ratio": posed["diag"] / rest["diag"] if rest["diag"] > 0 else None,
        "max_vertex_displacement": max_displacement,
        "min_required_displacement": min_required_displacement,
    })

reset_pose()
all_pass = all(item["passed"] for item in scenario_results)
armature_transform_finite = all(
    math.isfinite(float(value))
    for value in tuple(armature.location) + tuple(armature.rotation_euler) + tuple(armature.scale)
)
if not armature_transform_finite:
    all_pass = False

receipt = {
    "schema_version": 1,
    "status": "STATIC_DEFORMATION_STRESS_PASS" if all_pass else "STATIC_DEFORMATION_STRESS_REJECT",
    "technical_winner_sha256": winner_sha,
    "technical_winner_reference_bones": int(winner.get("ue4_reference_bones", 0)),
    "source_entry": candidate.get("source_entry"),
    "source_sha256": candidate.get("source_sha256"),
    "joint_map": {key: value.name for key, value in joints.items()},
    "hierarchy": hierarchy,
    "joint_influence_counts": joint_influence_counts,
    "rest_bounds": rest,
    "scenarios": scenario_results,
    "armature_transform": {
        "location": [float(value) for value in armature.location],
        "rotation_euler": [float(value) for value in armature.rotation_euler],
        "scale": [float(value) for value in armature.scale],
        "finite": armature_transform_finite,
    },
    "visual_deformation_accepted": False,
    "retarget_accepted": False,
    "runtime_integration_allowed": False,
    "next_gate": "Idle/Walk/Run animation inventory and retarget compatibility, then human visual deformation review.",
    "evidence_boundary": "Fail-closed numerical Blender deformation stress with deform-bone, weighted-influence and non-zero evaluated-displacement proof only; no rendered/human visual, retarget, runtime, PIE, device or FPS acceptance.",
}
os.makedirs(os.path.dirname(args.output), exist_ok=True)
with open(args.output, "w", encoding="utf-8") as f:
    json.dump(receipt, f, indent=2, sort_keys=True)
print(("HUMAN_WAVE3_DEFORMATION_PASS" if all_pass else "HUMAN_WAVE3_DEFORMATION_REJECT") + " winner=" + winner_sha)
if not all_pass:
    raise RuntimeError("static deformation stress rejected")
