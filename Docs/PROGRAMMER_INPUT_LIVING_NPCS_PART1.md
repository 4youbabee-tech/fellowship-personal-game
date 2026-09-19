# Programmer input — Living NPCs / Character Memory — Part 1

Status: ANALYZED_AND_PROMOTED
Date: 2026-09-19
Source: project owner forwarding programmer guidance
Disposition: the owner confirmed this was the complete combined message. The request has been analyzed and promoted into ProjectGovernor plus Data/LivingNPCIntelligencePlan.json. Existing NPC memory/social/dialogue foundations are reused rather than replaced.

## Core request

The project owner wants NPCs to feel like living people rather than static scripted actors.

Requested properties:
- personal memory of prior player conversations and meaningful events
- goals and daily needs
- daily routines such as work, eating, rest and travel
- emotional state that can change with context
- context-aware dialogue that changes with time/place/events
- relationships with other NPCs and the player
- character-specific knowledge limits
- speech support (STT/TTS) as a possible later layer

## Proposed technical ingredients from the programmer message

- LLM-backed dialogue, using an API or local model
- short-term and long-term memory
- goals/needs model
- emotional state
- context awareness
- relationship state
- speech-to-text and text-to-speech
- JSON/DataTable/lightweight database storage
- Behavior Tree / AI Controller / Blackboard as possible Unreal implementation mechanisms
- context injection into dialogue generation

## Requested character-memory model

Every important NPC should have a profile covering:
- identity: name, race, age, origin, occupation/role
- personal history
- historical/lore background known to that NPC
- family/friends/enemies/relationships
- world knowledge and explicit knowledge limits
- opinions/attitudes
- persistent event memory
- relationship changes caused by player actions

## Knowledge/canon rule

Character knowledge should be constrained by what that character could plausibly know at that point in the Part I film chronology.

Examples described in the programmer input:
- Gandalf should know his own deep history and relationships.
- Aragorn should know his heritage, Rivendell history and Arwen relationship.
- Sam should know his own Shire background and personal relationship to Frodo.
- ordinary Shire residents should know only local life, hearsay and limited outside-world information.

NPCs should admit ignorance rather than invent knowledge they should not possess.

## Suggested source material from programmer input

- project Story/Film canon plans
- NPCMemoryPlan.json
- StoryBeatPlan.csv
- Tolkien lore references
- Tolkien Gateway for detail verification when needed

## Suggested rollout from programmer input

1. Prototype the full living-NPC stack on one Shire NPC.
2. Expand first to major characters such as Gandalf, Frodo, Sam and Aragorn.
3. Expand to secondary named characters.
4. Expand to generic regional populations.

## Acceptance ideas from programmer input

- NPC remembers prior interactions.
- NPC follows a daily routine.
- dialogue changes with time/place/events.
- emotional state is reflected in behavior/presentation.
- each NPC has a coherent identity/profile.
- responses remain consistent with that NPC's knowledge.
- NPC admits when it does not know something.
- important memories persist.

## Important implementation note

This file stores the incoming request only. It does not approve a specific LLM vendor, API, cloud dependency, cost model, always-online requirement, voice provider, or unrestricted generative behavior. Final architecture will be decided after Part 2 and must remain compatible with the project's existing bounded-dialogue/canon/performance rules and the 8 GB RAM / ~2 GB VRAM target.

## Analysis outcome

Already present before this message:
- bounded named-NPC persistent memory and relationship deltas,
- profile/alias/knowledge tags,
- chapter-aware schedules,
- contextual NPC-to-NPC conversations,
- deterministic bounded dialogue selection and story/knowledge guards.

Newly promoted from this message:
- explicit goals/needs/emotion model,
- stronger character biography/knowledge-envelope requirement,
- explicit ignorance behavior when knowledge is unavailable,
- local-first architecture with optional future bounded LLM/STT/TTS layers,
- phased rollout from Shire prototype to major characters and then regional populations.

Runtime started in CP56 by adding bounded hunger/fatigue/social/fear state and goal/emotion bias to AShireAmbientNPC. This remains deliberately cheap and cannot own quest/story state.
