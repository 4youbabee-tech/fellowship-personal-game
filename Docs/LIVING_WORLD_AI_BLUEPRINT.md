# LIVING WORLD & NPC INTELLIGENCE BLUEPRINT

> This document captures the long-term requirement that the game world should feel alive during ordinary traversal,
> not only during scripted quests or cinematics.

## 1. Player-facing goal

Wherever the player walks, the world should provide believable signs of life:
- people with purpose,
- social interactions,
- environmental motion,
- readable geography,
- ambient sound,
- small discoveries,
- changing atmosphere,
- story-aware reactions,
- occasional low-cost events.

The goal is not random noise. Activity must fit the region, story state, time/atmosphere, canon and performance budget.

## 2. Current proven/foundation behavior

Present foundations in the current source include:
- ambient NPC walking/wait routines,
- distance-adaptive NPC ticking,
- player awareness and look-at behavior,
- nearby NPC-to-NPC social pauses,
- story NPC gaze/blink/mouth proxy acting,
- contextual/story-reactive dialogue foundations,
- story-reactive Shire atmosphere,
- persisted landmark discovery,
- chapter-specific biome contracts,
- hills/fields/wooded road/water in Shire,
- planned/implemented prototype geography for ridges, marshes, valley walls, waterfalls, snow pass, Moria scale, golden forest, river canyon,
- ambient/music/SFX runtime routing.

These are foundations. They do **not** yet satisfy the full living-world requirement.

## 3. NPC intelligence target

### 3.1 Identity
Every important or recurring NPC should eventually have:
- stable identity,
- role/job,
- home/anchor region,
- faction/community,
- temperament tags,
- social links,
- story knowledge boundary,
- current routine/state.

### 3.2 Daily/routine behavior
NPCs should support data-driven routine phases such as:
- home,
- work,
- travel,
- market/social,
- rest,
- story override,
- danger response.

For low-spec hardware, distant NPCs use cheap simulation/state updates rather than full behavior ticks.

### 3.3 Social graph
NPCs may know or recognize selected other NPCs.
Relationships can carry bounded values/tags such as:
- family,
- friend,
- coworker,
- authority,
- distrust,
- unfamiliar.

The social graph must be authored/data-driven. It must not invent canon-changing relationships.

### 3.4 Bounded conversation intelligence
NPC conversation should eventually combine:
- authored intent libraries,
- current story chapter/beat,
- NPC identity and knowledge,
- recent local event memory,
- relationship context,
- location/activity,
- player reputation/interaction history where appropriate.

The system may vary phrasing or choose among approved intents, but must not:
- contradict canon,
- reveal knowledge the NPC should not possess,
- change mandatory story outcomes,
- invent major quests or relationships,
- generate unlimited dialogue at runtime on the target laptop,
- imitate film screenplay dialogue verbatim.

Preferred architecture is **bounded generation/selection**, with deterministic fallbacks and cached lines where needed.

### 3.5 NPC-to-NPC conversation
Target behavior:
- NPCs can greet, gossip, work-talk or react to local events,
- conversations are short and context-aware,
- participants face/respond to each other,
- dialogue has cooldowns and repetition control,
- player proximity can make conversations audible/visible,
- story-critical NPC dialogue always overrides ambient chatter.

Current source has social pauses but not a complete NPC-to-NPC dialogue system.

### 3.6 Memory
Planned NPC memory tiers:
- immediate memory: recent player/NPC encounter,
- local story memory: completed nearby event/beat,
- relationship memory: repeated interactions,
- persistent named-NPC memory only when it improves continuity.

Ambient crowd NPCs should use cheaper aggregate memory to protect save size and CPU.

## 3A. Part I NPC social data contract

`Data/NPCSocialModel.json` is now the data-first contract for Part I NPC intelligence.

It defines:
- stable NPC identity IDs and aliases,
- named versus ambient archetype profiles,
- roles/community/temperament tags,
- bounded knowledge tags,
- low-cost schedule templates,
- initial authored relationship edges,
- persistence tiers,
- story/danger override precedence.

This is intentionally **not** the runtime AI implementation. The active functional hard gate still blocks a large behavior rollout.
When runtime consumption is opened, the game should read this contract rather than hard-code a second identity/relationship model.

The model uses aliases so one character identity (for example a story alias) cannot accidentally receive duplicate persistent memories.

## 3C. Remote-safe intelligence contracts

The following contracts are now defined before runtime rollout:

- `Data/NPCConversationPlan.json` — participant eligibility, intent types, knowledge/story gates, priority, cooldowns and repetition fallback.
- `Data/NPCMemoryPlan.json` — bounded memory tiers, expiry, route partitioning, per-profile/save budgets and alias identity rules.
- `Data/LivingWorldEventPlan.json` — per-chapter micro-events, fauna, weather/prop motion, activity density and low-spec caps.
- `Data/BoundedDialoguePlan.json` — authored/template/cached variation modes, deny-unlisted knowledge guard, canon safety, word/cache limits and deterministic fallback.

These are deliberately data/validation contracts only. Runtime conversation playback, memory storage, event directing and dialogue variation remain behind the current functional/device gate.

## 4. Living-world target

### 4.1 Geography
Each chapter should have a strong physical identity with:
- elevation changes,
- valleys/ridges,
- water where appropriate,
- occlusion and reveal,
- multiple readable paths/loops when story allows,
- distant silhouettes/landmarks,
- traversal rhythm rather than flat arena spacing.

`Data/BiomePlan.csv` remains the chapter-level geography contract.

### 4.2 Environmental motion
Planned examples:
- foliage motion/wind impression,
- water motion and sound,
- smoke/chimneys/fire where appropriate,
- birds/insects/animals when performance permits,
- carts/doors/props or work activity,
- weather transitions,
- distant movement that sells scale without expensive AI.

### 4.3 Micro-events
A region may contain low-cost events such as:
- villagers carrying goods,
- brief greetings,
- market activity,
- animal crossing,
- worker task,
- traveler passing,
- child/family activity where appropriate,
- guard/watch behavior,
- weather reaction,
- aftermath/reaction to story events.

Micro-events must never block main progression.

### 4.4 Exploration density
The player should regularly encounter at least one of:
- visual landmark,
- NPC activity,
- ambient sound shift,
- small interaction,
- environmental story detail,
- vista/reveal,
- danger signal,
- side-story beat.

Exact spacing is chapter-specific and must be performance-tested rather than enforced as one universal metric.

## 5. Story-state awareness

Living-world behavior should read current:
- chapter,
- route,
- episode,
- active quest/stage,
- completed story beats,
- playable character.

Examples:
- Shire mood changes as danger enters the story,
- NPC dialogue changes after major local events,
- dangerous chapters reduce casual ambient behavior,
- Gandalf route world state must not overwrite Frodo's social/world continuity.

## 6. Performance architecture

Target remains:
- Windows,
- UE4.27.2,
- DX11,
- 720p,
- Low/Medium,
- 30 FPS floor,
- 8 GB RAM,
- roughly 2 GB VRAM-class GPU.

Therefore:
- full AI only near player,
- distance-adaptive tick,
- pooled/instanced environment motion,
- capped active conversational agents,
- cheap offscreen simulation,
- no always-on large language model requirement,
- data-driven deterministic fallback for dialogue,
- one major generated region active at a time unless later profiling proves otherwise.

## 7. Development phases

### LW0 — Foundation (partially present)
- routines,
- awareness,
- social pause,
- story-reactive dialogue hooks,
- biome contracts,
- audio routing.

### LW1 — Data model
- NPC identity/profile data,
- relationship data,
- living-world event catalog,
- dialogue intent categories,
- memory policy.

### LW2 — Social conversation
- NPC-to-NPC authored/contextual conversation runtime,
- repetition/cooldown control,
- story priority rules.

### LW3 — Persistent named-NPC memory
- limited persistent memories,
- relationship state,
- save/load integration.

### LW4 — Environmental life
- low-cost fauna/prop/work/weather micro-events,
- traversal activity density pass,
- chapter-specific motion/ambience.

### LW5 — Bounded dialogue intelligence
- optional bounded generation/variation layer,
- strict knowledge/canon guard,
- caching/fallback,
- performance and safety gate.

### LW6 — Chapter-by-chapter acceptance
For each chapter:
- functional,
- PIE-tested,
- device-tested,
- performance observed,
- visually accepted,
- living-world completeness recorded.

## 8. Acceptance criteria

The full living-world requirement is not accepted until:
- NPCs have meaningful routines beyond pacing,
- named NPCs have controlled context/memory where needed,
- NPC-to-NPC conversations actually occur,
- ambient dialogue respects repetition and story state,
- geography feels authored and varied,
- environmental motion is visible/audible without overwhelming performance,
- ordinary traversal repeatedly exposes believable life,
- save/load and route switching preserve required continuity,
- the target laptop sustains acceptable playability.

Until those are proven, the correct status is PARTIAL or PLANNED, not complete.

## Regional dialogue correction — 2026-09-19

The existing regional mood hash changed a random choice but did not constrain line meaning. `RequiredMood` now excludes mismatched regions. After existing story/memory/knowledge eligibility checks, matching regional text outranks generic text; fresh-line selection stays within the best context tier. Thirty new original lines cover the eight Moria companions and seven Lothlorien companions, without adding Gandalf to Lothlorien or revealing future events. They reuse four supported intents; danger warnings retain their separate path. Voice IDs remain empty for unrecorded lines. This is authored offline response selection, not free language understanding. `Shire.NPC.RegionalDialogue` provides an engine automation test; build/runtime validation remains pending.

## Owner standard — Living Social Landscapes (2026-10-10)

The Bag End-above-Bagshot Row garden/path/gardener image supplies an **experience and composition benchmark**, not a literal production asset or standalone canon authority. Hobbiton must read as a lived-in village whose people have households, work, travel purposes, nearby relationships, and plausible daily schedules. A gardener should travel on a usable path between a plausible home/work anchor; other residents should work, rest or converse in bounded, context-safe ways; neighboring buildings, cultivated plots, trees, natural motion and region-appropriate ambient audio support that impression without needless actor density.

Apply the same *principle*, not identical Hobbit culture, to every one of the 28 planned Middle-earth regions. Match inhabited settlements to local hierarchy, trades, family/community and authored story state. Wilderness, battlefields, abandoned strongholds or dangerous regions need their own meaningful environmental, wildlife or threat life, not fabricated peacetime civilian routines. Canon references and film-story sequence remain controlling; dialogue is original and bounded.

**System contract:** `ALivingWorldDirector` owns budgeted regional ambient/micro-event activation; `UShireNPCContextSubsystem` owns bounded NPC role/knowledge/relationship/dialogue context; region plans select authorized anchors, roles, states and density. Do not create competing ownership or couple long-lived story character identities to ephemeral ambient event lifetime. Pool ambient NPCs, throttle distant behavior, soft/async-stream heavy assets, instance vegetation/props, and test collision/traversal, interaction cooldowns, save/revisit transitions and 720p/30 FPS target. This is an owner-accepted design target, **not** a completed UE implementation or human visual acceptance.

**Delivery order:** prototype and accept P1C01 first; independent concept/warehouse/material/character preparation may continue for future regions, but their Runtime remains gated by predecessor Gate 6/7.
