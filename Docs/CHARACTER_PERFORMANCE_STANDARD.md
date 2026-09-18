# CHARACTER PERFORMANCE STANDARD

This document prevents character quality from depending on chat memory.

A character is not production-ready because it merely has a mesh, walk cycle and dialogue.
Every important character must read as a living performer.

## Facial acting
- Natural blink timing with variation.
- Eye target / gaze behavior during conversations and nearby events.
- Eyebrow and eyelid motion appropriate to emotion.
- Jaw and mouth movement driven by spoken dialogue.
- Lip-sync / viseme support once authored voice assets exist.
- Micro-expressions before and after important lines.
- Emotional carry-over after scenes instead of instant reset to neutral.
- Fear, grief, joy, suspicion, anger, relief and fatigue must affect the face where the rig allows.

## Voice performance
- Every runtime VO_* line must exist in Data/VoiceCuePlan.csv.
- Original performances only; no cloning or deliberate imitation of a specific film actor.
- Voice direction may reflect age, temperament, culture, role and scene intent.
- Pace, pauses, breath, whisper, strain, urgency and volume vary by scene.
- World dialogue prefers positional 3D playback from the actor.
- Cinematic/offscreen lines may use controlled 2D playback.
- Subtitles remain functional if a voice asset is missing.
- Important dialogue should lightly duck music instead of abruptly muting it.
- Ambient barks require cooldowns and variation to avoid repetition.

## Body language
- Distinct posture and center of gravity by character and race.
- Head and torso often turn before the whole body.
- Weight shifts and subtle idle motion prevent statue-like characters.
- Gestures support speech intent rather than looping randomly.
- Personal space differs for strangers, friends, confrontation and intimate scenes.
- Listener characters remain active: gaze, reactions, posture changes.
- Group conversations distribute attention rather than everyone staring at the player.

## Locomotion
- Visible acceleration/deceleration; avoid instant full-speed movement.
- Minimize foot sliding.
- Character-specific walk/run cadence.
- Proper slope response.
- Snow, mud, shallow water and stone can alter cadence and footstep response.
- Injury, fear, fatigue and urgency may alter posture/speed.
- Companion formations should avoid jitter and constant collision.

## Interaction animation
- Doors, tables, cups, books, ropes, boats, ladders and quest props should align hands/body where feasible.
- Sitting, kneeling, crouching, hiding and mounting should transition rather than snap.
- Dialogue should not freeze the full body unless intentionally cinematic.
- Pickup/use animations should visibly connect to objects where IK support exists.

## Combat performance
- Attack anticipation, contact and recovery must read clearly.
- Hit reactions should reflect direction/weight where possible.
- Stagger, block, dodge and knockback must not break story-critical progression.
- Orc, Uruk-hai, Troll and Nazgul-style threats need distinct aggression and movement.
- Companions react to danger and each other instead of fighting as isolated bots.
- Combat barks need cooldown/priority rules.
- Defeated enemies must not block quest-critical paths.
- Camera shake and hit feedback remain restrained for comfort/performance.

## Environmental reaction
- Cold: tighter posture, slower idle, optional breath effect if affordable.
- Wind: clothing/hair/robe response where supported, otherwise animation-driven approximation.
- Rain/wetness: audio/material response where practical.
- Heat/fire: flinch/turn-away behavior when relevant.
- Darkness/fear: tighter grouping and reduced casual idle.
- Safe areas: looser posture, seated/resting/social behaviors.

## Crowd and living world
- Ambient NPCs have purpose: work, walk, rest, socialize, carry, watch, react.
- Avoid synchronized identical routines.
- Crowd density changes with place/time/story state.
- Nearby NPCs can react to events while distant NPCs remain cheap.
- NPCs recover from obstruction and should not permanently jam paths.

## Character continuity
- Injury, fear, grief, fatigue and equipment changes persist through the relevant story window.
- Dialogue, voice, posture and animation must agree with story state.
- Save/load and route switching restore the correct character state.
- Characters should not immediately act cheerful after tragic beats unless intentionally written.

## Performance budget
Target: UE4.27, DX11, 720p, 30 FPS, 8 GB RAM, low VRAM.
- Hero characters may use richer rigs than ambient NPCs.
- Facial animation may reduce/disable outside conversation distance.
- IK/face/cloth evaluation should be proximity/state gated.
- Ambient characters use LODs and reduced update frequency at distance.
- Cloth/hair physics must be selective and scalable.

## Acceptance rule
A hero character cannot be marked ACCEPTED until these are reviewed:
visual identity, locomotion, idle variation, gaze, facial expression, lip-sync/voice,
dialogue staging, interactions, story-state reactions, combat/stealth reactions when relevant,
save/load continuity, and target-device performance.

## Current implementation truth
Current characters are still procedural proxies. This document defines required production quality;
it does not claim final skeletal meshes, facial rigs, animation sets or voice assets already exist.
