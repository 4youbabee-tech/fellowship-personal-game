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


    def test_stopped_dialogue_cancels_voice_before_state_reset_event(self):
        source = SOURCE.read_text(encoding="utf-8")
        stop = source.split("void UShireDialogueSubsystem::StopDialogue()", 1)[1].split(
            "\nvoid UShireDialogueSubsystem::AdvanceQueue()", 1
        )[0]
        self.assertIn("if (bWasPlaying)", stop)
        self.assertIn("OnVoiceCueRequested.Broadcast(NAME_None);", stop)
        self.assertLess(stop.index("OnVoiceCueRequested.Broadcast(NAME_None);"),
                        stop.index("OnDialogueStateChanged.Broadcast(false);"))

    def test_unvoiced_subtitle_cancels_previous_voice(self):
        source = SOURCE.read_text(encoding="utf-8")
        advance = source.split("void UShireDialogueSubsystem::AdvanceQueue()", 1)[1]
        self.assertIn("OnSubtitleChanged.Broadcast(CurrentLine);", advance)
        self.assertIn("OnVoiceCueRequested.Broadcast(CurrentLine.VoiceCue);", advance)
        self.assertNotIn("if (CurrentLine.VoiceCue != NAME_None)", advance)

    def test_audio_none_cancels_async_and_active_voice_without_new_load(self):
        audio = (ROOT / "Source" / "ShireJourney" / "Private" /
                 "Subsystems" / "ShireAudioSubsystem.cpp").read_text(encoding="utf-8")
        play = audio.split("void UShireAudioSubsystem::PlayVoiceCue(FName CueId)", 1)[1].split(
            "\nvoid UShireAudioSubsystem::ClearPersistentAudio()", 1
        )[0]
        self.assertIn("if (CueId != NAME_None)", play)
        self.assertIn("CancelPendingAudioCategory(ShireAudioAssetPaths::VoiceCategory);", play)
        self.assertIn("PendingVoiceCue = CueId;", play)
        self.assertIn("ActiveVoiceComponent->Stop();", play)
        self.assertIn("if (CueId == NAME_None)\n    {\n        return;\n    }", play)
        self.assertLess(play.index("ActiveVoiceComponent->Stop();"),
                        play.index("if (CueId == NAME_None)"))
        self.assertLess(play.index("if (CueId == NAME_None)"),
                        play.index("ResolveVoiceAsset(CueId)"))


if __name__ == "__main__":
    unittest.main()
