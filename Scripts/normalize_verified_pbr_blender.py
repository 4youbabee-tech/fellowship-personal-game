"""Blender worker for derived P1C01 static PBR FBX. The warehouse originals are immutable."""
import argparse, math, os, sys
import bmesh
import bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verified_pbr_uv_repair import repaired_face_uvs

def require(ok, why):
    if not ok: raise RuntimeError("P1C01_FBX_NORMALIZE_FAIL:"+why)

def clean_mesh(obj):
    bpy.context.view_layer.objects.active=obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bm=bmesh.from_edit_mesh(obj.data)
    before=len(bm.faces)
    degenerate=[f for f in bm.faces if (not math.isfinite(f.calc_area())) or f.calc_area()<=1e-11]
    if degenerate:
        bmesh.ops.delete(bm, geom=degenerate, context='FACES')
    # Never weld UV seam/hard-normal vertices: remove only topology orphaned by face cleanup.
    orphans=[v for v in bm.verts if not v.link_faces]
    if orphans: bmesh.ops.delete(bm, geom=orphans, context='VERTS')
    bm.normal_update()
    uv_layer=bm.loops.layers.uv.active
    require(uv_layer is not None, "MISSING_UV_LAYER:"+obj.name)
    repaired_uv_faces=0
    for face in bm.faces:
        loops=list(face.loops)
        authored=tuple((float(loop[uv_layer].uv.x),float(loop[uv_layer].uv.y)) for loop in loops)
        positions=tuple(tuple(float(x) for x in loop.vert.co) for loop in loops)
        normal=tuple(float(x) for x in face.normal)
        corrected,changed=repaired_face_uvs(authored,positions,normal)
        if changed:
            for loop,uv in zip(loops,corrected):
                loop[uv_layer].uv=uv
            repaired_uv_faces+=1
    print("P1C01_FBX_UV_TANGENT_REPAIR asset_mesh="+obj.name+
          " corrected_faces="+str(repaired_uv_faces)+" valid_uv_untouched=yes no_vertex_weld=yes",flush=True)
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)
    removed=before-len(obj.data.polygons)
    if removed:
        print("P1C01_FBX_NORMALIZE_CLEANED asset_mesh="+obj.name+" removed_degenerate_faces="+str(removed),flush=True)

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
    bpy.ops.object.select_all(action='DESELECT')
    for mesh in meshes:
        clean_mesh(mesh)
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
