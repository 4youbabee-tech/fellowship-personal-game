"""Focused source-contract tests; never a substitute for UE4/rendered evidence."""
import json
import subprocess
import tempfile
import wave
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
        self.assertIn('AttachThreadInput', ps)
        self.assertIn('BringWindowToTop', ps)
        self.assertIn('SetActiveWindow($handle)', ps)
        self.assertIn('SetFocus($handle)', ps)
        self.assertIn('if ($attachedForeground)', ps)
        self.assertIn('if ($attachedTarget)', ps)
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

    def test_new_bag_end_cobbled_approach_is_original_uv_mapped_and_streamed(self):
        source = (ROOT / "SourceAssets/Production/World/Shire/SM_ShBagEndCobbledWalk.obj").read_text()
        faces = [line for line in source.splitlines() if line.startswith("f ")]
        vertices = [line for line in source.splitlines() if line.startswith("v ")]
        uv = [line for line in source.splitlines() if line.startswith("vt ")]
        self.assertIn("o SM_ShBagEndCobbledWalk", source)
        self.assertIn("mtllib ShireMaterials.mtl", source)
        self.assertIn("usemtl Stone", source)
        self.assertEqual(len(faces), 1440)
        self.assertEqual(len(vertices), 1008)
        self.assertEqual(len(uv), 1008)
        for triangle in faces:
            for ref in triangle.split()[1:]:
                v, tex = map(int, ref.split("/"))
                self.assertTrue(1 <= v <= len(vertices))
                self.assertTrue(1 <= tex <= len(uv))
        cpp = (ROOT / "Source/ShireJourney/Private/World/ShirePrototypeWorldBuilder.cpp").read_text()
        plan = json.loads((ROOT / "Data/ChapterAssetStreamingPlan.json").read_text())
        self.assertIn("PES002_BAG_END_COBBLED_WALK", cpp)
        self.assertIn("ProductionBagEndCobbledWalkMesh", cpp)
        self.assertIn('PathActor->GetStaticMeshComponent()->SetCastShadow(false)', cpp)
        self.assertIn("/Game/Production/World/Shire/SM_ShBagEndCobbledWalk.SM_ShBagEndCobbledWalk", plan["banks"]["P1C01"]["assets"])

    def test_pes002_authored_cottages_and_oaks_have_valid_triangle_uv_tangents(self):
        """Reject true zero-area geometry or UV triangles before costly Unreal import."""
        for name in ("SM_ShBagshotThatchedCottage",
                     "SM_ShBagshotTimberCottage", "SM_ShShireMatureOak"):
            source = (ROOT / "SourceAssets/Production/World/Shire" /
                      (name + ".obj")).read_text(encoding="utf-8")
            vertices = [tuple(map(float, line.split()[1:]))
                        for line in source.splitlines() if line.startswith("v ")]
            uv = [tuple(map(float, line.split()[1:]))
                  for line in source.splitlines() if line.startswith("vt ")]
            faces = [line.split()[1:] for line in source.splitlines()
                     if line.startswith("f ")]
            self.assertGreater(len(faces), 1000, name)
            self.assertEqual(len(vertices), 3 * len(faces), name)
            self.assertEqual(len(uv), len(vertices), name)
            for face_number, face in enumerate(faces, 1):
                self.assertEqual(len(face), 3, (name, face_number))
                ids = [tuple(map(int, entry.split("/"))) for entry in face]
                p = [vertices[vi - 1] for vi, _ in ids]
                t = [uv[ti - 1] for _, ti in ids]
                e = [p[1][j] - p[0][j] for j in range(3)]
                f = [p[2][j] - p[0][j] for j in range(3)]
                cross = (e[1] * f[2] - e[2] * f[1],
                         e[2] * f[0] - e[0] * f[2],
                         e[0] * f[1] - e[1] * f[0])
                self.assertGreater(sum(c * c for c in cross), 1e-12,
                                   (name, face_number, "zero geometric area"))
                uv_area = ((t[1][0] - t[0][0]) * (t[2][1] - t[0][1]) -
                           (t[1][1] - t[0][1]) * (t[2][0] - t[0][0]))
                self.assertGreater(abs(uv_area), 1e-9,
                                   (name, face_number, "zero UV tangent basis"))

    def test_one_cohesive_shire_houses_trees_sound_and_dialogue_batch(self):
        builder = (ROOT / "Source/ShireJourney/Private/World/ShirePrototypeWorldBuilder.cpp").read_text(encoding="utf-8")
        importer = (ROOT / "Source/ShireJourneyEditorTools/Private/ShireProductionImportCommandlet.cpp").read_text(encoding="utf-8")
        bank = json.loads((ROOT / "Data/ChapterAssetStreamingPlan.json").read_text(encoding="utf-8"))
        for name in ("SM_ShBagshotThatchedCottage",
                     "SM_ShBagshotTimberCottage", "SM_ShShireMatureOak"):
            obj = ROOT / "SourceAssets/Production/World/Shire" / (name + ".obj")
            source = obj.read_text(encoding="utf-8")
            vertices = [line for line in source.splitlines() if line.startswith("v ")]
            uv = [line for line in source.splitlines() if line.startswith("vt ")]
            faces = [line for line in source.splitlines() if line.startswith("f ")]
            self.assertGreater(len(faces), 1000, name)
            self.assertEqual(len(vertices), len(faces) * 3, name)
            self.assertEqual(len(uv), len(vertices), name)
            self.assertIn("mtllib ShireMaterials.mtl", source)
            self.assertIn("usemtl ", source)
            self.assertIn(
                "/Game/Production/World/Shire/" + name + "." + name,
                bank["banks"]["P1C01"]["assets"],
            )
            for face in faces:
                for vertex in face.split()[1:]:
                    vi, ti = (int(s) for s in vertex.split("/"))
                    self.assertTrue(1 <= vi <= len(vertices))
                    self.assertTrue(1 <= ti <= len(uv))
        for group, cue in [
            ("Ambience", "Amb_ShireMorning"),
            ("Ambience", "Amb_ShireRoad"),
            ("Ambience", "Amb_PartyField"),
            ("SFX", "Sfx_WagonDistant"),
        ]:
            source = ROOT / "SourceAssets/Production/Audio/Shire" / group / (cue + ".wav")
            with wave.open(str(source), "rb") as sound:
                self.assertEqual(sound.getnchannels(), 1)
                self.assertEqual(sound.getsampwidth(), 2)
                self.assertEqual(sound.getframerate(), 22050)
                self.assertGreater(sound.getnframes(), 22000)
            self.assertIn(cue, (ROOT / "Source/ShireJourney/Private/Subsystems/ShireStoryPresentationSubsystem.cpp").read_text(encoding="utf-8"))
        self.assertIn("P1C01_AUDIO_UASSET_SAVED", importer)
        self.assertIn("P1C01_AUDIO_BATCH_PERSISTED", importer)
        self.assertIn('TEXT("/Game/Audio/Ambience")', importer)
        self.assertIn("USoundWave* ImportedSound", importer)
        self.assertIn("PES002_BAGSHOT_COTTAGES", builder)
        self.assertIn("PES002_BAG_END_MATURE_OAKS", builder)
        self.assertIn("Side_GardenHelpStarted", builder)
        self.assertIn("Side_PartyTablesStarted", builder)
        self.assertIn("PES002MatureOakTerrain", builder)

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

    def test_p1c01_settlement_houses_use_batched_authored_visuals(self):
        cpp = (ROOT / "Source/ShireJourney/Private/World/ShirePrototypeWorldBuilder.cpp").read_text(encoding="utf-8")
        section = cpp.split("// Above-ground cottages make Hobbiton read", 1)[1].split(
            "SpawnProd(ProductionWellMesh", 1)[0]
        self.assertIn("SpawnCottageVisualCluster", section)
        self.assertIn("Configure(Mesh, false, 1600, 8500)", section)
        self.assertIn("AuthoredVisuals->AddDetailInstance(At, Rotation, Scale)", section)
        self.assertIn('OriginalComponent->SetVisibility(false, true)', section)
        self.assertIn('PES002PreservedCottageCollision', section)
        self.assertIn("ProductionBagshotThatchedCottageMesh", section)
        self.assertIn("ProductionBagshotTimberCottageMesh", section)
        self.assertNotIn("bNearBagEnd", section)
        self.assertIn("max=7 visualHISM=2", section)

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


    def test_project_owned_shire_canopy_has_broad_lobed_uv_geometry(self):
        generator = ROOT / "Tools/CloudAssetBuild/generate_shire_tree_canopy.py"
        tracked = ROOT / "SourceAssets/Production/World/Shire/SM_ShTreeCanopy.obj"
        with tempfile.TemporaryDirectory() as tmp:
            generated = Path(tmp) / tracked.name
            subprocess.run(["python3", str(generator), "--output", str(generated)], check=True, cwd=ROOT)
            self.assertEqual(generated.read_bytes(), tracked.read_bytes())
        source = tracked.read_text(encoding="utf-8")
        vertices = [tuple(map(float, line.split()[1:])) for line in source.splitlines() if line.startswith("v ")]
        uvs = [line for line in source.splitlines() if line.startswith("vt ")]
        faces = [line.split()[1:] for line in source.splitlines() if line.startswith("f ")]
        self.assertIn("five overlapped, UV-mapped foliage lobes", source)
        self.assertEqual(len(vertices), 285)
        self.assertEqual(len(uvs), len(vertices))
        self.assertEqual(len(faces), 500)
        bounds = [max(v[i] for v in vertices) - min(v[i] for v in vertices) for i in range(3)]
        self.assertGreater(bounds[0] / bounds[2], 1.10)
        self.assertGreater(bounds[1] / bounds[2], 1.00)
        for face in faces:
            self.assertEqual(len(face), 3)
            for ref in face:
                vertex, uv = map(int, ref.split("/"))
                self.assertTrue(1 <= vertex <= len(vertices))
                self.assertTrue(1 <= uv <= len(uvs))

if __name__ == "__main__":
    unittest.main()
