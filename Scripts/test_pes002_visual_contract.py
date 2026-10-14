"""Focused source-contract tests; never a substitute for UE4/rendered evidence."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PES002VisualContract(unittest.TestCase):
    def test_evidence_camera_is_opt_in_and_no_player_teleport(self):
        cpp = (ROOT / "Source/ShireJourney/Private/World/ShirePrototypeWorldBuilder.cpp").read_text(encoding="utf-8")
        self.assertIn('#if !UE_BUILD_SHIPPING', cpp)
        self.assertIn('FParse::Param(FCommandLine::Get(), TEXT("PES002VisualProof"))', cpp)
        self.assertIn('PC->SetViewTarget(ProofCamera);', cpp)
        self.assertIn('const FVector LookAt(-2210.0f, -520.0f, 115.0f);', cpp)
        self.assertIn('PES002_CAPTURE_CAMERA_READY target=BagEnd', cpp)
        self.assertIn('FScreenshotRequest::RequestScreenshot(Filename, false, false);', cpp)
        self.assertIn('PES002_CAPTURE_VIEW_READY view=%d', cpp)
        self.assertIn('PES002_BagEnd_View%d.png', cpp)
        self.assertNotIn('PC->GetPawn()->SetActorLocation', cpp)

    def test_capture_fails_closed_when_not_bag_end(self):
        ps = (ROOT / "Scripts/capture_pes002_bag_end_visual.ps1").read_text(encoding="utf-8")
        self.assertIn("'-PES002VisualProof'", ps)
        self.assertNotIn('ExecCmds', ps)
        self.assertIn('PES002_CAPTURE_CAMERA_NOT_CONFIRMED', ps)
        self.assertIn('PES002_BAG_END_SCREENSHOT_MISSING', ps)
        self.assertIn('PES002_CAPTURE_VIEW_NOT_READY', ps)
        self.assertIn('for ($view = 0; $view -lt 3; $view++)', ps)
        self.assertIn('$width -ne 1280 -or $height -ne 720', ps)
        workflow = (ROOT / ".github/workflows/unreal-build-validation.yml").read_text(encoding="utf-8")
        section = workflow.split("      - name: Capture Bag End targeted P1C01 visual proof", 1)[1].split("      - name:", 1)[0]
        self.assertNotIn('continue-on-error: true', section)

    def test_baseline_sky_is_not_overwritten_with_dark_values(self):
        cpp = (ROOT / "Source/ShireJourney/Private/World/ShirePrototypeWorldBuilder.cpp").read_text(encoding="utf-8")
        self.assertIn('SkyComponent->SetIntensity(1.12f);', cpp)
        self.assertIn('float SkyIntensity = 1.12f;', cpp)
        self.assertIn('PES002_DEFERRED_SKYLIGHT_RECAPTURE', cpp)
        self.assertEqual(cpp.count('RecaptureSky()'), 2)  # PG-172 startup + authored story refresh
        self.assertIn('PostProcess->Settings.AutoExposureMaxBrightness = 1.35f;', cpp)
        gov = json.loads((ROOT / "Data/ProjectGovernor.json").read_text(encoding="utf-8"))
        self.assertEqual(gov['pes_immediate_root_cause_repair_protocol_2026_10_14']['status'], 'OWNER_MANDATED')


if __name__ == "__main__":
    unittest.main()
