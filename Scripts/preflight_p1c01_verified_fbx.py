#!/usr/bin/env python3
"""Fail-closed pre-UE derived FBX normalization, original source kept byte-for-byte."""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SLUG=re.compile(r"[a-z0-9_]{3,80}\Z")
class SourceQCError(ValueError): pass
def check(ok, why):
    if not ok: raise SourceQCError(why)
def sha(path):
    check(path.is_file() and not path.is_symlink(),"MISSING_FILE:"+str(path))
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1048576),b""): h.update(block)
    return h.hexdigest()
def valid_derived(p):
    if not p.is_file() or p.is_symlink() or p.stat().st_size<=256:return False
    with p.open("rb") as f:return f.read(30).startswith(b"Kaydara FBX Binary") and b"LayerElementSmoothing" in f.read()
def blender_exec(candidate):
    if candidate:
        return str(candidate) if Path(candidate).is_file() else shutil.which(candidate)
    found=shutil.which("blender")
    if found:return found
    base=Path(os.environ.get("PROGRAMFILES","C:/Program Files"))/"Blender Foundation"
    if base.is_dir():
        for p in sorted(base.glob("Blender */blender.exe"),reverse=True):
            if p.is_file():return str(p)
    return None
def execute(project,blender=None,required=False,verify_only=False):
    folder=project/"SourceAssets/Production/World/Shire/VerifiedPBR"
    files=sorted(folder.glob("*/*.fbx")) if folder.is_dir() else []
    if not files:
        check(not required,"VERIFIED_FBX_SOURCE_EMPTY")
        print("P1C01_FBX_NORMALIZATION_NO_SOURCE")
        return []
    check(len(files)<=16,"VERIFIED_FBX_SOURCE_LIMIT")
    output=project/"Saved/P1C01NormalizedFBX"
    receipt=output/"receipt.json"
    prior=json.loads(receipt.read_text(encoding="utf-8")) if receipt.is_file() else {}
    old={x["id"]:x for x in prior.get("assets",[])}
    results=[]
    reused=0
    tool=None
    for source in files:
        slug=source.parent.name
        check(SLUG.fullmatch(slug) is not None and source.name==slug+".fbx" and not source.is_symlink(),"UNSAFE_SOURCE_ID")
        src_sha=sha(source)
        target=output/slug/(slug+".fbx")
        row=old.get(slug,{})
        reuse=(row.get("source_sha256")==src_sha and row.get("derived_sha256") and
               valid_derived(target) and sha(target)==row["derived_sha256"])
        if reuse:
            reused+=1
        if not reuse:
            check(not verify_only,"DERIVED_FBX_NOT_READY:"+slug)
            if tool is None:
                tool=blender_exec(blender)
                check(tool is not None,"BLENDER_REQUIRED_BEFORE_UNREAL")
            target.parent.mkdir(parents=True,exist_ok=True)
            temp=target.with_name(slug+".normalized.tmp.fbx")
            check(not temp.exists(),"INCOMPLETE_NORMALIZATION:"+slug)
            try:
                process=subprocess.run([tool,"--background","--factory-startup","--python-exit-code","85",
                    "--python",str(ROOT/"Scripts/normalize_verified_pbr_blender.py"),"--",
                    "--input",str(source),"--output",str(temp),"--asset",slug],
                    text=True,capture_output=True,timeout=180,check=False)
                check(process.returncode==0 and "P1C01_FBX_NORMALIZED asset="+slug in process.stdout,
                    "NORMALIZER_FAILED:"+slug+":"+(process.stdout+process.stderr)[-1000:])
                check(valid_derived(temp),"SMOOTHING_LAYER_NOT_EXPORTED:"+slug)
                temp.replace(target)
            finally:
                if temp.exists():temp.unlink()
        results.append({"id":slug,"source_sha256":src_sha,"derived_sha256":sha(target),
                        "derived_bytes":target.stat().st_size})
    if not verify_only:
        output.mkdir(parents=True,exist_ok=True)
        receipt.write_text(json.dumps({"schema_version":1,"stage":"DERIVED_STATIC_FBX_QC",
            "warehouse_mutated":False,"source_mutated":False,"assets":results},indent=2)+"\n",encoding="utf-8")
    print("P1C01_FBX_NORMALIZATION_PREFLIGHT_PASS count="+str(len(results))+" reused="+str(reused)+" normalized="+str(len(results)-reused),flush=True)
    return results
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--project-root",type=Path,required=True)
    p.add_argument("--blender")
    p.add_argument("--require-source",action="store_true")
    p.add_argument("--verify-only",action="store_true")
    a=p.parse_args()
    try:execute(a.project_root,a.blender,a.require_source,a.verify_only);return 0
    except (OSError,ValueError,subprocess.TimeoutExpired) as exc:
        print("P1C01_FBX_NORMALIZATION_PREFLIGHT_FAIL "+str(exc),file=sys.stderr);return 85
if __name__=="__main__":raise SystemExit(main())
