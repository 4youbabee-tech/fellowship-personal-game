import importlib.util
import pathlib
import sys
import types
import unittest

# Blender is only needed when exporting real FBX; this source guard does not fake it.
sys.modules["bpy"] = types.ModuleType("bpy")
file = pathlib.Path(__file__).with_name("frodo_locomotion.py")
spec = importlib.util.spec_from_file_location("frodo_source", file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class FrodoSourceContract(unittest.TestCase):
    def test_mixamo_limb_mapping_and_skeleton_guard(self):
        source = file.read_text(encoding="utf-8")
        self.assertIn('packed.startswith("left")', source)
        self.assertIn('packed.startswith("right")', source)
        self.assertIn('"forearm":("forearm","lowerarm")', source)
        self.assertIn("FRODO_ANIMATION_SKELETON_MISMATCH_ACROSS_CLIPS", source)
        self.assertIn("SOURCE_ANIMATION_FBX_REIMPORTED", source)
        self.assertIn('"unreal_imported":False', source)

if __name__ == "__main__":
    unittest.main()
