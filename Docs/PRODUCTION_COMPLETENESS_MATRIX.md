# PRODUCTION COMPLETENESS MATRIX

This file prevents major game pillars from depending on chat memory.

A chapter is not complete because its quest path works. Every chapter must be checked across all production pillars.

## Status
NOT_STARTED / FOUNDATION / PROTOTYPE / FUNCTIONAL / POLISH_PENDING / ACCEPTED

## Mandatory pillars
1. Canon/story
2. Main gameplay loop
3. Exploration/side content
4. Character visual identity
5. Body animation
6. Facial acting / gaze / lip-sync
7. Spoken voice
8. Subtitles/dialogue
9. Music
10. SFX/foley
11. Ambience
12. NPC routines/social life
13. Enemy/creature AI
14. Combat/stealth when story requires it
15. Terrain/geography/scale
16. Architecture/props
17. Vegetation/biome
18. Weather/time/atmosphere
19. Cinematic presentation
20. Save/load continuity
21. Performance on target laptop
22. Accessibility/readability
23. Guardian/static validation
24. UE4.27 compile
25. PIE/device test

| Chapter | Story | Gameplay | Exploration | Characters | Face/Anim | Voice | Audio | AI/Life | Combat | Geography | Atmosphere | Cinematic | Save | Perf | PIE |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1C01 Shire | FUNCTIONAL | FUNCTIONAL | FUNCTIONAL | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | FUNCTIONAL | FUNCTIONAL stealth | FUNCTIONAL | FUNCTIONAL | PROTOTYPE | FUNCTIONAL | PROTOTYPE | FUNCTIONAL |
| P1C02 Bree | FUNCTIONAL | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | NOT_STARTED | PENDING |
| P1C03 Weathertop/Ford | FUNCTIONAL | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | NOT_STARTED | PENDING |
| P1C04 Rivendell | FUNCTIONAL | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | PROTOTYPE | N/A | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | NOT_STARTED | PENDING |
| P1C05 Road/Caradhras/West Gate | FUNCTIONAL | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | NOT_STARTED | PENDING |
| P1C06 Moria | FUNCTIONAL | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | NOT_STARTED | PENDING |
| P1C07 Lothlorien | FUNCTIONAL | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | PROTOTYPE | N/A | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | NOT_STARTED | PENDING |
| P1C08 Anduin/Amon Hen | FUNCTIONAL | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | FOUNDATION | FOUNDATION | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | PROTOTYPE | FOUNDATION | NOT_STARTED | PENDING |

## Voice rule
Every runtime non-empty VO_* identifier must exist in Data/VoiceCuePlan.csv.
Voice status remains FOUNDATION while required voice assets are ASSET_PENDING.

## Update rule
Whenever a chapter, route, enemy, biome, mechanic or major story beat changes:
- update this matrix,
- update the relevant story/audio plan,
- add Guardian validation where machine-checkable,
- do not mark ACCEPTED without real UE4.27/PIE evidence.
