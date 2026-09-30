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
            "SOURCE_IMPLEMENTED_EXACT_HEAD_PROOF_PENDING",
        )
        for car_id in (
            "PARTY_AND_BAG_END_INTERACTION_DENSITY",
            "NPC_ROUTINES_SOCIAL_MEMORY",
            "FAUNA_ENVIRONMENTAL_MOTION",
            "CHARACTER_PRESENTATION",
            "QUEST_SIDE_ACTIVITY_COHERENCE",
            "CINEMATIC_CONTROL_HANDOFF",
            "SHIRE_AUDIO_IDENTITY",
            "SAVE_LOAD_LONG_SESSION",
            "TARGET_DEVICE_PROFILE_AND_GATE67",
        ):
            self.assertEqual(cars[car_id]["status"], "GATED")


    def test_p1c01_shire_world_density_is_bounded_and_instanced(self):
        root = Path(__file__).resolve().parents[1]
        contract = json.loads((root / "Data" / "P1C01ShireWorldDensityCarV1.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["status"], "SOURCE_IMPLEMENTED_EXACT_HEAD_PROOF_PENDING")
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


if __name__ == "__main__":
    unittest.main()
