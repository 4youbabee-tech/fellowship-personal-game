#!/usr/bin/env python3
"""Curate actual owner-provided Drive source ZIPs into an original, source-only Shire batch.

No UE4 import, licensing approval, runtime rollout, or Gate 6/7 acceptance is inferred.
"""
from __future__ import annotations
import argparse, hashlib, io, json, re, struct, zipfile, shutil
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
try:
    from PIL import Image, ImageDraw
except ImportError:  # Hosted/Windows source staging has no Pillow requirement.
    Image = None
    ImageDraw = None

ROOT=Path.cwd()
OUTDIR=Path.cwd()
INPUTS={}
OUT=OUTDIR/'SHIRE_P1C01_CURATED_SOURCE_20261012.zip'
REPORT=OUTDIR/'SHIRE_P1C01_CURATED_SOURCE_AUDIT_20261012.json'
SHEET=OUTDIR/'SHIRE_P1C01_MATERIAL_CONTACT_SHEET_20261012.png'
EXPECTED={
'GH11704614644_polyhaven_shard1.zip':'d0e931f51e36fb4a541ffb1e156b16ab32d790790d03bc8c9ef664dc8cb156f0',
'GH11704654471_polyhaven_shard2.zip':'c61755457e9547e9fa981d8dc327ab6b43ae9f036fb5242a758b87d30cc7f368',
'GH11705009927_shire_28regions.zip':'45cd2098345c3831d699ad81ede0cc187387858f1dd3f6bbcd5ab883e3d2498b',
'GH11705438692_polyhaven_shard3.zip':'24c5ae3024cc8da2db19c9d91925de51153b627b837c8015f12f0907585fa210',
'GH11705468534_frodo_source.zip':'b9b29c1f978643a77ea3766622dc66cd21ec081a919b85dae5aa27e08c81134b',
'GH11705506123_polyhaven_shard0.zip':'538b99a6175b657440eac67a6e49d44db0d2510ee1a46cc122595099ca41e965',
'GH11706518373_Shire_Nature_Binary_36_FBX.zip':'45746e3aa6a19021a0e717160b6cbcdc0343ba20c5cd7072189908cb0c1d7586',
'SHIRE_NATURE_UE427_BINARY_FBX_PNG_SOURCE_INTAKE_20261011.zip':'940bd5679ff27e97fbf9ae214fd62cb57c0d760ca99a3a37e6353e3afa423fc6',
'SHIRE_PRIORITY_LICENSED_PBR_4_MATERIALS_20261011.zip':'ff8c2d70377c89461e362a928c45157a6fea31353184c256cba2fd7fc3c48068',
'Shire_Nature_Wave_20261011.zip':'16809e17ecb91a732f6ea6b684a49801cef0cbf514e0abed3028db827f7a3a56'}
FBX_MAGIC=b'Kaydara FBX Binary  \x00\x1a\x00'
KIND_TRIPLET={'BaseColor','NormalDX','ORM'}

def digest(data):return hashlib.sha256(data).hexdigest()
def file_digests(path):
 h=hashlib.sha256();m=hashlib.md5()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):
   h.update(block);m.update(block)
 return h.hexdigest(),m.hexdigest()
def valid_path(p):
 q=PurePosixPath(p.replace('\\','/'))
 if not p or p.startswith('/') or '..' in q.parts or ':' in p or '\x00' in p or len(q.parts)>10:raise ValueError('UNSAFE_MEMBER '+p)
 return True

def png_size(b):
 if not b.startswith(b'\x89PNG\r\n\x1a\n') or b[12:16]!=b'IHDR':raise ValueError('NOT_PNG')
 w,h=struct.unpack('>II',b[16:24]); assert 0<w<=4096 and 0<h<=4096
 return [w,h]

def main():
 archive_meta=[]; handles={}; internal=[]; rejects=[]; entries=[]; material_basecolors=[]
 duplicate_content=defaultdict(list); physical_by_hash={}; candidates={}; lod_details=defaultdict(list)
 for name,sha in EXPECTED.items():
  p=INPUTS.get(name, ROOT/name)
  if not p.is_file():raise ValueError('MISSING_OWNER_ZIP '+name)
  h,m=file_digests(p)
  if h!=sha:raise ValueError('SOURCE_ZIP_HASH_MISMATCH '+name)
  z=zipfile.ZipFile(p)
  if z.testzip() is not None:raise ValueError('ZIP_CRC_FAILURE '+name)
  for x in z.infolist():
   valid_path(x.filename)
   if x.flag_bits&1:raise ValueError('ENCRYPTED_MEMBER '+name)
  handles[name]=z
  archive_meta.append({'name':name,'bytes':p.stat().st_size,'sha256':h,'md5':m,'zip_members':len(z.infolist()),'zip_crc':'PASS'})
 # Reuse the exact same source SHA set and tool version without rewriting 180MB.
 script_hash=digest(Path(__file__).read_bytes())
 if OUT.is_file() and REPORT.is_file():
  try:
   cached=json.loads(REPORT.read_text(encoding='utf-8'))
   prior={x['name']:x['sha256'] for x in cached['source_drive_archives']}
   present={x['name']:x['sha256'] for x in archive_meta}
   if (prior==present and cached.get('tool_sha256')==script_hash
       and (OUTDIR/'SHIRE_P1C01_RIG_REVIEW_ONLY_20261012.zip').is_file()
       and (OUTDIR/'SHIRE_P1C01_ASSET_MANIFEST_20261012.json').is_file()
       and file_digests(OUT)[0]==cached['output_zip_sha256']):
    for z in handles.values():z.close()
    print('SHIRE_CURATED_REUSED source_sha_set=10 archive_sha256='+cached['output_zip_sha256'])
    return
  except (KeyError,ValueError,OSError):
   pass
 # Fail-closed actual selection: import-source candidates only, no binaries execute.
 temp_out=OUT.with_name(OUT.name+'.partial')
 with zipfile.ZipFile(temp_out,'w',allowZip64=True) as produced:
  def add_asset(z, source_archive, member, dest, claimed_hash, claimed_bytes=None, license_claim='ORIGINAL_PROJECT_ASSET', notes=None):
   valid_path(member);valid_path(dest)
   if dest in candidates:raise ValueError('DEST_COLLISION '+dest)
   raw=z.read(member)
   if digest(raw)!=claimed_hash or (claimed_bytes is not None and len(raw)!=claimed_bytes):raise ValueError('ASSET_HASH_OR_SIZE_MISMATCH '+source_archive+'::'+member)
   ext=Path(member).suffix.lower()
   if ext=='.fbx':
    if not raw.startswith(FBX_MAGIC) or struct.unpack('<I',raw[len(FBX_MAGIC):len(FBX_MAGIC)+4])[0]!=7400:raise ValueError('FBX_NOT_BINARY_7400 '+member)
   elif ext=='.png':png_size(raw)
   else:raise ValueError('NOT_ALLOWED_FOR_PRODUCTION '+member)
   canonical=physical_by_hash.get((ext,claimed_hash))
   if canonical is None:
    produced.writestr(dest,raw,compress_type=zipfile.ZIP_DEFLATED if ext=='.fbx' else zipfile.ZIP_STORED)
    physical_by_hash[(ext,claimed_hash)]=dest
   row={'dest':dest,'source_archive':source_archive,'source_member':member,'bytes':len(raw),'sha256':claimed_hash,
        'license_claim_from_embedded_receipt':license_claim,'licensed_runtime_approved':False,'unreal_imported':False}
   if canonical is not None:row['alias_of']=canonical
   if notes:row.update(notes)
   entries.append(row);candidates[dest]=row;duplicate_content[(ext,claimed_hash)].append(dest)
   if ext=='.png' and ('BaseColor' in dest or 'Albedo' in dest):material_basecolors.append((dest,raw))

  n='SHIRE_NATURE_UE427_BINARY_FBX_PNG_SOURCE_INTAKE_20261011.zip'; z=handles[n]
  nature=json.loads(z.read('Receipts/import_bindings.json'))
  assert nature['source_only'] is True and nature['unreal_imported'] is False and len(nature['family_lod_meshes'])==36
  all_hashes=nature['source_file_hashes']
  assert len(all_hashes)==63
  for member,expected in sorted(all_hashes.items()):
   dest='Nature/'+member
   add_asset(z,n,member,dest,expected,license_claim='ORIGINAL_PROJECT_PROCEDURAL',notes={'lane':'FOLIAGE_NATURE','import_requires':'UE4_STATIC_MESH_LOD_GROUPING_AND_COLLISION_QC'})
  for r in nature['family_lod_meshes']:
   name=r['source_file']; assert name in all_hashes and r['lod'] in (0,1,2)
   assert r['polygons_after_blender_reimport']>0
   lod_details[r['family']].append({'lod':r['lod'],'polygons':r['polygons_after_blender_reimport'],'asset':'Nature/'+name,'collision_source_count':r.get('collision_source_count',0)})
  for family,items in lod_details.items():
   levels=sorted(items,key=lambda x:x['lod'])
   assert [a['lod'] for a in levels]==[0,1,2],('bad lod sequence',family)
   if not (levels[0]['polygons']>=levels[1]['polygons']>=levels[2]['polygons']):raise ValueError('NATURE_LOD_TRIANGLE_INVERSION '+family)
  # A second binary source duplicates existing 36 FBX; old ASCII is strictly source only.
  old=handles['Shire_Nature_Wave_20261011.zip']
  ascii_count=sum(1 for p in old.namelist() if p.lower().endswith('.fbx'))
  if ascii_count!=36:raise ValueError('LEGACY_NATURE_ASSET_COUNT_DRIFT')
  rejects.append({'source_archive':'Shire_Nature_Wave_20261011.zip','count':ascii_count,'reason':'LEGACY_ASCII_FBX_SOURCE_NOT_SELECTED'})
  other=handles['GH11706518373_Shire_Nature_Binary_36_FBX.zip']
  r=json.loads(other.read('nature_receipt.json')); assert len(r['objects'])==36
  canonical={a['sha256'] for a in entries if a['dest'].endswith('.fbx') and a['dest'].startswith('Nature/')}
  for row in r['objects']:
   if row['sha256'] not in canonical or digest(other.read(row['path']))!=row['sha256']:raise ValueError('DUPLICATE_NATURE_ASSERTION_FAILED '+row['path'])
  rejects.append({'source_archive':'GH11706518373_Shire_Nature_Binary_36_FBX.zip','count':36,'reason':'BYTE_IDENTICAL_DUPLICATE_NATURE_FBX_ALREADY_SELECTED'})

  # Nested modular Shire architecture: 22 families, LOD0/1 and 12 original PBR surface triplets.
  n='GH11705009927_shire_28regions.zip'; outer=handles[n]; assert len(outer.namelist())==1
  with zipfile.ZipFile(io.BytesIO(outer.read(outer.namelist()[0]))) as inner:
   assert inner.testzip() is None
   fbx=json.loads(inner.read('fbx_receipt.json'))
   mat=json.loads(inner.read('materials_receipt.json'))
   assert fbx['asset_count']==22 and fbx['fbx_count']==44 and fbx['provenance']=='ORIGINAL_PROJECT_PROCEDURAL_GEOMETRY'
   assert mat['license']=='ORIGINAL_PROJECT_ASSET' and mat['material_families']==12 and mat['physical_textures']==36
   for r in fbx['objects']:
    assert r['lod'] in (0,1) and r['reimport_uv_layers']>0 and r['reimport_polygons']>0
    add_asset(inner,n,r['path'],'Architecture/'+r['path'],r['sha256'],r['bytes'],license_claim='ORIGINAL_PROJECT_PROCEDURAL',notes={'lane':'SHIRE_ARCHITECTURE','family':r['asset'],'lod':r['lod'],'uv_layers':r['reimport_uv_layers'],'collider_count':r.get('collider_count',0),'import_requires':'UE4_STATIC_MESH_LOD_GROUPING'})
   for r in mat['textures']:
    assert r['type'] in KIND_TRIPLET and r['dimensions']==[1024,1024]
    add_asset(inner,n,r['path'],'Regional/'+r['path'],r['sha256'],r['bytes'],license_claim='ORIGINAL_PROJECT_ASSET',notes={'lane':'REGIONAL_SURFACE_PREP','material_family':r['family'],'map_kind':r['type'],'color_space':r['color_space']})
   regions=mat['region_bindings']; assert len(regions)==28
   shire_bindings={r['id']:r['support_surfaces'] for r in regions if r['id'] in ('SHIRE_HOBBITON','BAG_END')}
   assert len(shire_bindings)==2

  # Four project-priority licensed PBR triplets, each individually hash-attested.
  n='SHIRE_PRIORITY_LICENSED_PBR_4_MATERIALS_20261011.zip'; z=handles[n]
  pbr=json.loads(z.read('Receipts/provenance_and_material_bindings.json'))
  for family,row in sorted(pbr['material_sets'].items()):
   assert row['provider']=='Poly Haven' and row['license']=='CC0' and set(row['files'])==KIND_TRIPLET
   for k,r in sorted(row['files'].items()):
    add_asset(z,n,r['path'],f'PBR/Priority/{family}/{Path(r["path"]).name}',r['sha256'],r['bytes'],license_claim='CC0_EMBEDDED_PROVENANCE',notes={'lane':'PRIORITY_PBR','family':family,'kind':k,'source_page':row['source_page'],'map_to_slot':row['map_to_slot'],'srgb_expected':k=='BaseColor'})

  material_names=set()
  quarantined_shards=[]
  for n in sorted(x for x in EXPECTED if 'polyhaven_shard' in x):
   z=handles[n];r=json.loads(z.read('receipt.json'))
   assert r['staged']==len(r['materials']) and r['physical_png']==3*len(r['materials'])
   quarantined_shards += [{'source':n,'slug':x['slug'],'reason':x['reason']} for x in r['quarantined']]
   for m in r['materials']:
    slug=m['slug']
    assert slug not in material_names and re.fullmatch('[A-Za-z0-9_-]+',slug)
    material_names.add(slug)
    assert m['license']=='CC0' and m['source_page']=='https://polyhaven.com/a/'+slug
    assert {x['kind'] for x in m['outputs']}==KIND_TRIPLET
    for row in sorted(m['outputs'],key=lambda x:x['kind']):
     add_asset(z,n,row['path'],f'PBR/PolyHaven/{slug}/{Path(row["path"]).name}',row['sha256'],row['bytes'],license_claim='CC0_EMBEDDED_PROVENANCE',notes={'lane':'POLYHAVEN_PBR','family':slug,'kind':row['kind'],'source_page':m['source_page'],'srgb_expected':row['kind']=='BaseColor'})
  assert len(material_names)==36 and len(quarantined_shards)==1 and quarantined_shards[0]['slug']=='wooden_barrels_01'
  rejects.append({'source_archive':'GH11704614644_polyhaven_shard1.zip','count':1,'reason':'MISSING_REQUIRED_MAPS','item':'wooden_barrels_01'})

  # Character rig must not silently ride along in the environment pack.
  n='GH11705468534_frodo_source.zip';z=handles[n];hero=json.loads(z.read('p1c01_human_wave2_hosted.json'))
  assert hero['license']=='CC0' and len(hero['normalized_results'])==2
  viable=[x for x in hero['normalized_results'] if x['quality_pass']]
  rejected=[x for x in hero['normalized_results'] if not x['quality_pass']]
  assert len(viable)==1 and len(rejected)==1
  rejects.append({'source_archive':n,'count':1,'reason':'NONPRODUCTION_HERO_RIG_CANDIDATE_REJECTED','quality_reasons':rejected[0]['quality_reasons']})
  # No character claimed final: candidate_01 is stored in a separate review-only ZIP.
  with zipfile.ZipFile(OUTDIR/'SHIRE_P1C01_RIG_REVIEW_ONLY_20261012.zip','w',zipfile.ZIP_DEFLATED) as rig_out:
   p=viable[0]['normalized_relative_path']; raw=z.read(p)
   assert digest(raw)==viable[0]['normalized_sha256']
   rig_out.writestr('RigReview/'+Path(p).name,raw)
   rig_out.writestr('RigReview/README.txt','Original generic CC0 armature source candidate only. Not Frodo likeness, not UE-imported, not animated, not character acceptance. Requires skin deformation and UE4 re-target check.\n')
   rig_out.writestr('RigReview/source_receipt.json',json.dumps({'source_archive':n,'source_sha256':EXPECTED[n],'creator':hero['source_creator'],'source_page':hero['source_page'],'license_claim':'CC0','normalized_result':viable[0],'rejected_other_candidate':rejected[0]['quality_reasons'],'status':'REVIEW_ONLY'},indent=2))

  counts=Counter(r['lane'] for r in entries)
  if not (counts=={'FOLIAGE_NATURE':63,'SHIRE_ARCHITECTURE':44,'REGIONAL_SURFACE_PREP':36,'PRIORITY_PBR':12,'POLYHAVEN_PBR':108}):raise ValueError('CURATED_SELECTION_COUNT_MISMATCH '+str(counts))
  # Do not include an item twice (even under different output paths) without exposing it.
  dupe=[{'sha256':sha,'extension':ext,'copies':files} for (ext,sha),files in duplicate_content.items() if len(files)>1]
  manifest={'schema_version':1,'chapter':'P1C01','scope':'SOURCE_ONLY_NOT_UNREAL_IMPORTED','source_drive_archives':archive_meta,
            'source_integrity':'ACTUAL_BYTES_VERIFIED_IN_THIS_CHAT_CONTAINER','target':'UE4.27.2 DX11 720p 30FPS 8GB RAM 2GB VRAM',
            'archive_bytes':sum(x['bytes'] for x in archive_meta), 'logical_asset_bindings':len(entries), 'curated_physical_file_count':len(physical_by_hash),'deduplicated_alias_count':len(entries)-len(physical_by_hash),'counts_by_lane':dict(counts),
            'asset_files':entries, 'nature_lod_families':dict(lod_details),'shire_region_material_bindings':shire_bindings,
            'polyhaven_material_family_count':len(material_names),'priority_material_family_count':4,
            'sha256_duplicate_content_groups_within_output':dupe,'quarantine':rejects,'polyhaven_quarantine':quarantined_shards,
            'rights_boundary':'CC0 provider assertions are present in signed? NO: unsigned embedded receipts only. Human source rights review still required; project-original assets are project-attributed.',
            'engine_imported':False,'lod_assigned_in_ue4':False,'collision_tested_in_ue4':False,'pie_tested':False,'device_tested':False,'visual_accepted':False,'gate6_7_closed':False}
  readme='''SHIRE JOURNEY P1C01 - CURATED PHYSICAL SOURCE PACK 2026-10-12\n\nThis is a curated data source batch produced from exactly ten verified owner Drive archives. No downloaded model duplication: 36 duplicate binary nature FBX and 36 obsolete ASCII FBX are excluded. One incomplete Poly Haven material is excluded.\n\nSource assets: Nature (12 families x 3 FBX LOD, 9 texture families x 3 maps); Architecture (22 families x 2 FBX LOD); Regional (12 families x 3 maps); Priority PBR (4 families x 3 maps); Poly Haven (36 complete CC0-claimed families x 3 maps).\n\nBinary FBX versions 7400; texture PNG only. LOD0/1/2 are separate files and MUST be combined into UE4 StaticMesh LOD levels via a reviewed importer. Do NOT import each LOD as runtime-visible separate mesh. Preserve original HISM/LOD population. Non-physics foliage should not receive blockers; trees and rocks use authored UCX sources only after collision review.\n\nPBR: BaseColor sRGB; NormalDX linear/normal map; ORM R=AO,G=Roughness,B=Metallic linear mask. No heavy synchronous runtime LoadObject allowed. Store as soft references with async streaming.\n\nRightsholder and external source receipt assertions still require manual licensing/provenance review before approval. No copy of film imagery/dialogue. Do not enable P1C02 runtime.\n\nThe root AssetManifest.json contains SHA256 and source identity for each physical file. No .uasset was imported or accepted.\n'''
  produced.writestr('AssetManifest.json',json.dumps(manifest,indent=2,sort_keys=True,ensure_ascii=False)+'\n',zipfile.ZIP_DEFLATED)
  produced.writestr('IMPORT_NOTES.txt',readme,zipfile.ZIP_DEFLATED)
 for z in handles.values():z.close()
 with zipfile.ZipFile(temp_out) as check:
  if check.testzip() is not None:raise ValueError('OUTPUT_CRC_FAIL')
  assert len(check.namelist())==len(physical_by_hash)+2
  for row in entries:
   resolved=row.get('alias_of',row['dest'])
   if digest(check.read(resolved))!=row['sha256']:raise ValueError('OUTPUT_HASH_DRIFT '+row['dest'])
 mh,mm=file_digests(temp_out)
 temp_out.replace(OUT)
 report={k:v for k,v in manifest.items() if k!='asset_files'}
 report['output_zip']=OUT.name; report['output_zip_bytes']=OUT.stat().st_size;report['output_zip_sha256']=mh;report['output_zip_md5']=mm;report['tool_sha256']=script_hash
 report['rig_review_zip']='SHIRE_P1C01_RIG_REVIEW_ONLY_20261012.zip'
 (OUTDIR/'SHIRE_P1C01_ASSET_MANIFEST_20261012.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 REPORT.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 # Actual inspected source texture preview. No generated/reimagined artwork.
 cols=5; cell_w=190;cell_h=202;rows=(len(material_basecolors)+cols-1)//cols
 if Image is not None:
  canvas=Image.new('RGB',(cols*cell_w,rows*cell_h),(242,241,238));draw=ImageDraw.Draw(canvas)
  for i,(label,raw) in enumerate(material_basecolors):
   img=Image.open(io.BytesIO(raw)).convert('RGB');img.thumbnail((170,165))
   x=(i%cols)*cell_w+10;y=(i//cols)*cell_h+7
   canvas.paste(img,(x,y)); name=label.split('/')[-1].replace('TX_PH_','').replace('_BaseColor.png','').replace('TX_','')
   name=name[:25]
   draw.text((x,y+169),name,fill=(24,33,33))
  canvas.save(SHEET,optimize=True)
 print('SOURCE_PHYSICAL_SCAN_PASS archives=10 bytes=',sum(x['bytes'] for x in archive_meta))
 print('SOURCE_CURATED_PASS bindings=',len(entries),'physical_files=',len(physical_by_hash),'deduplicated_aliases=',len(entries)-len(physical_by_hash),'mesh_fbx=',sum(r['dest'].endswith('.fbx') for r in entries),'textures_png=',sum(r['dest'].endswith('.png') for r in entries))
 print('SOURCE_CURATED_COUNT_BY_LANE',dict(counts),'material_thumbnail_count',len(material_basecolors))
 print('SOURCE_CURATED_QUARANTINE',rejects,'member_sha_duplicate_groups',len(dupe))
 print('SOURCE_CURATED_ARCHIVE',OUT.name,'bytes',OUT.stat().st_size,'sha256',mh)
 print('SOURCE_CURATED_RIG_REVIEW',OUTDIR/'SHIRE_P1C01_RIG_REVIEW_ONLY_20261012.zip')
 print('BOUNDARY Not Unreal imported, no PIE, no target-device FPS, no chapter closeout')

def configure():
 global ROOT, OUTDIR, OUT, REPORT, SHEET, INPUTS
 ap=argparse.ArgumentParser(description='Curate verified Shire Drive ZIP source without claiming Unreal import')
 ap.add_argument('--archive-dir',type=Path,help='Local owner Drive ZIP directory for isolated audit')
 ap.add_argument('--warehouse-root',type=Path,help='Physical D: Warehouse root with all ten SHA-bound receipts')
 ap.add_argument('--output-dir',type=Path,help='Curated source destination, never Content/Production')
 args=ap.parse_args()
 if bool(args.archive_dir)==bool(args.warehouse_root):
  ap.error('Choose exactly one of --archive-dir or --warehouse-root')
 INPUTS={}
 if args.warehouse_root:
  import verify_drive_warehouse_receipts as proof
  warehouse=args.warehouse_root.resolve()
  qc=proof.assess(warehouse, proof.SNAPSHOT)
  if qc['state']!='SOURCE_QC_PASS_IMPORT_BLOCKED' or qc['verified_archive_count']!=10:
   raise ValueError('WAREHOUSE_PHYSICAL_TEN_ZIP_PROOF_REQUIRED')
  records=[]
  for p in sorted((warehouse/'_drive_temp_staging'/'receipts').glob('*.json')):
   records.append(json.loads(p.read_text(encoding='utf-8')))
  for name,sha in EXPECTED.items():
   matches=[r for r in records if r.get('remote_path')==proof.CATEGORIES[name]+'/'+name and r.get('sha256')==sha]
   if len(matches)!=1:raise ValueError('WAREHOUSE_RECEIPT_MISSING '+name)
   path=Path(matches[0]['local_path'])
   trusted=(warehouse/'_drive_temp_staging'/'files'/proof.CATEGORIES[name]).resolve()
   if path.resolve().parent!=trusted or path.name!=matches[0]['remote_id']+'-'+sha[:16]+'-'+name:
    raise ValueError('WAREHOUSE_PATH_NOT_TRUSTED '+name)
   INPUTS[name]=path
  ROOT=warehouse
  OUTDIR=args.output_dir or warehouse/'_drive_temp_staging'/'curated_p1c01'
 else:
  ROOT=args.archive_dir.resolve()
  OUTDIR=args.output_dir or ROOT/'_curated_p1c01'
 if any(part.lower()=='content' for part in OUTDIR.parts):
  raise ValueError('SOURCE_CURATION_MUST_NOT_WRITE_TO_UNREAL_CONTENT')
 OUTDIR.mkdir(parents=True,exist_ok=True)
 if args.warehouse_root and shutil.disk_usage(OUTDIR).free < 6*1024**3+256*1024**2:
  raise ValueError('PERSISTENT_WAREHOUSE_FREE_SPACE_RESERVE_BELOW_6GIB')
 OUT=OUTDIR/'SHIRE_P1C01_CURATED_SOURCE_20261012.zip'
 REPORT=OUTDIR/'SHIRE_P1C01_CURATED_SOURCE_AUDIT_20261012.json'
 SHEET=OUTDIR/'SHIRE_P1C01_MATERIAL_CONTACT_SHEET_20261012.png'

if __name__=='__main__':
 configure()
 main()
