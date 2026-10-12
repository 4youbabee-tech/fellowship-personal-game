#!/usr/bin/env python3
"""Authored P1C01 nature runtime bridge static regression (not PIE proof)."""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CPP = ROOT / "Source/ShireJourney/Private/World/ShirePrototypeWorldBuilder.cpp"
HEADER = ROOT / "Source/ShireJourney/Public/World/ShirePrototypeWorldBuilder.h"
ASSETS = ("grass_meadow", "garden_reed", "rock_field",
          "shrub_gorse", "shrub_hedge")

class CuratedNatureRuntimeContracts(unittest.TestCase):
    def test_five_original_imported_assets_are_soft_and_optional(self):
        source = CPP.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        for key in ASSETS:
            name = "SM_Sh_" + key + "_LOD0"
            self.assertIn("CuratedP1C01/Nature/Meshes/" + name + "." + name, source)
        self.assertIn("TSoftObjectPtr<UStaticMesh>", header)
        self.assertIn("FStreamableManager CuratedNatureLoader", header)
        self.assertIn("FPackageName::DoesPackageExist", source)
        self.assertIn("CuratedNatureLoader.RequestAsyncLoad", source)
        section = source.split("void AShirePrototypeWorldBuilder::RequestCuratedNatureLayer()", 1)[1]
        section = section.split("void AShirePrototypeWorldBuilder::EndPlay(", 1)[0]
        self.assertNotIn("LoadObject<", section)
        self.assertNotIn("LoadSynchronous", section)
        self.assertIn("bCuratedNatureRequested = true", section)

    def test_existing_world_only_and_bound_grounded_instances(self):
        source = CPP.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        self.assertIn("RequestCuratedNatureLayer();", source)
        self.assertIn("CuratedNatureSources.Num() != 5", source)
        self.assertIn("J < 12", source)
        self.assertIn("LineTraceSingleByChannel", source)
        self.assertIn("ECollisionEnabled::NoCollision", source)
        self.assertIn("PIE_device_visual=pending", source)
        self.assertIn("CuratedNatureLoadHandle->CancelHandle()", source)
        self.assertIn("UHierarchicalInstancedStaticMeshComponent", header)
        self.assertNotIn("CuratedNature", (ROOT/"Data/ChapterAssetStreamingPlan.json").read_text(encoding="utf-8"))
if __name__ == "__main__":
    unittest.main()
