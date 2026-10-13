# P1C01 — Living Shire: Eight-Question Production Audit
Date: 2026-10-13 | Status: SOURCE-ONLY CANDIDATE; NOT ACCEPTED | Authority: Data/ProjectGovernor.json

> This file is an implementation-question ledger, not a second project governor. Items below are proposals unless an exact repository/runtime receipt is cited. Verify film-core sequence against the supplied source before modifying any canonical beat. Dialogue written for this package must be original.

## Cross-system invariant
LivingWorldDirector owns coarse world schedule and weather/danger signals; ShireNPCContextSubsystem owns local NPC context and reactions. Exchange compact event identifiers with explicit lifetime and story-state guards, rather than synchronous cross-calls each frame. Near NPCs are leased from pools; far inhabitants are abstract schedule records. On release: clear interaction prompts, dialogue callbacks, pending path requests, transient awareness and source actor IDs. No per-NPC unconditional Tick; use significance and bounded event cadence. Heavy meshes via soft pointers and FStreamableManager; repeated static dressing via HISM. Save durable quest and story facts, not transient actor pointers.

## Location A: Bag End interior, doorstep and garden
1. **Contents:** hobbit-hole, door/threshold, furniture and writing objects, garden beds, paths, household clutter; exact character placements story-state gated.
2. **Without player:** light and ambient household sounds change; nearby passersby follow pooled schedules, with no NPC required to idle beside the door indefinitely.
3. **Interaction:** approach affords a prompt only in reach and line-of-sight; door transit checks collision and quest lock atomically; touching household objects yields short original context only where allowed.
4. **Sensory:** muffled interior ambience transitions to birds, breeze, soil and footsteps outside; interior/outdoor reverb volumes must not stack.
5. **Time/weather/danger:** warm occupied interior versus cooler evening threshold; rain ambience outside, interior attenuation; threat cannot instantly materialize indoors.
6. **Story visibility:** no later Ring-related knowledge or future characters before the proper beat; scene entry and exit depend on authoritative story flags.
7. **Missing details:** door open/close audio, clearance of smaller hobbit capsule, blocked interaction while cinematics control input, safe spawn orientation.
8. **Breakage:** load at doorway, repeated interact, input during animation, missing soft-loaded mesh, stuck capsule; restore to a tested fallback transform if collision invalid.

## Location B: Hobbiton lanes and inhabited gardens
1. **Contents:** homes, low fences, market/domestic tools, flower boxes, livestock or birds where source/capacity permits, carts, planted fields.
2. **Without player:** bounded delivery, gardening, conversations and animal idle loops; distant versions simulated as schedule data rather than active AIs.
3. **Interaction:** NPC greeting changes with familiarity/story, carts avoid blocking road, footsteps respond to material, fences are collidable but decorative flowers non-blocking.
4. **Sensory:** staggered birds/voices, cart wheels and distant work; avoid synchronized audio loops.
5. **Time/weather/danger:** lights and shutters follow evening, reduced population overnight, rain redirects NPCs toward cover; fear overrides routines only after authoritative threat flag.
6. **Story visibility:** inhabitants cannot casually discuss future plot facts; party-related dressing activates only at correct phase.
7. **Missing details:** social spacing, work tools returning to rest pose, animal avoidance, shadow and LOD budgeting.
8. **Breakage:** pooled NPC retaining previous greeting, navigation through fence, cart blocking critical path, NPC pop-in near camera, save during context transition.

## Location C: Party Field and departure road
1. **Contents:** field edges, lanterns, seating, serving counters, streamers if the currently active canonical phase permits, forks/signs and path landmarks.
2. **Without player:** setup/cleanup and crowd routines exist only in relevant story phases; offscreen simulation records activity without spawning a full crowd.
3. **Interaction:** crowded dialogue uses priority/LOS; route stays navigable; nonessential props have no blocking collision.
4. **Sensory:** sound beds shift from gatherings to quieter road, with distance-based attenuation and performance-capped voices.
5. **Time/weather/danger:** weather and sunset alter ambience and occupation, not timeline truth; threat phase suppresses cheerful routines if canonically appropriate.
6. **Story visibility:** phase-specific party state is hidden outside its moment; departing NPCs must not be duplicated after the story transition.
7. **Missing details:** cleanup persistence, dynamic prompt arbitration, sign readability at 720p and festival material overdraw.
8. **Breakage:** dialogue overlap, crowd pool identity leak, save reload restoring obsolete party props, path narrowed by benches.

## Location D: Fields, hedgerows and wooded road
1. **Contents:** crop fields, fences, tree canopy, undergrowth, rocks, small wildlife, bends and trail markers.
2. **Without player:** birds and wind are ambient state; small animals flee on bounded triggers, not persistent per-frame chase; remote routes use proxy schedules.
3. **Interaction:** vegetation rustles locally, branches never trap player collision; pursuit/stealth response obeys quest state and LOS rather than omniscience.
4. **Sensory:** decreasing village sound, graded wind and foliage, footsteps by ground surface, silence reserved for scripted tension.
5. **Time/weather/danger:** dusk reduces visual reach without concealing path; rainfall softens distance cues; danger alters ambience only after narrative authorization.
6. **Story visibility:** hostile agents or overt omens cannot appear before their authorized beat; route signage never points to inaccessible future-runtime regions as playable.
7. **Missing details:** camera snag risk in hedges, rain shelter under canopy, ambient wildlife despawn policy.
8. **Breakage:** navmesh gaps, collision on LOD swap, actor loading too close to camera, falling outside world, save inside moving foliage mesh.

## Location E: Bucklebury Ferry approach, platform and bank
1. **Contents:** bank slope, path markers, reeds, queue posts/rope, landing structure, water and ferry surfaces; actual crossing state is story-gated.
2. **Without player:** quiet water motion, wind and shore ecology; ferry placement/state managed by one existing owner, not an independently ticking alternate controller.
3. **Interaction:** approach offers unambiguous objective; collision must support capsule grounding; boarding disables repeated prompt and does not assume a successful crossing from a static trigger.
4. **Sensory:** water lap, damp bank footing, wood creak and open-air wind; water sound should not play after leaving acoustic zone.
5. **Time/weather/danger:** mist and dimness can increase tension but must preserve route readability at 720p; rain effects capped for 2GB VRAM.
6. **Story visibility:** ferry availability, companion presence, pursuit and crossing completion require exact mission-story flags; later scenes remain unloaded/inaccessible.
7. **Missing details:** return route after partial objective, bank edge recovery, queue rope collisions, simultaneous party member boarding.
8. **Breakage:** known FerryLanding UCX collision import risk (PR #435); no acceptance before real UE import + landing/boarding PIE. Include save/load at near-bank and boarded boundaries, objective idempotency, repeated use and stream-out/reentry.

## Mission & cutscene rules across the route
- Each canonical beat has unique stable ID, prerequisite set, start/end story flags, visible actors/props, forbidden actors/props and save migration policy.
- Cinematic handoff must acquire/release input ownership exactly once, including skip, load and exception paths. Dialogue must never grant narrative knowledge before an authorized beat.
- Quest advancement is idempotent; save after atomic story-state updates. NPC context and world simulation only consume immutable event snapshots of that authoritative change.

## Story visibility matrix — proposed contract, awaiting exact canonical beat mapping
| Entity/family | Allowed when | Forbidden when | Proof required |
| --- | --- | --- | --- |
| Bag End household prompts | authorized local exploration phase | cinematics/input locked, irrelevant future phase | PIE interaction+restore |
| Party-specific decoration and crowds | party phase enabled by mission state | before party setup or after persisted cleanup | save/load and visual |
| Road/passersby and livestock | approved ambient phase and distance budget | despawn should never change story facts | pool lease/reuse test |
| Threat/pursuit appearances | explicit canonical threat beat committed | prior to corresponding authored reveal | quest event log + PIE |
| Ferry boarding/crossing | approach/boarding prerequisites complete | before authorized ferry beat, or after completion unless replay design allows | collider, quest and save tests |
| Later-region heroes/landmarks | future chapter authority after predecessor Gates 6/7 | during P1C01 as runtime encounters | gate inspection |

## Required observable acceptance before closing P1C01
- Actual on-device traversal Bag End → Ferry, threshold clearance, prompt LOS, grounded FerryLanding, no stuck spot.
- Story-state enter/re-enter/load at the five location boundaries; chapter-specific log showing stable flags and absence of premature content.
- Demonstrated pool identity reset and bounded near-NPC cost; async callback lifetime safety.
- 720p target device telemetry (frame-time p95, FPS and VRAM) and human visual/pacing review.
- Until evidence exists: STATIC DESIGN AUDIT ONLY. Asset counts, source validation and import commands are separate from world residency and acceptance.
