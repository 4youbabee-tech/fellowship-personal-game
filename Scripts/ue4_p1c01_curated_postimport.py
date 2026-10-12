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
    report = {
        'schema_version': 1,
        'chapter': 'P1C01', 'mode': 'UE4_EDITOR_CURATED_POSTIMPORT_OBSERVATION',
        'target_sha': os.environ.get('SHIRE_TARGET_SHA', 'NOT_SUPPLIED'),
        'stage_receipt_sha256': plan['stage_receipt_sha256'],
        'source_manifest_sha256': plan['source_manifest_sha256'],
        'static_meshes_with_verified_lods': len(outcomes),
        'asset_registry_path_checks': len(outcomes) + len(texture_rows),
        'imported_authored_sidecar_lods': sum(x['lod_count'] - 1 for x in outcomes),
        'configured_packed_textures': len(texture_rows),
        'external_held_for_license': plan['counts']['license_held_external'],
        'mesh_observations': outcomes, 'texture_observations': texture_rows,
        'collision_review_pending': collision_review,
        'material_bindings_verified': False,
        'collision_nav_verified': False,
        'world_placement_verified': False,
        'character_final_verified': False,
        'pie_tested': False, 'device_tested': False, 'visual_accepted': False,
        'gate6_7_closed': False,
    }
    if (len(outcomes) != 34 or report['imported_authored_sidecar_lods'] != 46 or
        len(texture_rows) != 63):
        raise RuntimeError('P1C01_UNREAL_POSTIMPORT_COUNTS_UNEXPECTED')
    report_path.write_text(json.dumps(report, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    print('P1C01_CURATED_EDITOR_POSTIMPORT_PASS meshes=34 authoredLods=46 textures=63')
    print('P1C01_CURATED_EDITOR_POSTIMPORT_RECEIPT=' + str(report_path))
    print('BOUNDARY P1C01_LOD_TEXTURE_ONLY_NOT_COLLISION_WORLD_PIE_DEVICE_VISUAL_ACCEPTANCE')
    return report


if __name__ == '__main__':
    import unreal
    editor_apply(unreal)
