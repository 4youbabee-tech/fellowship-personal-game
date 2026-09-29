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


if __name__ == "__main__":
    unittest.main()
