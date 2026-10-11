#!/usr/bin/env python3
"""Source contract for pending chapter checkpoint dispatch (no Unreal required)."""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Source/ShireJourney/Private/Characters/ShirePlayerCharacter.cpp"


class PendingCheckpointGuardTest(unittest.TestCase):
    def test_dispatch_rejection_preserves_pending_checkpoint(self):
        text = SOURCE.read_text(encoding="utf-8")
        start = text.index("if (PendingChapterCheckpointId != NAME_None &&")
        end = text.index("AttackCooldownRemaining =", start)
        block = text[start:end]
        self.assertIn("if (SaveAutomaticCheckpoint(CheckpointId, true))", block)
        success = block.split("if (SaveAutomaticCheckpoint(CheckpointId, true))", 1)[1]
        self.assertIn("PendingChapterCheckpointId = NAME_None;", success)
        self.assertNotIn("PendingChapterCheckpointId = NAME_None;", block.split("if (SaveAutomaticCheckpoint(CheckpointId, true))")[0])
        self.assertIn("dispatch=accepted", success)
        self.assertIn("!bPendingSaveRestoreTransform", block)
        self.assertIn("!bWorldTransitionHeld", block)
        self.assertIn("PendingCheckpointRetrySeconds <= 0.0f", block)
        self.assertIn("PendingCheckpointRetrySeconds = 1.0f", block)
        self.assertIn("dispatch=rejected", block)
        self.assertNotIn("async-save=success", block)


if __name__ == "__main__":
    unittest.main()
