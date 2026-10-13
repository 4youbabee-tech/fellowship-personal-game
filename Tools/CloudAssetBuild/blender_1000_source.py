#!/usr/bin/env python3
"""Build 20 hosted shards x 50 physical FBX supporting scene props (source-only).

Procedural originals, not hero landmarks, animated characters or Unreal assets.
Every file is Blender-reimported with UCX, UV and SHA256 source receipt.
"""
import hashlib
import json
import sys
from pathlib import Path
import bpy

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import blender_shire as sh
import blender_regions as reg
ROOT=HERE.parents[1]
PLAN=ROOT/"Data/WholeGameRegionProductionPacketsV1.json"
ROLES=("BridgePost","FieldMarker","TimberStack","StoneKerb","WorkBench",
       "WaterStake","ShelterFrame","MarketTable","TrailBeacon","WallPier")
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def piece(index,out):
    regions=[x["region_id"] for x in json.loads(PLAN.read_text())["packets"]]
    if len(regions)!=28: raise RuntimeError("REGION_DRIFT")
    region=regions[index%28]
    role=ROLES[(index//28)%len(ROLES)]
    variant=index//280
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sh.PARTS=[]
    category=reg.GROUP_FOR[region]
    material=reg.MATERIAL_FOR[category]
    span=1.0+0.16*variant+0.025*(index%28)
    tall=0.7+0.14*variant+0.035*(index%7)
    if role in ("BridgePost","FieldMarker","WaterStake","TrailBeacon","WallPier"):
        sh.box("Footing",(0,0,.12),(span,.72,.24),material,out)
        for x in (-span*.32,span*.32):
            sh.box("Upright",(x,0,tall/2),(.17,.20,tall),"oak_timber" if category=="pastoral" else material,out)
        sh.box("Cap",(0,0,tall),(span,.25,.12),material,out)
    elif role in ("TimberStack","StoneKerb"):
        for n in range(3+variant):
            sh.box("Course",(0,0,.13+n*.19),(span*(1+.03*n),.50,.20),material,out)
    else:
        for x in (-span*.37,span*.37):
            sh.box("Support",(x,0,tall/2),(.18,.42,tall),material,out)
        sh.box("Platform",(0,0,tall),(span,.95,.13),material,out)
        if variant%2:
            sh.box("Shelf",(0,0,tall*.45),(span*.85,.68,.09),material,out)
    name=f"SM_WG_{region}_{role}_V{variant}_I{index:04d}"
    mesh=sh.join_visual(name)
    if not 0<len(mesh.data.polygons)<=12000: raise RuntimeError("POLYGON_BUDGET")
    sh.collider(name,(0,0,max(tall,.5)/2),(span,.95,max(tall,.5)),0)
    folder=out/"fbx";folder.mkdir(parents=True,exist_ok=True)
    dest=folder/(name+".fbx")
    bpy.ops.object.select_all(action="DESELECT")
    mesh.select_set(True)
    for obj in bpy.data.objects:
        if obj.name.startswith("UCX_"+name+"_"):obj.select_set(True)
    bpy.context.view_layer.objects.active=mesh
    bpy.ops.export_scene.fbx(filepath=str(dest),use_selection=True,object_types={"MESH"},
        mesh_smooth_type="FACE",use_mesh_modifiers=True,apply_unit_scale=True,
        global_scale=1.0,axis_forward="-Y",axis_up="Z",path_mode="RELATIVE",
        bake_anim=False,embed_textures=False)
    data=dest.read_bytes()
    if not data.startswith(b"Kaydara FBX Binary") or int.from_bytes(data[23:27],"little")!=7400:
        raise RuntimeError("FBX_FORMAT")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(dest),use_anim=False)
    meshes=[o for o in bpy.data.objects if o.type=="MESH"]
    visible=[o for o in meshes if not o.name.startswith("UCX_")]
    colliders=[o for o in meshes if o.name.startswith("UCX_")]
    if len(visible)!=1 or len(colliders)!=1 or not visible[0].data.uv_layers:
        raise RuntimeError("REIMPORT_COLLISION_UV")
    if any(p.area<=1e-8 for p in visible[0].data.polygons):
        raise RuntimeError("DEGENERATE_FACE")
    return {"index":index,"region":region,"role":role,"variant":variant,
            "path":"fbx/"+dest.name,"sha256":digest(dest),"bytes":len(data),
            "uv_layers":len(visible[0].data.uv_layers),"ucx":len(colliders),
            "warehouse_persisted":False,"unreal_imported":False}

def main(shard,out):
    if not 0<=shard<20:raise RuntimeError("SHARD_RANGE")
    out.mkdir(parents=True,exist_ok=True)
    records=[]
    for index in range(shard*50,(shard+1)*50):
        records.append(piece(index,out))
        print(f"PRODUCED_AND_REIMPORTED index={index} of=1000",flush=True)
    if len(records)!=50 or len({x["sha256"] for x in records})!=50:
        raise RuntimeError("SHARD_DUPLICATE")
    (out/"receipt.json").write_text(json.dumps({"shard":shard,"source_only":True,
         "records":records,"warehouse_persisted":False,"unreal_imported":False},indent=2))
    print(f"SOURCE_SHARD_QC_PASS shard={shard} files=50",flush=True)

if __name__=="__main__":
    args=sys.argv[sys.argv.index("--")+1:]
    if len(args)!=3 or args[0]!="--shard":raise SystemExit("usage: ... -- --shard N OUT")
    main(int(args[1]),Path(args[2]).resolve())
