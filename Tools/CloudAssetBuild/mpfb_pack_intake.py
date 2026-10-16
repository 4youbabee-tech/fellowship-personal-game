"""Offline, Blender-independent extraction of the official MakeHuman CC0 asset pack.

MakeHuman archives keep assets in category/asset-name/filename trees. Never
flatten that tree: MH material files refer to textures relative to their folder.
"""
from pathlib import Path, PurePosixPath
import shutil
import stat
import zipfile

ASSET_CATEGORIES = frozenset({
    "skins", "clothes", "hair", "eyes", "eyebrows", "eyelashes",
    "tongue", "teeth", "proxymeshes", "expressions", "poses", "rigs",
    "targets", "materials", "packs",
})
MAX_FILES = 50000
MAX_UNCOMPRESSED_BYTES = 1_000_000_000
MAX_SINGLE_BYTES = 100_000_000


def relative_asset_path(filename):
    """Return a safe category-prefixed path, removing only outer ZIP prefixes."""
    if not filename or filename.startswith("/") or "\\" in filename:
        raise RuntimeError("MPFB_UNSAFE_ZIP_NAME")
    parts = PurePosixPath(filename).parts
    if (".." in parts or any(":" in p for p in parts)
            or any(p in ("", ".") for p in filename.split("/"))):
        raise RuntimeError("MPFB_ZIP_TRAVERSAL")
    roots = [i for i, part in enumerate(parts) if part in ASSET_CATEGORIES]
    if not roots:
        return None
    relative = PurePosixPath(*parts[roots[0]:])
    if len(relative.parts) < 2:
        raise RuntimeError("MPFB_INVALID_ASSET_ENTRY")
    return relative


def extract_verified_pack(archive_path, destination, required_assets):
    """Check the complete archive, then extract it with unique safe target paths.

    required_assets: pairs of (category, filename), e.g.
    ('skins', 'young_caucasian_male.mhmat'); nested folders are supported.
    Does not claim that a Blender skin/pose/Unreal import has succeeded.
    """
    destination = Path(destination).resolve()
    wanted = []
    for category, basename in required_assets:
        if (category not in ASSET_CATEGORIES or not basename or
                Path(basename).name != basename):
            raise RuntimeError("MPFB_INVALID_REQUIRED_ASSET")
        wanted.append((category, basename))
    if len(set(wanted)) != len(wanted):
        raise RuntimeError("MPFB_DUPLICATE_REQUIRED_ASSET")

    planned = []
    seen = set()
    archive_bytes = 0
    with zipfile.ZipFile(archive_path) as archive:
        for info in archive.infolist():
            # Official archives include explicit category directory entries;
            # they are not files and need no target extraction.
            if info.is_dir():
                continue
            relative = relative_asset_path(info.filename)
            if relative is None:
                continue
            if stat.S_ISLNK(info.external_attr >> 16):
                raise RuntimeError("MPFB_ZIP_SYMLINK_REJECTED")
            canonical = relative.as_posix().casefold()
            if canonical in seen:
                raise RuntimeError("MPFB_DUPLICATE_ZIP_TARGET " + relative.as_posix())
            seen.add(canonical)
            archive_bytes += info.file_size
            if (len(planned) >= MAX_FILES or info.file_size > MAX_SINGLE_BYTES or
                    archive_bytes > MAX_UNCOMPRESSED_BYTES):
                raise RuntimeError("MPFB_ZIP_SIZE_LIMIT")
            planned.append((info, relative))

        # Exact basename in its own category, including nested named asset dirs.
        # Check uniqueness BEFORE writing; an absent outfit must not leave a
        # half-installed input that the next run mistakes for a complete pack.
        for category, name in wanted:
            matches = [path for _, path in planned
                       if path.parts[0] == category and path.name == name]
            if len(matches) != 1:
                raise RuntimeError("MPFB_CORE_ASSET_PACK_MISSING_OR_AMBIGUOUS " +
                                   category + "/" + name + " matches=" + str(len(matches)))
        if len(planned) < 50:
            raise RuntimeError("MPFB_INCOMPLETE_SYSTEM_ASSET_PACK")

        for info, relative in planned:
            target = (destination / Path(*relative.parts)).resolve()
            if not target.is_relative_to(destination):
                raise RuntimeError("MPFB_UNSAFE_ZIP_TARGET")
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as src, target.open("xb") as dst:
                shutil.copyfileobj(src, dst)
    return len(planned), archive_bytes
