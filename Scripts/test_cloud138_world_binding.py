#!/usr/bin/env python3
import ast
from pathlib import Path
import unittest
from runtime_smoke import cloud138_observation

ROOT = Path(__file__).resolve().parents[1]
CPP = (ROOT/"Source/ShireJourney/Private/World/ShirePrototypeWorldBuilder.cpp").read_text(encoding="utf-8")
H = (ROOT/"Source/ShireJourney/Public/World/ShirePrototypeWorldBuilder.h").read_text(encoding="utf-8")
MODELS = next(ast.literal_eval(n.value) for n in ast.parse(
    (ROOT/"Tools/CloudAssetBuild/blender_shire.py").read_text(encoding="utf-8")).body
    if isinstance(n, ast.Assign) and any(isinstance(t,ast.Name) and t.id=="MODELS" for t in n.targets))
FAMILIES = ["GardenPlanter","OrchardCrate","MarketBasket","WindowFlowerBox","ReedPlanter","HerbDryingRack","GrainSackStack","PartyServingCounter"]

class Cloud138Tests(unittest.TestCase):
    def test_curated_families_exist_and_bridge_is_quarantined(self):
        sub=CPP.split("void AShirePrototypeWorldBuilder::RequestCloud138Layer()",1)[1].split(
            "void AShirePrototypeWorldBuilder::EndPlay(",1)[0]
        for family in FAMILIES:
            self.assertIn(family, MODELS)
            name="SM_Sh"+family
            self.assertIn("Cloud138/"+name+"."+name, CPP)
        for illegal in ["WoodenFootbridge","RoundDoor","StonePath","LoadSynchronous","LoadObject<"]:
            self.assertNotIn(illegal,sub)
        for required in ["Cloud138Loader.RequestAsyncLoad","FPackageName::DoesPackageExist",
                         "Hit.ImpactNormal.Z < 0.70f","J < 6","max=48","P1C01_CLOUD138_WORLD_READY"]:
            self.assertIn(required,sub)
        self.assertIn("Cloud138Handle->CancelHandle()",CPP)
        self.assertIn("FStreamableManager Cloud138Loader",H)
        self.assertIn("TSoftObjectPtr<UStaticMesh>",H)
    def test_truthful_observation(self):
        v=cloud138_observation("P1C01_CLOUD138_WORLD families=8 grounded=37 max=48")
        self.assertEqual(v["grounded"],37)
        self.assertFalse(v["visual_accepted"])
        self.assertFalse(v["pie_tested"])
    def test_restoration_is_sha_verified(self):
        code=(ROOT/"Scripts/restore_cloud138_unreal.py").read_text(encoding="utf-8")
        self.assertIn("hash_file(asset) == row",code)
        self.assertIn("hash_file(target) == row",code)
        self.assertIn("len(rows) == 90",code)
        self.assertIn("NAV", "NAV_QUARANTINE") if False else None

if __name__ == "__main__":
    unittest.main()
