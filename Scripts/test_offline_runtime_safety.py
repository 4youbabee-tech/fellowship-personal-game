#!/usr/bin/env python3
"""Fail-closed static regressions for off-runner player continuity fixes.

These assert production C++ ownership boundaries, not Unreal runtime behavior.
"""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

def source(relative):
    return (ROOT / relative).read_text(encoding="utf-8")

def body_between(text, start, end):
    begin = text.index(start)
    return text[begin:text.index(end, begin + len(start))]

PLAYER_CPP = "Source/ShireJourney/Private/Characters/ShirePlayerCharacter.cpp"
PLAYER_H = "Source/ShireJourney/Public/Characters/ShirePlayerCharacter.h"
PRESENT = "Source/ShireJourney/Private/Subsystems/ShireStoryPresentationSubsystem.cpp"
AUDIO_CPP = "Source/ShireJourney/Private/Subsystems/ShireAudioSubsystem.cpp"
AUDIO_H = "Source/ShireJourney/Public/Subsystems/ShireAudioSubsystem.h"

class OfflineRuntimeSafetyTests(unittest.TestCase):
    def test_cinematic_interrupted_by_gameplay_releases_lock(self):
        cpp = source(PRESENT)
        transition = body_between(cpp,
            "void UShireStoryPresentationSubsystem::HandleStoryBeat(",
            "void UShireStoryPresentationSubsystem::RequestSkipActivePresentation()")
        self.assertIn("bCinematicLocked && ActiveCue.Mode != EShireStoryPresentationMode::Cinematic", transition)
        release = transition.index("ReleaseCinematicLock();")
        self.assertLess(release, transition.index("OnStoryPresentationRequested.Broadcast(ActiveCue);"))
        skip = body_between(cpp, "void UShireStoryPresentationSubsystem::RequestSkipActivePresentation()",
                              "void UShireStoryPresentationSubsystem::ReleaseCinematicLock()")
        self.assertIn("ReleaseCinematicLock();", skip)
        self.assertNotIn("TriggerStoryBeat", skip)
        self.assertNotIn("StartChapter", skip)

    def test_escape_skip_bound_in_input_and_player(self):
        cpp = source(PLAYER_CPP)
        ini = source("Config/DefaultInput.ini")
        header = source(PLAYER_H)
        self.assertIn('ActionName="SkipCinematic"', ini)
        self.assertIn("Key=Escape", ini)
        self.assertIn('BindAction(TEXT("SkipCinematic"), IE_Pressed', cpp)
        self.assertIn("void SkipActiveCinematic();", header)
        skip = body_between(cpp, "void AShirePlayerCharacter::SkipActiveCinematic()",
                            "void AShirePlayerCharacter::HandleCinematicStateChanged(")
        self.assertIn("Presentation->IsCinematicLocked()", skip)
        self.assertIn("Presentation->RequestSkipActivePresentation();", skip)
        self.assertNotIn("TriggerStoryBeat", skip)

    def test_spawn_during_cinematic_inherits_lock(self):
        cpp = source(PLAYER_CPP)
        start = body_between(cpp, "void AShirePlayerCharacter::BeginPlay()",
                             "void AShirePlayerCharacter::EndPlay(")
        self.assertIn("Presentation->IsCinematicLocked()", start)
        self.assertIn("HandleCinematicStateChanged(true)", start)

    def test_audio_async_callback_has_unique_generation(self):
        cpp = source(AUDIO_CPP)
        header = source(AUDIO_H)
        self.assertIn("TMap<FName, uint64> PendingAudioRequestTokens", header)
        self.assertIn("uint64 NextAudioRequestToken = 0;", header)
        request = body_between(cpp, "void UShireAudioSubsystem::RequestAudioAssetAsync(",
                               "void UShireAudioSubsystem::CancelPendingAudioCategory(")
        self.assertLess(request.index("PendingAudioRequestTokens.Add(LoadKey, RequestToken)"),
                        request.index("StreamableManager.RequestAsyncLoad("))
        self.assertIn("RequestToken));", request)
        cancel = body_between(cpp, "void UShireAudioSubsystem::CancelPendingAudioCategory(",
                              "void UShireAudioSubsystem::HandleAsyncAudioReady(")
        self.assertIn("PendingAudioRequestTokens.Remove(It.Key())", cancel)
        callback = body_between(cpp, "void UShireAudioSubsystem::HandleAsyncAudioReady(",
                                "void UShireAudioSubsystem::ApplyMusicDuck(")
        self.assertIn("PendingAudioRequestTokens.FindRef(LoadKey) != RequestToken", callback)
        self.assertLess(callback.index("PendingAudioRequestTokens.FindRef(LoadKey) != RequestToken"),
                        callback.index("Cast<USoundBase>(AssetPath.ResolveObject())"))

    def test_pg129_validator_requires_stronger_audio_generation_guard(self):
        preflight = source("Scripts/pre_unreal_validate.py")
        self.assertIn("PG-129 async audio generation-token cancellation guard missing", preflight)
        self.assertIn("PendingAudioRequestTokens.FindRef(LoadKey) != RequestToken", preflight)
        self.assertIn("PendingAudioRequestTokens.Remove(It.Key())", preflight)
        self.assertNotIn('if "if (!PendingAudioLoads.Contains(LoadKey))" not in pg129_audio:', preflight)

    def test_player_placement_must_observe_teleport_result(self):
        cpp = source("Source/ShireJourney/Private/World/ChapterWorldRouter.cpp")
        restore = body_between(cpp, "bool AChapterWorldRouter::PlacePlayerAtCommittedTransform(",
                                  "bool AChapterWorldRouter::MovePlayerToChapterStart(")
        start = body_between(cpp, "bool AChapterWorldRouter::MovePlayerToChapterStart(",
                                "void AChapterWorldRouter::VerifyPlayerGroundingStability(")
        for body in (restore, start):
            self.assertIn("if (!PlayerPawn->SetActorLocationAndRotation(", body)
            self.assertIn("reason=actor-teleport-rejected", body)
            self.assertLess(body.index("reason=actor-teleport-rejected"), body.index("return true;"))
        self.assertIn("SetPlayerWorldHold(true)", start)

    def test_no_ground_never_teleports_to_unvalidated_requested_location(self):
        router = source("Source/ShireJourney/Private/World/ChapterWorldRouter.cpp")
        start = body_between(router, "bool AChapterWorldRouter::MovePlayerToChapterStart(",
                             "void AChapterWorldRouter::VerifyPlayerGroundingStability(")
        failure = start.split("if (!ResolveGroundedSpawnLocation(PlayerPawn, RequestedLocation, GroundedLocation))", 1)[1].split("reason=no-blocking-ground", 1)[0]
        self.assertNotIn("SetActorLocationAndRotation(", failure)
        self.assertNotIn("SetActorLocation(", failure)
        self.assertIn("SetPlayerWorldHold(true);", failure)
        self.assertLess(failure.index("SetPlayerWorldHold(true);"), len(failure))

    def test_pending_restored_transform_blocks_gameplay_input_and_saves(self):
        cpp = source(PLAYER_CPP)
        names = ("MoveForward", "MoveRight", "StartJump", "StartSprint",
                 "StartCrouch", "Interact", "PrimaryAttack", "UseSupply",
                 "QuickSave", "QuickLoad", "SaveAutomaticCheckpoint")
        for name in names:
            begin = cpp.index("AShirePlayerCharacter::" + name + "(")
            brace = cpp.index("{", begin)
            end = cpp.index("\n}", brace)
            with self.subTest(name=name):
                self.assertIn("bPendingSaveRestoreTransform", cpp[brace:end])
        restore = body_between(cpp, "bool AShirePlayerCharacter::TryApplyPendingSaveRestoreTransform(",
                               "bool AShirePlayerCharacter::RestoreSaveSnapshot(")
        self.assertIn("bPendingSaveRestoreTransform = false;", restore)

    def test_stale_asset_ready_rolls_back_and_clears_pending_hold(self):
        router = source("Source/ShireJourney/Private/World/ChapterWorldRouter.cpp")
        header = source("Source/ShireJourney/Public/World/ChapterWorldRouter.h")
        self.assertIn("void ClearPendingGroundingBarrier();", header)
        self.assertIn("void ClearPendingWorldTransaction(bool bCancelStreamingRequest);", header)
        helper = body_between(router, "void AChapterWorldRouter::ClearPendingWorldTransaction(",
                              "void AChapterWorldRouter::ClearPrototypeBuilders(")
        self.assertIn("AssetStreamingSubsystem->CancelPendingRequest();", helper)
        self.assertIn("PendingRouteId = NAME_None;", helper)
        self.assertIn("PendingEpisodeId = NAME_None;", helper)
        self.assertIn("PendingChapterId = NAME_None;", helper)
        self.assertIn("bPendingRestoreRouteTransform = false;", helper)
        self.assertIn("ClearPendingGroundingBarrier();", helper)

        ready = body_between(router, "void AChapterWorldRouter::HandleChapterAssetsReady(",
                             "void AChapterWorldRouter::HandleChapterAssetsFailed(")
        stale = ready.split("Quest/save state changed while assets were loading", 1)[1]
        self.assertIn("stale-asset-ready", stale)
        self.assertIn("RollbackFailedWorldSwap(LastLoadedChapterId, LastLoadedRouteId);", stale)
        self.assertLess(stale.index("RollbackFailedWorldSwap(LastLoadedChapterId, LastLoadedRouteId);"),
                        stale.index("return;"))

        rollback = body_between(router, "void AChapterWorldRouter::RollbackFailedWorldSwap(",
                                "void AChapterWorldRouter::CommitChapterWorld(")
        self.assertIn("ClearPendingWorldTransaction(true);", rollback)
        self.assertLess(rollback.index("ClearPendingWorldTransaction(true);"),
                        rollback.index("SetPlayerWorldHold(true);"))
    def test_npc_committed_context_accepts_zero_revision_as_valid_commit(self):
        cpp = source("Source/ShireJourney/Private/Subsystems/ShireNPCContextSubsystem.cpp")
        method = body_between(cpp, "void UShireNPCContextSubsystem::SetCommittedWorldContext(",
                              "bool UShireNPCContextSubsystem::IsLogicalWorldContextCommitted()")
        guard = method.split("CommittedChapterId = ChapterId;", 1)[0]
        self.assertIn("ChapterId.IsNone() || RouteId.IsNone() || EpisodeId.IsNone()", guard)
        self.assertNotIn("WorldRevision == 0", guard)
        self.assertLess(method.index("CommittedWorldRevision = WorldRevision;"),
                        method.index("bHasCommittedWorldContext = true;"))



    def test_living_world_initial_commit_synchronizes_before_population(self):
        header = source("Source/ShireJourney/Public/World/LivingWorldDirector.h")
        cpp = source("Source/ShireJourney/Private/World/LivingWorldDirector.cpp")

        self.assertIn("uint32 AppliedWorldRevision = MAX_uint32;", header)

        begin = body_between(cpp, "void ALivingWorldDirector::BeginPlay()",
                             "void ALivingWorldDirector::EndPlay(")
        self.assertNotIn("ActiveChapterId = QuestSubsystem->GetCurrentChapterId();", begin)
        self.assertIn("SynchronizeCommittedWorld();", begin)

        sync = body_between(cpp, "bool ALivingWorldDirector::SynchronizeCommittedWorld()",
                            "void ALivingWorldDirector::ResetForCurrentChapter()")
        self.assertIn("Router->IsWorldCommitted(", sync)
        self.assertLess(sync.index("Router->IsWorldCommitted("),
                        sync.index("ActiveChapterId = QuestSubsystem->GetCurrentChapterId();"))
        self.assertLess(sync.index("ActiveChapterId = QuestSubsystem->GetCurrentChapterId();"),
                        sync.index("ResetForCurrentChapter();"))



    def test_self_hosted_requires_manual_opt_in(self):
        workflow = source(".github/workflows/unreal-build-validation.yml")
        self.assertIn("run_self_hosted:", workflow)
        guard = body_between(workflow, "  unreal-build:", "    name: UE4.27.2 C++ Build")
        self.assertIn("github.event_name == 'workflow_dispatch'", guard)
        self.assertIn("inputs.run_self_hosted == true", guard)
        self.assertNotIn("github.event_name == 'pull_request' &&", guard)

if __name__ == "__main__":
    unittest.main()
