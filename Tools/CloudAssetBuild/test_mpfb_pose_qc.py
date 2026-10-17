"""Pure mocked regressions for the joint-motion pre-export gate.

These prove the gate's failure semantics without claiming a real Blender/UE run.
Execute: python -m unittest Tools/CloudAssetBuild/test_mpfb_pose_qc.py -v
"""
import importlib.util
import sys
import types
import unittest
from pathlib import Path


class Vec:
    def __init__(self, x, y=0, z=0):
        self.xyz = (x, y, z)

    @property
    def x(self):
        return self.xyz[0]

    @x.setter
    def x(self, value):
        self.xyz = (value, self.xyz[1], self.xyz[2])

    def copy(self):
        return Vec(*self.xyz)

    def __sub__(self, other):
        return Vec(*(a - b for a, b in zip(self.xyz, other.xyz)))

    @property
    def length(self):
        return sum(v * v for v in self.xyz) ** 0.5


class FakePoseBone:
    def __init__(self):
        self.rotation_mode = "XYZ"
        self.rotation_euler = Vec(0, 0, 0)
        self.rotation_quaternion = Vec(1, 0, 0)


class FakeBody:
    def __init__(self, deform=True, armature_modifier=True):
        self.deform = deform
        self.modifiers = [types.SimpleNamespace(type="ARMATURE", object=None)] if armature_modifier else []
        self.dimensions = Vec(2)
        self.vertex_groups = [types.SimpleNamespace(name=n, index=i)
                              for i, n in enumerate(["lowerarm_l", "calf_l"])]
        self.data = types.SimpleNamespace(vertices=[
            types.SimpleNamespace(index=i, groups=[types.SimpleNamespace(group=i % 2, weight=0.8)])
            for i in range(400)])

    def evaluated_get(self, graph):
        return self

    def to_mesh(self):
        moving = bool(self.deform and (
            self.armature.pose.bones["lowerarm_l"].rotation_euler.x or
            self.armature.pose.bones["calf_l"].rotation_euler.x))
        return types.SimpleNamespace(vertices=[
            types.SimpleNamespace(co=Vec(i * 0.005 + (
                (0.2 if i % 2 == 0 else 0.1) if moving else 0.0)))
            for i in range(400)])

    def to_mesh_clear(self):
        pass


class PoseProofTests(unittest.TestCase):
    def setUp(self):
        self.previous_bpy = sys.modules.get("bpy")
        sys.modules["bpy"] = types.SimpleNamespace(context=types.SimpleNamespace(
            evaluated_depsgraph_get=lambda: object(),
            view_layer=types.SimpleNamespace(update=lambda: None)))
        path = Path(__file__).with_name("mpfb_pose_qc.py")
        spec = importlib.util.spec_from_file_location("mpfb_pose_qc_standalone_test", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.check = module.inspect_deform_and_pose

    def tearDown(self):
        if self.previous_bpy is None:
            del sys.modules["bpy"]
        else:
            sys.modules["bpy"] = self.previous_bpy

    def world(self, deform=True, armature_modifier=True):
        armature = types.SimpleNamespace(
            data=types.SimpleNamespace(bones=[
                types.SimpleNamespace(name=n, use_deform=True) for n in ["lowerarm_l", "calf_l"]]),
            pose=types.SimpleNamespace(bones={
                "lowerarm_l": FakePoseBone(), "calf_l": FakePoseBone()}))
        body = FakeBody(deform=deform, armature_modifier=armature_modifier)
        body.armature = armature
        if armature_modifier:
            body.modifiers[0].object = armature
        return body, armature

    def test_both_limb_families_move(self):
        body, armature = self.world()
        weighted, movement = self.check(body, armature)
        self.assertEqual(weighted, 400)
        self.assertEqual(set(movement), {"arm", "leg"})
        self.assertGreater(movement["arm"]["max_position_delta_blender_units"], 0)

    def test_armature_modifier_required(self):
        body, armature = self.world(armature_modifier=False)
        with self.assertRaisesRegex(RuntimeError, "ARMATURE_MODIFIER_MISSING"):
            self.check(body, armature)

    def test_static_weighted_mesh_fails_deformation(self):
        body, armature = self.world(deform=False)
        with self.assertRaisesRegex(RuntimeError, "DOES_NOT_DEFORM"):
            self.check(body, armature)


if __name__ == "__main__":
    unittest.main()
