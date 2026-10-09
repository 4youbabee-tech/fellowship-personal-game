import pathlib
import unittest

class P1C01CaptureContractTests(unittest.TestCase):
    def test_capture_has_lifecycle_safety_contract(self):
        path = pathlib.Path(__file__).with_name("ci_capture_p1c01_visuals.cmd")
        text = path.read_text(encoding="utf-8")
        self.assertIn('set "CAPTURE_WAIT_SECONDS=150"', text)
        self.assertIn('set "PROCESS_DRAIN_SECONDS=30"', text)
        self.assertIn('P1C01_RENDER_CAPTURE_PROCESS_DRAIN_PASS', text)
        self.assertIn('reason=ue4_process_drain_timeout', text)
        self.assertIn('waitSeconds=%CAPTURE_WAIT_SECONDS%', text)
        self.assertIn('Format-List', text)

    def test_screenshot_is_requested_only_after_world_commit(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        script = (root / "Scripts" / "ci_capture_p1c01_visuals.cmd").read_text(encoding="utf-8")
        router = (root / "Source" / "ShireJourney" / "Private" / "World" /
                  "ChapterWorldRouter.cpp").read_text(encoding="utf-8")
        header = (root / "Source" / "ShireJourney" / "Public" / "World" /
                  "ChapterWorldRouter.h").read_text(encoding="utf-8")

        self.assertIn("-ShireCapturePose=%X%,%Y%,%Z%,%PITCH%,%YAW%,%ROLL%", script)
        self.assertNotIn("HighResShot 1", script)
        self.assertNotIn("BugItGo %X% %Y%", script)
        for token in (
            "reason=precommit_capture",
            "reason=deferred_camera_not_applied",
            "reason=deferred_camera_not_ready",
            "reason=precommit_screenshot_request",
            "ShireWorldCommit: PASS chapter=P1C01",
            "P1C01_RENDER_CAPTURE_REQUESTED chapter=P1C01 worldCommitted=yes",
        ):
            self.assertIn(token, script)

        self.assertIn("FTimerHandle P1C01VisualPoseTimer;", header)
        self.assertIn("FTimerHandle P1C01VisualScreenshotTimer;", header)
        self.assertIn("FParse::Param(FCommandLine::Get(), TEXT(\"ShireVisualCapture\"))", router)
        self.assertIn("FScreenshotRequest::RequestScreenshot(false);", router)
        self.assertIn("P1C01VisualCaptureRevision != WorldRevision", router)
        self.assertIn("GetWorldTimerManager().ClearTimer(P1C01VisualPoseTimer);", router)
        self.assertLess(
            router.index('TEXT("ShireWorldCommit: PASS chapter=%s route=%s episode=%s revision=%u")'),
            router.index("QueueP1C01VisualCapture();"),
        )


if __name__ == "__main__":
    unittest.main()

