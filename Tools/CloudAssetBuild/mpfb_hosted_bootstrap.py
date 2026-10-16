"""Enable official MPFB2 as Blender extension; install only the verified CC0 system pack."""
import argparse
import importlib
from pathlib import Path, PurePosixPath
import runpy
import shutil
import sys
import zipfile

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
    asset_dirs = {"skins", "clothes", "hair", "eyes", "eyebrows",
                  "eyelashes", "tongue", "teeth", "proxymeshes",
                  "expressions", "poses", "rigs", "targets", "materials"}
    written = 0
    total_bytes = 0
    with zipfile.ZipFile(cfg.system_pack.resolve()) as archive:
        for record in archive.infolist():
            if record.is_dir():
                continue
            pieces = PurePosixPath(record.filename).parts
            if ".." in pieces or record.filename.startswith("/"):
                raise RuntimeError("MPFB_ZIP_TRAVERSAL")
            offsets = [i for i, v in enumerate(pieces) if v in asset_dirs]
            if not offsets:
                continue
            relative = Path(*pieces[offsets[0]:])
            target = (destination / relative).resolve()
            if not target.is_relative_to(destination):
                raise RuntimeError("MPFB_UNSAFE_ZIP_TARGET")
            total_bytes += record.file_size
            if record.file_size > 100_000_000 or total_bytes > 1_000_000_000:
                raise RuntimeError("MPFB_ZIP_SIZE_LIMIT")
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(record) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            written += 1
    for sub, name in (
        ("skins", "young_caucasian_male.mhmat"),
        ("eyes", "low-poly.mhclo"),
        ("hair", "short01.mhclo"),
        ("clothes", "male_casualsuit01.mhclo"),
    ):
        if not (destination / sub / name).is_file():
            raise RuntimeError("MPFB_CORE_ASSET_PACK_MISSING " + sub + "/" + name)
    if written < 50:
        raise RuntimeError("MPFB_INCOMPLETE_SYSTEM_ASSET_PACK")
    print("MPFB2_HOSTED_BLENDER_VERIFIED addon=" + module +
          " files=" + str(written), flush=True)
    script = Path(__file__).with_name("prepare_mpfb_hobbit_candidate.py").resolve()
    sys.argv = [str(script), "--", "--spec", str(cfg.spec), "--out", str(cfg.out)]
    runpy.run_path(str(script), run_name="__main__")


if __name__ == "__main__":
    main()
