"""Single source of truth for headless runtime audit expectations.

Runtime C++ emits evidence. Python consumers use semantic evidence IDs so a log-text
change cannot silently desynchronize the harness, static guards, deep audit and tests.
"""
from __future__ import annotations

ALL_MODES = ("startup", "chapters", "state", "transitions", "faults", "pending", "edges")
STATE_SEQUENCE_MODES = ("state", "transitions", "faults", "pending", "edges")

EVIDENCE_MARKERS = {
    "startup.ready": "ShirePlayableStartup: GameMode ready",
    "startup.ground_p1c01": "ShireStartupGrounding: PASS chapter=P1C01",
    "startup.route_p1c01": "ShirePlayableStartup: chapter=P1C01 route=FrodoMain",
    "state.ground_p1c03": "ShireStartupGrounding: PASS chapter=P1C03",
    "state.route_roundtrip": "ShireStateAudit: route-roundtrip=PASS",
    "state.ring_core": "ShireStateAudit: ring-core=PASS",
    "state.discovery_core": "ShireStateAudit: discovery-core=PASS",
    "state.progression_core": "ShireStateAudit: progression-core=PASS",
    "state.knowledge_core": "ShireStateAudit: knowledge-core=PASS",
    "state.persistence_commit": "ShirePersistenceRestore: COMMIT",
    "state.persistence_fields": "ShireStateAudit: persistence-fields=PASS",
    "state.disk_save": "ShireStateAudit: disk-save-roundtrip=PASS",
    "state.identity_guard": "ShireStateAudit: experience-identity=PASS direct-invalid-rejected=yes",
    "transition.barrier": "ShireTransitionBarrier: PASS held-during-swap=yes cancel-release=yes",
    "transition.sequence": "ShireTransitionAudit: sequence=PASS chapters=8 routes=2 disk-save=PASS",
    "transition.resident_recommit": "ShireResidentBankAudit: PASS already-resident-recommit=yes",
    "fault.invalid_request_rejected": "ShireInvalidTransitionAudit: PASS rejected-before-transaction=yes identityStable=yes revisionUnchanged=yes movementReleased=yes stateStable=yes npcContext=yes livingWorld=yes",
    "fault.snapshot_stream": "ShireRollbackSnapshotApplied: health=63.0 stamina=52.0 resolve=41.0 supplies=1",
    "fault.stream_failure": "ShireStreamFailureAudit: PASS async-failure rollback=yes resident-origin=yes movementReleased=yes freshSnapshot=yes",
    "pending.window": "ShirePendingTransitionAudit: WINDOW-PASS old-world-authority=yes movementHeld=yes npcDestinationBlocked=yes",
    "pending.commit": "ShirePendingTransitionAudit: PASS delayed-ready old-world-authority=yes destination-commit=yes",
    "edge.legacy_terminal": "ShirePersistenceEdgeAudit: PASS legacy-terminal preserved=yes canonical-publications=1 worldCommits=0 chapter=P1C01",
    "edge.stale_checkpoint": "ShireCheckpointRevisionAudit: PASS stale-completion stateApplied=no",
    "edge.identity_restore": "ShireExperienceRestoreAudit: PASS current=yes route-progress=yes",
    "edge.queued_checkpoint_race": "ShireQueuedCheckpointRaceAudit: PASS writes=2 staleEffects=0 revisionAdvanced=yes",
}

MODE_EVIDENCE_IDS = {
    "startup": (
        "startup.ready",
        "startup.ground_p1c01",
        "startup.route_p1c01",
    ),
    "state": (
        "startup.ready",
        "state.ground_p1c03",
        "state.route_roundtrip",
        "state.ring_core",
        "state.discovery_core",
        "state.progression_core",
        "state.knowledge_core",
        "state.persistence_commit",
        "state.persistence_fields",
        "state.disk_save",
        "state.identity_guard",
    ),
    "transitions": ("transition.barrier", "transition.sequence", "transition.resident_recommit"),
    "faults": (
        "fault.invalid_request_rejected",
        "fault.snapshot_stream",
        "fault.stream_failure",
    ),
    "pending": ("pending.window", "pending.commit"),
    "edges": (
        "edge.legacy_terminal",
        "edge.stale_checkpoint",
        "edge.identity_restore",
        "edge.queued_checkpoint_race",
    ),
}

MODE_MARKERS = {
    mode: tuple(EVIDENCE_MARKERS[evidence_id] for evidence_id in evidence_ids)
    for mode, evidence_ids in MODE_EVIDENCE_IDS.items()
}

MODE_LOG_NAMES = {
    "startup": "CI-PlayableStartup",
    "state": "CI-StateAudit",
    "transitions": "CI-TransitionAudit",
    "faults": "CI-FaultAudit",
    "pending": "CI-PendingTransitionAudit",
    "edges": "CI-PersistenceEdgeAudit",
}

MODE_EXTRA_ARGS = {
    "startup": (),
    "chapters": (),
    "state": ("-AuditState",),
    "transitions": ("-AuditTransitions",),
    "faults": ("-AuditFaults", "-ShireCIForceChapterAssetFailure=P1C02"),
    "pending": ("-AuditPendingTransition", "-ShireCIAssetReadyDelay=2.0"),
    "edges": ("-AuditPersistenceEdges",),
}

RUNTIME_LOG_PREFIXES = (
    "CI-PlayableStartup",
    "CI-ChapterAudit-",
    "CI-StateAudit",
    "CI-TransitionAudit",
    "CI-FaultAudit",
    "CI-PendingTransitionAudit",
    "CI-PersistenceEdgeAudit",
)

EVIDENCE_SOURCE_ANCHORS = {
    "startup.ready": ("Source/ShireJourney/Private/Core/ShireGameMode.cpp", "ShirePlayableStartup: GameMode ready;"),
    "startup.ground_p1c01": ("Source/ShireJourney/Private/World/ChapterWorldRouter.cpp", "ShireStartupGrounding: PASS chapter=%s"),
    "startup.route_p1c01": ("Source/ShireJourney/Private/World/ChapterWorldRouter.cpp", "ShirePlayableStartup: chapter=P1C01 route=%s"),
    "state.ground_p1c03": ("Source/ShireJourney/Private/World/ChapterWorldRouter.cpp", "ShireStartupGrounding: PASS chapter=%s"),
    "state.route_roundtrip": ("Source/ShireJourney/Private/Core/ShireGameMode.cpp", "ShireStateAudit: route-roundtrip=PASS"),
    "state.ring_core": ("Source/ShireJourney/Private/Core/ShireGameMode.cpp", "ShireStateAudit: ring-core=PASS"),
    "state.discovery_core": ("Source/ShireJourney/Private/Core/ShireGameMode.cpp", "ShireStateAudit: discovery-core=PASS"),
    "state.progression_core": ("Source/ShireJourney/Private/Core/ShireGameMode.cpp", "ShireStateAudit: progression-core=PASS"),
    "state.knowledge_core": ("Source/ShireJourney/Private/Core/ShireGameMode.cpp", "ShireStateAudit: knowledge-core=PASS"),
    "state.persistence_commit": ("Source/ShireJourney/Private/Subsystems/ShireQuestSubsystem.cpp", "ShirePersistenceRestore: COMMIT chapter=%s"),
    "state.persistence_fields": ("Source/ShireJourney/Private/Characters/ShirePlayerCharacter.cpp", "ShireStateAudit: persistence-fields=PASS transformDelta=("),
    "state.disk_save": ("Source/ShireJourney/Private/Core/ShireGameMode.cpp", "ShireStateAudit: disk-save-roundtrip=PASS"),
    "state.identity_guard": ("Source/ShireJourney/Private/Core/ShireGameMode.cpp", "ShireStateAudit: experience-identity=PASS direct-invalid-rejected=yes"),
    "transition.barrier": ("Source/ShireJourney/Private/Core/ShireGameMode.cpp", "ShireTransitionBarrier: PASS held-during-swap=yes cancel-release=yes"),
    "transition.sequence": ("Source/ShireJourney/Private/Core/ShireGameMode.cpp", "ShireTransitionAudit: sequence=PASS chapters=8 routes=2 disk-save=PASS"),
    "transition.resident_recommit": ("Source/ShireJourney/Private/Core/ShireGameMode.cpp", "ShireResidentBankAudit: PASS already-resident-recommit=yes"),
    "fault.invalid_request_rejected": ("Source/ShireJourney/Private/Core/ShireGameMode.cpp", "ShireInvalidTransitionAudit: PASS rejected-before-transaction=yes identityStable=yes revisionUnchanged=yes movementReleased=yes stateStable=yes npcContext=yes livingWorld=yes"),
    "fault.snapshot_stream": ("Source/ShireJourney/Private/World/ChapterWorldRouter.cpp", "ShireRollbackSnapshotApplied: health=%.1f stamina=%.1f resolve=%.1f supplies=%d"),
    "fault.stream_failure": ("Source/ShireJourney/Private/Core/ShireGameMode.cpp", "ShireStreamFailureAudit: PASS async-failure rollback=yes resident-origin=yes movementReleased=yes freshSnapshot=yes"),
    "pending.window": ("Source/ShireJourney/Private/Core/ShireGameMode.cpp", "ShirePendingTransitionAudit: WINDOW-PASS old-world-authority=yes movementHeld=yes npcDestinationBlocked=yes"),
    "pending.commit": ("Source/ShireJourney/Private/Core/ShireGameMode.cpp", "ShirePendingTransitionAudit: PASS delayed-ready old-world-authority=yes destination-commit=yes"),
    "edge.legacy_terminal": ("Source/ShireJourney/Private/Core/ShireGameMode.cpp", "ShirePersistenceEdgeAudit: PASS legacy-terminal preserved=yes canonical-publications=1 worldCommits=0 chapter=P1C01"),
    "edge.stale_checkpoint": ("Source/ShireJourney/Private/Characters/ShirePlayerCharacter.cpp", "ShireCheckpointRevisionAudit: PASS stale-completion stateApplied=no"),
    "edge.identity_restore": ("Source/ShireJourney/Private/Core/ShireGameMode.cpp", "ShireExperienceRestoreAudit: PASS current=yes route-progress=yes"),
    "edge.queued_checkpoint_race": ("Source/ShireJourney/Private/Characters/ShirePlayerCharacter.cpp", "ShireQueuedCheckpointRaceAudit: PASS writes=2 staleEffects=0 revisionAdvanced=yes"),
}

SOURCE_MARKER_ANCHORS = {
    mode: tuple(
        (index, *EVIDENCE_SOURCE_ANCHORS[evidence_id])
        for index, evidence_id in enumerate(evidence_ids)
    )
    for mode, evidence_ids in MODE_EVIDENCE_IDS.items()
}

CHAPTER_EVIDENCE_KINDS = ("requested", "grounding", "loaded", "living_world", "weather")
CHAPTER_MARKER_TEMPLATES = {
    "requested": "ShireChapterAudit: requested={chapter}",
    "grounding": "ShireStartupGrounding: PASS chapter={chapter}",
    "loaded": "ShireChapterAudit: loaded={chapter}",
    "living_world": "ShireChapterAudit: living-world chapter={chapter}",
    "weather": "ShireChapterAudit: weather chapter={chapter}",
}
CHAPTER_SOURCE_ANCHORS = {
    "requested": ("Source/ShireJourney/Private/Core/ShireGameMode.cpp", "ShireChapterAudit: requested=%s quest=%s"),
    "grounding": ("Source/ShireJourney/Private/World/ChapterWorldRouter.cpp", "ShireStartupGrounding: PASS chapter=%s"),
    "loaded": ("Source/ShireJourney/Private/World/ChapterWorldRouter.cpp", "ShireChapterAudit: loaded=%s"),
    "living_world": ("Source/ShireJourney/Private/World/LivingWorldDirector.cpp", "ShireChapterAudit: living-world chapter=%s"),
    "weather": ("Source/ShireJourney/Private/World/LivingWorldDirector.cpp", "ShireChapterAudit: weather chapter=%s"),
}


def mode_has_evidence(mode, evidence_id):
    return evidence_id in MODE_EVIDENCE_IDS.get(mode, ())


def evidence_marker(evidence_id):
    return EVIDENCE_MARKERS[evidence_id]


def chapter_has_evidence(kind):
    return kind in CHAPTER_EVIDENCE_KINDS


def required_markers(chapter, mode):
    if mode == "chapters":
        if not chapter:
            raise ValueError("chapter audit mode requires a chapter id")
        return [CHAPTER_MARKER_TEMPLATES[kind].format(chapter=chapter)
                for kind in CHAPTER_EVIDENCE_KINDS]
    try:
        return list(MODE_MARKERS[mode])
    except KeyError as exc:
        raise ValueError(f"unknown runtime audit mode: {mode}") from exc


def chapters_for_mode(mode):
    if mode == "chapters":
        return [f"P1C{i:02d}" for i in range(1, 9)]
    if mode in MODE_MARKERS:
        return [None]
    raise ValueError(f"unknown runtime audit mode: {mode}")


def log_name_for(chapter, mode):
    if mode == "chapters":
        if not chapter:
            raise ValueError("chapter audit log requires a chapter id")
        return f"CI-ChapterAudit-{chapter}"
    try:
        return MODE_LOG_NAMES[mode]
    except KeyError as exc:
        raise ValueError(f"unknown runtime audit mode: {mode}") from exc


def extra_args_for(mode):
    try:
        return list(MODE_EXTRA_ARGS[mode])
    except KeyError as exc:
        raise ValueError(f"unknown runtime audit mode: {mode}") from exc
