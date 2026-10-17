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
    # Keep the source trousers full length. The previous knee cut read as
    # modern shorts in the actual Blender render and broke the Shire silhouette.
    # The fitted source trousers remain skinned to the same rig and are recolored
    # as dark wool below; the body underneath stays intact.
    linen = material('Shire_Undyed_Linen', (.56,.45,.29))
    wool = material('Shire_Walnut_Wool', (.075,.043,.021))
    vestmat = material('Shire_Moss_Waistcoat', (.055,.095,.042))
    clothes.data.materials.clear(); clothes.data.materials.append(linen); clothes.data.materials.append(wool)
    for face in clothes.data.polygons:
        z=sum((clothes.matrix_world@clothes.data.vertices[i].co).z for i in face.vertices)/len(face.vertices)
        face.material_index=0 if z>.87 else 1
    # Duplicate fitted upper garment as a sleeveless, open-front waistcoat.
    vest=clothes.copy(); vest.data=clothes.data.copy(); bpy.context.collection.objects.link(vest);vest.name='Shire_Authored_Waistcoat'
    # Keep the fitted source garment closed across the front. The earlier
    # hand-cut opening sliced through irregular suit topology and exposed
    # triangular body patches in the Blender render. Retain only the four
    # torso bounds; never duplicate the full clothing object into the vest.
    bm=bmesh.new();bm.from_mesh(vest.data)
    for co,normal in [((0,0,.865),(0,0,1)),((0,0,1.285),(0,0,-1)),
                      ((-.177,0,0),(1,0,0)),((.177,0,0),(-1,0,0))]:
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
            plane_co=vest.matrix_world.inverted()@Vector(co),
            plane_no=vest.matrix_world.to_3x3().transposed()@Vector(normal),
            clear_inner=True,dist=1e-6)
    bm.normal_update()
    bm.to_mesh(vest.data);bm.free()
    vest.data.materials.clear();vest.data.materials.append(vestmat)
    for f in vest.data.polygons:f.material_index=0
    # The source suit has an open central placket. Fit a narrow wool panel to
    # the actual garment surface; a guessed fixed Y offset left skin visible.
    surface_samples=[]
    for vertex in vest.data.vertices:
        point=vest.matrix_world@vertex.co
        if abs(point.x-.010)<.085 and point.z>.87 and point.y<0:
            surface_samples.append((point.x,point.y,point.z))
    def placket_front_y(z):
        nearby=[y for x,y,height in surface_samples
                if abs(x-.010)<.085 and abs(height-z)<.045]
        if not nearby:raise RuntimeError('SHIRE_WAISTCOAT_PLACKET_SURFACE_MISSING')
        return min(nearby)-.003
    placket=bmesh.new();placket.from_mesh(vest.data)
    columns=[]
    for z in (.895,.965,1.035,1.105,1.175):
        y=placket_front_y(z)
        columns.append([placket.verts.new(vest.matrix_world.inverted()@Vector((x,y,z)))
                        for x in (-.010,.030)])
    for lower,upper in zip(columns,columns[1:]):
        placket.faces.new((lower[0],lower[1],upper[1],upper[0]))
    placket.normal_update();placket.to_mesh(vest.data);placket.free();vest.data.update()
    for f in vest.data.polygons:f.material_index=0
    for v in vest.data.vertices:
        v.co+=v.normal*.004
    # A thin applied shell gives the garment a readable hem and cloth thickness.
    bpy.context.view_layer.objects.active=vest
    vest.select_set(True)
    shell=vest.modifiers.new('Shire_Waistcoat_Cloth_Edge','SOLIDIFY')
    shell.thickness=.006;shell.offset=0.0;shell.use_rim=True
    bpy.ops.object.modifier_apply(modifier=shell.name)
    # Add a small, attached row of wooden/brass-toned buttons to make the vest
    # closure read as authored clothing instead of an unfastened proxy shell.
    # The detail stays inside the character texture/material budget: one
    # additional low-triangle material and five small smooth buttons.
    buttons = bmesh.new(); buttons.from_mesh(vest.data)
    for index in range(5):
        z = .925 + index * .046
        center = vest.matrix_world.inverted() @ Vector((.010, placket_front_y(z)-.010, z))
        # Blender versions do not consistently return a `faces` key from
        # create_uvsphere; snapshot the BMFace collection so operator result
        # schema cannot abort source export after building the sphere.
        old_faces = set(buttons.faces)
        bmesh.ops.create_uvsphere(
            buttons, u_segments=10, v_segments=8, radius=.008,
            matrix=Matrix.Translation(center))
        for face in set(buttons.faces) - old_faces:
            face.smooth = True
    buttons.to_mesh(vest.data); buttons.free(); vest.data.update()
    vest.data.materials.append(material('Shire_Aged_Brass_Fasteners', (.29, .19, .07)))
    for face in vest.data.polygons:
        # Button centers are close to the front seam and below the collar.
        c = sum((vest.matrix_world @ vest.data.vertices[i].co for i in face.vertices), Vector()) / len(face.vertices)
        if abs(c.x - .010) < .010 and .91 < c.z < 1.16 and c.y < placket_front_y(c.z)-.004:
            face.material_index = 1
    upper_torso = next((name for name in ('spine_03', 'spine_02', 'spine_01')
                        if vest.vertex_groups.get(name)), None)
    if upper_torso is None:
        raise RuntimeError('SHIRE_WAISTCOAT_UPPER_TORSO_WEIGHT_GROUP_MISSING')
    upper_group = vest.vertex_groups[upper_torso]
    for vertex in vest.data.vertices:
        if not any(binding.group < len(vest.vertex_groups) and
                   vest.vertex_groups[binding.group].name in ('spine_03', 'spine_02', 'spine_01')
                   and binding.weight > 0 for binding in vertex.groups):
            world = vest.matrix_world @ vertex.co
            if .89 < world.z < 1.18 and world.y < -.085 and abs(world.x - .010) < .025:
                upper_group.add([vertex.index], 1.0, 'REPLACE')
    meshes.append(vest)
    # Head-weighted cascading ringlets replace the flat short-hair crest. The
    # source preview rejected the old stack of tiny sphere clumps; tapered tube
    # locks form a softer silhouette around the temples and back of the head.
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
    # Form tapered, scalp-following tubes. 12 strands per side/back profile,
    # 10 centerline samples and six-sided rings keep the extra geometry modest.
    for i in range(24):
        angle = 2 * math.pi * i / 24 + .035 * math.sin(i * 1.7)
        # Forehead-facing strands stay close to the cap; the temples and nape
        # receive longer locks so the silhouette reads as naturally curly hair.
        side_weight = abs(math.sin(angle))
        length = .038 + .052 * side_weight
        radial = .82 + .06 * math.cos(i * 2.41)
        phase = i * 1.91
        centers=[]
        for step in range(11):
            t=step/10
            wave=math.sin(t * math.tau * 1.35 + phase) * (.003 + .004*t)
            x=hc.x+(rx*radial + wave)*math.cos(angle)
            y=hc.y+(ry*radial + wave)*math.sin(angle)
            z=hhi.z-.014-length*t
            centers.append(hair.matrix_world.inverted() @ Vector((x,y,z)))
        strand_vertices=[]
        for step,center in enumerate(centers):
            tangent=(centers[min(step+1,10)]-centers[max(step-1,0)]).normalized()
            radial_axis=Vector((math.cos(angle),math.sin(angle),0))
            side_axis=tangent.cross(radial_axis).normalized()
            radius=.0052*(1.0-.58*(step/10))
            ring=[]
            for side in range(6):
                phi=math.tau*side/6
                point=center + radius*(radial_axis*math.cos(phi)+side_axis*math.sin(phi))
                ring.append(curl_bm.verts.new(point))
            strand_vertices.append(ring)
        for step in range(10):
            a=strand_vertices[step];b=strand_vertices[step+1]
            for side in range(6):
                curl_bm.faces.new((a[side],a[(side+1)%6],b[(side+1)%6],b[side]))
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
    result={'status':'SOURCE_WARDROBE_STUDY_NOT_UE_IMPORTED','curly_hair_locks':curls,'curl_geometry':'24 tapered six-sided cascading ringlet tubes integrated into the head-weighted hair mesh','waistcoat_button_count':5,'waistcoat_front_placket':'surface-fitted spine-weighted wool panel','waistcoat_shell_thickness_m':.006,'license':'CC0','source_fbx_sha256':digest,'fbx_sha256':hashlib.file_digest(output.open('rb'),'sha256').hexdigest(),'source_spec_sha256':receipt['spec_sha256'],'source_gender':'female (upstream gender=0); original supporting resident, not named cast','weighted_body_vertices':weighted,'pose':pose,'max_deform_influences':4,'animation':'NOT_AUTHORED','visual':'PENDING','ue_import':'NOT_RUN','known_open_items':['Manual hair silhouette/face review','Waistcoat fit/closure/hem review','Full bilateral shoulder/knee visual stress','LODs and material section budget','Authored locomotion and UE4 deformation']}
    (out/'variant_receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print('SHIRE_WARDROBE_STUDY_EXPORTED '+json.dumps(result),flush=True)


if __name__=='__main__':main()
