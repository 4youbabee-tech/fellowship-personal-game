#!/usr/bin/env python3
"""Static player-journey gap audit; never claim PIE, device, or visual acceptance."""
import argparse
import json
import re
from pathlib import Path


def inspect(root):
    root = Path(root)
    player = (root / "Source/ShireJourney/Private/Characters/ShirePlayerCharacter.cpp").read_text()
    world = (root / "Source/ShireJourney/Private/World/ShireWorldEventInteraction.cpp").read_text()
    quest = (root / "Source/ShireJourney/Private/Subsystems/ShireQuestSubsystem.cpp").read_text()
    route_files = list((root / "Source/ShireJourney/Private").rglob("*.cpp"))
    # A door actor must be a real runtime behavior with persistent state, not a FBX named RoundDoor.
    door_files = [p.relative_to(root).as_posix() for p in route_files
                  if re.search(r"door|hinge", p.stem, re.IGNORECASE)]
    assert "void AShirePlayerCharacter::Interact()" in player
    assert "LineTraceSingleByChannel" in player
    assert "GetCurrentChapterId()" in world
    assert "ShireArrival" in quest and "FerryEscape" in quest
    assert "CreateSaveSnapshot" in player
    alerts = "ShowAlert(PromptText" in world and "ShowAlert(ResponseText" in world
    findings = [
        {
            "id": "P1C01-DOOR-INTERACTION",
            "status": "UNPROVEN_MISSING_NATIVE_IMPLEMENTATION" if not door_files else "REQUIRES_RUNTIME_PROOF",
            "severity": "high",
            "evidence": "Native door/hinge C++ filenames: " + repr(door_files),
            "acceptance": "Door hinge pivot, timed state transition, input distance, collision while opening, obstruction/AI navigation and save/reload in PIE",
        },
        {
            "id": "P1C01-ALERT-ORDER",
            "status": "STATIC_RISK" if alerts else "REVIEW",
            "severity": "medium",
            "evidence": "World event interaction calls prompt and response ShowAlert sequentially in one Interact invocation",
            "acceptance": "Prompt must not be overwritten by response before player can read it; validate HUD timing",
        },
        {
            "id": "P1C01-FERRY-COLLISION",
            "status": "ENGINE_RETEST_REQUIRED",
            "severity": "high",
            "evidence": "Cloud138 UE4 intake #38302410362 failed on SM_ShFerryLanding simple collision; corrective PR #435 under review",
            "acceptance": "UE4 package reimport, persisted collider, traversable ferry walk path, AI NavMesh and chapter-specific PIE",
        },
        {
            "id": "P1C01-SAVE-RESTORE",
            "status": "STATIC_PATH_PRESENT_NOT_PLAY_ACCEPTED",
            "severity": "high",
            "evidence": "Player snapshot method exists; per-door open state persistence not evidenced",
            "acceptance": "Load inside/outside houses, after event, and at ferry; verify identical world and quest state",
        },
        {
            "id": "P1C01-FPS-VRAM",
            "status": "DEVICE_EVIDENCE_REQUIRED",
            "severity": "high",
            "evidence": "Source inspection cannot measure DX11 720p GPU frame times or 2GB VRAM",
            "acceptance": "Actual i7 6th gen / approximately 2GB VRAM device capture with measured FPS, VRAM and representative full route",
        },
    ]
    return {
        "schema_version": 1,
        "mode": "STATIC_GAP_AUDIT_ONLY",
        "area": "P1C01 Bag End to Bucklebury Ferry",
        "source_files_reviewed": 4,
        "runtime_door_cpp_files": door_files,
        "findings": findings,
        "gate6_closed": False,
        "gate7_closed": False,
        "pie_tested": False,
        "device_tested": False,
        "visually_accepted": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = inspect(args.root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print("P1C01_STATIC_PLAYER_JOURNEY_AUDIT_PASS findings=%d doors_native=%d gate67=OPEN" %
          (len(report["findings"]), len(report["runtime_door_cpp_files"])))


if __name__ == "__main__":
    main()
