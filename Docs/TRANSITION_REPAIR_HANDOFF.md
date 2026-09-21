# World transition coordination repair

Base: develop f4886b39feea29973543bf6cfb1be4659f10ff9d.
Branch: repair/world-transition-coordination-v1. PR #62 remains separate; do not overwrite it.

The router now publishes a world revision after building the destination and placing the player.
LivingWorldDirector only resets residents, weather and micro-events when that revision matches
the quest chapter/route/episode. During pending streaming it preserves existing life and suspends
director updates. Returning to the resident world does not manufacture a new revision.

The state CI stage also runs a fresh continuous-session audit: rapid chapter return, all eight
chapters, Gandalf/Frodo roundtrip and isolated disk save/restore, checking router/director agreement.
This audit does not force a delayed load and does not yet prove saving while a load is pending.
It does not certify rendered visuals, frame rate or long-session memory behavior.

At session start run `python Scripts/live_governor_status.py` with read-only GH_TOKEN/GITHUB_TOKEN.
It reads develop and open PRs, selects exact-SHA workflow evidence and rechecks heads for concurrent
movement. It never commits CI results. A missing workflow is NOT_OBSERVED, not green.
This is a read-time refresh tool, not an installed background updater. The static governor remains
the requirements/decision register; its evidence snapshots are historical, not current live status.

Remaining work: pending-save safety/audit, bounded offscreen crowd retirement, narrower ownership
of chapter cleanup, and scheduled publication of live status. Compare PR #62 before integrating.
