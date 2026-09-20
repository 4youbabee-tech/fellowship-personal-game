# Character surface parity wave

Base: develop `c929ab657dba10266536d51aa04fb21da04ada12`.
Pre-Unreal #504 (35534129087) succeeded. Unreal #339 (35534128972) attempt 2 succeeded after attempt 1 was interrupted. No compiler defect was established by that interruption.

The integrated NPC implementation already uses M_ProductionSurface. The playable modular character still used BasicShapeMaterial, so switching between player and companion exposed inconsistent surface response. This wave reuses the existing master for the player, assigns roughness/metallic for skin, cloth, hair, eyes, boots, gear and weapons, and fixes companion secondary blades, wizard beards and circlets. Hobbit feet use the skin palette. Legolas's bow and Gandalf's staff use nonmetallic wood. Authored skeletal rig materials are unaffected.

The runtime state audit now reads the actual player skin/cloth instances and their master path and parameters before proceeding to the existing disk save roundtrip. This prevents a basic-material fallback from silently satisfying the surface checks. The shared material directory is included in cooking; this is not proof of a packaged-game run.

Source guidance: the supplied 3D Visual Asset Atlas pages 1–2 require canon/reference priority and costume/gear/material-response review. It is a modeling aid, not authority to change film outcomes. No story, mission, save format, or timeline change is introduced.

Validation for this new source wave remains pending until its own Pre-Unreal and Unreal runs finish. Rendered quality and 30 FPS are unverified. Composite weapons still use one surface per component; final textures, rigs and animations remain separate production work. After this short wave, continue priority chapter art from current develop, avoiding duplication: minecarts, docks and P1C08 atmosphere are already integrated.
