#!/usr/bin/env python3
"""Blender source-only animation export for an already normalized CC0 skeletal FBX."""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    p=argparse.ArgumentParser()
    p.add_argument("--rig",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args(argv)
    rig=Path(args.rig).resolve()
    out=Path(args.out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(rig))
    armatures=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"]
    meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
    if len(armatures)!=1 or not meshes:
        raise ValueError("FRODO_ANIMATION_INVALID_SKINNED_RIG")
    arm=armatures[0]
    skinned=[o for o in meshes if any(m.type=="ARMATURE" and m.object==arm for m in o.modifiers)]
    if not skinned:
        raise ValueError("FRODO_ANIMATION_SKIN_BINDING_MISSING")
    names={}
    for pb in arm.pose.bones:
        n=pb.name.lower()
        if n.startswith(("mch_","org_")): continue
        side=("L" if n.endswith((".l","_l","left")) else "R" if n.endswith((".r","_r","right")) else None)
        if not side: continue
        role=next((role for role,parts in {
            "thigh":("thigh","upleg","upperleg"),
            "shin":("shin","calf","lowerleg"),
            "arm":("upper_arm","upperarm","uparm"),
            "forearm":("forearm","lowerarm","lower_arm")}.items()
            if any(v in n for v in parts)),None)
        if role:
            key=(role,side)
            score=(5 if n.startswith("def") else 0)+(3 if pb.bone.use_deform else 0)
            if key not in names or score>names[key][0]: names[key]=(score,pb)
    required={(role,side) for role in ("thigh","shin","arm","forearm") for side in ("L","R")}
    if required-set(names):
        raise ValueError("FRODO_ANIMATION_MISSING_LIMBS "+str(sorted(required-set(names))))
    bpy.context.scene.render.fps=30
    rows=[]
    for clip,frames,stride,arm_swing in (("Idle",48,0.0,0.025),("Walk",32,0.44,0.30),("Run",24,0.72,0.55)):
        arm.animation_data_clear()
        for pb in arm.pose.bones:
            pb.rotation_mode="XYZ"
            pb.rotation_euler=(0,0,0)
        action=bpy.data.actions.new("AN_FrodoSource_"+clip)
        arm.animation_data_create().action=action
        for frame in range(1,frames+2):
            t=2*math.pi*((frame-1)%frames)/frames
            for side in ("L","R"):
                phase=t+(0 if side=="L" else math.pi)
                sine=math.sin(phase)
                motion={
                    "thigh":stride*sine,
                    "shin":max(0,-sine)*stride*0.7,
                    "arm":(-arm_swing*sine if stride else arm_swing*math.sin(t)*(1 if side=="L" else -1)),
                    "forearm":(-0.14 if clip=="Walk" else -0.32 if clip=="Run" else 0.0)}
                for role,angle in motion.items():
                    pb=names[(role,side)][1]
                    pb.rotation_euler=(angle,0,0)
                    pb.keyframe_insert(data_path="rotation_euler",frame=frame,group=pb.name)
        bpy.context.scene.frame_start=1
        bpy.context.scene.frame_end=frames+1
        bpy.context.scene.frame_set(1)
        bpy.ops.object.select_all(action="DESELECT")
        for obj in [arm]+skinned:
            obj.hide_set(False)
            obj.select_set(True)
        bpy.context.view_layer.objects.active=arm
        path=out/("AN_FrodoSource_"+clip+".fbx")
        bpy.ops.export_scene.fbx(filepath=str(path),check_existing=False,use_selection=True,
            object_types={"ARMATURE","MESH"},add_leaf_bones=False,use_armature_deform_only=True,
            primary_bone_axis="Y",secondary_bone_axis="X",bake_anim=True,
            bake_anim_use_nla_strips=False,bake_anim_use_all_actions=False,
            bake_anim_simplify_factor=0.0,path_mode="AUTO",embed_textures=False)
        raw=path.read_bytes()
        if not raw.startswith(b"Kaydara FBX Binary") or int.from_bytes(raw[23:27],"little") not in (7400,7500):
            raise ValueError("FRODO_ANIMATION_NOT_BINARY_FBX")
        rows.append({"clip":clip,"frames":frames+1,"path":path.name,"sha256":digest(path),"bytes":len(raw)})
    for row in rows:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=str(out/row["path"]))
        bones=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"]
        curves=sum(len(a.fcurves) for a in bpy.data.actions)
        keys=sum(len(fc.keyframe_points) for a in bpy.data.actions for fc in a.fcurves)
        if len(bones)!=1 or curves<4 or keys<12:
            raise ValueError("FRODO_ANIMATION_REIMPORT_FAILED "+row["clip"])
        row["reimport_curves"]=curves
        row["reimport_keys"]=keys
    receipt={"status":"SOURCE_ANIMATION_FBX_REIMPORTED","source_rig_sha256":digest(rig),
        "fps":30,"clips":rows,"unreal_imported":False,"pie_tested":False,
        "device_tested":False,"visually_accepted":False,"final_character":False}
    (out/"frodo_locomotion_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print("FRODO_SOURCE_LOCOMOTION_FBX_PASS clips=3 reimported=3")
if __name__=="__main__": main()
