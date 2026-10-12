#!/usr/bin/env python3
"""Offline fake-source/editor tests: no actual UE4 compilation or PIE is claimed."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import p1c01_curated_ue_plan as bridge
import ue4_p1c01_curated_postimport as editor


def create_fixture(root):
    root = Path(root)
    inventory, families, materials = [], [], {}

    def add(name, folder, blob, track, kind):
        target = root / folder / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)
        inventory.append({'source':name, 'track':track, 'kind':kind})
        return {'source_file':name,'sha256':hashlib.sha256(blob).hexdigest()}

    for i in range(34):
        nature = i < 12
        scope = 'Nature' if nature else 'Architecture'
        name = ('tree' if nature else 'hobbit') + ('_%02d' % i)
        levels = {}
        for lod in range(3 if nature else 2):
            rel = '%s/Meshes/SM_Sh_%s_LOD%d.fbx' % (scope, name, lod)
            data = ('Kaydara FBX Binary  \x00\x1a\x00' + 'dummy:%02d-%d' % (i,lod)).encode()
            entry = add(rel, bridge.CONTENT_ROOT if lod==0 else bridge.LOD_ROOT,
                        data, 'L01_TREES' if nature else 'L03_BAG_END_HERO_ARCH',
                        'UE4_COMMANDLET_BASE_STATIC_MESH' if lod==0 else 'UE4_EDITOR_LOD_ONLY_NOT_SEPARATE_MESH')
            levels[str(lod)] = entry
        families.append({'id':scope+'/'+name,'expected_lod_count':len(levels),
                         'base_asset_path':bridge.ASSET_ROOT +
                             Path(levels['0']['source_file']).with_suffix('').as_posix(),
                         'lods':levels,
                         'collision_policy':'SIMPLE_REVIEW_TREE_TRUNK' if nature else 'SIMPLIFIED_AUTHOR_COLLIDER_REVIEW',
                         'hism_candidate':nature})
    for i in range(21):
        group = ('Nature' if i<9 else 'Regional')+'/surface_%02d'%i
        triplet = {}
        for kind in ['BaseColor','NormalDX','ORM']:
            rel = '%s/Textures/T_Surface%02d_%s.png' % ('Nature' if i<9 else 'Regional',i,kind)
            entry = add(rel,bridge.CONTENT_ROOT,b'PNG fixture:'+rel.encode(),
                        'L05_ORIGINAL_SURFACES','UE4_COMMANDLET_TEXTURE')
            entry.update({'asset_path':bridge.ASSET_ROOT+Path(rel).with_suffix('').as_posix(),
                          'srgb':kind=='BaseColor',
                          'compression':{'BaseColor':'TC_DEFAULT','NormalDX':'TC_NORMALMAP','ORM':'TC_MASKS'}[kind]})
            triplet[kind] = entry
        materials[group] = triplet
    held = [{'source':'External/held_%03d.png' % i} for i in range(120)]
    receipt = {'schema_version':1,'chapter':'P1C01',
               'mode':'ORIGINAL_SOURCE_STAGED_NOT_UE4_IMPORTED',
               'source_manifest_sha256':bridge.MANIFEST_SHA,
               'workspace':str(root.resolve()),'engine_import_allowed_now':False,
               'mesh_families':families,'material_triplets':materials,
               'source_stage_files':inventory,'source_stage_count':143,
               'source_png':63,'lod_sidecars':46,'importable_ue_base_meshed_families':34,
               'external_license_held_count':120,'external_license_held':held}
    receipt.update({k:False for k in bridge.FALSE_GATES})
    path = root/bridge.RECEIPT
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(receipt),encoding='utf-8')
    return receipt, path


class MockMesh:
    def __init__(self): self.verts=[120]


class MockTexture:
    def __init__(self): self.props={}
    def set_editor_property(self,k,v): self.props[k]=v
    def get_editor_property(self,k): return self.props[k]


class MockEngine:
    StaticMesh = MockMesh
    Texture2D = MockTexture

    class TextureCompressionSettings:
        TC_DEFAULT = 'TC_DEFAULT'
        TC_NORMALMAP = 'TC_NORMALMAP'
        TC_MASKS = 'TC_MASKS'

    def __init__(self):
        self.objects={}
        engine=self
        class AssetLibrary:
            @staticmethod
            def load_asset(path):
                if path not in engine.objects:
                    engine.objects[path] = MockTexture() if '/Textures/' in path else MockMesh()
                return engine.objects[path]
            @staticmethod
            def save_loaded_asset(asset,only_if_is_dirty=False): return True
            @staticmethod
            def does_asset_exist(path): return path in engine.objects
        class MeshLibrary:
            @staticmethod
            def get_lod_count(mesh): return len(mesh.verts)
            @staticmethod
            def get_number_verts(mesh,index): return mesh.verts[index]
            @staticmethod
            def import_lod(mesh,index,source):
                if 'LOD%d.fbx'%index not in source: return -1
                if index==len(mesh.verts): mesh.verts.append(50-index)
                elif index < len(mesh.verts): mesh.verts[index]=50-index
                return index
            @staticmethod
            def get_number_materials(mesh): return 1
            @staticmethod
            def get_simple_collision_count(mesh): return 0
        self.EditorAssetLibrary = AssetLibrary
        self.EditorStaticMeshLibrary = MeshLibrary


class CuratedPlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.receipt, self.receipt_path = create_fixture(self.root)

    def tearDown(self): self.temp.cleanup()

    def test_physical_34_meshes_46_lods_and_63_packed_textures(self):
        plan=bridge.build_plan(self.root)
        self.assertEqual(34,len(plan['mesh_families']))
        self.assertEqual(46,sum(len(m['lod_paths'])-1 for m in plan['mesh_families']))
        self.assertEqual(63,len(plan['textures']))
        self.assertEqual(120,plan['counts']['license_held_external'])

    def test_lod_hash_tamper_fails_before_unreal(self):
        p=self.root/bridge.LOD_ROOT/self.receipt['mesh_families'][0]['lods']['1']['source_file']
        p.write_bytes(b'broken')
        with self.assertRaisesRegex(bridge.CuratedBridgeError,'STAGED_ASSET_HASH_MISMATCH'):
            bridge.build_plan(self.root)

    def test_external_rights_cannot_be_promoted_into_inventory(self):
        self.receipt['source_stage_files'][0]['source']=self.receipt['external_license_held'][0]['source']
        self.receipt_path.write_text(json.dumps(self.receipt))
        with self.assertRaisesRegex(bridge.CuratedBridgeError,'EXTERNAL_LICENSE_SOURCE_IN_STAGE'):
            bridge.build_plan(self.root)

    def test_false_acceptance_gate_never_accepted(self):
        self.receipt['pie_tested']=True
        self.receipt_path.write_text(json.dumps(self.receipt))
        with self.assertRaisesRegex(bridge.CuratedBridgeError,'SOURCE_FALSE_EVIDENCE:pie_tested'):
            bridge.build_plan(self.root)

    def test_editor_records_only_lod_texture_observation(self):
        engine=MockEngine()
        outcome=editor.editor_apply(engine,self.root)
        self.assertEqual(34,outcome['static_meshes_with_verified_lods'])
        self.assertEqual(46,outcome['imported_authored_sidecar_lods'])
        self.assertEqual(63,outcome['configured_packed_textures'])
        self.assertFalse(outcome['gate6_7_closed'])
        self.assertFalse(outcome['collision_nav_verified'])
        self.assertEqual(34,len(outcome['collision_review_pending']))

    def test_missing_asset_registry_entry_fails_closed(self):
        engine=MockEngine()
        engine.EditorAssetLibrary.does_asset_exist=lambda path: False
        with self.assertRaisesRegex(RuntimeError,'P1C01_STATIC_MESH_ASSET_REGISTRY_MISSING'):
            editor.editor_apply(engine,self.root)
        self.assertFalse((self.root/'Saved/P1C01CuratedEditorPostImport/receipt.json').exists())

    def test_failed_editor_import_does_not_leave_success_receipt(self):
        engine=MockEngine()
        original=engine.EditorStaticMeshLibrary.import_lod
        engine.EditorStaticMeshLibrary.import_lod=lambda *args:-1
        try:
            with self.assertRaisesRegex(RuntimeError,'P1C01_AUTHORED_LOD_IMPORT_FAILED'):
                editor.editor_apply(engine,self.root)
        finally:
            engine.EditorStaticMeshLibrary.import_lod=original
        self.assertFalse((self.root/'Saved/P1C01CuratedEditorPostImport/receipt.json').exists())


if __name__=='__main__': unittest.main()
