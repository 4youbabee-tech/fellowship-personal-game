# P1C01 Visual Economy and Graphics/Video Settings

## Scope

This is a P1C01-only source increment under W01_P1C01_PRODUCTION_VERTICAL_SLICE. It does not open later runtime chapters and it does not claim compile, PIE, device, visual, or performance acceptance.

## Permanent visual-economy doctrine

Spend first on what the player can actually see and remember: silhouette, composition, hero materials, lighting, atmosphere, landmark framing, near-field surface detail, and readable character presentation. When the target budget is threatened, recover cost first from duplicate actors, far shadows, overdraw/translucency, redundant lights, uninstanced repetition, unnecessary Tick, and invisible or far detail.

The protected floor remains DX11 at 1280x720, Low-Medium class settings, and a 30 FPS target on the established low-spec laptop profile. Higher presets are opt-in quality headroom; they never redefine the floor.

## Presets

- Performance: lowest shadow/view/effects/foliage tiers, low texture tier, 85 percent render scale. Emergency headroom.
- Cinematic Balanced: default. Medium view/shadow/post/effects/foliage, higher anti-aliasing, medium texture, 100 percent render scale. This is the visually strong target-laptop starting point.
- High: quality level 2 across the major scalability groups at 100 percent render scale.
- Ultra: quality level 3 across the major scalability groups at 100 percent render scale. Opt-in only; not part of low-spec acceptance.
- Custom: independent quality controls for view distance, anti-aliasing, shadows, post-processing, textures, effects, foliage, and render scale.

Display controls cover resolution, Fullscreen/Borderless/Windowed, VSync, and frame-rate limit. The runtime API is Blueprint-callable so a polished UMG settings surface can consume one authoritative backend instead of duplicating console-variable logic.

## Cost ordering encoded in scalability

The project scalability file keeps texture-pool authority in TextureQuality, sharply bounds shadow distance/cascade cost at lower tiers, scales foliage density before hero composition is sacrificed, and reduces expensive translucency/refraction/SSR work before higher presets add them back.

## Evidence boundary

Source architecture, config, and hosted static contract checks can prove that the settings backend is coherent. They cannot prove target-device FPS, VRAM, hitching, image quality, or visual acceptance. Those remain exact-head Unreal/device/human gates.
