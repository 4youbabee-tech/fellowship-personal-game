import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

MATERIALS = (
    "/Game/Production/Imported/P1C01Materials/SH_DIRT_SOIL/MI_Sh_DirtSoil_PH.MI_Sh_DirtSoil_PH",
    "/Game/Production/Imported/P1C01Materials/SH_STONY_PATH/MI_Sh_StonyPath_PH.MI_Sh_StonyPath_PH",
    "/Game/Production/Imported/P1C01Materials/SH_TREE_BARK/MI_Sh_TreeBark_PH.MI_Sh_TreeBark_PH",
    "/Game/Production/Imported/P1C01Materials/SH_MOSS_STONE/MI_Sh_MossStone_PH.MI_Sh_MossStone_PH",
)

class HighFidelitySurfaceBindingContract(unittest.TestCase):
    def test_p1c01_bank_preloads_only_high_impact_surface_set(self):
        plan = json.loads((ROOT/'Data'/'ChapterAssetStreamingPlan.json').read_text(encoding='utf-8'))
        assets = plan['banks']['P1C01']['assets']
        for path in MATERIALS:
            self.assertIn(path, assets)

    def test_world_builder_consumes_resident_materials_without_sync_loading(self):
        cpp = (ROOT/'Source'/'ShireJourney'/'Private'/'World'/'ShirePrototypeWorldBuilder.cpp').read_text(encoding='utf-8')
        for path in MATERIALS:
            self.assertIn(path, cpp)
        for token in (
            'HighFidelityDirtMaterial',
            'HighFidelityPathMaterial',
            'HighFidelityBarkMaterial',
            'HighFidelityStoneMaterial',
            'GardenSoilInstances->SetMaterial(0, HighFidelityDirtMaterial)',
            'GeographyRiverBankInstances->SetMaterial(0, HighFidelityDirtMaterial)',
            'PathStoneInstances->SetMaterial(0, HighFidelityPathMaterial)',
            'DistantTreeTrunkInstances->SetMaterial(0, HighFidelityBarkMaterial)',
            'WoodlandTreeInstances->SetMaterial(0, HighFidelityBarkMaterial)',
            'RockInstances->SetMaterial(0, HighFidelityStoneMaterial)',
            'densityIncrease=no',
        ):
            self.assertIn(token, cpp)
        region = cpp[cpp.index('UMaterialInterface* HighFidelityDirtMaterial'):]
        self.assertNotIn('LoadObject<', region)
        self.assertNotIn('RequestSyncLoad', region)
        self.assertNotIn('StaticLoadObject', region)

if __name__ == '__main__':
    unittest.main()
