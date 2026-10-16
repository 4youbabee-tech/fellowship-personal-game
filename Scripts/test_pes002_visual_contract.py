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
        self.assertIn('PES002_CAPTURE_STARTUP_TIMEOUT', ps)
        self.assertLess(ps.index('Remove-Item -LiteralPath $log'), ps.index('$proc = Start-Process'))
        self.assertIn('PES002_EDITOR_EXITED_EARLY', ps)
        self.assertIn('PES002_SCREENSHOT_REQUESTED target=BagEnd view=3', ps)
        self.assertIn('for ($view = 0; $view -lt 4; $view++)', ps)
        self.assertIn('PES002_LUMINANCE_TOO_DARK', ps)
        self.assertIn('PES002_LUMINANCE_METRIC', ps)
        self.assertIn('proofOnly=1 views=4', (ROOT / 'Source/ShireJourney/Private/World/ShirePrototypeWorldBuilder.cpp').read_text(encoding='utf-8'))
        self.assertIn('$width -ne 1280 -or $height -ne 720', ps)
        workflow = (ROOT / ".github/workflows/unreal-build-validation.yml").read_text(encoding="utf-8")
        section = workflow.split("      - name: Capture Bag End targeted P1C01 visual proof", 1)[1].split("      - name:", 1)[0]
        self.assertNotIn('continue-on-error: true', section)

    def test_managed_resident_path_follows_ground_probed_endpoint_elevations(self):
        # M1 source regression only; actual 4.27.2 traversal/visual FPS remain separate.
        director = (ROOT / "Source/ShireJourney/Private/World/LivingWorldDirector.cpp").read_text(encoding="utf-8")
        npc = (ROOT / "Source/ShireJourney/Private/Characters/ShireAmbientNPC.cpp").read_text(encoding="utf-8")
        self.assertIn("ResolveGroundedAmbientPoint(Location, SpawnLocation)", director)
        self.assertIn("ResolveGroundedAmbientPoint(RoutineEnd, GroundedRoutineEnd)", director)
        self.assertIn('NPC->Tags.AddUnique(TEXT("LivingWorldManaged"))', director)
        # Flyers/fauna never enter the last, ground-bound walking branch.
        movement = npc.rsplit("const FVector Direction = ToTarget.GetSafeNormal2D();", 1)[1]
        self.assertIn('ActorHasTag(TEXT("LivingWorldManaged")) && LivingWorldDirector.IsValid()', movement)
        self.assertIn("const float PlanarLengthSq = Segment.X * Segment.X + Segment.Y * Segment.Y;", movement)
        self.assertIn("PlanarLengthSq > KINDA_SMALL_NUMBER", movement)
        self.assertIn("FMath::IsFinite(RoutinePointA.Z)", movement)
        self.assertIn("FMath::IsFinite(RoutinePointB.Z)", movement)
        self.assertIn("FMath::Clamp(", movement)
        self.assertIn("FMath::Lerp(RoutinePointA.Z, RoutinePointB.Z, Fraction)", movement)
        self.assertIn("FVector(Current.X, Current.Y, ExpectedZ)", movement)
        self.assertNotIn("LineTraceSingleByChannel", movement)
        self.assertNotIn("SetActorEnableCollision(true)", movement)
        self.assertNotIn("GetPlayerPawnCached()", movement)

    def test_bag_end_imported_fbx_architecture_is_world_placed_safely(self):
        cpp = (ROOT / "Source/ShireJourney/Private/World/ShirePrototypeWorldBuilder.cpp").read_text(encoding="utf-8")
        header = (ROOT / "Source/ShireJourney/Public/World/ShirePrototypeWorldBuilder.h").read_text(encoding="utf-8")
        self.assertIn("RequestBagEndArchitecture();", cpp)
        self.assertIn("BagEndArchLoader.RequestAsyncLoad(", cpp)
        self.assertIn("OnBagEndArchitectureReady()", cpp)
        self.assertIn("PES002_ARCH_GARDEN importedFamilies=", cpp)
        self.assertIn("PES002BagEndImportedFBXGround", cpp)
        self.assertIn("Group->AddInstanceWorldSpace(", cpp)
        self.assertIn("BagEndArchHandle->CancelHandle();", cpp)
        self.assertIn("BagEndArchSources", header)
        for name in ("SM_ShGardenCart_LOD0", "SM_ShGardenPlanter_LOD0",
                     "SM_ShGardenHedge_LOD0", "SM_ShLanternPost_LOD0", "SM_ShStonePath_LOD0"):
            self.assertIn(name, cpp)
        self.assertNotIn("PES002_BAG_END_WOODLAND_FBX_REPLACEMENT", cpp)

    def test_bag_end_curated_pbr_shrub_swap_preserves_entrance(self):
        cpp = (ROOT / "Source/ShireJourney/Private/World/ShirePrototypeWorldBuilder.cpp").read_text(encoding="utf-8")
        section = cpp.split("// Bag End close-up: swap sparse", 1)[1].split(
            "// PR484 additional canopy replacement", 1)[0]
        self.assertIn("PES002_BAG_END_PBR_SHRUBS", section)
        self.assertIn("CuratedNatureSources[Family].Get()", section)
        self.assertIn("Target->GetStaticMesh()!=Replacement", section)
        self.assertIn("PES002BagEndPBRGardenGround", section)
        self.assertIn("ConvertedIndices.Num()<18", section)
        self.assertIn("FMath::Abs(At.Y+520.0f)<205.0f", section)
        self.assertIn("ShrubInstances->RemoveInstance(ConvertedIndices[J]);", section)
        self.assertNotIn("SetCollisionEnabled", section)

    def test_incident_captures_real_window_focus_and_ue4_native_stat_file(self):
        proof = (ROOT / "Scripts/capture_pes002_bag_end_visual.ps1").read_text(encoding="utf-8")
        preview = (ROOT / "SHIRE_FAST_PIE_PREVIEW.bat").read_text(encoding="utf-8")
        cpp = (ROOT / "Source/ShireJourney/Private/World/ShirePrototypeWorldBuilder.cpp").read_text(encoding="utf-8")
        self.assertIn("GetForegroundWindow", proof)
        self.assertIn("GetWindowThreadProcessId", proof)
        self.assertIn("PES002_WINDOW_FOCUS_SUMMARY", proof)
        self.assertIn("PES002_PERF_INCONCLUSIVE_BACKGROUND_THROTTLE", proof)
        self.assertIn("PES002_INCIDENT_STATFILE_ARCHIVED", proof)
        self.assertIn("-PES002PerformanceIncident", preview)
        for stat in ("stat unit", "stat rhi", "stat streaming", "stat startfile", "stat stopfile"):
            self.assertIn('TEXT("' + stat + '")', cpp)
        self.assertNotIn('TEXT("stat renderfile")', cpp)

    def test_bag_end_hero_exterior_keeps_entrance_visible(self):
        cpp = (ROOT / "Source/ShireJourney/Private/World/ShirePrototypeWorldBuilder.cpp").read_text(encoding="utf-8")
        self.assertIn('PES002_BAG_END_HERO_FACADE', cpp)
        self.assertIn('bUseAuthoredHero = bBagEndHero && ProductionBagEndHeroFacadeMesh', cpp)
        self.assertIn('roof=joined door=recessed windows=2 collision=none', cpp)
        hero = cpp.split('if (bUseAuthoredHero)', 1)[1].split('else if (bHasProductionFacade)', 1)[0]
        self.assertIn('SpawnShape(ProductionBagEndHeroFacadeMesh', hero)
        self.assertNotIn('CylinderMesh', hero)
        self.assertNotIn('ProductionTurfMoundMesh', hero)
        self.assertIn('if (!bUseAuthoredHero)', cpp)
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
        self.assertEqual(text.count("usemtl Stone"), 1)
        self.assertEqual(text.count("usemtl Wood"), 1)
        self.assertGreater(text.count("\nf "), 500)
        plan = json.loads((ROOT / "Data/ChapterAssetStreamingPlan.json").read_text(encoding="utf-8"))
        self.assertIn(
            "/Game/Production/World/Shire/SM_ShBagEndHeroFacade.SM_ShBagEndHeroFacade",
            plan["banks"]["P1C01"]["assets"],
        )

    def test_hero_geometry_has_uvs_valid_triangles_and_bound_finishes(self):
        text = (ROOT / "SourceAssets/Production/World/Shire/SM_ShBagEndHeroFacade.obj").read_text()
        vertices = [tuple(map(float, line.split()[1:])) for line in text.splitlines() if line.startswith('v ')]
        uvs = [line for line in text.splitlines() if line.startswith('vt ')]
        faces = [line.split()[1:] for line in text.splitlines() if line.startswith('f ')]
        materials = {line.split()[1] for line in text.splitlines() if line.startswith('usemtl ')}
        mtl = (ROOT / 'SourceAssets/Production/World/Shire/ShireMaterials.mtl').read_text()
        self.assertEqual(len(materials), 7)
        self.assertLess(len(faces), 3000)  # a single bounded hero asset, not a scenery rebuild
        for name in materials:
            self.assertIn('newmtl ' + name + '\n', mtl)
        for face in faces:
            self.assertEqual(len(face), 3)
            coords = []
            for ref in face:
                v, uv = map(int, ref.split('/'))
                self.assertTrue(1 <= v <= len(vertices))
                self.assertTrue(1 <= uv <= len(uvs))
                coords.append(vertices[v-1])
            a,b,c = coords
            u = [b[i]-a[i] for i in range(3)]
            v = [c[i]-a[i] for i in range(3)]
            cross = (u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
            self.assertGreater(sum(x*x for x in cross), 1e-10)
        src = (ROOT / "Source/ShireJourneyEditorTools/Private/ShireProductionImportCommandlet.cpp").read_text()
        self.assertIn('PES002_HERO_MATERIALS_REJECT', src)
        self.assertIn('Found && Found->MaterialInterface', src)
        self.assertIn('HeroRenderData->LODResources[0].Sections', src)
        self.assertIn('RequiredSlots.Contains(Drawn.MaterialSlotName) && Drawn.MaterialInterface', src)
        self.assertIn('DrawnFinishes.Num() == RequiredSlots.Num()', src)
        self.assertNotIn('StaticMaterials.Num() == RequiredSlots.Num()', src)

    def test_hero_facade_import_is_single_named_package_not_split_groups(self):
        src = (ROOT / "Source/ShireJourneyEditorTools/Private/ShireProductionImportCommandlet.cpp").read_text(encoding="utf-8")
        self.assertIn('Relative.Equals(TEXT("World/Shire/SM_ShBagEndHeroFacade.obj")', src)
        self.assertIn('ImportOptions->StaticMeshImportData->bCombineMeshes = true;', src)
        self.assertIn('ImportOptions->StaticMeshImportData->bAutoGenerateCollision = false;', src)
        self.assertIn('PES002_HERO_FACADE_IMPORT_REJECT', src)
        self.assertIn('bExactHeroPackageResolved &&', src)
        # The 30-way split was observed on exact-head UE4.27 CI, not inferred from file count.
        self.assertIn('FindObject<UStaticMesh>(nullptr, *ExpectedObjectPath)', src)

    def test_round_door_and_windows_face_west_not_upwards(self):
        cpp = (ROOT / "Source/ShireJourney/Private/World/ShirePrototypeWorldBuilder.cpp").read_text(encoding="utf-8")
        hobbit = cpp.split("void AShirePrototypeWorldBuilder::SpawnHobbitHole(", 1)[1].split(
            "void AShirePrototypeWorldBuilder::SpawnFenceLine(", 1
        )[0]
        # UE4 Engine Cylinder uses local Z as its axis; yaw rotates in XY and
        # cannot turn an upward-facing circle into an entrance on the west wall.
        # Hero, fallback, timber rims and window glass all need pitch instead.
        self.assertEqual(hobbit.count("FRotator(90.0f, 0.0f, 0.0f)"), 4)
        self.assertNotIn("FRotator(0.0f, 90.0f, 0.0f)", hobbit)
        self.assertIn("door=recessed windows=2", hobbit)

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
