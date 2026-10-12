#!/usr/bin/env python3
"""Authored P1C01 nature runtime bridge static regression (not PIE proof)."""
import pathlib
import unittest

from runtime_smoke import curated_nature_observation

ROOT = pathlib.Path(__file__).resolve().parents[1]
CPP = ROOT / "Source/ShireJourney/Private/World/ShirePrototypeWorldBuilder.cpp"
HEADER = ROOT / "Source/ShireJourney/Public/World/ShirePrototypeWorldBuilder.h"
ASSETS = ("grass_meadow", "garden_reed", "rock_field",
          "shrub_gorse", "shrub_hedge", "tree_apple",
          "tree_elm", "tree_oak", "tree_willow")

class CuratedNatureRuntimeContracts(unittest.TestCase):
    def test_nine_original_imported_assets_are_soft_and_optional(self):
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

    def test_multi_zone_traces_are_bounded_and_cull_preserved(self):
        source = CPP.read_text(encoding="utf-8")
        region = source.split("void AShirePrototypeWorldBuilder::OnCuratedNatureLayerReady()", 1)[1]
        region = region.split("void AShirePrototypeWorldBuilder::EndPlay(", 1)[0]
        self.assertIn("const FVector Anchors[9][3]", region)
        self.assertIn("Anchors[I][J % 3]", region)
        self.assertIn("Hit.ImpactNormal.Z < 0.70f", region)
        self.assertIn("missingGround=%d steepGround=%d", region)
        self.assertIn("I < 5 ? 12 : 8", region)
        self.assertIn("max=92", region)

    def test_observation_is_truthful_and_not_pie_evidence(self):
        observed = curated_nature_observation(
            "P1C01_CURATED_NATURE_WORLD families=9 grounded=68 max=92 "
            "collision=none async=1 missingGround=21 steepGround=0 PIE_device_visual=pending")
        self.assertEqual("instanced_unreviewed", observed["status"])
        self.assertEqual(68, observed["grounded"])
        self.assertFalse(observed["visual_accepted"])
        self.assertFalse(observed["pie_tested"])
        self.assertEqual("optional_packages_absent", curated_nature_observation(
            "P1C01_CURATED_NATURE_WORLD deferred=9 optional-packages-not-staged")["status"])
        self.assertEqual("not_observed", curated_nature_observation("other log line")["status"])

    def test_existing_world_only_and_bound_grounded_instances(self):
        source = CPP.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        self.assertIn("RequestCuratedNatureLayer();", source)
        self.assertIn("CuratedNatureSources.Num() != 9", source)
        self.assertIn("I < 5 ? 12 : 8", source)
        self.assertIn("LineTraceSingleByChannel", source)
        self.assertIn("ECollisionEnabled::NoCollision", source)
        self.assertIn("PIE_device_visual=pending", source)
        self.assertIn("CuratedNatureLoadHandle->CancelHandle()", source)
        self.assertIn("UHierarchicalInstancedStaticMeshComponent", header)
        self.assertNotIn("CuratedNature", (ROOT/"Data/ChapterAssetStreamingPlan.json").read_text(encoding="utf-8"))
if __name__ == "__main__":
    unittest.main()
