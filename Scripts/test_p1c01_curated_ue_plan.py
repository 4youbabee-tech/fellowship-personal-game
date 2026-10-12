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

    nature_names = ['flower_wild','garden_reed','grass_meadow','rock_field','rock_river',
                    'shrub_gorse','shrub_hawthorn','shrub_hedge',
                    'tree_apple','tree_elm','tree_oak','tree_willow']
    nature_surfaces = ['Bark','Grass','Hedge','LeafAutumn','LeafGreen',
                       'Reed','Soil','Stone','Wildflower']
    for i in range(34):
        nature = i < 12
        scope = 'Nature' if nature else 'Architecture'
        name = nature_names[i] if nature else 'hobbit_%02d' % i
        levels = {}
        for lod in range(3 if nature else 2):
            rel = '%s/Meshes/SM_Sh_%s_LOD%d.fbx' % (scope, name, lod)
            data = ('Kaydara FBX Binary  \x00\x1a\x00' + 'dummy:%02d-%d' % (i,lod)).encode()
            entry = add(rel, bridge.CONTENT_ROOT if lod==0 else bridge.LOD_ROOT,
                        data, 'L01_TREES' if nature else 'L03_BAG_END_HERO_ARCH',
                        'UE4_COMMANDLET_BASE_STATIC_MESH' if lod==0 else 'UE4_EDITOR_LOD_ONLY_NOT_SEPARATE_MESH')
            levels[str(lod)] = entry
        families.append({'id':scope+'/SM_Sh_'+name,'expected_lod_count':len(levels),
                         'base_asset_path':bridge.ASSET_ROOT +
                             Path(levels['0']['source_file']).with_suffix('').as_posix(),
                         'lods':levels,
                         'collision_policy':'SIMPLE_REVIEW_TREE_TRUNK' if nature else 'SIMPLIFIED_AUTHOR_COLLIDER_REVIEW',
                         'hism_candidate':nature})
    for i in range(21):
        surface = ('T_Sh_'+nature_surfaces[i]) if i<9 else 'surface_%02d'%i
        group = ('Nature' if i<9 else 'Regional')+'/'+surface
        triplet = {}
        for kind in ['BaseColor','NormalDX','ORM']:
            rel = '%s/Textures/%s_%s.png' % ('Nature' if i<9 else 'Regional',surface,kind)
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


class MockObject:
    def __init__(self, path=''):
        self.path = path
    def get_path_name(self):
        if self.path.startswith('/Game/'):
            return self.path + '.' + self.path.rsplit('/', 1)[1]
        return self.path

class MockMaster(MockObject):
    params = ('AlbedoTexture', 'NormalTexture', 'ORMTexture')

class MockInstance(MockObject):
    def __init__(self, path=''):
        super().__init__(path)
        self.props = {}
        self.parameters = {}
    def set_editor_property(self, key, value): self.props[key] = value
    def get_editor_property(self, key): return self.props[key]

class MockFactory:
    def set_editor_property(self, key, value):
        raise AssertionError('UNSUPPORTED_FACTORY_PROPERTY:' + str(key))

class MockMesh(MockObject):
    def __init__(self, path=''):
        super().__init__(path)
        self.verts=[120]
        self.materials=[None]
    def set_material(self, index, material): self.materials[index] = material
    def get_material(self, index): return self.materials[index]


class MockTexture(MockObject):
    def __init__(self, path=''):
        super().__init__(path)
        self.props={}
    def set_editor_property(self,k,v): self.props[k]=v
    def get_editor_property(self,k): return self.props[k]


class MockEngine:
    StaticMesh = MockMesh
    Texture2D = MockTexture
    MaterialInterface = MockMaster
    MaterialInstanceConstant = MockInstance
    MaterialInstanceConstantFactoryNew = MockFactory

    class TextureCompressionSettings:
        TC_DEFAULT = 'TC_DEFAULT'
        TC_NORMALMAP = 'TC_NORMALMAP'
        TC_MASKS = 'TC_MASKS'

    def __init__(self, root):
        self.root = Path(root)
        self.objects={}
        engine=self
        class Paths:
            @staticmethod
            def project_content_dir(): return str(engine.root/'Content')
        self.Paths = Paths
        class Tools:
            @staticmethod
            def create_asset(name, folder, cls, factory):
                path = folder+'/'+name
                obj = MockInstance(path)
                engine.objects[path] = obj
                return obj
        class ToolsHelpers:
            @staticmethod
            def get_asset_tools(): return Tools
        self.AssetToolsHelpers = ToolsHelpers
        class Editing:
            @staticmethod
            def get_texture_parameter_names(material): return list(material.params)
            @staticmethod
            def set_material_instance_parent(obj, parent): obj.props['parent']=parent
            @staticmethod
            def set_material_instance_texture_parameter_value(obj, name, value):
                if getattr(engine, 'fail_parameter', None)==name: return False
                obj.parameters[name] = value
                # Simulate real editor regressions: False despite a valid write.
                return not getattr(engine, 'false_but_applied', False)
            @staticmethod
            def get_material_instance_texture_parameter_value(obj, name): return obj.parameters.get(name)
            @staticmethod
            def update_material_instance(obj): pass
        self.MaterialEditingLibrary = Editing
        class AssetLibrary:
            @staticmethod
            def load_asset(path):
                if path not in engine.objects:
                    if path == editor.PBR_PARENT: engine.objects[path] = MockMaster(path)
                    elif '/Textures/' in path: engine.objects[path] = MockTexture(path)
                    elif '/Materials/' in path: return None
                    else: engine.objects[path] = MockMesh(path)
                return engine.objects[path]
            @staticmethod
            def save_loaded_asset(asset,only_if_is_dirty=False):
                rel = asset.get_path_name().split('.', 1)[0].removeprefix('/Game/') + '.uasset'
                target = engine.root/'Content'/rel
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(b'MOCK_ONLY_NOT_REAL_UASSET')
                return True
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
            def get_number_materials(mesh): return len(mesh.materials)
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
        engine=MockEngine(self.root)
        outcome=editor.editor_apply(engine,self.root)
        self.assertEqual(34,outcome['static_meshes_with_verified_lods'])
        self.assertEqual(46,outcome['imported_authored_sidecar_lods'])
        self.assertEqual(63,outcome['configured_packed_textures'])
        self.assertEqual(21,outcome['created_or_updated_material_instances'])
        self.assertEqual(63,outcome['material_triplet_bindings'])
        self.assertEqual(8,outcome['exact_nature_single_slot_bindings'])
        self.assertEqual(118,outcome['physically_persisted_uasset_checks'])
        self.assertFalse(outcome['gate6_7_closed'])
        self.assertFalse(outcome['collision_nav_verified'])
        self.assertEqual(34,len(outcome['collision_review_pending']))

    def test_missing_asset_registry_entry_fails_closed(self):
        engine=MockEngine(self.root)
        engine.EditorAssetLibrary.does_asset_exist=lambda path: False
        with self.assertRaisesRegex(RuntimeError,'P1C01_STATIC_MESH_ASSET_REGISTRY_MISSING'):
            editor.editor_apply(engine,self.root)
        self.assertFalse((self.root/'Saved/P1C01CuratedEditorPostImport/receipt.json').exists())

    def test_failed_editor_import_does_not_leave_success_receipt(self):
        engine=MockEngine(self.root)
        original=engine.EditorStaticMeshLibrary.import_lod
        engine.EditorStaticMeshLibrary.import_lod=lambda *args:-1
        try:
            with self.assertRaisesRegex(RuntimeError,'P1C01_AUTHORED_LOD_IMPORT_FAILED'):
                editor.editor_apply(engine,self.root)
        finally:
            engine.EditorStaticMeshLibrary.import_lod=original
        self.assertFalse((self.root/'Saved/P1C01CuratedEditorPostImport/receipt.json').exists())

    def test_unavailable_existing_master_fails_closed(self):
        engine = MockEngine(self.root)
        original = engine.EditorAssetLibrary.load_asset
        engine.EditorAssetLibrary.load_asset = lambda p: None if p == editor.PBR_PARENT else original(p)
        with self.assertRaisesRegex(RuntimeError, 'P1C01_PBR_MASTER_NOT_IMPORTER_AUTHORED'):
            editor.editor_apply(engine, self.root)
        self.assertFalse((self.root/'Saved/P1C01CuratedEditorPostImport/receipt.json').exists())

    def test_missing_master_parameter_fails_closed(self):
        engine = MockEngine(self.root)
        engine.fail_parameter = 'ORMTexture'
        with self.assertRaisesRegex(RuntimeError, 'P1C01_MI_TEXTURE_NOT_PERSISTED'):
            editor.editor_apply(engine, self.root)
        self.assertFalse((self.root/'Saved/P1C01CuratedEditorPostImport/receipt.json').exists())

    def test_setter_false_with_correct_persisted_texture_passes(self):
        engine = MockEngine(self.root)
        engine.false_but_applied = True
        result = editor.editor_apply(engine, self.root)
        self.assertEqual(result['created_or_updated_material_instances'], 21)
        self.assertTrue(result['material_bindings_verified'])

    def test_stale_pbr_master_with_no_required_parameters_rejected(self):
        engine = MockEngine(self.root)
        load = engine.EditorAssetLibrary.load_asset
        def load_stale(path):
            v = load(path)
            if path == editor.PBR_PARENT:
                v.params = ('WrongAlbedo', 'WrongORM')
            return v
        engine.EditorAssetLibrary.load_asset = load_stale
        with self.assertRaisesRegex(RuntimeError, 'P1C01_PBR_MASTER_PARAMETER_SCHEMA_MISSING'):
            editor.editor_apply(engine, self.root)
        self.assertFalse((self.root/'Saved/P1C01CuratedEditorPostImport/receipt.json').exists())

    def test_ambiguous_nature_slot_fails_closed(self):
        engine = MockEngine(self.root)
        initial = engine.EditorAssetLibrary.load_asset
        def load(path):
            value = initial(path)
            if path.endswith('SM_Sh_flower_wild_LOD0'):
                value.materials = [None, None]
            return value
        engine.EditorAssetLibrary.load_asset = load
        with self.assertRaisesRegex(RuntimeError, 'P1C01_NATURE_SLOT_IDENTITY_UNPROVEN'):
            editor.editor_apply(engine, self.root)
        self.assertFalse((self.root/'Saved/P1C01CuratedEditorPostImport/receipt.json').exists())

    def test_missing_physical_uasset_fails_closed(self):
        engine = MockEngine(self.root)
        saved = engine.EditorAssetLibrary.save_loaded_asset
        def incomplete(asset, only_if_is_dirty=False):
            if isinstance(asset, MockInstance):
                return True
            return saved(asset, only_if_is_dirty)
        engine.EditorAssetLibrary.save_loaded_asset = incomplete
        with self.assertRaisesRegex(RuntimeError, 'P1C01_UASSET_NOT_PERSISTED'):
            editor.editor_apply(engine, self.root)
        self.assertFalse((self.root/'Saved/P1C01CuratedEditorPostImport/receipt.json').exists())



    def test_unreal_427_python_commandlet_has_non_silent_entrypoint(self):
        root = Path(__file__).resolve().parents[1]
        wrapper = (root/'Scripts/run_p1c01_curated_ue4.ps1').read_text(encoding='utf-8')
        script = (root/'Scripts/ue4_p1c01_curated_postimport.py').read_text(encoding='utf-8')
        self.assertIn("'-run=pythonscript'", wrapper)
        self.assertIn('("-script=" + $script)', wrapper)
        self.assertNotIn("-ExecutePythonScript=", wrapper)
        self.assertIn("'-stdout'", wrapper)
        self.assertIn('P1C01-Curated-EditorPython.log', wrapper)
        self.assertIn("SHIRE_CURATED_EDITOR_RUN", wrapper)
        self.assertIn("P1C01_CURATED_EDITOR_PYTHON_ENTERED", script)
        self.assertIn("if os.environ.get('SHIRE_CURATED_EDITOR_RUN') == '1':", script)
        self.assertNotIn("if __name__ == '__main__':", script)

    def test_auto_windows_curated_workflow_is_exact_head_and_single_writer(self):
        wf = (Path(__file__).resolve().parents[1] /
              '.github/workflows/unreal-build-validation.yml').read_text(encoding='utf-8')
        classifier = (Path(__file__).resolve().parents[1] /
              'Scripts/classify_unreal_validation.ps1').read_text(encoding='utf-8')
        self.assertIn("github.event_name == 'pull_request'", wf)
        self.assertIn("needs.classify.outputs.curated == 'true'", wf)
        self.assertIn("env.SHIRE_CURATED_REQUIRED == 'true'", wf)
        self.assertIn('run_p1c01_curated_ue4.ps1', wf)
        self.assertIn('Set-Mode "curated"', classifier)
        self.assertIn("Scripts/ue4_p1c01_curated_postimport.py", classifier)
        # The curated branch invokes its one importer through the wrapper.
        self.assertNotIn("if: env.SHIRE_CURATED_REQUIRED == 'true'\n        shell: cmd", wf)

if __name__=='__main__': unittest.main()
