# PIE / DEVICE VERIFICATION RECORD — 2026-09-19

## Baseline

- Branch: `develop`
- Historical merged baseline: `f7c2b081e7b064fcf27bb4c80124b21f351331ab`
- Engine: Unreal Engine 4.27.2
- Target profile: Windows / DX11 / 1280x720 / Low-Medium

## Correction

The project owner did confirm in conversation that the earlier check/fix phase was complete and that construction could resume. That statement is retained as **historical production authorization only**.

It is **not** sufficient evidence to mark P1C01-P1C08 as `PIE_TESTED`, because the record contains no chapter-specific FPS measurement, screenshot/video reference, or concrete observation unique to each chapter. Repeating the same generic sentence across eight chapters is no longer accepted as proof.

## Valid machine evidence on the historical baseline

- Pre-Unreal Validation #264: PASS
- Unreal Build Validation #99: PASS
- UE4.27.2 C++ build: PASS
- production asset import: PASS
- playable startup smoke: PASS
- headless P1C01-P1C08 chapter audit: PASS
- runtime warning-debt guard: PASS

These checks prove machine/build/runtime conditions only. They do not prove human PIE traversal, visuals, target-device FPS, hitching, memory behavior, or chapter-specific presentation quality.

## Required evidence for future chapter promotion

A chapter may enter `PIE_TESTED` or `PIE_TESTED_WITH_ISSUES` only when its exact tested commit is recorded and at least one of the following exists for that chapter:

- an actual numeric FPS observation;
- a screenshot or video reference;
- a concrete chapter-specific observation that is not copied across chapters.

Two concrete observed details remain required. Generic conversation sign-off cannot satisfy this rule.

## Production direction

Construction continues behind static, build/import and runtime regression gates. Shire should be re-established first as the visual/performance reference with chapter-specific evidence; the same evidence pattern can then be applied to Bree through Amon Hen. Film chronology and required outcomes remain above optional gameplay additions.
