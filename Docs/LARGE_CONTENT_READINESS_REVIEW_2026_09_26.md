# Large-content readiness review - 2026-09-26

Reviewed source: `7a31d40902bddb27ef752dbf48e11540ce0f95a8` (PR90), not merged develop.

Verdict: the existing architecture supports staged intake and representative chapter batches. Unrestricted large-scale runtime promotion is not yet proven. No evidence in this review justifies replacing the engine, chapter router, or existing intake system.

## Existing foundation verified in source

- ChapterAssetStreamingSubsystem owns asynchronous soft-path banks, cancels stale requests, retains the visible bank until destination commit, and checks unresolved assets before ready publication.
- Character rig callbacks hand ownership to actor components and release completed request handles.
- ChapterAssetStreamingPlan separates chapter banks. WholeGameStreamingResidencyPlanV1 describes active-region and bounded transition overlap, but explicitly remains preparation rather than whole-game acceptance.
- AssetPerformanceBudget requires measured baselines and already describes HISM/cull rules. No fabricated hard memory or triangle limits were added.
- P1C01WorldBuildIntakePacketV1 and PrivateOfflineAssetIntakeQueueV1 already provide staging, QC and promotion states; reuse them rather than creating duplicate inventories.
- Git LFS covers uasset/umap/FBX/WAV/PNG/EXR. TGA is absent from the inspected attributes; review actual TGA growth and existing tracked history before a separate LFS migration. No history rewrite performed.

## Repair implemented

The static asset audit read every PNG/TGA into memory merely to inspect its dimensions. It now reads 24 header bytes and obtains the actual source size from the open file descriptor. The OBJ parser now iterates input lines instead of retaining a complete source-text/line copy alongside parsed topology. Validation rules and strict failure behavior remain intact.

Three regression tests cover a 64 MiB sparse texture with a reader that rejects reads over 24 bytes, truncated PNG failure, and valid/invalid OBJ face behavior while disallowing whole-file text reads. They run in Pre-Unreal. This is a tooling memory improvement, not a game FPS claim. OBJ vertices/normals/UVs/faces still require memory proportional to topology. Header validation is not full image decoding or Unreal import validation.

## Remaining work before dense runtime content

1. Resolve the recorded rendered packaged-startup D3D11 failure (CI-REC-003). Verify supervised interactive execution on the device; do not substitute headless success for rendered acceptance.
2. Continue the existing P1C01 order: C2 proof/integration, C3 material identity, C4 LOD/cull/overdraw, then lighting and subsequent presentation/living-world steps. Staging and source QC can proceed while runtime proof is pending.
3. Capture exact SHA, scene/route, settings, frame time, hitches, texture pool and CPU/GPU memory on the target laptop. Include source/destination overlap during transitions and repeated travel away/back to detect residency accumulation.
4. Promote representative items through existing QC: material slots, collision, LOD/cull, mip behavior, skeleton/retargeting where applicable, cook inclusion and runtime reference resolution. A successful source audit alone cannot certify these.
5. Increase one content category per measured batch; compare against the preceding capture and retain a reversible commit. Keep unpromoted high-resolution sources in staging, outside active runtime banks.

## Source and evidence boundary

Source 00 advocates a complete vertical slice before world expansion. Source 11 sections 8-9 require measured performance, memory and streaming QA, and supersede the old claim that the ROTK screenplay is unavailable. These references support the existing measured-batch approach; they do not establish numeric device capacity.

This was a focused source/pipeline review, not an exhaustive audit of every subsystem or a UE/device stress test. The local checks passed; exact-head CI is pending. No guarantee of zero future stalls is made. ProjectGovernor records the finding and resume point so an interrupted conversation does not lose it.
