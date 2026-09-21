# PROJECT MEMORY SYSTEM

> **Permanent project memory.**
>
> This project must never depend on chat history, one programmer's memory, or the user's memory.
> If a conversation disappears or a developer changes, the repository must still explain what was requested,
> what was decided, what was implemented, what was tested, what remains incomplete, and what should happen next.

## 1. The two permanent systems

### A. Development memory / internal project intelligence
Purpose:
- capture every meaningful user request,
- distinguish request from implementation,
- preserve decisions and rejected/changed ideas,
- link work to commits/checkpoints/evidence,
- expose unfinished work,
- survive lost chats and developer handoffs.

Machine-readable source:
- `Data/ProjectGovernor.json`

Human recovery entry points:
- `Docs/CURRENT_PROJECT_STATE.md`
- `Docs/CHECKPOINTS.md`
- `Source/ShireJourney/README.md`
- this document.

### B. Living-world / NPC intelligence
Purpose:
- make the world feel inhabited rather than staged,
- give NPCs routines, awareness, social behavior, contextual dialogue and later bounded memory/relationships,
- make traversal continuously reveal believable life, geography, ambience and small events,
- preserve story canon and low-spec performance.

Design authority:
- `Docs/LIVING_WORLD_AI_BLUEPRINT.md`
- `Data/LivingWorldFeaturePlan.json`

## 2. Requirement lifecycle

Every meaningful request must have a stable ID and one status:

- `REQUESTED` — user asked for it; not yet designed enough to schedule.
- `PLANNED` — accepted and mapped to architecture/checkpoint work.
- `PARTIAL` — some foundation exists but the request is not satisfied.
- `IMPLEMENTED` — implementation exists in current source.
- `VALIDATED` — implementation passed the proof level required by the request.
- `DEFERRED` — intentionally postponed with a reason.
- `REJECTED` — intentionally not pursued, with a reason.
- `SUPERSEDED` — replaced by a newer requirement/decision.

Never mark a request `VALIDATED` because a programmer says it is done. Evidence must name the relevant
static/build/PIE/device/visual proof.

## 3. Required fields for every request

Each entry in `Data/ProjectGovernor.json` records:

- stable requirement ID,
- title,
- origin/source,
- intent in plain language,
- category,
- priority,
- status,
- current evidence,
- implementation references,
- missing work,
- acceptance criteria,
- dependencies,
- checkpoint association,
- notes/decision history.

A developer may add detail, but must not silently delete or rewrite the user's original intent.

## 4. Update rule

When the user makes a meaningful new request or materially changes an old one:

1. add/update the requirement ledger,
2. preserve the original intent,
3. classify current status honestly,
4. link existing implementation if any,
5. list what is still missing,
6. update the relevant blueprint/data plan,
7. update `CURRENT_PROJECT_STATE.md` if the active next steps change,
8. add a Guardian rule when the requirement creates a repeatable invariant.

When implementation lands:

1. update the requirement status,
2. link the commit/checkpoint/files,
3. record the actual proof level,
4. never erase remaining gaps.

## 5. Lost-chat recovery

A new human or automated programmer should:

1. read `Docs/CURRENT_PROJECT_STATE.md`,
2. read `Data/ProjectGovernor.json`,
3. read `Docs/CHECKPOINTS.md`,
4. read `Source/ShireJourney/README.md`,
5. inspect the latest `develop` head, open PRs and exact-SHA CI,
6. read `Data/OwnerSourceReferenceIndex.json` and confirm the Project Source materials needed for the task are available,
7. read the specific design plan for the work area,
8. resume only from recorded open requirements and the current hard gate.

Deleted chat text is not recoverable from this system unless it already left a trace in the repository.
The purpose of this ledger is to ensure future requests do leave that trace.

### Project Source recovery rule

The Project Source UI is a convenience surface; it is not the authoritative identity ledger. Durable source identity lives in `Data/OwnerSourceReferenceIndex.json` through stable source IDs, role/precedence metadata and SHA-256 fingerprints where recorded. If a chat or Project source attachment disappears, re-attach the source and compare its fingerprint when the bytes are available. Do not silently substitute a similarly named file.

The expected core library shape is Sources 01-11, three supplied film screenplays and one full Tolkien LOTR volume. Raw source PDFs are reference-only and never become runtime dependencies. Source availability does not itself prove canon interpretation or visual acceptance.

## 6. Memory integrity rules

- Never convert a vague idea into "implemented" without code/data evidence.
- Never convert a compile success into PIE/device/visual acceptance.
- Never remove an unfinished user request merely because scope is large.
- Never let a new developer replace a recorded requirement with a different interpretation without noting the decision.
- Keep performance constraints visible: UE4.27.2, target laptop, DX11, 720p, Low/Medium, 30 FPS floor.
- Story/world intelligence must remain compatible with the project's canon rules and route/save architecture.

## 6A. Project Governor / conflict and quality control

Permanent memory is not enough by itself. The project also uses a deterministic Governor:

- `Docs/PROJECT_GOVERNOR.md` — human-readable rules.
- `Data/ProjectGovernor.json` — the single authority containing requirements, decisions, conflicts, priorities, active gate and region quality state.
- `Scripts/project_governor.py` — CI validation of that single authority.

When two requests conflict, do not silently choose one. Record both, create a conflict/decision, and preserve the reason for the resolution.

## 7. Current recovered high-level user intent

The repository now explicitly records these long-lived directions:

- a personal, cinematic Part I journey that follows the established story spine,
- a world that feels alive while travelling, not only at quest markers,
- rich geography: hills, valleys, rivers, forests, mountains, settlements and chapter-specific atmosphere,
- NPCs that move, notice, socialize and eventually converse with bounded contextual intelligence,
- persistent save/route/checkpoint continuity,
- strict organization so another programmer can continue without chat memory,
- low-spec performance discipline rather than visual ambition that breaks the target device.

The machine-readable ledger is the status authority for what part of each direction is actually complete.
