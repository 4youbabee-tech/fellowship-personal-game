"""Single source of truth for headless runtime audit expectations.

Runtime C++ emits the evidence. Python consumers import this registry so marker text,
command-line modes, log names and warning-debt scope cannot drift independently.
"""
from __future__ import annotations

ALL_MODES = ("startup", "chapters", "state", "transitions", "faults", "pending", "edges")
STATE_SEQUENCE_MODES = ("state", "transitions", "faults", "pending", "edges")
DEDUP_MODES = ("transitions", "faults", "pending", "edges")

MODE_MARKERS = {
    "startup": (
        "ShirePlayableStartup: GameMode ready",
        "ShireStartupGrounding: PASS chapter=P1C01",
        "ShirePlayableStartup: chapter=P1C01 route=FrodoMain",
    ),
    "state": (
        "ShirePlayableStartup: GameMode ready",
        "ShireStartupGrounding: PASS chapter=P1C03",
        "ShireStateAudit: route-roundtrip=PASS",
        "ShireStateAudit: ring-core=PASS",
        "ShireStateAudit: discovery-core=PASS",
        "ShireStateAudit: progression-core=PASS",
        "ShireStateAudit: knowledge-core=PASS",
        "ShirePersistenceRestore: COMMIT",
        "ShireStateAudit: persistence-fields=PASS",
        "ShireStateAudit: disk-save-roundtrip=PASS",
    ),
    "transitions": (
        "ShireTransitionBarrier: PASS held-during-swap=yes cancel-release=yes",
        "ShireTransitionAudit: sequence=PASS chapters=8 routes=2 disk-save=PASS",
    ),
    "faults": (
        "ShireRollbackSnapshotApplied: health=67.0 stamina=54.0 resolve=43.0 supplies=2",
        "ShireRollbackAudit: PASS unsupported-request restored=yes movementReleased=yes freshSnapshot=yes npcContext=yes livingWorld=yes",
        "ShireRollbackSnapshotApplied: health=63.0 stamina=52.0 resolve=41.0 supplies=1",
        "ShireStreamFailureAudit: PASS async-failure rollback=yes resident-origin=yes movementReleased=yes freshSnapshot=yes",
    ),
    "pending": (
        "ShirePendingTransitionAudit: WINDOW-PASS old-world-authority=yes movementHeld=yes npcDestinationBlocked=yes",
        "ShirePendingTransitionAudit: PASS delayed-ready old-world-authority=yes destination-commit=yes",
    ),
    "edges": (
        "ShirePersistenceEdgeAudit: PASS legacy-terminal canonical-publications=1 worldCommits=1 chapter=P1C02",
        "ShireCheckpointRevisionAudit: PASS stale-completion stateApplied=no",
    ),
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

SOURCE_MARKER_ANCHORS = {
    "startup": (
        (0, "Source/ShireJourney/ShireGameMode.cpp", "ShirePlayableStartup: GameMode ready;"),
        (1, "Source/ShireJourney/ChapterWorldRouter.cpp", "ShireStartupGrounding: PASS chapter=%s"),
        (2, "Source/ShireJourney/ChapterWorldRouter.cpp", "ShirePlayableStartup: chapter=P1C01 route=%s"),
    ),
    "state": (
        (0, "Source/ShireJourney/ShireGameMode.cpp", "ShirePlayableStartup: GameMode ready;"),
        (1, "Source/ShireJourney/ChapterWorldRouter.cpp", "ShireStartupGrounding: PASS chapter=%s"),
        (2, "Source/ShireJourney/ShireGameMode.cpp", "ShireStateAudit: route-roundtrip=PASS"),
        (3, "Source/ShireJourney/ShireGameMode.cpp", "ShireStateAudit: ring-core=PASS"),
        (4, "Source/ShireJourney/ShireGameMode.cpp", "ShireStateAudit: discovery-core=PASS"),
        (5, "Source/ShireJourney/ShireGameMode.cpp", "ShireStateAudit: progression-core=PASS"),
        (6, "Source/ShireJourney/ShireGameMode.cpp", "ShireStateAudit: knowledge-core=PASS"),
        (7, "Source/ShireJourney/ShireQuestSubsystem.cpp", "ShirePersistenceRestore: COMMIT chapter=%s"),
        (8, "Source/ShireJourney/ShirePlayerCharacter.cpp", "ShireStateAudit: persistence-fields=PASS"),
        (9, "Source/ShireJourney/ShireGameMode.cpp", "ShireStateAudit: disk-save-roundtrip=PASS"),
    ),
    "transitions": (
        (0, "Source/ShireJourney/ShireGameMode.cpp", "ShireTransitionBarrier: PASS held-during-swap=yes cancel-release=yes"),
        (1, "Source/ShireJourney/ShireGameMode.cpp", "ShireTransitionAudit: sequence=PASS chapters=8 routes=2 disk-save=PASS"),
    ),
    "faults": (
        (0, "Source/ShireJourney/ChapterWorldRouter.cpp", "ShireRollbackSnapshotApplied: health=%.1f stamina=%.1f resolve=%.1f supplies=%d"),
        (1, "Source/ShireJourney/ShireGameMode.cpp", "ShireRollbackAudit: PASS unsupported-request restored=yes movementReleased=yes freshSnapshot=yes npcContext=yes livingWorld=yes"),
        (2, "Source/ShireJourney/ChapterWorldRouter.cpp", "ShireRollbackSnapshotApplied: health=%.1f stamina=%.1f resolve=%.1f supplies=%d"),
        (3, "Source/ShireJourney/ShireGameMode.cpp", "ShireStreamFailureAudit: PASS async-failure rollback=yes resident-origin=yes movementReleased=yes freshSnapshot=yes"),
    ),
    "pending": (
        (0, "Source/ShireJourney/ShireGameMode.cpp", "ShirePendingTransitionAudit: WINDOW-PASS old-world-authority=yes movementHeld=yes npcDestinationBlocked=yes"),
        (1, "Source/ShireJourney/ShireGameMode.cpp", "ShirePendingTransitionAudit: PASS delayed-ready old-world-authority=yes destination-commit=yes"),
    ),
    "edges": (
        (0, "Source/ShireJourney/ShireGameMode.cpp", "ShirePersistenceEdgeAudit: PASS legacy-terminal canonical-publications=1 worldCommits=1 chapter=P1C02"),
        (1, "Source/ShireJourney/ShirePlayerCharacter.cpp", "ShireCheckpointRevisionAudit: PASS stale-completion stateApplied=no"),
    ),
}

CHAPTER_SOURCE_ANCHORS = (
    ("Source/ShireJourney/ShireGameMode.cpp", "ShireChapterAudit: requested=%s quest=%s"),
    ("Source/ShireJourney/ChapterWorldRouter.cpp", "ShireStartupGrounding: PASS chapter=%s"),
    ("Source/ShireJourney/ChapterWorldRouter.cpp", "ShireChapterAudit: loaded=%s"),
    ("Source/ShireJourney/LivingWorldDirector.cpp", "ShireChapterAudit: living-world chapter=%s"),
    ("Source/ShireJourney/LivingWorldDirector.cpp", "ShireChapterAudit: weather chapter=%s"),
)

def required_markers(chapter, mode):
    if mode == "chapters":
        if not chapter:
            raise ValueError("chapter audit mode requires a chapter id")
        return [
            f"ShireChapterAudit: requested={chapter}",
            f"ShireStartupGrounding: PASS chapter={chapter}",
            f"ShireChapterAudit: loaded={chapter}",
            f"ShireChapterAudit: living-world chapter={chapter}",
            f"ShireChapterAudit: weather chapter={chapter}",
        ]
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
