"""Blender worker for derived P1C01 static PBR FBX. The warehouse originals are immutable."""
import argparse, math, os, sys
import bpy

def require(ok, why):
    if not ok: raise RuntimeError("P1C01_FBX_NORMALIZE_FAIL:"+why)

def inspect(objects):
    count=0
    for o in objects:
        m=o.data
        require(len(m.vertices)>=3 and len(m.polygons)>0, "EMPTY_MESH:"+o.name)
        require(len(m.uv_layers)>0, "MISSING_UV:"+o.name)
        for v in m.vertices:
            require(all(math.isfinite(float(x)) for x in v.co), "NONFINITE_VERTEX:"+o.name)
        for f in m.polygons:
            require(math.isfinite(f.area) and f.area>1e-11, "DEGENERATE_FACE:"+o.name)
            count+=1
    return count

def main(src,dst,asset):
    require(os.path.isfile(src) and os.path.abspath(src)!=os.path.abspath(dst),"INPUT_OUTPUT_OVERLAP")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    require('FINISHED' in bpy.ops.import_scene.fbx(filepath=os.path.abspath(src),use_custom_normals=True),"IMPORT_FAILED")
    meshes=sorted([o for o in bpy.context.scene.objects if o.type=='MESH'],key=lambda o:o.name)
    require(meshes and not any(o.type=='ARMATURE' for o in bpy.context.scene.objects),"NON_STATIC_FBX")
    count=inspect(meshes)
    bpy.ops.object.select_all(action='DESELECT')
    for m in meshes: m.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0]
    if len(meshes)>1: require('FINISHED' in bpy.ops.object.join(),"JOIN_FAILED")
    obj=bpy.context.view_layer.objects.active
    require(len(obj.data.polygons)==count,"GEOMETRY_LOST_ON_JOIN")
    obj.name=asset
    obj.data.name=asset
    obj.data.materials.clear()
    obj.data.materials.append(bpy.data.materials.new(name='MI_P1C01_'+asset))
    for p in obj.data.polygons: p.material_index=0
    inspect([obj])
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active=obj
    require('mesh_smooth_type' in bpy.ops.export_scene.fbx.get_rna_type().properties.keys(),"SMOOTHING_EXPORT_NOT_SUPPORTED")
    os.makedirs(os.path.dirname(os.path.abspath(dst)),exist_ok=True)
    require('FINISHED' in bpy.ops.export_scene.fbx(filepath=os.path.abspath(dst),use_selection=True,
        object_types={'MESH'},use_mesh_modifiers=True,mesh_smooth_type='FACE',
        use_tspace=True,path_mode='STRIP',add_leaf_bones=False),"EXPORT_FAILED")
    with open(dst,'rb') as f: payload=f.read()
    require(payload.startswith(b'Kaydara FBX Binary') and b'LayerElementSmoothing' in payload,"NO_EXPORTED_SMOOTHING")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    require('FINISHED' in bpy.ops.import_scene.fbx(filepath=os.path.abspath(dst)),"DERIVED_REIMPORT_FAILED")
    actual=[o for o in bpy.context.scene.objects if o.type=='MESH']
    require(len(actual)==1 and len(actual[0].data.materials)==1 and inspect(actual)==count,"DERIVED_MESH_SLOT_QC_FAILED")
    print("P1C01_FBX_NORMALIZED asset="+asset+" sourceMeshes="+str(len(meshes))+
          " derivedMeshes=1 slots=1 smoothing=yes polygons="+str(count),flush=True)

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    p=argparse.ArgumentParser()
    p.add_argument('--input',required=True)
    p.add_argument('--output',required=True)
    p.add_argument('--asset',required=True)
    a=p.parse_args(args)
    main(a.input,a.output,a.asset)
