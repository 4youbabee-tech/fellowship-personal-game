"""Source-contract regression guards, not a substitute for UE runtime tests."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class StreamingCancellationContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stream = (ROOT / 'Source/ShireJourney/ShireChapterAssetStreamingSubsystem.cpp').read_text()
        cls.router = (ROOT / 'Source/ShireJourney/ChapterWorldRouter.cpp').read_text()
        cls.player = (ROOT / 'Source/ShireJourney/ShirePlayerCharacter.cpp').read_text()

    def test_cancel_invalidates_before_handle_and_preserves_resident(self):
        body = self.stream.split('::CancelPendingRequest()', 1)[1].split('::Deinitialize()', 1)[0]
        self.assertLess(body.index('++RequestSerial'), body.index('CancelHandle()'))
        self.assertIn('PendingChapterId = NAME_None', body)
        self.assertIn('PendingRouteId = NAME_None', body)
        self.assertNotIn('ResidentHandle.Reset', body)
        self.assertNotIn('OnChapterAssetsReady.Broadcast', body)

    def test_return_to_visible_world_clears_obsolete_request(self):
        body = self.router.split('if (LastLoadedRouteId == RouteId', 1)[1].split('return;', 1)[0]
        for contract in ('PendingChapterId = NAME_None', 'PendingRouteId = NAME_None',
                         'PendingEpisodeId = NAME_None', 'CancelPendingRequest()'):
            self.assertIn(contract, body)

    def test_resident_fast_path_also_cancels_pending(self):
        body = self.stream.split('if (IsChapterBankReady(ChapterId, RouteId))', 1)[1].split('return;', 1)[0]
        self.assertLess(body.index('CancelPendingRequest()'), body.index('OnChapterAssetsReady.Broadcast'))

    def test_transition_checkpoint_waits_for_committed_world(self):
        tick = self.player.split('::Tick(float DeltaSeconds)', 1)[1].split('::BeginPlay()', 1)[0]
        self.assertIn('PendingChapterCheckpointId != NAME_None && IsCurrentWorldCommitted()', tick)
        self.assertLess(tick.index('IsCurrentWorldCommitted()'), tick.index('SaveAutomaticCheckpoint'))
        begin = self.player.split('::BeginPlay()', 1)[1].split('::EndPlay(', 1)[0]
        self.assertIn('PendingChapterCheckpointId = TEXT("WC_P1C01_START")', begin)
        self.assertNotIn('SaveAutomaticCheckpoint(TEXT("WC_P1C01_START")', begin)

    def test_save_restore_defers_transform_until_committed_world(self):
        restore = self.player.split('::RestoreSaveSnapshot(', 1)[1].split('::SaveAutomaticCheckpoint', 1)[0]
        self.assertIn('bPendingSaveRestoreTransform = true', restore)
        self.assertIn('TryApplyPendingSaveRestoreTransform()', restore)
        self.assertNotIn('SetActorLocationAndRotation(', restore)
        placement = self.router.split('::PlacePlayerAtCommittedTransform(', 1)[1].split('::MovePlayerToChapterStart', 1)[0]
        self.assertIn('IsWorldCommitted(ChapterId, RouteId, EpisodeId)', placement)
        self.assertIn('ResolveGroundedSpawnLocation', placement)
        self.assertLess(placement.index('IsWorldCommitted(ChapterId, RouteId, EpisodeId)'), placement.index('SetActorLocationAndRotation'))

    def test_completion_checks_authoritative_quest_identity(self):
        body = self.router.split('::HandleChapterAssetsReady(FName ChapterId, FName RouteId)', 1)[1].split('CommitChapterWorld(', 1)[0]
        for contract in ('GetCurrentChapterId() != ChapterId', 'GetCurrentRouteId() != RouteId',
                         'GetCurrentEpisodeId() != PendingEpisodeId'):
            self.assertIn(contract, body)
        body = self.stream.split('::HandleAsyncLoadComplete(uint64 CompletedSerial)', 1)[1]
        self.assertLess(body.index('CompletedSerial != RequestSerial'), body.index('OnChapterAssetsReady.Broadcast'))
        self.assertNotIn('ResidentHandle = PendingHandle', body)

        commit = self.stream.split('::CommitPendingRequest(', 1)[1].split('::Deinitialize()', 1)[0]
        self.assertIn('ResidentHandle = PendingHandle', commit)
        self.assertLess(commit.index('if (!bReady)'), commit.index('ResidentHandle = PendingHandle'))


if __name__ == '__main__':
    unittest.main()
