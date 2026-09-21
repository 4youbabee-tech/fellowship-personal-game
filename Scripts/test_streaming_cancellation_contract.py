"""Source-contract regression guards, not a substitute for UE runtime tests."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class StreamingCancellationContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stream = (ROOT / 'Source/ShireJourney/ShireChapterAssetStreamingSubsystem.cpp').read_text()
        cls.router = (ROOT / 'Source/ShireJourney/ChapterWorldRouter.cpp').read_text()

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
