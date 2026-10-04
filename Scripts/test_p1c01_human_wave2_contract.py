import json
import unittest
from pathlib import Path


class HumanWave2ContractTests(unittest.TestCase):
    def test_human_wave2_is_bounded_fbx_only_at_ue4_and_non_runtime(self):
        root=Path(__file__).resolve().parents[1]
        packet=json.loads((root/"Data"/"P1C01HumanCharacterProductionWave2V1.json").read_text(encoding="utf-8"))
        self.assertEqual(packet["runtime_chapter"],"P1C01")
        self.assertEqual(packet["source_family"]["observed_license"],"CC0")
        self.assertEqual(packet["source_family"]["final_animated_format"],"FBX")
        self.assertTrue(packet["source_policy"]["blend_as_intermediate_only"])
        self.assertFalse(packet["source_policy"]["direct_obj_for_animated_character"])
        self.assertEqual(packet["source_policy"]["max_ue4_candidates"],2)
        self.assertLessEqual(packet["source_policy"]["max_zero_weight_ratio"],0.35)
        self.assertTrue(packet["normalization_contract"]["export_deform_bones_only"])
        self.assertFalse(packet["runtime_contract"]["synchronous_heavy_load"])
        self.assertFalse(packet["runtime_contract"]["runtime_promotion_allowed"])
        self.assertIn("linked USkeleton via USkeletalMesh::GetSkeleton() is valid",packet["ue4_hard_gate"])
        self.assertFalse(packet["physics_asset_gate"]["hard_skeletal_import_failure"])

        stage=(root/"Scripts"/"stage_p1c01_human_wave2.ps1").read_text(encoding="utf-8")
        for token in (
            "HUMAN_WAVE2_SOURCE_PAGE_CC0_MARKER_MISSING",
            "HUMAN_WAVE2_ARCHIVE_PATH_UNSAFE",
            "HUMAN_WAVE2_NORMALIZE_FAIL",
            'mesh_smooth_type="FACE"',
            "add_leaf_bones=False",
            "weighted_vertex_count",
            "zero_weight_vertex_count",
            "deform_bone_count",
            "EXCESS_ZERO_WEIGHT_RATIO",
            "use_armature_deform_only=True",
            "uv_layer_count",
            "Get-FileHash",
        ):
            self.assertIn(token,stage)
        self.assertNotIn("LoadObject<",stage)
        self.assertNotIn("RequestSyncLoad",stage)

        probe=(root/"Scripts"/"run_p1c01_human_wave2_ue4.ps1").read_text(encoding="utf-8")
        for token in (
            "SKELETAL_REGISTRATION_FAILED",
            "ZERO_REFERENCE_BONES",
            "MISSING_SMOOTHING_GROUPS",
            "MISSING_BIND_POSE_BONES",
            "INVALID_BIND_POSE",
            "MISSING_UV_SET",
            "LINKED_USKELETON_MISSING",
            "skeletal-skeleton=yes",
            "generated_mesh_package_exists",
            "physics_sanity",
            "runtime_integration_allowed=$false",
        ):
            self.assertIn(token,probe)

        workflow=(root/".github"/"workflows"/"p1c01-human-wave2.yml").read_text(encoding="utf-8")
        self.assertIn("Hosted CC0 human source + Blender normalization",workflow)
        self.assertIn("UE4.27.2 Human Wave 2 skeletal gate",workflow)
        self.assertIn("if: needs.hosted_source_factory.outputs.selected_count != '0'",workflow)
        self.assertIn("ci_build_unreal.cmd",workflow)
        self.assertIn("Source/ShireJourneyEditorTools/Private/ShireProductionImportCommandlet.cpp",workflow)
        self.assertIn("ls-files --others --exclude-standard",workflow)


if __name__=="__main__":
    unittest.main()
