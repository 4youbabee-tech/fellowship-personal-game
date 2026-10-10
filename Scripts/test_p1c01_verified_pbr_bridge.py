#!/usr/bin/env python3
"""Offline evidence for verified FBX source -> importer -> runtime-bank bridge."""
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import p1c01_verified_pbr_bridge as bridge

class VerifiedPBRBridgeTest(unittest.TestCase):
    def setUp(self):
        self.root=tempfile.TemporaryDirectory()
        self.addCleanup(self.root.cleanup)
        self.work=Path(self.root.name)
        self.project=self.work/"project"
        (self.project/"Data").mkdir(parents=True)
        (self.project/"Data/ChapterAssetStreamingPlan.json").write_text(
            json.dumps({"banks":{"P1C01":{"assets":["/Game/Production/World/Shire/existing.existing"]}}}))
        self.warehouse=self.work/"warehouse"
        self.wave="test_wave"
        self.wave_root=self.warehouse/"_p1c01_adaptive_polyhaven"/self.wave
        self.wave_root.mkdir(parents=True)
        self.slug="barrel_01"
        files=[]
        def save(name,role):
            dest=self.wave_root/"assets"/self.slug/"prepared"/name
            dest.parent.mkdir(parents=True,exist_ok=True)
            content=(bridge.FBX+b"\x00"*80) if role=="FBX" else (
                bridge.PNG+b"\x00"*8+struct.pack(">II",1024,1024)+b"\x00"*24)
            dest.write_bytes(content)
            files.append({"file":str(dest),"asset_slug":self.slug,
                 "provider":"POLY_HAVEN","license":"CC0",
                 "bytes":len(content),"sha256":hashlib.sha256(content).hexdigest(),
                 "state":"SOURCE_PBR_PENDING_STATIC_GEOMETRY_LOD_COLLISION_QC"})
        save(self.slug+".fbx","FBX")
        maps=[]
        for role in ("BaseColor","NormalDX","ORM"):
            name="TX_"+self.slug+"_"+role+".png"
            save(name,role)
            maps.append({"path":"assets/"+self.slug+"/"+name,
                         "role":role,"resolution":[1024,1024]})
        (self.wave_root/"source_receipt_original.json").write_text('{"license":"CC0"}')
        pbr={"prepared_assets":1,"assets":[{
            "id":self.slug,"status":"STATIC_SOURCE_QC_ONLY","maps":maps}]}
        (self.wave_root/"pbr_receipt_original.json").write_text(json.dumps(pbr))
        sha=lambda n:hashlib.sha256((self.wave_root/n).read_bytes()).hexdigest()
        self.receipt={"wave":self.wave,"stage":"PERSISTENT_WAREHOUSE_SOURCE_ONLY",
          "license":"CC0","provider":"POLY_HAVEN","original_source_count":1,
          "converted_fbx_count":1,"asset_ids":[self.slug],"quarantined_ids":[],
          "files":files,
          "source_receipt_sha256":sha("source_receipt_original.json"),
          "pbr_receipt_sha256":sha("pbr_receipt_original.json")}
        (self.wave_root/"receipt_adaptive_pbr.json").write_text(json.dumps(self.receipt))
        patcher=patch.object(bridge,"WAVES",((self.wave,1,1),))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_stage_hash_qc_and_idempotent(self):
        a=bridge.stage(self.warehouse,self.project)
        b=bridge.stage(self.warehouse,self.project)
        self.assertEqual(a,b)
        self.assertEqual(a[0]["id"],self.slug)
        self.assertIn("map_Kd TX_barrel_01_BaseColor.png",
                      (self.project/"SourceAssets/Production/World/Shire/VerifiedPBR/barrel_01/barrel_01.mtl").read_text())

    def test_tampered_original_is_blocked(self):
        f=self.wave_root/"assets"/self.slug/"prepared"/(self.slug+".fbx")
        f.write_bytes(b"not an FBX")
        with self.assertRaisesRegex(bridge.PromotionError,"SOURCE_HASH_MISMATCH"):
            bridge.stage(self.warehouse,self.project)

    def test_missing_unreal_uasset_never_enables_bank(self):
        bridge.stage(self.warehouse,self.project)
        with self.assertRaisesRegex(bridge.PromotionError,"UE_PACKAGE_MISSING"):
            bridge.activate(self.project)
        plan=json.loads((self.project/"Data/ChapterAssetStreamingPlan.json").read_text())
        self.assertEqual(len(plan["banks"]["P1C01"]["assets"]),1)

    def test_source_material_hold_is_excluded(self):
        f=self.wave_root/"pbr_receipt_original.json"
        x=json.loads(f.read_text());x["assets"][0]["status"]="HOLD_BIOME"
        f.write_text(json.dumps(x))
        r=self.receipt.copy()
        r["pbr_receipt_sha256"]=hashlib.sha256(f.read_bytes()).hexdigest()
        (self.wave_root/"receipt_adaptive_pbr.json").write_text(json.dumps(r))
        with self.assertRaisesRegex(bridge.PromotionError,"NO_SUITABLE"):
            bridge.stage(self.warehouse,self.project)

    def test_ue_presence_promotes_soft_path_once(self):
        rows=bridge.stage(self.warehouse,self.project)
        d=self.project/"Content/Production/World/Shire/VerifiedPBR"/self.slug
        d.mkdir(parents=True)
        (d/(self.slug+".uasset")).write_bytes(b"x"*4000)
        (d/("MI_P1C01_"+self.slug+".uasset")).write_bytes(b"x"*4000)
        bridge.activate(self.project)
        bridge.activate(self.project)
        p=json.loads((self.project/"Data/ChapterAssetStreamingPlan.json").read_text())
        self.assertEqual(len(p["banks"]["P1C01"]["assets"]),2)
        visual=json.loads((self.project/"Data/P1C01VerifiedWorldDecor.json").read_text())
        self.assertEqual(visual["status"],"UE_PACKAGES_PRESENT_RENDER_QC_PENDING")
        self.assertEqual(visual["accents"][0]["location"],rows[0]["location"])

    def test_world_importer_and_async_contract(self):
        root=Path(__file__).resolve().parents[1]
        code=(root/"Source/ShireJourneyEditorTools/Private/ShireProductionImportCommandlet.cpp").read_text()
        world=(root/"Source/ShireJourney/Private/World/ShirePrototypeWorldBuilder.cpp").read_text()
        self.assertIn("P1C01_VERIFIED_PBR_IMPORT_QC",code)
        self.assertIn("StaticMaterials.Num() != 1",code)
        self.assertIn("SpawnVerifiedPBRDecor();",world)
        self.assertIn("ECollisionEnabled::NoCollision",world)
        self.assertIn("ResolveResidentStaticMesh(*AssetPath)",world)
        self.assertIn("P1C01VerifiedWorldDecor.json",
            (root/"Source/ShireJourney/ShireJourney.Build.cs").read_text())
if __name__=="__main__":
    unittest.main()
