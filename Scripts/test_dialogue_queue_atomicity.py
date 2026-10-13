"""Source-only regression for P1C01 dialogue replacement; not an Unreal runtime test."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Source" / "ShireJourney" / "Private" / "Subsystems" / "ShireDialogueSubsystem.cpp"


class DialogueQueueAtomicityContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        text = SOURCE.read_text(encoding="utf-8")
        cls.body = text.split("bool UShireDialogueSubsystem::PlayDynamicSequence(", 1)[1].split(
            "\nvoid UShireDialogueSubsystem::StopDialogue()", 1
        )[0]

    def test_rejected_empty_request_preserves_active_dialogue_queue(self):
        body = self.body
        check = body.index("if (FilteredLines.Num() == 0)")
        prefix = body[:check]
        for forbidden in (
            "PendingLines.Empty(", "PendingLines.Add(", "PendingLines.RemoveAt(",
            "PendingLines =", "StopDialogue(", "ActiveDialogueCue =", "bPlaying =",
        ):
            self.assertNotIn(forbidden, prefix, forbidden)
        rejection = body[check:body.index("}", check)]
        self.assertIn("return false;", rejection)
        self.assertLess(check, body.index("StopDialogue();"))

    def test_successful_request_commits_filtered_lines_once(self):
        body = self.body
        for required in (
            "TArray<FShireDialogueLine> FilteredLines;",
            "FilteredLines.Reserve(Lines.Num());",
            "if (!Line.Subtitle.IsEmpty())",
            "FilteredLines.Add(Line);",
            "PendingLines = MoveTemp(FilteredLines);",
            "OnDialogueStateChanged.Broadcast(true);",
            "AdvanceQueue();",
        ):
            self.assertIn(required, body)
        self.assertLess(body.index("StopDialogue();"), body.index("PendingLines = MoveTemp(FilteredLines);"))
        self.assertLess(body.index("PendingLines = MoveTemp(FilteredLines);"), body.index("AdvanceQueue();"))
        self.assertNotIn("PendingLines = Lines;", body)


if __name__ == "__main__":
    unittest.main()
