#!/usr/bin/env python3
"""Network-free strict regression for Cloud Shire + regional source warehouse intake."""
import hashlib
import io
import json
import struct
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stage_cloud_wholegame_source import IntakeError, validate_payload, safe_name


def h(data):
    return hashlib.sha256(data).hexdigest()


def synthetic():
    regions = ["REGION_" + str(i).zfill(2) for i in range(28)]
    archive = io.BytesIO()
    shire = []
    regional = []
    materials = []
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for i in range(41):
            for lod in (0, 1):
                name = "meshes/SM_ShSynthetic" + str(i) + "_LOD" + str(lod) + ".fbx"
                payload = b"Kaydara FBX Binary  \x00\x1a\x00" + struct.pack("<I", 7400) + (
                    ("Mesh-S-" + str(i) + "-LOD-" + str(lod)).encode() * 90)
                z.writestr(name, payload)
                shire.append({"path": name, "bytes": len(payload),
                              "sha256": h(payload), "asset": "Synthetic"+str(i),
                              "lod":lod, "export_format":"FBX_BINARY_7400",
                              "collider_count":1,"reimport_uv_layers":1,
                              "reimport_polygons":9})
        for i, reg in enumerate(regions):
            for lod in (0, 1):
                name = "regional_meshes/SM_Region_" + reg + "_LOD" + str(lod) + ".fbx"
                payload = b"Kaydara FBX Binary  \x00\x1a\x00" + struct.pack("<I", 7400) + (
                    ("Mesh-R-" + str(i) + "-LOD-" + str(lod)).encode() * 95)
                z.writestr(name, payload)
                regional.append({"path":name, "bytes":len(payload),
                                 "sha256":h(payload),"region_id":reg, "lod":lod,
                                 "format":"FBX_BINARY_7400","collider_count":1,
                                 "uv_layers":1,"reimport_polygons":9})
        for i in range(12):
            for role in ("BaseColor","NormalDX","ORM"):
                name = "materials/Family" + str(i) + "/TX_" + role + ".png"
                payload = bytes.fromhex("89504e470d0a1a0a") + struct.pack(">I",13) + b"IHDR" + struct.pack(">II", 1024,1024) + b"\x08\x02\x00\x00\x00" + b"\x00"*40
                z.writestr(name, payload)
                materials.append({"path":name,"bytes":len(payload),"sha256":h(payload),"dimensions":[1024,1024]})
        z.writestr("fbx_receipt.json", json.dumps({"asset_count":41,"fbx_count":82,"objects":shire,"runtime_imported":False,"provenance":"ORIGINAL_PROJECT_PROCEDURAL_GEOMETRY"}))
        z.writestr("regional_fbx_receipt.json",json.dumps({"region_count":28,"fbx_count":56,"objects":regional,"warehouse_persisted":False,"unreal_imported":False,"provenance":"ORIGINAL_PROJECT_PROCEDURAL"}))
        z.writestr("materials_receipt.json", json.dumps({"material_families":12,"physical_textures":36,"textures":materials,"region_bindings":[{"id":x} for x in regions],"runtime_imported":False,"license":"ORIGINAL_PROJECT_ASSET"}))
    result=archive.getvalue()
    return result, {"source_zip_sha256":h(result)}


class IntakeTests(unittest.TestCase):
    def test_canonical_physical_receipts(self):
        payload, cfg=synthetic()
        result=validate_payload(payload,cfg)
        self.assertEqual(result["physical_fbx"],138)
        self.assertEqual(result["region_count"],28)
        self.assertEqual(result["textures_png"],36)
    def test_corruption_rejected(self):
        payload,cfg=synthetic()
        with self.assertRaisesRegex(IntakeError,"SOURCE_ZIP_HASH_MISMATCH"):
            validate_payload(payload+b"corrupt",cfg)
    def test_traversal_rejected(self):
        for name in ("../path", "dir/../escape", "/absolute", "C:/drive", "foo\\bar"):
            with self.subTest(name=name):
                with self.assertRaises(IntakeError):
                    safe_name(name)


if __name__=="__main__":
    unittest.main()
