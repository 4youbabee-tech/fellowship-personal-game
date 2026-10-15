#!/usr/bin/env python3
"""Deterministic small-footprint authored Bag End PNG albedos, no 3rd-party art.

Project-owned input textures only. Each 512px RGBA-free RGB map targets the
existing UE4.27 material-instance AlbedoTexture binding. This is an albedo
source wave, not an invented imported normal/ORM or device performance result.
"""
from __future__ import annotations
import argparse
import math
import struct
import zlib
from pathlib import Path

SIZE=512
TEXTURES=("TX_BagEndPlaster.png","TX_BagEndTurf.png","TX_BagEndDoor.png","TX_BagEndGlass.png")


def hash2(x:int,y:int,seed:int)->float:
    # Zero global RNG state. Independent of Python hash randomization.
    n=(x*374761393+y*668265263+seed*1274126177)&0xffffffff
    n=((n^(n>>13))*1274126177)&0xffffffff
    return ((n^(n>>16))&65535)/65535.0


def smooth(t:float)->float:return t*t*(3.0-2.0*t)


def noise(x:float,y:float,scale:int,seed:int)->float:
    x=x/scale; y=y/scale
    ix=math.floor(x);iy=math.floor(y)
    tx=smooth(x-ix);ty=smooth(y-iy)
    a=hash2(ix,iy,seed);b=hash2(ix+1,iy,seed)
    c=hash2(ix,iy+1,seed);d=hash2(ix+1,iy+1,seed)
    return ((a*(1-tx)+b*tx)*(1-ty)+(c*(1-tx)+d*tx)*ty)


def clamp(a:float)->int:return max(1,min(254,int(round(a))))


def pixel(name:str,x:int,y:int)->tuple[int,int,int]:
    big=noise(x,y,91,4)-0.5
    med=noise(x,y,25,5)-0.5
    fine=noise(x,y,5,6)-0.5
    dust=hash2(x,y,7)-0.5
    if name=="TX_BagEndPlaster.png":
        grain=big*21+med*15+fine*9+dust*10
        # Aged earth-lime plaster with warm patches and fine micro-pitting.
        mineral=max(0.0,noise(x,y,48,11)-0.68)*48
        base=(222,208,184)
        return tuple(clamp(ch+grain-mineral*(1.1 if i==2 else 0.6)) for i,ch in enumerate(base))
    if name=="TX_BagEndTurf.png":
        # Dark moss clusters + fine clover/leaves without 2D high-frequency aliasing.
        tuft=med*38+fine*22+dust*16+big*43
        blossom=hash2(x//3,y//3,29)>0.997 and y%3==1 and x%3==1
        return (clamp(91+tuft+(32 if blossom else 0)),
                clamp(136+tuft*1.15+(20 if blossom else 0)),
                clamp(61+tuft*0.64+(12 if blossom else 0)))
    if name=="TX_BagEndDoor.png":
        # Vertical painted planks. Every face has authored Y/Z planar UVs.
        grain=math.sin(x*0.21+noise(x,y,22,13)*7)*4
        wood=big*12+med*13+fine*8+dust*5+grain
        seam= -34 if (x+2)%86<3 else 0
        split= -9 if (x+2)%86<8 else 0
        return (clamp(151+wood+seam+split),
                clamp(184+wood*0.88+seam+split),
                clamp(141+wood*0.65+seam+split))
    if name=="TX_BagEndGlass.png":
        # Soft warm interior at lower right; quiet sky reflection upper left.
        u=x/(SIZE-1);v=y/(SIZE-1)
        sky=max(0.0,1-u*1.35-v*0.35)
        glow=max(0.0,1.0-((u-.7)**2/.20+(v-.68)**2/.18))
        varnish=big*7+med*4
        return (clamp(69+sky*37+glow*74+varnish),
                clamp(100+sky*44+glow*42+varnish),
                clamp(99+sky*38+glow*8+varnish))
    raise ValueError(name)


def png_rgb(path:Path,name:str,size:int=SIZE)->None:
    if size!=SIZE:raise ValueError("Textures have fixed authored 512px contract")
    raw=bytearray()
    for y in range(size):
        raw.append(0)
        for x in range(size):raw.extend(pixel(name,x,y))
    def chunk(tag:bytes,data:bytes)->bytes:
        return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xffffffff)
    content=(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',size,size,8,2,0,0,0))+
             chunk(b'IDAT',zlib.compress(bytes(raw),9))+chunk(b'IEND',b''))
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(content)


def build(directory:Path)->None:
    for texture in TEXTURES:png_rgb(directory/texture,texture)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output-dir',type=Path,required=True)
    args=p.parse_args()
    build(args.output_dir)

if __name__=='__main__':main()
