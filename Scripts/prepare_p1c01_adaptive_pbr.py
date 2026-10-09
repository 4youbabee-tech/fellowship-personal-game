#!/usr/bin/env python3
"""39-source-asset existing-artifact to 1K FBX/PNG QC. NO UE4, no network, no warehouse write."""
import argparse,hashlib,io,json,os,re,shutil,zipfile
os.environ.setdefault('OPENCV_IO_ENABLE_OPENEXR','1')
from pathlib import Path
import cv2,numpy as np
from PIL import Image

HOLD_BIOME={'anthurium_botany_01','calathea_orbifolia_01','didelta_spinosa','pachira_aquatica_01'}
HOLD_ID={'picke_dirty_01','dead_quiver_trunk'}
MAX_FILE=32*1024**2
class QCError(ValueError): pass

def sha(blob): return hashlib.sha256(blob).hexdigest()
def safe(s):
    if not isinstance(s,str) or '\\' in s or '\x00' in s or s.startswith('/') or '..' in Path(s).parts: raise QCError('UNSAFE_PATH')
    return s

def pixels(blob,ext,gray=False):
    if ext.lower()=='.exr':
        a=cv2.imdecode(np.frombuffer(blob,dtype=np.uint8),cv2.IMREAD_UNCHANGED)
        if a is None: raise QCError('EXR_DECODE')
        if a.ndim==3: a=a[:,:,::-1]
        if not np.isfinite(a).all(): raise QCError('NONFINITE_EXR')
        a=np.round(np.clip(a.astype(np.float32),0,1)*255).astype(np.uint8)
    else:
        with Image.open(io.BytesIO(blob)) as im:
            im.load()
            a=np.asarray(im)
            if a.dtype==np.uint16: a=np.round(a.astype(np.float32)/257).astype(np.uint8)
            if a.dtype!=np.uint8: raise QCError('UNSUPPORTED_PIXEL_TYPE')
    if a.shape[:2]!=(1024,1024): raise QCError('NOT_1K')
    if gray:
        if a.ndim==3: a=a[:,:,:3].mean(axis=2).round().astype(np.uint8)
        return a
    if a.ndim!=3 or a.shape[2]<3: raise QCError('MISSING_RGB')
    return a[:,:,:3]

def material_groups(tex):
    """Preserve a dry diffuse-only color variant as held; never invent normal maps."""
    prefixes=sorted({re.sub(r'_diff_1k\.[^.]+$','',k) for k in tex
                     if re.search(r'_diff_1k\.(png|jpg|jpeg|tga)$',k)})
    if not prefixes: raise QCError('NO_DIFFUSE')
    def has(prefix,role):
        return any(re.fullmatch(re.escape(prefix)+'_'+role+r'_1k\.[^.]+',n) for n in tex)
    complete=[prefix for prefix in prefixes if has(prefix,'nor_gl') and has(prefix,'rough')]
    if not complete: raise QCError('NO_COMPLETE_MATERIAL')
    held=[]
    for prefix in prefixes:
        if prefix in complete: continue
        if prefix.endswith('_dry') and prefix[:-4] in complete: held.append(prefix)
        else: raise QCError('BAD_MAP_nor_gl_OR_rough')
    return complete,held

def convert(archive,output,source_run_id=None,source_artifact_id=None):
    output.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        names=z.namelist()
        if len(names)!=len(set(names)) or any(safe(n)!=n for n in names): raise QCError('BAD_ARCHIVE_PATHS')
        receipt=json.loads(z.read('p1c01_adaptive_polyhaven_receipt.json'))
        if receipt.get('source_assets_staged')!=len(receipt.get('accepted',[])) or receipt.get('source_assets_staged',0)<1: raise QCError('INVALID_RECEIPT')
        expected={'p1c01_adaptive_polyhaven_receipt.json'}
        for item in receipt['accepted']:
            for f in item['files']: expected.add(safe('assets/'+item['id']+'/'+f['relative_file']))
        if set(names)!=expected: raise QCError('SOURCE_FILESET_MISMATCH')
        completed=[]; quarantined=[]
        for item in receipt['accepted']:
            slug=item['id']; out=output/'assets'/slug
            try:
                if not re.fullmatch('[a-z0-9_]{3,80}',slug): raise QCError('BAD_ID')
                data={}
                for f in item['files']:
                    fn=f['relative_file']; info=z.getinfo('assets/'+slug+'/'+fn)
                    if info.file_size>MAX_FILE or info.file_size<1: raise QCError('SOURCE_FILE_SIZE_LIMIT')
                    b=z.read(info)
                    if len(b)!=f['bytes'] or sha(b)!=f['sha256'] or hashlib.md5(b).hexdigest()!=f['md5']: raise QCError('SOURCE_HASH_FAIL')
                    data[fn]=b
                fbx=data.get(slug+'.fbx')
                if not fbx or not fbx.startswith(b'Kaydara FBX Binary'): raise QCError('BAD_FBX')
                tex=[k for k in data if k.startswith('textures/')]
                prefixes,held_prefixes=material_groups(tex)
                out.mkdir(parents=True,exist_ok=True); rows=[]; held_variants=[]
                for variant in held_prefixes:
                    matches=[n for n in tex if re.fullmatch(re.escape(variant)+r'_diff_1k\.[^.]+',n)]
                    if len(matches)!=1: raise QCError('AMBIGUOUS_HELD_VARIANT')
                    original=matches[0]
                    hold=out/'holds'/('TX_'+variant.split('/')[-1]+'_BaseColor_HOLD.png')
                    hold.parent.mkdir(parents=True,exist_ok=True)
                    Image.fromarray(pixels(data[original],Path(original).suffix)).save(hold,format='PNG',optimize=True)
                    held_variants.append({'path':str(hold.relative_to(output)),
                                          'bytes':hold.stat().st_size,'sha256':sha(hold.read_bytes()),
                                          'source_path':original,'source_sha256':sha(data[original]),
                                          'status':'HOLD_MATERIAL_VARIANT_NO_INDEPENDENT_NORMAL_ROUGHNESS',
                                          'eligible_for_ue_import':False})
                for prefix in prefixes:
                    def find(role,mandatory=False):
                        m=[k for k in tex if re.fullmatch(re.escape(prefix)+'_'+role+r'_1k\.[^.]+',k)]
                        if len(m)>1 or (mandatory and not m): raise QCError('BAD_MAP_'+role)
                        return m[0] if m else None
                    def get(name,gray=False):
                        return pixels(data[name],Path(name).suffix,gray)
                    diff=find('diff',True); nor=find('nor_gl',True); rough=find('rough',True)
                    met=find('metal'); ao=find('ao'); opacity=find('alpha') or find('opacity')
                    base=get(diff); normal=get(nor).copy();normal[:,:,1]=255-normal[:,:,1]
                    r=get(rough,True); g=get(met,True) if met else np.zeros_like(r); a=get(ao,True) if ao else np.full_like(r,255)
                    images={'BaseColor':base,'NormalDX':normal,'ORM':np.stack((a,r,g),axis=-1)}
                    if opacity: images['OpacityMask']=get(opacity,True)
                    for kind,arr in images.items():
                        name='TX_'+prefix.split('/')[-1]+'_'+kind+'.png'
                        target=out/name
                        Image.fromarray(arr).save(target,format='PNG',optimize=True)
                        rows.append({'path':str(target.relative_to(output)),'role':kind,'bytes':target.stat().st_size,'sha256':sha(target.read_bytes()),'resolution':[1024,1024]})
                target=out/(slug+'.fbx');target.write_bytes(fbx)
                completed.append({'id':slug,'status':'HOLD_BIOME' if slug in HOLD_BIOME else 'HOLD_IDENTITY' if slug in HOLD_ID else 'STATIC_SOURCE_QC_ONLY','fbx_sha256':sha(fbx),'fbx_path':str(target.relative_to(output)),'maps':rows,'held_material_variants':held_variants,'fbx_bytes':len(fbx),'unreal_imported':False,'lod_collision_verified':False,'visual_accepted':False})
            except (QCError,ValueError,KeyError,OSError,zipfile.BadZipFile) as e:
                quarantined.append({'id':slug,'error':type(e).__name__+':'+str(e)[:140]})
                shutil.rmtree(out,ignore_errors=True)
        report={'schema_version':1,'stage':'SOURCE_FBX_PNG_CANDIDATES_ONLY','source_run_id':source_run_id,'source_artifact_id':source_artifact_id,'source_receipt_sha256':sha(z.read('p1c01_adaptive_polyhaven_receipt.json')),'input_assets':len(receipt['accepted']),'prepared_assets':len(completed),'prepared_fbx':len(completed),'prepared_png':sum(len(x['maps']) for x in completed),'held_material_variants_total':sum(len(x['held_material_variants']) for x in completed),'quarantined':quarantined,'biome_hold':[x['id'] for x in completed if x['status']=='HOLD_BIOME'],'identity_hold':[x['id'] for x in completed if x['status']=='HOLD_IDENTITY'],'assets':completed,'evidence_boundary':'No UE4 import, LOD, collision, visual acceptance, PIE, target device or persistent warehouse write.'}
        (output/'p1c01_adaptive_pbr_receipt.json').write_text(json.dumps(report,indent=2)+'\n')
        print('P1C01_ADAPTIVE_PBR_QC prepared='+str(len(completed))+' png='+str(report['prepared_png'])+' quarantined='+str(len(quarantined))+' NOT_UE4_IMPORTED',flush=True)
        return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-artifact',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--source-run-id',type=int);p.add_argument('--source-artifact-id',type=int);a=p.parse_args()
    result=convert(a.source_artifact,a.output,a.source_run_id,a.source_artifact_id)
    raise SystemExit(0 if result['prepared_assets'] else 2)
