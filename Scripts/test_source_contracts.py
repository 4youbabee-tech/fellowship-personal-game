import unittest

from source_contracts import (
    first_member_assignment_position,
    signal_precedes_member_mutation,
)


class SourceContractTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
