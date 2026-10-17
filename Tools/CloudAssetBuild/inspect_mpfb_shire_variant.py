"""Reimport, stress and render the actual exported source study; never UE proof."""
import bpy,sys,json,math,argparse
from pathlib import Path
from mathutils import Vector
parser=argparse.ArgumentParser()
parser.add_argument('--root',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
root=args.root.resolve(strict=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(next(root.glob('*.fbx'))))
for img in bpy.data.images:
 if img.source=='FILE':
  p=root/'Textures'/Path(img.filepath).name
  if p.is_file():img.filepath=str(p);img.reload()
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
sys.path.insert(0,str(Path(__file__).resolve().parent))
from mpfb_pose_qc import inspect_deform_and_pose
body=max(meshes,key=lambda o:len(o.data.vertices))
weighted,pose=inspect_deform_and_pose(body,rig)
report={'bones':len(rig.data.bones),'meshes':[{'name':o.name,'vertices':len(o.data.vertices),'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'materials':len(o.data.materials),'unweighted':sum(not any(g.weight>0 and o.vertex_groups[g.group].name in rig.data.bones for g in v.groups) for v in o.data.vertices),'max_influences':max(len([g for g in v.groups if g.weight>0 and o.vertex_groups[g.group].name in rig.data.bones]) for v in o.data.vertices)} for o in meshes],'weighted_body':weighted,'reimport_pose':pose}
report['total_triangles']=sum(m['triangles'] for m in report['meshes'])
hair=next((o for o in meshes if 'short01' in o.name),None)
if hair is None:raise RuntimeError('SHIRE_EXPORTED_HAIR_MESH_MISSING')
report['hair_triangles']=sum(len(p.vertices)-2 for p in hair.data.polygons)
# Fail closed on the exported bytes, rather than trusting a pre-export receipt.
if any(m['unweighted'] or m['max_influences']>4 for m in report['meshes']):
    raise RuntimeError('SHIRE_EXPORTED_SKIN_BUDGET_FAILED')
if len(rig.data.bones)!=53 or len(meshes)!=7 or body.dimensions.z<.9:
    raise RuntimeError('SHIRE_EXPORTED_HIERARCHY_OR_BODY_FAILED')
if report['hair_triangles']<8000 or report['total_triangles']>60000:
    raise RuntimeError('SHIRE_HAIR_OR_CHARACTER_TRIANGLE_BUDGET_FAILED')
if any(not m.data.uv_layers for m in meshes):
    raise RuntimeError('SHIRE_EXPORTED_UVS_MISSING')
# Stress both shoulders, elbows, hips and knees on reimported skin.
depsgraph=bpy.context.evaluated_depsgraph_get()
def coords():
    obj=body.evaluated_get(depsgraph); mesh=obj.to_mesh()
    try:return [v.co.copy() for v in mesh.vertices]
    finally:obj.to_mesh_clear()
rest=coords();stress={}
for name in ['upperarm_l','upperarm_r','lowerarm_l','lowerarm_r','thigh_l','thigh_r','calf_l','calf_r']:
    bone=rig.pose.bones.get(name);group=body.vertex_groups.get(name)
    if bone is None or group is None:raise RuntimeError('SHIRE_STRESS_JOINT_MISSING '+name)
    affected=[v.index for v in body.data.vertices if any(g.group==group.index and g.weight>=.1 for g in v.groups)]
    if len(affected)<12:raise RuntimeError('SHIRE_STRESS_INFLUENCE_SPARSE '+name)
    prior=bone.matrix_basis.copy()
    try:
        from mathutils import Matrix
        bone.matrix_basis=prior@Matrix.Rotation(math.radians(25),4,'X')
        bpy.context.view_layer.update();posed=coords()
        delta=max((posed[i]-rest[i]).length for i in affected)
        if not math.isfinite(delta) or not .0005<delta<body.dimensions.length*.65:
            raise RuntimeError('SHIRE_STRESS_MOTION_FAILED '+name)
        stress[name]={'vertices':len(affected),'max_delta':delta}
    finally:
        bone.matrix_basis=prior;bpy.context.view_layer.update()
report['exported_bilateral_stress']=stress
report['status']='EXPORTED_FBX_TECHNICAL_PASS_NOT_VISUALLY_ACCEPTED'
(root/'inspection.json').write_text(json.dumps(report,indent=2));print('FBX_REIMPORT_INSPECTION',json.dumps(report),flush=True)
coords=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box];lo=Vector(tuple(min(v[i] for v in coords) for i in range(3)));hi=Vector(tuple(max(v[i] for v in coords) for i in range(3)));center=(lo+hi)*.5;height=hi.z-lo.z
print('BOUNDS',list(lo),list(hi),flush=True)
bpy.ops.object.camera_add(location=center+Vector((height*1.15,-height*2.5,height*.2)))
cam=bpy.context.object;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=height*1.18;bpy.context.scene.camera=cam
for offset,power,size in [((2,-3,4),900,4),((-3,-1,2),650,3),((0,3,3),1000,3)]:
 bpy.ops.object.light_add(type='AREA',location=center+Vector(offset));l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(center-l.location).to_track_quat('-Z','Y').to_euler()
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.world.color=(.16,.16,.16);scene.render.resolution_x=640;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.render.filepath=str(root/'source-preview.png');bpy.ops.wm.save_as_mainfile(filepath=str(root/'inspection.blend'));bpy.ops.render.render(write_still=True)
