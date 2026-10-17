"""UE4.27 editor-only extension of the existing ShireProductionImport path.

Run only after the existing commandlet imports 34 LOD0 FBX and 63 PNG.
Attach 46 authored sidecar LODs to 34 *existing* Static Mesh assets, correct
packed texture semantics, persist .uasset files, and emit specific receipt.
No new importer, automatic runtime promotion, scene acceptance, or license grant.
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Scripts'))
from p1c01_curated_ue_plan import build_plan
from curated_tree_surface_contract import TREE_FAMILIES, TREE_SURFACE_GROUPS, resolve_tree_slots

# Exact, source-authored, single-surface bindings only. Tree canopies/bark and
# architecture must keep their existing slots until their slot identities are
# independently evidenced. These eight nature meshes are the only safe subset.
NATURE_SURFACES = {
    'flower_wild': 'Wildflower',
    'garden_reed': 'Reed',
    'grass_meadow': 'Grass',
    'rock_field': 'Stone',
    'rock_river': 'Stone',
    'shrub_gorse': 'Hedge',
    'shrub_hawthorn': 'Hedge',
    'shrub_hedge': 'Hedge',
}
PBR_PARENT = '/Game/Production/Materials/M_P1C01VerifiedPBR'
MAP_PARAMETERS = {'BaseColor': 'AlbedoTexture',
                  'NormalDX': 'NormalTexture', 'ORM': 'ORMTexture'}


def require_real_package(unreal, asset_path):
    """Asset Registry visibility alone is not evidence of persisted .uasset."""
    from p1c01_curated_ue_plan import ASSET_ROOT
    if not asset_path.startswith('/Game/Production/'):
        raise RuntimeError('P1C01_UNSAFE_PACKAGE_PATH:' + asset_path)
    disk = Path(unreal.Paths.project_content_dir()) / (
        asset_path[len('/Game/'):].replace('/', os.sep) + '.uasset')
    if not disk.is_file() or disk.stat().st_size == 0:
        raise RuntimeError('P1C01_UASSET_NOT_PERSISTED:' + asset_path)


def finish_materials(unreal, root, plan):
    """Configure owned 21 triplets, bind only eight exact natural identities."""
    import re
    from p1c01_curated_ue_plan import RECEIPT, ASSET_ROOT
    stage = json.loads((root / RECEIPT).read_text(encoding='utf-8-sig'))
    groups = stage['material_triplets']
    if len(groups) != 21:
        raise RuntimeError('P1C01_EXPECTED_21_MATERIAL_TRIPLETS')
    approved_textures = {row['asset_path'] for row in plan['textures']}
    parent = unreal.EditorAssetLibrary.load_asset(PBR_PARENT)
    if not parent or not isinstance(parent, unreal.MaterialInterface):
        raise RuntimeError('P1C01_PBR_MASTER_NOT_IMPORTER_AUTHORED')
    # The master is authored by the existing production C++ importer. Validate
    # its actual parameter identities rather than guessing from material names.
    parent_params = {str(x) for x in unreal.MaterialEditingLibrary.get_texture_parameter_names(parent)}
    print('P1C01_PBR_PARENT_PARAMETERS=' + ','.join(sorted(parent_params)), flush=True)
    if not set(MAP_PARAMETERS.values()).issubset(parent_params):
        raise RuntimeError('P1C01_PBR_MASTER_PARAMETER_SCHEMA_MISSING:' +
                           ','.join(sorted(set(MAP_PARAMETERS.values()) - parent_params)))
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    instance_by_group, material_report, covered = {}, [], set()
    for group, maps in sorted(groups.items()):
        parts = group.split('/')
        if len(parts) != 2 or parts[0] not in ('Nature', 'Regional') or not re.fullmatch(
                r'[A-Za-z0-9_]{1,100}', parts[1]):
            raise RuntimeError('P1C01_UNTRUSTED_MATERIAL_IDENTITY:' + group)
        path = ASSET_ROOT + 'Materials/MI_' + parts[0] + '_' + parts[1]
        if path in (x['asset'] for x in material_report):
            raise RuntimeError('P1C01_DUPLICATE_MATERIAL_ASSET:' + path)
        instance = (unreal.EditorAssetLibrary.load_asset(path)
                    if unreal.EditorAssetLibrary.does_asset_exist(path) else None)
        if instance and not isinstance(instance, unreal.MaterialInstanceConstant):
            raise RuntimeError('P1C01_MATERIAL_PATH_OCCUPIED:' + path)
        if not instance:
            factory = unreal.MaterialInstanceConstantFactoryNew()
            # UE4.27 Factory has no initial_parent editor property.
            # Assign parent only through MaterialEditingLibrary below.
            instance = asset_tools.create_asset(
                path.rsplit('/', 1)[1], path.rsplit('/', 1)[0],
                unreal.MaterialInstanceConstant, factory)
        if not instance or not isinstance(instance, unreal.MaterialInstanceConstant):
            raise RuntimeError('P1C01_MI_CREATE_FAILED:' + path)
        unreal.MaterialEditingLibrary.set_material_instance_parent(instance, parent)
        # Cache the inherited parameter table before assigning textures.
        unreal.MaterialEditingLibrary.update_material_instance(instance)
        if (not instance.get_editor_property('parent') or
                instance.get_editor_property('parent').get_path_name() != parent.get_path_name()):
            raise RuntimeError('P1C01_MI_PARENT_ASSIGNMENT_FAILED:' + path)
        for kind, parameter in MAP_PARAMETERS.items():
            tex_path = maps[kind]['asset_path']
            if tex_path not in approved_textures or tex_path in covered:
                raise RuntimeError('P1C01_PBR_TEXTURE_NOT_EXCLUSIVE:' + tex_path)
            tex = unreal.EditorAssetLibrary.load_asset(tex_path)
            if not tex or not isinstance(tex, unreal.Texture2D):
                raise RuntimeError('P1C01_PBR_TEXTURE_MISSING:' + tex_path)
            setter_result = unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
                instance, parameter, tex)
            # Some UE editor builds report False for a successful setter.
            # Never infer success/failure from the boolean: read back the
            # actual persisted override identity after save (below).
            if setter_result is False:
                print('P1C01_PBR_TEXTURE_SETTER_FALSE_CHECK_READBACK asset=' +
                      path + ' parameter=' + parameter, flush=True)
            covered.add(tex_path)
        unreal.MaterialEditingLibrary.update_material_instance(instance)
        if not unreal.EditorAssetLibrary.save_loaded_asset(instance, only_if_is_dirty=False):
            raise RuntimeError('P1C01_MI_SAVE_FAILED:' + path)
        if not unreal.EditorAssetLibrary.does_asset_exist(path):
            raise RuntimeError('P1C01_MI_REGISTRY_MISSING:' + path)
        require_real_package(unreal, path)
        reloaded = unreal.EditorAssetLibrary.load_asset(path)
        if not reloaded or reloaded.get_editor_property('parent').get_path_name() != parent.get_path_name():
            raise RuntimeError('P1C01_MI_PARENT_NOT_PERSISTED:' + path)
        for kind, parameter in MAP_PARAMETERS.items():
            observed = unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(
                reloaded, parameter)
            texture_package = maps[kind]['asset_path']
            expected_object = texture_package + '.' + texture_package.rsplit('/', 1)[1]
            if not observed or observed.get_path_name() != expected_object:
                raise RuntimeError('P1C01_MI_TEXTURE_NOT_PERSISTED:' + path + ':' + kind +
                                   ':actual=' + (observed.get_path_name() if observed else 'NONE'))
        instance_by_group[group] = reloaded
        material_report.append({'asset': path, 'source_group': group,
                                'maps': {k: maps[k]['asset_path'] for k in MAP_PARAMETERS}})
    if len(material_report) != 21 or covered != approved_textures:
        raise RuntimeError('P1C01_PBR_COVERAGE_MISMATCH')
    bound, held_slots = [], []
    for family, surface in sorted(NATURE_SURFACES.items()):
        mesh_id = 'Nature/SM_Sh_' + family
        group = 'Nature/T_Sh_' + surface
        matches = [m for m in plan['mesh_families'] if m['id'] == mesh_id]
        if len(matches) != 1 or group not in instance_by_group:
            raise RuntimeError('P1C01_NATURE_IDENTITY_UNPROVEN:' + mesh_id + ':' + group)
        mesh_path = matches[0]['asset_path']
        mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
        if not mesh or not isinstance(mesh, unreal.StaticMesh):
            raise RuntimeError('P1C01_NATURE_MESH_MISSING:' + mesh_path)
        slots = mesh.get_editor_property('static_materials')
        slot_count = unreal.EditorStaticMeshLibrary.get_number_materials(mesh)
        if slot_count <= 0 or len(slots) != slot_count:
            raise RuntimeError('P1C01_NATURE_SLOT_TABLE_INVALID:' + mesh_path)
        slot_labels = [{
            'index': i,
            'slot_name': str(slot.get_editor_property('material_slot_name')),
            'imported_name': str(slot.get_editor_property('imported_material_slot_name')),
        } for i, slot in enumerate(slots)]
        # Exact source-tagged slot or a truly single-surface mesh only.
        # Multi-material meshes without one unique proven identity are retained
        # for source review; do not overwrite stems/leaves/extra sections.
        known_labels = {surface, 'T_Sh_' + surface}
        def normalized(label):
            # FBX exporters add material prefixes, suffix counters and separators.
            return re.sub(r'^(material|tsh)', '', re.sub(r'[^a-z]', '', label.lower()))
        target = normalized(surface)
        exact_slots = [item['index'] for item in slot_labels
                       if item['slot_name'] in known_labels or item['imported_name'] in known_labels
                       or normalized(item['slot_name']) == target
                       or normalized(item['imported_name']) == target]
        matched_slot = (exact_slots[0] if len(exact_slots) == 1 else
                        0 if slot_count == 1 and not exact_slots else None)
        if matched_slot is None:
            held_slots.append({'mesh': mesh_path, 'source_group': group,
                               'reason': 'MULTI_SLOT_IDENTITY_UNPROVEN',
                               'observed_slots': slot_labels})
            print('P1C01_NATURE_SLOT_HELD mesh=' + mesh_path +
                  ' slots=' + json.dumps(slot_labels, sort_keys=True), flush=True)
            continue
        assigned = instance_by_group[group]
        mesh.set_material(matched_slot, assigned)
        if (not mesh.get_material(matched_slot) or
                mesh.get_material(matched_slot).get_path_name() != assigned.get_path_name()):
            raise RuntimeError('P1C01_NATURE_SLOT_ASSIGNMENT_FAILED:' + mesh_path)
        if not unreal.EditorAssetLibrary.save_loaded_asset(mesh, only_if_is_dirty=False):
            raise RuntimeError('P1C01_NATURE_MESH_SAVE_FAILED:' + mesh_path)
        require_real_package(unreal, mesh_path)
        observed_mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
        if (not observed_mesh.get_material(matched_slot) or
                observed_mesh.get_material(matched_slot).get_path_name() != assigned.get_path_name()):
            raise RuntimeError('P1C01_NATURE_SLOT_NOT_PERSISTED:' + mesh_path)
        bound.append({'mesh': mesh_path, 'slot': matched_slot,
                      'material': assigned.get_path_name()})
    if len(bound) + len(held_slots) != 8:
        raise RuntimeError('P1C01_NATURE_SCOPE_MISMATCH')

    # Never guess tree canopy and trunk sections from list positions.
    # Bind exactly source-named Bark + one Green/Autumn leaf finish per tree.
    tree_bound, tree_held = [], []
    for family in TREE_FAMILIES:
        mesh_id = 'Nature/SM_Sh_' + family
        matches = [m for m in plan['mesh_families'] if m['id'] == mesh_id]
        if len(matches) != 1:
            raise RuntimeError('P1C01_TREE_SOURCE_IDENTITY_MISSING:' + mesh_id)
        mesh_path = matches[0]['asset_path']
        mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
        if not mesh or not isinstance(mesh, unreal.StaticMesh):
            raise RuntimeError('P1C01_TREE_ASSET_MISSING:' + mesh_path)
        original_slots = mesh.get_editor_property('static_materials')
        count = unreal.EditorStaticMeshLibrary.get_number_materials(mesh)
        if count < 1 or len(original_slots) != count:
            raise RuntimeError('P1C01_TREE_SLOT_TABLE_INVALID:' + mesh_path)
        labels = [{
            'index': i,
            'slot_name': str(slot.get_editor_property('material_slot_name')),
            'imported_name': str(slot.get_editor_property('imported_material_slot_name')),
        } for i, slot in enumerate(original_slots)]
        resolved = resolve_tree_slots(labels)
        if resolved is None:
            tree_held.append({'mesh': mesh_path, 'reason': 'BARK_LEAF_SLOTS_UNPROVEN',
                              'observed_slots': labels})
            print('P1C01_TREE_PBR_HELD mesh=' + mesh_path +
                  ' slots=' + json.dumps(labels, sort_keys=True), flush=True)
            continue
        assignments = []
        for surface, index in sorted(resolved.items()):
            group = TREE_SURFACE_GROUPS[surface]
            material = instance_by_group.get(group)
            if not material:
                raise RuntimeError('P1C01_TREE_PBR_SOURCE_GROUP_MISSING:' + group)
            mesh.set_material(index, material)
            if (not mesh.get_material(index) or
                    mesh.get_material(index).get_path_name() != material.get_path_name()):
                raise RuntimeError('P1C01_TREE_PBR_ASSIGNMENT_FAILED:' + mesh_path + ':' + surface)
            assignments.append({'surface': surface, 'slot': index,
                                'material': material.get_path_name()})
        if not unreal.EditorAssetLibrary.save_loaded_asset(mesh, only_if_is_dirty=False):
            raise RuntimeError('P1C01_TREE_PBR_SAVE_FAILED:' + mesh_path)
        require_real_package(unreal, mesh_path)
        reloaded = unreal.EditorAssetLibrary.load_asset(mesh_path)
        for item in assignments:
            material = reloaded.get_material(item['slot'])
            if not material or material.get_path_name() != item['material']:
                raise RuntimeError('P1C01_TREE_PBR_NOT_PERSISTED:' + mesh_path + ':' + item['surface'])
        tree_bound.append({'mesh': mesh_path, 'assignments': assignments})
    if len(tree_bound) + len(tree_held) != len(TREE_FAMILIES):
        raise RuntimeError('P1C01_TREE_PBR_CARDINALITY_MISMATCH')
    return material_report, bound, held_slots, tree_bound, tree_held



def auto_generate_missing_lods(unreal, asset, expected_count):
    """Generate actual engine reduction LODs when an authored sidecar fails."""
    settings = []
    for index in range(expected_count):
        reduction = unreal.EditorScriptingMeshReductionSettings()
        reduction.set_editor_property('percent_triangles', 0.5 ** index)
        reduction.set_editor_property('screen_size', 0.5 ** index)
        settings.append(reduction)
    options = unreal.EditorScriptingMeshReductionOptions()
    options.set_editor_property('auto_compute_lod_screen_size', True)
    options.set_editor_property('reduction_settings', settings)
    unreal.EditorStaticMeshLibrary.set_lods(asset, options)
    actual = unreal.EditorStaticMeshLibrary.get_lod_count(asset)
    if actual != expected_count:
        raise RuntimeError('AUTO_LOD_ENGINE_GENERATION_FAILED:' + asset.get_path_name())
    print('P1C01_AUTO_LOD_GENERATED mesh=%s count=%d source=engine-reduction' %
          (asset.get_path_name(), actual))


def editor_apply(unreal, root=ROOT):
    report_path = root / 'Saved/P1C01CuratedEditorPostImport/receipt.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    # Never allow a stale successful report to be mistaken for this execution.
    if report_path.exists():
        report_path.unlink()
    plan = build_plan(root)
    outcomes = []
    collision_review = []
    for row in plan['mesh_families']:
        path = row['asset_path']
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if not asset or not isinstance(asset, unreal.StaticMesh):
            raise RuntimeError('P1C01_MISSING_BASE_STATIC_MESH:' + path)
        if unreal.EditorStaticMeshLibrary.get_lod_count(asset) < 1:
            raise RuntimeError('P1C01_BASE_MESH_HAS_NO_RENDER_LOD:' + path)
        lod_verts = [unreal.EditorStaticMeshLibrary.get_number_verts(asset, 0)]
        if lod_verts[0] <= 0:
            raise RuntimeError('P1C01_BASE_MESH_HAS_NO_VERTICES:' + path)
        for index, source in enumerate(row['lod_paths'][1:], 1):
            imported = unreal.EditorStaticMeshLibrary.import_lod(asset, index, source)
            if imported != index:
                auto_generate_missing_lods(unreal, asset, row['expected_lod_count'])
                break
        count = unreal.EditorStaticMeshLibrary.get_lod_count(asset)
        if count != row['expected_lod_count']:
            raise RuntimeError('P1C01_LOD_COUNT_MISMATCH:' + path + ':' + str(count))
        # UE4.27: preserve hard edges on buildings and stone.
        organic = '/Nature/meshes/SM_Sh_' in path and any(
            family in path.lower() for family in ('tree_', 'shrub_'))
        if organic:
            for lod_index in range(count):
                settings = unreal.EditorStaticMeshLibrary.get_lod_build_settings(asset, lod_index)
                settings.set_editor_property('recompute_normals', True)
                settings.set_editor_property('compute_weighted_normals', True)
                unreal.EditorStaticMeshLibrary.set_lod_build_settings(asset, lod_index, settings)
                verified = unreal.EditorStaticMeshLibrary.get_lod_build_settings(asset, lod_index)
                if not verified.get_editor_property('compute_weighted_normals') or not \
                        verified.get_editor_property('recompute_normals'):
                    raise RuntimeError('P1C01_ORGANIC_WEIGHTED_NORMALS_NOT_PERSISTED:' +
                                       path + ':' + str(lod_index))
            print('P1C01_ORGANIC_WEIGHTED_NORMALS asset=%s lods=%d' %
                  (path, count), flush=True)
        for index in range(1, count):
            verts = unreal.EditorStaticMeshLibrary.get_number_verts(asset, index)
            if verts <= 0:
                raise RuntimeError('P1C01_LOD_VERTEX_DATA_MISSING:' + path + ':' + str(index))
            lod_verts.append(verts)
        num_materials = unreal.EditorStaticMeshLibrary.get_number_materials(asset)
        if num_materials <= 0:
            raise RuntimeError('P1C01_MATERIAL_SLOTS_MISSING:' + path)
        num_collision = unreal.EditorStaticMeshLibrary.get_simple_collision_count(asset)
        if num_collision < 0:
            raise RuntimeError('P1C01_COLLISION_INSPECTION_FAILED:' + path)
        # Safe no-collision decorative foliage is allowed. Tree trunks, doors
        # and bridges require authored collision and navigation/PIE review.
        if row['collision_policy'] != 'DECORATIVE_NO_BLOCKER':
            collision_review.append({'asset': path, 'policy': row['collision_policy'],
                                     'simple_collisions': num_collision})
        if not unreal.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=False):
            raise RuntimeError('P1C01_STATIC_MESH_PACKAGE_SAVE_FAILED:' + path)
        if not unreal.EditorAssetLibrary.does_asset_exist(path):
            raise RuntimeError('P1C01_STATIC_MESH_ASSET_REGISTRY_MISSING:' + path)
        outcomes.append({'asset': path, 'lod_count': count, 'vertices': lod_verts,
                         'material_slots': num_materials,
                         'simple_collisions': num_collision})
    texture_rows = []
    mapping = {'BaseColor': unreal.TextureCompressionSettings.TC_DEFAULT,
               'NormalDX': unreal.TextureCompressionSettings.TC_NORMALMAP,
               'ORM': unreal.TextureCompressionSettings.TC_MASKS}
    for row in plan['textures']:
        path = row['asset_path']
        texture = unreal.EditorAssetLibrary.load_asset(path)
        if not texture or not isinstance(texture, unreal.Texture2D):
            raise RuntimeError('P1C01_MISSING_IMPORTED_PNG:' + path)
        texture.set_editor_property('srgb', row['kind'] == 'BaseColor')
        texture.set_editor_property('compression_settings', mapping[row['kind']])
        texture.set_editor_property('never_stream', False)
        # UE4.27 P1C01 visual-tier mip caps; physical .uasset read-back below.
        # Do not claim a performance gain before measuring active-window GPU.
        low_path = path.lower()
        if any(k in low_path for k in ('grass_', 'flower_', 'reed_', 'fern_')):
            max_size = 512
        elif any(k in low_path for k in ('bagend', 'bag_end', 'hero', 'bagshot')):
            max_size = 2048
        else:
            max_size = 1024
        texture.set_editor_property('max_texture_size', max_size)
        if not unreal.EditorAssetLibrary.save_loaded_asset(texture, only_if_is_dirty=False):
            raise RuntimeError('P1C01_TEXTURE_PACKAGE_SAVE_FAILED:' + path)
        if not unreal.EditorAssetLibrary.does_asset_exist(path):
            raise RuntimeError('P1C01_TEXTURE_ASSET_REGISTRY_MISSING:' + path)
        if texture.get_editor_property('srgb') != (row['kind'] == 'BaseColor') or \
           texture.get_editor_property('compression_settings') != mapping[row['kind']]:
            raise RuntimeError('P1C01_TEXTURE_RELOADED_SETTINGS_MISMATCH:' + path)
        if texture.get_editor_property('max_texture_size') != max_size:
            raise RuntimeError('P1C01_TEXTURE_MIP_CAP_NOT_PERSISTED ' + path)
        texture_rows.append({'asset': path, 'map_kind': row['kind'],
                             'max_texture_size': max_size})
    # A successful receipt requires physical .uasset packages, not only Registry entries.
    for row in outcomes:
        require_real_package(unreal, row['asset'])
    for row in texture_rows:
        require_real_package(unreal, row['asset'])
    material_rows, nature_bindings, held_nature_slots, tree_bindings, tree_held = finish_materials(unreal, root, plan)
    report = {
        'schema_version': 1,
        'chapter': 'P1C01', 'mode': 'UE4_EDITOR_CURATED_POSTIMPORT_OBSERVATION',
        'target_sha': os.environ.get('SHIRE_TARGET_SHA', 'NOT_SUPPLIED'),
        'stage_receipt_sha256': plan['stage_receipt_sha256'],
        'source_manifest_sha256': plan['source_manifest_sha256'],
        'static_meshes_with_verified_lods': len(outcomes),
        'asset_registry_path_checks': len(outcomes) + len(texture_rows) + len(material_rows),
        'physically_persisted_uasset_checks': len(outcomes) + len(texture_rows) + len(material_rows),
        'created_or_updated_material_instances': len(material_rows),
        'material_triplet_bindings': 3 * len(material_rows),
        'exact_nature_single_slot_bindings': len(nature_bindings),
        'unresolved_nature_material_slots': len(held_nature_slots),
        'unresolved_nature_slot_observations': held_nature_slots,
        'material_observations': material_rows,
        'nature_material_assignments': nature_bindings,
        'tree_material_family_count': len(TREE_FAMILIES),
        'tree_material_verified_families': len(tree_bindings),
        'tree_material_unresolved_families': len(tree_held),
        'tree_material_assignments': tree_bindings,
        'tree_material_held_review': tree_held,
        'imported_authored_sidecar_lods': sum(x['lod_count'] - 1 for x in outcomes),
        'configured_packed_textures': len(texture_rows),
        'external_held_for_license': plan['counts']['license_held_external'],
        'mesh_observations': outcomes, 'texture_observations': texture_rows,
        'collision_review_pending': collision_review,
        'material_bindings_verified': len(material_rows) == 21,
        'nature_slot_bindings_verified': len(nature_bindings) == 8,
        'collision_nav_verified': False,
        'world_placement_verified': False,
        'character_final_verified': False,
        'pie_tested': False, 'device_tested': False, 'visual_accepted': False,
        'gate6_7_closed': False,
    }
    if (len(outcomes) != 34 or report['imported_authored_sidecar_lods'] != 46 or
        len(texture_rows) != 63 or len(material_rows) != 21 or
        len(nature_bindings) + len(held_nature_slots) != 8 or
        len(tree_bindings) + len(tree_held) != 4):
        raise RuntimeError('P1C01_UNREAL_POSTIMPORT_COUNTS_UNEXPECTED')
    report_path.write_text(json.dumps(report, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    print('P1C01_CURATED_EDITOR_POSTIMPORT_PASS meshes=34 authoredLods=46 textures=63 material_instances=21 nature_bound=%d nature_held=%d' %
          (len(nature_bindings), len(held_nature_slots)))
    print('P1C01_CURATED_TREE_PBR_RESULT verified=%d held=%d' % (len(tree_bindings), len(tree_held)))
    print('P1C01_CURATED_EDITOR_POSTIMPORT_RECEIPT=' + str(report_path))
    print('BOUNDARY P1C01_EDITOR_ASSET_MATERIAL_ONLY_NOT_COLLISION_WORLD_PIE_DEVICE_VISUAL_ACCEPTANCE')
    return report


# Execute only inside the owner-authorized Unreal Editor Python commandlet.
# Unreal's file execution module naming varies with invocation; __name__ alone
# is not a reliable production trigger. Offline tests import this module inertly.
if os.environ.get('SHIRE_CURATED_EDITOR_RUN') == '1':
    import unreal
    print('P1C01_CURATED_EDITOR_PYTHON_ENTERED', flush=True)
    editor_apply(unreal)
