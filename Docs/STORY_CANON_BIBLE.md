# Fellowship Personal Game - Story & Canon Bible

> **Implementation status note:** this file defines story/canon intent, not current completion status.
> For what is actually implemented and tested, use `Docs/CURRENT_PROJECT_STATE.md`.

Status: living design reference
Primary branch: develop
Target engine: Unreal Engine 4.27.2
Target profile: DX11, 720p/30 FPS, Low/Medium, 8 GB RAM, ~2 GB GPU

## 1. Canon policy

The game uses an ensemble adaptation structure rather than a Frodo-only structure.

Primary story reference:
1. Peter Jackson's The Lord of the Rings film trilogy.
2. Prefer the Extended Edition when it adds useful character/world material without contradicting the theatrical core.
3. Tolkien's books are a lore and world-building reference, but book-only events must not silently overwrite film continuity.
4. Original dialogue and side stories may fill believable gaps in time, but must not contradict established film events.
5. Do not reproduce screenplay dialogue. Preserve scene intent with original game writing.

Every authored story beat should be tagged mentally as one of:
- FILM_CORE: required event from the film continuity.
- FILM_EXTENDED: extended-edition event/detail.
- LORE_COMPATIBLE: book/lore material that does not contradict the film route.
- ORIGINAL_GAP_FILL: original game content placed in a believable unused time/location.

## 1A. Experiential adaptation rule

The film continuity is not only a reference for names and locations; it is the **story spine the player is meant to live through**.

For every major film anchor, design should ask:
- what does the player physically do here,
- what can be explored before/after it,
- which character viewpoint is appropriate,
- whether the moment is best expressed as traversal, stealth, combat, social interaction, interactive cinematic, or a short non-playable cinematic,
- what emotional/story information must survive the conversion into gameplay.

The project should not invent a replacement main story merely because games need interaction. Instead, interaction is built **around and through** the known story.

Player freedom belongs primarily between fixed story anchors:
- explore,
- speak with inhabitants,
- discover optional details,
- take side routes,
- experience ambient life,
- perform compatible side content.

That freedom must not:
- remove a required film outcome,
- reorder the major chronology without an explicit design decision,
- let optional content overwrite the Ring quest,
- turn important emotional beats into disposable filler.

`Data/FilmExperiencePlan.json` is the machine-readable coverage map for Part I high-level film anchors. It records treatment and coverage state without reproducing screenplay text.

## 2. Narrative principle

Frodo is the Ring-bearer and the central line of the Ring quest, but The Lord of the Rings is an ensemble story.

The game should therefore support multiple playable routes while preserving one coherent chronology.

A playable character is justified when that route:
- shows an important event Frodo is not present for,
- opens a meaningful region or social group,
- adds a distinct gameplay identity,
- and advances an established story thread rather than existing only as filler.

Do not switch characters merely for novelty.

## 3. Playable route model

### Part I - Fellowship era

Core route - Frodo
- Shire
- flight from the Shire
- Bree
- Weathertop / Ford
- Rivendell
- Fellowship road
- Moria
- Lothlorien
- Anduin / Amon Hen

Parallel route - Gandalf
- departure after identifying the Ring threat
- research/investigation bridge
- Isengard
- Saruman's betrayal
- imprisonment on Orthanc
- escape
- return to the main chronology at Rivendell

Short route opportunities
- Arwen: Flight to the Ford, because the film gives her this role.
- Aragorn: scouting / leadership beats where Frodo is resting or separated.
- Boromir: a short Amon Hen defense perspective can deepen his final arc without changing Frodo's route.

### Part II - The Two Towers era

The story must visibly branch into three major playable threads:
1. Frodo / Sam / Gollum
   - Emyn Muil
   - Dead Marshes
   - Black Gate
   - Ithilien
   - Faramir
   - Osgiliath in film continuity
   - road toward Minas Morgul

2. Aragorn / Legolas / Gimli, later joined by Gandalf
   - pursuit of the Uruk-hai
   - Riders of Rohan
   - Fangorn edge
   - Gandalf's return
   - Edoras
   - Rohan evacuation
   - Helm's Deep
   - Isengard aftermath

3. Merry / Pippin
   - captivity
   - escape into Fangorn
   - Treebeard
   - Entmoot
   - march on Isengard
   - flooding / destruction of Isengard

Potential focused character episodes:
- Eowyn in Rohan
- Theoden leadership moments
- Faramir ranger missions in Ithilien

### Part III - Return of the King era

Major playable threads:
1. Frodo / Sam / Gollum
   - Minas Morgul
   - Cirith Ungol
   - Shelob
   - Sam's rescue of Frodo
   - Mordor crossing
   - Mount Doom

2. Gandalf / Pippin
   - Minas Tirith
   - Denethor
   - preparation for siege
   - siege of Gondor

3. Aragorn / Legolas / Gimli
   - Dunharrow
   - Paths of the Dead
   - southern route / Corsair consequence
   - Pelennor arrival
   - march to the Black Gate

4. Merry / Eowyn / Theoden
   - Rohan mustering
   - ride to Gondor
   - Pelennor Fields
   - Witch-king confrontation

Later convergence:
- Houses / aftermath
- Black Gate
- Mount Doom resolution
- coronation
- return to the Shire
- Grey Havens

## 4. Character gameplay identities

Characters must not feel like reskinned Frodo.

Frodo
- exploration
- stealth
- Ring pressure / temptation
- vulnerability
- perception and story discovery

Sam
- support
- resilience
- carrying / rescue interactions
- practical environmental problem solving
- later stronger solo survival role

Aragorn
- tracking
- sword combat
- leadership
- scouting
- route finding
- NPC command moments

Gandalf
- limited high-impact magic
- protection
- knowledge / lore interactions
- leadership
- environmental problem solving
- never become an unlimited spell shooter

Merry / Pippin
- agility
- stealth / escape
- social and environmental interactions
- Ent / Rohan-specific story mechanics later

Legolas
- ranged combat
- perception
- mobility
- long-distance spotting

Gimli
- heavy melee
- durability
- breaking / defensive interactions

Boromir
- defensive combat
- protecting allies
- pressure from the Ring represented through story/state rather than random villain behavior

Eowyn
- Rohan social role
- sword combat
- courage / identity arc
- Pelennor role

Faramir
- ranger scouting
- ambush / ranged combat
- Ithilien knowledge
- leadership

## 5. Intelligent-world rule

The player should feel that NPCs live inside Middle-earth, not inside a trigger script.

NPC intelligence rules:
- NPCs know only information appropriate to their location, faction and story stage.
- No NPC should speak as if they know future events.
- Ambient dialogue changes after major story beats.
- Companions comment on nearby landmarks, danger and recent events.
- NPC routines should include walking, waiting, talking, working, guarding, eating or resting.
- Combat allies should have a readable role and avoid blocking the player.
- Hostile groups should patrol, investigate and react rather than stand motionless.
- Important NPCs should remember completed local interactions when possible.
- Side quests must be grounded in the region and current conflict.
- Avoid generic fetch quests unless they reveal character, lore, danger or geography.

## 6. Living-world standard

Every major region should include:
- a strong skyline / silhouette,
- recognizable landmarks,
- region-specific lighting,
- region-specific ambience,
- local NPC population,
- local routines,
- optional conversations,
- at least a few optional discoveries,
- environmental storytelling,
- side routes,
- quiet spaces between danger,
- consequences after major events.

No region should be only a chain of quest triggers.

## 7. Current Part I audit

### P1C01 - Shire

Current strengths:
- Frodo meets Gandalf on the Shire road before the party.
- Bilbo party route exists.
- Sam, Merry and Pippin are present.
- crop / wooded-road / Black Rider / ferry progression is film-compatible.
- Old Forest, Tom Bombadil and Barrow-downs are absent, which is correct for a film-first route.
- side stories and ambient Hobbiton life are now being expanded.

Important correction:
- The current route jumps too directly from Bilbo's disappearance into the Ring warning.
- Film continuity contains an important parallel Gandalf investigation / Isengard thread before Frodo's urgent departure.
- This should not be represented as if Gandalf simply remained at Bag End continuously.

### Missing Part I parallel region - Isengard

Critical missing story thread:
- Gandalf seeks Saruman.
- Saruman reveals his betrayal.
- Gandalf is imprisoned on Orthanc.
- Isengard is transformed for war.
- the Uruk-hai threat is established.
- Gandalf escapes and later reaches Rivendell.

This should become the first major parallel playable route candidate because it fills an actual film-canon gap, not an invented detour.

### P1C02 - Bree

Current core is broadly aligned:
- gate
- Prancing Pony
- ring incident
- Strider
- Nazgul attack
- departure

Needed depth:
- more common-room population and reactions
- Butterbur / local life
- stronger transition from Shire travel to Bree
- better Strider trust-building before departure

### P1C03 - Weathertop / Ford

Current film-compatible strengths:
- Strider leads the hobbits.
- Nazgul attack.
- Frodo is wounded.
- Arwen performs the Ford rescue, matching the film adaptation rather than the book's Glorfindel route.

Needed depth:
- wilderness travel should be longer and less trigger-like
- camp interactions
- visible deterioration of Frodo after the Morgul wound
- better horse/flight presentation when resources permit

### P1C04 - Rivendell

Current version is too compressed.

Current key beats:
- awakening
- Gandalf
- Council
- Fellowship assembly

Missing or underrepresented material:
- Bilbo reunion
- Aragorn / Narsil heritage material
- Aragorn / Arwen emotional thread
- Boromir's Gondor perspective
- Legolas and Gimli presence before the Fellowship forms
- stronger Council conflict and motivations
- recovery / waiting period that allows exploration and optional character episodes

Rivendell should become a major social/exploration hub, not a short bridge between chapters.

### P1C05 - Fellowship road / Caradhras / West Gate

Current version has:
- Fellowship march
- Caradhras
- West Gate

Missing or underrepresented film beats:
- Fellowship camp life
- Boromir training Merry and Pippin
- Aragorn/Boromir tension and respect
- Crebain / Saruman surveillance
- clearer decision to abandon the mountain route
- stronger approach to Moria

### P1C06 - Moria

Current version has:
- Moria entry
- Balin's Tomb
- Balrog
- Bridge of Khazad-dum

Critical missing gameplay/presentation:
- Watcher in the Water encounter at the West Gate
- discovery that Moria is a tomb
- Pippin's noise consequence
- Orc assault
- Cave Troll encounter
- Mithril reveal consequence
- stair / collapsing-path escape energy
- stronger Balrog reveal

Moria should be one of the largest dramatic gameplay chapters in Part I.

### P1C07 - Lothlorien

Current version has:
- Haldir
- Galadriel
- Caras Galadhon
- departure

Major missing material:
- grief after Gandalf
- Galadriel testing / private psychological pressure
- Mirror of Galadriel
- temptation of Galadriel by the Ring
- gifts and their future importance
- quiet exploration of Caras Galadhon
- stronger character conversations before departure

### P1C08 - Anduin / Amon Hen

Current version has:
- river journey
- Argonath
- Amon Hen
- Boromir fall
- Fellowship break

Needed depth:
- camp / river conversations
- Gollum hints if appropriate
- Boromir's increasing pressure from the Ring
- Frodo/Boromir confrontation
- Uruk-hai attack with readable purpose
- Boromir defending Merry and Pippin
- Merry and Pippin capture
- Aragorn's final exchange with Boromir
- clear three-way split for Part II:
  - Frodo + Sam
  - Merry + Pippin captives
  - Aragorn + Legolas + Gimli pursuit

## 8. Map philosophy

The current P1C01-P1C08 structure should be treated as large chapter buckets, not as proof that Middle-earth consists of only eight places.

A chapter may contain multiple subregions and alternate routes.

Examples:
- Shire = Hobbiton + Party Field + eastern fields + wooded road + ferry route.
- Rivendell = House of Elrond + terraces + gardens + waterfalls + council + outer valley / Bruinen access.
- Moria = West Gate + entrance halls + deep passages + Chamber of Mazarbul + stairs + bridge.
- Anduin = river camps + Argonath + Parth Galen + Amon Hen woods.

Parallel character episodes may reuse part of a chapter world or load a distinct region while preserving the main-route state.

## 9. Route / save architecture

Do not create a second QuestSubsystem or a second ChapterWorldRouter yet.

Extend the current model with:
- RouteId
- EpisodeId
- PlayableCharacterId

Example:
- RouteId = FrodoMain
- EpisodeId = P1C04_Main
- PlayableCharacterId = Frodo

Parallel example:
- RouteId = GandalfParallel
- EpisodeId = P1_Isengard_01
- PlayableCharacterId = Gandalf

Save data must preserve the main route independently from a parallel episode so an alternate character never overwrites Frodo's quest, chapter, position or story-beat state.

Only one heavy world/route should be active at a time.

## 10. Performance rules

For the target laptop:
- one active major region at a time
- use HISM/ISM for foliage and repeated props
- avoid large numbers of ticking actors
- keep active ambient NPC counts bounded
- share base character code and visual profiles
- use simple AI state machines before expensive behavior trees
- keep dynamic shadow-casting lights limited
- use LODs and cull distances
- DX11-safe effects only
- no UE5-only systems
- preserve 720p/30 FPS as the floor

## 11. Immediate story priorities

1. Finish The Shire vertical slice visually and validate it in UE4.27.
2. Correct the Part I chronology around Gandalf's departure and Ring investigation.
3. Add a Gandalf / Isengard parallel route as the first true multi-character story branch.
4. Expand Rivendell into a hub with the missing Fellowship characters and relationships.
5. Add Crebain and Fellowship camp beats before Caradhras.
6. Add Watcher + Orc/Cave Troll escalation to Moria.
7. Add Mirror of Galadriel and meaningful Lothlorien exploration.
8. Expand Amon Hen so the end of Part I cleanly creates the three major Part II routes.

## 12. Research basis

This document is a paraphrased design reference. It intentionally does not copy screenplay dialogue.

Research cross-checks used:
- Tolkien Gateway entries for the Fellowship, the Peter Jackson film plots, Moria, the Watcher in the Water, Lothlorien / Mirror material and related locations.
- The Encyclopedia of Arda Movie-goer's Guides for differences between Tolkien's books and the Peter Jackson films.
- Current runtime source on the develop branch of this repository.

The project should continue to re-check canon before implementing each chapter rather than relying on memory.
