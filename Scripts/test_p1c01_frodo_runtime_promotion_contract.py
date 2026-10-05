import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class FrodoRuntimePromotionContract(unittest.TestCase):
    def test_streaming_uses_async_core_locomotion_assets(self):
        header = (ROOT/'Source'/'ShireJourney'/'Public'/'Subsystems'/'ShireChapterAssetStreamingSubsystem.h').read_text(encoding='utf-8')
        cpp = (ROOT/'Source'/'ShireJourney'/'Private'/'Subsystems'/'ShireChapterAssetStreamingSubsystem.cpp').read_text(encoding='utf-8')
        self.assertIn('ResolveCharacterLocomotionAssets', header)
        self.assertIn('FSoftObjectPath IdleAnimationPath', header)
        self.assertIn('FSoftObjectPath WalkAnimationPath', header)
        self.assertIn('FSoftObjectPath RunAnimationPath', header)
        self.assertIn('/Game/Production/Characters/Rigs/%s/SK_%s.SK_%s', cpp)
        self.assertIn('const FString RigToken = bFrodo ? FString(TEXT("FRODO")) : Character;', cpp)
        for token in (
            '/Game/Production/Characters/Animations/FRODO/A_Frodo_Idle.A_Frodo_Idle',
            '/Game/Production/Characters/Animations/FRODO/A_Frodo_Walk.A_Frodo_Walk',
            '/Game/Production/Characters/Animations/FRODO/A_Frodo_Run.A_Frodo_Run',
            'StreamableManager.RequestAsyncLoad',
            'Rig.bAnimBlueprintPackagePresent',
            'Rig.bSequenceLocomotionRequired',
        ):
            self.assertIn(token, cpp)
        region = cpp[cpp.index('void UShireChapterAssetStreamingSubsystem::RequestCharacterRig'):]
        self.assertNotIn('RequestSyncLoad', region)
        self.assertNotIn('LoadObject<', region)
        self.assertNotIn('StaticLoadObject', region)

    def test_player_promotes_only_after_core_assets_are_resident(self):
        header = (ROOT/'Source'/'ShireJourney'/'Public'/'Characters'/'ShirePlayerCharacter.h').read_text(encoding='utf-8')
        cpp = (ROOT/'Source'/'ShireJourney'/'Private'/'Characters'/'ShirePlayerCharacter.cpp').read_text(encoding='utf-8')
        self.assertIn('UAnimSequence* ProductionIdleAnimation', header)
        self.assertIn('UAnimSequence* ProductionWalkAnimation', header)
        self.assertIn('UAnimSequence* ProductionRunAnimation', header)
        start = cpp.index('bool AShirePlayerCharacter::TryApplyProductionRig')
        end = cpp.index('bool AShirePlayerCharacter::ShouldShowPrototypeWeaponForCurrentStory', start)
        region = cpp[start:end]
        self.assertLess(region.index('ResolveCharacterLocomotionAssets'), region.index('GetMesh()->SetVisibility(true, true)'))
        self.assertIn('EAnimationMode::AnimationSingleNode', region)
        self.assertIn('GetMesh()->PlayAnimation(Idle, true)', region)
        self.assertIn('idle-walk-run-sequences', region)
        self.assertIn('UpdateProductionSkeletalAnimation();', cpp)
        self.assertIn('ProductionRunAnimation : ProductionWalkAnimation', cpp)


if __name__ == '__main__':
    unittest.main()
