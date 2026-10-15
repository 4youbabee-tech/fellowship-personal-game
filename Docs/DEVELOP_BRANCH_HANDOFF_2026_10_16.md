# Shire Journey — safe develop programmer handoff and branch hygiene (2026-10-16)

Canonical integration: develop. Stable release: main. Runtime PES-002 ACTIVE. Do not open PES-003.

## Actually merged and validated
- PR #477 PES-002 at commit d473c234d858ca5590a230e55a4f094b25ba49d3: Pre-Unreal Run 38818365177 SUCCESS; UE4.27 Run 38818365146 SUCCESS. Squashed on develop as 386a2968954ea6423ae37da011b35ef187f53849.
- Do not conflate a passing Windows C++/import/startup/render validation with human visuals, full traversal, PIE or measured 720p 30 FPS.

## Legacy source audit and preservation
- Before cleanup, 49 refs existed: 47 noncanonical feature/legacy heads and 24 open PRs. After #477 and its successful built-in Branch Cleanup: 46 refs and 23 open PRs.
- The 43 remaining historical working refs have been losslessly captured under archive/pre-build-salvage-20260930 at **5ca617729e359249e09aa6acc05734e814c594c4**. The commit lists 43 direct parents (one old archive parent and 42 distinct source heads), with every branch/SHA and former open PR number in Archive/BranchHygieneHeads_2026-10-16.json.
- THESE 43 HISTORICAL HEADS ARE NOT MERGED INTO DEVELOP. Particularly old C++ dialogue/NPC/cinematic branches and more advanced world/character/prep branches have not passed current exact-HEAD compile/PIE/visual gates. Blind Git merging them would risk overwriting newer PBR, governance or Unreal C++ code.
- The administrative cleanup may delete a historical branch **name only** if its source commit exists as an exact direct parent of the immutable archive SHA, current branch head still matches recorded SHA, and no open PR points to it. SHA movement or unverifiable ancestry blocks deletion. The archive itself remains protected.
- To recover a single historical improvement, locate branch and SHA in the archive manifest, read old file diff against current develop, cherry-pick/port the needed logic in the currently governed PES wave with regression tests, exact-HEAD Pre-Unreal and real UE4 verification, and only then merge.
- Current initial source PRs include stale preproduction-only and legacy runtime candidates. Their unmerged history stays recoverable from this archive; closing historical PRs is not equivalent to accepting or merging them.

## Source of truth and download
- URL to send a programmer after consolidation: https://github.com/4youbabee-tech/fellowship-personal-game/archive/refs/heads/develop.zip . This is a moving branch archive: verify downloaded SHA against GitHub develop ref when sending.
- Data/ProjectGovernor.json, Docs/DEVELOPMENT_GATES.md, Docs/PES_PRODUCTION_EXECUTION_SESSIONS.md, CURRENT_PROJECT_STATE.md and PRODUCTION_COMPLETENESS_MATRIX.md define the runtime and evidence gates.
