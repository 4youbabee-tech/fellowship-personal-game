#!/usr/bin/env python3
"""Original Shire nature: Blender binary FBX 7400, LOD0-2, UV0, selective UCX."""
import bpy, math, random, json, hashlib, sys
from pathlib import Path
from mathutils import Vector
FAMILIES=("tree_oak","tree_elm","tree_apple","tree_willow","shrub_hedge","shrub_hawthorn","shrub_gorse","rock_field","rock_river","grass_meadow","flower_wild","garden_reed")
TRIS_LIMIT=(11000,5500,2600)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def material(n,color):
 m=bpy.data.materials.get(n) or bpy.data.materials.new(n); m.diffuse_color=(*color,1);return m
def create(name,typ,location,scale,mat,vertices=8):
 if typ=="cyl": bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=1,radius2=0.6,depth=1,location=location)
 elif typ=="foliage":
  bpy.ops.mesh.primitive_uv_sphere_add(segments=max(8,vertices),ring_count=max(5,vertices//2),radius=1,location=location)
 elif typ=="ico": bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=location)
 else: bpy.ops.mesh.primitive_cube_add(size=1,location=location)
 ob=bpy.context.object;ob.name=name;ob.scale=scale;ob.data.materials.append(mat)
 if typ=="foliage":
  for poly in ob.data.polygons:poly.use_smooth=True
 return ob
def branch(a,b,r,mat,steps=7):
 mid=(Vector(a)+Vector(b))/2; direction=Vector(b)-Vector(a)
 ob=create("NaturalBranch","cyl",mid,(r,r,direction.length),mat,steps)
 ob.rotation_euler=direction.to_track_quat('Z','Y').to_euler(); return ob
def build(family,lod,out):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 rng=random.Random(20261011+FAMILIES.index(family)*17)
 bark=material("M_Sh_Bark",(0.24,0.14,0.07));leaf=material("M_Sh_Leaf",(0.16,0.39,0.11))
 dry=material("M_Sh_Dry",(0.43,0.34,0.12));rock=material("M_Sh_Stone",(0.36,0.39,0.34))
 flower=material("M_Sh_Flower",(0.61,0.35,0.44))
 nfactor=(1,.55,.27)[lod];parts=[]
 if family.startswith("tree"):
  ht={"tree_oak":7,"tree_elm":8,"tree_apple":4.4,"tree_willow":7.7}[family]
  spread={"tree_oak":3.1,"tree_elm":2.3,"tree_apple":2.1,"tree_willow":2.6}[family]
  parts.append(branch((0,0,0),(0,0,ht*.73),.22 if family!="tree_apple" else .17,bark,10 if lod==0 else 6))
  count=max(3,round(10*nfactor))
  for i in range(count):
   a=i*2*math.pi/count;z=ht*(.46+.32*i/count);x=spread*.67*math.cos(a);y=spread*.67*math.sin(a)
   parts.append(branch((0,0,z),(x,y,z+ht*.13),.065,bark,6 if lod<2 else 4))
  leafcount=max(4,round((22 if family=="tree_willow" else 18)*nfactor))
  for i in range(leafcount):
   a=i*2.39996; rad=spread*math.sqrt((i+.5)/leafcount)*.8
   x=rad*math.cos(a);y=rad*math.sin(a);z=ht*(.68+.15*rng.random())
   if family=="tree_willow":z-=rad*.22
   scale=(spread*.38,spread*.30,ht*(.17 if family!="tree_willow" else .23))
   parts.append(create("FoliageCluster","foliage",(x,y,z),scale,leaf,14 if lod==0 else 10 if lod==1 else 8))
 elif family.startswith("shrub"):
  for i in range(max(3,round(13*nfactor))):
   a=i*2.39996;rad=(i%6)/6*1.08
   x=rad*math.cos(a);y=rad*math.sin(a);z=.52+rng.uniform(-.13,.15)
   parts.append(create("BushCluster","foliage",(x,y,z),(.5,.47,.49),leaf if family!="shrub_gorse" else dry,12 if lod==0 else 10 if lod==1 else 8))
 elif family.startswith("rock"):
  for i in range(max(1,round(5*nfactor))):
   x=rng.uniform(-1,1);y=rng.uniform(-.75,.75);h=rng.uniform(.3,.6)
   parts.append(create("Rock","ico",(x,y,h*.42),(rng.uniform(.35,.8),rng.uniform(.35,.7),h),rock))
 elif family=="grass_meadow":
  for i in range(max(6,round(32*nfactor))):
   x=rng.uniform(-.7,.7);y=rng.uniform(-.7,.7);h=rng.uniform(.3,.9)
   parts.append(create("GrassBlade","cube",(x,y,h/2),(.02,.035,h),leaf))
 elif family=="flower_wild":
  for i in range(max(3,round(15*nfactor))):
   x=rng.uniform(-.85,.85);y=rng.uniform(-.85,.85);h=rng.uniform(.35,.65)
   parts.append(branch((x,y,0),(x,y,h),.012,leaf,4))
   parts.append(create("FlowerHead","ico",(x,y,h),(.075,.07,.04),flower))
 else:
  for i in range(max(4,round(18*nfactor))):
   x=rng.uniform(-.5,.5);y=rng.uniform(-.5,.5);h=rng.uniform(.8,1.7)
   parts.append(branch((x,y,0),(x+.08,y,h),.014,dry,4))
 bpy.ops.object.select_all(action='DESELECT')
 for ob in parts:ob.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();visual=bpy.context.object
 name="SM_Sh_"+family+"_LOD"+str(lod);visual.name=name
 bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 bpy.context.view_layer.objects.active=visual;bpy.ops.object.mode_set(mode='EDIT')
 bpy.ops.mesh.select_all(action='SELECT')
 bpy.ops.uv.smart_project(island_margin=.01)
 bpy.ops.object.mode_set(mode='OBJECT')
 polys=len(visual.data.polygons)
 if not 0<polys<TRIS_LIMIT[lod] or not visual.data.uv_layers:raise ValueError("INVALID_GEOMETRY "+name+" "+str(polys))
 colliders=[]
 if family.startswith("tree"):
  colliders.append(create("UCX_"+name+"_00","cube",(0,0,ht*.36),(.46,.46,ht*.72),bark))
 elif family.startswith("rock"):
  colliders.append(create("UCX_"+name+"_00","cube",(0,0,.27),(1.8,1.5,.6),rock))
 bpy.ops.object.select_all(action='DESELECT');visual.select_set(True)
 for ob in colliders:ob.select_set(True)
 bpy.context.view_layer.objects.active=visual
 path=out/"meshes"/(name+".fbx");path.parent.mkdir(parents=True,exist_ok=True)
 bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},mesh_smooth_type='FACE',add_leaf_bones=False,axis_forward='-Y',axis_up='Z',bake_anim=False,embed_textures=False)
 if not path.read_bytes().startswith(b'Kaydara FBX Binary') or int.from_bytes(path.read_bytes()[23:27],'little')!=7400:raise ValueError("FBX_VERSION")
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(path),use_anim=False)
 imported=[ob for ob in bpy.data.objects if ob.type=='MESH' and not ob.name.startswith("UCX_")]
 if len(imported)!=1 or len(imported[0].data.polygons)<1 or not imported[0].data.uv_layers:raise ValueError("REIMPORT "+name)
 return {'family':family,'lod':lod,'path':'meshes/'+path.name,'sha256':sha(path),'bytes':path.stat().st_size,'source_polygons':polys,'reimport_polygons':len(imported[0].data.polygons),'reimport_uv0':True,'colliders':len(colliders),'material_slots':len(imported[0].material_slots)}
def main(out):
 out.mkdir(parents=True,exist_ok=True)
 receipt=[build(f,l,out) for f in FAMILIES for l in range(3)]
 for f in FAMILIES:
  counts=[x['source_polygons'] for x in receipt if x['family']==f]
  if not counts[0]>counts[1]>counts[2]:raise ValueError('LOD_NOT_DECREASING '+f+str(counts))
 info={'status':'BLENDER_SOURCE_BINARY_FBX_REIMPORTED_NOT_UE','engine':'UE4.27.2','families':len(FAMILIES),'fbx_count':len(receipt),'blender':bpy.app.version_string,'source':'ORIGINAL_PROJECT_PROCEDURAL','runtime_imported':False,'objects':receipt}
 (out/'nature_receipt.json').write_text(json.dumps(info,indent=2)+'\n')
 print('NATURE_BLENDER_BINARY_REIMPORT_PASS',len(FAMILIES),len(receipt))
if __name__=='__main__':
 a=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 if len(a)!=2 or a[0]!='--out':raise SystemExit('usage: --out PATH')
 main(Path(a[1]))
