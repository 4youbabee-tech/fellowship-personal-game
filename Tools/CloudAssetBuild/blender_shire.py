#!/usr/bin/env python3
"""Headless Blender 4.x source kit: 22 static families / 44 real FBX.

Models are ORIGINAL PROCEDURAL STATIC PROPS, not hero characters. Offline
Blender reimport is checked, but Unreal FBX import/PIE remains a separate gate.
Run: blender -b -t 2 --python Tools/CloudAssetBuild/blender_shire.py -- --out OUT
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import bpy

SOURCE_NAME = "SHIRE_P1C01_MODULAR_WORLD_AND_BAGEND_ASSET_WAVE_V3"
MODELS = ("RoundDoor", "PicketFence", "PartyTable", "GardenCart",
          "RoundWindow", "GardenHedge", "OakTree", "StorageBarrel", "FarmGate", "GardenPlanter",
          "BagEndFrontWall", "RoundRoomWallArc", "RoundRoomFloor", "Hearth", "Bookcase", "HobbitBed",
          "WoodenFootbridge", "MillWheel", "PartyCanopy", "StonePath", "LanternPost", "VillageWell")
PALETTE = {
    "oak_timber": (0.37, 0.19, 0.08, 1.0),
    "shire_meadow": (0.26, 0.45, 0.12, 1.0),
    "shire_earth": (0.40, 0.29, 0.19, 1.0),
    "bagend_plaster": (0.72, 0.54, 0.31, 1.0),
    "mossy_stone": (0.29, 0.32, 0.20, 1.0),
    "charred_basalt": (0.12, 0.11, 0.10, 1.0),
}
PARTS = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mat(family, output):
    name = "M_Sh_" + family
    material = bpy.data.materials.get(name)
    if material:
        return material
    material = bpy.data.materials.new(name)
    material.diffuse_color = PALETTE[family]
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = PALETTE[family]
        bsdf.inputs["Roughness"].default_value = 0.82
        png = output / "materials" / family / ("TX_" + family + "_BaseColor.png")
        if png.exists():
            tex = material.node_tree.nodes.new("ShaderNodeTexImage")
            tex.image = bpy.data.images.load(str(png), check_existing=True)
            material.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    return material


def finish(obj, family, output, bevel=0.0):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if bevel:
        mod = obj.modifiers.new("SubtleEdgeChamfer", "BEVEL")
        mod.width = bevel
        mod.segments = 1
        if hasattr(mod, "affect"):
            mod.affect = "EDGES"
        bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.data.materials.clear()
    obj.data.materials.append(mat(family, output))
    for polygon in obj.data.polygons:
        polygon.use_smooth = obj.type == "MESH" and len(polygon.vertices) >= 4 and family in ("mossy_stone",)
    PARTS.append(obj)
    return obj


def box(name, pos, scale, family, out, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    # Width must be substantially smaller than the thinnest edge; Blender
    # Bevel can create zero-area faces on 0.025m stepping stones otherwise.
    safe_bevel = min(bevel, min(scale) * 0.16) if bevel else 0.0
    return finish(obj, family, out, safe_bevel)


def cylinder(name, pos, radius, depth, family, out, vertices, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth,
                                        location=pos, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    return finish(obj, family, out)


def torus(name, pos, major, minor, family, out, segments, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_segments=segments, minor_segments=6,
                                     location=pos, rotation=rotation,
                                     major_radius=major, minor_radius=minor)
    obj = bpy.context.object
    obj.name = name
    return finish(obj, family, out)


def join_visual(name):
    bpy.ops.object.select_all(action="DESELECT")
    for ob in PARTS:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = PARTS[0]
    bpy.ops.object.join()
    visual = bpy.context.view_layer.objects.active
    visual.name = name
    bpy.context.scene.cursor.location = (0, 0, 0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(island_margin=0.012)
    bpy.ops.object.mode_set(mode="OBJECT")
    for face in visual.data.polygons:
        if face.area <= 0.0000001:
            raise ValueError(f"DEGENERATE_FACE in {name}")
    if not visual.data.uv_layers:
        raise ValueError(f"UV0_MISSING in {name}")
    return visual


def collider(name, pos, scale, index=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    ob = bpy.context.object
    ob.name = f"UCX_{name}_{index:02d}"
    ob.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    ob.display_type = "WIRE"
    ob.hide_render = True
    return ob


def draw_round_door(out, simple):
    d = 16 if simple else 32
    cylinder("RoundTimberSlab", (0, 0, 1.12), 0.91, 0.13, "oak_timber", out, d,
             rotation=(math.pi / 2, 0, 0))
    torus("TimberArchFrame", (0, 0.08, 1.12), 0.96, 0.10,
          "oak_timber", out, 20 if simple else 40, (math.pi / 2, 0, 0))
    torus("IronRingHandle", (0.31, -0.14, 1.14), 0.105, 0.024,
          "charred_basalt", out, 12 if simple else 20, (math.pi / 2, 0, 0))
    if not simple:
        for x in (-0.48, -0.10, 0.29, 0.58):
            box("WoodPlankAccent", (x, -0.091, 1.12), (0.027, 0.013, 1.15),
                "oak_timber", out)
        for z in (0.75, 1.47):
            box("IronHinge", (-0.62, -0.17, z), (0.28, 0.035, 0.07),
                "charred_basalt", out)


def draw_fence(out, simple):
    for x in (-1.38, -0.46, 0.46, 1.38):
        box("FencePost", (x, 0, 0.53), (0.115, 0.13, 1.06),
            "oak_timber", out, 0.012 if not simple else 0)
        if not simple:
            cylinder("PostCap", (x, 0, 1.10), 0.083, 0.06,
                     "oak_timber", out, 8)
    for z in (0.31, 0.78):
        box("CrossRail", (0, 0.065, z), (3.00, 0.09, 0.095), "oak_timber", out)


def draw_party_table(out, simple):
    box("PlankTableTop", (0, 0, 0.82), (2.42, 0.89, 0.11),
        "oak_timber", out, 0.018 if not simple else 0)
    for x in (-0.86, 0.86):
        for y in (-0.32, 0.32):
            box("TrestleLeg", (x, y, 0.41), (0.13, 0.13, 0.82), "oak_timber", out)
    for y in (-0.89, 0.89):
        box("PartyBenchSeat", (0, y, 0.47), (2.14, 0.29, 0.09),
            "oak_timber", out, 0.012 if not simple else 0)
        if not simple:
            for x in (-0.74, 0.74):
                box("BenchLeg", (x, y, 0.22), (0.12, 0.12, 0.44),
                    "oak_timber", out)


def draw_garden_cart(out, simple):
    box("CartBed", (0, 0, 0.66), (1.48, 0.83, 0.12),
        "oak_timber", out, 0.016 if not simple else 0)
    for y in (-0.37, 0.37):
        box("CartSide", (0, y, 0.91), (1.48, 0.08, 0.38),
            "oak_timber", out)
    box("CartFront", (0.70, 0, 0.91), (0.08, 0.78, 0.38), "oak_timber", out)
    for y in (-0.53, 0.53):
        cylinder("CartWheel", (-0.25, y, 0.43), 0.41, 0.115,
                 "oak_timber", out, 12 if simple else 24,
                 rotation=(math.pi / 2, 0, 0))
        if not simple:
            cylinder("WheelHub", (-0.25, y + (0.07 if y > 0 else -0.07), 0.43),
                     0.11, 0.04, "charred_basalt", out, 12,
                     rotation=(math.pi / 2, 0, 0))
    for y in (-0.30, 0.30):
        box("PullHandle", (1.09, y, 0.68), (0.93, 0.075, 0.075),
            "oak_timber", out)



def ico(name, pos, scale, family, out, simple):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1 if simple else 2, radius=1.0,
                                          location=pos)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    return finish(ob, family, out)


def draw_round_window(out, simple):
    cylinder("DarkWindowInset", (0, 0.0, 1.22), 0.50, 0.035,
             "charred_basalt", out, 16 if simple else 32,
             rotation=(math.pi / 2, 0, 0))
    torus("CircularWindowFrame", (0, -0.055, 1.22), 0.51, 0.085,
          "oak_timber", out, 16 if simple else 32, (math.pi / 2, 0, 0))
    box("WindowSill", (0, -0.16, 0.62), (1.20, 0.27, 0.11),
        "oak_timber", out, 0.018 if not simple else 0)
    if not simple:
        box("VerticalMullion", (0, -0.094, 1.22), (0.055, 0.045, 0.91),
            "oak_timber", out)
        box("HorizontalMullion", (0, -0.094, 1.22), (0.91, 0.045, 0.052),
            "oak_timber", out)


def draw_garden_hedge(out, simple):
    for i, x in enumerate((-1.30, -0.65, 0.0, 0.65, 1.30)):
        ico("LeafyHedgeShape", (x, 0, 0.72 + 0.05 * (i % 2)),
            (0.73, 0.50, 0.65), "shire_meadow", out, simple)
        if not simple:
            box("HedgeTrunk", (x, 0, 0.31), (0.10, 0.09, 0.62),
                "oak_timber", out)


def draw_oak_tree(out, simple):
    cylinder("OakTreeTrunk", (0, 0, 1.45), 0.22, 2.90, "oak_timber",
             out, 8 if simple else 12)
    ico("LeafCrownMain", (0, 0, 3.10),
        (1.55, 1.36, 1.25), "shire_meadow", out, simple)
    if not simple:
        for x, y in ((-0.8, 0.28), (0.7, -0.22)):
            ico("LeafCrownSide", (x, y, 2.70),
                (0.98, 1.05, 0.94), "shire_meadow", out, simple)
        box("BranchSupport", (-0.34, 0, 2.36), (0.80, 0.15, 0.16),
            "oak_timber", out)


def draw_storage_barrel(out, simple):
    cylinder("BarrelBody", (0, 0, 0.45), 0.39, 0.86, "oak_timber",
             out, 12 if simple else 20)
    for z in (0.21, 0.72):
        torus("BarrelIronHoop", (0, 0, z), 0.40, 0.030,
              "charred_basalt", out, 12 if simple else 24)
    if not simple:
        cylinder("BarrelTop", (0, 0, 0.89), 0.375, 0.025,
                 "oak_timber", out, 20)


def draw_farm_gate(out, simple):
    for x in (-1.12, 1.12):
        box("GatePost", (x, 0, 0.67), (0.15, 0.15, 1.34),
            "oak_timber", out, 0.01 if not simple else 0)
    for z in (0.27, 0.70, 1.08):
        box("GateHorizontalRail", (0, 0.01, z), (2.30, 0.10, 0.095),
            "oak_timber", out)
    if not simple:
        for x in (-0.70, -0.22, 0.26, 0.72):
            box("GatePicket", (x, 0.02, 0.65), (0.09, 0.09, 1.10),
                "oak_timber", out)


def draw_garden_planter(out, simple):
    box("PlanterSoil", (0, 0, 0.47), (1.36, 0.68, 0.16),
        "mossy_stone", out)
    for y in (-0.38, 0.38):
        box("PlanterWallLong", (0, y, 0.44), (1.52, 0.105, 0.39),
            "oak_timber", out)
    for x in (-0.71, 0.71):
        box("PlanterWallEnd", (x, 0, 0.44), (0.09, 0.77, 0.39),
            "oak_timber", out)
    for x in (-0.63, 0.63):
        for y in (-0.30, 0.30):
            box("PlanterLeg", (x, y, 0.23), (0.11, 0.11, 0.46),
                "oak_timber", out)
    for x in ((-0.46, 0.0, 0.46) if not simple else (0.0,)):
        ico("PlanterFoliage", (x, 0.0, 0.78), (0.23, 0.19, 0.25),
            "shire_meadow", out, simple)



def draw_bag_end_front_wall(out, simple):
    # Open 2.2 m portal; three separate UCX boxes, never one solid doorway blocker.
    for x in (-2.12, 2.12):
        box("PlasterEntryWing", (x, 0, 1.36), (1.55, 0.34, 2.72),
            "bagend_plaster", out, 0.045 if not simple else 0)
    box("PlasterEntryLintel", (0, 0, 3.04), (5.68, 0.34, 0.62),
        "bagend_plaster", out, 0.033 if not simple else 0)
    torus("CircularDoorPortalTrim", (0, -0.20, 1.23),
          1.20, 0.10, "oak_timber", out,
          20 if simple else 44, (math.pi / 2, 0, 0))
    if not simple:
        for x in (-2.55, 2.55):
            box("PlasterEdgeTrim", (x, -0.25, 1.37),
                (0.13, 0.14, 2.57), "oak_timber", out)


def draw_round_room_wall_arc(out, simple):
    # Sixty-degree modular interior wall, five separate blockers against wall only.
    for i in range(5):
        angle = (i - 2) * math.radians(14)
        radius = 3.10
        x, y = math.sin(angle) * radius, -math.cos(angle) * radius
        o = box("RoundRoomWallPanel", (x, y, 1.34),
                (0.83, 0.28, 2.68), "bagend_plaster", out,
                0.02 if not simple else 0)
        o.rotation_euler[2] = angle
        if not simple:
            o2 = box("CurvedOakSkirting", (x, y - 0.17, 0.15),
                     (0.83, 0.11, 0.29), "oak_timber", out)
            o2.rotation_euler[2] = angle


def draw_round_room_floor(out, simple):
    cylinder("RoundRoomWalkableFloor", (0, 0, 0.08),
             3.16, 0.15, "oak_timber", out, 24 if simple else 48)
    if not simple:
        torus("FloorPerimeterTrim", (0, 0, 0.14),
              3.03, 0.07, "oak_timber", out, 32)


def draw_hearth(out, simple):
    for x in (-0.77, 0.77):
        box("HearthStoneSide", (x, 0, 0.83),
            (0.58, 0.53, 1.62), "mossy_stone", out)
    box("HearthOverhang", (0, 0, 1.78), (2.23, 0.67, 0.28),
        "mossy_stone", out, 0.018 if not simple else 0)
    box("HearthBacking", (0, 0.24, 0.65), (1.12, 0.14, 1.26),
        "charred_basalt", out)
    box("HearthSill", (0, -0.27, 0.12),
        (2.15, 0.80, 0.20), "mossy_stone", out)


def draw_bookcase(out, simple):
    for x in (-0.96, 0.96):
        box("ShelfVertical", (x, 0, 1.08), (0.13, 0.42, 2.17),
            "oak_timber", out)
    for z in (0.12, 0.64, 1.17, 1.70, 2.18):
        box("ShelfBoard", (0, 0, z),
            (2.00, 0.50, 0.10), "oak_timber", out)
    if not simple:
        for row, z in enumerate((0.42, 0.94, 1.47)):
            for col in range(7):
                box("OriginalUnlabelledBook",
                    (-0.80 + col * 0.27, 0.0, z),
                    (0.16, 0.31, 0.37), "bagend_plaster" if (col+row)%2 else "oak_timber", out)


def draw_hobbit_bed(out, simple):
    box("ShortTimberBedFrame", (0, 0, 0.34),
        (1.96, 1.14, 0.25), "oak_timber", out, 0.02 if not simple else 0)
    box("ClothMattressProxy", (0, 0, 0.55),
        (1.75, 1.00, 0.19), "bagend_plaster", out,
        0.04 if not simple else 0)
    box("WoodHeadboard", (-0.96, 0, 0.74), (0.16, 1.18, 0.80),
        "oak_timber", out)
    if not simple:
        box("Pillow", (-0.63, 0, 0.71),
            (0.37, 0.72, 0.15), "bagend_plaster", out, 0.06)


def draw_wooden_footbridge(out, simple):
    box("BridgeDeck", (0, 0, 0.52), (5.80, 2.38, 0.22),
        "oak_timber", out, 0.01 if not simple else 0)
    for y in (-1.17, 1.17):
        for x in (-2.60, 0, 2.60):
            box("BridgeRailPost", (x, y, 1.05),
                (0.13, 0.13, 1.03), "oak_timber", out)
        box("BridgeHandrail", (0, y, 1.44),
            (5.65, 0.13, 0.14), "oak_timber", out)
    if not simple:
        for x in (-2.35, -1.17, 0, 1.17, 2.35):
            box("BridgeCrossPlank", (x, 0, 0.65),
                (0.10, 2.20, 0.025), "oak_timber", out)


def draw_mill_wheel(out, simple):
    torus("MillWheelRim", (0, 0, 1.28),
          1.17, 0.145, "oak_timber", out, 16 if simple else 32,
          (math.pi / 2, 0, 0))
    cylinder("MillWheelAxle", (0, 0, 1.28),
             0.18, 0.38, "oak_timber", out, 12,
             (math.pi / 2, 0, 0))
    for i in range(6 if not simple else 4):
        a = i * math.pi / (6 if not simple else 4)
        o = box("Spoke", (0, 0, 1.28), (0.12, 0.15, 2.08),
                "oak_timber", out)
        o.rotation_euler[1] = a
    # Static source component only. Rotation requires a future UE actor.


def draw_party_canopy(out, simple):
    for x in (-2.05, 2.05):
        for y in (-1.28, 1.28):
            box("PartyShelterPole", (x, y, 1.40),
                (0.13, 0.13, 2.80), "oak_timber", out)
    for x in (-1.04, 1.04):
        p = box("CanopyClothPanel", (x, 0, 2.92),
                (2.40, 3.05, 0.09), "bagend_plaster", out,
                0.025 if not simple else 0)
        p.rotation_euler[1] = -0.25 if x < 0 else 0.25
    if not simple:
        box("CanopyRidgeBeam", (0, 0, 3.20),
            (0.15, 3.2, 0.15), "oak_timber", out)


def draw_stone_path(out, simple):
    box("StoneFootpathBase", (0, 0, 0.052),
        (3.30, 2.70, 0.09), "shire_earth", out)
    if not simple:
        for x in (-1.02, 0.03, 1.08):
            for y in (-0.84, 0.85):
                box("FlatSteppingStone", (x, y, 0.107),
                    (0.67, 0.54, 0.025), "mossy_stone", out,
                    0.018)


def draw_lantern_post(out, simple):
    cylinder("OakLanternPost", (0, 0, 1.15),
             0.11, 2.30, "oak_timber", out, 8 if simple else 12)
    box("HangingLanternFrame", (0, -0.25, 2.28),
        (0.32, 0.37, 0.48), "charred_basalt", out)
    if not simple:
        box("LightProxyNotEmissive", (0, -0.25, 2.29),
            (0.25, 0.38, 0.34), "bagend_plaster", out)
        box("LanternTop", (0, -0.25, 2.62),
            (0.44, 0.50, 0.12), "oak_timber", out)


def draw_village_well(out, simple):
    cylinder("StoneWellWall", (0, 0, 0.70),
             0.87, 1.12, "mossy_stone", out, 12 if simple else 24)
    torus("UpperStoneRim", (0, 0, 1.26),
          0.86, 0.11, "mossy_stone", out, 12 if simple else 24)
    for x in (-0.87, 0.87):
        box("WellRoofPost", (x, 0, 1.72),
            (0.11, 0.12, 1.36), "oak_timber", out)
    box("WellCrossBeam", (0, 0, 2.38),
        (2.02, 0.13, 0.14), "oak_timber", out)
    if not simple:
        cylinder("WellWoodenWinch", (0, 0, 1.98),
                 0.15, 1.30, "oak_timber", out, 12, rotation=(0, math.pi/2, 0))


def make_one(asset, level, out):
    global PARTS
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.scale_length = 1.0
    PARTS = []
    simple = (level == 1)
    {"RoundDoor": draw_round_door, "PicketFence": draw_fence,
     "PartyTable": draw_party_table, "GardenCart": draw_garden_cart,
     "RoundWindow": draw_round_window, "GardenHedge": draw_garden_hedge,
     "OakTree": draw_oak_tree, "StorageBarrel": draw_storage_barrel,
     "FarmGate": draw_farm_gate, "GardenPlanter": draw_garden_planter,
     "BagEndFrontWall": draw_bag_end_front_wall,
     "RoundRoomWallArc": draw_round_room_wall_arc,
     "RoundRoomFloor": draw_round_room_floor,
     "Hearth": draw_hearth,
     "Bookcase": draw_bookcase,
     "HobbitBed": draw_hobbit_bed,
     "WoodenFootbridge": draw_wooden_footbridge,
     "MillWheel": draw_mill_wheel,
     "PartyCanopy": draw_party_canopy,
     "StonePath": draw_stone_path,
     "LanternPost": draw_lantern_post,
     "VillageWell": draw_village_well }[asset](out, simple)
    visual_name = "SM_Sh" + asset + "_LOD" + str(level)
    visual = join_visual(visual_name)
    bound = {
        "RoundDoor": ((0, 0, 1.11), (1.82, 0.16, 2.20)),
        "PicketFence": ((0, 0, 0.54), (3.0, 0.14, 1.06)),
        "PartyTable": ((0, 0, 0.75), (2.40, 0.90, 0.15)),
        "GardenCart": ((0, 0, 0.75), (1.53, 0.84, 0.60)),
        "RoundWindow": ((0, 0.02, 1.20), (1.12, 0.15, 1.17)),
        "GardenHedge": ((0, 0, 0.68), (3.55, 0.85, 1.35)),
        "OakTree": ((0, 0, 1.45), (0.48, 0.48, 2.92)),
        "StorageBarrel": ((0, 0, 0.45), (0.82, 0.82, 0.89)),
        "FarmGate": ((0, 0, 0.67), (2.42, 0.20, 1.37)),
        "GardenPlanter": ((0, 0, 0.37), (1.57, 0.83, 0.75)),
        "BagEndFrontWall": ((0, 0, 1.55), (5.68, 0.38, 3.34)),
        "RoundRoomWallArc": ((0, -2.9, 1.34), (3.4, 0.9, 2.68)),
        "RoundRoomFloor": ((0, 0, 0.08), (6.32, 6.32, 0.15)),
        "Hearth": ((0, 0.0, 0.91), (2.24, 0.62, 1.82)),
        "Bookcase": ((0, 0.0, 1.08), (2.02, 0.54, 2.17)),
        "HobbitBed": ((0, 0, 0.33), (2.00, 1.18, 0.67)),
        "WoodenFootbridge": ((0, 0, 0.52), (5.80, 2.42, 0.22)),
        "MillWheel": ((0, 0, 1.28), (2.47, 0.3, 2.50)),
        "PartyCanopy": ((0, 0, 1.45), (4.35, 2.68, 2.90)),
        "StonePath": ((0, 0, 0.052), (3.3, 2.70, 0.09)),
        "LanternPost": ((0, 0, 1.15), (0.24, 0.24, 2.3)),
        "VillageWell": ((0, 0, 0.7), (1.76, 1.76, 1.3)),
    }
    # UCX boxes deliberately avoid obstructing portals, canopy passages, bridge
    # traversal or the hollow room wall. Engine collision needs separate QA.
    collision_groups = {
        "BagEndFrontWall": [
            ((-2.12, 0, 1.36), (1.55, 0.34, 2.72), 0),
            ((2.12, 0, 1.36), (1.55, 0.34, 2.72), 0),
            ((0, 0, 3.04), (5.68, 0.34, 0.62), 0),
        ],
        "RoundRoomWallArc": [
            ((math.sin((i-2)*math.radians(14))*3.1,
              -math.cos((i-2)*math.radians(14))*3.1, 1.34),
             (0.83, 0.28, 2.68), (i-2)*math.radians(14))
            for i in range(5)
        ],
        "Hearth": [
            ((-0.77, 0, 0.83), (0.58, 0.53, 1.62), 0),
            ((0.77, 0, 0.83), (0.58, 0.53, 1.62), 0),
            ((0, 0, 1.78), (2.23, 0.67, 0.28), 0),
        ],
        "WoodenFootbridge": [
            ((0, 0, 0.52), (5.8, 2.38, 0.22), 0),
            ((0, -1.17, 1.44), (5.65, 0.13, 0.14), 0),
            ((0, 1.17, 1.44), (5.65, 0.13, 0.14), 0),
        ],
        "PartyCanopy": [
            ((x, y, 1.40), (0.13, 0.13, 2.80), 0)
            for x in (-2.05, 2.05) for y in (-1.28, 1.28)
        ],
    }
    colliders = []
    for index, (location, dimensions, z_angle) in enumerate(
        collision_groups.get(asset, [(*bound[asset], 0)])
    ):
        col = collider(visual_name, location, dimensions, index)
        col.rotation_euler[2] = z_angle
        colliders.append(col)
    bpy.ops.object.select_all(action="DESELECT")
    visual.select_set(True)
    for col in colliders:
        col.select_set(True)
    bpy.context.view_layer.objects.active = visual
    meshes = out / "meshes"
    meshes.mkdir(parents=True, exist_ok=True)
    fbx = meshes / (visual_name + ".fbx")
    bpy.ops.export_scene.fbx(
        filepath=str(fbx), use_selection=True, object_types={"MESH"},
        mesh_smooth_type="FACE", add_leaf_bones=False,
        use_mesh_modifiers=True, apply_unit_scale=True, global_scale=1.0,
        axis_forward="-Y", axis_up="Z", path_mode="RELATIVE",
        bake_anim=False, embed_textures=False)
    fbx_header = fbx.read_bytes()[:27]
    if not fbx_header.startswith(b"Kaydara FBX Binary"):
        raise ValueError("FBX_NOT_BINARY")
    binary_version = int.from_bytes(fbx_header[23:27], "little")
    if binary_version != 7400:
        raise ValueError(f"FBX_VERSION_NOT_7400: {binary_version}")
    original_polys = len(visual.data.polygons)
    # Physical file reimport: checks mesh survives FBX export, independently of
    # the original Blender scene. NOT the Unreal Asset Registry import gate.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(fbx), use_anim=False)
    imports = [o for o in bpy.data.objects if o.type == "MESH"]
    drawable = [o for o in imports if not o.name.startswith("UCX_")]
    blockers = [o for o in imports if o.name.startswith("UCX_")]
    if len(drawable) != 1 or len(blockers) < 1:
        raise ValueError("FBX_REIMPORT_OBJECT_COUNT " + str([(o.name, o.type) for o in imports]))
    mesh = drawable[0].data
    if len(mesh.polygons) <= 0 or len(mesh.polygons) > 15000 or not mesh.uv_layers:
        raise ValueError("FBX_REIMPORT_TOPOLOGY_OR_UV_INVALID")
    if any(p.area <= 0.00000001 for p in mesh.polygons):
        raise ValueError("FBX_REIMPORT_DEGENERATE_FACE")
    return {
        "asset": asset, "lod": level, "path": f"meshes/{fbx.name}",
        "bytes": fbx.stat().st_size, "sha256": sha(fbx),
        "source_polygons": original_polys,
        "reimport_polygons": len(mesh.polygons),
        "reimport_uv_layers": len(mesh.uv_layers),
        "material_slots": len(drawable[0].material_slots),
        "collider_count": len(blockers),
        "ucx_boxes": [
            {"center_m": [float(v) for v in location],
             "dimensions_m": [float(v) for v in dimensions],
             "yaw_rad": float(z_angle)}
            for location, dimensions, z_angle in collision_groups.get(
                asset, [(*bound[asset], 0)]
            )
        ],
        "collision_strategy": "UCX_SIMP_CONVEX",
        "target": "UE4.27.2", "export_format": "FBX_BINARY_7400",
        "quality_boundary": "BLENDER_REIMPORT_QC_ONLY_NOT_UNREAL_IMPORT"
    }


def main(out):
    out = out.resolve()
    if not (out / "materials_receipt.json").is_file():
        raise RuntimeError("REQUIRE_MATERIAL_RECEIPT_FIRST")
    meshes = [make_one(asset, lod, out) for asset in MODELS for lod in (0, 1)]
    receipt = {
        "id": SOURCE_NAME, "status": "GENERATED_BINARY_FBX_BLENDER_REIMPORT_QC",
        "provenance": "ORIGINAL_PROJECT_PROCEDURAL_GEOMETRY",
        "generator_sha256": sha(Path(__file__)), "blender_version": bpy.app.version_string,
        "asset_count": len(MODELS), "fbx_count": len(meshes),
        "objects": meshes, "runtime_imported": False, "skeletal_or_animated": False,
        "ue4_import_proof": None, "pie_proof": None, "device_fps": None,
    }
    (out / "fbx_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"SHIRE_BINARY_FBX_GENERATED assets={len(MODELS)} files={len(meshes)} blender={bpy.app.version_string}")


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) != 2 or args[0] != "--out":
        raise SystemExit("usage: blender -b --python ... -- --out OUTPUT")
    main(Path(args[1]))
