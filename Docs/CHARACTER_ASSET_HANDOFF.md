# CHARACTER ASSET HANDOFF - NATURAL HUMANOID PRODUCTION

This is the handoff contract for replacing the current modular/static proxy characters with believable skeletal characters.

## What the current game actually has

The repository contains project-owned modular character foundations and many static OBJ pieces. They are useful as temporary silhouettes and fallbacks, but they are not a final human character solution. A natural moving character requires a real skeletal mesh, skin weights, deformation, animation and material work.

Do not convert a static OBJ to FBX and call it finished. That changes the container format, not the character quality.

## What to provide when external character art is available

For each important animated character, the preferred package is:

- `SK_<Character>.fbx` - one skinned skeletal mesh.
- Same skeleton across that character's locomotion clips.
- `AN_<Character>_Idle.fbx`
- `AN_<Character>_Walk.fbx`
- `AN_<Character>_Run.fbx`
- `AN_<Character>_Crouch.fbx`
- `AN_<Character>_Jump.fbx`
- `AN_<Character>_Interact.fbx`
- story/combat clips only where the character needs them.
- BaseColor/Normal/ORM textures as PNG or TGA.
- Source/provider + permission/license terms + retrieval date.

The first high-value package is **Frodo**. After that: Gandalf, Sam, Aragorn, Gimli, Legolas, Merry, Pippin, Boromir.

## Folder contract

Source handoff:

`SourceAssets/Production/Characters/Rigs/<Character>/`

UE destination:

`/Game/Production/Characters/Rigs/<Character>/`

Expected UE assets:

- `SK_<Character>`
- `ABP_<Character>_Locomotion`
- imported animation sequences
- character material instances

## Visual standard

Characters must stop reading as cubes/spheres/cylinders or disconnected modular dolls. The production bar is:

- believable head/neck/shoulder anatomy,
- character-specific height and mass,
- layered clothing,
- readable hands/feet,
- natural hair volume,
- separate skin/cloth/leather/metal response,
- character-specific gait and idle,
- face/gaze behavior at conversation distance,
- no foot sliding or snapping as an accepted final state.

## Performance standard

The target is UE4.27.2, DX11, 720p Low-Medium, 30 FPS, 8 GB RAM and about 2 GB VRAM.

No arbitrary triangle ceiling is declared before target-device measurements. Hero detail is selective; secondary characters share safe skeleton/material families; facial/IK/cloth work is distance/state gated; LOD and material cost must be measured in Unreal.

## Source/canon identity

Use the project's character bible and visual atlas for race, age, wardrobe, equipment, silhouette and story-state cues. Film-context identity is useful, but the production pipeline does not require an exact actor scan or likeness.

## Acceptance

A supplied character is not called complete until:
1. provenance is recorded,
2. FBX imports as a real skeletal mesh,
3. skin/deformation is clean,
4. locomotion is integrated,
5. save/route state keeps the correct character,
6. exact-head UE4 build/import passes,
7. PIE visual/motion review passes,
8. target-device performance is measured.
