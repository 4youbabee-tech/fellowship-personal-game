"""Focused source-contract tests; never a substitute for UE4/rendered evidence."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PES002VisualContract(unittest.TestCase):
    def test_evidence_camera_is_opt_in_and_no_player_teleport(self):
        cpp = (ROOT / "Source/ShireJourney/Private/World/ShirePrototypeWorldBuilder.cpp").read_text(encoding="utf-8")
        self.assertIn('#if !UE_BUILD_SHIPPING', cpp)
        self.assertIn('FParse::Param(FCommandLine::Get(), TEXT("PES002VisualProof"))', cpp)
        self.assertIn('PC->SetViewTarget(ProofCamera);', cpp)
        self.assertIn('const FVector LookAt(-2210.0f, -520.0f, 105.0f);', cpp)
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

    def test_bag_end_hero_exterior_keeps_entrance_visible(self):
        cpp = (ROOT / "Source/ShireJourney/Private/World/ShirePrototypeWorldBuilder.cpp").read_text(encoding="utf-8")
        self.assertIn('PES002_BAG_END_HERO_FACADE', cpp)
        self.assertIn('ProductionBagEndHeroFacadeMesh', cpp)
        self.assertIn('FVector(200.0f, 0.0f, 14.0f * Scale)', cpp)
        self.assertIn('FVector(3.40f, 3.20f, 2.80f) * Scale', cpp)
        self.assertIn('asset=%s moundOffsetX=200', cpp)
        self.assertIn('FVector(0.57f, 0.57f, 0.06f) * Scale', cpp)
        self.assertIn('!bBagEndHero', cpp)
        self.assertIn('FVector(-2210.0f, -520.0f, 0.0f)', cpp)
        self.assertIn('FVector(-3070.0f, -520.0f, 285.0f)', cpp)
        self.assertIn('SetFieldOfView(48.0f)', cpp)
        self.assertIn('ApproachStones.Reserve(10)', cpp)
        self.assertIn('GardenPlanters.Reserve(6)', cpp)
        self.assertIn('WoodPiles.Reserve(4)', cpp)
        self.assertIn('cap=4 collision=none tick=none', cpp)
        self.assertIn('cap=8 collision=none tick=none', cpp)

    def test_dedicated_bag_end_facade_is_deterministic_curved_authored_mesh(self):
        generator = ROOT / "Tools/CloudAssetBuild/generate_bag_end_hero_facade.py"
        tracked = ROOT / "SourceAssets/Production/World/Shire/SM_ShBagEndHeroFacade.obj"
        with tempfile.TemporaryDirectory() as tmp:
            generated = Path(tmp) / tracked.name
            subprocess.run(
                ["python3", str(generator), "--output", str(generated)],
                check=True,
                cwd=ROOT,
            )
            self.assertEqual(generated.read_bytes(), tracked.read_bytes())
        text = tracked.read_text(encoding="utf-8")
        self.assertIn("o SM_ShBagEndHeroFacade", text)
        self.assertGreaterEqual(text.count("usemtl Stone"), 4)
        self.assertGreaterEqual(text.count("usemtl Wood"), 4)
        self.assertGreater(text.count("\nf "), 500)
        plan = json.loads((ROOT / "Data/ChapterAssetStreamingPlan.json").read_text(encoding="utf-8"))
        self.assertIn(
            "/Game/Production/World/Shire/SM_ShBagEndHeroFacade.SM_ShBagEndHeroFacade",
            plan["banks"]["P1C01"]["assets"],
        )

    def test_round_door_and_windows_face_west_not_upwards(self):
        cpp = (ROOT / "Source/ShireJourney/Private/World/ShirePrototypeWorldBuilder.cpp").read_text(encoding="utf-8")
        hobbit = cpp.split("void AShirePrototypeWorldBuilder::SpawnHobbitHole(", 1)[1].split(
            "void AShirePrototypeWorldBuilder::SpawnFenceLine(", 1
        )[0]
        # UE4 Engine Cylinder uses local Z as its axis; yaw rotates in XY and
        # cannot turn an upward-facing circle into an entrance on the west wall.
        # Hero, fallback, timber rims and window glass all need pitch instead.
        self.assertEqual(hobbit.count("FRotator(90.0f, 0.0f, 0.0f)"), 6)
        self.assertNotIn("FRotator(0.0f, 90.0f, 0.0f)", hobbit)
        self.assertIn("PES002_BAG_END_ROUND_FACADE_ORIENTATION=pitch90", hobbit)

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
