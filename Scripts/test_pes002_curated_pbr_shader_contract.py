"""PES-002 regressions for real imported HISM foliage shading.

These checks protect source invariants; exact UE4.27 shader/runtime screenshot
proof remains mandatory before visual acceptance.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Scripts"))

from curated_tree_surface_contract import resolve_tree_slots


class PES002CuratedPBRShaderTests(unittest.TestCase):
    def test_real_blender_green_bark_leaf_names_bind_by_identity(self):
        producer = (ROOT / 'Tools/CloudAssetBuild/blender_nature.py').read_text(encoding='utf-8')
        self.assertIn('material("M_Sh_Bark"', producer)
        self.assertIn('material("M_Sh_Leaf"', producer)
        self.assertEqual({'Bark': 0, 'LeafGreen': 1}, resolve_tree_slots([
            {'index': 0, 'slot_name': 'M_Sh_Bark', 'imported_name': 'M_Sh_Bark'},
            {'index': 1, 'slot_name': 'M_Sh_Leaf', 'imported_name': 'M_Sh_Leaf'},
        ]))
        self.assertIsNone(resolve_tree_slots([
            {'index': 0, 'slot_name': 'M_Sh_Bark', 'imported_name': 'M_Sh_Bark'},
            {'index': 1, 'slot_name': 'M_Sh_Unknown', 'imported_name': 'M_Sh_Unknown'},
        ]))

    def test_pbr_master_repairs_real_physical_linear_mask_and_instancing(self):
        src = (ROOT / 'Source/ShireJourneyEditorTools/Private/ShireProductionImportCommandlet.cpp').read_text(encoding='utf-8')
        self.assertIn('P1C01_CURATED_PBR_MASTER_REPAIR ready=%d', src)
        self.assertIn('T_Sh_Bark_ORM.T_Sh_Bark_ORM', src)
        self.assertIn('ORMParameter->SamplerType = SAMPLERTYPE_Masks;', src)
        self.assertIn('CuratedDefaultORM->CompressionSettings = TC_Masks;', src)
        self.assertIn('CuratedDefaultORM->SRGB = false;', src)
        self.assertIn('VerifiedMaster->bUsedWithInstancedStaticMeshes = true;', src)
        self.assertIn('ImportedMaterialPackages.AddUnique(', src)
        self.assertIn('VerifiedMaster->PostEditChange();', src)
        self.assertIn('VerifiedMaster->MarkPackageDirty();', src)
        self.assertIn('SAMPLERTYPE_Color);', src)
        self.assertNotIn('TEXT("ORMTexture"),\n                TEXT("/Engine/EngineResources/WhiteSquareTexture.WhiteSquareTexture"),\n                SAMPLERTYPE_LinearColor', src)
        self.assertLess(src.index('P1C01_CURATED_PBR_MASTER_REPAIR ready=%d'),
                        src.index('SaveMaterialPackagesDeterministically(TEXT("post-mesh-binding"))'))

    def test_unreal_camera_capture_cannot_hide_default_shader(self):
        src = (ROOT / 'Scripts/capture_pes002_bag_end_visual.ps1').read_text(encoding='utf-8')
        self.assertIn('PES002_CURATED_PBR_DEFAULT_SHADER_FALLBACK', src)
        self.assertIn('M_P1C01VerifiedPBR.*Failed to compile Material', src)
        self.assertIn('M_P1C01VerifiedPBR.*missing bUsedWithInstancedStaticMeshes', src)
        self.assertIn('PES002_CURATED_PBR_RUNTIME_SHADER_NO_FALLBACK_PASS', src)
        self.assertGreater(src.index('PES002_CURATED_PBR_DEFAULT_SHADER_FALLBACK'),
                           src.index('PES002_BAG_END_CAPTURE_PRESENT'))


if __name__ == '__main__':
    unittest.main()
