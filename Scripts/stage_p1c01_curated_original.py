#!/usr/bin/env python3
"""Production-stage owner-original Shire meshes and packed PNG textures for UE4.27.

No UE editor invocation, asset activation, external license auto-approval, or source deletion.
This command accepts ONLY the SHA-pinned ten-archive curated source from PR #406.
It creates a source tree consumable by the existing ShireProductionImport commandlet,
separate authored LOD 1/2 inputs, and a full immutable receipt for a later editor pass.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import struct
import tempfile
import zipfile

CURATED_MANIFEST_SHA = '65ae0447840725746614220d8135a65c9b897ba8326d69c756cf5e1a50519b7b'
# The outer ZIP has variable entry timestamps across rebuilds; exact manifest bytes,
# per-asset SHA256, and ten exact original archive digests are the stable boundary.
IMPORT_REL = Path('SourceAssets/Production/World/Shire/CuratedP1C01')
LOD_REL = Path('Saved/P1C01CuratedLOD')
RECEIPT_REL = Path('Saved/P1C01CuratedStage/receipt.json')
EXTERNAL_LANES = ('PRIORITY_PBR', 'POLYHAVEN_PBR')
ORIGINAL_LANES = ('FOLIAGE_NATURE', 'SHIRE_ARCHITECTURE', 'REGIONAL_SURFACE_PREP')
FBX_MAGIC = b'Kaydara FBX Binary  \x00\x1a\x00'
PNG_MAGIC = b'\x89PNG\r\n\x1a\n'
HARD_COUNTS = {'FOLIAGE_NATURE': 63, 'SHIRE_ARCHITECTURE': 44,
               'REGIONAL_SURFACE_PREP': 36, 'PRIORITY_PBR': 12, 'POLYHAVEN_PBR': 108}

# Eight logical deliverable streams inside the Project Governor's five authorized lanes.
ARCH_HERO = {'BagEndFrontWall','RoundDoor','RoundWindow','RoundRoomFloor','RoundRoomWallArc','Hearth','HobbitBed','Bookcase'}
ARCH_VILLAGE = {'FarmGate','GardenCart','GardenHedge','GardenPlanter','LanternPost','PartyCanopy','PartyTable','PicketFence','StorageBarrel','VillageWell'}
ARCH_ROUTE = {'OakTree','MillWheel','StonePath','WoodenFootbridge'}
TREE_FAMILIES = {'tree_apple','tree_elm','tree_oak','tree_willow'}
DECORATIVE = {'flower_wild', 'garden_reed', 'grass_meadow', 'shrub_gorse', 'shrub_hawthorn', 'shrub_hedge'}


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_file(path: Path) -> str:
    d = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            d.update(block)
    return d.hexdigest()


def safe_zip_name(name: str) -> str:
    if not isinstance(name, str) or not name or '\\' in name or '\x00' in name or ':' in name:
        raise ValueError('UNSAFE_ZIP_MEMBER')
    obj = PurePosixPath(name)
    if obj.is_absolute() or '..' in obj.parts or len(obj.parts) > 10:
        raise ValueError('UNSAFE_ZIP_MEMBER')
    if str(obj) != name:
        raise ValueError('NON_CANONICAL_ZIP_MEMBER')
    return name


def validate_fbx(raw: bytes) -> None:
    if len(raw) < len(FBX_MAGIC) + 4 or not raw.startswith(FBX_MAGIC):
        raise ValueError('BINARY_FBX_REQUIRED')
    version = struct.unpack('<I', raw[len(FBX_MAGIC):len(FBX_MAGIC) + 4])[0]
    if version != 7400:
        raise ValueError('FBX_VERSION_MUST_BE_7400')


def validate_png(raw: bytes) -> tuple[int, int]:
    if len(raw) < 33 or not raw.startswith(PNG_MAGIC) or raw[12:16] != b'IHDR':
        raise ValueError('BAD_PNG_HEADER')
    w,h,depth,mode,*_ = struct.unpack('>IIBBBBB', raw[16:29])
    if not (0 < w <= 1024 and 0 < h <= 1024 and depth in (8, 16) and mode in (0,2,3,4,6)):
        raise ValueError('TEXTURE_BUDGET_OR_FORMAT')
    return (w,h)


def texture_kind(name: str) -> str:
    if name.endswith('_BaseColor.png'):
        return 'BaseColor'
    if name.endswith('_NormalDX.png'):
        return 'NormalDX'
    if name.endswith('_ORM.png'):
        return 'ORM'
    raise ValueError('UNSUPPORTED_PBR_TEXTURE_SUFFIX')


def logical_track(row: dict) -> str:
    lane, name = row['lane'], row['dest']
    if lane == 'FOLIAGE_NATURE':
        if name.lower().endswith('.png'):
            return 'L05_ORIGINAL_SURFACES'
        family = re.sub(r'^SM_Sh_', '', Path(name).stem).rsplit('_LOD', 1)[0]
        return 'L01_TREES' if family in TREE_FAMILIES else 'L02_GROUND_AND_FOLIAGE'
    if lane == 'SHIRE_ARCHITECTURE':
        family = row['family']
        if family in ARCH_HERO:
            return 'L03_BAG_END_HERO_ARCH'
        if family in ARCH_VILLAGE:
            return 'L04_HOBBITON_VILLAGE_PROPS'
        if family in ARCH_ROUTE:
            return 'L06_ROAD_AND_FERRY_PROPS'
        raise ValueError('ARCH_FAMILY_UNCLASSIFIED:' + family)
    if lane == 'REGIONAL_SURFACE_PREP':
        return 'L05_ORIGINAL_SURFACES'
    raise ValueError('EXTERNAL_CANNOT_ENTER_ORIGINAL_TRACK')


def approved_original(row: dict) -> bool:
    claims = {
        'FOLIAGE_NATURE': 'ORIGINAL_PROJECT_PROCEDURAL',
        'SHIRE_ARCHITECTURE': 'ORIGINAL_PROJECT_PROCEDURAL',
        'REGIONAL_SURFACE_PREP': 'ORIGINAL_PROJECT_ASSET',
    }
    return (row.get('lane') in ORIGINAL_LANES
            and row.get('license_claim_from_embedded_receipt') == claims[row['lane']]
            and row.get('licensed_runtime_approved') is False
            and row.get('unreal_imported') is False)


def atomic_bytes(path: Path, value: bytes, project_root: Path) -> str:
    root = project_root.resolve()
    resolved = path.resolve()
    if root not in resolved.parents:
        raise ValueError('STAGING_ESCAPES_WORKSPACE')
    if path.exists():
        if path.is_symlink() or sha_file(path) != sha_bytes(value):
            raise ValueError('EXISTING_GENERATED_STAGE_CONFLICT:' + str(path))
        return 'REUSED_IDENTICAL'
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.stage-', delete=False) as tmp:
        tmp.write(value)
        temp = Path(tmp.name)
    try:
        if path.exists():
            raise ValueError('UNEXPECTED_CONCURRENT_STAGE_WRITER')
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)
    return 'WRITTEN'


def bound_file_rows(manifest: dict, names: set[str]) -> list[dict]:
    if (manifest.get('chapter') != 'P1C01' or
        manifest.get('scope') != 'SOURCE_ONLY_NOT_UNREAL_IMPORTED' or
        manifest.get('engine_imported') is not False or
        manifest.get('gate6_7_closed') is not False or
        manifest.get('counts_by_lane') != HARD_COUNTS or
        manifest.get('logical_asset_bindings') != 263 or
        manifest.get('curated_physical_file_count') != 230 or
        manifest.get('deduplicated_alias_count') != 33):
        raise ValueError('CURATED_MANIFEST_CONTRACT_CHANGED')
    rows = manifest['asset_files']
    if len(rows) != 263 or len({x['dest'] for x in rows}) != len(rows):
        raise ValueError('CURATED_BINDING_INVALID')
    accounted = set()
    for row in rows:
        name = safe_zip_name(row['dest'])
        resolved = safe_zip_name(row.get('alias_of', name))
        if not re.fullmatch(r'[0-9a-f]{64}', row.get('sha256', '')) or row.get('bytes', 0) <= 0:
            raise ValueError('INVALID_SHA_OR_SIZE:' + name)
        if resolved not in names or row.get('lane') not in HARD_COUNTS:
            raise ValueError('MISSING_OR_UNEXPECTED_ASSET:' + name)
        accounted.add(resolved)
        if row.get('lane') in ORIGINAL_LANES and not approved_original(row):
            raise ValueError('ORIGINAL_RIGHTS_CONTRACT_CHANGED:' + name)
    if len(accounted) != 230:
        raise ValueError('CURATED_UNIQUE_FILE_COUNT_DRIFT')
    return rows


def stage_archive(archive: Path, workspace: Path, source_only: bool=True) -> dict:
    """Build importer-ready verified source without invoking UE4. Editors require separate Gates."""
    workspace = workspace.resolve()
    source_root = workspace / IMPORT_REL
    lod_root = workspace / LOD_REL
    expected_paths: dict[str, str] = {}
    mesh = defaultdict(dict)
    material = defaultdict(dict)
    cases = defaultdict(list)
    actions = Counter()
    inventory = []
    staging_bytes = []
    outside = []
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError('CURATED_ARCHIVE_CRC_FAILURE')
        names = set(z.namelist())
        for file in z.infolist():
            safe_zip_name(file.filename)
            if file.flag_bits & 1 or file.is_dir():
                raise ValueError('UNEXPECTED_ZIP_MEMBER')
        if len(names) != 232 or 'AssetManifest.json' not in names or 'IMPORT_NOTES.txt' not in names:
            raise ValueError('CURATED_ZIP_MEMBER_COUNT_CHANGED')
        manifest_raw=z.read('AssetManifest.json')
        if sha_bytes(manifest_raw) != CURATED_MANIFEST_SHA:
            raise ValueError('CURATED_MANIFEST_SHA256_MISMATCH')
        manifest = json.loads(manifest_raw)
        rows = bound_file_rows(manifest, names)
        for row in sorted(rows, key=lambda r:r['dest']):
            name = row['dest']; lane = row['lane']
            resolved = row.get('alias_of', name)
            raw = z.read(resolved)
            if len(raw) != row['bytes'] or sha_bytes(raw) != row['sha256']:
                raise ValueError('SOURCE_FILE_CORRUPTED:' + name)
            if lane in EXTERNAL_LANES:
                outside.append({'source':name, 'reason':'EXTERNAL_LICENSE_REVIEW_REQUIRED',
                                'source_sha256':row['sha256'], 'source_page':row.get('source_page')})
                continue
            if not approved_original(row):
                raise ValueError('ONLY_PROJECT_OWNED_SOURCE_ALLOWED')
            original = Path(name)
            if original.suffix.lower() == '.fbx':
                validate_fbx(raw)
                lod_match = re.fullmatch(r'(.+)_LOD([012])', original.stem)
                if not lod_match:
                    raise ValueError('FBX_MISSING_EXPLICIT_LOD')
                stem,lod = lod_match.group(1),int(lod_match.group(2))
                category = ('Nature' if lane=='FOLIAGE_NATURE' else 'Architecture')
                key = category + '/' + stem
                if lod in mesh[key]:
                    raise ValueError('DUPLICATE_LOD_INDEX:' + key)
                if lod == 0:
                    target = source_root / name
                    import_mode = 'UE4_COMMANDLET_BASE_STATIC_MESH'
                else:
                    target = lod_root / name
                    import_mode = 'UE4_EDITOR_LOD_ONLY_NOT_SEPARATE_MESH'
                mesh[key][lod] = {'source_file':name,'sha256':row['sha256'], 'absolute_path':str(target),
                                  'import_mode':import_mode}
            elif original.suffix.lower() == '.png':
                dim=validate_png(raw)
                target=source_root/name
                kind=texture_kind(name)
                if lane=='FOLIAGE_NATURE':
                    family=original.stem.rsplit('_',1)[0]
                    namespace='Nature'
                else:
                    family=row['material_family']
                    namespace='Regional'
                key=namespace + '/' + family
                if kind in material[key]:
                    raise ValueError('DUPLICATE_MATERIAL_MAP:' + key)
                material[key][kind]={'source_file':name,'sha256':row['sha256'],
                                    'size':list(dim),'asset_path':'/Game/Production/World/Shire/CuratedP1C01/' + str(original.with_suffix('')).replace('\\','/'),
                                    'srgb':kind=='BaseColor',
                                    'compression':('TC_NORMALMAP' if kind=='NormalDX' else 'TC_MASKS' if kind=='ORM' else 'TC_DEFAULT')}
                import_mode='UE4_COMMANDLET_TEXTURE'
            else:
                raise ValueError('NOT_FBX_OR_PNG')
            track=logical_track(row)
            cases[track].append(name)
            staging_bytes.append((target,raw))
            inventory.append({'source':name,'output':str(target.relative_to(workspace)).replace('\\','/'),
                              'sha256':row['sha256'],'track':track,'kind':import_mode,
                              'bytes':len(raw)})
            expected_paths[name]=str(target)
        if len(outside)!=120 or len(inventory)!=143 or len(mesh)!=34 or len(material)!=21:
            raise ValueError('STAGE_COUNTS_UNEXPECTED:' + str((len(outside),len(inventory),len(mesh),len(material))))
    families = []
    for key,levels in sorted(mesh.items()):
        expected = (0,1,2) if key.startswith('Nature/') else (0,1)
        if tuple(sorted(levels)) != expected:
            raise ValueError('INCOMPLETE_MESH_LODS:' + key)
        base=levels[0]
        canonical='World/Shire/CuratedP1C01/'+base['source_file']
        package='/Game/Production/'+str(Path(canonical).with_suffix('')).replace('\\','/')
        stem=key.split('/',1)[1]
        if key.startswith('Nature/'):
            collider = 'SIMPLE_REVIEW_TREE_TRUNK' if stem in TREE_FAMILIES else 'SIMPLE_REVIEW_ROCK' if stem in ('rock_field','rock_river') else 'DECORATIVE_NO_BLOCKER'
        else:
            arch=next(r['family'] for r in manifest['asset_files'] if r['dest']==base['source_file'])
            collider='SIMPLIFIED_AUTHOR_COLLIDER_REVIEW' if arch in ('RoundDoor','RoundRoomWallArc','StonePath','WoodenFootbridge','FarmGate') else 'NO_AUTOGEN_COLLIDER_REVIEW'
        families.append({'id':key, 'base_asset_path':package,'base_filename':base['absolute_path'],
                         'lods':{str(lod):levels[lod] for lod in expected},
                         'expected_lod_count':len(expected), 'collision_policy':collider,
                         'hism_candidate':key.startswith('Nature/') or stem in ('PicketFence','GardenHedge','GardenPlanter','OakTree')})
    for key,triplet in material.items():
        if set(triplet) != {'BaseColor','NormalDX','ORM'}:
            raise ValueError('MATERIAL_TRIPLET_INCOMPLETE:' + key)
    # Original assets only: no signed external licenses, no audio source was supplied.
    logical_tracks={x:len(v) for x,v in cases.items()}
    logical_tracks['L07_CHARACTER_QC_REVIEW_ONLY']=0
    logical_tracks['L08_AUDIO_AND_RUNTIME_QA_REVIEW_ONLY']=0
    if len(cases)!=6:
        raise ValueError('TRACK_CLASSIFIER_NOT_SIX_SOURCE_TRACKS')
    ready = {
        'schema_version':1, 'chapter':'P1C01', 'mode':'ORIGINAL_SOURCE_STAGED_NOT_UE4_IMPORTED',
        'source_manifest_sha256':CURATED_MANIFEST_SHA,'workspace':str(workspace),
        'game_asset_root':'/Game/Production/World/Shire/CuratedP1C01',
        'engine':'UE4.27.2','target':'DX11 720p 30FPS 8GB_RAM 2GB_VRAM',
        'logical_tracks_eight_inside_governor_five_lanes':dict(sorted(logical_tracks.items())),
        'mesh_families':families,'material_triplets':dict(sorted(material.items())),
        'external_license_held_count':len(outside),
        'external_license_held':outside,
        'source_stage_files':inventory,'source_stage_count':len(inventory),
        'importable_ue_base_meshed_families':len(families),
        'lod_sidecars':sum(len(x['lods'])-1 for x in families),
        'source_png':sum(1 for x in inventory if x['source'].endswith('.png')),
        'source_eligible_for_engine_review':True,'engine_import_allowed_now':False,
        'unreal_asset_imported':False, 'ue_lods_built':False,
        'collision_tested':False,'nav_tested':False,'quest_tested':False,
        'audio_verified':False,'pie_tested':False,'device_tested':False,
        'visual_accepted':False,'gate6_7_closed':False,
        'warnings':['External CC0 receipts remain held for independent rights review',
                    'LOD1/2 stored separately and MUST NOT be imported as independent runtime-visible meshes',
                    'Actual collision/nav, HISM binding, material instances, PIE and DX11 FPS need UE4 runner proof'],
    }
    # Two-phase commit: malformed sources or incomplete LOD families never leave
    # a half-written checkout before the entire selection has passed QC.
    for target, raw in staging_bytes:
        actions[atomic_bytes(target,raw,workspace)] += 1
    atomic_bytes(workspace/RECEIPT_REL,(json.dumps(ready,indent=2,sort_keys=True)+'\n').encode('utf-8'),workspace)
    return ready


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--archive',type=Path,required=True,help='Exact curated ZIP from ten owner Drive packs')
    ap.add_argument('--workspace',type=Path,required=True,help='Isolated UE4 project checkout or staging workspace')
    args=ap.parse_args()
    report=stage_archive(args.archive,args.workspace)
    print('P1C01_ORIGINAL_SOURCE_STAGE_PASS mesh_families=%d lod_sidecars=%d textures=%d held_external=%d stage_files=%d' %
          (report['importable_ue_base_meshed_families'],report['lod_sidecars'],report['source_png'],
           report['external_license_held_count'],report['source_stage_count']))
    print('P1C01_ORIGINAL_SOURCE_RECEIPT '+str(args.workspace/RECEIPT_REL))
    print('BOUNDARY NO_UE_IMPORT_NO_PIE_NO_DEVICE_NO_VISUAL_NO_GATE67')

if __name__=='__main__':
    main()