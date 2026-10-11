import importlib.util,io,unittest
from pathlib import Path
from PIL import Image
s=importlib.util.spec_from_file_location("ph",Path(__file__).with_name("polyhaven_cloud_warehouse.py"));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_urls(self):
  for u in ("file:///secret","http://dl.polyhaven.org/x.png","https://evil.example/a.png"):
   with self.assertRaises(ValueError):m.urlcheck(u)
 def test_maps(self):
  tree={"1k":{x:{"png":{"url":"https://dl.polyhaven.org/"+x+".png","size":100}} for x in ("diff","nor_gl","rough")}}
  self.assertEqual(set(m.select(tree)),{"diff","nor_gl","rough"})
 def test_channel_pack(self):
  raw=io.BytesIO();Image.new("RGB",(1024,1024),(110,85,70)).save(raw,"PNG")
  self.assertEqual(m.decode(raw.getvalue(),"RGB").size,(1024,1024))
  self.assertEqual(m.png(Image.new("RGB",(1024,1024))).startswith(bytes.fromhex("89504e47")),True)
if __name__=="__main__":unittest.main()
