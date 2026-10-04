import argparse,json,math,os,re,sys,hashlib,traceback
import bpy
from mathutils import Matrix

argv=sys.argv
argv=argv[argv.index("--")+1:] if "--" in argv else []
p=argparse.ArgumentParser()
p.add_argument("--fbx",required=True); p.add_argument("--output",required=True)
args=p.parse_args(argv)

def write(r):
    os.makedirs(os.path.dirname(args.output),exist_ok=True)
    with open(args.output,"w",encoding="utf-8") as f: json.dump(r,f,indent=2,sort_keys=True)
def compact(n): return re.sub(r"[^a-z0-9]+","",n.lower())
def side(n,s):
    n=n.lower()
    return ("left" in n or ".l" in n or "_l" in n or "-l" in n or n.endswith(" l")) if s=="L" else (("right" in n or ".r" in n or "_r" in n or "-r" in n or n.endswith(" r")) if s=="R" else True)

r={"schema_version":1,"status":"HOSTED_DEFORMATION_PREFLIGHT_INFRA_FAILURE","fbx":os.path.basename(args.fbx),"reasons":[],"joint_map":{},"joint_influence_counts":{},"scenarios":[],"evidence_boundary":"Hosted normalized-FBX weighted-joint and static-pose preflight only; no UE4/retarget/runtime/PIE/device/visual/FPS acceptance."}
try:
    with open(args.fbx,"rb") as f:r["fbx_sha256"]=hashlib.sha256(f.read()).hexdigest()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if "FINISHED" not in bpy.ops.import_scene.fbx(filepath=args.fbx,use_custom_normals=True): raise RuntimeError("FBX import failed")
    arms=[o for o in bpy.context.scene.objects if o.type=="ARMATURE"]; meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
    r["armature_count"]=len(arms); r["armature_names"]=[o.name for o in arms]
    r["mesh_count"]=len(meshes); r["mesh_names"]=[o.name for o in meshes]
    if len(arms)!=1:r["reasons"].append("ARMATURE_COUNT_NOT_ONE:"+str(len(arms)))
    if not meshes:r["reasons"].append("NO_MESH_OBJECTS")
    if r["reasons"]: r["status"]="HOSTED_DEFORMATION_PREFLIGHT_REJECT";write(r);sys.exit(0)
    arm=arms[0];arm.data.pose_position="POSE"
    infl={}
    for o in meshes:
        for g in o.vertex_groups:
            c=sum(1 for v in o.data.vertices if any(x.group==g.index and x.weight>1e-5 for x in v.groups))
            if c: infl[g.name]=infl.get(g.name,0)+c
    def pick(tokens,side_id=None,exclude=()):
        rows=[]
        for b in arm.pose.bones:
            q=compact(b.name)
            if not b.bone.use_deform or (side_id and not side(b.name,side_id)) or any(x in q for x in exclude):continue
            if any(t in q for t in tokens): rows.append((infl.get(b.name,0),b))
        rows.sort(key=lambda x:(-x[0],len(x[1].name),x[1].name.lower()))
        return rows[0][1] if rows and rows[0][0]>0 else None
    specs={"pelvis":(("pelvis","hips","hip"),None,()),"spine":(("spine","chest"),None,()),"head":(("head",),None,()),"left_upper_arm":(("upperarm","uparm"),"L",("forearm","lowerarm")),"right_upper_arm":(("upperarm","uparm"),"R",("forearm","lowerarm")),"left_forearm":(("forearm","lowerarm"),"L",()),"right_forearm":(("forearm","lowerarm"),"R",()),"left_hand":(("hand",),"L",()),"right_hand":(("hand",),"R",()),"left_thigh":(("thigh","upleg","upperleg"),"L",()),"right_thigh":(("thigh","upleg","upperleg"),"R",()),"left_shin":(("shin","calf","lowerleg"),"L",()),"right_shin":(("shin","calf","lowerleg"),"R",()),"left_foot":(("foot",),"L",()),"right_foot":(("foot",),"R",())}
    joints={}
    for k,(t,s,e) in specs.items():
        b=pick(t,s,e)
        if not b:r["reasons"].append("NO_WEIGHTED_DEFORM_JOINT:"+k)
        else:joints[k]=b;r["joint_map"][k]=b.name;r["joint_influence_counts"][k]=infl.get(b.name,0)
    if r["reasons"]:r["status"]="HOSTED_DEFORMATION_PREFLIGHT_REJECT";write(r);sys.exit(0)
    def desc(c,p):
        n=c.bone.parent
        while n:
            if n==p.bone:return True
            n=n.parent
        return False
    checks=[desc(joints["left_forearm"],joints["left_upper_arm"]),desc(joints["left_hand"],joints["left_forearm"]),desc(joints["right_forearm"],joints["right_upper_arm"]),desc(joints["right_hand"],joints["right_forearm"]),desc(joints["left_shin"],joints["left_thigh"]),desc(joints["left_foot"],joints["left_shin"]),desc(joints["right_shin"],joints["right_thigh"]),desc(joints["right_foot"],joints["right_shin"]),desc(joints["head"],joints["spine"])]
    if not all(checks):r["reasons"].append("HIERARCHY_FAIL")
    weighted_meshes=[o for o in meshes if any(x.weight>1e-5 for v in o.data.vertices for x in v.groups)]
    if not weighted_meshes or any(not any(m.type=="ARMATURE" and m.object==arm for m in o.modifiers) for o in weighted_meshes):r["reasons"].append("ARMATURE_MODIFIER_LINK_MISSING")
    def pts():
        dg=bpy.context.evaluated_depsgraph_get();out=[]
        for o in meshes:
            ev=o.evaluated_get(dg);tmp=ev.to_mesh()
            try:out.extend([tuple(ev.matrix_world@v.co) for v in tmp.vertices])
            finally:ev.to_mesh_clear()
        return out
    def diag(p):
        mn=[min(float(v[i]) for v in p) for i in range(3)];mx=[max(float(v[i]) for v in p) for i in range(3)]
        return math.sqrt(sum((mx[i]-mn[i])**2 for i in range(3)))
    def reset():
        for b in arm.pose.bones:b.matrix_basis=Matrix.Identity(4)
        bpy.context.view_layer.update()
    reset();base=pts();d=diag(base);threshold=max(d*1e-5,1e-6)
    scenarios=[("shoulders",[("left_upper_arm",2,-45),("right_upper_arm",2,45)]),("elbows",[("left_forearm",0,-75),("right_forearm",0,-75)]),("knees",[("left_shin",0,65),("right_shin",0,65)]),("hands_feet",[("left_hand",1,-20),("right_hand",1,20),("left_foot",0,20),("right_foot",0,20)]),("locomotion_stress",[("left_upper_arm",0,22),("right_upper_arm",0,-22),("left_thigh",0,-28),("right_thigh",0,28),("left_shin",0,28),("right_shin",0,12)])]
    for name,rots in scenarios:
        reset()
        for k,a,deg in rots:joints[k].rotation_mode="XYZ";joints[k].rotation_euler[a]=math.radians(deg)
        bpy.context.view_layer.update();posed=pts()
        md=max(math.sqrt(sum((float(posed[i][a])-float(base[i][a]))**2 for a in range(3))) for i in range(len(base)))
        passed=md>=threshold
        r["scenarios"].append({"name":name,"passed":passed,"max_vertex_displacement":md,"min_required_displacement":threshold})
        if not passed:r["reasons"].append("NO_NONTRIVIAL_DEFORMATION:"+name)
    reset()
    r["status"]="HOSTED_DEFORMATION_PREFLIGHT_PASS" if not r["reasons"] else "HOSTED_DEFORMATION_PREFLIGHT_REJECT"
    write(r)
except Exception as e:
    r["reasons"].append("INFRA:"+str(e));r["traceback"]=traceback.format_exc(limit=8);write(r);raise
