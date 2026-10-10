#!/usr/bin/env python3
"""Offline fail-closed P1C01 source-stage contract tests (no engine/network)."""
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import stage_p1c01_verified_pbr_to_unreal as bridge

def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {"file":str(path),"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),
            "provider":"POLY_HAVEN","license":"CC0",
            "state":"SOURCE_PBR_PENDING_STATIC_GEOMETRY_LOD_COLLISION_QC"}

class VerifiedSourceTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.wh=self.root/"warehouse"
        self.project=self.root/"project"
        plan={"banks":{"P1C01":{"route":"FrodoMain","assets":["/Game/Existing"]}}}
        pf=self.project/"Data/ChapterAssetStreamingPlan.json"
        pf.parent.mkdir(parents=True)
        pf.write_text(json.dumps(plan))
        self.old=bridge.WAVES
        bridge.WAVES=(("p1c01_wave39",1,1),("p1c01_wave60",1,1))
        self.addCleanup(lambda:setattr(bridge,"WAVES",self.old))
        self.create("p1c01_wave39","barrel_01")
        self.create("p1c01_wave60","rock_01")

    def create(self,wave,slug):
        base=self.wh/"_p1c01_adaptive_polyhaven"/wave
        parent=base/"assets"/slug/"prepared"
        mesh=save(parent/(slug+".fbx"),bridge.MAGIC+b"x"*64)
        png=bridge.PNG+b"\x00\x00\x00\x0dIHDR"+struct.pack(">II",1024,1024)+b"x"*24
        maps=[]
        files=[mesh]
        for role in ("BaseColor","NormalDX","ORM"):
            name="TX_"+slug+"_"+role+".png"
            files.append(save(parent/name,png))
            maps.append({"path":"assets/"+slug+"/"+name,"resolution":[1024,1024],"role":role})
        (base/"source_receipt_original.json").write_text(json.dumps({"license":"CC0"}))
        (base/"pbr_receipt_original.json").write_text(json.dumps({
            "prepared_assets":1,"assets":[{"id":slug,"status":"STATIC_SOURCE_QC_ONLY","maps":maps}]}))
        sha=lambda p:hashlib.sha256((base/p).read_bytes()).hexdigest()
        receipt={"stage":"PERSISTENT_WAREHOUSE_SOURCE_ONLY","wave":wave,"license":"CC0",
                 "original_source_count":1,"converted_fbx_count":1,"asset_ids":[slug],
                 "source_receipt_sha256":sha("source_receipt_original.json"),
                 "pbr_receipt_sha256":sha("pbr_receipt_original.json"),"files":files}
        (base/"receipt_adaptive_pbr.json").write_text(json.dumps(receipt))

    def test_stage_copies_actual_fbx_and_png_and_adds_async_bank(self):
        result=bridge.stage(self.wh,self.project)
        self.assertEqual(result["count"],2)
        plan=json.loads((self.project/"Data/ChapterAssetStreamingPlan.json").read_text())
        self.assertEqual(len(plan["p1c01_verified_world_decoration"]),2)
        self.assertEqual(len(plan["banks"]["P1C01"]["assets"]),3)
        for asset in result["assets"]:
            self.assertTrue((self.project/"SourceAssets/Production"/bridge.ROOT/asset/(asset+".fbx")).is_file())

    def test_existing_files_reused_without_overwriting(self):
        first=bridge.stage(self.wh,self.project)
        self.assertEqual(first,bridge.stage(self.wh,self.project))

    def test_corrupted_source_fails_closed(self):
        path=self.wh/"_p1c01_adaptive_polyhaven/p1c01_wave39/assets/barrel_01/prepared/barrel_01.fbx"
        path.write_bytes(b"corrupt")
        with self.assertRaisesRegex(bridge.IntakeError,"SOURCE_DIGEST_FAILED"):
            bridge.stage(self.wh,self.project)

    def test_biome_hold_never_promoted(self):
        root=self.wh/"_p1c01_adaptive_polyhaven/p1c01_wave39"
        file=root/"pbr_receipt_original.json"
        pbr=json.loads(file.read_text())
        pbr["assets"][0]["status"]="HOLD_BIOME"
        file.write_text(json.dumps(pbr))
        rfile=root/"receipt_adaptive_pbr.json"
        receipt=json.loads(rfile.read_text())
        receipt["pbr_receipt_sha256"]=hashlib.sha256(file.read_bytes()).hexdigest()
        rfile.write_text(json.dumps(receipt))
        self.assertEqual(bridge.stage(self.wh,self.project)["count"],1)

if __name__=="__main__":
    unittest.main()
