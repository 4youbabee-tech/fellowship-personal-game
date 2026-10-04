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
        self.assertEqual(packet["source_family"]["title"],"KayKit Character Pack: Adventurers")
        self.assertEqual(packet["source_family"]["source_revision"],"672074b73ba276876a19e8816ecdc5241817ab47")
        self.assertTrue(packet["source_policy"]["blend_as_intermediate_only"])
        self.assertFalse(packet["source_policy"]["direct_obj_for_animated_character"])
        self.assertEqual(packet["source_policy"]["max_ue4_candidates"],2)
        self.assertGreaterEqual(packet["source_policy"]["max_hosted_candidates"],8)
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
            "HOSTED_DEFORMATION_PREFLIGHT_REJECT",
            "probe_p1c01_human_fbx_deformation.py",
            "HUMAN_WAVE2_HOSTED_FAST_REJECT",
            "--python-exit-code 18",
            "NORMALIZATION_REJECT_EXIT_",
            "HUMAN_WAVE2_CANDIDATE_HOSTED_RESULT",
            "HUMAN_WAVE2_CANDIDATE_FAST_REJECT",
            "HUMAN_WAVE2_HOSTED_SWEEP",
            "source_revision",
            "direct_source_count",
            "direct_fbx_sources",
            "HUMAN_WAVE2_DIRECT_SOURCE_IDENTITY_DRIFT",
            "HUMAN_WAVE2_DIRECT_SOURCE_PASS",
            "NORMALIZED_DERIVATIVE_SHA_EQUALS_RAW_SOURCE",
            "verification_page",
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

        commandlet=(root/"Source"/"ShireJourneyEditorTools"/"Private"/"ShireProductionImportCommandlet.cpp").read_text(encoding="utf-8")
        self.assertIn("bUseT0AsRefPose = true",commandlet)
        self.assertIn("use-t0-ref-pose=yes",commandlet)
        workflow=(root/".github"/"workflows"/"p1c01-human-wave2.yml").read_text(encoding="utf-8")
        self.assertIn("Hosted CC0 human source + Blender normalization",workflow)
        self.assertIn("UE4.27.2 Human Wave 2 skeletal gate",workflow)
        self.assertIn("if: needs.hosted_source_factory.outputs.selected_count != '0'",workflow)
        self.assertIn("ci_build_unreal.cmd",workflow)
        self.assertIn("Source/ShireJourneyEditorTools/Private/ShireProductionImportCommandlet.cpp",workflow)
        self.assertIn("ls-files --others --exclude-standard",workflow)
        self.assertIn("Hosted Frodo static deformation stress",workflow)
        self.assertIn("if: always()",workflow)
        self.assertIn("Fail fast before UE4 when hosted deformation preflight rejects all candidates",workflow)
        self.assertIn("run_p1c01_human_wave3_deformation.py",workflow)
        self.assertIn("Stage stable UE4 evidence contract",workflow)
        self.assertIn("shire-human-wave2-ue4-artifact",workflow)
        self.assertIn("HUMAN_WAVE2_ARTIFACT_CONTRACT_FAIL",workflow)
        self.assertIn("--python-exit-code 17",workflow)
        self.assertIn("HUMAN_WAVE3_DEFORMATION_CONTRACT_PASS",workflow)
        self.assertIn('test -s "$RUNNER_TEMP/shire-human-wave3/ue4/p1c01_human_wave2_ue4.json"',workflow)
        deformation=(root/"Scripts"/"run_p1c01_human_wave3_deformation.py").read_text(encoding="utf-8")
        for token in (
            "shoulders",
            "elbows",
            "knees",
            "hands_feet",
            "locomotion_stress",
            "visual_deformation_accepted",
            "retarget_accepted",
            'if not pb.bone.use_deform:',
            "joint_influence_counts",
            "required deform joints have no weighted vertex influence",
            "min_required_displacement",
            "NO_NONTRIVIAL_DEFORMATION",
            "bone_influence_count",
        ):
            self.assertIn(token,deformation)
        self.assertIn("upperleg",deformation)
        hosted_deformation=(root/"Scripts"/"probe_p1c01_human_fbx_deformation.py").read_text(encoding="utf-8")
        self.assertIn('"upperleg"',hosted_deformation)
        gate=json.loads((root/"Data"/"P1C01HumanDeformationGateV1.json").read_text(encoding="utf-8"))
        self.assertFalse(gate["runtime_contract"]["visual_deformation_accepted"])
        self.assertFalse(gate["runtime_contract"]["retarget_accepted"])
        self.assertFalse(gate["runtime_contract"]["runtime_integration_allowed"])


if __name__=="__main__":
    unittest.main()
