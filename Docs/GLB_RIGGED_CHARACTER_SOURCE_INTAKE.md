# GLB licensed rig to UE4.27 (source-only, no runtime PES transition)

Use the Blender 2.93+ script `Tools/CloudAssetBuild/convert_licensed_glb_rig_to_ue427_fbx.py` only for a physically downloaded file with confirmed CC0/Public Domain origin and a JSON receipt containing `source_url`, `creator`, `license`, `source_filename` and exact `source_sha256`. Do not scrape Tripo/Discord/Mixamo account pages, bypass paywalls or assume private-use permission overrides third-party license limitations.

Example offline invocation (replace placeholders with **actually held** files):

```sh
blender -b --python Tools/CloudAssetBuild/convert_licensed_glb_rig_to_ue427_fbx.py -- --glb Source.glb --manifest Source.license.json --output Saved/GLBStaging --require-clips
```

The script checks an actual deform armature, weighted vertices, up to four normalized influences, UVs, 2K max source textures and 65K triangle cap. `--require-clips` needs authored Idle, Walk and Turn action names. It exports a Skeletal FBX plus SHA receipt in Saved; no GLB is fetched and no runtime import occurs just from running this script.

After receipt: verify root scale/orientation, live source licenses, per-limb deformation, UE4.27 Skeleton, AnimSequences and BlendSpace, turning and interactions, and target 720p FPS/VRAM. Only thereafter may a real named character replace a modular NPC in its formally opened PES. In current scope, **PES-002 exterior is active, character PES-009/PES-011 and Bag End interior PES-003 are locked**. This file is implementation guidance only, not a secondary Governor.
