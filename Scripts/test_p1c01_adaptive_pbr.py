"""Offline negative and 1K material behavior tests, source download NEVER needed."""
import sys,io,unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parent))
from prepare_p1c01_adaptive_pbr import safe,pixels,QCError,HOLD_BIOME

class Tests(unittest.TestCase):
    def test_reject_parent_escape(self):
        with self.assertRaisesRegex(QCError,'UNSAFE_PATH'):safe('../bad.fbx')
    def test_preserve_16bit_alpha(self):
        ar=np.full((1024,1024),32768,dtype=np.uint16)
        buf=io.BytesIO();Image.fromarray(ar).save(buf,format='PNG')
        self.assertEqual(int(pixels(buf.getvalue(),'.png',True)[1,1]),128)
    def test_flip_normal_green_direction(self):
        buf=io.BytesIO();Image.new('RGB',(1024,1024),(127,60,255)).save(buf,format='PNG')
        nor=pixels(buf.getvalue(),'.png').copy();nor[:,:,1]=255-nor[:,:,1]
        self.assertEqual(nor[0,0,:].tolist(),[127,195,255])
    def test_tropical_held(self):
        self.assertIn('calathea_orbifolia_01',HOLD_BIOME)
    def test_non_1k_rejected(self):
        buf=io.BytesIO();Image.new('RGB',(16,16)).save(buf,format='PNG')
        with self.assertRaisesRegex(QCError,'NOT_1K'):pixels(buf.getvalue(),'.png')

if __name__=='__main__':unittest.main()
