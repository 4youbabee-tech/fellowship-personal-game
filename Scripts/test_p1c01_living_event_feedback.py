#!/usr/bin/env python3
"""P1C01 living-world micro-event UI/eligibility source regression; not PIE evidence."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
INTERACTION = ROOT / "Source/ShireJourney/Private/World/ShireWorldEventInteraction.cpp"
DIRECTOR = ROOT / "Source/ShireJourney/Private/World/LivingWorldDirector.cpp"
HUD = ROOT / "Source/ShireJourney/Private/UI/ShireHUD.cpp"


def interaction_body(source):
    return source.split(
        "void AShireWorldEventInteraction::Interact_Implementation(AActor* Interactor)", 1
    )[1].split("\n}", 1)[0]


def denied_branch(body):
    match = re.search(
        r"if\s*\(!IsInteractionAllowed\(\)\)\s*\{(?P<branch>[^{}]*)\}",
        body, re.S,
    )
    if not match:
        raise AssertionError("Missing conditional eligibility guard in micro-event interaction")
    return match


class LivingEventFeedbackContracts(unittest.TestCase):
    def test_temporary_danger_refusal_never_consumes_event(self):
        source = INTERACTION.read_text(encoding="utf-8")
        body = interaction_body(source)
        denied = denied_branch(body)
        self.assertRegex(denied.group("branch"), r"\breturn\s*;")
        for destructive in ("DisableInteraction", "bConsumed", "SetActorHiddenInGame"):
            self.assertNotIn(destructive, denied.group("branch"))
        self.assertIn("!Player->IsGameplayWorldCommitted()", body)
        self.assertEqual(body.count("DisableInteraction();"), 1)
        self.assertGreater(body.find("DisableInteraction();"), denied.end())
        self.assertIn("Context->IsDangerStateActive()", source)
        self.assertIn('GetCurrentChapterId() != ChapterId', source)

    def test_prompt_and_response_use_separate_visible_hud_slots(self):
        source = INTERACTION.read_text(encoding="utf-8")
        body = interaction_body(source)
        hud = HUD.read_text(encoding="utf-8")
        self.assertIn("ShowAlert(PromptText, 1.2f);", body)
        self.assertIn("HUD->ShowDialogue(", body)
        self.assertIn("ResponseText,\n                    3.6f", body)
        self.assertNotIn("ShowAlert(ResponseText", body)
        self.assertIn("AlertMessage = Message;", hud)
        self.assertIn("DialogueLine = Line;", hud)
        self.assertIn("DrawWrappedText(DialogueLine.ToString()", hud)
        self.assertLess(body.index("HUD->ShowDialogue("), body.index("DisableInteraction();"))

    def test_single_consumption_and_bounded_pool_lifecycle(self):
        source = INTERACTION.read_text(encoding="utf-8")
        director = DIRECTOR.read_text(encoding="utf-8")
        self.assertIn("bConsumed = false;", source)
        self.assertIn("void AShireWorldEventInteraction::DeactivateForLivingWorldPool()", source)
        self.assertIn("InteractionMarker->SetCollisionEnabled(ECollisionEnabled::NoCollision);", source)
        self.assertIn("ReleaseInteractionToPool(Interaction);", director)
        self.assertIn("Event.ExpiresAt <= Now", director)
        self.assertIn("storyEffect=NONE", source)


if __name__ == "__main__":
    unittest.main()
