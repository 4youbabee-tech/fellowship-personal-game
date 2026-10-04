import json
import unittest
from pathlib import Path

from source_contracts import (
    first_member_assignment_position,
    has_nonufs_runtime_dependency,
    has_strict_asset_audit_command,
    signal_precedes_member_mutation,
)


class SourceContractTests(unittest.TestCase):
    def test_asset_audit_supported_python_launchers(self):
        for command in ('python Scripts/asset_quality_audit.py --strict',
                        'python3 Scripts/asset_quality_audit.py --strict',
                        '\'"%PYTHON_EXE%" Scripts/asset_quality_audit.py --strict\'',
                        'cd /d "%SHIRE_PRE_ROOT%" && "%PYTHON_EXE%" Scripts\\asset_quality_audit.py --strict'):
            with self.subTest(command=command):
                self.assertTrue(has_strict_asset_audit_command('        run: ' + command))

    def test_asset_audit_rejects_missing_or_inactive_strict_command(self):
        for line in ('run: python Scripts/asset_quality_audit.py',
                     '# run: python Scripts/asset_quality_audit.py --strict',
                     'run: echo python Scripts/asset_quality_audit.py --strict',
                     'run: python Scripts/asset_quality_audit.py # --strict',
                     'run: python Scripts/asset_quality_audit.py --strict || true',
                     'run: cd /d "%SHIRE_PRE_ROOT%" && "%PYTHON_EXE%" Scripts\\asset_quality_audit.py --strict || true'):
            with self.subTest(line=line):
                self.assertFalse(has_strict_asset_audit_command(line))

    def test_transition_signal_accepts_alias_rhs(self):
        source = """
        void StartChapter()
        {
            TargetChapterId = ChapterId;
            OnWorldTransitionRequested.Broadcast(TargetChapterId);
            CurrentChapterId = TargetChapterId;
        }
        """
        self.assertTrue(signal_precedes_member_mutation(
            source,
            "OnWorldTransitionRequested.Broadcast",
            ("CurrentChapterId", "CurrentEpisodeId", "PlayableCharacterId"),
        ))

    def test_transition_signal_rejects_mutation_first(self):
        source = """
        void StartChapter()
        {
            CurrentChapterId = TargetChapterId;
            OnWorldTransitionRequested.Broadcast(TargetChapterId);
        }
        """
        self.assertFalse(signal_precedes_member_mutation(
            source,
            "OnWorldTransitionRequested.Broadcast",
            ("CurrentChapterId",),
        ))

    def test_comments_and_strings_do_not_fake_mutation(self):
        source = """
        // CurrentChapterId = FakeChapter;
        Log("CurrentChapterId = FakeChapter;");
        OnWorldTransitionRequested.Broadcast(TargetChapterId);
        CurrentChapterId = CanonicalChapterId;
        """
        position = first_member_assignment_position(source, ("CurrentChapterId",))
        self.assertGreater(position, source.find("OnWorldTransitionRequested.Broadcast"))

    def test_nested_route_progress_write_is_not_authoritative_mutation(self):
        source = """
        TargetExisting -> CurrentChapterId = ExistingChapterId;
        TargetExisting->PlayableCharacterId = ExistingCharacterId;
        OnWorldTransitionRequested.Broadcast(TargetChapterId);
        CurrentRouteId = RouteId;
        """
        self.assertTrue(signal_precedes_member_mutation(
            source,
            "OnWorldTransitionRequested.Broadcast",
            ("CurrentRouteId", "CurrentChapterId", "PlayableCharacterId"),
        ))

    def test_explicit_this_member_still_counts_as_authoritative_mutation(self):
        source = """
        this -> CurrentChapterId = TargetChapterId;
        OnWorldTransitionRequested.Broadcast(TargetChapterId);
        """
        self.assertFalse(signal_precedes_member_mutation(
            source,
            "OnWorldTransitionRequested.Broadcast",
            ("CurrentChapterId",),
        ))

    def test_missing_mutation_is_not_a_pass(self):
        source = "OnWorldTransitionRequested.Broadcast(TargetChapterId);"
        self.assertFalse(signal_precedes_member_mutation(
            source,
            "OnWorldTransitionRequested.Broadcast",
            ("CurrentChapterId",),
        ))

    def test_runtime_dependency_requires_nonufs(self):
        build_cs = 'RuntimeDependencies.Add("$(ProjectDir)/Data/NPCSocialModel.json", StagedFileType.NonUFS);'
        self.assertTrue(has_nonufs_runtime_dependency(
            build_cs,
            "Data/NPCSocialModel.json",
        ))

    def test_runtime_dependency_rejects_legacy_untyped_form(self):
        build_cs = 'RuntimeDependencies.Add("$(ProjectDir)/Data/NPCSocialModel.json");'
        self.assertFalse(has_nonufs_runtime_dependency(
            build_cs,
            "Data/NPCSocialModel.json",
        ))

    def test_runtime_dependency_rejects_wrong_staging_type(self):
        build_cs = 'RuntimeDependencies.Add("$(ProjectDir)/Data/NPCSocialModel.json", StagedFileType.UFS);'
        self.assertFalse(has_nonufs_runtime_dependency(
            build_cs,
            "Data/NPCSocialModel.json",
        ))


    def test_living_world_distance_cull_is_member_local(self):
        root = Path(__file__).resolve().parents[1]
        director = (root / "Source" / "ShireJourney" / "Private" / "World" / "LivingWorldDirector.cpp").read_text(encoding="utf-8")
        start = director.index("void ALivingWorldDirector::CleanupExpiredEvents()")
        end = director.index("FName ALivingWorldDirector::ChooseEventType()", start)
        cleanup = director[start:end]

        self.assertIn("LivingWorldEventMemberCull", cleanup)
        self.assertIn("Event.Actors.RemoveAtSwap", cleanup)
        self.assertIn("if (Event.ExpiresAt <= Now)", cleanup)
        self.assertIn("if (Event.Actors.Num() == 0)", cleanup)
        self.assertNotIn("bExpired = true", cleanup)


    def test_p1c01_disposition_rows_are_explicit(self):
        root = Path(__file__).resolve().parents[1]
        disposition = json.loads((root / "Data" / "P1C01SourceToRuntimeDispositionV1.json").read_text(encoding="utf-8"))
        rows = disposition["dispositions"]
        required = {
            "SHIRE_HOBBITON_WORLD",
            "BAG_END_WORLD",
            "F1_01_PARTY_SETUP",
            "F1_01_FIREWORKS",
            "F1_01_LOCKED_OUTCOME",
            "F1_02_RING_DANGER",
            "F1_03_FIELD_SHORTCUT",
            "F1_03_ROAD_HIDING",
            "F1_03_FERRY_ESCAPE",
            "SHIRE_LIVING_WORLD",
            "SHIRE_AUDIO_IDENTITY",
            "CHECKPOINT_AND_RETRY",
            "DIALOGUE_KNOWLEDGE_AND_CINEMATIC_SKIP",
            "SAFE_OPTIONAL_WINDOW_EXPIRY",
        }
        self.assertTrue(required.issubset({row["id"] for row in rows}))
        for row in rows:
            for field in ("id", "source", "source_requirement", "state", "next_car"):
                self.assertTrue(str(row.get(field, "")).strip(), (row.get("id"), field))
            self.assertIsInstance(row.get("current_runtime"), list)

    def test_save_schema_history_preserves_proven_and_unknown_boundaries(self):
        root = Path(__file__).resolve().parents[1]
        audit = json.loads((root / "Data" / "SaveSchemaMigrationAuditV1.json").read_text(encoding="utf-8"))
        self.assertEqual(
            audit["status"],
            "PARTIAL_HISTORY_RECOVERED_V3_TO_V6_V1_V2_UNDOCUMENTED_DO_NOT_INVENT",
        )
        self.assertEqual(
            [row["schema_version"] for row in audit["documented_transitions"]],
            [3, 4, 5, 6],
        )
        unknown = " ".join(audit["unknown_boundaries"])
        self.assertIn("schema versions 1 or 2", unknown)
        self.assertIn("retroactively labeled schema 1 or 2", unknown)

    def test_overnight_train_keeps_runtime_exact_head_gated(self):
        root = Path(__file__).resolve().parents[1]
        train = json.loads((root / "Data" / "P1C01OvernightMegaBuildTrainV1.json").read_text(encoding="utf-8"))
        cars = {row["id"]: row for row in train["cars"]}
        self.assertEqual(
            cars["W00_ACCEPTANCE_CLOSE"]["status"],
            "CLOSED_MACHINE_PROVEN_PR184_EXACT_HEAD",
        )
        self.assertEqual(
            train["preparation_progress"]["runtime_expansion"],
            "GATED_BY_RELEVANT_PER_CAR_EXACT_HEAD_UE4",
        )
        self.assertEqual(
            cars["SHIRE_WORLD_DENSITY_AND_ROUTE_LIFE"]["status"],
            "EXACT_HEAD_MACHINE_GREEN_PR192_PRE1467_UE1140_DEVELOP_PRE1468_UE1141",
        )
        self.assertEqual(
            cars["PARTY_AND_BAG_END_INTERACTION_DENSITY"]["status"],
            "PARTY_EXACT_HEAD_MACHINE_GREEN_PR194_PRE1472_UE1145_BAG_END_PR193_GREEN",
        )
        for car_id in (
            "NPC_ROUTINES_SOCIAL_MEMORY",
            "FAUNA_ENVIRONMENTAL_MOTION",
        ):
            self.assertEqual(
                cars[car_id]["status"],
                "SOURCE_IMPLEMENTED_LIVING_SHIRE_EXACT_HEAD_PROOF_PENDING",
            )
        self.assertEqual(
            cars["CHARACTER_PRESENTATION"]["status"],
            "EXACT_HEAD_MACHINE_GREEN_PR195_PRE1475_UE1148_MERGED_66CAF6",
        )
        self.assertEqual(
            cars["QUEST_SIDE_ACTIVITY_COHERENCE"]["status"],
            "EXACT_HEAD_MACHINE_GREEN_PR197_PRE1481_UE1154_MERGED_E92688",
        )
        self.assertEqual(
            cars["CINEMATIC_CONTROL_HANDOFF"]["status"],
            "EXACT_HEAD_MACHINE_GREEN_PR198_PRE1484_UE1157_MERGED_3B3869",
        )
        self.assertEqual(
            cars["SHIRE_AUDIO_IDENTITY"]["status"],
            "EXACT_HEAD_MACHINE_GREEN_PR199_PRE1486_UE1159_MERGED_EC96E9",
        )
        for car_id in (
            "SAVE_LOAD_LONG_SESSION",
            "TARGET_DEVICE_PROFILE_AND_GATE67",
        ):
            self.assertEqual(cars[car_id]["status"], "GATED")


    def test_p1c01_shire_world_density_is_bounded_and_instanced(self):
        root = Path(__file__).resolve().parents[1]
        contract = json.loads((root / "Data" / "P1C01ShireWorldDensityCarV1.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["status"], "EXACT_HEAD_MACHINE_GREEN_PR192_PRE1467_UE1140_DEVELOP_PRE1468_UE1141")
        self.assertEqual(contract["budget"]["ambient_population_target_p1c01"], 18)
        self.assertEqual(contract["budget"]["max_cluster_actors"], 5)
        self.assertEqual(contract["budget"]["max_detail_instances"], 70)
        self.assertEqual(
            sum(row["max_instances"] for row in contract["budget"]["categories"]),
            70,
        )

        life = json.loads((root / "Data" / "WorldLifeSaturationPlan.json").read_text(encoding="utf-8"))
        self.assertEqual(life["baseline_population_targets"]["P1C01"], 18)

        source = (root / "Source" / "ShireJourney" / "Private" / "World" / "ShirePrototypeWorldBuilder.cpp").read_text(encoding="utf-8")
        start = source.index("void AShirePrototypeWorldBuilder::SpawnWorldDensityDetailPass()")
        end = source.index("void AShirePrototypeWorldBuilder::SpawnScenicDetailPass()", start)
        body = source[start:end]
        self.assertEqual(body.count("SpawnDetailCluster("), 5)
        self.assertIn("Cluster->Configure(Mesh, false", body)
        self.assertIn("SHIRE_WORLD_DENSITY_DETAIL_PASS", body)
        self.assertIn("populationTarget=18", body)
        self.assertNotIn("LoadObject<", body)
        self.assertNotIn("StaticLoadObject", body)
        self.assertNotIn("SpawnActor<AShireAmbientNPC>", body)


    def test_p1c01_bag_end_hero_pass_is_bounded_and_state_driven(self):
        root = Path(__file__).resolve().parents[1]
        contract = json.loads((root / "Data" / "P1C01BagEndHeroChapterV1.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["status"], "EXACT_HEAD_MACHINE_GREEN_PR193_PRE1469_UE1142")
        self.assertEqual(contract["runtime_budget"]["max_hism_cluster_actors"], 3)
        self.assertEqual(contract["runtime_budget"]["max_hism_instances"], 36)
        self.assertEqual(contract["architecture"]["ambient_population_target_p1c01"], 18)
        self.assertEqual(
            contract["asset_policy"]["interior"],
            "CONTENT_PENDING_DEDICATED_FBX_KIT_AND_PROVENANCE",
        )

        source = (root / "Source" / "ShireJourney" / "Private" / "World" / "ShirePrototypeWorldBuilder.cpp").read_text(encoding="utf-8")
        start = source.index("void AShirePrototypeWorldBuilder::SpawnBagEndHeroPass()")
        end = source.index("void AShirePrototypeWorldBuilder::SpawnWorldDensityDetailPass()", start)
        body = source[start:end]
        self.assertEqual(body.count("SpawnDetailCluster("), 3)
        self.assertIn("BAG_END_HERO_PASS", body)
        self.assertIn("populationTarget=18", body)
        self.assertIn("Configure(Mesh, false", body)
        for forbidden in ("LoadObject<", "StaticLoadObject", "RequestSyncLoad", "SpawnActor<AShireAmbientNPC>"):
            self.assertNotIn(forbidden, body)

        state_start = source.index("void AShirePrototypeWorldBuilder::ApplyBagEndStoryVariant()")
        state_end = source.index("void AShirePrototypeWorldBuilder::ApplyStoryAtmosphere()", state_start)
        state_body = source[state_start:state_end]
        for token in ("ShireArrival", "LongExpectedParty", "RingSecret", "LeavingHome", "BAG_END_STORY_VARIANT"):
            self.assertIn(token, state_body)


    def test_p1c01_party_social_loop_is_bounded_and_windowed(self):
        root = Path(__file__).resolve().parents[1]
        contract = json.loads((root / "Data" / "P1C01PartySocialLoopChapterV1.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["status"], "SOURCE_IMPLEMENTED_EXACT_HEAD_PROOF_PENDING")
        self.assertEqual(contract["runtime_budget"]["max_hism_cluster_actors"], 4)
        self.assertEqual(contract["runtime_budget"]["max_hism_instances"], 56)
        self.assertEqual(contract["runtime_budget"]["max_state_variant_props"], 8)
        self.assertEqual(contract["architecture"]["ambient_population_target_p1c01"], 18)

        source = (root / "Source" / "ShireJourney" / "Private" / "World" / "ShirePrototypeWorldBuilder.cpp").read_text(encoding="utf-8")
        start = source.index("void AShirePrototypeWorldBuilder::SpawnPartySocialLoopPass()")
        end = source.index("void AShirePrototypeWorldBuilder::SpawnSideStories()", start)
        body = source[start:end]
        self.assertEqual(body.count("SpawnPartyCluster("), 4)
        self.assertIn("PARTY_SOCIAL_LOOP_PASS", body)
        self.assertIn("populationTarget=18", body)
        for forbidden in ("LoadObject<", "StaticLoadObject", "RequestSyncLoad", "SpawnActor<AShireAmbientNPC>"):
            self.assertNotIn(forbidden, body)

        plan = json.loads((root / "Data" / "ContextualSideActivityPlan.json").read_text(encoding="utf-8"))
        p1 = next(row for row in plan["chapters"] if row["route"] == "FrodoMain" and row["chapter"] == "P1C01")
        by_id = {row["id"]: row for row in p1["activities"]}
        for activity_id, reward_id in (
            ("SIDE_SHIRE_FIREWORKS_SAFETY", "SHIRE_FIREWORKS_SAFETY"),
            ("SIDE_SHIRE_DRAGON_FIREWORK_MISHAP", "SHIRE_DRAGON_FIREWORK_MISHAP"),
        ):
            row = by_id[activity_id]
            self.assertEqual(row["available_after"], "PartyArrival")
            self.assertEqual(row["ends_before"], "BilboDisappearance")
            self.assertEqual(row["discovery_reward_id"], reward_id)
            self.assertFalse(row["may_advance_required_anchor"])
            self.assertFalse(row["may_change_canon_outcome"])
            self.assertFalse(row["future_knowledge_allowed"])


    def test_p1c01_character_presentation_is_explicit_and_async(self):
        root = Path(__file__).resolve().parents[1]
        contract = json.loads((root / "Data" / "P1C01CharacterPresentationChapterV1.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["status"], "SOURCE_IMPLEMENTED_EXACT_HEAD_PROOF_PENDING")
        self.assertFalse(contract["runtime_contract"]["frodo_future_weapon_in_p1c01"])
        self.assertTrue(contract["runtime_contract"]["named_story_npcs_use_explicit_character_ids"])
        self.assertFalse(contract["runtime_contract"]["synchronous_heavy_load"])
        self.assertFalse(contract["runtime_contract"]["per_frame_asset_scan"])

        npc_h = (root / "Source" / "ShireJourney" / "Public" / "Characters" / "ShireNPC.h").read_text(encoding="utf-8")
        npc_cpp = (root / "Source" / "ShireJourney" / "Private" / "Characters" / "ShireNPC.cpp").read_text(encoding="utf-8")
        player = (root / "Source" / "ShireJourney" / "Private" / "Characters" / "ShirePlayerCharacter.cpp").read_text(encoding="utf-8")
        streaming = (root / "Source" / "ShireJourney" / "Private" / "Subsystems" / "ShireChapterAssetStreamingSubsystem.cpp").read_text(encoding="utf-8")
        world = (root / "Source" / "ShireJourney" / "Private" / "World" / "ShirePrototypeWorldBuilder.cpp").read_text(encoding="utf-8")

        self.assertIn("ProductionCharacterId", npc_h)
        self.assertIn("ResolveProductionCharacterId", npc_cpp)
        for token in (
            'GandalfRoad->ProductionCharacterId=TEXT("Gandalf")',
            'Bilbo->ProductionCharacterId=TEXT("Bilbo")',
            'GandalfBagEnd->ProductionCharacterId=TEXT("Gandalf")',
            'Sam->ProductionCharacterId=TEXT("Sam")',
        ):
            self.assertIn(token, world)

        self.assertIn("ShouldShowPrototypeWeaponForCurrentStory", player)
        self.assertIn('GetCurrentChapterId() == TEXT("P1C01")', player)
        self.assertIn("P1C01_CHARACTER_PRESENTATION", player)

        start = streaming.index("void UShireChapterAssetStreamingSubsystem::RequestCharacterRig")
        end = streaming.index("void UShireChapterAssetStreamingSubsystem::HandleCharacterRigLoadComplete", start)
        body = streaming[start:end]
        self.assertIn("RequestAsyncLoad", body)
        for forbidden in ("LoadObject<", "StaticLoadObject", "RequestSyncLoad"):
            self.assertNotIn(forbidden, body)
        self.assertIn("bEnableUpdateRateOptimizations = true", player)
        self.assertIn("OnlyTickPoseWhenRendered", player)
        self.assertIn("bEnableUpdateRateOptimizations = true", npc_cpp)
        self.assertIn("OnlyTickPoseWhenRendered", npc_cpp)

        hero_rig = json.loads((root / "Data" / "P1C01HeroSkeletalCandidateWaveV1.json").read_text(encoding="utf-8"))
        rig_prep = json.loads((root / "Data" / "P1C01CharacterRigAnimationPrepV1.json").read_text(encoding="utf-8"))
        self.assertEqual(
            hero_rig["candidate_policy"]["fbx_pipeline_compatibility"],
            "UE4.27 FBX 2018-compatible export required",
        )
        self.assertEqual(
            hero_rig["target_profile"]["quality"],
            "Balanced Medium / selective High where visually important",
        )
        self.assertEqual(
            rig_prep["required_bundle"]["fbx_pipeline_compatibility"],
            "UE4.27 FBX 2018-compatible export required",
        )
        self.assertEqual(rig_prep["project_owned_fallback"]["state"], "STATIC_MODULAR_FALLBACK_ONLY")


    def test_p1c01_living_shire_is_bounded_and_director_owned(self):
        root = Path(__file__).resolve().parents[1]
        contract = json.loads((root / "Data" / "P1C01LivingShireChapterV1.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["status"], "SOURCE_IMPLEMENTED_EXACT_HEAD_PROOF_PENDING")
        self.assertEqual(contract["runtime_budget"]["p1c01_ambient_population_target"], 18)
        self.assertEqual(contract["runtime_budget"]["max_active_fauna_groups_near_player"], 2)
        self.assertFalse(contract["runtime_budget"]["full_world_social_actor_scan"])
        self.assertTrue(contract["runtime_contract"]["bounded_context_snapshot"])
        self.assertTrue(contract["runtime_contract"]["social_pairing_uses_managed_active_query"])
        self.assertTrue(contract["runtime_contract"]["fauna_group_cap_enforced"])
        self.assertFalse(contract["runtime_contract"]["synchronous_heavy_load"])
        self.assertFalse(contract["runtime_contract"]["per_frame_context_reconstruction"])

        ambient = (root / "Source" / "ShireJourney" / "Private" / "Characters" / "ShireAmbientNPC.cpp").read_text(encoding="utf-8")
        social_start = ambient.index("void AShireAmbientNPC::UpdateSocialLife")
        social_end = ambient.index("void AShireAmbientNPC::Tick", social_start)
        social = ambient[social_start:social_end]
        self.assertIn("GatherActiveAmbientNPCsNear", social)
        self.assertNotIn("TActorIterator<AShireAmbientNPC>", social)

        schedule_start = ambient.index("void AShireAmbientNPC::UpdateScheduleContext")
        schedule_end = ambient.index("void AShireAmbientNPC::UpdateNeedsAndEmotion", schedule_start)
        self.assertIn("BuildBehaviorSnapshot", ambient[schedule_start:schedule_end])

        director = (root / "Source" / "ShireJourney" / "Private" / "World" / "LivingWorldDirector.cpp").read_text(encoding="utf-8")
        self.assertIn("GatherActiveAmbientNPCsNear", director)
        self.assertIn("ReconcilePersistentAmbientNPCRegistry", director)
        self.assertIn("PersistentAmbientNPCs", director)
        self.assertIn("TActorIterator<AShireAmbientNPC>", director)
        self.assertIn('ActorHasTag(TEXT("LivingWorldManaged"))', director)
        self.assertIn('RoutineRole == TEXT("Bird")', director)
        self.assertIn('max_active_fauna_groups_near_player', director)
        self.assertIn("MaxActiveFaunaGroups", director)

        self.assertTrue(contract["runtime_contract"]["persistent_builder_residents_registered_for_social_query"])
        self.assertFalse(contract["runtime_contract"]["persistent_registration_transfers_lifecycle_ownership"])
        self.assertFalse(contract["runtime_contract"]["per_tick_full_world_registration_scan"])

        context_h = (root / "Source" / "ShireJourney" / "Public" / "Subsystems" / "ShireNPCContextSubsystem.h").read_text(encoding="utf-8")
        context_cpp = (root / "Source" / "ShireJourney" / "Private" / "Subsystems" / "ShireNPCContextSubsystem.cpp").read_text(encoding="utf-8")
        self.assertIn("FShireNPCBehaviorSnapshot", context_h)
        self.assertIn("BuildBehaviorSnapshot", context_h)
        self.assertIn("BuildBehaviorSnapshot", context_cpp)

        life = json.loads((root / "Data" / "WorldLifeSaturationPlan.json").read_text(encoding="utf-8"))
        self.assertEqual(life["baseline_population_targets"]["P1C01"], 18)



    def test_p1c01_quest_side_activity_coherence_is_quest_owned_and_windowed(self):
        root = Path(__file__).resolve().parents[1]
        contract = json.loads((root / "Data" / "P1C01QuestSideActivityCoherenceV1.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["status"], "SOURCE_IMPLEMENTED_EXACT_HEAD_PROOF_PENDING")
        coherence = contract["coherence_contract"]
        self.assertTrue(coherence["main_quest_priority"])
        self.assertTrue(coherence["clean_expiry_on_closing_story_beat"])
        self.assertTrue(coherence["idempotent_completion"])
        self.assertEqual(
            set(coherence["p1c01_urgency_suppression"]),
            {"RingSecret", "LeavingHome", "KeepOffRoad", "FerryEscape"},
        )

        header = (root / "Source" / "ShireJourney" / "Public" / "Subsystems" / "ShireQuestSubsystem.h").read_text(encoding="utf-8")
        source = (root / "Source" / "ShireJourney" / "Private" / "Subsystems" / "ShireQuestSubsystem.cpp").read_text(encoding="utf-8")
        self.assertIn("GetAvailableSideActivityIdsForCurrentWindow", header)
        self.assertIn("IsMainQuestUrgencySuppressingSideActivities", header)
        self.assertIn("GetAvailableSideActivityIdsForCurrentWindow", source)
        self.assertIn("JourneyDiscoveryIds.Contains(DiscoveryId)", source)
        for quest_id in ("RingSecret", "LeavingHome", "KeepOffRoad", "FerryEscape"):
            self.assertIn(f'ActiveQuestId == TEXT("{quest_id}")', source)



    def test_p1c01_cinematic_control_handoff_converges_on_one_exit_path(self):
        root = Path(__file__).resolve().parents[1]
        contract = json.loads((root / "Data" / "P1C01CinematicControlHandoffV1.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["status"], "SOURCE_IMPLEMENTED_EXACT_HEAD_PROOF_PENDING")
        runtime = contract["runtime_contract"]
        self.assertTrue(runtime["skip_release_uses_same_exit_path"])
        self.assertTrue(runtime["camera_release_on_cinematic_unlock"])
        self.assertTrue(runtime["chapter_change_forces_release"])
        self.assertFalse(runtime["quest_route_save_state_mutation_from_presentation"])
        self.assertFalse(runtime["stale_runtime_camera_after_skip"])

        presentation_h = (root / "Source" / "ShireJourney" / "Public" / "Subsystems" / "ShireStoryPresentationSubsystem.h").read_text(encoding="utf-8")
        presentation_cpp = (root / "Source" / "ShireJourney" / "Private" / "Subsystems" / "ShireStoryPresentationSubsystem.cpp").read_text(encoding="utf-8")
        director_cpp = (root / "Source" / "ShireJourney" / "Private" / "World" / "StoryPresentationDirector.cpp").read_text(encoding="utf-8")

        self.assertIn("RequestSkipActivePresentation", presentation_h)
        skip_start = presentation_cpp.index("void UShireStoryPresentationSubsystem::RequestSkipActivePresentation")
        release_start = presentation_cpp.index("void UShireStoryPresentationSubsystem::ReleaseCinematicLock", skip_start)
        skip_body = presentation_cpp[skip_start:release_start]
        self.assertIn("ReleaseCinematicLock();", skip_body)
        for forbidden in ("SetQuestStage(", "AdvanceQuest(", "StartChapter(", "StartExperience(", "TriggerStoryBeat("):
            self.assertNotIn(forbidden, skip_body)

        self.assertIn("OnCinematicStateChanged.AddDynamic", director_cpp)
        self.assertIn("OnCinematicStateChanged.RemoveDynamic", director_cpp)
        self.assertIn("HandleCinematicStateChanged", director_cpp)
        self.assertIn("Presentation->ReleaseCinematicLock();", director_cpp)



    def test_p1c01_shire_audio_identity_is_async_and_bounded(self):
        root = Path(__file__).resolve().parents[1]
        contract = json.loads((root / "Data" / "P1C01ShireAudioIdentityV1.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["status"], "SOURCE_IMPLEMENTED_EXACT_HEAD_PROOF_PENDING")
        self.assertEqual(
            contract["source_identity"],
            ["birds", "breeze in hedges", "farm work", "distant laughter", "carts", "warm interiors", "fire/cutlery"],
        )
        self.assertEqual(contract["low_spec_budget"]["max_decorative_spatial_sfx_starts_per_window"], 6)
        self.assertEqual(contract["low_spec_budget"]["decorative_spatial_sfx_window_seconds"], 0.25)
        self.assertTrue(contract["runtime_contract"]["decorative_spatial_sfx_burst_bounded"])
        self.assertTrue(contract["runtime_contract"]["story_critical_sfx_not_blocked_by_decorative_burst"])

        header = (root / "Source" / "ShireJourney" / "Public" / "Subsystems" / "ShireAudioSubsystem.h").read_text(encoding="utf-8")
        source = (root / "Source" / "ShireJourney" / "Private" / "Subsystems" / "ShireAudioSubsystem.cpp").read_text(encoding="utf-8")
        self.assertIn("RecentDecorativeSfxStartTimes", header)
        self.assertIn("DecorativeSfxWindowSeconds = 0.25f", header)
        self.assertIn("MaxDecorativeSfxStartsPerWindow = 6", header)
        self.assertIn("RequestAsyncLoad", source)
        self.assertIn("CanPlaySfxNow(CueId, true)", source)
        self.assertIn("CanPlaySfxNow(CueId, false)", source)
        self.assertIn("RecentDecorativeSfxStartTimes.RemoveAll", source)
        for forbidden in ("LoadObject<", "StaticLoadObject", "RequestSyncLoad"):
            self.assertNotIn(forbidden, source)

        footstep = (root / "Source" / "ShireJourney" / "Private" / "Characters" / "ShireFootstepComponent.cpp").read_text(encoding="utf-8")
        engine_ini = (root / "Config" / "DefaultEngine.ini").read_text(encoding="utf-8")
        self.assertEqual(
            contract["runtime_contract"]["footstep_surface_types"],
            ["Grass", "Dirt", "Stone", "Wood"],
        )
        self.assertIn("UPhysicalMaterial::DetermineSurfaceType", footstep)
        for surface_type, cue in (
            ("SurfaceType1", "GrassCue"),
            ("SurfaceType2", "DirtCue"),
            ("SurfaceType3", "StoneCue"),
            ("SurfaceType4", "WoodCue"),
        ):
            self.assertIn(f"case {surface_type}:", footstep)
            self.assertIn(f"return ShireFootstep::{cue};", footstep)
        for index, name in enumerate(("Grass", "Dirt", "Stone", "Wood"), start=1):
            self.assertIn(f'PhysicalSurfaces=(Type=SurfaceType{index},Name="{name}")', engine_ini)



    def test_p1c01_save_load_long_session_is_bounded_before_restore_mutation(self):
        root = Path(__file__).resolve().parents[1]
        contract = json.loads((root / "Data" / "P1C01SaveLoadLongSessionV1.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["status"], "SOURCE_IMPLEMENTED_EXACT_HEAD_PROOF_PENDING")
        self.assertTrue(contract["runtime_contract"]["save_payload_bounds_checked_before_restore_mutation"])
        self.assertTrue(contract["runtime_contract"]["world_revision_guards_async_checkpoint_effects"])
        self.assertTrue(contract["runtime_contract"]["queued_checkpoint_preserves_captured_snapshot"])
        self.assertEqual(contract["restore_bounds"]["max_route_progress_entries"], 16)
        self.assertEqual(contract["restore_bounds"]["max_chronicle_entries"], 1024)

        header = (root / "Source" / "ShireJourney" / "Public" / "Characters" / "ShirePlayerCharacter.h").read_text(encoding="utf-8")
        source = (root / "Source" / "ShireJourney" / "Private" / "Characters" / "ShirePlayerCharacter.cpp").read_text(encoding="utf-8")
        save_h = (root / "Source" / "ShireJourney" / "Public" / "SaveGame" / "ShireSaveGame.h").read_text(encoding="utf-8")
        self.assertIn("ValidateSaveSnapshotBounds", header)
        restore_start = source.index("bool AShirePlayerCharacter::RestoreSaveSnapshot")
        begin_restore = source.index("BeginPersistenceRestore", restore_start)
        self.assertIn("ValidateSaveSnapshotBounds(Save)", source[restore_start:begin_restore])
        for token in (
            'TEXT("QuestStages"), Save->QuestStages.Num(), 128',
            'TEXT("CompletedStoryBeats"), Save->CompletedStoryBeats.Num(), 512',
            'TEXT("RouteProgress"), Save->RouteProgress.Num(), 16',
            'TEXT("NPCMemoryState"), Save->NPCMemoryState.Num(), 128',
            'TEXT("ChronicleEntryIds"), Save->ChronicleEntryIds.Num(), 1024',
        ):
            self.assertIn(token, source)
        self.assertIn("CurrentSchemaVersion = 6", save_h)


    def test_p1c01_gate67_acceptance_tooling_is_fail_closed(self):
        root = Path(__file__).resolve().parents[1]
        contract = json.loads((root / "Data" / "P1C01TargetDeviceGate67V1.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["status"], "STATIC_ACCEPTANCE_PREP_IMPLEMENTED_PREDECESSOR_MERGED")
        self.assertEqual(contract["target_profile"]["renderer"], "DX11")
        self.assertEqual(contract["target_profile"]["resolution_width"], 1280)
        self.assertEqual(contract["target_profile"]["resolution_height"], 720)
        self.assertEqual(contract["target_profile"]["quality"], "Balanced Medium / selective High where visually important")
        self.assertEqual(contract["target_profile"]["fps_floor"], 30)
        self.assertFalse(any(contract["current_claims"].values()))

        evaluator = (root / "Scripts" / "evaluate_p1c01_gate67_evidence.py").read_text(encoding="utf-8")
        self.assertIn('"status":"INCOMPLETE"', evaluator)
        self.assertIn('"status":"GATE67_NOT_ACCEPTED"', evaluator)
        self.assertIn('route below 30 FPS floor', evaluator)
        self.assertIn('blocking streaming hitch', evaluator)
        self.assertIn('synchronous heavy load observed', evaluator)
        self.assertIn('save/load continuity not proven', evaluator)
        self.assertIn('return-to-control continuity not proven', evaluator)
        self.assertIn('"DEVICE_TESTED":True', evaluator)
        self.assertIn('"PERFORMANCE_ACCEPTED":True', evaluator)


    def test_p1c01_authored_shire_wave_bc_is_bounded_and_single_writer(self):
        root = Path(__file__).resolve().parents[1]
        contract = json.loads((root / "Data" / "P1C01AuthoredShireMegaWaveBCV1.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["runtime_chapter"], "P1C01")
        self.assertEqual(contract["runtime_writer"], "AShirePrototypeWorldBuilder")
        self.assertFalse(contract["p1c02_runtime_opened"])
        self.assertEqual(contract["authored_landform_budget"]["total_instances"], 52)
        self.assertEqual(contract["presentation_composition_budget"]["total_instances"], 120)
        self.assertEqual(contract["implementation_contract"]["repeated_detail"], "HISM_ONLY")
        self.assertFalse(contract["implementation_contract"]["per_instance_tick"])
        self.assertFalse(contract["implementation_contract"]["repeated_collision"])
        self.assertFalse(contract["implementation_contract"]["synchronous_heavy_load"])
        self.assertTrue(contract["implementation_contract"]["resident_production_meshes_only"])
        self.assertTrue(contract["implementation_contract"]["production_materials_preserved"])
        self.assertFalse(contract["implementation_contract"]["volumetric_fog"])
        self.assertFalse(contract["implementation_contract"]["planar_reflection"])
        self.assertFalse(contract["implementation_contract"]["scene_capture_water"])

        source = (root / "Source" / "ShireJourney" / "Private" / "World" / "ShirePrototypeWorldBuilder.cpp").read_text(encoding="utf-8")
        header = (root / "Source" / "ShireJourney" / "Public" / "World" / "ShirePrototypeWorldBuilder.h").read_text(encoding="utf-8")
        self.assertIn("void SpawnAuthoredShireLandmarkPass();", header)
        self.assertIn("void SpawnPresentationCompositionPass();", header)

        landmark_start = source.index("void AShirePrototypeWorldBuilder::SpawnAuthoredShireLandmarkPass()")
        landmark_end = source.index("void AShirePrototypeWorldBuilder::SpawnPresentationCompositionPass()", landmark_start)
        landmark = source[landmark_start:landmark_end]
        presentation_start = landmark_end
        presentation_end = source.index("void AShirePrototypeWorldBuilder::SpawnWorldDensityDetailPass()", presentation_start)
        presentation = source[presentation_start:presentation_end]

        for token in (
            "P1C01_AUTHORED_SHIRE_LANDMARK_PASS",
            "BagEndTerrain[]",
            "VillageTerraces[]",
            "FieldRidges[]",
            "WoodlandShoulders[]",
            "FerryBanks[]",
        ):
            self.assertIn(token, landmark)
        for token in (
            "P1C01_PRESENTATION_COMPOSITION_PASS",
            "ForegroundShrubCount",
            "WoodlandThresholdTreeCount",
            "UnderstoryFernCount",
            "FerryReedAccentCount",
        ):
            self.assertIn(token, presentation)

        for body in (landmark, presentation):
            for forbidden in (
                "LoadObject<",
                "StaticLoadObject",
                "RequestSyncLoad",
                "SpawnActor<AShireAmbientNPC>",
                "SpawnActor<ALivingWorldDirector>",
                'TEXT("P1C02")',
            ):
                self.assertNotIn(forbidden, body)

        build_start = source.index("void AShirePrototypeWorldBuilder::BuildPrototypeWorld()")
        build = source[build_start:]
        order = [
            build.index("SpawnGeographyFoundationPass();"),
            build.index("SpawnAuthoredShireLandmarkPass();"),
            build.index("SpawnHobbitonArchitecturePass();"),
            build.index("SpawnNaturalRouteMegaPass();"),
            build.index("SpawnPresentationCompositionPass();"),
            build.index("SpawnWorldDensityDetailPass();"),
        ]
        self.assertEqual(order, sorted(order))

    def test_p1c01_visible_shire_mega_wave_d_is_bounded_and_single_writer(self):
        root = Path(__file__).resolve().parents[1]
        contract = json.loads((root / "Data" / "P1C01VisibleShireMegaWaveDV1.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["runtime_chapter"], "P1C01")
        self.assertEqual(contract["runtime_writer"], "AShirePrototypeWorldBuilder")
        self.assertEqual(contract["visible_budget"]["total_hism"], 268)
        self.assertEqual(contract["visible_budget"]["total_limited_hero_actors"], 12)
        self.assertFalse(contract["architecture_contract"]["new_world_authority"])
        self.assertFalse(contract["architecture_contract"]["per_instance_tick"])
        self.assertFalse(contract["architecture_contract"]["synchronous_heavy_load"])
        self.assertFalse(contract["architecture_contract"]["actor_per_prop_density"])
        self.assertFalse(contract["architecture_contract"]["p1c02_runtime_opened"])

        source = (root / "Source" / "ShireJourney" / "Private" / "World" / "ShirePrototypeWorldBuilder.cpp").read_text(encoding="utf-8")
        header = (root / "Source" / "ShireJourney" / "Public" / "World" / "ShirePrototypeWorldBuilder.h").read_text(encoding="utf-8")
        self.assertIn("void SpawnVisibleShireMegaWaveD();", header)

        start = source.index("void AShirePrototypeWorldBuilder::SpawnVisibleShireMegaWaveD()")
        end = source.index("void AShirePrototypeWorldBuilder::SpawnWorldDensityDetailPass()", start)
        body = source[start:end]
        for token in (
            "P1C01_VISIBLE_SHIRE_MEGA_WAVE_D",
            "BagEndEarth[]",
            "HobbitonTerraces[]",
            "FerryBanks[]",
            "ProductionCommonFootbridgeMesh",
            "ProductionCommonRiverBoatMesh",
            "ProductionCommonRopePostMesh",
            "ProductionLampPostMesh",
        ):
            self.assertIn(token, body)

        for forbidden in (
            "LoadObject<",
            "StaticLoadObject",
            "RequestSyncLoad",
            "SpawnActor<ALivingWorldDirector>",
            "SpawnActor<AShireAmbientNPC>",
            'TEXT("P1C02")',
        ):
            self.assertNotIn(forbidden, body)

        build = source[source.index("void AShirePrototypeWorldBuilder::BuildPrototypeWorld()"):]
        self.assertLess(build.index("SpawnPresentationCompositionPass();"), build.index("SpawnVisibleShireMegaWaveD();"))
        self.assertLess(build.index("SpawnVisibleShireMegaWaveD();"), build.index("SpawnWorldDensityDetailPass();"))

        scenic_start = source.index("void AShirePrototypeWorldBuilder::SpawnScenicDetailPass()")
        scenic = source[scenic_start:source.index("void AShirePrototypeWorldBuilder::BuildPrototypeWorld()", scenic_start)]
        self.assertIn("Deterministic multi-frequency offsets break the old evenly-spaced", scenic)
        self.assertIn("Index) * 1.17f", scenic)


    def test_p1c01_shire_visual_finish_wave_is_bounded_and_single_writer(self):
        root = Path(__file__).resolve().parents[1]
        contract = json.loads((root / "Data" / "P1C01ShireVisualFinishWaveV1.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["runtime_chapter"], "P1C01")
        self.assertEqual(contract["runtime_writer"], "AShirePrototypeWorldBuilder")
        self.assertEqual(contract["visible_budget"]["total_hism"], 212)
        self.assertEqual(contract["visible_budget"]["total_limited_hero_actors"], 4)
        self.assertFalse(contract["architecture_contract"]["new_world_authority"])
        self.assertFalse(contract["architecture_contract"]["per_instance_tick"])
        self.assertFalse(contract["architecture_contract"]["synchronous_heavy_load"])
        self.assertFalse(contract["architecture_contract"]["actor_per_prop_density"])
        self.assertFalse(contract["architecture_contract"]["p1c02_runtime_opened"])

        source = (root / "Source" / "ShireJourney" / "Private" / "World" / "ShirePrototypeWorldBuilder.cpp").read_text(encoding="utf-8")
        header = (root / "Source" / "ShireJourney" / "Public" / "World" / "ShirePrototypeWorldBuilder.h").read_text(encoding="utf-8")
        self.assertIn("void SpawnShireVisualFinishWave();", header)

        start = source.index("void AShirePrototypeWorldBuilder::SpawnShireVisualFinishWave()")
        end = source.index("void AShirePrototypeWorldBuilder::SpawnWorldDensityDetailPass()", start)
        body = source[start:end]
        for token in (
            "P1C01_SHIRE_VISUAL_FINISH_WAVE",
            "TerrainRidges[]",
            "BagEndHedges[]",
            "HobbitonHedges[]",
            "FerryBanks[]",
            "GeographySlopeInstances",
            "WoodlandTreeInstances",
            "GeographyRiverBankInstances",
            "hismBudget=212",
        ):
            self.assertIn(token, body)

        for forbidden in (
            "LoadObject<",
            "StaticLoadObject",
            "RequestSyncLoad",
            "SpawnActor<ALivingWorldDirector>",
            "SpawnActor<AShireAmbientNPC>",
            'TEXT("P1C02")',
        ):
            self.assertNotIn(forbidden, body)

        build = source[source.index("void AShirePrototypeWorldBuilder::BuildPrototypeWorld()"):]
        self.assertLess(build.index("SpawnVisibleShireMegaWaveD();"), build.index("SpawnShireVisualFinishWave();"))
        self.assertLess(build.index("SpawnShireVisualFinishWave();"), build.index("SpawnWorldDensityDetailPass();"))



    def test_p1c01_shire_settlement_completion_is_bounded_and_single_writer(self):
        root = Path(__file__).resolve().parents[1]
        contract = json.loads((root / "Data" / "P1C01ShireSettlementCompletionV1.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["runtime_chapter"], "P1C01")
        self.assertEqual(contract["runtime_writer"], "AShirePrototypeWorldBuilder")
        self.assertEqual(contract["budget"]["hism_instances"], 303)
        self.assertEqual(contract["budget"]["cluster_instances"], 82)
        self.assertEqual(contract["budget"]["cluster_actors_max"], 8)
        self.assertEqual(contract["budget"]["limited_hero_actors"], 16)
        self.assertFalse(contract["architecture_contract"]["new_world_authority"])
        self.assertFalse(contract["architecture_contract"]["per_instance_tick"])
        self.assertFalse(contract["architecture_contract"]["synchronous_heavy_load"])
        self.assertFalse(contract["architecture_contract"]["actor_per_prop_density"])
        self.assertFalse(contract["architecture_contract"]["p1c02_runtime_opened"])
        self.assertTrue(contract["architecture_contract"]["central_traversal_corridor_preserved"])

        source = (root / "Source" / "ShireJourney" / "Private" / "World" / "ShirePrototypeWorldBuilder.cpp").read_text(encoding="utf-8")
        header = (root / "Source" / "ShireJourney" / "Public" / "World" / "ShirePrototypeWorldBuilder.h").read_text(encoding="utf-8")
        self.assertIn("void SpawnShireSettlementCompletionPass();", header)
        self.assertIn("if (Index >= 6 && Index <= 8)", source)

        start = source.index("void AShirePrototypeWorldBuilder::SpawnShireSettlementCompletionPass()")
        end = source.index("void AShirePrototypeWorldBuilder::SpawnWorldDensityDetailPass()", start)
        body = source[start:end]
        self.assertEqual(body.count('TEXT("P1C01PartyFieldEntryGate")'), 2)
        self.assertNotIn('18.0f,\n        true,\n        TEXT("P1C01PartyFieldEntryGate")', body)

        for token in (
            "P1C01_SHIRE_SETTLEMENT_COMPLETION",
            "BagshotFacades[]",
            "P1C01PartyFieldEntryGate",
            "P1C01BywaterFacingCottage",
            "P1C01SettlementBenches",
            "P1C01SettlementBarrels",
            "P1C01SettlementCrates",
            "P1C01SettlementHaystacks",
            "P1C01PartyFieldTables",
            "P1C01SettlementLampPosts",
            "P1C01SettlementLoadedCarts",
            "P1C01SettlementFlowerBoxes",
            "hismBudget=303",
            "clusterBudget=82",
            "heroBudget=16",
        ):
            self.assertIn(token, body)

        for forbidden in (
            "LoadObject<",
            "StaticLoadObject",
            "RequestSyncLoad",
            "SpawnActor<ALivingWorldDirector>",
            "SpawnActor<AShireAmbientNPC>",
            'TEXT("P1C02")',
        ):
            self.assertNotIn(forbidden, body)

        build = source[source.index("void AShirePrototypeWorldBuilder::BuildPrototypeWorld()"):]
        self.assertLess(build.index("SpawnShireVisualFinishWave();"), build.index("SpawnShireSettlementCompletionPass();"))
        self.assertLess(build.index("SpawnShireSettlementCompletionPass();"), build.index("SpawnWorldDensityDetailPass();"))

    def test_p1c01_kaykit_rig_bridge_is_bounded_and_non_runtime(self):
        root = Path(__file__).resolve().parents[1]
        packet = json.loads((root / "Data" / "P1C01KayKitRigTechnicalBridgeV1.json").read_text(encoding="utf-8"))
        self.assertEqual(packet["runtime_chapter"], "P1C01")
        self.assertEqual(packet["role"], "TECHNICAL_RIG_DEFORMATION_BRIDGE_NOT_FINAL_LIKENESS")
        self.assertEqual(packet["source"]["provider"], "KAYKIT")
        self.assertEqual(packet["source"]["license"], "CC0-1.0")
        self.assertEqual(packet["source"]["required_final_format"], "FBX")
        self.assertEqual(packet["source"]["delivery_mode"], "DIRECT_OFFICIAL_RAW_FBX")
        self.assertTrue(packet["source"]["license_url"].startswith("https://raw.githubusercontent.com/KayKit-Game-Assets/"))
        self.assertEqual(len(packet["source"]["direct_candidates"]), 2)
        for candidate in packet["source"]["direct_candidates"]:
            self.assertTrue(candidate["filename"].lower().endswith(".fbx"))
            self.assertTrue(candidate["url"].startswith("https://raw.githubusercontent.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0/"))
        self.assertEqual(packet["candidate_policy"]["maximum_ue4_candidates"], 2)
        self.assertFalse(packet["candidate_policy"]["final_likeness"])
        self.assertTrue(packet["runtime_contract"]["modular_frodo_fallback"])
        self.assertFalse(packet["runtime_contract"]["synchronous_heavy_load"])

        stage = (root / "Scripts" / "stage_p1c01_kaykit_rig_bridge.ps1").read_text(encoding="utf-8")
        probe = (root / "Scripts" / "run_p1c01_kaykit_rig_bridge_ue4.ps1").read_text(encoding="utf-8")
        workflow = (root / ".github" / "workflows" / "p1c01-kaykit-rig-bridge.yml").read_text(encoding="utf-8")

        for token in (
            "KAYKIT_RIG_UNAPPROVED_RAW_SOURCE",
            "KAYKIT_RIG_NON_FBX_CANDIDATE",
            "KAYKIT_RIG_PAYLOAD_SIZE_FAIL",
            "KAYKIT_RIG_LICENSE_MARKER_MISSING",
            "Get-FileHash",
            "LimbNode",
            "Cluster",
            "Select-Object -First",
        ):
            self.assertIn(token, stage)
        for token in (
            "SKELETAL_REGISTRATION_FAILED",
            "ZERO_REFERENCE_BONES",
            "MISSING_SMOOTHING_GROUPS",
            "MISSING_BIND_POSE_BONES",
            "INVALID_BIND_POSE",
            "MISSING_UV_SET",
            "runtime_integration_allowed=$false",
        ):
            self.assertIn(token, probe)
        for forbidden in ("LoadObject<", "StaticLoadObject", "RequestSyncLoad", "RequestAsyncLoad"):
            self.assertNotIn(forbidden, stage)
            self.assertNotIn(forbidden, probe)

        self.assertIn("Hosted KayKit source and FBX static gate", workflow)
        self.assertIn("UE4.27.2 KayKit skeletal technical gate", workflow)
        self.assertIn("needs: hosted_static_bridge", workflow)
        self.assertIn("ci_build_unreal.cmd", workflow)
        self.assertIn("actions/upload-artifact@v4", workflow)

    def test_p1c01_kaykit_known_rejections_do_not_requeue_self_hosted_runner(self):
        root = Path(__file__).resolve().parents[1]
        manifest = json.loads((root / "Data" / "P1C01KayKitRigTechnicalBridgeV1.json").read_text(encoding="utf-8"))
        known = {row["sha256"]: row for row in manifest["known_technical_rejections"]}
        self.assertEqual(set(known.keys()), {
            "93a9ee0a67ae69b2d815050234acad2004c3b8af7d294b916e52609c8195eb71",
            "4a773f074695c6c089cc6f059eed85da080928a4a4137af4e38b177139d4cc27",
        })
        for row in known.values():
            self.assertEqual(row["ue4_reference_bones"], 48)
            self.assertEqual(set(row["reasons"]), {"MISSING_BIND_POSE_BONES", "MISSING_SMOOTHING_GROUPS"})
            self.assertEqual(row["disposition"], "REJECTED_TECHNICAL_DO_NOT_REQUEUE")

        stage = (root / "Scripts" / "stage_p1c01_kaykit_rig_bridge.ps1").read_text(encoding="utf-8")
        self.assertIn("STATIC_BRIDGE_EXHAUSTED_KNOWN_REJECTIONS", stage)
        self.assertIn("$knownRejected.ContainsKey($sha)", stage)

        workflow = (root / ".github" / "workflows" / "p1c01-kaykit-rig-bridge.yml").read_text(encoding="utf-8")
        self.assertIn("selected_count: ${{ steps.outcome.outputs.selected_count }}", workflow)
        self.assertIn("if: needs.hosted_static_bridge.outputs.selected_count != '0'", workflow)

        ue4 = (root / "Scripts" / "run_p1c01_kaykit_rig_bridge_ue4.ps1").read_text(encoding="utf-8")
        self.assertNotIn("archive_sha256=[string]$receipt.archive_sha256", ue4)
        self.assertIn("delivery_mode=[string]$receipt.delivery_mode", ue4)


if __name__ == "__main__":
    unittest.main()
