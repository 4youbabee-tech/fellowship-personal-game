#!/usr/bin/env python3
"""Offline negative controls for the Poly Haven source-to-UE bridge."""
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import stage_verified_shire_pbr as bridge

def h(b): return hashlib.sha256(b).hexdigest()
class VerifiedShirePBRTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory(); self.addCleanup(self.t.cleanup)
        self.root=Path(self.t.name); self.wh=self.root/"warehouse"; self.project=self.root/"project"
        self._wave("p1c01_wave39","barrel_01")
        self._wave("p1c01_wave60","stone_01")
        patcher=patch.object(bridge,"WAVES",(("p1c01_wave39",1,1),("p1c01_wave60",1,1)))
        patcher.start(); self.addCleanup(patcher.stop)
    def _wave(self,wave,slug):
        root=self.wh/"_p1c01_adaptive_polyhaven"/wave; root.mkdir(parents=True)
        fbx=b"Kaydara FBX Binary"+b"0"*100
        png=bytes.fromhex("89504e470d0a1a0a")+b"0000IHDR"+struct.pack(">II",1024,1024)+b"0"*40
        files=[];maps=[]
        for role,filename,data in [("STATIC_FBX",slug+".fbx",fbx)]+[
            (role,"TX_"+slug+"_"+role+".png",png) for role in bridge.ROLES]:
            path=root/"assets"/slug/"prepared"/filename
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
            files.append({"file":str(path),"asset_slug":slug,"provider":"POLY_HAVEN","license":"CC0",
                "state":"SOURCE_PBR_PENDING_STATIC_GEOMETRY_LOD_COLLISION_QC",
                "bytes":len(data),"sha256":h(data)})
            if role!="STATIC_FBX":maps.append({"path":"assets/"+slug+"/"+filename,"role":role,"resolution":[1024,1024]})
        source={"license":"CC0"}; pbr={"prepared_assets":1,"assets":[{
            "id":slug,"status":"STATIC_SOURCE_QC_ONLY","maps":maps}]}
        (root/"source_receipt_original.json").write_text(json.dumps(source))
        (root/"pbr_receipt_original.json").write_text(json.dumps(pbr))
        receipt={"wave":wave,"stage":"PERSISTENT_WAREHOUSE_SOURCE_ONLY","license":"CC0",
            "original_source_count":1,"converted_fbx_count":1,"asset_ids":[slug],"files":files,
            "source_receipt_sha256":h((root/"source_receipt_original.json").read_bytes()),
            "pbr_receipt_sha256":h((root/"pbr_receipt_original.json").read_bytes())}
        (root/"receipt_adaptive_pbr.json").write_text(json.dumps(receipt))
    def test_stages_two_assets_and_reuses_verified_bytes(self):
        r=bridge.stage(self.wh,self.project)
        self.assertEqual(r["selected_count"],2)
        self.assertEqual(bridge.stage(self.wh,self.project)["selected_count"],2)
        self.assertTrue((self.project/"SourceAssets/Production/World/Shire/VerifiedPBR/barrel_01/barrel_01.fbx").is_file())
    def test_corrupted_source_cannot_be_reused(self):
        path=self.wh/"_p1c01_adaptive_polyhaven/p1c01_wave39/assets/barrel_01/prepared/barrel_01.fbx"
        path.write_bytes(b"tampered")
        with self.assertRaisesRegex(bridge.IntakeError,"SOURCE_SHA256_MISMATCH"):
            bridge.stage(self.wh,self.project)
    def test_hold_fbx_is_excluded(self):
        root=self.wh/"_p1c01_adaptive_polyhaven/p1c01_wave39"
        item=json.loads((root/"pbr_receipt_original.json").read_text())
        item["assets"][0]["status"]="HOLD_BIOME"
        (root/"pbr_receipt_original.json").write_text(json.dumps(item))
        receipt=json.loads((root/"receipt_adaptive_pbr.json").read_text())
        receipt["pbr_receipt_sha256"]=h((root/"pbr_receipt_original.json").read_bytes())
        (root/"receipt_adaptive_pbr.json").write_text(json.dumps(receipt))
        self.assertEqual(bridge.stage(self.wh,self.project)["selected_count"],1)
    def test_tampered_source_receipt_blocks_stage(self):
        root=self.wh/"_p1c01_adaptive_polyhaven/p1c01_wave39"
        (root/"source_receipt_original.json").write_text('{"license":"UNKNOWN"}')
        with self.assertRaisesRegex(bridge.IntakeError,"PINNED_RECEIPT_HASH_MISMATCH"):
            bridge.stage(self.wh,self.project)
    def test_static_importer_binds_verified_material_explicitly(self):
        path=Path(__file__).resolve().parents[1]/"Source/ShireJourneyEditorTools/Private/ShireProductionImportCommandlet.cpp"
        text=path.read_text(encoding="utf-8")
        self.assertIn("P1C01_VERIFIED_PBR_IMPORT_BIND_PASS",text)
        self.assertIn("P1C01_VERIFIED_PBR_IMPORT_MULTI_SLOT_QC_REQUIRED",text)
    def test_no_source_pass_claims_ue_or_visual(self):
        result=bridge.stage(self.wh,self.project)
        self.assertEqual(result["stage"],"HASH_VERIFIED_SOURCE_ONLY")
        self.assertTrue(all(x["status"]=="SOURCE_STAGED_UNREAL_IMPORT_QC_PENDING" for x in result["assets"]))
if __name__=="__main__":unittest.main()
