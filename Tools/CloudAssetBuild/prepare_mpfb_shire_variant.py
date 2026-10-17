"""Original Shire wardrobe/proportion study from a verified CC0 MPFB packet.

Source only. Never promotes a modern pilot directly into Unreal. Retains the
body, shared skeleton and portable maps; authors wool/linen wardrobe surfaces.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

import bpy
import bmesh
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mpfb_pose_qc import inspect_deform_and_pose


def material(name, color):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = .88
    return m


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--extension', type=Path, required=True)
    args = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
    source = args.source.resolve(strict=True)
    out = args.out.resolve()
    if out.exists():
        raise RuntimeError('SHIRE_VARIANT_OUTPUT_MUST_BE_NEW')
    receipt = json.loads((source/'source_receipt.json').read_text())
    fbx = source/receipt['fbx_name']
    digest = hashlib.file_digest(fbx.open('rb'), 'sha256').hexdigest()
    if receipt['license'] != 'CC0' or digest != receipt['fbx_sha256']:
        raise RuntimeError('SHIRE_VARIANT_SOURCE_PROVENANCE_FAILED')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=str(fbx))
    rig = next(o for o in bpy.context.scene.objects if o.type == 'ARMATURE')
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    body = next(o for o in meshes if o.name == 'Human_shire_export')
    clothes = next(o for o in meshes if 'male_casualsuit01' in o.name)
    hair = next(o for o in meshes if 'short01' in o.name)
    # The upstream export has clothing-mask holes in its calves. Regenerate
    # the same female phenotype from pinned MPFB CC0 geometry, WITHOUT clothes
    # masks, instead of hiding that missing-body defect behind a camera.
    import importlib
    if not any(n.endswith('mpfb.services.humanservice') for n in sys.modules):
        from mpfb_hosted_bootstrap import main as install_extension
        original_argv=sys.argv[:]
        try:
            sys.argv=[__file__,'--','--extension',str(args.extension),'--probe-only']
            install_extension()
        finally:
            sys.argv=original_argv
    from prepare_mpfb_hobbit_candidate import mpfb_api
    Human = mpfb_api('mpfb.services.humanservice', 'HumanService')
    Props = mpfb_api('mpfb.entities.objectproperties', 'HumanObjectProperties')
    Targets = mpfb_api('mpfb.services.targetservice', 'TargetService')
    Export = mpfb_api('mpfb.services.exportservice', 'ExportService')
    newbody = Human.create_human()
    Props.set_value('gender', 0.0, entity_reference=newbody)
    Targets.reapply_macro_details(newbody)
    temporary_rig = Human.add_builtin_rig(newbody, 'game_engine')
    Export.bake_modifiers_remove_helpers(newbody, bake_masks=True,
                                        bake_subdiv=True, remove_helpers=True)
    if set(b.name for b in temporary_rig.data.bones) != set(b.name for b in rig.data.bones):
        raise RuntimeError('SHIRE_REGENERATED_SKELETON_MISMATCH')
    # Imported FBX uses root unit compensation; retain the identical local
    # bind transform and skin material for the complete regenerated body.
    newbody.parent=rig
    newbody.matrix_parent_inverse=body.matrix_parent_inverse.copy()
    newbody.matrix_basis=body.matrix_basis.copy()
    for mod in newbody.modifiers:
        if mod.type=='ARMATURE':mod.object=rig
    for mat in body.data.materials:newbody.data.materials.append(mat)
    meshes.remove(body);bpy.data.objects.remove(body,do_unlink=True)
    bpy.data.objects.remove(temporary_rig,do_unlink=True)
    body=newbody;body.name='Human_shire_export';meshes.append(body)
    # Existing garment topology keeps sleeves/collar. Remove jeans below knees;
    # preserve the full skinned body underneath and all gameplay collision.
    bm = bmesh.new(); bm.from_mesh(clothes.data)
    co=clothes.matrix_world.inverted()@Vector((0,0,.47))
    normal=clothes.matrix_world.to_3x3().transposed()@Vector((0,0,1))
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
                          plane_co=co,plane_no=normal,clear_inner=True,dist=1e-6)
    bm.normal_update()
    for v in bm.verts:v.co+=v.normal*.003
    bm.to_mesh(clothes.data); bm.free(); clothes.data.update()
    linen = material('Shire_Undyed_Linen', (.56,.45,.29))
    wool = material('Shire_Walnut_Wool', (.075,.043,.021))
    vestmat = material('Shire_Moss_Waistcoat', (.055,.095,.042))
    clothes.data.materials.clear(); clothes.data.materials.append(linen); clothes.data.materials.append(wool)
    for face in clothes.data.polygons:
        z=sum((clothes.matrix_world@clothes.data.vertices[i].co).z for i in face.vertices)/len(face.vertices)
        face.material_index=0 if z>.87 else 1
    # Duplicate fitted upper garment as a sleeveless, open-front waistcoat.
    vest=clothes.copy(); vest.data=clothes.data.copy(); bpy.context.collection.objects.link(vest);vest.name='Shire_Authored_Waistcoat'
    bm=bmesh.new();bm.from_mesh(vest.data)
    for co,normal in [((0,0,.865),(0,0,1)),((0,0,1.285),(0,0,-1)),
                      ((-.177,0,0),(1,0,0)),((.177,0,0),(-1,0,0))]:
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
            plane_co=vest.matrix_world.inverted()@Vector(co),
            plane_no=vest.matrix_world.to_3x3().transposed()@Vector(normal),
            clear_inner=True,dist=1e-6)
    remove=[]
    # Bisect both opening edges first so removing the front panel leaves clean seams.
    for x in (-.052, .052):
        bmesh.ops.bisect_plane(
            bm,
            geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
            plane_co=vest.matrix_world.inverted() @ Vector((x, 0, 0)),
            plane_no=vest.matrix_world.to_3x3().transposed() @ Vector((1, 0, 0)),
            dist=1e-6,
        )
    for f in bm.faces:
        c=sum((vest.matrix_world@v.co for v in f.verts),Vector())/len(f.verts)
        if c.y<-.065 and abs(c.x)<.052:remove.append(f)
    bmesh.ops.delete(bm,geom=remove,context='FACES')
    bm.normal_update()
    for v in bm.verts:
        c=vest.matrix_world@v.co
        if c.y<-.065 and abs(c.x)<.06:
            c.x=math.copysign(.035,c.x)
            v.co=vest.matrix_world.inverted()@c
        v.co+=v.normal*.004
    bm.to_mesh(vest.data);bm.free();vest.data.materials.clear();vest.data.materials.append(vestmat)
    for f in vest.data.polygons:f.material_index=0
    # A thin applied shell gives the cut lapels and hem real cloth edge thickness.
    bpy.context.view_layer.objects.active=vest
    vest.select_set(True)
    shell=vest.modifiers.new('Shire_Waistcoat_Cloth_Edge','SOLIDIFY')
    shell.thickness=.006;shell.offset=0.0;shell.use_rim=True
    bpy.ops.object.modifier_apply(modifier=shell.name)
    meshes.append(vest)
    # Joined, head-weighted low-poly curls replace the flat short-hair crest.
    hair.data.materials.clear();hair.data.materials.append(material('Shire_Chestnut_Hair',(.055,.024,.012)))
    head_name=next((n for n in ('head','Head') if rig.data.bones.get(n)),None)
    if head_name is None:raise RuntimeError('SHIRE_CURL_HEAD_BONE_MISSING')
    head_group=hair.vertex_groups.get(head_name) or hair.vertex_groups.new(name=head_name)
    hbox=[hair.matrix_world@Vector(c) for c in hair.bound_box]
    hlo=Vector(tuple(min(v[i] for v in hbox) for i in range(3)))
    hhi=Vector(tuple(max(v[i] for v in hbox) for i in range(3)))
    hc=(hlo+hhi)*.5
    rx=max((hhi.x-hlo.x)*.43,.025);ry=max((hhi.y-hlo.y)*.43,.025)
    start_curl_vertex=len(hair.data.vertices)
    curls=0
    curl_bm=bmesh.new();curl_bm.from_mesh(hair.data)
    # Smaller clumps and overlapping rows read as curls rather than beads.
    for ring,count,lower,radius in (
        (0,16,.018,.0185),(1,14,.038,.018),(2,12,.058,.0165),
        (3,10,.078,.015),(4,6,.004,.017),
    ):
        for i in range(count):
            angle=(2*math.pi*i/count)+(ring*.13)
            if ring==4:
                x=hc.x+rx*.26*math.cos(angle);y=hc.y+ry*.22*math.sin(angle)
            else:
                radial=(.91,.82,.68,.49)[ring]
                x=hc.x+rx*radial*math.cos(angle)
                y=hc.y+ry*radial*math.sin(angle)
            z=hhi.z-lower+(.006*math.cos(angle*3) if ring<4 else 0)
            local=hair.matrix_world.inverted()@Vector((x,y,z))
            size=radius*(.91+.12*math.sin(i*2.17+ring))
            bmesh.ops.create_icosphere(curl_bm,subdivisions=2,radius=size,matrix=Matrix.Translation(local))
            curls+=1
    curl_bm.normal_update();curl_bm.to_mesh(hair.data);curl_bm.free();hair.data.update()
    head_group.add(list(range(start_curl_vertex,len(hair.data.vertices))),1.0,'REPLACE')
    # Shorter, broader silhouette. Scale the root only; all bound parts follow.
    rig.scale.x*=.84;rig.scale.y*=.88;rig.scale.z*=.70
    bpy.ops.object.select_all(action='DESELECT')
    for o in [rig]+meshes:o.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    # Four normalized deform influences per vertex is a source budget gate.
    deform={b.name for b in rig.data.bones if b.use_deform}
    for mesh in meshes:
        for v in mesh.data.vertices:
            entries=sorted([(g.weight,g.group) for g in v.groups if mesh.vertex_groups[g.group].name in deform and g.weight>0],reverse=True)
            if not entries:raise RuntimeError('SHIRE_VARIANT_UNWEIGHTED_VERTEX')
            for _,idx in entries[4:]:mesh.vertex_groups[idx].remove([v.index])
            total=sum(w for w,_ in entries[:4])
            for w,idx in entries[:4]:mesh.vertex_groups[idx].add([v.index],w/total,'REPLACE')
        for poly in mesh.data.polygons:poly.use_smooth=True
    weighted,pose=inspect_deform_and_pose(body,rig)
    out.mkdir();shutil.copytree(source/'Textures',out/'Textures')
    for img in bpy.data.images:
        if img.source=='FILE':
            dest=out/'Textures'/Path(img.filepath).name
            if not dest.is_file():raise RuntimeError('SHIRE_VARIANT_TEXTURE_NOT_PORTABLE '+str(dest))
            img.filepath=str(dest);img.reload()
    bpy.ops.object.select_all(action='DESELECT')
    for o in [rig]+meshes:o.select_set(True)
    bpy.context.view_layer.objects.active=rig
    output=out/'PES002_Shira_WardrobeStudy.fbx'
    bpy.ops.export_scene.fbx(filepath=str(output),use_selection=True,add_leaf_bones=False,bake_anim=False,path_mode='RELATIVE')
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'Shira_WardrobeStudy.blend'))
    result={'status':'SOURCE_WARDROBE_STUDY_NOT_UE_IMPORTED','curly_hair_clumps':curls,'waistcoat_shell_thickness_m':.006,'license':'CC0','source_fbx_sha256':digest,'fbx_sha256':hashlib.file_digest(output.open('rb'),'sha256').hexdigest(),'source_spec_sha256':receipt['spec_sha256'],'source_gender':'female (upstream gender=0); original supporting resident, not named cast','weighted_body_vertices':weighted,'pose':pose,'max_deform_influences':4,'animation':'NOT_AUTHORED','visual':'PENDING','ue_import':'NOT_RUN','known_open_items':['Manual hair silhouette/face review','Waistcoat fit/closure/hem review','Full bilateral shoulder/knee visual stress','LODs and material section budget','Authored locomotion and UE4 deformation']}
    (out/'variant_receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print('SHIRE_WARDROBE_STUDY_EXPORTED '+json.dumps(result),flush=True)


if __name__=='__main__':main()
