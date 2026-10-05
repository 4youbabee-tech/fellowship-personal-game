import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrodoUE4AnimationImportContract(unittest.TestCase):
    def test_commandlet_is_animation_only_after_exact_rig_import(self):
        cpp = (ROOT/'Source'/'ShireJourneyEditorTools'/'Private'/'ShireFrodoAnimationImportCommandlet.cpp').read_text(encoding='utf-8')
        for token in (
            'EFBXImportType::FBXIT_Animation',
            'Options->bImportMesh = false',
            'Options->bImportAnimations = true',
            'Options->Skeleton = Skeleton',
            'Sequence->GetSkeleton() == Skeleton',
            'Sequence->GetNumberOfFrames()',
            'Sequence->GetPlayLength()',
            'ReferenceBoneCount != 48',
            'bUseT0AsRefPose = true',
            'UE4_ANIMATION_IMPORT_TECHNICAL_PASS',
            'ExpectedRigObjectPath',
            'ExpectedSequenceObjectPath',
            'GetAssetByObjectPath',
            'RigAssetData.AssetClass == USkeletalMesh::StaticClass()->GetFName()',
            'SequenceAssetData.AssetClass != UAnimSequence::StaticClass()->GetFName()',
        ):
            self.assertIn(token, cpp)

    def test_exact_three_fbx_roles_only(self):
        cpp = (ROOT/'Source'/'ShireJourneyEditorTools'/'Private'/'ShireFrodoAnimationImportCommandlet.cpp').read_text(encoding='utf-8')
        for name in ('Frodo_Idle_Retarget.fbx','Frodo_Walk_Retarget.fbx','Frodo_Run_Retarget.fbx'):
            self.assertIn(name, cpp)
        self.assertNotIn('.obj', cpp.lower())
        self.assertNotIn('.bmp', cpp.lower())

    def test_workflow_hosted_preflight_precedes_self_hosted_ue4(self):
        workflow = (ROOT/'.github'/'workflows'/'p1c01-frodo-ue4-animation-import.yml').read_text(encoding='utf-8')
        self.assertIn('hosted_artifact_preflight:', workflow)
        self.assertIn('runs-on: ubuntu-latest', workflow)
        self.assertIn('ue4_animation_import:', workflow)
        self.assertIn('needs: hosted_artifact_preflight', workflow)
        self.assertIn('self-hosted', workflow)
        self.assertIn('ci_build_unreal.cmd', workflow)
        self.assertIn('set "SHIRE_BUILD_WORKSPACE=%SHIRE_FRODO_UE4_SOURCE%"', workflow)
        build_script = (ROOT/'Scripts'/'ci_build_unreal.cmd').read_text(encoding='utf-8')
        self.assertIn('if defined SHIRE_BUILD_WORKSPACE set "BUILD_WORKSPACE=%SHIRE_BUILD_WORKSPACE%"', build_script)
        self.assertIn('CI_BUILD_WORKSPACE root=%BUILD_WORKSPACE%', build_script)
        self.assertIn('ShireFrodoAnimationImport', workflow)
        self.assertIn('UE4_ANIMATION_IMPORT_TECHNICAL_PASS', workflow)


if __name__ == '__main__':
    unittest.main()
