"""UE4.27 editor-only extension of the existing ShireProductionImport path.

Run only after the existing commandlet imports 34 LOD0 FBX and 63 PNG.
Attach 46 authored sidecar LODs to 34 *existing* Static Mesh assets, correct
packed texture semantics, persist .uasset files, and emit specific receipt.
No new importer, automatic runtime promotion, scene acceptance, or license grant.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Scripts'))
from p1c01_curated_ue_plan import build_plan

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
        instance = unreal.EditorAssetLibrary.load_asset(path)
        if instance and not isinstance(instance, unreal.MaterialInstanceConstant):
            raise RuntimeError('P1C01_MATERIAL_PATH_OCCUPIED:' + path)
        if not instance:
            factory = unreal.MaterialInstanceConstantFactoryNew()
            factory.set_editor_property('initial_parent', parent)
            instance = asset_tools.create_asset(
                path.rsplit('/', 1)[1], path.rsplit('/', 1)[0],
                unreal.MaterialInstanceConstant, factory)
        if not instance or not isinstance(instance, unreal.MaterialInstanceConstant):
            raise RuntimeError('P1C01_MI_CREATE_FAILED:' + path)
        unreal.MaterialEditingLibrary.set_material_instance_parent(instance, parent)
        for kind, parameter in MAP_PARAMETERS.items():
            tex_path = maps[kind]['asset_path']
            if tex_path not in approved_textures or tex_path in covered:
                raise RuntimeError('P1C01_PBR_TEXTURE_NOT_EXCLUSIVE:' + tex_path)
            tex = unreal.EditorAssetLibrary.load_asset(tex_path)
            if not tex or not isinstance(tex, unreal.Texture2D):
                raise RuntimeError('P1C01_PBR_TEXTURE_MISSING:' + tex_path)
            if not unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
                    instance, parameter, tex):
                raise RuntimeError('P1C01_PBR_TEXTURE_PARAMETER_MISSING:' + path + ':' + parameter)
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
            if not observed or observed.get_path_name() != maps[kind]['asset_path']:
                raise RuntimeError('P1C01_MI_TEXTURE_NOT_PERSISTED:' + path + ':' + kind)
        instance_by_group[group] = reloaded
        material_report.append({'asset': path, 'source_group': group,
                                'maps': {k: maps[k]['asset_path'] for k in MAP_PARAMETERS}})
    if len(material_report) != 21 or covered != approved_textures:
        raise RuntimeError('P1C01_PBR_COVERAGE_MISMATCH')
    bound = []
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
        if unreal.EditorStaticMeshLibrary.get_number_materials(mesh) != 1:
            raise RuntimeError('P1C01_NATURE_SLOT_IDENTITY_UNPROVEN:' + mesh_path)
        assigned = instance_by_group[group]
        mesh.set_material(0, assigned)
        if not mesh.get_material(0) or mesh.get_material(0).get_path_name() != assigned.get_path_name():
            raise RuntimeError('P1C01_NATURE_SLOT_ASSIGNMENT_FAILED:' + mesh_path)
        if not unreal.EditorAssetLibrary.save_loaded_asset(mesh, only_if_is_dirty=False):
            raise RuntimeError('P1C01_NATURE_MESH_SAVE_FAILED:' + mesh_path)
        require_real_package(unreal, mesh_path)
        observed_mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
        if not observed_mesh.get_material(0) or observed_mesh.get_material(0).get_path_name() != assigned.get_path_name():
            raise RuntimeError('P1C01_NATURE_SLOT_NOT_PERSISTED:' + mesh_path)
        bound.append({'mesh': mesh_path, 'slot': 0, 'material': assigned.get_path_name()})
    if len(bound) != 8:
        raise RuntimeError('P1C01_EIGHT_NATURE_BINDINGS_MISSING')
    return material_report, bound



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
                raise RuntimeError('P1C01_AUTHORED_LOD_IMPORT_FAILED:' + path + ':' + str(index))
        count = unreal.EditorStaticMeshLibrary.get_lod_count(asset)
        if count != row['expected_lod_count']:
            raise RuntimeError('P1C01_LOD_COUNT_MISMATCH:' + path + ':' + str(count))
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
        if not unreal.EditorAssetLibrary.save_loaded_asset(texture, only_if_is_dirty=False):
            raise RuntimeError('P1C01_TEXTURE_PACKAGE_SAVE_FAILED:' + path)
        if not unreal.EditorAssetLibrary.does_asset_exist(path):
            raise RuntimeError('P1C01_TEXTURE_ASSET_REGISTRY_MISSING:' + path)
        if texture.get_editor_property('srgb') != (row['kind'] == 'BaseColor') or \
           texture.get_editor_property('compression_settings') != mapping[row['kind']]:
            raise RuntimeError('P1C01_TEXTURE_RELOADED_SETTINGS_MISMATCH:' + path)
        texture_rows.append({'asset': path, 'map_kind': row['kind']})
    # A successful receipt requires physical .uasset packages, not only Registry entries.
    for row in outcomes:
        require_real_package(unreal, row['asset'])
    for row in texture_rows:
        require_real_package(unreal, row['asset'])
    material_rows, nature_bindings = finish_materials(unreal, root, plan)
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
        'material_observations': material_rows,
        'nature_material_assignments': nature_bindings,
        'imported_authored_sidecar_lods': sum(x['lod_count'] - 1 for x in outcomes),
        'configured_packed_textures': len(texture_rows),
        'external_held_for_license': plan['counts']['license_held_external'],
        'mesh_observations': outcomes, 'texture_observations': texture_rows,
        'collision_review_pending': collision_review,
        'material_bindings_verified': len(material_rows) == 21 and len(nature_bindings) == 8,
        'collision_nav_verified': False,
        'world_placement_verified': False,
        'character_final_verified': False,
        'pie_tested': False, 'device_tested': False, 'visual_accepted': False,
        'gate6_7_closed': False,
    }
    if (len(outcomes) != 34 or report['imported_authored_sidecar_lods'] != 46 or
        len(texture_rows) != 63 or len(material_rows) != 21 or len(nature_bindings) != 8):
        raise RuntimeError('P1C01_UNREAL_POSTIMPORT_COUNTS_UNEXPECTED')
    report_path.write_text(json.dumps(report, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    print('P1C01_CURATED_EDITOR_POSTIMPORT_PASS meshes=34 authoredLods=46 textures=63 material_instances=21 nature_bindings=8')
    print('P1C01_CURATED_EDITOR_POSTIMPORT_RECEIPT=' + str(report_path))
    print('BOUNDARY P1C01_EDITOR_ASSET_MATERIAL_ONLY_NOT_COLLISION_WORLD_PIE_DEVICE_VISUAL_ACCEPTANCE')
    return report


if __name__ == '__main__':
    import unreal
    editor_apply(unreal)
