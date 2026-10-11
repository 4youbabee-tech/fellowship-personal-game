#!/usr/bin/env python3
"""Source-only Poly Haven CC0 intake: real BaseColor/NormalDX/ORM 1K PNG."""
import argparse,hashlib,io,json,urllib.request,urllib.parse,time
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
HOSTS={"api.polyhaven.com","dl.polyhaven.org","cdn.polyhaven.com","polyhaven.com"}
def sha(data):return hashlib.sha256(data).hexdigest()
def urlcheck(url):
 p=urllib.parse.urlsplit(url)
 if p.scheme!="https" or p.hostname not in HOSTS or p.username or p.password:raise ValueError("UNAPPROVED_URL")
 return url
class Redirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,url):
  urlcheck(url)
  return super().redirect_request(req,fp,code,msg,headers,url)
opener=urllib.request.build_opener(Redirect())
def fetch(url,limit):
 urlcheck(url)
 for i in range(3):
  try:
   with opener.open(urllib.request.Request(url,headers={"User-Agent":"ShireJourney-CC0/1.0"}),timeout=30) as res:
    urlcheck(res.geturl())
    data=res.read(limit+1)
    if len(data)<8 or len(data)>limit:raise ValueError("INVALID_DOWNLOAD_SIZE")
    return data
  except (OSError,TimeoutError):
   if i==2:raise
   time.sleep(2**i)
def nodes(tree,path=()):
 if isinstance(tree,dict):
  if isinstance(tree.get("url"),str):yield path,tree
  else:
   for k,v in tree.items():yield from nodes(v,path+(str(k).lower(),))
 elif isinstance(tree,list):
  for i,v in enumerate(tree):yield from nodes(v,path+(str(i),))
def select(tree):
 rows={}
 for path,item in nodes(tree):
  if "png" not in path or not any(x in path for x in ("1k","2k")):continue
  if not urllib.parse.urlsplit(item["url"]).path.lower().endswith(".png"):continue
  channel=next((k for k in ("diff","nor_dx","nor_gl","rough","ao","metal") if any(token==k or token.startswith(k) for token in path)),None)
  if channel is None:continue
  urlcheck(item["url"])
  size=int(item.get("size") or 0)
  if size<0 or size>12000000:continue
  key=(0 if "1k" in path else 1,item["url"])
  if channel not in rows or key<rows[channel][0]:rows[channel]=(key,item)
 return {k:v[1] for k,v in rows.items()}
def decode(raw,mode):
 if not raw.startswith(bytes.fromhex("89504e470d0a1a0a")):raise ValueError("NOT_PNG")
 with Image.open(io.BytesIO(raw)) as img:
  img.load()
  if img.size not in ((1024,1024),(2048,2048)):raise ValueError("PNG_RESOLUTION_INVALID")
  out=img.convert(mode)
  return out if out.size==(1024,1024) else out.resize((1024,1024),Image.Resampling.LANCZOS)
def png(img):
 out=io.BytesIO();img.save(out,format="PNG",optimize=True);return out.getvalue()
def produce(asset,out,budget,fetcher=fetch):
 slug=asset["slug"]
 tree=json.loads(fetcher("https://api.polyhaven.com/files/"+slug,2000000))
 chosen=select(tree)
 if not all(k in chosen for k in ("diff","rough")) or not any(k in chosen for k in ("nor_dx","nor_gl")):raise ValueError("MISSING_REQUIRED_MAPS")
 source=[];imgs={}
 for key in ("diff","nor_dx" if "nor_dx" in chosen else "nor_gl","rough","ao","metal"):
  if key not in chosen:continue
  info=chosen[key]
  if budget[0]+int(info.get("size") or 0)>150000000:raise ValueError("SHARD_CAP")
  raw=fetcher(info["url"],12000000)
  if budget[0]+len(raw)>150000000:raise ValueError("SHARD_CAP")
  if info.get("md5") and hashlib.md5(raw).hexdigest()!=info["md5"].lower():raise ValueError("PROVIDER_MD5")
  imgs[key]=decode(raw,"RGB" if key in ("diff","nor_dx","nor_gl") else "L")
  source.append({"map":key,"url":info["url"],"sha256":sha(raw),"bytes":len(raw)})
  budget[0]+=len(raw)
 normal=imgs.get("nor_dx",imgs.get("nor_gl"))
 if "nor_dx" not in imgs:
  r,g,b=normal.split();normal=Image.merge("RGB",(r,g.point(lambda x:255-x),b))
 white=Image.new("L",(1024,1024),255);black=Image.new("L",(1024,1024),0)
 triplets={"BaseColor":imgs["diff"],"NormalDX":normal,"ORM":Image.merge("RGB",(imgs.get("ao",white),imgs["rough"],imgs.get("metal",black)))}
 saved=[]
 folder=out/"materials"/slug;folder.mkdir(parents=True,exist_ok=True)
 for channel,img in triplets.items():
  dest=folder/("TX_PH_"+slug+"_"+channel+".png");data=png(img);dest.write_bytes(data)
  with Image.open(dest) as check:check.verify()
  saved.append({"path":dest.relative_to(out).as_posix(),"sha256":sha(data),"bytes":len(data),"kind":channel})
 return {"slug":slug,"license":"CC0","source_page":"https://polyhaven.com/a/"+slug,"source_maps":source,"outputs":saved,"unreal_imported":False}
def verify(out):
 rec=json.loads((out/"receipt.json").read_text())
 if not rec["materials"] or rec["unreal_imported"] is not False:raise ValueError("EMPTY_OR_BAD_RECEIPT")
 count=0
 for material in rec["materials"]:
  for row in material["outputs"]:
   rel=Path(row["path"])
   if ".." in rel.parts or rel.is_absolute():raise ValueError("BAD_PATH")
   data=(out/rel).read_bytes()
   if len(data)!=row["bytes"] or sha(data)!=row["sha256"]:raise ValueError("HASH_MISMATCH")
   with Image.open(out/rel) as img:
    if img.size!=(1024,1024):raise ValueError("BAD_DIMENSIONS")
    img.verify()
   count+=1
 if count!=rec["physical_png"]:raise ValueError("COUNT_MISMATCH")
 print("CLOUD_CC0_SHA256_PASS physical_png="+str(count))
def main():
 p=argparse.ArgumentParser();p.add_argument("--out",required=True);p.add_argument("--shard",type=int,required=True);p.add_argument("--verify-only",action="store_true")
 a=p.parse_args()
 if a.shard not in range(4):raise ValueError("BAD_SHARD")
 out=Path(a.out)/("shard_"+str(a.shard))
 if a.verify_only:return verify(out)
 manifest=(ROOT/"Data/WarehouseAcquisitionBatchV1.json").read_bytes()
 data=json.loads(manifest)
 regions=json.loads((ROOT/"Data/WholeGameRegionProductionPacketsV1.json").read_text())["packets"]
 if data["provider"]!="POLY_HAVEN" or data["license"]!="CC0" or len(regions)!=28:raise ValueError("SOURCE_AUTHORITY")
 assets=data["assets"]
 if len(assets)!=37 or len({x["slug"] for x in assets})!=37:raise ValueError("37_APPROVED_SOURCE_SET_CHANGED")
 materials=[];quarantined=[];budget=[0]
 for i,asset in enumerate(assets):
  if i%4!=a.shard:continue
  try:
   row=produce(asset,out,budget);materials.append(row);print("CC0_SOURCE_PHYSICAL_PASS "+asset["slug"],flush=True)
  except (ValueError,OSError,KeyError) as e:
   quarantined.append({"slug":asset["slug"],"reason":str(e)[:120]});print("CC0_SOURCE_QUARANTINED "+asset["slug"]+" "+str(e)[:100],flush=True)
 out.mkdir(parents=True,exist_ok=True)
 receipt={"status":"CLOUD_SOURCE_STAGED" if materials else "CLOUD_SOURCE_EMPTY","shard":a.shard,"manifest_sha256":sha(manifest),"selected_assets":len([x for i,x in enumerate(assets) if i%4==a.shard]),"staged":len(materials),"physical_png":sum(len(x["outputs"]) for x in materials),"source_bytes":budget[0],"region_catalog_only":28,"materials":materials,"quarantined":quarantined,"unreal_imported":False,"owner_warehouse_written":False}
 (out/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
 if not materials:raise ValueError("EMPTY_SHARD")
 verify(out)
if __name__=="__main__":main()
