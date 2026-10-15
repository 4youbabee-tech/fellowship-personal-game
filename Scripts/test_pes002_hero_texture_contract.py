"""PES002 cheap material-funnel source checks; never pretend to be an UE render."""
from __future__ import annotations
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/'SourceAssets/Production/World/Shire'
GEN=ROOT/'Tools/CloudAssetBuild/generate_bag_end_hero_materials.py'
EXPECTED={
    'BagEndPlaster':'TX_BagEndPlaster.png',
    'BagEndTurf':'TX_BagEndTurf.png',
    'BagEndDoor':'TX_BagEndDoor.png',
    'BagEndGlass':'TX_BagEndGlass.png',
}


def png_sample(path):
    blob=path.read_bytes()
    assert blob.startswith(b'\x89PNG\r\n\x1a\n')
    index=8
    ihdr=None
    idat=bytearray()
    while index<len(blob):
        count=struct.unpack('>I',blob[index:index+4])[0]
        name=blob[index+4:index+8]
        data=blob[index+8:index+8+count]
        crc=struct.unpack('>I',blob[index+8+count:index+12+count])[0]
        assert crc==(zlib.crc32(name+data)&0xffffffff)
        if name==b'IHDR':ihdr=struct.unpack('>IIBBBBB',data)
        if name==b'IDAT':idat.extend(data)
        index+=count+12
    assert ihdr==(512,512,8,2,0,0,0)
    pixels=zlib.decompress(bytes(idat))
    assert len(pixels)==512*(1+512*3)
    for row in range(512):assert pixels[row*(1+512*3)]==0
    channels=[]
    for y in range(0,512,32):
        for x in range(0,512,32):
            start=y*(1+512*3)+1+x*3
            channels.append(tuple(pixels[start:start+3]))
    return channels


class BagEndHeroTextureContract(unittest.TestCase):
    def test_standalone_material_names_do_not_replace_world_grass(self):
        mtl=(PACK/'ShireMaterials.mtl').read_text(encoding='utf-8')
        names={}
        current=None
        for line in mtl.splitlines():
            if line.startswith('newmtl '):
                current=line.split(None,1)[1];names[current]=[]
            elif current is not None:names[current].append(line)
        for material,texture in EXPECTED.items():
            self.assertIn(material,names)
            self.assertIn('map_Kd '+texture,names[material])
            self.assertTrue((PACK/texture).is_file())
        self.assertIn('map_Kd TX_ShGrass.tga',names['Grass'])
        importer=(ROOT/'Source/ShireJourneyEditorTools/Private/ShireProductionImportCommandlet.cpp').read_text(encoding='utf-8')
        self.assertIn('TEXT("BagEndTurf")',importer)
        self.assertIn('TEXT("BagEndPlaster")',importer)
        self.assertIn('PES002_HERO_MATERIALS_READY drawn=7',importer)

    def test_four_albedos_are_reproducible_and_true_colour(self):
        with tempfile.TemporaryDirectory() as temp:
            subprocess.run([sys.executable,str(GEN),'--output-dir',temp],check=True)
            for texture in EXPECTED.values():
                self.assertEqual((PACK/texture).read_bytes(),(Path(temp)/texture).read_bytes())
                colors=png_sample(PACK/texture)
                self.assertGreater(len(set(colors)),60,texture)
                for rgb in colors:self.assertTrue(all(0<ch<255 for ch in rgb))

    def test_asset_budget_unchanged_single_obj_mesh_and_four_512_albedos(self):
        paths=[PACK/name for name in EXPECTED.values()]
        self.assertLess(sum(x.stat().st_size for x in paths),1024*1024)
        vertices=(PACK/'SM_ShBagEndHeroFacade.obj').read_text(encoding='utf-8')
        self.assertEqual(vertices.count('\no SM_ShBagEndHeroFacade\n'),1)
        self.assertIn('\nusemtl BagEndTurf\n',vertices)
        self.assertNotIn('\nusemtl Grass\n',vertices)

if __name__=='__main__':unittest.main()
