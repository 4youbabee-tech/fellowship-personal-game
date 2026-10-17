"""Enable official MPFB2 as Blender extension; install only the verified CC0 system pack."""
import argparse
import importlib
from pathlib import Path
import runpy
import sys

# Blender --python does not add this file's directory to sys.path.
# Resolve siblings from the script, independently of the working directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from mpfb_pack_intake import extract_verified_pack
import json

import bpy


def main():
    if "--" not in sys.argv:
        raise RuntimeError("MPFB_HOSTED_BLENDER_ARGS_MISSING")
    parser = argparse.ArgumentParser()
    parser.add_argument("--extension", type=Path, required=True)
    parser.add_argument("--system-pack", type=Path)
    parser.add_argument("--spec", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--probe-only", action="store_true")
    cfg = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    required_inputs = ("extension",) if cfg.probe_only else ("extension", "system_pack", "spec")
    for key in required_inputs:
        if not getattr(cfg, key).is_file():
            raise RuntimeError("MPFB_INPUT_MISSING_" + key)
    # Blender 4.2 background sessions have no extension repository selected.
    # This is the actual root cause of Run #38979644601: "Repository not set".
    # Create one local-only repo for this ephemeral hosted worker (no remote sync).
    repos = bpy.context.preferences.extensions.repos
    matches_local = [r for r in repos if r.name == "Shire MPFB Offline"]
    if not matches_local:
        created = bpy.ops.preferences.extension_repo_add(
            name="Shire MPFB Offline", type="LOCAL", use_sync_on_startup=False)
        if "FINISHED" not in created:
            raise RuntimeError("MPFB_LOCAL_EXTENSION_REPOSITORY_CREATE_FAILED")
        matches_local = [r for r in repos if r.name == "Shire MPFB Offline"]
    if len(matches_local) != 1 or not matches_local[0].module:
        raise RuntimeError("MPFB_LOCAL_EXTENSION_REPOSITORY_UNRESOLVED")
    repo_id = matches_local[0].module
    print("PES002_MPFB_LOCAL_REPOSITORY_READY id=" + repo_id, flush=True)
    ret = bpy.ops.extensions.package_install_files(
        filepath=str(cfg.extension.resolve()), repo=repo_id, enable_on_install=True)
    if "FINISHED" not in ret:
        raise RuntimeError("MPFB2_OFFICIAL_EXTENSION_INSTALL_FAILED")
    matches = [k for k in bpy.context.preferences.addons.keys()
               if k.endswith(".mpfb") or k == "mpfb"]
    if len(matches) != 1:
        raise RuntimeError("MPFB2_EXTENSION_ENABLE_MISSING " + repr(matches))
    module = matches[0]
    # Probe the installed MPFB service exports before the expensive core pack.
    importlib.import_module(module + ".services.humanservice")
    importlib.import_module(module + ".services.exportservice")
    print("PES002_MPFB2_EXTENSION_API_READY addon=" + module, flush=True)
    if cfg.probe_only:
        print("PES002_MPFB_INSTALL_PROBE_PASS source_only=1 core_pack_not_downloaded=1", flush=True)
        return
    loc = importlib.import_module(module + ".services.locationservice").LocationService
    destination = Path(loc.get_user_data()).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    # The official pack stores skins and meshes in named subdirectories:
    # skins/young_caucasian_male/young_caucasian_male.mhmat, not skins/file.
    # Keep those directories intact so MHMAT and MHCLO texture references work.
    spec = json.loads(cfg.spec.read_text(encoding="utf-8"))
    required = [("skins", spec["skin"])]
    required.extend((part["subdir"], part["name"]) for part in spec["parts"])
    written, total_bytes = extract_verified_pack(
        cfg.system_pack.resolve(), destination, required)
    AssetService = importlib.import_module(
        module + ".services.assetservice").AssetService
    for sub, name in required:
        resolved = AssetService.find_asset_absolute_path(name, asset_subdir=sub)
        if not resolved or not Path(resolved).is_file():
            raise RuntimeError("MPFB_SERVICE_CANNOT_RESOLVE_REQUIRED_ASSET " + sub + "/" + name)
        if not Path(resolved).resolve().is_relative_to(destination):
            raise RuntimeError("MPFB_ASSET_RESOLVED_OUTSIDE_APPROVED_PACK " + sub + "/" + name)
    print("PES002_MPFB_CORE_PACK_TREE_READY files=" + str(written) +
          " uncompressed_bytes=" + str(total_bytes) +
          " required=" + str(len(required)), flush=True)
    print("MPFB2_HOSTED_BLENDER_VERIFIED addon=" + module +
          " files=" + str(written), flush=True)
    script = Path(__file__).with_name("prepare_mpfb_hobbit_candidate.py").resolve()
    sys.argv = [str(script), "--", "--spec", str(cfg.spec), "--out", str(cfg.out)]
    runpy.run_path(str(script), run_name="__main__")


if __name__ == "__main__":
    main()
