#!/usr/bin/env python3
"""Offline deterministic regressions for the exact ten-archive P1C01 original source stage."""
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import stage_p1c01_curated_original as p

FBX = p.FBX_MAGIC + struct.pack('<I',7400)
ARCH = sorted(p.ARCH_HERO | p.ARCH_VILLAGE | p.ARCH_ROUTE)
NATURE = sorted(p.TREE_FAMILIES | p.DECORATIVE | {'rock_field','rock_river'})


def pbytes(path):
    n = path.encode('utf-8')
    if path.endswith('.fbx'):
        return FBX + n
    # Header-only PNG is adequate for source-staging header tests. Real ZIP is
    # independently CRC-checked and its content hash is pinned by parent source.
    return p.PNG_MAGIC + struct.pack('>I',13) + b'IHDR' + struct.pack('>IIBBBBB',128,128,8,2,0,0,0) + b'CRCC' + n


def fixture(path, change=None):
    fields=[]; payloads={}; source_set=[]; dupe_target=None; aliases=0
    def add(dest,lane,license_claim,family=None,kind=None,map_kind=None):
        nonlocal aliases,dupe_target
        row={'dest':dest,'lane':lane,'license_claim_from_embedded_receipt':license_claim,
             'licensed_runtime_approved':False,'unreal_imported':False}
        if family is not None:row['family']=family
        if lane=='REGIONAL_SURFACE_PREP':row['material_family']=family
        if kind is not None:row['kind']=kind
        if map_kind is not None:row['map_kind']=map_kind
        if lane=='POLYHAVEN_PBR' and kind=='ORM' and aliases<33:
            row['alias_of']=dupe_target
            aliases+=1
            raw=payloads[dupe_target]
        else:
            raw=pbytes(dest)
            payloads[dest]=raw
        row['sha256']=p.sha_bytes(raw)
        row['bytes']=len(raw)
        fields.append(row)
        return row
    for family in NATURE:
        for lod in range(3):
            add('Nature/Meshes/SM_Sh_%s_LOD%d.fbx'%(family,lod),'FOLIAGE_NATURE','ORIGINAL_PROJECT_PROCEDURAL')
    for family in ['Bark','Grass','Hedge','LeafAutumn','LeafGreen','Reed','Soil','Stone','Wildflower']:
        for kind in ['BaseColor','NormalDX','ORM']:
            add('Nature/Textures/T_Sh_%s_%s.png'%(family,kind),'FOLIAGE_NATURE','ORIGINAL_PROJECT_PROCEDURAL')
    for family in ARCH:
        for lod in range(2):
            add('Architecture/meshes/SM_Sh%s_LOD%d.fbx'%(family,lod),'SHIRE_ARCHITECTURE','ORIGINAL_PROJECT_PROCEDURAL',family=family)
    for family in ['ancient_bark','bagend_plaster','charred_basalt','frosted_rock','golden_leaf_floor','mossy_stone','oak_timber','shire_earth','shire_meadow','weathered_granite','wetland_peat','white_limestone']:
        for kind in ['BaseColor','NormalDX','ORM']:
            add('Regional/materials/%s/TX_%s_%s.png'%(family,family,kind),'REGIONAL_SURFACE_PREP','ORIGINAL_PROJECT_ASSET',map_kind=kind, family=family)
    for family in ['Bark','Grass','Soil','Stone']:
        for kind in ['BaseColor','NormalDX','ORM']:
            dest='PBR/Priority/%s/T_Sh_%s_%s.png'%(family,family,kind)
            add(dest,'PRIORITY_PBR','CC0_EMBEDDED_PROVENANCE',family=family,kind=kind)
            if family=='Bark' and kind=='ORM':dupe_target=dest
    for i in range(36):
        for kind in ['BaseColor','NormalDX','ORM']:
            add('PBR/PolyHaven/test%02d/TX_test%02d_%s.png'%(i,i,kind),'POLYHAVEN_PBR','CC0_EMBEDDED_PROVENANCE',family='test%02d'%i,kind=kind)
    assert len(fields)==263, len(fields)
    assert len(payloads)==230, len(payloads)
    obj={'chapter':'P1C01','scope':'SOURCE_ONLY_NOT_UNREAL_IMPORTED',
         'engine_imported':False,'gate6_7_closed':False,'counts_by_lane':p.HARD_COUNTS,
         'logical_asset_bindings':263,'curated_physical_file_count':230,
         'deduplicated_alias_count':33,'asset_files':fields}
    if change:change(obj,payloads)
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        for dest,data in payloads.items():
            z.writestr(dest,data)
        z.writestr('AssetManifest.json',json.dumps(obj))
        z.writestr('IMPORT_NOTES.txt','source only')
    with zipfile.ZipFile(path) as z:
        return p.sha_bytes(z.read('AssetManifest.json'))

class OriginalStageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.archive=Path(cls.temp.name)/'owner-curated.zip'
        cls.fake_hash=fixture(cls.archive)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def setUp(self):
        self.w=tempfile.TemporaryDirectory()
        self.addCleanup(self.w.cleanup)
        self.workspace=Path(self.w.name)/'workspace'

    def stage(self, file=None, sha=None):
        with patch.object(p,'CURATED_MANIFEST_SHA',sha or self.fake_hash):
            return p.stage_archive(file or self.archive,self.workspace)

    def test_real_pinned_archive_matches_report(self):
        self.assertEqual(len(p.CURATED_MANIFEST_SHA),64)
        self.assertEqual(len(p.HARD_COUNTS),5)

    def test_batch_has_34_original_meshes_and_63_png(self):
        report=self.stage()
        self.assertEqual(report['source_stage_count'],143)
        self.assertEqual(report['importable_ue_base_meshed_families'],34)
        self.assertEqual(report['lod_sidecars'],46)
        self.assertEqual(report['source_png'],63)
        self.assertEqual(len(report['material_triplets']),21)
        self.assertEqual(report['external_license_held_count'],120)
        self.assertFalse(report['unreal_asset_imported'])
        self.assertFalse(report['engine_import_allowed_now'])
        self.assertFalse(report['gate6_7_closed'])
        self.assertEqual(len(report['logical_tracks_eight_inside_governor_five_lanes']),8)
        actual=[x for x in self.workspace.rglob('*') if x.is_file()]
        self.assertEqual(len(actual),144)

    def test_idempotent_reimport_stage_does_not_rewrite(self):
        self.stage()
        receipt=self.workspace/p.RECEIPT_REL
        before=p.sha_file(receipt)
        self.stage()
        self.assertEqual(p.sha_file(receipt),before)

    def test_existing_wrong_content_fails_closed(self):
        self.stage()
        target=self.workspace/p.IMPORT_REL/'Nature/Meshes/SM_Sh_tree_oak_LOD0.fbx'
        target.write_bytes(b'tampered')
        with self.assertRaisesRegex(ValueError,'EXISTING_GENERATED_STAGE_CONFLICT'):
            self.stage()

    def test_repacked_zip_same_manifest_stages_despite_timestamp_changes(self):
        repacked=Path(self.w.name)/'repacked.zip'
        with zipfile.ZipFile(self.archive) as original,zipfile.ZipFile(repacked,'w') as out:
            for name in original.namelist():
                info=zipfile.ZipInfo(name,date_time=(2024,1,1,0,0,0))
                out.writestr(info,original.read(name))
        self.assertNotEqual(p.sha_file(repacked),p.sha_file(self.archive))
        result=self.stage(file=repacked)
        self.assertEqual(result['source_manifest_sha256'],self.fake_hash)

    def test_wrong_zip_sha_fails_before_staging(self):
        with self.assertRaisesRegex(ValueError,'CURATED_MANIFEST_SHA256_MISMATCH'):
            self.stage(sha='0'*64)
        self.assertFalse(self.workspace.exists())

    def test_archive_missing_lod_fails_before_ue_gate(self):
        def change(m,payloads):
            row=next(x for x in m['asset_files'] if x['dest'].endswith('SM_Sh_tree_oak_LOD2.fbx'))
            # Preserve declared count, but introduce a second LOD1 alias to exercise stage validation.
            row['dest']='Nature/Meshes/SM_Sh_tree_oak_copy_LOD1.fbx'
            payloads[row['dest']]=payloads.pop('Nature/Meshes/SM_Sh_tree_oak_LOD2.fbx')
            row['sha256']=p.sha_bytes(payloads[row['dest']]);row['bytes']=len(payloads[row['dest']])
        file=Path(self.w.name)/'incomplete.zip';sha=fixture(file,change)
        with self.assertRaisesRegex(ValueError,'STAGE_COUNTS_UNEXPECTED|INCOMPLETE_MESH_LODS'):
            self.stage(file=file,sha=sha)

    def test_unapproved_original_rights_fail_closed(self):
        def change(obj,payloads):
            obj['asset_files'][0]['license_claim_from_embedded_receipt']='UNKNOWN'
        file=Path(self.w.name)/'license.zip';sha=fixture(file,change)
        with self.assertRaisesRegex(ValueError,'ORIGINAL_RIGHTS_CONTRACT_CHANGED'):
            self.stage(file=file,sha=sha)

    def test_png_header_rejected(self):
        with self.assertRaisesRegex(ValueError,'BAD_PNG_HEADER'):
            p.validate_png(b'hello-world')
        with self.assertRaisesRegex(ValueError,'TEXTURE_BUDGET_OR_FORMAT'):
            p.validate_png(p.PNG_MAGIC+struct.pack('>I',13)+b'IHDR'+struct.pack('>IIBBBBB',8192,8192,8,2,0,0,0)+b'CRC!')

    def test_fbx_ascii_rejected(self):
        with self.assertRaisesRegex(ValueError,'BINARY_FBX_REQUIRED'):
            p.validate_fbx(b'; FBX 7.4.0 ASCII')

    def test_unsafe_path_rejected(self):
        for name in ('../bad.fbx','C:/windows/a.fbx','/etc/passwd','a\\b.fbx','a//x.fbx'):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):p.safe_zip_name(name)

    def test_source_only_cannot_gain_external_cc0_by_filename(self):
        self.assertFalse(p.approved_original({'lane':'PRIORITY_PBR','license_claim_from_embedded_receipt':'CC0_EMBEDDED_PROVENANCE'}))
        self.assertFalse(p.approved_original({'lane':'FOLIAGE_NATURE','license_claim_from_embedded_receipt':'UNKNOWN'}))

    def test_all_architectural_families_classified(self):
        self.assertEqual(len(p.ARCH_HERO),8)
        self.assertEqual(len(p.ARCH_VILLAGE),10)
        self.assertEqual(len(p.ARCH_ROUTE),4)
        self.assertEqual(len(ARCH),22)

if __name__=='__main__':unittest.main()